"""Novel chapter analyzer & human-readable director script exporter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .models import EpisodeCueSheet, VoiceCastingRegistry

_QUOTE_SPLIT = re.compile(r"(“[^”]+”)")
_SPEECH_VERB_TAIL = re.compile(
    r"[，,：:\s]*(?:[^，。！？“”]{0,12}?)(?:低声道|淡声道|平静道|哑声道|冷声道|温声反问了一句|轻描淡写道|低声反问|沉声道|冷笑道|喝道|哭喊道|喃喃道|开口道|说道|道)[：:]\s*$"
)


@dataclass
class ParsedSegment:
    paragraph_index: int
    kind: str  # "narration" | "dialogue"
    text: str
    speaker_hint: str = "narrator"


def analyze_markdown_chapter(
    markdown_text: str,
    registry: VoiceCastingRegistry | None = None,
) -> dict[str, object]:
    """Parse a Chinese novel chapter into narrative & dialogue segments with speaker hints."""
    lines = [ln.strip() for ln in markdown_text.splitlines() if ln.strip()]
    title = ""
    body_paragraphs: list[str] = []
    for ln in lines:
        if ln.startswith("#") and not title:
            title = ln.lstrip("#").strip()
        else:
            body_paragraphs.append(ln)

    role_names: list[tuple[str, str]] = []
    if registry is not None:
        for role_id, prof in registry.roles.items():
            if role_id == "narrator":
                continue
            role_names.append((prof.display_name, role_id))
            for alias in prof.aliases:
                role_names.append((alias, role_id))
        # Sort longest name first so "苏清寒" matches before "苏"
        role_names.sort(key=lambda x: len(x[0]), reverse=True)

    segments: list[ParsedSegment] = []
    last_speaker = "unknown"
    for p_idx, para in enumerate(body_paragraphs, 1):
        parts = _QUOTE_SPLIT.split(para)
        if len(parts) == 1:
            segments.append(ParsedSegment(p_idx, "narration", para, "narrator"))
            continue

        # Infer speaker for quoted lines in this paragraph from attribution text
        narration_context = " ".join(parts[0::2])
        inferred_role = "unknown"
        for name_str, r_id in role_names:
            if name_str in narration_context:
                inferred_role = r_id
                break
        if inferred_role == "unknown":
            inferred_role = last_speaker

        for idx, chunk in enumerate(parts):
            chunk = chunk.strip()
            if not chunk:
                continue
            if idx % 2 == 1 and chunk.startswith("“") and chunk.endswith("”"):
                inner = chunk[1:-1].strip()
                if inner:
                    segments.append(ParsedSegment(p_idx, "dialogue", inner, inferred_role))
                    if inferred_role != "unknown":
                        last_speaker = inferred_role
            else:
                # Strip trailing redundant speech verb ("福伯低声道：") before an acted quote
                cleaned = _SPEECH_VERB_TAIL.sub("", chunk).strip(" ，,：:")
                if cleaned:
                    segments.append(ParsedSegment(p_idx, "narration", cleaned, "narrator"))

    char_counts: dict[str, int] = {}
    line_counts: dict[str, int] = {}
    for seg in segments:
        key = seg.speaker_hint if seg.kind == "dialogue" else "narrator"
        char_counts[key] = char_counts.get(key, 0) + len(seg.text)
        line_counts[key] = line_counts.get(key, 0) + 1

    return {
        "title": title,
        "paragraph_count": len(body_paragraphs),
        "segment_count": len(segments),
        "line_counts_by_role": line_counts,
        "char_counts_by_role": char_counts,
        "segments": segments,
    }


def export_cue_sheet_markdown(
    cue_sheet: EpisodeCueSheet,
    registry: VoiceCastingRegistry | None = None,
) -> str:
    """Render an EpisodeCueSheet into a clean, human-readable Director & Cast Script (.md)."""
    out: list[str] = [
        f"# {cue_sheet.episode_id} ·《{cue_sheet.title}》广播剧 / 多人精品有声剧演出台本",
        "",
        f"- **模式**：`{cue_sheet.mode}`",
        f"- **对应章节**：第 {cue_sheet.chapter_number} 章（源文件：`{cue_sheet.source_chapter_file or 'N/A'}`）",
        f"- **时间轴规则**：自然语速完整保留（片头留白 `{cue_sheet.head_pad_s}s`，片尾收束 `{cue_sheet.tail_pad_s}s`，严禁按旧时长裁尾）",
        "- **混音总线**：人声主轨（`-16 LUFS`） + 前景独立音效轨（不随对白闪避） + 分幕纯音乐床（对白下闪避至 `0.11`，气口回升至 `0.34`）",
        "",
    ]

    if cue_sheet.acts:
        out.append("## 一、 分幕配乐设计（ElevenLabs `music_v2_5` · `force_instrumental=true`）")
        out.append("")
        out.append("| 幕次 | 幕名 | 音乐提示词（Prompt） | 参考时长 | 对白闪避 / 空隙增益 |")
        out.append("| :--- | :--- | :--- | :---: | :---: |")
        for act in cue_sheet.acts:
            out.append(
                f"| `{act.act_id}` | {act.title} | `{act.bgm_prompt}` | {act.bgm_duration_s:.0f}s | "
                f"`{act.bgm_gain_speech}` / `{act.bgm_gain_gap}` |"
            )
        out.append("")

    out.append("## 二、 逐句演出与音效时间轴清单")
    out.append("")

    act_titles = {a.act_id: a.title for a in cue_sheet.acts}
    current_act = None
    for cue in cue_sheet.cues:
        if cue.act_id and cue.act_id != current_act:
            current_act = cue.act_id
            act_label = act_titles.get(current_act, current_act)
            out.append(f"### 【{current_act} · {act_label}】")
            out.append("")

        if cue.kind == "sfx":
            mode_badge = "叠加下一句起拍" if cue.placement == "overlay_next" else "独立顺播"
            motif_str = f"（复用母题 `{cue.motif_id}`）" if cue.motif_id else ""
            out.append(
                f"- 🔊 **`[{cue.cue_id}]` 音效 · {mode_badge}**{motif_str} "
                f"（时长 `{cue.duration_seconds}s` | 句后留白 `{cue.gap_after_s}s`）  \n"
                f"  Prompt: `{cue.sfx_prompt}`"
                + (f"  \n  *导演备注：{cue.director_note}*" if cue.director_note else "")
            )
        else:
            role_label = cue.role_id
            if registry is not None:
                prof = registry.resolve_role(cue.role_id)
                if prof is not None:
                    role_label = f"{prof.display_name} (`{cue.role_id}`)"
            space_badge = f" | 声场 `{cue.acoustic_space}`" if cue.acoustic_space != "dry" else ""
            out.append(
                f"- 🎙️ **`[{cue.cue_id}]` {role_label}** "
                f"（`stability={cue.stability}`{space_badge} | 句后气口 `{cue.gap_after_s}s`）  \n"
                f"  > {cue.text}"
                + (f"  \n  *导演备注：{cue.director_note}*" if cue.director_note else "")
            )
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def write_cue_sheet_markdown(
    cue_sheet: EpisodeCueSheet,
    output_md: Path,
    registry: VoiceCastingRegistry | None = None,
) -> Path:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(export_cue_sheet_markdown(cue_sheet, registry=registry), encoding="utf-8")
    return output_md
