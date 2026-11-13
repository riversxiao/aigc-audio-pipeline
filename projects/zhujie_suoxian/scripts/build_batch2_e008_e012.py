"""Build, validate, render, and archive Batch 2: Episodes E008–E012 (Chapters 8–12)."""

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


def build_all_batch2() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E008 · 第8章 祠堂藏杀阵，寿宴不速客 (56 paras, 24 quotes)
    # =========================================================================
    md_08 = SOURCE_DIR / "第08章_祠堂藏杀阵，寿宴不速客.md"
    s08 = compile_episode_cue_sheet(
        episode_id="E008",
        chapter_number=8,
        source_md_path=md_08,
        source_rel_path=f"02_分章精修正文/{md_08.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_steward_pulse_probe",
                "start_p": 1,
                "title": "第一幕 · 泥坑拾红帖，空壳瞒恶奴",
                "bgm_prompt": "Cold restrained ancient Chinese courtyard confrontation score, tense pipa plucks, low brooding erhu and hidden calculation beneath feigned frailty, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_send_away_fubo",
                "start_p": 20,
                "title": "第二幕 · 抹血露霜刃，支走老忠仆",
                "bgm_prompt": "Poignant resolute Chinese chamber underscore, warm mournful xiao flute and deep cello resonance of loyalty and parting before a life-or-death battle, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_spirit_severing_array",
                "start_p": 35,
                "title": "第三幕 · 撬砖埋磁母，独坐待三更",
                "bgm_prompt": "Dark ritualistic Chinese xianxia suspense score, deep metallic bronze pulse, taut rhythmic woodblocks and gathering storm under a crimson moon, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_shatter_ancestral_plaque",
                "start_p": 46,
                "title": "第四幕 · 血月临飞檐，掌碎宗祠匾",
                "bgm_prompt": "Explosive menacing Chinese dark martial score, heavy war drum impacts, ominous brass-like horn drone and razor-sharp string stabs, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        skip_onomatopoeia_paras={6, 51},
        dialogue_specs=[
            {"match": "苏贵！你欺人太甚！", "role_id": "fu_bo", "tags": "[angry] [shouting]", "stability": 0.0, "note": "福伯独臂青筋暴起挡在祠堂石阶前怒喝"},
            {"match": "前夜你们三小姐刚拿了寒渊佩", "role_id": "fu_bo", "tags": "[angry] [hoarsely]", "stability": 0.0, "note": "福伯怒斥苏家吃绝户"},
            {"match": "王法？", "role_id": "snobbish_steward_npc", "tags": "[sarcastic]", "stability": 0.0, "note": "苏贵嗤笑掸袖"},
            {"match": "在北渊城，玄剑宗真传的金口便是王法", "role_id": "snobbish_steward_npc", "tags": "[arrogant] [shouting]", "stability": 0.0, "note": "苏贵狗仗人势抬脚欲踹"},
            {"match": "福伯，退下", "role_id": "lu_jin", "tags": "[hoarsely] [softly]", "stability": 0.5, "note": "陆烬伪装病弱走出西厢房"},
            {"match": "哎哟，陆少主身子骨这般虚", "role_id": "snobbish_steward_npc", "tags": "[sarcastic]", "stability": 0.0, "note": "苏贵假意搀扶扣脉试探丹田"},
            {"match": "看来陆少主果真是大病未愈", "role_id": "snobbish_steward_npc", "tags": "[dismissive]", "stability": 0.0, "note": "苏贵试出空丹田嫌弃擦手"},
            {"match": "明日正午苏府前厅", "role_id": "snobbish_steward_npc", "tags": "[laughs] [sarcastic]", "stability": 0.0, "note": "苏贵大笑扬长而去"},
            {"match": "少主，老奴这就去拼了这条老命", "role_id": "fu_bo", "tags": "[crying] [hoarsely]", "stability": 0.0, "note": "福伯双眼通红悲愤欲拼命"},
            {"match": "门关上", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬直起脊背抹去假血冷冽下令"},
            {"match": "少主，明日苏家寿宴咱们真要去么", "role_id": "fu_bo", "tags": "[whispers]", "stability": 0.0, "note": "福伯愣怔询问"},
            {"match": "等不到明日正午了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬审视青石砖冷静断言"},
            {"match": "春桃昨夜漏了底", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬剖析裴玄度掘祠动机"},
            {"match": "那苏贵方才送帖", "role_id": "fu_bo", "tags": "[gasps]", "stability": 0.0, "note": "福伯脸色一白"},
            {"match": "不过是投石问路", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬看穿投石问路毒计"},
            {"match": "既已试出我丹田空空", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "note": "锁定三更血月灭口掘祠时机"},
            {"match": "那咱们快去报镇渊司", "role_id": "fu_bo", "tags": "[desperately]", "stability": 0.0, "note": "福伯急声提议报官"},
            {"match": "镇渊司副统领苏牧便是苏清寒的亲兄长", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬指出报官等于自投罗网"},
            {"match": "福伯，你立刻提着菜篮从后巷出去", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬托付买玄磁铁母石并支开福伯"},
            {"match": "少主！老奴受老爷大恩", "role_id": "fu_bo", "tags": "[crying] [desperately]", "stability": 0.0, "note": "福伯单膝跪地死拽衣摆愿挡刀"},
            {"match": "留在这里，你是替我挡刀", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬俯身扶起老人"},
            {"match": "陆家就剩我们两个人了", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬温声嘱托福伯平安活着"},
            {"match": "苏二长老，这便是你说躺在榻上等死的废人", "role_id": "li_cang", "tags": "[coldly] [sarcastic]", "stability": 0.0, "note": "玄剑宗执法执事厉苍阴鸷登场"},
            {"match": "裴师侄心善，多留了你三日阳寿", "role_id": "li_cang", "tags": "[coldly]", "stability": 0.0, "note": "厉苍猫戏耗子般逼交天渊遗物"},
        ],
        sfx_blueprint=[
            {"p": 6, "pos": "before", "slug": "west_wing_door_creak", "sfx_prompt": "Old wooden room door slowly creaking open into a cold courtyard silence", "duration_seconds": 2.4, "gain_db": -0.5, "note": "吱呀！西厢房木门缓缓拉开"},
            {"p": 14, "pos": "before", "slug": "wrist_grab_qi_probe", "sfx_prompt": "Sharp cloth rustle of a claw-like hand grabbing a wrist followed by a cold hollow subterranean qi resonance", "duration_seconds": 2.4, "gain_db": -0.5, "note": "苏贵扣脉门真气长驱直入泥牛入海"},
            {"p": 31, "pos": "before", "slug": "fubo_kneel_stone", "sfx_prompt": "Heavy thud of knees dropping onto stone courtyard tiles with urgent cloth grab", "duration_seconds": 2.0, "gain_db": 0.0, "note": "扑通！福伯单膝跪地拽住衣摆"},
            {"p": 39, "pos": "before", "slug": "blade_carve_magnet_array", "sfx_prompt": "Iron blade tip carving runes into stone bricks and heavy magnetic ore blocks slotting into ground channels", "duration_seconds": 3.2, "gain_db": 0.0, "note": "断刀刻阵槽埋入十二块玄磁铁母石"},
            {"p": 46, "pos": "before", "slug": "midnight_watch_wind_stop", "sfx_prompt": "Three distant hollow bamboo night-watch claps fading into sudden eerie dead silence", "duration_seconds": 3.2, "gain_db": -0.5, "note": "三更梆子余音落尽，院外夜风骤滞"},
            {"p": 51, "pos": "before", "slug": "ancestral_gate_blast", "sfx_prompt": "Devastating martial palm blast violently shattering heavy wooden temple doors and an ancestral plaque into flying splinters", "duration_seconds": 3.5, "gain_db": 2.0, "note": "轰！半步筑基掌风拍碎祠堂木门与牌匾"},
        ],
    )
    j08, m08 = save_episode_scripts(s08, SCRIPTS_DIR, registry)
    built.append(("E008", j08, m08))

    # =========================================================================
    # E009 · 第9章 血月之下，第一阶基因锁开！ (76 paras, 12 quotes)
    # =========================================================================
    md_09 = SOURCE_DIR / "第09章_血月之下，第一阶基因锁开！.md"
    s09 = compile_episode_cue_sheet(
        episode_id="E009",
        chapter_number=9,
        source_md_path=md_09,
        source_rel_path=f"02_分章精修正文/{md_09.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_array_trap_beheading",
                "start_p": 1,
                "title": "第一幕 · 绝灵阵封院，一刀枭苏鹤",
                "bgm_prompt": "Sudden explosive Chinese martial ambush score, deep magnetic array hum, taut war drums and fierce erhu slashes in a sealed ancestral hall, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act2_iron_claw_desperate_stand",
                "start_p": 17,
                "title": "第二幕 · 裂魂爪压顶，染血靠供桌",
                "bgm_prompt": "Brutal oppressive dark xianxia boss-fight score, relentless pounding percussion, metallic claw screeches and desperate life-or-death tension, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_first_genelock_awakening",
                "start_p": 33,
                "title": "第三幕 · 冲断青铜锁，破妄斩命线",
                "bgm_prompt": "Monumental heroic Chinese xianxia awakening soundtrack, thunderous primal heartbeat drums, shattering bronze chains and blazing triumphant strings, instrumental only, no vocals",
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act4_true_blood_opens_vault",
                "start_p": 65,
                "title": "第四幕 · 吞液破七重，真血启暗井",
                "bgm_prompt": "Solemn mysterious ancient Chinese aftermath score, deep resonant bronze mechanisms, quiet xiao flute and ancient ancestral secret awakening, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        skip_onomatopoeia_paras={5, 12, 23, 38, 57, 61, 72, 74},
        dialogue_specs=[
            {"match": "装神弄鬼的小畜生", "role_id": "sect_elder_antagonist", "tags": "[arrogant] [shouting]", "stability": 0.0, "note": "苏家二长老苏鹤图狞笑扑抓"},
            {"match": "这是什么鬼阵法", "role_id": "sect_elder_antagonist", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "苏鹤图陷绝灵杀阵骇然惊呼"},
            {"match": "藏气敛息秘术？好狡猾的小杂种", "role_id": "li_cang", "tags": "[angry] [coldly]", "stability": 0.0, "note": "厉苍瞳孔骤缩识破藏气"},
            {"match": "区区引气六重", "role_id": "li_cang", "tags": "[shouting]", "stability": 0.0, "note": "厉苍祭出玄铁裂魂爪雷霆掏心"},
            {"match": "能接本执事一爪不死", "role_id": "li_cang", "tags": "[coldly]", "stability": 0.0, "note": "厉苍杀机暴涨逼降"},
            {"match": "看你这身邪门敛息术与古阵", "role_id": "li_cang", "tags": "[coldly]", "stability": 0.0, "note": "厉苍以搜魂抽髓威胁"},
            {"match": "想要天渊的东西？", "role_id": "lu_jin", "tags": "[hoarsely] [coldly]", "stability": 0.0, "note": "陆烬抹血拄刀冷笑迎战"},
            {"match": "冥顽不灵！下辈子投胎长个记性", "role_id": "li_cang", "tags": "[angry] [shouting]", "stability": 0.0, "note": "厉苍震怒全力扣向天灵盖"},
            {"match": "给我……开！", "role_id": "lu_jin", "tags": "[shouting]", "stability": 0.0, "space": "mental_realm", "note": "陆烬识海咆哮悍然冲断第一阶基因锁"},
            {"match": "怎么可能！你气海明明废了", "role_id": "li_cang", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "厉苍一爪砸空魂飞魄散"},
            {"match": "破你狗命的身法！", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "note": "陆烬燃火双指精准点碎命线死穴"},
            {"match": "你……你头顶没有线", "role_id": "li_cang", "tags": "[trembling] [whispers]", "stability": 0.0, "note": "厉苍被斜斩两半临死惊恐嘶声"},
        ],
        sfx_blueprint=[
            {"p": 5, "pos": "before", "slug": "magnetic_array_dome", "sfx_prompt": "Deep subterranean magnetic hum erupting into an inverted sonic barrier sealing an entire temple hall into dead silence", "duration_seconds": 3.0, "gain_db": 1.0, "note": "嗡！小颠倒绝灵杀阵冲天封院"},
            {"p": 12, "pos": "before", "slug": "blood_qi_burst_behead", "sfx_prompt": "Explosive stone tile crack under dashing footsteps followed by a razor-sharp heavy iron blade flash severing bone cleanly", "duration_seconds": 3.0, "gain_db": 1.5, "note": "轰！锵！断刀暗红火线一刀枭首苏鹤图"},
            {"p": 23, "pos": "before", "slug": "iron_claw_blade_clash", "sfx_prompt": "Deafening metallic clash of dark iron demon claws slamming against a heavy broken broadsword and crashing into a stone altar", "duration_seconds": 3.2, "gain_db": 2.0, "note": "铛！玄铁裂魂爪硬撼断刀震撞青石供桌"},
            {"p": 38, "pos": "before", "slug": "genelock_stage1_shatter", "motif_id": "motif_genelock_awaken", "gain_db": 2.5, "note": "轰咔嚓！第一阶基因锁青铜锁扣彻底崩断！"},
            {"p": 51, "pos": "after", "slug": "altar_smashed_miss", "sfx_prompt": "Five iron claws screeching past ear and violently smashing a solid stone altar table into rubble", "duration_seconds": 2.5, "gain_db": 1.5, "note": "极限折角滑开，铁爪轰碎青石供桌"},
            {"p": 57, "pos": "before", "slug": "fire_finger_snap_thread", "sfx_prompt": "Searing martial finger strike piercing an energy nexus with a crisp ethereal snap and muffled internal shockwave", "duration_seconds": 2.4, "gain_db": 1.5, "note": "噗！一指截断血月肉线死穴节点"},
            {"p": 61, "pos": "before", "slug": "diagonal_bisect_slash", "sfx_prompt": "Ferocious upward diagonal heavy blade slash tearing through armor and bone followed by a dripping blade clanking on stone", "duration_seconds": 3.2, "gain_db": 2.0, "note": "嗤啦！反握断刀斜斩厉苍"},
            {"p": 72, "pos": "before", "slug": "true_blood_drip_stone_mechanism", "sfx_prompt": "Two slow drops of warm blood hitting stone followed by an ancient bronze seal hum and massive granite floor slabs grinding open", "duration_seconds": 4.2, "gain_db": 1.0, "note": "滴答！破锁真血激活祠堂万年青冈岩暗井机括"},
        ],
    )
    j09, m09 = save_episode_scripts(s09, SCRIPTS_DIR, registry)
    built.append(("E009", j09, m09))

    # =========================================================================
    # E010 · 第10章 天渊无脐子，古棺一声叩 (57 paras, 16 quotes)
    # =========================================================================
    md_10 = SOURCE_DIR / "第10章_天渊无脐子，古棺一声叩.md"
    s10 = compile_episode_cue_sheet(
        episode_id="E010",
        chapter_number=10,
        source_md_path=md_10,
        source_rel_path=f"02_分章精修正文/{md_10.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_lime_box_birthday_gift",
                "start_p": 1,
                "title": "第一幕 · 石灰盛断袖，寿礼吓破胆",
                "bgm_prompt": "Distant festive Chinese banquet gongs twisting into cold panic and suffocating clan dread, sharp plucked pipa and low trembling strings, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act2_mirror_chill_vault_open": False,
                "act_id": "act2_mirror_chill_vault_open",
                "start_p": 16,
                "title": "第二幕 · 铜镜落玉佩，密室启遗匣",
                "bgm_prompt": "Icy haunting guqin solo transitioning into solemn subterranean chamber strings, quiet weight of three years of secrets, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_father_blood_jade_slip",
                "start_p": 33,
                "title": "第三幕 · 慈父泣血简，天渊无脐儿",
                "bgm_prompt": "Deeply emotional tragic ancient Chinese father-and-son score, mournful xiao flute, warm low cello and vast northern wasteland wind, instrumental only, no vocals",
                "bgm_duration_s": 115.0,
            },
            {
                "act_id": "act4_ancient_syllables_coffin_knock",
                "start_p": 46,
                "title": "第四幕 · 残铜开九环，古棺一声叩",
                "bgm_prompt": "Vast cosmic ancient Chinese mystery score, receding fog resonance, eerie frozen crystalline choir-free textures fading into absolute dead silence at the end, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(46, 57, "mental_realm")],
        skip_onomatopoeia_paras={10, 46, 57},
        dialogue_specs=[
            {"match": "爹，莫非是陆擎苍在祠堂地底", "role_id": "su_mu", "tags": "[coldly]", "stability": 0.5, "note": "苏牧皱眉揣测西城动静"},
            {"match": "儿子已派苏贵带两个机灵护院", "role_id": "su_mu", "tags": "[calmly]", "stability": 0.5, "note": "苏牧禀报已派苏贵探看"},
            {"match": "家、家主！大少爷！出大事了", "role_id": "snobbish_steward_npc", "tags": "[trembling] [shouting]", "stability": 0.0, "note": "苏贵捧石灰木盒连滚带爬骇然冲入"},
            {"match": "寿礼已收，勿念", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "memory_echo", "note": "木盒盖内侧炭条冷冽六字残响"},
            {"match": "不可能！厉执事乃是半步筑基高手", "role_id": "su_mu", "tags": "[angry] [shouting]", "stability": 0.0, "note": "苏牧铁青着脸暴怒失态"},
            {"match": "大少爷，陆氏宗祠两扇新换的木门紧闭着", "role_id": "snobbish_steward_npc", "tags": "[trembling]", "stability": 0.0, "note": "苏贵哆嗦汇报石阶三寸刀痕"},
            {"match": "小的远远看了一眼就不敢靠近了", "role_id": "snobbish_steward_npc", "tags": "[trembling] [whispers]", "stability": 0.0, "note": "苏贵恐惧猜测紫府高人"},
            {"match": "撤！立刻把西城盯梢的人手全部撤回来", "role_id": "sect_elder_antagonist", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "苏家家主苏正阳冷汗涔涔厉声下令"},
            {"match": "在裴真传亲自查明底细之前", "role_id": "sect_elder_antagonist", "tags": "[angry] [shouting]", "stability": 0.0, "note": "苏正阳严令禁提宗祠地契"},
            {"match": "小姐，裴公子闭关冲击筑基中期", "role_id": "female_maid_npc", "tags": "[trembling] [softly]", "stability": 0.5, "note": "春桃战战兢兢捡起白玉如意"},
            {"match": "裴玄度想破筑基中期最快也要十天半月", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "密室内陆烬盘点战利品"},
            {"match": "烬儿，当你能凭自己的血打开这只铁匣时", "role_id": "lu_qingcang", "tags": "[softly] [hoarsely]", "stability": 0.5, "space": "memory_echo", "note": "父亲陆擎苍跨越三年的泣血玉简留音"},
            {"match": "有些事，爹本想烂在肚子里一辈子", "role_id": "lu_qingcang", "tags": "[hoarsely]", "stability": 0.0, "space": "memory_echo", "note": "陆擎苍道出引开老怪与非亲生真相"},
            {"match": "十八年前九月廿三子夜", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "陆擎苍回忆血月黑瞬与天渊无脐弃婴"},
            {"match": "没有肚脐，便不是凡胎母体分娩之子", "role_id": "lu_qingcang", "tags": "[softly]", "stability": 0.5, "space": "memory_echo", "note": "陆擎苍讲述刀烫假肚脐护子十五年"},
            {"match": "烬儿，爹修到紫府才看明白", "role_id": "lu_qingcang", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "陆擎苍最后嘱托：莫信飞升，持铜向北破笼"},
        ],
        sfx_blueprint=[
            {"p": 10, "pos": "before", "slug": "jade_teacup_shatter", "sfx_prompt": "Fine porcelain jade teacup dropping and shattering sharply onto stone floor tiles with hot tea splashing", "duration_seconds": 2.4, "gain_db": 1.0, "note": "啪啦！苏正阳手中青玉茶盏摔碎"},
            {"p": 17, "pos": "after", "slug": "jade_ruyi_slip_table", "sfx_prompt": "Polished white jade scepter slipping from cold fingers and clattering softly onto a wooden dressing table", "duration_seconds": 2.2, "gain_db": 0.0, "note": "苏清寒手中白玉如意啪嗒滑落桌面"},
            {"p": 30, "pos": "before", "slug": "heavy_iron_chest_unlatch", "sfx_prompt": "Ancient blood-sealed black iron chest lock clicking open and heavy iron lid slowly lifting", "duration_seconds": 3.0, "gain_db": 0.5, "note": "解开血脉禁锁掀开尺许玄铁遗匣"},
            {"p": 34, "pos": "before", "slug": "blood_jade_slip_hum", "sfx_prompt": "Warm resonant spiritual jade chime awakening an ancient recorded memory voice", "duration_seconds": 2.4, "gain_db": -0.5, "note": "泣血玉简贴眉心嗡鸣显音"},
            {"p": 46, "pos": "before", "slug": "bronze_shard_enter_xujie", "motif_id": "motif_xujie_gate", "gain_db": 0.5, "note": "轰！手握焦黑青铜残片沉入墟界，九环荒原彻底解封"},
            {"p": 56, "pos": "after", "slug": "frost_coffin_knock_climax", "motif_id": "motif_frost_coffin_knock", "gain_db": 2.0, "gap_after_s": 1.4, "note": "咚！玄霜古棺内女子冰凉指尖轻轻一叩"},
        ],
    )
    j10, m10 = save_episode_scripts(s10, SCRIPTS_DIR, registry)
    built.append(("E010", j10, m10))

    # =========================================================================
    # E011 · 第11章 满城风雨疑故人，闭门数家珍 (70 paras, 22 quotes)
    # =========================================================================
    md_11 = SOURCE_DIR / "第11章_满城风雨疑故人，闭门数家珍.md"
    s11 = compile_episode_cue_sheet(
        episode_id="E011",
        chapter_number=11,
        source_md_path=md_11,
        source_rel_path=f"02_分章精修正文/{md_11.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_coffin_chill_refine_spike",
                "start_p": 1,
                "title": "第一幕 · 寒气惊退魂，滴血祭飞刺",
                "bgm_prompt": "Icy lingering cosmic sub-bass resonance transitioning into focused subterranean Chinese guqin and metallic refinement tones, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_ten_breath_genelock_rule",
                "start_p": 17,
                "title": "第二幕 · 十息测锁界，火焚旧密卷",
                "bgm_prompt": "Rhythmic disciplined Chinese martial training score, taut heartbeat pulse, crisp string accents and cool analytical tension, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_scare_off_snobbish_uncle",
                "start_p": 31,
                "title": "第三幕 · 奉茶敲族叔，笑谈槐下肥",
                "bgm_prompt": "Sly ironic ancient Chinese chamber underscore, playful plucked sanxian/pipa shifting into chilling deadpan psychological menace, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_blood_manor_iron_token",
                "start_p": 59,
                "title": "第四幕 · 挑袋现骷牌，剑指百草庄",
                "bgm_prompt": "Dark ominous Chinese investigation thriller score, low bowed cello, cold metallic chime and rising nocturnal resolve, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        acoustic_ranges=[(1, 4, "mental_realm")],
        skip_onomatopoeia_paras={2, 61},
        dialogue_specs=[
            {"match": "以我眼下引气七重的微末神识", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬退出墟界冷静复盘"},
            {"match": "无论那口古棺里葬着什么来历", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "立下戒律不轻易念动天渊古音"},
            {"match": "边界清楚了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "测清一阶基因锁十息零代价边界"},
            {"match": "常态开锁洞察破绽", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "定下十息常态与三十息拼命铁律"},
            {"match": "少主，前院来了个不速之客", "role_id": "fu_bo", "tags": "[softly]", "stability": 0.5, "note": "福伯敲板密报来客"},
            {"match": "是住东城柳条胡同的您那位远房三叔公", "role_id": "fu_bo", "tags": "[angry] [sarcastic]", "stability": 0.0, "note": "福伯愤懑说起势利眼陆明远"},
            {"match": "苏家早上刚撤走眼线", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬一眼看穿雇人探底"},
            {"match": "那老奴这就拿扫帚把他轰出去", "role_id": "fu_bo", "tags": "[angry]", "stability": 0.0, "note": "福伯挽袖欲赶人"},
            {"match": "不必，轰出去反而显得咱们心虚", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬借力打力唱空城计"},
            {"match": "让人请进偏厅奉茶", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "借陆明远快嘴传扬神秘高人"},
            {"match": "三叔公稀客", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬掀帘温和登场"},
            {"match": "哎呀呀，大侄子气色看着可比外头瞎传的好多了", "role_id": "snobbish_steward_npc", "tags": "[laughs] [sarcastic]", "stability": 0.0, "note": "陆明远干笑奉承"},
            {"match": "侄儿啊，自家人关起门来说亮话", "role_id": "snobbish_steward_npc", "tags": "[whispers]", "stability": 0.0, "note": "陆明远贼眉鼠眼探问高人底细"},
            {"match": "三叔公说笑了，家父若是回城", "role_id": "lu_jin", "tags": "[sarcastic] [calmly]", "stability": 0.5, "note": "陆烬敲打当年放狗拒借银旧账"},
            {"match": "家父并未归来，只是他老人家生前", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬轻描淡写说出槐树花肥"},
            {"match": "三叔公若是也想见见那位前辈", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "note": "陆烬留耳割舌之言吓破族叔苦胆"},
            {"match": "不、不用了！千万别惊动前辈清修", "role_id": "snobbish_steward_npc", "tags": "[trembling] [shouting]", "stability": 0.0, "note": "陆明远魂不附体惊叫摆手"},
            {"match": "侄儿好生休养，三叔家里炉子上还炖着药", "role_id": "snobbish_steward_npc", "tags": "[trembling]", "stability": 0.0, "note": "陆明远提鞋落荒而逃"},
            {"match": "狗眼看人低的东西", "role_id": "fu_bo", "tags": "[laughs] [hoarsely]", "stability": 0.0, "note": "福伯痛快低哼"},
            {"match": "要的就是他这张快嘴", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬赢得黄金十日空档"},
            {"match": "苏家和玄剑宗别院越是摸不清深浅", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬吩咐挂牌闭门"},
            {"match": "九月十五月圆前，备催脉汤三桶", "role_id": "li_cang", "tags": "[coldly]", "stability": 0.0, "space": "memory_echo", "note": "储物袋夹层朱砂交割单残响"},
        ],
        sfx_blueprint=[
            {"p": 2, "pos": "before", "slug": "frost_wave_soul_shiver", "sfx_prompt": "Piercing sub-zero crystalline frost wave sweeping across frozen earth with a sharp icy ring", "duration_seconds": 2.6, "gain_db": 0.5, "note": "嗡！玄霜古棺亿万分之一寒气震颤识海"},
            {"p": 16, "pos": "before", "slug": "wind_spike_hover", "sfx_prompt": "Razor-thin dark gold flying needle humming crisply in mid-air and zipping silently into a cloth sleeve", "duration_seconds": 2.2, "gain_db": 0.0, "note": "裂风刺炼化悬停没入左袖"},
            {"p": 21, "pos": "after", "slug": "finger_pierce_stone_wall", "sfx_prompt": "Swift martial dash whoosh followed by a single finger strike punching a crisp hole into solid granite wall", "duration_seconds": 2.4, "gain_db": 0.5, "note": "极限燃血步法一指戳穿千斤青石墙"},
            {"p": 30, "pos": "after", "slug": "three_light_one_heavy_knock", "sfx_prompt": "Secret signal of three light knocks and one firm knock on wooden floorboards overhead", "duration_seconds": 2.4, "gain_db": 0.0, "note": "密室上方传来福伯三轻一重暗号敲击声"},
            {"p": 50, "pos": "before", "slug": "teacup_set_down_click", "sfx_prompt": "Ceramic teacup lid clicking crisply and setting down onto a wooden side table in dead quiet", "duration_seconds": 1.8, "gain_db": 0.0, "note": "咔哒！茶盏轻放惊得陆明远手抖"},
            {"p": 61, "pos": "before", "slug": "cut_pouch_iron_token_drop", "sfx_prompt": "Knife ripping tough leather seam followed by a heavy cold iron token clattering onto a stone desk", "duration_seconds": 2.6, "gain_db": 1.0, "note": "嗤啦当啷！挑开储物袋夹层滚落【血庄】铁牌"},
        ],
    )
    j11, m11 = save_episode_scripts(s11, SCRIPTS_DIR, registry)
    built.append(("E011", j11, m11))

    # =========================================================================
    # E012 · 第12章 黑市再交易，上品凝髓丹震鬼樊 (56 paras, 17 quotes)
    # =========================================================================
    md_12 = SOURCE_DIR / "第12章_黑市再交易，上品凝髓丹震鬼樊.md"
    s12 = compile_episode_cue_sheet(
        episode_id="E012",
        chapter_number=12,
        source_md_path=md_12,
        source_rel_path=f"02_分章精修正文/{md_12.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_ancient_marrow_powder",
                "start_p": 1,
                "title": "第一幕 · 灵露点凡药，寒松凝玉散",
                "bgm_prompt": "Serene mystical Chinese alchemy score, gentle bubbling water, luminous guqin harmonics and pure pine-scented spiritual resonance, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_blind_master_shocked",
                "start_p": 13,
                "title": "第二幕 · 暗门入鬼市，一嗅惊瞎叟",
                "bgm_prompt": "Shadowy underground market intrigue score, muted plucked strings, eerie lantern ambience building to sudden breathless astonishment, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_red_sleeve_mistress_debut",
                "start_p": 36,
                "title": "第三幕 · 珠帘摇团扇，红袖赠玄令",
                "bgm_prompt": "Alluring aristocratic ancient Chinese court-and-underworld score, silky bowed erhu, delicate jade bead curtains and unfathomable dignified power, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act4_primordial_chill_warning",
                "start_p": 46,
                "title": "第四幕 · 太古寒息气，夜奔赤水坳",
                "bgm_prompt": "Taut nocturnal Chinese martial espionage score, crisp cold wind, driving low pipa rhythm and resolute hunter momentum into the mountains, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        skip_onomatopoeia_paras={7, 16, 24},
        dialogue_specs=[
            {"match": "这【古方凝髓散】的成色", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬炼成凝髓散推至引气七重巅峰"},
            {"match": "九号牌的客人？比约定的十五早了两天呐", "role_id": "chu_xiazi", "tags": "[laughs]", "stability": 0.0, "note": "褚瞎子听声辨客热络招呼"},
            {"match": "上次那六瓶凝血膏老头子转手卖给镇渊司", "role_id": "chu_xiazi", "tags": "[laughs]", "stability": 0.0, "note": "褚瞎子边拔蜡塞边夸赞销路"},
            {"match": "寒松沁髓，药敛无火", "role_id": "chu_xiazi", "tags": "[gasps] [whispers]", "stability": 0.0, "note": "褚瞎子闻香骇然变调"},
            {"match": "洗髓不伤脉，温养神魂本源", "role_id": "chu_xiazi", "tags": "[trembling] [whispers]", "stability": 0.0, "note": "褚瞎子眼眶排毒震惊失声"},
            {"match": "阁下到底是什么来路？", "role_id": "chu_xiazi", "tags": "[whispers]", "stability": 0.0, "note": "褚瞎子捂紧瓶塞呼吸粗重追问"},
            {"match": "只有两瓶", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬伪装沙哑平静控场"},
            {"match": "这一回我不换凡药", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬开出狂猿髓、敛息符与乌金针清单"},
            {"match": "一瓶这等极品凝髓散", "role_id": "chu_xiazi", "tags": "[calmly]", "stability": 0.0, "note": "褚瞎子公道估价二百四十灵石请东家支账"},
            {"match": "不必麻烦了，这两瓶凝髓散", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "二层珠帘后红袖楼主慵懒威严开口全收"},
            {"match": "见过红袖楼主！", "role_id": "chu_xiazi", "tags": "[calmly]", "stability": 0.5, "note": "褚瞎子起身恭敬行礼"},
            {"match": "这是我鬼樊楼的【玄客令】", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "红袖楼主隔帘轻笑赐玄客令"},
            {"match": "持此令入楼，买卖一应抽成减半", "role_id": "hongxiu_louzhu", "tags": "[calmly]", "stability": 0.5, "note": "红袖楼主许诺鬼樊楼烂舌守信"},
            {"match": "楼主爽快，日后若有成药", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬不卑不亢收下玄客令"},
            {"match": "先生最近夜里出门可千万留神", "role_id": "chu_xiazi", "tags": "[whispers]", "stability": 0.0, "note": "褚瞎子密告玄剑宗强抓十八岁后生入西山"},
            {"match": "对了先生，本座方才闻你那凝髓散尾韵里", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "红袖楼主点破太古寒息气与王都紫衣巡察使"},
            {"match": "多谢楼主金言", "role_id": "lu_jin", "tags": "[hoarsely] [calmly]", "stability": 0.5, "note": "陆烬从容道谢转身赴赤水坳"},
        ],
        sfx_blueprint=[
            {"p": 7, "pos": "before", "slug": "dew_condense_jade_powder", "sfx_prompt": "Three pure spiritual water drops hitting simmering amber medicinal liquid, instantly condensing with a crisp frosty pine chime", "duration_seconds": 2.8, "gain_db": 0.5, "note": "嗤！三滴墟界灵露入鼎凝成羊脂白玉药散"},
            {"p": 16, "pos": "before", "slug": "ebony_token_secret_door", "sfx_prompt": "Wooden token clicking into a hidden iron ring slot followed by a peephole sliding and a heavy secret door opening", "duration_seconds": 2.8, "gain_db": 0.0, "note": "咔哒！九字乌木牌开启染坊熟客暗门"},
            {"p": 24, "pos": "before", "slug": "bamboo_knife_drop_boot", "sfx_prompt": "Small bamboo carving knife dropping onto leather boot and rolling onto stone floor in sudden shock", "duration_seconds": 1.8, "gain_db": 0.0, "note": "啪嗒！褚瞎子闻到凝髓散竹刀掉在脚背"},
            {"p": 37, "pos": "before", "slug": "silk_fan_pearl_curtain", "sfx_prompt": "Delicate silk hand fan swaying softly behind gently clinking jade and pearl curtains in an upper stone pavilion", "duration_seconds": 3.0, "gain_db": 0.0, "note": "二层石阁珠帘微响与红袖楼主团扇轻摇"},
            {"p": 42, "pos": "before", "slug": "wooden_tray_spirit_stones", "sfx_prompt": "jade bead curtain parting, light footsteps descending stone stairs, and a rosewood tray laden with clinking spirit stones set down", "duration_seconds": 3.2, "gain_db": 0.0, "note": "白狐面具侍女捧一百八十枚灵石与玄客令下楼"},
            {"p": 55, "pos": "before", "slug": "night_wind_leap_canal", "sfx_prompt": "Cold autumn night wind rushing across dark rooftops as a swift martial figure leaps silently toward mountain shadows", "duration_seconds": 3.0, "gain_db": 0.0, "note": "出染坊迎冷冽秋风直奔西郊赤水坳"},
        ],
    )
    j12, m12 = save_episode_scripts(s12, SCRIPTS_DIR, registry)
    built.append(("E012", j12, m12))

    return built


if __name__ == "__main__":
    items = build_all_batch2()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if "--compile-only" not in sys.argv:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=4)
