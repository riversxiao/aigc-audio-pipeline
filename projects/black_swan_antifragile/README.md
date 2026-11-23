# 《感恩节火鸡警报：〈黑天鹅与反脆弱〉风险剧》工程目录

以 **地中海暗夜海港石屋、华尔街高空量化风控台、百年海运沉船档案室、港口柴火窑面包坊与医院急诊室** 为立体舞台打造的 **8 角色零翻译腔电影感金融与风险哲学广播剧**（**100% 原创情景剧与日常中国化狠比喻，严守版权合规红线，零原文直译与译本搬运**）。全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`，自动归档至 `MyDrive/《感恩节火鸡警报》黑天鹅与反脆弱风险剧/02_分集成片母带_WAV_MP3_SRT/`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：版权合规架构、8 角色选角档案、6 集风险哲学脉络与精确编译字数台账
  - `voice_casting_registry.json`：8 角色锁定配置（`domain="black_swan_antifragile"`）+ 6 个海港/风控台/沉船库/杠铃/窑炉电影级声音母题
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧锚点，与角色键 1-to-1 对齐）
- `02_分集广播剧台本/`：`AUDITION_SWAN` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（**359 轨 / 18,108 字**；其中正片 `E001–E006` 共 **343 轨 / 17,379 字**，每集 **2,860–2,934 字**，每集纯拟音 **8–9 轨**，全季单句最长 **83 字**）
- `03_喜马拉雅分发与爆款包装方案/`
  - `black_swan_antifragile_ximalaya_cover_titled_1x1.jpg`：1:1 带标题喜马拉雅官方专辑封面
  - `black_swan_antifragile_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台合规定位、爆款卖点、标签与试听包 + 6 集高点击标题钩子
- `scripts/`：台本编译器与地中海室内悬疑纯声学原声带主题配置（`ost_and_motifs.py`、`drama_helpers.py`、`ep01_03_scripts.py`、`ep04_06_scripts.py`、`build_season1.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本（零报错、精确字数/拟音/单句上限与声场硬门禁）
PYTHONPATH=src python3 projects/black_swan_antifragile/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project black_swan_antifragile --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project black_swan_antifragile --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
