# AUDITION_MONTE_CRISTO ·《《基督山伯爵·伊夫堡复仇广播剧》核心声线与复仇名场面试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 伊夫堡复仇核心试听 | `Razor-sharp aristocratic Parisian gothic suspense score, driving minor-key cello ostinato, icy dramatic chamber strings, dark harpsichord and restrained orchestral timpani pulse of calculating vengeance, purely instrumental film score, no modern synth trap, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 伊夫堡复仇核心试听】

- 🔊 **`[ma01_bell]` 音效 · 独立顺播**（复用母题 `marseille_harbor_bell`） （时长 `3.2s` | 句后留白 `0.22s`）  
  Prompt: `Bright sunlit Mediterranean harbor waves lapping against wooden piers, distant seagulls calling, taut wooden sailing ship rigging creaking and a crisp brass ship bell ringing twice, pure foley, no human voice`  
  *导演备注：马赛港法老号归航开篇*

- 🎙️ **`[ma02_narr]` 史诗旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [solemn] 一八一五年二月二十四日，法老号满帆驶入马赛港。谁也没想到，一封藏在酒杯背后的黑信，会把十九岁的大副拖进十四年暗无天日的海中孤牢。

- 🔊 **`[ma03_iron]` 音效 · 叠加下一句起拍**（复用母题 `chateau_dif_iron_door`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Heavy medieval stone dungeon iron-bound prison door slamming shut with echoing metallic latch clank and thick rusted iron key turning inside a massive lock over cold distant sea wind, pure foley, no human voice`

- 🎙️ **`[ma04_dantes]` 青年爱德蒙·唐泰斯 (`dantes_young`)** （`stability=0.0` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [desperately] [shouting] 维尔福先生！今天是我和梅尔塞苔丝的订婚日！我连那封信里写了什么都不知道——你们凭什么把我活埋在伊夫堡！

- 🎙️ **`[ma05_villefort]` 热拉尔·德·维尔福 (`villefort`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [coldly] [dismissive] 唐泰斯，你确实无罪。可你手里的信偏偏写着我父亲的名字。为了我的前程，这封信必须化作灰烬，而你必须永远消失。

- 🔊 **`[ma06_tap]` 音效 · 独立顺播**（复用母题 `faria_wall_tap`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Tense dead silence inside a damp stone dungeon broken by three deliberate muffled metallic scraping taps coming from deep inside a thick limestone wall followed by tiny falling gravel dust, pure foley, no human voice`

- 🎙️ **`[ma07_faria]` 法利亚神父 (`abbe_faria`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.26s`）  
  > [whispers] [warmly] 别哭，孩子。仇恨若不装进智慧的剑鞘，只会先割伤你自己。贴近石墙，我把学识、真相与基督山岛的千年宝藏全都交给你。

- 🔊 **`[ma08_paris]` 音效 · 独立顺播**（复用母题 `paris_salon_clock_glass`） （时长 `2.6s` | 句后留白 `0.22s`）  
  Prompt: `Refined 19th-century Parisian aristocratic salon ambience with antique gilded mantel clock ticking softly and two fine crystal champagne glasses clinking delicately beside crackling hearth fire, pure foley, no human voice`

- 🎙️ **`[ma09_count]` 基督山伯爵 (`monte_cristo`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [calmly] [coldly] 各位巴黎的贵客，不必惊慌。我不过是替上帝来结一笔迟到了二十三年的旧账——恩情加倍偿还，罪孽分毫不差。

- 🎙️ **`[ma10_mercedes]` 梅尔塞苔丝 (`mercedes`)** （`stability=0.0` | 句后气口 `0.28s`）  
  > [crying] [trembling] 伯爵……不，爱德蒙！这世上纵然所有人都忘了你的声音，我听第一句就知道是你——求你饶过我的孩子！

- 🎙️ **`[ma11_count_end]` 基督山伯爵 (`monte_cristo`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [softly] [solemn] 在上帝揭晓未来之前，人类全部的智慧，都包含在这五个字里——等待，和希望。
