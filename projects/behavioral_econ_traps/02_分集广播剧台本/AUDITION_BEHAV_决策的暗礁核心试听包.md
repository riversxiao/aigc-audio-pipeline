# AUDITION_BEHAV ·《《决策的暗礁：行为经济学与〈思考，快与慢〉剧场》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 决策的暗礁八角色核心试听 | `Curious warm modern documentary chamber score, intimate felt piano chords, gentle pulsing pizzicato strings, warm subtle wooden marimba resonance and soft upright bass evoking a twilight harbor study cafe and cognitive experiment table, purely acoustic instrumental, no heavy drums, no modern EDM beat, no singing, no vocals` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 决策的暗礁八角色核心试听】

- 🔊 **`[ba01_cafe]` 音效 · 独立顺播**（复用母题 `lab_cafe_espresso_ambience`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Warm cozy harbor-side study cafe foley with gentle pour-over coffee streaming into a porcelain mug, a brass tabletop hourglass turning smoothly onto oak wood, and soft dry sand trickling inside glass, pure foley, no human voice`

- 🎙️ **`[ba02_narr]` 剧场旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [warmly] 港湾暮色降临，灯塔巷那盏琥珀色台灯亮了起来。楼上是认知决策实验室，楼下连着咖啡馆与烟火菜场，每天都在上演一场场你以为自己很理智的心理暗礁大戏。

- 🎙️ **`[ba03_shen]` 沈明远教授 (`prof_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.18s`）  
  > [warmly] 各位先别急着点单，做道三秒钟热身题！一根球棒加一颗球卖一块一毛钱，球棒比球贵一块钱，请问这颗球卖多少钱？

- 🎙️ **`[ba04_zhou]` 周小川 (`investor_zhou`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.16s`）  
  > [excited] 这不送分题吗？一毛钱！我闭着眼都能算出来！

- 🔊 **`[ba05_stop]` 音效 · 叠加下一句起拍**（复用母题 `stopwatch_buzzer_click`） （时长 `2.6s` | 句后留白 `0.18s`）  
  Prompt: `Crisp close-up mechanical stopwatch metal crown clicking cleanly to a halt followed by a dry-erase marker circling briskly on a smooth lab whiteboard and the plastic cap snapping shut, pure foley, no human voice`

- 🎙️ **`[ba06_su]` 苏小禾 (`grad_su`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [chuckles] 秒表停！零点七秒抢答，恭喜周老板精准触礁！如果球卖一毛，球棒贵一块就是一块一，加起来可是一块二——正确答案是五分钱！

- 🎙️ **`[ba07_lin]` 林知微 (`pm_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [curious] 沈教授，我们做互联网产品天天盯漏斗数据，可为什么像小川这样的聪明人，一进购物节和股票市场，照样被直觉牵着鼻子走？

- 🎙️ **`[ba08_chen]` 陈老钱 (`boss_chen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [earthy] [chuckles] 姑娘你问对人了！我这咖啡馆中杯二十八、大杯三十二、超大杯三十五，你以为买大杯捡了便宜，其实中杯就是我特意摆出来的定价锚！

- 🎙️ **`[ba09_mei]` 梅姨 (`aunt_mei`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [wryly] 老陈你少得意，你一进股市还不是一样？赚五百急得直跺脚赶紧卖，亏三千反而死扛着说不卖就不算亏，手比嘴诚实多了！

- 🎙️ **`[ba10_zhou]` 周小川 (`investor_zhou`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [angry] 梅姨你别光说老陈啊！上次那部大烂片演了二十分钟我就想走，是谁死按着我说票钱八十块都花了，硬坐满两小时才算回本的？

- 🎙️ **`[ba10b_su]` 苏小禾 (`grad_su`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 还不止呢！刚发到小川哥手里的二十块马克杯，三分钟后他就敢叫价五十才肯卖；一提雨夜开车，他又拍胸脯说自己车技稳居全城前两成！

- 🎙️ **`[ba10c_lin]` 林知微 (`pm_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [wryly] [chuckles] 最绝的是上周那家网红茶饮暴雷，小川当场拍桌说半年前就看穿了——结果我一翻群聊记录，他当年差点拿积蓄去交加盟费！

- 🔊 **`[ba11_anchor]` 音效 · 独立顺播**（复用母题 `brass_anchor_desk_thud`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Solid miniature brass anchor setting down firmly onto an oak study table followed by a bright silver coin flicking cleanly into the air, spinning rapidly on wood, and settling flat, pure foley, no human voice`

- 🎙️ **`[ba12_xu]` 许南风博士 (`dr_xu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [wryly] 别互相揭短了！从损失厌恶、心理账户、沉没成本到事后诸葛亮，靠苦口婆心说教永远斗不过大脑偷懒；会设计默认选项和事前验尸，才能顺着人性绕开暗礁。

- 🎙️ **`[ba12b_chen]` 陈老钱 (`boss_chen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] 这话说透了！以前觉得吃亏是自己运气背，听完沈教授和许博士这几场桌上实验才明白，全是脑回路里藏着看不见的暗礁！

- 🎙️ **`[ba12c_mei]` 梅姨 (`aunt_mei`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [warmly] [chuckles] 不光少交智商税，连买菜、存钱、买保险、劝家里孩子挑工作，这一套避礁法子全都用得上，听着又过瘾又解气！

- 🎙️ **`[ba13_shen]` 沈明远教授 (`prof_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [warmly] 桌上的黄铜小锚、沙漏和棋盘已经摆好。这一季六场真人实验，带你一层层看穿快脑和慢脑的博弈，学会普通人拿来就能用的聪明决策清单。

- 🎙️ **`[ba14_lin]` 林知微 (`pm_lin`)** （`stability=0.5` | 句后气口 `0.55s`）  
  > [warmly] 告别晦涩翻译腔，把实验室搬进烟火街巷！欢迎走进八角色行为经济学心理剧——《决策的暗礁》。第一幕实验，现在开场！
