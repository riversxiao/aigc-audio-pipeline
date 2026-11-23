#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《激励侦探局：〈魔鬼经济学〉隐秘动机剧》.

Usage:
    PYTHONPATH=src python3 projects/freakonomics_theater/scripts/build_season1.py
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
    build_audition_freak,
    build_e001_daycare_fine,
    build_e002_broker_incentives,
    build_e003_cheating_fingerprints,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_correlation_causation,
    build_e005_cobra_effect,
    build_e006_seven_hidden_motives,
)

PROJECT_DIR = REPO_ROOT / "projects" / "freakonomics_theater"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "freakonomics_theater":
        raise SystemExit(f"Unexpected registry domain={registry.domain!r}; expected 'freakonomics_theater'")
    for motif_id, motif_spec in registry.sonic_motifs.items():
        if motif_spec.cached_file != "":
            raise SystemExit(f"SonicMotif {motif_id!r} must have cached_file='', got {motif_spec.cached_file!r}")
        if not motif_spec.sfx_prompt.endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif {motif_id!r} sfx_prompt must end with ', pure foley, no human voice'")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_FREAK_激励侦探局核心试听包", build_audition_freak),
        ("E001_越罚越迟到的幼儿园_经济激励如何杀掉道德愧疚_完整广播剧台本", build_e001_daycare_fine),
        ("E002_为什么中介卖自家房总多卖好几天_信息差与委托代理_完整广播剧台本", build_e002_broker_incentives),
        ("E003_数据里的作弊指纹_当考核变成唯一目标时会发生什么_完整广播剧台本", build_e003_cheating_fingerprints),
        ("E004_冰淇淋销量越高溺水越多_拆穿因果与相关的致命陷阱_完整广播剧台本", build_e004_correlation_causation),
        ("E005_眼镜蛇悬赏反而养出更多蛇_激励设计的反噬奇案_完整广播剧台本", build_e005_cobra_effect),
        ("E006_把激励侦探的放大镜带回家_识破生活里七大隐秘动机_完整广播剧台本", build_e006_seven_hidden_motives),
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
        if cs.episode_id != "AUDITION_FREAK":
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
        f"\n🎉 《激励侦探局：〈魔鬼经济学〉隐秘动机剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
