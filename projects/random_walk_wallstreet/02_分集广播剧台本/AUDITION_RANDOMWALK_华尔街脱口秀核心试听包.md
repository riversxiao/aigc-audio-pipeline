# AUDITION_RANDOMWALK ·《《华尔街脱口秀：〈漫步华尔街〉指数革命》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 华尔街脱口秀八角色试听 | `Breezy witty Manhattan acoustic jazz piano trio, warm felt upright piano swing voicings, buoyant walking upright double bass and light fingerpicked acoustic guitar evoking an evening Wall Street talk-show salon and relaxed strolls through Lower Manhattan, purely acoustic instrumental, no loud drums, no percussion, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 华尔街脱口秀八角色试听】

- 🔊 **`[rwa01_rain]` 音效 · 独立顺播**（复用母题 `wall_street_salon_rain`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Warm intimate Manhattan lower Wall Street salon ambience with light evening rain tapping tall arched glass windows, a heavy glass tumbler gently set onto polished oak, and crisp index cards tapped neatly on a studio table, pure foley, no human voice`

- 🎙️ **`[rwa02_narr]` 节目旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 曼哈顿下城华灯初上，细雨敲打着华尔街古老的石拱窗。暖黄台灯下，一只黄铜飞镖盘刚刚摆上木桌——今晚，我们要拆穿金融圈最贵的一场魔术。

- 🔊 **`[rwa03_dart]` 音效 · 叠加下一句起拍**（复用母题 `dartboard_thud_toss`） （时长 `2.6s` | 句后留白 `0.18s`）  
  Prompt: `Close-up studio foley of three weighted brass darts whistling briefly through quiet room air and landing one by one with crisp solid thuds into a tightly packed sisal cork dartboard, pure foley, no human voice`

- 🎙️ **`[rwa04_lin]` 林致远 (`prof_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [wryly] [chuckles] 给动物园猩猩蒙上眼朝股市名单扔飞镖，长期居然能打平甚至赢过穿定制西装的大师——更妙的是，猩猩还不收高额管理费！

- 🎙️ **`[rwa05_victor]` 维克多 (`manager_victor`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [condescending] 林教授，飞镖段子听着过瘾，可我手下三十位名校研究员天天拆财报、访高管，难道专业眼光还比不过一只猩猩？

- 🎙️ **`[rwa06_ray]` 老雷 (`chartist_ray`)** （`stability=0.0` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [excited] 别信西装革履的研报！财报会化妆，唯有K线最实在！瞧这标准头肩顶加回踩颈线，主力脚印清清楚楚印在图纸上呢！

- 🎙️ **`[rwa07_zhou]` 老周 (`boss_zhou`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [sighs] 办厂挣钱是一分一厘抠出来的，买明星基金交学费倒是一把全送了出去！去年冠军今年垫底，亏的咋全是我的本金？

- 🎙️ **`[rwa08_wu]` 吴姐 (`claire_wu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [calmly] [wryly] 别被合同里区区百分之二的年费骗了！按三十年复利一滚，这点看似不起眼的费率，能悄悄吃掉你最后将近一半的养老家底。

- 🎙️ **`[rwa09_kevin]` 凯文 (`young_kevin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [curious] 各位先别吵，我刚领了第一笔年终奖！到底有没有一种不盯盘、少交费、还能安心睡大觉的普通人理财笨办法？

- 🎙️ **`[rwa10_su]` 苏漫 (`host_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《华尔街脱口秀》！卸掉晦涩翻译腔，用最痛快的相声账本，听懂《漫步华尔街》背后的指数革命真相。
