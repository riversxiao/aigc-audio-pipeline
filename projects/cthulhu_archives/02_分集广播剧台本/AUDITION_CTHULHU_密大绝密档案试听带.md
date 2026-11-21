# AUDITION_CTHULHU ·《《克苏鲁神话·不可名状声音档案》密大绝密档案试听带》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 密大特藏档案试听 | `Dark atmospheric 1920s investigative horror documentary score, muted vintage felt piano sparse chords, low sustained solo cello drone and subtle contrabass pulse in a quiet rain-streaked university archive, restrained creeping dread, purely acoustic chamber instrumental, no drums, no modern beat, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 密大特藏档案试听】

- 🔊 **`[ca01_wax]` 音效 · 独立顺播**（复用母题 `wax_cylinder_click`） （时长 `2.4s` | 句后留白 `0.25s`）  
  Prompt: `Authentic 1920s antique wax cylinder phonograph mechanical brass lever click followed by subtle warm vintage needle hiss and slow crank rotation in a quiet archive room, pure foley, no human voice`  
  *导演备注：老式蜡筒留声机落针启封档案*

- 🎙️ **`[ca02_archivist]` 阿卡姆档案员 (`female_archivist`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [seriously] 密斯卡托尼克大学特藏室，封存档案零零一号，一九二八年冬。以下录音来自六位已经失踪或发疯的目击者。

- 🎙️ **`[ca03_thurston]` 弗朗西斯·瑟斯顿 / 密大首席调查员 (`archivist_narrator`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [solemn] 人类理智最慈悲之处，在于它无力将世间万象拼凑完整。我打开叔祖上锁的铁盒之前，从没想过深海底下还睡着什么东西。

- 🔊 **`[ca04_foghorn]` 音效 · 独立顺播**（复用母题 `foghorn_harbor_night`） （时长 `3.6s` | 句后留白 `0.22s`）  
  Prompt: `Lonely deep distant harbor foghorn blaring once across a cold foggy New England bay at midnight over dark lapping sea waves against rotting wooden pilings, pure foley, no human voice`

- 🎙️ **`[ca05_zadok]` 扎多克·艾伦 / 疯癫老酒鬼 (`mad_elder`)** （`stability=0.0` | 句后气口 `0.22s`）  
  > [hoarsely] [whispers] 别回头看魔鬼礁！印斯茅斯的海水底下全是眼睛——快跑，小子！他们今晚就要来撬你的旅馆门锁了！

- 🔊 **`[ca06_lock]` 音效 · 叠加下一句起拍**（复用母题 `heavy_wooden_lock_pick`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Close-up tense foley of a rusty skeleton key quietly probing and scraping inside an old brass hotel door lock followed by the heavy wooden doorknob slowly rattling in midnight silence, pure foley, no human voice`

- 🎙️ **`[ca07_wilcox]` 亨利·威尔科克斯 / 濒疯目击者 (`panicked_witness`)** （`stability=0.0` | 句后气口 `0.24s`）  
  > [terrified] [desperately] 那些墙全都是错的！锐角看起来像钝角，湿漉漉的绿石头顶天立地——它睁开眼了！

- 🎙️ **`[ca08_akeley_fake]` 黑暗中的阿克利 / 非人伪声 (`cultist_buzzing`)** （`stability=0.0` | 声场 `memory_echo` | 句后气口 `0.26s`）  
  > [hoarsely] [eerie] 别开灯，威尔马斯教授……走近一点，摸摸桌子上那只刻着你名字的金属圆筒。

- 🔊 **`[ca09_abyss]` 音效 · 叠加下一句起拍**（复用母题 `abyssal_sub_bass_hum`） （时长 `3.8s` | 句后留白 `0.18s`）  
  Prompt: `Colossal subterranean deep-sea tectonic sub-bass rumble with wet ancient monolith stone grinding and eerie cavernous resonance evoking an unfathomable waking entity, pure foley, no human voice`

- 🎙️ **`[ca10_whisper]` 拉莱耶梦语 / 深渊梦魇呢喃 (`eldritch_whisper`)** （`stability=0.0` | 声场 `mental_realm` | 句后气口 `0.55s`）  
  > [haunting] [whispers] 在永恒的宅邸拉莱耶中……长眠的克苏鲁，正在等待着做梦……
