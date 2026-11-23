# 《1911维也纳风暴：〈经济发展理论〉创新剧》工程目录

基于约瑟夫·熊彼特（1883–1950）**100% 全球公版巨著《经济发展理论》（1911）** 打造的 **8 角色零翻译腔电影感历史商业思想广播剧**，全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：全剧零翻译腔改编标准、8 角色选角、6 集大纲与字数台账
  - `voice_casting_registry.json`：8 角色锁定配置 + 6 个 1911 维也纳纯拟音声音母题
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧声线）
- `02_分集广播剧台本/`：`AUDITION_SCHUMPETER` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（361 轨 / 17,592 字；正片每集 2,822–2,912 字，单句最长 ≤ 78 字）
- `03_喜马拉雅分发与爆款包装方案/`
  - `schumpeter_1911_ximalaya_cover_titled_1x1.jpg`：1:1 烫金标题喜马拉雅官方专辑封面
  - `schumpeter_1911_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台标题、卖点、标签与 6 集点击钩子
- `scripts/`：台本编译器、严格 QA 校验器与 1911 维也纳浪漫派纯声学室内乐原声带配置

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并严格校验全部 7 份台本（验证声线锁定、四类声场白名单、纯拟音后缀、每集 2800–3050 字与单句 ≤ 88 字）
PYTHONPATH=src python3 projects/schumpeter_1911/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project schumpeter_1911 --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project schumpeter_1911 --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
