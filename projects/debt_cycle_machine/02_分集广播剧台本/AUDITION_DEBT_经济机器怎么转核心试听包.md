# AUDITION_DEBT ·《《经济机器怎么转：〈原则与大债务危机〉周期剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 经济机器与大债务周期八角色核心试听 | `Steady cyclical macro documentary minimalist piano arpeggio, warm sustained cello and subtle chamber string swell evoking precision brass clockwork gears and long-horizon economic rhythm, purely acoustic instrumental, no pop drums, no modern EDM beat, no singing, no vocals` | 70s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 经济机器与大债务周期八角色核心试听】

- 🔊 **`[da01_gears]` 音效 · 独立顺播**（复用母题 `brass_clockwork_gears`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Crisp close-up mechanical foley of an antique exposed brass clockwork gear machine turning smoothly with interlocking brass cogwheels clicking and a steady resonant pendulum ticking on a wooden study desk, pure foley, no human voice`  
  *导演备注：黄铜三层齿轮钟开场*

- 🎙️ **`[da02_narr]` 周期旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [calmly] 滨江夜色深沉，金融区摩天楼群灯火如星。红木桌正中，一台精密的黄铜三层齿轮机滴答作响，正把人类百年的繁荣与萧条拆解成听得见心跳的机械节奏。

- 🎙️ **`[da03_gu]` 顾知远 (`strategist_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 别被新闻里满天飞的宏观黑话吓住。经济机器说穿了就靠三股力量推动：底层的生产率慢跑、中层的信贷小弹簧，还有最外圈七十五年一轮的大债务潮。

- 🎙️ **`[da04_su]` 苏晓宁 (`reporter_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [curious] 顾老师，大家都说借钱像装在经济里的弹簧，可我跑了一整年工厂和银行，最纳闷的是：为什么昨天满街抢着扩张，明天全城突然喊缺钱？

- 🔊 **`[da05_factory]` 音效 · 叠加下一句起拍**（复用母题 `factory_cnc_floor`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Grounded industrial workshop ambience of precision CNC lathe spindles humming steadily in the background with stainless steel calipers clinking onto a metal workbench and a paper order slip tearing cleanly, pure foley, no human voice`

- 🎙️ **`[da06_chen]` 老陈 (`boss_chen`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 晓宁你问到点子上了！我靠银行贷款买了八台数控机床，一开工全街餐馆都跟着红火；可谁想到行情一转凉，银行收伞比变天还快啊！

- 🎙️ **`[da07_lu]` 陆维舟 (`banker_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [wryly] [calmly] 老陈可别光骂银行嫌贫爱富。晴天你厂房估值翻倍，我敲键盘给你放信贷，你的支出立马成了全城收入；雨天抵押物缩水，我替储户兜底只能抽贷。

- 🎙️ **`[da08_xu]` 许姐 (`saver_xu`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [seriously] 你们动不动几千万往外贷，可落到我们普通家庭饭桌上，就怕两件事：一是物价涨得工资追不上，二是盲目加杠杆把半辈子积蓄全搭进泡沫里。

- 🎙️ **`[da09_gu_mid]` 顾知远 (`strategist_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [calmly] 许姐说得透亮！一个人的支出永远是另一个人的收入。借钱扩张时，全城把未来十年的收入折叠搬到今天花，人人觉得自己是天才；等到还债那天，骨牌反着倒塌才见真章。

- 🎙️ **`[da10_lin]` 林清岚 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 这正是长短期债务周期最凶险的分野。五到八年的短周期靠利率油门刹车就能调顺，可等债务滚成大山、利息砍到零都没人敢借时，推软绳子的真考验才刚开始。

- 🎙️ **`[da10b_xu]` 许姐 (`saver_xu`)** （`stability=0.5` | 句后气口 `0.2s`）  
  > [curious] 利率贴地、银行惜贷、老百姓拼命还债缩开支——到那一步，全社会难道真就掉进无解的死胡同了吗？

- 🔊 **`[da11_cb]` 音效 · 独立顺播**（复用母题 `central_bank_press_bell`） （时长 `3.0s` | 句后留白 `0.2s`）  
  Prompt: `Hushed stately central bank conference hall foley with a heavy leather policy binder closing firmly on a polished table, a glass tumbler tapped softly, and a distant deep city clocktower bell tolling once, pure foley, no human voice`

- 🎙️ **`[da12_pei]` 裴明轩 (`advisor_pei`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [solemn] 撞上百年大债顶点，央行桌前只剩四味猛药：紧缩、违约、财富转移和印钞。冰水倒多成通缩萧条，沸水倒多变恶性通胀，把四招配成温水，才叫和谐去杠杆。

- 🎙️ **`[da13_chen2]` 老陈 (`boss_chen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] 国家有四张底牌，可咱们开小厂、领死工资过日子的老百姓，手头既没印钞机也没加息键，撞上周期巨浪到底靠什么活下来？

- 🎙️ **`[da14_gu2]` 顾知远 (`strategist_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] [calmly] 只需死守三条永恒铁律：别让债务跑赢收入，别让收入跑赢生产率，用一辈子的手艺、现金流垫子和四季衣柜的全天候视野安稳渡海。

- 🎙️ **`[da15_su2]` 苏晓宁 (`reporter_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《经济机器怎么转：〈原则与大债务危机〉周期剧》——八位角色零翻译腔飙戏，用最实在的家常细账，带你听懂信贷弹簧与百年周期的底层法则。
