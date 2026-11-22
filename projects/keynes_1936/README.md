# 《1936剑桥迷雾：〈就业、利息和货币通论〉宏观思想剧场》工程目录

基于约翰·梅纳德·凯恩斯 **1936 年英文原版全球 100% 公版巨著《就业、利息和货币通论》**（作者 1946 年逝世已满 80 年）打造的 **8 角色零翻译腔电影感宏观商业思想广播剧**，全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：公版版权说明、零翻译腔五大铁律、8 角色选角与第一季精确编译台账
  - `voice_casting_registry.json`：8 角色锁定配置（`domain="keynes_1936"`）+ 6 个 1936 剑桥/曼彻斯特/伦敦电影级声音母题
  - `anchor_sources.json`：零成本声线复用映射表（3 真人现代棚录 + 5 精选戏剧声线）
- `02_分集广播剧台本/`：`AUDITION_KEYNES` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（**338 轨 / 18,079 字**；正片 6 集每集 **2,891–2,977 字**，单句最长 **≤ 90 字**）
- `03_喜马拉雅分发与爆款包装方案/`
  - `keynes_1936_ximalaya_cover_titled_1x1.jpg`：1:1 烫金标题喜马拉雅官方专辑封面
  - `keynes_1936_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台标题、卖点、标签与 6 集高点击金句钩子
- `scripts/`：台本编译器（`build_season1.py`、`drama_helpers.py`、`ep01_03_scripts.py`、`ep04_06_scripts.py`）与 1936 剑桥战间期纯声学室内乐原声带配置（`ost_and_motifs.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本
PYTHONPATH=src python3 projects/keynes_1936/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project keynes_1936 --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project keynes_1936 --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
