# AUDITION_FREAK ·《《激励侦探局：〈魔鬼经济学〉隐秘动机剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 激励侦探局八角色核心试听 | `Curious playful modern detective-economics chamber score, nimble pizzicato violin and cello strings, light wooden marimba pulse, warm walking upright double bass and crisp felt piano accents evoking a clever investigative studio full of clues and aha moments, purely acoustic instrumental, no loud rock drums, no singing, no vocals, no Chinese instruments` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 激励侦探局八角色核心试听】

- 🔊 **`[fk_a01_pin]` 音效 · 独立顺播**（复用母题 `detective_whiteboard_pin`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Crisp close-up foley of corkboard pins pressing firmly into a wooden evidence board, dry-erase marker circling a clue on glass whiteboard, and a brass magnifying glass set cleanly onto an oak desk, pure foley, no human voice`

- 🎙️ **`[fk_a02_narr]` 悬疑侦探旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [calmly] 梧桐巷二楼灯火通明。这间专查隐秘动机的侦探局不找凶器，只翻账本——因为每一桩反常奇案背后，都藏着一只看不见的激励之手。

- 🎙️ **`[fk_a03_lu]` 陆寻 (`detective_lu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 别人破案查指纹脚印，咱们激励侦探局只抓一条硬线索：别听他们嘴上口号喊多响，先算算账本底下究竟谁掏钱、谁得利。

- 🔊 **`[fk_a04_bell]` 音效 · 叠加下一句起拍**（复用母题 `kindergarten_bell_gate`） （时长 `2.8s` | 句后留白 `0.18s`）  
  Prompt: `Gentle evening kindergarten iron gate latch clicking open, a bright reception desk bell tapping once, and a crisp electronic attendance chime in a quiet tiled lobby, pure foley, no human voice`

- 🎙️ **`[fk_a05_lin]` 林园长 (`principal_lin`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 我定下迟到罚款明明是一片好心，想让值班老师早点下班；谁料新规挂出去才两周，晚来接孩子的家长反倒硬生生翻了一倍！

- 🎙️ **`[fk_a06_zhao]` 赵姐 (`mom_zhao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [sighs] [wryly] 以前不罚钱我晚来十分钟脸都臊红了；现在标价三十块，那叫划算的晚托服务费，我花钱买单，心里可踏实多了！

- 🎙️ **`[fk_a07_zhou]` 周经理 (`agent_zhou`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [wryly] 赵姐，您这套房子早点落袋为安才是高明！至于我卖自家那套为何多等了十天，那可都是给您攒出来的行情经验呀。

- 🎙️ **`[fk_a08_hao]` 小浩 (`young_hao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [excited] 陆哥你快看大屏！三万条公开成交记录一跑完，中介卖自家房平均多挂十天、多卖三个点，这组数学指纹赖都赖不掉！

- 🎙️ **`[fk_a09_wang]` 老王 (`boss_wang`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 我开二十年铺子早看透了！赏钱若发歪了地方，你出十块钱收耗子尾巴，明天整条街都有人在家拿米养耗子！

- 🎙️ **`[fk_a10_su]` 苏小满 (`host_su`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《激励侦探局》——卸掉晦涩翻译腔，用六宗烧脑又爆笑的现代生活悬案，带你看穿藏在日常背后的隐秘动机！
