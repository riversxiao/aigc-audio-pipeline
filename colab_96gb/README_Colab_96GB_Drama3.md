# 《诸界锁仙》 96GB Colab G4 · Fish Audio Drama 3 满血本地推理工业管线 (`v1.1.0`)

## 一、为什么之前的 Colab `Fish Drama 3` 听起来不如 ElevenLabs？这套升级版如何逼近电影感成片？

通过逐行拆解此前《九狱剑主》的 96GB Colab 脚本并与 `ElevenLabs eleven_v3` 生产母带对照，旧版开源推理效果偏平、偶发吞字/机械腔的核心瓶颈并非 `fishaudio/drama-3`（35B MoE / 3B active）模型本身能力不足，而是 **6 个上下游工程环节缺失**。本升级版（`v1.1.0`）已逐一彻底打通：

| 核心瓶颈 | 旧版《九狱剑主》 96GB 脚本 | 本次《诸界锁仙》 `v1.1.0` 满血升级版 |
| :--- | :--- | :--- |
| **1. 零样本参考干音底座 (`references`)** | 参考锚点音色偏平，导致零样本克隆上限被锁死 | **「ElevenLabs 捏声优 + Drama 3 无限出演」混合架构**：直接提取《诸界锁仙》已用 `eleven_ttv_v3` 精调锁定的 **全剧 24 位纯正大陆普通话戏剧干音**（`44.1kHz` `-16 LUFS` 纯净棚录 WAV + 100% 逐字对齐 `anchor_text`）作为克隆底座，零 API 成本继承顶级国风声线！ |
| **2. 导演情绪与气口控制语法** | 仅用简单前缀文本，未发挥 Drama 3 原生标签能力 | 内置 `drama3_adapter.py`，将全 40 集未删减台本自动转译为 **Drama 3 原生自然语言导演指令**（如 `[aloof, aristocratic disdain] [cold laugh]`）+ **成对韵律跨度标签**（`<whisper>…</whisper>`、`<forceful>…</forceful>`、`<slow>…</slow>`） |
| **3. 仙侠生僻词与多音字读音** | 易将“引气三重”读成 `zhòng`、“真传”读成 `zhuàn` | 完整接入 `polyphones.py` **70+ 仙侠专有名词与古账册大写数字纠偏引擎**，并支持 `--phoneme-pins` 原生 `<\|phoneme_start\|>yin3 qi4 san1 chong2<\|phoneme_end\|>` 拼音强锚定 |
| **4. SGLang-Omni 采样器参数** | 默认基础采样，长句偶发语调平直或复读 | 自动检测并开启 Fish Audio 官方推荐的 **`reference_sampling=true` + `ras`（Repetition-Aware Sampling）** 高表现力防复读采样策略 |
| **5. 坏轨自动重抽与死寂切边** | 无 ASR 质检，偶发标签漏读或句尾拖 1 秒死寂空白 | 内置 **零显存占用 CPU `int8` `faster-whisper` 自动回听质检门** + 语速边界检测（最多自动降级提示词重抽 2 次），外加 **PCM 首尾死寂智能微裁切**，对白气口紧凑利落 |
| **6. 混音母带与跨集声音资产** | 音效串行拼接无法叠化对白、`tanh` 硬削波、无空间混响 | 100% 接入 `aigc-audio-pipeline` **三母线 `-16 LUFS` 母带台 (`mixer.py`)**：直接复用已生成的 **6 大标志性声效母题 WAV**（墟界开石门、玄霜叩棺、基因锁心跳等）与 E001–E002 母带配乐；支持 `overlay_next` 音效不闪避叠化、`mental_realm`/`memory_echo` 识海空间混响、BGM 侧链平滑闪避（对白期 `0.11` / 留白期 `0.34`）与中文角色名 `.srt` 字幕 |

> [!TIP]
> **零覆盖安全对照机制**：本管线产出的成片统一采用 `E001_drama3_master_v001.{mp3,wav,srt,json}` 独立命名并默认归档至 `05_Colab_96GB_FishDrama3_满血本地推理管线/outputs/`，绝不覆盖前 6 集 ElevenLabs 版成片。推荐先跑 **`--episodes AUDITION`**（25 秒出 6 句试听合集）或 **`--episodes E001`**，与 ElevenLabs 版做同集 A/B 盲听对比，满意后直接一键连跑 **`--episodes E007-E040`** 把剩余 34 章全部零 API 费用跑完！

---

## 二、96GB 显存黄金三件套同卡常驻预算（Colab G4 `RTX PRO 6000 Blackwell 96GB`）

| 轨道分工 | 开源旗舰模型 | 隔离环境 | 显存占用 | 说明 |
| :--- | :--- | :--- | :---: | :--- |
| **角色对白与表演** | `fishaudio/drama-3` (35B MoE, 3B active, FP8) | `drama3-venv` (`sglang-omni`) | **~59.5 GB** | `40G–80G` 显卡或 `--profile fast` 自动切换为 `fishaudio/drama-3-int4` (~20.8 GB) |
| **前景拟音 (Foley)** | `OpenMOSS-Team/MOSS-SoundEffect-v2.0` | `moss-venv` (`transformers==4.57.1`) | **~6.5 GB** | 6 大跨集母题直接零耗时复用母带 WAV，仅新音效走 MOSS 48kHz 生成 |
| **分幕原声配乐 (BGM)** | `ACE-Step/acestep-v15-xl-turbo-diffusers` | `acestep-venv` (`diffusers>=0.41.0`) | **~9.0 GB** | 48kHz 立体声纯器乐 `[inst]`，三模型合计 **~75.0 GB / 96 GB**，全程零重载！ |
| **回听质检 (ASR QA)** | `faster-whisper` (`small`, CPU `int8`) | `moss-venv` (CPU) | **0.0 GB** | 纯 CPU 16 核多线程推理，零显存争抢 |

---

## 三、两种极速启动方式（任选其一）

### 方式 A：命令行一键无头启动（推荐，完美适配您的 `colab` CLI 工作流）

```bash
# 1. 启动 96GB G4 实例并挂载 Google Drive（若已有 audio96 会话可跳过前两步）
colab new -s audio96 --gpu G4
colab drivemount -s audio96

# 2. 【极速盲听对比】先跑 6 句方案A试听合集 + 第 1 集完整版（默认即 AUDITION,E001，与 ElevenLabs 版同集 A/B 对照）
colab exec -s audio96 -f colab_96gb/launch_g4_zhujie_drama3.py

# 3. 【全量零成本续跑】确认质感满意后，三模型常驻显存一口气跑完第 7–40 集！（跑完记得释放实例）
echo "!python3 '/content/drive/MyDrive/《诸界锁仙》长篇修仙小说工程/04_有声剧与广播剧音频/05_Colab_96GB_FishDrama3_满血本地推理管线/launch_g4_zhujie_drama3.py' --episodes E007-E040 --skip-existing" | colab exec -s audio96
colab stop -s audio96
```

- **秒级复用云盘缓存**：启动器会自动检测您云盘现有的 `/content/drive/MyDrive/AI_Workstation/AudioStudio_G4_Cache/{sglang_omni_sm120.tar.gz, moss_tts_v2.tar.gz}` 及已建好的本地虚拟环境，并通过 `127.0.0.1:8012` 高速通道在 1.5 秒内将 164MB 工程包（含 24 角色干音 + 6 母题 + 40 集全剧本）解压至本地 NVMe SSD。
- **单集原子落盘**：每渲染完一集，立即通过 Google Drive REST API v3 原子上传 `.mp3` / `.wav` / `.srt` / `.json` 至云盘 `05_Colab_96GB_FishDrama3_满血本地推理管线/outputs/`（加 `--mirror-to-main-masters` 可同步抄送一份至 `03_分集成片音频/`），随时停机零丢片！

### 方式 B：浏览器交互式 Colab Notebook 一键运行

直接在 Google Drive 打开 `05_Colab_96GB_FishDrama3_满血本地推理管线/Zhujie_Suoxian_96GB_Drama3_Studio.ipynb`：
1. 右上角连接 **G4 (96GB)**（或 A100 80GB/40GB）运行时；
2. 设置 `EPISODES = "AUDITION,E001"` 或 `EPISODES = "E007-E040"`；
3. 点击 **`全部运行 (Run all)`**，即可在网页端直接在线试听并自动归档至 Google Drive！
