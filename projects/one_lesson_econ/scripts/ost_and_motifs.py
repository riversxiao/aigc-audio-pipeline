"""Canonical Pure-Acoustic Modern Documentary OST Palette & Sonic Motifs
for《一课经济学剧场：别只看眼前那一步》.

All 5 canonical OST themes are strictly pure acoustic modern documentary chamber music
(warm felt piano, upright double bass, gentle nylon/steel acoustic guitar & subtle chamber strings;
NO loud drums, NO percussion, NO electronic synth beats, NO singing/vocals, NO Chinese instruments) —
guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

ONE_LESSON_ECON_OST: dict[str, str] = {
    "city_cafe_clarity": (
        "Warm modern documentary acoustic chamber score, intimate felt upright piano voicings, "
        "gentle walking upright double bass and warm fingerpicked acoustic guitar evoking a sunlit "
        "urban podcast cafe studio and lucid everyday economic clarity, purely acoustic instrumental, "
        "no loud drums, no percussion, no synth, no singing, no vocals, no Chinese instruments"
    ),
    "workshop_gears_motion": (
        "Bright nimble modern documentary acoustic chamber underscore, crisp rhythmic acoustic guitar "
        "arpeggios, light felt piano pulse, playful plucked upright double bass and subtle chamber strings "
        "evoking bustling workshops, smart textile looms and everyday urban industry, purely acoustic instrumental, "
        "no loud drums, no percussion, no electronic beat, no singing, no vocals, no Chinese instruments"
    ),
    "policy_debate_pulse": (
        "Taut articulate modern documentary intellectual debate chamber score, insistent plucked upright "
        "double bass ostinato, crisp staccato felt piano chords and lean acoustic guitar counterpoint "
        "evoking lively urban policy debates and tracing second-order economic consequences, purely acoustic "
        "instrumental, no loud drums, no percussion, no synth, no singing, no vocals, no Chinese instruments"
    ),
    "night_street_reflection": (
        "Reflective warm-melancholic modern documentary chamber cue, sparse resonant felt piano melody, "
        "deep sustained upright double bass and soft lyrical acoustic guitar chords evoking quiet evening "
        "city alleys, old apartment blocks and hidden costs paid by ordinary families, purely acoustic "
        "instrumental, no loud drums, no percussion, no synth, no singing, no vocals, no Chinese instruments"
    ),
    "morning_horizon_warmth": (
        "Hopeful luminous modern documentary chamber epilogue, flowing warm felt piano arpeggios, "
        "gentle singing acoustic cello, bright fingerpicked acoustic guitar and steady upright double bass "
        "evoking a clear city morning horizon and lasting second-order common sense, purely acoustic "
        "instrumental, no loud drums, no percussion, no synth, no singing, no vocals, no Chinese instruments"
    ),
}

ONE_LESSON_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "cafe_chalkboard_cup": {
        "name": "梧桐巷播客录音室黑板粉笔算账与陶瓷杯",
        "description": "白色粉笔在木框黑板上利落连线写字、温热咖啡陶瓷杯轻落原木桌与笔记本翻页",
        "sfx_prompt": (
            "Warm intimate modern urban podcast cafe study ambience with crisp chalk drawing quick connecting "
            "lines on a matte blackboard, a warm ceramic mug gently placed onto an oak table, and notebook "
            "paper turning softly, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "broken_glass_sweep": {
        "name": "临街面馆橱窗玻璃碎裂与扫帚清扫",
        "description": "街角临街大块玻璃清脆碎裂落地，随后竹扫帚缓缓将碎玻璃渣拢进铁簸箕的清脆沙沙声",
        "sfx_prompt": (
            "Crisp impact of a street-front shop window pane shattering cleanly onto a stone sidewalk followed "
            "by steady bristle broom strokes sweeping glass shards into a metal dustpan, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "hardware_workshop_hum": {
        "name": "老赵五金厂精密车床与金属工件轻响",
        "description": "中小型五金加工车间车床电机平稳低鸣、卡尺轻合与金属零件落入木盘的清脆碰撞",
        "sfx_prompt": (
            "Steady rhythmic mechanical hum of a small modern metalworking lathe in a tidy hardware workshop "
            "followed by brass calipers closing lightly and precision steel bolts clinking into a wooden tray, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "old_apartment_keys": {
        "name": "老城区红砖楼防盗门与黄铜钥匙串",
        "description": "一串沉甸甸的黄铜钥匙哗啦轻响、插入老式铁门锁芯转动咔嗒与老旧木门轻微吱呀推开",
        "sfx_prompt": (
            "Heavy bunch of vintage brass apartment keys jingling closely, sliding into a worn iron lock "
            "cylinder with a firm mechanical click, and an older wooden apartment door swinging open with a "
            "gentle creak, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "weaving_loom_parcel": {
        "name": "智能织机律动切换电商打包胶带撕拉",
        "description": "现代化自动织机清脆有节奏的梭织声平稳过渡到电商打包台透明胶带利落拉扯封箱",
        "sfx_prompt": (
            "Clean rhythmic mechanical cadence of an automated modern textile loom weaving smoothly "
            "transitioning into crisp packing tape zipping cleanly across a cardboard e-commerce parcel box, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "bakery_register_coins": {
        "name": "街口面包坊烘焙烤箱与收银抽屉账本",
        "description": "清晨面包坊金属烤盘轻落不锈钢台面、收银机钱箱清脆叮铃弹开与纸质账本哗啦翻页",
        "sfx_prompt": (
            "Cozy morning neighborhood bakery foley with a warm metal baking tray set softly onto a counter, "
            "a crisp cash drawer bell chiming with coins settling, and thick ledger pages flipping briskly, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
