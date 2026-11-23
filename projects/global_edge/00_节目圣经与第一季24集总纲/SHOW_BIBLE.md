# 《跨境底牌：硅深暗战》（*Global Edge*）—— 顶级中英双语商战广播剧 · 节目制作圣经

> **一句话 IP 定位**：面向中国 **B1–C1 进阶科技/金融/外企职场人与出海创业者** 的完全独立连续商战双语广播剧——**音频版 HBO *Succession* × *Silicon Valley***。  
> **核心戏剧舞台**：深圳智造 × 硅谷算力与沙丘路资本 × 伦敦牛津街顶级零售 × 东南亚/欧盟地缘与合规——聚焦 AI 消费硬件独角兽 **NovaEdge Technologies（灵犀智造）** 将旗舰产品 **NovaEdge Glass**（AI 智能眼镜）与 **NovaDock**（桌面空间 AI 伴侣）杀向全球的 24 集连续商战弧光。  
> **核心语言与教学工法**：**「公开战场 100% 地道高管英语飙戏 + 贴麦中文内心独白/深圳私密复盘破译潜台词 + 片尾 3 分钟 `0.80x` 慢拆与 `1.0x` 原速影子跟读」**。  
> **零 API 96GB 工业底座**：100% 运行于 Colab 96GB G4 开源满血黄金栈（`fishaudio/drama-3` 35B MoE + `v2_real_human_studio` 全真人英美中录音棚干声锚点 + `OpenMOSS-Team/MOSS-SoundEffect-v2.0` + `ACE-Step/acestep-v15-xl-turbo-diffusers` + 本地 `faster-whisper-small-int8` 双脚本质检 + `48kHz` `-16.0 ± 0.5 LUFS` 三总线母带混音，外部语音 API 费用 **\$0**）。

---

## 一、 IP 定位、9 项锁定铁律与彻底“去切片味”脱钩宣言

### 1.1 锁定决策总控表（100% 锚定 `/grill-me` 9 项核心决策）

本圣经是《跨境底牌：硅深暗战》第一季 24 集编剧、配音选角、声纹采集（M4）、台本编译（M5）与混音质检的最高权威母本。以下 9 项产品铁律在任何单集或变体中均不可动摇：

| 决策号 | 维度 | 本剧不可妥协的工业规范 | 下游工程/验收绑定 |
| :---: | :--- | :--- | :--- |
| **#1** | **完全独立连续商战 IP** | 彻底脱离“评论某条短视频/播客”的二手搬运形态；只提炼 100 条真实高管语料的底层商业博弈与原话词块，**正片台词严禁出现任何外部视频平台名称、切片解说或二手复述痕迹**。 | `tests/test_global_edge_blueprint.py` 与 M5 反泄露扫描强检 `0` 命中 |
| **#2** | **B1–C1 高净值受众门槛** | 精准服务“能读懂英文邮件、但在真实跨国会议与大佬原速对谈中听不懂潜台词、张不开嘴反击”的科技/金融/外企职场人与出海创始人；单集精准嵌入 `5–8` 组 C1 级高管杀招词块。 | `season1_24ep_map.json` 每集 `5–8` 组词块，其中 `>= 70%` 原语料验真 |
| **#3** | **剧情内生双语 + 3 分钟拆局** | 公开董事会/VC 路演/伦敦买手谈判 100% 飙地道高管英语（`en`）；林沉《纸牌屋》式贴麦内心独白（`inner_monologue`）与深圳拍档周默私下密谋自然切中文（`zh`/`zh-en`）；片尾保留独立 3 分钟（`165–210s`）**Act 5 高管黑话复盘手记**，零“英语老师”出戏感。 | `EpisodeCueSheet.mode = "bilingual_business_drama"`；Act 5 由 `lin_chen`（及 `E001_VB` 中 `zhou_mo`）原角色承接 |
| **#4** | **三极跨国出海世界观** | 深圳（南山硬科技智造与 SMT 产线）× 硅谷/纽约（沙丘路 VC、大模型算力与华尔街 IPO）× 伦敦（牛津街高端零售）× 东南亚/布鲁塞尔（关税转移与欧盟 GDPR/AI 法案）。 | 贯穿 `E001–E024` 四大 6 集商战弧光 |
| **#5** | **85/15 口音矩阵 + HBO 动态语速** | 核心常驻角色锁死硅谷/纽约标准美音 + 伦敦 RP 英音（全季英文时长 `>= 85%`，本季蓝图实配 **`96.0%`**，E001 锁死 **`100%`**）；仅在 E011/E013/E016 引入 `<= 15%`（实配 **`4.0%`**）清晰可控的国际精英客串。正片英文按百条语料实证中位数 **`170.34 WPM`**（原始基线 **`170.20 WPM`**）锁定 **`150–185 WPM`**，片尾拆局采用确定性 **`0.80x`** 慢拆 + **`1.0x`** 原速跟读。 | `voice_casting_registry.json` + `ACCENT_AND_PROSODY_MANUAL.md` |
| **#6** | **黄金通勤体量 × 24 集 × 双漏斗变现** | 单集严控 **`10–14 分钟`**（`600–840s` = Acts 1–4 剧情 `480–600s` + Act 5 拆局 `165–210s`）；第一季 24 集完整商战弧光；小宇宙/喜马拉雅/微信听书免费做大盘 + 每集原生裁切 `38–55s` 竖屏飙戏冲突切片导流 + 后端双语精读手册（`¥79`）/付费专栏（`¥159`）/6 周跟读营（`¥699`）。 | `SEASON1_24EP_BLUEPRINT.md` 每集内置 `viral_45s_hook` |
| **#7** | **零 API 96GB 开源满血管线** | 严格 `$0` 商用语音 API（0 ElevenLabs、生产模式 0 `edge-tts`），全员使用 44.1kHz 单声道 `-16 LUFS` 真人录音棚锚点（`v2_real_human_studio`），配合 `drama-3` + `MOSS v2.0` + `ACE-Step 1.5 XL` + `faster-whisper` + 48kHz `-16 LUFS` 混音。 | `voice_casting_registry.json` 规范模型 ID 与 M4 96GB 脚本 |
| **#8** | **AI 消费硬件出海独角兽抓手** | 锁定大众 1 秒听懂、同时天然撞上消费零售压价、VC 估值、算力 Token 账单、隐私合规与 25% 关税的 AI 智能眼镜 + 桌面伴侣硬件独角兽 **NovaEdge Technologies（灵犀智造）**。 | 全季 24 集统一硬件单位经济账本 |
| **#9** | **第一期四变体对照实验体系** | 首集《八千万幽灵账单 / The \$80M Phantom》在严格控制剧情/卡司/5 条种子切片/8 组必考原话词块完全一致的前提下，同步交付 **`E001_VA` / `E001_VB` / `E001_VC` / `E001_VD`** 四变体 + `AUDITION_GLOBAL_EDGE` 试听包，通过 100 分盲测决选第一季正式母版。 | M5 编译与 `E001_COMPARATIVE_EVAL_RUBRIC.md` |

### 1.2 相较仓库标杆 `projects/buffett_letters/` 的四维升级跃迁

本剧完全复用并向下兼容仓库已跑通的 96GB 开源底座，但绝非《穿越周期的信》（非虚构历史圆桌节目）的换皮复刻，而是在核心产品与引擎架构上完成四次显性升维：

| 对比维度 | 仓库既有标杆 `buffett_letters/` | 本剧 `global_edge/`（《跨境底牌：硅深暗战》） |
| :--- | :--- | :--- |
| **剧集形态与节奏** | 15–22 分钟非虚构历史圆桌访谈 | **`10–14` 分钟 HBO 级虚构连续商战剧情剧**（Acts 1–4 商战飙戏 + Act 5 拆局） |
| **中英语言比重** | 中文圆桌为主，英文原典单句同传点缀 | **公开战场 100% 地道高管英语飙戏**（单集英文占比 `55%–70%`，直击 B1–C1 实战听力） |
| **声学空间与抢话** | `vintage_study` 书房对话 + `duck_under_next` 同传 | 新增 **`boardroom` / `inner_monologue` / `phone_call`** 企业声场 + **`[-0.25, -0.05]s`** 实时抢话打断 |
| **习得与跟读闭环** | 三阶财富认知锦囊（无语速拆解跟读） | 新增确定性 FFmpeg **`atempo=0.80`** 保音高慢拆 + **`1.0x`** 原速 + **`>= 1.8s`** 语音环路静默跟读窗 |

---

## 二、 世界观版图与三时区商战地理

### 2.1 三极跨国权力舞台（零视觉依赖的听觉空间切换）

广播剧没有画面镜头，听众必须在 1 秒内仅靠**声学空间特征、标志性物理拟音（Foley）与角色口音切换**辨识当下身处哪座城市、哪张权力谈判桌：

| 地理极点 | 代表物理场景与机构 | 典型听觉声场与拟音锚点 | 核心语言与口音主轴 | 核心商战矛盾类型 |
| :--- | :--- | :--- | :--- | :--- |
| **第一极：深圳南山（制造与研发心脏）** | NovaEdge 南山总部深夜战情室、自动化 SMT 无尘产线、光学暗室、深圳湾深夜后座出租车 | `dry` / `inner_monologue` + `shenzhen_smt_factory_line`（贴片机伺服律动与气动阀） | 现代干练大陆科技普通话（`zhou_mo` / `lin_chen` 私下复盘）+ 精准英文工程术语 | BOM 成本压缩、EVT/DVT/PVT 锁模、良率爬坡、开源大模型端侧蒸馏、芯片断供突围 |
| **第二极：硅谷 & 纽约（资本、算力与华尔街终局）** | 帕洛阿尔托沙丘路（Sand Hill Road）Apex Horizon 玻璃会议室、纽约红圈所、纳斯达克/纽交所交易大厅 | `boardroom`（玻璃紧致早反射）+ `glass_boardroom_door` / `paper_term_sheet_slide` / `nyse_bell_and_ticker_pulse` | 硅谷精英美音（`victoria_vance` / `lin_chen`）+ 纽约法务美音（`claire_chen_gc`） | 可转债会计重估估值杀、云端 Token 账单挤毛利、AB 股超级投票权攻防、做空狙击与 DCF 末日估值、IPO 敲钟 |
| **第三极：伦敦（欧美顶级线下渠道咽喉）** | 伦敦梅费尔区（Mayfair）采购办公室、牛津街 Selfridges 旗舰百货陈列厅、跨大西洋零售联采峰会 | `boardroom` / `vast_hall` + `paper_term_sheet_slide` / `smart_glasses_haptic_ping` | 纯正现代伦敦标准 RP 英音（`alistair_finch`）vs. 林沉美音 | 进场费（slotting fee）、寄售结算、退单扣款（chargeback）、MAP 破价危机、实销率（sell-through）与滞销降价补贴 |
| **第四战区：布鲁塞尔 & 新加坡 / 越南（合规与地缘棋盘）** | 布鲁塞尔欧盟 AI 法案隐私听证厅、新加坡滨海湾主权基金私密会所、胡志明市二供总装厂 | `vast_hall` / `phone_call` / `boardroom` + `transpacific_call_connect` | 精控国际精英客串（`henrik_lindqvist` E011、`rajiv_menon` E013、`wei_ling_tan` E013/E016，全季严控 `4.0% <= 15%`） | GDPR 数据驻留与 72 小时被遗忘权、25% 惩罚性关税与到岸成本重算、跨国复制产线良率崩盘、主权资本数据孤岛谈判 |

### 2.2 三时区同步压迫感（剧情天然倒计时引擎）

跨国出海最真实的窒息感来自时差错位——当深圳产线凌晨 2 点爆出微显示贴合良率警报时，伦敦牛津街恰好是下午 6 点下班前发来最后通牒，而硅谷沙丘路则是清晨 10 点投委会刚敲响玻璃门。编剧在全季特别是 `E001_VC` 及第二、三弧高频利用 **`phone_call`（300–3400Hz 电话带通）+ `transpacific_call_connect`** 构建“一条越洋电话未挂断、另一端会议室门已推开”的三时区窒息节奏。

---

## 三、 主角公司与旗舰硬件 SKU 商业圣经

### 3.1 公司档案：**NovaEdge Technologies（灵犀智造）**

- **成立时间与背景**：创立 4 年半，深圳南山硬件研发与智造中心（约 180 人→第三弧扩张至 2,000 人）+ 帕洛阿尔托北美商业与 AI 算法分部 + 伦敦欧洲渠道办。
- **融资阶段与资本结构（E001 起点）**：已完成 A/B 轮与一笔面向战略云基建方的可转债（`convertible notes`）过桥融资；当前正冲刺 **1.5 亿美元 C 轮融资（投前估值 12 亿美元）**，领投意向方为沙丘路顶级机构 **Apex Horizon Ventures**（主管合伙人 Victoria Vance）。
- **核心会计引爆点（E001 剧情发动机）**：因 NovaEdge 估值较可转债发行日大幅跳涨，按 US GAAP 公允价值计量准则，可转债衍生负债公允价值变动在资产负债表形成 **\$80M（八千万美元）非现金重估亏损**，并按规则传导进利润表（`flowed through into the income statement`）。该数字并非真实经营烧钱（`not a cash loss`），却成为 Victoria 在签约前夜企图借机把估值砍掉 30% 的致命借口——直接承接核心语料 `02_BIZ_Anthropic` 的真实华尔街会计逻辑。

### 3.2 两大旗舰硬件 SKU 与真实单位经济账本

全季 24 集绝不凭空编造违背商业常识的数字；所有财务冲突、渠道砍价、关税冲击与云成本焦虑全部锁死在下述统一单位经济账本内：

| 财务 / 工程指标 | **SKU 1：NovaEdge Glass（旗舰 AI 智能眼镜）** | **SKU 2：NovaDock（桌面空间 AI 伴侣终端，E007 登场）** | 对应核心商战冲突与词库锚点 |
| :--- | :--- | :--- | :--- |
| **产品形态与核心卖点** | 38 克钛合金超轻光学波导眼镜，主打跨国会议实时低延迟字幕、视觉对象识别与端侧语音代理 | 桌面级空间感知与长期情绪记忆伴侣主机（内置本地小型 NPU，面向欧美独居精英与书房办公场景） | `major new consumer category`、`world models`、`under the hood` |
| **欧美建议零售价 (MSRP)** | **\$399**（英国 £329） | **\$599**（英国 £499） | `MAP pricing`（防亚马逊第三方破价） |
| **大渠道批发扣点与净出厂价** | Best Buy / Selfridges 要求 **40% 零售毛利** → 净批发价 **\$239.4**（计账取整 **\$239**，\$399 × 60%；另附加 8% `co-op marketing` 与首批 `slotting fee` 博弈） | 净批发价 **\$359.4**（计账取整 **\$359**，\$599 × 60%）；Selfridges 伦敦首单试水要求 **3,000 台寄售（`consignment terms`）** | `slotting fee`、`shelf allocation`、`endcap placement`、`markdown allowance` |
| **深圳 BOM 与制造组装成本** | 光学微显示 + 端侧 NPU + 钛合金镜架 **BOM \$142**（周默在 E002–E004 通过去冗余工艺再砍掉 \$18 至 **\$124**） | 精密多自由度伺服底座 + 视觉传感器 + 本地 NPU **BOM \$218** | `BOM cost`、`MOQ`（50,000 台起订）、`EVT/DVT/PVT`、`yield ramp` |
| **25% 美国关税到岸成本冲击** | 25% 惩罚性关税直接拉高每台完税成本 **+\$31**（按优化后 \$124 BOM/FOB 报关基数 × 25% 计，不含另计空运保费；直逼硬件毛利生死线） | 按 \$218 BOM/FOB 报关基数 × 25% 计，每台关税直接暴涨 **+\$54.5**（不含另计空运保费），直接倒逼 E013 越南/墨西哥二供组装突围 | `base cost`、`landed cost`、`supply chain disruptions`、`chargeback` |
| **云端 AI Token 持续成本黑洞** | **改造前（E001–E004）**：纯调闭源公有云多模态 API，活跃用户日均烧 **\$0.18**（3 年累计 **\$197/台**，按 365 天 × 3 × \$0.18 计，彻底吞噬硬件毛利！）；**改造后（E005+）**：开源权重蒸馏 + **`on-device inference`** 端侧推理，云端成本压低 **78%**（精确 77.8%）至 **\$0.04/天** | 本地 NPU 处理 85% 语音与空间推理，仅复杂长程任务回云；企业版强制支持 **`on-prem`** 私有部署 | `eating into budgets`、`10 times the throughput`、`run this thing a million times`、`open weight AI`、`use it as a teacher` |
| **合规与售后红线** | 首批 **`RMA rate` 红线 `<= 2.5%`**；美国强制 **`FCC certification`**；欧洲强制法兰克福服务器 **`GDPR data residency`** + 72 小时 **`right to erasure`** | 同等 GDPR 与数据本地化孤岛要求（欧美亚三区物理隔离，拒绝单中心回传） | `rule-based guardrails`、`a request, not a rule`、`indemnity cap`、`data processing agreement` |

---

## 四、 核心与客串 8 位锁定角色 · 四层完整制作档案

> **选角铁律（与 `voice_casting_registry.json` 100% 逐字段对齐）**：
> 1. 全剧严格锁定 **8 个规范 `role_id`**（5 名核心常驻 + 3 名精控国际精英客串），**绝不新增抽离世界观的“播音员主持人”或“英语课堂老师”角色**；
> 2. 片尾 **Act 5 3 分钟高管黑话复盘** 全部由主角 **`lin_chen`**（及 `E001_VB` 出租车复盘版中的 **`zhou_mo`**）以剧中身份完成；
> 3. **英文标签避坑铁律**：所有纯英角色（`language_code="en"`）严禁使用 `[wryly]` 标签（因 `DRAMA3_TAG_MAP["wryly"]` 会输出 `"Midwestern wit"` 污染硅谷/伦敦/北欧口音），冷峻幽默统一使用 `[deadpan]`、`[understated]`、`[icy polite]`、`[sarcastic]`；`[wryly]` 仅允许在中文/双语角色（如 `zhou_mo`）触发 `BUSINESS_DRAMA_ZH_MICRO_MAP` 时使用。

### 4.1 全季 8 角色总控速查矩阵

| `role_id` | 角色名 (`display_name`) | 层级 (`tier`) | 性别/年龄 | 语言 (`language_code`) | 规范口音码 (`accent_code`) | 锁定锚点 (`voice_id`) | 默认稳定度 | 出场集数 (`appearance_chapters`) | 季口音阵营 |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: | :--- | :---: |
| `lin_chen` | 林沉 / Lin Chen | `protagonist` | 男 / 34 | `zh-en` | `zh_en_bilingual_us` | `drama3_anchor_lin_chen` | `0.5` | `1–24`（全勤） | 核心美音 + 中文 |
| `zhou_mo` | 周默 / Zhou Mo | `core_supporting` | 男 / 35 | `zh-en` | `zh_mainland_sz` | `drama3_anchor_zhou_mo` | `0.5` | `1–24`（全勤） | 深圳中文 + 术语 |
| `victoria_vance` | Victoria Vance | `antagonist` | 女 / 39 | `en` | `us_silicon_valley` | `drama3_anchor_victoria_vance` | `0.5` | `1, 2, 3, 5, 6, 12, 18, 19, 20, 21, 23, 24` | 核心硅谷美音 |
| `alistair_finch` | Alistair Finch | `antagonist` | 男 / 48 | `en` | `uk_london_rp` | `drama3_anchor_alistair_finch` | `0.5` | `1, 3, 7, 8, 11, 12, 13, 19, 20, 24` | 核心伦敦 RP |
| `claire_chen_gc` | Claire Sterling | `core_supporting` | 女 / 37 | `en` | `us_nyc` | `drama3_anchor_claire_chen_gc` | `0.5` | `1, 6, 10, 11, 12, 13, 15, 16, 20, 22, 23, 24` | 核心纽约美音 |
| `henrik_lindqvist` | Henrik Lindqvist | `recurring` | 男 / 49 | `en` | `intl_eu_legal` | `drama3_anchor_henrik_lindqvist` | `0.5` | `11` | 精控北欧客串 |
| `rajiv_menon` | Rajiv Menon | `recurring` | 男 / 44 | `en` | `intl_indian_exec` | `drama3_anchor_rajiv_menon` | `0.5` | `13` | 精控印度客串 |
| `wei_ling_tan` | Wei-Ling Tan | `recurring` | 女 / 46 | `en` | `intl_singapore_vc` | `drama3_anchor_wei_ling_tan` | `0.5` | `13, 16` | 精控新加坡客串 |

---

### 4.2 八位角色四层深度制作档案

#### 1. `lin_chen` — 林沉 / Lin Chen（NovaEdge 创始人兼 CEO）
- **Layer 1 · 戏剧权力定位与全季弧光**：第一主角（`E001–E024` 全勤）。深圳硬核工科出身、斯坦福电子工程硕士，曾任硅谷硬件大厂资深架构师后回国创立 NovaEdge。全季弧光从“在沙丘路与伦敦大渠道夹缝中死保生存现金流的出海挑战者”（第一、二弧），一路蜕变为“在 25% 关税、算力禁令、华尔街做空与巨头并购围剿下掌控全球定价权、敲响纽交所铜钟的新一代跨国掌舵者”（第三、四弧）。
- **Layer 2 · 语言机制与口音规范**：`language_code="zh-en"`，`accent_code="zh_en_bilingual_us"`。公开谈判室、投委会、媒体问答与欧盟听证会 **100% 飙纯正硅谷精英美音**（清晰 rhotic 卷舌、精准重音计时、`155–180 WPM`）；切入《纸牌屋》式内心独白、深圳私下与周默密谋及片尾 Act 5 复盘时，瞬间切回**冷峻克制的现代科技高管普通话**——严禁中式英文平调，也严禁在中文里端洋腔。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：低沉磁性的 34 岁同声源真实双语男中音（`similarity_boost=0.85`，`default_stability=0.5`；高压反杀或锐利反问可切 `0.0`）。专属标签：`[measured]`、`[blunt]`、`[aside]`、`[coach]`、`[firmly]`、`[short pause]`。常用声场：公开谈判用 `boardroom`、潜台词独白用 `inner_monologue`、越洋紧急调度用 `phone_call`、Act 5 黑话拆局用 `studio_warm` 或 `dry`。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁播音腔/英语老师说教腔；严禁失控咆哮（越被逼入绝境声音越低沉稳定）；严禁中式翻译腔；严禁提及任何外部视频平台名称或“各位听众/欢迎收听今天的英语课”。
  - *Audition Line*：`"[measured] That eighty-million-dollar loss is a phantom number—not a cash loss, and you know it. [short pause] [aside] 她把可转债重估包装成经营失血，不是看不懂财报，是想趁签约前把估值砍掉三成。"`

#### 2. `zhou_mo` — 周默 / Zhou Mo（NovaEdge 联合创始人兼 CTO）
- **Layer 1 · 戏剧权力定位与全季弧光**：核心战友与工程脊梁（`E001–E024` 全勤）。常驻深圳南山研发中心与 SMT 产线，偶尔亲赴越南与伦敦救火。全剧的“物理现实校准仪”——当硅谷 VC 讲宏大叙事、华尔街玩金融魔术时，周默永远用镜片良率、BOM 成本、功耗毫秒数和公有云账单把所有人拽回地面。在 `E001_VB` 中更在深夜出租车后座与林沉共同承担片尾双人拆局。
- **Layer 2 · 语言机制与口音规范**：`language_code="zh-en"`，`accent_code="zh_mainland_sz"`。以干脆犀利的现代深圳科技职场普通话为主体，对话中自然嵌入精准硬件与算力英文术语（如 `BOM cost`、`on-device inference`、`yield ramp`、`rule-based guardrails`），英文词吐字利落准确但绝不刻意卖弄洋腔。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：带熬夜产线质感与冷幽默锋芒的 35 岁硬核科技男中音（`similarity_boost=0.85`，`default_stability=0.5`）。专属标签：`[deadpan]`、`[blunt]`、`[skeptical]`、`[tense]`、`[wryly]`（仅限 `zh-en` 中文语境安全触发 `带着一丝冷幽默`）、`[sighs]`。常用声场：`phone_call`（跨洋连线）、`dry`（深圳战情室/产线）、`studio_warm`（`E001_VB` 复盘）。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁相声捧哏式廉价夸赞（“问到根子上了”“这个比方绝了”）；严禁干巴巴念技术参数表；严禁丑化式拙劣中式英语。
  - *Audition Line*：`"[deadpan] [sighs] 产线刚把微显示模组的 BOM cost 压掉十八美金，硅谷那边又要为公有云 token 账单多烧三十块。[blunt] 听好了，明天切回端侧推理，不然卖一台亏一台。"`

#### 3. `victoria_vance` — Victoria Vance（Apex Horizon Ventures 主管合伙人）
- **Layer 1 · 戏剧权力定位与全季弧光**：核心资本对手（`E001, 2, 3, 5, 6, 12, 18, 19, 20, 21, 23, 24`）。沙丘路顶级风投女掌门，斯坦福 GSB + 前高盛 TMT 银行家。第一弧借 `$80M` 账面虚亏与算力军备竞赛极限压价，第二弧末（E012）密谋借增发剥离林沉超级投票权，第四弧（E019–E023）在宏观寒冬与做空潮中反复逼迫低价私有化或折价发行，直到 E023/E024 才在林沉的绝对实绩面前罕见举杯致敬。她不是扁平恶人，而是顶级华尔街/硅谷资本冷血理性的完美化身。
- **Layer 2 · 语言机制与口音规范**：`language_code="en"`，`accent_code="us_silicon_valley"`。纯正硅谷/纽约精英标准美音（`165–185 WPM`），连读自然、句尾向下收束极富控制权，最擅长先礼貌微笑抛赞美、停顿半秒后冷酷切进财报要害。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：冰冷优雅、丝绸裹钢的 39 岁精英女中低音（`similarity_boost=0.85`，`default_stability=0.5`，强硬抢话打断切 `0.0`）。专属标签：`[icy polite]`、`[measured]`、`[skeptical]`、`[coldly]`、`[interrupting]`、`[short pause]`（**禁用 `[wryly]`**）。常用声场：`boardroom`、`phone_call`。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁歇斯底里高声尖叫或反派卡通冷笑；严禁慢吞吞 ESL 教材语速；严禁使用 `[wryly]`。
  - *Audition Line*：`"[icy polite] That is a charming deck, Lin, truly. [short pause] [coldly] Now walk me through the eighty million that just flowed through into the income statement before my partners lose patience."`

#### 4. `alistair_finch` — Alistair Finch（跨大西洋高端消费科技零售采购副总裁）
- **Layer 1 · 戏剧权力定位与全季弧光**：核心渠道对手（`E001, 3, 7, 8, 11, 12, 13, 19, 20, 24`）。掌管伦敦 Selfridges 旗舰百货及跨海联采联盟（联动北美 Best Buy）的消费电子采购实权。代表欧洲老钱百货对“硅谷浮夸科技概念”的天然戒备——E001 拿云端 Token 吞噬利润施压，第二弧（E007–E012）祭出进场费、寄售条款、幻觉召回追责与联合营销费连环刀法，第四弧先在 E019 趁消费退潮索要 12% 滞销补贴，又于 E020 借华尔街做空报告威胁冻结 Q4 英国零售授信额度，最终在 E024 见证 NovaEdge 成为伦敦牛津街最赚钱的新品类标杆。
- **Layer 2 · 语言机制与口音规范**：`language_code="en"`，`accent_code="uk_london_rp"`。纯正现代伦敦标准 RP 英音（非卷舌 `non-rhotic`、清脆齿龈 `/t/`、地道英式 `BATH/LOT` 元音与克制冷讽重音，`145–165 WPM`），与 Victoria 的快节奏美音形成一听即分的声学双极对比。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：矜持冷峭、略带牛津/梅费尔腔优雅压迫感的 48 岁英伦男中低音（`similarity_boost=0.85`，`default_stability=0.5`）。专属标签：`[icy polite]`、`[understated]`、`[deadpan]`、`[sarcastic]`、`[dismissive]`、`[clears throat]`（**禁用 `[wryly]`**）。常用声场：`boardroom`、`phone_call`、`vast_hall`。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁提高音量咆哮（英式杀机全在轻描淡写的低调停顿里）；严禁飘成美式卷舌音或 BBC 晚间播音腔；严禁使用 `[wryly]`。
  - *Audition Line*：`"[understated] [clears throat] Oxford Street shoppers do not subsidize your cloud bill, Mr. Chen. [icy polite] Tell me what is good enough, and what it costs to run this thing a million times without eating into my margin."`

#### 5. `claire_chen_gc` — Claire Sterling（NovaEdge 总法律顾问兼北美商业负责人）
- **Layer 1 · 戏剧权力定位与全季弧光**：核心法务与商业护盾（`E001, 6, 10, 11, 12, 13, 15, 16, 20, 22, 23, 24`）。前纽约华尔街顶尖律所并购合伙人，冷静果决。E001 结尾第一时间揪出 Victoria 藏在第 14 页的对赌陷阱；E010 坚决撕毁带毒的北美医保拒赔无限连带赔偿协议；E011 与林沉并肩硬刚布鲁塞尔 GDPR 听证会；E020–E023 联手操盘做空反击、硬通货财资对冲与 IPO 定价路演。
- **Layer 2 · 语言机制与口音规范**：`language_code="en"`，`accent_code="us_nyc"`。纯正纽约/东海岸精英商业美音（`160–185 WPM`），语速紧凑干练、辅音如手术刀般精准，极擅长在高压条款博弈中用短促反问一针封喉。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：干脆利落、毫无多余废话的 37 岁纽约法务女中音（`similarity_boost=0.85`，`default_stability=0.5`）。专属标签：`[blunt]`、`[firmly]`、`[measured]`、`[pushback]`、`[tense]`、`[short pause]`（**禁用 `[wryly]`**）。常用声场：`boardroom`、`phone_call`、`dry`。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁甜美温顺客服腔或情绪化惊慌；严禁冗长学院派长难句；严禁使用 `[wryly]`。
  - *Audition Line*：`"[blunt] Do not sign that bridge sheet without a hard indemnity cap, Lin. [firmly] Victoria buried a super voting strip on page fourteen, and she is banking on you being too exhausted to notice."`

#### 6. `henrik_lindqvist` — Henrik Lindqvist（布鲁塞尔欧盟 AI 法案与 GDPR 首席合规顾问 · 精控客串）
- **Layer 1 · 戏剧权力定位与全季弧光**：第二弧合规风暴守门人（**仅出场 `E011`**）。在布鲁塞尔欧盟听证会现场向 NovaEdge 发难，代表欧洲监管体系对消费级 AI 视觉/语音终端的数据主权铁腕，迫使林沉与周默用硬核法兰克福本地物理隔离与 72 小时删除流水线过关。
- **Layer 2 · 语言机制与口音规范**：`language_code="en"`，`accent_code="intl_eu_legal"`。极度清晰精密的北欧精英法务英语（`145–160 WPM`），遵循 Lingua Franca Core 辅音与核重音高辨识标准，带冷冽的北欧清辅音质感。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：手术刀般冰冷克制的 49 岁男中音（`similarity_boost=0.82`，`default_stability=0.5`）。专属标签：`[coldly]`、`[measured]`、`[firmly]`、`[understated]`、`[short pause]`。常用声场：`vast_hall`、`boardroom`。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁政治演讲式高亢语调；严禁在 E001 或 E011 以外的集数越权出场。
  - *Audition Line*：`"[measured] Under European law, a prompt policy is a polite wish, not an enforcement mechanism. [coldly] Prove strict GDPR data residency on Frankfurt metal, or your glasses never clear customs."`

#### 7. `rajiv_menon` — Rajiv Menon（北美大型零售集团全球硬件采购高级总监 · 精控客串）
- **Layer 1 · 戏剧权力定位与全季弧光**：第三弧关税冲击引爆者（**仅出场 `E013`**）。印度理工学院与沃顿商学院出身的跨国采购狠角色。25% 关税落地次日即冷酷重算 NovaEdge 深圳直出基准成本，倒逼林沉 72 小时内拍板越南/墨西哥二供总装布局，否则直接撤走 Q4 采购大单。
- **Layer 2 · 语言机制与口音规范**：`language_code="en"`，`accent_code="intl_indian_exec"`。高清晰度受控精英印度裔高管英语（`155–175 WPM`），保留自然可控的轻卷舌与音节节奏特色，确保 B1–C1 听众无障碍听辨核心商业数字与采购条款。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：逻辑密不透风、干脆强势的 44 岁男中音（`similarity_boost=0.82`，`default_stability=0.5`）。专属标签：`[measured]`、`[blunt]`、`[skeptical]`、`[confident]`、`[short pause]`。常用声场：`boardroom`、`phone_call`。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁任何刻板印象漫画化夸张口音；严禁在 E001 或 E013 以外出场。
  - *Audition Line*：`"[measured] At twenty-five percent tariff, your Shenzhen base cost no longer clears our North American hurdle rate. [blunt] Qualify a Vietnam assembly line by Friday, or we reallocate the entire Q4 purchase order."`

#### 8. `wei_ling_tan` — Wei-Ling Tan（新加坡主权财富基金亚洲科技直投主管合伙人 · 精控客串）
- **Layer 1 · 戏剧权力定位与全季弧光**：第三弧地缘资本破局者（**仅出场 `E013, E016`**）。E013 在关税风暴中向林沉抛出东南亚备产战略资金线；E016 在新加坡滨海湾私密闭门会上点穿大国博弈台面客套话，以务实商业飞轮与区域数据本地化架构为前提，领投 1.2 亿美元成为 NovaEdge 抵御欧美双线夹击的关键压舱石。
- **Layer 2 · 语言机制与口音规范**：`language_code="en"`，`accent_code="intl_singapore_vc"`。沉静外交官级新加坡精英金融英语（英式标准底色叠加清晰优雅的东南亚精英韵律，`150–170 WPM`，LFC 辨识度 100%）。
- **Layer 3 · 声线质感、Drama 3 标签库与默认声场**：绵里藏针、从容笃定的 46 岁外交官女中音（`similarity_boost=0.82`，`default_stability=0.5`）。专属标签：`[measured]`、`[guarded]`、`[icy polite]`、`[confident]`、`[short pause]`。常用声场：`boardroom`、`dry`。
- **Layer 4 · 绝对禁忌与试音基准句**：
  - *Forbidden Habits*：严禁市井 Singlish 助词破坏主权基金威严；严禁在 E013/E016 以外出场。
  - *Audition Line*：`"[measured] Ignore the polite modulations coming out of Washington and Brussels, Lin. [guarded] Sovereign capital does not invest in geopolitics—we invest in teams pragmatically adjusting before everyone else."`

---

## 五、 剧情内生双语机制、Act 5 黑话拆局与 E001 四变体实验架构

### 5.1 剧情内生双语铁律（杜绝一切教科书味）

1. **公开权力场 = 100% 地道高管英语（`en`）**：只要身处沙丘路投委会、伦敦梅费尔谈判室、纽约律所、布鲁塞尔听证会或新加坡主权基金圆桌，所有角色（含林沉）一律使用 100% 无水分的真实 C1 商业英语飙戏；英文句天然配发 `TimelineCue.subtitle_translation`（仅渲染至 `.srt` 字幕第二行，**绝对不输入 TTS**）。
2. **内心独白与深圳暗线 = 潜台词自然破译（`zh` / `zh-en`）**：绝不让角色在谈判桌上生硬重复中文翻译！而是通过两种高度戏剧化的电影手法让 B1 听众“不查词典秒懂杀机”：
   - **《纸牌屋》式贴麦内心独白（`inner_monologue`）**：对手刚丢出致命英文黑话（如 `"What is good enough?"`），林沉用极短近麦中文点破其真实商业刀锋（“她问的不是品质底线，是在试探我肯不肯把毛利让出十个点”）。
   - **深圳跨洋密谋与战后复盘（`phone_call` / `dry`）**：挂掉英文会议的下一秒，周默在南山产线用极接地气的中文直接骂穿刚才那句英文的坑，自然完成第二次高频强化复现。

### 5.2 Act 5 独立 3 分钟《高管黑话复盘手记》（`165–210s`）标准工法

每集正片高潮在最强悬念钩子处收束后，经 1 声干净的 `smart_glasses_haptic_ping` 过渡至 `studio_warm` 贴麦空间，由主角 `lin_chen`（在 `E001_VB` 中为后座出租车内的 `lin_chen` + `zhou_mo`）亲自主讲 3 分钟高密度实战拆局，严格遵循四步闭环：
1. **痛点刺穿（Chinglish 雷区 vs. 权力场原话）**：直接对比职场人最常脱口而出的中式直译（`chinglish_trap`）为何一秒暴露业余感，再甩出刚才谈判室里一锤定音的 3–4 组核心高管原话。
2. **第一遍：确定性 `0.80x` 保音高慢速剖音（`playback_rate = 0.8`）**：**严禁让 TTS 用“请慢读”提示词重新合成**（防止音色变虚或语调失真），而是**100% 复用 `1.0x` 原生 Drama 3 干声缓存**，由 `mixer.py:condition_dialogue_clip()` 前置 FFmpeg **`atempo=0.800`**（WSOLA 保音高变速），精准落入 `120–145 WPM` 区间，清晰剥开连读、弱读与爆破辅音。
3. **第二遍：`1.0x` 原速影子跟读 + 黄金静默窗（`gap_after_s >= 1.8s`，目标 `2.2–3.0s`）**：紧接一遍完整 `1.0x` 高管原速示范后留足静默空白，依据 Baddeley 工作记忆语音环路（~2.0s 窗口）与 Swain 可理解输出假说，逼迫听众在地铁或驾驶座上立刻开口跟读形成口腔肌肉记忆。
4. **30 秒战后复盘金句收束**：用一句直击职场的下班行动指令收尾，无缝引导领取/收听下集。

### 5.3 第一期（E001）四变体科学对照实验架构（同步 `RESEARCH_REPORT.md` §5.4）

为客观验证哪种双语叙事配比在真实 B1–C1 听众中最具追更黏性与学习转化率，第一期 **《八千万幽灵账单 / The \$80M Phantom》** 锁定全部控制常量，仅在叙事结构、英文占比、抢话密度与拆局形态上设立 4 个独立变体（外加声纹校准包 `AUDITION_GLOBAL_EDGE`）：

- **四变体 100% 共享控制常量**：
  - 同一核心危机（C 轮过桥融资 + 伦敦旗舰签约前夜的 `$80M` 账面巨亏 + 云端 Token 账单夹击）；
  - 同一 5 条实证种子切片：`02_BIZ_Anthropic`、`012_AI`、`039_BIZ`、`090_USC`、`059_FIN`；
  - 同一 8 组（13 条精确原话）必考英文词块：`phantom number`、`not a cash loss` + `flowed through into the income statement`、`capital-efficient`、`10 times the throughput`（严禁写为 `10x`）+ `Pick your favorite number`、`In other words`、`eating into budgets` + `a really hard trade-off`、`What is good enough` + `run this thing a million times`、`upside` + `When are you going to get it`；
  - 同一 4+1 核心卡司与 **100% 美音 + 伦敦 RP** 英文口音；统一时长 `600–840s`（Acts 1–4 `480–600s` + Act 5 `165–210s`）。

| 变体 ID | 中文版本定位 | 预估英文占比 | 标志性叙事与声学自变量 | 抢话 / 叠音硬门槛 | Act 5 拆局形态 |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **`E001_VA`** | **HBO 纯飙戏冷峻商战版** | `~70%` | 零内心独白冻帧，极致 *Succession* 会议室硬碰硬 + 私下深圳中文复盘 | `>= 6` 处负间隔抢话 | Lin Chen 贴麦独白标准拆局 |
| **`E001_VB`** | **纸牌屋冻帧潜台词狙击版** | `~55%` | 关键英文杀招落音即触发 `freeze_frame_sub_drop` + `inner_monologue` 中文刺穿潜台词 | `>= 4` 处负间隔抢话 | 后座出租车内 Lin Chen + Zhou Mo 双人复盘 |
| **`E001_VC`** | **三时区惊悚推进与实战跟读版** | `~60%` | 深圳深夜工厂 × 硅谷早盘 × 伦敦午后三线交叉快剪（`phone_call` + `boardroom` 倒计时） | `>= 6` 处高密抢话 | 对手原声甩狠话 → 静默跟读反击角色扮演演练 |
| **`E001_VD`** | **纪实同传叠音混合版** | `~55%` | 移植 `buffett_letters` 已验证的 `duck_under_next=True` 余弦同传叠音 + 调查纪实视角 | `>= 3` 处抢话 + **`>= 2`** 组同传叠音 | 纪实复盘 + `0.80x/1.0x` 双速跟读 |

- **100 分盲测决选与「混合胜出合成规则」（Hybrid-Winner Synthesis Rule）**：四变体同批渲染后匿名打乱为 `Track 1–4`，按 **前 30 秒钩子（15）+ HBO 商战真实感（20）+ 双语丝滑不掉线（15）+ 口音权威质感（15）+ 24h 教学黏性（15）+ 45 秒爆款潜质（10）+ 声场听感（10）= 100 分** 盲测评分；总分第一锁定为 `E002–E024` 主干母版，并允许从亚军/季军变体中**至多吸收 2 项独立模块化胜出工法**合成终极第一季生产标准。

---

## 六、 声学空间 DSP 规范、HBO 原声调色板与 7 大物理拟音库

### 6.1 企业声学空间 DSP 滤波链规范（100% 对齐 `src/aigc_audio_pipeline/mixer.py`）

本剧台本与混音严格仅使用 `ALLOWED_ACOUSTIC_SPACES` 中适配现代跨国商战的 **7 个有效声场**（**明令禁止使用遗留仙侠空间 `mental_realm`**；`vintage_study` 仅作历史档案对比保留，本剧默认不启用）。所有对白进入空间滤波前均先统一经基础链 `aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=75`，若 `playback_rate != 1.0` 则**先置** `atempo={rate:.3f}` 保音高变速，再接空间滤波与响度门禁（`effective_dur >= 1.4s` 走 `loudnorm=I=-16:TP=-1.5:LRA=11`，短句走 `alimiter=limit=0.84:level=disabled`）：

| `acoustic_space` | `mixer.py` 精确 FFmpeg 滤波链 | 听觉物理质感 | 本剧授权适用场景 |
| :--- | :--- | :--- | :--- |
| **`boardroom`** | `aecho=0.88:0.86:18\|36:0.12\|0.06` *(严格无尾随 `apad`)* | 玻璃幕墙会议室紧致早反射，声像干净冷峻且**绝不拖尾糊掉负间隔抢话** | 沙丘路 VC 投委会、伦敦 Selfridges 买手谈判室、纽约律所与董事会交锋 |
| **`inner_monologue`** | `equalizer=f=150:t=q:w=1.2:g=1.8,equalizer=f=3200:t=q:w=1.4:g=0.9` *(零混响回声)* | 极贴耳近讲胸腔低频厚度 + 齿音清晰度微提，瞬间打破第四面墙 | 林沉《纸牌屋》式中文潜台词独白、冻帧内心旁白（彻底取代仙侠 `mental_realm`） |
| **`phone_call`** | `highpass=f=300,lowpass=f=3400,acompressor=threshold=-18dB:ratio=3:attack=5:release=60` | 标准 300–3400Hz 跨洋加密通话带通与动态压缩，1 秒区分电话远端声线 | 深圳–硅谷–伦敦三时区深夜越洋连线、周默工厂急电、突发媒体预警 |
| **`studio_warm`** | `equalizer=f=175:t=q:w=1.2:g=1.2,equalizer=f=3600:t=q:w=1.4:g=0.8` | 温润亲密的高级播客录音棚质感，无会议室冷硬反射 | Act 5 片尾 3 分钟《高管黑话复盘手记》主声场、出租车后座深夜复盘 |
| **`dry`** | *(无附加房间滤波，仅基础 48kHz + 75Hz 高通)* | 零染色的超近干声，清晰度极高 | 深圳战情室私密低语、Act 5 `0.80x` 关键短语剖析对比、中性默认回退 |
| **`vast_hall`** | `aecho=0.88:0.85:35\|75:0.16\|0.08,apad=pad_dur=0.12` | 中大型礼堂/听证厅自然空间纵深与克制衰减 | 布鲁塞尔欧盟听证厅（E011）、CES 全球发布会、纽交所敲钟大厅（E024） |
| **`memory_echo`** | `highpass=f=180,lowpass=f=5500,aecho=0.85:0.80:65\|130:0.24\|0.12,apad=pad_dur=0.20` | 略带频段收窄与深远回响的录音回放质感 | 关键历史语音留言回放、媒体发布会实录闪回、证据音频播放 |
| ~~`mental_realm`~~ | ~~仙侠神识空间~~ | **严禁在本剧使用！** | 内心独白一律使用 `inner_monologue` |

### 6.2 HBO 极简商战原声调色板（`ACE-Step 1.5 XL` · 高复用零人声铁律）

为最大化 Colab 96GB G4 上基于提示词 SHA-256 的原声干音缓存复用率（**目标全季 stem 复用率 `> 80%`**），同时彻底杜绝仙侠古筝、流行电音鼓点或人声和声污染商战质感，全季 24 集统一采用以下 **5 支规范 HBO 极简室内乐 + 克制冷峻脉冲原声母题**（`bgm_gain_speech: 0.06–0.08`，`bgm_gain_gap: 0.24–0.30`）：

| OST 母题 ID | 对应剧集情绪与幕次 | 规范 `ACE-Step/acestep-v15-xl-turbo-diffusers` 英文提示词（强制零人声、零国风、零流行鼓点） |
| :--- | :--- | :--- |
| **`ost_boardroom_cold_open`** | 冷开场与沙丘路/伦敦冷峻对峙（Acts 1–2） | `Minimalist HBO prestige corporate drama underscore, taut muted solo cello ostinato over sparse dark felt piano chords and subtle low upright bass pulse, cold glass-tower tension, restrained chamber strings, strictly no vocals, no singing, no pop drums, no trap beats, no traditional Chinese instruments, no guzheng, purely instrumental` |
| **`ost_valuation_escalation`** | 数据交锋、条款博弈与三时区倒计时（Acts 2–3） | `Sophisticated modern financial thriller score inspired by minimalist chamber strings and restrained analog ticking pulse, crisp staccato viola rhythm with cool piano arpeggios building quiet executive pressure, no loud brass fanfare, no EDM drops, no vocals, no singing, no traditional Asian instruments, purely instrumental` |
| **`ost_shenzhen_midnight_lab`** | 深圳深夜产线、端侧攻关与内心独白（`inner_monologue` / 暗线） | `Intimate late-night tech founder underscore, warm muted Rhodes electric piano and subtle low cello harmonics with ultra-clean minimal ambient pad, focused midnight engineering tension in a quiet glass lab, no percussion, no vocals, no singing, no guqin, purely instrumental` |
| **`ost_endgame_counterstrike`** | 决胜反杀、听证通关与 IPO 敲钟（Act 4 高潮） | `Dignified modern prestige drama climax underscore, resolute low strings swelling with clean grand piano octaves and crisp understated timpani pulse, triumphant yet ice-cool executive composure, no cheesy pop rock, no choir, no vocals, no singing, no erhu, purely instrumental` |
| **`ost_blackbook_debrief`** | Act 5 3 分钟高管黑话拆局与跟读背景 | `Ultra-clean minimalist modern executive podcast bed, soft sparse muted acoustic bass pluck and warm understated felt piano chords at slow steady pulse, spacious midrange leaving total clarity for spoken voice and shadowing pauses, no drums, no melody solo, no vocals, no singing, purely instrumental` |

### 6.3 7 大纯物理英文拟音库（100% 同步 `voice_casting_registry.json`）

所有拟音严格遵循 `OpenMOSS-Team/MOSS-SoundEffect-v2.0` 纯物理发声规范：**绝对禁止出现任何人声/叹气/咳嗽/窃语词汇**，统一以英文逗号分隔的 **`, pure foley, no human voice`** 结尾（绝不写 `"with no human voice"` 以防误触 Colab 净化正则）：

| `motif_id` | 中文名称 | 时长 (`s`) | `prompt_influence` | 规范 `sfx_prompt`（逐字对齐 `voice_casting_registry.json`） |
| :--- | :--- | :---: | :---: | :--- |
| `glass_boardroom_door` | 沙丘路玻璃会议室门液压闭锁声 | `2.2` | `0.60` | `Heavy frameless tempered glass boardroom door swinging shut with a muted brushed-steel hydraulic latch click inside a quiet Sand Hill Road office suite, pure foley, no human voice` |
| `smart_glasses_haptic_ping` | NovaEdge Glass 镜腿触控微震与光学提示音 | `1.4` | `0.62` | `Crisp minimalist titanium smart-glasses temple haptic tap followed by a subtle ultra-clean low-latency micro-chime and soft optical shutter pulse in close stereo proximity, pure foley, no human voice` |
| `shenzhen_smt_factory_line` | 深圳南山 SMT 无尘产线精密贴片声 | `3.2` | `0.60` | `Precision high-speed surface-mount pick-and-place robotics humming rhythmically beside soft pneumatic air valves and optical inspection conveyor clicks inside a Shenzhen electronics cleanroom, pure foley, no human voice` |
| `transpacific_call_connect` | 跨太平洋三时区加密会议连线声 | `1.8` | `0.65` | `Crisp executive smartphone conference bridge dial chime clicking cleanly into a quiet transpacific encrypted telecom line hum across an empty midnight desk, pure foley, no human voice` |
| `paper_term_sheet_slide` | 胡桃木长桌条款清单推滑与钢笔合盖声 | `1.9` | `0.60` | `Thick bound term-sheet dossier sliding briskly across a polished walnut conference table followed by a solid fountain pen cap snapping shut on heavyweight cardstock, pure foley, no human voice` |
| `freeze_frame_sub_drop` | 《纸牌屋》式冻帧潜台词低频收束声 | `1.2` | `0.62` | `Subtle cinematic low-frequency sub-bass tension swell tightening smoothly into sudden vacuum room stillness like an editorial focus snap, pure foley, no human voice` |
| `nyse_bell_and_ticker_pulse` | 交易所开市铜钟与精密金融节拍声 | `2.8` | `0.60` | `Resonant brass financial exchange opening bell ringing crisply once over subtle precision mechanical stopwatch ticks and distant trading desk keyboard taps, pure foley, no human voice` |

---

## 七、 黄金五幕通勤预算、质检门禁、反油腻红线与商业变现闭环

### 7.1 单集 `10–14 分钟`（`600–840s`）黄金五幕量化预算表

以百条高管语料实证语速 **`170.34 WPM`**（原始基线 **`170.20 WPM`**）与中文播讲实测速率 **`3.55–3.65 字/秒`** 为工程锚点，单集时长与台词体量严控如下：

| 幕次 | 戏剧 / 教学功能 | 目标时长 | 声场与语速锚点 | 单句长度上限（防长句幻觉与气口崩坏） | 核心交付产出 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **Act 1 · 冷开场与危机引爆** | 前 30 秒直接扔进高压英文谈判或突发越洋警报，零寒暄铺垫 | `90–120s` | `boardroom` / `phone_call`；EN `160–185 WPM` | EN `<= 55` 词；ZH `<= 85` 字 | 建立本期商业生死赌注 + 埋下首枚 45s 冲突切片候选段 |
| **Act 2 · 双线施压与潜台词交锋** | VC/大渠道/监管连环出招，穿插首次 `inner_monologue` 或深圳暗线拆招 | `135–165s` | `boardroom` ↔ `inner_monologue`；含 `[-0.25, -0.05]s` 抢话 | EN `<= 55` 词；ZH `<= 85` 字 | 密集植入 `3–4` 组目标高管英文短语 + 中文潜台词自然破局 |
| **Act 3 · 底牌翻转与正面硬刚** | 主角亮出工程/财务/合规实锤，迎来全集最炸裂的 45 秒英美飙戏高潮 | `145–175s` | `boardroom` / `vast_hall`；EN `150–185 WPM` 峰值交锋 | EN `<= 55` 词；ZH `<= 85` 字 | 完成剩余 `3–4` 组目标词块植入 + 产出一刀直剪的 `38–55s` 爆款切片 |
| **Act 4 · 战果落定与下集悬念钩子** | 本集商业博弈暂告段落，但最后 20 秒甩出更高阶危机 `cliffhanger` | `110–140s` | `boardroom` → `phone_call` / `dry` | EN `<= 55` 词；ZH `<= 85` 字 | 闭合单集爽感（Acts 1–4 合计 **`480–600s`**），锁定下集追更钩子 |
| **Act 5 · 高管黑话复盘手记（拆局）** | 主角原声承接：Chinglish 雷区对比 + `0.80x` 慢拆 + `1.0x` 跟读留白 | **`165–210s`** | `studio_warm` / `dry`；慢拆 `atempo=0.80`（`120–145 WPM`），跟读 `1.0x` + **`gap_after_s >= 1.8s`** | 每组示范短语 `4–18` 词，留白 `2.2–3.0s` | 闭合“听懂 → 纠偏 → 开口输出”习得环路；全集总时长 **`600–840s`** |

### 7.2 零 API 96GB 生产质检与母带门禁

1. **声纹源门禁（M4）**：全员 8 角色采用 `ANCHOR_SCHEMA_VERSION = "v2_real_human_studio"`，`44100 Hz` 单声道 PCM16 `-16 LUFS` 干声（`10–18s` 棚录 + 逐字 `.txt` 旁车文本），生产模式 **0% `edge-tts` / 合成音**。
2. **双脚本 ASR 自动化质检（`src/aigc_audio_pipeline/qa.py`）**：本地 `faster-whisper-small-int8` 逐句核验：
   - 纯英台词（`en`）：当 `len(exp_en) >= 3` 校验英文 LCS 词召回率 `>= 0.72`，`len(exp_en) >= 5` 校验句尾保真；
   - 混合台词（`zh-en`）：**同时**校验中文字符召回（`len(exp_cjk) >= 4`）与嵌入英文关键词召回（`len(exp_en) >= 3`），并执行脚本感知句尾核验（`min_char_recall = 0.72`）；
   - 标签防泄漏门禁：静态 `COMMON_TAG_WORDS`（54 词，含全部 14 个 HBO 商战标签词）叠加本句动态标签提取，一旦 Drama 3 误读方括号标签立即自动重试（3 级重试阶梯 `attempt = 1 → 2 → 3`）；信号门禁要求 `duration_s >= 0.25s`、`peak_dbfs >= -45.0 dBFS`。
3. **三总线广播级母带规范（`mixer.py`）**：Bus A（精修对白）+ Bus B（永不被压混的前景物理拟音）+ Bus C（分幕自适应闪避原声），最终经 `-1.0 dBTP` 真峰值限幅器输出 **`48kHz` 立体声 WAV + 192kbps MP3（目标响度 `-16.0 ± 0.5 LUFS`，真峰值 `<= -1.0 dBTP`）** + 零重叠双行中英 `.srt` 字幕。

### 7.3 反套话 / 反 AI 油腻 / 反切片味强制红线表

以下内容在全季正片台词、试音句、剧情梗概、钩子文案与黑话潜台词中**严格零容忍**：

| 违禁类别 | 严禁出现的具体字符串或表演恶习 | 违规后果与替代规范 |
| :--- | :--- | :--- |
| **课堂/播客寒暄套话** | `"各位听众"`、`"欢迎收听今天的英语课"`、`"欢迎收听"`、`"大家好，我是..."` | 直接从谈判室交锋或越洋急电切入，零主持人开场白 |
| **廉价捧哏 AI 味套话** | `"问到根子上了"`、`"这个比方绝了"`、`"说得太好了"`、`"一针见血"` | 角色间用反问、沉默、拆台、冷幽默和商业数字推进，绝不互相吹捧 |
| **外部切片搬运泄露** | `"YouTube"`、`"视频号"`、`"上期切片"`、`"本期视频"`、`"今天这条短视频"` | 彻底解耦外部来源，100% 保持独立连续商战剧世界观纯净度 |
| **错误表演与声学退化** | 播音腔、晚会腔、古风朗诵腔、咆哮吵架、仙侠 `mental_realm`、纯英角色误用 `[wryly]` | 锁定 HBO 礼貌带刀克制写实风 + 规范 7 企业声场 + 校验标签白名单 |
| **伪造语料溯源** | 把 `world_bridge` 渠道/GDPR 词伪造为某条原切片出处，或把 `10x the throughput` 冒充 `012_AI` 原文 | 严守 70/30 诚实词源铁律；`012_AI` 严格使用经机器验真的 **`10 times the throughput`** |

### 7.4 全平台分发与三层商业变现闭环（同步 `RESEARCH_REPORT.md` §1）

1. **免费大盘音频主阵地**：**小宇宙**（核心口碑旗舰与时间戳评论场）、**喜马拉雅**（泛通勤车载与付费专栏收口）、**微信听书/公众号音频**（微信生态零跳转私域中枢）。
2. **45 秒高能飙戏引流飞轮**：每集原生内置至少 1 段独立成篇的 **`38–55s` 竖屏英美飙戏冲突切片**（动态声波 + 英文高管原话扫光 + 红色潜台词译注），以强商战钩子把公域流量导回 `10–14` 分钟正片与 Act 5 拆局。
3. **三层变现 SKU 与零 API 算力剪刀差**：第一季 24 集在 Colab 96GB G4 上全季直接算力成本 **`~25–30 CU`（`< ¥100`，`$0` 语音 API 费）**，后端承接三阶高毛利产品——**Tier 1《第一季高管黑话双语精读与 `0.80x` 跟读手册》（`¥79`）**、**Tier 2 喜马拉雅/私域全季深度付费专栏（`¥159`）**、**Tier 3 6 周《跨国谈判与融资路演影子跟读训练营》（`¥699`）**；按基准测算模型仅需售出 **2 份 `¥79` 手册即可 100% 覆盖全季直接 GPU 渲染成本**。
