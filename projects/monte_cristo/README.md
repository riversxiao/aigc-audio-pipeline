# 《基督山伯爵·伊夫堡复仇广播剧》（Season 1）

基于大仲马 1844 年全球公版名著 *Le Comte de Monte-Cristo* 全新改编的 **6 集 × 15–20 分钟电影级多播广播剧**，全程复用已锁定零 API 成本干音锚点（`Fish Audio Drama 3` + `MOSS-SoundEffect-v2.0` + `ACE-Step 1.5 XL`）。

## 目录结构
- `00_节目圣经与选角档案/`：`SHOW_BIBLE.md`、`voice_casting_registry.json`（14 角色 + 6 母题）、`anchor_sources.json`
- `02_分集广播剧台本/`：`AUDITION_MONTE_CRISTO` + `E001`–`E006` 完整 JSON / Markdown 广播剧台本
- `03_喜马拉雅分发与爆款包装方案/`：`XIMALAYA_LAUNCH_KIT.md` + 1:1 喜马拉雅方形专辑封面图（无字油画母版 + 排版成图）
- `scripts/`：台本生成与校验脚本（`PYTHONPATH=src python3 projects/monte_cristo/scripts/build_season1.py`）

## Colab 96GB G4 一键渲染命令
```bash
# 仅跑试听包（快速回听质检）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project monte_cristo --episodes AUDITION --keep-drama-alive

# 跑全季 6 集正片并自动落盘 Google Drive & 释放 G4 止费
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project monte_cristo --episodes E001-E006 --skip-existing --auto-unassign
```
- **Google Drive 自动落盘路径**：`MyDrive/《基督山伯爵》伊夫堡复仇广播剧/02_分集成片母带_WAV_MP3_SRT/`
