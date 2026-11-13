"""《诸界锁仙》Project Workspace Configuration & Batch Runner Adapter."""

from __future__ import annotations

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

_DEFAULT_PERSISTENT = Path("/shared/user/.gemini/config/zhujie_suoxian_audio")
_REPO_PROJECT_DIR = Path(__file__).resolve().parents[1]

BASE_DIR = Path(
    os.environ.get(
        "ZHUJIE_AUDIO_WORKSPACE",
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

DRIVE_SCRIPTS_FOLDER = "1QAw0bQdvDU-MSo3lz3icOfviI61hUczd"
DRIVE_MASTER_FOLDER = "1NYCi-TP2VwR2bAmPwekeG-V5-YvLnNBG"
DRIVE_MOTIFS_FOLDER = "1DPOHY_l_rYydKRaAoCfcqfxEILBsfTvj"
DRIVE_LEDGER_FILE_ID = "1j8kUC_uKBZx1HJIkP8asE91TcUKnrjZ5"
DRIVE_RUNS_FILE_ID = "1z7Lx5uWfzqK5ex48fGV9EVeDOM53fsxM"
DRIVE_REGISTRY_FILE_ID = "1K3YyZc2tuLBVrlQyRDzXSmWwGemf9m0q"


def get_workspace(enable_gdrive: bool = True) -> BatchWorkspace:
    return BatchWorkspace(
        workspace_dir=BASE_DIR,
        enable_gdrive=enable_gdrive,
        drive_ledger_file_id=DRIVE_LEDGER_FILE_ID,
        drive_runs_file_id=DRIVE_RUNS_FILE_ID,
        drive_registry_file_id=DRIVE_REGISTRY_FILE_ID,
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


__all__ = [
    "BASE_DIR",
    "CACHE_DIR",
    "DRIVE_LEDGER_FILE_ID",
    "DRIVE_MASTER_FOLDER",
    "DRIVE_MOTIFS_FOLDER",
    "DRIVE_REGISTRY_FILE_ID",
    "DRIVE_RUNS_FILE_ID",
    "DRIVE_SCRIPTS_FOLDER",
    "LEDGER_PATH",
    "MASTER_DIR",
    "MOTIFS_DIR",
    "REGISTRY_PATH",
    "RUNS_JSONL_PATH",
    "SCRIPTS_DIR",
    "canonical_episode_stem",
    "get_workspace",
    "measure_ebur128",
    "render_and_archive_episode",
]
