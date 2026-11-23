"""Canonical 1850 Parisian Salon Satirical Chamber OST Palette & Sonic Motifs for《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》.

All 5 canonical OST themes are strictly pure acoustic 1850 Parisian salon chamber music (witty chamber
string quartet, crisp pizzicato cello, light expressive fortepiano, agile classical woodwinds) with
zero modern drums, zero pop beats, zero vocals, and zero Chinese instruments — guaranteeing 100%
SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

BASTIAT_UNSEEN_OST: dict[str, str] = {
    "paris_salon_wit": (
        "Sparkling witty 1850 Parisian salon chamber string quartet, crisp playful pizzicato cello pulse, "
        "light articulated classical fortepiano arpeggios and nimble violin phrasing evoking lively French intellectual satire, "
        "purely acoustic chamber instrumental, no modern drums, no pop beat, no singing, no vocals, no Chinese instruments"
    ),
    "broken_window_alley": (
        "Lively cheeky 1850 Paris cobblestone street chamber vignette, sprightly pizzicato cello walking bass, "
        "crisp staccato string quartet and bright dainty fortepiano chords evoking bustling Parisian neighborhood comedy and sharp logic, "
        "purely acoustic instrumental, no modern drums, no pop beat, no singing, no vocals, no Chinese instruments"
    ),
    "parliament_satire_march": (
        "Mock-pompous satirical 1850 French parliamentary chamber scherzo, dry witty pizzicato cello march, "
        "crisp mischievous violin accents, light fortepiano flourishes and cheeky classical bassoon cadence evoking absurd political rhetoric, "
        "purely acoustic instrumental, no modern drums, no military snare, no singing, no vocals, no Chinese instruments"
    ),
    "candle_makers_petition": (
        "Comically theatrical 1850 Parisian courtroom satire chamber piece, melodramatic minor-to-major string quartet turns, "
        "crisp bounding pizzicato cello and sparkling humorous fortepiano runs evoking the absurd Candlemakers Petition against the Sun, "
        "purely acoustic instrumental, no modern drums, no pop beat, no singing, no vocals, no Chinese instruments"
    ),
    "seine_evening_clarity": (
        "Poignant luminous 1850 Parisian evening chamber epilogue, warm expressive solo cello melody, "
        "gentle lyrical string quartet harmonies and soft delicate fortepiano chords evoking quiet wisdom, truth and farewell along the Seine, "
        "purely acoustic instrumental, no modern drums, no synth, no singing, no vocals, no Chinese instruments"
    ),
}

BASTIAT_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "paris_cafe_salon": {
        "name": "1850巴黎左岸沙龙瓷杯与马车",
        "description": "巴黎左岸咖啡沙龙清脆白瓷杯碰碟、银匙轻搅与窗外石板路马车远行声",
        "sfx_prompt": (
            "Crisp 1850 Parisian cafe salon ambience with porcelain coffee cup resting lightly on saucer, "
            "delicate silver spoon clinking once, and distant horse carriage wheels rolling over cobblestone street outside, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "broken_shop_window": {
        "name": "老博诺姆面包铺六法郎破窗清脆碎裂",
        "description": "顽童抛石击中临街大玻璃窗，清脆哗啦炸裂与玻璃碴叮当滚落石阶（破窗谬误锚点）",
        "sfx_prompt": (
            "Sudden crisp impact of a small tossed stone shattering a large 1850 storefront glass window pane cleanly "
            "with glittering glass shards tinkling onto a cobblestone sidewalk, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "parliament_gavel_hall": {
        "name": "1850巴黎国民议会大厅木槌三击",
        "description": "高耸大理石议会厅回声中，厚重橡木议长槌干脆连敲三下与硬木桌翻阅法案纸页声",
        "sfx_prompt": (
            "Resonant grand 1850 stone assembly hall acoustics with three crisp authoritative wooden chairman gavel strikes "
            "on an oak podium followed by thick legislative parchment pages rustling, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "candle_wax_petition": {
        "name": "蜡烛作坊融蜡与《控告太阳》火漆印章",
        "description": "铜锅蜡液微沸轻响、鹅毛笔沙沙签署请愿书与沉稳红火漆啪地落印声",
        "sfx_prompt": (
            "Close-up 1850 tallow candle workshop foley with gentle sizzling molten wax, brisk quill pen scratching firmly "
            "across heavy petition parchment, and a brass wax seal stamping decisively onto red sealing wax, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "rail_track_pickaxe": {
        "name": "波尔多负铁路铁轨铿锵与铁镐拆轨",
        "description": "十九世纪蒸汽列车气笛远鸣，紧接着铁镐当啷猛砸钢轨木枕故意拆路声",
        "sfx_prompt": (
            "1850 European railway construction foley with distant iron steam locomotive whistle fading into sharp rhythmic "
            "iron pickaxe strikes clanging against steel rail tracks and wooden sleepers on gravel, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "seine_quill_clock": {
        "name": "塞纳河晚风、法式座钟与绝笔鹅毛笔",
        "description": "沉稳古典法式铜钟嘀嗒声、微风拂过窗帘与鹅毛笔沙沙写下《看得见的与看不见的》",
        "sfx_prompt": (
            "Quiet 1850 Parisian study evening ambience with steady delicate antique French mantel clock ticking, "
            "crisp quill pen scratching thoughtfully across rag paper, and soft breeze rustling window drapes, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
