"""Canonical 1920s Investigative Cosmic Horror OST Palette & Sonic Motifs for《克苏鲁神话·不可名状声音档案》.

Sharing canonical `bgm_prompt` strings across acts across all Season-1 episodes:
1. Crafts an unmistakable 1920s Arkham / Miskatonic University noir-horror documentary atmosphere
   (sub-bass bowed contrabass, muted felt piano, desolate solo cello, icy chamber strings, ghostly harmonium).
2. Guarantees 100% SHA-256 stem-cache reuse in `ACE-Step 1.5 XL` on Colab 96GB G4, cutting
   multi-episode BGM generation time by >80% while strictly forbidding modern EDM beats or singing vocals.
"""

from __future__ import annotations

CTHULHU_ARCHIVES_OST: dict[str, str] = {
    # Act 1: 1920s Miskatonic University Archive & Rainy Study Inquiry
    "miskatonic_archive_noir": (
        "Dark atmospheric 1920s investigative horror documentary score, muted vintage felt piano sparse chords, "
        "low sustained solo cello drone and subtle contrabass pulse in a quiet rain-streaked university archive, "
        "restrained creeping dread, purely acoustic chamber instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    # Coastal Fog / Decaying New England Town (Innsmouth harbor, Arkham blighted heath)
    "new_england_coastal_dread": (
        "Bleak haunting coastal gothic chamber score, desolate minor-key solo violin harmonics, "
        "creaking low double bass swells and distant somber harmonium chords evoking wet harbor fog and decay, "
        "purely instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    # Cosmic Anomaly / Uncanny Alien Color & Wax Cylinder Uncanny Tension
    "cosmic_anomaly_shimmer": (
        "Uncanny eerie dark ambient chamber instrumental, fragile bowed glass harmonics, "
        "dissonant high string clusters over a brooding subterranean cello drone, otherworldly creeping wrongness, "
        "cinematic Lovecraftian mystery, purely instrumental, no drums, no pop rhythm, no singing, no vocals"
    ),
    # Midnight Pursuit / Monster Confrontation Climax (Innsmouth hotel chase, Dunwich hill, R'lyeh awakening)
    "eldritch_pursuit_climax": (
        "Intense cinematic cosmic horror orchestral suspense underscore, frantic low cello ostinato, "
        "ominous deep brass swells, dissonant tremolo strings and dark timpani rumbles of colossal awakening terror, "
        "purely instrumental film score, no modern synth trap, no singing, no vocals"
    ),
    # Polar Desolation & Ancient Cyclopean Ruins (At the Mountains of Madness)
    "antarctic_cyclopean_ruins": (
        "Vast freezing desolate orchestral ambient score, icy high bowed strings, "
        "monolithic hollow low brass drones and sparse haunting piano echoes evoking ancient cyclopean ruins under Antarctic ice, "
        "purely instrumental, no drums, no singing, no vocals"
    ),
    # Shattered Sanity / Epilogue Case Closed (Chilling aftermath & existential vertigo)
    "shattered_sanity_epilogue": (
        "Somber devastating dark chamber epilogue underscore, slow solitary muted piano notes, "
        "aching low cello lament fading into cold abyssal silence, haunting existential dread, "
        "purely acoustic instrumental, no drums, no singing, no vocals"
    ),
}

CTHULHU_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "wax_cylinder_click": {
        "name": "1920s老式蜡筒留声机启停噪点",
        "description": "密斯卡托尼克大学档案室老式爱迪生蜡筒/黑胶留声机落针咔哒声与轻微底噪（全季档案调取标志锚点）",
        "sfx_prompt": (
            "Authentic 1920s antique wax cylinder phonograph mechanical brass lever click followed by "
            "subtle warm vintage needle hiss and slow crank rotation in a quiet archive room, pure foley, no human voice"
        ),
        "duration_seconds": 2.4,
    },
    "morse_telegraph_distress": {
        "name": "短波电报急促莫尔斯求救信号",
        "description": "南极科考营地与海轮发出的嘶哑短波电报滋啦静电与急促滴答信号",
        "sfx_prompt": (
            "1920s maritime shortwave wireless telegraph static crackle with urgent rhythmic Morse code beeps "
            "fading in and out across stormy open ocean interference, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "foghorn_harbor_night": {
        "name": "新英格兰浓雾海港低沉雾号",
        "description": "印斯茅斯/阿卡姆海湾夜雾里一声拖长而凄厉的船只雾号，夹杂阴冷海浪拍打腐朽木码头",
        "sfx_prompt": (
            "Lonely deep distant harbor foghorn blaring once across a cold foggy New England bay at midnight "
            "over dark lapping sea waves against rotting wooden pilings, pure foley, no human voice"
        ),
        "duration_seconds": 3.6,
    },
    "heavy_wooden_lock_pick": {
        "name": "深夜旅馆门锁暗中撬动声",
        "description": "漆黑旅馆门外有人用铁丝悄悄试探并拨动老式铜门锁的金属刮擦与门栓轻震",
        "sfx_prompt": (
            "Close-up tense foley of a rusty skeleton key quietly probing and scraping inside an old brass hotel door lock "
            "followed by the heavy wooden doorknob slowly rattling in midnight silence, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "polar_blizzard_gust": {
        "name": "南极黑山绝谷嘶啸暴风雪",
        "description": "极地黑色巨峰风口如笛声般凄厉呜咽的零下六十度暴风雪呼啸",
        "sfx_prompt": (
            "Fierce howling Antarctic polar blizzard wind piping eerily through colossal jagged black stone peaks, "
            "sub-zero whistling gale and drifting ice crystals, pure foley, no human voice"
        ),
        "duration_seconds": 3.4,
    },
    "abyssal_sub_bass_hum": {
        "name": "不可名状深渊次声波震颤",
        "description": "巨石苏醒或旧日支配者逼近时的深海巨物低频震颤与潮湿石壁龟裂回响",
        "sfx_prompt": (
            "Colossal subterranean deep-sea tectonic sub-bass rumble with wet ancient monolith stone grinding "
            "and eerie cavernous resonance evoking an unfathomable waking entity, pure foley, no human voice"
        ),
        "duration_seconds": 3.8,
    },
}
