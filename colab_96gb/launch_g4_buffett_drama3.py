#!/usr/bin/env python3
"""《穿越周期的信》——巴菲特致股东信双语圆桌 · Colab 96GB G4 零成本一键冷启动与云盘归档器 (v1.0.0).

零 API 成本黄金三件套同卡常驻架构 (~75.0 GB / 96 GB VRAM)：
  1. Fish Audio Drama 3 (`fishaudio/drama-3` 35B MoE FP8 或 `drama-3-int4`) via SGLang-Omni (+ RAS 高表现力圆桌采样)
  2. MOSS-SoundEffect v2.0 (`OpenMOSS-Team/MOSS-SoundEffect-v2.0`, 48kHz 商业纪实拟音：年报翻页/1980s机械打字机/休市钟)
  3. ACE-Step 1.5 XL Turbo (`ACE-Step/acestep-v15-xl-turbo-diffusers`, 48kHz 美式指弹木吉他/室内乐大提琴/毛毡钢琴纯器乐)
  4. Faster-Whisper (`small`, CPU int8, 0 MB 显存开销中英双语自动回听防吞词质检)

全自动端到端闭环：
  - 自动兼容源码仓库直跑（`git clone`）或独立 `buffett_letters_96gb_drama3_bundle.zip` 解压直跑。
  - 自动复用云盘 `AI_Workstation/AudioStudio_G4_Cache` 与已有虚拟环境，秒级增量补齐 `yt-dlp` / `edge-tts`。
  - 首次运行自动提纯 1980s–90s 壮年巴菲特公开演讲真实干音 + 制备 3 位现代中文圆桌主播参考干音，并持久化锁死至云盘，确保全 50 期节目声线 100% 恒定。
  - 每完成一期（检测到 `.done` 原子标记），立即通过 Google Drive REST API v3 / FUSE 双通道将 WAV + 320k MP3 + 零重叠中英双语 SRT + JSON 归档至云盘 `《穿越周期的信》巴菲特股东信双语圆桌节目/`，支持 `--auto-unassign` 完工立停计费！
"""

from __future__ import annotations

import argparse
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
from typing import Optional
import urllib.parse
import urllib.request
import zipfile

# 1. Heal `colab dfs mount` path with space (`/content/drive/My Drive` -> `/content/drive/MyDrive`)
if os.path.isdir("/content/drive/My Drive") and not os.path.exists("/content/drive/MyDrive"):
    os.symlink("/content/drive/My Drive", "/content/drive/MyDrive")

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT_CANDIDATE = SCRIPT_PATH.parent.parent

NVME_ROOT = Path("/content") if Path("/content").exists() else Path("/tmp")
HF_CACHE_DIR = NVME_ROOT / "hf_cache"
WORK_ROOT = NVME_ROOT / "buffett_letters_work"
# Reuse existing warm G4 virtualenvs if already built on this instance
ENV_ROOT = (
    NVME_ROOT / "nine_prison_envs"
    if (NVME_ROOT / "nine_prison_envs" / "drama3-venv" / "bin" / "sgl-omni").exists()
    else (NVME_ROOT / "audio_studio_envs")
)

os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["UV_CONCURRENT_DOWNLOADS"] = "32"

DRIVE_SHOW_FOLDER_NAME = "《穿越周期的信》巴菲特股东信双语圆桌节目"
DRIVE_WORKBENCH_FOLDER_NAME = "01_Colab_96GB_FishDrama3_工作台"
DRIVE_MASTERS_FOLDER_NAME = "02_分期双语成片母带_WAV_MP3_SRT"
BUNDLE_ZIP_NAME = "buffett_letters_96gb_drama3_bundle.zip"

DRIVE_ROOT = Path("/content/drive/MyDrive")
DRIVE_WORKSTATION = DRIVE_ROOT / "AI_Workstation"
DRIVE_REPO_CACHE = DRIVE_WORKSTATION / "AudioStudio_G4_Cache"
DRIVE_PROJECT_ROOT = DRIVE_ROOT / DRIVE_SHOW_FOLDER_NAME
DRIVE_STUDIO_DIR = DRIVE_PROJECT_ROOT / DRIVE_WORKBENCH_FOLDER_NAME
DRIVE_OUTPUTS_DIR = DRIVE_STUDIO_DIR / "outputs"
DRIVE_MAIN_MASTERS_DIR = DRIVE_PROJECT_ROOT / DRIVE_MASTERS_FOLDER_NAME


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
    """Retrieve OAuth token from Colab's local metadata shim (`172.28.0.1:8009` or `127.0.0.1:8012`) if active."""
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


def drive_api_find_file_by_name(name: str, tok: str, *, parent_id: Optional[str] = None, mime_type: Optional[str] = None) -> Optional[str]:
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


def ensure_drive_show_folders(tok: Optional[str]) -> Optional[dict[str, str]]:
    """Ensure Drive folders exist and return `{root, studio, outputs, masters}` Drive IDs when REST API is active."""
    if DRIVE_ROOT.exists():
        for d in (DRIVE_STUDIO_DIR / "voice_anchors", DRIVE_STUDIO_DIR / "custom_anchors", DRIVE_OUTPUTS_DIR, DRIVE_MAIN_MASTERS_DIR):
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
    if not tok:
        return None
    try:
        show_id = drive_api_ensure_folder(DRIVE_SHOW_FOLDER_NAME, "root", tok)
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
        boundary = f"buffett_drama3_{int(time.time() * 1000)}"
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


def stage_buffett_studio_to_nvme(local_studio: Path) -> Path:
    """Stage `buffett_studio` onto NVMe from either local Git checkout or `buffett_letters_96gb_drama3_bundle.zip`."""
    t0 = time.time()
    local_studio.mkdir(parents=True, exist_ok=True)

    repo_proj = REPO_ROOT_CANDIDATE / "projects" / "buffett_letters"
    repo_src = REPO_ROOT_CANDIDATE / "src" / "aigc_audio_pipeline"
    repo_colab = REPO_ROOT_CANDIDATE / "colab_96gb"

    if repo_proj.is_dir() and repo_src.is_dir():
        print(f"⚡ 检测到本地源码仓库 ({REPO_ROOT_CANDIDATE})，正在组装 NVMe 双语圆桌工作台...", flush=True)
        for sub in ("auditions", "cue_sheets", "voice_anchors", "custom_anchors", "motifs", "bgm_cache"):
            (local_studio / sub).mkdir(parents=True, exist_ok=True)

        pkg_dst = local_studio / "src" / "aigc_audio_pipeline"
        if pkg_dst.exists():
            shutil.rmtree(pkg_dst)
        shutil.copytree(repo_src, pkg_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

        shutil.copy2(
            repo_proj / "00_节目圣经与第一季12期总纲" / "voice_casting_registry.json",
            local_studio / "voice_casting_registry.json",
        )
        repo_anchors = repo_proj / "00_节目圣经与第一季12期总纲" / "voice_anchors"
        if repo_anchors.is_dir():
            (local_studio / "voice_anchors").mkdir(parents=True, exist_ok=True)
            for af in sorted(repo_anchors.iterdir()):
                if af.is_file() and af.suffix.lower() in (".wav", ".txt"):
                    shutil.copy2(af, local_studio / "voice_anchors" / af.name)
        scripts_dir = repo_proj / "02_分期圆桌台本"
        for aud_json in sorted(scripts_dir.glob("AUDITION*.json")):
            shutil.copy2(aud_json, local_studio / "auditions" / aud_json.name)
        for ep_json in sorted(scripts_dir.glob("E*.json")):
            shutil.copy2(ep_json, local_studio / "cue_sheets" / ep_json.name)

        for helper_name in (
            "prepare_buffett_voice_anchors.py",
            "run_buffett_96gb_studio.py",
            "launch_g4_buffett_drama3.py",
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
                *DRIVE_ROOT.glob(f"*穿越周期的信*/**/{BUNDLE_ZIP_NAME}"),
            ]
            fuse_zip = next((p for p in fuse_candidates if p.is_file()), None)
            tok = get_drive_token()
            if fuse_zip is not None:
                print(f"⬇️ 正在从云盘复制《穿越周期的信》工程包至本地 NVMe: {fuse_zip} ...", flush=True)
                shutil.copy2(fuse_zip, zip_dst)
            elif tok:
                fid = drive_api_find_file_by_name(BUNDLE_ZIP_NAME, tok)
                if not fid:
                    raise RuntimeError(
                        f"未在 Google Drive 找到 {BUNDLE_ZIP_NAME}，且当前不在源码仓库目录内！"
                    )
                print(f"⬇️ 正在通过 Drive API 拉取 {BUNDLE_ZIP_NAME} 至本地 NVMe...", flush=True)
                drive_api_download(fid, zip_dst, tok)
            else:
                raise RuntimeError(
                    f"未检测到本地源码仓库或 {BUNDLE_ZIP_NAME}，请先挂载 Google Drive 或在仓库根目录运行！"
                )

        with zipfile.ZipFile(zip_dst, "r") as zf:
            zf.extractall(local_studio)
        print(f"✅ 《穿越周期的信》工程包解压就绪 ({time.time() - t0:.2f}s) -> {local_studio}", flush=True)

    # Pull any user-supplied custom vocal clips from Drive `custom_anchors/` if present
    drive_custom_dir = DRIVE_STUDIO_DIR / "custom_anchors"
    if drive_custom_dir.is_dir():
        nvme_custom = local_studio / "custom_anchors"
        nvme_custom.mkdir(parents=True, exist_ok=True)
        for cf in drive_custom_dir.iterdir():
            if cf.is_file():
                shutil.copy2(cf, nvme_custom / cf.name)

    return local_studio


def _anchors_are_real_and_complete(studio_dir: Path) -> bool:
    vc_file = studio_dir / "voice_cast_drama3.json"
    if not vc_file.is_file():
        return False
    try:
        data = json.loads(vc_file.read_text(encoding="utf-8"))
        if data.get("anchor_schema_version") != "v2_real_human_studio":
            return False
        chars = data.get("characters", {})
        for role_id in ("host_zhiwei", "guest_huaiyuan", "guest_laozhou", "buffett_prime_en"):
            if role_id not in chars:
                return False
            cinfo = chars[role_id]
            src_name = str(cinfo.get("source_voice_name", ""))
            if (
                src_name == "offline_synthetic_stub"
                or src_name.startswith("zero_cost_studio_anchor:")
                or "Neural" in src_name
            ):
                return False
            ap = studio_dir / cinfo.get("anchor_wav", "")
            if not ap.is_file() or ap.stat().st_size < 4096:
                return False
            if not str(cinfo.get("anchor_text", "")).strip():
                return False
        return True
    except Exception:
        return False


def ensure_real_buffett_voice_anchors(
    local_studio: Path,
    *,
    python_bin: Path,
    drive_ids: Optional[dict[str, str]],
    buffett_source: str = "",
    refresh_anchors: bool = False,
    offline_dry_run: bool = False,
) -> None:
    """Ensure the 4 locked vocal anchors exist (pulling from Drive cache if available, else building & caching)."""
    if offline_dry_run:
        if not (local_studio / "voice_cast_drama3.json").is_file():
            subprocess.run(
                [
                    sys.executable,
                    str(local_studio / "prepare_buffett_voice_anchors.py"),
                    "--registry",
                    str(local_studio / "voice_casting_registry.json"),
                    "--output-dir",
                    str(local_studio),
                    "--offline-stub",
                ],
                check=True,
            )
        return

    # 1. Try restoring locked vocal anchors from Google Drive so all 50 episodes stay 100% voice-consistent
    if not refresh_anchors and not buffett_source and not _anchors_are_real_and_complete(local_studio):
        drive_vc = DRIVE_STUDIO_DIR / "voice_cast_drama3.json"
        drive_anc_dir = DRIVE_STUDIO_DIR / "voice_anchors"
        if drive_vc.is_file() and drive_anc_dir.is_dir():
            try:
                shutil.copy2(drive_vc, local_studio / "voice_cast_drama3.json")
                (local_studio / "voice_anchors").mkdir(parents=True, exist_ok=True)
                for wf in drive_anc_dir.glob("*.wav"):
                    shutil.copy2(wf, local_studio / "voice_anchors" / wf.name)
                if _anchors_are_real_and_complete(local_studio):
                    print("🎙️ 已从 Google Drive 恢复全季锁死四角色真实干音锚点，声线 100% 跨集恒定！", flush=True)
                    return
            except Exception as exc:
                print(f"ℹ️ 云盘声线锚点读取跳过，将重新制备 ({exc})", flush=True)

    if not refresh_anchors and not buffett_source and _anchors_are_real_and_complete(local_studio):
        print("🎙️ 本地 NVMe 四角色真实干音锚点校验通过！", flush=True)
        return

    # 2. Build zero-cost real vocal anchors via `prepare_buffett_voice_anchors.py`
    print("🎙️ [首次声线定角] 正在零成本提纯 1980s–90s 壮年巴菲特演讲原声 + 现代中文圆桌主播参考干音...", flush=True)
    env = os.environ.copy()
    env["PATH"] = f"{python_bin.parent}:{env.get('PATH', '')}"
    prep_cmd = [
        str(python_bin),
        "-u",
        str(local_studio / "prepare_buffett_voice_anchors.py"),
        "--registry",
        str(local_studio / "voice_casting_registry.json"),
        "--output-dir",
        str(local_studio),
    ]
    if buffett_source:
        prep_cmd.extend(["--buffett-source", buffett_source])
    subprocess.run(prep_cmd, env=env, check=True)

    # 3. Persist locked anchors back to Google Drive (REST API + FUSE)
    tok = get_drive_token()
    vc_path = local_studio / "voice_cast_drama3.json"
    if tok and drive_ids:
        try:
            drive_api_upsert_file(vc_path, drive_ids["studio"], tok)
            for wf in sorted((local_studio / "voice_anchors").glob("*.wav")):
                drive_api_upsert_file(wf, drive_ids["anchors"], tok)
        except Exception as exc:
            print(f"⚠️ Drive API 备份声线锚点跳过 ({exc})", flush=True)
    if DRIVE_STUDIO_DIR.exists():
        try:
            (DRIVE_STUDIO_DIR / "voice_anchors").mkdir(parents=True, exist_ok=True)
            shutil.copy2(vc_path, DRIVE_STUDIO_DIR / "voice_cast_drama3.json")
            for wf in sorted((local_studio / "voice_anchors").glob("*.wav")):
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
    from huggingface_hub import snapshot_download

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
    """Build or reuse isolated `{drama3,moss,acestep}-venv` with Drive tarball cache + `yt-dlp`/`edge-tts`."""
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

    # 1. SGLang-Omni (`drama3-venv` — Blackwell sm_120 compatible + ninja for FlashInfer JIT)
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
        sh(f"cd '{sgl_repo}' && '{uv_bin}' pip install --python '{drama_venv}/bin/python' --prerelease=allow -e '.[fishaudio]' hf_transfer ninja")
        print(f"✅ Drama 3 (SGLang-Omni) 隔离推理环境就绪 ({time.time() - t1:.1f}s)", flush=True)

    # 2. MOSS-SoundEffect v2.0 + faster-whisper + yt-dlp + edge-tts (`moss-venv`)
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
            f"scipy soundfile requests hf_transfer faster-whisper yt-dlp edge-tts"
        )
        print(f"✅ MOSS-SoundEffect v2.0 + 双语 Whisper + 干音制备环境就绪 ({time.time() - t2:.1f}s)", flush=True)
    elif not _venv_ok(moss_venv, "import yt_dlp, edge_tts"):
        sh(f"'{uv_bin}' pip install --python '{moss_venv}/bin/python' yt-dlp edge-tts")

    # 3. ACE-Step 1.5 XL (`acestep-venv` — diffusers >= 0.41.0)
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
        print(f"✅ ACE-Step 1.5 XL 美式原声配乐环境就绪 ({time.time() - t3:.1f}s)", flush=True)

    return drama_venv, moss_venv, acestep_venv


def sync_completed_outputs(
    local_outputs: Path,
    synced_markers: set[str],
    *,
    drive_ids: Optional[dict[str, str]],
) -> None:
    """Atomically sync every finished `.done` stem group to Google Drive (`outputs/` + `02_分期双语成片母带_WAV_MP3_SRT/`)."""
    if not local_outputs.exists():
        return

    tok = get_drive_token()
    if DRIVE_PROJECT_ROOT.exists():
        DRIVE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        DRIVE_MAIN_MASTERS_DIR.mkdir(parents=True, exist_ok=True)

    def _fuse_sync_one(fpath: Path) -> None:
        src_sz = fpath.stat().st_size
        for target_dir in (DRIVE_OUTPUTS_DIR, DRIVE_MAIN_MASTERS_DIR):
            if target_dir.exists():
                dst = target_dir / fpath.name
                if not dst.exists() or dst.stat().st_size != src_sz:
                    shutil.copy2(fpath, dst)
                    print(f"☁️ [FUSE 同步] {fpath.name} -> {target_dir}", flush=True)

    for done_file in sorted(local_outputs.glob("*.done")):
        if done_file.name in synced_markers:
            continue
        stem = done_file.stem
        related_files = [
            f
            for f in sorted(local_outputs.glob(f"{stem}.*"))
            if f.is_file() and f.suffix in (".mp3", ".wav", ".srt", ".json")
        ]
        for fpath in related_files:
            if tok and drive_ids:
                try:
                    drive_api_upsert_file(fpath, drive_ids["outputs"], tok)
                    drive_api_upsert_file(fpath, drive_ids["masters"], tok)
                except Exception as exc:
                    print(f"⚠️ Drive API 上传回退至 FUSE ({fpath.name}): {exc}", flush=True)
                    _fuse_sync_one(fpath)
            else:
                _fuse_sync_one(fpath)

        synced_markers.add(done_file.name)
        # Reclaim ~220MB local NVMe master .wav once safely archived (keep .mp3 + .srt + .done)
        local_wav = local_outputs / f"{stem}.wav"
        local_mp3 = local_outputs / f"{stem}.mp3"
        if (tok and drive_ids) or DRIVE_MAIN_MASTERS_DIR.exists():
            if stem.startswith("E") and local_wav.is_file() and local_mp3.is_file():
                try:
                    local_wav.unlink()
                except Exception:
                    pass


def seed_and_sync_reusable_stems(nvme_cache: Path, drive_cache: Path, direction: str) -> None:
    """Sync reusable documentary BGM & Foley stems between Drive FUSE and local NVMe."""
    from concurrent.futures import ThreadPoolExecutor

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
                    if nm.startswith("E") and nm.endswith(".mp3"):
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
                    if nm.startswith("E") and nm.endswith(".mp3"):
                        (markers_dir / nm).touch()
            except Exception:
                pass
    return markers_dir


def release_colab_runtime() -> None:
    """Destroy the Colab runtime immediately after archiving outputs so 0 idle CCU is burned."""
    print("🛑 [--auto-unassign] 所有双语成片已原子归档至 Google Drive，正在主动释放 G4 运行时立停计费...", flush=True)
    try:
        (NVME_ROOT / ".colab_auto_unassign").write_text("auto_unassign_after_completion\n", encoding="utf-8")
        os.sync()
    except Exception:
        pass
    try:
        from google.colab import runtime  # type: ignore

        runtime.unassign()
    except Exception as exc:
        print(f"ℹ️ 已写入 .colab_auto_unassign 交由 Notebook 主内核自动释放实例 ({exc})。", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="《穿越周期的信》 Colab 96GB G4 Fish Drama 3 零成本一键冷启动与归档器")
    parser.add_argument(
        "--episodes",
        default="AUDITION,E001",
        help="要合成的期数，如 AUDITION,E001（四角色试听+首期2008致股东信）或 E001-E012",
    )
    parser.add_argument(
        "--profile",
        choices=["fp8", "fast"],
        default="fp8",
        help="fp8 = 满血 fishaudio/drama-3 (35B MoE FP8, 96G推荐); fast = fishaudio/drama-3-int4 (20.8GB)",
    )
    parser.add_argument("--buffett-source", default="", help="可选：自定义 1980s-90s 壮年巴菲特音频/视频文件路径")
    parser.add_argument("--refresh-anchors", action="store_true", help="强制重新制备四角色参考干音锚点")
    parser.add_argument("--skip-existing", action="store_true", help="跳过本地或云盘已存在成片的期数")
    parser.add_argument(
        "--auto-unassign",
        "--auto-shutdown",
        dest="auto_unassign",
        action="store_true",
        help="全部成品落盘 Google Drive 后自动释放 G4 实例立停 CCU 计费",
    )
    parser.add_argument("--refresh-envs", action="store_true", help="强制重建虚拟环境")
    parser.add_argument("--offline-dry-run", action="store_true", help="CPU 离线全链路干跑自检（无需 GPU / 网络）")
    args = parser.parse_args()

    t_boot = time.time()
    print("=" * 80, flush=True)
    print("🎙️ 《穿越周期的信》——巴菲特50年致股东信双语圆桌 · 96GB G4 零成本生产线启动", flush=True)
    if not args.offline_dry_run:
        print(
            sh("nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader || echo 'GPU Check Skipped'").strip(),
            flush=True,
        )
    print("=" * 80, flush=True)

    local_studio = stage_buffett_studio_to_nvme(WORK_ROOT / "buffett_studio")
    tok = None if args.offline_dry_run else get_drive_token()
    drive_ids = None if args.offline_dry_run else ensure_drive_show_folders(tok)

    if args.offline_dry_run:
        ensure_real_buffett_voice_anchors(
            local_studio,
            python_bin=Path(sys.executable),
            drive_ids=None,
            offline_dry_run=True,
        )
        local_outputs = local_studio / "outputs"
        nvme_cache = WORK_ROOT / "stem_cache"
        subprocess.run(
            [
                sys.executable,
                "-u",
                str(local_studio / "run_buffett_96gb_studio.py"),
                "--studio-dir",
                str(local_studio),
                "--episodes",
                args.episodes,
                "--output-dir",
                str(local_outputs),
                "--cache-dir",
                str(nvme_cache),
                "--offline-dry-run",
            ],
            check=True,
        )
        return 0

    use_int4 = args.profile == "fast"
    try:
        vram_mib = int(float(sh("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits").strip().splitlines()[0]))
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

    ensure_real_buffett_voice_anchors(
        local_studio,
        python_bin=moss_venv / "bin/python",
        drive_ids=drive_ids,
        buffett_source=args.buffett_source,
        refresh_anchors=args.refresh_anchors,
        offline_dry_run=False,
    )
    print(f"⚡ G4 预热与四角色干音锚点全部就绪！耗时: {time.time() - t_boot:.1f}s", flush=True)

    local_outputs = local_studio / "outputs"
    local_outputs.mkdir(parents=True, exist_ok=True)
    nvme_cache = WORK_ROOT / "stem_cache"
    drive_cache = DRIVE_STUDIO_DIR / ".stem_cache"
    seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="pull")
    existing_markers = (
        populate_existing_markers_dir(WORK_ROOT / "drive_existing_markers", drive_ids) if args.skip_existing else None
    )

    cmd = [
        str(moss_venv / "bin/python"),
        "-u",
        str(local_studio / "run_buffett_96gb_studio.py"),
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
    sync_completed_outputs(local_outputs, synced_markers, drive_ids=drive_ids)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        if existing_markers is not None:
            populate_existing_markers_dir(existing_markers, drive_ids)
        print(
            f"=== [开始双语圆桌合成 · 第 {attempt}/{max_attempts} 轮] 任务: {args.episodes} | 引擎: {drama_repo} ===",
            flush=True,
        )
        proc = subprocess.Popen(cmd, cwd=str(local_studio), env=os.environ.copy())
        while proc.poll() is None:
            prev_n = len(synced_markers)
            sync_completed_outputs(local_outputs, synced_markers, drive_ids=drive_ids)
            if len(synced_markers) > prev_n:
                seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="push")
            time.sleep(4.0)

        sync_completed_outputs(local_outputs, synced_markers, drive_ids=drive_ids)
        seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="push")

        if proc.returncode == 0:
            break
        if attempt < max_attempts:
            print(
                f"⚠️ [自动守护] run_buffett_96gb_studio.py 退出 (rc={proc.returncode})，已完成期数已落盘，5s 后断点续跑...",
                flush=True,
            )
            time.sleep(5.0)
        else:
            raise RuntimeError(f"❌ run_buffett_96gb_studio.py 连续 {max_attempts} 次异常退出 (rc={proc.returncode})")

    os.sync()
    time.sleep(2.0)

    print("\n" + "=" * 80, flush=True)
    print(
        f"🎉 《穿越周期的信》双语成片渲染与 Google Drive 原子归档全部完成！共归档: {len(synced_markers)} 项 | 总耗时: {time.time() - t_boot:.1f}s",
        flush=True,
    )
    print(f"📂 Google Drive 成品目录: MyDrive/{DRIVE_SHOW_FOLDER_NAME}/{DRIVE_MASTERS_FOLDER_NAME}/", flush=True)
    print("=" * 80, flush=True)

    if args.auto_unassign:
        release_colab_runtime()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
