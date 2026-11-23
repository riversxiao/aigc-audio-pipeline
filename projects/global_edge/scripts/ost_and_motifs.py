"""Canonical OST prompts (ACE-Step 1.5 XL) and Sonic Motifs (MOSS-SoundEffect-v2.0) for Global Edge.

Every prompt string and motif parameter in this module is locked verbatim against:
- `projects/global_edge/00_节目圣经与第一季24集总纲/SHOW_BIBLE.md` (§6.2)
- `projects/global_edge/00_节目圣经与第一季24集总纲/voice_casting_registry.json` (`sonic_motifs`)

Never alter prompt punctuation or word order — SHA-256 stem caches in the Colab 96GB studio
rely on exact byte parity across E001_VA/VB/VC/VD and Season 1 episodes E001–E024.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigc_audio_pipeline.models import VoiceCastingRegistry

# ---------------------------------------------------------------------------
# 5 Canonical HBO Minimalist Instrumental OST Prompts (ACE-Step 1.5 XL)
# Verbatim from SHOW_BIBLE.md §6.2
# ---------------------------------------------------------------------------

GLOBAL_EDGE_OST_PROMPTS: dict[str, str] = {
    "ost_boardroom_cold_open": (
        "Minimalist HBO prestige corporate drama underscore, taut muted solo cello ostinato "
        "over sparse dark felt piano chords and subtle low upright bass pulse, cold glass-tower "
        "tension, restrained chamber strings, strictly no vocals, no singing, no pop drums, "
        "no trap beats, no traditional Chinese instruments, no guzheng, purely instrumental"
    ),
    "ost_valuation_escalation": (
        "Sophisticated modern financial thriller score inspired by minimalist chamber strings "
        "and restrained analog ticking pulse, crisp staccato viola rhythm with cool piano "
        "arpeggios building quiet executive pressure, no loud brass fanfare, no EDM drops, "
        "no vocals, no singing, no traditional Asian instruments, purely instrumental"
    ),
    "ost_shenzhen_midnight_lab": (
        "Intimate late-night tech founder underscore, warm muted Rhodes electric piano and "
        "subtle low cello harmonics with ultra-clean minimal ambient pad, focused midnight "
        "engineering tension in a quiet glass lab, no percussion, no vocals, no singing, "
        "no guqin, purely instrumental"
    ),
    "ost_endgame_counterstrike": (
        "Dignified modern prestige drama climax underscore, resolute low strings swelling with "
        "clean grand piano octaves and crisp understated timpani pulse, triumphant yet ice-cool "
        "executive composure, no cheesy pop rock, no choir, no vocals, no singing, no erhu, "
        "purely instrumental"
    ),
    "ost_blackbook_debrief": (
        "Ultra-clean minimalist modern executive podcast bed, soft sparse muted acoustic bass "
        "pluck and warm understated felt piano chords at slow steady pulse, spacious midrange "
        "leaving total clarity for spoken voice and shadowing pauses, no drums, no melody solo, "
        "no vocals, no singing, purely instrumental"
    ),
}

# Gains calibrated strictly within SHOW_BIBLE.md §6.2 bounds:
# bgm_gain_speech in [0.06, 0.08], bgm_gain_gap in [0.24, 0.30], bgm_duration_s = 60.0
GLOBAL_EDGE_OST_SPECS: dict[str, dict[str, Any]] = {
    "ost_boardroom_cold_open": {
        "bgm_prompt": GLOBAL_EDGE_OST_PROMPTS["ost_boardroom_cold_open"],
        "bgm_duration_s": 60.0,
        "bgm_gain_speech": 0.07,
        "bgm_gain_gap": 0.28,
    },
    "ost_valuation_escalation": {
        "bgm_prompt": GLOBAL_EDGE_OST_PROMPTS["ost_valuation_escalation"],
        "bgm_duration_s": 60.0,
        "bgm_gain_speech": 0.075,
        "bgm_gain_gap": 0.29,
    },
    "ost_shenzhen_midnight_lab": {
        "bgm_prompt": GLOBAL_EDGE_OST_PROMPTS["ost_shenzhen_midnight_lab"],
        "bgm_duration_s": 60.0,
        "bgm_gain_speech": 0.065,
        "bgm_gain_gap": 0.25,
    },
    "ost_endgame_counterstrike": {
        "bgm_prompt": GLOBAL_EDGE_OST_PROMPTS["ost_endgame_counterstrike"],
        "bgm_duration_s": 60.0,
        "bgm_gain_speech": 0.08,
        "bgm_gain_gap": 0.30,
    },
    "ost_blackbook_debrief": {
        "bgm_prompt": GLOBAL_EDGE_OST_PROMPTS["ost_blackbook_debrief"],
        "bgm_duration_s": 60.0,
        "bgm_gain_speech": 0.06,
        "bgm_gain_gap": 0.24,
    },
}

# ---------------------------------------------------------------------------
# 7 Canonical Sonic Motifs (MOSS-SoundEffect-v2.0)
# Verbatim from voice_casting_registry.json
# ---------------------------------------------------------------------------

GLOBAL_EDGE_SONIC_MOTIFS: dict[str, dict[str, Any]] = {
    "glass_boardroom_door": {
        "name": "沙丘路玻璃会议室门液压闭锁声",
        "sfx_prompt": (
            "Heavy frameless tempered glass boardroom door swinging shut with a muted "
            "brushed-steel hydraulic latch click inside a quiet Sand Hill Road office suite, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.2,
        "prompt_influence": 0.6,
        "loop": False,
    },
    "smart_glasses_haptic_ping": {
        "name": "NovaEdge Glass 镜腿触控微震与光学提示音",
        "sfx_prompt": (
            "Crisp minimalist titanium smart-glasses temple haptic tap followed by a subtle "
            "ultra-clean low-latency micro-chime and soft optical shutter pulse in close stereo "
            "proximity, pure foley, no human voice"
        ),
        "duration_seconds": 1.4,
        "prompt_influence": 0.62,
        "loop": False,
    },
    "shenzhen_smt_factory_line": {
        "name": "深圳南山 SMT 无尘产线精密贴片声",
        "sfx_prompt": (
            "Precision high-speed surface-mount pick-and-place robotics humming rhythmically "
            "beside soft pneumatic air valves and optical inspection conveyor clicks inside a "
            "Shenzhen electronics cleanroom, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
        "prompt_influence": 0.6,
        "loop": False,
    },
    "transpacific_call_connect": {
        "name": "跨太平洋三时区加密会议连线声",
        "sfx_prompt": (
            "Crisp executive smartphone conference bridge dial chime clicking cleanly into a "
            "quiet transpacific encrypted telecom line hum across an empty midnight desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 1.8,
        "prompt_influence": 0.65,
        "loop": False,
    },
    "paper_term_sheet_slide": {
        "name": "胡桃木长桌条款清单推滑与钢笔合盖声",
        "sfx_prompt": (
            "Thick bound term-sheet dossier sliding briskly across a polished walnut conference "
            "table followed by a solid fountain pen cap snapping shut on heavyweight cardstock, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 1.9,
        "prompt_influence": 0.6,
        "loop": False,
    },
    "freeze_frame_sub_drop": {
        "name": "《纸牌屋》式冻帧潜台词低频收束声",
        "sfx_prompt": (
            "Subtle cinematic low-frequency sub-bass tension swell tightening smoothly into "
            "sudden vacuum room stillness like an editorial focus snap, pure foley, no human voice"
        ),
        "duration_seconds": 1.2,
        "prompt_influence": 0.62,
        "loop": False,
    },
    "nyse_bell_and_ticker_pulse": {
        "name": "交易所开市铜钟与精密金融节拍声",
        "sfx_prompt": (
            "Resonant brass financial exchange opening bell ringing crisply once over subtle "
            "precision mechanical stopwatch ticks and distant trading desk keyboard taps, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
        "prompt_influence": 0.6,
        "loop": False,
    },
}


def verify_sync_with_bible_and_registry(
    registry: VoiceCastingRegistry,
    show_bible_path: Path,
) -> list[str]:
    """Return a list of drift errors between this module, SHOW_BIBLE.md, and voice_casting_registry.json."""
    errors: list[str] = []

    if not show_bible_path.exists():
        errors.append(f"SHOW_BIBLE.md not found at {show_bible_path}")
    else:
        bible_text = show_bible_path.read_text(encoding="utf-8")
        for ost_key, prompt in GLOBAL_EDGE_OST_PROMPTS.items():
            if ost_key not in bible_text:
                errors.append(f"OST key {ost_key!r} missing from {show_bible_path.name}")
            if prompt not in bible_text:
                errors.append(
                    f"OST prompt for {ost_key!r} is NOT byte-verbatim in {show_bible_path.name}"
                )
            spec = GLOBAL_EDGE_OST_SPECS.get(ost_key)
            if not spec:
                errors.append(f"Missing GLOBAL_EDGE_OST_SPECS entry for {ost_key!r}")
                continue
            if spec["bgm_prompt"] != prompt:
                errors.append(f"OST spec prompt mismatch for {ost_key!r}")
            if not (0.06 <= float(spec["bgm_gain_speech"]) <= 0.08):
                errors.append(
                    f"{ost_key}: bgm_gain_speech={spec['bgm_gain_speech']} outside [0.06, 0.08]"
                )
            if not (0.24 <= float(spec["bgm_gain_gap"]) <= 0.30):
                errors.append(
                    f"{ost_key}: bgm_gain_gap={spec['bgm_gain_gap']} outside [0.24, 0.30]"
                )

    reg_keys = set(registry.sonic_motifs.keys())
    mod_keys = set(GLOBAL_EDGE_SONIC_MOTIFS.keys())
    if reg_keys != mod_keys:
        errors.append(
            f"Sonic motif key mismatch: registry={sorted(reg_keys)} vs module={sorted(mod_keys)}"
        )

    for motif_id in sorted(reg_keys & mod_keys):
        reg_m = registry.sonic_motifs[motif_id]
        mod_m = GLOBAL_EDGE_SONIC_MOTIFS[motif_id]
        if reg_m.sfx_prompt != mod_m["sfx_prompt"]:
            errors.append(f"Motif {motif_id!r} sfx_prompt drifted from registry")
        if abs(float(reg_m.duration_seconds) - float(mod_m["duration_seconds"])) > 1e-6:
            errors.append(
                f"Motif {motif_id!r} duration_seconds={mod_m['duration_seconds']} != registry {reg_m.duration_seconds}"
            )
        if abs(float(reg_m.prompt_influence) - float(mod_m["prompt_influence"])) > 1e-6:
            errors.append(
                f"Motif {motif_id!r} prompt_influence={mod_m['prompt_influence']} != registry {reg_m.prompt_influence}"
            )
        if bool(reg_m.loop) != bool(mod_m["loop"]):
            errors.append(
                f"Motif {motif_id!r} loop={mod_m['loop']} != registry {reg_m.loop}"
            )

    return errors
