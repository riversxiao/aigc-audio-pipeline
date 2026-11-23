"""Canonical 1911 Vienna Late-Romantic Chamber OST Palette & Sonic Motifs for《1911维也纳风暴：〈经济发展理论〉创新剧》.

All 5 canonical OST themes are strictly pure acoustic 1911 Vienna expressive romantic string quartet,
driving cello ostinato & grand piano (zero modern pop drums, zero vocals, zero Chinese instruments) —
guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

SCHUMPETER_1911_OST: dict[str, str] = {
    "vienna_cafe_spark": (
        "Warm sparkling 1911 Vienna expressive romantic string quartet and lively grand piano arpeggios, "
        "crisp lyrical violin dialogue over supple cello pulse evoking bright intellectual sparks in a candlelit Ringstrasse coffeehouse, "
        "purely acoustic chamber instrumental, no modern pop drums, no percussion kit, no vocals, no singing, no Chinese instruments"
    ),
    "horse_carriage_equilibrium": (
        "Measured classical 1911 Vienna romantic string quartet with steady gentle cello ostinato and warm resonant grand piano chords, "
        "graceful unhurried rhythmic cadence evoking the predictable circular flow of old horse-drawn Vienna workshops, "
        "purely acoustic chamber instrumental, no modern pop drums, no percussion kit, no vocals, no singing, no Chinese instruments"
    ),
    "creative_destruction_surge": (
        "Urgent sweeping 1911 Vienna expressive romantic string quartet, driving relentless cello ostinato and bold grand piano bass chords, "
        "passionate dramatic violin surges evoking creative destruction, industrial disruption and fierce clash against old guilds, "
        "purely acoustic chamber instrumental, no modern pop drums, no percussion kit, no vocals, no singing, no Chinese instruments"
    ),
    "bank_credit_ledger": (
        "Focused incisive 1911 Vienna chamber underscore, taut driving cello ostinato, articulate staccato grand piano phrases "
        "and poised muted string quartet tension evoking high-stakes bank credit ledgers, risk calculations and business cycles, "
        "purely acoustic chamber instrumental, no modern pop drums, no percussion kit, no vocals, no singing, no Chinese instruments"
    ),
    "danube_horizon_innovation": (
        "Soaring poignant 1911 Vienna late-romantic string quartet and luminous grand piano harmonies, "
        "deeply expressive solo cello melody rising over warm flowing accompaniment evoking Danube dawn, entrepreneurial fire and timeless creation, "
        "purely acoustic chamber instrumental, no modern pop drums, no percussion kit, no vocals, no singing, no Chinese instruments"
    ),
}

SCHUMPETER_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "vienna_coffeehouse_chime": {
        "name": "1911维也纳星火咖啡馆瓷杯与电车铃",
        "description": "维也纳环形大道咖啡馆青花瓷杯轻落瓷碟、银匙搅动黑咖啡与窗外远处有轨电车叮当清响",
        "sfx_prompt": (
            "Warm 1911 Vienna Ringstrasse coffeehouse parlor ambience with a delicate porcelain demitasse cup set gently on a saucer, "
            "silver spoon stirring espresso softly, wooden chair creaking, and a distant street tram bell outside arched glass windows, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "horse_carriage_cobblestone": {
        "name": "老汉斯马车铁箍木轮与石板蹄声",
        "description": "维也纳老街规律平稳的马蹄清踏、铁箍木轮碾过石板路与黄铜马具叮当，象征周而复始的循环流转",
        "sfx_prompt": (
            "Steady rhythmic clip-clop of carriage horses and iron-rimmed wooden wheels rolling evenly over 1911 Vienna cobblestone street "
            "with gentle brass harness jingles in a calm predictable cadence, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "motorcar_engine_ignition": {
        "name": "莱奥漏风工坊内燃机手摇点火轰鸣",
        "description": "1911年早期汽油内燃机手摇曲柄发力转动、两声咳喘后骤然轰鸣启动与钢扳手脆响",
        "sfx_prompt": (
            "Early 1911 gasoline motorcar metal hand crank turning firmly, brass ignition clicking, engine sputtering twice before roaring alive "
            "with energetic rhythmic pistons and clinking steel wrenches inside a timber workshop, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
    "bank_vault_credit_stamp": {
        "name": "维也纳商业银行厚账本与信贷钢印",
        "description": "牛皮厚账本翻页、蘸水钢笔刷刷签署信贷票据、黄铜钢印清脆落纸与厚重铁金库锁舌轻咔",
        "sfx_prompt": (
            "Heavy leather-bound 1911 Viennese bank ledger opening crisply, fountain pen signing a cotton-paper credit promissory note, "
            "solid brass embossing stamp pressing cleanly onto paper beside an iron vault latch click, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "vienna_stock_exchange_bell": {
        "name": "维也纳交易所铜钟与电报纸带急响",
        "description": "1911年维也纳交易所开盘铜钟清越急鸣、机械行情电报机哒哒吐带与交易纸单翻飞声",
        "sfx_prompt": (
            "Resonant 1911 European financial exchange brass trading bell ringing sharply followed by brisk mechanical telegraph stock ticker "
            "clacking rapidly and crisp paper order slips fluttering over an oak trading floor, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "danube_press_and_wind": {
        "name": "1911维也纳平板印刷机与多瑙河晨风",
        "description": "老式平板印刷机滚筒压印《经济发展理论》油墨书页，渐化作多瑙河畔清爽晨风与远方教堂钟声",
        "sfx_prompt": (
            "Steady 1911 flatbed printing press rollers pulling freshly inked thick book pages transitioning smoothly into gentle Danube morning breeze "
            "and soft distant Vienna cathedral chimes, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
