#!/usr/bin/env python3
"""Curate all 24 locked 《诸界锁仙》 Mainland Mandarin studio vocal anchors, 6 motifs, and 40 cue sheets
into a self-contained 96GB Colab Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL deployment bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from aigc_audio_pipeline.drama3_adapter import export_colab_96gb_bundle
from aigc_audio_pipeline.models import extract_tags_and_spoken_text


def discover_zhujie_24_anchor_specs(audio_workspace: Path, cue_sheets_dir: Path) -> dict[str, dict[str, str]]:
    """Resolve the cleanest, verbatim-verified dry WAV + spoken transcript for all 24 active roles."""
    specs: dict[str, dict[str, str]] = {}

    # 1. Roles with QA-verified, dry unconditioned studio takes from E001-E006 (10s - 20s sweet spot)
    cue_lookup: dict[tuple[str, str], dict] = {}
    for ep_n in range(1, 7):
        ep_id = f"E{ep_n:03d}"
        for cs_path in sorted(cue_sheets_dir.glob(f"{ep_id}_*.json")):
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
        "chu_xiazi": ("E006", "c039_chu_xiazi_p032"),
        "weathered_elder_npc": ("E003", "c009_weathered_elder_npc_p005"),
        "male_guard_captain": ("E006", "c048_male_guard_captain_p042"),
        "female_maid_npc": ("E006", "c045_female_maid_npc_p039"),
        "ancient_construct_echo": ("E005", "c030_ancient_construct_echo_p035"),
    }

    masters_dir = audio_workspace / "03_分集成片音频"
    manifest_by_ep: dict[str, dict] = {}
    for m_path in sorted(masters_dir.glob("E*_master_*.json")):
        d = json.loads(m_path.read_text(encoding="utf-8"))
        manifest_by_ep[d["episode_id"]] = d

    for role_id, (ep_id, cue_id) in preferred_ep_cues.items():
        m_data = manifest_by_ep[ep_id]
        item = next(it for it in m_data["timeline"] if it["cue_id"] == cue_id)
        raw_cue = cue_lookup[(ep_id, cue_id)]
        # Use exact phonetic spoken text (`tts_text` if overridden, else `text`) for 100% phoneme alignment
        _, exact_spoken = extract_tags_and_spoken_text(raw_cue.get("tts_text") or raw_cue["text"])
        specs[role_id] = {
            "audio_path": item["stem_file"],
            "anchor_text": exact_spoken,
        }

    # 2. Custom VoiceDesign (`eleven_ttv_v3`) locked roles for Chapters 07-40
    cand_dir = audio_workspace / "01_声线试听小样" / "voice_design_ch03_40_candidates"
    locked_ch03_40 = json.loads((cand_dir / "locked_ch03_40_voices.json").read_text(encoding="utf-8"))
    for role_id, info in locked_ch03_40.items():
        if role_id in specs:
            continue
        dr_path = cand_dir / role_id / "_design_result.json"
        dr_data = json.loads(dr_path.read_text(encoding="utf-8"))
        cand = next(c for c in dr_data["candidates"] if c["generated_voice_id"] == info["voice_id"])
        specs[role_id] = {
            "audio_path": cand["wav_path"],
            "anchor_text": dr_data["sample_text"].strip(),
        }

    # 3. Mainland Studio Library ensemble roles (15-16s natural speech clips + Ch40 eerie whisper)
    aud_b_clips = audio_workspace / "01_声线试听小样" / "suite_b_library_benchmark" / "clips"
    ens_clips = cand_dir / "_ensemble_lib_tests"
    specs["male_disciple_a"] = {
        "audio_path": str(aud_b_clips / "E001_AUDITION_B_LIBRARY_aud_06_pei_xuandu_hypocrite_pei_xuandu_5s3UifUu.wav"),
        "anchor_text": "紫府之下皆凡尘，而你这辈子连筑基的门槛都摸不到。方才你撕婚书时眼底藏着杀意，废你丹田，是替你留条残命。",
    }
    specs["male_disciple_b"] = {
        "audio_path": str(aud_b_clips / "E001_AUDITION_B_LIBRARY_aud_02_lujin_cold_restraint_lu_jin_lkK6X9yp.wav"),
        "anchor_text": "为何不收？苏家欠我父亲一条命，这五十枚灵石与一瓶丹药，连利息的零头都不够，权当苏小姐赎身的路费。至于这枚寒渊佩，拿去便是。",
    }
    specs["eternal_night_whisper"] = {
        "audio_path": str(ens_clips / "eternal_night_whisper_Linda.wav"),
        "anchor_text": "好黑啊……为什么你不点灯……把你的眼珠子抠出来点着吧……留下来陪我们吧……",
    }

    # 4. Dedicated VoiceDesign (`eleven_ttv_v3`) studio anchors for Chapters 41-120 Grand Finale core roles
    init_vd_dir = audio_workspace / "01_声线试听小样" / "voice_design_candidates"
    specs["jiang_qinghuang"] = {
        "audio_path": str(init_vd_dir / "design_suqinghan_cand1_zt8t4yac_v001.wav"),
        "anchor_text": "陆公子言重了。三年前陆伯父失陷天渊，苏家上下亦曾多方打探，奈何仙凡殊途，各有命数。如今清寒已入玄剑宗内门，大道在前，实在不宜再耽于俗世旧约。今日特来归还当年庚帖，也请陆公子交还那枚寒渊佩，自此男婚女嫁，两不相干。",
    }
    specs["tai_yi"] = {
        "audio_path": str(init_vd_dir / "design_narrator_cand2_27lNSssv_v001.wav"),
        "anchor_text": "北渊城深秋的冷雨，已经连着下了七日。残破的青瓦飞檐下，雨水顺着断裂的兽首滴落在天井青石板上。就在那枚灰白印记彻底崩碎的刹那，万古尘封的石门在陆烬识海中轰然洞开。九根断裂的青铜巨柱下，无数暗红锁链正死死缠绕着一口结满寒霜的古老白棺。",
    }
    specs["fifth_soul_self"] = {
        "audio_path": str(init_vd_dir / "design_lujin_cand1_qyh0QmEx_v001.wav"),
        "anchor_text": "为何不收？苏家欠我父亲一条命，这五十枚下品灵石与一瓶凝气丹，连当年救命利息的零头都不够，权当苏小姐今日登门赎身的路费。至于这枚寒渊佩，拿去便是。福伯，不必送客，去把大门关上，莫让外头的秋风吹灭了父亲灵前的长明灯。",
    }
    specs["shou_mu_ren"] = {
        "audio_path": str(cand_dir / "weathered_elder_npc" / "weathered_elder_npc_cand2_VfkYbZq5_v001.wav"),
        "anchor_text": "造孽啊，当年陆爷在城里何等威风，快拿回去罢，铜板下月再结也不迟。老汉我在这断头哨守了四十年界碑，三年前也是这么个鬼天，陆擎苍那汉子浑身是血走到老汉这石屋里歇脚，拿半袋白面换了一壶烧酒。后生，赶紧顺着前人脚印往下走，莫回头！",
    }

    return specs


def main() -> int:
    parser = argparse.ArgumentParser(description="Export 《诸界锁仙》 96GB Colab Drama 3 Studio Bundle")
    parser.add_argument(
        "--audio-workspace",
        default="/shared/user/.gemini/config/zhujie_suoxian_audio",
        help="Path to local 《诸界锁仙》 audio workspace containing cached stems, auditions, and motifs.",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/zhujie_suoxian_96gb_drama3_bundle",
        help="Directory to stage unpacked bundle.",
    )
    parser.add_argument(
        "--zip-out",
        default="/tmp/zhujie_suoxian_96gb_drama3_bundle.zip",
        help="Output .zip archive path.",
    )
    args = parser.parse_args()

    ws = Path(args.audio_workspace)
    proj_dir = REPO_ROOT / "projects" / "zhujie_suoxian"
    cue_sheets_dir = proj_dir / "02_分集广播剧台本"
    registry_path = ws / "00_声音选角档案与进度台账" / "voice_casting_registry.json"
    if not registry_path.is_file():
        registry_path = proj_dir / "00_声音选角档案与进度台账" / "voice_casting_registry.json"

    specs = discover_zhujie_24_anchor_specs(ws, cue_sheets_dir)
    summary = export_colab_96gb_bundle(
        registry_path=registry_path,
        cue_sheets_dir=cue_sheets_dir,
        anchor_specs=specs,
        output_bundle_dir=Path(args.output_dir),
        motifs_source_dir=ws / "04_跨集复用声效与配乐母题",
        bgm_source_dir=ws / "04_跨集复用声效与配乐母题",
        pipeline_repo_root=REPO_ROOT,
        studio_scripts=[REPO_ROOT / "colab_96gb" / "run_zhujie_96gb_studio.py"],
        zip_output_path=Path(args.zip_out) if args.zip_out else None,
    )
    # Also save portable `voice_cast_drama3_template.json` metadata (without binary WAVs) into Git repo
    cast_meta_src = Path(args.output_dir) / "voice_cast_drama3.json"
    cast_meta_dst = proj_dir / "00_声音选角档案与进度台账" / "voice_cast_drama3.json"
    cast_meta_dst.write_text(cast_meta_src.read_text(encoding="utf-8"), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
