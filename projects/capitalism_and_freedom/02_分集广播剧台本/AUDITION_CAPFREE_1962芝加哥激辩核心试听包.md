# AUDITION_CAPFREE ·《《1962芝加哥激辩：〈资本主义与自由〉》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1962芝加哥深夜激辩八角色精华试听 | `Warm 1962 Chicago late-night intellectual acoustic jazz piano, warm walking upright double bass and mellow legato chamber strings evoking autumn streetlamps outside a Gothic Hyde Park seminar hall, purely acoustic instrumental, no loud drums, no percussion, no modern beat, no singing, no vocals` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1962芝加哥深夜激辩八角色精华试听】

- 🔊 **`[ca01_rain]` 音效 · 独立顺播**（复用母题 `hydepark_chalk_rain`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Cozy 1962 University of Chicago Gothic seminar room ambience with light autumn rain tapping leaded glass windows, crisp white chalk writing briskly on a slate blackboard, and an oak chair creaking gently, pure foley, no human voice`

- 🎙️ **`[ca02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一九六二年深秋，芝加哥海德公园灯火通明。在全美笃信大政府微调与黄金平价的年代，一场改写半个世纪制度常识的深夜激辩，正式打响。

- 🎙️ **`[ca03_qiao]` 乔知微 (`researcher_qiao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [curious] 各位，今晚咱们把话说透！华盛顿总说只要选票还在，国家多管一点经济、多批几道执照、多印点财政预算，就能把老百姓护得严严实实，真是这样吗？

- 🎙️ **`[ca04_keene]` 基恩顾问 (`advisor_keene`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [seriously] 乔女士，现代社会这么复杂，工厂排污、经济起落、穷人看不起病，全靠市场冷冰冰算账行吗？政府必须果断出手，替普通人兜住底线！

- 🔊 **`[ca05_whistle]` 音效 · 叠加下一句起拍**（复用母题 `referee_whistle_gavel`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Sharp brief vintage brass sports referee whistle blast echoing faintly across an empty court transitioning cleanly into a heavy oak committee gavel striking a wooden sound block twice in a quiet hall, pure foley, no human voice`

- 🎙️ **`[ca06_friedman]` 米尔顿·弗里德曼 (`prof_friedman`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [warmly] [wryly] 基恩先生，球场上离不了裁判！可裁判的本分是站在边线吹哨、守好规矩；一旦裁判自己套上球衣带球冲锋，全场的比赛还能公平踢下去吗？

- 🎙️ **`[ca07_samson]` 萨姆森 (`grad_samson`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [excited] 教授，这比喻太狠了！可要是全城就剩下一个超级大老板发工资、管印刷机，就算纸面上写着人人有言论自由，明天真敢唱反调的又有几个？

- 🎙️ **`[ca08_friedman]` 米尔顿·弗里德曼 (`prof_friedman`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [calmly] 问到根子上了！分散的钱袋子，就是普通人挺直腰杆的防火墙。东街老板不爱听你的真话，西街顾客只要认你的好手艺，照样能给你一碗热饭吃。

- 🎙️ **`[ca09_aldrich]` 奥尔德里奇行长 (`banker_aldrich`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.2s`）  
  > [solemn] 慢着，小生意可以由着市场折腾！可三十五美元换一盎司黄金的汇率铁锚、中央银行相机决断的大权，你们芝加哥书生也敢说交给死板规则和浮动汇率？

- 🎙️ **`[ca10_friedman]` 米尔顿·弗里德曼 (`prof_friedman`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [seriously] 老奥尔德里奇，硬撑固定汇率就像发高烧按着体温计水银柱不准涨！布雷顿森林撑不了十年必会裂开，与其等崩盘，不如给印钞机立下铁规则。

- 🔊 **`[ca11_coffee]` 音效 · 独立顺播**（复用母题 `chicago_lounge_coffee`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Intimate 1962 Chicago late-night neighborhood coffee lounge foley with a ceramic mug stirred gently with a metal spoon, a porcelain saucer clinking onto a polished mahogany table, and crisp notepad pages turning, pure foley, no human voice`

- 🎙️ **`[ca12_han]` 老韩 (`barber_han`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [earthy] [chuckles] 我一街角理发匠不懂大理论，可我徒弟剪头街坊抢着夸，就因为没交够老行会的高价考证费不准动剪刀，这哪是护着顾客，分明是挡新人财路！

- 🎙️ **`[ca13_claire]` 克莱尔 (`mother_claire`)** （`stability=0.5` | 句后气口 `0.2s`）  
  > [sighs] [seriously] 我这当单亲妈的也说句掏心窝话：别派督察员天天查我衣柜，更别让我多加班反被扣光补助！给我一张负所得税和教育券，我照样靠双手把娃养体面！

- 🎙️ **`[ca14_keene]` 基恩顾问 (`advisor_keene`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [pushback] 听着都痛快，可万一市场拆掉了保护伞，普通家庭扛不住大风大浪、工厂排污没人管、衰退来了没人救，华盛顿真能袖手旁观吗？

- 🎙️ **`[ca15_friedman]` 米尔顿·弗里德曼 (`prof_friedman`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [warmly] 绝不是袖手旁观，而是看清每条政策的真实激励与代价！六个晚上，咱们把听起来最动听的口号统统摆上桌，一笔一笔把账算到透亮！

- 🎙️ **`[ca16_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 从海德公园的哥特拱窗，到华盛顿的黄金听证走廊，再到芝加哥南区的理发铺与厨房餐桌，八位鲜活角色针锋相对，六夜燃爆思辨火花。

- 🎙️ **`[ca17_qiao]` 乔知微 (`researcher_qiao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《一九六二芝加哥激辩：资本主义与自由》——卸掉冰冷翻译腔，把听起来很美的理想放进激励与成本的显微镜下，听懂市场边界与公民常识。
