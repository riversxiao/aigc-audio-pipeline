#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《高手怎么出牌：〈策略思维与博弈论〉商业剧》.

Usage:
    PYTHONPATH=src python3 projects/game_theory_strategy/scripts/build_season1.py
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
    build_audition_game,
    build_e001_prisoners_dilemma,
    build_e002_backward_induction_mover_advantage,
    build_e003_burning_bridges_credible_commitment,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_price_war_traps_and_guarantees,
    build_e005_auction_winners_curse_signals,
    build_e006_repeated_games_cooperation_code,
)

PROJECT_DIR = REPO_ROOT / "projects" / "game_theory_strategy"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_STRAY_ASCII_RE = re.compile(r"[0-9A-Za-z]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    raw_registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for motif_id, motif_obj in raw_registry.get("sonic_motifs", {}).items():
        if "asset_path" in motif_obj:
            raise SystemExit(f"SonicMotif {motif_id!r} must use 'cached_file', NEVER 'asset_path'!")
        if "cached_file" not in motif_obj:
            raise SystemExit(f"SonicMotif {motif_id!r} is missing 'cached_file'!")

    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "game_theory_strategy":
        raise SystemExit(f"Expected registry domain='game_theory_strategy', got {registry.domain!r}")
    if len(registry.roles) != 8:
        raise SystemExit(f"Expected exactly 8 locked roles, got {len(registry.roles)}")
    for rid, prof in registry.roles.items():
        if prof.status != "locked":
            raise SystemExit(f"Role {rid!r} status={prof.status!r}, expected 'locked'")
        _, aud_spoken = extract_tags_and_spoken_text(prof.audition_line)
        if _STRAY_ASCII_RE.search(aud_spoken):
            raise SystemExit(f"Role {rid!r} audition_line contains stray ASCII/digits: {aud_spoken!r}")

    anchor_cfg = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    if set(anchor_cfg.get("role_mappings", {}).keys()) != set(registry.roles.keys()):
        raise SystemExit("anchor_sources.json role_mappings keys do not match voice_casting_registry.json roles 1-to-1!")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_GAME_高手怎么出牌核心试听包", build_audition_game),
        ("E001_囚徒困境与为什么聪明人一起选最差解_完整广播剧台本", build_e001_prisoners_dilemma),
        ("E002_倒推法与先发后发优势_完整广播剧台本", build_e002_backward_induction_mover_advantage),
        ("E003_破釜沉舟与可信承诺_完整广播剧台本", build_e003_burning_bridges_credible_commitment),
        ("E004_价格战如何避免两败俱伤_完整广播剧台本", build_e004_price_war_traps_and_guarantees),
        ("E005_拍卖会的赢家诅咒与信息信号_完整广播剧台本", build_e005_auction_winners_curse_signals),
        ("E006_重复博弈与把零和变共赢的合作密码_完整广播剧台本", build_e006_repeated_games_cooperation_code),
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
                bad = _STRAY_ASCII_RE.findall(spoken)
                if bad:
                    raise SystemExit(
                        f"[{c.cue_id}] Stray Arabic digits or Latin letters {bad!r} in spoken dialogue: {spoken!r}"
                    )
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 88:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88)")
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
                    f"[{cs.episode_id}] Audition CJK count {ep_chars} out of required range [700, 900]"
                )
        else:
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Episode CJK count {ep_chars} out of required range [2800, 3050]"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] Episode SFX count {sfx_n} out of required range [7, 10]"
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
        f"\n🎉 《高手怎么出牌：〈策略思维与博弈论〉商业剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
