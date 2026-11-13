"""Build, validate, render, and archive Batch 4: Episodes E018–E022 (Chapters 18–22)."""

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


def build_all_batch4() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E018 · 第18章 血月盲区，无瑕筑基成！ (69 paras, 19 quotes)
    # =========================================================================
    md_18 = SOURCE_DIR / "第18章_血月盲区，无瑕筑基成！.md"
    s18 = compile_episode_cue_sheet(
        episode_id="E018",
        chapter_number=18,
        source_md_path=md_18,
        source_rel_path=f"02_分章精修正文/{md_18.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_new_moon_hundred_forges",
                "start_p": 1,
                "title": "第一幕 · 朔月盲区至，百锻铸金基",
                "bgm_prompt": "Monumental Chinese xianxia breakthrough soundtrack, deep rhythmic anvil-like war drums, icy dragon-blood strings and blazing golden spiritual transcendence, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act2_taming_venom_swarm_fire_seed",
                "start_p": 25,
                "title": "第二幕 · 灵识镇奇虫，炉底妖煞火",
                "bgm_prompt": "Mysterious commanding ancient Chinese spirit-realm score, deep bronze resonance, sharp crystalline textures and dangerous ancient violet flame pulse, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_number_zero_bronze_plate",
                "start_p": 45,
                "title": "第三幕 · 双铜合星轨，宿命零号牌",
                "bgm_prompt": "Vast cosmic ancient Chinese destiny theme, solemn xiao flute, deep cosmic chimes and resolute heroic strings defying heaven's chessboard, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_pei_xuandu_emerges_early",
                "start_p": 58,
                "title": "第四幕 · 裴贼提前出，玉镯点后火",
                "bgm_prompt": "Cold pre-dawn Chinese garrison suspense score, crackling brazier warmth shifting into urgent political storm strings, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[(29, 57, "mental_realm")],
        skip_onomatopoeia_paras={5, 9, 18, 31, 36, 50},
        dialogue_specs=[
            {"match": "就是此刻，开锁，压基", "role_id": "lu_jin", "tags": "[dramatically]", "stability": 0.0, "note": "陆烬吞龙鲤血全开基因锁百锻压基"},
            {"match": "第一百锻，给我凝", "role_id": "lu_jin", "tags": "[shouting]", "stability": 0.0, "space": "mental_realm", "note": "灵魂低吼凝成九滴暗金无瑕灵液"},
            {"match": "以我现在的筑基灵识强度", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "二十丈筑基灵识底气十足"},
            {"match": "镇！", "role_id": "lu_jin", "tags": "[shouting]", "stability": 0.0, "space": "mental_realm", "note": "筑基灵识磨盘碾碎二十余只金背毒虫"},
            {"match": "三阶大妖凝出的【焚锁妖煞火】", "role_id": "lu_jin", "tags": "[gasps] [whispers]", "stability": 0.0, "space": "mental_realm", "note": "发现青铜丹炉底紫青火种"},
            {"match": "这是日后冲击筑基中期与重铸父亲", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "space": "mental_realm", "note": "暂封焚锁妖煞火留作杀手锏"},
            {"match": "不管做局的人是谁，既然如今活在这具身体里", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "手握【零号】青铜铭牌立下执棋誓言"},
            {"match": "奇了怪了，少主不过在祠堂歇了半个时辰", "role_id": "fu_bo", "tags": "[softly]", "stability": 0.5, "note": "廊下福伯醒来惊叹少主脱胎换骨"},
            {"match": "许是前几日配的养骨药起了效用", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬温声替老人披上厚夹袄"},
            {"match": "夜深露重，福伯回屋睡吧", "role_id": "lu_jin", "tags": "[softly]", "stability": 0.5, "note": "陆烬赴北衙销假"},
            {"match": "哎，少主夜路慢些走", "role_id": "fu_bo", "tags": "[softly]", "stability": 0.5, "note": "福伯叮嘱"},
            {"match": "怪事……老子怎么觉着你小子身上那股血腥气", "role_id": "qin_lie", "tags": "[whispers]", "stability": 0.5, "note": "秦烈狐疑惊叹陆烬深潭顽石般的气机"},
            {"match": "托秦伯父的福，侥幸成了", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬含蓄应答"},
            {"match": "成了就好！成了总算多三分保命本钱", "role_id": "qin_lie", "tags": "[sighs]", "stability": 0.5, "note": "秦烈长舒一口气"},
            {"match": "你回来得正好，半个时辰前衙门刚接到", "role_id": "qin_lie", "tags": "[hoarsely] [whispers]", "stability": 0.0, "note": "秦烈凝重通报裴玄度破筑基中期提前出关"},
            {"match": "裴玄度出关了？十月十五的纳妾大典呢", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬眸光微凝"},
            {"match": "那小畜生许是因为百草庄被烧缺了辅药", "role_id": "qin_lie", "tags": "[angry] [hoarsely]", "stability": 0.0, "note": "纳妾提前至十月初六"},
            {"match": "而且玄剑宗山上还派了三名筑基后期", "role_id": "qin_lie", "tags": "[hoarsely]", "stability": 0.0, "note": "三大筑基后期长老护驾"},
            {"match": "多谢秦伯父提醒，侄儿心里有数", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬抚摸染血玉镯冷笑布局"},
        ],
        sfx_blueprint=[
            {"p": 5, "pos": "before", "slug": "swallow_dragon_carp_blood", "sfx_prompt": "Icy crystalline surge colliding with roaring molten internal qi inside a silent stone chamber", "duration_seconds": 3.0, "gain_db": 1.0, "note": "轰！吞服铁甲寒潭龙鲤心头真血冰火激荡"},
            {"p": 9, "pos": "before", "slug": "genelock_hundred_forges", "motif_id": "motif_genelock_awaken", "gain_db": 1.5, "note": "嗡！全开基因锁百锻压缩真气"},
            {"p": 18, "pos": "before", "slug": "nine_golden_drops_condense", "sfx_prompt": "Crisp crystalline compression snap followed by nine heavy liquid-gold droplets chiming with deep oceanic power", "duration_seconds": 3.2, "gain_db": 1.5, "note": "咔嚓哗啦！凝成九滴暗金无瑕灵液，寿涨二百载"},
            {"p": 31, "pos": "before", "slug": "thirty_eight_beetles_crush", "sfx_prompt": "Fierce metallic insect swarm buzz suddenly crushed flat by an invisible heavy spiritual shockwave into crisp powder", "duration_seconds": 3.2, "gain_db": 1.5, "note": "嗡嗡噼啪！筑基灵识碾碎金背噬毒虫群"},
            {"p": 50, "pos": "before", "slug": "two_bronze_halves_snap_zero", "sfx_prompt": "Two ancient jagged bronze plates clicking and fusing together with a deep cosmic starlight hum", "duration_seconds": 3.0, "gain_db": 1.5, "note": "咔哒！两块焦黑青铜残片咬合拼成【零号】铭牌"},
        ],
    )
    j18, m18 = save_episode_scripts(s18, SCRIPTS_DIR, registry)
    built.append(("E018", j18, m18))

    # =========================================================================
    # E019 · 第19章 苏女叩旧门，迟来的悔意不值钱 (44 paras, 14 quotes)
    # =========================================================================
    md_19 = SOURCE_DIR / "第19章_苏女叩旧门，迟来的悔意不值钱.md"
    s19 = compile_episode_cue_sheet(
        episode_id="E019",
        chapter_number=19,
        source_md_path=md_19,
        source_rel_path=f"02_分章精修正文/{md_19.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_poison_spike_rainy_gift",
                "start_p": 1,
                "title": "第一幕 · 碎炭传贺礼，冷雨淬毒刺",
                "bgm_prompt": "Cold autumn rain and sparse icy guqin notes over a quiet ancestral hall, calm karma coming full circle, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act2_su_qinghan_begs_at_gate",
                "start_p": 10,
                "title": "第二幕 · 嫁衣染污泥，雨夜叩旧门",
                "bgm_prompt": "Tragic desperate Chinese erhu and rainstorm underscore contrasted against cold unmoved silence behind closed doors, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_blood_map_karma_severed",
                "start_p": 28,
                "title": "第三幕 · 回旋刀扎心，指血留阵图",
                "bgm_prompt": "Bleak desolate ancient Chinese xiao and low strings, bitter regret and cold finality in pouring night rain, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act4_four_swords_lock_city",
                "start_p": 38,
                "title": "第四幕 · 四剑裂雨幕，法旨封四门",
                "bgm_prompt": "Thunderous overwhelming dark xianxia sky-pressure score, roaring storm thunder, screaming flying-sword resonance andbrass-like war horns, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        skip_onomatopoeia_paras={8, 11, 41},
        dialogue_specs=[
            {"match": "谁啊？大半夜的拍什么门", "role_id": "fu_bo", "tags": "[hoarsely]", "stability": 0.5, "note": "福伯披蓑衣提灯看门缝"},
            {"match": "少、少主！奇了大怪了，门外头跪着苏家", "role_id": "fu_bo", "tags": "[gasps] [whispers]", "stability": 0.0, "note": "福伯小跑进祠堂震惊禀报"},
            {"match": "陆烬！陆大哥！我知道你在里面", "role_id": "su_qinghan", "tags": "[crying] [shouting]", "stability": 0.0, "note": "苏清寒跪在积水石阶凄惶拍门哭求"},
            {"match": "是我瞎了眼！是我有眼无珠信了裴玄度", "role_id": "su_qinghan", "tags": "[crying] [desperately]", "stability": 0.0, "note": "苏清寒磕头悔恨哀求救命"},
            {"match": "少主，要老奴出去赶她走么", "role_id": "fu_bo", "tags": "[coldly]", "stability": 0.5, "note": "福伯毫无同情请示"},
            {"match": "不必开门，脏了门槛", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬抿凉茶淡漠吐出六字"},
            {"match": "福伯只管隔着门传我一句话便是", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬原话奉还五十灵石两清因果"},
            {"match": "不……你骗我！厉苍执事和二叔明明", "role_id": "su_qinghan", "tags": "[crying] [shouting]", "stability": 0.0, "note": "苏清寒指甲抓门嘶喊"},
            {"match": "我有赤松岭别院的换防阵图", "role_id": "su_qinghan", "tags": "[desperately] [shouting]", "stability": 0.0, "note": "苏清寒抛出别院换防阵图筹码"},
            {"match": "苏小姐既然听过玄剑宗的手段", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬隔雨幕点破本命血种死局"},
            {"match": "把你知道的别院阵眼与丹房暗道留在门槛石缝下", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬收阵图打发其往南门引开追兵"},
            {"match": "福伯，收拾两件换洗衣裳", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬果断下令走暗渠撤离"},
            {"match": "啊？少主，咱们现在就走", "role_id": "fu_bo", "tags": "[gasps]", "stability": 0.0, "note": "福伯一愣"},
            {"match": "传玄剑宗赤阳老祖法旨", "role_id": "pei_xuandu", "tags": "[angry] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "裴玄度立飞剑携三长老雷音封城四门"},
        ],
        sfx_blueprint=[
            {"p": 5, "pos": "before", "slug": "autumn_rain_return_callback", "motif_id": "motif_beiyuan_cold_rain", "placement": "overlay_next", "gain_db": -6.0, "gap_after_s": 0.8, "note": "北渊深秋冷雨夜母题回响（呼应第一集退婚夜）"},
            {"p": 8, "pos": "before", "slug": "poison_spike_seal_hum", "sfx_prompt": "Dark gold flying needle humming softly as venomous spiritual aura seals into its razor tip", "duration_seconds": 2.2, "gain_db": 0.0, "note": "嗡！金背毒煞淬入裂风刺"},
            {"p": 11, "pos": "before", "slug": "desperate_pounding_wet_gate", "sfx_prompt": "Slipping footsteps in mud puddles followed by frantic wet hands pounding desperately on heavy wooden courtyard doors in pouring rain", "duration_seconds": 3.4, "gain_db": 1.5, "note": "啪啪啪！苏清寒雨夜拍门哭求"},
            {"p": 36, "pos": "before", "slug": "tear_silk_robe_flee_mud", "sfx_prompt": "Ripping silk inner sleeve followed by stumbling footsteps splashing away into a rainy alley", "duration_seconds": 2.8, "gain_db": 0.0, "note": "撕破白衣咬指画阵图狼狈逃往南城"},
            {"p": 41, "pos": "before", "slug": "four_flying_swords_thunder", "sfx_prompt": "Deafening thunderclap and four supersonic flying-sword sonic booms tearing open storm clouds over a city", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰隆！裴玄度携三大筑基后期长老剑虹压城"},
        ],
    )
    j19, m19 = save_episode_scripts(s19, SCRIPTS_DIR, registry)
    built.append(("E019", j19, m19))

    # =========================================================================
    # E020 · 第20章 第二次重估，谁才是猎物？ (56 paras, 18 quotes)
    # =========================================================================
    md_20 = SOURCE_DIR / "第20章_第二次重估，谁才是猎物？.md"
    s20 = compile_episode_cue_sheet(
        episode_id="E020",
        chapter_number=20,
        source_md_path=md_20,
        source_rel_path=f"02_分章精修正文/{md_20.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_city_terror_rain_pavilion",
                "start_p": 1,
                "title": "第一幕 · 全城坠冰窖，只身赴听雨",
                "bgm_prompt": "Heavy oppressive storm-besieged ancient Chinese city score transitioning into quiet sandalwood-scented underground stone pavilion intrigue, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_remove_iron_hat_reveal",
                "start_p": 13,
                "title": "第二幕 · 摘笠露真容，谁求挡剑人",
                "bgm_prompt": "Taut dramatic ancient Chinese chamber confrontation score, sharp pipa plucks, rising spiritual pressure and breathless shock, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_shatter_jade_cup_alliance",
                "start_p": 28,
                "title": "第三幕 · 一指碎玉盏，红袖拜丹师",
                "bgm_prompt": "Commanding charismatic Chinese xianxia power-shift theme, deep resonant golden bass chime, soaring strings of awe and grand alliance, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_soul_banner_bait_sun_he",
                "start_p": 45,
                "title": "第四幕 · 白幡书血字，引狗入西林",
                "bgm_prompt": "Fierce stormy nocturnal Chinese hunter-thriller score, pouring rain thunder, rapid taut war drums and lethal trap springing, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        skip_onomatopoeia_paras={16, 30, 32, 34},
        dialogue_specs=[
            {"match": "楼主，玄剑宗这回是彻底撕破脸皮发疯了", "role_id": "chu_xiazi", "tags": "[desperately] [whispers]", "stability": 0.0, "note": "褚瞎子踱步担忧九号古丹师被吓走"},
            {"match": "玄剑宗赤阳老怪寿元见底", "role_id": "hongxiu_louzhu", "tags": "[calmly]", "stability": 0.5, "note": "红袖楼主慵懒隔帘回应"},
            {"match": "启禀楼主、褚老，持【玄客令】的九号先生到了", "role_id": "female_maid_npc", "tags": "[calmly]", "stability": 0.5, "note": "白狐面具侍女通禀"},
            {"match": "哦？这节骨眼上还敢出门", "role_id": "chu_xiazi", "tags": "[laughs]", "stability": 0.0, "note": "褚瞎子喜迎"},
            {"match": "陆……陆家少主？", "role_id": "hongxiu_louzhu", "tags": "[gasps]", "stability": 0.0, "note": "红袖楼主看清陆烬十八岁真容失态轻呼"},
            {"match": "什么陆家少主？哪个陆家少主", "role_id": "chu_xiazi", "tags": "[gasps]", "stability": 0.0, "note": "褚瞎子耳朵狂跳追问"},
            {"match": "楼主是说……上面玄剑宗四名筑基高手", "role_id": "chu_xiazi", "tags": "[trembling] [whispers]", "stability": 0.0, "note": "褚瞎子震惊不可置信"},
            {"match": "正是陆某", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬恢复清朗冷冽本音"},
            {"match": "半刻钟前，家仆福伯与一名受伤故人", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "托付鬼樊楼护送福伯与石猛出城"},
            {"match": "陆公子好深的城府，竟把整座北渊城", "role_id": "hongxiu_louzhu", "tags": "[coldly]", "stability": 0.5, "note": "红袖楼主散发筑基后期气机施压试探"},
            {"match": "谁告诉楼主，我是来求鬼樊楼替我挡剑的", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "陆烬纹丝不动淡然反问"},
            {"match": "筑、筑基境？灵液暗凝如渊", "role_id": "chu_xiazi", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "褚瞎子撞翻圆凳骇然失声"},
            {"match": "原来真正踏进死局的猎物，根本不是陆公子", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.0, "note": "红袖楼主跨出珠帘彻底改观"},
            {"match": "小女子方才眼拙，慢待了陆丹师", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "红袖楼主敛衽深福改称陆丹师"},
            {"match": "这三张古方归贵楼。未来三夜", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "三张二阶古方买断全城眼线与破阵天雷珠"},
            {"match": "成交！三枚【天雷子】乃是本座压箱底的私藏", "role_id": "hongxiu_louzhu", "tags": "[dramatically]", "stability": 0.0, "note": "红袖楼主重金押注奉送天雷子"},
            {"match": "赤松西林，先收一息！", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "space": "memory_echo", "note": "陆宅白幡鸡血八字战书残响"},
            {"match": "狂妄小辈！竟敢调虎离山袭我别院后山", "role_id": "sect_elder_antagonist", "tags": "[angry] [shouting]", "stability": 0.0, "note": "孙鹤长老暴跳如雷中计追出西门"},
        ],
        sfx_blueprint=[
            {"p": 3, "pos": "after", "slug": "qin_lie_cleave_desk", "sfx_prompt": "Heavy iron broadsword angrily cleaving a wooden officer desk in half inside a locked barracks", "duration_seconds": 2.4, "gain_db": 0.5, "note": "北衙内秦烈怒劈桌案"},
            {"p": 16, "pos": "before", "slug": "remove_wet_iron_hat", "sfx_prompt": "Dripping wet black iron conical hat lifted off and set down onto stone floor in dead silence", "duration_seconds": 2.4, "gain_db": 0.0, "note": "哗！摘下黑铁斗笠显露十八岁真容"},
            {"p": 30, "pos": "before", "slug": "golden_qi_pulverize_jade_cup", "sfx_prompt": "Deep golden spiritual bass pulse followed by a solid jade teacup crumbling into fine powder and a wooden stool knocking over", "duration_seconds": 3.2, "gain_db": 1.5, "note": "嗡咔嚓砰！一指暗金筑基灵压震粉玉盏，褚瞎子撞翻圆凳"},
            {"p": 36, "pos": "before", "slug": "step_through_pearl_curtain", "sfx_prompt": "Jade and pearl curtain parting briskly with silk robes rustling forward", "duration_seconds": 2.2, "gain_db": 0.0, "note": "哗啦！红袖楼主一步跨出珠帘"},
            {"p": 47, "pos": "before", "slug": "sword_blast_empty_courtyard", "sfx_prompt": "Torrential rain and thunder as a flying sword blasts open wooden gates and white cloth banner snaps in the wind", "duration_seconds": 3.4, "gain_db": 1.0, "note": "孙长老劈门冲入空宅见鸡血白幡"},
        ],
    )
    j20, m20 = save_episode_scripts(s20, SCRIPTS_DIR, registry)
    built.append(("E020", j20, m20))

    # =========================================================================
    # E021 · 第21章 风雪西林伏杀，第一滴筑基血 (56 paras, 15 quotes)
    # =========================================================================
    md_21 = SOURCE_DIR / "第21章_风雪西林伏杀，第一滴筑基血.md"
    s21 = compile_episode_cue_sheet(
        episode_id="E021",
        chapter_number=21,
        source_md_path=md_21,
        source_rel_path=f"02_分章精修正文/{md_21.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_sleet_ravine_ambush",
                "start_p": 1,
                "title": "第一幕 · 雪夜落鹰涧，死血诱贪狼",
                "bgm_prompt": "Freezing sleet-swept Chinese mountain ambush score, eerie low bamboo flute, taut pizzicato strings and approaching hunter tension, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_corrode_turtle_shield",
                "start_p": 13,
                "title": "第二幕 · 毒砂封石谷，飞刺蚀龟盾",
                "bgm_prompt": "High-velocity Chinese xianxia spell-and-blade combat score, pounding war percussion, aggressive pipa and sizzling venomous tension, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_ten_moves_slay_elder",
                "start_p": 26,
                "title": "第三幕 · 十招斩筑基，弹剑串六徒",
                "bgm_prompt": "Overwhelming ferocious Chinese martial slaughter score, thunderous drums, razor-sharp erhu cries and unstoppable dark-gold momentum, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_sect_master_urgent_decree",
                "start_p": 44,
                "title": "第四幕 · 矿洞清重宝，老怪五日限",
                "bgm_prompt": "Dark ominous subterranean Chinese mystery score, howling distant blizzard wind and chilling zombie-ancestor dread, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        skip_onomatopoeia_paras={14, 22, 24, 31, 34, 39},
        dialogue_specs=[
            {"match": "启禀陆丹师，西便门刚开", "role_id": "male_guard_captain", "tags": "[whispers]", "stability": 0.5, "note": "鬼樊楼暗哨涧底密报孙鹤出城"},
            {"match": "知道了，通知沿途兄弟全部撤回地下暗渠", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬冷静下令撤哨"},
            {"match": "遵命！", "role_id": "male_guard_captain", "tags": "[whispers]", "stability": 0.5, "note": "暗哨退去"},
            {"match": "孙师叔，林深雪滑，要不要等裴师兄", "role_id": "male_disciple_a", "tags": "[shouting]", "stability": 0.0, "note": "随行执事喘息劝阻"},
            {"match": "等他们过来，抓捕天渊血引的头功", "role_id": "sect_elder_antagonist", "tags": "[arrogant] [coldly]", "stability": 0.0, "note": "孙鹤贪功斥责"},
            {"match": "就在前面百丈乱石坡！", "role_id": "sect_elder_antagonist", "tags": "[shouting]", "stability": 0.0, "note": "孙鹤单骑扎入落鹰涧"},
            {"match": "不好！是死血诱饵！", "role_id": "sect_elder_antagonist", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "黑鸦惊飞识破死血布条"},
            {"match": "藏头露尾的鼠辈！以为凭一座残缺困阵", "role_id": "sect_elder_antagonist", "tags": "[angry] [shouting]", "stability": 0.0, "note": "孙鹤祭出二阶青罡玄龟盾"},
            {"match": "给老夫滚出来受死！", "role_id": "sect_elder_antagonist", "tags": "[shouting]", "stability": 0.0, "note": "青芒剑斩阵眼"},
            {"match": "孙长老不是急着抢头功么，陆某这便送你上路", "role_id": "lu_jin", "tags": "[coldly]", "stability": 0.5, "note": "风雪毒雾中陆烬从天而降"},
            {"match": "什么鬼毒？这股灵识压迫", "role_id": "sect_elder_antagonist", "tags": "[gasps] [shouting]", "stability": 0.0, "note": "二阶龟盾被蚀穿骇然惊觉陆烬筑基"},
            {"match": "太慢了！", "role_id": "lu_jin", "tags": "[coldly] [shouting]", "stability": 0.0, "note": "陆烬欺入怀中暴喝"},
            {"match": "孙、孙长老死了！", "role_id": "male_disciple_a", "tags": "[trembling] [shouting]", "stability": 0.0, "note": "阵外内门弟子见无头尸骇叫"},
            {"match": "魔鬼！快发剑符向裴师兄求救", "role_id": "male_disciple_b", "tags": "[trembling] [shouting]", "stability": 0.0, "note": "残余弟子肝胆俱裂溃逃"},
            {"match": "赤阳师叔祖死关生变，紫府道胎已半化尸煞", "role_id": "li_cang", "tags": "[dramatically]", "stability": 0.0, "space": "memory_echo", "note": "赤红传令玉简掌门十万火急密令残响"},
        ],
        sfx_blueprint=[
            {"p": 11, "pos": "before", "slug": "crow_startle_sleet", "sfx_prompt": "Startled black crow cawing harshly and flapping wings up from snowy rocks in howling mountain wind", "duration_seconds": 2.4, "gain_db": 0.5, "note": "黑鸦扑棱棱惊飞露出死血诱饵"},
            {"p": 14, "pos": "before", "slug": "ravine_array_poison_cloud", "sfx_prompt": "Twelve formation flags humming up from frozen mud followed by a sack of corrosive poison sand bursting into roaring wind", "duration_seconds": 3.2, "gain_db": 1.5, "note": "轰！绝灵杀阵合拢，二阶腐灵毒砂炸开"},
            {"p": 24, "pos": "before", "slug": "venom_spike_corrode_shield", "sfx_prompt": "Supersonic metal needle clanging onto an energy shield followed by violent acid-like sizzling eating through spiritual barrier", "duration_seconds": 3.0, "gain_db": 1.5, "note": "铛滋滋滋！裂风刺破灵奇毒两息蚀穿二阶玄龟盾"},
            {"p": 31, "pos": "before", "slug": "duanyue_smash_flying_sword", "sfx_prompt": "Colossal heavy broadsword slamming a flying sword and its wielder crashing into a rocky cliff wall, followed by a clean throat slash", "duration_seconds": 3.4, "gain_db": 2.0, "note": "铛噗嗤！断岳砸飞青芒剑，一刀抹喉斩孙鹤"},
            {"p": 39, "pos": "before", "slug": "flick_flying_sword_skewer", "sfx_prompt": "Finger flicking a captured flying sword shooting like lightning through six steel blades and pinning into a tree trunk", "duration_seconds": 2.8, "gain_db": 1.5, "note": "嗤嗤嗤！弹指飞射青芒剑串杀六名内门精锐"},
            {"p": 55, "pos": "before", "slug": "crush_jade_slip_powder", "sfx_prompt": "Bare hand calmly crushing a red jade slip into trickling stone dust inside a quiet cave", "duration_seconds": 2.2, "gain_db": 0.0, "note": "捏碎赤红传令玉简"},
        ],
    )
    j21, m21 = save_episode_scripts(s21, SCRIPTS_DIR, registry)
    built.append(("E021", j21, m21))

    # =========================================================================
    # E022 · 第22章 暗流站队，风雨欲来的北渊城 (49 paras, 15 quotes)
    # =========================================================================
    md_22 = SOURCE_DIR / "第22章_暗流站队，风雨欲来的北渊城.md"
    s22 = compile_episode_cue_sheet(
        episode_id="E022",
        chapter_number=22,
        source_md_path=md_22,
        source_rel_path=f"02_分章精修正文/{md_22.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_city_shock_nine_deaths_herb",
                "start_p": 1,
                "title": "第一幕 · 全城惊恶蛟，息壤育替草",
                "bgm_prompt": "Hushed tense Chinese city rumors transitioning into luminous mystical spirit-garden guqin and vital growth resonance, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_su_clan_jailed_qin_note",
                "start_p": 16,
                "title": "第二幕 · 苏氏满门锁，秦烈欲劫营",
                "bgm_prompt": "Serious strategic underground chamber Chinese score, low cello, crisp pipa and warm unspoken loyalty toward an old soldier, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act3_wax_pill_over_alley_wall",
                "start_p": 32,
                "title": "第三幕 · 残阳老榆巷，弹丸安义伯",
                "bgm_prompt": "Quiet dusk stealth Chinese underscore, sparse flute over deserted streets building subtle foreboding tension under crimson clouds, instrumental only, no vocals",
                "bgm_duration_s": 80.0,
            },
            {
                "act_id": "act4_hundred_zhang_blood_moon_eye",
                "start_p": 37,
                "title": "第四幕 · 血幡拽残月，竖瞳锁无瑕",
                "bgm_prompt": "Apocalyptic cosmic horror xianxia cliffhanger soundtrack, colossal sub-bass blood pillar roar, terrifying sky-eye drone and pounding war drums, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[(9, 15, "mental_realm")],
        skip_onomatopoeia_paras={16, 38, 42, 46},
        dialogue_specs=[
            {"match": "陆丹师，福伯与那位叫石猛的小兄弟", "role_id": "hongxiu_louzhu", "tags": "[calmly]", "stability": 0.5, "note": "红袖楼主亲自报平安送抵白鹤药庄"},
            {"match": "有劳楼主费心", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬起身致谢"},
            {"match": "丹师客气了，如今我们可是一条船上的人", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "红袖楼主呈上两份密报"},
            {"match": "本楼今日已彻底切断城内黑市一切疗伤丹药", "role_id": "hongxiu_louzhu", "tags": "[calmly]", "stability": 0.5, "note": "切断赤松岭散货补给"},
            {"match": "裴玄度把苏家给抄了？", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬挑眉看第一份密报"},
            {"match": "岂止是抄家！", "role_id": "hongxiu_louzhu", "tags": "[sarcastic]", "stability": 0.0, "note": "红袖楼主冷笑"},
            {"match": "今早苏正阳带着苏牧拉了三车灵石家产", "role_id": "hongxiu_louzhu", "tags": "[sarcastic]", "stability": 0.5, "note": "苏氏全族七十口被锁进地牢充作血曲"},
            {"match": "这是镇渊司北衙传出来的？", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬看第二份秦烈密信"},
            {"match": "是丙字队那位独眼队正秦烈", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "红袖楼主说明口信来源"},
            {"match": "苏牧被扣在赤松岭后，秦烈暗中联络了", "role_id": "hongxiu_louzhu", "tags": "[softly]", "stability": 0.5, "note": "秦烈欲拼官皮带三十老卒护陆烬突围"},
            {"match": "若我不亲自去知会秦伯父一声按兵不动", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬决意亲自去止住秦烈莽撞"},
            {"match": "楼主先替我盯紧赤松岭别院另外两名长老", "role_id": "lu_jin", "tags": "[calmly]", "stability": 0.5, "note": "陆烬披氅出发北衙后巷"},
            {"match": "陆丹师万万小心！", "role_id": "hongxiu_louzhu", "tags": "[desperately]", "stability": 0.0, "note": "红袖楼主急忙提醒"},
            {"match": "方才探子回报，裴玄度今日午后一直在别院", "role_id": "hongxiu_louzhu", "tags": "[whispers]", "stability": 0.0, "note": "预警祭天台邪门血色阵盘"},
            {"match": "找到了！没有命线的天渊漏网异类", "role_id": "pei_xuandu", "tags": "[laughs] [shouting]", "stability": 0.0, "space": "vast_hall", "note": "百丈高空裴玄度借引月锁魂幡锁定陆烬狂笑"},
        ],
        sfx_blueprint=[
            {"p": 13, "pos": "before", "slug": "nine_deaths_orchid_sprout", "sfx_prompt": "Mystical crystalline soil shimmering warmly as a ruby-red spirit herb rapidly sprouts three leaves", "duration_seconds": 2.6, "gain_db": 0.0, "note": "息壤残灰点化枯种破土长成九死血替草"},
            {"p": 16, "pos": "before", "slug": "three_polite_stone_knocks", "sfx_prompt": "Three polite crisp knocks on a stone chamber door followed by sliding stone and light footsteps", "duration_seconds": 2.4, "gain_db": 0.0, "note": "笃笃笃！红袖楼主叩门送密报"},
            {"p": 34, "pos": "after", "slug": "flick_wax_pill_teabowl", "sfx_prompt": "Tiny wax pill flicked briskly through air and dropping with a clean clink into a porcelain tea bowl", "duration_seconds": 2.0, "gain_db": 0.0, "note": "屈指弹蜡丸纸条落入秦烈茶碗"},
            {"p": 38, "pos": "before", "slug": "ten_zhang_blood_pillar_sky", "sfx_prompt": "Cataclysmic subterranean blood-altar eruption shooting a massive crimson energy pillar into storm clouds", "duration_seconds": 3.6, "gain_db": 2.0, "note": "轰隆隆！赤松岭冲起十丈血柱催动引月锁魂幡"},
            {"p": 46, "pos": "before", "slug": "blood_moon_eye_lock_beam", "sfx_prompt": "Terrifying cosmic sub-bass drone and piercing crimson light beam locking down from the sky with two screaming sword auras", "duration_seconds": 3.8, "gain_db": 2.0, "note": "轰！百丈血月竖瞳锁定无瑕之躯，双长老十丈剑罡轰落"},
        ],
    )
    j22, m22 = save_episode_scripts(s22, SCRIPTS_DIR, registry)
    built.append(("E022", j22, m22))

    return built


if __name__ == "__main__":
    items = build_all_batch4()
    for ep_id, jp, mp in items:
        print(f"[COMPILED & VALIDATED] {ep_id}: {jp.name}", flush=True)
    if "--compile-only" not in sys.argv:
        for ep_id, jp, mp in items:
            render_and_archive_episode(ep_id, jp, mp, workers=4)
