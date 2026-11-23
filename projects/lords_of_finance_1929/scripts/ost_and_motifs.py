"""Canonical 1929 Interwar European Tragic Chamber Orchestra OST Palette & Sonic Motifs
for《1929黄金镣铐：〈金融之王〉四央行行长博弈》.

All 5 canonical OST themes strictly match `_ECON_FINANCE_BGM_PRESETS["lords_of_finance_1929"]`
(1929 interwar European tragic chamber orchestra, somber solo cello, dark stately grand piano,
and restrained string quartet — purely acoustic instrumental, zero modern drums, zero electronic synths,
zero singing/vocals, zero Chinese xianxia instruments), guaranteeing 100% SHA-256 stem-cache reuse
across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

LORDS_FINANCE_OST: dict[str, str] = {
    "golden_fetters_overture": (
        "1929 interwar European tragic chamber orchestra, somber solo cello melody, dark stately grand piano chords "
        "and restrained string quartet evoking foggy Threadneedle Street gold vaults and the solemn weight of "
        "postwar central banking, purely acoustic instrumental, no modern drums, no percussion, no singing, no vocals"
    ),
    "weimar_press_tension": (
        "Tense 1923 interwar European tragic chamber orchestra thriller score, urgent pulsing pizzicato cello and "
        "double bass ostinato, dark stately grand piano staccato motifs and anxious restrained string quartet "
        "evoking Berlin banknote presses racing toward hyperinflation and frantic Wall Street fever, "
        "purely acoustic instrumental, no modern drums, no electronic synth, no singing, no vocals"
    ),
    "four_capitals_duel": (
        "Articulate taut 1920s interwar European chamber orchestra diplomatic duel, crisp interplay between dark "
        "stately grand piano chords, incisive somber solo cello and restrained string quartet counterpoints "
        "evoking high-stakes central bank negotiations across London, Paris, Berlin and New York, "
        "purely acoustic instrumental, no modern drums, no percussion, no singing, no vocals"
    ),
    "crash_winter_elegy": (
        "Deeply mournful 1929 interwar European tragic chamber orchestra elegy, haunting sustained somber solo "
        "cello lament, sparse dark stately grand piano harmonies and hushed weeping string quartet evoking "
        "freezing bank runs, shuttered mines and global deflationary paralysis, purely acoustic instrumental, "
        "no modern drums, no percussion, no singing, no vocals"
    ),
    "unbound_gold_epilogue": (
        "Reflective dignified 1933 interwar European chamber orchestra epilogue, warm resolving solo cello theme, "
        "stately grand piano arpeggios and luminous restrained string quartet rising gently from gloom into "
        "hard-won monetary clarity after breaking golden fetters, purely acoustic instrumental, "
        "no modern drums, no percussion, no singing, no vocals"
    ),
}

LORDS_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "gold_vault_chains": {
        "name": "伦敦针线街地下金库铁门与金砖锁链",
        "description": "英格兰银行厚重铸铁金库大门缓缓合拢，沉甸甸的金砖落上木车并伴随黄铜铁链清冷碰响",
        "sfx_prompt": (
            "Heavy iron Bank of England underground vault door grinding shut in a stone corridor followed by "
            "heavy gold bullion bars thudding onto an oak trolley and brass chains clinking solemnly, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "weimar_printing_press": {
        "name": "1923柏林印钞厂昼夜轰鸣与成捆钞票跌落",
        "description": "魏玛柏林工业轮转印钞机疯狂高速运转，刚裁切好的厚厚纸币成叠拍落木台",
        "sfx_prompt": (
            "Relentless fast mechanical clatter of a 1923 industrial rotary banknote printing press running "
            "at fever pitch with thick freshly cut stacks of paper currency slapping rapidly onto a wooden "
            "sorting table, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "transatlantic_telegraph": {
        "name": "跨大西洋海底电报机哒哒发报与火漆封函",
        "description": "红木央行书房内黄铜电报键急促哒哒拍击，窄窄电报纸带滑出，火漆印章沉稳盖上密函",
        "sfx_prompt": (
            "Crisp 1920s brass Morse telegraph key tapping urgently inside a wood-paneled central bank study "
            "followed by a paper telegram ribbon clicking out and a heavy wax seal stamping parchment, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "coal_mine_whistle": {
        "name": "1926威尔士煤矿停工铁闸落锁与寒风",
        "description": "远方老矿井低沉汽笛渐散，沉重铁矿门在寒风中合拢并咔嗒扣上粗重铁锁",
        "sfx_prompt": (
            "Somber distant steam whistle fading over a quiet 1926 Welsh coal colliery as heavy steel mine "
            "gates swing shut with an iron padlock clanking against cold winter wind, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "wall_street_ticker_crash": {
        "name": "1929华尔街黄铜纸带行情机狂响与交易铜钟",
        "description": "玻璃罩下老式华尔街行情纸带机急促失控哒哒狂敲，随后交易所收盘铜钟震响、账纸散落桌面",
        "sfx_prompt": (
            "Frenzied 1929 mechanical brass stock ticker tape clattering wildly inside a glass dome "
            "culminating in a sharp resonant trading floor closing bell and thick ledger sheets scattering "
            "across oak, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "bank_run_iron_grille": {
        "name": "挤兑潮中银行大理石大厅铁栅门砰然紧闭",
        "description": "空旷大理石银行大厅里急促杂乱脚步声戛然而止，厚重锻铁柜台栅栏门猛然拉拢上栓",
        "sfx_prompt": (
            "Echoing hurried footsteps across a grand marble banking hall abruptly halted by a heavy "
            "wrought-iron teller grille sliding violently shut and brass bolts locking into place, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
}
