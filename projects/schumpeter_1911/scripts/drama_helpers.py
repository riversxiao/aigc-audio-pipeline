"""Shared cue-sheet builder helpers for《1911维也纳风暴：〈经济发展理论〉创新剧》."""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from aigc_audio_pipeline.models import ActMusicSpec, TimelineCue  # noqa: E402
from aigc_audio_pipeline.polyphones import compute_tts_text_override  # noqa: E402
from ost_and_motifs import SCHUMPETER_1911_OST, SCHUMPETER_SONIC_MOTIFS  # noqa: E402

PROJECT_ALLOWED_ACOUSTIC_SPACES: frozenset[str] = frozenset({
    "dry",
    "vintage_study",
    "studio_warm",
    "vast_hall",
})


def dlg(
    cue_id: str,
    act_id: str,
    role_id: str,
    speaker_name: str,
    text: str,
    *,
    stability: float = 0.5,
    acoustic_space: str = "studio_warm",
    gap_after_s: float = 0.26,
    director_note: str = "",
) -> TimelineCue:
    if acoustic_space not in PROJECT_ALLOWED_ACOUSTIC_SPACES:
        raise ValueError(
            f"[{cue_id}] acoustic_space={acoustic_space!r} not in {sorted(PROJECT_ALLOWED_ACOUSTIC_SPACES)}"
        )
    tts_over = compute_tts_text_override(text, domain="schumpeter_1911")
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="dialogue",
        role_id=role_id,
        speaker_name=speaker_name,
        language_code="zh",
        text=text,
        tts_text=tts_over or "",
        stability=stability,
        acoustic_space=acoustic_space,
        gap_after_s=gap_after_s,
        director_note=director_note,
    )


def motif(
    cue_id: str,
    act_id: str,
    motif_id: str,
    *,
    placement: str = "sequential",
    gap_after_s: float = 0.22,
    gain_db: float = -2.0,
    director_note: str = "",
) -> TimelineCue:
    spec = SCHUMPETER_SONIC_MOTIFS[motif_id]
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="sfx",
        motif_id=motif_id,
        sfx_prompt=str(spec["sfx_prompt"]),
        duration_seconds=float(spec["duration_seconds"]),
        placement=placement,
        gap_after_s=gap_after_s,
        gain_db=gain_db,
        director_note=director_note,
    )


def sfx(
    cue_id: str,
    act_id: str,
    prompt: str,
    *,
    duration_seconds: float = 2.6,
    placement: str = "sequential",
    gap_after_s: float = 0.22,
    gain_db: float = -2.0,
    director_note: str = "",
) -> TimelineCue:
    if not prompt.strip().endswith(", pure foley, no human voice"):
        raise ValueError(f"[{cue_id}] SFX prompt must end with ', pure foley, no human voice': {prompt!r}")
    return TimelineCue(
        cue_id=cue_id,
        act_id=act_id,
        kind="sfx",
        sfx_prompt=prompt,
        duration_seconds=duration_seconds,
        placement=placement,
        gap_after_s=gap_after_s,
        gain_db=gain_db,
        director_note=director_note,
    )


def act(
    act_id: str,
    title: str,
    ost_key: str,
    *,
    bgm_duration_s: float = 75.0,
    bgm_gain_speech: float = 0.11,
    bgm_gain_gap: float = 0.34,
) -> ActMusicSpec:
    return ActMusicSpec(
        act_id=act_id,
        title=title,
        bgm_prompt=SCHUMPETER_1911_OST[ost_key],
        bgm_duration_s=bgm_duration_s,
        bgm_gain_speech=bgm_gain_speech,
        bgm_gain_gap=bgm_gain_gap,
    )
