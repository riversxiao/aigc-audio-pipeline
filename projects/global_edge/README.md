# 《跨境底牌：硅深暗战》/ *Global Edge* — 双语商战广播剧旗舰工程

> **零外部 API 成本声明**：本项目全链路坚守 **100% Colab 96GB 开源满血管线**（**`$0` 商业 TTS/SFX/BGM API 调用**）——采用 `fishaudio/drama-3`（35B MoE）+ 全真人录音棚英美中干声锚点（`v2_real_human_studio`，44.1kHz mono `-16 LUFS`，0% 合成 `edge-tts`）+ `MOSS-SoundEffect-v2.0` + `ACE-Step 1.5 XL` + 本地 `faster-whisper` 双脚本 QA + FFmpeg 48kHz 立体声 `-16 LUFS` 三总线母带混音（含保音高 `atempo=0.800` 慢拆与半余弦同传叠音压混）。

---

## 一、 节目定位与核心架构

- **独立商战 IP（音频版《继承之战》×《硅谷》）**：以深圳南山智造 × 硅谷沙丘路 VC × 伦敦牛津街大渠道 × 东南亚供应链为舞台，讲述 AI 消费硬件独角兽 **NovaEdge Technologies（灵犀智造）** 出海突围第一季 24 集连续剧。完全去“短视频解说/英文课堂”味，只吸收 100 条真实高热商业语料中的高频高管表达与底层商业算术。
- **黄金通勤结构（`10–14 min` / 集）**：
  - **Acts 1–4（`8–10 min`）**：跨国公开谈判/董事会 100% 飙地道高管英文（`150–185 WPM`），私下深圳连线或潜台词切自然中文，零教科书味。
  - **Act 5（`~3 min`）**：独立高管黑话拆局（中式直译陷阱 vs 高管原话杀招 + `0.80x` 保音高 `atempo` 慢拆 + `1.0x` 原速 `>= 2.0s` 静音留白跟读）。
- **口音矩阵（96% 核心英美 + 4% 精控客串）**：常驻核心角色（林沉、Victoria Vance、Alistair Finch、Claire Sterling）100% 锁定硅谷/纽约标准美音与伦敦 RP 英音（**E001 为 100% 纯英美核心口音**），仅在 E011 / E013 / E016 引入清晰可控的国际客串（印度裔采购、新加坡主权基金、欧盟法务）。

---

## 二、 项目目录地图

```text
projects/global_edge/
├── README.md                                                     # 本文件：工程总览与标准命令行手册
├── 00_节目圣经与第一季24集总纲/
│   ├── RESEARCH_REPORT.md                                        # 五大支柱前期调研报告（市场/受众/竞品/百条语料/语音心理学）
│   ├── SHOW_BIBLE.md                                             # 节目总圣经（世界观、财务账本、角色档案、声场与 5 首 OST）
│   ├── ACCENT_AND_PROSODY_MANUAL.md                              # 口音韵律手册（Drama 3 合法标签、连读拆解、0.80x 与 G1–G8 门禁）
│   ├── SEASON1_24EP_BLUEPRINT.md                                 # 第一季 24 集四大弧光完整分集大纲
│   ├── season1_24ep_map.json                                     # 100/100 语料双射映射表（0 重复、0 遗漏）
│   ├── voice_casting_registry.json                               # 8 角色锁定声纹与 7 条 FOLEY 音效总表（domain=business_english_drama）
│   ├── anchor_sources.json                                       # 真人录音棚声纹源清单（v2_real_human_studio）
│   └── VOICE_ANCHOR_ACQUISITION_SPEC.md                          # 声纹采集与降噪验收规范
├── 01_视频号语料与商业词库/
│   ├── corpus_100_structured.json                                # 100 条真实商业语料清洗结构化库（含 ASR 纠偏与 WPM）
│   ├── executive_lexicon.json                                    # 120 条核验高管商业词库（96 条 corpus + 24 条 world_bridge）
│   └── CORPUS_INTELLIGENCE_REPORT.md                             # 语料定量分析报告
├── 02_分集广播剧台本/
│   ├── AUDITION_GLOBAL_EDGE_全口音与双语飙戏试听包.{json,md}        # 8 角色全口音 + G1–G8 全门禁试听包（15 Cues）
│   ├── E001_VA_HBO纯飙戏冷峻商战版_完整双语台本.{json,md}          # 变体 A：纯飙戏冷峻商战（EN ~72%、0 冻帧、林沉独白拆局）
│   ├── E001_VB_纸牌屋冻帧潜台词狙击版_完整双语台本.{json,md}        # 变体 B：8 次冻帧潜台词（EN ~55%、林沉+周默后座双人拆局）
│   ├── E001_VC_三时区惊悚推进与实战跟读版_完整双语台本.{json,md}     # 变体 C：三时区跨洋电话连切（EN ~59%、反派原声盲打实战）
│   ├── E001_VD_纪实同传叠音混合版_完整双语台本.{json,md}           # 变体 D：4 组同传叠音压混（EN ~56%、闪卡 + 30s E002 预告）
│   └── E001_COMPARATIVE_EVAL_RUBRIC.md                           # 实时量化对比矩阵 + 100 分盲听评分表 + 混合胜出者合成法则
├── 03_全平台分发与切片方案/
│   ├── LAUNCH_KIT_AND_E001_45S_CLIPS.md                          # 小宇宙/喜马拉雅/微信听书发行包 + 4 支 38–55s 爆款切片脚本
│   └── E001_BILINGUAL_COMPANION_MANUAL.md                        # Tier 1 付费精读样章（8 组核心表达 + 5 彩蛋 + 逐字节语料溯源）
└── scripts/
    ├── extract_100_clips_corpus.py                               # 100 条语料确定性 ETL
    ├── ost_and_motifs.py                                         # 5 首 ACE-Step OST 与 7 条 MOSS Foley（与圣经/注册表 1:1 同步）
    ├── drama_helpers.py                                          # 确定性台本构造器、双语时长估算器与自动化质检 Linter
    ├── ep001_va_hbo_duel.py                                      # E001_VA 编译器
    ├── ep001_vb_hoc_sniper.py                                    # E001_VB 编译器
    ├── ep001_vc_thriller_drill.py                                # E001_VC 编译器
    ├── ep001_vd_doc_duck.py                                      # E001_VD 编译器
    ├── build_e001_variants.py                                    # 一键编译、全量质检并实时生成对比评测矩阵
    └── export_drama3_bundle.py                                   # 导出 Colab 96GB 一键推理压缩包
```

---

## 三、 E001 四变体赛马实验与 100 分盲听工作流

为在量产 `E002–E024` 前找到留存与学习效果最优的工业定型模板，第一集（`E001《八千万幽灵账单 / The $80M Phantom》`）在**完全锁死同一核心剧情、同一 5 角色（100% 美音 + 伦敦 RP）、同一 5 条种子语料、同一 8 组（13 条）强制高管表达与约 11 分 38 秒一致总时长**的前提下，独立编写了 4 套零克隆的风格变体：

| 变体 ID | 风格定位 | 正片 EN 占比 | 核心听觉差异化机制 | Act 5 拆局形态 | 45s 爆款切片区间 |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **`E001_VA`** | **HBO 纯飙戏冷峻商战版** | `~72%` | `0` 冻帧独白、9 次董事会负间隔抢话、纯靠深圳私下通话切中文 | 林沉单人贴麦 4 组 `0.80x -> 1.0x` 跟读 | `va_005 .. va_010` (`51.20s`) |
| **`E001_VB`** | **纸牌屋冻帧潜台词狙击版** | `~55%` | 8 次 `freeze_frame_sub_drop` 抽真空 + 贴麦中文第四面墙拆解 | 林沉 + 周默回程后座双人拆局 | `vb_023 .. vb_028` (`42.96s`) |
| **`E001_VC`** | **三时区惊悚推进与实战跟读版** | `~59%` | 深圳 01:47 × 硅谷 09:47 × 伦敦 17:47（13 次 `phone_call` + 14 条 SFX） | 反派原声 2.8s 盲打模拟 + 4 组慢拆 | `vc_035 .. vc_040` (`43.79s`) |
| **`E001_VD`** | **纪实同传叠音混合版** | `~56%` | 4 组 `duck_under_next=True`（3.6–4.0s 原声独奏 → `0.15` 压混叠中文） | 极速四连闪卡 + 32s E002 预告 | `vd_020 .. vd_024` (`44.61s`) |

**盲听选型流程**：先跑通 `AUDITION_GLOBAL_EDGE` 通过 G1–G8 声纹/声场/慢拆/响度门禁 → 批量渲染 4 支 E001 变体 MP3 → 随机匿名重命名为 `Track_01`～`Track_04` → 按 [`E001_COMPARATIVE_EVAL_RUBRIC.md`](02_分集广播剧台本/E001_COMPARATIVE_EVAL_RUBRIC.md) 完成 **100 分盲听打分 + 24 小时无提示回忆检验** → 按 **Hybrid-Winner 法则**（#1 定骨架，至多吸收 #2/#3 最多 2 项模块化机制）定型 `E002–E024`。

---

## 四、 本地验证与质检命令（零 GPU 即可 100% 跑通）

所有命令均在仓库根目录 `/home/antigravity/riversxiao/aigc-audio-pipeline` 下执行：

```bash
# 1. 重新编译 AUDITION_GLOBAL_EDGE + E001_VA/VB/VC/VD（.json + .md）并动态刷新对比评分表
PYTHONPATH=src python3 projects/global_edge/scripts/build_e001_variants.py

# 2. 纯内存全量质检（零文件写入，输出 JSON 质检报告；全部通过退出码 0）
PYTHONPATH=src python3 projects/global_edge/scripts/build_e001_variants.py --check-only

# 3. 使用官方 CLI 严格校验台本 Schema 与锁定声纹
PYTHONPATH=src python3 -m aigc_audio_pipeline.cli validate \
  --registry projects/global_edge/00_节目圣经与第一季24集总纲/voice_casting_registry.json \
  --cue-sheet projects/global_edge/02_分集广播剧台本/E001_VA_HBO纯飙戏冷峻商战版_完整双语台本.json \
  --require-locked-voices

# 4. 预览 Drama 3 提示词转换（务必传 --registry 激活 business_english_drama 域，确保 0 仙侠词泄露）
PYTHONPATH=src python3 -m aigc_audio_pipeline.cli preview-drama3 \
  --registry projects/global_edge/00_节目圣经与第一季24集总纲/voice_casting_registry.json \
  --cue-sheet projects/global_edge/02_分集广播剧台本/E001_VB_纸牌屋冻帧潜台词狙击版_完整双语台本.json \
  --limit 15

# 5. 本地真实 FFmpeg 三总线混音 + 0.80x 保音高拉伸 + 双行 .srt 干跑试音包
PYTHONPATH=src python3 -m aigc_audio_pipeline.cli synth-dry-test \
  --registry projects/global_edge/00_节目圣经与第一季24集总纲/voice_casting_registry.json \
  --cue-sheet projects/global_edge/02_分集广播剧台本/AUDITION_GLOBAL_EDGE_全口音与双语飙戏试听包.json \
  --output-dir /tmp/global_edge_audition_dry_test

# 6. 运行 M5 专项自动化单测及全套项目回归单测
PYTHONPATH=src python3 -m unittest tests/test_global_edge_e001_variants.py -v
PYTHONPATH=src python3 -m unittest \
  tests/test_pipeline.py \
  tests/test_bilingual_business_drama_engine.py \
  tests/test_global_edge_corpus.py \
  tests/test_global_edge_blueprint.py \
  tests/test_global_edge_colab_studio.py \
  tests/test_global_edge_e001_variants.py -v
```

---

## 五、 Colab 96GB G4 零 API 满血渲染命令（试听包 + E001 四变体一键批跑）

```bash
# 1. 准备 8 角色 v2_real_human_studio 真人录音棚干声锚点（44.1kHz mono -16 LUFS；
#    自有录音棚干声 WAV 可追加 --custom-anchors-dir <dir>，纯 CI 干跑可加 --offline-stub）
PYTHONPATH=src python3 colab_96gb/prepare_global_edge_voice_anchors.py \
  --output-dir /tmp/global_edge_anchors

# 2. 串联第 1 步真人锚点打包 Global Edge 96GB 推理包（含注册表、真人锚点、试听包与 E001_VA/VB/VC/VD 全部台本）
PYTHONPATH=src python3 projects/global_edge/scripts/export_drama3_bundle.py \
  --anchors-dir /tmp/global_edge_anchors \
  --output-dir /tmp/global_edge_96gb_studio \
  --zip

# 3. 在 Colab 96GB G4 上一键渲染试听包 + E001 全部四变体
#    （本地无 GPU 验证可追加 --offline-dry-run --output-dir /tmp/global_edge_dry_run）
PYTHONPATH=src python3 colab_96gb/launch_g4_global_edge_drama3.py \
  --episodes AUDITION,E001_VARIANTS
```
