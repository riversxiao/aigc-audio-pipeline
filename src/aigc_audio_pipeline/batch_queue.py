"""Resilient Multi-Episode Batch Queue Runner, EBU R128 Verifier & Cloud Checkpoint Archiver."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any

from .models import utc_now_iso


def measure_ebur128(audio_path: Path) -> tuple[float, float]:
    """Return `(integrated_lufs, true_peak_dbfs)` measured via `ffmpeg ebur128=peak=true`."""
    proc = subprocess.run(
        [
            "ffmpeg",
            "-nostats",
            "-hide_banner",
            "-i",
            str(audio_path),
            "-filter_complex",
            "ebur128=peak=true",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    stderr = proc.stderr
    m_i = re.findall(r"I:\s*([-\d.]+)\s*LUFS", stderr)
    m_pk = re.findall(r"Peak:\s*([-\d.]+)\s*dBFS", stderr)
    lufs = float(m_i[-1]) if m_i else -16.0
    tp = float(m_pk[-1]) if m_pk else -1.0
    return round(lufs, 2), round(tp, 2)


def canonical_episode_stem(episode_id: str, title: str, suffix: str = "电影感多人有声剧") -> str:
    """Build normalized Chinese deliverable filename stem without punctuation."""
    clean = (
        title.replace(" ", "_")
        .replace("，", "")
        .replace("？", "")
        .replace("！", "")
        .replace("：", "")
        .replace("·", "")
    )
    m = re.match(r"^第(\d+)章_(.*)$", clean)
    if m:
        clean = f"第{int(m.group(1)):02d}章_{m.group(2)}"
    return f"{episode_id}_{clean}_{suffix}"


def _gdrive_upload(local_path: Path, parent_folder_id: str) -> str:
    out = subprocess.check_output(
        ["gdrive", "mutate", "upload", str(local_path), "--parent", parent_folder_id],
        text=True,
    )
    m = re.search(r"ID:\s*([A-Za-z0-9_-]+)", out)
    if m:
        return m.group(1)
    ls_out = subprocess.check_output(
        [
            "gdrive",
            "readonly",
            "search",
            "--parent-id",
            parent_folder_id,
            "--name-exact",
            local_path.name,
            "--json",
        ],
        text=True,
    )
    data = json.loads(ls_out)
    files = data if isinstance(data, list) else data.get("files", [])
    return files[0]["id"] if files else ""


def _gdrive_update(file_id: str, local_path: Path) -> None:
    if file_id:
        subprocess.run(["gdrive", "mutate", "update", file_id, str(local_path)], check=True)


@dataclass
class BatchWorkspace:
    """Standard persistent directory layout for serialized multi-cast audio production."""

    workspace_dir: Path
    enable_gdrive: bool = True
    drive_ledger_file_id: str = ""
    drive_runs_file_id: str = ""
    drive_registry_file_id: str = ""

    @property
    def casting_dir(self) -> Path:
        return self.workspace_dir / "00_声音选角档案与进度台账"

    @property
    def ledger_path(self) -> Path:
        return self.casting_dir / "production_progress_ledger.json"

    @property
    def runs_jsonl_path(self) -> Path:
        return self.casting_dir / "production_runs.jsonl"

    @property
    def registry_path(self) -> Path:
        return self.casting_dir / "voice_casting_registry.json"

    @property
    def scripts_dir(self) -> Path:
        return self.workspace_dir / "02_分集广播剧台本"

    @property
    def master_dir(self) -> Path:
        return self.workspace_dir / "03_分集成片音频"

    @property
    def motifs_dir(self) -> Path:
        return self.workspace_dir / "04_跨集复用声效与配乐母题"

    @property
    def cache_dir(self) -> Path:
        return self.workspace_dir / ".cache"

    def find_episode_scripts(self, ep_num: int) -> tuple[Path, Path]:
        ep_id = f"E{ep_num:03d}"
        jsons = sorted(self.scripts_dir.glob(f"{ep_id}_*_完整有声剧台本.json"))
        mds = sorted(self.scripts_dir.glob(f"{ep_id}_*_完整有声剧台本.md"))
        if not jsons or not mds:
            raise FileNotFoundError(f"Missing compiled script for {ep_id} in {self.scripts_dir}")
        return jsons[-1], mds[-1]

    def sync_new_motifs(self, drive_motifs_folder: str) -> None:
        if not self.enable_gdrive or not drive_motifs_folder or not self.registry_path.is_file():
            return
        reg = json.loads(self.registry_path.read_text(encoding="utf-8"))
        changed = False
        for mid, mdata in reg.get("sonic_motifs", {}).items():
            cf = mdata.get("cached_file", "")
            if cf and Path(cf).is_file() and not mdata.get("drive_file_id"):
                drv_id = _gdrive_upload(Path(cf), drive_motifs_folder)
                mdata["drive_file_id"] = drv_id
                changed = True
                print(f"  [MOTIF UPLOADED] {mid} -> {drv_id}", flush=True)
        if changed:
            self.registry_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            _gdrive_update(self.drive_registry_file_id, self.registry_path)


def render_and_archive_episode(
    ws: BatchWorkspace,
    episode_id: str,
    script_json_path: Path,
    script_md_path: Path,
    *,
    workers: int = 4,
) -> dict[str, Any]:
    """Render one compiled episode, verify EBU R128 loudness & QA, and checkpoint to ledger/Drive."""
    t0 = time.time()
    ledger = json.loads(ws.ledger_path.read_text(encoding="utf-8"))
    drive_folders = ledger.get("drive_folders", {})
    drive_scripts_folder = drive_folders.get("02_episode_scripts", "")
    drive_master_folder = drive_folders.get("03_mastered_episodes", "")
    drive_motifs_folder = drive_folders.get("04_reusable_motifs_and_stems", "")

    ep_entry = next(e for e in ledger["episodes"] if e["episode_id"] == episode_id)
    if ep_entry.get("status") == "mastered_and_archived" and (
        ep_entry.get("latest_master_mp3_drive_id") or not ws.enable_gdrive
    ):
        print(f"[SKIP] {episode_id} already mastered_and_archived", flush=True)
        return ep_entry

    sheet_raw = json.loads(script_json_path.read_text(encoding="utf-8"))
    title = sheet_raw["title"]
    print("\n============================================================", flush=True)
    print(f"[START] {episode_id} · {title} (cues={len(sheet_raw['cues'])})", flush=True)

    if ws.enable_gdrive and drive_scripts_folder:
        if not ep_entry.get("script_json_drive_id"):
            ep_entry["script_json_drive_id"] = _gdrive_upload(script_json_path, drive_scripts_folder)
        else:
            _gdrive_update(ep_entry["script_json_drive_id"], script_json_path)
        if not ep_entry.get("script_md_drive_id"):
            ep_entry["script_md_drive_id"] = _gdrive_upload(script_md_path, drive_scripts_folder)
        else:
            _gdrive_update(ep_entry["script_md_drive_id"], script_md_path)

    ep_entry["cue_sheet_file"] = f"02_分集广播剧台本/{script_json_path.name}"
    ep_entry["status"] = "rendering"
    ledger["summary"]["scripts_ready"] = sum(1 for e in ledger["episodes"] if e.get("cue_sheet_file"))
    ws.ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ws.master_dir.mkdir(parents=True, exist_ok=True)
    ws.motifs_dir.mkdir(parents=True, exist_ok=True)
    ws.cache_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "aigc_audio_pipeline.cli",
        "render-episode",
        "--registry",
        str(ws.registry_path),
        "--cue-sheet",
        str(script_json_path),
        "--output-dir",
        str(ws.master_dir),
        "--cache-dir",
        str(ws.cache_dir),
        "--motifs-dir",
        str(ws.motifs_dir),
        "--workers",
        str(workers),
        "--clean-work-dir",
    ]
    env = dict(os.environ)
    pkg_src = str(Path(__file__).resolve().parents[1])
    existing_pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{pkg_src}:{existing_pp}" if existing_pp else pkg_src

    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        print(
            f"[ERROR] {episode_id} render-episode failed (rc={proc.returncode}):\n"
            f"STDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}",
            flush=True,
        )
        raise RuntimeError(f"{episode_id} render failed")

    render_summary = json.loads(proc.stdout)
    master_wav = Path(render_summary["master_wav"])
    master_mp3 = Path(render_summary["master_mp3"])
    subtitles_srt = Path(render_summary["subtitles_srt"])
    manifest_json = Path(render_summary["manifest_json"])
    ver_suffix = re.search(r"(_v\d+)$", master_wav.stem)
    ver_tag = ver_suffix.group(1) if ver_suffix else "_v001"

    manifest_data = json.loads(manifest_json.read_text(encoding="utf-8"))
    qa_failures = manifest_data.get("qa_failures") or render_summary.get("qa_failures") or []
    lufs, true_peak = measure_ebur128(master_wav)
    dur_s = float(render_summary.get("total_duration_s") or render_summary.get("duration_s") or 0.0)
    print(
        f"  [MASTERED] {episode_id}: dur={dur_s:.1f}s ({dur_s/60:.1f}m), "
        f"LUFS={lufs}, TP={true_peak}dBFS, qa_failures={len(qa_failures)}",
        flush=True,
    )
    for qf in qa_failures:
        reasons = qf.get("qa", {}).get("reasons") if isinstance(qf.get("qa"), dict) else qf.get("reasons")
        print(f"    [QA WARN] {qf.get('cue_id')} ({qf.get('role_id')}): {reasons}", flush=True)

    c_stem = f"{canonical_episode_stem(episode_id, title)}{ver_tag}"
    dst_wav = ws.master_dir / f"{c_stem}.wav"
    dst_mp3 = ws.master_dir / f"{c_stem}.mp3"
    dst_srt = ws.master_dir / f"{c_stem}.srt"
    dst_json = ws.master_dir / f"{c_stem}.json"
    # Use shutil.copyfile (not copy2) for FUSE / shared-volume mount compatibility
    shutil.copyfile(master_wav, dst_wav)
    shutil.copyfile(master_mp3, dst_mp3)
    shutil.copyfile(subtitles_srt, dst_srt)
    shutil.copyfile(manifest_json, dst_json)

    wav_id = mp3_id = srt_id = json_id = ""
    if ws.enable_gdrive and drive_master_folder:
        with ThreadPoolExecutor(max_workers=4) as up_pool:
            f_wav = up_pool.submit(_gdrive_upload, dst_wav, drive_master_folder)
            f_mp3 = up_pool.submit(_gdrive_upload, dst_mp3, drive_master_folder)
            f_srt = up_pool.submit(_gdrive_upload, dst_srt, drive_master_folder)
            f_jsn = up_pool.submit(_gdrive_upload, dst_json, drive_master_folder)
            wav_id, mp3_id, srt_id, json_id = f_wav.result(), f_mp3.result(), f_srt.result(), f_jsn.result()
        ws.sync_new_motifs(drive_motifs_folder)

    ledger = json.loads(ws.ledger_path.read_text(encoding="utf-8"))
    ep_entry = next(e for e in ledger["episodes"] if e["episode_id"] == episode_id)
    ep_entry["status"] = "mastered_and_archived"
    ep_entry["cue_sheet_file"] = f"02_分集广播剧台本/{script_json_path.name}"
    ep_entry["duration_seconds"] = round(dur_s, 3)
    ep_entry["integrated_lufs"] = lufs
    ep_entry["true_peak_dbfs"] = true_peak
    ep_entry["qa_failure_count"] = len(qa_failures)
    if wav_id:
        ep_entry["latest_master_wav_drive_id"] = wav_id
        ep_entry["latest_master_mp3_drive_id"] = mp3_id
        ep_entry["latest_subtitles_srt_drive_id"] = srt_id
        ep_entry["latest_manifest_json_drive_id"] = json_id
    ep_entry["local_master_mp3"] = str(dst_mp3)
    ep_entry["notes"] = (
        f"已完成4幕{len(sheet_raw['cues'])}轨三总线精修母带（{ver_tag.lstrip('_')}），"
        f"时长{int(dur_s//60)}分{int(dur_s%60):02d}秒，响度{lufs} LUFS（TP {true_peak} dBFS），"
        f"Scribe v3质检失败数={len(qa_failures)}。"
    )
    ledger["summary"]["scripts_ready"] = sum(1 for e in ledger["episodes"] if e.get("cue_sheet_file"))
    ledger["summary"]["episodes_mastered"] = sum(
        1 for e in ledger["episodes"] if e.get("status") == "mastered_and_archived"
    )
    ws.ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    run_record = {
        "timestamp": utc_now_iso(),
        "episode_id": episode_id,
        "title": title,
        "version": ver_tag.lstrip("_"),
        "duration_seconds": round(dur_s, 3),
        "integrated_lufs": lufs,
        "true_peak_dbfs": true_peak,
        "qa_failures": len(qa_failures),
        "elapsed_wall_s": round(time.time() - t0, 1),
        "drive_mp3_id": mp3_id,
        "drive_wav_id": wav_id,
    }
    ws.runs_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with ws.runs_jsonl_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(run_record, ensure_ascii=False) + "\n")

    if ws.enable_gdrive:
        _gdrive_update(ws.drive_ledger_file_id, ws.ledger_path)
        _gdrive_update(ws.drive_runs_file_id, ws.runs_jsonl_path)

    print(
        f"  [CHECKPOINT SAVED] {episode_id} ({ledger['summary']['episodes_mastered']}/"
        f"{len(ledger['episodes'])} done in {time.time()-t0:.1f}s)",
        flush=True,
    )
    return ep_entry


def run_episode_queue(
    ws: BatchWorkspace,
    *,
    from_ep: int,
    to_ep: int,
    max_count: int = 40,
    workers: int = 4,
) -> dict[str, Any]:
    """Run resilient episode synthesis & mastering across `[from_ep, to_ep]`."""
    rendered_now = 0
    for ep_num in range(from_ep, to_ep + 1):
        ep_id = f"E{ep_num:03d}"
        ledger = json.loads(ws.ledger_path.read_text(encoding="utf-8"))
        ep_entry = next(e for e in ledger["episodes"] if e["episode_id"] == ep_id)
        if ep_entry.get("status") == "mastered_and_archived" and (
            ep_entry.get("latest_master_mp3_drive_id") or not ws.enable_gdrive
        ):
            print(f"[QUEUE SKIP] {ep_id} already mastered_and_archived", flush=True)
            continue
        if rendered_now >= max_count:
            print(f"[QUEUE LIMIT REACHED] Rendered {rendered_now} new episodes; stopping before {ep_id}.", flush=True)
            break

        json_path, md_path = ws.find_episode_scripts(ep_num)
        render_and_archive_episode(ws, ep_id, json_path, md_path, workers=workers)
        rendered_now += 1

    ledger_after = json.loads(ws.ledger_path.read_text(encoding="utf-8"))
    mastered_total = ledger_after["summary"]["episodes_mastered"]
    total_eps = len(ledger_after["episodes"])
    print(
        f"\n[QUEUE COMPLETE] Newly rendered={rendered_now}, Total mastered_and_archived={mastered_total}/{total_eps}",
        flush=True,
    )
    return {
        "newly_rendered": rendered_now,
        "episodes_mastered": mastered_total,
        "total_episodes": total_eps,
    }
