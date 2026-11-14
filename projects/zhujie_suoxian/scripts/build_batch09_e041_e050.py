"""Compile and validate Batch 09: Episodes E041–E050 (Chapters 41–50, World 2 永夜大胤)."""

from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
for _p in (str(REPO_ROOT / "src"), str(SCRIPT_DIR)):
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


def _stage_clean_chapter_md(md_path: Path, tmp_dir: Path) -> Path:
    """Move standalone sentence-final punctuation immediately following `”` inside the quote."""
    raw = md_path.read_text(encoding="utf-8")
    cleaned = re.sub(r"”([！？。]+)(\s*)$", r"\1”\2", raw, flags=re.MULTILINE)
    if cleaned == raw:
        return md_path
    staged = tmp_dir / md_path.name
    staged.write_text(cleaned, encoding="utf-8")
    return staged


def build_all_batch09() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []
    _tmp_ctx = tempfile.TemporaryDirectory(prefix="batch09_md_")
    tmp_dir = Path(_tmp_ctx.name)

    # =========================================================================
    # E041 · 第41章 认知牢笼，从未见过太阳的王朝 (68 paras, 19 quotes)
    # =========================================================================
    md_41 = SOURCE_DIR / "第41章_认知牢笼，从未见过太阳的王朝.md"
    s41 = compile_episode_cue_sheet(
        episode_id="E041",
        chapter_number=41,
        source_md_path=md_41,
        source_rel_path=f"02_分章精修正文/{md_41.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_ancient_scroll_excuse_board_caravan",
                "start_p": 1,
                "title": "第一幕 · 巧言圆口误，搭车赴骨城",
                "bgm_prompt": WORLD_OST["w2_eternal_night_tension"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_three_step_probe_marrow_tax_cage",
                "start_p": 19,
                "title": "第二幕 · 三步验视锁，髓税吃人笼",
                "bgm_prompt": WORLD_OST["w2_ghost_market_stealth"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_sun_stealing_madman_father_trace",
                "start_p": 40,
                "title": "第三幕 · 皇榜盗日魔，慈父留刀踪",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_disguised_violet_flame_west_gate",
                "start_p": 51,
                "title": "第四幕 · 煞火化紫髓，骨镜拦西门",
                "bgm_prompt": WORLD_OST["w2_eternal_night_tension"],
                "bgm_duration_s": 95.0,
            },
        ],
        skip_onomatopoeia_paras={55},
        dialogue_specs=[
            {"match": "看来是闭关太久，把山中孤本杂记里的荒诞痴话当真了", "role_id": "lu_jin", "tags": "[sighs] [calmly]", "stability": 0.5, "note": "陆烬松开刀柄半真半假圆过太阳之言"},
            {"match": "恩公此言何意", "role_id": "weathered_elder_npc", "speaker_name": "陈福", "tags": "[trembling]", "stability": 0.0, "note": "老管事陈福咽唾沫颤声追问"},
            {"match": "家师性情孤僻，早年曾在极西荒山古洞里拾得几卷残缺兽皮古籍", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬借孤本古籍将太阳解释为天穹巨灯代称"},
            {"match": "原来是前朝疯人留下的荒诞杂书！吓死小老儿了", "role_id": "weathered_elder_npc", "speaker_name": "陈福", "tags": "[sighs] [laughs]", "stability": 0.0, "note": "陈福擦去冷汗如释重负苦笑"},
            {"match": "前辈有所不知，咱们【大胤圣朝】律法森严", "role_id": "male_guard_captain", "speaker_name": "周青", "tags": "[whispers] [calmly]", "stability": 0.5, "note": "护卫队长周青捡起骨灯压低声音郑重提醒"},
            {"match": "多谢周统领提点，在下记下了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬拱手致谢顺势搭车"},
            {"match": "小兄弟，路边那丛蓝草可能入药", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬指路边暗蓝荧光苔藓试探本土生灵视神经"},
            {"match": "回前辈的话，路边除了白骨渣子和黑灰，哪有什么蓝草", "role_id": "male_disciple_a", "speaker_name": "少年护卫", "tags": "[calmly]", "stability": 0.5, "note": "少年护卫茫然张望看不见自然荧光"},
            {"match": "恩公在深山清修，自是不知外头苦楚", "role_id": "weathered_elder_npc", "speaker_name": "陈福", "tags": "[sighs] [softly]", "stability": 0.5, "note": "陈福奉上苦根水叹息大胤月初髓油税"},
            {"match": "髓油税，莫非是抽活人骨髓", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬指尖微顿淡声询问"},
            {"match": "正是用司灯特制的抽髓银针刺入尾椎", "role_id": "weathered_elder_npc", "speaker_name": "陈福", "tags": "[whispers] [trembling]", "stability": 0.0, "note": "陈福麻木畏惧讲述抽髓银针与燃髓折寿之苦"},
            {"match": "既然人人都信奉骨灯，为何方才在官道上", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬吹开茶沫顺势打探跨界先驱踪迹"},
            {"match": "前辈神机妙算！实不相瞒，就在两年前", "role_id": "male_guard_captain", "speaker_name": "周青", "tags": "[whispers] [dramatically]", "stability": 0.0, "note": "周青策马贴近车窗压低声音道出永夜圣京狂徒"},
            {"match": "哦？什么样的狂徒", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬眸光微凝不动声色追问"},
            {"match": "据皇城传回来的海捕皇榜所载，那人是个来历不明的外乡猛汉", "role_id": "male_guard_captain", "speaker_name": "周青", "tags": "[whispers] [dramatically]", "stability": 0.0, "note": "周青震撼描述背负黑铁重刀痛斥骨灯的独眼猛汉"},
            {"match": "后来圣朝震怒，将其定为妄言惑众的【盗日疯魔】", "role_id": "weathered_elder_npc", "speaker_name": "陈福", "tags": "[whispers] [trembling]", "stability": 0.0, "note": "陈福缩脖补充盗日疯魔砍翻半条街杀出重围"},
            {"match": "以此界修士的眼界，定会将这缕伪装后的火焰认作皇城高品紫髓圣火", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬以暗金灵液包裹焚锁妖煞火伪装上位真火"},
            {"match": "前辈，白骨灯城到了", "role_id": "male_guard_captain", "speaker_name": "周青", "tags": "[softly]", "stability": 0.5, "note": "车外周青紧绷低呼抵达白骨灯城"},
            {"match": "面生得很啊，外乡人，报上你的灯籍骨印来", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[coldly] [sarcastic]", "stability": 0.0, "note": "西门司灯校尉韩烈抬起照髓骨镜拦住陆烬"},
        ],
        sfx_blueprint=[
            {"p": 18, "pos": "before", "slug": "caravan_wheels_bone_road", "sfx_prompt": "Heavy wooden carriage wheels rolling and creaking steadily across a gravel road in dry dark wind", "duration_seconds": 3.0, "gain_db": 0.5, "note": "商队整顿车马顺着兽骨官道向东疾行"},
            {"p": 32, "pos": "before", "slug": "pour_hot_tea_in_carriage", "sfx_prompt": "Warm herbal tea poured from an earthen pot into a coarse ceramic bowl inside a moving wooden carriage", "duration_seconds": 2.2, "gain_db": 0.5, "note": "陈福端着温热苦根水登车奉茶"},
            {"p": 55, "pos": "before", "slug": "violet_gold_flame_disguise", "sfx_prompt": "Crisp hot violet-gold flame igniting softly in palm with a deep noble resonant hum", "duration_seconds": 2.4, "gain_db": 1.0, "note": "嗤！暗金灵液包裹妖煞火折射紫金色火晕"},
            {"p": 60, "pos": "before", "slug": "carriage_halt_iron_drawbridge", "sfx_prompt": "Heavy iron-rimmed carriage wheels rumbling over stone and slowing to a halt near creaking iron chains", "duration_seconds": 3.0, "gain_db": 1.0, "note": "马车抵达白骨灯城西门黑铁吊桥"},
        ],
    )
    j41, m41 = save_episode_scripts(s41, REPO_SCRIPTS_DIR, registry)
    built.append(("E041", j41, m41))

    # =========================================================================
    # E042 · 第42章 白骨灯城，一缕妖火瞒司灯 (71 paras, 15 quotes)
    # =========================================================================
    md_42 = SOURCE_DIR / "第42章_白骨灯城，一缕妖火瞒司灯.md"
    s42 = compile_episode_cue_sheet(
        episode_id="E042",
        chapter_number=42,
        source_md_path=_stage_clean_chapter_md(md_42, tmp_dir),
        source_rel_path=f"02_分章精修正文/{md_42.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_bone_mirror_cracks_royal_fire_awe",
                "start_p": 1,
                "title": "第一幕 · 妖火裂骨镜，万火齐俯首",
                "bgm_prompt": WORLD_OST["w2_eternal_night_tension"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_kneeling_captain_jade_pass_greed",
                "start_p": 27,
                "title": "第二幕 · 校尉跪献牌，暗影起贪心",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act3_true_sight_pierces_man_eating_tower",
                "start_p": 43,
                "title": "第三幕 · 破妄窥巨塔，十万抽魂管",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_ash_ghost_market_snow_lotus_mark",
                "start_p": 58,
                "title": "第四幕 · 子夜探灰市，铁牌现旧纹",
                "bgm_prompt": WORLD_OST["w2_ghost_market_stealth"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(60, 71, "vast_hall")],
        skip_onomatopoeia_paras={10, 17, 27, 48, 66},
        dialogue_specs=[
            {"match": "韩校尉息怒，这位爷是老朽在官道上请来的护道贵客", "role_id": "weathered_elder_npc", "speaker_name": "陈福", "tags": "[trembling] [desperately]", "stability": 0.0, "note": "陈福脸色煞白上前替陆烬求情"},
            {"match": "滚一边去", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[angry] [shouting]", "stability": 0.0, "note": "韩烈一袖震退陈福贪婪盯住陆烬"},
            {"match": "本校尉数三声，亮不出大胤灯籍魂印，就地锁拿抽髓", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[coldly] [sarcastic]", "stability": 0.0, "note": "韩烈欲扣偷渡客罪名私吞重刀与肉身"},
            {"match": "紫、紫极真火气象？三品之上的皇城圣火种", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[gasps] [trembling]", "stability": 0.0, "note": "照髓骨镜崩裂腾起紫黑金纹火影吓呆韩烈"},
            {"match": "卑职西门司灯校尉韩烈有眼无珠，不知皇城圣师门下上使", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[trembling] [desperately]", "stability": 0.0, "note": "韩烈双膝跪倒骨灰地面高举裂镜请罪"},
            {"match": "我赶时间", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬垂眸惜字如金冷淡吐出四字"},
            {"match": "上使息怒！这是咱们灰原郡【内城通行骨牌】", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[trembling] [rushed]", "stability": 0.0, "note": "韩烈冷汗涔涔献上内城通行骨牌并免去商队髓税"},
            {"match": "震慑住了场面，却也因为外地衣饰与没有随从惹了一丝觊觎么", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬敏锐察觉身后韩烈贪疑目光记入必防名单"},
            {"match": "恩公若是想寻些不入司灯监官账的古旧奇珍或是凝魂宝药", "role_id": "weathered_elder_npc", "speaker_name": "陈福", "tags": "[whispers]", "stability": 0.5, "note": "临别之际陈福低声指点城南枯骨井下灰烬鬼市"},
            {"match": "好一座吃人灯塔", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "note": "陆烬开启破妄真目看穿千丈白骨灯塔十万抽魂细管"},
            {"match": "在没有开辟无瑕紫府、修出足以正面硬撼金丹强者的底牌之前", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬冷静决断今夜探完鬼市便走"},
            {"match": "这盒凝魂髓膏怎么卖", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬在地下灰烬鬼市石摊前询价"},
            {"match": "三百下品灵石，或拿五钱筑基精髓来换，概不还价", "role_id": "chu_xiazi", "speaker_name": "鬼市摊主", "tags": "[hoarsely] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "白骨面具摊主沙哑开价"},
            {"match": "杂质太重，不要", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬察觉膏体混杂死囚怨毒摇头离开"},
            {"match": "断刀雪莲纹", "role_id": "lu_jin", "tags": "[whispers] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬认出破铁招牌角落北渊镇渊司旧部生死暗记"},
        ],
        sfx_blueprint=[
            {"p": 10, "pos": "before", "slug": "bone_mirror_beam_shoot", "sfx_prompt": "Ancient bronze mirror humming deeply and projecting a cold eerie energy beam through wind", "duration_seconds": 2.4, "gain_db": 1.0, "note": "嗡！照髓骨镜百道骨纹亮起射出惨白光柱"},
            {"p": 17, "pos": "before", "slug": "bronze_mirror_crack_flame_flare", "sfx_prompt": "Crisp metallic bronze mirror cracking sharply followed by a blazing noble flame surge", "duration_seconds": 2.8, "gain_db": 1.5, "note": "咔嚓！照髓骨镜崩裂腾起三尺紫黑金纹圣火"},
            {"p": 27, "pos": "before", "slug": "armored_guards_kneel_ash", "sfx_prompt": "Heavy bone-plated armor dropping hard onto ash-covered stone followed by a dozen crossbows clattering down", "duration_seconds": 2.6, "gain_db": 1.0, "note": "扑通！韩烈与十二名骨甲兵卒骇然跪倒"},
            {"p": 48, "pos": "before", "slug": "true_sight_pierce_bone_tower", "sfx_prompt": "Crystalline ocular resonance chime opening into a sinister deep subterranean energy conduit drone", "duration_seconds": 3.0, "gain_db": 1.0, "note": "嗡！破妄真目洞穿白骨灯塔十万抽魂管"},
            {"p": 66, "pos": "before", "slug": "beiyuan_rhythmic_blacksmith_hammer", "sfx_prompt": "Rhythmic blacksmith iron hammer striking an anvil in a dark underground stone alley, three light taps and one heavy strike", "duration_seconds": 3.2, "gain_db": 1.5, "note": "铛锵铛铛锵！暗合北渊军伍呼吸锤法的打铁声"},
        ],
    )
    j42, m42 = save_episode_scripts(s42, REPO_SCRIPTS_DIR, registry)
    built.append(("E042", j42, m42))

    # =========================================================================
    # E043 · 第43章 灰市暗记，故人断臂指皇城 (54 paras, 20 quotes)
    # =========================================================================
    md_43 = SOURCE_DIR / "第43章_灰市暗记，故人断臂指皇城.md"
    s43 = compile_episode_cue_sheet(
        episode_id="E043",
        chapter_number=43,
        source_md_path=md_43,
        source_rel_path=f"02_分章精修正文/{md_43.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_secret_knock_passphrase_broken_blade",
                "start_p": 1,
                "title": "第一幕 · 叩门对切口，抚刀认少主",
                "bgm_prompt": WORLD_OST["w2_ghost_market_stealth"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_one_armed_veteran_father_slays_core",
                "start_p": 21,
                "title": "第二幕 · 断臂盲统领，刀狂逆斩丹",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_iron_casket_gift_purple_mansion_map",
                "start_p": 35,
                "title": "第三幕 · 铁匣留古图，紫府道途圆",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act4_hundred_bone_array_warden_descends",
                "start_p": 45,
                "title": "第四幕 · 百骨封窄巷，真人压铁铺",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[(45, 54, "vast_hall")],
        skip_onomatopoeia_paras={45, 48},
        dialogue_specs=[
            {"match": "鬼市打铁只收骨币，不修官刀，客官走错门了", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[hoarsely] [coldly]", "stability": 0.5, "note": "门板后独臂盲眼老汉铁山沙哑试探"},
            {"match": "朔风吹断北渊雪", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "note": "陆烬隔门低声吐出北渊镇渊司旧日上半句切口"},
            {"match": "下半句是什么？你这后生究竟打哪儿学来的这句话", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[trembling] [fiercely]", "stability": 0.0, "note": "独臂盲眼老汉拉开木门紫府神识锁住陆烬颤声追问"},
            {"match": "残刃犹温故人血", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.5, "note": "陆烬栓门布禁掀开斗篷轻声接上下半句"},
            {"match": "百炼乌金混北渊寒铁，六十四斤三两", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[trembling] [dramatically]", "stability": 0.0, "note": "铁山独手抚过断岳刀脊缺角浑身剧震认出故兵"},
            {"match": "这眉眼骨相……像，太像了！你是擎苍那小子的骨肉", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[crying] [trembling]", "stability": 0.0, "note": "铁山焦黑眼眶涌出热泪摸着陆烬眉骨哽咽相认"},
            {"match": "晚辈正是陆烬。敢问前辈尊姓大名", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "note": "陆烬扶住老人温声询问"},
            {"match": "老奴铁山，原北渊镇渊司左卫铸兵统领", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[hoarsely] [dramatically]", "stability": 0.5, "note": "铁山抹泪挺脊自报镇渊司旧职与二十年前探路往事"},
            {"match": "老奴初来乍到不懂规矩，妄图窥探城中心那座白骨妖塔", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[angry] [hoarsely]", "stability": 0.0, "note": "铁山咬牙讲述被塔灵烧瞎双目削去左臂之恨"},
            {"match": "少主，你爹还活着！两年前，擎苍小子真的打穿界隙找过来了", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[whispers] [excited]", "stability": 0.0, "note": "铁山拉陆烬至地窖暗格前振奋报喜"},
            {"match": "铁山叔亲眼见过家父？他如今身在何处", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "陆烬眸光骤亮急问父亲下落"},
            {"match": "两年前的一个夜里，擎苍背着一把临时抢来的黑铁重刀摸进鬼市", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[calmly]", "stability": 0.5, "note": "铁山拧开铁砧底座机括讲述两年前叔侄重逢"},
            {"match": "擎苍何等敏锐，他在灰原郡与皇城潜伏数月", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[dramatically]", "stability": 0.0, "note": "铁山捧出火油铁匣道出皇城熄灯古井吞日骗局"},
            {"match": "两年前，擎苍潜入皇城司灯总监想要毁掉古井救人", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[dramatically]", "stability": 0.0, "note": "铁山讲述陆擎苍皇城遭遇金丹司灯使"},
            {"match": "你爹当真是天生刀狂！他以紫府后期逆战金丹", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[excited] [dramatically]", "stability": 0.0, "note": "铁山傲然道出陆擎苍当街逆斩金丹并赴归墟殖骨海"},
            {"match": "这是你爹临去皇城前留在我这儿的", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[softly] [dramatically]", "stability": 0.5, "note": "铁山郑重递交陆擎苍留给儿子的火油铁匣"},
            {"match": "这半卷《紫府开天劈海图》是你爹从一处跨界古尸身上所得", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[calmly]", "stability": 0.5, "note": "铁山解释开天劈海图与二阶巅峰凶兽精血石之用"},
            {"match": "铁山叔，此地既已暴露了我的行踪", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬收好古图准备带铁山出城闭关"},
            {"match": "启禀镇守使大人！卑职散值后越想越不对劲", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[sarcastic] [excited]", "stability": 0.0, "space": "vast_hall", "note": "韩烈引巡夜司铁卫封巷向白骨真人邀功"},
            {"match": "好精纯的气血，好霸道的异火气息！屋里的小辈", "role_id": "chiyang_laozu", "speaker_name": "白骨真人", "tags": "[laughs] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "紫府后期白骨真人托九骷骨灯沙哑怪笑逼降"},
        ],
        sfx_blueprint=[
            {"p": 8, "pos": "before", "slug": "five_coded_knocks_wood_door", "sfx_prompt": "Five deliberate rhythmic knuckle knocks on an old weathered wooden door, three slow and two quick", "duration_seconds": 2.5, "gain_db": 1.0, "note": "三长两短尾指一顿，北渊镇渊司叩门军规"},
            {"p": 12, "pos": "before", "slug": "hammer_drop_wood_door_creak", "sfx_prompt": "Heavy iron blacksmith hammer thudding onto packed dirt floor followed by old wooden doors creaking open", "duration_seconds": 2.8, "gain_db": 1.0, "note": "铺内铁锤砸地闷响，腐朽木门一把拉开"},
            {"p": 17, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "unsheathe_duanyue_three_inches", "gain_db": 1.0, "note": "断岳乌金重刀拔出三寸让铁山触摸刀背刻痕"},
            {"p": 45, "pos": "before", "slug": "hundred_bone_guards_surround", "sfx_prompt": "Hundreds of heavy iron boots marching rapidly in unison with clattering bone armor and rattling chains", "duration_seconds": 3.4, "gain_db": 1.5, "note": "轰隆！百名巡夜司铁卫涌入窄巷合围铁匠铺"},
            {"p": 48, "pos": "before", "slug": "hundred_bone_soul_array_rise", "sfx_prompt": "Sinister arcane formation barrier humming and snapping shut with crackling pale energy arcs", "duration_seconds": 2.8, "gain_db": 1.5, "note": "滋啦！百骨锁魂阵升起封死巷道"},
        ],
    )
    j43, m43 = save_episode_scripts(s43, REPO_SCRIPTS_DIR, registry)
    built.append(("E043", j43, m43))

    # =========================================================================
    # E044 · 第44章 永夜开紫府，一里神识斩白骨！ (84 paras, 18 quotes)
    # =========================================================================
    md_44 = SOURCE_DIR / "第44章_永夜开紫府，一里神识斩白骨！.md"
    s44 = compile_episode_cue_sheet(
        episode_id="E044",
        chapter_number=44,
        source_md_path=md_44,
        source_rel_path=f"02_分章精修正文/{md_44.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_calm_step_into_hundred_bone_array",
                "start_p": 1,
                "title": "第一幕 · 按肩止死志，独步踏骨阵",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act2_open_flawless_purple_mansion_in_battle",
                "start_p": 20,
                "title": "第二幕 · 逆冲泥丸宫，永夜开紫府",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_three_sabre_slashes_slay_white_bone",
                "start_p": 42,
                "title": "第三幕 · 刀崩锁魂链，三刃斩白骨",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_settle_veteran_enter_sixth_ring",
                "start_p": 72,
                "title": "第四幕 · 安顿故人去，神识入六环",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(1, 73, "vast_hall"), (80, 84, "mental_realm")],
        skip_onomatopoeia_paras={7, 21, 23, 29, 36, 46, 53, 63, 66},
        dialogue_specs=[
            {"match": "竟把白骨老鬼这尊紫府后期的镇守使亲自招来了", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[gasps] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "铁山感知到半空白骨真人威压脸色剧变"},
            {"match": "少主，后堂铁炉底下有一条早年挖通的排烟暗渠", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "铁山抄起百斤红锤欲自爆紫府替少主开路"},
            {"match": "铁山叔歇着便是", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬单手按住铁山肩膀稳稳压回自爆气血"},
            {"match": "区区一座百人骨阵，还犯不着让您老拼命", "role_id": "lu_jin", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬解开重刀皮扣踹门独步立于窄巷中央"},
            {"match": "不知死活的小杂种，在镇守使大人的【百骨锁魂阵】面前", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[sarcastic] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "韩烈在阵眼处狰狞厉喝"},
            {"match": "结阵，锁他四肢，莫伤了他的泥丸火种", "role_id": "chiyang_laozu", "speaker_name": "白骨真人", "tags": "[coldly] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "白骨真人枯指一点下令生擒"},
            {"match": "诺", "role_id": "male_guard_captain", "speaker_name": "巡夜司铁卫", "tags": "[shouting]", "stability": 0.5, "space": "vast_hall", "note": "百名巡夜司铁卫齐声领命射出锁魂骨链"},
            {"match": "百液归流，逆冲泥丸，给我开", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬捏碎精血石与界隙源晶临阵强冲无瑕紫府"},
            {"match": "什么？临阵强开紫府？这怎么可能", "role_id": "chiyang_laozu", "speaker_name": "白骨真人", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "白骨真人骇然失声不敢置信"},
            {"match": "靠吸食百姓脑髓攒出来的鬼火，也配入我陆烬的紫府", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬踏风悬空冷声斥破大胤骨火"},
            {"match": "不好！快退", "role_id": "li_cang", "speaker_name": "韩烈", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "第一刀劈穿三十丈鬼市穹顶吓得韩烈转身狂逃"},
            {"match": "方才不是要锁拿抽髓么？现在想走，晚了", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬御风跨出二十丈斜劈第二刀斩灭韩烈"},
            {"match": "小畜生，敢杀本座爱将，给我纳命来", "role_id": "chiyang_laozu", "speaker_name": "白骨真人", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "白骨真人狂喷本命髓血祭出三丈白骨鬼爪"},
            {"match": "靠透支寿元堆出来的腐朽假紫府，也敢称真人？破", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬锁定骨灯破绽高举断岳劈出第三刀"},
            {"match": "虎父无犬子……老司主，您在天有灵听见了吗", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[trembling] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "门槛前铁山听见三刀斩灭镇守使激动颤抖喃喃"},
            {"match": "铁山叔，得罪了，我们走", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬摄起战利品卷起铁山化雷光冲出白骨灯城"},
            {"match": "铁山叔安心在此静养，切莫轻出矿洞", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬在六十里外地下古矿洞妥善安置铁山"},
            {"match": "少主万事小心，皇城那位燃灯国师乃是金丹中期老怪", "role_id": "qin_lie", "speaker_name": "铁山", "tags": "[dramatically]", "stability": 0.5, "note": "铁山紧握陆烬手背沉声叮嘱"},
        ],
        sfx_blueprint=[
            {"p": 7, "pos": "before", "slug": "clasp_shoulder_kick_doors", "sfx_prompt": "Firm palm clap on heavy leather shoulder armor followed shortly by wooden doors kicked splintering open", "duration_seconds": 2.6, "gain_db": 1.0, "note": "啪！陆烬按住铁山右肩，一脚踹碎木门跨入窄巷"},
            {"p": 21, "pos": "before", "motif_id": "motif_qi_sea_shatter", "slug": "crush_origin_crystal_surge", "gain_db": 1.5, "note": "咔嚓轰隆！捏碎凶兽精血石与界隙伴生源晶"},
            {"p": 29, "pos": "before", "slug": "ancient_bell_open_purple_mansion", "sfx_prompt": "Colossal ancient bronze bell chime resounding deeply with surging spiritual wind tearing open a barrier", "duration_seconds": 3.5, "gain_db": 2.0, "note": "咚！泥丸宫如太古洪钟轰鸣开辟十丈无瑕紫府"},
            {"p": 46, "pos": "before", "slug": "thunder_fire_blade_shatter_dome", "sfx_prompt": "Thunderous lightning-and-fire broadsword slash snapping iron chains and blasting open a thick stone ceiling", "duration_seconds": 3.6, "gain_db": 2.0, "note": "轰咔！十丈紫金雷火刀虹崩断百链劈穿鬼市穹顶"},
            {"p": 63, "pos": "before", "slug": "cleave_bone_claw_explode_lamp", "sfx_prompt": "Heavy broadsword wrapped in crackling lightning cleaving a massive bone construct and exploding a bronze lantern", "duration_seconds": 3.4, "gain_db": 2.0, "note": "铛咔嚓轰！第三刀劈碎鬼爪与九骷骨灯斩杀白骨真人"},
            {"p": 80, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "enter_xujie_unlock_sixth_ring", "gain_db": 1.5, "note": "贴零号铭牌踏入方寸墟界解锁第六环囚道殿"},
        ],
    )
    j44, m44 = save_episode_scripts(s44, REPO_SCRIPTS_DIR, registry)
    built.append(("E044", j44, m44))

    # =========================================================================
    # E045 · 第45章 第六环囚道殿，老怪残魂欲夺舍 (59 paras, 17 quotes)
    # =========================================================================
    md_45 = SOURCE_DIR / "第45章_第六环囚道殿，老怪残魂欲夺舍.md"
    s45 = compile_episode_cue_sheet(
        episode_id="E045",
        chapter_number=45,
        source_md_path=md_45,
        source_rel_path=f"02_分章精修正文/{md_45.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_crimson_flood_dragon_blood_bronze_halls",
                "start_p": 1,
                "title": "第一幕 · 冰壁取蛟血，黄沙现铜殿",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_ninth_bronze_cage_hypocrite_remnant_soul",
                "start_p": 19,
                "title": "第二幕 · 九笼囚恶鬼，真目破伪善",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_baiting_secret_formulas_from_old_ghost",
                "start_p": 39,
                "title": "第三幕 · 将计套秘诀，尽得破盘法",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_feigned_soul_flaw_body_snatch_trap",
                "start_p": 48,
                "title": "第四幕 · 佯露识海隙，黑风扑眉心",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 85.0,
            },
        ],
        acoustic_ranges=[(1, 59, "mental_realm")],
        skip_onomatopoeia_paras={12, 54},
        dialogue_specs=[
            {"match": "竟有一滴尚未干涸的三阶【焚天赤蛟精血】", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "mental_realm", "note": "陆烬在第七环内段玄冰壁中发现三阶焚天赤蛟精血"},
            {"match": "这滴赤蛟精血火煞虽猛，可惜被冰渊寒气侵蚀了万载", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬评估蛟血最宜用来淬炼重铸断岳重刀"},
            {"match": "咦？竟有生人神魂踏入此殿", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[hoarsely] [sighs]", "stability": 0.0, "space": "mental_realm", "note": "第九座青铜囚笼内亮起幽绿微光传出苍老颤音"},
            {"match": "天不绝我人族正道！小友年纪轻轻", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[dramatically] [crying]", "stability": 0.0, "space": "mental_realm", "note": "鹤阴散人残魂假扮仙风道骨老泪纵横夸赞陆烬"},
            {"match": "晚辈误入宝地，不知老前辈尊姓大名", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬立于十丈安全界外露出一丝谨慎试探"},
            {"match": "老夫道号【鹤阴散人】，生前乃是上古金丹圆满大修", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[sighs] [crying]", "stability": 0.0, "space": "mental_realm", "note": "鹤阴散人颠倒黑白谎称抗击仙庭遭叛徒暗算"},
            {"match": "小友你看，老夫神魂油尽灯枯", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[desperately] [softly]", "stability": 0.0, "space": "mental_realm", "note": "鹤阴散人以金丹真解为饵哀求陆烬上前揭开镇魂符"},
            {"match": "第九笼，镇欺师叛界夺舍恶犯鹤阴", "role_id": "ancient_construct_echo", "speaker_name": "囚笼刻字", "tags": "[coldly]", "stability": 1.0, "space": "memory_echo", "note": "破妄真目穿透笼底积沙看清玄铁基石剑指刻字"},
            {"match": "前辈所言虽重，但晚辈修为浅薄", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬将计就计抛出古井母锁与寒星沉银两大难题"},
            {"match": "区区司命仙庭布下的下等【盲昼噬火母盘】，何足道哉", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[dismissive] [calmly]", "stability": 0.5, "space": "mental_realm", "note": "鹤阴散人暗喜上钩故作高人姿态捻须傲然"},
            {"match": "那类吞日母盘外层虽有仙庭法则护盾", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "鹤阴散人道出吞日母盘最大命门在抽髓魂管"},
            {"match": "它需要日夜吞吸活人骨髓魂火维持运转", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[whispers] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "鹤阴散人详述异火逆灌抽魂主管道引爆母盘之法"},
            {"match": "那三阶【寒星沉银】又该如何无丹火熔炼", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬牢记破阵之法继续追问熔炼奇金秘诀"},
            {"match": "听好了，此乃上古器道秘传《九转熔兵古火诀》", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[dramatically]", "stability": 0.5, "space": "mental_realm", "note": "鹤阴散人诵出三百字九转熔兵古火诀真传"},
            {"match": "小友，口诀与破阵之法老夫皆已倾囊相授", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[rushed] [desperately]", "stability": 0.0, "space": "mental_realm", "note": "鹤阴散人急不可耐催促陆烬上前揭符"},
            {"match": "多谢前辈厚赐，晚辈这便助前辈脱困", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬踏入三尺内故意卖出一丝神魂紊乱破绽"},
            {"match": "蠢不可及的小畜生！好一具万古难寻的无瑕紫府道胎", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[laughs] [angry]", "stability": 0.0, "space": "mental_realm", "note": "鹤阴散人化作青面獠牙阴魂黑风直扑陆烬眉心"},
        ],
        sfx_blueprint=[
            {"p": 9, "pos": "before", "slug": "melt_glacier_extract_dragon_blood", "sfx_prompt": "Focused hot flame sizzling through ancient glacier ice followed by a dense molten droplet sealing into jade", "duration_seconds": 2.6, "gain_db": 1.0, "note": "妖煞火融开玄冰细孔摄出焚天赤蛟精血"},
            {"p": 12, "pos": "before", "slug": "step_into_sixth_ring_sandstorm", "sfx_prompt": "Sudden gust of dry desert sandstorm wind sweeping across ancient bronze ruins and broken blades", "duration_seconds": 3.0, "gain_db": 1.0, "note": "呼啦！跨出冰渊步入第六环黄沙戈壁"},
            {"p": 18, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "enter_qiudao_bronze_hall", "gain_db": 1.0, "note": "迈步跨过十丈斑驳铜门踏入第六环囚道殿"},
            {"p": 54, "pos": "before", "slug": "talisman_rip_dark_gale_lunge", "sfx_prompt": "Crisp paper seal tearing slightly followed by a fierce sinister wind gust lunging across bronze bars", "duration_seconds": 2.6, "gain_db": 1.5, "note": "嗤啦！阴魂黑风自符箓卷角钻出扑向眉心"},
        ],
    )
    j45, m45 = save_episode_scripts(s45, REPO_SCRIPTS_DIR, registry)
    built.append(("E045", j45, m45))

    # =========================================================================
    # E046 · 第46章 请君入瓮炼魂髓，紫府中期凝神威 (66 paras, 13 quotes)
    # =========================================================================
    md_46 = SOURCE_DIR / "第46章_请君入瓮炼魂髓，紫府中期凝神威.md"
    s46 = compile_episode_cue_sheet(
        episode_id="E046",
        chapter_number=46,
        source_md_path=md_46,
        source_rel_path=f"02_分章精修正文/{md_46.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_zero_token_chains_immortal_burial_secret",
                "start_p": 1,
                "title": "第一幕 · 请君入铁瓮，初闻葬仙狱",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_refine_soul_marrow_spirit_shock_spike",
                "start_p": 22,
                "title": "第二幕 · 炼髓晋中期，石案得惊神",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_reforge_hundred_eight_jin_duanyue",
                "start_p": 38,
                "title": "第三幕 · 九转熔沉银，百八铸新刀",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_black_canyon_blindfolded_day_watchers",
                "start_p": 57,
                "title": "第四幕 · 东行闻兵戈，蒙眼守昼人",
                "bgm_prompt": WORLD_OST["w2_eternal_night_tension"],
                "bgm_duration_s": 85.0,
            },
        ],
        acoustic_ranges=[(1, 37, "mental_realm")],
        skip_onomatopoeia_paras={4, 7, 25, 50},
        dialogue_specs=[
            {"match": "晚辈正愁刚开紫府缺一味凝神大药，多谢老前辈主动送上门来", "role_id": "lu_jin", "tags": "[coldly] [calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬嘴角微掀冷淡揭穿请君入瓮之局"},
            {"match": "这、这是什么令牌？不对，你刚刚的神魂破绽是装出来的", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[gasps] [trembling]", "stability": 0.0, "space": "mental_realm", "note": "九根暗金锁链洞穿残魂将鹤阴散人钉死在地"},
            {"match": "零号？这怎么可能是太上大司命亲手封禁的葬仙狱", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "mental_realm", "note": "鹤阴散人认出零号铭牌与葬仙狱骇然尖叫"},
            {"match": "啊！饶命，老夫愿为奴为婢", "role_id": "sect_elder_antagonist", "speaker_name": "鹤阴散人", "tags": "[crying] [desperately]", "stability": 0.0, "space": "mental_realm", "note": "焚锁妖煞火淹没鹤阴散人将其炼作纯净无主魂髓"},
            {"match": "葬仙狱……看来我眉心这座【方寸墟界】的来历", "role_id": "lu_jin", "tags": "[whispers] [dramatically]", "stability": 0.5, "space": "mental_realm", "note": "陆烬扫过残存记忆光斑暗忖太上大司命与葬仙狱"},
            {"match": "修为已至紫府中期，神识秘术亦有了着落", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬回归石室睁眼电芒激射准备重锻断岳"},
            {"match": "起火", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "note": "陆烬掐动九转熔兵古火诀化出九层子母火炉"},
            {"match": "融", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "note": "陆烬以两里半神识为锤将寒星沉银与赤血金精揉入刀身"},
            {"match": "好一把百零八斤的新【断岳】，足够陪我去大胤皇城", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "note": "陆烬握住百零八斤准三阶新断岳重刀长身而起"},
            {"match": "燃髓圣宗办事，奉皇城国师法旨清剿逆党，一个活口不留", "role_id": "zhao_kui", "speaker_name": "燃髓宗头目", "tags": "[angry] [shouting]", "stability": 0.0, "note": "谷底乱石滩燃髓宗精锐结阵围剿"},
            {"match": "保护少主突围！哪怕战至最后一人", "role_id": "shi_meng", "speaker_name": "守昼护卫", "tags": "[fiercely] [shouting]", "stability": 0.0, "note": "浴血蒙眼护卫拼死护住少主与皇城地宫图"},
            {"match": "沈烛音，两年前那个背黑铁大刀的【盗日疯魔】已经滚去东海喂鱼了", "role_id": "li_cang", "speaker_name": "燃髓宗长老", "tags": "[sarcastic] [coldly]", "stability": 0.0, "note": "紫府圆满白发长老祭白骨飞剑狞笑逼降"},
            {"match": "我辈蒙眼不看妖灯，只待真阳重临人间", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[coldly] [fiercely]", "stability": 0.0, "note": "蒙眼青衣女剑客沈烛音持剑独立凛然怒斥"},
        ],
        sfx_blueprint=[
            {"p": 4, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "zero_token_awaken_prison_runes", "gain_db": 1.0, "note": "嗡！零号青铜铭牌绽放暗金神纹唤醒囚道铜殿阵法"},
            {"p": 7, "pos": "before", "slug": "nine_law_chains_pierce_slam", "sfx_prompt": "Nine heavy bronze chains shooting rapidly from stone floor tiles and slamming down onto bronze pavement", "duration_seconds": 3.0, "gain_db": 1.5, "note": "哗啦啦！九根暗金法则锁链洞穿鹤阴残魂钉在石砖"},
            {"p": 25, "pos": "before", "motif_id": "motif_qi_sea_shatter", "slug": "refine_soul_marrow_mid_zifu", "gain_db": 1.5, "note": "轰隆！吞服无主魂髓开辟十八丈紫府晋升紫府中期"},
            {"p": 48, "pos": "before", "slug": "spiritual_hammer_forging_duanyue", "sfx_prompt": "Steady powerful blacksmith forging strikes hammering molten silver metal into a heavy dark iron broadsword", "duration_seconds": 3.4, "gain_db": 1.5, "note": "神识重锤千锤百炼将寒星沉银锻入断岳刀脊"},
            {"p": 50, "pos": "before", "slug": "dragon_blood_quench_heavy_sabre", "sfx_prompt": "Searing molten droplet hitting red-hot steel with a blazing metallic ring and deep resonant blade hum", "duration_seconds": 3.0, "gain_db": 1.5, "note": "嗤啦！焚天赤蛟精血入槽铸成百零八斤准三阶重刀"},
        ],
    )
    j46, m46 = save_episode_scripts(s46, REPO_SCRIPTS_DIR, registry)
    built.append(("E046", j46, m46))

    # =========================================================================
    # E047 · 第47章 蒙眼守昼人，谁盗走了天上太阳？ (63 paras, 21 quotes)
    # =========================================================================
    md_47 = SOURCE_DIR / "第47章_蒙眼守昼人，谁盗走了天上太阳？.md"
    s47 = compile_episode_cue_sheet(
        episode_id="E047",
        chapter_number=47,
        source_md_path=md_47,
        source_rel_path=f"02_分章精修正文/{md_47.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_spirit_spike_slay_two_peak_elders",
                "start_p": 1,
                "title": "第一幕 · 惊神刺双老，重刀荡群邪",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_sabre_recognizes_kin_spirit_dew_heals",
                "start_p": 25,
                "title": "第二幕 · 刀势认故子，灵液疗暗伤",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_ancient_mural_stolen_sun_vow",
                "start_p": 40,
                "title": "第三幕 · 壁画述盗日，宁盲守真阳",
                "bgm_prompt": WORLD_OST["w2_first_sunlight_catharsis"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_palace_map_phoenix_crystal_nine_tolls",
                "start_p": 51,
                "title": "第四幕 · 皇城地宫图，九响万骨钟",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(34, 63, "vast_hall")],
        skip_onomatopoeia_paras={10, 15, 18, 58},
        dialogue_specs=[
            {"match": "冥顽不灵的瞎子，给老夫跪下受死", "role_id": "li_cang", "speaker_name": "燃髓宗长老", "tags": "[angry] [shouting]", "stability": 0.0, "note": "两名燃髓宗紫府圆满长老祭白骨飞剑直刺沈烛音"},
            {"match": "啊", "role_id": "li_cang", "speaker_name": "燃髓宗长老", "tags": "[gasps] [desperately]", "stability": 0.0, "note": "两记惊神刺扎入泥丸识海令双长老七窍飙血失神"},
            {"match": "什么人？两位长老死了，快逃", "role_id": "male_disciple_b", "speaker_name": "燃髓宗弟子", "tags": "[gasps] [desperately]", "stability": 0.0, "note": "围攻的燃髓宗弟子见双长老被秒杀魂飞魄散"},
            {"match": "助纣为虐者，不必走了", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬脚踏霜电三记雷火刀浪荡平二十余名恶修"},
            {"match": "敢问救命恩公尊姓大名？恩公方才这套霸烈无匹的重刀路数", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[softly] [dramatically]", "stability": 0.5, "note": "沈烛音凭剑心感知认出与陆擎苍一脉相承的重刀路数"},
            {"match": "陆擎苍正是家父，在下陆烬", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬冷峻眉宇微舒拱手自报家门"},
            {"match": "什么？你便是陆伯父挂在嘴边的独子，陆烬少侠", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[gasps] [excited]", "stability": 0.0, "note": "沈烛音惊喜失声认出恩人之子"},
            {"match": "守昼遗族拜见陆少侠！昔日若非陆前辈在皇城血战断后", "role_id": "shou_mu_ren", "speaker_name": "蒙眼守昼人", "tags": "[trembling] [dramatically]", "stability": 0.5, "note": "重伤守昼遗族众人强撑伤体向陆烬深深一揖"},
            {"match": "此处距燃髓宗分坛不远，不宜久留", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[rushed] [softly]", "stability": 0.5, "note": "沈烛音强压伤势邀陆烬前往地下守昼石窟"},
            {"match": "沈姑娘服下此液，可化去肺腑火毒", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬引出第八环息壤草木灵液赠予沈烛音疗伤"},
            {"match": "好神妙的生机灵液，多谢陆少侠再造之恩", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[softly] [excited]", "stability": 0.5, "space": "vast_hall", "note": "沈烛音肺腑金丹火毒消融起身深深致谢"},
            {"match": "陆少侠既从界外而来，可知我们这座【烬昼界】为何人人畏惧白昼", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[softly] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "沈烛音引陆烬来到石窟深处五丈远古壁画前"},
            {"match": "四千年前，我们这方天地本有四季晨昏，本有温暖万物的太阳", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[crying] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "沈烛音抚摸壁画烈日刻痕悲怆诉说司命仙庭盗日往事"},
            {"match": "凡是睁眼看过白骨妖灯哪怕一眼的婴儿", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[coldly] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "沈烛音揭露白骨妖灯种下母锁奴印篡改视神经真相"},
            {"match": "所以我辈自号【守昼人】，宁可生生世世蒙眼做个不见妖光的瞎子", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "沈烛音转身面向陆烬一字一顿道出守昼四千年风骨"},
            {"match": "家父一年前赴东海之前，可曾留下关于皇城地底古井的口信", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬决意劈碎无日黑幕并询问古井路径与真灵血材"},
            {"match": "陆伯父当年正是与家父联手探明了皇城虚实", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "沈烛音双手奉上三代死士换来的永夜皇城地宫详图"},
            {"match": "至于陆少侠所需的真灵血材，我族祖上曾守护过一枚", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "沈烛音告知燃灯国师丹房密库藏有九幽冥凰血晶"},
            {"match": "陆伯父临去东海前也曾提过一嘴，古井水脉连通的那片", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "沈烛音补充归墟殖骨海深处栖息三阶海族真灵"},
            {"match": "九响【万骨丧钟】？非逢皇朝倾覆或百年大祭绝不轻鸣", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[gasps] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "东方九声万骨丧钟震落石窟碎石令沈烛音色变"},
            {"match": "少主不好了！大胤老神皇油尽灯枯熬不过这个月了", "role_id": "male_disciple_a", "speaker_name": "守昼斥候", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "染血蒙眼斥候冲入石窟急报三日后万灵添油屠城大典"},
        ],
        sfx_blueprint=[
            {"p": 10, "pos": "before", "slug": "twin_spirit_shock_spikes", "sfx_prompt": "Twin high-pitched crystalline energy spikes slicing silently through air with a sharp internal impact thud", "duration_seconds": 2.4, "gain_db": 1.5, "note": "嗡！两记惊神刺跨越百丈扎入双长老识海"},
            {"p": 15, "pos": "before", "slug": "meteor_descent_canyon_crash", "sfx_prompt": "Explosive lightning-and-fire meteoric descent crashing heavily onto jagged canyon stone", "duration_seconds": 2.8, "gain_db": 1.5, "note": "轰！陆烬携雷火如陨星砸落谷底"},
            {"p": 18, "pos": "before", "slug": "heavy_sabre_behead_twin_elders", "sfx_prompt": "Colossal heavy iron broadsword sweeping cleanly in a wide arc with blazing flames shattering bone shields", "duration_seconds": 3.0, "gain_db": 2.0, "note": "嗤啦！百零八斤断岳横扫一刀枭首双圆满长老"},
            {"p": 26, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "clean_sheathe_sabre_canyon", "gain_db": 1.0, "note": "山谷重归寂静，陆烬反手收刀归鞘"},
            {"p": 58, "pos": "before", "slug": "nine_tolls_myriad_bone_bell", "sfx_prompt": "Colossal ominous ancient bronze bell tolling deeply across distant wasteland shaking loose cavern gravel", "duration_seconds": 4.2, "gain_db": 2.0, "note": "咚咚咚！东方皇城连响九声万骨丧钟震动百丈石窟"},
        ],
    )
    j47, m47 = save_episode_scripts(s47, REPO_SCRIPTS_DIR, registry)
    built.append(("E047", j47, m47))

    # =========================================================================
    # E048 · 第48章 潜入永夜圣京，万民骨髓作灯油 (58 paras, 10 quotes)
    # =========================================================================
    md_48 = SOURCE_DIR / "第48章_潜入永夜圣京，万民骨髓作灯油.md"
    s48 = compile_episode_cue_sheet(
        episode_id="E048",
        chapter_number=48,
        source_md_path=md_48,
        source_rel_path=f"02_分章精修正文/{md_48.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_enter_eternal_night_imperial_capital",
                "start_p": 1,
                "title": "第一幕 · 潜入永夜京，三千丈骨塔",
                "bgm_prompt": WORLD_OST["w2_eternal_night_tension"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_silent_assassination_free_prisoners",
                "start_p": 14,
                "title": "第二幕 · 无声诛狱长，天牢结奇兵",
                "bgm_prompt": WORLD_OST["w2_ghost_market_stealth"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_empty_vault_nether_phoenix_crystal",
                "start_p": 29,
                "title": "第三幕 · 融墙入秘库，冥凰血晶成",
                "bgm_prompt": WORLD_OST["w2_ghost_market_stealth"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act4_late_zifu_breakthrough_golden_core_rage",
                "start_p": 40,
                "title": "第四幕 · 炼石晋后期，金丹震圣京",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(16, 39, "vast_hall"), (53, 58, "vast_hall")],
        skip_onomatopoeia_paras={20, 23, 45, 53},
        dialogue_specs=[
            {"match": "叩谢神皇圣师赐光，愿献微躯骨髓", "role_id": "weathered_elder_npc", "speaker_name": "圣京百姓", "tags": "[hoarsely] [trembling]", "stability": 0.0, "note": "长街未老先衰百姓闻号角如木偶跪地沙哑诵念"},
            {"match": "燃灯国师平日大多坐镇主塔顶层调理伪金丹", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[whispers]", "stability": 0.5, "space": "mental_realm", "note": "沈烛音传音告知司灯天牢与国师私人丹房方位"},
            {"match": "今夜子时动手。沈姑娘带城内守昼人暗桩在外城接应", "role_id": "lu_jin", "tags": "[whispers] [calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬沉静传音定下子时单刀潜入天牢丹房之计"},
            {"match": "骂吧，省点力气多骂两句，明晚大典一开", "role_id": "zhao_kui", "speaker_name": "独目典狱长", "tags": "[sarcastic] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "紫府圆满独目典狱长端起血髓酒狞笑嘲弄水牢重犯"},
            {"match": "好恐怖的暗杀手段！阁下是何方高人", "role_id": "qin_lie", "speaker_name": "雷横", "tags": "[gasps] [whispers]", "stability": 0.0, "space": "vast_hall", "note": "水牢内虬髯老刀客雷横目睹无声瞬杀失声低呼"},
            {"match": "救你们命的人。我替诸位化去体内锁髓钩", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬斩断牢门锁链与三十四名紫府重犯定下破阵盟约"},
            {"match": "恩公活命大恩，莫说砸两座阵脚", "role_id": "qin_lie", "speaker_name": "雷横", "tags": "[fiercely] [whispers]", "stability": 0.0, "space": "vast_hall", "note": "雷横拍胸抱拳率众散修慨然应战"},
            {"match": "三阶跨界真灵至宝，【九幽冥凰血晶】！到手了", "role_id": "lu_jin", "tags": "[softly] [excited]", "stability": 0.0, "space": "vast_hall", "note": "陆烬将九幽冥凰血晶与国师密库宝药灵石一扫而空"},
            {"match": "炼", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "note": "陆烬退回暗室吞吸三十六枚极品灵石冲击紫府后期"},
            {"match": "好胆！竟有界外无锁老鼠溜进圣京盗本座宝药", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "金丹中期燃灯国师发现密库被盗暴怒下令提前抽城"},
        ],
        sfx_blueprint=[
            {"p": 9, "pos": "before", "slug": "bone_tower_low_horn", "sfx_prompt": "Deep eerie low ceremonial horn echoing across stone city streets", "duration_seconds": 3.0, "gain_db": 1.0, "note": "中心三千丈骨灯主塔传来低沉号角声"},
            {"p": 20, "pos": "before", "slug": "silent_spike_catch_wine_bowl", "sfx_prompt": "Faint sharp mental needle hum followed by a ceramic wine bowl set gently onto an iron table in silence", "duration_seconds": 2.4, "gain_db": 1.0, "note": "嗡！惊神刺定住典狱长，陆烬接住酒碗无声抹喉"},
            {"p": 26, "pos": "before", "slug": "blade_qi_sever_dungeon_chains", "sfx_prompt": "Crisp dark-gold blade slash cleanly severing heavy iron prison chains inside a damp stone dungeon", "duration_seconds": 2.5, "gain_db": 1.5, "note": "暗金刀气斩断水牢大门锁链"},
            {"p": 45, "pos": "before", "motif_id": "motif_qi_sea_shatter", "slug": "supreme_spirit_stones_late_zifu", "gain_db": 1.5, "note": "咔嚓！三十六枚极品灵石碎裂助陆烬冲入紫府境后期"},
            {"p": 53, "pos": "before", "slug": "main_tower_golden_core_eruption", "sfx_prompt": "Colossal thunderous fire-cloud explosion high atop a stone tower sending crushing pressure across a vast city", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆！太祖不灭骨灯主塔顶端炸开金丹中期恐怖火云"},
        ],
    )
    j48, m48 = save_episode_scripts(s48, REPO_SCRIPTS_DIR, registry)
    built.append(("E048", j48, m48))

    # =========================================================================
    # E049 · 第49章 金丹威压临城，古井下的遮天黑幕 (75 paras, 17 quotes)
    # =========================================================================
    md_49 = SOURCE_DIR / "第49章_金丹威压临城，古井下的遮天黑幕.md"
    s49 = compile_episode_cue_sheet(
        episode_id="E049",
        chapter_number=49,
        source_md_path=md_49,
        source_rel_path=f"02_分章精修正文/{md_49.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_citywide_soul_drain_diversion_strike",
                "start_p": 1,
                "title": "第一幕 · 万灵抽城劫，奇兵碎阵枢",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_genelock_burst_cleave_nine_gates",
                "start_p": 21,
                "title": "第二幕 · 燃血化霜电，十息破九门",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act3_ten_slashes_behead_bone_dragon_peak_zifu",
                "start_p": 37,
                "title": "第三幕 · 十刀斩骨蛟，紫府大圆满",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_black_sun_mother_disc_preceptor_returns",
                "start_p": 62,
                "title": "第四幕 · 井底见黑日，国师破顶来",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(28, 75, "vast_hall")],
        skip_onomatopoeia_paras={2, 16, 26, 32, 47, 57, 71},
        dialogue_specs=[
            {"match": "我的头好痛！救命啊，圣塔在吸我们的命", "role_id": "male_disciple_b", "speaker_name": "圣京百姓", "tags": "[crying] [desperately]", "stability": 0.0, "note": "万灵添油大阵发动长街百姓被强扯魂光惨烈求救"},
            {"match": "好狠毒的老狗，竟真敢拿一城百万人命强冲金丹后期", "role_id": "lu_jin", "tags": "[coldly] [angry]", "stability": 0.0, "note": "陆烬目睹全城炼狱眼神冷冽如铁"},
            {"match": "欲斩毒蛇，先挖其巢！攻敌必救", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "note": "陆烬瞬息定下声东击西直捣古井之策"},
            {"match": "大阵已开，再拖半柱香全城皆成干尸", "role_id": "lu_jin", "tags": "[fiercely] [rushed]", "stability": 0.0, "space": "mental_realm", "note": "陆烬三里半神识同时传音雷横与沈烛音强攻西南辅阵"},
            {"match": "好！老子这条命本就是恩公救的", "role_id": "qin_lie", "speaker_name": "雷横", "tags": "[fiercely] [shouting]", "stability": 0.0, "note": "雷横怒吼率三十三名紫府散修撞破天牢杀向西城阵枢"},
            {"match": "南城两处阵台已碎，陆少侠尽管放手去破古井", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[fiercely]", "stability": 0.0, "space": "mental_realm", "note": "沈烛音一剑劈裂南门白骨阵台传音回报"},
            {"match": "嗯？一群本该关在水牢等死的紫府蝼蚁，还有守昼余孽", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[coldly] [angry]", "stability": 0.0, "space": "vast_hall", "note": "百万魂流一滞令主塔上空燃灯国师惊怒转头"},
            {"match": "区区跳梁小丑也敢坏本座大典，禁军大统领何在", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "燃灯国师分化身并将九成金丹神念投向西南外城"},
            {"match": "就是现在", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "note": "十息空当撕开陆烬自皇宫阴影暴起突进"},
            {"match": "大胆狂徒，此乃国师禁地，没有圣师手谕擅闯者", "role_id": "male_guard_captain", "speaker_name": "金甲神卫", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "主塔底座第一重玄铁巨门八名金甲神卫举戟怒喝"},
            {"match": "滚开", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬脚步不停一刀连人带门劈穿九重地宫"},
            {"match": "吼", "role_id": "sect_elder_antagonist", "speaker_name": "噬日骨蛟", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "古井旁四十丈准三阶噬日骨蛟喷出漆黑盲火毒雾"},
            {"match": "挡我路者，死", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬催动妖煞火烧穿毒雾并发出巅峰惊神刺"},
            {"match": "嗷", "role_id": "sect_elder_antagonist", "speaker_name": "噬日骨蛟", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "神识长锥贯入兽魂火种令噬日骨蛟剧痛翻滚"},
            {"match": "第十刀，断首", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬腾空十丈双手高举断岳一刀斩断准三阶蛟颈"},
            {"match": "四千年不见天日，今日该碎了", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬晋升紫府大圆满跃下百丈井底举刀劈向永夜黑日母盘"},
            {"match": "好个声东击西的紫府小畜生！竟敢潜入禁地妄动上界仙使", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "燃灯国师轰穿千丈岩层携百丈金丹火海俯冲杀至"},
        ],
        sfx_blueprint=[
            {"p": 2, "pos": "before", "slug": "thirty_six_bone_pillars_erupt", "sfx_prompt": "Deep subterranean rumble followed by thirty-six massive energy beams erupting across a vast stone city", "duration_seconds": 3.4, "gain_db": 1.5, "note": "轰隆隆！三十六座白骨阵枢冲起光柱发动万灵添油大阵"},
            {"p": 16, "pos": "before", "slug": "outer_city_altars_shatter_blast", "sfx_prompt": "Twin thunderous fiery oil explosions shattering massive stone altars in the distance", "duration_seconds": 3.0, "gain_db": 1.5, "note": "轰！轰！西南外城四座白骨阵枢接连炸碎"},
            {"p": 24, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "genelock_thunder_roc_charge", "gain_db": 1.5, "note": "一阶基因锁圆满叠加雷鹏极速直扑主塔地宫"},
            {"p": 32, "pos": "before", "slug": "cleave_nine_iron_palace_gates", "sfx_prompt": "Colossal heavy iron broadsword smashing straight through thick forged iron gates in rapid thunderous succession", "duration_seconds": 3.6, "gain_db": 2.0, "note": "轰咔！十息之内连劈九重玄铁地宫巨门杀入熄灯古井"},
            {"p": 57, "pos": "before", "slug": "tenth_sabre_sever_bone_dragon", "sfx_prompt": "Blazing heavy broadsword cleaving thick bone armor apart followed by a massive armored body crashing onto stone", "duration_seconds": 3.5, "gain_db": 2.0, "note": "咔嚓轰隆！第十刀斩断噬日骨蛟晋升三十六丈紫府大圆满"},
            {"p": 71, "pos": "before", "slug": "golden_core_blast_cavern_dome", "sfx_prompt": "Cataclysmic overhead explosion blasting open a thick underground rock dome with falling boulders and surging fire", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆！燃灯国师一击轰穿千丈地宫穹顶杀至井底"},
        ],
    )
    j49, m49 = save_episode_scripts(s49, REPO_SCRIPTS_DIR, registry)
    built.append(("E049", j49, m49))

    # =========================================================================
    # E050 · 第50章 紫府逆伐金丹，焚锁火烧穿骨灯塔！ (69 paras, 14 quotes)
    # =========================================================================
    md_50 = SOURCE_DIR / "第50章_紫府逆伐金丹，焚锁火烧穿骨灯塔！.md"
    s50 = compile_episode_cue_sheet(
        episode_id="E050",
        chapter_number=50,
        source_md_path=md_50,
        source_rel_path=f"02_分章精修正文/{md_50.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_heavy_sabre_blocks_core_fire_blind_domain",
                "start_p": 1,
                "title": "第一幕 · 横刀扛丹火，盲域夺五识",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_blind_heart_eye_parries_expose_false_core",
                "start_p": 21,
                "title": "第二幕 · 闭目挡九刃，真目破髓丹",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_sacrifice_shoulder_reverse_pour_demon_fire",
                "start_p": 37,
                "title": "第三幕 · 碎肩欺三尺，煞火灌髓脐",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_burn_through_bone_tower_slay_golden_core",
                "start_p": 56,
                "title": "第四幕 · 焚穿三千塔，逆斩成假丹",
                "bgm_prompt": WORLD_OST["w2_first_sunlight_catharsis"],
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(1, 55, "vast_hall"), (61, 69, "vast_hall")],
        skip_onomatopoeia_paras={5, 14, 27, 39, 48, 54, 58, 63},
        dialogue_specs=[
            {"match": "起", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬横架百零八斤断岳硬接三阶万魂燃灯钵一击"},
            {"match": "金丹中期的本命真火，看来也不过如此，还劈不断我这把刀", "role_id": "lu_jin", "tags": "[coldly] [sarcastic]", "stability": 0.0, "space": "vast_hall", "note": "陆烬以刀杵地擦去唇边鲜血冷笑嘲讽"},
            {"match": "嗯？区区紫府大圆满，正面硬接本座三阶法宝一击竟然没死", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[gasps] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "燃灯国师眼皮猛跳震惊于陆烬重刀与体魄"},
            {"match": "难怪敢盗本座的【九幽冥凰血晶】，原来是个修成了上古无瑕道基", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[hoarsely] [excited]", "stability": 0.0, "space": "vast_hall", "note": "燃灯国师看清陆烬无瑕暗金宝光贪婪杀意暴涨"},
            {"match": "桀桀桀，在这绝对盲昼领域里，看不见也探不着", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[laughs] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "燃灯国师激活盲昼噬火锁剥夺五识祭出九道金丹弯刃"},
            {"match": "左三，右四，头顶两道", "role_id": "lu_jin", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬闭目散识以基因锁毛孔感应精准预判九刃方位"},
            {"match": "什么？闭着眼睛不用神识也能挡住本座九道金丹斩", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "九道金丹骨火弯刃尽碎令燃灯国师骇然失色"},
            {"match": "原来如此", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "破妄真目洞穿燃灯国师满布怨魂裂纹的吸髓脐带金丹"},
            {"match": "什么狗屁金丹真人，不过是靠吸食千万百姓脑髓魂火", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬一语揭穿燃灯国师伪劣髓丹致命死穴"},
            {"match": "找死！就算本座是髓丹，捏死你这紫府爬虫也易如反掌", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "燃灯国师羞怒交加推出三丈万魂骨火大印封死井底"},
            {"match": "你疯了不成", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "陆烬以左肩骨裂硬换贴身欺入国师身前三尺死域"},
            {"match": "老狗，你不是最喜欢抽全城百姓的骨髓点灯么", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬卡死钵口将整团母体焚锁妖煞火反向按入抽魂主管道"},
            {"match": "不！这是什么鬼火，我的金丹……快停下，给本座滚出去啊", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "焚锁妖煞火顺脐带狂涌入髓丹引爆百年万民怨气"},
            {"match": "紫府……逆伐金丹……老夫不甘", "role_id": "chiyang_laozu", "speaker_name": "燃灯国师", "tags": "[hoarsely] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "金丹炸碎经脉寸断的燃灯国师临死绝望伸手"},
        ],
        sfx_blueprint=[
            {"p": 5, "pos": "before", "slug": "sabre_block_core_fire_pillar", "sfx_prompt": "Deafening metallic broadsword clash blocking a massive fire blast followed by stone pillars shattering", "duration_seconds": 3.5, "gain_db": 2.0, "note": "铛轰！断岳重刀硬扛万魂燃灯钵金丹火柱撞穿三根石柱"},
            {"p": 14, "pos": "before", "slug": "blind_day_domain_vacuum_pulse", "sfx_prompt": "Deep sub-bass arcane vacuum pulse swallowing ambient sound into sudden eerie silence", "duration_seconds": 2.8, "gain_db": 1.5, "note": "嗡！盲昼噬火锁本源禁域张开剥夺五识"},
            {"p": 27, "pos": "before", "slug": "nine_rapid_blind_sabre_parries", "sfx_prompt": "Nine ultra-fast crisp metallic steel parries ringing out in rapid succession inside a dark stone cavern", "duration_seconds": 2.8, "gain_db": 2.0, "note": "叮叮当当！闭目心眼刀半息内磕飞九道金丹骨火弯刃"},
            {"p": 39, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "shoulder_impact_three_feet_dash", "gain_db": 1.5, "note": "嘭咔嚓！左肩硬扛骨火印借反震雷鹏极速欺入三尺"},
            {"p": 48, "pos": "before", "slug": "demon_fire_ignite_marrow_core", "sfx_prompt": "Explosive surge of wildfire rushing through a hollow conduit culminating in a crystalline core shattering blast", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰哗砰咔嚓！焚锁妖煞火逆灌引爆伪劣髓丹与万魂燃灯钵"},
            {"p": 58, "pos": "before", "slug": "three_thousand_zhang_tower_burn_collapse", "sfx_prompt": "Colossal stone-and-bone tower erupting into a sky-piercing pillar of fire and crumbling thunderously", "duration_seconds": 4.2, "gain_db": 2.0, "note": "轰隆隆！三千丈太祖不灭骨灯主塔化作紫黑火柱崩塌解体"},
        ],
    )
    j50, m50 = save_episode_scripts(s50, REPO_SCRIPTS_DIR, registry)
    built.append(("E050", j50, m50))

    _tmp_ctx.cleanup()
    return built


if __name__ == "__main__":
    items = build_all_batch09()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name} | {mp.name}", flush=True)
