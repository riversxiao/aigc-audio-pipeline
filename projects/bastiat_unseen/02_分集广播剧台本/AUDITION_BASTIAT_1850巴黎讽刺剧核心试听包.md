# AUDITION_BASTIAT ·《《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1850巴黎街角与国民议会核心试听 | `Sparkling witty 1850 Parisian salon chamber string quartet, crisp playful pizzicato cello pulse, light articulated classical fortepiano arpeggios and nimble violin phrasing evoking lively French intellectual satire, purely acoustic chamber instrumental, no modern drums, no pop beat, no singing, no vocals, no Chinese instruments` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1850巴黎街角与国民议会核心试听】

- 🔊 **`[ba01_window]` 音效 · 独立顺播**（复用母题 `broken_shop_window`） （时长 `2.6s` | 句后留白 `0.22s`）  
  Prompt: `Sudden crisp impact of a small tossed stone shattering a large 1850 storefront glass window pane cleanly with glittering glass shards tinkling onto a cobblestone sidewalk, pure foley, no human voice`

- 🎙️ **`[ba02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一八五零年巴黎街头，一块值六法郎的面包店玻璃刚被砸碎，经济学史上最辛辣爆笑的议会讽刺大戏便热热闹闹拉开了帷幕。

- 🎙️ **`[ba03_baker]` 老博诺姆 (`baker_bonhomme`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [angry] 熊孩子一石头砸碎我六法郎的大玻璃，街坊还拍手夸我救活了玻璃匠——那我原本打算买新皮鞋的六法郎算谁的？

- 🎙️ **`[ba04_luc]` 吕克 (`apprentice_luc`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [excited] 哈哈，我上午刚替大叔装完玻璃赚了六法郎，下午回鞋铺一翻账本才听说——咱鞋铺平白无故丢了一单皮鞋买卖！

- 🔊 **`[ba05_gavel]` 音效 · 叠加下一句起拍**（复用母题 `parliament_gavel_hall`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Resonant grand 1850 stone assembly hall acoustics with three crisp authoritative wooden chairman gavel strikes on an oak podium followed by thick legislative parchment pages rustling, pure foley, no human voice`

- 🎙️ **`[ba06_candle]` 杜邦会长 (`candle_boss`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [dramatically] 各位议员！法兰西蜡烛业正惨遭一个卑鄙外国对手零元恶意倾销——它的名字叫太阳！恳请立刻立法钉死全国所有窗户！

- 🎙️ **`[ba07_mont]` 蒙托邦议员 (`deputy_mont`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [condescending] 说得太妙了！最好再下令把通往波尔多的铁路故意挖断一截，客栈、马车夫和搬运工立刻全有活干，全法国一夜暴富！

- 🎙️ **`[ba08_claire]` 玛丽夫人 (`madame_claire`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [sarcastic] [chuckles] 照议员这套高招，我大白天钉死窗户点蜡烛织布多掏的冤枉钱，全是从女工工钱和街坊面包钱里硬抠出来的！

- 🎙️ **`[ba09_su]` 苏晚星 (`host_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 巴斯夏议员，一百七十多年过去了，怎么换件现代马甲，当年您骂过的糊涂账今天照样有人拼命鼓掌叫好呢？

- 🎙️ **`[ba10_bastiat]` 弗雷德里克·巴斯夏 (`bastiat`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [wryly] [chuckles] 因为坏经济学家只盯眼前的明账，好经济学家才算背后的暗账！欢迎走进一八五零巴黎议会讽刺剧，咱们笑着拆穿一切歪理！
