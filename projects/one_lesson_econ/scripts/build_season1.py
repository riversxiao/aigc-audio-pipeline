#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《一课经济学剧场：别只看眼前那一步》.

Usage:
    PYTHONPATH=src python3 projects/one_lesson_econ/scripts/build_season1.py
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
    build_audition_onelesson,
    build_e001_second_order_lens,
    build_e002_automation_myth,
    build_e003_rent_control_trap,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_min_wage_and_subsidies,
    build_e005_inflation_hidden_theft,
    build_e006_savings_and_clarity_filter,
)

PROJECT_DIR = REPO_ROOT / "projects" / "one_lesson_econ"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_ONELESSON_一课经济学剧场核心试听包", build_audition_onelesson),
        ("E001_透视眼第一课_为什么坏经济学只看眼前这一步_完整广播剧台本", build_e001_second_order_lens),
        ("E002_机器抢饭碗的百年恐慌_为什么自动化没让人类失业_完整广播剧台本", build_e002_automation_myth),
        ("E003_为什么限租令反而让穷人租不到房_价格上限的暗雷_完整广播剧台本", build_e003_rent_control_trap),
        ("E004_好心办坏事的最低工资与行业补贴_谁被悄悄挤出门_完整广播剧台本", build_e004_min_wage_and_subsidies),
        ("E005_印钞救市的幻觉_为什么通货膨胀是隐形偷盗_完整广播剧台本", build_e005_inflation_hidden_theft),
        ("E006_省钱不是吝啬_储蓄投资与普通人的清醒滤镜_完整广播剧台本", build_e006_savings_and_clarity_filter),
    ]

    total_cues = 0
    total_chars = 0
    failures: list[str] = []

    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            failures.extend(f"[{cs.episode_id}] {e}" for e in errors)

        max_len = 0
        max_cue_id = ""
        ep_chars = 0
        over_88: list[str] = []
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in _ALLOWED_SPACES:
                    failures.append(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r} "
                        f"(allowed={sorted(_ALLOWED_SPACES)})"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                if "*" in spoken:
                    failures.append(f"[{c.cue_id}] Markdown asterisk '*' found in spoken text: {spoken!r}")
                if _LATIN_RE.search(spoken):
                    failures.append(f"[{c.cue_id}] Latin letters found in pure-Chinese spoken text: {spoken!r}")
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 88:
                    over_88.append(f"{c.cue_id}({n_cjk})")
                    failures.append(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88)")
            elif c.kind == "sfx":
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    failures.append(
                        f"[{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': {c.sfx_prompt!r}"
                    )

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")
        is_full_ep = cs.mode != "audition_pack"
        if is_full_ep:
            if not (2800 <= ep_chars <= 3050):
                failures.append(f"[{cs.episode_id}] Spoken CJK chars {ep_chars} out of required range [2800, 3050]")
            if not (7 <= sfx_n <= 10):
                failures.append(f"[{cs.episode_id}] Pure-foley SFX count {sfx_n} out of required range [7, 10]")

        extra = f" | OVER88: {', '.join(over_88)}" if over_88 else ""
        print(
            f"{'✅' if not over_88 and (not is_full_ep or (2800 <= ep_chars <= 3050 and 7 <= sfx_n <= 10)) else '⚠️'} "
            f"[{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字 [{max_cue_id}]{extra})"
        )

        if not failures:
            json_path = SCRIPTS_DIR / f"{stem}.json"
            md_path = SCRIPTS_DIR / f"{stem}.md"
            cs.save(json_path)
            write_cue_sheet_markdown(cs, md_path, registry=registry)

        total_cues += len(cs.cues)
        total_chars += ep_chars

    if failures:
        print("\n❌ QA Validation Failures:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print(
        f"\n🎉 《一课经济学剧场：别只看眼前那一步》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
