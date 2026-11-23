# 《跨境底牌：硅深暗战》/ *Global Edge* — 96GB 真人录音棚干声锚点采集与验收规范
# Voice Anchor Acquisition, Conditioning & Audition Gate Specification (`v2_real_human_studio`)

> **工程对齐基准**：100% 对齐 `voice_casting_registry.json`（8 位锁定角色、`domain="business_english_drama"`）、`anchor_sources.json`（`anchor_schema_version="v2_real_human_studio"`）与 `ACCENT_AND_PROSODY_MANUAL.md`（85/15 口音配额与 G1–G8 试音验收门）。
> **引擎栈**：`fishaudio/drama-3`（35B MoE FP8 / INT4，`sglang-omni`）+ `OpenMOSS-Team/MOSS-SoundEffect-v2.0` + `ACE-Step/acestep-v15-xl-turbo-diffusers` + `faster-whisper-small-int8`（CPU 零显存质检）。

---

## 1. `v2_real_human_studio` 零合成红线与生产门禁策略 (Zero-`edge-tts` / Zero-Synthetic Policy)

1. **生产级铁律（0% 商业语音 API、0% 合成 TTS 污染）**：
   - `fishaudio/drama-3` 的零样本音色克隆会忠实继承参考干声的微呼吸、口腔共鸣、停顿质感与口音韵律。一旦使用任何合成 TTS（包括历史遗留的 `edge-tts`、`Neural` 合成语音或离线占位音频）作为参考锚点，成片必然出现“电子金属味”“播音腔”和跨语种音色坍塌。
   - 因此，本项目全面锁死 **`anchor_schema_version = "v2_real_human_studio"`**，**严禁在任何生产模式中使用 `edge-tts`、商业付费语音 API 或合成 `Neural` 语音**。
   - `prepare_global_edge_voice_anchors.py --offline-stub` 生成的 `offline_synthetic_stub` **仅限无 GPU CI/本地全链路干跑自检使用**，严禁进入 Colab G4 真实 GPU 渲染流程。

2. **强制代码门禁（`validate_production_voice_cast()`）**：
   - 在 `colab_96gb/launch_g4_global_edge_drama3.py` 与 `colab_96gb/run_global_edge_96gb_studio.py` 启动 `fishaudio/drama-3` 之前（所有非 `--offline-dry-run` 模式），系统自动执行 `validate_production_voice_cast()`，对以下 6 项实施强阻断校验，任意一项失败立即终止启动并给出清晰报错：
     1. `voice_cast_drama3.json` 存在且为合法 JSON 对象；
     2. 顶层 `anchor_schema_version == "v2_real_human_studio"`；
     3. 全部目标锁定角色（默认 8 位完整剧组）均存在；
     4. 每位角色的 `source_voice_name` 非空，且严格拦截任何合成/遗留标记（匹配 `edge[-_]?tts`、`neural`、`offline_synthetic_stub`、`zero_cost_studio_anchor:`、`synthetic` 均直接拒绝）；
     5. 每位角色的 `voice_anchors/<role_id>.wav` 存在、文件体积 `>= 4096 bytes`，且经 `wave.open()` 校验为合法 `44100 Hz` 单声道 16-bit PCM WAV（`nframes > 0`）；
     6. 每位角色的 `anchor_text` 逐字转录稿非空。

---

## 2. 全剧组 8 角色真人声源矩阵、85/15 口音账本与开源许可审计表

### 2.1 第一季 24 集口音配额硬指标（Accent Budget Ledger）

| 维度 | 项目硬红线 | 第一季 24 集实际锁账 | 合规状态 |
| :--- | :---: | :---: | :---: |
| **核心美音 + 伦敦 RP 英音占比** | `>= 85.0%` | **`96.0%`**（E001 四个变体严格 `100.0%`） | PASS (+11.0 pp 余量) |
| **受控国际精英客串口音占比** | `<= 15.0%` | **`4.0%`**（仅限 E011 / E013 / E016 三集） | PASS (-11.0 pp 余量) |

### 2.2 8 角色真人干声来源与许可审计总表（100% 同步 `anchor_sources.json`）

| `role_id` | 角色名 (`display_name`) | 语言 (`language_code`) | 口音代码 (`accent_code`) | 阵营 / 出场集数 | 开源真人语料来源 (`source_name`) | 开源许可 (`license`) | 目标时长 | 语速基准 |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| `lin_chen` | 林沉 / Lin Chen | `zh-en` | `zh_en_bilingual_us` | Core (`E001–E024` 全勤 + Act 5 主讲) | `OpenMOSS/MOSS-TTSD` 双语近麦干声 / 同声源真人定制棚录 | `Apache-2.0` | `14.0s` | EN `155–180 WPM` / ZH `3.55–3.65 字/秒` |
| `zhou_mo` | 周默 / Zhou Mo | `zh-en` | `zh_mainland_sz` | Core (`E001–E024` 全勤 + `E001_VB` 复盘) | `OpenMOSS/MOSS-TTSD` (`pod_m_enhanced`) / `AISHELL-3` 近麦男中音 | `Apache-2.0` | `13.0s` | ZH `3.55–3.65 字/秒` + 清晰英文术语 |
| `victoria_vance` | Victoria Vance | `en` | `us_silicon_valley` | Core (`E001` 等 12 集，沙丘路 VC) | `Hi-Fi TTS` / `LibriTTS-R` 硅谷/标准美音近麦女中低音 | `CC-BY-4.0` | `12.5s` | `165–185 WPM` |
| `alistair_finch` | Alistair Finch | `en` | `uk_london_rp` | Core (`E001` 等 10 集，伦敦零售 VP) | `CSTR VCTK v0.92` / `OpenSLR-83` 伦敦标准 RP 近麦男中低音 | `CC-BY-4.0` | `13.5s` | `145–165 WPM` |
| `claire_chen_gc` | Claire Sterling | `en` | `us_nyc` | Core (`E001` 等 12 集，纽约总法务) | `LibriTTS-R` / `Hi-Fi TTS` 纽约东海岸精英美音近麦女中音 | `CC-BY-4.0` | `12.0s` | `160–185 WPM` |
| `rajiv_menon` | Rajiv Menon | `en` | `intl_indian_exec` | Guest (`<=15%` 池，仅 `E013`) | `Mozilla Common Voice` / `OpenSLR-103` LFC 高清晰印度精英男声 | `CC0-1.0` | `12.5s` | `155–175 WPM` |
| `wei_ling_tan` | Wei-Ling Tan | `en` | `intl_singapore_vc` | Guest (`<=15%` 池，仅 `E013/E016`) | `IMDA National Speech Corpus` / `Common Voice` 新加坡外交精英女声 | `CC-BY-4.0` | `12.5s` | `150–170 WPM` |
| `henrik_lindqvist` | Henrik Lindqvist | `en` | `intl_eu_legal` | Guest (`<=15%` 池，仅 `E011`) | `VoxPopuli` / `Common Voice` 北欧布鲁塞尔法务清晰英语男声 | `CC0-1.0` | `13.0s` | `145–160 WPM` |

> **零跨口音替代与零漫画化原则**：6 位纯英文角色必须严格匹配对应 `accent_code` 的真人近麦干声，严禁用美音替代伦敦 RP，严禁在国际客串角色中出现任何喜剧化/刻板化夸张口音或市井 Singlish。

---

## 3. 主角 `lin_chen` 同声源双语克隆专项协议 (`bilingual_same_speaker_protocol`)

林沉（`lin_chen`）是全剧唯一需要在同一集内高频无缝切换 **硅谷董事会纯正美音（`en`）** 与 **《纸牌屋》式贴麦冷峻中文独白 / Act 5 片尾拆局（`zh` / `zh-en`）** 的主角。为彻底杜绝“中英割裂像两个人”或“跨语种口音互串”，必须执行以下专项协议：

1. **单一真实声道强制要求 (`single_human_speaker_required: true`)**：
   - 严禁把“美国白人配音员英文片段”与“国内配音员中文片段”硬拼给 `lin_chen`。
   - 必须由 **同一位 30–38 岁、具备真实硅谷/北美顶级职场流利美音与纯正现代大陆普通话的男性真人在同一录音棚、同一支近讲大振膜电容麦（同麦距、同增益）下录制**，确保基频 `F0`（约 `105–135 Hz`）与共振峰（Formants F1–F3）跨语种 100% 锁定。

2. **12–16 秒双语拼接锚点 vs 同声源英/中成对试听 A/B 测试**：
   - **方案 A（默认首选 · 14s 双语无缝拼接锚点 `55:45`）**：
     - 前 `7–9s`：冷峻克制的硅谷标准美音商务陈述（如 `That eighty-million-dollar loss is a phantom number—not a cash loss, and you know it.`，`155–180 WPM`，清晰卷舌 `/r/`、自然美式闪音与核重音）。
     - 中间 `0.35s` 自然呼吸气口。
     - 后 `5–7s`：同一声线自然切入贴麦冷峻中文（如 `她把可转债重估包装成经营失血，不是看不懂财报，是想趁签约前把估值砍掉三成。`，`3.55–3.65 字/秒`，胸腔低沉共鸣、零洋腔零播音腔）。
     - 优势：单一 `voice_anchors/lin_chen.wav` 即可在 `fishaudio/drama-3` 单次零样本推理中同时覆盖 `en`、`zh` 与 `zh-en` 混说台词，且缓存键 100% 统一。
   - **方案 B（同声源分语种对照验证）**：
     - 从同一位真人的同场录音中分别截取 `12s` 纯英干声与 `12s` 纯中干声，在 `AUDITION_GLOBAL_EDGE` 试听环节与方案 A 做双盲 A/B 对比。
     - 验收标准：通过 **Gate G1** 盲听确认“英/中 100% 为同一声带主体、无年龄/共振峰漂移、无中式平调串入英文、无西式洋腔串入中文”后锁死入库。

3. **防跨语种口音污染铁律 (`anti_accent_bleed_rules`)**：
   - 英文参考段严禁出现元音扁平化或音节等时（syllable-timed）朗读腔；
   - 中文参考段严禁出现“翻译腔重音上扬”或英语教师说教腔；
   - 严禁对 `lin_chen.wav` 施加 `afftdn` 频谱降噪，避免抹平高频声道共振峰指纹。

---

## 4. `custom_anchors/` 真人录音即插即用替换流 (Drop-In Workflow)

团队或配音演员随时可以用更高质量的定制真人棚录音频覆盖任意角色，无需改动任何脚本代码：

1. **文件命名规范**：
   - 音频文件：`<role_id>.wav`（亦支持 `.mp3` / `.m4a` / `.flac`，自动转为标准 44.1kHz 单声道 PCM16 `-16 LUFS` WAV）；
   - 逐字台词伴生文件（强烈推荐）：`<role_id>.txt`（UTF-8 纯文本，必须与音频实际念出的每一个字词 100% 一致，含数字与英文专有名词）。

2. **目录投放位置**：
   - **Google Drive 云盘路径**：
     `MyDrive/《跨境底牌：硅深暗战》Global_Edge_双语商战广播剧/01_Colab_96GB_FishDrama3_工作台/custom_anchors/`
   - **本地 / CI 路径**：通过 `--custom-anchors-dir /path/to/custom_anchors` 显式传入。

3. **四级真实声源解析优先级**（由 `colab_96gb/prepare_global_edge_voice_anchors.py` 执行，**零合成回退**）：
   1. `custom_anchors/<role_id>.{wav,mp3,m4a,flac}` 用户定制真人棚录投放（最高优先级）；
   2. 仓库内置 `projects/global_edge/00_节目圣经与第一季24集总纲/voice_anchors/<role_id>.wav`（体积 `> 10000 bytes`）；
   3. `anchor_sources.json` 中登记的开源许可真人语料直链（仅限角色独占直链，严禁两角色共用同一音频 URL；HTTP 下载后实时做 FFmpeg 棚录标准化，且**严禁**将虚构试音台词硬写为参考文本，必须严格读取 `direct_audio_transcript`/`source_transcript` 或调用本地 `faster-whisper-small-int8` 实录转写，否则立即报错退出并清理文件）；
   4. 若无可用真人源且未开启 `--offline-stub`，直接抛出明确可操作错误并指示人工投放路径，**绝不偷偷回退至任何合成 TTS**。

4. **CLI 一键制备命令**：
   ```bash
   # 生产模式：注入自定义棚录目录并锁死 8 角色 v2_real_human_studio 声纹库
   PYTHONPATH=src python3 colab_96gb/prepare_global_edge_voice_anchors.py \
     --custom-anchors-dir /path/to/custom_anchors \
     --output-dir /tmp/global_edge_anchors

   # 本地 CI / 无 GPU 离线干跑自检模式（明确标记 offline_synthetic_stub，严禁用于生产）
   PYTHONPATH=src python3 colab_96gb/prepare_global_edge_voice_anchors.py \
     --output-dir /tmp/global_edge_stub_anchors \
     --offline-stub
   ```

---

## 5. 统一 FFmpeg 棚录标准化链与声学硬指标 (Conditioning Spec)

所有进入 `voice_anchors/<role_id>.wav` 的真人参考音频，必须统一经过 `condition_studio_anchor_wav()` 精确处理：

| 声学参数 | 锁定指标 | 工程原因与防坑说明 |
| :--- | :--- | :--- |
| **采样率 (`-ar`)** | **`44100 Hz`** | 与 `fishaudio/drama-3` 原生音频编码器（`DRAMA3_ANCHOR_SAMPLE_RATE = 44100`）零重采样对齐 |
| **声道 (`-ac`)** | **`1`（单声道 Mono）** | 消除双麦相位差与立体声房间反射偏移 |
| **编码格式 (`-c:a`)** | **`pcm_s16le`**（16-bit PCM WAV） | 无损、零编解码延迟、全平台兼容 |
| **单声道下混前置** | **`aformat=sample_rates=44100:channel_layouts=mono`** | **必须置于 `highpass` 与 `loudnorm` 之前**：若对 48kHz 双声道立体声源先做 `loudnorm` 再经 `-ac 1` 下混，单声道响度会系统性跌落 `-3.0 dB`（双单声道）至 `-6.0 dB`（非相关立体声，实测跌至 `-19`~`-22 LUFS`）；前置 `aformat` 可确保所有立体声源精准锁定 `-16.0 LUFS` |
| **高通滤波** | **`highpass=f=75`** | 精准切掉 75 Hz 以下空调低频轰鸣与桌架震动，完整保留男中低音 90–140 Hz 胸腔基频 |
| **响度标准化** | **`loudnorm=I=-16:TP=-1.5:LRA=11`** | 全 8 位角色锚点能量完全齐平（若切片 `< 1.5s` 则自动退守 `alimiter=limit=0.89:level=disabled`） |
| **频谱降噪 (`afftdn`)** | **严禁使用 (`no_afftdn: true`)** | `afftdn` 会造成高频辅音发闷、水下金属感与声纹高频泛音损失，显著劣化 Drama 3 克隆保真度 |
| **有效时长** | **`10.0s – 18.0s`**（`lin_chen` 推荐 `12.0s – 16.0s`） | 过短缺少韵律统计信息，过长增加参考序列显存占用且易引入情绪漂移 |
| **信噪比与干度** | **`SNR >= 45 dB`**、近麦无混响、0 背景音乐、0 他人插话 | 确保克隆出的对白在 `boardroom`/`inner_monologue`/`phone_call` 空间切换时基底完全干净 |

**标准 FFmpeg 执行链**（严格先 `aformat` 单声道重采样，再高通与响度标准化）：
```bash
ffmpeg -y -hide_banner -loglevel error \
  -i input_raw_human_voice.wav \
  -af "aformat=sample_rates=44100:channel_layouts=mono,highpass=f=75,afade=t=in:st=0:d=0.03,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -ar 44100 -ac 1 -c:a pcm_s16le \
  voice_anchors/<role_id>.wav
```

---

## 6. 逐字 `.txt` 伴生稿与 `faster-whisper-small-int8` 核验流程

`fishaudio/drama-3` 在零样本克隆时同时读取参考音频 `audio_path` 与参考文本 `text`。若参考文本哪怕漏掉一个词或错标一个数字，模型对齐注意力都会漂移并导致成片吞词。

1. **双文件绑定规则**：
   - 每个 `voice_anchors/<role_id>.wav` 必须同步生成同名 UTF-8 文本文件 `voice_anchors/<role_id>.txt`，并同步写入 `voice_cast_drama3.json` 的 `characters[role_id].anchor_text`。
2. **自动回写与核验流程**：
   - 若 `custom_anchors/<role_id>.txt` 存在且非空，优先直接读取该人工核对稿；
   - 若缺失 `.txt` 伴生稿，脚本惰性加载 CPU `int8` **`faster-whisper-small-int8`**（0 MB 显存，经 FFmpeg 管道实时转 16kHz 单声道 `f32le`，`beam_size=5, vad_filter=True`）：
     - 纯英角色（`language_code="en"`）：固定 `language="en"`；
     - 双语角色（`lin_chen` / `zhou_mo`）：自动检测混合语种并附带 NovaEdge 商战词表提示，随后人工抽检修正标点与英文术语拼写（如 `BOM cost`、`income statement`、`GDPR`）。
   - 音频与文本中严禁保留 `[measured]`、`[short pause]` 等导演表演标签——`anchor_text` 必须是**100% 实际说出口的纯净台词**。

---

## 7. `AUDITION_GLOBAL_EDGE` 试音包 `G1–G8` 八道量化验收门

在进入第一季 24 集全量渲染前，必须先使用锁定后的 8 角色 `v2_real_human_studio` 锚点渲染 `AUDITION_GLOBAL_EDGE`，并逐项通过与 `ACCENT_AND_PROSODY_MANUAL.md` 完全一致的 **G1–G8** 八道门禁：

| 门禁编号 | 核验维度 | 量化通过标准 | 未通过处置动作 |
| :---: | :--- | :--- | :--- |
| **G1** | `lin_chen` 跨语种同声源一致性 | 盲听确认 `lin_chen` 公开英文谈判与中文 `inner_monologue` 为**同一真人声带主体**（无年龄、性别、共振峰跳变，无中英口音互串） | 切换方案 A/B 或重剪同场双语 `lin_chen.wav`，重跑试音 |
| **G2** | 硅谷/纽约美音 vs 伦敦 RP 英音区分度 | 3 秒内 100% 盲听区分 `victoria_vance`（SV 美音）、`claire_chen_gc`（NYC 美音）与 `alistair_finch`（伦敦 RP）；零 `[wryly]` 美式中西部口音漂移 | 复核 `anchor_sources.json` 与纯英角色禁用标签表 |
| **G3** | 国际客串 LFC 清晰度与零漫画化 | `henrik_lindqvist` / `rajiv_menon` / `wei_ling_tan` 关键财务数字与商业术语 B1–C1 听辨率 100%，零刻板印象夸张腔 | 更换更克制、吐字更清晰的精英访谈近麦片段 |
| **G4** | 正片高管自然语速区段 | 纯英正片试音落在 **`150–185 WPM`**（伦敦 RP / 北欧法务 `145–165 WPM`，硅谷 / 纽约 `160–185 WPM`），零播音拖腔 | 调整标点停顿、`stability` 或锚点语速样本 |
| **G5** | Act 5 `0.80x` 不降调慢速拆解质检 | FFmpeg `atempo=0.800` 输出（`120–145 WPM`）无降调变粗、无金属抖动伪影、辅音连读清晰，且 100% 复用 `1.0x` Drama 3 原始缓存轨 | 核查 `mixer.py:condition_dialogue_clip()` 滤镜顺序与 48kHz 采样率 |
| **G6** | 抢话重叠与声学空间无缝切换 | `boardroom` 抢话（`gap_after_s = -0.15s`）干净无爆音；`inner_monologue` 零洞穴混响；`phone_call` 300–3400Hz 频带辨识清晰 | 审计 `acoustic_space`（确认 `boardroom` 无 `apad`、全剧禁用 `mental_realm`） |
| **G7** | 本地 `faster-whisper-small-int8` 双脚本自动质检 | 全 8 角色通过 `evaluate_dialogue_qa()`：`char_recall >= 0.72`（`zh-en` 同时校验 `CJK >= 4` 与 `EN >= 3`）、`0` 标签漏读、`duration_s >= 0.25s`、`peak_dbfs >= -45.0` | 自动触发 `attempt=1 -> 2 -> 3` 三级降级重抽并复核 `polyphones.py` |
| **G8** | 广电级三母线母带与双行字幕验收 | 最终 48kHz 立体声 WAV/MP3 实测 **`-16.0 ± 0.5 LUFS`**、真峰值 **`<= -1.0 dBTP`**；中英双行 `.srt` 时间轴零重叠、`subtitle_translation` 零泄露进 TTS | 检查 `mixer.py` 限幅器参数与 SRT 夹紧逻辑 |
