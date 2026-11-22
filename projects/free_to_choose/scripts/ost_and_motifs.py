"""Canonical 1980 Chicago Documentary Acoustic Chamber-Jazz OST Palette & Sonic Motifs
for《1980芝加哥夜话：〈自由选择〉商业思想剧场》.

All 5 canonical OST themes are strictly pure acoustic 1980 Chicago documentary chamber-jazz
(warm felt piano, upright double bass, warm acoustic strings & nylon/steel guitar, zero loud drums,
zero modern electronic synth beats, zero singing vocals, zero Chinese xianxia instruments) —
guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

FREE_TO_CHOOSE_OST: dict[str, str] = {
    "chicago_twilight_study": (
        "Warm intimate 1980 Chicago documentary acoustic chamber-jazz, soft felt upright piano chords, "
        "gentle walking upright double bass and warm lyrical acoustic cello evoking a twilight Hyde Park study "
        "overlooking Lake Michigan, purely acoustic instrumental, no loud drums, no percussion, no singing, no vocals"
    ),
    "pencil_factory_pulse": (
        "Bright nimble 1980 documentary acoustic chamber underscore, crisp rhythmic acoustic guitar fingerpicking, "
        "playful pizzicato strings, warm felt piano pulse and light upright double bass evoking global workshops, "
        "bustling Hong Kong trade docks and spontaneous human cooperation, purely acoustic instrumental, "
        "no loud drums, no modern beat, no singing, no vocals"
    ),
    "washington_policy_clash": (
        "Taut articulate 1980 intellectual debate chamber-jazz score, insistent plucked upright double bass ostinato, "
        "crisp staccato felt piano chords and tense bowed viola and cello lines evoking sharp Washington policy hearings "
        "and lively economic debate, purely acoustic instrumental, no drums, no modern synth, no singing, no vocals"
    ),
    "depression_archive_elegy": (
        "Solemn reflective 1980 historical documentary chamber elegy, expressive mournful solo cello melody, "
        "sparse warm felt piano voicings and deep sustained upright double bass evoking 1929 winter bank queues "
        "and archival economic memory, purely acoustic instrumental, no drums, no synth, no singing, no vocals"
    ),
    "lake_michigan_dawn": (
        "Hopeful luminous 1980 documentary chamber epilogue, warm flowing felt piano arpeggios, singing acoustic strings, "
        "gentle fingerpicked acoustic guitar and soft upright bass evoking Lake Michigan sunrise and enduring human "
        "common sense, purely acoustic instrumental, no drums, no percussion, no singing, no vocals"
    ),
}

FREE_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "chicago_study_rain": {
        "name": "1980芝加哥海德公园书房秋雨与咖啡杯",
        "description": "密歇根湖畔秋雨轻叩木框窗棂、温热瓷杯轻落橡木书桌与笔记纸页沙沙翻动",
        "sfx_prompt": (
            "Warm cozy 1980 Chicago Hyde Park wood-paneled study ambience with soft autumn lake rain tapping "
            "against tall sash windows, a ceramic coffee mug gently set onto an oak desk, and crisp notepad pages "
            "turning, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "wooden_pencil_sketch": {
        "name": "黄色二号雪松木铅笔削笔与沙沙算账",
        "description": "木铅笔在黄铜卷笔刀里清脆旋转、石墨笔尖在账本纸上沙沙划动与轻叩桌面",
        "sfx_prompt": (
            "Crisp close-up foley of a yellow cedar wooden pencil twisting smoothly inside a brass hand sharpener "
            "followed by brisk graphite sketching across ledger paper and two light wooden taps on a desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "cash_register_bell": {
        "name": "芝加哥街口餐馆老式机械收银机清脆叮铃",
        "description": "老方小餐馆黄铜机械收银机按键咔嗒轻响、清脆铃声叮铃与钱箱滑出硬币碰响",
        "sfx_prompt": (
            "Vintage 1980 neighborhood diner mechanical brass cash register keys clicking crisply followed by "
            "a cheerful bell chime and the cash drawer sliding open with coins clinking gently, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "printing_press_hum": {
        "name": "老方社区小印刷厂胶印滚筒与出纸声",
        "description": "1980年社区小型胶印机滚筒平稳轻转、纸张清脆吸附翻落成叠的实业律动",
        "sfx_prompt": (
            "Warm rhythmic mechanical cadence of a small 1980 Chicago neighborhood offset printing press rollers "
            "turning steadily with freshly inked paper sheets flipping neatly onto a delivery tray, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "school_chalk_bell": {
        "name": "芝加哥公立教室粉笔板书与下课铜铃",
        "description": "粉笔在木框黑板上清脆书写、黑板擦轻拍与老式教学楼走廊铜铃响起",
        "sfx_prompt": (
            "Crisp white chalk tapping and writing briskly across a vintage classroom slate chalkboard followed by "
            "a clear brass school hallway bell ringing in a quiet wooden corridor, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "wall_street_ticker_hum": {
        "name": "1929华尔街老式行情纸带机与银行铁门",
        "description": "玻璃罩下黄铜纸带行情机急促哒哒作响，转入大理石银行大厅厚重金属门缓缓闭合",
        "sfx_prompt": (
            "Vintage 1929 mechanical brass stock ticker tape clattering briskly under a glass dome transitioning "
            "into a heavy steel bank vault door shutting firmly inside a hushed marble hall, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
