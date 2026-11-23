# AUDITION_SWAN ·《《感恩节火鸡警报：〈黑天鹅与反脆弱〉风险剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 感恩节火鸡警报八角色试听 | `Tense intellectual Mediterranean-meets-chamber cello drone, stark lonely solo piano notes, subtle plucked acoustic oud and nylon guitar harmonic accents with suspenseful bowed strings evoking a moonlit storm-lit limestone harbor tavern overlooking dark waters, purely acoustic instrumental, no pop drums, no modern beat, no singing, no vocals` | 75s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 感恩节火鸡警报八角色试听】

- 🔊 **`[bsa01_storm]` 音效 · 独立顺播**（复用母题 `harbor_stone_storm`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Mediterranean limestone harbor tavern interior at night with dark sea waves lapping heavily against stone seawalls outside an arched window, soft wind howling faintly through wooden shutters and a tallow candle flame flickering quietly on a rough oak table, pure foley, no human voice`

- 🎙️ **`[bsa02_narr]` 风险旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [solemn] 地中海暗夜浪涌拍打石堤，拱窗外一只黑天鹅划破金色月影。橡木长桌上，一张连涨整整一千天的完美收益曲线，正把八个立场针锋相对的人拖进风暴眼。

- 🎙️ **`[bsa03_gu]` 顾承泽 (`risk_director_gu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [condescending] 一千个交易日零回撤，百万级样本回测，加上六个标准差的严密风控模型——马库斯，这叫现代金融工程的胜利，可不是你嘴里那套玄学。

- 🎙️ **`[bsa04_marcus]` 马库斯 (`trader_marcus`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [wryly] [chuckles] 巧了，顾总监。养鸡场里那只感恩节火鸡，前一千天也被主人准时喂得油光水滑。到了第一千零一天早上，它对主人的科学信任达到顶峰——然后屠夫进了门。

- 🎙️ **`[bsa05_qi_q]` 齐明月 (`journalist_qi`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 等等！满大街理财报告都说过去三年稳赚不赔，普通人一辈子血汗钱输不起一次清零。咱们到底该怎么分辨，眼前的安稳是真安全，还是压路机前面捡硬币？

- 🎙️ **`[bsa06_zhou]` 周凯 (`founder_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [excited] 照你这么说，大家都缩进山洞别干活算了？我靠五倍杠杆、零库存冲刺，三年把公司干到十亿估值，市场奖励的就是敢把油门踩到底的赢家！

- 🔊 **`[bsa07_chart]` 音效 · 叠加下一句起拍**（复用母题 `maritime_chart_brass`） （时长 `2.6s` | 句后留白 `0.18s`）  
  Prompt: `Crisp heavy parchment nautical chart unrolling across a mahogany desk followed by a heavy brass marine compass and dividers clicking precisely onto aged paper, pure foley, no human voice`

- 🎙️ **`[bsa08_helen]` 海伦 (`actuary_helen`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [coldly] 周总，你墙上只挂着扛过狂风的冠军名船。我地下档案室锁着三百年沉在海底的账本，当年那批敢踩死油门的船长，一个都没机会爬上岸写回忆录。

- 🔊 **`[bsa09_vase]` 音效 · 独立顺播**（复用母题 `porcelain_vase_shatter`） （时长 `2.6s` | 句后留白 `0.2s`）  
  Prompt: `Crisp startling foley of a delicate thin-walled ceramic vase slipping off a hardwood table and shattering sharply into dozens of tinkling shards across a stone floor, pure foley, no human voice`

- 🎙️ **`[bsa10_marcus2]` 马库斯 (`trader_marcus`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [seriously] 听见没？薄瓷瓶一摔就碎，那叫脆弱；花岗岩不怕摔，顶多算强韧。可真正能在黑天鹅风暴里越活越狠的，是挨了震荡反而长肌肉的新物种——反脆弱！

- 🎙️ **`[bsa11_lin]` 林大夫 (`doctor_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [calmly] 医院里干了三十五年我最明白，骨头越负重越密实，躺温室里反倒疏松。最可怕的不是刮风下雨，是没病硬灌猛药、把身体底子掏个精光。

- 🎙️ **`[bsa12_gu2]` 顾承泽 (`risk_director_gu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [pushback] 说得轻巧！普通人既不想存死现金挨通胀，又怕高风险爆仓，买中度风险平衡配置难道不是唯一出路？

- 🎙️ **`[bsa13_marcus3]` 马库斯 (`trader_marcus`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [seriously] 错！全金融界最坑人的就是虚伪的平庸中间派。拿九成家底守住铜墙铁壁、绝不出局，再拿一成小钱押注无限好运——这副铸铁杠铃，才是普通人的护身符。

- 🎙️ **`[bsa14_chen]` 陈老爹 (`artisan_chen`)** （`stability=0.0` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 别听穿西装的满嘴平均数，淹死鬼哪管河水平均才一米二！街坊凭啥信我这炉面包没掺假？因为我一家老小天天早饭也啃这一炉！

- 🎙️ **`[bsa15_narr2]` 风险旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [calmly] 不坐自己修的桥、不亏自己钱的专家，凭什么替你拍板？六场硬核夜话，拆透火鸡幻觉、肥尾崩盘、沉默证据、反脆弱与杠铃铁律。

- 🎙️ **`[bsa16_qi]` 齐明月 (`journalist_qi`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [seriously] 告别晦涩翻译腔，直面让你一夜清零的隐形地雷。欢迎收听八角色金融风险剧《感恩节火鸡警报》——在不确定世界里，活成真正的强者！
