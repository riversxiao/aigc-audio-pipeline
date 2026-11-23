"""Canonical Cyclical Macro Documentary Acoustic OST Palette & Sonic Motifs
for《经济机器怎么转：〈原则与大债务危机〉周期剧》.

All 5 canonical OST themes strictly match `_ECON_FINANCE_BGM_PRESETS["debt_cycle_machine"]`:
steady cyclical macro documentary minimalist piano arpeggio, warm cello and subtle chamber string swell —
purely acoustic instrumental, zero pop drums, zero modern EDM beat, zero singing vocals, zero Chinese
xianxia instruments — guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

DEBT_CYCLE_OST: dict[str, str] = {
    "clockwork_macro_pulse": (
        "Steady cyclical macro documentary minimalist piano arpeggio, warm sustained cello and subtle chamber "
        "string swell evoking precision brass clockwork gears and long-horizon economic rhythm, purely acoustic "
        "instrumental, no pop drums, no modern EDM beat, no singing, no vocals"
    ),
    "credit_spring_expansion": (
        "Buoyant cyclical macro documentary minimalist felt piano arpeggio, crisp rhythmic pizzicato cello "
        "and rising warm chamber string swell evoking brisk credit expansion, busy industrial workshops and "
        "expanding household incomes, purely acoustic instrumental, no pop drums, no modern EDM beat, "
        "no singing, no vocals"
    ),
    "central_bank_tug_of_war": (
        "Taut analytical macro documentary minimalist piano arpeggio ostinato, insistent bowed cello, incisive "
        "viola counterpoint and subtle tense chamber string swell evoking central bank interest-rate tightening "
        "and credit debates, purely acoustic instrumental, no pop drums, no modern EDM beat, no singing, no vocals"
    ),
    "deleveraging_winter_elegy": (
        "Solemn reflective macro documentary minimalist sparse piano arpeggio, deep expressive solo cello and "
        "hushed dark chamber string swell evoking zero-interest-rate liquidity trap, deflationary depression "
        "and historic debt crisis turning points, purely acoustic instrumental, no pop drums, no modern EDM beat, "
        "no singing, no vocals"
    ),
    "all_weather_horizon": (
        "Luminous balanced macro documentary minimalist flowing piano arpeggio, warm singing cello and gentle "
        "uplifting chamber string swell evoking beautiful deleveraging harmony, steady productivity and timeless "
        "cross-cycle resilience, purely acoustic instrumental, no pop drums, no modern EDM beat, no singing, no vocals"
    ),
}

DEBT_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "brass_clockwork_gears": {
        "name": "滨江书房黄铜机械齿轮钟稳健啮合与钟摆滴答",
        "description": "精密黄铜三层机械齿轮平稳咬合旋转、清脆擒纵机构滴答与沉稳铜摆轻荡的周期母题",
        "sfx_prompt": (
            "Crisp close-up mechanical foley of an antique exposed brass clockwork gear machine turning smoothly "
            "with interlocking brass cogwheels clicking and a steady resonant pendulum ticking on a wooden study "
            "desk, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "macro_warroom_rain": {
        "name": "滨江金融区高窗夜雨、暖灯瓷杯与图表翻页",
        "description": "金融区高大拱窗外细雨轻洒、温热陶瓷茶杯轻落红木桌面与厚重宏观周期报表翻页沙沙声",
        "sfx_prompt": (
            "Warm quiet evening study overlooking a rainy city skyline with soft rain tapping arched glass windows, "
            "a porcelain tea cup gently set onto a mahogany table, and crisp heavy chart pages turning, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.9,
    },
    "bank_vault_credit_stamp": {
        "name": "商业银行授信钢印落章、键盘敲击放款与金库门响",
        "description": "银行信贷审批台利落敲击键盘、沉实金属授信印章啪然落纸与远处厚重金库钢门轻闭",
        "sfx_prompt": (
            "Crisp commercial bank credit desk foley with brisk keyboard typing followed by a firm heavy brass "
            "approval stamp pressing onto paper documents and a distant solid steel vault latch clicking shut, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "factory_cnc_floor": {
        "name": "长三角精密五金厂数控机床稳健运转与游标卡尺",
        "description": "老陈精密加工车间数控主轴平稳低鸣、金属精密零件轻碰工作台与出货联单撕页声",
        "sfx_prompt": (
            "Grounded industrial workshop ambience of precision CNC lathe spindles humming steadily in the "
            "background with stainless steel calipers clinking onto a metal workbench and a paper order slip "
            "tearing cleanly, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "kitchen_ledger_abacus": {
        "name": "城市家庭暖灯饭桌账本翻页与计算器按键",
        "description": "许姐餐桌旁瓷碗轻落、塑料按键计算器哒哒连敲清账与圆珠笔在家庭账本上沙沙划勾",
        "sfx_prompt": (
            "Warm domestic kitchen table foley with a porcelain bowl set down gently followed by crisp desktop "
            "calculator keys tapping briskly and a ballpoint pen scratching figures across a household ledger "
            "notebook, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "central_bank_press_bell": {
        "name": "央行议息大厅玻璃杯轻放、决议卷宗合拢与远钟低鸣",
        "description": "肃穆议息长桌厚重皮面决议卷宗啪然合拢、玻璃水杯轻叩桌面与窗外金融区钟楼沉缓钟响",
        "sfx_prompt": (
            "Hushed stately central bank conference hall foley with a heavy leather policy binder closing firmly "
            "on a polished table, a glass tumbler tapped softly, and a distant deep city clocktower bell tolling "
            "once, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
