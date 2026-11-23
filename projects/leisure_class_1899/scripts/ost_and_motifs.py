"""Canonical 1899 Gilded Age Ironic Waltz & Parlor Chamber OST Palette & Sonic Motifs
for《1899镀金时代：〈有闲阶级论〉奢侈消费剧》.

All 5 canonical OST themes are strictly pure acoustic 1899 Gilded Age chamber music
(ironic salon waltz chamber strings, witty solo violin, parlor grand piano, expressive cello)
with NO modern drums, NO synth, NO Chinese instruments, and NO singing vocals — guaranteeing
100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

LEISURE_CLASS_1899_OST: dict[str, str] = {
    "gilded_ballroom_irony": (
        "Witty ironic 1899 Gilded Age New York salon waltz for chamber strings, playful solo violin, "
        "crisp parlor grand piano arpeggios and nimble pizzicato cello evoking ostentatious Fifth Avenue champagne galas, "
        "purely acoustic classical instrumental, no modern drums, no synth, no Chinese instruments, no singing, no vocals"
    ),
    "silver_spoon_parlor": (
        "Slyly satirical late-19th-century parlor chamber music, articulate parlor grand piano chords, "
        "wry expressive solo violin melodies and dry chamber cello counterpoint evoking gilded drawing-room snobbery and silver etiquette, "
        "purely acoustic instrumental, no modern drums, no synth, no Chinese instruments, no singing, no vocals"
    ),
    "fifth_avenue_carriage": (
        "Brisk cosmopolitan 1899 Gilded Age chamber underscore, lively rhythmic chamber strings, "
        "bright parlor grand piano pulse and spirited solo violin phrasing evoking Fifth Avenue carriages and bustling luxury windows, "
        "purely acoustic instrumental, no modern drums, no synth, no Chinese instruments, no singing, no vocals"
    ),
    "workshop_honest_rhythm": (
        "Warm grounded late-19th-century acoustic chamber theme, steady lyrical solo cello, "
        "honest warm parlor grand piano accompaniment and clear singing solo violin evoking true silversmith craftsmanship and practical utility, "
        "purely acoustic instrumental, no modern drums, no synth, no Chinese instruments, no singing, no vocals"
    ),
    "quiet_dignity_dusk": (
        "Tender reflective 1899 acoustic chamber epilogue, gentle lyrical solo violin over soft parlor grand piano nocturne chords "
        "and warm muted chamber strings evoking inner dignity, honest work, and quiet freedom from status anxiety at twilight, "
        "purely acoustic instrumental, no modern drums, no synth, no Chinese instruments, no singing, no vocals"
    ),
}

LEISURE_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "gilded_champagne_ballroom": {
        "name": "1899第五大道镀金宴会厅香槟碰杯",
        "description": "水晶吊灯轻颤、香槟木塞清脆拔开、细长水晶高脚杯轻碰与大理石舞厅轻柔脚步声",
        "sfx_prompt": (
            "Opulent 1899 New York Fifth Avenue gilded marble ballroom ambience with a crisp champagne cork pop, "
            "effervescent pouring, delicate crystal flutes clinking together, and light satin heels stepping across polished parquet, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "silver_spoon_workshop": {
        "name": "老工匠银器工坊手工敲击银勺",
        "description": "小银锤有节奏轻敲纯银勺坯清脆金属叮当声、细锉刀打磨与银勺轻落木台声",
        "sfx_prompt": (
            "Crisp intimate 1899 silversmith workshop foley with rhythmic light metal planishing hammer taps shaping a solid silver spoon "
            "on a small iron stake, gentle fine file brushing, and finished silver placed cleanly onto a warm oak bench, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "fifth_avenue_carriage_bells": {
        "name": "1899纽约第五大道马车石板路与黄铜车铃",
        "description": "四轮豪华马车铁蹄清脆踏过石板大街、马车皮弹簧微响与亮耳黄铜车铃叮当",
        "sfx_prompt": (
            "Bustling 1899 New York Fifth Avenue street ambience with rhythmic horse hooves trotting briskly over stone cobblestones, "
            "polished carriage wheels rolling, leather harness creaking, and a bright brass carriage bell ringing, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "corset_silk_boutique": {
        "name": "高级女装沙龙丝绸曳地与细高跟叩地",
        "description": "硬挺塔夫绸礼服摩挲沙沙声、紧身胸衣丝带抽拉系紧与细高跟鞋轻叩实木地板",
        "sfx_prompt": (
            "Close-up 1899 luxury dressmaker salon foley with heavy silk taffeta skirts rustling, "
            "taut corset lacing strings pulling snug through brass eyelets, and narrow high heels tapping crisply on polished hardwood floor, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "manicured_estate_shears": {
        "name": "纽波特豪门庄园齐整草坪大剪修剪声",
        "description": "园丁钢铁草坪大剪清脆咔嚓修整青草、手推滚筒割草机沙沙滚动与远方轻柔微风",
        "sfx_prompt": (
            "Crisp sunny 1899 Newport manor garden foley with sharp steel garden shears snipping lush grass blades neatly, "
            "a manual reel lawnmower whirring evenly over turf, and a gentle coastal breeze through manicured hedges, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "chicago_study_typewriter": {
        "name": "1899芝加哥大学书房机械打字机与稿纸",
        "description": "老式机械打字机清脆落键、回车清铃叮声与厚重书稿翻页沙沙作响",
        "sfx_prompt": (
            "Quiet wood-paneled 1899 Chicago university study ambience with crisp mechanical typewriter keys clacking steadily, "
            "a bright brass carriage return bell dinging, and thick cotton manuscript pages turning gently on an oak desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
