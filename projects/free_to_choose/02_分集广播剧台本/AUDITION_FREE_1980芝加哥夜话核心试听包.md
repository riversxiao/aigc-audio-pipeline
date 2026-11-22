# AUDITION_FREE ·《《1980芝加哥夜话：〈自由选择〉商业思想剧场》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1980芝加哥夜话八角色试听 | `Warm intimate 1980 Chicago documentary acoustic chamber-jazz, soft felt upright piano chords, gentle walking upright double bass and warm lyrical acoustic cello evoking a twilight Hyde Park study overlooking Lake Michigan, purely acoustic instrumental, no loud drums, no percussion, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1980芝加哥夜话八角色试听】

- 🔊 **`[fa01_rain]` 音效 · 独立顺播**（复用母题 `chicago_study_rain`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Warm cozy 1980 Chicago Hyde Park wood-paneled study ambience with soft autumn lake rain tapping against tall sash windows, a ceramic coffee mug gently set onto an oak desk, and crisp notepad pages turning, pure foley, no human voice`

- 🎙️ **`[fa02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一九八〇年深秋，芝加哥密歇根湖晚风微凉。通胀飙破两位数的历史十字路口上，一场关乎每个人钱包、饭碗与选择的思想夜话，在暖灯下开场了。

- 🔊 **`[fa03_pencil]` 音效 · 叠加下一句起拍**（复用母题 `wooden_pencil_sketch`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Crisp close-up foley of a yellow cedar wooden pencil twisting smoothly inside a brass hand sharpener followed by brisk graphite sketching across ledger paper and two light wooden taps on a desk, pure foley, no human voice`

- 🎙️ **`[fa04_milton]` 米尔顿·弗里德曼 (`milton_friedman`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 全世界找不出哪个人能独自造出这支一毛钱的黄木铅笔；可没设任何总司令，价格却悄悄指挥上万陌生人替你把它摆上了书桌。

- 🎙️ **`[fa05_fang]` 老方 (`boss_fang`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 花自个儿钱买把小葱我还得挑两遍呢！可花公家的钱给别人办事，既不心疼钱又不管好不好用，这笔账能不浪费吗？

- 🎙️ **`[fa06_vance]` 万斯专员 (`regulator_vance`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 教授，说市场万能很轻松。可要是拆掉联邦牌照门槛、药监审批和福利救济署，消费者吃了亏、穷人没着落，谁来兜底？

- 🎙️ **`[fa07_alex]` 阿历克斯 (`young_alex`)** （`stability=0.5` | 句后气口 `0.2s`）  
  > [excited] 我在香港两台二手缝纫机就能起步做外贸，怎么到了芝加哥，连开辆机场出租车都得先花买房的钱去买块铁皮牌照？

- 🎙️ **`[fa08_chen]` 陈老师 (`teacher_chen`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [sighs] [seriously] 街口餐馆不好吃我能换一家，可我每年照样交房产税，为什么我家孩子偏偏被一道邮编高墙，锁死在糟糕学校里？

- 🎙️ **`[fa09_rose]` 罗丝·弗里德曼 (`rose_friedman`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [warmly] [calmly] 评判一项政策好不好，绝不能光看它起草时有多动听的好心，而要看它十年后究竟让普通人更体面，还是更无助。

- 🎙️ **`[fa10_lin]` 林晚晴 (`host_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《1980芝加哥夜话》——彻底卸掉晦涩翻译腔，用中国人的家常细账，听懂自由、物价与选择的底层商业常识。
