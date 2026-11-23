"""Canonical Grand Historical Documentary Pure-Acoustic OST Palette & Sonic Motifs
for《国运的开关：〈为什么国家会失败〉制度史剧》.

All 5 canonical OST themes are strictly pure-acoustic grand historical documentary cinematic
chamber strings, warm French horn swells & deep expressive cello (NO pop drums, NO modern
electronic synth beats, NO vocals or singing, NO Chinese instruments) — guaranteeing 100%
SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

WHY_NATIONS_FAIL_OST: dict[str, str] = {
    "border_town_overture": (
        "Grand historical documentary cinematic chamber strings, warm French horn swell and deep expressive cello "
        "over sustained contrabass pedal tones evoking sweeping borderlands and centuries of diverging national fate, "
        "purely acoustic orchestral chamber instrumental, no pop drums, no percussion, no vocals, no singing, "
        "no Chinese instruments"
    ),
    "venice_canal_prosperity": (
        "Luminous historical documentary cinematic chamber strings, bright lyrical violin and viola interplay, "
        "warm French horn harmonic bloom, delicate acoustic harp arpeggios and resonant deep cello evoking sunlit "
        "medieval Venice canals, bustling maritime contracts and open commerce, purely acoustic orchestral chamber "
        "instrumental, no pop drums, no percussion, no vocals, no singing, no Chinese instruments"
    ),
    "royal_charter_clash": (
        "Taut dramatic historical documentary cinematic chamber strings, urgent low cello ostinato, incisive bowed "
        "viola counter-melody and dark brooding French horn swells evoking Tudor royal courts, oligarchic council "
        "debates and clashes over monopoly charters, purely acoustic orchestral chamber instrumental, no pop drums, "
        "no percussion, no electronic synth, no vocals, no singing, no Chinese instruments"
    ),
    "industrial_spark_1688": (
        "Driving purposeful historical documentary cinematic chamber strings, brisk rhythmic spiccato violins, "
        "propulsive deep cello pulse and soaring warm French horn chords evoking 1688 Westminster constitutional "
        "breakthroughs, workshops awakening and the dawn of the Industrial Revolution, purely acoustic orchestral "
        "chamber instrumental, no pop drums, no drum kit, no vocals, no singing, no Chinese instruments"
    ),
    "turning_points_of_nations": (
        "Solemn expansive historical documentary cinematic chamber strings, rich elegiac solo cello theme answered "
        "by majestic warm French horn swells and luminous chamber ensemble harmonies evoking five centuries of "
        "institutional turning points and enduring civic wisdom, purely acoustic orchestral chamber instrumental, "
        "no pop drums, no percussion, no vocals, no singing, no Chinese instruments"
    ),
}

NATIONS_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "border_fence_wind": {
        "name": "边境铁丝网荒漠风声与双城街道反差",
        "description": "干热荒漠风掠过边境金属铁丝网轻吟，远方一边是沥青路平顺车流、另一边是土路木车颠簸",
        "sfx_prompt": (
            "Dry desert wind humming across a taut metallic border wire fence separating a smooth paved town street "
            "with gentle passing traffic from a dusty unpaved lane with rattling cart wheels, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "archive_map_unroll": {
        "name": "历史档案室羊皮古地图摊开与黄铜放大镜",
        "description": "厚重羊皮世界地图在深色木桌上舒展铺开，黄铜放大镜轻落桌面，钢笔尖在史料笔记上沙沙划过",
        "sfx_prompt": (
            "Warm hushed historical archive study ambience as a heavy parchment world map unrolls across a dark "
            "mahogany table, a brass magnifying glass sets down softly, and a fountain pen scratches ledger paper, "
            "pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "knitting_frame_clack": {
        "name": "1589年威廉木制手摇织袜机精巧机括声",
        "description": "十六世纪木工坊里手摇织袜机齿轮咔哒咬合、脚踏木板规律起落与钢针穿引毛线的清脆律动",
        "sfx_prompt": (
            "Intricate sixteenth-century wooden hand-operated stocking knitting frame gears clicking crisply, "
            "wooden treadle pumping rhythmically, and fine steel needles interlacing wool yarn inside a quiet "
            "timber workshop, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "venice_canal_galleon": {
        "name": "威尼斯大运河木船摇橹与海港货绳吱呀",
        "description": "亚得里亚海运河水波轻拍木质商船船身、木桨有节奏划水与麻绳在橡木系缆桩上绷紧吱呀",
        "sfx_prompt": (
            "Gentle Adriatic lagoon water lapping against weathered wooden merchant galley hulls along a Venice "
            "canal, rhythmic wooden oar strokes dipping smoothly, and taut hemp rigging creaking against oak harbor "
            "bollards, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "wax_seal_charter": {
        "name": "皇家特许状火漆封蜡压印与元老院重门闭合",
        "description": "厚羊皮纸敕令摊平、滚烫红火漆滴落、黄铜印章重重压下，随即厚重雕花橡木议事大门轰然闭锁",
        "sfx_prompt": (
            "Heavy parchment royal charter unfolding crisply, molten sealing wax dripping softly, a solid brass "
            "signet stamp pressing firmly into warm wax, followed by a heavy carved oak council hall door shutting "
            "decisively, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "parliament_gavel_loom": {
        "name": "1688威斯敏斯特议会木槌与早期纺机律动",
        "description": "挑高议会大厅内橡木议事槌清脆落定，随即过渡为英国早期机械纺织机规律有力的齿轮轰鸣与炭火轻响",
        "sfx_prompt": (
            "Resonant oak gavel striking a wooden sounding block inside a tall timber-vaulted parliamentary hall "
            "transitioning smoothly into the brisk rhythmic clatter of an early British mechanical spinning loom "
            "and warm coal-hearth crackle, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
}
