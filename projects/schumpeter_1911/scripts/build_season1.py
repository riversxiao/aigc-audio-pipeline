#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1911维也纳风暴：〈经济发展理论〉创新剧》.

Usage:
    PYTHONPATH=src python3 projects/schumpeter_1911/scripts/build_season1.py
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
from drama_helpers import PROJECT_ALLOWED_ACOUSTIC_SPACES  # noqa: E402
from ep01_03_scripts import (  # noqa: E402
    build_audition_schumpeter,
    build_e001_circular_flow_vs_railway,
    build_e002_five_new_combinations,
    build_e003_banker_midwife_of_innovation,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_creative_destruction_pains,
    build_e005_swarms_boom_and_bust,
    build_e006_three_ambitions_and_1950_prophecy,
)

PROJECT_DIR = REPO_ROOT / "projects" / "schumpeter_1911"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "schumpeter_1911":
        raise SystemExit(f"[registry] Expected domain='schumpeter_1911', got {registry.domain!r}")
    for motif_id, m in registry.sonic_motifs.items():
        if m.cached_file != "":
            raise SystemExit(f"[registry] SonicMotif {motif_id!r} must use cached_file='' (got {m.cached_file!r})")
        if not m.sfx_prompt.strip().endswith(", pure foley, no human voice"):
            raise SystemExit(f"[registry] SonicMotif {motif_id!r} missing pure-foley suffix: {m.sfx_prompt!r}")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_SCHUMPETER_1911维也纳风暴核心试听包", build_audition_schumpeter),
        ("E001_一潭死水的循环流转_为什么多造一万辆马车也变不出火车_完整广播剧台本", build_e001_circular_flow_vs_railway),
        ("E002_五种新组合_谁才是真正的企业家而不是守摊经理_完整广播剧台本", build_e002_five_new_combinations),
        ("E003_银行家是创新的产婆_为什么没本钱的疯子能掀翻巨头_完整广播剧台本", build_e003_banker_midwife_of_innovation),
        ("E004_创造性破坏的阵痛_马车夫的眼泪与全社会的新生_完整广播剧台本", build_e004_creative_destruction_pains),
        ("E005_为什么经济总像过山车_创新集群如何制造繁荣与萧条_完整广播剧台本", build_e005_swarms_boom_and_bust),
        ("E006_企业家的三股野心与1950预言_成功为何反倒容易杀死创新_完整广播剧台本", build_e006_three_ambitions_and_1950_prophecy),
    ]

    total_cues = 0
    total_chars = 0
    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        ep_chars = 0
        roles_seen: set[str] = set()
        for c in cs.cues:
            if c.kind == "dialogue":
                roles_seen.add(c.role_id)
                if c.acoustic_space not in PROJECT_ALLOWED_ACOUSTIC_SPACES:
                    raise SystemExit(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r}; "
                        f"allowed={sorted(PROJECT_ALLOWED_ACOUSTIC_SPACES)}"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                max_len = max(max_len, n_cjk)
                if n_cjk > 88:
                    raise SystemExit(
                        f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88): {spoken}"
                    )
            elif c.kind == "sfx":
                if not c.sfx_prompt.strip().endswith(", pure foley, no human voice"):
                    raise SystemExit(f"[{c.cue_id}] SFX prompt missing pure foley suffix: {c.sfx_prompt!r}")

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")

        if cs.episode_id == "AUDITION_SCHUMPETER":
            if len(roles_seen) != 8:
                raise SystemExit(f"[{cs.episode_id}] Audition pack must feature all 8 roles (got {sorted(roles_seen)})")
        else:
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Spoken CJK chars {ep_chars} out of strict target range [2800, 3050]"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] Pure-foley SFX count {sfx_n} out of strict target range [7, 10]"
                )

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"✅ [{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字 | 登场角色 {len(roles_seen)}/8)"
        )

    print(
        f"\n🎉 《1911维也纳风暴：〈经济发展理论〉创新剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
