# 《聊斋志异·午夜悬疑广播剧场》第一季生产工程包

本目录收纳《聊斋志异·午夜悬疑广播剧场》第一季（**定角试听包 + 6 大王牌名篇：`画皮 / 聂小倩 / 陆判 / 尸变 / 崂山道士 / 考城隍`**）的全套选角注册表、零成本声线复用映射、分幕广播剧台本（`.json` + `.md`）与喜马拉雅冷启动分发包。

> **100% 零 API 成本架构**：复用 Google Drive 已归档的 `zhujie_suoxian_96gb_drama3_bundle.zip` 15 条纯正国风棚录干音锚点，在 Colab 96GB G4 上由 `Fish Drama 3 + MOSS-SoundEffect v2.0 + ACE-Step 1.5 XL` 全本地渲染，单集完成即原子归档至 `MyDrive/《聊斋志异》午夜悬疑广播剧场/02_分集成片母带_WAV_MP3_SRT/`。

## 快速命令

```bash
# 1. 本地重新编译并校验全部 7 份台本（零 GPU / 零 API）
PYTHONPATH=src python3 projects/liaozhai_midnight/scripts/build_season1.py

# 2. 本地 CPU 离线干跑验证完整三总线混音链路
python3 colab_96gb/launch_g4_anthology_drama3.py --project liaozhai_midnight --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键满血渲染全部 6 集 + 试听包，完工自动关机止费
python3 colab_96gb/launch_g4_anthology_drama3.py \
  --project liaozhai_midnight \
  --episodes AUDITION,E001-E006 \
  --skip-existing --auto-unassign
```
