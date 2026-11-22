#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1776爱丁堡夜话：〈国富论〉商业思想剧场》.

Usage:
    PYTHONPATH=src python3 projects/wealth_of_nations/scripts/build_season1.py
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
    build_audition_wealth,
    build_e001_pin_factory_division,
    build_e002_money_and_price,
    build_e003_wages_profits_guilds,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_invisible_hand_capital,
    build_e005_gold_illusion_trade_wars,
    build_e006_night_watchman_1776_farewell,
)

PROJECT_DIR = REPO_ROOT / "projects" / "wealth_of_nations"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_WEALTH_1776爱丁堡夜话核心试听包", build_audition_wealth),
        ("E001_一枚扣针的奇迹_为什么分工让世界突然变富了_完整广播剧台本", build_e001_pin_factory_division),
        ("E002_从贝壳到金币_钱是怎么长出来的与水钻悖论_完整广播剧台本", build_e002_money_and_price),
        ("E003_谁在切蛋糕_工资利润地租与为什么同行爱凑堆_完整广播剧台本", build_e003_wages_profits_guilds),
        ("E004_看不见的手真相_资本流向与纸币空中公路_完整广播剧台本", build_e004_invisible_hand_capital),
        ("E005_黄金不是财富_重商主义关税战与东印度公司毒药_完整广播剧台本", build_e005_gold_illusion_trade_wars),
        ("E006_守夜人的三张账单_政府边界与1776告别信_完整广播剧台本", build_e006_night_watchman_1776_farewell),
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
        f"\n🎉 《1776爱丁堡夜话：〈国富论〉商业思想剧场》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
