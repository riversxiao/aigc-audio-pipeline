"""Canonical 19th-Century European Romantic & Gothic Revenge OST Palette & Sonic Motifs for《基督山伯爵·伊夫堡复仇广播剧》.

Sharing 6 canonical `bgm_prompt` strings across acts across all Season-1 episodes:
1. Crafts an unmistakable Alexandre Dumas 1815–1838 Mediterranean-to-Paris cinematic soundscape
   (lyrical cello, Mediterranean classical guitar, baroque harpsichord intrigue, gothic dungeon contrabass,
   soaring romantic strings, and sharp aristocratic Parisian vengeance ostinatos).
2. Guarantees 100% SHA-256 stem-cache reuse in `ACE-Step 1.5 XL` on Colab 96GB G4 while strictly
   forbidding modern pop beats, synth trap, or singing vocals.
"""

from __future__ import annotations

MONTE_CRISTO_OST: dict[str, str] = {
    "marseille_sunlit_harbor": (
        "Warm lyrical 19th-century Mediterranean romantic chamber score, expressive solo cello, "
        "gentle classical nylon acoustic guitar arpeggios and sunlit European strings evoking Marseille harbor and young love, "
        "purely instrumental orchestral chamber music, no drums, no modern beat, no singing, no vocals"
    ),
    "conspiracy_tavern_shadow": (
        "Tense 19th-century European baroque intrigue chamber score, dark plucked harpsichord, "
        "brooding pizzicato low strings and ominous solo viola evoking secret betrayal and anonymous denunciation, "
        "purely instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "chateau_dif_abyss": (
        "Bleak suffocating gothic dungeon chamber score, desolate low bowed contrabass, "
        "mournful lone cello lament and distant cavernous low organ pedal point evoking fourteen years in Chateau d'If, "
        "purely instrumental, no drums, no modern beat, no singing, no vocals"
    ),
    "treasure_rebirth_overture": (
        "Sweeping triumphant 19th-century European romantic orchestral film score, soaring passionate strings, "
        "noble French horn swell and glistening harp arpeggios evoking the Monte Cristo treasure cave and rebirth, "
        "purely instrumental orchestral music, no modern pop beat, no singing, no vocals"
    ),
    "paris_venetian_revenge": (
        "Razor-sharp aristocratic Parisian gothic suspense score, driving minor-key cello ostinato, "
        "icy dramatic chamber strings, dark harpsichord and restrained orchestral timpani pulse of calculating vengeance, "
        "purely instrumental film score, no modern synth trap, no singing, no vocals"
    ),
    "wait_and_hope_epilogue": (
        "Profound bittersweet 19th-century romantic orchestral epilogue, tender reflective solo piano, "
        "warm soaring cello melody and serene sea-breeze string swells evoking forgiveness, reunion and wait and hope, "
        "purely acoustic instrumental, no drums, no singing, no vocals"
    ),
}

MONTE_CRISTO_SONIC_MOTIFS: dict[str, dict[str, object]] = {
    "marseille_harbor_bell": {
        "name": "马赛港海鸥与法老号铜钟",
        "description": "阳光地中海海浪拍打木码头、三桅商船帆索绷紧吱呀与清脆船头铜钟声",
        "sfx_prompt": (
            "Bright sunlit Mediterranean harbor waves lapping against wooden piers, distant seagulls calling, "
            "taut wooden sailing ship rigging creaking and a crisp brass ship bell ringing twice, pure foley, no human voice"
        ),
        "duration_seconds": 3.2,
    },
    "chateau_dif_iron_door": {
        "name": "伊夫堡地牢沉重铁门落锁",
        "description": "湿冷石堡海风呼啸中沉重铁闸门轰然闭合与厚重铁栓落锁的冰冷回响",
        "sfx_prompt": (
            "Heavy medieval stone dungeon iron-bound prison door slamming shut with echoing metallic latch clank "
            "and thick rusted iron key turning inside a massive lock over cold distant sea wind, pure foley, no human voice"
        ),
        "duration_seconds": 3.0,
    },
    "faria_wall_tap": {
        "name": "法利亚神父地牢三声凿石暗号",
        "description": "漆黑地牢寂静中，厚石墙深处传来克制清晰的三声铁凿刮石暗号",
        "sfx_prompt": (
            "Tense dead silence inside a damp stone dungeon broken by three deliberate muffled metallic scraping taps "
            "coming from deep inside a thick limestone wall followed by tiny falling gravel dust, pure foley, no human voice"
        ),
        "duration_seconds": 2.8,
    },
    "midnight_sea_plunge": {
        "name": "装尸麻袋铁球坠入暴风海浪",
        "description": "雷鸣暴雨夜里重物拖着铁链坠入漆黑地中海怒涛的巨大落水炸响与翻涌波涛",
        "sfx_prompt": (
            "Violent midnight thunderstorm over crashing Mediterranean cliff waves followed by a heavy weighted canvas sack "
            "plunging dramatically into deep dark ocean water with thunderous splash and churning surf, pure foley, no human voice"
        ),
        "duration_seconds": 3.6,
    },
    "paris_salon_clock_glass": {
        "name": "巴黎贵族沙龙座钟与水晶杯轻碰",
        "description": "十九世纪巴黎烛光沙龙古董金摆钟清越滴答与水晶高脚杯优雅轻碰",
        "sfx_prompt": (
            "Refined 19th-century Parisian aristocratic salon ambience with antique gilded mantel clock ticking softly "
            "and two fine crystal champagne glasses clinking delicately beside crackling hearth fire, pure foley, no human voice"
        ),
        "duration_seconds": 2.6,
    },
    "duel_pistol_cock": {
        "name": "黎明决斗手枪击锤上膛",
        "description": "寒雾林间寂静中，古典精致决斗手枪金属击锤清脆上膛的致命咔哒声",
        "sfx_prompt": (
            "Chilling crisp close-up mechanical double click of a 19th-century antique dueling pistol hammer "
            "being cocked sharply amidst quiet misty dawn forest breeze, pure foley, no human voice"
        ),
        "duration_seconds": 2.2,
    },
}
