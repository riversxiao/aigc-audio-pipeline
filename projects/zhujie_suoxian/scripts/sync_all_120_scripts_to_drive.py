#!/usr/bin/env python3
"""Validate all 120 compiled EpisodeCueSheets (E001–E120), mirror E041–E120 into the persistent
workspace, upload all new (.json + .md) scripts to Google Drive, and update production_progress_ledger.json."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aigc_audio_pipeline.batch_queue import _gdrive_update, _gdrive_upload
from aigc_audio_pipeline.models import EpisodeCueSheet, VoiceCastingRegistry
from batch_runner import (
    DRIVE_LEDGER_FILE_ID,
    DRIVE_REGISTRY_FILE_ID,
    DRIVE_SCRIPTS_FOLDER,
    LEDGER_PATH as PERSISTENT_LEDGER_PATH,
    REGISTRY_PATH as PERSISTENT_REGISTRY_PATH,
    SCRIPTS_DIR as PERSISTENT_SCRIPTS_DIR,
)

DRIVE_NOVEL_CHAPTERS_ID = "1twPsy8aPjRHhkpGiRUAEIpChRZRN6JTH"
REPO_PROJ_DIR = REPO_ROOT / "projects" / "zhujie_suoxian"
REPO_SCRIPTS_DIR = REPO_PROJ_DIR / "02_分集广播剧台本"
REPO_LEDGER_PATH = REPO_PROJ_DIR / "00_声音选角档案与进度台账" / "production_progress_ledger.json"
REPO_REGISTRY_PATH = REPO_PROJ_DIR / "00_声音选角档案与进度台账" / "voice_casting_registry.json"


def find_repo_script_pair(ep_num: int) -> tuple[Path, Path]:
    ep_id = f"E{ep_num:03d}"
    jsons = [
        p
        for p in sorted(REPO_SCRIPTS_DIR.glob(f"{ep_id}_*.json"))
        if "试听" not in p.name and "AUDITION" not in p.name
    ]
    if not jsons:
        raise FileNotFoundError(f"Missing compiled JSON cue sheet for {ep_id} in {REPO_SCRIPTS_DIR}")
    jp = jsons[-1]
    mp = jp.with_suffix(".md")
    if not mp.is_file():
        raise FileNotFoundError(f"Missing paired Markdown script for {ep_id}: {mp}")
    return jp, mp


def list_drive_folder_map(folder_id: str) -> dict[str, str]:
    raw = subprocess.check_output(
        ["gdrive", "readonly", "ls", folder_id, "--max", "0", "--json"],
        text=True,
    )
    data = json.loads(raw)
    items = data if isinstance(data, list) else data.get("files", [])
    return {it["name"]: it["id"] for it in items if "name" in it and "id" in it}


def main() -> int:
    registry = VoiceCastingRegistry.load(REPO_REGISTRY_PATH)
    print(f"Validating all 120 EpisodeCueSheets against {len(registry.roles)} locked voices...", flush=True)

    PERSISTENT_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    pairs: dict[int, tuple[Path, Path, EpisodeCueSheet]] = {}
    for ep_num in range(1, 121):
        jp, mp = find_repo_script_pair(ep_num)
        sheet = EpisodeCueSheet.load(jp)
        errs = sheet.validate(registry=registry, require_locked_voices=True)
        if errs:
            raise ValueError(f"[E{ep_num:03d}] Validation failed:\n" + "\n".join(errs))
        pairs[ep_num] = (jp, mp, sheet)
        # Mirror E041-E120 into persistent workspace using pure-Python bytes write (safe on FUSE)
        for src_p in (jp, mp):
            dst_p = PERSISTENT_SCRIPTS_DIR / src_p.name
            if not dst_p.is_file() or dst_p.stat().st_size != src_p.stat().st_size:
                dst_p.write_bytes(src_p.read_bytes())

    print("All 120 EpisodeCueSheets passed 100% validation & mirrored to persistent workspace!", flush=True)

    drive_chapters = list_drive_folder_map(DRIVE_NOVEL_CHAPTERS_ID)
    drive_scripts = list_drive_folder_map(DRIVE_SCRIPTS_FOLDER)

    ch_by_num: dict[int, tuple[str, str]] = {}
    for cname, cid in drive_chapters.items():
        m = re.match(r"^第(\d+)章_.*\.md$", cname)
        if m:
            ch_by_num[int(m.group(1))] = (cname, cid)

    ledger = json.loads(REPO_LEDGER_PATH.read_text(encoding="utf-8"))
    by_id = {e["episode_id"]: e for e in ledger["episodes"]}

    for ep_num in range(1, 121):
        ep_id = f"E{ep_num:03d}"
        jp, mp, sheet = pairs[ep_num]
        cname, cid = ch_by_num.get(ep_num, (Path(sheet.source_chapter_file).name, ""))
        if ep_id not in by_id:
            entry = {
                "episode_id": ep_id,
                "chapter_number": ep_num,
                "chapter_file_name": cname,
                "drive_chapter_file_id": cid,
                "status": "script_ready_for_g4_drama3",
                "cue_sheet_file": f"02_分集广播剧台本/{jp.name}",
                "audition_pack_file": "",
                "latest_master_wav_drive_id": "",
                "latest_master_mp3_drive_id": "",
                "script_json_drive_id": drive_scripts.get(jp.name, ""),
                "script_md_drive_id": drive_scripts.get(mp.name, ""),
                "notes": f"已完成4幕多角色无删节广播剧台本编译（共{len(sheet.cues)}轨，28角色同源国风声优锁定）。",
            }
            ledger["episodes"].append(entry)
            by_id[ep_id] = entry
        else:
            e = by_id[ep_id]
            e["cue_sheet_file"] = f"02_分集广播剧台本/{jp.name}"
            if cid and not e.get("drive_chapter_file_id"):
                e["drive_chapter_file_id"] = cid
            if not e.get("script_json_drive_id") and jp.name in drive_scripts:
                e["script_json_drive_id"] = drive_scripts[jp.name]
            if not e.get("script_md_drive_id") and mp.name in drive_scripts:
                e["script_md_drive_id"] = drive_scripts[mp.name]

    ledger["episodes"].sort(key=lambda item: int(item["chapter_number"]))

    upload_tasks: list[tuple[int, Path, Path, str, str]] = []
    for ep_num in range(1, 121):
        ep_id = f"E{ep_num:03d}"
        e = by_id[ep_id]
        jp, mp, _ = pairs[ep_num]
        jid = e.get("script_json_drive_id", "")
        mid = e.get("script_md_drive_id", "")
        if not jid or not mid:
            upload_tasks.append((ep_num, jp, mp, jid, mid))

    print(f"Uploading {len(upload_tasks)} new episode script pairs (.json + .md) to Google Drive...", flush=True)

    def _upload_one(task: tuple[int, Path, Path, str, str]) -> tuple[int, str, str]:
        ep_num, jp, mp, jid, mid = task
        if not jid:
            jid = _gdrive_upload(jp, DRIVE_SCRIPTS_FOLDER)
        if not mid:
            mid = _gdrive_upload(mp, DRIVE_SCRIPTS_FOLDER)
        return ep_num, jid, mid

    if upload_tasks:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for ep_num, jid, mid in pool.map(_upload_one, upload_tasks):
                ep_id = f"E{ep_num:03d}"
                by_id[ep_id]["script_json_drive_id"] = jid
                by_id[ep_id]["script_md_drive_id"] = mid
                print(f"  [DRIVE ARCHIVED] {ep_id} -> json={jid}, md={mid}", flush=True)

    ledger["summary"]["total_novel_chapters_synced"] = 120
    ledger["summary"]["scripts_ready"] = sum(
        1 for e in ledger["episodes"] if e.get("script_json_drive_id") and e.get("script_md_drive_id")
    )
    ledger["summary"]["voices_locked"] = len(registry.roles)
    ledger["summary"]["checkpoint_status"] = "all_120_scripts_ready_for_g4_drama3_marathon"

    serialized = json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    REPO_LEDGER_PATH.write_text(serialized, encoding="utf-8")
    PERSISTENT_LEDGER_PATH.write_text(serialized, encoding="utf-8")
    PERSISTENT_REGISTRY_PATH.write_text(REPO_REGISTRY_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    _gdrive_update(DRIVE_LEDGER_FILE_ID, REPO_LEDGER_PATH)
    _gdrive_update(DRIVE_REGISTRY_FILE_ID, REPO_REGISTRY_PATH)
    print(
        f"[ALL 120 SCRIPTS SYNCED] scripts_ready={ledger['summary']['scripts_ready']}/120 | "
        f"voices_locked={ledger['summary']['voices_locked']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
