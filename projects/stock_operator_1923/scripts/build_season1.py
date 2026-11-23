#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1923华尔街风云：〈股票大作手回忆录〉》.

Usage:
    PYTHONPATH=src python3 projects/stock_operator_1923/scripts/build_season1.py
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
from drama_helpers import ALLOWED_OPERATOR_ACOUSTIC_SPACES  # noqa: E402
from ep01_03_scripts import (  # noqa: E402
    build_audition_operator,
    build_e001_boy_plunger_bucket_shops,
    build_e002_wall_street_tuition_blowup,
    build_e003_old_turkey_sit_tight,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_panic_of_1907_morgan,
    build_e005_cotton_king_deadly_tips,
    build_e006_nothing_new_survival_laws,
)

PROJECT_DIR = REPO_ROOT / "projects" / "stock_operator_1923"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_OPERATOR_1923华尔街风云核心试听包", build_audition_operator, False),
        ("E001_黑板少年与对赌行_为什么纸带比一切内幕消息都诚实_完整广播剧台本", build_e001_boy_plunger_bucket_shops, True),
        ("E002_华尔街惨痛学费_为什么在真实交易所第一年就爆仓_完整广播剧台本", build_e002_wall_street_tuition_blowup, True),
        ("E003_老火鸡的黄金忠告_大钱从不是靠折腾而是靠坐稳赚来的_完整广播剧台本", build_e003_old_turkey_sit_tight, True),
        ("E004_1907大恐慌之夜_一人做空全华尔街直到摩根派人求情_完整广播剧台本", build_e004_panic_of_1907_morgan, True),
        ("E005_轻信棉花大王惨败_为什么最致命的敌人是别人的好心小道_完整广播剧台本", build_e005_cotton_king_deadly_tips, True),
        ("E006_华尔街没有新鲜事_百年不变的贪婪恐惧与交易铁律_完整广播剧台本", build_e006_nothing_new_survival_laws, True),
    ]

    total_cues = 0
    total_chars = 0
    for stem, fn, is_full_ep in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        ep_chars = 0
        sfx_n = 0
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in ALLOWED_OPERATOR_ACOUSTIC_SPACES:
                    raise SystemExit(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r}; "
                        f"allowed={sorted(ALLOWED_OPERATOR_ACOUSTIC_SPACES)}"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                max_len = max(max_len, n_cjk)
                if n_cjk > 88:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88): {spoken}")
            elif c.kind == "sfx":
                sfx_n += 1
                if not c.sfx_prompt.strip().endswith(", pure foley, no human voice"):
                    raise SystemExit(f"[{c.cue_id}] SFX prompt missing pure foley suffix: {c.sfx_prompt!r}")

        if is_full_ep:
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Full episode CJK char count {ep_chars} out of required range [2800, 3050]!"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] Full episode SFX count {sfx_n} out of required range [7, 10]!"
                )

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"✅ [{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字)"
        )

    print(
        f"\n🎉 《1923华尔街风云：〈股票大作手回忆录〉》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
