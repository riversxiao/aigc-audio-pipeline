#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1899镀金时代：〈有闲阶级论〉奢侈消费剧》.

Usage:
    PYTHONPATH=src python3 projects/leisure_class_1899/scripts/build_season1.py
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
    build_audition_leisure,
    build_e001_conspicuous_leisure,
    build_e002_veblen_effect_consumption,
    build_e003_silver_spoon_waste_aesthetics,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_corsets_heels_fashion_obsolescence,
    build_e005_vicarious_consumption_status_anxiety,
    build_e006_instinct_of_workmanship_inner_dignity,
)

PROJECT_DIR = REPO_ROOT / "projects" / "leisure_class_1899"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    for motif_id, m in registry.sonic_motifs.items():
        if m.cached_file != "":
            raise SystemExit(f"[registry] SonicMotif {motif_id!r} must use cached_file='' (got {m.cached_file!r})")
        if not m.sfx_prompt.strip().endswith(", pure foley, no human voice"):
            raise SystemExit(f"[registry] SonicMotif {motif_id!r} missing pure-foley suffix: {m.sfx_prompt!r}")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_LEISURE_1899镀金时代核心试听包", build_audition_leisure),
        ("E001_不干活才体面_有闲阶级如何发明了炫耀性闲暇_完整广播剧台本", build_e001_conspicuous_leisure),
        ("E002_越贵越抢的密码_炫耀性消费与凡勃伦效应_完整广播剧台本", build_e002_veblen_effect_consumption),
        ("E003_为什么手工银勺比机器造贵十倍_浪费美学与品味骗局_完整广播剧台本", build_e003_silver_spoon_waste_aesthetics),
        ("E004_束腰高跟鞋与流行换季_时尚为什么故意让你穿得不舒服_完整广播剧台本", build_e004_corsets_heels_fashion_obsolescence),
        ("E005_代理人消费与鄙视链_为什么中产永远觉得钱不够花_完整广播剧台本", build_e005_vicarious_consumption_status_anxiety),
        ("E006_找回工匠本能_如何在消费主义时代守住内心体面_完整广播剧台本", build_e006_instinct_of_workmanship_inner_dignity),
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

        if cs.episode_id == "AUDITION_LEISURE":
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
        f"\n🎉 《1899镀金时代：〈有闲阶级论〉奢侈消费剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
