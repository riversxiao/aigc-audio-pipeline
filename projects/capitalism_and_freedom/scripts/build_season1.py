#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1962芝加哥激辩：〈资本主义与自由〉》.

Usage:
    PYTHONPATH=src python3 projects/capitalism_and_freedom/scripts/build_season1.py
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
    build_audition_capfree,
    build_e001_economic_political_freedom,
    build_e002_referee_vs_player,
    build_e003_monetary_rule_floating_rates,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_occupational_licensing_walls,
    build_e005_negative_tax_school_vouchers,
    build_e006_chicago_finale_market_boundaries,
)

PROJECT_DIR = REPO_ROOT / "projects" / "capitalism_and_freedom"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_SOURCES_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_STRAY_ASCII_RE = re.compile(r"[0-9A-Za-z]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "capitalism_and_freedom":
        raise SystemExit(f"Registry domain must be 'capitalism_and_freedom', got {registry.domain!r}")
    if len(registry.roles) != 8:
        raise SystemExit(f"Expected exactly 8 locked roles, got {len(registry.roles)}")
    for rid, rprof in registry.roles.items():
        if rprof.status != "locked":
            raise SystemExit(f"Role {rid!r} must have status='locked', got {rprof.status!r}")
    for mid, mspec in registry.sonic_motifs.items():
        if mspec.cached_file != "":
            raise SystemExit(f"SonicMotif {mid!r} must have cached_file='', got {mspec.cached_file!r}")
        if not mspec.sfx_prompt.endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif {mid!r} sfx_prompt must end with ', pure foley, no human voice'")

    anchor_cfg = json.loads(ANCHOR_SOURCES_PATH.read_text(encoding="utf-8"))
    anchor_keys = set(anchor_cfg.get("role_mappings", {}).keys())
    registry_keys = set(registry.roles.keys())
    if anchor_keys != registry_keys:
        raise SystemExit(
            f"anchor_sources.json role_mappings keys {sorted(anchor_keys)} != "
            f"voice_casting_registry.json roles keys {sorted(registry_keys)}"
        )

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_CAPFREE_1962芝加哥激辩核心试听包", build_audition_capfree),
        ("E001_经济自由与个人选择的共生关系_完整广播剧台本", build_e001_economic_political_freedom),
        ("E002_政府该当裁判还是下场踢球_完整广播剧台本", build_e002_referee_vs_player),
        ("E003_固定货币规则与浮动汇率预言_完整广播剧台本", build_e003_monetary_rule_floating_rates),
        ("E004_打破职业牌照与行会垄断高墙_完整广播剧台本", build_e004_occupational_licensing_walls),
        ("E005_负所得税与教育券制度重构_完整广播剧台本", build_e005_negative_tax_school_vouchers),
        ("E006_1962芝加哥夜话终章_市场边界与公民常识_完整广播剧台本", build_e006_chicago_finale_market_boundaries),
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
                stray = _STRAY_ASCII_RE.findall(spoken)
                if stray:
                    raise SystemExit(
                        f"[{c.cue_id}] Stray Arabic digits or Latin letters {stray!r} in spoken text: {spoken!r}"
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
        if cs.mode == "audition_pack":
            if not (700 <= ep_chars <= 900):
                raise SystemExit(
                    f"[{cs.episode_id}] Audition spoken CJK chars={ep_chars} out of required range [700, 900]"
                )
        else:
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Spoken CJK chars={ep_chars} out of required range [2800, 3050]"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] SFX cue count={sfx_n} out of required range [7, 10]"
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
        f"\n🎉 《1962芝加哥激辩：〈资本主义与自由〉》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
