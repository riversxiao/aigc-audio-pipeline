"""Canonical 2008 Financial Thriller Acoustic Chamber OST Palette & Sonic Motifs
for《2008次贷暗战：〈大空头〉金融危机剧》.

All 5 canonical OST themes match `_ECON_FINANCE_BGM_PRESETS["big_short_2008"]`:
taut 2008 financial thriller low pulsing cello ostinato, moody upright bass and dark minimalist
felt piano — strictly purely acoustic instrumental, zero EDM beat, zero heavy rock drums,
zero singing/vocals, zero Chinese xianxia instruments — guaranteeing 100% SHA-256 stem-cache
reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

BIG_SHORT_2008_OST: dict[str, str] = {
    "midnight_spreadsheet_pulse": (
        "Taut 2008 financial thriller low pulsing cello ostinato, moody plucked upright double bass, "
        "sparse dark minimalist felt piano motifs and restrained tremolando chamber viola evoking a lone "
        "San Jose fund manager combing through subprime mortgage spreadsheets at 3 a.m., purely acoustic "
        "instrumental, no EDM beat, no heavy rock drums, no singing, no vocals"
    ),
    "florida_empty_suburb": (
        "Dry sun-bleached 2008 investigative financial thriller acoustic chamber score, wry plucked upright "
        "double bass groove, muted nylon acoustic guitar pulse, restless pizzicato cello and dark minimalist "
        "felt piano evoking vacant Florida housing developments and reckless subprime boom, purely acoustic "
        "instrumental, no EDM beat, no heavy rock drums, no singing, no vocals"
    ),
    "cdo_jenga_alchemy": (
        "Slick suspenseful 2008 Wall Street chamber thriller score, crisp staccato dark minimalist felt piano "
        "chords, insistent low pulsing cello ostinato, moody upright double bass and sharp bowed chamber strings "
        "evoking gleaming Manhattan trading floors stacking fragile triple-A CDO towers, purely acoustic "
        "instrumental, no EDM beat, no heavy rock drums, no singing, no vocals"
    ),
    "vegas_countdown_tension": (
        "High-stakes brooding 2008 financial crisis thriller chamber underscore, relentless low pulsing cello "
        "ostinato, ticking pizzicato upright bass, dark minimalist piano chords and tightening dissonant string "
        "harmonics evoking margin-call countdowns and Las Vegas securitization showdowns, purely acoustic "
        "instrumental, no EDM beat, no heavy rock drums, no singing, no vocals"
    ),
    "lehman_cold_dawn": (
        "Solemn austere 2008 Wall Street dawn chamber elegy, deeply expressive mournful solo cello over dark "
        "minimalist felt piano arpeggios, grounded upright double bass and hushed chamber strings slowly "
        "clearing into sober clarity, purely acoustic instrumental, no EDM beat, no heavy rock drums, "
        "no singing, no vocals"
    ),
}

BIG_SHORT_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "san_jose_rain_keyboard": {
        "name": "2005圣何塞午夜暴雨、键盘核账与打印机出纸",
        "description": "硅谷办公室深夜雨水敲打玻璃窗、机械键盘急促核对房贷表格与激光打印机吐出成叠明细纸",
        "sfx_prompt": (
            "Late-night 2005 San Jose office rain drumming softly on glass windows, rapid tactile mechanical "
            "keyboard typing on spreadsheets and a laser printer spitting out crisp mortgage ledger sheets, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "jenga_tower_collapse": {
        "name": "银行家绿罩台灯咔哒开启与积木高塔瞬间倾塌",
        "description": "老式黄铜拉链绿罩台灯在红木桌清脆点亮，木块积木抽动摩擦后整座高塔哗啦坍塌",
        "sfx_prompt": (
            "Brass pull-chain click of a green banker desk lamp on dark mahogany followed by dry wooden Jenga "
            "blocks scraping as one block slides out and the tall wooden tower clatters down in a sharp cascade, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "wall_street_trading_desk": {
        "name": "曼哈顿华尔街债券交易台电话、键盘与玻璃会议室门",
        "description": "纽约投行交易大厅直线电话听筒咔哒、急促敲击报价键盘、合同活页翻动与磨砂玻璃门沉重闭合",
        "sfx_prompt": (
            "Tense 2007 Manhattan Wall Street bond trading floor ambience with brisk desk-phone handset clicks, "
            "crisp keyboard keystrokes, rustling contract binders and a heavy frosted-glass boardroom door "
            "latching shut, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "florida_empty_house": {
        "name": "佛罗里达迈阿密空城燥风、锈锁铁牌与空屋脚步回声",
        "description": "烈日荒废别墅区棕榈叶沙沙作响、铁锁链轻敲待售铁牌、空荡未装修木地板脚步回响",
        "sfx_prompt": (
            "Hot quiet Florida empty suburban cul-de-sac wind rustling dry palm fronds, a rusted metal padlock "
            "clanking against a real-estate sign post and hollow footsteps echoing across an unfurnished wooden "
            "living room floor, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "vegas_casino_clink": {
        "name": "拉斯维加斯证券化狂欢夜冰块酒杯、筹码与地毯脚步",
        "description": "奢华酒店宴会厅水晶威士忌杯冰块轻碰、筹码敲击绒面桌沿与昂贵皮鞋踏过厚地毯",
        "sfx_prompt": (
            "Upscale Las Vegas hotel ballroom conference lounge foley with crystal ice clinking inside heavy "
            "whiskey tumblers, muted poker chips tapping softly on velvet tables and crisp dress shoes striding "
            "across carpeted floor, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "lehman_cardboard_dawn": {
        "name": "2008年9月雷曼清晨冷风、搬家纸箱胶带与玻璃旋转门",
        "description": "纽约曼哈顿秋晨冷风掠过高楼、瓦楞搬家纸箱封口胶带撕拉、电梯铜铃叮响与厚重玻璃旋转门缓缓转动",
        "sfx_prompt": (
            "Chilly September 2008 Manhattan dawn breeze outside a glass tower, crisp packing tape ripping across "
            "cardboard moving boxes, a quiet brass elevator bell dinging and a heavy glass revolving door turning "
            "slowly, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
