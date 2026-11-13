"""Chunked Episode Render & Archive Queue Runner for《诸界锁仙》Audio Drama."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

SCRIPTS_CODE_DIR = Path(__file__).resolve().parent
REPO_SRC = SCRIPTS_CODE_DIR.parents[2] / "src"
for p in (str(REPO_SRC), str(SCRIPTS_CODE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from aigc_audio_pipeline.batch_queue import run_episode_queue  # noqa: E402
from batch_runner import get_workspace  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Render & archive《诸界锁仙》episodes in resilient chunks.")
    ap.add_argument("--from-ep", type=int, required=True, help="Start episode number (e.g. 7)")
    ap.add_argument("--to-ep", type=int, required=True, help="End episode number (e.g. 40)")
    ap.add_argument("--max-count", type=int, default=40, help="Max newly rendered episodes in this run")
    ap.add_argument("--workers", type=int, default=4, help="Concurrent workers (default 4, <= 5 API limit)")
    ap.add_argument("--no-gdrive", action="store_true", help="Run locally without Google Drive upload")
    args = ap.parse_args()

    ws = get_workspace(enable_gdrive=not args.no_gdrive)
    run_episode_queue(
        ws,
        from_ep=args.from_ep,
        to_ep=args.to_ep,
        max_count=args.max_count,
        workers=args.workers,
    )


if __name__ == "__main__":
    main()
