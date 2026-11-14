#!/usr/bin/env python3
"""Idempotently provision and synchronize 《逆模因部》有声剧工程（SCP CC-BY-SA-3.0） on Google Drive."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[1]
PERSISTENT_WS = Path("/home/antigravity/.gemini/config/antimemetics_division_audio")
ROOT_FOLDER_NAME = "《逆模因部》有声剧工程（SCP CC-BY-SA-3.0）"


def _extract_id(out_text: str) -> str:
    try:
        data = json.loads(out_text)
        if isinstance(data, dict) and "id" in data:
            return str(data["id"])
    except Exception:
        pass
    m = re.search(r"ID:\s*([A-Za-z0-9_-]+)", out_text)
    if m:
        return m.group(1)
    raise RuntimeError(f"Could not parse Drive ID from: {out_text!r}")


def find_item_entry_in_parent(
    name: str, parent_id: str | None = None, mime_type: str | None = None
) -> dict[str, Any] | None:
    cmd = ["gdrive", "readonly", "search", "--name-exact", name, "--json"]
    if parent_id:
        cmd.extend(["--parent-id", parent_id])
    out = subprocess.check_output(cmd, text=True)
    data = json.loads(out)
    items = data if isinstance(data, list) else data.get("files", [])
    for it in items:
        if mime_type and it.get("mimeType") != mime_type:
            continue
        return it
    return None


def find_item_in_parent(name: str, parent_id: str | None = None, mime_type: str | None = None) -> str:
    it = find_item_entry_in_parent(name, parent_id=parent_id, mime_type=mime_type)
    return str(it["id"]) if it else ""


def ensure_folder(name: str, parent_id: str | None = None) -> str:
    existing = find_item_in_parent(name, parent_id=parent_id, mime_type="application/vnd.google-apps.folder")
    if existing:
        return existing
    cmd = ["gdrive", "mutate", "mkdir", name, "--json"]
    if parent_id:
        cmd.extend(["--parent", parent_id])
    out = subprocess.check_output(cmd, text=True)
    return _extract_id(out)


def upsert_file(local_path: Path, parent_id: str) -> str:
    entry = find_item_entry_in_parent(local_path.name, parent_id=parent_id)
    if entry:
        fid = str(entry["id"])
        remote_sz = int(entry.get("size") or -1)
        if local_path.suffix.lower() in (".mp3", ".wav", ".zip") and remote_sz == local_path.stat().st_size:
            return fid
        subprocess.run(["gdrive", "mutate", "update", fid, str(local_path)], check=True)
        return fid
    out = subprocess.check_output(
        ["gdrive", "mutate", "upload", str(local_path), "--parent", parent_id, "--json"],
        text=True,
    )
    return _extract_id(out)


def sync_all(bundle_zip: Path | None = None, colab_files: list[Path] | None = None) -> dict[str, Any]:
    root_id = ensure_folder(ROOT_FOLDER_NAME)
    subfolders = {
        "00_casting_and_ledgers": ensure_folder("00_声音选角档案与进度台账", root_id),
        "01_voice_auditions": ensure_folder("01_声线试听小样", root_id),
        "02_episode_scripts": ensure_folder("02_分集广播剧台本", root_id),
        "03_mastered_episodes": ensure_folder("03_分集成片音频", root_id),
        "04_reusable_motifs_and_stems": ensure_folder("04_跨集复用声效与配乐母题", root_id),
        "05_colab_96gb_studio": ensure_folder("05_Colab_96GB_FishDrama3_满血本地推理管线", root_id),
        "source_chapters": ensure_folder("source_chapters_中文精译全本", root_id),
    }
    colab_outputs_id = ensure_folder("outputs", subfolders["05_colab_96gb_studio"])
    subfolders["05_colab_outputs"] = colab_outputs_id

    # Update registry & ledger locally BEFORE uploading 00_casting_and_ledgers
    reg_path = PROJECT_DIR / "00_声音选角档案与进度台账" / "voice_casting_registry.json"
    led_path = PROJECT_DIR / "00_声音选角档案与进度台账" / "production_progress_ledger.json"

    reg_data = json.loads(reg_path.read_text(encoding="utf-8"))
    reg_data["drive_audio_root_id"] = root_id
    reg_path.write_text(json.dumps(reg_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    led_data = json.loads(led_path.read_text(encoding="utf-8"))
    led_data["drive_folders"] = {
        "audio_root": root_id,
        **subfolders,
    }
    led_data.setdefault("drive_files", {})

    # 1. Root attribution & README
    for fname in ("CC_BY_SA_3.0_ATTRIBUTION.md", "README.md"):
        fpath = PROJECT_DIR / fname
        if fpath.is_file():
            fid = upsert_file(fpath, root_id)
            led_data["drive_files"][fname] = fid

    # 2. Source chapters (6 Chinese novel chapters)
    for md in sorted((PROJECT_DIR / "source_chapters").glob("*.md")):
        upsert_file(md, subfolders["source_chapters"])

    # 3. Episode scripts (.json + .md) & Audition pack
    for sf in sorted((PROJECT_DIR / "02_分集广播剧台本").iterdir()):
        if sf.is_file():
            upsert_file(sf, subfolders["02_episode_scripts"])
    for af in sorted((PROJECT_DIR / "01_声线试听小样").iterdir()):
        if af.is_file():
            upsert_file(af, subfolders["01_voice_auditions"])

    # 4. Upload mastered audio & motifs if present in PERSISTENT_WS
    if PERSISTENT_WS.is_dir():
        for af in sorted((PERSISTENT_WS / "01_声线试听小样").glob("*")):
            if af.is_file() and af.suffix in (".mp3", ".wav", ".json"):
                upsert_file(af, subfolders["01_voice_auditions"])
        for mf in sorted((PERSISTENT_WS / "04_跨集复用声效与配乐母题").glob("*.wav")):
            upsert_file(mf, subfolders["04_reusable_motifs_and_stems"])
        for ep_f in sorted((PERSISTENT_WS / "03_分集成片音频").glob("*")):
            if ep_f.is_file() and ep_f.suffix in (".mp3", ".wav", ".srt", ".json"):
                fid = upsert_file(ep_f, subfolders["03_mastered_episodes"])
                for ep_entry in led_data.get("episodes", []):
                    eid = ep_entry["episode_id"]
                    if ep_f.name.startswith(f"{eid}_"):
                        if ep_f.suffix == ".mp3":
                            ep_entry["latest_master_mp3_drive_id"] = fid
                        elif ep_f.suffix == ".wav":
                            ep_entry["latest_master_wav_drive_id"] = fid
                        elif ep_f.suffix == ".srt":
                            ep_entry["latest_subtitles_srt_drive_id"] = fid
                        elif ep_f.suffix == ".json":
                            ep_entry["latest_manifest_json_drive_id"] = fid

    # 5. Upload Colab 96GB bundle & scripts if provided
    if bundle_zip and bundle_zip.is_file():
        led_data["drive_files"]["bundle_zip_id"] = upsert_file(bundle_zip, subfolders["05_colab_96gb_studio"])
    for cf in colab_files or []:
        if cf.is_file():
            led_data["drive_files"][cf.name] = upsert_file(cf, subfolders["05_colab_96gb_studio"])

    # 6. Save & upload casting bible, registries, and ledger
    led_path.write_text(json.dumps(led_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cfile in sorted((PROJECT_DIR / "00_声音选角档案与进度台账").iterdir()):
        if cfile.is_file():
            fid = upsert_file(cfile, subfolders["00_casting_and_ledgers"])
            key = cfile.name.replace(".", "_")
            led_data["drive_files"][key] = fid

    led_path.write_text(json.dumps(led_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    upsert_file(led_path, subfolders["00_casting_and_ledgers"])

    # Mirror updated json configs to persistent workspace
    if PERSISTENT_WS.is_dir():
        cfg_ws = PERSISTENT_WS / "00_声音选角档案与进度台账"
        cfg_ws.mkdir(parents=True, exist_ok=True)
        for cfile in (reg_path, led_path):
            (cfg_ws / cfile.name).write_bytes(cfile.read_bytes())

    return {
        "root_folder_id": root_id,
        "root_url": f"https://drive.google.com/drive/folders/{root_id}",
        "drive_folders": led_data["drive_folders"],
        "drive_files": led_data["drive_files"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Sync 《逆模因部》 project to Google Drive.")
    ap.add_argument("--bundle-zip", default="/tmp/antimemetics_division_96gb_drama3_bundle.zip")
    args = ap.parse_args()

    repo_root = PROJECT_DIR.parents[1]
    colab_dir = repo_root / "colab_96gb"
    colab_files = [
        colab_dir / "Antimemetics_96GB_Drama3_Studio.ipynb",
        colab_dir / "launch_g4_antimemetics_drama3.py",
        colab_dir / "run_zhujie_96gb_studio.py",
        colab_dir / "colab_agent_bridge.py",
        PROJECT_DIR / "00_声音选角档案与进度台账" / "voice_cast_drama3.json",
    ]
    bzip = Path(args.bundle_zip) if args.bundle_zip else None
    res = sync_all(bundle_zip=bzip if (bzip and bzip.is_file()) else None, colab_files=colab_files)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
