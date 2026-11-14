#!/usr/bin/env python3
"""
《逆模因部》(There Is No Antimemetics Division — SCP CC-BY-SA-3.0)
96GB G4 (Blackwell sm_120) 黄金三件套全自动冷启动、全六集合成与云盘原子归档启动器 (v1.1.0)

黄金三件套同卡常驻架构 (~75.0 GB / 96 GB VRAM)：
  1. Fish Audio Drama 3 (`fishaudio/drama-3` 35B MoE FP8 或 `drama-3-int4`) via SGLang-Omni (+ RAS 高表现力采样)
  2. MOSS-SoundEffect v2.0 (`OpenMOSS-Team/MOSS-SoundEffect-v2.0`, 48kHz 科幻拟音 + 5 大跨集母题自动缓存复用)
  3. ACE-Step 1.5 XL Turbo (`ACE-Step/acestep-v15-xl-turbo-diffusers`, `--bgm-style scifi_dark` 48kHz 暗黑科幻悬疑原声配乐)
  4. Faster-Whisper (`small`, CPU int8, 0 MB 显存开销自动回听防吞字/防标签漏读质检)
"""

from __future__ import annotations

import argparse
import hashlib
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

if os.path.isdir("/content/drive/My Drive") and not os.path.exists("/content/drive/MyDrive"):
    os.symlink("/content/drive/My Drive", "/content/drive/MyDrive")

NVME_ROOT = Path("/content") if Path("/content").exists() else Path("/tmp")
HF_CACHE_DIR = NVME_ROOT / "hf_cache"
WORK_ROOT = NVME_ROOT / "antimemetics_division_work"
ENV_ROOT = (
    NVME_ROOT / "nine_prison_envs"
    if (NVME_ROOT / "nine_prison_envs" / "drama3-venv" / "bin" / "sgl-omni").exists()
    else (NVME_ROOT / "audio_studio_envs")
)

os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["HF_HUB_CACHE"] = str(HF_CACHE_DIR / "hub")
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["UV_CONCURRENT_DOWNLOADS"] = "32"

DRIVE_ROOT = Path("/content/drive/MyDrive")
DRIVE_WORKSTATION = DRIVE_ROOT / "AI_Workstation"
DRIVE_REPO_CACHE = DRIVE_WORKSTATION / "AudioStudio_G4_Cache"
DRIVE_PROJECT_ROOT = DRIVE_ROOT / "《逆模因部》有声剧工程（SCP CC-BY-SA-3.0）"
DRIVE_STUDIO_DIR = DRIVE_PROJECT_ROOT / "05_Colab_96GB_FishDrama3_满血本地推理管线"
DRIVE_OUTPUTS_DIR = DRIVE_STUDIO_DIR / "outputs"
DRIVE_MASTERS_DIR = DRIVE_PROJECT_ROOT / "03_分集成片音频"


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
    if not parent_id:
        return
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
            headers={"Authorization": f"Bearer {tok}", "Content-Type": mime_type},
        )
    else:
        boundary = f"antimemetics_drama3_{int(time.time() * 1000)}"
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


def unpack_project_to_nvme(bundle_file_id: str = "") -> Path:
    """Unpack the 13-anchor + 5-motif + 6-episode bundle onto local G4 NVMe SSD."""
    t0 = time.time()
    local_studio = WORK_ROOT / "antimemetics_studio"
    if (local_studio / "voice_cast_drama3.json").exists() and len(list((local_studio / "cue_sheets").glob("E*.json"))) >= 6:
        print(f"⚡ 本地 NVMe 《逆模因部》有声剧工程已就绪: {local_studio}", flush=True)
    else:
        local_studio.mkdir(parents=True, exist_ok=True)
        zip_dst = NVME_ROOT / "antimemetics_division_96gb_drama3_bundle.zip"
        if not zip_dst.exists():
            tok = get_drive_token()
            fuse_candidates = [
                DRIVE_STUDIO_DIR / "antimemetics_division_96gb_drama3_bundle.zip",
                *DRIVE_ROOT.glob("*逆模因部*/05_Colab_96GB_FishDrama3*/antimemetics_division_96gb_drama3_bundle.zip"),
            ]
            fuse_zip = next((p for p in fuse_candidates if p.exists()), None)
            if tok and bundle_file_id:
                print("⬇️ 正在通过 Drive v3 高速通道拉取《逆模因部》工程包至本地 NVMe...", flush=True)
                drive_api_download(bundle_file_id, zip_dst, tok)
            elif fuse_zip is not None:
                print(f"⬇️ 正在从挂载云盘复制《逆模因部》工程包至本地 NVMe: {fuse_zip} ...", flush=True)
                shutil.copy2(fuse_zip, zip_dst)
            else:
                raise RuntimeError(
                    f"未找到 {zip_dst}！请先通过 colab upload 上传工程包，或挂载 Google Drive。"
                )

        with zipfile.ZipFile(zip_dst, "r") as zf:
            zf.extractall(local_studio)
        print(f"✅ 《逆模因部》工程包本地 NVMe 解压完成 ({time.time() - t0:.2f}s) -> {local_studio}", flush=True)

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
    if not all(shutil.which(x) for x in ("ffmpeg", "git", "zstd")):
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
    from huggingface_hub import snapshot_download

    hub_dir = HF_CACHE_DIR / "hub"
    hub_dir.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HUB_CACHE"] = str(hub_dir)
    repos = [
        drama_repo,
        "OpenMOSS-Team/MOSS-SoundEffect-v2.0",
        "ACE-Step/acestep-v15-xl-turbo-diffusers",
        "Systran/faster-whisper-small",
    ]
    for repo_id in repos:
        t_m = time.time()
        print(f"🚀 [HF CDN -> NVMe] 高速预取权重: {repo_id} ...", flush=True)
        snapshot_download(repo_id=repo_id, cache_dir=str(hub_dir))
        print(f"✅ [HF CDN -> NVMe] 权重就绪: {repo_id} ({time.time() - t_m:.1f}s)", flush=True)


def build_isolated_venvs(uv_bin: str, refresh_envs: bool = False) -> tuple[Path, Path, Path]:
    """Build or reuse isolated `{drama3,moss,acestep}-venv` on NVMe."""
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

    if not (drama_venv / "bin/sgl-omni").exists() or not (drama_venv / "bin/ninja").exists():
        t1 = time.time()
        sgl_tar_nvme = NVME_ROOT / "sglang_omni_sm120.tar.gz"
        sgl_tar_drive = DRIVE_REPO_CACHE / "sglang_omni_sm120.tar.gz"
        if not sgl_repo.exists():
            if sgl_tar_nvme.is_file():
                print("⚡ 从本地 NVMe 缓存秒级解压 sglang-omni (sm_120)...", flush=True)
                sh(f"tar -xzf '{sgl_tar_nvme}' -C '{ENV_ROOT}'")
            elif can_cache_drive and sgl_tar_drive.is_file():
                print("⚡ 从云盘缓存秒级解压 sglang-omni (sm_120)...", flush=True)
                sh(f"tar -xzf '{sgl_tar_drive}' -C '{ENV_ROOT}'")
            else:
                sh(f"git clone --depth 1 https://github.com/sgl-project/sglang-omni.git '{sgl_repo}'")
        sh(f"'{uv_bin}' venv '{drama_venv}' --python 3.12 --allow-existing")
        sh(
            f"cd '{sgl_repo}' && '{uv_bin}' pip install --python '{drama_venv}/bin/python' "
            f"--prerelease=allow -e '.[fishaudio]' hf_transfer ninja"
        )
        print(f"✅ Drama 3 (SGLang-Omni) 隔离推理环境就绪 ({time.time() - t1:.1f}s)", flush=True)

    if not _venv_ok(moss_venv, "import moss_soundeffect_v2, scipy, soundfile, faster_whisper"):
        t2 = time.time()
        moss_tar_nvme = NVME_ROOT / "moss_tts_v2.tar.gz"
        moss_tar_drive = DRIVE_REPO_CACHE / "moss_tts_v2.tar.gz"
        if not moss_repo.exists():
            if moss_tar_nvme.is_file():
                print("⚡ 从本地 NVMe 缓存秒级解压 MOSS-TTS...", flush=True)
                sh(f"tar -xzf '{moss_tar_nvme}' -C '{ENV_ROOT}'")
            elif can_cache_drive and moss_tar_drive.is_file():
                print("⚡ 从云盘缓存秒级解压 MOSS-TTS...", flush=True)
                sh(f"tar -xzf '{moss_tar_drive}' -C '{ENV_ROOT}'")
            else:
                sh(f"git clone --depth 1 https://github.com/OpenMOSS/MOSS-TTS.git '{moss_repo}'")
        sh(f"'{uv_bin}' venv '{moss_venv}' --python 3.12 --allow-existing")
        sh(
            f"'{uv_bin}' pip install --python '{moss_venv}/bin/python' "
            f"--extra-index-url https://download.pytorch.org/whl/cu128 "
            f"--index-strategy unsafe-best-match "
            f"-e '{moss_repo}/moss_soundeffect_v2[torch-cu128]' "
            f"scipy soundfile requests hf_transfer faster-whisper"
        )
        print(f"✅ MOSS-SoundEffect v2.0 + faster-whisper 质检环境就绪 ({time.time() - t2:.1f}s)", flush=True)

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


def export_cached_motifs(local_studio: Path, cache_dir: Path, local_outputs: Path) -> None:
    """Copy synthesized 48kHz sci-fi motif WAVs out of `moss_sfx` cache with human-readable motif IDs."""
    reg_file = local_studio / "voice_casting_registry.json"
    if not reg_file.is_file():
        return
    # Import sanitize_moss_foley_prompt from run_zhujie_96gb_studio for exact SHA-256 key match
    import sys as _sys

    if str(local_studio) not in _sys.path:
        _sys.path.insert(0, str(local_studio))
    if str(local_studio / "src") not in _sys.path:
        _sys.path.insert(0, str(local_studio / "src"))
    try:
        from run_zhujie_96gb_studio import sanitize_moss_foley_prompt  # type: ignore
    except Exception:
        return

    reg = json.loads(reg_file.read_text(encoding="utf-8"))
    motifs_out = local_outputs / "motifs"
    motifs_out.mkdir(parents=True, exist_ok=True)
    for mid, mdata in reg.get("sonic_motifs", {}).items():
        prompt = sanitize_moss_foley_prompt(mdata.get("sfx_prompt", ""))
        dur = round(float(mdata.get("duration_seconds", 3.0)), 2)
        raw_key = json.dumps({"prompt": prompt, "dur": dur}, ensure_ascii=False, sort_keys=True)
        sha24 = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:24]
        src_wav = cache_dir / "moss_sfx" / f"{sha24}.wav"
        if src_wav.is_file():
            shutil.copy2(src_wav, motifs_out / f"{mid}.wav")


def sync_completed_outputs(
    local_outputs: Path,
    synced_markers: set[str],
    *,
    local_studio: Optional[Path] = None,
    persistent_cache: Optional[Path] = None,
    drive_outputs_id: str = "",
    drive_masters_id: str = "",
) -> None:
    if not local_outputs.exists():
        return
    tok = get_drive_token()
    if DRIVE_STUDIO_DIR.exists():
        DRIVE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if DRIVE_PROJECT_ROOT.exists():
        DRIVE_MASTERS_DIR.mkdir(parents=True, exist_ok=True)

    newly_synced = False
    for done_file in sorted(local_outputs.glob("*.done")):
        if done_file.name in synced_markers:
            continue
        newly_synced = True
        stem = done_file.stem
        related_files = [
            f
            for f in sorted(local_outputs.glob(f"{stem}.*"))
            if f.is_file() and f.suffix in (".mp3", ".wav", ".srt", ".json")
        ]
        for fpath in related_files:
            if tok and drive_outputs_id:
                try:
                    drive_api_upsert_file(fpath, drive_outputs_id, tok)
                    if drive_masters_id and stem.startswith("E"):
                        drive_api_upsert_file(fpath, drive_masters_id, tok)
                except Exception as exc:
                    print(f"⚠️ Drive API 上传回退至 FUSE ({fpath.name}): {exc}", flush=True)
                    if DRIVE_OUTPUTS_DIR.exists():
                        shutil.copy2(fpath, DRIVE_OUTPUTS_DIR / fpath.name)
            elif DRIVE_OUTPUTS_DIR.exists():
                shutil.copy2(fpath, DRIVE_OUTPUTS_DIR / fpath.name)
                if DRIVE_MASTERS_DIR.exists() and stem.startswith("E"):
                    shutil.copy2(fpath, DRIVE_MASTERS_DIR / fpath.name)
                print(f"☁️ [FUSE 同步] {fpath.name} -> {DRIVE_OUTPUTS_DIR}", flush=True)
        synced_markers.add(done_file.name)

    if newly_synced and local_studio is not None and persistent_cache is not None:
        export_cached_motifs(local_studio, persistent_cache, local_outputs)


def main() -> None:
    parser = argparse.ArgumentParser(description="《逆模因部》 96GB G4 Fish Drama 3 黄金三件套全自动冷启动器")
    parser.add_argument(
        "--episodes",
        default="AUDITION,E001-E006",
        help="要渲染的集数，默认 AUDITION,E001-E006（试听合集 + 第一季全六集完整版）",
    )
    parser.add_argument("--profile", choices=["fp8", "fast"], default="fp8")
    parser.add_argument("--bgm-style", choices=["scifi_dark", "guofeng", "raw"], default="scifi_dark")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--bundle-file-id", default="")
    parser.add_argument("--drive-outputs-id", default="")
    parser.add_argument("--drive-masters-id", default="")
    parser.add_argument("--refresh-envs", action="store_true")
    args = parser.parse_args()

    t_boot = time.time()
    print("=" * 78, flush=True)
    print("🎬 《逆模因部》(SCP CC-BY-SA-3.0) 96GB G4 Fish Audio Drama 3 满血有声剧管线启动", flush=True)
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

    local_studio = unpack_project_to_nvme(bundle_file_id=args.bundle_file_id)
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

    local_outputs = local_studio / "outputs"
    local_outputs.mkdir(parents=True, exist_ok=True)
    persistent_cache = (DRIVE_STUDIO_DIR / ".stem_cache") if DRIVE_STUDIO_DIR.exists() else (local_studio / "cache")

    cmd = [
        str(moss_venv / "bin/python"),
        "-u",
        str(local_studio / "run_zhujie_96gb_studio.py"),
        "--studio-dir",
        str(local_studio),
        "--episodes",
        args.episodes,
        "--bgm-style",
        args.bgm_style,
        "--output-dir",
        str(local_outputs),
        "--cache-dir",
        str(persistent_cache),
        "--sgl-bin",
        str(drama_venv / "bin/sgl-omni"),
        "--moss-python",
        str(moss_venv / "bin/python"),
        "--acestep-python",
        str(acestep_venv / "bin/python"),
    ]
    if use_int4:
        cmd.append("--force-int4")
    if args.skip_existing:
        cmd.append("--skip-existing")

    print(f"=== [开始合成] 任务: {args.episodes} | 引擎: {drama_repo} | 配乐: {args.bgm_style} ===", flush=True)
    proc = subprocess.Popen(cmd, cwd=str(local_studio), env=os.environ.copy())
    synced_markers: set[str] = set()

    while proc.poll() is None:
        sync_completed_outputs(
            local_outputs,
            synced_markers,
            local_studio=local_studio,
            persistent_cache=persistent_cache,
            drive_outputs_id=args.drive_outputs_id,
            drive_masters_id=args.drive_masters_id,
        )
        time.sleep(4.0)

    if proc.returncode != 0:
        raise RuntimeError(f"❌ run_zhujie_96gb_studio.py 异常退出 (rc={proc.returncode})")

    sync_completed_outputs(
        local_outputs,
        synced_markers,
        local_studio=local_studio,
        persistent_cache=persistent_cache,
        drive_outputs_id=args.drive_outputs_id,
        drive_masters_id=args.drive_masters_id,
    )
    export_cached_motifs(local_studio, persistent_cache, local_outputs)
    os.sync()

    print("\n" + "=" * 78, flush=True)
    print(
        f"🎉 《逆模因部》 Drama 3 成片渲染完成！共生成: {len(synced_markers)} 项 | 总耗时: {time.time() - t_boot:.1f}s",
        flush=True,
    )
    print(f"📂 本地成品目录: {local_outputs}", flush=True)
    print("=" * 78, flush=True)


if __name__ == "__main__":
    main()
