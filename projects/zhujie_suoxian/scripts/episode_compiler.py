"""Compatibility re-export of core `aigc_audio_pipeline.compiler` for《诸界锁仙》builder scripts."""

from __future__ import annotations

from pathlib import Path
import sys

REPO_SRC = Path(__file__).resolve().parents[3] / "src"
if str(REPO_SRC) not in sys.path:
    sys.path.insert(0, str(REPO_SRC))

from aigc_audio_pipeline.compiler import (  # noqa: E402
    compile_episode_cue_sheet,
    extract_spoken_quotes_in_chapter,
    parse_chapter_paragraphs,
    save_episode_scripts,
)

__all__ = [
    "compile_episode_cue_sheet",
    "extract_spoken_quotes_in_chapter",
    "parse_chapter_paragraphs",
    "save_episode_scripts",
]
