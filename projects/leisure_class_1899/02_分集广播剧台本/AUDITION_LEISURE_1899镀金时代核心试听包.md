# AUDITION_LEISURE ·《《1899镀金时代：〈有闲阶级论〉奢侈消费剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1899第五大道镀金舞厅核心试听 | `Witty ironic 1899 Gilded Age New York salon waltz for chamber strings, playful solo violin, crisp parlor grand piano arpeggios and nimble pizzicato cello evoking ostentatious Fifth Avenue champagne galas, purely acoustic classical instrumental, no modern drums, no synth, no Chinese instruments, no singing, no vocals` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1899第五大道镀金舞厅核心试听】

- 🔊 **`[la01_ballroom]` 音效 · 独立顺播**（复用母题 `gilded_champagne_ballroom`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Opulent 1899 New York Fifth Avenue gilded marble ballroom ambience with a crisp champagne cork pop, effervescent pouring, delicate crystal flutes clinking together, and light satin heels stepping across polished parquet, pure foley, no human voice`

- 🎙️ **`[la02_narr]` 历史讽刺旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [wryly] 一八九九年，纽约第五大道的镀金吊灯彻夜长明。芝加哥书房里，一位穿着旧裤子的怪才学者，正准备掀翻全天下奢侈炫耀的老底。

- 🎙️ **`[la03_mrs]` 斯特林夫人 (`mrs_sterling`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [sarcastic] 机器压的纯银勺滑溜溜的，一看就像便宜货！晚宴不摆十倍价的手工锤纹银勺，明天名媛圈还不笑掉大牙？

- 🔊 **`[la04_spoon]` 音效 · 叠加下一句起拍**（复用母题 `silver_spoon_workshop`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Crisp intimate 1899 silversmith workshop foley with rhythmic light metal planishing hammer taps shaping a solid silver spoon on a small iron stake, gentle fine file brushing, and finished silver placed cleanly onto a warm oak bench, pure foley, no human voice`

- 🎙️ **`[la05_tom]` 老工匠托马斯 (`craftsman_tom`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 机器勺喝汤不刮嘴才两美元，我故意敲歪几锤卖二十美元，结果阔太太全抢歪的——合着她们买的是我的锤子印！

- 🎙️ **`[la06_tycoon]` 斯特林爵士 (`tycoon_sterling`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [condescending] 在第五大道谈性价比简直荒唐！香槟喝最贵的，草坪绝不放奶牛，排场撑不起来，谁信我修得起跨洲铁路？

- 🎙️ **`[la07_edward]` 爱德华 (`young_edward`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.2s`）  
  > [sighs] 我死背了六年没人说的拉丁语，脖子还被硬白领磨破皮——合着我家花大钱，就为证明我啥实用活都不会干？

- 🎙️ **`[la08_clara]` 克拉拉 (`clara`)** （`stability=0.5` | 句后气口 `0.2s`）  
  > [sighs] 我上个月午饭顿顿啃黑面包省菜钱，却咬牙买双磨脚的新款高跟鞋，就怕进办公室被同事瞧不起！

- 🎙️ **`[la09_bai]` 白清浅 (`host_bai`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 凡勃伦教授，一百多年过去，为什么限量奢侈包越涨价越疯抢、时尚季季劝人扔旧衣？您的消费密码真的一点没过时吗？

- 🎙️ **`[la10_veblen]` 索尔斯坦·凡勃伦 (`veblen`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.55s`）  
  > [wryly] [calmly] 欢迎走进《1899镀金时代》。卸掉绕口翻译腔，咱们今晚拿银勺、草坪、束腰和高跟鞋当手术刀，把“炫耀性消费”的底裤扒个干干净净！
