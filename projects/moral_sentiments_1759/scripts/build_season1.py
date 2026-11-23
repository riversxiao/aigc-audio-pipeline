#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1759格拉斯哥灯火：〈道德情操论〉商业温度》.

Usage:
    PYTHONPATH=src python3 projects/moral_sentiments_1759/scripts/build_season1.py
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
from drama_helpers import ALLOWED_MORAL_ACOUSTIC_SPACES  # noqa: E402
from ep01_03_scripts import (  # noqa: E402
    build_audition_moral,
    build_e001_sympathy_other_half,
    build_e002_impartial_spectator,
    build_e003_poor_mans_son,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_corruption_of_sentiments,
    build_e005_justice_pillar_trust,
    build_e006_true_dignity_epilogue,
)

PROJECT_DIR = REPO_ROOT / "projects" / "moral_sentiments_1759"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_MORAL_1759格拉斯哥灯火核心试听包", build_audition_moral, False),
        ("E001_人天生会替别人疼_同情共情与〈国富论〉的另一半灵魂_完整广播剧台本", build_e001_sympathy_other_half, True),
        ("E002_心里住着一位公正旁观者_良知是如何驯服情绪的_完整广播剧台本", build_e002_impartial_spectator, True),
        ("E003_穷人之子的幻觉_为什么追逐名利常常买不到快乐_完整广播剧台本", build_e003_poor_mans_son, True),
        ("E004_崇富轻贫的致命毒药_斯密晚年最痛心的一章_完整广播剧台本", build_e004_corruption_of_sentiments, True),
        ("E005_正义是支柱仁爱是装饰_为什么商业信任离不开底线_完整广播剧台本", build_e005_justice_pillar_trust, True),
        ("E006_真正的体面_既想被爱更配得上被爱的人生智慧_完整广播剧台本", build_e006_true_dignity_epilogue, True),
    ]

    total_cues = 0
    total_chars = 0
    for stem, fn, is_full_ep in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        ep_chars = 0
        sfx_n = 0
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in ALLOWED_MORAL_ACOUSTIC_SPACES:
                    raise SystemExit(
                        f"[{c.cue_id}] Disallowed acoustic_space={c.acoustic_space!r}; "
                        f"allowed={sorted(ALLOWED_MORAL_ACOUSTIC_SPACES)}"
                    )
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                max_len = max(max_len, n_cjk)
                if n_cjk > 88:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88): {spoken}")
            elif c.kind == "sfx":
                sfx_n += 1
                if not c.sfx_prompt.strip().endswith(", pure foley, no human voice"):
                    raise SystemExit(f"[{c.cue_id}] SFX prompt missing pure foley suffix: {c.sfx_prompt!r}")

        if is_full_ep:
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Full episode CJK char count {ep_chars} out of required range [2800, 3050]!"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] Full episode SFX count {sfx_n} out of required range [7, 10]!"
                )

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"✅ [{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字)"
        )

    print(
        f"\n🎉 《1759格拉斯哥灯火：〈道德情操论〉商业温度》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
