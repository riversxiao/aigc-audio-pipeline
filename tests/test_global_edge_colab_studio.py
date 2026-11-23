"""Comprehensive self-contained tests for M4 Global Edge Colab 96GB Real-Human Anchor & Multi-Variant Studio Suite.

Zero third-party dependencies, zero mocks/skips, zero network/API calls, zero tracked-tree side effects.
All audio conditioning, bundle assembly, and 3-bus mastering runs execute real `ffmpeg`/`ffprobe`
inside `tempfile.TemporaryDirectory()`.
"""

from __future__ import annotations

from array import array
import ast
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import wave
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
COLAB_DIR = REPO_ROOT / "colab_96gb"
PROJECT_DIR = REPO_ROOT / "projects" / "global_edge"
META_DIR = PROJECT_DIR / "00_节目圣经与第一季24集总纲"
SCRIPTS_DIR = PROJECT_DIR / "scripts"

for _p in (SRC_DIR, COLAB_DIR, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from aigc_audio_pipeline.batch_queue import measure_ebur128  # noqa: E402
from aigc_audio_pipeline.models import (  # noqa: E402
    ActMusicSpec,
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
)

import export_drama3_bundle as exporter_mod  # noqa: E402
import launch_g4_global_edge_drama3 as launcher_mod  # noqa: E402
import prepare_global_edge_voice_anchors as prep_mod  # noqa: E402
import run_global_edge_96gb_studio as studio_mod  # noqa: E402

REGISTRY_PATH = META_DIR / "voice_casting_registry.json"
ANCHOR_SOURCES_PATH = META_DIR / "anchor_sources.json"
ACQUISITION_SPEC_PATH = META_DIR / "VOICE_ANCHOR_ACQUISITION_SPEC.md"
NOTEBOOK_PATH = COLAB_DIR / "Global_Edge_96GB_Drama3_Studio.ipynb"

EXPECTED_ROLES: tuple[str, ...] = (
    "lin_chen",
    "zhou_mo",
    "victoria_vance",
    "alistair_finch",
    "claire_chen_gc",
    "rajiv_menon",
    "wei_ling_tan",
    "henrik_lindqvist",
)


def _ffprobe_audio_stream(wav_path: Path) -> dict[str, str]:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=sample_rate,channels,codec_name:format=duration",
            "-of",
            "json",
            str(wav_path),
        ],
        text=True,
    )
    parsed = json.loads(out)
    stream = parsed["streams"][0]
    fmt = parsed["format"]
    return {
        "sample_rate": str(stream["sample_rate"]),
        "channels": str(stream["channels"]),
        "codec_name": str(stream["codec_name"]),
        "duration": str(fmt["duration"]),
    }


def _write_stereo_48k_wav(
    dst_wav: Path,
    *,
    duration_s: float = 11.0,
    uncorrelated: bool = False,
) -> Path:
    """Synthesize a 48000 Hz 2-channel PCM16 stereo WAV (dual-mono L==R or uncorrelated L!=R)."""
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    sr = 48000
    tile_frames = sr
    two_pi = 2.0 * math.pi
    tile = array("h", [0]) * (tile_frames * 2)
    for i in range(tile_frames):
        t = i / sr
        env_l = 0.55 + 0.35 * math.sin(two_pi * 3.0 * t)
        sig_l = (
            0.40 * math.sin(two_pi * 130.0 * t)
            + 0.35 * math.sin(two_pi * 260.0 * t)
            + 0.25 * math.sin(two_pi * 390.0 * t)
        )
        samp_l = int(max(-32767, min(32767, round(32767.0 * 0.26 * env_l * sig_l))))
        if uncorrelated:
            env_r = 0.55 + 0.35 * math.cos(two_pi * 4.0 * t)
            sig_r = (
                0.40 * math.sin(two_pi * 197.0 * t + 1.1)
                + 0.35 * math.sin(two_pi * 394.0 * t + 0.7)
                + 0.25 * math.sin(two_pi * 591.0 * t + 2.3)
            )
            samp_r = int(max(-32767, min(32767, round(32767.0 * 0.26 * env_r * sig_r))))
        else:
            samp_r = samp_l
        tile[2 * i] = samp_l
        tile[2 * i + 1] = samp_r

    total_frames = max(sr, int(round(duration_s * sr)))
    full_repeats, remainder = divmod(total_frames, tile_frames)
    buf = array("h")
    for _ in range(full_repeats):
        buf.extend(tile)
    if remainder > 0:
        buf.extend(tile[: remainder * 2])

    with wave.open(str(dst_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(buf.tobytes())
    return dst_wav


def _parse_srt_timestamps(srt_text: str) -> list[tuple[float, float, list[str]]]:
    blocks = [b.strip() for b in re.split(r"\r?\n\r?\n+", srt_text.strip()) if b.strip()]
    parsed: list[tuple[float, float, list[str]]] = []
    ts_re = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})")

    def _to_s(h: str, m: str, s: str, ms: str) -> float:
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    for block in blocks:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
        if len(lines) < 3:
            continue
        m = ts_re.search(lines[1])
        if not m:
            continue
        start_s = _to_s(m.group(1), m.group(2), m.group(3), m.group(4))
        end_s = _to_s(m.group(5), m.group(6), m.group(7), m.group(8))
        parsed.append((start_s, end_s, lines[2:]))
    return parsed


def _build_synthetic_cue_sheets(cue_dir: Path, registry: VoiceCastingRegistry) -> dict[str, Path]:
    """Create validated synthetic AUDITION + E001_VA/VB/VC/VD cue sheets strictly in temp dir."""
    cue_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    audition = EpisodeCueSheet(
        episode_id="AUDITION_GLOBAL_EDGE",
        chapter_number=0,
        title="全口音与双语飙戏试听包",
        mode="audition_pack",
        acts=[],
        cues=[
            TimelineCue(
                cue_id="aud_01",
                act_id="audition",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="zh-en",
                text="[measured] That loss is a phantom number, not a cash loss. [aside] 她不是看不懂财报。",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=0.4,
            ),
            TimelineCue(
                cue_id="aud_02",
                act_id="audition",
                kind="dialogue",
                role_id="victoria_vance",
                speaker_name="Victoria Vance",
                language_code="en",
                text="[icy polite] Walk me through the eighty million on the income statement.",
                subtitle_translation="给我解释清楚损益表上那八千万。",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=0.4,
            ),
            TimelineCue(
                cue_id="aud_03",
                act_id="audition",
                kind="dialogue",
                role_id="alistair_finch",
                speaker_name="Alistair Finch",
                language_code="en",
                text="[understated] Tell me what is good enough without eating into my margin.",
                subtitle_translation="告诉我什么叫够用，同时别吞掉我的毛利。",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=0.4,
            ),
        ],
    )
    assert audition.validate(registry=registry, require_locked_voices=True) == []
    aud_path = cue_dir / "AUDITION_GLOBAL_EDGE_全口音与双语飙戏试听包.json"
    audition.save(aud_path)
    written["AUDITION_GLOBAL_EDGE"] = aud_path

    # Shared HBO OST prompts (including one with negative traditional mention to exercise sanitizer)
    act1 = ActMusicSpec(
        act_id="act_1",
        title="Sand Hill Boardroom Duel",
        bgm_prompt=(
            "Minimalist HBO prestige corporate drama underscore, muted solo cello ostinato over dark felt piano, "
            "no traditional Chinese instruments, no guzheng, strictly instrumental, no vocals"
        ),
        bgm_duration_s=45.0,
        bgm_gain_speech=0.07,
        bgm_gain_gap=0.25,
    )
    act5 = ActMusicSpec(
        act_id="act_5",
        title="Black-Book Debrief",
        bgm_prompt=(
            "Ultra-clean minimalist modern executive podcast bed, sparse muted acoustic bass and warm felt piano, "
            "strictly instrumental, no drums, no vocals, no singing"
        ),
        bgm_duration_s=45.0,
        bgm_gain_speech=0.06,
        bgm_gain_gap=0.22,
    )

    shared_drill_line = "[coach] That eighty-million-dollar loss is a phantom number, not a cash loss."

    # E001_VA: boardroom crosstalk (-0.12s), inner_monologue, phone_call, plus paired 0.80x / 1.0x drill cues
    va_sheet = EpisodeCueSheet(
        episode_id="E001_VA",
        chapter_number=1,
        title="HBO纯飙戏冷峻商战版",
        mode="bilingual_business_drama",
        acts=[act1, act5],
        cues=[
            TimelineCue(
                cue_id="va_sfx_door",
                act_id="act_1",
                kind="sfx",
                motif_id="glass_boardroom_door",
                duration_seconds=1.6,
                placement="sequential",
                gap_after_s=0.2,
            ),
            TimelineCue(
                cue_id="va_dlg_01",
                act_id="act_1",
                kind="dialogue",
                role_id="victoria_vance",
                speaker_name="Victoria Vance",
                language_code="en",
                text="[icy polite] Eighty million flowed through into the income statement, Lin.",
                subtitle_translation="八千万直接计入了损益表，林沉。",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=-0.12,
            ),
            TimelineCue(
                cue_id="va_dlg_02",
                act_id="act_1",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="en",
                text="[measured] It is a phantom number—not a cash loss, and we remain capital-efficient.",
                subtitle_translation="那是账面虚数——不是现金亏损，我们的资本效率依然很稳。",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=0.25,
            ),
            TimelineCue(
                cue_id="va_dlg_03",
                act_id="act_1",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="zh",
                text="[aside] 她把可转债公允价值变动包装成失血，就是想在签字前压估值。",
                stability=0.5,
                acoustic_space="inner_monologue",
                gap_after_s=0.25,
            ),
            TimelineCue(
                cue_id="va_dlg_04",
                act_id="act_1",
                kind="dialogue",
                role_id="zhou_mo",
                speaker_name="周默 / Zhou Mo",
                language_code="zh-en",
                text="[blunt] 深圳产线已经把 BOM cost 压下来了，别被她的估值话术带偏。",
                stability=0.5,
                acoustic_space="phone_call",
                gap_after_s=0.35,
            ),
            TimelineCue(
                cue_id="va_debrief_slow",
                act_id="act_5",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="en",
                text=shared_drill_line,
                subtitle_translation="慢速拆解：那八千万亏损只是账面虚数，不是现金流出。",
                stability=0.5,
                acoustic_space="studio_warm",
                playback_rate=0.8,
                gap_after_s=0.5,
            ),
            TimelineCue(
                cue_id="va_debrief_fast",
                act_id="act_5",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="en",
                text=shared_drill_line,
                subtitle_translation="原速跟读：那八千万亏损只是账面虚数，不是现金流出。",
                stability=0.5,
                acoustic_space="studio_warm",
                playback_rate=1.0,
                gap_after_s=1.8,
            ),
        ],
    )
    assert va_sheet.validate(registry=registry, require_locked_voices=True) == []
    va_path = cue_dir / "E001_VA_HBO纯飙戏冷峻商战版_完整双语台本.json"
    va_sheet.save(va_path)
    written["E001_VA"] = va_path

    # E001_VB: freeze_frame_sub_drop + inner_monologue
    vb_sheet = EpisodeCueSheet(
        episode_id="E001_VB",
        chapter_number=1,
        title="纸牌屋冻帧潜台词狙击版",
        mode="bilingual_business_drama",
        acts=[act1, act5],
        cues=[
            TimelineCue(
                cue_id="vb_sfx_freeze",
                act_id="act_1",
                kind="sfx",
                motif_id="freeze_frame_sub_drop",
                duration_seconds=1.2,
                placement="sequential",
                gap_after_s=0.15,
            ),
            TimelineCue(
                cue_id="vb_dlg_01",
                act_id="act_1",
                kind="dialogue",
                role_id="alistair_finch",
                speaker_name="Alistair Finch",
                language_code="en",
                text="[understated] What is good enough if we run this thing a million times?",
                subtitle_translation="如果跑一百万次，什么标准才算够用？",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=0.2,
            ),
            TimelineCue(
                cue_id="vb_dlg_02",
                act_id="act_5",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="zh",
                text="[aside] 听懂这句，你就看穿了伦敦大买手压毛利的底牌。",
                stability=0.5,
                acoustic_space="inner_monologue",
                gap_after_s=0.5,
            ),
        ],
    )
    assert vb_sheet.validate(registry=registry, require_locked_voices=True) == []
    vb_path = cue_dir / "E001_VB_纸牌屋冻帧潜台词狙击版_完整双语台本.json"
    vb_sheet.save(vb_path)
    written["E001_VB"] = vb_path

    # E001_VC: phone_call + boardroom thriller
    vc_sheet = EpisodeCueSheet(
        episode_id="E001_VC",
        chapter_number=1,
        title="三时区惊悚推进与实战跟读版",
        mode="bilingual_business_drama",
        acts=[act1, act5],
        cues=[
            TimelineCue(
                cue_id="vc_sfx_call",
                act_id="act_1",
                kind="sfx",
                motif_id="transpacific_call_connect",
                duration_seconds=1.5,
                placement="sequential",
                gap_after_s=0.15,
            ),
            TimelineCue(
                cue_id="vc_dlg_01",
                act_id="act_1",
                kind="dialogue",
                role_id="claire_chen_gc",
                speaker_name="Claire Sterling",
                language_code="en",
                text="[blunt] Pick your favorite number, but protect our upside on page fourteen.",
                subtitle_translation="随便选哪个口径，但十四页的上行收益必须守住。",
                stability=0.5,
                acoustic_space="phone_call",
                gap_after_s=0.3,
            ),
            TimelineCue(
                cue_id="vc_dlg_02",
                act_id="act_5",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="en",
                text="[coach] In other words, we get ten times the throughput at half the cost.",
                subtitle_translation="换句话说，我们用一半成本拿到十倍吞吐量。",
                stability=0.5,
                acoustic_space="studio_warm",
                playback_rate=0.8,
                gap_after_s=1.8,
            ),
        ],
    )
    assert vc_sheet.validate(registry=registry, require_locked_voices=True) == []
    vc_path = cue_dir / "E001_VC_三时区惊悚推进与实战跟读版_完整双语台本.json"
    vc_sheet.save(vc_path)
    written["E001_VC"] = vc_path

    # E001_VD: documentary simultaneous-translation duck_under_next=True
    vd_sheet = EpisodeCueSheet(
        episode_id="E001_VD",
        chapter_number=1,
        title="纪实同传叠音混合版",
        mode="bilingual_business_drama",
        acts=[act1, act5],
        cues=[
            TimelineCue(
                cue_id="vd_dlg_01_en",
                act_id="act_1",
                kind="dialogue",
                role_id="victoria_vance",
                speaker_name="Victoria Vance",
                language_code="en",
                text=(
                    "[icy polite] Cloud inference is eating into budgets across every hardware startup "
                    "we backed this year, and that forces a really hard trade-off on gross margin."
                ),
                stability=0.5,
                acoustic_space="boardroom",
                duck_under_next=True,
                duck_lead_in_s=2.0,
                duck_gain=0.15,
                gap_after_s=0.25,
            ),
            TimelineCue(
                cue_id="vd_dlg_02_zh",
                act_id="act_1",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="zh",
                text="[aside] 她的潜台词很直白：云端算力正在吞噬预算，逼你在毛利和体验之间做残酷取舍。",
                stability=0.5,
                acoustic_space="inner_monologue",
                gap_after_s=0.35,
            ),
            TimelineCue(
                cue_id="vd_dlg_03_debrief",
                act_id="act_5",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="林沉 / Lin Chen",
                language_code="en",
                text="[coach] When are you going to get it—the real upside is on-device inference.",
                subtitle_translation="你什么时候才能拿回上行收益——真正的增量在端侧推理。",
                stability=0.5,
                acoustic_space="studio_warm",
                playback_rate=0.8,
                gap_after_s=1.8,
            ),
        ],
    )
    assert vd_sheet.validate(registry=registry, require_locked_voices=True) == []
    vd_path = cue_dir / "E001_VD_纪实同传叠音混合版_完整双语台本.json"
    vd_sheet.save(vd_path)
    written["E001_VD"] = vd_path

    return written


class TestGlobalEdgeColabStudio(unittest.TestCase):
    """M4 self-contained real-execution verification suite."""

    def test_01_anchor_sources_manifest_alignment(self) -> None:
        self.assertTrue(ANCHOR_SOURCES_PATH.is_file(), f"Missing {ANCHOR_SOURCES_PATH}")
        data = json.loads(ANCHOR_SOURCES_PATH.read_text(encoding="utf-8"))
        registry = VoiceCastingRegistry.load(REGISTRY_PATH)

        self.assertEqual(data["project_id"], "global_edge")
        self.assertEqual(data["domain"], "business_english_drama")
        self.assertEqual(data["anchor_schema_version"], "v2_real_human_studio")
        self.assertEqual(data["target_sample_rate_hz"], 44100)
        self.assertEqual(data["target_channels"], 1)
        self.assertAlmostEqual(float(data["target_lufs"]), -16.0, places=2)
        self.assertIs(data["synthetic_tts_forbidden"], True)

        budget = data["accent_budget"]
        self.assertGreaterEqual(float(budget["core_us_uk_en_pct_min"]), 85.0)
        self.assertAlmostEqual(float(budget["season1_actual_core_pct"]), 96.0, places=2)
        self.assertLessEqual(float(budget["intl_guest_en_pct_max"]), 15.0)
        self.assertAlmostEqual(float(budget["season1_actual_intl_pct"]), 4.0, places=2)

        roles = data["roles"]
        self.assertEqual(set(roles.keys()), set(EXPECTED_ROLES))
        self.assertEqual(set(roles.keys()), set(registry.roles.keys()))

        for role_id in EXPECTED_ROLES:
            entry = roles[role_id]
            prof = registry.roles[role_id]
            self.assertEqual(entry["role_id"], role_id)
            self.assertEqual(entry["display_name"], prof.display_name)
            self.assertEqual(entry["language_code"], prof.language_code)
            self.assertEqual(entry["accent_code"], prof.accent_code)
            self.assertIn(entry["source_type"], ("real_human_studio_corpus", "repo_bundled_real_human"))
            self.assertTrue(str(entry["license"]).strip())
            self.assertTrue(str(entry["source_name"]).strip())
            self.assertIsNone(launcher_mod.FORBIDDEN_SYNTHETIC_SOURCE_RE.search(entry["source_name"]))
            self.assertIsInstance(entry["source_urls"], list)
            self.assertGreaterEqual(len(entry["source_urls"]), 1)
            self.assertEqual(entry["repo_relative_source"], f"voice_anchors/{role_id}.wav")
            self.assertEqual(entry["custom_anchor_filename"], f"{role_id}.wav")
            self.assertTrue(str(entry["fallback_strategy"]).strip())
            self.assertTrue(str(entry["anchor_text"]).strip())
            self.assertNotIn("[", entry["anchor_text"], f"[{role_id}] anchor_text must be plain spoken text")

            dur = float(entry["target_duration_s"])
            self.assertGreaterEqual(dur, 10.0)
            self.assertLessEqual(dur, 18.0)

            cond = entry["conditioning_spec"]
            self.assertEqual(cond["sample_rate_hz"], 44100)
            self.assertEqual(cond["channels"], 1)
            self.assertEqual(cond["codec"], "pcm_s16le")
            self.assertEqual(cond["highpass_hz"], 75)
            filt = cond["ffmpeg_filter"]
            self.assertIn("aformat=sample_rates=44100:channel_layouts=mono", filt)
            self.assertIn("highpass=f=75", filt)
            self.assertIn("loudnorm=I=-16:TP=-1.5:LRA=11", filt)
            self.assertLess(
                filt.index("aformat=sample_rates=44100:channel_layouts=mono"),
                filt.index("loudnorm=I=-16:TP=-1.5:LRA=11"),
            )
            self.assertIs(cond["no_afftdn"], True)

        # Direct audio URLs across all 8 roles must be strictly unique & paired with verbatim direct_audio_transcript
        audio_exts = (".wav", ".mp3", ".m4a", ".flac", ".ogg")
        seen_direct_urls: dict[str, str] = {}
        for role_id in EXPECTED_ROLES:
            entry = roles[role_id]
            role_direct_urls = [
                str(u).strip()
                for u in entry["source_urls"]
                if str(u).strip().split("?", 1)[0].lower().endswith(audio_exts)
            ]
            if role_id == "lin_chen":
                self.assertEqual(
                    role_direct_urls,
                    [],
                    "lin_chen must NOT inherit a Mandarin-only direct audio URL (must use same-speaker EN+ZH anchor)",
                )
            for u in role_direct_urls:
                self.assertNotIn(
                    u,
                    seen_direct_urls,
                    f"Duplicate direct audio URL {u!r} shared by {seen_direct_urls.get(u)!r} and {role_id!r}",
                )
                seen_direct_urls[u] = role_id
                direct_txt = str(entry.get("direct_audio_transcript") or "").strip()
                self.assertTrue(
                    direct_txt,
                    f"[{role_id}] Direct audio URL {u!r} must declare verbatim direct_audio_transcript",
                )
                self.assertNotIn("[", direct_txt)
                self.assertNotEqual(
                    direct_txt,
                    str(entry["anchor_text"]).strip(),
                    f"[{role_id}] direct_audio_transcript must match real audio, not fictional audition script",
                )

        proto = roles["lin_chen"]["bilingual_same_speaker_protocol"]
        self.assertIs(proto["single_human_speaker_required"], True)
        self.assertTrue(str(proto["age_vocal_profile"]).strip())
        self.assertTrue(str(proto["spliced_bilingual_anchor_ratio_en_zh"]).strip())
        self.assertTrue(str(proto["paired_en_zh_audition_ab_test"]).strip())
        self.assertIsInstance(proto["anti_accent_bleed_rules"], list)
        self.assertGreaterEqual(len(proto["anti_accent_bleed_rules"]), 3)
        self.assertEqual(proto["target_en_wpm"], "155-180")
        self.assertEqual(proto["target_zh_cps"], "3.55-3.65")

    def test_02_voice_anchor_acquisition_spec_doc(self) -> None:
        self.assertTrue(ACQUISITION_SPEC_PATH.is_file())
        text = ACQUISITION_SPEC_PATH.read_text(encoding="utf-8")
        for role_id in EXPECTED_ROLES:
            self.assertIn(role_id, text)
        for required_token in (
            "v2_real_human_studio",
            "validate_production_voice_cast",
            "96.0%",
            "4.0%",
            "bilingual_same_speaker_protocol",
            "custom_anchors/",
            "highpass=f=75",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "afftdn",
            "faster-whisper-small-int8",
            "AUDITION_GLOBAL_EDGE",
            "G1",
            "G2",
            "G3",
            "G4",
            "G5",
            "G6",
            "G7",
            "G8",
        ):
            self.assertIn(required_token, text, f"Missing required section/token {required_token!r}")

    def test_03_prepare_voice_anchors_offline_stub_and_custom_dropin(self) -> None:
        registry = VoiceCastingRegistry.load(REGISTRY_PATH)
        with tempfile.TemporaryDirectory(prefix="ge_prep_test_") as td:
            out_dir = Path(td) / "anchors_out"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(SRC_DIR)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(COLAB_DIR / "prepare_global_edge_voice_anchors.py"),
                    "--registry",
                    str(REGISTRY_PATH),
                    "--sources",
                    str(ANCHOR_SOURCES_PATH),
                    "--output-dir",
                    str(out_dir),
                    "--offline-stub",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            stdout_json = json.loads(proc.stdout)
            self.assertTrue(stdout_json["ok"])
            self.assertEqual(stdout_json["anchor_schema_version"], "v2_real_human_studio")
            self.assertEqual(stdout_json["role_count"], 8)

            cast_path = out_dir / "voice_cast_drama3.json"
            self.assertTrue(cast_path.is_file())
            cast = json.loads(cast_path.read_text(encoding="utf-8"))
            self.assertEqual(cast["project_id"], "global_edge")
            self.assertEqual(cast["domain"], "business_english_drama")
            self.assertEqual(cast["anchor_schema_version"], "v2_real_human_studio")
            self.assertEqual(cast["anchor_sample_rate_hz"], 44100)
            self.assertEqual(cast["role_count"], 8)

            for role_id in EXPECTED_ROLES:
                cinfo = cast["characters"][role_id]
                self.assertEqual(cinfo["accent_code"], registry.roles[role_id].accent_code)
                self.assertEqual(cinfo["source_voice_name"], "offline_synthetic_stub")
                wav_p = out_dir / cinfo["anchor_wav"]
                txt_p = out_dir / "voice_anchors" / f"{role_id}.txt"
                self.assertTrue(wav_p.is_file())
                self.assertTrue(txt_p.is_file())
                self.assertEqual(txt_p.read_text(encoding="utf-8").strip(), cinfo["anchor_text"].strip())
                self.assertGreater(wav_p.stat().st_size, 100000)

                with wave.open(str(wav_p), "rb") as wf:
                    self.assertEqual(wf.getframerate(), 44100)
                    self.assertEqual(wf.getnchannels(), 1)
                    self.assertEqual(wf.getsampwidth(), 2)
                    dur_wave = wf.getnframes() / float(wf.getframerate())
                self.assertGreaterEqual(dur_wave, 9.8)
                self.assertLessEqual(dur_wave, 18.0)

                probe = _ffprobe_audio_stream(wav_p)
                self.assertEqual(probe["sample_rate"], "44100")
                self.assertEqual(probe["channels"], "1")
                self.assertEqual(probe["codec_name"], "pcm_s16le")

            # Verify EBU R128 loudness on conditioned stub anchor
            lufs, tp = measure_ebur128(out_dir / "voice_anchors" / "lin_chen.wav")
            self.assertGreater(lufs, -20.5)
            self.assertLess(lufs, -12.5)
            self.assertLessEqual(tp, -0.5)

            # Verify custom_anchors drop-in tier with BOTH 48kHz dual-mono stereo (L==R) AND uncorrelated stereo (L!=R)
            custom_dir = Path(td) / "custom_anchors"
            custom_dir.mkdir(parents=True, exist_ok=True)
            _write_stereo_48k_wav(custom_dir / "lin_chen.wav", duration_s=11.0, uncorrelated=False)
            _write_stereo_48k_wav(custom_dir / "zhou_mo.wav", duration_s=11.0, uncorrelated=True)
            custom_txt_lc = "Custom studio close-mic recording for Lin Chen. 硅谷美音与冷峻中文同声源校准。"
            custom_txt_zm = "Custom studio close-mic recording for Zhou Mo. 深圳南山产线硬核校准。"
            (custom_dir / "lin_chen.txt").write_text(custom_txt_lc + "\n", encoding="utf-8")
            (custom_dir / "zhou_mo.txt").write_text(custom_txt_zm + "\n", encoding="utf-8")

            custom_out = Path(td) / "custom_out"
            res_custom = prep_mod.prepare_all_global_edge_anchors(
                registry_path=REGISTRY_PATH,
                anchor_sources_path=ANCHOR_SOURCES_PATH,
                output_dir=custom_out,
                custom_anchors_dir=custom_dir,
                roles="lin_chen,zhou_mo",
                offline_stub=False,
            )
            self.assertEqual(res_custom["role_count"], 2)
            for rid, expected_txt in (("lin_chen", custom_txt_lc), ("zhou_mo", custom_txt_zm)):
                entry = res_custom["characters"][rid]
                self.assertEqual(entry["source_voice_name"], f"custom_real_human_anchor:{rid}.wav")
                self.assertEqual(entry["anchor_text"], expected_txt)
                out_wav = custom_out / "voice_anchors" / f"{rid}.wav"
                self.assertTrue(out_wav.is_file())
                probe = _ffprobe_audio_stream(out_wav)
                self.assertEqual(probe["sample_rate"], "44100")
                self.assertEqual(probe["channels"], "1")
                self.assertEqual(probe["codec_name"], "pcm_s16le")
                lufs_stereo, tp_stereo = measure_ebur128(out_wav)
                self.assertGreaterEqual(
                    lufs_stereo,
                    -17.5,
                    f"[{rid}] Stereo-to-mono loudness dropped below -17.5 LUFS: {lufs_stereo:.2f}",
                )
                self.assertLessEqual(
                    lufs_stereo,
                    -14.5,
                    f"[{rid}] Stereo-to-mono loudness exceeded -14.5 LUFS: {lufs_stereo:.2f}",
                )
                self.assertLessEqual(tp_stereo, -0.5)

            # Verify Tier 3 transcript resolution strictly uses verbatim direct_audio_transcript (NEVER default_spoken)
            sources_manifest = json.loads(ANCHOR_SOURCES_PATH.read_text(encoding="utf-8"))
            zm_spec = sources_manifest["roles"]["zhou_mo"]
            resolved_zm_txt = prep_mod._resolve_tier3_transcript(
                zm_spec,
                custom_out / "voice_anchors" / "zhou_mo.wav",
                role_id="zhou_mo",
                language_code="zh-en",
                whisper_size="small",
            )
            self.assertEqual(resolved_zm_txt, zm_spec["direct_audio_transcript"])
            self.assertNotEqual(resolved_zm_txt, zm_spec["anchor_text"])

            # Verify Tier 3 fails loudly & removes broken WAV if direct_audio_transcript is absent & Whisper fails
            orphan_wav = Path(td) / "orphan_tier3.wav"
            orphan_wav.write_bytes((custom_out / "voice_anchors" / "lin_chen.wav").read_bytes())
            with self.assertRaises(RuntimeError):
                prep_mod._resolve_tier3_transcript(
                    {"anchor_text": "Fictional audition line must NEVER be stamped"},
                    orphan_wav,
                    role_id="victoria_vance",
                    language_code="en",
                    whisper_size="__nonexistent_whisper_model__",
                )
            self.assertFalse(orphan_wav.exists(), "Orphan Tier 3 WAV should be cleaned up when transcript fails")

            # Verify bilingual Whisper segment joining inserts spaces between adjacent ASCII words only
            self.assertEqual(
                prep_mod._join_whisper_segments(
                    ["That eighty-million", "dollar loss.", "Not a cash loss.", "她把可转债", "包装成失血"],
                    language_code="zh-en",
                ),
                "That eighty-million dollar loss. Not a cash loss.她把可转债包装成失血",
            )

            # Verify zero synthetic fallback & zero Mandarin clip download for lin_chen / victoria_vance in real mode
            for missing_role in ("lin_chen", "victoria_vance"):
                with self.assertRaises(RuntimeError):
                    prep_mod.prepare_all_global_edge_anchors(
                        registry_path=REGISTRY_PATH,
                        anchor_sources_path=ANCHOR_SOURCES_PATH,
                        output_dir=Path(td) / f"no_real_anchor_{missing_role}",
                        custom_anchors_dir=Path(td) / "empty_custom_dir",
                        roles=missing_role,
                        offline_stub=False,
                    )

    def test_04_variant_resolver_and_skip_existing_collision_safety(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ge_resolver_test_") as td:
            cue_dir = Path(td) / "cue_sheets"
            aud_dir = Path(td) / "auditions"
            mp3_dir = Path(td) / "outputs"
            cue_dir.mkdir()
            aud_dir.mkdir()
            mp3_dir.mkdir()

            (aud_dir / "AUDITION_GLOBAL_EDGE_试听包.json").write_text("{}", encoding="utf-8")
            for fname in (
                "E001_基础版.json",
                "E001_VA_HBO版.json",
                "E001_VB_纸牌屋版.json",
                "E001_VC_三时区版.json",
                "E001_VD_同传版.json",
                "E001A_旧版A.json",
                "E001B_旧版B.json",
                "E002_第二集.json",
            ):
                (cue_dir / fname).write_text("{}", encoding="utf-8")

            self.assertEqual(
                [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "AUDITION")],
                ["AUDITION_GLOBAL_EDGE"],
            )
            self.assertEqual(
                [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "AUDITION_GLOBAL_EDGE")],
                ["AUDITION_GLOBAL_EDGE"],
            )
            self.assertEqual(
                [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "E001")],
                ["E001"],
            )
            self.assertEqual(
                [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "1")],
                ["E001"],
            )
            self.assertEqual(
                [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "E001_VA,E001_VD,E001A")],
                ["E001_VA", "E001_VD", "E001A"],
            )
            # E001_VARIANTS expands to all E001 variant files (excluding bare E001)
            variants = [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "E001_VARIANTS")]
            self.assertEqual(variants, ["E001A", "E001B", "E001_VA", "E001_VB", "E001_VC", "E001_VD"])
            self.assertNotIn("E001", variants)

            # Deduplication preserving order
            dedup = [
                k
                for k, _ in studio_mod.resolve_global_edge_targets(
                    cue_dir, aud_dir, "E001_VC,E001_VARIANTS,E001_VA"
                )
            ]
            self.assertEqual(dedup[0], "E001_VC")
            self.assertEqual(len(dedup), len(set(dedup)))

            # Range E001-E002 & ALL (ALL includes AUDITION_GLOBAL_EDGE ahead of sorted E*.json when present)
            r12 = [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "E001-E002")]
            all_eps = [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, aud_dir, "ALL")]
            self.assertEqual(all_eps, ["AUDITION_GLOBAL_EDGE", *r12])
            self.assertEqual(len(all_eps), 9)

            # ALL with empty auditions directory resolves cleanly to sorted E*.json only
            empty_aud_dir = Path(td) / "empty_auditions"
            empty_aud_dir.mkdir()
            all_no_aud = [k for k, _ in studio_mod.resolve_global_edge_targets(cue_dir, empty_aud_dir, "ALL")]
            self.assertEqual(all_no_aud, r12)
            self.assertEqual(len(all_no_aud), 8)

            # Empty directory raises FileNotFoundError for E001_VARIANTS and ALL
            empty_dir = Path(td) / "empty"
            empty_dir.mkdir()
            with self.assertRaises(FileNotFoundError):
                studio_mod.resolve_global_edge_targets(empty_dir, empty_dir, "E001_VARIANTS")
            with self.assertRaises(FileNotFoundError):
                studio_mod.resolve_global_edge_targets(empty_dir, empty_dir, "ALL")

            # Collision-safe MP3 matching: E001 must NOT match E001_VA or E001A
            for nm in (
                "E001_VA_HBO版_v001.mp3",
                "E001_VB_纸牌屋版_v001.mp3",
                "E001A_旧版A_v001.mp3",
                "AUDITION_GLOBAL_EDGE_试听_v001.mp3",
            ):
                (mp3_dir / nm).write_bytes(b"mp3")
            self.assertEqual(studio_mod.find_existing_episode_mp3s("E001", [mp3_dir]), [])
            self.assertEqual(
                [p.name for p in studio_mod.find_existing_episode_mp3s("E001_VA", [mp3_dir])],
                ["E001_VA_HBO版_v001.mp3"],
            )
            self.assertEqual(
                [p.name for p in studio_mod.find_existing_episode_mp3s("E001A", [mp3_dir])],
                ["E001A_旧版A_v001.mp3"],
            )
            self.assertEqual(
                [p.name for p in studio_mod.find_existing_episode_mp3s("AUDITION_GLOBAL_EDGE", [mp3_dir])],
                ["AUDITION_GLOBAL_EDGE_试听_v001.mp3"],
            )

    def test_05_hbo_bgm_guardrails_foley_sanitizer_and_080x_cache_key(self) -> None:
        forbidden_tokens = (
            "xianxia",
            "guqin",
            "guzheng",
            "erhu",
            "flute",
            "dizi",
            "pipa",
            "traditional chinese",
            "traditional asian",
        )
        test_prompts = (
            "",
            "Dark tense boardroom underscore",
            "Traditional Chinese music, dark boardroom cello",
            "Traditional eastern folk melody, Chinese folk music, muted felt piano",
            (
                "Minimalist HBO prestige corporate drama underscore, muted solo cello over dark felt piano, "
                "no traditional Chinese instruments, no guzheng, no erhu, purely instrumental, no vocals"
            ),
            (
                "Epic xianxia guqin and guzheng with bamboo flute, dizi, pipa, erhu, traditional Asian instruments, "
                "soaring female singing vocals, pop drums, trap beats, and EDM drops"
            ),
        )
        for raw in test_prompts:
            enriched = studio_mod.enrich_business_drama_bgm_prompt(raw)
            low = enriched.lower()
            for tok in (*forbidden_tokens, "traditional eastern", "chinese folk"):
                self.assertNotIn(tok, low, f"Forbidden token {tok!r} leaked into BGM prompt: {enriched!r}")
            self.assertIn("instrumental", low)
            self.assertIn("no vocals", low)
            self.assertIn("no singing", low)
            self.assertIn("no choir", low)
            self.assertIn("no trap", low)
            self.assertIn("no edm", low)
            # Strict idempotency
            self.assertEqual(studio_mod.enrich_business_drama_bgm_prompt(enriched), enriched)

        # MOSS Foley sanitizer: preserve ALL 7 canonical sonic_motifs byte-identically & strip standalone/plural vocals
        registry = VoiceCastingRegistry.load(REGISTRY_PATH)
        self.assertEqual(len(registry.sonic_motifs), 7)
        for motif_id, motif in registry.sonic_motifs.items():
            self.assertEqual(
                studio_mod.sanitize_moss_foley_prompt(motif.sfx_prompt),
                motif.sfx_prompt,
                f"Canonical motif {motif_id!r} was unexpectedly altered by sanitize_moss_foley_prompt()",
            )

        for tainted_sfx, bad_words in (
            ("Glass boardroom door click with coughing and human voice", ("coughing",)),
            ("Heavy glass door shutting, muffled office chatter, distant talking", ("chatter", "talking")),
            ("Boardroom latch click with background voices and laughter", ("voices", "laughter")),
            ("Quiet elevator chime, soft laughing, distant vocals", ("laughing", "vocals")),
        ):
            san = studio_mod.sanitize_moss_foley_prompt(tainted_sfx)
            san_low = san.lower()
            for bw in bad_words:
                self.assertNotIn(bw, san_low, f"Vocal token {bw!r} leaked in {san!r}")
            self.assertIn("pure foley", san_low)
            self.assertIn("no human voice", san_low)
            self.assertEqual(studio_mod.sanitize_moss_foley_prompt(san), san)
        self.assertIn("no human voice", studio_mod.sanitize_moss_foley_prompt("").lower())

        # Deterministic 0.80x TTS cache key invariance
        k_fast = studio_mod.build_dialogue_tts_cache_key(
            engine="fishaudio/drama-3",
            domain="business_english_drama",
            role_id="lin_chen",
            anchor_sha256="abcdef0123456789",
            prompt_a1="That loss is a phantom number.",
            max_tokens=512,
        )
        k_slow = studio_mod.build_dialogue_tts_cache_key(
            engine="fishaudio/drama-3",
            domain="business_english_drama",
            role_id="lin_chen",
            anchor_sha256="abcdef0123456789",
            prompt_a1="That loss is a phantom number.",
            max_tokens=512,
        )
        self.assertEqual(k_fast, k_slow)
        self.assertEqual(len(k_fast), 24)
        k_diff_anchor = studio_mod.build_dialogue_tts_cache_key(
            engine="fishaudio/drama-3",
            domain="business_english_drama",
            role_id="lin_chen",
            anchor_sha256="9999999999999999",
            prompt_a1="That loss is a phantom number.",
            max_tokens=512,
        )
        self.assertNotEqual(k_fast, k_diff_anchor)

    def test_06_validate_production_voice_cast_gate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ge_cast_gate_") as td:
            studio = Path(td) / "studio"
            prep_mod.prepare_all_global_edge_anchors(
                registry_path=REGISTRY_PATH,
                anchor_sources_path=ANCHOR_SOURCES_PATH,
                output_dir=studio,
                offline_stub=True,
            )

            # 1. Must reject offline_synthetic_stub (unit + live studio CLI guard)
            ok, errs = launcher_mod.validate_production_voice_cast(studio)
            self.assertFalse(ok)
            self.assertTrue(any("offline_synthetic_stub" in e for e in errs))
            (studio / "voice_casting_registry.json").write_text(
                REGISTRY_PATH.read_text(encoding="utf-8"), encoding="utf-8"
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = str(SRC_DIR)
            guard_proc = subprocess.run(
                [
                    sys.executable,
                    str(COLAB_DIR / "run_global_edge_96gb_studio.py"),
                    "--studio-dir",
                    str(studio),
                    "--episodes",
                    "AUDITION",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(guard_proc.returncode, 0)
            self.assertIn("validate_production_voice_cast", guard_proc.stderr + guard_proc.stdout)

            # 1b. Offline dry-run mode (allow_offline_stub=True) permits valid v2 offline_synthetic_stub,
            #     but still strictly rejects Neural / legacy TTS sources and legacy schema versions
            ok_stub_dry, errs_stub_dry = launcher_mod.validate_production_voice_cast(
                studio, allow_offline_stub=True
            )
            self.assertTrue(ok_stub_dry, f"Expected offline_synthetic_stub to pass dry-run gate: {errs_stub_dry}")

            # Promote all 8 roles to genuine real-human studio corpus provenance
            vc_file = studio / "voice_cast_drama3.json"
            base_cast = json.loads(vc_file.read_text(encoding="utf-8"))
            for rid, cinfo in base_cast["characters"].items():
                cinfo["source_voice_name"] = f"real_human_studio_corpus:{rid}"
            vc_file.write_text(json.dumps(base_cast, ensure_ascii=False, indent=2), encoding="utf-8")

            # 2. Genuine v2_real_human_studio cast passes (both dir path & direct json path)
            ok_dir, errs_dir = launcher_mod.validate_production_voice_cast(studio)
            self.assertTrue(ok_dir, f"Expected valid real-human cast, got errors: {errs_dir}")
            ok_file, errs_file = launcher_mod.validate_production_voice_cast(vc_file)
            self.assertTrue(ok_file, f"Expected valid real-human cast file, got errors: {errs_file}")

            # 3. Reject forbidden synthetic/Neural/legacy-TTS source names
            legacy_dash = "-".join(["edge", "tts"])
            legacy_under = "_".join(["edge", "tts"])
            for bad_src in (
                "zh-CN-YunxiNeural",
                f"{legacy_dash}:en-US-Guy",
                f"{legacy_under}:zh-CN-Xiaoxiao",
                "zero_cost_studio_anchor:lin_chen",
                "synthetic_voice_v1",
            ):
                mut = json.loads(json.dumps(base_cast))
                mut["characters"]["lin_chen"]["source_voice_name"] = bad_src
                vc_file.write_text(json.dumps(mut, ensure_ascii=False, indent=2), encoding="utf-8")
                ok_bad, _ = launcher_mod.validate_production_voice_cast(studio)
                self.assertFalse(ok_bad, f"Should have rejected forbidden source_voice_name={bad_src!r}")
                ok_bad_dry, _ = launcher_mod.validate_production_voice_cast(
                    studio, allow_offline_stub=True
                )
                self.assertFalse(
                    ok_bad_dry,
                    f"Dry-run gate must still reject non-stub synthetic/forbidden source_voice_name={bad_src!r}",
                )

            # 4. Reject wrong schema version (in both production and dry-run modes)
            mut = json.loads(json.dumps(base_cast))
            mut["anchor_schema_version"] = "v1_legacy"
            vc_file.write_text(json.dumps(mut, ensure_ascii=False, indent=2), encoding="utf-8")
            self.assertFalse(launcher_mod.validate_production_voice_cast(studio)[0])
            self.assertFalse(launcher_mod.validate_production_voice_cast(studio, allow_offline_stub=True)[0])

            # 5. Reject missing role
            mut = json.loads(json.dumps(base_cast))
            del mut["characters"]["henrik_lindqvist"]
            vc_file.write_text(json.dumps(mut, ensure_ascii=False, indent=2), encoding="utf-8")
            self.assertFalse(launcher_mod.validate_production_voice_cast(studio)[0])

            # 6. Reject blank anchor_text
            mut = json.loads(json.dumps(base_cast))
            mut["characters"]["zhou_mo"]["anchor_text"] = "   "
            vc_file.write_text(json.dumps(mut, ensure_ascii=False, indent=2), encoding="utf-8")
            self.assertFalse(launcher_mod.validate_production_voice_cast(studio)[0])

            # 7. Reject tiny WAV (< 4096 bytes)
            vc_file.write_text(json.dumps(base_cast, ensure_ascii=False, indent=2), encoding="utf-8")
            (studio / "voice_anchors" / "rajiv_menon.wav").write_bytes(b"RIFFtiny")
            self.assertFalse(launcher_mod.validate_production_voice_cast(studio)[0])

            # 8. Reject corrupt >= 4096-byte non-WAV payload (`wave.open` header check)
            (studio / "voice_anchors" / "rajiv_menon.wav").write_bytes(b"NOT_A_WAV" * 600)
            ok_corrupt, errs_corrupt = launcher_mod.validate_production_voice_cast(studio)
            self.assertFalse(ok_corrupt)
            self.assertTrue(any("Corrupt or non-WAV" in e for e in errs_corrupt))

            # 9. Reject valid WAV with wrong sample rate / channel layout (48kHz stereo instead of 44.1kHz mono)
            _write_stereo_48k_wav(studio / "voice_anchors" / "rajiv_menon.wav", duration_s=1.0)
            ok_fmt, errs_fmt = launcher_mod.validate_production_voice_cast(studio)
            self.assertFalse(ok_fmt)
            self.assertTrue(any("44100 Hz mono 16-bit PCM" in e for e in errs_fmt))

            # 10. Live studio CLI runs production gate BEFORE json.loads(voice_cast_drama3.json)
            vc_file.unlink()
            missing_proc = subprocess.run(
                [
                    sys.executable,
                    str(COLAB_DIR / "run_global_edge_96gb_studio.py"),
                    "--studio-dir",
                    str(studio),
                    "--episodes",
                    "AUDITION",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(missing_proc.returncode, 0)
            self.assertIn("validate_production_voice_cast", missing_proc.stderr + missing_proc.stdout)

    def test_07_bundle_exporter_and_full_offline_dry_run_e2e(self) -> None:
        registry = VoiceCastingRegistry.load(REGISTRY_PATH)
        with tempfile.TemporaryDirectory(prefix="ge_e2e_dryrun_") as td:
            root = Path(td)
            cue_dir = root / "synthetic_cues"
            _build_synthetic_cue_sheets(cue_dir, registry)

            # Part A: Bundle exporter tolerates missing cue-sheets-dir (parallel M5 safety) & writes patched ZIP
            empty_bundle = root / "empty_bundle"
            empty_zip = root / "empty_bundle.zip"
            res_empty = exporter_mod.build_global_edge_bundle(
                project_dir=PROJECT_DIR,
                cue_sheets_dir=root / "nonexistent_cues_dir",
                output_bundle_dir=empty_bundle,
                zip_output_path=empty_zip,
                offline_stub_anchors=True,
            )
            self.assertEqual(res_empty["anchor_schema_version"], "v2_real_human_studio")
            self.assertEqual(res_empty["episode_count"], 0)
            self.assertTrue(empty_zip.is_file())
            with zipfile.ZipFile(empty_zip, "r") as zf:
                names = set(zf.namelist())
                self.assertIn("voice_cast_drama3.json", names)
                self.assertIn("anchor_sources.json", names)
                self.assertIn("voice_casting_registry.json", names)
                self.assertIn("voice_anchors/lin_chen.wav", names)
                self.assertIn("voice_anchors/lin_chen.txt", names)
                self.assertIn("run_global_edge_96gb_studio.py", names)
                vc_in_zip = json.loads(zf.read("voice_cast_drama3.json").decode("utf-8"))
                self.assertEqual(vc_in_zip["anchor_schema_version"], "v2_real_human_studio")
                self.assertEqual(vc_in_zip["domain"], "business_english_drama")
                self.assertEqual(vc_in_zip["role_count"], 8)

            # Part A2: Verify bare `--zip` CLI flag preserves dotted directory names (`cli_bundle.v1.0.zip`)
            cli_bundle_dir = root / "cli_bundle.v1.0"
            env_cli = os.environ.copy()
            env_cli["PYTHONPATH"] = str(SRC_DIR)
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "export_drama3_bundle.py"),
                    "--project-dir",
                    str(PROJECT_DIR),
                    "--cue-sheets-dir",
                    str(cue_dir),
                    "--anchors-dir",
                    str(empty_bundle),
                    "--output-dir",
                    str(cli_bundle_dir),
                    "--zip",
                ],
                env=env_cli,
                capture_output=True,
                text=True,
                check=True,
            )
            auto_zip = cli_bundle_dir.parent / f"{cli_bundle_dir.name}.zip"
            self.assertTrue(auto_zip.is_file(), f"Expected dotted auto-zip at {auto_zip}")
            with zipfile.ZipFile(auto_zip, "r") as zf:
                self.assertIn("anchor_sources.json", set(zf.namelist()))
                self.assertEqual(
                    json.loads(zf.read("voice_cast_drama3.json").decode("utf-8"))["anchor_schema_version"],
                    "v2_real_human_studio",
                )

            # Part B: Full end-to-end `launch_g4_global_edge_drama3.py --offline-dry-run`
            run_out = root / "launcher_out"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(SRC_DIR)
            subprocess.run(
                [
                    sys.executable,
                    str(COLAB_DIR / "launch_g4_global_edge_drama3.py"),
                    "--project-dir",
                    str(PROJECT_DIR),
                    "--cue-sheets-dir",
                    str(cue_dir),
                    "--output-dir",
                    str(run_out),
                    "--episodes",
                    "AUDITION,E001_VARIANTS",
                    "--offline-dry-run",
                ],
                env=env,
                check=True,
            )

            # Verify bundle layout created by launcher
            bundle_dir = run_out / "bundle"
            self.assertTrue((bundle_dir / "voice_cast_drama3.json").is_file())
            self.assertTrue((bundle_dir / "anchor_sources.json").is_file())
            self.assertTrue((bundle_dir / "src" / "aigc_audio_pipeline" / "mixer.py").is_file())
            self.assertTrue((bundle_dir / "run_global_edge_96gb_studio.py").is_file())
            self.assertEqual(len(list((bundle_dir / "cue_sheets").glob("E001_V*.json"))), 4)
            self.assertEqual(len(list((bundle_dir / "auditions").glob("AUDITION*.json"))), 1)

            # Verify all 5 masters (AUDITION + E001_VA..E001_VD)
            masters_dir = run_out / "masters"
            done_files = sorted(masters_dir.glob("*.done"))
            self.assertEqual(len(done_files), 5)
            rendered_ids: set[str] = set()
            manifests_by_id: dict[str, dict] = {}

            for df in done_files:
                summary = json.loads(df.read_text(encoding="utf-8"))
                eid = summary["episode_id"]
                rendered_ids.add(eid)
                wav_p = Path(summary["master_wav"])
                mp3_p = Path(summary["master_mp3"])
                srt_p = Path(summary["subtitles_srt"])
                json_p = Path(summary["manifest_json"])
                for artifact in (wav_p, mp3_p, srt_p, json_p):
                    self.assertTrue(artifact.is_file(), f"Missing artifact {artifact}")
                    self.assertGreater(artifact.stat().st_size, 100)

                probe = _ffprobe_audio_stream(wav_p)
                self.assertEqual(probe["sample_rate"], "48000")
                self.assertEqual(probe["channels"], "2")

                lufs, tp = measure_ebur128(wav_p)
                self.assertGreater(lufs, -30.0)
                self.assertLessEqual(tp, -0.5)

                manifests_by_id[eid] = json.loads(json_p.read_text(encoding="utf-8"))

            self.assertEqual(
                rendered_ids,
                {"AUDITION_GLOBAL_EDGE", "E001_VA", "E001_VB", "E001_VC", "E001_VD"},
            )

            # Verify E001_VA 0.80x real FFmpeg atempo stretching (~1.25x longer than identical 1.0x cue)
            va_items = {it["cue_id"]: it for it in manifests_by_id["E001_VA"]["timeline"]}
            slow_dur = float(va_items["va_debrief_slow"]["duration_s"])
            fast_dur = float(va_items["va_debrief_fast"]["duration_s"])
            ratio = slow_dur / fast_dur
            self.assertAlmostEqual(float(va_items["va_debrief_slow"]["playback_rate"]), 0.8, places=2)
            self.assertAlmostEqual(float(va_items["va_debrief_fast"]["playback_rate"]), 1.0, places=2)
            self.assertGreaterEqual(ratio, 1.15, f"Expected ~1.25x atempo stretch, got ratio={ratio:.3f}")
            self.assertLessEqual(ratio, 1.38, f"Expected ~1.25x atempo stretch, got ratio={ratio:.3f}")
            # Confirm stem reuse: both va_debrief_slow & va_debrief_fast shared the EXACT same cached raw stem
            self.assertEqual(
                va_items["va_debrief_slow"]["stem_file"],
                va_items["va_debrief_fast"]["stem_file"],
            )

            # Verify E001_VA dual-line bilingual SRT has translation gloss and zero timestamp overlaps
            va_srt = Path(manifests_by_id["E001_VA"]["subtitles_srt"]).read_text(encoding="utf-8")
            self.assertIn("八千万直接计入了损益表", va_srt)
            self.assertIn("慢速拆解：那八千万亏损只是账面虚数", va_srt)
            srt_entries = _parse_srt_timestamps(va_srt)
            self.assertGreaterEqual(len(srt_entries), 4)
            for idx in range(len(srt_entries) - 1):
                self.assertLessEqual(
                    srt_entries[idx][1],
                    srt_entries[idx + 1][0] + 0.005,
                    f"SRT timestamp overlap between blocks {idx} and {idx + 1}",
                )

            # Verify E001_VD simultaneous-translation ducking (`duck_under_next=True`)
            vd_items = {it["cue_id"]: it for it in manifests_by_id["E001_VD"]["timeline"]}
            self.assertIs(vd_items["vd_dlg_01_en"]["duck_under_next"], True)
            self.assertLess(
                float(vd_items["vd_dlg_02_zh"]["start_s"]),
                float(vd_items["vd_dlg_01_en"]["end_s"]),
                "Expected interpreter VO to enter while primary EN cue is ducked underneath",
            )

            # Part C: Verify `--skip-existing` per-variant idempotency (zero new _v002 files)
            mp3_before = sorted(p.name for p in masters_dir.glob("*.mp3"))
            subprocess.run(
                [
                    sys.executable,
                    str(COLAB_DIR / "launch_g4_global_edge_drama3.py"),
                    "--project-dir",
                    str(PROJECT_DIR),
                    "--cue-sheets-dir",
                    str(cue_dir),
                    "--output-dir",
                    str(run_out),
                    "--episodes",
                    "AUDITION,E001_VARIANTS",
                    "--skip-existing",
                    "--offline-dry-run",
                ],
                env=env,
                check=True,
            )
            mp3_after = sorted(p.name for p in masters_dir.glob("*.mp3"))
            self.assertEqual(mp3_before, mp3_after, "Expected --skip-existing to skip all 5 existing masters")

    def test_08_colab_notebook_validity_and_cli_flag_parity(self) -> None:
        self.assertTrue(NOTEBOOK_PATH.is_file())
        nb = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(nb["nbformat"], 4)
        self.assertEqual(nb["metadata"]["accelerator"], "GPU")
        self.assertEqual(nb["metadata"]["colab"]["gpuType"], "G4")

        all_src = "\n".join("".join(c.get("source", [])) for c in nb["cells"])
        self.assertIn("colab_agent_bridge.py", all_src)
        self.assertIn(".colab_auto_unassign", all_src)
        self.assertIn("runtime.unassign()", all_src)
        self.assertIn("launch_g4_global_edge_drama3.py", all_src)
        self.assertIn("AUDITION,E001_VARIANTS", all_src)
        self.assertIn("IPython.display", all_src)

        # Verify EVERY `--flag` passed to launch_g4_global_edge_drama3.py in Mode B exists in its ArgumentParser!
        mode_b_cells = [
            "".join(c.get("source", []))
            for c in nb["cells"]
            if c.get("cell_type") == "code" and "launch_g4_global_edge_drama3.py" in "".join(c.get("source", []))
        ]
        self.assertGreaterEqual(len(mode_b_cells), 1)
        parser = launcher_mod.build_arg_parser()
        valid_options: set[str] = set()
        for action in parser._actions:
            valid_options.update(action.option_strings)

        found_flags: set[str] = set()
        for cell_code in mode_b_cells:
            tree = ast.parse(cell_code)
            cmd_var_names: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                    list_src = ast.unparse(node.value)
                    if "launch_g4_global_edge_drama3.py" in list_src:
                        for tgt in node.targets:
                            if isinstance(tgt, ast.Name):
                                cmd_var_names.add(tgt.id)
                        for elt in ast.walk(node.value):
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str) and elt.value.startswith("--"):
                                found_flags.add(elt.value)
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in cmd_var_names
                    and node.func.attr in ("append", "extend")
                ):
                    for arg in node.args:
                        for elt in ast.walk(arg):
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str) and elt.value.startswith("--"):
                                found_flags.add(elt.value)

        self.assertEqual(
            found_flags,
            {"--episodes", "--profile", "--skip-existing", "--mirror-to-main-masters", "--auto-unassign"},
        )
        unknown_flags = found_flags - valid_options
        self.assertEqual(unknown_flags, set(), f"Notebook passes unsupported launcher flags: {unknown_flags}")

        # Verify ALL code cells parse cleanly and Mode B matches Mode A's /content/.colab_auto_unassign fallback
        for cell in nb["cells"]:
            if cell.get("cell_type") == "code":
                ast.parse("".join(cell.get("source", [])))
        self.assertIn(".colab_auto_unassign", mode_b_cells[0])
        self.assertIn("runtime.unassign()", mode_b_cells[0])

    def test_09_ast_zero_elevenlabs_zero_synthetic_tts_zero_third_party_toplevel(self) -> None:
        prod_py_files = [
            COLAB_DIR / "prepare_global_edge_voice_anchors.py",
            COLAB_DIR / "run_global_edge_96gb_studio.py",
            COLAB_DIR / "launch_g4_global_edge_drama3.py",
            SCRIPTS_DIR / "export_drama3_bundle.py",
        ]
        all_py_files = [*prod_py_files, Path(__file__).resolve()]

        allowed_local_modules = {
            "aigc_audio_pipeline",
            "prepare_global_edge_voice_anchors",
            "run_global_edge_96gb_studio",
            "launch_g4_global_edge_drama3",
            "export_drama3_bundle",
        }
        stdlib_names = set(sys.stdlib_module_names)

        forbidden_eleven = "".join(["eleven", "labs"])
        forbidden_edge_dash = "-".join(["edge", "tts"])
        forbidden_edge_under = "_".join(["edge", "tts"])

        for py_path in all_py_files:
            source = py_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_path))

            # 1. Check ZERO elevenlabs imports/calls anywhere in AST (and zero forbidden third-party top-level imports)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(forbidden_eleven, alias.name.lower(), f"Forbidden import in {py_path}")
                        self.assertNotIn(forbidden_edge_under, alias.name.lower(), f"Forbidden import in {py_path}")
                elif isinstance(node, ast.ImportFrom):
                    mod_name = (node.module or "").lower()
                    self.assertNotIn(forbidden_eleven, mod_name, f"Forbidden from-import in {py_path}")
                    self.assertNotIn(forbidden_edge_under, mod_name, f"Forbidden from-import in {py_path}")
                elif isinstance(node, ast.Attribute):
                    self.assertNotIn(forbidden_eleven, node.attr.lower(), f"Forbidden attr in {py_path}")

            for top_node in tree.body:
                if isinstance(top_node, ast.Import):
                    for alias in top_node.names:
                        root_mod = alias.name.split(".", 1)[0]
                        self.assertIn(
                            root_mod,
                            stdlib_names | allowed_local_modules,
                            f"Unauthorized third-party top-level import {root_mod!r} in {py_path}",
                        )
                elif isinstance(top_node, ast.ImportFrom) and top_node.module:
                    root_mod = top_node.module.split(".", 1)[0]
                    self.assertIn(
                        root_mod,
                        stdlib_names | allowed_local_modules,
                        f"Unauthorized third-party top-level from-import {root_mod!r} in {py_path}",
                    )

        # 2. Strictly ZERO literal legacy synthetic-TTS substrings in all production M4 artifacts
        for prod_artifact in (*prod_py_files, NOTEBOOK_PATH, ANCHOR_SOURCES_PATH):
            raw = prod_artifact.read_text(encoding="utf-8").lower()
            self.assertNotIn(forbidden_edge_dash, raw, f"Forbidden literal token in {prod_artifact}")
            self.assertNotIn(forbidden_edge_under, raw, f"Forbidden literal token in {prod_artifact}")
            self.assertNotIn(forbidden_eleven, raw, f"Forbidden elevenlabs token in {prod_artifact}")


if __name__ == "__main__":
    unittest.main()
