# 《跨境底牌：硅深暗战》（*Global Edge*）—— 口音矩阵、表演韵律与语速声学指导手册

> **手册定位**：本手册是《跨境底牌：硅深暗战》全季 24 集及 `AUDITION_GLOBAL_EDGE` 声纹试听包的**权威语音学、表演导演与 Drama 3 声学控制规范**。所有指标均严格绑定仓库 M1 双语引擎源码（`src/aigc_audio_pipeline/{models,drama3_adapter,mixer,qa,polyphones}.py`）与 M2 百条真实高管语料实证分布（`corpus_100_structured.json`），零拍脑袋估算、零教科书腔妥协。

---

## 一、 「85% 美音 + 伦敦 RP / 15% 精控国际客串」口音矩阵与季配额账本

### 1.1 语言学立项依据与全季实配账本

基于二语语音习得研究与 Jennifer Jenkins **通用语核心理论（Lingua Franca Core, LFC）**，B1–C1 学习者建立稳定口语运动表征（speech motor targets）需要高度一致、元音与核重音清晰的高声望语音标杆；而真实跨国商战又需要有限度的多国口音抗干扰训练。本剧严格执行 **核心 US+UK RP `>= 85.0%` / 精控国际客串 `<= 15.0%`** 红线，第一季 24 集精确锁定为 **`96.0%` 核心 US+UK RP / `4.0%` 国际客串**（且首集 **`E001` 锁定 `100.0%` 纯美音 + 伦敦 RP**，确保听众第一集即建立最高级听觉锚点）：

| 弧光 / 集数 | 总集数 | 国际客串出场明细与占比 | 弧光核心 US+UK RP 均占比 | 弧光国际客串占比 |
| :--- | :---: | :--- | :---: | :---: |
| **第一弧（`E001–E006`）** | 6 | 无客串（`E001` 严格 `100%` 纯美音 + 伦敦 RP） | **`100.0%`** | `0.0%` |
| **第二弧（`E007–E012`）** | 6 | 仅 **`E011`**：`henrik_lindqvist`（`intl_eu_legal`，布鲁塞尔欧盟法务，占该集英文 **`30.0%`**，该集核心 `70.0%`） | **`95.0%`** | `5.0%` |
| **第三弧（`E013–E018`）** | 6 | **`E013`**：`rajiv_menon`（`intl_indian_exec`，**`22.0%`**）+ `wei_ling_tan`（`intl_singapore_vc`，**`14.0%`**）合计 `36.0%`（核心 `64.0%`）；**`E016`**：`wei_ling_tan`（**`30.0%`**，核心 `70.0%`） | **`89.0%`** | `11.0%` |
| **第四弧（`E019–E024`）** | 6 | 无客串（全员美音 + 伦敦 RP 决战 IPO 终局） | **`100.0%`** | `0.0%` |
| **第一季 24 集总计** | **24** | 21 集 `100%` + `E011` (`70%`) + `E013` (`64%`) + `E016` (`70%`) = `2304 / 24` | **`96.0%`**（超额满足 `>= 85%`） | **`4.0%`**（严控 `<= 15%`） |

### 1.2 全剧 8 角色口音代码（`accent_code`）与反刻板印象红线

| 口音阵营 | 规范 `accent_code` | 绑定角色 | 目标语速带 (`WPM`) | 声学与清晰度铁律（Anti-Caricature & LFC 标准） |
| :--- | :--- | :--- | :---: | :--- |
| **核心美音（硅谷双语）** | `zh_en_bilingual_us` | `lin_chen` | `155–180` | 硅谷标准 General American 英文 + 冷峻克制现代科技普通话；同一真人声源跨语种零音色断裂 |
| **核心中文（深圳智造）** | `zh_mainland_sz` | `zhou_mo` | `3.55–3.65 字/秒` | 现代深圳科技高管普通话 + 准确利落的英文硬件术语（`BOM cost` / `yield ramp`），零土味丑化 |
| **核心美音（沙丘路 VC）** | `us_silicon_valley` | `victoria_vance` | `165–185` | 硅谷/斯坦福商学院精英美音：丝绸裹钢、句尾权威下压、自然闪音连读 |
| **核心英音（伦敦旗舰）** | `uk_london_rp` | `alistair_finch` | `145–165` | 现代伦敦标准 RP（Modern RP）：非卷舌、清脆 `/t/`、低调冷讽重音，严禁美音混入或舞台剧腔 |
| **核心美音（纽约法务）** | `us_nyc` | `claire_chen_gc` | `160–185` | 纽约东海岸红圈所律师美音：辅音如刀、节奏短促干脆、零多余废话 |
| **精控客串（北欧欧盟）** | `intl_eu_legal` | `henrik_lindqvist` (`E011`) | `145–160` | 极度清晰冷冽的北欧国际法务英语；保留全部 LFC 辅音群与核重音对比，严禁生硬机械音 |
| **精控客串（印度精英）** | `intl_indian_exec` | `rajiv_menon` (`E013`) | `155–175` | IIT + 沃顿商学院级高清晰跨国高管英语；自然微卷舌韵律但元音/重音 100% 清晰，**严禁喜剧化刻板口音** |
| **精控客串（新加坡外交）** | `intl_singapore_vc` | `wei_ling_tan` (`E013/E016`) | `150–170` | 受过英式精英教育的新加坡主权基金外交英语；**严禁街头 Singlish 助词（`lah`/`lor`）或吞尾音** |

---

## 二、 语音学与韵律精雕指南：硅谷/纽约美音 vs. 伦敦 RP 英音

为了保证双人纯英文对峙时听众**无需旁白报幕即可 1 秒听声辨人**，同时为 B1–C1 学习者提供最高价值的跟读模仿范本，全剧严格拉开美音组（`lin_chen`, `victoria_vance`, `claire_chen_gc`）与伦敦 RP 组（`alistair_finch`）的五大语音学边界：

### 2.1 美音与伦敦 RP 五维音系对照表

| 音系特征 | 硅谷 / 纽约美音（`us_silicon_valley` / `us_nyc` / `zh_en_bilingual_us`） | 伦敦现代 RP 英音（`uk_london_rp` — `alistair_finch`） | 剧本实战例词（出自本季核心词库） |
| :--- | :--- | :--- | :--- |
| **卷舌性 (Rhoticity)** | 强卷舌（词尾与辅音前 `/r/` 清晰卷舌，如 `number` `/ˈnʌmbər/`、`margin` `/ˈmɑːrdʒɪn/`） | 严格非卷舌（`non-rhotic`），仅在元音前出现连读 `linking /r/`（如 `other words` 不卷舌，`far enough` 连读 `/r/`） | `phantom number`、`In other words`、`hard trade-off`、`margin` |
| **齿龈爆破 `/t/` 变体** | 词中元音间自然美式闪音 flapping `/ɾ/`（如 `better`, `get it` → `/ˈgɛɾɪt/`、`eating` → `/ˈiːɾɪŋ/`） | 始终保持清脆精准的齿龈清爆破 `/t/`（`not a cash loss`、`what is good enough` 的 `/t/` 干脆如冰锥落地） | `When are you going to get it`、`eating into budgets`、`capital-efficient` |
| **核心元音体系** | `LOT` 偏展唇低后 `/ɑː/`（`not` `/nɑːt/`、`cost` `/kɔːst/`）；`BATH` 读前低 `/æ/`（`ask`, `pass`）；`GOAT` 读 `/oʊ/` | `LOT` 圆唇短促 `/ɒ/`（`not` `/nɒt/`、`cost` `/kɒst/`）；`BATH` 读长后 `/ɑː/`（`ask` `/ɑːsk/`、`margin` `/ˈmɑːdʒɪn/`）；`GOAT` 读中央起音 `/əʊ/` | `not a cash loss`、`cost`、`flowed through`、`last` |
| **重音计时与功能词弱读** | 极强重音计时（stress-timed）：虚词 `to / of / into / a` 高速压缩弱化，实义动词与数字拉长加重 | 同为重音计时，但辅音边界更锐利、低调降调幅更克制，依靠轻描淡写制造“英式贵族压迫感” | `flowed through into the income statement`、`run this thing a million times` |
| **语调轮廓与权力潜台词** | 断言与反杀采用**干净向下终止调（falling terminal pitch）**，绝不在陈述句末尾无意识上扬（杜绝 uptalk 显得心虚） | 标志性**“礼貌带刀”高低折线（fall-rise concession → 冰冷低降调）**：前半句礼貌微扬让步，停顿 `0.2s` 后低音直刺要害 | `That is a fair criticism...`（微扬让步）→ `at the end of the day...`（冷降定调） |

### 2.2 破除中式“音节计时”习惯的四大实战连读剖音样本（Act 5 拆局重点）

汉语属于偏音节计时（syllable-timed）语言，B1–B2 职场人听真实 `170+ WPM` 会议卡壳的首要元凶，正是真实语流中的弱读与辅音连缀。以下 4 组 E001 高频杀招必须在 Act 5 的 `0.80x` 慢拆中清晰暴露声学细节：
1. **`When are you going to get it?`**（`059_FIN`）：实速中 `going to` 弱化连读为 `/ˈɡənə/`、`get it` 发生美式闪音连读 `/ˈɡɛɾɪt/`，全句核重音钉死在 **`When`** 与 **`get`** 两个音节。
2. **`flowed through into the income statement`**（`02_BIZ_Anthropic`）：`flowed through` 的 `/d/` 不完全爆破直接滑入 `/θ/`，`into the` 极速弱化，声能集中在 **`flowed`** 与 **`income`**。
3. **`eating into budgets`**（`090_USC`）：美音 `eating` 闪音连读 `into`（`/ˈiːɾɪŋ ˌɪntə/`），伦敦 RP 则清晰保留 `/t/` 爆破制造冷冽苛责感。
4. **`run this thing a million times`**（`090_USC`）：`thing a` 自然连读，`million` 与 `times` 拖出沉重数量级重音，配合微短停顿凸显成本灾难感。

---

## 三、 HBO 冷峻写实表演法与 Drama 3 精确标签控制规范

### 3.1 表演美学四条铁律（HBO *Succession* × *Silicon Valley*）

1. **零咆哮、零喊麦、零播音腔（`播音腔`）**：真正掌握十亿美元筹码的合伙人与大买手从不提高嗓门吵架——**筹码越致命，声音越低沉、语速越稳、呼吸越克制**。
2. **“礼貌带刀”（Silk Over Steel）**：最毒的拒绝往往包裹在极度体面的词汇里（`"That is a charming deck, Lin, truly."` / `"That's a fair criticism."`），利用 `[short pause]` 与 `[clears throat]` 在礼貌和刀锋之间劈开 `0.25–0.40s` 的冷场真空。
3. **呼吸感与微停顿**：用真实点事件 `[sighs]`、`[short pause]`、`[clears throat]` 锚定人类思考、压火与换气节奏，彻底消灭 AI 朗读机式的均匀节拍。
4. **离散 `stability` 纪律（严格遵守 `ALLOWED_V3_STABILITIES = (0.0, 0.5, 1.0)`）**：
   - **`0.5`（默认基准）**：全剧 80%+ 台词锁定 `0.5`，输出沉稳、丝滑、极具电影自然波动的 HBO 表演基线；
   - **`0.0`（高张力情绪/锐利反杀）**：仅用于高烈度抢话打断、冷嘲反讽、惊险转折反击（如 `E001` 掀桌回击 `"phantom number"`、`E012` 守住超级投票权），拉满微表情语调张力；
   - **`1.0`（冷漠宣告/正式宣读）**：仅用于宣读冷冰冰的监管裁定、纽交所开市公告或条款原文；在 `domain="business_english_drama"` 下，M1 引擎已彻底阻断仙侠退化，**`stability=1.0` 绝不会注入 `"ancient monotone"` 或 `<slow>`**。

### 3.2 核心 21 个 M1 认证 HBO 商战 Drama 3 标签完整映射表

> **M1 引擎关键防踩坑铁律（100% 实测自 `src/aigc_audio_pipeline/drama3_adapter.py`）**：
> - 所有标签必须为**小写 ASCII 方括号**且**严格属于 `DRAMA3_TAG_MAP | DRAMA3_POINT_EVENTS`**（`validate_v3_dialogue_text()` 只查语法不查白名单，拼错或自创标签如 `[smugly]` 会在运行时被静默丢弃！）；
> - **单分句风格标签上限严格 `<= 2` 个**（`drama3_adapter.py` 仅取 `style_briefs[:2]`，第 3 个风格标签会被截断）；可额外叠加点事件（`[sighs]` / `[short pause]` / `[clears throat]`）；
> - **⚠️ `[wryly]` 纯英禁用红线**：在 `DRAMA3_TAG_MAP` 中 `"wryly"` 映射到 `"wry, folksy Midwestern wit with a knowing smile"`（巴菲特奥马哈遗产），**严禁用于任何纯英 `language_code="en"` 角色**（`victoria_vance`、`alistair_finch`、`claire_chen_gc` 及三位国际客串）！`[wryly]` **仅限**用于 `zh` / `zh-en` 角色（如 `zhou_mo`），此时引擎自动路由至 `BUSINESS_DRAMA_ZH_MICRO_MAP["wryly"]` → `"带着一丝冷幽默"`，绝对零中西部口音泄露。

| 规范标签 | 归属词典 | 纯英 (`en`) Drama 3 提示词 (`DRAMA3_TAG_MAP`) | XML 语势包裹 | 双语/中文 (`zh`/`zh-en`) 提示词 (`BUSINESS_DRAMA_ZH_MICRO_MAP`) | 本剧授权角色与使用场景 |
| :--- | :---: | :--- | :---: | :--- | :--- |
| `[measured]` | `TAG_MAP` | `measured, poised executive cadence, unhurried control` | *(无)* | `不疾不徐、沉稳克制` | 全员核心基线，掌控会议室节奏 |
| `[deadpan]` | `TAG_MAP` | `flat, deadpan understatement, dry executive delivery` | *(无)* | `冷面平淡、不带波澜` | `zhou_mo` 产线吐槽、`alistair_finch` 英式冷面讽刺 |
| `[icy polite]` | `TAG_MAP` | `icy-polite, silk-over-steel corporate courtesy with quiet menace` | *(无)* | `礼貌克制、暗藏锋芒` | `victoria_vance` / `alistair_finch` / `wei_ling_tan` 标志性“礼貌带刀” |
| `[blunt]` | `TAG_MAP` | `blunt, clipped, matter-of-fact boardroom directness` | *(无)* | `干脆直白、利落切入` | `lin_chen` / `claire_chen_gc` / `zhou_mo` / `rajiv_menon` 直接亮底牌 |
| `[guarded]` | `TAG_MAP` | `guarded, cautious, calculated restraint` | *(无)* | `谨慎克制、话留三分` | `wei_ling_tan` 主权资本试探、敏感地缘议题博弈 |
| `[skeptical]` | `TAG_MAP` | `dry, skeptical corporate questioning, eyebrow-raised doubt` | *(无)* | `语气微沉、带着审视与怀疑` | `victoria_vance` 审视财报、`zhou_mo` / `rajiv_menon` 质疑成本 |
| `[firmly]` | `TAG_MAP` | `firm, grounded executive authority, steady resolve` | *(无)* | `语气沉稳笃定` | `lin_chen` 拍板红线、`claire_chen_gc` 守条款、`henrik_lindqvist` 宣读合规边界 |
| `[understated]` | `TAG_MAP` | `quiet, understated intensity, restrained low-key delivery` | `<soft>` | `克制低沉` + `<soft>` | `alistair_finch` / `henrik_lindqvist` 轻声重压、低调威慑 |
| `[coldly]` | `TAG_MAP` | `cold, restrained and icy tone` | *(无)* | `冷峻克制` | `victoria_vance` / `henrik_lindqvist` 撕掉客套亮出最后通牒 |
| `[wryly]` ⚠️ | `TAG_MAP` | *(纯英禁用！映射 Midwestern wit)* | *(无)* | `带着一丝冷幽默` | **仅限 `zh`/`zh-en`（如 `zhou_mo`）！纯英角色严禁使用** |
| `[sarcastic]` | `TAG_MAP` | `cold, mocking sneer` | *(无)* | `略带反讽` | `alistair_finch` 讽刺硅谷 PPT 吹牛与实验室翻车 |
| `[dismissive]` | `TAG_MAP` | `aloof, aristocratic disdain` | *(无)* | `漫不经心、略带不屑` | `alistair_finch` 轻蔑压价与居高临下审视新品类 |
| `[pushback]` | `TAG_MAP` | `sharp, lively conversational pushback` | *(无)* | `语气微顿、敏锐反问` | `claire_chen_gc` / `lin_chen` 敏锐顶回陷阱条款 |
| `[tense]` | `TAG_MAP` | `tight, controlled high-stakes tension, restrained breath` | *(无)* | `节奏收紧、压迫感克制` | `zhou_mo` 产线良率报警、`claire_chen_gc` 突发传票警报 |
| `[confident]` | `TAG_MAP` | `calm, effortless executive confidence, assured clarity` | *(无)* | `从容笃定、不急不躁` | `rajiv_menon` / `wei_ling_tan` / `lin_chen` 胜券在握定调 |
| `[aside]` | `TAG_MAP` | `close-mic private aside, quiet knowing inner monologue` | `<soft>` | `贴麦内心独白，克制冷静` + `<soft>` | `lin_chen` 《纸牌屋》式贴麦潜台词破译（配 `inner_monologue`） |
| `[coach]` | `TAG_MAP` | `clear, crisp executive mentor cadence, articulate natural emphasis` | *(无)* | `口语化拆解、吐字清晰自然` | `lin_chen` Act 5 3 分钟黑话复盘拆局专用（绝无课堂老师味） |
| `[interrupting]` | `TAG_MAP` | `brisk, sharp executive cut-in, tight conversational pace` | *(无)* | `语速微快、干脆打断` | 配合 `gap_after_s ∈ [-0.25, -0.05]s` 的高压会议室抢话切入 |
| `[sighs]` | `POINT` | `[sighs]` | *(无)* | `[sighs]` | 熬夜产线疲惫压火、无声冷嘲 |
| `[short pause]` | `POINT` | `[short pause]` | *(无)* | `[short pause]` | 礼貌让步与致命杀招之间的黄金真空停顿 |
| `[clears throat]` | `POINT` | `[clears throat]` | *(无)* | `[clears throat]` | `alistair_finch` 伦敦会议室开场清嗓控场 |

> **补充说明（M1 引擎全量合法标签边界）**：上表列出本剧最高频的**核心 21 个**标签；M1 引擎源码 `BUSINESS_DRAMA_ZH_MICRO_MAP`（共 24 键）另合法支持 6 个辅助微调标签（`[calmly]`、`[rushed]`、`[seriously]`、`[softly]`、`[whispers]`、`[whispering]`），`DRAMA3_POINT_EVENTS`（共 8 键）另合法支持 5 个点事件（`[pause]`、`[long pause]`、`[exhales]`、`[gasps]`、`[chuckles]`），M5 编剧在贴合 HBO 克制写实美学前提下可按需选用。

### 3.3 `domain="business_english_drama"` 零仙侠保障与 3 级质检重试阶梯

当本地 `faster-whisper` 双脚本质检判定某句 Drama 3 产出存在漏字、丢尾或误读方括号标签时，`drama3_adapter.py` 按严格 3 级重试阶梯自动降噪重试（且全程零仙侠、零古风旁白回退；中文多音字自动走 `BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP`，如 `重估 → 崇估`）：
- **`attempt = 1`（全表现力模式）**：保留最多 2 个分句风格描述 + 点事件 + `<soft>`/`<whisper>` 语势包裹；
- **`attempt = 2`（稳态降噪模式）**：若首个标签为点事件则保留该点事件；否则纯中文/双语直接降级为纯净口语正文（去全部括号与 XML），纯英文仅保留首标签单句提示词并剥离 XML；
- **`attempt = 3`（纯声纹直出兜底）**：剥除全部标签与 XML，完全依赖 `v2_real_human_studio` 真人录音棚锚点原生韵律直出，确保 ASR 召回率 `>= 0.72`。

### 3.4 负间隔抢话编排（Crosstalk）与纪录片同传叠音（`duck_under_next`）规范

1. **实时抢话打断编排（`gap_after_s ∈ [-0.25, -0.05]s`）**：
   - `models.py` 校验范围 `[-0.25, 10.0]s`；HBO 会议室真实打断黄金区间锁死在 **`[-0.25, -0.05]s`**（最佳自然听感甜蜜点 **`-0.12s` 至 `-0.20s`**）。
   - 被打断的前一句若处于会议室，优先使用 **`boardroom`**（该声场在 `mixer.py` 中严格零尾随 `apad` 填充，确保人声瞬间无缝搭接而不拖泥带水）；打断切入句配合 **`[interrupting]`**（可选 `stability=0.0`）。
   - 底层安全防护：`mixer.py` 内置反倒退时间戳钳位（`min_next_start = start_s + min(dur_s * 0.5, 0.05)`）并自动裁平 `.srt` 字幕边界，杜绝任何字幕重叠报错。
   - E001 四变体抢话硬门槛：`E001_VA >= 6`、`E001_VB >= 4`、`E001_VC >= 6`、`E001_VD >= 3`。
2. **纪录片同传叠音规范（`duck_under_next=True`，专用于 `E001_VD >= 2` 组及特殊纪实桥段）**：
   - 仅限 `kind="dialogue"` 且紧随其后的下一条同样为 `kind="dialogue"`；参数边界锁定 `duck_lead_in_s ∈ [0.5, 15.0]`（默认 `3.5s`，长于 `4.5s` 自动吸附 180ms 呼吸谷）、`duck_gain ∈ [0.02, 0.60]`（默认 `0.15`，约 `-16.5 dB`）、半余弦淡出 `0.40s` / 尾韵回升 `0.78`；`.srt` 自动输出无重叠双行对照块。

---

## 四、 实证动态语速梯度与 Act 5 `0.80x / 1.0x` 影子跟读科学

### 4.1 100 条真实高管语料实证语速基准（100% 同步 `corpus_100_structured.json`）

传统 ESL 商务英语教材停留在 `110–135 WPM` 人工朗读，导致 B1–C1 学习者一进真实跨国会议就被甩出 `40–65 WPM` 语速断层。本剧全部语速标准严格锚定 M2 清洗验真后的百条真实大佬实证数据：

| 语料维度 | 清洗后 `en_clean` 中位数 | 原始基线 `en_raw` 中位数 | 清洗后均值 / 极值范围 (`WPM`) | 对本剧各场景语速的精确指导 |
| :--- | :---: | :---: | :---: | :--- |
| **全库 100 条汇总** | **`170.34 WPM`** | **`170.20 WPM`** | 均值 `173.72`（IQR `154.24–194.46`，极值 `125.31–227.45`） | 锚定全剧正片英文自然语速主带 **`150–185 WPM`** |
| **`AI`（硅谷前沿科技）** | **`194.55 WPM`** | `194.42 WPM` | 均值 `188.70`（`139.46–227.45`） | 硅谷 VC 估值对峙、算力架构辩论锁定 **`165–185 WPM`**（高频压迫、吐字清晰不糊词） |
| **`BUSINESS`（商业策略）** | **`170.40 WPM`** | `169.24 WPM` | 均值 `175.25`（`135.54–224.01`） | 董事会战略摊牌、组织重构、渠道谈判锁定 **`155–175 WPM`** |
| **`US_CHINA`（地缘与制造）** | **`160.33 WPM`** | `160.33 WPM` | 均值 `161.99`（`125.31–211.17`） | 伦敦旗舰零售、布鲁塞尔合规听证、关税与新加坡外交对谈锁定 **`145–165 WPM`** |
| **`FINANCE`（金融与宏观）** | **`159.40 WPM`** | `160.73 WPM` | 均值 `168.94`（`130.90–225.51`） | 估值拆解、做空反击、宏观周期警示锁定 **`145–165 WPM`**（重数字精准顿挫） |

### 4.2 Act 5 确定性 `atempo=0.80` 慢拆与 `>= 1.8s` 影子跟读机制

| 阶段 | 工程配置参数 | 实际输出语速 | 心理语言学与声学工程原理 |
| :--- | :--- | :---: | :--- |
| **Pass 1 · 慢速剖音拆解** | `playback_rate = 0.8`（`models.py` 合法范围 `[0.65, 1.35]`），**复用 `1.0x` 原生 Drama 3 干声缓存**，经 `mixer.py` 前置 FFmpeg **`atempo=0.800`**（WSOLA 保音高变速，位于声场 EQ 与 `loudnorm` 之前） | **`~120–145 WPM`**（精准落入实证最慢高管区间 `125–140 WPM`） | 零基频变调、零音色漂移、零额外 GPU 推理耗时；完整保留真实连读与核重音关系，同时让 B1 听众听清每一个弱读功能词与辅音爆破 |
| **Pass 2 · 原速影子跟读** | `playback_rate = 1.0` + 显式留白 **`gap_after_s >= 1.8s`**（标准推荐 **`2.2–3.0s`**，对应 5–12 词核心短语） | **`150–185 WPM`** 真实高管原速 | 基于 **Baddeley 工作记忆语音环路**（未复述表征在 `~2.0s` 内迅速衰减）与 **Swain 可理解输出假说**，逼迫学习者在黄金听觉残影期内立刻出声跟读，完成肌肉记忆固化 |

### 4.3 中英混合长句切分预算（`drama3_adapter.py` 实测规则）

对于 `lin_chen` 与 `zhou_mo` 的中英夹杂（`zh-en`）台词，若直接按中文字数切分会导致英文单词占比高的句子撑爆 Drama 3 单次 token 窗口。M1 引擎 `split_cue_into_subcues_for_drama3()` 已升级联合计量公式：
- **联合有效单元公式**：`effective_units = cjk_count + 2.2 * en_words`（默认阈值 `max_cjk_chars = 105`、`max_en_words = 65`）；
- **编剧单句硬控**：正片单条台词英文不超过 **`55` 词**、中文不超过 **`85` 字**（中英混合按联合单元 `<= 90` 控制），确保 95%+ 台词无需强制二次切片即可一次高保真吐字成型；若触发自动切片，中间子句自动插入 `0.16s` 自然换气气口，并完整继承 `playback_rate` 与 `acoustic_space`。

---

## 五、 双语同声源声纹克隆规范（`lin_chen` / `zhou_mo`）与试音门禁清单

### 5.1 同声源跨语种一致性采集铁律（衔接 M4 `v2_real_human_studio`）

双语广播剧最致命的出戏雷区是“主角说英文时像 A、切回中文独白突然变成 B”，或是中文声纹锚点直接驱动英文导致满嘴中式元音漂移。针对两位双语角色，M4 真人声纹采集强制执行以下规格：
1. **统一母带底规**：`ANCHOR_SCHEMA_VERSION = "v2_real_human_studio"`，**`44100 Hz` 单声道 PCM16 WAV**，集成响度标准化至 **`-16 LUFS`**，单条干声时长 **`10–18s`**，极低本底噪声（`SNR >= 45 dB`、无房间混响、无背景音乐），配 100% 逐字校对的同名 `.txt` 旁车文件，生产环境 **0% `edge-tts` / 合成音**。
2. **`lin_chen`（同声源真正双语母带策略）**：
   - 严选具备真实北美顶级科技/金融背景的**同一名 30–38 岁男性双语真人**录音棚干声，确保其英文具备纯正 General American 卷舌与连读、中文具备冷峻克制的现代普通话胸腔共鸣；
   - 锚点参考片段优先截取**英中自然切换且情绪沉稳克制**（语速英文 `~165 WPM`、中文 `~3.6 字/秒`）的黄金 12–16 秒独白，保证 Drama 3 跨语种克隆时音色基频（`F0`）与共振峰（Formants）完全锁死同一人物，既不把中式平调带入英文，也不把欧美洋腔带入中文内心独白。
3. **`zhou_mo`（深圳科技高管中文主干 + 精准英文术语）**：
   - 严选 32–40 岁现代干练大陆科技男中音近麦棚录干声（含 2–3 个清晰吐字的常见英文科技词，如 `AI / GPU / token`），确保其在中文主轴中穿插 `BOM cost`、`yield ramp` 等术语时自然无断层。
4. **纯英 6 角色（3 核心 + 3 精控客串）**：全部采自各自目标口音母语级/精英级真人录音棚访谈或演讲干声（`us_silicon_valley`、`uk_london_rp`、`us_nyc`、`intl_eu_legal`、`intl_indian_exec`、`intl_singapore_vc`），严禁跨口音混用。

### 5.2 产前声纹与口音试听门禁（`AUDITION_GLOBAL_EDGE` 量化验收清单）

在正式启动 Colab 96GB G4 批量渲染 `E001_VA/VB/VC/VD` 之前，必须先渲染并 100% 通过 `AUDITION_GLOBAL_EDGE` 试听包的以下 **8 项硬性门禁**：

| 门禁编号 | 核验维度 | 量化通过标准（Pass Gate） | 未通过处理动作 |
| :---: | :--- | :--- | :--- |
| **G1** | **跨语种音色一致性（`lin_chen`）** | `lin_chen` 英文公开谈判句与中文 `inner_monologue` 独白盲听确认为**同一声源人物**，无性别/年龄/共振峰漂移 | 替换或重裁 `v2_real_human_studio` 锚点区间，重录试听句 |
| **G2** | **美音 vs. 伦敦 RP 听觉区隔度** | 盲听 `victoria_vance`（SV 美音）与 `alistair_finch`（伦敦 RP）3 秒内 100% 区分口音与人物气场；零 `[wryly]` 中西部漂移 | 核查 `voice_casting_registry.json` 与锚点源，强制清洗错误标签 |
| **G3** | **国际客串 LFC 清晰度** | `henrik_lindqvist` / `rajiv_menon` / `wei_ling_tan` 试听句对 B1–C1 听众关键商业数字与术语辨识率 `100%`，零漫画化刻板印象 | 调整锚点源为语速更稳、吐字更清晰的精英访谈片段 |
| **G4** | **正片自然语速落点** | 全部纯英试听句实测语速落于 **`150–185 WPM`**（伦敦/欧陆法务 `145–165`、硅谷/纽约 `160–185`），无拖沓播音腔 | 检查标点停顿与 `stability` 档位，必要时微调参考锚点语速 |
| **G5** | **Act 5 `0.80x` 慢拆保音高测试** | `atempo=0.800` 处理后 `120–145 WPM` 音高零下沉、无金属颤音伪影，辅音连读清晰可拆 | 复核 `mixer.py:condition_dialogue_clip()` 前置 `atempo` 链路与输入采样率 |
| **G6** | **负间隔抢话与声场切换** | `boardroom` 抢话（`-0.15s`）接缝干净无爆音，`inner_monologue` 无洞穴混响，`phone_call` 电话带通辨识鲜明 | 校验 `acoustic_space` 赋值（确保 `boardroom` 无 `apad`、零 `mental_realm`） |
| **G7** | **本地 `faster-whisper` 双脚本 QA** | 全部 8 角色试音句一次通过 `evaluate_dialogue_qa()`：`char_recall >= 0.72`（混合句同时验 `CJK >= 4` & `EN >= 3`）、0 标签泄露、`duration_s >= 0.25s`、`peak_dbfs >= -45.0` | 触发 3 级重试阶梯或检查 `polyphones.py` 领域多音字映射 |
| **G8** | **母带广播响度合规** | `AUDITION_GLOBAL_EDGE` 终混立体声 WAV/MP3 实测集成响度 **`-16.0 ± 0.5 LUFS`**、真峰值 **`<= -1.0 dBTP`**、双行 `.srt` 零重叠 | 复核 `mixer.py` 终混限幅器与 SRT 时间戳钳平输出 |
