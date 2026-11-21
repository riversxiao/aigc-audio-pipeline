"""Canonical 1944 Wartime Cambridge Chamber OST Palette & Sonic Motifs for《1944剑桥夜话：〈通往奴役之路〉思想剧场》.

Sharing canonical `bgm_prompt` strings across acts across all Season-1 episodes:
1. Crafts a warm, lucid, gripping 1944 BBC historical intellectual-drama atmosphere
   (wartime Cambridge wood-paneled study, rain on Gothic windows, restrained British chamber strings,
   warm felt piano, solo cello reflection).
2. Guarantees 100% SHA-256 stem-cache reuse in `ACE-Step 1.5 XL` on Colab 96GB G4 with strictly
   zero modern pop drums or vocals.
"""

from __future__ import annotations

HAYEK_1944_OST: dict[str, str] = {
    # Act 1: 1944 Wartime Cambridge Rain & Midnight Fire-Watch Reflection
    "cambridge_wartime_study": (
        "Warm poignant 1944 British historical drama chamber score, restrained solo cello melody, "
        "soft muted upright felt piano chords and gentle string quartet sustain in a quiet rain-washed Cambridge college study, "
        "thoughtful intellectual gravity, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    # Act 2: Lively Economic Debate & Everyday Market Hustle Metaphors
    "london_market_pulse_strings": (
        "Crisp engaging British documentary chamber underscore, rhythmic pizzicato strings, "
        "articulate warm acoustic piano and light woodwind clarinet dialogue evoking lively ideas and everyday trade, "
        "clear intellectual momentum, purely instrumental, no heavy drums, no singing, no vocals"
    ),
    # Act 3: Warning & Moral Tension (Slippery slope, Rule of Law vs Arbitrary Discretion)
    "warning_crossroads_cello": (
        "Tense solemn historical drama underscore, brooding low chamber cello ostinato, "
        "sparse serious piano chords and subtle dark viola harmony conveying historical warning and philosophical depth, "
        "purely acoustic instrumental, no drums, no synth, no singing, no vocals"
    ),
    # Act 4: Atlantic Liner Letter (Hayek vs Keynes 1944) & Lucid Epilogue
    "atlantic_letter_epilogue": (
        "Luminous dignified British period-drama epilogue underscore, expressive warm piano, "
        "lyrical solo violin and rich reassuring chamber strings fading into serene reflection on liberty and responsibility, "
        "purely acoustic instrumental, no drums, no singing, no vocals"
    ),
}

HAYEK_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "cambridge_fireplace_rain": {
        "name": "1944剑桥雨夜壁炉与远钟",
        "description": "剑桥学院木质书房壁炉柴火轻响，窗外细雨轻叩彩绘玻璃（全剧夜间夜话定场母题）",
        "sfx_prompt": (
            "Cozy subtle wood fireplace crackle inside a quiet vintage wooden university study while soft steady evening rain "
            "taps gently against leaded glass windows, distant muted college clock chime, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
    "wartime_radio_dial": {
        "name": "1944老式真空管收音机调频声",
        "description": "老式木壳真空管收音机旋钮调台时的柔和静电滋啦声（用于切入1944历史背景与战时新闻）",
        "sfx_prompt": (
            "Vintage 1940s wooden vacuum-tube tabletop radio tuning knob turning slowly across brief warm shortwave static "
            "before clicking cleanly off in a quiet study, pure foley, no human voice"
        ),
        "duration_seconds": 2.4,
    },
    "porcelain_teacup_study": {
        "name": "剑桥书房骨瓷红茶杯轻放声",
        "description": "红茶倒入骨瓷杯并轻轻放回瓷碟的清脆生活声响（圆桌辩论转折气口）",
        "sfx_prompt": (
            "Hot tea pouring briefly into a delicate bone china teacup followed by the cup settling softly onto its saucer "
            "on a mahogany table in a quiet room, pure foley, no human voice"
        ),
        "duration_seconds": 2.2,
    },
    "chalk_blackboard_debate": {
        "name": "讲堂粉笔划黑板与纸页翻动",
        "description": "伦敦经济学院讲堂粉笔利落画线与厚手稿翻页声（推导经济学直觉比喻时触发）",
        "sfx_prompt": (
            "Crisp wooden lecture hall chalk drawing a sharp dividing line on a slate blackboard followed by heavy paper "
            "manuscript pages turning briskly, pure foley, no human voice"
        ),
        "duration_seconds": 2.4,
    },
    "atlantic_liner_horn": {
        "name": "大西洋邮轮低沉离港汽笛",
        "description": "1944年夏凯恩斯赴美参加布雷顿森林会议所乘邮轮在海雾中的低沉汽笛与海风声",
        "sfx_prompt": (
            "Distant dignified low steam horn of a 1940s transatlantic ocean liner sounding once across gentle open Atlantic swells "
            "and cool sea breeze, historical documentary foley, no human voice"
        ),
        "duration_seconds": 3.4,
    },
}
