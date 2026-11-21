# 《克苏鲁神话·不可名状声音档案》第一季生产工程包

本目录收纳 H.P. 洛夫克拉夫特（1890–1937，全球 100% 公版）六大核心神作的**电影级中文多人悬疑广播剧**完整工程（**定角试听带 + 6 卷正片：`克苏鲁的呼唤 / 印斯茅斯之影 / 星之彩 / 暗夜呢喃 / 敦威治恐怖事件 / 疯狂山脉`**）。

> **100% 零 API 成本架构**：混合复用本地仓库 3 条 V2 全真人近讲现代棚录干音（`projects/buffett_letters/.../voice_anchors/`）+ Google Drive `zhujie_suoxian_96gb_drama3_bundle.zip` 11 条高张力戏剧惊悚声线，在 Colab 96GB G4 上零 API 费用批量输出 48kHz WAV / 320k MP3 / 角色真名 SRT 并自动同步至 `MyDrive/《克苏鲁神话》不可名状声音档案/02_分集成片母带_WAV_MP3_SRT/`。

## 快速命令

```bash
# 1. 本地编译并严格校验全部 7 份台本
PYTHONPATH=src python3 projects/cthulhu_archives/scripts/build_season1.py

# 2. 本地 CPU 离线干跑验证完整链路
python3 colab_96gb/launch_g4_anthology_drama3.py --project cthulhu_archives --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键满血渲染全部 6 卷 + 试听带，完工自动关机止费
python3 colab_96gb/launch_g4_anthology_drama3.py \
  --project cthulhu_archives \
  --episodes AUDITION,E001-E006 \
  --skip-existing --auto-unassign
```
