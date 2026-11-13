# Playbook · ElevenLabs 中文广播剧配音

把「像专业中文广播剧」的配音、音效和配乐流程从单集成片里抽出来，可复用到其他有声书 / 广播剧 / 短剧对白。

本方法在 2026-11-10 用《九狱剑主》E001《抽骨之夜与黑匣初鸣》对照验证：引擎、中文声优套、自然语速时间轴、ElevenLabs 音效配乐，以及 `eleven_v3` Audio Tags + Creative 稳定性的激烈表演，均已听过并认可。激烈表演的整集重跑先不自动开，等明确叫跑再做。

大媒体与母带不进 Git。

## 一句话

听感差通常不是模型再换一家，而是这四步没做对：

1. 用 `eleven_v3`，中文角色用大陆普通话戏剧声线（不要用会飘口音的英文库声）
2. 表演不够激烈时，把稳定性打到 Creative `0.0`，并在要生效的那半句前写入 Audio Tags；不要靠加大音量或改台词
3. 时间轴跟人声走，不要把人声剪短去套旧母带格子
4. 音效和配乐用同一家一起合成，先出关键对白短试听，听过再跑整集；旧成片只新增、不覆盖

## 选型：我们踩过的坑

| 做法 | 结果 | 结论 |
| --- | --- | --- |
| Drama 3（Fish Audio，Colab 本地推理）整集 | 能出片，但听感偏平、偏假 | 不当成中文广播剧主引擎 |
| IndexTTS2 官方锚点克隆 + `emo_text` | 能跑通，听感不如 ElevenLabs | 可作对照，不优先 |
| ElevenLabs `eleven_v3` + 美式 Tex / 澳洲 Charlie / 新加坡 Loh 演中文角色 | 引擎好，但声线会飘，不像大陆戏剧配音 | 引擎留，声线换 |
| 用中文专业库声，但把新对白硬套进旧 Drama 3 的 149.5 秒格子 | 语速慢于格子的句子被收短，听起来话说到一半被掐 | 禁止按旧时长裁人声 |
| 稳定性设成 `0.35–0.55`，不加标签 | 接近官方 Natural `0.5`，标签几乎不生效，表演不够激烈 | 激烈戏用 Creative `0.0` + 行内标签 |
| 把稳定性设成 `0.15–0.30` 这种中间值 | 不是官方 v3 档位，可能被吸附到 `0.5` | 只用 `0.0` / `0.5` / `1.0` |
| 第一轮把音效和背景一起按 `0.34` 压下去 | 音效被连带压矮 | 音效走前景总线，只闪避配乐 |

对照顺序建议：同一段关键对白，先定引擎，再定声线，再定时间轴，最后加表演标签。不要四件一起改，否则分不清是哪一步生效。

## 硬规则

- 中文角色必须用大陆普通话戏剧 / 配音声线。不要用美式、澳洲、新加坡等会在中文里飘口音的库声。
- 人声按自然语速完整保留。禁止为了贴齐旧母带、旧时间轴或旧片长而裁句、淡出掐尾。
- 激烈表演用 `eleven_v3` 的 Creative 稳定性 `0.0` + 行内 Audio Tags。不要对 v3 使用 SSML（SSML 属于 `multilingual_v2` / `flash_v2_5`）。
- 不要给 v3 传 `previous_text` / `next_text`，接口会拒。
- `language_code` 用 `zh`。发出去的口语必须是中文；英文表演标签只写在方括号里，不能被念出来。
- 先出 6 句左右的关键对白短试听（对白 only、无主题板、无整床音效配乐），听过并认可后再跑整集。
- 旧成片、旧对照版、旧试听一律不覆盖，只新增文件。
- 标签要匹配这条声线的性格。不要指望一条偏柔的声线突然能稳定喊穿。

## 声线

### 1. 共享库中文筛选与防洋腔漏网

- 共享库检索 `GET /v1/shared-voices` 的大陆普通话 `locale` 参数必须传 **`cmn-CN`**（传 `zh-CN` 会直接报 `400 Invalid locale`）。
- 注意：即便指定 `locale=cmn-CN`，共享库在 `age=old` 等稀缺标签下仍会混入外语母语声优的多语种自动配音（例如描述里写着 `older British` 却挂在 `cmn-CN` 下），说中文会有明显「老外腔」。必须结合 `accent` 与 `description` 二次过滤。
- 从共享库加入我的声音库时，`POST /v1/voices/add/{public_owner_id}/{voice_id}` 必须带 `new_name`，否则会返回 `422`。

### 2. 原生国风声线捏造（Voice Design `eleven_ttv_v3`）

当现有库声缺少特定国风人物质感（如 60 岁沧桑忠仆老管家、黑市怪医老头、极寒清冷古风仙子、深沉厚重电影感古风旁白）时，直接用同一个 API Key 调用 **Voice Design v3** 从零创造纯正中国大陆普通话专属声线：

1. **生成 3 条候选试听**：`POST /v1/text-to-voice/design`，`model_id="eleven_ttv_v3"`。
   - `voice_description`（`20–1000` 字符）：用中文写清年龄、籍贯/普通话标准度、共鸣位置、人物性格与禁忌（例如：`一位六十五岁的中国北方老管家，纯正标准中国大陆普通话，嗓音苍老沙哑却透着温厚慈爱与忠心耿耿，带有古典仙侠影视剧老戏骨的沧桑颗粒感与自然呼吸感，绝无外国口音或播音腔`）。
   - `text`（**必须 `100–1000` 字符**，过短会报 `422`）：直接放入一段约 120–200 字的本剧高张力中文台词，一次返回 3 个不同音色的 `generated_voice_id` 与试听音频。
2. **固化为永久角色声优**：挑中最贴脸的一条 `generated_voice_id`，调用 `POST /v1/text-to-voice`（附带 `voice_name`、`voice_description`、`labels={"language": "zh", "accent": "cmn-CN"}`）存入工作区，拿到永久 `voice_id`，后续即可在 `eleven_v3` 中配合 `[crying]`、`[whispers]`、`[coldly]` 等全套行内标签出演整部连载。

《九狱剑主》E001 已过审的中文库声范例（新项目可「库声 + `eleven_ttv_v3` 原创定制声线」混合选角）：

| 角色 | 库声 | voice_id |
| --- | --- | --- |
| 旁白 | Jerry | `pz7hOfW7kgI9kF818eDS` |
| 沈璃 | Shasha | `8uceOSflAGVvQuMt4HPh` |
| 沈渊 | Hou Xiaohou | `lkK6X9yp6sIA3vecwS2p` |
| 雷豹 | WangSong | `vBK1ICucZ4f5G7wjYUBd` |
| 苏清寒 | Linda | `t5SIDRTVMdbNUqrSAycs` |
| 沈傲 | Jun | `5s3UifUu3OJ90z17rRMA` |

Shasha 是戏剧演员声线，适合哭喊、恳求这类戏；不适合当财经口播主持。换项目时仍要按「这条声线能不能演这个人物」来听，不要只看标签名字。

## 表演控制：稳定性 + Audio Tags

### 稳定性（v3 只有三档）

官方离散档位：

| 值 | 模式 | 什么时候用 |
| --- | --- | --- |
| `0.0` | Creative | 戏剧、冲突、哭喊、冷嘲、反派笑；要让标签真正生效 |
| `0.5` | Natural | 叙述平稳、日常对白 |
| `1.0` | Robust | 要稳、要齐，宁可少一点起伏 |

激烈戏（包括旁白里的高潮句）用 `0.0`。`similarity_boost` 保持较高（本轮验证用 `0.85`），避免稳定性打到 Creative 后面貌漂移。

### Audio Tags 写法

- 用小写方括号，写在它要管的那半句**前面**，一直管到下一个标签。
- 官方常见类别：情绪（`[angry]`、`[crying]`、`[dramatic tone]`、`[excited]`、`[sarcastic]`）、语态（`[whispers]`、`[shouts]` / `[shouting]`、`[rushed]`、`[drawn out]`、`[softly]`）、反应（`[laughs]`、`[sighs]`、`[exhales]`、`[gasps]`、`[clears throat]`）、停顿（`[pause]`、`[short pause]`、`[long pause]`，或省略号）。
- 标签不是封闭枚举，自然语言交付标签（如 `[coldly]`、`[desperately]`、`[mischievously]`）可以使用；官方示例里已有 `[dismissive]`。
- 关键词大写会加重强调，但不要整句大写来「喊响」。
- 要有对比：可以先气声 / 冷声，再在决断句上 `[shouting]`。不要六句全喊。
- 表演扁了，先降稳定性并重写标签，而不是把形容词堆进台词。

参考：

- [Audio Tags 101](https://elevenlabs.io/blog/v3-audiotags)
- [Best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [How audio tags work with v3 / v4](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-do-audio-tags-work-with-eleven-v3-and-v4)
- [AbyssusErigo 的标签流程](https://x.com/AbyssusErigo/status/1991689291551109596)、[Audio Tag prompt](https://x.com/AbyssusErigo/status/1995664379791220808)

### 已过审的激烈表演示例（E001 关键六句）

口语中文不变，只在前面加标签。全部 `stability=0.0`，`similarity_boost=0.85`，`language_code=zh`。

| 角色 | 发出去的文本 |
| --- | --- |
| 旁白 | `[dramatically] 沈渊一口心头血喷在锁骨下的暗金烙印上—— [shouting] 九重镇狱黑匣，轰然开启！` |
| 沈璃 | `[crying] 哥……别管我…… [desperately] 快走啊！` |
| 沈渊 | `[desperately] 开第一层！ [shouting] 用我十年阳寿，换你一缕斩铁剑意！` |
| 雷豹 | `[angry] [shouting] S级无垢剑骨！二少爷今晚融合它，你妹妹，就能当具全尸了！` |
| 苏清寒 | `[coldly] 经脉尽碎才想起敲门？ [dismissive] 我的祭品，你太弱了。` |
| 沈傲 | `[laughs] [mischievously] 今晚过后，沈璃的剑骨归我，沈渊的未婚妻夜惊鸿——也归我！` |

质检：用 ASR 听写，确认方括号里的英文标签没有被念出来，句子完整、没有爆音截断。标签被念出或这条坏了，才允许用更简单的标签集重试一次；两次仍失败就停，不要循环烧额度。

## 自然语速时间轴

不要把新对白锁进旧成片的秒数。正确拼法：

1. 每句对白 WAV 完整播放（不裁尾）
2. 每个音效按自己的时长完整播放
3. 条目之间只留清单里的 `gap_after_s`
4. 片头可留约 `0.30s` 垫，片尾约 `1.2s` 收

E001 从锁格子的 149.49 秒，变成自然语速的 176.60 秒（约长 27 秒）。片长变化是预期结果，不是错误。

## 音效与配乐

同一集里，对白、音效、配乐都用 ElevenLabs，避免「人声是一家、床是另一家」的质感裂缝。

- 音效：`POST /v1/sound-generation?output_format=wav_48000`，模型 `eleven_text_to_sound_v3`。`duration_seconds` 跟清单走，`prompt_influence` 可用 `0.55`。
- 配乐：`POST /v1/music?output_format=mp3_48000_192`，模型 `music_v2_5`，`force_instrumental=true`。按幕铺床，不要试图用一首歌硬撑全片所有情绪。
- 闪避：对白底下把配乐压到约 `0.11`，空隙里回到约 `0.34`。音效走前景，不要和对白闪避用同一系数。
- 混音检查：对人声做中侧 / 语音段闪避时，不要把音效一并压矮。

官方列表价或「预估字符」往往会偏低；合成后等订阅用量落定再记一笔。标签字符也计入额度。

## 推荐工作流

1. **定声线**：每人 1 句关键对白，对白 only，听音色和口音。
2. **定时间轴**：按自然语速出一版整集（可先用已过审声线，音效配乐一起合成）。若仍在套旧格子，先停下来改拼法，不要继续修标签。
3. **加表演**：同一组关键句，改用 Creative `0.0` + Audio Tags 再出短试听。
4. **整集重跑**：短试听听过并认可后，再用同一套标签规则重跑整集。未叫跑之前不要自动开。
5. **归档**：每次只新增文件；把发出去的原文、标签、稳定性、voice_id 写成 JSON 一起存。

## 长篇连载持续生产：声线圣经与母题归档

单集验证跑通后，一旦进入几十到上千章的小说连载有声剧 / 广播剧持续制作，最容易崩的不是单句音质，而是**跨会话遗忘与前后串音**。必须把以下三份结构化记录放进项目专属音频目录持续维护：

1. **角色声线注册表（`voice_casting_registry.json` + 可读选角圣经 `.md`）**：
   - 每个角色从首次出场起就登记 `role_id`、人物底色、年龄音域、`voice_id`、`public_owner_id`、库声原名、默认 `stability` / `similarity_boost`、标志性标签、禁忌习惯，以及历次试听小样路径与过审状态（`pending_audition` → `auditioning` → `locked`）。
   - 一旦角色进入 `locked`，后续所有章节严禁擅自更换 `voice_id`；隔了几十章返场的老角色直接查表复用。
   - 多重身份 / 识海潜魂角色（如前世残魂、棺中人物）必须独立建角色槽位并配合声场标记（如 `mental_realm` / `memory_echo`），与现世主声线拉开听感层次。
2. **世界观标志性声效母题（`sonic_motifs`）**：
   - 长篇里反复出现的核心意象（如识海小世界开启、血脉/基因锁崩裂心跳、古棺叩响、特定法器出鞘）统一注册为 `motif_id` 并缓存母带，跨集直接复用，建立听众的巴甫洛夫听觉锚点，同时节省重复生成额度。
3. **生产进度与用量台账（`production_ledger.jsonl` / `production_progress_ledger.json`）**：
   - 记录每一章的拆本状态、试听状态、成片版本号、订阅用量前后差值与网盘归档文件 ID，任何新会话接手都能一秒定位续跑位置。

## 小说转有声剧 / 广播剧拆本四条准则

1. **剥离冗余提示语（「某某道」转标签）**：原文写「福伯哑声道：“……”」或「裴玄度轻描淡写道：“……”」，当角色已是独立声优出演时，删除旁白末尾机械的「某某某道」，把神态副词转译为该角色台词前的行内标签（如 `[hoarsely] [crying]`、`[warmly] [dismissive]`），避免旁白演一遍、角色再重复演一遍。
2. **旁白也要做戏剧分级**：环境铺陈与过渡句用 `stability=0.5`（Natural）；生死一线、丹田破碎、识海洞开等纯视觉高潮段（往往没有角色对话），旁白必须切到 `stability=0.0`（Creative）配合 `[dramatically]`、`[whispers]` 与前景动效撑起场面。
3. **双密度模式按需切换**：
   - `immersive_audiobook_drama`（精品多人有声剧，推荐长篇连载）：一章一集（约 8–12 分钟），保留凝练文学旁白与心理暗流，全角色独立配音 + 分幕配乐 + 关键动效，零剧情遗漏。
   - `condensed_radio_drama`（浓缩纯广播剧）：大刀阔斧删减叙述性旁白，把视觉描写改写为前景动效（Foley）与潜台词交锋，单集压缩至 3–5 分钟。
4. **动效顺播 vs 叠拍**：需要留出戏剧空白听清的动效（如深夜叩门三声「咚，咚，咚」、撕毁婚书、烛火爆灯花熄灭）用 `sequential` 独立占时；需要贴着动作瞬间炸开的动效（如雷鸣、破空一指）用 `overlay_next` 与下一句同步切入。

## 接口与长篇量产备忘（《诸界锁仙》40 章实战增补）

- 对白模型：`eleven_v3`。输出建议 `48 kHz`（`wav_48000` 需 Pro 及以上档位；Creator / Starter 档位自动回退 `mp3_44100_192` / `mp3_44100_128` 并在本地无损转码为 `48kHz 16-bit PCM WAV` 上时间轴，绝不裁尾）。
- 并发上限与熔断：常规订阅最大并发请求数为 **5**（`--workers 8` 会密集触发 `HTTP 429 concurrent_limit_exceeded`）。量产默认锁定 `--workers 4`，配合 6 次带随机抖动的指数退避重试；若响应体出现 `quota_exceeded` 则立即熔断停机，绝不空转重试。
- 双轨多音字与古典数字纠偏：台本同时维护 `text`（原著文学正字，供 `.srt` 字幕与审阅）与 `tts_text`（自动把 `引气一重..九重`、`真传`、`忝为`、`降生/降临`、`九月廿三`、`白芨/虫豸/龟裂` 及大写数字 `壹号..拾号 / 第柒拾叁号` 替换为同音字喂给 TTS），并在 Scribe 质检层做双参考对齐。
- 100% 无删节硬门禁：长篇多人有声剧（`immersive_audiobook_drama`）使用 `compiler.py` 编译时，强制校检编译后口播汉字数占原著正文比例 **`>= 96.5%`**（仅剔除独立拟声词行与冗余 `“某某道：”`），杜绝漏段缩写。
- 配乐接口防坑：`POST /v1/music`（`music_v2_5`）使用 `prompt` 生成时，**严禁同时传 `seed` 字段**，否则官方接口直接返回 `422 Unprocessable Entity`。
- 双语 ASR 质检与 SHA-256 缓存：`POST /v1/speech-to-text` 使用 `scribe_v3` 时传入 `language_code="zh"` 与 `secondary_language_codes=["en"]`，并对音频 SHA-256 缓存转写结果，重混母带时零重复扣费。
- 不要把密钥写进仓库、提示词或文档（推荐存于环境变量 `ELEVENLABS_API_KEY` 或用户级持久化配置 `~/.gemini/config/aigc_audio.env`）。
- 共享库加声必须带 `new_name`。
- 额度以订阅页落定后的 used / remaining 为准，不要只信调用当时的即时回读。
- 完整十二项技术优化点详见：[`docs/OPTIMIZATIONS.md`](../docs/OPTIMIZATIONS.md)。

## 和 aigc-mv-pipeline 的关系

影像成片在同级仓库 [aigc-mv-pipeline](https://github.com/riversxiao/aigc-mv-pipeline) 的 [`PIPELINE.md`](https://github.com/riversxiao/aigc-mv-pipeline/blob/master/playbook/PIPELINE.md)（焚诀：先剪后生成、首尾帧硬检、fl2va）。本文件管的是**声音**：广播剧 / 有声书 / 短剧对白床，且本仓产出的逐句精确毫秒时间轴（`.json` + `.srt`）可直接喂给影像流水线做音画对齐。两套可以配在同一项目里，但两个仓库互不替代——画面过检不等于配音能过，反之亦然。
