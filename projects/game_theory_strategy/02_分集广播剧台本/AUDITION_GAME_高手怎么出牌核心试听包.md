# AUDITION_GAME ·《《高手怎么出牌：〈策略思维与博弈论〉商业剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 高手怎么出牌八角色核心试听 | `Clever crisp minimalist chamber strings, nimble rhythmic pizzicato cello, sharp staccato felt piano and light upright bass evoking a refined modern strategy tea-room and the first calculated move on a wooden Go board, purely acoustic instrumental, no heavy pop drums, no percussion, no singing, no vocals` | 65s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 高手怎么出牌八角色核心试听】

- 🔊 **`[ga01_printer]` 音效 · 独立顺播**（复用母题 `tea_shop_receipt_printer`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Brisk modern beverage shop thermal receipt printer whirring and tearing off a paper order slip rapidly followed by a crisp plastic cup lid snapping shut and ice cubes clinking, pure foley, no human voice`

- 🎙️ **`[ga02_narr]` 剧场旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [calmly] 春风商业街的早高峰，两家对门奶茶店又杀红了眼。一边挂出买一送一，一边半小时内干到九块九。商海从不是闷头算死账的考场，而是你落一子、对手立刻变招的活棋盘。

- 🎙️ **`[ga03_ma]` 马大川 (`boss_ma`)** （`stability=0.0` | 句后气口 `0.2s`）  
  > [earthy] [angry] 顾教授您评评理！对门姓陈的小子天不亮就拉补贴横幅，我要是不跟着跳楼大甩卖，门口老主顾全得跑光！明知道降价会亏钱，可谁敢先当傻子？

- 🎙️ **`[ga04_chen]` 陈锐 (`chen_ruo`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [excited] 马老板，商场如战场，天下武功唯快不破！地铁口黄金旺铺就这一间，谁先砸钱抢位、谁先圈住流量，谁就锁死整条街的江山！

- 🔊 **`[ga05_go]` 音效 · 叠加下一句起拍**（复用母题 `go_stone_snap`） （时长 `2.6s` | 句后留白 `0.18s`）  
  Prompt: `Close-up crisp foley of a polished slate Go stone snapping firmly onto a resonant wooden goban board followed by glass stones shifting lightly inside a lidded cedar bowl, pure foley, no human voice`

- 🎙️ **`[ga06_gu]` 顾行之 (`prof_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] [wryly] 有意思就在于此。你们俩都是精明人，人人都在算自己眼前的最优解，可凑到一块儿，怎么反倒携手跳进了谁都亏光的最差结局？

- 🎙️ **`[ga07_gu2]` 顾行之 (`prof_gu`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [calmly] 真正的高手出牌，从不只盯着眼前的牌面。他们先站在结局往回倒推三步，再看清对手的底牌、退路与软肋，用规则逼着对方按自己的剧本走。

- 🎙️ **`[ga08_zhou]` 周振霆 (`ceo_zhou`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [coldly] [wryly] 两条街的小铺子还敢谈规则？下周一我就派快闪车停在你们门口免费赠饮！门口那块买贵双倍补差价的招牌，你们真以为是做慈善？那是封死全街价格的铁锁！

- 🎙️ **`[ga09_lin]` 林书瑶 (`lin_shuyao`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [seriously] 周董，您下季度要冲刺上市财报审计，根本烧不起无底洞。嘴上放狠话没人信，可我们六家商户刚签下三年不可退订的直采铁契——自断退路的破釜沉舟，您还敢赌吗？

- 🎙️ **`[ga09b_zhou]` 周振霆 (`ceo_zhou`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [sighs] [wryly] 好一个把方向盘卸下来扔出窗外！跟一群连退路都焊死的硬骨头拼刺刀，我算完倒推账，确实划不来。

- 🔊 **`[ga10_gavel]` 音效 · 独立顺播**（复用母题 `auction_gavel_strike`） （时长 `2.8s` | 句后留白 `0.2s`）  
  Prompt: `Spacious refined auction hall acoustics with numbered cardboard paddles lifting through quiet air followed by three crisp resonant mahogany gavel strikes echoing softly on a wooden sounding block, pure foley, no human voice`

- 🎙️ **`[ga11_shen]` 沈青黛 (`shen_qing`)** （`stability=0.5` | 声场 `vast_hall` | 句后气口 `0.22s`）  
  > [calmly] [wryly] 拍卖大厅里，举起最高号牌满面红光的人别急着开香槟。赢家诅咒告诉我们，出价最高的人，往往只是全场估得最盲目乐观的冤大头。

- 🎙️ **`[ga12_xu]` 许老伯 (`master_xu`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [warmly] [chuckles] 景区门口坑你一回，是算准你这辈子只路过一次；咱老巷子三十年街坊生意没人赖账，靠的从来不是谁更高尚，而是明天还得抬头见的长久局。

- 🎙️ **`[ga12b_ma]` 马大川 (`boss_ma`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [warmly] 嘿，听完顾教授这六堂实战棋局，我算彻底开了窍：商海里最狠的不是嗓门大、降价狠，而是看透对手算盘、把你死我活拆成共赢大蛋糕！

- 🎙️ **`[ga13_lin2]` 林书瑶 (`lin_shuyao`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 囚徒困境、倒推法、破釜沉舟、买贵补差锁价、赢家诅咒到重复博弈——彻底告别晦涩公式与翻译腔，用最鲜活的中国商战烟火气听懂策略思维底层密码。

- 🎙️ **`[ga14_narr2]` 剧场旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.55s`）  
  > [warmly] 《高手怎么出牌：〈策略思维与博弈论〉商业剧》第一季六集连播，八位高手齐聚春风街与谈判桌，现在落子开局。
