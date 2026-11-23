"""Canonical Pure-Acoustic Detective-Economics OST Palette & Sonic Motifs
for《激励侦探局：〈魔鬼经济学〉隐秘动机剧》.

All 5 canonical OST themes are strictly pure-acoustic detective-economics chamber scores
(curious playful pizzicato chamber strings, wooden marimba pulse, warm upright double bass
and crisp felt piano; ZERO loud rock drums, ZERO singing vocals, ZERO Chinese instruments) —
guaranteeing 100% SHA-256 stem-cache reuse across all Season-1 episodes on Colab 96GB G4.
"""

from __future__ import annotations

FREAKONOMICS_OST: dict[str, str] = {
    "incentive_detective_theme": (
        "Curious playful modern detective-economics chamber score, nimble pizzicato violin and cello strings, "
        "light wooden marimba pulse, warm walking upright double bass and crisp felt piano accents evoking a "
        "clever investigative studio full of clues and aha moments, purely acoustic instrumental, "
        "no loud rock drums, no singing, no vocals, no Chinese instruments"
    ),
    "data_clue_hunt": (
        "Brisk inquisitive investigative chamber underscore, articulate rhythmic wooden marimba patterns, "
        "plucked pizzicato strings, agile upright double bass ostinato and crisp staccato felt piano evoking "
        "rapid data crunching, spreadsheets and uncovering hidden statistical fingerprints, purely acoustic instrumental, "
        "no loud rock drums, no modern electronic beat, no singing, no vocals, no Chinese instruments"
    ),
    "agent_secret_parlor": (
        "Sly witty modern salon chamber score, smooth walking upright double bass, playful muted pizzicato strings, "
        "subtle dry wooden marimba touches and crisp wry felt piano chords evoking sharp broker banter, "
        "negotiation tables and hidden commission incentives, purely acoustic instrumental, "
        "no loud rock drums, no heavy percussion, no singing, no vocals, no Chinese instruments"
    ),
    "correlation_trap_puzzle": (
        "Intriguing mischievous puzzle chamber underscore, questioning off-beat pizzicato viola and cello motifs, "
        "delicate wooden marimba syncopation, thoughtful crisp felt piano voicings and warm plucked upright bass "
        "evoking untangling optical illusions, confounding variables and unintended backfires, purely acoustic instrumental, "
        "no loud rock drums, no singing, no vocals, no Chinese instruments"
    ),
    "eureka_case_closed": (
        "Bright uplifting warm investigative chamber epilogue, lyrical flowing felt piano arpeggios, "
        "gentle sparkling wooden marimba harmony, buoyant pizzicato and bowed chamber strings and warm upright bass "
        "evoking case-closed clarity and everyday human insight, purely acoustic instrumental, "
        "no loud rock drums, no heavy percussion, no singing, no vocals, no Chinese instruments"
    ),
}

FREAKONOMICS_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "detective_whiteboard_pin": {
        "name": "激励侦探局白板红线图钉与放大镜落桌",
        "description": "软木线索板清脆按入图钉、马克笔在玻璃白板画圈与黄铜放大镜干脆落于橡木桌面",
        "sfx_prompt": (
            "Crisp close-up foley of corkboard pins pressing firmly into a wooden evidence board, "
            "dry-erase marker circling a clue on glass whiteboard, and a brass magnifying glass set cleanly "
            "onto an oak desk, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "kindergarten_bell_gate": {
        "name": "傍晚幼儿园铁门铃声与电子接送打卡",
        "description": "暮色幼儿园铁门门闩轻响、前台黄铜按铃清脆一响与门口接送打卡机滴答提示音",
        "sfx_prompt": (
            "Gentle evening kindergarten iron gate latch clicking open, a bright reception desk bell tapping once, "
            "and a crisp electronic attendance chime in a quiet tiled lobby, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "data_terminal_clack": {
        "name": "侦探局机械键盘敲击与打印机吐出数据长纸",
        "description": "年轻研究员高速敲击机械键盘后，微型热敏图表打印机哒哒吐出长条数据纸并利落撕下",
        "sfx_prompt": (
            "Brisk rhythmic mechanical keyboard keystrokes followed by an office receipt-style data printer "
            "feeding out a long chart paper slip and tearing cleanly, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "broker_keys_contract": {
        "name": "房产中介钥匙串碰响与合同翻页拔笔帽",
        "description": "沉甸甸一串看房铁钥匙落在玻璃茶几上清脆作响，伴随精装楼书翻页与钢笔笔帽轻拔",
        "sfx_prompt": (
            "Jingle of a heavy steel real-estate key ring laid onto a glossy glass table followed by crisp "
            "glossy brochure pages flipping and a fountain pen uncapping smoothly, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "diner_teacup_abacus": {
        "name": "老王街角茶铺粗瓷沏茶与老式木算盘拨珠",
        "description": "暖水茶壶倾注热茶入厚瓷茶杯，紧接着老式红木算盘珠子噼啪利落拨响三下",
        "sfx_prompt": (
            "Warm ceramic teapot pouring hot tea into a thick stoneware cup on a wooden table followed by "
            "brisk wooden abacus beads clacking crisply in a cozy street-corner shop, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "case_file_stamp": {
        "name": "悬案卷宗合拢与红木结案章干脆落印",
        "description": "厚实牛皮纸案件卷宗利落合上拍桌，黄铜木柄结案印章沾墨清脆重落盖印",
        "sfx_prompt": (
            "Thick manila case folder snapping shut cleanly on a wooden desk followed by a heavy brass-and-wood "
            "stamp pressing crisply onto paper to close an investigation file, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
}
