"""Natural speech-rate timeline & 3-bus mastering engine (Dialogue + Foreground SFX + Ducked BGM)."""

from __future__ import annotations

from array import array
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import subprocess
import wave
from typing import Any

from .elevenlabs_client import probe_duration_seconds
from .models import EpisodeCueSheet, extract_tags_and_spoken_text, next_append_only_path

SAMPLE_RATE = 48000
CHANNELS = 2


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
    spoken_text: str = ""
    tagged_text: str = ""
    voice_id: str = ""
    stability: float = 0.5
    qa_passed: bool = True


def _format_srt_ts(seconds: float) -> str:
    ms_total = max(0, int(round(seconds * 1000)))
    hh = ms_total // 3600000
    rem = ms_total % 3600000
    mm = rem // 60000
    rem %= 60000
    ss = rem // 1000
    ms = rem % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def condition_dialogue_clip(
    raw_wav: Path,
    conditioned_wav: Path,
    *,
    acoustic_space: str = "dry",
) -> Path:
    """Condition a 48kHz dialogue clip: rumble filter, gentle speech leveling, optional space."""
    conditioned_wav.parent.mkdir(parents=True, exist_ok=True)
    dur = probe_duration_seconds(raw_wav)

    filters: list[str] = [
        "aformat=sample_rates=48000:channel_layouts=stereo",
        "highpass=f=75",
    ]
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

    if dur >= 1.4:
        # EBU R128 / podcast-drama broadcast loudness target (-16 LUFS) for consistent actor levels
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
    else:
        # Very short gasps/exclamations (<1.4s): avoid loudnorm over-amplifying breath noise
        filters.append("alimiter=limit=0.84:level=disabled")

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

    # Compute envelope at 100 Hz control rate (every 480 frames = 10ms) for speed & smoothness
    step_frames = 480
    num_steps = (total_frames + step_frames - 1) // step_frames
    ctrl_gains = [gain_gap] * (num_steps + 1)

    for step_idx in range(num_steps + 1):
        t = (step_idx * step_frames) / SAMPLE_RATE
        g = gain_gap
        for st, en in merged:
            if t < st - attack_s:
                break
            if st <= t <= en:
                g = gain_speech
                break
            if st - attack_s <= t < st:
                # Smooth cosine ramp down from gain_gap -> gain_speech
                alpha = (t - (st - attack_s)) / max(attack_s, 1e-3)
                blend = 0.5 * (1.0 - math.cos(math.pi * alpha))
                g = min(g, gain_gap + (gain_speech - gain_gap) * blend)
            elif en < t <= en + release_s:
                # Smooth cosine ramp up from gain_speech -> gain_gap
                alpha = (t - en) / max(release_s, 1e-3)
                blend = 0.5 * (1.0 - math.cos(math.pi * alpha))
                g = min(g, gain_speech + (gain_gap - gain_speech) * blend)
        ctrl_gains[step_idx] = g

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
        condition_dialogue_clip(raw_wav, cond_wav, acoustic_space="dry")
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


def master_episode_three_bus(
    cue_sheet: EpisodeCueSheet,
    cue_audio_map: dict[str, Path],
    act_bgm_map: dict[str, Path],
    output_dir: Path,
    *,
    cue_meta_map: dict[str, dict[str, Any]] | None = None,
    registry: Any | None = None,
) -> dict[str, Any]:
    """Assemble natural-rate Dialogue Bus + Foreground SFX Bus + Ducked Per-Act BGM Bus."""
    work_dir = output_dir / "_stems_work"
    work_dir.mkdir(parents=True, exist_ok=True)
    cue_meta_map = cue_meta_map or {}

    # 1. Condition each cue clip & compute exact natural timeline
    cursor_s = cue_sheet.head_pad_s
    max_end_s = cursor_s
    resolved_items: list[ResolvedTimelineItem] = []
    conditioned_map: dict[str, array] = {}
    act_spans: dict[str, list[float]] = {}

    for cue in cue_sheet.cues:
        raw_path = cue_audio_map[cue.cue_id]
        cond_path = work_dir / f"{cue.cue_id}_cond.wav"
        if cue.kind == "dialogue":
            condition_dialogue_clip(raw_path, cond_path, acoustic_space=cue.acoustic_space)
        else:
            condition_sfx_clip(raw_path, cond_path, gain_db=cue.gain_db)

        samples = _read_stereo_s16(cond_path)
        dur_s = (len(samples) // CHANNELS) / SAMPLE_RATE
        conditioned_map[cue.cue_id] = samples

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
                spoken_text=clean_spoken,
                tagged_text=cue.text,
                voice_id=str(meta.get("voice_id", "")),
                stability=cue.stability,
                qa_passed=bool(meta.get("qa_passed", True)),
            )
        )

        if cue.kind == "sfx" and cue.placement == "overlay_next":
            # Optional pre-offset before dialogue enters while SFX continues underneath
            cursor_s = start_s + cue.gap_after_s
        else:
            cursor_s = end_s + cue.gap_after_s

    total_duration_s = max(cursor_s, max_end_s) + cue_sheet.tail_pad_s
    total_frames = int(math.ceil(total_duration_s * SAMPLE_RATE))

    # 2. Render Bus A (Dialogue) & Bus B (Foreground SFX - never ducked!)
    dialogue_buf = array("h", [0]) * (total_frames * CHANNELS)
    sfx_buf = array("h", [0]) * (total_frames * CHANNELS)
    speech_intervals: list[tuple[float, float]] = []

    for item in resolved_items:
        samples = conditioned_map[item.cue_id]
        start_frame = int(round(item.start_s * SAMPLE_RATE))
        if item.kind == "dialogue":
            _mix_into_buffer(dialogue_buf, samples, start_frame, gain=1.0)
            speech_intervals.append((item.start_s, item.end_s))
        else:
            _mix_into_buffer(sfx_buf, samples, start_frame, gain=1.0)

    # 3. Render Bus C (Per-Act BGM Bed with dialogue-only ducking: 0.11 speech / 0.34 gap)
    bgm_ducked_buf = array("h", [0]) * (total_frames * CHANNELS)
    acts_with_bgm = [a for a in cue_sheet.acts if a.act_id in act_bgm_map]
    for idx, act in enumerate(acts_with_bgm):
        if act.act_id not in act_spans:
            continue
        act_st = 0.0 if idx == 0 else max(0.0, act_spans[act.act_id][0] - 0.6)
        if idx == len(acts_with_bgm) - 1:
            act_en = total_duration_s
        else:
            next_act = acts_with_bgm[idx + 1]
            next_st = act_spans.get(next_act.act_id, [act_spans[act.act_id][1]])[0]
            act_en = min(total_duration_s, next_st + 0.6)
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
    master_wav = next_append_only_path(output_dir, f"{cue_sheet.episode_id}_master", ".wav")
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
            "192k",
            str(master_mp3),
        ],
        check=True,
    )

    # 5. Export sample-accurate SRT subtitles
    srt_blocks: list[str] = []
    sub_idx = 1
    for item in resolved_items:
        if item.kind != "dialogue" or not item.spoken_text:
            continue
        if item.role_id == "narrator":
            speaker_prefix = ""
        else:
            prof = registry.resolve_role(item.role_id) if registry is not None else None
            speaker_label = prof.display_name if prof is not None else item.role_id
            speaker_prefix = f"【{speaker_label}】"
        srt_blocks.append(
            f"{sub_idx}\n"
            f"{_format_srt_ts(item.start_s)} --> {_format_srt_ts(item.end_s)}\n"
            f"{speaker_prefix}{item.spoken_text}\n"
        )
        sub_idx += 1
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
    return {
        "master_wav": master_wav,
        "master_mp3": master_mp3,
        "subtitles_srt": srt_path,
        "manifest_json": manifest_path,
        "total_duration_s": round(total_duration_s, 3),
    }
