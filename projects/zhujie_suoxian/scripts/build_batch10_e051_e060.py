#!/usr/bin/env python3
"""Build and validate Batch 10: Episodes E051–E060 (Chapters 51–60 of 《诸界锁仙》).

Covers:
- E051–E052: World 2 Finale — Four Millennia's First Sunlight, Second Coffin Key & Crossing into the Bitter Sea
- E053–E055: World 3 Opening — Landless Bitter Sea, Parasitic Immortal Bones, Slaying the Rift-Leviathan & Second Gene-Lock / Flawless Golden Core
- E056: True Body Enters Fangcun Xujie & Fifth Ring Double-Helix Gene Monoliths (Chen Xuan's Bone Testament)
- E057–E058: Night Raid on Black-Abyss Sea Prison, Father-Son Reunion with Lu Qingcang, Twin Sabres Breakout & Origin Secret
- E059–E060: Seven-Turn Golden Core, Fourth Ring Fallen-Star Palace (Faceless Lord Gu Mural), Reforging 360-Jin Duanyue & Lone Sabre into Guixu Eye
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRATCH_DIR = Path(__file__).resolve().parent
for p in (str(REPO_ROOT / "src"), str(SCRATCH_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

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

_TRAILING_QUOTE_PUNCT_RE = re.compile(r"”([。！？]+)\s*$", re.MULTILINE)


def _prepare_chapter_md(md_path: Path, tmp_dir: Path) -> Path:
    """Normalize line-final `”。`/`”！` into `。”`/`！”` in an ephemeral temp copy if needed.

    Prevents trailing punctuation outside closing quotes (e.g. Ch56 P17, Ch59 P69)
    from emitting a standalone non-CJK punctuation narrator cue, without modifying
    any source files or shared compiler code and preserving 100% CJK characters.
    """
    raw = md_path.read_text(encoding="utf-8")
    fixed = _TRAILING_QUOTE_PUNCT_RE.sub(r"\1”", raw)
    if fixed == raw:
        return md_path
    staged = tmp_dir / md_path.name
    staged.write_text(fixed, encoding="utf-8")
    return staged


def build_all_batch10() -> list[tuple[str, object, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, object, Path, Path]] = []

    with tempfile.TemporaryDirectory(prefix="zhujie_batch10_") as tmp_s:
        tmp_dir = Path(tmp_s)

        # =====================================================================
        # E051 · 第51章 四千年第一缕阳光，世间原是有白昼！ (68 paras, 16 quotes)
        # =====================================================================
        md_51 = SOURCE_DIR / "第51章_四千年第一缕阳光，世间原是有白昼！.md"
        s51 = compile_episode_cue_sheet(
            episode_id="E051",
            chapter_number=51,
            source_md_path=_prepare_chapter_md(md_51, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_51.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_cleave_black_sun_tower_falls",
                    "start_p": 1,
                    "title": "第一幕 · 断岳劈母盘，圣塔坠黑渊",
                    "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act2_eternal_night_panic_blind_curse_breaks",
                    "start_p": 10,
                    "title": "第二幕 · 骨灯灭全城，盲锁碎无声",
                    "bgm_prompt": WORLD_OST["w2_eternal_night_tension"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act3_four_millennia_first_sunlight",
                    "start_p": 26,
                    "title": "第三幕 · 破夜跃金乌，四千载初阳",
                    "bgm_prompt": WORLD_OST["w2_first_sunlight_catharsis"],
                    "bgm_duration_s": 120.0,
                },
                {
                    "act_id": "act4_second_coffin_key_father_carving",
                    "start_p": 50,
                    "title": "第四幕 · 棺中初闻语，井底见父痕",
                    "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                    "bgm_duration_s": 100.0,
                },
            ],
            acoustic_ranges=[
                (1, 9, "vast_hall"),
                (50, 53, "vast_hall"),
                (54, 61, "mental_realm"),
                (62, 68, "vast_hall"),
            ],
            skip_onomatopoeia_paras={5, 22, 29, 54, 56},
            dialogue_specs=[
                {"match": "四千年认知画皮，给我破", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百丈井底陆烬灌注半步金丹与焚锁妖煞火怒劈黑日母盘"},
                {"match": "圣塔塌了！不灭骨灯灭了", "role_id": "male_disciple_b", "speaker_name": "圣京惊恐百姓", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "骨灯主塔轰塌全城陷入漆黑，百姓惊恐哭喊"},
                {"match": "没有圣塔照明，黑暗里的", "role_id": "snobbish_steward_npc", "speaker_name": "司灯小吏", "tags": "[crying] [desperately]", "stability": 0.0, "note": "司灯小吏跪在骨灰里绝望哭嚎惧怕噬影夜魔"},
                {"match": "不冷……这光不吃人！孩儿他爹", "role_id": "female_maid_npc", "speaker_name": "铁匠铺妇人", "tags": "[crying] [trembling]", "stability": 0.0, "note": "二十五岁枯发妇人捧住第一缕温暖阳光喜极哭喊"},
                {"match": "天亮了？原来古书残页里写的不是疯话", "role_id": "weathered_elder_npc", "speaker_name": "圣京老丈", "tags": "[gasps] [trembling]", "stability": 0.0, "note": "老者仰望高天金日震撼惊呼"},
                {"match": "什么金灯，我听守昼逆党喊过", "role_id": "male_disciple_a", "speaker_name": "圣京青年修士", "tags": "[shouting] [crying]", "stability": 0.0, "note": "青年修士热泪盈眶高喊出太阳之名"},
                {"match": "陆少侠，这便是古籍里记载的真正太阳么", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[softly] [crying]", "stability": 0.0, "note": "沈烛音解下蒙眼黑布首见烈日，含泪向陆烬深揖"},
                {"match": "这才是人间本该有的白昼", "role_id": "lu_jin", "tags": "[calmly] [softly]", "stability": 0.5, "note": "陆烬任晨曦洒满虎口淡然回应"},
                {"match": "老雷活了六十岁，头一回知道晒太阳是什么滋味", "role_id": "qin_lie", "speaker_name": "雷横", "tags": "[laughs] [shouting]", "stability": 0.0, "note": "虬髯刀客雷横拄刀仰天含泪豪笑抱拳"},
                {"match": "列祖列宗在上，四千年了，守昼一脉不辱使命", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[dramatically] [trembling]", "stability": 0.0, "note": "沈烛音朝朝阳与陆烬郑重俯首告慰守昼先祖"},
                {"match": "井底尚有首尾待我处置，外头残局便交由沈姑娘收拢了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬神识锁定井底界钥微光，颔首重返地宫"},
                {"match": "第二枚开棺界钥，【烬昼界锁核心碎片】", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "陆烬于母盘残骸中拾起第二枚暗金界钥"},
                {"match": "第二把了……这一世，你倒是走得比当年快", "role_id": "jiang_qinghuang", "speaker_name": "棺中女帝", "tags": "[whispers] [coldly]", "stability": 0.5, "space": "mental_realm", "note": "玄霜古棺松开第二链，姜清凰跨越万古首次传出清冷心音"},
                {"match": "棺中果然锁着一尊尚存意识的绝世人物", "role_id": "lu_jin", "tags": "[coldly] [whispers]", "stability": 0.5, "space": "vast_hall", "note": "井底陆烬瞳孔微缩握紧零号铭牌"},
                {"match": "无妨。不管是谁的过去，如今握刀的人是我陆烬", "role_id": "lu_jin", "tags": "[fiercely] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬坚立本我道心"},
                {"match": "烬儿，父携遗民赴东海归墟，勿念", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.5, "space": "memory_echo", "note": "黑石井壁上陆擎苍重刀入石三分劈刻的十一字留书"},
            ],
            sfx_blueprint=[
                {"p": 5, "pos": "before", "slug": "cleave_black_sun_disk", "sfx_prompt": "Heavy dark-gold broadsword thunder strike shattering a colossal ancient obsidian disk and snapping ethereal chains in a deep stone cavern", "duration_seconds": 3.6, "gain_db": 2.0, "note": "铛咔嚓！断岳一刀劈裂永夜黑日母盘"},
                {"p": 11, "pos": "before", "slug": "bone_tower_collapse_rumble", "sfx_prompt": "Colossal three-thousand-foot bone tower collapsing into rubble with roaring dark flames extinguishing into eerie silence", "duration_seconds": 3.8, "gain_db": 1.5, "note": "太祖不灭骨灯主塔轰塌，惨白鬼火熄灭"},
                {"p": 22, "pos": "before", "slug": "warm_dawn_breeze_sweep", "sfx_prompt": "Gentle clean morning mountain breeze sweeping softly across quiet stone battlements", "duration_seconds": 2.8, "gain_db": 0.5, "note": "呼……清凉温润的自然晨风吹过圣京城头"},
                {"p": 29, "pos": "before", "slug": "golden_sunrise_flood_horizon", "sfx_prompt": "Majestic resonant dawn horizon shimmer and warm golden light cresting over distant mountain peaks", "duration_seconds": 3.5, "gain_db": 1.5, "note": "轰！四千年第一轮朝阳刺破长夜倾泻人间"},
                {"p": 56, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "second_coffin_chain_loosen", "gain_db": 1.5, "note": "哗啦铿！玄霜古棺第二根寒铁法则锁链松开三寸"},
            ],
        )
        j51, m51 = save_episode_scripts(s51, REPO_SCRIPTS_DIR, registry)
        built.append(("E051", s51, j51, m51))

        # =====================================================================
        # E052 · 第52章 辞别晨曦入苦海，半步金丹踏鲸波 (51 paras, 10 quotes)
        # =====================================================================
        md_52 = SOURCE_DIR / "第52章_辞别晨曦入苦海，半步金丹踏鲸波.md"
        s52 = compile_episode_cue_sheet(
            episode_id="E052",
            chapter_number=52,
            source_md_path=_prepare_chapter_md(md_52, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_52.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_morning_healing_reborn_capital",
                    "start_p": 1,
                    "title": "第一幕 · 抚痕追父迹，圣京沐新生",
                    "bgm_prompt": WORLD_OST["w2_first_sunlight_catharsis"],
                    "bgm_duration_s": 100.0,
                },
                {
                    "act_id": "act2_city_gate_farewell_dragon_pearl",
                    "start_p": 11,
                    "title": "第二幕 · 托书寻铁山，赠法别晨曦",
                    "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                    "bgm_duration_s": 105.0,
                },
                {
                    "act_id": "act3_plunge_vortex_cross_abyssal_current",
                    "start_p": 27,
                    "title": "第三幕 · 龙珠辟暗流，潜龙破界波",
                    "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act4_landless_bitter_sea_whale_bone_island",
                    "start_p": 43,
                    "title": "第四幕 · 万里无寸土，百里玄鲸骸",
                    "bgm_prompt": WORLD_OST["w3_abyssal_sea_desolation"],
                    "bgm_duration_s": 95.0,
                },
            ],
            acoustic_ranges=[
                (1, 4, "vast_hall"),
                (27, 41, "vast_hall"),
            ],
            skip_onomatopoeia_paras={34, 42},
            dialogue_specs=[
                {"match": "东海归墟么，爹，儿子这便随后跟上了", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬轻抚井壁勿念刀痕低语"},
                {"match": "有劳雷前辈走一趟西境灰原郡", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "东华门城楼陆烬托雷横送信接独臂盲眼老丈铁山"},
                {"match": "陆少侠救了老雷和三十三位兄弟的命", "role_id": "qin_lie", "speaker_name": "雷横", "tags": "[shouting] [laughs]", "stability": 0.5, "note": "雷横拍胸脯郑重应承护送铁山老丈"},
                {"match": "沿途各郡刚历剧变，难免有溃兵宵小作乱", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬赠五百上品灵石作沿途补给"},
                {"match": "陆少侠劈碎永夜、斩灭国师", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[softly] [dramatically]", "stability": 0.5, "note": "沈烛音奉上定海龙珠与十八株三阶大药"},
                {"match": "大胤旧修的《燃髓功》透支寿元不可再练", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬收下龙珠灵药，回赠正统《古引气篇》玉简"},
                {"match": "恭送陆少侠！愿少侠前路破浪乘风", "role_id": "su_qinghan", "speaker_name": "沈烛音", "tags": "[dramatically] [crying]", "stability": 0.0, "note": "沈烛音率全城守昼族老将士长揖送别"},
                {"match": "保重", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬拱手道别转身入井"},
                {"match": "底牌已足，该去会一会这第三座认知世界了", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.5, "space": "vast_hall", "note": "跨界水脉旁陆烬盘点底蕴决然跃入漩涡"},
                {"match": "破！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬双足重踏暗流如潜龙冲破万顷碧波"},
            ],
            sfx_blueprint=[
                {"p": 15, "pos": "after", "slug": "warhorse_gallop_depart_gate", "sfx_prompt": "Armored warhorse hooves galloping briskly away down a stone city rampart", "duration_seconds": 2.6, "gain_db": 0.5, "note": "雷横翻身上马疾驰出城西去"},
                {"p": 34, "pos": "before", "slug": "plunge_interworld_sea_vortex", "sfx_prompt": "Powerful plunge into a roaring abyssal underwater whirlpool with crushing sub-bass current pressure and shimmering water-shield hum", "duration_seconds": 3.8, "gain_db": 1.5, "note": "轰隆隆！陆烬手持定海龙珠跃入碧蓝跨界漩涡"},
                {"p": 42, "pos": "before", "slug": "burst_from_ocean_waves", "sfx_prompt": "Explosive water breach bursting up through heavy ocean waves into open coastal wind and spray", "duration_seconds": 3.2, "gain_db": 1.5, "note": "哗啦！陆烬冲破万顷碧波立于无陆苦海浪尖"},
                {"p": 48, "pos": "before", "slug": "colossal_whale_bone_island_waves", "sfx_prompt": "Deep booming ocean swells crashing against hollow mountain-sized ancient whale bones", "duration_seconds": 3.4, "gain_db": 0.5, "note": "八里外怒涛中央横卧百里太古鲸骸筑成的玄鲸岛"},
            ],
        )
        j52, m52 = save_episode_scripts(s52, REPO_SCRIPTS_DIR, registry)
        built.append(("E052", s52, j52, m52))

        # =====================================================================
        # E053 · 第53章 第三认知世界：无陆苦海，人人殖仙骨！ (67 paras, 25 quotes)
        # =====================================================================
        md_53 = SOURCE_DIR / "第53章_第三认知世界：无陆苦海，人人殖仙骨！.md"
        s53 = compile_episode_cue_sheet(
            episode_id="E053",
            chapter_number=53,
            source_md_path=_prepare_chapter_md(md_53, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_53.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_slay_bone_shark_three_step_probe",
                    "start_p": 1,
                    "title": "第一幕 · 弹指毙骨鲨，禁言大陆名",
                    "bgm_prompt": WORLD_OST["w3_abyssal_sea_desolation"],
                    "bgm_duration_s": 105.0,
                },
                {
                    "act_id": "act2_whale_harbor_parasite_bone_truth",
                    "start_p": 27,
                    "title": "第二幕 · 破妄窥菌丝，溺灵寄生锁",
                    "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                    "bgm_duration_s": 100.0,
                },
                {
                    "act_id": "act3_one_armed_blademaster_sea_prison_news",
                    "start_p": 48,
                    "title": "第三幕 · 独臂断后战，父陷黑渊狱",
                    "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act4_bone_bell_tolls_young_lord_aohuan",
                    "start_p": 62,
                    "title": "第四幕 · 鲸颚骨钟鸣，少主锁无骨",
                    "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                    "bgm_duration_s": 85.0,
                },
            ],
            skip_onomatopoeia_paras={11, 55, 62},
            dialogue_specs=[
                {"match": "难怪岛上那些修士人人后背都刺出活体白骨", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬初探苦海水汽看破殖骨之毒"},
                {"match": "滚开！这船苦珠是给我娘换续命膏的", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "采珠少女海棠虎口淌血持锈铁叉死战锯齿骨鲨"},
                {"match": "多谢前辈救命之恩！晚辈玄鲸岛外港采珠女海棠", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[gasps] [softly]", "stability": 0.5, "note": "海棠跪拜叩谢陆烬救命之恩"},
                {"match": "举手之劳，起来说话", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬抬手示意海棠起身"},
                {"match": "我自外海远游遇风暴毁了船，此去玄鲸岛可顺路", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬见海棠背嵌死鱼碎骨未染魔性，搭船入港"},
                {"match": "顺路！晚辈这就摇橹送前辈入港", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[softly]", "stability": 0.5, "note": "海棠欣喜摇橹引路"},
                {"match": "我在外海迷了方位，不知从玄鲸岛往东或往西", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬入界三步试探第一步：试问大陆方位"},
                {"match": "前辈慎言！进了玄鲸岛千万别提", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[whispers] [trembling]", "stability": 0.0, "note": "海棠吓得手抖压低嗓音警告切莫提大陆二字"},
                {"match": "去年岛上有个老书生醉酒妄言海底曾是万里桑田", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[whispers] [softly]", "stability": 0.0, "note": "海棠心有余悸说起老书生被沉海沟"},
                {"match": "前辈可是觉得咱们苦海的灵气滞重难吸", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[softly]", "stability": 0.5, "note": "海棠见陆烬逼出指尖白汽轻声发问"},
                {"match": "咱们苦海人族生来便是漏灵泥胎", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[sighs] [softly]", "stability": 0.5, "note": "海棠道出苦海人族十岁剖背植入古仙遗骨的铁律"},
                {"match": "只怪我十岁那年爹爹下海捞骨丧了命", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[sighs] [crying]", "stability": 0.0, "note": "海棠黯然诉说大伯夺骨、自己仅嵌死鱼碎骨的身世"},
                {"match": "好毒的一道【溺灵寄生锁】", "role_id": "lu_jin", "tags": "[coldly] [whispers]", "stability": 0.5, "note": "陆烬以破妄真目看穿外骨下扎入脑干的万千寄生菌丝"},
                {"match": "先在水气里下毒断绝凡人正统引气之路", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬心底冷冽剖析溺灵寄生锁真相"},
                {"match": "海棠姑娘常在码头走动，这两年间可曾听说过", "role_id": "lu_jin", "tags": "[calmly] [softly]", "stability": 0.5, "note": "小船靠港陆烬赠灵石试探父亲消息"},
                {"match": "前辈莫非认识去年闯海的那批外海狂徒", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[whispers] [trembling]", "stability": 0.0, "note": "海棠脸色煞白拉陆烬退入巨鲸肋骨死角低语"},
                {"match": "有一位长辈走散，正是使黑铁阔刀", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬心头剧震面上沉稳应答"},
                {"match": "那可遭了大难了", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[gasps] [whispers]", "stability": 0.0, "note": "海棠急促低呼"},
                {"match": "就在一年前秋汛狂风那日，外海怒涛里冲进来", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[whispers] [softly]", "stability": 0.0, "note": "海棠低声讲述一年前无骨木船闯海血战"},
                {"match": "领头的正是一位左袖空空、断了左臂的高大猛汉", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[trembling] [softly]", "stability": 0.0, "note": "海棠讲述陆擎苍断左臂单刀砍翻三名金丹海卫断后被擒"},
                {"match": "人现在关在何处", "role_id": "lu_jin", "tags": "[hoarsely] [coldly]", "stability": 0.0, "note": "陆烬攥紧断岳刀柄强压四年翻涌气血沙哑追问"},
                {"match": "全关在三千里外万丈海底的【黑渊海狱】", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[whispers] [desperately]", "stability": 0.0, "note": "海棠急告黑渊海狱下落"},
                {"match": "前两日码头海卫喝酒漏了嘴，说是血骨狱主", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[whispers] [trembling]", "stability": 0.0, "note": "海棠急告血骨狱主欲剖陆擎苍脊梁试种三阶凶魔骨"},
                {"match": "是玄鲸少岛主鳌桓！快低头亮出后背仙骨", "role_id": "male_disciple_b", "speaker_name": "码头散修", "tags": "[gasps] [trembling]", "stability": 0.0, "note": "满港散修惊见少岛主鳌桓降临魂飞魄散跪伏"},
                {"match": "奉海皇殿严令，搜捕混入三十六岛的无骨异端", "role_id": "pei_xuandu", "speaker_name": "鳌桓", "tags": "[coldly] [shouting]", "stability": 0.0, "note": "玄鲸少岛主鳌桓踏空阴冷下令搜捕无骨异端"},
            ],
            sfx_blueprint=[
                {"p": 11, "pos": "before", "slug": "finger_qi_pierce_bone_shark", "sfx_prompt": "Razor-sharp golden qi flick slicing through ocean spray and shattering a giant shark skull in churning waves", "duration_seconds": 2.5, "gain_db": 1.5, "note": "咻！陆烬屈指一弹暗金指风瞬毙二阶锯齿骨鲨"},
                {"p": 33, "pos": "before", "slug": "wooden_skiff_enter_whale_harbor", "sfx_prompt": "Wooden oars rowing a small skiff into a cavernous harbor with creaking timber and lapping tidewater", "duration_seconds": 3.0, "gain_db": 0.5, "note": "乌木小船顺潮驶入巨鲸骸骨敞开的百丈巨口港湾"},
                {"p": 55, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "fist_clench_sabre_hilt_blood_surge", "gain_db": 1.0, "note": "轰！听闻养父断臂死战被锁，陆烬五指攥紧断岳热血冲眶"},
                {"p": 62, "pos": "before", "slug": "whale_jaw_bone_bell_alarm", "sfx_prompt": "Three harsh resonant strikes of a giant hollow bone bell echoing across a coastal dock and splashing sea foam", "duration_seconds": 3.4, "gain_db": 2.0, "note": "当当当！鲸颚顶端三丈惨白骨钟骤然轰鸣封港"},
            ],
        )
        j53, m53 = save_episode_scripts(s53, REPO_SCRIPTS_DIR, registry)
        built.append(("E053", s53, j53, m53))

        # =====================================================================
        # E054 · 第54章 无骨亦斩假丹，深海猎取第三真血 (71 paras, 18 quotes)
        # =====================================================================
        md_54 = SOURCE_DIR / "第54章_无骨亦斩假丹，深海猎取第三真血.md"
        s54 = compile_episode_cue_sheet(
            episode_id="E054",
            chapter_number=54,
            source_md_path=_prepare_chapter_md(md_54, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_54.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_unsheathed_scabbard_slay_aohuan",
                    "start_p": 1,
                    "title": "第一幕 · 刀未出鞘碎八蛛，一击毙少主",
                    "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act2_lone_reef_deduction_kun_sea_chart",
                    "start_p": 30,
                    "title": "第二幕 · 孤礁推海防，古图指雷渊",
                    "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                    "bgm_duration_s": 100.0,
                },
                {
                    "act_id": "act3_abyss_trench_hundred_clashes_kun",
                    "start_p": 43,
                    "title": "第三幕 · 潜渊三千丈，百招撼裂空",
                    "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                    "bgm_duration_s": 105.0,
                },
                {
                    "act_id": "act4_soul_spike_slay_kun_three_bloods_ready",
                    "start_p": 59,
                    "title": "第四幕 · 惊神破逆鳞，三血聚火岩",
                    "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                    "bgm_duration_s": 95.0,
                },
            ],
            acoustic_ranges=[(44, 71, "vast_hall")],
            skip_onomatopoeia_paras={11, 15, 20, 52, 62, 66},
            dialogue_specs=[
                {"match": "站稳了，别出来", "role_id": "lu_jin", "tags": "[calmly] [softly]", "stability": 0.5, "note": "陆烬按住海棠肩头将其护在巨鲸肋骨后"},
                {"match": "怪不得浑身漏不出半点水灵气", "role_id": "pei_xuandu", "speaker_name": "鳌桓", "tags": "[coldly]", "stability": 0.5, "note": "少岛主鳌桓居高临下蔑视陆烬"},
                {"match": "说吧，你是去年那批外海独臂刀匪的余孽", "role_id": "pei_xuandu", "speaker_name": "鳌桓", "tags": "[coldly] [laughs]", "stability": 0.0, "note": "鳌桓残忍戏谑欲拿腐尸虾骨钉入陆烬脖颈"},
                {"match": "把深海妖魔烂肉塞进自己脊梁替怪物养菌丝", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬看穿鳌桓体内菌丝淡漠讥讽"},
                {"match": "不知死活的泥胎，本少先把你钉穿拆成肉泥", "role_id": "pei_xuandu", "speaker_name": "鳌桓", "tags": "[angry] [shouting]", "stability": 0.0, "note": "鳌桓暴怒催动八蛛穿心刺扑杀而下"},
                {"match": "什么？不……", "role_id": "pei_xuandu", "speaker_name": "鳌桓", "tags": "[gasps] [desperately]", "stability": 0.0, "note": "八根准三阶蜘蛛骨刺被乌金刀鞘一击拍碎，鳌桓骇然绝望"},
                {"match": "走！", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬震晕全港玄鲸卫提海棠化电光离港"},
                {"match": "救人只有一次雷霆突袭的机会", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "孤礁上陆烬研读海防图冷静决断"},
                {"match": "我如今虽是半步金丹，足以逆斩寻常金丹初期", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬权衡十招速杀血骨狱主与全身而退所需底气"},
                {"match": "海棠姑娘，玄鲸岛百里之内，可有什么天生不长白骨菌丝", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬向海棠打听纯净三阶深海古兽"},
                {"match": "回恩公的话！寻常海兽大多也被白骨同化了", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[softly] [dramatically]", "stability": 0.0, "note": "海棠奉上祖传鱼皮古海图指明雷渊海沟裂空鲲兽"},
                {"match": "我爷爷当年远远见过它换气，那鲲兽浑身星斑蓝鳞", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[desperately] [softly]", "stability": 0.0, "note": "海棠急切提醒裂空鲲兽折叠吞水凶险"},
                {"match": "玄鲸岛不能再回了，顺西侧暗流去百里外红珊渔村暂避十日", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬留护身刀意玉佩与灵丹安排海棠去红珊渔村"},
                {"match": "来得好！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三千丈雷渊海底陆烬拔刀迎战裂空鲲兽"},
                {"match": "皮肉堪比三阶法宝，吞噬水幕每十息需换气一次", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬一招试出鲲兽换气破绽"},
                {"match": "就是现在，《惊神刺》！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百招交汇半息空档陆烬祭出惊神刺重创鲲兽识海"},
                {"match": "给我破！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬灌注焚锁妖煞火一刀贯穿鲲兽逆鳞"},
                {"match": "今夜，便在这三千丈苦海地底，破二阶基因锁", "role_id": "lu_jin", "tags": "[dramatically] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "海底死火山空腔内陆烬双掌拍碎三只真血玉匣"},
            ],
            sfx_blueprint=[
                {"p": 11, "pos": "before", "slug": "spider_bone_spears_lunge", "sfx_prompt": "Sharp stone beam shattering followed by eight barbed bone spears whistling viciously through coastal wind", "duration_seconds": 2.5, "gain_db": 1.5, "note": "刺啦！鳌桓脚碎石梁八根蜘蛛骨刺扑杀而下"},
                {"p": 15, "pos": "before", "slug": "heavy_scabbard_shatter_eight_bones", "sfx_prompt": "Colossal heavy iron scabbard slam pulverizing brittle bone spears with a thunderous shockwave and searing dark flame", "duration_seconds": 3.2, "gain_db": 2.0, "note": "嘭咔嚓！陆烬连刀带鞘一击横拍震碎八根准三阶蜘蛛骨刺"},
                {"p": 20, "pos": "before", "motif_id": "motif_qi_sea_shatter", "slug": "aohuan_false_core_shatter_crash", "gain_db": 1.5, "note": "噗！雷火寸劲震碎鳌桓斑驳假丹撞塌十丈珊瑚石牌坊"},
                {"p": 52, "pos": "before", "slug": "abyssal_sabre_clash_spatial_water", "sfx_prompt": "Heavy broadsword clashing against a warping underwater vortex current and smashing into submerged black stone peaks", "duration_seconds": 3.4, "gain_db": 1.5, "note": "铛轰隆！深海三千丈断岳硬撼裂空鲲兽折叠水幕"},
                {"p": 66, "pos": "before", "slug": "blade_moon_pierce_leviathan_scale", "sfx_prompt": "Blazing heavy broadsword cleaving through thick armored leviathan scales in deep water with a massive pressurized shockwave", "duration_seconds": 3.4, "gain_db": 2.0, "note": "噗嗤！十丈紫黑暗金刀月一刀贯穿裂空鲲兽胸腔逆鳞"},
            ],
        )
        j54, m54 = save_episode_scripts(s54, REPO_SCRIPTS_DIR, registry)
        built.append(("E054", s54, j54, m54))

        # =====================================================================
        # E055 · 第55章 第二阶基因锁开！周天星窍，无瑕金丹成！ (68 paras, 10 quotes)
        # =====================================================================
        md_55 = SOURCE_DIR / "第55章_第二阶基因锁开！周天星窍，无瑕金丹成！.md"
        s55 = compile_episode_cue_sheet(
            episode_id="E055",
            chapter_number=55,
            source_md_path=_prepare_chapter_md(md_55, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_55.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_three_true_bloods_flesh_crucible",
                    "start_p": 1,
                    "title": "第一幕 · 三血焚五脏，碎骨铸新躯",
                    "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act2_suppress_spine_shadow_second_genelock",
                    "start_p": 18,
                    "title": "第二幕 · 零号镇椎影，二阶破命锁",
                    "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                    "bgm_duration_s": 105.0,
                },
                {
                    "act_id": "act3_star_acupoints_flawless_golden_core",
                    "start_p": 42,
                    "title": "第三幕 · 星窍三百六，一转成真丹",
                    "bgm_prompt": WORLD_OST["w3_sea_prison_rising_land"],
                    "bgm_duration_s": 105.0,
                },
                {
                    "act_id": "act4_physical_body_enters_xujie_first_time",
                    "start_p": 60,
                    "title": "第四幕 · 界源裹血肉，真身踏墟荒",
                    "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                    "bgm_duration_s": 85.0,
                },
            ],
            acoustic_ranges=[(1, 68, "vast_hall")],
            skip_onomatopoeia_paras={1, 10, 19, 28, 32, 45, 61},
            dialogue_specs=[
                {"match": "第一阶基因锁破开的是感官阈值与神经反射", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬盘膝赤红火岩凝视三团异血沉声自语"},
                {"match": "烬儿，刀要够重，握刀的人骨头就得比刀更硬", "role_id": "lu_qingcang", "tags": "[dramatically] [calmly]", "stability": 0.5, "space": "memory_echo", "note": "陆烬脑海回响四年前北渊祠堂养父陆擎苍教刀叮嘱"},
                {"match": "谁！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "大椎穴深处凶戾潜影趁肉身重组异动，陆烬刀意暴起厉喝"},
                {"match": "不管你是什么东西，藏在谁的骨头里", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "零号铭牌幽光震荡，陆烬冷喝镇压大椎潜影"},
                {"match": "这具躯壳姓陆，我的刀往哪儿劈", "role_id": "lu_jin", "tags": "[fiercely] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬带血冷喝引焚锁妖煞火重锤砸回潜影"},
                {"match": "大椎骨髓里果然藏着古怪", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬记下脊柱潜影隐患留待日后清算"},
                {"match": "雷鹏铸速，冥凰涅髓，裂空承渊，灵肉重构", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬双手结印暴喝冲击第二阶基因锁"},
                {"match": "古修典籍常言，金丹大道难在精气神同炉不毁", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.5, "space": "vast_hall", "note": "三百六十五星窍洞开，陆烬趁势凝聚古法真丹"},
                {"match": "三十里无死角神识，一转无瑕金丹", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "无瑕金丹功成神识暴涨三十里"},
                {"match": "老伙计，当年爹用你镇守北渊三千里风雪", "role_id": "lu_jin", "tags": "[softly] [fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬握起断岳重刀誓赴黑渊海狱救父"},
            ],
            sfx_blueprint=[
                {"p": 1, "pos": "before", "slug": "shatter_three_jade_caskets", "sfx_prompt": "Three cold jade boxes shattering simultaneously under palm strikes with crackling lightning, dark flame, and deep ocean resonance", "duration_seconds": 3.0, "gain_db": 1.5, "note": "咔嚓！三只白玉寒匣同时拍碎，三团真灵本源悬空"},
                {"p": 10, "pos": "before", "slug": "three_true_bloods_internal_eruption", "sfx_prompt": "Deep volcanic magma rumble and crackling electrical arcs surging intensely inside a stone chamber", "duration_seconds": 3.4, "gain_db": 1.5, "note": "轰隆！三大跨界真血如火山引爆冲刷筋骨血髓"},
                {"p": 32, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "second_genelock_chains_shatter", "gain_db": 2.0, "note": "咔嚓！第二阶基因锁灵肉重构正式破开，三百六十五星窍洞开"},
                {"p": 45, "pos": "before", "slug": "flawless_golden_core_bell_chime", "sfx_prompt": "Subterranean volcanic rock tremor culminating in a pure transcendent ancient bronze-and-gold bell resonance", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆！精气神三宝合一，古法一转无瑕金丹凝成"},
                {"p": 61, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "physical_body_drawn_into_xujie", "gain_db": 1.5, "note": "嗡！方寸墟界银白界源光芒透体而出将陆烬现世真身摄入墟界"},
            ],
        )
        j55, m55 = save_episode_scripts(s55, REPO_SCRIPTS_DIR, registry)
        built.append(("E055", s55, j55, m55))

        # =====================================================================
        # E056 · 第56章 真身首入墟界！第五环石林的基因秘辛 (62 paras, 16 quotes)
        # =====================================================================
        md_56 = SOURCE_DIR / "第56章_真身首入墟界！第五环石林的基因秘辛.md"
        s56 = compile_episode_cue_sheet(
            episode_id="E056",
            chapter_number=56,
            source_md_path=_prepare_chapter_md(md_56, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_56.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_true_body_three_step_verification",
                    "start_p": 1,
                    "title": "第一幕 · 冻土留真印，洞天携物归",
                    "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act2_fifth_ring_chen_xuan_bone_testament",
                    "start_p": 15,
                    "title": "第二幕 · 雾开第五环，试锁三千骨",
                    "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                    "bgm_duration_s": 115.0,
                },
                {
                    "act_id": "act3_gift_zhenyue_three_turns_golden_core",
                    "start_p": 46,
                    "title": "第三幕 · 为父收镇岳，石林证三转",
                    "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act4_return_ocean_intercept_prison_ship",
                    "start_p": 58,
                    "title": "第四幕 · 神识锁骨舰，借船赴黑渊",
                    "bgm_prompt": WORLD_OST["w3_abyssal_sea_desolation"],
                    "bgm_duration_s": 80.0,
                },
            ],
            acoustic_ranges=[
                (1, 9, "vast_hall"),
                (10, 14, "dry"),
                (15, 57, "vast_hall"),
                (58, 62, "dry"),
            ],
            skip_onomatopoeia_paras={1, 38, 52},
            dialogue_specs=[
                {"match": "金丹成道，二阶基因锁重构灵肉", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬真身立于第九环荒原核验随身重刀与储物戒"},
                {"match": "出！", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬握万年玄冰心念一动回归现世"},
                {"match": "能进，能出，随身储物戒不受排斥", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.5, "space": "dry", "note": "陆烬见万年玄冰成功带回现世火山岩"},
                {"match": "而且墟界三刻钟对应现世一刻钟的三倍时差依旧存在", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬核验三倍时差与每日两时辰真身停留时限"},
                {"match": "太上大司命亲手封禁的葬仙狱", "role_id": "zhao_kui", "speaker_name": "鹤阴散人", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "memory_echo", "note": "陆烬回想第六环夺舍老怪鹤阴散人临死前的惊恐尖叫"},
                {"match": "答案就在前面几环里", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬提刀迈向第六环尽头灰雾"},
                {"match": "这不是寻常修仙阵纹，这是……生灵血肉最底层的生命基因图谱", "role_id": "lu_jin", "tags": "[gasps] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬仰望第五环石柱上的暗金神血双螺旋图谱震撼明悟"},
                {"match": "吾乃太上试锁院第七十二代执剑使陈玄", "role_id": "weathered_elder_npc", "speaker_name": "陈玄", "tags": "[dramatically] [hoarsely]", "stability": 0.5, "space": "memory_echo", "note": "第五环主碑前先贤陈玄暗金骨简神念炸响"},
                {"match": "世人皆被天外欺瞒，以为血脉五锁乃天生残缺之厄", "role_id": "weathered_elder_npc", "speaker_name": "陈玄", "tags": "[dramatically]", "stability": 0.5, "space": "memory_echo", "note": "陈玄骨书揭开太初大寂灭与原初始祖设五重基因护道锁秘辛"},
                {"match": "奈何天外【司命仙庭】叛道窃权，篡改万界母碑", "role_id": "weathered_elder_npc", "speaker_name": "陈玄", "tags": "[angry] [dramatically]", "stability": 0.0, "space": "memory_echo", "note": "陈玄痛斥司命仙庭加装世界母锁圈养诸界"},
                {"match": "仙庭所传伪法，名为灵脉品阶，实为催熟奴印", "role_id": "weathered_elder_npc", "speaker_name": "陈玄", "tags": "[hoarsely] [dramatically]", "stability": 0.0, "space": "memory_echo", "note": "陈玄泣血道出试锁院三千同道二千九百九十九人爆体证出的唯一破局生路"},
                {"match": "原来基因锁本是护佑苍生拾级而上的阶梯", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "space": "vast_hall", "note": "陆烬贯通前两卷所有谜团看透司命仙庭牧场本质"},
                {"match": "既然路是对的，那就一阶一阶把这死锁全劈开", "role_id": "lu_jin", "tags": "[fiercely] [calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬吐出浊气立下劈碎五锁登天斩牧神之志"},
                {"match": "匣中三钉名曰【破邪镇骨钉】", "role_id": "weathered_elder_npc", "speaker_name": "陈玄", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "陈玄第三枚骨简说明遗赠破邪镇骨钉与三阶阔刀镇岳"},
                {"match": "爹那把老黑刀早砍卷了刃，这柄三阶【镇岳】正合他", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬抚过二百一十斤镇岳阔刀为独臂养父收好佩兵"},
                {"match": "正好借你们的船，带路去接我爹", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.5, "space": "dry", "note": "陆烬神识锁死海面押运骨舰化潜流追击"},
            ],
            sfx_blueprint=[
                {"p": 1, "pos": "before", "slug": "boots_crunch_frozen_gravel", "sfx_prompt": "Heavy leather combat boots crunching firmly onto frozen gravel in a cold desolate wasteland wind", "duration_seconds": 2.4, "gain_db": 1.0, "note": "咯吱！陆烬真身战靴踩碎方寸墟界冻土砂砾"},
                {"p": 20, "pos": "before", "slug": "fifth_ring_fog_part_monoliths", "sfx_prompt": "Deep ancient stone resonance as dense mystic fog parts slowly to reveal towering monoliths", "duration_seconds": 3.4, "gain_db": 1.5, "note": "第五环浓稠灰雾共鸣分开，三百六十根双螺旋血纹巨柱显现"},
                {"p": 38, "pos": "before", "slug": "bone_slip_crumble_stardust", "sfx_prompt": "Crisp dry snap of an ancient bone tablet crumbling into shimmering golden dust in a quiet stone hall", "duration_seconds": 2.2, "gain_db": 1.0, "note": "啪嗒！陈玄第一枚暗金骨简读毕化作金光消散"},
                {"p": 50, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "caress_zhenyue_heavy_broadsword", "gain_db": 1.0, "note": "陆烬伸手抚过二百一十斤三阶玄铁阔刀镇岳"},
                {"p": 52, "pos": "before", "slug": "three_hundred_pillars_qi_vortex", "sfx_prompt": "Three hundred stone pillars humming in unison as a roaring vortex of spiritual energy pours downward", "duration_seconds": 3.6, "gain_db": 1.5, "note": "轰隆隆！三百六十根黑石柱引动古灵源气助陆烬晋升金丹三转"},
            ],
        )
        j56, m56 = save_episode_scripts(s56, REPO_SCRIPTS_DIR, registry)
        built.append(("E056", s56, j56, m56))

        # =====================================================================
        # E057 · 第57章 夜袭黑渊海狱，阔别四载父子重逢！ (76 paras, 16 quotes)
        # =====================================================================
        md_57 = SOURCE_DIR / "第57章_夜袭黑渊海狱，阔别四载父子重逢！.md"
        s57 = compile_episode_cue_sheet(
            episode_id="E057",
            chapter_number=57,
            source_md_path=_prepare_chapter_md(md_57, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_57.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_infiltrate_abyssal_sea_prison",
                    "start_p": 1,
                    "title": "第一幕 · 贴骨潜魔窟，三百无骨囚",
                    "bgm_prompt": WORLD_OST["w3_abyssal_sea_desolation"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act2_unbending_backbone_on_cross_rack",
                    "start_p": 15,
                    "title": "第二幕 · 断臂悬刑架，铮铮北渊骨",
                    "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                    "bgm_duration_s": 110.0,
                },
                {
                    "act_id": "act3_dome_shatters_heavenly_sabre_descends",
                    "start_p": 40,
                    "title": "第三幕 · 破穹降惊雷，一刀退狱主",
                    "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act4_four_years_father_son_reunion",
                    "start_p": 55,
                    "title": "第四幕 · 双手奉旧刀，接爹回北渊",
                    "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                    "bgm_duration_s": 115.0,
                },
            ],
            acoustic_ranges=[(9, 76, "vast_hall")],
            skip_onomatopoeia_paras={27, 41, 46, 50, 71, 74},
            dialogue_specs=[
                {"match": "姓陆的外海硬骨头，在老夫这毒水池子里整整熬了一年", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[hoarsely] [coldly]", "stability": 0.0, "space": "vast_hall", "note": "血骨狱主托着三阶噬魂魔鳗骨居高临下冷笑"},
                {"match": "海皇陛下万仙大祭在即，爱惜你这身罕见的气血底子", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[coldly] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "血骨狱主用冰冷骨尖拍陆擎苍脸颊逼其剖背种骨"},
                {"match": "若是再敢不识抬举", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "血骨狱主竖瞳寒光一闪威胁"},
                {"match": "本座今日便当着你的面，把跟着你逃难来的那三十几个", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[angry] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "血骨狱主拿外海老弱妇孺点天灯相胁"},
                {"match": "呸！少拿这套下三滥的把戏吓唬你陆爷爷", "role_id": "lu_qingcang", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍血痰啐在血骨狱主战靴上洪钟怒骂"},
                {"match": "老子在大苍不跪血月，在永夜不拜骨灯", "role_id": "lu_qingcang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍宁死不植半寸妖魔烂肉"},
                {"match": "至于你们这群人不人鬼不鬼的寄生虫豸", "role_id": "lu_qingcang", "tags": "[laughs] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍桀骜冷笑深信儿子早晚提刀杀穿苦海"},
                {"match": "好！好得很！死到临头还做梦指望你那不知死在哪界", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[angry] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "血骨狱主怒极反笑"},
                {"match": "左右副使听令，把这泥胎的脖子给本座死死按在铁桩上", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "血骨狱主下令活剖陆擎苍脊椎硬钉魔鳗骨"},
                {"match": "遵狱主令！", "role_id": "li_cang", "speaker_name": "海狱副使", "tags": "[coldly] [shouting]", "stability": 0.5, "space": "vast_hall", "note": "两名金丹初期副狱使狞笑领命上前压肩"},
                {"match": "什么人！", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "玄铁穹顶炸裂暗金刀虹天降，血骨狱主骇然惊呼"},
                {"match": "烬……烬儿？", "role_id": "lu_qingcang", "tags": "[trembling] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍认出断岳重刀与儿子背影，嘴唇哆嗦沙哑轻唤"},
                {"match": "爹，北渊的血月笼子我劈了，永夜的古井我也闯过来了", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.0, "space": "vast_hall", "note": "陆烬眼眶微红双手平托断岳重刀递向养父"},
                {"match": "儿子来晚了，接你回家", "role_id": "lu_jin", "tags": "[softly] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "阔别四载父子重逢最催泪誓言"},
                {"match": "好！好小子！真是老子的好儿子", "role_id": "lu_qingcang", "tags": "[laughs] [crying]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍热泪夺眶独臂重拍儿子肩膀仰天狂喜大笑"},
                {"match": "原来是父子两个无骨孽障！已经晚了", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "血骨狱主捏碎传讯骨螺开启万钧沉渊大阵自毁"},
            ],
            sfx_blueprint=[
                {"p": 27, "pos": "before", "slug": "iron_chains_rattle_cross_rack", "sfx_prompt": "Heavy barbed iron chains rattling violently against a dark iron cross rack in a stone dungeon", "duration_seconds": 2.6, "gain_db": 1.5, "note": "哗啦！十字刑架剧烈晃动，陆擎苍猛然抬头"},
                {"p": 41, "pos": "before", "slug": "iron_dome_explode_sabre_descent", "sfx_prompt": "Three-foot-thick iron dungeon dome exploding inward under a thunderous descending broadsword energy slash", "duration_seconds": 3.6, "gain_db": 2.5, "note": "轰隆！头顶海狱玄铁穹顶炸裂，陆烬十丈暗金刀虹天降斩杀二副使"},
                {"p": 50, "pos": "before", "slug": "sabre_shatter_eel_bone_smash_wall", "sfx_prompt": "Colossal broadsword impact snapping thick bone armor and blasting a heavy body through a stone cavern wall", "duration_seconds": 3.4, "gain_db": 2.0, "note": "铛咔嚓！断岳劈断三阶魔鳗骨将血骨狱主轰进三丈海岩壁"},
                {"p": 53, "pos": "before", "slug": "eight_qi_threads_sever_chains", "sfx_prompt": "Eight crisp rapid metallic pings as razor-thin blade threads cleanly sever heavy iron chains", "duration_seconds": 2.6, "gain_db": 1.5, "note": "叮叮当当！八缕暗金刀丝削断锁魂寒铁链"},
                {"p": 71, "pos": "before", "slug": "rock_pile_erupt_debris", "sfx_prompt": "Subterranean stone wall rubble exploding outward in a spray of dark gravel and water", "duration_seconds": 2.5, "gain_db": 1.5, "note": "轰隆！坍塌海岩壁深坑炸开，血骨狱主爬出"},
                {"p": 74, "pos": "before", "slug": "bone_conch_shatter_infrasound_alarm", "sfx_prompt": "Brittle bone conch shell crushing followed by an eerie low-frequency underwater resonance alarm and rumbling stone pillars", "duration_seconds": 3.6, "gain_db": 1.5, "note": "嗡嗡嗡！海皇传讯骨螺捏碎，九百根阵柱亮起自毁红光"},
            ],
        )
        j57, m57 = save_episode_scripts(s57, REPO_SCRIPTS_DIR, registry)
        built.append(("E057", s57, j57, m57))

        # =====================================================================
        # E058 · 第58章 父子双刀破海狱，陆擎苍的跨界见闻 (68 paras, 26 quotes)
        # =====================================================================
        md_58 = SOURCE_DIR / "第58章_父子双刀破海狱，陆擎苍的跨界见闻.md"
        s58 = compile_episode_cue_sheet(
            episode_id="E058",
            chapter_number=58,
            source_md_path=_prepare_chapter_md(md_58, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_58.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_gift_zhenyue_ten_strokes_slay_warden",
                    "start_p": 1,
                    "title": "第一幕 · 赠父镇岳刃，十招斩血骨",
                    "bgm_prompt": WORLD_OST["shared_tactical_ambush_kill"],
                    "bgm_duration_s": 110.0,
                },
                {
                    "act_id": "act2_father_son_twin_sabres_break_prison",
                    "start_p": 32,
                    "title": "第二幕 · 双刀十字斩，骨舰冲黑渊",
                    "bgm_prompt": WORLD_OST["w3_sea_prison_rising_land"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act3_heal_old_wound_father_golden_core",
                    "start_p": 42,
                    "title": "第三幕 · 息壤补旧伤，独臂证金丹",
                    "bgm_prompt": WORLD_OST["shared_calm_aftermath_planning"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act4_cliffside_wine_eighteen_year_origin_secret",
                    "start_p": 51,
                    "title": "第四幕 · 篝火饮烈酒，天渊素手秘",
                    "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                    "bgm_duration_s": 115.0,
                },
            ],
            acoustic_ranges=[
                (1, 41, "vast_hall"),
                (59, 60, "mental_realm"),
            ],
            skip_onomatopoeia_paras={1, 7, 28, 58},
            dialogue_specs=[
                {"match": "儿子，把刀收回去", "role_id": "lu_qingcang", "tags": "[shouting]", "stability": 0.5, "space": "vast_hall", "note": "陆擎苍独臂按住断岳刀背推回陆烬掌中"},
                {"match": "这把【断岳】跟着你连闯两界", "role_id": "lu_qingcang", "tags": "[fiercely] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍豪迈不夺儿子本命兵刃"},
                {"match": "铁棍没有，从上古先贤遗迹带出来的二百一十斤", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬反手将二百一十斤三阶镇岳阔刀拍入父亲独掌"},
                {"match": "好沉的刀！痛快！今日咱们爷俩双刀开路", "role_id": "lu_qingcang", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍扣住镇岳刀意冲霄朗声狂笑"},
                {"match": "爹去劈开上层矿坑铁门带人先登舰", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬分兵独战金丹中期血骨狱主"},
                {"match": "狂妄小辈！真当本座方才大意被你偷袭一刀", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "血骨狱主燃烧三阶寄生母骨施展血翼天魔解体"},
                {"match": "在真正的无瑕金丹面前，你这身靠妖魔菌丝催肥的烂骨头", "role_id": "lu_jin", "tags": "[coldly] [fiercely]", "stability": 0.0, "space": "vast_hall", "note": "陆烬全开二阶基因锁与周天星窍战诀"},
                {"match": "怎么可能！你才金丹初期，哪来这等怪物般的肉身气力", "role_id": "chiyang_laozu", "speaker_name": "血骨狱主", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "vast_hall", "note": "八刀削断猩红骨翼，血骨狱主魂飞魄散欲逃"},
                {"match": "第九招，《惊神刺》！", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬三十里金丹神识成锤轰碎血骨狱主识海菌丝"},
                {"match": "北渊的弟兄、永夜的汉子，还有苦海不肯弯腰的硬骨头们", "role_id": "lu_qingcang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍独臂抡镇岳劈碎寒铁大闸高呼突围"},
                {"match": "是陆司主！还有少主杀来了", "role_id": "shi_meng", "speaker_name": "北渊旧卒", "tags": "[shouting] [crying]", "stability": 0.0, "space": "vast_hall", "note": "矿坑内北渊镇渊司旧部激动高呼"},
                {"match": "跟陆前辈冲出去！", "role_id": "male_disciple_a", "speaker_name": "无骨义士", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三百二十名无骨义士涌上百丈押运骨舰"},
                {"match": "爹，合刀破阵！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "船头父子并肩高举断岳与镇岳"},
                {"match": "好！", "role_id": "lu_qingcang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆擎苍应声与儿子双刀合璧十字斩破大阵"},
                {"match": "痛快！四年没喝过这么舒心的酒了", "role_id": "lu_qingcang", "tags": "[laughs] [sighs]", "stability": 0.5, "space": "dry", "note": "红珊秘岛海崖篝火旁，新晋金丹的陆擎苍与儿子碰碗豪饮"},
                {"match": "爹，当年祠堂地下你留给我的血玉简我都看了", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "dry", "note": "陆烬借火光轻声询问十八年前天渊抱婴往事"},
                {"match": "那件事，爹烂在肚子里十八年", "role_id": "lu_qingcang", "tags": "[calmly] [sighs]", "stability": 0.5, "space": "dry", "note": "陆擎苍神色肃穆望向漆黑海天缓缓开口"},
                {"match": "十八年前十月初九，我追杀一头寒渊妖狼", "role_id": "lu_qingcang", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆擎苍追忆十八年前血月食日之夜"},
                {"match": "就在那片死寂里，离地十丈高的半空中", "role_id": "lu_qingcang", "tags": "[dramatically] [softly]", "stability": 0.0, "space": "dry", "note": "陆擎苍道出金色裂缝后探出的结霜染血女子素手"},
                {"match": "裂缝那一头似乎正在经历毁天灭地的大战", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.5, "space": "dry", "note": "陆擎苍讲述染血素手将无脐婴孩与零号铜牌推落天渊"},
                {"match": "我抱起你一看，你天生连肚脐眼都没有", "role_id": "lu_qingcang", "tags": "[softly] [sighs]", "stability": 0.5, "space": "dry", "note": "陆擎苍摩挲酒碗道出十八年撑伞父爱誓言"},
                {"match": "不管那道裂缝后面是谁，生恩不及养恩重", "role_id": "lu_jin", "tags": "[softly] [calmly]", "stability": 0.5, "space": "dry", "note": "陆烬温声认父：这辈子就只有你一个爹"},
                {"match": "叙旧的话往后有的是工夫说，眼下这片苦海要出塌天大祸了", "role_id": "lu_qingcang", "tags": "[fiercely] [dramatically]", "stability": 0.0, "space": "dry", "note": "陆擎苍拍案揭露殖骨海皇三天内开启万仙献骨大祭"},
                {"match": "一旦大祭发动，三十六岛上百万植入了仙骨的修士", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.0, "space": "dry", "note": "陆擎苍告知万骨母坛下镇压着天外魔物触须与第四界通道"},
                {"match": "只有三天么，足够了", "role_id": "lu_jin", "tags": "[coldly] [calmly]", "stability": 0.5, "space": "dry", "note": "陆烬霍然起身目光锁定上千块深海万年灵髓"},
                {"match": "爹，替我在石洞外护法两日", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "dry", "note": "陆烬决定闭关两日冲金丹后期、开第四环再斩海皇"},
            ],
            sfx_blueprint=[
                {"p": 1, "pos": "before", "slug": "undersea_prison_collapse_flood", "sfx_prompt": "Colossal underwater cavern cracking open with roaring abyssal currents and falling boulders", "duration_seconds": 3.5, "gain_db": 1.5, "note": "轰隆隆！黑渊海狱倾斜崩塌，万丈深海重水倒灌"},
                {"p": 7, "pos": "before", "slug": "zhenyue_heavy_broadsword_unsheathe", "sfx_prompt": "Heavy two-hundred-pound ancient dark iron broadsword materializing with a deep metallic clang", "duration_seconds": 2.4, "gain_db": 1.5, "note": "铿！二百一十斤三阶镇岳重阔刀显现拍入陆擎苍独掌"},
                {"p": 28, "pos": "before", "slug": "tenth_slash_cleave_warden_ash", "sfx_prompt": "Devastating vertical broadsword cleave followed by roaring violet flames reducing bone armor to ash", "duration_seconds": 3.2, "gain_db": 2.0, "note": "噗嗤轰！第十刀垂直劈裂血骨狱主，妖煞火将其焚为灰烬"},
                {"p": 41, "pos": "before", "slug": "twin_sabres_cross_cleave_dome", "sfx_prompt": "Two colossal broadsword energy arcs crossing in an X-slash, shattering a massive barrier as a giant ship surges upward through ocean waves", "duration_seconds": 4.0, "gain_db": 2.0, "note": "轰隆！父子断岳镇岳十字合斩劈穿万骨噬灵大阵冲出海面"},
                {"p": 51, "pos": "before", "slug": "cliffside_campfire_ceramic_bowls_clink", "sfx_prompt": "Crackling coastal driftwood campfire with ocean breeze and two coarse ceramic wine bowls clinking crisply", "duration_seconds": 3.0, "gain_db": 1.0, "note": "海崖绝顶柴火噼啪，父子粗陶酒碗重重相碰"},
                {"p": 58, "pos": "before", "motif_id": "motif_frost_coffin_knock", "slug": "frost_wrist_memory_coffin_hum", "gain_db": 1.0, "note": "轰！听闻结霜染血女子素手，第一环玄霜古棺发出轻冷嗡鸣"},
            ],
        )
        j58, m58 = save_episode_scripts(s58, REPO_SCRIPTS_DIR, registry)
        built.append(("E058", s58, j58, m58))

        # =====================================================================
        # E059 · 第59章 金丹六转破中境，第四环坠星古宗！ (70 paras, 14 quotes)
        # =====================================================================
        md_59 = SOURCE_DIR / "第59章_金丹六转破中境，第四环坠星古宗！.md"
        s59 = compile_episode_cue_sheet(
            episode_id="E059",
            chapter_number=59,
            source_md_path=_prepare_chapter_md(md_59, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_59.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_father_guards_cave_enter_xujie",
                    "start_p": 1,
                    "title": "第一幕 · 慈父横刀守，千髓堆墟山",
                    "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                    "bgm_duration_s": 85.0,
                },
                {
                    "act_id": "act2_devour_thousand_marrows_seven_turns_core",
                    "start_p": 9,
                    "title": "第二幕 · 星窍吞灵河，六日证七转",
                    "bgm_prompt": WORLD_OST["w3_sea_prison_rising_land"],
                    "bgm_duration_s": 105.0,
                },
                {
                    "act_id": "act3_fourth_ring_fallen_star_palace_gate",
                    "start_p": 30,
                    "title": "第三幕 · 雾辟镇狱门，帝篆书太上",
                    "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                    "bgm_duration_s": 100.0,
                },
                {
                    "act_id": "act4_faceless_mural_frost_coffin_sword_cry",
                    "start_p": 48,
                    "title": "第四幕 · 无面司命画，古棺铮剑鸣",
                    "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                    "bgm_duration_s": 110.0,
                },
            ],
            acoustic_ranges=[
                (1, 5, "dry"),
                (6, 70, "vast_hall"),
            ],
            skip_onomatopoeia_paras={13, 24, 32, 37, 61, 63},
            dialogue_specs=[
                {"match": "洞外有爹和三百弟兄替你守着", "role_id": "lu_qingcang", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "石洞外陆擎苍横搁镇岳阔刀为儿子护法"},
                {"match": "归墟海眼那头老怪物攒了上千年的家底", "role_id": "lu_qingcang", "tags": "[fiercely] [calmly]", "stability": 0.5, "space": "dry", "note": "陆擎苍沉声叮嘱儿子安心把修为推到顶"},
                {"match": "好，爹多保重", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "陆烬抱拳应声步入方寸墟界"},
                {"match": "现世两日，在墟界之内便是足足六日", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "第八环空地陆烬凝视一千二百块深海万年灵髓"},
                {"match": "《周天星窍战诀》，鲸吞", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "陆烬焚尽惰性浊气开启三百六十五星窍鲸吞灵河"},
                {"match": "中三转已满，还不破入上三转更待何时", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "第五日陆烬挟剩余三百块髓心精粹强冲金丹上三转"},
                {"match": "金丹七转，再加上二阶基因锁与三百六十五星窍", "role_id": "lu_jin", "tags": "[calmly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "金丹七转功成，神识暴涨至方圆七十里"},
                {"match": "也是时候看看，这第四环里究竟藏着什么上古旧事了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬提断岳迈向第五环尽头浓雾"},
                {"match": "宁断镇狱骨，不作牧神奴，凡入此门者，当持斩天心", "role_id": "ancient_construct_echo", "speaker_name": "镇狱石座古训", "tags": "[dramatically] [coldly]", "stability": 1.0, "space": "vast_hall", "note": "第四环三十丈青铜宫门白玉神兽石座古训"},
                {"match": "验明……零号火种血契……金丹上三转", "role_id": "ancient_construct_echo", "speaker_name": "镇狱阵枢残音", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "门廊上方残破阵法晶石耗尽最后灵力传出古老准入残音"},
                {"match": "第六环囚笼里的鹤阴散人死前喊过太上大司命", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬凝视半块太上镇狱紫金牌匾串联线索"},
                {"match": "这座残破小世界在被打碎之前，莫非便是上古那座", "role_id": "lu_jin", "tags": "[softly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "陆烬踏上九十九级染血玉阶步入太上镇狱主殿"},
                {"match": "好重的一缕寒霜恨意，连隔着三道界环看一眼这具无脸背影", "role_id": "lu_jin", "tags": "[coldly] [whispers]", "stability": 0.5, "space": "vast_hall", "note": "陆烬低头看着脚尖前三寸被第一环古棺剑气凝出的惨白冰花"},
                {"match": "顾", "role_id": "ancient_construct_echo", "speaker_name": "司命残印古篆", "tags": "[coldly] [dramatically]", "stability": 1.0, "space": "vast_hall", "note": "半枚染血玄黑大印底部铁画银钩的苍劲古篆顾字"},
            ],
            sfx_blueprint=[
                {"p": 13, "pos": "before", "slug": "liquid_essence_waterfall_pour", "sfx_prompt": "Roaring cascade of luminous liquid energy pouring downward like a waterfall with deep resonant thunder", "duration_seconds": 3.4, "gain_db": 1.5, "note": "轰隆隆！上千块万年海髓化作湛蓝灵河倒灌三百六十五星窍"},
                {"p": 24, "pos": "before", "slug": "seventh_turn_golden_core_chime", "sfx_prompt": "Piercing transcendent bronze-and-jade bell chime echoing with immense spiritual shockwave", "duration_seconds": 3.2, "gain_db": 2.0, "note": "嗡！大道钟鸣炸响，第七道太古星纹烙印，金丹七转功成"},
                {"p": 37, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "push_open_zhenyu_bronze_gates", "gain_db": 2.0, "note": "嘎吱轰！陆烬推开三十丈青铜宫门解锁第四环坠星古宗"},
                {"p": 61, "pos": "before", "slug": "heart_throb_heavy_pulse", "sfx_prompt": "Single deep heavy heartbeat thud echoing tensely inside a silent stone hall", "duration_seconds": 2.0, "gain_db": 1.5, "note": "咚！凝视壁画无脸黑衣大司命剑痕，陆烬心脏骤抽"},
                {"p": 63, "pos": "before", "slug": "frost_coffin_sword_cry_ice_flower", "sfx_prompt": "Piercing icy sword ring echoing from afar followed by crisp frost crystallizing rapidly on white jade stone", "duration_seconds": 3.5, "gain_db": 2.0, "note": "铮！第一环玄霜古棺剑鸣穿透壁垒在陆烬脚尖前凝出惨白冰花"},
            ],
        )
        j59, m59 = save_episode_scripts(s59, REPO_SCRIPTS_DIR, registry)
        built.append(("E059", s59, j59, m59))

        # =====================================================================
        # E060 · 第60章 三十六岛万骨潮，只身独刀赴归墟 (66 paras, 15 quotes)
        # =====================================================================
        md_60 = SOURCE_DIR / "第60章_三十六岛万骨潮，只身独刀赴归墟.md"
        s60 = compile_episode_cue_sheet(
            episode_id="E060",
            chapter_number=60,
            source_md_path=_prepare_chapter_md(md_60, tmp_dir),
            source_rel_path=f"02_分章精修正文/{md_60.name}",
            registry=registry,
            acts_blueprint=[
                {
                    "act_id": "act1_star_iron_reforge_duanyue_sabre",
                    "start_p": 1,
                    "title": "第一幕 · 千拳锻星铁，断岳重三百六",
                    "bgm_prompt": WORLD_OST["shared_xujie_shattered_realm"],
                    "bgm_duration_s": 105.0,
                },
                {
                    "act_id": "act2_mother_bell_tolls_ten_thousand_bone_tide",
                    "start_p": 26,
                    "title": "第二幕 · 母钟勾万魂，三十六岛投海",
                    "bgm_prompt": WORLD_OST["shared_boss_overwhelming_pressure"],
                    "bgm_duration_s": 100.0,
                },
                {
                    "act_id": "act3_father_guards_outer_sea_wine_pact",
                    "start_p": 42,
                    "title": "第三幕 · 嘱父拦狂澜，备宴候归刀",
                    "bgm_prompt": WORLD_OST["w3_father_son_reunion"],
                    "bgm_duration_s": 95.0,
                },
                {
                    "act_id": "act4_lone_sabre_plunges_into_guixu_eye",
                    "start_p": 50,
                    "title": "第四幕 · 一刀斩三鲸，只身踏母坛",
                    "bgm_prompt": WORLD_OST["w3_sea_prison_rising_land"],
                    "bgm_duration_s": 105.0,
                },
            ],
            acoustic_ranges=[
                (1, 25, "vast_hall"),
                (26, 58, "dry"),
                (59, 66, "vast_hall"),
            ],
            skip_onomatopoeia_paras={16, 22, 27, 39, 51, 55, 59},
            dialogue_specs=[
                {"match": "太上镇狱大司命，姓顾。明明曾与那位白衣女帝", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬拿起供桌上刻有顾字的半枚玄黑残印"},
                {"match": "而第一环【玄霜古棺】里的寒气，与刮碎壁画的剑意同出一源", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "vast_hall", "note": "陆烬封存残印留待集齐四钥推棺见分晓"},
                {"match": "便在这镇狱殿前，重铸刀魂", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.5, "space": "vast_hall", "note": "陆烬催动金丹真火与焚锁妖煞火熔炼太上星辰铁"},
                {"match": "三百六十斤，正好配我三百六十五周天星窍", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "vast_hall", "note": "断岳晋升三百六十斤三阶中品重宝，随手一挥撕裂虚空"},
                {"match": "不好！是【归墟母钟】", "role_id": "lu_qingcang", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "dry", "note": "万里海心母钟骤响，洞外陆擎苍霍然提刀变色"},
                {"match": "烬儿，殖骨海皇那老畜生提前敲响母钟", "role_id": "lu_qingcang", "tags": "[angry] [shouting]", "stability": 0.0, "space": "dry", "note": "陆擎苍急报殖骨海皇提前发动三十六岛万仙献骨大祭"},
                {"match": "苦海无岸，血肉归渊，奉吾仙骨，得见真仙", "role_id": "eternal_night_whisper", "speaker_name": "万骨狂潮众修", "tags": "[coldly] [dramatically]", "stability": 0.5, "space": "vast_hall", "note": "数万名被菌丝接管大脑的殖骨修士赤目诡笑齐声诵念"},
                {"match": "是玄鲸岛东街的陈大叔和采珠行的姐妹们", "role_id": "a_mang", "speaker_name": "海棠", "tags": "[crying] [desperately]", "stability": 0.0, "space": "dry", "note": "秘岛海滩上海棠痛哭认出被勾魂游向海眼的底层乡邻"},
                {"match": "烬儿，点齐骨舰，爹陪你杀去归墟海眼剁了那头海皇", "role_id": "lu_qingcang", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "dry", "note": "陆擎苍独臂抡起镇岳阔刀冲上崖顶请战"},
                {"match": "不行，大船进不去！", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "dry", "note": "陆烬按住父亲肩膀果断拦阻"},
                {"match": "归墟海眼乃是万丈海底漩涡绝地，殖骨海皇是金丹大圆满", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.5, "space": "dry", "note": "陆烬冷静剖析归墟海眼凶险"},
                {"match": "那些种了低品骨的底层修士菌丝未入脑髓深处，还有救", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "dry", "note": "陆烬托付父亲与海棠驾骨舰敲镇魂鼓在百里外拦截救人"},
                {"match": "好！外围航道交给老子，谁敢越雷池一步老子劈了谁", "role_id": "lu_qingcang", "tags": "[fiercely] [laughs]", "stability": 0.0, "space": "dry", "note": "陆擎苍重拳砸在儿子胸膛立下船头温酒之约"},
                {"match": "一炷香温酒太短，爹且备好庆功宴", "role_id": "lu_jin", "tags": "[calmly] [fiercely]", "stability": 0.5, "space": "dry", "note": "陆烬豪然一笑转身背负三百六十斤断岳踏空赴海眼"},
                {"match": "本皇道是谁杀了血骨那废物，原来真有一具完美的无骨金丹道胎", "role_id": "sect_elder_antagonist", "speaker_name": "殖骨海皇", "tags": "[coldly] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "万骨母坛顶端金丹大圆满殖骨海皇俯视陆烬沙哑冷笑"},
            ],
            sfx_blueprint=[
                {"p": 16, "pos": "before", "slug": "thousand_fist_forging_star_iron", "sfx_prompt": "Rhythmic thunderous metallic forging strikes ringing out on glowing molten star-iron followed by a soaring dragon-like blade resonance", "duration_seconds": 3.8, "gain_db": 1.5, "note": "铛铛铛！陆烬以拳为锤锻打一千零八十拳重铸断岳"},
                {"p": 22, "pos": "before", "motif_id": "motif_broken_blade_wipe", "slug": "three_hundred_sixty_jin_sabre_rip_void", "gain_db": 1.5, "note": "嗡！三百六十斤三阶重宝断岳随手一挥撕裂虚空"},
                {"p": 27, "pos": "before", "slug": "guixu_mother_bell_abyssal_tolls", "sfx_prompt": "Three colossal ominous deep underwater bone-bell tolls rolling across a boiling stormy ocean", "duration_seconds": 4.0, "gain_db": 2.0, "note": "咚咚咚！万里中心归墟母钟轰然敲响，海水沸腾"},
                {"p": 39, "pos": "before", "slug": "thousands_plunge_into_stormy_sea", "sfx_prompt": "Countless heavy water splashes plunging one after another from high cliffs into churning ocean waves", "duration_seconds": 3.2, "gain_db": 1.0, "note": "扑通！三十六岛数万殖骨修士跳海汇成万骨狂潮"},
                {"p": 55, "pos": "before", "slug": "single_slash_bisect_three_bone_whales", "sfx_prompt": "Blazing thirty-yard broadsword energy arc cleaving cleanly through three giant armored bone-whales mid-air above stormy waves", "duration_seconds": 3.4, "gain_db": 2.0, "note": "刷！三十丈星河刀罡一刀两断三头三阶护法骨鲸"},
                {"p": 59, "pos": "before", "slug": "meteor_plunge_crush_abyssal_seabed", "sfx_prompt": "Supersonic descent through a roaring ten-mile ocean whirlpool culminating in heavy boots shattering black seabed rock", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆！陆烬孤身杀入万丈归墟海眼踏碎海底黑岩"},
            ],
        )
        j60, m60 = save_episode_scripts(s60, REPO_SCRIPTS_DIR, registry)
        built.append(("E060", s60, j60, m60))

    return built


if __name__ == "__main__":
    items = build_all_batch10()
    for ep_id, sheet, jp, mp in items:
        d_cnt = sum(1 for c in sheet.cues if c.kind == "dialogue" and c.role_id != "narrator")
        n_cnt = sum(1 for c in sheet.cues if c.kind == "dialogue" and c.role_id == "narrator")
        s_cnt = sum(1 for c in sheet.cues if c.kind == "sfx")
        print(
            f"[COMPILED & VALIDATED] {ep_id} | acts={len(sheet.acts)} | "
            f"cues={len(sheet.cues)} (narr={n_cnt}, char={d_cnt}, sfx={s_cnt}) | {jp.name}",
            flush=True,
        )
