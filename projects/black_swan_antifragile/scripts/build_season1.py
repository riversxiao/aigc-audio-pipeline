#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《感恩节火鸡警报：〈黑天鹅与反脆弱〉风险剧》.

Usage:
    PYTHONPATH=src python3 projects/black_swan_antifragile/scripts/build_season1.py
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
    build_audition_swan,
    build_e001_turkey_illusion,
    build_e002_mediocristan_extremistan,
    build_e003_silent_evidence_narrative,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_fragile_robust_antifragile,
    build_e005_barbell_nonlinearity,
    build_e006_skin_in_the_game,
)

PROJECT_DIR = REPO_ROOT / "projects" / "black_swan_antifragile"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "black_swan_antifragile":
        raise SystemExit(f"Expected registry domain='black_swan_antifragile', got {registry.domain!r}")

    anchor_cfg = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    if set(anchor_cfg.get("role_mappings", {}).keys()) != set(registry.roles.keys()):
        raise SystemExit("anchor_sources.json role_mappings keys do not match voice_casting_registry.json roles 1-to-1!")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_SWAN_感恩节火鸡警报核心试听包", build_audition_swan),
        ("E001_感恩节火鸡的千日幻觉_连涨一千天为何在最自信那天归零_完整广播剧台本", build_e001_turkey_illusion),
        ("E002_平均斯坦与极端斯坦_身高能算平均数为何财富与崩盘全是极端值_完整广播剧台本", build_e002_mediocristan_extremistan),
        ("E003_沉默证据与叙事谬误_活下来的大侠写回忆录沉在海底的船谁替它们说话_完整广播剧台本", build_e003_silent_evidence_narrative),
        ("E004_脆弱强韧与反脆弱_玻璃杯怕摔石头不怕摔什么越摔反而越强壮_完整广播剧台本", build_e004_fragile_robust_antifragile),
        ("E005_杠铃策略与非线性红利_九成极度保守配一成押注奇迹为何平庸中间派最危险_完整广播剧台本", build_e005_barbell_nonlinearity),
        ("E006_切身利益在局中_不坐自己修的桥不亏自己钱的专家凭什么替你拍板_完整广播剧台本", build_e006_skin_in_the_game),
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
        f"\n🎉 《感恩节火鸡警报：〈黑天鹅与反脆弱〉风险剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
