#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1936剑桥迷雾：〈就业、利息和货币通论〉宏观思想剧场》.

Usage:
    PYTHONPATH=src python3 projects/keynes_1936/scripts/build_season1.py
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
    build_audition_keynes,
    build_e001_depression_deadlock,
    build_e002_thrift_paradox_multiplier,
    build_e003_beauty_contest_animal_spirits,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_liquidity_preference_trap,
    build_e005_burying_banknotes_fiscal_truth,
    build_e006_ideas_keynes_hayek_echo,
)

PROJECT_DIR = REPO_ROOT / "projects" / "keynes_1936"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_KEYNES_1936剑桥迷雾核心试听包", build_audition_keynes),
        ("E001_大萧条的死结_为什么想干活的人居然没活干_完整广播剧台本", build_e001_depression_deadlock),
        ("E002_节俭悖论与乘数魔术_为什么人人省钱反而全城变穷_完整广播剧台本", build_e002_thrift_paradox_multiplier),
        ("E003_选美比赛与动物精神_股市为什么根本不看公司真价值_完整广播剧台本", build_e003_beauty_contest_animal_spirits),
        ("E004_为什么大家死攥现金不花_流动性偏好与流动性陷阱_完整广播剧台本", build_e004_liquidity_preference_trap),
        ("E005_挖坑再填坑的玩笑_财政救火与政府花钱的真相_完整广播剧台本", build_e005_burying_banknotes_fiscal_truth),
        ("E006_思想比既得利益更危险_凯恩斯与哈耶克的百年回响_完整广播剧台本", build_e006_ideas_keynes_hayek_echo),
    ]

    total_cues = 0
    total_chars = 0
    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        ep_chars = 0
        for c in cs.cues:
            if c.kind == "dialogue":
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                max_len = max(max_len, n_cjk)
                if n_cjk > 105:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 105)")
            elif c.kind == "sfx":
                if not c.sfx_prompt.strip().endswith(", pure foley, no human voice"):
                    raise SystemExit(f"[{c.cue_id}] SFX prompt missing pure foley suffix: {c.sfx_prompt!r}")

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")
        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"✅ [{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字)"
        )

    print(
        f"\n🎉 《1936剑桥迷雾：〈就业、利息和货币通论〉宏观思想剧场》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
