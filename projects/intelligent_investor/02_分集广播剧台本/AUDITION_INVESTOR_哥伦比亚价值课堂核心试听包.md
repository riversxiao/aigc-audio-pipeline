# AUDITION_INVESTOR ·《《哥伦比亚价值课堂：〈聪明的投资者〉》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 哥伦比亚价值课堂八角色试听 | `Calm warm 1950s New York academic study pure acoustic chamber music, soft felt acoustic piano chords, warm lyrical solo cello and gentle walking jazz upright double bass evoking an autumn dusk lecture hall at Columbia University, purely acoustic instrumental, no drums, no percussion, no vocals, no singing, no Chinese instruments` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 哥伦比亚价值课堂八角色试听】

- 🔊 **`[ia01_chalk]` 音效 · 独立顺播**（复用母题 `columbia_chalkboard_evening`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Warm 1950s Columbia University evening lecture hall ambience with a heavy oak door closing softly, crisp white chalk writing steadily on a slate chalkboard, and thick annual report pages turning gently, pure foley, no human voice`

- 🎙️ **`[ia02_narr]` 历史纪录片旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一九五一年深秋，纽约哥伦比亚大学商学院的晚间课堂灯火温暖。五十八岁的华尔街教父本杰明·格雷厄姆拿起粉笔，开启了一场守护普通人钱袋子的理性思辨。

- 🎙️ **`[ia03_graham]` 本杰明·格雷厄姆 (`graham`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] [calmly] 股票从来不是屏幕上乱跳的红绿代码，它是背后活生生的实业切片；把本金安全和足够便宜放在头一位，才配叫真正的投资。

- 🔊 **`[ia04_knock]` 音效 · 叠加下一句起拍**（复用母题 `mr_market_door_knock`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Brisk impatient knuckles knocking loudly on a wooden diner office door while a small brass shop bell jingles excitedly, followed by the heavy door calmly latching shut, pure foley, no human voice`

- 🎙️ **`[ia05_chen]` 老陈 (`boss_chen`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [sighs] 我盘家餐馆都得把厨房账本查三遍，可去年听风口炒股，仨月就亏掉我两家店一年的辛苦钱！

- 🎙️ **`[ia06_brad]` 布拉德 (`broker_brad`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [wryly] 教授，等您慢吞吞翻完旧年报，热门风口早翻倍啦！华尔街拼的是先手眼光和行情气势，谁耐烦守着您那套笨账本？

- 🎙️ **`[ia07_warren]` 青年巴菲特 (`young_warren`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [excited] 教授，我把三千页企业手册翻了个底朝天，真找到几家半价甩卖的好底子——可要是遇上能滚二十年雪球的绝佳好生意呢？

- 🎙️ **`[ia08_arthur]` 亚瑟先生 (`old_arthur`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [solemn] [sighs] 一九二九年秋天，连门口擦鞋的小伙都在给我荐股；后来杠杆一爆仓，半生积蓄一夜清零，永远别拿养老钱进赌场。

- 🎙️ **`[ia09_claire]` 林雪 (`claire_lin`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [curious] 我每天上班带娃，压根没空盯盘看线，就想学套不踩坑的稳健笨办法，跑赢物价，踏踏实实攒下孩子的学费。

- 🎙️ **`[ia10_su]` 苏知夏 (`host_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《哥伦比亚价值课堂》——零翻译腔、不讲玄学，用家常细账听懂格雷厄姆跨越百年的投资常识与人性定力。
