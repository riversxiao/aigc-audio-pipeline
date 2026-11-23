#!/usr/bin/env python3
"""Build, validate, and benchmark AUDITION_GLOBAL_EDGE + E001_VA/VB/VC/VD for Global Edge.

Outputs (under `--out-dir`, default `projects/global_edge/02_分集广播剧台本`):
- `AUDITION_GLOBAL_EDGE_全口音与双语飙戏试听包.{json,md}`
- `E001_VA_HBO纯飙戏冷峻商战版_完整双语台本.{json,md}`
- `E001_VB_纸牌屋冻帧潜台词狙击版_完整双语台本.{json,md}`
- `E001_VC_三时区惊悚推进与实战跟读版_完整双语台本.{json,md}`
- `E001_VD_纪实同传叠音混合版_完整双语台本.{json,md}`
- `E001_COMPARATIVE_EVAL_RUBRIC.md` (generated dynamically from live computed metrics)

Usage:
    PYTHONPATH=src python3 projects/global_edge/scripts/build_e001_variants.py
    PYTHONPATH=src python3 projects/global_edge/scripts/build_e001_variants.py --check-only
    PYTHONPATH=src python3 projects/global_edge/scripts/build_e001_variants.py --out-dir /tmp/test_out
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
for _p in (str(SRC_DIR), str(SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from aigc_audio_pipeline.adapter import write_cue_sheet_markdown
from aigc_audio_pipeline.models import (
    EpisodeCueSheet,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
)
from drama_helpers import (
    DEFAULT_OUT_DIR,
    DRAMA_ACT_IDS,
    REGISTRY_PATH,
    SHOW_BIBLE_PATH,
    act_spec,
    compute_variant_metrics,
    ducked_en_pair,
    en_boardroom,
    estimate_cue_range_duration_s,
    lint_audition_pack,
    lint_e001_variant,
    motif_cue,
    slow_drill_pair,
    zh_en_backroom,
    zh_inner_monologue,
)
from ep001_va_hbo_duel import VA_VIRAL_CLIP_END, VA_VIRAL_CLIP_START, build_e001_va
from ep001_vb_hoc_sniper import VB_VIRAL_CLIP_END, VB_VIRAL_CLIP_START, build_e001_vb
from ep001_vc_thriller_drill import VC_VIRAL_CLIP_END, VC_VIRAL_CLIP_START, build_e001_vc
from ep001_vd_doc_duck import VD_VIRAL_CLIP_END, VD_VIRAL_CLIP_START, build_e001_vd
from ost_and_motifs import verify_sync_with_bible_and_registry

OUTPUT_FILENAMES: dict[str, str] = {
    "AUDITION_GLOBAL_EDGE": "AUDITION_GLOBAL_EDGE_全口音与双语飙戏试听包",
    "E001_VA": "E001_VA_HBO纯飙戏冷峻商战版_完整双语台本",
    "E001_VB": "E001_VB_纸牌屋冻帧潜台词狙击版_完整双语台本",
    "E001_VC": "E001_VC_三时区惊悚推进与实战跟读版_完整双语台本",
    "E001_VD": "E001_VD_纪实同传叠音混合版_完整双语台本",
}

VIRAL_CLIP_RANGES: dict[str, tuple[str, str]] = {
    "E001_VA": (VA_VIRAL_CLIP_START, VA_VIRAL_CLIP_END),
    "E001_VB": (VB_VIRAL_CLIP_START, VB_VIRAL_CLIP_END),
    "E001_VC": (VC_VIRAL_CLIP_START, VC_VIRAL_CLIP_END),
    "E001_VD": (VD_VIRAL_CLIP_START, VD_VIRAL_CLIP_END),
}


def build_audition_pack() -> EpisodeCueSheet:
    """Build AUDITION_GLOBAL_EDGE (15 cues) exercising ALL 8 locked roles & Gates G1–G8."""
    acts = [
        act_spec(
            "act1",
            "全口音与双语飙戏试听总览（G1–G8 声纹/声场/慢拆/同传全门禁验收）",
            "ost_boardroom_cold_open",
        )
    ]

    cues = [
        motif_cue(
            "aud_001",
            "act1",
            "glass_boardroom_door",
            placement="sequential",
            gap_after_s=0.18,
            gain_db=-3.0,
            director_note="G6/G8: 沙丘路玻璃门开场 Foley",
        ),
        en_boardroom(
            "aud_002",
            "act1",
            "victoria_vance",
            "[icy polite] That is a charming deck, Lin, truly. [coldly] Now walk me through the eighty million that just flowed through into the income statement before my partners lose patience.",
            subtitle_translation="很漂亮的路演文稿，林，真的。现在在我合伙人失去耐心之前，给我解释清楚刚流进利润表的那八千万美元。",
            gap_after_s=-0.15,
            director_note="G2/G4/G6: 硅谷美音女合伙人 + -0.15s 负间隔接抢话",
        ),
        en_boardroom(
            "aud_003",
            "act1",
            "lin_chen",
            "[interrupting] [measured] That eighty-million-dollar loss is a phantom number—not a cash loss, and your diligence team already knows it.",
            subtitle_translation="那八千万美元亏损纯粹是个幽灵数字——不是现金亏损，你们尽调团队早就心知肚明。",
            stability=0.0,
            gap_after_s=0.22,
            director_note="G1/G4/G6: 林沉公开硅谷英文（同一真人双语锚点）",
        ),
        zh_inner_monologue(
            "aud_004",
            "act1",
            "[aside] 她把可转债重估包装成经营失血，不是看不懂财报，是想趁签约前把估值砍掉三成。",
            gap_after_s=0.28,
            director_note="G1/G6: 林沉贴麦中文 inner_monologue（零混响、验证跨语种音色一致）",
        ),
        en_boardroom(
            "aud_005",
            "act1",
            "alistair_finch",
            "[understated] [clears throat] Oxford Street shoppers do not subsidize your cloud bill, Mr. Chen. [icy polite] Tell me what is good enough, and what it costs to run this thing a million times without eating into budgets.",
            subtitle_translation="牛津街顾客不会替你的云端账单买单，陈先生。告诉我做到什么线算够用，以及把这东西跑一百万次又不啃噬预算要花多少钱。",
            gap_after_s=0.25,
            director_note="G2/G4: 伦敦 RP 男中低音（与 Victoria 美音 3 秒听觉区隔）",
        ),
        en_boardroom(
            "aud_006",
            "act1",
            "claire_chen_gc",
            "[blunt] Do not sign that bridge sheet without a hard indemnity cap, Lin. [firmly] Victoria buried a super voting strip on page fourteen, and she is banking on you being too exhausted to notice.",
            subtitle_translation="没有硬性赔偿上限别签那份过桥协议，林。维多利亚在第十四页埋了超级投票权条款，就赌你熬得太累没看见。",
            gap_after_s=0.25,
            director_note="G4: Claire Sterling 纽约法务快节奏美音",
        ),
        zh_en_backroom(
            "aud_007",
            "act1",
            "zhou_mo",
            "[deadpan] [sighs] 产线刚把微显示模组的 BOM cost 压掉十八美金，硅谷那边又要为公有云 token 账单多烧三十块。[blunt] 听好了，明天切回本地 NPU 推理，不然卖一台亏一台。",
            language_code="zh-en",
            acoustic_space="phone_call",
            gap_after_s=0.25,
            director_note="G6/G7: 周默 phone_call 电话带通 + zh-en 双脚本 ASR 验收",
        ),
        en_boardroom(
            "aud_008",
            "act1",
            "rajiv_menon",
            "[measured] At twenty-five percent tariff, your Shenzhen base cost no longer clears our North American hurdle rate. [blunt] Qualify a Vietnam assembly line by Friday, or we reallocate the entire fourth-quarter order.",
            subtitle_translation="按百分之二十五关税算，你们深圳基础成本已过不了我们北美门槛。周五前通过越南产线认证，否则我们重分整个四季度订单。",
            similarity_boost=0.82,
            gap_after_s=0.25,
            director_note="G3: 印度裔高管国际客串清晰度验收（仅限试听包与 E013）",
        ),
        en_boardroom(
            "aud_009",
            "act1",
            "wei_ling_tan",
            "[measured] Ignore the polite modulations coming out of Washington and Brussels, Lin. [guarded] Sovereign capital does not invest in geopolitics—we invest in teams pragmatically adjusting before everyone else.",
            subtitle_translation="别管华盛顿和布鲁塞尔的客套风向，林。主权资本不投地缘政治——我们只投比所有人都更快务实调整的团队。",
            similarity_boost=0.82,
            gap_after_s=0.25,
            director_note="G3: 新加坡主权基金客串清晰度验收（仅限试听包与 E013/E016）",
        ),
        en_boardroom(
            "aud_010",
            "act1",
            "henrik_lindqvist",
            "[measured] Under European law, a prompt policy is a polite wish, not an enforcement mechanism. [coldly] Prove strict European data residency on Frankfurt metal, or your glasses never clear customs.",
            subtitle_translation="在欧洲法律下，提示词政策只是礼貌愿望，不是强制执行机制。拿出法兰克福本地物理机数据留存证明，否则眼镜永不通关。",
            similarity_boost=0.82,
            acoustic_space="vast_hall",
            gap_after_s=0.28,
            director_note="G3/G6: 欧盟法务客串 + vast_hall 听证会声场验收（仅限试听包与 E011）",
        ),
        *ducked_en_pair(
            "aud_011",
            "aud_012",
            "act1",
            "victoria_vance",
            "[understated] You pitched tremendous three-year subscription upside in that room, Lin—so answer the only question that matters: when are you going to get it?",
            "lin_chen",
            "[aside] 同传叠音测试：在沙丘路谈估值，画再大的远期上行空间都没用，投资人只盯现金到底哪年落袋。",
            en_acoustic_space="boardroom",
            zh_acoustic_space="studio_warm",
            duck_lead_in_s=3.5,
            duck_gain=0.15,
            zh_language_code="zh",
            zh_gap_after_s=0.28,
            en_subtitle_translation="你在那间屋里画了巨大的三年订阅上行空间，林——那就回答唯一重要的问题：你到底什么时候拿到这笔钱？",
            en_director_note="G6/G8: duck_under_next 同传原声独奏 3.5s -> 0.15 压混验收",
            zh_director_note="G6/G8: studio_warm 中文同传叠音轨 + 双行 SRT 验证",
        ),
        motif_cue(
            "aud_013",
            "act1",
            "smart_glasses_haptic_ping",
            placement="sequential",
            gap_after_s=0.20,
            gain_db=-3.5,
            director_note="G5/G8: 切入 Act 5 0.80x 慢拆与原速跟读测试",
        ),
        *slow_drill_pair(
            "aud_014",
            "aud_015",
            "act1",
            "lin_chen",
            "[coach] Pick your favorite number—10 times the throughput wins when you run this thing a million times.",
            subtitle_translation="参数随便你挑——把这东西跑一百万次时，十倍吞吐量才是硬道理。",
            acoustic_space="dry",
            slow_rate=0.8,
            slow_gap_s=0.70,
            shadow_gap_s=2.2,
            director_note_slow="G5: 0.80x atempo 保音高慢拆验收（dry 零混响）",
            director_note_native="G5: 1.0x 原速跟读 + 2.2s 留白验收",
        ),
    ]

    return EpisodeCueSheet(
        episode_id="AUDITION_GLOBAL_EDGE",
        chapter_number=0,
        title="《跨境底牌：硅深暗战》全口音与双语飙戏试听包（8 角色 · G1–G8 验收）",
        mode="audition_pack",
        source_chapter_file="voice_casting_registry.json#G1-G8",
        head_pad_s=0.25,
        tail_pad_s=0.80,
        acts=acts,
        cues=cues,
    )


def compute_pairwise_distinctiveness(
    variant_sheets: dict[str, EpisodeCueSheet],
) -> dict[str, float]:
    """Return pairwise Jaccard similarity of normalized Drama Acts 1-4 dialogue lines across variants."""
    sets_by_id: dict[str, set[str]] = {}
    for vid, sheet in variant_sheets.items():
        norm_lines: set[str] = set()
        for c in sheet.cues:
            if c.kind == "dialogue" and c.act_id in DRAMA_ACT_IDS:
                _, spoken = extract_tags_and_spoken_text(c.text)
                norm_lines.add(" ".join(spoken.lower().split()))
        sets_by_id[vid] = norm_lines

    out: dict[str, float] = {}
    for a, b in itertools.combinations(sorted(variant_sheets.keys()), 2):
        sa, sb = sets_by_id[a], sets_by_id[b]
        inter = len(sa & sb)
        union = len(sa | sb)
        out[f"{a}_vs_{b}"] = round(inter / union, 4) if union else 0.0
    return out


def render_comparative_eval_rubric_md(
    metrics_by_id: dict[str, dict[str, Any]],
    clip_durations: dict[str, dict[str, Any]],
    pairwise_sim: dict[str, float],
) -> str:
    """Dynamically render `E001_COMPARATIVE_EVAL_RUBRIC.md` from LIVE computed telemetry."""
    va = metrics_by_id["E001_VA"]
    vb = metrics_by_id["E001_VB"]
    vc = metrics_by_id["E001_VC"]
    vd = metrics_by_id["E001_VD"]

    def _pct(x: float) -> str:
        return f"{x * 100:.1f}%"

    def _mmss(sec: float) -> str:
        m = int(sec // 60)
        s = int(round(sec - m * 60))
        if s == 60:
            m += 1
            s = 0
        return f"{m:02d}:{s:02d}"

    lines = [
        "# 《跨境底牌：硅深暗战》E001 四变体对比评测矩阵与 100 分盲听打分表",
        "",
        "> **自动生成声明**：本文件第 1 节的所有结构与时长指标均由 `projects/global_edge/scripts/build_e001_variants.py` 直接从 `E001_VA`、`E001_VB`、`E001_VC`、`E001_VD` 四个已校验 `.json` 台本实时计算生成，确保 100% 账实相符。",
        "> **共同控制变量**：四版共享同一商业危机（`$150M` C 轮 / `$1.2B` 投前 / `$80M` GAAP 可转债账面亏损 / 伦敦云端算力毛利围剿 / 第 14 页 60 天 5 万台董事会否决权暗雷）、同一核心 5 角色（**100% 核心美音 + 伦敦 RP，0 国际客串口音**）、同一 5 条种子语料（`02_BIZ_Anthropic`、`012_AI`、`039_BIZ`、`090_USC`、`059_FIN`）与全部 **8 组（13 条精确子短语）** 强制高管表达。",
        "",
        "---",
        "",
        "## 一、 渲染前自动化量化对比矩阵（实时脚本实测）",
        "",
        "| 维度 / 指标 | `E001_VA`（HBO纯飙戏冷峻商战版） | `E001_VB`（纸牌屋冻帧潜台词狙击版） | `E001_VC`（三时区惊悚推进与实战跟读版） | `E001_VD`（纪实同传叠音混合版） | 工程硬门槛 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
        f"| **总 Cue 数（对白 / SFX）** | `{va['total_cues']}`（`{va['dialogue_cues']}` / `{va['sfx_cues']}`） | `{vb['total_cues']}`（`{vb['dialogue_cues']}` / `{vb['sfx_cues']}`） | `{vc['total_cues']}`（`{vc['dialogue_cues']}` / `{vc['sfx_cues']}`） | `{vd['total_cues']}`（`{vd['dialogue_cues']}` / `{vd['sfx_cues']}`） | `VA/VB/VD` 精炼，`VC SFX >= 13` |",
        f"| **总预估时长（经验值 / dry-test）** | `{va['total_duration_est_s']}s` (`{_mmss(va['total_duration_est_s'])}`) / `{va['synth_total_duration_est_s']}s` | `{vb['total_duration_est_s']}s` (`{_mmss(vb['total_duration_est_s'])}`) / `{vb['synth_total_duration_est_s']}s` | `{vc['total_duration_est_s']}s` (`{_mmss(vc['total_duration_est_s'])}`) / `{vc['synth_total_duration_est_s']}s` | `{vd['total_duration_est_s']}s` (`{_mmss(vd['total_duration_est_s'])}`) / `{vd['synth_total_duration_est_s']}s` | **`600–840s`** (`10–14 min`) |",
        f"| **正片 Acts 1–4 时长（经验 / dry）** | `{va['drama_duration_est_s']}s` / `{va['synth_drama_duration_est_s']}s` | `{vb['drama_duration_est_s']}s` / `{vb['synth_drama_duration_est_s']}s` | `{vc['drama_duration_est_s']}s` / `{vc['synth_drama_duration_est_s']}s` | `{vd['drama_duration_est_s']}s` / `{vd['synth_drama_duration_est_s']}s` | **`480–600s`** (`8–10 min`) |",
        f"| **片尾 Act 5 拆局时长（经验 / dry）** | `{va['debrief_duration_est_s']}s` / `{va['synth_debrief_duration_est_s']}s` | `{vb['debrief_duration_est_s']}s` / `{vb['synth_debrief_duration_est_s']}s` | `{vc['debrief_duration_est_s']}s` / `{vc['synth_debrief_duration_est_s']}s` | `{vd['debrief_duration_est_s']}s` / `{vd['synth_debrief_duration_est_s']}s` | **`165–210s`** (`~3 min`) |",
        f"| **正片英/中对白时长占比** | **`{_pct(va['drama_en_ratio'])}`** EN / `{_pct(va['drama_zh_ratio'])}` ZH | **`{_pct(vb['drama_en_ratio'])}`** EN / `{_pct(vb['drama_zh_ratio'])}` ZH | **`{_pct(vc['drama_en_ratio'])}`** EN / `{_pct(vc['drama_zh_ratio'])}` ZH | **`{_pct(vd['drama_en_ratio'])}`** EN / `{_pct(vd['drama_zh_ratio'])}` ZH | `VA 65-75% / VB 50-60% / VC 55-65% / VD 50-60%` |",
        f"| **负间隔抢话次数 (`[-0.25, -0.05]s`)** | `{va['crosstalk_count']}` | `{vb['crosstalk_count']}` | `{vc['crosstalk_count']}` | `{vd['crosstalk_count']}` | `VA>=6 / VB>=4 / VC>=6 / VD>=3` |",
        f"| **纸牌屋冻帧 `inner_monologue` 次数** | `{va['inner_monologue_count']}` | **`{vb['inner_monologue_count']}`**（全配 `freeze_frame_sub_drop`） | `{vc['inner_monologue_count']}` | `{vd['inner_monologue_count']}` | `VA=0 / VB>=6 / VC=0` |",
        f"| **跨洋电话 `phone_call` 次数** | `{va['phone_call_count']}` | `{vb['phone_call_count']}` | **`{vc['phone_call_count']}`** | `{vd['phone_call_count']}` | `VC >= 4` |",
        f"| **纪实同传 `duck_under_next` 对数** | `{va['duck_under_next_count']}` | `{vb['duck_under_next_count']}` | `{vc['duck_under_next_count']}` | **`{vd['duck_under_next_count']}`**（`3.6–4.0s` -> `0.15`） | `VD >= 2`（不连环嵌套） |",
        f"| **Act 5 `0.80x` 慢拆 / `1.0x` 跟读留白(`>=2.0s`)** | `{va['act5_slow_count']}` / `{va['act5_shadow_gap_2s_count']}` | `{vb['act5_slow_count']}` / `{vb['act5_shadow_gap_2s_count']}` | `{vc['act5_slow_count']}` / `{vc['act5_shadow_gap_2s_count']}` | `{vd['act5_slow_count']}` / `{vd['act5_shadow_gap_2s_count']}` | 均 `>= 3` 且留白 `>= 2.0s` |",
        f"| **Act 5 拆局形态与出镜角色** | 林沉单人贴麦（`{', '.join(va['act5_roles'])}`） | 高速后座双人拆局（`{', '.join(vb['act5_roles'])}`） | 反派原声盲打+慢拆（`{', '.join(vc['act5_roles'])}`） | 四连闪卡+E002预告（`{', '.join(vd['act5_roles'])}`） | 四版形态零雷同 |",
        f"| **8 组强制高管表达覆盖（正片 EN）** | **`{va['mandatory_phrase_groups_hit']}/{va['mandatory_phrase_groups_total']}`** | **`{vb['mandatory_phrase_groups_hit']}/{vb['mandatory_phrase_groups_total']}`** | **`{vc['mandatory_phrase_groups_hit']}/{vc['mandatory_phrase_groups_total']}`** | **`{vd['mandatory_phrase_groups_hit']}/{vd['mandatory_phrase_groups_total']}`** | `8/8`（13/13 子短语） |",
        f"| **核心美音+伦敦 RP 占比（EN 句）** | **`{va['core_us_uk_en_pct']}%`** | **`{vb['core_us_uk_en_pct']}%`** | **`{vc['core_us_uk_en_pct']}%`** | **`{vd['core_us_uk_en_pct']}%`** | `100.0%`（0 国际客串） |",
        f"| **禁词套话 / 仙侠 Drama 3 提示词泄露** | `{va['banned_cliche_count']}` / `{va['xianxia_drama3_leak_count']}` | `{vb['banned_cliche_count']}` / `{vb['xianxia_drama3_leak_count']}` | `{vc['banned_cliche_count']}` / `{vc['xianxia_drama3_leak_count']}` | `{vd['banned_cliche_count']}` / `{vd['xianxia_drama3_leak_count']}` | **双零 (`0 / 0`)** |",
        f"| **45 秒爆款切片区间与实测时长** | `{clip_durations['E001_VA']['start']}..{clip_durations['E001_VA']['end']}` (**`{clip_durations['E001_VA']['duration_s']}s`**) | `{clip_durations['E001_VB']['start']}..{clip_durations['E001_VB']['end']}` (**`{clip_durations['E001_VB']['duration_s']}s`**) | `{clip_durations['E001_VC']['start']}..{clip_durations['E001_VC']['end']}` (**`{clip_durations['E001_VC']['duration_s']}s`**) | `{clip_durations['E001_VD']['start']}..{clip_durations['E001_VD']['end']}` (**`{clip_durations['E001_VD']['duration_s']}s`**) | 严格落入 **`38–55s`** |",
        "",
        "### 四变体剧本原创度校验（正片对白两两 Jaccard 相似度）",
        "",
        "| 对比组合 | 正片对白 Jaccard 重合度 | 判定 |",
        "| :--- | :---: | :---: |",
    ]
    for pair_key, score in sorted(pairwise_sim.items()):
        verdict = "PASS（完全独立重写，零复制克隆）" if score < 0.15 else "CHECK"
        lines.append(f"| `{pair_key}` | `{score:.4f}` | {verdict} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## 二、 100 分盲听对比评分标准（Synced with `SHOW_BIBLE.md` §5.3）",
            "",
            "Colab 96GB 渲染出四版 `-16 LUFS` 立体声母带后，评测人必须在不看变体编号的前提下按以下 **7 大加权维度（合计 100 分）** 独立打分：",
            "",
            "| 编号 | 评测维度 | 权重分值 | 满分锚点（Top-Level 标准） | 扣分红线（一票拉低） |",
            "| :---: | :--- | :---: | :--- | :--- |",
            "| **D1** | **前 30 秒黄金钩子与通勤留存欲** | **15** | 0–3 秒立刻进入高利害冲突（金额/立场/气压一步到位），戴上耳机 30 秒内绝不想划走 | 出现慢吞吞寒暄、背景铺陈超 20 秒或播音主持开场白 |",
            "| **D2** | **HBO 商战真实感与反播音腔指数** | **20** | 冷峻克制、礼貌带刀、真实高管呼吸停顿与打断抢话，完全听不出 AI 朗读或英语老师说教味 | 夸张咆哮、廉价捧哏、教材念课文语调或“视频号/YouTube”破壁词 |",
            "| **D3** | **英美口音权威度与自然语速控制** | **15** | 硅谷/纽约美音与伦敦 RP 3 秒清晰区隔，正片稳居 `150–185 WPM`，重音连读有高管压迫感 | 美音/英音混漂、`[wryly]` 乡土漂移或慢吞吞 `120 WPM` ESL 语速 |",
            "| **D4** | **双语无缝流转与潜台词翻译爽感** | **15** | 英文原话锋芒不减、中文切入零割裂，B1–B2 听众不看字幕也能秒懂潜台词并感到过瘾 | 生硬逐句翻译腔、中文打断正片爽感或 `zh-en` 混读吐字糊词 |",
            "| **D5** | **教学留存与 24 小时主动回忆度** | **15** | Act 5 拆局把“中式直译 vs 高管原话”打进肌肉记忆，`0.80x` 慢拆保音高、`1.0x` 跟读留白刚好张口复述 | `0.80x` 出现音高下沉/金属伪影、跟读留白 `< 1.8s` 来不及开口 |",
            "| **D6** | **45 秒视频号/Shorts 爆款切片穿透力** | **10** | 从正片直切 `38–55s` 无需补录即构成独立反转冲突，静音看双语字幕 3 秒也能停滑评论 | 切片前后依赖长背景、金句分散在 90 秒以上无法独立成片 |",
            "| **D7** | **电影级声场质感与三总线混音舒适度** | **10** | `boardroom` / `inner_monologue` / `phone_call` / `studio_warm` 声场辨识分明，OST 压混通透，连续听 14 分钟零耳疲劳 | 抢话爆音、BGM 盖过人声、`inner_monologue` 带洞穴混响或响度飘出 `-16 ± 0.5 LUFS` |",
            "| **合计** | **综合总分** | **100** | — | — |",
            "",
            "---",
            "",
            "## 三、 盲听打分工作表（Track 1–4 匿名随机评测）",
            "",
            "### 3.1 盲听洗牌与执行协议",
            "1. **制作人洗牌**：由执行人将渲染后的 4 支 MP3（`E001_VA` / `E001_VB` / `E001_VC` / `E001_VD`）随机重命名为 `Track_01.mp3` ～ `Track_04.mp3`，把映射密钥锁入独立文档，评测期间对打分人严格保密。",
            "2. **真实场景测试**：建议招募 **3–5 名目标受众**（含科技/外企 B1–B2 与金融/出海 B2–C1 听众），在真实通勤降噪耳机环境下，不看台本完整盲听，并在 **24 小时后** 完成第 3.3 节无提示回忆测试。",
            "3. **听感记录**：每听完一轨立即独立填表，全部四轨听毕并打分完毕后再揭盲对照。",
            "",
            "### 3.2 Track 1–4 匿名打分表",
            "",
            "| 评测维度（满分） | `Track 1` | `Track 2` | `Track 3` | `Track 4` | 评委关键听感批注（最炸瞬间 / 掉线时间戳） |",
            "| :--- | :---: | :---: | :---: | :---: | :--- |",
            "| **D1 前 30 秒钩子** (`15`) | / 15 | / 15 | / 15 | / 15 | |",
            "| **D2 HBO 商战真实感** (`20`) | / 20 | / 20 | / 20 | / 20 | |",
            "| **D3 口音权威度与语速** (`15`) | / 15 | / 15 | / 15 | / 15 | |",
            "| **D4 双语流转与潜台词** (`15`) | / 15 | / 15 | / 15 | / 15 | |",
            "| **D5 教学留存与 24h 回忆** (`15`) | / 15 | / 15 | / 15 | / 15 | |",
            "| **D6 45s 爆款切片潜力** (`10`) | / 10 | / 10 | / 10 | / 10 | |",
            "| **D7 声场质感与混音舒适** (`10`) | / 10 | / 10 | / 10 | / 10 | |",
            "| **总分（100）** | **/ 100** | **/ 100** | **/ 100** | **/ 100** | |",
            "| **揭盲后对应变体** | `VA / VB / VC / VD` | `VA / VB / VC / VD` | `VA / VB / VC / VD` | `VA / VB / VC / VD` | |",
            "",
            "### 3.3 24 小时延迟主动回忆检验（对应 D5 实证分）",
            "盲听结束 **24 小时后**，向受试者仅给出左侧中文商战场景，检验其能否不看讲义脱口说出对应高管英语杀招（8 组命中 `>= 5` 组为优秀，`>= 6` 组为顶级）：",
            "",
            "| # | 24 小时后无提示场景触发词 | 目标回忆高管原话 | 命中标记 (`✓ / ✗`) |",
            "| :-: | :--- | :--- | :---: |",
            "| 1 | 戳破会计准则导致的八千万账面巨亏 | `phantom number` | `[ ]` |",
            "| 2 | 切割账面重估传导进利润表 vs 真金白银流失 | `flowed through into the income statement` / `not a cash loss` | `[ ]` |",
            "| 3 | 证明每一美元融资效率远超烧钱同行 | `capital-efficient` | `[ ]` |",
            "| 4 | 芯片单价随便调、十倍吞吐量降维碾压 | `Pick your favorite number` / `10 times the throughput` | `[ ]` |",
            "| 5 | 董事会瞬间把复杂数据“翻译成人话” | `In other words` | `[ ]` |",
            "| 6 | 欧美买手体面压价：算力啃噬预算、残酷权衡 | `eating into budgets` / `a really hard trade-off` | `[ ]` |",
            "| 7 | 撕碎跑分滤镜：够用底线 + 跑一百万次成本 | `What is good enough` / `run this thing a million times` | `[ ]` |",
            "| 8 | 拆穿远期上行画饼：钱到底哪年到账 | `upside` / `When are you going to get it` | `[ ]` |",
            "",
            "---",
            "",
            "## 四、 混合胜出者合成规则（锁定 `E002–E024` 工业定型模板）",
            "",
            "为了避免“四不像拼盘”破坏节奏或超预算，正式启动 `E002–E024` 批量生产前，严格执行 **Hybrid-Winner Synthesis Rule（混合胜出者合成法则）**：",
            "",
            "1. **第一名定骨架**：100 分盲听总分排名 **#1** 的变体直接成为第一季 `E002–E024` 的**主叙事骨架、正片英中比例基线与声场主模板**。",
            "2. **最多吸收 2 项模块化优势机制**：可从排名 **#2 / #3** 的单项高分维度中，**至多吸收 2 项独立可插拔机制**（禁止超过 2 项），例如：",
            "   - 若 **`E001_VA`** 综合夺冠（HBO 真实感最高），但 **`E001_VB`** 在 D4（潜台词）领跑、**`E001_VC`** 在 D5（反派原声盲打）领跑 → 可在 `VA` 骨架中每集限插 `2–3` 次 `freeze_frame_sub_drop + inner_monologue` 关键点睛，并采用 `VC` 的 Act 5 反派冷突袭跟读模块。",
            "   - 若 **`E001_VB`** 综合夺冠（B1–B2 潜台词爽感最高），但 **`E001_VC`** 在 D1（三时区前 30 秒钩子）领跑、**`E001_VD`** 在 Act 5 下集预告拉动追更最高 → 保留 `VB` 冻帧与双人复盘骨架，吸收 `VC` 的冷开场三时区跨切与 `VD` 的 30 秒下集预告。",
            "   - 若 **`E001_VD`** 综合夺冠（通勤零阻力同传最高），则保留 `duck_under_next=True`（每集 `2–4` 对，严禁连续嵌套），吸收 `VA` 更高密度的董事会负间隔抢话（`>= 6` 次）。",
            "3. **硬边界绝不妥协**：合成后的 `E002–E024` 定型模板必须继续 100% 满足：`600–840s` 总时长、`480–600s` 正片、`165–210s` Act 5 拆局（含 `0.80x` 慢拆 + `1.0x >= 1.8s` 留白）、第一季整体 `>= 85%` 美音+伦敦 RP、`0` 播音腔/禁词、`0` 仙侠提示词泄露。",
            "",
        ]
    )
    return "\n".join(lines)


def run_build(
    *,
    out_dir: Path,
    rubric_out: Path | None,
    check_only: bool,
) -> dict[str, Any]:
    registry = VoiceCastingRegistry.load(REGISTRY_PATH)

    errors: list[str] = []
    # 1. Verify OST & Sonic Motifs byte-for-byte sync with SHOW_BIBLE.md & registry
    sync_errs = verify_sync_with_bible_and_registry(registry, SHOW_BIBLE_PATH)
    for e in sync_errs:
        errors.append(f"[ost_motif_sync] {e}")

    # 2. Build all 5 cue sheets
    audition = build_audition_pack()
    variants: dict[str, EpisodeCueSheet] = {
        "E001_VA": build_e001_va(),
        "E001_VB": build_e001_vb(),
        "E001_VC": build_e001_vc(),
        "E001_VD": build_e001_vd(),
    }

    # 3. Validate Audition pack + all 4 E001 variants
    for e in lint_audition_pack(audition, registry):
        errors.append(f"[AUDITION_GLOBAL_EDGE] {e}")

    metrics_by_id: dict[str, dict[str, Any]] = {}
    clip_durations: dict[str, dict[str, Any]] = {}
    for vid, sheet in variants.items():
        for e in lint_e001_variant(sheet, registry, vid):
            errors.append(f"[{vid}] {e}")
        metrics_by_id[vid] = compute_variant_metrics(sheet, registry)
        c_start, c_end = VIRAL_CLIP_RANGES[vid]
        c_dur = estimate_cue_range_duration_s(sheet, c_start, c_end)
        clip_durations[vid] = {"start": c_start, "end": c_end, "duration_s": c_dur}
        if not (38.0 <= c_dur <= 55.0):
            errors.append(
                f"[{vid}] viral clip range {c_start}..{c_end} duration={c_dur}s outside [38.0, 55.0]s"
            )

    # 4. Pairwise distinctiveness guard (anti-cloning across variants)
    pairwise_sim = compute_pairwise_distinctiveness(variants)
    for pair_key, sim in pairwise_sim.items():
        if sim > 0.20:
            errors.append(
                f"[distinctiveness] {pair_key} Jaccard={sim} > 0.20 (variants too similar)"
            )

    rubric_md = render_comparative_eval_rubric_md(metrics_by_id, clip_durations, pairwise_sim)

    written_files: list[str] = []
    if not check_only and not errors:
        out_dir.mkdir(parents=True, exist_ok=True)
        all_sheets: dict[str, EpisodeCueSheet] = {"AUDITION_GLOBAL_EDGE": audition, **variants}
        for ep_id, sheet in all_sheets.items():
            stem = OUTPUT_FILENAMES[ep_id]
            json_path = out_dir / f"{stem}.json"
            md_path = out_dir / f"{stem}.md"
            sheet.save(json_path)
            write_cue_sheet_markdown(sheet, md_path, registry=registry)
            written_files.extend([str(json_path), str(md_path)])

        target_rubric = rubric_out or (out_dir / "E001_COMPARATIVE_EVAL_RUBRIC.md")
        target_rubric.parent.mkdir(parents=True, exist_ok=True)
        target_rubric.write_text(rubric_md, encoding="utf-8")
        written_files.append(str(target_rubric))

    return {
        "ok": len(errors) == 0,
        "check_only": check_only,
        "error_count": len(errors),
        "errors": errors,
        "audition_cues": len(audition.cues),
        "metrics": metrics_by_id,
        "viral_clips": clip_durations,
        "pairwise_similarity": pairwise_sim,
        "written_files": written_files,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build & validate Global Edge AUDITION + E001_VA/VB/VC/VD cue sheets and rubric."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Output directory for JSON/MD cue sheets (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument(
        "--rubric-out",
        type=Path,
        default=None,
        help="Optional explicit output path for E001_COMPARATIVE_EVAL_RUBRIC.md",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run all validations in memory without writing any files",
    )
    args = parser.parse_args(argv)

    report = run_build(
        out_dir=args.out_dir,
        rubric_out=args.rubric_out,
        check_only=args.check_only,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
