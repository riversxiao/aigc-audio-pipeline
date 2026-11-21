# 《1944剑桥夜话：〈通往奴役之路〉思想剧场》工程包

本目录收纳以 **1944 年战时剑桥书房历史情景** 为舞台、通俗接地气演绎哈耶克核心经济学思想及“哈耶克 × 凯恩斯世纪辩论”的多人有声剧全套资产（**试听包 + 6 集完整思想剧场**）。

> **版权合规与零 API 成本**：因哈耶克 1992 年去世，原书仍在著作权保护期内（中国至 2042 年底），本工程采用**100% 原创历史情景剧 + 日常中国化比喻拆解**，绝不搬运既有译本或做侵权全文直译。声库混合复用本地 3 条 V2 真人现代棚录干音 + 3 条戏剧声线，全程在 Colab 96GB G4 零 API 成本合成并自动归档至 `MyDrive/《1944剑桥夜话》哈耶克思想剧场/02_分集成片母带_WAV_MP3_SRT/`。

## 快速命令

```bash
# 1. 本地重新编译校验全部 7 份台本
PYTHONPATH=src python3 projects/hayek_1944/scripts/build_season1.py

# 2. 本地 CPU 离线干跑自检
python3 colab_96gb/launch_g4_anthology_drama3.py --project hayek_1944 --episodes AUDITION,E001 --offline-dry-run

# 3. Colab 96GB G4 一键满血渲染全部 6 集 + 试听包
python3 colab_96gb/launch_g4_anthology_drama3.py \
  --project hayek_1944 \
  --episodes AUDITION,E001-E006 \
  --skip-existing --auto-unassign
```
