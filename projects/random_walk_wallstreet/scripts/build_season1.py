#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《华尔街脱口秀：〈漫步华尔街〉指数革命》.

Usage:
    PYTHONPATH=src python3 projects/random_walk_wallstreet/scripts/build_season1.py
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
    build_audition_randomwalk,
    build_e001_dartboard_vs_wallstreet,
    build_e002_firm_foundation_vs_castle,
    build_e003_kline_chart_myth,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_star_manager_fee_trap,
    build_e005_modern_portfolio_index_revolution,
    build_e006_ordinary_lazy_guide_finale,
)

PROJECT_DIR = REPO_ROOT / "projects" / "random_walk_wallstreet"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "random_walk_wallstreet":
        raise SystemExit(f"Expected registry.domain='random_walk_wallstreet', got {registry.domain!r}")
    for motif_id, m in registry.sonic_motifs.items():
        if m.cached_file != "":
            raise SystemExit(f"SonicMotif {motif_id!r} must have cached_file='', got {m.cached_file!r}")
        if not m.sfx_prompt.endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif {motif_id!r} prompt must end with ', pure foley, no human voice'")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_RANDOMWALK_华尔街脱口秀核心试听包", build_audition_randomwalk),
        ("E001_蒙眼猩猩扔飞镖_为什么华尔街大师跑不赢大盘_完整广播剧台本", build_e001_dartboard_vs_wallstreet),
        ("E002_坚实基础与空中楼阁_股票究竟值多少钱的两大门派_完整广播剧台本", build_e002_firm_foundation_vs_castle),
        ("E003_K线图真的能算命吗_拆穿技术分析与股评神棍_完整广播剧台本", build_e003_kline_chart_myth),
        ("E004_明星基金经理的秘密_高管理费如何悄悄吃掉一半复利_完整广播剧台本", build_e004_star_manager_fee_trap),
        ("E005_别把鸡蛋放进同一篮子_现代投资组合与低费率指数革命_完整广播剧台本", build_e005_modern_portfolio_index_revolution),
        ("E006_普通人的终极懒人指南_省下时间过好生活才是赢家_完整广播剧台本", build_e006_ordinary_lazy_guide_finale),
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
        f"\n🎉 《华尔街脱口秀：〈漫步华尔街〉指数革命》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"\n   总计：{total_cues} 轨 / {total_chars} 字；"
        f"正片 E001–E006：{ep_total_cues} 轨（对白 {ep_total_dlg} | 拟音 {ep_total_sfx}）/ {ep_total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
