# aigc-audio-pipeline

中文广播剧 / 多人精品有声剧的独立音频生产流水线：**选角定声 → 台本校验 → 关键句试听（含双语 ASR 质检） → 自然语速三总线母带合成**。大媒体与母带不进 Git。

听感差通常不是模型再换一家，而是这四步没做对：用 `eleven_v3` 与大陆普通话戏剧声线，激烈戏把稳定性打到 Creative `0.0` 并写入行内 Audio Tags，时间轴跟人声自然语速走（绝不裁尾），音效（前景独立总线）和配乐（分幕自动闪避总线）用同一家合成并先出短试听。

方法论全文：[playbook/AUDIO_RADIO_DRAMA.md](playbook/AUDIO_RADIO_DRAMA.md)

## 工程架构（v0.2 升级）

本仓将 [`playbook/AUDIO_RADIO_DRAMA.md`](playbook/AUDIO_RADIO_DRAMA.md) 的实战铁律固化为零第三方依赖（Python 3.11+ 标准库 + `ffmpeg`）的可执行流水线：

- **`models.py`（硬规则防呆与持久化声线库）**：
  - 强制校验 `eleven_v3` 三档离散稳定性（`0.0` Creative / `0.5` Natural / `1.0` Robust），拦截 SSML 误用与非英文行内标签。
  - 维护跨百章连载的持久化角色声线库（`voice_casting_registry.json`）与世界观标志性声效母题（`sonic_motifs`），杜绝长篇连载跨会话串音。
  - 强制追加式版本命名（`_v001`、`_v002`），旧试听与旧母带永不覆盖。
- **`elevenlabs_client.py`（同源五合一接口、原生国风捏声与档位自适应）**：
  - 仅需单个 `ELEVENLABS_API_KEY`（兼容细粒度 Scoped API Key）打通：原生国风声线捏造（`eleven_ttv_v3` Voice Design）、戏剧对白（`eleven_v3`）、动效（`eleven_text_to_sound_v3`）、分幕纯配乐（`music_v2_5`，自动规避 `prompt`+`seed` 422 冲突）与双语质检（`scribe_v3`）。
  - 共享库默认按 `locale=cmn-CN` 过滤外语母语配音洋腔并强制注入 `new_name`（防 422）；订阅档位受限时自动降级采样格式并在本地无损归一为 `48kHz 16-bit PCM WAV`，带内容哈希缓存避免重复扣费。
- **`qa.py`（Scribe v3 中英双语 ASR 质检）**：
  - 自动检测英文方括号标签是否被误念出口、句尾是否截断漏字；若首轮异常自动简化标签重试一次，满两次即停机保护额度。
- **`mixer.py`（48kHz 采样级自然语速三总线母带引擎）**：
  - **Bus A（人声主轨）**：完整保留自然语速与气口（`-16 LUFS` 响度归一，支持 `mental_realm` 识海空间与 `memory_echo` 记忆混响微染）。
  - **Bus B（前景动效轨）**：独立前景总线，**绝不随对白压矮**，支持 `sequential`（独立留白顺播）与 `overlay_next`（贴拍同步触发）。
  - **Bus C（分幕配乐床）**：按幕自动铺床循环，仅在对白区间平滑闪避至 `0.11`，气口与纯动效段回升至 `0.34`。
  - 同步导出 `48kHz WAV` 母带、`192kbps MP3` 试听版、毫秒级对齐 `.srt` 字幕与完整溯源 `manifest.json`。

## 快速上手

```bash
# 1. 环境与额度自检（支持 ELEVENLABS_API_KEY 环境变量或 ~/.gemini/config/aigc_audio.env）
PYTHONPATH=src python3 -m aigc_audio_pipeline check-env

# 2. 离线校验声线表与单集台本（无需消耗任何 API 额度）
PYTHONPATH=src python3 -m aigc_audio_pipeline validate \
  --registry templates/voice_casting_registry.example.json \
  --cue-sheet templates/episode_cue_sheet.example.json

# 3. 离线合成波形演练（零成本验证三总线闪避混音与字幕对齐）
PYTHONPATH=src python3 -m aigc_audio_pipeline synth-dry-test \
  --registry templates/voice_casting_registry.example.json \
  --cue-sheet templates/episode_cue_sheet.example.json \
  --output-dir /tmp/audio_dry_test

# 4. 从零捏造纯正大陆普通话专属国风声线（eleven_ttv_v3）或检索共享库（cmn-CN）
PYTHONPATH=src python3 -m aigc_audio_pipeline voices design \
  --description "一位六十五岁的中国北方老管家，纯正标准中国大陆普通话，嗓音苍老沙哑却透着温厚忠心，绝无外国口音。" \
  --sample-text "少主撑住！外头秋雨寒重，您丹田刚受了反噬，老奴这就去西街敲李郎中的门，拿亡妻这支簪子换半粒护心丸，哪怕拼了这把老骨头，老奴也绝不叫少主死在这冷堂里！" \
  --output-dir /tmp/voice_design_fubo --prefix fubo_old_butler

PYTHONPATH=src python3 -m aigc_audio_pipeline voices create-designed \
  --generated-voice-id <CHOSEN_GENERATED_VOICE_ID> \
  --name "诸界锁仙_福伯_苍老忠仆" \
  --description "65岁中国北方老管家，沧桑沙哑温厚忠仆声线" \
  --registry path/to/voice_casting_registry.json --role fu_bo --lock

# 5. 先跑 6 句短试听（含 Scribe v3 质检） → 认可后渲染整集三总线母带
PYTHONPATH=src python3 -m aigc_audio_pipeline audition \
  --registry path/to/voice_casting_registry.json \
  --cue-sheet path/to/e001_audition.json \
  --output-dir path/to/01_声线试听小样
PYTHONPATH=src python3 -m aigc_audio_pipeline render-episode \
  --registry path/to/voice_casting_registry.json \
  --cue-sheet path/to/e001_cue_sheet.json \
  --output-dir path/to/03_分集成片音频
```

## 相关仓库

影像成片见同级仓库 [aigc-mv-pipeline](https://github.com/riversxiao/aigc-mv-pipeline) 的 [`PIPELINE.md`](https://github.com/riversxiao/aigc-mv-pipeline/blob/master/playbook/PIPELINE.md)。两仓互不替代，本仓导出的毫秒级 `.srt` 与 `manifest.json` 可直接作为影像仓的精准声音母带时间轴。
