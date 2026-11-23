# AUDITION_DELUSIONS ·《《1841伦敦泡沫档案：〈大癫狂〉金融疯魔史》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1841伦敦泡沫档案八角试听 | `Intimate atmospheric 1841 Victorian London chamber music, warm expressive solo cello, delicate baroque harpsichord arpeggios and muted romantic strings evoking a gaslit Fleet Street archive study on a foggy night, purely acoustic instrumental, no modern drums, no vocals, no singing, no Chinese instruments` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1841伦敦泡沫档案八角试听】

- 🔊 **`[da01_gaslight]` 音效 · 独立顺播**（复用母题 `fleet_street_gaslight`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Atmospheric 1841 Victorian London gaslit study ambience with soft hissing brass gas lamp, heavy bound archive ledger pages turning on an oak desk, faint rain on windowpanes, and distant carriage wheels on damp cobblestones, pure foley, no human voice`

- 🎙️ **`[da02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一八四一年秋夜，伦敦舰队街煤气灯微亮。三十五岁的记者查尔斯·麦基摊开泛黄卷宗，里头记录的不是疯人院，而是三百年里无数聪明人如何集体失了智。

- 🔊 **`[da03_bell]` 音效 · 叠加下一句起拍**（复用母题 `exchange_alley_bell`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Frantic 1720 London Exchange Alley coffeehouse foley with a bright hand-rung brass trading bell, porcelain coffee cups clattering against saucers, urgent boots tapping wooden floorboards, and crisp stock certificates rustling fast, pure foley, no human voice`

- 🎙️ **`[da04_henry]` 亨利 (`clerk_henry`)** （`stability=0.0` | 句后气口 `0.22s`）  
  > [excited] 别劝我干实业啦！早上花两英镑抢进的神秘公司认购单，中午走回咖啡馆就有人出五英镑抢！傻瓜才一辈子靠工资攒钱！

- 🎙️ **`[da05_vander]` 老范德 (`merchant_vander`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 阿姆斯特丹一颗花根炒到一套运河豪宅加两匹骏马，结果一个水手以为是洋葱，拿去配咸鲱鱼三口啃了个精光！

- 🎙️ **`[da06_law]` 约翰·劳 (`john_law`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [condescending] [chuckles] 黄金沉得像石头，信用才长着翅膀！只要全巴黎相信我的银行纸币，密西西比河的泥滩明天就能变出花不完的金矿！

- 🎙️ **`[da07_claire]` 克莱尔夫人 (`lady_claire`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [chuckles] [wryly] 巴黎的公爵夫人们连家传钻石都当掉了，甚至故意把马车翻在约翰·劳家门口，就为逼他下车匀两张密西西比股票！

- 🎙️ **`[da08_newton]` 艾萨克·牛顿 (`newton`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [sighs] [solemn] 一七二〇年的南海股让我痛失两万英镑毕生积蓄。我能精确算准天体的运行，却永远算不透人性的疯狂！

- 🎙️ **`[da09_mackay]` 查尔斯·麦基 (`mackay`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [wryly] [solemn] 历史早把真相写透了：人类总是成群结队地思考，成群结队地发疯；可醒过来的时候，却只能一个一个慢慢恢复理智。

- 🎙️ **`[da10_shen]` 沈知微 (`host_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《1841伦敦泡沫档案》——告别晦涩翻译腔，八位鲜活角色现场飙戏，听懂三百年金融疯魔史！
