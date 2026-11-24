"""Natural speech-rate timeline & 3-bus mastering engine (Dialogue + Foreground SFX + Ducked BGM)."""

from __future__ import annotations

from array import array
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import wave
from typing import Any

try:
    import audioop as _audioop
except ImportError:  # pragma: no cover - Python 3.13+ fallback
    _audioop = None  # type: ignore[assignment]

from .elevenlabs_client import probe_duration_seconds
from .models import EpisodeCueSheet, extract_tags_and_spoken_text, next_append_only_path

SAMPLE_RATE = 48000
CHANNELS = 2
_CTRL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass
class ResolvedTimelineItem:
    cue_id: str
    act_id: str
    kind: str
    role_id: str
    start_s: float
    end_s: float
    duration_s: float
    gap_after_s: float
    stem_file: str
    speaker_name: str = ""
    language_code: str = ""
    spoken_text: str = ""
    tagged_text: str = ""
    voice_id: str = ""
    stability: float = 0.5
    qa_passed: bool = True
    duck_under_next: bool = False
    duck_lead_in_s: float = 3.5
    duck_gain: float = 0.15
    duck_tail_out_s: float = 0.80
    playback_rate: float = 1.0
    subtitle_translation: str = ""


def _format_srt_ts(seconds: float) -> str:
    ms_total = max(0, int(round(seconds * 1000)))
    hh = ms_total // 3600000
    rem = ms_total % 3600000
    mm = rem // 60000
    rem %= 60000
    ss = rem // 1000
    ms = rem % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


# Real flagship Chinese podcasts (e.g. 硅谷101) keep all hosts & guests naturally centered
# (mono-in-stereo center imaging) rather than theatrical left/right stage panning.
# Bilingual hybrid chatroom-dramas (e.g. silicon_gossip with host_xiaowei) keep subtle opposing table seating.
_CENTERED_CHINESE_PODCAST_ROLES: frozenset[str] = frozenset({
    "podcast_ensemble",
    "moss_ttsd_ensemble",
    "host_zhiwei",
    "guest_huaiyuan",
    "guest_laozhou",
    "guest_linxi",
    "guest_azhe",
    "guest_sumin",
    "guest_chengfeng",
})
_CHATROOM_ROLE_PAN_HINTS: dict[str, float] = {
    "guest_laozhou": -0.20,
}
_CHATROOM_FALLBACK_PANS: tuple[float, ...] = (-0.12, 0.15, -0.20, 0.20, -0.06, 0.08)


def _compute_chatroom_pan_map(cue_sheet: EpisodeCueSheet) -> dict[str, float]:
    """Return stereo seating pan overrides for `chatroom_table`.

    Flagship Chinese deep podcasts (`ximalaya_hotline` & `MOSS-TTSD` continuous blocks) stay
    strictly centered (`{}`) matching Silicon Valley 101; bilingual theater-chat hybrids
    (e.g. `silicon_gossip` featuring `host_xiaowei`) keep subtle opposing table pan.
    """
    ordered_roles: list[str] = []
    for c in cue_sheet.cues:
        if c.kind == "dialogue" and c.acoustic_space == "chatroom_table" and c.role_id and c.role_id not in ordered_roles:
            ordered_roles.append(c.role_id)
    if len(ordered_roles) < 2:
        return {}
    if set(ordered_roles).issubset(_CENTERED_CHINESE_PODCAST_ROLES):
        return {}
    pan_map: dict[str, float] = {}
    used_signs: list[float] = []
    for idx, rid in enumerate(ordered_roles):
        if rid in _CHATROOM_ROLE_PAN_HINTS:
            p = _CHATROOM_ROLE_PAN_HINTS[rid]
        else:
            p = _CHATROOM_FALLBACK_PANS[idx % len(_CHATROOM_FALLBACK_PANS)]
        if len(ordered_roles) == 2 and idx == 1 and used_signs and (used_signs[0] * p > 0):
            p = -p
        pan_map[rid] = max(-0.28, min(0.28, p))
        used_signs.append(pan_map[rid])
    return pan_map


def condition_dialogue_clip(
    raw_wav: Path,
    conditioned_wav: Path,
    *,
    acoustic_space: str = "dry",
    playback_rate: float = 1.0,
    role_id: str = "",
    stereo_pan: float = 0.0,
) -> Path:
    """Condition a 48kHz dialogue clip: rumble filter, optional pitch-preserving tempo, space, leveling & table pan."""
    if isinstance(playback_rate, bool) or not isinstance(playback_rate, (int, float)):
        raise ValueError(
            f"playback_rate={playback_rate!r} must be a finite numeric value within [0.5, 2.0]."
        )
    rate = float(playback_rate)
    if not math.isfinite(rate) or not (0.5 <= rate <= 2.0):
        raise ValueError(
            f"playback_rate={playback_rate!r} out of supported FFmpeg atempo range [0.5, 2.0]."
        )

    conditioned_wav.parent.mkdir(parents=True, exist_ok=True)
    raw_dur = probe_duration_seconds(raw_wav)
    apply_tempo = abs(rate - 1.0) > 1e-3
    effective_dur = (raw_dur / rate) if apply_tempo else raw_dur

    filters: list[str] = [
        "aformat=sample_rates=48000:channel_layouts=stereo",
        "highpass=f=75",
    ]
    if apply_tempo:
        # Pitch-preserving WSOLA time-scale BEFORE acoustic filters & loudness leveling
        filters.append(f"atempo={rate:.3f}")

    if acoustic_space == "mental_realm":
        # Subtle ancient void / mental-world early reflections without muddying diction
        filters.append("aecho=0.85:0.82:48|96:0.20|0.10")
        filters.append("apad=pad_dur=0.18")
    elif acoustic_space == "memory_echo":
        filters.append("highpass=f=180,lowpass=f=5500")
        filters.append("aecho=0.85:0.80:65|130:0.24|0.12")
        filters.append("apad=pad_dur=0.20")
    elif acoustic_space == "vast_hall":
        filters.append("aecho=0.88:0.85:35|75:0.16|0.08")
        filters.append("apad=pad_dur=0.12")
    elif acoustic_space == "studio_warm":
        # Warm broadcast condenser podcast intimacy without room echo
        filters.append("equalizer=f=175:t=q:w=1.2:g=1.2,equalizer=f=3600:t=q:w=1.4:g=0.8")
    elif acoustic_space == "chatroom_table":
        # Silicon Valley 101-grade close-mic podcast mastering: clean sub-rumble roll-off,
        # warm vocal body, subtle de-box mid dip, crisp clarity & smooth broadcast glue
        filters.append(
            "highpass=f=80,equalizer=f=150:t=q:w=1.2:g=0.8,"
            "equalizer=f=320:t=q:w=1.5:g=-1.1,equalizer=f=3200:t=q:w=1.4:g=0.9,"
            "acompressor=threshold=-18dB:ratio=2.2:attack=10:release=85"
        )
    elif acoustic_space == "vintage_study":
        # Prime-age Omaha / PBS studio close-mic warmth (crisp articulation, zero analog tape hiss or echo)
        filters.append("equalizer=f=220:t=q:w=1.2:g=0.9,lowpass=f=9600")
    elif acoustic_space == "inner_monologue":
        # Dry intimate proximity (House of Cards aside, zero cavern echo)
        filters.append("equalizer=f=150:t=q:w=1.2:g=1.8,equalizer=f=3200:t=q:w=1.4:g=0.9")
    elif acoustic_space == "boardroom":
        # Tight glass-room early reflection (no trailing apad so negative-gap crosstalk stays tight)
        filters.append("aecho=0.88:0.86:18|36:0.12|0.06")
    elif acoustic_space == "phone_call":
        # Clean telecom voiceband bandpass + gentle dynamics leveling
        filters.append("highpass=f=300,lowpass=f=3400,acompressor=threshold=-18dB:ratio=3:attack=5:release=60")
    elif acoustic_space == "livestream_mic":
        # Crisp modern streaming/voice-chat condenser presence (slightly compressed, intimate forward mids)
        filters.append("highpass=f=100,equalizer=f=2800:t=q:w=1.3:g=1.8,acompressor=threshold=-18dB:ratio=2.4:attack=8:release=80")

    # Tame slight low-mid boxiness on legacy guest_laozhou clips when rendered in studio spaces
    if role_id == "guest_laozhou" and acoustic_space in ("chatroom_table", "studio_warm"):
        filters.append("equalizer=f=260:t=q:w=1.4:g=-2.0,equalizer=f=500:t=q:w=1.6:g=-1.2")

    if effective_dur >= 1.4:
        if acoustic_space == "chatroom_table":
            # Tight flagship Chinese podcast loudness (-15 LUFS, LRA 5 LU; matching 硅谷101's -14.4 LUFS / 3-4.5 LU)
            filters.append("loudnorm=I=-15:TP=-1.5:LRA=5")
        else:
            # EBU R128 / cinema radio-drama broadcast loudness target (-16 LUFS, wider cinematic dynamic range)
            filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
    else:
        # Very short gasps/exclamations (<1.4s): avoid loudnorm over-amplifying breath noise
        filters.append("alimiter=limit=0.84:level=disabled")

    # Optional equal-power stereo pan (0.0 for natural center-imaged podcasts)
    pan_clamped = max(-0.35, min(0.35, float(stereo_pan)))
    if abs(pan_clamped) > 1e-4:
        l_gain = min(1.18, math.sqrt(1.0 - pan_clamped))
        r_gain = min(1.18, math.sqrt(1.0 + pan_clamped))
        filters.append(f"pan=stereo|c0={l_gain:.4f}*c0|c1={r_gain:.4f}*c1")

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(raw_wav),
        "-af",
        ",".join(filters),
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        str(CHANNELS),
        "-c:a",
        "pcm_s16le",
        str(conditioned_wav),
    ]
    subprocess.run(cmd, check=True)
    return conditioned_wav


def condition_sfx_clip(raw_wav: Path, conditioned_wav: Path, *, gain_db: float = 0.0) -> Path:
    """Prepare a 48kHz stereo foreground SFX clip (never ducked by dialogue)."""
    conditioned_wav.parent.mkdir(parents=True, exist_ok=True)
    filters: list[str] = ["aformat=sample_rates=48000:channel_layouts=stereo"]
    if abs(gain_db) > 0.01:
        filters.append(f"volume={gain_db:.2f}dB")
    filters.append("alimiter=limit=0.88:level=disabled")
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(raw_wav),
        "-af",
        ",".join(filters),
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        str(CHANNELS),
        "-c:a",
        "pcm_s16le",
        str(conditioned_wav),
    ]
    subprocess.run(cmd, check=True)
    return conditioned_wav


def fit_bgm_to_duration(raw_bgm_wav: Path, target_duration_s: float, output_wav: Path) -> Path:
    """Loop-crossfade or trim an instrumental BGM bed to cover `target_duration_s` at 48kHz stereo."""
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    src_dur = probe_duration_seconds(raw_bgm_wav)
    target_duration_s = max(1.0, target_duration_s)

    if src_dur >= target_duration_s + 0.05:
        fade_out_st = max(0.0, target_duration_s - 1.2)
        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(raw_bgm_wav),
            "-t",
            f"{target_duration_s:.3f}",
            "-af",
            f"afade=t=in:st=0:d=0.6,afade=t=out:st={fade_out_st:.3f}:d=1.2",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            str(CHANNELS),
            "-c:a",
            "pcm_s16le",
            str(output_wav),
        ]
        subprocess.run(cmd, check=True)
        return output_wav

    # Need seamless looping to cover target_duration_s
    loops_needed = int(math.ceil(target_duration_s / max(src_dur, 1.0))) + 1
    fade_out_st = max(0.0, target_duration_s - 1.2)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-stream_loop",
        str(loops_needed),
        "-i",
        str(raw_bgm_wav),
        "-t",
        f"{target_duration_s:.3f}",
        "-af",
        f"afade=t=in:st=0:d=0.6,afade=t=out:st={fade_out_st:.3f}:d=1.2",
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        str(CHANNELS),
        "-c:a",
        "pcm_s16le",
        str(output_wav),
    ]
    subprocess.run(cmd, check=True)
    return output_wav


def _read_stereo_s16(wav_path: Path) -> array:
    with wave.open(str(wav_path), "rb") as wf:
        if wf.getnchannels() != CHANNELS or wf.getsampwidth() != 2 or wf.getframerate() != SAMPLE_RATE:
            raise ValueError(
                f"Expected 48kHz 16-bit stereo WAV, got {wf.getframerate()}Hz "
                f"{wf.getsampwidth()*8}-bit {wf.getnchannels()}ch in {wav_path}"
            )
        raw = wf.readframes(wf.getnframes())
    samples = array("h")
    samples.frombytes(raw)
    return samples


def _write_stereo_s16(wav_path: Path, samples: array) -> Path:
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(samples.tobytes())
    return wav_path


def _mix_into_buffer(buf: array, clip: array, start_frame: int, gain: float = 1.0) -> None:
    """Mix stereo s16 `clip` into `buf` starting at `start_frame` with saturation protection."""
    start_idx = max(0, start_frame * CHANNELS)
    end_idx = min(len(buf), start_idx + len(clip))
    count = end_idx - start_idx
    if count <= 0:
        return
    if _audioop is not None:
        buf_bytes = memoryview(buf)[start_idx:end_idx].tobytes()
        clip_bytes = memoryview(clip)[:count].tobytes()
        if abs(gain - 1.0) >= 1e-6:
            clip_bytes = _audioop.mul(clip_bytes, 2, gain)
        mixed_bytes = _audioop.add(buf_bytes, clip_bytes, 2)
        mixed_arr = array("h")
        mixed_arr.frombytes(mixed_bytes)
        buf[start_idx:end_idx] = mixed_arr
        return

    if abs(gain - 1.0) < 1e-6:
        for i in range(count):
            val = buf[start_idx + i] + clip[i]
            if val > 32767:
                val = 32767
            elif val < -32768:
                val = -32768
            buf[start_idx + i] = val
    else:
        for i in range(count):
            val = buf[start_idx + i] + int(clip[i] * gain)
            if val > 32767:
                val = 32767
            elif val < -32768:
                val = -32768
            buf[start_idx + i] = val


def _merge_speech_intervals(
    intervals: list[tuple[float, float]],
    bridge_gap_s: float = 0.45,
) -> list[tuple[float, float]]:
    """Merge adjacent speech intervals separated by < `bridge_gap_s` to prevent BGM pumping."""
    if not intervals:
        return []
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    merged: list[tuple[float, float]] = [sorted_iv[0]]
    for st, en in sorted_iv[1:]:
        prev_st, prev_en = merged[-1]
        if st <= prev_en + bridge_gap_s:
            merged[-1] = (prev_st, max(prev_en, en))
        else:
            merged.append((st, en))
    return merged


def apply_voiceover_duck_envelope(
    primary_samples: array,
    *,
    rel_duck_start_s: float,
    rel_duck_end_s: float,
    duck_gain: float = 0.15,
    ramp_down_s: float = 0.40,
    ramp_up_s: float = 0.35,
    tail_gain: float = 0.78,
) -> array:
    """Apply smooth BBC/Netflix documentary simultaneous-translation gain curve to an original English voice clip.

    - `[0, rel_duck_start_s - ramp_down_s]`: `1.0` (full-clarity original English hook).
    - `(rel_duck_start_s - ramp_down_s, rel_duck_start_s)`: half-cosine ramp down from `1.0` -> `duck_gain` (`0.15`).
    - `[rel_duck_start_s, rel_duck_end_s]`: `duck_gain` (`-16.5 dB` warm English documentary bed under Chinese voiceover).
    - If `clip_dur_s > rel_duck_end_s + 0.20s`: half-cosine ramp up to `tail_gain` (`0.78`) for resonant English tail.
    """
    total_frames = len(primary_samples) // CHANNELS
    if total_frames == 0:
        return array("h")

    clip_dur_s = total_frames / SAMPLE_RATE
    has_tail_lift = clip_dur_s > (rel_duck_end_s + 0.20)
    ramp_down_st = max(0.0, rel_duck_start_s - ramp_down_s)

    step_frames = 480  # 10ms control steps at 48kHz
    num_steps = (total_frames + step_frames - 1) // step_frames
    ctrl_gains = [1.0] * (num_steps + 1)

    for step_idx in range(num_steps + 1):
        t = (step_idx * step_frames) / SAMPLE_RATE
        if t <= ramp_down_st:
            g = 1.0
        elif t < rel_duck_start_s:
            alpha = (t - ramp_down_st) / max(rel_duck_start_s - ramp_down_st, 1e-3)
            blend = 0.5 * (1.0 - math.cos(math.pi * alpha))
            g = 1.0 + (duck_gain - 1.0) * blend
        elif not has_tail_lift or t <= rel_duck_end_s:
            g = duck_gain
        elif t < rel_duck_end_s + ramp_up_s:
            alpha = (t - rel_duck_end_s) / max(ramp_up_s, 1e-3)
            blend = 0.5 * (1.0 - math.cos(math.pi * alpha))
            g = duck_gain + (tail_gain - duck_gain) * blend
        else:
            g = tail_gain
        ctrl_gains[step_idx] = g

    if _audioop is not None and len(primary_samples) > 0:
        raw_bytes = primary_samples.tobytes()
        mv = memoryview(raw_bytes)
        bytes_per_frame = CHANNELS * 2
        out_chunks: list[bytes] = []
        for step_idx in range(num_steps):
            b_start = step_idx * step_frames * bytes_per_frame
            b_end = min(len(raw_bytes), b_start + step_frames * bytes_per_frame)
            g_mid = 0.5 * (ctrl_gains[step_idx] + ctrl_gains[step_idx + 1])
            out_chunks.append(_audioop.mul(mv[b_start:b_end], 2, g_mid))
        out = array("h")
        out.frombytes(b"".join(out_chunks))
        return out

    out = array("h", [0]) * len(primary_samples)
    for step_idx in range(num_steps):
        f_start = step_idx * step_frames
        f_end = min(total_frames, f_start + step_frames)
        g0 = ctrl_gains[step_idx]
        g1 = ctrl_gains[step_idx + 1]
        span = max(1, f_end - f_start)
        dg = (g1 - g0) / span
        g = g0
        for f in range(f_start, f_end):
            idx = f * CHANNELS
            out[idx] = int(primary_samples[idx] * g)
            out[idx + 1] = int(primary_samples[idx + 1] * g)
            g += dg
    return out


def apply_bgm_ducking_envelope(
    bgm_samples: array,
    speech_intervals: list[tuple[float, float]],
    *,
    gain_speech: float = 0.11,
    gain_gap: float = 0.34,
    attack_s: float = 0.30,
    release_s: float = 0.65,
) -> array:
    """Apply smooth ducking curve to BGM bus ONLY (`0.11` under dialogue, `0.34` in gaps)."""
    total_frames = len(bgm_samples) // CHANNELS
    merged = _merge_speech_intervals(speech_intervals, bridge_gap_s=0.45)

    # Compute envelope at 100 Hz control rate (every 480 frames = 10ms) in O(steps + intervals)
    step_frames = 480
    num_steps = (total_frames + step_frames - 1) // step_frames
    ctrl_gains = [gain_gap] * (num_steps + 1)

    iv_start_idx = 0
    n_merged = len(merged)
    for step_idx in range(num_steps + 1):
        t = (step_idx * step_frames) / SAMPLE_RATE
        while iv_start_idx < n_merged and merged[iv_start_idx][1] + release_s < t:
            iv_start_idx += 1
        g = gain_gap
        for j in range(iv_start_idx, n_merged):
            st, en = merged[j]
            if t < st - attack_s:
                break
            if st <= t <= en:
                g = gain_speech
                break
            if st - attack_s <= t < st:
                alpha = (t - (st - attack_s)) / max(attack_s, 1e-3)
                blend = 0.5 * (1.0 - math.cos(math.pi * alpha))
                g = min(g, gain_gap + (gain_speech - gain_gap) * blend)
            elif en < t <= en + release_s:
                alpha = (t - en) / max(release_s, 1e-3)
                blend = 0.5 * (1.0 - math.cos(math.pi * alpha))
                g = min(g, gain_speech + (gain_gap - gain_speech) * blend)
        ctrl_gains[step_idx] = g

    if _audioop is not None and len(bgm_samples) > 0:
        raw_bytes = bgm_samples.tobytes()
        mv = memoryview(raw_bytes)
        bytes_per_frame = CHANNELS * 2
        out_chunks: list[bytes] = []
        for step_idx in range(num_steps):
            b_start = step_idx * step_frames * bytes_per_frame
            b_end = min(len(raw_bytes), b_start + step_frames * bytes_per_frame)
            g_mid = 0.5 * (ctrl_gains[step_idx] + ctrl_gains[step_idx + 1])
            out_chunks.append(_audioop.mul(mv[b_start:b_end], 2, g_mid))
        out = array("h")
        out.frombytes(b"".join(out_chunks))
        return out

    out = array("h", [0]) * len(bgm_samples)
    for step_idx in range(num_steps):
        f_start = step_idx * step_frames
        f_end = min(total_frames, f_start + step_frames)
        g0 = ctrl_gains[step_idx]
        g1 = ctrl_gains[step_idx + 1]
        span = max(1, f_end - f_start)
        dg = (g1 - g0) / span
        g = g0
        for f in range(f_start, f_end):
            idx = f * CHANNELS
            out[idx] = int(bgm_samples[idx] * g)
            out[idx + 1] = int(bgm_samples[idx + 1] * g)
            g += dg
    return out


def render_audition_reel(
    audition_items: list[dict[str, Any]],
    output_dir: Path,
    stem_prefix: str,
    gap_between_s: float = 0.80,
) -> dict[str, Path]:
    """Assemble dialogue-only audition clips into a clean review reel (Playbook Step 1 & Step 3)."""
    conditioned_clips: list[tuple[dict[str, Any], array, float]] = []
    temp_dir = output_dir / "_conditioned_audition"
    temp_dir.mkdir(parents=True, exist_ok=True)

    total_dur_s = 0.30
    for idx, item in enumerate(audition_items):
        raw_wav = Path(item["wav_path"])
        cond_wav = temp_dir / f"aud_{idx:03d}.wav"
        condition_dialogue_clip(
            raw_wav,
            cond_wav,
            acoustic_space=str(item.get("acoustic_space", "dry") or "dry"),
            playback_rate=item.get("playback_rate", 1.0),
        )
        samples = _read_stereo_s16(cond_wav)
        dur_s = (len(samples) // CHANNELS) / SAMPLE_RATE
        conditioned_clips.append((item, samples, dur_s))
        total_dur_s += dur_s + gap_between_s
    total_dur_s += 0.50

    total_frames = int(math.ceil(total_dur_s * SAMPLE_RATE))
    reel_buf = array("h", [0]) * (total_frames * CHANNELS)
    cursor_s = 0.30
    timeline_records: list[dict[str, Any]] = []
    for item, samples, dur_s in conditioned_clips:
        start_frame = int(round(cursor_s * SAMPLE_RATE))
        _mix_into_buffer(reel_buf, samples, start_frame, gain=1.0)
        rec = dict(item)
        rec["wav_path"] = str(item["wav_path"])
        rec["reel_start_s"] = round(cursor_s, 3)
        rec["reel_end_s"] = round(cursor_s + dur_s, 3)
        timeline_records.append(rec)
        cursor_s += dur_s + gap_between_s

    wav_out = next_append_only_path(output_dir, stem_prefix, ".wav")
    mp3_out = wav_out.with_suffix(".mp3")
    json_out = wav_out.with_suffix(".json")

    _write_stereo_s16(wav_out, reel_buf)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(wav_out),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(mp3_out),
        ],
        check=True,
    )
    json_out.write_text(
        json.dumps(
            {
                "kind": "audition_reel",
                "total_duration_s": round(total_dur_s, 3),
                "wav_file": str(wav_out),
                "mp3_file": str(mp3_out),
                "items": timeline_records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"wav": wav_out, "mp3": mp3_out, "manifest": json_out}


def _resolve_speaker_prefix(item: ResolvedTimelineItem, registry: Any | None) -> str:
    if item.role_id == "narrator":
        return ""
    if item.speaker_name:
        return f"【{item.speaker_name}】"
    prof = registry.resolve_role(item.role_id) if registry is not None else None
    speaker_label = prof.display_name if prof is not None else item.role_id
    return f"【{speaker_label}】"


def _excerpt_opening_english(text: str, max_chars: int = 92) -> str:
    s = text.strip()
    if len(s) <= max_chars:
        return s
    cut = s[:max_chars].rsplit(" ", 1)[0]
    return f"{cut}…"


def find_natural_duck_pause_s(
    stereo_samples: array,
    *,
    target_s: float,
    dur_s: float,
    sample_rate: int = SAMPLE_RATE,
) -> float:
    """Snap `target_s` to the cleanest inter-sentence breath pause (`~180ms` RMS valley) if one exists."""
    fallback = min(float(target_s), max(0.0, dur_s * 0.85))
    if dur_s < 4.5 or len(stereo_samples) < sample_rate * CHANNELS * 3:
        return fallback

    win_frames = max(1, int(0.18 * sample_rate))
    step_frames = max(1, int(0.04 * sample_rate))
    lo_s = max(2.6, min(target_s - 1.2, dur_s * 0.55))
    hi_s = min(dur_s * 0.85, max(lo_s + 0.5, target_s + 3.6))
    lo_f = int(lo_s * sample_rate)
    hi_f = int(hi_s * sample_rate) - win_frames
    if hi_f <= lo_f:
        return fallback

    raw_mv = memoryview(stereo_samples).cast("B")
    bytes_per_frame = CHANNELS * 2
    if _audioop is not None:
        overall_rms = float(_audioop.rms(raw_mv.tobytes(), 2))
    else:
        overall_rms = 3000.0
    if overall_rms < 120.0:
        return fallback

    best_score = float("inf")
    best_rms = overall_rms
    best_center_s = fallback
    for f0 in range(lo_f, hi_f + 1, step_frames):
        b0 = f0 * bytes_per_frame
        b1 = (f0 + win_frames) * bytes_per_frame
        if _audioop is not None:
            w_rms = float(_audioop.rms(raw_mv[b0:b1].tobytes(), 2))
        else:
            s0 = f0 * CHANNELS
            s1 = (f0 + win_frames) * CHANNELS
            seg = stereo_samples[s0:s1:4]
            w_rms = math.sqrt(sum(int(x) * int(x) for x in seg) / max(1, len(seg)))
        center_s = (f0 + 0.5 * win_frames) / sample_rate
        # Prefer genuine silence valleys (< 28% of speech RMS) with mild proximity preference to target_s
        dist_penalty = 1.0 + 0.06 * abs(center_s - target_s)
        score = w_rms * dist_penalty
        if score < best_score:
            best_score = score
            best_rms = w_rms
            best_center_s = center_s

    if best_rms <= 0.30 * overall_rms:
        return round(best_center_s, 3)
    return fallback


def master_episode_three_bus(
    cue_sheet: EpisodeCueSheet,
    cue_audio_map: dict[str, Path],
    act_bgm_map: dict[str, Path],
    output_dir: Path,
    *,
    cue_meta_map: dict[str, dict[str, Any]] | None = None,
    preconditioned_samples: dict[str, array] | None = None,
    registry: Any | None = None,
    workers: int = 4,
    clean_work_dir: bool = False,
    stem_prefix: str | None = None,
    mp3_bitrate: str = "192k",
) -> dict[str, Any]:
    """Assemble natural-rate Dialogue Bus + Foreground SFX Bus + Ducked Per-Act BGM Bus."""
    work_dir = output_dir / f"_stems_work_{cue_sheet.episode_id}"
    work_dir.mkdir(parents=True, exist_ok=True)
    cue_meta_map = cue_meta_map or {}

    # 1. Condition each cue clip concurrently & compute exact natural timeline
    chatroom_pan_map = _compute_chatroom_pan_map(cue_sheet)

    def _cond_one(cue: Any) -> tuple[str, array]:
        if preconditioned_samples and cue.cue_id in preconditioned_samples:
            return cue.cue_id, preconditioned_samples[cue.cue_id]
        raw_path = cue_audio_map[cue.cue_id]
        cond_path = work_dir / f"{cue.cue_id}_cond.wav"
        if cue.kind == "dialogue":
            pan_val = chatroom_pan_map.get(cue.role_id, 0.0) if cue.acoustic_space == "chatroom_table" else 0.0
            condition_dialogue_clip(
                raw_path,
                cond_path,
                acoustic_space=cue.acoustic_space,
                playback_rate=getattr(cue, "playback_rate", 1.0),
                role_id=cue.role_id,
                stereo_pan=pan_val,
            )
        else:
            condition_sfx_clip(raw_path, cond_path, gain_db=cue.gain_db)
        return cue.cue_id, _read_stereo_s16(cond_path)

    conditioned_map: dict[str, array] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for cid, samples in pool.map(_cond_one, cue_sheet.cues):
            conditioned_map[cid] = samples

    cursor_s = cue_sheet.head_pad_s
    max_end_s = cursor_s
    resolved_items: list[ResolvedTimelineItem] = []
    act_spans: dict[str, list[float]] = {}
    active_duck_bed_end_s = 0.0

    for idx, cue in enumerate(cue_sheet.cues):
        raw_path = cue_audio_map.get(cue.cue_id, work_dir / f"{cue.cue_id}_recovered.wav")
        samples = conditioned_map[cue.cue_id]
        dur_s = (len(samples) // CHANNELS) / SAMPLE_RATE

        start_s = cursor_s
        end_s = start_s + dur_s
        max_end_s = max(max_end_s, end_s)

        if cue.act_id:
            if cue.act_id not in act_spans:
                act_spans[cue.act_id] = [start_s, end_s]
            else:
                act_spans[cue.act_id][0] = min(act_spans[cue.act_id][0], start_s)
                act_spans[cue.act_id][1] = max(act_spans[cue.act_id][1], end_s)

        meta = cue_meta_map.get(cue.cue_id, {})
        _, clean_spoken = extract_tags_and_spoken_text(cue.text) if cue.kind == "dialogue" else ([], "")
        has_valid_duck_target = (
            cue.kind == "dialogue"
            and bool(getattr(cue, "duck_under_next", False))
            and idx + 1 < len(cue_sheet.cues)
            and cue_sheet.cues[idx + 1].kind == "dialogue"
        )
        effective_lead_in_s = (
            find_natural_duck_pause_s(samples, target_s=float(getattr(cue, "duck_lead_in_s", 3.5)), dur_s=dur_s)
            if has_valid_duck_target
            else float(getattr(cue, "duck_lead_in_s", 3.5))
        )

        raw_cue_rate = getattr(cue, "playback_rate", 1.0)
        resolved_rate = (
            float(raw_cue_rate)
            if isinstance(raw_cue_rate, (int, float))
            and not isinstance(raw_cue_rate, bool)
            and math.isfinite(float(raw_cue_rate))
            else 1.0
        )
        raw_sub_tr = getattr(cue, "subtitle_translation", "")
        resolved_sub_tr = raw_sub_tr if isinstance(raw_sub_tr, str) else ""

        resolved_items.append(
            ResolvedTimelineItem(
                cue_id=cue.cue_id,
                act_id=cue.act_id,
                kind=cue.kind,
                role_id=cue.role_id,
                start_s=round(start_s, 4),
                end_s=round(end_s, 4),
                duration_s=round(dur_s, 4),
                gap_after_s=cue.gap_after_s,
                stem_file=str(raw_path),
                speaker_name=getattr(cue, "speaker_name", ""),
                language_code=getattr(cue, "language_code", ""),
                spoken_text=clean_spoken,
                tagged_text=cue.text,
                voice_id=str(meta.get("voice_id", "")),
                stability=cue.stability,
                qa_passed=bool(meta.get("qa_passed", True)),
                duck_under_next=has_valid_duck_target,
                duck_lead_in_s=effective_lead_in_s,
                duck_gain=float(getattr(cue, "duck_gain", 0.15)),
                duck_tail_out_s=float(getattr(cue, "duck_tail_out_s", 0.80)),
                playback_rate=resolved_rate,
                subtitle_translation=resolved_sub_tr,
            )
        )

        if cue.kind == "sfx" and cue.placement == "overlay_next":
            # Optional pre-offset before dialogue enters while SFX continues underneath (never backwards/negative)
            cursor_s = max(0.0, start_s, start_s + cue.gap_after_s)
        elif has_valid_duck_target:
            # Documentary simultaneous-translation: play solo English sentence up to natural pause, then start interpreter
            active_duck_bed_end_s = end_s
            cursor_s = max(0.0, start_s + max(0.0, effective_lead_in_s))
        else:
            effective_end_s = max(end_s, active_duck_bed_end_s)
            active_duck_bed_end_s = 0.0
            min_next_start = (
                start_s + min(dur_s * 0.5, 0.05)
                if cue.kind == "dialogue" and dur_s > 0
                else start_s
            )
            cursor_s = max(0.0, min_next_start, effective_end_s + cue.gap_after_s)

    total_duration_s = max(cursor_s, max_end_s) + cue_sheet.tail_pad_s
    total_frames = int(math.ceil(total_duration_s * SAMPLE_RATE))

    # 2. Render Bus A (Dialogue, with documentary simultaneous-translation ducking when enabled) & Bus B (Foreground SFX)
    dialogue_buf = array("h", [0]) * (total_frames * CHANNELS)
    sfx_buf = array("h", [0]) * (total_frames * CHANNELS)
    speech_intervals: list[tuple[float, float]] = []

    for idx, item in enumerate(resolved_items):
        samples = conditioned_map[item.cue_id]
        start_frame = int(round(item.start_s * SAMPLE_RATE))
        if item.kind == "dialogue":
            if item.duck_under_next and idx + 1 < len(resolved_items) and resolved_items[idx + 1].kind == "dialogue":
                next_it = resolved_items[idx + 1]
                samples = apply_voiceover_duck_envelope(
                    samples,
                    rel_duck_start_s=max(0.0, next_it.start_s - item.start_s),
                    rel_duck_end_s=max(0.0, next_it.end_s - item.start_s),
                    duck_gain=item.duck_gain,
                )
            _mix_into_buffer(dialogue_buf, samples, start_frame, gain=1.0)
            speech_intervals.append((item.start_s, item.end_s))
        else:
            _mix_into_buffer(sfx_buf, samples, start_frame, gain=1.0)

    # 3. Render Bus C (Per-Act BGM Bed with dialogue-only ducking; supports silent/dry chatroom acts!)
    bgm_ducked_buf = array("h", [0]) * (total_frames * CHANNELS)
    active_acts = [a for a in cue_sheet.acts if a.act_id in act_spans]
    for idx, act in enumerate(active_acts):
        is_silent_act = (
            act.act_id not in act_bgm_map
            or not (act.bgm_prompt or "").strip()
            or (act.bgm_gain_speech <= 1e-4 and act.bgm_gain_gap <= 1e-4)
        )
        if is_silent_act:
            continue
        act_st = 0.0 if idx == 0 else max(0.0, act_spans[act.act_id][0] - 0.6)
        if idx == len(active_acts) - 1:
            act_en = total_duration_s
        else:
            next_act = active_acts[idx + 1]
            next_st = act_spans[next_act.act_id][0]
            next_is_silent = (
                next_act.act_id not in act_bgm_map
                or not (next_act.bgm_prompt or "").strip()
                or (next_act.bgm_gain_speech <= 1e-4 and next_act.bgm_gain_gap <= 1e-4)
            )
            # Clean fade-out right before a silent dry chatroom act; smooth +0.6s crossfade into another scored act
            act_en = min(total_duration_s, next_st + (0.15 if next_is_silent else 0.6))
        span_dur = max(1.0, act_en - act_st)

        fitted_wav = work_dir / f"bgm_{act.act_id}_fitted.wav"
        fit_bgm_to_duration(act_bgm_map[act.act_id], span_dur, fitted_wav)
        raw_act_samples = _read_stereo_s16(fitted_wav)

        # Shift speech intervals relative to act_st
        rel_speech = [
            (max(0.0, st - act_st), min(span_dur, en - act_st))
            for st, en in speech_intervals
            if en > act_st and st < act_en
        ]
        ducked_act_samples = apply_bgm_ducking_envelope(
            raw_act_samples,
            rel_speech,
            gain_speech=act.bgm_gain_speech,
            gain_gap=act.bgm_gain_gap,
        )
        _mix_into_buffer(bgm_ducked_buf, ducked_act_samples, int(round(act_st * SAMPLE_RATE)), gain=1.0)

    dialogue_bus_wav = work_dir / "bus_A_dialogue.wav"
    sfx_bus_wav = work_dir / "bus_B_sfx_foreground.wav"
    bgm_bus_wav = work_dir / "bus_C_bgm_ducked.wav"
    _write_stereo_s16(dialogue_bus_wav, dialogue_buf)
    _write_stereo_s16(sfx_bus_wav, sfx_buf)
    _write_stereo_s16(bgm_bus_wav, bgm_ducked_buf)

    # 4. Final true-peak limited master (append-only naming: never overwrite!)
    resolved_prefix = stem_prefix or f"{cue_sheet.episode_id}_master"
    master_wav = next_append_only_path(output_dir, resolved_prefix, ".wav")
    master_mp3 = master_wav.with_suffix(".mp3")
    srt_path = master_wav.with_suffix(".srt")
    manifest_path = master_wav.with_suffix(".json")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(dialogue_bus_wav),
            "-i",
            str(sfx_bus_wav),
            "-i",
            str(bgm_bus_wav),
            "-filter_complex",
            "[0:a][1:a][2:a]amix=inputs=3:duration=longest:normalize=0,alimiter=limit=0.891:attack=5:release=50:level=disabled[out]",
            "-map",
            "[out]",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            str(CHANNELS),
            "-c:a",
            "pcm_s16le",
            str(master_wav),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(master_wav),
            "-c:a",
            "libmp3lame",
            "-b:a",
            mp3_bitrate,
            str(master_mp3),
        ],
        check=True,
    )

    # 5. Export sample-accurate non-overlapping SRT subtitles (with bilingual simultaneous-translation blocks)
    srt_blocks: list[str] = []
    sub_idx = 1
    idx = 0
    while idx < len(resolved_items):
        item = resolved_items[idx]
        if item.kind != "dialogue" or not item.spoken_text:
            idx += 1
            continue

        next_dlg_start: float | None = None
        for look_i in range(idx + 1, len(resolved_items)):
            if resolved_items[look_i].kind == "dialogue" and resolved_items[look_i].spoken_text:
                next_dlg_start = resolved_items[look_i].start_s
                break

        if (
            item.duck_under_next
            and idx + 1 < len(resolved_items)
            and resolved_items[idx + 1].kind == "dialogue"
            and resolved_items[idx + 1].spoken_text
        ):
            next_it = resolved_items[idx + 1]
            en_prefix = _resolve_speaker_prefix(item, registry)
            zh_prefix = _resolve_speaker_prefix(next_it, registry)
            if next_it.start_s > item.start_s + 0.15:
                srt_blocks.append(
                    f"{sub_idx}\n"
                    f"{_format_srt_ts(item.start_s)} --> {_format_srt_ts(next_it.start_s)}\n"
                    f"{en_prefix}{_excerpt_opening_english(item.spoken_text)}\n"
                )
                sub_idx += 1
            pair_end_s = max(item.end_s, next_it.end_s)
            next_after_pair_start: float | None = None
            for look_j in range(idx + 2, len(resolved_items)):
                if resolved_items[look_j].kind == "dialogue" and resolved_items[look_j].spoken_text:
                    next_after_pair_start = resolved_items[look_j].start_s
                    break
            if next_after_pair_start is not None and pair_end_s > next_after_pair_start - 0.01:
                clamped_pair = next_after_pair_start - 0.01
                pair_end_s = (
                    clamped_pair
                    if clamped_pair >= next_it.start_s + 0.05
                    else max(next_it.start_s, next_after_pair_start)
                )
            srt_blocks.append(
                f"{sub_idx}\n"
                f"{_format_srt_ts(next_it.start_s)} --> {_format_srt_ts(pair_end_s)}\n"
                f"{zh_prefix}{next_it.spoken_text}\n"
                f"EN: {item.spoken_text}\n"
            )
            sub_idx += 1
            idx += 2
            continue

        srt_end_s = item.end_s
        if next_dlg_start is not None and srt_end_s > next_dlg_start - 0.01:
            clamped = next_dlg_start - 0.01
            srt_end_s = clamped if clamped >= item.start_s + 0.05 else max(item.start_s, next_dlg_start)

        meta = (cue_meta_map or {}).get(item.cue_id, {})
        sub_segs = meta.get("subtitle_segments") if isinstance(meta, dict) else None
        if isinstance(sub_segs, list) and sub_segs:
            for seg in sub_segs:
                seg_text = str(seg.get("text", "")).strip()
                if not seg_text:
                    continue
                s0 = item.start_s + max(0.0, float(seg.get("start_rel_s", 0.0)))
                s1 = min(srt_end_s, item.start_s + max(0.0, float(seg.get("end_rel_s", item.duration_s))))
                if s1 <= s0 + 0.05:
                    s1 = min(srt_end_s, s0 + 0.25)
                srt_blocks.append(
                    f"{sub_idx}\n"
                    f"{_format_srt_ts(s0)} --> {_format_srt_ts(s1)}\n"
                    f"{seg_text}\n"
                )
                sub_idx += 1
            idx += 1
            continue

        speaker_prefix = _resolve_speaker_prefix(item, registry)
        translation = " ".join(_CTRL_CHAR_RE.sub("", item.subtitle_translation).split())
        text_body = f"{speaker_prefix}{item.spoken_text}\n"
        if translation:
            text_body += f"{translation}\n"
        srt_blocks.append(
            f"{sub_idx}\n"
            f"{_format_srt_ts(item.start_s)} --> {_format_srt_ts(srt_end_s)}\n"
            f"{text_body}"
        )
        sub_idx += 1
        idx += 1
    srt_path.write_text("\n".join(srt_blocks), encoding="utf-8")

    manifest_data = {
        "episode_id": cue_sheet.episode_id,
        "chapter_number": cue_sheet.chapter_number,
        "title": cue_sheet.title,
        "mode": cue_sheet.mode,
        "total_duration_s": round(total_duration_s, 3),
        "sample_rate_hz": SAMPLE_RATE,
        "master_wav": str(master_wav),
        "master_mp3": str(master_mp3),
        "subtitles_srt": str(srt_path),
        "buses": {
            "dialogue_bus": str(dialogue_bus_wav),
            "sfx_foreground_bus": str(sfx_bus_wav),
            "bgm_ducked_bus": str(bgm_bus_wav),
        },
        "timeline": [asdict(it) for it in resolved_items],
    }
    manifest_path.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if clean_work_dir and work_dir.is_dir():
        shutil.rmtree(work_dir, ignore_errors=True)
    return {
        "master_wav": master_wav,
        "master_mp3": master_mp3,
        "subtitles_srt": srt_path,
        "manifest_json": manifest_path,
        "total_duration_s": round(total_duration_s, 3),
    }


def recover_intact_dialogue_from_master(
    cue_sheet: EpisodeCueSheet,
    v001_wav_path: Path,
    v001_manifest_path: Path,
    sfx_audio_map: dict[str, Path],
    act_bgm_map: dict[str, Path],
    keep_cue_ids: set[str],
    *,
    work_dir: Path | None = None,
    default_alimiter_delay_frames: int = 239,
) -> tuple[dict[str, array], dict[str, dict[str, Any]]]:
    """Recover conditioned 48kHz stereo dialogue stems from an existing `v001` master WAV.

    `master_episode_three_bus` sums `dialogue_buf + sfx_buf + bgm_ducked_buf` through FFmpeg
    `amix=inputs=3:normalize=0,alimiter=limit=0.891:attack=5:release=50:level=disabled`, which applies
    unity gain below -1.0 dBFS with a deterministic 5ms (`239`-frame at 48kHz) lookahead shift.
    Reconstructing `sfx_buf` and `bgm_ducked_buf` from `v001_manifest_path` + cached BGM/SFX stems
    and subtracting them recovers bit-exact conditioned dialogue clips for all intact cues.
    """
    manifest = json.loads(v001_manifest_path.read_text(encoding="utf-8"))
    timeline_items: list[dict[str, Any]] = manifest.get("timeline", [])
    if not timeline_items:
        raise ValueError(f"Empty timeline in manifest: {v001_manifest_path}")

    tmp_dir = work_dir or (v001_wav_path.parent / f"_recover_work_{cue_sheet.episode_id}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    clean_tmp = work_dir is None

    cue_lookup = {c.cue_id: c for c in cue_sheet.cues}
    master_samples = _read_stereo_s16(v001_wav_path)
    master_frames = len(master_samples) // CHANNELS

    # Reconstruct exact v001 timeline duration and frame buffer length
    max_item_end = max(float(it["end_s"]) for it in timeline_items)
    last_it = timeline_items[-1]
    last_cue = cue_lookup.get(last_it["cue_id"])
    if last_cue is not None and last_cue.kind == "sfx" and last_cue.placement == "overlay_next":
        cursor_end = float(last_it["start_s"]) + float(last_it.get("gap_after_s", last_cue.gap_after_s))
    else:
        cursor_end = float(last_it["end_s"]) + float(last_it.get("gap_after_s", 0.0))
    total_duration_s = max(cursor_end, max_item_end) + cue_sheet.tail_pad_s
    total_frames = max(master_frames, int(math.ceil(total_duration_s * SAMPLE_RATE)))

    # 1. Reconstruct v001 Bus B (Foreground SFX) & speech intervals + act spans
    sfx_buf = array("h", [0]) * (total_frames * CHANNELS)
    speech_intervals: list[tuple[float, float]] = []
    act_spans: dict[str, list[float]] = {}

    for it in timeline_items:
        cid = str(it["cue_id"])
        act_id = str(it.get("act_id", ""))
        st_s = float(it["start_s"])
        en_s = float(it["end_s"])
        if act_id:
            if act_id not in act_spans:
                act_spans[act_id] = [st_s, en_s]
            else:
                act_spans[act_id][0] = min(act_spans[act_id][0], st_s)
                act_spans[act_id][1] = max(act_spans[act_id][1], en_s)

        if it.get("kind") == "dialogue":
            speech_intervals.append((st_s, en_s))
        elif cid in sfx_audio_map and sfx_audio_map[cid].is_file():
            cue_obj = cue_lookup.get(cid)
            gain_db = cue_obj.gain_db if cue_obj is not None else 0.0
            cond_sfx = tmp_dir / f"rec_sfx_{cid}.wav"
            condition_sfx_clip(sfx_audio_map[cid], cond_sfx, gain_db=gain_db)
            sfx_samples = _read_stereo_s16(cond_sfx)
            _mix_into_buffer(sfx_buf, sfx_samples, int(round(st_s * SAMPLE_RATE)), gain=1.0)

    # 2. Reconstruct v001 Bus C (Ducked Per-Act BGM; respects silent dry acts)
    bgm_ducked_buf = array("h", [0]) * (total_frames * CHANNELS)
    active_acts = [a for a in cue_sheet.acts if a.act_id in act_spans]
    for idx, act in enumerate(active_acts):
        is_silent_act = (
            act.act_id not in act_bgm_map
            or not act_bgm_map[act.act_id].is_file()
            or not (act.bgm_prompt or "").strip()
            or (act.bgm_gain_speech <= 1e-4 and act.bgm_gain_gap <= 1e-4)
        )
        if is_silent_act:
            continue
        act_st = 0.0 if idx == 0 else max(0.0, act_spans[act.act_id][0] - 0.6)
        if idx == len(active_acts) - 1:
            act_en = total_duration_s
        else:
            next_act = active_acts[idx + 1]
            next_st = act_spans[next_act.act_id][0]
            next_is_silent = (
                next_act.act_id not in act_bgm_map
                or not act_bgm_map[next_act.act_id].is_file()
                or not (next_act.bgm_prompt or "").strip()
                or (next_act.bgm_gain_speech <= 1e-4 and next_act.bgm_gain_gap <= 1e-4)
            )
            act_en = min(total_duration_s, next_st + (0.15 if next_is_silent else 0.6))
        span_dur = max(1.0, act_en - act_st)

        fitted_wav = tmp_dir / f"rec_bgm_{act.act_id}.wav"
        fit_bgm_to_duration(act_bgm_map[act.act_id], span_dur, fitted_wav)
        raw_act_samples = _read_stereo_s16(fitted_wav)
        rel_speech = [
            (max(0.0, st - act_st), min(span_dur, en - act_st))
            for st, en in speech_intervals
            if en > act_st and st < act_en
        ]
        ducked_act_samples = apply_bgm_ducking_envelope(
            raw_act_samples,
            rel_speech,
            gain_speech=act.bgm_gain_speech,
            gain_gap=act.bgm_gain_gap,
        )
        _mix_into_buffer(bgm_ducked_buf, ducked_act_samples, int(round(act_st * SAMPLE_RATE)), gain=1.0)

    # Combine sfx_buf + bgm_ducked_buf into non-dialogue accompaniment buffer
    accompaniment = array("h", sfx_buf)
    _mix_into_buffer(accompaniment, bgm_ducked_buf, 0, gain=1.0)

    # 3. Auto-verify lookahead delay on leading head_pad silence (typically 239 frames at 48kHz)
    delay_frames = default_alimiter_delay_frames
    first_speech_s = min((st for st, _ in speech_intervals), default=cue_sheet.head_pad_s)
    probe_end_frame = min(master_frames - 260, int((first_speech_s - 0.02) * SAMPLE_RATE))
    if probe_end_frame > 2400:
        best_err = float("inf")
        for cand in (default_alimiter_delay_frames, 240, 238, 0):
            err_sum = 0
            cnt = 0
            for f in range(1200, probe_end_frame, 16):
                mf = f + cand
                if 0 <= mf < master_frames:
                    acc_l = accompaniment[f * CHANNELS]
                    if abs(acc_l) > 8:
                        err_sum += abs(master_samples[mf * CHANNELS] - acc_l)
                        cnt += 1
            if cnt >= 10:
                mean_err = err_sum / cnt
                if mean_err < best_err:
                    best_err = mean_err
                    delay_frames = cand

    # 4. Subtract accompaniment at `delay_frames` and slice each intact dialogue cue
    recovered_samples: dict[str, array] = {}
    recovered_meta: dict[str, dict[str, Any]] = {}

    for it in timeline_items:
        cid = str(it["cue_id"])
        if it.get("kind") != "dialogue" or cid not in keep_cue_ids:
            continue
        st_frame = int(round(float(it["start_s"]) * SAMPLE_RATE))
        n_frames = max(1, int(round(float(it["duration_s"]) * SAMPLE_RATE)))
        end_frame = min(total_frames, st_frame + n_frames)

        # Slice master[st_frame + delay : end_frame + delay] - accompaniment[st_frame : end_frame]
        m_start = st_frame + delay_frames
        m_end = end_frame + delay_frames
        slice_frames = max(0, min(end_frame - st_frame, master_frames - m_start))
        if slice_frames <= 0:
            continue

        if _audioop is not None:
            m_bytes = memoryview(master_samples)[m_start * CHANNELS : (m_start + slice_frames) * CHANNELS].tobytes()
            a_bytes = memoryview(accompaniment)[st_frame * CHANNELS : (st_frame + slice_frames) * CHANNELS].tobytes()
            neg_a = _audioop.mul(a_bytes, 2, -1.0)
            diff_bytes = _audioop.add(m_bytes, neg_a, 2)
            clip_arr = array("h")
            clip_arr.frombytes(diff_bytes)
        else:
            clip_arr = array("h", [0]) * (slice_frames * CHANNELS)
            for i in range(slice_frames * CHANNELS):
                val = master_samples[m_start * CHANNELS + i] - accompaniment[st_frame * CHANNELS + i]
                if val > 32767:
                    val = 32767
                elif val < -32768:
                    val = -32768
                clip_arr[i] = val

        recovered_samples[cid] = clip_arr
        recovered_meta[cid] = {
            "voice_id": str(it.get("voice_id", f"drama3:{it.get('role_id', '')}")),
            "qa_passed": bool(it.get("qa_passed", True)),
            "recovered_from_v001": True,
        }

    if clean_tmp and tmp_dir.is_dir():
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return recovered_samples, recovered_meta

