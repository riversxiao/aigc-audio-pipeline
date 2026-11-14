#!/usr/bin/env python3
"""Export 《逆模因部》 13 locked Mainland Mandarin studio dry anchors, 5 sci-fi motif specs,
and all 6 unabridged cue sheets (+ 6-line Audition Pack) into a self-contained 96GB Colab
Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL deployment bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from aigc_audio_pipeline.drama3_adapter import export_colab_96gb_bundle
from aigc_audio_pipeline.models import extract_tags_and_spoken_text

# Read-only mapping from verified Mainland Mandarin dry studio takes to 《逆模因部》 13 roles
ANTIMEMETICS_TO_STUDIO_ANCHOR_ROLE: dict[str, str] = {
    "narrator": "narrator",
    "db_terminal": "ancient_construct_echo",
    "marion_wheeler": "hongxiu_louzhu",
    "paul_kim": "lu_jin",
    "o5_8": "lu_qingcang",
    "clay": "male_disciple_a",
    "receptionist_npc": "su_qinghan",
    "alastair_grey": "pei_xuandu",
    "lyn_marness": "fu_bo",
    "bart_hughes": "male_disciple_b",
    "subject_055": "weathered_elder_npc",
    "scp_3125_voice": "zhao_kui",
    "infected_female": "eternal_night_whisper",
}


def discover_antimemetics_13_anchor_specs(
    studio_library_root: Path,
    ref_cue_sheets_dir: Path,
) -> dict[str, dict[str, str]]:
    """Read-only resolution of clean dry Mandarin vocal WAVs + verbatim transcripts for all 13 roles."""
    ref_pool: dict[str, dict[str, str]] = {}

    cue_lookup: dict[tuple[str, str], dict] = {}
    for ep_n in range(1, 7):
        ep_id = f"E{ep_n:03d}"
        for cs_path in sorted(ref_cue_sheets_dir.glob(f"{ep_id}_*.json")):
            cs_data = json.loads(cs_path.read_text(encoding="utf-8"))
            if cs_data.get("mode") == "audition_pack":
                continue
            for c in cs_data.get("cues", []):
                cue_lookup[(ep_id, c["cue_id"])] = c

    preferred_ep_cues = {
        "narrator": ("E005", "c028_nar_p032"),
        "lu_jin": ("E006", "c024_lu_jin_p024"),
        "fu_bo": ("E005", "c045_fu_bo_p052"),
        "su_qinghan": ("E001", "c021_su_excuse"),
        "pei_xuandu": ("E001", "c036_pei_whisper_threat"),
        "zhao_kui": ("E004", "c042_zhao_kui_p057"),
        "weathered_elder_npc": ("E003", "c009_weathered_elder_npc_p005"),
        "ancient_construct_echo": ("E005", "c030_ancient_construct_echo_p035"),
    }

    masters_dir = studio_library_root / "03_分集成片音频"
    manifest_by_ep: dict[str, dict] = {}
    for m_path in sorted(masters_dir.glob("E*_master_*.json")):
        d = json.loads(m_path.read_text(encoding="utf-8"))
        manifest_by_ep[d["episode_id"]] = d

    for src_role, (ep_id, cue_id) in preferred_ep_cues.items():
        m_data = manifest_by_ep[ep_id]
        item = next(it for it in m_data["timeline"] if it["cue_id"] == cue_id)
        raw_cue = cue_lookup[(ep_id, cue_id)]
        _, exact_spoken = extract_tags_and_spoken_text(raw_cue.get("tts_text") or raw_cue["text"])
        ref_pool[src_role] = {
            "audio_path": item["stem_file"],
            "anchor_text": exact_spoken,
        }

    needed_src_roles = set(ANTIMEMETICS_TO_STUDIO_ANCHOR_ROLE.values())
    cand_dir = studio_library_root / "01_声线试听小样" / "voice_design_ch03_40_candidates"
    locked_ch03_40 = json.loads((cand_dir / "locked_ch03_40_voices.json").read_text(encoding="utf-8"))
    for src_role, info in locked_ch03_40.items():
        if src_role in ref_pool or src_role not in needed_src_roles:
            continue
        dr_path = cand_dir / src_role / "_design_result.json"
        dr_data = json.loads(dr_path.read_text(encoding="utf-8"))
        cand = next(c for c in dr_data["candidates"] if c["generated_voice_id"] == info["voice_id"])
        ref_pool[src_role] = {
            "audio_path": cand["wav_path"],
            "anchor_text": dr_data["sample_text"].strip(),
        }

    aud_b_clips = studio_library_root / "01_声线试听小样" / "suite_b_library_benchmark" / "clips"
    ens_clips = cand_dir / "_ensemble_lib_tests"
    ref_pool["male_disciple_a"] = {
        "audio_path": str(aud_b_clips / "E001_AUDITION_B_LIBRARY_aud_06_pei_xuandu_hypocrite_pei_xuandu_5s3UifUu.wav"),
        "anchor_text": "紫府之下皆凡尘，而你这辈子连筑基的门槛都摸不到。方才你撕婚书时眼底藏着杀意，废你丹田，是替你留条残命。",
    }
    ref_pool["male_disciple_b"] = {
        "audio_path": str(aud_b_clips / "E001_AUDITION_B_LIBRARY_aud_02_lujin_cold_restraint_lu_jin_lkK6X9yp.wav"),
        "anchor_text": "为何不收？苏家欠我父亲一条命，这五十枚灵石与一瓶丹药，连利息的零头都不够，权当苏小姐赎身的路费。至于这枚寒渊佩，拿去便是。",
    }
    ref_pool["eternal_night_whisper"] = {
        "audio_path": str(ens_clips / "eternal_night_whisper_Linda.wav"),
        "anchor_text": "好黑啊……为什么你不点灯……把你的眼珠子抠出来点着吧……留下来陪我们吧……",
    }

    out_specs: dict[str, dict[str, str]] = {}
    for target_role, src_role in ANTIMEMETICS_TO_STUDIO_ANCHOR_ROLE.items():
        if src_role not in ref_pool:
            raise KeyError(f"Missing studio dry reference for {target_role} -> {src_role}")
        out_specs[target_role] = dict(ref_pool[src_role])
    return out_specs


def main() -> int:
    parser = argparse.ArgumentParser(description="Export 《逆模因部》 96GB Colab Drama 3 Studio Bundle")
    parser.add_argument(
        "--studio-library-root",
        default="/shared/user/.gemini/config/zhujie_suoxian_audio",
        help="Read-only path to existing Mainland Mandarin dry vocal anchor pool.",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/antimemetics_division_96gb_drama3_bundle",
        help="Directory to stage unpacked bundle.",
    )
    parser.add_argument(
        "--zip-out",
        default="/tmp/antimemetics_division_96gb_drama3_bundle.zip",
        help="Output .zip archive path.",
    )
    parser.add_argument(
        "--motifs-dir",
        default="/home/antigravity/.gemini/config/antimemetics_division_audio/_g4_stream/outputs/motifs",
        help="Optional directory of already-rendered 48kHz motif WAVs to bundle for cross-episode reuse.",
    )
    args = parser.parse_args()

    cue_sheets_dir = PROJECT_DIR / "02_分集广播剧台本"
    registry_path = PROJECT_DIR / "00_声音选角档案与进度台账" / "voice_casting_registry.json"
    ref_cue_sheets_dir = REPO_ROOT / "projects" / "zhujie_suoxian" / "02_分集广播剧台本"
    motifs_src = Path(args.motifs_dir) if args.motifs_dir and Path(args.motifs_dir).is_dir() else None

    specs = discover_antimemetics_13_anchor_specs(Path(args.studio_library_root), ref_cue_sheets_dir)
    summary = export_colab_96gb_bundle(
        registry_path=registry_path,
        cue_sheets_dir=cue_sheets_dir,
        anchor_specs=specs,
        output_bundle_dir=Path(args.output_dir),
        motifs_source_dir=motifs_src,
        bgm_source_dir=None,
        pipeline_repo_root=REPO_ROOT,
        studio_scripts=[REPO_ROOT / "colab_96gb" / "run_zhujie_96gb_studio.py"],
        zip_output_path=Path(args.zip_out) if args.zip_out else None,
    )
    cast_meta_src = Path(args.output_dir) / "voice_cast_drama3.json"
    cast_meta_dst = PROJECT_DIR / "00_声音选角档案与进度台账" / "voice_cast_drama3.json"
    cast_meta_dst.write_text(cast_meta_src.read_text(encoding="utf-8"), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
