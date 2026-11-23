"""Shared opaque-box E2E helpers, ground-truth corpus oracles, audio DSP tools,
and 18-family positive/negative mutation self-test harness for Global Edge
(projects/global_edge/).

Zero third-party dependencies (Python 3.11+ stdlib + system ffmpeg/ffprobe).
NEVER place __init__.py inside tests/e2e_global_edge/.
"""

from __future__ import annotations

import array
import ast
import dataclasses
import inspect
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import wave
import zipfile
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

# ---------------------------------------------------------------------------
# Path Setup (works whether invoked with or without PYTHONPATH=src)
# ---------------------------------------------------------------------------

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[1]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

# ---------------------------------------------------------------------------
# Verbatim Canonical Paths (PROJECT.md § Code Layout)
# ---------------------------------------------------------------------------

GLOBAL_EDGE_ROOT = REPO_ROOT / "projects" / "global_edge"
DIR_BIBLE = GLOBAL_EDGE_ROOT / "00_节目圣经与第一季24集总纲"
DIR_CORPUS = GLOBAL_EDGE_ROOT / "01_视频号语料与商业词库"
DIR_SCRIPTS_OUT = GLOBAL_EDGE_ROOT / "02_分集广播剧台本"
DIR_DIST = GLOBAL_EDGE_ROOT / "03_全平台分发与切片方案"
DIR_PY_SCRIPTS = GLOBAL_EDGE_ROOT / "scripts"
DIR_COLAB = REPO_ROOT / "colab_96gb"

RAW_ARSENAL_JSON = Path("/tmp/arsenal_100_queue.json")
PATH_PYPROJECT = REPO_ROOT / "pyproject.toml"
PATH_README = GLOBAL_EDGE_ROOT / "README.md"

PATH_RESEARCH_REPORT = DIR_BIBLE / "RESEARCH_REPORT.md"
PATH_SHOW_BIBLE = DIR_BIBLE / "SHOW_BIBLE.md"
PATH_ACCENT_MANUAL = DIR_BIBLE / "ACCENT_AND_PROSODY_MANUAL.md"
PATH_SEASON1_BLUEPRINT = DIR_BIBLE / "SEASON1_24EP_BLUEPRINT.md"
PATH_SEASON1_MAP = DIR_BIBLE / "season1_24ep_map.json"
PATH_REGISTRY = DIR_BIBLE / "voice_casting_registry.json"
PATH_ANCHOR_SOURCES = DIR_BIBLE / "anchor_sources.json"
PATH_ANCHOR_SPEC = DIR_BIBLE / "VOICE_ANCHOR_ACQUISITION_SPEC.md"

PATH_CORPUS_JSON = DIR_CORPUS / "corpus_100_structured.json"
PATH_LEXICON_JSON = DIR_CORPUS / "executive_lexicon.json"
PATH_CORPUS_REPORT = DIR_CORPUS / "CORPUS_INTELLIGENCE_REPORT.md"

PATH_AUDITION_JSON = DIR_SCRIPTS_OUT / "AUDITION_GLOBAL_EDGE_全口音与双语飙戏试听包.json"
PATH_AUDITION_MD = DIR_SCRIPTS_OUT / "AUDITION_GLOBAL_EDGE_全口音与双语飙戏试听包.md"

VARIANT_JSON_PATHS: dict[str, Path] = {
    "E001_VA": DIR_SCRIPTS_OUT / "E001_VA_HBO纯飙戏冷峻商战版_完整双语台本.json",
    "E001_VB": DIR_SCRIPTS_OUT / "E001_VB_纸牌屋冻帧潜台词狙击版_完整双语台本.json",
    "E001_VC": DIR_SCRIPTS_OUT / "E001_VC_三时区惊悚推进与实战跟读版_完整双语台本.json",
    "E001_VD": DIR_SCRIPTS_OUT / "E001_VD_纪实同传叠音混合版_完整双语台本.json",
}
VARIANT_MD_PATHS: dict[str, Path] = {
    k: v.with_suffix(".md") for k, v in VARIANT_JSON_PATHS.items()
}
ALL_5_CUE_SHEETS: dict[str, Path] = {
    "AUDITION_GLOBAL_EDGE": PATH_AUDITION_JSON,
    **VARIANT_JSON_PATHS,
}
ALL_5_MD_PATHS: dict[str, Path] = {
    "AUDITION_GLOBAL_EDGE": PATH_AUDITION_MD,
    **VARIANT_MD_PATHS,
}

PATH_RUBRIC_MD = DIR_SCRIPTS_OUT / "E001_COMPARATIVE_EVAL_RUBRIC.md"
PATH_LAUNCH_KIT_MD = DIR_DIST / "LAUNCH_KIT_AND_E001_45S_CLIPS.md"
PATH_COMPANION_MD = DIR_DIST / "E001_BILINGUAL_COMPANION_MANUAL.md"

SCRIPT_EXTRACT_CORPUS = DIR_PY_SCRIPTS / "extract_100_clips_corpus.py"
SCRIPT_EXPORT_BUNDLE = DIR_PY_SCRIPTS / "export_drama3_bundle.py"
SCRIPT_BUILD_E001 = DIR_PY_SCRIPTS / "build_e001_variants.py"

COLAB_PREPARE_ANCHORS = DIR_COLAB / "prepare_global_edge_voice_anchors.py"
COLAB_RUN_STUDIO = DIR_COLAB / "run_global_edge_96gb_studio.py"
COLAB_LAUNCH_G4 = DIR_COLAB / "launch_g4_global_edge_drama3.py"
COLAB_NOTEBOOK = DIR_COLAB / "Global_Edge_96GB_Drama3_Studio.ipynb"

LEGACY_BUFFETT_REGISTRY = (
    REPO_ROOT
    / "projects"
    / "buffett_letters"
    / "00_节目圣经与第一季12期总纲"
    / "voice_casting_registry.json"
)
LEGACY_BUFFETT_E001 = (
    REPO_ROOT
    / "projects"
    / "buffett_letters"
    / "02_分期圆桌台本"
    / "E001_2008年致股东信_满地是血的夜晚谁在裸泳_完整圆桌台本.json"
)

# ---------------------------------------------------------------------------
# Ground-Truth Corpus Oracle Constants (/tmp/arsenal_100_queue.json)
# ---------------------------------------------------------------------------

CORPUS_IDS_BY_TOPIC: dict[str, tuple[str, ...]] = {
    "AI": (
        "01_AI_DHH",
        "006_AI", "007_AI", "008_AI", "009_AI", "010_AI",
        "011_AI", "012_AI", "013_AI", "014_AI", "015_AI",
        "016_AI", "017_AI", "018_AI", "019_AI", "020_AI",
        "021_AI", "022_AI", "023_AI", "024_AI", "025_AI",
        "026_AI", "027_AI", "029_AI", "030_AI",
    ),
    "BUSINESS": (
        "02_BIZ_Anthropic",
        "030_BIZ", "031_BIZ", "032_BIZ", "033_BIZ", "034_BIZ",
        "035_BIZ", "036_BIZ", "037_BIZ", "038_BIZ", "039_BIZ",
        "040_BIZ", "041_BIZ", "042_BIZ", "043_BIZ", "044_BIZ",
        "045_BIZ", "047_BIZ", "048_BIZ", "049_BIZ", "050_BIZ",
        "051_BIZ", "052_BIZ", "053_BIZ", "054_BIZ",
    ),
    "FINANCE": (
        "03_FIN_Dalio",
        "054_FIN", "055_FIN", "056_FIN", "057_FIN", "058_FIN",
        "059_FIN", "060_FIN", "061_FIN", "062_FIN", "063_FIN",
        "064_FIN", "065_FIN", "066_FIN", "067_FIN", "068_FIN",
        "069_FIN", "070_FIN", "071_FIN", "072_FIN", "073_FIN",
        "074_FIN", "075_FIN", "076_FIN", "077_FIN",
    ),
    "US_CHINA": (
        "04_USCHINA_Jensen", "05_USCHINA_Robots",
        "078_USC", "079_USC", "080_USC", "081_USC", "082_USC",
        "083_USC", "084_USC", "085_USC", "086_USC", "087_USC",
        "088_USC", "089_USC", "090_USC", "091_USC", "092_USC",
        "093_USC", "094_USC", "095_USC", "096_USC", "097_USC",
        "098_USC", "099_USC", "100_USC",
    ),
}

EXPECTED_100_CLIP_IDS: frozenset[str] = frozenset(
    cid for ids in CORPUS_IDS_BY_TOPIC.values() for cid in ids
)
assert len(EXPECTED_100_CLIP_IDS) == 100

CLIP_TOPIC_LOOKUP: dict[str, str] = {
    cid: topic for topic, ids in CORPUS_IDS_BY_TOPIC.items() for cid in ids
}

COLLIDING_PREFIX_IDS: tuple[str, ...] = ("030_AI", "030_BIZ", "054_BIZ", "054_FIN")
ABSENT_PREFIXES: tuple[str, ...] = ("028_", "046_")
E001_SEED_CLIP_IDS: frozenset[str] = frozenset(
    {"02_BIZ_Anthropic", "012_AI", "039_BIZ", "090_USC", "059_FIN"}
)
EXPECTED_TOTAL_SEGMENTS = 1408
EXPECTED_MEDIAN_WPM = 170.20

ZERO_HIT_WORLD_BRIDGE_TERMS: tuple[str, ...] = (
    "best buy",
    "selfridges",
    "slotting fee",
    "chargeback",
    "moq",
    "sell-through",
    "gdpr",
    "privacy",
    "compliance",
    "lawsuit",
    "antitrust",
    "sanctions",
    "decoupling",
)

# 8 mandatory E001 phrases honoring exact PROJECT.md §5 OR-clauses
# Structure: (phrase_id, human_label, tuple_of_AND_clauses)
# where each AND-clause is a tuple of acceptable OR-alternatives (case-insensitive).
E001_MANDATORY_PHRASES: tuple[tuple[str, str, tuple[tuple[str, ...], ...]], ...] = (
    ("P1", "phantom number", (("phantom number",),)),
    (
        "P2",
        "not a cash loss + income statement",
        (
            ("not a cash loss",),
            ("flowed through into the income statement", "income statement"),
        ),
    ),
    ("P3", "capital-efficient", (("capital-efficient",),)),
    (
        "P4",
        "10 times/10x the throughput + Pick your favorite number",
        (
            ("10 times the throughput", "10x the throughput"),
            ("pick your favorite number",),
        ),
    ),
    ("P5", "In other words", (("in other words",),)),
    (
        "P6",
        "eating into budgets + a really hard trade-off",
        (("eating into budgets",), ("a really hard trade-off",)),
    ),
    (
        "P7",
        "What is good enough + run this thing a million times",
        (("what is good enough",), ("run this thing a million times",)),
    ),
    (
        "P8",
        "upside + When are you going to get it",
        (("upside",), ("when are you going to get it",)),
    ),
)

# All 38 raw corpus anomalies across 23 clips (37 ASR typos + [snorts] = 51 raw hits)
# Tuple: (clip_id, label, pattern_str, regex_flags, clean_hint, batch)
RAW_CORPUS_ANOMALIES: tuple[tuple[str, str, str, int, str, str], ...] = (
    # Batch A (11 clips, 16 anomalies)
    ("010_AI", "like5 trillion", r"like5\s+trillion", re.IGNORECASE, "like $5 trillion", "A"),
    ("014_AI", "Hammarabi", r"\bHammarabi\b", re.IGNORECASE, "Hammurabi", "A"),
    ("018_AI", "1,24 tokens", r"\b1,24\s+tokens\b", re.IGNORECASE, "1,024 tokens", "A"),
    ("021_AI", "Abene", r"\bAbene\b", re.IGNORECASE, "Abilene", "A"),
    ("069_FIN", "law of holds", r"\blaw of holds\b", re.IGNORECASE, "law of holes", "A"),
    ("069_FIN", "caught in half", r"\bcaught in half\b", re.IGNORECASE, "cut in half", "A"),
    ("070_FIN", "tor rate", r"\btor rate\b", re.IGNORECASE, "torrid rate", "A"),
    ("070_FIN", "a trillion change", r"\ba trillion change\b", re.IGNORECASE, "a trillion and change", "A"),
    ("073_FIN", "cast robbery", r"\bcast robbery\b", re.IGNORECASE, "catastrophe", "A"),
    ("082_USC", "one tiny floor", r"\bone tiny floor\b", re.IGNORECASE, "one tiny flaw", "A"),
    ("082_USC", "Tynan Science Park", r"\bTynan Science Park\b", re.IGNORECASE, "Tainan Science Park", "A"),
    ("086_USC", "Kaiser Supply Chain", r"\bKaiser Supply Chain\b", re.IGNORECASE, "kinds of supply chain", "A"),
    ("090_USC", "Jipu", r"\bJipu\b", re.IGNORECASE, "Zhipu", "A"),
    ("093_USC", "$122,000", r"\$122,000\b", 0, "$12,000", "A"),
    ("093_USC", "$115,000", r"\$115,000\b", 0, "$15,000", "A"),
    ("093_USC", "BD's", r"\bBD's\b", 0, "BYD's", "A"),
    # Batch B (11 clips, 21 anomalies — includes word-boundary traps \bClaud\b & case-sensitive \bMs\b)
    ("015_AI", "grock 3", r"\bgrock\s+3\b", re.IGNORECASE, "Grok 3", "B"),
    ("015_AI", "Claud", r"\bClaud\b", re.IGNORECASE, "Claude", "B"),
    ("031_BIZ", "dber cartoon", r"\bdber cartoon\b", re.IGNORECASE, "Dilbert cartoon", "B"),
    ("031_BIZ", "Ms", r"\bMs\b", 0, "mats", "B"),
    ("045_BIZ", "Palanteer", r"\bPalanteer\b", re.IGNORECASE, "Palantir", "B"),
    ("045_BIZ", "Palunteers", r"\bPalunteers\b", re.IGNORECASE, "Palantir", "B"),
    ("050_BIZ", "r d v span", r"\br d v span\b", re.IGNORECASE, "R&D spend", "B"),
    ("051_BIZ", "gp4", r"\bgp4\b", re.IGNORECASE, "GPT-4", "B"),
    ("054_BIZ", "crude mission", r"\bcrude mission\b", re.IGNORECASE, "crewed mission", "B"),
    ("054_BIZ", "totally shelf", r"\btotally shelf\b", re.IGNORECASE, "totally shelved", "B"),
    ("055_FIN", "truckee miller", r"\btruckee miller\b", re.IGNORECASE, "Druckenmiller", "B"),
    ("055_FIN", "drucker miller", r"\bdrucker miller\b", re.IGNORECASE, "Druckenmiller", "B"),
    ("055_FIN", "sorrows", r"\bsorrows\b", re.IGNORECASE, "Soros", "B"),
    ("064_FIN", "tight money suit", r"\btight money suit\b", re.IGNORECASE, "tight money soon", "B"),
    ("064_FIN", "easy money suit", r"\beasy money suit\b", re.IGNORECASE, "easy money soon", "B"),
    ("085_USC", "chakyang", r"\bchakyang\b", re.IGNORECASE, "Zhejiang", "B"),
    ("099_USC", "Mas son", r"\bMas son\b", re.IGNORECASE, "Masayoshi Son", "B"),
    ("099_USC", "Arison", r"\bArison\b", re.IGNORECASE, "Larry Ellison", "B"),
    ("099_USC", "Sam Alman", r"\bSam Alman\b", re.IGNORECASE, "Sam Altman", "B"),
    ("099_USC", "do announcement", r"\bdo announcement\b", re.IGNORECASE, "dollar announcement", "B"),
    ("100_USC", "UBEC", r"\bUBEC\b", re.IGNORECASE, "UBTECH", "B"),
    # Non-speech bracket tag (1 clip, 1 anomaly)
    ("087_USC", "[snorts]", r"\[snorts\]", re.IGNORECASE, "(stripped)", "TAG"),
)
assert len(RAW_CORPUS_ANOMALIES) == 38

# ---------------------------------------------------------------------------
# Engine, Role, Accent & Domain Constants (PROJECT.md § Interface Contracts)
# ---------------------------------------------------------------------------

CANONICAL_MODEL_IDS: dict[str, str] = {
    "tts_model_id": "fishaudio/drama-3",
    "sfx_model_id": "OpenMOSS-Team/MOSS-SoundEffect-v2.0",
    "music_model_id": "ACE-Step/acestep-v15-xl-turbo-diffusers",
    "asr_model_id": "faster-whisper-small-int8",
    "domain": "business_english_drama",
}

CORE_E001_ROLES: tuple[str, ...] = (
    "lin_chen",
    "zhou_mo",
    "victoria_vance",
    "alistair_finch",
)
CANONICAL_CORE_ROLES: tuple[str, ...] = (
    "lin_chen",
    "zhou_mo",
    "victoria_vance",
    "alistair_finch",
    "claire_chen_gc",
)
CANONICAL_GUEST_ROLES: tuple[str, ...] = (
    "rajiv_menon",
    "wei_ling_tan",
    "henrik_lindqvist",
)
CANONICAL_ALL_8_ROLES: tuple[str, ...] = CANONICAL_CORE_ROLES + CANONICAL_GUEST_ROLES

EXPECTED_ROLE_ACCENTS: dict[str, str] = {
    "lin_chen": "zh_en_bilingual_us",
    "zhou_mo": "zh_mainland_sz",
    "victoria_vance": "us_silicon_valley",
    "alistair_finch": "uk_london_rp",
    "claire_chen_gc": "us_nyc",
    "rajiv_menon": "intl_indian_exec",
    "wei_ling_tan": "intl_singapore_vc",
    "henrik_lindqvist": "intl_eu_legal",
}

CORE_US_UK_ACCENT_CODES: frozenset[str] = frozenset(
    {"us_silicon_valley", "us_nyc", "uk_london_rp", "zh_en_bilingual_us"}
)
INTL_GUEST_ACCENT_CODES: frozenset[str] = frozenset(
    {"intl_indian_exec", "intl_singapore_vc", "intl_eu_legal"}
)

EXPECTED_9_ACOUSTIC_SPACES: tuple[str, ...] = (
    "dry",
    "mental_realm",
    "memory_echo",
    "vast_hall",
    "studio_warm",
    "vintage_study",
    "inner_monologue",
    "boardroom",
    "phone_call",
)

REQUIRED_13_HBO_TAGS: tuple[str, ...] = (
    "measured",
    "deadpan",
    "icy polite",
    "blunt",
    "guarded",
    "skeptical",
    "firmly",
    "understated",
    "tense",
    "confident",
    "aside",
    "coach",
    "interrupting",
)

VARIANT_RESOLVER_REGEX = re.compile(r"^(E\d{3}(?:_V[A-Z0-9]+|[A-Z])?)(?:_|\.|$)")
LEGACY_BROKEN_RESOLVER_REGEX = re.compile(r"^(E\d{3})(?:_|\.|$)")

BANNED_YOUTUBE_SHORTS_TERMS: tuple[str, ...] = (
    "youtube",
    "视频号",
    "上期切片",
    "短视频切片",
    "这条视频",
    "这条切片",
)
BANNED_CLICHES: tuple[str, ...] = (
    "各位听众",
    "欢迎收听今天的英语课",
    "问到根子上了",
    "这个比方绝了",
)
BANNED_ELEMENTARY_ESL: tuple[str, ...] = (
    "hello, how are you today",
    "let's learn a new word",
    "welcome to today's english class",
    "repeat after me class",
)
BANNED_MELODRAMA_YELLING_TAGS: frozenset[str] = frozenset(
    {"shouting", "screaming", "hysterical", "roaring"}
)
XIANXIA_PLOT_STRINGS: tuple[str, ...] = (
    "修仙",
    "引气",
    "宗门",
    "筑基",
    "金丹",
    "元婴",
    "炼丹",
    "仙侠",
)
VARIANT_CROSSTALK_MIN: dict[str, int] = {
    "E001_VA": 6,
    "E001_VB": 4,
    "E001_VC": 6,
    "E001_VD": 3,
}

ALLOWED_LOCAL_ELEVENLABS_HELPERS: frozenset[str] = frozenset(
    {"probe_duration_seconds", "ffmpeg_available", "ffprobe_available"}
)

ANCHOR_SOURCE_CONTAINERS: tuple[str, ...] = (
    "role_mappings",
    "roles",
    "anchors",
    "characters",
    "sources",
    "voice_anchors",
)
ANCHOR_POLICY_META_KEYS: frozenset[str] = frozenset(
    {
        "policy",
        "policies",
        "notes",
        "note",
        "comment",
        "comments",
        "description",
        "rationale",
        "rules",
        "guardrails",
        "compliance",
        "forbidden_providers",
        "forbidden_sources",
        "banned_providers",
        "disallowed_providers",
    }
)
ANCHOR_ACTUAL_SOURCE_FIELDS: frozenset[str] = frozenset(
    {
        "source_type",
        "source",
        "provider",
        "engine",
        "url",
        "source_url",
        "yt_url",
        "youtube_url",
        "fallback_url",
        "fallback_raw_url",
        "audio_url",
        "source_voice_name",
        "voice_name",
        "voice_id",
        "method",
        "acquisition_method",
        "primary_source",
        "backup_source",
        "primary",
        "fallback",
        "command",
        "cli",
        "default_provider",
        "default_source",
        "fallback_engine",
    }
)
_SYNTHETIC_ANCHOR_RE = re.compile(
    r"(?:edge[-_]?tts|elevenlabs|api\.elevenlabs\.io|[a-z]{2}-[a-z]{2}-[a-z0-9]+neural\b|\bneural\b)",
    re.IGNORECASE,
)

_XIANXIA_STRICT_TROPES: tuple[str, ...] = (
    "引气",
    "宗门",
    "炼气",
    "筑基",
    "金丹",
    "元婴",
    "化神",
    "渡劫",
    "飞升",
    "辟谷",
    "灵根",
    "道侣",
    "丹田",
    "道行",
    "炼丹",
)
_ML_LIANDAN_JARGON_RE = re.compile(r"(?:预训练|大模型|模型|算力|AI|GPU)\s*炼丹", re.IGNORECASE)
_XIANXIA_GENRE_TERMS: tuple[str, ...] = ("修仙", "仙侠")
_GUARDRAIL_NEGATION_RE = re.compile(
    r"(?:严禁|禁止|非|零|切忌|不得|不再|绝不|无|回退|规避|消除|杜绝|不同于|摒弃|摆脱|脱离|"
    r"(?:^|[^\d.])0\s*(?:条|次|词|个|仙侠|修仙|泄露)|"
    r"zero|no\s+|non-|never|forbid|avoid|eliminate|fallback)",
    re.IGNORECASE,
)
_BAN_TABLE_HEADER_RE = re.compile(
    r"(?:严禁|违禁|禁止|禁用|红线|forbidden|banned|prohibited)",
    re.IGNORECASE,
)
_LEXICON_SLASH_STOPWORDS: frozenset[str] = frozenset(
    {
        "that", "this", "with", "from", "have", "were", "been", "they", "them",
        "what", "when", "will", "into", "your", "some", "than", "then", "also",
        "just", "very", "more", "most", "such", "only", "over", "here", "there",
    }
)

# ---------------------------------------------------------------------------
# Pre-M1 / Post-M1 Safe Introspection & Artifact Loaders
# ---------------------------------------------------------------------------

def require_file(path: Path, label: str = "") -> Path:
    if not path.is_file():
        desc = f" ({label})" if label else ""
        raise AssertionError(f"Required artifact missing{desc}: {path}")
    return path


def require_dir(path: Path, label: str = "") -> Path:
    if not path.is_dir():
        desc = f" ({label})" if label else ""
        raise AssertionError(f"Required directory missing{desc}: {path}")
    return path


def require_ffmpeg(
    ffmpeg_bin: str | None = None,
    ffprobe_bin: str | None = None,
) -> tuple[str, str]:
    """Verify ffmpeg & ffprobe binaries are executable; raises AssertionError cleanly if absent."""
    def _resolve(name: str, override: str | None) -> str:
        target = override if override is not None else name
        found = shutil.which(target)
        if not found:
            raise AssertionError(
                f"Prerequisite missing: {target!r} not found on PATH (required from M1)"
            )
        return found

    ff = _resolve("ffmpeg", ffmpeg_bin)
    fp = _resolve("ffprobe", ffprobe_bin)
    return ff, fp


def require_dataclass_fields(cls: type, required_fields: Iterable[str]) -> set[str]:
    present = {f.name for f in dataclasses.fields(cls)}
    missing = [name for name in required_fields if name not in present]
    if missing:
        raise AssertionError(
            f"M1 schema contract gap: {cls.__name__} missing dataclass field(s): {missing}"
        )
    return present


def require_signature_param(func: Callable[..., Any], param_name: str) -> None:
    sig = inspect.signature(func)
    if param_name not in sig.parameters:
        raise AssertionError(
            f"M1 API contract gap: {func.__name__}{sig} lacks required parameter '{param_name}'"
        )


def load_json_file(path: Path, label: str = "") -> Any:
    require_file(path, label=label)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON in {path}: {exc}") from exc


def load_text_file(path: Path, label: str = "") -> str:
    require_file(path, label=label)
    return path.read_text(encoding="utf-8")


def load_registry_safe(path: Path = PATH_REGISTRY):
    from aigc_audio_pipeline.models import VoiceCastingRegistry

    require_file(path, label="voice_casting_registry.json")
    try:
        return VoiceCastingRegistry.load(path)
    except TypeError as exc:
        raise AssertionError(
            f"VoiceCastingRegistry.load({path.name}) failed with TypeError "
            f"(likely missing M1 field or undeclared JSON key): {exc}"
        ) from exc


def load_cue_sheet_safe(path: Path):
    from aigc_audio_pipeline.models import EpisodeCueSheet

    require_file(path, label=path.name)
    try:
        return EpisodeCueSheet.load(path)
    except TypeError as exc:
        raise AssertionError(
            f"EpisodeCueSheet.load({path.name}) failed with TypeError "
            f"(likely missing M1 field or undeclared JSON key): {exc}"
        ) from exc


def load_all_e001_variants() -> dict[str, Any]:
    return {vid: load_cue_sheet_safe(p) for vid, p in VARIANT_JSON_PATHS.items()}


# ---------------------------------------------------------------------------
# Text Normalization, Tokenization, Duration Estimator & Jaccard
# ---------------------------------------------------------------------------

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_EN_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['\-][A-Za-z0-9]+)*")
_BRACKET_TAG_RE = re.compile(r"\[[^\]]+\]")


def normalize_for_phrase_match(text: str) -> str:
    s = text.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _word_bounded_in(needle: str, haystack: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack) is not None


def extract_anchor_source_roles(src_cfg: Any) -> dict[str, Any]:
    if isinstance(src_cfg, list):
        return {
            str(it["role_id"]).strip(): it
            for it in src_cfg
            if isinstance(it, dict) and str(it.get("role_id", "")).strip()
        }
    if not isinstance(src_cfg, dict):
        return {}
    for container in ANCHOR_SOURCE_CONTAINERS:
        val = src_cfg.get(container)
        if isinstance(val, dict) and val:
            return dict(val)
        if isinstance(val, list) and val:
            mapped = {
                str(it["role_id"]).strip(): it
                for it in val
                if isinstance(it, dict) and str(it.get("role_id", "")).strip()
            }
            if mapped:
                return mapped
    return {
        k: v
        for k, v in src_cfg.items()
        if isinstance(v, dict)
        and (k in CANONICAL_ALL_8_ROLES or bool(set(v.keys()) & ANCHOR_ACTUAL_SOURCE_FIELDS))
    }


def assert_anchor_sources_clean(
    src_cfg: Any,
    expected_roles: Sequence[str],
    label: str = "anchor_sources.json",
) -> dict[str, Any]:
    mapping = extract_anchor_source_roles(src_cfg)
    if not mapping or len(mapping) < len(expected_roles):
        raise AssertionError(
            f"{label} missing role entries covering all {len(expected_roles)} roles (found {len(mapping)})"
        )
    missing = sorted(set(expected_roles) - set(mapping.keys()))
    if missing:
        raise AssertionError(f"{label} missing registered role(s): {missing}")

    violations: list[str] = []

    def _scan_value(path: str, val: Any) -> None:
        if isinstance(val, str):
            if _SYNTHETIC_ANCHOR_RE.search(val):
                violations.append(f"{path}={val!r}")
        elif isinstance(val, list):
            for idx, item in enumerate(val):
                _scan_value(f"{path}[{idx}]", item)
        elif isinstance(val, dict):
            for k, sub in val.items():
                if k.lower() in ANCHOR_POLICY_META_KEYS:
                    continue
                _scan_value(f"{path}.{k}", sub)

    if isinstance(src_cfg, dict):
        for k, v in src_cfg.items():
            kl = k.lower()
            if kl in ANCHOR_POLICY_META_KEYS or kl in ANCHOR_SOURCE_CONTAINERS or k in mapping:
                continue
            if kl in ANCHOR_ACTUAL_SOURCE_FIELDS or kl.endswith(
                ("_provider", "_source", "_engine", "_url", "_method")
            ):
                _scan_value(k, v)
    for rid, entry in mapping.items():
        _scan_value(f"role[{rid}]", entry)
    if violations:
        raise AssertionError(f"{label} contains synthetic/API anchor source(s): {violations[:8]}")
    return mapping


def assert_no_xianxia_plot_drift(doc_text: str, label: str = "document") -> None:
    """Strictly ban Xianxia plot tropes everywhere (allowing narrow ML jargon like '预训练炼丹');
    permit '修仙'/'仙侠' ONLY on negative guardrail lines or data rows inside a Markdown ban table
    whose header explicitly carries prohibition keywords."""
    strict_check_text = _ML_LIANDAN_JARGON_RE.sub("", doc_text)
    for trope in _XIANXIA_STRICT_TROPES:
        if trope in strict_check_text:
            raise AssertionError(f"{label} contains Xianxia plot trope {trope!r}")
    in_table = False
    table_is_ban_guardrail = False
    for lineno, line in enumerate(doc_text.splitlines(), start=1):
        stripped = line.strip()
        is_table_row = stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 3
        if is_table_row:
            if not in_table:
                in_table = True
                table_is_ban_guardrail = bool(_BAN_TABLE_HEADER_RE.search(stripped))
        else:
            in_table = False
            table_is_ban_guardrail = False
        for term in _XIANXIA_GENRE_TERMS:
            if term in line and not (_GUARDRAIL_NEGATION_RE.search(line) or table_is_ban_guardrail):
                raise AssertionError(
                    f"{label}:{lineno} contains unnegated Xianxia drift {term!r}: {line.strip()[:120]!r}"
                )


def strip_inline_tags(text: str) -> tuple[list[str], str]:
    from aigc_audio_pipeline.models import extract_tags_and_spoken_text

    return extract_tags_and_spoken_text(text)


def count_cjk_chars(text: str) -> int:
    return len(_CJK_RE.findall(text))


def count_en_words(text: str) -> int:
    return len(_EN_WORD_RE.findall(text))


def get_debrief_act_id(cue_sheet: Any) -> str:
    acts = getattr(cue_sheet, "acts", None) or []
    if len(acts) < 4:
        raise AssertionError(
            f"{getattr(cue_sheet, 'episode_id', '<unknown>')} has only {len(acts)} acts; "
            "expected >= 4 acts with standalone final Debrief act"
        )
    return acts[-1].act_id


def split_drama_and_debrief_cues(cue_sheet: Any) -> tuple[str, list[Any], list[Any]]:
    debrief_act_id = get_debrief_act_id(cue_sheet)
    drama_cues = [c for c in cue_sheet.cues if c.act_id != debrief_act_id]
    debrief_cues = [c for c in cue_sheet.cues if c.act_id == debrief_act_id]
    return debrief_act_id, drama_cues, debrief_cues


def estimate_cue_spoken_duration_s(cue: Any) -> float:
    if cue.kind == "sfx":
        return float(getattr(cue, "duration_seconds", 0.0))
    _, spoken = strip_inline_tags(cue.text or "")
    cjk = count_cjk_chars(spoken)
    en_w = count_en_words(spoken)
    rate = float(getattr(cue, "playback_rate", 1.0))
    if rate <= 0:
        raise AssertionError(f"Non-positive playback_rate={rate} on cue {cue.cue_id}")
    return max(0.45, (cjk / 3.60 + en_w / 2.65) / rate)


def _find_next_dialogue_cue(cues: Sequence[Any], start_idx: int) -> Any | None:
    """Find immediately following dialogue cue, bridging overlay_next SFX but stopping on sequential SFX."""
    for j in range(start_idx + 1, len(cues)):
        nxt = cues[j]
        if nxt.kind == "dialogue":
            return nxt
        if nxt.kind == "sfx" and getattr(nxt, "placement", "sequential") == "overlay_next":
            continue
        return None
    return None


def _cross_speaker_crosstalk_cues(cues: Sequence[Any]) -> list[Any]:
    """Return dialogue cues with negative crosstalk gap [-0.25, -0.05]s into a DIFFERENT speaker."""
    out: list[Any] = []
    for idx, cue in enumerate(cues):
        if cue.kind != "dialogue":
            continue
        if -0.25 <= float(cue.gap_after_s) <= -0.05:
            nxt = _find_next_dialogue_cue(cues, idx)
            if nxt is not None and nxt.role_id != cue.role_id:
                out.append(cue)
    return out


def estimate_cue_slice_duration_s(cues: Sequence[Any]) -> float:
    """Deterministic pre-render timeline estimator matching TEST_INFRA.md §3.3.6 & mixer.py."""
    total = 0.0
    n = len(cues)
    idx = 0
    while idx < n:
        cue = cues[idx]
        if cue.kind == "sfx":
            if getattr(cue, "placement", "sequential") == "overlay_next":
                idx += 1
                continue
            total += max(0.0, float(cue.duration_seconds) + float(cue.gap_after_s))
            idx += 1
            continue
        dur_s = estimate_cue_spoken_duration_s(cue)
        if getattr(cue, "duck_under_next", False) and idx + 1 < n and cues[idx + 1].kind == "dialogue":
            next_cue = cues[idx + 1]
            lead_in = min(dur_s, float(getattr(cue, "duck_lead_in_s", 3.5)))
            next_dur = estimate_cue_spoken_duration_s(next_cue)
            pair_span = max(dur_s, lead_in + next_dur)
            total += max(0.0, pair_span + float(next_cue.gap_after_s))
            idx += 2
            continue
        total += max(0.0, dur_s + float(cue.gap_after_s))
        idx += 1
    return total


def estimate_episode_runtime_breakdown(cue_sheet: Any) -> dict[str, float]:
    debrief_act_id, drama_cues, debrief_cues = split_drama_and_debrief_cues(cue_sheet)
    drama_s = estimate_cue_slice_duration_s(drama_cues)
    debrief_s = estimate_cue_slice_duration_s(debrief_cues)
    pads = float(getattr(cue_sheet, "head_pad_s", 0.0)) + float(
        getattr(cue_sheet, "tail_pad_s", 0.0)
    )
    total_s = estimate_cue_slice_duration_s(cue_sheet.cues) + pads
    return {
        "debrief_act_id": debrief_act_id,
        "drama_s": drama_s,
        "debrief_s": debrief_s,
        "total_s": total_s,
    }


def spoken_word_set(cue_sheet: Any) -> set[str]:
    tokens: set[str] = set()
    for cue in cue_sheet.cues:
        if cue.kind != "dialogue":
            continue
        _, spoken = strip_inline_tags(cue.text or "")
        for w in _EN_WORD_RE.findall(spoken.lower()):
            if len(w) >= 2:
                tokens.add(w)
        cjk_chars = _CJK_RE.findall(spoken)
        for i in range(len(cjk_chars) - 1):
            tokens.add(cjk_chars[i] + cjk_chars[i + 1])
    return tokens


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    return len(set_a & set_b) / len(union) if union else 0.0


# ---------------------------------------------------------------------------
# Public CLI Wrappers & Dynamic Flag Probing
# ---------------------------------------------------------------------------

def pipeline_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{SRC_ROOT}{os.pathsep}{existing}" if existing else str(SRC_ROOT)
    )
    if extra:
        env.update(extra)
    return env


def run_pipeline_cli(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int = 120,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "aigc_audio_pipeline", *args]
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        env=pipeline_env(extra_env),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_python_script(
    script_path: Path,
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int = 180,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    require_file(script_path, label=script_path.name)
    cmd = [sys.executable, str(script_path), *args]
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        env=pipeline_env(extra_env),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def get_script_help_flags(script_path: Path) -> set[str]:
    proc = run_python_script(script_path, ["--help"], timeout=30)
    if proc.returncode != 0:
        raise AssertionError(
            f"{script_path.name} --help failed (rc={proc.returncode}): "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return set(re.findall(r"--[a-zA-Z0-9][a-zA-Z0-9_-]*", combined))


def probe_script_flag(script_path: Path, candidates: Sequence[str]) -> str:
    flags = get_script_help_flags(script_path)
    for cand in candidates:
        if cand in flags:
            return cand
    raise AssertionError(
        f"{script_path.name} --help exposes none of {list(candidates)}; found: {sorted(flags)}"
    )


def parse_last_json_object(text: str) -> dict[str, Any]:
    s = (text or "").strip()
    if not s:
        raise AssertionError("Expected JSON output but got empty string")
    try:
        parsed = json.loads(s)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    # Fallback: scan for final JSON object printed after log lines
    decoder = json.JSONDecoder()
    last_obj: dict[str, Any] | None = None
    idx = 0
    while idx < len(s):
        brace = s.find("{", idx)
        if brace == -1:
            break
        try:
            obj, end_idx = decoder.raw_decode(s, brace)
            if isinstance(obj, dict):
                last_obj = obj
            idx = end_idx
        except json.JSONDecodeError:
            idx = brace + 1
    if last_obj is None:
        raise AssertionError(f"Could not parse JSON object from output:\n{s[:600]}")
    return last_obj


# ---------------------------------------------------------------------------
# Pure-Stdlib Synthetic Audio, Goertzel DFT, Pitch & Independent FFmpeg/ffprobe
# ---------------------------------------------------------------------------

def write_sine_wav(
    path: Path,
    duration_s: float,
    freq_hz: float = 440.0,
    sample_rate: int = 48000,
    channels: int = 1,
    amplitude: float = 0.45,
    fade_s: float = 0.02,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    n_frames = max(1, int(round(duration_s * sample_rate)))
    fade_frames = max(1, min(n_frames // 2, int(round(fade_s * sample_rate))))
    peak = int(32767 * max(0.0, min(0.99, amplitude)))
    samples = array.array("h")
    two_pi_f_over_sr = 2.0 * math.pi * freq_hz / sample_rate
    for i in range(n_frames):
        env = 1.0
        if i < fade_frames:
            env = i / fade_frames
        elif i >= n_frames - fade_frames:
            env = (n_frames - 1 - i) / fade_frames
        val = int(peak * env * math.sin(two_pi_f_over_sr * i))
        if channels == 1:
            samples.append(val)
        else:
            samples.extend((val, val))
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())
    return path


def write_multitone_wav(
    path: Path,
    duration_s: float,
    freqs_amps: Sequence[tuple[float, float]],
    sample_rate: int = 48000,
    channels: int = 1,
    fade_s: float = 0.02,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    n_frames = max(1, int(round(duration_s * sample_rate)))
    fade_frames = max(1, min(n_frames // 2, int(round(fade_s * sample_rate))))
    samples = array.array("h")
    terms = [(2.0 * math.pi * f / sample_rate, amp) for f, amp in freqs_amps]
    for i in range(n_frames):
        env = 1.0
        if i < fade_frames:
            env = i / fade_frames
        elif i >= n_frames - fade_frames:
            env = (n_frames - 1 - i) / fade_frames
        acc = sum(amp * math.sin(w * i) for w, amp in terms)
        clamped = max(-0.98, min(0.98, acc * env))
        val = int(32767 * clamped)
        if channels == 1:
            samples.append(val)
        else:
            samples.extend((val, val))
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())
    return path


def write_tone_burst_wav(
    path: Path,
    *,
    burst_s: float = 0.80,
    silence_s: float = 0.80,
    freq_hz: float = 1000.0,
    sample_rate: int = 48000,
    channels: int = 1,
    amplitude: float = 0.45,
    fade_s: float = 0.005,
    echo_taps: Sequence[tuple[float, float]] = (),
) -> Path:
    """Generate a tone burst followed by silence (and optional synthetic echo taps for self-test)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    burst_frames = max(1, int(round(burst_s * sample_rate)))
    total_frames = max(burst_frames + 1, int(round((burst_s + silence_s) * sample_rate)))
    fade_frames = max(1, min(burst_frames // 2, int(round(fade_s * sample_rate))))
    two_pi_f_over_sr = 2.0 * math.pi * freq_hz / sample_rate

    dry_buf = [0.0] * total_frames
    for i in range(burst_frames):
        env = 1.0
        if i < fade_frames:
            env = i / fade_frames
        elif i >= burst_frames - fade_frames:
            env = (burst_frames - 1 - i) / fade_frames
        dry_buf[i] = amplitude * env * math.sin(two_pi_f_over_sr * i)

    if echo_taps:
        out_buf = list(dry_buf)
        for delay_s, decay in echo_taps:
            d_frames = int(round(delay_s * sample_rate))
            if d_frames <= 0:
                continue
            limit = min(burst_frames, total_frames - d_frames)
            for i in range(limit):
                out_buf[i + d_frames] += decay * dry_buf[i]
    else:
        out_buf = dry_buf

    samples = array.array("h")
    for x in out_buf:
        clamped = max(-0.98, min(0.98, x))
        val = int(32767 * clamped)
        if channels == 1:
            samples.append(val)
        else:
            samples.extend((val, val))

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())
    return path


def read_wav_info_and_mono_samples(wav_path: Path) -> dict[str, Any]:
    require_file(wav_path, label=wav_path.name)
    with wave.open(str(wav_path), "rb") as wf:
        ch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    if sw != 2:
        raise AssertionError(f"Expected 16-bit PCM WAV (sampwidth=2), got {sw} in {wav_path}")
    arr = array.array("h")
    arr.frombytes(raw)
    if sys.byteorder != "little":
        arr.byteswap()
    left = [arr[i] / 32768.0 for i in range(0, len(arr), ch)]
    peak_lin = max((abs(x) for x in left), default=0.0)
    peak_dbfs = 20.0 * math.log10(peak_lin) if peak_lin > 1e-12 else -120.0
    return {
        "channels": ch,
        "sampwidth": sw,
        "sample_rate": sr,
        "nframes": nframes,
        "duration_s": nframes / float(sr) if sr else 0.0,
        "peak_dbfs": peak_dbfs,
        "samples": left,
    }


def goertzel_power(samples: Sequence[float], sample_rate: int, target_hz: float) -> float:
    n = len(samples)
    if n == 0 or sample_rate <= 0:
        return 0.0
    omega = 2.0 * math.pi * target_hz / sample_rate
    coeff = 2.0 * math.cos(omega)
    s_prev = 0.0
    s_prev2 = 0.0
    for x in samples:
        s = x + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    power = s_prev2 * s_prev2 + s_prev * s_prev - coeff * s_prev * s_prev2
    return max(0.0, power) / (n * n)


def estimate_pitch_zero_crossings(samples: Sequence[float], sample_rate: int) -> float:
    n = len(samples)
    if n < 4 or sample_rate <= 0:
        return 0.0
    crossings = 0
    prev = samples[0]
    for cur in samples[1:]:
        if prev <= 0.0 < cur:
            crossings += 1
        prev = cur
    dur_s = (n - 1) / float(sample_rate)
    return crossings / dur_s if dur_s > 0 else 0.0


def probe_audio_ffprobe(audio_path: Path) -> dict[str, Any]:
    _, fp = require_ffmpeg()
    require_file(audio_path, label=audio_path.name)
    proc = subprocess.run(
        [
            fp,
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bits_per_sample,duration",
            "-show_entries",
            "format=duration,bit_rate",
            "-of",
            "json",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"ffprobe failed on {audio_path} (rc={proc.returncode}): {proc.stderr.strip()}"
        )
    data = json.loads(proc.stdout)
    streams = data.get("streams") or []
    if not streams:
        raise AssertionError(f"ffprobe found no audio stream in {audio_path}")
    st = streams[0]
    fmt = data.get("format") or {}
    dur_raw = fmt.get("duration") or st.get("duration")
    return {
        "codec_name": str(st.get("codec_name", "")),
        "sample_rate": int(st["sample_rate"]),
        "channels": int(st["channels"]),
        "bits_per_sample": int(st.get("bits_per_sample") or 0),
        "duration_s": float(dur_raw) if dur_raw is not None else 0.0,
        "bit_rate": int(fmt["bit_rate"]) if fmt.get("bit_rate") else 0,
    }


def measure_loudness_ffmpeg(audio_path: Path) -> tuple[float, float]:
    """Directly parse ffmpeg loudnorm JSON with strict rc==0 check (zero silent fallbacks)."""
    ff, _ = require_ffmpeg()
    require_file(audio_path, label=audio_path.name)
    proc = subprocess.run(
        [
            ff,
            "-hide_banner",
            "-nostats",
            "-i",
            str(audio_path),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"ffmpeg loudnorm measurement failed on {audio_path} (rc={proc.returncode}): "
            f"{proc.stderr[-400:]}"
        )
    matches = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', proc.stderr, flags=re.DOTALL)
    if not matches:
        raise AssertionError(
            f"ffmpeg loudnorm JSON missing 'input_i' for {audio_path}: {proc.stderr[-400:]}"
        )
    obj = json.loads(matches[-1])
    try:
        lufs = float(obj["input_i"])
        tp = float(obj["input_tp"])
    except (KeyError, ValueError) as exc:
        raise AssertionError(f"Non-numeric loudness output in {obj}: {exc}") from exc
    if not (math.isfinite(lufs) and math.isfinite(tp)):
        raise AssertionError(f"Non-finite loudness values ({lufs}, {tp}) for {audio_path}")
    return lufs, tp


# ---------------------------------------------------------------------------
# SRT Parser & Notebook Flag Extractor
# ---------------------------------------------------------------------------

_SRT_TS_RE = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)


def parse_srt(srt_text: str) -> list[dict[str, Any]]:
    blocks = re.split(r"\r?\n\r?\n+", srt_text.strip())
    parsed: list[dict[str, Any]] = []
    for raw_block in blocks:
        lines = [ln.rstrip("\r") for ln in raw_block.splitlines() if ln.strip() != ""]
        if not lines:
            continue
        if len(lines) < 3:
            raise AssertionError(f"Malformed SRT block (<3 lines): {raw_block!r}")
        try:
            index = int(lines[0].strip())
        except ValueError as exc:
            raise AssertionError(f"Non-integer SRT index {lines[0]!r}") from exc
        m = _SRT_TS_RE.match(lines[1].strip())
        if not m:
            raise AssertionError(f"Malformed SRT timestamp line: {lines[1]!r}")
        h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(g) for g in m.groups())
        start_ms = ((h1 * 60 + m1) * 60 + s1) * 1000 + ms1
        end_ms = ((h2 * 60 + m2) * 60 + s2) * 1000 + ms2
        parsed.append(
            {
                "index": index,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "lines": lines[2:],
                "text": "\n".join(lines[2:]),
            }
        )
    return parsed


def strip_notebook_magics(cell_source: str) -> str:
    cleaned: list[str] = []
    in_magic_cont = False
    magic_indent = ""
    for line in cell_source.splitlines():
        stripped = line.lstrip()
        if in_magic_cont:
            cleaned.append(f"{magic_indent}pass  # magic cont")
            in_magic_cont = line.rstrip().endswith("\\")
        elif stripped.startswith("!") or stripped.startswith("%"):
            magic_indent = line[: len(line) - len(stripped)]
            cleaned.append(f"{magic_indent}pass  # magic")
            in_magic_cont = line.rstrip().endswith("\\")
        else:
            cleaned.append(line)
    return "\n".join(cleaned)


_TOKEN_BOUNDARY_FLAG_RE = re.compile(r"(?:^|[\s'\"`(\[])(--[a-zA-Z0-9][a-zA-Z0-9_-]*)")
_EXACT_CLI_FLAG_RE = re.compile(r"^(--[a-zA-Z0-9][a-zA-Z0-9_-]*)(?:=.*)?$")


def _extract_launcher_flags_from_python_ast(
    code: str,
    launcher_basename: str = "launch_g4_global_edge_drama3.py",
) -> set[str]:
    """Parse Python AST (including multi-line subprocess lists and dynamic list mutations)."""
    cleaned = strip_notebook_magics(code)
    try:
        tree = ast.parse(cleaned)
    except SyntaxError:
        return set()

    def _extract_string_repr(node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            parts: list[str] = []
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(v.value)
                else:
                    parts.append(" <expr> ")
            return "".join(parts)
        return None

    def _subtree_has_str(node: ast.AST, needle: str) -> bool:
        return any(
            isinstance(sub, ast.Constant) and isinstance(sub.value, str) and needle in sub.value
            for sub in ast.walk(node)
        )

    def _subtree_uses_any_name(node: ast.AST, names: set[str]) -> bool:
        return any(
            isinstance(sub, ast.Name) and sub.id in names
            for sub in ast.walk(node)
        )

    def _collect_target_names(tgt: ast.AST) -> list[str]:
        if isinstance(tgt, ast.Name):
            return [tgt.id]
        if isinstance(tgt, (ast.Tuple, ast.List)):
            out: list[str] = []
            for e in tgt.elts:
                out.extend(_collect_target_names(e))
            return out
        return []

    def _collect_flags_from_expr(
        expr: ast.AST,
        var_flags_map: dict[str, set[str]] | None = None,
    ) -> set[str]:
        found: set[str] = set()
        for sub in ast.walk(expr):
            if isinstance(sub, ast.JoinedStr):
                s = _extract_string_repr(sub)
                if s is not None:
                    m = _EXACT_CLI_FLAG_RE.fullmatch(s.strip())
                    if m:
                        found.add(m.group(1))
            elif isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                m = _EXACT_CLI_FLAG_RE.fullmatch(sub.value.strip())
                if m:
                    found.add(m.group(1))
            elif var_flags_map is not None and isinstance(sub, ast.Name) and sub.id in var_flags_map:
                found.update(var_flags_map[sub.id])
        return found

    all_nodes = list(ast.walk(tree))
    assign_nodes = [n for n in all_nodes if isinstance(n, (ast.Assign, ast.AnnAssign))]
    aug_nodes = [n for n in all_nodes if isinstance(n, ast.AugAssign)]
    mutator_calls = [
        n
        for n in all_nodes
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name)
        and n.func.attr in ("append", "extend", "insert")
    ]

    # Step 1: Track launcher command list variables + alias propagation
    launcher_list_vars: set[str] = set()
    for node in assign_nodes:
        val = node.value
        if val is None:
            continue
        if _subtree_has_str(val, launcher_basename) and any(
            isinstance(sub, (ast.List, ast.Tuple)) for sub in ast.walk(val)
        ):
            tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tgt in tgts:
                launcher_list_vars.update(_collect_target_names(tgt))

    for _ in range(3):
        changed = False
        for node in assign_nodes:
            val = node.value
            if val is None or not _subtree_uses_any_name(val, launcher_list_vars):
                continue
            tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tgt in tgts:
                for nm in _collect_target_names(tgt):
                    if nm not in launcher_list_vars:
                        launcher_list_vars.add(nm)
                        changed = True
        if not changed:
            break

    # Step 2: 1-hop helper list/flag variable map (e.g. extra = ["--bad"]; cmd.extend(extra))
    list_var_flags: dict[str, set[str]] = {}
    for _ in range(2):
        for node in assign_nodes:
            val = node.value
            if val is None:
                continue
            extracted = _collect_flags_from_expr(val, list_var_flags)
            if extracted:
                tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
                for tgt in tgts:
                    for nm in _collect_target_names(tgt):
                        if nm not in launcher_list_vars:
                            list_var_flags.setdefault(nm, set()).update(extracted)
        for node in aug_nodes:
            if isinstance(node.target, ast.Name) and node.target.id not in launcher_list_vars:
                extracted = _collect_flags_from_expr(node.value, list_var_flags)
                if extracted:
                    list_var_flags.setdefault(node.target.id, set()).update(extracted)
        for call in mutator_calls:
            vname = call.func.value.id  # type: ignore[union-attr]
            if vname not in launcher_list_vars:
                for arg in call.args:
                    extracted = _collect_flags_from_expr(arg, list_var_flags)
                    if extracted:
                        list_var_flags.setdefault(vname, set()).update(extracted)

    # Step 3: Extract flags from direct lists/tuples, shell strings, and launcher_list_vars mutations
    flags: set[str] = set()
    for node in all_nodes:
        if isinstance(node, (ast.List, ast.Tuple)):
            elts = node.elts
            hit_idx = next(
                (idx for idx, elt in enumerate(elts) if _subtree_has_str(elt, launcher_basename)),
                None,
            )
            if hit_idx is not None:
                for elt in elts[hit_idx + 1 :]:
                    flags.update(_collect_flags_from_expr(elt, list_var_flags))
        elif isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in launcher_list_vars
                and node.func.attr in ("append", "extend", "insert")
            ):
                for arg in node.args:
                    flags.update(_collect_flags_from_expr(arg, list_var_flags))
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                s = _extract_string_repr(arg)
                if s is not None and launcher_basename in s:
                    pos = s.find(launcher_basename)
                    tail = s[pos + len(launcher_basename) :]
                    for fl in _TOKEN_BOUNDARY_FLAG_RE.findall(tail):
                        flags.add(fl)
                elif (
                    isinstance(arg, (ast.BinOp, ast.List, ast.Tuple))
                    and _subtree_uses_any_name(arg, launcher_list_vars)
                ):
                    flags.update(_collect_flags_from_expr(arg, list_var_flags))
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name) and node.target.id in launcher_list_vars:
                flags.update(_collect_flags_from_expr(node.value, list_var_flags))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            val = node.value
            if val is None:
                continue
            s = _extract_string_repr(val)
            if s is not None and launcher_basename in s:
                pos = s.find(launcher_basename)
                tail = s[pos + len(launcher_basename) :]
                for fl in _TOKEN_BOUNDARY_FLAG_RE.findall(tail):
                    flags.add(fl)
            if _subtree_uses_any_name(val, launcher_list_vars):
                flags.update(_collect_flags_from_expr(val, list_var_flags))
    return flags


def _strip_inline_hash_comment(line: str) -> str:
    """Strip full-line or trailing `# ...` comments outside quotes (preserving `#` in strings/URLs)."""
    in_quote: str | None = None
    escaped = False
    for idx, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_quote is not None:
            escaped = True
            continue
        if in_quote is not None:
            if ch == in_quote:
                in_quote = None
            continue
        if ch in ("'", '"'):
            in_quote = ch
        elif ch == "#" and (idx == 0 or line[idx - 1].isspace()):
            return line[:idx]
    return line


def extract_launcher_cli_flags_from_text(
    text: str,
    launcher_basename: str = "launch_g4_global_edge_drama3.py",
) -> set[str]:
    flags: set[str] = set(_extract_launcher_flags_from_python_ast(text, launcher_basename))
    lines = text.splitlines()

    # If the cell is valid Python (after stripping !/% magics) and NO shell magic line
    # invokes launcher_basename, trust the AST result exclusively so Python `#` comments
    # inside multi-line subprocess.check_call([...]) lists are never falsely flagged.
    code_cleaned = strip_notebook_magics(text)
    has_shell_magic_launcher = any(
        re.match(r"^\s*[!%]", ln) and launcher_basename in _strip_inline_hash_comment(ln)
        for ln in lines
    )
    try:
        ast.parse(code_cleaned)
        is_valid_python = True
    except SyntaxError:
        is_valid_python = False
    if is_valid_python and not has_shell_magic_launcher:
        return flags

    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            continue
        clean_line = _strip_inline_hash_comment(line)
        if launcher_basename not in clean_line:
            continue
        # Track brackets opened on up to 3 preceding lines (e.g. subprocess.check_call([\n ...))
        preceding = [_strip_inline_hash_comment(ln) for ln in lines[max(0, i - 3) : i]] + [clean_line]
        open_brackets = sum(ln.count("[") - ln.count("]") for ln in preceding)
        chunk_lines = [clean_line]
        j = i + 1
        while j < len(lines) and (
            chunk_lines[-1].rstrip().endswith("\\") or open_brackets > 0
        ):
            nxt = lines[j]
            if nxt.lstrip().startswith("#"):
                j += 1
                if j - i > 25:
                    break
                continue
            clean_nxt = _strip_inline_hash_comment(nxt)
            chunk_lines.append(clean_nxt)
            open_brackets += clean_nxt.count("[") - clean_nxt.count("]")
            j += 1
            if j - i > 25:
                break
        chunk = " ".join(chunk_lines)
        pos = chunk.find(launcher_basename)
        tail = chunk[pos + len(launcher_basename) :]
        for flag in _TOKEN_BOUNDARY_FLAG_RE.findall(tail):
            flags.add(flag)
    return flags


def extract_notebook_launcher_flags(
    nb_data: dict[str, Any],
    launcher_basename: str = "launch_g4_global_edge_drama3.py",
) -> set[str]:
    flags: set[str] = set()
    for cell in nb_data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        flags |= extract_launcher_cli_flags_from_text(src, launcher_basename)
    return flags


# ---------------------------------------------------------------------------
# 18 Named Opaque-Box Oracles (Shared by Tiers 1–4 AND --self-test!)
# ---------------------------------------------------------------------------

# Family 1
def oracle_standalone_ip_and_banned_cliches(cue_sheet: Any) -> dict[str, Any]:
    """Assert zero YouTube/Shorts meta-commentary and zero classroom/radio clichés across
    cue_sheet.title, act.title, inline tags, spoken text, and subtitle_translation.

    NOTE: Intentionally does NOT scan `cue.director_note`, because legitimate production
    notes may contain negative guardrails (e.g. 'Do not sound like a YouTube host').
    """
    violations: list[str] = []

    def _scan_text(location: str, raw_text: str) -> None:
        if not raw_text:
            return
        low = normalize_for_phrase_match(raw_text)
        for term in BANNED_YOUTUBE_SHORTS_TERMS:
            if term in low:
                violations.append(f"{location}: banned YouTube/Shorts term {term!r}")
        for cliche in BANNED_CLICHES:
            if cliche in raw_text:
                violations.append(f"{location}: banned cliché {cliche!r}")
        for esl in BANNED_ELEMENTARY_ESL:
            if esl in low:
                violations.append(f"{location}: elementary ESL phrase {esl!r}")

    _scan_text("cue_sheet.title", str(getattr(cue_sheet, "title", "") or ""))
    for act in getattr(cue_sheet, "acts", None) or []:
        _scan_text(f"act[{getattr(act, 'act_id', '?')}].title", str(getattr(act, "title", "") or ""))

    dialogue_count = 0
    for cue in cue_sheet.cues:
        if cue.kind != "dialogue":
            continue
        dialogue_count += 1
        tags, spoken = strip_inline_tags(cue.text or "")
        for tag in tags:
            _scan_text(f"{cue.cue_id}[tag]", tag)
        _scan_text(cue.cue_id, spoken)
        sub_tr = str(getattr(cue, "subtitle_translation", "") or "")
        if sub_tr:
            _scan_text(f"{cue.cue_id}.subtitle_translation", sub_tr)

    if dialogue_count == 0:
        raise AssertionError(f"{cue_sheet.episode_id}: contains 0 dialogue cues")
    if violations:
        raise AssertionError(
            f"{cue_sheet.episode_id}: standalone-IP/cliché violations: {violations[:8]}"
        )
    return {"dialogue_count": dialogue_count, "violations": 0}


# Family 2
def oracle_e001_8_mandatory_phrases(cue_sheet: Any, *, drama_only: bool = True) -> dict[str, Any]:
    """Verify all 8 mandatory E001 target phrases (word-bounded, no cross-cue stitching,
    strictly requiring >=4 acts when drama_only=True)."""
    if drama_only:
        _, cues_to_scan, _ = split_drama_and_debrief_cues(cue_sheet)
    else:
        cues_to_scan = list(cue_sheet.cues)
    en_parts: list[str] = []
    for cue in cues_to_scan:
        if cue.kind != "dialogue":
            continue
        if cue.language_code in ("en", "zh-en", ""):
            _, spoken = strip_inline_tags(cue.text or "")
            en_parts.append(spoken)
    # Non-word sentinel prevents cross-cue stitching (e.g. "...phantom" + "number...")
    blob = normalize_for_phrase_match(" ||| ".join(en_parts))
    missing: list[str] = []
    matched: dict[str, list[str]] = {}
    for pid, label, and_clauses in E001_MANDATORY_PHRASES:
        hits: list[str] = []
        ok = True
        for alts in and_clauses:
            hit = next((a for a in alts if _word_bounded_in(a, blob)), None)
            if hit is None:
                ok = False
                missing.append(f"{pid} ({label}): missing any of {list(alts)}")
            else:
                hits.append(hit)
        if ok:
            matched[pid] = hits
    if missing:
        raise AssertionError(
            f"{getattr(cue_sheet, 'episode_id', '<cue_sheet>')}: "
            f"missing mandatory E001 phrases ({len(missing)}): {missing}"
        )
    return {"matched_count": len(matched), "matched": matched}


# Family 3
def oracle_corpus_100_etl_integrity(
    corpus_data: dict[str, Any],
    raw_data: Any | None = None,
) -> dict[str, Any]:
    """Verify 100/100 unique clip_ids, 25x4 topics, 030/054 collisions, 1408 segs, 38 anomalies."""
    required_top = (
        "schema_version",
        "source_file",
        "total_clips",
        "topic_counts",
        "summary_metrics",
        "asr_corrections_applied",
        "clips",
    )
    missing_top = [k for k in required_top if k not in corpus_data]
    if missing_top:
        raise AssertionError(f"corpus_100_structured.json missing top-level keys: {missing_top}")
    if corpus_data["total_clips"] != 100:
        raise AssertionError(f"total_clips={corpus_data['total_clips']}, expected 100")
    expected_topics = {"AI": 25, "BUSINESS": 25, "FINANCE": 25, "US_CHINA": 25}
    if corpus_data["topic_counts"] != expected_topics:
        raise AssertionError(
            f"topic_counts={corpus_data['topic_counts']}, expected {expected_topics}"
        )
    clips = corpus_data["clips"]
    if not isinstance(clips, list) or len(clips) != 100:
        raise AssertionError(f"clips list length={len(clips) if isinstance(clips, list) else type(clips)}, expected 100")

    by_id: dict[str, dict[str, Any]] = {}
    recomp_topics: dict[str, int] = {}
    recomp_segments = 0
    wpms: list[float] = []
    required_clip_keys = (
        "clip_id", "topic_key", "topic_label", "video_id", "video_title",
        "channel", "inferred_speakers", "duration_sec", "wpm", "virality_score",
        "hook_line_1", "hook_line_2", "en_title_hook", "summary_zh",
        "en_raw", "en_clean", "zh_full", "subtitles_clean",
    )
    for rec in clips:
        cid = rec.get("clip_id")
        if not isinstance(cid, str) or not cid:
            raise AssertionError(f"Clip record missing string clip_id: {rec}")
        if cid in by_id:
            raise AssertionError(f"Duplicate clip_id in corpus: {cid!r}")
        miss_k = [k for k in required_clip_keys if k not in rec]
        if miss_k:
            raise AssertionError(f"Clip {cid} missing required keys: {miss_k}")
        tkey = str(rec.get("topic_key", ""))
        recomp_topics[tkey] = recomp_topics.get(tkey, 0) + 1
        subs = rec.get("subtitles_clean")
        if not isinstance(subs, list):
            raise AssertionError(f"Clip {cid} subtitles_clean is not a list")
        recomp_segments += len(subs)
        wpm_val = float(rec["wpm"])
        if not math.isfinite(wpm_val):
            raise AssertionError(f"Clip {cid} has non-finite wpm={wpm_val!r}")
        wpms.append(wpm_val)
        by_id[cid] = rec

    actual_ids = frozenset(by_id.keys())
    if actual_ids != EXPECTED_100_CLIP_IDS:
        dropped = sorted(EXPECTED_100_CLIP_IDS - actual_ids)
        extra = sorted(actual_ids - EXPECTED_100_CLIP_IDS)
        raise AssertionError(
            f"100-clip set mismatch: dropped={dropped[:10]}, extra={extra[:10]}"
        )
    topic_mismatches = [
        f"{cid}({by_id[cid]['topic_key']}!={CLIP_TOPIC_LOOKUP[cid]})"
        for cid in sorted(by_id)
        if by_id[cid]["topic_key"] != CLIP_TOPIC_LOOKUP[cid]
    ]
    if topic_mismatches:
        raise AssertionError(f"Clip topic_key mismatches vs canonical topics: {topic_mismatches[:8]}")
    if recomp_topics != expected_topics or recomp_topics != corpus_data["topic_counts"]:
        raise AssertionError(
            f"Recomputed topic_counts={recomp_topics} disagrees with expected={expected_topics} "
            f"or reported={corpus_data['topic_counts']}"
        )
    for col_id in COLLIDING_PREFIX_IDS:
        if col_id not in by_id:
            raise AssertionError(f"Colliding prefix clip missing: {col_id}")
    if by_id["030_AI"]["video_id"] == by_id["030_BIZ"]["video_id"]:
        raise AssertionError("Prefix collision bug: 030_AI and 030_BIZ share video_id")
    if by_id["054_BIZ"]["video_id"] == by_id["054_FIN"]["video_id"]:
        raise AssertionError("Prefix collision bug: 054_BIZ and 054_FIN share video_id")

    sm = corpus_data["summary_metrics"]
    reported_segs = int(sm.get("total_segments", -1))
    if reported_segs != EXPECTED_TOTAL_SEGMENTS or recomp_segments != EXPECTED_TOTAL_SEGMENTS:
        raise AssertionError(
            f"total_segments mismatch: reported={reported_segs}, recomputed={recomp_segments}, "
            f"expected={EXPECTED_TOTAL_SEGMENTS}"
        )
    med_wpm = float(sm.get("median_wpm", 0.0))
    recomp_med_wpm = float(statistics.median(wpms))
    if abs(med_wpm - EXPECTED_MEDIAN_WPM) > 2.0:
        raise AssertionError(
            f"summary_metrics.median_wpm={med_wpm}, expected ~{EXPECTED_MEDIAN_WPM} (±2.0)"
        )
    if abs(recomp_med_wpm - med_wpm) > 0.5 or abs(recomp_med_wpm - EXPECTED_MEDIAN_WPM) > 2.0:
        raise AssertionError(
            f"Recomputed median_wpm={recomp_med_wpm:.2f} disagrees with reported={med_wpm:.2f} "
            f"(expected ~{EXPECTED_MEDIAN_WPM} ±2.0)"
        )

    corrections = corpus_data["asr_corrections_applied"]
    if not isinstance(corrections, list) or len(corrections) < 20:
        raise AssertionError(
            f"asr_corrections_applied count={len(corrections) if isinstance(corrections, list) else 0}, expected >= 20"
        )
    for entry in corrections:
        for req_k in ("clip_id", "raw", "reason"):
            if not str(entry.get(req_k, "")).strip():
                raise AssertionError(f"asr_corrections_applied entry missing {req_k!r}: {entry}")
        if "clean" not in entry or not isinstance(entry["clean"], str):
            raise AssertionError(f"asr_corrections_applied entry missing string 'clean': {entry}")
        raw_str = str(entry["raw"]).strip()
        is_tag_strip = raw_str.startswith("[") and raw_str.endswith("]")
        if not is_tag_strip and not entry["clean"].strip():
            raise AssertionError(f"asr_corrections_applied entry has empty 'clean' for non-tag {raw_str!r}: {entry}")

    # Verify all 38 raw corpus anomalies cleaned in en_clean & subtitles_clean
    anomaly_failures: list[str] = []
    for cid, label, pat, flags, clean_hint, _batch in RAW_CORPUS_ANOMALIES:
        rec = by_id[cid]
        rx = re.compile(pat, flags)
        en_clean = rec.get("en_clean", "")
        if rx.search(en_clean):
            anomaly_failures.append(
                f"{cid}: raw anomaly {label!r} ({pat}) still present in en_clean (expected {clean_hint!r})"
            )
        subs_text = " ".join(
            str(s.get("en", s.get("en_clean", "")))
            for s in (rec.get("subtitles_clean") or [])
            if isinstance(s, dict)
        )
        if subs_text and rx.search(subs_text):
            anomaly_failures.append(
                f"{cid}: raw anomaly {label!r} still present in subtitles_clean"
            )
    # Global bracket-tag ban in en_clean across all 100 clips
    for cid, rec in by_id.items():
        if _BRACKET_TAG_RE.search(rec.get("en_clean", "")):
            anomaly_failures.append(f"{cid}: bracket tag remains in en_clean")
    # Specificity check: Claude intact in 015_AI
    if "claude" not in by_id["015_AI"].get("en_clean", "").lower():
        anomaly_failures.append("015_AI: 'Claude' missing from en_clean (over-aggressive Claud regex?)")

    if anomaly_failures:
        raise AssertionError(
            f"Corpus cleaning failures ({len(anomaly_failures)}): {anomaly_failures[:8]}"
        )
    if raw_data is not None:
        raw_clips = raw_data if isinstance(raw_data, list) else raw_data.get("clips", raw_data.get("items", []))
        if len(raw_clips) != 100:
            raise AssertionError(f"Raw data expected 100 clips, got {len(raw_clips)}")
    return {
        "total_clips": 100,
        "total_segments": int(sm["total_segments"]),
        "median_wpm": med_wpm,
        "corrections_count": len(corrections),
    }


# Family 4
def oracle_lexicon_provenance_70_30(
    lexicon_data: Any,
    corpus_data: dict[str, Any],
) -> dict[str, Any]:
    """Verify >=100 lexicon entries, >=70% verified corpus provenance, <=30% world_bridge."""
    entries = (
        lexicon_data
        if isinstance(lexicon_data, list)
        else lexicon_data.get("phrases", lexicon_data.get("entries", lexicon_data.get("lexicon", [])))
    )
    if not isinstance(entries, list) or len(entries) < 100:
        raise AssertionError(
            f"executive_lexicon.json must have >= 100 entries, got {len(entries) if isinstance(entries, list) else type(entries)}"
        )
    clips_by_id = {c["clip_id"]: c for c in corpus_data.get("clips", [])}
    required_keys = (
        "phrase_id",
        "phrase_en",
        "category",
        "cefr_level",
        "chinglish_trap",
        "executive_subtext_zh",
        "verbatim_context_en",
        "source_type",
        "clip_ids",
    )
    allowed_cefr = {"B1", "B2", "C1", "C2", "B1-B2", "B2-C1", "C1+", "C1-C2", "B1-C1"}
    corpus_count = 0
    bridge_count = 0
    errors: list[str] = []

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry[{idx}] is not a dict")
            continue
        for k in required_keys:
            if k not in entry:
                errors.append(f"entry[{idx}] missing key {k!r}")
        for str_k in ("phrase_id", "phrase_en", "category", "cefr_level", "chinglish_trap", "executive_subtext_zh", "verbatim_context_en"):
            if not str(entry.get(str_k, "")).strip():
                errors.append(f"{entry.get('phrase_id', idx)}: empty {str_k!r}")
        cefr = str(entry.get("cefr_level", "")).strip().upper()
        if cefr and cefr not in allowed_cefr:
            errors.append(f"{entry.get('phrase_id', idx)}: unexpected cefr_level={cefr!r}")

        stype = entry.get("source_type")
        cids = entry.get("clip_ids")
        if not isinstance(cids, list):
            errors.append(f"{entry.get('phrase_id', idx)}: clip_ids must be list")
            continue
        if stype == "corpus":
            corpus_count += 1
            if not cids:
                errors.append(f"{entry.get('phrase_id', idx)}: source_type='corpus' has empty clip_ids")
                continue
            phrase_norm = normalize_for_phrase_match(str(entry.get("phrase_en", "")))
            core_phrase = re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", "", phrase_norm)).strip()
            raw_alts = [v.strip() for v in re.split(r"[/|]", core_phrase) if v.strip()]
            if len(raw_alts) > 1:
                # Slash/pipe alternatives must be >=4 chars and non-stopword to block spoofs like "that / bogus"
                valid_alts = [v for v in raw_alts if len(v) >= 4 and v not in _LEXICON_SLASH_STOPWORDS]
            else:
                valid_alts = [v for v in raw_alts if len(v) >= 3]
            if not valid_alts:
                errors.append(
                    f"{entry.get('phrase_id', idx)}: phrase {entry.get('phrase_en')!r} has no valid >=4-char non-stopword alternative"
                )
                continue

            def _phrase_matches(alt: str, hay: str) -> bool:
                if "..." in alt or "…" in alt:
                    parts = [p.strip() for p in re.split(r"\.\.\.|…", alt) if len(p.strip()) >= 3]
                    return bool(parts) and all(_word_bounded_in(p, hay) for p in parts)
                return _word_bounded_in(alt, hay)

            for cid in cids:
                if cid not in clips_by_id:
                    errors.append(f"{entry.get('phrase_id', idx)}: fabricated/unknown clip_id {cid!r}")
                    continue
                en_clean_norm = normalize_for_phrase_match(str(clips_by_id[cid].get("en_clean", "")))
                if not any(_phrase_matches(v, en_clean_norm) for v in valid_alts):
                    errors.append(
                        f"{entry.get('phrase_id', idx)}: phrase {entry.get('phrase_en')!r} not verified (word-bounded) in en_clean of cited clip {cid!r}"
                    )
            verbatim_norm = normalize_for_phrase_match(str(entry.get("verbatim_context_en", "")))
            if not any(_phrase_matches(v, verbatim_norm) for v in valid_alts):
                errors.append(
                    f"{entry.get('phrase_id', idx)}: phrase {entry.get('phrase_en')!r} not found (word-bounded) in verbatim_context_en"
                )
        elif stype == "world_bridge":
            bridge_count += 1
            if cids:
                errors.append(
                    f"{entry.get('phrase_id', idx)}: source_type='world_bridge' must have empty clip_ids, got {cids!r}"
                )
        else:
            errors.append(f"{entry.get('phrase_id', idx)}: invalid source_type={stype!r}")

    total = len(entries)
    corpus_ratio = corpus_count / float(total)
    if corpus_ratio < 0.70 - 1e-9:
        errors.append(
            f"corpus provenance ratio={corpus_ratio:.4f} ({corpus_count}/{total}) < 0.70"
        )
    if errors:
        raise AssertionError(
            f"Lexicon provenance audit failed ({len(errors)} errors): {errors[:8]}"
        )
    return {
        "total": total,
        "corpus_count": corpus_count,
        "world_bridge_count": bridge_count,
        "corpus_ratio": corpus_ratio,
    }


# Family 5
def oracle_season1_24ep_bijection(
    season_map: dict[str, Any],
    expected_ids: frozenset[str] = EXPECTED_100_CLIP_IDS,
) -> dict[str, Any]:
    """Verify exact 24 episodes (4x6 arcs), 20x4 + 4x5 = 100/100 bijection, E001 5 seeds."""
    episodes = season_map.get("episodes")
    if not isinstance(episodes, list) or len(episodes) != 24:
        raise AssertionError(
            f"season1_24ep_map.json must have exactly 24 episodes, got {len(episodes) if isinstance(episodes, list) else type(episodes)}"
        )
    required_keys = (
        "episode_id",
        "arc_number",
        "arc_title",
        "title_zh",
        "title_en",
        "logline_zh",
        "primary_clip_ids",
        "accent_profile",
        "core_us_uk_en_pct",
        "target_phrases",
        "viral_45s_hook",
        "cliffhanger_zh",
    )
    arc_counts: dict[int, int] = {}
    all_assigned: list[str] = []
    per_ep_counts: list[int] = []
    titles_zh: set[str] = set()
    titles_en: set[str] = set()
    e001_seeds: set[str] | None = None

    for idx, ep in enumerate(episodes, start=1):
        miss = [k for k in required_keys if k not in ep]
        if miss:
            raise AssertionError(f"Episode index {idx} missing keys: {miss}")
        expected_eid = f"E{idx:03d}"
        if ep["episode_id"] != expected_eid:
            raise AssertionError(f"Expected episode_id={expected_eid}, got {ep['episode_id']!r}")
        arc_num = int(ep["arc_number"])
        arc_counts[arc_num] = arc_counts.get(arc_num, 0) + 1
        for text_k in ("arc_title", "title_zh", "title_en", "logline_zh", "cliffhanger_zh"):
            val = ep.get(text_k)
            if not isinstance(val, str) or not val.strip():
                raise AssertionError(f"{expected_eid}: {text_k!r} must be a non-empty string, got {val!r}")
        vh = ep.get("viral_45s_hook")
        vh_ok = (isinstance(vh, str) and len(vh.strip()) >= 10) or (
            isinstance(vh, dict)
            and isinstance(vh.get("conflict_angle"), str)
            and bool(vh["conflict_angle"].strip())
            and isinstance(vh.get("hook_line_en"), str)
            and bool(vh["hook_line_en"].strip())
        )
        if not vh_ok:
            raise AssertionError(
                f"{expected_eid}: viral_45s_hook must be a >=10-char string or a dict with non-empty "
                f"'conflict_angle' and 'hook_line_en', got {vh!r}"
            )
        titles_zh.add(ep["title_zh"].strip())
        titles_en.add(ep["title_en"].strip())

        cids = ep["primary_clip_ids"]
        if not isinstance(cids, list) or len(cids) not in (4, 5):
            raise AssertionError(
                f"{expected_eid}: primary_clip_ids count={len(cids) if isinstance(cids, list) else type(cids)}, expected 4 or 5"
            )
        per_ep_counts.append(len(cids))
        all_assigned.extend(cids)
        if expected_eid == "E001":
            e001_seeds = set(cids)

        tp = ep["target_phrases"]

        def _valid_tp_item(item: Any) -> bool:
            if isinstance(item, str):
                return bool(item.strip())
            if isinstance(item, dict):
                pe = item.get("phrase_en")
                return isinstance(pe, str) and bool(pe.strip())
            return False

        if not isinstance(tp, list) or not (5 <= len(tp) <= 8) or not all(_valid_tp_item(x) for x in tp):
            raise AssertionError(
                f"{expected_eid}: target_phrases must have 5..8 non-empty str or {{'phrase_en': ...}} items, got {tp!r}"
            )

    if arc_counts != {1: 6, 2: 6, 3: 6, 4: 6}:
        raise AssertionError(f"Expected 4 arcs x 6 episodes, got {arc_counts}")
    if len(titles_zh) != 24 or len(titles_en) != 24:
        raise AssertionError(
            f"Episode titles must be 24/24 unique (zh={len(titles_zh)}, en={len(titles_en)})"
        )
    if per_ep_counts.count(4) != 20 or per_ep_counts.count(5) != 4:
        raise AssertionError(
            f"Expected 20x4 + 4x5 clip distribution, got 4s={per_ep_counts.count(4)}, 5s={per_ep_counts.count(5)}"
        )

    seen: set[str] = set()
    dups: list[str] = []
    for cid in all_assigned:
        if cid in seen:
            dups.append(cid)
        seen.add(cid)
    if dups:
        raise AssertionError(f"Duplicate clip_ids across Season 1 map: {dups}")
    if frozenset(seen) != expected_ids:
        missing = sorted(expected_ids - seen)
        extra = sorted(seen - expected_ids)
        raise AssertionError(
            f"Season 1 clip bijection broken: missing={missing[:10]}, extra={extra[:10]}"
        )
    if e001_seeds != set(E001_SEED_CLIP_IDS):
        raise AssertionError(
            f"E001 primary_clip_ids={sorted(e001_seeds or [])}, expected {sorted(E001_SEED_CLIP_IDS)}"
        )
    return {
        "episode_count": 24,
        "unique_clips": len(seen),
        "arc_counts": arc_counts,
    }


# Family 6
def oracle_accent_matrix_budget(
    registry: Any,
    season_map: dict[str, Any] | None = None,
    e001_cue_sheets: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify 85% US+London RP season-wide floor, <=15% intl guest cap, 100% core US+UK in E001."""
    roles = registry.roles if hasattr(registry, "roles") else registry.get("roles", {})
    missing_roles = [r for r in CANONICAL_ALL_8_ROLES if r not in roles]
    if missing_roles:
        raise AssertionError(f"Registry missing canonical roles: {missing_roles}")

    role_accents: dict[str, str] = {}
    role_langs: dict[str, str] = {}
    for rid, prof in roles.items():
        acc = prof.accent_code if hasattr(prof, "accent_code") else prof.get("accent_code", "")
        if not str(acc).strip():
            raise AssertionError(f"Role {rid!r} has empty accent_code")
        role_accents[rid] = str(acc).strip()
        lang_val = prof.language_code if hasattr(prof, "language_code") else prof.get("language_code", "")
        role_langs[rid] = str(lang_val).strip()
        if rid in EXPECTED_ROLE_ACCENTS and role_accents[rid] != EXPECTED_ROLE_ACCENTS[rid]:
            raise AssertionError(
                f"Role {rid!r} accent_code={role_accents[rid]!r}, expected {EXPECTED_ROLE_ACCENTS[rid]!r}"
            )

    mean_pct: float | None = None
    if season_map is not None:
        eps = season_map.get("episodes", [])
        if not eps:
            raise AssertionError("season_map has 0 episodes")
        pcts: list[float] = []
        e001_pct: float | None = None
        for ep in eps:
            eid = ep.get("episode_id", "<unknown>")
            pct = float(ep["core_us_uk_en_pct"])
            if not math.isfinite(pct) or not (0.0 <= pct <= 100.0):
                raise AssertionError(
                    f"{eid}: core_us_uk_en_pct={pct!r} outside valid [0.0, 100.0] range"
                )
            pcts.append(pct)
            if eid == "E001":
                e001_pct = pct
        if e001_pct is not None and e001_pct < 99.99:
            raise AssertionError(
                f"E001 core_us_uk_en_pct={e001_pct:.2f}% < 100.0% (E001 must be 100% US + London RP)"
            )
        mean_pct = sum(pcts) / len(pcts)
        if mean_pct < 85.0 - 1e-9:
            raise AssertionError(
                f"Season-wide core US+UK RP share={mean_pct:.2f}% < 85.0%"
            )
        intl_share = 100.0 - mean_pct
        if intl_share > 15.0 + 1e-9:
            raise AssertionError(
                f"Season-wide international guest accent share={intl_share:.2f}% > 15.0%"
            )

    e001_report: dict[str, dict[str, Any]] = {}
    if e001_cue_sheets is not None:
        if not e001_cue_sheets:
            raise AssertionError("e001_cue_sheets dict is empty")
        for vid, cs in e001_cue_sheets.items():
            en_core_dur = 0.0
            en_total_dur = 0.0
            us_cues = 0
            uk_cues = 0
            for cue in cs.cues:
                if cue.kind != "dialogue":
                    continue
                rid = cue.role_id
                if rid not in role_accents:
                    raise AssertionError(
                        f"{vid} cue {cue.cue_id}: unregistered role_id {rid!r} not in VoiceCastingRegistry"
                    )
                acc = role_accents[rid]
                if rid in CANONICAL_GUEST_ROLES or acc in INTL_GUEST_ACCENT_CODES:
                    raise AssertionError(
                        f"{vid} cue {cue.cue_id}: international guest role {rid!r} ({acc!r}) forbidden in E001"
                    )
                eff_lang = str(cue.language_code or "").strip() or role_langs.get(rid, "")
                if eff_lang == "en":
                    dur = estimate_cue_spoken_duration_s(cue)
                    en_total_dur += dur
                    if acc in CORE_US_UK_ACCENT_CODES:
                        en_core_dur += dur
                    else:
                        raise AssertionError(
                            f"{vid} cue {cue.cue_id}: pure EN cue spoken by non-US/UK role {rid!r} ({acc!r})"
                        )
                    if rid == "victoria_vance" or acc in ("us_silicon_valley", "us_nyc"):
                        us_cues += 1
                    if rid == "alistair_finch" or acc == "uk_london_rp":
                        uk_cues += 1
            if en_total_dur <= 0:
                raise AssertionError(f"{vid}: contains 0s of pure EN dialogue")
            core_pct = 100.0 * en_core_dur / en_total_dur
            if core_pct < 99.99:
                raise AssertionError(f"{vid}: E001 US+UK RP EN share={core_pct:.2f}% < 100%")
            e001_report[vid] = {
                "en_core_pct": core_pct,
                "us_cues": us_cues,
                "uk_cues": uk_cues,
            }

    return {"season_mean_us_uk_pct": mean_pct, "e001": e001_report}


# Family 7
def oracle_runtime_and_debrief_windows(cue_sheet: Any) -> dict[str, Any]:
    """Verify total [600, 840]s, drama [480, 600]s, debrief [165, 210]s, 0.8x + 1.0x + >=1.8s gaps."""
    br = estimate_episode_runtime_breakdown(cue_sheet)
    eid = getattr(cue_sheet, "episode_id", "<episode>")
    total_s = br["total_s"]
    drama_s = br["drama_s"]
    debrief_s = br["debrief_s"]

    if not (600.0 <= total_s <= 840.0):
        raise AssertionError(f"{eid}: total estimated runtime={total_s:.1f}s outside [600, 840]s")
    if not (480.0 <= drama_s <= 600.0):
        raise AssertionError(f"{eid}: drama estimated runtime={drama_s:.1f}s outside [480, 600]s")
    if not (165.0 <= debrief_s <= 210.0):
        raise AssertionError(f"{eid}: debrief estimated runtime={debrief_s:.1f}s outside [165, 210]s")

    _, _, debrief_cues = split_drama_and_debrief_cues(cue_sheet)
    dlg_debrief = [c for c in debrief_cues if c.kind == "dialogue"]
    slow_cues = [
        c for c in dlg_debrief if abs(float(getattr(c, "playback_rate", 1.0)) - 0.8) < 1e-3
    ]
    native_cues = [
        c
        for c in dlg_debrief
        if abs(float(getattr(c, "playback_rate", 1.0)) - 1.0) < 1e-3
        and c.language_code in ("en", "zh-en")
    ]
    shadow_gap_cues = [
        c
        for c in dlg_debrief
        if abs(float(getattr(c, "playback_rate", 1.0)) - 1.0) < 1e-3
        and c.language_code in ("en", "zh-en")
        and float(c.gap_after_s) >= 1.8 - 1e-9
    ]

    if len(slow_cues) < 3:
        raise AssertionError(
            f"{eid}: Debrief has only {len(slow_cues)} slow (playback_rate=0.8) cues; expected >= 3"
        )
    if len(native_cues) < 3:
        raise AssertionError(
            f"{eid}: Debrief has only {len(native_cues)} native-speed (1.0x) EN/ZH-EN cues; expected >= 3"
        )
    if len(shadow_gap_cues) < 3:
        raise AssertionError(
            f"{eid}: Debrief has only {len(shadow_gap_cues)} shadowing cues with gap_after_s >= 1.8s; expected >= 3"
        )
    return {
        **br,
        "slow_count": len(slow_cues),
        "native_count": len(native_cues),
        "shadow_gap_count": len(shadow_gap_cues),
    }


# Family 8
def oracle_variant_differentiation_and_crosstalk(
    variant_sheets: dict[str, Any],
) -> dict[str, Any]:
    """Verify all 4 variants meet crosstalk floors, structural signatures, UK RP presence, and Jaccard < 0.70."""
    required_vids = ("E001_VA", "E001_VB", "E001_VC", "E001_VD")
    missing = [v for v in required_vids if v not in variant_sheets]
    if missing:
        raise AssertionError(f"Missing variants for differentiation audit: {missing}")

    metrics: dict[str, dict[str, Any]] = {}
    word_sets: dict[str, set[str]] = {}
    for vid in required_vids:
        cs = variant_sheets[vid]
        _, drama_cues, debrief_cues = split_drama_and_debrief_cues(cs)
        dlg_all = [c for c in cs.cues if c.kind == "dialogue"]
        crosstalk = _cross_speaker_crosstalk_cues(cs.cues)
        inner_mono = [c for c in dlg_all if c.acoustic_space == "inner_monologue"]
        phone_cues = [c for c in dlg_all if c.acoustic_space == "phone_call"]
        duck_cues = [c for c in dlg_all if getattr(c, "duck_under_next", False)]
        uk_cues = [c for c in dlg_all if c.role_id == "alistair_finch" and c.language_code == "en"]
        us_cues = [c for c in dlg_all if c.role_id == "victoria_vance" and c.language_code == "en"]
        debrief_roles = {c.role_id for c in debrief_cues if c.kind == "dialogue"}

        if len(crosstalk) < VARIANT_CROSSTALK_MIN[vid]:
            raise AssertionError(
                f"{vid}: crosstalk count={len(crosstalk)} < required {VARIANT_CROSSTALK_MIN[vid]}"
            )
        if len(uk_cues) < 4:
            raise AssertionError(f"{vid}: alistair_finch (UK RP) EN cues={len(uk_cues)} < 4")
        if len(us_cues) < 4:
            raise AssertionError(f"{vid}: victoria_vance (US) EN cues={len(us_cues)} < 4")

        metrics[vid] = {
            "crosstalk": len(crosstalk),
            "inner_monologue": len(inner_mono),
            "phone_call": len(phone_cues),
            "duck_under_next": len(duck_cues),
            "uk_cues": len(uk_cues),
            "us_cues": len(us_cues),
            "debrief_roles": sorted(debrief_roles),
        }
        word_sets[vid] = spoken_word_set(cs)

    if metrics["E001_VB"]["inner_monologue"] < 4:
        raise AssertionError(
            f"E001_VB must have >= 4 inner_monologue cues, got {metrics['E001_VB']['inner_monologue']}"
        )
    if metrics["E001_VB"]["inner_monologue"] <= metrics["E001_VA"]["inner_monologue"]:
        raise AssertionError(
            f"E001_VB inner_monologue ({metrics['E001_VB']['inner_monologue']}) must strictly exceed "
            f"E001_VA ({metrics['E001_VA']['inner_monologue']})"
        )
    if "zhou_mo" not in metrics["E001_VB"]["debrief_roles"]:
        raise AssertionError(
            f"E001_VB Act 5 post-mortem must include zhou_mo; found {metrics['E001_VB']['debrief_roles']}"
        )
    if metrics["E001_VC"]["phone_call"] < 1:
        raise AssertionError("E001_VC must include >= 1 phone_call cue")
    if metrics["E001_VD"]["duck_under_next"] < 2:
        raise AssertionError(
            f"E001_VD must include >= 2 duck_under_next=True blocks, got {metrics['E001_VD']['duck_under_next']}"
        )

    pair_jaccards: dict[str, float] = {}
    for i, va in enumerate(required_vids):
        for vb in required_vids[i + 1 :]:
            sim = jaccard_similarity(word_sets[va], word_sets[vb])
            pair_jaccards[f"{va}__{vb}"] = round(sim, 4)
            if sim >= 0.70:
                raise AssertionError(
                    f"Variants {va} and {vb} are too similar (Jaccard={sim:.3f} >= 0.70)"
                )

    return {"metrics": metrics, "pair_jaccards": pair_jaccards}


# Family 9
def oracle_cue_sheet_numeric_boundaries(cue_sheet: Any, registry: Any = None) -> dict[str, Any]:
    """Validate cue sheet via public EpisodeCueSheet.validate() + assert M1 playback_rate field."""
    from aigc_audio_pipeline.models import TimelineCue

    require_dataclass_fields(TimelineCue, ("playback_rate", "subtitle_translation"))
    errors = cue_sheet.validate(registry=registry, require_locked_voices=False)
    if errors:
        raise AssertionError(
            f"{getattr(cue_sheet, 'episode_id', '<sheet>')} failed numeric/schema validation: {errors[:8]}"
        )
    return {"cue_count": len(cue_sheet.cues), "errors": 0}


# Family 10
def oracle_dialogue_text_and_bilingual_rules(
    text: str,
    stability: float,
    language_code: str,
) -> dict[str, Any]:
    from aigc_audio_pipeline.models import validate_v3_dialogue_text

    errors = validate_v3_dialogue_text(
        text, stability, language_code=language_code, item_label="e2e_line"
    )
    if errors:
        raise AssertionError(f"Dialogue validation failed: {errors}")
    return {"valid": True}


# Family 11
def oracle_ast_zero_api_and_zero_edge_tts(
    source_code: str,
    filename: str = "<memory>",
) -> dict[str, Any]:
    """AST-based audit proving zero ElevenLabs API calls and zero edge-tts production usage,
    whitelisting pure-local ffprobe helpers while catching dynamic imports, import aliases,
    and tainted command variables (and allowing truthful docstrings/negation guards)."""
    try:
        tree = ast.parse(source_code, filename=filename)
    except SyntaxError as exc:
        raise AssertionError(f"SyntaxError in {filename}: {exc}") from exc

    # Identify all docstring Expr nodes so comments/docstrings don't trigger false positives
    docstring_node_ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                docstring_node_ids.add(id(node.body[0].value))

    violations: list[str] = []

    def _call_name(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = _call_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        return ""

    def _const_str_value(expr: ast.AST) -> str | None:
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            if id(expr) in docstring_node_ids:
                return None
            return expr.value
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            left = _const_str_value(expr.left)
            right = _const_str_value(expr.right)
            if left is not None and right is not None:
                return left + right
        return None

    def _has_forbidden_token(text: str) -> bool:
        sv = text.lower()
        return "edge-tts" in sv or "edge_tts" in sv or "elevenlabs" in sv

    def _expr_is_tainted(expr: ast.AST, tainted: set[str]) -> bool:
        if isinstance(expr, (ast.Compare, ast.BoolOp)):
            return False
        if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
            return False
        sval = _const_str_value(expr)
        if sval is not None:
            return _has_forbidden_token(sval)
        if isinstance(expr, ast.Name):
            return expr.id in tainted
        return any(_expr_is_tainted(child, tainted) for child in ast.iter_child_nodes(expr))

    def _collect_target_names(target: ast.AST) -> list[str]:
        if isinstance(target, ast.Name):
            return [target.id]
        if isinstance(target, (ast.Tuple, ast.List)):
            out: list[str] = []
            for elt in target.elts:
                out.extend(_collect_target_names(elt))
            return out
        return []

    # Pass 1: Build import alias map and inspect imports / literals
    alias_map: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name
                alias_map[local] = alias.name
                name_low = alias.name.lower()
                if "edge_tts" in name_low or "elevenlabs" in name_low:
                    violations.append(f"{filename}:{node.lineno}: forbidden import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            mod_name = node.module or ""
            mod_low = mod_name.lower()
            for alias in node.names:
                if alias.name != "*":
                    local = alias.asname or alias.name
                    alias_map[local] = f"{mod_name}.{alias.name}" if mod_name else alias.name
            if mod_low in ("aigc_audio_pipeline.elevenlabs_client", "elevenlabs_client"):
                bad_syms = [
                    a.name for a in node.names if a.name not in ALLOWED_LOCAL_ELEVENLABS_HELPERS
                ]
                if not node.names or bad_syms:
                    violations.append(
                        f"{filename}:{node.lineno}: forbidden from-import {node.module!r} "
                        f"symbol(s) {bad_syms or ['<empty>']}"
                    )
            else:
                if "edge_tts" in mod_low or "elevenlabs" in mod_low:
                    violations.append(f"{filename}:{node.lineno}: forbidden from-import {node.module!r}")
                for alias in node.names:
                    if "edge_tts" in alias.name.lower() or "elevenlabs" in alias.name.lower():
                        violations.append(
                            f"{filename}:{node.lineno}: forbidden imported symbol {alias.name!r}"
                        )
        elif isinstance(node, ast.Name):
            if node.id in ("ElevenLabsClient", "edge_tts"):
                violations.append(f"{filename}:{node.lineno}: forbidden identifier {node.id!r}")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstring_node_ids:
                continue
            val_low = node.value.lower()
            if "api.elevenlabs.io" in val_low:
                violations.append(
                    f"{filename}:{node.lineno}: forbidden ElevenLabs endpoint string {node.value!r}"
                )

    # Pass 1b: Fixed-point variable taint propagation (excluding comparisons/negations/docstrings)
    tainted_vars: set[str] = set()
    assign_nodes = [
        n for n in ast.walk(tree) if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign))
    ]
    list_mutator_calls = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name)
        and n.func.attr in ("append", "extend", "insert")
    ]
    for _ in range(4):
        changed = False
        for node in assign_nodes:
            if isinstance(node, ast.Assign):
                if _expr_is_tainted(node.value, tainted_vars):
                    for tgt in node.targets:
                        for nm in _collect_target_names(tgt):
                            if nm not in tainted_vars:
                                tainted_vars.add(nm)
                                changed = True
            elif isinstance(node, ast.AnnAssign):
                if node.value is not None and _expr_is_tainted(node.value, tainted_vars):
                    for nm in _collect_target_names(node.target):
                        if nm not in tainted_vars:
                            tainted_vars.add(nm)
                            changed = True
            elif isinstance(node, ast.AugAssign):
                if _expr_is_tainted(node.value, tainted_vars):
                    for nm in _collect_target_names(node.target):
                        if nm not in tainted_vars:
                            tainted_vars.add(nm)
                            changed = True
        for call in list_mutator_calls:
            var_name = call.func.value.id  # type: ignore[union-attr]
            if var_name not in tainted_vars and any(
                _expr_is_tainted(arg, tainted_vars) for arg in call.args
            ):
                tainted_vars.add(var_name)
                changed = True
        if not changed:
            break

    # Pass 2: Inspect resolved dangerous callees (dynamic imports, exec/eval, subprocess, os.exec/spawn)
    exact_dangerous = frozenset(
        {
            "__import__",
            "builtins.__import__",
            "exec",
            "builtins.exec",
            "eval",
            "builtins.eval",
            "importlib.import_module",
            "import_module",
            "os.system",
            "os.popen",
            "sh",
        }
    )
    substr_dangerous = ("subprocess", "popen", "system", "run_cmd", "check_call", "check_output", "install")

    def _resolve_call_name(func_node: ast.AST) -> str:
        raw = _call_name(func_node)
        if not raw:
            return ""
        parts = raw.split(".")
        if parts[0] in alias_map:
            raw = ".".join([alias_map[parts[0]], *parts[1:]])
        return raw.lower()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        cname = _resolve_call_name(node.func)
        if not cname:
            continue
        is_dangerous = (
            cname in exact_dangerous
            or cname.startswith(("subprocess.", "os.exec", "os.spawn"))
            or any(k in cname for k in substr_dangerous)
        )
        if not is_dangerous:
            continue
        call_inputs = list(node.args) + [kw.value for kw in node.keywords]
        for arg in call_inputs:
            if _expr_is_tainted(arg, tainted_vars):
                violations.append(
                    f"{filename}:{node.lineno}: forbidden dynamic/subprocess call {cname!r} "
                    f"with tainted edge-tts/elevenlabs argument"
                )
                break

    if violations:
        raise AssertionError(
            f"Zero-API / Zero-edge-tts AST audit failed on {filename}: {violations}"
        )
    return {"filename": filename, "violations": 0}


# Family 12
def oracle_variant_resolver_regex(
    filenames: Sequence[str],
    requested_targets: Sequence[str] | None = None,
    regex: re.Pattern[str] = VARIANT_RESOLVER_REGEX,
) -> dict[str, str]:
    """Resolve filenames without collision and validate requested episode/variant targets."""
    resolved: dict[str, str] = {}
    for fname in filenames:
        m = regex.match(Path(fname).name)
        if not m:
            raise AssertionError(f"Filename {fname!r} did not match resolver regex {regex.pattern!r}")
        key = m.group(1)
        if key in resolved:
            raise AssertionError(
                f"Resolver collision: both {resolved[key]!r} and {fname!r} collapsed onto key {key!r}"
            )
        resolved[key] = fname
    if requested_targets is not None:
        expanded: list[str] = []
        for tok in requested_targets:
            up = tok.strip().upper()
            if up == "E001_VARIANTS":
                for v in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
                    if v not in resolved:
                        raise AssertionError(f"E001_VARIANTS missing target {v!r}")
                    expanded.append(v)
            elif up == "ALL":
                expanded.extend(sorted(resolved.keys()))
            elif up in resolved:
                expanded.append(up)
            else:
                raise AssertionError(
                    f"Unknown episode/variant target {tok!r}; available: {sorted(resolved.keys())}"
                )
        if not expanded:
            raise AssertionError("Resolver produced 0 targets")
    return resolved


# Family 13
def oracle_srt_non_overlap_and_dual_line(
    srt_text: str,
    expected_translations: Sequence[str] | None = None,
    tts_prompts: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Verify monotonic non-overlapping SRT blocks, dual-line Chinese glosses, and zero TTS leak."""
    blocks = parse_srt(srt_text)
    if not blocks:
        raise AssertionError("SRT contains 0 subtitle blocks")
    prev_end = -1
    for expected_idx, blk in enumerate(blocks, start=1):
        if blk["index"] != expected_idx:
            raise AssertionError(
                f"SRT block index mismatch: expected {expected_idx}, got {blk['index']}"
            )
        if blk["end_ms"] <= blk["start_ms"]:
            raise AssertionError(
                f"SRT block {blk['index']} has non-positive duration: "
                f"{blk['start_ms']} -> {blk['end_ms']}"
            )
        if prev_end > blk["start_ms"]:
            raise AssertionError(
                f"SRT timestamp overlap at block {blk['index']}: "
                f"prev_end={prev_end}ms > start={blk['start_ms']}ms"
            )
        prev_end = blk["end_ms"]

    if expected_translations:
        all_two_line_texts = [
            "\n".join(b["lines"][1:]) for b in blocks if len(b["lines"]) >= 2
        ]
        joined_line2 = "\n".join(all_two_line_texts)
        for gloss in expected_translations:
            if gloss not in joined_line2:
                raise AssertionError(
                    f"Expected subtitle_translation gloss {gloss!r} missing from SRT line 2"
                )
        if tts_prompts is not None:
            joined_tts = "\n".join(tts_prompts)
            for gloss in expected_translations:
                if gloss in joined_tts:
                    raise AssertionError(
                        f"subtitle_translation {gloss!r} leaked into TTS prompt!"
                    )
    return {"block_count": len(blocks)}


# Family 14
def oracle_dual_script_zh_en_qa(
    tagged_prompt: str,
    asr_text: str,
    *,
    duration_s: float = 2.0,
    peak_dbfs: float = -6.0,
    language_code: str = "zh-en",
) -> dict[str, Any]:
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    res = evaluate_dialogue_qa(
        tagged_prompt=tagged_prompt,
        asr_text=asr_text,
        duration_s=duration_s,
        peak_dbfs=peak_dbfs,
        language_code=language_code,
    )
    if not res.passed:
        raise AssertionError(
            f"Dual-script QA failed (recall={res.char_recall:.2f}, tail={res.tail_preserved}, "
            f"leaked={res.leaked_tags}, reasons={res.reasons})"
        )
    return res.to_dict()


# Family 15
def oracle_domain_no_xianxia_leak(
    polyphone_input: str | None = None,
    polyphone_output: str | None = None,
    drama3_prompt: str | None = None,
) -> dict[str, Any]:
    """Assert zero Xianxia polyphone fallback and zero Xianxia narration injection."""
    if polyphone_input is not None and polyphone_output is not None:
        if "引气" in polyphone_input and "引气九崇" in polyphone_output:
            raise AssertionError(
                f"Xianxia polyphone fallback leaked: {polyphone_input!r} -> {polyphone_output!r}"
            )
        if "降临" in polyphone_input and "酱临" in polyphone_output:
            raise AssertionError(
                f"Xianxia polyphone fallback leaked ('降临'->'酱临'): {polyphone_output!r}"
            )
        if "辟谷" in polyphone_input and "必谷" in polyphone_output:
            raise AssertionError(
                f"Xianxia polyphone fallback leaked ('辟谷'->'必谷'): {polyphone_output!r}"
            )
    if drama3_prompt is not None:
        low = drama3_prompt.lower()
        if "xianxia" in low or "修仙" in drama3_prompt:
            raise AssertionError(
                f"Xianxia narration/domain string leaked into Drama 3 prompt: {drama3_prompt!r}"
            )
    return {"clean": True}


# Family 16
_WEIGHT_COL_PRIMARY_RE = re.compile(r"权重|weight|占比|配分", re.IGNORECASE)
_WEIGHT_COL_SECONDARY_RE = re.compile(r"分值|满分|points|pts", re.IGNORECASE)
_RANGE_SEP = r"(?:\s*(?:→|->|~|～|—|–|\.\.|至|-)\s*|\s+[tT][oO]\s+)"
_CUE_RANGE_RE = re.compile(
    rf"[`*_]{{0,3}}([A-Za-z0-9_]+)[`*_]{{0,3}}{_RANGE_SEP}[`*_]{{0,3}}([A-Za-z0-9_]+)[`*_]{{0,3}}"
)
_EXPLICIT_BAD_RANGE_RE = re.compile(
    rf"[`*_]{{0,3}}((?:E001_)?V[ABCD]_[A-Za-z0-9_]+)[`*_]{{0,3}}{_RANGE_SEP}"
    rf"[`*_]{{0,3}}((?:E001_)?V[ABCD]_[A-Za-z0-9_]+)[`*_]{{0,3}}"
)
_OVERVIEW_HEADING_RE = re.compile(
    r"(?:总览|概述|概览|总控表|总表|索引|目录|架构|播客主盘|主盘发布|发行日历|排期|show\s*notes|overview|summary|toc)",
    re.IGNORECASE,
)
_CUTLIST_CTX_KWS = ("切片", "cutlist", "45s", "45秒", "视频号", "短视频", "viral", "clip", "高光", "引流片", "38", "55")
_HOOK_KWS = ("3秒", "3s", "3-second", "开场钩子", "冲突钩子", "hook", "钩子")
_HOOK_3S_RE = re.compile(r"3\s*秒")
_CTA_KWS = ("cta", "引流", "小宇宙", "精读手册", "专栏", "评论区", "听完整", "完整版", "搜索")
_TITLE_KWS = ("vs", "标题", "headline", "冲突", "封面")


def _has_hook_cue(text_low: str) -> bool:
    return any(k in text_low for k in _HOOK_KWS) or bool(_HOOK_3S_RE.search(text_low))


def parse_rubric_blind_weights(rubric_md: str) -> list[tuple[str, int]]:
    """Extract blind-listening rubric dimension weights (5..10 dimensions summing to 100)
    using header-aware weight-column detection prioritized over non-weight tables."""
    lines = rubric_md.splitlines()
    tables: list[list[list[str]]] = []
    cur_table: list[list[str]] = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            cur_table.append(cells)
        else:
            if cur_table:
                tables.append(cur_table)
                cur_table = []
    if cur_table:
        tables.append(cur_table)

    def _extract_weight(cell: str) -> int | None:
        cleaned = cell.replace("*", "").replace("`", "").strip()
        m = re.fullmatch(r"(\d{1,3})\s*(?:%|分|pts?|points?|/100)?", cleaned, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 60:
                return val
        return None

    explicit_weight_cands: list[list[tuple[str, int]]] = []
    generic_cands: list[list[tuple[str, int]]] = []

    for tbl in tables:
        if len(tbl) < 3:
            continue
        header_cells = tbl[0]
        header_low = " ".join(header_cells).lower()
        weight_col_idx = next(
            (idx for idx, hcell in enumerate(header_cells) if _WEIGHT_COL_PRIMARY_RE.search(hcell)),
            None,
        )
        if weight_col_idx is None:
            weight_col_idx = next(
                (idx for idx, hcell in enumerate(header_cells) if _WEIGHT_COL_SECONDARY_RE.search(hcell)),
                None,
            )
        is_blind_table = weight_col_idx is not None or any(
            k in header_low for k in ("score", "维度", "dimension")
        )
        if not is_blind_table:
            continue

        rows_out: list[tuple[str, int]] = []
        for row in tbl[1:]:
            if all(re.fullmatch(r"[-:\s]+", c) for c in row):
                continue
            row_joined = " ".join(row).lower()
            if any(k in row_joined for k in ("总分", "合计", "总计", "total", "100分", "100%")):
                continue
            weight_val: int | None = None
            if weight_col_idx is not None and weight_col_idx < len(row):
                weight_val = _extract_weight(row[weight_col_idx])
            else:
                for cell in row[1:]:
                    w = _extract_weight(cell)
                    if w is not None:
                        weight_val = w
                        break
            if weight_val is not None:
                rows_out.append((row[0], weight_val))

        if weight_col_idx is not None and len(rows_out) >= 3:
            explicit_weight_cands.append(rows_out)
        elif len(rows_out) >= 5:
            generic_cands.append(rows_out)

    # Explicit weight-column tables ALWAYS outrank generic tables
    for pool in (explicit_weight_cands, generic_cands):
        if not pool:
            continue
        in_range = [c for c in pool if 5 <= len(c) <= 10]
        if in_range:
            for c in in_range:
                if sum(w for _, w in c) == 100:
                    return c
            return in_range[0]
        return pool[0]

    # Strategy 2: fallback bulleted list like "- **维度1...**（20分）" or "1. Dimension (20 pts)"
    bullet_rows: list[tuple[str, int]] = []
    for ln in lines:
        m = re.search(
            r"^(?:[-*]|\d+\.)\s+(.+?)[（(\[]\s*(\d{1,2})\s*(?:分|%|pts?|points?)\s*[）)\]]",
            ln.strip(),
            re.IGNORECASE,
        )
        if m:
            label = m.group(1).strip()
            if any(k in label.lower() for k in ("总分", "合计", "总计", "total")):
                continue
            bullet_rows.append((label, int(m.group(2))))
    return bullet_rows


def _extract_range_in_text(
    text: str,
    cue_id_list: Sequence[str],
    cue_id_set: set[str],
    *,
    allow_bare_id_fallback: bool,
) -> tuple[str, str] | None:
    for a, b in _CUE_RANGE_RE.findall(text):
        if a in cue_id_set and b in cue_id_set:
            return (a, b)
    if allow_bare_id_fallback:
        found_ids = [cid for cid in cue_id_list if re.search(rf"\b{re.escape(cid)}\b", text)]
        if len(found_ids) >= 2:
            return (found_ids[0], found_ids[-1])
    bad_ranges = _EXPLICIT_BAD_RANGE_RE.findall(text)
    if bad_ranges:
        return bad_ranges[0]
    return None


def extract_viral_cutlists_from_markdown(
    md_text: str,
    cue_sheets_by_variant: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract executable viral clip cutlist definitions across 3 Markdown layouts:
    (A) Markdown table rows, (B) multi-variant bullet/line lists, (C) per-heading single-variant sections.
    Suppresses overview bare-ID fallback and avoids double-counting summary/index tables (lacking hook & CTA
    columns) when detailed per-clip sections define the exact same (variant_id, start_cue_id, end_cue_id).
    """
    sections = re.split(r"(?m)^(?=#{2,4}\s+)", md_text)
    raw_items: list[tuple[str, dict[str, Any]]] = []

    def _cell_filled(val: str) -> bool:
        cleaned = val.strip(" -—–/\\*`").lower()
        return cleaned not in ("", "n/a", "none", "无", "待定")

    for sec in sections:
        if not sec.strip():
            continue
        sec_lines = sec.splitlines()
        heading_line = sec_lines[0] if sec_lines else ""
        var_matches = re.findall(r"\b(E001_V[ABCD])\b", sec)
        if not var_matches:
            continue
        heading_vars = list(dict.fromkeys(re.findall(r"\b(E001_V[ABCD])\b", heading_line)))

        # Separate table blocks vs non-table prose in this section
        table_blocks: list[list[tuple[str, list[str]]]] = []
        cur_tbl: list[tuple[str, list[str]]] = []
        prose_lines: list[str] = []
        for ln in sec_lines:
            st = ln.strip()
            if st.startswith("|") and st.endswith("|"):
                cells = [c.strip() for c in st.strip("|").split("|")]
                cur_tbl.append((st, cells))
            else:
                if cur_tbl:
                    table_blocks.append(cur_tbl)
                    cur_tbl = []
                prose_lines.append(ln)
        if cur_tbl:
            table_blocks.append(cur_tbl)

        prose_low = "\n".join(prose_lines).lower()

        # Layout A: Markdown Table Rows
        table_extracted: list[tuple[str, dict[str, Any]]] = []
        for tbl in table_blocks:
            if len(tbl) < 3:
                continue
            header_cells = tbl[0][1]
            hook_col = next(
                (i for i, c in enumerate(header_cells) if re.search(r"钩子|hook|3\s*秒", c, re.IGNORECASE)),
                None,
            )
            cta_col = next((i for i, c in enumerate(header_cells) if re.search(r"cta|引流", c, re.IGNORECASE)), None)
            title_col = next(
                (i for i, c in enumerate(header_cells) if re.search(r"标题|headline|title|封面", c, re.IGNORECASE)),
                None,
            )
            row_kind = "table_summary" if (hook_col is None and cta_col is None) else "table_full"
            for row_line, cells in tbl[1:]:
                if all(re.fullmatch(r"[-:\s]+", c) for c in cells):
                    continue
                row_vars = list(dict.fromkeys(re.findall(r"\b(E001_V[ABCD])\b", row_line)))
                if len(row_vars) == 1:
                    vid = row_vars[0]
                    allow_bare = True
                elif not row_vars and len(heading_vars) == 1:
                    vid = heading_vars[0]
                    allow_bare = False
                else:
                    continue
                cs = cue_sheets_by_variant.get(vid)
                if cs is None:
                    continue
                cue_id_list = [c.cue_id for c in cs.cues]
                cue_id_set = set(cue_id_list)
                rng = _extract_range_in_text(
                    row_line,
                    cue_id_list,
                    cue_id_set,
                    allow_bare_id_fallback=allow_bare,
                )
                if rng is None:
                    continue
                row_low = row_line.lower()
                if hook_col is not None and hook_col < len(cells):
                    has_hook = _cell_filled(cells[hook_col]) or _has_hook_cue(row_low)
                else:
                    has_hook = _has_hook_cue(row_low) or _has_hook_cue(prose_low)
                if cta_col is not None and cta_col < len(cells):
                    has_cta = _cell_filled(cells[cta_col]) or any(k in row_low for k in _CTA_KWS)
                else:
                    has_cta = any(k in row_low or k in prose_low for k in _CTA_KWS)
                if title_col is not None and title_col < len(cells):
                    has_title = _cell_filled(cells[title_col]) or any(k in row_low for k in _TITLE_KWS)
                else:
                    has_title = any(k in row_low or k in prose_low for k in _TITLE_KWS)
                table_extracted.append(
                    (
                        row_kind,
                        {
                            "variant_id": vid,
                            "start_cue_id": rng[0],
                            "end_cue_id": rng[1],
                            "has_hook": has_hook,
                            "has_cta": has_cta,
                            "has_title": has_title,
                            "raw_section": row_line[:300],
                        },
                    )
                )
        if table_extracted:
            raw_items.extend(table_extracted)
            continue

        unique_vars = list(dict.fromkeys(var_matches))

        # Layout B: Multi-Variant Bullet / Line List under One Heading
        if len(unique_vars) >= 2:
            for ln in sec_lines[1:]:
                ln_vars = list(dict.fromkeys(re.findall(r"\b(E001_V[ABCD])\b", ln)))
                if len(ln_vars) != 1:
                    continue
                vid = ln_vars[0]
                cs = cue_sheets_by_variant.get(vid)
                if cs is None:
                    continue
                cue_id_list = [c.cue_id for c in cs.cues]
                cue_id_set = set(cue_id_list)
                rng = _extract_range_in_text(
                    ln,
                    cue_id_list,
                    cue_id_set,
                    allow_bare_id_fallback=False,
                )
                if rng is None:
                    continue
                ctx_low = (ln + "\n" + prose_low).lower()
                raw_items.append(
                    (
                        "bullet",
                        {
                            "variant_id": vid,
                            "start_cue_id": rng[0],
                            "end_cue_id": rng[1],
                            "has_hook": _has_hook_cue(ctx_low),
                            "has_cta": any(k in ctx_low for k in _CTA_KWS),
                            "has_title": any(k in ctx_low for k in _TITLE_KWS),
                            "raw_section": ln[:300],
                        },
                    )
                )
            continue

        # Layout C: Standard Per-Heading Single-Variant Section
        variant_id = unique_vars[0]
        cs = cue_sheets_by_variant.get(variant_id)
        if cs is None:
            continue
        cue_id_list = [c.cue_id for c in cs.cues]
        cue_id_set = set(cue_id_list)
        sec_low = sec.lower()
        is_overview = bool(_OVERVIEW_HEADING_RE.search(heading_line))
        if is_overview:
            continue
        has_ctx = any(k in sec_low for k in _CUTLIST_CTX_KWS)
        matched_range = _extract_range_in_text(
            sec,
            cue_id_list,
            cue_id_set,
            allow_bare_id_fallback=has_ctx,
        )
        if matched_range is None:
            continue
        raw_items.append(
            (
                "section",
                {
                    "variant_id": variant_id,
                    "start_cue_id": matched_range[0],
                    "end_cue_id": matched_range[1],
                    "has_hook": _has_hook_cue(sec_low),
                    "has_cta": any(k in sec_low for k in _CTA_KWS),
                    "has_title": any(k in sec_low for k in _TITLE_KWS),
                    "raw_section": sec[:300],
                },
            )
        )

    # Drop at most one overview/index table row per exact (variant, start, end) when a detailed section defines it,
    # while strictly preserving duplicate detection within detailed sections / full tables / duplicate summary rows.
    detailed_keys = {
        (entry["variant_id"], entry["start_cue_id"], entry["end_cue_id"])
        for kind, entry in raw_items
        if kind != "table_summary"
    }
    suppressed_summary_keys: set[tuple[str, str, str]] = set()
    cutlists: list[dict[str, Any]] = []
    for kind, entry in raw_items:
        key = (entry["variant_id"], entry["start_cue_id"], entry["end_cue_id"])
        if kind == "table_summary" and key in detailed_keys and key not in suppressed_summary_keys:
            suppressed_summary_keys.add(key)
            continue
        cutlists.append(entry)
    return cutlists


def oracle_viral_45s_cutlist_and_rubric(
    cutlists: Sequence[dict[str, Any]] | None = None,
    cue_sheets_by_variant: dict[str, Any] | None = None,
    rubric_md: str | None = None,
) -> dict[str, Any]:
    """Validate 45s viral clip cutlists ([38, 55]s, unique ordered cue_ids, hook+CTA, anti-padding)
    and 5..10 dimension 100-pt blind-listening rubric."""
    res: dict[str, Any] = {}
    if cutlists is not None:
        if not cutlists:
            raise AssertionError("No executable viral clip cutlists found")
        if not cue_sheets_by_variant:
            raise AssertionError("cue_sheets_by_variant required to validate cutlists")
        checked: list[dict[str, Any]] = []
        seen_ranges: set[tuple[str, str, str]] = set()
        covered_variants: set[str] = set()
        for idx, cl in enumerate(cutlists):
            vid = cl["variant_id"]
            cs = cue_sheets_by_variant.get(vid)
            if cs is None:
                raise AssertionError(f"Cutlist[{idx}] references unknown variant {vid!r}")
            id_to_idx = {c.cue_id: i for i, c in enumerate(cs.cues)}
            s_id = cl["start_cue_id"]
            e_id = cl["end_cue_id"]
            key = (vid, s_id, e_id)
            if key in seen_ranges:
                raise AssertionError(f"Duplicate viral clip cutlist detected: {vid} {s_id}..{e_id}")
            seen_ranges.add(key)
            covered_variants.add(vid)
            if s_id not in id_to_idx:
                raise AssertionError(f"Cutlist[{idx}] ({vid}) start cue_id {s_id!r} not found in cue sheet")
            if e_id not in id_to_idx:
                raise AssertionError(f"Cutlist[{idx}] ({vid}) end cue_id {e_id!r} not found in cue sheet")
            si, ei = id_to_idx[s_id], id_to_idx[e_id]
            if si > ei:
                raise AssertionError(
                    f"Cutlist[{idx}] ({vid}) inverted cue range: {s_id} (idx {si}) > {e_id} (idx {ei})"
                )
            dur_s = estimate_cue_slice_duration_s(cs.cues[si : ei + 1])
            if not (38.0 <= dur_s <= 55.0):
                raise AssertionError(
                    f"Cutlist[{idx}] ({vid} {s_id}..{e_id}): estimated duration={dur_s:.1f}s outside [38.0, 55.0]s"
                )
            if not cl.get("has_hook", False):
                raise AssertionError(f"Cutlist[{idx}] ({vid}) missing 3-second conflict hook")
            if not cl.get("has_cta", False):
                raise AssertionError(f"Cutlist[{idx}] ({vid}) missing funnel CTA")
            checked.append({"variant_id": vid, "start": s_id, "end": e_id, "duration_s": round(dur_s, 1)})
        all_four = {"E001_VA", "E001_VB", "E001_VC", "E001_VD"}
        if len(cutlists) >= 4 and all_four <= set(cue_sheets_by_variant.keys()):
            missing_vars = sorted(all_four - covered_variants)
            if missing_vars:
                raise AssertionError(
                    f"4+ viral cutlists audited across 4-variant benchmark must cover all 4 distinct variants "
                    f"(no single-variant padding); missing: {missing_vars}, covered: {sorted(covered_variants)}"
                )
        res["cutlists"] = checked

    if rubric_md is not None:
        weights = parse_rubric_blind_weights(rubric_md)
        if not (5 <= len(weights) <= 10):
            raise AssertionError(
                f"Blind listening rubric must define 5..10 weighted dimensions, found {len(weights)}: {weights}"
            )
        total_w = sum(w for _, w in weights)
        if total_w != 100:
            raise AssertionError(
                f"Blind listening rubric weights sum to {total_w}, expected exact 100: {weights}"
            )
        res["rubric_weights"] = weights
        res["rubric_sum"] = total_w
    return res


# Family 17
def oracle_notebook_and_bundle_integrity(
    notebook_data: dict[str, Any] | None = None,
    zip_path: Path | None = None,
    voice_cast_manifest: dict[str, Any] | None = None,
    launcher_help_flags: set[str] | None = None,
) -> dict[str, Any]:
    """Validate Colab G4 .ipynb schema/AST/flag-parity, self-contained ZIP bundle, and v2 anchor manifest."""
    summary: dict[str, Any] = {}

    if notebook_data is not None:
        if notebook_data.get("nbformat") != 4:
            raise AssertionError(f"Notebook nbformat={notebook_data.get('nbformat')}, expected 4")
        meta = notebook_data.get("metadata") or {}
        if meta.get("accelerator") != "GPU":
            raise AssertionError(f"Notebook metadata.accelerator={meta.get('accelerator')!r}, expected 'GPU'")
        colab_meta = meta.get("colab") or {}
        if colab_meta.get("gpuType") != "G4":
            raise AssertionError(f"Notebook metadata.colab.gpuType={colab_meta.get('gpuType')!r}, expected 'G4'")
        cells = notebook_data.get("cells") or []
        if not cells:
            raise AssertionError("Notebook contains 0 cells")
        all_code_parts: list[str] = []
        code_cell_count = 0
        for idx, cell in enumerate(cells):
            ctype = cell.get("cell_type")
            src = cell.get("source", "")
            if isinstance(src, list):
                src = "".join(src)
            if ctype == "code":
                code_cell_count += 1
                if cell.get("outputs"):
                    raise AssertionError(f"Notebook code cell {idx} has non-empty outputs (must be clean)")
                if cell.get("execution_count") is not None:
                    raise AssertionError(f"Notebook code cell {idx} has non-null execution_count")
                cleaned = strip_notebook_magics(src)
                try:
                    ast.parse(cleaned, filename=f"cell_{idx}.py")
                except SyntaxError as exc:
                    raise AssertionError(f"Notebook code cell {idx} Python SyntaxError: {exc}") from exc
                all_code_parts.append(src)
        full_code = "\n".join(all_code_parts)
        if "colab_agent_bridge.py" not in full_code:
            raise AssertionError("Notebook missing Mode A (Agent HTTPS Bridge / colab_agent_bridge.py)")
        if "launch_g4_global_edge_drama3.py" not in full_code:
            raise AssertionError("Notebook missing Mode B (Direct Run / launch_g4_global_edge_drama3.py)")
        if "E001_VARIANTS" not in full_code and not all(
            v in full_code for v in ("E001_VA", "E001_VB", "E001_VC", "E001_VD")
        ):
            raise AssertionError("Notebook missing E001_VARIANTS / multi-variant launch target")
        nb_flags = extract_notebook_launcher_flags(notebook_data)
        if launcher_help_flags is not None:
            if not nb_flags:
                raise AssertionError(
                    "Notebook invokes launch_g4_global_edge_drama3.py with 0 extracted CLI flags"
                )
            unknown = sorted(nb_flags - launcher_help_flags)
            if unknown:
                raise AssertionError(
                    f"Notebook passes unsupported CLI flag(s) to launch_g4_global_edge_drama3.py: "
                    f"{unknown} (supported: {sorted(launcher_help_flags)})"
                )
        summary["notebook"] = {
            "code_cells": code_cell_count,
            "launcher_flags": sorted(nb_flags),
        }

    if zip_path is not None:
        require_file(zip_path, label="bundle.zip")
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad_member = zf.testzip()
            if bad_member is not None:
                raise AssertionError(f"Corrupt ZIP member {bad_member!r} in {zip_path}")
            names = set(zf.namelist())
        if any("__pycache__" in n or n.endswith(".pyc") for n in names):
            raise AssertionError(f"ZIP bundle {zip_path} contains __pycache__/.pyc pollution")
        required_exact = (
            "voice_casting_registry.json",
            "voice_cast_drama3.json",
            "src/aigc_audio_pipeline/models.py",
            "src/aigc_audio_pipeline/mixer.py",
            "prepare_global_edge_voice_anchors.py",
            "run_global_edge_96gb_studio.py",
            "launch_g4_global_edge_drama3.py",
        )
        miss_exact = [m for m in required_exact if m not in names]
        if miss_exact:
            raise AssertionError(f"ZIP bundle missing required members: {miss_exact}")
        if not any(n.startswith("auditions/AUDITION_GLOBAL_EDGE") and n.endswith(".json") for n in names):
            raise AssertionError("ZIP bundle missing auditions/AUDITION_GLOBAL_EDGE*.json")
        for vid in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
            if not any(n.startswith(f"cue_sheets/{vid}") and n.endswith(".json") for n in names):
                raise AssertionError(f"ZIP bundle missing cue_sheets/{vid}*.json")
        if not any(n.startswith("voice_anchors/") and n.endswith(".wav") for n in names):
            raise AssertionError("ZIP bundle missing voice_anchors/*.wav")
        summary["zip_member_count"] = len(names)

    if voice_cast_manifest is not None:
        ver = voice_cast_manifest.get("anchor_schema_version")
        if ver != "v2_real_human_studio":
            raise AssertionError(
                f"anchor_schema_version={ver!r}, expected 'v2_real_human_studio'"
            )
        sr = int(voice_cast_manifest.get("anchor_sample_rate_hz", 0))
        if sr != 44100:
            raise AssertionError(f"anchor_sample_rate_hz={sr}, expected 44100")
        chars = voice_cast_manifest.get("characters") or {}
        if not chars:
            raise AssertionError("voice_cast_drama3.json has empty characters map")
        for rid, entry in chars.items():
            src_name = str(entry.get("source_voice_name", ""))
            if "neural" in src_name.lower() or "edge-tts" in src_name.lower() or "edge_tts" in src_name.lower():
                raise AssertionError(
                    f"Synthetic Edge/Neural voice detected in anchor manifest for {rid!r}: {src_name!r}"
                )
            if not str(entry.get("anchor_text", "")).strip():
                raise AssertionError(f"Empty anchor_text in manifest for {rid!r}")
        summary["manifest_roles"] = len(chars)

    return summary


# Family 18
def oracle_audio_signal_and_atempo_ratio(
    wav_48k_path: Path | None = None,
    wav_anchor_path: Path | None = None,
    slow_wav_path: Path | None = None,
    base_wav_path: Path | None = None,
    expected_pitch_hz: float | None = None,
    check_ffmpeg_bin: str | None = None,
) -> dict[str, Any]:
    """Validate WAV format/peak/duration, 0.80x atempo stretch + pitch preservation, and ffmpeg check."""
    out: dict[str, Any] = {}
    if check_ffmpeg_bin is not None:
        ff, fp = require_ffmpeg(ffmpeg_bin=check_ffmpeg_bin)
        out["ffmpeg"] = ff
        out["ffprobe"] = fp

    if wav_48k_path is not None:
        info = read_wav_info_and_mono_samples(wav_48k_path)
        if info["sample_rate"] != 48000:
            raise AssertionError(f"{wav_48k_path.name}: sample_rate={info['sample_rate']}, expected 48000")
        if info["channels"] != 2:
            raise AssertionError(f"{wav_48k_path.name}: channels={info['channels']}, expected 2 (stereo)")
        if info["peak_dbfs"] < -45.0:
            raise AssertionError(f"{wav_48k_path.name}: silent/near-silent peak={info['peak_dbfs']:.1f} dBFS")
        out["wav_48k"] = {"sr": info["sample_rate"], "ch": info["channels"], "dur_s": info["duration_s"], "peak_dbfs": info["peak_dbfs"]}

    if wav_anchor_path is not None:
        info = read_wav_info_and_mono_samples(wav_anchor_path)
        if info["sample_rate"] != 44100:
            raise AssertionError(f"{wav_anchor_path.name}: sample_rate={info['sample_rate']}, expected 44100")
        if info["channels"] != 1:
            raise AssertionError(f"{wav_anchor_path.name}: channels={info['channels']}, expected 1 (mono)")
        if info["duration_s"] <= 0.25:
            raise AssertionError(f"{wav_anchor_path.name}: duration_s={info['duration_s']:.3f} too short")
        if info["peak_dbfs"] < -45.0:
            raise AssertionError(f"{wav_anchor_path.name}: silent anchor peak={info['peak_dbfs']:.1f} dBFS")
        out["wav_anchor"] = {"sr": info["sample_rate"], "ch": info["channels"], "dur_s": info["duration_s"]}

    if slow_wav_path is not None and base_wav_path is not None:
        base = read_wav_info_and_mono_samples(base_wav_path)
        slow = read_wav_info_and_mono_samples(slow_wav_path)
        if base["duration_s"] <= 0:
            raise AssertionError("Base WAV has 0s duration")
        ratio = slow["duration_s"] / base["duration_s"]
        if not (1.18 <= ratio <= 1.32):
            raise AssertionError(
                f"0.80x slowdown duration ratio={ratio:.3f} (slow={slow['duration_s']:.3f}s / "
                f"base={base['duration_s']:.3f}s) outside [1.18, 1.32]"
            )
        out["atempo_ratio"] = ratio
        if expected_pitch_hz is not None:
            sr = slow["sample_rate"]
            samples = slow["samples"]
            margin = min(len(samples) // 5, int(0.35 * sr))
            mid = samples[margin : len(samples) - margin] if len(samples) > 2 * margin + 100 else samples
            f_zc = estimate_pitch_zero_crossings(mid, sr)
            e_target = goertzel_power(mid, sr, expected_pitch_hz)
            e_shifted = goertzel_power(mid, sr, expected_pitch_hz * 0.8)
            if not (expected_pitch_hz - 25.0 <= f_zc <= expected_pitch_hz + 25.0):
                raise AssertionError(
                    f"Pitch not preserved on 0.80x atempo: zero-crossing est={f_zc:.1f}Hz, "
                    f"expected {expected_pitch_hz:.1f}±25Hz (naive resample would be {expected_pitch_hz*0.8:.1f}Hz)"
                )
            if e_target <= 5.0 * e_shifted:
                raise AssertionError(
                    f"Goertzel spectral power failed pitch preservation: "
                    f"E({expected_pitch_hz:.0f}Hz)={e_target:.6f} <= 5 * E({expected_pitch_hz*0.8:.0f}Hz)={e_shifted:.6f}"
                )
            out["pitch_hz"] = f_zc
            out["goertzel_ratio"] = e_target / max(e_shifted, 1e-12)

    return out


def oracle_corporate_acoustic_spaces_dsp(
    *,
    dry_mt_wav: Path,
    phone_mt_wav: Path,
    inner_mt_wav: Path,
    boardroom_mt_wav: Path | None = None,
    dry_burst_wav: Path | None = None,
    inner_burst_wav: Path | None = None,
    boardroom_burst_wav: Path | None = None,
    burst_end_s: float = 0.80,
) -> dict[str, Any]:
    """Verify non-identity DSP behavior across corporate acoustic spaces using pure-stdlib
    Goertzel spectral ratios + tone-burst RMS tail analysis:
      - phone_call: 300-3400Hz bandpass attenuating 100Hz & 6000Hz (<0.25x dry)
      - inner_monologue: proximity EQ boost at 150Hz (>1.20x) & 3200Hz (>1.10x), zero cavern echo
      - boardroom: tight early reflection tail (15-55ms >=0.015) with zero late cavern tail (45-160ms <0.02)
    """
    def _load_48k_stereo(path: Path) -> dict[str, Any]:
        info = read_wav_info_and_mono_samples(path)
        if info["sample_rate"] != 48000:
            raise AssertionError(f"{path.name}: sample_rate={info['sample_rate']}, expected 48000")
        if info["channels"] != 2:
            raise AssertionError(f"{path.name}: channels={info['channels']}, expected 2")
        if info["peak_dbfs"] < -45.0:
            raise AssertionError(f"{path.name}: silent/near-silent peak={info['peak_dbfs']:.1f} dBFS")
        return info

    def _mt_ratios(info: dict[str, Any]) -> dict[float, float]:
        sr = info["sample_rate"]
        samples = info["samples"]
        margin = min(len(samples) // 5, int(0.30 * sr))
        mid = samples[margin : len(samples) - margin] if len(samples) > 2 * margin + 100 else samples
        e1k = max(goertzel_power(mid, sr, 1000.0), 1e-12)
        return {
            f: goertzel_power(mid, sr, f) / e1k
            for f in (100.0, 150.0, 3200.0, 6000.0)
        }

    dry_r = _mt_ratios(_load_48k_stereo(dry_mt_wav))
    ph_r = _mt_ratios(_load_48k_stereo(phone_mt_wav))
    inn_r = _mt_ratios(_load_48k_stereo(inner_mt_wav))
    if boardroom_mt_wav is not None:
        _load_48k_stereo(boardroom_mt_wav)

    if ph_r[100.0] >= dry_r[100.0] * 0.25:
        raise AssertionError(
            f"phone_call failed to attenuate 100Hz vs dry (phone={ph_r[100.0]:.4f}, dry={dry_r[100.0]:.4f})"
        )
    if ph_r[6000.0] >= dry_r[6000.0] * 0.25:
        raise AssertionError(
            f"phone_call failed to attenuate 6000Hz vs dry (phone={ph_r[6000.0]:.4f}, dry={dry_r[6000.0]:.4f})"
        )
    if inn_r[150.0] <= dry_r[150.0] * 1.20:
        raise AssertionError(
            f"inner_monologue failed 150Hz proximity EQ boost vs dry "
            f"(inner={inn_r[150.0]:.4f}, dry={dry_r[150.0]:.4f}, ratio={inn_r[150.0]/max(dry_r[150.0],1e-12):.3f}x)"
        )
    if inn_r[3200.0] <= dry_r[3200.0] * 1.10:
        raise AssertionError(
            f"inner_monologue failed 3200Hz presence EQ boost vs dry "
            f"(inner={inn_r[3200.0]:.4f}, dry={dry_r[3200.0]:.4f}, ratio={inn_r[3200.0]/max(dry_r[3200.0],1e-12):.3f}x)"
        )

    out: dict[str, Any] = {
        "phone_100_vs_dry": ph_r[100.0] / max(dry_r[100.0], 1e-12),
        "phone_6000_vs_dry": ph_r[6000.0] / max(dry_r[6000.0], 1e-12),
        "inner_150_vs_dry": inn_r[150.0] / max(dry_r[150.0], 1e-12),
        "inner_3200_vs_dry": inn_r[3200.0] / max(dry_r[3200.0], 1e-12),
    }

    def _burst_tail_ratios(path: Path) -> tuple[float, float]:
        info = _load_48k_stereo(path)
        sr = info["sample_rate"]
        samples = info["samples"]

        def _rms(t0: float, t1: float) -> float:
            a = max(0, int(round(t0 * sr)))
            b = min(len(samples), int(round(t1 * sr)))
            sl = samples[a:b]
            if not sl:
                return 0.0
            return math.sqrt(sum(x * x for x in sl) / len(sl))

        act = _rms(0.10, max(0.15, burst_end_s - 0.05))
        if act < 1e-4:
            raise AssertionError(f"{path.name}: tone burst active window is silent (rms={act:.6f})")
        early = _rms(burst_end_s + 0.015, burst_end_s + 0.055) / act
        late = _rms(burst_end_s + 0.045, burst_end_s + 0.160) / act
        return early, late

    dry_early = 0.0
    if dry_burst_wav is not None:
        dry_early, dry_late = _burst_tail_ratios(dry_burst_wav)
        out["dry_burst"] = {"early": dry_early, "late": dry_late}

    if inner_burst_wav is not None:
        in_early, in_late = _burst_tail_ratios(inner_burst_wav)
        out["inner_burst"] = {"early": in_early, "late": in_late}
        if in_early >= 0.015 or in_late >= 0.01:
            raise AssertionError(
                f"inner_monologue must remain dry/intimate with zero cavern echo "
                f"(early={in_early:.5f}, late={in_late:.5f})"
            )

    if boardroom_burst_wav is not None:
        br_early, br_late = _burst_tail_ratios(boardroom_burst_wav)
        out["boardroom_burst"] = {"early": br_early, "late": br_late}
        if br_early < 0.015 or br_early <= dry_early * 5.0 + 0.01:
            raise AssertionError(
                f"boardroom missing tight early glass-room reflections vs dry "
                f"(boardroom_early={br_early:.5f}, dry_early={dry_early:.5f})"
            )
        if br_late >= 0.02:
            raise AssertionError(
                f"boardroom has excessive late cavern reverb tail (late={br_late:.5f} >= 0.02)"
            )

    return out


# ---------------------------------------------------------------------------
# Synthetic Fixture Builders (Used by Tier 2 Negative Tests & --self-test)
# ---------------------------------------------------------------------------

def make_minimal_registry(include_locked: bool = True):
    from aigc_audio_pipeline.models import SonicMotif, VoiceCastingRegistry, VoiceProfile

    has_accent = "accent_code" in {f.name for f in dataclasses.fields(VoiceProfile)}
    roles: dict[str, VoiceProfile] = {}
    specs = [
        ("lin_chen", "Lin Chen", "protagonist", "male", "zh-en", "zh_en_bilingual_us", "[measured] That is a phantom number, Victoria. 先把账算清楚。"),
        ("zhou_mo", "Zhou Mo", "core_supporting", "male", "zh-en", "zh_mainland_sz", "[dry] 这批芯片的良率和 token 成本必须重算。"),
        ("victoria_vance", "Victoria Vance", "antagonist", "female", "en", "us_silicon_valley", "[icy polite] Your cap table has an uncomfortable story to tell."),
        ("alistair_finch", "Alistair Finch", "antagonist", "male", "en", "uk_london_rp", "[deadpan] Margin compression is rather unforgiving in London."),
        ("claire_chen_gc", "Claire Sterling", "core_supporting", "female", "en", "us_nyc", "[firmly] The convertible note covenants are non-negotiable."),
        ("rajiv_menon", "Rajiv Menon", "recurring", "male", "en", "intl_indian_exec", "[measured] We need clarity on the supply chain buffer."),
        ("wei_ling_tan", "Wei-Ling Tan", "recurring", "female", "en", "intl_singapore_vc", "[calmly] Sovereign capital looks three cycles ahead."),
        ("henrik_lindqvist", "Henrik Lindqvist", "recurring", "male", "en", "intl_eu_legal", "[guarded] EU AI Act compliance is mandatory before launch."),
    ]
    for idx, (rid, name, tier, gender, lang, accent, line) in enumerate(specs, start=1):
        kw: dict[str, Any] = dict(
            role_id=rid,
            display_name=name,
            aliases=[name],
            tier=tier,
            gender=gender,
            age_group="35-45",
            language_code=lang,
            vocal_register="baritone" if gender == "male" else "alto",
            persona_summary=f"Canonical role {name}",
            accent_requirement=accent,
            status="locked" if include_locked else "pending_audition",
            voice_id=f"drama3_anchor_{rid}_{idx:02d}" if include_locked else "",
            default_stability=0.5,
            signature_tags=["measured", "deadpan"],
            forbidden_habits=["no yelling", "no announcer voice"],
            audition_line=line,
        )
        if has_accent:
            kw["accent_code"] = accent
        roles[rid] = VoiceProfile(**kw)

    motifs = {
        "boardroom_door": SonicMotif(
            motif_id="boardroom_door",
            name="Glass Boardroom Door",
            description="Heavy frosted glass boardroom door closing",
            sfx_prompt="Heavy modern glass boardroom door closing softly with crisp latch click, no human voice",
            duration_seconds=2.0,
        )
    }
    return VoiceCastingRegistry(
        project_id="global_edge",
        project_title="Global Edge",
        language_code="zh-en",
        domain="business_english_drama",
        tts_model_id="fishaudio/drama-3",
        sfx_model_id="OpenMOSS-Team/MOSS-SoundEffect-v2.0",
        music_model_id="ACE-Step/acestep-v15-xl-turbo-diffusers",
        asr_model_id="faster-whisper-small-int8",
        roles=roles,
        sonic_motifs=motifs,
    )


def make_timeline_cue(**kwargs: Any):
    from aigc_audio_pipeline.models import TimelineCue

    fields_present = {f.name for f in dataclasses.fields(TimelineCue)}
    if "playback_rate" in kwargs and "playback_rate" not in fields_present:
        raise AssertionError("M1 schema gap: TimelineCue lacks playback_rate")
    if "subtitle_translation" in kwargs and "subtitle_translation" not in fields_present:
        raise AssertionError("M1 schema gap: TimelineCue lacks subtitle_translation")
    return TimelineCue(**kwargs)


def make_mini_cue_sheet(
    episode_id: str,
    *,
    cues: list[Any] | None = None,
    mode: str = "bilingual_business_drama",
    chapter_number: int = 1,
):
    """Build a lightweight 1-act, 1-cue synthetic cue sheet (~0.5-1.0s under --offline-dry-run)."""
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    acts = [
        ActMusicSpec(
            act_id="act_1",
            title="Act 1: Mini Dry-Run Probe",
            bgm_prompt="Minimalist tense cello pulse, strictly instrumental, no vocals",
        )
    ]
    if cues is None:
        cues = [
            make_timeline_cue(
                cue_id=f"{episode_id}_C001",
                act_id="act_1",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text="[measured] That is a phantom number.",
                subtitle_translation="这是虚构数字。",
                acoustic_space="boardroom",
                gap_after_s=0.30,
                playback_rate=1.0,
            )
        ]
    return EpisodeCueSheet(
        episode_id=episode_id,
        chapter_number=chapter_number,
        title=f"Global Edge {episode_id} Mini Studio Probe",
        mode=mode,
        head_pad_s=0.20,
        tail_pad_s=0.50,
        acts=acts,
        cues=cues,
    )


def build_mini_studio_dir(
    studio_dir: Path,
    *,
    cue_sheets: dict[str, Any] | None = None,
    audition_sheets: dict[str, Any] | None = None,
    voice_cast_manifest: dict[str, Any] | None = None,
    registry: Any | None = None,
) -> Path:
    """Create a self-contained isolated mini-studio directory for opaque-box M4 CLI testing."""
    for sub in ("auditions", "cue_sheets", "voice_anchors", "motifs", "bgm_cache"):
        (studio_dir / sub).mkdir(parents=True, exist_ok=True)
    reg = registry if registry is not None else make_minimal_registry()
    reg.save(studio_dir / "voice_casting_registry.json")

    chars: dict[str, Any] = {}
    for idx, rid in enumerate(reg.roles.keys()):
        wav_rel = f"voice_anchors/{rid}.wav"
        txt_rel = f"voice_anchors/{rid}.txt"
        write_sine_wav(
            studio_dir / wav_rel,
            duration_s=2.0,
            freq_hz=220.0 + idx * 25.0,
            sample_rate=44100,
            channels=1,
            amplitude=0.40,
        )
        anchor_text = "Clean studio anchor."
        (studio_dir / txt_rel).write_text(anchor_text + "\n", encoding="utf-8")
        chars[rid] = {
            "source_voice_name": "offline_synthetic_stub",
            "anchor_wav": wav_rel,
            "anchor_text": anchor_text,
        }

    manifest = (
        voice_cast_manifest
        if voice_cast_manifest is not None
        else {
            "anchor_schema_version": "v2_real_human_studio",
            "anchor_sample_rate_hz": 44100,
            "characters": chars,
        }
    )
    (studio_dir / "voice_cast_drama3.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    for fname, sheet in (cue_sheets or {}).items():
        sheet.save(studio_dir / "cue_sheets" / fname)
    for fname, sheet in (audition_sheets or {}).items():
        sheet.save(studio_dir / "auditions" / fname)
    return studio_dir


def verify_studio_08x_cache_reuse(
    studio_script: Path,
    tmp_dir: Path,
    *,
    self_contained: bool = False,
) -> dict[str, Any]:
    """Opaque-box behavioral proof that studio runner reuses a single 1.0x Drama 3 TTS cache
    stem across identical (role_id, language_code, text) cues at playback_rate=1.0 vs 0.8
    while applying real ~1.25x pitch-preserving atempo stretch on the 0.8x cue."""
    probe_root = tmp_dir / "cache_probe_08x"
    sdir = probe_root / "studio"
    out_dir = probe_root / "out"
    cache_dir = probe_root / "cache"
    shared_text = "[measured] That is a phantom number, not a cash loss."
    sheet = make_mini_cue_sheet(
        "E001_VA",
        cues=[
            make_timeline_cue(
                cue_id="C_NORM",
                act_id="act_1",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text=shared_text,
                subtitle_translation="那是虚构数字，不是现金亏损。",
                acoustic_space="studio_warm",
                gap_after_s=0.30,
                playback_rate=1.0,
            ),
            make_timeline_cue(
                cue_id="C_SLOW",
                act_id="act_1",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text=shared_text,
                subtitle_translation="那是虚构数字，不是现金亏损。",
                acoustic_space="studio_warm",
                gap_after_s=0.30,
                playback_rate=0.8,
            ),
        ],
    )
    build_mini_studio_dir(sdir, cue_sheets={"E001_VA_cache.json": sheet})
    args = [
        "--studio-dir", str(sdir),
        "--episodes", "E001_VA",
        "--output-dir", str(out_dir),
        "--cache-dir", str(cache_dir),
        "--offline-dry-run",
    ]
    if self_contained:
        proc = subprocess.run(
            [sys.executable, str(studio_script), *args],
            cwd=str(studio_script.parent),
            capture_output=True,
            text=True,
            timeout=180,
        )
    else:
        proc = run_python_script(studio_script, args, timeout=180)
    if proc.returncode != 0:
        raise AssertionError(
            f"Studio 0.8x cache-reuse probe failed (rc={proc.returncode}): "
            f"{proc.stderr[-800:]}\n{proc.stdout[-400:]}"
        )
    man_paths = sorted(out_dir.glob("E001_VA*_v001.json"))
    if not man_paths:
        raise AssertionError(f"0.8x cache-reuse probe produced no E001_VA*_v001.json in {out_dir}")
    man = load_json_file(man_paths[0])
    tl = {it["cue_id"]: it for it in man.get("timeline", []) if it.get("kind") == "dialogue"}
    if "C_NORM" not in tl or "C_SLOW" not in tl:
        raise AssertionError(f"Expected C_NORM and C_SLOW in timeline manifest, got {sorted(tl.keys())}")
    norm_it, slow_it = tl["C_NORM"], tl["C_SLOW"]
    if abs(float(norm_it.get("playback_rate", 1.0)) - 1.0) > 1e-3:
        raise AssertionError(f"C_NORM playback_rate={norm_it.get('playback_rate')}, expected 1.0")
    if abs(float(slow_it.get("playback_rate", 1.0)) - 0.8) > 1e-3:
        raise AssertionError(f"C_SLOW playback_rate={slow_it.get('playback_rate')}, expected 0.8")
    norm_stem = Path(str(norm_it.get("stem_file", ""))).resolve()
    slow_stem = Path(str(slow_it.get("stem_file", ""))).resolve()
    if not norm_stem.is_file() or not slow_stem.is_file():
        raise AssertionError(f"Cached stem_file missing on disk: norm={norm_stem}, slow={slow_stem}")
    if slow_stem != norm_stem:
        raise AssertionError(
            f"0.8x cue did NOT reuse 1.0x cached TTS stem (playback_rate leaked into cache key!): "
            f"C_NORM={norm_stem} vs C_SLOW={slow_stem}"
        )
    tts_cache_dir = cache_dir / "drama3_tts"
    if tts_cache_dir.is_dir():
        tts_wavs = list(tts_cache_dir.glob("*.wav"))
        if len(tts_wavs) != 1:
            raise AssertionError(
                f"Expected exactly 1 cached TTS WAV in {tts_cache_dir} for identical 1.0x/0.8x text, "
                f"found {len(tts_wavs)}: {[p.name for p in tts_wavs]}"
            )
    ratio = float(slow_it["duration_s"]) / max(float(norm_it["duration_s"]), 1e-6)
    if not (1.18 <= ratio <= 1.32):
        raise AssertionError(
            f"C_SLOW / C_NORM manifest duration ratio={ratio:.3f} outside [1.18, 1.32]"
        )
    return {"ratio": ratio, "stem_file": str(norm_stem)}


def make_synthetic_e001_variant(
    variant_id: str,
    *,
    or_form: bool = False,
    total_drama_cues: int = 36,
    debrief_slow_count: int = 4,
    debrief_native_count: int = 4,
    shadow_gap_s: float = 2.1,
    crosstalk_count: int | None = None,
    inner_monologue_count: int = 0,
    phone_call_count: int = 0,
    duck_count: int = 0,
    include_zhou_mo_debrief: bool = False,
    distinct_seed_word: str = "alpha",
):
    """Build a valid synthetic E001 variant hitting all runtime, phrase, accent & structural gates."""
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    if crosstalk_count is None:
        crosstalk_count = VARIANT_CROSSTALK_MIN.get(variant_id, 6)

    acts = [
        ActMusicSpec(act_id="act_1", title="Act 1: Sand Hill Ambush", bgm_prompt="Minimalist tense cello pulse, strictly instrumental, no vocals"),
        ActMusicSpec(act_id="act_2", title="Act 2: London Margin Squeeze", bgm_prompt="Restrained corporate thriller piano ostinato, purely instrumental, no singing"),
        ActMusicSpec(act_id="act_3", title="Act 3: Compute Bill Reckoning", bgm_prompt="Low dark synth bed, strictly instrumental, no vocals"),
        ActMusicSpec(act_id="act_4", title="Act 4: Counterstrike", bgm_prompt="Tight rhythmic strings, strictly instrumental, no vocals"),
        ActMusicSpec(act_id="act_5_debrief", title="Act 5: Black-Book Debrief", bgm_prompt="Warm restrained acoustic jazz-noir pulse, strictly instrumental, no vocals"),
    ]

    p2b = "income statement" if or_form else "flowed through into the income statement"
    p4a = "10x the throughput" if or_form else "10 times the throughput"

    phrase_lines = [
        ("victoria_vance", "en", "boardroom", f"[icy polite] Let us stop pretending that convertible note loss is merely a phantom number on your {distinct_seed_word} deck today."),
        ("lin_chen", "en", "boardroom", f"[measured] It is not a cash loss, Victoria; the mark-to-market adjustment simply {p2b} under accounting rules for NovaEdge."),
        ("alistair_finch", "en", "boardroom", f"[deadpan] Being capital-efficient in Shenzhen hardware does not protect our London flagship retail margin on {distinct_seed_word} units."),
        ("lin_chen", "en", "boardroom", f"[firmly] Our new inference pipeline delivers {p4a}. Pick your favorite number for the blended gross margin forecast across Europe."),
        ("victoria_vance", "en", "boardroom", f"[skeptical] In other words, you want Apex Horizon to fund the Series C bridge while your {distinct_seed_word} token bill spikes."),
        ("alistair_finch", "en", "boardroom", f"[blunt] Cloud inference costs are eating into budgets, and every buyer faces a really hard trade-off on {distinct_seed_word} shelf pricing."),
        ("lin_chen", "en", "boardroom", f"[confident] Ask yourself what is good enough for edge silicon when customers run this thing a million times every evening."),
        ("victoria_vance", "en", "boardroom", f"[guarded] You keep pitching the upside on NovaEdge Glass, Lin. When are you going to get it onto the cash ledger?"),
    ]

    cues: list[Any] = []
    cid_num = 1

    # Inject phrase lines (8 cues, ~48-55s)
    for role_id, lang, space, txt in phrase_lines:
        gap = -0.15 if crosstalk_count > 0 else 0.45
        if crosstalk_count > 0:
            crosstalk_count -= 1
        cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_C{cid_num:03d}",
                act_id="act_1" if cid_num <= 4 else "act_2",
                kind="dialogue",
                role_id=role_id,
                speaker_name=role_id,
                language_code=lang,
                text=txt,
                stability=0.5,
                acoustic_space=space,
                gap_after_s=gap,
                playback_rate=1.0,
                subtitle_translation="这是双语中文字幕对照翻译。",
            )
        )
        cid_num += 1

    # Add duck_under_next pairs if requested (E001_VD)
    for d in range(duck_count):
        cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_C{cid_num:03d}",
                act_id="act_2",
                kind="dialogue",
                role_id="alistair_finch",
                speaker_name="Alistair Finch",
                language_code="en",
                text=f"[measured] Our flagship buying committee expects disciplined unit economics and transparent {distinct_seed_word} {d} allocation across every quarter.",
                stability=0.5,
                acoustic_space="boardroom",
                duck_under_next=True,
                duck_lead_in_s=2.8,
                duck_gain=0.15,
                gap_after_s=0.35,
                playback_rate=1.0,
                subtitle_translation="伦敦采购委员会要求透明的季度单位经济模型。",
            )
        )
        cid_num += 1
        cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_C{cid_num:03d}",
                act_id="act_2",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="zh",
                text=f"[aside] 听懂他在压价了，他故意拿 {distinct_seed_word} 渠道返点试探我们的底线，我们必须稳住节奏。",
                stability=0.5,
                acoustic_space="studio_warm",
                gap_after_s=0.45,
                playback_rate=1.0,
            )
        )
        cid_num += 1

    # Add inner monologue cues if requested (E001_VB)
    for m in range(inner_monologue_count):
        cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_C{cid_num:03d}",
                act_id="act_3",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="zh",
                text=f"[aside] 表面上她在谈财务准则，实际上她盯紧的是深圳产线的 {distinct_seed_word} 现金流和话语权，第{m + 1}步不能退。",
                stability=0.5,
                acoustic_space="inner_monologue",
                gap_after_s=0.40,
                playback_rate=1.0,
            )
        )
        cid_num += 1

    # Add phone_call cues if requested (E001_VC)
    for p in range(phone_call_count):
        cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_C{cid_num:03d}",
                act_id="act_3",
                kind="dialogue",
                role_id="zhou_mo",
                speaker_name="Zhou Mo",
                language_code="zh-en",
                text=f"[tense] 深圳产线凌晨三点刚跑完 {distinct_seed_word} 固件压测，第{p + 1}组 NovaDock 本地推理延迟压到四十毫秒以内。",
                stability=0.5,
                acoustic_space="phone_call",
                gap_after_s=0.35,
                playback_rate=1.0,
            )
        )
        cid_num += 1

    # Fill remaining drama cues to target ~525s drama duration (well inside [480, 600]s)
    role_cycle = [
        ("victoria_vance", "en", "boardroom"),
        ("alistair_finch", "en", "boardroom"),
        ("lin_chen", "en", "boardroom"),
        ("zhou_mo", "zh", "dry"),
        ("lin_chen", "zh", "dry"),
    ]
    idx_fill = 0
    while estimate_cue_slice_duration_s(cues) < 515.0 and len(cues) < total_drama_cues + 40:
        r_id, lang, space = role_cycle[idx_fill % len(role_cycle)]
        gap = -0.14 if crosstalk_count > 0 else 0.45
        if crosstalk_count > 0:
            crosstalk_count -= 1
        if lang == "en":
            txt = (
                f"[measured] Under scenario {distinct_seed_word}{idx_fill}, NovaEdge Glass hardware margins "
                f"and European flagship distribution commitments require disciplined milestone verification "
                f"before the syndicate releases the next tranche of Series C capital."
            )
            sub_tr = f"在方案 {idx_fill} 下，硬件毛利与欧洲旗舰渠道条款必须在交割前锁定。"
        else:
            txt = (
                f"[firmly] 周默把深圳供应链第{idx_fill}轮物料报价和 {distinct_seed_word} 算力账单全部摊开，"
                f"我们今晚必须给出让伦敦与硅谷双方都挑不出毛病的硬数据，绝不能在估值条款上退让半寸。"
            )
            sub_tr = ""
        act_id = "act_3" if idx_fill % 2 == 0 else "act_4"
        cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_C{cid_num:03d}",
                act_id=act_id,
                kind="dialogue",
                role_id=r_id,
                speaker_name=r_id,
                language_code=lang,
                text=txt,
                stability=0.5,
                acoustic_space=space,
                gap_after_s=gap,
                playback_rate=1.0,
                subtitle_translation=sub_tr,
            )
        )
        cid_num += 1
        idx_fill += 1

    # Act 5 Debrief (~185s, well inside [165, 210]s)
    debrief_cues: list[Any] = []
    debrief_phrases = [
        "That is a phantom number, not a cash loss.",
        "In other words, it is eating into budgets and forcing a really hard trade-off.",
        "We stay capital-efficient and deliver ten times the throughput.",
        "Where is the upside, and when are you going to get it?",
    ]
    for s_i in range(debrief_slow_count):
        ph = debrief_phrases[s_i % len(debrief_phrases)]
        debrief_cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_D{s_i + 1:03d}",
                act_id="act_5_debrief",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text=f"[coach] {ph}",
                stability=0.5,
                acoustic_space="studio_warm",
                gap_after_s=0.60,
                playback_rate=0.8,
                subtitle_translation="慢速拆解：高管原话重音与节奏。",
            )
        )
    for n_i in range(debrief_native_count):
        ph = debrief_phrases[n_i % len(debrief_phrases)]
        debrief_cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_N{n_i + 1:03d}",
                act_id="act_5_debrief",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text=f"[measured] {ph}",
                stability=0.5,
                acoustic_space="studio_warm",
                gap_after_s=shadow_gap_s,
                playback_rate=1.0,
                subtitle_translation="原速跟读，停顿留白模仿高管语气。",
            )
        )
    ex_idx = 0
    while estimate_cue_slice_duration_s(debrief_cues) < 176.0:
        r_id = "zhou_mo" if (include_zhou_mo_debrief and ex_idx % 2 == 1) else "lin_chen"
        debrief_cues.append(
            make_timeline_cue(
                cue_id=f"{variant_id}_X{ex_idx + 1:03d}",
                act_id="act_5_debrief",
                kind="dialogue",
                role_id=r_id,
                speaker_name=r_id,
                language_code="zh-en",
                text=(
                    f"[coach] 第{ex_idx + 1}条拆局：中式直译常说 fake number，但华尔街高管用 phantom number "
                    f"和 not a cash loss 把估值波动与现金流彻底切割，既体面又有压迫感。"
                ),
                stability=0.5,
                acoustic_space="studio_warm",
                gap_after_s=0.50,
                playback_rate=1.0,
            )
        )
        ex_idx += 1

    cues.extend(debrief_cues)
    return EpisodeCueSheet(
        episode_id=variant_id,
        chapter_number=1,
        title=f"Global Edge {variant_id} Synthetic Control",
        mode="bilingual_business_drama",
        head_pad_s=0.30,
        tail_pad_s=1.20,
        acts=acts,
        cues=cues,
    )


def make_synthetic_corpus_100() -> dict[str, Any]:
    """Create a minimal compliant 100-clip corpus matching all oracle_corpus_100_etl_integrity rules."""
    clips: list[dict[str, Any]] = []
    # Distribute 1408 segments across 100 clips: 92 clips * 14 + 8 clips * 15 = 1288 + 120 = 1408
    all_ids = [cid for ids in CORPUS_IDS_BY_TOPIC.values() for cid in ids]
    for idx, cid in enumerate(all_ids):
        topic = CLIP_TOPIC_LOOKUP[cid]
        n_segs = 15 if idx < 8 else 14
        en_clean = (
            f"Executive discussion on {cid} covering Claude models, terms, and capital-efficient growth."
            if cid == "015_AI"
            else f"Executive briefing on {cid} covering unit economics, terms, and global strategy."
        )
        en_raw = en_clean
        if cid == "087_USC":
            en_raw = "[snorts] " + en_clean
        elif cid == "069_FIN":
            en_raw = "When you are in a hole, stop digging, the law of holds applies."
            en_clean = "When you are in a hole, stop digging, the law of holes applies."
        subs = [{"index": s + 1, "start_sec": s * 3.0, "end_sec": (s + 1) * 3.0, "en": en_clean, "zh": "商业分析"} for s in range(n_segs)]
        clips.append(
            {
                "clip_id": cid,
                "topic_key": topic,
                "topic_label": topic,
                "video_id": f"vid_{idx:03d}_{cid}",
                "video_title": f"Title for {cid}",
                "channel": f"Channel {topic}",
                "inferred_speakers": [f"Speaker {idx}"],
                "duration_sec": 50.0,
                "wpm": 170.2,
                "virality_score": 9.0,
                "hook_line_1": "Hook 1",
                "hook_line_2": "Hook 2",
                "en_title_hook": "Executive Clash",
                "summary_zh": "商业核心要点",
                "en_raw": en_raw,
                "en_clean": en_clean,
                "zh_full": "商业核心要点全文",
                "subtitles_clean": subs,
            }
        )
    corrections = [
        {"clip_id": cid, "raw": label, "clean": clean_hint, "reason": "ASR typo normalization"}
        for cid, label, _pat, _flags, clean_hint, _batch in RAW_CORPUS_ANOMALIES[:24]
    ]
    return {
        "schema_version": "1.0",
        "source_file": "/tmp/arsenal_100_queue.json",
        "total_clips": 100,
        "topic_counts": {"AI": 25, "BUSINESS": 25, "FINANCE": 25, "US_CHINA": 25},
        "summary_metrics": {
            "total_segments": 1408,
            "median_wpm": 170.20,
            "mean_wpm": 173.86,
            "total_en_words": 14420,
            "total_zh_chars": 27095,
            "total_duration_sec": 4976.89,
        },
        "asr_corrections_applied": corrections,
        "clips": clips,
    }


def make_synthetic_lexicon(corpus_data: dict[str, Any], corpus_count: int = 70, total: int = 100) -> list[dict[str, Any]]:
    clips = corpus_data["clips"]
    out: list[dict[str, Any]] = []
    for i in range(total):
        if i < corpus_count:
            c = clips[i % len(clips)]
            if c["clip_id"] == "015_AI":
                phrase = "capital-efficient"
            elif c["clip_id"] == "069_FIN":
                phrase = "law of holes"
            else:
                phrase = "unit economics"
            out.append(
                {
                    "phrase_id": f"LEX_{i + 1:03d}",
                    "phrase_en": phrase,
                    "category": "finance_hedging",
                    "cefr_level": "C1",
                    "chinglish_trap": "single product money",
                    "executive_subtext_zh": "单位经济模型拆解",
                    "verbatim_context_en": c["en_clean"],
                    "source_type": "corpus",
                    "clip_ids": [c["clip_id"]],
                }
            )
        else:
            out.append(
                {
                    "phrase_id": f"LEX_{i + 1:03d}",
                    "phrase_en": f"slotting fee clause {i}",
                    "category": "retail_channel",
                    "cefr_level": "B2-C1",
                    "chinglish_trap": "shelf money",
                    "executive_subtext_zh": "渠道进场费条款",
                    "verbatim_context_en": "Selfridges demanded a slotting fee waiver.",
                    "source_type": "world_bridge",
                    "clip_ids": [],
                }
            )
    return out


def make_synthetic_season1_map(
    mean_us_uk_pct: float = 85.0,
    *,
    e001_pct: float = 100.0,
) -> dict[str, Any]:
    remaining = [
        cid for cid in sorted(EXPECTED_100_CLIP_IDS) if cid not in E001_SEED_CLIP_IDS
    ]
    # 20 episodes * 4 + 4 episodes * 5 = 100 (E001, E007, E013, E019 get 5 clips)
    five_eps = {1, 7, 13, 19}
    other_pct = (24.0 * mean_us_uk_pct - e001_pct) / 23.0
    episodes: list[dict[str, Any]] = []
    cursor = 0
    for ep_num in range(1, 25):
        arc = ((ep_num - 1) // 6) + 1
        if ep_num == 1:
            cids = sorted(E001_SEED_CLIP_IDS)
            ep_pct = e001_pct
        else:
            take = 5 if ep_num in five_eps else 4
            cids = remaining[cursor : cursor + take]
            cursor += take
            ep_pct = other_pct
        episodes.append(
            {
                "episode_id": f"E{ep_num:03d}",
                "arc_number": arc,
                "arc_title": f"Arc {arc}",
                "title_zh": f"第{ep_num}集商战",
                "title_en": f"Episode {ep_num} Edge",
                "logline_zh": f"第{ep_num}集剧情梗概：出海硬件生死局。",
                "primary_clip_ids": cids,
                "accent_profile": "US + London RP" if ep_num not in (11, 13, 16) else "US + UK + Intl Guest",
                "core_us_uk_en_pct": ep_pct,
                "target_phrases": [f"phrase_{ep_num}_{k}" for k in range(1, 7)],
                "viral_45s_hook": f"E{ep_num:03d} 45s boardroom confrontation hook",
                "cliffhanger_zh": f"第{ep_num}集结尾反转钩子。",
            }
        )
    return {"season": 1, "episodes": episodes}


# ---------------------------------------------------------------------------
# 18-Family Positive + Negative Synthetic Mutation Self-Test Harness
# ---------------------------------------------------------------------------

def _assert_mutant_fails(fn: Callable[[], Any], label: str) -> None:
    try:
        fn()
    except AssertionError:
        return
    raise AssertionError(
        f"SELF-TEST MUTATION ESCAPED (oracle failed to catch mutant): {label}"
    )


def run_self_test_suite() -> list[dict[str, Any]]:
    """Run all 18 positive + negative mutation families strictly inside mktemp -d."""
    from aigc_audio_pipeline.models import EpisodeCueSheet

    tmp_root = Path(tempfile.mkdtemp(prefix="global_edge_e2e_selftest_"))
    results: list[dict[str, Any]] = []

    try:
        def _record(num: int, name: str, fn: Callable[[], tuple[int, int]]) -> None:
            try:
                pos_n, mut_n = fn()
                results.append(
                    {
                        "family": num,
                        "name": name,
                        "status": "PASS",
                        "positives_passed": pos_n,
                        "mutants_caught": mut_n,
                        "message": "",
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "family": num,
                        "name": name,
                        "status": "FAIL",
                        "positives_passed": 0,
                        "mutants_caught": 0,
                        "message": f"{type(exc).__name__}: {exc}",
                    }
                )

        # 1. oracle_standalone_ip_and_banned_cliches
        def _f01() -> tuple[int, int]:
            clean = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f1")
            oracle_standalone_ip_and_banned_cliches(clean)
            # Specificity control: negative guardrail inside director_note MUST PASS
            clean_note = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f1note")
            clean_note.cues[0].director_note = "Do NOT sound like a YouTube host or 各位听众."
            oracle_standalone_ip_and_banned_cliches(clean_note)

            mutants_caught = 0
            for bad in ("视频号", "YouTube", "欢迎收听今天的英语课", "各位听众"):
                m_sheet = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f1")
                m_sheet.cues[0].text = f"[measured] Check {bad} right now."
                _assert_mutant_fails(
                    lambda s=m_sheet: oracle_standalone_ip_and_banned_cliches(s),
                    f"F1 inject {bad!r}",
                )
                mutants_caught += 1
            # B3b anti-spoofing mutants
            m_sub = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f1sub")
            m_sub.cues[0].subtitle_translation = "欢迎来到视频号，各位听众看YouTube。"
            _assert_mutant_fails(
                lambda: oracle_standalone_ip_and_banned_cliches(m_sub),
                "F1 banned term in subtitle_translation",
            )
            mutants_caught += 1

            m_tag = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f1tag")
            m_tag.cues[0].text = "[youtube] Clean spoken line."
            _assert_mutant_fails(
                lambda: oracle_standalone_ip_and_banned_cliches(m_tag),
                "F1 banned lowercase inline tag [youtube]",
            )
            mutants_caught += 1

            m_title = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f1title")
            m_title.title = "Global Edge 视频号特辑"
            _assert_mutant_fails(
                lambda: oracle_standalone_ip_and_banned_cliches(m_title),
                "F1 banned term in cue_sheet.title",
            )
            mutants_caught += 1

            m_act = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f1act")
            m_act.acts[0].title = "Act 1: YouTube Breakdown"
            _assert_mutant_fails(
                lambda: oracle_standalone_ip_and_banned_cliches(m_act),
                "F1 banned term in act.title",
            )
            mutants_caught += 1
            return 2, mutants_caught

        _record(1, "oracle_standalone_ip_and_banned_cliches", _f01)

        # 2. oracle_e001_8_mandatory_phrases
        def _f02() -> tuple[int, int]:
            canon = make_synthetic_e001_variant("E001_VA", or_form=False, distinct_seed_word="f2a")
            alt = make_synthetic_e001_variant("E001_VA", or_form=True, distinct_seed_word="f2b")
            oracle_e001_8_mandatory_phrases(canon)
            oracle_e001_8_mandatory_phrases(alt)
            mutants_caught = 0
            for idx in range(8):
                m_sheet = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f2m")
                m_sheet.cues[idx].text = "[measured] Generic corporate line replacing target idiom."
                _assert_mutant_fails(
                    lambda s=m_sheet: oracle_e001_8_mandatory_phrases(s),
                    f"F2 drop P{idx + 1}",
                )
                mutants_caught += 1
            # B3a mutant 1: cross-cue stitching ("...phantom" + "number...")
            m_stitch = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f2st")
            m_stitch.cues[0].text = "[icy polite] That deck is a total phantom"
            m_stitch.cues[1].text = "[measured] number one priority: it is not a cash loss; it flowed through into the income statement."
            _assert_mutant_fails(
                lambda: oracle_e001_8_mandatory_phrases(m_stitch),
                "F2 cross-cue stitching phantom + number",
            )
            mutants_caught += 1
            # B3a mutant 2: substring spoof ("upsidedown" replacing "upside")
            m_sub = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f2sub")
            m_sub.cues[7].text = "[guarded] The ledger flipped upsidedown, Lin. When are you going to get it?"
            _assert_mutant_fails(
                lambda: oracle_e001_8_mandatory_phrases(m_sub),
                "F2 substring spoof upsidedown",
            )
            mutants_caught += 1
            # B3a mutant 3: drama_only=True with <4 acts
            m_few = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f2few")
            m_few.acts = m_few.acts[:2]
            _assert_mutant_fails(
                lambda: oracle_e001_8_mandatory_phrases(m_few, drama_only=True),
                "F2 drama_only=True with <4 acts",
            )
            mutants_caught += 1
            # B3a mutant 4: P1 present ONLY in Act 5 Debrief (dropped from drama)
            m_deb_only = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f2deb")
            m_deb_only.cues[0].text = "[icy polite] Let us review your convertible note valuation."
            _assert_mutant_fails(
                lambda: oracle_e001_8_mandatory_phrases(m_deb_only, drama_only=True),
                "F2 P1 only in Act 5 Debrief",
            )
            mutants_caught += 1
            return 2, mutants_caught

        _record(2, "oracle_e001_8_mandatory_phrases", _f02)

        # 3. oracle_corpus_100_etl_integrity
        def _f03() -> tuple[int, int]:
            good = make_synthetic_corpus_100()
            oracle_corpus_100_etl_integrity(good)
            # Mutant 1: 99 clips
            m1 = json.loads(json.dumps(good))
            m1["clips"].pop()
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m1), "F3 99 clips")
            # Mutant 2: 030_AI overwritten by 030_BIZ video_id
            m2 = json.loads(json.dumps(good))
            c_map = {c["clip_id"]: c for c in m2["clips"]}
            c_map["030_AI"]["video_id"] = c_map["030_BIZ"]["video_id"]
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m2), "F3 030 collision")
            # Mutant 3: [snorts] in 087_USC.en_clean
            m3 = json.loads(json.dumps(good))
            for c in m3["clips"]:
                if c["clip_id"] == "087_USC":
                    c["en_clean"] = "[snorts] " + c["en_clean"]
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m3), "F3 [snorts] left")
            # Mutant 4: law of holds in 069_FIN.en_clean
            m4 = json.loads(json.dumps(good))
            for c in m4["clips"]:
                if c["clip_id"] == "069_FIN":
                    c["en_clean"] = "This is the law of holds."
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m4), "F3 law of holds")
            # Mutant 5: \bClaud\b in 015_AI.en_clean (while positive above verified "Claude" passes!)
            m5 = json.loads(json.dumps(good))
            for c in m5["clips"]:
                if c["clip_id"] == "015_AI":
                    c["en_clean"] = "We tested Claud and Claude together."
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m5), "F3 \\bClaud\\b typo")
            # Mutant 6: case-sensitive \bMs\b in 031_BIZ (while "terms" in positive passes!)
            m6 = json.loads(json.dumps(good))
            for c in m6["clips"]:
                if c["clip_id"] == "031_BIZ":
                    c["en_clean"] = "We placed Ms on the boardroom floor."
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m6), "F3 \\bMs\\b typo")
            # B3d Mutant 7: lying topic_counts (030_BIZ mutated to AI while top-level untouched)
            m7 = json.loads(json.dumps(good))
            for c in m7["clips"]:
                if c["clip_id"] == "030_BIZ":
                    c["topic_key"] = "AI"
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m7), "F3 lying topic_counts")
            # B3d Mutant 8: lying total_segments (1 clip subtitles_clean=[] while summary_metrics=1408)
            m8 = json.loads(json.dumps(good))
            m8["clips"][0]["subtitles_clean"] = []
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m8), "F3 lying total_segments")
            # B3d Mutant 9: lying median_wpm (all clips wpm=220.0 while summary_metrics.median_wpm=170.20)
            m9 = json.loads(json.dumps(good))
            for c in m9["clips"]:
                c["wpm"] = 220.0
            _assert_mutant_fails(lambda: oracle_corpus_100_etl_integrity(m9), "F3 lying median_wpm")
            return 1, 9

        _record(3, "oracle_corpus_100_etl_integrity", _f03)

        # 4. oracle_lexicon_provenance_70_30
        def _f04() -> tuple[int, int]:
            corp = make_synthetic_corpus_100()
            lex_ok = make_synthetic_lexicon(corp, corpus_count=70, total=100)
            oracle_lexicon_provenance_70_30(lex_ok, corp)
            # Mutant 1: 69% corpus
            lex_69 = make_synthetic_lexicon(corp, corpus_count=69, total=100)
            _assert_mutant_fails(lambda: oracle_lexicon_provenance_70_30(lex_69, corp), "F4 69% corpus")
            # Mutant 2: fabricated clip_id 028_AI
            lex_bad_id = json.loads(json.dumps(lex_ok))
            lex_bad_id[0]["clip_ids"] = ["028_AI"]
            _assert_mutant_fails(lambda: oracle_lexicon_provenance_70_30(lex_bad_id, corp), "F4 fake 028_AI")
            # Mutant 3: phrase absent from cited clip's en_clean
            lex_absent = json.loads(json.dumps(lex_ok))
            lex_absent[0]["phrase_en"] = "nonexistent phantom unicorn phrase"
            _assert_mutant_fails(lambda: oracle_lexicon_provenance_70_30(lex_absent, corp), "F4 ungrounded phrase")
            # Mutant 4: 99 total phrases
            lex_99 = lex_ok[:99]
            _assert_mutant_fails(lambda: oracle_lexicon_provenance_70_30(lex_99, corp), "F4 99 phrases")
            # B3e Mutant 5: slash-split stopword bypass ("in / fabricated unicorn jargon")
            lex_slash = json.loads(json.dumps(lex_ok))
            lex_slash[0]["phrase_en"] = "in / fabricated unicorn jargon"
            _assert_mutant_fails(lambda: oracle_lexicon_provenance_70_30(lex_slash, corp), "F4 slash stopword bypass")
            # B3e Mutant 6: substring word-boundary bypass ("nomic" inside "economics")
            lex_sub = json.loads(json.dumps(lex_ok))
            lex_sub[0]["phrase_en"] = "nomic"
            _assert_mutant_fails(lambda: oracle_lexicon_provenance_70_30(lex_sub, corp), "F4 substring nomic bypass")
            # B3e Mutant 7: verbatim_context_en omits matched phrase
            lex_verb = json.loads(json.dumps(lex_ok))
            lex_verb[0]["verbatim_context_en"] = "Completely unrelated context sentence."
            _assert_mutant_fails(lambda: oracle_lexicon_provenance_70_30(lex_verb, corp), "F4 verbatim_context mismatch")
            # D5 Mutant 8: 4-char stopword slash spoof ("that / totally fabricated bogus jargon")
            corp_that = json.loads(json.dumps(corp))
            corp_that["clips"][0]["en_clean"] = "Executive briefing confirming that unit economics matter globally."
            lex_stop4 = json.loads(json.dumps(lex_ok))
            lex_stop4[0]["phrase_en"] = "that / totally fabricated bogus jargon"
            lex_stop4[0]["verbatim_context_en"] = corp_that["clips"][0]["en_clean"]
            _assert_mutant_fails(
                lambda: oracle_lexicon_provenance_70_30(lex_stop4, corp_that),
                "F4 4-char stopword slash spoof",
            )
            # D5 Mutant 9: extra unrelated valid clip_id appended to corpus entry
            lex_extra_cid = json.loads(json.dumps(lex_ok))
            lex_extra_cid[0]["clip_ids"] = [lex_extra_cid[0]["clip_ids"][0], "015_AI"]
            _assert_mutant_fails(
                lambda: oracle_lexicon_provenance_70_30(lex_extra_cid, corp),
                "F4 extra unrelated clip_id on corpus entry",
            )
            # D5 Mutant 10: world_bridge entry carrying non-empty clip_ids
            lex_wb_cid = json.loads(json.dumps(lex_ok))
            lex_wb_cid[-1]["clip_ids"] = ["02_BIZ_Anthropic"]
            _assert_mutant_fails(
                lambda: oracle_lexicon_provenance_70_30(lex_wb_cid, corp),
                "F4 world_bridge with non-empty clip_ids",
            )
            return 1, 10

        _record(4, "oracle_lexicon_provenance_70_30", _f04)

        # 5. oracle_season1_24ep_bijection
        def _f05() -> tuple[int, int]:
            smap = make_synthetic_season1_map(85.0)
            oracle_season1_24ep_bijection(smap)
            # Positive 2 (D2): structured-dict viral_45s_hook & target_phrases schema MUST PASS
            smap_struct = json.loads(json.dumps(smap))
            for ep in smap_struct["episodes"]:
                ep["viral_45s_hook"] = {
                    "conflict_angle": "GAAP loss vs zero cash outflow",
                    "hook_line_en": "That is a phantom number, not a cash loss.",
                }
                ep["target_phrases"] = [{"phrase_en": f"exec_phrase_{k}"} for k in range(1, 7)]
            oracle_season1_24ep_bijection(smap_struct)
            # Mutant 1: 23 episodes
            m1 = json.loads(json.dumps(smap))
            m1["episodes"].pop()
            _assert_mutant_fails(lambda: oracle_season1_24ep_bijection(m1), "F5 23 episodes")
            # Mutant 2: duplicate 012_AI
            m2 = json.loads(json.dumps(smap))
            m2["episodes"][4]["primary_clip_ids"][0] = "012_AI"
            _assert_mutant_fails(lambda: oracle_season1_24ep_bijection(m2), "F5 duplicate 012_AI")
            # Mutant 3: missing clip (drop 1 from E007)
            m3 = json.loads(json.dumps(smap))
            m3["episodes"][6]["primary_clip_ids"].pop()
            _assert_mutant_fails(lambda: oracle_season1_24ep_bijection(m3), "F5 missing 1 clip")
            # Mutant 4: extra fake clip 028_AI
            m4 = json.loads(json.dumps(smap))
            m4["episodes"][1]["primary_clip_ids"][0] = "028_AI"
            _assert_mutant_fails(lambda: oracle_season1_24ep_bijection(m4), "F5 fake 028_AI")
            # Mutant 5: wrong E001 seed set
            m5 = json.loads(json.dumps(smap))
            m5["episodes"][0]["primary_clip_ids"][0], m5["episodes"][1]["primary_clip_ids"][0] = (
                m5["episodes"][1]["primary_clip_ids"][0],
                m5["episodes"][0]["primary_clip_ids"][0],
            )
            _assert_mutant_fails(lambda: oracle_season1_24ep_bijection(m5), "F5 wrong E001 seeds")
            # D2 Mutants 6-14: None / {} / blank dict fields / non-str primitives
            d2_mutants: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
                ("target_phrases_empty_dict", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, {})),
                ("target_phrases_blank_dict", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, {"phrase_en": "   "})),
                ("target_phrases_none_elem", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, None)),
                ("target_phrases_int_elem", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, 123)),
                ("viral_45s_hook_empty_dict", lambda d: d["episodes"][0].__setitem__("viral_45s_hook", {})),
                ("viral_45s_hook_blank_dict", lambda d: d["episodes"][0].__setitem__("viral_45s_hook", {"conflict_angle": "", "hook_line_en": ""})),
                ("viral_45s_hook_none", lambda d: d["episodes"][0].__setitem__("viral_45s_hook", None)),
                ("title_zh_none", lambda d: d["episodes"][0].__setitem__("title_zh", None)),
                ("cliffhanger_zh_none", lambda d: d["episodes"][0].__setitem__("cliffhanger_zh", None)),
            ]
            for lbl, mutator in d2_mutants:
                md = json.loads(json.dumps(smap))
                mutator(md)
                _assert_mutant_fails(lambda x=md: oracle_season1_24ep_bijection(x), f"F5 {lbl}")
            return 2, 5 + len(d2_mutants)

        _record(5, "oracle_season1_24ep_bijection", _f05)

        # 6. oracle_accent_matrix_budget
        def _f06() -> tuple[int, int]:
            reg = make_minimal_registry()
            smap_ok = make_synthetic_season1_map(85.0)
            e001_ok = {"E001_VA": make_synthetic_e001_variant("E001_VA", distinct_seed_word="f6")}
            oracle_accent_matrix_budget(reg, smap_ok, e001_ok)
            # Mutant 1: 84.9% season
            smap_low = make_synthetic_season1_map(84.9)
            _assert_mutant_fails(lambda: oracle_accent_matrix_budget(reg, smap_low, e001_ok), "F6 84.9% season")
            # Mutant 2: rajiv_menon injected in E001
            e001_guest = {"E001_VA": make_synthetic_e001_variant("E001_VA", distinct_seed_word="f6g")}
            e001_guest["E001_VA"].cues[0].role_id = "rajiv_menon"
            _assert_mutant_fails(lambda: oracle_accent_matrix_budget(reg, smap_ok, e001_guest), "F6 guest in E001")
            # Mutant 3: missing accent_code on core role
            reg_bad = make_minimal_registry()
            reg_bad.roles["lin_chen"].accent_code = ""
            _assert_mutant_fails(lambda: oracle_accent_matrix_budget(reg_bad, smap_ok), "F6 empty accent_code")
            # B3c Mutant 4: inflated E001=300.0 + E002..E024=76.0 (fake mean 85.33%)
            smap_300 = json.loads(json.dumps(smap_ok))
            smap_300["episodes"][0]["core_us_uk_en_pct"] = 300.0
            for ep in smap_300["episodes"][1:]:
                ep["core_us_uk_en_pct"] = 76.0
            _assert_mutant_fails(lambda: oracle_accent_matrix_budget(reg, smap_300), "F6 inflated 300% pct")
            # B3c Mutant 5: negative E002=-5.0
            smap_neg = json.loads(json.dumps(smap_ok))
            smap_neg["episodes"][1]["core_us_uk_en_pct"] = -5.0
            _assert_mutant_fails(lambda: oracle_accent_matrix_budget(reg, smap_neg), "F6 negative -5% pct")
            # B3c Mutant 6: E001 < 100% despite season mean 90%
            smap_e001_90 = make_synthetic_season1_map(90.0, e001_pct=90.0)
            _assert_mutant_fails(lambda: oracle_accent_matrix_budget(reg, smap_e001_90), "F6 E001=90% < 100%")
            # D7.4 Mutant 7: unregistered role_id with empty language_code
            e001_unreg_empty = {"E001_VA": make_synthetic_e001_variant("E001_VA", distinct_seed_word="f6u1")}
            e001_unreg_empty["E001_VA"].cues[0].role_id = "unregistered_accent_guest"
            e001_unreg_empty["E001_VA"].cues[0].language_code = ""
            _assert_mutant_fails(
                lambda: oracle_accent_matrix_budget(reg, smap_ok, e001_unreg_empty),
                "F6 unregistered role with empty lang",
            )
            # D7.4 Mutant 8: unregistered role_id with zh-en language_code
            e001_unreg_zhen = {"E001_VA": make_synthetic_e001_variant("E001_VA", distinct_seed_word="f6u2")}
            e001_unreg_zhen["E001_VA"].cues[0].role_id = "unregistered_accent_guest"
            e001_unreg_zhen["E001_VA"].cues[0].language_code = "zh-en"
            _assert_mutant_fails(
                lambda: oracle_accent_matrix_budget(reg, smap_ok, e001_unreg_zhen),
                "F6 unregistered role with zh-en",
            )
            # D7.4 Mutant 9: registered non-US/UK role whose cue inherits language_code='en' from registry
            from aigc_audio_pipeline.models import VoiceProfile
            reg_ext = make_minimal_registry()
            reg_ext.roles["custom_non_uk_us"] = VoiceProfile(
                role_id="custom_non_uk_us",
                display_name="Custom Non-Core",
                tier="recurring",
                gender="male",
                language_code="en",
                accent_code="zh_mainland_sz",
                voice_id="v_custom",
            )
            e001_inh = {"E001_VA": make_synthetic_e001_variant("E001_VA", distinct_seed_word="f6u3")}
            e001_inh["E001_VA"].cues[0].role_id = "custom_non_uk_us"
            e001_inh["E001_VA"].cues[0].language_code = ""
            _assert_mutant_fails(
                lambda: oracle_accent_matrix_budget(reg_ext, smap_ok, e001_inh),
                "F6 inherited en language on non-US/UK accent role",
            )
            return 1, 9

        _record(6, "oracle_accent_matrix_budget", _f06)

        # 7. oracle_runtime_and_debrief_windows
        def _f07() -> tuple[int, int]:
            ok = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f7")
            oracle_runtime_and_debrief_windows(ok)
            # Mutant 1: total < 600s
            m1 = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f7m1")
            m1.cues = m1.cues[:12] + [c for c in m1.cues if c.act_id == "act_5_debrief"]
            _assert_mutant_fails(lambda: oracle_runtime_and_debrief_windows(m1), "F7 total < 600s")
            # Mutant 2: total > 840s
            m2 = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f7m2")
            for k in range(30):
                m2.cues.insert(
                    2,
                    make_timeline_cue(
                        cue_id=f"EXTRA_{k}",
                        act_id="act_1",
                        kind="dialogue",
                        role_id="lin_chen",
                        language_code="en",
                        text="[measured] " + " ".join(["margin"] * 25),
                        gap_after_s=2.0,
                    ),
                )
            _assert_mutant_fails(lambda: oracle_runtime_and_debrief_windows(m2), "F7 total > 840s")
            # Mutant 3: debrief < 165s
            m3 = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f7m3")
            m3.cues = [c for c in m3.cues if c.act_id != "act_5_debrief"] + [
                c for c in m3.cues if c.act_id == "act_5_debrief"
            ][:8]
            _assert_mutant_fails(lambda: oracle_runtime_and_debrief_windows(m3), "F7 debrief < 165s")
            # Mutant 4: debrief > 210s
            m4 = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f7m4")
            for k in range(8):
                m4.cues.append(
                    make_timeline_cue(
                        cue_id=f"DEBRIEF_LONG_{k}",
                        act_id="act_5_debrief",
                        kind="dialogue",
                        role_id="lin_chen",
                        language_code="zh",
                        text="[coach] " + "高管黑话拆局深度剖析" * 6,
                        gap_after_s=1.0,
                    )
                )
            _assert_mutant_fails(lambda: oracle_runtime_and_debrief_windows(m4), "F7 debrief > 210s")
            # Mutant 5: zero playback_rate=0.8 cues
            m5 = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f7m5")
            for c in m5.cues:
                c.playback_rate = 1.0
            _assert_mutant_fails(lambda: oracle_runtime_and_debrief_windows(m5), "F7 zero 0.8x cues")
            # Mutant 6: max shadow gap 1.75s
            m6 = make_synthetic_e001_variant("E001_VA", shadow_gap_s=1.75, distinct_seed_word="f7m6")
            _assert_mutant_fails(lambda: oracle_runtime_and_debrief_windows(m6), "F7 shadow gap 1.75s")
            # D7.2 Mutant 7: gap>=1.8s placed ONLY on 0.8x slow cues while all 1.0x native cues have gap=0.25s
            m7 = make_synthetic_e001_variant("E001_VA", shadow_gap_s=0.25, distinct_seed_word="f7m7")
            for c in m7.cues:
                if c.act_id == "act_5_debrief" and c.kind == "dialogue" and abs(float(c.playback_rate) - 0.8) < 1e-3:
                    c.gap_after_s = 2.1
            _assert_mutant_fails(
                lambda: oracle_runtime_and_debrief_windows(m7),
                "F7 Act 5 gap>=1.8s decoupled onto 0.8x cues only",
            )
            return 1, 7

        _record(7, "oracle_runtime_and_debrief_windows", _f07)

        # 8. oracle_variant_differentiation_and_crosstalk
        def _f08() -> tuple[int, int]:
            def _make_set() -> dict[str, Any]:
                return {
                    "E001_VA": make_synthetic_e001_variant("E001_VA", crosstalk_count=6, inner_monologue_count=0, distinct_seed_word="crimson_duel"),
                    "E001_VB": make_synthetic_e001_variant("E001_VB", crosstalk_count=4, inner_monologue_count=4, include_zhou_mo_debrief=True, distinct_seed_word="cobalt_sniper"),
                    "E001_VC": make_synthetic_e001_variant("E001_VC", crosstalk_count=6, phone_call_count=3, distinct_seed_word="amber_timezone"),
                    "E001_VD": make_synthetic_e001_variant("E001_VD", crosstalk_count=3, duck_count=2, distinct_seed_word="emerald_memoir"),
                }

            good = _make_set()
            # Ensure strong lexical diversity in synthetic control
            for vid, tok_list in {
                "E001_VA": ["tranche", "covenant", "syndicate", "dilution", "liquidation", "boardwalk", "harbor", "ledger"],
                "E001_VB": ["chessboard", "freeze", "subtext", "deception", "whisper", "taxi", "midnight", "leverage"],
                "E001_VC": ["firmware", "latency", "factory", "shipment", "customs", "silicon", "prototype", "deadline"],
                "E001_VD": ["archive", "chronicle", "translator", "headline", "memoir", "podcast", "retrospective", "dispatch"],
            }.items():
                for i, c in enumerate(good[vid].cues[8:]):
                    if c.language_code == "en":
                        c.text = f"[measured] {' '.join(f'{w}{i}' for w in tok_list)} {vid.lower()}."
            oracle_variant_differentiation_and_crosstalk(good)
            # Reconciled positive control: VA=1 inner_monologue, VB=4 (VB >= 4 and VB > VA) MUST PASS
            good_va1 = dict(good)
            va1_sheet = make_synthetic_e001_variant("E001_VA", crosstalk_count=6, inner_monologue_count=1, distinct_seed_word="crimson_duel")
            for i, c in enumerate(va1_sheet.cues[8:]):
                if c.language_code == "en":
                    c.text = f"[measured] {' '.join(f'{w}{i}' for w in ['tranche', 'covenant', 'syndicate', 'dilution', 'liquidation', 'boardwalk', 'harbor', 'ledger'])} e001_va."
            good_va1["E001_VA"] = va1_sheet
            oracle_variant_differentiation_and_crosstalk(good_va1)

            # Mutant 1: VA with 5 crosstalk
            m1 = _make_set()
            for vid in m1:
                m1[vid] = good[vid]
            m1_va = make_synthetic_e001_variant("E001_VA", crosstalk_count=5, distinct_seed_word="crimson_duel")
            m1["E001_VA"] = m1_va
            _assert_mutant_fails(lambda: oracle_variant_differentiation_and_crosstalk(m1), "F8 VA crosstalk=5")
            # Mutant 2: VD with 1 duck_under_next
            m2 = dict(good)
            m2["E001_VD"] = make_synthetic_e001_variant("E001_VD", crosstalk_count=3, duck_count=1, distinct_seed_word="emerald_memoir")
            _assert_mutant_fails(lambda: oracle_variant_differentiation_and_crosstalk(m2), "F8 VD duck=1")
            # Mutant 3: VA & VB near-identical
            m3 = dict(good)
            m3["E001_VB"] = make_synthetic_e001_variant("E001_VB", crosstalk_count=6, inner_monologue_count=4, include_zhou_mo_debrief=True, distinct_seed_word="same_seed")
            m3["E001_VA"] = make_synthetic_e001_variant("E001_VA", crosstalk_count=6, inner_monologue_count=0, distinct_seed_word="same_seed")
            _assert_mutant_fails(lambda: oracle_variant_differentiation_and_crosstalk(m3), "F8 VA/VB Jaccard>=0.70")
            # Mutant 4: VA missing UK RP turns
            m4 = dict(good)
            va_no_uk = make_synthetic_e001_variant("E001_VA", crosstalk_count=6, distinct_seed_word="no_uk")
            for c in va_no_uk.cues:
                if c.role_id == "alistair_finch":
                    c.role_id = "victoria_vance"
            m4["E001_VA"] = va_no_uk
            _assert_mutant_fails(lambda: oracle_variant_differentiation_and_crosstalk(m4), "F8 VA 0 UK RP")
            # Mutant 5: VA=4 == VB=4 (VB must strictly exceed VA)
            m5 = dict(good)
            va4 = make_synthetic_e001_variant("E001_VA", crosstalk_count=6, inner_monologue_count=4, distinct_seed_word="crimson_duel")
            for i, c in enumerate(va4.cues[8:]):
                if c.language_code == "en":
                    c.text = f"[measured] {' '.join(f'{w}{i}' for w in ['tranche', 'covenant', 'syndicate', 'dilution', 'liquidation', 'boardwalk', 'harbor', 'ledger'])} e001_va."
            m5["E001_VA"] = va4
            _assert_mutant_fails(lambda: oracle_variant_differentiation_and_crosstalk(m5), "F8 VA=4 == VB=4 inner_monologue")
            # D7.1 Mutant 6: same-speaker negative gaps cannot satisfy crosstalk floor
            m6 = dict(good)
            va_self = make_synthetic_e001_variant("E001_VA", crosstalk_count=0, distinct_seed_word="crimson_duel")
            for i, c in enumerate(va_self.cues[8:]):
                if c.language_code == "en":
                    c.text = f"[measured] {' '.join(f'{w}{i}' for w in ['tranche', 'covenant', 'syndicate', 'dilution', 'liquidation', 'boardwalk', 'harbor', 'ledger'])} e001_va."
            # Insert 8 consecutive same-speaker negative-gap cues (0 cross-speaker crosstalk)
            same_spk = [
                make_timeline_cue(
                    cue_id=f"SELF_CT_{k}",
                    act_id="act_1",
                    kind="dialogue",
                    role_id="lin_chen",
                    language_code="en",
                    text=f"[measured] Self-overlap monologue line {k}.",
                    gap_after_s=-0.15 if k < 8 else 0.4,
                )
                for k in range(9)
            ]
            va_self.cues[8:8] = same_spk
            m6["E001_VA"] = va_self
            _assert_mutant_fails(
                lambda: oracle_variant_differentiation_and_crosstalk(m6),
                "F8 same-speaker negative-gap crosstalk spoof",
            )
            return 2, 6

        _record(8, "oracle_variant_differentiation_and_crosstalk", _f08)

        # 9. oracle_cue_sheet_numeric_boundaries
        def _f09() -> tuple[int, int]:
            reg = make_minimal_registry()

            def _sheet(cues: list[Any]) -> EpisodeCueSheet:
                return EpisodeCueSheet(
                    episode_id="E001_TEST",
                    chapter_number=1,
                    title="Boundary Test",
                    mode="bilingual_business_drama",
                    acts=[],
                    cues=cues,
                )

            ok_cues = [
                make_timeline_cue(cue_id="B1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="[measured] Boundary pass one.", stability=0.0, playback_rate=0.65, gap_after_s=-0.25),
                make_timeline_cue(cue_id="B2", act_id="a1", kind="dialogue", role_id="victoria_vance", language_code="en", text="[measured] Boundary pass two.", stability=0.5, playback_rate=1.35, gap_after_s=10.0, duck_under_next=True, duck_gain=0.02, duck_lead_in_s=0.5),
                make_timeline_cue(cue_id="B2_TGT", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="[measured] 同传目标一。", stability=0.5),
                make_timeline_cue(cue_id="B3", act_id="a1", kind="dialogue", role_id="alistair_finch", language_code="en", text="[measured] Boundary pass three.", stability=1.0, playback_rate=1.0, gap_after_s=0.3, duck_under_next=True, duck_gain=0.60, duck_lead_in_s=15.0),
                make_timeline_cue(cue_id="B4", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="[measured] Target cue.", stability=0.5),
                make_timeline_cue(cue_id="S1", act_id="a1", kind="sfx", sfx_prompt="Door click, no human voice", duration_seconds=0.5),
                make_timeline_cue(cue_id="S2", act_id="a1", kind="sfx", sfx_prompt="Boardroom rain, no human voice", duration_seconds=30.0),
            ]
            oracle_cue_sheet_numeric_boundaries(_sheet(ok_cues), reg)

            bad_cases: list[tuple[str, list[Any]]] = [
                ("playback_rate=0.649", [make_timeline_cue(cue_id="X1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello world.", playback_rate=0.649)]),
                ("playback_rate=1.351", [make_timeline_cue(cue_id="X2", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello world.", playback_rate=1.351)]),
                ("gap_after_s=-0.251", [make_timeline_cue(cue_id="X3", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello world.", gap_after_s=-0.251)]),
                ("gap_after_s=10.01", [make_timeline_cue(cue_id="X4", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello world.", gap_after_s=10.01)]),
                ("duck_gain=0.019", [make_timeline_cue(cue_id="X5a", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", duck_under_next=True, duck_gain=0.019), make_timeline_cue(cue_id="X5b", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="你好。")]),
                ("duck_gain=0.601", [make_timeline_cue(cue_id="X6a", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", duck_under_next=True, duck_gain=0.601), make_timeline_cue(cue_id="X6b", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="你好。")]),
                ("duck_lead_in_s=0.49", [make_timeline_cue(cue_id="X7a", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", duck_under_next=True, duck_lead_in_s=0.49), make_timeline_cue(cue_id="X7b", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="你好。")]),
                ("duck_lead_in_s=15.01", [make_timeline_cue(cue_id="X8a", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", duck_under_next=True, duck_lead_in_s=15.01), make_timeline_cue(cue_id="X8b", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="你好。")]),
                ("sfx_dur=0.49", [make_timeline_cue(cue_id="X9", act_id="a1", kind="sfx", sfx_prompt="Click, no voice", duration_seconds=0.49)]),
                ("sfx_dur=30.01", [make_timeline_cue(cue_id="X10", act_id="a1", kind="sfx", sfx_prompt="Rain, no voice", duration_seconds=30.01)]),
                ("duck_at_eof", [make_timeline_cue(cue_id="X11", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", duck_under_next=True)]),
                ("stability=0.25", [make_timeline_cue(cue_id="X12", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", stability=0.25)]),
                ("duck_chained", [
                    make_timeline_cue(cue_id="X13a", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="One.", duck_under_next=True),
                    make_timeline_cue(cue_id="X13b", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="en", text="Two.", duck_under_next=True),
                    make_timeline_cue(cue_id="X13c", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="zh", text="三。"),
                ]),
                ("stability=True", [make_timeline_cue(cue_id="X14", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", stability=True)]),  # type: ignore[arg-type]
                ("duck_lead_in_str", [make_timeline_cue(cue_id="X15a", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.", duck_under_next=True, duck_lead_in_s="2.0"), make_timeline_cue(cue_id="X15b", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="你好。")]),  # type: ignore[arg-type]
                ("sfx_dur_none", [make_timeline_cue(cue_id="X16", act_id="a1", kind="sfx", sfx_prompt="Click, no voice", duration_seconds=None)]),  # type: ignore[arg-type]
            ]
            for lbl, clist in bad_cases:
                _assert_mutant_fails(
                    lambda cl=clist: oracle_cue_sheet_numeric_boundaries(_sheet(cl), reg),
                    f"F9 {lbl}",
                )
            return 1, len(bad_cases)

        _record(9, "oracle_cue_sheet_numeric_boundaries", _f09)

        # 10. oracle_dialogue_text_and_bilingual_rules
        def _f10() -> tuple[int, int]:
            oracle_dialogue_text_and_bilingual_rules("[measured] It is not a cash loss.", 0.5, "en")
            oracle_dialogue_text_and_bilingual_rules("[aside] 我们把账算清楚。", 0.5, "zh")
            oracle_dialogue_text_and_bilingual_rules("[icy polite] 这个 phantom number 站不住脚。", 0.5, "zh-en")
            mutants = [
                ("SSML", '<break time="0.5s"/> Hello.', 0.5, "en"),
                ("CJK tag", "[冷笑] 这不可能。", 0.5, "zh"),
                ("UPPER tag", "[COLDLY] That is absurd.", 0.5, "en"),
                ("Unclosed bracket", "[softly Watch the ledger.", 0.5, "en"),
                ("EN pure CJK", "[measured] 纯中文句子。", 0.5, "en"),
                ("ZH pure EN", "[measured] Pure English sentence.", 0.5, "zh"),
                ("Bad lang fr", "[measured] Bonjour.", 0.5, "fr"),
            ]
            for lbl, txt, stab, lang in mutants:
                _assert_mutant_fails(
                    lambda t=txt, s=stab, l=lang: oracle_dialogue_text_and_bilingual_rules(t, s, l),
                    f"F10 {lbl}",
                )
            return 3, len(mutants)

        _record(10, "oracle_dialogue_text_and_bilingual_rules", _f10)

        # 11. oracle_ast_zero_api_and_zero_edge_tts
        def _f11() -> tuple[int, int]:
            clean_src = (
                '"""Production anchor builder: 0% edge-tts, 0 ElevenLabs API."""\n'
                "import json\nimport wave\n"
                "def check(name):\n"
                '    is_clean = "edge-tts" not in name\n'
                "    return is_clean\n"
            )
            oracle_ast_zero_api_and_zero_edge_tts(clean_src, "clean_control.py")
            # Specificity control: whitelisted pure-local ffprobe helper from elevenlabs_client MUST PASS
            local_helper_src = (
                "from aigc_audio_pipeline.elevenlabs_client import probe_duration_seconds, ffmpeg_available\n"
                "def dur(p):\n    return probe_duration_seconds(p)\n"
            )
            oracle_ast_zero_api_and_zero_edge_tts(local_helper_src, "local_ffprobe_helper.py")
            # Specificity control (D6): benign cmd.append MUST PASS
            benign_append_src = (
                "import subprocess\n"
                'cmd = ["python3", "launch_g4_global_edge_drama3.py"]\n'
                'cmd.append("--episodes")\n'
                "subprocess.run(cmd)\n"
            )
            oracle_ast_zero_api_and_zero_edge_tts(benign_append_src, "benign_append.py")
            mutants = [
                ("import edge_tts", "import edge_tts\n"),
                ("subprocess edge-tts", 'import subprocess\nsubprocess.run(["edge-tts", "--text", "hi"])\n'),
                ("ElevenLabsClient import", "from aigc_audio_pipeline.elevenlabs_client import ElevenLabsClient\n"),
                ("ElevenLabs star import", "from aigc_audio_pipeline.elevenlabs_client import *\n"),
                ("ElevenLabs URL", 'URL = "https://api.elevenlabs.io/v1/text-to-speech"\n'),
                # 8 Challenger B1 dynamic-import / alias / taint bypasses
                ("importlib edge_tts", 'import importlib\nimportlib.import_module("edge_tts")\n'),
                ("dunder __import__ edge_tts", '__import__("edge_tts")\n'),
                ("importlib elevenlabs", 'import importlib\nimportlib.import_module("elevenlabs")\n'),
                ("from subprocess import run", 'from subprocess import run\nrun(["edge-tts", "--text", "hi"])\n'),
                ("subprocess alias sp", 'import subprocess as sp\nsp.run(["edge-tts", "--text", "hi"])\n'),
                ("tainted cmd variable", 'import subprocess\ncmd = ["edge-tts", "--text", "hi"]\nsubprocess.run(cmd)\n'),
                ("os.execvp edge-tts", 'import os\nos.execvp("edge-tts", ["edge-tts"])\n'),
                ("exec import edge_tts", 'exec("import edge_tts")\n'),
                # D6 list-mutator taint bypasses
                ("cmd.append edge-tts", 'import subprocess\ncmd = ["python3"]\ncmd.append("edge-tts")\nsubprocess.run(cmd)\n'),
                ("cmd.extend edge-tts", 'import subprocess\ncmd = ["python3"]\ncmd.extend(["edge-tts", "-t", "hi"])\nsubprocess.run(cmd)\n'),
                ("cmd.insert edge-tts", 'import subprocess\ncmd = ["-t", "hi"]\ncmd.insert(0, "edge-tts")\nsubprocess.run(cmd)\n'),
            ]
            for lbl, src in mutants:
                _assert_mutant_fails(
                    lambda s=src: oracle_ast_zero_api_and_zero_edge_tts(s, f"{lbl}.py"),
                    f"F11 {lbl}",
                )
            return 3, len(mutants)

        _record(11, "oracle_ast_zero_api_and_zero_edge_tts", _f11)

        # 12. oracle_variant_resolver_regex
        def _f12() -> tuple[int, int]:
            fnames = [
                "E001_VA_a.json",
                "E001_VB_b.json",
                "E001_VC_c.json",
                "E001_VD_d.json",
                "E002_x.json",
                "E003A_y.json",
            ]
            res = oracle_variant_resolver_regex(fnames, ["E001_VARIANTS", "E002", "E003A"])
            assert len(res) == 6
            # Mutant 1: legacy broken regex collapses E001_VA..VD onto E001
            _assert_mutant_fails(
                lambda: oracle_variant_resolver_regex(fnames, None, regex=LEGACY_BROKEN_RESOLVER_REGEX),
                "F12 legacy regex collision",
            )
            # Mutant 2: invalid target E001_VZ
            _assert_mutant_fails(
                lambda: oracle_variant_resolver_regex(fnames, ["E001_VZ"]),
                "F12 invalid target E001_VZ",
            )
            return 1, 2

        _record(12, "oracle_variant_resolver_regex", _f12)

        # 13. oracle_srt_non_overlap_and_dual_line
        def _f13() -> tuple[int, int]:
            good_srt = (
                "1\n00:00:00,300 --> 00:00:02,500\n【Lin Chen】It is not a cash loss.\n这不是现金亏损。\n\n"
                "2\n00:00:02,510 --> 00:00:05,100\n【Victoria】In other words, you need capital.\n换句话说，你需要融资。\n"
            )
            oracle_srt_non_overlap_and_dual_line(
                good_srt,
                expected_translations=["这不是现金亏损。", "换句话说，你需要融资。"],
                tts_prompts=["[measured] It is not a cash loss.", "[icy polite] In other words, you need capital."],
            )
            # Mutant 1: overlapping timestamps
            bad_overlap = good_srt.replace("00:00:02,510", "00:00:02,200")
            _assert_mutant_fails(lambda: oracle_srt_non_overlap_and_dual_line(bad_overlap), "F13 overlap SRT")
            # Mutant 2: missing ZH line 2
            bad_no_zh = "1\n00:00:00,300 --> 00:00:02,500\n【Lin Chen】It is not a cash loss.\n"
            _assert_mutant_fails(
                lambda: oracle_srt_non_overlap_and_dual_line(bad_no_zh, expected_translations=["这不是现金亏损。"]),
                "F13 missing ZH line 2",
            )
            # Mutant 3: ZH gloss leaked into TTS prompt
            _assert_mutant_fails(
                lambda: oracle_srt_non_overlap_and_dual_line(
                    good_srt,
                    expected_translations=["这不是现金亏损。"],
                    tts_prompts=["[measured] It is not a cash loss. 这不是现金亏损。"],
                ),
                "F13 gloss leaked into TTS",
            )
            return 1, 3

        _record(13, "oracle_srt_non_overlap_and_dual_line", _f13)

        # 14. oracle_dual_script_zh_en_qa
        def _f14() -> tuple[int, int]:
            oracle_dual_script_zh_en_qa(
                "[measured] 这份财报里的 phantom number 根本不是 not a cash loss。",
                "这份财报里的 phantom number 根本不是 not a cash loss。",
                language_code="zh-en",
            )
            # Specificity control: legitimate spoken "confident" must PASS!
            oracle_dual_script_zh_en_qa(
                "[confident] We remain confident in our unit economics today.",
                "We remain confident in our unit economics today.",
                language_code="en",
            )
            # Mutant 1: CJK intact, EN dropped
            _assert_mutant_fails(
                lambda: oracle_dual_script_zh_en_qa(
                    "[measured] 这份财报里的 phantom number 和 capital efficient 根本站不住脚。",
                    "这份财报里的和根本站不住脚。",
                    language_code="zh-en",
                ),
                "F14 dropped embedded EN",
            )
            # Mutant 2: trailing EN phrase truncated
            _assert_mutant_fails(
                lambda: oracle_dual_script_zh_en_qa(
                    "[firmly] 我们今天必须彻底锁死这个 phantom number and upside",
                    "我们今天必须彻底锁死这个",
                    language_code="zh-en",
                ),
                "F14 truncated EN tail",
            )
            # Mutant 3: unprompted corporate tag "deadpan" leaked aloud
            _assert_mutant_fails(
                lambda: oracle_dual_script_zh_en_qa(
                    "[deadpan] That margin forecast is completely unsustainable.",
                    "deadpan That margin forecast is completely unsustainable.",
                    language_code="en",
                ),
                "F14 leaked deadpan tag",
            )
            return 2, 3

        _record(14, "oracle_dual_script_zh_en_qa", _f14)

        # 15. oracle_domain_no_xianxia_leak
        def _f15() -> tuple[int, int]:
            from aigc_audio_pipeline.polyphones import apply_domain_polyphone_overrides

            sample_in = "引气九重降临辟谷"
            sample_out = apply_domain_polyphone_overrides(sample_in, domain="business_english_drama")
            oracle_domain_no_xianxia_leak(
                polyphone_input=sample_in,
                polyphone_output=sample_out,
                drama3_prompt="[measured, calm executive tone] That is not a cash loss.",
            )
            # Specificity control 1: negative guardrail line referencing '仙侠/修仙' MUST PASS
            assert_no_xianxia_plot_drift("技术规范：严禁回退仙侠/修仙旁白模板，保持HBO商战冷峻风。", "guardrail_ok.md")
            # Specificity control 2: Markdown ban-table row inheriting header negation MUST PASS
            ban_table_md = (
                "| 违禁类别 | 严禁出现的具体字符串或表演恶习 | 替代规范 |\n"
                "| :--- | :--- | :--- |\n"
                "| **声学退化** | 播音腔、仙侠 `mental_realm` | 锁定 HBO 商战声场 |\n"
            )
            assert_no_xianxia_plot_drift(ban_table_md, "ban_table_ok.md")
            # Specificity control 3 (D3): legitimate ML jargon '预训练炼丹' MUST PASS
            assert_no_xianxia_plot_drift("区分“推理部署轻便”与“预训练炼丹天价”的专业科技高管词。", "ml_jargon_ok.md")
            # Specificity control 4 (D3): ASCII '0 仙侠词泄露' negative guardrail MUST PASS
            assert_no_xianxia_plot_drift("门禁校验确保 0 仙侠词泄露与零播音腔。", "zero_ascii_guardrail_ok.md")
            # Mutant 1: Xianxia narration leaked
            _assert_mutant_fails(
                lambda: oracle_domain_no_xianxia_leak(
                    drama3_prompt="[steady, cinematic Xianxia narration] That is not a cash loss."
                ),
                "F15 Xianxia narration leak",
            )
            # Mutant 2: Xianxia polyphone mutated
            _assert_mutant_fails(
                lambda: oracle_domain_no_xianxia_leak(
                    polyphone_input="引气九重降临辟谷",
                    polyphone_output="引气九崇酱临必谷",
                ),
                "F15 Xianxia polyphone leak",
            )
            # Mutant 3: unnegated Xianxia plot drift in document
            _assert_mutant_fails(
                lambda: assert_no_xianxia_plot_drift("主角林沉开启修仙之路。", "bad_doc.md"),
                "F15 unnegated 修仙 drift",
            )
            # Mutant 4: strict trope '筑基' banned even on negated line
            _assert_mutant_fails(
                lambda: assert_no_xianxia_plot_drift("禁止出现筑基设定。", "bad_trope.md"),
                "F15 strict trope 筑基",
            )
            # Mutant 5: unnegated '仙侠' in ordinary (non-ban) Markdown table MUST FAIL
            ordinary_table_md = (
                "| 集数 | 剧情主线 | 声场 |\n"
                "| :--- | :--- | :--- |\n"
                "| E001 | 主角踏入仙侠商战世界 | boardroom |\n"
            )
            _assert_mutant_fails(
                lambda: assert_no_xianxia_plot_drift(ordinary_table_md, "ordinary_table_bad.md"),
                "F15 unnegated 仙侠 in non-ban table",
            )
            # Mutant 6: ban-table context must reset immediately after table ends
            reset_after_ban_md = ban_table_md + "\n主角林沉开启仙侠商战。\n"
            _assert_mutant_fails(
                lambda: assert_no_xianxia_plot_drift(reset_after_ban_md, "post_table_bad.md"),
                "F15 unnegated 仙侠 after ban table reset",
            )
            # D3 Mutants 7-11: expanded strict tropes + standalone 炼丹 + non-zero '10 集仙侠'
            for trope in ("炼气", "渡劫", "飞升", "灵根"):
                _assert_mutant_fails(
                    lambda t=trope: assert_no_xianxia_plot_drift(
                        f"| 违禁词 | 严禁出现 |\n|---|---|\n| 剧情 | {t} |\n",
                        f"bad_{t}.md",
                    ),
                    f"F15 expanded strict trope {trope}",
                )
            _assert_mutant_fails(
                lambda: assert_no_xianxia_plot_drift("山洞里的炼丹炉突然炸裂。", "bad_liandan.md"),
                "F15 standalone 炼丹炉",
            )
            _assert_mutant_fails(
                lambda: assert_no_xianxia_plot_drift("第 10 集仙侠商战终局。", "bad_ep10_xianxia.md"),
                "F15 non-zero '第 10 集仙侠'",
            )
            return 5, 12

        _record(15, "oracle_domain_no_xianxia_leak", _f15)

        # 16. oracle_viral_45s_cutlist_and_rubric
        def _f16() -> tuple[int, int]:
            va = make_synthetic_e001_variant("E001_VA", distinct_seed_word="f16a")
            vb = make_synthetic_e001_variant("E001_VB", inner_monologue_count=4, include_zhou_mo_debrief=True, distinct_seed_word="f16b")
            vc = make_synthetic_e001_variant("E001_VC", phone_call_count=2, distinct_seed_word="f16c")
            vd = make_synthetic_e001_variant("E001_VD", duck_count=2, distinct_seed_word="f16d")
            four_sheets = {"E001_VA": va, "E001_VB": vb, "E001_VC": vc, "E001_VD": vd}

            def _find_slice(cs, start_idx: int = 0) -> tuple[str, str]:
                for j in range(start_idx + 1, len(cs.cues)):
                    d = estimate_cue_slice_duration_s(cs.cues[start_idx : j + 1])
                    if 40.0 <= d <= 50.0:
                        return cs.cues[start_idx].cue_id, cs.cues[j].cue_id
                raise AssertionError(f"Could not find 40-50s slice in {cs.episode_id}")

            va_s, va_e = _find_slice(va, 0)
            vb_s, vb_e = _find_slice(vb, 0)
            vc_s, vc_e = _find_slice(vc, 0)
            vd_s, vd_e = _find_slice(vd, 0)

            good_cutlist = [
                {
                    "variant_id": "E001_VA",
                    "start_cue_id": va_s,
                    "end_cue_id": va_e,
                    "has_hook": True,
                    "has_cta": True,
                }
            ]
            good_rubric = (
                "| 维度 | 权重 |\n|---|---|\n"
                "| 1. 剧情沉浸感 | 20分 |\n| 2. 英语地道度 | 20分 |\n"
                "| 3. 口音听感 | 15分 |\n| 4. 节奏压迫感 | 15分 |\n"
                "| 5. 双语无缝度 | 10分 |\n| 6. 拆局留存 | 10分 |\n"
                "| 7. 切片传播力 | 10分 |\n| 总分 | 100分 |\n"
            )
            oracle_viral_45s_cutlist_and_rubric(good_cutlist, {"E001_VA": va}, good_rubric)

            # Positive 2: Combined 4-variant Markdown table with bold cue IDs + preceding overview section ignored
            combined_md = (
                f"## 总览\n本方案以 E001_VA 为例，提及 {va.cues[0].cue_id} 和 {va.cues[1].cue_id} 作为示例。\n\n"
                f"## E001 四版本 45s 爆款短视频切片清单\n"
                f"| 变体 | 切片范围 | 标题 | 3秒钩子 | 引流CTA |\n"
                f"|---|---|---|---|---|\n"
                f"| E001_VA | **{va_s}** → **{va_e}** | 中式直译 vs 华尔街反杀 | 3秒冲突开场 | 评论区领小宇宙完整版 |\n"
                f"| E001_VB | `{vb_s}` – `{vb_e}` | 硅谷暗战 vs 纸牌屋独白 | 开场钩子狙击 | 搜索小宇宙听完整版 |\n"
                f"| E001_VC | **{vc_s}** -> **{vc_e}** | 深圳凌晨 vs 伦敦压价 | 3s急促电话 | 领取双语精读手册 |\n"
                f"| E001_VD | `{vd_s}` ~ `{vd_e}` | 英文原声 vs 同传叠音 | 冲突钩子开局 | 小宇宙搜索跨境底牌 |\n"
            )
            extracted_4 = extract_viral_cutlists_from_markdown(combined_md, four_sheets)
            assert len(extracted_4) == 4, f"Expected 4 table cutlists (overview ignored), got {len(extracted_4)}"
            oracle_viral_45s_cutlist_and_rubric(extracted_4, four_sheets)

            # Positive 3: 6-dim rubric with extra scale column BEFORE 权重 + preceding scorecard table
            rubric_6dim = (
                "## 自动化指标总览\n"
                "| 维度 | E001_VA | E001_VB | E001_VC | E001_VD |\n|---|---|---|---|---|\n"
                "| 总时长(秒) | 710 | 725 | 705 | 718 |\n"
                "| 打断次数 | 8 | 5 | 7 | 4 |\n"
                "| 慢速条数 | 4 | 4 | 4 | 4 |\n"
                "| 跟读条数 | 4 | 4 | 4 | 4 |\n"
                "| 英文占比 | 68 | 55 | 62 | 58 |\n\n"
                "## 100分盲听评分表\n"
                "| 维度 | 评分刻度 | 权重 |\n|---|---|---|\n"
                "| 1. 剧情张力 | 1-5 | 25分 |\n| 2. 商战英语地道度 | 1-5 | 20分 |\n"
                "| 3. 英美口音听感 | 1-5 | 15分 |\n| 4. 双语节奏无缝度 | 1-5 | 15分 |\n"
                "| 5. 3分钟拆局留存 | 1-5 | 15分 |\n| 6. 45秒传播钩子 | 1-5 | 10分 |\n"
                "| 总计 | — | 100分 |\n"
            )
            res_6 = oracle_viral_45s_cutlist_and_rubric(rubric_md=rubric_6dim)
            assert len(res_6["rubric_weights"]) == 6 and res_6["rubric_sum"] == 100

            # Positive 4 (H2): 分值(1-5) column BEFORE 权重 column prioritizes 权重
            rubric_h2 = (
                "## 100分盲听评分表\n"
                "| 评估维度 | 分值(1-5) | 权重 | 锚定标准 |\n"
                "|---|---|---|---|\n"
                "| 1. 剧情张力 | 1-5 | 25% | HBO级压迫感 |\n"
                "| 2. 商战英语地道度 | 1-5 | 20% | 真实高管表达 |\n"
                "| 3. 英美口音听感 | 1-5 | 15% | 美音+伦敦RP清晰度 |\n"
                "| 4. 双语节奏无缝度 | 1-5 | 15% | 零教科书味 |\n"
                "| 5. 3分钟拆局留存 | 1-5 | 15% | 0.8x+1.0x可跟读 |\n"
                "| 6. 45秒传播钩子 | 1-5 | 10% | 3秒强钩子 |\n"
                "| 总计 | — | 100% | 盲听汇总 |\n"
            )
            res_h2 = oracle_viral_45s_cutlist_and_rubric(rubric_md=rubric_h2)
            assert len(res_h2["rubric_weights"]) == 6 and res_h2["rubric_sum"] == 100

            # Positive 5 (H3): ## 总览 prose citing short sample range with arrow -> ignored before real 4-row table
            overview_arrow_md = (
                f"## 总览\n本方案以 E001_VA 为例，节选 {va.cues[0].cue_id} → {va.cues[1].cue_id}（约15秒示例引用）说明节奏。\n\n"
                f"## E001 四版本 45s 爆款短视频切片清单\n"
                f"| 变体 | 切片范围 | 标题 | 3秒钩子 | 引流CTA |\n"
                f"|---|---|---|---|---|\n"
                f"| E001_VA | **{va_s}** → **{va_e}** | 中式直译 vs 华尔街反杀 | 3秒冲突开场 | 评论区领小宇宙完整版 |\n"
                f"| E001_VB | `{vb_s}` – `{vb_e}` | 硅谷暗战 vs 纸牌屋独白 | 开场钩子狙击 | 搜索小宇宙听完整版 |\n"
                f"| E001_VC | **{vc_s}** -> **{vc_e}** | 深圳凌晨 vs 伦敦压价 | 3s急促电话 | 领取双语精读手册 |\n"
                f"| E001_VD | `{vd_s}` ~ `{vd_e}` | 英文原声 vs 同传叠音 | 冲突钩子开局 | 小宇宙搜索跨境底牌 |\n"
            )
            extracted_h3 = extract_viral_cutlists_from_markdown(overview_arrow_md, four_sheets)
            assert len(extracted_h3) == 4, (
                f"Expected exact 4 cutlists (ignoring ## 总览 arrow citation), got {len(extracted_h3)}"
            )
            oracle_viral_45s_cutlist_and_rubric(extracted_h3, four_sheets)

            # Positive 6 (C5): Overview summary index table (§3.1 总控表, no hook/CTA cols) + detailed Layout C sections
            # with CJK-digit spaced "前 3 秒" hook MUST extract exact 4 cutlists cleanly
            summary_plus_detail_md = (
                f"### 3.1 四变体爆款切片总控表\n"
                f"| 切片编号 | 来源变体 | 精确 Cue 区间 | 冲突主题（A vs B） |\n"
                f"|---|---|---|---|\n"
                f"| Clip A | `E001_VA` | `{va_s}` .. `{va_e}` | 账面巨亏 vs 零现金流出 |\n"
                f"| Clip B | `E001_VB` | `{vb_s}` .. `{vb_e}` | 优雅砍价 vs 冻帧直译 |\n"
                f"| Clip C | `E001_VC` | `{vc_s}` .. `{vc_e}` | 裸芯片 vs 十倍吞吐 |\n"
                f"| Clip D | `E001_VD` | `{vd_s}` .. `{vd_e}` | 算力绞杀 vs 同传拆解 |\n\n"
                f"### 3.2 Clip A — `E001_VA`\n"
                f"- **Cue Range**: `{va_s}` .. `{va_e}`\n"
                f"- **顶部 A vs B 冲突标题**：巨亏 8000 万 vs 零现金流出\n"
                f"- **前 3 秒静音抓手**：开屏红字直接打断 VC\n"
                f"- **引流尾帧 CTA**：点击小宇宙听完整版\n\n"
                f"### 3.3 Clip B — `E001_VB`\n"
                f"- **Cue Range**: `{vb_s}` .. `{vb_e}`\n"
                f"- **顶部 A vs B 冲突标题**：优雅伦敦腔 vs 冻帧直译\n"
                f"- **前 3 秒静音抓手**：冻帧揭穿礼貌带刀\n"
                f"- **引流尾帧 CTA**：评论区领双语精读手册\n\n"
                f"### 3.4 Clip C — `E001_VC`\n"
                f"- **Cue Range**: `{vc_s}` .. `{vc_e}`\n"
                f"- **顶部 A vs B 冲突标题**：单颗芯片 vs 十倍吞吐\n"
                f"- **前 3 秒静音抓手**：伦敦电话线实时抢话\n"
                f"- **引流尾帧 CTA**：点左下角听完整版\n\n"
                f"### 3.5 Clip D — `E001_VD`\n"
                f"- **Cue Range**: `{vd_s}` .. `{vd_e}`\n"
                f"- **顶部 A vs B 冲突标题**：原声独奏 vs 同传压混\n"
                f"- **前 3 秒静音抓手**：左轨原声压混叠中文\n"
                f"- **引流尾帧 CTA**：小宇宙搜索完整版\n"
            )
            extracted_c5 = extract_viral_cutlists_from_markdown(summary_plus_detail_md, four_sheets)
            assert len(extracted_c5) == 4, (
                f"Expected exact 4 cutlists from summary table + detailed sections, got {len(extracted_c5)}"
            )
            assert all(cl["has_hook"] and cl["has_cta"] and cl["has_title"] for cl in extracted_c5)
            oracle_viral_45s_cutlist_and_rubric(extracted_c5, four_sheets)

            # Mutant 1: < 38s cutlist
            short_cl = [{**good_cutlist[0], "end_cue_id": va.cues[1].cue_id}]
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(short_cl, {"E001_VA": va}),
                "F16 <38s cutlist",
            )
            # Mutant 2: > 55s cutlist
            end_idx_va = next(i for i, c in enumerate(va.cues) if c.cue_id == va_e)
            long_cl = [{**good_cutlist[0], "end_cue_id": va.cues[min(len(va.cues) - 1, end_idx_va + 10)].cue_id}]
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(long_cl, {"E001_VA": va}),
                "F16 >55s cutlist",
            )
            # Mutant 3: nonexistent cue_id
            bad_id_cl = [{**good_cutlist[0], "end_cue_id": "E001_VA_C999"}]
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(bad_id_cl, {"E001_VA": va}),
                "F16 nonexistent cue_id",
            )
            # Mutant 4: rubric weights sum to 95
            bad_rubric = good_rubric.replace("| 7. 切片传播力 | 10分 |", "| 7. 切片传播力 | 5分 |")
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(rubric_md=bad_rubric),
                "F16 rubric sum=95",
            )
            # Mutant 5 (B4c): 4x duplicate E001_VA cutlists
            dup_4 = [dict(good_cutlist[0]) for _ in range(4)]
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(dup_4, four_sheets),
                "F16 4x duplicate E001_VA cutlists",
            )
            # Mutant 6 (B4c): 4 distinct-slice E001_VA-only cutlists (single-variant padding)
            va_pad_4 = []
            for st_i in range(4):
                s_i, e_i = _find_slice(va, st_i)
                va_pad_4.append({"variant_id": "E001_VA", "start_cue_id": s_i, "end_cue_id": e_i, "has_hook": True, "has_cta": True})
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(va_pad_4, four_sheets),
                "F16 4x E001_VA-only padding missing VB/VC/VD",
            )
            # Mutant 7 (HIGH-1): 4-dim rubric sum=100 (<5 dims)
            rubric_4dim = (
                "| 维度 | 权重 |\n|---|---|\n"
                "| 1. A | 25分 |\n| 2. B | 25分 |\n| 3. C | 25分 |\n| 4. D | 25分 |\n"
            )
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(rubric_md=rubric_4dim),
                "F16 4-dim rubric (<5)",
            )
            # Mutant 8 (HIGH-1): 6-dim rubric sum=95
            bad_6dim = rubric_6dim.replace("| 6. 45秒传播钩子 | 1-5 | 10分 |", "| 6. 45秒传播钩子 | 1-5 | 5分 |")
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(rubric_md=bad_6dim),
                "F16 6-dim rubric sum=95",
            )
            # Mutant 9 (C5): duplicate Layout C sections MUST STILL FAIL duplicate detection
            dup_section_md = (
                summary_plus_detail_md
                + f"\n### 3.6 Clip A Repeat — `E001_VA`\n"
                + f"- **Cue Range**: `{va_s}` .. `{va_e}`\n"
                + f"- **顶部 A vs B 冲突标题**：重复切片\n"
                + f"- **前 3 秒静音抓手**：重复抓手\n"
                + f"- **引流尾帧 CTA**：点击小宇宙听完整版\n"
            )
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(
                    extract_viral_cutlists_from_markdown(dup_section_md, four_sheets),
                    four_sheets,
                ),
                "F16 duplicate Layout C section",
            )
            # D7.3 Mutant 10: duck_under_next viral slice whose true paired span exceeds 55s (~57.7s)
            vd_long_duck = EpisodeCueSheet(
                episode_id="E001_VD",
                chapter_number=1,
                title="Long Duck Viral Mutant",
                mode="bilingual_business_drama",
                acts=vd.acts,
                cues=[
                    c
                    for k in range(3)
                    for c in (
                        make_timeline_cue(
                            cue_id=f"LD_EN_{k}",
                            act_id="act_2",
                            kind="dialogue",
                            role_id="alistair_finch",
                            language_code="en",
                            text="[measured] " + " ".join(["throughput"] * 50),
                            duck_under_next=True,
                            duck_lead_in_s=3.5,
                            duck_gain=0.15,
                            gap_after_s=0.0,
                        ),
                        make_timeline_cue(
                            cue_id=f"LD_ZH_{k}",
                            act_id="act_2",
                            kind="dialogue",
                            role_id="lin_chen",
                            language_code="zh",
                            text="[aside] " + "同传拆局压价条款底线防守" * 3,
                            gap_after_s=0.35,
                        ),
                    )
                ],
            )
            _assert_mutant_fails(
                lambda: oracle_viral_45s_cutlist_and_rubric(
                    [{"variant_id": "E001_VD", "start_cue_id": "LD_EN_0", "end_cue_id": "LD_ZH_2", "has_hook": True, "has_cta": True}],
                    {"E001_VD": vd_long_duck},
                ),
                "F16 duck_under_next paired duration >55s",
            )
            return 6, 10

        _record(16, "oracle_viral_45s_cutlist_and_rubric", _f16)

        # 17. oracle_notebook_and_bundle_integrity
        def _f17() -> tuple[int, int]:
            good_nb = {
                "nbformat": 4,
                "nbformat_minor": 5,
                "metadata": {"accelerator": "GPU", "colab": {"gpuType": "G4", "machine_shape": "hm"}},
                "cells": [
                    {
                        "cell_type": "code",
                        "id": "c1",
                        "metadata": {},
                        "execution_count": None,
                        "outputs": [],
                        "source": [
                            "import subprocess\n",
                            "subprocess.run(['python3', 'colab_96gb/colab_agent_bridge.py'])\n",
                        ],
                    },
                    {
                        "cell_type": "code",
                        "id": "c2",
                        "metadata": {},
                        "execution_count": None,
                        "outputs": [],
                        "source": [
                            "!python3 colab_96gb/launch_g4_global_edge_drama3.py --episodes E001_VARIANTS --skip-existing\n"
                        ],
                    },
                ],
            }
            good_zip = tmp_root / "good_bundle.zip"
            members = [
                "voice_casting_registry.json",
                "voice_cast_drama3.json",
                "src/aigc_audio_pipeline/models.py",
                "src/aigc_audio_pipeline/mixer.py",
                "prepare_global_edge_voice_anchors.py",
                "run_global_edge_96gb_studio.py",
                "launch_g4_global_edge_drama3.py",
                "auditions/AUDITION_GLOBAL_EDGE_test.json",
                "cue_sheets/E001_VA_test.json",
                "cue_sheets/E001_VB_test.json",
                "cue_sheets/E001_VC_test.json",
                "cue_sheets/E001_VD_test.json",
                "voice_anchors/lin_chen.wav",
            ]
            with zipfile.ZipFile(good_zip, "w") as zf:
                for m in members:
                    zf.writestr(m, "{}")
            good_manifest = {
                "anchor_schema_version": "v2_real_human_studio",
                "anchor_sample_rate_hz": 44100,
                "characters": {
                    "lin_chen": {"source_voice_name": "real_studio_lin_chen", "anchor_text": "Clean studio anchor."}
                },
            }
            oracle_notebook_and_bundle_integrity(
                good_nb,
                good_zip,
                good_manifest,
                launcher_help_flags={"--episodes", "--skip-existing", "--offline-dry-run"},
            )
            # Positive 2: Buffett-style multi-line subprocess.check_call([...]) with valid flags
            multiline_ok_nb = json.loads(json.dumps(good_nb))
            multiline_ok_nb["cells"][1]["source"] = [
                "import subprocess\n",
                "from pathlib import Path\n",
                "REPO = Path('/content/repo')\n",
                "subprocess.check_call([\n",
                "    'python3', '-u', str(REPO / 'colab_96gb/launch_g4_global_edge_drama3.py'),\n",
                "    '--episodes', 'E001_VARIANTS',\n",
                "    '--skip-existing',\n",
                "], cwd=str(REPO))\n",
            ]
            ml_summary = oracle_notebook_and_bundle_integrity(
                notebook_data=multiline_ok_nb,
                launcher_help_flags={"--episodes", "--skip-existing", "--offline-dry-run"},
            )
            assert ml_summary["notebook"]["launcher_flags"] == ["--episodes", "--skip-existing"]

            # Positive 5 (H1): commented-out legacy flag inside multi-line subprocess.check_call([...]) must PASS
            commented_ok_nb = json.loads(json.dumps(multiline_ok_nb))
            commented_ok_nb["cells"][1]["source"].insert(
                -1, "    # '--mirror-to-main-masters',  # legacy Buffett flag\n"
            )
            cm_summary = oracle_notebook_and_bundle_integrity(
                notebook_data=commented_ok_nb,
                launcher_help_flags={"--episodes", "--skip-existing", "--offline-dry-run"},
            )
            assert cm_summary["notebook"]["launcher_flags"] == ["--episodes", "--skip-existing"], (
                f"Commented-out flag leaked into launcher_flags: {cm_summary['notebook']['launcher_flags']}"
            )

            # Positive 6 (D1): multiline backslash-continued !magic cell MUST PASS
            multiline_magic_nb = json.loads(json.dumps(good_nb))
            multiline_magic_nb["cells"][1]["source"] = [
                "!python3 colab_96gb/launch_g4_global_edge_drama3.py \\\n",
                "  --episodes E001_VARIANTS \\\n",
                "  --skip-existing\n",
            ]
            mm_summary = oracle_notebook_and_bundle_integrity(
                notebook_data=multiline_magic_nb,
                launcher_help_flags={"--episodes", "--skip-existing", "--offline-dry-run"},
            )
            assert mm_summary["notebook"]["launcher_flags"] == ["--episodes", "--skip-existing"]

            # Positive 7 (D1/G6b): dynamic cmd.append(...) with valid flags extracts ALL flags
            append_ok_nb = json.loads(json.dumps(good_nb))
            append_ok_nb["cells"][1]["source"] = [
                "import subprocess\n",
                "cmd = ['python3', 'colab_96gb/launch_g4_global_edge_drama3.py', '--episodes', 'E001_VARIANTS']\n",
                "cmd.append('--skip-existing')\n",
                "subprocess.check_call(cmd)\n",
            ]
            ap_summary = oracle_notebook_and_bundle_integrity(
                notebook_data=append_ok_nb,
                launcher_help_flags={"--episodes", "--skip-existing"},
            )
            assert ap_summary["notebook"]["launcher_flags"] == ["--episodes", "--skip-existing"]

            # Positive 3 & 4 (HIGH-2): assert_anchor_sources_clean with policy metadata & list layout
            clean_anc_dict = {
                "policy": "0% edge-tts, 0% ElevenLabs API",
                "forbidden_providers": ["edge-tts", "elevenlabs"],
                "characters": {
                    rid: {"source_type": "real_human_studio", "url": f"https://archive.org/download/{rid}.wav"}
                    for rid in CANONICAL_ALL_8_ROLES
                },
            }
            assert_anchor_sources_clean(clean_anc_dict, CANONICAL_ALL_8_ROLES)
            clean_anc_list = [
                {"role_id": rid, "provider": "studio_recording", "source_url": f"https://example.org/{rid}.wav"}
                for rid in CANONICAL_ALL_8_ROLES
            ]
            assert_anchor_sources_clean(clean_anc_list, CANONICAL_ALL_8_ROLES)

            # Mutant 1: syntax error in code cell
            bad_nb = json.loads(json.dumps(good_nb))
            bad_nb["cells"][0]["source"] = ["def broken(:\n    pass\n"]
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(notebook_data=bad_nb),
                "F17 notebook syntax error",
            )
            # Mutant 2: ZIP missing E001_VD
            bad_zip = tmp_root / "bad_bundle.zip"
            with zipfile.ZipFile(bad_zip, "w") as zf:
                for m in members:
                    if "E001_VD" not in m:
                        zf.writestr(m, "{}")
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(zip_path=bad_zip),
                "F17 ZIP missing E001_VD",
            )
            # Mutant 3: anchor_schema_version v1_edge_tts
            bad_manifest = dict(good_manifest, anchor_schema_version="v1_edge_tts")
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(voice_cast_manifest=bad_manifest),
                "F17 v1_edge_tts manifest",
            )
            # Mutant 4: unsupported flag in notebook vs launcher --help
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(
                    notebook_data=good_nb,
                    launcher_help_flags={"--episodes"},
                ),
                "F17 notebook unsupported flag drift",
            )
            # Mutant 5: Buffett-style multi-line subprocess.check_call with bogus flag --mirror-to-main-masters
            multiline_bad_nb = json.loads(json.dumps(multiline_ok_nb))
            multiline_bad_nb["cells"][1]["source"].insert(-1, "    '--mirror-to-main-masters',\n")
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(
                    notebook_data=multiline_bad_nb,
                    launcher_help_flags={"--episodes", "--skip-existing"},
                ),
                "F17 multi-line notebook bogus flag",
            )
            # Mutant 6: launcher invoked with 0 extracted flags
            noflag_nb = json.loads(json.dumps(good_nb))
            noflag_nb["cells"][1]["source"] = [
                "# E001_VARIANTS\n",
                "!python3 colab_96gb/launch_g4_global_edge_drama3.py\n",
            ]
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(
                    notebook_data=noflag_nb,
                    launcher_help_flags={"--episodes", "--skip-existing"},
                ),
                "F17 notebook 0 extracted launcher flags",
            )
            # Mutant 7: en-US-GuyNeural under v2_real_human_studio
            neural_manifest = {
                "anchor_schema_version": "v2_real_human_studio",
                "anchor_sample_rate_hz": 44100,
                "characters": {
                    "lin_chen": {"source_voice_name": "en-US-GuyNeural", "anchor_text": "Synthetic."}
                },
            }
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(voice_cast_manifest=neural_manifest),
                "F17 en-US-GuyNeural manifest",
            )
            # Mutant 8: anchor_sample_rate_hz=24000
            bad_sr_manifest = dict(good_manifest, anchor_sample_rate_hz=24000)
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(voice_cast_manifest=bad_sr_manifest),
                "F17 anchor_sample_rate_hz=24000",
            )
            # Mutant 9: ZIP polluted with __pycache__/.pyc
            pyc_zip = tmp_root / "pyc_bundle.zip"
            with zipfile.ZipFile(pyc_zip, "w") as zf:
                for m in members:
                    zf.writestr(m, "{}")
                zf.writestr("src/aigc_audio_pipeline/__pycache__/models.cpython-311.pyc", b"pyc")
            _assert_mutant_fails(
                lambda: oracle_notebook_and_bundle_integrity(zip_path=pyc_zip),
                "F17 ZIP __pycache__/.pyc pollution",
            )
            # Mutants 10-12 (HIGH-2): assert_anchor_sources_clean synthetic source checks
            bad_anc_edge = json.loads(json.dumps(clean_anc_dict))
            bad_anc_edge["characters"]["lin_chen"]["source_type"] = "edge-tts"
            _assert_mutant_fails(
                lambda: assert_anchor_sources_clean(bad_anc_edge, CANONICAL_ALL_8_ROLES),
                "F17 anchor_sources edge-tts",
            )
            bad_anc_neural = json.loads(json.dumps(clean_anc_dict))
            bad_anc_neural["characters"]["victoria_vance"]["source_voice_name"] = "en-US-GuyNeural"
            _assert_mutant_fails(
                lambda: assert_anchor_sources_clean(bad_anc_neural, CANONICAL_ALL_8_ROLES),
                "F17 anchor_sources en-US-GuyNeural",
            )
            bad_anc_el = json.loads(json.dumps(clean_anc_dict))
            bad_anc_el["characters"]["alistair_finch"]["url"] = "https://api.elevenlabs.io/v1/voices/abc"
            _assert_mutant_fails(
                lambda: assert_anchor_sources_clean(bad_anc_el, CANONICAL_ALL_8_ROLES),
                "F17 anchor_sources api.elevenlabs.io",
            )
            # D1/G6b Mutants 13-18: dynamic cmd list mutations with bogus flags
            dyn_mutants = [
                ("cmd.append bogus", ["cmd.append('--bogus-append')\n"]),
                ("cmd.extend bogus", ["cmd.extend(['--bogus-extend', '1'])\n"]),
                ("cmd += bogus", ["cmd += ['--bogus-aug']\n"]),
                ("cmd = cmd + bogus", ["cmd = cmd + ['--bogus-add']\n"]),
                ("cmd.append f-string bogus", ["x = '1'\n", "cmd.append(f'--bogus-fstr={x}')\n"]),
                ("indirect helper extend", ["extra = ['--bogus-ind']\n", "cmd.extend(extra)\n"]),
            ]
            for lbl, extra_lines in dyn_mutants:
                m_nb = json.loads(json.dumps(append_ok_nb))
                m_nb["cells"][1]["source"] = m_nb["cells"][1]["source"][:-1] + extra_lines + [m_nb["cells"][1]["source"][-1]]
                _assert_mutant_fails(
                    lambda nb=m_nb: oracle_notebook_and_bundle_integrity(
                        notebook_data=nb,
                        launcher_help_flags={"--episodes", "--skip-existing"},
                    ),
                    f"F17 {lbl}",
                )
            return 7, 12 + len(dyn_mutants)

        _record(17, "oracle_notebook_and_bundle_integrity", _f17)

        # 18. oracle_audio_signal_and_atempo_ratio + oracle_corporate_acoustic_spaces_dsp
        def _f18() -> tuple[int, int]:
            w48 = write_sine_wav(tmp_root / "master_48k.wav", 2.0, freq_hz=440.0, sample_rate=48000, channels=2, amplitude=0.5)
            w44 = write_sine_wav(tmp_root / "anchor_44k.wav", 3.2, freq_hz=330.0, sample_rate=44100, channels=1, amplitude=0.5)
            w_slow = write_sine_wav(tmp_root / "slow_25s.wav", 2.5, freq_hz=440.0, sample_rate=48000, channels=2, amplitude=0.5)
            oracle_audio_signal_and_atempo_ratio(
                wav_48k_path=w48,
                wav_anchor_path=w44,
                slow_wav_path=w_slow,
                base_wav_path=w48,
                expected_pitch_hz=440.0,
            )

            # Pure-stdlib synthetic positive controls for corporate acoustic spaces DSP
            dry_mt = write_multitone_wav(
                tmp_root / "dsp_dry_mt.wav", 1.6,
                [(100.0, 0.16), (150.0, 0.16), (1000.0, 0.16), (3200.0, 0.16), (6000.0, 0.16)],
                sample_rate=48000, channels=2,
            )
            phone_mt = write_multitone_wav(
                tmp_root / "dsp_phone_mt.wav", 1.6,
                [(100.0, 0.02), (150.0, 0.04), (1000.0, 0.25), (3200.0, 0.18), (6000.0, 0.02)],
                sample_rate=48000, channels=2,
            )
            inner_mt = write_multitone_wav(
                tmp_root / "dsp_inner_mt.wav", 1.6,
                [(100.0, 0.16), (150.0, 0.21), (1000.0, 0.16), (3200.0, 0.19), (6000.0, 0.16)],
                sample_rate=48000, channels=2,
            )
            dry_burst = write_tone_burst_wav(tmp_root / "dsp_dry_b.wav", burst_s=0.80, silence_s=0.80, channels=2)
            inner_burst = write_tone_burst_wav(tmp_root / "dsp_inner_b.wav", burst_s=0.80, silence_s=0.80, channels=2)
            boardroom_burst = write_tone_burst_wav(
                tmp_root / "dsp_board_b.wav", burst_s=0.80, silence_s=0.80, channels=2,
                echo_taps=((0.018, 0.12), (0.036, 0.06)),
            )
            cavern_burst = write_tone_burst_wav(
                tmp_root / "dsp_cavern_b.wav", burst_s=0.80, silence_s=0.80, channels=2,
                echo_taps=((0.048, 0.20), (0.096, 0.10)),
            )
            vast_hall_burst = write_tone_burst_wav(
                tmp_root / "dsp_vasthall_b.wav", burst_s=0.80, silence_s=0.80, channels=2,
                echo_taps=((0.035, 0.16), (0.075, 0.08)),
            )
            oracle_corporate_acoustic_spaces_dsp(
                dry_mt_wav=dry_mt,
                phone_mt_wav=phone_mt,
                inner_mt_wav=inner_mt,
                boardroom_mt_wav=dry_mt,
                dry_burst_wav=dry_burst,
                inner_burst_wav=inner_burst,
                boardroom_burst_wav=boardroom_burst,
            )

            # Mutant 1: 22050 Hz sample rate
            w_bad_sr = write_sine_wav(tmp_root / "bad_22k.wav", 2.0, sample_rate=22050, channels=2)
            _assert_mutant_fails(
                lambda: oracle_audio_signal_and_atempo_ratio(wav_48k_path=w_bad_sr),
                "F18 22050 Hz sample rate",
            )
            # Mutant 2: silent WAV
            w_silent = write_sine_wav(tmp_root / "silent.wav", 2.0, sample_rate=48000, channels=2, amplitude=0.0)
            _assert_mutant_fails(
                lambda: oracle_audio_signal_and_atempo_ratio(wav_48k_path=w_silent),
                "F18 silent WAV",
            )
            # Mutant 3: 0.80x ratio == 1.00 (no stretch)
            _assert_mutant_fails(
                lambda: oracle_audio_signal_and_atempo_ratio(slow_wav_path=w48, base_wav_path=w48),
                "F18 ratio=1.00 no stretch",
            )
            # Mutant 4: pitch shifted to 352 Hz (naive resample without pitch preservation!)
            w_naive = write_sine_wav(tmp_root / "naive_352.wav", 2.5, freq_hz=352.0, sample_rate=48000, channels=2, amplitude=0.5)
            _assert_mutant_fails(
                lambda: oracle_audio_signal_and_atempo_ratio(
                    slow_wav_path=w_naive,
                    base_wav_path=w48,
                    expected_pitch_hz=440.0,
                ),
                "F18 naive 352Hz pitch drop",
            )
            # Mutant 5: missing ffmpeg binary
            _assert_mutant_fails(
                lambda: oracle_audio_signal_and_atempo_ratio(check_ffmpeg_bin="/nonexistent/ffmpeg_e2e_probe"),
                "F18 missing ffmpeg",
            )
            # B4d Mutant 6: phone_mt == dry_mt (unfiltered bypass)
            _assert_mutant_fails(
                lambda: oracle_corporate_acoustic_spaces_dsp(
                    dry_mt_wav=dry_mt, phone_mt_wav=dry_mt, inner_mt_wav=inner_mt,
                ),
                "F18 DSP unfiltered phone_call bypass",
            )
            # B4d Mutant 7: inner_mt == dry_mt (flat EQ bypass)
            _assert_mutant_fails(
                lambda: oracle_corporate_acoustic_spaces_dsp(
                    dry_mt_wav=dry_mt, phone_mt_wav=phone_mt, inner_mt_wav=dry_mt,
                ),
                "F18 DSP flat inner_monologue bypass",
            )
            # B4d Mutant 8: inner_burst with cavern echo
            _assert_mutant_fails(
                lambda: oracle_corporate_acoustic_spaces_dsp(
                    dry_mt_wav=dry_mt, phone_mt_wav=phone_mt, inner_mt_wav=inner_mt,
                    dry_burst_wav=dry_burst, inner_burst_wav=cavern_burst,
                ),
                "F18 DSP inner_monologue cavern echo",
            )
            # B4d Mutant 9: boardroom_burst == dry_burst (missing early reflections)
            _assert_mutant_fails(
                lambda: oracle_corporate_acoustic_spaces_dsp(
                    dry_mt_wav=dry_mt, phone_mt_wav=phone_mt, inner_mt_wav=inner_mt,
                    dry_burst_wav=dry_burst, boardroom_burst_wav=dry_burst,
                ),
                "F18 DSP dry boardroom missing early reflections",
            )
            # B4d Mutant 10: boardroom_burst with late cavern echo
            _assert_mutant_fails(
                lambda: oracle_corporate_acoustic_spaces_dsp(
                    dry_mt_wav=dry_mt, phone_mt_wav=phone_mt, inner_mt_wav=inner_mt,
                    dry_burst_wav=dry_burst, boardroom_burst_wav=cavern_burst,
                ),
                "F18 DSP boardroom late cavern echo",
            )
            # D4/G6a Mutant 11: vast_hall (35|75ms) burst must NOT pass as boardroom
            _assert_mutant_fails(
                lambda: oracle_corporate_acoustic_spaces_dsp(
                    dry_mt_wav=dry_mt, phone_mt_wav=phone_mt, inner_mt_wav=inner_mt,
                    dry_burst_wav=dry_burst, boardroom_burst_wav=vast_hall_burst,
                ),
                "F18 DSP vast_hall (35|75ms) rejected as boardroom",
            )
            return 2, 11

        _record(18, "oracle_audio_signal_and_atempo_ratio", _f18)

    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    return results


# ---------------------------------------------------------------------------
# Uniform Tier Test Registration & Isolated Workflow Helpers
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class TestCaseSpec:
    test_id: str
    tier: int
    feature_id: str
    title: str
    fn: Callable[[], None]


class TierCollector:
    """Deterministic ordered test registry for e2e_tier*.py modules."""

    def __init__(self, tier: int) -> None:
        self.tier = tier
        self._tests: list[TestCaseSpec] = []
        self._seen: set[str] = set()

    def test(self, test_id: str, feature_id: str, title: str):
        def _decorator(fn: Callable[[], None]) -> Callable[[], None]:
            if test_id in self._seen:
                raise ValueError(f"Duplicate E2E test_id registered: {test_id}")
            self._seen.add(test_id)
            self._tests.append(
                TestCaseSpec(
                    test_id=test_id,
                    tier=self.tier,
                    feature_id=feature_id,
                    title=title,
                    fn=fn,
                )
            )
            return fn

        return _decorator

    @property
    def tests(self) -> list[TestCaseSpec]:
        return list(self._tests)


def load_raw_arsenal_by_id(path: Path = RAW_ARSENAL_JSON) -> dict[str, dict[str, Any]]:
    raw = load_json_file(path, label="arsenal_100_queue.json")
    items = raw if isinstance(raw, list) else raw.get("clips", raw.get("items", []))
    if not isinstance(items, list) or len(items) != 100:
        raise AssertionError(
            f"Raw arsenal {path} expected 100 clips, got {len(items) if isinstance(items, list) else type(items)}"
        )
    out: dict[str, dict[str, Any]] = {}
    for it in items:
        plan = it.get("plan") if isinstance(it.get("plan"), dict) else it
        cid = plan.get("clip_id")
        if not cid or cid in out:
            raise AssertionError(f"Missing or duplicate raw clip_id: {cid!r}")
        out[cid] = it
    return out


def run_validate_cli(
    registry_path: Path,
    cue_sheet_path: Path,
    *,
    require_locked_voices: bool = True,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None]:
    args = [
        "validate",
        "--registry",
        str(registry_path),
        "--cue-sheet",
        str(cue_sheet_path),
    ]
    if require_locked_voices:
        args.append("--require-locked-voices")
    proc = run_pipeline_cli(args, timeout=60)
    payload: dict[str, Any] | None = None
    if (proc.stdout or "").strip():
        try:
            payload = parse_last_json_object(proc.stdout)
        except AssertionError:
            payload = None
    return proc, payload


def _unlink_generated_e001_files(out_dir: Path) -> None:
    """Remove pre-copied AUDITION_GLOBAL_EDGE / E001_V* outputs while preserving rubric docs."""
    if not out_dir.is_dir():
        return
    for pattern in (
        "AUDITION_GLOBAL_EDGE*.json",
        "AUDITION_GLOBAL_EDGE*.md",
        "E001_V*.json",
        "E001_V*.md",
    ):
        for old_f in out_dir.glob(pattern):
            old_f.unlink()


def _script_uses_argparse(script_path: Path) -> bool:
    """Statically inspect a script without executing it to check if it declares argparse / out-dir flags."""
    src = script_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return bool(re.search(r"\b(?:argparse|ArgumentParser|add_argument)\b|--out(?:put)?-dir", src))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name == "argparse" for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom) and node.module == "argparse":
            return True
        if isinstance(node, ast.Name) and node.id == "ArgumentParser":
            return True
        if isinstance(node, ast.Attribute) and node.attr in ("ArgumentParser", "add_argument"):
            return True
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in ("--out-dir", "--output-dir"):
                return True
    return False


def run_build_e001_isolated(tmp_dir: Path) -> tuple[subprocess.CompletedProcess[str], Path]:
    """Execute build_e001_variants.py strictly inside an isolated tmp_dir copy so live tracked
    repository files are NEVER executed against or mutated (not even during --help probing)."""
    require_file(SCRIPT_BUILD_E001, label="build_e001_variants.py")
    require_dir(GLOBAL_EDGE_ROOT, label="projects/global_edge")
    require_dir(SRC_ROOT, label="src")

    iso_repo = tmp_dir / "iso_repo"
    shutil.copytree(
        GLOBAL_EDGE_ROOT,
        iso_repo / "projects" / "global_edge",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    shutil.copytree(
        SRC_ROOT,
        iso_repo / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    iso_out_dir = iso_repo / "projects" / "global_edge" / "02_分集广播剧台本"
    _unlink_generated_e001_files(iso_out_dir)

    iso_script = iso_repo / "projects" / "global_edge" / "scripts" / "build_e001_variants.py"
    expected_live_script = GLOBAL_EDGE_ROOT / "scripts" / "build_e001_variants.py"
    if SCRIPT_BUILD_E001.resolve() != expected_live_script.resolve():
        iso_script.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCRIPT_BUILD_E001, iso_script)

    env = dict(os.environ)
    env["PYTHONPATH"] = str(iso_repo / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    # Only probe --help on iso_script (never live tree!) and only if static inspection finds argparse/out-dir
    if _script_uses_argparse(iso_script):
        help_proc = subprocess.run(
            [sys.executable, str(iso_script), "--help"],
            cwd=str(iso_repo),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        help_text = (help_proc.stdout or "") + "\n" + (help_proc.stderr or "")
        help_flags = set(re.findall(r"--[a-zA-Z0-9][a-zA-Z0-9_-]*", help_text))
        for out_flag in ("--out-dir", "--output-dir"):
            if help_proc.returncode == 0 and out_flag in help_flags:
                built_dir = tmp_dir / "built_e001"
                built_dir.mkdir(parents=True, exist_ok=True)
                proc = subprocess.run(
                    [sys.executable, str(iso_script), out_flag, str(built_dir)],
                    cwd=str(iso_repo),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                return proc, built_dir
        _unlink_generated_e001_files(iso_out_dir)

    # Buffett-style no-argparse (or no --out-dir) compiler: execute inside iso_repo directly
    proc = subprocess.run(
        [sys.executable, str(iso_script)],
        cwd=str(iso_repo),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc, iso_out_dir

