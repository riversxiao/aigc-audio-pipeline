#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《金钱的崛起：从美第奇银行到现代华尔街》.

Usage:
    PYTHONPATH=src python3 projects/ascent_of_money/scripts/build_season1.py
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
    build_audition_ascent,
    build_e001_medici_ledger,
    build_e002_venice_bonds,
    build_e003_amsterdam_voc_stock,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_scottish_actuarial_insurance,
    build_e005_mortgage_housing_revolution,
    build_e006_trust_crystallized_finale,
)

PROJECT_DIR = REPO_ROOT / "projects" / "ascent_of_money"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_SOURCES_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_FORBIDDEN_SPOKEN_ASCII_RE = re.compile(r"[0-9A-Za-z]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def _validate_project_configs(registry: VoiceCastingRegistry) -> None:
    raw_reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if raw_reg.get("domain") != "ascent_of_money":
        raise SystemExit(f"Registry domain must be 'ascent_of_money', got {raw_reg.get('domain')!r}")
    if len(registry.roles) != 8:
        raise SystemExit(f"Expected exactly 8 locked roles, got {len(registry.roles)}")
    for rid, prof in registry.roles.items():
        if prof.status != "locked":
            raise SystemExit(f"Role {rid!r} must have status='locked', got {prof.status!r}")
    for mid, raw_m in raw_reg.get("sonic_motifs", {}).items():
        if "asset_path" in raw_m:
            raise SystemExit(f"SonicMotif {mid!r} must NEVER contain 'asset_path'")
        if raw_m.get("cached_file") != "":
            raise SystemExit(f"SonicMotif {mid!r} must have cached_file='', got {raw_m.get('cached_file')!r}")
        if not str(raw_m.get("sfx_prompt", "")).endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif {mid!r} sfx_prompt must end with ', pure foley, no human voice'")

    anchor_cfg = json.loads(ANCHOR_SOURCES_PATH.read_text(encoding="utf-8"))
    reg_keys = set(registry.roles.keys())
    map_keys = set(anchor_cfg.get("role_mappings", {}).keys())
    if reg_keys != map_keys:
        raise SystemExit(
            f"anchor_sources.json role_mappings keys mismatch registry roles!\n"
            f"Only in registry: {sorted(reg_keys - map_keys)}\n"
            f"Only in anchor_sources: {sorted(map_keys - reg_keys)}"
        )


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    _validate_project_configs(registry)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_ASCENT_金钱的崛起核心试听包", build_audition_ascent),
        ("E001_粘土借条与美第奇复式记账银行_完整广播剧台本", build_e001_medici_ledger),
        ("E002_威尼斯国债与债券市场决定战争胜负_完整广播剧台本", build_e002_venice_bonds),
        ("E003_1602阿姆斯特丹东印度公司全球第一张股票_完整广播剧台本", build_e003_amsterdam_voc_stock),
        ("E004_苏格兰牧师精算与现代保险诞生_完整广播剧台本", build_e004_scottish_actuarial_insurance),
        ("E005_房贷证券化与普通人资产革命_完整广播剧台本", build_e005_mortgage_housing_revolution),
        ("E006_金钱是信任的结晶而非冰冷金属_完整广播剧台本", build_e006_trust_crystallized_finale),
    ]

    total_cues = 0
    total_chars = 0
    hard_failures: list[str] = []

    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            hard_failures.extend(f"[{cs.episode_id}] {e}" for e in errors)

        max_len = 0
        max_cue_id = ""
        ep_chars = 0
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in _ALLOWED_SPACES:
                    hard_failures.append(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r} "
                        f"(allowed={sorted(_ALLOWED_SPACES)})"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                bad_ascii = _FORBIDDEN_SPOKEN_ASCII_RE.findall(spoken)
                if bad_ascii:
                    hard_failures.append(
                        f"[{c.cue_id}] Stray ASCII digits/letters {bad_ascii!r} in spoken text: {spoken!r}"
                    )
                if c.tts_text:
                    _, spoken_tts = extract_tags_and_spoken_text(c.tts_text)
                    bad_tts_ascii = _FORBIDDEN_SPOKEN_ASCII_RE.findall(spoken_tts)
                    if bad_tts_ascii:
                        hard_failures.append(
                            f"[{c.cue_id}] Stray ASCII digits/letters {bad_tts_ascii!r} in tts_text: {spoken_tts!r}"
                        )
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 88:
                    hard_failures.append(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88)")
            elif c.kind == "sfx":
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    hard_failures.append(
                        f"[{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': {c.sfx_prompt!r}"
                    )

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")

        if cs.episode_id.startswith("AUDITION"):
            if not (700 <= ep_chars <= 900):
                hard_failures.append(
                    f"[{cs.episode_id}] Audition CJK count {ep_chars} outside target [700, 900]"
                )
        else:
            if not (2800 <= ep_chars <= 3050):
                hard_failures.append(
                    f"[{cs.episode_id}] Full episode CJK count {ep_chars} outside [2800, 3050]"
                )
            if not (7 <= sfx_n <= 10):
                hard_failures.append(
                    f"[{cs.episode_id}] Full episode SFX count {sfx_n} outside [7, 10]"
                )

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"{'✅' if not [x for x in hard_failures if cs.episode_id in x] else '⚠️'} "
            f"[{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字 [{max_cue_id}])"
        )

    if hard_failures:
        print("\n❌ HARD GATE FAILURES:")
        for msg in hard_failures:
            print("  -", msg)
        return 1

    print(
        f"\n🎉 《金钱的崛起：从美第奇银行到现代华尔街》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字，0 错误。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
