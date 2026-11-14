#!/usr/bin/env python3
"""Initialize `voice_casting_registry.json` and `production_progress_ledger.json` for 《逆模因部》."""

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from aigc_audio_pipeline.models import SonicMotif, VoiceCastingRegistry, VoiceProfile, utc_now_iso

PROJECT_DIR = REPO_ROOT / "projects" / "antimemetics_division"
LEDGER_DIR = PROJECT_DIR / "00_声音选角档案与进度台账"


def build_antimemetics_registry() -> VoiceCastingRegistry:
    roles = {
        "narrator": VoiceProfile(
            role_id="narrator",
            display_name="旁白",
            aliases=["叙述", "画外音"],
            tier="narrator",
            gender="male",
            age_group="middle_aged",
            vocal_register="冷峻克制、极具硬核科幻悬疑电影质感的大陆男中音；平叙如精密仪器，概念崩塌与高维巨物降临时爆发刺骨压迫感",
            persona_summary="《逆模因部》全剧科幻悬疑主视角，冷冽展现信息吞噬、记忆断层与基金会逆模因战争",
            status="locked",
            voice_id="LFGpHeEhtShcrG0IJ1b4",
            library_voice_name="逆模因部_旁白_冷峻科幻悬疑男中音",
            default_stability=0.5,
            signature_tags=["[calmly]", "[softly]", "[dramatically]", "[whispers]"],
            forbidden_habits=["禁止晚会朗诵腔", "禁止轻浮播报腔"],
            first_appearance_chapter=1,
            appearance_chapters=[1, 2, 3, 4, 5, 6],
            audition_line="[calmly] 你该如何收容一个你既无法记录、也无法记住的东西？欢迎来到逆模因部。不，今天不是你第一天上班。",
        ),
        "db_terminal": VoiceProfile(
            role_id="db_terminal",
            display_name="基金会终端",
            aliases=["数据库终端", "SCiPNET", "机密档案"],
            tier="recurring",
            gender="male",
            age_group="middle_aged",
            vocal_register="绝对冰冷、零情绪波动的SCP基金会五级机密档案终端播报男中低音（配合 mental_realm 声场）",
            persona_summary="播报 SCP-055、SCP-4739、SCP-3125 及化学记忆强化剂指南等机密数据库词条",
            status="locked",
            voice_id="vBK1ICucZ4f5G7wjYUBd",
            library_voice_name="WangSong (Mainland Studio Terminal Anchor)",
            default_stability=1.0,
            signature_tags=["[calmly]", "[coldly]"],
            forbidden_habits=["严禁带入人类情绪起伏"],
            first_appearance_chapter=1,
            appearance_chapters=[1, 3, 4, 5],
            audition_line="项目编号：SCP-055。项目等级：Keter。特殊收容措施：任何情况下严禁在收容室外安排安保警卫。",
        ),
        "marion_wheeler": VoiceProfile(
            role_id="marion_wheeler",
            display_name="玛丽安·惠勒",
            aliases=["玛丽安", "惠勒", "惠勒部长", "玛丽安·哈钦森"],
            tier="protagonist",
            gender="female",
            age_group="middle_aged",
            vocal_register="成熟磁性、干练冷厉、锋芒内敛的四十九岁女部长御姐声线；平时极度镇定犀利，绝境下兼具钢铁意志与悲怆破碎感",
            persona_summary="SCP基金会逆模因部部长（女一号），凭头脑与生化记忆强化剂在必败的高维概念战争中孤身死战到底",
            status="locked",
            voice_id="lreFqOKRKWFzRiYosSD9",
            library_voice_name="逆模因部_玛丽安惠勒_冷厉干练女部长",
            default_stability=0.5,
            signature_tags=["[calmly]", "[coldly]", "[sarcastic]", "[whispers]", "[hoarsely]"],
            forbidden_habits=["严禁演成稚嫩少女或歇斯底里泼妇"],
            first_appearance_chapter=2,
            appearance_chapters=[2, 3, 4, 5, 6],
            audition_line="[coldly] 你这蠢货，我是你们的逆模因部部长。 [whispers] 这世上根本就没有逆模因部。",
        ),
        "paul_kim": VoiceProfile(
            role_id="paul_kim",
            display_name="保罗·金",
            aliases=["金", "初级研究员金", "非金"],
            tier="protagonist",
            gender="male",
            age_group="young",
            vocal_register="清冷敏锐、思维极快且富有戏剧爆发力的青年研究员男声；后期被3125夺舍后转为麻木冰冷的非人语调",
            persona_summary="逆模因部核心研究员，曾用网线编成流星锤单杀SCP-4739，后在3125收容失效中遭概念夺舍",
            status="locked",
            voice_id="yMY8ojQH9HrvDUfScAa9",
            library_voice_name="逆模因部_保罗金_敏锐青年研究员",
            default_stability=0.5,
            signature_tags=["[calmly]", "[rushed]", "[desperately]", "[shouting]", "[coldly]"],
            forbidden_habits=["禁止轻佻油腻"],
            first_appearance_chapter=3,
            appearance_chapters=[3, 5, 6],
            audition_line="[rushed] 手机是一块塞满信息的实心砖头！在我之前，从来没有人试过把信息当成投射武器砸过去！",
        ),
        "o5_8": VoiceProfile(
            role_id="o5_8",
            display_name="O5-8",
            aliases=["布伦特", "监督者"],
            tier="core_supporting",
            gender="male",
            age_group="middle_aged",
            vocal_register="醇厚威严、城府极深、泰山崩于前而色不变的基金会最高议会监督者男低音",
            persona_summary="SCP基金会O5议会第八席（布伦特），漏服W级记忆强化剂后传讯玛丽安，目睹寄生助手被击毙仍面不改色",
            status="locked",
            voice_id="Alm4bKh9IhYI6Js4fmFB",
            library_voice_name="逆模因部_O5之8_威严深沉监督者",
            default_stability=0.5,
            signature_tags=["[calmly]", "[coldly]", "[sighs]"],
            forbidden_habits=["禁止大惊小怪失态"],
            first_appearance_chapter=2,
            appearance_chapters=[2],
            audition_line="[calmly] 那是克莱的枪。你从他身上偷走的。那么告诉我，这些药片有什么副作用吗？",
        ),
        "clay": VoiceProfile(
            role_id="clay",
            display_name="克莱",
            aliases=["年轻助手", "助理"],
            tier="antagonist",
            gender="male",
            age_group="young",
            vocal_register="清亮紧绷、警觉多疑的二十多岁年轻男助理声线",
            persona_summary="潜伏在O5-8身边伪装成行政助理的人形逆模因实体，阻断O5服药，被玛丽安识破后三枪击毙",
            status="locked",
            voice_id="5s3UifUu3OJ90z17rRMA",
            library_voice_name="Jun (Mainland Studio Young Male)",
            default_stability=0.0,
            signature_tags=["[coldly]", "[dismissive]", "[gasps]"],
            forbidden_habits=["严禁外语飘口音"],
            first_appearance_chapter=2,
            appearance_chapters=[2],
            audition_line="[dismissive] 我们根本没有逆模因部。也没有什么SCP-055，那套编号从来就没分配过。",
        ),
        "receptionist_npc": VoiceProfile(
            role_id="receptionist_npc",
            display_name="前台女职员",
            aliases=["女前台"],
            tier="recurring",
            gender="female",
            age_group="young",
            vocal_register="清冽干练、带几分职业克制与困惑的行政总部年轻女职员声线",
            persona_summary="两百号站点行政大楼前台接待员，一再提醒玛丽安大楼内严禁吸烟",
            status="locked",
            voice_id="5txYoyqgH78h22OKoJVP",
            library_voice_name="逆模因部_前台女职员_清冽干练女声",
            default_stability=0.5,
            signature_tags=["[calmly]", "[dismissive]"],
            forbidden_habits=["禁止夸张搞笑"],
            first_appearance_chapter=2,
            appearance_chapters=[2],
            audition_line="[calmly] 不行，两百号站点任何地方都不准抽烟。这过去的十五分钟里你已经问过我两次了。",
        ),
        "alastair_grey": VoiceProfile(
            role_id="alastair_grey",
            display_name="阿拉斯泰尔·格雷",
            aliases=["格雷", "SCP-4739"],
            tier="antagonist",
            gender="male",
            age_group="middle_aged",
            vocal_register="温文尔雅、吐字考究却毫无人类温度的灰西装高管捕食者男声；永远面带微笑吞噬受害者全部记忆",
            persona_summary="SCP-4739慢速逆模因抹杀媒介，专挑博学复杂的基金会研究员下手，将其隔绝于现实之外蚕食殆尽",
            status="locked",
            voice_id="WX7zQiwvnb3yk5qplrqL",
            library_voice_name="逆模因部_格雷_温文毛骨悚然捕食者",
            default_stability=0.0,
            signature_tags=["[calmly]", "[condescending]", "[softly]", "[sarcastic]"],
            forbidden_habits=["严禁咆哮怒吼，越优雅礼貌越显恐怖"],
            first_appearance_chapter=3,
            appearance_chapters=[3],
            audition_line="[calmly] 第一天上班够呛吧？我叫阿拉斯泰尔·格雷。你曾经会说四门语言，现在只剩一门，很快就会归零。",
        ),
        "lyn_marness": VoiceProfile(
            role_id="lyn_marness",
            display_name="林·马内斯",
            aliases=["马内斯", "马内斯博士", "艾尔"],
            tier="core_supporting",
            gender="male",
            age_group="old",
            vocal_register="沧桑厚重、兼具九旬垂死老者沙哑气短与逆龄后老派特工铮铮铁骨的戏剧男声",
            persona_summary="二战美军“不可思议小队”元老及1976年基金会逆模因部创始人，临终注射X级血清揭开SCP-3125宿命闭环",
            status="locked",
            voice_id="GwFDftWWl0cM0vklLlbt",
            library_voice_name="逆模因部_林马内斯_沧桑初代创始人",
            default_stability=0.0,
            signature_tags=["[hoarsely]", "[calmly]", "[whispers]", "[shouting]", "[desperately]"],
            forbidden_habits=["严禁假捏尖嗓老年音"],
            first_appearance_chapter=4,
            appearance_chapters=[4],
            audition_line="[whispers] 如果你知道它存在，它就知道你存在。你一整个下午都在直勾勾地盯着它看！",
        ),
        "bart_hughes": VoiceProfile(
            role_id="bart_hughes",
            display_name="巴特·休斯",
            aliases=["休斯博士", "巴塞洛缪·休斯"],
            tier="core_supporting",
            gender="male",
            age_group="young",
            vocal_register="聪慧机敏、充满好奇心与学者敏锐度的青年研究员男声",
            persona_summary="逆模因部传奇收容架构师，《SCP-055》档案执笔人与3125逆向收容室设计者",
            status="locked",
            voice_id="lkK6X9yp6sIA3vecwS2p",
            library_voice_name="Hou Xiaohou (Mainland Studio Researcher)",
            default_stability=0.5,
            signature_tags=["[calmly]", "[excited]"],
            forbidden_habits=["严禁油滑腔调"],
            first_appearance_chapter=1,
            appearance_chapters=[1],
            audition_line="[calmly] 等等，如果我们一直记录它不是什么，会怎么样？那些否定事实我们总能记住吧？",
        ),
        "subject_055": VoiceProfile(
            role_id="subject_055",
            display_name="受试研究员",
            aliases=["调查员", "被感染男特工"],
            tier="recurring",
            gender="male",
            age_group="middle_aged",
            vocal_register="恍惚迷茫、精神紧绷的中年男性职员声线",
            persona_summary="演绎第1章刚走出055收容间失忆恍惚的受试者，以及第6章被3125感染的空壳男特工",
            status="locked",
            voice_id="33zIzrLo9ZcbbVBQyuAA",
            library_voice_name="逆模因部_受试研究员_恍惚中年男声",
            default_stability=0.0,
            signature_tags=["[trembling]", "[calmly]", "[coldly]"],
            forbidden_habits=["严禁外语口音"],
            first_appearance_chapter=1,
            appearance_chapters=[1, 6],
            audition_line="[trembling] 我不知道那是什么，但我知道里头肯定有个你记不住的东西，而且它绝对不是圆的！",
        ),
        "scp_3125_voice": VoiceProfile(
            role_id="scp_3125_voice",
            display_name="SCP-3125",
            aliases=["五维幻听", "逃逸恶神"],
            tier="antagonist",
            gender="male",
            age_group="middle_aged",
            vocal_register="阴森低哑、带着五维概念俯视与残酷嘲弄的非人低频幻听声线（配合 mental_realm）",
            persona_summary="第6章玛丽安在Z级记忆强化剂极限过载下听见的SCP-3125高维意识投射",
            status="locked",
            voice_id="azKtUp81mLUKHHE3BOA0",
            library_voice_name="逆模因部_SCP3125_高维恶意低语",
            default_stability=0.0,
            signature_tags=["[coldly]", "[sarcastic]", "[hoarsely]"],
            forbidden_habits=["禁止演成普通人类混混"],
            first_appearance_chapter=6,
            appearance_chapters=[6],
            audition_line="[sarcastic] 战争已经结束了，玛丽安！只剩你一个人，一个人的逆模因部，面对一个不死不灭的观念。",
        ),
        "infected_female": VoiceProfile(
            role_id="infected_female",
            display_name="受感染女特工",
            aliases=["空壳女特工"],
            tier="recurring",
            gender="female",
            age_group="young",
            vocal_register="幽冷空洞、毫无人类怜悯的贴耳女声",
            persona_summary="第6章终局围拢在玛丽安身旁、已被SCP-3125抽空心智的前逆模因部女特工躯壳",
            status="locked",
            voice_id="t5SIDRTVMdbNUqrSAycs",
            library_voice_name="Linda (Mainland Studio Eerie Female)",
            default_stability=0.0,
            signature_tags=["[coldly]", "[whispers]"],
            forbidden_habits=["严禁甜美播音腔"],
            first_appearance_chapter=6,
            appearance_chapters=[6],
            audition_line="[coldly] 先从她的眼睛下手，这样她剩下的部分就更容易纠正了。",
        ),
    }

    motifs = {
        "motif_scp_terminal_boot": SonicMotif(
            motif_id="motif_scp_terminal_boot",
            name="SCiPNET五级机密终端解锁母题",
            description="调取SCP机密数据库词条时的冷冽电子握手音与微弱显像管底噪",
            sfx_prompt="Cold classified sci-fi computer terminal decryption telemetry chime followed by low CRT monitor static hum in a quiet bunker",
            duration_seconds=2.6,
            prompt_influence=0.55,
        ),
        "motif_mnestic_pill_beep": SonicMotif(
            motif_id="motif_mnestic_pill_beep",
            name="W级记忆强化剂服药提醒与铝塑掰药声",
            description="准点响起的极简电子双蜂鸣提醒音与清脆掰出药片声",
            sfx_prompt="Sharp minimalist digital wristwatch double beep reminder followed by crisp blister pack foil pop of a small pill",
            duration_seconds=2.2,
            prompt_influence=0.55,
        ),
        "motif_antimemetic_static": SonicMotif(
            motif_id="motif_antimemetic_static",
            name="逆模因认知侵蚀·脑内静电刺痛母题",
            description="记忆被吞噬或高维视线锁定时，眼球后方泛起的放射性静电刺痛与低频空洞下潜",
            sfx_prompt="Eerie high-frequency Geiger-like cognitive static prickle blending into a deep hollow sub-bass memory vacuum drop",
            duration_seconds=3.4,
            prompt_influence=0.55,
        ),
        "motif_heavy_blast_door": SonicMotif(
            motif_id="motif_heavy_blast_door",
            name="基金会重型防爆气闸门闭锁母题",
            description="防弹办公室、潜艇级舱门与3125旋转气闸门的沉重液压机械咬合声",
            sfx_prompt="Massive pneumatic steel containment airlock rotating and latching shut with heavy mechanical clunks and pressurized seal hiss",
            duration_seconds=3.8,
            prompt_influence=0.55,
        ),
        "motif_memory_wipe_pulse": SonicMotif(
            motif_id="motif_memory_wipe_pulse",
            name="逆模因湮灭·记忆归零脉冲母题",
            description="气闸清除脉冲、冰湖坠水断片与终章逆模因氢弹通电引爆瞬间的绝对归零震响",
            sfx_prompt="Piercing electromagnetic flash pulse collapsing instantly into an abyssal sub-bass thud and absolute dead silence",
            duration_seconds=3.6,
            prompt_influence=0.55,
        ),
    }

    return VoiceCastingRegistry(
        project_id="antimemetics_division",
        project_title="《逆模因部》硬核科幻悬疑多人有声剧（SCP CC-BY-SA-3.0）",
        language_code="zh",
        roles=roles,
        sonic_motifs=motifs,
    )


def build_initial_ledger() -> dict:
    episodes_meta = [
        (1, "E001", "第1章 SCP-055：未知自封机密", "scp-055"),
        (2, "E002", "第2章 我们得谈谈五十五号", "we-need-to-talk-about-fifty-five"),
        (3, "E003", "第3章 逆模因学导论", "introductory-antimemetics"),
        (4, "E004", "第4章 难以忘怀，你本如此", "unforgettable-that-s-what-you-are"),
        (5, "E005", "第5章 无色绿意案", "case-colourless-green"),
        (6, "E006", "第6章 你最后一次首日上班", "your-last-first-day"),
    ]
    return {
        "project_id": "antimemetics_division",
        "project_title": "《逆模因部》硬核科幻悬疑多人有声剧（SCP CC-BY-SA-3.0）",
        "license": "CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/)",
        "source_hub_url": "https://scp-wiki.wikidot.com/antimemetics-division-hub",
        "updated_at": utc_now_iso(),
        "drive_folders": {
            "audio_root": "",
            "00_casting_and_ledgers": "",
            "01_voice_auditions": "",
            "02_episode_scripts": "",
            "03_mastered_episodes": "",
            "04_reusable_motifs_and_stems": "",
        },
        "summary": {
            "total_planned_episodes": 6,
            "scripts_ready": 0,
            "episodes_mastered": 0,
            "voices_locked": 13,
        },
        "episodes": [
            {
                "chapter_number": ch_num,
                "episode_id": ep_id,
                "title": title,
                "scp_wiki_slug": slug,
                "scp_wiki_url": f"https://scp-wiki.wikidot.com/{slug}",
                "status": "pending_script",
                "cue_sheet_file": "",
            }
            for ch_num, ep_id, title, slug in episodes_meta
        ],
    }


def main() -> int:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    reg = build_antimemetics_registry()
    reg_path = LEDGER_DIR / "voice_casting_registry.json"
    reg.save(reg_path)

    ledger_path = LEDGER_DIR / "production_progress_ledger.json"
    if not ledger_path.exists():
        ledger_path.write_text(json.dumps(build_initial_ledger(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Saved registry ({len(reg.roles)} locked roles, {len(reg.sonic_motifs)} motifs) -> {reg_path}")
    print(f"Saved ledger -> {ledger_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
