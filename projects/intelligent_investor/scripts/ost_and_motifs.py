"""Canonical 1950s Columbia University Academic Study Pure-Acoustic OST Palette & Sonic Motifs
for《哥伦比亚价值课堂：〈聪明的投资者〉》.

All 5 canonical OST themes are strictly pure acoustic 1950s New York academic study music
(warm felt acoustic piano, soft lyrical cello, and gentle jazz upright double bass — NO loud drums,
NO modern electronic synths, NO singing vocals, NO Chinese instruments), guaranteeing 100% SHA-256
stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

INTELLIGENT_INVESTOR_OST: dict[str, str] = {
    "columbia_evening_lecture": (
        "Calm warm 1950s New York academic study pure acoustic chamber music, soft felt acoustic piano chords, "
        "warm lyrical solo cello and gentle walking jazz upright double bass evoking an autumn dusk lecture hall "
        "at Columbia University, purely acoustic instrumental, no drums, no percussion, no vocals, no singing, "
        "no Chinese instruments"
    ),
    "mr_market_knock": (
        "Witty articulate 1950s New York chamber-jazz underscore, nimble playful upright double bass pizzicato, "
        "crisp conversational felt acoustic piano phrasing and light bowed cello counterpoint evoking an eccentric "
        "business partner knocking at the door, purely acoustic instrumental, no drums, no percussion, no vocals, "
        "no singing, no Chinese instruments"
    ),
    "margin_of_safety_bridge": (
        "Grounded steady 1950s New York study chamber piece, resonant measured acoustic piano voicings, "
        "deep reassuring solo cello melody and firm warm upright double bass evoking timeless architectural "
        "strength and calm arithmetic discipline, purely acoustic instrumental, no drums, no percussion, "
        "no vocals, no singing, no Chinese instruments"
    ),
    "wall_street_noise_fade": (
        "Taut reflective 1950s financial documentary acoustic score, restrained pulsing upright double bass ostinato, "
        "sparse minor felt acoustic piano chords and poignant bowed cello lines evoking Wall Street frenzy fading "
        "into quiet sober reflection, purely acoustic instrumental, no loud drums, no percussion, no vocals, "
        "no singing, no Chinese instruments"
    ),
    "steady_compounding_dusk": (
        "Serene luminous 1950s New York twilight chamber epilogue, flowing warm acoustic piano arpeggios, "
        "tender singing cello harmonies and soft unhurried jazz upright double bass evoking quiet patience, "
        "family peace of mind and lifelong compounding, purely acoustic instrumental, no drums, no percussion, "
        "no vocals, no singing, no Chinese instruments"
    ),
}

INVESTOR_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "columbia_chalkboard_evening": {
        "name": "1951哥伦比亚大学暮色阶梯教室粉笔与年报翻页",
        "description": "纽约晨边高地晚间阶梯教室橡木推门轻阖、白色粉笔在石板黑板上沉稳落笔与厚重纸质企业手册沙沙翻页",
        "sfx_prompt": (
            "Warm 1950s Columbia University evening lecture hall ambience with a heavy oak door closing softly, "
            "crisp white chalk writing steadily on a slate chalkboard, and thick annual report pages turning gently, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "mr_market_door_knock": {
        "name": "“市场先生”每天敲门与餐厅黄铜门铃",
        "description": "急促而情绪起伏的指节砰砰叩响老陈餐厅木门、门框黄铜铃铛一阵乱晃与木门沉稳阖上",
        "sfx_prompt": (
            "Brisk impatient knuckles knocking loudly on a wooden diner office door while a small brass shop bell "
            "jingles excitedly, followed by the heavy door calmly latching shut, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "ledger_pencil_calc": {
        "name": "格雷厄姆资产负债表钢笔勾画与怀表滴答",
        "description": "厚重账簿摊开在实木讲台、钢笔尖在资产负债纸页上清脆勾画数字与口袋机械怀表平稳滴答",
        "sfx_prompt": (
            "Close-up foley of a thick accounting ledger opening on an oak desk, a fountain pen sketching crisp "
            "columns across paper, and a calm mechanical pocket watch ticking steadily, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "wall_street_ticker_clatter": {
        "name": "华尔街行情纸带机急促哒哒与交易所铃声",
        "description": "玻璃罩下老式黄铜行情纸带机密集敲击、纸带簌簌吐出与远程电报铃清脆短鸣",
        "sfx_prompt": (
            "Vintage 1950s Wall Street mechanical brass stock ticker clattering rapidly beneath a glass dome "
            "with paper tape feeding briskly and a crisp telegraph desk bell ringing once, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "steel_bridge_train_test": {
        "name": "三十吨承重钢铁铁路桥稳扛重型货车驶过",
        "description": "厚重铆接钢架桥低沉踏实的钢铁共鸣、重型货运车轮平稳滚过铁轨接缝而桥身纹丝不动",
        "sfx_prompt": (
            "Deep sturdy metallic resonance of a heavy riveted steel truss bridge supporting a slow freight truck "
            "rolling steadily across iron deck plates without flexing, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "family_piggybank_tea": {
        "name": "普通家庭暖灯书桌瓷杯轻放与存折翻页",
        "description": "安静客厅书桌上温热茶杯轻落木垫、定投存折平整翻页与几枚硬币清脆落入瓷罐",
        "sfx_prompt": (
            "Quiet cozy home study desk foley of a warm porcelain teacup resting onto a wooden coaster, crisp "
            "savings passbook pages turning smoothly, and three coins dropping gently into a ceramic jar, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
