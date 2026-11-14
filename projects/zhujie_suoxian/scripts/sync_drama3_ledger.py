#!/usr/bin/env python3
"""Sync Drama 3 mastered episode Drive IDs and loudness stats into production_progress_ledger.json."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
LEDGER_PATH = (
    REPO_ROOT
    / "projects"
    / "zhujie_suoxian"
    / "00_声音选角档案与进度台账"
    / "production_progress_ledger.json"
)
PERSISTENT_LEDGER_PATH = Path(
    "/shared/user/.gemini/config/zhujie_suoxian_audio/00_声音选角档案与进度台账/production_progress_ledger.json"
)

DRIVE_LEDGER_FILE_ID = "1j8kUC_uKBZx1HJIkP8asE91TcUKnrjZ5"
DRIVE_MAIN_MASTERS_ID = "1NYCi-TP2VwR2bAmPwekeG-V5-YvLnNBG"
DRIVE_COLAB_OUTPUTS_ID = "1-5OT1dX9iFyCjkfXMnciNAeSybdhX74k"


def gdrive_ls(folder_id: str) -> list[dict[str, Any]]:
    raw = subprocess.check_output(
        ["gdrive", "readonly", "ls", folder_id, "--max", "0", "--json"],
        text=True,
    )
    return json.loads(raw)


def index_drama3_files(items: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Map episode_id -> {mp3, wav, srt, json, mp3_name} for `*Drama3*` files."""
    by_ep: dict[str, dict[str, str]] = {}
    for item in sorted(items, key=lambda x: x.get("modifiedTime", "")):
        name = item.get("name", "")
        if "Drama3" not in name and "drama3_master" not in name:
            continue
        m = re.match(r"^(E\d{3})_", name)
        if not m:
            continue
        ep_id = m.group(1)
        bucket = by_ep.setdefault(ep_id, {})
        fid = item["id"]
        if name.endswith(".mp3"):
            bucket["mp3"] = fid
            bucket["mp3_name"] = name
        elif name.endswith(".wav"):
            bucket["wav"] = fid
        elif name.endswith(".srt"):
            bucket["srt"] = fid
        elif name.endswith(".json"):
            bucket["json"] = fid
    return by_ep


def main() -> int:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    main_idx = index_drama3_files(gdrive_ls(DRIVE_MAIN_MASTERS_ID))
    colab_idx = index_drama3_files(gdrive_ls(DRIVE_COLAB_OUTPUTS_ID))

    drama3_count = 0
    total_mastered = 0

    for ep in ledger.get("episodes", []):
        ep_id = ep["episode_id"]
        rec = main_idx.get(ep_id) or colab_idx.get(ep_id)
        if rec and rec.get("mp3"):
            drama3_count += 1
            ep["status"] = "mastered_and_archived_drama3"
            ep["drama3_master_mp3_drive_id"] = rec.get("mp3", "")
            ep["drama3_master_wav_drive_id"] = rec.get("wav", "")
            ep["drama3_subtitles_srt_drive_id"] = rec.get("srt", "")
            ep["drama3_manifest_json_drive_id"] = rec.get("json", "")
            ep["latest_master_mp3_drive_id"] = rec.get("mp3", ep.get("latest_master_mp3_drive_id", ""))
            if rec.get("wav"):
                ep["latest_master_wav_drive_id"] = rec["wav"]
            if rec.get("srt"):
                ep["latest_subtitles_srt_drive_id"] = rec["srt"]
            if rec.get("json"):
                ep["latest_manifest_json_drive_id"] = rec["json"]
            mp3_name = rec.get("mp3_name", "")
            if "Drama3同源古风母带" not in ep.get("notes", ""):
                ep["notes"] = (
                    f"已完成 Fish Audio Drama 3 (35B FP8) + MOSS v2.0 + ACE-Step 1.5 XL 同源古风母带归档 ({mp3_name})。"
                )
        if ep.get("latest_master_mp3_drive_id"):
            total_mastered += 1

    summary = ledger.setdefault("summary", {})
    summary["episodes_mastered"] = total_mastered
    summary["drama3_episodes_mastered"] = drama3_count
    summary["checkpoint_status"] = (
        "all_120_drama3_masters_archived"
        if drama3_count >= 120
        else f"g4_drama3_running_{drama3_count}_of_120"
    )

    encoded = json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    LEDGER_PATH.write_text(encoded, encoding="utf-8")
    if PERSISTENT_LEDGER_PATH.parent.exists():
        PERSISTENT_LEDGER_PATH.write_text(encoded, encoding="utf-8")

    subprocess.run(
        ["gdrive", "mutate", "update", DRIVE_LEDGER_FILE_ID, str(LEDGER_PATH)],
        check=True,
    )
    print(f"Synced ledger: drama3_episodes_mastered={drama3_count}/120, total_mastered={total_mastered}/120")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
