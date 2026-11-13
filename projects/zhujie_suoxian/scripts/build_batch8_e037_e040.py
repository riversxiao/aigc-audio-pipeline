"""Build, validate, render, and archive Batch 8: Episodes E037–E040 (Chapters 37–40, Volume 1 Finale)."""

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


def build_all_batch8() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E037 · 第37章 黄雀拔刀时，越阶斩紫府！ (69 paras, 13 quotes)
    # =========================================================================
    md_37 = SOURCE_DIR / "第37章_黄雀拔刀时，越阶斩紫府！.md"
    s37 = compile_episode_cue_sheet(
        episode_id="E037",
        chapter_number=37,
        source_md_path=md_37,
        source_rel_path=f"02_分章精修正文/{md_37.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_thunder_roc_ambush_shatter_shield",
                "start_p": 1,
                "title": "第一幕 · 破渊起惊雷，一刀崩尸盾",
                "bgm_prompt": "Explosive triumphant Chinese xianxia boss-slaying climax, silver-blue lightning eruption from black water, pounding war drums and unstoppable heavy sabre strike, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_demon_fire_burn_parasite_behead_zifu",
                "start_p": 25,
                "title": "第二幕 · 煞火焚母虫，断岳枭赤阳",
                "bgm_prompt": "Fierce cathartic vengeance score, searing erhu cry and solemn ancestral justice culminating in a clean decisive execution slash, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_void_origin_crystal_peak_foundation",
                "start_p": 44,
                "title": "第三幕 · 界隙取源晶，百零八滴圆",
                "bgm_prompt": "Pure celestial starlight spiritual ascension music, crystalline chime resonance, surging golden sea of qi reaching grand perfection, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_blood_crystal_alarm_cleave_altar",
                "start_p": 63,
                "title": "第四幕 · 母晶鸣警讯，怒刀劈血坛",
                "bgm_prompt": "Urgent ominous crimson alarm pulse instantly overpowered by a heaven-splitting heroic broadsword crescendo, instrumental only, no vocals",
                "bgm_duration_s": 80.0,
            },
        ],
        acoustic_ranges=[(1, 69, "vast_hall")],
        skip_onomatopoeia_paras={3, 13, 21, 39, 57, 64},
        dialogue_specs=[
            {"match": "谁！", "role_id": "chiyang_laozu", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "距母晶半寸处赤阳老祖骇然惊觉"},
            {"match": "原来是你在水底算计本座！玄阴护命尸盾", "role_id": "chiyang_laozu", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳喷出最后精血凝出三尺黑红骨盾"},
            {"match": "小畜生！本座得不到的金丹大道，你也休想活着带走", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳妄图引爆体内噬丹血月母虫拉陆烬陪葬"},
            {"match": "凭你这具烂透了的虫壳，也配拉我陪葬", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "半空陆烬冷喝如雷当头劈落断岳"},
            {"match": "这是什么火……不！", "role_id": "chiyang_laozu", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "焚锁妖煞火锥捅入紫府点燃母虫"},
            {"match": "啊！饶命……陆少主饶命！老夫愿奉你为主", "role_id": "chiyang_laozu", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "盘踞北渊百年的紫府老祖涕泪崩溃求饶"},
            {"match": "三年前你勾结中州仙使逼走我爹", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬俯视赤阳清算第一桩血债"},
            {"match": "一个月前你纵容裴玄度夺我道基", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬清算北渊百户与守渊盲裔血债"},
            {"match": "赤阳，这一刀，北渊陆氏连本带利向你讨还", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三色刀月横贯三丈一刀枭首紫府老祖"},
            {"match": "这颗母晶由无数紫府修士被血虫吞噬的怨血寿元凝成", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬不碰剧毒母晶，看向底座阵眼"},
            {"match": "那是……跨界通道与一方世界灵脉交汇处才会凝结的", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬发现三枚纯净银白界隙伴生源晶"},
            {"match": "吸了大苍众生三千年的骨血，临死还想往天外报信", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "space": "vast_hall", "note": "母晶闪烁猩红警报欲向无面仙使传讯"},
            {"match": "给我——碎！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬双手高举断岳重刀怒劈整座血月母坛"},
        ],
        sfx_blueprint=[
            {"p": 3, "pos": "before", "slug": "frost_water_split_roc_burst", "sfx_prompt": "Black water freezing and splitting silently followed by an explosive thunder-eagle sonic dash", "duration_seconds": 2.8, "gain_db": 1.5, "note": "哗啦！陆烬自三丈外黑水裂隙暴起发难"},
            {"p": 6, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "full_burst_slay_zifu", "gain_db": 1.0, "note": "基因锁圆满二段燃血叠加雷鹏十成极速全开"},
            {"p": 21, "pos": "before", "slug": "thunder_sabre_shatter_bone_shield", "sfx_prompt": "Heavy broadsword wrapped in crackling lightning smashing a dark bone shield into frozen shards", "duration_seconds": 3.0, "gain_db": 2.0, "note": "铛咔嚓！断岳雷霜劈碎玄阴护命尸盾"},
            {"p": 39, "pos": "before", "slug": "three_color_blade_behead_zifu", "sfx_prompt": "Clean decisive heavy broadsword arc slicing through air followed by roaring dark flames turning a body to ash", "duration_seconds": 3.0, "gain_db": 2.0, "note": "噗嗤！三色刀月枭首赤阳老祖焚成灰烬"},
            {"p": 57, "pos": "before", "motif_id": "motif_qi_sea_shatter", "slug": "origin_crystal_peak_foundation", "gain_db": 1.5, "note": "轰隆！鲸吞界隙伴生源晶晋升筑基大圆满百零八滴"},
            {"p": 64, "pos": "before", "slug": "crimson_crystal_alarm_pulse", "sfx_prompt": "Urgent high-pitched crystalline rune alarm pulsing rapidly inside an ancient underground chamber", "duration_seconds": 2.6, "gain_db": 1.0, "note": "嗡嗡嗡！百年血月母晶闪烁猩红警报符文"},
        ],
    )
    j37, m37 = save_episode_scripts(s37, SCRIPTS_DIR, registry)
    built.append(("E037", j37, m37))

    # =========================================================================
    # E038 · 第38章 天幕画皮碎，北渊抬头见真星 (57 paras, 12 quotes)
    # =========================================================================
    md_38 = SOURCE_DIR / "第38章_天幕画皮碎，北渊抬头见真星.md"
    s38 = compile_episode_cue_sheet(
        episode_id="E038",
        chapter_number=38,
        source_md_path=md_38,
        source_rel_path=f"02_分章精修正文/{md_38.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_false_sky_rips_true_stars_shine",
                "start_p": 1,
                "title": "第一幕 · 一刀裂画皮，九州见真星",
                "bgm_prompt": "Breathtaking epic Chinese xianxia catharsis score, shattering false crimson dome revealing an infinite tranquil starry cosmos, soaring guqin, bamboo xiao and awe-inspiring orchestral wonder, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_blind_clan_tears_first_coffin_chain",
                "start_p": 20,
                "title": "第二幕 · 星辉抚盲裔，古棺松一锁",
                "bgm_prompt": "Deeply moving sacred starlight chamber strings transitioning into ancient frost-coffin bronze chain resonance and phoenix sword chime, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_farewell_pasture_seventy_three",
                "start_p": 37,
                "title": "第三幕 · 赠牌遣盲族，牧场七十三",
                "bgm_prompt": "Solemn dignified farewell melody on guzheng and low strings darkening into cold cosmic resolve before an ancient star-carved stone gate, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_father_palmprint_step_across_worlds",
                "start_p": 49,
                "title": "第四幕 · 掌叠慈父印，踏步入界隙",
                "bgm_prompt": "Heroic emotional father-son palmprint resonance building into a sudden perilous void-storm cliffhanger, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        acoustic_ranges=[(30, 34, "mental_realm")],
        skip_onomatopoeia_paras={1, 4, 29, 55},
        dialogue_specs=[
            {"match": "星光……原来天外真的没有血月，只有真星", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.0, "note": "陆烬仰望三千年来首次洒入大苍的清澈真星"},
            {"match": "弟弟，你感觉到了么？阿爷说过头顶只有烤人骨头的血光", "role_id": "a_mang", "tags": "[crying] [softly]", "stability": 0.0, "note": "白发盲女阿盲抚摸脸颊感受清凉真星辉哽咽"},
            {"match": "这是……维持大苍界【折寿锁灵锁】运转的核心阵枢残片", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬挑起刻有苍字锁纹的暗青金属碎片"},
            {"match": "原来如此！", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "陆烬明悟集齐四界锁碎可解玄霜古棺第一重封"},
            {"match": "方寸墟界最中心那口古棺，竟然需要打碎四座不同认知世界的基因锁核心", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "陆烬握紧第一把开棺界钥"},
            {"match": "赤阳老鬼与守坛傀儡都已伏诛，上方黑风已散", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬留下灵石丹药与镇渊司腰牌指引盲裔回地面寻秦烈"},
            {"match": "恩公大德，阿盲和守渊四十七口永世不忘", "role_id": "a_mang", "tags": "[crying] [softly]", "stability": 0.0, "note": "阿盲双手紧捧铁牌含泪送别"},
            {"match": "嗯，笼子破了，总得出去看看外头真正的天地有多大", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬微笑转身走向五丈跨界石门"},
            {"match": "第柒拾叁号下界牧场【大苍】，北接【烬昼】，东连【枯海】", "role_id": "ancient_construct_echo", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "跨界石门门楣仙庭残缺小篆刻字"},
            {"match": "第七十三号下界牧场", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬抚过仙庭刻字眼神冷冽"},
            {"match": "在那些高高在上的天外牧羊人眼里，大苍九州亿万生灵", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "note": "陆烬锁定父亲去往的第二认知世界烬昼"},
            {"match": "爹，等着我", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.0, "note": "陆烬右手叠上石柱父亲血掌印毅然跨入跨界古道"},
        ],
        sfx_blueprint=[
            {"p": 1, "pos": "before", "slug": "cleave_blood_crystal_and_altar", "sfx_prompt": "Heaven-splitting heavy broadsword thunder strike shattering a giant crystal and cleaving a bronze-and-bone altar in half", "duration_seconds": 4.2, "gain_db": 2.5, "note": "轰隆咔嚓！一刀劈碎百年血月母晶与九角母坛"},
            {"p": 15, "pos": "before", "slug": "false_sky_dome_shatter_starlight", "sfx_prompt": "Colossal illusory glass-like sky dome cracking open across the heavens, fading into serene crystalline starlight shimmer", "duration_seconds": 4.0, "gain_db": 1.5, "note": "万里苍穹虚假血月画皮裂开巨口，真星洒落人间"},
            {"p": 29, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "frost_coffin_chain_loosen", "gain_db": 1.5, "note": "轰！玄霜古棺第一根太古寒铁锁链松开三寸传出凤鸣剑意"},
            {"p": 55, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "step_through_world_gate", "gain_db": 1.5, "note": "嗡！一步跨过跨界石门踏上黑色星石古道"},
        ],
    )
    j38, m38 = save_episode_scripts(s38, SCRIPTS_DIR, registry)
    built.append(("E038", j38, m38))

    # =========================================================================
    # E039 · 第39章 死前一瞬的心脏停跳，跨界风暴 (79 paras, 13 quotes)
    # =========================================================================
    md_39 = SOURCE_DIR / "第39章_死前一瞬的心脏停跳，跨界风暴.md"
    s39 = compile_episode_cue_sheet(
        episode_id="E039",
        chapter_number=39,
        source_md_path=md_39,
        source_rel_path=f"02_分章精修正文/{md_39.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_interworld_rift_eyeless_corpses",
                "start_p": 1,
                "title": "第一幕 · 跨界墟隙道，漂流无目尸",
                "bgm_prompt": "Eerie weightless cosmic void soundtrack between worlds, crushing dimensional pressure drone, drifting ancient ruins and ominous tension, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_patrol_white_eye_causal_blades",
                "start_p": 15,
                "title": "第二幕 · 巡界白瞳开，因果清道刃",
                "bgm_prompt": "Terrifying celestial machine awakening score, blinding white geometric law chords, razor-sharp causal wind blades and desperate mortal peril, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_heart_stops_blind_seven_steps",
                "start_p": 37,
                "title": "第三幕 · 心脏停半息，闭目踏七步",
                "bgm_prompt": "Sudden time-freeze heartbeat silence exploding into a heroic blind seven-step charge through a storm of blades, pounding war drums and unyielding willpower, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_fourth_soul_mystery_eternal_night_sky",
                "start_p": 61,
                "title": "第四幕 · 心藏未知魂，抬头无日天",
                "bgm_prompt": "Mysterious unsettling awakening on a warm bone-ash wasteland, solitary low guqin over pitch-black sunless eternal-night ambience, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(1, 61, "vast_hall"), (67, 68, "mental_realm")],
        skip_onomatopoeia_paras={15, 27, 38, 40, 48, 52, 61},
        dialogue_specs=[
            {"match": "好可怕的界隙排斥力", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "踏上跨界墟隙古道骨骼咔咔作响"},
            {"match": "专斩双目与泥丸神魂？难怪爹在石柱上留字警告", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬瞥见虚空漂流的无目金丹古尸凛然"},
            {"match": "无巡天令偷渡界隙者，视同窃药叛奴，抹去五识神魂", "role_id": "ancient_construct_echo", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "断桥上方三丈巡界白瞳降下冰冷仙庭神念"},
            {"match": "不好！", "role_id": "lu_jin", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "无面清道风刃凭空降临陆烬偏头横刀硬挡"},
            {"match": "好快！连破妄真目都捕捉不到风刃成型的轨迹", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬惊觉目光越盯防风刃落点越准"},
            {"match": "莫用眼看，闭目散识，抱刀走七步", "role_id": "eternal_night_whisper", "tags": "[whispers] [hoarsely]", "stability": 0.0, "space": "mental_realm", "note": "心脏停跳半息间血管深处浮起的苍凉沙哑低语"},
            {"match": "第二步！第三步！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬闭死双目散去灵识抱刀踏向断桥虚空"},
            {"match": "第七步，给我破！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬拼尽百零八滴灵液撞向新世界胎膜"},
            {"match": "咳……咳咳！", "role_id": "lu_jin", "tags": "[coughs] [hoarsely]", "stability": 0.0, "note": "砸落温热骨灰荒原剧烈咳嗽"},
            {"match": "不是玄霜古棺，也不是第六环冰渊深处那个声音", "role_id": "lu_jin", "tags": "[whispers]", "stability": 0.5, "note": "陆烬按住恢复跳动的心口排查方寸墟界"},
            {"match": "天渊无脐弃婴，零号青铜铭牌……原来除了眉心识海里的", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "note": "第四层身世悬念揭开：心脏深处藏着未知残魂意志"},
            {"match": "不管你是谁，既然藏在我陆烬的肉身里", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "note": "陆烬绝不做提线木偶立下誓言"},
            {"match": "不是沙土，整片大地铺满的竟然全是某种生灵骸骨烧透之后留下的温热骨灰", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬捻起脚下灰白骨灰抬头望向无日永夜苍穹"},
        ],
        sfx_blueprint=[
            {"p": 15, "pos": "before", "slug": "patrol_white_eye_rift_open", "sfx_prompt": "Blinding geometric celestial eye ripping open in void space with an icy resonant law hum", "duration_seconds": 3.0, "gain_db": 1.5, "note": "嗡！断桥虚空裂开三丈巡界白瞳"},
            {"p": 27, "pos": "before", "slug": "invisible_causal_blade_cut_sabre", "sfx_prompt": "Piercing invisible dimensional razor slicing setengah-inch into heavy乌金 iron steel", "duration_seconds": 2.2, "gain_db": 1.5, "note": "铛噗嗤！无面清道风刃切入断岳刀身半寸"},
            {"p": 38, "pos": "before", "slug": "heart_stop_time_freeze_thud", "sfx_prompt": "Single colossal deep human heartbeat thud abruptly stopping into eerie ticking time-freeze silence", "duration_seconds": 3.0, "gain_db": 2.0, "note": "咚——咔！心脏骤停半息，时光沙漏按停"},
            {"p": 48, "pos": "before", "slug": "heartbeat_resume_blind_footsteps", "sfx_prompt": "Powerful heartbeat resuming followed by heavy resolute footsteps charging across stone while wind blades miss", "duration_seconds": 3.4, "gain_db": 1.5, "note": "咚！轰！心脏重跳，闭目抱刀踏出七步"},
            {"p": 61, "pos": "before", "slug": "pierce_world_membrane_crash_ash", "sfx_prompt": "Bursting through a thick resonant cosmic water-membrane followed by a heavy body crashing into soft ash earth", "duration_seconds": 3.5, "gain_db": 1.5, "note": "啵——砰！撞破世界胎衣砸落烬昼界骨灰荒原"},
        ],
    )
    j39, m39 = save_episode_scripts(s39, SCRIPTS_DIR, registry)
    built.append(("E039", j39, m39))

    # =========================================================================
    # E040 · 第40章 第二认知世界：永夜无日，骨灯大胤！ (65 paras, 19 quotes)
    # =========================================================================
    md_40 = SOURCE_DIR / "第40章_第二认知世界：永夜无日，骨灯大胤！.md"
    s40 = compile_episode_cue_sheet(
        episode_id="E040",
        chapter_number=40,
        source_md_path=md_40,
        source_rel_path=f"02_分章精修正文/{md_40.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_three_step_test_eternal_night_whispers",
                "start_p": 1,
                "title": "第一幕 · 三步试永夜，十息起诡音",
                "bgm_prompt": "Suffocating pitch-black ash wasteland horror-xianxia score, eerie bowed bone-like strings, creeping shadow whispers purged by crisp violet demon fire, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_skull_lantern_caravan_shadow_demons",
                "start_p": 20,
                "title": "第二幕 · 白骨官道险，髓灯抗夜魔",
                "bgm_prompt": "Desperate dark-fantasy caravan siege soundtrack, flickering skull lantern fire, screeching shadow monsters and frantic steel clashes, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_walk_from_darkness_one_slash_purify",
                "start_p": 33,
                "title": "第三幕 · 踏暗拔重刀，一刃净三魔",
                "bgm_prompt": "Cool awe-inspiring Chinese xianxia hero entrance from pitch darkness, calm footsteps, single razor-clean heavy sabre sweep and warm campfire glow, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_bone_lamp_empire_what_is_the_sun",
                "start_p": 47,
                "title": "第四幕 · 千丈白骨塔，何物唤太阳",
                "bgm_prompt": "Towering gothic-xianxia bone-lamp city vista turning into chilling mind-bending cognitive-world revelation silence and haunting final guqin harmonic, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
        ],
        skip_onomatopoeia_paras={10, 17, 34, 39, 46, 57},
        dialogue_specs=[
            {"match": "好燥烈的灰烬火毒！这方世界的天地元气里", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬三步试险测出烬昼界骨油灰毒灵气"},
            {"match": "好黑啊……为什么你不点灯……没有灯的人都是死人", "role_id": "eternal_night_whisper", "tags": "[whispers] [hoarsely]", "stability": 0.0, "space": "mental_realm", "note": "踏入永夜满十息后颈贴耳响起诡异重叠低语"},
            {"match": "把你的眼珠子抠出来点着吧……骨头烧起来就不冷了", "role_id": "eternal_night_whisper", "tags": "[whispers] [trembling]", "stability": 0.0, "space": "mental_realm", "note": "噬影鬼手抓向脚踝伴随蛊惑低语"},
            {"match": "一踏入黑暗十息便会触发幻听低语与噬影袭击", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬看破烬昼界世界基因锁"},
            {"match": "原来如此，三阶【焚锁妖煞火】不仅能克大苍血虫", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "一豆紫黑煞火瞬间烧空鬼手与低语"},
            {"match": "快护住车头母灯！灯油只剩最后一指厚了", "role_id": "male_guard_captain", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "白骨官道上周护卫队长浴血嘶吼护灯"},
            {"match": "周头儿救命！左边黑影里又有【噬影夜魔】扑上来了", "role_id": "male_disciple_a", "tags": "[crying] [shouting]", "stability": 0.0, "note": "商队护卫惊恐求救"},
            {"match": "陈叔小心！", "role_id": "male_guard_captain", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "周护卫队长目眦欲裂救援不及"},
            {"match": "完了，髓油尽了，咱们全要沦为永夜里的孤魂野鬼了", "role_id": "weathered_elder_npc", "tags": "[desperately] [trembling]", "stability": 0.0, "note": "老管事陈福绝望闭目待死"},
            {"match": "黑、黑暗里怎么会有活人没提骨灯？是化形大夜魔", "role_id": "male_disciple_b", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "护卫骇然看见不提骨灯走出黑暗的陆烬"},
            {"match": "路过贵宝地，见诸位遇险顺手解围，不知此处是何地界", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬弹碎阳炎珠燃起温暖红火拱手询问"},
            {"match": "小老儿大胤百草行管事陈福，多谢前辈救下我全队二十三口性命", "role_id": "weathered_elder_npc", "tags": "[trembling] [hoarsely]", "stability": 0.0, "note": "陈福确认陆烬有活人影子激动拜倒"},
            {"match": "前辈神刀盖世，连二阶噬影夜魔都能一刀净化", "role_id": "male_guard_captain", "tags": "[dramatically]", "stability": 0.0, "note": "周护卫队长捧上骨币与青铜骨灯指向白骨灯城"},
            {"match": "大胤圣朝，白骨灯城", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬远眺八十里外千丈白骨巨塔"},
            {"match": "多谢陈老丈指路。在下深山苦修多年，刚出山门有些不辨时辰", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬随口询问距离天亮日出还有几个时辰"},
            {"match": "老丈，在下可是说错了什么话", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "见商队二十三口齐退三步惨白如鬼，陆烬按刀微蹙"},
            {"match": "恩、恩公快莫要在外头说这等掉脑袋的胡话啊", "role_id": "weathered_elder_npc", "tags": "[whispers] [trembling]", "stability": 0.0, "note": "陈老头吓得嘴唇哆嗦四下张望"},
            {"match": "打从太古混沌开天辟地以来，这世间万物头顶就只有茫茫永夜", "role_id": "weathered_elder_npc", "tags": "[trembling] [dramatically]", "stability": 0.0, "note": "陈老头道出大胤圣朝不灭骨灯塔的世界观铁律"},
            {"match": "恩公方才说的……什么叫‘天亮’？什么叫‘太阳’？", "role_id": "weathered_elder_npc", "tags": "[whispers] [trembling]", "stability": 0.0, "note": "第一卷终极认知悬念收官钩子：什么叫天亮？什么叫太阳？"},
        ],
        sfx_blueprint=[
            {"p": 10, "pos": "before", "slug": "eternal_night_shadow_creep", "sfx_prompt": "Unsettling sub-audible dark drone and creeping shadow tendrils rustling through bone ash right behind the ears", "duration_seconds": 2.8, "gain_db": 0.5, "note": "嗡……黑暗满十息诡异阴影蠕动"},
            {"p": 17, "pos": "before", "slug": "demon_fire_evaporate_shadows", "sfx_prompt": "Crisp hot violet flame spark flaring up and instantly evaporating screeching dark shadows into silence", "duration_seconds": 2.4, "gain_db": 1.0, "note": "嗤啦！焚锁妖煞火蒸发黑暗鬼手与低语"},
            {"p": 34, "pos": "before", "slug": "calm_footstep_from_pitch_dark", "sfx_prompt": "Single steady calm boot footstep crunching on bone-paved road out of total silence", "duration_seconds": 1.8, "gain_db": 1.5, "note": "踏！陆烬自绝对永夜黑暗中稳步走出"},
            {"p": 39, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "one_sabre_purify_three_night_demons", "gain_db": 1.5, "note": "嗡——嗤！断岳横扫一刀净化三头二阶噬影夜魔，收刀归鞘"},
            {"p": 57, "pos": "before", "slug": "bronze_bone_lantern_drop_ash", "sfx_prompt": "Heavy bronze lantern slipping from trembling hands and clattering onto soft ash ground in dead silence", "duration_seconds": 2.2, "gain_db": 1.5, "note": "啪嗒！听见天亮日出四字，周护卫吓掉手中青铜骨灯"},
        ],
    )
    j40, m40 = save_episode_scripts(s40, SCRIPTS_DIR, registry)
    built.append(("E040", j40, m40))

    return built


if __name__ == "__main__":
    only_compile = "--compile-only" in sys.argv
    items = build_all_batch8()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if not only_compile:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=8)
