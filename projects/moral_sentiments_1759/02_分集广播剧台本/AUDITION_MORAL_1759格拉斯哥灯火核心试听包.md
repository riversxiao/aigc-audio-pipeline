# AUDITION_MORAL ·《《1759格拉斯哥灯火：〈道德情操论〉商业温度》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1759格拉斯哥烛光试听 | `Warm intimate 1759 Scottish Enlightenment baroque chamber music, lyrical expressive solo cello, soft glowing chamber strings and gentle wooden flute evoking candlelit Glasgow warmth and human empathy, purely acoustic instrumental, no drums, no modern beat, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1759格拉斯哥烛光试听】

- 🔊 **`[ms00_study]` 音效 · 独立顺播**（复用母题 `glasgow_rainy_candle_study`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Warm cozy 1759 Glasgow stone study ambience with soft evening rain pattering on leaded glass windows, gentle hearth fire crackling, a porcelain teacup resting on an oak table, and a quill pen lightly scratching thick rag paper, pure foley, no human voice`

- 🎙️ **`[ms00_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一七五九年春，格拉斯哥暮雨微凉。一盏黄铜烛火照亮三十六岁年轻教授的书稿，也照见商业世界最深处的人间温度。

- 🎙️ **`[ms00_su]` 苏清禾 (`host_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 斯密教授，人人都以为《国富论》只讲冷冰冰的自利算账，怎么十七年前您先写下的，却是这么温柔通透的《道德情操论》？

- 🎙️ **`[ms00_smith]` 亚当·斯密 (`adam_smith`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] [calmly] 因为无论人显得多自私，骨子里总有一根软弦，看见陌生人在高空走钢丝摇晃，自己也会跟着歪身子、暗暗攥出一把冷汗。

- 🔊 **`[ms00_plane]` 音效 · 叠加下一句起拍**（复用母题 `carpenter_workshop_plane`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Warm 18th-century Scottish carpenter workshop foley with a wooden hand plane crisply shaving fragrant pine wood curls, steady soft wooden mallet taps fitting a tight mortise joint, and wood shavings brushing off an oak bench, pure foley, no human voice`

- 🎙️ **`[ms00_mac]` 老麦克 (`carpenter_mac`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [warmly] 咱木匠最懂这理儿！坑街坊一把能多赚几个铜板，可名声臭了以后连根木钉都没人买，信任底线才是手艺人的命根子！

- 🎙️ **`[ms00_craven]` 克雷文勋爵 (`lord_craven`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [condescending] 笑话！满大街的人眼里只认镶金马车和显赫头衔，谁有闲工夫关心一个穷木匠心里住着什么公正旁观者？

- 🎙️ **`[ms00_andrew]` 安德鲁 (`student_andrew`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [seriously] 我衣袖虽打着补丁，可宁愿靠真本事一步一个脚印站稳脚跟，也绝不为了坐上您的镶金马车去低头拍权贵的马屁！

- 🎙️ **`[ms00_margaret]` 玛格丽特 (`mrs_margaret`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] [softly] 日子过到最后大伙儿都明白，人求的哪是什么虚头巴脑的热闹，不过是心里踏实，真真切切配得上被人惦记、被人打心底喜爱。

- 🎙️ **`[ms00_hume]` 大卫·休谟 (`david_hume`)** （`stability=0.5` | 句后气口 `0.55s`）  
  > [chuckles] [warmly] 欢迎走进《1759格拉斯哥灯火》——彻底卸掉晦涩翻译腔，听八位鲜活角色用大白话把亚当·斯密的商业温度与良知智慧讲透！
