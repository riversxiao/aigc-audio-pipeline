# AUDITION_MONEY ·《《财富长跑课：〈金钱心理学〉普通人致富剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 慢火书屋八角色炉边核心试听 | `Warm fireside intimate acoustic guitar fingerpicking, soft felt piano chords, tender solo cello melody and gentle upright bass evoking a glowing autumn wood-paneled bookshop hearth and honest late-night conversation about life and money, purely acoustic instrumental, no modern drums, no percussion, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 慢火书屋八角色炉边核心试听】

- 🔊 **`[ma01_hearth]` 音效 · 独立顺播**（复用母题 `fireside_bookshop_hearth`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Warm intimate wood-paneled bookshop ambience with gentle fireplace logs crackling softly, a ceramic mug set lightly onto a scarred oak table, and soft autumn rain outside, pure foley, no human voice`

- 🎙️ **`[ma02_narr]` 故事旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [warmly] 秋雨敲打着老街转角的玻璃窗，慢火书屋里的壁炉劈啪作响。一只老黄铜怀表，一本磨毛边的蓝皮记账本，还有八张截然不同的人生账单，正悄悄摊开在炉火前。

- 🎙️ **`[ma03_chen]` 陈小川 (`young_chen`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [excited] 各位快看这条新闻！一个修了一辈子水管、扫了一辈子地的小镇老人，去世竟留下相当于几千万的积蓄；可同一座城里，顶流名校毕业的投行高管却破产了！这合理吗？

- 🎙️ **`[ma04_lu]` 陆明轩 (`banker_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [wryly] [pushback] 小伙子，别拿孤例唬人。金融是数学、杠杆和信息的修罗场，一个连财报都读不全的老人，凭什么赢过受过顶级训练的职业选手？

- 🔊 **`[ma05_watch]` 音效 · 叠加下一句起拍**（复用母题 `brass_pocket_watch_tick`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Close-up foley of a vintage brass pocket watch lid snapping open cleanly followed by steady rhythmic mechanical ticking in a quiet wooden room, pure foley, no human voice`

- 🎙️ **`[ma06_qiao]` 乔师傅 (`uncle_qiao`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [earthy] [chuckles] 陆先生，我这双摸惯扳手的手确实算不懂高深公式。我就守一条笨规矩：发工资先攒四成，大跌那年照常去公园遛弯，一晃眼，怀表走了整整三十年。

- 🎙️ **`[ma07_gu]` 顾知远 (`chronicler_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [warmly] [seriously] 这正是管钱最奇妙的地方。造大桥、做手术拼的都是绝顶智商，门外汉绝无胜算；唯独在金钱的世界里，脾气稳的普通人，可以轻松赢过管不住贪心的天才。

- 🎙️ **`[ma08_zhou]` 老周 (`fund_veteran_zhou`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [calmly] [wryly] 我管过上百亿资金，说句大实话：我这辈子看走眼的股票比看对的还多！可只要没在错的那把压上全家身家，留在牌桌上，就能等到那几匹改写命运的大黑马。

- 🎙️ **`[ma09_shen]` 沈念安 (`host_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [seriously] 纸上公式总教你满仓加杠杆才最有效率，可等你半夜陪老人冲进急诊签手术单那刻才明白，账户里趴着的那笔低息应急现金，是全天下最管用的睡觉药。

- 🔊 **`[ma10_car]` 音效 · 独立顺播**（复用母题 `luxury_car_door_thud`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Crisp close-up foley of a heavy luxury sports car door closing with a deep muted thud inside an echoing concrete parking garage followed by a key fob chime and retreating leather footsteps, pure foley, no human voice`

- 🎙️ **`[ma11_lu2]` 陆明轩 (`banker_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [sighs] [softly] 直到把最后一辆跑车开进典当行我才看清，当年我手里的钱早够活三辈子，可为了追上朋友圈里多出来的一个零，我把最输不起的安稳全押上了赌桌。

- 🎙️ **`[ma12_su]` 苏岚 (`cafe_owner_su`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [warmly] [softly] 赚钱最怕球门跟着你的脚步不断往后退。其实财富能买到最昂贵的奢侈品，从来不是街上惹眼的跑车，而是清晨推开木窗时，你能笑着决定今天怎么过。

- 🎙️ **`[ma13_chen2]` 陈小川 (`young_chen`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 原来我天天刷涨停板、算翻倍公式，焦虑的根本不是钱太少，而是把一场三十年的长跑，错当成了百米冲刺！

- 🎙️ **`[ma14_qiao2]` 乔师傅 (`uncle_qiao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [warmly] 孩子，别急着跟外头跑得最快的人较劲。留足安全垫，认清运气和风险，守住心里的知足线，时间自会在后半程替你滚出大雪球。

- 🎙️ **`[ma15_shen2]` 沈念安 (`host_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 六个秋夜，六堂最接地气的普通人致富心理课，不贩卖焦虑，不照搬洋教材，只讲能让你夜里睡得踏实的真本事。

- 🎙️ **`[ma16_gu2]` 顾知远 (`chronicler_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《财富长跑课：金钱心理学普通人致富剧》。倒上一杯热茶，坐到壁炉边来，咱们一起修一颗稳得住、睡得香、走得远的财富平常心。
