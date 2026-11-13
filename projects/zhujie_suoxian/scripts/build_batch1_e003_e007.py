"""Build, validate, render, and archive Batch 1: Episodes E003–E007 (Chapters 3–7)."""

from __future__ import annotations

from pathlib import Path
import sys

SCRATCH_DIR = Path(__file__).resolve().parent
REPO_SRC = Path(__file__).resolve().parents[3] / "src"
for p in (str(REPO_SRC), str(SCRATCH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from aigc_audio_pipeline.models import VoiceCastingRegistry
from batch_runner import BASE_DIR, REGISTRY_PATH, SCRIPTS_DIR, render_and_archive_episode
from episode_compiler import compile_episode_cue_sheet, save_episode_scripts

SOURCE_DIR = BASE_DIR / "source_chapters"


def build_all_batch1() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E003 · 第3章 三步试墟界，残碑上的古引气篇 (62 paras, 12 quotes)
    # =========================================================================
    md_03 = SOURCE_DIR / "第03章_三步试墟界，残碑上的古引气篇.md"
    s03 = compile_episode_cue_sheet(
        episode_id="E003",
        chapter_number=3,
        source_md_path=md_03,
        source_rel_path=f"02_分章精修正文/{md_03.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_morning_funeral_bait",
                "start_p": 1,
                "title": "第一幕 · 晨雾赊麻布，垂死撒鱼饵",
                "bgm_prompt": "Mournful restrained ancient Chinese xiao flute and sparse guqin over cold misty morning alley, quiet sorrow masking deep calculation, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_xujie_three_tests",
                "start_p": 14,
                "title": "第二幕 · 三步试墟界，冻土焚红尘",
                "bgm_prompt": "Mysterious ancient Chinese dark ambient score, deep bronze resonance, ethereal bowed strings and subtle crystalline textures in a desolate spirit realm, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_blood_burning_stele",
                "start_p": 31,
                "title": "第三幕 · 残碑古篆字，燃血破三重",
                "bgm_prompt": "Rising intense Chinese xianxia martial score, solemn low war drums, taut pipa and surging strings of ancient bone-tempering power, instrumental only, no vocals",
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act4_mist_beast_stalker",
                "start_p": 49,
                "title": "第四幕 · 灰雾窥残蜥，三更夜枭来",
                "bgm_prompt": "Suspenseful nocturnal Chinese espionage thriller score, eerie sub-bass drone, tense pizzicato strings and distant night watch atmosphere, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[(15, 57, "mental_realm")],
        skip_onomatopoeia_paras={14, 46, 50},
        dialogue_specs=[
            {"match": "陆老哥，一大早买白麻布", "role_id": "weathered_elder_npc", "tags": "[softly]", "stability": 0.5, "note": "西街杂货铺老掌柜压低嗓音关切询问"},
            {"match": "昨夜苏家来退了亲", "role_id": "fu_bo", "tags": "[crying] [hoarsely]", "stability": 0.0, "note": "福伯泣声演戏做局，引暗桩入套"},
            {"match": "造孽啊，当年陆爷", "role_id": "weathered_elder_npc", "tags": "[sighs]", "stability": 0.5, "note": "老掌柜叹息赊布"},
            {"match": "多谢掌柜的", "role_id": "fu_bo", "tags": "[hoarsely]", "stability": 0.0, "note": "福伯深深弯腰致谢"},
            {"match": "外头的鱼饵已经撒下去了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "床帐内陆烬冷静推演裴玄度死命令"},
            {"match": "趁白昼他不敢贸然闯宅", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬沉入眉心识海"},
            {"match": "第一步验证清楚了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "墟界第一步验证：死物不入"},
            {"match": "大苍界的灵石里", "role_id": "lu_jin", "tags": "[whispers]", "stability": 0.0, "note": "发现灵石暗红杂质心头凛然"},
            {"match": "暂且叫这地方", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "正式命名墟界"},
            {"match": "凡诸界下民，降生即负血锁", "role_id": "ancient_construct_echo", "tags": "[dramatically]", "stability": 1.0, "space": "mental_realm", "note": "墨青残碑《燃血引气篇》总纲古篆震响"},
            {"match": "血锁？", "role_id": "lu_jin", "tags": "[gasps]", "stability": 0.0, "note": "陆烬瞳孔微缩"},
            {"match": "莫非我血脉深处看到的那条", "role_id": "lu_jin", "tags": "[whispers]", "stability": 0.0, "note": "印证心脏后方青铜锁影"},
        ],
        sfx_blueprint=[
            {"p": 2, "pos": "before", "slug": "wooden_door_abacus", "sfx_prompt": "Old weathered wooden side gate creaking open in damp morning fog followed by muffled wooden abacus beads clicking", "duration_seconds": 3.2, "gain_db": -1.5, "note": "偏门吱呀打开与西街算盘声"},
            {"p": 14, "pos": "before", "slug": "enter_xujie", "motif_id": "motif_xujie_gate", "gain_db": -0.5, "note": "嗡！神识降临方寸墟界"},
            {"p": 25, "pos": "before", "slug": "red_dust_burn", "sfx_prompt": "Fine mystical rain falling onto ancient rune-carved frozen earth with sharp searing hot iron sizzle burning away dark impurities", "duration_seconds": 3.0, "gain_db": 0.0, "note": "冻土道纹如烙铁烫雪焚毁暗红微尘"},
            {"p": 35, "pos": "before", "slug": "brush_frost_stele", "sfx_prompt": "Hand brushing dry frost dust off an ancient stone stele followed by a deep resonant bronze hum", "duration_seconds": 2.6, "gain_db": -0.5, "note": "拂去断碑暗红霜尘显露古篆"},
            {"p": 46, "pos": "before", "slug": "blood_qi_breakthrough", "sfx_prompt": "Explosive internal martial blood-qi surge like taut bowstrings snapping into resonant power, breaking through a cultivation barrier", "duration_seconds": 3.0, "gain_db": 1.0, "note": "轰！燃血真气逆冲踏入引气三重"},
            {"p": 50, "pos": "before", "slug": "beast_scales_bone_crunch", "sfx_prompt": "Heavy armored reptile claws scraping across frozen gravel in thick fog followed by a terrifying jaw snap crunching ancient bone", "duration_seconds": 4.0, "gain_db": 1.0, "note": "灰雾深处骨甲摩擦冻土与荒蜥嚼碎腿骨"},
            {"p": 60, "pos": "before", "slug": "third_watch_clapper", "sfx_prompt": "Distant Chinese night watchman striking hollow bamboo clapper three times in cold dark alley followed by a soft stealthy cloth rustle over leaves", "duration_seconds": 3.5, "gain_db": 0.0, "note": "三更梆子声远传，槐树暗桩夜枭翻墙"},
        ],
    )
    j03, m03 = save_episode_scripts(s03, SCRIPTS_DIR, registry)
    built.append(("E003", j03, m03))

    # =========================================================================
    # E004 · 第4章 请君入灵堂，一指毙暗桩 (61 paras, 14 quotes)
    # =========================================================================
    md_04 = SOURCE_DIR / "第04章_请君入灵堂，一指毙暗桩.md"
    s04 = compile_episode_cue_sheet(
        episode_id="E004",
        chapter_number=4,
        source_md_path=md_04,
        source_rel_path=f"02_分章精修正文/{md_04.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_midnight_infiltration",
                "start_p": 1,
                "title": "第一幕 · 三更潜灵堂，毒刺扎草人",
                "bgm_prompt": "Tense stealthy Chinese dark thriller score, sparse eerie guqin plucks, low breathy bamboo flute and creeping sub-bass pulse at midnight, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act2_lime_ambush_genelock",
                "start_p": 14,
                "title": "第二幕 · 石灰迷毒眼，燃血破死局",
                "bgm_prompt": "Ferocious close-quarters Chinese martial arts combat score, rapid taut percussion, razor-sharp bowed erhu accents and surging heartbeat tension, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_throat_pierce_aftermath",
                "start_p": 31,
                "title": "第三幕 · 一指透咽喉，枯井埋暗桩",
                "bgm_prompt": "Cold restrained post-battle Chinese chamber underscore, low brooding cello and sparse solemn guqin notes in a quiet courtyard, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_ninth_blood_seed_list",
                "start_p": 47,
                "title": "第四幕 · 靴底蜡封管，九号血引名",
                "bgm_prompt": "Chilling ominous Chinese mystery horror underscore, icy high string harmonics, deep hollow bronze drone and creeping dread, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        skip_onomatopoeia_paras={10, 15, 25, 30},
        dialogue_specs=[
            {"match": "到底是没熬过三更", "role_id": "zhao_kui", "tags": "[sarcastic] [whispers]", "stability": 0.0, "note": "赵魁贴窗冷笑"},
            {"match": "不好！", "role_id": "zhao_kui", "tags": "[gasps]", "stability": 0.0, "note": "扎中稻草人惊觉中计"},
            {"match": "找死的老狗", "role_id": "zhao_kui", "tags": "[angry] [shouting]", "stability": 0.0, "note": "赵魁被生石灰迷眼暴怒抓向屏风"},
            {"match": "没死？", "role_id": "zhao_kui", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "恶风压颈骇然回刺"},
            {"match": "方才那一瞬", "role_id": "lu_jin", "tags": "[hoarsely] [whispers]", "stability": 0.0, "note": "陆烬喘息回味燃血冲锁与肌肉本能"},
            {"match": "少、少主！", "role_id": "fu_bo", "tags": "[gasps]", "stability": 0.0, "note": "福伯提柴刀冲出屏风"},
            {"match": "这人……少主，这是引气五重的杀手啊", "role_id": "fu_bo", "tags": "[trembling] [whispers]", "stability": 0.0, "note": "福伯震惊颤声确认"},
            {"match": "不杀他，今夜横着出去的", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬冷冽回应"},
            {"match": "福伯，去把偏门白麻布摘下来一半", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬沉着布置毁尸灭迹"},
            {"match": "哎，老奴这就去办", "role_id": "fu_bo", "tags": "[hoarsely]", "stability": 0.0, "note": "福伯领命去后院"},
            {"match": "肆号血引，周氏周明", "role_id": "zhao_kui", "tags": "[coldly]", "stability": 0.0, "space": "memory_echo", "note": "油纸朱砂血引名单残响（肆号）"},
            {"match": "陆号血引，柳氏柳青禾", "role_id": "zhao_kui", "tags": "[coldly]", "stability": 0.0, "space": "memory_echo", "note": "油纸朱砂血引名单残响（陆号）"},
            {"match": "柒号血引，散修秦小石", "role_id": "zhao_kui", "tags": "[coldly]", "stability": 0.0, "space": "memory_echo", "note": "油纸朱砂血引名单残响（柒号）"},
            {"match": "玖号血引，陆氏陆烬", "role_id": "zhao_kui", "tags": "[coldly]", "stability": 0.0, "space": "memory_echo", "note": "油纸末尾未干新字（玖号陆烬！）"},
        ],
        sfx_blueprint=[
            {"p": 8, "pos": "before", "slug": "knife_door_latch", "sfx_prompt": "Thin metal blade quietly snapping a wooden door bolt in a dead-silent room followed by soft stealthy footsteps", "duration_seconds": 2.6, "gain_db": -1.0, "note": "短刺挑断门栓木销滑入卧房"},
            {"p": 10, "pos": "before", "slug": "stab_straw_dummy", "sfx_prompt": "Sharp iron spike stabbing hard into a bundle of wet cotton and dry straw with a muffled hollow thud", "duration_seconds": 2.0, "gain_db": 0.5, "note": "噗嗤！短刺扎中湿棉稻草人"},
            {"p": 15, "pos": "before", "slug": "lime_sack_burst", "sfx_prompt": "Taut hemp rope snapping overhead followed by a heavy burlap sack ripping open and ten pounds of fine lime powder cascading down", "duration_seconds": 3.0, "gain_db": 1.0, "note": "哗啦！麻袋撕裂生石灰毒雾倾泻"},
            {"p": 25, "pos": "before", "slug": "genelock_heartbeat_first", "motif_id": "motif_genelock_awaken", "gain_db": 1.5, "note": "咚！生死一瞬血锁发烫，基因锁心跳母题首现"},
            {"p": 30, "pos": "before", "slug": "finger_pierce_dagger_drop", "sfx_prompt": "Searing martial finger strike piercing flesh and snapping bone, followed by a metal dagger clattering onto stone bricks", "duration_seconds": 2.8, "gain_db": 1.5, "note": "噗！双指贯喉震断颈椎，短刺当啷落地"},
            {"p": 32, "pos": "before", "slug": "blade_draw_guard", "motif_id": "motif_broken_blade_wipe", "gain_db": 0.0, "note": "拔出玄铁断刀横在身前警戒"},
            {"p": 58, "pos": "before", "slug": "cold_wind_torn_window", "sfx_prompt": "Eerie freezing night wind whining softly through a torn paper window frame in an old ancestral hall", "duration_seconds": 3.2, "gain_db": -1.0, "note": "寒风吹过窗纸破洞呜呜低咽"},
        ],
    )
    j04, m04 = save_episode_scripts(s04, SCRIPTS_DIR, registry)
    built.append(("E004", j04, m04))

    # =========================================================================
    # E005 · 第5章 古骸兽皮卷，莫信头顶月 (56 paras, 20 quotes)
    # =========================================================================
    md_05 = SOURCE_DIR / "第05章_古骸兽皮卷，莫信头顶月.md"
    s05 = compile_episode_cue_sheet(
        episode_id="E005",
        chapter_number=5,
        source_md_path=md_05,
        source_rel_path=f"02_分章精修正文/{md_05.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_well_burial_and_resolve",
                "start_p": 1,
                "title": "第一幕 · 枯井封血灰，火焚血引名",
                "bgm_prompt": "Dark resolute ancient Chinese chamber score, low tense guqin and solemn cello drone before dawn, quiet determination in a besieged clan home, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_spirit_rain_fourth_layer",
                "start_p": 10,
                "title": "第二幕 · 灵雨焚暗尘，重登引气四",
                "bgm_prompt": "Driving Chinese xianxia cultivation breakthrough score, deep rhythmic bronze pulse and rising luminous strings, purifying spiritual rain, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_headless_outsider_scroll",
                "start_p": 19,
                "title": "第三幕 · 无头巡山客，莫信头顶月",
                "bgm_prompt": "Vast cosmic tragic ancient Chinese soundtrack, haunting desolate xiao flute, deep ominous bronze chimes and solemn strings revealing a world-cage secret, instrumental only, no vocals",
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act4_herb_embargo_iron_hat",
                "start_p": 49,
                "title": "第四幕 · 全城断汤药，黑笠赴鬼樊",
                "bgm_prompt": "Gritty determined Chinese martial arts underscore, taut pipa and low steady war drum pulse, lone bladesman stepping into underground black market, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        acoustic_ranges=[(19, 48, "mental_realm")],
        skip_onomatopoeia_paras={13},
        dialogue_specs=[
            {"match": "裴玄度自恃筑基真传", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬锁起传讯纸鹤冷静分析"},
            {"match": "赵魁不发传讯", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "锁定三日宝贵空窗期"},
            {"match": "少主，那名单上写着三日后", "role_id": "fu_bo", "tags": "[trembling] [hoarsely]", "stability": 0.0, "note": "福伯攥抹布担忧提议逃出南门"},
            {"match": "玄剑宗在城外赤松岭", "role_id": "fu_bo", "tags": "[desperately] [hoarsely]", "stability": 0.0, "note": "福伯忧心赤松岭筑基执事"},
            {"match": "逃不掉的", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬冷静否决盲目出逃"},
            {"match": "裴玄度前夜抽走了我一滴心头血", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "剖析气血追踪与四门眼线"},
            {"match": "他们以为我是躺在砧板上", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "note": "字字斩钉截铁反猎杀宣言"},
            {"match": "晚辈陆烬，误入前辈坐化之地", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬向无头古修恭敬抱拳行礼"},
            {"match": "吾本外界巡山客，误坠大苍饲笼", "role_id": "ancient_construct_echo", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "无头巡山客血书开篇惊雷十七字"},
            {"match": "大苍众生以为大地四极之外", "role_id": "ancient_construct_echo", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "揭穿血月实为巡天母锁阵眼"},
            {"match": "所谓九品灵脉，品阶越高", "role_id": "ancient_construct_echo", "tags": "[coldly]", "stability": 0.0, "space": "memory_echo", "note": "揭露九品灵脉皆是催熟血食良苗"},
            {"match": "生灵血肉本源深处，自有五重", "role_id": "ancient_construct_echo", "tags": "[dramatically]", "stability": 1.0, "space": "memory_echo", "note": "五重基因命锁与燃血醒觉真谛"},
            {"match": "惜吾坠界时道基已损", "role_id": "ancient_construct_echo", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "挥剑自斩首级遗言：切记莫信头顶月！"},
            {"match": "基因锁……燃血醒觉", "role_id": "lu_jin", "tags": "[whispers]", "stability": 0.0, "space": "mental_realm", "note": "陆烬反复咀嚼破局关键"},
            {"match": "少主，出事了！", "role_id": "fu_bo", "tags": "[desperately] [hoarsely]", "stability": 0.0, "note": "福伯拎空药篓满头大汗奔回"},
            {"match": "是苏家打过招呼了？", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "note": "陆烬眼神微冷"},
            {"match": "正是苏清寒的大哥苏牧！", "role_id": "fu_bo", "tags": "[angry] [hoarsely]", "stability": 0.0, "note": "福伯咬牙切齿道出苏牧封杀"},
            {"match": "老奴找相熟的药童偷偷打听了一句", "role_id": "fu_bo", "tags": "[hoarsely]", "stability": 0.0, "note": "全城药堂断药封锁"},
            {"match": "正经药堂不卖", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬取下黑铁斗笠"},
            {"match": "北渊城老运河地底的鬼樊楼", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "戴上黑纱斗笠动身鬼樊楼"},
        ],
        sfx_blueprint=[
            {"p": 2, "pos": "before", "slug": "stone_mill_seal_well", "sfx_prompt": "Heavy stone millstones grinding shut over an old dry well mouth followed by a splash of water on dry leaves in quiet night", "duration_seconds": 3.4, "gain_db": -0.5, "note": "两扇废弃石磨压死枯井口"},
            {"p": 8, "pos": "before", "slug": "burn_oil_paper", "sfx_prompt": "Flint fire-striker spark igniting oiled paper, crisp flame crackling briefly into ashes in a brass basin", "duration_seconds": 2.8, "gain_db": 0.0, "note": "火折子点燃防水油纸烧毁名单"},
            {"p": 13, "pos": "before", "slug": "four_stones_shatter_surge", "sfx_prompt": "Torrential spiritual rain roaring inside an energy vortex followed by four crystal stones cracking into powder and bones popping", "duration_seconds": 3.5, "gain_db": 1.0, "note": "轰隆！四枚灵石碎粉，踏入引气四重"},
            {"p": 19, "pos": "before", "slug": "xujie_expand_130", "motif_id": "motif_xujie_gate", "gain_db": -0.5, "note": "神识降临扩张至一百三十丈的方寸墟界"},
            {"p": 28, "pos": "before", "slug": "unroll_beast_parchment", "sfx_prompt": "Ancient stiff leather parchment scroll slowly unrolling against dry stone in a silent cavern with a deep ominous sub-bass rumble", "duration_seconds": 3.0, "gain_db": 0.5, "note": "抽出无头古修指骨下的暗金兽皮卷"},
            {"p": 54, "pos": "before", "slug": "dust_off_iron_hat", "sfx_prompt": "Hand brushing dust off a dark iron conical hat with black silk veil rustling softly", "duration_seconds": 2.4, "gain_db": 0.0, "note": "取下黑铁帷帽斗笠掸去积灰"},
        ],
    )
    j05, m05 = save_episode_scripts(s05, SCRIPTS_DIR, registry)
    built.append(("E005", j05, m05))

    # =========================================================================
    # E006 · 第6章 鬼樊楼试水，瞎眼鉴药人 (47 paras, 17 quotes)
    # =========================================================================
    md_06 = SOURCE_DIR / "第06章_鬼樊楼试水，瞎眼鉴药人.md"
    s06 = compile_episode_cue_sheet(
        episode_id="E006",
        chapter_number=6,
        source_md_path=md_06,
        source_rel_path=f"02_分章精修正文/{md_06.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_canal_gate_ghost_market",
                "start_p": 1,
                "title": "第一幕 · 古河叩鬼脸，骨灯映暗市",
                "bgm_prompt": "Shadowy subterranean Chinese black-market soundtrack, low eerie bassoon-like Sheng drone, muted plucked strings and mysterious lantern-lit cavern atmosphere, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_blind_appraiser_salve",
                "start_p": 13,
                "title": "第二幕 · 竹刀试黑膏，三息敛金膜",
                "bgm_prompt": "Quirky tense ancient Chinese chamber underscore, dry sparse pipa plucks, subtle bamboo percussion and intrigue between disguised alchemist and blind master, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_moon_gaze_taboo",
                "start_p": 25,
                "title": "第三幕 · 冰盒换蝎心，莫看天上娘",
                "bgm_prompt": "Eerie chilling ancient Chinese folkloric dark ambient, ghostly xiao harmonics, cold sub-bass drone and whispered taboo of the crimson sky, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_baoruige_eavesdrop",
                "start_p": 37,
                "title": "第四幕 · 暗巷闻毒计，祠堂作坟场",
                "bgm_prompt": "Cold nocturnal Chinese conspiracy thriller score, taut low strings, sharp icy metallic accents and rising murderous resolve, instrumental only, no vocals",
                "bgm_duration_s": 65.0,
            },
        ],
        dialogue_specs=[
            {"match": "入楼规矩，一粒碎灵砂", "role_id": "male_guard_captain", "tags": "[dismissive]", "stability": 0.5, "note": "鬼樊楼铁栅门刺青壮汉懒洋洋报规矩"},
            {"match": "老山白芨、陈年血竭", "role_id": "chu_xiazi", "tags": "[sarcastic]", "stability": 0.0, "note": "褚瞎子抽鼻识破凡药底料"},
            {"match": "褚先生不妨试试药力再开价", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬压粗喉骨伪装中年药农平淡开口"},
            {"match": "嘿，脾气倒不小", "role_id": "chu_xiazi", "tags": "[sarcastic]", "stability": 0.0, "note": "褚瞎子怪笑划破手背试药"},
            {"match": "怪事……奇了怪了", "role_id": "chu_xiazi", "tags": "[whispers]", "stability": 0.0, "note": "褚瞎子震惊于清润如初雪的药引"},
            {"match": "家传残方，偶然熬成六瓶", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬滴水不漏不接话茬"},
            {"match": "六瓶全归褚先生，我要一枚活剖", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "报出三年赤尾妖蝎心与铁背熊精肉需求"},
            {"match": "赤尾妖蝎心店里恰好昨天刚收了一枚极品", "role_id": "chu_xiazi", "tags": "[calmly]", "stability": 0.0, "note": "褚瞎子高价全收倒找十枚灵石"},
            {"match": "可以。若褚先生销路稳当", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "定下初一十五长线供货"},
            {"match": "痛快！", "role_id": "chu_xiazi", "tags": "[laughs]", "stability": 0.0, "note": "褚瞎子抚掌一笑"},
            {"match": "拿着这乌木牌", "role_id": "chu_xiazi", "tags": "[softly]", "stability": 0.0, "note": "赠九字乌木小牌走暗门"},
            {"match": "客人这药引子干净得不像这世道的东西", "role_id": "chu_xiazi", "tags": "[whispers]", "stability": 0.0, "note": "褚瞎子幽幽道出二十年前月食夜窥天烧瞎双眼"},
            {"match": "好东西自己捂严实了用", "role_id": "chu_xiazi", "tags": "[whispers]", "stability": 0.0, "note": "惊悚忠告：天上的娘娘看不得底下人睁眼"},
            {"match": "多谢褚先生提点", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬颔首离去"},
            {"match": "周执事尽管放心，我家小姐今早", "role_id": "female_maid_npc", "tags": "[softly]", "stability": 0.5, "note": "宝瑞阁侧门丫鬟春桃得意交账"},
            {"match": "裴师兄对苏师妹果真上心", "role_id": "male_guard_captain", "tags": "[softly]", "stability": 0.5, "note": "玄剑宗周执事掂钱袋低笑"},
            {"match": "可不是么！我家大少爷已经拟好了除名折子", "role_id": "female_maid_npc", "tags": "[sarcastic] [whispers]", "stability": 0.0, "note": "春桃泄露送帖逼交宗祠地契掘地夺宝毒计"},
        ],
        sfx_blueprint=[
            {"p": 3, "pos": "before", "slug": "stone_knock_iron_grate", "sfx_prompt": "Two light knocks and one heavy knock on hollow stone brick followed by a rusted underground iron sluice gate sliding open", "duration_seconds": 3.2, "gain_db": 0.5, "note": "两轻一重叩击鬼脸砖，排洪暗渠铁栅滑开"},
            {"p": 5, "pos": "before", "slug": "silver_toss_cavern_steps", "sfx_prompt": "Piece of silver clinking into a wooden bucket followed by footsteps descending wet stone stairs into a vast echoing underground market", "duration_seconds": 3.4, "gain_db": -0.5, "note": "弹出二两纹银落斗，步入地下古河道鬼樊楼"},
            {"p": 20, "pos": "after", "slug": "bamboo_cut_salve_heal", "sfx_prompt": "Sharp thin bamboo blade nicking skin followed by a gentle warm crystalline shimmer sealing the wound", "duration_seconds": 2.4, "gain_db": 0.0, "note": "竹刀划破手背，黑膏三息凝成淡金薄膜"},
            {"p": 29, "pos": "before", "slug": "ice_jade_box_push", "sfx_prompt": "Frosty jade box and wooden token sliding across stone table with clinking spirit stones", "duration_seconds": 2.6, "gain_db": 0.0, "note": "推出寒气森森的冰玉盒与乌木小牌"},
            {"p": 33, "pos": "before", "slug": "coffin_taboo_echo", "motif_id": "motif_frost_coffin_knock", "gain_db": -3.0, "note": "‘天上的娘娘’话音落下，极寒宿命余韵轻震"},
            {"p": 44, "pos": "before", "slug": "alley_wind_murderous", "sfx_prompt": "Cold night wind whistling sharply between stacked clay wine jars in a dark narrow alley", "duration_seconds": 2.8, "gain_db": -1.0, "note": "巷口寒风吹过酒坛缝隙，杀意森然"},
        ],
    )
    j06, m06 = save_episode_scripts(s06, SCRIPTS_DIR, registry)
    built.append(("E006", j06, m06))

    # =========================================================================
    # E007 · 第7章 荒原猎残妖，吞髓触命锁 (62 paras, 7 quotes)
    # =========================================================================
    md_07 = SOURCE_DIR / "第07章_荒原猎残妖，吞髓触命锁.md"
    s07 = compile_episode_cue_sheet(
        episode_id="E007",
        chapter_number=7,
        source_md_path=md_07,
        source_rel_path=f"02_分章精修正文/{md_07.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_bear_broth_scorpion_brew",
                "start_p": 1,
                "title": "第一幕 · 砂锅煨熊肉，生吞妖蝎浆",
                "bgm_prompt": "Warm intimate Chinese guqin and gentle flute opening transitioning into intense fiery internal alchemy percussion and low strings, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_wasteland_sword_trap",
                "start_p": 19,
                "title": "第二幕 · 命锁裂四成，断碑设死角",
                "bgm_prompt": "Taut minimalist Chinese hunting suspense score, low ominous bronze drone, stealthy pizzicato and cold wind over ancient ruins, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_slaying_rift_claw_lizard",
                "start_p": 32,
                "title": "第三幕 · 血芝诱荒蜥，一剑贯颅腔",
                "bgm_prompt": "Explosive ferocious Chinese xianxia monster-slaying battle score, thunderous war drums, aggressive pipa and soaring heroic brass-like suona/horn undertones, instrumental only, no vocals",
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act4_coffin_sigh_gate_crash",
                "start_p": 51,
                "title": "第四幕 · 古棺轻叹息，恶奴踹祠门",
                "bgm_prompt": "Icy ethereal cosmic resonance shifting abruptly into arrogant confrontational clan tension strings and sharp percussion, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(25, 54, "mental_realm")],
        skip_onomatopoeia_paras={10, 14, 17, 33, 38, 41, 48},
        dialogue_specs=[
            {"match": "少主，这么金贵的一阶妖兽精肉", "role_id": "fu_bo", "tags": "[hoarsely]", "stability": 0.0, "note": "福伯连连摆手心疼精肉"},
            {"match": "让你喝便喝，明后两日还有硬仗", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬将灵液熊肉汤塞进福伯手中"},
            {"match": "大苍界的一阶妖蝎心终究受限于此界血锁", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬总结大苍界妖物本源上限"},
            {"match": "引气五重的神识加上", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "note": "决意入墟界猎杀异界残妖"},
            {"match": "死！", "role_id": "lu_jin", "tags": "[shouting]", "stability": 0.0, "space": "mental_realm", "note": "陆烬暴喝一剑贯入荒蜥瞎眼颅腔"},
            {"match": "陆少主还没咽气罢？", "role_id": "snobbish_steward_npc", "tags": "[sarcastic] [shouting]", "stability": 0.0, "note": "苏家大管事苏贵踹门嚣张叫阵"},
            {"match": "大少爷有话带到，陆家既已绝了修行香火", "role_id": "snobbish_steward_npc", "tags": "[dismissive] [sarcastic]", "stability": 0.0, "note": "苏贵掷帖进泥坑逼交陆氏宗祠红契"},
        ],
        sfx_blueprint=[
            {"p": 1, "pos": "before", "slug": "clay_pot_simmer", "sfx_prompt": "Rich broth bubbling gently in an earthen clay pot over a small charcoal stove in a quiet night kitchen", "duration_seconds": 3.0, "gain_db": -1.5, "note": "后厨小泥炉咕嘟煨熊肉汤"},
            {"p": 10, "pos": "before", "slug": "scorpion_heart_boil", "sfx_prompt": "Sharp blade piercing a scorpion heart with a loud violent sizzle and thick medicinal liquid boiling rapidly", "duration_seconds": 2.6, "gain_db": 0.5, "note": "嗤！刺破妖蝎心挤入滚烫药汁沸腾"},
            {"p": 14, "pos": "before", "slug": "meridian_crack_fifth", "sfx_prompt": "Internal bone and meridian joints cracking powerfully as surging heat breaks open a martial threshold", "duration_seconds": 2.4, "gain_db": 0.5, "note": "咔嚓！冲破关口晋入引气五重"},
            {"p": 17, "pos": "before", "slug": "bronze_lock_three_cracks", "sfx_prompt": "Two razor-sharp metallic bronze chain cracks ringing deep inside the chest followed by receding wave resonance", "duration_seconds": 2.8, "gain_db": 1.5, "note": "铮！铮！第一枚青铜锁扣裂开四成"},
            {"p": 33, "pos": "before", "slug": "lizard_roar_charge", "sfx_prompt": "Monstrous armored giant lizard roaring greedily and charging furiously across frozen rock, claws tearing stone", "duration_seconds": 3.6, "gain_db": 1.5, "note": "吼！裂爪荒蜥冲破灰雾狂扑而来"},
            {"p": 38, "pos": "before", "slug": "twin_swords_impale", "sfx_prompt": "Two heavy ancient bronze swords violently impaling thick scaly monster flesh and wedging against giant stone slabs", "duration_seconds": 2.8, "gain_db": 1.5, "note": "噗嗤！两截古修断剑贯入荒蜥颈侧卡死窄道"},
            {"p": 41, "pos": "before", "slug": "tail_shatter_stele", "sfx_prompt": "Enormous bone tail whipping like steel and shattering a massive stone stele into flying gravel", "duration_seconds": 3.0, "gain_db": 1.5, "note": "昂！荒蜥骨尾轰然抽碎万斤断碑"},
            {"p": 48, "pos": "before", "slug": "essence_absorb_sixth", "sfx_prompt": "Deep cosmic energy vortex absorbing crystalline beast core with thunderous bone-reforging resonance", "duration_seconds": 3.2, "gain_db": 1.0, "note": "轰隆！吞噬紫晶本源迈入引气六重，命锁裂七成"},
            {"p": 54, "pos": "before", "slug": "frost_coffin_sigh", "motif_id": "motif_frost_coffin_knock", "gain_db": -1.0, "note": "万里迷雾深处玄霜古棺极轻冰冷叹息"},
            {"p": 57, "pos": "before", "slug": "kick_open_clan_gates", "sfx_prompt": "Arrogant horses trotting outside followed by a violent kick snapping a wooden bar and slamming heavy wooden courtyard doors against brick wall", "duration_seconds": 3.6, "gain_db": 1.5, "note": "砰！苏贵带护院一脚踹断陆宅黑漆大门"},
        ],
    )
    j07, m07 = save_episode_scripts(s07, SCRIPTS_DIR, registry)
    built.append(("E007", j07, m07))

    return built


if __name__ == "__main__":
    items = build_all_batch1()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if "--compile-only" not in sys.argv:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=4)
