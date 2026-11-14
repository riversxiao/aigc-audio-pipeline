"""Data contracts, Playbook hard-rule validators, and persistent casting registry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Any, Literal

ALLOWED_V3_STABILITIES: tuple[float, ...] = (0.0, 0.5, 1.0)
ALLOWED_ACOUSTIC_SPACES: tuple[str, ...] = ("dry", "mental_realm", "memory_echo", "vast_hall")
ALLOWED_SFX_PLACEMENTS: tuple[str, ...] = ("sequential", "overlay_next")

_SSML_PATTERN = re.compile(r"<\s*/?\s*(speak|break|prosody|phoneme|emphasis|say-as)\b", re.IGNORECASE)
_BRACKET_TAG_PATTERN = re.compile(r"\[([^\[\]]+)\]")
_CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
_ASCII_TAG_PATTERN = re.compile(r"^[a-z0-9\s,\-']+$")

# Core fallback mapping when a multi-tag or rare tag gets read aloud on Attempt 1
_SIMPLE_TAG_FALLBACKS: dict[str, str] = {
    "dramatically": "dramatic tone",
    "desperately": "crying",
    "mischievously": "laughs",
    "dismissive": "coldly",
    "condescending": "coldly",
    "hoarsely": "sighs",
    "trembling": "crying",
    "fiercely": "angry",
    "coldly": "softly",
    "shouts": "shouting",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def next_append_only_path(directory: Path, stem_prefix: str, suffix: str) -> Path:
    """Return a strictly non-existing versioned file path (Playbook hard rule: never overwrite)."""
    directory.mkdir(parents=True, exist_ok=True)
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    version = 1
    while True:
        candidate = directory / f"{stem_prefix}_v{version:03d}{suffix}"
        if not candidate.exists():
            return candidate
        version += 1


def extract_tags_and_spoken_text(text: str) -> tuple[list[str], str]:
    """Split an eleven_v3 tagged string into (inline_tags, clean_spoken_text)."""
    tags = [m.group(1).strip() for m in _BRACKET_TAG_PATTERN.finditer(text)]
    spoken = _BRACKET_TAG_PATTERN.sub("", text)
    spoken = re.sub(r"\s+", " ", spoken).strip()
    return tags, spoken


def simplify_inline_tags(text: str) -> str:
    """Simplify inline audio tags for the single permitted QA retry."""
    tags, spoken = extract_tags_and_spoken_text(text)
    if not tags:
        return spoken
    primary = tags[0].lower().strip()
    mapped = _SIMPLE_TAG_FALLBACKS.get(primary, primary)
    # Keep at most one simple leading tag on retry to eliminate tag-reading glitches
    if mapped in {"angry", "crying", "shouting", "whispers", "softly", "laughs", "sighs", "dramatic tone"}:
        return f"[{mapped}] {spoken}"
    return spoken


def validate_v3_dialogue_text(
    text: str,
    stability: float,
    language_code: str = "zh",
    item_label: str = "line",
) -> list[str]:
    """Validate an eleven_v3 dialogue line against all Playbook hard rules.

    Returns a list of validation error strings (empty if valid).
    """
    errors: list[str] = []
    if not text or not text.strip():
        errors.append(f"[{item_label}] Text cannot be empty.")
        return errors

    if stability not in ALLOWED_V3_STABILITIES:
        errors.append(
            f"[{item_label}] Invalid eleven_v3 stability={stability!r}. "
            f"Only discrete values {ALLOWED_V3_STABILITIES} (0.0 Creative, 0.5 Natural, 1.0 Robust) are allowed."
        )

    if _SSML_PATTERN.search(text):
        errors.append(
            f"[{item_label}] SSML tags detected in {text!r}. "
            "SSML is forbidden on eleven_v3; use inline [audio tags] instead."
        )

    # Check balanced square brackets
    depth = 0
    for ch in text:
        if ch == "[":
            depth += 1
            if depth > 1:
                errors.append(f"[{item_label}] Nested '[' brackets in {text!r}.")
                break
        elif ch == "]":
            depth -= 1
            if depth < 0:
                errors.append(f"[{item_label}] Unmatched ']' bracket in {text!r}.")
                break
    if depth != 0:
        errors.append(f"[{item_label}] Unclosed '[' bracket in {text!r}.")

    tags, spoken = extract_tags_and_spoken_text(text)
    for tag in tags:
        if not _ASCII_TAG_PATTERN.match(tag):
            errors.append(
                f"[{item_label}] Inline audio tag [{tag}] must be lowercase English delivery words "
                "(e.g. [coldly], [shouting], [crying], [sighs]) so it is acted, not spoken."
            )

    if not spoken:
        errors.append(f"[{item_label}] Spoken text is empty after stripping [audio tags].")
    elif language_code == "zh" and not _CJK_PATTERN.search(spoken):
        errors.append(f"[{item_label}] Spoken text {spoken!r} contains no Chinese characters under language_code='zh'.")

    return errors


@dataclass
class AuditionRecord:
    recorded_at: str
    voice_id: str
    library_voice_name: str
    sample_text: str
    stability: float
    similarity_boost: float
    local_file: str = ""
    drive_file_id: str = ""
    qa_passed: bool = False
    decision: Literal["candidate", "approved", "rejected"] = "candidate"
    notes: str = ""


@dataclass
class VoiceProfile:
    role_id: str
    display_name: str
    aliases: list[str] = field(default_factory=list)
    tier: Literal["narrator", "protagonist", "core_supporting", "antagonist", "recurring", "future_nested"] = "recurring"
    gender: Literal["male", "female", "neutral"] = "male"
    age_group: str = "young_adult"
    vocal_register: str = ""
    persona_summary: str = ""
    accent_requirement: str = "大陆普通话戏剧配音（严禁港台/美式/澳洲/新加坡飘口音）"
    status: Literal["pending_audition", "auditioning", "locked"] = "pending_audition"
    voice_id: str = ""
    public_owner_id: str = ""
    library_voice_name: str = ""
    default_stability: float = 0.5
    similarity_boost: float = 0.85
    signature_tags: list[str] = field(default_factory=list)
    forbidden_habits: list[str] = field(default_factory=list)
    first_appearance_chapter: int = 1
    appearance_chapters: list[int] = field(default_factory=list)
    audition_line: str = ""
    audition_history: list[AuditionRecord] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceProfile:
        raw = dict(data)
        hist = [AuditionRecord(**r) for r in raw.pop("audition_history", [])]
        return cls(**raw, audition_history=hist)


@dataclass
class SonicMotif:
    motif_id: str
    name: str
    description: str
    sfx_prompt: str
    duration_seconds: float
    prompt_influence: float = 0.55
    loop: bool = False
    cached_file: str = ""
    drive_file_id: str = ""


@dataclass
class VoiceCastingRegistry:
    project_id: str
    project_title: str
    language_code: str = "zh"
    tts_model_id: str = "eleven_v3"
    sfx_model_id: str = "eleven_text_to_sound_v3"
    music_model_id: str = "music_v2_5"
    asr_model_id: str = "scribe_v3"
    updated_at: str = field(default_factory=utc_now_iso)
    drive_audio_root_id: str = ""
    roles: dict[str, VoiceProfile] = field(default_factory=dict)
    sonic_motifs: dict[str, SonicMotif] = field(default_factory=dict)

    def resolve_role(self, role_or_name: str) -> VoiceProfile | None:
        if role_or_name in self.roles:
            return self.roles[role_or_name]
        for profile in self.roles.values():
            if profile.display_name == role_or_name or role_or_name in profile.aliases:
                return profile
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "project_title": self.project_title,
            "language_code": self.language_code,
            "tts_model_id": self.tts_model_id,
            "sfx_model_id": self.sfx_model_id,
            "music_model_id": self.music_model_id,
            "asr_model_id": self.asr_model_id,
            "updated_at": self.updated_at,
            "drive_audio_root_id": self.drive_audio_root_id,
            "roles": {k: asdict(v) for k, v in self.roles.items()},
            "sonic_motifs": {k: asdict(m) for k, m in self.sonic_motifs.items()},
        }

    def save(self, path: Path) -> None:
        self.updated_at = utc_now_iso()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> VoiceCastingRegistry:
        raw = json.loads(path.read_text(encoding="utf-8"))
        roles = {k: VoiceProfile.from_dict(v) for k, v in raw.get("roles", {}).items()}
        motifs = {k: SonicMotif(**v) for k, v in raw.get("sonic_motifs", {}).items()}
        return cls(
            project_id=raw["project_id"],
            project_title=raw["project_title"],
            language_code=raw.get("language_code", "zh"),
            tts_model_id=raw.get("tts_model_id", "eleven_v3"),
            sfx_model_id=raw.get("sfx_model_id", "eleven_text_to_sound_v3"),
            music_model_id=raw.get("music_model_id", "music_v2_5"),
            asr_model_id=raw.get("asr_model_id", "scribe_v3"),
            updated_at=raw.get("updated_at", utc_now_iso()),
            drive_audio_root_id=raw.get("drive_audio_root_id", ""),
            roles=roles,
            sonic_motifs=motifs,
        )


@dataclass
class ActMusicSpec:
    act_id: str
    title: str
    bgm_prompt: str
    bgm_duration_s: float = 60.0
    bgm_gain_speech: float = 0.11
    bgm_gain_gap: float = 0.34
    cached_bgm_file: str = ""


@dataclass
class TimelineCue:
    cue_id: str
    act_id: str
    kind: Literal["dialogue", "sfx"]
    # Dialogue fields
    role_id: str = ""
    speaker_name: str = ""
    text: str = ""
    tts_text: str = ""
    stability: float = 0.5
    similarity_boost: float = 0.85
    acoustic_space: str = "dry"
    # SFX fields
    motif_id: str = ""
    sfx_prompt: str = ""
    duration_seconds: float = 2.5
    prompt_influence: float = 0.55
    loop: bool = False
    placement: str = "sequential"
    gain_db: float = 0.0
    # Shared timing & direction notes
    gap_after_s: float = 0.35
    director_note: str = ""


@dataclass
class EpisodeCueSheet:
    episode_id: str
    chapter_number: int
    title: str
    mode: Literal["immersive_audiobook_drama", "condensed_radio_drama", "audition_pack"] = "immersive_audiobook_drama"
    source_chapter_file: str = ""
    head_pad_s: float = 0.30
    tail_pad_s: float = 1.20
    acts: list[ActMusicSpec] = field(default_factory=list)
    cues: list[TimelineCue] = field(default_factory=list)

    def validate(self, registry: VoiceCastingRegistry | None = None, require_locked_voices: bool = False) -> list[str]:
        errors: list[str] = []
        act_ids = {a.act_id for a in self.acts}
        seen_cue_ids: set[str] = set()

        if not self.cues:
            errors.append(f"[{self.episode_id}] Cue sheet contains 0 cues.")

        for cue in self.cues:
            if cue.cue_id in seen_cue_ids:
                errors.append(f"[{cue.cue_id}] Duplicate cue_id.")
            seen_cue_ids.add(cue.cue_id)

            if self.mode != "audition_pack" and act_ids and cue.act_id not in act_ids:
                errors.append(f"[{cue.cue_id}] Unknown act_id={cue.act_id!r} (known: {sorted(act_ids)}).")

            if cue.gap_after_s < 0.0 or cue.gap_after_s > 10.0:
                errors.append(f"[{cue.cue_id}] gap_after_s={cue.gap_after_s} out of range [0.0, 10.0].")

            if cue.kind == "dialogue":
                if not cue.role_id:
                    errors.append(f"[{cue.cue_id}] Missing role_id on dialogue cue.")
                if cue.acoustic_space not in ALLOWED_ACOUSTIC_SPACES:
                    errors.append(
                        f"[{cue.cue_id}] Unknown acoustic_space={cue.acoustic_space!r}; "
                        f"allowed={ALLOWED_ACOUSTIC_SPACES}."
                    )
                lang = registry.language_code if registry else "zh"
                errors.extend(
                    validate_v3_dialogue_text(
                        cue.text,
                        cue.stability,
                        language_code=lang,
                        item_label=cue.cue_id,
                    )
                )
                if cue.tts_text:
                    errors.extend(
                        validate_v3_dialogue_text(
                            cue.tts_text,
                            cue.stability,
                            language_code=lang,
                            item_label=f"{cue.cue_id}.tts_text",
                        )
                    )
                if registry is not None and cue.role_id:
                    profile = registry.resolve_role(cue.role_id)
                    if profile is None:
                        errors.append(f"[{cue.cue_id}] Role {cue.role_id!r} not found in VoiceCastingRegistry.")
                    elif require_locked_voices and not profile.voice_id:
                        errors.append(
                            f"[{cue.cue_id}] Role {cue.role_id!r} ({profile.display_name}) has no voice_id assigned yet."
                        )

            elif cue.kind == "sfx":
                if cue.placement not in ALLOWED_SFX_PLACEMENTS:
                    errors.append(
                        f"[{cue.cue_id}] Invalid SFX placement={cue.placement!r}; allowed={ALLOWED_SFX_PLACEMENTS}."
                    )
                if not cue.sfx_prompt and not cue.motif_id:
                    errors.append(f"[{cue.cue_id}] SFX cue must specify either sfx_prompt or motif_id.")
                if registry is not None and cue.motif_id and not cue.sfx_prompt:
                    if cue.motif_id not in registry.sonic_motifs:
                        errors.append(f"[{cue.cue_id}] motif_id={cue.motif_id!r} not found in registry.sonic_motifs.")
                if not (0.5 <= cue.duration_seconds <= 30.0):
                    errors.append(
                        f"[{cue.cue_id}] SFX duration_seconds={cue.duration_seconds} must be within [0.5, 30.0]."
                    )
            else:
                errors.append(f"[{cue.cue_id}] Unknown cue kind={cue.kind!r}.")

        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "chapter_number": self.chapter_number,
            "title": self.title,
            "mode": self.mode,
            "source_chapter_file": self.source_chapter_file,
            "head_pad_s": self.head_pad_s,
            "tail_pad_s": self.tail_pad_s,
            "acts": [asdict(a) for a in self.acts],
            "cues": [asdict(c) for c in self.cues],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> EpisodeCueSheet:
        raw = json.loads(path.read_text(encoding="utf-8"))
        acts = [ActMusicSpec(**a) for a in raw.get("acts", [])]
        cues = [TimelineCue(**c) for c in raw.get("cues", [])]
        return cls(
            episode_id=raw["episode_id"],
            chapter_number=int(raw.get("chapter_number", 1)),
            title=raw["title"],
            mode=raw.get("mode", "immersive_audiobook_drama"),
            source_chapter_file=raw.get("source_chapter_file", ""),
            head_pad_s=float(raw.get("head_pad_s", 0.30)),
            tail_pad_s=float(raw.get("tail_pad_s", 1.20)),
            acts=acts,
            cues=cues,
        )
