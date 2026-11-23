# 《激励侦探局：〈魔鬼经济学〉隐秘动机剧》工程目录

以现代中国都市梧桐巷二楼**“激励侦探局”**与街角**“老王杂货茶铺”**为常驻剧场打造的 **8 角色零翻译腔悬疑探案行为经济学广播剧**（**100% 原创中国现代生活悬案与公知经典实证谜题，严守原著版权合规红线，零原文直译与译本搬运**）。全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`，自动归档至 `MyDrive/《激励侦探局》魔鬼经济学隐秘动机剧/02_分集成片母带_WAV_MP3_SRT/`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：原著版权合规架构、8 角色选角、6 集探案脉络与精确编译字数台账
  - `voice_casting_registry.json`：8 角色锁定配置（`domain="freakonomics_theater"`）+ 6 个现代侦探经济学纯拟音声音母题（`cached_file=""`）
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧锚点）
- `02_分集广播剧台本/`：`AUDITION_FREAK` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（**365 轨 / 17,584 字**；其中正片 `E001–E006` 共 **355 轨 / 17,202 字**，每集 **2,838–2,907 字**，单句最长 **78 字**，每集纯拟音 **8–9 轨**）
- `03_喜马拉雅分发与爆款包装方案/`
  - `freakonomics_theater_ximalaya_cover_titled_1x1.jpg`：1:1 带标题喜马拉雅官方专辑封面
  - `freakonomics_theater_cover_clean_1x1.jpg`：1:1 纯净无字母版封面
  - `XIMALAYA_LAUNCH_KIT.md`：平台合规定位、卖点、标签与试听包 + 6 集高点击钩子
- `scripts/`：台本编译器与纯声学侦探经济学室内乐原声带主题配置（`ost_and_motifs.py`、`drama_helpers.py`、`ep01_03_scripts.py`、`ep04_06_scripts.py`、`build_season1.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本
PYTHONPATH=src python3 projects/freakonomics_theater/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project freakonomics_theater --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project freakonomics_theater --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
