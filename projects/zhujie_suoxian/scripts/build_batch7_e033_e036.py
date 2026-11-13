"""Build, validate, render, and archive Batch 7: Episodes E033–E036 (Chapters 33–36)."""

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


def build_all_batch7() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E033 · 第33章 慈父三载迹，筑基后期成！ (64 paras, 12 quotes)
    # =========================================================================
    md_33 = SOURCE_DIR / "第33章_慈父三载迹，筑基后期成！.md"
    s33 = compile_episode_cue_sheet(
        episode_id="E033",
        chapter_number=33,
        source_md_path=md_33,
        source_rel_path=f"02_分章精修正文/{md_33.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_secret_mechanism_blood_letter",
                "start_p": 1,
                "title": "第一幕 · 解扣入密窟，石壁见父书",
                "bgm_prompt": "Solemn emotional Chinese guqin and low cello-like erhu score inside a hidden icefall cavern, quiet fatherly sacrifice and ruthless determination, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_burn_parasite_frost_ganoderma",
                "start_p": 20,
                "title": "第二幕 · 煞火焚死虫，冰缝取寒芝",
                "bgm_prompt": "Mysterious ancient xianxia discovery music, shimmering sapphire frost-herb resonance and warm soaring hope, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_swallow_twin_herbs_late_foundation",
                "start_p": 38,
                "title": "第三幕 · 连吞九叶芝，一朝破筑后",
                "bgm_prompt": "Surging Chinese cultivation breakthrough soundtrack, extreme ice and dark fire colliding in meridians, roaring golden sea of qi and triumphant gong climax, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_seventh_ring_glacier_arch_opens",
                "start_p": 60,
                "title": "第四幕 · 七十二滴满，冰渊拱门开",
                "bgm_prompt": "Colossal primordial glacier gate rumbling open in a vast spiritual dimension, crystalline sub-zero choir-free chimes and awe-inspiring ancient grandeur, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        acoustic_ranges=[(61, 64, "mental_realm")],
        skip_onomatopoeia_paras={41, 51, 55},
        dialogue_specs=[
            {"match": "那是……爹当年用过的护身短刀", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬认出石榻边父亲自剖紫府的剔骨短刀"},
            {"match": "吾儿陆烬亲启：若你终究未能安稳留在北渊做个富家翁", "role_id": "lu_qingcang", "tags": "[calmly] [dramatically]", "stability": 0.0, "space": "memory_echo", "note": "父亲陆擎苍石壁炭血留书开篇"},
            {"match": "三年前为父突破紫府后期之日", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "陆擎苍揭露四品以上皆生百足血虫"},
            {"match": "玄剑宗赤阳老狗甘做血月鹰犬", "role_id": "lu_qingcang", "tags": "[fiercely]", "stability": 0.0, "space": "memory_echo", "note": "陆擎苍记述石榻之上自剖紫府三寸挖虫钉匣"},
            {"match": "这便是赤阳老鬼与紫袍长老体内养着的", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬凝视玄石匣内风干百足母虫"},
            {"match": "挖虫之后，为父紫府半废，跌落筑基圆满", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "陆擎苍指出渊底黑冥湖心母坛与守坛血尸卫"},
            {"match": "为父当年重伤未愈，不敢硬撼那尊血尸卫", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "陆擎苍留下两株九叶寒髓芝并嘱托天外相见"},
            {"match": "爹还活着，而且三年前就已经穿过母坛后方的跨界古道去往天外了", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "陆烬心头巨石落地豪情涌动"},
            {"match": "小畜生，这西崖下头风势渐小", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "三四里外西侧绝壁传来赤阳老祖怨毒搜山声"},
            {"match": "断了一条手臂绕远路摸黑搜寻，至少需要一个半时辰", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬布下隐匿阵旗盘膝闭关"},
            {"match": "古引气篇，大周天搬运，给我炼", "role_id": "lu_jin", "tags": "[fiercely]", "stability": 0.0, "note": "陆烬生吞第一株九叶寒髓芝运转大周天"},
            {"match": "一鼓作气，破入筑基后期", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "note": "陆烬吞下第二株寒髓芝冲击筑基后期"},
        ],
        sfx_blueprint=[
            {"p": 6, "pos": "before", "slug": "disarm_wire_mechanism_click", "sfx_prompt": "Subtle precision stone lock turning and taut metallic tripwires slackening quietly inside a rocky cave", "duration_seconds": 2.2, "gain_db": 0.5, "note": "拧动暗槽解除洞口三根乌金丝机括"},
            {"p": 24, "pos": "after", "slug": "demon_fire_incinerate_parasite", "sfx_prompt": "Fierce violet flame hiss instantly incinerating a dried chitinous centipede into ash inside a stone box", "duration_seconds": 2.4, "gain_db": 1.0, "note": "焚锁妖煞火将石匣内百足血虫烧成灰白粉末"},
            {"p": 41, "pos": "before", "slug": "glacial_herb_surge_meridians", "sfx_prompt": "Roaring sub-zero glacial river surging internally mixed with crackling spiritual furnace flame", "duration_seconds": 3.2, "gain_db": 1.5, "note": "轰！九叶寒髓芝极寒药力冲入四肢百骸"},
            {"p": 55, "pos": "before", "motif_id": "motif_qi_sea_shatter", "slug": "late_foundation_barrier_break", "gain_db": 1.5, "note": "咔嚓！突破筑基境后期，七十二滴暗金灵液成阵"},
            {"p": 63, "pos": "before", "motif_id": "motif_xujie_gate", "slug": "seventh_ring_ice_arch_open", "gain_db": 1.5, "note": "第七环百兽冰渊三丈幽蓝冰晶拱门轰然洞开"},
        ],
    )
    j33, m33 = save_episode_scripts(s33, SCRIPTS_DIR, registry)
    built.append(("E033", j33, m33))

    # =========================================================================
    # E034 · 第34章 踏入第七环，百兽冰渊的活体残爪 (59 paras, 10 quotes)
    # =========================================================================
    md_34 = SOURCE_DIR / "第34章_踏入第七环，百兽冰渊的活体残爪.md"
    s34 = compile_episode_cue_sheet(
        episode_id="E034",
        chapter_number=34,
        source_md_path=md_34,
        source_rel_path=f"02_分章精修正文/{md_34.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_hundred_beasts_glacier_canyon",
                "start_p": 1,
                "title": "第一幕 · 踏足百兽渊，红线镇大凶",
                "bgm_prompt": "Awe-inspiring primordial frozen canyon soundtrack, towering sapphire ice walls entombing colossal ancient monsters, deep resonant drone and icy chimes, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_living_frost_thunder_roc_marrow",
                "start_p": 17,
                "title": "第二幕 · 冰笋锁鹏爪，铭牌镇活髓",
                "bgm_prompt": "Suspenseful mystical treasure extraction score, rhythmic nine-second thunder heartbeat inside ancient ice escalating into sharp lightning burst, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_sixth_ring_chains_spine_reforge",
                "start_p": 35,
                "title": "第三幕 · 雾深闻铁链，雷霜锻脊龙",
                "bgm_prompt": "Eerie distant bronze chains giving way to ferocious lightning-and-frost bone tempering, intense martial percussion and soaring silver-blue speed motif, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_screams_from_abyss_floor",
                "start_p": 54,
                "title": "第四幕 · 二阶锁松动，渊底起血光",
                "bgm_prompt": "Sudden dark horror escalation echoing up from a deep subterranean chasm, ruthless demonic slaughter pressure and cold blade readiness, instrumental only, no vocals",
                "bgm_duration_s": 80.0,
            },
        ],
        acoustic_ranges=[(2, 40, "mental_realm")],
        skip_onomatopoeia_paras={30, 36, 41, 43, 51},
        dialogue_specs=[
            {"match": "好可怕的太古冻气！难怪筑基中期之时", "role_id": "lu_jin", "tags": "[gasps] [calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬灵识化身踏入第七环抵御太古寒意"},
            {"match": "第七环，镇诸界百兽遗煞", "role_id": "ancient_construct_echo", "tags": "[calmly]", "stability": 1.0, "space": "mental_realm", "note": "第七环入口冰封石碑太古篆文警示"},
            {"match": "知止不贪，我如今刚刚踏入筑基后期", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬谨守百丈红线不越雷池"},
            {"match": "竟然还有一滴尚未死绝的活体二阶绝巅雷鹏真髓", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "space": "mental_realm", "note": "陆烬发现冰笋内太古霜翼雷鹏活体骨髓"},
            {"match": "试试看能否引出来", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "陆烬以零号铭牌贴壁融冰引髓"},
            {"match": "等的就是你，给我进来", "role_id": "lu_jin", "tags": "[fiercely] [shouting]", "stability": 0.0, "space": "mental_realm", "note": "陆烬以零号铭牌镇压银蓝幼鹏虚影带回肉身"},
            {"match": "又是零号的气息……太一已死，锁链未断", "role_id": "eternal_night_whisper", "tags": "[whispers] [hoarsely]", "stability": 0.0, "space": "mental_realm", "note": "百丈红线后第六环深处飘来苍老沙哑残破低语"},
            {"match": "那是……【第二阶基因锁】的门槛", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "雷鹏真髓锻骨后陆烬感应到第二阶基因锁白银门户"},
            {"match": "啊！救命！族长快跑，有吃人的妖怪下来了", "role_id": "male_disciple_b", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "五百丈下渊底盲裔族人凄厉惨叫"},
            {"match": "桀桀桀……真是天无绝人之路！没想到这暗无天日的天渊谷底", "role_id": "chiyang_laozu", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖在谷底屠戮盲裔吞血修补断臂"},
        ],
        sfx_blueprint=[
            {"p": 30, "pos": "before", "slug": "melt_ice_thunder_roc_screech", "sfx_prompt": "Sizzling flame piercing thick glacier ice followed by an electrifying primordial thunder-eagle screech bursting out", "duration_seconds": 3.2, "gain_db": 1.5, "note": "滋啦！融开冰孔，霜翼雷鹏真髓化幼鹏扑出"},
            {"p": 36, "pos": "before", "slug": "distant_bronze_chains_dragging", "sfx_prompt": "Colossal heavy ancient bronze chains dragging slowly across frozen stone deep inside a misty abyss", "duration_seconds": 3.4, "gain_db": 0.5, "note": "哗啦……第六环冰渊深处传来青铜锁链拖拽声"},
            {"p": 41, "pos": "before", "motif_id": "motif_genelock_awaken", "slug": "roc_marrow_spine_lightning", "gain_db": 1.5, "note": "轰隆！噼里啪啦！雷鹏真髓化开贯通二十四节脊椎"},
            {"p": 51, "pos": "before", "slug": "frost_lightning_flash_step_sabre", "sfx_prompt": "Instantaneous supersonic lightning flash-step dash and heavy sabre unsheathing wrapped in crackling frost electricity", "duration_seconds": 2.6, "gain_db": 1.5, "note": "嗤！原地留淡蓝霜电残影，零点一息掠十丈挥刀"},
        ],
    )
    j34, m34 = save_episode_scripts(s34, SCRIPTS_DIR, registry)
    built.append(("E034", j34, m34))

    # =========================================================================
    # E035 · 第35章 天渊守墓奴，谁在牧养大苍？ (61 paras, 23 quotes)
    # =========================================================================
    md_35 = SOURCE_DIR / "第35章_天渊守墓奴，谁在牧养大苍？.md"
    s35 = compile_episode_cue_sheet(
        episode_id="E035",
        chapter_number=35,
        source_md_path=md_35,
        source_rel_path=f"02_分章精修正文/{md_35.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_black_lake_altar_blind_clan",
                "start_p": 1,
                "title": "第一幕 · 黑冥母坛现，暗刺救盲女",
                "bgm_prompt": "Dark oppressive subterranean lake basin score, colossal crimson light pillar hum, sudden razor-sharp lightning rescue strike, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_soul_absorbing_mine_pie_memory",
                "start_p": 24,
                "title": "第二幕 · 遁入吸灵洞，半块旧饼恩",
                "bgm_prompt": "Quiet poignant shelter inside a deep stone mine, gentle sorrowful xiao flute and warm memory of a scarred hero's kindness, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_three_thousand_year_blood_farm",
                "start_p": 39,
                "title": "第三幕 · 十万工匠血，苍穹假月影",
                "bgm_prompt": "Tragic ancient cosmic truth Chinese xianxia soundtrack, mournful bowed strings revealing a three-thousand-year world-scale blood harvest altar, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_faceless_guardian_hunter_gambit",
                "start_p": 50,
                "title": "第四幕 · 守坛死傀律，驱虎吞狼谋",
                "bgm_prompt": "Cold calculating tactical suspense score, heavy bronze guardian aura and sharp razor-like hunter resolve, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[(3, 29, "vast_hall")],
        skip_onomatopoeia_paras={16},
        dialogue_specs=[
            {"match": "跑什么？你们这群世代烂在渊底的瞎眼虫豸", "role_id": "chiyang_laozu", "tags": "[sarcastic] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖掐住老族长脖颈狞笑刺向阿盲"},
            {"match": "放开阿爷！上使立过规矩，不许外人杀光守渊人", "role_id": "a_mang", "tags": "[crying] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "白发盲眼少女阿盲护住幼弟抓黑石拼命"},
            {"match": "狗屁的规矩！等本座吞够百人精血恢复七成元气", "role_id": "chiyang_laozu", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳狂笑催动腐血触须"},
            {"match": "谁！", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "触须被裂风刺斩断赤阳暴退十丈惊喝"},
            {"match": "陆家小畜生！是你躲在那儿鬼鬼祟祟放冷箭", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳死盯吸灵矿石堆厉喝"},
            {"match": "该死！这渊底到处都是隔绝神识的鬼石头", "role_id": "chiyang_laozu", "tags": "[angry]", "stability": 0.0, "space": "vast_hall", "note": "紫府神识撞上吸灵冥石矿洞粉碎"},
            {"match": "缩头乌龟！本座没工夫进老鼠洞陪你玩命", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳忌惮陷阱转身扑向黑冥湖南岸"},
            {"match": "咳咳……多、多谢壮士救命大恩", "role_id": "weathered_elder_npc", "tags": "[coughs] [hoarsely]", "stability": 0.0, "note": "矿洞内垂死老族长饮下灵泉喘息致谢"},
            {"match": "我叫阿盲，这是我阿爷。壮士，外头那个浑身腐臭的恶鬼走了么", "role_id": "a_mang", "tags": "[trembling] [softly]", "stability": 0.0, "note": "盲眼少女阿盲拉着幼弟磕头询问"},
            {"match": "暂时退去黑冥湖边了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬虚扶起阿盲"},
            {"match": "老人家，我爹陆擎苍三年前曾经过这片谷底", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬向老族长打听父亲踪迹"},
            {"match": "恩公可是当年那位陆大侠的后人", "role_id": "weathered_elder_npc", "tags": "[gasps] [hoarsely]", "stability": 0.0, "note": "老族长激动抬头"},
            {"match": "三年前月亏之夜，有一位胸口缠着血布", "role_id": "a_mang", "tags": "[softly] [dramatically]", "stability": 0.0, "note": "阿盲摸出珍藏三年的半块风干面饼角讲述陆擎苍过往"},
            {"match": "老人家，你们为何世代居住在这暗无天日的渊底", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬追问守渊盲裔与湖心母坛来历"},
            {"match": "老朽死前能遇上陆大侠之子，也算天意", "role_id": "weathered_elder_npc", "tags": "[sighs] [hoarsely]", "stability": 0.0, "note": "老族长惨笑追述三千年前凡人工匠先祖"},
            {"match": "后来有自称来自天外上界的‘无面仙使’降临", "role_id": "weathered_elder_npc", "tags": "[trembling] [hoarsely]", "stability": 0.0, "note": "老族长血泪控诉九万九千工匠祭坛与夺目恶咒"},
            {"match": "难怪在断天戍见到的鹤鸣掌门遗言写着‘血月在渊不在天’", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬破妄真目看穿百年血月母晶与万千血线"},
            {"match": "大苍界九州生灵跪拜畏惧了三千年的那轮天上血月", "role_id": "lu_jin", "tags": "[coldly] [dramatically]", "stability": 0.0, "note": "陆烬彻底洞悉大苍三千年血食药田真相"},
            {"match": "小恩公看得真切……每隔一百年，母坛后方那条黑色石道尽头", "role_id": "weathered_elder_npc", "tags": "[hoarsely]", "stability": 0.5, "note": "老族长说明百年收割将至与守坛血尸卫"},
            {"match": "老人家，那尊【守坛血尸卫】有何弱点或是行动铁律", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬追问破局关键"},
            {"match": "它……它没有神智，只认死理", "role_id": "weathered_elder_npc", "tags": "[trembling] [hoarsely]", "stability": 0.0, "note": "老族长用尽最后力气道出十丈禁界死令后咽气"},
            {"match": "阿爷！", "role_id": "a_mang", "tags": "[crying] [whispers]", "stability": 0.0, "note": "阿盲死死咬住手臂无声泣血"},
            {"match": "单靠我一人硬杀全盛傀儡或是搏命老鬼，多少还要费些手脚", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "note": "陆烬摸出零号铭牌与裂风刺定下驱虎吞狼之计"},
        ],
        sfx_blueprint=[
            {"p": 6, "pos": "before", "slug": "blood_altar_siphon_hum", "sfx_prompt": "Deep ominous subterranean blood-altar beam humming upward and sucking air into a skyward vortex", "duration_seconds": 3.2, "placement": "overlay_next", "gain_db": -3.0, "note": "黑冥湖心九丈母坛暗红光柱虹吸轰鸣"},
            {"p": 16, "pos": "before", "slug": "frost_spike_sever_blood_tentacle", "sfx_prompt": "Razor-silent frost-lightning dart slicing through a thick wet flesh tentacle with sizzling venom", "duration_seconds": 2.4, "gain_db": 1.5, "note": "嗤！裂风刺携太古雷霜精准斩断赤阳腐血触须"},
        ],
    )
    j35, m35 = save_episode_scripts(s35, SCRIPTS_DIR, registry)
    built.append(("E035", j35, m35))

    # =========================================================================
    # E036 · 第36章 驱虎吞恶狼，双紫府死斗 (77 paras, 17 quotes)
    # =========================================================================
    md_36 = SOURCE_DIR / "第36章_驱虎吞恶狼，双紫府死斗.md"
    s36 = compile_episode_cue_sheet(
        episode_id="E036",
        chapter_number=36,
        source_md_path=md_36,
        source_rel_path=f"02_分章精修正文/{md_36.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_underwater_stealth_blood_bait",
                "start_p": 1,
                "title": "第一幕 · 割指涂隐符，龟息潜冥湖",
                "bgm_prompt": "Submerged dark-water stealth suspense soundtrack, muffled underwater pulse, cold calculating precision and ticking five-second fuse tension, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_talisman_burns_guardian_awakens",
                "start_p": 18,
                "title": "第二幕 · 破符诈老鬼，重戟醒死卫",
                "bgm_prompt": "Sudden trap-springing escalation Chinese xianxia score, greedy demonic charge colliding with a colossal bronze construct awakening roar, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_twin_zifu_hundred_blow_clash",
                "start_p": 46,
                "title": "第三幕 · 百斤泣血戟，双紫府死斗",
                "bgm_prompt": "Earth-shattering clash of two Zifu-realm titans over a black underground lake, massive halberd shockwaves, shattering bone pillars and ferocious war percussion, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_core_detonation_predator_surfaces",
                "start_p": 64,
                "title": "第四幕 · 尸丹炸铁傀，破水起寒芒",
                "bgm_prompt": "Cataclysmic core self-detonation fading into eerie breathless silence, manic wheezing laughter cut short by silent icy water parting behind the prey, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(12, 77, "vast_hall")],
        skip_onomatopoeia_paras={19, 25, 37, 42, 64, 68},
        dialogue_specs=[
            {"match": "阿盲，带着你弟弟退进矿洞最里面的石窟", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬安顿阿盲姐弟退入深窟塞紧耳朵"},
            {"match": "赤阳老鬼生性多疑，若是寻常飞石打进母坛", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬边制作五息破胆隐尘血饵边推演"},
            {"match": "唯有让他亲眼认定我已经靠着隐身秘宝潜上了母坛", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬攻心算死赤阳老祖"},
            {"match": "该死……这具上使留下的铁疙瘩怎么还不休眠", "role_id": "chiyang_laozu", "tags": "[angry] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "南岸礁石后赤阳老祖焦躁窥伺母晶"},
            {"match": "什么人！", "role_id": "chiyang_laozu", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "母晶底座爆出零号血气赤阳双目赤红惊喝"},
            {"match": "好阴险的陆家小杂种！难怪刚才在矿洞口虚晃一枪", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳老祖彻底上当误以为陆烬隐身偷摘母晶"},
            {"match": "给本座住手！那颗母晶是老夫的", "role_id": "chiyang_laozu", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳燃烧十滴紫府精血冲入母坛十丈禁界"},
            {"match": "检测到母晶受损……锁定十丈禁界闯入活体", "role_id": "ancient_construct_echo", "tags": "[coldly]", "stability": 1.0, "space": "vast_hall", "note": "守坛血尸卫青铜白面具裂开血红竖眼法则抹杀"},
            {"match": "不好！", "role_id": "chiyang_laozu", "tags": "[gasps] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳抓到冰冷铁刺瞬间惊骇欲绝"},
            {"match": "该死的小畜生！拿根死钉子诈我入局", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳扭断肋骨祭出赤阳万魂幡硬挡"},
            {"match": "停手！上使傀儡且慢动手！本座乃大苍玄剑宗护道人赤阳", "role_id": "chiyang_laozu", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "万魂幡折断赤阳吐血飞退求饶"},
            {"match": "闯禁界者，死！", "role_id": "ancient_construct_echo", "tags": "[coldly] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "守坛血尸卫踏碎湖面挥百斤泣血重戟绝命追杀"},
            {"match": "疯子！没长脑子的死铁皮！真当本座怕了你不成", "role_id": "chiyang_laozu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "退路断绝的赤阳催动全身紫府尸火死拼"},
            {"match": "守坛血尸卫力大无穷，全身由三百年渊底血铁浇铸", "role_id": "lu_jin", "tags": "[whispers] [coldly]", "stability": 0.5, "space": "dry", "note": "水下三十丈暗礁后陆烬冷静剖析双方死穴"},
            {"match": "给老夫碎！", "role_id": "chiyang_laozu", "tags": "[desperately] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "赤阳挖下半边本命尸丹塞入傀儡面具引爆"},
            {"match": "咳咳……哈哈哈！赢了！最后活下来的还是本座", "role_id": "chiyang_laozu", "tags": "[coughs] [laughs]", "stability": 0.0, "space": "vast_hall", "note": "只剩半截残躯的赤阳在母坛石阶癫狂大笑"},
            {"match": "只要吞了这颗母晶……本座马上就能重塑金丹肉身", "role_id": "chiyang_laozu", "tags": "[laughs] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "赤阳颤抖伸手抓向半寸外的血月母晶"},
        ],
        sfx_blueprint=[
            {"p": 8, "pos": "before", "slug": "submerge_into_black_lake", "sfx_prompt": "Silent smooth dive into thick dark subterranean water followed by deep muffled underwater ambience", "duration_seconds": 2.6, "gain_db": 0.5, "note": "滑入黑冥湖水下暗渠龟息潜行"},
            {"p": 19, "pos": "before", "slug": "stealth_spike_nail_altar_base", "sfx_prompt": "Whisper-thin metallic dart skimming over water and embedding sharply into crystalline stone", "duration_seconds": 2.0, "gain_db": 1.0, "note": "嗖！裂风刺钉入母晶底座血晶池"},
            {"p": 25, "pos": "before", "slug": "concealment_talisman_burn_ash", "sfx_prompt": "Paper talisman suddenly flaring and burning to ash with a sharp spiritual aura pulse", "duration_seconds": 2.0, "gain_db": 1.0, "note": "嗤啦！五息到，敛息隐尘符燃尽爆出零号气机"},
            {"p": 37, "pos": "before", "slug": "bronze_mask_eye_crack_halberd_chop", "sfx_prompt": "Ancient bronze mask cracking open with a terrifying metallic hum followed by a hundred-pound halberd cleaving the air like thunder", "duration_seconds": 3.6, "gain_db": 2.0, "note": "咔嚓轰隆！守坛血尸卫睁开血色竖眼当头一戟劈落"},
            {"p": 49, "pos": "before", "slug": "halberd_smash_soul_banner", "sfx_prompt": "Deafening heavy halberd impact snapping an iron banner pole and blasting three-zhang waves across an underground lake", "duration_seconds": 3.4, "gain_db": 2.0, "note": "铛！百斤泣血重戟劈折赤阳万魂幡"},
            {"p": 68, "pos": "before", "slug": "zifu_corpse_core_self_destruct", "sfx_prompt": "Devastating dark-purple spiritual core explosion shattering bronze pillars and raining debris into black water", "duration_seconds": 4.2, "gain_db": 2.5, "note": "轰隆！半颗紫府本命尸丹在守坛血尸卫头颅内殉爆"},
        ],
    )
    j36, m36 = save_episode_scripts(s36, SCRIPTS_DIR, registry)
    built.append(("E036", j36, m36))

    return built


if __name__ == "__main__":
    only_compile = "--compile-only" in sys.argv
    items = build_all_batch7()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if not only_compile:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=8)
