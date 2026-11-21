#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《克苏鲁神话·不可名状声音档案》.

Usage:
    PYTHONPATH=src python3 projects/cthulhu_archives/scripts/build_season1.py
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
    build_audition_cthulhu,
    build_e001_call_of_cthulhu,
    build_e002_innsmouth,
    build_e003_colour_out_of_space,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_whisperer_in_darkness,
    build_e005_dunwich_horror,
    build_e006_mountains_of_madness,
)

PROJECT_DIR = REPO_ROOT / "projects" / "cthulhu_archives"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_CTHULHU_密大绝密档案试听带", build_audition_cthulhu),
        ("E001_克苏鲁的呼唤_拉莱耶苏醒之夜_完整广播剧台本", build_e001_call_of_cthulhu),
        ("E002_印斯茅斯之影_逃离深潜者之镇_完整广播剧台本", build_e002_innsmouth),
        ("E003_星之彩_阿卡姆荒原坠落之夜_完整广播剧台本", build_e003_colour_out_of_space),
        ("E004_暗夜呢喃_佛蒙特黑山蜡筒录音_完整广播剧台本", build_e004_whisperer_in_darkness),
        ("E005_敦威治恐怖事件_隐形巨兽踏碎群山_完整广播剧台本", build_e005_dunwich_horror),
        ("E006_疯狂山脉_南极黑山深处的远古遗迹_完整广播剧台本", build_e006_mountains_of_madness),
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
                if n_cjk > 135:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 135)")

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

    print(f"\n🎉 《克苏鲁神话·不可名状声音档案》第一季全部 {len(builders)} 份台本编译校验通过！总轨数 {total_cues}，总口播 {total_chars} 字。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
