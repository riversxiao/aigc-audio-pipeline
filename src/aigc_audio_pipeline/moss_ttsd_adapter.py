"""OpenMOSS MOSS-TTSD-v1.0 multi-speaker continuous podcast dialogue adapter.

Transforms an `EpisodeCueSheet`'s contiguous podcast turns within each act into
native 1–5 speaker `[S1]`–`[S5]` continuous studio sessions for
`OpenMOSS-Team/MOSS-TTSD-v1.0` (`voice_clone_and_continuation` mode), eliminating
line-by-line isolated TTS cold starts and stitched-turn cadence while preserving
exact per-act BGM boundaries (e.g. Silicon Valley 101-style scored Prologue ->
100% dry main conversation -> warm scored Outro).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import re
from typing import Any

from .models import EpisodeCueSheet, TimelineCue, extract_tags_and_spoken_text
from .polyphones import apply_domain_polyphone_overrides

MOSS_TTSD_MODEL_REPO = "OpenMOSS-Team/MOSS-TTSD-v1.0"
MOSS_AUDIO_TOKENIZER_REPO = "OpenMOSS-Team/MOSS-Audio-Tokenizer"

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_EN_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")
_TAG_RE = re.compile(r"\[([^\[\]]+)\]")
_XML_RE = re.compile(r"</?(?:whisper|soft|forceful|slow|fast|emphasis)>")
_REMOVE_PUNCT_CHARS = "【】《》（）『』「」\"“”～~‘’"
_LAUGH_TAGS = frozenset({"chuckles", "laughs", "laughing", "light chuckle", "笑"})


@dataclass
class DialogueBlock:
    """A continuous multi-speaker podcast recording take within a single act."""

    block_id: str
    act_id: str
    cues: list[TimelineCue] = field(default_factory=list)
    speaker_roles: list[str] = field(default_factory=list)
    dialogue_script: str = ""
    plain_text: str = ""
    cjk_chars: int = 0
    en_words: int = 0
    estimated_max_new_tokens: int = 1024
    gap_after_s: float = 0.25
    acoustic_space: str = "chatroom_table"


def _clean_single_turn_for_moss_ttsd(raw_text: str, *, domain: str = "hotline_roundtable") -> str:
    """Normalize one dialogue turn into natural OpenMOSS MOSS-TTSD-v1.0 spoken text."""
    text = _XML_RE.sub("", raw_text or "")
    text = apply_domain_polyphone_overrides(text, domain=domain)

    def _replace_tag(match: re.Match[str]) -> str:
        tok = match.group(1).strip().lower()
        if tok in _LAUGH_TAGS:
            return "[笑]"
        return ""

    text = _TAG_RE.sub(_replace_tag, text)
    text = re.sub(r"哈{2,}", "[笑]", text)
    text = re.sub(f"[{re.escape(_REMOVE_PUNCT_CHARS)}]", "", text)

    for dash in ("——", "……", "...", "⸺", "―", "—", "…"):
        text = text.replace(dash, "，")

    # Convert Chinese pause punctuation to flowing commas (keep ASCII ':' inside times/ratios)
    text = text.translate(str.maketrans({"；": "，", "：": "，", "、": "，", ";": ","}))
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([，。？！,.?!])[，。？！,.?!]+", r"\1", text)

    # OpenMOSS official normalization: keep flowing commas inside a turn and terminal punctuation at the end
    # so long intellectual podcast turns never trigger premature EOS or accidental speaker switches.
    if len(text) > 1:
        last_ch = "。" if text[-1] == "，" else ("." if text[-1] == "," else text[-1])
        body = text[:-1].replace("。", "，")
        text = body + last_ch
    elif text and text[-1] not in "。？！.?!":
        text = text + "。"

    # Keep [笑] tokens intact while ensuring no stray empty brackets remain
    text = re.sub(r"\[\s*\]", "", text).strip()
    return text


def normalize_moss_ttsd_text(script_text: str) -> str:
    """Apply OpenMOSS MOSS-TTSD-v1.0 script normalization and merge consecutive same-speaker turns."""
    normalized_in = re.sub(r"\[(\d+)\]", r"[S\1]", (script_text or "").replace("\n", " "))
    segments = re.split(r"(?=\[S\d+\])", normalized_in)
    parts: list[tuple[str, str]] = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        m = re.match(r"^(\[S\d+\])\s*(.*)$", seg, re.DOTALL)
        tag, body = m.groups() if m else ("", seg)
        cleaned = _clean_single_turn_for_moss_ttsd(body)
        if not cleaned:
            continue
        if parts and tag and parts[-1][0] == tag:
            prev_tag, prev_body = parts[-1]
            prev_body_joined = prev_body[:-1] + "，" if prev_body.endswith("。") else prev_body
            parts[-1] = (prev_tag, f"{prev_body_joined}{cleaned}")
        else:
            parts.append((tag, cleaned))
    return "".join(f"{t}{c}" for t, c in parts).strip()


def estimate_moss_ttsd_max_new_tokens(cjk_chars: int, en_words: int = 0) -> int:
    """Estimate safe `max_new_tokens` for MOSS-TTSD-v1.0 (12.5 audio tokens/s, ~2.3x safety factor)."""
    est_sec = max(4.0, (cjk_chars + 2.3 * en_words) / 3.7)
    est_tokens = int(math.ceil(est_sec * 12.5 * 2.35)) + 160
    return max(512, min(6144, est_tokens))


def build_moss_ttsd_prefixed_prompt(
    dialogue_script: str,
    speaker_prompt_texts: list[str],
) -> str:
    """Build MOSS-TTSD `voice_clone_and_continuation` prefixed text (`[S1]ref1[S2]ref2...[S1]turn1...`)."""
    prefix_parts: list[str] = []
    for idx, raw_ref in enumerate(speaker_prompt_texts, 1):
        ref = (raw_ref or "").strip()
        tag = f"[S{idx}]"
        if not ref.startswith(tag):
            ref = f"{tag}{ref}"
        prefix_parts.append(ref)
    combined = "".join(prefix_parts) + (dialogue_script or "")
    return normalize_moss_ttsd_text(combined)


def _finalize_block(
    *,
    act_id: str,
    block_num: int,
    cues: list[TimelineCue],
    domain: str,
) -> DialogueBlock:
    speaker_roles: list[str] = []
    role_to_sid: dict[str, int] = {}
    turns: list[str] = []
    plain_parts: list[str] = []

    for cue in cues:
        rid = cue.role_id
        if rid not in role_to_sid:
            speaker_roles.append(rid)
            role_to_sid[rid] = len(speaker_roles)
        sid = role_to_sid[rid]
        source_txt = cue.tts_text or cue.text
        cleaned_turn = _clean_single_turn_for_moss_ttsd(source_txt, domain=domain)
        if not cleaned_turn:
            continue
        turns.append(f"[S{sid}]{cleaned_turn}")
        _, spoken = extract_tags_and_spoken_text(cue.text)
        if spoken:
            plain_parts.append(spoken)

    script = normalize_moss_ttsd_text("".join(turns))
    plain_text = " ".join(plain_parts).strip()
    cjk_n = len(_CJK_RE.findall(plain_text))
    en_n = len(_EN_WORD_RE.findall(plain_text))
    last_cue = cues[-1]
    space = next((c.acoustic_space for c in cues if c.acoustic_space), "chatroom_table")

    return DialogueBlock(
        block_id=f"{act_id}_BLK{block_num:02d}",
        act_id=act_id,
        cues=list(cues),
        speaker_roles=speaker_roles,
        dialogue_script=script,
        plain_text=plain_text,
        cjk_chars=cjk_n,
        en_words=en_n,
        estimated_max_new_tokens=estimate_moss_ttsd_max_new_tokens(cjk_n, en_n),
        gap_after_s=max(0.18, float(last_cue.gap_after_s or 0.25)),
        acoustic_space=space,
    )


def group_podcast_cues_into_dialogue_blocks(
    cue_sheet: EpisodeCueSheet,
    *,
    max_cjk_chars: int = 850,
    max_speakers: int = 5,
    domain: str = "hotline_roundtable",
) -> list[tuple[str, TimelineCue | DialogueBlock]]:
    """Group contiguous podcast dialogue cues per act into unbroken MOSS-TTSD takes.

    Flushes cleanly on every SFX cue, act boundary, speaker cap (>5), or length cap
    (`max_cjk_chars`, default 850 chars ≈ 3.2 min sweet spot for zero speaker drift).
    """
    items: list[tuple[str, TimelineCue | DialogueBlock]] = []
    buf: list[TimelineCue] = []
    buf_roles: set[str] = set()
    buf_cjk = 0
    buf_act = ""
    act_block_counts: dict[str, int] = {}

    def _flush() -> None:
        nonlocal buf, buf_roles, buf_cjk, buf_act
        if not buf:
            return
        act_block_counts[buf_act] = act_block_counts.get(buf_act, 0) + 1
        blk = _finalize_block(
            act_id=buf_act,
            block_num=act_block_counts[buf_act],
            cues=buf,
            domain=domain,
        )
        items.append(("dialogue_block", blk))
        buf = []
        buf_roles = set()
        buf_cjk = 0
        buf_act = ""

    for cue in cue_sheet.cues:
        if cue.kind != "dialogue":
            _flush()
            items.append(("sfx", cue))
            continue

        _, spoken = extract_tags_and_spoken_text(cue.text)
        cue_cjk = len(_CJK_RE.findall(spoken)) + int(len(_EN_WORD_RE.findall(spoken)) * 1.8)
        projected_roles = buf_roles | {cue.role_id}

        need_split = (
            bool(buf)
            and (
                cue.act_id != buf_act
                or (buf_cjk + cue_cjk > max_cjk_chars and len(buf) >= 2)
                or len(projected_roles) > max_speakers
            )
        )
        if need_split:
            _flush()

        if not buf:
            buf_act = cue.act_id
        buf.append(cue)
        buf_roles.add(cue.role_id)
        buf_cjk += cue_cjk

    _flush()
    return items


def build_synthetic_block_cue(block: DialogueBlock) -> TimelineCue:
    """Wrap a multi-speaker continuous `DialogueBlock` into one `TimelineCue` for 3-bus mastering."""
    speaker_names: list[str] = []
    for c in block.cues:
        nm = (c.speaker_name or c.role_id).strip()
        if nm and nm not in speaker_names:
            speaker_names.append(nm)
    return TimelineCue(
        cue_id=block.block_id,
        act_id=block.act_id,
        kind="dialogue",
        role_id=block.speaker_roles[0] if len(block.speaker_roles) == 1 else "podcast_ensemble",
        speaker_name=" / ".join(speaker_names[:4]),
        text=block.plain_text,
        tts_text=block.dialogue_script,
        acoustic_space=block.acoustic_space,
        gap_after_s=block.gap_after_s,
    )


def build_block_subtitle_segments(
    block: DialogueBlock,
    *,
    whisper_segments: list[tuple[float, float, str]] | None,
    block_duration_s: float,
) -> list[dict[str, Any]]:
    """Build relative-timestamp SRT subtitle entries for a continuous multi-speaker block."""
    dur = max(0.5, float(block_duration_s))
    if whisper_segments:
        out: list[dict[str, Any]] = []
        for st, en, txt in whisper_segments:
            clean = re.sub(r"\s+", " ", (txt or "")).strip()
            if not clean:
                continue
            s0 = max(0.0, min(dur - 0.05, float(st)))
            s1 = max(s0 + 0.15, min(dur, float(en)))
            out.append({"start_rel_s": round(s0, 3), "end_rel_s": round(s1, 3), "text": clean})
        if out:
            return out

    # Deterministic proportional fallback (used in offline dry-run or --skip-asr-qa)
    weights: list[tuple[TimelineCue, str, int]] = []
    total_w = 0
    for c in block.cues:
        _, spoken = extract_tags_and_spoken_text(c.text)
        if not spoken:
            continue
        w = max(4, len(spoken))
        weights.append((c, spoken, w))
        total_w += w
    if not weights:
        return [{"start_rel_s": 0.0, "end_rel_s": round(dur, 3), "text": block.plain_text}]

    segs: list[dict[str, Any]] = []
    cur = 0.0
    for idx, (c, spoken, w) in enumerate(weights):
        span = dur * (w / max(1, total_w))
        end = dur if idx == len(weights) - 1 else min(dur, cur + span)
        prefix = f"{c.speaker_name}：" if c.speaker_name else ""
        segs.append(
            {
                "start_rel_s": round(cur, 3),
                "end_rel_s": round(max(cur + 0.15, end), 3),
                "text": f"{prefix}{spoken}",
            }
        )
        cur = end
    return segs


def _extract_eval_units(text: str) -> str:
    return "".join(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", (text or "").lower()))


def evaluate_dialogue_block_qa(
    expected_plain_text: str,
    asr_text: str | None,
    *,
    duration_s: float,
    peak_dbfs: float,
) -> tuple[bool, float, str]:
    """Quality gate for a continuous MOSS-TTSD dialogue block (rate + peak + ASR recall)."""
    exp_units = _extract_eval_units(expected_plain_text)
    cjk_n = len(_CJK_RE.findall(expected_plain_text))
    en_n = len(_EN_WORD_RE.findall(expected_plain_text))
    eff_chars = max(1, cjk_n + int(round(en_n * 2.0)))

    if peak_dbfs <= -34.0:
        return False, 0.0, f"silent_peak={peak_dbfs:.1f}dBFS"

    sec_per_char = duration_s / eff_chars
    if eff_chars >= 15:
        if sec_per_char < 0.095:
            return False, 0.0, f"too_fast={sec_per_char:.3f}s/ch"
        if sec_per_char > 0.56:
            return False, 0.0, f"too_slow_or_runaway={sec_per_char:.3f}s/ch"

    if not asr_text or not exp_units:
        return True, 0.85, f"signal_only_ok rate={sec_per_char:.3f}s/ch"

    asr_units = _extract_eval_units(asr_text)
    if not asr_units:
        return False, 0.0, "empty_asr"

    # Bag-of-characters recall (order-tolerant across fast multi-speaker turns)
    exp_counts: dict[str, int] = {}
    for ch in exp_units:
        exp_counts[ch] = exp_counts.get(ch, 0) + 1
    asr_counts: dict[str, int] = {}
    for ch in asr_units:
        asr_counts[ch] = asr_counts.get(ch, 0) + 1
    matched = sum(min(cnt, asr_counts.get(ch, 0)) for ch, cnt in exp_counts.items())
    recall = matched / max(1, len(exp_units))
    passed = recall >= 0.70
    return passed, round(recall, 4), f"recall={recall:.2%} rate={sec_per_char:.3f}s/ch"
