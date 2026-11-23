#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《零公式常识课：〈常识经济学〉街头案例剧》.

Usage:
    PYTHONPATH=src python3 projects/basic_economics/scripts/build_season1.py
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from aigc_audio_pipeline.adapter import write_cue_sheet_markdown  # noqa: E402
from aigc_audio_pipeline.models import VoiceCastingRegistry, extract_tags_and_spoken_text  # noqa: E402
from ep01_03_scripts import (  # noqa: E402
    build_audition_basic,
    build_e001_scarcity_price_signals,
    build_e002_shortages_and_surpluses,
    build_e003_profit_and_loss_brake,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_human_capital_wages,
    build_e005_comparative_advantage_trade,
    build_e006_common_sense_three_questions,
)

PROJECT_DIR = REPO_ROOT / "projects" / "basic_economics"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "basic_economics":
        raise SystemExit(f"Registry domain must be 'basic_economics', got {registry.domain!r}")
    for motif_id, m in registry.sonic_motifs.items():
        if m.cached_file != "":
            raise SystemExit(f"SonicMotif {motif_id!r} must have cached_file == '', got {m.cached_file!r}")
        if not m.sfx_prompt.endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif {motif_id!r} sfx_prompt must end with ', pure foley, no human voice'")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_BASIC_零公式常识课核心试听包", build_audition_basic),
        ("E001_稀缺不是穷_零公式看懂价格如何替全城管库存_完整广播剧台本", build_e001_scarcity_price_signals),
        ("E002_为什么排长队总在限价后_短缺与过剩的真实账本_完整广播剧台本", build_e002_shortages_and_surpluses),
        ("E003_亏损比利润更伟大_为什么好公司照样会倒闭_完整广播剧台本", build_e003_profit_and_loss_brake),
        ("E004_凭啥他工资比我高十倍_人力资本、经验与统计幻觉_完整广播剧台本", build_e004_human_capital_wages),
        ("E005_绝对优势与比较优势_为什么全能高手还得雇助理_完整广播剧台本", build_e005_comparative_advantage_trade),
        ("E006_别拿愿望当结果_常识经济学的三道防忽悠体检_完整广播剧台本", build_e006_common_sense_three_questions),
    ]

    total_cues = 0
    total_chars = 0
    ep_only_cues = 0
    ep_only_dlg = 0
    ep_only_sfx = 0
    ep_only_chars = 0
    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        max_cue_id = ""
        ep_chars = 0
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in _ALLOWED_SPACES:
                    raise SystemExit(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r} "
                        f"(allowed={sorted(_ALLOWED_SPACES)})"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                if "*" in spoken:
                    raise SystemExit(f"[{c.cue_id}] Markdown '*' not allowed in dialogue spoken text: {spoken}")
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 88:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88): {spoken}")
            elif c.kind == "sfx":
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    raise SystemExit(
                        f"[{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': {c.sfx_prompt!r}"
                    )

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")
        if cs.episode_id.startswith("E"):
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Full episode spoken CJK chars={ep_chars} out of target range [2800, 3050]"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] Full episode SFX count={sfx_n} out of target range [7, 10]"
                )
            ep_only_cues += len(cs.cues)
            ep_only_dlg += dlg_n
            ep_only_sfx += sfx_n
            ep_only_chars += ep_chars

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"✅ [{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字 [{max_cue_id}])"
        )

    print(
        f"\n🎉 《零公式常识课：〈常识经济学〉街头案例剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"\n   全套（含试听包）：总轨数 {total_cues}，总口播 {total_chars} 字。"
        f"\n   正片 E001–E006：总轨数 {ep_only_cues}（对白 {ep_only_dlg} | 拟音 {ep_only_sfx}），正片口播 {ep_only_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
