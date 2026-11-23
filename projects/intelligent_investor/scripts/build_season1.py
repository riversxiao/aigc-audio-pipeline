#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《哥伦比亚价值课堂：〈聪明的投资者〉》.

Usage:
    PYTHONPATH=src python3 projects/intelligent_investor/scripts/build_season1.py
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
    build_audition_investor,
    build_e001_investing_vs_speculation,
    build_e002_mr_market_partner,
    build_e003_margin_of_safety_bridge,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_defensive_investor_blueprint,
    build_e005_cigar_butts_and_wonderful_businesses,
    build_e006_enemy_in_the_mirror_finale,
)

PROJECT_DIR = REPO_ROOT / "projects" / "intelligent_investor"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_INVESTOR_哥伦比亚价值课堂核心试听包", build_audition_investor),
        ("E001_投资还是赌博_格雷厄姆划下的第一道生死红线_完整广播剧台本", build_e001_investing_vs_speculation),
        ("E002_每天敲门的市场先生_情绪失控的合伙人该怎么用_完整广播剧台本", build_e002_mr_market_partner),
        ("E003_安全边际_为什么造承重十吨的桥要按三十吨设计_完整广播剧台本", build_e003_margin_of_safety_bridge),
        ("E004_防御型普通人怎么投_不盯盘跑赢九成高手的笨办法_完整广播剧台本", build_e004_defensive_investor_blueprint),
        ("E005_进取型烟蒂股与好生意_格雷厄姆与青年巴菲特的师徒对话_完整广播剧台本", build_e005_cigar_butts_and_wonderful_businesses),
        ("E006_投资的敌人就在镜子里_跨越百年的理性与品格课_完整广播剧台本", build_e006_enemy_in_the_mirror_finale),
    ]

    total_cues = 0
    total_chars = 0
    ep_total_cues = 0
    ep_total_dlg = 0
    ep_total_sfx = 0
    ep_total_chars = 0

    for stem, fn in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        max_cue_id = ""
        ep_chars = 0
        dlg_n = 0
        sfx_n = 0
        for c in cs.cues:
            if c.kind == "dialogue":
                dlg_n += 1
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
                    raise SystemExit(
                        f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 88): {spoken}"
                    )
            elif c.kind == "sfx":
                sfx_n += 1
                if not c.sfx_prompt.endswith(", pure foley, no human voice"):
                    raise SystemExit(
                        f"[{c.cue_id}] SFX prompt must end with ', pure foley, no human voice': {c.sfx_prompt!r}"
                    )

        if cs.mode != "audition_pack":
            if not (2800 <= ep_chars <= 3050):
                raise SystemExit(
                    f"[{cs.episode_id}] Spoken CJK chars {ep_chars} out of required range [2800, 3050]"
                )
            if not (7 <= sfx_n <= 10):
                raise SystemExit(
                    f"[{cs.episode_id}] SFX cue count {sfx_n} out of required range [7, 10]"
                )
            ep_total_cues += len(cs.cues)
            ep_total_dlg += dlg_n
            ep_total_sfx += sfx_n
            ep_total_chars += ep_chars

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
        f"\n🎉 《哥伦比亚价值课堂：〈聪明的投资者〉》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"\n   总计：{total_cues} 轨 / {total_chars} 字；"
        f"正片 E001–E006：{ep_total_cues} 轨（对白 {ep_total_dlg} | 拟音 {ep_total_sfx}）/ {ep_total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
