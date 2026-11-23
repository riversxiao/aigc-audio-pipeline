# AUDITION_OPERATOR ·《《1923华尔街风云：〈股票大作手回忆录〉》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1923华尔街风云八角试听 | `Smoky atmospheric 1920s Wall Street noir nocturnal chamber music, warm slow walking upright double bass, pensive moody felt piano phrases and velvet muted brass horn sighs evoking rain-streaked Manhattan trading offices under green banker lamps, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1923华尔街风云八角试听】

- 🔊 **`[oa01_rain]` 音效 · 独立顺播**（复用母题 `banker_lamp_rain_study`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Raindrops tapping steadily against tall 1920s Manhattan office windows beside the crisp metal pull-chain click of a green glass banker lamp and fountain pen scratching on thick ledger paper, pure foley, no human voice`

- 🎙️ **`[oa02_narr]` 华尔街黑色纪实旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 一九二三年深秋曼哈顿雨夜，绿灯微亮，黄铜行情打字机静静停转。华尔街传奇大作手翻开旧账，讲出三起三落的血泪真相。

- 🔊 **`[oa03_chalk]` 音效 · 叠加下一句起拍**（复用母题 `boston_chalkboard_scribble`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Brisk crisp white chalk writing numbers rapidly on a tall slate quotation board followed by a felt eraser swishing clean and wooden clip snapping shut in a quiet 1890s Boston brokerage room, pure foley, no human voice`

- 🎙️ **`[oa04_young]` 少年拉里 (`young_larry`)** （`stability=0.0` | 句后气口 `0.22s`）  
  > [excited] 别再打听公司内幕啦！你看伯灵顿铁路在黑板上连跳三格又收稳，跟上个月暴涨前节奏一模一样，五美元周薪全押上，今天稳赢！

- 🎙️ **`[oa05_clara]` 克拉拉 (`clara_ny`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [coldly] 我在纽交所电报台坐了十二年，听过一万条号称稳赚不赔的绝密小道。可真正从不说谎的，只有纸带吐出的冰冷成交价。

- 🎙️ **`[oa06_turkey]` 老火鸡帕特里奇 (`old_partridge`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [chuckles] [earthy] 小伙子，谢谢你的好意，可我一股都不卖！别忘了现在可是大牛市——华尔街赚大钱从不靠折腾，全靠看准后坐得稳！

- 🎙️ **`[oa07_cotton]` 帕西·托马斯 (`cotton_king`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [warmly] 拉里，这份绝密产区电报只给你看！棉花严重减产已成定局，快把赚钱的小麦全卖了，跟我重仓抄底，联手吞下全美市场！

- 🎙️ **`[oa08_morgan]` 银行家老威廉 (`morgan_envoy`)** （`stability=0.0` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [solemn] 摩根先生正紧急筹措救市款，可场内拆借资金一分都没了！如果你继续往下砸盘，纽交所撑不过下午两点，请高抬贵手！

- 🎙️ **`[oa09_larry]` 拉里·利文斯顿 (`livermore`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [calmly] 华尔街从来没有新鲜事，因为投机像群山一样古老。股票代码会换，可人性里的贪婪、恐惧和侥幸，一百年从未改变。

- 🎙️ **`[oa10_su]` 苏南星 (`host_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《一九二三华尔街风云：股票大作手回忆录》——八大角色零翻译腔飙戏，听懂百年交易人性与生存铁律！
