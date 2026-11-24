#!/usr/bin/env python3
"""Build V2.1 Pilot Episode: 《商战大瓜英语局》E001《OpenAI 政变 72 小时》.

V2.1 Upgrades (Addressing All 4 Listener Audit Notes):
  1. Same Dry Studio Booth (Zero Male Echo): Male co-host 大周 switched from reverberant `guest_laozhou.wav`
     to dry close-mic `guest_huaiyuan.wav` (exact same OpenMOSS studio room as `host_zhiwei.wav`, stereo pan -0.12 / +0.14).
  2. Relaxed Xiaoyuzhou Café-Chat Tone (Zero Stage-Acting Overhype): Cut 85% of exclamation marks and excessive
     chuckles (3 organic laughs max), set host `stability=0.5`, dry-wit conversational Chinese phrasing.
  3. Crisp Modern Podcast Pace (`playback_rate=1.16` pitch-preserving `atempo=1.160` on host banter cues + tight
     inter-turn gaps `-0.04s..0.06s`), bringing total runtime to a snappy ~6.8-7.2 min.
  4. Authentic Real-Person Voices + 100% Character-Matched Act 5 Takeaway Card + Distinct World Accents:
     - `board_ilya`: Real Ilya Sutskever solo studio anchor (Russian-Canadian AI scientist accent) -> voices Phrase 1 (`Let's be candid.`)
     - `satya_nadella`: Dry 47.8dB Indian business executive accent (`rajiv_menon.wav`) -> voices Phrases 2 & 3 (`We were completely blindsided.` / `Not on my watch.`)
     - `sam_altman`: Real Sam Altman solo studio anchor (Silicon Valley founder cadence) -> voices Phrase 4 (`We have the leverage.`)
     - `exec_female`: Crisp Meta Expresso `ex02` Silicon Valley American female exec.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
REPO_ROOT = PROJECT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from aigc_audio_pipeline.adapter import export_cue_sheet_markdown  # noqa: E402
from aigc_audio_pipeline.models import (  # noqa: E402
    ActMusicSpec,
    EpisodeCueSheet,
    SonicMotif,
    TimelineCue,
    VoiceCastingRegistry,
    VoiceProfile,
    extract_tags_and_spoken_text,
)

META_DIR = PROJECT_DIR / "00_节目圣经与选角档案"
SCRIPTS_OUT_DIR = PROJECT_DIR / "02_分集广播剧台本"

HOST_PACE = 1.16  # Pitch-preserving WSOLA atempo=1.160 -> crisp Xiaoyuzhou conversational cadence

# Upbeat, witty, modern corporate-heist / The Big Short style pure instrumental BGM prompts (zero funeral cello!)
BGM_COLD_OPEN = (
    "Upbeat witty modern Silicon Valley caper underscore like The Big Short and Ocean's Eleven, "
    "crisp plucked pizzicato strings, nimble acoustic upright bass groove, light brushed snare pulse, "
    "energetic intriguing storytelling rhythm, strictly instrumental, no vocals, no singing, no dark funeral drone"
)
BGM_FLASH_DRAMA = (
    "Taut brisk modern tech thriller pulse like The Social Network, subtle ticking rhythmic synth arpeggio "
    "and crisp muted electric bass drive, high-stakes boardroom coup momentum, clean modern production, "
    "strictly instrumental, no vocals, no singing, no traditional instruments"
)
BGM_OUTRO_GROOVE = (
    "Bright crisp modern podcast outro groove, light jazzy Rhodes electric piano chords with clean finger-snap "
    "percussion and warm upright bass bounce, upbeat confident urban feel, strictly instrumental, no vocals, no singing"
)


def build_registry() -> VoiceCastingRegistry:
    roles = {
        "host_xiaowei": VoiceProfile(
            role_id="host_xiaowei",
            display_name="小微",
            aliases=["主机小微", "主理人小微"],
            tier="protagonist",
            gender="female",
            age_group="young_adult",
            language_code="zh-en",
            accent_code="zh_en_bilingual_us",
            vocal_register="清亮松弛、语速明快、不端着的小宇宙女主播（贴麦纯干声），英文短句自然地道",
            persona_summary="硅谷商业故事主讲人，节奏利落、冷幽默、不喊麦不演戏，专把商战名场面里的短狠英文翻译成日常上班场景。",
            accent_requirement="标准现代大陆普通话贴麦聊天口吻（零播音腔、零演戏感）+ 地道美式英文短句",
            status="locked",
            voice_id="drama3_anchor_host_xiaowei",
            library_voice_name="Real-Human Dry Studio: host_zhiwei (OpenMOSS Apache-2.0)",
            default_stability=0.5,
            similarity_boost=0.82,
            signature_tags=["[conversational]", "[curious]", "[chuckles]"],
            forbidden_habits=["严禁晚会播音腔", "严禁夸张喊麦感", "严禁英文老师说教腔"],
            first_appearance_chapter=1,
            appearance_chapters=[1],
            audition_line="[conversational] 估值八百六十亿美元的老板，居然在一个十五分钟视频会里被自己公司开除了。",
        ),
        "guest_huaiyuan": VoiceProfile(
            role_id="guest_huaiyuan",
            display_name="大周",
            aliases=["搭档大周", "老周", "怀远"],
            tier="core_supporting",
            gender="male",
            age_group="middle_aged",
            language_code="zh-en",
            accent_code="zh_en_bilingual_cn",
            vocal_register="贴麦干声、温润松弛、带冷幽默吐槽感的现代男搭档（与小微同一无回音棚录声场），英文短词发音清晰自然",
            persona_summary="普通打工人和创业者的清醒嘴替，松弛聊八卦不浮夸，专门一针见血把硅谷宫斗翻成咱们平时上班的人情世故。",
            accent_requirement="标准大陆普通话近讲贴麦聊天口吻（严禁房间回音、严禁浮夸小品腔）+ 自然清晰英文词连读",
            status="locked",
            voice_id="drama3_anchor_guest_huaiyuan",
            library_voice_name="Real-Human Dry Studio: guest_huaiyuan (OpenMOSS Apache-2.0, same booth as host_zhiwei)",
            default_stability=0.5,
            similarity_boost=0.82,
            signature_tags=["[conversational]", "[wryly]", "[chuckles]"],
            forbidden_habits=["严禁房间混响回音", "严禁过度亢奋演戏腔"],
            first_appearance_chapter=1,
            appearance_chapters=[1],
            audition_line="[conversational] 刷了一百三十亿当榜一大哥，临开播前一分钟才通知把头牌封号了，换谁都得上火。",
        ),
        "sam_altman": VoiceProfile(
            role_id="sam_altman",
            display_name="Sam Altman",
            aliases=["奥特曼", "Sam"],
            tier="core_supporting",
            gender="male",
            age_group="young_adult",
            language_code="en",
            accent_code="us_silicon_valley",
            vocal_register="Authentic Sam Altman studio podcast voice: crisp, brisk, slightly dry Silicon Valley founder cadence",
            persona_summary="OpenAI CEO Sam Altman in the November 2023 board coup — blindsided on Friday, ice-cold comeback by Wednesday.",
            accent_requirement="Authentic Sam Altman Silicon Valley American English (real solo studio podcast anchor)",
            status="locked",
            voice_id="drama3_anchor_sam_altman",
            library_voice_name="Real-Person Studio Anchor: Sam Altman solo interview (014_AI dry close-mic)",
            default_stability=0.0,
            similarity_boost=0.88,
            signature_tags=["[shocked]", "[firmly]", "[confident]", "[blunt]"],
            forbidden_habits=["No ESL slow textbook reading", "No generic radio announcer baritone"],
            first_appearance_chapter=1,
            appearance_chapters=[1],
            audition_line="[shocked] Wait—are you firing me right now?",
        ),
        "board_ilya": VoiceProfile(
            role_id="board_ilya",
            display_name="Ilya Sutskever",
            aliases=["伊利亚", "董事会代表", "Ilya"],
            tier="antagonist",
            gender="male",
            age_group="middle_aged",
            language_code="en",
            accent_code="intl_russian_canadian_ai",
            vocal_register="Authentic Ilya Sutskever studio podcast voice: calm, deliberate, distinctive Russian-Israeli-Canadian AI scientist accent",
            persona_summary="OpenAI Chief Scientist & board member Ilya Sutskever delivering the polite yet devastating firing notice over Google Meet.",
            accent_requirement="Authentic Ilya Sutskever accented English (real solo Lex Fridman studio anchor, 022_AI)",
            status="locked",
            voice_id="drama3_anchor_board_ilya",
            library_voice_name="Real-Person Studio Anchor: Ilya Sutskever solo podcast (022_AI dry close-mic)",
            default_stability=0.0,
            similarity_boost=0.88,
            signature_tags=["[coldly]", "[icy polite]", "[measured]"],
            forbidden_habits=["No shouting or cartoonish villainy"],
            first_appearance_chapter=1,
            appearance_chapters=[1],
            audition_line="[coldly] Sam, you haven't been consistently candid.",
        ),
        "satya_nadella": VoiceProfile(
            role_id="satya_nadella",
            display_name="Satya Nadella",
            aliases=["纳德拉", "微软CEO"],
            tier="core_supporting",
            gender="male",
            age_group="middle_aged",
            language_code="en",
            accent_code="intl_indian_exec",
            vocal_register="Commanding, articulate educated Indian-American tech CEO baritone, razor-sharp executive authority",
            persona_summary="Microsoft CEO Satya Nadella — furious at being blindsided on a $13B stake, executing a midnight counter-strike.",
            accent_requirement="Authentic, crystal-clear educated Indian-American executive English (zero caricature)",
            status="locked",
            voice_id="drama3_anchor_satya_nadella",
            library_voice_name="Real-Human Studio Reuse: rajiv_menon (47.8dB dry Indian business podcaster)",
            default_stability=0.0,
            similarity_boost=0.86,
            signature_tags=["[angry]", "[firmly]", "[blunt]"],
            forbidden_habits=["No exaggerated accent caricature"],
            first_appearance_chapter=1,
            appearance_chapters=[1],
            audition_line="[angry] We were completely blindsided.",
        ),
        "exec_female": VoiceProfile(
            role_id="exec_female",
            display_name="OpenAI Exec",
            aliases=["高管代表", "女高管"],
            tier="recurring",
            gender="female",
            age_group="young_adult",
            language_code="en",
            accent_code="us_silicon_valley",
            vocal_register="Sharp, fast, crisp Silicon Valley female tech executive American English",
            persona_summary="Senior OpenAI executive / employee revolt spokesperson rallying 700 signatures.",
            accent_requirement="Crisp Silicon Valley General American Female English",
            status="locked",
            voice_id="drama3_anchor_exec_female",
            library_voice_name="Real-Human Studio Reuse: victoria_vance (Meta Expresso ex02 48kHz studio)",
            default_stability=0.0,
            similarity_boost=0.85,
            signature_tags=["[urgent]", "[firmly]", "[blunt]"],
            forbidden_habits=["No slow textbook cadence"],
            first_appearance_chapter=1,
            appearance_chapters=[1],
            audition_line="[urgent] Seven hundred people signed. We're backing you, Sam.",
        ),
    }

    motifs = {
        "gmeet_join_chime": SonicMotif(
            motif_id="gmeet_join_chime",
            name="Google Meet 视频会进房提示音",
            description="清脆利落的现代视频会议软件进房叮咚声（瞬间把听众拉进 2023 年周五中午的鸿门宴）",
            sfx_prompt="Crisp clean two-tone modern video conference call join chime followed by a subtle laptop microphone unmute click, pure foley, no human voice",
            duration_seconds=1.6,
            prompt_influence=0.65,
        ),
        "record_scratch_freeze": SonicMotif(
            motif_id="record_scratch_freeze",
            name="综艺定格切换叮咚提示音",
            description="明快干脆的现代播客定格转场提示音（短剧狠话甩完立刻切回双主播干声拆台）",
            sfx_prompt="Snappy clean modern broadcast transition pop chime with subtle percussive rim click, crisp podcast sting, pure foley, no human voice",
            duration_seconds=1.0,
            prompt_influence=0.60,
        ),
        "midnight_phone_buzz": SonicMotif(
            motif_id="midnight_phone_buzz",
            name="凌晨手机狂震与接通声",
            description="木质床头柜上手机疯狂连续震动两下后接通免提电话的真实拟音（纳德拉半夜被惊醒名场面）",
            sfx_prompt="Smartphone vibrating urgently twice on a wooden nightstand in a quiet bedroom followed by a crisp call pickup beep, pure foley, no human voice",
            duration_seconds=2.2,
            prompt_influence=0.65,
        ),
        "tweet_post_and_buzz": SonicMotif(
            motif_id="tweet_post_and_buzz",
            name="键盘狂敲与办公室骚动欢呼",
            description="机械键盘急速敲击接清脆发送提示音与隐约办公区鼓掌沸腾声（700 员工逼宫与奥特曼杀回总部）",
            sfx_prompt="Fast brisk laptop typing burst ending in a crisp message sent whoosh followed by brief upbeat office applause in a bright modern glass headquarters, pure foley, no human voice",
            duration_seconds=2.4,
            prompt_influence=0.60,
        ),
    }

    return VoiceCastingRegistry(
        project_id="silicon_gossip",
        project_title="《商战大瓜英语局》— 真实硅谷/华尔街名场面轻英语广播剧场",
        domain="hotline_roundtable",
        language_code="zh-en",
        tts_model_id="fishaudio/drama-3",
        sfx_model_id="OpenMOSS-Team/MOSS-SoundEffect-v2.0",
        music_model_id="ACE-Step/acestep-v15-xl-turbo-diffusers",
        asr_model_id="faster-whisper-small-int8",
        roles=roles,
        sonic_motifs=motifs,
    )


def _dlg(
    cid: str,
    act: str,
    role: str,
    text: str,
    *,
    lang: str = "zh",
    space: str = "chatroom_table",
    gap: float = 0.05,
    stab: float | None = None,
    rate: float | None = None,
    sub_zh: str = "",
    note: str = "",
) -> TimelineCue:
    is_host = role in ("host_xiaowei", "guest_huaiyuan")
    eff_stab = (0.5 if is_host else 0.0) if stab is None else stab
    eff_rate = (HOST_PACE if is_host else 1.0) if rate is None else rate
    return TimelineCue(
        cue_id=cid,
        act_id=act,
        kind="dialogue",
        role_id=role,
        text=text,
        language_code=lang,
        stability=eff_stab,
        acoustic_space=space,
        gap_after_s=gap,
        playback_rate=eff_rate,
        subtitle_translation=sub_zh,
        director_note=note,
    )


def _sfx(cid: str, act: str, motif: str, prompt: str, dur: float, *, gap: float = 0.08, note: str = "") -> TimelineCue:
    return TimelineCue(
        cue_id=cid,
        act_id=act,
        kind="sfx",
        motif_id=motif,
        sfx_prompt=prompt,
        duration_seconds=dur,
        placement="sequential",
        gap_after_s=gap,
        director_note=note,
    )


def build_v2_pilot_cue_sheet(reg: VoiceCastingRegistry) -> EpisodeCueSheet:
    m = reg.sonic_motifs
    acts = [
        ActMusicSpec(
            act_id="act1_hook",
            title="冷开场：15 分钟视频会被自己公司开除",
            bgm_prompt=BGM_COLD_OPEN,
            bgm_duration_s=50.0,
            bgm_gain_speech=0.07,
            bgm_gain_gap=0.22,
        ),
        ActMusicSpec(
            act_id="act2_coup",
            title="第一幕：周五中午鸿门宴（学会 candid）",
            bgm_prompt="",  # Dry crisp Xiaoyuzhou chatroom banter — zero boring drone!
            bgm_duration_s=10.0,
            bgm_gain_speech=0.0,
            bgm_gain_gap=0.0,
        ),
        ActMusicSpec(
            act_id="act2_scene",
            title="名场面闪回 ①：Google Meet 开除现场（Ilya vs Sam）",
            bgm_prompt=BGM_FLASH_DRAMA,
            bgm_duration_s=35.0,
            bgm_gain_speech=0.08,
            bgm_gain_gap=0.22,
        ),
        ActMusicSpec(
            act_id="act2_roast",
            title="松弛拆台 ①：老外越客气，刀捅得越深",
            bgm_prompt="",
            bgm_duration_s=10.0,
            bgm_gain_speech=0.0,
            bgm_gain_gap=0.0,
        ),
        ActMusicSpec(
            act_id="act3_scene",
            title="名场面闪回 ②：微软 CEO 凌晨怒火（学会 blindsided / Not on my watch）",
            bgm_prompt=BGM_FLASH_DRAMA,
            bgm_duration_s=35.0,
            bgm_gain_speech=0.08,
            bgm_gain_gap=0.22,
        ),
        ActMusicSpec(
            act_id="act3_roast",
            title="松弛拆台 ②：榜一大哥被偷袭，明天开会怎么体面反杀甩锅",
            bgm_prompt="",
            bgm_duration_s=10.0,
            bgm_gain_speech=0.0,
            bgm_gain_gap=0.0,
        ),
        ActMusicSpec(
            act_id="act4_scene",
            title="名场面闪回 ③：700 员工逼宫大反转（学会 leverage / walk away）",
            bgm_prompt=BGM_FLASH_DRAMA,
            bgm_duration_s=35.0,
            bgm_gain_speech=0.09,
            bgm_gain_gap=0.24,
        ),
        ActMusicSpec(
            act_id="act4_roast",
            title="终极复盘：谁手里有底牌，谁才有资格说真话",
            bgm_prompt="",
            bgm_duration_s=10.0,
            bgm_gain_speech=0.0,
            bgm_gain_gap=0.0,
        ),
        ActMusicSpec(
            act_id="act5_card",
            title="90 秒带走卡：4 句短狠职场英文（对应人物原声 0.85x + 原速跟读）",
            bgm_prompt=BGM_OUTRO_GROOVE,
            bgm_duration_s=65.0,
            bgm_gain_speech=0.05,
            bgm_gain_gap=0.20,
        ),
    ]

    cues: list[TimelineCue] = [
        # ==================== ACT 1: COLD OPEN (0:00 - 0:40) ====================
        _sfx("v2_001", "act1_hook", "gmeet_join_chime", m["gmeet_join_chime"].sfx_prompt, 1.6, gap=0.08, note="Google Meet 开场音效"),
        _dlg("v2_002", "act1_hook", "board_ilya", "[coldly] Sam, you haven't been consistently candid.", lang="en", space="boardroom", gap=0.12, sub_zh="萨姆，你一直不够坦诚。", note="Ilya 原声开场核爆金句"),
        _sfx("v2_003", "act1_hook", "record_scratch_freeze", m["record_scratch_freeze"].sfx_prompt, 1.0, gap=0.06, note="叮一声定格切回双主播"),
        _dlg("v2_004", "act1_hook", "host_xiaowei", "[conversational] 二零二三年十一月一个周五中午，估值八百六十亿美元的 OpenAI 老板奥特曼，正在拉斯维加斯看赛车，随手点进了一条视频会议链接。", lang="zh-en", gap=0.03),
        _dlg("v2_005", "act1_hook", "host_xiaowei", "[conversational] 结果十五分钟后，他被自己亲手创办的公司，当场开除了。", gap=-0.04),
        _dlg("v2_006", "act1_hook", "guest_huaiyuan", "[conversational] 等会儿，自己创办的公司还能被自己人踢出群聊？而且刚才那句英文，听着怎么还挺客气的。", gap=0.04),
        _dlg("v2_007", "act1_hook", "host_xiaowei", "[chuckles] 客气？大周，欧美职场说话，越客气，刀捅得越深。", gap=0.06),
        _dlg("v2_008", "act1_hook", "host_xiaowei", "[conversational] 欢迎来到《商战大瓜英语局》。今天七分钟，带你扒透硅谷史上最戏剧性的 OpenAI 政变七十二小时，顺手带走四句超短、超狠、明天开会就能直接用的职场英文。", lang="zh-en", gap=0.18),

        # ==================== ACT 2: FRIDAY COUP + CANDID ====================
        _dlg("v2_009", "act2_coup", "guest_huaiyuan", "[conversational] 咱先不聊那些复杂股权啊，我就好奇一件事，奥特曼可是带出 ChatGPT 的头号功臣，谁胆子这么大敢开除他？", lang="zh-en", gap=0.04),
        _dlg("v2_010", "act2_coup", "host_xiaowei", "[conversational] 这就得说到 OpenAI 那个奇葩架构了。打个比方，你辛辛苦苦开了家全城最火的网红奶茶店，每天排队排到马路对面。", lang="zh-en", gap=0.02),
        _dlg("v2_011", "act2_coup", "host_xiaowei", "[conversational] 但你开业那天签了个章程，奶茶店不归你管，归六个不拿分红的居委会大爷管。大爷要是觉得你太爱赚钱、忘了初心，随时可以开个小会让你卷铺盖走人。", gap=-0.04),
        _dlg("v2_012", "act2_coup", "guest_huaiyuan", "[conversational] 好家伙，这哪是科技巨头，这是给自己请了六个太上皇供在头顶上。然后周五中午真动手了？", gap=0.05),
        _dlg("v2_013", "act2_coup", "host_xiaowei", "[conversational] 真动手了。周五中午十二点，首席科学家伊利亚给奥特曼发了个视频链接，一上线，镜头对面整整齐齐坐着四位董事，直接宣读结果。", gap=0.14),

        # Flash Drama Scene 1 (~18s, real Ilya + real Sam Altman voices, strictly <= 7 words per line!)
        _sfx("v2_014", "act2_scene", "gmeet_join_chime", m["gmeet_join_chime"].sfx_prompt, 1.6, gap=0.10),
        _dlg("v2_015", "act2_scene", "board_ilya", "[coldly] Sam, you haven't been consistently candid.", lang="en", space="boardroom", gap=0.14, sub_zh="萨姆，你一直不够坦诚。"),
        _dlg("v2_016", "act2_scene", "board_ilya", "[icy polite] The board has lost confidence in you.", lang="en", space="boardroom", gap=-0.06, sub_zh="董事会已经对你失去信心。"),
        _dlg("v2_017", "act2_scene", "sam_altman", "[shocked] Wait—are you firing me right now?", lang="en", space="boardroom", gap=0.14, sub_zh="等等——你们现在就要开除我？"),
        _dlg("v2_018", "act2_scene", "board_ilya", "[coldly] Yes. Effective immediately.", lang="en", space="boardroom", gap=0.16, sub_zh="是的，立刻生效。"),
        _sfx("v2_019", "act2_scene", "record_scratch_freeze", m["record_scratch_freeze"].sfx_prompt, 1.0, gap=0.06),

        # Relaxed Café-Chat Roast #1
        _dlg("v2_020", "act2_roast", "guest_huaiyuan", "[conversational] 鸡皮疙瘩都起来了，一句脏字没带，但字字往心窝子扎。那个 consistently candid 到底是啥意思？", lang="zh-en", gap=0.04),
        _dlg("v2_021", "act2_roast", "host_xiaowei", "[conversational] 这就是咱今天第一句狠话。candid 就是坦诚、直白、不藏着掖着。董事会在公告里写了一句很体面的黑话，说你 haven't been consistently candid，没有一贯保持坦诚。", lang="zh-en", gap=0.04),
        _dlg("v2_022", "act2_roast", "guest_huaiyuan", "[chuckles] 翻译成大白话不就是，你小子满嘴跑火车，当面一套背后一套，今天抓现行了，收拾东西走人吧。", gap=0.04),
        _dlg("v2_023", "act2_roast", "host_xiaowei", "[conversational] 特别准。而且 candid 这个词平时上班超级好用。以前咱想说“说句实话吧”，总爱说 be honest with me，听着有点像吵架起手式。", lang="zh-en", gap=0.03),
        _dlg("v2_024", "act2_roast", "host_xiaowei", "[conversational] 下次开会想直接摊牌，换成三个词：Let's be candid. 咱敞开天窗说亮话，瞬间就有高管气场。", lang="zh-en", gap=0.05),
        _dlg("v2_025", "act2_roast", "guest_huaiyuan", "[conversational] Let's be candid，这句短，好记。行，那奥特曼被踢了，大股东能答应吗？微软不是砸了一百三十亿美元进去吗？", lang="zh-en", gap=0.05),
        _dlg("v2_026", "act2_roast", "host_xiaowei", "[conversational] 最离谱的地方就在这儿。微软砸了一百三十亿当最大金主，结果董事会发开除公告前，整整一分钟才给微软 CEO 纳德拉发了条通知。", lang="zh-en", gap=-0.04),
        _dlg("v2_027", "act2_roast", "guest_huaiyuan", "[conversational] 提前一分钟？我刷了一百三十亿当榜一大哥，你把头牌主播封号了临开播才告诉我，换谁都得上火。", gap=0.10),

        # ==================== ACT 3: MICROSOFT FURY + BLINDSIDED ====================
        _sfx("v2_028", "act3_scene", "midnight_phone_buzz", m["midnight_phone_buzz"].sfx_prompt, 2.2, gap=0.08, note="凌晨手机狂震"),
        _dlg("v2_029", "act3_scene", "satya_nadella", "[angry] We were completely blindsided.", lang="en", space="phone_call", gap=0.14, sub_zh="我们彻底被打了个措手不及。"),
        _dlg("v2_030", "act3_scene", "satya_nadella", "[blunt] Thirteen billion dollars, and nobody called me?", lang="en", space="phone_call", gap=0.14, sub_zh="一百三十亿美元，居然没人给我打个电话？"),
        _dlg("v2_031", "act3_scene", "exec_female", "[urgent] Satya, the board is refusing to back down.", lang="en", space="phone_call", gap=0.12, sub_zh="萨提亚，董事会死活不肯让步。"),
        _dlg("v2_032", "act3_scene", "satya_nadella", "[firmly] Not on my watch. Get Sam on the phone.", lang="en", space="phone_call", gap=0.16, sub_zh="有我在，休想。马上把萨姆接进来。"),
        _sfx("v2_033", "act3_scene", "record_scratch_freeze", m["record_scratch_freeze"].sfx_prompt, 1.0, gap=0.06),

        # Relaxed Café-Chat Roast #2 & #3
        _dlg("v2_034", "act3_roast", "guest_huaiyuan", "[conversational] 纳德拉这火气，隔着电话都能听出来。那个 blindsided，听着像眼睛被蒙住了？", lang="zh-en", gap=0.04),
        _dlg("v2_035", "act3_roast", "host_xiaowei", "[conversational] 很形象。blind 是盲区，side 是侧面。blindsided 本来是橄榄球里从你视野盲区冲过来把你撞翻，放在职场里，就是事先一点风声没透，突然背刺、打你个措手不及。", lang="zh-en", gap=0.04),
        _dlg("v2_036", "act3_roast", "guest_huaiyuan", "[conversational] 这词太实用了。咱们平时上班最怕啥？隔壁组平时一声不吭，一到大老板周会，突然当众把一个大锅甩你头上。", gap=0.04),
        _dlg("v2_037", "act3_roast", "host_xiaowei", "[conversational] 对，这时候千万别急眼结巴，稳稳看他一眼说一句：I'm a bit blindsided here. 这事我事先完全没听说。既体面，又当场告诉老板，是他在搞偷袭。", lang="zh-en", gap=0.05),
        _dlg("v2_038", "act3_roast", "guest_huaiyuan", "[conversational] 这招够稳。那纳德拉后面那句 Not on my watch，翻成咱们的话就是“有我在，门儿都没有”吧？", lang="zh-en", gap=0.04),
        _dlg("v2_039", "act3_roast", "host_xiaowei", "[conversational] 没错，watch 是值班看守的意思。Not on my watch 就是只要我还在岗一天，这种事休想发生。说完这句，纳德拉周日半夜干了件直接写进商学院教材的操作。", lang="zh-en", gap=0.04),
        _dlg("v2_040", "act3_roast", "guest_huaiyuan", "[conversational] 怎么干的，派律师团去告董事会？", gap=0.03),
        _dlg("v2_041", "act3_roast", "host_xiaowei", "[conversational] 告太慢了。纳德拉直接发推特官宣，奥特曼来微软，专门给你新开个部门，而且你原来公司那七百多号兄弟，谁愿意一起跳槽，微软全盘接收、薪水照旧。", gap=-0.04),
        _dlg("v2_042", "act3_roast", "guest_huaiyuan", "[chuckles] 这招是真狠，直接端老窝啊。董事会手里留着个空壳公章，活人全让微软打包带走了。", gap=0.05),
        _dlg("v2_043", "act3_roast", "host_xiaowei", "[conversational] 不到十二个小时，OpenAI 七百七十名员工里，超过七百个人签了联名信，连当初投票开除奥特曼的伊利亚自己都反水签名了。来听这记终极反杀。", lang="zh-en", gap=0.12),

        # ==================== ACT 4: 700 MUTINY + LEVERAGE / WALK AWAY ====================
        _sfx("v2_044", "act4_scene", "tweet_post_and_buzz", m["tweet_post_and_buzz"].sfx_prompt, 2.4, gap=0.08, note="键盘敲击+办公区沸腾"),
        _dlg("v2_045", "act4_scene", "exec_female", "[urgent] Seven hundred people signed. We're backing you, Sam.", lang="en", space="boardroom", gap=0.12, sub_zh="七百人签了联名信，我们站你这边，萨姆。"),
        _dlg("v2_046", "act4_scene", "sam_altman", "[firmly] We have the leverage. Step down, or we walk away.", lang="en", space="boardroom", gap=0.18, sub_zh="底牌在我们手里。你们下台，不然我们全部走人。"),
        _dlg("v2_047", "act4_scene", "board_ilya", "[sighs] [softly] Fine. Let's talk terms.", lang="en", space="boardroom", gap=0.16, sub_zh="好吧，我们来谈条件。"),
        _dlg("v2_048", "act4_scene", "sam_altman", "[confident] We're back in business.", lang="en", space="boardroom", gap=0.16, sub_zh="我们杀回来了。"),
        _sfx("v2_049", "act4_scene", "record_scratch_freeze", m["record_scratch_freeze"].sfx_prompt, 1.0, gap=0.06),

        # Final Calm Roast & Takeaway #4
        _dlg("v2_050", "act4_roast", "guest_huaiyuan", "[conversational] 短短五天，被开除的老板不仅回来了，还顺手把开除他的董事会全换了一遍。奥特曼刚才那句 We have the leverage 确实硬气。", lang="zh-en", gap=0.04),
        _dlg("v2_051", "act4_roast", "host_xiaowei", "[conversational] 好多人以为 leverage 只是炒股加杠杆，其实欧美职场天天用它指谈判底牌和筹码。七百个顶尖工程师给你撑腰，微软兜底给 offer，这就叫 We have the leverage，底牌全在我手里。", lang="zh-en", gap=0.04),
        _dlg("v2_052", "act4_roast", "guest_huaiyuan", "[conversational] 后面那个 walk away 一听就懂，掀桌子走人。说句大实话，不管是谈融资还是普通人跟老板谈涨薪，你得先攒出能随时 walk away 的底气，别人才能坐下来跟你 be candid 说真话。", lang="zh-en", gap=0.08),
        _dlg("v2_053", "act4_roast", "host_xiaowei", "[conversational] 咱不贪多，最后花一分钟，让今天这三位大佬各自用自己的原声，把四句最值钱的职场短狠英文慢速一遍、原速一遍带你跟读，明天开会直接用。", gap=0.18),

        # ==================== ACT 5: 90s 4-PHRASE SHADOWING CARD (100% EXACT CHARACTER VOICES!) ====================
        # Phrase 1: Let's be candid. -> Ilya Sutskever (`board_ilya`, authentic Russian-Canadian accent!)
        _dlg("v2_054", "act5_card", "host_xiaowei", "[conversational] 第一句，伊利亚在开除会上用的词，摊牌说亮话：Let's be candid.", lang="zh-en", space="studio_warm", gap=0.18),
        _dlg("v2_055", "act5_card", "board_ilya", "[measured] Let's be candid.", lang="en", space="studio_warm", rate=0.85, gap=0.45, sub_zh="（伊利亚原声 0.85x 慢速）咱敞开说亮话吧。"),
        _dlg("v2_056", "act5_card", "board_ilya", "[measured] Let's be candid.", lang="en", space="studio_warm", rate=1.00, gap=1.60, sub_zh="（伊利亚原声跟读）咱敞开说亮话吧。"),

        # Phrase 2: We were completely blindsided. -> Satya Nadella (`satya_nadella`, authentic Indian-exec accent!)
        _dlg("v2_057", "act5_card", "host_xiaowei", "[conversational] 第二句，微软纳德拉被背刺时的原话，打了个措手不及：We were completely blindsided.", lang="zh-en", space="studio_warm", gap=0.18),
        _dlg("v2_058", "act5_card", "satya_nadella", "[firmly] We were completely blindsided.", lang="en", space="studio_warm", rate=0.85, gap=0.45, sub_zh="（纳德拉原声 0.85x 慢速）我们彻底被打了个措手不及。"),
        _dlg("v2_059", "act5_card", "satya_nadella", "[firmly] We were completely blindsided.", lang="en", space="studio_warm", rate=1.00, gap=1.60, sub_zh="（纳德拉原声跟读）我们彻底被打了个措手不及。"),

        # Phrase 3: Not on my watch. -> Satya Nadella (`satya_nadella`, authentic Indian-exec accent!)
        _dlg("v2_060", "act5_card", "host_xiaowei", "[conversational] 第三句，还是纳德拉的狠话，有我在休想：Not on my watch.", lang="zh-en", space="studio_warm", gap=0.18),
        _dlg("v2_061", "act5_card", "satya_nadella", "[firmly] Not on my watch.", lang="en", space="studio_warm", rate=0.85, gap=0.45, sub_zh="（纳德拉原声 0.85x 慢速）有我在，休想。"),
        _dlg("v2_062", "act5_card", "satya_nadella", "[firmly] Not on my watch.", lang="en", space="studio_warm", rate=1.00, gap=1.60, sub_zh="（纳德拉原声跟读）有我在，休想。"),

        # Phrase 4: We have the leverage. -> Sam Altman (`sam_altman`, authentic Sam Altman voice!)
        _dlg("v2_063", "act5_card", "host_xiaowei", "[conversational] 第四句，奥特曼绝地反杀的底气，底牌在我们手里：We have the leverage.", lang="zh-en", space="studio_warm", gap=0.18),
        _dlg("v2_064", "act5_card", "sam_altman", "[firmly] We have the leverage.", lang="en", space="studio_warm", rate=0.85, gap=0.45, sub_zh="（奥特曼原声 0.85x 慢速）底牌在我们手里。"),
        _dlg("v2_065", "act5_card", "sam_altman", "[firmly] We have the leverage.", lang="en", space="studio_warm", rate=1.00, gap=1.60, sub_zh="（奥特曼原声跟读）底牌在我们手里。"),

        # Crisp 10-second Next-Episode Hook
        _dlg("v2_066", "act5_card", "guest_huaiyuan", "[conversational] 四句全记住了吧。下期大瓜更有意思，二零一八年马斯克睡在工厂地板上，为什么半夜抡起钳子，亲手把花十亿美元买来的全自动产线拆了个稀巴烂？", gap=0.04),
        _dlg("v2_067", "act5_card", "host_xiaowei", "[conversational] 下期《马斯克午夜拆厂》，教你用最直接的硅谷英文把老板的蠢需求当场砍掉。点个订阅，咱们下期见。", gap=0.60),
    ]

    return EpisodeCueSheet(
        episode_id="V2_E001",
        chapter_number=1,
        title="第 1 集（V2.1精修版）：OpenAI 政变 72 小时——一条 15 分钟视频会，怎么差点拆了全球最贵 AI 巨头？",
        mode="podcast_roundtable",
        source_chapter_file="OpenAI_Nov2023_Coup_72h_Real_Business_Drama",
        head_pad_s=0.20,
        tail_pad_s=1.00,
        acts=acts,
        cues=cues,
    )


def main() -> int:
    META_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    reg = build_registry()
    reg_path = META_DIR / "voice_casting_registry.json"
    reg.save(reg_path)

    cue_sheet = build_v2_pilot_cue_sheet(reg)
    errors = cue_sheet.validate(reg)
    if errors:
        raise SystemExit("Validation failed:\n" + "\n".join(errors))

    # Verify V2 hard rules: every pure EN line <= 10 words
    en_lines = []
    zh_chars = 0
    en_words = 0
    for c in cue_sheet.cues:
        if c.kind != "dialogue":
            continue
        _, spoken = extract_tags_and_spoken_text(c.text)
        cjk = len(re.findall(r"[\u4e00-\u9fff]", spoken))
        eng = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", spoken)
        zh_chars += cjk
        en_words += len(eng)
        if c.language_code == "en":
            en_lines.append((c.cue_id, len(eng), spoken))
            if len(eng) > 10:
                raise SystemExit(f"V2 Hard Rule Violation: {c.cue_id} has {len(eng)} words (>10): {spoken}")

    zh_time_est = zh_chars / (3.8 * HOST_PACE)
    en_time_est = en_words / 2.5
    en_pct = 100.0 * en_time_est / max(1.0, zh_time_est + en_time_est)
    total_est_s = zh_time_est + en_time_est + sum(max(0.0, c.gap_after_s) + (c.duration_seconds if c.kind == "sfx" else 0.0) for c in cue_sheet.cues)

    json_path = SCRIPTS_OUT_DIR / "V2_E001_OpenAI政变72小时_商战大瓜英语剧场.json"
    md_path = SCRIPTS_OUT_DIR / "V2_E001_OpenAI政变72小时_商战大瓜英语剧场.md"
    cue_sheet.save(json_path)
    md_path.write_text(export_cue_sheet_markdown(cue_sheet, reg), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "registry": str(reg_path),
        "cue_sheet_json": str(json_path),
        "cue_sheet_md": str(md_path),
        "dialogue_cues": sum(1 for c in cue_sheet.cues if c.kind == "dialogue"),
        "sfx_cues": sum(1 for c in cue_sheet.cues if c.kind == "sfx"),
        "pure_en_lines": len(en_lines),
        "max_en_words_per_line": max(n for _, n, _ in en_lines),
        "zh_chars": zh_chars,
        "en_words": en_words,
        "host_pace": HOST_PACE,
        "est_en_speech_pct": round(en_pct, 1),
        "est_zh_speech_pct": round(100.0 - en_pct, 1),
        "est_runtime_min": round(total_est_s / 60.0, 2),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
