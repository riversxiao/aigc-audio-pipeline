# AUDITION_BASIC ·《《零公式常识课：〈常识经济学〉街头案例剧》核心试听包》广播剧 / 多人精品有声剧演出台本

- **模式**：`audition_pack`
- **对应章节**：第 0 章（源文件：`N/A`）
- **时间轴规则**：自然语速完整保留（片头留白 `0.35s`，片尾收束 `1.0s`，严禁按旧时长裁尾）
- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）

## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）

| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |
| :--- | :--- | :--- | :---: | :---: |
| `audition` | 零公式常识课八角色核心试听 | `Grounded warm street-documentary acoustic chamber score, nimble warm felt piano chords, buoyant plucked upright double bass, light acoustic guitar arpeggios and gentle pizzicato cello evoking an awakening neighborhood produce market and bustling everyday trade, purely acoustic instrumental, no loud drums, no percussion, no vocals, no singing, no Chinese instruments` | 60s | `0.11` / `0.34` |

## 二、 逐句演出与音效时间轴清单

### 【audition · 零公式常识课八角色核心试听】

- 🔊 **`[ba01_market]` 音效 · 独立顺播**（复用母题 `morning_produce_scale`） （时长 `2.8s` | 句后留白 `0.22s`）  
  Prompt: `Crisp early-morning neighborhood produce market foley with fresh leafy vegetables rustling into a thin shopping bag, a digital market scale beeping softly, and coins clinking into a metal cash tray, pure foley, no human voice`

- 🎙️ **`[ba02_narr]` 节目旁白 (`narrator`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [warmly] 告别公式曲线和催眠术语！走进海洲早市、台风夜便利店与街角茶铺，六堂零公式案例剧，带你用常识看穿物价与选择的真相。

- 🔊 **`[ba03_tea]` 音效 · 叠加下一句起拍**（复用母题 `porch_tea_ledger`） （时长 `3.0s` | 句后留白 `0.18s`）  
  Prompt: `Intimate evening tea porch ambience with warm hot tea pouring steadily from a ceramic pot into small cups, porcelain saucers clinking lightly, and crisp paper ledger pages turning in a calm breeze, pure foley, no human voice`

- 🎙️ **`[ba04_tang]` 唐致远 (`prof_tang`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [warmly] 经济学压根不是算不完的公式，就是过日子的明白账：东西有限、用处太多，谁替全城悄悄管库存？就是街上涨落的价签。

- 🎙️ **`[ba05_he]` 老何 (`boss_he`)** （`stability=0.0` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [earthy] [chuckles] 谁不想卖便宜菜挣好名声？可半夜暴雨三百公里调车，油费摆在那儿，按死价签，明天全城货架就得唱空城计！

- 🎙️ **`[ba06_song]` 宋处长 (`official_song`)** （`stability=0.5` | 声场 `vintage_study` | 句后气口 `0.22s`）  
  > [seriously] 老唐，账不能只按生意人的算盘打。要是救命菜价、房租封顶和老厂饭碗都撒手不管，全交给价签，普通百姓谁来护？

- 🎙️ **`[ba07_wu]` 老吴 (`farmer_wu`)** （`stability=0.5` | 句后气口 `0.22s`）  
  > [sighs] [calmly] 保底高价那年全县改种番茄，冷库塞炸烂果堆成山；寒潮一挂限价红牌，运菜赔油钱，菜车干脆绕城走了。

- 🎙️ **`[ba08_zhou]` 小周 (`young_zhou`)** （`stability=0.5` | 句后气口 `0.2s`）  
  > [curious] 我淋雨跑外卖十二小时，凭啥专家工资是我十倍？还有那片限租老楼，租金数字真降了，我咋连间不漏雨的单间都租不到？

- 🎙️ **`[ba09_lin]` 林医生 (`doctor_lin`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.22s`）  
  > [calmly] 我打字整理病历比助理快一倍，可我还是花钱雇她——省下五十块人工，我就白丢了一小时救治六位急诊病人的时间。

- 🎙️ **`[ba10_xia]` 夏宁 (`host_xia`)** （`stability=0.5` | 声场 `studio_warm` | 句后气口 `0.55s`）  
  > [warmly] 欢迎走进《零公式常识课：〈常识经济学〉街头案例剧》——不画曲线、不掉书袋，用街坊身边的真故事，练出看穿经济忽悠的火眼金睛！
