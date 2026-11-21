"""Canonical Midnight Chinese Folklore OST Palette & Sonic Motifs for《聊斋志异·午夜悬疑广播剧场》.

Sharing canonical `bgm_prompt` strings across acts across all Season-1 episodes:
1. Establishes a dark, poetic, spine-tingling midnight Chinese supernatural cinema atmosphere
   (guqin, low xiao flute, mournful erhu, temple bronze bell, rain-soaked courtyard stillness).
2. Guarantees 100% SHA-256 stem-cache reuse in `ACE-Step 1.5 XL` on Colab 96GB G4, cutting
   multi-episode BGM generation time by >80% while strictly forbidding modern beats or vocals.
"""

from __future__ import annotations

LIAOZHAI_MIDNIGHT_OST: dict[str, str] = {
    # Act 1 / Cold Open: Eerie midnight lantern suspense, quiet drizzle, low guqin & breathy xiao flute
    "midnight_lantern_suspense": (
        "Dark eerie traditional Chinese classical instrumental underscore for midnight ghost folklore, "
        "sparse low guqin harmonics, haunting breathy bamboo xiao flute sustained notes, distant soft temple woodblock, "
        "chilling misty courtyard silence, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    # Enchanting / Bewitching: Silky eerie pipa & melancholic erhu (Painted Skin allure, Nie Xiaoqian candlelight)
    "fox_spirit_silk_melancholy": (
        "Hauntingly beautiful traditional Chinese classical chamber music, delicate gossamer pipa arpeggios, "
        "mournful silk-string erhu solo and soft guzheng shimmer under pale moonlight, seductive yet tragic ghost tale mood, "
        "purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    # Terror / Climax: Tense low bronze bell drone, bowed low erhu & urgent plucked pipa (Demon reveal, Corpse chase)
    "ghost_climax_dread_strings": (
        "Suspenseful dark ancient Chinese horror film score, ominous deep bronze temple bell drone, "
        "tremolo low erhu bowing, sharp urgent pipa stabs and tense guqin bass plucks building dread, "
        "cinematic supernatural climax, traditional Chinese instruments only, no pop beat, no singing, no vocals"
    ),
    # Daoist / Swordsman Heroics: Crisp heroic guqin, resonant bronze chimes & fierce bamboo flute (Yan Chixia, Judge Lu)
    "swordsman_exorcism_heroic": (
        "Dramatic traditional Chinese wuxia supernatural instrumental underscore, crisp commanding guqin strums, "
        "bold low bamboo dizi flute phrases, resonant ancient bronze chimes and restrained frame drum accents, "
        "righteous exorcist tension, purely instrumental, no modern synth, no singing, no vocals"
    ),
    # Whimsical / Satirical Daoist Folklore (Laoshan Taoist moon-cutting & comedic misstep)
    "laoshan_mystic_whimsy": (
        "Playful mystical traditional Chinese classical chamber instrumental, lively light guzheng plucks, "
        "airy bamboo flute melody and gentle wooden percussion, mountain Daoist folklore wonder and subtle irony, "
        "purely acoustic instrumental, no modern beat, no singing, no vocals"
    ),
    # Underworld Majesty & Solemn Fate Epilogue (City God Examination, Karma Aftermath)
    "underworld_karma_solemn": (
        "Solemn atmospheric traditional Chinese classical instrumental epilogue, resonant deep temple bell, "
        "stately mournful guqin and warm restrained solo xiao flute fading into midnight mist, "
        "poetic karma reflection and quiet goosebumps, purely instrumental, no drums, no singing, no vocals"
    ),
}

LIAOZHAI_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "night_watch_clapper": {
        "name": "三更打更梆子与铜锣",
        "description": "深夜空巷里由远及近的竹梆子敲击与一声低沉铜锣余韵（《午夜聊斋》全季标志性开篇与转夜锚点）",
        "sfx_prompt": (
            "Traditional ancient Chinese night watchman hollow bamboo clapper struck three slow times "
            "followed by one distant low brass gong shimmer echoing down a wet cobblestone alley in midnight mist, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.4,
    },
    "creaking_wooden_door": {
        "name": "古宅腐木门吱呀推开",
        "description": "潮湿破败木门在死寂深夜缓缓推开的刺耳木轴摩擦声",
        "sfx_prompt": (
            "Slow eerie creaking of an old damp wooden Chinese courtyard door swinging open on dry wooden hinges "
            "in dead midnight silence, subtle cold draft wind, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "paper_window_tear": {
        "name": "湿润窗纸悄然捅破声",
        "description": "书斋窗纸被指尖湿润后轻轻捅破的脆薄撕裂声（《画皮》核心名场面锚点）",
        "sfx_prompt": (
            "Delicate close-up foley of a dampened thin traditional mulberry paper window screen being poked "
            "and slowly torn open by a fingertip in a dead silent midnight courtyard, pure foley, no human voice"
        ),
        "duration_seconds": 2.0,
    },
    "ghostly_wind_chimes": {
        "name": "荒寺夜雨与阴风铁马铃",
        "description": "破败古刹檐下阴风骤起，铜铃乱响夹杂细密夜雨声",
        "sfx_prompt": (
            "Sudden chilly midnight gust rattling rusty bronze wind chimes under an abandoned temple eave "
            "amid steady pattering rain on old clay tiles, eerie atmosphere, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
    "sword_unsheathe_thunder": {
        "name": "古剑破空出鞘与惊雷",
        "description": "斩妖除魔长剑铿然出鞘，剑鸣穿云夹杂沉闷滚雷",
        "sfx_prompt": (
            "Sharp metallic ringing unsheathe of an ancient steel Chinese sword slicing through midnight air "
            "accompanied by a sudden cracking distant thunderclap, cinematic foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "temple_bell_midnight": {
        "name": "子夜古寺幽深铜钟",
        "description": "一声浑厚苍凉的古寺大铜钟在雾夜中缓缓散开（收尾与阴司场景母题）",
        "sfx_prompt": (
            "Single deep resonant strike of an ancient bronze temple bell ringing out slowly into a cold misty midnight valley, "
            "long natural metallic decay, pure foley, no human voice"
        ),
        "duration_seconds": 3.8,
    },
}
