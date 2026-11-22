"""Canonical 1936 Interwar Cambridge Chamber OST Palette & Sonic Motifs for《1936剑桥迷雾：〈就业、利息和货币通论〉宏观思想剧场》.

All 5 canonical OST themes are strictly pure acoustic 1936 interwar British chamber music
(deep reflective solo cello, muted felt upright piano, intimate English string quartet, warm clarinet)
with zero modern drums, zero synths, zero Chinese xianxia instruments, and zero singing vocals —
guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

KEYNES_1936_OST: dict[str, str] = {
    "cambridge_winter_mist": (
        "Atmospheric 1936 interwar Cambridge chamber music, deep reflective solo cello, "
        "warm muted felt upright piano arpeggios and intimate English string quartet evoking misty college courtyards and fireside reflection, "
        "purely acoustic instrumental, no drums, no modern beat, no synth, no singing, no vocals"
    ),
    "manchester_silent_looms": (
        "Somber poignant 1936 interwar British chamber elegy, dark low bowed cello sustained tones, "
        "sparse melancholic felt upright piano chords and restrained minor-key English strings evoking silent Depression-era cotton mills, "
        "purely acoustic instrumental, no drums, no modern beat, no synth, no singing, no vocals"
    ),
    "london_exchange_fever": (
        "Restless taut 1936 interwar chamber suspense score, crisp rhythmic pizzicato strings, "
        "nimble staccato muted upright piano motifs and darting solo cello pulse evoking speculative London Stock Exchange fever and market nerves, "
        "purely acoustic instrumental, no modern drums, no pop beat, no synth, no singing, no vocals"
    ),
    "kings_college_debate": (
        "Sharp witty 1936 Cambridge intellectual chamber underscore, articulate contrapuntal English string quartet, "
        "clear conversational felt piano phrases and thoughtful solo cello dialogue evoking spirited academic debate and lucid logic, "
        "purely acoustic instrumental, no drums, no modern beat, no synth, no singing, no vocals"
    ),
    "river_cam_twilight_wisdom": (
        "Tender luminous 1936 English chamber epilogue, lyrical warm solo cello melody, "
        "gentle flowing muted felt upright piano and soft pastel string quartet evoking River Cam twilight and timeless economic wisdom, "
        "purely acoustic instrumental, no drums, no modern beat, no synth, no singing, no vocals"
    ),
}

KEYNES_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "cambridge_study_rain": {
        "name": "1936剑桥国王学院书房冬雨与炭炉",
        "description": "剑桥老石屋铅格窗外细密冬雨、壁炉红炭轻爆与厚重硬皮书页翻动声",
        "sfx_prompt": (
            "Cozy 1936 Cambridge university study ambience with steady cold winter rain tapping leaded glass windows, "
            "soft crackling coal fireplace hearth, and thick rag-paper book pages turning gently on an oak desk, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "textile_mill_halt": {
        "name": "曼彻斯特纺织厂织布机戛然停转与铁门落锁",
        "description": "老式蒸汽棉纺织布机由沉稳运转骤然减速停摆，随后空旷厂房回荡沉重铁链锁门声",
        "sfx_prompt": (
            "1930s Manchester brick cotton textile mill power looms slowing down with metallic belt squeal to an eerie halt, "
            "followed by a heavy iron factory gate clanging shut and padlock snapping in a quiet rainy yard, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
    "london_stock_ticker": {
        "name": "伦敦金融城纸带打字机与铜钟开盘沸腾",
        "description": "1936年伦敦证交所老式玻璃罩行情纸带机急促哒哒吐纸与黄铜交易钟清脆鸣响",
        "sfx_prompt": (
            "Brisk 1936 City of London stock exchange ticker-tape machine clicking rapidly under a glass dome "
            "beside a bright brass trading bell ring and rustling paper order slips on a wooden desk, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "college_tea_china": {
        "name": "剑桥高桌会骨瓷茶杯轻碰与银匙搅茶",
        "description": "英式细骨瓷茶杯落碟清响、银勺轻搅红茶与实木扶手椅微微挪动声",
        "sfx_prompt": (
            "Intimate 1930s Cambridge college parlor foley with delicate English bone china teacup clinking gently onto a saucer, "
            "silver teaspoon stirring hot tea, and warm creak of an oak armchair, pure foley, no human voice"
        ),
        "duration_seconds": 2.5,
    },
    "treasury_clock_chime": {
        "name": "伦敦白厅财政部老座钟报时与卷宗合页",
        "description": "伦敦白厅木嵌大理石座钟深沉报时、钢笔签字划过公文与沉稳合上牛皮预算账本",
        "sfx_prompt": (
            "Deep resonant chime of a grand 1930s Whitehall British Treasury mantle clock followed by crisp fountain pen scratching "
            "across ledger paper and a heavy leather budget folder closing firmly on mahogany, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "river_cam_rowing": {
        "name": "剑河暮色木船撑篙水波与远岸晚钟",
        "description": "剑河黄昏平底木船轻划水波、竹木撑篙滴水清响与国王学院礼拜堂悠远晚钟",
        "sfx_prompt": (
            "Peaceful twilight on the River Cam in Cambridge with gentle wooden punt gliding through calm water, "
            "rhythmic dripping pole ripples, and soft distant chapel bell echoing across the misty meadow, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
}
