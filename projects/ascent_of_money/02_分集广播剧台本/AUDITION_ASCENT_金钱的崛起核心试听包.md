# AUDITION_ASCENT ·《《金钱的崛起：从美第奇银行到现代华尔街》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 五千年金融史八角色核心试听 | `Sweeping European historical documentary chamber strings, delicate Renaissance lute accents, warm expressive solo cello and crisp wooden harpsichord pulse evoking golden twilight over the Arno River and a Florentine banking ledger hall, purely acoustic instrumental, no pop drums, no percussion, no singing, no vocals, no Chinese xianxia instruments` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 五千年金融史八角色核心试听】

- 🔊 **`[aa01_clay]` 音效 · 独立顺播**（复用母题 `clay_tablet_quill`） （时长 `2.8s` | 句后留白 `0.22s`）  
  Prompt: `Close-up dry foley of a sharpened reed stylus pressing crisp wedge marks into damp clay transitioning into a goose-quill pen scratching neatly across heavy parchment ledger paper, pure foley, no human voice`

- 🎙️ **`[aa02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 四千年前的两河流域，太阳还没铸出第一枚金币，一块巴掌大的晒干泥巴借条，就已经悄悄转动了人类财富的齿轮。

- 🎙️ **`[aa03_lin]` 林清晏 (`archivist_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 欢迎走进世界金融档案馆！这桌上摆着巴比伦泥板、美第奇大账本、威尼斯羊皮纸国债，还有阿姆斯特丹最早的远洋船票股票。

- 🎙️ **`[aa04_zhou]` 老周 (`homeowner_zhou`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 我说林馆长、沈教授，我一个开小厂子背房贷的实在人，看这些老古董干嘛？它们跟我每个月算流水还按揭真有关系？

- 🎙️ **`[aa05_shen]` 沈知行 (`historian_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [warmly] 老周，关系可大着呢！你手机里每一次扫码转账、每一笔房贷分期，往上倒推几百年，都能在佛罗伦萨和阿姆斯特丹找到老祖宗。

- 🔊 **`[aa06_florin]` 音效 · 叠加下一句起拍**（复用母题 `florin_gold_scales`） （时长 `2.6s` | 句后留白 `0.18s`）  
  Prompt: `Crisp foley of heavy gold florin coins dropping gently onto a small Renaissance brass balance scale pan followed by a thick leather-bound accounting ledger closing firmly on a walnut desk, pure foley, no human voice`

- 🎙️ **`[aa07_giovanni]` 老乔瓦尼 (`medici_banker`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [calmly] 一四三五年佛罗伦萨阿诺河畔，美第奇银行靠的从不是谁的剑更利，而是这本左借右贷分毫不差的复式大账本！

- 🎙️ **`[aa08_giovanni2]` 老乔瓦尼 (`medici_banker`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 每一笔进项必有一笔去处，账本一照，骗子无处遁形；正是靠这份信用，小钱庄才撑起了文艺复兴的大穹顶。

- 🎙️ **`[aa09_clara]` 克拉拉女士 (`bond_broker_clara`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [wryly] 光有银行还不够。到了威尼斯运河和滑铁卢前夕的伦敦债市，决定帝国输赢的往往不是火炮数量，而是国债利率牌上那根冷冰冰的曲线。

- 🔊 **`[aa10_harbor]` 音效 · 叠加下一句起拍**（复用母题 `amsterdam_harbor_bell`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Wooden Dutch merchant sailing ship rigging creaking gently beside harbor waves followed by a bright cast-brass Amsterdam exchange opening bell ringing once and crisp linen share certificates rustling, pure foley, no human voice`

- 🎙️ **`[aa11_hans]` 汉斯船长 (`amsterdam_captain`)** （`stability=0.0` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [excited] 一六零二年阿姆斯特丹码头上，一艘香料船沉海就能让船东跳河！可荷兰人把船票切成上千张可买卖的股份，全城百姓都成了股东！

- 🎙️ **`[aa12_hans2]` 汉斯船长 (`amsterdam_captain`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [warmly] 急用钱也不用拆船散伙，走进达姆广场交易所拍掌转手就能套现——人类第一座股票市场，就这样点亮了现代资本的引擎！

- 🎙️ **`[aa13_wallace]` 华莱士牧师 (`scottish_pastor`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [warmly] [calmly] 而在暴雨里的爱丁堡石屋，我们拿寿命统计表与复利算式，把靠天吃饭的慈悲施舍，锻造成了替普通家庭遮风挡雨的现代保险。

- 🎙️ **`[aa14_clara2]` 克拉拉女士 (`bond_broker_clara`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 只是别忘了金融工具天生是双刃剑：三十年按揭能帮工薪家庭安家立业，可一旦贪婪加上三十倍杠杆，也能引爆席卷全球的次贷海啸。

- 🎙️ **`[aa15_zhou2]` 老周 (`homeowner_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [seriously] 听你们这么一说，原来银行、国债、股票、保险加上我家房贷，全都不是为了炫耀金砖，而是帮人类把大风险拆小、把信任变成财富！

- 🎙️ **`[aa16_shen2]` 沈知行 (`historian_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 一针见血！金钱从来不是冰冷的金属，它是人类五千年彼此托付的信任结晶；懂了这套底层规律，看财富才算真正开了天眼。

- 🎙️ **`[aa17_lin2]` 林清晏 (`archivist_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 六集原创历史情景广播剧《金钱的崛起》，八位角色零翻译腔飙戏，带你从美第奇账房一路听懂现代华尔街！

- 🎙️ **`[aa18_narr2]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.55s`）  
  > [solemn] 打开账本，听见金币落盘；五千年财富密码，现在正式启幕。
