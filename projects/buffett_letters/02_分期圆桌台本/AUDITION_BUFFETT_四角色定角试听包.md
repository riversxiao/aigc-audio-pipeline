# AUDITION_BUFFETT ·《《穿越周期的信》V2真人录音棚声线与实景圆桌试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`01_股东信英文原典库/2008_berkshire_shareholder_letter_excerpts.md`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `0.85s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 深夜书房双语圆桌试听 | `Warm intimate American Heartland acoustic fingerstyle guitar and gentle upright double bass duet, cozy late-night mahogany study atmosphere, thoughtful and grounded storytelling underscore, purely instrumental, no drums, no singing, no vocals` | 95s | `0.055` / `0.22` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 深夜书房双语圆桌试听】

- 🎙️ **`[aud01_zhiwei_open]` 许知微 (`host_zhiwei`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.14s`）  
  > 哎，怀远、老周，今天咱们第一期没从一九六五年顺着念，直接翻到了二〇〇九年二月底那个周末——巴菲特刚把〇八年的股东信挂上网，第一行就是四十四年里最难看的账单。  
  *导演备注：许知微：松弛近麦聊天起手，零播音腔，像深夜隔着木桌对谈。*

- 🎙️ **`[aud02_laozhou_banter]` 老周 (`guest_laozhou`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.18s`）  
  > [chuckles] 那年谁账面好看啊？二〇〇八年十一月我去东莞上游冷库提冻品，人家铁门上直接贴张红纸——支票免谈，熟人免谈，见现钞起杆。  
  *导演备注：老周：真实制造业/供应链老江湖口吻，不端架子。*

- 🎙️ **`[aud03_huaiyuan_setup]` 陈怀远 (`guest_huaiyuan`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > 那会儿华尔街也一模一样。巴菲特没掉书袋，直接搬出了他年轻时在小餐馆墙上见过的一句老话。  
  *导演备注：陈怀远：沉稳松弛男中音，自然引出英文原声。*

- 🎙️ **`[aud04_buffett_solo]` 沃伦·巴菲特 (`buffett_prime_en`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.3s`）  
  > [wryly] The watchword throughout the country became the creed I saw on restaurant walls when I was young: In God we trust; all others pay cash.  
  *导演备注：壮年巴菲特短金句 100% 完整独奏，不中途掐断。*

- 🎙️ **`[aud05_zhiwei_pushback]` 许知微 (`host_zhiwei`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [pushback] 除了上帝，所有人一律付现。但我就好奇一件事——那时候连雷曼和 AIG 都断气了，伯克希尔也是做保险的，凭什么他没被挤兑垮？  
  *导演备注：许知微：自然回味金句后犀利追问。*

- 🎙️ **`[aud06_buffett_simul_en]` 沃伦·巴菲特 (`buffett_prime_en`)** （`stability=0.5` | 声场 `vintage_study` | **同传叠音：原声独奏 `6.8s` → 压混 `0.11`** | 句后气口 `0.0s`）  
  > [seriously] I have pledged – to you, the rating agencies and myself – to always run Berkshire with more than ample cash. We never want to count on the kindness of strangers in order to meet tomorrow's obligations. When forced to choose, I will not trade even a night's sleep for the chance of extra profits.  
  *导演备注：长段原典：完整读完第一句自动寻气口后再平滑压低至-19dB垫底。*

- 🎙️ **`[aud07_huaiyuan_simul_zh]` 陈怀远 (`guest_huaiyuan`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.45s`）  
  > 我向你们、向评级机构、也向我自己立过誓：永远让伯克希尔保有绰绰有余的现金。我们绝不指望靠陌生人的仁慈，去偿付明天的债务。真要二选一，我绝不会拿哪怕一夜的安稳觉，去换取额外利润。  
  *导演备注：陈怀远：纯粹克制的同传译文，读完留半秒呼吸，绝不混入个人议论。*

- 🎙️ **`[aud07b_zhiwei_bridge]` 许知微 (`host_zhiwei`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.14s`）  
  > 绝不指望陌生人的仁慈——这话搁在当年华尔街也太扎心了。  
  *导演备注：许知微：自然短句承接，避免同一嘉宾同传后连说两段。*

- 🎙️ **`[aud08_huaiyuan_bilingual_tag]` 陈怀远 (`guest_huaiyuan`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.5s`）  
  > 说白了，华尔街投行赌的是 overnight funding，隔夜借新还旧；而巴菲特守着五百八十五亿美金的 insurance float，还非要在枕头底下多压几百亿国债——所以天塌下来，他睡得着。  
  *导演备注：中英短语(overnight funding / insurance float)自然镶嵌在口语节奏里。*
