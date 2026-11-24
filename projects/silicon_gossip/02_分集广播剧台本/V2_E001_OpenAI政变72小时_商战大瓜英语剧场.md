# V2_E001 ·《第 1 集（V2.1精修版）：OpenAI 政变 72 小时——一条 15 分钟视频会，怎么差点拆了全球最贵 AI 巨头？》中英双语深度圆桌播客演出台本

- **模式**：`podcast_roundtable`
- **对应章节**：第 1 期（原典档案：`OpenAI_Nov2023_Coup_72h_Real_Business_Drama`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.2s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声圆桌主轨（`-16 LUFS`，含巴菲特英文原声前 `3.5s` 独奏 → 余弦压混至 `0.15` 同传垫底） + 前景独立声效母题轨（不随对白闪避） + 分幕纯器乐床（ACE-Step 1.5 XL，对白下极轻垫底）

## 一、 分幕配乐设计（ACE-Step 1.5 XL · 纯器乐纪录片书房声场）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `act1_hook` | 冷开场：15 分钟视频会被自己公司开除 | `Upbeat witty modern Silicon Valley caper underscore like The Big Short and Ocean's Eleven, crisp plucked pizzicato strings, nimble acoustic upright bass groove, light brushed snare pulse, energetic intriguing storytelling rhythm, strictly instrumental, no vocals, no singing, no dark funeral drone` | 50s | `0.07` / `0.22` |
| `act2_coup` | 第一幕：周五中午鸿门宴（学会 candid） | `` | 10s | `0.0` / `0.0` |
| `act2_scene` | 名场面闪回 ①：Google Meet 开除现场（Ilya vs Sam） | `Taut brisk modern tech thriller pulse like The Social Network, subtle ticking rhythmic synth arpeggio and crisp muted electric bass drive, high-stakes boardroom coup momentum, clean modern production, strictly instrumental, no vocals, no singing, no traditional instruments` | 35s | `0.08` / `0.22` |
| `act2_roast` | 松弛拆台 ①：老外越客气，刀捅得越深 | `` | 10s | `0.0` / `0.0` |
| `act3_scene` | 名场面闪回 ②：微软 CEO 凌晨怒火（学会 blindsided / Not on my watch） | `Taut brisk modern tech thriller pulse like The Social Network, subtle ticking rhythmic synth arpeggio and crisp muted electric bass drive, high-stakes boardroom coup momentum, clean modern production, strictly instrumental, no vocals, no singing, no traditional instruments` | 35s | `0.08` / `0.22` |
| `act3_roast` | 松弛拆台 ②：榜一大哥被偷袭，明天开会怎么体面反杀甩锅 | `` | 10s | `0.0` / `0.0` |
| `act4_scene` | 名场面闪回 ③：700 员工逼宫大反转（学会 leverage / walk away） | `Taut brisk modern tech thriller pulse like The Social Network, subtle ticking rhythmic synth arpeggio and crisp muted electric bass drive, high-stakes boardroom coup momentum, clean modern production, strictly instrumental, no vocals, no singing, no traditional instruments` | 35s | `0.09` / `0.24` |
| `act4_roast` | 终极复盘：谁手里有底牌，谁才有资格说真话 | `` | 10s | `0.0` / `0.0` |
| `act5_card` | 90 秒带走卡：4 句短狠职场英文（对应人物原声 0.85x + 原速跟读） | `Bright crisp modern podcast outro groove, light jazzy Rhodes electric piano chords with clean finger-snap percussion and warm upright bass bounce, upbeat confident urban feel, strictly instrumental, no vocals, no singing` | 65s | `0.05` / `0.2` |

## 二、 逐句演出与音效时间轴清单

### 【act1_hook · 冷开场：15 分钟视频会被自己公司开除】

- 🔊 **`[v2_001]` 音效 · 独立顺播**（复用母题 `gmeet_join_chime`） （时长 `1.6s` | 句后留白 `0.08s`）  
  Prompt: `Crisp clean two-tone modern video conference call join chime followed by a subtle laptop microphone unmute click, pure foley, no human voice`  
  *导演备注：Google Meet 开场音效*

- 🎙️ **`[v2_002]` Ilya Sutskever (`board_ilya`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.12s`）  
  > [coldly] Sam, you haven't been consistently candid.  
  *中文字幕译文：萨姆，你一直不够坦诚。*  
  *导演备注：Ilya 原声开场核爆金句*

- 🔊 **`[v2_003]` 音效 · 独立顺播**（复用母题 `record_scratch_freeze`） （时长 `1.0s` | 句后留白 `0.06s`）  
  Prompt: `Snappy clean modern broadcast transition pop chime with subtle percussive rim click, crisp podcast sting, pure foley, no human voice`  
  *导演备注：叮一声定格切回双主播*

- 🎙️ **`[v2_004]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.03s`）  
  > [conversational] 二零二三年十一月一个周五中午，估值八百六十亿美元的 OpenAI 老板奥特曼，正在拉斯维加斯看赛车，随手点进了一条视频会议链接。

- 🎙️ **`[v2_005]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `-0.04s`）  
  > [conversational] 结果十五分钟后，他被自己亲手创办的公司，当场开除了。

- 🎙️ **`[v2_006]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 等会儿，自己创办的公司还能被自己人踢出群聊？而且刚才那句英文，听着怎么还挺客气的。

- 🎙️ **`[v2_007]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.06s`）  
  > [chuckles] 客气？大周，欧美职场说话，越客气，刀捅得越深。

- 🎙️ **`[v2_008]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.18s`）  
  > [conversational] 欢迎来到《商战大瓜英语局》。今天七分钟，带你扒透硅谷史上最戏剧性的 OpenAI 政变七十二小时，顺手带走四句超短、超狠、明天开会就能直接用的职场英文。

### 【act2_coup · 第一幕：周五中午鸿门宴（学会 candid）】

- 🎙️ **`[v2_009]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 咱先不聊那些复杂股权啊，我就好奇一件事，奥特曼可是带出 ChatGPT 的头号功臣，谁胆子这么大敢开除他？

- 🎙️ **`[v2_010]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.02s`）  
  > [conversational] 这就得说到 OpenAI 那个奇葩架构了。打个比方，你辛辛苦苦开了家全城最火的网红奶茶店，每天排队排到马路对面。

- 🎙️ **`[v2_011]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `-0.04s`）  
  > [conversational] 但你开业那天签了个章程，奶茶店不归你管，归六个不拿分红的居委会大爷管。大爷要是觉得你太爱赚钱、忘了初心，随时可以开个小会让你卷铺盖走人。

- 🎙️ **`[v2_012]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.05s`）  
  > [conversational] 好家伙，这哪是科技巨头，这是给自己请了六个太上皇供在头顶上。然后周五中午真动手了？

- 🎙️ **`[v2_013]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.14s`）  
  > [conversational] 真动手了。周五中午十二点，首席科学家伊利亚给奥特曼发了个视频链接，一上线，镜头对面整整齐齐坐着四位董事，直接宣读结果。

### 【act2_scene · 名场面闪回 ①：Google Meet 开除现场（Ilya vs Sam）】

- 🔊 **`[v2_014]` 音效 · 独立顺播**（复用母题 `gmeet_join_chime`） （时长 `1.6s` | 句后留白 `0.1s`）  
  Prompt: `Crisp clean two-tone modern video conference call join chime followed by a subtle laptop microphone unmute click, pure foley, no human voice`

- 🎙️ **`[v2_015]` Ilya Sutskever (`board_ilya`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.14s`）  
  > [coldly] Sam, you haven't been consistently candid.  
  *中文字幕译文：萨姆，你一直不够坦诚。*

- 🎙️ **`[v2_016]` Ilya Sutskever (`board_ilya`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `-0.06s`）  
  > [icy polite] The board has lost confidence in you.  
  *中文字幕译文：董事会已经对你失去信心。*

- 🎙️ **`[v2_017]` Sam Altman (`sam_altman`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.14s`）  
  > [shocked] Wait—are you firing me right now?  
  *中文字幕译文：等等——你们现在就要开除我？*

- 🎙️ **`[v2_018]` Ilya Sutskever (`board_ilya`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.16s`）  
  > [coldly] Yes. Effective immediately.  
  *中文字幕译文：是的，立刻生效。*

- 🔊 **`[v2_019]` 音效 · 独立顺播**（复用母题 `record_scratch_freeze`） （时长 `1.0s` | 句后留白 `0.06s`）  
  Prompt: `Snappy clean modern broadcast transition pop chime with subtle percussive rim click, crisp podcast sting, pure foley, no human voice`

### 【act2_roast · 松弛拆台 ①：老外越客气，刀捅得越深】

- 🎙️ **`[v2_020]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 鸡皮疙瘩都起来了，一句脏字没带，但字字往心窝子扎。那个 consistently candid 到底是啥意思？

- 🎙️ **`[v2_021]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 这就是咱今天第一句狠话。candid 就是坦诚、直白、不藏着掖着。董事会在公告里写了一句很体面的黑话，说你 haven't been consistently candid，没有一贯保持坦诚。

- 🎙️ **`[v2_022]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [chuckles] 翻译成大白话不就是，你小子满嘴跑火车，当面一套背后一套，今天抓现行了，收拾东西走人吧。

- 🎙️ **`[v2_023]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.03s`）  
  > [conversational] 特别准。而且 candid 这个词平时上班超级好用。以前咱想说“说句实话吧”，总爱说 be honest with me，听着有点像吵架起手式。

- 🎙️ **`[v2_024]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.05s`）  
  > [conversational] 下次开会想直接摊牌，换成三个词：Let's be candid. 咱敞开天窗说亮话，瞬间就有高管气场。

- 🎙️ **`[v2_025]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.05s`）  
  > [conversational] Let's be candid，这句短，好记。行，那奥特曼被踢了，大股东能答应吗？微软不是砸了一百三十亿美元进去吗？

- 🎙️ **`[v2_026]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `-0.04s`）  
  > [conversational] 最离谱的地方就在这儿。微软砸了一百三十亿当最大金主，结果董事会发开除公告前，整整一分钟才给微软 CEO 纳德拉发了条通知。

- 🎙️ **`[v2_027]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.1s`）  
  > [conversational] 提前一分钟？我刷了一百三十亿当榜一大哥，你把头牌主播封号了临开播才告诉我，换谁都得上火。

### 【act3_scene · 名场面闪回 ②：微软 CEO 凌晨怒火（学会 blindsided / Not on my watch）】

- 🔊 **`[v2_028]` 音效 · 独立顺播**（复用母题 `midnight_phone_buzz`） （时长 `2.2s` | 句后留白 `0.08s`）  
  Prompt: `Smartphone vibrating urgently twice on a wooden nightstand in a quiet bedroom followed by a crisp call pickup beep, pure foley, no human voice`  
  *导演备注：凌晨手机狂震*

- 🎙️ **`[v2_029]` Satya Nadella (`satya_nadella`)** （`stability=0.0` | 语言 `en` | 声场 `phone_call` | 句后气口 `0.14s`）  
  > [angry] We were completely blindsided.  
  *中文字幕译文：我们彻底被打了个措手不及。*

- 🎙️ **`[v2_030]` Satya Nadella (`satya_nadella`)** （`stability=0.0` | 语言 `en` | 声场 `phone_call` | 句后气口 `0.14s`）  
  > [blunt] Thirteen billion dollars, and nobody called me?  
  *中文字幕译文：一百三十亿美元，居然没人给我打个电话？*

- 🎙️ **`[v2_031]` OpenAI Exec (`exec_female`)** （`stability=0.0` | 语言 `en` | 声场 `phone_call` | 句后气口 `0.12s`）  
  > [urgent] Satya, the board is refusing to back down.  
  *中文字幕译文：萨提亚，董事会死活不肯让步。*

- 🎙️ **`[v2_032]` Satya Nadella (`satya_nadella`)** （`stability=0.0` | 语言 `en` | 声场 `phone_call` | 句后气口 `0.16s`）  
  > [firmly] Not on my watch. Get Sam on the phone.  
  *中文字幕译文：有我在，休想。马上把萨姆接进来。*

- 🔊 **`[v2_033]` 音效 · 独立顺播**（复用母题 `record_scratch_freeze`） （时长 `1.0s` | 句后留白 `0.06s`）  
  Prompt: `Snappy clean modern broadcast transition pop chime with subtle percussive rim click, crisp podcast sting, pure foley, no human voice`

### 【act3_roast · 松弛拆台 ②：榜一大哥被偷袭，明天开会怎么体面反杀甩锅】

- 🎙️ **`[v2_034]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 纳德拉这火气，隔着电话都能听出来。那个 blindsided，听着像眼睛被蒙住了？

- 🎙️ **`[v2_035]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 很形象。blind 是盲区，side 是侧面。blindsided 本来是橄榄球里从你视野盲区冲过来把你撞翻，放在职场里，就是事先一点风声没透，突然背刺、打你个措手不及。

- 🎙️ **`[v2_036]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 这词太实用了。咱们平时上班最怕啥？隔壁组平时一声不吭，一到大老板周会，突然当众把一个大锅甩你头上。

- 🎙️ **`[v2_037]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.05s`）  
  > [conversational] 对，这时候千万别急眼结巴，稳稳看他一眼说一句：I'm a bit blindsided here. 这事我事先完全没听说。既体面，又当场告诉老板，是他在搞偷袭。

- 🎙️ **`[v2_038]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 这招够稳。那纳德拉后面那句 Not on my watch，翻成咱们的话就是“有我在，门儿都没有”吧？

- 🎙️ **`[v2_039]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 没错，watch 是值班看守的意思。Not on my watch 就是只要我还在岗一天，这种事休想发生。说完这句，纳德拉周日半夜干了件直接写进商学院教材的操作。

- 🎙️ **`[v2_040]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.03s`）  
  > [conversational] 怎么干的，派律师团去告董事会？

- 🎙️ **`[v2_041]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `-0.04s`）  
  > [conversational] 告太慢了。纳德拉直接发推特官宣，奥特曼来微软，专门给你新开个部门，而且你原来公司那七百多号兄弟，谁愿意一起跳槽，微软全盘接收、薪水照旧。

- 🎙️ **`[v2_042]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.05s`）  
  > [chuckles] 这招是真狠，直接端老窝啊。董事会手里留着个空壳公章，活人全让微软打包带走了。

- 🎙️ **`[v2_043]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.12s`）  
  > [conversational] 不到十二个小时，OpenAI 七百七十名员工里，超过七百个人签了联名信，连当初投票开除奥特曼的伊利亚自己都反水签名了。来听这记终极反杀。

### 【act4_scene · 名场面闪回 ③：700 员工逼宫大反转（学会 leverage / walk away）】

- 🔊 **`[v2_044]` 音效 · 独立顺播**（复用母题 `tweet_post_and_buzz`） （时长 `2.4s` | 句后留白 `0.08s`）  
  Prompt: `Fast brisk laptop typing burst ending in a crisp message sent whoosh followed by brief upbeat office applause in a bright modern glass headquarters, pure foley, no human voice`  
  *导演备注：键盘敲击+办公区沸腾*

- 🎙️ **`[v2_045]` OpenAI Exec (`exec_female`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.12s`）  
  > [urgent] Seven hundred people signed. We're backing you, Sam.  
  *中文字幕译文：七百人签了联名信，我们站你这边，萨姆。*

- 🎙️ **`[v2_046]` Sam Altman (`sam_altman`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.18s`）  
  > [firmly] We have the leverage. Step down, or we walk away.  
  *中文字幕译文：底牌在我们手里。你们下台，不然我们全部走人。*

- 🎙️ **`[v2_047]` Ilya Sutskever (`board_ilya`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.16s`）  
  > [sighs] [softly] Fine. Let's talk terms.  
  *中文字幕译文：好吧，我们来谈条件。*

- 🎙️ **`[v2_048]` Sam Altman (`sam_altman`)** （`stability=0.0` | 语言 `en` | 声场 `boardroom` | 句后气口 `0.16s`）  
  > [confident] We're back in business.  
  *中文字幕译文：我们杀回来了。*

- 🔊 **`[v2_049]` 音效 · 独立顺播**（复用母题 `record_scratch_freeze`） （时长 `1.0s` | 句后留白 `0.06s`）  
  Prompt: `Snappy clean modern broadcast transition pop chime with subtle percussive rim click, crisp podcast sting, pure foley, no human voice`

### 【act4_roast · 终极复盘：谁手里有底牌，谁才有资格说真话】

- 🎙️ **`[v2_050]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 短短五天，被开除的老板不仅回来了，还顺手把开除他的董事会全换了一遍。奥特曼刚才那句 We have the leverage 确实硬气。

- 🎙️ **`[v2_051]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 好多人以为 leverage 只是炒股加杠杆，其实欧美职场天天用它指谈判底牌和筹码。七百个顶尖工程师给你撑腰，微软兜底给 offer，这就叫 We have the leverage，底牌全在我手里。

- 🎙️ **`[v2_052]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh-en` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.08s`）  
  > [conversational] 后面那个 walk away 一听就懂，掀桌子走人。说句大实话，不管是谈融资还是普通人跟老板谈涨薪，你得先攒出能随时 walk away 的底气，别人才能坐下来跟你 be candid 说真话。

- 🎙️ **`[v2_053]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.18s`）  
  > [conversational] 咱不贪多，最后花一分钟，让今天这三位大佬各自用自己的原声，把四句最值钱的职场短狠英文慢速一遍、原速一遍带你跟读，明天开会直接用。

### 【act5_card · 90 秒带走卡：4 句短狠职场英文（对应人物原声 0.85x + 原速跟读）】

- 🎙️ **`[v2_054]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `studio_warm` | 语速 `[1.16x]` | 句后气口 `0.18s`）  
  > [conversational] 第一句，伊利亚在开除会上用的词，摊牌说亮话：Let's be candid.

- 🎙️ **`[v2_055]` Ilya Sutskever (`board_ilya`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 语速 `[0.85x]` | 句后气口 `0.45s`）  
  > [measured] Let's be candid.  
  *中文字幕译文：（伊利亚原声 0.85x 慢速）咱敞开说亮话吧。*

- 🎙️ **`[v2_056]` Ilya Sutskever (`board_ilya`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 句后气口 `1.6s`）  
  > [measured] Let's be candid.  
  *中文字幕译文：（伊利亚原声跟读）咱敞开说亮话吧。*

- 🎙️ **`[v2_057]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `studio_warm` | 语速 `[1.16x]` | 句后气口 `0.18s`）  
  > [conversational] 第二句，微软纳德拉被背刺时的原话，打了个措手不及：We were completely blindsided.

- 🎙️ **`[v2_058]` Satya Nadella (`satya_nadella`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 语速 `[0.85x]` | 句后气口 `0.45s`）  
  > [firmly] We were completely blindsided.  
  *中文字幕译文：（纳德拉原声 0.85x 慢速）我们彻底被打了个措手不及。*

- 🎙️ **`[v2_059]` Satya Nadella (`satya_nadella`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 句后气口 `1.6s`）  
  > [firmly] We were completely blindsided.  
  *中文字幕译文：（纳德拉原声跟读）我们彻底被打了个措手不及。*

- 🎙️ **`[v2_060]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `studio_warm` | 语速 `[1.16x]` | 句后气口 `0.18s`）  
  > [conversational] 第三句，还是纳德拉的狠话，有我在休想：Not on my watch.

- 🎙️ **`[v2_061]` Satya Nadella (`satya_nadella`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 语速 `[0.85x]` | 句后气口 `0.45s`）  
  > [firmly] Not on my watch.  
  *中文字幕译文：（纳德拉原声 0.85x 慢速）有我在，休想。*

- 🎙️ **`[v2_062]` Satya Nadella (`satya_nadella`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 句后气口 `1.6s`）  
  > [firmly] Not on my watch.  
  *中文字幕译文：（纳德拉原声跟读）有我在，休想。*

- 🎙️ **`[v2_063]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh-en` | 声场 `studio_warm` | 语速 `[1.16x]` | 句后气口 `0.18s`）  
  > [conversational] 第四句，奥特曼绝地反杀的底气，底牌在我们手里：We have the leverage.

- 🎙️ **`[v2_064]` Sam Altman (`sam_altman`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 语速 `[0.85x]` | 句后气口 `0.45s`）  
  > [firmly] We have the leverage.  
  *中文字幕译文：（奥特曼原声 0.85x 慢速）底牌在我们手里。*

- 🎙️ **`[v2_065]` Sam Altman (`sam_altman`)** （`stability=0.0` | 语言 `en` | 声场 `studio_warm` | 句后气口 `1.6s`）  
  > [firmly] We have the leverage.  
  *中文字幕译文：（奥特曼原声跟读）底牌在我们手里。*

- 🎙️ **`[v2_066]` 大周 (`guest_huaiyuan`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.04s`）  
  > [conversational] 四句全记住了吧。下期大瓜更有意思，二零一八年马斯克睡在工厂地板上，为什么半夜抡起钳子，亲手把花十亿美元买来的全自动产线拆了个稀巴烂？

- 🎙️ **`[v2_067]` 小微 (`host_xiaowei`)** （`stability=0.5` | 语言 `zh` | 声场 `chatroom_table` | 语速 `[1.16x]` | 句后气口 `0.6s`）  
  > [conversational] 下期《马斯克午夜拆厂》，教你用最直接的硅谷英文把老板的蠢需求当场砍掉。点个订阅，咱们下期见。
