"""Canonical Modern Cognitive Documentary Acoustic OST Palette & Sonic Motifs
for《决策的暗礁：行为经济学与〈思考，快与慢〉剧场》.

All 5 canonical OST themes match `_ECON_FINANCE_BGM_PRESETS["behavioral_econ_traps"]`
(curious modern documentary felt piano, pulsing pizzicato strings, warm subtle wooden marimba,
and plucked/bowed upright bass — strictly purely acoustic instrumental, zero heavy drums,
zero modern EDM beat, zero singing/vocals, zero Chinese xianxia instruments), guaranteeing
100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

BEHAVIORAL_ECON_OST: dict[str, str] = {
    "harbor_lab_curiosity": (
        "Curious warm modern documentary chamber score, intimate felt piano chords, gentle pulsing pizzicato "
        "strings, warm subtle wooden marimba resonance and soft upright bass evoking a twilight harbor study "
        "cafe and cognitive experiment table, purely acoustic instrumental, no heavy drums, no modern EDM beat, "
        "no singing, no vocals"
    ),
    "fast_brain_pizzicato": (
        "Playful nimble modern documentary chamber underscore, brisk pulsing pizzicato violin and cello, "
        "bright warm subtle wooden marimba ostinato, crisp staccato felt piano and light upright bass evoking "
        "snap intuitions, bustling cafe pricing traps and lively tabletop experiments, purely acoustic instrumental, "
        "no heavy drums, no modern EDM beat, no singing, no vocals"
    ),
    "reef_tension_clockwork": (
        "Taut inquisitive modern documentary chamber tension, insistent pulsing pizzicato cello line, sparse "
        "inquisitive felt piano voicings, subtle muted wooden marimba accents and low bowed upright bass evoking "
        "stock-loss pain, sunk-cost dilemmas and sharp cognitive debate, purely acoustic instrumental, "
        "no heavy drums, no modern EDM beat, no singing, no vocals"
    ),
    "slow_brain_reflection": (
        "Calm lucid modern documentary chamber reflection, warm unhurried felt piano progressions, expressive "
        "lyrical solo cello, delicate subtle wooden marimba overtones and soft upright bass evoking deliberate "
        "System-2 scrutiny, quiet humility and honest self-reflection, purely acoustic instrumental, "
        "no heavy drums, no modern EDM beat, no singing, no vocals"
    ),
    "lighthouse_nudge_clarity": (
        "Uplifting clear-eyed modern documentary chamber epilogue, flowing luminous felt piano arpeggios, "
        "warm singing acoustic strings, gentle glowing wooden marimba accents and steady upright bass evoking "
        "a coastal lighthouse sweeping clear night air and practical everyday decision clarity, purely acoustic "
        "instrumental, no heavy drums, no modern EDM beat, no singing, no vocals"
    ),
}

BEHAVIORAL_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "lab_cafe_espresso_ambience": {
        "name": "灯塔巷实验咖啡馆手冲水流与黄铜沙漏翻转",
        "description": "温热手冲咖啡轻注入陶瓷杯、黄铜框沙漏在木桌上轻翻转并响起细沙流动的微响",
        "sfx_prompt": (
            "Warm cozy harbor-side study cafe foley with gentle pour-over coffee streaming into a porcelain mug, "
            "a brass tabletop hourglass turning smoothly onto oak wood, and soft dry sand trickling inside glass, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "stopwatch_buzzer_click": {
        "name": "认知实验机械秒表按停与白板马克笔圈画",
        "description": "精密机械秒表清脆咔嗒按停，随后白板马克笔快速画圈与笔帽轻扣合拢",
        "sfx_prompt": (
            "Crisp close-up mechanical stopwatch metal crown clicking cleanly to a halt followed by a dry-erase "
            "marker circling briskly on a smooth lab whiteboard and the plastic cap snapping shut, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "brass_anchor_desk_thud": {
        "name": "黄铜小船锚轻磕橡木实验桌与硬币旋落",
        "description": "桌面黄铜小锚沉稳轻叩实木台面，一枚金属硬币清脆弹起旋转后平稳落定",
        "sfx_prompt": (
            "Solid miniature brass anchor setting down firmly onto an oak study table followed by a bright silver "
            "coin flicking cleanly into the air, spinning rapidly on wood, and settling flat, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "supermarket_scanner_receipt": {
        "name": "社区生鲜超市条码扫码嘀声与纸质小票撕下",
        "description": "超市收银台激光扫码器清脆嘀嘀两声、热敏打印机吐纸并利落撕下购物小票",
        "sfx_prompt": (
            "Modern neighborhood grocery checkout laser barcode scanner beeping twice crisply followed by a "
            "thermal receipt printer whirring out a paper strip and tearing cleanly along the metal edge, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "stock_ticker_mouse_click": {
        "name": "手机股市看盘提醒、鼠标急促连点与水杯顿落",
        "description": "办公桌面鼠标急促双击、键盘敲击几声后玻璃水杯微重顿落在木桌杯垫上",
        "sfx_prompt": (
            "Rapid tense computer mouse double clicks and brisk mechanical keyboard taps on a wooden desk "
            "followed by a heavy glass tumbler setting down firmly onto a cork coaster, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "checklist_pen_stamp": {
        "name": "钢笔在决策避礁清单上利落打勾与手账合拢",
        "description": "钢笔尖在厚实纸页上干脆划出几个对勾、纸页翻动随后硬壳实验手账稳稳合拢",
        "sfx_prompt": (
            "Fountain pen nib scratching four crisp checkmarks across thick notebook paper followed by a single "
            "page turning smoothly and a hardcover journal closing neatly onto a wooden desk, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
