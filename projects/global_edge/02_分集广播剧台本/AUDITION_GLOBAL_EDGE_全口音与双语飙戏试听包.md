# AUDITION_GLOBAL_EDGE ·《《跨境底牌：硅深暗战》全口音与双语飙戏试听包（8 角色 · G1–G8 验收）》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`voice_casting_registry.json#G1-G8`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.25s`，片尾收束 `0.8s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `act1` | 全口音与双语飙戏试听总览（G1–G8 声纹/声场/慢拆/同传全门禁验收） | `Minimalist HBO prestige corporate drama underscore, taut muted solo cello ostinato over sparse dark felt piano chords and subtle low upright bass pulse, cold glass-tower tension, restrained chamber strings, strictly no vocals, no singing, no pop drums, no trap beats, no traditional Chinese instruments, no guzheng, purely instrumental` | 60s | `0.07` / `0.28` |

## 二、 逐句演出与音效时间轴清单

### 【act1 · 全口音与双语飙戏试听总览（G1–G8 声纹/声场/慢拆/同传全门禁验收）】

- 🔊 **`[aud_001]` 音效 · 独立顺播**（复用母题 `glass_boardroom_door`） （时长 `2.2s` | 句后留白 `0.18s`）  
  Prompt: `Heavy frameless tempered glass boardroom door swinging shut with a muted brushed-steel hydraulic latch click inside a quiet Sand Hill Road office suite, pure foley, no human voice`  
  *导演备注：G6/G8: 沙丘路玻璃门开场 Foley*

- 🎙️ **`[aud_002]` Victoria Vance (`victoria_vance`)** （`stability=0.5` | 语言 `en` | 声场 `boardroom` | 句后气口 `-0.15s`）  
  > [icy polite] That is a charming deck, Lin, truly. [coldly] Now walk me through the eighty million that just flowed through into the income statement before my partners lose patience.  
  *中文字幕译文：很漂亮的路演文稿，林，真的。现在在我合伙人失去耐心之前，给我解释清楚刚流进利润表的那八千万美元。*  
  *导演备注：G2/G4/G6: 硅谷美音女合伙人 + -0.15s 负间隔接抢话*

- 🎙️ **`[aud_003]` 林沉 / Lin Chen (`lin_chen`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.22s`）  
  > [interrupting] [measured] That eighty-million-dollar loss is a phantom number—not a cash loss, and your diligence team already knows it.  
  *中文字幕译文：那八千万美元亏损纯粹是个幽灵数字——不是现金亏损，你们尽调团队早就心知肚明。*  
  *导演备注：G1/G4/G6: 林沉公开硅谷英文（同一真人双语锚点）*

- 🎙️ **`[aud_004]` 林沉 / Lin Chen (`lin_chen`)** （`stability=0.5` | 语言 `zh` | 声场 `inner_monologue` | 句后气口 `0.28s`）  
  > [aside] 她把可转债重估包装成经营失血，不是看不懂财报，是想趁签约前把估值砍掉三成。  
  *导演备注：G1/G6: 林沉贴麦中文 inner_monologue（零混响、验证跨语种音色一致）*

- 🎙️ **`[aud_005]` Alistair Finch (`alistair_finch`)** （`stability=0.5` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.25s`）  
  > [understated] [clears throat] Oxford Street shoppers do not subsidize your cloud bill, Mr. Chen. [icy polite] Tell me what is good enough, and what it costs to run this thing a million times without eating into budgets.  
  *中文字幕译文：牛津街顾客不会替你的云端账单买单，陈先生。告诉我做到什么线算够用，以及把这东西跑一百万次又不啃噬预算要花多少钱。*  
  *导演备注：G2/G4: 伦敦 RP 男中低音（与 Victoria 美音 3 秒听觉区隔）*

- 🎙️ **`[aud_006]` Claire Sterling (`claire_chen_gc`)** （`stability=0.5` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.25s`）  
  > [blunt] Do not sign that bridge sheet without a hard indemnity cap, Lin. [firmly] Victoria buried a super voting strip on page fourteen, and she is banking on you being too exhausted to notice.  
  *中文字幕译文：没有硬性赔偿上限别签那份过桥协议，林。维多利亚在第十四页埋了超级投票权条款，就赌你熬得太累没看见。*  
  *导演备注：G4: Claire Sterling 纽约法务快节奏美音*

- 🎙️ **`[aud_007]` 周默 / Zhou Mo (`zhou_mo`)** （`stability=0.5` | 语言 `zh-en` | 声场 `phone_call` | 句后气口 `0.25s`）  
  > [deadpan] [sighs] 产线刚把微显示模组的 BOM cost 压掉十八美金，硅谷那边又要为公有云 token 账单多烧三十块。[blunt] 听好了，明天切回本地 NPU 推理，不然卖一台亏一台。  
  *导演备注：G6/G7: 周默 phone_call 电话带通 + zh-en 双脚本 ASR 验收*

- 🎙️ **`[aud_008]` Rajiv Menon (`rajiv_menon`)** （`stability=0.5` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.25s`）  
  > [measured] At twenty-five percent tariff, your Shenzhen base cost no longer clears our North American hurdle rate. [blunt] Qualify a Vietnam assembly line by Friday, or we reallocate the entire fourth-quarter order.  
  *中文字幕译文：按百分之二十五关税算，你们深圳基础成本已过不了我们北美门槛。周五前通过越南产线认证，否则我们重分整个四季度订单。*  
  *导演备注：G3: 印度裔高管国际客串清晰度验收（仅限试听包与 E013）*

- 🎙️ **`[aud_009]` Wei-Ling Tan (`wei_ling_tan`)** （`stability=0.5` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.25s`）  
  > [measured] Ignore the polite modulations coming out of Washington and Brussels, Lin. [guarded] Sovereign capital does not invest in geopolitics—we invest in teams pragmatically adjusting before everyone else.  
  *中文字幕译文：别管华盛顿和布鲁塞尔的客套风向，林。主权资本不投地缘政治——我们只投比所有人都更快务实调整的团队。*  
  *导演备注：G3: 新加坡主权基金客串清晰度验收（仅限试听包与 E013/E016）*

- 🎙️ **`[aud_010]` Henrik Lindqvist (`henrik_lindqvist`)** （`stability=0.5` | 语言 `en` | 声场 `vast_hall` | 句后气口 `0.28s`）  
  > [measured] Under European law, a prompt policy is a polite wish, not an enforcement mechanism. [coldly] Prove strict European data residency on Frankfurt metal, or your glasses never clear customs.  
  *中文字幕译文：在欧洲法律下，提示词政策只是礼貌愿望，不是强制执行机制。拿出法兰克福本地物理机数据留存证明，否则眼镜永不通关。*  
  *导演备注：G3/G6: 欧盟法务客串 + vast_hall 听证会声场验收（仅限试听包与 E011）*

- 🎙️ **`[aud_011]` Victoria Vance (`victoria_vance`)** （`stability=0.5` | 语言 `en` | 声场 `boardroom` | **同传叠音：原声独奏 `3.5s` → 压混 `0.15`** | 句后气口 `0.0s`）  
  > [understated] You pitched tremendous three-year subscription upside in that room, Lin—so answer the only question that matters: when are you going to get it?  
  *中文字幕译文：你在那间屋里画了巨大的三年订阅上行空间，林——那就回答唯一重要的问题：你到底什么时候拿到这笔钱？*  
  *导演备注：G6/G8: duck_under_next 同传原声独奏 3.5s -> 0.15 压混验收*

- 🎙️ **`[aud_012]` 林沉 / Lin Chen (`lin_chen`)** （`stability=0.5` | 语言 `zh` | 声场 `studio_warm` | 句后气口 `0.28s`）  
  > [aside] 同传叠音测试：在沙丘路谈估值，画再大的远期上行空间都没用，投资人只盯现金到底哪年落袋。  
  *导演备注：G6/G8: studio_warm 中文同传叠音轨 + 双行 SRT 验证*

- 🔊 **`[aud_013]` 音效 · 独立顺播**（复用母题 `smart_glasses_haptic_ping`） （时长 `1.4s` | 句后留白 `0.2s`）  
  Prompt: `Crisp minimalist titanium smart-glasses temple haptic tap followed by a subtle ultra-clean low-latency micro-chime and soft optical shutter pulse in close stereo proximity, pure foley, no human voice`  
  *导演备注：G5/G8: 切入 Act 5 0.80x 慢拆与原速跟读测试*

- 🎙️ **`[aud_014]` 林沉 / Lin Chen (`lin_chen`)** （`stability=0.5` | 语言 `en` | 语速 `[0.80x]` | 句后气口 `0.7s`）  
  > [coach] Pick your favorite number—10 times the throughput wins when you run this thing a million times.  
  *中文字幕译文：参数随便你挑——把这东西跑一百万次时，十倍吞吐量才是硬道理。*  
  *导演备注：G5: 0.80x atempo 保音高慢拆验收（dry 零混响）*

- 🎙️ **`[aud_015]` 林沉 / Lin Chen (`lin_chen`)** （`stability=0.5` | 语言 `en` | 句后气口 `2.2s`）  
  > [coach] Pick your favorite number—10 times the throughput wins when you run this thing a million times.  
  *中文字幕译文：参数随便你挑——把这东西跑一百万次时，十倍吞吐量才是硬道理。*  
  *导演备注：G5: 1.0x 原速跟读 + 2.2s 留白验收*
