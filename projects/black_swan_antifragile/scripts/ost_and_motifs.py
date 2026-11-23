"""Canonical Mediterranean-Meets-Chamber Acoustic OST Palette & Sonic Motifs
for《感恩节火鸡警报：〈黑天鹅与反脆弱〉风险剧》.

All 5 canonical OST themes strictly match `_ECON_FINANCE_BGM_PRESETS["black_swan_antifragile"]`
(tense intellectual Mediterranean-meets-chamber cello drone, stark solo piano, suspenseful bowed strings,
and subtle acoustic oud/nylon accents — purely acoustic instrumental, zero pop drums, zero electronic synths,
zero singing/vocals, zero Chinese xianxia instruments), guaranteeing 100% SHA-256 stem-cache reuse across
all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

BLACK_SWAN_OST: dict[str, str] = {
    "mediterranean_storm_harbor": (
        "Tense intellectual Mediterranean-meets-chamber cello drone, stark lonely solo piano notes, "
        "subtle plucked acoustic oud and nylon guitar harmonic accents with suspenseful bowed strings "
        "evoking a moonlit storm-lit limestone harbor tavern overlooking dark waters, "
        "purely acoustic instrumental, no pop drums, no modern beat, no singing, no vocals"
    ),
    "bell_curve_risk_desk": (
        "Taut razor-sharp intellectual chamber suspense score, insistent pizzicato double bass ostinato, "
        "stark staccato solo piano intervals and tense bowed cello and viola pulse evoking a high-altitude "
        "Manhattan bank risk desk ticking toward a fat-tail crash, "
        "purely acoustic instrumental, no pop drums, no electronic synth, no singing, no vocals"
    ),
    "sunken_ship_archive": (
        "Solemn atmospheric Mediterranean maritime chamber elegy, deep sustained cello drone, "
        "sparse resonant solo piano chords and mournful bowed viola with faint acoustic nylon guitar echoes "
        "evoking centuries of silent shipwrecks beneath calm seas, "
        "purely acoustic instrumental, no pop drums, no percussion, no singing, no vocals"
    ),
    "barbell_iron_forge": (
        "Focused grounded Mediterranean-meets-chamber acoustic pulse, warm rhythmic acoustic oud and "
        "nylon guitar ostinato, firm resilient bowed cello melodies and crisp upright double bass evoking "
        "an old harbor stone oven, tempered iron barbell discipline and antifragile strength under stress, "
        "purely acoustic instrumental, no pop drums, no modern beat, no singing, no vocals"
    ),
    "stone_arch_clarity": (
        "Clear unsentimental Mediterranean twilight chamber epilogue, luminous stark solo piano arpeggios, "
        "warm sustained cello resonance and gentle acoustic nylon guitar harmonics evoking calm after a sea squall "
        "and hard-won skin-in-the-game wisdom, "
        "purely acoustic instrumental, no pop drums, no percussion, no singing, no vocals"
    ),
}

BLACK_SWAN_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "harbor_stone_storm": {
        "name": "地中海石屋拱窗夜浪与烛火轻摇",
        "description": "月夜暗浪沉重拍击海港石堤、海风低掠木百叶窗、粗木桌上长烛轻晃的悬疑海港室感",
        "sfx_prompt": (
            "Mediterranean limestone harbor tavern interior at night with dark sea waves lapping heavily "
            "against stone seawalls outside an arched window, soft wind howling faintly through wooden shutters "
            "and a tallow candle flame flickering quietly on a rough oak table, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "porcelain_vase_shatter": {
        "name": "薄胎瓷瓶坠地碎裂清响",
        "description": "精致薄壁瓷器从橡木桌面滑落，在石板地上干脆利落摔成清脆四散碎片的听觉冲击",
        "sfx_prompt": (
            "Crisp startling foley of a delicate thin-walled ceramic vase slipping off a hardwood table "
            "and shattering sharply into dozens of tinkling shards across a stone floor, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "trading_bell_alarm": {
        "name": "华尔街风控台强平警报与厚报表合拢",
        "description": "高楼交易大厅密集键盘敲击、急促电子追保警报提示音与厚重风控报告狠狠合上玻璃桌",
        "sfx_prompt": (
            "Tense high-floor trading desk ambience with rapid mechanical keyboard clatter, urgent subtle "
            "electronic margin-call alert chimes and thick risk-report binders slamming shut onto a glass desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "maritime_chart_brass": {
        "name": "百年海运沉船海图展开与黄铜圆规落纸",
        "description": "厚重羊皮纸航海图在桃花心木桌刷地摊开，黄铜罗盘与分规咔嗒一声精准落点",
        "sfx_prompt": (
            "Crisp heavy parchment nautical chart unrolling across a mahogany desk followed by a heavy brass "
            "marine compass and dividers clicking precisely onto aged paper, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "iron_barbell_clink": {
        "name": "石屋庭院铸铁杠铃片沉稳碰撞与落地",
        "description": "厚实铸铁杠铃片套上铁杆清脆碰响，随后稳稳顿落石板地面的扎实金属质感",
        "sfx_prompt": (
            "Heavy cast-iron barbell weight plates clinking crisply onto a steel bar followed by a solid "
            "grounded thud on a stone courtyard floor, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "stone_oven_hearth": {
        "name": "港口柴火石窑木炭噼啪与木铲出炉",
        "description": "海港老面包坊砖窑里硬木炭火温暖噼啪作响，长柄木铲划过热石底端出脆皮面包轻落木架",
        "sfx_prompt": (
            "Warm crackling hardwood embers inside an old Mediterranean stone bread oven as a long wooden "
            "baker peel slides smoothly across hearth stone and crisp crusty loaves tap lightly onto a rack, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
