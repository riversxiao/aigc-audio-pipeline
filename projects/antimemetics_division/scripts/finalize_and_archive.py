#!/usr/bin/env python3
"""Verify GPU-synthesized 《逆模因部》 masters, populate isolated workspace, update ledger, and archive to Google Drive."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_DIR.parents[1]
PERSISTENT_WS = Path("/home/antigravity/.gemini/config/antimemetics_division_audio")

if str(PROJECT_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR / "scripts"))

import sync_to_drive  # noqa: E402

EPISODE_FILE_STEMS = {
    "E001": "E001_第01章_SCP-055未知自封机密_电影感多人有声剧_v001",
    "E002": "E002_第02章_我们得谈谈五十五号_电影感多人有声剧_v001",
    "E003": "E003_第03章_逆模因学导论_电影感多人有声剧_v001",
    "E004": "E004_第04章_难以忘怀你本如此_电影感多人有声剧_v001",
    "E005": "E005_第05章_无色绿意案_电影感多人有声剧_v001",
    "E006": "E006_第06章_你最后一次首日上班_电影感多人有声剧_v001",
}


def ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def measure_loudness(path: Path) -> tuple[float, float]:
    p = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    m = re.search(r"\{\s*\"input_i\".*?\}", p.stderr, flags=re.DOTALL)
    if not m:
        raise RuntimeError(f"Could not parse loudnorm JSON for {path}")
    info = json.loads(m.group(0))
    return float(info["input_i"]), float(info["input_tp"])


def verify_srt_clean(srt_path: Path) -> int:
    txt = srt_path.read_text(encoding="utf-8")
    if not txt.strip():
        raise RuntimeError(f"Empty SRT file: {srt_path}")
    leaked = re.findall(r"<\|phoneme_start\|>|<whisper>|<forceful>|<slow>", txt)
    if leaked:
        raise RuntimeError(f"SRT contains leaked control tags {leaked}: {srt_path}")
    blocks = [b for b in txt.strip().split("\n\n") if b.strip()]
    if len(blocks) < 20:
        raise RuntimeError(f"Unexpectedly few SRT blocks ({len(blocks)}) in {srt_path}")
    return len(blocks)


def finalize_all(g4_out_dir: Path) -> dict[str, Any]:
    aud_ws = PERSISTENT_WS / "01_声线试听小样"
    ep_ws = PERSISTENT_WS / "03_分集成片音频"
    motif_ws = PERSISTENT_WS / "04_跨集复用声效与配乐母题"
    for d in (aud_ws, ep_ws, motif_ws):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Verify & stage Audition Reel
    aud_mp3 = g4_out_dir / "AUDITION_A_drama3_reel_v001.mp3"
    aud_wav = g4_out_dir / "AUDITION_A_drama3_reel_v001.wav"
    aud_json = g4_out_dir / "AUDITION_A_drama3_reel_v001.json"
    if not aud_mp3.is_file() or not aud_wav.is_file():
        raise FileNotFoundError(f"Missing AUDITION_A reel in {g4_out_dir}")
    aud_dur = ffprobe_duration(aud_mp3)
    aud_lufs, aud_tp = measure_loudness(aud_mp3)
    aud_stem = "AUDITION_A_逆模因部核心声优六句试听合集_v001"
    shutil.copy2(aud_mp3, aud_ws / f"{aud_stem}.mp3")
    shutil.copy2(aud_wav, aud_ws / f"{aud_stem}.wav")
    if aud_json.is_file():
        shutil.copy2(aud_json, aud_ws / f"{aud_stem}.json")

    # 2. Stage 5 reusable sci-fi motifs
    motifs_src = g4_out_dir / "motifs"
    staged_motifs: list[str] = []
    if motifs_src.is_dir():
        for mw in sorted(motifs_src.glob("*.wav")):
            shutil.copy2(mw, motif_ws / mw.name)
            staged_motifs.append(mw.name)

    # 3. Verify & stage all 6 episodes (E001-E006)
    qa_report: dict[str, dict[str, Any]] = {}
    for eid, cn_stem in EPISODE_FILE_STEMS.items():
        src_stem = f"{eid}_drama3_master_v001"
        mp3_p = g4_out_dir / f"{src_stem}.mp3"
        wav_p = g4_out_dir / f"{src_stem}.wav"
        srt_p = g4_out_dir / f"{src_stem}.srt"
        js_p = g4_out_dir / f"{src_stem}.json"
        for req_p in (mp3_p, wav_p, srt_p, js_p):
            if not req_p.is_file() or req_p.stat().st_size == 0:
                raise FileNotFoundError(f"Missing or empty episode artifact: {req_p}")

        dur_s = ffprobe_duration(mp3_p)
        if dur_s < 180.0:
            raise RuntimeError(f"{eid} duration too short ({dur_s:.1f}s < 180s)")
        lufs, tp = measure_loudness(mp3_p)
        if not (-17.5 <= lufs <= -14.5):
            raise RuntimeError(f"{eid} loudness out of broadcast range: {lufs:.2f} LUFS")
        srt_count = verify_srt_clean(srt_p)

        shutil.copy2(mp3_p, ep_ws / f"{cn_stem}.mp3")
        shutil.copy2(wav_p, ep_ws / f"{cn_stem}.wav")
        shutil.copy2(srt_p, ep_ws / f"{cn_stem}.srt")
        shutil.copy2(js_p, ep_ws / f"{cn_stem}.json")

        qa_report[eid] = {
            "canonical_stem": cn_stem,
            "duration_seconds": round(dur_s, 2),
            "duration_minutes": round(dur_s / 60.0, 2),
            "integrated_lufs": round(lufs, 2),
            "true_peak_dbtp": round(tp, 2),
            "srt_subtitles": srt_count,
            "mp3_size_mb": round(mp3_p.stat().st_size / (1024 * 1024), 2),
            "wav_size_mb": round(wav_p.stat().st_size / (1024 * 1024), 2),
        }
        print(
            f"✅ [{eid}] QA PASSED | {qa_report[eid]['duration_minutes']:.2f} min | "
            f"{lufs:.2f} LUFS (TP {tp:.2f} dBTP) | SRT {srt_count} lines | MP3 {qa_report[eid]['mp3_size_mb']} MB",
            flush=True,
        )

    # 4. Update production_progress_ledger.json prior to Google Drive sync
    led_path = PROJECT_DIR / "00_声音选角档案与进度台账" / "production_progress_ledger.json"
    led = json.loads(led_path.read_text(encoding="utf-8"))
    led["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total_dur_min = round(sum(v["duration_minutes"] for v in qa_report.values()), 2)
    led["summary"] = {
        "total_planned_episodes": 6,
        "scripts_ready": 6,
        "episodes_mastered": 6,
        "voices_locked": 13,
        "reusable_motifs_synthesized": len(staged_motifs),
        "total_runtime_minutes": total_dur_min,
        "synthesis_stack": "Fish Audio Drama 3 (35B MoE FP8) + MOSS-SoundEffect v2.0 + ACE-Step 1.5 XL (scifi_dark) + faster-whisper QA",
        "audition_reel": {
            "duration_seconds": round(aud_dur, 2),
            "integrated_lufs": round(aud_lufs, 2),
            "true_peak_dbtp": round(aud_tp, 2),
        },
    }
    for ep_entry in led.get("episodes", []):
        eid = ep_entry["episode_id"]
        if eid in qa_report:
            ep_entry["status"] = "mastered_and_archived"
            ep_entry.update(qa_report[eid])

    led_path.write_text(json.dumps(led, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 5. Run Google Drive full sync (uploads 01_声线试听小样, 03_分集成片音频, 04_跨集复用声效与配乐母题, 00_台账)
    colab_dir = REPO_ROOT / "colab_96gb"
    colab_files = [
        colab_dir / "Antimemetics_96GB_Drama3_Studio.ipynb",
        colab_dir / "launch_g4_antimemetics_drama3.py",
        colab_dir / "run_zhujie_96gb_studio.py",
        colab_dir / "colab_agent_bridge.py",
        PROJECT_DIR / "00_声音选角档案与进度台账" / "voice_cast_drama3.json",
    ]
    bzip_candidates = [
        Path("/home/antigravity/.antimemetics_colab/antimemetics_division_96gb_drama3_bundle.zip"),
        Path("/tmp/antimemetics_division_96gb_drama3_bundle.zip"),
    ]
    bzip = next((p for p in bzip_candidates if p.is_file()), None)
    drive_res = sync_to_drive.sync_all(bundle_zip=bzip, colab_files=colab_files)

    # Also mirror raw Drama3 `.mp3`/`.srt`/`.json` into 05_colab_outputs on Drive for studio parity
    colab_outputs_id = drive_res["drive_folders"].get("05_colab_outputs", "")
    if colab_outputs_id:
        for raw_f in sorted(g4_out_dir.glob("*_drama3_*")):
            if raw_f.is_file() and raw_f.suffix in (".mp3", ".srt", ".json"):
                sync_to_drive.upsert_file(raw_f, colab_outputs_id)

    return {
        "audition": {"duration_s": round(aud_dur, 2), "lufs": round(aud_lufs, 2)},
        "motifs": staged_motifs,
        "episodes": qa_report,
        "total_runtime_minutes": total_dur_min,
        "drive": drive_res,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--g4-out-dir",
        default="/home/antigravity/.gemini/config/antimemetics_division_audio/_g4_stream/outputs",
    )
    args = ap.parse_args()
    res = finalize_all(Path(args.g4_out_dir))
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
