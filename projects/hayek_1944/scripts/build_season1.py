#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1944剑桥夜话：〈通往奴役之路〉思想剧场》.

Usage:
    PYTHONPATH=src python3 projects/hayek_1944/scripts/build_season1.py
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
    build_audition_hayek,
    build_e001_abandoned_road,
    build_e002_price_signals,
    build_e003_rule_of_law,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_economic_control,
    build_e005_worst_get_on_top,
    build_e006_keynes_letter,
)

PROJECT_DIR = REPO_ROOT / "projects" / "hayek_1944"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_HAYEK_1944剑桥夜话六角色试听包", build_audition_hayek),
        ("E001_被遗忘的十字路口_为什么好心常常铺出坏路_完整有声剧台本", build_e001_abandoned_road),
        ("E002_菜市场与计划局_为什么没人能替所有人算清一笔账_完整有声剧台本", build_e002_price_signals),
        ("E003_红绿灯还是方向盘_法治真正保护的是什么_完整有声剧台本", build_e003_rule_of_law),
        ("E004_端谁的饭碗听谁的话_经济命脉安全网与个人选择_完整有声剧台本", build_e004_economic_control),
        ("E005_为什么最坏的人容易爬到顶层_与词义的悄悄变形_完整有声剧台本", build_e005_worst_get_on_top),
        ("E006_大西洋邮轮来信_1944哈耶克与凯恩斯的世纪之辩_完整有声剧台本", build_e006_keynes_letter),
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
                if n_cjk > 145:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 145)")

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

    print(f"\n🎉 《1944剑桥夜话：〈通往奴役之路〉思想剧场》全部 {len(builders)} 份台本编译校验通过！总轨数 {total_cues}，总口播 {total_chars} 字。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
