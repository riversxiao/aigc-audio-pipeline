# AUDITION_SCHUMPETER ·《《1911维也纳风暴：〈经济发展理论〉创新剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1911维也纳星火咖啡馆试听 | `Warm sparkling 1911 Vienna expressive romantic string quartet and lively grand piano arpeggios, crisp lyrical violin dialogue over supple cello pulse evoking bright intellectual sparks in a candlelit Ringstrasse coffeehouse, purely acoustic chamber instrumental, no modern pop drums, no percussion kit, no vocals, no singing, no Chinese instruments` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1911维也纳星火咖啡馆试听】

- 🔊 **`[sc00_01_cafe]` 音效 · 独立顺播**（复用母题 `vienna_coffeehouse_chime`） （时长 `3.0s` | 句后留白 `0.2s`）  
  Prompt: `Warm 1911 Vienna Ringstrasse coffeehouse parlor ambience with a delicate porcelain demitasse cup set gently on a saucer, silver spoon stirring espresso softly, wooden chair creaking, and a distant street tram bell outside arched glass windows, pure foley, no human voice`

- 🎙️ **`[sc00_02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一九一一年秋夜，维也纳环形大道煤气路灯亮起。二十八岁的天才教授熊彼特带着《经济发展理论》走进星火咖啡馆，一场改写现代商业命运的思想风暴就此引爆。

- 🎙️ **`[sc00_03_anna]` 安娜 (`clara_vienna`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [wryly] [chuckles] 诸位快别光盯着瓷杯啦，瞧瞧窗外！马车夫气得挥鞭子，银行家算盘打得飞起，全冲着那个满手黑机油的毛头小子！

- 🔊 **`[sc00_04_engine]` 音效 · 叠加下一句起拍**（复用母题 `motorcar_engine_ignition`） （时长 `3.2s` | 句后留白 `0.18s`）  
  Prompt: `Early 1911 gasoline motorcar metal hand crank turning firmly, brass ignition clicking, engine sputtering twice before roaring alive with energetic rhythmic pistons and clinking steel wrenches inside a timber workshop, pure foley, no human voice`

- 🎙️ **`[sc00_05_leo]` 莱奥 (`inventor_leo`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [excited] 我兜里连三个克朗都掏不出，可这台轻量内燃机汽车跑起来比四匹骏马快三倍！只要谁敢借我信贷，一年之内我掀翻整条老马车街！

- 🎙️ **`[sc00_06_hans]` 老汉斯 (`coach_maker`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] 我家三代给维也纳造皇家四轮马车，橡木严丝合缝、黄铜擦得锃亮，年年稳稳养活十五个伙计，怎么就被铁盒子搅翻了天？

- 🎙️ **`[sc00_07_baron]` 冯·克劳斯男爵 (`guild_baron`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [condescending] 荒唐！若任由没祖产、没根基的修车疯子到处搅局，旧铁路和马车行会几十年攒下的体面秩序岂不全毁了？

- 🎙️ **`[sc00_08_karl]` 卡尔行长 (`banker_karl`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [calmly] 男爵，商业银行不是旧砖头和旧房产的看门狗——这笔凭空创造的五万克朗新信贷，我决定签给莱奥！

- 🎙️ **`[sc00_09_schump]` 约瑟夫·熊彼特 (`schumpeter`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [seriously] [warmly] 诸位记住：你把一万辆驿站马车首尾连在一起，也绝对变不出一列火车！真正的增长，靠的是企业家砸碎旧平衡的创造性破坏！

- 🎙️ **`[sc00_10_cheng]` 程岚 (`host_cheng`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《1911维也纳风暴》——彻底告别晦涩翻译腔，八角色沉浸飙戏，用大白话听透熊彼特的创新与破局密码！
