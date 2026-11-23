"""Canonical Minimalist Chamber-Strategy Acoustic OST Palette & Pure-Foley Sonic Motifs
for《高手怎么出牌：〈策略思维与博弈论〉商业剧》.

All 5 canonical OST themes strictly match `_ECON_FINANCE_BGM_PRESETS["game_theory_strategy"]`
(clever crisp minimalist chamber strings, rhythmic pizzicato cello, sharp felt piano and nimble
upright bass — purely acoustic instrumental, no heavy pop drums, no modern electronic synth beats,
no singing vocals, no Chinese xianxia instruments), ensuring 100% SHA-256 stem-cache reuse across
all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

GAME_THEORY_OST: dict[str, str] = {
    "chessboard_opening": (
        "Clever crisp minimalist chamber strings, nimble rhythmic pizzicato cello, sharp staccato felt piano "
        "and light upright bass evoking a refined modern strategy tea-room and the first calculated move on a "
        "wooden Go board, purely acoustic instrumental, no heavy pop drums, no percussion, no singing, no vocals"
    ),
    "street_price_war": (
        "Brisk witty minimalist chamber tension, driving rhythmic pizzicato cello ostinato, sharp crisp felt piano "
        "chords, nimble plucked upright bass and darting chamber violin evoking rival commercial-street storefronts "
        "launching rapid discount banners, purely acoustic instrumental, no heavy pop drums, no modern beat, "
        "no singing, no vocals"
    ),
    "boardroom_brinkmanship": (
        "Taut high-stakes minimalist chamber thriller underscore, crisp bowed viola and cello lines over insistent "
        "rhythmic pizzicato upright bass and razor-sharp felt piano accents evoking a late-night M&A boardroom "
        "showdown and burning-bridges commitment, purely acoustic instrumental, no heavy pop drums, no synth, "
        "no singing, no vocals"
    ),
    "auction_floor_pulse": (
        "Suspenseful poised minimalist chamber strings, crisp ticking pizzicato cello, delicate sharp felt piano "
        "motifs and restrained low upright bass evoking a gleaming auction hall where numbered paddles rise in "
        "calculated silence, purely acoustic instrumental, no heavy pop drums, no percussion, no singing, no vocals"
    ),
    "repeated_game_dawn": (
        "Warm lucid minimalist chamber resolution, flowing sharp felt piano arpeggios, graceful lyrical cello, "
        "bright minimalist chamber strings and gentle walking upright bass evoking long-term trust, enduring rules "
        "and a sunlit courtyard tea table, purely acoustic instrumental, no heavy pop drums, no percussion, "
        "no singing, no vocals"
    ),
}

GAME_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "go_stone_snap": {
        "name": "黑白棋盘落子与木罐清脆磕响",
        "description": "云子黑石清脆拍落厚木围棋盘，伴随雪松棋罐内棋子轻碰的策略破局提示音",
        "sfx_prompt": (
            "Close-up crisp foley of a polished slate Go stone snapping firmly onto a resonant wooden goban board "
            "followed by glass stones shifting lightly inside a lidded cedar bowl, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "tea_shop_receipt_printer": {
        "name": "商业街奶茶店外卖小票机急促出单声",
        "description": "春风商业街热敏小票机连续吐纸撕单、冷饮塑盖清脆扣合与冰块晃动声",
        "sfx_prompt": (
            "Brisk modern beverage shop thermal receipt printer whirring and tearing off a paper order slip rapidly "
            "followed by a crisp plastic cup lid snapping shut and ice cubes clinking, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "boardroom_contract_slide": {
        "name": "陆家嘴会议室合同推桌与钢笔落墨",
        "description": "厚重装订商业合同划过实木会议长桌、黄铜钢笔拔帽与纸面利落签字声",
        "sfx_prompt": (
            "Sleek glass-and-oak corporate boardroom ambience with a thick bound contract folder sliding briskly "
            "across polished wood, brass fountain pen uncapping and crisp signature scratching on heavy paper, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "auction_gavel_strike": {
        "name": "滨江拍卖大厅举牌轻响与木槌三落",
        "description": "宽阔拍卖大厅内硬纸竞价号牌微扬，随后红木拍卖槌清脆三响落定音砧",
        "sfx_prompt": (
            "Spacious refined auction hall acoustics with numbered cardboard paddles lifting through quiet air "
            "followed by three crisp resonant mahogany gavel strikes echoing softly on a wooden sounding block, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "abacus_and_ledger_flip": {
        "name": "老马铺子脆拨算盘与快翻进货账本",
        "description": "老式木算珠在竹档间连串脆响，紧接厚实进货账本快速翻页与签字笔轻点柜台",
        "sfx_prompt": (
            "Crisp wooden abacus beads clicking briskly across bamboo rods followed by thick paper ledger pages "
            "flipping quickly and a ballpoint pen tapping twice on a counter, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "courtyard_tea_pour": {
        "name": "黑白茶社紫砂壶斟茶与白瓷轻碰",
        "description": "暖静庭院内紫砂壶热乌龙清流注入白瓷品茗杯，杯托轻放原木茶桌",
        "sfx_prompt": (
            "Warm peaceful tea-house courtyard ambience with hot oolong tea streaming cleanly from a clay teapot "
            "into small porcelain cups and a bamboo coaster resting softly on a wooden table, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
