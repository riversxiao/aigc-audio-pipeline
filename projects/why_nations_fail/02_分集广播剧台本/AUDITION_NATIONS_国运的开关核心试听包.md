# AUDITION_NATIONS ·《《国运的开关：〈为什么国家会失败〉制度史剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 国运的开关八角色试听 | `Grand historical documentary cinematic chamber strings, warm French horn swell and deep expressive cello over sustained contrabass pedal tones evoking sweeping borderlands and centuries of diverging national fate, purely acoustic orchestral chamber instrumental, no pop drums, no percussion, no vocals, no singing, no Chinese instruments` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 国运的开关八角色试听】

- 🔊 **`[wn_a01_wind]` 音效 · 独立顺播**（复用母题 `border_fence_wind`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Dry desert wind humming across a taut metallic border wire fence separating a smooth paved town street with gentle passing traffic from a dusty unpaved lane with rattling cart wheels, pure foley, no human voice`

- 🎙️ **`[wn_a02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 有些城池生在荒漠却商贾云集，有些帝国坐拥银矿却百年停滞。翻开五百年世界经济史，真正撬动国运的，是一道悄然扳动的制度开关。

- 🔊 **`[wn_a03_map]` 音效 · 叠加下一句起拍**（复用母题 `archive_map_unroll`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Warm hushed historical archive study ambience as a heavy parchment world map unrolls across a dark mahogany table, a brass magnifying glass sets down softly, and a fountain pen scratches ledger paper, pure foley, no human voice`

- 🎙️ **`[wn_a04_shen]` 沈观澜 (`prof_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 同一片沙漠、同一种气候，连墙两边都是亲表兄弟，收入却硬生生差出三倍。地理给不了答案，真正决定命运的，是看不见的制度规矩。

- 🎙️ **`[wn_a05_lin]` 老林 (`boss_lin`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 咱们跑外贸的看一个地方能不能长红，不听口号有多响，就看你在院里种下果树，半夜怕不怕被人连根端走！

- 🎙️ **`[wn_a06_wei]` 魏老先生 (`historian_wei`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 沈教授别把功劳全记在制度账上！赤道湿热疫病横行、温带良港舟楫便利，山川水土和千年习俗，岂能轻言无关？

- 🎙️ **`[wn_a07_lord]` 特许大臣 (`lord_monopoly`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [coldly] [condescending] 蛋糕做得再大，要是切蛋糕的刀子落进新商人手里，王座都要晃三晃。与其求变，不如牢牢攥紧眼下这口铁锅。

- 🎙️ **`[wn_a08_william]` 威廉 (`inventor_william`)** （`stability=0.5` | 句后气口 `0.2s`）  
  > [angry] [sighs] 我熬了三年油灯造出这台快过十双手的织袜机，可宫廷嫌它砸了老行会饭碗、怕惹乱子，连张专利纸都不肯批！

- 🎙️ **`[wn_a09_elena]` 埃琳娜 (`merchant_elena`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [warmly] 当年在威尼斯码头，没金币也能签份出海合伙契约闯地中海；可贵族一夜锁死名册，海上明珠也就悄悄停摆了。

- 🎙️ **`[wn_a10_su]` 苏晚舟 (`host_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《国运的开关》——告别晦涩翻译腔，用八位人物穿越五百年风云，听懂大国兴衰与普通人选择的底层制度密码。
