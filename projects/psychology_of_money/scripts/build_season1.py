#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《财富长跑课：〈金钱心理学〉普通人致富剧》.

Usage:
    PYTHONPATH=src python3 projects/psychology_of_money/scripts/build_season1.py
"""

from __future__ import annotations

import json
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
    build_audition_money,
    build_e001_janitor_and_banker,
    build_e002_luck_and_risk,
    build_e003_never_enough_trap,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_compounding_time_miracle,
    build_e005_tail_events_and_margin,
    build_e006_freedom_of_time_finale,
)

PROJECT_DIR = REPO_ROOT / "projects" / "psychology_of_money"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    anchor_cfg = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    if set(anchor_cfg.get("role_mappings", {}).keys()) != set(registry.roles.keys()):
        raise SystemExit(
            f"anchor_sources.json role_mappings keys {sorted(anchor_cfg.get('role_mappings', {}).keys())} "
            f"do not match voice_casting_registry.json roles {sorted(registry.roles.keys())}"
        )

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_MONEY_财富长跑课核心试听包", build_audition_money),
        ("E001_扫地老人与华尔街高管_为什么管钱拼的不是智商而是脾气_完整广播剧台本", build_e001_janitor_and_banker),
        ("E002_运气与风险的孪生真相_别把时代红利当神功也别把黑天鹅当无能_完整广播剧台本", build_e002_luck_and_risk),
        ("E003_永不知足的陷阱_够花一辈子的人为什么还要拿身家去赌_完整广播剧台本", build_e003_never_enough_trap),
        ("E004_复利的时间奇迹_为什么真正吓人的雪球全滚在后半程_完整广播剧台本", build_e004_compounding_time_miracle),
        ("E005_尾部事件与容错安全垫_允许自己看错一半照样赢的睡觉药_完整广播剧台本", build_e005_tail_events_and_margin),
        ("E006_财富的最高红利是掌控时间_豪车旁没人看车主真自由是决定今天_完整广播剧台本", build_e006_freedom_of_time_finale),
    ]

    total_cues = 0
    total_chars = 0
    failures: list[str] = []
    compiled: list[tuple[str, object]] = []

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
        else:
            if not (700 <= ep_chars <= 900):
                failures.append(f"[{cs.episode_id}] Audition spoken CJK chars {ep_chars} out of range [700, 900]")

        ok = not over_88 and (
            (2800 <= ep_chars <= 3050 and 7 <= sfx_n <= 10) if is_full_ep else (700 <= ep_chars <= 900)
        )
        extra = f" | OVER88: {', '.join(over_88)}" if over_88 else ""
        print(
            f"{'✅' if ok else '⚠️'} "
            f"[{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字 [{max_cue_id}]{extra})"
        )

        compiled.append((stem, cs))
        total_cues += len(cs.cues)
        total_chars += ep_chars

    if failures:
        print("\n❌ QA Validation Failures:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    for stem, cs in compiled:
        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

    print(
        f"\n🎉 《财富长跑课：〈金钱心理学〉普通人致富剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
