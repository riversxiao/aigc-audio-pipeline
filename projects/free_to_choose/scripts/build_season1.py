#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1980芝加哥夜话：〈自由选择〉商业思想剧场》.

Usage:
    PYTHONPATH=src python3 projects/free_to_choose/scripts/build_season1.py
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
    build_audition_free,
    build_e001_pencil_miracle,
    build_e002_four_ways_spending,
    build_e003_great_depression_fed,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_consumer_protection_paradox,
    build_e005_school_vouchers_equality,
    build_e006_inflation_hangover_finale,
)

PROJECT_DIR = REPO_ROOT / "projects" / "free_to_choose"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_FREE_1980芝加哥夜话核心试听包", build_audition_free),
        ("E001_一只铅笔的奇迹_价格如何指挥全世界陌生人合作_完整广播剧台本", build_e001_pencil_miracle),
        ("E002_四种花钱的人_为什么花别人的钱永远最浪费_完整广播剧台本", build_e002_four_ways_spending),
        ("E003_1929大萧条真凶_美联储为什么在失火时关了水龙头_完整广播剧台本", build_e003_great_depression_fed),
        ("E004_谁在替消费者做主_职业牌照高墙与保护的悖论_完整广播剧台本", build_e004_consumer_protection_paradox),
        ("E005_给家长一张选择券_教育垄断工会与两种平等_完整广播剧台本", build_e005_school_vouchers_equality),
        ("E006_通胀只在一处诞生_印钞宿醉与1980芝加哥终章_完整广播剧台本", build_e006_inflation_hangover_finale),
    ]

    total_cues = 0
    total_chars = 0
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
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 105:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 105)")
            elif c.kind == "sfx":
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    raise SystemExit(
                        f"[{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': {c.sfx_prompt!r}"
                    )

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
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字 [{max_cue_id}])"
        )

    print(
        f"\n🎉 《1980芝加哥夜话：〈自由选择〉商业思想剧场》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
