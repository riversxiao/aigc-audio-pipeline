#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《国运的开关：〈为什么国家会失败〉制度史剧》.

Usage:
    PYTHONPATH=src python3 projects/why_nations_fail/scripts/build_season1.py
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
    build_audition_nations,
    build_e001_border_town_cliff,
    build_e002_inclusive_vs_extractive,
    build_e003_stocking_frame_creative_destruction,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_venice_rise_and_closure,
    build_e005_1688_critical_juncture,
    build_e006_institutional_inertia_and_breakthrough,
)

PROJECT_DIR = REPO_ROOT / "projects" / "why_nations_fail"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "why_nations_fail":
        raise SystemExit(f"Registry domain must be 'why_nations_fail', got {registry.domain!r}")
    for mid, mspec in registry.sonic_motifs.items():
        if mspec.cached_file != "":
            raise SystemExit(f"SonicMotif {mid!r} must have cached_file='', got {mspec.cached_file!r}")
        if not mspec.sfx_prompt.endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif {mid!r} sfx_prompt must end with ', pure foley, no human voice'")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_NATIONS_国运的开关核心试听包", build_audition_nations),
        ("E001_一墙之隔的贫富悬崖_为什么地理和气候解释不了国运_完整广播剧台本", build_e001_border_town_cliff),
        ("E002_把蛋糕做大还是抢蛋糕_包容性制度与汲取性制度_完整广播剧台本", build_e002_inclusive_vs_extractive),
        ("E003_为什么女王拒绝了织袜机_既得利益为何最怕创造性破坏_完整广播剧台本", build_e003_stocking_frame_creative_destruction),
        ("E004_威尼斯的兴盛与关门_从人人合伙出海到贵族锁死名册_完整广播剧台本", build_e004_venice_rise_and_closure),
        ("E005_1688关键节点_一场分权博弈如何点亮工业革命_完整广播剧台本", build_e005_1688_critical_juncture),
        ("E006_制度的惯性与破局_普通人如何读懂大国兴衰与个人选择_完整广播剧台本", build_e006_institutional_inertia_and_breakthrough),
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
        if cs.mode != "audition_pack":
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
        f"\n🎉 《国运的开关：〈为什么国家会失败〉制度史剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
