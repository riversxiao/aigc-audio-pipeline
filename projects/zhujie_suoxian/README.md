# 《诸界锁仙》电影感多人精品有声剧 · 持续生产工程包

本目录收纳《诸界锁仙》第一卷（第 01–40 章，`E001`–`E040`）的全套**选角圣经、锁定声优注册表、生产进度台账、40 集无删节演出台本（`.json` + `.md`）与分批构建/续跑脚本**。

> **规则遵循**：所有大体积二进制音频母带（`.wav` / `.mp3`）与 API 密钥均不入库 Git，统一归档于项目 Google Drive `04_有声剧与广播剧音频`（Folder ID：`1wF3upZfT9zG5B06ZGNAkX9YynTJWERjs`）。

## 一、 目录结构

- [`00_声音选角档案与进度台账/`](00_声音选角档案与进度台账/)
  - [`00_诸界锁仙_配音选角圣经与声线档案.md`](00_声音选角档案与进度台账/00_诸界锁仙_配音选角圣经与声线档案.md)：24 位纯正大陆普通话锁定声优档案、6 枚跨集声效母题与续跑说明。
  - [`voice_casting_registry.json`](00_声音选角档案与进度台账/voice_casting_registry.json)：机器可读角色 `voice_id`、默认离散稳定性、行内标签与声效母题定义。
  - [`voice_cast_drama3.json`](00_声音选角档案与进度台账/voice_cast_drama3.json)：全 24 位活跃角色 `44.1kHz -16 LUFS` 零样本干声锚点与 100% 逐字对齐 `anchor_text` 清单（供 Fish Audio Drama 3 本地推理使用）。
  - [`production_progress_ledger.json`](00_声音选角档案与进度台账/production_progress_ledger.json)：全 40 集台本与母带生产进度、响度指标及 Google Drive 文件 ID 映射总表。
  - [`production_runs.jsonl`](00_声音选角档案与进度台账/production_runs.jsonl)：逐集成片构建审计流水。
- [`02_分集广播剧台本/`](02_分集广播剧台本/)
  - `E001`–`E040` 全 40 集 100% 无删节多角色演出台本（`.json` 机器执行版 + `.md` 导演审阅版，均已注入修仙多音字与古典大写数字 `tts_text` 纠偏）。
- [`scripts/`](scripts/)
  - `build_batch1_e003_e007.py` ～ `build_batch8_e037_e040.py`：第 03–40 章分幕导演蓝图与台本编译脚本（支持 `--compile-only` 离线重编译校验）。
  - `design_cast_ch03_40.py`：全剧新增角色 `eleven_ttv_v3` 国风捏声与锁定脚本。
  - `export_drama3_bundle.py`：一键导出全自包含 Colab 96GB Fish Drama 3 资产包（24 角色干声锚点 + 6 跨集母题 + 配乐缓存 + 40 集台本 + 试听包）。
  - `run_queue.py` / `batch_runner.py`：支持单集原子归档、EBU R128 响度校验与断点续跑的队列执行器。

## 二、 续跑与批量生产（`E007`–`E040` 双后端任选）

### 路线 A：Colab 96GB G4 本地开源三件套（`Fish Drama 3` 零 API 边际成本，推荐跑长篇大批量）
完整套件与自包含资产包已上传至项目 Google Drive `04_有声剧与广播剧音频/05_Colab_96GB_FishDrama3_满血本地推理管线`（Folder ID：`1GB1Cku8vW88H6p0FAXOjNZAOOr4-iZjH`），详见 [`colab_96gb/README_Colab_96GB_Drama3.md`](../../colab_96gb/README_Colab_96GB_Drama3.md)：

```bash
# 1. 启动 G4 实例并挂载云盘，先跑试听小样 + E001 做 A/B 听感验收（输出 E001_drama3_master_v001.*，绝不覆盖云端版）
colab new -s audio96 --gpu G4
colab drivemount -s audio96
colab exec -s audio96 -f colab_96gb/launch_g4_zhujie_drama3.py

# 2. 听感满意后，零 API 成本一键跑完剩余第 07–40 章（跑完释放实例）
echo "!python3 '/content/drive/MyDrive/《诸界锁仙》长篇修仙小说工程/04_有声剧与广播剧音频/05_Colab_96GB_FishDrama3_满血本地推理管线/launch_g4_zhujie_drama3.py' --episodes E007-E040 --skip-existing" | colab exec -s audio96
colab stop -s audio96
```

### 路线 B：ElevenLabs v3 云端五合一队列续跑
充值或更新 `ELEVENLABS_API_KEY` 后，直接执行：

```bash
# 方式 1：使用通用 CLI（支持自动读取 ZHUJIE_AUDIO_WORKSPACE 或指定工作区）
PYTHONPATH=src python3 -m aigc_audio_pipeline run-queue \
  --workspace /shared/user/.gemini/config/zhujie_suoxian_audio \
  --from-ep 7 --to-ep 40 --workers 4 \
  --drive-ledger-id 1j8kUC_uKBZx1HJIkP8asE91TcUKnrjZ5 \
  --drive-runs-id 1z7Lx5uWfzqK5ex48fGV9EVeDOM53fsxM \
  --drive-registry-id 1K3YyZc2tuLBVrlQyRDzXSmWwGemf9m0q

# 方式 2：使用项目快捷脚本
python3 projects/zhujie_suoxian/scripts/run_queue.py --from-ep 7 --to-ep 40 --workers 4
```

如需离线重新编译任意批次台本并执行 `>= 96.5%` 原文覆盖率硬门禁校验：

```bash
python3 projects/zhujie_suoxian/scripts/build_batch1_e003_e007.py --compile-only
```
