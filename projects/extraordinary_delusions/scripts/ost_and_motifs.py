"""Canonical 1841 Victorian London Baroque-Romantic Chamber OST Palette & Pure-Foley Motifs
for《1841伦敦泡沫档案：〈大癫狂〉金融疯魔史》.

All 5 canonical OST themes are strictly pure acoustic 1841 Victorian London baroque-romantic chamber
strings, harpsichord & dramatic cello (NO modern drums, NO vocals, NO Chinese instruments) — guaranteeing
100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

EXTRAORDINARY_DELUSIONS_OST: dict[str, str] = {
    "london_archive_gaslight": (
        "Intimate atmospheric 1841 Victorian London chamber music, warm expressive solo cello, "
        "delicate baroque harpsichord arpeggios and muted romantic strings evoking a gaslit Fleet Street archive study on a foggy night, "
        "purely acoustic instrumental, no modern drums, no vocals, no singing, no Chinese instruments"
    ),
    "amsterdam_tulip_fever": (
        "Lively playful 17th-century baroque-romantic chamber underscore, brisk harpsichord, "
        "nimble pizzicato violins and buoyant cello pulse evoking bustling Amsterdam canal taverns and absurd tulip bulb auctions, "
        "purely acoustic instrumental, no modern drums, no vocals, no singing, no Chinese instruments"
    ),
    "paris_rue_quincampoix": (
        "Elegant yet breathless 18th-century French baroque-romantic salon chamber score, sparkling swift harpsichord flourishes, "
        "dazzling classical violins and restless driving cello evoking Parisian Rue Quincampoix paper-money euphoria, "
        "purely acoustic instrumental, no modern drums, no vocals, no singing, no Chinese instruments"
    ),
    "south_sea_storm": (
        "Tense dramatic minor-key baroque-romantic chamber orchestra score, urgent low cello ostinato, "
        "sharp bowed strings and ominous harpsichord chords evoking Exchange Alley panic, bank runs and financial bubble collapse, "
        "purely acoustic instrumental, no modern drums, no vocals, no singing, no Chinese instruments"
    ),
    "sober_dawn_thames": (
        "Reflective poignant 1841 Victorian romantic chamber epilogue, lyrical melancholic solo cello melody, "
        "soft warm bowed strings and sparse tender harpsichord resonance evoking quiet foggy dawn along the Thames after crowd madness subsides, "
        "purely acoustic instrumental, no modern drums, no vocals, no singing, no Chinese instruments"
    ),
}

DELUSIONS_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "fleet_street_gaslight": {
        "name": "1841伦敦舰队街煤气灯档案室与雨窗",
        "description": "1841年伦敦雾夜煤气灯微微嘶响、厚重报刊卷宗翻页、黄铜镇纸轻落与窗外雨夜马车声",
        "sfx_prompt": (
            "Atmospheric 1841 Victorian London gaslit study ambience with soft hissing brass gas lamp, "
            "heavy bound archive ledger pages turning on an oak desk, faint rain on windowpanes, "
            "and distant carriage wheels on damp cobblestones, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "amsterdam_tulip_tavern": {
        "name": "1637阿姆斯特丹运河酒馆铜杯与木槌拍桌",
        "description": "1637年荷兰酒馆郁金香拍卖木槌脆落、锡制啤酒杯碰撞、鹅毛笔急促签下期货契约与运河水波",
        "sfx_prompt": (
            "17th-century Amsterdam canal tavern auction foley with sharp wooden gavel striking an oak table, "
            "pewter beer mugs clinking briskly, quill pen scratching rapidly on parchment contracts, "
            "and gentle canal water lapping outside, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "paris_banknote_press": {
        "name": "1720巴黎皇家银行木质印钞机与纸币翻飞",
        "description": "约翰·劳皇家银行连轴运转的木质印钞机滚压声与成捆崭新里弗尔纸币哗啦清点声",
        "sfx_prompt": (
            "Rapid mechanical thump and rolling slide of an 18th-century wooden banknote printing press pulling fresh sheets, "
            "followed by crisp stacks of cotton paper bank notes riffled swiftly across a polished counter, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "exchange_alley_bell": {
        "name": "1720伦敦交易所巷铜钟狂响与咖啡馆沸腾",
        "description": "伦敦乔纳森咖啡馆与交易所巷开盘黄铜摇铃急响、瓷咖啡杯磕碰与股票单据沙沙飞传",
        "sfx_prompt": (
            "Frantic 1720 London Exchange Alley coffeehouse foley with a bright hand-rung brass trading bell, "
            "porcelain coffee cups clattering against saucers, urgent boots tapping wooden floorboards, "
            "and crisp stock certificates rustling fast, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "royal_mint_gold_scale": {
        "name": "伦敦塔皇家造币厂精密天平与金币落盘",
        "description": "牛顿执掌的皇家造币厂精密黄铜天平轻颤、纯金基尼硬币清脆坠盘与石室座钟沉稳滴答",
        "sfx_prompt": (
            "Close-up precision foley inside the 18th-century Royal Mint at the Tower of London with a delicate brass balance scale swaying, "
            "pure gold guinea coins clinking crisply onto a metal pan, and a heavy stone chamber clock ticking steadily, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "thames_fog_bell": {
        "name": "泰晤士河晨雾渡船铜钟与远岸钟声",
        "description": "狂热退潮后的泰晤士河清晨水波拍岸、木船轻摇桨声与雾中远处青铜钟楼低沉缓鸣",
        "sfx_prompt": (
            "Quiet foggy Victorian morning along the River Thames with gentle water lapping stone embankment steps, "
            "distant slow bronze church bell tolling across calm mist, and soft wooden rowboat oars dipping smoothly, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
}
