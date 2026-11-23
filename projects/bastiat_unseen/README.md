# 《1850巴黎议会讽刺剧：〈看得见的与看不见的〉》工程目录

基于法国经济学讽刺大师弗雷德里克·巴斯夏（1801–1850）**100% 全球公版名著《看得见的与看不见的》《经济谬论》《国家论》《法律》** 打造的 **8 角色零翻译腔电影感巴黎议会讽刺广播剧**，全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：全剧零翻译腔讽刺改编标准、8 角色选角、6 集大纲与字数台账
  - `voice_casting_registry.json`：8 角色锁定配置 + 6 个 1850 巴黎街角/议会纯物理声音母题（`domain="bastiat_unseen"`，`cached_file=""`）
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧声线）
- `02_分集广播剧台本/`：`AUDITION_BASTIAT` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（368 轨 / 17,519 字；正片 6 集每集 2,832–2,884 字、8–9 条纯物理拟音、单句最长 ≤ 80 字）
- `03_喜马拉雅分发与爆款包装方案/`
  - `bastiat_unseen_ximalaya_cover_titled_1x1.jpg`：1:1 烫金标题喜马拉雅官方专辑封面
  - `bastiat_unseen_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台标题、卖点、标签与 6 集点击钩子
- `scripts/`
  - `ost_and_motifs.py`：5 首纯声学 1850 巴黎沙龙弦乐四重奏/大提琴拨弦/古钢琴 OST 主题 + 6 个纯物理拟音母题
  - `drama_helpers.py`：台本构造器（严格校验 4 种允许声场 + `bastiat_unseen` 多音字矫正）
  - `ep01_03_scripts.py`：`AUDITION_BASTIAT` + `E001–E003` 台本源码
  - `ep04_06_scripts.py`：`E004–E006` 台本源码
  - `build_season1.py`：全季编译、QA 硬性校验与 JSON/Markdown 导出脚本

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本（0 错误、每集 2,800–3,050 字、单句 ≤ 88 字、7–10 条纯物理 SFX）
PYTHONPATH=src python3 projects/bastiat_unseen/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project bastiat_unseen --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project bastiat_unseen --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
