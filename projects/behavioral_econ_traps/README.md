# 《决策的暗礁：行为经济学与〈思考，快与慢〉剧场》工程目录

以**灯塔巷认知实验咖啡馆（二楼行为决策实验室 + 一楼咖啡吧台、生鲜超市与烟火商圈）**为原创双舞台打造的 **8 角色零翻译腔行为经济学心理广播剧**（**100% 原创情景剧场与日常中国化实验对白，严守当代著作版权合规红线，零原文直译与译本搬运**）。全程 **\$0 ElevenLabs API 成本**（100% 复用仓库真人现代棚录干音 + `zhujie_suoxian` 锁定戏剧锚点，直出 Colab 96GB G4 `Fish Audio Drama 3 + MOSS-SoundEffect-v2.0 + ACE-Step 1.5 XL` 广播级 `-16 LUFS` 48kHz WAV / 320k MP3 / 角色真名 `.srt`，自动归档至 `MyDrive/《决策的暗礁》行为经济学心理陷阱剧场/02_分集成片母带_WAV_MP3_SRT/`）。

## 目录结构

- `00_节目圣经与选角档案/`
  - `SHOW_BIBLE.md`：原著版权合规架构、8 角色选角、6 集实验思想脉络与精确编译字数台账
  - `voice_casting_registry.json`：8 角色锁定配置（`domain="behavioral_econ_traps"`）+ 6 个咖啡馆实验桌/秒表/黄铜锚/超市/看盘/清单纯拟音母题
  - `anchor_sources.json`：零成本声线复用映射表（3 真人棚录 + 5 戏剧锚点，与 `voice_casting_registry.json` 严格 1 对 1 匹配）
- `02_分集广播剧台本/`：`AUDITION_BEHAV` + `E001–E006` 全部 7 份 JSON & Markdown 导演台本（**386 轨 / 18,170 字**；其中试听包 **18 轨 / 752 字**，正片 `E001–E006` 共 **368 轨 / 17,418 字**，每集 **2,859–2,946 字**，纯拟音 **8–9 轨/集**，单句最长 **79 字**）
- `03_喜马拉雅分发与爆款包装方案/`
  - `behavioral_econ_traps_ximalaya_cover_titled_1x1.jpg`：1:1 带标题喜马拉雅官方专辑封面
  - `behavioral_econ_traps_cover_clean_1x1.jpg`：1:1 纯净无字油画母版
  - `XIMALAYA_LAUNCH_KIT.md`：平台合规定位、卖点、标签与试听包 + 6 集高点击钩子
- `scripts/`：台本编译器与现代认知纪录片纯声学原声带主题配置（`ost_and_motifs.py`、`drama_helpers.py`、`ep01_03_scripts.py`、`ep04_06_scripts.py`、`build_season1.py`）

## 快速验证与云端 G4 渲染

```bash
# 1. 重编并校验全部 7 份台本
PYTHONPATH=src python3 projects/behavioral_econ_traps/scripts/build_season1.py

# 2. 本地离线三总线混音与 -16 LUFS 母带干跑验证
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project behavioral_econ_traps --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键渲染全季并原子落盘至 Google Drive（跑完自动销毁止费）
python3 -u colab_96gb/launch_g4_anthology_drama3.py --project behavioral_econ_traps --episodes AUDITION,E001-E006 --skip-existing --auto-unassign
```
