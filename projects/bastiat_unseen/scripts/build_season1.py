#!/usr/bin/env python3
"""Compile, validate & export Season 1 (Audition + E001–E006) for《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》.

Usage:
    PYTHONPATH=src python3 projects/bastiat_unseen/scripts/build_season1.py
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
from drama_helpers import ALLOWED_PROJECT_SPACES  # noqa: E402
from ep01_03_scripts import (  # noqa: E402
    build_audition_bastiat,
    build_e001_broken_window,
    build_e002_candlemakers_petition,
    build_e003_negative_railroad_machines,
)
from ep04_06_scripts import (  # noqa: E402
    build_e004_disbanding_troops_taxes,
    build_e005_thrift_vs_spendthrift,
    build_e006_state_fiction_rome_farewell,
)

PROJECT_DIR = REPO_ROOT / "projects" / "bastiat_unseen"
REGISTRY_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")

MAX_CUE_CJK = 88
MIN_EP_CJK = 2800
MAX_EP_CJK = 3050
MIN_EP_SFX = 7
MAX_EP_SFX = 10


def main() -> int:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    if registry.domain != "bastiat_unseen":
        raise SystemExit(f"Registry domain mismatch: {registry.domain!r} != 'bastiat_unseen'")
    for mid, m in registry.sonic_motifs.items():
        if m.cached_file != "":
            raise SystemExit(f"SonicMotif [{mid}] cached_file must be empty string, got {m.cached_file!r}")
        if not m.sfx_prompt.strip().endswith(", pure foley, no human voice"):
            raise SystemExit(f"SonicMotif [{mid}] missing pure foley suffix: {m.sfx_prompt!r}")

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    builders = [
        ("AUDITION_BASTIAT_1850巴黎讽刺剧核心试听包", build_audition_bastiat, True),
        ("E001_砸碎玻璃能救经济吗_史上最经典的破窗谬误_完整广播剧台本", build_e001_broken_window, False),
        ("E002_蜡烛匠控告太阳_史上最爆笑的关税保护请愿书_完整广播剧台本", build_e002_candlemakers_petition, False),
        ("E003_把铁路挖断能创就业吗_负铁路谬误与机器恐慌_完整广播剧台本", build_e003_negative_railroad_machines, False),
        ("E004_裁军与铁饭碗_政府养闲人为什么没增加总需求_完整广播剧台本", build_e004_disbanding_troops_taxes, False),
        ("E005_花钱如流水是恩人吗_浪子阔少与节俭人的暗账_完整广播剧台本", build_e005_thrift_vs_spendthrift, False),
        ("E006_国家是什么_每个人都想靠别人养活的宏大幻觉_完整广播剧台本", build_e006_state_fiction_rome_farewell, False),
    ]

    total_cues = 0
    total_chars = 0
    for stem, fn, is_audition in builders:
        cs = fn()
        errors = cs.validate(registry, require_locked_voices=True)
        if errors:
            raise SystemExit(f"Validation failed for {cs.episode_id}:\n" + "\n".join(errors))

        max_len = 0
        ep_chars = 0
        roles_seen: set[str] = set()
        for c in cs.cues:
            if c.kind == "dialogue":
                if c.acoustic_space not in ALLOWED_PROJECT_SPACES:
                    raise SystemExit(
                        f"[{c.cue_id}] Invalid acoustic_space={c.acoustic_space!r}; allowed={sorted(ALLOWED_PROJECT_SPACES)}"
                    )
                roles_seen.add(c.role_id)
                _, spoken = extract_tags_and_spoken_text(c.text)
                n_cjk = len(_CJK_RE.findall(spoken))
                ep_chars += n_cjk
                max_len = max(max_len, n_cjk)
                if n_cjk > MAX_CUE_CJK:
                    raise SystemExit(
                        f"[{c.cue_id}] Dialogue cue too long ({n_cjk} CJK chars > {MAX_CUE_CJK}): {spoken}"
                    )
            elif c.kind == "sfx":
                if not c.sfx_prompt.strip().endswith(", pure foley, no human voice"):
                    raise SystemExit(f"[{c.cue_id}] SFX prompt missing pure foley suffix: {c.sfx_prompt!r}")

        dlg_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")

        if is_audition:
            missing_roles = set(registry.roles.keys()) - roles_seen
            if missing_roles:
                raise SystemExit(f"[{cs.episode_id}] Audition pack missing roles: {sorted(missing_roles)}")
        else:
            if not (MIN_EP_CJK <= ep_chars <= MAX_EP_CJK):
                raise SystemExit(
                    f"[{cs.episode_id}] Episode CJK chars={ep_chars} out of required range [{MIN_EP_CJK}, {MAX_EP_CJK}]"
                )
            if not (MIN_EP_SFX <= sfx_n <= MAX_EP_SFX):
                raise SystemExit(
                    f"[{cs.episode_id}] Episode SFX count={sfx_n} out of required range [{MIN_EP_SFX}, {MAX_EP_SFX}]"
                )

        json_path = SCRIPTS_DIR / f"{stem}.json"
        md_path = SCRIPTS_DIR / f"{stem}.md"
        cs.save(json_path)
        write_cue_sheet_markdown(cs, md_path, registry=registry)

        total_cues += len(cs.cues)
        total_chars += ep_chars
        print(
            f"✅ [{cs.episode_id}] {cs.title} -> {len(cs.cues)} 轨 "
            f"(对白 {dlg_n} | 拟音 {sfx_n} | 角色 {len(roles_seen)}/8 | 口播 {ep_chars} 字 | 单句最长 {max_len} 字)"
        )

    print(
        f"\n🎉 《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》第一季全部 {len(builders)} 份台本编译校验通过！"
        f"总轨数 {total_cues}，总口播 {total_chars} 字。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
