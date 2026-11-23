# E004 ·《发明信用违约互换CDS做空华尔街：替别人房子买火灾险的漫长煎熬》广播剧 / 多人精品有声剧演出台本

- **模式**：`condensed_radio_drama`
- **对应章节**：第 4 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.3s`，片尾收束 `1.2s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `act1` | 第一幕·量身定做对赌合约：向华尔街买一张火灾险 | `Taut 2008 financial thriller low pulsing cello ostinato, moody plucked upright double bass, sparse dark minimalist felt piano motifs and restrained tremolando chamber viola evoking a lone San Jose fund manager combing through subprime mortgage spreadsheets at 3 a.m., purely acoustic instrumental, no EDM beat, no heavy rock drums, no singing, no vocals` | 75s | `0.11` / `0.34` |
| `act2` | 第二幕·替邻居危房投保：拆解CDS与非对称赔率 | `Slick suspenseful 2008 Wall Street chamber thriller score, crisp staccato dark minimalist felt piano chords, insistent low pulsing cello ostinato, moody upright double bass and sharp bowed chamber strings evoking gleaming Manhattan trading floors stacking fragile triple-A CDO towers, purely acoustic instrumental, no EDM beat, no heavy rock drums, no singing, no vocals` | 75s | `0.11` / `0.34` |
| `act3` | 第三幕·保费流血倒计时：投资人逼宫与锁死赎回闸门 | `High-stakes brooding 2008 financial crisis thriller chamber underscore, relentless low pulsing cello ostinato, ticking pizzicato upright bass, dark minimalist piano chords and tightening dissonant string harmonics evoking margin-call countdowns and Las Vegas securitization showdowns, purely acoustic instrumental, no EDM beat, no heavy rock drums, no singing, no vocals` | 75s | `0.11` / `0.34` |
| `act4` | 第四幕·最可怕的暗礁：如果卖保险的大银行先倒了怎么办 | `Taut 2008 financial thriller low pulsing cello ostinato, moody plucked upright double bass, sparse dark minimalist felt piano motifs and restrained tremolando chamber viola evoking a lone San Jose fund manager combing through subprime mortgage spreadsheets at 3 a.m., purely acoustic instrumental, no EDM beat, no heavy rock drums, no singing, no vocals` | 75s | `0.11` / `0.34` |
| `act5` | 第五幕·烈火已经烧到屋檐，报价单为何纹丝不动 | `High-stakes brooding 2008 financial crisis thriller chamber underscore, relentless low pulsing cello ostinato, ticking pizzicato upright bass, dark minimalist piano chords and tightening dissonant string harmonics evoking margin-call countdowns and Las Vegas securitization showdowns, purely acoustic instrumental, no EDM beat, no heavy rock drums, no singing, no vocals` | 75s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【act1 · 第一幕·量身定做对赌合约：向华尔街买一张火灾险】

- 🔊 **`[s04_01]` 音效 · 独立顺播**（复用母题 `wall_street_trading_desk`） （时长 `3.0s` | 句后留白 `0.2s`）  
  Prompt: `Tense 2007 Manhattan Wall Street bond trading floor ambience with brisk desk-phone handset clicks, crisp keyboard keystrokes, rustling contract binders and a heavy frosted-glass boardroom door latching shut, pure foley, no human voice`  
  *导演备注：华尔街投行高楼签署定制CDS合约*

- 🎙️ **`[s04_02]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 欢迎收听《2008次贷暗战》第四集。时间回拨到二〇〇五年夏天，在赵明轩踏上佛罗里达空城之前，硅谷怪人陆沉已经穿着褪色圆领衫，独自敲开了曼哈顿投行的大门。

- 🎙️ **`[s04_03]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > 他一连拜访了五家顶级投行，前三家听完他的想法直接礼貌送客。直到第四家，维克多饶有兴致地把他请进了顶楼玻璃厅，像打量一件稀有珍奇品般上下审视。

- 🎙️ **`[s04_04]` 维克多 (`banker_victor`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [condescending] [chuckles] 陆先生，让我再确认一遍我没听错。你手里一美元的次级房贷债券都没买，却要求我们法务部专门起草一套针对房贷债券违约的信用违约互换合约？

- 🎙️ **`[s04_05]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [coldly] 没错，就是 CDS，信用违约互换。你们以前只给企业债和国家主权债签这种违约保险，现在把它移植到我勾出来的这批二〇〇五年次级房贷债上，卖给我十亿美元名义本金。

- 🔊 **`[s04_06]` 音效 · 独立顺播** （时长 `2.4s` | 句后留白 `0.2s`）  
  Prompt: `Thick legal contract pages shuffling swiftly followed by a silver Montblanc pen tapping rhythmically on a glass boardroom desk, pure foley, no human voice`

- 🎙️ **`[s04_07]` 维克多 (`banker_victor`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [wryly] [chuckles] 你知道全曼哈顿的交易员听见这笔生意会怎么说吗？他们会觉得圣诞老人提前半年爬进了烟囱！每年白收你几千万美元保费，赌一个百年从未发生过的美国房市崩盘。

- 🎙️ **`[s04_08]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [calmly] 只要你们愿意签字画押、把按期赔付条款写进国际标准协议，你们爱怎么在背后笑话我都可以。但我有一个硬前提——只要底层房贷本金开始核销减记，你们就必须按月赔付，不许扯皮赖账。

- 🎙️ **`[s04_08b]` 维克多 (`banker_victor`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [wryly] 陆先生眼光倒毒，一眼就划掉了法务部埋的“实物交割延期条款”。行，改成现金差额结算。反正这批三B房贷根本不可能大规模违约，条款写得再严也是废纸。

- 🎙️ **`[s04_08c]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [coldly] 那就把你刚才那句话记在备忘录里。还有，所有保证金划转必须双方对等——将来合同涨到对我有利时，你们每天也得老老实实往我账户里打真金白银。

- 🎙️ **`[s04_09]` 维克多 (`banker_victor`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.26s`）  
  > [warmly] 成交！不过陆先生，合约一旦生效，不管明天刮风下雨，你每个季度都得按时把保费打到我们账户上。还有，如果债价继续上涨，我们随时有权要求你追加现金保证金。

### 【act2 · 第二幕·替邻居危房投保：拆解CDS与非对称赔率】

- 🔊 **`[s04_10]` 音效 · 独立顺播** （时长 `2.4s` | 句后留白 `0.2s`）  
  Prompt: `Warm porcelain teapot pouring tea quietly into two cups inside a wood-paneled Wall Street study with faint rain on windows, pure foley, no human voice`

- 🎙️ **`[s04_11]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [calmly] 很快，不仅陆沉买了十几亿美元的次贷 CDS，从佛罗里达满腔怒火归来的赵明轩也跟进重仓。深夜书房里，林夏拿出一张草纸，把这种听起来云里雾里的金融工具剥了个精光。

- 🎙️ **`[s04_12]` 赵明轩 (`desk_head_zhao`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [earthy] 咱把话说透，听众朋友们一听“信用违约互换”六个字就头大。老周，你用胡同口大爷都能听懂的话讲讲，我跟陆沉手里攥着的这叠纸到底算啥？

- 🎙️ **`[s04_13]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [warmly] 太简单了，明轩。你就把它想象成一张“火灾保险单”——但最奇葩的是，你买的不是自家房子的火灾险，而是替对门邻居那栋电线老化、堆满干柴的木头老宅买保险！

- 🎙️ **`[s04_14]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [seriously] 平时买车险房险，法律规定你必须是车主房主才能投保，防止你盼着别人家着火。可华尔街场外 CDS 市场压根不管这套，谁都能替别人的债买违约险，一栋危房还能卖给一百个人同时投保！

- 🎙️ **`[s04_15]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [calmly] 看看它的非对称赔率有多惊人：如果那栋危房安然无恙，买保险的陆沉每年掏百分之二、三的保费，亏得有底线；可一旦房子起火烧塌，卖保险的投行就得按全额十倍、二十倍赔钱！

- 🎙️ **`[s04_16]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [seriously] 而且二〇〇六年初，华尔街为了方便交易，还推出了专门追踪次级房贷违约险价格的公开指数。从此以后，整个次贷市场终于有了一支看得见的体温计！

- 🎙️ **`[s04_17]` 赵明轩 (`desk_head_zhao`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.26s`）  
  > [wryly] [chuckles] 用小保费撬动几十倍赔付，听着像天上掉馅饼！可我刚入局三个月就发现，这碗饭吃起来比吞玻璃渣还扎嗓子——只要大楼还没塌，每拖一天咱都在往外哗哗流血！

### 【act3 · 第三幕·保费流血倒计时：投资人逼宫与锁死赎回闸门】

- 🔊 **`[s04_18]` 音效 · 独立顺播**（复用母题 `san_jose_rain_keyboard`） （时长 `3.0s` | 句后留白 `0.2s`）  
  Prompt: `Late-night 2005 San Jose office rain drumming softly on glass windows, rapid tactile mechanical keyboard typing on spreadsheets and a laser printer spitting out crisp mortgage ledger sheets, pure foley, no human voice`  
  *导演备注：2006年深秋圣何塞机房投资人逼宫*

- 🎙️ **`[s04_19]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [tense] 二〇〇六年深秋，最煎熬的考验降临了。尽管全美新房销售已经悄悄滑坡，可华尔街股市仍在惯性冲高。陆沉的孤礁资本账面浮亏直逼两成，保费像无底洞一样吞噬着现金。

- 🔊 **`[s04_20]` 音效 · 独立顺播** （时长 `2.6s` | 句后留白 `0.2s`）  
  Prompt: `Office desk phone ringing insistently twice before an inbox alert chimes rapidly and angry paper memos slap onto an oak desk, pure foley, no human voice`

- 🎙️ **`[s04_21]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [tense] 陆总，外头彻底炸锅了！刚刚又收到三家机构出资人的律师函，骂你不务正业跑去买什么冷门房贷保险，全市场都在创新高，只有咱们基金净值连续六个季度往下掉！

- 🎙️ **`[s04_22]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [coldly] 他们两年前追着我把钱塞进门的时候，可不是这套嘴脸。连当年最看好我、陪我度过科技股寒冬的老赞助人，今天也发邮件骂我狂妄失控了吧？他们想干什么？

- 🎙️ **`[s04_23]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [sighs] 对，他们联合发起了强制赎回！更糟的是，维克多那边今天早上又发来追加保证金通知书，要我们七十二小时内补缴三千万现金。要是放投资人抽血，咱们今晚就得被迫割肉平仓！

- 🎙️ **`[s04_24]` 陆沉 (`lone_wolf_lu`)** （`stability=0.0` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [angry] [tense] 割肉？开什么玩笑！我熬穿三千页明细算准了二〇〇七年的重置悬崖，眼看离倒计时归零就剩最后几个月，让我把保单贱卖回给华尔街？！

- 🎙️ **`[s04_25]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [coldly] 起草正式公告：依据合伙协议第十四条，针对流动受限资产启动隔离赎回限制！在真相水落石出前，一分钱也不准撤！哪怕他们把我告上法庭、骂我疯子，我也绝不交枪！

- 🔊 **`[s04_26]` 音效 · 独立顺播** （时长 `2.2s` | 句后留白 `0.2s`）  
  Prompt: `Wooden chair scraping sharply back on hardwood floor followed by a heavy fist thumping once against an office glass partition, pure foley, no human voice`

- 🎙️ **`[s04_27]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [sighs] [calmly] 林夏，老实说，凌晨三点睡不着的时候，我也问过自己一百遍：万一华尔街真能靠改规则硬撑五年怎么办？可每次重新翻开那些借款名单，数字都在冷冰冰告诉我——我只是早到了一步。

- 🎙️ **`[s04_27b]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [warmly] 小陆，一九九九年科网泡沫时，好几位华尔街顶尖老空头明明把估值算得丝毫不差，却偏偏死在崩盘前三个月——就是因为熬不住投资人撤资和保证金流血。活下来，才有资格见证真相。

- 🎙️ **`[s04_27c]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [seriously] 明白，周老。所以我手头永远留足三成现金备付保费，绝不借一分钱加杠杆。我宁可背一辈子孤僻骂名，也要帮出资人把这场风暴扛到天亮。

- 🎙️ **`[s04_28]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.26s`）  
  > [solemn] 锁死赎回闸门那一晚，陆沉的邮箱塞满谩骂与绝交信。看对大方向其实只算半步，在全世界指着鼻子骂你傻瓜时熬过黎明前的流血期，才最折磨人心。

### 【act4 · 第四幕·最可怕的暗礁：如果卖保险的大银行先倒了怎么办】

- 🔊 **`[s04_29]` 音效 · 独立顺播**（复用母题 `wall_street_trading_desk`） （时长 `3.0s` | 句后留白 `0.2s`）  
  Prompt: `Tense 2007 Manhattan Wall Street bond trading floor ambience with brisk desk-phone handset clicks, crisp keyboard keystrokes, rustling contract binders and a heavy frosted-glass boardroom door latching shut, pure foley, no human voice`  
  *导演备注：纽约交易台深夜骤现交易对手风险危机*

- 🎙️ **`[s04_30]` 赵明轩 (`desk_head_zhao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [tense] 等等！老周、林夏，先别光顾着替陆沉揪心，我刚才对着屏幕突然冒出一身冷汗！咱们全都漏算了一颗比保费还毒的定时炸弹！

- 🎙️ **`[s04_31]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 老赵，你手里哪张单子出纰漏了？难道咱们挑的房贷池子质量变好了？

- 🎙️ **`[s04_32]` 赵明轩 (`desk_head_zhao`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [angry] 你们抬头看看墙上那排合约对手方的名字！贝尔斯登、雷曼兄弟、美林、还有那家号称给全球兜底的超级保险巨头！咱们押注的是整条华尔街一起塌方，对不对？

- 🎙️ **`[s04_33]` 赵明轩 (`desk_head_zhao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [tense] 那我问你，要是明年大火真烧起来，把卖咱们火灾保险的那家大投行连锅端烧成破产灰烬了——咱们手里赢来的十亿美元赔款，找谁去兑现？！找破产清算律师排队吗？！

- 🎙️ **`[s04_34]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [solemn] 明轩点中要害了。金融学上这叫“交易对手风险”。你在小赌场押冷门赢了一个亿，结果庄家连夜卷铺盖宣布倒闭，你手里那张赢钱筹码瞬间就变成一张废纸。

- 🎙️ **`[s04_35]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [coldly] 更可怕的是那家全球保险巨头！它在伦敦的分部签出去了几千亿美元裸奔 CDS 担保，竟然一分钱现金赔付准备金都没存——他们真以为三A债券永远不会违约，白捡保费！

- 🎙️ **`[s04_36]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [seriously] 也就是说，我们不仅要猜中危机什么时候爆发，还必须在对手方银行彻底断气之前，把纸面盈利稳稳换成真金白银，甚至得挑最不容易先倒下的大机构分散对手盘！

- 🎙️ **`[s04_36b]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [tense] 还有一点必须死守——执行每日现金抵押品划转！不能等合同到期总清算，银行亏一百万就得当天划一百万现金进托管账户，否则等它倒闭，谁也讨不回债！

- 🎙️ **`[s04_37]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.26s`）  
  > [calmly] 我早就想过这一层。所以我把十几个亿的空单刻意拆散到了七家不同的欧美顶级银行手里，同时盯紧抵押品划转协议——只要对方账面一松动，我必须第一时间锁住现金抵押物。

### 【act5 · 第五幕·烈火已经烧到屋檐，报价单为何纹丝不动】

- 🔊 **`[s04_38]` 音效 · 独立顺播**（复用母题 `florida_empty_house`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Hot quiet Florida empty suburban cul-de-sac wind rustling dry palm fronds, a rusted metal padlock clanking against a real-estate sign post and hollow footsteps echoing across an unfurnished wooden living room floor, pure foley, no human voice`  
  *导演备注：2007年初佛罗里达封条蔓延与报价异象*

- 🎙️ **`[s04_39]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [tense] 二〇〇七年春天终于到了。陆沉两年前设下的重置闹钟准时炸响。佛罗里达与加州的次贷断供浪潮像野火般漫开，苏梅所在的整片社区，短短两个月贴出了十几张法拍告示。

- 🎙️ **`[s04_40]` 苏梅 (`homebuyer_mei`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [sighs] [trembling] 林小姐，我撑不住了……女儿发烧住院请了三天假，这个月加班费不够补三千四的月供。昨天银行催收员已经来门口拍了照，整个街区一半人都在连夜搬空家具。

- 🎙️ **`[s04_41]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [solemn] 挂完梅姐电话，我立刻核对了全美二〇〇六批次次贷的逾期数据——逾期六十天以上的比例已经飙破百分之十，全美最大的几家次贷专营公司上周直接宣布破产关门！

- 🔊 **`[s04_42]` 音效 · 独立顺播** （时长 `2.5s` | 句后留白 `0.2s`）  
  Prompt: `Rapid electronic quote terminal keyboard strokes halting suddenly followed by a stunned silence and a binder dropping onto a desk, pure foley, no human voice`

- 🎙️ **`[s04_43]` 赵明轩 (`desk_head_zhao`)** （`stability=0.0` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [angry] 活见鬼了！你们快来看我刚从维克多交易台要来的最新估值报价单！底层次贷都烂成一锅粥了，放贷公司都在排队倒闭，可他们给咱们手里三B级次贷债的报价一分没跌，咱们的 CDS 反倒还在亏钱？！

- 🎙️ **`[s04_44]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [coldly] 我这边也一样。三家大投行同时发来荒唐的每日盯市报告，嘴硬说市场成交稀少、要按他们自家内部模型估值，拒绝调高我的 CDS 合约价值，甚至还在催我交保证金！

- 🎙️ **`[s04_45]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [tense] 怎么可能违约率一路飙升，债券价格和信用评级却像冻在冰块里一样纹丝不动？哪怕傻瓜都知道大楼起火了，怎么消防警报器一声不响？

- 🎙️ **`[s04_46]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [coldly] 警报器不是坏了，是有人亲手拔了电源线。违约数据不会撒谎，价格之所以死活不肯动，只剩一种解释——华尔街大投行和三大评级机构，正在集体装睡、联手捂盖子！

- 🎙️ **`[s04_46b]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [tense] 我刚核对完最新账单，银行不仅拒绝重估我的合约，还偷偷调高了对手方交易手续费。他们越是拼命按住锅盖，越说明底下的高压锅已经快顶不住了！

- 🎙️ **`[s04_47]` 赵明轩 (`desk_head_zhao`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.24s`）  
  > [angry] 好啊！明天上午我直接杀进三大评级大楼当面对质，下周咱们直飞拉斯维加斯年度证券化峰会！我倒要看看，维克多和这群考官到底能把这出双簧演到几时！

- 🔊 **`[s04_48]` 音效 · 独立顺播** （时长 `2.4s` | 句后留白 `0.22s`）  
  Prompt: `Heavy elevator chime ringing sharply as brisk footsteps stride down a marble Wall Street corridor, pure foley, no human voice`

- 🎙️ **`[s04_49]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.55s`）  
  > [dramatically] 谁在给垃圾债强行续命？付钱买三A的利益旋转门背后究竟藏着什么交易？下一集，直击评级黑幕与拉斯维加斯纸醉金迷的末日狂欢夜。
