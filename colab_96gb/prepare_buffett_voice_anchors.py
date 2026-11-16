#!/usr/bin/env python3
"""Real-Human Studio Vocal Anchor Builder for《穿越周期的信》(Fish Audio Drama 3 44.1kHz -16 LUFS).

Prepares and locks the 4 character reference anchors required by `fishaudio/drama-3` (`sglang-omni`)
with ZERO ElevenLabs API usage and ZERO synthetic `edge-tts` voices:
  1. `host_zhiwei` (30yo female finance-podcast host):
     - Real-human close-mic Mainland Mandarin podcast studio recording (`OpenMOSS/MOSS-TTSD` Apache-2.0
       `pod_f_enhanced.wav`, finance-major spontaneous studio speech).
  2. `guest_huaiyuan` (40yo EN-ZH bilingual investor):
     - Real-human close-mic Mainland Mandarin podcast studio recording (`OpenMOSS/MOSS-TTSD` Apache-2.0
       `pod_m_enhanced.wav`, calm actuary/finance conversationalist).
  3. `guest_laozhou` (48yo grounded manufacturing & brick-and-mortar veteran):
     - Real-human close-mic Mainland Mandarin manufacturing veteran studio dialogue (`10.9s` solo studio stem).
  4. `buffett_prime_en` (50-60yo Prime-Age Warren Buffett):
     - Real-human 58-year-old Warren Buffett close-mic PBS studio interview (*Adam Smith's Money World*,
       `15.6s` clean solo lavalier stem, zero auditorium echo, zero `afftdn` muffling).
  5. `--offline-stub`: Pure FFmpeg/Python synthetic WAVs for local CI & CPU dry-run unit tests ONLY.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any
import urllib.request
import wave

STUDIO_DIR = Path(__file__).resolve().parent
for cand in (STUDIO_DIR / "src", STUDIO_DIR.parent / "src"):
    if (cand / "aigc_audio_pipeline").is_dir() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from aigc_audio_pipeline.drama3_adapter import (  # noqa: E402
    DRAMA3_ANCHOR_SAMPLE_RATE,
    convert_to_drama3_anchor_wav,
)
from aigc_audio_pipeline.elevenlabs_client import probe_duration_seconds  # noqa: E402
from aigc_audio_pipeline.models import VoiceCastingRegistry, utc_now_iso  # noqa: E402

ANCHOR_SCHEMA_VERSION = "v2_real_human_studio"

REAL_HUMAN_ANCHOR_SPECS: dict[str, dict[str, Any]] = {
    "host_zhiwei": {
        "source_label": "real_human_podcast_studio:moss_pod_f_enhanced",
        "fallback_raw_url": "https://raw.githubusercontent.com/OpenMOSS/MOSS-TTSD/main/legacy/v0.7/examples/pod_f_enhanced.wav",
        "anchor_text": (
            "但是因为我上学的时候学的是金融学专业嘛，所以确实可能就看起来这个领域跨度还是比较大的。"
            "那如果说回我当时的情况的话呢，当时在毕业季的话大家肯定都会争取拿到更多的offer嘛。"
        ),
    },
    "guest_huaiyuan": {
        "source_label": "real_human_podcast_studio:moss_pod_m_enhanced",
        "fallback_raw_url": "https://raw.githubusercontent.com/OpenMOSS/MOSS-TTSD/main/legacy/v0.7/examples/pod_m_enhanced.wav",
        "anchor_text": (
            "九二年回到中国之后跟复旦去建了精算学院，现在跟很多学校也有在合作，就是这是最早在国内去做精算的。"
            "现在精算就是有中精，就中国精算师体系，还有北美精算师，这个是提得比较多的，也可能是业界含金量最高的吧。"
        ),
    },
    "guest_laozhou": {
        "source_label": "real_human_podcast_studio:mainland_mfg_veteran_solo",
        "yt_url": "https://www.youtube.com/watch?v=9BxnMCkLmKQ",
        "yt_section": (260.0, 282.0),
        "trim_window": (6.65, 17.55),
        "anchor_text": (
            "就是说我在这个产线上我生产都是同样的东西。"
            "但实际你今天再看工业生产，其实这种非标制造，或者这种柔性的生产，占的比例会越来越高。"
        ),
    },
    "buffett_prime_en": {
        "source_label": "real_human_pbs_studio_1990:warren_buffett_58yo_adamsmith",
        "yt_url": "https://www.youtube.com/watch?v=j6niTA1AMws",
        "yt_section": (420.0, 452.0),
        "trim_window": (12.35, 27.95),
        "anchor_text": (
            "I look for a business where I think I know what in a general way is going to happen. "
            "If you buy a bond you know exactly what's going to happen, assuming it's a good bond, a U.S. government bond. "
            "If it says 9% coupons, you know what the 9% coupons are going to be for maybe 30 years if it's a 30-year bond."
        ),
    },
}


def _write_stub_anchor_wav(dst_wav: Path, *, freq_hz: float, duration_s: float = 4.0) -> float:
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    sr = DRAMA3_ANCHOR_SAMPLE_RATE
    nframes = int(round(duration_s * sr))
    buf = bytearray(nframes * 2)
    two_pi_f = 2.0 * math.pi * freq_hz / sr
    for i in range(nframes):
        val = int(9500.0 * math.sin(two_pi_f * i))
        buf[i * 2] = val & 0xFF
        buf[i * 2 + 1] = (val >> 8) & 0xFF
    with wave.open(str(dst_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(bytes(buf))
    return round(duration_s, 3)


def _condition_studio_anchor_slice(
    src_media: Path,
    dst_wav: Path,
    *,
    start_s: float = 0.0,
    end_s: float = 0.0,
) -> float:
    """Slice with sample-accurate `atrim+asetpts` and level to 44.1kHz mono -16 LUFS PCM16 (no muffling afftdn)."""
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    filters: list[str] = []
    if end_s > start_s:
        dur = end_s - start_s
        filters.append(f"atrim=start={start_s:.2f}:end={end_s:.2f},asetpts=PTS-STARTPTS")
        filters.append(f"highpass=f=75,afade=t=in:st=0:d=0.04,afade=t=out:st={max(0.1, dur - 0.06):.2f}:d=0.06")
    else:
        filters.append("highpass=f=75,afade=t=in:st=0:d=0.03")
    filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
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
            str(dst_wav),
        ],
        check=True,
    )
    return round(probe_duration_seconds(dst_wav), 3)


def _transcribe_verbatim_whisper(wav_path: Path, language: str, whisper_model_size: str = "small") -> str:
    """Transcribe exact spoken words in `wav_path` when a custom anchor has no `.txt` sidecar."""
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
    segments, _ = model.transcribe(audio_16k, language=language, beam_size=5, vad_filter=True)
    sep = " " if language == "en" else ""
    return sep.join(seg.text.strip() for seg in segments if seg.text.strip()).strip()


def _download_yt_studio_slice(
    yt_url: str,
    section: tuple[float, float],
    trim_window: tuple[float, float],
    tmp_dir: Path,
    dst_wav: Path,
    role_id: str,
) -> float:
    import os

    env = os.environ.copy()
    for extra_p in ("/tools/node/bin", "/usr/local/bin"):
        if Path(extra_p).is_dir() and extra_p not in env.get("PATH", ""):
            env["PATH"] = f"{extra_p}:{env.get('PATH', '')}"
    ytdlp_bin = shutil.which("yt-dlp", path=env.get("PATH"))
    if not ytdlp_bin:
        raise RuntimeError(f"[{role_id}] Missing bundled voice_anchors/{role_id}.wav and yt-dlp is not on PATH.")

    dl_cmd = [ytdlp_bin]
    if shutil.which("node", path=env.get("PATH")):
        dl_cmd.extend(["--js-runtimes", "node"])
    tmpl = tmp_dir / f"{role_id}_yt.%(ext)s"
    for old in tmp_dir.glob(f"{role_id}_yt.*"):
        old.unlink(missing_ok=True)
    dl_cmd.extend(
        [
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "-f",
            "bestaudio/best",
            "--download-sections",
            f"*{section[0]:.1f}-{section[1]:.1f}",
            "-o",
            str(tmpl),
            yt_url,
        ]
    )
    subprocess.run(dl_cmd, env=env, check=True, timeout=120)
    downloaded = sorted(tmp_dir.glob(f"{role_id}_yt.*"))
    if not downloaded:
        raise RuntimeError(f"[{role_id}] yt-dlp returned no media for {yt_url}")
    return _condition_studio_anchor_slice(
        downloaded[0],
        dst_wav,
        start_s=trim_window[0],
        end_s=trim_window[1],
    )


def prepare_all_buffett_anchors(
    *,
    registry_path: Path,
    output_dir: Path,
    custom_anchors_dir: Path | None = None,
    buffett_source: Path | None = None,
    buffett_start_s: float = 0.0,
    buffett_duration_s: float = 16.0,
    whisper_size: str = "small",
    offline_stub: bool = False,
) -> dict[str, Any]:
    """Build real-human `voice_anchors/*.wav` + `voice_cast_drama3.json` inside `output_dir` (0% edge-tts)."""
    registry = VoiceCastingRegistry.load(registry_path)
    anchors_dir = output_dir / "voice_anchors"
    tmp_dir = output_dir / "_anchor_prep_tmp"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Search order for curated real-human anchors:
    # 1) Explicit --custom-anchors-dir or <output_dir>/custom_anchors
    # 2) Bundled repo anchors next to voice_casting_registry.json (`00_节目圣经与第一季12期总纲/voice_anchors`)
    bundled_repo_anchors_dir = registry_path.resolve().parent / "voice_anchors"
    custom_dir = custom_anchors_dir or (output_dir / "custom_anchors")

    cast_entries: dict[str, dict[str, Any]] = {}
    role_freqs = {
        "host_zhiwei": 295.0,
        "guest_huaiyuan": 195.0,
        "guest_laozhou": 165.0,
        "buffett_prime_en": 180.0,
    }

    for role_id in ("host_zhiwei", "guest_huaiyuan", "guest_laozhou", "buffett_prime_en"):
        prof = registry.resolve_role(role_id)
        assert prof is not None
        rel_wav = f"voice_anchors/{role_id}.wav"
        dst_wav = output_dir / rel_wav
        spec = REAL_HUMAN_ANCHOR_SPECS[role_id]
        anchor_text = ""
        source_note = ""

        custom_candidates: list[Path] = []
        if role_id == "buffett_prime_en" and buffett_source and buffett_source.is_file():
            custom_candidates.append(buffett_source)
        if custom_dir.is_dir():
            custom_candidates.extend(
                p for p in sorted(custom_dir.glob(f"{role_id}.*")) if p.suffix.lower() in (".wav", ".mp3", ".m4a", ".flac")
            )
        bundled_wav = bundled_repo_anchors_dir / f"{role_id}.wav"

        if offline_stub:
            dur_s = _write_stub_anchor_wav(dst_wav, freq_hz=role_freqs[role_id], duration_s=4.2)
            anchor_text = str(spec["anchor_text"])
            source_note = "offline_synthetic_stub"
        elif custom_candidates:
            src_file = custom_candidates[0]
            txt_sidecar = src_file.with_suffix(".txt")
            if role_id == "buffett_prime_en" and buffett_source and src_file == buffett_source and buffett_duration_s > 0:
                dur_s = _condition_studio_anchor_slice(
                    src_file,
                    dst_wav,
                    start_s=buffett_start_s,
                    end_s=buffett_start_s + buffett_duration_s,
                )
            else:
                dur_s = convert_to_drama3_anchor_wav(src_file, dst_wav)

            if txt_sidecar.is_file() and txt_sidecar.read_text(encoding="utf-8").strip():
                anchor_text = txt_sidecar.read_text(encoding="utf-8").strip()
            else:
                w_lang = "en" if prof.language_code == "en" else "zh"
                anchor_text = _transcribe_verbatim_whisper(dst_wav, language=w_lang, whisper_model_size=whisper_size)
            source_note = f"custom_real_human_anchor:{src_file.name}"
        elif bundled_wav.is_file() and bundled_wav.stat().st_size > 10000:
            if bundled_wav.resolve() != dst_wav.resolve():
                dur_s = convert_to_drama3_anchor_wav(bundled_wav, dst_wav)
            else:
                dur_s = round(probe_duration_seconds(dst_wav), 3)
            txt_sidecar = bundled_wav.with_suffix(".txt")
            anchor_text = (
                txt_sidecar.read_text(encoding="utf-8").strip()
                if txt_sidecar.is_file() and txt_sidecar.read_text(encoding="utf-8").strip()
                else str(spec["anchor_text"])
            )
            source_note = str(spec["source_label"])
        elif "fallback_raw_url" in spec:
            dl_wav = tmp_dir / f"{role_id}_oss.wav"
            req = urllib.request.Request(str(spec["fallback_raw_url"]), headers={"User-Agent": "Mozilla/5.0"})
            dl_wav.write_bytes(urllib.request.urlopen(req, timeout=45).read())
            dur_s = convert_to_drama3_anchor_wav(dl_wav, dst_wav)
            anchor_text = str(spec["anchor_text"])
            source_note = str(spec["source_label"])
        else:
            dur_s = _download_yt_studio_slice(
                yt_url=str(spec["yt_url"]),
                section=tuple(spec["yt_section"]),  # type: ignore[arg-type]
                trim_window=tuple(spec["trim_window"]),  # type: ignore[arg-type]
                tmp_dir=tmp_dir,
                dst_wav=dst_wav,
                role_id=role_id,
            )
            anchor_text = str(spec["anchor_text"])
            source_note = str(spec["source_label"])

        cast_entries[role_id] = {
            "role_id": role_id,
            "display_name": prof.display_name,
            "tier": prof.tier,
            "gender": prof.gender,
            "age_group": prof.age_group,
            "language_code": prof.language_code,
            "vocal_register": prof.vocal_register,
            "source_voice_name": source_note,
            "anchor_wav": rel_wav,
            "anchor_duration_s": dur_s,
            "anchor_text": anchor_text,
            "default_stability": prof.default_stability,
        }

    shutil.rmtree(tmp_dir, ignore_errors=True)

    voice_cast_json = output_dir / "voice_cast_drama3.json"
    payload = {
        "project_id": registry.project_id,
        "project_title": registry.project_title,
        "domain": registry.domain,
        "anchor_schema_version": ANCHOR_SCHEMA_VERSION,
        "engine": "fishaudio/drama-3 + OpenMOSS-Team/MOSS-SoundEffect-v2.0 + ACE-Step/acestep-v15-xl-turbo-diffusers",
        "exported_at": utc_now_iso(),
        "anchor_sample_rate_hz": DRAMA3_ANCHOR_SAMPLE_RATE,
        "role_count": len(cast_entries),
        "characters": cast_entries,
    }
    voice_cast_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="《穿越周期的信》真人录音棚级四角色干音锚点制备工具 (Fish Drama 3, 0% edge-tts)")
    parser.add_argument(
        "--registry",
        default=str(
            STUDIO_DIR.parent
            / "projects"
            / "buffett_letters"
            / "00_节目圣经与第一季12期总纲"
            / "voice_casting_registry.json"
        ),
        help="Path to voice_casting_registry.json",
    )
    parser.add_argument("--output-dir", required=True, help="Target studio directory to write voice_anchors/ & voice_cast_drama3.json")
    parser.add_argument("--custom-anchors-dir", default="", help="Optional directory with user-supplied <role_id>.wav/.mp3")
    parser.add_argument("--buffett-source", default="", help="Optional path to a 1980s-90s Warren Buffett studio speech file")
    parser.add_argument("--buffett-start-s", type=float, default=0.0)
    parser.add_argument("--buffett-duration-s", type=float, default=16.0)
    parser.add_argument("--whisper-size", default="small")
    parser.add_argument("--offline-stub", action="store_true", help="Generate offline synthetic WAV stubs (for CI/dry-run)")
    args = parser.parse_args()

    res = prepare_all_buffett_anchors(
        registry_path=Path(args.registry).resolve(),
        output_dir=Path(args.output_dir).resolve(),
        custom_anchors_dir=Path(args.custom_anchors_dir).resolve() if args.custom_anchors_dir else None,
        buffett_source=Path(args.buffett_source).resolve() if args.buffett_source else None,
        buffett_start_s=args.buffett_start_s,
        buffett_duration_s=args.buffett_duration_s,
        whisper_size=args.whisper_size,
        offline_stub=args.offline_stub,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "anchor_schema_version": res["anchor_schema_version"],
                "role_count": res["role_count"],
                "roles": {
                    k: {"source": v["source_voice_name"], "duration_s": v["anchor_duration_s"]}
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
