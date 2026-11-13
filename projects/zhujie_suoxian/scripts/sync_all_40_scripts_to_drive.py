"""Upload all remaining compiled E007–E040 (.json + .md) cue sheets to Google Drive and update ledger."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys

SCRATCH_DIR = Path(__file__).resolve().parent
if str(SCRATCH_DIR) not in sys.path:
    sys.path.insert(0, str(SCRATCH_DIR))

from batch_runner import (
    DRIVE_LEDGER_FILE_ID,
    DRIVE_SCRIPTS_FOLDER,
    LEDGER_PATH,
    SCRIPTS_DIR,
    _gdrive_update,
    _gdrive_upload,
)
from run_queue import find_episode_scripts


def _upload_pair(ep_num: int, existing_json_id: str, existing_md_id: str) -> tuple[int, str, str, str]:
    jp, mp = find_episode_scripts(ep_num)
    if existing_json_id:
        _gdrive_update(existing_json_id, jp)
        jid = existing_json_id
    else:
        jid = _gdrive_upload(jp, DRIVE_SCRIPTS_FOLDER)
    if existing_md_id:
        _gdrive_update(existing_md_id, mp)
        mid = existing_md_id
    else:
        mid = _gdrive_upload(mp, DRIVE_SCRIPTS_FOLDER)
    return ep_num, f"02_分集广播剧台本/{jp.name}", jid, mid


def main() -> None:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    by_id = {e["episode_id"]: e for e in ledger["episodes"]}

    tasks: list[tuple[int, str, str]] = []
    for ep_num in range(1, 41):
        ep_id = f"E{ep_num:03d}"
        e = by_id[ep_id]
        if not e.get("script_json_drive_id") or not e.get("script_md_drive_id"):
            tasks.append((ep_num, e.get("script_json_drive_id", ""), e.get("script_md_drive_id", "")))

    print(f"Uploading {len(tasks)} episode script pairs (.json + .md) to Google Drive...", flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = [pool.submit(_upload_pair, n, jid, mid) for n, jid, mid in tasks]
        for fut in futs:
            ep_num, rel_file, jid, mid = fut.result()
            ep_id = f"E{ep_num:03d}"
            e = by_id[ep_id]
            e["cue_sheet_file"] = rel_file
            e["script_json_drive_id"] = jid
            e["script_md_drive_id"] = mid
            if e.get("status") in (None, "", "pending", "pending_script"):
                e["status"] = "script_ready_awaiting_credits"
            print(f"  [SCRIPT ARCHIVED] {ep_id} -> json={jid}, md={mid}", flush=True)

    ledger["summary"]["scripts_ready"] = sum(
        1 for e in ledger["episodes"] if e.get("script_json_drive_id") and e.get("script_md_drive_id")
    )
    ledger["summary"]["episodes_mastered"] = sum(
        1 for e in ledger["episodes"] if e.get("status") == "mastered_and_archived"
    )
    LEDGER_PATH.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _gdrive_update(DRIVE_LEDGER_FILE_ID, LEDGER_PATH)
    print(
        f"[ALL SCRIPTS SYNCED] scripts_ready={ledger['summary']['scripts_ready']}/40, "
        f"episodes_mastered={ledger['summary']['episodes_mastered']}/40",
        flush=True,
    )


if __name__ == "__main__":
    main()
