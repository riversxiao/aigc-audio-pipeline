#!/usr/bin/env python3
"""Assemble a self-contained Colab 96GB `Fish Audio Drama 3` bundle for《跨境底牌：硅深暗战》/ Global Edge.

Packages:
  - `src/aigc_audio_pipeline/` (with `business_english_drama` domain, `atempo` 0.80x slow breakdown,
    corporate acoustic spaces, dual-script `zh-en` QA, and dual-line bilingual `.srt` mastering)
  - `voice_casting_registry.json` (8 locked roles + 7 MOSS Foley motifs)
  - `anchor_sources.json` (`v2_real_human_studio` provenance manifest)
  - `auditions/AUDITION*.json` + `cue_sheets/E*.json` (gracefully tolerates empty/missing cue-sheet directory)
  - `voice_anchors/*.{wav,txt}` + patched `voice_cast_drama3.json` (`anchor_schema_version="v2_real_human_studio"`,
    `domain="business_english_drama"`, `anchor_sample_rate_hz=44100`, all `accent_code`s & `source_voice_name`s preserved)
  - `prepare_global_edge_voice_anchors.py`, `run_global_edge_96gb_studio.py`, `launch_g4_global_edge_drama3.py`
  - Optional post-patch ZIP archive (`--zip` / `--zip-out`) containing the fully patched bundle
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any
import zipfile

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parent.parent

for _p in (REPO_ROOT / "src", REPO_ROOT / "colab_96gb"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from aigc_audio_pipeline.drama3_adapter import (  # noqa: E402
    DRAMA3_ANCHOR_SAMPLE_RATE,
    export_colab_96gb_bundle,
)
from aigc_audio_pipeline.models import VoiceCastingRegistry  # noqa: E402
from launch_g4_global_edge_drama3 import validate_production_voice_cast  # noqa: E402
from prepare_global_edge_voice_anchors import (  # noqa: E402
    ANCHOR_SCHEMA_VERSION,
    prepare_all_global_edge_anchors,
)

META_SUBDIR = "00_节目圣经与第一季24集总纲"
DEFAULT_CUE_SHEETS_SUBDIR = "02_分集广播剧台本"


def _write_bundle_zip(bundle_dir: Path, zip_path: Path) -> float:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(bundle_dir.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, arcname=file_path.relative_to(bundle_dir))
    return round(zip_path.stat().st_size / (1024.0 * 1024.0), 3)


def build_global_edge_bundle(
    *,
    project_dir: Path = PROJECT_DIR,
    cue_sheets_dir: Path | None = None,
    anchors_source_dir: Path | None = None,
    output_bundle_dir: Path,
    zip_output_path: Path | None = None,
    offline_stub_anchors: bool = True,
) -> dict[str, Any]:
    """Assemble and patch a self-contained Global Edge 96GB Drama 3 studio bundle."""
    meta_dir = project_dir / META_SUBDIR
    registry_path = meta_dir / "voice_casting_registry.json"
    anchor_sources_path = meta_dir / "anchor_sources.json"
    colab_dir = REPO_ROOT / "colab_96gb"

    if not registry_path.is_file():
        raise FileNotFoundError(f"Missing voice_casting_registry.json: {registry_path}")

    registry = VoiceCastingRegistry.load(registry_path)

    tmp_anchor_root: Path | None = None
    tmp_empty_cues_dir: Path | None = None
    try:
        if cue_sheets_dir is not None:
            effective_cue_dir = cue_sheets_dir
        else:
            effective_cue_dir = project_dir / DEFAULT_CUE_SHEETS_SUBDIR

        if not effective_cue_dir.is_dir():
            tmp_empty_cues_dir = Path(tempfile.mkdtemp(prefix="global_edge_empty_cues_"))
            effective_cue_dir = tmp_empty_cues_dir

        if anchors_source_dir is not None:
            vc_manifest_path = anchors_source_dir / "voice_cast_drama3.json"
            if not vc_manifest_path.is_file():
                raise FileNotFoundError(
                    f"Missing voice_cast_drama3.json inside --anchors-dir: {vc_manifest_path}"
                )
            ok_cast, cast_errors = validate_production_voice_cast(
                anchors_source_dir,
                required_roles=list(registry.roles.keys()),
                allow_offline_stub=offline_stub_anchors,
            )
            if not ok_cast:
                detail = "\n".join(f"  - {err}" for err in cast_errors)
                raise ValueError(
                    f"Invalid --anchors-dir ({anchors_source_dir}) failed voice cast validation "
                    f"(allow_offline_stub={offline_stub_anchors}):\n{detail}"
                )
            vc_data = json.loads(vc_manifest_path.read_text(encoding="utf-8"))
            anchor_base = anchors_source_dir
        else:
            tmp_anchor_root = Path(tempfile.mkdtemp(prefix="global_edge_anchor_stage_"))
            vc_data = prepare_all_global_edge_anchors(
                registry_path=registry_path,
                anchor_sources_path=anchor_sources_path if anchor_sources_path.is_file() else None,
                output_dir=tmp_anchor_root,
                offline_stub=offline_stub_anchors,
            )
            anchor_base = tmp_anchor_root

        anchor_specs: dict[str, dict[str, str]] = {}
        source_chars: dict[str, dict[str, Any]] = vc_data.get("characters", {})
        for role_id, cinfo in source_chars.items():
            anchor_specs[role_id] = {
                "audio_path": str((anchor_base / cinfo["anchor_wav"]).resolve()),
                "anchor_text": str(cinfo["anchor_text"]),
                "source_voice_name": str(cinfo.get("source_voice_name", "")),
            }

        studio_scripts = [
            p
            for p in (
                colab_dir / "prepare_global_edge_voice_anchors.py",
                colab_dir / "run_global_edge_96gb_studio.py",
                colab_dir / "launch_g4_global_edge_drama3.py",
            )
            if p.is_file()
        ]

        # Step 1: Export bundle WITHOUT creating ZIP yet so we can patch metadata & sidecars first
        res = export_colab_96gb_bundle(
            registry_path=registry_path,
            cue_sheets_dir=effective_cue_dir,
            anchor_specs=anchor_specs,
            output_bundle_dir=output_bundle_dir,
            pipeline_repo_root=REPO_ROOT,
            studio_scripts=studio_scripts,
            zip_output_path=None,
        )

        # Ensure standard subdirectories exist even when cue_sheets_dir was empty
        for sub in ("auditions", "cue_sheets", "voice_anchors", "custom_anchors"):
            (output_bundle_dir / sub).mkdir(parents=True, exist_ok=True)

        # Step 2: Patch `voice_cast_drama3.json` with v2_real_human_studio schema + preserved fields
        vc_out_path = output_bundle_dir / "voice_cast_drama3.json"
        vc_exported = json.loads(vc_out_path.read_text(encoding="utf-8"))
        vc_exported["project_id"] = registry.project_id
        vc_exported["project_title"] = registry.project_title
        vc_exported["domain"] = registry.domain or "business_english_drama"
        vc_exported["anchor_schema_version"] = ANCHOR_SCHEMA_VERSION
        vc_exported["anchor_sample_rate_hz"] = DRAMA3_ANCHOR_SAMPLE_RATE

        exported_chars: dict[str, dict[str, Any]] = vc_exported.get("characters", {})
        for role_id, cinfo in exported_chars.items():
            prof = registry.resolve_role(role_id)
            src_meta = source_chars.get(role_id, {})
            if prof is not None and not cinfo.get("accent_code"):
                cinfo["accent_code"] = prof.accent_code
            if src_meta.get("accent_code"):
                cinfo["accent_code"] = src_meta["accent_code"]
            if src_meta.get("source_voice_name"):
                cinfo["source_voice_name"] = src_meta["source_voice_name"]
        vc_exported["role_count"] = len(exported_chars)
        vc_out_path.write_text(
            json.dumps(vc_exported, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # Step 3: Copy `anchor_sources.json`, `voice_casting_registry.json`, and `.txt` sidecars
        if anchor_sources_path.is_file():
            dst_anc_src = output_bundle_dir / "anchor_sources.json"
            if anchor_sources_path.resolve() != dst_anc_src.resolve():
                shutil.copy2(anchor_sources_path, dst_anc_src)
        if not (output_bundle_dir / "voice_casting_registry.json").is_file():
            shutil.copy2(registry_path, output_bundle_dir / "voice_casting_registry.json")

        for role_id, cinfo in exported_chars.items():
            src_txt = anchor_base / "voice_anchors" / f"{role_id}.txt"
            dst_txt = output_bundle_dir / "voice_anchors" / f"{role_id}.txt"
            if src_txt.is_file() and src_txt.read_text(encoding="utf-8").strip():
                if src_txt.resolve() != dst_txt.resolve():
                    shutil.copy2(src_txt, dst_txt)
            else:
                dst_txt.write_text(str(cinfo.get("anchor_text", "")).strip() + "\n", encoding="utf-8")

        # Step 4: Write ZIP archive AFTER all patching & sidecar copies so ZIP is 100% consistent
        if zip_output_path is not None:
            res["zip_path"] = str(zip_output_path)
            res["zip_size_mb"] = _write_bundle_zip(output_bundle_dir, zip_output_path)
        else:
            res["zip_path"] = ""
            res["zip_size_mb"] = 0.0

        res["anchor_schema_version"] = ANCHOR_SCHEMA_VERSION
        res["domain"] = vc_exported["domain"]
        res["audition_count"] = len(list((output_bundle_dir / "auditions").glob("*.json")))
        return res
    finally:
        if tmp_anchor_root is not None:
            shutil.rmtree(tmp_anchor_root, ignore_errors=True)
        if tmp_empty_cues_dir is not None:
            shutil.rmtree(tmp_empty_cues_dir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="打包《跨境底牌：硅深暗战》/ Global Edge Colab 96GB Fish Audio Drama 3 自包含推理工程包"
    )
    parser.add_argument(
        "--project-dir",
        default=str(PROJECT_DIR),
        help="Global Edge 项目目录路径（默认 projects/global_edge）",
    )
    parser.add_argument(
        "--cue-sheets-dir",
        default="",
        help="可选：分集台本目录覆盖路径（默认 <project-dir>/02_分集广播剧台本）",
    )
    parser.add_argument(
        "--anchors-dir",
        default="",
        help="可选：已制备好的声线目录（含 voice_cast_drama3.json 与 voice_anchors/）",
    )
    parser.add_argument(
        "--output-dir",
        "--bundle-dir",
        dest="output_dir",
        default="/tmp/global_edge_96gb_studio",
        help="解压态工程包输出目录",
    )
    parser.add_argument(
        "--zip",
        nargs="?",
        const="__AUTO__",
        default=None,
        help="可选：输出 ZIP 归档路径（仅传 `--zip` 时自动写入 `<output-dir>.zip`）",
    )
    parser.add_argument(
        "--zip-out",
        default=None,
        help="可选：`--zip` 别名，指定 ZIP 归档包输出路径",
    )
    parser.add_argument(
        "--offline-stub",
        action="store_true",
        help="当未提供 --anchors-dir 时使用 FFmpeg 离线占位锚点（供 CI/本地干跑）",
    )
    parser.add_argument(
        "--real-anchors",
        action="store_true",
        help="当未提供 --anchors-dir 时尝试拉取真实人类录音棚锚点（严禁合成 TTS）",
    )
    args = parser.parse_args(argv)

    out_dir = Path(args.output_dir).resolve()
    zip_target: Path | None = None
    if args.zip_out:
        zip_target = Path(args.zip_out).resolve()
    elif args.zip is not None:
        if args.zip == "__AUTO__":
            zip_target = out_dir.parent / f"{out_dir.name}.zip"
        elif args.zip.strip():
            zip_target = Path(args.zip).resolve()

    offline_stub_flag = True if args.offline_stub or not args.real_anchors else False

    res = build_global_edge_bundle(
        project_dir=Path(args.project_dir).resolve(),
        cue_sheets_dir=Path(args.cue_sheets_dir).resolve() if args.cue_sheets_dir else None,
        anchors_source_dir=Path(args.anchors_dir).resolve() if args.anchors_dir else None,
        output_bundle_dir=out_dir,
        zip_output_path=zip_target,
        offline_stub_anchors=offline_stub_flag,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
