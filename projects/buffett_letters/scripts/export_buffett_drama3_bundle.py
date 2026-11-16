#!/usr/bin/env python3
"""Assemble a self-contained Colab 96GB `Fish Drama 3` bundle for《穿越周期的信》.

Packages:
  - `src/aigc_audio_pipeline/` (with bilingual `language_code`, `finance_podcast` polyphones, and simultaneous-translation ducking)
  - `voice_casting_registry.json` (`3+1` cross-class cast + 4 documentary Foley motifs)
  - `auditions/AUDITION_BUFFETT_四角色定角试听包.json` + `cue_sheets/E*.json`
  - `voice_anchors/*.wav` + `voice_cast_drama3.json` (uses existing real anchors if provided, else `--offline-stub` placeholders that `launch_g4_buffett_drama3.py` automatically upgrades to real 1990s Buffett & podcast anchors on Colab)
  - `prepare_buffett_voice_anchors.py`, `run_buffett_96gb_studio.py`, `launch_g4_buffett_drama3.py`
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parent.parent

for p in (REPO_ROOT / "src", REPO_ROOT / "colab_96gb"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from aigc_audio_pipeline.drama3_adapter import export_colab_96gb_bundle  # noqa: E402
from prepare_buffett_voice_anchors import prepare_all_buffett_anchors  # noqa: E402


def build_buffett_bundle(
    *,
    output_bundle_dir: Path,
    zip_output_path: Path | None = None,
    anchors_source_dir: Path | None = None,
    offline_stub_anchors: bool = True,
) -> dict[str, object]:
    registry_path = PROJECT_DIR / "00_节目圣经与第一季12期总纲" / "voice_casting_registry.json"
    cue_sheets_dir = PROJECT_DIR / "02_分期圆桌台本"
    colab_dir = REPO_ROOT / "colab_96gb"

    tmp_anchor_root: Path | None = None
    try:
        if anchors_source_dir and (anchors_source_dir / "voice_cast_drama3.json").is_file():
            vc_data = json.loads((anchors_source_dir / "voice_cast_drama3.json").read_text(encoding="utf-8"))
            anchor_base = anchors_source_dir
        else:
            tmp_anchor_root = Path(tempfile.mkdtemp(prefix="buffett_anchor_stage_"))
            vc_data = prepare_all_buffett_anchors(
                registry_path=registry_path,
                output_dir=tmp_anchor_root,
                offline_stub=offline_stub_anchors,
            )
            anchor_base = tmp_anchor_root

        anchor_specs: dict[str, dict[str, str]] = {}
        for role_id, cinfo in vc_data["characters"].items():
            anchor_specs[role_id] = {
                "audio_path": str((anchor_base / cinfo["anchor_wav"]).resolve()),
                "anchor_text": str(cinfo["anchor_text"]),
                "source_voice_name": str(cinfo.get("source_voice_name", "")),
            }

        studio_scripts = [
            colab_dir / "prepare_buffett_voice_anchors.py",
            colab_dir / "run_buffett_96gb_studio.py",
            colab_dir / "launch_g4_buffett_drama3.py",
        ]

        res = export_colab_96gb_bundle(
            registry_path=registry_path,
            cue_sheets_dir=cue_sheets_dir,
            anchor_specs=anchor_specs,
            output_bundle_dir=output_bundle_dir,
            pipeline_repo_root=REPO_ROOT,
            studio_scripts=studio_scripts,
            zip_output_path=zip_output_path,
        )
        return res
    finally:
        if tmp_anchor_root is not None:
            shutil.rmtree(tmp_anchor_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="打包《穿越周期的信》Colab 96GB Fish Drama 3 自包含推理工程包")
    parser.add_argument(
        "--bundle-dir",
        default="/tmp/buffett_letters_96gb_studio",
        help="解压态工程包输出目录",
    )
    parser.add_argument(
        "--zip-out",
        default="/tmp/buffett_letters_96gb_drama3_bundle.zip",
        help="ZIP 归档包输出路径（留空则不打包 ZIP）",
    )
    parser.add_argument(
        "--anchors-dir",
        default="",
        help="可选：已制备好的真实声线目录（含 voice_cast_drama3.json 与 voice_anchors/）",
    )
    parser.add_argument(
        "--real-anchors",
        action="store_true",
        help="在本地直接调用 yt-dlp / edge-tts 制备真实干音（默认使用轻量占位并在 Colab 端首次启动时自动提纯）",
    )
    args = parser.parse_args()

    res = build_buffett_bundle(
        output_bundle_dir=Path(args.bundle_dir).resolve(),
        zip_output_path=Path(args.zip_out).resolve() if args.zip_out else None,
        anchors_source_dir=Path(args.anchors_dir).resolve() if args.anchors_dir else None,
        offline_stub_anchors=not args.real_anchors,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
