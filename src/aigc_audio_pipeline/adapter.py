"""Novel chapter analyzer & human-readable director script exporter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .models import EpisodeCueSheet, VoiceCastingRegistry

_QUOTE_SPLIT = re.compile(r"(“[^”]+”)")
_PURE_SPEAKER_TAG = re.compile(
    r"^\s*(?:[^，,。！？“”]{1,14}?)"
    r"(?:低声道|淡声道|平静道|哑声道|冷声道|温声道|沉声道|冷笑道|怒声道|急声道|失声道|瓮声道|颤声道|厉声道|狞声道|"
    r"咬牙切齿道|瓮声瓮气道|压低声音道|压低嗓音道|压低嗓门道|沙哑冷笑道|沙哑道|平静开口|沙哑开口|淡淡开口|"
    r"低声问道|淡声问道|沉声问道|追问了一句|开口道|问道|答道|说道|"
    r"低声说|轻声说|平静地说|冷冷地说|缓缓地说|一字一句地说|压低声音说|沙哑着嗓子说|面无表情地说|"
    r"反问道|追问道|回答道|解释道|补充道|补充说|提醒说|喃喃道|喃喃自语道|耳语道|嘶声喊道|大喊道|尖叫道|吼道|喊道|叫道|说)[：:]\s*$"
)
_SPEECH_VERB_TAIL = re.compile(
    r"[，,]\s*(?:压低声音|压低嗓音|压低嗓门|哑着嗓子|咬牙切齿|瓮声瓮气|斩钉截铁|慢条斯理|一字一句|似笑非笑|哭笑不得|痛心疾首|战战兢兢|连滚带爬|面无表情地|不动声色地|平静地|冷冷地|轻声|低声)?"
    r"(?:低声道|淡声道|平静道|哑声道|冷声道|温声道|沉声道|冷笑道|怒声道|急声道|失声道|瓮声道|颤声道|厉声道|狞声道|"
    r"低声问道|淡声问道|沉声问道|追问了一句|温声反问了一句|轻描淡写道|低声反问|厉声下令|厉声喝道|狞声喝道|嘶声喊道|"
    r"高声喊道|低声禀报|通禀道|复述道|补充道|提醒道|叮嘱道|吩咐道|应道|笑道|叹道|骂道|喝道|哭喊道|喃喃道|自语道|"
    r"开口道|沙哑开口|平静开口|淡淡开口|淡声吩咐|喃喃低语|低声自语道|"
    r"低声说|轻声说|平静地说|冷冷地说|缓缓地说|反问道|追问道|回答道|解释道|补充说|耳语道|尖叫道|大喊道|吼道|喊道|叫道|"
    r"问道|答道|说道|说|道)[：:]\s*$"
)
_INLINE_QUOTE_SUFFIXES = ("的", "二字", "三字", "四字", "五字", "六个字", "字样", "时，", "时,", "一词", "这个词")
_WRITTEN_INTRO_TAILS = ("写着：", "刻着：", "字痕：", "写有：", "写道：")


def is_spoken_dialogue_quote(prev_text: str, inner_quote: str, next_text: str) -> bool:
    """Return True if `“inner_quote”` is spoken dialogue rather than an inline scare-quote/term."""
    if not inner_quote.strip():
        return False
    prev_s = prev_text.rstrip()
    next_s = next_text.lstrip()
    if any(prev_s.endswith(w) for w in _WRITTEN_INTRO_TAILS):
        return False
    if any(next_s.startswith(sfx) for sfx in _INLINE_QUOTE_SUFFIXES):
        return False
    if prev_s and prev_s[-1] not in "：:，,。！？…—”":
        return False
    return True


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

        # Merge inline non-spoken scare-quotes ("血锁", "饲笼", etc.) back into narration first
        merged_tokens: list[tuple[str, str]] = []  # (kind, text)
        for idx, chunk in enumerate(parts):
            if idx % 2 == 1 and chunk.startswith("“") and chunk.endswith("”"):
                prev_txt = parts[idx - 1] if idx > 0 else ""
                next_txt = parts[idx + 1] if idx + 1 < len(parts) else ""
                inner = chunk[1:-1].strip()
                if is_spoken_dialogue_quote(prev_txt, inner, next_txt):
                    merged_tokens.append(("dialogue", inner))
                else:
                    if merged_tokens and merged_tokens[-1][0] == "narration":
                        merged_tokens[-1] = ("narration", merged_tokens[-1][1] + chunk)
                    else:
                        merged_tokens.append(("narration", chunk))
            else:
                if not chunk:
                    continue
                if merged_tokens and merged_tokens[-1][0] == "narration":
                    merged_tokens[-1] = ("narration", merged_tokens[-1][1] + chunk)
                else:
                    merged_tokens.append(("narration", chunk))

        if all(k == "narration" for k, _ in merged_tokens):
            full_narr = "".join(t for _, t in merged_tokens).strip()
            if full_narr:
                segments.append(ParsedSegment(p_idx, "narration", full_narr, "narrator"))
            continue

        narration_context = " ".join(t for k, t in merged_tokens if k == "narration")
        inferred_role = "unknown"
        for name_str, r_id in role_names:
            if name_str in narration_context:
                inferred_role = r_id
                break
        if inferred_role == "unknown":
            inferred_role = last_speaker

        for tok_idx, (kind, tok_text) in enumerate(merged_tokens):
            tok_text = tok_text.strip()
            if not tok_text:
                continue
            if kind == "dialogue":
                segments.append(ParsedSegment(p_idx, "dialogue", tok_text, inferred_role))
                if inferred_role != "unknown":
                    last_speaker = inferred_role
            else:
                has_following_dialogue = any(k == "dialogue" for k, _ in merged_tokens[tok_idx + 1 :])
                if has_following_dialogue:
                    cleaned = _PURE_SPEAKER_TAG.sub("", tok_text)
                    cleaned = _SPEECH_VERB_TAIL.sub("", cleaned).strip(" ，,：:")
                else:
                    cleaned = tok_text.strip(" ，,：:")
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
