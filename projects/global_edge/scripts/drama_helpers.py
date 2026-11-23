"""Deterministic builders, empirical bilingual runtime estimator, and automated linter for Global Edge.

Zero third-party dependencies — stdlib + first-party `aigc_audio_pipeline` only.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from aigc_audio_pipeline.drama3_adapter import (
    DRAMA3_POINT_EVENTS,
    DRAMA3_TAG_MAP,
    split_cue_into_subcues_for_drama3,
    translate_cue_to_drama3_input,
)
from aigc_audio_pipeline.models import (
    ALLOWED_V3_STABILITIES,
    ActMusicSpec,
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
)
from aigc_audio_pipeline.polyphones import compute_tts_text_override
from ost_and_motifs import GLOBAL_EDGE_OST_SPECS, GLOBAL_EDGE_SONIC_MOTIFS

# ---------------------------------------------------------------------------
# Canonical Paths & Constants
# ---------------------------------------------------------------------------

SCRIPTS_DIR = Path(__file__).resolve().parent
GLOBAL_EDGE_ROOT = SCRIPTS_DIR.parent
REPO_ROOT = GLOBAL_EDGE_ROOT.parent.parent
REGISTRY_PATH = GLOBAL_EDGE_ROOT / "00_节目圣经与第一季24集总纲" / "voice_casting_registry.json"
SHOW_BIBLE_PATH = GLOBAL_EDGE_ROOT / "00_节目圣经与第一季24集总纲" / "SHOW_BIBLE.md"
SEASON_MAP_PATH = GLOBAL_EDGE_ROOT / "00_节目圣经与第一季24集总纲" / "season1_24ep_map.json"
DEFAULT_OUT_DIR = GLOBAL_EDGE_ROOT / "02_分集广播剧台本"
DEFAULT_LAUNCH_DIR = GLOBAL_EDGE_ROOT / "03_全平台分发与切片方案"

DOMAIN = "business_english_drama"

CORE_E001_ROLES: frozenset[str] = frozenset(
    {"lin_chen", "zhou_mo", "victoria_vance", "alistair_finch", "claire_chen_gc"}
)
FORBIDDEN_E001_GUEST_ROLES: frozenset[str] = frozenset(
    {"rajiv_menon", "wei_ling_tan", "henrik_lindqvist"}
)
ALL_LOCKED_ROLES: frozenset[str] = CORE_E001_ROLES | FORBIDDEN_E001_GUEST_ROLES
CORE_US_UK_ACCENTS: frozenset[str] = frozenset(
    {"zh_en_bilingual_us", "us_silicon_valley", "uk_london_rp", "us_nyc"}
)
DRAMA_ACT_IDS: frozenset[str] = frozenset({"act1", "act2", "act3", "act4"})
DEBRIEF_ACT_ID: str = "act5"

# All 8 mandatory phrase groups (13 exact verbatim sub-phrases from 5 E001 seed clips)
MANDATORY_E001_PHRASE_GROUPS: tuple[dict[str, Any], ...] = (
    {
        "group_id": 1,
        "clip_id": "02_BIZ_Anthropic",
        "lexicon_ids": ("LEX_025",),
        "subphrases": ("phantom number",),
    },
    {
        "group_id": 2,
        "clip_id": "02_BIZ_Anthropic",
        "lexicon_ids": ("LEX_026", "LEX_027"),
        "subphrases": ("not a cash loss", "flowed through into the income statement"),
    },
    {
        "group_id": 3,
        "clip_id": "02_BIZ_Anthropic",
        "lexicon_ids": ("LEX_028",),
        "subphrases": ("capital-efficient",),
    },
    {
        "group_id": 4,
        "clip_id": "012_AI",
        "lexicon_ids": ("LEX_049", "LEX_001"),
        "subphrases": ("10 times the throughput", "Pick your favorite number"),
    },
    {
        "group_id": 5,
        "clip_id": "039_BIZ",
        "lexicon_ids": ("LEX_002",),
        "subphrases": ("In other words",),
    },
    {
        "group_id": 6,
        "clip_id": "090_USC",
        "lexicon_ids": ("LEX_050", "LEX_003"),
        "subphrases": ("eating into budgets", "a really hard trade-off"),
    },
    {
        "group_id": 7,
        "clip_id": "090_USC",
        "lexicon_ids": ("LEX_004", "LEX_051"),
        "subphrases": ("What is good enough", "run this thing a million times"),
    },
    {
        "group_id": 8,
        "clip_id": "059_FIN",
        "lexicon_ids": ("LEX_029", "LEX_030"),
        "subphrases": ("upside", "When are you going to get it"),
    },
)

BANNED_CLICHES_AND_LEAKS: tuple[str, ...] = (
    "各位听众",
    "欢迎收听",
    "大家好，我是",
    "问到根子上了",
    "这个比方绝了",
    "说得太好了",
    "一针见血",
    "youtube",
    "视频号",
    "上期切片",
    "本期视频",
    "这期视频",
    "今天这条短视频",
    "all-in podcast",
    "cnbc",
    "anthropic",
    "nvidia",
    "zhipu",
    "buffett",
    "10x the throughput",
    "claire chen",
)

XIANXIA_LEAK_TOKENS: tuple[str, ...] = (
    "Xianxia",
    "ancient monotone",
    "distant, solemn memory voice",
    "仙侠",
    "修仙",
    "引气",
    "宗门",
    "炼气",
    "筑基",
    "金丹",
    "元婴",
    "化神",
    "渡劫",
    "飞升",
    "灵根",
    "道侣",
    "丹田",
    "道行",
    "辟谷",
)

VALID_DRAMA3_TAGS: frozenset[str] = frozenset(
    set(DRAMA3_TAG_MAP.keys()) | set(DRAMA3_POINT_EVENTS.keys()) | {"laughs", "laughing"}
)
POINT_EVENT_TAGS: frozenset[str] = frozenset(
    set(DRAMA3_POINT_EVENTS.keys()) | {"laughs", "laughing"}
)

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_EN_WORD_RE = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z0-9]+)*")
_LATIN_LETTER_RE = re.compile(r"[A-Za-z]")
_TAG_SPLIT_CLAUSE_RE = re.compile(r"(?<=[.!?。！？；\n])\s*")
_BRACKET_TAG_RE = re.compile(r"\[([^\[\]]+)\]")
_CURLY_PUNCT_TRANS = str.maketrans({
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2010": "-",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2015": "-",
    "\u2212": "-",
})


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def _assert_no_pure_en_wryly(cue_id: str, text: str) -> None:
    tags, _ = extract_tags_and_spoken_text(text)
    if any(t.lower().strip() == "wryly" for t in tags):
        raise ValueError(
            f"{cue_id}: [wryly] is strictly banned on pure-EN cues (triggers Midwestern drift)"
        )


def count_cjk_and_en_words(text: str) -> tuple[int, int]:
    """Return `(cjk_char_count, en_word_count)` after stripping `[...]` performance tags."""
    _, spoken = extract_tags_and_spoken_text(text)
    cjk_count = len(_CJK_RE.findall(spoken))
    en_count = len(_EN_WORD_RE.findall(spoken))
    return cjk_count, en_count


def _compute_zh_tts_override(text: str) -> str:
    override = compute_tts_text_override(text, domain=DOMAIN)
    return override if override else ""


# ---------------------------------------------------------------------------
# Deterministic Cue & Act Builders
# ---------------------------------------------------------------------------


def act_spec(
    act_id: str,
    title: str,
    ost_key: str,
    *,
    bgm_duration_s: float = 60.0,
    bgm_gain_speech: float | None = None,
    bgm_gain_gap: float | None = None,
) -> ActMusicSpec:
    """Build an `ActMusicSpec` locked to a canonical Global Edge ACE-Step 1.5 XL OST prompt."""
    if ost_key not in GLOBAL_EDGE_OST_SPECS:
        raise KeyError(
            f"Unknown ost_key {ost_key!r}; expected one of {sorted(GLOBAL_EDGE_OST_SPECS)}"
        )
    spec = GLOBAL_EDGE_OST_SPECS[ost_key]
    return ActMusicSpec(
        act_id=act_id,
        title=title,
        bgm_prompt=str(spec["bgm_prompt"]),
        bgm_duration_s=float(bgm_duration_s),
        bgm_gain_speech=float(
            spec["bgm_gain_speech"] if bgm_gain_speech is None else bgm_gain_speech
        ),
        bgm_gain_gap=float(
            spec["bgm_gain_gap"] if bgm_gain_gap is None else bgm_gain_gap
        ),
    )


def en_boardroom(
    cue_id: str,
    act_id: str,
    role_id: str,
    text: str,
    *,
    subtitle_translation: str,
    stability: float = 0.5,
    similarity_boost: float = 0.85,
    gap_after_s: float = 0.35,
    playback_rate: float = 1.0,
    acoustic_space: str = "boardroom",
    director_note: str = "",
) -> TimelineCue:
    """Build a pure-English executive boardroom/negotiation dialogue cue."""
    _assert_no_pure_en_wryly(cue_id, text)
    if not subtitle_translation.strip():
        raise ValueError(f"{cue_id}: pure-EN cue requires non-empty Chinese subtitle_translation")
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="dialogue",
        role_id=role_id,
        language_code="en",
        text=text,
        tts_text="",
        stability=float(stability),
        similarity_boost=float(similarity_boost),
        acoustic_space=acoustic_space,
        playback_rate=float(playback_rate),
        subtitle_translation=subtitle_translation.strip(),
        gap_after_s=float(gap_after_s),
        director_note=director_note,
    )


def zh_inner_monologue(
    cue_id: str,
    act_id: str,
    text: str,
    *,
    role_id: str = "lin_chen",
    language_code: str = "zh",
    stability: float = 0.5,
    similarity_boost: float = 0.85,
    gap_after_s: float = 0.35,
    director_note: str = "",
) -> TimelineCue:
    """Build a close-mic House-of-Cards Mandarin inner monologue cue (`acoustic_space='inner_monologue'`)."""
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="dialogue",
        role_id=role_id,
        language_code=language_code,
        text=text,
        tts_text=_compute_zh_tts_override(text),
        stability=float(stability),
        similarity_boost=float(similarity_boost),
        acoustic_space="inner_monologue",
        playback_rate=1.0,
        subtitle_translation="",
        gap_after_s=float(gap_after_s),
        director_note=director_note,
    )


def zh_en_backroom(
    cue_id: str,
    act_id: str,
    role_id: str,
    text: str,
    *,
    language_code: str = "zh",
    acoustic_space: str = "dry",
    stability: float = 0.5,
    similarity_boost: float = 0.85,
    gap_after_s: float = 0.35,
    subtitle_translation: str = "",
    director_note: str = "",
) -> TimelineCue:
    """Build a private Mandarin or strictly controlled `zh-en` backroom / Act 5 coaching cue."""
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="dialogue",
        role_id=role_id,
        language_code=language_code,
        text=text,
        tts_text=_compute_zh_tts_override(text),
        stability=float(stability),
        similarity_boost=float(similarity_boost),
        acoustic_space=acoustic_space,
        playback_rate=1.0,
        subtitle_translation=subtitle_translation.strip(),
        gap_after_s=float(gap_after_s),
        director_note=director_note,
    )


def en_phone_call(
    cue_id: str,
    act_id: str,
    role_id: str,
    text: str,
    *,
    subtitle_translation: str,
    stability: float = 0.5,
    similarity_boost: float = 0.85,
    gap_after_s: float = 0.35,
    director_note: str = "",
) -> TimelineCue:
    """Build a pure-English transpacific telephone / bridge-call cue (`acoustic_space='phone_call'`)."""
    _assert_no_pure_en_wryly(cue_id, text)
    if not subtitle_translation.strip():
        raise ValueError(f"{cue_id}: pure-EN phone cue requires non-empty Chinese subtitle_translation")
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="dialogue",
        role_id=role_id,
        language_code="en",
        text=text,
        tts_text="",
        stability=float(stability),
        similarity_boost=float(similarity_boost),
        acoustic_space="phone_call",
        playback_rate=1.0,
        subtitle_translation=subtitle_translation.strip(),
        gap_after_s=float(gap_after_s),
        director_note=director_note,
    )


def slow_drill_pair(
    slow_cue_id: str,
    native_cue_id: str,
    act_id: str,
    role_id: str,
    text: str,
    *,
    subtitle_translation: str,
    acoustic_space: str = "dry",
    slow_rate: float = 0.8,
    slow_gap_s: float = 0.7,
    shadow_gap_s: float = 2.4,
    stability: float = 0.5,
    director_note_slow: str = "",
    director_note_native: str = "",
) -> list[TimelineCue]:
    """Emit a paired `0.80x` slow dissection cue + `1.0x` native shadowing cue with `>= 2.0s` pause."""
    _assert_no_pure_en_wryly(slow_cue_id, text)
    if shadow_gap_s < 2.0:
        raise ValueError(
            f"{native_cue_id}: shadow_gap_s={shadow_gap_s} must be >= 2.0s for phonological-loop shadowing"
        )
    if not subtitle_translation.strip():
        raise ValueError(f"{slow_cue_id}: slow_drill_pair requires Chinese subtitle_translation")
    return [
        TimelineCue(
            cue_id=slow_cue_id,
            act_id=act_id,
            kind="dialogue",
            role_id=role_id,
            language_code="en",
            text=text,
            tts_text="",
            stability=float(stability),
            similarity_boost=0.85,
            acoustic_space=acoustic_space,
            playback_rate=float(slow_rate),
            subtitle_translation=subtitle_translation.strip(),
            gap_after_s=float(slow_gap_s),
            director_note=director_note_slow or "Act 5 0.80x 慢拆（复用 1.0x 干声经 FFmpeg atempo 保音高拉慢）",
        ),
        TimelineCue(
            cue_id=native_cue_id,
            act_id=act_id,
            kind="dialogue",
            role_id=role_id,
            language_code="en",
            text=text,
            tts_text="",
            stability=float(stability),
            similarity_boost=0.85,
            acoustic_space=acoustic_space,
            playback_rate=1.0,
            subtitle_translation=subtitle_translation.strip(),
            gap_after_s=float(shadow_gap_s),
            director_note=director_note_native or f"Act 5 1.0x 原速跟读（留白 {shadow_gap_s:.1f}s 供开口复述）",
        ),
    ]


def ducked_en_pair(
    en_cue_id: str,
    zh_cue_id: str,
    act_id: str,
    en_role_id: str,
    en_text: str,
    zh_role_id: str,
    zh_text: str,
    *,
    en_acoustic_space: str = "boardroom",
    zh_acoustic_space: str = "studio_warm",
    duck_lead_in_s: float = 3.6,
    duck_gain: float = 0.15,
    zh_language_code: str = "zh",
    zh_gap_after_s: float = 0.45,
    en_stability: float = 0.5,
    zh_stability: float = 0.5,
    en_subtitle_translation: str = "",
    en_director_note: str = "",
    zh_director_note: str = "",
) -> list[TimelineCue]:
    """Emit a documentary simultaneous-translation pair (`duck_under_next=True` EN -> Mandarin VO)."""
    _assert_no_pure_en_wryly(en_cue_id, en_text)
    if not (3.0 <= duck_lead_in_s <= 5.0):
        raise ValueError(f"{en_cue_id}: duck_lead_in_s={duck_lead_in_s} must be in [3.0, 5.0]")
    if abs(duck_gain - 0.15) > 1e-6:
        raise ValueError(f"{en_cue_id}: duck_gain={duck_gain} must be 0.15 for Global Edge spec")
    _, en_words = count_cjk_and_en_words(en_text)
    if en_words > 55:
        raise ValueError(
            f"{en_cue_id}: duck_under_next EN cue has {en_words} words (> 55); must never auto-split"
        )
    if not en_subtitle_translation.strip():
        raise ValueError(
            f"{en_cue_id}: ducked EN cue requires concise Chinese en_subtitle_translation"
        )

    return [
        TimelineCue(
            cue_id=en_cue_id,
            act_id=act_id,
            kind="dialogue",
            role_id=en_role_id,
            language_code="en",
            text=en_text,
            tts_text="",
            stability=float(en_stability),
            similarity_boost=0.85,
            acoustic_space=en_acoustic_space,
            playback_rate=1.0,
            subtitle_translation=en_subtitle_translation.strip(),
            duck_under_next=True,
            duck_lead_in_s=float(duck_lead_in_s),
            duck_gain=float(duck_gain),
            gap_after_s=0.0,
            director_note=en_director_note
            or f"纪实同传原声（独奏 {duck_lead_in_s:.1f}s 后半余弦压混至 {duck_gain:.2f}）",
        ),
        TimelineCue(
            cue_id=zh_cue_id,
            act_id=act_id,
            kind="dialogue",
            role_id=zh_role_id,
            language_code=zh_language_code,
            text=zh_text,
            tts_text=_compute_zh_tts_override(zh_text),
            stability=float(zh_stability),
            similarity_boost=0.85,
            acoustic_space=zh_acoustic_space,
            playback_rate=1.0,
            subtitle_translation="",
            duck_under_next=False,
            gap_after_s=float(zh_gap_after_s),
            director_note=zh_director_note or "纪实同传中文叠音画外拆解（切入原声低轨之上）",
        ),
    ]


def motif_cue(
    cue_id: str,
    act_id: str,
    motif_id: str,
    *,
    placement: str = "sequential",
    gap_after_s: float = 0.18,
    gain_db: float = -3.5,
    director_note: str = "",
) -> TimelineCue:
    """Build a canonical MOSS-SoundEffect-v2.0 Foley cue verbatim from `GLOBAL_EDGE_SONIC_MOTIFS`."""
    if motif_id not in GLOBAL_EDGE_SONIC_MOTIFS:
        raise KeyError(
            f"Unknown motif_id {motif_id!r}; expected one of {sorted(GLOBAL_EDGE_SONIC_MOTIFS)}"
        )
    m = GLOBAL_EDGE_SONIC_MOTIFS[motif_id]
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="sfx",
        motif_id=motif_id,
        sfx_prompt=str(m["sfx_prompt"]),
        duration_seconds=float(m["duration_seconds"]),
        prompt_influence=float(m["prompt_influence"]),
        loop=bool(m["loop"]),
        placement=placement,
        gain_db=float(gain_db),
        gap_after_s=float(gap_after_s),
        director_note=director_note or str(m["name"]),
    )


# ---------------------------------------------------------------------------
# Empirical Bilingual Duration Estimators
# ---------------------------------------------------------------------------


def estimate_cue_speech_duration_s(cue: TimelineCue) -> float:
    """Empirical speech duration of a dialogue cue: `max(0.8, en/2.60 + cjk/3.60) / playback_rate`."""
    if cue.kind != "dialogue":
        return float(cue.duration_seconds)
    cjk_count, en_words = count_cjk_and_en_words(cue.text)
    raw = max(0.8, (en_words / 2.60) + (cjk_count / 3.60))
    return raw / float(cue.playback_rate)


def estimate_cues_duration_s(
    cues: list[TimelineCue],
    *,
    include_pads: tuple[float, float] = (0.0, 0.0),
) -> float:
    """Estimate timeline duration of a contiguous cue sequence accounting for SFX, crosstalk, and ducking."""
    total_s = float(include_pads[0]) + float(include_pads[1])
    idx = 0
    n = len(cues)
    while idx < n:
        cue = cues[idx]
        if cue.kind == "sfx":
            if cue.placement == "overlay_next":
                total_s += max(0.0, float(cue.gap_after_s))
            else:
                total_s += float(cue.duration_seconds) + max(0.0, float(cue.gap_after_s))
            idx += 1
            continue

        dur_s = estimate_cue_speech_duration_s(cue)
        if cue.duck_under_next and idx + 1 < n and cues[idx + 1].kind == "dialogue":
            next_cue = cues[idx + 1]
            zh_dur = estimate_cue_speech_duration_s(next_cue)
            lead_in = min(float(cue.duck_lead_in_s), max(0.8, dur_s * 0.85))
            pair_dur = max(dur_s, lead_in + zh_dur)
            gap = max(-0.25, float(next_cue.gap_after_s))
            total_s += max(0.05, pair_dur + gap)
            idx += 2
            continue

        gap = max(-0.25, float(cue.gap_after_s))
        total_s += max(0.05, dur_s + gap)
        idx += 1

    return round(total_s, 2)


def estimate_synth_dry_duration_s(
    cues: list[TimelineCue],
    *,
    include_pads: tuple[float, float] = (0.0, 0.0),
) -> float:
    """Mirror `cli.py:cmd_synth_dry_test` duration formula so both estimators stay inside budgets."""
    total_s = float(include_pads[0]) + float(include_pads[1])
    idx = 0
    n = len(cues)
    while idx < n:
        cue = cues[idx]
        if cue.kind == "sfx":
            if cue.placement == "overlay_next":
                total_s += max(0.0, float(cue.gap_after_s))
            else:
                total_s += min(float(cue.duration_seconds), 6.0) + max(0.0, float(cue.gap_after_s))
            idx += 1
            continue

        _, spoken = extract_tags_and_spoken_text(cue.text)
        if cue.language_code == "en":
            raw_dur = max(1.2, min(36.0, len(spoken.split()) / 2.65))
        else:
            raw_dur = max(0.8, min(36.0, len(spoken) / 4.15))
        dur_s = raw_dur / float(cue.playback_rate)

        if cue.duck_under_next and idx + 1 < n and cues[idx + 1].kind == "dialogue":
            next_cue = cues[idx + 1]
            _, next_spoken = extract_tags_and_spoken_text(next_cue.text)
            if next_cue.language_code == "en":
                next_raw = max(1.2, min(36.0, len(next_spoken.split()) / 2.65))
            else:
                next_raw = max(0.8, min(36.0, len(next_spoken) / 4.15))
            next_dur = next_raw / float(next_cue.playback_rate)
            lead_in = min(float(cue.duck_lead_in_s), max(0.8, dur_s * 0.85))
            pair_dur = max(dur_s, lead_in + next_dur)
            gap = max(-0.25, float(next_cue.gap_after_s))
            total_s += max(0.05, pair_dur + gap)
            idx += 2
            continue

        gap = max(-0.25, float(cue.gap_after_s))
        total_s += max(0.05, dur_s + gap)
        idx += 1

    return round(total_s, 2)


def slice_cue_range(
    sheet: EpisodeCueSheet,
    start_cue_id: str,
    end_cue_id: str,
) -> list[TimelineCue]:
    """Return contiguous slice `[start_cue_id .. end_cue_id]` inclusive, raising on bad IDs."""
    id_to_idx = {c.cue_id: i for i, c in enumerate(sheet.cues)}
    if start_cue_id not in id_to_idx:
        raise KeyError(f"{sheet.episode_id}: start_cue_id {start_cue_id!r} not found")
    if end_cue_id not in id_to_idx:
        raise KeyError(f"{sheet.episode_id}: end_cue_id {end_cue_id!r} not found")
    i0 = id_to_idx[start_cue_id]
    i1 = id_to_idx[end_cue_id]
    if i1 < i0:
        raise ValueError(
            f"{sheet.episode_id}: end_cue_id {end_cue_id!r} precedes start_cue_id {start_cue_id!r}"
        )
    return sheet.cues[i0 : i1 + 1]


def estimate_cue_range_duration_s(
    sheet: EpisodeCueSheet,
    start_cue_id: str,
    end_cue_id: str,
) -> float:
    """Estimate exact duration of a contiguous cue range (e.g., 45s WeChat Channels viral clip)."""
    return estimate_cues_duration_s(slice_cue_range(sheet, start_cue_id, end_cue_id))


# ---------------------------------------------------------------------------
# Metrics Collector & Automated Linter
# ---------------------------------------------------------------------------


def _eff_lang(cue: TimelineCue, registry: VoiceCastingRegistry) -> str:
    prof = registry.resolve_role(cue.role_id)
    return cue.language_code or (prof.language_code if prof else "") or "zh"


def _find_next_dialogue_cue(cues: list[TimelineCue], idx: int) -> TimelineCue | None:
    """Return the next dialogue cue immediately following `idx` (or bridged by `overlay_next` SFX)."""
    for j in range(idx + 1, len(cues)):
        nxt = cues[j]
        if nxt.kind == "dialogue":
            return nxt
        if nxt.kind == "sfx" and nxt.placement == "overlay_next":
            continue
        return None
    return None


def _find_prev_dialogue_cue(cues: list[TimelineCue], idx: int) -> TimelineCue | None:
    """Return the immediately preceding dialogue cue before `idx`."""
    for j in range(idx - 1, -1, -1):
        if cues[j].kind == "dialogue":
            return cues[j]
    return None


def compute_variant_metrics(
    sheet: EpisodeCueSheet,
    registry: VoiceCastingRegistry,
) -> dict[str, Any]:
    """Compute live quantitative telemetry for any Global Edge EpisodeCueSheet."""
    dialogue_cues = [c for c in sheet.cues if c.kind == "dialogue"]
    sfx_cues = [c for c in sheet.cues if c.kind == "sfx"]
    drama_cues = [c for c in sheet.cues if c.act_id in DRAMA_ACT_IDS]
    debrief_cues = [c for c in sheet.cues if c.act_id == DEBRIEF_ACT_ID]

    drama_dialogue = [c for c in drama_cues if c.kind == "dialogue"]
    debrief_dialogue = [c for c in debrief_cues if c.kind == "dialogue"]

    total_est_s = estimate_cues_duration_s(
        sheet.cues, include_pads=(sheet.head_pad_s, sheet.tail_pad_s)
    )
    drama_est_s = estimate_cues_duration_s(drama_cues)
    debrief_est_s = estimate_cues_duration_s(debrief_cues)
    synth_total_s = estimate_synth_dry_duration_s(
        sheet.cues, include_pads=(sheet.head_pad_s, sheet.tail_pad_s)
    )
    synth_drama_s = estimate_synth_dry_duration_s(drama_cues)
    synth_debrief_s = estimate_synth_dry_duration_s(debrief_cues)

    # Bilingual share in Drama Acts 1–4 by estimated speech time
    drama_en_speech_s = 0.0
    drama_zh_speech_s = 0.0
    for c in drama_dialogue:
        lang = _eff_lang(c, registry)
        cjk_n, en_n = count_cjk_and_en_words(c.text)
        en_part = (en_n / 2.60) / float(c.playback_rate)
        zh_part = (cjk_n / 3.60) / float(c.playback_rate)
        if lang == "en":
            drama_en_speech_s += max(0.8 / float(c.playback_rate), en_part)
        elif lang == "zh":
            drama_zh_speech_s += max(0.8 / float(c.playback_rate), zh_part)
        else:
            # Split mixed zh-en proportionally across spoken scripts
            drama_en_speech_s += en_part
            drama_zh_speech_s += zh_part

    drama_speech_total_s = drama_en_speech_s + drama_zh_speech_s
    drama_en_ratio = (
        round(drama_en_speech_s / drama_speech_total_s, 4) if drama_speech_total_s > 0 else 0.0
    )
    drama_zh_ratio = round(1.0 - drama_en_ratio, 4)

    # Accent share on English dialogue lines
    en_dialogue_all = [c for c in dialogue_cues if _eff_lang(c, registry) == "en"]
    core_us_uk_en_count = 0
    for c in en_dialogue_all:
        prof = registry.resolve_role(c.role_id)
        if prof and prof.accent_code in CORE_US_UK_ACCENTS:
            core_us_uk_en_count += 1
    core_us_uk_en_pct = (
        round(100.0 * core_us_uk_en_count / len(en_dialogue_all), 2) if en_dialogue_all else 0.0
    )

    # Structural counts (crosstalk counts ONLY genuine cross-speaker negative-gap overlaps)
    crosstalk_count = 0
    for idx, c in enumerate(sheet.cues):
        if c.kind != "dialogue":
            continue
        if -0.25 <= float(c.gap_after_s) <= -0.05:
            next_dlg = _find_next_dialogue_cue(sheet.cues, idx)
            if next_dlg is not None and next_dlg.role_id != c.role_id:
                crosstalk_count += 1
    inner_monologue_count = sum(
        1 for c in dialogue_cues if c.acoustic_space == "inner_monologue"
    )
    phone_call_count = sum(
        1 for c in dialogue_cues if c.acoustic_space == "phone_call"
    )
    studio_warm_drama_count = sum(
        1 for c in drama_dialogue if c.acoustic_space == "studio_warm"
    )
    duck_under_next_count = sum(1 for c in dialogue_cues if c.duck_under_next)
    act5_slow_count = sum(
        1 for c in debrief_dialogue if abs(float(c.playback_rate) - 0.8) < 1e-6
    )
    act5_shadow_gap_count = sum(
        1
        for c in debrief_dialogue
        if abs(float(c.playback_rate) - 1.0) < 1e-6 and float(c.gap_after_s) >= 1.8
    )
    act5_shadow_gap_2s_count = sum(
        1
        for c in debrief_dialogue
        if abs(float(c.playback_rate) - 1.0) < 1e-6 and float(c.gap_after_s) >= 2.0
    )

    # Mandatory phrase coverage in Drama Acts 1–4 EN dialogue (sentinel prevents cross-cue stitching;
    # word-bounded regex prevents substring spoofs like "upsidedown" for "upside")
    drama_en_corpus = (
        " ||| ".join(
            extract_tags_and_spoken_text(c.text)[1]
            for c in drama_dialogue
            if _eff_lang(c, registry) == "en"
        )
        .translate(_CURLY_PUNCT_TRANS)
        .lower()
    )
    groups_hit = 0
    missing_subphrases: list[str] = []
    for grp in MANDATORY_E001_PHRASE_GROUPS:
        grp_ok = True
        for sub in grp["subphrases"]:
            sub_norm = sub.translate(_CURLY_PUNCT_TRANS).lower()
            if not re.search(rf"(?<![a-z0-9]){re.escape(sub_norm)}(?![a-z0-9])", drama_en_corpus):
                grp_ok = False
                missing_subphrases.append(sub)
        if grp_ok:
            groups_hit += 1

    roles_used = sorted({c.role_id for c in dialogue_cues})
    act5_roles = sorted({c.role_id for c in debrief_dialogue})
    act_durations = {
        act.act_id: estimate_cues_duration_s([c for c in sheet.cues if c.act_id == act.act_id])
        for act in sheet.acts
    }

    # Check banned clichés and Xianxia leaks for metrics table
    banned_hits: list[str] = []
    xianxia_leaks = 0
    sheet_title_low = (sheet.title or "").lower()
    for banned in BANNED_CLICHES_AND_LEAKS:
        if banned in sheet_title_low:
            banned_hits.append(f"sheet.title:{banned}")
    for act in sheet.acts:
        act_title_low = (act.title or "").lower()
        for banned in BANNED_CLICHES_AND_LEAKS:
            if banned in act_title_low:
                banned_hits.append(f"{act.act_id}.title:{banned}")
    for c in dialogue_cues:
        tags, spoken = extract_tags_and_spoken_text(c.text)
        low = spoken.lower()
        sub_low = c.subtitle_translation.lower()
        tags_low = " ".join(tags).lower()
        for banned in BANNED_CLICHES_AND_LEAKS:
            if banned in low:
                banned_hits.append(f"{c.cue_id}:{banned}")
            if sub_low and banned in sub_low:
                banned_hits.append(f"{c.cue_id}:subtitle_translation:{banned}")
            if tags_low and banned in tags_low:
                banned_hits.append(f"{c.cue_id}:tags:{banned}")
        prof = registry.resolve_role(c.role_id)
        for attempt in (1, 2):
            rendered = translate_cue_to_drama3_input(c, prof, attempt=attempt, domain=DOMAIN)
            if any(tok in rendered for tok in XIANXIA_LEAK_TOKENS):
                xianxia_leaks += 1

    return {
        "episode_id": sheet.episode_id,
        "title": sheet.title,
        "mode": sheet.mode,
        "total_cues": len(sheet.cues),
        "dialogue_cues": len(dialogue_cues),
        "sfx_cues": len(sfx_cues),
        "drama_cues": len(drama_cues),
        "debrief_cues": len(debrief_cues),
        "roles_used": roles_used,
        "act5_roles": act5_roles,
        "total_duration_est_s": total_est_s,
        "drama_duration_est_s": drama_est_s,
        "debrief_duration_est_s": debrief_est_s,
        "synth_total_duration_est_s": synth_total_s,
        "synth_drama_duration_est_s": synth_drama_s,
        "synth_debrief_duration_est_s": synth_debrief_s,
        "act_durations_est_s": act_durations,
        "drama_en_ratio": drama_en_ratio,
        "drama_zh_ratio": drama_zh_ratio,
        "core_us_uk_en_pct": core_us_uk_en_pct,
        "crosstalk_count": crosstalk_count,
        "inner_monologue_count": inner_monologue_count,
        "phone_call_count": phone_call_count,
        "studio_warm_drama_count": studio_warm_drama_count,
        "duck_under_next_count": duck_under_next_count,
        "act5_slow_count": act5_slow_count,
        "act5_shadow_gap_count": act5_shadow_gap_count,
        "act5_shadow_gap_2s_count": act5_shadow_gap_2s_count,
        "mandatory_phrase_groups_hit": groups_hit,
        "mandatory_phrase_groups_total": len(MANDATORY_E001_PHRASE_GROUPS),
        "missing_subphrases": missing_subphrases,
        "banned_cliche_count": len(banned_hits),
        "banned_cliche_hits": banned_hits,
        "xianxia_drama3_leak_count": xianxia_leaks,
    }


def _lint_common_dialogue_cues(
    sheet: EpisodeCueSheet,
    registry: VoiceCastingRegistry,
    *,
    is_e001: bool,
) -> list[str]:
    """Run cue-level schema, tag, Drama 3, language, and anti-cliché lint rules."""
    errors: list[str] = []

    schema_errors = sheet.validate(registry=registry, require_locked_voices=True)
    for err in schema_errors:
        errors.append(f"[schema] {err}")

    for idx, cue in enumerate(sheet.cues):
        if cue.kind != "dialogue":
            continue

        prof = registry.resolve_role(cue.role_id)
        lang = _eff_lang(cue, registry)
        tags, spoken = extract_tags_and_spoken_text(cue.text)
        cjk_count, en_words = count_cjk_and_en_words(cue.text)

        # Discrete stability & forbidden spaces
        if float(cue.stability) not in ALLOWED_V3_STABILITIES:
            errors.append(f"{cue.cue_id}: stability={cue.stability} not in {ALLOWED_V3_STABILITIES}")
        if cue.acoustic_space == "mental_realm":
            errors.append(f"{cue.cue_id}: acoustic_space='mental_realm' is strictly forbidden")

        # Pure-EN [wryly] ban + legal Drama 3 tag whitelist + max 2 style tags per clause
        for t in tags:
            t_low = t.lower().strip()
            if t_low not in VALID_DRAMA3_TAGS:
                errors.append(f"{cue.cue_id}: unknown Drama 3 tag [{t}]")
            if lang == "en" and t_low == "wryly":
                errors.append(f"{cue.cue_id}: [wryly] forbidden on pure-EN cue")

        for cl_idx, clause in enumerate(_TAG_SPLIT_CLAUSE_RE.split(cue.text)):
            if not clause.strip():
                continue
            cl_tags = [m.lower().strip() for m in _BRACKET_TAG_RE.findall(clause)]
            style_tags = [t for t in cl_tags if t not in POINT_EVENT_TAGS]
            if len(style_tags) > 2:
                errors.append(
                    f"{cue.cue_id}: clause {cl_idx + 1} has {len(style_tags)} style tags (> 2): {style_tags}"
                )

        # Language discipline & per-line length caps
        if lang == "en":
            if cjk_count > 0:
                errors.append(f"{cue.cue_id}: pure-EN cue contains {cjk_count} CJK chars")
            if not (1 <= en_words <= 55):
                errors.append(f"{cue.cue_id}: pure-EN cue word count={en_words} outside [1, 55]")
            if not cue.subtitle_translation.strip() or not _CJK_RE.search(cue.subtitle_translation):
                errors.append(
                    f"{cue.cue_id}: pure-EN dialogue cue missing Chinese subtitle_translation"
                )
        elif lang == "zh":
            if not (4 <= cjk_count <= 85):
                errors.append(f"{cue.cue_id}: pure-ZH cue CJK count={cjk_count} outside [4, 85]")
            if _LATIN_LETTER_RE.search(spoken):
                errors.append(
                    f"{cue.cue_id}: pure-ZH cue contains Latin letters ({spoken!r}); use pure Chinese or language_code='zh-en'"
                )
        elif lang == "zh-en":
            effective_units = cjk_count + 2.2 * en_words
            if is_e001:
                if not (10 <= cjk_count <= 85):
                    errors.append(
                        f"{cue.cue_id}: zh-en cue CJK count={cjk_count} outside [10, 85]"
                    )
                if not (1 <= en_words <= 4):
                    errors.append(
                        f"{cue.cue_id}: zh-en cue EN word count={en_words} outside [1, 4]"
                    )
            if effective_units > 90.0:
                errors.append(
                    f"{cue.cue_id}: zh-en effective_units={effective_units:.1f} exceeds 90.0"
                )

        # Ducking invariants
        if cue.duck_under_next:
            if lang != "en":
                errors.append(
                    f"{cue.cue_id}: duck_under_next source cue must be pure English ('en'), got {lang!r}"
                )
            if abs(float(cue.playback_rate) - 1.0) > 1e-6:
                errors.append(
                    f"{cue.cue_id}: duck_under_next source cue must use playback_rate=1.0, got {cue.playback_rate}"
                )
            if abs(float(cue.gap_after_s)) > 1e-6:
                errors.append(
                    f"{cue.cue_id}: duck_under_next source cue must use gap_after_s=0.0, got {cue.gap_after_s}"
                )
            if not (3.0 <= float(cue.duck_lead_in_s) <= 5.0):
                errors.append(
                    f"{cue.cue_id}: duck_lead_in_s={cue.duck_lead_in_s} outside [3.0, 5.0]"
                )
            if abs(float(cue.duck_gain) - 0.15) > 1e-6:
                errors.append(f"{cue.cue_id}: duck_gain={cue.duck_gain} != 0.15")
            if idx + 1 >= len(sheet.cues) or sheet.cues[idx + 1].kind != "dialogue":
                errors.append(f"{cue.cue_id}: duck_under_next must be followed by a dialogue cue")
            else:
                next_cue = sheet.cues[idx + 1]
                if next_cue.duck_under_next:
                    errors.append(f"{cue.cue_id}: consecutive duck_under_next cues are forbidden")
                if next_cue.act_id != cue.act_id:
                    errors.append(
                        f"{cue.cue_id}: duck_under_next target {next_cue.cue_id} crosses act boundary "
                        f"({cue.act_id!r} -> {next_cue.act_id!r})"
                    )
                next_lang = _eff_lang(next_cue, registry)
                if next_lang not in ("zh", "zh-en"):
                    errors.append(
                        f"{cue.cue_id}: duck_under_next target {next_cue.cue_id} must be Mandarin/zh-en VO, got {next_lang!r}"
                    )
            subcues = split_cue_into_subcues_for_drama3(cue, domain=DOMAIN)
            if len(subcues) != 1:
                errors.append(
                    f"{cue.cue_id}: duck_under_next cue split into {len(subcues)} sub-cues (must stay 1)"
                )

        # Drama 3 Xianxia-leak guard (both attempt 1 and attempt 2)
        for attempt in (1, 2):
            rendered = translate_cue_to_drama3_input(cue, prof, attempt=attempt, domain=DOMAIN)
            for tok in XIANXIA_LEAK_TOKENS:
                if tok in rendered:
                    errors.append(
                        f"{cue.cue_id}: Drama 3 attempt={attempt} leaked Xianxia token {tok!r}"
                    )

        # Crosstalk & interruption speaker-turn guards
        if float(cue.gap_after_s) < 0.0:
            next_dlg = _find_next_dialogue_cue(sheet.cues, idx)
            if next_dlg is not None and next_dlg.role_id == cue.role_id:
                errors.append(
                    f"{cue.cue_id}: same-speaker negative-gap self-overlap "
                    f"(gap_after_s={cue.gap_after_s} into {next_dlg.cue_id}, role_id={cue.role_id!r})"
                )
        if any(t.lower().strip() == "interrupting" for t in tags):
            prev_dlg = _find_prev_dialogue_cue(sheet.cues, idx)
            if prev_dlg is not None and prev_dlg.role_id == cue.role_id:
                errors.append(
                    f"{cue.cue_id}: same-speaker [interrupting] self-interruption "
                    f"(follows {prev_dlg.cue_id}, role_id={cue.role_id!r})"
                )

        # Anti-cliché & external-source firewall (spoken text + subtitle_translation + inline tags;
        # director_note intentionally unscanned so production guardrails remain allowed)
        low = spoken.lower()
        sub_low = cue.subtitle_translation.lower()
        tags_low = " ".join(tags).lower()
        for banned in BANNED_CLICHES_AND_LEAKS:
            if banned in low:
                errors.append(f"{cue.cue_id}: banned phrase/leak {banned!r} in spoken text")
            if sub_low and banned in sub_low:
                errors.append(
                    f"{cue.cue_id}: banned phrase/leak {banned!r} in subtitle_translation"
                )
            if tags_low and banned in tags_low:
                errors.append(
                    f"{cue.cue_id}: banned phrase/leak {banned!r} in inline tags"
                )

    # Anti-cliché & external-source firewall on sheet.title and every act.title
    sheet_title_low = (sheet.title or "").lower()
    for banned in BANNED_CLICHES_AND_LEAKS:
        if banned in sheet_title_low:
            errors.append(f"{sheet.episode_id}: banned phrase/leak {banned!r} in sheet.title")
    for act in sheet.acts:
        act_title_low = (act.title or "").lower()
        for banned in BANNED_CLICHES_AND_LEAKS:
            if banned in act_title_low:
                errors.append(
                    f"{sheet.episode_id}:{act.act_id}: banned phrase/leak {banned!r} in act.title"
                )

    return errors


def lint_e001_variant(
    sheet: EpisodeCueSheet,
    registry: VoiceCastingRegistry,
    variant_id: str,
) -> list[str]:
    """Enforce ALL shared E001 invariants + variant-specific structural constraints."""
    errors = _lint_common_dialogue_cues(sheet, registry, is_e001=True)
    m = compute_variant_metrics(sheet, registry)

    if sheet.episode_id != variant_id:
        errors.append(f"episode_id={sheet.episode_id!r} != expected {variant_id!r}")
    if sheet.mode != "bilingual_business_drama":
        errors.append(f"mode={sheet.mode!r} != 'bilingual_business_drama'")
    if sheet.chapter_number != 1:
        errors.append(f"chapter_number={sheet.chapter_number} != 1")

    # Core cast & 100% US+UK RP check
    bad_roles = set(m["roles_used"]) - CORE_E001_ROLES
    if bad_roles:
        errors.append(f"E001 uses forbidden non-core roles: {sorted(bad_roles)}")
    if m["core_us_uk_en_pct"] < 100.0:
        errors.append(f"core_us_uk_en_pct={m['core_us_uk_en_pct']}% < 100.0%")

    # All 8 mandatory phrase groups (13 sub-phrases) in Drama Acts 1-4
    if m["mandatory_phrase_groups_hit"] != 8 or m["missing_subphrases"]:
        errors.append(
            f"Missing mandatory E001 sub-phrases in Drama Acts 1-4: {m['missing_subphrases']}"
        )

    # Runtime budgets (both empirical AND synth-dry-test checked)
    if not (600.0 <= m["total_duration_est_s"] <= 840.0):
        errors.append(
            f"total_duration_est_s={m['total_duration_est_s']} outside [600.0, 840.0]"
        )
    if not (480.0 <= m["drama_duration_est_s"] <= 600.0):
        errors.append(
            f"drama_duration_est_s={m['drama_duration_est_s']} outside [480.0, 600.0]"
        )
    if not (165.0 <= m["debrief_duration_est_s"] <= 210.0):
        errors.append(
            f"debrief_duration_est_s={m['debrief_duration_est_s']} outside [165.0, 210.0]"
        )
    if not (600.0 <= m["synth_total_duration_est_s"] <= 840.0):
        errors.append(
            f"synth_total_duration_est_s={m['synth_total_duration_est_s']} outside [600.0, 840.0]"
        )
    if not (480.0 <= m["synth_drama_duration_est_s"] <= 600.0):
        errors.append(
            f"synth_drama_duration_est_s={m['synth_drama_duration_est_s']} outside [480.0, 600.0]"
        )
    if not (165.0 <= m["synth_debrief_duration_est_s"] <= 210.0):
        errors.append(
            f"synth_debrief_duration_est_s={m['synth_debrief_duration_est_s']} outside [165.0, 210.0]"
        )

    # Act 5 shadowing requirements
    if m["act5_slow_count"] < 3:
        errors.append(f"Act 5 0.80x slow cues={m['act5_slow_count']} < 3")
    if m["act5_shadow_gap_2s_count"] < 3:
        errors.append(
            f"Act 5 1.0x shadowing cues with gap_after_s >= 2.0s = {m['act5_shadow_gap_2s_count']} < 3"
        )

    # Act 5 Chinglish-vs-native contrast & NovaEdge brand identity checks
    act5_spoken_low = " ".join(
        extract_tags_and_spoken_text(c.text)[1]
        for c in sheet.cues
        if c.act_id == DEBRIEF_ACT_ID and c.kind == "dialogue"
    ).lower()
    chinglish_contrast_tokens = ("直译", "中式", "chinglish", "别说", "不要说", "菜鸟", "对比")
    if not any(tok in act5_spoken_low for tok in chinglish_contrast_tokens):
        errors.append(
            f"{variant_id}: Act 5 debrief missing Chinglish-vs-native contrast cues "
            f"(expected one of {chinglish_contrast_tokens})"
        )
    all_spoken_low = " ".join(
        extract_tags_and_spoken_text(c.text)[1]
        for c in sheet.cues
        if c.kind == "dialogue"
    ).lower()
    if "novaedge" not in all_spoken_low and "灵犀" not in all_spoken_low:
        errors.append(f"{variant_id}: dialogue missing NovaEdge / 灵犀 brand identity")

    # Variant-specific structural differentiation rules
    if variant_id == "E001_VA":
        if m["inner_monologue_count"] != 0:
            errors.append(f"E001_VA must have 0 inner_monologue cues, got {m['inner_monologue_count']}")
        if m["crosstalk_count"] < 6:
            errors.append(f"E001_VA crosstalk_count={m['crosstalk_count']} < 6")
        if not (0.65 <= m["drama_en_ratio"] <= 0.75):
            errors.append(f"E001_VA drama_en_ratio={m['drama_en_ratio']} outside [0.65, 0.75]")
        if m["act5_roles"] != ["lin_chen"]:
            errors.append(f"E001_VA Act 5 must be solo lin_chen, got {m['act5_roles']}")

    elif variant_id == "E001_VB":
        if m["inner_monologue_count"] < 6:
            errors.append(f"E001_VB inner_monologue_count={m['inner_monologue_count']} < 6")
        # Every inner_monologue cue in E001_VB must be preceded by freeze_frame_sub_drop
        for idx, cue in enumerate(sheet.cues):
            if cue.kind == "dialogue" and cue.acoustic_space == "inner_monologue":
                prev = sheet.cues[idx - 1] if idx > 0 else None
                if not (prev and prev.kind == "sfx" and prev.motif_id == "freeze_frame_sub_drop"):
                    errors.append(
                        f"E001_VB {cue.cue_id}: inner_monologue must be preceded by freeze_frame_sub_drop SFX"
                    )
        if m["crosstalk_count"] < 4:
            errors.append(f"E001_VB crosstalk_count={m['crosstalk_count']} < 4")
        if not (0.50 <= m["drama_en_ratio"] <= 0.60):
            errors.append(f"E001_VB drama_en_ratio={m['drama_en_ratio']} outside [0.50, 0.60]")
        if not {"lin_chen", "zhou_mo"}.issubset(set(m["act5_roles"])):
            errors.append(f"E001_VB Act 5 must feature lin_chen + zhou_mo, got {m['act5_roles']}")

    elif variant_id == "E001_VC":
        if m["inner_monologue_count"] != 0:
            errors.append(f"E001_VC must have 0 inner_monologue cues, got {m['inner_monologue_count']}")
        if m["phone_call_count"] < 4:
            errors.append(f"E001_VC phone_call_count={m['phone_call_count']} < 4")
        if m["sfx_cues"] < 13:
            errors.append(f"E001_VC sfx_cues={m['sfx_cues']} < 13")
        if m["crosstalk_count"] < 6:
            errors.append(f"E001_VC crosstalk_count={m['crosstalk_count']} < 6")
        if not (0.55 <= m["drama_en_ratio"] <= 0.65):
            errors.append(f"E001_VC drama_en_ratio={m['drama_en_ratio']} outside [0.55, 0.65]")
        # Act 5 antagonist cold-call roleplay check
        act5_cues = [c for c in sheet.cues if c.act_id == DEBRIEF_ACT_ID and c.kind == "dialogue"]
        antag_drill_found = False
        for idx, c in enumerate(act5_cues):
            if c.role_id in ("victoria_vance", "alistair_finch") and float(c.gap_after_s) >= 2.5:
                if idx + 1 < len(act5_cues) and act5_cues[idx + 1].role_id == "lin_chen":
                    antag_drill_found = True
                    break
        if not antag_drill_found:
            errors.append(
                "E001_VC Act 5 must include antagonist cold-call attack (gap_after_s >= 2.5s) followed by lin_chen counter"
            )

    elif variant_id == "E001_VD":
        if m["duck_under_next_count"] < 2:
            errors.append(f"E001_VD duck_under_next_count={m['duck_under_next_count']} < 2")
        if m["crosstalk_count"] < 3:
            errors.append(f"E001_VD crosstalk_count={m['crosstalk_count']} < 3")
        if not (0.50 <= m["drama_en_ratio"] <= 0.60):
            errors.append(f"E001_VD drama_en_ratio={m['drama_en_ratio']} outside [0.50, 0.60]")
        if m["studio_warm_drama_count"] < 3:
            errors.append(
                f"E001_VD must use retrospective studio_warm documentary narration in Acts 1-4 (got {m['studio_warm_drama_count']})"
            )
        act5_text = " ".join(
            extract_tags_and_spoken_text(c.text)[1]
            for c in sheet.cues
            if c.act_id == DEBRIEF_ACT_ID and c.kind == "dialogue"
        )
        teaser_markers = ("帕洛阿尔托", "晚宴", "六十天", "亚马逊")
        if sum(1 for tok in teaser_markers if tok in act5_text) < 2:
            errors.append(
                "E001_VD Act 5 must include a ~30s E002 teaser referencing Palo Alto dinner / 60-day / Amazon continuity"
            )
    else:
        errors.append(f"Unknown E001 variant_id {variant_id!r}")

    return errors


def lint_audition_pack(
    sheet: EpisodeCueSheet,
    registry: VoiceCastingRegistry,
) -> list[str]:
    """Validate AUDITION_GLOBAL_EDGE against G1–G8 audition gate requirements."""
    errors = _lint_common_dialogue_cues(sheet, registry, is_e001=False)
    if sheet.episode_id != "AUDITION_GLOBAL_EDGE":
        errors.append(f"Audition episode_id={sheet.episode_id!r} != 'AUDITION_GLOBAL_EDGE'")
    if sheet.mode != "audition_pack":
        errors.append(f"Audition mode={sheet.mode!r} != 'audition_pack'")
    if not (12 <= len(sheet.cues) <= 16):
        errors.append(f"Audition cue count={len(sheet.cues)} outside [12, 16]")

    dlg = [c for c in sheet.cues if c.kind == "dialogue"]
    sfx = [c for c in sheet.cues if c.kind == "sfx"]
    roles_present = {c.role_id for c in dlg}
    missing_roles = ALL_LOCKED_ROLES - roles_present
    if missing_roles:
        errors.append(f"Audition missing locked roles: {sorted(missing_roles)}")

    # G1: lin_chen must appear in BOTH EN and ZH inner_monologue
    lin_langs = {_eff_lang(c, registry) for c in dlg if c.role_id == "lin_chen"}
    if not ({"en", "zh"}.issubset(lin_langs) or ({"en", "zh-en"}.issubset(lin_langs))):
        errors.append(f"Audition G1 failed: lin_chen langs={sorted(lin_langs)} (need EN + ZH)")
    if not any(c.role_id == "lin_chen" and c.acoustic_space == "inner_monologue" for c in dlg):
        errors.append("Audition G1/G6 failed: lin_chen needs inner_monologue cue")

    # G5: 0.80x slow + 1.0x shadowing gap >= 2.0
    if not any(abs(float(c.playback_rate) - 0.8) < 1e-6 for c in dlg):
        errors.append("Audition G5 failed: missing playback_rate=0.8 slow cue")
    if not any(
        abs(float(c.playback_rate) - 1.0) < 1e-6 and float(c.gap_after_s) >= 2.0 for c in dlg
    ):
        errors.append("Audition G5 failed: missing 1.0x shadowing cue with gap_after_s >= 2.0s")

    # G6: negative-gap crosstalk + required acoustic spaces + duck_under_next pair
    has_cross_speaker_crosstalk = False
    for idx, c in enumerate(sheet.cues):
        if c.kind == "dialogue" and -0.25 <= float(c.gap_after_s) <= -0.05:
            next_dlg = _find_next_dialogue_cue(sheet.cues, idx)
            if next_dlg is not None and next_dlg.role_id != c.role_id:
                has_cross_speaker_crosstalk = True
                break
    if not has_cross_speaker_crosstalk:
        errors.append("Audition G6 failed: missing cross-speaker negative-gap crosstalk cue")
    spaces_present = {c.acoustic_space for c in dlg}
    for req_space in ("boardroom", "inner_monologue", "phone_call", "vast_hall", "studio_warm", "dry"):
        if req_space not in spaces_present:
            errors.append(f"Audition missing required acoustic_space={req_space!r}")
    if not any(c.duck_under_next for c in dlg):
        errors.append("Audition missing duck_under_next=True test pair")
    if len(sfx) < 2:
        errors.append(f"Audition needs >= 2 SFX motifs, got {len(sfx)}")
    if len(sheet.acts) < 1:
        errors.append("Audition needs >= 1 ActMusicSpec for 3-bus mastering")

    return errors
