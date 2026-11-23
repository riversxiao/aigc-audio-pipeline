"""Canonical Manhattan Acoustic Jazz-Chamber OST Palette & Sonic Motifs
for《华尔街脱口秀：〈漫步华尔街〉指数革命》.

All 5 canonical OST themes are strictly pure-acoustic Manhattan jazz-chamber piano trio
(warm felt upright piano, walking upright double bass, light fingerpicked/strummed acoustic guitar;
NO loud drums, NO electronic beats, NO vocals, NO Chinese instruments) — guaranteeing 100%
SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

RANDOM_WALK_OST: dict[str, str] = {
    "manhattan_walk_swing": (
        "Breezy witty Manhattan acoustic jazz piano trio, warm felt upright piano swing voicings, "
        "buoyant walking upright double bass and light fingerpicked acoustic guitar evoking an evening "
        "Wall Street talk-show salon and relaxed strolls through Lower Manhattan, purely acoustic "
        "instrumental, no loud drums, no percussion, no singing, no vocals"
    ),
    "castle_in_air_bubble": (
        "Sparkling whimsical Manhattan acoustic chamber-jazz piano trio, playful staccato felt piano "
        "arpeggios, nimble plucked upright double bass and jaunty crisp acoustic guitar flourishes "
        "evoking frothy market manias, tulip bulbs and floating castles in the air, purely acoustic "
        "instrumental, no loud drums, no percussion, no singing, no vocals"
    ),
    "dartboard_salon_wit": (
        "Crisp cheeky Manhattan late-night salon acoustic jazz piano trio, witty syncopated upright "
        "piano riffs, warm agile walking upright bass and buoyant light acoustic guitar rhythm evoking "
        "playful intellectual comedy, coin-flip experiments and dartboard wagers, purely acoustic "
        "instrumental, no loud drums, no percussion, no singing, no vocals"
    ),
    "wall_street_fee_clash": (
        "Taut articulate Manhattan debate chamber-jazz piano trio, insistent walking upright double bass "
        "ostinato, crisp rhythmic felt piano chords and tight muted acoustic guitar pulse evoking "
        "sharp Wall Street fee showdowns and lively cross-examination, purely acoustic instrumental, "
        "no loud drums, no percussion, no singing, no vocals"
    ),
    "index_freedom_sunset": (
        "Warm luminous Manhattan Hudson River sunset acoustic jazz-chamber epilogue, unhurried lyrical "
        "felt piano melodies, gentle arpeggiated acoustic guitar and deep glowing upright double bass "
        "evoking quiet compounding peace of mind and reclaimed life freedom, purely acoustic "
        "instrumental, no loud drums, no percussion, no singing, no vocals"
    ),
}

RANDOM_WALK_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "wall_street_salon_rain": {
        "name": "曼哈顿下城演播沙龙夜雨与桌牌",
        "description": "细雨轻敲华尔街拱窗玻璃、厚重玻璃水杯轻落橡木桌与演播室提词卡轻刷整理",
        "sfx_prompt": (
            "Warm intimate Manhattan lower Wall Street salon ambience with light evening rain tapping "
            "tall arched glass windows, a heavy glass tumbler gently set onto polished oak, and crisp "
            "index cards tapped neatly on a studio table, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "dartboard_thud_toss": {
        "name": "黄铜飞镖破空钉入软木镖盘",
        "description": "三支黄铜配重飞镖接连轻啸飞出，笃笃笃干脆利落地扎进厚实软木飞镖盘靶心",
        "sfx_prompt": (
            "Close-up studio foley of three weighted brass darts whistling briefly through quiet room air "
            "and landing one by one with crisp solid thuds into a tightly packed sisal cork dartboard, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "coin_flip_clink": {
        "name": "银元硬币弹起清鸣与木桌旋落",
        "description": "拇指清脆弹出厚重银币发出叮当金属余韵，在实木演播桌上高速旋转后嗒然落平",
        "sfx_prompt": (
            "Crisp metallic ring of a heavy silver coin flicked cleanly into the air, landing on a solid "
            "oak studio desk where it spins rapidly with diminishing clatter before settling flat, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "chart_ruler_scratch": {
        "name": "塑料直尺与自动铅笔沙沙画K线",
        "description": "透明直尺在方格图纸上轻滑定位，尖锐铅笔沙沙划出急促斜线并重重点出高点",
        "sfx_prompt": (
            "Close-up foley of a clear plastic drafting ruler sliding smoothly across crisp graph paper "
            "while a sharp pencil sketches brisk diagonal trendlines and circles chart peaks firmly, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "calculator_receipt_click": {
        "name": "会计师台式计算器急敲与纸带打印",
        "description": "老式台式会计计算器按键清脆连击，伴随纸带打印机咔嚓嚓吐出长条费率明细",
        "sfx_prompt": (
            "Tactile plastic keys of a vintage desktop accounting calculator clacking briskly followed by "
            "a rhythmic mechanical paper tape printer whirring and tearing off a crisp fee receipt strip, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "coffee_mug_pocket_watch": {
        "name": "黄铜怀表合盖咔嗒与深夜咖啡瓷杯",
        "description": "黄铜怀表清脆咔嗒合盖，旁边温热浓缩咖啡瓷杯轻放回木托盘的松弛夜话收尾声",
        "sfx_prompt": (
            "Refined mechanical snap of a brass pocket watch lid closing cleanly beside a warm ceramic "
            "espresso cup gently placed onto a wooden saucer in a calm evening studio lounge, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
}
