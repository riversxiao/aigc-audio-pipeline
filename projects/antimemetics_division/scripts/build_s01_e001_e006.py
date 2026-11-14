#!/usr/bin/env python3
"""Compile & strictly validate all 6 unabridged episodes (E001–E006) + 6-line Audition Pack
for 《逆模因部》(There Is No Antimemetics Division — SCP Wiki V1, CC BY-SA 3.0)."""

from __future__ import annotations

import json
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from aigc_audio_pipeline.compiler import compile_episode_cue_sheet, save_episode_scripts
from aigc_audio_pipeline.models import EpisodeCueSheet, TimelineCue, VoiceCastingRegistry, utc_now_iso
from aigc_audio_pipeline.polyphones import compute_tts_text_override

SOURCE_DIR = PROJECT_DIR / "source_chapters"
CASTING_DIR = PROJECT_DIR / "00_声音选角档案与进度台账"
AUDITION_DIR = PROJECT_DIR / "01_声线试听小样"
SCRIPTS_DIR = PROJECT_DIR / "02_分集广播剧台本"
REGISTRY_PATH = CASTING_DIR / "voice_casting_registry.json"
LEDGER_PATH = CASTING_DIR / "production_progress_ledger.json"


def build_audition_pack(registry: VoiceCastingRegistry) -> Path:
    """Build the 6-line core cast audition cue sheet (`E001_AUDITION_A_逆模因部六句试听清单.json`)."""
    lines = [
        (
            "aud_01_narrator_hook",
            "narrator",
            "[calmly] 你该如何收容一个你既无法记录、也无法记住的东西？ [whispers] 欢迎来到逆模因部。不，今天不是你第一天上班。",
            0.0,
            "dry",
            "检验旁白冷峻硬核科幻悬疑质感，以及从克制审视切换至贴耳低语的压迫感",
        ),
        (
            "aud_02_terminal_scp055",
            "db_terminal",
            "项目编号：SCP-055。项目等级：Keter。特殊收容措施：任何情况下严禁在收容室外安排安保警卫。",
            1.0,
            "mental_realm",
            "检验SCiPNET五级机密终端绝对零情绪的冷冽播报质感与多音字/编号读音",
        ),
        (
            "aud_03_marion_chief",
            "marion_wheeler",
            "[coldly] 你这蠢货，我是你们的逆模因部部长。 [whispers] 这世上，根本就没有逆模因部。",
            0.0,
            "dry",
            "检验女一号玛丽安·惠勒四十九岁铁腕部长的锋利气场与终局贴耳绝唱",
        ),
        (
            "aud_04_paul_kim_eureka",
            "paul_kim",
            "[rushed] 手机是一块塞满高密度信息的实心砖头！在我之前，从来没有人试过把信息本身当成投射武器砸过去！",
            0.0,
            "dry",
            "检验保罗·金在绝境实验室里思维电光石火爆发的青年学者张力",
        ),
        (
            "aud_05_grey_predator",
            "alastair_grey",
            "[calmly] 第一天上班够呛吧？我叫阿拉斯泰尔·格雷。 [condescending] 你原本精通四门语言，现在只剩一门了，而且很快就会归零。",
            0.0,
            "dry",
            "检验SCP-4739灰西装捕食者温文尔雅却令人毛骨悚然的非人微笑感",
        ),
        (
            "aud_06_marness_warning",
            "lyn_marness",
            "[whispers] 如果你知道它存在，它就知道你存在。 [shouting] 整个逆模因部本身就是一个死循环！我们永远也收容不了它！",
            0.0,
            "dry",
            "检验初代创始人林·马内斯从毛骨悚然耳语到绝望嘶吼的戏剧跨度",
        ),
    ]

    cues = [
        TimelineCue(
            cue_id=cid,
            act_id="",
            kind="dialogue",
            role_id=rid,
            text=txt,
            tts_text=compute_tts_text_override(txt),
            stability=stab,
            similarity_boost=0.85,
            acoustic_space=space,
            gap_after_s=0.8,
            director_note=note,
        )
        for cid, rid, txt, stab, space, note in lines
    ]
    sheet = EpisodeCueSheet(
        episode_id="E001_AUDITION_A_CUSTOM",
        chapter_number=1,
        title="《逆模因部》核心声优六句试听合集（SCP CC-BY-SA-3.0）",
        mode="audition_pack",
        source_chapter_file="source_chapters/第01章_SCP-055_未知自封机密.md",
        head_pad_s=0.3,
        tail_pad_s=0.8,
        acts=[],
        cues=cues,
    )
    errs = sheet.validate(registry=registry, require_locked_voices=True)
    if errs:
        raise ValueError("Audition CueSheet validation failed:\n" + "\n".join(errs))

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    AUDITION_DIR.mkdir(parents=True, exist_ok=True)
    fname = "E001_AUDITION_A_逆模因部六句试听清单.json"
    out_main = SCRIPTS_DIR / fname
    sheet.save(out_main)
    sheet.save(AUDITION_DIR / fname)
    return out_main


def build_all_episodes() -> list[tuple[str, Path, Path]]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)
    built: list[tuple[str, Path, Path]] = []

    # =========================================================================
    # E001 · 第1章 SCP-055：未知自封机密 (29 paras, 24 quotes)
    # =========================================================================
    md_01 = SOURCE_DIR / "第01章_SCP-055_未知自封机密.md"
    s01 = compile_episode_cue_sheet(
        episode_id="E001",
        chapter_number=1,
        source_md_path=md_01,
        source_rel_path=f"source_chapters/{md_01.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_classified_file_055",
                "start_p": 1,
                "title": "第一幕 · 五级机密词条：自我保守的秘密",
                "bgm_prompt": "Cold minimalist analog synthesizer drone in a deep subterranean bunker, sparse eerie glass pulses and sub-bass hum of classified secrecy, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act2_hughes_negative_epiphany",
                "start_p": 8,
                "title": "第二幕 · 涂黑附件与巴特·休斯的逆向灵光",
                "bgm_prompt": "Mysterious cerebral sci-fi suspense underscore, muted felt piano notes over dark modular synth textures, quiet intellectual tension, instrumental only, no vocals",
                "bgm_duration_s": 75.0,
            },
            {
                "act_id": "act3_debriefing_tape_not_round",
                "start_p": 12,
                "title": "第三幕 · 审讯磁带：它绝对不是圆的",
                "bgm_prompt": "Unsettling psychological thriller ambient score, subtle tape-loop warble, taut pizzicato strings and creeping cognitive dread, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
        ],
        acoustic_ranges=[
            (2, 7, "mental_realm"),
            (9, 9, "mental_realm"),
            (13, 27, "memory_echo"),
            (29, 29, "mental_realm"),
        ],
        dialogue_specs=[
            {"match": "项目编号：SCP-055", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "SCiPNET终端播报编号与Keter等级"},
            {"match": "特殊收容措施：项目被保存在", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报5×5×2.5米水泥铅笼收容措施"},
            {"match": "描述：SCP-055是一个", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端定义逆模因：自我保守的秘密"},
            {"match": "具体表现如下：第一", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端列举前三条未知属性"},
            {"match": "第四，究竟是谁批准建造", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端列举后三条未知与记忆归零"},
            {"match": "评估结论：SCP-055可能构成", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报Keter威胁评估"},
            {"match": "文档零五五之一：一份关于SCP-055的态势分析", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报涂黑态势分析附件"},
            {"match": "嘿，如果这东西真是个所谓的", "role_id": "bart_hughes", "tags": "[calmly]", "stability": 0.5, "space": "dry", "note": "巴特·休斯附录A便签：逆向记它不是什么"},
            {"match": "好的，现在我要问你几个关于五十五号的问题", "role_id": "bart_hughes", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "审讯录音开始，休斯博士温和提问"},
            {"match": "多少号？", "role_id": "subject_055", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "受试研究员一脸茫然反问"},
            {"match": "SCP项目零五五。你刚刚才进去调查过的那个", "role_id": "bart_hughes", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "休斯博士耐心提醒"},
            {"match": "嗯……我完全不知道你在说什么", "role_id": "subject_055", "tags": "[trembling]", "stability": 0.0, "space": "memory_echo", "note": "受试研究员迟疑否认存在055"},
            {"match": "好吧。那么，我想问问你，在刚刚过去的两个小时里", "role_id": "bart_hughes", "tags": "[sighs] [calmly]", "stability": 0.5, "space": "memory_echo", "note": "休斯轻叹换切入点追问失落的两小时"},
            {"match": "啊？我……我不知道", "role_id": "subject_055", "tags": "[trembling]", "stability": 0.0, "space": "memory_echo", "note": "受试研究员惊觉两小时记忆空白"},
            {"match": "没关系。那么，你还记不记得，刚才我们大家一致同意", "role_id": "bart_hughes", "tags": "[softly]", "stability": 0.5, "space": "memory_echo", "note": "休斯前倾抛出否定锚点：它不是球形的"},
            {"match": "什么东西不是……噢！对！它一点儿都不圆", "role_id": "subject_055", "tags": "[gasps] [excited]", "stability": 0.0, "space": "memory_echo", "note": "受试研究员猛然惊醒脱口叫出它不是圆的"},
            {"match": "所以你现在想起来了吗？", "role_id": "bart_hughes", "tags": "[excited]", "stability": 0.0, "space": "memory_echo", "note": "休斯眼睛一亮追问"},
            {"match": "呃，并没有。我是说，我还是不知道它到底是什么东西", "role_id": "subject_055", "tags": "[trembling]", "stability": 0.0, "space": "memory_echo", "note": "受试者揉太阳穴说出否定认知悖论"},
            {"match": "等等……你说什么东西不是球体？", "role_id": "bart_hughes", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "两秒后休斯自己也突然失忆愣住"},
            {"match": "五十五号项目啊", "role_id": "subject_055", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "受试者立刻回答"},
            {"match": "多少号项目？", "role_id": "bart_hughes", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "休斯再次彻底遗忘"},
            {"match": "博士，你还记不记得你刚才亲口同意过", "role_id": "subject_055", "tags": "[rushed]", "stability": 0.0, "space": "memory_echo", "note": "受试者反向用否定命题唤醒休斯"},
            {"match": "噢——对！我想起来了！", "role_id": "bart_hughes", "tags": "[excited]", "stability": 0.0, "space": "memory_echo", "note": "休斯拍案恍然大悟"},
            {"match": "调查结论：实验证实，人类大脑可以记住", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报结案批注"},
        ],
        sfx_blueprint=[
            {"p": 2, "pos": "before", "slug": "scp055_terminal_boot", "motif_id": "motif_scp_terminal_boot", "gain_db": -0.5, "note": "SCiPNET终端解密调出SCP-055主档案"},
            {"p": 9, "pos": "before", "slug": "redacted_doc_static", "motif_id": "motif_antimemetic_static", "gain_db": -1.5, "note": "翻开涂黑态势分析附件时的认知静电底噪"},
            {"p": 13, "pos": "before", "slug": "cassette_recorder_play", "sfx_prompt": "Vintage magnetic cassette tape deck button clunking down followed by analog tape hiss and reel spin in an interrogation room", "duration_seconds": 2.8, "gain_db": -0.5, "note": "按下审讯录音机播放键与磁带底噪"},
            {"p": 23, "pos": "before", "slug": "hughes_amnesia_static", "motif_id": "motif_antimemetic_static", "gain_db": -1.5, "note": "两秒间逆模因抹除休斯博士短期记忆"},
            {"p": 28, "pos": "before", "slug": "tape_cutoff_click", "sfx_prompt": "Sharp analog magnetic tape stop click and brief static buzz cutting to silence", "duration_seconds": 2.0, "gain_db": -0.5, "note": "审讯录音在电流嘶鸣中切断"},
        ],
    )
    j01, m01 = save_episode_scripts(s01, SCRIPTS_DIR, registry)
    built.append(("E001", j01, m01))

    # =========================================================================
    # E002 · 第2章 我们得谈谈五十五号 (84 paras, 68 quotes)
    # =========================================================================
    md_02 = SOURCE_DIR / "第02章_我们得谈谈五十五号.md"
    s02 = compile_episode_cue_sheet(
        episode_id="E002",
        chapter_number=2,
        source_md_path=md_02,
        source_rel_path=f"source_chapters/{md_02.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_lobby_smoking_loop",
                "start_p": 1,
                "title": "第一幕 · 两百号站点前厅：十五分钟三次借火",
                "bgm_prompt": "Cool restrained neo-noir espionage ambient score, muted upright bass pulse, ticking clockwork synth and sterile corporate lobby tension, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act2_o5_gunpoint_antimemetics",
                "start_p": 12,
                "title": "第二幕 · 防爆门内的枪口：这世上有逆模因部",
                "bgm_prompt": "Taut subterranean sci-fi chamber thriller score, deep ominous cello drone and sparse metallic synth pings in a soundproof bunker office, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_class_w_mnestic_pill",
                "start_p": 51,
                "title": "第三幕 · 绿色六边形药片：W级记忆强化剂",
                "bgm_prompt": "Cerebral dark electronic suspense score, hypnotic pulsing analog synth arpeggio over hollow sub-bass memory void, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act4_three_shots_at_clay",
                "start_p": 70,
                "title": "第四幕 · 连开三枪：你从来就没有私人助理",
                "bgm_prompt": "Razor-sharp cold sci-fi thriller climax score, sudden percussive sub-bass drops, icy dissonant strings and chilling aftermath stillness, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        dialogue_specs=[
            {"match": "我能抽根烟吗？", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安第三次试探前台记忆"},
            {"match": "不行。你——不行，两百号站点任何地方都不准抽烟", "role_id": "receptionist_npc", "tags": "[dismissive]", "stability": 0.5, "note": "女前台斩钉截铁禁烟"},
            {"match": "这话我之前已经问过你了，对吧？", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安平静印证"},
            {"match": "过去十五分钟里问过两次了", "role_id": "receptionist_npc", "tags": "[calmly]", "stability": 0.5, "note": "女前台无奈又困惑"},
            {"match": "你觉得这像电影《记忆碎片》里的情节", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.5, "note": "玛丽安温和替女前台解围"},
            {"match": "我……猜是吧？", "role_id": "receptionist_npc", "tags": "[calmly]", "stability": 0.5, "note": "女前台迟疑回应"},
            {"match": "玛丽安？你现在可以进来了", "role_id": "clay", "tags": "[calmly]", "stability": 0.5, "note": "年轻助理克莱探头传唤"},
            {"match": "那么，今天要谈什么议题？", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安落座率先开口"},
            {"match": "好吧？", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "被手枪指头仍保持绝对镇定"},
            {"match": "你到底是谁？", "role_id": "o5_8", "tags": "[coldly]", "stability": 0.5, "note": "O5-8沉声审问"},
            {"match": "什么？噢，天哪", "role_id": "marion_wheeler", "tags": "[sighs]", "stability": 0.5, "note": "玛丽安瞬间意识到O5-8漏服了药"},
            {"match": "容我换个问法。玛丽安·惠勒，四十九岁", "role_id": "o5_8", "tags": "[coldly]", "stability": 0.5, "note": "O5-8宣读玛丽安空白背景调查"},
            {"match": "你这蠢货，我是你们的逆模因部部长", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.0, "note": "玛丽安毫不客气亮出身份"},
            {"match": "我们根本没有逆模因部", "role_id": "clay", "tags": "[dismissive]", "stability": 0.0, "note": "克莱冷声否定"},
            {"match": "不，你们有。我们有", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安平静笃定回应"},
            {"match": "我们有模因部、心灵遮断收容部", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8列举基金会正规部门"},
            {"match": "那我们设有反讽部吗？", "role_id": "marion_wheeler", "tags": "[sarcastic]", "stability": 0.0, "note": "玛丽安犀利反讽"},
            {"match": "没有？好吧。那不妨动脑子想想这个问题", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.0, "note": "玛丽安点破逆模因部不可能上花名册"},
            {"match": "这只是一套掩护说辞", "role_id": "clay", "tags": "[coldly]", "stability": 0.0, "note": "克莱向O5-8进谗"},
            {"match": "克莱，把枪收起来", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8抬手命令收枪"},
            {"match": "基金会里收容着许多具有危险模因性质的SCP异常", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安从模因切入阐述"},
            {"match": "没错", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8颔首认同"},
            {"match": "那么同理，世界上也存在着具有", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安系统阐释逆模因概念"},
            {"match": "报一个名字。随便报出一个逆模因SCP", "role_id": "o5_8", "tags": "[coldly]", "stability": 0.5, "note": "O5-8要求实证"},
            {"match": "SCP-055", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安脱口报出055"},
            {"match": "根本就没有SCP-055", "role_id": "clay", "tags": "[dismissive]", "stability": 0.0, "note": "克莱冷笑反驳"},
            {"match": "我再说一遍：有的", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安寸步不让"},
            {"match": "绝对没有！SCP编号从来不是按顺序连号分配的", "role_id": "clay", "tags": "[angry]", "stability": 0.0, "note": "克莱急切否定055编号"},
            {"match": "克莱，你最好过来看看这个", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8在主库调出055真档"},
            {"match": "可是……", "role_id": "clay", "tags": "[gasps]", "stability": 0.0, "note": "克莱读完哑口无言"},
            {"match": "这份档案的建档日期是二零零八年", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8确认密钥签名全真"},
            {"match": "您以前见过这份文件吗？", "role_id": "clay", "tags": "[rushed]", "stability": 0.0, "note": "克莱抬头急问"},
            {"match": "我这辈子从没见过——至少就我能记住的范围而言", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8推导出两人恐怕读过几十遍"},
            {"match": "这根本不可能", "role_id": "clay", "tags": "[angry]", "stability": 0.0, "note": "克莱咬牙死瞪玛丽安"},
            {"match": "看在上帝份上，克莱，你在这儿工作多久了？", "role_id": "marion_wheeler", "tags": "[sarcastic]", "stability": 0.0, "note": "玛丽安暗藏试探的一问（克莱答不上来）"},
            {"match": "可如果这个SCP真的强大到这种地步", "role_id": "clay", "tags": "[coldly]", "stability": 0.0, "note": "克莱回避工龄质问"},
            {"match": "接着说？", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安挑眉引导"},
            {"match": "那么到底是谁写下了这份档案？", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8追问巴特·休斯与玛丽安记忆来源"},
            {"match": "档案是巴特·休斯写的。他已经死了", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安冷淡宣告休斯死讯"},
            {"match": "他怎么死的？", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8追问死因"},
            {"match": "你不会想知道的", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安警告认知危害"},
            {"match": "如果……我们真的知道了，会发生什么？", "role_id": "o5_8", "tags": "[softly]", "stability": 0.5, "note": "O5-8洞悉信息致命性谨慎发问"},
            {"match": "同样的下场也会降临到你们头上", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安引出记忆强化剂体系"},
            {"match": "这就是W级记忆强化剂，药效最温和的一档", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安讲解W级药片与药房领药"},
            {"match": "到了这一步，我想我彻底明白了", "role_id": "o5_8", "tags": "[sighs]", "stability": 0.5, "note": "O5-8叹息恍然大悟"},
            {"match": "没错，因为你漏服了一剂", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安递出第二粒药片复盘全过程"},
            {"match": "只要我把这粒药咽下去，我就能记住今天整场谈话", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8端详绿色药片确认"},
            {"match": "但愿不用", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安淡淡回应"},
            {"match": "呃，那我是不是也该吃一粒这个？", "role_id": "clay", "tags": "[calmly]", "stability": 0.0, "note": "寄生逆模因克莱试探讨药"},
            {"match": "抱歉，小子，这属于知密权限管制范畴", "role_id": "o5_8", "tags": "[dismissive]", "stability": 0.5, "note": "O5-8随口回绝并服药"},
            {"match": "那么，SCP-055到底是什么？", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "药效生效，O5-8追问055本质"},
            {"match": "SCP-055什么也不是", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安放松靠背解释055无害性与唯一收容措施"},
            {"match": "你们居然制定了收容措施？写在哪儿？", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8诧异询问"},
            {"match": "那除了它之外，还有多少个其他的逆模因？", "role_id": "o5_8", "tags": "[softly]", "stability": 0.5, "note": "O5-8倒吸凉气追问逆模因总量"},
            {"match": "据我所知的就有十个", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安点出这间办公室里就有两个野生逆模因"},
            {"match": "有一只看不见的怪物成天跟在我屁股后面转", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安介绍宠物般无害的SCP-4987"},
            {"match": "那另一个呢？", "role_id": "clay", "tags": "[trembling]", "stability": 0.0, "note": "克莱咽唾沫追问第二个逆模因"},
            {"match": "你怎……么知……", "role_id": "clay", "tags": "[gasps] [hoarsely]", "stability": 0.0, "note": "克莱胸口中两枪濒死惊骇嘶声"},
            {"match": "那是克莱的枪。你从他身上偷走的", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8眼皮都不跳冷淡指出枪源"},
            {"match": "想在当事人毫无察觉的情况下顺走这么重的一把制式手枪", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安退弹清膛解释贴身催眠夺枪"},
            {"match": "是，这一点我已经猜到了。但为什么要杀他？", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8追问击毙理由"},
            {"match": "因为你原本一直在按时服用W级记忆强化剂", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安揭露克莱蓄意断药与答不出工龄"},
            {"match": "他没有回答。我当时以为你只是在用反问句讽刺他", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8怔然复盘"},
            {"match": "因为他压根就不是这儿的员工，布伦特", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.0, "note": "玛丽安直呼O5真名布伦特，揭穿克莱本身就是人形逆模因"},
            {"match": "他死了吗？", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8荒诞而冷静的一问"},
            {"match": "也许吧。我会把他的尸体排进我们部门的解剖研究队列", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安阐述概念与物质双生体理论"},
            {"match": "吃这种药片，有什么副作用吗？", "role_id": "o5_8", "tags": "[calmly]", "stability": 0.5, "note": "O5-8最后询问W级副作用"},
            {"match": "恶心反胃，外加胰腺癌发病率急剧飙升", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安拎包离去留下冷冽尾句：还有可怕的噩梦"},
        ],
        sfx_blueprint=[
            {"p": 8, "pos": "before", "slug": "zippo_lighter_fidget", "sfx_prompt": "Metallic Zippo lighter lid clinking open and shut repeatedly in a quiet waiting room", "duration_seconds": 2.4, "gain_db": -1.5, "note": "玛丽安在指间反复把玩金属打火机"},
            {"p": 12, "pos": "before", "slug": "o5_office_vault_door", "motif_id": "motif_heavy_blast_door", "gain_db": -0.5, "note": "O5-8防弹办公室重型机械门合拢"},
            {"p": 38, "pos": "before", "slug": "o5_query_scp055", "motif_id": "motif_scp_terminal_boot", "gain_db": -1.0, "note": "O5-8敲击键盘调出SCP-055主库机密档案"},
            {"p": 54, "pos": "before", "slug": "mnestic_alarm_and_foil", "motif_id": "motif_mnestic_pill_beep", "gain_db": 0.0, "note": "手提包内准点服药蜂鸣与铝塑板掰出药片"},
            {"p": 72, "pos": "after", "slug": "double_gunshot_chest", "sfx_prompt": "Two sharp close-range 9mm pistol gunshots inside a wood-paneled soundproof office followed by brass casings hitting carpet and a body thudding into a bookshelf", "duration_seconds": 3.0, "gain_db": 1.0, "note": "玛丽安拔枪朝克莱心脏连开两枪"},
            {"p": 74, "pos": "after", "slug": "third_gunshot_headshot", "sfx_prompt": "Single decisive 9mm pistol gunshot at close range followed by metallic magazine eject and slide rack clearing chamber onto wooden desk", "duration_seconds": 3.2, "gain_db": 1.0, "note": "第三枪爆头与利落退匣清膛放上桌面"},
        ],
    )
    j02, m02 = save_episode_scripts(s02, SCRIPTS_DIR, registry)
    built.append(("E002", j02, m02))

    # =========================================================================
    # E003 · 第3章 逆模因学导论 (77 paras, 47 quotes)
    # =========================================================================
    md_03 = SOURCE_DIR / "第03章_逆模因学导论.md"
    s03 = compile_episode_cue_sheet(
        episode_id="E003",
        chapter_number=3,
        source_md_path=md_03,
        source_rel_path=f"source_chapters/{md_03.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_cafeteria_man_in_grey",
                "start_p": 1,
                "title": "第一幕 · 新人食堂：穿灰西装的格雷先生",
                "bgm_prompt": "Subtle uncanny sci-fi psychological suspense score, quiet cafeteria room tone morphing into eerie detuned glass harmonics and creeping dread, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_isolated_universe_chase",
                "start_p": 20,
                "title": "第二幕 · 一个人的孤岛宇宙：镜中无脸与SCP-4739",
                "bgm_prompt": "Propulsive claustrophobic sci-fi chase thriller score, rapid pulsing analog bass synth, heartbeat percussion and high-pitched cognitive static tension, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_information_morningstar",
                "start_p": 46,
                "title": "第三幕 · 第八十道刻痕：网线流星锤与圆周率阵列",
                "bgm_prompt": "High-stakes sci-fi survival action score, driving industrial synth rhythms building to an explosive electromagnetic climax, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_debrief_ideas_dont_die",
                "start_p": 65,
                "title": "第四幕 · 战后简报：观念是不会死的",
                "bgm_prompt": "Cold sobering dark ambient thriller coda, sparse low piano chords over deep subterranean drone, lingering existential chill, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
        ],
        acoustic_ranges=[
            (39, 39, "mental_realm"),
            (47, 50, "mental_realm"),
        ],
        dialogue_specs=[
            {"match": "第一天上班够呛吧？我叫阿拉斯泰尔·格雷", "role_id": "alastair_grey", "tags": "[calmly]", "stability": 0.5, "note": "灰西装捕食者格雷礼貌伸手"},
            {"match": "我姓金，保罗·金", "role_id": "paul_kim", "tags": "[calmly]", "stability": 0.5, "note": "保罗·金握手自我介绍"},
            {"match": "很高兴认识你。如果不介意我多嘴的话", "role_id": "alastair_grey", "tags": "[calmly]", "stability": 0.5, "note": "格雷试探并锁定金的家乡记忆"},
            {"match": "纽约口音。我是纽约人", "role_id": "paul_kim", "tags": "[calmly]", "stability": 0.5, "note": "金回答纽约人并反问格雷身份"},
            {"match": "你看起来神经绷得很紧啊", "role_id": "alastair_grey", "tags": "[softly]", "stability": 0.5, "note": "格雷微笑回避"},
            {"match": "这不很正常吗？您肯定清楚早上那堂入职导论课", "role_id": "paul_kim", "tags": "[sighs]", "stability": 0.5, "note": "金苦笑吐槽入职导论课颠覆三观"},
            {"match": "嘿，您在这儿到底是负责什么工作的？", "role_id": "paul_kim", "tags": "[calmly]", "stability": 0.5, "note": "金追问格雷职务"},
            {"match": "你也没回答我的问题啊", "role_id": "alastair_grey", "tags": "[condescending]", "stability": 0.0, "note": "格雷微笑揭示纽约记忆已被吞掉"},
            {"match": "我当然回答了，我是从——", "role_id": "paul_kim", "tags": "[rushed]", "stability": 0.0, "note": "金脱口而出却骤然卡壳"},
            {"match": "怪了", "role_id": "paul_kim", "tags": "[whispers]", "stability": 0.5, "note": "金晃脑袋惊觉吐不出家乡名字"},
            {"match": "你到底是谁？", "role_id": "paul_kim", "tags": "[coldly]", "stability": 0.0, "note": "金发现格雷没戴工牌沉声质问"},
            {"match": "你的人生履历曾经非常迷人", "role_id": "alastair_grey", "tags": "[condescending]", "stability": 0.0, "note": "格雷优雅品鉴猎物大脑"},
            {"match": "你说什么？", "role_id": "paul_kim", "tags": "[gasps]", "stability": 0.0, "note": "金心头剧震"},
            {"match": "你原本精通四门语言——现在只剩一门了", "role_id": "alastair_grey", "tags": "[calmly]", "stability": 0.0, "note": "格雷慢条斯理宣告正在吃光他的学识"},
            {"match": "失陪一秒钟好吗？", "role_id": "paul_kim", "tags": "[calmly]", "stability": 0.5, "note": "金强作镇定起身求救"},
            {"match": "嘿！出事了！有入侵者混进来了", "role_id": "paul_kim", "tags": "[shouting]", "stability": 0.0, "note": "金对着女教官大喊却无人能感知他"},
            {"match": "嘿！大家醒醒！听我说话啊！", "role_id": "paul_kim", "tags": "[desperately]", "stability": 0.0, "note": "金惊恐发现自己已被隔绝出主世界"},
            {"match": "这完全说不通啊……", "role_id": "paul_kim", "tags": "[trembling]", "stability": 0.0, "note": "金拨通电话无人接听后倒退喃喃"},
            {"match": "你还记得你的父亲吗？", "role_id": "alastair_grey", "tags": "[softly]", "stability": 0.0, "note": "格雷吞掉他关于父亲的全部记忆"},
            {"match": "我从来没见过我父亲，我是我妈一手带大的", "role_id": "paul_kim", "tags": "[trembling]", "stability": 0.0, "note": "金记忆被篡改后下意识作答"},
            {"match": "这儿的人原本非常欣赏你的独特视角", "role_id": "alastair_grey", "tags": "[condescending]", "stability": 0.0, "note": "格雷微笑宣判：你根本就不存在"},
            {"match": "这座站点里根本没有收容危险级SCP", "role_id": "paul_kim", "tags": "[rushed]", "stability": 0.0, "note": "金飞速逻辑推演格雷是野生未收容异常"},
            {"match": "第一天上班够呛吧？", "role_id": "alastair_grey", "tags": "[calmly]", "stability": 0.0, "note": "格雷非人复读开场白"},
            {"match": "你有自我意识吗？", "role_id": "paul_kim", "tags": "[coldly]", "stability": 0.0, "note": "金试探格雷是否只是拟态捕食者"},
            {"match": "你看起来神经绷得很紧啊", "role_id": "alastair_grey", "tags": "[calmly]", "stability": 0.0, "note": "格雷再次机械复读"},
            {"match": "老天爷！不不不，这到底是怎么回事", "role_id": "paul_kim", "tags": "[gasps] [desperately]", "stability": 0.0, "note": "金瞥见电梯镜子里不认识自己的脸惊骇叫出声"},
            {"match": "项目编号：SCP-4739。项目等级：Keter", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "手机屏幕弹出遇难前辈接力留下的SCP-4739红色词条"},
            {"match": "快开啊！快点，快点啊！", "role_id": "paul_kim", "tags": "[desperately]", "stability": 0.0, "note": "金拍打053实验室潜艇舱门"},
            {"match": "你还记得你的母亲吗？", "role_id": "alastair_grey", "tags": "[softly]", "stability": 0.0, "note": "走廊远端格雷继续啃食他母亲的记忆"},
            {"match": "我从小没见过父母，我是个孤儿！", "role_id": "paul_kim", "tags": "[angry]", "stability": 0.0, "note": "金咬牙低吼出被篡改后的孤儿记忆"},
            {"match": "描述：SCP-4739是一种强效、慢速作用的逆模因抹杀媒介", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "实验室终端播报SCP-4739捕食机制"},
            {"match": "研究认为SCP-4739并不具备真正的自我意识", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报受害者孤岛效应"},
            {"match": "你此刻正在阅读的这篇SCP词条", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报历代遇难者接力遗书"},
            {"match": "自二零一三年八月三日我们开始计数以来", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报七十九名遇难者刻痕"},
            {"match": "可我到底该怎么杀了它啊？！", "role_id": "paul_kim", "tags": "[shouting]", "stability": 0.0, "note": "金对着杂乱无章的实验记录崩溃尖叫"},
            {"match": "我死定了！", "role_id": "paul_kim", "tags": "[desperately]", "stability": 0.0, "note": "金看见格雷即将穿墙而入绝望咒骂"},
            {"match": "那东西正顺着我们逆模因部的职级金字塔一路往上啃食", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "简报室里玛丽安·惠勒冷静评价战果"},
            {"match": "我很想说今天纯粹是走了狗屎运", "role_id": "paul_kim", "tags": "[sighs]", "stability": 0.5, "note": "金缓缓复盘自己绝非新人"},
            {"match": "你根本不是我的新上司——你一直都是我的上司", "role_id": "paul_kim", "tags": "[calmly]", "stability": 0.5, "note": "金推导出自己早已是十几年资深研究员"},
            {"match": "在我看来，今天发生的事里几乎没有任何运气的成分", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "惠勒肯定他刻入骨髓的肌肉训练"},
            {"match": "甚至连眼下这场对话，都不是我们第一次进行了吧？", "role_id": "paul_kim", "tags": "[softly]", "stability": 0.5, "note": "金揉眉心洞察轮回对话"},
            {"match": "而且看多少遍都还挺百看不厌的", "role_id": "marion_wheeler", "tags": "[sarcastic]", "stability": 0.5, "note": "惠勒罕见冷幽默"},
            {"match": "我通常需要多久才能彻底恢复记忆？", "role_id": "paul_kim", "tags": "[sighs]", "stability": 0.5, "note": "金叹气询问恢复周期"},
            {"match": "几个月吧。不过要是你想听句掏心窝子的大实话", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "惠勒道出逆模因部名言：第一天有多能干巅峰就多能干"},
            {"match": "所以你真正想表达的意思是：你压根不在乎我现在的精神创伤", "role_id": "paul_kim", "tags": "[sarcastic]", "stability": 0.5, "note": "金无奈听懂立刻返工指令"},
            {"match": "首先，我需要你立刻更新那篇SCP-4739正式档案", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "惠勒布置四项后续收容任务"},
            {"match": "它还没死透？等等……我想起来了", "role_id": "paul_kim", "tags": "[gasps]", "stability": 0.0, "note": "金猛然忆起核心铁律：观念是不会死的"},
        ],
        sfx_blueprint=[
            {"p": 13, "pos": "before", "slug": "memory_derail_static", "motif_id": "motif_antimemetic_static", "gain_db": -1.0, "note": "纽约地名被吞噬瞬间的脑内静电断轨"},
            {"p": 22, "pos": "before", "slug": "unanswered_cellphone_ring", "sfx_prompt": "Modern smartphone ringtone ringing unanswered inside a strangely muffled empty cafeteria", "duration_seconds": 3.0, "gain_db": -1.0, "note": "新人裤兜里手机铃声大作却无人感知"},
            {"p": 38, "pos": "before", "slug": "scp4739_red_entry", "motif_id": "motif_scp_terminal_boot", "gain_db": -0.5, "note": "手机检索弹出SCP-4739红色紧急词条"},
            {"p": 40, "pos": "before", "slug": "elevator_ding_b8", "sfx_prompt": "Subterranean freight elevator arrival chime ding followed by heavy steel sliding doors opening", "duration_seconds": 2.6, "gain_db": -0.5, "note": "地下八层电梯叮声滑开，格雷已在门外"},
            {"p": 41, "pos": "before", "slug": "phone_throw_impact", "sfx_prompt": "Heavy metal-cased smartphone hurled through air striking skull with a sharp crack and clattering onto concrete corridor floor", "duration_seconds": 2.6, "gain_db": 0.5, "note": "金属工作手机狠狠砸退格雷"},
            {"p": 46, "pos": "before", "slug": "submarine_hatch_lock", "motif_id": "motif_heavy_blast_door", "gain_db": -0.5, "note": "053实验室潜艇级气密舱门拉合锁紧"},
            {"p": 63, "pos": "before", "slug": "raid_morningstar_explosion", "sfx_prompt": "Heavy metal server drive swung on braided cables smashing into an entity with a blinding green high-voltage subway arc explosion and shattering electronics", "duration_seconds": 4.2, "gain_db": 1.5, "note": "网线编织圆周率磁盘流星锤轰爆SCP-4739惨绿电弧"},
        ],
    )
    j03, m03 = save_episode_scripts(s03, SCRIPTS_DIR, registry)
    built.append(("E003", j03, m03))

    # =========================================================================
    # E004 · 第4章 难以忘怀，你本如此 (84 paras, 51 quotes)
    # =========================================================================
    md_04 = SOURCE_DIR / "第04章_难以忘怀，你本如此.md"
    s04 = compile_episode_cue_sheet(
        episode_id="E004",
        chapter_number=4,
        source_md_path=md_04,
        source_rel_path=f"source_chapters/{md_04.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_lake_boat_resurrection",
                "start_p": 1,
                "title": "第一幕 · 金色湖面：最后的十二小时契约",
                "bgm_prompt": "Bittersweet nostalgic ambient chamber score over gentle lake water, warm solitary cello and sparse felt piano hiding quiet clinical sorrow, instrumental only, no vocals",
                "bgm_duration_s": 95.0,
            },
            {
                "act_id": "act2_class_x_unthinkable_history",
                "start_p": 21,
                "title": "第二幕 · X级逆龄血清：二战不可思议小队与七六年黑洞",
                "bgm_prompt": "Mysterious historical espionage sci-fi score, deep pulsing analog synth, solemn brass undertones and fractured dual-timeline tension, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
            {
                "act_id": "act3_the_escaped_one_awakens",
                "start_p": 51,
                "title": "第三幕 · 逃逸恶神：如果你看见它，它就看见你",
                "bgm_prompt": "Terrifying cosmic horror escalation score, shrieking bowed dissonant strings, colossal sub-bass pressure and relentless panic, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act4_thirty_meter_plunge_oblivion",
                "start_p": 72,
                "title": "第四幕 · 三十米高空坠湖与失落时间总图",
                "bgm_prompt": "Desolate haunting post-trauma ambient score, icy crystalline pads and hollow sub-bass memory vacuum fading into cold stillness, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
        ],
        acoustic_ranges=[
            (21, 21, "mental_realm"),
        ],
        dialogue_specs=[
            {"match": "艾尔，已经结束了", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.5, "note": "玛丽安在游艇甲板上轻声唤醒恩师"},
            {"match": "艾尔，你现在可以醒过来了", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.5, "note": "玛丽安第二次温和呼唤"},
            {"match": "你还记得我吗？", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安轻声询问"},
            {"match": "玛丽安", "role_id": "lyn_marness", "tags": "[hoarsely]", "stability": 0.0, "note": "九旬垂死老者马内斯沙哑认出弟子"},
            {"match": "艾尔，你已经死了。你在悲痛欲绝的家人们的簇拥下安详离世", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.5, "note": "玛丽安平静告知假死替身葬礼"},
            {"match": "玛丽安·哈钦森", "role_id": "lyn_marness", "tags": "[hoarsely]", "stability": 0.0, "note": "X级血清初效，马内斯念出她少女闺名"},
            {"match": "当年你从基金会光荣退休的时候", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安说明退休记忆删除程序"},
            {"match": "想起来了", "role_id": "lyn_marness", "tags": "[hoarsely]", "stability": 0.5, "note": "尘封往事倒灌，马内斯沉声回应"},
            {"match": "你把生命最后的十二个小时签给了我们", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安出示泛黄契约"},
            {"match": "认得", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "马内斯认出亲笔签名"},
            {"match": "现在，你还记得自己是谁吗？", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安确认恩师身份归位"},
            {"match": "基金会所属，林·帕特里克·马内斯博士。逆模因部创始人", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "马内斯脊背绷紧庄严报出创始人名号"},
            {"match": "我们需要从你脑海里提取一段记忆", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安坦陈提取代价是致死量逆转"},
            {"match": "一九七六年，究竟发生了什么？", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安抛出核心悬案"},
            {"match": "摘录自文件一八零零四七一零九号《化学记忆强化剂用户指南》", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报X级永生驻颜血清与致死副作用档案"},
            {"match": "但当年那一切都顺利得太反常、太快了", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "马内斯察觉1976年建部快得违背常理"},
            {"match": "结果你在半个工作日之后，发现自己莫名其妙坐在办公桌前醒来", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安接话复述失忆死循环"},
            {"match": "当我把所有旁证拼凑在一起时，我看到的……是一个巨大的空洞", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "马内斯描摹历史黑洞轮廓"},
            {"match": "这些情况我们都已经掌握了", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安要求直抵墙后的终极答案"},
            {"match": "不在那儿……你把我送回去的年头还不够远", "role_id": "lyn_marness", "tags": "[hoarsely]", "stability": 0.0, "note": "马内斯捂右眼痛苦发现记忆仍被堵在墙外"},
            {"match": "起初，我们根本不属于基金会", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "第二针逆龄生效，马内斯立于船头追忆二战陆军计划"},
            {"match": "你是说，早在上世纪四十年代", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安震惊挑眉"},
            {"match": "千真万确", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "马内斯朗声自豪确认"},
            {"match": "当然了，如今这整个世界上，连一个能替你作证的人都找不出来", "role_id": "marion_wheeler", "tags": "[sarcastic]", "stability": 0.5, "note": "玛丽安冷淡点出死无对证"},
            {"match": "一点没错，全凭我一张嘴空口白牙，挺妙吧？", "role_id": "lyn_marness", "tags": "[laughs] [calmly]", "stability": 0.0, "note": "马内斯爽朗一笑"},
            {"match": "我复活你，是为了得到一个极其具体的问题的答案", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安直指逆模因炸弹就是1976作案工具"},
            {"match": "——是『不可思议小队』——", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "马内斯插话纠正老番号"},
            {"match": "——用某种方式，亲手用炸弹炸掉了他们自己", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安寸步不让接完推论"},
            {"match": "没错", "role_id": "lyn_marness", "tags": "[coldly]", "stability": 0.5, "note": "马内斯敛去笑容沉声承认"},
            {"match": "结合上下文来看，我猜一九七六年那一次", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安判定绝非试爆事故"},
            {"match": "绝非事故", "role_id": "lyn_marness", "tags": "[coldly]", "stability": 0.5, "note": "马内斯一字一顿确认"},
            {"match": "二战结束后，第二颗炸弹在军方仓库里积了好几年灰", "role_id": "lyn_marness", "tags": "[calmly]", "stability": 0.5, "note": "马内斯诵读脑海中的《新编初代真史》"},
            {"match": "奇怪……我现在一下子记起了好多截然不同的人", "role_id": "lyn_marness", "tags": "[trembling]", "stability": 0.0, "note": "马内斯记忆变成双重立体声，记起被抹除的先烈"},
            {"match": "那奥乔比鲁博士呢？朱莉·斯蒂尔呢？", "role_id": "lyn_marness", "tags": "[rushed]", "stability": 0.0, "note": "马内斯急切追问昔日战友"},
            {"match": "艾尔，集中精神，这至关重要！", "role_id": "marion_wheeler", "tags": "[shouting]", "stability": 0.0, "note": "玛丽安厉声喝令他聚焦1976节点"},
            {"match": "有一个SCP异常，是你们这一代逆模因部从未见过的", "role_id": "lyn_marness", "tags": "[whispers]", "stability": 0.0, "note": "马内斯毛骨悚然耳语揭开『逃逸者』与双向感知铁律"},
            {"match": "是。这就是我今天不惜杀掉你也要拿到的数据", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "note": "玛丽安冷酷确认"},
            {"match": "当年，它正在活生生吃掉我的整个部门！", "role_id": "lyn_marness", "tags": "[desperately]", "stability": 0.0, "note": "马内斯字字泣血揭露自己就是当年唯一的逃生者"},
            {"match": "它在哪儿？！它在你身体里面吗？！", "role_id": "marion_wheeler", "tags": "[shouting]", "stability": 0.0, "note": "玛丽安拔枪惊骇喝问"},
            {"match": "彻底销毁关于它的一切知识，是消灭它的唯一办法！", "role_id": "lyn_marness", "tags": "[shouting]", "stability": 0.0, "note": "马内斯捂眼嘶喊：恢复我记忆就是自杀召唤术"},
            {"match": "艾尔！你的意识还在里面吗？！", "role_id": "marion_wheeler", "tags": "[shouting]", "stability": 0.0, "note": "玛丽安退至船舷持枪锁住马内斯眉心"},
            {"match": "还有一个办法能挽回局面！", "role_id": "lyn_marness", "tags": "[hoarsely] [desperately]", "stability": 0.0, "note": "马内斯跪倒紧闭双眼摸索爬行嘶喊"},
            {"match": "艾尔，你必须立刻告诉我这东西究竟是什么！", "role_id": "marion_wheeler", "tags": "[shouting]", "stability": 0.0, "note": "玛丽安厉喝追问怪物本质"},
            {"match": "那跟我们该做的事完全背道而驰！你必须去引爆另一颗逆模因炸弹！", "role_id": "lyn_marness", "tags": "[shouting]", "stability": 0.0, "note": "马内斯嘶吼唯一生路"},
            {"match": "我们手里根本没有那种炸弹！", "role_id": "marion_wheeler", "tags": "[rushed]", "stability": 0.0, "note": "玛丽安急促反驳"},
            {"match": "你们一直都有！就在四十一号站点底下有一座重型工程实验室", "role_id": "lyn_marness", "tags": "[shouting]", "stability": 0.0, "note": "马内斯狂吼点破41号站点地下闲置实验室"},
            {"match": "可那只会把一切打回原点！", "role_id": "marion_wheeler", "tags": "[shouting]", "stability": 0.0, "note": "玛丽安怒吼追问如何收容"},
            {"match": "我们收容不了！永远也不可能收容！", "role_id": "lyn_marness", "tags": "[shouting] [desperately]", "stability": 0.0, "note": "马内斯绝望咆哮道破逆模因部宿命死循环"},
            {"match": "它到底是什么东西？！真相绝不可能就这么一点！", "role_id": "marion_wheeler", "tags": "[shouting]", "stability": 0.0, "note": "巨蛛刺穿左眼时玛丽安仍执念怒吼追问"},
            {"match": "救——", "role_id": "lyn_marness", "tags": "[gasps] [hoarsely]", "stability": 0.0, "note": "马内斯咽喉被巨蛛步足绞碎前的最后半个字"},
            {"match": "见鬼……这到底是怎么回事？这是哪儿啊？！", "role_id": "marion_wheeler", "tags": "[gasps] [trembling]", "stability": 0.0, "note": "B级记忆删除剂生效，玛丽安在冰湖中失忆惊醒"},
        ],
        sfx_blueprint=[
            {"p": 4, "pos": "before", "slug": "lake_water_lapping_boat", "sfx_prompt": "Gentle calm lake waves lapping softly against a small fiberglass motorboat hull under a quiet breeze", "duration_seconds": 3.2, "gain_db": -2.0, "note": "微风与湖水轻拍游艇船舷"},
            {"p": 21, "pos": "before", "slug": "class_x_guide_terminal", "motif_id": "motif_scp_terminal_boot", "gain_db": -1.0, "note": "调取X级记忆强化剂绝密档案"},
            {"p": 32, "pos": "before", "slug": "iv_syringe_push", "sfx_prompt": "Medical alcohol swab rustle and glass syringe plunger injecting serum steadily with a subtle high-frequency neural shimmer", "duration_seconds": 2.6, "gain_db": -1.0, "note": "推注第二针高浓度X级逆龄血清"},
            {"p": 51, "pos": "before", "slug": "scp3125_gaze_static", "motif_id": "motif_antimemetic_static", "gain_db": 0.0, "note": "触及1976逃逸恶神记忆，高维视线锁定"},
            {"p": 66, "pos": "before", "slug": "spider_appendage_eye_burst", "sfx_prompt": "Horrific wet visceral rip and heavy chitinous monster leg bursting outward with chittering sub-bass dread on a wooden boat deck", "duration_seconds": 3.4, "gain_db": 1.0, "note": "黑色刚毛巨蛛触肢从马内斯左眼眶破体而出"},
            {"p": 70, "pos": "before", "slug": "six_gunshots_into_sky", "sfx_prompt": "Single sharp pistol shot followed by five rapid 9mm gunshots fired upward into open outdoor air over a lake with echoing reports", "duration_seconds": 3.8, "gain_db": 1.0, "note": "玛丽安一枪击穿马内斯后对空打光弹匣"},
            {"p": 75, "pos": "before", "slug": "thirty_meter_lake_plunge", "sfx_prompt": "Two-second rushing wind freefall culminating in a massive violent body splash plunging deep into freezing underwater silence", "duration_seconds": 3.8, "gain_db": 1.5, "note": "十层楼高空跃下重重砸入冰冷湖水"},
            {"p": 76, "pos": "before", "slug": "b_amnestic_memory_wipe", "motif_id": "motif_memory_wipe_pulse", "gain_db": 0.0, "note": "B级记忆删除剂与冰水冲击清空记忆"},
        ],
    )
    j04, m04 = save_episode_scripts(s04, SCRIPTS_DIR, registry)
    built.append(("E004", j04, m04))

    # =========================================================================
    # E005 · 第5章 无色绿意案 (51 paras, 29 quotes)
    # =========================================================================
    md_05 = SOURCE_DIR / "第05章_无色绿意案.md"
    s05 = compile_episode_cue_sheet(
        episode_id="E005",
        chapter_number=5,
        source_md_path=md_05,
        source_rel_path=f"source_chapters/{md_05.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_unit_3125_airlock",
                "start_p": 1,
                "title": "第一幕 · 三一二五号收容单元：一片口香糖",
                "bgm_prompt": "Stark clinical sci-fi containment suspense score, cold pulsing sub-bass drone and minimalist metallic ticks outside a sealed vault, instrumental only, no vocals",
                "bgm_duration_s": 85.0,
            },
            {
                "act_id": "act2_inverted_containment_video",
                "start_p": 13,
                "title": "第二幕 · 逆向收容密室：来自过去的认输录像",
                "bgm_prompt": "Haunting desolate dark ambient score, hollow ghostly synth pads, distant mournful bowed glass and crushing cosmic dread, instrumental only, no vocals",
                "bgm_duration_s": 110.0,
            },
            {
                "act_id": "act3_head_slam_and_not_kim",
                "start_p": 36,
                "title": "第三幕 · 自撞昏迷越狱：被夺舍的保罗·金",
                "bgm_prompt": "Ferocious panic-stricken sci-fi horror action score, jagged industrial percussion, screeching metallic tension and catastrophic breach alarms, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
        ],
        acoustic_ranges=[
            (1, 1, "mental_realm"),
        ],
        dialogue_specs=[
            {"match": "项目编号：SCP-3125。项目等级：Keter", "role_id": "db_terminal", "stability": 1.0, "space": "mental_realm", "note": "终端播报SCP-3125极简逆向收容档案"},
            {"match": "你在跟我开玩笑吧？整篇档案就只有这么几行字？", "role_id": "paul_kim", "tags": "[rushed]", "stability": 0.0, "note": "保罗·金瞪大眼睛难以置信"},
            {"match": "整篇档案就只有这么几行字", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安平静回应"},
            {"match": "没有项目描述、没有收容起源报告", "role_id": "paul_kim", "tags": "[rushed]", "stability": 0.0, "note": "金连珠炮质疑空白档案"},
            {"match": "很明显，这座收容单元肯定是巴特·休斯亲手设计的", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安一眼认出休斯建筑风格"},
            {"match": "我实在不喜欢看你定期把自己暴露在一个", "role_id": "paul_kim", "tags": "[sighs]", "stability": 0.5, "note": "金紧锁眉头担忧劝阻"},
            {"match": "你打算随身带什么装备进去？", "role_id": "paul_kim", "tags": "[rushed]", "stability": 0.5, "note": "金在气闸门外急问"},
            {"match": "一片口香糖", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "玛丽安耸肩淡定幽默"},
            {"match": "我可以去给你领全套外勤作战装备！", "role_id": "paul_kim", "tags": "[shouting]", "stability": 0.0, "note": "气闸闭合时金冲着门缝焦急高喊"},
            {"match": "玛丽安，是我", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.5, "space": "memory_echo", "note": "笔记本电脑扬声器传出过去自己的声音"},
            {"match": "想必你已经猜到了，SCP-3125根本就不在这间屋子里", "role_id": "marion_wheeler", "tags": "[hoarsely]", "stability": 0.5, "space": "memory_echo", "note": "录像里的惠勒疲惫揭晓『逆向收容』真相：全世界早已沦陷"},
            {"match": "世界上任何一个够格的逆模因研究课题组", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "space": "memory_echo", "note": "录像里的惠勒阐述五维巨物投影指纹"},
            {"match": "可一旦你的研究再往深处迈出一步", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.5, "space": "memory_echo", "note": "录像里的惠勒一边画五指巨手一边讲述完形拼合"},
            {"match": "一旦那一幕发生，一旦你与它形成了", "role_id": "marion_wheeler", "tags": "[whispers]", "stability": 0.0, "space": "memory_echo", "note": "录像里的惠勒飘忽讲述视线对视连坐灭绝"},
            {"match": "你该如何去对抗一个你甚至绝对不能发现它存在的敌人？", "role_id": "marion_wheeler", "tags": "[desperately]", "stability": 0.0, "space": "memory_echo", "note": "录像里的惠勒绝望报出四百组织全灭与两百人仅存四十人"},
            {"match": "原本有一台机器是我们可以造出来的", "role_id": "marion_wheeler", "tags": "[hoarsely]", "stability": 0.5, "space": "memory_echo", "note": "录像里的惠勒讲述休斯死后无人能造出模因增幅巨构"},
            {"match": "那就再想别的办法啊！你到底怎么回事？！", "role_id": "marion_wheeler", "tags": "[angry]", "stability": 0.0, "space": "dry", "note": "屏幕前的惠勒怒火中烧对着录像低吼"},
            {"match": "我本可以直接死在这间屋子里的", "role_id": "marion_wheeler", "tags": "[crying]", "stability": 0.0, "space": "memory_echo", "note": "录像里的惠勒空洞低语提及已故丈夫亚当"},
            {"match": "你不该是这副样子的，玛丽安，你明明比这坚强得多！", "role_id": "marion_wheeler", "tags": "[whispers] [trembling]", "stability": 0.0, "space": "dry", "note": "桌前的惠勒脸色煞白颤声追问亚当是谁"},
            {"match": "我不知道我们怎么才能活下去，不知道怎么才能赢", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.0, "space": "memory_echo", "note": "录像里的惠勒认输道别"},
            {"match": "天哪，我的眼睛好疼……我觉得它们已经钻", "role_id": "marion_wheeler", "tags": "[gasps] [desperately]", "stability": 0.0, "space": "memory_echo", "note": "录像里的惠勒走出气闸门瞬间遭3125收容失效侵蚀惨叫"},
            {"match": "按规程我们得搜查你身上有没有夹带笔记——", "role_id": "paul_kim", "tags": "[calmly]", "stability": 0.5, "note": "外间保罗·金下意识例行公事开口"},
            {"match": "你在里头到底遭遇什么了？！", "role_id": "paul_kim", "tags": "[gasps]", "stability": 0.0, "note": "金看见满头鲜血的惠勒惊愕发问"},
            {"match": "我只需要……喘口气……缓一秒钟就好", "role_id": "marion_wheeler", "tags": "[gasps] [hoarsely]", "stability": 0.0, "note": "自撞昏迷躲过清洗脉冲的惠勒剧烈喘息"},
            {"match": "按理说你绝不可能记得任何东西才对……你到底干了什么？", "role_id": "paul_kim", "tags": "[coldly]", "stability": 0.0, "note": "3125瞬间夺舍取代保罗·金，眼神冰冷质问"},
            {"match": "自己拿头撞墙砸晕了呗", "role_id": "marion_wheeler", "tags": "[hoarsely]", "stability": 0.5, "note": "惠勒随口答完猛然察觉金杀意锁门"},
            {"match": "你的脸色难看极了。你脖子皮……肉里头", "role_id": "paul_kim", "tags": "[coldly]", "stability": 0.0, "note": "被感染的非金语调扭曲乱码指着咽喉"},
            {"match": "什么？！", "role_id": "marion_wheeler", "tags": "[gasps]", "stability": 0.0, "note": "惠勒瞳孔骤缩"},
            {"match": "就在你脖子上。我觉……得你已经被屋里那东西感染了", "role_id": "paul_kim", "tags": "[coldly]", "stability": 0.0, "note": "非金弹出瑞士军刀刺向惠勒咽喉"},
        ],
        sfx_blueprint=[
            {"p": 1, "pos": "before", "slug": "scp3125_terminal_boot", "motif_id": "motif_scp_terminal_boot", "gain_db": -0.5, "note": "终端显示SCP-3125极简词条"},
            {"p": 8, "pos": "before", "slug": "rotary_airlock_open", "motif_id": "motif_heavy_blast_door", "gain_db": -0.5, "note": "刷门禁卡开启三一二五旋转气闸圆筒"},
            {"p": 13, "pos": "before", "slug": "fluorescent_tubes_buzz", "sfx_prompt": "Half-broken overhead fluorescent tubes flickering on with a cold electrical buzz in a sealed glass vault", "duration_seconds": 2.8, "gain_db": -1.5, "note": "密室残损日光灯管嗡鸣亮起"},
            {"p": 35, "pos": "before", "slug": "video_airlock_purge_pulse", "motif_id": "motif_memory_wipe_pulse", "gain_db": 0.5, "note": "录像末尾气闸清洗脉冲炸响后屏幕死黑"},
            {"p": 40, "pos": "after", "slug": "head_slam_against_wall", "sfx_prompt": "Three brutal sickening skull impacts slamming hard against solid frosted bulletproof glass wall followed by body slumping unconscious", "duration_seconds": 3.4, "gain_db": 1.0, "note": "惠勒用自己的头狠撞墙壁砸晕自己"},
            {"p": 44, "pos": "before", "slug": "kim_infected_static", "motif_id": "motif_antimemetic_static", "gain_db": 0.5, "note": "3125瞬间吞噬并接管保罗·金心智"},
            {"p": 50, "pos": "before", "slug": "knife_scrape_airlock_fight", "sfx_prompt": "Pocket knife blade flicking open and screeching violently across curved steel airlock wall during a desperate close-quarters struggle", "duration_seconds": 3.4, "gain_db": 1.0, "note": "瑞士军刀刮擦气闸金属内壁生死搏斗"},
            {"p": 51, "pos": "before", "slug": "site41_distant_explosion", "sfx_prompt": "Massive muffled subterranean explosion echoing down concrete corridors with distant containment breach klaxons wailing", "duration_seconds": 4.0, "gain_db": 1.0, "note": "站点远处轰隆爆炸与收容失效警报"},
        ],
    )
    j05, m05 = save_episode_scripts(s05, SCRIPTS_DIR, registry)
    built.append(("E005", j05, m05))

    # =========================================================================
    # E006 · 第6章 你最后一次首日上班 (41 paras, 19 quotes)
    # =========================================================================
    md_06 = SOURCE_DIR / "第06章_你最后一次首日上班.md"
    s06 = compile_episode_cue_sheet(
        episode_id="E006",
        chapter_number=6,
        source_md_path=md_06,
        source_rel_path=f"source_chapters/{md_06.name}",
        registry=registry,
        acts_blueprint=[
            {
                "act_id": "act1_elevator_class_z_overload",
                "start_p": 1,
                "title": "第一幕 · 货运电梯下行：一针Z级终极强化剂",
                "bgm_prompt": "Catastrophic subterranean sci-fi thriller score, distant muffled explosions above, throbbing industrial freight elevator rumble and rising neural tension, instrumental only, no vocals",
                "bgm_duration_s": 90.0,
            },
            {
                "act_id": "act2_duel_with_voice_of_3125",
                "start_p": 12,
                "title": "第二幕 · 脑海交锋：拿更强大的观念来杀",
                "bgm_prompt": "Colossal five-dimensional cosmic horror score, overwhelming sub-bass roar, razor-sharp dissonant synth brass and defiant solitary human pulse, instrumental only, no vocals",
                "bgm_duration_s": 100.0,
            },
            {
                "act_id": "act3_b30_antimemetic_hbomb_finale",
                "start_p": 27,
                "title": "第三幕 · 地下三十层终局：这世上根本就没有逆模因部",
                "bgm_prompt": "Tragic monumental sci-fi requiem score, vast hollow hangar resonance, mournful solitary cello over dark modular synth fading into absolute black silence, instrumental only, no vocals",
                "bgm_duration_s": 105.0,
            },
        ],
        acoustic_ranges=[
            (12, 26, "mental_realm"),
            (28, 41, "vast_hall"),
        ],
        dialogue_specs=[
            {"match": "这也太过分了！我根本应付不了这种场面", "role_id": "marion_wheeler", "tags": "[angry] [shouting]", "stability": 0.0, "note": "失忆的惠勒在电梯里愤怒骂出：今天才是我第一天上班"},
            {"match": "当那个怪物看见我的第一秒钟", "role_id": "marion_wheeler", "tags": "[calmly]", "stability": 0.5, "note": "惠勒对着面板倒影逆向推演自己布下的盲棋"},
            {"match": "想来最聪明的先手第一步", "role_id": "marion_wheeler", "tags": "[softly]", "stability": 0.5, "note": "惠勒挠着左腕针眼推导出Z级药剂"},
            {"match": "我知道该怎么打败你了", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.0, "space": "mental_realm", "note": "惠勒砸破拳骨锚定神智，向高维恶神宣战"},
            {"match": "不，你不知道", "role_id": "scp_3125_voice", "tags": "[coldly]", "stability": 0.0, "space": "mental_realm", "note": "SCP-3125冰冷低沉幻听在脑海直接响起"},
            {"match": "SCP-3125根本没有嗓音", "role_id": "marion_wheeler", "tags": "[hoarsely]", "stability": 0.5, "space": "mental_realm", "note": "惠勒紧闭双眼咬牙否定幻听"},
            {"match": "我当然有", "role_id": "scp_3125_voice", "tags": "[sarcastic]", "stability": 0.0, "space": "mental_realm", "note": "3125讥诮回应"},
            {"match": "SCP-3125只是一团由恶毒模因与恶毒逆模因", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "惠勒一字一顿背诵五维癌变聚合体科学定义"},
            {"match": "玛丽安，你知道我最恨你哪一点吗？", "role_id": "scp_3125_voice", "tags": "[sarcastic]", "stability": 0.0, "space": "mental_realm", "note": "3125冷哼嘲弄她屡战屡败却仍活着"},
            {"match": "总得有人撑到最后一个。总得有人做到最好", "role_id": "marion_wheeler", "tags": "[hoarsely]", "stability": 0.0, "space": "mental_realm", "note": "惠勒拄着外星射线枪撑地站起"},
            {"match": "你的团队已经死绝了！他们的心智像眼珠子一样", "role_id": "scp_3125_voice", "tags": "[coldly] [sarcastic]", "stability": 0.0, "space": "mental_realm", "note": "3125宣告全员团灭只剩一个人的逆模因部"},
            {"match": "观念是可以被杀死的", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.5, "space": "mental_realm", "note": "惠勒迈入巨型铅封气闸冷冷宣告"},
            {"match": "拿什么杀？", "role_id": "scp_3125_voice", "tags": "[sarcastic]", "stability": 0.0, "space": "mental_realm", "note": "3125反问"},
            {"match": "拿更强大的观念来杀", "role_id": "marion_wheeler", "tags": "[coldly]", "stability": 0.0, "space": "mental_realm", "note": "气闸锁死将3125隔绝门外"},
            {"match": "休斯！时间到了！", "role_id": "marion_wheeler", "tags": "[shouting] [hoarsely]", "stability": 0.0, "space": "vast_hall", "note": "双目近盲的惠勒在空旷地下机库中放声高喊"},
            {"match": "我找到她了", "role_id": "paul_kim", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "非金召唤十几个被抽空灵魂的前特工躯壳"},
            {"match": "她为什么没有正常敞开心智？", "role_id": "subject_055", "tags": "[coldly]", "stability": 0.5, "space": "vast_hall", "note": "被感染男特工空壳俯视疑惑"},
            {"match": "先从她的眼睛下手吧，这样她剩下的部分就更容易纠正了", "role_id": "infected_female", "tags": "[coldly]", "stability": 0.0, "space": "vast_hall", "note": "被感染女特工空壳冷血提议挖眼"},
            {"match": "这一切都从未发生过，保罗。你和我，都从来没有存在过", "role_id": "marion_wheeler", "tags": "[whispers]", "stability": 0.0, "space": "vast_hall", "gap_after_s": 0.9, "note": "惠勒垂死贴耳绝唱：这世上根本就没有逆模因部"},
        ],
        sfx_blueprint=[
            {"p": 1, "pos": "before", "slug": "freight_elevator_descent", "sfx_prompt": "Heavy industrial subterranean freight elevator descending deep underground with steel cable hum and distant muffled ceiling collapses far above", "duration_seconds": 3.6, "gain_db": -0.5, "note": "主货运电梯向地下三十层深渊下沉"},
            {"p": 10, "pos": "before", "slug": "class_z_overload_static", "motif_id": "motif_antimemetic_static", "gain_db": 0.5, "note": "Z级药剂全面爆发，剥除遗忘能力"},
            {"p": 13, "pos": "before", "slug": "fist_smash_steel_panel", "sfx_prompt": "Bare human fist slamming brutally into solid steel elevator wall with a sharp metallic thud and knuckle crack", "duration_seconds": 2.2, "gain_db": 1.0, "note": "惠勒一拳砸向电梯钢壁以剧痛锚定神智"},
            {"p": 23, "pos": "before", "slug": "b30_ten_ton_airlock", "motif_id": "motif_heavy_blast_door", "gain_db": 0.5, "note": "地下三十层十吨级铅封心灵遮断旋转气闸解锁"},
            {"p": 35, "pos": "before", "slug": "raygun_clatter_hangar", "sfx_prompt": "Heavy futuristic metallic rifle tossed carelessly clattering and echoing across a vast dusty epoxy hangar floor", "duration_seconds": 2.8, "gain_db": -0.5, "note": "非金随手把外星射线枪扔在机库地上"},
            {"p": 40, "pos": "before", "slug": "antimemetic_bomb_click", "sfx_prompt": "Single ultra-crisp precision mechanical relay click on the back of a military truck echoing in a silent underground hangar", "duration_seconds": 1.8, "gain_db": 1.0, "note": "军用卡车后斗逆模因氢弹咔哒一声完成充能点火"},
            {"p": 41, "pos": "before", "slug": "final_antimemetic_detonation", "motif_id": "motif_memory_wipe_pulse", "gain_db": 1.5, "note": "逆模因氢弹起爆，万物归于纯粹的黑"},
        ],
    )
    j06, m06 = save_episode_scripts(s06, SCRIPTS_DIR, registry)
    built.append(("E006", j06, m06))

    # Update production_progress_ledger.json
    aud_path = build_audition_pack(registry)
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    by_ep = {ep["episode_id"]: ep for ep in ledger["episodes"]}
    for eid, j_path, _m_path in built:
        by_ep[eid]["status"] = "script_validated"
        by_ep[eid]["cue_sheet_file"] = f"02_分集广播剧台本/{j_path.name}"
    ledger["updated_at"] = utc_now_iso()
    ledger["summary"]["scripts_ready"] = len(built)
    LEDGER_PATH.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"✅ Built Audition Pack: {aud_path.name}")
    for eid, j_path, m_path in built:
        cs = EpisodeCueSheet.load(j_path)
        dial_n = sum(1 for c in cs.cues if c.kind == "dialogue")
        sfx_n = sum(1 for c in cs.cues if c.kind == "sfx")
        print(f"✅ [{eid}] {j_path.name} | acts={len(cs.acts)} | dialogue_cues={dial_n} | sfx_cues={sfx_n}")
    return built


if __name__ == "__main__":
    build_all_episodes()
