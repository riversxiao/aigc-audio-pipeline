# 《经济机器怎么转：〈原则与大债务危机〉周期剧》工程目录

24 部经典经济金融广播剧全目录的**宏大收官第 24 部**！以**滨江夜雨黄铜齿轮书房、长三角精密五金车间、商业银行信贷风控台、央行议息厅与寻常家庭账本餐桌**为现代情景舞台打造的 **8 角色零翻译腔电影感宏观周期广播剧**（**100% 原创中国化情景剧与家常比喻，严守原著版权合规红线，零原文直译与既有译本搬运**）。全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`，自动归档至 `MyDrive/《经济机器怎么转》大债务危机周期剧场/02_分集成片母带_WAV_MP3_SRT/`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：版权合规架构、8 角色选角、6 集周期脉络与精确编译字数台账
  - `voice_casting_registry.json`：8 角色锁定配置（`domain="debt_cycle_machine"`）+ 6 个滨江齿轮钟/工业园/银行/央行/家庭账本纯拟音声音母题
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧锚点，与选角表 1:1 严格对齐）
- `02_分集广播剧台本/`：`AUDITION_DEBT` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（**355 轨 / 18,277 字**；其中试听包 **16 轨 / 749 字**，正片 `E001–E006` 共 **339 轨 / 17,528 字**，每集 **2,896–2,960 字**，单句最长 **79 字**，每集纯拟音 **8–9 轨**）
- `03_喜马拉雅分发与爆款包装方案/`
  - `debt_cycle_machine_ximalaya_cover_titled_1x1.jpg`：1:1 带标题喜马拉雅官方专辑封面
  - `debt_cycle_machine_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台合规定位、卖点、标签与试听包 + 6 集高点击钩子
- `scripts/`：台本编译器与纯声学周期纪录片极简钢琴大提琴原声带主题配置（`ost_and_motifs.py`、`drama_helpers.py`、`ep01_03_scripts.py`、`ep04_06_scripts.py`、`build_season1.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本（零错误、字数/拟音/单句/纯中文硬门禁）
PYTHONPATH=src python3 projects/debt_cycle_machine/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project debt_cycle_machine --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project debt_cycle_machine --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
