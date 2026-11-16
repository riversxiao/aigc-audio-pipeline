# 《穿越周期的信》——巴菲特 50 年致股东信深度拆解 · 持续生产工程包

本目录收纳中英双语跨阶层商业纪实圆桌播客**《穿越周期的信》**的全套**节目制作圣经、角色声线与声效母题注册表、股东信核验英文原典库、分期圆桌演出台本（`.json` + `.md`）及全平台爆款切片分发包**。

> **零 API 成本架构承诺**：本工程专为 **Colab 96GB G4 开源满血三件套**（`fishaudio/drama-3` 35B MoE + `MOSS-SoundEffect-v2.0` + `ACE-Step 1.5 XL` + 本地 `faster-whisper` 双语质检）设计，**全程不消耗任何 ElevenLabs API 额度**。

---

## 一、 目录结构

- [`00_节目圣经与第一季12期总纲/`](00_节目圣经与第一季12期总纲/)
  - [`SEASON1_SHOW_BIBLE.md`](00_节目圣经与第一季12期总纲/SEASON1_SHOW_BIBLE.md)：`3+1` 跨阶层选角设定（许知微 / 陈怀远 / 老周 / 58岁壮年巴菲特）、“纪录片同声传译叠音法”混音规范、单集四幕结构与第一季 12 期（及后续三季全编年）完整规划。
  - [`voice_casting_registry.json`](00_节目圣经与第一季12期总纲/voice_casting_registry.json)：`domain="finance_podcast"` 机器可读角色注册表与 4 枚商业纪录片专属声效母题。
  - [`voice_anchors/`](00_节目圣经与第一季12期总纲/voice_anchors/)：**V2 全真人录音棚近讲参考干音（`v2_real_human_studio`，0% 合成 TTS）**——含 30 岁金融专业女主播（`host_zhiwei.wav`）、40 岁留美精算师男嘉宾（`guest_huaiyuan.wav`）、48 岁大陆制造业实战老兵（`guest_laozhou.wav`）与 1990 年 PBS《Adam Smith's Money World》58 岁壮年巴菲特零混响棚录干音（`buffett_prime_en.wav`）及逐字校验 `.txt`。
- [`01_股东信英文原典库/`](01_股东信英文原典库/)
  - [`2008_berkshire_shareholder_letter_excerpts.md`](01_股东信英文原典库/2008_berkshire_shareholder_letter_excerpts.md)：EP01 对应的 2008 年伯克希尔致股东信核心账面数据与 6 组（7 轨）100% 逐字核验英文原典。
- [`02_分期圆桌台本/`](02_分期圆桌台本/)
  - [`AUDITION_BUFFETT_四角色定角试听包.json`](02_分期圆桌台本/AUDITION_BUFFETT_四角色定角试听包.json) / [`.md`](02_分期圆桌台本/AUDITION_BUFFETT_四角色定角试听包.md)：8 轨 75 秒真实圆桌交锋试听包（检验四位真人锚点声线、短句抢话呼吸感、中英混说与首句独奏同传压混）。
  - [`E001_2008年致股东信_满地是血的夜晚谁在裸泳_完整圆桌台本.json`](02_分期圆桌台本/E001_2008年致股东信_满地是血的夜晚谁在裸泳_完整圆桌台本.json) / [`.md`](02_分期圆桌台本/E001_2008年致股东信_满地是血的夜晚谁在裸泳_完整圆桌台本.md)：V2 去 AI 味完整圆桌台本（79 轨：71 轨短句交锋对话 + 8 轨纪实声效，零寒暄互捧、零播音腔前缀，含壮年巴菲特原声独奏/同传双编排）。
- [`03_全平台分发与切片方案/`](03_全平台分发与切片方案/)
  - [`E001_2008_爆款标题与3条短视频高光切片方案.md`](03_全平台分发与切片方案/E001_2008_爆款标题与3条短视频高光切片方案.md)：小宇宙/喜马拉雅/B站标题包、完整时间轴 Shownotes 与 3 条抖音/视频号竖屏切片脚本。
- [`scripts/`](scripts/)
  - [`ost_and_motifs.py`](scripts/ost_and_motifs.py)：美式指弹木吉他、室内乐大提琴与深夜书房毛毡钢琴纯器乐配乐母带词表（跨集自动命中 SHA-256 缓存）。
  - [`build_s01e01_2008.py`](scripts/build_s01e01_2008.py)：V2 试听包与 EP01 台本确定性编译与强校验脚本。

---

## 二、 快速命令参考

### 1. 本地重编译、强校验与全套单元测试（零 GPU / 零 API）
```bash
# 重新编译 V2 试听包与 EP01 台本
PYTHONPATH=src python3 projects/buffett_letters/scripts/build_s01e01_2008.py

# 运行全套 20 项回归与 V2 去播音腔/抢话字幕防重叠测试
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

### 2. Colab 96GB G4 一键合成 V2 试听包 + EP01 双语母带
```bash
# 在挂载了 Google Drive 的 Colab 96GB G4 实例上运行（自动加载 bundled 真人录音棚干音锚点并复用云盘已缓存的 SFX/BGM）：
python3 colab_96gb/launch_g4_buffett_drama3.py --episodes AUDITION_BUFFETT,E001 --mirror-to-main-masters
```
