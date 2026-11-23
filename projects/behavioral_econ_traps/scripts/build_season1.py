#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《决策的暗礁：行为经济学与〈思考，快与慢〉剧场》.

Usage:
    PYTHONPATH=src python3 projects/behavioral_econ_traps/scripts/build_season1.py
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
    build_audition_behav,
    build_e001_system1_system2,
    build_e002_loss_aversion_prospect,
    build_e003_anchoring_mental_accounting,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_sunk_cost_endowment,
    build_e005_overconfidence_hindsight,
    build_e006_nudge_decision_checklist,
)

PROJECT_DIR = REPO_ROOT / "projects" / "behavioral_econ_traps"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_SOURCES_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "behavioral_econ_traps":
        raise SystemExit(f"Unexpected registry domain={registry.domain!r}; expected 'behavioral_econ_traps'")
    if len(registry.roles) != 8:
        raise SystemExit(f"Expected 8 locked roles, found {len(registry.roles)}")
    for role_id, profile in registry.roles.items():
        if profile.status != "locked":
            raise SystemExit(f"Role {role_id!r} must have status='locked', got {profile.status!r}")

    anchors_raw = json.loads(ANCHOR_SOURCES_PATH.read_text(encoding="utf-8"))
    anchor_keys = set(anchors_raw.get("role_mappings", {}).keys())
    registry_keys = set(registry.roles.keys())
    if anchor_keys != registry_keys:
        raise SystemExit(
            f"anchor_sources.json role_mappings keys {sorted(anchor_keys)} != "
            f"voice_casting_registry.json roles keys {sorted(registry_keys)}"
        )

    for motif_id, motif_spec in registry.sonic_motifs.items():
        if motif_spec.cached_file != "":
            raise SystemExit(f"SonicMotif {motif_id!r} must have cached_file='', got {motif_spec.cached_file!r}")
        if not motif_spec.sfx_prompt.endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif {motif_id!r} sfx_prompt must end with ', pure foley, no human voice'")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_BEHAV_决策的暗礁核心试听包", build_audition_behav),
        ("E001_系统一与系统二_快脑偷懒与慢脑加班_完整广播剧台本", build_e001_system1_system2),
        ("E002_损失厌恶与前景理论_赚两百为何抵不过亏一百_完整广播剧台本", build_e002_loss_aversion_prospect),
        ("E003_锚定效应与心理账户_咖啡定价锚与私房钱秘密_完整广播剧台本", build_e003_anchoring_mental_accounting),
        ("E004_沉没成本与禀赋效应_烂电影硬看完与杯子值两倍_完整广播剧台本", build_e004_sunk_cost_endowment),
        ("E005_过度自信与后见之明_九成司机高估车技与马后炮_完整广播剧台本", build_e005_overconfidence_hindsight),
        ("E006_助推与聪明决策清单_默认选项与事前验尸防坑指南_完整广播剧台本", build_e006_nudge_decision_checklist),
    ]

    total_cues = 0
    total_chars = 0
    failures: list[str] = []

    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        max_cue_id = ""
        ep_chars = 0
        over_88: list[tuple[str, int]] = []
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in _ALLOWED_SPACES:
                    failures.append(
                        f"[{cs.episode_id}/{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r} "
                        f"(allowed={sorted(_ALLOWED_SPACES)})"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                if n_cjk > max_len:
                    max_len = n_cjk
                    max_cue_id = c.cue_id
                if n_cjk > 88:
                    over_88.append((c.cue_id, n_cjk))
            elif c.kind == "sfx":
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    failures.append(
                        f"[{cs.episode_id}/{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': "
                        f"{c.sfx_prompt!r}"
                    )

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")

        if over_88:
            failures.append(
                f"[{cs.episode_id}] Dialogue cues > 88 CJK chars: "
                + ", ".join(f"{cid}={n}" for cid, n in over_88)
            )
        if cs.episode_id == "AUDITION_BEHAV":
            if not (700 <= ep_chars <= 900):
                failures.append(f"[{cs.episode_id}] Audition spoken CJK chars={ep_chars} outside [700, 900]")
        else:
            if not (2800 <= ep_chars <= 3050):
                failures.append(f"[{cs.episode_id}] Spoken CJK chars={ep_chars} outside [2800, 3050]")
            if not (7 <= sfx_n <= 10):
                failures.append(f"[{cs.episode_id}] Pure-foley SFX count={sfx_n} outside [7, 10]")

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

    if failures:
        raise SystemExit("\n❌ QA constraint failures:\n" + "\n".join(failures))

    print(
        f"\n🎉 《决策的暗礁：行为经济学与〈思考，快与慢〉剧场》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
