"""Canonical 1759 Scottish Enlightenment Chamber OST Palette & Sonic Motifs for《1759格拉斯哥灯火：〈道德情操论〉商业温度》.

All 5 canonical OST themes are strictly pure acoustic 1759 Scottish Enlightenment chamber music
(warm intimate baroque chamber strings, expressive solo cello, gentle wooden flute) with zero
modern drums, zero synths, zero Chinese instruments, and zero vocals — guaranteeing 100% SHA-256
stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

MORAL_SENTIMENTS_OST: dict[str, str] = {
    "glasgow_candle_empathy": (
        "Warm intimate 1759 Scottish Enlightenment baroque chamber music, lyrical expressive solo cello, "
        "soft glowing chamber strings and gentle wooden flute evoking candlelit Glasgow warmth and human empathy, "
        "purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "impartial_spectator_theme": (
        "Clear poised 18th-century Scottish Enlightenment baroque chamber underscore, articulate solo cello, "
        "luminous chamber violins and delicate classical wooden flute dialogue evoking quiet conscience and self-command, "
        "purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "vanity_parlor_tension": (
        "Dramatic minor-key 18th-century Scottish aristocratic parlor chamber score, crisp taut baroque strings, "
        "brooding low solo cello ostinato and poised wooden flute accents evoking gilded vanity, class scorn and sharp moral clash, "
        "purely acoustic instrumental, no drums, no modern synth, no singing, no vocals"
    ),
    "poor_mans_son_elegy": (
        "Poignant reflective 18th-century Scottish chamber elegy, deeply expressive melancholic solo cello, "
        "hushed sustained baroque strings and wistful wooden flute sighs evoking a lifetime chasing hollow palaces before finding quiet peace, "
        "purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "kirkcaldy_twilight_peace": (
        "Serene luminous 1759 Scottish coastal twilight chamber epilogue, tender warm solo cello melody, "
        "gentle glowing baroque chamber strings and airy wooden flute breath evoking Kirkcaldy calm, honest dignity and humane warmth, "
        "purely acoustic instrumental, no drums, no modern beat, no singing, no vocals"
    ),
}

MORAL_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "glasgow_rainy_candle_study": {
        "name": "1759格拉斯哥雨夜烛火书斋与热茶",
        "description": "苏格兰雨夜窗棂细雨轻敲、石壁炉暖火劈啪、青瓷茶杯轻落橡木桌与鹅毛笔沙沙落纸",
        "sfx_prompt": (
            "Warm cozy 1759 Glasgow stone study ambience with soft evening rain pattering on leaded glass windows, "
            "gentle hearth fire crackling, a porcelain teacup resting on an oak table, and a quill pen lightly scratching thick rag paper, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "carpenter_workshop_plane": {
        "name": "老麦克木匠坊推刨木花与木槌敲榫",
        "description": "格拉斯哥手工木匠坊手推木刨清脆削出松木刨花、木槌沉稳轻敲严丝合缝的榫卯结构",
        "sfx_prompt": (
            "Warm 18th-century Scottish carpenter workshop foley with a wooden hand plane crisply shaving fragrant pine wood curls, "
            "steady soft wooden mallet taps fitting a tight mortise joint, and wood shavings brushing off an oak bench, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "aristocrat_carriage_velvet": {
        "name": "克雷文勋爵镶金马车与贵族客厅银茶具",
        "description": "沉重四驾马车铁轮滚过格拉斯哥湿润石板路、车门铜锁脆响与华丽客厅纯银茶匙轻碰瓷盘",
        "sfx_prompt": (
            "18th-century gilded aristocratic horse carriage wheels rumbling crisply across wet Glasgow cobblestones, "
            "sharp brass coach door latch opening, transitioning to delicate silver tea spoons clinking softly against fine bone china in an ornate parlor, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "glasgow_lecture_hall_bells": {
        "name": "格拉斯哥大学石院钟声与讲堂书页",
        "description": "1759年格拉斯哥老学院钟楼温润铜钟远鸣、讲堂木椅轻移与学生翻开厚重笔记沙沙响",
        "sfx_prompt": (
            "Atmospheric 1759 University of Glasgow stone courtyard bell tolling softly in the distance, "
            "wooden lecture hall benches creaking lightly, and crisp parchment notebook pages turning with steady quill strokes, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "brass_pocket_compass_tick": {
        "name": "心内“公正旁观者”黄铜怀表与罗盘轻合",
        "description": "万籁俱寂中的精致十八世纪黄铜怀表沉稳滴答与黄铜罗盘表盖清脆一合（良知校准声音锚点）",
        "sfx_prompt": (
            "Intimate close-up foley of a fine antique 18th-century brass pocket watch ticking calmly in a hushed candlelit room, "
            "followed by the crisp metallic click of a hinged brass compass lid closing cleanly on oak wood, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "kirkcaldy_hearth_tea_pour": {
        "name": "柯科迪海风暮色壁炉与清茶倾注",
        "description": "苏格兰东岸柯科迪小镇海风拂窗、壁炉余烬温润微响与滚烫清茶缓缓注入瓷杯的宁静暖意",
        "sfx_prompt": (
            "Serene Scottish coastal twilight breeze outside a warm stone cottage window in Kirkcaldy, "
            "soft hearth embers settling quietly, and hot amber tea pouring smoothly from a ceramic pot into a warm cup, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
