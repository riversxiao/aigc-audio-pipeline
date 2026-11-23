"""Canonical Pure-Acoustic Street-Documentary OST Palette & Sonic Motifs
for《零公式常识课：〈常识经济学〉街头案例剧》.

All 5 canonical OST themes are strictly grounded warm street-documentary pure-acoustic ensembles
(warm felt piano, mellow acoustic cello, plucked upright double bass, subtle acoustic guitar;
ZERO loud drums, ZERO percussion beats, ZERO vocals/singing, ZERO Chinese traditional instruments) —
guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

BASIC_ECONOMICS_OST: dict[str, str] = {
    "morning_market_pulse": (
        "Grounded warm street-documentary acoustic chamber score, nimble warm felt piano chords, "
        "buoyant plucked upright double bass, light acoustic guitar arpeggios and gentle pizzicato cello "
        "evoking an awakening neighborhood produce market and bustling everyday trade, purely acoustic "
        "instrumental, no loud drums, no percussion, no vocals, no singing, no Chinese instruments"
    ),
    "urban_commute_clarity": (
        "Crisp articulate modern documentary acoustic underscore, steady walking plucked upright bass, "
        "clean warm acoustic piano harmonies and flowing lyrical mellow cello evoking morning city commutes, "
        "neighborhood storefronts and clear-eyed common sense, purely acoustic instrumental, no loud drums, "
        "no percussion, no electronic synth, no vocals, no singing, no Chinese instruments"
    ),
    "price_control_tension": (
        "Taut thoughtful documentary debate acoustic score, insistent plucked upright double bass ostinato, "
        "crisp staccato felt piano voicings and tense expressive bowed cello evoking sharp policy debates, "
        "lengthening market queues and tightening supply chains, purely acoustic instrumental, no loud drums, "
        "no percussion, no modern synth, no vocals, no singing, no Chinese instruments"
    ),
    "harbor_trade_breeze": (
        "Expansive warm coastal documentary acoustic chamber score, airy warm acoustic piano arpeggios, "
        "singing mellow cello melody, gentle fingerpicked steel-string acoustic guitar and deep plucked "
        "upright bass evoking busy cargo harbors, cross-city freight and voluntary exchange, purely acoustic "
        "instrumental, no loud drums, no percussion, no vocals, no singing, no Chinese instruments"
    ),
    "evening_porch_common_sense": (
        "Intimate reflective twilight documentary acoustic epilogue, soft flowing felt piano chords, "
        "warm expressive solo cello melody and resonant plucked upright double bass evoking an evening "
        "neighborhood tea porch breeze and enduring everyday economic common sense, purely acoustic "
        "instrumental, no loud drums, no percussion, no vocals, no singing, no Chinese instruments"
    ),
}

BASIC_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "morning_produce_scale": {
        "name": "早市生鲜菜摊电子秤与塑袋装菜",
        "description": "海洲市清晨菜摊新鲜青菜装入薄膜袋沙沙作响、电子计价秤清脆滴声与铁盒硬币轻碰",
        "sfx_prompt": (
            "Crisp early-morning neighborhood produce market foley with fresh leafy vegetables rustling "
            "into a thin shopping bag, a digital market scale beeping softly, and coins clinking into "
            "a metal cash tray, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "warehouse_shutter_pallet": {
        "name": "生鲜冷链仓卷帘门升起与推车滑行",
        "description": "老何生鲜物流仓铁皮卷帘门顺畅拉起、液压地牛推车碾过水泥地与塑料菜筐清脆码放",
        "sfx_prompt": (
            "Grounded warehouse loading dock foley of a corrugated metal shutter rolling upward smoothly "
            "followed by a wooden hand-pallet truck rumbling across smooth concrete and plastic produce "
            "crates stacking neatly, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "typhoon_storefront_rain": {
        "name": "台风夜便利店雨打铁皮棚与门铃响",
        "description": "沿海台风大雨密密砸落街边雨棚、便利店玻璃门推开清脆铜铃响起与湿润脚步踏入",
        "sfx_prompt": (
            "Heavy coastal typhoon rain drumming steadily against a storefront metal awning as a glass "
            "convenience store door swings open with a brisk brass shop chime and damp footsteps enter, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "scooter_helm_receipt": {
        "name": "外卖电驴刹停、翻开面罩与热敏出单",
        "description": "电动摩托稳稳刹停路边、头盔护目面罩咔哒弹起与小店热敏打印机滋滋吐纸撕单",
        "sfx_prompt": (
            "Close-up street foley of an electric delivery scooter braking smoothly to a stop at a curb, "
            "a plastic helmet visor clicking open, and a thermal order receipt printer buzzing and "
            "tearing cleanly, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "clinic_pager_door": {
        "name": "诊所叫号柔和双音与听诊器轻放木桌",
        "description": "社区诊所清晰双音叫号提示、磨砂诊室门轻声合拢与不锈钢听诊器落上木质诊台",
        "sfx_prompt": (
            "Quiet modern neighborhood medical clinic interior foley with a gentle two-tone digital "
            "queue chime, a frosted glass consultation door clicking shut, and a steel stethoscope set "
            "softly onto a wooden desk, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "porch_tea_ledger": {
        "name": "街角常识茶铺倒茶与纸质账本翻页",
        "description": "海洲街角茶铺陶壶热茶倾入白瓷杯、茶碟轻碰与记账本在晚风中沙沙翻页",
        "sfx_prompt": (
            "Intimate evening tea porch ambience with warm hot tea pouring steadily from a ceramic pot "
            "into small cups, porcelain saucers clinking lightly, and crisp paper ledger pages turning "
            "in a calm breeze, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
