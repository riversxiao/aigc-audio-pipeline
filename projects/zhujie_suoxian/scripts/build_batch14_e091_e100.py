"""Build and validate Batch 14: Episodes E091–E100 (Chapters 91–100 of 《诸界锁仙》)."""

from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_HELPER_DIR = Path(__file__).resolve().parent
for _p in (str(REPO_ROOT / "src"), str(SCRIPTS_HELPER_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from aigc_audio_pipeline.compiler import compile_episode_cue_sheet, save_episode_scripts
from aigc_audio_pipeline.models import EpisodeCueSheet, VoiceCastingRegistry
from world_ost_palette import WORLD_OST

SOURCE_DIR = (
    Path("/tmp/zhujie_source_chapters")
    if Path("/tmp/zhujie_source_chapters").is_dir()
    else Path("/shared/user/.gemini/config/zhujie_suoxian_audio/source_chapters")
)
REGISTRY_PATH = REPO_ROOT / "projects/zhujie_suoxian/00_声音选角档案与进度台账/voice_casting_registry.json"
REPO_SCRIPTS_DIR = REPO_ROOT / "projects/zhujie_suoxian/02_分集广播剧台本"

_TRAILING_QUOTE_PUNCT_RE = re.compile(r"”([！!？?。…]+)(\s*)$", re.MULTILINE)


def _prepare_source_md(src_md: Path, tmp_dir: Path) -> Path:
    """Fold sentence-final punctuation right after a closing quote inside the quote to prevent punctuation-only narrator cues."""
    raw = src_md.read_text(encoding="utf-8")
    fixed = _TRAILING_QUOTE_PUNCT_RE.sub(r"\1”\2", raw)
    if fixed == raw:
        return src_md
    out = tmp_dir / src_md.name
    out.write_text(fixed, encoding="utf-8")
    return out


def build_all_batch14() -> list[tuple[str, EpisodeCueSheet, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, EpisodeCueSheet, Path, Path]] = []
    _tmp_ctx = tempfile.TemporaryDirectory(prefix="zhujie_b14_")
    _tmp_dir = Path(_tmp_ctx.name)

    # =========================================================================
    # E091 · 第91章 三阶锁全开屠百魂，掀翻万魂饲魔渊！ (71 paras, 18 quotes)
    # =========================================================================
    md_91 = SOURCE_DIR / "第91章_三阶锁全开屠百魂，掀翻万魂饲魔渊！.md"
    s91 = compile_episode_cue_sheet(
        episode_id="E091",
        chapter_number=91,
        source_md_path=md_91,
        source_rel_path=f"02_分章精修正文/{md_91.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_immortal_demon_body_crush_arm",
                "start_p": 1,
                "title": "第一幕 · 魔躯硬撼爪，徒手爆凶臂",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_ninety_nine_phantoms_third_lock_deduce",
                "start_p": 19,
                "title": "第二幕 · 百相灭界阵，三阶算破绽",
                "bgm_prompt": WORLD_OST["w6_soul_abyss_dread"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_three_thunder_fire_slashes_slay_baihun",
                "start_p": 39,
                "title": "第三幕 · 雷火三刀落，形神诛百魂",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_devour_origin_half_step_dongxu",
                "start_p": 59,
                "title": "第四幕 · 鲸吞登圆满，提刀向地核",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[
            (1, 27, "vast_hall"),
            (28, 33, "mental_realm"),
            (34, 71, "vast_hall"),
        ],
        skip_onomatopoeia_paras={8, 10, 15, 22, 27, 39, 49, 56, 65},
        dialogue_specs=[
            {"match": "不对劲！退！", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖扑至陆烬头顶三寸骤觉大恐怖急退"},
            {"match": "方才趁我闭关砍得那么痛快", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬立于育胎台探出左掌反扣"},
            {"match": "什么怪物肉身！这不可能", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖骇然发现陆烬衣角未损"},
            {"match": "啊啊啊！我的手", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖右小臂被陆烬徒手捏爆"},
            {"match": "这小畜生吞了原胎里的上古凶魂", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖捂住断腕逃回阵心催动三宗绝阵"},
            {"match": "九十九相灭界大阵，给老夫轰碎他", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖扯碎百鬼袈裟放出九十九尊化神魔相"},
            {"match": "花里胡哨，破绽百出", "role_id": "lu_jin", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "vast_hall", "note": "三阶基因锁百倍算力瞬间看穿满场死角"},
            {"match": "吞了九十九道别人的魂魄", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬一步踏空冷晒拼凑纸老虎"},
            {"match": "狂妄小辈！九十九尊化神齐攻", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖色厉内荏藏身魔相群后催阵"},
            {"match": "老祖莫与他废话，先把他的四肢轰下来", "role_id": "li_cang", "speaker_name": "万傀魔教大长老", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "北侧万傀魔教大长老摇动白骨阵旗"},
            {"match": "北侧阵旗慢了三成息，第一个死的便是你", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬并指虚划宣判死刑"},
            {"match": "不！九位太上长老一刀全没了", "role_id": "zhao_kui", "speaker_name": "魔宗太上长老", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "残存魔宗长老见第一刀腰斩九名化神骇极尖叫"},
            {"match": "藏在第三十三张鬼脸后面拿副魂垫背", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬一眼锁定哭丧老妇面具内的主魂劈下第二刀"},
            {"match": "饶命！陆上仙刀下留人", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖被截断在裂缝出口崩溃讨饶"},
            {"match": "老奴愿交出本命魂血永生为奴", "role_id": "chiyang_laozu", "speaker_name": "百魂老祖", "tags": "[crying] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "百魂老祖凌空跪倒磕头献渊底秘密求生"},
            {"match": "你吃的血食太多，留着脏了我的刀", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬漠然斩落第三记千丈紫金刀光"},
            {"match": "多谢陆道友替魔渊万灵诛此大害", "role_id": "hongxiu_louzhu", "speaker_name": "夜琉璃", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "夜琉璃走出石窟向负刀立空的陆烬深深行礼"},
            {"match": "外面的苍蝇清干净了，接下来", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬晋升半步洞虚锁定地底三千丈养蛊母碑"},
        ],
        sfx_blueprint=[
            {"p": 8, "pos": "before", "slug": "iron_palm_clamp_bone_wrist", "sfx_prompt": "Heavy metallic vise clamp impact catching a razor claw mid-swing followed by a deep subterranean shockwave cracking stone", "duration_seconds": 2.6, "gain_db": 1.5, "note": "咔！轰隆！陆烬徒手攥住百魂老祖右腕震塌血池地面"},
            {"p": 15, "pos": "before", "slug": "crush_forearm_bone_shatter", "sfx_prompt": "Brutal brittle bone crunching and snapping followed by a pressurized burst of mist in a vast stone cavern", "duration_seconds": 2.2, "gain_db": 1.5, "note": "咔嚓噗嗤！徒手捏爆百魂老祖右小臂"},
            {"p": 27, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "third_genelock_mind_fission_open", "gain_db": 1.5, "note": "嗡！泥丸宫内第三阶基因锁神识裂变百倍算力全开"},
            {"p": 49, "pos": "before", "slug": "thunder_fire_broadsword_cleave_wall", "sfx_prompt": "Colossal broadsword wreathed in roaring flame and crackling thunder cleaving through a massive barrier with fiery explosion", "duration_seconds": 3.4, "gain_db": 2.0, "note": "轰隆！千丈紫金雷火魔刀正面劈穿魂墙"},
            {"p": 65, "pos": "before", "slug": "half_step_dongxu_aura_surge", "sfx_prompt": "Deep resonant cosmic energy vortex rushing inward and erupting into a luminous golden shockwave chime", "duration_seconds": 3.2, "gain_db": 1.5, "note": "轰！鲸吞百魂本源一举踏入化神大圆满半步洞虚"},
        ],
    )
    j91, m91 = save_episode_scripts(s91, REPO_SCRIPTS_DIR, registry)
    built.append(("E091", s91, j91, m91))

    # =========================================================================
    # E092 · 第92章 碎养蛊母碑，反向窃听仙庭监天网！ (56 paras, 14 quotes)
    # =========================================================================
    md_92 = SOURCE_DIR / "第92章_碎养蛊母碑，反向窃听仙庭监天网！.md"
    s92 = compile_episode_cue_sheet(
        episode_id="E092",
        chapter_number=92,
        source_md_path=md_92,
        source_rel_path=f"02_分章精修正文/{md_92.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_sever_threads_shatter_gu_monolith",
                "start_p": 1,
                "title": "第一幕 · 逆纹剪魂丝，重刀碎母碑",
                "bgm_prompt": WORLD_OST["w6_soul_abyss_dread"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_shouxin_alliance_six_source_codes",
                "start_p": 21,
                "title": "第二幕 · 孤峰立守心，六码共鸣动",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act3_trojan_wiretap_two_urgent_decrees",
                "start_p": 31,
                "title": "第三幕 · 铜笼截密电，两界起杀劫",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_empress_counsel_three_day_pledge",
                "start_p": 49,
                "title": "第四幕 · 寒棺急传讯，三日定征程",
                "bgm_prompt": WORLD_OST["w4_frost_coffin_empress_awaken"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[
            (1, 20, "vast_hall"),
            (21, 30, "dry"),
            (31, 56, "mental_realm"),
        ],
        skip_onomatopoeia_paras={10, 15, 27, 42},
        dialogue_specs=[
            {"match": "难怪此界修士越是吞魂", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬洞察地核空腔裂魂养蛊母碑的摇瓮机制"},
            {"match": "好歹毒的设计！若是不懂阵理的莽夫", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬看穿碑底拉全界陪葬的仙庭自毁陷阱"},
            {"match": "先断丝，再碎碑", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬凌空刻画三百六十道逆向解锁灵纹"},
            {"match": "现在，给我碎", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬高举断岳斩锁刀劈向百丈母碑"},
            {"match": "陆尊大恩，九幽永世不忘", "role_id": "hongxiu_louzhu", "speaker_name": "夜琉璃", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "dry", "note": "孤峰之巅夜琉璃率守心盟众首领深深稽首"},
            {"match": "路已经替你们劈开了，日后仙庭若来反扑", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬留下固魂正元篇淡然嘱咐"},
            {"match": "《试锁石林》记载，冲击【第四阶基因锁", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬手托六枚世界母锁源码复盘四阶铁律"},
            {"match": "如今六枚源码在手，只要再踏破第七大境", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "dry", "note": "陆烬感应星窍深处松动的第四重基因壁垒"},
            {"match": "让我看看，高高在上的司命仙庭最近都在忙些什么勾当", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬阳神入第六环囚道铜殿破译太一木马魂截获密电"},
            {"match": "陆烬，先去第七界【玄黄母界】", "role_id": "jiang_qinghuang", "tags": "[desperately] [coldly]", "stability": 0.0, "space": "mental_realm", "note": "玄霜古棺内姜清凰三千年来首次带颤音急切传讯"},
            {"match": "巡狩舰队尚在船坞整备，但玄冥老鬼十五日后便要抽干母界", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "姜清凰道破方寸墟界乃玄黄母界半块心脏的渊源"},
            {"match": "只要赶在十五日内杀入玄黄母界", "role_id": "jiang_qinghuang", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "姜清凰指明寻回天心即可拔骨剑真身出棺重归合道"},
            {"match": "届时重修【万界坐标台】远程天门", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "姜清凰许诺半日跨七界联手斩敌北渊城外"},
            {"match": "好！给我三天时间闭关破入【洞虚境】", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "陆烬当场拍板先破洞虚铸五阶刀再杀入玄黄母界"},
        ],
        sfx_blueprint=[
            {"p": 10, "pos": "before", "slug": "golden_ring_sever_soul_threads", "sfx_prompt": "Crisp metallic scissor-like energy ring snapping millions of taut ethereal wires simultaneously in a deep magma cavern", "duration_seconds": 2.6, "gain_db": 1.5, "note": "嗤啦！暗金剪刀光环从根部剪断全界无形养蛊锁线"},
            {"p": 15, "pos": "before", "slug": "cleave_hundred_foot_gu_monolith", "sfx_prompt": "Heaven-splitting heavy broadsword strike cleaving a colossal black stone monolith from top to bottom into exploding rubble", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆隆！断岳一刀劈碎百丈裂魂养蛊母碑"},
            {"p": 27, "pos": "before", "slug": "six_world_source_codes_resonance", "sfx_prompt": "Six luminous crystalline cores orbiting and chiming in deep harmonic resonance with subtle celestial hum", "duration_seconds": 3.0, "gain_db": 1.0, "note": "嗡嗡嗡！六枚世界母锁源码环绕阳神交相辉映"},
            {"p": 42, "pos": "before", "slug": "killing_intent_crack_void", "sfx_prompt": "Sudden sub-bass pressure boom cracking spatial glass around an ancient bronze hall", "duration_seconds": 2.4, "gain_db": 1.5, "note": "轰！见大苍故乡将被抹平，陆烬滔天杀意震裂虚空"},
            {"p": 49, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "frost_coffin_urgent_sword_hum", "gain_db": 1.5, "note": "第一环玄霜古棺剧震透出凛冽剑芒传讯"},
        ],
    )
    j92, m92 = save_episode_scripts(s92, REPO_SCRIPTS_DIR, registry)
    built.append(("E092", s92, j92, m92))

    # =========================================================================
    # E093 · 第93章 横渡第七界前夕，洞彻虚空铸五阶神刀 (61 paras, 10 quotes)
    # =========================================================================
    md_93 = SOURCE_DIR / "第93章_横渡第七界前夕，洞彻虚空铸五阶神刀.md"
    s93 = compile_episode_cue_sheet(
        episode_id="E093",
        chapter_number=93,
        source_md_path=_prepare_source_md(md_93, _tmp_dir),
        source_rel_path=f"02_分章精修正文/{md_93.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_pierce_void_membrane_step_dongxu",
                "start_p": 1,
                "title": "第一幕 · 墟界化真舟，一指破妄膜",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_sacred_river_forge_tier5_sabre",
                "start_p": 25,
                "title": "第二幕 · 神河熔古铜，双拳锻五阶",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_star_platform_beam_cross_seventh_world",
                "start_p": 43,
                "title": "第三幕 · 坐标贯星海，仗刀赴玄黄",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act4_shattered_mother_world_cursed_statue",
                "start_p": 53,
                "title": "第四幕 · 破碎旧皇都，十万唾忠魂",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[
            (1, 28, "dry"),
            (29, 51, "mental_realm"),
            (52, 61, "vast_hall"),
        ],
        skip_onomatopoeia_paras={12, 17, 30, 32, 36, 39, 50},
        dialogue_specs=[
            {"match": "化神修阳神共鸣，借的终究是一界之内的表层灵气法则", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬闭关参透太上洞虚真解与六界源码"},
            {"match": "别人苦求半生而不得的洞天真种，一直就在我的眉心里", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "dry", "note": "陆烬以方寸墟界为舟冲击洞虚"},
            {"match": "看清了，给我破", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "dry", "note": "百丈阳神并指戳穿银灰真妄胎膜"},
            {"match": "这便是洞虚神通，缩地折叠", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬晋升洞虚初期随手折叠三尺空间"},
            {"match": "老伙计，跟了我这么久", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "dry", "note": "陆烬轻抚断岳重刀拔起十万斤太初九幽神铜"},
            {"match": "那便是三千年前统御百界", "role_id": "jiang_qinghuang", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "玄霜古棺开启一线姜清凰遥指星盘赤金主星"},
            {"match": "罪血", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬听闻太上罪血遗墟之名眼神微冷"},
            {"match": "该背罪名的是强盗，从来不是守家的人", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "mental_realm", "note": "陆烬将五阶断岳刀插入万界坐标台拧动启程"},
            {"match": "千古灭界叛徒·顾长渊", "role_id": "ancient_construct_echo", "speaker_name": "石像底座红漆铭文", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "皇都广场三十丈铁链跪像底座刺目血字"},
            {"match": "呸！顾长渊你这不得好死的畜生", "role_id": "male_disciple_a", "speaker_name": "玄黄遗民修士", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "被洗脑的母界遗民抓起烂泥碎石唾骂顾长渊石像"},
        ],
        sfx_blueprint=[
            {"p": 12, "pos": "before", "slug": "spatial_fabric_stretch_hum", "sfx_prompt": "Deep spatial distortion drone with taut metallic threads stretching across a silent underground chamber", "duration_seconds": 2.4, "gain_db": 1.0, "note": "嗡！阳神重叠九环壁垒引发空间撕扯"},
            {"p": 17, "pos": "before", "slug": "void_membrane_pop_inrush", "sfx_prompt": "Crisp resonant cosmic bubble pop followed by a majestic rushing torrent of ethereal starlight energy and deep heartbeat pulse", "duration_seconds": 3.4, "gain_db": 1.5, "note": "啵！戳穿真妄胎膜高维太虚精气倒灌入体晋升洞虚"},
            {"p": 32, "pos": "before", "slug": "fist_hammer_divine_bronze_sabre", "sfx_prompt": "Rhythmic thunderous metallic forging impacts compressing molten metal with spatial shockwaves over a rushing river", "duration_seconds": 3.5, "gain_db": 2.0, "note": "铛铛铛！双拳折叠空间千锤百炼十万斤太初神铜"},
            {"p": 39, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "tier5_duanyue_slice_void_rift", "gain_db": 1.5, "note": "嗤啦！五阶断岳斩锁刀随手切开百丈平滑虚空裂缝"},
            {"p": 50, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "coordinate_platform_star_beam", "gain_db": 1.5, "note": "轰隆！万界坐标台冲起银白跨界光柱贯通第七界"},
        ],
    )
    j93, m93 = save_episode_scripts(s93, REPO_SCRIPTS_DIR, registry)
    built.append(("E093", s93, j93, m93))

    # =========================================================================
    # E094 · 第94章 第七认知世界：罪血天刑锁，跪着骂恩人的遗民！ (70 paras, 19 quotes)
    # =========================================================================
    md_94 = SOURCE_DIR / "第94章_第七认知世界：罪血天刑锁，跪着骂恩人的遗民！.md"
    s94 = compile_episode_cue_sheet(
        episode_id="E094",
        chapter_number=94,
        source_md_path=md_94,
        source_rel_path=f"02_分章精修正文/{md_94.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_sin_blood_slave_brand_kneeling_crowd",
                "start_p": 1,
                "title": "第一幕 · 天恩催奴印，十万折脊梁",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_xiao_lie_unbending_spear_lu_jin_steps_out",
                "start_p": 22,
                "title": "第二幕 · 断枪撑血骨，孤身踏法场",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_one_finger_execute_imperial_preceptor",
                "start_p": 44,
                "title": "第三幕 · 弹指碎仙印，一击毙双狗",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act4_stones_at_savior_xuanming_descends",
                "start_p": 59,
                "title": "第四幕 · 愚民掷血石，冰渊降玄冥",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[
            (1, 2, "vast_hall"),
            (3, 5, "mental_realm"),
            (6, 70, "vast_hall"),
        ],
        skip_onomatopoeia_paras={9, 31, 33, 39, 44, 50, 52, 68},
        dialogue_specs=[
            {"match": "好一个司命仙庭……好毒的诛心之计", "role_id": "jiang_qinghuang", "tags": "[coldly] [trembling]", "stability": 0.0, "space": "mental_realm", "note": "棺内姜清凰见故国后人跪骂顾长渊悲怒彻骨"},
            {"match": "时辰已到，见仙庭天恩令", "role_id": "li_cang", "speaker_name": "天刑国师", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "高台洞虚初期天刑国师亮出仙庭白玉令符"},
            {"match": "啊", "role_id": "male_disciple_b", "speaker_name": "玄黄遗民", "tags": "[gasps] [crying]", "stability": 0.0, "space": "vast_hall", "note": "十万遗民眉心罪字奴印引爆膝骨剧痛趴伏在地"},
            {"match": "这便是第七道世界认知基因锁", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "虚空夹层内陆烬认出罪血天刑锁"},
            {"match": "仙庭在所有玄黄母界遗民的血脉基因里", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬拆解代代遗传天刑奴印的运转原理"},
            {"match": "罪民叩谢仙庭上使慈悲", "role_id": "weathered_elder_npc", "speaker_name": "白发老族长", "tags": "[crying] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "前排被洗脑的白发老族长拼命磕头求处决萧烈"},
            {"match": "请国师大人速斩逆贼萧烈", "role_id": "male_disciple_a", "speaker_name": "玄黄顺民", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "广场被驯化的遗民齐声高呼请杀萧烈"},
            {"match": "住口！你们全都给我住口", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[hoarsely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "双膝碎裂拄断枪死撑不跪的少将军萧烈怒吼"},
            {"match": "睁开你们的眼睛看看头顶破碎的天", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈泣血揭穿仙庭抽脉灭界的真面目"},
            {"match": "玄黄儿郎生来顶天立地", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈宁站着碎骨死绝不跪骂先贤"},
            {"match": "冥顽不灵的太上余孽，死到临头还敢妖言惑众", "role_id": "li_cang", "speaker_name": "天刑国师", "tags": "[coldly] [angry]", "stability": 0.0, "space": "vast_hall", "note": "天刑国师冷笑逼近欲按断萧烈脊梁骨"},
            {"match": "爹……孩儿无能，护不住镇狱军的军旗了", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[crying] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "萧烈膝盖距地两寸滑落血泪欲自爆阳神"},
            {"match": "玄黄还有一个人肯站着说话，这面旗便不算倒", "role_id": "lu_jin", "tags": "[calmly] [softly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬踏出虚空单手托直萧烈染血脊梁"},
            {"match": "什么人敢闯太上遗墟劫法场", "role_id": "li_cang", "speaker_name": "天刑国师", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "天刑国师骇然祭出四阶极品天刑碎虚印"},
            {"match": "国师大人快撕碎这狂徒，拿他的头颅祭旗", "role_id": "snobbish_steward_npc", "speaker_name": "伪朝皇帝", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "高台金椅上的伪朝皇帝狞笑尖叫"},
            {"match": "前……前辈神威", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[gasps] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "见陆烬一指弹杀洞虚国师与伪皇，萧烈震撼失声"},
            {"match": "是葬仙残界的气息！跟史书上记载的一模一样", "role_id": "male_disciple_a", "speaker_name": "玄黄遗民甲", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "石像共鸣触发被洗脑遗民的极度惊恐"},
            {"match": "他是千古灭界叛徒顾长渊的转世余孽", "role_id": "male_disciple_b", "speaker_name": "玄黄遗民乙", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "十万遗民歇斯底里抓起血泥碎石砸向救命恩人陆烬"},
            {"match": "好胆！竟敢在本尊眼皮子底下杀本尊立的看门狗", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "九天撕开玄冥冰渊，洞虚大圆满玄冥尊携三仙将降临"},
        ],
        sfx_blueprint=[
            {"p": 3, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "frost_coffin_tremble_grief", "gain_db": 1.0, "note": "玄霜古棺剧烈颤抖寒霜蔓延十丈"},
            {"p": 9, "pos": "before", "slug": "jade_decree_wave_mass_kneel_thud", "sfx_prompt": "Piercing silver rune chime sweeping across an open stone plaza followed by a massive synchronized thud onto stone slabs", "duration_seconds": 3.2, "gain_db": 1.5, "note": "嗡！天恩令波纹扫过，十万遗民噗通趴伏青石板"},
            {"p": 33, "pos": "before", "slug": "iron_spear_bend_crack_pressure", "sfx_prompt": "Crushing gravitational sub-bass hum bending and cracking a thick iron spear shaft on black stone", "duration_seconds": 2.6, "gain_db": 1.5, "note": "咔嚓咔嚓！洞虚威压下萧烈断枪寸寸弯曲崩折"},
            {"p": 50, "pos": "before", "slug": "golden_finger_blade_shatter_seal", "sfx_prompt": "Crisp metallic finger flick launching a razor-sharp sonic blade that shatters a heavy bronze seal into fragments", "duration_seconds": 3.0, "gain_db": 2.0, "note": "铮！噗嗤轰隆！陆烬弹指粉碎天刑碎虚印瞬杀国师"},
            {"p": 68, "pos": "before", "slug": "nine_heavens_glacial_abyss_rift", "sfx_prompt": "Sky-shattering glacial thunder tearing open a colossal dark rift across the clouds with overwhelming deep pressure", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆隆！九天天幕裂开千丈玄冥冰渊"},
        ],
    )
    j94, m94 = save_episode_scripts(s94, REPO_SCRIPTS_DIR, registry)
    built.append(("E094", s94, j94, m94))

    # =========================================================================
    # E095 · 第95章 第四阶基因锁开！徒手剥奴印，言出法随惊玄黄！ (79 paras, 19 quotes)
    # =========================================================================
    md_95 = SOURCE_DIR / "第95章_第四阶基因锁开！徒手剥奴印，言出法随惊玄黄！.md"
    s95 = compile_episode_cue_sheet(
        episode_id="E095",
        chapter_number=95,
        source_md_path=md_95,
        source_rel_path=f"02_分章精修正文/{md_95.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_death_decree_hundred_thousand_throats",
                "start_p": 1,
                "title": "第一幕 · 权杖降死令，十万逼自戕",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_fourth_genelock_word_as_law_halt",
                "start_p": 21,
                "title": "第二幕 · 四阶基因开，一言喝天止",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_one_slash_slay_three_dongxu_generals",
                "start_p": 44,
                "title": "第三幕 · 紫金横一刀，瞬秒三仙将",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act4_rip_slave_brands_stand_tall_xuanhuang",
                "start_p": 55,
                "title": "第四幕 · 徒手拔奴链，十万挺脊梁",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[(1, 79, "vast_hall")],
        skip_onomatopoeia_paras={6, 23, 26, 29, 32, 39, 47, 49, 60, 66, 76},
        dialogue_specs=[
            {"match": "三千年前，顾长渊那个蠢货为了护住这群不知感恩的猪羊", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[coldly] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊高踞冰渊俯视陆烬残忍讥诮"},
            {"match": "天刑死令，全城罪奴，自绝谢罪", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊顿动白骨权杖下达全城自绝死令"},
            {"match": "不！怎么会这样！上使大人饶命啊", "role_id": "weathered_elder_npc", "speaker_name": "白发老族长", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "白发老族长右手不受控制割破颈皮绝望哭求"},
            {"match": "卑鄙无耻的老狗！你有种冲我萧烈一个人来", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "高台萧烈目眦欲裂怒骂玄冥尊"},
            {"match": "贪狼、破军、七杀，取他首级", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊趁乱命三尊洞虚中期神将合围绝杀"},
            {"match": "谨遵古尊法旨！下界蝼蚁，还不束手就擒", "role_id": "male_guard_captain", "speaker_name": "贪狼仙将", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三尊银甲仙将结三才戮仙战阵暴起刺来"},
            {"match": "拿十万活人性命当锁链来捆我的刀", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "绝境怒火引爆六界源码冲击第四阶基因锁"},
            {"match": "刺中了！不过如此", "role_id": "male_guard_captain", "speaker_name": "贪狼仙将", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "贪狼仙将仙戈擦破陆烬左肩旋即骇见滴血重生"},
            {"match": "止", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "四阶基因锁言出法随一言喝停十万自刎兵刃"},
            {"match": "什么！一言喝停世界母锁", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊骇然失态握紧白骨权杖"},
            {"match": "莫管那群贱奴，结阵先绞碎他的泥丸", "role_id": "li_cang", "speaker_name": "破军仙将", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三尊洞虚仙将魂飞魄散拼命催动破虚仙戈"},
            {"match": "现在想起来拼命，晚了", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬拔出五阶断岳斩锁刀横掠虚空"},
            {"match": "一刀斩三尊洞虚仙将……我玄黄母界", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[trembling] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "萧烈震撼仰望当空晋升洞虚中期的陆烬"},
            {"match": "三千年前，顾长渊与太上女帝宁死不降", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "陆烬持刀立于高台前端俯视十万遗民"},
            {"match": "跪了三千年，也该跪够了", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬施展四阶基因锁隔空连根抓扯十万天刑奴印"},
            {"match": "给我碎", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬左掌合拢一把握爆十丈赤黑奴印光球"},
            {"match": "没了……钉了咱们祖孙百代的奴印真没了", "role_id": "weathered_elder_npc", "speaker_name": "白发老族长", "tags": "[crying] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "白发老族长抚摸光洁眉心悔恨痛哭站起脊梁"},
            {"match": "徒手剥离母锁源码……第四阶基因锁", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊彻底暴怒显化万丈法相真身扑落"},
            {"match": "想留我的命？下来试试你的脖子够不够硬", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬一振五阶断岳刀正面拔刀冲天迎战玄冥尊"},
        ],
        sfx_blueprint=[
            {"p": 6, "pos": "before", "slug": "bone_staff_death_decree_pulse", "sfx_prompt": "Hollow bone staff striking empty air followed by a sinister dark magnetic ripple and thousands of steel blades unsheathing", "duration_seconds": 3.0, "gain_db": 1.5, "note": "嗡！白骨权杖降下母锁死令，十万人拔刃架颈"},
            {"p": 26, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "fourth_genelock_law_micro_awaken", "gain_db": 2.0, "note": "轰咔嚓！第四阶基因锁法则入微于绝境悍然洞开"},
            {"p": 39, "pos": "before", "slug": "word_as_law_amber_freeze_ripple", "sfx_prompt": "Deep golden resonant law wave sweeping ten miles and instantly freezing thousands of metallic blades into crystal stillness", "duration_seconds": 3.2, "gain_db": 2.0, "note": "轰隆！一言喝止，百里规则改写定格十万刀剑"},
            {"p": 47, "pos": "before", "slug": "sabre_unsheathe_snap_three_halberds", "sfx_prompt": "Heavy dark iron broadsword unsheathing ring followed immediately by three metallic halberd shafts snapping cleanly in mid-air", "duration_seconds": 2.8, "gain_db": 2.0, "note": "铮！嗤啦咔嚓！一刀斩断三杆破虚仙戈瞬秒三仙将"},
            {"p": 60, "pos": "before", "slug": "rip_hundred_thousand_slave_chains", "sfx_prompt": "Dense eerie rustling and snapping of countless dark metallic chains being pulled out of thin air simultaneously", "duration_seconds": 3.0, "gain_db": 1.5, "note": "嗤嗤嗤！隔空将十万条罪血天刑奴印连根抽出"},
            {"p": 66, "pos": "before", "slug": "crush_slave_brand_orb_explosion", "sfx_prompt": "Colossal thunderous implosion shattering a dense dark energy sphere into harmless dissipating wind", "duration_seconds": 2.8, "gain_db": 2.0, "note": "砰！徒手捏爆三千年十万天刑奴印"},
        ],
    )
    j95, m95 = save_episode_scripts(s95, REPO_SCRIPTS_DIR, registry)
    built.append(("E095", s95, j95, m95))

    # =========================================================================
    # E096 · 第96章 洞虚死战玄冥尊，当众揭开万古暗门铁证！ (61 paras, 23 quotes)
    # =========================================================================
    md_96 = SOURCE_DIR / "第96章_洞虚死战玄冥尊，当众揭开万古暗门铁证！.md"
    s96 = compile_episode_cue_sheet(
        episode_id="E096",
        chapter_number=96,
        source_md_path=md_96,
        source_rel_path=f"02_分章精修正文/{md_96.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_cleave_black_water_seal_challenge_sky",
                "start_p": 1,
                "title": "第一幕 · 逆斩黑水印，邀战入天心",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act2_thirty_seven_clashes_breach_secret_vault",
                "start_p": 17,
                "title": "第二幕 · 碎骨算破绽，卖血闯密库",
                "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_sky_projection_three_millennia_truth",
                "start_p": 35,
                "title": "第三幕 · 天幕映留影，三千奇冤白",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act4_lie_shattered_hedao_thunder_palm",
                "start_p": 57,
                "title": "第四幕 · 谎崩老狗狂，捏符招雷掌",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 80.0,
            },
        ],
        acoustic_ranges=[
            (1, 39, "vast_hall"),
            (40, 40, "mental_realm"),
            (41, 61, "vast_hall"),
        ],
        skip_onomatopoeia_paras={11, 19, 30, 35, 43, 60},
        dialogue_specs=[
            {"match": "好一个不知死活的下界孽障", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[coldly] [angry]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊高踞云涡倾泻洞虚大圆满威压"},
            {"match": "竟敢当着本尊的面毁去三尊洞虚仙将", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊按落万丈黑水巨印欲灭十万遗民"},
            {"match": "萧将军，带众人退开百里", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬立于最前沿双手握刀踏碎虚空"},
            {"match": "破", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "千丈紫金雷火刀罡逆斩万丈黑水巨印"},
            {"match": "堂堂仙庭镇界古尊，只会拿化神与凡俗遗民撒气么", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬偏转九成余波引玄冥尊入九天天心遗迹"},
            {"match": "狂妄小辈，区区洞虚中期也敢邀战本尊", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊化作玄黑流光紧追入九天"},
            {"match": "所有人听令，结太上守御阵退至外城高台", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈握紧战枪率众结阵后撤"},
            {"match": "不过如此", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[coldly] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "玄冥镇界碑震断陆烬琵琶骨后玄冥尊逼近冷笑"},
            {"match": "肉身再强，终究只是太虚境蝼蚁", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[coldly]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊环绕九条黑水苍龙居高临下"},
            {"match": "打了三十七招，你有九成神念都死死锁在左后方", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬骨骼瞬息归位道破玄冥尊护殿破绽"},
            {"match": "若我没猜错，那里便是你镇守了三千年的", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬目光锁定天心裂缝深处的仙庭监天密库"},
            {"match": "你竟敢窥探仙庭重地！给本尊死来", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊杀机暴涨催镇界碑直轰陆烬眉心"},
            {"match": "不好，尔敢", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬故意卖右肋空门借反震瞬移至密库门前"},
            {"match": "给我开", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬浑身浴血倾尽全力一刀劈碎密库青铜巨门"},
            {"match": "原来一万年前，太一便已在太上皇室的传承里埋好了屠刀", "role_id": "jiang_qinghuang", "tags": "[trembling] [coldly]", "stability": 0.0, "space": "mental_realm", "note": "棺内姜清凰见万法母锁原石暗门源码指尖掐入掌心"},
            {"match": "顾长渊替这方天地背了三千年的黑锅", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬抓起原石与留影玉璧直冲九霄"},
            {"match": "散", "role_id": "lu_jin", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬一掌将万古暗门铁证与留影铺满万里天幕"},
            {"match": "玄黄母界气运已熟，待太上女帝姜清凰修成", "role_id": "ancient_construct_echo", "speaker_name": "仙庭母石批注", "tags": "[coldly]", "stability": 1.0, "space": "memory_echo", "note": "万法母锁原石上仙庭上使留下的冰冷灭界批注"},
            {"match": "大司命！末将萧氏不孝，我玄黄子孙眼瞎了三千年啊", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "看清顾长渊剖心护界真相，萧烈双膝砸碎青石痛哭失声"},
            {"match": "大司命！", "role_id": "male_disciple_b", "speaker_name": "玄黄年轻修士", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "外城年轻遗民仰望天幕撕心裂肺哭喊"},
            {"match": "是我们骂错了恩人，是我们拿石头砸了救命的大司命啊", "role_id": "weathered_elder_npc", "speaker_name": "白发老族长", "tags": "[crying] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "亿万遗民面向苍穹叩首泣血三千年奇冤昭雪"},
            {"match": "闭嘴！统统给本尊闭嘴", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "罪血谎言彻底崩塌，玄冥尊双目赤红疯魔咆哮"},
            {"match": "知道了真相又如何？一群待宰的猪羊", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊喷血捏碎仙庭最高底牌合道半仙符诏"},
        ],
        sfx_blueprint=[
            {"p": 11, "pos": "before", "slug": "thunder_blade_clash_black_water_seal", "sfx_prompt": "Colossal lightning broadsword beam colliding head-on with a massive dark tidal monolith in the upper atmosphere", "duration_seconds": 3.4, "gain_db": 2.0, "note": "轰隆！千丈紫金刀罡硬撼万丈黑水巨印"},
            {"p": 19, "pos": "before", "slug": "thirty_seven_void_shattering_clashes", "sfx_prompt": "Rapid ferocious heavy steel-on-stone weapon clashes shattering floating boulders in turbulent high-altitude wind", "duration_seconds": 3.2, "gain_db": 2.0, "note": "铛铛铛！断裂天心遗迹内三十七招正面硬拼"},
            {"p": 35, "pos": "before", "slug": "shatter_nine_chains_and_bronze_vault", "sfx_prompt": "Heaven-splitting flame broadsword strike snapping nine heavy iron chains and blasting massive bronze vault doors into fragments", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰！一刀劈断九重禁制神链炸开仙庭监天密库大门"},
            {"p": 43, "pos": "before", "slug": "sky_jade_projection_unfurl", "sfx_prompt": "Luminous crystalline jade projection unfurling across ten thousand miles of sky with a solemn ancient chime", "duration_seconds": 3.0, "gain_db": 1.5, "note": "嗡！监天留影光幕铺满整座玄黄界苍穹"},
            {"p": 60, "pos": "before", "slug": "crush_talisman_hedao_thunder_palm", "sfx_prompt": "Crisp jade talisman shattering followed immediately by apocalyptic white-gold thunderclouds ripping open the heavens", "duration_seconds": 4.0, "gain_db": 2.5, "note": "轰隆！捏碎半仙符诏，万丈合道灭界雷掌探出云涡"},
        ],
    )
    j96, m96 = save_episode_scripts(s96, REPO_SCRIPTS_DIR, registry)
    built.append(("E096", s96, j96, m96))

    # =========================================================================
    # E097 · 第97章 墟界融母界，拔剑补帝心！ (58 paras, 16 quotes)
    # =========================================================================
    md_97 = SOURCE_DIR / "第97章_墟界融母界，拔剑补帝心！.md"
    s97 = compile_episode_cue_sheet(
        episode_id="E097",
        chapter_number=97,
        source_md_path=md_97,
        source_rel_path=f"02_分章精修正文/{md_97.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_hedao_palm_falls_sheathe_sabre_open_mind",
                "start_p": 1,
                "title": "第一幕 · 合道雷掌压，收刀敞识海",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act2_nine_rings_fuse_mother_world_peak_dongxu",
                "start_p": 12,
                "title": "第二幕 · 九环融母界，一步登归墟",
                "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_pull_cursed_sword_golden_blood_heal_heart",
                "start_p": 32,
                "title": "第三幕 · 徒手拔死咒，金血补帝心",
                "bgm_prompt": WORLD_OST["w4_frost_coffin_empress_awaken"],
                "bgm_duration_s": 115.0,
            },
        ],
        acoustic_ranges=[
            (1, 31, "vast_hall"),
            (32, 58, "mental_realm"),
        ],
        skip_onomatopoeia_paras={12, 19, 24, 45, 52, 55},
        dialogue_specs=[
            {"match": "哈哈哈哈！死吧，统统给本尊化作劫灰", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊面色惨白癫狂大笑"},
            {"match": "此乃仙庭东华仙君亲手封存的一击合道神罚", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊断定无人能挡下合道灭界雷掌"},
            {"match": "谁告诉你，我要挡了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬反手收刀归鞘平静抬头"},
            {"match": "三千年前，顾长渊从这里带走了一抔带血的故土", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬结开界法印彻底敞开眉心识海"},
            {"match": "怎么可能！你竟敢把本命识海世界直接撞向破碎母界地脉", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊狂笑僵住失声惊吼"},
            {"match": "融", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬重踏虚空令九环方寸墟界与玄黄天心残骸嵌合归一"},
            {"match": "母界天心既已归位，仙庭监天镜的隔界抹杀便再压不住你的本源", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "洞虚大圆满陆烬迈入第一环停在玄霜古棺边"},
            {"match": "当年在太虚界推开这口棺材时我答应过你", "role_id": "lu_jin", "tags": "[calmly] [softly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬兑现替顾长渊补齐半颗帝心的承诺"},
            {"match": "那半截骨剑连着太一亲手编织的合道级死咒", "role_id": "jiang_qinghuang", "tags": "[coldly] [trembling]", "stability": 0.0, "space": "mental_realm", "note": "棺内姜清凰罕见紧绷提醒合道死咒反噬凶险"},
            {"match": "仙庭的锁，我拆得多了，不差这一把", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬嘴角微扬从容以对"},
            {"match": "况且外头那只合道雷掌替咱们省了开棺的动静", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "mental_realm", "note": "陆烬借外界合道雷掌掩护当机立断拔剑"},
            {"match": "好。若死咒失控，你不必管我", "role_id": "jiang_qinghuang", "tags": "[softly] [coldly]", "stability": 0.5, "space": "mental_realm", "note": "姜清凰闭眸散去胸口最后一层玄凰寒气"},
            {"match": "我陆烬出手，从无退走二字", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.5, "space": "mental_realm", "note": "陆烬开启四阶基因锁一把握住苍白断骨剑"},
            {"match": "陆烬，快松手，它在吞你的元神生机", "role_id": "jiang_qinghuang", "tags": "[desperately] [gasps]", "stability": 0.0, "space": "mental_realm", "note": "见死咒噬裂陆烬右臂皮肉，姜清凰急切欲扣他手腕"},
            {"match": "别动，稳住你的帝心", "role_id": "lu_jin", "tags": "[hoarsely] [fiercely]", "stability": 0.0, "space": "mental_realm", "note": "陆烬碾碎黑咒并指划开心口逼出无漏原胎金血"},
            {"match": "困了三千年够久了，给我滚出来", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "mental_realm", "note": "陆烬悍然连根拔出死咒断骨剑捏爆并送入金血补全帝心"},
        ],
        sfx_blueprint=[
            {"p": 12, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "nine_ring_xujie_manifest_sky", "gain_db": 1.5, "note": "轰！万里九环方寸墟界自陆烬眉心毫无保留降临天地"},
            {"p": 19, "pos": "before", "slug": "two_worlds_fusion_river_thaw", "sfx_prompt": "Monumental tectonic locking resonance followed by cracking ancient ice and a mighty subterranean river surging to life", "duration_seconds": 4.0, "gain_db": 2.0, "note": "轰隆！九环墟界与玄黄天心嵌合归一，断血神河解冻奔流"},
            {"p": 24, "pos": "before", "slug": "golden_world_dome_block_thunder_palm", "sfx_prompt": "Colossal bronze-bell-like barrier impact absorbing a heaven-shaking lightning strike with crackling sparks", "duration_seconds": 3.4, "gain_db": 2.0, "note": "咚！新生方寸玄黄界金色天幕硬扛合道灭界雷掌"},
            {"p": 45, "pos": "before", "slug": "grab_cursed_bone_sword_sizzle", "sfx_prompt": "Piercing icy bone-blade grip followed by searing dark corrosive energy sizzling against metallic golden armour", "duration_seconds": 2.6, "gain_db": 1.5, "note": "嗤啦！徒手握住死咒断骨剑，黑咒疯狂噬咬右臂"},
            {"p": 58, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "frost_coffin_shatter_empress_step", "gain_db": 2.0, "note": "咔嚓轰！玄霜古棺寸寸炸裂化作冰花，玄凰女帝真身踏出"},
        ],
    )
    j97, m97 = save_episode_scripts(s97, REPO_SCRIPTS_DIR, registry)
    built.append(("E097", s97, j97, m97))

    # =========================================================================
    # E098 · 第98章 玄凰女帝真身出棺，双强并肩斩古尊！ (63 paras, 20 quotes)
    # =========================================================================
    md_98 = SOURCE_DIR / "第98章_玄凰女帝真身出棺，双强并肩斩古尊！.md"
    s98 = compile_episode_cue_sheet(
        episode_id="E098",
        chapter_number=98,
        source_md_path=md_98,
        source_rel_path=f"02_分章精修正文/{md_98.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_empress_steps_from_coffin_hedao_reborn",
                "start_p": 1,
                "title": "第一幕 · 素鞋踏白玉，三千帝威归",
                "bgm_prompt": WORLD_OST["w4_frost_coffin_empress_awaken"],
                "bgm_duration_s": 80.0,
            },
            {
                "act_id": "act2_side_by_side_one_sword_cleave_thunder_palm",
                "start_p": 10,
                "title": "第二幕 · 并肩出界门，一剑断雷掌",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_seal_spatial_rift_dual_strike_slay_xuanming",
                "start_p": 36,
                "title": "第三幕 · 言出合界裂，刀剑诛玄冥",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_ten_thousand_hail_jiantian_mirror_locks",
                "start_p": 59,
                "title": "第四幕 · 万众拜双尊，深空监天凝",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 75.0,
            },
        ],
        acoustic_ranges=[
            (1, 9, "dry"),
            (10, 63, "vast_hall"),
        ],
        skip_onomatopoeia_paras={11, 16, 26, 29, 42, 49},
        dialogue_specs=[
            {"match": "这一回，你倒没食言", "role_id": "jiang_qinghuang", "tags": "[softly] [calmly]", "stability": 0.5, "space": "dry", "note": "真身出棺重归合道的姜清凰凝视陆烬掌心金血痕轻语"},
            {"match": "棺材已经炸碎了，往后想躲懒也没地方躺", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬反手握刀邀白衣女帝一道收拾仙庭老狗"},
            {"match": "正合吾意", "role_id": "jiang_qinghuang", "tags": "[coldly]", "stability": 0.5, "space": "dry", "note": "姜清凰眸底寒芒乍现杀机凛冽"},
            {"match": "碎了！他的乌龟壳终于要碎了", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "外界玄冥尊见界幕裂开百里蛛网狂喜叫嚣"},
            {"match": "什么狗屁四阶破锁者，在真正的第八境合道天威面前", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊狞笑催动雷掌欲连人带界抹灭"},
            {"match": "眉心凤翎印……太上玄凰气……是女帝陛下", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈认出与陆烬并肩踏出界门的白衣女帝真身"},
            {"match": "姜清凰！不可能，这绝对不可能", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊如白日见鬼尖利变调骇呼"},
            {"match": "太一的狗链子，已经被我身边这位拆干净了", "role_id": "jiang_qinghuang", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰看都未看玄冥尊淡漠宣告"},
            {"match": "雷掌归我，那条要跑的老狗归你", "role_id": "jiang_qinghuang", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰迎向万丈雷掌与陆烬分摊猎物"},
            {"match": "好，一人一半，公平得很", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬战意灼烧蓄势锁定玄冥尊逃路"},
            {"match": "东华老儿的一道半仙死符，也敢在本帝家门口撒野", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰掌凝玄凰帝剑自下而上一剑竖斩"},
            {"match": "留得青山在，待本尊回仙庭禀明四大仙君", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊吓破苦胆燃五成精血撕开裂缝仓皇逃窜"},
            {"match": "镇压玄黄三千年，抽干亿万遗民脊梁血", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬提前瞬移百里在裂缝尽头迎面截断玄冥尊"},
            {"match": "给我合上", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬言出法随强行闭合空间壁垒夹断玄冥尊右臂"},
            {"match": "小畜生，本尊便是自爆洞虚道果也要拉你垫背", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "断臂绝路的玄冥尊鼓胀气海妄图自爆道果"},
            {"match": "在我与女帝面前，你连自爆的资格都没有", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬眼神漠然宣判死局"},
            {"match": "太上敕令，封天锁道", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "姜清凰玄凰帝剑平点合拢合道领域冰封万法"},
            {"match": "断岳，斩锁", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬紫金焚天刀虹与玄凰帝剑交错成十字星芒"},
            {"match": "不！仙庭不会放过你们", "role_id": "sect_elder_antagonist", "speaker_name": "玄冥尊", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄冥尊连同镇界碑在刀剑合璧下灰飞烟灭"},
            {"match": "恭迎女帝陛下归位！拜谢陆尊救世再造大恩", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈率十万挺直脊梁的玄黄遗民热泪长拜"},
        ],
        sfx_blueprint=[
            {"p": 11, "pos": "before", "slug": "golden_dome_crack_under_thunder", "sfx_prompt": "Deafening white-gold thunderbolt hammering a giant golden crystal dome and cracking spiderweb fissures across the sky", "duration_seconds": 3.0, "gain_db": 1.5, "note": "轰咔！灭界雷掌将界幕压出百里蛛网裂痕"},
            {"p": 16, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "dual_protagonists_step_from_world_gate", "gain_db": 1.5, "note": "嗡！金色界幕主动洞开，陆烬与白衣女帝并肩踏空而出"},
            {"p": 26, "pos": "before", "slug": "condense_frost_phoenix_empress_sword", "sfx_prompt": "Rapid crystalline ice formation freezing surrounding wind into a razor-sharp translucent glacial sword with a pure high ring", "duration_seconds": 2.6, "gain_db": 1.5, "note": "咔嚓嚓！万里寒霜法则于姜清凰掌心凝成玄凰帝剑"},
            {"p": 29, "pos": "before", "slug": "one_frost_sword_cleave_thunder_to_rain", "sfx_prompt": "Pure razor-thin icy sword arc slicing upward, snapping a colossal thundercloud in half and dissolving into gentle falling rain", "duration_seconds": 3.8, "gain_db": 2.0, "note": "嗤！咔嚓！一剑两断合道灭界雷掌化作漫天温润灵雨"},
            {"p": 42, "pos": "before", "slug": "spatial_wall_slam_shut_sever", "sfx_prompt": "Heavy dimensional stone-like space barrier slamming shut with a thunderous boom", "duration_seconds": 2.4, "gain_db": 2.0, "note": "轰！言出法随强行闭合空间裂缝夹断玄冥尊右臂"},
            {"p": 55, "pos": "before", "slug": "frost_sword_flame_sabre_cross_slay", "sfx_prompt": "Twin intersecting weapon arcs of crystalline frost chime and roaring flame broadsword shattering a stone monument into dust", "duration_seconds": 3.6, "gain_db": 2.5, "note": "刀剑合璧交错十字星芒，彻底斩灭玄冥尊"},
        ],
    )
    j98, m98 = save_episode_scripts(s98, REPO_SCRIPTS_DIR, registry)
    built.append(("E098", s98, j98, m98))

    # =========================================================================
    # E099 · 第99章 重整太上旧山河，参悟合道执道门 (53 paras, 24 quotes)
    # =========================================================================
    md_99 = SOURCE_DIR / "第99章_重整太上旧山河，参悟合道执道门.md"
    s99 = compile_episode_cue_sheet(
        episode_id="E099",
        chapter_number=99,
        source_md_path=md_99,
        source_rel_path=f"02_分章精修正文/{md_99.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_uproot_sin_blood_monolith_nine_arrays",
                "start_p": 1,
                "title": "第一幕 · 连根拔母碑，九石护玄黄",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act2_heal_prison_army_restore_true_canon",
                "start_p": 12,
                "title": "第二幕 · 灵雨愈铁骑，正典授镇狱",
                "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act3_moonlit_rooftop_tea_own_world_hedao",
                "start_p": 21,
                "title": "第三幕 · 观星煮新茶，月下论合道",
                "bgm_prompt": WORLD_OST["w4_frost_coffin_empress_awaken"],
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act4_crimson_alarm_sixty_years_beiyuan_peril",
                "start_p": 40,
                "title": "第四幕 · 木马鸣血警，谁敢动北渊",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[
            (1, 20, "vast_hall"),
            (21, 40, "dry"),
            (41, 47, "mental_realm"),
            (48, 53, "vast_hall"),
        ],
        skip_onomatopoeia_paras={10, 41, 48},
        dialogue_specs=[
            {"match": "监天镜只是记录坐标的死物", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬立于高天感应监天镜银波退去核算时间"},
            {"match": "数日，足够把家底拾掇干净了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬从容定下整顿大计"},
            {"match": "皇城地底还埋着玄冥老狗留下的第七界母锁根基", "role_id": "jiang_qinghuang", "tags": "[coldly] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰散去帝剑提醒拔除皇城地底母锁"},
            {"match": "起", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬抹去罪血天刑母碑程序反手拔刀劈碎"},
            {"match": "末将萧烈，率太上镇狱军残部三千八百骑", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[shouting] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "萧烈率三千八百铁骑单膝触地抱拳听令"},
            {"match": "监天密库里的母石源码我已尽数破译", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬降灵雨化开全军暗伤并赐下剔除暗门的正本战典"},
            {"match": "陆尊大恩，镇狱军上下百死莫赎", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[trembling] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "萧烈手捧温热玉简虎目泛红重重抱拳"},
            {"match": "传本帝旨意，即日起废除伪朝一切苛政奴印", "role_id": "jiang_qinghuang", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰下旨开宝库重整太上镇狱军团备战仙庭"},
            {"match": "末将领旨", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[shouting]", "stability": 0.5, "space": "vast_hall", "note": "萧烈激动领命率军传檄四方"},
            {"match": "尝尝，用第八环息壤新芽配第三环神河净水泡的", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "dry", "note": "观星残殿屋脊月下，陆烬斟满热茶递与姜清凰"},
            {"match": "手艺尚可，勉强入得口", "role_id": "jiang_qinghuang", "tags": "[softly] [calmly]", "stability": 0.5, "space": "dry", "note": "姜清凰轻抿粗陶灵茶唇角微弯一丝极淡弧度"},
            {"match": "你如今已臻至洞虚大圆满，又有七界母锁源码", "role_id": "jiang_qinghuang", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "姜清凰放下茶盏正色询问陆烬欲合何道"},
            {"match": "愿闻女帝高见", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬端盏远眺皇城万家灯火"},
            {"match": "按上古常识，所谓第八境【合道】", "role_id": "jiang_qinghuang", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "姜清凰阐述上古第八境合道之理"},
            {"match": "例如本帝当年合的是太古玄冰凰道", "role_id": "jiang_qinghuang", "tags": "[coldly] [calmly]", "stability": 0.5, "space": "dry", "note": "姜清凰指沾茶水划出星河轨迹道出合道十万载威能"},
            {"match": "但今日在监天密库你也亲眼看见了", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "dry", "note": "姜清凰抹断水痕警告外层大道早被天道母碑篡改"},
            {"match": "所以我不能去合外头那条被太一篡改过的旧天道", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "dry", "note": "陆烬回首七界破锁征途眸底亮起璀璨神采"},
            {"match": "我有【方寸玄黄界】在身，这方世界本就脱胎于上古母界", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "dry", "note": "陆烬按胸立志以自身新界为基合众生破锁自强之道"},
            {"match": "以己界代天心，执破锁之刃为道基", "role_id": "jiang_qinghuang", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "dry", "note": "姜清凰眸光微震举起茶盏敬这条前无古人之路"},
            {"match": "早在北渊他们派人碎我丹田、逼走我爹的那天起", "role_id": "lu_jin", "tags": "[calmly] [coldly]", "stability": 0.5, "space": "dry", "note": "陆烬与女帝碰盏仰头一饮而尽"},
            {"match": "仙庭第七巡狩司急令：据监天副镜核查", "role_id": "ancient_construct_echo", "speaker_name": "仙庭监天网急令", "tags": "[coldly]", "stability": 1.0, "space": "mental_realm", "note": "第六环太一木马魂截获仙庭核查大苍血月界密电"},
            {"match": "现命洞虚大圆满【无面巡狩使·苍刑】", "role_id": "ancient_construct_echo", "speaker_name": "仙庭监天网急令", "tags": "[coldly]", "stability": 1.0, "space": "mental_realm", "note": "十艘白金屠界战舰直扑大苍北渊启动灭界主炮"},
            {"match": "一甲子……大苍界与高维墟海的时间流速竟差了十倍不止", "role_id": "lu_jin", "tags": "[hoarsely] [trembling]", "stability": 0.0, "space": "vast_hall", "note": "陆烬惊觉故乡已过六十年沧桑岁月"},
            {"match": "仙庭老狗，谁敢动我北渊故乡一草一木", "role_id": "lu_jin", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬反手紧握断岳刀杀意令整座玄黄夜空结霜"},
        ],
        sfx_blueprint=[
            {"p": 10, "pos": "before", "slug": "cleave_sin_monolith_nine_stones", "sfx_prompt": "Heavy broadsword slash shattering a giant subterranean stone monument into nine glowing boulders with deep earth rumble", "duration_seconds": 3.4, "gain_db": 2.0, "note": "轰隆！劈碎罪血天刑母碑化作九块界源神石护界"},
            {"p": 22, "pos": "before", "slug": "night_breeze_bronze_roof_bell_tea", "sfx_prompt": "Gentle night breeze chiming weathered bronze roof bells while water softly simmers over charcoal in a clay kettle", "duration_seconds": 3.5, "gain_db": 0.5, "note": "观星残殿屋脊夜风吹响青铜古铃，泥炉煮茶"},
            {"p": 39, "pos": "after", "slug": "ceramic_teacups_clink_moonlight", "sfx_prompt": "Two rustic ceramic teacups clinking together crisply once in quiet night air", "duration_seconds": 1.8, "gain_db": 1.0, "note": "陆烬与姜清凰月下碰盏一饮而尽"},
            {"p": 41, "pos": "before", "slug": "sixth_ring_bronze_chains_alarm", "sfx_prompt": "Urgent rapid clanking of heavy bronze cage chains and sharp metallic alarm hum in a dark hall", "duration_seconds": 2.8, "gain_db": 1.5, "note": "嗡嗡嗡！第六环囚道铜殿传来急促青铜锁链警报"},
            {"p": 48, "pos": "before", "slug": "rooftop_pulverize_sabre_cry", "sfx_prompt": "Sudden explosive shockwave pulverizing stone roof tiles into dust accompanied by a fierce resonant broadsword hum", "duration_seconds": 3.2, "gain_db": 2.0, "note": "轰！滔天杀意震碎观星残殿砖瓦，断岳刀剧烈嗡鸣"},
        ],
    )
    j99, m99 = save_episode_scripts(s99, REPO_SCRIPTS_DIR, registry)
    built.append(("E099", s99, j99, m99))

    # =========================================================================
    # E100 · 第100章 百章里程碑：合道执道成！谁敢动我故乡一草一木！ (57 paras, 16 quotes)
    # =========================================================================
    md_100 = SOURCE_DIR / "第100章_百章里程碑：合道执道成！谁敢动我故乡一草一木！.md"
    s100 = compile_episode_cue_sheet(
        episode_id="E100",
        chapter_number=100,
        source_md_path=md_100,
        source_rel_path=f"02_分章精修正文/{md_100.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_hundred_breaths_crisis_step_into_hedao",
                "start_p": 1,
                "title": "第一幕 · 百息悬屠炮，一步冲合道",
                "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                "bgm_duration_s": 80.0,
            },
            {
                "act_id": "act2_prove_dao_by_own_world_tear_heaven_chains",
                "start_p": 9,
                "title": "第二幕 · 己界立真道，徒手撕天链",
                "bgm_prompt": WORLD_OST["w7_empress_out_of_coffin_war"],
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act3_dual_hedao_spin_astrolabe_cleave_seven_worlds",
                "start_p": 29,
                "title": "第三幕 · 双尊催星盘，一刀贯七界",
                "bgm_prompt": WORLD_OST["w4_frost_coffin_empress_awaken"],
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_sixty_years_apart_step_over_beiyuan_sky",
                "start_p": 45,
                "title": "第四幕 · 阔别一甲子，踏门临北渊",
                "bgm_prompt": WORLD_OST["w7_ancestral_wasteland_sorrow"],
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[
            (1, 7, "dry"),
            (8, 57, "vast_hall"),
        ],
        skip_onomatopoeia_paras={9, 15, 21, 43},
        dialogue_specs=[
            {"match": "从第七界横渡回第一图大苍界", "role_id": "jiang_qinghuang", "tags": "[coldly]", "stability": 0.5, "space": "dry", "note": "姜清凰踏至陆烬身侧神念扫过万界坐标台"},
            {"match": "若按常规洞虚遁速逐层穿界，哪怕不眠不休也需半个时辰", "role_id": "jiang_qinghuang", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "dry", "note": "姜清凰指出屠界战舰主炮蓄能最多百息"},
            {"match": "半个时辰太久，百息也太长", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "dry", "note": "绝境之中陆烬绝对理智冷冽如万载寒铁"},
            {"match": "洞虚境跨不过去，那便现在踏入合道", "role_id": "lu_jin", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "dry", "note": "陆烬决定当场证道第八境合道一步跨回故乡"},
            {"match": "天地不仁，以万物为刍狗", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬将全部道果撞入方寸玄黄界本源声震九霄"},
            {"match": "今日我陆烬立道，不拜太一，不合伪天", "role_id": "lu_jin", "tags": "[dramatically] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬立众生破锁自强之道悍然冲破合道天堑"},
            {"match": "连面都不敢露的死物，也妄想锁我的道", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬徒手拽住天道母碑降下的数十根灰色秩序锁链"},
            {"match": "好霸道的执道法相，竟连天道母碑自动降下的锁道链都被你生嚼了", "role_id": "jiang_qinghuang", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰近距离感受陆烬独立于仙庭天网外的合道威压"},
            {"match": "不假外求，自成一界大道，单论根基之浑厚", "role_id": "jiang_qinghuang", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "玄凰女帝赞叹陆烬合道根基已胜全盛时的顾长渊"},
            {"match": "道成了，该去救人了", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬晋升合道执道境与六阶神兵后毫不停留"},
            {"match": "萧烈，守好九重护界大阵，我去故乡斩几条仙庭恶犬", "role_id": "lu_jin", "tags": "[calmly] [shouting]", "stability": 0.5, "space": "vast_hall", "note": "陆烬隔空向皇城大营降下宏大合道法旨"},
            {"match": "末将遵旨，誓与母界共存亡", "role_id": "qin_lie", "speaker_name": "萧烈", "tags": "[shouting]", "stability": 0.5, "space": "vast_hall", "note": "下方萧烈恭敬领命镇守玄黄"},
            {"match": "女帝，助我定锚，直接打穿七界壁障", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬左手按住第七十三号星点右手拔出六阶断岳刀"},
            {"match": "好，本帝倒也想看看，养出你这尊怪物的故乡究竟是何模样", "role_id": "jiang_qinghuang", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "姜清凰结太上玄凰印毫无保留汇入合道帝力"},
            {"match": "大苍北渊，给我开", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "两位合道至尊联手，陆烬一刀竖劈贯穿七重世界晶壁"},
            {"match": "走", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "见十艘屠界战舰主炮压顶北渊雄城，陆烬与姜清凰并肩踏入天门"},
        ],
        sfx_blueprint=[
            {"p": 9, "pos": "before", "slug": "new_world_mountains_rivers_boom", "sfx_prompt": "Monumental cosmic earth-and-sky resonance boom with roaring rivers and deep bronze bell overtones", "duration_seconds": 3.4, "gain_db": 2.0, "note": "轰隆！一步踏向天心，九环大地与旧母界山河轰鸣"},
            {"p": 15, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "shatter_hedao_barrier_ascension", "gain_db": 2.0, "note": "咔嚓！刀心与一界本源撞碎第八境合道万古天堑"},
            {"p": 21, "pos": "before", "slug": "tear_apart_heaven_order_chains", "sfx_prompt": "Dozens of taut heavy metallic chains snapping apart violently under immense force followed by roaring golden furnace fire", "duration_seconds": 3.4, "gain_db": 2.5, "note": "崩崩崩！陆烬徒手扯断数十根灰色天道秩序锁链塞入本源烘炉"},
            {"p": 35, "pos": "before", "slug": "giant_star_astrolabe_rings_align", "sfx_prompt": "Three hundred concentric ancient stone astrolabe rings spinning rapidly and locking into alignment with celestial chimes", "duration_seconds": 3.0, "gain_db": 1.5, "note": "万界坐标台三百六十圈古老星轨极速飞旋对齐"},
            {"p": 43, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "cleave_seven_worlds_star_gate", "gain_db": 2.0, "note": "嗤啦！六阶断岳刀一刀劈开贯穿七重维度晶壁的千丈紫金空间天门"},
        ],
    )
    j100, m100 = save_episode_scripts(s100, REPO_SCRIPTS_DIR, registry)
    built.append(("E100", s100, j100, m100))

    return built


if __name__ == "__main__":
    results = build_all_batch14()
    for ep_id, sheet, jp, mp in results:
        dial_cnt = sum(1 for c in sheet.cues if c.kind == "dialogue" and c.role_id != "narrator")
        narr_cnt = sum(1 for c in sheet.cues if c.kind == "dialogue" and c.role_id == "narrator")
        sfx_cnt = sum(1 for c in sheet.cues if c.kind == "sfx")
        print(
            f"[COMPILED & VALIDATED] {ep_id} | acts={len(sheet.acts)} | "
            f"cues={len(sheet.cues)} (narr={narr_cnt}, char={dial_cnt}, sfx={sfx_cnt}) | "
            f"json={jp.name}",
            flush=True,
        )
