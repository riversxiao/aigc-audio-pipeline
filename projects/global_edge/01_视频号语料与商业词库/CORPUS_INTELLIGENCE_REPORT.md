# Global Edge（《跨境底牌：硅深暗战》）——百条视频号爆款语料实证情报报告

> **100% 程序实时聚合生成声明**：本报告由 `projects/global_edge/scripts/extract_100_clips_corpus.py` 基于规范化后的 `corpus_100_structured.json` 与 `executive_lexicon.json` 实时计算渲染，不含任何手工硬编码统计或墙钟时间戳，重复运行严格字节级一致。
> - **Schema 版本**：`1.0.0` ｜ **源文件**：`/tmp/arsenal_100_queue.json` ｜ **Google Drive ID**：`1K61WnLZKDEwW5QIwkc1BJ9SzOxRD-Gzj`
> - **源文件 SHA-256**：`525bd90c7ce4af3f0ccdef9d4e205a818237eb39ba11dcaa999b2691bb6fdb4c`

---

## 一、核心全景指标（100% 程序实时聚合）

| 指标维度 | 清洗后实证值（Full-85 `en_clean`） | 原始基线值（`en_raw`） | 工程与节目意义 |
| :--- | :---: | :---: | :--- |
| 切片总条数 (`total_clips`) | **100**（`25 × 4` 四大支柱均分） | `100` | 100% 唯一 `clip_id` 严格字符串主键，支持第一季 24 集无损双射分配 |
| 发布队列状态 | 已发布 **`9`** / 待发 **`91`** | `9` / `91` | 覆盖 `@一分钟想明白 1-Min Clarity` 现有爆款池与 91 条未发弹药 |
| 字幕总片段数 (`total_segments`) | **`1,408`** | `1,408` | 均长 `3.53s/句`，所有时间轴重叠已零损钳平 |
| 总有效时长 (`total_duration_sec`) | **`4,976.89s`**（**`82.95 min`**） | `4,976.89s` | 单条 `43.33–57.76s`（均值 `49.77s`），验证 45s 竖屏切片黄金时长 |
| 英文总词数（正则口径 / 空格口径） | **`14,409`** / `14,379` | `14,420` / `14,392` | Full-85 纠偏净变 `-11` 词（含剔除 `[snorts]` 与修复连写词） |
| 中文字幕总字符数 (`total_zh_chars`) | **`27,095`** | `27,095` | 每条切片均提供完整中英逐句对照，支撑双语潜台词与精读手册对齐 |
| 英文真实高管语速中位数 (`median_wpm`) | **`170.34 WPM`** | **`170.20 WPM`**（`170.2` 基线） | 直接锚定正片自然高管语速 `150–185 WPM` 工业标准 |
| 英文真实高管语速均值 (`mean_wpm`) | **`173.72 WPM`** | `173.86 WPM`（`173.9` 基线） | 远高于传统 ESL 慢速教材（`110–135 WPM`），直击 B1–C1 听觉卡壳 |
| 语速四分位与极值 (`p25–p75` / `min–max`) | **`154.24–194.46 WPM`** / `125.31–227.45` | `154.24–194.86` / `125.31–227.45` | 片尾 `0.80x` 慢拆落于 `~120–145 WPM`，恰位于最低自然语速区 |
| 独立原片 YouTube 频道数 (`unique_channels`) | **`64`** | `64` | 跨硅谷一线播客、华尔街电视网与顶级智库的多元权力场语源 |
| 爆款潜力评分均值 (`virality_mean`) | **`9.59`**（`9.2–9.9`） | `9.59` | 全量经冲突张力筛选的高密商业弹药 |
| ASR 规范化纠偏记录 | **`85/85` 规则命中 → `98` 处修复（`47` 条切片）** | `0` | `en_clean` 实现 100% 纯 ASCII、0 `[snorts]` 残余，且 `en_raw` 原样保留审计 |

## 二、四大内容支柱分布与实证语速梯度

| 支柱 (`topic_key`) | 切片数（已发/待发） | 字幕段数 | 总时长 / 均长（范围） | 英文词数（正则 / 空格） | 中文字符数 | 语速中位数 (`median`) | 语速均值 (`mean`) | 语速范围 (`min–max`) | 爆款均分 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`AI`**（AI · 前沿科技） | `25` (`2`/`23`) | `370` | `1268.46s` / `50.74s` (`44.00–56.36s`) | `3,985` / `3,981` | `7,352` | **`194.55`** *(raw `194.42`)* | `188.70` | `139.46–227.45` | `9.560` |
| **`BUSINESS`**（BUSINESS · 商业策略） | `25` (`2`/`23`) | `332` | `1222.78s` / `48.91s` (`43.50–57.76s`) | `3,573` / `3,564` | `6,751` | **`170.40`** *(raw `169.24`)* | `175.25` | `135.54–224.01` | `9.640` |
| **`FINANCE`**（FINANCE · 金融投资） | `25` (`2`/`23`) | `362` | `1265.32s` / `50.61s` (`45.17–55.92s`) | `3,563` / `3,558` | `6,774` | **`159.40`** *(raw `160.73`)* | `168.94` | `130.90–225.51` | `9.576` |
| **`US_CHINA`**（US_CHINA · 中美博弈） | `25` (`3`/`22`) | `344` | `1220.33s` / `48.81s` (`43.33–54.84s`) | `3,288` / `3,276` | `6,218` | **`160.33`** *(raw `160.33`)* | `161.99` | `125.31–211.17` | `9.572` |
| **全库合计 / 总计** | **`100`** (`9`/`91`) | **`1,408`** | **`4,976.89s`** / `49.77s` | **`14,409`** / `14,379` | **`27,095`** | **`170.34`** *(raw `170.20`)* | **`173.72`** | `125.31–227.45` | **`9.59`** |

- **实证语速梯度核心发现**：`AI` 支柱技术领袖语速中位数高达 **`194.55 WPM`**，比 `US_CHINA` 政策/宏观支柱（**`160.33 WPM`**）快出 **`34.22 WPM`**，也比 `FINANCE` 支柱（**`159.40 WPM`**）快出 **`35.15 WPM`**。这直接为《跨境底牌》提供声学表演标尺：硅谷技术/VC 对峙戏（`AI`/`BUSINESS`）采用偏高紧迫感语速（`165–185 WPM`），伦敦零售与华盛顿/布鲁塞尔合规博弈戏（`FINANCE`/`US_CHINA`）采用更沉稳的冷峻压迫节奏（`145–165 WPM`）。

## 三、高频原片频道（Top 15）与核心发言人图谱（Top 20）

### 3.1 高频来源频道 Top 15（全库共 64 个独立频道）

| 排名 | YouTube 频道 (`channel`) | 切片数 | 关联 `clip_id` 列表 |
| :---: | :--- | :---: | :--- |
| 1 | **Bloomberg Television** | `9` | `065_FIN`, `068_FIN`, `070_FIN`, `071_FIN`, `096_USC`, `073_FIN`, `074_FIN`, `075_FIN`, `030_AI` |
| 2 | **Lex Fridman** | `6` | `01_AI_DHH`, `04_USCHINA_Jensen`, `013_AI`, `022_AI`, `024_AI`, `051_BIZ` |
| 3 | **All-In Podcast** | `5` | `02_BIZ_Anthropic`, `012_AI`, `039_BIZ`, `040_BIZ`, `041_BIZ` |
| 4 | **CNBC** | `4` | `078_USC`, `079_USC`, `088_USC`, `090_USC` |
| 5 | **The Swedish Investor** | `4` | `059_FIN`, `063_FIN`, `069_FIN`, `072_FIN` |
| 6 | **Andrej Karpathy** | `3` | `006_AI`, `015_AI`, `018_AI` |
| 7 | **CNN** | `3` | `083_USC`, `026_AI`, `029_AI` |
| 8 | **The Economist** | `3` | `042_BIZ`, `094_USC`, `053_BIZ` |
| 9 | **Bloomberg Originals** | `2` | `037_BIZ`, `047_BIZ` |
| 10 | **Cleo Abram** | `2` | `007_AI`, `036_BIZ` |
| 11 | **CNBC Television** | `2` | `060_FIN`, `077_FIN` |
| 12 | **FINAiUS** | `2` | `055_FIN`, `058_FIN` |
| 13 | **Inside China Business** | `2` | `092_USC`, `093_USC` |
| 14 | **The Wall Street Journal** | `2` | `086_USC`, `043_BIZ` |
| 15 | **Y Combinator** | `2` | `044_BIZ`, `048_BIZ` |

### 3.2 高频发言人 Top 20（4 阶段确定性归因，100/100 非空全覆盖）

| 排名 | 发言人 / 旁白主体 (`inferred_speakers`) | 出现切片数 | 关联 `clip_id` 列表 |
| :---: | :--- | :---: | :--- |
| 1 | **Elon Musk** | `7` | `030_BIZ`, `031_BIZ`, `042_BIZ`, `043_BIZ`, `044_BIZ`, `053_BIZ`, `054_BIZ` |
| 2 | **Ray Dalio** | `6` | `03_FIN_Dalio`, `060_FIN`, `064_FIN`, `068_FIN`, `075_FIN`, `076_FIN` |
| 3 | **All-In Podcast (Hosts)** | `5` | `02_BIZ_Anthropic`, `012_AI`, `039_BIZ`, `040_BIZ`, `041_BIZ` |
| 4 | **Andrej Karpathy** | `5` | `006_AI`, `011_AI`, `015_AI`, `018_AI`, `025_AI` |
| 5 | **Bloomberg Television (Interviewer)** | `5` | `065_FIN`, `068_FIN`, `071_FIN`, `074_FIN`, `075_FIN` |
| 6 | **Jensen Huang** | `5` | `04_USCHINA_Jensen`, `007_AI`, `009_AI`, `012_AI`, `029_AI` |
| 7 | **Sam Altman** | `5` | `013_AI`, `014_AI`, `021_AI`, `027_AI`, `030_AI` |
| 8 | **Dario Amodei** | `4` | `010_AI`, `017_AI`, `023_AI`, `026_AI` |
| 9 | **The Swedish Investor (Narrator)** | `4` | `059_FIN`, `063_FIN`, `069_FIN`, `072_FIN` |
| 10 | **Howard Marks** | `3` | `062_FIN`, `071_FIN`, `074_FIN` |
| 11 | **Jamie Dimon** | `3` | `061_FIN`, `065_FIN`, `073_FIN` |
| 12 | **Mark Zuckerberg** | `3` | `036_BIZ`, `037_BIZ`, `051_BIZ` |
| 13 | **Stanley Druckenmiller** | `3` | `055_FIN`, `056_FIN`, `057_FIN` |
| 14 | **The Economist (Interviewer)** | `3` | `042_BIZ`, `094_USC`, `053_BIZ` |
| 15 | **CNBC (Narrator)** | `2` | `078_USC`, `079_USC` |
| 16 | **CNN (Interviewer)** | `2` | `026_AI`, `029_AI` |
| 17 | **FINAiUS (Narrator)** | `2` | `055_FIN`, `058_FIN` |
| 18 | **Inside China Business (Narrator)** | `2` | `092_USC`, `093_USC` |
| 19 | **Jeff Bezos** | `2` | `033_BIZ`, `034_BIZ` |
| 20 | **Kevin Rudd** | `2` | `094_USC`, `097_USC` |

## 四、语速两极样本（Top 5 最慢 vs Top 5 最快）与节目定速锚点

### 4.1 语速最慢 Top 5 切片（深沉压迫与外交稳重范式）

| 排名 | `clip_id` | 支柱 | 语速 (`WPM`) | 时长 (`s`) | 归因发言人 | 英文标题钩子 (`en_title_hook`) |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| 1 | `04_USCHINA_Jensen` | `US_CHINA` | **`125.31`** | `47.88` | Jensen Huang, Lex Fridman | Exclude China vs Shared Flywheel |
| 2 | `092_USC` | `US_CHINA` | **`130.26`** | `52.97` | Inside China Business (Narrator) | ASML Ban vs Chinese EUV |
| 3 | `082_USC` | `US_CHINA` | **`130.46`** | `49.67` | Behind Asia (Narrator) | Tiny Flaw vs \$550M Loss |
| 4 | `03_FIN_Dalio` | `FINANCE` | **`130.90`** | `55.92` | Ray Dalio, The Diary Of A CEO (Host) | Gold vs Bitcoin |
| 5 | `087_USC` | `US_CHINA` | **`131.22`** | `51.67` | Kishore Mahbubani | Zero-Sum Rivalry vs Asian Pragmatism |

### 4.2 语速最快 Top 5 切片（硅谷高频连珠炮与交易室高压范式）

| 排名 | `clip_id` | 支柱 | 语速 (`WPM`) | 时长 (`s`) | 归因发言人 | 英文标题钩子 (`en_title_hook`) |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| 1 | `025_AI` | `AI` | **`227.45`** | `48.01` | Andrej Karpathy, No Priors (Host) | Raw Token Predictor vs Digital Persona |
| 2 | `065_FIN` | `FINANCE` | **`225.51`** | `46.03` | Jamie Dimon, Bloomberg Television (Interviewer) | America's Edge vs Tariff Chaos |
| 3 | `037_BIZ` | `BUSINESS` | **`224.01`** | `54.64` | Mark Zuckerberg, Bloomberg Originals (Interviewer) | Closed Gatekeepers vs Open Distillation |
| 4 | `027_AI` | `AI` | **`223.60`** | `50.18` | Sam Altman, Alex Heath | Made Without AI vs New Art |
| 5 | `036_BIZ` | `BUSINESS` | **`222.35`** | `53.43` | Mark Zuckerberg | One God AI vs Million Agents |

- **定速工程映射**：正片飙戏锁定 **`150–185 WPM`**（紧贴全库实证中位数 `170.34 WPM` / 原始 `170.20 WPM` 与四分位 `154.24–194.46 WPM`）；片尾 3 分钟黑话拆局通过确定性 FFmpeg `atempo=0.80` 保音高降至 **`~120–145 WPM`**（对应上表最慢高管区间），随后以 `1.0x` 原速配合 `>= 1.8s` 跟读窗完成肌肉记忆固化。

## 五、数据异常诊断与 ASR 纠偏审计台账

### 5.1 结构性异常与清洗核验摘要

| 审计维度 | 实测结果 | 工程防御处置 |
| :--- | :--- | :--- |
| 数字前缀冲突 (`prefix_collisions`) | **2 组**：`030` → `030_BIZ`, `030_AI`；`054` → `054_FIN`, `054_BIZ` | 全链路严格以完整字符串 `clip_id` 为主键，严禁解析整数前缀，4 条冲突切片 100% 完整留存 |
| 缺失数字编号 (`missing_numeric_prefixes`) | **2 处**：`028`, `046` | 仅作审计记录，不依赖连续 `001..100` 编号假设 |
| 混合相对路径 MP4 (`relative_mp4_path_clip_ids`) | **5 条种子切片**：`01_AI_DHH`, `02_BIZ_Anthropic`, `03_FIN_Dalio`, `04_USCHINA_Jensen`, `05_USCHINA_Robots`（其余 95 条为绝对路径） | ETL 纯内存处理 JSON 元数据，不假设本地 MP4 路径存在 |
| 字幕时间轴微重叠 (`subtitle_overlaps_repaired`) | **`36` 对重叠**（跨 **`24` 条切片**，`0.04–0.09s`） | 在 `subtitles_clean` 中将 `prev.end_sec` 钳平至 `curr.start_sec`，1,408 段 100% 严格单调无重叠，原始重叠记录完整归档 |
| 非语音标签 `[snorts]` 清洗 | `087_USC` 原始 `en_raw` 保留 `[snorts]` 审计；全库 100 条 `en_clean` 及 1,408 条 `subtitles_clean` 中 **0 残余** | 正则 `\s*\[snorts\]\s*` 精准剥离；同时完整保留 `063_FIN` 合法财务缩写 `(or DCF)` |
| 非 ASCII 字符清洗 | `063_FIN` `U+2019` → `'`，`100_USC` `19° of freedom` → `19 degrees of freedom` | 全库 100 条 `en_clean` 经程序断言为 **100% 纯 ASCII** |
| 切片冷切边界统计 | `30` 条句中起切（首字母小写），`30` 条句尾无终结标点 | 台本引用短语均提取完整语法语块，不生搬冷切残句 |

### 5.2 全量 ASR 纠偏执行台账（`85` 条规则 / `98` 处逐段修复 / `47` 条切片）

| # | `clip_id` | 句段 `seg_idx` | 原始错词 (`raw`) | 规范化修复 (`clean`) | 纠偏依据 (`reason`) |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 1 | `031_BIZ` | `0` | `Proby fix` | `Probably fix` | Truncated ASR word Proby->Probably |
| 2 | `031_BIZ` | `4` | `these Ms` | `these mats` | Fiberglass mats (phrase+clip-scoped; protects Ms./MS) |
| 3 | `031_BIZ` | `5` | `these Ms` | `these mats` | Fiberglass mats (phrase+clip-scoped; protects Ms./MS) |
| 4 | `031_BIZ` | `7` | `NBA noise vibration hes` | `NVH (noise, vibration, harshness)` | Automotive NVH team (ZH: NVH噪声振动团队) |
| 5 | `031_BIZ` | `9` | `dber cartoon` | `Dilbert cartoon` | Dilbert cartoon reference |
| 6 | `031_BIZ` | `10` | `dber cartoon` | `Dilbert cartoon` | Dilbert cartoon reference |
| 7 | `031_BIZ` | `11` | `five glass mats` | `fiberglass mats` | Fiberglass battery mats (ZH: 玻璃纤维垫) |
| 8 | `055_FIN` | `0` | `for truckee` | `for Druckenmiller` | Cross-seg split truckee / miller -> Druckenmiller (part 1) |
| 9 | `055_FIN` | `1` | `miller he got out` | `he got out` | Cross-seg split truckee / miller absorbed into seg 0 (part 2) |
| 10 | `055_FIN` | `4` | `drucker miller` | `Druckenmiller` | Stanley Druckenmiller (ZH: 德鲁肯米勒) |
| 11 | `055_FIN` | `4` | `sorrows` | `Soros` | George Soros (clip-scoped, ZH: 索罗斯) |
| 12 | `055_FIN` | `5` | `to colossus` | `to cut losses` | ASR phonetic garble cut losses->colossus (ZH: 果断止损) |
| 13 | `055_FIN` | `11` | `sorrows` | `Soros` | George Soros (clip-scoped, ZH: 索罗斯) |
| 14 | `055_FIN` | `12` | `drucker miller` | `Druckenmiller` | Stanley Druckenmiller (ZH: 德鲁肯米勒) |
| 15 | `079_USC` | `0` | `former Google Co Eric Schmidt` | `former Google CEO Eric Schmidt` | Title CEO garbled to Co (ZH: 前谷歌CEO) |
| 16 | `079_USC` | `8` | `open AI Mo really is` | `OpenAI's moat really is` | Business moat garbled to Mo (ZH: OpenAI的护城河) |
| 17 | `079_USC` | `8` | `chat gbt` | `ChatGPT` | Product name ChatGPT |
| 18 | `079_USC` | `11` | `anthropics` | `Anthropic's` | Possessive Anthropic's (continues into seg 12 Claude) |
| 19 | `079_USC` | `12` | `clad` | `Claude` | Anthropic's Claude (ZH: Anthropic Claude) |
| 20 | `032_BIZ` | `1` | `as a100` | `as a $100` | Glued article+number at end of seg 1 (continues into seg 2 billion) |
| 21 | `056_FIN` | `1` | `add in capacity` | `adding capacity` | ASR split gerund adding->add in (ZH: 扩产) |
| 22 | `080_USC` | `2` | `cuttingedge` | `cutting-edge` | Auto-caption dropped hyphen |
| 23 | `080_USC` | `9` | `inhouse` | `in-house` | Auto-caption dropped hyphen |
| 24 | `009_AI` | `3` | `on prem` | `on-prem` | Hyphenate standard term on-prem (enables verbatim lexicon match) |
| 25 | `033_BIZ` | `1` | `16 million with an M` | `60 million with an M` | Bezos reiterating \$60 million from 5 words prior (ZH: 6000万美元) |
| 26 | `010_AI` | `0` | `like5 trillion` | `like $5 trillion` | Missing space and \$ before 5 trillion (ZH: 五万亿美元) |
| 27 | `058_FIN` | `0` | `howard marx` | `Howard Marks` | Oaktree co-founder Howard Marks (ZH: 霍华德·马克斯) |
| 28 | `058_FIN` | `4` | `often than ron` | `often than wrong` | ASR garble wrong->ron (ZH: 看对的次数总会比看错多) |
| 29 | `058_FIN` | `6` | `howard mark's` | `Howard Marks's` | Possessive Howard Marks's research group |
| 30 | `082_USC` | `2` | `one tiny floor` | `one tiny flaw` | Wafer defect flaw (ZH: 一个微小瑕疵) |
| 31 | `082_USC` | `7` | `nanometerclass` | `nanometer-class` | Auto-caption dropped hyphen |
| 32 | `082_USC` | `10` | `cuttingedge` | `cutting-edge` | Auto-caption dropped hyphen |
| 33 | `082_USC` | `11` | `Tynan Science Park` | `Tainan Science Park` | TSMC Tainan Science Park (ZH: 台南科学园区) |
| 34 | `011_AI` | `8` | `AI sent` | `AI Ascent` | Sequoia Capital's AI Ascent summit (ZH: 红杉峰会) |
| 35 | `011_AI` | `14` | `open claw` | `OpenClaw` | Coding agent OpenClaw (ZH: OpenClaw) |
| 36 | `011_AI` | `15` | `cloud code` | `Claude Code` | Anthropic Claude Code (ZH: Claude Code) |
| 37 | `035_BIZ` | `6` | `50 000 jobs` | `50,000 jobs` | Missing thousands comma in 50,000 |
| 38 | `084_USC` | `8` | `Californiabased` | `California-based` | Auto-caption dropped hyphen |
| 39 | `037_BIZ` | `0` | `met AI be` | `Meta AI be` | Meta AI assistant (ZH: Meta AI) |
| 40 | `037_BIZ` | `5` | `45 billion parameters` | `405 billion parameters` | Llama 3.1 flagship is 405B (9x numeric ASR error; ZH: 4050亿参数) |
| 41 | `085_USC` | `8` | `chakyang` | `Zhejiang` | Morris Chang birthplace Ningbo, Zhejiang (ZH: 浙江宁波) |
| 42 | `014_AI` | `9` | `Hammarabi` | `Hammurabi` | Historical spelling of Hammurabi (ZH: 汉谟拉比法典) |
| 43 | `038_BIZ` | `4` | `Teal` | `Thiel` | Peter Thiel (ZH: 蒂尔) |
| 44 | `038_BIZ` | `6` | `Teal` | `Thiel` | Peter Thiel (ZH: 蒂尔) |
| 45 | `038_BIZ` | `7` | `Teal` | `Thiel` | Peter Thiel (ZH: 蒂尔) |
| 46 | `038_BIZ` | `10` | `Teal` | `Thiel` | Peter Thiel (ZH: 蒂尔) |
| 47 | `086_USC` | `0` | `Kaiser Supply Chain` | `kinds of supply chain` | ASR phonetic garble kinds of->Kaiser |
| 48 | `015_AI` | `0` | `grock 3` | `Grok 3` | xAI model name Grok 3 |
| 49 | `015_AI` | `4` | `grock 3` | `Grok 3` | xAI model name Grok 3 |
| 50 | `015_AI` | `6` | `Claud` | `Claude` | Anthropic Claude (word boundary avoids Claude->Claudee) |
| 51 | `015_AI` | `8` | `programming l language` | `programming language` | Stray single-letter ASR stutter l |
| 52 | `039_BIZ` | `10` | `SAS software` | `SaaS software` | Software-as-a-Service SaaS (ZH: SaaS软件) |
| 53 | `063_FIN` | `13` | `’` | `'` | Normalize Unicode right apostrophe U+2019 to ASCII ' |
| 54 | `087_USC` | `3` | `[snorts]` | `(stripped)` | Strip non-speech bracket tag [snorts] |
| 55 | `064_FIN` | `0` | `tight money suit` | `tight money soon` | ASR phonetic garble soon->suit |
| 56 | `064_FIN` | `1` | `easy money suit` | `easy money soon` | ASR phonetic garble soon->suit |
| 57 | `018_AI` | `0` | `1,24 tokens` | `1,024 tokens` | GPT-2 context is 1,024 tokens (ZH: 1024) |
| 58 | `018_AI` | `2` | `1,24 tokens` | `1,024 tokens` | GPT-2 context is 1,024 tokens (ZH: 1024) |
| 59 | `018_AI` | `13` | `project called lm.` | `project called llm.c.` | Karpathy's llm.c repo (ZH: 开源项目llm.c里) |
| 60 | `042_BIZ` | `6` | `Kimik 3` | `Kimi K3` | Moonshot Kimi K3 (verified verbatim in 078_USC[8]) |
| 61 | `090_USC` | `5` | `Jipu` | `Zhipu` | Chinese AI lab Zhipu / Z.ai (ZH: 智谱) |
| 62 | `043_BIZ` | `0` | `stepped literally on the floor` | `slept literally on the floor` | Musk sleeping on factory floor (ZH: 直接睡在工厂地上) |
| 63 | `067_FIN` | `3` | `banks air for the 2008` | `banks after the 2008` | ASR garble after->air for (ZH: 2008年金融危机后) |
| 64 | `044_BIZ` | `4` | `sliding our company is insane` | `starting a rocket company is insane` | Musk YC quote (ZH: 创办一家火箭公司绝对是彻头彻尾的疯子行为) |
| 65 | `044_BIZ` | `6` | `to improve ROC` | `to improve rocket` | Continues into seg 7 technology (ZH: 火箭技术) |
| 66 | `021_AI` | `15` | `Abene` | `Abilene` | Stargate Texas site Abilene (ZH: 得州阿比林) |
| 67 | `045_BIZ` | `0` | `Palanteer` | `Palantir` | Company name Palantir |
| 68 | `045_BIZ` | `1` | `Palanteer` | `Palantir` | Company name Palantir |
| 69 | `045_BIZ` | `3` | `Palunteers` | `Palantir's` | Possessive Palantir's AI (ZH: Palantir的算法) |
| 70 | `045_BIZ` | `7` | `Palanteer` | `Palantir` | Company name Palantir |
| 71 | `045_BIZ` | `10` | `Palanteer` | `Palantir` | Company name Palantir |
| 72 | `045_BIZ` | `10` | `Sham Sankar` | `Shyam Sankar` | Palantir CTO Shyam Sankar spelling |
| 73 | `069_FIN` | `4` | `law of holds` | `law of holes` | First Law of Holes (matches seg 5 law of holes) |
| 74 | `069_FIN` | `7` | `law of holds` | `law of holes` | First Law of Holes (matches seg 5 law of holes) |
| 75 | `069_FIN` | `9` | `caught in half` | `cut in half` | Einhorn quote: down 80% then cut in half (ZH: 腰斩) |
| 76 | `093_USC` | `0` | `BD's` | `BYD's` | Automaker BYD's (ZH: 比亚迪) |
| 77 | `093_USC` | `5` | `$122,000` | `$12,000` | BYD Seagull <\$12,000 (en_title_hook: \$12K EV, ZH: 1.2万) |
| 78 | `093_USC` | `6` | `$115,000` | `$15,000` | \$12,000 + 25% tariff = \$15,000 (ZH: 1.5万) |
| 79 | `022_AI` | `10` | `non-spike in neural networks` | `non-spiking neural networks` | Matches seg 8 non-spiking neural networks in same clip |
| 80 | `047_BIZ` | `9` | `10 000 hours` | `10,000 hours` | Missing thousands comma in 10,000 |
| 81 | `070_FIN` | `7` | `tor rate` | `torrid rate` | Spent at a torrid rate (ZH: 惊人的速度) |
| 82 | `070_FIN` | `8` | `a trillion change` | `a trillion and change` | Idiom a trillion and change (ZH: 一万多亿美元) |
| 83 | `071_FIN` | `4` | `company who's supposed` | `company who's exposed` | Continues into seg 5 to AI (ZH: 押注AI浪潮) |
| 84 | `072_FIN` | `9` | `stores of physical` | `stores are physical` | ASR garble are->of (ZH: 都在地面实体店) |
| 85 | `096_USC` | `7` | `people in the developed countries` | `people in the developing countries` | Global South developing countries (ZH: 发展中国家) |
| 86 | `050_BIZ` | `9` | `r d v span` | `R&D spend` | R&D spend (ZH: 研发预算) |
| 87 | `073_FIN` | `5` | `gets cast robbery` | `is a catastrophe` | Default catastrophe (removes cast robbery grammatically) |
| 88 | `051_BIZ` | `4` | `gp4` | `GPT-4` | OpenAI model GPT-4 |
| 89 | `052_BIZ` | `3` | `workingclass` | `working-class` | Auto-caption dropped hyphen |
| 90 | `099_USC` | `0` | `do announcement` | `dollar announcement` | \$500 billion dollar announcement |
| 91 | `099_USC` | `6` | `Mas son` | `Masayoshi Son` | SoftBank CEO Masayoshi Son (ZH: 孙正义) |
| 92 | `099_USC` | `7` | `Larry Ellison and Arison and` | `Larry Ellison` | Deduplicate garbled stutter without doubling Larry Ellison |
| 93 | `099_USC` | `7` | `Sam Alman` | `Sam Altman` | OpenAI CEO Sam Altman |
| 94 | `100_USC` | `1` | `Brainet 2.0` | `BrainNet 2.0` | UBTECH BrainNet 2.0 (ZH: BrainNet 2.0) |
| 95 | `100_USC` | `9` | `UBEC` | `UBTECH` | Robotics firm UBTECH (matches 095_USC & ZH: 优必选) |
| 96 | `100_USC` | `10` | `19° of freedom` | `19 degrees of freedom` | ASR converted degrees to U+00B0 (ZH: 19个自由度) |
| 97 | `054_BIZ` | `3` | `totally shelf` | `totally shelved` | Past participle shelved (ZH: 束之高阁) |
| 98 | `054_BIZ` | `4` | `crude mission` | `crewed mission` | Crewed Mars mission (ZH: 载人登陆火星) |

## 六、实证语料缺口审计（Gap Audit）与 70/30 词源铁律核验

为彻底杜绝“把原语料中不存在的渠道/隐私词硬说成出自切片”的伪引注风险，ETL 脚本在全库 100 条 `en_clean` 上实时执行正则扫描：

| 维度分组 | 目标检索词 | 正则表达式 | 命中总次数 | 命中切片数 | 命中 `clip_id` | 词源定性与策略说明 |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| Retail & Channel | `Best Buy` | `\bBest\s+Buy\b` | **`0`** | `0` | `[]` | 纯 world_bridge（渠道剧情世界观补齐） |
| Retail & Channel | `Selfridges` | `\bSelfridges\b` | **`0`** | `0` | `[]` | 纯 world_bridge（伦敦旗舰渠道世界观补齐） |
| Retail & Channel | `slotting fee` | `\bslotting\s+fees?\b` | **`0`** | `0` | `[]` | 纯 world_bridge（见 LEX_097） |
| Retail & Channel | `chargeback` | `\bchargebacks?\b` | **`0`** | `0` | `[]` | 纯 world_bridge（见 LEX_098） |
| Retail & Channel | `MOQ` | `\bMOQs?\b` | **`0`** | `0` | `[]` | 纯 world_bridge（见 LEX_099） |
| Retail & Channel | `sell-through` | `\bsell[\s\-]through\b` | **`0`** | `0` | `[]` | 纯 world_bridge（见 LEX_100） |
| Retail & Channel | `shelf space` | `\bshelf\s+space\b` | **`0`** | `0` | `[]` | 纯 world_bridge（见 LEX_107） |
| Retail & Channel | `channel` | `\bchannels?\b` | **`0`** | `0` | `[]` | 纯 world_bridge（渠道谈判术语需桥接） |
| Retail & Channel | `pricing` | `\bpricing\b` | **`0`** | `0` | `[]` | 字面 0 次（邻近词 price/prices 出现于 7 条切片） |
| Retail & Channel (Adjacent) | `retail` | `\bretail\w*\b` | **`2`** | `2` | `067_FIN`, `072_FIN` | 邻近锚点：067_FIN 散户交易 / 072_FIN 电商零售 |
| Retail & Channel (Adjacent) | `consumer` | `\bconsumers?\b` | **`3`** | `2` | `070_FIN`, `095_USC` | 邻近锚点：070_FIN / 095_USC 消费级新品类 |
| Retail & Channel (Adjacent) | `margin` | `\bmargins?\b` | **`1`** | `1` | `077_FIN` | 邻近锚点：077_FIN net interest margin |
| Privacy, Legal & Geo | `GDPR` | `\bGDPR\b` | **`0`** | `0` | `[]` | 纯 world_bridge（见 LEX_109 / LEX_118） |
| Privacy, Legal & Geo | `privacy` | `\bprivacy\b` | **`0`** | `0` | `[]` | 纯 world_bridge（欧盟隐私合规线需桥接） |
| Privacy, Legal & Geo | `compliance` | `\bcompliance\b` | **`0`** | `0` | `[]` | 纯 world_bridge（跨境合规审计需桥接） |
| Privacy, Legal & Geo | `lawsuit` | `\blawsuits?\b` | **`0`** | `0` | `[]` | 纯 world_bridge（法务诉讼线需桥接） |
| Privacy, Legal & Geo | `antitrust` | `\bantitrust\b` | **`0`** | `0` | `[]` | 纯 world_bridge（反垄断线需桥接） |
| Privacy, Legal & Geo | `sanctions` | `\bsanctions?\b` | **`0`** | `0` | `[]` | 纯 world_bridge（制裁线需桥接） |
| Privacy, Legal & Geo | `decoupling` | `\bdecoupl\w*\b` | **`0`** | `0` | `[]` | 纯 world_bridge（地缘脱钩线需桥接） |
| Privacy, Legal & Geo | `export ban (literal)` | `\bexport\s+bans?\b` | **`0`** | `0` | `[]` | 字面 0 次（实为 042_BIZ 'banned the export' 及 092_USC 'barred'/'cut off'） |
| Privacy, Legal & Geo (Adjacent) | `tariff` | `\btariffs?\b` | **`4`** | `2` | `065_FIN`, `093_USC` | 邻近锚点：065_FIN / 093_USC 25% 关税成本 |
| Privacy, Legal & Geo (Adjacent) | `regulation` | `\bregulat\w*\b` | **`1`** | `1` | `064_FIN` | 邻近锚点：064_FIN 宏观监管 |
| Privacy, Legal & Geo (Adjacent) | `guardrails` | `\bguardrails?\b` | **`1`** | `1` | `019_AI` | 邻近锚点：019_AI rule-based guardrails |
| Privacy, Legal & Geo (Adjacent) | `on-prem` | `\bon-prem\b` | **`1`** | `1` | `009_AI` | 规则 #40 归一后命中 009_AI（原文本为 'on prem'） |
| Privacy, Legal & Geo (Adjacent) | `supply chain` | `\bsupply\s+chains?\b` | **`4`** | `3` | `086_USC`, `092_USC`, `045_BIZ` | 邻近锚点：045_BIZ / 086_USC / 092_USC |
| Privacy, Legal & Geo (Adjacent) | `chip` | `\bchips?\b` | **`21`** | `8` | `078_USC`, `080_USC`, `081_USC`, `082_USC`, `085_USC`, `086_USC`, `088_USC`, `042_BIZ` | 邻近锚点：半导体与算力博弈主轴 |

- **70/30 词源铁律实时核验结果**：本工程 `executive_lexicon.json` 共计 **`120`** 条商业英语高管词条，其中 `source_type == "corpus"` 占比 **`96/120 (80.0%)`**（远高于 `PROJECT.md` `>= 70%` 合同红线及 M2 `>= 75%` 强化门槛，且 100% 逐词通过所属 `clip_id` 的 `en_clean` 精确子串验真），`source_type == "world_bridge"` 占比 **`24/120 (20.0%)`**（严格设 `clip_ids: []` 且全库 100 条 `en_clean` 零碰撞，专职补齐 Best Buy / Selfridges 零售谈判、GDPR 数据驻留与深圳硬件量产桥梁词）。

## 七、高管黑话词库总览与 E001 五条种子切片 / 八大必考词组核验

### 7.1 词库结构分布（`executive_lexicon.json`，共 120 条）

| 类别 (`category`) | 中文定位 | 词条数 | 词源类型 |
| :--- | :--- | :---: | :---: |
| `executive_hedging_framing` | 高管立场控场与礼貌带刀框架 (Executive Hedging & Framing) | **`24`** | `corpus` |
| `vc_valuation_finance` | 融资估值、财报反杀与宏观金融 (VC Valuation & Finance) | **`24`** | `corpus` |
| `ai_compute_product` | AI 算力经济学与产品工程 (AI Compute & Product) | **`24`** | `corpus` |
| `tariffs_supply_chain_geopolitics` | 关税、供应链与地缘合规博弈 (Tariffs, Supply Chain & Geopolitics) | **`24`** | `corpus` |
| `retail_channel_bridge` | 欧美大渠道零售谈判桥梁词 (Retail Channel World-Bridge) | **`12`** | `world_bridge` |
| `compliance_hardware_bridge` | 欧美合规与深圳硬件量产桥梁词 (Compliance & Hardware World-Bridge) | **`12`** | `world_bridge` |

- **CEFR 难度分布**：`B1`: `1` 条、`B2`: `39` 条、`C1`: `75` 条、`C2`: `5` 条（`B2+C1` 合计 **`114/120` = `95.0%`**，精准锚定 B1–C1 职场进阶听众）。
- **原语料覆盖广度**：96 条 `corpus` 词条共覆盖 **`70 / 100`** 条独立切片（`AI`: `17`、`BUSINESS`: `13`、`FINANCE`: `20`、`US_CHINA`: `20`）。

### 7.2 E001 五条共享种子切片验真

| 种子 `clip_id` | 支柱 | 频道 | 归因发言人 | 语速 (`WPM`) | 核心商业议题 (`hook_line_2`) |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **`02_BIZ_Anthropic`** | `BUSINESS` | All-In Podcast | All-In Podcast (Hosts) | `164.13` | Anthropic招股书真相 |
| **`012_AI`** | `AI` | All-In Podcast | Jensen Huang, All-In Podcast (Hosts) | `163.05` | 黄仁勋算透五百亿账本 |
| **`039_BIZ`** | `BUSINESS` | All-In Podcast | All-In Podcast (Hosts) | `181.82` | 万亿AI市场极简算术 |
| **`090_USC`** | `US_CHINA` | CNBC | CNBC (Commentator) | `188.80` | 华尔街漏算的中国AI杀招 |
| **`059_FIN`** | `FINANCE` | The Swedish Investor | The Swedish Investor (Narrator) | `141.16` | 巴菲特估值灵魂第二问 |

### 7.3 E001 八大必考词组（13 条原话短语）100% 验真矩阵

| 必考分组 | `phrase_id` | 精确英文原话 (`phrase_en`) | 词库分类 | 归属种子 `clip_id` | `en_clean` 验真 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| Group #1 | `LEX_025` | `phantom number` | `vc_valuation_finance` | `02_BIZ_Anthropic` | PASS |
| Group #2a | `LEX_026` | `not a cash loss` | `vc_valuation_finance` | `02_BIZ_Anthropic` | PASS |
| Group #2b | `LEX_027` | `flowed through into the income statement` | `vc_valuation_finance` | `02_BIZ_Anthropic` | PASS |
| Group #3 | `LEX_028` | `capital-efficient` | `vc_valuation_finance` | `02_BIZ_Anthropic` | PASS |
| Group #4a | `LEX_049` | `10 times the throughput` | `ai_compute_product` | `012_AI` | PASS |
| Group #4b | `LEX_001` | `Pick your favorite number` | `executive_hedging_framing` | `012_AI` | PASS |
| Group #5 | `LEX_002` | `In other words` | `executive_hedging_framing` | `039_BIZ`, `066_FIN` | PASS |
| Group #6a | `LEX_050` | `eating into budgets` | `ai_compute_product` | `090_USC` | PASS |
| Group #6b | `LEX_003` | `a really hard trade-off` | `executive_hedging_framing` | `090_USC` | PASS |
| Group #7a | `LEX_004` | `What is good enough` | `executive_hedging_framing` | `090_USC` | PASS |
| Group #7b | `LEX_051` | `run this thing a million times` | `ai_compute_product` | `090_USC` | PASS |
| Group #8a | `LEX_029` | `upside` | `vc_valuation_finance` | `059_FIN`, `062_FIN`, `071_FIN` | PASS |
| Group #8b | `LEX_030` | `When are you going to get it` | `vc_valuation_finance` | `059_FIN` | PASS |

### 7.4 全量 120 条高管黑话词库分类索引（带 `clip_id` 溯源）

| `phrase_id` | 英文高管原话 (`phrase_en`) | 分类 | CEFR | 词源 | 溯源 `clip_ids` | 中式直译雷区 (`chinglish_trap`) |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| `LEX_001` | `Pick your favorite number` | `executive_hedging_framing` | `C1` | `corpus` | `012_AI` | You can choose any number you want, it doesn't matter. |
| `LEX_002` | `In other words` | `executive_hedging_framing` | `B2` | `corpus` | `039_BIZ`, `066_FIN` | That is to say / Let me explain simply to you. |
| `LEX_003` | `a really hard trade-off` | `executive_hedging_framing` | `B2` | `corpus` | `090_USC` | a very difficult choice between two bad things |
| `LEX_004` | `What is good enough` | `executive_hedging_framing` | `B2` | `corpus` | `090_USC` | Is the quality okay enough for us to use? |
| `LEX_005` | `a fair criticism` | `executive_hedging_framing` | `C1` | `corpus` | `027_AI` | Your blame is very reasonable and I admit my fault. |
| `LEX_006` | `at the end of the day` | `executive_hedging_framing` | `B2` | `corpus` | `026_AI` | Finally speaking / In the final analysis |
| `LEX_007` | `the reality is` | `executive_hedging_framing` | `B2` | `corpus` | `049_BIZ` | The true fact is that... |
| `LEX_008` | `completely refuted` | `executive_hedging_framing` | `C1` | `corpus` | `02_BIZ_Anthropic` | totally proved wrong by our evidence |
| `LEX_009` | `I really like that framing` | `executive_hedging_framing` | `C1` | `corpus` | `011_AI` | I agree with your way of speaking very much. |
| `LEX_010` | `in the long run` | `executive_hedging_framing` | `B1` | `corpus` | `058_FIN` | after a very long time in the future |
| `LEX_011` | `let alone` | `executive_hedging_framing` | `C1` | `corpus` | `099_USC` | not to mention / even less possible is... |
| `LEX_012` | `orders of magnitude` | `executive_hedging_framing` | `C1` | `corpus` | `008_AI` | many times bigger / a huge gap in numbers |
| `LEX_013` | `higher level of abstraction` | `executive_hedging_framing` | `C1` | `corpus` | `013_AI` | more high-level and conceptual thinking |
| `LEX_014` | `working backwards from` | `executive_hedging_framing` | `C1` | `corpus` | `025_AI` | thinking from the final result back to the start |
| `LEX_015` | `singing a different tune` | `executive_hedging_framing` | `C1` | `corpus` | `079_USC` | changing his opinion completely now |
| `LEX_016` | `the game has changed` | `executive_hedging_framing` | `B2` | `corpus` | `079_USC` | The rules of competition are totally different now. |
| `LEX_017` | `leaning into the future` | `executive_hedging_framing` | `C1` | `corpus` | `034_BIZ` | actively embracing future market trends |
| `LEX_018` | `no hedge on earth` | `executive_hedging_framing` | `C2` | `corpus` | `010_AI` | no financial tool in the world can protect us |
| `LEX_019` | `good for it` | `executive_hedging_framing` | `C1` | `corpus` | `021_AI` | they really have enough money to pay back |
| `LEX_020` | `polite modulations` | `executive_hedging_framing` | `C2` | `corpus` | `094_USC` | polite changes of speaking tone in diplomacy |
| `LEX_021` | `in hindsight` | `executive_hedging_framing` | `C1` | `corpus` | `077_FIN` | looking back after everything already happened |
| `LEX_022` | `stick to their guns` | `executive_hedging_framing` | `C1` | `corpus` | `073_FIN` | refuse to compromise their original position |
| `LEX_023` | `where the puck is` | `executive_hedging_framing` | `C1` | `corpus` | `056_FIN` | only looking at the current market instead of the future |
| `LEX_024` | `All Hands meeting` | `executive_hedging_framing` | `B2` | `corpus` | `033_BIZ` | a whole-company employee meeting |
| `LEX_025` | `phantom number` | `vc_valuation_finance` | `C1` | `corpus` | `02_BIZ_Anthropic` | a fake and unreal accounting paper number |
| `LEX_026` | `not a cash loss` | `vc_valuation_finance` | `B2` | `corpus` | `02_BIZ_Anthropic` | we did not actually lose real bank cash |
| `LEX_027` | `flowed through into the income statement` | `vc_valuation_finance` | `C1` | `corpus` | `02_BIZ_Anthropic` | appeared inside our profit and loss report |
| `LEX_028` | `capital-efficient` | `vc_valuation_finance` | `C1` | `corpus` | `02_BIZ_Anthropic` | using investors' money very savingly and smartly |
| `LEX_029` | `upside` | `vc_valuation_finance` | `B2` | `corpus` | `059_FIN`, `062_FIN`, `071_FIN` | future rising room / profit space |
| `LEX_030` | `When are you going to get it` | `vc_valuation_finance` | `B2` | `corpus` | `059_FIN` | What year will we actually receive this cash? |
| `LEX_031` | `convertible notes` | `vc_valuation_finance` | `C1` | `corpus` | `02_BIZ_Anthropic` | bridge loans that can turn into shares later |
| `LEX_032` | `balance sheet` | `vc_valuation_finance` | `B2` | `corpus` | `02_BIZ_Anthropic` | the company's asset and debt accounting table |
| `LEX_033` | `downside` | `vc_valuation_finance` | `B2` | `corpus` | `062_FIN` | the bad risk of losing our investment |
| `LEX_034` | `discounted cashflow` | `vc_valuation_finance` | `C1` | `corpus` | `063_FIN` | future cash calculated back to today's value |
| `LEX_035` | `discount rate` | `vc_valuation_finance` | `C1` | `corpus` | `063_FIN` | the percentage we use to shrink future money |
| `LEX_036` | `compare apples to apples` | `vc_valuation_finance` | `B2` | `corpus` | `072_FIN` | put two same-level companies together fairly |
| `LEX_037` | `doomsday scenario` | `vc_valuation_finance` | `C1` | `corpus` | `066_FIN` | the most terrible disaster assumption case |
| `LEX_038` | `super voting provision` | `vc_valuation_finance` | `C1` | `corpus` | `041_BIZ` | special founder shares with ten times voting power |
| `LEX_039` | `raise another round` | `vc_valuation_finance` | `B2` | `corpus` | `048_BIZ` | get one more batch of VC investment money |
| `LEX_040` | `positive ROE` | `vc_valuation_finance` | `C1` | `corpus` | `061_FIN` | still earning positive profit on shareholder money |
| `LEX_041` | `net interest margin` | `vc_valuation_finance` | `C1` | `corpus` | `077_FIN` | the profit gap between loan and deposit interest |
| `LEX_042` | `already in the price` | `vc_valuation_finance` | `C1` | `corpus` | `055_FIN` | the stock price already reflects this good news |
| `LEX_043` | `the law of holes` | `vc_valuation_finance` | `C1` | `corpus` | `069_FIN` | stop pouring more money into a losing project |
| `LEX_044` | `the punch is out of the bowl` | `vc_valuation_finance` | `C2` | `corpus` | `070_FIN` | government stimulus money and hot spending are over |
| `LEX_045` | `risk adjusted return` | `vc_valuation_finance` | `C1` | `corpus` | `044_BIZ` | profit calculated together with the risk level |
| `LEX_046` | `bubble indicator` | `vc_valuation_finance` | `B2` | `corpus` | `076_FIN`, `060_FIN` | a number showing if the market is overheating |
| `LEX_047` | `hard money` | `vc_valuation_finance` | `C1` | `corpus` | `03_FIN_Dalio` | strong real assets that governments cannot print |
| `LEX_048` | `catch the exact bottom` | `vc_valuation_finance` | `B2` | `corpus` | `054_FIN` | buy right at the lowest price point of the crash |
| `LEX_049` | `10 times the throughput` | `ai_compute_product` | `C1` | `corpus` | `012_AI` | 10 times faster processing and output speed |
| `LEX_050` | `eating into budgets` | `ai_compute_product` | `C1` | `corpus` | `090_USC` | spending too much of our annual department budget |
| `LEX_051` | `run this thing a million times` | `ai_compute_product` | `B2` | `corpus` | `090_USC` | call this AI API for one million times |
| `LEX_052` | `lowest cost tokens` | `ai_compute_product` | `C1` | `corpus` | `012_AI` | cheapest AI word generation unit price |
| `LEX_053` | `land power and shell` | `ai_compute_product` | `C1` | `corpus` | `012_AI` | data center land, electricity and building body |
| `LEX_054` | `open weight AI` | `ai_compute_product` | `C1` | `corpus` | `078_USC` | AI model whose parameter weights are free to download |
| `LEX_055` | `use it as a teacher` | `ai_compute_product` | `B2` | `corpus` | `037_BIZ` | use a huge model to train a smaller model |
| `LEX_056` | `rule-based guardrails` | `ai_compute_product` | `C1` | `corpus` | `019_AI` | strict safety limits written in code rules |
| `LEX_057` | `a request, not a rule` | `ai_compute_product` | `C1` | `corpus` | `019_AI` | just politely asking the AI, not forcing it |
| `LEX_058` | `feedback loops` | `ai_compute_product` | `B2` | `corpus` | `020_AI` | automatic testing and self-fixing cycles |
| `LEX_059` | `coding blind` | `ai_compute_product` | `C1` | `corpus` | `020_AI` | writing code without seeing any test feedback |
| `LEX_060` | `agent acceleration` | `ai_compute_product` | `C1` | `corpus` | `01_AI_DHH` | making software work faster by using AI agents |
| `LEX_061` | `under the hood` | `ai_compute_product` | `B2` | `corpus` | `025_AI` | the hidden technical architecture inside the product |
| `LEX_062` | `too raw of a primitive` | `ai_compute_product` | `C2` | `corpus` | `025_AI` | too basic and rough to sell straight to consumers |
| `LEX_063` | `world models` | `ai_compute_product` | `C1` | `corpus` | `016_AI` | AI models that understand real physical space rules |
| `LEX_064` | `AI in the loop` | `ai_compute_product` | `B2` | `corpus` | `009_AI` | embedding AI into every company workflow |
| `LEX_065` | `on-prem` | `ai_compute_product` | `C1` | `corpus` | `009_AI` | installed locally on company servers, not public cloud |
| `LEX_066` | `hallucinate through` | `ai_compute_product` | `C1` | `corpus` | `015_AI` | blindly guess and make up fake answers |
| `LEX_067` | `AI first` | `ai_compute_product` | `B2` | `corpus` | `050_BIZ` | putting AI as our number one company strategy |
| `LEX_068` | `hyperscalers` | `ai_compute_product` | `C1` | `corpus` | `074_FIN` | super massive cloud computing tech giants |
| `LEX_069` | `job one is to create something that works` | `ai_compute_product` | `B2` | `corpus` | `029_AI` | our first task is building a usable product |
| `LEX_070` | `sizable fleet` | `ai_compute_product` | `C1` | `corpus` | `089_USC` | a quite large group of deployed robots and devices |
| `LEX_071` | `major new consumer category` | `ai_compute_product` | `B2` | `corpus` | `095_USC` | a big brand-new kind of consumer product |
| `LEX_072` | `tightly controlled environment` | `ai_compute_product` | `C1` | `corpus` | `084_USC` | strictly arranged lab testing room |
| `LEX_073` | `destroy everybody's flywheel` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `04_USCHINA_Jensen` | break everyone's good business growth cycle |
| `LEX_074` | `supply chain disruptions` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `086_USC` | supply chain stopping or breaking accidents |
| `LEX_075` | `insulated from` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `086_USC` | well protected and separated from outside shocks |
| `LEX_076` | `base cost` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `093_USC` | the basic bottom price after adding import tax |
| `LEX_077` | `back off of it` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `065_FIN` | cancel or retreat from that tough tariff policy |
| `LEX_078` | `choke off the supply` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `080_USC` | completely block and cut the chip supply |
| `LEX_079` | `eating a loss` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `082_USC` | having to swallow and pay for a big money loss |
| `LEX_080` | `copy exact` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `082_USC` | copy every factory step 100% without any change |
| `LEX_081` | `hitting a ceiling` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `081_USC` | reaching the highest limit and cannot go up more |
| `LEX_082` | `third-party validation` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `081_USC` | independent outside lab testing to prove it |
| `LEX_083` | `domestically sourced` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `092_USC` | bought from local suppliers inside the home country |
| `LEX_084` | `barred from selling` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `092_USC` | legally not allowed by government to sell |
| `LEX_085` | `chip starved` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `042_BIZ` | seriously lacking advanced semiconductor chips |
| `LEX_086` | `biggest bottlenecks` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `088_USC` | the most serious blocking points stopping growth |
| `LEX_087` | `pragmatically adjusting` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `087_USC` | realistically changing strategy to fit new power |
| `LEX_088` | `active strategic competition` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `094_USC` | fierce long-term fighting between two superpowers |
| `LEX_089` | `shaping global AI norms` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `096_USC` | making international AI rules and standards |
| `LEX_090` | `purchasing power parity` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `097_USC` | comparing countries by what local money really buys |
| `LEX_091` | `tax breaks` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `035_BIZ` | government tax discount gifts for factories |
| `LEX_092` | `denials management` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `045_BIZ` | using AI to reject insurance claims for profit |
| `LEX_093` | `pacing the frontier` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `026_AI` | controlling the speed of leading AI research |
| `LEX_094` | `acceptable use` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `030_AI` | rules saying how users are allowed to use AI |
| `LEX_095` | `live in the shadow of` | `tariffs_supply_chain_geopolitics` | `C1` | `corpus` | `098_USC` | always stay under the influence of a huge neighbor |
| `LEX_096` | `debt to GDP` | `tariffs_supply_chain_geopolitics` | `B2` | `corpus` | `073_FIN` | the ratio between national debt and GDP size |
| `LEX_097` | `slotting fee` | `retail_channel_bridge` | `C1` | `world_bridge` | `[]` | shelf entrance fee / store display entry money |
| `LEX_098` | `chargeback` | `retail_channel_bridge` | `C1` | `world_bridge` | `[]` | deduct-money fine from the retail store |
| `LEX_099` | `MOQ` | `retail_channel_bridge` | `B2` | `world_bridge` | `[]` | smallest order quantity number we must buy |
| `LEX_100` | `sell-through rate` | `retail_channel_bridge` | `C1` | `world_bridge` | `[]` | real consumer selling speed percentage |
| `LEX_101` | `MAP pricing` | `retail_channel_bridge` | `C1` | `world_bridge` | `[]` | lowest online advertisement price control |
| `LEX_102` | `co-op marketing` | `retail_channel_bridge` | `B2` | `world_bridge` | `[]` | together-advertising fee with the retailer |
| `LEX_103` | `endcap placement` | `retail_channel_bridge` | `C1` | `world_bridge` | `[]` | store aisle front-head display spot |
| `LEX_104` | `markdown allowance` | `retail_channel_bridge` | `C1` | `world_bridge` | `[]` | slow-selling price-cut compensation money |
| `LEX_105` | `landed cost` | `retail_channel_bridge` | `B2` | `world_bridge` | `[]` | arrive-at-port all-included total cost |
| `LEX_106` | `consignment terms` | `retail_channel_bridge` | `C1` | `world_bridge` | `[]` | sell-first pay-later store contract |
| `LEX_107` | `shelf allocation` | `retail_channel_bridge` | `B2` | `world_bridge` | `[]` | how much shelf space the store gives us |
| `LEX_108` | `net-60 payment terms` | `retail_channel_bridge` | `B2` | `world_bridge` | `[]` | paying our money 60 days after goods arrive |
| `LEX_109` | `GDPR data residency` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | European user data staying inside Europe rule |
| `LEX_110` | `BOM cost` | `compliance_hardware_bridge` | `B2` | `world_bridge` | `[]` | hardware parts list total material cost |
| `LEX_111` | `EVT/DVT/PVT` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | three factory sample-to-mass-production test stages |
| `LEX_112` | `RMA rate` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | broken product return-and-repair percentage |
| `LEX_113` | `indemnity cap` | `compliance_hardware_bridge` | `C2` | `world_bridge` | `[]` | highest legal compensation ceiling in a contract |
| `LEX_114` | `data localization` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | forcing user data to stay in local country |
| `LEX_115` | `yield ramp` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | factory good-product rate slowly climbing up |
| `LEX_116` | `on-device inference` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | running AI locally inside the glasses chip |
| `LEX_117` | `FCC certification` | `compliance_hardware_bridge` | `B2` | `world_bridge` | `[]` | US government wireless radio entry certificate |
| `LEX_118` | `right to erasure` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | user legal right to delete all saved history |
| `LEX_119` | `data processing agreement` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | user data handling legal contract |
| `LEX_120` | `sole-source bottleneck` | `compliance_hardware_bridge` | `C1` | `world_bridge` | `[]` | only-one-supplier neck-choking supply risk |

## 八、全量 100 条切片紧凑索引表（按四大支柱有序排列）

| # | `clip_id` | 支柱 | 来源频道 (`channel`) | 归因发言人 (`inferred_speakers`) | 时长 (`s`) | 语速 (`WPM`) | 爆款分 | 英文标题钩子 (`en_title_hook`) |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `01_AI_DHH` | `AI` | Lex Fridman | David Heinemeier Hansson (DHH) | `56.36` | `139.46` | `9.7` | Hand-Coding vs AI Agents |
| 2 | `006_AI` | `AI` | Andrej Karpathy | Andrej Karpathy | `52.10` | `214.20` | `9.6` | Two Tiny Files vs Massive Training |
| 3 | `007_AI` | `AI` | Cleo Abram | Jensen Huang, Cleo Abram | `51.84` | `167.82` | `9.8` | Quarter Million Rack vs Desk Supercomputer |
| 4 | `008_AI` | `AI` | StarTalk | Geoffrey Hinton, StarTalk (Host) | `53.18` | `170.36` | `9.8` | Human Brain Connections vs AI Experience |
| 5 | `009_AI` | `AI` | Cisco | Jensen Huang | `49.75` | `149.55` | `9.7` | Human In Loop vs AI Loop |
| 6 | `010_AI` | `AI` | Dwarkesh Patel | Dario Amodei | `48.76` | `195.65` | `9.8` | Trillion Compute Bet vs Instant Bankruptcy |
| 7 | `011_AI` | `AI` | Sequoia Capital | Andrej Karpathy, Stephanie Zhan | `52.30` | `196.18` | `9.7` | 10x Engineers vs Agentic AI Pros |
| 8 | `012_AI` | `AI` | All-In Podcast | Jensen Huang, All-In Podcast (Hosts) | `52.99` | `163.05` | `9.8` | Cheap Chips vs 10x Token Throughput |
| 9 | `013_AI` | `AI` | Lex Fridman | Sam Altman | `54.70` | `189.76` | `9.6` | Job Loss Count vs Task Horizon |
| 10 | `014_AI` | `AI` | Tucker Carlson | Sam Altman, Tucker Carlson | `51.65` | `198.64` | `9.7` | Tiny Model Tweaks vs Moral Power |
| 11 | `015_AI` | `AI` | Andrej Karpathy | Andrej Karpathy | `52.25` | `187.18` | `9.6` | Mental Math Hallucination vs Code Tool |
| 12 | `016_AI` | `AI` | Welch Labs | Yann LeCun, Welch Labs (Narrator) | `48.52` | `163.23` | `9.7` | Next Token LLMs vs World Models |
| 13 | `017_AI` | `AI` | Anthropic | Dario Amodei, Anthropic Co-Founders | `49.34` | `154.44` | `9.2` | Authoritarian Tool vs Human Freedom |
| 14 | `018_AI` | `AI` | Andrej Karpathy | Andrej Karpathy | `52.05` | `201.73` | `9.6` | Tiny GPT-2 Context vs Million Tokens |
| 15 | `019_AI` | `AI` | Austin Marchese | Austin Marchese | `44.00` | `200.45` | `9.5` | Polite Prompt Rules vs Hard Hooks |
| 16 | `020_AI` | `AI` | AI Engineer and Matt Pocock | Matt Pocock | `46.47` | `160.10` | `9.5` | Coding Blind vs Tight Feedback Loops |
| 17 | `021_AI` | `AI` | OpenAI | Sam Altman, OpenAI Podcast (Host) | `51.13` | `193.62` | `9.5` | Empty Bank Doubt vs Stargate Billions |
| 18 | `022_AI` | `AI` | Lex Fridman | Ilya Sutskever, Lex Fridman | `46.57` | `194.55` | `9.3` | Brain Spikes vs Deep Learning Magic |
| 19 | `023_AI` | `AI` | Interesting Times and 2 more | Dario Amodei, Ross Douthat | `54.47` | `193.87` | `9.5` | Linear Growth vs 10x AI Wealth |
| 20 | `024_AI` | `AI` | Lex Fridman | Yann LeCun | `45.50` | `205.71` | `9.4` | Rogue Persuasive AI vs Smart Shield |
| 21 | `025_AI` | `AI` | No Priors: AI, Machine Learning, Tech, & Startups | Andrej Karpathy, No Priors (Host) | `48.01` | `227.45` | `9.4` | Raw Token Predictor vs Digital Persona |
| 22 | `026_AI` | `AI` | CNN | Dario Amodei, CNN (Interviewer) | `53.99` | `207.82` | `9.5` | Reckless Speed vs Ceding AI Power |
| 23 | `027_AI` | `AI` | Sources Podcast and Alex Heath | Sam Altman, Alex Heath | `50.18` | `223.60` | `9.3` | Made Without AI vs New Art |
| 24 | `029_AI` | `AI` | CNN | Jensen Huang, CNN (Interviewer) | `48.52` | `204.04` | `9.5` | Blind AI Race vs Useful Systems |
| 25 | `030_AI` | `AI` | Bloomberg Television | Sam Altman | `53.83` | `215.12` | `9.3` | Strict AI Bans vs Electricity Right |
| 26 | `02_BIZ_Anthropic` | `BUSINESS` | All-In Podcast | All-In Podcast (Hosts) | `57.76` | `164.13` | `9.5` | Phantom Loss vs Capital Efficiency |
| 27 | `030_BIZ` | `BUSINESS` | Savanteum | Elon Musk | `47.87` | `154.17` | `9.9` | Zero Ads vs Pure Product |
| 28 | `031_BIZ` | `BUSINESS` | Startup Archive | Elon Musk | `46.65` | `194.21` | `9.9` | Blind Automation vs First Principles |
| 29 | `032_BIZ` | `BUSINESS` | Business Motiversity | Business Motiversity (Storyteller on Jeff Bezos) | `43.50` | `187.59` | `9.8` | Cynical Mockery vs Billionaire Conviction |
| 30 | `033_BIZ` | `BUSINESS` | Personal Finance Insider | Jeff Bezos | `47.67` | `142.23` | `9.7` | Tiny Startup vs Giant Incumbent |
| 31 | `034_BIZ` | `BUSINESS` | MotivationHub | Jeff Bezos | `44.31` | `193.64` | `9.6` | Fighting Change vs Leaning Into Future |
| 32 | `035_BIZ` | `BUSINESS` | FRONTLINE PBS \| Official | FRONTLINE PBS (Narrator/Interviewer), Amazon Executive (Interviewee) | `43.54` | `158.47` | `9.7` | Desperate Cities vs Monopoly Leverage |
| 33 | `036_BIZ` | `BUSINESS` | Cleo Abram | Mark Zuckerberg | `53.43` | `222.35` | `9.8` | One God AI vs Million Agents |
| 34 | `037_BIZ` | `BUSINESS` | Bloomberg Originals | Mark Zuckerberg, Bloomberg Originals (Interviewer) | `54.64` | `224.01` | `9.6` | Closed Gatekeepers vs Open Distillation |
| 35 | `038_BIZ` | `BUSINESS` | fern | Peter Thiel, fern (Narrator) | `43.84` | `164.23` | `9.8` | Crowd Thinking vs Contrarian Billions |
| 36 | `039_BIZ` | `BUSINESS` | All-In Podcast | All-In Podcast (Hosts) | `51.48` | `181.82` | `9.8` | Human Payroll vs Token Spend |
| 37 | `040_BIZ` | `BUSINESS` | All-In Podcast | All-In Podcast (Hosts) | `45.21` | `163.24` | `9.7` | Legacy Revenue vs Monopoly Valuation |
| 38 | `041_BIZ` | `BUSINESS` | All-In Podcast | All-In Podcast (Hosts) | `44.71` | `206.67` | `9.6` | Super Voting Stock vs Tax Trap |
| 39 | `042_BIZ` | `BUSINESS` | The Economist | Elon Musk, The Economist (Interviewer) | `53.64` | `158.84` | `9.9` | US Power Bottleneck vs China Chips |
| 40 | `043_BIZ` | `BUSINESS` | The Wall Street Journal | Elon Musk, Tesla Ex-Employee, The Wall Street Journal (Narrator) | `44.17` | `202.40` | `9.7` | Comfort Boss vs Factory Floor |
| 41 | `044_BIZ` | `BUSINESS` | Y Combinator | Elon Musk, Y Combinator (Interviewer) | `51.76` | `170.40` | `9.6` | Safe Returns vs Radical Innovation |
| 42 | `045_BIZ` | `BUSINESS` | More Perfect Union | More Perfect Union (Narrator) | `53.09` | `144.66` | `9.6` | Software Vendor vs Shadow Empire |
| 43 | `047_BIZ` | `BUSINESS` | Bloomberg Originals | Emily Chang, Y Combinator Partner | `48.55` | `189.08` | `9.5` | Ten Minute Pitch vs 10000 Hours |
| 44 | `048_BIZ` | `BUSINESS` | Y Combinator | Paul Graham, Y Combinator (Interviewer) | `54.72` | `202.85` | `9.4` | Fancy Slides vs Hard Milestones |
| 45 | `049_BIZ` | `BUSINESS` | STILL I RISE Motivation | Satya Nadella | `51.15` | `168.91` | `9.5` | Initial Idea vs Core Capability |
| 46 | `050_BIZ` | `BUSINESS` | Stanford Graduate School of Business | Sundar Pichai, Stanford GSB (Interviewer) | `46.28` | `175.02` | `9.3` | Legacy Comfort vs AI First |
| 47 | `051_BIZ` | `BUSINESS` | Lex Fridman | Mark Zuckerberg | `49.63` | `180.13` | `9.4` | Bloated Scale vs Lean Efficiency |
| 48 | `052_BIZ` | `BUSINESS` | Epoch Philosophy | Epoch Philosophy (Narrator) | `48.08` | `136.02` | `9.7` | Wage Labor vs Equity Monopoly |
| 49 | `053_BIZ` | `BUSINESS` | The Economist | Elon Musk, The Economist (Interviewer) | `52.68` | `135.54` | `9.7` | Scarcity Era vs Radical Abundance |
| 50 | `054_BIZ` | `BUSINESS` | Mulligan Brothers Interviews | Elon Musk | `44.42` | `160.74` | `9.3` | 500B Bureaucracy vs Mars Greenhouse |
| 51 | `03_FIN_Dalio` | `FINANCE` | The Diary Of A CEO | Ray Dalio, The Diary Of A CEO (Host) | `55.92` | `130.90` | `9.9` | Gold vs Bitcoin |
| 52 | `054_FIN` | `FINANCE` | Boardroom Billions | Warren Buffett (Boardroom Billions Commentary) | `52.57` | `182.61` | `9.9` | Timing Bottoms vs Buying Quality |
| 53 | `055_FIN` | `FINANCE` | FINAiUS | Stanley Druckenmiller, FINAiUS (Narrator) | `53.20` | `151.13` | `9.8` | Diversifying Risk vs Concentrated Conviction |
| 54 | `056_FIN` | `FINANCE` | Norges Bank Investment Management | Stanley Druckenmiller | `45.17` | `159.40` | `9.8` | Buying Today vs Investing Ahead |
| 55 | `057_FIN` | `FINANCE` | Morgan Stanley | Stanley Druckenmiller | `47.13` | `136.22` | `9.6` | Wall Street Consensus vs Campus Talent |
| 56 | `058_FIN` | `FINANCE` | FINAiUS | FINAiUS (Narrator) | `46.71` | `149.00` | `9.7` | Safe Blue Chips vs Valuation Crashes |
| 57 | `059_FIN` | `FINANCE` | The Swedish Investor | The Swedish Investor (Narrator) | `51.43` | `141.16` | `9.5` | Paper Upside vs Cash Timing |
| 58 | `060_FIN` | `FINANCE` | CNBC Television | Ray Dalio, CNBC Television (Interviewer) | `49.95` | `162.16` | `9.6` | Rate Hikes vs Forced Selling |
| 59 | `061_FIN` | `FINANCE` | The Master Investor Podcast with Wilfred Frost | Jamie Dimon, Wilfred Frost | `54.56` | `208.94` | `9.4` | Chasing Size vs Fortress Discipline |
| 60 | `062_FIN` | `FINANCE` | My First Million | Howard Marks, My First Million (Host) | `54.00` | `183.33` | `9.3` | Pitch Decks vs Decades of Trust |
| 61 | `063_FIN` | `FINANCE` | The Swedish Investor | The Swedish Investor (Narrator) | `52.73` | `177.51` | `9.5` | Money Today vs Future Millions |
| 62 | `064_FIN` | `FINANCE` | Principles by Ray Dalio | Ray Dalio, Andrew Ross Sorkin | `53.90` | `170.32` | `9.6` | 1929 Surplus vs Today's Deficit |
| 63 | `065_FIN` | `FINANCE` | Bloomberg Television | Jamie Dimon, Bloomberg Television (Interviewer) | `46.03` | `225.51` | `9.7` | America's Edge vs Tariff Chaos |
| 64 | `066_FIN` | `FINANCE` | Millennial Investing | Aswath Damodaran | `50.88` | `211.08` | `9.7` | Market Panic vs Doomsday Math |
| 65 | `067_FIN` | `FINANCE` | David Rubenstein | Bloomberg Wealth / David Rubenstein (Narrator) | `46.65` | `173.63` | `9.8` | Free Retail Trades vs Citadel |
| 66 | `068_FIN` | `FINANCE` | Bloomberg Television | Ray Dalio, Bloomberg Television (Interviewer) | `50.42` | `179.69` | `9.6` | Personal Bankruptcy vs Printing Money |
| 67 | `069_FIN` | `FINANCE` | The Swedish Investor | The Swedish Investor (Narrator) | `53.67` | `158.75` | `9.9` | Averaging Down vs Quit Digging |
| 68 | `070_FIN` | `FINANCE` | Bloomberg Television | Ken Griffin | `52.73` | `158.16` | `9.5` | Wartime Stimulus vs Empty Savings |
| 69 | `071_FIN` | `FINANCE` | Bloomberg Television | Howard Marks, Bloomberg Television (Interviewer) | `48.08` | `153.49` | `9.6` | Lending Debt vs Buying Equity |
| 70 | `072_FIN` | `FINANCE` | The Swedish Investor | The Swedish Investor (Narrator) | `50.93` | `153.15` | `9.3` | Comparing Multiples vs True Monopolies |
| 71 | `073_FIN` | `FINANCE` | Bloomberg Television | Jamie Dimon | `52.99` | `193.62` | `9.4` | Default Panic vs Debt Downgrade |
| 72 | `074_FIN` | `FINANCE` | Bloomberg Television | Howard Marks, Bloomberg Television (Interviewer) | `52.29` | `158.35` | `9.3` | Tech Giants vs Pure AI |
| 73 | `075_FIN` | `FINANCE` | Bloomberg Television | Ray Dalio, Bloomberg Television (Interviewer) | `48.62` | `156.73` | `9.4` | Human Gut vs AI Investing |
| 74 | `076_FIN` | `FINANCE` | Nicholas Thompson and Principles by Ray Dalio | Ray Dalio, Nicholas Thompson | `46.68` | `146.53` | `9.4` | 2008 Debt vs 2000 Bubble |
| 75 | `077_FIN` | `FINANCE` | CNBC Television | CNBC Television (Host), CNBC Investment Committee Panelist (Liz) | `48.08` | `202.16` | `9.2` | 1997 Soft Landing vs 1999 Crash |
| 76 | `04_USCHINA_Jensen` | `US_CHINA` | Lex Fridman | Jensen Huang, Lex Fridman | `47.88` | `125.31` | `9.6` | Exclude China vs Shared Flywheel |
| 77 | `05_USCHINA_Robots` | `US_CHINA` | BBC News | BBC News (Correspondent), Chinese Auto Factory Engineer | `54.84` | `133.48` | `9.3` | China vs US Factory Robots |
| 78 | `078_USC` | `US_CHINA` | CNBC | CNBC (Narrator) | `51.22` | `161.66` | `9.9` | Closed Models vs Open Takeover |
| 79 | `079_USC` | `US_CHINA` | CNBC | CNBC (Narrator), Eric Schmidt | `54.27` | `174.68` | `9.8` | Three-Year Lead vs Six-Month Catchup |
| 80 | `080_USC` | `US_CHINA` | Newsthink | Newsthink (Narrator) | `46.03` | `160.33` | `9.5` | Silicon Origin vs Zero Fabs |
| 81 | `081_USC` | `US_CHINA` | Dr Ben Miles | Dr Ben Miles | `53.64` | `185.68` | `9.6` | Lithography Ceiling vs Logic Folding |
| 82 | `082_USC` | `US_CHINA` | Behind Asia | Behind Asia (Narrator) | `49.67` | `130.46` | `9.7` | Tiny Flaw vs \$550M Loss |
| 83 | `083_USC` | `US_CHINA` | CNN | CNN (Correspondent), CNN (Anchor John) | `44.00` | `195.00` | `9.7` | \$65B Spend vs DeepSeek Shock |
| 84 | `084_USC` | `US_CHINA` | TIME | Figure AI Executive, TIME (Narrator) | `46.03` | `211.17` | `9.4` | Billion-Dollar Hype vs Home Reality |
| 85 | `085_USC` | `US_CHINA` | Logically Answered | Logically Answered (Narrator) | `47.95` | `158.92` | `9.5` | Hidden Giant vs 92% Monopoly |
| 86 | `086_USC` | `US_CHINA` | The Wall Street Journal | The Wall Street Journal (Narrator) | `43.33` | `156.47` | `9.2` | Phone Exit vs Chip Dependency |
| 87 | `087_USC` | `US_CHINA` | Bloomberg Podcasts and Bloomberg Television | Kishore Mahbubani | `51.67` | `131.22` | `9.8` | Zero-Sum Rivalry vs Asian Pragmatism |
| 88 | `088_USC` | `US_CHINA` | CNBC | CNBC (Narrator/Analyst) | `49.55` | `197.38` | `9.9` | Idle Chips vs Power Dominance |
| 89 | `089_USC` | `US_CHINA` | Bloomberg Tech | Barclays Analyst, Bloomberg Tech (Host) | `48.68` | `170.09` | `9.8` | Optimus Hype vs China Volume |
| 90 | `090_USC` | `US_CHINA` | CNBC | CNBC (Commentator) | `53.39` | `188.80` | `9.7` | Leaderboard Hype vs Enterprise Cost |
| 91 | `091_USC` | `US_CHINA` | Bloomberg Television and Bloomberg Originals | Bloomberg Originals (Narrator/Correspondent) | `53.93` | `149.08` | `9.6` | Frontier AI vs Real-World Scale |
| 92 | `092_USC` | `US_CHINA` | Inside China Business | Inside China Business (Narrator) | `52.97` | `130.26` | `9.8` | ASML Ban vs Chinese EUV |
| 93 | `093_USC` | `US_CHINA` | Inside China Business | Inside China Business (Narrator) | `45.07` | `146.44` | `9.7` | Tariff Walls vs \$12K EV |
| 94 | `094_USC` | `US_CHINA` | The Economist | Kevin Rudd, The Economist (Interviewer) | `44.12` | `165.91` | `9.5` | Polite Diplomacy vs AI Supremacy |
| 95 | `095_USC` | `US_CHINA` | AI Revolution | AI Revolution (Narrator) | `47.67` | `144.75` | `9.3` | Lonely Millions vs Bionic Companions |
| 96 | `096_USC` | `US_CHINA` | Bloomberg Television | Bloomberg Television (Correspondent) | `49.92` | `177.88` | `9.3` | Tech Monopoly vs Global South |
| 97 | `097_USC` | `US_CHINA` | ABC News (Australia) | Kevin Rudd | `47.76` | `152.01` | `9.9` | GDP Scale vs Tech Dominance |
| 98 | `098_USC` | `US_CHINA` | Asia Society | Asia Society (Southeast Asia Forum Speaker) | `44.21` | `172.36` | `9.2` | Short Century vs 4,000-Year Cycle |
| 99 | `099_USC` | `US_CHINA` | FRANCE 24 English | FRANCE 24 English (Anchor/Analyst) | `44.56` | `180.43` | `9.4` | \$500B Stargate vs DeepSeek Timing |
| 100 | `100_USC` | `US_CHINA` | PRO ROBOTS | PRO ROBOTS (Narrator) | `47.97` | `150.09` | `9.2` | Lab Demos vs Factory Bots |
