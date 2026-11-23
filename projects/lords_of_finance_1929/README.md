# 《1929黄金镣铐：〈金融之王〉四央行行长博弈》工程目录

以 **1919–1933 年巴黎凡尔赛走廊、柏林魏玛印钞车间与运河面包坊、伦敦针线街地下金库、巴黎法兰西银行与纽约长岛秘密庄园** 为历史舞台打造的 **8 角色零翻译腔电影感金融史广播剧**（**100% 原创历史情景剧与日常中国化比喻，基于公有领域战间期央行史实独立创作，零任何版权著作直译或译本搬运**）。全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`，自动归档至 `MyDrive/《1929黄金镣铐》金融之王四央行博弈剧/02_分集成片母带_WAV_MP3_SRT/`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：原著版权合规边界、8 角色选角、6 集货币史脉络与精确编译字数台账
  - `voice_casting_registry.json`：8 角色锁定配置（`domain="lords_of_finance_1929"`）+ 6 个 1929 伦敦/柏林/华尔街电影级声音母题
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧锚点，与选角表 1-to-1 严格对应）
- `02_分集广播剧台本/`：`AUDITION_LORDS` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（**344 轨 / 18,088 字**；其中试听包 **771 字**，正片 `E001–E006` 共 **326 轨 / 17,317 字**，每集 **2,828–2,914 字**，每集纯拟音 **8 轨**，单句最长 **83 字**）
- `03_喜马拉雅分发与爆款包装方案/`
  - `lords_of_finance_1929_ximalaya_cover_titled_1x1.jpg`：1:1 带标题喜马拉雅官方专辑封面
  - `lords_of_finance_1929_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台合规定位、卖点、标签与试听包 + 6 集高点击钩子
- `scripts/`：台本编译器与 1929 欧洲战间期纯声学悲剧室内管弦原声带主题配置（`ost_and_motifs.py`、`drama_helpers.py`、`ep01_03_scripts.py`、`ep04_06_scripts.py`、`build_season1.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本
PYTHONPATH=src python3 projects/lords_of_finance_1929/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project lords_of_finance_1929 --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project lords_of_finance_1929 --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
