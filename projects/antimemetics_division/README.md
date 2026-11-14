# 《逆模因部》硬核科幻悬疑多人有声剧工程（SCP Wiki V1 · CC BY-SA 3.0）

本目录是 `aigc-audio-pipeline` 针对海外硬核科幻神作 **《逆模因部》（*There Is No Antimemetics Division*，SCP Wiki 原版第一季全六章）** 的完整中文精译与电影感多人有声剧工程，与仓库内其他小说工程 100% 物理与云端隔离。

## 1. 版权与文本来源（CC BY-SA 3.0）

- **原著来源**：100% 源自 [SCP Wiki Antimemetics Division Hub](https://scp-wiki.wikidot.com/antimemetics-division-hub) 原版网页连载 V1（原作者 `qntm` 及 `CptBellman`），**绝未使用** 2025 年企鹅兰登（Penguin / Del Rey）重写商业出版物内容。
- **开源许可**：衍生中文精译底本、分集广播剧台本及有声剧音频遵循 **[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)** 协议共享（详见 [`CC_BY_SA_3.0_ATTRIBUTION.md`](./CC_BY_SA_3.0_ATTRIBUTION.md)）。

## 2. 第一季完整章节与分集台本（未删减 >= 96.5% 覆盖率）

| 集数 | 中文精译章节 (`source_chapters/`) | 原作词条 | 对白轨数 | 音效轨数 | 分幕配乐 |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **AUDITION** | 核心声优六句试听合集 | — | 6 | 0 | — |
| **E001** | `第01章_SCP-055_未知自封机密.md` | `scp-055` | 42 | 5 | 3 幕 |
| **E002** | `第02章_我们得谈谈五十五号.md` | `we-need-to-talk-about-fifty-five` | 135 | 6 | 4 幕 |
| **E003** | `第03章_逆模因学导论.md` | `introductory-antimemetics` | 110 | 7 | 4 幕 |
| **E004** | `第04章_难以忘怀，你本如此.md` | `unforgettable-that-s-what-you-are` | 124 | 8 | 4 幕 |
| **E005** | `第05章_无色绿意案.md` | `case-colourless-green` | 74 | 8 | 3 幕 |
| **E006** | `第06章_你最后一次首日上班.md` | `your-last-first-day` | 62 | 7 | 3 幕 |

## 3. 全剧 13 角色大陆戏剧配音阵容 & 5 大跨集科幻声效母题

- **核心角色（13 人）**：`narrator`（旁白）、`db_terminal`（基金会终端，`stability=1.0` + `mental_realm`）、`marion_wheeler`（玛丽安·惠勒）、`paul_kim`（保罗·金 / 非金）、`o5_8`（O5-8 布伦特）、`clay`（人形逆模因克莱）、`receptionist_npc`（两百号站点前台）、`alastair_grey`（阿拉斯泰尔·格雷 / SCP-4739）、`lyn_marness`（初代创始人林·马内斯）、`bart_hughes`（巴特·休斯）、`subject_055`（055 受试研究员 / 被感染男特工）、`scp_3125_voice`（五维恶神 SCP-3125 脑海幻听）、`infected_female`（被感染女特工）。
- **跨集复用声效母题（5 枚）**：`motif_scp_terminal_boot`（五级终端解锁）、`motif_mnestic_pill_beep`（W 级强化剂蜂鸣与掰药声）、`motif_antimemetic_static`（逆模因脑内静电刺痛）、`motif_heavy_blast_door`（重型防爆旋转气闸）、`motif_memory_wipe_pulse`（逆模因记忆归零脉冲）。

## 4. 一键编译、打包与合成指令

```bash
# 1. 从中文精译底本编译并校验全 6 集未删减有声剧台本 + 6 句试听清单
python3 projects/antimemetics_division/scripts/build_s01_e001_e006.py

# 2. 导出自包含 96GB Colab Drama 3 工程包（含 13 角色 44.1kHz -16 LUFS 干音锚点）
python3 projects/antimemetics_division/scripts/export_drama3_bundle.py

# 3A. 方式一：96GB Colab G4 零 API 成本满血合成（Fish Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL scifi_dark）
colab exec -s antimemetics96 -f colab_96gb/launch_g4_antimemetics_drama3.py

# 3B. 方式二：ElevenLabs eleven_v3 云端队列合成并自动归档 Google Drive
python3 projects/antimemetics_division/scripts/run_queue.py --from-ep 1 --to-ep 6

# 4. 将全套中文底本、台本、选角圣经与成片同步归档至 Google Drive
python3 projects/antimemetics_division/scripts/sync_to_drive.py
```
