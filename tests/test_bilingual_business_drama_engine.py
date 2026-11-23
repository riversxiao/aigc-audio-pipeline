"""Comprehensive M1 unit & real-FFmpeg DSP tests for the bilingual business drama engine."""

from __future__ import annotations

from array import array
import json
import math
from pathlib import Path
import re
import tempfile
import unittest
import wave

from aigc_audio_pipeline.adapter import export_cue_sheet_markdown
from aigc_audio_pipeline.batch_queue import measure_ebur128
from aigc_audio_pipeline.drama3_adapter import (
    _join_bilingual_units,
    export_colab_96gb_bundle,
    split_cue_into_subcues_for_drama3,
    translate_cue_to_drama3_input,
)
from aigc_audio_pipeline.elevenlabs_client import SynthesisResult, probe_duration_seconds
from aigc_audio_pipeline.mixer import (
    CHANNELS,
    SAMPLE_RATE,
    condition_dialogue_clip,
    master_episode_three_bus,
    render_audition_reel,
)
from aigc_audio_pipeline.models import (
    ALLOWED_ACOUSTIC_SPACES,
    ActMusicSpec,
    EpisodeCueSheet,
    MAX_PLAYBACK_RATE,
    MIN_PLAYBACK_RATE,
    SonicMotif,
    TimelineCue,
    VoiceCastingRegistry,
    VoiceProfile,
)
from aigc_audio_pipeline.polyphones import (
    apply_business_english_drama_polyphone_overrides,
    apply_domain_polyphone_overrides,
    compute_tts_text_override,
)
from aigc_audio_pipeline.qa import COMMON_TAG_WORDS, evaluate_dialogue_qa, synthesize_with_playbook_qa

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_stereo_wav(path: Path, samples: array, sr: int = SAMPLE_RATE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples.tobytes())
    return path


def _write_voiced_wav(
    path: Path,
    duration_s: float,
    *,
    amplitude: float = 0.35,
    sr: int = SAMPLE_RATE,
) -> Path:
    """Synthesize a deterministic multi-harmonic voiced-speech-like stereo WAV for WSOLA/DSP tests."""
    n_frames = int(round(duration_s * sr))
    fade_frames = max(1, int(0.02 * sr))
    harmonics = (
        (150.0, 0.25),
        (300.0, 0.30),
        (450.0, 0.22),
        (900.0, 0.14),
        (1500.0, 0.08),
        (2400.0, 0.04),
    )
    norm_scale = sum(w for _, w in harmonics)
    buf = array("h", [0]) * (n_frames * CHANNELS)
    for i in range(n_frames):
        t = i / sr
        env = 0.55 + 0.45 * math.sin(2.0 * math.pi * 3.5 * t)
        if i < fade_frames:
            env *= 0.5 * (1.0 - math.cos(math.pi * i / fade_frames))
        elif i >= n_frames - fade_frames:
            rem = n_frames - 1 - i
            env *= 0.5 * (1.0 - math.cos(math.pi * rem / fade_frames))
        sig = sum(w * math.sin(2.0 * math.pi * f * t) for f, w in harmonics) / norm_scale
        val = int(max(-32767, min(32767, round(32767.0 * amplitude * env * sig))))
        buf[2 * i] = val
        buf[2 * i + 1] = val
    return _write_stereo_wav(path, buf, sr=sr)


def _write_multitone_wav(
    path: Path,
    freqs_amps: list[tuple[float, float]],
    *,
    duration_s: float = 1.8,
    sr: int = SAMPLE_RATE,
) -> Path:
    """Synthesize an exact-frequency multi-band stereo probe WAV."""
    n_frames = int(round(duration_s * sr))
    fade_frames = max(1, int(0.02 * sr))
    buf = array("h", [0]) * (n_frames * CHANNELS)
    for i in range(n_frames):
        t = i / sr
        env = 1.0
        if i < fade_frames:
            env = 0.5 * (1.0 - math.cos(math.pi * i / fade_frames))
        elif i >= n_frames - fade_frames:
            rem = n_frames - 1 - i
            env = 0.5 * (1.0 - math.cos(math.pi * rem / fade_frames))
        sig = sum(amp * math.sin(2.0 * math.pi * freq * t) for freq, amp in freqs_amps)
        val = int(max(-32767, min(32767, round(32767.0 * env * sig))))
        buf[2 * i] = val
        buf[2 * i + 1] = val
    return _write_stereo_wav(path, buf, sr=sr)


def _write_burst_silence_wav(
    path: Path,
    *,
    burst_s: float = 0.15,
    silence_s: float = 0.25,
    amplitude: float = 0.45,
    sr: int = SAMPLE_RATE,
) -> Path:
    """Synthesize a clean multi-harmonic burst followed by silence for impulse/reflection checks."""
    burst_frames = int(round(burst_s * sr))
    total_frames = int(round((burst_s + silence_s) * sr))
    fade_frames = max(1, int(0.005 * sr))
    buf = array("h", [0]) * (total_frames * CHANNELS)
    for i in range(burst_frames):
        t = i / sr
        env = 1.0
        if i < fade_frames:
            env = i / fade_frames
        elif i >= burst_frames - fade_frames:
            env = max(0.0, (burst_frames - 1 - i) / fade_frames)
        sig = (
            0.50 * math.sin(2.0 * math.pi * 440.0 * t)
            + 0.30 * math.sin(2.0 * math.pi * 1100.0 * t)
            + 0.20 * math.sin(2.0 * math.pi * 2200.0 * t)
        )
        val = int(max(-32767, min(32767, round(32767.0 * amplitude * env * sig))))
        buf[2 * i] = val
        buf[2 * i + 1] = val
    return _write_stereo_wav(path, buf, sr=sr)


def _read_stereo_pcm(path: Path) -> tuple[array, int]:
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        if nch != 2 or wf.getsampwidth() != 2:
            raise AssertionError(f"Expected 48kHz stereo PCM16 WAV, got {sr}Hz {nch}ch width={wf.getsampwidth()}")
        raw = wf.readframes(wf.getnframes())
    samples = array("h")
    samples.frombytes(raw)
    return samples, sr


def _pcm_peak_and_rms(samples: array, start_frame: int = 0, end_frame: int | None = None) -> tuple[float, float]:
    total_frames = len(samples) // CHANNELS
    s0 = max(0, start_frame) * CHANNELS
    s1 = min(total_frames, total_frames if end_frame is None else end_frame) * CHANNELS
    seg = samples[s0:s1]
    if not seg:
        return 0.0, 0.0
    peak = max(abs(x) for x in seg) / 32767.0
    rms = math.sqrt(sum(int(x) * int(x) for x in seg) / len(seg)) / 32767.0
    return peak, rms


def _goertzel_rms(
    stereo_samples: array,
    freq_hz: float,
    *,
    sr: int = SAMPLE_RATE,
    margin_s: float = 0.15,
) -> float:
    """Compute narrowband DFT bin RMS on left channel via Goertzel algorithm (pure stdlib)."""
    total_frames = len(stereo_samples) // CHANNELS
    m = int(margin_s * sr)
    lo = min(total_frames // 4, m)
    hi = max(lo + 1, total_frames - lo)
    mono = [stereo_samples[2 * i] / 32767.0 for i in range(lo, hi)]
    n = len(mono)
    omega = 2.0 * math.pi * freq_hz / sr
    coeff = 2.0 * math.cos(omega)
    s_prev = 0.0
    s_prev2 = 0.0
    for x in mono:
        s = x + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    power = max(0.0, s_prev2 * s_prev2 + s_prev * s_prev - coeff * s_prev * s_prev2)
    return math.sqrt(power) / max(1, n)


def _parse_srt_ts(ts: str) -> float:
    m = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", ts.strip())
    if not m:
        raise AssertionError(f"Invalid SRT timestamp: {ts!r}")
    hh, mm, ss, ms = (int(g) for g in m.groups())
    return hh * 3600.0 + mm * 60.0 + ss + ms / 1000.0


def _parse_srt_blocks(srt_text: str) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for raw_block in re.split(r"\n{2,}", srt_text.strip()):
        lines = [ln for ln in raw_block.splitlines()]
        if not lines:
            continue
        idx = int(lines[0].strip())
        st_s, en_s = lines[1].split(" --> ")
        blocks.append(
            {
                "index": idx,
                "start_s": _parse_srt_ts(st_s),
                "end_s": _parse_srt_ts(en_s),
                "lines": lines[2:],
            }
        )
    return blocks


def _build_sample_biz_registry() -> VoiceCastingRegistry:
    return VoiceCastingRegistry(
        project_id="global_edge",
        project_title="Global Edge · 跨境底牌",
        language_code="zh-en",
        domain="business_english_drama",
        tts_model_id="fishaudio/drama-3",
        sfx_model_id="OpenMOSS-Team/MOSS-SoundEffect-v2.0",
        music_model_id="ACE-Step/acestep-v15-xl-turbo-diffusers",
        asr_model_id="faster-whisper-small-int8",
        roles={
            "lin_chen": VoiceProfile(
                role_id="lin_chen",
                display_name="林沉",
                tier="protagonist",
                gender="male",
                language_code="zh-en",
                accent_code="zh_en_bilingual_us",
                status="locked",
                voice_id="anchor_lin_chen",
            ),
            "alistair_finch": VoiceProfile(
                role_id="alistair_finch",
                display_name="阿利斯泰尔·芬奇",
                tier="antagonist",
                gender="male",
                language_code="en",
                accent_code="uk_london_rp",
                status="locked",
                voice_id="anchor_alistair",
            ),
            "victoria_vance": VoiceProfile(
                role_id="victoria_vance",
                display_name="维多利亚·万斯",
                tier="antagonist",
                gender="female",
                language_code="en",
                accent_code="us_silicon_valley",
                status="locked",
                voice_id="anchor_victoria",
            ),
        },
        sonic_motifs={
            "glass_ping": SonicMotif(
                motif_id="glass_ping",
                name="Boardroom Glass Ping",
                description="Subtle executive phone buzz on glass desk",
                sfx_prompt="Subtle muted smartphone vibration on glass boardroom table, short",
                duration_seconds=1.2,
            )
        },
    )


class ModelsSchemaExtensionTests(unittest.TestCase):
    def test_allowed_acoustic_spaces_and_validation(self) -> None:
        expected_spaces = {
            "dry",
            "mental_realm",
            "memory_echo",
            "vast_hall",
            "studio_warm",
            "vintage_study",
            "inner_monologue",
            "boardroom",
            "phone_call",
        }
        self.assertTrue(expected_spaces.issubset(set(ALLOWED_ACOUSTIC_SPACES)))

        reg = _build_sample_biz_registry()
        for space in ("inner_monologue", "boardroom", "phone_call"):
            sheet = EpisodeCueSheet(
                episode_id="E001_VA",
                chapter_number=1,
                title="Margin War",
                mode="bilingual_business_drama",
                acts=[ActMusicSpec(act_id="act1", title="Boardroom", bgm_prompt="minimalist cello tension")],
                cues=[
                    TimelineCue(
                        cue_id="c1",
                        act_id="act1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        language_code="en",
                        text="[icy polite] That is a phantom number.",
                        acoustic_space=space,
                    )
                ],
            )
            self.assertEqual(sheet.validate(registry=reg, require_locked_voices=True), [])

        bad_sheet = EpisodeCueSheet(
            episode_id="E001_BAD",
            chapter_number=1,
            title="Bad Space",
            mode="bilingual_business_drama",
            acts=[ActMusicSpec(act_id="act1", title="Boardroom", bgm_prompt="minimalist pulse")],
            cues=[
                TimelineCue(
                    cue_id="c1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[measured] Hold the line.",
                    acoustic_space="conference_hall",
                )
            ],
        )
        errs = bad_sheet.validate(registry=reg)
        self.assertTrue(any("Unknown acoustic_space" in e for e in errs))

    def test_episode_cue_sheet_modes_and_legacy_preservation(self) -> None:
        reg = _build_sample_biz_registry()
        for mode in (
            "bilingual_business_drama",
            "immersive_audiobook_drama",
            "condensed_radio_drama",
            "podcast_roundtable",
            "audition_pack",
            "radio_drama",
        ):
            sheet = EpisodeCueSheet(
                episode_id="E_MODE",
                chapter_number=1,
                title="Mode Check",
                mode=mode,  # type: ignore[arg-type]
                acts=[ActMusicSpec(act_id="act1", title="Act 1", bgm_prompt="ambient pad")],
                cues=[
                    TimelineCue(
                        cue_id="c1",
                        act_id="act1",
                        kind="dialogue",
                        role_id="lin_chen",
                        language_code="zh-en",
                        text="[aside] 表面客气，底牌全是刀。",
                    )
                ],
            )
            self.assertEqual(sheet.validate(registry=reg), [], msg=f"Failed for mode={mode}")

    def test_voice_profile_accent_code_and_registry_round_trip(self) -> None:
        default_prof = VoiceProfile(role_id="r1", display_name="Role One")
        self.assertEqual(default_prof.accent_code, "")

        rp_prof = VoiceProfile(
            role_id="alistair_finch",
            display_name="Alistair Finch",
            language_code="en",
            accent_code="uk_london_rp",
        )
        rp_dict = rp_prof.to_dict()
        self.assertEqual(rp_dict["accent_code"], "uk_london_rp")
        self.assertEqual(VoiceProfile.from_dict(rp_dict), rp_prof)

        legacy_dict = dict(rp_dict)
        legacy_dict.pop("accent_code")
        rebuilt_legacy = VoiceProfile.from_dict(legacy_dict)
        self.assertEqual(rebuilt_legacy.accent_code, "")

        reg = _build_sample_biz_registry()
        self.assertEqual(VoiceCastingRegistry.from_dict(reg.to_dict()), reg)
        with tempfile.TemporaryDirectory() as td:
            reg_path = Path(td) / "registry.json"
            reg.save(reg_path)
            loaded = VoiceCastingRegistry.load(reg_path)
            self.assertEqual(loaded.roles["alistair_finch"].accent_code, "uk_london_rp")
            self.assertEqual(loaded.domain, "business_english_drama")

        # Verify real committed legacy Buffett registry loads with empty accent_code defaults
        buffett_reg_path = (
            REPO_ROOT
            / "projects"
            / "buffett_letters"
            / "00_节目圣经与第一季12期总纲"
            / "voice_casting_registry.json"
        )
        if buffett_reg_path.is_file():
            buffett_reg = VoiceCastingRegistry.load(buffett_reg_path)
            self.assertTrue(len(buffett_reg.roles) > 0)
            for prof in buffett_reg.roles.values():
                self.assertEqual(prof.accent_code, "")

    def test_timeline_cue_playback_rate_boundary_and_type_matrix(self) -> None:
        self.assertAlmostEqual(MIN_PLAYBACK_RATE, 0.65)
        self.assertAlmostEqual(MAX_PLAYBACK_RATE, 1.35)
        reg = _build_sample_biz_registry()

        def _validate_rate(rate_val: object, *, kind: str = "dialogue") -> list[str]:
            if kind == "dialogue":
                cue = TimelineCue(
                    cue_id="c_rate",
                    act_id="act1",
                    kind="dialogue",
                    role_id="victoria_vance",
                    language_code="en",
                    text="[measured] Pick your favorite number.",
                    playback_rate=rate_val,  # type: ignore[arg-type]
                )
            else:
                cue = TimelineCue(
                    cue_id="c_sfx",
                    act_id="act1",
                    kind="sfx",
                    sfx_prompt="soft glass tap",
                    duration_seconds=1.2,
                    playback_rate=rate_val,  # type: ignore[arg-type]
                )
            sheet = EpisodeCueSheet(
                episode_id="E_RATE",
                chapter_number=1,
                title="Rate Matrix",
                mode="bilingual_business_drama",
                acts=[ActMusicSpec(act_id="act1", title="Act 1", bgm_prompt="ambient tension")],
                cues=[cue],
            )
            return sheet.validate(registry=reg)

        for valid_rate in (0.65, 0.8, 1, 1.0, 1.35):
            self.assertEqual(_validate_rate(valid_rate), [], msg=f"Unexpected failure for rate={valid_rate!r}")
        self.assertEqual(_validate_rate(1.0, kind="sfx"), [])

        invalid_rates: list[object] = [
            0.64,
            0.6499,
            1.36,
            1.3501,
            0.0,
            -0.8,
            float("nan"),
            float("inf"),
            float("-inf"),
            True,
            False,
            "0.8",
            None,
        ]
        for bad_rate in invalid_rates:
            errs = _validate_rate(bad_rate)
            self.assertTrue(
                any("playback_rate" in e for e in errs),
                msg=f"Expected playback_rate validation error for {bad_rate!r}, got {errs!r}",
            )

        # Invalid playback_rate on SFX cues must also be caught
        for bad_sfx_rate in (0.5, True, "0.8"):
            sfx_errs = _validate_rate(bad_sfx_rate, kind="sfx")
            self.assertTrue(
                any("playback_rate" in e for e in sfx_errs),
                msg=f"Expected SFX playback_rate error for {bad_sfx_rate!r}, got {sfx_errs!r}",
            )

        # Verify from_dict preserves raw malformed types instead of silently coercing via float()
        for raw_bad in (True, "0.8", None):
            raw_sheet = {
                "episode_id": "E_RAW",
                "chapter_number": 1,
                "title": "Raw Unpack",
                "mode": "bilingual_business_drama",
                "acts": [{"act_id": "act1", "title": "A1", "bgm_prompt": "pulse"}],
                "cues": [
                    {
                        "cue_id": "c1",
                        "act_id": "act1",
                        "kind": "dialogue",
                        "role_id": "victoria_vance",
                        "language_code": "en",
                        "text": "That is a phantom number.",
                        "playback_rate": raw_bad,
                    }
                ],
            }
            rebuilt = EpisodeCueSheet.from_dict(raw_sheet)
            errs = rebuilt.validate(registry=reg)
            self.assertTrue(any("playback_rate" in e for e in errs), msg=f"from_dict coerced {raw_bad!r}")

    def test_subtitle_translation_isolation_and_type_validation(self) -> None:
        reg = _build_sample_biz_registry()
        prof = reg.roles["alistair_finch"]
        cue = TimelineCue(
            cue_id="c_tr",
            act_id="act1",
            kind="dialogue",
            role_id="alistair_finch",
            language_code="en",
            text="[icy polite] That is a phantom number.",
            subtitle_translation="[潜台词] 那只是个账面虚数。",
            acoustic_space="boardroom",
        )
        sheet = EpisodeCueSheet(
            episode_id="E_TR",
            chapter_number=1,
            title="Translation Isolation",
            mode="bilingual_business_drama",
            acts=[ActMusicSpec(act_id="act1", title="Act 1", bgm_prompt="cello pulse")],
            cues=[cue],
        )
        self.assertEqual(sheet.validate(registry=reg), [])

        # Confirm subtitle_translation NEVER leaks into Drama 3 TTS input across all retry attempts
        for attempt in (1, 2, 3):
            d3 = translate_cue_to_drama3_input(cue, prof, attempt=attempt, domain="business_english_drama")
            self.assertNotIn("潜台词", d3)
            self.assertNotIn("账面虚数", d3)

        # Whitespace-only subtitle_translation is allowed
        ws_cue = TimelineCue(
            cue_id="c_ws",
            act_id="act1",
            kind="dialogue",
            role_id="alistair_finch",
            language_code="en",
            text="That is not a cash loss.",
            subtitle_translation="   ",
        )
        sheet.cues = [ws_cue]
        self.assertEqual(sheet.validate(registry=reg), [])

        # Non-string subtitle_translation is rejected
        for bad_tr in (123, ["x"], True, None):
            bad_cue = TimelineCue(
                cue_id="c_bad_tr",
                act_id="act1",
                kind="dialogue",
                role_id="alistair_finch",
                language_code="en",
                text="That is not a cash loss.",
                subtitle_translation=bad_tr,  # type: ignore[arg-type]
            )
            sheet.cues = [bad_cue]
            errs = sheet.validate(registry=reg)
            self.assertTrue(
                any("subtitle_translation" in e for e in errs),
                msg=f"Expected subtitle_translation error for {bad_tr!r}, got {errs!r}",
            )

    def test_episode_cue_sheet_round_trip_and_legacy_json_compatibility(self) -> None:
        sheet = EpisodeCueSheet(
            episode_id="E001_VA",
            chapter_number=1,
            title="跨境底牌",
            mode="bilingual_business_drama",
            source_chapter_file="season1_24ep_map.json#E001",
            acts=[ActMusicSpec(act_id="act1", title="Boardroom", bgm_prompt="minimalist tension")],
            cues=[
                TimelineCue(
                    cue_id="c1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[measured] Pick your favorite number.",
                    acoustic_space="boardroom",
                    playback_rate=0.8,
                    subtitle_translation="挑一个你最喜欢的数字。",
                )
            ],
        )
        self.assertEqual(EpisodeCueSheet.from_dict(sheet.to_dict()), sheet)

        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "ep.json"
            sheet.save(out_json)
            loaded = EpisodeCueSheet.load(out_json)
            self.assertEqual(loaded, sheet)
            self.assertAlmostEqual(loaded.cues[0].playback_rate, 0.8)
            self.assertEqual(loaded.cues[0].subtitle_translation, "挑一个你最喜欢的数字。")

        # Legacy dict omitting playback_rate and subtitle_translation
        legacy_raw = sheet.to_dict()
        legacy_raw["cues"][0].pop("playback_rate")
        legacy_raw["cues"][0].pop("subtitle_translation")
        rebuilt_legacy = EpisodeCueSheet.from_dict(legacy_raw)
        self.assertEqual(rebuilt_legacy.cues[0].playback_rate, 1.0)
        self.assertEqual(rebuilt_legacy.cues[0].subtitle_translation, "")

        # Real committed template JSON
        tpl_path = REPO_ROOT / "templates" / "episode_cue_sheet.example.json"
        if tpl_path.is_file():
            tpl = EpisodeCueSheet.load(tpl_path)
            self.assertTrue(len(tpl.cues) > 0)
            for c in tpl.cues:
                self.assertEqual(c.playback_rate, 1.0)
                self.assertEqual(c.subtitle_translation, "")

    def test_gap_after_s_nan_inf_bool_and_type_validation(self) -> None:
        reg = _build_sample_biz_registry()

        def _validate_gap(gap_val: object) -> list[str]:
            sheet = EpisodeCueSheet(
                episode_id="E_GAP",
                chapter_number=1,
                title="Gap Matrix",
                mode="bilingual_business_drama",
                acts=[ActMusicSpec(act_id="act1", title="Act 1", bgm_prompt="ambient pulse")],
                cues=[
                    TimelineCue(
                        cue_id="c_gap",
                        act_id="act1",
                        kind="dialogue",
                        role_id="victoria_vance",
                        language_code="en",
                        text="[measured] Pick your favorite number.",
                        gap_after_s=gap_val,  # type: ignore[arg-type]
                    )
                ],
            )
            return sheet.validate(registry=reg)

        for valid_gap in (-0.25, -0.05, 0, 0.0, 1.8, 10.0):
            self.assertEqual(_validate_gap(valid_gap), [], msg=f"Unexpected failure for gap={valid_gap!r}")

        for bad_gap in (-0.26, 10.01, float("nan"), float("inf"), float("-inf"), True, False, "0.2", None):
            errs = _validate_gap(bad_gap)
            self.assertTrue(
                any("gap_after_s" in e for e in errs),
                msg=f"Expected gap_after_s validation error for {bad_gap!r}, got {errs!r}",
            )


class MixerDSPAndSRTTests(unittest.TestCase):
    def test_condition_dialogue_clip_atempo_slow_fast_and_guards(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            raw_wav = _write_voiced_wav(tmp / "voiced_2s.wav", duration_s=2.0, amplitude=0.35)

            # 0.80x slow breakdown -> ~2.50s (1.25x +/- 5%), no clipping, non-silent, valid LUFS
            slow_wav = condition_dialogue_clip(raw_wav, tmp / "slow_080.wav", playback_rate=0.80)
            slow_dur = probe_duration_seconds(slow_wav)
            self.assertGreaterEqual(slow_dur, 2.375)
            self.assertLessEqual(slow_dur, 2.625)
            slow_samples, sr = _read_stereo_pcm(slow_wav)
            self.assertEqual(sr, SAMPLE_RATE)
            slow_peak, slow_rms = _pcm_peak_and_rms(slow_samples)
            self.assertLessEqual(slow_peak, 0.99)
            self.assertGreater(slow_rms, 0.02)
            slow_lufs, slow_tp = measure_ebur128(slow_wav)
            self.assertGreaterEqual(slow_lufs, -19.0)
            self.assertLessEqual(slow_lufs, -13.0)
            self.assertLessEqual(slow_tp, -0.8)

            # 1.25x fast compression -> ~1.60s (0.80x +/- 5%), no clipping, non-silent
            fast_wav = condition_dialogue_clip(raw_wav, tmp / "fast_125.wav", playback_rate=1.25)
            fast_dur = probe_duration_seconds(fast_wav)
            self.assertGreaterEqual(fast_dur, 1.52)
            self.assertLessEqual(fast_dur, 1.68)
            fast_samples, _ = _read_stereo_pcm(fast_wav)
            fast_peak, fast_rms = _pcm_peak_and_rms(fast_samples)
            self.assertLessEqual(fast_peak, 0.99)
            self.assertGreater(fast_rms, 0.02)

            # Guard against invalid playback_rate inputs
            for bad_rate in (0.4, 2.5, 0.0, -0.8, float("nan"), float("inf"), True, False, "0.8", None):
                with self.assertRaises(ValueError, msg=f"Expected ValueError for playback_rate={bad_rate!r}"):
                    condition_dialogue_clip(
                        raw_wav,
                        tmp / "bad.wav",
                        playback_rate=bad_rate,  # type: ignore[arg-type]
                    )

    def test_condition_dialogue_clip_stretched_duration_loudnorm_gate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            # Quiet 1.2s clip (~-30 dBFS): at 0.80x -> 1.5s >= 1.4s (loudnorm) vs at 1.0x -> 1.2s < 1.4s (limiter only)
            quiet_12 = _write_voiced_wav(tmp / "quiet_12.wav", duration_s=1.2, amplitude=0.03)
            out_12_slow = condition_dialogue_clip(quiet_12, tmp / "quiet_12_080.wav", playback_rate=0.80)
            out_12_orig = condition_dialogue_clip(quiet_12, tmp / "quiet_12_100.wav", playback_rate=1.0)
            lufs_12_slow, _ = measure_ebur128(out_12_slow)
            lufs_12_orig, _ = measure_ebur128(out_12_orig)
            _, rms_12_slow = _pcm_peak_and_rms(_read_stereo_pcm(out_12_slow)[0])
            _, rms_12_orig = _pcm_peak_and_rms(_read_stereo_pcm(out_12_orig)[0])
            self.assertGreater(rms_12_slow, 0.05)
            self.assertGreater(rms_12_orig, 0.003)
            self.assertGreaterEqual(lufs_12_slow - lufs_12_orig, 6.0)
            self.assertGreaterEqual(20.0 * math.log10(rms_12_slow / rms_12_orig), 6.0)

            # Quiet 1.5s clip: at 1.0x -> 1.5s >= 1.4s (loudnorm) vs at 1.25x -> 1.2s < 1.4s (limiter only)
            quiet_15 = _write_voiced_wav(tmp / "quiet_15.wav", duration_s=1.5, amplitude=0.03)
            out_15_orig = condition_dialogue_clip(quiet_15, tmp / "quiet_15_100.wav", playback_rate=1.0)
            out_15_fast = condition_dialogue_clip(quiet_15, tmp / "quiet_15_125.wav", playback_rate=1.25)
            lufs_15_orig, _ = measure_ebur128(out_15_orig)
            lufs_15_fast, _ = measure_ebur128(out_15_fast)
            _, rms_15_orig = _pcm_peak_and_rms(_read_stereo_pcm(out_15_orig)[0])
            _, rms_15_fast = _pcm_peak_and_rms(_read_stereo_pcm(out_15_fast)[0])
            self.assertGreater(rms_15_orig, 0.05)
            self.assertGreater(rms_15_fast, 0.003)
            self.assertGreaterEqual(lufs_15_orig - lufs_15_fast, 6.0)
            self.assertGreaterEqual(20.0 * math.log10(rms_15_orig / rms_15_fast), 6.0)

    def test_corporate_acoustic_spaces_dsp_characteristics(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)

            # 1. phone_call bandpass attenuation vs dry on (100Hz, 1000Hz, 6500Hz)
            phone_probe = _write_multitone_wav(
                tmp / "probe_phone.wav",
                [(100.0, 0.25), (1000.0, 0.25), (6500.0, 0.25)],
                duration_s=1.8,
            )
            dry_phone_wav = condition_dialogue_clip(phone_probe, tmp / "dry_phone.wav", acoustic_space="dry")
            call_wav = condition_dialogue_clip(phone_probe, tmp / "phone_call.wav", acoustic_space="phone_call")
            dry_p_samples, _ = _read_stereo_pcm(dry_phone_wav)
            call_samples, _ = _read_stereo_pcm(call_wav)
            call_peak, call_rms = _pcm_peak_and_rms(call_samples)
            self.assertLessEqual(call_peak, 0.99)
            self.assertGreater(call_rms, 0.02)

            dry_low_ratio = _goertzel_rms(dry_p_samples, 100.0) / max(1e-9, _goertzel_rms(dry_p_samples, 1000.0))
            call_low_ratio = _goertzel_rms(call_samples, 100.0) / max(1e-9, _goertzel_rms(call_samples, 1000.0))
            low_atten_db = 20.0 * math.log10(dry_low_ratio / max(1e-9, call_low_ratio))
            self.assertGreaterEqual(low_atten_db, 10.0)

            dry_hi_ratio = _goertzel_rms(dry_p_samples, 6500.0) / max(1e-9, _goertzel_rms(dry_p_samples, 1000.0))
            call_hi_ratio = _goertzel_rms(call_samples, 6500.0) / max(1e-9, _goertzel_rms(call_samples, 1000.0))
            hi_atten_db = 20.0 * math.log10(dry_hi_ratio / max(1e-9, call_hi_ratio))
            self.assertGreaterEqual(hi_atten_db, 8.0)

            # 2. inner_monologue proximity warmth boost vs dry AND zero cavern echo vs mental_realm
            mono_probe = _write_multitone_wav(
                tmp / "probe_inner.wav",
                [(150.0, 0.22), (1000.0, 0.22), (3200.0, 0.22)],
                duration_s=1.8,
            )
            dry_inner_wav = condition_dialogue_clip(mono_probe, tmp / "dry_inner.wav", acoustic_space="dry")
            inner_wav = condition_dialogue_clip(mono_probe, tmp / "inner_mono.wav", acoustic_space="inner_monologue")
            dry_i_samples, _ = _read_stereo_pcm(dry_inner_wav)
            inner_samples, _ = _read_stereo_pcm(inner_wav)
            dry_150_ratio = _goertzel_rms(dry_i_samples, 150.0) / max(1e-9, _goertzel_rms(dry_i_samples, 1000.0))
            inner_150_ratio = _goertzel_rms(inner_samples, 150.0) / max(1e-9, _goertzel_rms(inner_samples, 1000.0))
            warmth_boost_db = 20.0 * math.log10(inner_150_ratio / max(1e-9, dry_150_ratio))
            self.assertGreaterEqual(warmth_boost_db, 1.0)

            burst_long = _write_burst_silence_wav(tmp / "burst_long.wav", burst_s=0.15, silence_s=0.35)
            inner_burst_wav = condition_dialogue_clip(burst_long, tmp / "inner_b.wav", acoustic_space="inner_monologue")
            mental_burst_wav = condition_dialogue_clip(burst_long, tmp / "mental_b.wav", acoustic_space="mental_realm")
            inner_b_samples, _ = _read_stereo_pcm(inner_burst_wav)
            mental_b_samples, _ = _read_stereo_pcm(mental_burst_wav)
            _, inner_tail_rms = _pcm_peak_and_rms(inner_b_samples, int(0.20 * SAMPLE_RATE), int(0.35 * SAMPLE_RATE))
            _, mental_tail_rms = _pcm_peak_and_rms(mental_b_samples, int(0.20 * SAMPLE_RATE), int(0.35 * SAMPLE_RATE))
            self.assertGreater(mental_tail_rms, 0.005)
            self.assertLess(inner_tail_rms, 0.5 * mental_tail_rms)

            # 3. boardroom tight early reflections without trailing silence bloat
            burst_short = _write_burst_silence_wav(tmp / "burst_short.wav", burst_s=0.15, silence_s=0.25)
            dry_b_wav = condition_dialogue_clip(burst_short, tmp / "dry_b.wav", acoustic_space="dry")
            board_b_wav = condition_dialogue_clip(burst_short, tmp / "board_b.wav", acoustic_space="boardroom")
            dry_b_samples, _ = _read_stereo_pcm(dry_b_wav)
            board_b_samples, _ = _read_stereo_pcm(board_b_wav)
            _, dry_refl_rms = _pcm_peak_and_rms(dry_b_samples, int(0.155 * SAMPLE_RATE), int(0.195 * SAMPLE_RATE))
            _, board_refl_rms = _pcm_peak_and_rms(board_b_samples, int(0.155 * SAMPLE_RATE), int(0.195 * SAMPLE_RATE))
            self.assertGreater(board_refl_rms * 32767.0, 50.0)
            self.assertGreater(board_refl_rms, 3.0 * max(1e-6, dry_refl_rms))
            self.assertLess(probe_duration_seconds(board_b_wav), 0.46)

    def test_master_episode_three_bus_playback_rate_bilingual_srt_and_ducking(self) -> None:
        reg = _build_sample_biz_registry()
        sheet = EpisodeCueSheet(
            episode_id="E001_TEST",
            chapter_number=1,
            title="硅深暗战测试",
            mode="bilingual_business_drama",
            head_pad_s=0.25,
            tail_pad_s=0.80,
            acts=[
                ActMusicSpec(
                    act_id="act1",
                    title="Boardroom Duel",
                    bgm_prompt="minimalist dark cello corporate pulse, instrumental",
                    bgm_duration_s=15.0,
                )
            ],
            cues=[
                TimelineCue(
                    cue_id="c1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    speaker_name="Alistair Finch",
                    language_code="en",
                    text="[icy polite] That is a phantom number.",
                    acoustic_space="boardroom",
                    subtitle_translation="这是第一行\n  这是第二行",
                    gap_after_s=-0.10,
                ),
                TimelineCue(
                    cue_id="c2",
                    act_id="act1",
                    kind="dialogue",
                    role_id="lin_chen",
                    speaker_name="林沉",
                    language_code="zh",
                    text="[aside] 表面客气，底牌全是刀。",
                    acoustic_space="inner_monologue",
                    subtitle_translation="",
                    gap_after_s=0.30,
                ),
                TimelineCue(
                    cue_id="c3",
                    act_id="act1",
                    kind="dialogue",
                    role_id="victoria_vance",
                    speaker_name="Victoria Vance",
                    language_code="en",
                    text="[measured] It flowed through into the income statement, not a cash loss.",
                    acoustic_space="phone_call",
                    duck_under_next=True,
                    duck_lead_in_s=2.0,
                    duck_gain=0.15,
                    subtitle_translation="ignored when ducked",
                    gap_after_s=0.20,
                ),
                TimelineCue(
                    cue_id="c4",
                    act_id="act1",
                    kind="dialogue",
                    role_id="lin_chen",
                    speaker_name="林沉",
                    language_code="zh-en",
                    text="[aside] 她在把非现金项包装成利润表冲击。",
                    acoustic_space="inner_monologue",
                    gap_after_s=-0.08,
                ),
                TimelineCue(
                    cue_id="c5",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    speaker_name="Alistair Finch",
                    language_code="en",
                    text="[coach] Pick your favorite number.",
                    acoustic_space="studio_warm",
                    playback_rate=0.80,
                    subtitle_translation="中文对照翻译",
                    gap_after_s=1.80,
                ),
            ],
        )
        self.assertEqual(sheet.validate(registry=reg, require_locked_voices=True), [])

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            cue_audio_map = {
                "c1": _write_voiced_wav(tmp / "c1.wav", duration_s=1.8),
                "c2": _write_voiced_wav(tmp / "c2.wav", duration_s=1.6),
                "c3": _write_voiced_wav(tmp / "c3.wav", duration_s=4.2),
                "c4": _write_voiced_wav(tmp / "c4.wav", duration_s=2.4),
                "c5": _write_voiced_wav(tmp / "c5.wav", duration_s=2.0),
            }
            bgm_wav = _write_multitone_wav(tmp / "bgm_act1.wav", [(110.0, 0.12), (220.0, 0.08)], duration_s=15.0)
            res = master_episode_three_bus(
                sheet,
                cue_audio_map,
                {"act1": bgm_wav},
                tmp / "out",
                registry=reg,
                workers=2,
            )

            manifest = json.loads(res["manifest_json"].read_text(encoding="utf-8"))
            tl = {item["cue_id"]: item for item in manifest["timeline"]}

            # Verify playback_rate & subtitle_translation propagated to manifest
            self.assertAlmostEqual(tl["c5"]["playback_rate"], 0.80)
            self.assertEqual(tl["c5"]["subtitle_translation"], "中文对照翻译")
            self.assertAlmostEqual(tl["c1"]["playback_rate"], 1.0)
            self.assertEqual(tl["c1"]["subtitle_translation"], "这是第一行\n  这是第二行")
            # c5 raw 2.0s at 0.80x -> stretched 2.50s +/- 5%
            self.assertGreaterEqual(tl["c5"]["duration_s"], 2.375)
            self.assertLessEqual(tl["c5"]["duration_s"], 2.625)

            # Verify both negative-gap audio overlaps in timeline
            self.assertLess(tl["c2"]["start_s"], tl["c1"]["end_s"])
            self.assertLess(tl["c5"]["start_s"], max(tl["c3"]["end_s"], tl["c4"]["end_s"]))

            # Verify SRT structure, bilingual 2-line format, ducked simultaneous-translation, and non-overlap
            srt_text = res["subtitles_srt"].read_text(encoding="utf-8")
            self.assertNotIn("ignored when ducked", srt_text)
            blocks = _parse_srt_blocks(srt_text)
            self.assertEqual([b["index"] for b in blocks], list(range(1, len(blocks) + 1)))
            for prev_b, next_b in zip(blocks, blocks[1:]):
                self.assertLessEqual(
                    prev_b["end_s"],
                    next_b["start_s"],
                    msg=f"Overlapping SRT blocks: {prev_b} vs {next_b}",
                )

            # Block 1: c1 2-line bilingual with multiline collapsed cleanly
            self.assertEqual(
                blocks[0]["lines"],
                ["【Alistair Finch】That is a phantom number.", "这是第一行 这是第二行"],
            )
            # Block 2: c2 1-line Mandarin
            self.assertEqual(blocks[1]["lines"], ["【林沉】表面客气，底牌全是刀。"])
            # Blocks 3 & 4: c3 + c4 documentary simultaneous-translation pair
            self.assertEqual(
                blocks[2]["lines"],
                ["【Victoria Vance】It flowed through into the income statement, not a cash loss."],
            )
            self.assertEqual(
                blocks[3]["lines"],
                [
                    "【林沉】她在把非现金项包装成利润表冲击。",
                    "EN: It flowed through into the income statement, not a cash loss.",
                ],
            )
            # Block 5: c5 2-line bilingual with stretched span (~2.5s)
            self.assertEqual(
                blocks[4]["lines"],
                ["【Alistair Finch】Pick your favorite number.", "中文对照翻译"],
            )
            c5_span = float(blocks[4]["end_s"]) - float(blocks[4]["start_s"])
            self.assertGreaterEqual(c5_span, 2.35)

            # Master WAV non-silent + valid EBU R128 loudness & true-peak ceiling
            master_samples, _ = _read_stereo_pcm(res["master_wav"])
            _, master_rms = _pcm_peak_and_rms(master_samples)
            self.assertGreater(master_rms, 0.02)
            lufs, tp = measure_ebur128(res["master_wav"])
            self.assertGreater(lufs, -30.0)
            self.assertLessEqual(tp, -0.8)

            # Verify render_audition_reel honors optional acoustic_space & playback_rate
            reel = render_audition_reel(
                [
                    {
                        "role_id": "alistair_finch",
                        "wav_path": str(cue_audio_map["c5"]),
                        "acoustic_space": "boardroom",
                        "playback_rate": 0.80,
                    }
                ],
                tmp / "reel",
                "audition_test",
            )
            reel_meta = json.loads(reel["manifest"].read_text(encoding="utf-8"))
            reel_item_dur = reel_meta["items"][0]["reel_end_s"] - reel_meta["items"][0]["reel_start_s"]
            self.assertGreaterEqual(reel_item_dur, 2.375)
            self.assertLessEqual(reel_item_dur, 2.625)

    def test_negative_gap_ultrashort_cues_short_duck_partner_and_sfx_overlay_never_go_backwards(self) -> None:
        reg = _build_sample_biz_registry()

        def _assert_monotonic_timeline_and_srt(res: dict[str, object], label: str) -> list[dict[str, object]]:
            manifest = json.loads(Path(str(res["manifest_json"])).read_text(encoding="utf-8"))
            timeline = manifest["timeline"]
            prev_start = -1.0
            for item in timeline:
                self.assertGreaterEqual(item["start_s"], 0.0, msg=f"{label}: negative start_s in {item}")
                self.assertGreaterEqual(
                    item["start_s"],
                    prev_start,
                    msg=f"{label}: backwards start_s {item['start_s']} < {prev_start} ({item['cue_id']})",
                )
                prev_start = item["start_s"]

            blocks = _parse_srt_blocks(Path(str(res["subtitles_srt"])).read_text(encoding="utf-8"))
            self.assertEqual([b["index"] for b in blocks], list(range(1, len(blocks) + 1)))
            for idx, blk in enumerate(blocks):
                self.assertGreaterEqual(float(blk["start_s"]), 0.0, msg=f"{label}: negative SRT start {blk}")
                self.assertLessEqual(float(blk["start_s"]), float(blk["end_s"]), msg=f"{label}: inverted SRT {blk}")
                if idx + 1 < len(blocks):
                    nxt = blocks[idx + 1]
                    self.assertLessEqual(
                        float(blk["end_s"]),
                        float(nxt["start_s"]),
                        msg=f"{label}: overlapping SRT {blk} vs {nxt}",
                    )
                    self.assertLessEqual(
                        float(blk["start_s"]),
                        float(nxt["start_s"]),
                        msg=f"{label}: backwards SRT {blk} vs {nxt}",
                    )
            return timeline

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            bgm = _write_multitone_wav(tmp / "bgm.wav", [(110.0, 0.10)], duration_s=8.0)

            # 1A: Ultra-short 0.20s + 0.28s @ 1.35x (~0.21s) + 1.00s with gap_after_s=-0.25
            short_sheet = EpisodeCueSheet(
                episode_id="E_SHORT_NEG",
                chapter_number=1,
                title="Ultra-short Crosstalk",
                mode="bilingual_business_drama",
                head_pad_s=0.25,
                tail_pad_s=0.50,
                acts=[ActMusicSpec(act_id="act1", title="Duel", bgm_prompt="pulse", bgm_duration_s=8.0)],
                cues=[
                    TimelineCue(
                        cue_id="c1",
                        act_id="act1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        language_code="en",
                        text="No.",
                        gap_after_s=-0.25,
                    ),
                    TimelineCue(
                        cue_id="c2",
                        act_id="act1",
                        kind="dialogue",
                        role_id="lin_chen",
                        language_code="zh",
                        text="等等！",
                        playback_rate=1.35,
                        gap_after_s=-0.25,
                    ),
                    TimelineCue(
                        cue_id="c3",
                        act_id="act1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        language_code="en",
                        text="Listen carefully.",
                        gap_after_s=0.30,
                    ),
                ],
            )
            self.assertEqual(short_sheet.validate(registry=reg, require_locked_voices=True), [])
            res_short = master_episode_three_bus(
                short_sheet,
                {
                    "c1": _write_voiced_wav(tmp / "s1.wav", duration_s=0.20),
                    "c2": _write_voiced_wav(tmp / "s2.wav", duration_s=0.28),
                    "c3": _write_voiced_wav(tmp / "s3.wav", duration_s=1.00),
                },
                {"act1": bgm},
                tmp / "out_short",
                registry=reg,
                workers=1,
            )
            tl_short = _assert_monotonic_timeline_and_srt(res_short, "ultrashort_neg025")
            self.assertLess(tl_short[0]["start_s"], tl_short[1]["start_s"])
            self.assertLess(tl_short[1]["start_s"], tl_short[2]["start_s"])

            # 1B: duck_under_next with short 0.15s partner having gap_after_s=-0.25
            duck_sheet = EpisodeCueSheet(
                episode_id="E_DUCK_SHORT",
                chapter_number=1,
                title="Short Duck Partner",
                mode="bilingual_business_drama",
                head_pad_s=0.25,
                tail_pad_s=0.50,
                acts=[ActMusicSpec(act_id="act1", title="Duck", bgm_prompt="pulse", bgm_duration_s=8.0)],
                cues=[
                    TimelineCue(
                        cue_id="d1",
                        act_id="act1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        language_code="en",
                        text="Short English hook.",
                        duck_under_next=True,
                        duck_lead_in_s=0.80,
                        gap_after_s=0.20,
                    ),
                    TimelineCue(
                        cue_id="d2",
                        act_id="act1",
                        kind="dialogue",
                        role_id="lin_chen",
                        language_code="zh",
                        text="对。",
                        gap_after_s=-0.25,
                    ),
                    TimelineCue(
                        cue_id="d3",
                        act_id="act1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        language_code="en",
                        text="Third line.",
                        gap_after_s=0.30,
                    ),
                ],
            )
            self.assertEqual(duck_sheet.validate(registry=reg, require_locked_voices=True), [])
            res_duck = master_episode_three_bus(
                duck_sheet,
                {
                    "d1": _write_voiced_wav(tmp / "d1.wav", duration_s=1.00),
                    "d2": _write_voiced_wav(tmp / "d2.wav", duration_s=0.15),
                    "d3": _write_voiced_wav(tmp / "d3.wav", duration_s=1.00),
                },
                {"act1": bgm},
                tmp / "out_duck",
                registry=reg,
                workers=1,
            )
            tl_duck = _assert_monotonic_timeline_and_srt(res_duck, "duck_short_partner_neg025")
            self.assertLess(tl_duck[1]["start_s"], tl_duck[2]["start_s"])

            # 1C: sfx overlay_next with head_pad_s=0.20, gap_after_s=-0.25, and unvalidated SFX playback_rate=None
            sfx_sheet = EpisodeCueSheet(
                episode_id="E_SFX_OV_NEG",
                chapter_number=1,
                title="SFX Overlay Neg Gap",
                mode="bilingual_business_drama",
                head_pad_s=0.20,
                tail_pad_s=0.50,
                acts=[ActMusicSpec(act_id="act1", title="SFX", bgm_prompt="pulse", bgm_duration_s=8.0)],
                cues=[
                    TimelineCue(
                        cue_id="sfx_ov",
                        act_id="act1",
                        kind="sfx",
                        sfx_prompt="subtle glass desk ping",
                        duration_seconds=1.0,
                        placement="overlay_next",
                        gap_after_s=-0.25,
                        playback_rate=None,  # type: ignore[arg-type]
                    ),
                    TimelineCue(
                        cue_id="d_after",
                        act_id="act1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        language_code="en",
                        text="After negative overlay.",
                        gap_after_s=0.30,
                    ),
                ],
            )
            res_sfx = master_episode_three_bus(
                sfx_sheet,
                {
                    "sfx_ov": _write_voiced_wav(tmp / "sfx.wav", duration_s=1.00),
                    "d_after": _write_voiced_wav(tmp / "after.wav", duration_s=1.80),
                },
                {"act1": bgm},
                tmp / "out_sfx",
                registry=reg,
                workers=1,
            )
            tl_sfx = _assert_monotonic_timeline_and_srt(res_sfx, "sfx_overlay_neg025")
            self.assertAlmostEqual(tl_sfx[0]["start_s"], 0.20)
            self.assertAlmostEqual(tl_sfx[1]["start_s"], 0.20)
            self.assertAlmostEqual(tl_sfx[0]["playback_rate"], 1.0)


class BusinessDramaPolyphoneTests(unittest.TestCase):
    def test_business_english_drama_positive_overrides_and_dispatch(self) -> None:
        cases = (
            ("老行当", "老航当"),
            ("硬件行业", "硬件航业"),
            ("同行都在卷", "同航都在卷"),
            ("同行业对比", "同航业对比"),
            ("同行们都懂", "同航们都懂"),
            ("银行行长签字", "银行航长签字"),
            ("投行给的估值", "投航给的估值"),
            ("外资商行", "外资商航"),
            ("季度调价", "季度条价"),
            ("估值回调", "估值回条"),
            ("股价突然回调", "股价突然回条"),
            ("机构调仓", "机构条仓"),
            ("调低毛利预期", "条低毛利预期"),
            ("调高目标价", "条高目标价"),
            ("结构调整", "结构条整"),
            ("资产重组", "资产崇组"),
            ("供应链重构", "供应链崇构"),
            ("重新报价", "崇新报价"),
            ("重塑渠道", "崇塑渠道"),
            ("重估现金流", "崇估现金流"),
            ("重定价权", "崇定价权"),
            ("突破重重关卡", "突破崇崇关卡"),
            ("多重杠杆", "多崇杠杆"),
            ("股权摊薄", "股权摊博"),
            ("薄利多销", "博利多销"),
            ("按会计准则", "按快计准则"),
            ("财务会计部", "财务快计部"),
            ("渠道差价", "渠道插价"),
            ("预期落差", "预期落插"),
            ("飞伦敦出差", "飞伦敦出拆"),
            ("非常称职", "非常衬职"),
            ("信息不对称", "信息不对衬"),
            ("算力供给紧张", "算力工己紧张"),
            ("实现软着陆", "实现软卓陆"),
            ("着手准备路演", "卓手准备路演"),
            ("着手推进项目", "卓手推进项目"),
            ("从哪着手", "从哪卓手"),
            ("着眼长期利润", "卓眼长期利润"),
            ("着眼于全球布局", "卓眼于全球布局"),
            ("着眼长远", "卓眼长远"),
            ("着眼全局", "卓眼全局"),
            ("着眼未来", "卓眼未来"),
            ("着眼大局", "卓眼大局"),
            ("着眼点很准", "卓眼点很准"),
            ("董事会着重构建海外合规体系。", "董事会卓重构建海外合规体系。"),
            ("着重演示核心功能", "卓重演示核心功能"),
            ("着重组建海外团队", "卓重组建海外团队"),
            ("我们要着重新品研发", "我们要卓重新品研发"),
            ("着重强调价格底线", "卓重强调价格底线"),
            ("着重指出核心问题", "卓重指出核心问题"),
            ("业内行话", "业内航话"),
            ("跨行业竞争", "跨航业竞争"),
            ("模型微调", "模型微条"),
            ("调优参数", "条优参数"),
            ("宏观调控", "宏观条控"),
            ("自动调节", "自动条节"),
            ("赚价差", "赚价插"),
            ("中美利差收窄", "中美利插收窄"),
            ("银行净息差", "银行净息插"),
            ("信息差", "信息插"),
            ("信息对称", "信息对衬"),
            ("供给侧改革", "工己侧改革"),
            ("供给端承压", "工己端承压"),
            ("市场供给不足", "市场工己不足"),
            ("差点露底", "差点漏底"),
            ("权重组合需要调整", "权重组合需要条整"),
            ("进行业务重组", "进行业务崇组"),
            ("削减渠道返点", "靴减渠道返点"),
            ("维多利亚·万斯", "维多利亚万斯"),
            ("阿利斯泰尔·芬奇", "阿利斯泰尔芬奇"),
            # Iteration 3 recovered positives, [V]着+重* separation, live-corpus hits & Drama 3 tagged cues
            ("我们决定调高指引", "我们决定条高指引"),
            ("决定调价", "决定条价"),
            ("决定调整", "决定条整"),
            ("从供给侧重塑成本结构", "从工己侧崇塑成本结构"),
            ("端侧重构推理引擎", "端侧崇构推理引擎"),
            ("欧美渠道价差太悬殊", "欧美渠道价插太悬殊"),
            ("别让同行看到报价", "别让同航看到报价"),
            ("忙着重组", "忙着崇组"),
            ("我们正忙着重组欧洲分销团队。", "我们正忙着崇组欧洲分销团队。"),
            ("催着重新报价", "催着崇新报价"),
            ("投资人天天催着重新报价。", "投资人天天催着崇新报价。"),
            ("试着重构", "试着崇构"),
            ("工程团队正试着重构端侧推理引擎。", "工程团队正试着崇构端侧推理引擎。"),
            ("等着重估", "等着崇估"),
            ("董事会一直在等着重估这笔资产。", "董事会一直在等着崇估这笔资产。"),
            ("想着重演", "想着崇演"),
            ("她一直想着重演去年的并购奇迹。", "她一直想着崇演去年的并购奇迹。"),
            ("面对着重重困难", "面对着崇崇困难"),
            ("面对着重重困难，我们没有退路。", "面对着崇崇困难，我们没有退路。"),
            ("着重构建", "卓重构建"),
            ("着重演示", "卓重演示"),
            ("着重组建", "卓重组建"),
            ("着重新品", "卓重新品"),
            ("着重定价", "卓重定价"),
            ("本质上就是个失真的会计数字。", "本质上就是个失真的快计数字。"),
            ("[measured] 调高目标价", "[measured] 条高目标价"),
            ("[aside] 重新报价", "[aside] 崇新报价"),
            ("[measured] 着手推进项目", "[measured] 卓手推进项目"),
            ("削减预算", "靴减预算"),
            ("削减成本", "靴减成本"),
            ("背负债务", "杯负债务"),
            ("展开角逐", "展开决逐"),
            ("银行业前景", "银航业前景"),
            ("汇率差收窄", "汇率插收窄"),
            ("山姆·奥特曼", "山姆奥特曼"),
            ("肯·格里芬", "肯格里芬"),
            ("保罗·格雷厄姆", "保罗格雷厄姆"),
            ("埃里克·施密特", "埃里克施密特"),
            ("大卫·艾因霍恩", "大卫艾因霍恩"),
            ("拉里·埃里森", "拉里埃里森"),
            ("马克·吐温", "马克吐温"),
            ("詹姆斯·佩奇", "詹姆斯佩奇"),
            ("鲍勃·奥利里", "鲍勃奥利里"),
            ("哈利·波特", "哈利波特"),
            # Iteration 4 surgical finalization positives
            ("股价回调了15%", "股价回条了15%"),
            ("大盘回调了15%", "大盘回条了15%"),
            ("估值回调了三个点", "估值回条了三个点"),
            ("股价回调了一半", "股价回条了一半"),
            ("市场回调压力", "市场回条压力"),
            ("板块回调压力", "板块回条压力"),
            ("估值回调周期", "估值回条周期"),
            ("回调抄底", "回条抄底"),
            ("芯片供给短缺", "芯片工己短缺"),
            ("压缩芯片供给。", "压缩芯片工己。"),
            ("外行人", "外航人"),
            ("内行人", "内航人"),
            ("信息差太大", "信息插太大"),
            ("信息差很大", "信息插很大"),
            ("行业内卷", "航业内卷"),
            ("行业内部", "航业内部"),
            ("财务会计准则", "财务快计准则"),
            ("管理会计报告", "管理快计报告"),
            ("四大会计师", "四大快计师"),
            ("重新定价", "崇新定价"),
            ("重新着手推进", "崇新卓手推进"),
            ("重新洗牌", "崇新洗牌"),
            ("开始重新架构", "开始崇新架构"),
            ("估值重定价", "估值崇定价"),
            ("通过重构供应链", "通过崇构供应链"),
            ("经过重新评估", "经过崇新评估"),
            ("经常出差", "经常出拆"),
            ("出差报销", "出拆报销"),
            ("套利差价", "套利插价"),
            ("屏息凝神", "丙息凝神"),
            ("屏息以待", "丙息以待"),
            ("屏息静气", "丙息静气"),
            ("屏息聆听", "丙息聆听"),
            # Iteration 5 pure-whitelist & regex-unit positives
            ("大盘回调超过5%", "大盘回条超过5%"),
            ("估值回调了三成", "估值回条了三成"),
            ("大盘回调了一半", "大盘回条了一半"),
            ("利率或风险溢价哪怕只上调200个基点", "利率或风险溢价哪怕只上条200个基点"),
            ("毛利预期下调了三个点", "毛利预期下条了三个点"),
            ("目标价下调了15%", "目标价下条了15%"),
            ("下调了20美元", "下条了20美元"),
            ("调高年度营收预期", "条高年度营收预期"),
            ("削减供给。", "靴减工己。"),
            ("台积电削减供给苹果的晶圆产能。", "台积电靴减供给苹果的晶圆产能。"),
            ("渠道价差", "渠道价插"),
            ("别向Best Buy透露任何信息差，", "别向Best Buy透露任何信息插，"),
            ("是个外行人", "是个外航人"),
            ("骗外行人", "骗外航人"),
            ("内行人一眼看出", "内航人一眼看出"),
            ("外行人看热闹，内行人看门道。", "外航人看热闹，内航人看门道。"),
            ("抢回重定价权", "抢回崇定价权"),
            ("资产重定价", "资产崇定价"),
            ("通过重定价", "通过崇定价"),
            ("欧美同行纷纷降价", "欧美同航纷纷降价"),
            ("国内同行早就出海", "国内同航早就出海"),
            ("着眼点在于", "卓眼点在于"),
            ("核心着眼点", "核心卓眼点"),
            ("着眼点。", "卓眼点。"),
            ("重新核定", "崇新核定"),
            # Iteration 6 pure-whitelist split-rule positives
            ("上调预期", "上条预期"),
            ("下调指引", "下条指引"),
            ("上调至买入", "上条至买入"),
            ("上调年度预期", "上条年度预期"),
            ("花旗下调估值", "花旗下条估值"),
            ("对比同行而言", "对比同航而言"),
            ("找同行比价", "找同航比价"),
            ("找同行对标", "找同航对标"),
            ("找同行打听", "找同航打听"),
            ("同行的估值倍数", "同航的估值倍数"),
            ("欧美同行的毛利率", "欧美同航的毛利率"),
            ("其他同行的估值", "其他同航的估值"),
            ("回调20个基点", "回条20个基点"),
            ("价格回调了15%", "价格回条了15%"),
        )
        for src, expected in cases:
            out = apply_business_english_drama_polyphone_overrides(src)
            self.assertEqual(out, expected, msg=f"Failed override for {src!r}")
            self.assertEqual(
                apply_domain_polyphone_overrides(src, domain="business_english_drama"),
                expected,
            )
            # Every positive & cascade override must be strictly idempotent across 2 passes
            self.assertEqual(
                apply_business_english_drama_polyphone_overrides(out),
                expected,
                msg=f"Non-idempotent override on {src!r}: 1st={out!r}",
            )

        self.assertEqual(
            compute_tts_text_override("这份报价非常扎实。", domain="business_english_drama"),
            "",
        )

    def test_business_english_drama_polyphone_map_structural_invariants(self) -> None:
        from aigc_audio_pipeline.polyphones import (
            BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP,
            XIANXIA_POLYPHONE_MAP,
        )

        self.assertIsInstance(BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP, tuple)
        self.assertGreater(len(BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP), 0)
        self.assertEqual(BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP[0], ("老行当", "老航当"))
        for entry in BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP:
            self.assertIsInstance(entry, tuple)
            self.assertEqual(len(entry), 2)
            self.assertIsInstance(entry[0], str)
            self.assertIsInstance(entry[1], str)

        keys = [k for k, _ in BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP]
        # 0 duplicates
        self.assertEqual(len(keys), len(set(keys)), msg="Duplicate keys in Tier A map")
        # Strictly only the 3 proven-safe 2-char entries
        short_keys = {k for k in keys if len(k) <= 2}
        self.assertEqual(short_keys, {"摊薄", "埋怨", "露馅"})
        # 0 shorter-before-longer substring ordering violations
        order_violations = [
            (keys[i], keys[j])
            for i in range(len(keys))
            for j in range(i + 1, len(keys))
            if keys[i] in keys[j]
        ]
        self.assertEqual(order_violations, [], msg=f"Shorter-before-longer violations: {order_violations}")
        # 0 value-triggers-key collisions
        val_collisions = [
            (k, v, k2)
            for k, v in BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP
            for k2 in keys
            if k2 in v
        ]
        self.assertEqual(val_collisions, [], msg=f"Value-triggers-key collisions: {val_collisions}")
        # 100% 2-pass self-idempotency across every Tier A entry
        for k, v in BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP:
            once = apply_business_english_drama_polyphone_overrides(k)
            twice = apply_business_english_drama_polyphone_overrides(once)
            self.assertEqual(once, v, msg=f"Tier A entry {k!r} drifted to {once!r} (expected {v!r})")
            self.assertEqual(once, twice, msg=f"Tier A entry {k!r} non-idempotent: 1st={once!r}, 2nd={twice!r}")
        # Zero Xianxia leakage/overlap
        xianxia_keys = {k for k, _ in XIANXIA_POLYPHONE_MAP}
        self.assertEqual(set(keys) & xianxia_keys, set())

    def test_business_english_drama_false_positive_preservation_isolation_and_idempotency(self) -> None:
        protected_phrases = (
            "重资产模式",
            "重仓科技股",
            "非常重要",
            "业务重心",
            "重力感应",
            "立刻行动",
            "坚决执行",
            "公开发行",
            "尽职调查",
            "市场调研",
            "反复强调",
            "跨部门协调",
            "利润太单薄",
            "超薄智能眼镜",
            "董事会议",
            "共同行动",
            "领投行不行",
            "领投行得通吗",
            "供应商行不行",
            "这家供应商行吗",
            "供应商行得通吗",
            "协商行程安排",
            "同行程序校验",
            "进行长期合作",
            "年内行权窗口",
            "尊重组织原则",
            "注重新品研发",
            "重重一击",
            "这副眼镜有多重",
            "撤回调研报告",
            "私下调查取证",
            "线上调研样本",
            "AI会计算得更快",
            "不会计较得失",
            "全球供应链稳定",
            # Cross-word false-positive regression matrix (live corpus + corporate Mandarin)
            "看着眼前的现状",
            "完全是在蒙着眼睛瞎写代码",
            "林沉戴着眼镜走进了会议室。",
            "戴着眼镜开会",
            "她手里拿着手机，闭着眼听完报价。",
            "盯着手机看报表",
            "拿着手机打电话",
            "看着手表算时间",
            "攥着手里的底牌",
            "闭着眼睛都能算清",
            "面临着重大风险",
            "顶着重大风险推进",
            "抓着重点不放",
            "握着重要筹码",
            "我们提供给渠道的返点方案已经发过去了。",
            "提供给客户最新报价",
            "直供给北美大渠道",
            "专供给核心客户",
            "我们正在进行业务扩张，必须执行业绩对赌。",
            "海外团队负责执行业务",
            "券商发行业务暂停",
            "智能出行业务线",
            "实行业绩对赌",
            "立刻执行话术标准",
            "硅谷最流行话题",
            "她反复强调价格底线，语调低沉得像刀锋。",
            "反复强调价值和毛利",
            "反复强调低成本优势",
            "强调低功耗与低成本",
            "她在会上强调高毛利",
            "强调高端智能硬件定位",
            "强调优化供应链",
            "强调优势明显",
            "强调整体战略协同",
            "强调控制研发预算",
            "强调节奏和现金流",
            "稍微调查一下背景",
            "稍微调研一下渠道",
            "这次发布绝不能出差错",
            "拿出差异化卖点",
            "一眼看出差异在哪里",
            "拉出差距才算赢",
            "零售商给出差评",
            "千万别暴露底牌",
            "绝不能暴露底线",
            "不能提前披露底价",
            "披露底层财务数据",
            "核心报价泄露底价",
            "这笔非现金项会计入利润表，但不会计提额外现金支出。",
            "这笔不会计入现金流",
            "年底会计提巨额减值",
            "按Token调用量会计费",
            "按美元会计价",
            "投资人更看重估值倍数",
            "投资人最看重定价权",
            "团队更注重构建壁垒",
            "严重构成违约",
            "必须慎重组建班子",
            "承重组件全部过检",
            "你们的报价差太多了",
            "报价差了一倍",
            "单价差太远",
            "我们的毛利差两个点",
            "毛利差远了",
            "消息差一点走漏",
            "绝对称得上顶级谈判",
            "工商行政合规审查",
            "给谈判先定下调子",
            "私下调阅财务底稿",
            "马上调出所有数据",
            "线下调货补仓",
            "配置好软件回调接口",
            "触发异步回调接口",
            # All 67 verbatim Iteration-2 adversarial challenger traps (BI #1-#4)
            "异步回调",
            "同步回调",
            "API异步回调超时了，眼镜端直接卡死。",
            "同步回调阻塞了主线程，必须改架构。",
            "把伦敦总监回调总部述职。",
            "这轮VC尽调高度敏感，法务必须全程盯盘。",
            "尽调节奏不能被对方牵着鼻子走。",
            "红杉尽调整整拖了三个月。",
            "尽调优先级最高的条款是专利归属。",
            "尽调控制权交给了纽约律所。",
            "猎头背调高管背景查出问题。",
            "从深圳抽调高管飞伦敦救火。",
            "从总部借调优质工程师支援量产。",
            "紧急抽调整支供应链团队去越南。",
            "这种悲观论调低估了我们的端侧护城河。",
            "产品色调高冷克制，对标顶级奢侈品。",
            "仓库里急调仓库存货发往洛杉矶。",
            "对手急着重签百思买的排他协议。",
            "这轮他们下着重注，绝不会轻易撤退。",
            "分析师盯着重磅财报不敢眨眼。",
            "媒体憋着重磅爆料准备明天发。",
            "这副眼镜戴着重不重？",
            "样机拎着重不重？",
            "她抱着手靠在玻璃幕墙前冷笑。",
            "他摆着手打断了对方CFO的发言。",
            "她翻着手册里的合规条款一字一句核对。",
            "林沉拎着手提箱走出希思罗机场。",
            "周默对着手写笔记复盘了三遍。",
            "她留着手底下的王牌一直没出。",
            "他插着手站在会议室门口。",
            "这批货先走着陆运过关。",
            "他朝着陆家嘴的摩天大楼看了一眼。",
            "按GAAP，这笔期权会计为当期费用。",
            "研发补贴会计成其他收益吗？",
            "这笔折旧会计到下个财年。",
            "这笔亏损会计在母公司账上。",
            "这笔开支会计作销售成本。",
            "否则会计成现金流缺口。",
            "新品在亚马逊评价差，退货率直接翻倍。",
            "如果用户评价差到三星以下，百思买会直接下架。",
            "去年股价差强人意，今年必须翻盘。",
            "那家外企薪资高但福利差，核心骨干留不住。",
            "连续跨三时区开会，作息差到极点。",
            "一定要确保这次量产交付不出差池。",
            "深圳产线筛出差品率高达百分之八。",
            "AI眼镜自重构成了佩戴舒适度的最大瓶颈。",
            "物流净重估算偏差导致运费超支。",
            "高关税会进一步加重估值压力。",
            "每周五的例行业务复盘取消。",
            "宏观下行业绩承压是全市场共识。",
            "周期上行业务增速自然会修复。",
            "海关放行业务今天全面恢复。",
            "结伴同行去伦敦参加路演。",
            "她是这一路最默契的同行者。",
            "不同行政区的隐私合规标准完全不同。",
            "跟投行了，别再纠结估值细节。",
            "跨境电商行销成本今年涨了三成。",
            "这番应对称不上体面。",
            "你的反对称不上正当理由。",
            "出厂前必须核对称重数据。",
            "我们已经停供给不合规的经销商。",
            "芯片产能优先保供给旗舰型号。",
            "员工在底下调侃董事会的PPT。",
            "法务已经签下调令，把他调回纽约。",
            "高管往上调任亚太区总裁。",
            "这份审计报告彻底揭露底账漏洞。",
            "他的一番话展露底气十足。",
            # Iteration 3 novel traps (aspectual verbs, hardware screens, closed boundaries, accounting modals)
            "搓着手准备",
            "背着手评估",
            "并着手准备",
            "翻着眼长叹",
            "合着眼点头",
            "把新芯片提供给端侧研发团队",
            "把备件专供给量产线",
            "抬腕亮屏，放下自动息屏，测试主屏息屏功耗",
            "Webhook回调延迟",
            "Webhook回调超过两秒",
            "微信支付回调失败",
            "举行业务",
            "履行业绩",
            "现行业态",
            "盛行业界",
            "通行业主",
            "图书发行业",
            "这次同行也很愉快",
            "两个同学同行去伦敦",
            "友商行径",
            "这副耳塞这双重不重？",
            "这笔债券会计息",
            "跨境交易会计税",
            "地磅会计重",
            "这笔开支会计票",
            "独供给北美大渠道",
            "把核心产品供给大客户",
            "从不对称呼计较",
            "商业银行业务扩张",
            "现在投行不行？",
            "这种风投行为太激进",
            "公司决定调高管去伦敦坐镇",
            "我们更侧重塑造品牌形象",
            "中微调高管去深圳",
            "人民币汇率差一点破七",
            "今年汇率差强人意",
            "这条信息差一点就泄密了",
            # All 10 newly caught static 2-char traps
            "很多职场人不是词汇差，是不懂权力场潜台词。",
            "外屏息屏功耗必须压到最低。",
            "眼镜支持抬腕亮屏息屏显示",
            "珠三角逐年扩大AI硬件产能。",
            "视角逐渐清晰",
            "合规死角逐一排查",
            "这份合同堪称职场教科书。",
            "他声称职责不在我。",
            "质差价高的硬件必然被百思买清退。",
            "最差价格",
            "股价回落差点跌破发行价。",
            "销量滑落差不多一半。",
            "这副超薄利器镜片很薄利于散热。",
            "轻薄利于佩戴",
            "信用差额度低，资信差额外加息。",
            "不能违背负债率红线，更不能违背负责人指令。",
            "违背负面清单",
            "CNC切削减薄工艺。",
            "双重点布局决定了这双重量必须减半。",
            # Iteration 4 surgical finalization traps (Reviewer 1, Reviewer 2 & Challenger 2)
            # 1. 供给 (gōng gěi — supply X to ANY company/brand/store/facility/team)
            "AWS把大部分算力供给Anthropic。",
            "英伟达把最顶级的H200芯片供给微软和Meta。",
            "台积电优先把三纳米芯片供给苹果。",
            "深圳工厂把核心产能供给百思买。",
            "台积电把高端产能供给英伟达和苹果。",
            "我们把首批硬件供给伦敦旗舰店。",
            "这家光学厂只把优质原料供给一线大厂。",
            "我们优先把新增产能供给Selfridges和Best Buy。",
            "供应商拒绝把核心硬件供给灵犀智造。",
            "上游工厂把全部产能供给苹果链。",
            "银行把低息信贷供给国企。",
            "我们只把最新产品供给VIP会员。",
            "不能把核心硬件供给竞争对手。",
            "把芯片产能供给端侧团队。",
            "把新增产能供给量产线。",
            "把这批原料供给深圳总装厂。",
            "把核心产品供给百思买",
            "把优质产能供给苹果",
            "把核心产品供给亚马逊",
            "将高端硬件供给伦敦旗舰店",
            "把核心芯片供给北美大客户",
            "把高端算力供给大客户",
            "把电力供给数据中心",
            "把原料供给深圳工厂",
            "把硬件供给端侧研发团队",
            "把商品供给本地代理商",
            "把高端芯片供给大客户。",
            "把冗余算力供给北美渠道。",
            "把新增产能供给头部品牌。",
            # 2. 重新 / 重定价 / 重* (zhòng modifiers & 着重 + 新*)
            "我们下一步着重新加坡市场。",
            "董事会着重新一轮融资。",
            "团队着重新兴市场拓展。",
            "团队更着重新的出海渠道。",
            "这轮战略着重新一代AI眼镜。",
            "着重新一代AI眼镜",
            "团队着重新架构设计。",
            "高关税会进一步加重定价压力。",
            "新关税会直接加重定价压力。",
            "这只会加重定价权流失的焦虑。",
            "高通胀进一步加重定价难题。",
            "汇率波动会加重定价难题。",
            "比起短期GMV，华尔街更重定价权。",
            "华尔街更重定价权。",
            "欧洲渠道商最重定价纪律和毛利空间。",
            "资本市场更重定价能力。",
            "这项合规条款会加重新加坡团队的税负。",
            "这轮关税直接加重新加坡转口成本。",
            "关税升级会加重新一轮融资难度。",
            "监管收紧会加重新项目的合规成本。",
            "这项政策会加重新关税冲击。",
            "高关税会加重新的供应链风险。",
            "汇兑波动加重新兴市场的利润下滑。",
            "如果利息负担加重新项目就全部冻结。",
            "算力账单不断加重新硬件团队的现金流负担。",
            "现金流恶化加重新融资谈判的被动局面。",
            "监管收紧加重新部门的预算压力。",
            "负担过重新项目很难推进。",
            "渠道压货过重新季度出货量肯定崩盘。",
            "如果税负过重新加坡子公司就得撤资。",
            "如果债务杠杆过重新团队根本接不住。",
            "包袱太重新团队扛不住。",
            "压力更重新一轮估值要打折。",
            "这笔债太重新一轮VC不敢接。",
            "智能眼镜太重新用户戴不住。",
            "首代样机还是太重新一代必须减到四十克以内。",
            "AI眼镜如果太重新增复购直接归零。",
            "对赌条件签得太重新投资人全被吓跑了。",
            "这笔并购债务太重新一轮融资根本谈不下来。",
            "违约成本极重新合同必须逐字审核。",
            "这轮对赌压力很重新CFO第一天就提了辞职。",
            "供应链角色吃重新总监必须懂深圳工厂。",
            "红杉这轮更重新兴硬件赛道。",
            "欧美客户最重新增续航指标。",
            "安全与效率并重新架构",
            "条款罚则太重组里没人敢签字。",
            "他把语气压得很重演得滴水不漏。",
            "这套方案侧重构件化设计。",
            # 3. 财务会计 / 管理会计 modal 会 + 计*
            "这笔非现金项，财务会计入利润表吗？",
            "财务会计入利润表吗？",
            "年底财务会计提减值吗？",
            "财务会计提这笔减值准备。",
            "财务会计算清楚每笔账。",
            "财务会计为当期费用吗？",
            "财务会计较那几个点吗？",
            "管理会计算成本吗",
            # 4. 回调 tech/HR callbacks & non-financial units
            "Webhook回调了三次都没响应。",
            "Webhook回调了三次全部失败！",
            "API回调了五次全部超时。",
            "SDK回调了十几次才拿到token。",
            "服务器回调了一百毫秒。",
            "总部一次性回调了三名区域总监。",
            "把海外派驻的工程师回调了二十人支援深圳产线。",
            "把伦敦总监回调了两年。",
            "客户端回调周期设成了五秒。",
            "Webhook回调风险必须在上线前压测。",
            "API回调深度嵌套导致堆栈溢出。",
            "传感器回调到位后再触发推理。",
            # 5. 出差 (得出差不多 & 剔/挑出差货)
            "两家投行得出差不多的估值。",
            "财务模型得出差不多的结论。",
            "几轮尽调得出差不多的结果。",
            "去深圳产线剔出差货",
            "到仓库挑出差货",
            # 6. Price/FX/Arbitrage/Info spreads, 行业内*/业财, 外行人, 同行嘉宾, CNC 削减, 屏息, 商行, 着眼
            "这款眼镜在英美的零售价差太多了。",
            "这两家渠道的批发价差了一倍。",
            "单品零售价差了一截",
            "出厂批发价差了十美金",
            "欧洲零售价差远了。",
            "今年海外零售价差强人意。",
            "这批货的渠道价差太多了",
            "这个零售价差一点就击穿底线了。",
            "他们的零售价差太远了。",
            "这波跨境套利差一点就踩雷爆仓。",
            "今年这笔债券套利差强人意。",
            "算下来跨境套利差得远，根本不划算。",
            "高频套利差了一毫秒。",
            "这条市场信息差太远了。",
            "两边的核心信息差很远。",
            "这两边同步的信息差得太远了。",
            "两边给的信息差了一大截。",
            "两边口径里的信息差不少。",
            "汇率差了两个点。",
            "这季度汇率差了五个点，直接吃掉一半毛利。",
            "美元兑人民币汇率差不到两分钱。",
            "今年汇率差得离谱，跨境结算亏麻了。",
            "离岸汇率差几分钱就破七了。",
            "今天的牌价汇率差半个点就触发锁汇了。",
            "英镑汇率差那么一点就跌穿底线。",
            "今天美元汇率差极了，结汇血亏。",
            "最近英镑汇率差到谷底。",
            "游戏发行业内卷严重。",
            "新能源出行业内卷加剧。",
            "传统旅行业内部洗牌。",
            "财务团队正在推行业财一体化。",
            "CFO正在进行业财融合改革。",
            "新ERP系统将实行业财分离审计。",
            "财务部全面执行业财融合。",
            "伦敦金融城窗外行人匆匆。",
            "海外行人很多",
            "深圳科技园园区内行人熙攘。",
            "站内行人通道",
            "这位同行嘉宾是牛津毕业的律师。",
            "其他同行成员已经在希思罗机场候机。",
            "几个同行朋友一起飞伦敦看展。",
            "外壳采用五轴铣削减薄工艺。",
            "镜框通过磨削减重十克。",
            "CNC精车削减薄到零点八毫米。",
            "铝合金镜腿采用CNC铣削减薄工艺。",
            "钛合金中框通过CNC车削减重。",
            "光学模组经过精密磨削减薄处理。",
            "大商行销",
            "海外大商行径",
            "他捂着眼点了一下头",
            "她擦着眼点点头",
            # Iteration 5 pure-whitelist & regex-unit traps (Reviewer 2 & Challenger 2)
            # 1. 回调 character-class & HR recall fraction & tech-bridge traps
            "把驻美销售总监回调了三个月。",
            "总部一次性回调了三个人支援深圳。",
            "把海外派驻的工程师回调了五个。",
            "把伦敦团队回调了两个总监。",
            "把海外工程师回调三个月。",
            "客户端回调了五个事件。",
            "后台回调超过两个小时还没结束。",
            "定时任务回调了三点钟的队列。",
            "总部把派驻伦敦的销售回调了一半。",
            "公司把欧洲区外派人员回调了近半。",
            "深圳把驻美工程师回调了大半。",
            "把外派团队回调了三成支援总部。",
            "把驻海外研发人员回调了三分之一。",
            "外派员工被回调了一半回深圳。",
            "行情接口正在回调数据。",
            # 2. ([上下])调 character-class & unitless 了<num> & locative/transfer traps
            "从手下调了三个人飞深圳。",
            "从旗下调了两个资深总监。",
            "从楼上调十个人下来。",
            "向上调了三名工程师。",
            "从账上调了五百万美元救急。",
            "从账上调一百万美元过去。",
            "从库房下调了两箱样机。",
            # 3. 供给 pangu-spaced bilingual, relative-clause 的 & recipient-department traps
            "AWS把大部分算力供给 Anthropic。",
            "我们优先把新增产能供给 Selfridges 和 Best Buy。",
            "英伟达把高端芯片供给 OpenAI 和 Meta。",
            "供应商拒绝把核心硬件供给 NovaEdge。",
            "我们只把最新产品供给 VIP 客户。",
            "把首批芯片供给 AI 团队。",
            "这批芯片供给的客户主要是北美大厂。",
            "深圳工厂核心产能供给的正是Best Buy和Selfridges。",
            "英伟达把高端芯片供给的大多是微软和Meta。",
            "银行把低息信贷供给的都是头部国企。",
            "这批优质原料供给的对象是苹果链。",
            "把核心硬件供给安全团队做渗透测试。",
            "把这批样机硬件供给质量部门做抽检。",
            "把这批样机供给质量部做抽检。",
            "把算力供给效率工程团队做压测。",
            "把优质产能供给链主企业。",
            "把新增产能供给端到端测试团队。",
            "把零配件供给体系外代工厂。",
            "把产品供给体系内的经销商。",
            "把份额供给有限合伙人。",
            # 4. 价差 & 信息差 pure-whitelist chà predicate traps
            "深圳和伦敦的零售价差不到十美元。",
            "这两款眼镜的零售价差不到十美金。",
            "这两家渠道给的批发价差不了一百块。",
            "亚马逊和百思买的零售价差几百美元。",
            "这两款眼镜的零售价差几美金。",
            "欧洲和北美的渠道价差两百欧元。",
            "这批货的批发价差一半，怎么卖？",
            "新品零售价差得不是一点半点。",
            "两家渠道的批发价差得太多了。",
            "百思买的批发价差得很，我们根本没毛利。",
            "这个季度的渠道价差极了。",
            "这批货的渠道价差极了。",
            "这两款眼镜的零售价差着两个档次。",
            "这两条线的批发价差得有点大。",
            "这个区域价差到没法做代理。",
            "首代和二代的零售价差那么大，老用户肯定骂。",
            "欧洲和北美的零售价差二十个点。",
            "我们的批发价差百分之十五。",
            "这两份尽调报告的信息差得不是一点半点。",
            "双方同步的信息差得很，完全对不上账。",
            "两边的财务信息差不到两个百分点。",
            "他们给的合规信息差着十万八千里。",
            "两边披露的信息差太离谱了。",
            "两边报上来的信息差太多了。",
            "两边给的信息差得太多了。",
            "两边的信息差不到哪儿去。",
            "这两份财报的信息差这么远，谁在造假？",
            "两边同步的信息差那么大，你让我怎么签字？",
            "这家机构提供的信息差得一塌糊涂。",
            "给投资人的披露信息差得没法看。",
            "两份口径的信息差一大截。",
            "深圳和硅谷同步的信息差两周。",
            "两边掌握的信息差不了一个数量级。",
            "这份研报的信息差透了。",
            # 5. ([内外])行人 smart-glasses CV & flagship-retail pedestrian traps
            "镜片视野内行人检测延迟低于二十毫秒。",
            "十米范围内行人识别准确率达到九成九。",
            "伦敦旗舰店外行人驻足率提升了三倍。",
            "落地玻璃外行人步履匆匆。",
            "百米以内行人轨迹追踪非常稳定。",
            "五米之外行人面部自动打码保护隐私。",
            "门店外行人流量决定了线下获客成本。",
            "斑马线外行人预警是下一代眼镜的核心卖点。",
            "护栏外行人闯入触发了实时语音提醒。",
            "幕墙外行人抬头看着我们的巨幅广告。",
            "玻璃幕墙外行人匆匆。",
            "门店外行人排起长队。",
            "隧道内行人禁止通行。",
            "境外行人安全标准很高。",
            # 6. 重定价 zhòng-modifier & 着重定价(权) traps
            "他着重定价权，不看短期出货量。",
            "华尔街着重定价权和现金流质量。",
            "发布会上着重定价权和护城河。",
            "谈判中着重定价权，别纠结账期。",
            "VC着重定价权，根本不在乎毛利以外的故事。",
            "这轮谈判着重定价，不谈账期。",
            "巴菲特向来重定价权。",
            "华尔街只重定价权，不看短期销量。",
            "他们不重定价权，只抢出货量。",
            "一线基金一贯重定价权和毛利率。",
            "欧洲渠道商素来重定价权。",
            "这副样机这么重定价还卖五百美元？",
            "债务负担依然重定价权却在流失。",
            # 7. 同行 accompanying staff/execs & generic verb predicates
            "这位同行翻译是伦敦本地人。",
            "几个同行助理留在酒店整理材料。",
            "这位同行律师负责审查对赌条款。",
            "这位同行顾问明天一起去见Best Buy。",
            "几个同行保镖守在会议室门外。",
            "一起同行的高管刚下飞机。",
            "全程同行的团队都是深圳核心工程师。",
            "和老板同行不敢松懈半步。",
            "和客户同行都在聊二代样机。",
            "跟他们同行早就抵达伦敦了。",
            "这次和我们同行的团队有十二个人。",
            # 8. Minor observations (着眼点开/破, 财务会计量, 翻出差账, 笨重构)
            "他撑着眼点开深夜发来的财报邮件。",
            "他沉着眼点破了对方的报价陷阱。",
            "他遮着眼点了支烟。",
            "他瞄着眼点开后台实时销量数据。",
            "财务会计量这批库存的减值损失。",
            "到审计现场翻出差账。",
            "这批样机还是太笨重构型太老气了。",
            # Iteration 6 pure-whitelist Challenger-2 traps (all 61 blocking traps + 3 出差 hygiene + defensive cases)
            # 1. 供给 (20 Challenger-2 traps + 3 defensive traps)
            "英伟达把高端芯片供给面向欧美的硬件厂商。",
            "台积电把新增产能供给面向北美市场的出海独角兽。",
            "我们只把核心产品供给面向高端消费群体的旗舰渠道。",
            "AWS把稀缺算力供给面向企业级客户的AI创业公司。",
            "这批高端芯片主要供给面向欧洲市场的智能眼镜厂商。",
            "把核心算力供给有限的几家头部客户。",
            "把高端芯片供给有限的几个战略伙伴。",
            "英伟达只能把核心算力供给有限的几家超大云厂商。",
            "把优先产能供给稳定合作十年的老渠道。",
            "把核心算力供给能力最强的研发团队。",
            "把高端芯片供给价格敏感度最低的大客户。",
            "把这批货供给成本控制最好的代工厂。",
            "把优质原料供给质量要求最高的欧美客户。",
            "把优先产能供给效率最高的深圳产线。",
            "把这批芯片供给安全等级最高的金融机构。",
            "把算力供给结构最稳健的头部客户。",
            "在把芯片供给的同时要求对方签排他协议。",
            "把算力供给安全研究院。",
            "把芯片供给质量监督局。",
            "把产能供给链家旗下平台。",
            "把算力供给量化基金。",
            "把算力供给量子实验室。",
            "把新增产能供给能解决良率问题的代工厂。",
            # 2. ([上下])调 (17 Challenger-2 traps + 3 defensive traps)
            "从公司名下调了两百万美元救急。",
            "从总部名下调了五百万美元支援伦敦。",
            "从创始人名下调了一千万美元进项目。",
            "从控股公司名下调至离岸信托。",
            "把资金从海外分公司名下调至总部。",
            "把资金从香港名下调到2号账户。",
            "从子公司名下调了20%的资金回来。",
            "把货从老渠道名下调了30%给百思买。",
            "从老项目名下调了三成预算给新品。",
            "从银行卡上调了一百万美元过去。",
            "从离岸户头上调了五百万美元。",
            "从母公司账面上调了五百万美元救急。",
            "从账面上调了两百万美元补窟窿。",
            "在极端情况下调了五百万美元救急。",
            "在这种情况下调了50%的库存去伦敦。",
            "在这个前提下调了三成产能给欧洲。",
            "在高压下调了50%的工程师回深圳。",
            "从老项目名下调预算给新品。",
            "从市场预算上调了两百万美元救急。",
            "从研发预算上调了两百万美元给市场。",
            "在年度目标下调了一百万美元支援伦敦。",
            # 3. 同行 (14 Challenger-2 traps + 1 defensive trap)
            "一起同行的产品经理刚落地伦敦。",
            "全程同行的渠道总监负责对接百思买。",
            "和我们同行的供应链专家已经到深圳了。",
            "跟林沉同行的供应链总监正在谈代工价。",
            "跟老板同行的数据分析师正在整理报表。",
            "跟林沉同行的产品总监也坐在头等舱。",
            "陪维多利亚同行的估值团队刚进会议室。",
            "昨天同行的成本总监已经飞回深圳了。",
            "今天同行的定价专家是伦敦本地人。",
            "其他同行的人都留在酒店整理PPT。",
            "其他同行员工已经先去机场了。",
            "其他同行工程师都在实验室调试。",
            "其他同行合伙人明天才到伦敦。",
            "找同行的人一起拼车去机场。",
            "其他同行的产品经理刚落地伦敦。",
            # 4. 回调 (10 Challenger-2 traps + 2 defensive traps)
            "总部把派驻伦敦的销售回调了50%。",
            "公司把欧洲区外派人员回调了30%。",
            "为了降本，深圳把驻美工程师回调了20%。",
            "客户端回调了100%的待处理事件。",
            "行情接口已经回调了100%的订单。",
            "市场部正在回调驻伦敦销售总监。",
            "市场团队已经回调了外派工程师。",
            "市场运营部突然回调了所有海外实习生。",
            "资产管理部正在回调驻新加坡的法务。",
            "价格引擎正在回调客户报价接口。",
            "美股行情接口已经回调了100%的订单。",
            "市场价格引擎已经回调了报价接口。",
            # 5. 出差 Regex 40 hygiene (3 Challenger-2 minor observations)
            "来深圳看出差在哪里。",
            "来会议室说出差在哪儿。",
            "去深圳拉出差单据。",
        )
        for phrase in protected_phrases:
            self.assertEqual(
                apply_domain_polyphone_overrides(phrase, domain="business_english_drama"),
                phrase,
                msg=f"False-positive corruption on protected phrase: {phrase!r}",
            )

        # Zero Xianxia leakage under business_english_drama
        xianxia_terms = ("劈开", "降临", "祠堂", "引气三重", "九月廿三")
        for term in xianxia_terms:
            self.assertEqual(
                apply_domain_polyphone_overrides(term, domain="business_english_drama"),
                term,
                msg=f"Xianxia leakage on {term!r}",
            )

        # Idempotency & exact expected output check on mixed realistic corporate text + pairwise tokens
        sample = (
            "维多利亚·万斯在投行和行业重估里反复强调：这副重资产超薄眼镜的供应链重构，"
            "绝不是撤回调研后靠摊薄股权或削减供给能解决的，必须着重构建底盘并重新审视估值回调。"
        )
        expected_once = (
            "维多利亚万斯在投航和航业崇估里反复强调：这副重资产超薄眼镜的供应链崇构，"
            "绝不是撤回调研后靠摊博股权或靴减工己能解决的，必须卓重构建底盘并崇新审视估值回条。"
        )
        once = apply_business_english_drama_polyphone_overrides(sample)
        twice = apply_business_english_drama_polyphone_overrides(once)
        self.assertEqual(once, expected_once)
        self.assertEqual(once, twice)

        for pairwise_case in ("屏息屏息", "股价突然回调股价突然回调", "飞伦敦出差出差", "飞伦敦出差出差报销"):
            p1 = apply_business_english_drama_polyphone_overrides(pairwise_case)
            p2 = apply_business_english_drama_polyphone_overrides(p1)
            self.assertEqual(p1, p2, msg=f"Pairwise non-idempotent on {pairwise_case!r}: p1={p1!r}, p2={p2!r}")
        self.assertEqual(apply_business_english_drama_polyphone_overrides("屏息屏息"), "屏息屏息")


class Drama3BusinessDramaTests(unittest.TestCase):
    def test_hbo_corporate_tags_en_and_zh_across_attempts(self) -> None:
        en_prof = VoiceProfile(
            role_id="victoria_vance",
            display_name="Victoria Vance",
            tier="antagonist",
            language_code="en",
            accent_code="us_silicon_valley",
        )
        zh_prof = VoiceProfile(
            role_id="lin_chen",
            display_name="林沉",
            tier="protagonist",
            language_code="zh-en",
            accent_code="zh_en_bilingual_us",
        )
        all_13_tags = (
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

        for tag in all_13_tags:
            en_cue = TimelineCue(
                cue_id=f"c_en_{tag.replace(' ', '_')}",
                act_id="act1",
                kind="dialogue",
                role_id="victoria_vance",
                language_code="en",
                text=f"[{tag}] That is a phantom number.",
            )
            a1_en = translate_cue_to_drama3_input(en_cue, en_prof, attempt=1, domain="business_english_drama")
            a2_en = translate_cue_to_drama3_input(en_cue, en_prof, attempt=2, domain="business_english_drama")
            a3_en = translate_cue_to_drama3_input(en_cue, en_prof, attempt=3, domain="business_english_drama")

            self.assertTrue(a1_en.startswith("["), msg=f"Missing Drama 3 brief on EN [{tag}]: {a1_en!r}")
            self.assertIn("That is a phantom number.", a1_en)
            self.assertNotIn("Xianxia", a1_en)
            self.assertNotIn("<forceful>", a1_en)
            if tag in ("aside", "understated"):
                self.assertIn("<soft>", a1_en)
                self.assertIn("</soft>", a1_en)
            else:
                self.assertNotIn("<soft>", a1_en)
            # Attempt 2 strips XML spans while preserving brief; Attempt 3 is pure spoken text
            self.assertNotIn("<soft>", a2_en)
            self.assertTrue(a2_en.startswith("["))
            self.assertEqual(a3_en, "That is a phantom number.")

            zh_cue = TimelineCue(
                cue_id=f"c_zh_{tag.replace(' ', '_')}",
                act_id="act1",
                kind="dialogue",
                role_id="lin_chen",
                language_code="zh-en",
                text=f"[{tag}] 这就是她说的 phantom number。",
            )
            a1_zh = translate_cue_to_drama3_input(zh_cue, zh_prof, attempt=1, domain="business_english_drama")
            a2_zh = translate_cue_to_drama3_input(zh_cue, zh_prof, attempt=2, domain="business_english_drama")
            a3_zh = translate_cue_to_drama3_input(zh_cue, zh_prof, attempt=3, domain="business_english_drama")

            self.assertTrue(a1_zh.startswith("["), msg=f"Missing ZH micro-brief on [{tag}]: {a1_zh!r}")
            if tag in ("aside", "understated"):
                self.assertIn("<soft>", a1_zh)
            self.assertEqual(a2_zh, "这就是她说的 phantom number。")
            self.assertEqual(a3_zh, "这就是她说的 phantom number。")

    def test_business_english_drama_zero_xianxia_or_ancient_monotone_fallback(self) -> None:
        narr_en = VoiceProfile(role_id="narrator", display_name="Narrator", tier="narrator", language_code="en")
        narr_zh = VoiceProfile(role_id="narrator", display_name="旁白", tier="narrator", language_code="zh")
        protag = VoiceProfile(role_id="lin_chen", display_name="林沉", tier="protagonist", language_code="zh-en")

        cues_and_profs = (
            (
                TimelineCue(
                    cue_id="c_narr_en",
                    act_id="act1",
                    kind="dialogue",
                    role_id="narrator",
                    language_code="en",
                    text="Sand Hill Road, 7:15 AM.",
                    stability=1.0,
                ),
                narr_en,
            ),
            (
                TimelineCue(
                    cue_id="c_narr_zh",
                    act_id="act1",
                    kind="dialogue",
                    role_id="narrator",
                    language_code="zh",
                    text="伦敦金融城，上午九点。",
                    stability=1.0,
                ),
                narr_zh,
            ),
            (
                TimelineCue(
                    cue_id="c_protag_s1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="lin_chen",
                    language_code="zh-en",
                    text="别急，先听完她的报价。",
                    stability=1.0,
                    acoustic_space="memory_echo",
                ),
                protag,
            ),
            (
                TimelineCue(
                    cue_id="c_protag_en",
                    act_id="act1",
                    kind="dialogue",
                    role_id="lin_chen",
                    language_code="en",
                    text="We stay capital-efficient.",
                    stability=1.0,
                ),
                protag,
            ),
        )

        for cue, prof in cues_and_profs:
            out = translate_cue_to_drama3_input(cue, prof, attempt=1, domain="business_english_drama")
            self.assertNotIn("Xianxia", out)
            self.assertNotIn("ancient monotone", out)
            self.assertNotIn("solemn memory", out)
            self.assertNotIn("<slow>", out)

        # Untagged protagonist stays completely clean (zero artificial prefix)
        self.assertEqual(
            translate_cue_to_drama3_input(cues_and_profs[2][0], protag, attempt=1, domain="business_english_drama"),
            "别急，先听完她的报价。",
        )
        # Untagged narrator gets restrained corporate drama brief
        self.assertIn(
            "restrained, understated modern corporate drama narration",
            translate_cue_to_drama3_input(cues_and_profs[0][0], narr_en, attempt=1, domain="business_english_drama"),
        )
        self.assertIn(
            "克制冷静、低沉写实的现代商战叙事",
            translate_cue_to_drama3_input(cues_and_profs[1][0], narr_zh, attempt=1, domain="business_english_drama"),
        )

    def test_combined_unit_bilingual_chunking_and_attribute_preservation(self) -> None:
        # 5 CJK chars + 55 EN words => effective_units = 5 + 2.2 * 55 = 126 > 105
        mixed_text = (
            "[coach] 注意听原句。 "
            "That is a phantom number and it is not a cash loss even though it flowed through into the income statement. "
            "We built a capital-efficient hardware stack that delivers ten times the throughput at half the compute cost. "
            "In other words, eating into budgets forces a really hard trade-off for every flagship retail buyer."
        )
        cue = TimelineCue(
            cue_id="c_mix_long",
            act_id="act5",
            kind="dialogue",
            role_id="lin_chen",
            speaker_name="林沉",
            language_code="zh-en",
            text=mixed_text,
            stability=0.5,
            similarity_boost=0.88,
            acoustic_space="studio_warm",
            playback_rate=0.80,
            subtitle_translation="拆局慢速原句解析。",
            gap_after_s=1.80,
            director_note="Debrief slow drill",
        )
        subcues = split_cue_into_subcues_for_drama3(
            cue,
            max_cjk_chars=105,
            max_en_words=65,
            domain="business_english_drama",
        )
        self.assertGreaterEqual(len(subcues), 2)
        for idx, sc in enumerate(subcues):
            self.assertAlmostEqual(sc.playback_rate, 0.80)
            self.assertAlmostEqual(sc.similarity_boost, 0.88)
            self.assertEqual(sc.acoustic_space, "studio_warm")
            self.assertTrue(sc.text.startswith("[coach]"))
            self.assertEqual(sc.tts_text, "")
            # No smashed ASCII sentences without space (e.g. "statement.We")
            self.assertIsNone(re.search(r"[.!?][A-Za-z]", sc.text), msg=f"Missing space in {sc.text!r}")
            if idx == 0:
                self.assertEqual(sc.subtitle_translation, "拆局慢速原句解析。")
                self.assertEqual(sc.director_note, "Debrief slow drill")
            else:
                self.assertEqual(sc.subtitle_translation, "")
                self.assertEqual(sc.director_note, "")
            if idx == len(subcues) - 1:
                self.assertAlmostEqual(sc.gap_after_s, 1.80)
            else:
                self.assertAlmostEqual(sc.gap_after_s, 0.16)

        # Edge case: unpunctuated English-heavy mixed cue still splits gracefully on whitespace
        unpunct_words = " ".join(f"word{i}" for i in range(60))
        unpunct_cue = TimelineCue(
            cue_id="c_mix_unpunct",
            act_id="act5",
            kind="dialogue",
            role_id="lin_chen",
            language_code="zh-en",
            text=f"[coach] 记住 {unpunct_words}",
            playback_rate=0.80,
        )
        unpunct_subs = split_cue_into_subcues_for_drama3(
            unpunct_cue,
            max_cjk_chars=105,
            max_en_words=40,
            domain="business_english_drama",
        )
        self.assertGreaterEqual(len(unpunct_subs), 2)
        for sc in unpunct_subs:
            self.assertAlmostEqual(sc.playback_rate, 0.80)
            self.assertLessEqual(len(re.findall(r"[A-Za-z]+", sc.text)), 42)

        # Pure-EN long cue also preserves playback_rate & subtitle_translation (subcue 1 only)
        en_long = TimelineCue(
            cue_id="c_en_long",
            act_id="act5",
            kind="dialogue",
            role_id="alistair_finch",
            language_code="en",
            text=(
                "[measured] First, this margin concession is a phantom number that flowed through into the income statement. "
                "Second, we need ten times the throughput before we run this thing a million times in retail stores. "
                "Third, eating into budgets creates a really hard trade-off when are you going to get the upside."
            ),
            playback_rate=0.80,
            similarity_boost=0.90,
            subtitle_translation="全英文长句慢速跟读。",
            gap_after_s=2.0,
        )
        en_subs = split_cue_into_subcues_for_drama3(en_long, max_en_words=28, domain="business_english_drama")
        self.assertGreaterEqual(len(en_subs), 2)
        self.assertTrue(all(abs(sc.playback_rate - 0.80) < 1e-6 for sc in en_subs))
        self.assertTrue(all(abs(sc.similarity_boost - 0.90) < 1e-6 for sc in en_subs))
        self.assertTrue(all(sc.tts_text == "" for sc in en_subs))
        self.assertEqual(en_subs[0].subtitle_translation, "全英文长句慢速跟读。")
        self.assertEqual(en_subs[1].subtitle_translation, "")

        # Typographic closing quotes insert space before ASCII without adding spurious spaces before CJK
        self.assertEqual(
            _join_bilingual_units("He said \u201cphantom number.\u201d", "Next sentence."),
            "He said \u201cphantom number.\u201d Next sentence.",
        )
        self.assertEqual(
            _join_bilingual_units("He said \u2018upside.\u2019", "Next."),
            "He said \u2018upside.\u2019 Next.",
        )
        self.assertEqual(
            _join_bilingual_units("他说“这是底牌。”", "下一句。"),
            "他说“这是底牌。”下一句。",
        )

    def test_export_colab_bundle_forwards_accent_code(self) -> None:
        reg = _build_sample_biz_registry()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            reg_path = tmp / "voice_casting_registry.json"
            reg.save(reg_path)
            scripts_dir = tmp / "scripts"
            scripts_dir.mkdir()
            sheet = EpisodeCueSheet(
                episode_id="E001_VA",
                chapter_number=1,
                title="Test",
                mode="bilingual_business_drama",
                acts=[ActMusicSpec(act_id="act1", title="Act 1", bgm_prompt="minimal cello")],
                cues=[
                    TimelineCue(
                        cue_id="c1",
                        act_id="act1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        language_code="en",
                        text="[icy polite] That is a phantom number.",
                    )
                ],
            )
            sheet.save(scripts_dir / "E001_VA_test.json")
            anchor_wav = _write_voiced_wav(tmp / "alistair_anchor.wav", duration_s=1.8)
            bundle_dir = tmp / "bundle"
            export_colab_96gb_bundle(
                registry_path=reg_path,
                cue_sheets_dir=scripts_dir,
                anchor_specs={
                    "alistair_finch": {
                        "audio_path": str(anchor_wav),
                        "anchor_text": "That is a phantom number.",
                    }
                },
                output_bundle_dir=bundle_dir,
            )
            voice_cast = json.loads((bundle_dir / "voice_cast_drama3.json").read_text(encoding="utf-8"))
            self.assertEqual(voice_cast["domain"], "business_english_drama")
            self.assertEqual(voice_cast["characters"]["alistair_finch"]["accent_code"], "uk_london_rp")


class BilingualQATests(unittest.TestCase):
    def test_zh_en_dual_script_recall_and_tail_preservation(self) -> None:
        # 1. Mixed zh-en intact passes
        ok = evaluate_dialogue_qa(
            tagged_prompt="[aside] 翻译成人话就是 take it or leave it.",
            asr_text="翻译成人话就是 take it or leave it.",
            duration_s=2.8,
            peak_dbfs=-10.0,
        )
        self.assertTrue(ok.passed)
        self.assertEqual(ok.char_recall, 1.0)
        self.assertTrue(ok.tail_preserved)

        # 2. Mixed zh-en with truncated trailing English fails BOTH embedded EN recall AND EN tail check
        trunc_tail = evaluate_dialogue_qa(
            tagged_prompt="[aside] 翻译成人话就是 take it or leave it.",
            asr_text="翻译成人话就是",
            duration_s=1.4,
            peak_dbfs=-10.0,
        )
        self.assertFalse(trunc_tail.passed)
        self.assertFalse(trunc_tail.tail_preserved)
        self.assertTrue(any("embedded English word recall" in r for r in trunc_tail.reasons))
        self.assertTrue(any("English tail truncation" in r for r in trunc_tail.reasons))

        # 3. < 4 CJK chars + >= 3 EN words catches dropped English
        short_cjk_drop = evaluate_dialogue_qa(
            tagged_prompt="[blunt] 对，that's a phantom number, not a cash loss.",
            asr_text="对，that's a phantom",
            duration_s=1.6,
            peak_dbfs=-11.0,
        )
        self.assertFalse(short_cjk_drop.passed)
        self.assertLess(short_cjk_drop.char_recall, 0.72)
        self.assertFalse(short_cjk_drop.tail_preserved)

        # 4. Mixed zh-en ending in CJK catches mid-sentence embedded English drop
        mid_en_drop = evaluate_dialogue_qa(
            tagged_prompt="[coach] 翻译成人话就是 take it or leave it，你看着办。",
            asr_text="翻译成人话就是，你看着办。",
            duration_s=2.0,
            peak_dbfs=-11.0,
        )
        self.assertFalse(mid_en_drop.passed)
        self.assertEqual(mid_en_drop.char_recall, 0.0)
        self.assertTrue(any("embedded English word recall" in r for r in mid_en_drop.reasons))

        # 5. Pure Chinese with 3+ Arabic numbers does NOT false-fail embedded English check
        zh_dates = evaluate_dialogue_qa(
            tagged_prompt="[measured] 2008年10月15日破产",
            asr_text="二零零八年十月十五日破产",
            duration_s=2.4,
            peak_dbfs=-10.5,
        )
        self.assertTrue(zh_dates.passed, msg=f"Unexpected failure on Chinese Arabic dates: {zh_dates.reasons}")

    def test_corporate_tag_leak_detection_and_spoken_exemption(self) -> None:
        corporate_tokens = (
            "measured",
            "deadpan",
            "icy",
            "polite",
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
        for tok in corporate_tokens:
            self.assertIn(tok, COMMON_TAG_WORDS)
            # Detect leaked tag even when the tag is NOT in tagged_prompt (proving COMMON_TAG_WORDS works)
            leaked_res = evaluate_dialogue_qa(
                tagged_prompt="That is a phantom number, not a cash loss.",
                asr_text=f"{tok} That is a phantom number, not a cash loss.",
                duration_s=3.0,
                peak_dbfs=-10.0,
            )
            self.assertFalse(leaked_res.passed, msg=f"Failed to catch leaked token {tok!r}")
            self.assertIn(tok, leaked_res.leaked_tags)

        # Multi-word [icy polite] tag leak detection
        icy_polite_leak = evaluate_dialogue_qa(
            tagged_prompt="[icy polite] Pick your favorite number.",
            asr_text="icy polite Pick your favorite number.",
            duration_s=2.4,
            peak_dbfs=-10.0,
        )
        self.assertFalse(icy_polite_leak.passed)
        self.assertEqual(set(icy_polite_leak.leaked_tags), {"icy", "polite"})

        # Legitimate words present in expected_spoken must NOT false-flag
        legit = evaluate_dialogue_qa(
            tagged_prompt="[measured] I'm confident that polite feedback stays blunt and measured.",
            asr_text="I'm confident that polite feedback stays blunt and measured.",
            duration_s=3.5,
            peak_dbfs=-10.0,
        )
        self.assertTrue(legit.passed)
        self.assertEqual(legit.leaked_tags, [])

    def test_pure_english_percent_digits_curly_apostrophes_and_single_trailing_keyword(self) -> None:
        # 1. Pure-English cues containing % and 4+ digits route cleanly to pure-EN branch (with or without language_code="en")
        en_numeric_pass_cases = (
            (
                "[measured] Our gross margin jumped 50% this quarter.",
                "Our gross margin jumped 50 percent this quarter.",
            ),
            (
                "[measured] Our margin target is 42.5%.",
                "Our margin target is 42.5 percent.",
            ),
            (
                "[measured] We shipped 10,000 units at 35% margin.",
                "We shipped 10,000 units at 35 percent margin.",
            ),
            (
                "[measured] We cut retail margin by 20.5%.",
                "We cut retail margin by 20.5 percent.",
            ),
            (
                "[confident] We deliver 10 times the throughput at 30% lower compute cost.",
                "We deliver ten times the throughput at 30 percent lower compute cost.",
            ),
            (
                "[measured] By 2026, our 10x throughput cuts 50% of compute cost.",
                "By twenty twenty-six, our ten x throughput cuts fifty percent of compute cost.",
            ),
            (
                "[measured] By 2026, we deliver 10 times the throughput.",
                "By twenty twenty-six, we deliver ten times the throughput.",
            ),
            (
                "[measured] In 2026, we need to run this thing 1,000,000 times.",
                "In 2026, we need to run this thing a million times.",
            ),
        )
        for prompt, asr in en_numeric_pass_cases:
            for lang in ("en", "zh"):
                res = evaluate_dialogue_qa(
                    tagged_prompt=prompt,
                    asr_text=asr,
                    duration_s=3.0,
                    peak_dbfs=-10.0,
                    language_code=lang,
                )
                self.assertTrue(res.passed, msg=f"False fail ({lang}) on {prompt!r} vs {asr!r}: {res.reasons}")

        # 2. Inverse false-pass trap: dropping "margin" after "20.5%" MUST fail English word recall
        drop_margin = evaluate_dialogue_qa(
            tagged_prompt="[blunt] 20.5% margin.",
            asr_text="20.5%",
            duration_s=1.2,
            peak_dbfs=-10.0,
            language_code="en",
        )
        self.assertFalse(drop_margin.passed)
        self.assertTrue(any("Low English word recall" in r for r in drop_margin.reasons))
        keep_margin = evaluate_dialogue_qa(
            tagged_prompt="[blunt] 20.5% margin.",
            asr_text="20.5 percent margin.",
            duration_s=1.4,
            peak_dbfs=-10.0,
            language_code="en",
        )
        self.assertTrue(keep_margin.passed)

        # 3. Single trailing English keyword (len >= 3) truncation caught; single-letter marker (图A) exempt
        upside_drop = evaluate_dialogue_qa(
            tagged_prompt="[aside] 她嘴上谈风险，心里全盯着那块 upside。",
            asr_text="她嘴上谈风险，心里全盯着那块",
            duration_s=2.2,
            peak_dbfs=-10.0,
            language_code="zh-en",
        )
        self.assertFalse(upside_drop.passed)
        self.assertFalse(upside_drop.tail_preserved)
        self.assertTrue(any("Potential English tail truncation" in r for r in upside_drop.reasons))

        upside_ok = evaluate_dialogue_qa(
            tagged_prompt="[aside] 她嘴上谈风险，心里全盯着那块 upside。",
            asr_text="她嘴上谈风险，心里全盯着那块 upside。",
            duration_s=2.4,
            peak_dbfs=-10.0,
            language_code="zh-en",
        )
        self.assertTrue(upside_ok.passed)

        fig_a = evaluate_dialogue_qa(
            tagged_prompt="[measured] 请看图A。",
            asr_text="请看图",
            duration_s=1.2,
            peak_dbfs=-10.0,
            language_code="zh-en",
        )
        self.assertTrue(fig_a.passed)

        # 4. Typographic curly apostrophes (\u2018 / \u2019) match ASCII apostrophes cleanly in both zh-en and en
        curly_mix = evaluate_dialogue_qa(
            tagged_prompt="[aside] 说白了，that\u2019s a phantom number, it\u2019s not cash.",
            asr_text="说白了，that's a phantom number, it's not cash.",
            duration_s=2.6,
            peak_dbfs=-10.0,
            language_code="zh-en",
        )
        self.assertTrue(curly_mix.passed, msg=f"Curly apostrophe zh-en failed: {curly_mix.reasons}")
        self.assertEqual(curly_mix.char_recall, 1.0)

        curly_en = evaluate_dialogue_qa(
            tagged_prompt="[blunt] That\u2019s not a cash loss; it\u2019s a phantom number, don\u2019t blink.",
            asr_text="That's not a cash loss; it's a phantom number, don't blink.",
            duration_s=3.0,
            peak_dbfs=-10.0,
            language_code="en",
        )
        self.assertTrue(curly_en.passed, msg=f"Curly apostrophe en failed: {curly_en.reasons}")
        self.assertEqual(curly_en.char_recall, 1.0)

        # 5. Mixed zh-en cue with % vs Whisper "percent" passes when tail intact and still catches dropped tail
        mix_pct_ok = evaluate_dialogue_qa(
            tagged_prompt="[aside] 这就是 20% upside。",
            asr_text="这就是 20 percent upside。",
            duration_s=1.8,
            peak_dbfs=-10.0,
            language_code="zh-en",
        )
        self.assertTrue(mix_pct_ok.passed, msg=f"Mixed zh-en % vs percent failed: {mix_pct_ok.reasons}")
        mix_pct_drop = evaluate_dialogue_qa(
            tagged_prompt="[aside] 这就是 20% upside。",
            asr_text="这就是 20 percent",
            duration_s=1.5,
            peak_dbfs=-10.0,
            language_code="zh-en",
        )
        self.assertFalse(mix_pct_drop.passed)

        # 6. synthesize_with_playbook_qa forwards language_code="en" into evaluate_dialogue_qa
        class _LocalWavClient:
            def __init__(self, asr_reply: str) -> None:
                self.asr_reply = asr_reply

            def synthesize_dialogue(
                self,
                *,
                voice_id: str,
                text: str,
                output_wav: Path,
                stability: float,
                similarity_boost: float,
                language_code: str,
                use_cache: bool,
            ) -> SynthesisResult:
                _write_voiced_wav(output_wav, duration_s=1.4, amplitude=0.35)
                return SynthesisResult(
                    wav_path=output_wav,
                    duration_s=1.4,
                    output_format_used="pcm_48000",
                    character_cost=0,
                    request_id="local_test",
                    from_cache=False,
                )

            def transcribe_asr(self, wav_path: Path, *, language_code: str) -> dict[str, str]:
                return {"text": self.asr_reply}

        with tempfile.TemporaryDirectory() as td:
            # Pure-numeric "100%" vs "one hundred percent" passes ONLY because language_code="en" is forwarded
            _, qa_pct, _ = synthesize_with_playbook_qa(
                _LocalWavClient("one hundred percent"),  # type: ignore[arg-type]
                voice_id="v_en",
                tagged_text="[blunt] 100%",
                output_wav=Path(td) / "pct.wav",
                stability=0.5,
                language_code="en",
            )
            self.assertTrue(qa_pct.passed, msg=f"language_code='en' not forwarded: {qa_pct.reasons}")

            _, qa_drop, _ = synthesize_with_playbook_qa(
                _LocalWavClient("20.5%"),  # type: ignore[arg-type]
                voice_id="v_en",
                tagged_text="[blunt] 20.5% margin.",
                output_wav=Path(td) / "drop.wav",
                stability=0.5,
                language_code="en",
            )
            self.assertFalse(qa_drop.passed)
            self.assertTrue(any("Low English word recall" in r for r in qa_drop.reasons))


class AdapterMarkdownExportTests(unittest.TestCase):
    def test_bilingual_business_drama_markdown_export_and_regressions(self) -> None:
        reg = _build_sample_biz_registry()
        biz_sheet = EpisodeCueSheet(
            episode_id="E001_VA",
            chapter_number=1,
            title="跨境底牌",
            mode="bilingual_business_drama",
            source_chapter_file="season1_24ep_map.json#E001",
            acts=[
                ActMusicSpec(
                    act_id="act1",
                    title="London Boardroom",
                    bgm_prompt="minimalist dark cello pulse, instrumental",
                )
            ],
            cues=[
                TimelineCue(
                    cue_id="c1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[icy polite] That is a phantom number.",
                    acoustic_space="boardroom",
                    playback_rate=0.80,
                    subtitle_translation="那只是个账面虚数。",
                ),
                TimelineCue(
                    cue_id="c2",
                    act_id="act1",
                    kind="dialogue",
                    role_id="lin_chen",
                    language_code="zh",
                    text="[aside] 表面客气，底牌全是刀。",
                    acoustic_space="inner_monologue",
                    playback_rate=1.0,
                    subtitle_translation="   ",
                ),
                TimelineCue(
                    cue_id="c3",
                    act_id="act1",
                    kind="dialogue",
                    role_id="victoria_vance",
                    language_code="zh-en",
                    text="[blunt] 直接看 unit economics。",
                    acoustic_space="phone_call",
                    playback_rate=1.25,
                ),
            ],
        )
        md = export_cue_sheet_markdown(biz_sheet, registry=reg)
        self.assertIn("中英双语商战广播剧演出台本", md)
        self.assertIn("ACE-Step 1.5 XL · 纯器乐冷峻商战原声", md)
        self.assertNotIn("ElevenLabs", md)
        self.assertNotIn("music_v2_5", md)
        self.assertIn("语言 `en`", md)
        self.assertIn("语言 `zh`", md)
        self.assertIn("语言 `zh-en`", md)
        self.assertIn("口音 `uk_london_rp`", md)
        self.assertIn("声场 `boardroom`", md)
        self.assertIn("声场 `inner_monologue`", md)
        self.assertIn("声场 `phone_call`", md)
        self.assertIn("[0.80x]", md)
        self.assertIn("[1.25x]", md)
        self.assertNotIn("[1.00x]", md)
        self.assertIn("*中文字幕译文：那只是个账面虚数。*", md)
        self.assertEqual(md.count("中文字幕译文："), 1)

        # Cross-mode audition_pack still displays [0.80x] and subtitle_translation
        aud_sheet = EpisodeCueSheet(
            episode_id="AUDITION_GLOBAL_EDGE",
            chapter_number=0,
            title="试音包",
            mode="audition_pack",
            cues=[
                TimelineCue(
                    cue_id="a1",
                    act_id="aud",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[coach] Pick your favorite number.",
                    playback_rate=0.80,
                    subtitle_translation="挑一个你最喜欢的数字。",
                )
            ],
        )
        aud_md = export_cue_sheet_markdown(aud_sheet, registry=reg)
        self.assertIn("[0.80x]", aud_md)
        self.assertIn("*中文字幕译文：挑一个你最喜欢的数字。*", aud_md)

        # Legacy modes remain intact
        pod_sheet = EpisodeCueSheet(
            episode_id="EP01",
            chapter_number=1,
            title="巴菲特致股东信",
            mode="podcast_roundtable",
            acts=[ActMusicSpec(act_id="act1", title="开场", bgm_prompt="warm acoustic guitar")],
            cues=[
                TimelineCue(
                    cue_id="p1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="lin_chen",
                    text="这是一期圆桌播客。",
                )
            ],
        )
        pod_md = export_cue_sheet_markdown(pod_sheet)
        self.assertIn("ACE-Step 1.5 XL · 纯器乐纪录片书房声场", pod_md)

        legacy_sheet = EpisodeCueSheet(
            episode_id="E001",
            chapter_number=1,
            title="青阳旧事",
            mode="immersive_audiobook_drama",
            cues=[
                TimelineCue(
                    cue_id="l1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="fu_bo",
                    speaker_name="福伯",
                    text="少主小心。",
                )
            ],
        )
        legacy_md = export_cue_sheet_markdown(legacy_sheet)
        self.assertIn("广播剧 / 多人精品有声剧演出台本", legacy_md)
        self.assertIn("（`stability=0.5` | 句后气口 `0.35s`）", legacy_md)
        self.assertNotIn("| 语速", legacy_md)
        self.assertNotIn("| 语言", legacy_md)
        self.assertNotIn("| 口音", legacy_md)
        self.assertNotIn("中文字幕译文", legacy_md)

    def test_adapter_markdown_multiline_non_string_and_non_finite_hardening(self) -> None:
        reg = _build_sample_biz_registry()
        sheet = EpisodeCueSheet(
            episode_id="E001_HARDEN",
            chapter_number=1,
            title="Markdown Hardening",
            mode="bilingual_business_drama",
            acts=[ActMusicSpec(act_id="act1", title="Boardroom", bgm_prompt="minimalist pulse")],
            cues=[
                TimelineCue(
                    cue_id="h1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[measured] Line one.",
                    playback_rate=float("inf"),
                    subtitle_translation="第一行\n\n  第二行\t第三行",
                ),
                TimelineCue(
                    cue_id="h2",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[measured] Line two.",
                    playback_rate=float("-inf"),
                    subtitle_translation=123,  # type: ignore[arg-type]
                ),
                TimelineCue(
                    cue_id="h3",
                    act_id="act1",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[measured] Line three.",
                    playback_rate=float("nan"),
                    subtitle_translation=["zh"],  # type: ignore[arg-type]
                ),
            ],
        )
        md = export_cue_sheet_markdown(sheet, registry=reg)
        self.assertIn("*中文字幕译文：第一行 第二行 第三行*", md)
        self.assertEqual(md.count("中文字幕译文："), 1)
        self.assertNotIn("[infx]", md)
        self.assertNotIn("[-infx]", md)
        self.assertNotIn("[nanx]", md)
        self.assertNotIn("| 语速", md)


if __name__ == "__main__":
    unittest.main()
