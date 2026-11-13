"""Build, validate, render, and archive Batch 3: Episodes E013–E017 (Chapters 13–17)."""

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


def build_all_batch3() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E013 · 第13章 夜探血月庄，笼中同命人 (64 paras, 14 quotes)
    # =========================================================================
    md_13 = SOURCE_DIR / "第13章_夜探血月庄，笼中同命人.md"
    s13 = compile_episode_cue_sheet(
        episode_id="E013",
        chapter_number=13,
        source_md_path=md_13,
        source_rel_path=f"02_分章精修正文/{md_13.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_mist_infiltration_cages",
                "start_p": 1,
                "title": "第一幕 · 夜潜百草庄，人形育血芽",
                "bgm_prompt": "Dark eerie Chinese horror espionage score, damp mountain fog drone, ominous low bowed strings and creeping subterranean dread, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_four_breath_execution",
                "start_p": 17,
                "title": "第二幕 · 毒师举屠刀，四息斩三枭",
                "bgm_prompt": "Sudden ferocious Chinese martial assassination score, razor-sharp pipa stabs, taut rapid war percussion and decisive lethal momentum, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_mercy_blade_shimeng_oath",
                "start_p": 42,
                "title": "第三幕 · 飞刺渡苦命，铁骨拜恩公",
                "bgm_prompt": "Solemn tragic ancient Chinese xiao flute and deep warm cello, quiet mercy in a blood-soaked dungeon shifting into iron-willed brotherhood, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_furnace_ledger_crimson_fire",
                "start_p": 55,
                "title": "第四幕 · 账揭头号鼎，烈火焚魔窟",
                "bgm_prompt": "Chilling revelation strings building into blazing righteous Chinese orchestral percussion as flames consume a dark fortress, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        skip_onomatopoeia_paras={38},
        dialogue_specs=[
            {"match": "原来如此……哪有什么天赐高品灵脉", "role_id": "lu_jin", "tags": "[whispers] [coldly]", "stability": 0.0, "note": "陆烬看穿催脉汤嫁接血月肉芽真相"},
            {"match": "钱叔，伍号和捌号今晚喝完最后半桶", "role_id": "male_disciple_a", "tags": "[sarcastic]", "stability": 0.0, "note": "麻衣药童谄笑汇报血芽成熟"},
            {"match": "倒是这个叫石猛的铁匠铺傻大个", "role_id": "male_disciple_a", "tags": "[dismissive]", "stability": 0.0, "note": "药童指向角落铁骨少年石猛"},
            {"match": "天生石骨，经脉闭塞如铁块", "role_id": "sect_elder_antagonist", "tags": "[coldly] [dismissive]", "stability": 0.5, "note": "外门毒师钱百草阴冷评判"},
            {"match": "不过这小子一身横练气血倒壮实得很", "role_id": "sect_elder_antagonist", "tags": "[sarcastic]", "stability": 0.0, "note": "钱百草掂剔骨刀欲剁人喂尸蟞"},
            {"match": "救……杀了我……求求你杀了我", "role_id": "male_disciple_b", "tags": "[crying] [whispers]", "stability": 0.0, "note": "柒号秦小石痛苦哀嚎求死"},
            {"match": "什么人！找死！", "role_id": "sect_elder_antagonist", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "钱百草惊觉头顶石窗炸裂"},
            {"match": "引气七重？不对，你这身法", "role_id": "sect_elder_antagonist", "tags": "[gasps] [trembling]", "stability": 0.0, "note": "钱百草临死骇然惊呼"},
            {"match": "痛……谢……", "role_id": "male_disciple_b", "tags": "[whispers]", "stability": 0.0, "note": "秦小石涣散瞳孔挤出遗言"},
            {"match": "能走么？", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬一刀斩断精铁链简短发问"},
            {"match": "恩公救命大恩！俺爹上个月", "role_id": "shi_meng", "tags": "[crying] [shouting]", "stability": 0.0, "note": "八尺石猛重跪磕头立下死誓"},
            {"match": "抹在伤口上止血。把外面库房", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬赐凝血膏命其搬空药库"},
            {"match": "俺省得！打死也不吐半个字", "role_id": "shi_meng", "tags": "[shouting]", "stability": 0.0, "note": "石猛抓紧药瓶咬牙领命"},
            {"match": "赤水庄玖名九月廿三生人", "role_id": "pei_xuandu", "tags": "[coldly]", "stability": 0.5, "space": "memory_echo", "note": "《血丹督造册》朱砂批注：苏清寒乃甲字头号主药炉鼎"},
        ],
        sfx_blueprint=[
            {"p": 7, "pos": "after", "slug": "bend_iron_bars_tunnel", "sfx_prompt": "Two rusted iron grate bars silently bending under hot martial grip followed by dripping underground tunnel ambience", "duration_seconds": 2.8, "gain_db": -0.5, "note": "燃血指劲拧弯排水铁栅潜入地牢"},
            {"p": 17, "pos": "before", "slug": "dungeon_stone_door_chains", "sfx_prompt": "Heavy dungeon stone door grinding open with rusted iron prisoner chains clanking", "duration_seconds": 3.0, "gain_db": 0.5, "note": "地牢石门哗啦推开"},
            {"p": 29, "pos": "before", "slug": "skylight_burst_spike_shot", "sfx_prompt": "Overhead stone vent window exploding into gravel followed by a supersonic metallic needle whistle and sparks", "duration_seconds": 3.0, "gain_db": 1.5, "note": "石窗炸裂，裂风刺直射咽喉"},
            {"p": 38, "pos": "before", "slug": "flame_blade_triple_kill", "sfx_prompt": "Blazing heavy broadsword slash severing armor followed by two crisp flying needle impacts", "duration_seconds": 2.8, "gain_db": 1.5, "note": "噗嗤！断刀枭首钱百草，飞刺双杀药童"},
            {"p": 48, "pos": "after", "slug": "sever_iron_shackles_kneel", "sfx_prompt": "Heavy blade cleanly snapping four thick iron chains clattering onto wet stone, followed by heavy knees slamming the floor", "duration_seconds": 3.2, "gain_db": 1.0, "note": "断刀斩断精铁链，石猛轰然跪地磕头"},
            {"p": 63, "pos": "after", "slug": "brazier_kick_roaring_blaze", "sfx_prompt": "Iron fire brazier kicked over igniting barrels of oil into a roaring towering inferno", "duration_seconds": 3.8, "gain_db": 1.5, "note": "挑翻火盆烈火冲天吞没百草庄"},
        ],
    )
    j13, m13 = save_episode_scripts(s13, SCRIPTS_DIR, registry)
    built.append(("E013", j13, m13))

    # =========================================================================
    # E014 · 第14章 推开第八环，无头药师与息壤灰 (58 paras, 13 quotes)
    # =========================================================================
    md_14 = SOURCE_DIR / "第14章_推开第八环，无头药师与息壤灰.md"
    s14 = compile_episode_cue_sheet(
        episode_id="E014",
        chapter_number=14,
        source_md_path=md_14,
        source_rel_path=f"02_分章精修正文/{md_14.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_forge_pact_ape_marrow",
                "start_p": 1,
                "title": "第一幕 · 荒铺留炭约，吞髓破八重",
                "bgm_prompt": "Cold pre-dawn Chinese flute over an old forge transitioning into surging fiery martial blood-refining drums and strings, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_eighth_ring_herb_hut",
                "start_p": 18,
                "title": "第二幕 · 推雾入八环，息壤无头师",
                "bgm_prompt": "Ancient desolate Chinese xianxia exploration score, ethereal bowed strings, bronze chimes and timeless herbal ruin mystery, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_flawless_foundation_sutras",
                "start_p": 31,
                "title": "第三幕 · 百草破障经，炉底噬神虫",
                "bgm_prompt": "Solemn luminous ancient scripture guqin rising into sudden razor-sharp insectoid tremolo strings and urgent danger, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_taboo_name_taiyi",
                "start_p": 47,
                "title": "第四幕 · 断指抠血训，莫提太一名",
                "bgm_prompt": "Haunting cosmic dread ancient Chinese score, deep hollow bronze resonance, icy high harmonics and ancient taboo gravitas, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[(19, 46, "mental_realm"), (49, 57, "mental_realm")],
        skip_onomatopoeia_paras={12, 40, 43},
        dialogue_specs=[
            {"match": "这两天玄剑宗的人必然满山搜查", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "废铁匠铺内陆烬嘱咐石猛藏身"},
            {"match": "恩公放心！俺爹打小教俺钻炉灰坑", "role_id": "shi_meng", "tags": "[calmly]", "stability": 0.5, "note": "石猛瓮声瓮气拍胸保证"},
            {"match": "先把伤养利索，活下来的人才有资格提刀", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬沉声点拨"},
            {"match": "需要用你的时候，我自然会在铁砧底下", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "定下刀痕碎炭联络暗号"},
            {"match": "好！俺就在南城等恩公的炭块", "role_id": "shi_meng", "tags": "[shouting]", "stability": 0.0, "note": "石猛重重点头"},
            {"match": "少主可算回来了！刚才半夜西边山头", "role_id": "fu_bo", "tags": "[softly]", "stability": 0.5, "note": "晨雾中福伯迎上关切询问"},
            {"match": "烧了一窝毒虫罢了，牵连不到西城来", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬摘下斗笠温声宽慰"},
            {"match": "这几日我要闭死关冲击引气后期", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬宣布闭死关"},
            {"match": "哎，老奴省得，锅里温着熊肉汤", "role_id": "fu_bo", "tags": "[softly]", "stability": 0.5, "note": "福伯端热汤进祠堂"},
            {"match": "无瑕界基……铁甲寒潭龙鲤血", "role_id": "lu_jin", "tags": "[whispers]", "stability": 0.0, "space": "mental_realm", "note": "陆烬在墨玉石壁前豁然开朗"},
            {"match": "第八环的活物同样受环形禁制束缚", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "密室中陆烬冷静盘算金背噬毒虫妙用"},
            {"match": "吾试破二阶锁败，血肉生异", "role_id": "ancient_construct_echo", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "无头药师断指血书遗训"},
            {"match": "后来者若得吾《破障经》，切记守住本心", "role_id": "ancient_construct_echo", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "惊天禁忌：寒棺娘娘若醒，切记莫提太一！"},
        ],
        sfx_blueprint=[
            {"p": 12, "pos": "before", "slug": "ape_marrow_break_eighth", "sfx_prompt": "Fiery internal martial blood roar and crisp spine bones aligning powerfully as cultivation breaks through", "duration_seconds": 3.0, "gain_db": 1.0, "note": "轰！生吞赤睛狂猿髓晋入引气八重"},
            {"p": 20, "pos": "before", "slug": "part_eighth_ring_fog", "motif_id": "motif_xujie_gate", "gain_db": 0.0, "note": "神识推开铅灰雾幕踏入第八环枯药残庐"},
            {"p": 40, "pos": "before", "slug": "venom_beetles_swarm", "sfx_prompt": "Terrifying metallic buzz of dozens of armored venomous beetles erupting from beneath a bronze cauldron", "duration_seconds": 3.0, "gain_db": 1.5, "note": "嗡嗡嗡！炉底钻出金背噬毒虫群"},
            {"p": 43, "pos": "before", "slug": "sever_spirit_thread", "sfx_prompt": "Sharp searing hiss of spiritual thread snapping cleanly followed by rapid footsteps retreating across stone", "duration_seconds": 2.4, "gain_db": 1.0, "note": "嘶！挥指斩断受损神识退回九环界线"},
            {"p": 53, "pos": "after", "slug": "taiyi_taboo_coffin_chill", "motif_id": "motif_frost_coffin_knock", "gain_db": -2.0, "note": "‘太一’禁忌血字落下，极寒余韵低鸣"},
        ],
    )
    j14, m14 = save_episode_scripts(s14, SCRIPTS_DIR, registry)
    built.append(("E014", j14, m14))

    # =========================================================================
    # E015 · 第15章 引气九重圆满，无瑕筑基之困 (54 paras, 14 quotes)
    # =========================================================================
    md_15 = SOURCE_DIR / "第15章_引气九重圆满，无瑕筑基之困.md"
    s15 = compile_episode_cue_sheet(
        episode_id="E015",
        chapter_number=15,
        source_md_path=md_15,
        source_rel_path=f"02_分章精修正文/{md_15.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_ninth_layer_sky_probe",
                "start_p": 1,
                "title": "第一幕 · 九重臻圆满，绝灵挡天针",
                "bgm_prompt": "Deep surging Chinese xianxia cultivation score shifting into eerie celestial surveillance tension and protective array hum, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_cold_pool_military_lockdown",
                "start_p": 21,
                "title": "第二幕 · 寒潭围铁桶，龙鲤断偏门",
                "bgm_prompt": "Shadowy underground lantern-lit guqin and pipa dialogue underscore, tense strategic problem-solving in a black market, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_three_birds_one_stone",
                "start_p": 30,
                "title": "第三幕 · 阳谋披官皮，一石落三鸟",
                "bgm_prompt": "Crisp resolute Chinese martial march theme, steady low drumbeat, taut strings and cool fearless calculation in autumn night wind, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act4_zhenyuansi_drill_ground",
                "start_p": 42,
                "title": "第四幕 · 废躯登校场，高台逢旧仇",
                "bgm_prompt": "Grand imposing imperial Chinese demon-hunting garrison score, solemn bronze horns, heavy stone courtyard drums and sharp confrontational strings, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        skip_onomatopoeia_paras={5},
        dialogue_specs=[
            {"match": "好霸道的界锁规则", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "note": "陆烬拍阵盘隔绝百会穴天幕窥探"},
            {"match": "根本不需要等到紫府境", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "破妄真目看穿小筑基散内暗红丝虫"},
            {"match": "要想半根命线都不沾身", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "锁定十月初一朔月无光夜铸无瑕界基"},
            {"match": "先生有所不知，别的二阶灵药", "role_id": "chu_xiazi", "tags": "[sighs]", "stability": 0.0, "note": "褚瞎子苦笑说出龙鲤真血断货"},
            {"match": "方圆三百里内，只有北渊城北十里外", "role_id": "chu_xiazi", "tags": "[whispers]", "stability": 0.0, "note": "褚瞎子道出王都紫衣巡察使军阵封潭"},
            {"match": "连鬼樊楼的人也进不去", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬蹙眉追问"},
            {"match": "前夜有两个贪财的筑基初期水匪", "role_id": "chu_xiazi", "tags": "[whispers]", "stability": 0.0, "note": "水匪被乱弩射杀挂北门示众"},
            {"match": "而且最晦气的是，如今兼领黑水寒潭", "role_id": "chu_xiazi", "tags": "[sarcastic]", "stability": 0.0, "note": "点出苏牧兼领寒潭防务"},
            {"match": "褚老，我记得刚才进南城时看见城门告示", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬心生阳谋询问镇渊司招人"},
            {"match": "不错！前阵子北境荒原妖兽异动", "role_id": "chu_xiazi", "tags": "[calmly]", "stability": 0.0, "note": "褚瞎子提醒考选需验真名根骨"},
            {"match": "无妨，多谢褚老告知", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬定计离去"},
            {"match": "西城陆氏，陆烬，年十八", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬本尊现身镇渊司校场坦然报名"},
            {"match": "嘶，他就是前阵子传得沸沸扬扬", "role_id": "male_disciple_a", "tags": "[gasps] [whispers]", "stability": 0.0, "note": "排队散修甲惊讶低呼"},
            {"match": "你懂个屁！前些天苏家二长老", "role_id": "male_disciple_b", "tags": "[sarcastic] [whispers]", "stability": 0.0, "note": "排队散修乙反驳议论古武传承"},
        ],
        sfx_blueprint=[
            {"p": 5, "pos": "before", "slug": "ninth_layer_river_roar", "sfx_prompt": "Deep internal river-like qi surge resonating powerfully inside a stone chamber as nine meridians align", "duration_seconds": 3.0, "gain_db": 1.0, "note": "轰隆！九脉贯通踏入引气九重圆满"},
            {"p": 12, "pos": "after", "slug": "slap_array_disc_shield", "sfx_prompt": "Sharp palm slap on a bronze formation disc activating twelve humming spirit flags sealing a subterranean room", "duration_seconds": 2.8, "gain_db": 0.5, "note": "一掌拍阵盘激发十二阵旗隔绝天幕窥探"},
            {"p": 18, "pos": "before", "slug": "incinerate_pill_powder", "sfx_prompt": "Crisp burst of white-hot martial finger flame burning tainted medicinal powder into thin smoke", "duration_seconds": 2.0, "gain_db": 0.0, "note": "搓出火芒烧毁带丝虫的小筑基散"},
            {"p": 42, "pos": "before", "slug": "garrison_crowd_armor", "sfx_prompt": "Solemn military garrison courtyard ambience with distant iron armor clinking and murmured crowd chatter", "duration_seconds": 3.2, "gain_db": -1.0, "note": "镇渊猎妖司黑石校场肃杀喧嚣"},
            {"p": 51, "pos": "before", "slug": "teacup_slam_spiritual_scan", "sfx_prompt": "Porcelain teacup slammed onto a stone railing followed by a cold sweeping spiritual pressure wave", "duration_seconds": 2.6, "gain_db": 0.5, "note": "苏牧重顿茶盏横扫筑基灵识探查空丹田"},
        ],
    )
    j15, m15 = save_episode_scripts(s15, SCRIPTS_DIR, registry)
    built.append(("E015", j15, m15))

    # =========================================================================
    # E016 · 第16章 考入镇渊司，废少主的藏锋刀 (58 paras, 21 quotes)
    # =========================================================================
    md_16 = SOURCE_DIR / "第16章_考入镇渊司，废少主的藏锋刀.md"
    s16 = compile_episode_cue_sheet(
        episode_id="E016",
        chapter_number=16,
        source_md_path=md_16,
        source_rel_path=f"02_分章精修正文/{md_16.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_two_thousand_jin_iron_stele",
                "start_p": 1,
                "title": "第一幕 · 苏牧设毒槛，黑铁压校场",
                "bgm_prompt": "Tense oppressive Chinese military arena score, heavy low war drums, arrogant brass-like horn accents and cold confrontation, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_three_overlapping_wave_slashes",
                "start_p": 14,
                "title": "第二幕 · 凡刀走毫厘，三叠劈重碑",
                "bgm_prompt": "Explosive heroic Chinese martial bladework score, escalating thunderous taiko-style war drums, blazing strings and awe-inspiring physical mastery, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_assigned_to_cold_pool",
                "start_p": 32,
                "title": "第三幕 · 甲等入黑衣，正中寒潭怀",
                "bgm_prompt": "Solemn dignified imperial Chinese garrison theme, crisp pipa, measured drum cadence and cool triumph over political scheming, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act4_old_veteran_broken_blade",
                "start_p": 40,
                "title": "第四幕 · 独眼识故刀，半截断岳归",
                "bgm_prompt": "Deeply moving weathered Chinese brotherhood score,沧桑 xiao flute, warm low guqin and solemn frontier camaraderie across generations, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
        ],
        skip_onomatopoeia_paras={7, 20, 22, 26, 30},
        dialogue_specs=[
            {"match": "镇渊司乃朝廷斩妖重地", "role_id": "su_mu", "tags": "[arrogant] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "苏牧运灵力传遍校场公然羞辱"},
            {"match": "多谢苏副统领挂心", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬抱拳不卑不亢接招"},
            {"match": "好一个生死自负！", "role_id": "su_mu", "tags": "[coldly]", "stability": 0.0, "note": "苏牧狞笑使眼色"},
            {"match": "来人！既然陆少主自称得了古武横练真传", "role_id": "su_mu", "tags": "[sarcastic] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "苏牧公报私仇换上两千斤黑铁重碑"},
            {"match": "陆少主，请吧，限时十息", "role_id": "snobbish_steward_npc", "tags": "[sarcastic]", "stability": 0.0, "note": "监考军侯冷笑指定官造凡铁刀"},
            {"match": "哈哈哈，就这点力气还敢", "role_id": "male_disciple_a", "tags": "[laughs] [sarcastic]", "stability": 0.0, "note": "台下苏家旁支武夫刚笑半声卡壳"},
            {"match": "开！", "role_id": "lu_jin", "tags": "[shouting]", "stability": 0.0, "note": "陆烬第三刀叠浪寸劲暴喝劈碑"},
            {"match": "气血浑凝，刀走毫厘", "role_id": "male_guard_captain", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "王都紫衣巡察使击掌赞叹"},
            {"match": "此子虽无丹田灵气，外门刀术", "role_id": "male_guard_captain", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "巡察使一锤定音钦定上上甲等"},
            {"match": "谨遵大人评判！来人，发陆烬黑衣刀卫铜牌", "role_id": "su_mu", "tags": "[angry] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "苏牧咬牙顺势将陆烬塞进丙字巡夜队"},
            {"match": "卑职领命", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬正中下怀平静领牌"},
            {"match": "你们几个先去武库领今夜的破甲箭", "role_id": "qin_lie", "tags": "[shouting]", "stability": 0.0, "note": "独眼老将秦烈粗豪轰走老卒单独留人"},
            {"match": "像……太像了！方才校场上那记叠浪回腕刀", "role_id": "qin_lie", "tags": "[hoarsely] [trembling]", "stability": 0.0, "note": "秦烈独目通红认出故人刀法"},
            {"match": "晚辈陆烬，见过秦伯父", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬郑重抱拳行晚辈礼"},
            {"match": "什么狗屁将军，当年在野狼谷", "role_id": "qin_lie", "tags": "[hoarsely]", "stability": 0.0, "note": "秦烈感念陆擎苍野狼谷救命大恩"},
            {"match": "前半个月外头传你被玄剑宗那群伪君子", "role_id": "qin_lie", "tags": "[angry] [hoarsely]", "stability": 0.0, "note": "秦烈拍肩痛骂玄剑宗与苏牧"},
            {"match": "打开看看", "role_id": "qin_lie", "tags": "[softly]", "stability": 0.5, "note": "秦烈捧出三尺油布木匣"},
            {"match": "三年前你爹独自往北进【天渊裂谷】前夜", "role_id": "qin_lie", "tags": "[hoarsely]", "stability": 0.5, "note": "秦烈追忆三年前夜饮托刀"},
            {"match": "你爹当时留了一句怪话", "role_id": "qin_lie", "tags": "[softly]", "stability": 0.5, "note": "秦烈神色肃穆"},
            {"match": "他说，‘老秦，若我儿平平安安", "role_id": "qin_lie", "tags": "[dramatically] [hoarsely]", "stability": 0.0, "note": "秦烈复述陆擎苍三年前惊世预判遗言"},
            {"match": "黑水潭底三百丈，寒铁龙鲤守旧尸", "role_id": "lu_qingcang", "tags": "[whispers]", "stability": 0.5, "space": "memory_echo", "note": "无尖刀槽内陆擎苍暗码批注残响"},
        ],
        sfx_blueprint=[
            {"p": 12, "pos": "before", "slug": "drop_two_thousand_jin_stele", "sfx_prompt": "Four strong men grunting and slamming a massive one-ton black iron monolith onto stone courtyard tiles with a ground-shaking thud", "duration_seconds": 3.4, "gain_db": 1.5, "note": "两千斤黑铁重碑轰隆砸在校场中央"},
            {"p": 14, "pos": "after", "slug": "finger_flick_iron_blade", "sfx_prompt": "Drawing an iron sabre from a rack and flicking the steel spine with a clear metallic ring", "duration_seconds": 2.2, "gain_db": 0.0, "note": "抽出官造熟铁长刀屈指轻弹刀脊"},
            {"p": 22, "pos": "before", "slug": "first_slash_iron_sparks", "sfx_prompt": "Ferocious heavy sabre slash clanging against solid black iron monolith with flying sparks", "duration_seconds": 2.2, "gain_db": 1.5, "note": "铛！第一刀火星暴射三尺"},
            {"p": 26, "pos": "before", "slug": "second_slash_deep_dent", "sfx_prompt": "Even heavier second overlapping sabre strike slamming into the exact metal groove with steel blade cracking", "duration_seconds": 2.4, "gain_db": 2.0, "note": "铛！第二刀叠浪劈入，凡铁刀崩开豁口"},
            {"p": 30, "pos": "before", "slug": "third_slash_monolith_split", "sfx_prompt": "Iron sabre shattering into shrapnel as a colossal black iron monolith splits cleanly in half and crashes thunderously onto stone", "duration_seconds": 3.8, "gain_db": 2.5, "note": "咔嚓轰隆！三叠寸劲劈裂两千斤黑铁重碑！"},
            {"p": 49, "pos": "after", "slug": "unlock_wooden_blade_case", "sfx_prompt": "Three brass padlocks clicking open and oiled cloth unwrapping from a heavy wooden weapon box", "duration_seconds": 2.8, "gain_db": 0.0, "note": "秦烈精血解开三重铜锁捧出断刃木匣"},
        ],
    )
    j16, m16 = save_episode_scripts(s16, SCRIPTS_DIR, registry)
    built.append(("E016", j16, m16))

    # =========================================================================
    # E017 · 第17章 故人赠断刃，寒潭夜钓龙鲤 (56 paras, 19 quotes)
    # =========================================================================
    md_17 = SOURCE_DIR / "第17章_故人赠断刃，寒潭夜钓龙鲤.md"
    s17 = compile_episode_cue_sheet(
        episode_id="E017",
        chapter_number=17,
        source_md_path=md_17,
        source_rel_path=f"02_分章精修正文/{md_17.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_duanyue_resonance_pact",
                "start_p": 1,
                "title": "第一幕 · 双刃鸣断岳，请命潜寒潭",
                "bgm_prompt": "Deep resonant bronze blade hum with warm resolute Chinese guqin and low frontier strings, unspoken trust between veteran and youth, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_midnight_dive_abyss",
                "start_p": 16,
                "title": "第二幕 · 残月临黑水，三百丈潜渊",
                "bgm_prompt": "Submerged dark ambient Chinese suspense score, freezing howling cliff wind fading into deep pressurized underwater sub-bass pulse, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_slay_iron_dragon_carp",
                "start_p": 29,
                "title": "第三幕 · 飞刺钉鱼鳃，重刃取真血",
                "bgm_prompt": "Fierce underwater monster-hunting Chinese percussion and taut surging strings, muffled deep-water impacts and lethal precision, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_fourteen_sunken_brides",
                "start_p": 42,
                "title": "第四幕 · 铁石沉旧尸，玉镯藏血冤",
                "bgm_prompt": "Chilling tragic underwater horror score, mournful ghostly xiao harmonics, cold jade clink and urgent return dash before midnight eclipse, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        skip_onomatopoeia_paras={2, 34, 37},
        dialogue_specs=[
            {"match": "你爹这把佩刀名叫【断岳】", "role_id": "qin_lie", "tags": "[calmly] [hoarsely]", "stability": 0.5, "note": "秦烈道出六十四斤断岳重刀来历"},
            {"match": "三年前不知在天渊外围撞上了什么硬茬子", "role_id": "qin_lie", "tags": "[sighs] [hoarsely]", "stability": 0.5, "note": "秦烈叮嘱日后重铸二阶利器"},
            {"match": "多谢秦伯父三年守刀之恩", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬收妥断刃深深一揖"},
            {"match": "自家人谢个屁！", "role_id": "qin_lie", "tags": "[laughs] [hoarsely]", "stability": 0.0, "note": "秦烈摆手豪爽护短"},
            {"match": "苏牧那小杂种把你塞进老子的丙字队", "role_id": "qin_lie", "tags": "[coldly]", "stability": 0.5, "note": "秦烈承诺巡夜护持"},
            {"match": "秦伯父，侄儿来丙字队", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬坦诚相告入队真意"},
            {"match": "家父留下的古武横练功法", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬请允明夜独自下水一炷香取龙鲤血"},
            {"match": "你小子疯了不成！黑水寒潭三百丈下", "role_id": "qin_lie", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "秦烈骇然失声劝阻"},
            {"match": "没有十成把握，侄儿断不会拿陆家", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬沉静笃定"},
            {"match": "方才那块两千斤黑铁碑，侄儿只用了五分力", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬露三分底气说服秦烈"},
            {"match": "娘的，你们老陆家两代人都是不撞南墙", "role_id": "qin_lie", "tags": "[laughs] [hoarsely]", "stability": 0.0, "note": "秦烈拍腿笑骂应承"},
            {"match": "好！明夜九月卅日交子时分", "role_id": "qin_lie", "tags": "[calmly]", "stability": 0.5, "note": "秦烈定计调开苏牧眼线亲自放哨"},
            {"match": "刘三、赵五，你们六个去东边野猪林", "role_id": "qin_lie", "tags": "[shouting]", "stability": 0.0, "note": "断崖上秦烈挥刀调走眼线"},
            {"match": "腰上拴个活扣，真要顶不住了", "role_id": "qin_lie", "tags": "[softly] [hoarsely]", "stability": 0.5, "note": "秦烈递牛皮绳关切叮嘱"},
            {"match": "多谢秦伯父，两百息足矣", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬绕绳悄然入水"},
            {"match": "一百六十息……你小子真在底下宰了一头铁甲龙鲤", "role_id": "qin_lie", "tags": "[gasps] [whispers]", "stability": 0.0, "note": "秦烈独眼滚圆震撼失声"},
            {"match": "侥幸未辱家父刀法", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬拧干冰水谦逊应答"},
            {"match": "秦伯父，侄儿旧伤复发腹痛难忍", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬告假赶回密室冲击无瑕筑基"},
            {"match": "滚吧滚吧！名册上老子给你画满勤", "role_id": "qin_lie", "tags": "[laughs]", "stability": 0.0, "note": "秦烈哭笑不得挥手放行"},
        ],
        sfx_blueprint=[
            {"p": 2, "pos": "before", "slug": "duanyue_twin_halves_hum", "motif_id": "motif_broken_blade_wipe", "gain_db": 1.0, "note": "嗡！两截断岳重刀靠近寸许发出龙吟共鸣"},
            {"p": 23, "pos": "after", "slug": "silent_plunge_freezing_pool", "sfx_prompt": "Clean streamlined dive slicing into deep freezing black water followed by pressurized underwater current hum", "duration_seconds": 3.0, "gain_db": 0.5, "note": "如标枪无声扎入黑水寒潭极速下潜"},
            {"p": 29, "pos": "after", "slug": "abyss_mud_burst_carp_jaws", "sfx_prompt": "Deep underwater silt exploding as a massive iron-scaled monster fish lunges through heavy water current", "duration_seconds": 3.0, "gain_db": 1.5, "note": "三百丈潭底黑泥炸开，铁甲寒潭龙鲤扑咬"},
            {"p": 34, "pos": "before", "slug": "gill_pierce_rock_smash", "sfx_prompt": "Metallic spike piercing thick underwater gills followed by a colossal iron tail smashing underwater cliff rock", "duration_seconds": 3.0, "gain_db": 1.5, "note": "噗嗤！裂风刺贯鳃，千斤铁尾抽碎水下岩壁"},
            {"p": 37, "pos": "before", "slug": "reverse_scale_pierce_jade_box", "sfx_prompt": "Heavy broken blade crunching through armored scale underwater followed by a frosty jade box lid snapping shut", "duration_seconds": 2.8, "gain_db": 1.5, "note": "咔嚓！刺穿逆鳞吸取龙鲤心头真血封入冰玉盒"},
            {"p": 50, "pos": "before", "slug": "underwater_jade_bangle_clink", "sfx_prompt": "Eerie underwater iron chains swaying softly and a white jade bangle sliding off dry bone", "duration_seconds": 2.8, "gain_db": 0.0, "note": "潭底十四具女尸铁链微晃，褪下刻‘玄度’白玉镯"},
            {"p": 51, "pos": "after", "slug": "break_water_surface_cliff", "sfx_prompt": "Streamlined figure bursting cleanly out of cold dark water onto a windswept rocky shore", "duration_seconds": 2.6, "gain_db": 0.5, "note": "冲破三百丈寒水悄然跃上岸崖"},
        ],
    )
    j17, m17 = save_episode_scripts(s17, SCRIPTS_DIR, registry)
    built.append(("E017", j17, m17))

    return built


if __name__ == "__main__":
    items = build_all_batch3()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if "--compile-only" not in sys.argv:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=4)
