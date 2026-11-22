#!/usr/bin/env python3
"""通用精品广播剧矩阵 · Colab 96GB G4 零 API 成本一键启动、跨项目声库复用与云盘原子归档器 (v1.0.0).

支持项目（可单跑或 `--project all` 一次 G4 过夜全跑完并自动关机止费）：
  1. `liaozhai_midnight` -> MyDrive/《聊斋志异》午夜悬疑广播剧场/
  2. `cthulhu_archives`  -> MyDrive/《克苏鲁神话》不可名状声音档案/
  3. `hayek_1944`        -> MyDrive/《1944剑桥夜话》哈耶克思想剧场/

零 API 成本声库装配原理：
  - 现代真实棚录角色（`repo_buffett_real_human`）：直接读取本仓 `projects/buffett_letters/.../voice_anchors/*.wav`。
  - 国风/惊悚/威严戏剧角色（`zhujie_suoxian`）：自动从挂载云盘或 Drive API v3 拉取已锁定的
    `zhujie_suoxian_96gb_drama3_bundle.zip`（File ID: `1pTHmq6kw0y2-jUzGDY3ngApk91uSn4Ks`），
    按各剧 `anchor_sources.json` 精准解包所需干音 WAV 并对齐 100% 逐字 `anchor_text`。
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
from typing import Any, Optional
import urllib.parse
import urllib.request
import wave
import zipfile

if os.path.isdir("/content/drive/My Drive") and not os.path.exists("/content/drive/MyDrive"):
    os.symlink("/content/drive/My Drive", "/content/drive/MyDrive")

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent
NVME_ROOT = Path("/content") if Path("/content").exists() else Path("/tmp")
HF_CACHE_DIR = NVME_ROOT / "hf_cache"
WORK_BASE = NVME_ROOT / "anthology_drama3_work"
ENV_ROOT = (
    NVME_ROOT / "nine_prison_envs"
    if (NVME_ROOT / "nine_prison_envs" / "drama3-venv" / "bin" / "sgl-omni").exists()
    else (NVME_ROOT / "audio_studio_envs")
)

os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["UV_CONCURRENT_DOWNLOADS"] = "32"

DRIVE_ROOT = Path("/content/drive/MyDrive")
DRIVE_WORKSTATION = DRIVE_ROOT / "AI_Workstation"
DRIVE_REPO_CACHE = DRIVE_WORKSTATION / "AudioStudio_G4_Cache"
DRIVE_WORKBENCH_SUB = "01_Colab_96GB_FishDrama3_工作台"
DRIVE_MASTERS_SUB = "02_分集成片母带_WAV_MP3_SRT"

ANTHOLOGY_PROJECTS: dict[str, dict[str, str]] = {
    "liaozhai_midnight": {
        "title": "《聊斋志异·午夜悬疑广播剧场》",
        "project_rel": "projects/liaozhai_midnight",
        "drive_show_folder": "《聊斋志异》午夜悬疑广播剧场",
        "bgm_style": "liaozhai_horror",
    },
    "cthulhu_archives": {
        "title": "《克苏鲁神话·不可名状声音档案》",
        "project_rel": "projects/cthulhu_archives",
        "drive_show_folder": "《克苏鲁神话》不可名状声音档案",
        "bgm_style": "cosmic_horror",
    },
    "hayek_1944": {
        "title": "《1944剑桥夜话：〈通往奴役之路〉思想剧场》",
        "project_rel": "projects/hayek_1944",
        "drive_show_folder": "《1944剑桥夜话》哈耶克思想剧场",
        "bgm_style": "hayek_economics",
    },
}


def sh(cmd: str, env: Optional[dict[str, str]] = None) -> str:
    safe_cmd = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer [REDACTED]", cmd)
    print(f"🔧 $ {safe_cmd}", flush=True)
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True, env=env)
    if p.returncode != 0:
        if p.stdout:
            print(p.stdout[-800:], flush=True)
        if p.stderr:
            print(f"⚠️ {p.stderr[-1200:]}", flush=True)
        raise RuntimeError(f"命令执行失败 (rc={p.returncode}): {safe_cmd}")
    return p.stdout


def get_drive_token() -> Optional[str]:
    for endpoint in (
        "http://172.28.0.1:8009/computeMetadata/v1/instance/service-accounts/default/token",
        "http://127.0.0.1:8012/computeMetadata/v1/instance/service-accounts/default/token",
    ):
        try:
            req = urllib.request.Request(endpoint, headers={"Metadata-Flavor": "Google"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                tok = json.loads(resp.read().decode("utf-8")).get("access_token")
                if tok:
                    return str(tok)
        except Exception:
            continue
    return None


def drive_api_find_file_by_name(
    name: str,
    tok: str,
    *,
    parent_id: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> Optional[str]:
    safe_name = name.replace("'", "\\'")
    clauses = ["trashed = false", f"name = '{safe_name}'"]
    if parent_id:
        clauses.append(f"'{parent_id}' in parents")
    if mime_type:
        clauses.append(f"mimeType = '{mime_type}'")
    q = " and ".join(clauses)
    url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(
        {"q": q, "fields": "files(id,name)", "pageSize": 5}
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        files = json.loads(resp.read().decode("utf-8")).get("files", [])
    return files[0]["id"] if files else None


def drive_api_ensure_folder(name: str, parent_id: str, tok: str) -> str:
    folder_mime = "application/vnd.google-apps.folder"
    existing_id = drive_api_find_file_by_name(name, tok, parent_id=parent_id, mime_type=folder_mime)
    if existing_id:
        return existing_id
    meta = json.dumps({"name": name, "mimeType": folder_mime, "parents": [parent_id]}).encode("utf-8")
    req = urllib.request.Request(
        "https://www.googleapis.com/drive/v3/files?fields=id,name",
        data=meta,
        method="POST",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["id"]


def drive_api_download(file_id: str, dest: Path, tok: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
        headers={"Authorization": f"Bearer {tok}"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp, open(dest, "wb") as fout:
        shutil.copyfileobj(resp, fout, length=4 * 1024 * 1024)


def drive_api_upsert_file(local_path: Path, parent_id: str, tok: str) -> None:
    mime_type, _ = mimetypes.guess_type(local_path.name)
    if not mime_type:
        mime_type = "audio/mpeg" if local_path.suffix == ".mp3" else ("text/plain" if local_path.suffix == ".srt" else "application/octet-stream")
    existing_id = drive_api_find_file_by_name(local_path.name, tok, parent_id=parent_id)
    raw = local_path.read_bytes()
    if existing_id:
        up_req = urllib.request.Request(
            f"https://www.googleapis.com/upload/drive/v3/files/{existing_id}?uploadType=media&fields=id,name,size",
            data=raw,
            method="PATCH",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": mime_type},
        )
    else:
        boundary = f"anthology_drama3_{int(time.time() * 1000)}"
        meta = json.dumps({"name": local_path.name, "parents": [parent_id]}).encode("utf-8")
        body = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode("utf-8")
            + meta
            + f"\r\n--{boundary}\r\nContent-Type: {mime_type}\r\n\r\n".encode("utf-8")
            + raw
            + f"\r\n--{boundary}--\r\n".encode("utf-8")
        )
        up_req = urllib.request.Request(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,size",
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": f"multipart/related; boundary={boundary}"},
        )
    with urllib.request.urlopen(up_req, timeout=360) as resp:
        info = json.loads(resp.read().decode("utf-8"))
    print(f"☁️ [Drive API 原子落盘] {local_path.name} ({len(raw)/(1024*1024):.2f} MB, id={info.get('id')})", flush=True)


def _write_stub_anchor_wav(dst_wav: Path, *, freq_hz: float = 210.0, duration_s: float = 3.0) -> float:
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    sr = 44100
    nframes = int(round(duration_s * sr))
    buf = bytearray(nframes * 2)
    two_pi_f = 2.0 * math.pi * freq_hz / sr
    for i in range(nframes):
        val = int(9000.0 * math.sin(two_pi_f * i))
        buf[i * 2] = val & 0xFF
        buf[i * 2 + 1] = (val >> 8) & 0xFF
    with wave.open(str(dst_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(bytes(buf))
    return duration_s


def _locate_zhujie_bundle_zip(spec: dict[str, str]) -> Path:
    zip_name = spec["zip_name"]
    local_zip = WORK_BASE / "shared_bundles" / zip_name
    if local_zip.is_file() and local_zip.stat().st_size > 10_000_000:
        return local_zip

    fuse_cands = [
        DRIVE_ROOT / "《诸界锁仙》长篇修仙小说工程" / "04_有声剧与广播剧音频" / "05_Colab_96GB_FishDrama3_满血本地推理管线" / zip_name,
        *DRIVE_ROOT.glob(spec.get("drive_glob", f"**/{zip_name}")),
    ]
    fuse_hit = next((p for p in fuse_cands if p.is_file()), None)
    if fuse_hit is not None:
        local_zip.parent.mkdir(parents=True, exist_ok=True)
        print(f"⚡ 从云盘复制国风声库母包至本地 NVMe: {fuse_hit} ...", flush=True)
        shutil.copy2(fuse_hit, local_zip)
        return local_zip

    tok = get_drive_token()
    if tok:
        fid = spec.get("drive_file_id") or drive_api_find_file_by_name(zip_name, tok)
        if fid:
            print(f"⬇️ 通过 Drive API v3 拉取国风声库母包 ({zip_name}, id={fid})...", flush=True)
            drive_api_download(fid, local_zip, tok)
            return local_zip

    raise FileNotFoundError(
        f"未找到国风声库母包 {zip_name}！请确认已挂载 Google Drive 且存在《诸界锁仙》Drama3 资产包。"
    )


def prepare_anthology_voice_anchors(
    *,
    project_key: str,
    project_dir: Path,
    local_studio: Path,
    drive_studio_dir: Path,
    drive_ids: Optional[dict[str, str]],
    offline_dry_run: bool = False,
) -> Path:
    """Assemble zero-cost `voice_cast_drama3.json` + `voice_anchors/*.wav` by reusing locked studio anchors."""
    registry_path = project_dir / "00_节目圣经与选角档案" / "voice_casting_registry.json"
    anchor_cfg = json.loads((project_dir / "00_节目圣经与选角档案" / "anchor_sources.json").read_text(encoding="utf-8"))
    registry_raw = json.loads(registry_path.read_text(encoding="utf-8"))
    roles_raw: dict[str, dict[str, Any]] = registry_raw["roles"]

    anchors_dir = local_studio / "voice_anchors"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    vc_path = local_studio / "voice_cast_drama3.json"

    # Fast path: restore already-assembled anchors from project's own Drive folder
    if not offline_dry_run and (drive_studio_dir / "voice_cast_drama3.json").is_file() and (drive_studio_dir / "voice_anchors").is_dir():
        try:
            cached_vc = json.loads((drive_studio_dir / "voice_cast_drama3.json").read_text(encoding="utf-8"))
            cached_chars = cached_vc.get("characters", {})
            if all(
                r in cached_chars and (drive_studio_dir / cached_chars[r]["anchor_wav"]).is_file()
                for r in anchor_cfg["role_mappings"]
            ):
                shutil.copy2(drive_studio_dir / "voice_cast_drama3.json", vc_path)
                for r in anchor_cfg["role_mappings"]:
                    src_w = drive_studio_dir / cached_chars[r]["anchor_wav"]
                    shutil.copy2(src_w, local_studio / cached_chars[r]["anchor_wav"])
                print(f"🎙️ [{project_key}] 已从云盘秒级恢复全套 {len(anchor_cfg['role_mappings'])} 角色零成本干音锚点！", flush=True)
                return vc_path
        except Exception as exc:
            print(f"ℹ️ [{project_key}] 云盘锚点缓存检查跳过 ({exc})，重新从母库装配。", flush=True)

    zhujie_cast_meta = json.loads(
        (REPO_ROOT / "projects" / "zhujie_suoxian" / "00_声音选角档案与进度台账" / "voice_cast_drama3.json").read_text(encoding="utf-8")
    )["characters"]
    zhujie_zip_obj: Optional[zipfile.ZipFile] = None
    repo_local_dir = REPO_ROOT / anchor_cfg.get(
        "repo_local_anchors_dir", "projects/buffett_letters/00_节目圣经与第一季12期总纲/voice_anchors"
    )

    cast_entries: dict[str, dict[str, Any]] = {}
    try:
        for idx, (role_id, mapping) in enumerate(sorted(anchor_cfg["role_mappings"].items()), 1):
            src_bundle = mapping["source_bundle"]
            src_role = mapping["source_role_id"]
            rel_wav = f"voice_anchors/{role_id}.wav"
            dst_wav = local_studio / rel_wav
            prof = roles_raw.get(role_id, {})

            if src_bundle == "repo_buffett_real_human":
                src_wav = repo_local_dir / f"{src_role}.wav"
                src_txt = repo_local_dir / f"{src_role}.txt"
                if src_wav.is_file() and src_txt.is_file():
                    shutil.copy2(src_wav, dst_wav)
                    anchor_text = src_txt.read_text(encoding="utf-8").strip()
                elif offline_dry_run:
                    _write_stub_anchor_wav(dst_wav, freq_hz=180.0 + idx * 17.0)
                    anchor_text = "离线测试参考干音文本。"
                else:
                    raise FileNotFoundError(f"缺少本地真人干音锚点: {src_wav}")
            elif src_bundle == "zhujie_suoxian":
                anchor_text = zhujie_cast_meta[src_role]["anchor_text"].strip()
                if offline_dry_run:
                    _write_stub_anchor_wav(dst_wav, freq_hz=170.0 + idx * 15.0)
                else:
                    if zhujie_zip_obj is None:
                        zpath = _locate_zhujie_bundle_zip(anchor_cfg["drive_source_bundles"]["zhujie_suoxian"])
                        zhujie_zip_obj = zipfile.ZipFile(zpath, "r")
                    member = f"voice_anchors/{src_role}.wav"
                    with zhujie_zip_obj.open(member) as fin, open(dst_wav, "wb") as fout:
                        shutil.copyfileobj(fin, fout)
            else:
                raise ValueError(f"不支持的声库来源: {src_bundle}")

            with wave.open(str(dst_wav), "rb") as wf:
                dur_s = round(wf.getnframes() / max(1, wf.getframerate()), 3)

            cast_entries[role_id] = {
                "role_id": role_id,
                "display_name": prof.get("display_name", role_id),
                "tier": prof.get("tier", "recurring"),
                "gender": prof.get("gender", "male"),
                "age_group": prof.get("age_group", "adult"),
                "language_code": prof.get("language_code", "zh"),
                "vocal_register": prof.get("vocal_register", ""),
                "source_voice_name": mapping.get("source_voice_name", ""),
                "anchor_wav": rel_wav,
                "anchor_duration_s": dur_s,
                "anchor_text": anchor_text,
                "default_stability": prof.get("default_stability", 0.5),
            }
    finally:
        if zhujie_zip_obj is not None:
            zhujie_zip_obj.close()

    payload = {
        "project_id": registry_raw["project_id"],
        "project_title": registry_raw["project_title"],
        "domain": registry_raw.get("domain", ""),
        "anchor_strategy": anchor_cfg.get("strategy", "zero_cost_reuse"),
        "anchor_sample_rate_hz": 44100,
        "role_count": len(cast_entries),
        "characters": cast_entries,
    }
    vc_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"🎙️ [{project_key}] 零成本装配 {len(cast_entries)} 角色干音锚点完成 -> {vc_path}", flush=True)

    # Persist assembled anchors to Drive workbench for instant future restarts
    if not offline_dry_run:
        tok = get_drive_token()
        if tok and drive_ids:
            try:
                drive_api_upsert_file(vc_path, drive_ids["studio"], tok)
                for wf in sorted(anchors_dir.glob("*.wav")):
                    drive_api_upsert_file(wf, drive_ids["anchors"], tok)
            except Exception as exc:
                print(f"ℹ️ [{project_key}] Drive API 备份锚点跳过 ({exc})", flush=True)
        if drive_studio_dir.exists():
            try:
                (drive_studio_dir / "voice_anchors").mkdir(parents=True, exist_ok=True)
                shutil.copy2(vc_path, drive_studio_dir / "voice_cast_drama3.json")
                for wf in sorted(anchors_dir.glob("*.wav")):
                    shutil.copy2(wf, drive_studio_dir / "voice_anchors" / wf.name)
            except Exception:
                pass
    return vc_path


def stage_project_studio_to_nvme(project_key: str, project_dir: Path, local_studio: Path) -> Path:
    local_studio.mkdir(parents=True, exist_ok=True)
    for sub in ("auditions", "cue_sheets", "voice_anchors", "motifs", "bgm_cache"):
        (local_studio / sub).mkdir(parents=True, exist_ok=True)

    pkg_dst = local_studio / "src" / "aigc_audio_pipeline"
    if pkg_dst.exists():
        shutil.rmtree(pkg_dst)
    shutil.copytree(REPO_ROOT / "src" / "aigc_audio_pipeline", pkg_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    shutil.copy2(
        project_dir / "00_节目圣经与选角档案" / "voice_casting_registry.json",
        local_studio / "voice_casting_registry.json",
    )
    scripts_dir = project_dir / "02_分集广播剧台本"
    for aud_json in sorted(scripts_dir.glob("AUDITION*.json")):
        shutil.copy2(aud_json, local_studio / "auditions" / aud_json.name)
    for ep_json in sorted(scripts_dir.glob("E*.json")):
        shutil.copy2(ep_json, local_studio / "cue_sheets" / ep_json.name)

    shutil.copy2(SCRIPT_PATH.parent / "run_anthology_96gb_studio.py", local_studio / "run_anthology_96gb_studio.py")
    print(f"⚡ [{project_key}] NVMe 工作台组装完成 -> {local_studio}", flush=True)
    return local_studio


def ensure_drive_show_folders(show_folder_name: str, tok: Optional[str]) -> tuple[Path, Path, Path, Optional[dict[str, str]]]:
    proj_root = DRIVE_ROOT / show_folder_name
    studio_dir = proj_root / DRIVE_WORKBENCH_SUB
    outputs_dir = studio_dir / "outputs"
    masters_dir = proj_root / DRIVE_MASTERS_SUB
    if DRIVE_ROOT.exists():
        for d in (studio_dir / "voice_anchors", outputs_dir, masters_dir):
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
    if not tok:
        return studio_dir, outputs_dir, masters_dir, None
    try:
        show_id = drive_api_ensure_folder(show_folder_name, "root", tok)
        studio_id = drive_api_ensure_folder(DRIVE_WORKBENCH_SUB, show_id, tok)
        anchors_id = drive_api_ensure_folder("voice_anchors", studio_id, tok)
        outputs_id = drive_api_ensure_folder("outputs", studio_id, tok)
        masters_id = drive_api_ensure_folder(DRIVE_MASTERS_SUB, show_id, tok)
        return studio_dir, outputs_dir, masters_dir, {
            "show": show_id,
            "studio": studio_id,
            "anchors": anchors_id,
            "outputs": outputs_id,
            "masters": masters_id,
        }
    except Exception:
        return studio_dir, outputs_dir, masters_dir, None


def ensure_uv_and_hf_tools() -> str:
    sh("apt-get update -qq && apt-get install -y -qq ffmpeg git zstd ninja-build build-essential >/dev/null 2>&1 || true")
    uv_bin = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
    if not Path(uv_bin).exists():
        sh("pip install -q uv hf_transfer 'huggingface_hub>=0.26.0'")
        uv_bin = shutil.which("uv") or "uv"
    else:
        sh(f"{uv_bin} pip install --system -q hf_transfer 'huggingface_hub>=0.26.0' || pip install -q hf_transfer 'huggingface_hub>=0.26.0'")
    return uv_bin


def stage_hf_models_nvme(drama_repo: str) -> None:
    from huggingface_hub import snapshot_download

    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for repo_id in (
        drama_repo,
        "OpenMOSS-Team/MOSS-SoundEffect-v2.0",
        "ACE-Step/acestep-v15-xl-turbo-diffusers",
        "Systran/faster-whisper-small",
    ):
        t0 = time.time()
        print(f"🚀 [HF CDN -> NVMe] 预取权重: {repo_id} ...", flush=True)
        snapshot_download(repo_id=repo_id, cache_dir=str(HF_CACHE_DIR))
        print(f"✅ [HF CDN -> NVMe] 权重就绪: {repo_id} ({time.time() - t0:.1f}s)", flush=True)


def build_isolated_venvs(uv_bin: str, refresh_envs: bool = False) -> tuple[Path, Path, Path]:
    ENV_ROOT.mkdir(parents=True, exist_ok=True)
    drama_venv = ENV_ROOT / "drama3-venv"
    moss_venv = ENV_ROOT / "moss-venv"
    acestep_venv = ENV_ROOT / "acestep-venv"
    sgl_repo = ENV_ROOT / "sglang-omni"
    moss_repo = ENV_ROOT / "MOSS-TTS"

    if refresh_envs:
        for d in (drama_venv, moss_venv, acestep_venv):
            shutil.rmtree(d, ignore_errors=True)

    can_cache = DRIVE_WORKSTATION.exists()
    if can_cache:
        DRIVE_REPO_CACHE.mkdir(parents=True, exist_ok=True)

    def _ok(vdir: Path, stmt: str) -> bool:
        py = vdir / "bin/python"
        return py.exists() and subprocess.run([str(py), "-c", stmt], capture_output=True).returncode == 0

    if not (drama_venv / "bin/sgl-omni").exists() or not (drama_venv / "bin/ninja").exists():
        sgl_tar = DRIVE_REPO_CACHE / "sglang_omni_sm120.tar.gz"
        if not sgl_repo.exists():
            if can_cache and sgl_tar.exists():
                sh(f"tar -xzf '{sgl_tar}' -C '{ENV_ROOT}'")
            else:
                sh(f"git clone --depth 1 https://github.com/sgl-project/sglang-omni.git '{sgl_repo}'")
                if can_cache:
                    sh(f"tar -czf '{sgl_tar}' -C '{ENV_ROOT}' sglang-omni || true")
        sh(f"'{uv_bin}' venv '{drama_venv}' --python 3.12 --allow-existing")
        sh(f"cd '{sgl_repo}' && '{uv_bin}' pip install --python '{drama_venv}/bin/python' --prerelease=allow -e '.[fishaudio]' hf_transfer ninja")

    if not _ok(moss_venv, "import moss_soundeffect_v2, scipy, soundfile, faster_whisper"):
        moss_tar = DRIVE_REPO_CACHE / "moss_tts_v2.tar.gz"
        if not moss_repo.exists():
            if can_cache and moss_tar.exists():
                sh(f"tar -xzf '{moss_tar}' -C '{ENV_ROOT}'")
            else:
                sh(f"git clone --depth 1 https://github.com/OpenMOSS/MOSS-TTS.git '{moss_repo}'")
                if can_cache:
                    sh(f"tar -czf '{moss_tar}' -C '{ENV_ROOT}' MOSS-TTS || true")
        sh(f"'{uv_bin}' venv '{moss_venv}' --python 3.12 --allow-existing")
        sh(
            f"'{uv_bin}' pip install --python '{moss_venv}/bin/python' "
            f"--extra-index-url https://download.pytorch.org/whl/cu128 "
            f"--index-strategy unsafe-best-match "
            f"-e '{moss_repo}/moss_soundeffect_v2[torch-cu128]' "
            f"scipy soundfile requests hf_transfer faster-whisper"
        )

    if not _ok(acestep_venv, "from diffusers import AceStepPipeline; import soundfile"):
        sh(f"'{uv_bin}' venv '{acestep_venv}' --python 3.12 --allow-existing")
        sh(
            f"'{uv_bin}' pip install --python '{acestep_venv}/bin/python' "
            f"--extra-index-url https://download.pytorch.org/whl/cu128 "
            f"--index-strategy unsafe-best-match "
            f"'torch==2.9.0+cu128' 'torchaudio==2.9.0+cu128' "
            f"'diffusers>=0.41.0' transformers accelerate safetensors packaging "
            f"soundfile scipy numpy requests hf_transfer sentencepiece protobuf"
        )

    return drama_venv, moss_venv, acestep_venv


def sync_completed_outputs(
    local_outputs: Path,
    synced_markers: set[str],
    *,
    drive_outputs_dir: Path,
    drive_masters_dir: Path,
    drive_ids: Optional[dict[str, str]],
) -> None:
    if not local_outputs.exists():
        return
    tok = get_drive_token()

    def _fuse_cp(fpath: Path) -> None:
        sz = fpath.stat().st_size
        for target_dir in (drive_outputs_dir, drive_masters_dir):
            if target_dir.exists():
                dst = target_dir / fpath.name
                if not dst.exists() or dst.stat().st_size != sz:
                    shutil.copy2(fpath, dst)
                    print(f"☁️ [FUSE 同步] {fpath.name} -> {target_dir}", flush=True)

    for done_file in sorted(local_outputs.glob("*.done")):
        if done_file.name in synced_markers:
            continue
        stem = done_file.stem
        for fpath in sorted(local_outputs.glob(f"{stem}.*")):
            if not fpath.is_file() or fpath.suffix not in (".mp3", ".wav", ".srt", ".json"):
                continue
            if tok and drive_ids:
                try:
                    drive_api_upsert_file(fpath, drive_ids["outputs"], tok)
                    drive_api_upsert_file(fpath, drive_ids["masters"], tok)
                except Exception as exc:
                    print(f"⚠️ Drive API 回退 FUSE ({fpath.name}): {exc}", flush=True)
                    _fuse_cp(fpath)
            else:
                _fuse_cp(fpath)
        synced_markers.add(done_file.name)
        local_wav = local_outputs / f"{stem}.wav"
        local_mp3 = local_outputs / f"{stem}.mp3"
        if ((tok and drive_ids) or drive_masters_dir.exists()) and stem.startswith("E") and local_wav.is_file() and local_mp3.is_file():
            local_wav.unlink(missing_ok=True)


def sync_stem_cache(nvme_cache: Path, drive_cache: Path, direction: str) -> None:
    if not drive_cache.parent.exists():
        return
    pairs: list[tuple[Path, Path]] = []
    for sub in ("acestep_bgm", "moss_sfx"):
        src_d = (drive_cache / sub) if direction == "pull" else (nvme_cache / sub)
        dst_d = (nvme_cache / sub) if direction == "pull" else (drive_cache / sub)
        if not src_d.exists():
            continue
        dst_d.mkdir(parents=True, exist_ok=True)
        for wf in src_d.glob("*.wav"):
            if not wf.name.endswith("_raw.wav"):
                t = dst_d / wf.name
                if not t.exists():
                    pairs.append((wf, t))
    if not pairs:
        return
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(lambda p: shutil.copy2(p[0], p[1]), pairs))


def populate_existing_markers(
    markers_dir: Path,
    *,
    drive_outputs_dir: Path,
    drive_masters_dir: Path,
    drive_ids: Optional[dict[str, str]],
) -> Path:
    markers_dir.mkdir(parents=True, exist_ok=True)
    for d in (drive_outputs_dir, drive_masters_dir):
        if d.exists():
            for nm in os.listdir(d):
                if nm.startswith("E") and nm.endswith(".mp3"):
                    (markers_dir / nm).touch()
    tok = get_drive_token()
    if tok and drive_ids:
        for key in ("outputs", "masters"):
            fid = drive_ids.get(key)
            if not fid:
                continue
            try:
                url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(
                    {"q": f"trashed = false and '{fid}' in parents", "fields": "files(name)", "pageSize": 500}
                )
                req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    for item in json.loads(resp.read().decode("utf-8")).get("files", []):
                        nm = item.get("name", "")
                        if nm.startswith("E") and nm.endswith(".mp3"):
                            (markers_dir / nm).touch()
            except Exception:
                pass
    return markers_dir


def release_colab_runtime() -> None:
    print("🛑 [--auto-unassign] 所有广播剧成片已安全落盘 Google Drive，立即释放 G4 实例止费...", flush=True)
    try:
        (NVME_ROOT / ".colab_auto_unassign").write_text("auto_unassign_after_completion\n", encoding="utf-8")
        os.sync()
    except Exception:
        pass
    try:
        from google.colab import runtime  # type: ignore

        runtime.unassign()
    except Exception as exc:
        print(f"ℹ️ 已写入 .colab_auto_unassign 交由 Notebook 释放实例 ({exc})。", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="通用精品广播剧矩阵 · Colab 96GB G4 零 API 成本一键冷启动与归档器")
    parser.add_argument(
        "--project",
        required=True,
        choices=[*ANTHOLOGY_PROJECTS.keys(), "all"],
        help="选择要渲染的项目：liaozhai_midnight / cthulhu_archives / hayek_1944 / all（三部连跑）",
    )
    parser.add_argument("--episodes", default="AUDITION,E001-E006", help="如 AUDITION,E001 或 AUDITION,E001-E006")
    parser.add_argument("--profile", choices=["fp8", "fast"], default="fp8")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--auto-unassign", "--auto-shutdown", dest="auto_unassign", action="store_true")
    parser.add_argument("--refresh-envs", action="store_true")
    parser.add_argument("--keep-drama-alive", action="store_true", help="批次完成后保留 Drama 3 常驻服务以便下一阶段免冷启动复用")
    parser.add_argument("--offline-dry-run", action="store_true")
    args = parser.parse_args()

    selected_keys = list(ANTHOLOGY_PROJECTS.keys()) if args.project == "all" else [args.project]
    t_boot = time.time()

    print("=" * 80, flush=True)
    print(f"🎭 精品广播剧矩阵 G4 生产线启动 | 目标项目: {', '.join(selected_keys)} | 集数: {args.episodes}", flush=True)
    if not args.offline_dry_run:
        print(sh("nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader || echo 'GPU Check Skipped'").strip(), flush=True)
    print("=" * 80, flush=True)

    use_int4 = args.profile == "fast"
    drama_venv = moss_venv = acestep_venv = Path(sys.executable).parent.parent
    if not args.offline_dry_run:
        try:
            vram_mib = int(float(sh("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits").strip().splitlines()[0]))
            if vram_mib < 85000:
                use_int4 = True
        except Exception:
            pass
        drama_repo = "fishaudio/drama-3-int4" if use_int4 else "fishaudio/drama-3"
        uv_bin = ensure_uv_and_hf_tools()
        bg_errors: list[Exception] = []

        def _dl() -> None:
            try:
                stage_hf_models_nvme(drama_repo)
            except Exception as exc:
                bg_errors.append(exc)

        t_dl = threading.Thread(target=_dl, daemon=True)
        t_dl.start()
        drama_venv, moss_venv, acestep_venv = build_isolated_venvs(uv_bin, refresh_envs=args.refresh_envs)
        t_dl.join()
        if bg_errors:
            raise RuntimeError(f"❌ 模型预取失败: {bg_errors[0]}") from bg_errors[0]
        print(f"⚡ 96GB G4 底层环境与模型权重就绪 ({time.time() - t_boot:.1f}s)", flush=True)

    for idx_p, pkey in enumerate(selected_keys):
        cfg = ANTHOLOGY_PROJECTS[pkey]
        project_dir = REPO_ROOT / cfg["project_rel"]
        local_studio = WORK_BASE / f"{pkey}_studio"
        local_outputs = local_studio / "outputs"
        nvme_cache = WORK_BASE / f"{pkey}_stem_cache"

        stage_project_studio_to_nvme(pkey, project_dir, local_studio)
        tok = None if args.offline_dry_run else get_drive_token()
        drive_studio_dir, drive_outputs_dir, drive_masters_dir, drive_ids = (
            (local_studio, local_outputs, local_outputs, None)
            if args.offline_dry_run
            else ensure_drive_show_folders(cfg["drive_show_folder"], tok)
        )

        prepare_anthology_voice_anchors(
            project_key=pkey,
            project_dir=project_dir,
            local_studio=local_studio,
            drive_studio_dir=drive_studio_dir,
            drive_ids=drive_ids,
            offline_dry_run=args.offline_dry_run,
        )

        if args.offline_dry_run:
            subprocess.run(
                [
                    sys.executable,
                    "-u",
                    str(local_studio / "run_anthology_96gb_studio.py"),
                    "--studio-dir",
                    str(local_studio),
                    "--episodes",
                    args.episodes,
                    "--output-dir",
                    str(local_outputs),
                    "--cache-dir",
                    str(nvme_cache),
                    "--bgm-style",
                    cfg["bgm_style"],
                    "--offline-dry-run",
                ],
                check=True,
            )
            continue

        drive_cache = drive_studio_dir / ".stem_cache"
        sync_stem_cache(nvme_cache, drive_cache, direction="pull")
        existing_markers = (
            populate_existing_markers(
                WORK_BASE / f"{pkey}_existing_markers",
                drive_outputs_dir=drive_outputs_dir,
                drive_masters_dir=drive_masters_dir,
                drive_ids=drive_ids,
            )
            if args.skip_existing
            else None
        )

        cmd = [
            str(moss_venv / "bin/python"),
            "-u",
            str(local_studio / "run_anthology_96gb_studio.py"),
            "--studio-dir",
            str(local_studio),
            "--episodes",
            args.episodes,
            "--output-dir",
            str(local_outputs),
            "--cache-dir",
            str(nvme_cache),
            "--bgm-style",
            cfg["bgm_style"],
            "--sgl-bin",
            str(drama_venv / "bin/sgl-omni"),
            "--moss-python",
            str(moss_venv / "bin/python"),
            "--acestep-python",
            str(acestep_venv / "bin/python"),
        ]
        if existing_markers is not None:
            cmd.extend(["--existing-dir", str(existing_markers)])
        if use_int4:
            cmd.append("--force-int4")
        if args.skip_existing:
            cmd.append("--skip-existing")
        if args.keep_drama_alive or idx_p < len(selected_keys) - 1:
            cmd.append("--keep-drama-alive")

        synced_markers: set[str] = set()
        for attempt in range(1, 4):
            proc = subprocess.Popen(cmd, cwd=str(local_studio), env=os.environ.copy())
            while proc.poll() is None:
                prev_n = len(synced_markers)
                sync_completed_outputs(
                    local_outputs,
                    synced_markers,
                    drive_outputs_dir=drive_outputs_dir,
                    drive_masters_dir=drive_masters_dir,
                    drive_ids=drive_ids,
                )
                if len(synced_markers) > prev_n:
                    sync_stem_cache(nvme_cache, drive_cache, direction="push")
                time.sleep(4.0)
            sync_completed_outputs(
                local_outputs,
                synced_markers,
                drive_outputs_dir=drive_outputs_dir,
                drive_masters_dir=drive_masters_dir,
                drive_ids=drive_ids,
            )
            sync_stem_cache(nvme_cache, drive_cache, direction="push")
            if proc.returncode == 0:
                break
            if attempt < 3:
                print(f"⚠️ [{pkey}] 第 {attempt} 轮异常退出，5s 后自动断点续跑...", flush=True)
                time.sleep(5.0)
            else:
                raise RuntimeError(f"❌ [{pkey}] 连续 3 轮失败 (rc={proc.returncode})")

        print(f"🎉 [{pkey}] {cfg['title']} 归档完成！云盘路径: MyDrive/{cfg['drive_show_folder']}/{DRIVE_MASTERS_SUB}/", flush=True)

    if not args.offline_dry_run and args.auto_unassign:
        os.sync()
        time.sleep(2.0)
        release_colab_runtime()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
