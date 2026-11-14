"""Curated 36-Track Pure Traditional Chinese Xianxia OST Palette for Chapters 41–120 (Worlds 2–7 & Finale).

Sharing canonical `bgm_prompt` strings across acts of the same Cognitive World and dramatic mood:
1. Establishes cohesive worldbuilding leitmotifs (just like a multi-season animation/drama OST album).
2. Enables automatic SHA-256 stem-cache reuse in `ACE-Step 1.5 XL`, cutting 80-episode BGM GPU time by ~85%.
"""

from __future__ import annotations

WORLD_OST: dict[str, str] = {
    # --- World 2: 永夜大胤 (Ch41-52, Eternal Night & Bone-Lamp Dynasty) ---
    "w2_eternal_night_tension": (
        "Dark atmospheric ancient Chinese xianxia chamber score, eerie xun ocarina and sparse cold guqin plucks "
        "over a deep bone-lamp cavern drone, eternal night tension, traditional Chinese instruments only, no drums, no vocals"
    ),
    "w2_ghost_market_stealth": (
        "Mysterious shadowy ancient Chinese stealth underscore, muted pipa pizzicato and low bamboo xiao breath "
        "in a subterranean bone-lantern market, suspenseful and restrained, no drums, no vocals"
    ),
    "w2_first_sunlight_catharsis": (
        "Deeply moving sacred Chinese xianxia dawn symphony, warm soaring bamboo xiao and radiant guzheng arpeggios "
        "breaking through four thousand years of darkness into golden morning light, purely instrumental, no drums, no vocals"
    ),
    # --- World 3: 无陆苦海 (Ch53-63, Landless Abyssal Sea & Father-Son Reunion) ---
    "w3_abyssal_sea_desolation": (
        "Vast desolate ancient Chinese ocean xianxia underscore, rolling deep erhu waves and lonely bamboo xiao flute "
        "over dark abyssal sub-bass resonance, endless black sea mood, no drums, no vocals"
    ),
    "w3_father_son_reunion": (
        "Profoundly emotional heroic Chinese xianxia chamber score, dignified low cello and warm guqin duet "
        "expressing unspoken father-and-son bond after years of separation, restrained solemn warmth, no drums, no vocals"
    ),
    "w3_sea_prison_rising_land": (
        "Monumental epic Chinese xianxia orchestral score with heavy taiko war drums, surging brass-like sheng "
        "and triumphant erhu as new continent rises from the bitter sea, purely instrumental, no vocals"
    ),
    # --- World 4: 白鹤画界 (Ch64-75, Two-Dimensional Painted Immortal Illusion & Frost Coffin Empress) ---
    "w4_painted_illusion_eeriness": (
        "Uncanny crystalline ancient Chinese silk-and-bamboo chamber music, delicate porcelain chimes and "
        "too-perfect guzheng harmonics hiding cold surveillance beneath an ink-wash immortal illusion, no drums, no vocals"
    ),
    "w4_frost_coffin_empress_awaken": (
        "Regal ancient Chinese xianxia empress theme, colossal bronze bell chime, icy jade guqin and solitary proud "
        "phoenix xiao melody echoing across three thousand years of frost, solemn and transcendent, no drums, no vocals"
    ),
    # --- World 5: 时间税界 (Ch76-83, Lifespan-Tax Empire & Yang-Spirit Ascension) ---
    "w5_lifespan_tax_oppression": (
        "Cold mechanical-feeling ancient Chinese bronze clockwork chime and taut bowed erhu ostinato over oppressive "
        "imperial drone, solemn tension of stolen centuries, traditional acoustic instruments, no drums, no vocals"
    ),
    "w5_yang_spirit_ascension": (
        "Transcendent golden Chinese xianxia breakthrough score, resonant temple bells, luminous guqin glissandos "
        "and soaring bamboo flute celebrating Yang-Spirit divine illumination, no drums, no vocals"
    ),
    # --- World 6: 万魂魔窟 & 五魂争壳 (Ch84-93, Soul-Splitting Abyss & Five-Soul Mind War) ---
    "w6_soul_abyss_dread": (
        "Sinister dark ambient Chinese xianxia score, ghostly xun clay flute, scraping bowed strings and deep "
        "abyssal bronze resonance inside an ancient soul-refining pit, ominous suspense, no drums, no vocals"
    ),
    "w6_five_souls_mind_duel": (
        "Intense psychological Chinese xianxia duel score, rapid razor-sharp pipa tremolos trading phrases with "
        "icy guqin strikes over a taut heartbeat-like low string drone, high mental tension, no vocals"
    ),
    # --- World 7: 罪血母界 (Ch94-105, Ancestral Sin-Blood Mother World & Fourth Gene-Lock) ---
    "w7_ancestral_wasteland_sorrow": (
        "Tragic ancient Chinese frontier elegy, mournful guanzi reed pipe and weathered mournful erhu over wind-swept "
        "red earth drone, ancient sacrifice and unyielding backbone, no drums, no vocals"
    ),
    "w7_empress_out_of_coffin_war": (
        "Blazing heroic Chinese xianxia dual-protagonist war anthem with thunderous battle percussion, fiery pipa, "
        "soaring phoenix flute and iron broadsword momentum cleaving the heavens, purely instrumental, no vocals"
    ),
    # --- Finale: 第五魂真容 & 原初牧神天宫终局 (Ch106-120, Failed-Timeline Self, Tai Yi & Grand Finale) ---
    "f1_fifth_soul_tragic_mirror": (
        "Hauntingly intimate ancient Chinese solo guqin and fragile weeping erhu in a frozen timeless void, "
        "quiet tragic resolve of meeting one's own failed-timeline soul, no drums, no vocals"
    ),
    "f2_tomb_guardian_firewood": (
        "Sacred solemn Chinese xianxia farewell hymn, warm low xun ocarina and ascending guzheng notes like "
        "sparks of an eternal torch passed to the next generation, deeply poignant, no drums, no vocals"
    ),
    "f3_celestial_palace_confrontation": (
        "Colossal cosmic Chinese xianxia divine throne-room score, ancient ritual bianzhong bronze bells, "
        "vast cold starry drone and immovable philosophical tension, no drums, no vocals"
    ),
    "f4_final_battle_slay_taiyi": (
        "Ultimate heaven-shattering Chinese xianxia grand finale boss battle score with pounding taiko war drums, "
        "furious pipa, blazing suona-and-strings tutti and unstoppable mortal willpower, purely instrumental, no vocals"
    ),
    "f5_epilogue_new_year_horizon": (
        "Peaceful timeless ancient Chinese pastoral epilogue, warm hearthside guqin, gentle bamboo flute and "
        "serene horizon strings evoking mortal spring festival wine and a lone sabre walking toward infinite worlds, no drums, no vocals"
    ),
    # --- Cross-World Shared Dramatic Archetypes ---
    "shared_xujie_shattered_realm": (
        "Vast ancient cosmic xianxia dark ambient score, colossal bronze bell resonance, desolate sub-bass drone "
        "and eerie high crystalline frost textures inside a shattered mental realm, no drums, no vocals"
    ),
    "shared_tactical_ambush_kill": (
        "Fierce razor-edged Chinese xianxia combat score with driving battle drums, aggressive fast pipa strumming "
        "and lethal sabre-clash tension, purely instrumental, no vocals"
    ),
    "shared_boss_overwhelming_pressure": (
        "Ominous overwhelming Chinese xianxia high-realm pressure underscore, crushing sub-bass bronze gong resonance "
        "and taut trembling erhu harmonics before a life-or-death strike, no drums, no vocals"
    ),
    "shared_calm_aftermath_planning": (
        "Restrained contemplative ancient Chinese guqin and soft xiao chamber music in a quiet lamp-lit room, "
        "calm deduction and careful preparation, no drums, no vocals"
    ),
}
