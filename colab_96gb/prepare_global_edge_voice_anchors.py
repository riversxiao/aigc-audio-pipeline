#!/usr/bin/env python3
"""Real-Human Studio Vocal Anchor Builder for《跨境底牌：硅深暗战》/ Global Edge (Fish Audio Drama 3).

Prepares and locks the 8 character reference anchors required by `fishaudio/drama-3` (`sglang-omni`)
under `anchor_schema_version = "v2_real_human_studio"` with 0% commercial voice APIs and 0% synthetic TTS:
  - 5 Core Cast (100% of E001; 96.0% of Season 1 EN runtime):
      `lin_chen` (same-speaker bilingual EN+ZH), `zhou_mo` (Shenzhen tech exec Mandarin + EN terms),
      `victoria_vance` (Silicon Valley US Female), `alistair_finch` (London RP Male),
      `claire_chen_gc` (NYC General Counsel Female)
  - 3 Controlled International Guests (4.0% of Season 1 EN runtime; E011/E013/E016 only):
      `rajiv_menon` (Indian Exec Male), `wei_ling_tan` (Singapore Sovereign VC Female),
      `henrik_lindqvist` (Northern-European EU Legal Male)

Conditioning chain:
  - 44100 Hz, mono (`aformat=sample_rates=44100:channel_layouts=mono` BEFORE `loudnorm`), 16-bit PCM WAV (`pcm_s16le`)
  - `aformat=sample_rates=44100:channel_layouts=mono,highpass=f=75`, fade, `loudnorm=I=-16:TP=-1.5:LRA=11` (strictly ZERO `afftdn` spectral denoising)
  - Verbatim `.txt` sidecar written alongside every `voice_anchors/<role_id>.wav`

Note:
  - `--offline-stub` synthesizes multi-harmonic speech-like WAVs conditioned through real FFmpeg strictly
    for local CPU dry-runs and automated tests, explicitly stamped `source_voice_name = "offline_synthetic_stub"`.
"""

from __future__ import annotations

import argparse
from array import array
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Iterable
import urllib.request
import wave

STUDIO_DIR = Path(__file__).resolve().parent
for _cand in (STUDIO_DIR / "src", STUDIO_DIR.parent / "src"):
    if (_cand / "aigc_audio_pipeline").is_dir() and str(_cand) not in sys.path:
        sys.path.insert(0, str(_cand))

from aigc_audio_pipeline.drama3_adapter import DRAMA3_ANCHOR_SAMPLE_RATE  # noqa: E402
from aigc_audio_pipeline.models import (  # noqa: E402
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
    utc_now_iso,
)

ANCHOR_SCHEMA_VERSION = "v2_real_human_studio"
DEFAULT_DOMAIN = "business_english_drama"

DEFAULT_PROJECT_META_DIR = (
    STUDIO_DIR.parent / "projects" / "global_edge" / "00_节目圣经与第一季24集总纲"
)
DEFAULT_REGISTRY_PATH = DEFAULT_PROJECT_META_DIR / "voice_casting_registry.json"
DEFAULT_SOURCES_PATH = DEFAULT_PROJECT_META_DIR / "anchor_sources.json"

CORE_ROLE_IDS: tuple[str, ...] = (
    "lin_chen",
    "zhou_mo",
    "victoria_vance",
    "alistair_finch",
    "claire_chen_gc",
)
ALL_ROLE_IDS: tuple[str, ...] = (
    "lin_chen",
    "zhou_mo",
    "victoria_vance",
    "alistair_finch",
    "claire_chen_gc",
    "rajiv_menon",
    "wei_ling_tan",
    "henrik_lindqvist",
)

_STUB_ROLE_BASE_FREQS: dict[str, float] = {
    "lin_chen": 122.0,
    "zhou_mo": 134.0,
    "victoria_vance": 208.0,
    "alistair_finch": 114.0,
    "claire_chen_gc": 224.0,
    "rajiv_menon": 128.0,
    "wei_ling_tan": 216.0,
    "henrik_lindqvist": 110.0,
}

_AUDIO_EXTENSIONS: tuple[str, ...] = (".wav", ".mp3", ".m4a", ".flac", ".ogg")


def probe_duration_seconds(audio_path: Path) -> float:
    """Probe audio duration in seconds via `ffprobe` with pure-stdlib `wave` fallback."""
    if not audio_path.is_file():
        return 0.0
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=15,
        ).strip()
        if out and out != "N/A":
            dur = float(out.splitlines()[0].strip())
            if math.isfinite(dur) and dur > 0.0:
                return dur
    except Exception:
        pass
    try:
        with wave.open(str(audio_path), "rb") as wf:
            rate = wf.getframerate()
            if rate > 0:
                return wf.getnframes() / float(rate)
    except Exception:
        pass
    return 0.0


def condition_studio_anchor_wav(
    src_media: Path,
    dst_wav: Path,
    *,
    start_s: float = 0.0,
    end_s: float = 0.0,
) -> float:
    """Condition real-human studio audio to 44.1kHz mono PCM16 -16 LUFS WAV (strictly ZERO afftdn)."""
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    # Downmix to mono & target sample rate BEFORE highpass/loudnorm so stereo drop-ins hit exact -16 LUFS
    filters: list[str] = [
        f"aformat=sample_rates={DRAMA3_ANCHOR_SAMPLE_RATE}:channel_layouts=mono"
    ]
    if end_s > start_s:
        effective_dur = end_s - start_s
        filters.append(f"atrim=start={start_s:.2f}:end={end_s:.2f},asetpts=PTS-STARTPTS")
        fade_out_st = max(0.08, effective_dur - 0.06)
        filters.append(
            f"highpass=f=75,afade=t=in:st=0:d=0.04,afade=t=out:st={fade_out_st:.2f}:d=0.06"
        )
    else:
        effective_dur = probe_duration_seconds(src_media)
        filters.append("highpass=f=75,afade=t=in:st=0:d=0.03")

    if effective_dur >= 1.5 or effective_dur <= 0.0:
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
    else:
        filters.append("alimiter=limit=0.89:level=disabled")

    work_target = dst_wav
    same_file = src_media.resolve() == dst_wav.resolve()
    if same_file:
        work_target = dst_wav.with_suffix(".cond_tmp.wav")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(src_media),
                "-af",
                ",".join(filters),
                "-ar",
                str(DRAMA3_ANCHOR_SAMPLE_RATE),
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(work_target),
            ],
            check=True,
        )
        if same_file:
            work_target.replace(dst_wav)
    finally:
        if same_file and work_target.exists():
            work_target.unlink(missing_ok=True)

    return round(probe_duration_seconds(dst_wav), 3)


def _write_stub_speech_like_raw_wav(
    raw_wav: Path,
    *,
    base_freq_hz: float,
    duration_s: float = 11.0,
) -> Path:
    """Synthesize a rich multi-harmonic speech-like mono 44.1kHz PCM16 waveform for offline stub testing."""
    raw_wav.parent.mkdir(parents=True, exist_ok=True)
    sr = DRAMA3_ANCHOR_SAMPLE_RATE
    # Generate a seamless 1.0-second multi-harmonic tile (syllabic 3.5Hz & 4Hz envelope) and repeat cleanly
    tile_frames = sr
    harmonics = (
        (base_freq_hz, 0.28),
        (base_freq_hz * 2.0, 0.30),
        (base_freq_hz * 3.0, 0.20),
        (base_freq_hz * 5.0, 0.12),
        (base_freq_hz * 7.0, 0.07),
        (base_freq_hz * 10.0, 0.03),
    )
    norm_scale = sum(w for _, w in harmonics)
    tile = array("h", [0]) * tile_frames
    two_pi = 2.0 * math.pi
    for i in range(tile_frames):
        t = i / sr
        env = 0.56 + 0.34 * math.sin(two_pi * 3.0 * t) + 0.10 * math.cos(two_pi * 7.0 * t)
        sig = sum(w * math.sin(two_pi * f * t) for f, w in harmonics) / norm_scale
        tile[i] = int(max(-32767, min(32767, round(32767.0 * 0.34 * env * sig))))

    total_frames = max(int(round(1.0 * sr)), int(round(duration_s * sr)))
    full_repeats, remainder = divmod(total_frames, tile_frames)
    buf = array("h")
    for _ in range(full_repeats):
        buf.extend(tile)
    if remainder > 0:
        buf.extend(tile[:remainder])

    fade_frames = min(int(0.03 * sr), len(buf) // 4)
    for i in range(fade_frames):
        gain = 0.5 * (1.0 - math.cos(math.pi * i / fade_frames))
        buf[i] = int(round(buf[i] * gain))
        buf[len(buf) - 1 - i] = int(round(buf[len(buf) - 1 - i] * gain))

    with wave.open(str(raw_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(buf.tobytes())
    return raw_wav


def _join_whisper_segments(parts: Iterable[str], *, language_code: str) -> str:
    """Join Whisper segment strings without concatenating adjacent English words on bilingual audio."""
    cleaned = [str(p).strip() for p in parts if str(p).strip()]
    if not cleaned:
        return ""
    if language_code == "en":
        return " ".join(cleaned).strip()
    out = cleaned[0]
    for seg in cleaned[1:]:
        prev_ch = out[-1]
        next_ch = seg[0]
        if (prev_ch.isascii() and prev_ch.isalnum()) and (next_ch.isascii() and next_ch.isalnum()):
            out = f"{out} {seg}"
        elif prev_ch in ".,!?;:)]}\"'" and next_ch.isascii() and next_ch.isalnum():
            out = f"{out} {seg}"
        else:
            out = f"{out}{seg}"
    return out.strip()


def _transcribe_verbatim_whisper(
    wav_path: Path,
    *,
    language_code: str,
    whisper_model_size: str = "small",
) -> str:
    """Lazily transcribe exact spoken words via CPU int8 `faster-whisper` when a custom `.txt` sidecar is absent."""
    from faster_whisper import WhisperModel  # type: ignore[import-not-found]
    import numpy as np  # type: ignore[import-not-found]

    raw_pcm = subprocess.check_output(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(wav_path),
            "-ar",
            "16000",
            "-ac",
            "1",
            "-f",
            "f32le",
            "pipe:1",
        ]
    )
    audio_16k = np.frombuffer(raw_pcm, dtype=np.float32).copy()
    model = WhisperModel(whisper_model_size, device="cpu", compute_type="int8")
    transcribe_kwargs: dict[str, Any] = {"beam_size": 5, "vad_filter": True}
    if language_code == "en":
        transcribe_kwargs["language"] = "en"
    elif language_code == "zh":
        transcribe_kwargs["language"] = "zh"
    segments, _ = model.transcribe(audio_16k, **transcribe_kwargs)
    return _join_whisper_segments((seg.text for seg in segments), language_code=language_code)


def _resolve_tier3_transcript(
    spec: dict[str, Any],
    dst_wav: Path,
    *,
    role_id: str,
    language_code: str,
    whisper_size: str = "small",
) -> str:
    """Resolve verbatim transcript for Tier 3 downloaded external audio (NEVER stamps fictional audition text)."""
    explicit = str(
        spec.get("direct_audio_transcript") or spec.get("source_transcript") or ""
    ).strip()
    if explicit:
        return explicit
    try:
        transcribed = _transcribe_verbatim_whisper(
            dst_wav,
            language_code=language_code,
            whisper_model_size=whisper_size,
        ).strip()
    except Exception as exc:
        dst_wav.unlink(missing_ok=True)
        raise RuntimeError(
            f"[{role_id}] Tier 3 downloaded audio `{dst_wav.name}` lacks "
            f"`direct_audio_transcript`/`source_transcript` in anchor_sources.json and "
            f"local faster-whisper transcription failed ({exc}). "
            f"Refusing to stamp mismatched audition text onto external audio."
        ) from exc
    if not transcribed:
        dst_wav.unlink(missing_ok=True)
        raise RuntimeError(
            f"[{role_id}] Tier 3 downloaded audio `{dst_wav.name}` produced an empty "
            f"Whisper transcript and lacks `direct_audio_transcript`/`source_transcript`. "
            f"Refusing to stamp mismatched audition text onto external audio."
        )
    return transcribed


def _try_download_direct_audio(
    urls: Iterable[str],
    dl_dir: Path,
    role_id: str,
) -> Path | None:
    """Attempt direct permissive HTTP download for URLs pointing to raw studio audio files."""
    for idx, url in enumerate(urls):
        clean_url = str(url).strip()
        if not clean_url.startswith(("http://", "https://")):
            continue
        lower_path = clean_url.split("?", 1)[0].lower()
        if not any(lower_path.endswith(ext) for ext in _AUDIO_EXTENSIONS):
            continue
        ext = Path(lower_path).suffix or ".wav"
        dst = dl_dir / f"{role_id}_corpus_{idx}{ext}"
        try:
            req = urllib.request.Request(
                clean_url,
                headers={"User-Agent": "GlobalEdgeAudioPipeline/2.0"},
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
            if len(data) > 4096:
                dst.write_bytes(data)
                return dst
        except Exception:
            continue
    return None


def _resolve_requested_roles(roles_spec: str, registry: VoiceCastingRegistry) -> list[str]:
    spec = (roles_spec or "all").strip()
    lower = spec.lower()
    if lower in ("", "all"):
        ordered = [r for r in ALL_ROLE_IDS if r in registry.roles]
        for r in registry.roles:
            if r not in ordered:
                ordered.append(r)
        return ordered
    if lower == "core":
        return [r for r in CORE_ROLE_IDS if r in registry.roles]

    selected: list[str] = []
    for tok in [t.strip() for t in spec.split(",") if t.strip()]:
        if tok not in registry.roles:
            raise ValueError(f"Unknown role_id {tok!r}; available: {sorted(registry.roles)}")
        if tok not in selected:
            selected.append(tok)
    if not selected:
        raise ValueError("No valid roles selected.")
    return selected


def prepare_all_global_edge_anchors(
    *,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    anchor_sources_path: Path | None = None,
    output_dir: Path,
    custom_anchors_dir: Path | None = None,
    roles: str = "all",
    whisper_size: str = "small",
    offline_stub: bool = False,
) -> dict[str, Any]:
    """Build `v2_real_human_studio` `voice_anchors/*.{wav,txt}` + `voice_cast_drama3.json` in `output_dir`."""
    registry = VoiceCastingRegistry.load(registry_path)
    sources_path = anchor_sources_path or (registry_path.resolve().parent / "anchor_sources.json")
    sources_data: dict[str, Any] = {}
    if sources_path.is_file():
        sources_data = json.loads(sources_path.read_text(encoding="utf-8"))
    source_roles: dict[str, dict[str, Any]] = sources_data.get("roles", {})

    output_dir.mkdir(parents=True, exist_ok=True)
    anchors_dir = output_dir / "voice_anchors"
    tmp_dir = output_dir / "_anchor_prep_tmp"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    bundled_repo_anchors_dir = registry_path.resolve().parent / "voice_anchors"
    custom_dir = custom_anchors_dir or (output_dir / "custom_anchors")

    target_roles = _resolve_requested_roles(roles, registry)
    cast_entries: dict[str, dict[str, Any]] = {}

    try:
        for role_id in target_roles:
            prof = registry.resolve_role(role_id)
            if prof is None:
                raise KeyError(f"Role {role_id!r} missing from registry {registry_path}")

            spec = source_roles.get(role_id, {})
            default_spoken = str(spec.get("anchor_text") or "").strip()
            if not default_spoken:
                _, default_spoken = extract_tags_and_spoken_text(prof.audition_line)
            if not default_spoken:
                default_spoken = f"{prof.display_name} studio reference voice anchor."

            rel_wav = f"voice_anchors/{role_id}.wav"
            dst_wav = output_dir / rel_wav
            dst_txt = anchors_dir / f"{role_id}.txt"

            custom_candidates: list[Path] = []
            if custom_dir.is_dir():
                custom_candidates = [
                    p
                    for p in sorted(custom_dir.glob(f"{role_id}.*"))
                    if p.is_file() and p.suffix.lower() in _AUDIO_EXTENSIONS
                ]
            bundled_wav = bundled_repo_anchors_dir / f"{role_id}.wav"

            anchor_text = ""
            source_note = ""

            if offline_stub:
                target_dur = float(spec.get("target_duration_s", 11.0))
                stub_dur = max(10.0, min(12.0, target_dur))
                raw_stub = tmp_dir / f"{role_id}_raw_stub.wav"
                _write_stub_speech_like_raw_wav(
                    raw_stub,
                    base_freq_hz=_STUB_ROLE_BASE_FREQS.get(role_id, 165.0),
                    duration_s=stub_dur,
                )
                dur_s = condition_studio_anchor_wav(raw_stub, dst_wav)
                anchor_text = default_spoken
                source_note = "offline_synthetic_stub"
            elif custom_candidates:
                src_file = custom_candidates[0]
                dur_s = condition_studio_anchor_wav(src_file, dst_wav)
                txt_sidecar = src_file.with_suffix(".txt")
                if txt_sidecar.is_file() and txt_sidecar.read_text(encoding="utf-8").strip():
                    anchor_text = txt_sidecar.read_text(encoding="utf-8").strip()
                else:
                    anchor_text = _transcribe_verbatim_whisper(
                        dst_wav,
                        language_code=prof.language_code,
                        whisper_model_size=whisper_size,
                    )
                    if not anchor_text:
                        anchor_text = default_spoken
                source_note = f"custom_real_human_anchor:{src_file.name}"
            elif bundled_wav.is_file() and bundled_wav.stat().st_size > 10000:
                if bundled_wav.resolve() != dst_wav.resolve():
                    dur_s = condition_studio_anchor_wav(bundled_wav, dst_wav)
                else:
                    dur_s = round(probe_duration_seconds(dst_wav), 3)
                txt_sidecar = bundled_wav.with_suffix(".txt")
                if txt_sidecar.is_file() and txt_sidecar.read_text(encoding="utf-8").strip():
                    anchor_text = txt_sidecar.read_text(encoding="utf-8").strip()
                else:
                    anchor_text = default_spoken
                source_note = str(spec.get("source_name") or f"repo_bundled_real_human:{role_id}")
            else:
                downloaded = _try_download_direct_audio(
                    spec.get("source_urls", []),
                    tmp_dir,
                    role_id,
                )
                if downloaded is not None:
                    trim_start = float(spec.get("source_trim_start_s", 0.0) or 0.0)
                    trim_end = float(spec.get("source_trim_end_s", 0.0) or 0.0)
                    dur_s = condition_studio_anchor_wav(
                        downloaded,
                        dst_wav,
                        start_s=trim_start,
                        end_s=trim_end,
                    )
                    anchor_text = _resolve_tier3_transcript(
                        spec,
                        dst_wav,
                        role_id=role_id,
                        language_code=prof.language_code,
                        whisper_size=whisper_size,
                    )
                    source_note = str(spec.get("source_name") or f"real_human_studio_corpus:{role_id}")
                else:
                    raise RuntimeError(
                        f"[{role_id}] No real-human studio anchor found. "
                        f"Drop a close-mic real-human recording at `{custom_dir / (role_id + '.wav')}` "
                        f"(with optional `{role_id}.txt` verbatim transcript) or place bundled anchors in "
                        f"`{bundled_repo_anchors_dir}`. Synthetic TTS fallback is strictly forbidden "
                        f"(use `--offline-stub` only for local CPU dry-runs)."
                    )

            dst_txt.write_text(anchor_text.strip() + "\n", encoding="utf-8")

            cast_entries[role_id] = {
                "role_id": role_id,
                "display_name": prof.display_name,
                "tier": prof.tier,
                "gender": prof.gender,
                "age_group": prof.age_group,
                "language_code": prof.language_code,
                "accent_code": prof.accent_code,
                "vocal_register": prof.vocal_register,
                "source_voice_name": source_note,
                "anchor_wav": rel_wav,
                "anchor_duration_s": dur_s,
                "anchor_text": anchor_text,
                "default_stability": prof.default_stability,
            }
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    payload: dict[str, Any] = {
        "project_id": registry.project_id,
        "project_title": registry.project_title,
        "domain": registry.domain or DEFAULT_DOMAIN,
        "anchor_schema_version": ANCHOR_SCHEMA_VERSION,
        "engine": (
            "fishaudio/drama-3 + OpenMOSS-Team/MOSS-SoundEffect-v2.0 "
            "+ ACE-Step/acestep-v15-xl-turbo-diffusers"
        ),
        "exported_at": utc_now_iso(),
        "anchor_sample_rate_hz": DRAMA3_ANCHOR_SAMPLE_RATE,
        "role_count": len(cast_entries),
        "characters": cast_entries,
    }
    voice_cast_json = output_dir / "voice_cast_drama3.json"
    voice_cast_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "《跨境底牌：硅深暗战》/ Global Edge 8角色真人录音棚级干声锚点制备工具 "
            "(Fish Audio Drama 3, v2_real_human_studio, 44.1kHz mono -16 LUFS)"
        )
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY_PATH),
        help="Path to voice_casting_registry.json",
    )
    parser.add_argument(
        "--sources",
        "--anchor-sources",
        dest="anchor_sources",
        default=str(DEFAULT_SOURCES_PATH),
        help="Path to anchor_sources.json provenance manifest",
    )
    parser.add_argument(
        "--custom-anchors-dir",
        default="",
        help="Optional directory with user-supplied real-human <role_id>.{wav,mp3,m4a,flac} (+ optional .txt)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Target directory to write voice_anchors/*.{wav,txt} and voice_cast_drama3.json",
    )
    parser.add_argument(
        "--roles",
        default="all",
        help="Role subset: 'all', 'core', or comma-separated role_ids (default: all)",
    )
    parser.add_argument(
        "--whisper-size",
        default="small",
        help="CPU int8 faster-whisper size when a custom anchor lacks a .txt sidecar (default: small)",
    )
    parser.add_argument(
        "--offline-stub",
        action="store_true",
        help="Generate FFmpeg-conditioned offline synthetic WAV stubs strictly for local CI/dry-runs",
    )
    args = parser.parse_args(argv)

    res = prepare_all_global_edge_anchors(
        registry_path=Path(args.registry).resolve(),
        anchor_sources_path=Path(args.anchor_sources).resolve() if args.anchor_sources else None,
        output_dir=Path(args.output_dir).resolve(),
        custom_anchors_dir=Path(args.custom_anchors_dir).resolve() if args.custom_anchors_dir else None,
        roles=args.roles,
        whisper_size=args.whisper_size,
        offline_stub=args.offline_stub,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "project_id": res["project_id"],
                "domain": res["domain"],
                "anchor_schema_version": res["anchor_schema_version"],
                "anchor_sample_rate_hz": res["anchor_sample_rate_hz"],
                "role_count": res["role_count"],
                "roles": {
                    k: {
                        "accent_code": v["accent_code"],
                        "source": v["source_voice_name"],
                        "duration_s": v["anchor_duration_s"],
                    }
                    for k, v in res["characters"].items()
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
