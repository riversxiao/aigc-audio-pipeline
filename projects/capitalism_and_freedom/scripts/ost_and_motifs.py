"""Canonical 1962 Chicago Late-Night Acoustic Chamber-Jazz OST Palette & Sonic Motifs
for《1962芝加哥激辩：〈资本主义与自由〉》.

All 5 canonical OST themes match `_ECON_FINANCE_BGM_PRESETS["capitalism_and_freedom"]`:
1962 Chicago late-night intellectual acoustic jazz piano, warm upright bass and mellow chamber strings —
strictly purely acoustic instrumental, zero loud drums, zero modern EDM/electronic beat, zero singing/vocals,
zero Chinese xianxia instruments — guaranteeing 100% SHA-256 stem-cache reuse across Season 1 on Colab 96GB G4.
"""

from __future__ import annotations

CAPFREE_OST: dict[str, str] = {
    "chicago_1962_seminar": (
        "Warm 1962 Chicago late-night intellectual acoustic jazz piano, warm walking upright double bass "
        "and mellow legato chamber strings evoking autumn streetlamps outside a Gothic Hyde Park seminar hall, "
        "purely acoustic instrumental, no loud drums, no percussion, no modern beat, no singing, no vocals"
    ),
    "jazz_lounge_sparks": (
        "Nimble witty 1962 Chicago late-night intellectual acoustic jazz piano voicings, agile plucked upright bass "
        "and lively pizzicato mellow strings evoking spirited café-table debate and sharp economic insight, "
        "purely acoustic instrumental, no loud drums, no percussion, no modern EDM beat, no singing, no vocals"
    ),
    "washington_hearing_tension": (
        "Taut articulate 1962 Washington policy hearing chamber-jazz underscore, insistent upright double bass ostinato, "
        "crisp staccato acoustic jazz piano chords and tense bowed mellow viola and cello lines evoking sharp "
        "congressional debate and institutional clash, purely acoustic instrumental, no loud drums, no modern synth, "
        "no singing, no vocals"
    ),
    "gold_peg_elegy": (
        "Solemn reflective 1962 Chicago nocturnal chamber elegy, expressive solo acoustic cello melody, sparse warm "
        "late-night acoustic jazz piano voicings and deep sustained upright double bass evoking Bretton Woods strain, "
        "Depression archives and quiet working-family hardship, purely acoustic instrumental, no loud drums, "
        "no percussion, no singing, no vocals"
    ),
    "lakeshore_clarity_dawn": (
        "Luminous hopeful 1962 Chicago lakeshore epilogue, flowing warm acoustic jazz piano arpeggios, mellow singing "
        "chamber strings and gentle upright double bass evoking crisp dawn clarity and enduring civic common sense, "
        "purely acoustic instrumental, no loud drums, no percussion, no modern beat, no singing, no vocals"
    ),
}

CAPFREE_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "hydepark_chalk_rain": {
        "name": "1962芝加哥海德公园哥特讲堂秋雨与粉笔板书",
        "description": "秋雨轻敲海德公园哥特拱窗铅框玻璃、白色粉笔在石板黑板上沙沙疾书、橡木座椅轻响",
        "sfx_prompt": (
            "Cozy 1962 University of Chicago Gothic seminar room ambience with light autumn rain tapping leaded "
            "glass windows, crisp white chalk writing briskly on a slate blackboard, and an oak chair creaking "
            "gently, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "chicago_lounge_coffee": {
        "name": "1962芝加哥深夜爵士清吧瓷杯轻碰与翻页",
        "description": "深夜清吧金属小勺轻搅温热咖啡杯、瓷碟轻放桃花心木桌面与笔记本纸页脆响翻动",
        "sfx_prompt": (
            "Intimate 1962 Chicago late-night neighborhood coffee lounge foley with a ceramic mug stirred gently "
            "with a metal spoon, a porcelain saucer clinking onto a polished mahogany table, and crisp notepad "
            "pages turning, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "referee_whistle_gavel": {
        "name": "裁判黄铜哨音转华盛顿听证会橡木法槌",
        "description": "清脆复古黄铜裁判哨声回荡，随即切入华盛顿听证厅厚重橡木法槌连敲两下",
        "sfx_prompt": (
            "Sharp brief vintage brass sports referee whistle blast echoing faintly across an empty court "
            "transitioning cleanly into a heavy oak committee gavel striking a wooden sound block twice in a "
            "quiet hall, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "teleprinter_gold_vault": {
        "name": "1962外汇电传打字机与中央银行金库沉重铁门",
        "description": "老式国际外汇电传机在纸带上急促哒哒敲击，转入中央银行金库黄铜转盘沉重锁闭",
        "sfx_prompt": (
            "Vintage 1962 international currency desk mechanical teleprinter clacking rhythmically on paper tape "
            "followed by the resonant metallic clunk of a central bank gold vault wheel locking firmly, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "barber_shears_bell": {
        "name": "芝加哥街角老韩理发铺铜门铃与剪刀咔嚓",
        "description": "社区老理发铺黄铜门铃清脆摇响、精钢理发剪刀节奏明快地咔嚓裁剪与皮质理发椅液压沉降",
        "sfx_prompt": (
            "Warm neighborhood 1962 barbershop entrance brass door bell jingling softly followed by crisp steel "
            "barber shears snipping rhythmically and a heavy leather barber chair hydraulic pedal settling, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "school_bell_voucher_stamp": {
        "name": "芝加哥社区校园铜铃与厚纸凭证叠放桌面",
        "description": "木质走廊里清脆的复古铜铃摇响，转入几张厚实纸质教育凭证整齐轻叩橡木餐桌",
        "sfx_prompt": (
            "Clear vintage brass school hallway bell ringing softly in a wooden corridor followed by crisp thick "
            "paper certificates stacked neatly and tapped squarely onto an oak kitchen table, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
