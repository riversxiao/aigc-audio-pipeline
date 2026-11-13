"""Build, validate, render, and archive Batch 6: Episodes E028–E032 (Chapters 28–32)."""

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


def build_all_batch6() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E028 · 第28章 北渊变天，战利品大结算 (39 paras, 5 quotes)
    # =========================================================================
    md_28 = SOURCE_DIR / "第28章_北渊变天，战利品大结算.md"
    s28 = compile_episode_cue_sheet(
        episode_id="E028",
        chapter_number=28,
        source_md_path=md_28,
        source_rel_path=f"02_分章精修正文/{md_28.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_beiyuan_dawn_new_order",
                "start_p": 1,
                "title": "第一幕 · 北渊变天日，银章百户封",
                "bgm_prompt": "Triumphant solemn Chinese xianxia dawn orchestral score, morning mist clearing over ancient frontier city, dignified guqin and distant bronze ceremonial drums, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act2_guifan_spoils_settlement",
                "start_p": 8,
                "title": "第二幕 · 红袖奉四袋，重宝归旧祠",
                "bgm_prompt": "Refined mysterious Chinese chamber tea-house guzheng and xiao flute score, quiet respect, shimmering spiritual jade treasure aura, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_seventh_ring_frost_fissure",
                "start_p": 18,
                "title": "第三幕 · 紫府甘霖哺，冰缝窥凶爪",
                "bgm_prompt": "Vast primordial frozen abyss ambient Chinese soundtrack, crystalline sub-zero chimes, deep ethereal drone and ancient beast aura, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_blood_moon_parasite_truth",
                "start_p": 26,
                "title": "第四幕 · 破丹血手札，熟牲牧场明",
                "bgm_prompt": "Chilling cosmic-horror Chinese xianxia revelation score, eerie bowed erhu harmonics, sinister heartbeat pulse rising into cold northern resolve, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(18, 25, "mental_realm")],
        dialogue_specs=[
            {"match": "陆丹师，赤松岭别院地下宝库", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "红袖楼主恭敬呈上四只高阶储物袋"},
            {"match": "按昨夜三七之约，本楼只取了库房里", "role_id": "hongxiu_louzhu", "tags": "[calmly]", "stability": 0.5, "note": "红袖楼主执壶斟茶"},
            {"match": "鬼樊楼昨夜两颗天雷珠破阵及时", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬从容谢过鬼樊楼盟友之谊"},
            {"match": "骗局！大苍界万年修仙史皆是彻头彻尾的骗局", "role_id": "chiyang_laozu", "tags": "[angry] [hoarsely]", "stability": 0.0, "space": "memory_echo", "note": "赤阳老祖《紫府破丹考》癫狂血字批注回响"},
            {"match": "这三百年来，唯一一个修至紫府圆满却没长出噬丹肉虫的人", "role_id": "chiyang_laozu", "tags": "[hoarsely] [dramatically]", "stability": 0.0, "space": "memory_echo", "note": "手札末页关于陆擎苍与天渊血胎的怨毒批注"},
        ],
        sfx_blueprint=[
            {"p": 12, "pos": "after", "slug": "pour_spirit_stones_pile", "sfx_prompt": "Thousands of crystalline jade spirit stones and ancient metallic artifacts pouring onto a heavy stone table", "duration_seconds": 3.0, "gain_db": 0.5, "note": "四只储物袋两千四百八十枚灵石倾倒石案"},
            {"p": 19, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "enter_xujie_e28", "gain_db": 0.0, "note": "沉入方寸墟界查验第九环与第七环冰缝"},
            {"p": 21, "pos": "after", "slug": "primordial_ice_fissure_crack", "sfx_prompt": "Deep glacial ice wall cracking open with eerie sub-zero crystalline wind hissing through a narrow fissure", "duration_seconds": 3.2, "gain_db": 1.0, "note": "第七环百兽冰渊三尺幽蓝冰缝逸散太古极寒"},
            {"p": 34, "pos": "before", "slug": "candle_wick_pop_quiet_room", "sfx_prompt": "Sharp quiet oil-lamp candle wick pop and crackle in a dead-silent ancestral stone chamber", "duration_seconds": 2.0, "gain_db": 0.5, "note": "静室烛火啪地爆出灯花，大苍牧场真相拼齐"},
        ],
    )
    j28, m28 = save_episode_scripts(s28, SCRIPTS_DIR, registry)
    built.append(("E028", j28, m28))

    # =========================================================================
    # E029 · 第29章 故宅重立碑，向北问天渊 (47 paras, 21 quotes)
    # =========================================================================
    md_29 = SOURCE_DIR / "第29章_故宅重立碑，向北问天渊.md"
    s29 = compile_episode_cue_sheet(
        episode_id="E029",
        chapter_number=29,
        source_md_path=md_29,
        source_rel_path=f"02_分章精修正文/{md_29.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_ancestral_plaque_guifan_farewell",
                "start_p": 1,
                "title": "第一幕 · 故宅重立匾，盲叟赠烈酒",
                "bgm_prompt": "Gentle early-winter snowfall Chinese guqin and warm bamboo xiao melody, quiet dignity of a rebuilt clan hall and old underworld farewell, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_hearth_cloak_family_parting",
                "start_p": 14,
                "title": "第二幕 · 炭火缝玄氅，温言托旧巢",
                "bgm_prompt": "Deeply moving tender Chinese chamber strings and warm hearthside guzheng, loyal elderly butler sewing winter cloak, tearful unspoken familial love, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_ten_mile_pavilion_toast",
                "start_p": 26,
                "title": "第三幕 · 十里长亭雪，摔坛送孤刀",
                "bgm_prompt": "Heroic windswept Chinese frontier farewell score, lonely suona-free mournful dizi, galloping warhorse rhythm and fierce brotherhood resolve, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_crimson_rainbow_tianyuan_scar",
                "start_p": 40,
                "title": "第四幕 · 尸虹压南天，北望大渊裂",
                "bgm_prompt": "Ominous colossal dark-red sky pressure colliding with vast frozen northern abyss wind, heavy low brass-like horn and unyielding blade spirit, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[(5, 5, "mental_realm")],
        dialogue_specs=[
            {"match": "这是老头子用三十味烈阳草泡了十年的火烧春", "role_id": "chu_xiazi", "tags": "[hoarsely]", "stability": 0.5, "note": "褚瞎子塞给陆烬十年火烧春铜酒壶"},
            {"match": "多谢褚老，留下的那两张洗髓残方", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬抱拳致谢"},
            {"match": "嘿，老头子这辈子瞎着挺好", "role_id": "chu_xiazi", "tags": "[laughs] [hoarsely]", "stability": 0.5, "note": "褚瞎子摆手自嘲"},
            {"match": "倒是陆丹师此去天渊千万留个心眼", "role_id": "chu_xiazi", "tags": "[whispers] [dramatically]", "stability": 0.0, "note": "褚瞎子压低声音警告天渊肚里多魂异闻"},
            {"match": "鬼樊楼在北境三郡皆有暗桩", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "红袖楼主递上赤玉传讯符"},
            {"match": "行了，小石头先收功吧", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬唤停苦练蛮牛锻骨劲的石猛"},
            {"match": "白鹤药庄的地契和护庄阵盘我都交给你与福伯了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬安排福伯与石猛退居白鹤药庄"},
            {"match": "恩公放心！只要俺石猛还有一口气在", "role_id": "shi_meng", "tags": "[crying] [fiercely]", "stability": 0.0, "note": "石猛虎目微红立誓死护福伯"},
            {"match": "少主从小性子就跟老爷一个模子刻出来的", "role_id": "fu_bo", "tags": "[trembling] [softly]", "stability": 0.0, "note": "福伯颤巍巍替陆烬披上玄绒黑氅"},
            {"match": "少主只管放心大胆往前走，老奴这把骨头", "role_id": "fu_bo", "tags": "[crying] [softly]", "stability": 0.0, "note": "福伯忍泪含笑嘱咐祠堂长明灯与热汤"},
            {"match": "福伯保重，等我找到父亲下落，定回来喝您炖的汤", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬眼底泛暖轻握老人手背道别"},
            {"match": "就知道你小子今天天不亮准得溜", "role_id": "qin_lie", "tags": "[laughs]", "stability": 0.0, "note": "秦烈在十里长亭风雪中等候扔来烧刀子"},
            {"match": "喝一口暖暖身子！半个时辰前，南边百里外清风驿", "role_id": "qin_lie", "tags": "[dramatically]", "stability": 0.0, "note": "秦烈急告南方百丈暗红尸云逼近"},
            {"match": "算算脚程，赤阳老怪至多今日正午便会抵达北渊地界", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬饮酒平静推算"},
            {"match": "老子已经在北城门备好了三十架破灵重弩", "role_id": "qin_lie", "tags": "[fiercely]", "stability": 0.0, "note": "秦烈决意死战"},
            {"match": "秦伯父糊涂", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬沉声劝阻"},
            {"match": "破灵重弩伤得了筑基，却挡不住紫府老怪的尸煞领域", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬剖析赤阳真正目标是零号原血"},
            {"match": "你小子想一个人做饵把他引去极北冰原", "role_id": "qin_lie", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "秦烈脸色剧变惊呼"},
            {"match": "在平原官道上自然跑不过他，可若是进了前面三百里外", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬成竹在胸指向哭风冰原与黑风带"},
            {"match": "家父当年能在天渊外围斩断血月虫根全身而退", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "陆烬翻身上马拍重刀凛然托付"},
            {"match": "老陆，你生了个比你更狠的好儿子！给老子活着回来", "role_id": "qin_lie", "tags": "[shouting] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "秦烈仰天饮尽烈酒摔碎酒坛怒吼送行"},
        ],
        sfx_blueprint=[
            {"p": 16, "pos": "before", "slug": "charcoal_brazier_warm_crackle", "sfx_prompt": "Warm indoor charcoal brazier softly crackling while winter snow wind blows faintly outside wooden shutters", "duration_seconds": 3.0, "placement": "overlay_next", "gain_db": -3.5, "note": "后堂炭火盆噼啪微响，福伯灯下缝氅"},
            {"p": 38, "pos": "after", "slug": "warhorse_gallop_smash_wine_jar", "sfx_prompt": "Warhorse neighing and galloping fiercely into howling blizzard snow followed by a heavy clay wine jar smashing onto frozen stone", "duration_seconds": 3.6, "gain_db": 1.5, "note": "乌云踏雪驹冲入风雪，秦烈摔碎酒坛"},
            {"p": 42, "pos": "after", "slug": "corpse_rainbow_tear_clouds", "sfx_prompt": "Terrifying supersonic dark energy boom tearing storm clouds apart across the horizon", "duration_seconds": 3.2, "gain_db": 1.5, "note": "百里外赤阳紫府暗红尸虹撕裂云层破空压来"},
        ],
    )
    j29, m29 = save_episode_scripts(s29, SCRIPTS_DIR, registry)
    built.append(("E029", j29, m29))

    # =========================================================================
    # E030 · 第30章 一刀向北行，天幕后面是什么？ (53 paras, 14 quotes)
    # =========================================================================
    md_30 = SOURCE_DIR / "第30章_一刀向北行，天幕后面是什么？.md"
    s30 = compile_episode_cue_sheet(
        episode_id="E030",
        chapter_number=30,
        source_md_path=md_30,
        source_rel_path=f"02_分章精修正文/{md_30.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_blood_bait_kufeng_icefield",
                "start_p": 1,
                "title": "第一幕 · 一血引疯鲨，三昼遁冰原",
                "bgm_prompt": "High-velocity cat-and-mouse chase across a howling frozen glacier, sharp ice-crystal wind percussion, tense low strings and stealthy pulse, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_crippled_sentry_dead_drum_sky",
                "start_p": 16,
                "title": "第二幕 · 断头哨老卒，死皮鼓苍天",
                "bgm_prompt": "Desolate ancient border outpost at the edge of the world, bleak xiao flute, crackling dung fire and weathered old soldier memory, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_frost_coffin_glitching_moon",
                "start_p": 28,
                "title": "第三幕 · 遥望玄霜棺，血月露画皮",
                "bgm_prompt": "Vast surreal cosmic mystery Chinese xianxia score, shimmering frost coffin resonance and uncanny flickering false sky dome drone, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_stele_carving_leap_into_abyss",
                "start_p": 40,
                "title": "第四幕 · 界碑留父字，拔刀跃天渊",
                "bgm_prompt": "Epic heroic Chinese xianxia climax, roaring black abyssal gale, deeply emotional father-son legacy rising into fearless heavy-sabre leap into darkness, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(28, 35, "mental_realm")],
        skip_onomatopoeia_paras={41},
        dialogue_specs=[
            {"match": "桀桀桀……零号血胎的气息", "role_id": "chiyang_laozu", "tags": "[laughs] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖扑落孤狼岭狂笑追向北方"},
            {"match": "好滑溜的小畜生！竟连半点热气命线都没露出来", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "哭风冰原上空赤阳老祖暴怒搜寻"},
            {"match": "六十四斤的乌金重刀……后生，你姓陆", "role_id": "weathered_elder_npc", "tags": "[hoarsely]", "stability": 0.5, "note": "断头哨冻残守碑老卒认出断岳重刀"},
            {"match": "老人家认得这把刀", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬按刀立于风口"},
            {"match": "认得，怎么不认得", "role_id": "weathered_elder_npc", "tags": "[sighs] [hoarsely]", "stability": 0.0, "note": "老卒惨笑追忆"},
            {"match": "老汉我在这断头哨守了四十年界碑", "role_id": "weathered_elder_npc", "tags": "[hoarsely]", "stability": 0.5, "note": "老卒讲述三年前陆擎苍浑身是血换酒歇脚"},
            {"match": "家父当时情形如何？往哪条路走了", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.5, "note": "陆烬奉上十年火烧春急问父亲下落"},
            {"match": "那汉子当时胸口有一道刚结痂的大口子", "role_id": "weathered_elder_npc", "tags": "[hoarsely] [dramatically]", "stability": 0.0, "note": "老卒指向鹰嘴黑岩讲述陆擎苍自剖紫府"},
            {"match": "那汉子临走前跟老汉说了句怪话，说这大苍界的天是个画出来的死人皮鼓", "role_id": "weathered_elder_npc", "tags": "[whispers] [hoarsely]", "stability": 0.0, "note": "老卒低声转述死人皮鼓之言并愿舍命误导追兵"},
            {"match": "多谢老丈指路，保重", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬留下灵药兽肉郑重抱拳"},
            {"match": "原来在这座世界的尽头，连天幕本身都开始露馅了", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬看破天渊上空扁平闪烁的虚假血月"},
            {"match": "烬儿莫追，天外有笼", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "大苍止界碑背面父亲陆擎苍刀刻八字警告回响"},
            {"match": "爹，笼子里面我拆干净了", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.0, "note": "陆烬抚过界碑刀痕轻声回应"},
            {"match": "至于天外那座更大的笼子，儿子提刀来替你一块儿劈开", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "note": "陆烬拔出断岳重刀纵身跃入天渊裂谷"},
        ],
        sfx_blueprint=[
            {"p": 6, "pos": "before", "slug": "corpse_patriarch_screech_turn", "sfx_prompt": "Ear-splitting demonic eagle screech and sonic boom turning sharply across high mountain clouds", "duration_seconds": 2.8, "gain_db": 1.5, "note": "三十里高空赤阳老祖怪啸折向孤狼岭"},
            {"p": 30, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "frost_coffin_echo_e30", "gain_db": -1.5, "note": "方寸墟界遥望九柱中央玄霜古棺"},
            {"p": 41, "pos": "before", "slug": "black_bone_wind_parting", "sfx_prompt": "Ferocious roaring black abyssal gale hitting a resonant golden aura shield and parting cleanly around a warrior", "duration_seconds": 3.5, "gain_db": 1.5, "note": "呼——！蚀骨黑风撞上避风诀气场向两侧滑开"},
            {"p": 46, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "brush_frost_off_stele", "gain_db": 0.5, "note": "拂去大苍止界碑背面黑霜露出父亲刀痕"},
        ],
    )
    j30, m30 = save_episode_scripts(s30, SCRIPTS_DIR, registry)
    built.append(("E030", j30, m30))

    # =========================================================================
    # E031 · 第31章 黑风古栈道，天渊下的死人城 (67 paras, 14 quotes)
    # =========================================================================
    md_31 = SOURCE_DIR / "第31章_黑风古栈道，天渊下的死人城.md"
    s31 = compile_episode_cue_sheet(
        episode_id="E031",
        chapter_number=31,
        source_md_path=md_31,
        source_rel_path=f"02_分章精修正文/{md_31.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_black_wind_cliff_plankway",
                "start_p": 1,
                "title": "第一幕 · 刀插玄铁桩，潜行古栈道",
                "bgm_prompt": "Vertiginous descent down a pitch-black canyon cliff, screaming metallic wind, tense pizzicato strings and iron chain rattles, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act2_duantianshu_city_of_corpses",
                "start_p": 14,
                "title": "第二幕 · 悬空断天戍，满街破颅尸",
                "bgm_prompt": "Eerie ancient subterranean ghost fortress score, hollow stone street echoes, mournful bone flute and horrifying millennia-old silence, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_chiyang_descends_vent_decoy",
                "start_p": 30,
                "title": "第三幕 · 老魔强闯渊，风管戏紫府",
                "bgm_prompt": "Claustrophobic stealth cat-and-mouse suspense music, heavy monstrous footsteps, sweeping spiritual radar drone and cunning tactical tension, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_thunder_trap_headless_sect_master",
                "start_p": 52,
                "title": "第四幕 · 暗埋天雷阵，无头掌门书",
                "bgm_prompt": "escalating dread and dark revelation score, crackling hidden lightning beads, chilling headless corpse discovery ending on sudden horror impact, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(20, 67, "vast_hall")],
        skip_onomatopoeia_paras={32, 39},
        dialogue_specs=[
            {"match": "好霸道的风煞，寻常筑基修士若是没有避风法门", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬顶着蚀骨黑风感叹风煞凶险"},
            {"match": "天渊裂谷三百丈下，怎会有一座上古军戍", "role_id": "lu_jin", "tags": "[whispers]", "stability": 0.5, "note": "陆烬凝视悬空孤城断天戍"},
            {"match": "这服制……至少是三百年前中州大宗的紫府老祖", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬查验石井边紫袍古尸"},
            {"match": "明白了……", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬立于死寂黑石十字街心"},
            {"match": "数百年来，并非只有爹一个人察觉到了大苍血月的猫腻", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬洞悉历代紫府巅峰逃入天渊之谜"},
            {"match": "可惜他们只要不曾像爹那样狠下心剖开紫府挖出母虫", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬揭破越界三百丈血虫爆颅机制"},
            {"match": "小畜生！区区蚀骨黑风，也想拦住本座的成道之路", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "头顶三百丈赤阳老祖咆哮强闯黑风带"},
            {"match": "咳……咳咳！该死的鬼风，竟蚀了本座二十年苦修的尸罡", "role_id": "chiyang_laozu", "tags": "[coughs] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "血肉模糊的赤阳老祖砸落城门外喘息"},
            {"match": "姓陆的小杂种，本座知道你就藏在这座死人城里", "role_id": "chiyang_laozu", "tags": "[sarcastic] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖鬼眼扫视断天戍"},
            {"match": "赤阳老鬼，玄剑宗满门长老都已经下去探路了", "role_id": "lu_jin", "tags": "[sarcastic] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "陆烬借地下传声风管声东击西嘲讽"},
            {"match": "找死！", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖暴怒扑向西侧演武场"},
            {"match": "牙尖嘴利的小辈！你以为靠着几句鬼话就能乱了本座心神", "role_id": "chiyang_laozu", "tags": "[angry] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖贪婪叫嚣要夺陆烬无瑕肉身"},
            {"match": "血月在渊不在天！莫信飞升，入谷底者慎防守坛", "role_id": "weathered_elder_npc", "tags": "[hoarsely] [trembling]", "stability": 0.0, "space": "memory_echo", "note": "无头掌门鹤鸣真人青玉命牌绝笔血书回响"},
            {"match": "抓到你了，小畜生！原来躲在本门鹤鸣师伯的尸骨旁边发抖呢", "role_id": "chiyang_laozu", "tags": "[laughs] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "断戟残塔外赤阳老祖鬼脚踏碎黑石狞笑"},
        ],
        sfx_blueprint=[
            {"p": 8, "pos": "before", "slug": "heavy_blade_sparks_cliff_slide", "sfx_prompt": "Heavy iron broadsword stabbing into obsidian cliff rock and screeching downward in a shower of sparks to arrest a fall", "duration_seconds": 3.0, "gain_db": 1.5, "note": "断岳重刀插入崖缝划出三丈暗金火星止住下坠"},
            {"p": 32, "pos": "before", "slug": "chiyang_crash_city_gate", "sfx_prompt": "Massive demonic body crashing down from high cliff onto ancient stone plaza, shaking dust and rocks loose", "duration_seconds": 3.0, "gain_db": 2.0, "note": "轰隆！赤阳老祖强穿黑风带砸落断天戍城外"},
            {"p": 39, "pos": "before", "slug": "zifu_divine_sense_sweep", "sfx_prompt": "Suffocating low-frequency psychic radar pulse sweeping across hollow stone ruins", "duration_seconds": 2.8, "gain_db": 1.0, "note": "嗡！一里紫府神识横扫断天戍"},
            {"p": 65, "pos": "before", "slug": "rotten_footstep_outside_tower", "sfx_prompt": "Single eerie heavy footstep crushing brittle black stone right outside a ruined stone doorway", "duration_seconds": 2.0, "gain_db": 1.5, "note": "啪嗒！赤阳老祖踏碎断戟残塔门前黑石"},
        ],
    )
    j31, m31 = save_episode_scripts(s31, SCRIPTS_DIR, registry)
    built.append(("E031", j31, m31))

    # =========================================================================
    # E032 · 第32章 借风设死局，初试紫府威 (69 paras, 14 quotes)
    # =========================================================================
    md_32 = SOURCE_DIR / "第32章_借风设死局，初试紫府威.md"
    s32 = compile_episode_cue_sheet(
        episode_id="E032",
        chapter_number=32,
        source_md_path=md_32,
        source_rel_path=f"02_分章精修正文/{md_32.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_tower_collapse_clash_zifu",
                "start_p": 1,
                "title": "第一幕 · 古塔轰半塌，重刀削尸腕",
                "bgm_prompt": "Explosive Chinese xianxia boss combat score, collapsing stone tower, ferocious heavy sabre clashing against overwhelming Zifu realm pressure, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_broken_bridge_spear_rebound",
                "start_p": 22,
                "title": "第二幕 · 断桥横刀架，借矛跃深渊",
                "bgm_prompt": "Breathless life-or-death cliff-bridge pursuit music, pounding war drums, taut bowstring tension and daring tactical leap, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act3_six_thunder_pearls_sever_arm",
                "start_p": 36,
                "title": "第三幕 · 六雷崩岩檐，黑风绞尸臂",
                "bgm_prompt": "Cataclysmic lightning detonation unleashing a monstrous fifty-zhang abyssal hurricane vortex, chaotic destructive orchestra climax, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_thousand_zhang_icefall_arrow_mark",
                "start_p": 55,
                "title": "第四幕 · 千丈荡枯藤，冰瀑见父箭",
                "bgm_prompt": "Quiet aftermath beneath an underground ice waterfall, dripping icicles, solitary guqin warmth upon finding a father's secret arrow sign, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[(1, 54, "vast_hall")],
        skip_onomatopoeia_paras={3, 30, 38, 42, 48},
        dialogue_specs=[
            {"match": "给本座滚出来", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖一掌轰塌半座断戟残塔"},
            {"match": "嗯？好快的肉身", "role_id": "chiyang_laozu", "tags": "[gasps] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "赤阳惊诧于陆烬二段燃血极速"},
            {"match": "好一副生龙活虎的年轻血胎，给本座拿来", "role_id": "chiyang_laozu", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖紫府尸爪当胸抓落"},
            {"match": "不能硬撼他的力场中心，削腕借力", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬冷静决断斜斩尺骨"},
            {"match": "嘶！这是陆擎苍那把断刀？不对，刀上是什么鬼火", "role_id": "chiyang_laozu", "tags": "[gasps] [angry]", "stability": 0.0, "space": "vast_hall", "note": "赤阳手腕被焚锁妖煞火灼烧吃痛"},
            {"match": "伤了本座还想跑？留下你的肉身", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳喷出精血化作残影追至风眼断桥"},
            {"match": "死不了你的泥丸魂，本座只要这具热乎的皮囊", "role_id": "chiyang_laozu", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "十丈血色尸矛贯穿而下"},
            {"match": "老鬼，这具肉身太烫，怕你牙口不好吞不下去", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬借力倒飞跃出断桥冷笑"},
            {"match": "给小爷炸", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬弹指点燃煞火引线引爆六枚天雷珠"},
            {"match": "二阶极品破阵天雷珠？你哪来这么多", "role_id": "chiyang_laozu", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖察觉脚下六团银雷魂飞魄散"},
            {"match": "不！小杂种你敢阴本座", "role_id": "chiyang_laozu", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖被五十丈蚀骨黑风龙正面吞没"},
            {"match": "我的手……我的紫府尸臂！陆家小畜生", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳被黑风绞断整条左臂凄厉怨吼"},
            {"match": "没死……本座感应得到那滴零号真血还在往下坠", "role_id": "chiyang_laozu", "tags": "[hoarsely] [angry]", "stability": 0.0, "space": "vast_hall", "note": "断臂赤阳绕往西侧绝壁追索"},
            {"match": "就是这里", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "note": "千丈崖腰陆烬甩出裂风刺钉入铁线老藤"},
        ],
        sfx_blueprint=[
            {"p": 3, "pos": "before", "slug": "stone_tower_half_shatter", "sfx_prompt": "Colossal demonic palm strike blasting an ancient black-stone tower in half with boulders crashing everywhere", "duration_seconds": 3.4, "gain_db": 2.0, "note": "轰隆！赤阳腐血大手印轰塌断戟残塔"},
            {"p": 8, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "genelock_burst_e32", "gain_db": 0.5, "note": "第一阶基因锁圆满二段燃血全开"},
            {"p": 16, "pos": "before", "slug": "duanyue_slash_iron_wrist", "sfx_prompt": "Deafening heavy broadsword clang against metallic bone wrist followed by sizzling dark demon fire", "duration_seconds": 2.6, "gain_db": 1.5, "note": "铛！断岳重刀斩上赤阳手腕迸出妖煞火"},
            {"p": 30, "pos": "before", "slug": "blood_spear_slam_heavy_blade", "sfx_prompt": "Titanic energy spear slamming onto a braced broadsword, cracking solid stone bridge deck underneath", "duration_seconds": 3.0, "gain_db": 2.0, "note": "轰！十丈血矛轰在断岳刀面震碎桥面"},
            {"p": 38, "pos": "before", "slug": "fire_spark_ignite_fuse", "sfx_prompt": "Sharp sizzling violet fire spark racing rapidly along a hidden stone fuse", "duration_seconds": 1.8, "gain_db": 1.0, "note": "滋啦！焚线指火星引燃风眼石缝引线"},
            {"p": 42, "pos": "before", "slug": "six_thunder_pearls_hurricane_breach", "sfx_prompt": "Six simultaneous thunder-pearl explosions shattering a cliff overhang and unleashing a deafening abyssal black wind tornado", "duration_seconds": 4.5, "gain_db": 2.5, "note": "轰隆隆隆！六枚破阵天雷珠炸塌断风岩檐，五十丈黑风龙倒灌"},
            {"p": 48, "pos": "before", "slug": "wind_blades_rip_corpse_arm", "sfx_prompt": "Razor-sharp hurricane wind ripping through armor and snapping bone violently", "duration_seconds": 2.5, "gain_db": 1.5, "note": "噗嗤咔嚓！蚀骨黑风绞碎赤阳左胸与整条左臂"},
        ],
    )
    j32, m32 = save_episode_scripts(s32, SCRIPTS_DIR, registry)
    built.append(("E032", j32, m32))

    return built


if __name__ == "__main__":
    only_compile = "--compile-only" in sys.argv
    items = build_all_batch6()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if not only_compile:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=8)
