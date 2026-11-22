# AUDITION_WEALTH ·《《1776爱丁堡夜话：〈国富论〉商业思想剧场》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 爱丁堡牡蛎俱乐部试听 | `Warm intimate 18th-century Scottish Enlightenment chamber music, lyrical solo cello, gentle classical baroque harpsichord arpeggios and warm acoustic strings evoking a candlelit Edinburgh parlor debate, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 爱丁堡牡蛎俱乐部试听】

- 🔊 **`[wa01_hearth]` 音效 · 独立顺播**（复用母题 `edinburgh_tavern_hearth`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Warm cozy 18th-century Edinburgh wooden tavern parlor ambience with crackling stone hearth fire, two pewter mugs gently clinking on an oak table, and soft distant evening rain on leaded glass, pure foley, no human voice`

- 🎙️ **`[wa02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [warmly] 一七七六年三月，爱丁堡老城海风微凉。牡蛎俱乐部摇曳的烛光里，一本彻底改写人类财富命运的大书刚刚付印，而书里藏着的，全是普通人挣钱过日子的实在门道。

- 🔊 **`[wa03_pins]` 音效 · 叠加下一句起拍**（复用母题 `pin_factory_clatter`） （时长 `3.2s` | 句后留白 `0.18s`）  
  Prompt: `Brisk rhythmic 18th-century brass pin-making workshop foley with crisp wire snipping, light precise miniature hammer taps, and hundreds of tiny gleaming brass pins cascading into a wooden sorting tray, pure foley, no human voice`

- 🎙️ **`[wa04_boss]` 老麦考利 (`boss_macaulay`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [earthy] [chuckles] 姑娘你算笔实在账！我厂里十个毛头小伙各盯一道工序，一天能砸出四万八千根亮晶晶的扣针；要是一个人从头干到尾，一天连二十根都凑不齐！

- 🎙️ **`[wa05_smith]` 亚当·斯密 (`adam_smith`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [warmly] [calmly] 所以大伙儿每天端上餐桌的面包和牛肉，靠的从来不是肉铺老板和面包师傅发善心，而是人家也得挣钱养家。你跟他谈慈悲他未必理你，可谈成一笔双赢买卖，天没亮面包就烤好了。

- 🎙️ **`[wa06_watt]` 詹姆斯·瓦特 (`james_watt`)** （`stability=0.0` | 句后气口 `0.22s`）  
  > [angry] 格拉斯哥老行会根本不是嫌我手艺差！他们就是怕我改良的蒸汽机抢了老作坊的饭碗，硬拿规矩卡死不让我开店！

- 🎙️ **`[wa07_lord]` 东印度商董 (`merchant_lord`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [condescending] 笑话！要是不给大公司特许垄断、不对外国货加满关税，咱们国家的黄金岂不都流进外人腰包了？

- 🎙️ **`[wa08_hume]` 大卫·休谟 (`david_hume`)** （`stability=0.5` | 句后气口 `0.26s`）  
  > [chuckles] [warmly] 照老爷这套算盘，西班牙抢了美洲一船船白银，怎么反倒越抢越穷？金银只是筹码，老百姓手里买得起衣食住行，那才叫真富！

- 🎙️ **`[wa09_smith_end]` 亚当·斯密 (`adam_smith`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [solemn] [warmly] 欢迎走进《1776爱丁堡夜话》——咱们卸掉晦涩翻译腔，用最接地气的中国话，把《国富论》听成一门活生生的赚钱与看世道学问。
