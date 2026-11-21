# AUDITION_HAYEK ·《《1944剑桥夜话：〈通往奴役之路〉思想剧场》六角色试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1944剑桥夜话试听 | `Warm poignant 1944 British historical drama chamber score, restrained solo cello melody, soft muted upright felt piano chords and gentle string quartet sustain in a quiet rain-washed Cambridge college study, thoughtful intellectual gravity, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1944剑桥夜话试听】

- 🔊 **`[ha01_rain]` 音效 · 独立顺播**（复用母题 `cambridge_fireplace_rain`） （时长 `3.2s` | 句后留白 `0.25s`）  
  Prompt: `Cozy subtle wood fireplace crackle inside a quiet vintage wooden university study while soft steady evening rain taps gently against leaded glass windows, distant muted college clock chime, pure foley, no human voice`  
  *导演备注：1944剑桥雨夜壁炉入戏*

- 🎙️ **`[ha02_narrator]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [solemn] 一九四四年三月，二战炮火还没停息。在剑桥大学一间拉着遮光帘的书房里，一场关乎普通人饭碗、自由与秩序的深夜辩论，正在红茶热气里展开。

- 🎙️ **`[ha03_shen]` 沈明微 (`reporter_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 哈耶克教授，您这本小册子刚在伦敦上架就被抢空了，可普通人一听书名就发懵——战后大家只想过上安稳、公平的日子，由国家统一安排生产，错在哪儿了？

- 🎙️ **`[ha04_lin]` 林致远 (`student_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [pushback] 是啊教授！大萧条把那么多工厂整倒闭了，如果我们请最聪明的科学家把全国的粮食、煤炭和学校统筹规划好，难道不比市场乱糟糟地撞大运更高效？

- 🎙️ **`[ha05_hayek]` 哈耶克 (`hayek`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [calmly] 致远，打个最简单的比方。法律就像马路上的红绿灯，它规定大家靠哪边走、红灯停绿灯行；可如果有一天，交警不但管红绿灯，还非要替你决定今天几点出门、必须去哪家馆子吃面——那就不再是秩序，而是替你活着。

- 🎙️ **`[ha06_chen]` 老陈 (`shopkeeper_chen`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [earthy] [chuckles] 哎哟，教授这比方一下说到我心坎里去了！我街口那家小杂货铺，哪天谁捏着全镇的面粉批条，我就算本事再大，也得天天弯腰看人脸色过活！

- 🔊 **`[ha07_teacup]` 音效 · 独立顺播**（复用母题 `porcelain_teacup_study`） （时长 `2.2s` | 句后留白 `0.2s`）  
  Prompt: `Hot tea pouring briefly into a delicate bone china teacup followed by the cup settling softly onto its saucer on a mahogany table in a quiet room, pure foley, no human voice`

- 🎙️ **`[ha08_keynes]` 凯恩斯 (`keynes`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.5s`）  
  > [warmly] [seriously] 弗里茨，你的担忧我感同身受。可眼下千万人失业、满街工厂熄火，难道政府能袖手旁观？真问题从来不是要不要画线，而是——这条线，究竟该画在哪儿。
