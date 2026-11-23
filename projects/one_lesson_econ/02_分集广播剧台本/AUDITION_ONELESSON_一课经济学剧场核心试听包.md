# AUDITION_ONELESSON ·《《一课经济学剧场：别只看眼前那一步》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 一课经济学剧场八角色试听 | `Warm modern documentary acoustic chamber score, intimate felt upright piano voicings, gentle walking upright double bass and warm fingerpicked acoustic guitar evoking a sunlit urban podcast cafe studio and lucid everyday economic clarity, purely acoustic instrumental, no loud drums, no percussion, no synth, no singing, no vocals, no Chinese instruments` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 一课经济学剧场八角色试听】

- 🔊 **`[ol01_cafe]` 音效 · 独立顺播**（复用母题 `cafe_chalkboard_cup`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Warm intimate modern urban podcast cafe study ambience with crisp chalk drawing quick connecting lines on a matte blackboard, a warm ceramic mug gently placed onto an oak table, and notebook paper turning softly, pure foley, no human voice`

- 🎙️ **`[ol02_narr]` 节目旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 梧桐巷的暖灯亮了。一项听起来格外动听的经济口号，究竟是救命良方，还是埋在半年后的暗雷？别急着鼓掌，先跟着这堂课往后多看一步。

- 🔊 **`[ol03_glass]` 音效 · 叠加下一句起拍**（复用母题 `broken_glass_sweep`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Crisp impact of a street-front shop window pane shattering cleanly onto a stone sidewalk followed by steady bristle broom strokes sweeping glass shards into a metal dustpan, pure foley, no human voice`

- 🎙️ **`[ol04_zhao]` 老赵 (`boss_zhao`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 砸碎我面馆两千块的落地玻璃，玻璃店确实赚了一单，可我原本给老婆买大衣的钱没了！整条街到底多赚了还是白亏了一块玻璃？

- 🎙️ **`[ol05_xu]` 徐科长 (`planner_xu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 顾老师，纸上谈兵太轻松！要是房租不限价、亏损老厂不补贴、工资不划高线，普通老百姓眼前过不去的坎谁来拉一把？

- 🎙️ **`[ol06_liu]` 刘大爷 (`landlord_liu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [sighs] [seriously] 一纸限租令把我房租砍掉三成，水管爆了我都修不起，干脆撤盘不租；转头物价一涨，我存折还在悄悄缩水！

- 🎙️ **`[ol07_chen]` 小陈 (`young_chen`)** （`stability=0.5` | 句后气口 `0.2s`）  
  > [angry] 听说限租令要降房租、最低工资要涨到六千五，我高兴了一整宿；结果第二天中介说没房可租，厂里也不招新手学徒了！

- 🎙️ **`[ol08_mei]` 林梅 (`lin_mei`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [seriously] [calmly] 换上智能织机，每件衣服成本降了三十块；可拿我们交的税去续命亏损老厂，倒把我们准备扩招的新产线生生拖垮了。

- 🎙️ **`[ol09_gu]` 顾明远 (`mentor_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 坏经济学只盯着眼前看得见的一撮人，好经济学却要顺着钱和资源的流向，追查一年后落在所有人身上的看不见的账本。

- 🎙️ **`[ol10_qiao]` 乔安 (`host_qiao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《一课经济学剧场：别只看眼前那一步》——零公式、零翻译腔，用中国街坊的实在账本，练就你的二阶透视眼。
