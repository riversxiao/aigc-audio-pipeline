"""Canonical 18th-Century Scottish Enlightenment Chamber OST Palette & Sonic Motifs for《1776爱丁堡夜话：〈国富论〉商业思想剧场》.

All 5 canonical OST themes are strictly pure acoustic 18th-century chamber music (warm baroque strings,
expressive solo cello, delicate harpsichord, classical nylon acoustic guitar, gentle Scottish chamber flute)
with zero modern pop beats, zero drums, and zero singing vocals — guaranteeing 100% SHA-256 stem-cache
reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

WEALTH_OF_NATIONS_OST: dict[str, str] = {
    "edinburgh_hearth_enlightenment": (
        "Warm intimate 18th-century Scottish Enlightenment chamber music, lyrical solo cello, "
        "gentle classical baroque harpsichord arpeggios and warm acoustic strings evoking a candlelit Edinburgh parlor debate, "
        "purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "glasgow_workshop_vigor": (
        "Lively bright 18th-century baroque chamber strings and plucked acoustic nylon guitar, "
        "crisp rhythmic pizzicato cello pulse evoking bustling Glasgow workshops, craftsmanship and rising commerce, "
        "purely instrumental chamber music, no modern drums, no pop beat, no singing, no vocals"
    ),
    "market_ledger_debate": (
        "Smart inquisitive 18th-century baroque intellectual chamber underscore, playful crisp harpsichord, "
        "articulate pizzicato strings and thoughtful solo oboe lines evoking lively commercial debate and clear logic, "
        "purely instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "monopoly_trade_storm": (
        "Tense dramatic 18th-century minor-key baroque orchestral chamber score, driving low cello ostinato, "
        "sharp bowed strings and urgent harpsichord chords evoking mercantilist trade wars, monopoly and financial bubbles, "
        "purely instrumental, no drums, no modern synth, no singing, no vocals"
    ),
    "north_sea_farewell_warmth": (
        "Profound tender 18th-century Scottish chamber epilogue, warm expressive solo cello melody, "
        "soft gentle classical acoustic strings and delicate wooden flute breath evoking lifelong friendship and humane commerce, "
        "purely acoustic instrumental, no drums, no singing, no vocals"
    ),
}

WEALTH_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "edinburgh_tavern_hearth": {
        "name": "1776爱丁堡牡蛎俱乐部炉火与锡杯",
        "description": "苏格兰雨夜木屋壁炉劈啪暖火、两只锡制啤酒杯轻碰与老式木椅轻响",
        "sfx_prompt": (
            "Warm cozy 18th-century Edinburgh wooden tavern parlor ambience with crackling stone hearth fire, "
            "two pewter mugs gently clinking on an oak table, and soft distant evening rain on leaded glass, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "pin_factory_clatter": {
        "name": "格拉斯哥扣针作坊清脆打针流水声",
        "description": "十八道工序流水线节奏明快的拉丝、截铜、轻锤安帽与成把黄铜扣针哗啦落入木盘",
        "sfx_prompt": (
            "Brisk rhythmic 18th-century brass pin-making workshop foley with crisp wire snipping, light precise miniature hammer taps, "
            "and hundreds of tiny gleaming brass pins cascading into a wooden sorting tray, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
    "brass_balance_coins": {
        "name": "黄铜天平称量金银币清响",
        "description": "老式黄铜砝码轻落秤盘与清脆金银币叮当计数声（商品交换与货币锚点）",
        "sfx_prompt": (
            "Crisp close-up foley of an antique brass balance scale swaying gently as gleaming silver shillings and gold sovereign coins "
            "clink onto the brass pan and wooden merchant counter, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "watt_steam_workshop": {
        "name": "瓦特大学工坊蒸汽机铜阀嘶鸣",
        "description": "早年实验蒸汽机铜制活塞沉稳往复、蒸汽微喷嘶鸣与精密铜齿轮咔嗒声",
        "sfx_prompt": (
            "18th-century experimental brass steam engine model pulsing steadily in a stone university workshop "
            "with crisp rhythmic steam hiss, clinking brass valves, and turning flywheel gears, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "merchant_port_harbor": {
        "name": "格拉斯哥与伦敦商港帆船卸货号角",
        "description": "大西洋贸易商船帆索吱呀、木吊机卸下茶叶与烟草货箱及海鸥拍浪声",
        "sfx_prompt": (
            "Bustling 18th-century British merchant harbor ambience with lapping sea waves, wooden sailing ship masts creaking, "
            "heavy pulley hoisting wooden tea crates onto cobblestone quay, and distant seagulls, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
    "quill_printing_press": {
        "name": "鹅毛笔书稿与1776木质印刷机压印",
        "description": "清脆鹅毛笔落纸划动与伦敦印刷作坊沉稳合压出刚印好的《国富论》初版书页",
        "sfx_prompt": (
            "Crisp quill pen writing across thick rag paper followed by the warm mechanical clunk and smooth rolling slide "
            "of an 18th-century wooden hand printing press pulling a fresh printed book sheet, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
