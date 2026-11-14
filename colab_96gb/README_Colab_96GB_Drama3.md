# 《诸界锁仙》 96GB Colab G4 · Fish Audio Drama 3 全本 120 章满血本地推理工业管线 (`v1.2.0`)

## 一、为什么之前的 Colab `Fish Drama 3` 听起来不如 ElevenLabs？这套升级版如何逼近电影感成片？

通过逐行拆解此前《九狱剑主》的 96GB Colab 脚本并与 `ElevenLabs eleven_v3` 生产母带对照，旧版开源推理效果偏平、偶发吞字/机械腔的核心瓶颈并非 `fishaudio/drama-3`（35B MoE / 3B active）模型本身能力不足，而是 **6 个上下游工程环节缺失**。本升级版（`v1.2.0`）已逐一彻底打通：

| 核心瓶颈 | 旧版《九狱剑主》 96GB 脚本 | 本次《诸界锁仙》 `v1.2.0` 满血升级版 |
| :--- | :--- | :--- |
| **1. 零样本参考干音底座 (`references`)** | 参考锚点音色偏平，导致零样本克隆上限被锁死 | **「ElevenLabs 捏声优 + Drama 3 无限出演」混合架构**：直接提取《诸界锁仙》已用 `eleven_ttv_v3` 精调锁定的 **全剧 28 位纯正大陆普通话戏剧干音**（`44.1kHz` `-16 LUFS` 纯净棚录 WAV + 100% 逐字对齐 `anchor_text`，含姜清凰、太一、终局残魂、守墓老人四大中后期灵魂角色）作为克隆底座，零 API 成本继承顶级国风声线！ |
| **2. 导演情绪与气口控制语法** | 仅用简单前缀文本，未发挥 Drama 3 原生标签能力 | 内置 `drama3_adapter.py`，将全本 120 集未删减台本自动转译为 **Drama 3 原生自然语言导演指令**（如 `[aloof, aristocratic disdain] [cold laugh]`）+ **成对韵律跨度标签**（`<whisper>…</whisper>`、`<forceful>…</forceful>`、`<slow>…</slow>`） |
| **3. 仙侠生僻词与多音字读音** | 易将“引气三重”读成 `zhòng`、“真传”读成 `zhuàn` | 完整接入 `polyphones.py` **70+ 仙侠专有名词与古账册大写数字纠偏引擎**，并支持 `--phoneme-pins` 原生 `<\|phoneme_start\|>yin3 qi4 san1 chong2<\|phoneme_end\|>` 拼音强锚定 |
| **4. SGLang-Omni 采样器参数** | 默认基础采样，长句偶发语调平直或复读 | 自动检测并开启 Fish Audio 官方推荐的 **`reference_sampling=true` + `ras`（Repetition-Aware Sampling）** 高表现力防复读采样策略 |
| **5. 坏轨自动重抽与死寂切边** | 无 ASR 质检，偶发标签漏读或繁简误判重抽 | 内置 **零显存占用 CPU `int8` `faster-whisper` 简体中文引导质检门** + 语速边界检测（最多自动降级提示词重抽 2 次），外加 **PCM 首尾死寂智能微裁切**，对白气口紧凑利落 |
| **6. 纯古风母题配乐与三母线母带** | 现代鼓点串味、拟音混入假人声、混音无空间感 | 100% 接入 `aigc-audio-pipeline` **三母线 `-16 LUFS` 母带台 (`mixer.py`)** + `world_ost_palette.py` **23 首纯中国古典器乐母题**（`vocal_language="unknown"` 杜绝现代鼓点与人声采样）+ `sanitize_moss_foley_prompt` 纯净拟音守门员；支持 `speaker_name` 跨世界角色真名 `.srt` 字幕 |

---

## 二、96GB 显存黄金三件套同卡常驻预算（Colab G4 `RTX PRO 6000 Blackwell 96GB`）

| 轨道分工 | 开源旗舰模型 | 隔离环境 | 显存占用 | 说明 |
| :--- | :--- | :--- | :---: | :--- |
| **角色对白与表演** | `fishaudio/drama-3` (35B MoE, 3B active, FP8) | `drama3-venv` (`sglang-omni` + `ninja`) | **~59.5 GB** | `40G–80G` 显卡或 `--profile fast` 自动切换为 `fishaudio/drama-3-int4` (~20.8 GB) |
| **前景拟音 (Foley)** | `OpenMOSS-Team/MOSS-SoundEffect-v2.0` | `moss-venv` (`transformers==4.57.1`) | **~6.5 GB** | 6 大跨集母题直接零耗时复用母带 WAV，仅新音效走 MOSS 48kHz 纯净拟音 |
| **分幕原声配乐 (BGM)** | `ACE-Step/acestep-v15-xl-turbo-diffusers` | `acestep-venv` (`diffusers>=0.41.0`) | **~9.0 GB** | 48kHz 立体声纯中国古典器乐，跨集世界观 OST 自动命中 SHA-256 缓存，全程零重载！ |
| **回听质检 (ASR QA)** | `faster-whisper` (`small`, CPU `int8`, 简中引导) | `moss-venv` (CPU) | **0.0 GB** | FFmpeg 16kHz PCM 直喂 + 简体中文 `initial_prompt`，零显存争抢 |

---

## 三、两种极速启动方式（任选其一）

### 方式 A：【最省心推荐】Colab Notebook 点一下 `Cell 0`，交由云端 Agent 纯 HTTPS 全自动跑完 `E007-E120` 并自动关机！

直接在 Google Drive 打开 `05_Colab_96GB_FishDrama3_满血本地推理管线/Zhujie_Suoxian_96GB_Drama3_Studio.ipynb`：
1. 右上角连接 **G4 (96GB)** 运行时；
2. 点击 **Cell 0（`▶ 点击此处一键移交云端 Antigravity Agent 全自动接管`）**，授权挂载 Google Drive；
3. 对云端 Agent 说一句 **`开了`** —— Agent 会自动启动 **`E007-E120`（共 114 集直达第 120 章大结局）**，每完成一集秒级原子同步至 Google Drive（`outputs/` 与 `03_分集成片音频/`），并在 `E120` 归档完毕后**自动触发 `runtime.unassign()` 销毁 G4 实例立停 CCU 计费**（支持无人值守过夜）！

### 方式 B：命令行一键无头启动

```bash
colab new -s audio96 --gpu G4
colab drivemount -s audio96
echo "!python3 '/content/drive/MyDrive/《诸界锁仙》长篇修仙小说工程/04_有声剧与广播剧音频/05_Colab_96GB_FishDrama3_满血本地推理管线/launch_g4_zhujie_drama3.py' --episodes E007-E120 --skip-existing --mirror-to-main-masters --auto-unassign" | colab exec -s audio96
```
