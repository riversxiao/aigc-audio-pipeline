#!/usr/bin/env python3
"""《跨境底牌：硅深暗战》/ Global Edge · Colab 96GB G4 零成本一键冷启动与云盘归档器 (v1.0.0).

零商业语音 API / 零合成 TTS 黄金三件套同卡常驻架构 (~75 GB / 96 GB VRAM)：
  1. Fish Audio Drama 3 (`fishaudio/drama-3` 35B MoE FP8 或 `drama-3-int4`) via SGLang-Omni (+ RAS 高表现力采样)
  2. MOSS-SoundEffect v2.0 (`OpenMOSS-Team/MOSS-SoundEffect-v2.0`, 48kHz 跨国商战纯拟音)
  3. ACE-Step 1.5 XL Turbo (`ACE-Step/acestep-v15-xl-turbo-diffusers`, 48kHz HBO 冷峻室内乐纯器乐)
  4. Faster-Whisper (`small`, CPU int8, 0 MB 显存双语自动回听防吞词质检)

全自动端到端闭环：
  - 生产模式强制执行 `validate_production_voice_cast()`：严格校验 `v2_real_human_studio` 真人棚录干声锚点，
    拦截任何合成/离线占位/遗留语音来源。
  - 原生支持 `AUDITION,E001_VARIANTS` 四变体同台对比批跑、`--skip-existing` 防碰撞断点续跑、
    Google Drive REST API v3 + FUSE 双通道原子同步、`--mirror-to-main-masters` 主母带镜像、
    以及 `--auto-unassign` 完工立停计费。
  - `--offline-dry-run` 在纯 CPU 环境串联 `prepare_global_edge_voice_anchors.py --offline-stub`
    -> `export_drama3_bundle.py --offline-stub` -> `run_global_edge_96gb_studio.py --offline-dry-run`
    完成真实 48kHz `-16 LUFS` 3-bus FFmpeg 母带全链路验证，零污染工作区。
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
from typing import Iterable, Optional
import urllib.parse
import urllib.request
import wave
import zipfile

if os.path.isdir("/content/drive/My Drive") and not os.path.exists("/content/drive/MyDrive"):
    os.symlink("/content/drive/My Drive", "/content/drive/MyDrive")

SCRIPT_PATH = Path(__file__).resolve()
COLAB_DIR = SCRIPT_PATH.parent
REPO_ROOT_CANDIDATE = COLAB_DIR.parent
DEFAULT_PROJECT_DIR = REPO_ROOT_CANDIDATE / "projects" / "global_edge"

NVME_ROOT = Path("/content") if Path("/content").exists() else Path("/tmp")
HF_CACHE_DIR = NVME_ROOT / "hf_cache"
WORK_ROOT = NVME_ROOT / "global_edge_work"
ENV_ROOT = (
    NVME_ROOT / "nine_prison_envs"
    if (NVME_ROOT / "nine_prison_envs" / "drama3-venv" / "bin" / "sgl-omni").exists()
    else (NVME_ROOT / "audio_studio_envs")
)

os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["UV_CONCURRENT_DOWNLOADS"] = "32"

DRIVE_SHOW_FOLDER_NAME = "《跨境底牌：硅深暗战》Global_Edge_双语商战广播剧"
DRIVE_WORKBENCH_FOLDER_NAME = "01_Colab_96GB_FishDrama3_工作台"
DRIVE_MASTERS_FOLDER_NAME = "02_分集双语成片母带_WAV_MP3_SRT"
BUNDLE_ZIP_NAME = "global_edge_96gb_drama3_bundle.zip"

DRIVE_ROOT = Path("/content/drive/MyDrive")
DRIVE_WORKSTATION = DRIVE_ROOT / "AI_Workstation"
DRIVE_REPO_CACHE = DRIVE_WORKSTATION / "AudioStudio_G4_Cache"
DRIVE_PROJECT_ROOT = DRIVE_ROOT / DRIVE_SHOW_FOLDER_NAME
DRIVE_STUDIO_DIR = DRIVE_PROJECT_ROOT / DRIVE_WORKBENCH_FOLDER_NAME
DRIVE_OUTPUTS_DIR = DRIVE_STUDIO_DIR / "outputs"
DRIVE_MAIN_MASTERS_DIR = DRIVE_PROJECT_ROOT / DRIVE_MASTERS_FOLDER_NAME

ANCHOR_SCHEMA_VERSION = "v2_real_human_studio"
CANONICAL_ROLE_IDS: tuple[str, ...] = (
    "lin_chen",
    "zhou_mo",
    "victoria_vance",
    "alistair_finch",
    "claire_chen_gc",
    "rajiv_menon",
    "wei_ling_tan",
    "henrik_lindqvist",
)

OFFLINE_STUB_SOURCE_NAME = "offline_synthetic_stub"
ALWAYS_FORBIDDEN_SOURCE_RE = re.compile(
    r"(?:edge[-_]?tts|neural|zero_cost_studio_anchor:|eleven[-_]?labs)",
    re.IGNORECASE,
)
FORBIDDEN_SYNTHETIC_SOURCE_RE = re.compile(
    r"(?:edge[-_]?tts|neural|offline_synthetic_stub|zero_cost_studio_anchor:|eleven[-_]?labs|synthetic)",
    re.IGNORECASE,
)


def validate_production_voice_cast(
    cast_or_dir: Path,
    required_roles: Iterable[str] | None = None,
    *,
    allow_offline_stub: bool = False,
) -> tuple[bool, list[str]]:
    """Strictly validate that a Global Edge voice cast uses genuine `v2_real_human_studio` anchors.

    Accepts either a studio directory (containing `voice_cast_drama3.json`) or a direct path to
    `voice_cast_drama3.json`. Rejects missing/malformed JSON, wrong schema version, missing roles,
    any synthetic/stub/legacy TTS source name, missing/tiny WAV (<4096 bytes), or blank `anchor_text`.
    When `allow_offline_stub=True` (strictly for `--offline-dry-run`), `offline_synthetic_stub` is
    permitted while legacy schema versions, neural/commercial TTS markers, missing roles, blank
    transcripts, and invalid WAV headers remain strictly rejected.
    """
    errors: list[str] = []
    target = Path(cast_or_dir)
    if target.is_dir():
        base_dir = target
        vc_file = target / "voice_cast_drama3.json"
    else:
        vc_file = target
        base_dir = target.parent

    if not vc_file.is_file():
        return False, [f"Missing voice cast manifest: {vc_file}"]

    try:
        data = json.loads(vc_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"Invalid JSON in {vc_file}: {exc}"]

    if not isinstance(data, dict):
        return False, [f"Voice cast manifest must be a JSON object: {vc_file}"]

    schema_ver = data.get("anchor_schema_version")
    if schema_ver != ANCHOR_SCHEMA_VERSION:
        errors.append(
            f"anchor_schema_version must be {ANCHOR_SCHEMA_VERSION!r}, got {schema_ver!r}"
        )

    characters = data.get("characters")
    if not isinstance(characters, dict) or not characters:
        errors.append("Manifest `characters` mapping is missing or empty.")
        return False, errors

    if required_roles is not None:
        roles_to_check = list(required_roles)
    else:
        reg_path = base_dir / "voice_casting_registry.json"
        if reg_path.is_file():
            try:
                reg_raw = json.loads(reg_path.read_text(encoding="utf-8"))
                roles_to_check = list(reg_raw.get("roles", {}).keys()) or list(CANONICAL_ROLE_IDS)
            except Exception:
                roles_to_check = list(CANONICAL_ROLE_IDS)
        else:
            roles_to_check = list(CANONICAL_ROLE_IDS)

    for role_id in roles_to_check:
        if role_id not in characters:
            errors.append(f"Missing required role_id {role_id!r} in voice_cast_drama3.json")
            continue
        cinfo = characters[role_id]
        if not isinstance(cinfo, dict):
            errors.append(f"Role entry {role_id!r} must be a JSON object")
            continue

        src_name = str(cinfo.get("source_voice_name", "")).strip()
        if not src_name:
            errors.append(f"[{role_id}] source_voice_name is empty")
        elif not (allow_offline_stub and src_name == OFFLINE_STUB_SOURCE_NAME):
            if FORBIDDEN_SYNTHETIC_SOURCE_RE.search(src_name):
                mode_label = "offline dry-run cast" if allow_offline_stub else "production cast"
                errors.append(
                    f"[{role_id}] Forbidden synthetic/stub source_voice_name in {mode_label}: {src_name!r}"
                )

        anchor_wav_rel = str(cinfo.get("anchor_wav", "")).strip()
        if not anchor_wav_rel:
            errors.append(f"[{role_id}] anchor_wav path is empty")
        else:
            anchor_path = Path(anchor_wav_rel)
            if not anchor_path.is_absolute():
                anchor_path = base_dir / anchor_path
            if not anchor_path.is_file():
                errors.append(f"[{role_id}] Missing anchor WAV file: {anchor_path}")
            elif anchor_path.stat().st_size < 4096:
                errors.append(
                    f"[{role_id}] Anchor WAV too small ({anchor_path.stat().st_size} bytes < 4096): {anchor_path}"
                )
            else:
                try:
                    with wave.open(str(anchor_path), "rb") as wf:
                        nch = wf.getnchannels()
                        sw = wf.getsampwidth()
                        sr = wf.getframerate()
                        nframes = wf.getnframes()
                    if nch != 1 or sw != 2 or sr != 44100 or nframes <= 0:
                        errors.append(
                            f"[{role_id}] Anchor WAV header must be 44100 Hz mono 16-bit PCM with >0 frames "
                            f"(got {sr} Hz, {nch} ch, {sw * 8}-bit, {nframes} frames): {anchor_path}"
                        )
                except Exception as exc:
                    errors.append(
                        f"[{role_id}] Corrupt or non-WAV anchor file ({exc}): {anchor_path}"
                    )

        anchor_text = str(cinfo.get("anchor_text", "")).strip()
        if not anchor_text:
            errors.append(f"[{role_id}] anchor_text verbatim transcript is blank")

    return (len(errors) == 0), errors


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
    """Retrieve OAuth token from Colab's local metadata shim if active."""
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
    list_url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(
        {"q": q, "fields": "files(id,name)", "pageSize": 5}
    )
    req = urllib.request.Request(list_url, headers={"Authorization": f"Bearer {tok}"})
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
        headers={
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json; charset=UTF-8",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["id"]


def ensure_drive_show_folders(
    tok: Optional[str],
    *,
    root_folder_id: str = "",
) -> Optional[dict[str, str]]:
    """Ensure Drive folders exist and return Drive folder IDs when REST API is active."""
    if DRIVE_ROOT.exists():
        for d in (
            DRIVE_STUDIO_DIR / "voice_anchors",
            DRIVE_STUDIO_DIR / "custom_anchors",
            DRIVE_OUTPUTS_DIR,
            DRIVE_MAIN_MASTERS_DIR,
        ):
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
    if not tok:
        return None
    try:
        show_id = root_folder_id or drive_api_ensure_folder(DRIVE_SHOW_FOLDER_NAME, "root", tok)
        studio_id = drive_api_ensure_folder(DRIVE_WORKBENCH_FOLDER_NAME, show_id, tok)
        anchors_id = drive_api_ensure_folder("voice_anchors", studio_id, tok)
        outputs_id = drive_api_ensure_folder("outputs", studio_id, tok)
        masters_id = drive_api_ensure_folder(DRIVE_MASTERS_FOLDER_NAME, show_id, tok)
        return {
            "show": show_id,
            "studio": studio_id,
            "anchors": anchors_id,
            "outputs": outputs_id,
            "masters": masters_id,
        }
    except Exception as exc:
        print(f"ℹ️ Drive API 目录初始化回退至 FUSE ({exc})", flush=True)
        return None


def drive_api_download(file_id: str, dest: Path, tok: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
        headers={"Authorization": f"Bearer {tok}"},
    )
    with urllib.request.urlopen(req, timeout=240) as resp, open(dest, "wb") as fout:
        shutil.copyfileobj(resp, fout, length=4 * 1024 * 1024)


def drive_api_upsert_file(local_path: Path, parent_id: str, tok: str) -> None:
    """Atomically create or update `local_path.name` inside Google Drive `parent_id` via REST API v3."""
    mime_type, _ = mimetypes.guess_type(local_path.name)
    if not mime_type:
        if local_path.suffix == ".mp3":
            mime_type = "audio/mpeg"
        elif local_path.suffix == ".srt":
            mime_type = "text/plain"
        else:
            mime_type = "application/octet-stream"

    existing_id = drive_api_find_file_by_name(local_path.name, tok, parent_id=parent_id)
    raw = local_path.read_bytes()
    if existing_id:
        up_req = urllib.request.Request(
            f"https://www.googleapis.com/upload/drive/v3/files/{existing_id}?uploadType=media&fields=id,name,size",
            data=raw,
            method="PATCH",
            headers={
                "Authorization": f"Bearer {tok}",
                "Content-Type": mime_type,
            },
        )
    else:
        boundary = f"global_edge_drama3_{int(time.time() * 1000)}"
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
            headers={
                "Authorization": f"Bearer {tok}",
                "Content-Type": f"multipart/related; boundary={boundary}",
            },
        )
    with urllib.request.urlopen(up_req, timeout=360) as resp:
        info = json.loads(resp.read().decode("utf-8"))
    sz_mb = len(raw) / (1024 * 1024)
    print(f"☁️ [Drive API 原子落盘] {local_path.name} ({sz_mb:.2f} MB, id={info.get('id')})", flush=True)


def stage_global_edge_studio_to_nvme(
    local_studio: Path,
    *,
    project_dir: Path = DEFAULT_PROJECT_DIR,
    cue_sheets_dir: Path | None = None,
    custom_anchors_dir: Path | None = None,
) -> Path:
    """Stage `global_edge_studio` onto NVMe from local Git checkout or `global_edge_96gb_drama3_bundle.zip`."""
    t0 = time.time()
    local_studio.mkdir(parents=True, exist_ok=True)

    meta_dir = project_dir / "00_节目圣经与第一季24集总纲"
    repo_src = REPO_ROOT_CANDIDATE / "src" / "aigc_audio_pipeline"
    repo_colab = REPO_ROOT_CANDIDATE / "colab_96gb"

    if meta_dir.is_dir() and repo_src.is_dir():
        print(f"⚡ 检测到本地源码仓库 ({REPO_ROOT_CANDIDATE})，正在组装 NVMe Global Edge 双语工作台...", flush=True)
        for sub in ("auditions", "cue_sheets", "voice_anchors", "custom_anchors", "motifs", "bgm_cache"):
            (local_studio / sub).mkdir(parents=True, exist_ok=True)

        pkg_dst = local_studio / "src" / "aigc_audio_pipeline"
        if pkg_dst.exists():
            shutil.rmtree(pkg_dst)
        shutil.copytree(repo_src, pkg_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

        shutil.copy2(meta_dir / "voice_casting_registry.json", local_studio / "voice_casting_registry.json")
        if (meta_dir / "anchor_sources.json").is_file():
            shutil.copy2(meta_dir / "anchor_sources.json", local_studio / "anchor_sources.json")

        repo_anchors = meta_dir / "voice_anchors"
        if repo_anchors.is_dir():
            for af in sorted(repo_anchors.iterdir()):
                if af.is_file() and af.suffix.lower() in (".wav", ".txt"):
                    shutil.copy2(af, local_studio / "voice_anchors" / af.name)

        scripts_dir = cue_sheets_dir if cue_sheets_dir is not None else (project_dir / "02_分集广播剧台本")
        if scripts_dir.is_dir():
            for aud_json in sorted(scripts_dir.glob("AUDITION*.json")):
                shutil.copy2(aud_json, local_studio / "auditions" / aud_json.name)
            for ep_json in sorted(scripts_dir.glob("E*.json")):
                shutil.copy2(ep_json, local_studio / "cue_sheets" / ep_json.name)

        for helper_name in (
            "prepare_global_edge_voice_anchors.py",
            "run_global_edge_96gb_studio.py",
            "launch_g4_global_edge_drama3.py",
        ):
            src_h = repo_colab / helper_name
            if src_h.is_file():
                shutil.copy2(src_h, local_studio / helper_name)

        print(f"✅ NVMe 工作台组装完成 ({time.time() - t0:.2f}s) -> {local_studio}", flush=True)
    elif not (local_studio / "voice_casting_registry.json").is_file():
        zip_dst = NVME_ROOT / BUNDLE_ZIP_NAME
        if not zip_dst.is_file():
            fuse_candidates = [
                SCRIPT_PATH.parent / BUNDLE_ZIP_NAME,
                DRIVE_STUDIO_DIR / BUNDLE_ZIP_NAME,
                DRIVE_PROJECT_ROOT / BUNDLE_ZIP_NAME,
                *DRIVE_ROOT.glob(f"*跨境底牌*/**/{BUNDLE_ZIP_NAME}"),
                *DRIVE_ROOT.glob(f"*Global_Edge*/**/{BUNDLE_ZIP_NAME}"),
            ]
            fuse_zip = next((p for p in fuse_candidates if p.is_file()), None)
            tok = get_drive_token()
            if fuse_zip is not None:
                print(f"⬇️ 正在从云盘复制 Global Edge 工程包至本地 NVMe: {fuse_zip} ...", flush=True)
                shutil.copy2(fuse_zip, zip_dst)
            elif tok:
                fid = drive_api_find_file_by_name(BUNDLE_ZIP_NAME, tok)
                if not fid:
                    raise RuntimeError(f"未在 Google Drive 找到 {BUNDLE_ZIP_NAME}，且当前不在源码仓库目录内！")
                print(f"⬇️ 正在通过 Drive API 拉取 {BUNDLE_ZIP_NAME} 至本地 NVMe...", flush=True)
                drive_api_download(fid, zip_dst, tok)
            else:
                raise RuntimeError(
                    f"未检测到本地源码仓库或 {BUNDLE_ZIP_NAME}，请先挂载 Google Drive 或在仓库根目录运行！"
                )

        with zipfile.ZipFile(zip_dst, "r") as zf:
            zf.extractall(local_studio)
        print(f"✅ Global Edge 工程包解压就绪 ({time.time() - t0:.2f}s) -> {local_studio}", flush=True)

    # Pull custom real-human anchors from Drive or explicit `--custom-anchors-dir`
    nvme_custom = local_studio / "custom_anchors"
    nvme_custom.mkdir(parents=True, exist_ok=True)
    for src_custom in (DRIVE_STUDIO_DIR / "custom_anchors", custom_anchors_dir):
        if src_custom and src_custom.is_dir():
            for cf in sorted(src_custom.iterdir()):
                if cf.is_file():
                    shutil.copy2(cf, nvme_custom / cf.name)

    return local_studio


def ensure_real_global_edge_voice_anchors(
    local_studio: Path,
    *,
    python_bin: Path,
    drive_ids: Optional[dict[str, str]],
    custom_anchors_dir: str = "",
    refresh_anchors: bool = False,
) -> None:
    """Restore or prepare genuine `v2_real_human_studio` anchors and enforce `validate_production_voice_cast()`."""
    if not refresh_anchors and not custom_anchors_dir:
        ok, _ = validate_production_voice_cast(local_studio)
        if not ok:
            drive_vc = DRIVE_STUDIO_DIR / "voice_cast_drama3.json"
            drive_anc_dir = DRIVE_STUDIO_DIR / "voice_anchors"
            if drive_vc.is_file() and drive_anc_dir.is_dir():
                try:
                    shutil.copy2(drive_vc, local_studio / "voice_cast_drama3.json")
                    (local_studio / "voice_anchors").mkdir(parents=True, exist_ok=True)
                    for wf in drive_anc_dir.iterdir():
                        if wf.is_file() and wf.suffix.lower() in (".wav", ".txt"):
                            shutil.copy2(wf, local_studio / "voice_anchors" / wf.name)
                    ok, _ = validate_production_voice_cast(local_studio)
                    if ok:
                        print("🎙️ 已从 Google Drive 恢复 8 角色锁死真人棚录干声锚点！", flush=True)
                        return
                except Exception as exc:
                    print(f"ℹ️ 云盘声线锚点读取跳过，将重新制备 ({exc})", flush=True)
        else:
            print("🎙️ 本地 NVMe 8 角色 `v2_real_human_studio` 真人干声锚点校验通过！", flush=True)
            return

    print("🎙️ [声线锚点制备] 正在制备 8 角色 `v2_real_human_studio` 真人棚录参考干声...", flush=True)
    env = os.environ.copy()
    env["PATH"] = f"{python_bin.parent}:{env.get('PATH', '')}"
    prep_cmd = [
        str(python_bin),
        "-u",
        str(local_studio / "prepare_global_edge_voice_anchors.py"),
        "--registry",
        str(local_studio / "voice_casting_registry.json"),
        "--output-dir",
        str(local_studio),
    ]
    if (local_studio / "anchor_sources.json").is_file():
        prep_cmd.extend(["--anchor-sources", str(local_studio / "anchor_sources.json")])
    merged_custom_dir = local_studio / "custom_anchors"
    if custom_anchors_dir:
        src_cli_custom = Path(custom_anchors_dir).resolve()
        if src_cli_custom.is_dir() and src_cli_custom != merged_custom_dir.resolve():
            merged_custom_dir.mkdir(parents=True, exist_ok=True)
            for cf in sorted(src_cli_custom.iterdir()):
                if cf.is_file():
                    shutil.copy2(cf, merged_custom_dir / cf.name)
    if merged_custom_dir.is_dir() and any(p.is_file() for p in merged_custom_dir.iterdir()):
        prep_cmd.extend(["--custom-anchors-dir", str(merged_custom_dir.resolve())])
    elif custom_anchors_dir:
        prep_cmd.extend(["--custom-anchors-dir", str(Path(custom_anchors_dir).resolve())])
    subprocess.run(prep_cmd, env=env, check=True)

    ok, errs = validate_production_voice_cast(local_studio)
    if not ok:
        raise RuntimeError(
            "生产声纹校验 `validate_production_voice_cast()` 未通过，拒绝进入 GPU 推理：\n  - "
            + "\n  - ".join(errs)
        )

    tok = get_drive_token()
    vc_path = local_studio / "voice_cast_drama3.json"
    if tok and drive_ids:
        try:
            drive_api_upsert_file(vc_path, drive_ids["studio"], tok)
            for wf in sorted((local_studio / "voice_anchors").glob("*")):
                if wf.is_file() and wf.suffix.lower() in (".wav", ".txt"):
                    drive_api_upsert_file(wf, drive_ids["anchors"], tok)
        except Exception as exc:
            print(f"⚠️ Drive API 备份声线锚点跳过 ({exc})", flush=True)
    if DRIVE_STUDIO_DIR.exists():
        try:
            (DRIVE_STUDIO_DIR / "voice_anchors").mkdir(parents=True, exist_ok=True)
            shutil.copy2(vc_path, DRIVE_STUDIO_DIR / "voice_cast_drama3.json")
            for wf in sorted((local_studio / "voice_anchors").glob("*")):
                if wf.is_file() and wf.suffix.lower() in (".wav", ".txt"):
                    shutil.copy2(wf, DRIVE_STUDIO_DIR / "voice_anchors" / wf.name)
        except Exception:
            pass


def ensure_uv_and_hf_tools() -> str:
    sh("apt-get update -qq && apt-get install -y -qq ffmpeg git zstd ninja-build build-essential >/dev/null 2>&1 || true")
    uv_bin = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
    if not Path(uv_bin).exists():
        sh("pip install -q uv hf_transfer 'huggingface_hub>=0.26.0'")
        uv_bin = shutil.which("uv") or "uv"
    else:
        sh(
            f"{uv_bin} pip install --system -q hf_transfer 'huggingface_hub>=0.26.0' "
            f"|| pip install -q hf_transfer 'huggingface_hub>=0.26.0'"
        )
    return uv_bin


def stage_hf_models_nvme(drama_repo: str) -> None:
    """Prefetch Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL + faster-whisper-small onto NVMe."""
    from huggingface_hub import snapshot_download  # type: ignore[import-not-found]

    HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    repos = [
        drama_repo,
        "OpenMOSS-Team/MOSS-SoundEffect-v2.0",
        "ACE-Step/acestep-v15-xl-turbo-diffusers",
        "Systran/faster-whisper-small",
    ]
    for repo_id in repos:
        t_m = time.time()
        print(f"🚀 [HF CDN -> NVMe] 高速预取权重: {repo_id} ...", flush=True)
        snapshot_download(repo_id=repo_id, cache_dir=str(HF_CACHE_DIR))
        print(f"✅ [HF CDN -> NVMe] 权重就绪: {repo_id} ({time.time() - t_m:.1f}s)", flush=True)


def build_isolated_venvs(uv_bin: str, refresh_envs: bool = False) -> tuple[Path, Path, Path]:
    """Build or reuse isolated `{drama3,moss,acestep}-venv` (strictly ZERO synthetic TTS packages)."""
    ENV_ROOT.mkdir(parents=True, exist_ok=True)
    drama_venv = ENV_ROOT / "drama3-venv"
    moss_venv = ENV_ROOT / "moss-venv"
    acestep_venv = ENV_ROOT / "acestep-venv"
    sgl_repo = ENV_ROOT / "sglang-omni"
    moss_repo = ENV_ROOT / "MOSS-TTS"

    if refresh_envs:
        shutil.rmtree(drama_venv, ignore_errors=True)
        shutil.rmtree(moss_venv, ignore_errors=True)
        shutil.rmtree(acestep_venv, ignore_errors=True)

    can_cache_drive = DRIVE_WORKSTATION.exists()
    if can_cache_drive:
        DRIVE_REPO_CACHE.mkdir(parents=True, exist_ok=True)

    def _venv_ok(vdir: Path, check_stmt: str) -> bool:
        py = vdir / "bin/python"
        if not py.exists():
            return False
        return subprocess.run([str(py), "-c", check_stmt], capture_output=True).returncode == 0

    # 1. SGLang-Omni (`drama3-venv`)
    if not (drama_venv / "bin/sgl-omni").exists() or not (drama_venv / "bin/ninja").exists():
        t1 = time.time()
        sgl_tar = DRIVE_REPO_CACHE / "sglang_omni_sm120.tar.gz"
        if not sgl_repo.exists():
            if can_cache_drive and sgl_tar.exists():
                print("⚡ 从云盘缓存秒级解压 sglang-omni 源码...", flush=True)
                sh(f"tar -xzf '{sgl_tar}' -C '{ENV_ROOT}'")
            else:
                sh(f"git clone --depth 1 https://github.com/sgl-project/sglang-omni.git '{sgl_repo}'")
                if can_cache_drive:
                    sh(f"tar -czf '{sgl_tar}' -C '{ENV_ROOT}' sglang-omni || true")
        sh(f"'{uv_bin}' venv '{drama_venv}' --python 3.12 --allow-existing")
        sh(
            f"cd '{sgl_repo}' && '{uv_bin}' pip install --python '{drama_venv}/bin/python' "
            f"--prerelease=allow -e '.[fishaudio]' hf_transfer ninja"
        )
        print(f"✅ Drama 3 (SGLang-Omni) 隔离推理环境就绪 ({time.time() - t1:.1f}s)", flush=True)

    # 2. MOSS-SoundEffect v2.0 + faster-whisper (`moss-venv`, zero synthetic TTS packages)
    if not _venv_ok(moss_venv, "import moss_soundeffect_v2, scipy, soundfile, faster_whisper"):
        t2 = time.time()
        moss_tar = DRIVE_REPO_CACHE / "moss_tts_v2.tar.gz"
        if not moss_repo.exists():
            if can_cache_drive and moss_tar.exists():
                print("⚡ 从云盘缓存秒级解压 MOSS-TTS 源码...", flush=True)
                sh(f"tar -xzf '{moss_tar}' -C '{ENV_ROOT}'")
            else:
                sh(f"git clone --depth 1 https://github.com/OpenMOSS/MOSS-TTS.git '{moss_repo}'")
                if can_cache_drive:
                    sh(f"tar -czf '{moss_tar}' -C '{ENV_ROOT}' MOSS-TTS || true")
        sh(f"'{uv_bin}' venv '{moss_venv}' --python 3.12 --allow-existing")
        sh(
            f"'{uv_bin}' pip install --python '{moss_venv}/bin/python' "
            f"--extra-index-url https://download.pytorch.org/whl/cu128 "
            f"--index-strategy unsafe-best-match "
            f"-e '{moss_repo}/moss_soundeffect_v2[torch-cu128]' "
            f"scipy soundfile requests hf_transfer faster-whisper"
        )
        print(f"✅ MOSS-SoundEffect v2.0 + 双语 Whisper 环境就绪 ({time.time() - t2:.1f}s)", flush=True)

    # 3. ACE-Step 1.5 XL (`acestep-venv`)
    if not _venv_ok(acestep_venv, "from diffusers import AceStepPipeline; import soundfile"):
        t3 = time.time()
        sh(f"'{uv_bin}' venv '{acestep_venv}' --python 3.12 --allow-existing")
        sh(
            f"'{uv_bin}' pip install --python '{acestep_venv}/bin/python' "
            f"--extra-index-url https://download.pytorch.org/whl/cu128 "
            f"--index-strategy unsafe-best-match "
            f"'torch==2.9.0+cu128' 'torchaudio==2.9.0+cu128' "
            f"'diffusers>=0.41.0' transformers accelerate safetensors packaging "
            f"soundfile scipy numpy requests hf_transfer sentencepiece protobuf"
        )
        print(f"✅ ACE-Step 1.5 XL HBO 商战纯器乐环境就绪 ({time.time() - t3:.1f}s)", flush=True)

    return drama_venv, moss_venv, acestep_venv


def sync_completed_outputs(
    local_outputs: Path,
    synced_markers: set[str],
    *,
    drive_ids: Optional[dict[str, str]],
    mirror_to_main_masters: bool = False,
) -> None:
    """Atomically sync every finished `.done` stem group to Google Drive (`outputs/` + optional main masters)."""
    if not local_outputs.exists():
        return

    tok = get_drive_token()
    if DRIVE_PROJECT_ROOT.exists():
        DRIVE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        if mirror_to_main_masters:
            DRIVE_MAIN_MASTERS_DIR.mkdir(parents=True, exist_ok=True)

    def _fuse_sync_one(fpath: Path, *, mirror_master: bool) -> None:
        src_sz = fpath.stat().st_size
        targets = [DRIVE_OUTPUTS_DIR]
        if mirror_master:
            targets.append(DRIVE_MAIN_MASTERS_DIR)
        for target_dir in targets:
            if target_dir.exists():
                dst = target_dir / fpath.name
                if not dst.exists() or dst.stat().st_size != src_sz:
                    shutil.copy2(fpath, dst)
                    print(f"☁️ [FUSE 同步] {fpath.name} -> {target_dir}", flush=True)

    for done_file in sorted(local_outputs.glob("*.done")):
        if done_file.name in synced_markers:
            continue
        stem = done_file.stem
        should_mirror = mirror_to_main_masters and (stem.startswith("E") or stem.startswith("AUDITION"))
        related_files = [
            f
            for f in sorted(local_outputs.glob(f"{stem}.*"))
            if f.is_file() and f.suffix in (".mp3", ".wav", ".srt", ".json")
        ]
        for fpath in related_files:
            if tok and drive_ids:
                try:
                    drive_api_upsert_file(fpath, drive_ids["outputs"], tok)
                    if should_mirror:
                        drive_api_upsert_file(fpath, drive_ids["masters"], tok)
                except Exception as exc:
                    print(f"⚠️ Drive API 上传回退至 FUSE ({fpath.name}): {exc}", flush=True)
                    _fuse_sync_one(fpath, mirror_master=should_mirror)
            else:
                _fuse_sync_one(fpath, mirror_master=should_mirror)

        synced_markers.add(done_file.name)
        local_wav = local_outputs / f"{stem}.wav"
        local_mp3 = local_outputs / f"{stem}.mp3"
        if (tok and drive_ids) or DRIVE_OUTPUTS_DIR.exists():
            if stem.startswith("E") and local_wav.is_file() and local_mp3.is_file():
                try:
                    local_wav.unlink()
                except Exception:
                    pass


def seed_and_sync_reusable_stems(nvme_cache: Path, drive_cache: Path, direction: str) -> None:
    """Sync reusable HBO OST BGM & Foley stems between Drive FUSE and local NVMe."""
    if not DRIVE_STUDIO_DIR.exists():
        return
    copy_pairs: list[tuple[Path, Path]] = []
    for sub in ("acestep_bgm", "moss_sfx"):
        src_d = (drive_cache / sub) if direction == "pull" else (nvme_cache / sub)
        dst_d = (nvme_cache / sub) if direction == "pull" else (drive_cache / sub)
        if not src_d.exists():
            continue
        dst_d.mkdir(parents=True, exist_ok=True)
        for wf in src_d.glob("*.wav"):
            if wf.name.endswith("_raw.wav"):
                continue
            target = dst_d / wf.name
            if not target.exists():
                copy_pairs.append((wf, target))

    if not copy_pairs:
        return

    def _cp(pair: tuple[Path, Path]) -> None:
        try:
            shutil.copy2(pair[0], pair[1])
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(_cp, copy_pairs))


def populate_existing_markers_dir(markers_dir: Path, drive_ids: Optional[dict[str, str]]) -> Path:
    """Populate `.mp3` existence markers from Drive so `--skip-existing` skips already-archived episodes."""
    markers_dir.mkdir(parents=True, exist_ok=True)
    for d in (DRIVE_OUTPUTS_DIR, DRIVE_MAIN_MASTERS_DIR):
        if d.exists():
            try:
                for nm in os.listdir(d):
                    if nm.endswith(".mp3") and (nm.startswith("E") or nm.startswith("AUDITION")):
                        (markers_dir / nm).touch()
            except Exception:
                pass

    tok = get_drive_token()
    if tok and drive_ids:
        for key in ("outputs", "masters"):
            folder_id = drive_ids.get(key)
            if not folder_id:
                continue
            try:
                params = {
                    "q": f"trashed = false and '{folder_id}' in parents",
                    "fields": "files(name)",
                    "pageSize": 500,
                }
                req = urllib.request.Request(
                    "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(params),
                    headers={"Authorization": f"Bearer {tok}"},
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                for item in payload.get("files", []):
                    nm = item.get("name", "")
                    if nm.endswith(".mp3") and (nm.startswith("E") or nm.startswith("AUDITION")):
                        (markers_dir / nm).touch()
            except Exception:
                pass
    return markers_dir


def release_colab_runtime() -> None:
    """Destroy the Colab runtime immediately after archiving outputs so 0 idle CCU is burned."""
    print("🛑 [--auto-unassign] 所有双语成片已原子归档至 Google Drive，正在主动释放 G4 运行时立停计费...", flush=True)
    for bridge_p in (NVME_ROOT / "colab_agent_bridge.json", DRIVE_STUDIO_DIR / "colab_agent_bridge.json"):
        try:
            bridge_p.unlink(missing_ok=True)
        except Exception:
            pass
    try:
        (NVME_ROOT / ".colab_auto_unassign").write_text("auto_unassign_after_completion\n", encoding="utf-8")
        os.sync()
    except Exception:
        pass
    try:
        from google.colab import runtime  # type: ignore[import-not-found]

        runtime.unassign()
    except Exception as exc:
        print(f"ℹ️ 已写入 .colab_auto_unassign 交由 Notebook 主内核自动释放实例 ({exc})。", flush=True)


def _is_prepopulated_bundle(bundle_dir: Path) -> bool:
    """Return True if `bundle_dir` already contains a self-contained unpacked Global Edge studio bundle."""
    return (
        (bundle_dir / "voice_casting_registry.json").is_file()
        and (bundle_dir / "voice_cast_drama3.json").is_file()
        and (bundle_dir / "voice_anchors").is_dir()
    )


def run_offline_dry_run_pipeline(args: argparse.Namespace) -> int:
    """Orchestrate full CPU offline dry-run cleanly inside `--output-dir` without touching git working tree."""
    project_dir = Path(args.project_dir).resolve()
    meta_dir = project_dir / "00_节目圣经与第一季24集总纲"
    registry_path = meta_dir / "voice_casting_registry.json"
    anchor_sources_path = meta_dir / "anchor_sources.json"
    cue_sheets_dir = (
        Path(args.cue_sheets_dir).resolve()
        if args.cue_sheets_dir
        else (project_dir / "02_分集广播剧台本")
    )

    run_root = Path(args.output_dir).resolve() if args.output_dir else (WORK_ROOT / "offline_dry_run")
    anchors_dir = run_root / "anchors"
    bundle_dir = Path(args.bundle_dir).resolve() if args.bundle_dir else (run_root / "bundle")
    masters_dir = run_root / "masters"
    cache_dir = run_root / "stem_cache"

    use_prepopulated = False
    if args.bundle_dir and _is_prepopulated_bundle(bundle_dir):
        use_prepopulated = True
    elif not registry_path.is_file() and not args.bundle_dir and _is_prepopulated_bundle(COLAB_DIR):
        bundle_dir = COLAB_DIR.resolve()
        use_prepopulated = True

    masters_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if (bundle_dir / "src" / "aigc_audio_pipeline").is_dir():
        src_path = str((bundle_dir / "src").resolve())
    else:
        src_path = str((REPO_ROOT_CANDIDATE / "src").resolve())
    env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else src_path

    if use_prepopulated:
        ok_cast, cast_errors = validate_production_voice_cast(bundle_dir, allow_offline_stub=True)
        if not ok_cast:
            detail = "\n".join(f"  - {err}" for err in cast_errors)
            raise RuntimeError(
                f"Pre-unpacked bundle failed validate_production_voice_cast(allow_offline_stub=True) "
                f"at {bundle_dir}:\n{detail}"
            )
        studio_script = (
            bundle_dir / "run_global_edge_96gb_studio.py"
            if (bundle_dir / "run_global_edge_96gb_studio.py").is_file()
            else COLAB_DIR / "run_global_edge_96gb_studio.py"
        )
        print(
            f"📦 [Offline Dry-Run] 检测到预解压自包含工程包，跳过步骤 1–2 直接校验并渲染: {bundle_dir}",
            flush=True,
        )
    else:
        anchors_dir.mkdir(parents=True, exist_ok=True)
        bundle_dir.mkdir(parents=True, exist_ok=True)

        prep_script = COLAB_DIR / "prepare_global_edge_voice_anchors.py"
        export_script = project_dir / "scripts" / "export_drama3_bundle.py"
        if not export_script.is_file():
            export_script = REPO_ROOT_CANDIDATE / "projects" / "global_edge" / "scripts" / "export_drama3_bundle.py"
        studio_script = COLAB_DIR / "run_global_edge_96gb_studio.py"

        # Step 1: Prepare FFmpeg-conditioned offline stub voice anchors
        prep_cmd = [
            sys.executable,
            "-u",
            str(prep_script),
            "--registry",
            str(registry_path),
            "--anchor-sources",
            str(anchor_sources_path),
            "--output-dir",
            str(anchors_dir),
            "--offline-stub",
        ]
        if args.custom_anchors_dir:
            prep_cmd.extend(["--custom-anchors-dir", str(Path(args.custom_anchors_dir).resolve())])
        print("🎙️ [Offline Dry-Run 1/3] 制备 44.1kHz -16 LUFS 离线测试声纹锚点...", flush=True)
        subprocess.run(prep_cmd, env=env, check=True)

        # Step 2: Assemble self-contained Drama 3 bundle
        export_cmd = [
            sys.executable,
            "-u",
            str(export_script),
            "--project-dir",
            str(project_dir),
            "--cue-sheets-dir",
            str(cue_sheets_dir),
            "--anchors-dir",
            str(anchors_dir),
            "--output-dir",
            str(bundle_dir),
            "--offline-stub",
        ]
        print("📦 [Offline Dry-Run 2/3] 组装自包含 Colab 96GB 工程包...", flush=True)
        subprocess.run(export_cmd, env=env, check=True)

    # Step 3: Run 3-bus FFmpeg mastering dry-run inside bundle
    studio_cmd = [
        sys.executable,
        "-u",
        str(studio_script),
        "--studio-dir",
        str(bundle_dir),
        "--episodes",
        args.episodes,
        "--output-dir",
        str(masters_dir),
        "--cache-dir",
        str(cache_dir),
        "--offline-dry-run",
    ]
    if args.cue_sheets_dir:
        studio_cmd.extend(["--cue-sheets-dir", str(Path(args.cue_sheets_dir).resolve())])
    if args.skip_existing:
        studio_cmd.append("--skip-existing")
    print("🎚️ [Offline Dry-Run 3/3] 执行 48kHz -16 LUFS 三母线混音与双行双语字幕渲染...", flush=True)
    subprocess.run(studio_cmd, env=env, check=True)

    print(f"✅ [Offline Dry-Run] 全链路闭环完成！母带目录: {masters_dir}", flush=True)
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="《跨境底牌：硅深暗战》/ Global Edge Colab 96GB G4 Fish Audio Drama 3 一键冷启动与归档器"
    )
    parser.add_argument(
        "--episodes",
        default="AUDITION,E001_VARIANTS",
        help="要合成的目标：AUDITION,E001_VARIANTS（默认四变体对比）或 E001_VA / E001-E024 / ALL",
    )
    parser.add_argument(
        "--project-dir",
        default=str(DEFAULT_PROJECT_DIR),
        help="Global Edge 项目目录路径（默认 projects/global_edge）",
    )
    parser.add_argument(
        "--bundle-dir",
        default="",
        help="可选：工程包工作目录路径（默认 NVMe 工作台或 <output-dir>/bundle）",
    )
    parser.add_argument(
        "--cue-sheets-dir",
        default="",
        help="可选：分集台本目录覆盖路径（默认 <project-dir>/02_分集广播剧台本）",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="可选：本地输出根目录（--offline-dry-run 下写入 anchors/、bundle/、masters/）",
    )
    parser.add_argument(
        "--profile",
        choices=["quality", "fast", "fp8"],
        default="quality",
        help="quality/fp8 = 满血 fishaudio/drama-3 (35B MoE FP8, 96GB推荐); fast = fishaudio/drama-3-int4",
    )
    parser.add_argument(
        "--custom-anchors-dir",
        default="",
        help="可选：真人录音棚干声投放目录（含 <role_id>.{wav,mp3,m4a,flac} 与可选 .txt）",
    )
    parser.add_argument("--refresh-anchors", action="store_true", help="强制重新制备 8 角色真人参考干声锚点")
    parser.add_argument("--skip-existing", action="store_true", help="跳过本地或云盘已存在成片的变体/剧集")
    parser.add_argument(
        "--mirror-to-main-masters",
        action="store_true",
        help="除 outputs/ 外同步镜像归档至 02_分集双语成片母带_WAV_MP3_SRT/",
    )
    parser.add_argument(
        "--auto-unassign",
        "--auto-shutdown",
        dest="auto_unassign",
        action="store_true",
        help="全部成片落盘 Google Drive 后自动释放 G4 实例立停 CCU 计费",
    )
    parser.add_argument("--refresh-envs", action="store_true", help="强制重建三路隔离虚拟环境")
    parser.add_argument("--offline-dry-run", action="store_true", help="纯 CPU 离线全链路干跑自检（无需 GPU/网络）")
    parser.add_argument("--drive-folder-id", default="", help="可选：显式指定 Google Drive 节目根目录 ID")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    t_boot = time.time()
    print("=" * 80, flush=True)
    print("🎙️ 《跨境底牌：硅深暗战》/ Global Edge · 96GB G4 零 API 双语多变体生产线启动", flush=True)
    if not args.offline_dry_run:
        print(
            sh("nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader || echo 'GPU Check Skipped'").strip(),
            flush=True,
        )
    print("=" * 80, flush=True)

    if args.offline_dry_run:
        return run_offline_dry_run_pipeline(args)

    target_studio_dir = (
        Path(args.bundle_dir).resolve() if args.bundle_dir else (WORK_ROOT / "global_edge_studio")
    )
    local_studio = stage_global_edge_studio_to_nvme(
        target_studio_dir,
        project_dir=Path(args.project_dir).resolve(),
        cue_sheets_dir=Path(args.cue_sheets_dir).resolve() if args.cue_sheets_dir else None,
        custom_anchors_dir=Path(args.custom_anchors_dir).resolve() if args.custom_anchors_dir else None,
    )
    tok = get_drive_token()
    drive_ids = ensure_drive_show_folders(tok, root_folder_id=args.drive_folder_id)

    use_int4 = args.profile == "fast"
    try:
        vram_mib = int(
            float(
                sh("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits")
                .strip()
                .splitlines()[0]
            )
        )
        if vram_mib < 85000:
            print(f"ℹ️ 检测到显存 {vram_mib} MiB (<85GB)，自动切换为 fishaudio/drama-3-int4 显存接力模式", flush=True)
            use_int4 = True
    except Exception:
        pass
    drama_repo = "fishaudio/drama-3-int4" if use_int4 else "fishaudio/drama-3"

    uv_bin = ensure_uv_and_hf_tools()
    print(f"=== [并发冷启动] 通道 A: HF CDN 高速预取 ({drama_repo}) || 通道 B: 隔离环境就绪 ===", flush=True)
    bg_errors: list[Exception] = []

    def _download_worker() -> None:
        try:
            stage_hf_models_nvme(drama_repo)
        except Exception as exc:
            bg_errors.append(exc)

    t_dl = threading.Thread(target=_download_worker, daemon=True)
    t_dl.start()

    drama_venv, moss_venv, acestep_venv = build_isolated_venvs(uv_bin, refresh_envs=args.refresh_envs)
    t_dl.join()
    if bg_errors:
        raise RuntimeError(f"❌ 模型高速预取失败: {bg_errors[0]}") from bg_errors[0]

    ensure_real_global_edge_voice_anchors(
        local_studio,
        python_bin=moss_venv / "bin/python",
        drive_ids=drive_ids,
        custom_anchors_dir=args.custom_anchors_dir,
        refresh_anchors=args.refresh_anchors,
    )
    print(f"⚡ G4 预热与 8 角色真人棚录声纹全部就绪！耗时: {time.time() - t_boot:.1f}s", flush=True)

    local_outputs = Path(args.output_dir).resolve() if args.output_dir else (local_studio / "outputs")
    local_outputs.mkdir(parents=True, exist_ok=True)
    nvme_cache = WORK_ROOT / "stem_cache"
    drive_cache = DRIVE_STUDIO_DIR / ".stem_cache"
    seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="pull")
    existing_markers = (
        populate_existing_markers_dir(WORK_ROOT / "drive_existing_markers", drive_ids)
        if args.skip_existing
        else None
    )

    cmd = [
        str(moss_venv / "bin/python"),
        "-u",
        str(local_studio / "run_global_edge_96gb_studio.py"),
        "--studio-dir",
        str(local_studio),
        "--episodes",
        args.episodes,
        "--output-dir",
        str(local_outputs),
        "--cache-dir",
        str(nvme_cache),
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

    synced_markers: set[str] = set()
    sync_completed_outputs(
        local_outputs,
        synced_markers,
        drive_ids=drive_ids,
        mirror_to_main_masters=args.mirror_to_main_masters,
    )

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        attempt_cmd = list(cmd)
        if attempt > 1 and "--skip-existing" not in attempt_cmd:
            attempt_cmd.append("--skip-existing")
        if existing_markers is not None:
            populate_existing_markers_dir(existing_markers, drive_ids)
        elif attempt > 1:
            retry_markers = populate_existing_markers_dir(
                WORK_ROOT / "drive_existing_markers", drive_ids
            )
            if "--existing-dir" not in attempt_cmd:
                attempt_cmd.extend(["--existing-dir", str(retry_markers)])
        print(
            f"=== [开始双语多变体合成 · 第 {attempt}/{max_attempts} 轮] 任务: {args.episodes} | 引擎: {drama_repo} ===",
            flush=True,
        )
        proc = subprocess.Popen(attempt_cmd, cwd=str(local_studio), env=os.environ.copy())
        while proc.poll() is None:
            prev_n = len(synced_markers)
            sync_completed_outputs(
                local_outputs,
                synced_markers,
                drive_ids=drive_ids,
                mirror_to_main_masters=args.mirror_to_main_masters,
            )
            if len(synced_markers) > prev_n:
                seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="push")
            time.sleep(4.0)

        sync_completed_outputs(
            local_outputs,
            synced_markers,
            drive_ids=drive_ids,
            mirror_to_main_masters=args.mirror_to_main_masters,
        )
        seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="push")

        if proc.returncode == 0:
            break
        if attempt < max_attempts:
            print(
                f"⚠️ [自动守护] run_global_edge_96gb_studio.py 退出 (rc={proc.returncode})，已完成母带已归档，5s 后断点续跑...",
                flush=True,
            )
            time.sleep(5.0)
        else:
            raise RuntimeError(
                f"❌ run_global_edge_96gb_studio.py 连续 {max_attempts} 次异常退出 (rc={proc.returncode})"
            )

    os.sync()
    time.sleep(2.0)

    print("\n" + "=" * 80, flush=True)
    print(
        f"🎉 《跨境底牌：硅深暗战》双语成片渲染与 Google Drive 原子归档全部完成！共归档: {len(synced_markers)} 项 | "
        f"总耗时: {time.time() - t_boot:.1f}s",
        flush=True,
    )
    print(f"📂 Google Drive 成品目录: MyDrive/{DRIVE_SHOW_FOLDER_NAME}/{DRIVE_MASTERS_FOLDER_NAME}/", flush=True)
    print("=" * 80, flush=True)

    if args.auto_unassign:
        release_colab_runtime()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
