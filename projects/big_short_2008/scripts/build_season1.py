#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《2008次贷暗战：〈大空头〉金融危机剧》.

Usage:
    PYTHONPATH=src python3 projects/big_short_2008/scripts/build_season1.py
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
    build_audition_short,
    build_e001_unread_mortgage_ledger,
    build_e002_florida_ninja_boom,
    build_e003_aaa_cdo_alchemy,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_cds_fire_insurance,
    build_e005_rating_agency_vegas,
    build_e006_lehman_dawn_rules,
)

PROJECT_DIR = REPO_ROOT / "projects" / "big_short_2008"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
ANCHOR_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "anchor_sources.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ALLOWED_SPACES = frozenset({"dry", "vintage_study", "studio_warm", "vast_hall"})


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "big_short_2008":
        raise SystemExit(f"Expected registry domain='big_short_2008', got {registry.domain!r}")

    anchor_cfg = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    if set(anchor_cfg.get("role_mappings", {}).keys()) != set(registry.roles.keys()):
        raise SystemExit("anchor_sources.json role_mappings keys do not match voice_casting_registry.json roles 1-to-1!")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_SHORT_2008次贷暗战核心试听包", build_audition_short),
        ("E001_2005无人翻开的房贷明细_当全华尔街高喊房价永不跌谁在翻完借款名单_完整广播剧台本", build_e001_unread_mortgage_ledger),
        ("E002_脱衣舞娘五套房与零首付狂欢_佛罗里达空城暗访与忍者贷荒诞现场_完整广播剧台本", build_e002_florida_ninja_boom),
        ("E003_把垃圾债包装成3A级CDO魔术_过期鱼汤变海鲜与合成CDO套娃_完整广播剧台本", build_e003_aaa_cdo_alchemy),
        ("E004_发明信用违约互换CDS做空华尔街_替别人房子买火灾险的漫长煎熬_完整广播剧台本", build_e004_cds_fire_insurance),
        ("E005_评级机构与华尔街合谋装睡_付钱买3A旋转门与拉斯维加斯狂欢夜_完整广播剧台本", build_e005_rating_agency_vegas),
        ("E006_2008雷曼倒塌与普通人的防泡沫铁律_纸牌屋坍塌后的冰冷清晨_完整广播剧台本", build_e006_lehman_dawn_rules),
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
        f"\n🎉 《2008次贷暗战：〈大空头〉金融危机剧》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
