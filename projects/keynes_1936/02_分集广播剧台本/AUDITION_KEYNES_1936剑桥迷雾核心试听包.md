# AUDITION_KEYNES ·《《1936剑桥迷雾：〈就业、利息和货币通论〉宏观思想剧场》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1936剑桥迷雾八角试听 | `Atmospheric 1936 interwar Cambridge chamber music, deep reflective solo cello, warm muted felt upright piano arpeggios and intimate English string quartet evoking misty college courtyards and fireside reflection, purely acoustic instrumental, no drums, no modern beat, no synth, no singing, no vocals` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1936剑桥迷雾八角试听】

- 🔊 **`[ka01_rain]` 音效 · 独立顺播**（复用母题 `cambridge_study_rain`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Cozy 1936 Cambridge university study ambience with steady cold winter rain tapping leaded glass windows, soft crackling coal fireplace hearth, and thick rag-paper book pages turning gently on an oak desk, pure foley, no human voice`

- 🎙️ **`[ka02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 一九三六年二月，剑桥冬雾漫过国王学院的石头窗棂。外面是大萧条冻僵的工厂与绵延的失业长队，屋里一本奇书即将改写现代世界的经济常识。

- 🔊 **`[ka03_loom]` 音效 · 叠加下一句起拍**（复用母题 `textile_mill_halt`） （时长 `3.2s` | 句后留白 `0.18s`）  
  Prompt: `1930s Manchester brick cotton textile mill power looms slowing down with metallic belt squeal to an eerie halt, followed by a heavy iron factory gate clanging shut and padlock snapping in a quiet rainy yard, pure foley, no human voice`

- 🎙️ **`[ka04_jack]` 杰克 (`worker_jack`)** （`stability=0.0` | 句后气口 `0.22s`）  
  > [angry] 教授别坐在剑桥暖炉边猜我们偷懒！我干了八年细纱机，降两成工钱我都肯干，可整条街的厂门全用大铁链锁着！

- 🎙️ **`[ka05_pigou]` 庇古教授 (`classical_prof`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 梅纳德，节俭攒钱与降薪出清是百年正统铁律！只要熬过眼下短期阵痛，市场从长期来看自然会恢复平衡！

- 🎙️ **`[ka06_keynes]` 约翰·梅纳德·凯恩斯 (`keynes`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.24s`）  
  > [wryly] [seriously] 阿瑟，长期来看，咱们所有人都已经死了！暴风雨里水手要的是别翻船，不是听你念叨风停之后海面自然会平！

- 🎙️ **`[ka07_lydia]` 莉迪亚 (`lydia_keynes`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [chuckles] [wryly] 梅纳德，快收起你那堆“边际消费倾向”和“流动性偏好”的黑话吧！说人话，不就是多挣十镑舍得拿出几镑买菜嘛！

- 🎙️ **`[ka08_burton]` 老伯顿 (`factory_owner`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [sighs] 银行把利息砍到贴地板有啥用？大街上没人买新衬衫，我仓库里的上等棉布堆到房梁上，白借钱我也不敢买新机器！

- 🎙️ **`[ka09_harris]` 哈里斯 (`broker_harris`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [sarcastic] [chuckles] 进交易所还研究工厂十年真实价值？股市本来就是一场报纸选美比赛，全看谁先猜中明天大伙儿疯抢哪张股票！

- 🎙️ **`[ka10_ye]` 叶知秋 (`host_ye`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《1936剑桥迷雾》——告别晦涩翻译腔，八位鲜活角色现场飙戏，带您用最透亮的中国话听懂凯恩斯《通论》！
