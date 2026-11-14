"""Build and validate Batch 16 (GRAND FINALE): Episodes E111–E120 (Chapters 111–120 of 《诸界锁仙》)."""

from __future__ import annotations

from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = (
    Path("/tmp/zhujie_source_chapters")
    if Path("/tmp/zhujie_source_chapters").is_dir()
    else Path("/shared/user/.gemini/config/zhujie_suoxian_audio/source_chapters")
)
REGISTRY_PATH = REPO_ROOT / "projects/zhujie_suoxian/00_声音选角档案与进度台账/voice_casting_registry.json"
REPO_SCRIPTS_DIR = REPO_ROOT / "projects/zhujie_suoxian/02_分集广播剧台本"

SCRATCH_DIR = Path(__file__).resolve().parent
REPO_SRC = REPO_ROOT / "src"
for p in (str(REPO_SRC), str(SCRATCH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from aigc_audio_pipeline.compiler import (
    compile_episode_cue_sheet,
    parse_chapter_paragraphs,
    save_episode_scripts,
)
from aigc_audio_pipeline.models import EpisodeCueSheet, VoiceCastingRegistry
from world_ost_palette import WORLD_OST

_CJK_RE = re.compile(r"[\u4e00-\u9fff]+")


def build_all_batch16() -> list[tuple[EpisodeCueSheet, Path, Path, float]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[EpisodeCueSheet, Path, Path, float]] = []

    def _finalize(
        sheet: EpisodeCueSheet,
        md_file: Path,
        skip_paras: set[int],
    ) -> None:
        _, paras = parse_chapter_paragraphs(md_file)
        src_cjk = sum(len("".join(_CJK_RE.findall(para))) for para in paras)
        comp_cjk = sum(
            len("".join(_CJK_RE.findall(c.text)))
            for c in sheet.cues
            if c.kind == "dialogue"
        )
        ratio = comp_cjk / max(1, src_cjk)
        jp, mp = save_episode_scripts(sheet, REPO_SCRIPTS_DIR, registry)
        built.append((sheet, jp, mp, ratio))

    # =========================================================================
    # E111 · 第111章 第四层终极真相：原初铸锁始祖「墟」！ (65 paras, 15 quotes)
    # =========================================================================
    md_111 = SOURCE_DIR / "第111章_第四层终极真相：原初铸锁始祖「墟」！.md"
    skip_111 = {8, 15, 60}
    s111 = compile_episode_cue_sheet(
        episode_id="E111",
        chapter_number=111,
        source_md_path=md_111,
        source_rel_path=f"02_分章精修正文/{md_111.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_lingxiao_headless_corpse_taiyi",
                "start_p": 1,
                "title": "第一幕 · 凌霄无头尸，王座见太一",
                "bgm_prompt": WORLD_OST["f3_celestial_palace_confrontation"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_primordial_xu_five_locks_cradle",
                "start_p": 16,
                "title": "第二幕 · 始祖抽仙骨，五锁铸摇篮",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act3_cold_math_betrayal_dead_locks",
                "start_p": 31,
                "title": "第三幕 · 至算零点四，背刺焊死锁",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act4_four_lives_puzzle_abyssal_sea",
                "start_p": 45,
                "title": "第四幕 · 四世归凡心，源壁映寂灭",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 110.0,
            },
        ],
        acoustic_ranges=[(1, 15, "vast_hall"), (16, 44, "memory_echo"), (45, 65, "vast_hall")],
        skip_onomatopoeia_paras=skip_111,
        dialogue_specs=[
            {"match": "这具无头仙躯的气息超越了合道无极", "role_id": "jiang_qinghuang", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰震动凝视天道母碑基座下的无头真仙古尸"},
            {"match": "因为他本来就不该叫陆烬", "role_id": "tai_yi", "tags": "[calmly]", "stability": 1.0, "space": "vast_hall", "note": "白玉王座上的太一缓缓垂眸开口"},
            {"match": "欢迎回家，我的本尊", "role_id": "tai_yi", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一揭晓原初第一铸锁者「墟」之名"},
            {"match": "原来……这才是【无限认知世界】", "role_id": "jiang_qinghuang", "tags": "[gasps] [softly]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰明悟认知保育世界与五重保护基因锁初衷"},
            {"match": "那不是囚笼，那是始祖【墟】拿自己半条命", "role_id": "jiang_qinghuang", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰震撼质问护道摇篮为何沦为血肉牧场"},
            {"match": "胜率不足半成，在逻辑上便等同于必败", "role_id": "tai_yi", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "太一毫无愧疚陈述一亿三千万次推演定理"},
            {"match": "既然放任羊群冲出栅栏与恶狼搏命", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一道出永远锁死栅栏的极端秩序逻辑"},
            {"match": "至于你，陆烬", "role_id": "tai_yi", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "太一走下玉阶俯视陆烬揭开最后身世拼图"},
            {"match": "当年本尊被我钉死在母碑王座下的最后一瞬", "role_id": "tai_yi", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "太一道出第零号原初无脐心胎与四片残存意志"},
            {"match": "你斩出的极道杀性化作了", "role_id": "tai_yi", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "太一历数苍溟、顾长渊与枯骨守墓人三世分魂"},
            {"match": "而十八岁那年秋雨夜，在第七十三号牧场", "role_id": "tai_yi", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一指向陆烬心脏点破原初凡人本心真相"},
            {"match": "说完了？", "role_id": "lu_jin", "tags": "[calmly] [coldly]", "stability": 1.0, "space": "vast_hall", "note": "陆烬平静收回零号铭牌，手按断岳刀柄反问"},
            {"match": "看清楚外头那片真正的绝望了么", "role_id": "tai_yi", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一挥袖展露源壁外翻涌的归墟大寂灭源海"},
            {"match": "这九个纪元以来，若非我狠下心焊死三千牧场", "role_id": "tai_yi", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一站在万丈母碑之巅为九纪圈养辩护"},
            {"match": "放下你手里那把凡铁断刀", "role_id": "tai_yi", "tags": "[softly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "太一伸出白金右手蛊惑陆烬散去凡心重归牧羊神"},
        ],
        sfx_blueprint=[
            {"p": 3, "pos": "before", "slug": "order_chains_bind_primordial_corpse", "sfx_prompt": "Thousands of heavy platinum chains clinking coldly around a colossal stone monument in a silent vast hall", "duration_seconds": 3.4, "gain_db": 0.5, "note": "九万九千根白金秩序神链哗啦轻响锁死无头仙躯"},
            {"p": 8, "pos": "before", "slug": "taiyi_divine_gaze_resonance", "sfx_prompt": "Deep resonant celestial bronze chime and pure geometric crystal vibration descending from a high throne", "duration_seconds": 2.8, "gain_db": 1.0, "note": "嗡！母碑顶端太一垂下纯白无瞳目光"},
            {"p": 15, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "zero_token_unlock_primordial_memory", "gain_db": 1.5, "note": "轰隆！零号铭牌映照母碑铺展九纪元前太初记忆"},
            {"p": 40, "pos": "before", "slug": "chains_pierce_primordial_spine", "sfx_prompt": "Sudden violent eruption of metallic chains piercing stone and heavy bronze impact echoing in an abyss", "duration_seconds": 3.2, "gain_db": 2.0, "note": "秩序神链从母碑背后暴起贯穿始祖墟仙躯"},
            {"p": 60, "pos": "before", "slug": "sighing_wall_turns_transparent_abyss", "sfx_prompt": "Colossal crystalline wall resonating and turning transparent to reveal a low sub-bass abyssal ocean rumble", "duration_seconds": 3.8, "gain_db": 1.5, "note": "轰隆！叹息源壁透明如镜展露归墟大寂灭源海"},
        ],
    )
    _finalize(s111, md_111, skip_111)

    # =========================================================================
    # E112 · 第112章 牧羊神与破笼人，凌霄殿上问大道！ (54 paras, 25 quotes)
    # =========================================================================
    md_112 = SOURCE_DIR / "第112章_牧羊神与破笼人，凌霄殿上问大道！.md"
    skip_112 = {34, 44, 52}
    s112 = compile_episode_cue_sheet(
        episode_id="E112",
        chapter_number=112,
        source_md_path=md_112,
        source_rel_path=f"02_分章精修正文/{md_112.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_blood_palace_taiyi_amnesty",
                "start_p": 1,
                "title": "第一幕 · 骨血筑仙阙，牧神许特赦",
                "bgm_prompt": WORLD_OST["f3_celestial_palace_confrontation"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_mortal_backbone_name_is_lujin",
                "start_p": 13,
                "title": "第二幕 · 拾级问大道，坐不改陆烬",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act3_true_immortal_wrath_cleave_dome",
                "start_p": 38,
                "title": "第三幕 · 万锁诛仙阵，破穹上堤巅",
                "bgm_prompt": WORLD_OST["f4_final_battle_slay_taiyi"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 54, "vast_hall")],
        skip_onomatopoeia_paras=skip_112,
        dialogue_specs=[
            {"match": "只要你点头，只需一念之间", "role_id": "tai_yi", "tags": "[softly]", "stability": 0.5, "space": "vast_hall", "note": "太一保持伸手姿态温和劝诱"},
            {"match": "你不必再流血拼命，不必再去赌那连半成都没有", "role_id": "tai_yi", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "太一许诺将北渊亲故与姜清凰划入仙庭特赦神域"},
            {"match": "太一，你刚才算了一亿三千万次胜率", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬踏上九重白玉台阶停步开口"},
            {"match": "可有一笔账，你这颗只有算术没有心肝的脑子", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬摩挲断岳刀柄旧痕冷声斥太一算错九纪"},
            {"match": "天道母碑穷尽宇宙因果，绝无错漏", "role_id": "tai_yi", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "太一微蹙眉头笃定天算无漏"},
            {"match": "你错就错在，把活生生的人", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬字字如重锤砸向凌霄宝殿穹顶"},
            {"match": "你说把众生锁死在黑屋子里当猪羊", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬双眸燃起暗金神光质问牧羊神"},
            {"match": "我在大苍北渊见过我的养父陆擎苍", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬追忆养父陆擎苍天渊剖丹拒向血月低头"},
            {"match": "我在天渊谷底见过天生没有眼珠的盲眼少女阿盲", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬追忆盲女阿盲仰望第一缕干净真星"},
            {"match": "我还在烬昼界见过四千年不曾摘下蒙眼黑布的守昼人", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬历数守昼老人、归墟硬汉与老槐树下的福伯"},
            {"match": "你把三千世界里所有敢抬头看天", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬重踏玉阶怒斥太一掐断万界脊梁"},
            {"match": "猪羊不知明日刀俎，那不叫安稳，那叫等死", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬反手拔出断岳重刀遥指太一眉心"},
            {"match": "当年【墟】抽自己半截脊梁铸五重基因锁", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬为始祖登天梯正名，痛斥太一屠宰场"},
            {"match": "至于你让我散去记忆变回太初古神", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬回望无头古尸与身后生死与共的姜清凰"},
            {"match": "听好了，太一！", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬眼神清澈坚定如万古磐石"},
            {"match": "太初始祖【墟】，早在九个纪元前被你背刺斩首", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬宣告墟、顾长渊与上一轮回刀客皆已谢幕"},
            {"match": "今日站在这座凌霄宝殿上提刀斩你的人", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬拒绝神化自我，不作任何人的牧羊神"},
            {"match": "行不改名，坐不改姓，大苍北渊陆氏之子，陆烬", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬凌霄问大道巅峰自报家门"},
            {"match": "大苍北渊陆氏之子，陆烬", "role_id": "narrator", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "gap_after_s": 0.1, "note": "旁白紧接回响陆烬自报家门十字震彻宝殿"},
            {"match": "说得好！本帝等了三千年", "role_id": "jiang_qinghuang", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰眼底绽放笑意，玄凰帝剑凤鸣长吟"},
            {"match": "冥顽不灵。本以为历经万世轮回", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一收回右手敛去温和假象，双眸化作毁灭旋涡"},
            {"match": "既然你不愿重归为【墟】，那我便亲手抹去你这道失控", "role_id": "tai_yi", "tags": "[coldly] [angry]", "stability": 0.0, "space": "vast_hall", "note": "太一决意抹杀陆烬将其炼入母碑"},
            {"match": "天道总敕：万锁归源，诛仙灭神", "role_id": "tai_yi", "tags": "[shouting] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "太一结总纲法印发动第九境真仙三千母锁大阵"},
            {"match": "清凰，破东阙，上天宫穹顶", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬催动四阶基因锁引战场至源海堤坝"},
            {"match": "好，本帝替你开路！", "role_id": "jiang_qinghuang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰化千丈冰晶神凰一剑斩向九重琉璃神穹"},
        ],
        sfx_blueprint=[
            {"p": 12, "pos": "before", "slug": "steady_footsteps_jade_stairs", "sfx_prompt": "Slow steady resolute boot footsteps ascending echoing white marble palace stairs in dead silence", "duration_seconds": 3.2, "gain_db": 1.0, "note": "陆烬踏着沉稳脚步走上通往天道母碑的九重白玉阶"},
            {"p": 25, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "draw_duanyue_point_at_taiyi", "gain_db": 1.5, "note": "铿锵反手拔出断岳重刀遥指太一眉心"},
            {"p": 34, "pos": "before", "slug": "mortal_blade_intent_shakes_palace", "sfx_prompt": "Colossal resonant shockwave and deep bronze bell tremor shaking an ancient stone palace", "duration_seconds": 3.5, "gain_db": 2.0, "note": "轰隆——！凡人本心刀意震得整座凌霄宝殿剧颤"},
            {"p": 44, "pos": "before", "slug": "three_thousand_mother_chains_storm", "sfx_prompt": "Thousands of heavy metallic chains erupting from a monolith and whipping through the air like a tempest", "duration_seconds": 3.6, "gain_db": 1.5, "note": "哗啦啦啦！三千世界母锁化作白金锁链巨龙绞杀"},
            {"p": 52, "pos": "before", "slug": "phoenix_sword_duanyue_rip_palace_dome", "sfx_prompt": "Blazing icy sword slash followed by a thunderous heavy broadsword strike shattering a crystal palace dome", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆！刀剑合击撕开凌霄殿顶百丈豁口直冲堤巅"},
        ],
    )
    _finalize(s112, md_112, skip_112)

    # =========================================================================
    # E113 · 第113章 真仙神罚锁诸天，刀剑同心战太一！ (69 paras, 17 quotes)
    # =========================================================================
    md_113 = SOURCE_DIR / "第113章_真仙神罚锁诸天，刀剑同心战太一！.md"
    skip_113 = {6, 12, 18, 22, 29, 36, 44, 61}
    s113 = compile_episode_cue_sheet(
        episode_id="E113",
        chapter_number=113,
        source_md_path=md_113,
        source_rel_path=f"02_分章精修正文/{md_113.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_sighing_dike_dual_edicts_blood_mark",
                "start_p": 1,
                "title": "第一幕 · 叹息骨长城，刀剑伤真仙",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act2_hundred_clashes_empress_blocks_erasure",
                "start_p": 36,
                "title": "第二幕 · 抹名绝因剑，玄凰燃羽挡",
                "bgm_prompt": WORLD_OST["f4_final_battle_slay_taiyi"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_mother_stele_crush_four_locks_sealed",
                "start_p": 56,
                "title": "第三幕 · 母碑压断岳，四锁陷绝渊",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(1, 69, "vast_hall")],
        skip_onomatopoeia_paras=skip_113,
        dialogue_specs=[
            {"match": "在凌霄殿内尚要顾忌震坏宫室", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一携万丈天道母碑降临叹息堤坝高空"},
            {"match": "第一敕：万血归锁，封窍", "role_id": "tai_yi", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一点出母碑第一道太初血纹封锁周天星窍"},
            {"match": "拿我当年留在石碑上的旧规矩来锁我的血", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬催动四阶基因锁与五阶焚锁妖煞火烧断禁制"},
            {"match": "本尊的第四阶基因锁果然已经圆满", "role_id": "tai_yi", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "太一淡漠点评境界一重天之隔"},
            {"match": "第二敕：岁星倒悬，剥寿十万载", "role_id": "tai_yi", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一引灰白岁月洪流冲向陆烬刀锋"},
            {"match": "你的对手不止他一个！", "role_id": "jiang_qinghuang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰横剑侧翼以斩岁剑意劈开岁月乱流"},
            {"match": "刀剑合璧，竟能以半步真仙之躯斩断母碑两根主链", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一抹去左颊淡金仙血，九纪以来首次负伤"},
            {"match": "难怪当年本尊宁可舍弃无上仙躯也要赌你这颗凡心", "role_id": "tai_yi", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "太一彻底收起试探，全力催沸万丈母碑"},
            {"match": "天道终敕：抹名绝因！", "role_id": "tai_yi", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百零八招交错际太一自损气运抽出概念抹名剑"},
            {"match": "陆烬小心！", "role_id": "jiang_qinghuang", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "千钧一发际姜清凰察觉陆烬后心透明绝杀剑"},
            {"match": "三千年前顾长渊替本帝剖心挡了一劫", "role_id": "jiang_qinghuang", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰主动燃烧三片太上玄凰帝羽横挡陆烬后背"},
            {"match": "清凰！", "role_id": "lu_jin", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "见姜清凰喋血撞入断骨柱，陆烬目眦欲裂"},
            {"match": "顾念儿女私情，这便是凡心最大的死穴", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一冷酷抓住破绽将万丈天道母碑当空镇落"},
            {"match": "断岳，给我顶住！", "role_id": "lu_jin", "tags": "[hoarsely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬双足踏入真仙脊骨横举断岳硬扛万丈母碑"},
            {"match": "陆烬！快弃刀退回玄黄界门", "role_id": "jiang_qinghuang", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "被秩序光环钉住的姜清凰红着眼眶凄声嘶喊"},
            {"match": "退不走了。四阶基因锁已被母碑源头彻底锁死", "role_id": "tai_yi", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一立于母碑顶端居高临下宣判绝境"},
            {"match": "承认吧，陆烬。凡人本心终究敌不过天道至算", "role_id": "tai_yi", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "太一逼迫陆烬散去神魂回炉重铸"},
        ],
        sfx_blueprint=[
            {"p": 6, "pos": "before", "slug": "taiyi_descends_mother_stele_rises", "sfx_prompt": "Colossal stone monolith tearing through palace roofs into rushing cosmic wind with deep sub-bass rumble", "duration_seconds": 3.6, "gain_db": 1.5, "note": "轰隆！太一踏出殿顶，万丈天道母碑穿透宫阙升空"},
            {"p": 12, "pos": "before", "motif_id": "motif_qi_sea_shatter", "slug": "blood_lock_edict_seals_acupoints", "gain_db": 1.0, "note": "嗡！母碑第一敕从基因底层封锁周天星窍"},
            {"p": 18, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "fourth_lock_demon_fire_burn_seals", "gain_db": 1.5, "note": "嗤啦！四阶基因锁携焚锁妖煞火烧断体表禁制"},
            {"p": 29, "pos": "before", "slug": "duanyue_severs_two_order_chains", "sfx_prompt": "Deafening heavy broadsword impact clashing against thick platinum chains and snapping two massive links", "duration_seconds": 3.5, "gain_db": 2.0, "note": "铛——！刀剑同心劈断太一身前两根秩序主神链"},
            {"p": 44, "pos": "before", "slug": "invisible_name_erasure_sword_pierce", "sfx_prompt": "Eerie razor-thin dimensional rift slicing almost silently through void air with icy high-frequency tension", "duration_seconds": 2.4, "gain_db": 1.5, "note": "嗤！透明天道抹名剑瞬息刺至陆烬后心半寸"},
            {"p": 61, "pos": "before", "slug": "mother_stele_crushes_duanyue_cracks", "sfx_prompt": "Crushing celestial stone monolith pressing down on a heavy iron broadsword with three sharp metal fracture cracks", "duration_seconds": 3.8, "gain_db": 2.5, "note": "咔嚓！万丈母碑压得断岳崩出三道贯穿裂痕"},
        ],
    )
    _finalize(s113, md_113, skip_113)

    # =========================================================================
    # E114 · 第114章 大寂灭源海灌体，直面不可名状之怖！ (64 paras, 21 quotes)
    # =========================================================================
    md_114 = SOURCE_DIR / "第114章_大寂灭源海灌体，直面不可名状之怖！.md"
    skip_114 = {29, 48, 59}
    s114 = compile_episode_cue_sheet(
        episode_id="E114",
        chapter_number=114,
        source_md_path=md_114,
        source_rel_path=f"02_分章精修正文/{md_114.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_see_through_taiyi_cowardice_smash_wall",
                "start_p": 1,
                "title": "第一幕 · 喝破伪仙怯，挥拳碎源壁",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act2_great_extinction_nihilism_pollution",
                "start_p": 36,
                "title": "第二幕 · 寂灭黑火灌，虚无蚀阳神",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_ten_thousand_worlds_torch_heartbeat",
                "start_p": 48,
                "title": "第三幕 · 万界借薪火，凡心永不墟",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 115.0,
            },
        ],
        acoustic_ranges=[(1, 35, "vast_hall"), (36, 47, "mental_realm"), (48, 64, "vast_hall")],
        skip_onomatopoeia_paras=skip_114,
        dialogue_specs=[
            {"match": "咳……哈哈哈！", "role_id": "lu_jin", "tags": "[hoarsely] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "绝境中看穿太一畏避源海，陆烬染血长笑"},
            {"match": "死到临头，你笑什么？", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "母碑顶端的太一微皱眉头质问"},
            {"match": "我笑我自己差点被你这副高高在上的真仙架子给唬住了", "role_id": "lu_jin", "tags": "[hoarsely] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬单臂死撑断岳刀脊直刺太一灵魂深处"},
            {"match": "太一，你霸占本尊仙躯与天道母碑整整九个纪元", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬喝破太一九纪仍停留在伪真仙之境的秘密"},
            {"match": "因为你怕死！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三字如惊雷劈碎太一维持万古的神圣假面"},
            {"match": "当年始祖【墟】在试锁石林留下的第五阶基因锁", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬道破第五阶超脱无漏唯有踏入大寂灭方能证道"},
            {"match": "你太一打从诞生的第一天起，就是因为算出了胜率不足半成", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬痛斥太一被源海吓破胆背叛本尊"},
            {"match": "住口！", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "被撕开最深恐惧伤疤的太一彻底暴怒"},
            {"match": "呈口舌之快有何用！大寂灭乃宇宙万道终焉", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一双掌猛压母碑厉声喝问陆烬敢不敢碰大寂灭"},
            {"match": "你不敢走的路，我陆烬今日走给你看", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬决绝撤去左半身仙元砸碎叹息堤坝晶壁"},
            {"match": "陆烬不要！", "role_id": "jiang_qinghuang", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰眼角迸裂血泪拼命劈砍秩序光环"},
            {"match": "彻头彻尾的疯子！不用我动手，不出三息", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.0, "space": "vast_hall", "note": "太一骇然暴退三十丈冷笑注视黑雾吞没陆烬"},
            {"match": "何必挣扎呢？宇宙终将热寂归墟", "role_id": "ancient_construct_echo", "speaker_name": "大寂灭虚无低语", "tags": "[whispers] [coldly]", "stability": 1.0, "space": "mental_realm", "note": "大寂灭逻辑污染第一重冰冷宇宙热寂低语"},
            {"match": "北渊秋雨是假的，福伯的热粥是碳水幻觉", "role_id": "eternal_night_whisper", "speaker_name": "大寂灭蚀心呢喃", "tags": "[whispers] [softly]", "stability": 0.0, "space": "mental_realm", "note": "大寂灭否定北渊记忆与人间意义的蚀心呢喃"},
            {"match": "结束了。九个纪元前【墟】自己都不敢生吞大寂灭原浆", "role_id": "tai_yi", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "太一冷漠俯视气息将归零的灰黑茧子"},
            {"match": "为陆尊贺！大苍儿郎，宁战死不做笼中虫", "role_id": "qin_lie", "speaker_name": "秦烈", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "memory_echo", "note": "大苍界北渊城独臂老帅秦烈率十万军民高举佩刀怒吼"},
            {"match": "愿借人间一寸日光，助破笼恩公斩尽长夜", "role_id": "female_maid_npc", "speaker_name": "沈烛音", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "memory_echo", "note": "烬昼界烈日下女剑仙沈烛音与百万百姓高举火把祈愿"},
            {"match": "陆烬，你答应过替他补全这人间，你不准死", "role_id": "jiang_qinghuang", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰拼死劈开光环扑来紧握陆烬冰冷右手"},
            {"match": "大寂灭说万物皆空、求索无用？", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.0, "space": "vast_hall", "note": "心脏重锤搏动，满头白发的陆烬重握断岳刀柄"},
            {"match": "一滴水或许会干涸，但只要三千世界万家灯火不灭", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬双眸重燃万丈金焰俯瞰归墟"},
            {"match": "给我——炼！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬以万家灯火强炼大寂灭原初黑火"},
        ],
        sfx_blueprint=[
            {"p": 29, "pos": "before", "slug": "fist_shatters_sighing_crystal_barrier", "sfx_prompt": "Heavy bare-knuckle impact cracking a thick cosmic crystal barrier open followed by surging dark ocean waves", "duration_seconds": 3.5, "gain_db": 2.0, "note": "咔嚓！陆烬左拳砸碎堤坝法则晶壁拽入大寂灭黑火"},
            {"p": 38, "pos": "before", "slug": "dark_nihility_flame_corrodes_meridians", "sfx_prompt": "Eerie freezing dark void current rushing inward and draining ambient sound into hollow crystalline static", "duration_seconds": 3.0, "gain_db": 1.0, "note": "大寂灭黑火涌入四肢百骸褪尽色彩"},
            {"p": 48, "pos": "before", "slug": "myriad_worlds_astrolabe_ripple", "sfx_prompt": "Warm faint golden starlight chime rippling outward through deep space", "duration_seconds": 2.8, "gain_db": 1.0, "note": "嗡……眉心万界坐标星盘自发亮起执着涟漪"},
            {"p": 58, "pos": "before", "slug": "golden_mortal_fire_river_surge", "sfx_prompt": "Millions of warm crackling torch sparks converging across space into a blazing river of golden fire", "duration_seconds": 3.6, "gain_db": 1.5, "note": "三千世界亿万人间薪火汇成金色星河冲入心房"},
            {"p": 59, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "mortal_heart_reignites_in_abyss", "gain_db": 2.0, "note": "轰隆！停滞发灰的凡人心脏爆发响彻源海的惊天搏动"},
        ],
    )
    _finalize(s114, md_114, skip_114)

    # =========================================================================
    # E115 · 第115章 万界众生借薪火，不作古神作陆烬！ (62 paras, 16 quotes)
    # =========================================================================
    md_115 = SOURCE_DIR / "第115章_万界众生借薪火，不作古神作陆烬！.md"
    skip_115 = {5, 27, 51, 56, 61}
    s115 = compile_episode_cue_sheet(
        episode_id="E115",
        chapter_number=115,
        source_md_path=md_115,
        source_rel_path=f"02_分章精修正文/{md_115.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_mortal_sparks_clash_thunder_spears",
                "start_p": 1,
                "title": "第一幕 · 薪火磨黑潮，白凰挡灭雷",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act2_shatter_god_crown_keep_mortal_name",
                "start_p": 31,
                "title": "第二幕 · 碎冠拒神格，只姓北渊陆",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_fifth_genelock_supreme_immortal",
                "start_p": 51,
                "title": "第三幕 · 奇点开五锁，九境证真仙",
                "bgm_prompt": WORLD_OST["f4_final_battle_slay_taiyi"],
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(1, 30, "vast_hall"), (31, 52, "mental_realm"), (53, 62, "vast_hall")],
        skip_onomatopoeia_paras=skip_115,
        dialogue_specs=[
            {"match": "给我，炼！", "role_id": "lu_jin", "tags": "[hoarsely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "灰黑雾潮中心陆烬死扣断岳刀柄嘶喝"},
            {"match": "有戏！", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "人间烟火与大寂灭原浆摩擦迸出灰金奇异火星"},
            {"match": "三息已过，他的生命波动非但没有归零", "role_id": "tai_yi", "tags": "[gasps] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "太一纯白双眸骤凝惊觉陆烬正在吞噬大寂灭"},
            {"match": "不可能！一亿三千万次演化早已证明", "role_id": "tai_yi", "tags": "[angry] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "太一淡漠面容出现裂痕，杀机暴涨十倍"},
            {"match": "休想在我面前破茧！天道敕令：九霄灭神枪，落", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一降下九道白金灭神雷枪直取陆烬与姜清凰"},
            {"match": "滚开！", "role_id": "jiang_qinghuang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰右手死扣陆烬五指，左手挥残剑迎战雷枪"},
            {"match": "陆烬，外头的雷我替你挡着！给我活着走出来", "role_id": "jiang_qinghuang", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "琵琶骨被雷枪擦碎单膝跪地的姜清凰挺直脊背嘶喊"},
            {"match": "陆烬", "role_id": "narrator", "tags": "[softly]", "stability": 0.5, "space": "mental_realm", "gap_after_s": 0.1, "note": "旁白紧接叙述‘陆烬’这短短一生"},
            {"match": "啧，戴上这顶破帽子固然省事", "role_id": "li_cang", "speaker_name": "苍溟残印", "tags": "[coldly] [laughs]", "stability": 0.0, "space": "mental_realm", "note": "识海魂龛中苍溟残印化作桀骜血焰冷笑"},
            {"match": "小子，本魔神当年把肉身输给你", "role_id": "li_cang", "speaker_name": "苍溟残印", "tags": "[fiercely]", "stability": 0.0, "space": "mental_realm", "note": "苍溟残印激励陆烬绝不当古神傀儡"},
            {"match": "三千年古棺霜寒，我等的是一个有血有肉能替她撑伞的人", "role_id": "fifth_soul_self", "speaker_name": "顾长渊残印", "tags": "[softly] [calmly]", "stability": 0.5, "space": "mental_realm", "note": "顾长渊清癯剑意轻轻震鸣托付人间真情"},
            {"match": "说得好。", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬低头凝视掌心厚茧与人间牵挂展颜一笑"},
            {"match": "始祖【墟】早在九个纪元前抽取脊骨筑起堤坝的那一天", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "mental_realm", "note": "陆烬向走完一生的始祖墟致敬，一拳轰碎古神冠冕"},
            {"match": "前人栽树未竟之功，自当由后人提刀续上", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "mental_realm", "note": "陆烬握拳将神冠轰成无主本源金沙"},
            {"match": "我陆烬不是任何古神的转世旧壳", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "mental_realm", "note": "陆烬拒绝借古神真名证道"},
            {"match": "自十八岁北渊秋雨碎丹那夜起，这具身躯", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "mental_realm", "note": "陆烬立下终极本心誓言：只姓陆，名烬"},
        ],
        sfx_blueprint=[
            {"p": 5, "pos": "before", "slug": "mortal_fire_clashes_abyssal_sludge", "sfx_prompt": "Boiling golden fire pouring onto ancient black ice, sizzling violently and bursting with metallic sparks", "duration_seconds": 3.0, "gain_db": 1.5, "note": "嗤啦！万界人间薪火与大寂灭原初黑火正面相撞"},
            {"p": 27, "pos": "before", "slug": "empress_sword_deflects_divine_thunder_spears", "sfx_prompt": "Two colossal thunderbolts deflected by an icy steel sword clang followed by a third lightning lance blasting stone", "duration_seconds": 3.6, "gain_db": 2.0, "note": "轰隆！轰隆！姜清凰挥剑挑偏灭神雷枪负伤跪撑"},
            {"p": 41, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "gu_changyuan_frost_coffin_sword_echo", "gain_db": 0.5, "note": "顾长渊清癯剑意震鸣追忆三千年古棺霜寒"},
            {"p": 47, "pos": "before", "slug": "fist_shatters_primordial_god_crown", "sfx_prompt": "Powerful bare fist shattering a crystalline starlight crown into a shimmering cascade of golden sand", "duration_seconds": 3.0, "gain_db": 1.5, "note": "陆烬反手一拳轰碎太初古神冠冕"},
            {"p": 56, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "fifth_genelock_transcendence_snap", "gain_db": 2.0, "note": "咔嚓！第五阶基因锁超脱无漏应声崩开"},
            {"p": 61, "pos": "before", "slug": "ash_gold_pillar_blasts_mother_stele", "sfx_prompt": "Earth-shattering transcendent golden energy pillar erupting skyward, pulverizing lightning and blasting a giant stone monolith away", "duration_seconds": 4.2, "gain_db": 2.5, "note": "轰隆——！无上仙境功成，灰金光柱轰飞万丈天道母碑"},
        ],
    )
    _finalize(s115, md_115, skip_115)

    # =========================================================================
    # E116 · 第116章 第五阶基因锁超脱！重聚原初破母碑！ (56 paras, 14 quotes)
    # =========================================================================
    md_116 = SOURCE_DIR / "第116章_第五阶基因锁超脱！重聚原初破母碑！.md"
    skip_116 = {17, 27, 32, 39, 50}
    s116 = compile_episode_cue_sheet(
        episode_id="E116",
        chapter_number=116,
        source_md_path=md_116,
        source_rel_path=f"02_分章精修正文/{md_116.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_flawless_immortal_blank_in_stele",
                "start_p": 1,
                "title": "第一幕 · 超脱无漏躯，母碑查空白",
                "bgm_prompt": WORLD_OST["f3_celestial_palace_confrontation"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_primordial_corpse_bows_reforge_duanyue",
                "start_p": 27,
                "title": "第二幕 · 仙骸折腰拜，重铸新断岳",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_single_stroke_cleaves_mother_stele",
                "start_p": 46,
                "title": "第三幕 · 撩刀开百丈，一刃碎帝冠",
                "bgm_prompt": WORLD_OST["f4_final_battle_slay_taiyi"],
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(1, 56, "vast_hall")],
        skip_onomatopoeia_paras=skip_116,
        dialogue_specs=[
            {"match": "不可能……这绝不可能！", "role_id": "tai_yi", "tags": "[gasps] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "被震退百丈的太一双手发麻，九纪以来首露惊骇"},
            {"match": "未曾舍弃凡人杂念，未曾觉醒古神神格", "role_id": "tai_yi", "tags": "[dramatically] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "太一难以置信凡人本心竟能生吞大寂灭踏入第五阶"},
            {"match": "休想瞒过天算！即便你侥幸踏入第九境", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一疯狂催动母碑最高权限妄图溯源锁死零号样本"},
            {"match": "别白费力气了，太一。", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "已跳出母碑序列化作超脱空白的陆烬淡然开口"},
            {"match": "清凰，多谢你方才替我拽住人间", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬轻拂姜清凰鬓角染血碎发温和致谢"},
            {"match": "好。三千年等来这一剑开天", "role_id": "jiang_qinghuang", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "伤势尽复的姜清凰展颜一笑退至骨柱之巅压阵"},
            {"match": "母碑只能锁住笼子里的旧血", "role_id": "lu_jin", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬踏空拾级而上宣告旧规再也管不到自己"},
            {"match": "放肆！一具死去九个纪元的残躯也敢造反", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一铁青着脸试图镇压凌霄殿下震颤的无头仙躯"},
            {"match": "前辈安息，剩下的路，晚辈替你守了", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "陆烬左手抚胸向抱拳一拜的始祖无头遗骸肃然还礼"},
            {"match": "看见没有！那是我陆擎苍的儿子", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "南天门外陆擎苍劈翻三尊神卫统领仰天狂笑"},
            {"match": "杀！破仙庭，碎天锁！", "role_id": "male_guard_captain", "speaker_name": "萧烈与破锁联军", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈、石猛与十万破锁联军士气大振席卷外城"},
            {"match": "装神弄鬼！就算重铸了兵器又如何", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一彻底撕下伪装杀意沸腾"},
            {"match": "天碑镇世，给我死！", "role_id": "tai_yi", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一双掌合推万丈天道母碑真身当胸撞向陆烬"},
            {"match": "九个纪元的血肉牧场，今日该彻底清账了", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "一刀劈裂母碑震碎太一帝冠后，陆烬冷冽俯视宣判"},
        ],
        sfx_blueprint=[
            {"p": 17, "pos": "before", "slug": "mother_stele_error_overload_hum", "sfx_prompt": "Rapid frantic crystalline rune pulsing ending in a harsh discordant stone monument overload fracture", "duration_seconds": 3.0, "gain_db": 1.0, "note": "嗡！嗡！嗡！天道母碑检索超脱空白弹出刺目乱码"},
            {"p": 32, "pos": "before", "slug": "ninety_nine_thousand_chains_snap", "sfx_prompt": "Thousands of taut heavy metal chains snapping in rapid succession and marble throne shattering", "duration_seconds": 3.5, "gain_db": 2.0, "note": "嘣！嘣！嘣！九万九千根秩序神链崩断掀翻白玉帝座"},
            {"p": 39, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "transcendent_duanyue_sabre_reforged", "gain_db": 1.5, "note": "嗡——！吞融太初仙躯与零号铭牌，超脱神刀断岳重铸"},
            {"p": 45, "pos": "before", "slug": "allied_legions_charge_war_drums", "sfx_prompt": "Thunderous war drums and thousands of armored boots and steel blades surging forward across a stone plaza", "duration_seconds": 3.2, "gain_db": 1.5, "note": "十万破锁联军汇成钢铁洪流杀穿南天门"},
            {"p": 50, "pos": "before", "slug": "hair_thin_blade_cleaves_mother_stele", "sfx_prompt": "Single razor-clean transcendent metallic sabre ring cleaving deep into a colossal ancient bronze-stone stele", "duration_seconds": 3.6, "gain_db": 2.5, "note": "铛！灰金刀线正面劈开万丈天道母碑百丈豁口"},
        ],
    )
    _finalize(s116, md_116, skip_116)

    # =========================================================================
    # E117 · 第117章 最后一刀斩太一，旧日牧场化飞灰！ (69 paras, 13 quotes)
    # =========================================================================
    md_117 = SOURCE_DIR / "第117章_最后一刀斩太一，旧日牧场化飞灰！.md"
    skip_117 = {12, 47, 64}
    s117 = compile_episode_cue_sheet(
        episode_id="E117",
        chapter_number=117,
        source_md_path=md_117,
        source_rel_path=f"02_分章精修正文/{md_117.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_taiyi_madness_celestial_order_avatar",
                "start_p": 1,
                "title": "第一幕 · 万卫祭魂池，法身绑诸界",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_nine_realms_steps_final_blade_slays_taiyi",
                "start_p": 27,
                "title": "第二幕 · 九境踏血印，一刀剥死锁",
                "bgm_prompt": WORLD_OST["f4_final_battle_slay_taiyi"],
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act3_pasture_to_ash_mother_stele_dilemma",
                "start_p": 52,
                "title": "第三幕 · 牧神化光雨，母碑系苍生",
                "bgm_prompt": WORLD_OST["f3_celestial_palace_confrontation"],
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[(1, 69, "vast_hall")],
        skip_onomatopoeia_paras=skip_117,
        dialogue_specs=[
            {"match": "算错了……一亿三千万次演化，怎么会漏算了这一刀", "role_id": "tai_yi", "tags": "[whispers] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "太一死死盯着母碑百丈刀痕，绝对理智道心崩塌"},
            {"match": "不！天算绝不会错！错的是你们这些本不该脱离控制的变数", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一面浮血纹滑向偏执疯狂极端"},
            {"match": "天道归元，万卫献祭！九纪魂池，尽归吾身", "role_id": "tai_yi", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太一十指插胸献祭数万神卫与九纪魂池化万丈秩序法身"},
            {"match": "陆烬小心！", "role_id": "jiang_qinghuang", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "骨柱之巅姜清凰脸色微变横剑斩出万里冰封剑域"},
            {"match": "太一疯了！他把自己的仙魂核心与母碑连接三千世界", "role_id": "jiang_qinghuang", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰急声示警太一绑架三千世界本源胎膜陪葬"},
            {"match": "看见了么，陆烬！", "role_id": "tai_yi", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "万丈天道秩序法身张开六臂狂吼震动墟海"},
            {"match": "本帝即是秩序，秩序即是诸天", "role_id": "tai_yi", "tags": "[angry] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "太一以拆毁三千羊圈亿万生灵性命要挟陆烬"},
            {"match": "拿始祖造的方舟来要挟我？太一", "role_id": "lu_jin", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬立于毁灭神光下眼睫不颤看穿零厚隙缝"},
            {"match": "你从来就不是诸天的支柱，你只是趴在支柱上吸血的蛀虫", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬收紧断岳刀柄迈出九大修行真境血印步伐"},
            {"match": "这一刀，替始祖清理门户，斩你九纪圈养之罪", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "九境合一五锁全开，陆烬双手举刀对准法身眉心劈落"},
            {"match": "怎么可能……连半座世界都没伤到", "role_id": "tai_yi", "tags": "[gasps] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "三千自爆死锁被精准剥离斩断，太一跌回人形骇然喃喃"},
            {"match": "原来……在我的算式之外，真的有五成之上的路", "role_id": "tai_yi", "tags": "[sighs] [softly]", "stability": 0.0, "space": "vast_hall", "note": "望见三千世界生机勃勃，太一卸下万载执念化光雨消散"},
            {"match": "赢了！太一死了！仙庭灭了！", "role_id": "male_disciple_a", "speaker_name": "破锁联军修士", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "南天门内外十万破锁修士扔掉断刃狂喜痛哭欢呼"},
        ],
        sfx_blueprint=[
            {"p": 12, "pos": "before", "slug": "nine_bronze_blood_pools_erupt", "sfx_prompt": "Nine colossal underground bronze cauldrons bursting open with turbulent dark energy vortexes and deep stone tremor", "duration_seconds": 3.6, "gain_db": 1.5, "note": "轰隆隆！万卫爆碎献祭，地底九座青铜血池炸开"},
            {"p": 20, "pos": "before", "slug": "frost_sword_domain_freezes_chains", "sfx_prompt": "Sweeping glacial sword wind rapidly freezing a hundred rattling iron chains in crystalline ice", "duration_seconds": 3.0, "gain_db": 1.0, "note": "姜清凰斩出万里冰封剑域强行冻住前排世界锁链"},
            {"p": 35, "pos": "before", "slug": "nine_realms_footsteps_converge_suns", "sfx_prompt": "Steady echoing footsteps stepping across cosmic space, each step igniting a deeper resonant golden chime", "duration_seconds": 3.8, "gain_db": 1.5, "note": "陆烬一步一血印踏过九境，九轮大日坍缩归于断岳刀锋"},
            {"p": 47, "pos": "before", "slug": "zero_thickness_final_sabre_cut", "sfx_prompt": "Absolute silence broken by a single ultra-fine metallic silk slice cleanly severing three thousand chains without a tremor", "duration_seconds": 3.2, "gain_db": 2.0, "note": "嗤！零厚隙缝绝巅一刀剥离全部自爆死锁斩穿太一"},
            {"p": 64, "pos": "before", "slug": "ownerless_mother_stele_unstable_tremor", "sfx_prompt": "Colossal ancient stone monolith vibrating ominously with cracking surface runes and creeping abyssal wind", "duration_seconds": 3.4, "gain_db": 1.5, "note": "嗡！嗡！嗡！失去执掌者的万丈天道母碑剧烈震颤"},
        ],
    )
    _finalize(s117, md_117, skip_117)

    # =========================================================================
    # E118 · 第118章 不毁方舟改天碑，死锁重铸通天阶！ (58 paras, 21 quotes)
    # =========================================================================
    md_118 = SOURCE_DIR / "第118章_不毁方舟改天碑，死锁重铸通天阶！.md"
    skip_118 = {13, 24, 27, 32, 41, 46}
    s118 = compile_episode_cue_sheet(
        episode_id="E118",
        chapter_number=118,
        source_md_path=md_118,
        source_rel_path=f"02_分章精修正文/{md_118.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_shatter_jade_throne_no_more_emperor",
                "start_p": 1,
                "title": "第一幕 · 弹指碎帝座，诸天无牧神",
                "bgm_prompt": WORLD_OST["f3_celestial_palace_confrontation"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_recut_mother_stele_five_sky_trials",
                "start_p": 24,
                "title": "第二幕 · 断岳改天宪，死锁化五阶",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act3_lay_down_sky_bridge_walk_hand_in_hand",
                "start_p": 43,
                "title": "第三幕 · 天碑横作桥，携美下人间",
                "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 58, "vast_hall")],
        skip_onomatopoeia_paras=skip_118,
        dialogue_specs=[
            {"match": "请陆仙尊挥刀劈碎这害死万古英杰的恶碑", "role_id": "weathered_elder_npc", "speaker_name": "太虚白发老剑修", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太虚界白发老剑修红着眼眶振臂请毁恶碑"},
            {"match": "使不得！", "role_id": "male_guard_captain", "speaker_name": "北渊军师", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "北渊军师脸色煞白急声劝阻"},
            {"match": "老前辈息怒！您看堤坝外头的大寂灭黑海", "role_id": "male_guard_captain", "speaker_name": "北渊军师", "tags": "[desperately]", "stability": 0.0, "space": "vast_hall", "note": "北渊军师道出毁碑撤去认知胎膜必致亿万凡人惨死"},
            {"match": "天不可一日无主！如今太一伏诛", "role_id": "sect_elder_antagonist", "speaker_name": "诸界老祖", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "诸界老祖躬身请陆烬登临凌霄宝座册封新天庭"},
            {"match": "新天庭", "role_id": "narrator", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "gap_after_s": 0.1, "note": "旁白紧接叙述‘新天庭’三个字一出"},
            {"match": "我提刀杀上三十三重天，不是为了把太一赶下去", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬屈指弹碎白玉帝座后温和传音万里"},
            {"match": "诸天众生头顶，从此不再需要任何一张天帝王座", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "陆烬字字如钟宣告终结天帝制度"},
            {"match": "可若无人执掌母碑，又不毁去母碑", "role_id": "sect_elder_antagonist", "speaker_name": "诸界老祖", "tags": "[trembling]", "stability": 0.0, "space": "vast_hall", "note": "诸界老祖忧心母碑死锁自动反噬"},
            {"match": "谁说不坐王座、不毁船身，便治不了这面旧碑", "role_id": "jiang_qinghuang", "tags": "[calmly] [softly]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰飘落陆烬身侧唇角微扬心意相通"},
            {"match": "还是清凰懂我。", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬转头冲姜清凰温和一笑，轻抚天道母碑"},
            {"match": "刀能害人，亦能护人。错的从来不是始祖当年造来", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬辨明保育方舟与吃人铁锁之别"},
            {"match": "既然船身尚有用处，那今日便不拆船", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬立誓以断岳为刀、真血为墨改天换锁"},
            {"match": "第一刀，斩尽诸界收割恶锁！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬挥刀连根铲除三千世界全部抽髓剥寿恶锁"},
            {"match": "第二刀，留护道胎膜，化死锁为【通天五阶】", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬铭刻超脱真血重写诸天九境与通天五阶试炼锁"},
            {"match": "这还没完。", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬收刀立于高天望向仍需众生仰望的万丈天碑"},
            {"match": "既是给人走的阶梯，就不该立在天上让人跪拜", "role_id": "lu_jin", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬左手按碑顶将万丈天碑放平化作万界通天桥"},
            {"match": "不毁方舟改天碑，碎却帝座铺凡阶", "role_id": "weathered_elder_npc", "speaker_name": "太虚白发老剑修", "tags": "[crying] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "太虚老剑修抚摸桥头温润石阶老泪纵横长揖到底"},
            {"match": "礼敬陆仙尊！礼敬破锁至尊！", "role_id": "male_disciple_a", "speaker_name": "诸界联军将士", "tags": "[shouting] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "十万联军修士齐举兵刃向桥巅欢呼致敬"},
            {"match": "哈哈哈！好小子！比老子当年在北渊想得还要敞亮痛快", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍扛刀大笑第一个踩过帝座残片铺成的白石阶"},
            {"match": "臭小子，天碑改完了，还不快带儿媳妇下来", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍扯着洪钟嗓子喊儿子带儿媳妇回母界喝酒"},
            {"match": "来了！", "role_id": "lu_jin", "tags": "[laughs] [softly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬归刀入鞘牵起耳根微红的姜清凰走下通天长桥"},
        ],
        sfx_blueprint=[
            {"p": 13, "pos": "before", "slug": "finger_flick_shatters_jade_throne", "sfx_prompt": "Crisp finger-flick shockwave blasting a massive white jade throne into scattering ordinary gravel stones", "duration_seconds": 2.8, "gain_db": 1.5, "note": "砰！陆烬屈指一弹震碎九纪白玉天帝宝座"},
            {"p": 27, "pos": "before", "slug": "duanyue_carves_mother_stele_sparks", "sfx_prompt": "Heavy metallic broadsword chiseling rapidly down a colossal bronze-stone monolith with showers of ringing sparks", "duration_seconds": 3.5, "gain_db": 2.0, "note": "铿！铿！铿！断岳疾掠挥刀剔除母碑篡改源码"},
            {"p": 32, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "xujie_star_chart_merges_new_stele", "gain_db": 1.0, "note": "嗡！三千恶锁尽除，方寸墟界共享万界星图航道"},
            {"p": 41, "pos": "before", "slug": "golden_runes_close_warm_resonance", "sfx_prompt": "Warm majestic ancient Chinese temple bell and golden jade resonance spreading peacefully across the cosmos", "duration_seconds": 3.4, "gain_db": 1.0, "note": "嗡——！最后一笔灰金神纹闭合绽放温润金辉"},
            {"p": 46, "pos": "before", "slug": "mother_stele_lays_flat_sky_bridge", "sfx_prompt": "Monumental ancient stone monolith slowly tilting and locking horizontally into a grand golden bridge with cascading white stones", "duration_seconds": 4.2, "gain_db": 2.0, "note": "轰隆隆！万丈天道母碑倾倒放平化作万界通天桥"},
        ],
    )
    _finalize(s118, md_118, skip_118)

    # =========================================================================
    # E119 · 第119章 诸界人间皆新岁，故人把酒话桑麻 (47 paras, 15 quotes)
    # =========================================================================
    md_119 = SOURCE_DIR / "第119章_诸界人间皆新岁，故人把酒话桑麻.md"
    skip_119: set[int] = set()
    s119 = compile_episode_cue_sheet(
        episode_id="E119",
        chapter_number=119,
        source_md_path=md_119,
        source_rel_path=f"02_分章精修正文/{md_119.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_return_beiyuan_tribute_to_fubo",
                "start_p": 1,
                "title": "第一幕 · 归北渊武院，祭老槐福伯",
                "bgm_prompt": WORLD_OST["f2_tomb_guardian_firewood"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_warm_sun_jinzhou_touring_worlds",
                "start_p": 17,
                "title": "第二幕 · 迎日城暖阳，携美游诸界",
                "bgm_prompt": WORLD_OST["f5_epilogue_new_year_horizon"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_buzhou_cliff_father_son_wine",
                "start_p": 27,
                "title": "第三幕 · 不周崖篝火，父子饮烧刀",
                "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_starlit_vow_pulse_beyond_sea",
                "start_p": 33,
                "title": "第四幕 · 余生只认君，海深有远路",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[],
        skip_onomatopoeia_paras=skip_119,
        dialogue_specs=[
            {"match": "腰挺直了！当年你们陆院长十八岁丹田碎了", "role_id": "qin_lie", "speaker_name": "秦烈", "tags": "[laughs] [shouting]", "stability": 0.5, "note": "断岳武院高台上独臂老帅秦烈笑骂督训北渊寒门少年"},
            {"match": "秦老帅放心，等月底测完第一阶", "role_id": "shi_meng", "speaker_name": "石猛", "tags": "[laughs] [shouting]", "stability": 0.5, "note": "石猛抱着两口千斤石锁哈哈大笑应和"},
            {"match": "福伯，天上的锁我已经劈开了", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.0, "note": "西城老槐树下陆烬在福伯坟前浇洒半坛粗酿黄酒"},
            {"match": "以后北渊的孩子再也不用看一品世家的脸色求活", "role_id": "lu_jin", "tags": "[softly] [sighs]", "stability": 0.0, "note": "陆烬轻拂坟头新草向忠仆福伯温柔告慰"},
            {"match": "陆兄，姜姐姐，烬昼今日的太阳，暖得很", "role_id": "female_maid_npc", "speaker_name": "沈烛音", "tags": "[laughs] [softly]", "stability": 0.5, "note": "迎日阁飞檐上红衣沈烛音举起酒葫芦向云端两人遥敬"},
            {"match": "臭小子，巡个界磨磨蹭蹭七天", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "note": "不周崖篝火旁陆擎苍扔来一坛二十年北渊烧刀子"},
            {"match": "爹尽管喝，管够。", "role_id": "lu_jin", "tags": "[laughs] [calmly]", "stability": 0.5, "note": "陆烬笑着单手接坛与父亲痛快碰酒"},
            {"match": "行了，老子明天还要跟萧烈那小子组队", "role_id": "lu_qingcang", "tags": "[laughs] [calmly]", "stability": 0.5, "note": "微醺的陆擎苍大笑着摆手下山把崖巅留给小两口"},
            {"match": "方才在大苍北渊，我看你在老宅门外多停了三息", "role_id": "jiang_qinghuang", "tags": "[softly]", "stability": 0.5, "note": "星河崖边姜清凰侧首温柔凝视陆烬"},
            {"match": "只是忽然觉得很奇妙。", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬握住姜清凰温暖素手轻声感慨"},
            {"match": "十八岁那年秋雨碎丹，我只想着怎么活过三天", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "note": "陆烬回想初见玄霜古棺至今日并肩吹山风"},
            {"match": "三千年前顾长渊留给我的只是一道死结", "role_id": "jiang_qinghuang", "tags": "[softly] [dramatically]", "stability": 0.0, "note": "姜清凰指尖回扣陆烬，笃定是陆烬带她重回人间"},
            {"match": "前尘早已随太一散尽。往后余生，我只认北渊陆烬一人", "role_id": "jiang_qinghuang", "tags": "[softly]", "stability": 0.0, "note": "星光下姜清凰定下余生只认陆烬一人的心意"},
            {"match": "温室里的锁已经斩完了。外头那片海里，莫非还有路", "role_id": "jiang_qinghuang", "tags": "[calmly] [dramatically]", "stability": 0.5, "note": "姜清凰察觉陆烬望向源海深处，眸中亮起昂扬剑意"},
            {"match": "等家里这批幼苗长稳了根基，咱们去会一会", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬手按断岳刀柄定下远征真实大宇宙之约"},
        ],
        sfx_blueprint=[
            {"p": 13, "pos": "before", "slug": "pour_warm_yellow_wine_grave_earth", "sfx_prompt": "Clay wine jar unsealed and warm rice wine pouring gently onto quiet soil with rustling autumn leaves", "duration_seconds": 3.2, "gain_db": 1.0, "note": "老槐树下拔开泥封在福伯墓碑前缓缓浇下黄酒"},
            {"p": 22, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "dawn_sword_intent_enter_scabbard", "gain_db": 1.0, "note": "太初晨曦剑意送入沈烛音剑鞘清鸣"},
            {"p": 31, "pos": "before", "slug": "clay_wine_jars_clink_bonfire_crackle", "sfx_prompt": "Two heavy clay wine jars clinking crisply together beside a warm crackling mountain campfire", "duration_seconds": 2.8, "gain_db": 1.5, "note": "不周崖篝火旁父子二人仰头痛快碰坛"},
            {"p": 42, "pos": "before", "slug": "distant_true_universe_dao_heartbeat", "sfx_prompt": "Faint ancient cosmic pulse echoing across vast misty ocean depths like a distant celestial drumbeat", "duration_seconds": 3.4, "gain_db": 1.0, "note": "源海最深处传来微弱而古老的真实大宇宙搏动"},
        ],
    )
    _finalize(s119, md_119, skip_119)

    # =========================================================================
    # E120 · 第120章 大结局：山高自有行路人，提刀再向真界行！ (57 paras, 19 quotes)
    # =========================================================================
    md_120 = SOURCE_DIR / "第120章_大结局：山高自有行路人，提刀再向真界行！.md"
    skip_120 = {40}
    s120 = compile_episode_cue_sheet(
        episode_id="E120",
        chapter_number=120,
        source_md_path=md_120,
        source_rel_path=f"02_分章精修正文/{md_120.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_beiyuan_autumn_rain_young_wayfarer",
                "start_p": 1,
                "title": "第一幕 · 北渊秋雨澈，旧祠少年行",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_great_wall_friends_father_wine_flask",
                "start_p": 25,
                "title": "第二幕 · 长城故人聚，慈父赠铜壶",
                "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act3_step_beyond_horizon_true_universe",
                "start_p": 46,
                "title": "第三幕 · 诸天无死锁，提刀向真界",
                "bgm_prompt": WORLD_OST["f5_epilogue_new_year_horizon"],
                "bgm_duration_s": 115.0,
            },
        ],
        acoustic_ranges=[(1, 24, "dry"), (25, 57, "vast_hall")],
        skip_onomatopoeia_paras=skip_120,
        dialogue_specs=[
            {"match": "山高自有行路人，锁硬不过掌中刀", "role_id": "male_disciple_a", "speaker_name": "北渊寒门少年", "tags": "[softly] [dramatically]", "stability": 0.0, "space": "dry", "note": "十八岁寒门背刀少年在陆氏旧祠青石碑前轻声念出刻字"},
            {"match": "看够了？", "role_id": "jiang_qinghuang", "tags": "[softly]", "stability": 0.5, "space": "dry", "note": "廊檐下撑素白油纸伞的姜清凰缓步走近柔声询问"},
            {"match": "断岳武院这一届有石猛和秦老帅盯着", "role_id": "jiang_qinghuang", "tags": "[softly] [calmly]", "stability": 0.5, "space": "dry", "note": "姜清凰微笑赞许秋雨中奔向断岳武院的坚韧少年"},
            {"match": "嗯，家里的烟火气旺得很，我彻底放心了", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "dry", "note": "陆烬收伞入袖与姜清凰并肩迈出旧祠踏向源海长城"},
            {"match": "真决定今日就出关远行了？", "role_id": "male_guard_captain", "speaker_name": "萧烈", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "源海长城烽火台上玄黄少帅萧烈按戟送别"},
            {"match": "这三年来我们在长城驻守观测", "role_id": "male_guard_captain", "speaker_name": "萧烈", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "萧烈望向混沌海沟尽头的异域古老道域残骸"},
            {"match": "风浪不大，我背上这把刀岂不是要闲出锈来", "role_id": "lu_jin", "tags": "[laughs] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬洒脱一笑拍了拍萧烈肩膀"},
            {"match": "长城内外的防务总阵我已经用第五阶超脱神纹加固了三遍", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬温和托付季长生执掌长城防务枢机"},
            {"match": "盟主放心！老朽这把骨头如今也沾了通天桥的光踏入合道", "role_id": "weathered_elder_npc", "speaker_name": "季长生", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "季长生手捧阵盘郑重揖手领命"},
            {"match": "陆小子，外头若是遇上什么耍剑厉害的异域古仙", "role_id": "sect_elder_antagonist", "speaker_name": "莫问天", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "太虚疯剑修莫问天灌酒哈哈大笑相约源海论剑"},
            {"match": "待我等推开第五阶基因锁之日，定出关与盟主", "role_id": "female_maid_npc", "speaker_name": "沈烛音与夜琉璃", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "沈烛音与夜琉璃相视一笑抱拳定下重聚之约"},
            {"match": "还有俺！少主放心去闯！", "role_id": "shi_meng", "speaker_name": "石猛", "tags": "[shouting]", "stability": 0.5, "space": "vast_hall", "note": "石猛拍着胸脯瓮声瓮气高喊壮行"},
            {"match": "如今没了血月压头，俺老石也修成紫府之上的金丹元婴大道", "role_id": "shi_meng", "speaker_name": "石猛", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "石猛豪迈承诺带出北渊娃娃后再去外头给少主开路"},
            {"match": "外头不比家里，冷了累了就喝一口热热身子", "role_id": "lu_qingcang", "tags": "[softly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍用力拥抱儿子并将熟铜烧刀子酒壶塞进陆烬怀里"},
            {"match": "尽管放手往高处走！家里这三千座院子的城墙", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍退后半步朗声大笑替儿子守稳三千人间"},
            {"match": "诸位，保重！", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "留下九境超脱刀痕后，陆烬与姜清凰向众故人抱拳道别"},
            {"match": "恭送陆仙尊！恭送姜女帝！", "role_id": "male_disciple_b", "speaker_name": "源海长城众天骄", "tags": "[shouting] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "十万里长城数万天骄同时拔刃齐呼壮行"},
            {"match": "走吧，清凰。", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "回望万家灯火与通天桥后，陆烬向姜清凰伸出左手"},
            {"match": "好，去看看真正的诸天之外，究竟是什么模样", "role_id": "jiang_qinghuang", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰展颜一笑与陆烬十指相扣携手跨出源海长城"},
        ],
        sfx_blueprint=[
            {"p": 7, "pos": "before", "motif_id": "motif_beiyuan_cold_rain", "slug": "beiyuan_clear_autumn_rain_echo", "gain_db": 0.5, "note": "清晨北渊秋雨洗刷青石长街，遥相呼应全书开篇母题"},
            {"p": 14, "pos": "before", "slug": "youth_footsteps_splash_rain_puddles", "sfx_prompt": "Determined young footsteps splashing briskly through rain puddles on a stone street", "duration_seconds": 2.6, "gain_db": 1.0, "note": "十八岁寒门少年踏碎积水奔向断岳武院"},
            {"p": 25, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "step_to_origin_sea_great_wall", "gain_db": 1.0, "note": "星光涟漪轻荡一步跨至源海长城尽头烽火台"},
            {"p": 40, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "finger_carves_nine_realms_blade_mark", "gain_db": 1.5, "note": "嗤！陆烬并指如刀在镇海巨石烙下九境超脱刀痕"},
            {"p": 45, "pos": "before", "slug": "ten_thousand_blades_unsheathe_salute", "sfx_prompt": "Thousands of swords and broadswords unsheathing in unison with a soaring heroic metallic ring across a vast wall", "duration_seconds": 3.8, "gain_db": 2.0, "note": "十万里长城数万天骄同时拔刃出鞘争鸣壮行"},
            {"p": 53, "pos": "before", "slug": "phoenix_sword_duanyue_joyful_chime_mist_parts", "sfx_prompt": "Clear dual resonance of a jade sword and heavy iron broadsword followed by vast ocean mist parting into calm horizon wind", "duration_seconds": 4.2, "gain_db": 1.5, "note": "玄凰帝剑与断岳重刀同时清吟，携手迈向真界星火"},
        ],
    )
    _finalize(s120, md_120, skip_120)

    return built


if __name__ == "__main__":
    results = build_all_batch16()
    for sheet, jp, mp, cov in results:
        sfx_n = sum(1 for c in sheet.cues if c.kind == "sfx")
        dlg_n = sum(1 for c in sheet.cues if c.kind == "dialogue" and c.role_id != "narrator")
        nar_n = sum(1 for c in sheet.cues if c.kind == "dialogue" and c.role_id == "narrator")
        print(
            f"[COMPILED & VALIDATED] {sheet.episode_id} | acts={len(sheet.acts)} | "
            f"cues={len(sheet.cues)} (nar={nar_n}, dlg={dlg_n}, sfx={sfx_n}) | "
            f"cjk_cov={cov:.3%} | {jp.name}",
            flush=True,
        )
