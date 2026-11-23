# 《华尔街脱口秀：〈漫步华尔街〉指数革命》工程目录

以 **曼哈顿下城雨夜暖灯演播沙龙、软木飞镖盘、银元硬币盲测桌与会计师纸带计算器** 为固定剧场舞台打造的 **8 角色零翻译腔金融思想脱口秀广播剧**（**100% 原创华尔街演播沙龙辩论与日常中国化比喻，严守原著版权合规红线，零原文直译与译本搬运**）。全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`，自动归档至 `MyDrive/《华尔街脱口秀》漫步华尔街指数思想剧/02_分集成片母带_WAV_MP3_SRT/`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：原著版权合规架构、8 角色选角、6 集金融思想脉络与精确编译字数台账
  - `voice_casting_registry.json`：8 角色锁定配置（`domain="random_walk_wallstreet"`）+ 6 个曼哈顿演播沙龙/飞镖盘/硬币/计算器纯拟音母题（`cached_file=""`）
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧锚点）
- `02_分集广播剧台本/`：`AUDITION_RANDOMWALK` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（**348 轨 / 17,798 字**；其中正片 `E001–E006` 共 **338 轨 / 17,415 字**，每集 **2,882–2,943 字**，每集纯拟音 **8 轨**，单句最长 **87 字**）
- `03_喜马拉雅分发与爆款包装方案/`
  - `random_walk_wallstreet_ximalaya_cover_titled_1x1.jpg`：1:1 带标题喜马拉雅官方专辑封面
  - `random_walk_wallstreet_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台合规定位、卖点、标签与试听包 + 6 集高点击钩子
- `scripts/`：台本编译器与曼哈顿纯声学爵士室内乐原声带主题配置（`ost_and_motifs.py`、`drama_helpers.py`、`ep01_03_scripts.py`、`ep04_06_scripts.py`、`build_season1.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本
PYTHONPATH=src python3 projects/random_walk_wallstreet/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project random_walk_wallstreet --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project random_walk_wallstreet --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
