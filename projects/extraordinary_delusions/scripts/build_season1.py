#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1841伦敦泡沫档案：〈大癫狂〉金融疯魔史》.

Usage:
    PYTHONPATH=src python3 projects/extraordinary_delusions/scripts/build_season1.py
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
from drama_helpers import ALLOWED_DELUSIONS_ACOUSTIC_SPACES  # noqa: E402
from ep01_03_scripts import (  # noqa: E402
    build_audition_delusions,
    build_e001_tulip_mania,
    build_e002_john_law_mississippi,
    build_e003_paris_bank_run_collapse,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_south_sea_newton,
    build_e005_bubble_companies_psychology,
    build_e006_alchemy_crowd_madness,
)

PROJECT_DIR = REPO_ROOT / "projects" / "extraordinary_delusions"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_DELUSIONS_1841伦敦泡沫档案核心试听包", build_audition_delusions, False),
        ("E001_一颗洋葱换豪宅_1637荷兰郁金香狂热全纪实_完整广播剧台本", build_e001_tulip_mania, True),
        ("E002_赌徒变身法国财神_约翰劳与密西西比纸币魔术_完整广播剧台本", build_e002_john_law_mississippi, True),
        ("E003_巴黎街头大踩踏_印钞机失控与密西西比帝国崩塌_完整广播剧台本", build_e003_paris_bank_run_collapse, True),
        ("E004_连牛顿都亏光老本_1720英国南海公司超级骗局_完整广播剧台本", build_e004_south_sea_newton, True),
        ("E005_最荒唐的造富项目_空气公司与击鼓传花心理学_完整广播剧台本", build_e005_bubble_companies_psychology, True),
        ("E006_从炼金术到群体盲从_为什么人类每隔十年就忘疼_完整广播剧台本", build_e006_alchemy_crowd_madness, True),
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
                if c.acoustic_space not in ALLOWED_DELUSIONS_ACOUSTIC_SPACES:
                    raise SystemExit(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r}; "
                        f"allowed={sorted(ALLOWED_DELUSIONS_ACOUSTIC_SPACES)}"
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
        f"\n🎉 《1841伦敦泡沫档案：〈大癫狂〉金融疯魔史》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
