"""《逆模因部》Isolated Project Workspace Configuration & Batch Runner Adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

REPO_SRC = Path(__file__).resolve().parents[3] / "src"
if str(REPO_SRC) not in sys.path:
    sys.path.insert(0, str(REPO_SRC))

from aigc_audio_pipeline.batch_queue import (  # noqa: E402
    BatchWorkspace,
    canonical_episode_stem,
    measure_ebur128,
    render_and_archive_episode as _core_render_and_archive,
)

_DEFAULT_PERSISTENT = Path("/home/antigravity/.gemini/config/antimemetics_division_audio")
_REPO_PROJECT_DIR = Path(__file__).resolve().parents[1]

BASE_DIR = Path(
    os.environ.get(
        "ANTIMEMETICS_AUDIO_WORKSPACE",
        str(_DEFAULT_PERSISTENT if _DEFAULT_PERSISTENT.is_dir() else _REPO_PROJECT_DIR),
    )
)

LEDGER_PATH = BASE_DIR / "00_声音选角档案与进度台账" / "production_progress_ledger.json"
RUNS_JSONL_PATH = BASE_DIR / "00_声音选角档案与进度台账" / "production_runs.jsonl"
REGISTRY_PATH = BASE_DIR / "00_声音选角档案与进度台账" / "voice_casting_registry.json"
SCRIPTS_DIR = BASE_DIR / "02_分集广播剧台本"
MASTER_DIR = BASE_DIR / "03_分集成片音频"
MOTIFS_DIR = BASE_DIR / "04_跨集复用声效与配乐母题"
CACHE_DIR = BASE_DIR / ".cache"


def _load_drive_ids() -> dict[str, str]:
    lp = LEDGER_PATH if LEDGER_PATH.is_file() else (_REPO_PROJECT_DIR / "00_声音选角档案与进度台账" / "production_progress_ledger.json")
    if not lp.is_file():
        return {}
    data = json.loads(lp.read_text(encoding="utf-8"))
    return data.get("drive_files", {})


def get_workspace(enable_gdrive: bool = True) -> BatchWorkspace:
    dfiles = _load_drive_ids()
    return BatchWorkspace(
        workspace_dir=BASE_DIR,
        enable_gdrive=enable_gdrive,
        drive_ledger_file_id=dfiles.get("production_progress_ledger_json", ""),
        drive_runs_file_id=dfiles.get("production_runs_jsonl", ""),
        drive_registry_file_id=dfiles.get("voice_casting_registry_json", ""),
    )


def render_and_archive_episode(
    episode_id: str,
    script_json_path: Path,
    script_md_path: Path,
    workers: int = 4,
    enable_gdrive: bool = True,
) -> dict[str, Any]:
    ws = get_workspace(enable_gdrive=enable_gdrive)
    return _core_render_and_archive(
        ws,
        episode_id,
        script_json_path,
        script_md_path,
        workers=workers,
    )
