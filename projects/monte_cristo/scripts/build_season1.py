#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《基督山伯爵·伊夫堡复仇广播剧》.

Usage:
    PYTHONPATH=src python3 projects/monte_cristo/scripts/build_season1.py
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
    build_audition_monte_cristo,
    build_e001_betrothal_betrayal,
    build_e002_chateau_dif_faria,
    build_e003_island_treasure_return,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_paris_mask_haydee,
    build_e005_poison_court_bankruptcy,
    build_e006_roman_feast_wait_hope,
)

PROJECT_DIR = REPO_ROOT / "projects" / "monte_cristo"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_MONTE_CRISTO_伊夫堡复仇核心声线试听包", build_audition_monte_cristo),
        ("E001_订婚夜的黑信_马赛港法老号与伊夫堡铁门_完整广播剧台本", build_e001_betrothal_betrayal),
        ("E002_十四年石墙暗道_法利亚神父与装尸袋跃海_完整广播剧台本", build_e002_chateau_dif_faria),
        ("E003_荒岛黄金与幽灵归来_水手辛巴达与巴黎暗棋_完整广播剧台本", build_e003_island_treasure_return),
        ("E004_巴黎假面盛宴_奥特伊毒屋与海黛公主血证_完整广播剧台本", build_e004_paris_mask_haydee),
        ("E005_玫瑰毒影与金融风暴_维尔福崩塌与唐格拉尔破产_完整广播剧台本", build_e005_poison_court_bankruptcy),
        ("E006_罗马地窟天价烤鸡与尾声_等待和希望_完整广播剧台本", build_e006_roman_feast_wait_hope),
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
        for c in cs.cues:
            if c.kind == "dialogue":
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                max_len = max(max_len, n_cjk)
                if n_cjk > 105:
                    raise SystemExit(f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > 105)")

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")
        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"✅ [{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 口播 {ep_chars} 字 | 单句最长 {max_len} 字)"
        )

    print(
        f"\n🎉 《基督山伯爵·伊夫堡复仇广播剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
