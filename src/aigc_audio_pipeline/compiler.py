"""Precision Unabridged Novel-to-CueSheet Compiler for Multi-Cast Audio Drama.

Guarantees:
1. 100% unabridged novel prose coverage (`>= 96.5%` CJK character gate, excluding only
   standalone 1-line sound onomatopoeia converted into foreground SFX cues and pure
   redundant speaker attribution tags like `'福伯低声道：'`).
2. Exact 1-to-1 verification of spoken quotes against Director Blueprint `dialogue_specs`
   (using `is_spoken_dialogue_quote` to ignore inline emphasis/proper-noun quotes, plus
   optional `match` substring assertions to prevent speaker index drift).
3. Smart grouping of adjacent narration paragraphs (`<= max_narration_group_chars`) within
   the same `(act_id, acoustic_space)` without crossing foreground SFX boundaries.
4. Automatic dramatic narrator performance grading (`[dramatically]` + `stability=0.0` on
   combat/breakthrough/horror peaks, `[softly]` + `stability=0.5` on stealth/whispers,
   `[calmly]` + `stability=0.5` on act openings).
5. Automatic Xianxia & classical banker-numeral `tts_text` phonetic override injection via
   `compute_tts_text_override`, while preserving canonical literary `text` for `.srt`
   subtitles and Scribe v3 dual-reference ASR QA.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from .adapter import (
    _PURE_SPEAKER_TAG,
    _QUOTE_SPLIT,
    _SPEECH_VERB_TAIL,
    is_spoken_dialogue_quote,
    write_cue_sheet_markdown,
)
from .models import ActMusicSpec, EpisodeCueSheet, TimelineCue, VoiceCastingRegistry
from .polyphones import compute_tts_text_override

_CJK_RE = re.compile(r"[\u4e00-\u9fff]+")
_HIGH_INTENSITY_KEYWORDS = (
    "轰", "炸", "碎", "杀", "死", "血", "痛", "惊雷", "骇然", "暴退", "狂吼", "咆哮",
    "基因锁", "锁扣", "崩断", "古棺", "煞气", "寒意", "森然", "断刀", "贯入", "斩",
    "紫府", "窒息", "畸变", "倒灌", "冲破", "剧震", "死寂",
    "枪响", "爆头", "扳机", "尖叫", "惨叫", "触肢", "蜘蛛", "吞噬", "抹除", "坍塌",
    "警报", "剧痛", "过载", "引爆", "深渊", "核弹", "黑洞",
)
_WHISPER_KEYWORDS = (
    "悄无声息", "屏住呼吸", "微不可闻", "幽幽", "鬼火", "呢喃", "叹息",
    "低语", "耳语", "死一般寂静", "悄声",
)


def parse_chapter_paragraphs(md_path: Path) -> tuple[str, list[str]]:
    """Parse a Markdown chapter file into `(chapter_title, body_paragraphs)`."""
    lines = [ln.strip() for ln in md_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    title = ""
    paras: list[str] = []
    for ln in lines:
        if ln.startswith("#") and not title:
            title = ln.lstrip("#").strip()
        elif ln in ("---", "***", "___"):
            continue
        elif (ln.startswith("*（") and ln.endswith("）*")) or (ln.startswith("*(") and ln.endswith(")*")):
            continue
        else:
            paras.append(ln)
    return title, paras


def extract_spoken_quotes_in_chapter(paras: list[str]) -> list[tuple[int, int, str]]:
    """Return `(p_idx_1based, quote_idx_in_para_0based, inner_quote)` for all spoken quotes."""
    found: list[tuple[int, int, str]] = []
    for p_idx, para in enumerate(paras, 1):
        parts = _QUOTE_SPLIT.split(para)
        if len(parts) == 1:
            continue
        q_i = 0
        for idx, chunk in enumerate(parts):
            if idx % 2 == 1 and chunk.startswith("“") and chunk.endswith("”"):
                prev_txt = parts[idx - 1] if idx > 0 else ""
                next_txt = parts[idx + 1] if idx + 1 < len(parts) else ""
                inner = chunk[1:-1].strip()
                if is_spoken_dialogue_quote(prev_txt, inner, next_txt):
                    found.append((p_idx, q_i, inner))
                    q_i += 1
    return found


def compile_episode_cue_sheet(
    *,
    episode_id: str,
    chapter_number: int,
    source_md_path: Path,
    source_rel_path: str,
    registry: VoiceCastingRegistry,
    acts_blueprint: list[dict[str, Any]],
    dialogue_specs: list[dict[str, Any]],
    sfx_blueprint: list[dict[str, Any]],
    acoustic_ranges: list[tuple[int, int, str]] | None = None,
    skip_onomatopoeia_paras: set[int] | None = None,
    max_narration_group_chars: int = 260,
    min_cjk_coverage_ratio: float = 0.965,
) -> EpisodeCueSheet:
    """Compile and strictly validate a 100% unabridged multi-cast `EpisodeCueSheet`."""
    title, paras = parse_chapter_paragraphs(source_md_path)
    total_p = len(paras)
    skip_paras = skip_onomatopoeia_paras or set()
    acoustic_ranges = acoustic_ranges or []

    # 1. Verify quote count matches dialogue_specs 1-to-1
    chapter_quotes = extract_spoken_quotes_in_chapter(paras)
    if len(chapter_quotes) != len(dialogue_specs):
        detail = "\n".join(
            f"  #{i}: P{p}.{q}: {txt[:45]}" for i, (p, q, txt) in enumerate(chapter_quotes)
        )
        raise ValueError(
            f"[{episode_id}] Quote count mismatch! Chapter has {len(chapter_quotes)} spoken quotes, "
            f"but dialogue_specs has {len(dialogue_specs)} entries.\nDetected quotes:\n{detail}"
        )

    # Verify optional substring assertion on each dialogue_spec to prevent index shift bugs
    for i, ((p_idx, _q_i, q_txt), spec) in enumerate(zip(chapter_quotes, dialogue_specs)):
        expect_sub = spec.get("match", "")
        if expect_sub and expect_sub not in q_txt:
            raise ValueError(
                f"[{episode_id}] Dialogue spec #{i} mismatch at P{p_idx}: "
                f"expected substring {expect_sub!r}, got {q_txt!r}"
            )

    def _act_for_para(p_idx: int) -> str:
        chosen = acts_blueprint[0]["act_id"]
        for ab in acts_blueprint:
            if p_idx >= ab["start_p"]:
                chosen = ab["act_id"]
        return chosen

    def _space_for_para(p_idx: int) -> str:
        space = "dry"
        for s_p, e_p, sp_name in acoustic_ranges:
            if s_p <= p_idx <= e_p:
                space = sp_name
        return space

    sfx_before: dict[int, list[dict[str, Any]]] = {}
    sfx_after: dict[int, list[dict[str, Any]]] = {}
    for sfx in sfx_blueprint:
        ap = int(sfx["p"])
        pos = sfx.get("pos", "before")
        if pos == "after":
            sfx_after.setdefault(ap, []).append(sfx)
        else:
            sfx_before.setdefault(ap, []).append(sfx)

    acts = [
        ActMusicSpec(
            act_id=ab["act_id"],
            title=ab["title"],
            bgm_prompt=ab["bgm_prompt"],
            bgm_duration_s=float(ab.get("bgm_duration_s", 105.0)),
            bgm_gain_speech=float(ab.get("bgm_gain_speech", 0.11)),
            bgm_gain_gap=float(ab.get("bgm_gain_gap", 0.34)),
        )
        for ab in acts_blueprint
    ]

    # Build raw sequence of items before grouping adjacent narrator blocks
    raw_items: list[dict[str, Any]] = []
    q_cursor = 0
    for p_idx in range(1, total_p + 1):
        act_id = _act_for_para(p_idx)
        base_space = _space_for_para(p_idx)

        for sfx in sfx_before.get(p_idx, []):
            raw_items.append({"type": "sfx", "act_id": sfx.get("act_id", act_id), "sfx": sfx})

        if p_idx in skip_paras:
            for sfx in sfx_after.get(p_idx, []):
                raw_items.append({"type": "sfx", "act_id": sfx.get("act_id", act_id), "sfx": sfx})
            continue

        para = paras[p_idx - 1]
        parts = _QUOTE_SPLIT.split(para)
        if len(parts) == 1:
            raw_items.append(
                {
                    "type": "narration",
                    "p_idx": p_idx,
                    "act_id": act_id,
                    "space": base_space,
                    "text": para,
                    "can_merge": True,
                }
            )
        else:
            merged_tokens: list[tuple[str, str]] = []
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
                    raw_items.append(
                        {
                            "type": "narration",
                            "p_idx": p_idx,
                            "act_id": act_id,
                            "space": base_space,
                            "text": full_narr,
                            "can_merge": True,
                        }
                    )
            else:
                for tok_idx, (kind, tok_text) in enumerate(merged_tokens):
                    tok_text = tok_text.strip()
                    if not tok_text:
                        continue
                    if kind == "dialogue":
                        dspec = dialogue_specs[q_cursor]
                        q_cursor += 1
                        raw_items.append(
                            {
                                "type": "dialogue",
                                "p_idx": p_idx,
                                "act_id": act_id,
                                "space": dspec.get("space", base_space),
                                "text": tok_text,
                                "spec": dspec,
                            }
                        )
                    else:
                        has_following = any(k == "dialogue" for k, _ in merged_tokens[tok_idx + 1 :])
                        if has_following:
                            cleaned = _PURE_SPEAKER_TAG.sub("", tok_text)
                            cleaned = _SPEECH_VERB_TAIL.sub("", cleaned).strip(" ，,：:")
                            if cleaned and cleaned[-1] not in "。！？…—":
                                cleaned += "。"
                        else:
                            cleaned = tok_text.strip(" ，,：:")
                        if cleaned:
                            raw_items.append(
                                {
                                    "type": "narration",
                                    "p_idx": p_idx,
                                    "act_id": act_id,
                                    "space": base_space,
                                    "text": cleaned,
                                    "can_merge": False,
                                }
                            )

        for sfx in sfx_after.get(p_idx, []):
            raw_items.append({"type": "sfx", "act_id": sfx.get("act_id", act_id), "sfx": sfx})

    # 2. Group adjacent mergeable narration blocks within same (act_id, space)
    grouped_items: list[dict[str, Any]] = []
    for item in raw_items:
        if (
            item["type"] == "narration"
            and item.get("can_merge")
            and grouped_items
            and grouped_items[-1]["type"] == "narration"
            and grouped_items[-1].get("can_merge")
            and grouped_items[-1]["act_id"] == item["act_id"]
            and grouped_items[-1]["space"] == item["space"]
            and len(grouped_items[-1]["text"]) + len(item["text"]) <= max_narration_group_chars
        ):
            grouped_items[-1]["text"] = grouped_items[-1]["text"] + item["text"]
        else:
            grouped_items.append(dict(item))

    # 3. Materialize TimelineCues with automatic acting tags, stability & polyphones
    cues: list[TimelineCue] = []
    seen_acts: set[str] = set()
    for idx, item in enumerate(grouped_items, 1):
        act_id = item["act_id"]
        is_act_first_speech = act_id not in seen_acts and item["type"] in ("narration", "dialogue")
        if is_act_first_speech:
            seen_acts.add(act_id)

        next_act = grouped_items[idx]["act_id"] if idx < len(grouped_items) else None
        is_act_end = next_act is not None and next_act != act_id

        if item["type"] == "sfx":
            s = item["sfx"]
            motif_id = s.get("motif_id", "")
            sfx_prompt = s.get("sfx_prompt", "")
            dur = float(s.get("duration_seconds", 3.0))
            infl = float(s.get("prompt_influence", 0.55))
            if motif_id and motif_id in registry.sonic_motifs:
                m = registry.sonic_motifs[motif_id]
                sfx_prompt = sfx_prompt or m.sfx_prompt
                dur = float(s.get("duration_seconds", m.duration_seconds))
                infl = float(s.get("prompt_influence", m.prompt_influence))
            cues.append(
                TimelineCue(
                    cue_id=f"c{idx:03d}_sfx_{s.get('slug', 'fx')}",
                    act_id=act_id,
                    kind="sfx",
                    motif_id=motif_id,
                    sfx_prompt=sfx_prompt,
                    duration_seconds=dur,
                    prompt_influence=infl,
                    loop=False,
                    placement=s.get("placement", "sequential"),
                    gain_db=float(s.get("gain_db", 0.0)),
                    gap_after_s=float(
                        s.get("gap_after_s", 0.25 if s.get("placement", "sequential") == "sequential" else 1.2)
                    ),
                    director_note=s.get("note", ""),
                )
            )
        elif item["type"] == "narration":
            raw_txt = item["text"]
            intense = sum(1 for kw in _HIGH_INTENSITY_KEYWORDS if kw in raw_txt) >= 2
            whispery = any(kw in raw_txt for kw in _WHISPER_KEYWORDS) and not intense
            if intense:
                tagged = f"[dramatically] {raw_txt}"
                stab = 0.0
            elif whispery:
                tagged = f"[softly] {raw_txt}"
                stab = 0.5
            elif is_act_first_speech:
                tagged = f"[calmly] {raw_txt}"
                stab = 0.5
            else:
                tagged = raw_txt
                stab = 0.5
            cues.append(
                TimelineCue(
                    cue_id=f"c{idx:03d}_nar_p{item['p_idx']:03d}",
                    act_id=act_id,
                    kind="dialogue",
                    role_id="narrator",
                    text=tagged,
                    tts_text=compute_tts_text_override(tagged),
                    stability=stab,
                    similarity_boost=0.85,
                    acoustic_space=item["space"],
                    gap_after_s=0.65 if is_act_end else 0.28,
                    director_note=f"旁白叙事（声场：{item['space']}）",
                )
            )
        else:
            spec = item["spec"]
            role_id = spec["role_id"]
            prof = registry.resolve_role(role_id)
            if prof is None:
                raise ValueError(f"[{episode_id}] Unknown role_id={role_id!r}")
            tag_prefix = spec.get("tags", "").strip()
            raw_txt = item["text"]
            tagged = f"{tag_prefix} {raw_txt}".strip() if tag_prefix else raw_txt
            stab = float(spec.get("stability", prof.default_stability))
            cues.append(
                TimelineCue(
                    cue_id=f"c{idx:03d}_{role_id}_p{item['p_idx']:03d}",
                    act_id=act_id,
                    kind="dialogue",
                    role_id=role_id,
                    text=tagged,
                    tts_text=compute_tts_text_override(tagged),
                    stability=stab,
                    similarity_boost=0.85,
                    acoustic_space=item["space"],
                    gap_after_s=float(spec.get("gap_after_s", 0.65 if is_act_end else 0.32)),
                    director_note=spec.get("note", f"{prof.display_name}对白"),
                )
            )

    sheet = EpisodeCueSheet(
        episode_id=episode_id,
        chapter_number=chapter_number,
        title=title,
        mode="immersive_audiobook_drama",
        source_chapter_file=source_rel_path,
        head_pad_s=0.3,
        tail_pad_s=1.6,
        acts=acts,
        cues=cues,
    )

    # 4. Strict validation: Playbook v3 rules + locked voices + unabridged prose coverage
    errs = sheet.validate(registry=registry, require_locked_voices=True)
    if errs:
        raise ValueError(f"[{episode_id}] CueSheet validation failed:\n" + "\n".join(errs))

    src_cjk = "".join(
        "".join(_CJK_RE.findall(p))
        for i, p in enumerate(paras, 1)
        if i not in skip_paras
    )
    compiled_cjk = "".join(
        "".join(_CJK_RE.findall(c.text))
        for c in sheet.cues
        if c.kind == "dialogue"
    )
    ratio = len(compiled_cjk) / max(1, len(src_cjk))
    if ratio < min_cjk_coverage_ratio:
        raise ValueError(
            f"[{episode_id}] Unabridged prose check failed: compiled CJK={len(compiled_cjk)} "
            f"vs source={len(src_cjk)} ({ratio:.3%} < {min_cjk_coverage_ratio:.1%})"
        )

    return sheet


def save_episode_scripts(
    sheet: EpisodeCueSheet,
    scripts_dir: Path,
    registry: VoiceCastingRegistry,
) -> tuple[Path, Path]:
    """Save paired `.json` machine cue sheet and `.md` director script."""
    scripts_dir.mkdir(parents=True, exist_ok=True)
    clean_title = (
        sheet.title.replace(" ", "_")
        .replace("，", "")
        .replace("？", "")
        .replace("！", "")
        .replace("：", "")
        .replace("·", "")
    )
    m = re.match(r"^第(\d+)章_(.*)$", clean_title)
    if m:
        clean_title = f"第{int(m.group(1)):02d}章_{m.group(2)}"
    stem = f"{sheet.episode_id}_{clean_title}_完整有声剧台本"
    json_path = scripts_dir / f"{stem}.json"
    md_path = scripts_dir / f"{stem}.md"
    sheet.save(json_path)
    write_cue_sheet_markdown(sheet, md_path, registry=registry)
    return json_path, md_path
