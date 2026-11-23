#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《经济机器怎么转：〈原则与大债务危机〉周期剧》.

Usage:
    PYTHONPATH=src python3 projects/debt_cycle_machine/scripts/build_season1.py
"""

from __future__ import annotations

from pathlib import Path
import json
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
    build_audition_debt,
    build_e001_transactions_and_credit,
    build_e002_spending_is_income,
    build_e003_short_term_debt_cycle,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_long_term_debt_peak,
    build_e005_beautiful_deleveraging,
    build_e006_three_timeless_rules,
)

PROJECT_DIR = REPO_ROOT / "projects" / "debt_cycle_machine"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_SOURCES_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_STRAY_ASCII_ALNUM_RE = re.compile(r"[A-Za-z0-9]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def _verify_registry_and_anchors(registry: VoiceCastingRegistry) -> None:
    anchor_data = json.loads(ANCHOR_SOURCES_PATH.read_text(encoding="utf-8"))
    reg_roles = set(registry.roles.keys())
    map_roles = set(anchor_data.get("role_mappings", {}).keys())
    if reg_roles != map_roles:
        raise SystemExit(
            f"Role mismatch between voice_casting_registry.json ({sorted(reg_roles)}) "
            f"and anchor_sources.json ({sorted(map_roles)})"
        )
    if registry.domain != "debt_cycle_machine":
        raise SystemExit(f"Expected domain='debt_cycle_machine', got {registry.domain!r}")
    for role_id, profile in registry.roles.items():
        if profile.status != "locked":
            raise SystemExit(f"Role {role_id!r} must have status='locked', got {profile.status!r}")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    _verify_registry_and_anchors(registry)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_DEBT_经济机器怎么转核心试听包", build_audition_debt),
        ("E001_交易与信贷_经济机器的三股动力_完整广播剧台本", build_e001_transactions_and_credit),
        ("E002_为什么一个人支出是另一个人收入_完整广播剧台本", build_e002_spending_is_income),
        ("E003_短期债务周期与央行利率弹簧_完整广播剧台本", build_e003_short_term_debt_cycle),
        ("E004_长期债务周期与泡沫顶点警报_完整广播剧台本", build_e004_long_term_debt_peak),
        ("E005_通缩萧条_通胀危机与和谐去杠杆四招_完整广播剧台本", build_e005_beautiful_deleveraging),
        ("E006_普通人与企业的跨周期三条底线_完整广播剧台本", build_e006_three_timeless_rules),
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
                stray = _STRAY_ASCII_ALNUM_RE.findall(spoken)
                if stray:
                    raise SystemExit(
                        f"[{c.cue_id}] Stray ASCII digits/letters {stray!r} found in spoken Chinese text: {spoken!r}"
                    )
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 88:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88): {spoken!r}")
            elif c.kind == "sfx":
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    raise SystemExit(
                        f"[{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': {c.sfx_prompt!r}"
                    )

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")

        if cs.episode_id.startswith("AUDITION"):
            if not (700 <= ep_chars <= 900):
                raise SystemExit(
                    f"[{cs.episode_id}] Audition CJK chars={ep_chars} out of target range [700, 900]"
                )
        else:
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Episode CJK chars={ep_chars} out of hard gate [2800, 3050]"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] Episode SFX count={sfx_n} out of hard gate [7, 10]"
                )

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
        f"\n🎉 《经济机器怎么转：〈原则与大债务危机〉周期剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
