"""Canonical Sweeping European Historical Documentary Acoustic OST Palette & Sonic Motifs
for《金钱的崛起：从美第奇银行到现代华尔街》.

All 5 canonical OST themes match `_ECON_FINANCE_BGM_PRESETS["ascent_of_money"]`
(sweeping European historical documentary chamber strings, Renaissance lute accents,
warm solo cello and crisp harpsichord/piano — purely acoustic instrumental, zero pop drums,
zero modern electronic beats, zero singing vocals, zero Chinese xianxia instruments) —
guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

ASCENT_OF_MONEY_OST: dict[str, str] = {
    "florence_ledger_overture": (
        "Sweeping European historical documentary chamber strings, delicate Renaissance lute accents, "
        "warm expressive solo cello and crisp wooden harpsichord pulse evoking golden twilight over "
        "the Arno River and a Florentine banking ledger hall, purely acoustic instrumental, "
        "no pop drums, no percussion, no singing, no vocals, no Chinese xianxia instruments"
    ),
    "venice_bond_intrigue": (
        "Taut articulate European historical documentary chamber strings ostinato, crisp baroque harpsichord "
        "figures, urgent bowed viola and resonant low cello lines evoking Venetian canal sovereign bond desks "
        "and London Waterloo courier intrigue, purely acoustic instrumental, "
        "no pop drums, no modern synth, no singing, no vocals, no Chinese xianxia instruments"
    ),
    "amsterdam_spice_voyage": (
        "Buoyant nimble European historical documentary chamber ensemble, bright plucked Renaissance lute "
        "arpeggios, lively pizzicato strings, warm solo cello and crisp parlor piano pulse evoking "
        "1602 Amsterdam spice ships and the first stock exchange courtyard, purely acoustic instrumental, "
        "no pop drums, no percussion, no singing, no vocals, no Chinese xianxia instruments"
    ),
    "edinburgh_actuarial_hearth": (
        "Reflective scholarly European historical documentary chamber elegy, warm lyrical solo cello melody, "
        "sparse resonant acoustic piano chords and soft sustained chamber strings evoking a rainy 1744 "
        "Edinburgh stone parish study and patient actuarial math, purely acoustic instrumental, "
        "no pop drums, no modern synth, no singing, no vocals, no Chinese xianxia instruments"
    ),
    "trust_across_millennia": (
        "Sweeping luminous European historical documentary chamber finale, soaring acoustic chamber strings, "
        "noble warm solo cello, gentle Renaissance lute filigree and rich acoustic grand piano chords "
        "evoking five thousand years of human financial trust from clay tablets to modern networks, "
        "purely acoustic instrumental, no pop drums, no percussion, no singing, no vocals, "
        "no Chinese xianxia instruments"
    ),
}

ASCENT_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "clay_tablet_quill": {
        "name": "巴比伦芦苇笔刻泥板与美第奇鹅毛笔大账本",
        "description": "削尖的芦苇笔在湿润泥板上清脆压出契约刻痕，顺畅切入文艺复兴鹅毛笔在羊皮纸账本上沙沙记账",
        "sfx_prompt": (
            "Close-up dry foley of a sharpened reed stylus pressing crisp wedge marks into damp clay "
            "transitioning into a goose-quill pen scratching neatly across heavy parchment ledger paper, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "florin_gold_scales": {
        "name": "佛罗伦萨黄铜天平称量弗罗林金币与合拢账册",
        "description": "沉甸甸的弗罗林金币轻落文艺复兴黄铜天平秤盘叮当作响，厚重皮面大账本在胡桃木桌上稳稳合拢",
        "sfx_prompt": (
            "Crisp foley of heavy gold florin coins dropping gently onto a small Renaissance brass balance "
            "scale pan followed by a thick leather-bound accounting ledger closing firmly on a walnut desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "venice_canal_wax_seal": {
        "name": "威尼斯运河水波、火漆封缄公债与石板信使马蹄",
        "description": "威尼斯运河水浪轻拍石阶码头、黄铜印章利落压下滚烫火漆封住羊皮纸国债、远方急促信使马蹄踏过石街",
        "sfx_prompt": (
            "Gentle Venetian canal water lapping softly against stone quay steps, hot sealing wax stamped "
            "crisply onto parchment bond paper with a brass signet ring, and brisk distant horse hooves "
            "over cobblestones, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "amsterdam_harbor_bell": {
        "name": "一六零二阿姆斯特丹木帆船缆绳与交易所开市铜钟",
        "description": "荷兰远洋木帆船桅杆缆绳随港湾潮水吱呀轻响，清亮铸铜交易所开市钟敲响与亚麻纸股票翻动声",
        "sfx_prompt": (
            "Wooden Dutch merchant sailing ship rigging creaking gently beside harbor waves followed by "
            "a bright cast-brass Amsterdam exchange opening bell ringing once and crisp linen share "
            "certificates rustling, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "edinburgh_rain_clock": {
        "name": "爱丁堡石屋秋雨、老式落地摆钟与石板精算粉笔",
        "description": "苏格兰绵密雨点敲打铅框窗棂、木质落地摆钟沉稳滴答，伴随清脆粉笔在石板上列出寿数精算栏",
        "sfx_prompt": (
            "Steady Scottish rain tapping against leaded stone-parish windowpanes, a warm wooden grandfather "
            "pendulum clock ticking deliberately, and crisp slate chalk noting actuarial columns on a desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "modern_ledger_keys": {
        "name": "现代房贷合同翻页、门钥匙轻落与数字账本敲击",
        "description": "厚实纸质房贷合同翻页、一串沉甸甸的金属家门钥匙轻落木桌，衔接利落的现代键盘数字入账轻响",
        "sfx_prompt": (
            "Crisp paper pages of a modern housing mortgage contract flipping on a desk, a set of steel house "
            "keys clinking softly onto wood, and a subtle clean mechanical keyboard typing ledger entries, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
}
