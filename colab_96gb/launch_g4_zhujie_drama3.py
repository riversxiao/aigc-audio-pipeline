#!/usr/bin/env python3
"""
《诸界锁仙》 96GB G4 (Blackwell sm_120) 三件套全自动冷启动与云盘原子归档启动器 (v1.1.0)

黄金三件套同卡常驻架构 (~75.0 GB / 96 GB VRAM)：
  1. Fish Audio Drama 3 (`fishaudio/drama-3` 35B MoE FP8 或 `drama-3-int4`) via SGLang-Omni (+ RAS 高表现力采样)
  2. MOSS-SoundEffect v2.0 (`OpenMOSS-Team/MOSS-SoundEffect-v2.0`, 48kHz 真实拟音 + 6 大跨集母题零成本直通)
  3. ACE-Step 1.5 XL Turbo (`ACE-Step/acestep-v15-xl-turbo-diffusers`, 48kHz 立体声分幕原声配乐)
  4. Faster-Whisper (`small`, CPU int8, 0 MB 显存开销自动回听防吞字/防标签漏读质检)

无缝兼容您的 `colab new -s audio96 --gpu G4` + `colab dfs mount -s audio96` 工作流：
  - 自动修复 `/content/drive/My Drive` -> `/content/drive/MyDrive` 符号链接。
  - 自动复用 `/content/drive/MyDrive/AI_Workstation/AudioStudio_G4_Cache` 源码包与已有虚拟环境。
  - 通过 `127.0.0.1:8012` OAuth 高速通道 1.5 秒拉取 164MB 自包含工程包（24 角色国风干音 + 6 母题 + 全 40 集台本）至本地 NVMe。
  - 每完成一集（检测到 `.done` 原子标记），立即通过 Google Drive REST API v3 将 WAV + 320k MP3 + 中文角色名 SRT + JSON
    原子落盘至云盘 `05_Colab_96GB_FishDrama3_满血本地推理管线/outputs/`，随时安全停机零丢片！
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
import threading
import time
from typing import Optional
import urllib.parse
import urllib.request
import zipfile

# 1. Heal `colab dfs mount` path with space (`/content/drive/My Drive` -> `/content/drive/MyDrive`)
if os.path.isdir("/content/drive/My Drive") and not os.path.exists("/content/drive/MyDrive"):
    os.symlink("/content/drive/My Drive", "/content/drive/MyDrive")

NVME_ROOT = Path("/content") if Path("/content").exists() else Path("/tmp")
HF_CACHE_DIR = NVME_ROOT / "hf_cache"
WORK_ROOT = NVME_ROOT / "zhujie_suoxian_work"
# Reuse existing `/content/nine_prison_envs` if warm on this G4 runtime; else `/content/audio_studio_envs`
ENV_ROOT = (
    NVME_ROOT / "nine_prison_envs"
    if (NVME_ROOT / "nine_prison_envs" / "drama3-venv" / "bin" / "sgl-omni").exists()
    else (NVME_ROOT / "audio_studio_envs")
)

os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["UV_CONCURRENT_DOWNLOADS"] = "32"

# Pre-deployed Google Drive Resource IDs for 《诸界锁仙》
DRIVE_BUNDLE_ZIP_ID = "1pTHmq6kw0y2-jUzGDY3ngApk91uSn4Ks"
DRIVE_PIPELINE_FOLDER_ID = "1GB1Cku8vW88H6p0FAXOjNZAOOr4-iZjH"
DRIVE_OUTPUTS_FOLDER_ID = "1-5OT1dX9iFyCjkfXMnciNAeSybdhX74k"
DRIVE_MAIN_MASTERS_FOLDER_ID = "1NYCi-TP2VwR2bAmPwekeG-V5-YvLnNBG"

DRIVE_ROOT = Path("/content/drive/MyDrive")
DRIVE_WORKSTATION = DRIVE_ROOT / "AI_Workstation"
DRIVE_REPO_CACHE = DRIVE_WORKSTATION / "AudioStudio_G4_Cache"
DRIVE_PROJECT_ROOT = DRIVE_ROOT / "《诸界锁仙》长篇修仙小说工程"
DRIVE_AUDIO_ROOT = DRIVE_PROJECT_ROOT / "04_有声剧与广播剧音频"
DRIVE_MAIN_MASTERS_DIR = DRIVE_AUDIO_ROOT / "03_分集成片音频"
DRIVE_STUDIO_DIR = DRIVE_AUDIO_ROOT / "05_Colab_96GB_FishDrama3_满血本地推理管线"
DRIVE_OUTPUTS_DIR = DRIVE_STUDIO_DIR / "outputs"


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
    """Retrieve OAuth token from `colab dfs mount` local metadata shim (127.0.0.1:8012) if active."""
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8012/computeMetadata/v1/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"},
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            return json.loads(resp.read().decode("utf-8"))["access_token"]
    except Exception:
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

    safe_name = local_path.name.replace("'", "\\'")
    q = f"trashed = false and '{parent_id}' in parents and name = '{safe_name}'"
    list_url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(
        {"q": q, "fields": "files(id,name)", "pageSize": 5}
    )
    req_list = urllib.request.Request(list_url, headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req_list, timeout=30) as resp:
        existing = json.loads(resp.read().decode("utf-8")).get("files", [])

    raw = local_path.read_bytes()
    if existing:
        fid = existing[0]["id"]
        up_req = urllib.request.Request(
            f"https://www.googleapis.com/upload/drive/v3/files/{fid}?uploadType=media&fields=id,name,size",
            data=raw,
            method="PATCH",
            headers={
                "Authorization": f"Bearer {tok}",
                "Content-Type": mime_type,
            },
        )
    else:
        boundary = f"zhujie_drama3_{int(time.time() * 1000)}"
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


def unpack_project_to_nvme() -> Path:
    """Unpack the 28-anchor + 6-motif + 120-episode bundle onto local G4 NVMe SSD in <2s."""
    t0 = time.time()
    local_studio = WORK_ROOT / "zhujie_studio"
    has_120 = len(list((local_studio / "cue_sheets").glob("E*.json"))) >= 120 if (local_studio / "cue_sheets").exists() else False
    has_28 = False
    if (local_studio / "voice_cast_drama3.json").is_file():
        try:
            has_28 = len(json.loads((local_studio / "voice_cast_drama3.json").read_text(encoding="utf-8")).get("characters", {})) >= 28
        except Exception:
            has_28 = False

    if has_120 and has_28:
        print(f"⚡ 本地 NVMe 《诸界锁仙》120集全本广播剧工程已就绪: {local_studio}", flush=True)
    else:
        local_studio.mkdir(parents=True, exist_ok=True)
        zip_dst = NVME_ROOT / "zhujie_suoxian_96gb_drama3_bundle.zip"
        if zip_dst.exists() and not (has_120 and has_28):
            zip_dst.unlink(missing_ok=True)
        if not zip_dst.exists():
            tok = get_drive_token()
            fuse_candidates = [
                DRIVE_STUDIO_DIR / "zhujie_suoxian_96gb_drama3_bundle.zip",
                *DRIVE_ROOT.glob("*诸界锁仙*/04_有声剧与广播剧音频/05_Colab_96GB_FishDrama3*/zhujie_suoxian_96gb_drama3_bundle.zip"),
            ]
            fuse_zip = next((p for p in fuse_candidates if p.exists()), None)
            if tok:
                print("⬇️ 正在通过 Drive v3 高速通道拉取《诸界锁仙》120集全本工程包至本地 NVMe...", flush=True)
                drive_api_download(DRIVE_BUNDLE_ZIP_ID, zip_dst, tok)
            elif fuse_zip is not None:
                print(f"⬇️ 正在从挂载云盘复制《诸界锁仙》120集全本工程包至本地 NVMe: {fuse_zip} ...", flush=True)
                shutil.copy2(fuse_zip, zip_dst)
            else:
                raise RuntimeError("未检测到 127.0.0.1:8012 Token 服务或挂载云盘工程包，请先挂载 Google Drive！")

        with zipfile.ZipFile(zip_dst, "r") as zf:
            zf.extractall(local_studio)
        print(f"✅ 120集全本工程包本地 NVMe 极速解压完成 ({time.time() - t0:.2f}s) -> {local_studio}", flush=True)

    # Overlay latest run_zhujie_96gb_studio.py / voice_cast_drama3.json from Drive or /content upload
    for rel in ("run_zhujie_96gb_studio.py", "voice_cast_drama3.json"):
        nvme_override = NVME_ROOT / rel
        drive_override = DRIVE_STUDIO_DIR / rel
        f_dst = local_studio / rel
        if nvme_override.is_file():
            shutil.copy2(nvme_override, f_dst)
        elif DRIVE_STUDIO_DIR.exists() and drive_override.is_file():
            try:
                shutil.copy2(drive_override, f_dst)
            except Exception:
                pass
    return local_studio


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
    """Build or reuse isolated `{drama3,moss,acestep}-venv` with Drive tarball cache acceleration."""
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

    # 2. MOSS-SoundEffect v2.0 + CPU int8 faster-whisper (`moss-venv`)
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
        print(f"✅ MOSS-SoundEffect v2.0 + faster-whisper 质检环境就绪 ({time.time() - t2:.1f}s)", flush=True)

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
        print(f"✅ ACE-Step 1.5 XL 配乐环境就绪 ({time.time() - t3:.1f}s)", flush=True)

    return drama_venv, moss_venv, acestep_venv


def sync_completed_outputs(
    local_outputs: Path,
    synced_markers: set[str],
    *,
    mirror_to_main_masters: bool = False,
) -> None:
    """Atomically sync every finished `.done` stem group to Google Drive via REST API v3 (+ FUSE fallback)."""
    if not local_outputs.exists():
        return

    tok = get_drive_token()
    if DRIVE_STUDIO_DIR.exists():
        DRIVE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if mirror_to_main_masters and DRIVE_AUDIO_ROOT.exists():
        DRIVE_MAIN_MASTERS_DIR.mkdir(parents=True, exist_ok=True)

    def _fuse_sync_one(fpath: Path, stem: str) -> None:
        src_sz = fpath.stat().st_size
        if DRIVE_OUTPUTS_DIR.exists():
            dst_out = DRIVE_OUTPUTS_DIR / fpath.name
            if not dst_out.exists() or dst_out.stat().st_size != src_sz:
                shutil.copy2(fpath, dst_out)
                print(f"☁️ [FUSE 同步] {fpath.name} -> {DRIVE_OUTPUTS_DIR}", flush=True)
        if mirror_to_main_masters and stem.startswith("E") and DRIVE_MAIN_MASTERS_DIR.exists():
            dst_main = DRIVE_MAIN_MASTERS_DIR / fpath.name
            if not dst_main.exists() or dst_main.stat().st_size != src_sz:
                shutil.copy2(fpath, dst_main)
                print(f"☁️ [FUSE 同步主库] {fpath.name} -> {DRIVE_MAIN_MASTERS_DIR}", flush=True)

    for done_file in sorted(local_outputs.glob("*.done")):
        if done_file.name in synced_markers:
            continue
        stem = done_file.stem  # e.g. E001_drama3_master_v001 or AUDITION_A_drama3_reel_v001
        related_files = [
            f
            for f in sorted(local_outputs.glob(f"{stem}.*"))
            if f.is_file() and f.suffix in (".mp3", ".wav", ".srt", ".json")
        ]
        for fpath in related_files:
            if tok:
                try:
                    drive_api_upsert_file(fpath, DRIVE_OUTPUTS_FOLDER_ID, tok)
                    if mirror_to_main_masters and stem.startswith("E"):
                        drive_api_upsert_file(fpath, DRIVE_MAIN_MASTERS_FOLDER_ID, tok)
                except Exception as exc:
                    print(f"⚠️ Drive API 上传回退至 FUSE ({fpath.name}): {exc}", flush=True)
                    _fuse_sync_one(fpath, stem)
            else:
                _fuse_sync_one(fpath, stem)

        synced_markers.add(done_file.name)
        # Reclaim ~180MB local NVMe master .wav once archived to Drive (keep .mp3 + .done for --skip-existing)
        local_wav = local_outputs / f"{stem}.wav"
        local_mp3 = local_outputs / f"{stem}.mp3"
        if stem.startswith("E") and local_wav.is_file() and local_mp3.is_file():
            try:
                local_wav.unlink()
            except Exception:
                pass

    # Reclaim temporary per-line TTS stems older than 45 min from NVMe cache
    tts_cache_dir = WORK_ROOT / "stem_cache" / "drama3_tts"
    if tts_cache_dir.exists():
        cutoff = time.time() - 2700
        for wf in tts_cache_dir.glob("*.wav"):
            try:
                if wf.stat().st_mtime < cutoff:
                    wf.unlink()
            except Exception:
                pass


def start_cloudflare_tunnel(port: int = 8000) -> Optional[subprocess.Popen]:
    """Expose local Drama 3 SGLang-Omni HTTP server via trycloudflare.com and sync URL to Google Drive."""
    cf_bin = NVME_ROOT / "cloudflared"
    if not cf_bin.exists():
        sh(
            f"curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 "
            f"-o '{cf_bin}' && chmod +x '{cf_bin}'"
        )
    log_path = NVME_ROOT / "cloudflared_drama3.log"
    log_file = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(cf_bin), "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"],
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )
    tunnel_url: Optional[str] = None
    for _ in range(40):
        if log_path.exists():
            txt = log_path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", txt)
            if m:
                tunnel_url = m.group(0)
                break
        time.sleep(0.5)

    if tunnel_url:
        url_file = NVME_ROOT / "drama3_colab_tunnel_url.txt"
        url_file.write_text(tunnel_url + "\n", encoding="utf-8")
        print(f"🌐 [Cloudflare HTTPS 隧道就绪] {tunnel_url}", flush=True)
        tok = get_drive_token()
        if tok:
            try:
                drive_api_upsert_file(url_file, DRIVE_PIPELINE_FOLDER_ID, tok)
            except Exception as exc:
                print(f"⚠️ 隧道地址写入 Drive API 失败: {exc}", flush=True)
        elif DRIVE_STUDIO_DIR.exists():
            shutil.copy2(url_file, DRIVE_STUDIO_DIR / url_file.name)
    else:
        print("⚠️ 未能在 20s 内捕获 trycloudflare 隧道地址，继续本地批处理。", flush=True)
    return proc


def seed_and_sync_reusable_stems(nvme_cache: Path, drive_cache: Path, direction: str) -> None:
    """Sync lightweight reusable BGM/SFX stems (~30-80 WAVs) between Drive FUSE and local NVMe."""
    if not DRIVE_STUDIO_DIR.exists():
        return
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
                try:
                    shutil.copy2(wf, target)
                except Exception:
                    pass


def populate_existing_markers_dir(markers_dir: Path) -> Path:
    """Build fast local `.mp3` existence markers from Drive REST API v3 + FUSE outputs/ & 03_分集成片音频/ for `--skip-existing`."""
    markers_dir.mkdir(parents=True, exist_ok=True)
    for d, require_drama3 in ((DRIVE_OUTPUTS_DIR, False), (DRIVE_MAIN_MASTERS_DIR, True)):
        if d.exists():
            try:
                for nm in os.listdir(d):
                    if nm.startswith("E") and nm.endswith(".mp3"):
                        if not require_drama3 or ("Drama3" in nm or "drama3" in nm):
                            (markers_dir / nm).touch()
            except Exception:
                pass
    tok = get_drive_token()
    if tok:
        for folder_id, require_drama3 in ((DRIVE_OUTPUTS_FOLDER_ID, False), (DRIVE_MAIN_MASTERS_FOLDER_ID, True)):
            try:
                page_token = ""
                while True:
                    params = {
                        "q": f"trashed = false and '{folder_id}' in parents",
                        "fields": "nextPageToken,files(name)",
                        "pageSize": 500,
                    }
                    if page_token:
                        params["pageToken"] = page_token
                    req = urllib.request.Request(
                        "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(params),
                        headers={"Authorization": f"Bearer {tok}"},
                    )
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        payload = json.loads(resp.read().decode("utf-8"))
                    for item in payload.get("files", []):
                        nm = item.get("name", "")
                        if nm.endswith(".mp3") and nm.startswith("E"):
                            if not require_drama3 or ("Drama3" in nm or "drama3" in nm):
                                (markers_dir / nm).touch()
                    page_token = payload.get("nextPageToken", "")
                    if not page_token:
                        break
            except Exception as exc:
                print(f"ℹ️ Drive API 已完成集数预检跳过 ({exc})", flush=True)
    return markers_dir


def release_colab_runtime() -> None:
    """Destroy the Colab runtime immediately after archiving outputs so 0 idle CCU is burned."""
    print("🛑 [--auto-unassign] 所有成品已原子归档至 Google Drive，正在主动销毁 G4 运行时立停 CCU 计费...", flush=True)
    for bp in (NVME_ROOT / "colab_agent_bridge.json", DRIVE_STUDIO_DIR / "colab_agent_bridge.json"):
        try:
            bp.unlink(missing_ok=True)
        except Exception:
            pass
    # Signal `colab_agent_bridge.py` -> Notebook Cell 0 IPython kernel to invoke `google.colab.runtime.unassign()`!
    try:
        (NVME_ROOT / ".colab_auto_unassign").write_text("auto_unassign_after_completion\n", encoding="utf-8")
        os.sync()
    except Exception:
        pass
    try:
        from google.colab import runtime  # type: ignore

        runtime.unassign()
    except Exception as exc:
        print(f"ℹ️ 已写入 .colab_auto_unassign 交由 Notebook 主内核自动销毁实例 ({exc})。", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="《诸界锁仙》 96GB G4 Fish Drama 3 黄金三件套全自动冷启动器")
    parser.add_argument(
        "--episodes",
        default="AUDITION,E001",
        help="要渲染的集数，例如 AUDITION,E001（试听+首集A/B对照）、E002-E120（全本收官续跑）或 SERVE",
    )
    parser.add_argument(
        "--profile",
        choices=["fp8", "fast"],
        default="fp8",
        help="fp8 = 满血 fishaudio/drama-3 (35B MoE FP8, 96G推荐); fast = fishaudio/drama-3-int4 (20.8GB)",
    )
    parser.add_argument("--skip-existing", action="store_true", help="跳过本地或云盘 outputs/ 已存在成品的集数")
    parser.add_argument("--phoneme-pins", action="store_true", help="启用 Drama 3 原生 <|phoneme_start|> 拼音锚点")
    parser.add_argument(
        "--mirror-to-main-masters",
        action="store_true",
        help="除保存至 05_Colab_96GB.../outputs/ 外，同步抄送一份母带至 03_分集成片音频/",
    )
    parser.add_argument(
        "--public-tunnel",
        action="store_true",
        help="对齐 ai-cinema-studio-kit：启动 trycloudflare HTTPS 隧道并将地址同步至 Drive drama3_colab_tunnel_url.txt",
    )
    parser.add_argument(
        "--auto-unassign",
        "--auto-shutdown",
        dest="auto_unassign",
        action="store_true",
        help="防烧钱守门员：全部成品落盘 Google Drive 后自动销毁 G4 实例立停 CCU 计费（支持无人值守过夜）",
    )
    parser.add_argument("--refresh-envs", action="store_true", help="强制重建虚拟环境")
    args = parser.parse_args()

    t_boot = time.time()
    print("=" * 78, flush=True)
    print("🎬 《诸界锁仙》 96GB G4 (Blackwell) Fish Audio Drama 3 满血有声剧工业管线启动", flush=True)
    print(sh("nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader || echo 'GPU Check Skipped'").strip(), flush=True)
    print("=" * 78, flush=True)

    use_int4 = args.profile == "fast"
    try:
        vram_mib = int(float(sh("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits").strip().splitlines()[0]))
        if vram_mib < 85000:
            print(f"ℹ️ 检测到显存 {vram_mib} MiB (<85GB)，自动切换为 fishaudio/drama-3-int4 显存接力模式", flush=True)
            use_int4 = True
    except Exception:
        pass
    drama_repo = "fishaudio/drama-3-int4" if use_int4 else "fishaudio/drama-3"

    local_studio = unpack_project_to_nvme()
    uv_bin = ensure_uv_and_hf_tools()

    print(f"=== [并发冷启动] 通道 A: HF CDN 高速预取 ({drama_repo} + MOSS v2.0 + ACE-Step 1.5 XL) || 通道 B: 隔离环境就绪 ===", flush=True)
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

    print(f"⚡ G4 预热全部就绪！耗时: {time.time() - t_boot:.1f}s", flush=True)

    tunnel_proc: Optional[subprocess.Popen] = None
    if args.public_tunnel or args.episodes.strip().upper() == "SERVE":
        tunnel_proc = start_cloudflare_tunnel(port=8000)

    if args.episodes.strip().upper() == "SERVE":
        sgl_cmd = [
            str(drama_venv / "bin/sgl-omni"),
            "serve",
            "--model-path",
            drama_repo,
            "--port",
            "8000",
            "--tts_engine.gpu_memory_fraction",
            "0.75",
            "--vocoder.gpu_memory_fraction",
            "0.10",
            "--preprocessing.total_reserve_bytes",
            "4GiB",
        ]
        print(f"=== [常驻 HTTP 服务模式] Drama 3 引擎: {drama_repo} (供云端/远程 Agent 直接调用) ===", flush=True)
        sgl_proc = subprocess.Popen(sgl_cmd, cwd=str(local_studio), env=os.environ.copy())
        try:
            sgl_proc.wait()
        finally:
            if tunnel_proc and tunnel_proc.poll() is None:
                tunnel_proc.terminate()
        return

    local_outputs = local_studio / "outputs"
    local_outputs.mkdir(parents=True, exist_ok=True)
    nvme_cache = WORK_ROOT / "stem_cache"
    drive_cache = DRIVE_STUDIO_DIR / ".stem_cache"
    seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="pull")
    existing_markers = populate_existing_markers_dir(WORK_ROOT / "drive_existing_markers") if args.skip_existing else None

    cmd = [
        str(moss_venv / "bin/python"),
        "-u",
        str(local_studio / "run_zhujie_96gb_studio.py"),
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
    if args.phoneme_pins:
        cmd.append("--phoneme-pins")

    synced_markers: set[str] = set()
    # Sync any already-finished `.done` episodes on NVMe before starting!
    sync_completed_outputs(local_outputs, synced_markers, mirror_to_main_masters=args.mirror_to_main_masters)

    max_attempts = 3
    try:
        for attempt in range(1, max_attempts + 1):
            if existing_markers is not None:
                populate_existing_markers_dir(existing_markers)
            print(
                f"=== [开始合成 · 第 {attempt}/{max_attempts} 轮] 任务: {args.episodes} | Drama 3 引擎: {drama_repo} ===",
                flush=True,
            )
            proc = subprocess.Popen(cmd, cwd=str(local_studio), env=os.environ.copy())
            while proc.poll() is None:
                prev_n = len(synced_markers)
                sync_completed_outputs(local_outputs, synced_markers, mirror_to_main_masters=args.mirror_to_main_masters)
                if len(synced_markers) > prev_n:
                    seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="push")
                time.sleep(4.0)

            sync_completed_outputs(local_outputs, synced_markers, mirror_to_main_masters=args.mirror_to_main_masters)
            seed_and_sync_reusable_stems(nvme_cache, drive_cache, direction="push")

            if proc.returncode == 0:
                break
            if attempt < max_attempts:
                print(
                    f"⚠️ [自动守护] run_zhujie_96gb_studio.py 退出 (rc={proc.returncode})，已完成分集已原子落盘，5s 后自动断点续跑...",
                    flush=True,
                )
                time.sleep(5.0)
            else:
                raise RuntimeError(f"❌ run_zhujie_96gb_studio.py 连续 {max_attempts} 次异常退出 (rc={proc.returncode})")

        os.sync()
        time.sleep(2.0)
    finally:
        if tunnel_proc and tunnel_proc.poll() is None:
            tunnel_proc.terminate()

    print("\n" + "=" * 78, flush=True)
    print(
        f"🎉 《诸界锁仙》 Drama 3 成片渲染与云盘原子归档全部完成！共归档: {len(synced_markers)} 项 | 总耗时: {time.time() - t_boot:.1f}s",
        flush=True,
    )
    print("📂 Google Drive 成品目录: 《诸界锁仙》长篇修仙小说工程/04_有声剧与广播剧音频/05_Colab_96GB_FishDrama3_满血本地推理管线/outputs/", flush=True)
    print("=" * 78, flush=True)

    if args.auto_unassign:
        release_colab_runtime()


if __name__ == "__main__":
    main()

