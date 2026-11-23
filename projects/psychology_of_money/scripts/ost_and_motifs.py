"""Canonical Warm Fireside Acoustic Chamber OST Palette & Sonic Motifs
for《财富长跑课：〈金钱心理学〉普通人致富剧》.

All 5 canonical OST themes match `_ECON_FINANCE_BGM_PRESETS["psychology_of_money"]`
(warm fireside intimate acoustic guitar, soft felt piano, tender solo cello and gentle upright bass —
purely acoustic instrumental, zero modern drums, zero percussion, zero singing/vocals, zero Chinese
xianxia instruments) — guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes.
"""

from __future__ import annotations

PSYCHOLOGY_OF_MONEY_OST: dict[str, str] = {
    "fireside_hearth_theme": (
        "Warm fireside intimate acoustic guitar fingerpicking, soft felt piano chords, tender solo cello melody "
        "and gentle upright bass evoking a glowing autumn wood-paneled bookshop hearth and honest late-night "
        "conversation about life and money, purely acoustic instrumental, no modern drums, no percussion, "
        "no singing, no vocals"
    ),
    "quiet_compounding_pulse": (
        "Warm fireside intimate acoustic guitar arpeggios, soft steady felt piano pulse, gentle walking upright bass "
        "and tender lyrical solo cello evoking quiet patience, ticking vintage pocket watches and decades of silent "
        "compound growth, purely acoustic instrumental, no modern drums, no percussion, no singing, no vocals"
    ),
    "glass_tower_tension": (
        "Restrained intimate acoustic chamber underscore with sparse low felt piano chords, muted acoustic guitar "
        "harmonics, taut plucked upright bass and tense bowed solo cello evoking sleepless midnight markets, fragile "
        "leverage and bruised pride, purely acoustic instrumental, no modern drums, no electronic synth, "
        "no singing, no vocals"
    ),
    "autumn_rain_reflection": (
        "Tender reflective fireside chamber elegy with expressive poignant solo cello, soft sparse felt piano "
        "voicings, warm resonant acoustic guitar and hushed upright bass evoking autumn rain on window panes, "
        "humility before luck and risk and quiet forgiveness, purely acoustic instrumental, no modern drums, "
        "no percussion, no singing, no vocals"
    ),
    "morning_autonomy_dawn": (
        "Luminous hopeful morning fireside chamber epilogue with warm flowing felt piano arpeggios, gentle sunlit "
        "acoustic guitar, singing tender solo cello and soft upright bass evoking peaceful sleep, enoughness and "
        "waking up in charge of your own time, purely acoustic instrumental, no modern drums, no percussion, "
        "no singing, no vocals"
    ),
}

MONEY_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "fireside_bookshop_hearth": {
        "name": "慢火书屋壁炉柴火轻爆与温热茶杯落桌",
        "description": "木屋书吧壁炉柴火噼啪轻响、窗外细微秋雨，与一只温热瓷杯轻轻落在老橡木桌上",
        "sfx_prompt": (
            "Warm intimate wood-paneled bookshop ambience with gentle fireplace logs crackling softly, "
            "a ceramic mug set lightly onto a scarred oak table, and soft autumn rain outside, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "brass_pocket_watch_tick": {
        "name": "老黄铜怀表弹开与沉稳时光复利滴答",
        "description": "乔师傅珍藏的老式黄铜怀表盖清脆弹开，在安静木屋里响起不疾不徐的机械滴答声",
        "sfx_prompt": (
            "Close-up foley of a vintage brass pocket watch lid snapping open cleanly followed by "
            "steady rhythmic mechanical ticking in a quiet wooden room, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "toolbox_ledger_flip": {
        "name": "旧帆布工具包落凳与手写记账本沙沙翻页",
        "description": "褪色帆布维修工具包轻放长木凳、扳手微碰轻响，与磨毛边手写记账本纸页缓缓翻开",
        "sfx_prompt": (
            "Tactile foley of a worn canvas repairman tool bag setting down gently on a wooden bench, "
            "a brass wrench clinking softly, and crisp worn notebook ledger pages turning, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "midnight_phone_vibrate": {
        "name": "深夜行情提醒微震与高楼冷风玻璃声",
        "description": "深夜玻璃书桌上手机连续两声低沉震动、笔记本触控板急促轻点与高楼窗外冷风低吟",
        "sfx_prompt": (
            "Quiet late-night apartment foley of a smartphone buzzing softly twice against a glass desk "
            "beside a rapid laptop trackpad click and faint high-rise wind against window panes, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "luxury_car_door_thud": {
        "name": "豪车厚重关门闷响与冷清地库皮鞋脚步",
        "description": "豪华跑车厚重车门在空旷水泥地库里沉闷合上、锁车轻响与渐行渐远的孤独皮鞋声",
        "sfx_prompt": (
            "Crisp close-up foley of a heavy luxury sports car door closing with a deep muted thud "
            "inside an echoing concrete parking garage followed by a key fob chime and retreating "
            "leather footsteps, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "morning_kettle_chime": {
        "name": "清晨细嘴壶注水茶香与木窗推开微风鸟鸣",
        "description": "清晨安静厨房里细嘴壶热水平稳注入瓷杯，木格窗轻轻推开迎来微风与远处几声轻快鸟鸣",
        "sfx_prompt": (
            "Peaceful morning kitchen foley of a stovetop gooseneck kettle softly pouring hot water "
            "into a porcelain teacup as a wooden sash window slides open to distant gentle morning breeze "
            "and faint birdsong, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
