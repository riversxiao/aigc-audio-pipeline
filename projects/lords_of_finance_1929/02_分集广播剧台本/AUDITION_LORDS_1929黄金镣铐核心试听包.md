# AUDITION_LORDS ·《《1929黄金镣铐：〈金融之王〉四央行行长博弈》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 1929黄金镣铐八角色核心试听 | `1929 interwar European tragic chamber orchestra, somber solo cello melody, dark stately grand piano chords and restrained string quartet evoking foggy Threadneedle Street gold vaults and the solemn weight of postwar central banking, purely acoustic instrumental, no modern drums, no percussion, no singing, no vocals` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 1929黄金镣铐八角色核心试听】

- 🔊 **`[la01_vault]` 音效 · 独立顺播**（复用母题 `gold_vault_chains`） （时长 `3.0s` | 句后留白 `0.22s`）  
  Prompt: `Heavy iron Bank of England underground vault door grinding shut in a stone corridor followed by heavy gold bullion bars thudding onto an oak trolley and brass chains clinking solemnly, pure foley, no human voice`  
  *导演备注：金库铁门与金砖锁链定调*

- 🎙️ **`[la02_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 一九一九到一九三三，世界经济的大开关不在总统府，也不在议会厅，而是握在伦敦、纽约、柏林与巴黎四张红木书桌后面。

- 🎙️ **`[la03_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.24s`）  
  > [calmly] 四位性格截然不同的中央银行掌门，手握黄金与印钞机的生死闸门，本想修补战后废墟，却亲手把一个繁华时代推进了大萧条的冰窖。

- 🎙️ **`[la04_norman]` 蒙塔古·诺曼 (`montagu_norman`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [solemn] 伦敦针线街百年招牌，靠的就是纸英镑随时能换回足额真金。要是连大英帝国都向贬值低头，全世界的商业信用就彻底崩盘了！

- 🎙️ **`[la05_moreau]` 埃米尔·莫罗 (`emile_moreau`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [coldly] [wryly] 说得冠冕堂皇，诺曼先生。法国北部城镇被炮火夷为平地，巴黎金库每一块金砖都是拿命换的，凭什么替伦敦的帝国面子掏钱？

- 🎙️ **`[la06_norman]` 蒙塔古·诺曼 (`montagu_norman`)** （`stability=0.0` | 声场 `vast_hall` | 句后气口 `0.2s`）  
  > [angry] 你把半个欧洲的黄金锁进巴黎地窖一动不动，伦敦失血到快窒息，这就是法兰西讲的合作吗？

- 🔊 **`[la07_press]` 音效 · 叠加下一句起拍**（复用母题 `weimar_printing_press`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Relentless fast mechanical clatter of a 1923 industrial rotary banknote printing press running at fever pitch with thick freshly cut stacks of paper currency slapping rapidly onto a wooden sorting table, pure foley, no human voice`

- 🎙️ **`[la08_schacht]` 亚尔马·沙赫特 (`hjalmar_schacht`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [coldly] 你们光顾着分黄金，可曾去柏林看过？一万亿旧马克买不到半斤黑面包！稳住纸币靠的不是金砖堆山，是央行敢当面拉断政府的印钞电源！

- 🎙️ **`[la09_strong]` 本杰明·斯特朗 (`benjamin_strong`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [seriously] 诸位先停火！欧洲再往下塌，美国农场主的小麦也得烂在地里。可我给纽约降息去拉伦敦一把，华尔街那群炒股狂徒转眼就能点着冲天大火！

- 🎙️ **`[la10_strong]` 本杰明·斯特朗 (`benjamin_strong`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.24s`）  
  > [sighs] 拧松水龙头怕烧起泡沫，拧紧水龙头又怕冻死工厂，全世界的钱袋子就悬在咱们这一念之间。

- 🎙️ **`[la11_keynes]` 凯恩斯 (`john_keynes`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [wryly] [seriously] 四位大人把黄金供上神坛，说它能防着政客乱印钱。可这把尺子早就冻锈卡死了，你们硬把千万活生生的工人和工厂，锁上黄金镣铐活活窒息！

- 🎙️ **`[la11b_schacht]` 亚尔马·沙赫特 (`hjalmar_schacht`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [coldly] 凯恩斯教授坐在剑桥喝茶自然轻松！可一旦放任纸币脱缰，中产阶级毕生积蓄一夜清零，那份街头怒火会把整个欧洲烧成灰烬！

- 🎙️ **`[la11c_keynes]` 凯恩斯 (`john_keynes`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [seriously] [pushback] 所以为了防止着火，你们就干脆把整座屋子锁进零下三十度的冰窖，活活冻死里面所有人？大萧条不是天灾，是你们亲手拧死的阀门！

- 🔊 **`[la12_grille]` 音效 · 独立顺播**（复用母题 `bank_run_iron_grille`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Echoing hurried footsteps across a grand marble banking hall abruptly halted by a heavy wrought-iron teller grille sliding violently shut and brass bolts locking into place, pure foley, no human voice`  
  *导演备注：挤兑铁栅门猛然关闭*

- 🎙️ **`[la13_hans]` 老汉斯 (`baker_hans`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [sighs] 你们这些大行长吵来吵去，挨耳光的总是咱们小铺子！前几年我推着独轮车装满百万马克买不到面粉，如今面粉便宜一半，满街却没人掏得出铜板！

- 🎙️ **`[la14_shen]` 沈明薇 (`correspondent_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [curious] 同样是一张纸钞，为什么一九二三年在柏林能一夜变成烧火废纸，一九三一年在欧美又突然紧缺到冻死半个地球？

- 🎙️ **`[la15_narr]` 历史旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [solemn] 从凡尔赛天价赔款、魏玛印钞狂潮、伦敦英镑枷锁，到长岛秘密降息与华尔街股灾崩盘，谁先砸碎黄金镣铐，谁就最早走出深渊。

- 🎙️ **`[la16_shen]` 沈明薇 (`correspondent_shen`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 答案全藏在伦敦、柏林、巴黎与纽约四座金库的生死角力里。欢迎走进《一九二九黄金镣铐》，八角色零翻译腔，带你听懂百年货币真相！
