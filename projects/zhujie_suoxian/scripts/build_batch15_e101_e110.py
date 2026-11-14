"""Build and validate Batch 15: Episodes E101–E110 (Chapters 101–110 of 《诸界锁仙》)."""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_SELF_DIR = Path(__file__).resolve().parent
for _p in (str(REPO_ROOT / "src"), str(SCRIPTS_SELF_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from aigc_audio_pipeline.compiler import compile_episode_cue_sheet, save_episode_scripts
from aigc_audio_pipeline.models import VoiceCastingRegistry
from world_ost_palette import WORLD_OST

SOURCE_DIR = (
    Path("/tmp/zhujie_source_chapters")
    if Path("/tmp/zhujie_source_chapters").is_dir()
    else Path("/shared/user/.gemini/config/zhujie_suoxian_audio/source_chapters")
)
REGISTRY_PATH = REPO_ROOT / "projects/zhujie_suoxian/00_声音选角档案与进度台账/voice_casting_registry.json"
REPO_SCRIPTS_DIR = REPO_ROOT / "projects/zhujie_suoxian/02_分集广播剧台本"


def build_batch15_e101_e110() -> list[tuple[str, Path, Path, int, int]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path, int, int]] = []

    # =========================================================================
    # E101 · 第101章 阔别一甲子重返北渊，抬手覆灭仙庭舰队！ (59 paras, 17 quotes)
    # =========================================================================
    md_101 = SOURCE_DIR / "第101章_阔别一甲子重返北渊，抬手覆灭仙庭舰队！.md"
    s101 = compile_episode_cue_sheet(
        episode_id="E101",
        chapter_number=101,
        source_md_path=md_101,
        source_rel_path=f"02_分章精修正文/{md_101.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_beiyuan_siege_sixty_years_stand",
                "start_p": 1,
                "title": "第一幕 · 甲子守孤城，白发拒仙舰",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_star_gate_palm_crush_armada",
                "start_p": 18,
                "title": "第二幕 · 踏门挡灭炮，只手捏十舰",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_tears_of_old_friends_where_is_fubo",
                "start_p": 38,
                "title": "第三幕 · 故人泣跪迎，轻声问福伯",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 38, "vast_hall")],
        skip_onomatopoeia_paras={15, 19, 31, 36},
        dialogue_specs=[
            {"match": "北渊儿郎听令！六十年前少主一人一刀", "role_id": "shi_meng", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "两鬓斑白的石猛城头嘶吼死守北渊"},
            {"match": "小石头说得对！老子替老陆和烬小子守了六十年北门", "role_id": "qin_lie", "tags": "[hoarsely] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "百岁垂暮秦烈咳血惨笑死战"},
            {"match": "区区紫府虫豸，也妄想螳臂当车", "role_id": "ancient_construct_echo", "speaker_name": "无面巡狩使·苍刑", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "旗舰舰首无面巡狩使漠然下令开炮"},
            {"match": "什么人敢拦仙庭巡狩舰队", "role_id": "ancient_construct_echo", "speaker_name": "无面巡狩使·苍刑", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "苍刑惊见十道灭世炮光凭空湮灭"},
            {"match": "我家的城，也是你们这群没脸的狗东西配动的", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬立于北渊上空冰冷宣判"},
            {"match": "不！这是第八境合道古尊", "role_id": "ancient_construct_echo", "speaker_name": "无面巡狩使·苍刑", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "苍刑被合道大手攥住魂飞魄散求饶"},
            {"match": "少主！是少主回来了！秦帅，阿盲妹子", "role_id": "shi_meng", "tags": "[crying] [shouting]", "stability": 0.0, "note": "石猛重刀滑落双膝跪地虎泪狂飙"},
            {"match": "好小子……六十年了，你小子还跟十八岁走那天一个样", "role_id": "qin_lie", "tags": "[crying] [laughs]", "stability": 0.0, "note": "百岁秦烈揉着独眼老泪纵横大笑"},
            {"match": "守渊阿盲，恭迎恩公回家", "role_id": "a_mang", "tags": "[crying] [softly]", "stability": 0.0, "note": "白发阿盲双手捧心深深拜倒"},
            {"match": "妈的，老头子当年那壶十年火烧春", "role_id": "chu_xiazi", "tags": "[laughs] [hoarsely]", "stability": 0.0, "note": "鬼樊楼顶百岁褚瞎子擦眼角怪笑"},
            {"match": "是六十年前劈碎血月母坛的陆少主", "role_id": "male_disciple_a", "speaker_name": "北渊修士", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "城头修士认出广场神像本尊"},
            {"match": "北渊真仙归来，咱们大苍有救了", "role_id": "male_disciple_b", "speaker_name": "北渊军民", "tags": "[crying] [shouting]", "stability": 0.0, "note": "全城百万军民喜极而泣欢呼"},
            {"match": "小石头，锻骨劲练得不错，都没耽误", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬托住石猛双肩温言扶起"},
            {"match": "少主当年赏俺装壮骨丸的那个白瓷瓶", "role_id": "shi_meng", "tags": "[crying] [hoarsely]", "stability": 0.0, "note": "石猛重拍胸甲像孩子般哽咽"},
            {"match": "秦伯父，辛苦你替我守了六十年北门", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬渡入合道生机护住秦烈心脉"},
            {"match": "活着回来就好，你爹要是知道你如今抬手就能捏碎天上的仙船", "role_id": "qin_lie", "tags": "[laughs] [hoarsely]", "stability": 0.0, "note": "秦烈拍着陆烬手臂满脸皱纹舒展"},
            {"match": "小石头，福伯呢", "role_id": "lu_jin", "tags": "[softly] [trembling]", "stability": 0.0, "note": "欢呼声中陆烬轻声问出心底最牵挂的人"},
        ],
        sfx_blueprint=[
            {"p": 15, "pos": "before", "slug": "celestial_world_destroyer_cannons", "sfx_prompt": "Ten colossal celestial warships charging and firing blinding high-energy annihilation beams tearing through clouds", "duration_seconds": 3.5, "gain_db": 1.5, "note": "轰！十艘白金战舰主炮轰落"},
            {"p": 19, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "star_gate_open_above_beiyuan", "gain_db": 1.5, "note": "嗤啦！百丈星辉天门当空裂开"},
            {"p": 31, "pos": "before", "slug": "hedao_domain_crush_silence", "sfx_prompt": "Deep cosmic sub-bass law resonance descending and freezing ten giant metallic warships in midair", "duration_seconds": 2.8, "gain_db": 1.5, "note": "嗡！合道执道境无上伟力降临"},
            {"p": 36, "pos": "before", "slug": "ten_warships_crumple_fireworks", "sfx_prompt": "Colossal metal hulls twisting, folding, and exploding into shimmering golden crystalline sparks high in the sky", "duration_seconds": 4.0, "gain_db": 2.0, "note": "咔嚓轰隆！单手捏爆十艘白金屠界战舰"},
            {"p": 42, "pos": "before", "slug": "heavy_broadsword_drop_stone", "sfx_prompt": "Heavy hundred-pound iron broadsword slipping from hands and clanging onto ancient stone battlements", "duration_seconds": 2.2, "gain_db": 1.0, "note": "啪嗒！石猛手中百斤重刀滑落城砖"},
        ],
    )
    j101, m101 = save_episode_scripts(s101, REPO_SCRIPTS_DIR, registry)
    built.append(("E101", j101, m101, len(s101.cues), len(s101.acts)))

    # =========================================================================
    # E102 · 第102章 西城老槐树下酒，敬人间故人坟 (50 paras, 12 quotes)
    # =========================================================================
    md_102 = SOURCE_DIR / "第102章_西城老槐树下酒，敬人间故人坟.md"
    s102 = compile_episode_cue_sheet(
        episode_id="E102",
        chapter_number=102,
        source_md_path=md_102,
        source_rel_path=f"02_分章精修正文/{md_102.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_autumn_rain_walk_to_locust_tree",
                "start_p": 1,
                "title": "第一幕 · 秋雨入西城，老槐立青碑",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_wooden_box_relics_night_wine_by_grave",
                "start_p": 14,
                "title": "第二幕 · 旧牌留余温，树下夜温酒",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act3_uproot_world_lock_summon_seven_realms",
                "start_p": 41,
                "title": "第三幕 · 拔锁立仙碑，传檄聚七界",
                "bgm_prompt": WORLD_OST["w2_first_sunlight_catharsis"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(42, 50, "vast_hall")],
        skip_onomatopoeia_paras={43},
        dialogue_specs=[
            {"match": "带我去看看他", "role_id": "lu_jin", "tags": "[calmly] [softly]", "stability": 0.5, "note": "陆烬收敛合道神识平静点头"},
            {"match": "少主，您走之后那年冬天，俺照您的吩咐把福爷爷接进了白鹤药庄", "role_id": "shi_meng", "tags": "[softly]", "stability": 0.5, "note": "石猛立于回廊边低声禀报福伯晚年"},
            {"match": "福爷爷原本只是引气三重，按理活不过七十岁", "role_id": "shi_meng", "tags": "[softly]", "stability": 0.5, "note": "石猛擦眼角欣慰讲述福伯享年九十八岁"},
            {"match": "走的时候，受罪了么", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "秋雨打湿黑发，陆烬轻声询问"},
            {"match": "没有，半点罪都没受", "role_id": "shi_meng", "tags": "[softly] [crying]", "stability": 0.0, "note": "石猛摇头落泪"},
            {"match": "就是十二年前一个秋高气爽的午后", "role_id": "shi_meng", "tags": "[crying] [softly]", "stability": 0.0, "note": "石猛讲述福伯在老槐树竹躺椅上含笑睡去"},
            {"match": "福爷爷临走前头一天，像是心里有数似的", "role_id": "shi_meng", "tags": "[hoarsely] [softly]", "stability": 0.0, "note": "石猛捧出红绸木匣转述福伯遗训"},
            {"match": "这是老人家闭眼时死死揣在怀里的两样东西", "role_id": "shi_meng", "tags": "[crying] [softly]", "stability": 0.0, "note": "福伯临终念叨少主在外莫饿着肚子"},
            {"match": "福伯，我回来了", "role_id": "lu_jin", "tags": "[softly] [hoarsely]", "stability": 0.0, "note": "陆烬跪在湿冷青石碑前指腹擦去雨珠"},
            {"match": "我在外头没饿着肚子，也没给陆家丢人", "role_id": "lu_jin", "tags": "[softly] [sighs]", "stability": 0.0, "note": "陆烬靠着老槐树根温酒轻声诉说半生"},
            {"match": "福伯，您安心睡。那些把人间当牧场", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.0, "note": "黎明雨歇陆烬饮尽残酒按碑立誓"},
            {"match": "散！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬踏上九霄连根拔起大苍界折寿锁灵锁"},
        ],
        sfx_blueprint=[
            {"p": 5, "pos": "before", "motif_id": "motif_beiyuan_cold_rain", "slug": "autumn_rain_beiyuan_streets", "gain_db": 0.5, "note": "傍晚北渊城飘起细密绵长的深秋冷雨"},
            {"p": 32, "pos": "before", "slug": "flint_pine_fire_warm_wine", "sfx_prompt": "Traditional flint spark lighting dry pine twigs in a clay stove with gentle simmering rice wine poured into ceramic bowls", "duration_seconds": 3.6, "gain_db": 1.0, "note": "火折子点燃松枝泥炉温热黄酒倾洒墓前"},
            {"p": 43, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "uproot_dacang_world_lock", "gain_db": 1.5, "note": "轰隆！四阶基因锁连根拔起大苍折寿锁灵锁化作灵雨"},
            {"p": 47, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "step_into_guixu_portal", "gain_db": 1.2, "note": "转身携姜清凰迈入空间天门开启总反攻"},
        ],
    )
    j102, m102 = save_episode_scripts(s102, REPO_SCRIPTS_DIR, registry)
    built.append(("E102", j102, m102, len(s102.cues), len(s102.acts)))

    # =========================================================================
    # E103 · 第103章 串联七界燃烽火，合道中期融万界！ (48 paras, 17 quotes)
    # =========================================================================
    md_103 = SOURCE_DIR / "第103章_串联七界燃烽火，合道中期融万界！.md"
    s103 = compile_episode_cue_sheet(
        episode_id="E103",
        chapter_number=103,
        source_md_path=md_103,
        source_rel_path=f"02_分章精修正文/{md_103.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_father_son_reunion_libation_for_fubo",
                "start_p": 1,
                "title": "第一幕 · 镇渊父子聚，酹酒敬忠魂",
                "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_seven_worlds_alliance_twelve_realms_crusade",
                "start_p": 10,
                "title": "第二幕 · 朝天盟七界，十日破十二笼",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_hedao_mid_realm_thirty_three_heavens_horn",
                "start_p": 32,
                "title": "第三幕 · 融界晋中期，挥师三十三天",
                "bgm_prompt": WORLD_OST["w5_yang_spirit_ascension"],
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(10, 22, "vast_hall"), (32, 48, "vast_hall")],
        skip_onomatopoeia_paras={35, 41, 44},
        dialogue_specs=[
            {"match": "好小子！老子前些日子还在跟海棠丫头念叨你", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "note": "陆擎苍冲上高台独臂重拍儿子肩膀大笑"},
            {"match": "可以啊烬儿，出去闯荡几年，不仅把仙庭的狗窝捅穿了", "role_id": "lu_qingcang", "tags": "[laughs] [whispers]", "stability": 0.0, "note": "陆擎苍凑近陆烬调侃请出女帝"},
            {"match": "陆将军虎父无犬子，当年天渊风雪夜若无将军一念仁善", "role_id": "jiang_qinghuang", "tags": "[calmly]", "stability": 0.5, "note": "姜清凰向陆擎苍颔首致意"},
            {"match": "北渊那边怎么样了", "role_id": "lu_qingcang", "tags": "[calmly]", "stability": 0.5, "note": "陆擎苍神色一正询问故乡"},
            {"match": "仙庭派去灭口的十艘战舰已被孩儿随手抹平", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬禀报北渊故人安好"},
            {"match": "福伯享年九十八岁，十二年前在白鹤药庄老槐树下睡梦中含笑善终", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬轻声告知福伯善终"},
            {"match": "忠叔护了咱们爷俩半辈子，九十八岁喜丧", "role_id": "lu_qingcang", "tags": "[hoarsely] [dramatically]", "stability": 0.0, "note": "陆擎苍面北将整囊烈酒洒入东海波涛"},
            {"match": "当年永夜圣京若非陆前辈仗刀相助", "role_id": "female_maid_npc", "speaker_name": "沈烛音", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "烬昼界白衣女剑仙沈烛音执晚辈剑礼"},
            {"match": "都是自家战友，沈姑娘不必多礼", "role_id": "lu_qingcang", "tags": "[laughs]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍爽朗摆手"},
            {"match": "诸位皆是从各自世界的血肉囚笼里杀出来的明白人", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬点亮朝天殿穹顶墟海星图"},
            {"match": "司命仙庭将诸天万界编作牧场丹皿", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬宣告主动出击拆毁仙庭外围篱笆"},
            {"match": "陆尊尽管下令，我太虚七十二仙宗十万剑修愿为前驱", "role_id": "li_cang", "speaker_name": "莫问天", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "疯剑尊莫问天拍着剑匣请战"},
            {"match": "有第二环那座完整的【万界坐标台】在", "role_id": "weathered_elder_npc", "speaker_name": "季长生", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "阵师季长生踏前一步请命布传兵大阵"},
            {"match": "守昼剑修、归墟义军、魔渊本部，皆听凭少主调遣", "role_id": "hongxiu_louzhu", "speaker_name": "夜琉璃", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "夜琉璃与诸界领袖齐声抱拳应诺"},
            {"match": "十九界连成一体，如今便是仙庭合道后期亲至", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "陆烬晋升合道境中期融界境"},
            {"match": "终于舍得把看门的主力全派出来了么", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬遥望三十三天百万天兵压境"},
            {"match": "传我盟主令，全军登舰开拔", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬拔出断岳斩锁刀号令十九界联军出关"},
        ],
        sfx_blueprint=[
            {"p": 9, "pos": "before", "slug": "wine_poured_into_ocean_waves", "sfx_prompt": "Strong liquor pouring from a leather flask into crashing ocean waves beneath howling coastal wind", "duration_seconds": 3.0, "gain_db": 1.0, "note": "陆擎苍拔塞将烈酒洒入东海波涛祭奠福伯"},
            {"p": 24, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "fourth_genelock_crush_thunder_stele", "gain_db": 1.5, "note": "四阶基因锁大圆满徒手捏碎天雷锁脉碑"},
            {"p": 35, "pos": "before", "slug": "nineteen_worlds_fusion_breakthrough", "sfx_prompt": "Colossal cosmic resonance of nineteen worlds merging into a blazing golden aura boom above vast clouds", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰！十九界本源归一晋升合道中期融界境"},
            {"p": 41, "pos": "before", "slug": "crimson_war_horn_across_void", "sfx_prompt": "Three deep mournful ancient bronze war horns echoing across infinite starry void", "duration_seconds": 4.0, "gain_db": 2.0, "note": "呜呜呜！三十三天镇界长城吹响血色号角"},
            {"p": 44, "pos": "before", "slug": "celestial_gates_open_million_armada", "sfx_prompt": "Titan star-fortress gates grinding open with rumbling armada engines and marching silver armor", "duration_seconds": 3.6, "gain_db": 1.5, "note": "轰隆隆！镇界天门洞开百万天兵倾巢而出"},
        ],
    )
    j103, m103 = save_episode_scripts(s103, REPO_SCRIPTS_DIR, registry)
    built.append(("E103", j103, m103, len(s103.cues), len(s103.acts)))

    # =========================================================================
    # E104 · 第104章 血战仙庭外三十三天，叩响牧神天门！ (55 paras, 18 quotes)
    # =========================================================================
    md_104 = SOURCE_DIR / "第104章_血战仙庭外三十三天，叩响牧神天门！.md"
    s104 = compile_episode_cue_sheet(
        episode_id="E104",
        chapter_number=104,
        source_md_path=md_104,
        source_rel_path=f"02_分章精修正文/{md_104.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_mother_world_ram_great_wall",
                "start_p": 1,
                "title": "第一幕 · 母界撞长城，百万破锁军",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_empress_freezes_two_lords_blade_duel",
                "start_p": 17,
                "title": "第二幕 · 冰凰拦双尊，魔躯硬扛火",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_cleave_furnace_slay_two_hedao_peek_taiyi",
                "start_p": 36,
                "title": "第三幕 · 一刀斩双尊，天帝初垂眸",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 55, "vast_hall")],
        skip_onomatopoeia_paras={9, 29, 32, 41},
        dialogue_specs=[
            {"match": "区区一群从猪圈皿笼里跑出来的下界泥腿子", "role_id": "sect_elder_antagonist", "speaker_name": "东华仙君", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "东华仙君手托赤金丹炉轻蔑怒喝"},
            {"match": "天帝法旨已下，凡沾染零号原胎与玄黄旧孽气息者", "role_id": "sect_elder_antagonist", "speaker_name": "东华仙君", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "东华仙君妄图将百万人塞进炼界炉炼丹"},
            {"match": "东华兄莫把炉火烧太旺，记得给本尊留几条化神洞虚的主魂下酒", "role_id": "chiyang_laozu", "speaker_name": "南极古尊", "tags": "[laughs] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "南极古尊缭绕惨白神火狞笑附和"},
            {"match": "破阵！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬立于苍穹最高处挥刀下令破阵"},
            {"match": "杀！替万界死难先辈讨还血债", "role_id": "lu_qingcang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍与萧烈立于破城巨舰舰首怒吼冲锋"},
            {"match": "一群疯狗，先斩了他们领头的两尊合道", "role_id": "pei_xuandu", "speaker_name": "西极金母", "tags": "[coldly] [angry]", "stability": 0.0, "space": "vast_hall", "note": "仙庭四大合道同时暴起企图四打二围杀"},
            {"match": "想以多欺少？问过本帝手中的剑", "role_id": "jiang_qinghuang", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰横跨千里展开太古冰凰神域"},
            {"match": "这两个老家伙归我拖住，东华和南极那两条老狗", "role_id": "jiang_qinghuang", "tags": "[coldly] [fiercely]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰独剑圈住西极与北辰两大合道后期"},
            {"match": "足够了！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬长啸迎面撞向东华与南极"},
            {"match": "不知天高地厚的小畜生，不过刚刚踏入合道中期", "role_id": "sect_elder_antagonist", "speaker_name": "东华仙君", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "东华仙君祭出千丈九转东华炼界炉当空罩落"},
            {"match": "太虚界九十代飞升修士的血债，今日一并找你清算", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬双眸燃起炽烈战火不退反进"},
            {"match": "什么！硬扛本尊寂灭神火而不伤", "role_id": "chiyang_laozu", "speaker_name": "南极古尊", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "南极古尊骇然惊见陆烬后背瞬息滴血重生"},
            {"match": "万法不侵，给本君镇", "role_id": "sect_elder_antagonist", "speaker_name": "东华仙君", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "东华仙君拼命催动炼界炉横挡胸前"},
            {"match": "区区一口吃人破炉，给我碎", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬左手抹去三成道纹右手高举断岳"},
            {"match": "这一刀，开天，斩锁", "role_id": "lu_jin", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "十九界山河伟力合一悍然劈出开天斩锁式"},
            {"match": "不！天帝救我", "role_id": "sect_elder_antagonist", "speaker_name": "东华仙君", "tags": "[desperately] [crying]", "stability": 0.0, "space": "vast_hall", "note": "东华仙君与南极古尊被一刀拦腰斩爆"},
            {"match": "东华和南极死了！快退，快回牧神天宫禀报天帝", "role_id": "pei_xuandu", "speaker_name": "北辰道君", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "剩余两尊合道狂喷金血撕裂虚空溃逃"},
            {"match": "全军冲锋，踏平镇界长城", "role_id": "male_guard_captain", "speaker_name": "萧烈", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈与陆擎苍振臂高呼撞塌三十三天核心关隘"},
        ],
        sfx_blueprint=[
            {"p": 9, "pos": "before", "slug": "mother_world_crash_void_storm", "sfx_prompt": "Colossal burning war-planet crashing through dimensional storms and halting before a star-fortress wall with thunderous war drums", "duration_seconds": 4.2, "gain_db": 2.0, "note": "轰隆隆！方寸玄黄母界横撞三十三天镇界长城"},
            {"p": 20, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "ice_phoenix_domain_freeze_void", "gain_db": 1.5, "note": "玄凰帝剑凌空一划冻结万里墟海时空"},
            {"p": 29, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "fourth_lock_demon_god_body", "gain_db": 1.5, "note": "轰！四阶基因锁大圆满全开不灭魔神战躯"},
            {"p": 32, "pos": "before", "slug": "spear_fire_explosion_instant_heal", "sfx_prompt": "Nine searing white fire spears exploding against golden armor followed by rapid surging blood regeneration", "duration_seconds": 2.8, "gain_db": 1.5, "note": "嘭！硬扛九道寂灭神火矛瞬息滴血重生"},
            {"p": 41, "pos": "before", "slug": "heaven_splitting_sabre_shatter_furnace", "sfx_prompt": "Earth-shattering broadsword slash cleaving a giant bronze cauldron in two with roaring cosmic shockwaves", "duration_seconds": 4.5, "gain_db": 2.5, "note": "咔嚓轰隆！一刀劈碎九转炼界炉阵斩双合道"},
        ],
    )
    j104, m104 = save_episode_scripts(s104, REPO_SCRIPTS_DIR, registry)
    built.append(("E104", j104, m104, len(s104.cues), len(s104.acts)))

    # =========================================================================
    # E105 · 第105章 万灵破锁大狂潮，诸界不再跪仙神 (74 paras, 21 quotes)
    # =========================================================================
    md_105 = SOURCE_DIR / "第105章_万灵破锁大狂潮，诸界不再跪仙神.md"
    s105 = compile_episode_cue_sheet(
        episode_id="E105",
        chapter_number=105,
        source_md_path=md_105,
        source_rel_path=f"02_分章精修正文/{md_105.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_inspect_central_token_deadly_backlash",
                "start_p": 1,
                "title": "第一幕 · 执掌中枢令，暗藏灭界咒",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_hijack_heavens_net_broadcast_three_thousand_worlds",
                "start_p": 21,
                "title": "第二幕 · 篡网昭铁证，万灵齐破锁",
                "bgm_prompt": WORLD_OST["w2_first_sunlight_catharsis"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act3_hedao_perfection_wall_of_sighs_taiyi_finger",
                "start_p": 53,
                "title": "第三幕 · 合道臻无极，源壁降帝指",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(1, 20, "vast_hall"), (38, 74, "vast_hall")],
        skip_onomatopoeia_paras={25, 35, 42, 61},
        dialogue_specs=[
            {"match": "别直接用蛮力震碎它", "role_id": "jiang_qinghuang", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰收剑落于陆烬身侧出言提醒"},
            {"match": "这枚中枢令连着东华辖区的监天子网", "role_id": "jiang_qinghuang", "tags": "[calmly] [hoarsely]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰道出中枢令底层的反噬死咒"},
            {"match": "一旦中枢令被外力强行毁去，子网会在三息之内", "role_id": "jiang_qinghuang", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰指尖剑意点出三千界灭界清洗暗门"},
            {"match": "好狠的手段，连战败退走前都要拿三千界众生作人质", "role_id": "lu_qingcang", "tags": "[angry]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍踏空掠来怒斥仙庭毒计"},
            {"match": "那这玩意儿岂不是成了烫手山芋", "role_id": "lu_qingcang", "tags": "[angry] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍沉声骂道进退两难"},
            {"match": "东华老贼统御东域三千界数万年", "role_id": "li_cang", "speaker_name": "莫问天", "tags": "[hoarsely]", "stability": 0.5, "space": "vast_hall", "note": "莫问天拭去断剑血迹分析分兵之危"},
            {"match": "仙庭修这张监天网，本是为了居高临下向三千牧场降下法旨", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬借木马魂波段试探成功后嘴角微扬"},
            {"match": "水能顺着管子往上抽，自然也能顺着管子往下灌", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "note": "陆烬提出反向借监天网广播三千界"},
            {"match": "陆盟主的意思是，不毁子网，反而篡改这枚中枢令的下行法旨", "role_id": "weathered_elder_npc", "speaker_name": "季长生", "tags": "[gasps] [dramatically]", "stability": 0.0, "note": "季长生眼睛猛地一亮领会奇策"},
            {"match": "不错", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬淡声颔首"},
            {"match": "季先生助我稳住三千子网的分流阵频", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬分派季长生与姜清凰联手改令"},
            {"match": "五息都够，动手便是", "role_id": "jiang_qinghuang", "tags": "[coldly]", "stability": 0.5, "note": "姜清凰唇角微扬傲岸应允"},
            {"match": "三千世界，凡有血气者，今日且抬头看天", "role_id": "lu_jin", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬捏爆中枢令向三千世界广播铁证与破锁真解"},
            {"match": "原来头顶根本没有救苦救难的上界真仙", "role_id": "male_disciple_a", "speaker_name": "下界金丹修士", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "低维世界修士看清活人炼丹铁证怒吼"},
            {"match": "所谓天劫入魔，竟是锁死吾辈血脉的屠夫铁链", "role_id": "sect_elder_antagonist", "speaker_name": "白发剑圣", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "枯坐三百载的白发剑圣引燃热血崩断枷锁"},
            {"match": "不跪了！今日便是碎骨燃魂，我辈也要自己劈开这方囚笼", "role_id": "male_disciple_b", "speaker_name": "万界破锁众修", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三千世界压抑万古的怒吼逆流回传"},
            {"match": "当年白骨灯城亮起第一缕阳光时", "role_id": "female_maid_npc", "speaker_name": "沈烛音", "tags": "[softly] [crying]", "stability": 0.0, "space": "vast_hall", "note": "沈烛音眼眶微红感慨三千人间同见太阳"},
            {"match": "来得好！", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬迎纳万界破锁愿力共鸣"},
            {"match": "全军止步结阵！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬于叹息源壁前抬手喝令稳住前锋"},
            {"match": "到了，这就是隔绝牧场与仙庭中枢的【叹息源壁】", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰肃然指认原初牧神天宫外墙"},
            {"match": "墙体掺了第九境秩序碎片，寻常合道硬撼必伤道基", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬高举断岳欲劈开叹息源壁"},
        ],
        sfx_blueprint=[
            {"p": 25, "pos": "before", "slug": "jade_token_channel_hum", "sfx_prompt": "Crisp metallic-jade token chiming softly as an arcane silver transmission channel unlocks", "duration_seconds": 2.2, "gain_db": 1.0, "note": "嗡！分界中枢令敞开单向广播通道"},
            {"p": 35, "pos": "before", "slug": "erase_seal_shatter_broadcast_gold", "sfx_prompt": "Sharp crystalline seal cracking followed by a blinding golden shockwave surging through thousands of starlight conduits", "duration_seconds": 4.0, "gain_db": 2.0, "note": "咔嚓轰隆！抹去仙庭禁令向三千世界灌入破锁真解"},
            {"p": 47, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "myriad_worlds_genelock_shatter", "gain_db": 1.5, "note": "三千世界无数修士引燃热血崩断基因枷锁"},
            {"p": 61, "pos": "before", "slug": "hedao_grand_perfection_zenith", "sfx_prompt": "Deep resonant cosmic bell and surging golden qi tide calming chaotic void storms into tranquil perfection", "duration_seconds": 3.5, "gain_db": 1.5, "note": "轰！陆烬与姜清凰双双晋升合道境大圆满"},
            {"p": 72, "pos": "before", "slug": "absolute_void_silence_drop", "sfx_prompt": "Deafening sub-bass vacuum drop abruptly muting all ambient noise into eerie bone-chilling silence", "duration_seconds": 2.8, "gain_db": 2.0, "note": "沸腾墟海骤然陷入绝对死寂，天帝隔空点出一指"},
        ],
    )
    j105, m105 = save_episode_scripts(s105, REPO_SCRIPTS_DIR, registry)
    built.append(("E105", j105, m105, len(s105.cues), len(s105.acts)))

    # =========================================================================
    # E106 · 第106章 天帝隔空灭世指，生死关头心跳再停！ (68 paras, 19 quotes)
    # =========================================================================
    md_106 = SOURCE_DIR / "第106章_天帝隔空灭世指，生死关头心跳再停！.md"
    s106 = compile_episode_cue_sheet(
        episode_id="E106",
        chapter_number=106,
        source_md_path=md_106,
        source_rel_path=f"02_分章精修正文/{md_106.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_true_immortal_erasure_law_nine_slashes_vanish",
                "start_p": 1,
                "title": "第一幕 · 母碑抹名律，九刀归虚无",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_empress_nine_shields_shatter_erasing_memories",
                "start_p": 35,
                "title": "第二幕 · 九阙护孤刃，泣血抗抹痕",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_third_heart_stop_fifth_soul_steps_out",
                "start_p": 56,
                "title": "第三幕 · 心跳三度止，麻衣出孤坟",
                "bgm_prompt": WORLD_OST["f1_fifth_soul_tragic_mirror"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(1, 57, "vast_hall"), (58, 68, "mental_realm")],
        skip_onomatopoeia_paras={33, 38, 44, 50, 57, 59},
        dialogue_specs=[
            {"match": "陆烬，快退！这不是合道神通", "role_id": "jiang_qinghuang", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰脸色骤变急喝提醒真仙母碑抹名律"},
            {"match": "唯有执掌万界源头的真仙，才能不借灵气招式", "role_id": "jiang_qinghuang", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄凰女帝清冷嗓音首现撕裂急促"},
            {"match": "主上醒了……零号，你逃不掉的", "role_id": "eternal_night_whisper", "speaker_name": "太一木马魂", "tags": "[trembling] [desperately]", "stability": 0.0, "space": "mental_realm", "note": "第六环青铜囚笼内太一木马魂自燃成灰"},
            {"match": "季长生，立刻斩断全军与我的气机共鸣链", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬果断斩断阵链护住身后百万联军"},
            {"match": "他冲的是我体内【第零号原胎】的底层编码", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬严令父亲与战舰不许踏入白域"},
            {"match": "盟主小心，这股规则不在八境五行之内", "role_id": "weathered_elder_npc", "speaker_name": "季长生", "tags": "[desperately] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "季长生喷血断阵骇然示警"},
            {"match": "第零号失控样本，毁吾三千界供奉", "role_id": "tai_yi", "tags": "[coldly] [calmly]", "stability": 1.0, "space": "mental_realm", "note": "太一绝对理智无悲无喜的抹名宣判直贯泥丸宫"},
            {"match": "拿我当写歪的墨迹？我陆烬一步步修出来的命", "role_id": "lu_jin", "tags": "[angry] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "生死绝境压顶陆烬凶悍血性炸裂"},
            {"match": "开天斩锁，给我破", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬燃烧合道无极修为迎指连劈九刀"},
            {"match": "陆烬！", "role_id": "jiang_qinghuang", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰横跨半步决然挡在陆烬身前"},
            {"match": "太上玄凰，九重帝阙，凝", "role_id": "jiang_qinghuang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰透支帝心倒插帝剑撑开九重冰凰帝盾"},
            {"match": "清凰，快退开！这一指锁的是零号原胎源码", "role_id": "lu_jin", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "双腿半透明化的陆烬双目赤红欲拉开姜清凰"},
            {"match": "三千年前我躺进寒棺，让他一个人碎了元神去背万古骂名", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰唇角溢血九死不悔死守陆烬身前"},
            {"match": "烬儿！放开老子的儿子", "role_id": "lu_qingcang", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "十里白域外陆擎苍独臂狂劈屏障嘶吼"},
            {"match": "不对劲！季先生，为什么我脑子里突然有点记不清", "role_id": "lu_qingcang", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍惊觉天帝正在抹除儿子生平记忆虎目泣血"},
            {"match": "少主！俺记着呢，北渊西城的老槐树", "role_id": "shi_meng", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "石猛红着眼眶拼死砸向屏障死记北渊旧事"},
            {"match": "陆烬，撑住", "role_id": "jiang_qinghuang", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "第九重帝盾炸碎姜清凰喋血掀飞伸手抓空"},
            {"match": "想让我认命归零……你还不够格", "role_id": "lu_jin", "tags": "[hoarsely] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "巨指距眉心半寸陆烬死扣断岳齿缝挤出低吼"},
            {"match": "又是他……心脏里那第五道魂", "role_id": "lu_jin", "tags": "[whispers] [gasps]", "stability": 0.0, "space": "mental_realm", "note": "凝固猩红世界里陆烬注视心脏命窍亮起暗金残烛"},
        ],
        sfx_blueprint=[
            {"p": 33, "pos": "before", "slug": "duanyue_blade_crack_backlash", "sfx_prompt": "Heavy dark-gold broadsword cracking sharply under invisible cosmic erasure pressure", "duration_seconds": 2.4, "gain_db": 1.5, "note": "咔嚓！断岳刀身崩裂虎口炸碎"},
            {"p": 38, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "nine_phoenix_shields_deploy", "gain_db": 1.5, "note": "轰轰轰！九重太上玄凰冰晶帝盾层层撑开"},
            {"p": 44, "pos": "before", "slug": "ice_shields_crumble_to_dust", "sfx_prompt": "Rapid succession of colossal crystalline ice shields shattering into fine dust", "duration_seconds": 3.0, "gain_db": 2.0, "note": "咔咔咔！七重冰凰帝盾接连化作透明粉末"},
            {"p": 50, "pos": "before", "slug": "ninth_shield_burst_final_impact", "sfx_prompt": "Massive crystalline ice barrier exploding completely with a violent shockwave", "duration_seconds": 2.8, "gain_db": 2.0, "note": "砰！第九重玄凰帝盾炸碎成漫天冰晶"},
            {"p": 57, "pos": "before", "slug": "third_heart_stop_cosmic_clock_freeze", "sfx_prompt": "Single monumental deep heartbeat thud abruptly halting into a crisp metallic clockwork time-stop click", "duration_seconds": 3.6, "gain_db": 2.5, "note": "咚——咔！心脏第三次停跳，按停宇宙时光沙漏"},
        ],
    )
    j106, m106 = save_episode_scripts(s106, REPO_SCRIPTS_DIR, registry)
    built.append(("E106", j106, m106, len(s106.cues), len(s106.acts)))

    # =========================================================================
    # E107 · 第107章 心脏第五魂真容：来自失败终局的自己！ (70 paras, 24 quotes)
    # =========================================================================
    md_107 = SOURCE_DIR / "第107章_心脏第五魂真容：来自失败终局的自己！.md"
    s107 = compile_episode_cue_sheet(
        episode_id="E107",
        chapter_number=107,
        source_md_path=md_107,
        source_rel_path=f"02_分章精修正文/{md_107.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_withered_back_broken_duanyue_true_face",
                "start_p": 1,
                "title": "第一幕 · 麻衣拄断岳，转身见吾颜",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_failed_timeline_forty_seven_millennia_lone_blade",
                "start_p": 32,
                "title": "第二幕 · 旧纪皆成骨，孤刀四万年",
                "bgm_prompt": WORLD_OST["f1_fifth_soul_tragic_mirror"],
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act3_three_breaths_of_ash_smile_toward_finger",
                "start_p": 53,
                "title": "第三幕 · 心坟守余烬，含笑赴仙指",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 70, "mental_realm")],
        skip_onomatopoeia_paras=set(),
        dialogue_specs=[
            {"match": "前辈……究竟是谁", "role_id": "lu_jin", "tags": "[hoarsely] [whispers]", "stability": 0.0, "space": "mental_realm", "note": "静止猩红世界里陆烬凝视麻衣老人背影"},
            {"match": "为何你的刀，与我的【断岳】一模一样", "role_id": "lu_jin", "tags": "[hoarsely] [trembling]", "stability": 0.0, "space": "mental_realm", "note": "陆烬认出老人手中半截锈蚀断岳"},
            {"match": "咳……咳咳", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[hoarsely] [sighs]", "stability": 0.0, "space": "mental_realm", "note": "麻衣老人低头轻咳指缝飘落灰烬魂光"},
            {"match": "你是……我", "role_id": "lu_jin", "tags": "[gasps] [trembling]", "stability": 0.0, "space": "mental_realm", "note": "看清老人面庞轮廓陆烬如遭惊雷僵在原地"},
            {"match": "别叫前辈，听着怪生分的", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[softly]", "stability": 0.5, "space": "mental_realm", "note": "暮年陆烬独眼打量年轻自己扯出温和笑意"},
            {"match": "叫声老头子就行……毕竟我这把烂骨头", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[hoarsely] [softly]", "stability": 0.5, "space": "mental_realm", "note": "暮年陆烬沙哑熟稔道出多熬了四万七千年"},
            {"match": "父母皆殁，故友尽绝，连棺中最后那个能说话的人", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[calmly] [hoarsely]", "stability": 0.5, "space": "mental_realm", "note": "暮年陆烬低头看锈刀平静诉说失败终局"},
            {"match": "从那以后，诸天三千界，就只剩我一把孤刀了", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[softly] [sighs]", "stability": 0.5, "space": "mental_realm", "note": "枯瘦指节用力发白道尽万古孤寂"},
            {"match": "后来呢？你杀进牧神天宫了", "role_id": "lu_jin", "tags": "[hoarsely] [trembling]", "stability": 0.0, "space": "mental_realm", "note": "青年陆烬眼眶滚烫攥拳渗出金血追问"},
            {"match": "杀进去了", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "暮年陆烬沉声回应"},
            {"match": "我背着一口空棺材，提着半截断刀，花了四万七千年", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[fiercely] [hoarsely]", "stability": 0.0, "space": "mental_realm", "note": "暮年陆烬独眼掠过滔天凶戾忆及血战凌霄"},
            {"match": "可惜啊", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[sighs] [softly]", "stability": 0.5, "space": "mental_realm", "note": "老人抬头看静止巨指轻叹"},
            {"match": "太一执掌【天道母碑】无数纪元，我与他在源海堤坝上血战九天九夜", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[calmly] [hoarsely]", "stability": 0.5, "space": "mental_realm", "note": "心死如灰推不开第五阶基因锁惜败半招"},
            {"match": "第九境真仙陨落尚可重入轮回，你为何会变成这样", "role_id": "lu_jin", "tags": "[gasps] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "陆烬心神剧震失声追问"},
            {"match": "轮回？", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "暮年陆烬嗤笑摇头"},
            {"match": "入了太一执掌的轮回，不过是再当一回没有记忆的笼中猪羊", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[hoarsely] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "燃尽真仙道果与九成九元神逆流万古退回秋雨夜"},
            {"match": "我逆流万古回来时，只剩最后三口气的余烬了", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[softly] [hoarsely]", "stability": 0.5, "space": "mental_realm", "note": "道出二十余载沉默守望的真相"},
            {"match": "那时候太一的木马魂就蹲在你视神经里盯着", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[whispers] [calmly]", "stability": 0.5, "space": "mental_realm", "note": "解释为避时间悖论不敢泄露半点真仙气息"},
            {"match": "所以我只能把所有真仙记忆封死，缩在你心窝子里装一块死木头", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[softly] [sighs]", "stability": 0.5, "space": "mental_realm", "note": "自嘲在心窝里当守墓老头"},
            {"match": "好在，十八岁的陆烬从来没让我失望过", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[laughs] [softly]", "stability": 0.0, "space": "mental_realm", "note": "浑浊独眼满是快慰与骄傲"},
            {"match": "真好啊", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[softly] [crying]", "stability": 0.0, "space": "mental_realm", "note": "遥望战场活着的父亲石猛与姜清凰眼角微光"},
            {"match": "这一世，福伯善终，爹还在，她也醒着站在你身边", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[softly] [laughs]", "stability": 0.0, "space": "mental_realm", "note": "苍老脸庞绽开从未有过的灿烂笑容"},
            {"match": "老头子，回来！把你的刀意借给我", "role_id": "lu_jin", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "mental_realm", "note": "青年陆烬察觉决死火光上前伸手欲拉住老人"},
            {"match": "傻小子，逆流回来的孤魂野鬼，本来就是替你挡这一劫的骨灰薪柴啊", "role_id": "fifth_soul_self", "speaker_name": "暮年陆烬", "tags": "[softly] [laughs]", "stability": 0.0, "space": "mental_realm", "note": "暮年陆烬含笑推回年轻自己转身迎向灭世巨指"},
        ],
        sfx_blueprint=[
            {"p": 8, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "rusted_duanyue_cane_tap", "gain_db": 1.0, "note": "半截锈迹斑斑的断岳残刀拄立在凝固时空"},
            {"p": 32, "pos": "before", "slug": "flick_ash_memory_ripple", "sfx_prompt": "Finger flicking dust off an ancient rusted iron blade triggering a deep echoing time-river memory chime", "duration_seconds": 3.0, "gain_db": 1.0, "note": "弹去锈刀灰尘，映出失败终局时间线"},
            {"p": 42, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "failed_timeline_coffin_shatter_memory", "gain_db": 1.0, "note": "旧时间线木马魂引爆，棺中姜清凰冰消瓦解"},
            {"p": 70, "pos": "before", "slug": "shatter_crimson_void_charge_finger", "sfx_prompt": "Frozen glass-like time barrier shattering as resolute footsteps charge forward gripping a rusted iron blade", "duration_seconds": 3.5, "gain_db": 2.0, "note": "枯骨守墓人一步踏碎猩红噪点迎撞真仙巨指"},
        ],
    )
    j107, m107 = save_episode_scripts(s107, REPO_SCRIPTS_DIR, registry)
    built.append(("E107", j107, m107, len(s107.cues), len(s107.acts)))

    # =========================================================================
    # E108 · 第108章 守墓人含笑化薪柴，一念半步入真仙！ (80 paras, 20 quotes)
    # =========================================================================
    md_108 = SOURCE_DIR / "第108章_守墓人含笑化薪柴，一念半步入真仙！.md"
    s108 = compile_episode_cue_sheet(
        episode_id="E108",
        chapter_number=108,
        source_md_path=md_108,
        source_rel_path=f"02_分章精修正文/{md_108.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_rusted_blade_clashes_divine_finger_shatters",
                "start_p": 1,
                "title": "第一幕 · 残刀撼仙指，燃魂破天算",
                "bgm_prompt": WORLD_OST["f4_final_battle_slay_taiyi"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_golden_rain_farewell_secret_under_throne",
                "start_p": 28,
                "title": "第二幕 · 金雨归心窍，遗言指王座",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act3_half_step_true_immortal_cleave_wall_of_sighs",
                "start_p": 48,
                "title": "第三幕 · 半步入真仙，一刀劈源壁",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 80, "vast_hall")],
        skip_onomatopoeia_paras={1, 6, 12, 14, 22, 24, 45, 47, 60, 74},
        dialogue_specs=[
            {"match": "嗯？", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一古井无波的神念亿万年来首次泛起波澜"},
            {"match": "逆流源海的残灰？上一纪本已抹除的败犬", "role_id": "tai_yi", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一催动三倍真仙秩序神焰灼烧残魂"},
            {"match": "既定天算？太一，你少在那儿装什么全知全能的天道", "role_id": "shou_mu_ren", "speaker_name": "守墓老人", "tags": "[laughs] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "守墓老人冲着源壁后王座发出震天沙哑狂笑"},
            {"match": "上一世老子孤家寡人、心死如灰，尚能杀进你的凌霄殿", "role_id": "shou_mu_ren", "speaker_name": "守墓老人", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "守墓老人傲然历数这一世陆烬身后的万家灯火"},
            {"match": "给老子……碎", "role_id": "shou_mu_ren", "speaker_name": "守墓老人", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "燃尽最后三口心头余烬与真仙刀骨贯入巨指"},
            {"match": "呼！", "role_id": "lu_jin", "tags": "[gasps] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "概念抹除白域崩解陆烬血肉重凝大口喘息"},
            {"match": "烬儿！", "role_id": "lu_qingcang", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "记忆恢复清明的陆擎苍破空冲来"},
            {"match": "陆烬！", "role_id": "jiang_qinghuang", "tags": "[gasps] [softly]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰化作素白惊虹掠至近前"},
            {"match": "老头子，别散！进我的玄黄界", "role_id": "lu_jin", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "青年陆烬伸手拼命想拢住溃散的金色光雨"},
            {"match": "傻小子，这天地间，有一个活生生的陆烬就够了", "role_id": "shou_mu_ren", "speaker_name": "守墓老人", "tags": "[softly] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "老人笑着侧身避开手掌"},
            {"match": "我这座坟守完了，也该合上眼歇歇啦", "role_id": "shou_mu_ren", "speaker_name": "守墓老人", "tags": "[softly] [sighs]", "stability": 0.5, "space": "vast_hall", "note": "老人虚拍青年陆烬右肩卸下万古重担"},
            {"match": "去牧神天宫最底层的【天道母碑】王座看看吧", "role_id": "shou_mu_ren", "speaker_name": "守墓老人", "tags": "[whispers] [hoarsely]", "stability": 0.5, "space": "mental_realm", "note": "消散前最后一息以心血密音嘱托王座下的骨头"},
            {"match": "记住，无论看到什么，别变回那个高高在上、没有心的神", "role_id": "shou_mu_ren", "speaker_name": "守墓老人", "tags": "[whispers] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "守墓人最后一句振聋发聩的叮嘱"},
            {"match": "陆烬，方才替你挡下天帝一指的那位前辈", "role_id": "jiang_qinghuang", "tags": "[softly] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰落回身畔震动询问老人相似眉眼"},
            {"match": "他不是外人，是一个在更黑的夜里替我们蹚过绝路的守墓人", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬替姜清凰抚平伤势轻声致敬守墓人"},
            {"match": "他走累了，把剩下的最后半程路，交给我们走完", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "陆烬松手独自向前迈出一步"},
            {"match": "好强的刀势……连这片墟海的法则都在向盟主低头", "role_id": "weathered_elder_npc", "speaker_name": "季长生", "tags": "[gasps] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "季长生震骇仰望半步无上真仙仙威"},
            {"match": "好小子！没给咱们北渊陆氏丢人", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍抹去眼角血水拍刀放声大笑"},
            {"match": "太一，你躲在墙后擦了我两世", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬踏至叹息源壁前举刀过顶"},
            {"match": "今日，换我来掀你的王座", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "两世刀心合一悍然劈开亘古叹息源壁"},
        ],
        sfx_blueprint=[
            {"p": 6, "pos": "before", "slug": "rusted_blade_bell_clash_divine_finger", "sfx_prompt": "Monumental ancient bronze bell-like metallic clash as a broken iron blade halts a colossal celestial energy pillar", "duration_seconds": 3.8, "gain_db": 2.5, "note": "铛——！半截断岳残刀硬生生架停真仙白金巨指"},
            {"p": 24, "pos": "before", "slug": "golden_fire_shatter_celestial_finger", "sfx_prompt": "Roaring golden soul-fire imploding inside a giant crystal pillar and shattering it into booming shockwaves", "duration_seconds": 4.0, "gain_db": 2.5, "note": "咔嚓轰！金色薪柴引爆震碎天帝灭世巨指"},
            {"p": 47, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "two_lifetimes_heartbeat_drum", "gain_db": 2.0, "note": "咚咚咚！两世刀心归一心跳过处如太古战鼓擂响"},
            {"p": 60, "pos": "before", "slug": "half_step_immortal_fifth_gate_loom", "sfx_prompt": "Crisp dimensional barrier cracking open followed by colossal ancient bronze gates rumbling in deep cosmic mist", "duration_seconds": 3.8, "gain_db": 2.0, "note": "咔嚓！冲破仙凡壁垒晋升半步真仙，显露五阶源门"},
            {"p": 74, "pos": "before", "slug": "cleave_wall_of_sighs_hundred_miles", "sfx_prompt": "Heaven-rending broadsword slash splitting an infinite stone-and-law wall open with parting storm clouds", "duration_seconds": 4.5, "gain_db": 2.5, "note": "轰隆——！一刀劈开叹息源壁百里通天巨壑"},
        ],
    )
    j108, m108 = save_episode_scripts(s108, REPO_SCRIPTS_DIR, registry)
    built.append(("E108", j108, m108, len(s108.cues), len(s108.acts)))

    # =========================================================================
    # E109 · 第109章 兵临原初牧神天宫，故人齐聚守天门 (78 paras, 23 quotes)
    # =========================================================================
    md_109 = SOURCE_DIR / "第109章_兵临原初牧神天宫，故人齐聚守天门.md"
    s109 = compile_episode_cue_sheet(
        episode_id="E109",
        chapter_number=109,
        source_md_path=md_109,
        source_rel_path=f"02_分章精修正文/{md_109.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_abyssal_origin_sea_south_heaven_gate_blockade",
                "start_p": 1,
                "title": "第一幕 · 源海立天宫，十万无面卫",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_seven_worlds_companions_hold_south_gate",
                "start_p": 26,
                "title": "第二幕 · 七界故人聚，温酒守天门",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act3_blade_and_sword_ascend_nine_palaces_open_lingxiao",
                "start_p": 53,
                "title": "第三幕 · 刀剑破九阙，推门见太一",
                "bgm_prompt": WORLD_OST["f3_celestial_palace_confrontation"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 78, "vast_hall")],
        skip_onomatopoeia_paras={14, 16, 58, 72},
        dialogue_specs=[
            {"match": "低头敛识，化神以下莫要直视天宫后面的那片黑海", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬挥出百里暗金刀幕替大军隔绝源海疯魔气息"},
            {"match": "太上皇室孤本里曾有一句残缺记载", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰忌惮凝望归墟大寂灭源海"},
            {"match": "叛逆陆烬，还有太上余孽姜清凰", "role_id": "pei_xuandu", "speaker_name": "西极古尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "带伤的西极古尊与北辰仙君率十万神卫拦门"},
            {"match": "莫以为仗着外道残魂碎了天帝陛下一缕隔空指影", "role_id": "pei_xuandu", "speaker_name": "西极古尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "西极古尊色厉内荏结起周天牧神锁界大阵"},
            {"match": "他们在拖延时间", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬瞬息看穿两尊古尊拖延算盘"},
            {"match": "这座锁界大阵守强攻弱，而且阵眼深处连着天宫核心", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬点破太一遭反噬需蓄力调动母碑"},
            {"match": "盟主所言极是！此阵与十万无面神卫性命相连", "role_id": "weathered_elder_npc", "speaker_name": "季长生", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "季长生凝重印证三炷香内真仙气机将复苏"},
            {"match": "三炷香？半息老子都不给那狗屁天帝留", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍在旗舰舰首放声豪笑拔出千钧阔刀"},
            {"match": "烬儿，你还回头看啥？外头这些没脸的杂鱼", "role_id": "lu_qingcang", "tags": "[laughs] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍跨上栏杆让儿子与女帝放手进宫掀桌"},
            {"match": "陆伯父说得好！太上镇狱军等这一天", "role_id": "male_guard_captain", "speaker_name": "萧烈", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄黄少帅萧烈高举战戟响应"},
            {"match": "末将萧烈，愿率镇狱军死钉南天门左翼", "role_id": "male_guard_captain", "speaker_name": "萧烈", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈率三十万太上遗民精锐请命死守左翼"},
            {"match": "算我太虚剑修一份", "role_id": "li_cang", "speaker_name": "莫问天", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "断耳疯剑修莫问天朗笑拔剑"},
            {"match": "老夫在画纸笼子里憋屈了八百年", "role_id": "li_cang", "speaker_name": "莫问天", "tags": "[fiercely] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "莫问天古剑斜指北辰仙君"},
            {"match": "烬昼守昼剑阵，领右翼", "role_id": "female_maid_npc", "speaker_name": "沈烛音", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "沈烛音长剑出鞘如烈日初升"},
            {"match": "万魂渊儿郎，随本座撕开他们中军", "role_id": "hongxiu_louzhu", "speaker_name": "夜琉璃", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "夜琉璃率魔渊修士压上侧翼"},
            {"match": "少主只管进去砍翻那鸟天帝！季老先生已经把三十六门合道破界神炮", "role_id": "shi_meng", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "石猛拍胸怒吼已在船舱温好十坛老槐树黄酒"},
            {"match": "季先生，以【方寸玄黄母阵】为基", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬干净利落抱拳嘱托季长生稳困双尊"},
            {"match": "石猛，把北渊的酒温好了，等我出来喝", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬嘴角扬起锋芒弧度与故人定下归约"},
            {"match": "得令！", "role_id": "male_disciple_a", "speaker_name": "破锁联军", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百万联军齐声怒吼震动南天门牌坊"},
            {"match": "杀！结万界破锁大阵，替盟主开道", "role_id": "lu_qingcang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍一马当先挥刀率四路大军撞上神卫"},
            {"match": "拦住那小畜生，绝不能让他进内宫", "role_id": "pei_xuandu", "speaker_name": "西极古尊", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "西极古尊与北辰仙君惊骇欲抽身拦截"},
            {"match": "滚开！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬与姜清凰刀剑合璧一击重创轰飞双尊"},
            {"match": "走！", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬携姜清凰一步跨过崩塌的南天门直杀九重帝阙"},
        ],
        sfx_blueprint=[
            {"p": 14, "pos": "before", "slug": "south_heaven_gate_horn_ten_thousand_pillars", "sfx_prompt": "Deep ancient celestial horn followed by myriad metallic armor formations locking spears in unison", "duration_seconds": 3.5, "gain_db": 1.5, "note": "呜——轰！牧神南天门号角拉响十万无面神卫结阵"},
            {"p": 51, "pos": "before", "slug": "thirty_six_world_breaker_cannons_volley", "sfx_prompt": "Thirty-six colossal arcane siege cannons firing a deafening synchronized volley amidst charging armored legions", "duration_seconds": 3.8, "gain_db": 2.0, "note": "三十六门合道破界神炮齐射，百万联军开道"},
            {"p": 58, "pos": "before", "slug": "blade_and_phoenix_sword_combined_strike", "sfx_prompt": "Heavy dark-gold broadsword roar and crystalline ice-phoenix sword chime striking together in an explosive boom", "duration_seconds": 3.2, "gain_db": 2.0, "note": "轰噗嗤！刀剑合璧一击轰飞西极与北辰双尊"},
            {"p": 72, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "lingxiao_palace_doors_grind_open", "gain_db": 2.0, "note": "轰隆隆！推开太一凌霄宝殿尘封万古的白金巨门"},
        ],
    )
    j109, m109 = save_episode_scripts(s109, REPO_SCRIPTS_DIR, registry)
    built.append(("E109", j109, m109, len(s109.cues), len(s109.acts)))

    # =========================================================================
    # E110 · 第110章 踏入凌霄见太一，王座下的无头原初尸！ (73 paras, 12 quotes)
    # =========================================================================
    md_110 = SOURCE_DIR / "第110章_踏入凌霄见太一，王座下的无头原初尸！.md"
    s110 = compile_episode_cue_sheet(
        episode_id="E110",
        chapter_number=110,
        source_md_path=md_110,
        source_rel_path=f"02_分章精修正文/{md_110.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_footsteps_in_lingxiao_confront_taiyi",
                "start_p": 1,
                "title": "第一幕 · 踏足凌霄殿，剑指牧神座",
                "bgm_prompt": WORLD_OST["f3_celestial_palace_confrontation"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_mother_stele_weeps_nine_layers_white_fog",
                "start_p": 28,
                "title": "第二幕 · 母碑悲鸣警，九重遮羞雾",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_true_eyes_rip_fog_headless_primordial_corpse",
                "start_p": 47,
                "title": "第三幕 · 真目撕神雾，无头原初尸",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 110.0,
            },
        ],
        acoustic_ranges=[(1, 73, "vast_hall")],
        skip_onomatopoeia_paras={47, 53, 67},
        dialogue_specs=[
            {"match": "太一！", "role_id": "jiang_qinghuang", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰停在母碑前五百丈玄凰帝剑直指白玉王座"},
            {"match": "三千年前，你在我玄黄母界万部道经里暗植收割死门", "role_id": "jiang_qinghuang", "tags": "[coldly] [angry]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰清冷彻骨质问三千年玄黄血债"},
            {"match": "玄黄也好，大苍也罢，在母碑的账册上", "role_id": "tai_yi", "tags": "[calmly]", "stability": 1.0, "space": "vast_hall", "note": "王座上太一温和却无悲无喜俯视陆烬"},
            {"match": "既然见过了外头的终极恐怖，为何还要毁我三千界秩序", "role_id": "tai_yi", "tags": "[calmly] [coldly]", "stability": 1.0, "space": "vast_hall", "note": "太一轻抬愈合刀痕的食指指向殿外源海"},
            {"match": "三千纪元以来，能活着跨进凌霄殿门槛", "role_id": "tai_yi", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一道出陆烬两世皆是同一个变数"},
            {"match": "母碑在畏惧你？不对，它在向你的气血示警哀鸣", "role_id": "jiang_qinghuang", "tags": "[gasps] [whispers]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰敏锐察觉天道母碑向陆烬气血低头悲鸣"},
            {"match": "陆烬，你看母碑最底下的白玉地基", "role_id": "jiang_qinghuang", "tags": "[whispers]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰压低声音指向母碑根部异常"},
            {"match": "好古怪的障眼禁制！在我的神识感应里", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰神识探入九层白雾被琉璃般滑开"},
            {"match": "太一，你口口声声说诸界只是你的保育皿", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬忆起守墓人遗言停在两百丈处开口试探"},
            {"match": "既然你便是天道本身，又何必在自己脚下的王座地基上", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬刀锋斜指王座冷声揭穿九层遮羞白雾"},
            {"match": "你既然已经走到了第五阶源门之前，想看，那便自己睁眼看清楚", "role_id": "tai_yi", "tags": "[calmly] [coldly]", "stability": 1.0, "space": "vast_hall", "note": "太一垂下白金眸子并未阻拦"},
            {"match": "王座地基底下钉着的……竟是一具太初神躯", "role_id": "jiang_qinghuang", "tags": "[gasps] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰看清雾下真容指尖寒气炸碎失声发颤"},
        ],
        sfx_blueprint=[
            {"p": 7, "pos": "before", "slug": "echoing_footsteps_vast_star_hall", "sfx_prompt": "Two pairs of steady footsteps echoing clearly across polished cold stone in a colossal silent cathedral-like hall", "duration_seconds": 3.2, "gain_db": 1.0, "note": "两人脚步声在死寂空旷的凌霄宝殿内清晰回荡"},
            {"p": 33, "pos": "before", "slug": "mother_stele_mournful_stone_hum", "sfx_prompt": "Colossal ancient monolith trembling slightly with a deep resonant metallic-stone mournful vibration", "duration_seconds": 3.4, "gain_db": 1.5, "note": "万丈天道母碑感应无漏金血轻微颤抖低沉嗡鸣"},
            {"p": 47, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "fifth_gate_crack_true_eyes_open", "gain_db": 1.5, "note": "轰！第五阶青铜源门震开一线，破妄真目极致全开"},
            {"p": 53, "pos": "before", "slug": "true_gaze_rip_nine_order_fogs", "sfx_prompt": "Crackling violet lightning gaze ripping cleanly through nine dense layers of ethereal mist into a dark abyss", "duration_seconds": 3.0, "gain_db": 2.0, "note": "嗤啦——！破妄真目撕裂九重纯白秩序神雾"},
            {"p": 67, "pos": "before", "slug": "zero_bronze_tag_resonates_collarbone", "sfx_prompt": "High-pitched tragic ancient bronze talisman ringing and resonating with ninety-nine thousand clinking chains in a deep pit", "duration_seconds": 4.2, "gain_db": 2.0, "note": "嗡！零号青铜铭牌飞浮铮鸣，与无头原初古尸锁骨缺口共鸣"},
        ],
    )
    j110, m110 = save_episode_scripts(s110, REPO_SCRIPTS_DIR, registry)
    built.append(("E110", j110, m110, len(s110.cues), len(s110.acts)))

    return built


if __name__ == "__main__":
    results = build_batch15_e101_e110()
    print(f"Successfully compiled {len(results)} episodes for Batch 15 (E101-E110):")
    for ep_id, j_path, m_path, n_cues, n_acts in results:
        print(f"  {ep_id}: acts={n_acts}, cues={n_cues} -> {j_path.name} / {m_path.name}")
