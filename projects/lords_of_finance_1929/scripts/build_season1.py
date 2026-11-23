#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1929黄金镣铐：〈金融之王〉四央行行长博弈》.

Usage:
    PYTHONPATH=src python3 projects/lords_of_finance_1929/scripts/build_season1.py
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
    build_audition_lords,
    build_e001_postwar_reparations_four_governors,
    build_e002_weimar_hyperinflation_rentenmark,
    build_e003_churchill_gold_standard_pound,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_long_island_summit_bubble,
    build_e005_crash_and_golden_fetters,
    build_e006_leaving_gold_and_modern_lessons,
)

PROJECT_DIR = REPO_ROOT / "projects" / "lords_of_finance_1929"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_STRAY_ASCII_RE = re.compile(r"[0-9A-Za-z]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "lords_of_finance_1929":
        raise SystemExit(f"Expected registry domain='lords_of_finance_1929', got {registry.domain!r}")

    for role_id, profile in registry.roles.items():
        if profile.status != "locked":
            raise SystemExit(f"Role {role_id!r} must have status='locked', got {profile.status!r}")

    raw_reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for motif_id, mdata in raw_reg.get("sonic_motifs", {}).items():
        if "asset_path" in mdata:
            raise SystemExit(f"SonicMotif {motif_id!r} must use 'cached_file', NEVER 'asset_path'!")
        if "cached_file" not in mdata:
            raise SystemExit(f"SonicMotif {motif_id!r} missing 'cached_file' field!")

    anchor_cfg = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    if set(anchor_cfg.get("role_mappings", {}).keys()) != set(registry.roles.keys()):
        raise SystemExit("anchor_sources.json role_mappings keys do not match voice_casting_registry.json roles 1-to-1!")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_LORDS_1929黄金镣铐核心试听包", build_audition_lords),
        ("E001_战后赔款与四位央行掌门登场_完整广播剧台本", build_e001_postwar_reparations_four_governors),
        ("E002_1923魏玛印钞机与百万马克买面包_完整广播剧台本", build_e002_weimar_hyperinflation_rentenmark),
        ("E003_丘吉尔重返金本位与英镑枷锁_完整广播剧台本", build_e003_churchill_gold_standard_pound),
        ("E004_1927长岛密会降息埋下华尔街泡沫_完整广播剧台本", build_e004_long_island_summit_bubble),
        ("E005_1929崩盘与黄金镣铐窒息全球_完整广播剧台本", build_e005_crash_and_golden_fetters),
        ("E006_放弃金本位破局与现代央行独立性教训_完整广播剧台本", build_e006_leaving_gold_and_modern_lessons),
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
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in _ALLOWED_SPACES:
                    failures.append(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r} "
                        f"(allowed={sorted(_ALLOWED_SPACES)})"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                bad_ascii = _STRAY_ASCII_RE.findall(spoken)
                if bad_ascii:
                    failures.append(f"[{c.cue_id}] Stray Arabic/Latin chars {bad_ascii!r} in spoken text: {spoken!r}")
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 88:
                    failures.append(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88)")
            elif c.kind == "sfx":
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    failures.append(
                        f"[{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': {c.sfx_prompt!r}"
                    )

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")

        if cs.episode_id.startswith("AUDITION"):
            if not (700 <= ep_chars <= 900):
                failures.append(f"[{cs.episode_id}] Audition CJK count {ep_chars} out of required range [700, 900]")
        else:
            if not (2800 <= ep_chars <= 3050):
                failures.append(f"[{cs.episode_id}] Episode CJK count {ep_chars} out of required range [2800, 3050]")
            if not (7 <= sfx_n <= 10):
                failures.append(f"[{cs.episode_id}] Episode SFX count {sfx_n} out of required range [7, 10]")

        print(
            f"{'✅' if not any(f'[{cs.episode_id}]' in x for x in failures) else '⚠️'} "
            f"[{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字 [{max_cue_id}])"
        )

        if not failures:
            json_path = SCRIPTS_DIR / f"{stem}.json"
            md_path = SCRIPTS_DIR / f"{stem}.md"
            cs.save(json_path)
            write_cue_sheet_markdown(cs, md_path, registry=registry)
            total_cues += len(cs.cues)
            total_chars += ep_chars

    if failures:
        print("\n❌ Validation failures detected:")
        for f in failures:
            print("  -", f)
        return 1

    print(
        f"\n🎉 《1929黄金镣铐：〈金融之王〉四央行行长博弈》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
