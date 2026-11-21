#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《聊斋志异·午夜悬疑广播剧场》.

Usage:
    PYTHONPATH=src python3 projects/liaozhai_midnight/scripts/build_season1.py
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
    build_audition_liaozhai,
    build_e001_huapi,
    build_e002_niexiaoqian,
    build_e003_lupan,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_shibian,
    build_e005_laoshan,
    build_e006_kaochenghuang,
)

PROJECT_DIR = REPO_ROOT / "projects" / "liaozhai_midnight"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_LIAOZHAI_核心声线与恐怖氛围试听包", build_audition_liaozhai),
        ("E001_画皮_夜半窗纸后的第二张脸_完整广播剧台本", build_e001_huapi),
        ("E002_聂小倩_兰若寺荒夜白骨弦_完整广播剧台本", build_e002_niexiaoqian),
        ("E003_陆判_十王殿醉酒换心头_完整广播剧台本", build_e003_lupan),
        ("E004_尸变_蔡店荒村夜半起尸_完整广播剧台本", build_e004_shibian),
        ("E005_崂山道士_穿墙术与贪心梦醒_完整广播剧台本", build_e005_laoshan),
        ("E006_考城隍_寒门书生夜审阴司_完整广播剧台本", build_e006_kaochenghuang),
    ]

    total_cues = 0
    total_chars = 0
    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        # Guardrail: keep every single dialogue cue <= 120 CJK chars so Drama 3 stays super crisp
        max_len = 0
        ep_chars = 0
        for c in cs.cues:
            if c.kind == "dialogue":
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                max_len = max(max_len, n_cjk)
                if n_cjk > 125:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 125)")

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

    print(f"\n🎉 《聊斋志异·午夜悬疑广播剧场》第一季全部 {len(builders)} 份台本编译校验通过！总轨数 {total_cues}，总口播 {total_chars} 字。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
