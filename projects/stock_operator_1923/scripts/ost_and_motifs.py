"""Canonical 1920s Wall Street Noir Pure-Acoustic OST Palette & Sonic Motifs for《1923华尔街风云：〈股票大作手回忆录〉》.

All 5 canonical OST themes are strictly pure acoustic 1920s Wall Street noir chamber music
(late-night upright double bass, moody felt piano, velvet muted brass chamber accents)
with ZERO loud rock drums, ZERO singing vocals, and ZERO Chinese instruments — guaranteeing
100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

STOCK_OPERATOR_1923_OST: dict[str, str] = {
    "boston_bucket_shop_pulse": (
        "Brisk sly 1920s late-night Wall Street noir chamber underscore, nimble walking upright double bass, "
        "crisp moody felt piano chords and subtle muted brass trumpet accents evoking clandestine Boston bucket shops "
        "and sharp youthful ticker calculation, purely acoustic instrumental, no drums, no rock beat, no singing, no vocals"
    ),
    "wall_street_ticker_noir": (
        "Smoky atmospheric 1920s Wall Street noir nocturnal chamber music, warm slow walking upright double bass, "
        "pensive moody felt piano phrases and velvet muted brass horn sighs evoking rain-streaked Manhattan trading offices "
        "under green banker lamps, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "panic_of_1907_storm": (
        "Tense high-stakes 1920s financial noir thriller chamber score, urgent low bowed double bass ostinato, "
        "sharp dissonant moody felt piano bass chords and dark muted trombone chamber swells evoking the October 1907 "
        "Wall Street crash and vanishing liquidity, purely acoustic instrumental, no drums, no rock beat, no synth, no singing, no vocals"
    ),
    "cotton_king_trap": (
        "Seductive ominous 1920s Manhattan noir chamber underscore, smooth velvet muted brass horn melody "
        "over brooding minor-key felt piano arpeggios and heavy deliberate upright double bass footsteps evoking "
        "Wall Street persuasion and a fatal psychological trap, purely acoustic instrumental, no drums, no singing, no vocals"
    ),
    "manhattan_midnight_wisdom": (
        "Reflective soulful 1920s late-night Manhattan noir chamber epilogue, intimate solo moody felt piano ballad, "
        "warm resonant upright double bass and distant melancholic muted trumpet whisper evoking timeless wisdom "
        "on human greed, fear and market discipline, purely acoustic instrumental, no drums, no singing, no vocals"
    ),
}

STOCK_OPERATOR_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "brass_stock_ticker": {
        "name": "黄铜玻璃罩行情打字机哒哒吐带",
        "description": "1920年代华尔街标志性黄铜玻璃罩行情打字机机械嘀嗒打字、纸带卷曲滑落红木桌面的清脆声响",
        "sfx_prompt": (
            "Antique 1920s brass stock ticker machine under a glass dome clattering rhythmically "
            "with crisp mechanical printing ticks and curling paper ticker tape unreeling across a mahogany desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "boston_chalkboard_scribble": {
        "name": "波士顿对赌行黑板粉笔飞速抄价",
        "description": "十九世纪末波士顿证券黑板上清脆粉笔急促书写报价、毛毡黑板擦利落擦拭与木夹轻扣声",
        "sfx_prompt": (
            "Brisk crisp white chalk writing numbers rapidly on a tall slate quotation board "
            "followed by a felt eraser swishing clean and wooden clip snapping shut "
            "in a quiet 1890s Boston brokerage room, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "wall_street_trading_bell": {
        "name": "纽交所铜铃与大厅木地板急促脚步",
        "description": "纽约证券交易所黄铜开闭市响铃回荡大理石大厅，伴随皮鞋急奔木地板与纸质交易单沙沙翻飞",
        "sfx_prompt": (
            "Resonant antique brass trading floor bell ringing sharply inside a vast marble exchange hall "
            "followed by hurried leather shoes rushing over polished wood and fluttering paper order slips, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "banker_lamp_rain_study": {
        "name": "曼哈顿雨夜银行家绿灯与钢笔账簿",
        "description": "1923年曼哈顿高层办公室窗外夜雨敲玻璃、绿色银行家台灯金属拉链脆响与钢笔划过厚纸账簿声",
        "sfx_prompt": (
            "Raindrops tapping steadily against tall 1920s Manhattan office windows "
            "beside the crisp metal pull-chain click of a green glass banker lamp "
            "and fountain pen scratching on thick ledger paper, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "telegraph_morse_urgency": {
        "name": "华尔街电报机急促滴答脉冲",
        "description": "黄铜电报发报键高频急促敲击与西联黄色电报纸撕落桌面的紧张金属声响",
        "sfx_prompt": (
            "Crisp brass telegraph key tapping urgent rapid metallic clicks across a wooden dispatch desk "
            "with fluttering yellow Western Union telegram sheets, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "gold_vault_cash_count": {
        "name": "1907危机现钞点算与黄铜保险柜落锁",
        "description": "厚沓美钞在红木柜台上快速翻点清脆声，紧接沉重银行金库钢门闷响落锁",
        "sfx_prompt": (
            "Crisp thick stacks of 1907 paper dollar bills riffled swiftly on a dark mahogany bank counter "
            "followed by a heavy steel safe door shutting with a deep metallic lock clunk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
