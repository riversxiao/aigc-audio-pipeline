# AUDITION_LIAOZHAI ·《《聊斋志异·午夜悬疑广播剧场》核心声线与恐怖氛围试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 午夜聊斋试听总场 | `Dark eerie traditional Chinese classical instrumental underscore for midnight ghost folklore, sparse low guqin harmonics, haunting breathy bamboo xiao flute sustained notes, distant soft temple woodblock, chilling misty courtyard silence, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 午夜聊斋试听总场】

- 🔊 **`[la01_clapper]` 音效 · 独立顺播**（复用母题 `night_watch_clapper`） （时长 `3.4s` | 句后留白 `0.3s`）  
  Prompt: `Traditional ancient Chinese night watchman hollow bamboo clapper struck three slow times followed by one distant low brass gong shimmer echoing down a wet cobblestone alley in midnight mist, pure foley, no human voice`  
  *导演备注：三更梆子定调入戏*

- 🎙️ **`[la02_narrator]` 午夜说书人 (`narrator`)** （`stability=0.5` | 句后气口 `0.25s`）  
  > [eerie] 三更梆子刚过，书斋窗纸外头忽然起了一阵阴风。你听，纸窗那头，像是有人正拿湿漉漉的画笔，一下一下往一张人皮上描眉毛。

- 🔊 **`[la03_tear]` 音效 · 独立顺播**（复用母题 `paper_window_tear`） （时长 `2.0s` | 句后留白 `0.2s`）  
  Prompt: `Delicate close-up foley of a dampened thin traditional mulberry paper window screen being poked and slowly torn open by a fingertip in a dead silent midnight courtyard, pure foley, no human voice`  
  *导演备注：湿润手指捅破窗纸*

- 🎙️ **`[la04_wang]` 王生 / 青年书生 (`scholar_young`)** （`stability=0.0` | 句后气口 `0.22s`）  
  > [terrified] [whispers] 天爷啊……屋里哪是什么绝色佳人！那张画得活灵活现的皮，正摊在长榻上，灯底下坐着个浑身发绿的恶鬼！

- 🎙️ **`[la05_seductive]` 画皮魅女 (`seductive_ghost`)** （`stability=0.0` | 句后气口 `0.18s`）  
  > [seductive] 郎君怎么在窗外发抖呀？风这么凉，快进屋来，奴家替你温了酒……

- 🎙️ **`[la06_demon]` 青面厉鬼 (`demon_fiend`)** （`stability=0.0` | 句后气口 `0.26s`）  
  > [hoarsely] [laughs] 既偷看了本座的皮囊，还想活着跨出这道门槛？今夜便挖了你的活心来补这副空壳！

- 🔊 **`[la07_sword]` 音效 · 叠加下一句起拍**（复用母题 `sword_unsheathe_thunder`） （时长 `2.8s` | 句后留白 `0.15s`）  
  Prompt: `Sharp metallic ringing unsheathe of an ancient steel Chinese sword slicing through midnight air accompanied by a sudden cracking distant thunderclap, cinematic foley, no human voice`  
  *导演备注：飞剑出鞘压惊雷*

- 🎙️ **`[la08_yanchixia]` 燕赤霞 / 豪侠剑客 (`heroic_swordsman`)** （`stability=0.0` | 句后气口 `0.28s`）  
  > [shouting] 孽畜休得猖狂！宁采臣，退后三步捂紧耳朵，看我剑光斩了这荒寺老妖！

- 🎙️ **`[la09_xiaoqian]` 聂小倩 / 清丽佳人 (`gentle_maiden`)** （`stability=0.0` | 句后气口 `0.35s`）  
  > [crying] [whispers] 宁公子，小倩白骨就埋在荒寺北头那棵白杨树下……你若肯带我离开兰若寺，来世做牛做马报答恩公。

- 🎙️ **`[la10_whisper]` 幽冥诡影 (`eerie_whisper`)** （`stability=0.0` | 声场 `mental_realm` | 句后气口 `0.55s`）  
  > [haunting] [whispers] 嘘……灯灭了。今晚的《午夜聊斋》，才刚刚翻开第一页……
