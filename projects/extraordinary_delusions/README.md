# 《1841伦敦泡沫档案：〈大癫狂〉金融疯魔史》工程目录

基于查尔斯·麦基（Charles Mackay，1814–1889）**1841 年全球公版金融心理奇书《大癫狂》**（*Extraordinary Popular Delusions and the Madness of Crowds*）打造的 **8 角色零翻译腔电影感历史财经广播剧**，全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：全剧零翻译腔改编标准、8 角色选角、6 集大纲与字数台账
  - `voice_casting_registry.json`：8 角色锁定配置 + 6 个 1841 伦敦 / 阿姆斯特丹 / 巴黎纯拟音声音母题
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧声线）
- `02_分集广播剧台本/`：`AUDITION_DELUSIONS` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（324 轨 / 17,815 字；正片 E001–E006 每集 2,825–3,015 字、8–9 条纯拟音、单句最长 ≤ 85 字）
- `03_喜马拉雅分发与爆款包装方案/`
  - `extraordinary_delusions_ximalaya_cover_titled_1x1.jpg`：1:1 烫金标题喜马拉雅官方专辑封面
  - `extraordinary_delusions_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台标题、卖点、标签与 6 集高点击钩子
- `scripts/`：台本编译器（`build_season1.py`）、共享构建器（`drama_helpers.py`）、5 首 1841 伦敦纯声学巴洛克-浪漫派室内原声带主题配置（`ost_and_motifs.py`）与分集台本源码（`ep01_03_scripts.py`、`ep04_06_scripts.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本（强制检查 0 错误、2800–3050 字/集、7–10 纯拟音/集、单句 ≤ 88 字）
PYTHONPATH=src python3 projects/extraordinary_delusions/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project extraordinary_delusions --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project extraordinary_delusions --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
