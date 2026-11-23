# AUDITION_SHORT ·《《2008次贷暗战：〈大空头〉金融危机剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 2008次贷暗战八角色试听 | `Taut 2008 financial thriller low pulsing cello ostinato, moody plucked upright double bass, sparse dark minimalist felt piano motifs and restrained tremolando chamber viola evoking a lone San Jose fund manager combing through subprime mortgage spreadsheets at 3 a.m., purely acoustic instrumental, no EDM beat, no heavy rock drums, no singing, no vocals` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 2008次贷暗战八角色试听】

- 🔊 **`[bsa01_rain]` 音效 · 独立顺播**（复用母题 `san_jose_rain_keyboard`） （时长 `3.0s` | 句后留白 `0.2s`）  
  Prompt: `Late-night 2005 San Jose office rain drumming softly on glass windows, rapid tactile mechanical keyboard typing on spreadsheets and a laser printer spitting out crisp mortgage ledger sheets, pure foley, no human voice`

- 🎙️ **`[bsa02_narr]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 二〇〇五年春夜，硅谷暴雨倾盆。一盏绿罩台灯下，三千页从来没人翻完的次级房贷明细摊满桌面，把全华尔街最昂贵的美梦撕开了一道暗缝。

- 🎙️ **`[bsa03_lu]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [coldly] 整条华尔街都在高喊房价永远不会跌，可他们连最底下那几千页借款名单都没点开过。两年后浮动利率一翻倍，这批人连利息都还不起，整座高楼会直接断腰。

- 🎙️ **`[bsa04_victor]` 维克多 (`banker_victor`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [condescending] [chuckles] 陆先生，一百年来全美五十个州的房价从未一起下跌。上万户贷款装进同一个大池子再贴上三A安全标签，你想做空美国房市？华尔街欢迎你上门白送保费。

- 🔊 **`[bsa05_jenga]` 音效 · 叠加下一句起拍**（复用母题 `jenga_tower_collapse`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Brass pull-chain click of a green banker desk lamp on dark mahogany followed by dry wooden Jenga blocks scraping as one block slides out and the tall wooden tower clatters down in a sharp cascade, pure foley, no human voice`

- 🎙️ **`[bsa06_zhao]` 赵明轩 (`desk_head_zhao`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [angry] 别跟我念英文缩写！我刚从佛罗里达空城飞回来，那儿的别墅草坪半人高，连宠物狗名字都能批下房贷，舞场姑娘零首付背五套房，这叫风控？

- 🎙️ **`[bsa07_kyle]` 凯尔 (`broker_kyle`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [excited] [chuckles] 老哥你太古板啦！无收入、无工作、无资产照样秒批，签完字我拿高额佣金，债单转手打包卖给纽约大投行，谁管两年后谁还钱？

- 🎙️ **`[bsa08_mei]` 苏梅 (`homebuyer_mei`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [sighs] [trembling] 签合同时他拍胸脯说头两年轻松，涨了再换低息。可昨晚账单寄来月供翻了一倍，我连医院夜班都抢着顶，还是保不住女儿这间房。

- 🎙️ **`[bsa09_lin]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 更可怕的在评级大楼里。把三天卖不掉的臭鱼烂虾重新熬锅浓汤，再拿卖家的钱请考官盖上三A红章，华尔街就是这么把垃圾次贷卖给全世界的。

- 🎙️ **`[bsa10_lin2]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.2s`）  
  > [tense] 真实烂房贷不够卖了，他们干脆造出合成 CDO——像一桌五千万麻将局外围着二十圈十亿赌客，一旦崩盘，整条华尔街一起核爆！

- 🔊 **`[bsa11_desk]` 音效 · 独立顺播**（复用母题 `wall_street_trading_desk`） （时长 `3.0s` | 句后留白 `0.2s`）  
  Prompt: `Tense 2007 Manhattan Wall Street bond trading floor ambience with brisk desk-phone handset clicks, crisp keyboard keystrokes, rustling contract binders and a heavy frosted-glass boardroom door latching shut, pure foley, no human voice`

- 🎙️ **`[bsa12_zhou]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [calmly] 泡沫最毒的地方，从不是让人相信鬼话，而是让所有人都知道它是泡沫，却个个以为自己能在音乐停下前一秒抢先逃出门。

- 🎙️ **`[bsa13_lu2]` 陆沉 (`lone_wolf_lu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [tense] 违约率已经烧到屋檐了，可华尔街的报价单纹丝不动，投资人天天发律师函逼我割肉撤资。因为庄家还没把烫手山芋甩干净——这场暗战，拼的是谁先断气。

- 🎙️ **`[bsa14_zhao2]` 赵明轩 (`desk_head_zhao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [seriously] 等三十倍杠杆叠出的雷曼纸牌屋轰然坍塌，我们就算赢光账面数字也笑不出来。真正该听懂这场风暴的，是每一个手里攥着血汗钱的普通人。

- 🎙️ **`[bsa15_zhou2]` 周启明 (`mentor_zhou`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 看不懂底层资产的高息零风险黑盒别碰，拿卖家红包的评分别信，更别拿浮动高杠杆赌单一资产永远只涨不跌。

- 🎙️ **`[bsa15b_lin3]` 林夏 (`analyst_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 从圣何塞午夜机房、迈阿密空城，到拉斯维加斯狂欢夜与雷曼清晨——六集实战暗战，带你彻底看清每一次金融泡沫的剧本。

- 🎙️ **`[bsa16_narr2]` 风暴旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.55s`）  
  > [dramatically] 欢迎收听八角色金融悬疑广播剧《2008次贷暗战：〈大空头〉金融危机剧》。彻底卸掉晦涩翻译腔，带你看清三A纸牌屋如何在一夜间轰然坍塌。
