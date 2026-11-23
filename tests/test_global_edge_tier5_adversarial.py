"""Tier-5 White-Box Adversarial Regression Suite for Global Edge (《跨境底牌：硅深暗战》).

Pure Python stdlib `unittest` suite (zero third-party dependencies, isolated
`tempfile.TemporaryDirectory()` only — zero fixed `/tmp/test_*` paths, zero mocks,
zero skips, zero tautologies). Covers all 12 Tier-5 white-box findings (`G1`–`G6`,
`D1`–`D8`) with both positive and negative regression proofs.
"""

from __future__ import annotations

from array import array
import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
COLAB_DIR = REPO_ROOT / "colab_96gb"
GLOBAL_EDGE_DIR = REPO_ROOT / "projects" / "global_edge"
SCRIPTS_DIR = GLOBAL_EDGE_DIR / "scripts"
META_DIR = GLOBAL_EDGE_DIR / "00_节目圣经与第一季24集总纲"
CORPUS_DIR = GLOBAL_EDGE_DIR / "01_视频号语料与商业词库"
CUE_SHEETS_DIR = GLOBAL_EDGE_DIR / "02_分集广播剧台本"
E2E_HELPERS_PATH = REPO_ROOT / "tests" / "e2e_global_edge" / "e2e_helpers.py"
RAW_ARSENAL_PATH = Path("/tmp/arsenal_100_queue.json")

for _p in (SRC_DIR, COLAB_DIR, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from aigc_audio_pipeline.adapter import export_cue_sheet_markdown  # noqa: E402
from aigc_audio_pipeline.drama3_adapter import convert_to_drama3_anchor_wav  # noqa: E402
from aigc_audio_pipeline.mixer import (  # noqa: E402
    condition_dialogue_clip,
    master_episode_three_bus,
)
from aigc_audio_pipeline.models import (  # noqa: E402
    ActMusicSpec,
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    VoiceProfile,
    validate_v3_dialogue_text,
)
from aigc_audio_pipeline.qa import evaluate_dialogue_qa  # noqa: E402
import drama_helpers  # noqa: E402
import extract_100_clips_corpus as etl_mod  # noqa: E402
import launch_g4_global_edge_drama3 as launcher_mod  # noqa: E402
import prepare_global_edge_voice_anchors as prep_mod  # noqa: E402


def _load_e2e_helpers_no_bytecode():
    """Load `tests/e2e_global_edge/e2e_helpers.py` via spec_from_file_location without writing __pycache__."""
    prev_dont_write = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_tier5_e2e_helpers", E2E_HELPERS_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load {E2E_HELPERS_PATH}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_tier5_e2e_helpers"] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.dont_write_bytecode = prev_dont_write


def _write_uncorrelated_stereo_48k_wav(path: Path, duration_s: float = 2.5) -> Path:
    """Write an uncorrelated 48kHz stereo PCM16 WAV (L=330Hz, R=440Hz) for anchor loudness tests."""
    sr = 48000
    nframes = int(round(duration_s * sr))
    samples = array("h")
    for i in range(nframes):
        t = i / sr
        left = int(round(0.35 * 32767 * math.sin(2.0 * math.pi * 330.0 * t)))
        right = int(round(0.35 * 32767 * math.sin(2.0 * math.pi * 440.0 * t + 1.1)))
        samples.append(left)
        samples.append(right)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(samples.tobytes())
    return path


def _measure_lufs(wav_path: Path) -> float:
    """Measure integrated LUFS directly via FFmpeg loudnorm JSON output (no silent fallback)."""
    proc = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-i",
            str(wav_path),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"FFmpeg loudnorm failed (rc={proc.returncode}): {proc.stderr}")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, re.DOTALL)
    if not m:
        raise AssertionError(f"Missing loudnorm JSON block in FFmpeg output:\n{proc.stderr}")
    data = json.loads(m.group(0))
    return float(data["input_i"])


def _write_minimal_e001_va_sheet(path: Path, title: str = "E001_VA Tier-5 Pre-Unpacked Bundle Test") -> Path:
    """Write a minimal valid 4-cue E001_VA EpisodeCueSheet for fast real-FFmpeg launcher dry-runs."""
    sheet = EpisodeCueSheet(
        episode_id="E001_VA",
        chapter_number=1,
        title=title,
        mode="bilingual_business_drama",
        head_pad_s=0.1,
        tail_pad_s=0.2,
        acts=[
            ActMusicSpec(
                act_id="act_1",
                title="Act 1: Sand Hill Ambush",
                bgm_prompt="Minimalist cello pulse, strictly instrumental, no vocals",
            ),
            ActMusicSpec(
                act_id="act_5_debrief",
                title="Act 5: Black-Book Debrief",
                bgm_prompt="Warm restrained jazz-noir, strictly instrumental, no vocals",
            ),
        ],
        cues=[
            TimelineCue(
                cue_id="T5_C01",
                act_id="act_1",
                kind="dialogue",
                role_id="victoria_vance",
                speaker_name="Victoria Vance",
                language_code="en",
                text="[icy polite] That convertible note loss is a phantom number.",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=-0.10,
                subtitle_translation="那笔可转债亏损不过是账面幻数。",
            ),
            TimelineCue(
                cue_id="T5_C02",
                act_id="act_1",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text="[measured] It is not a cash loss, Victoria.",
                stability=0.5,
                acoustic_space="boardroom",
                gap_after_s=0.25,
                subtitle_translation="这不是现金亏损，维多利亚。",
            ),
            TimelineCue(
                cue_id="T5_C03",
                act_id="act_5_debrief",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text="[coach] That is a phantom number.",
                stability=0.5,
                acoustic_space="studio_warm",
                playback_rate=0.8,
                gap_after_s=0.3,
                subtitle_translation="慢速拆解：账面幻数。",
            ),
            TimelineCue(
                cue_id="T5_C04",
                act_id="act_5_debrief",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name="Lin Chen",
                language_code="en",
                text="[measured] That is a phantom number.",
                stability=0.5,
                acoustic_space="studio_warm",
                playback_rate=1.0,
                gap_after_s=1.8,
                subtitle_translation="原速跟读：账面幻数。",
            ),
        ],
    )
    sheet.save(path)
    return path


class TestGlobalEdgeTier5Adversarial(unittest.TestCase):
    """Comprehensive Tier-5 white-box regression tests closing G1–G6 and D1–D8."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.e2e = _load_e2e_helpers_no_bytecode()
        cls.registry = VoiceCastingRegistry.load(META_DIR / "voice_casting_registry.json")

    def _base_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_DIR)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    # ------------------------------------------------------------------
    # G1 — Exact offline_synthetic_stub whitelist in voice cast gate
    # ------------------------------------------------------------------
    def test_g1_voice_cast_gate_exact_offline_stub_whitelist(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t5_g1_") as td:
            tmp = Path(td)
            studio = tmp / "studio"
            prep_mod.prepare_all_global_edge_anchors(
                registry_path=META_DIR / "voice_casting_registry.json",
                anchor_sources_path=META_DIR / "anchor_sources.json",
                output_dir=studio,
                offline_stub=True,
            )
            (studio / "voice_casting_registry.json").write_text(
                (META_DIR / "voice_casting_registry.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            _write_minimal_e001_va_sheet(studio / "cue_sheets" / "E001_VA_test.json")

            # Exact "offline_synthetic_stub": allowed in dry-run, rejected in production
            ok_prod, _ = launcher_mod.validate_production_voice_cast(studio, allow_offline_stub=False)
            ok_dry, errs_dry = launcher_mod.validate_production_voice_cast(studio, allow_offline_stub=True)
            self.assertFalse(ok_prod, "Production gate must reject offline_synthetic_stub")
            self.assertTrue(ok_dry, f"Dry-run gate must allow exact offline_synthetic_stub: {errs_dry}")

            vc_file = studio / "voice_cast_drama3.json"
            base_cast = json.loads(vc_file.read_text(encoding="utf-8"))

            # Spoofed synthetic / case-mutated / Neural sources MUST fail BOTH production AND dry-run
            for spoof in (
                "synthetic_voice_v1",
                "my_synthetic_clone",
                "offline_synthetic_stub_v2",
                "OFFLINE_SYNTHETIC_STUB",
                "openai_synthetic",
                "zh-CN-YunxiNeural",
            ):
                mut = copy.deepcopy(base_cast)
                mut["characters"]["lin_chen"]["source_voice_name"] = spoof
                vc_file.write_text(json.dumps(mut, ensure_ascii=False, indent=2), encoding="utf-8")
                self.assertFalse(
                    launcher_mod.validate_production_voice_cast(studio, allow_offline_stub=False)[0],
                    f"Production gate failed to reject {spoof!r}",
                )
                self.assertFalse(
                    launcher_mod.validate_production_voice_cast(studio, allow_offline_stub=True)[0],
                    f"Dry-run gate failed to reject non-exact synthetic source {spoof!r}",
                )

            # Live studio CLI under --offline-dry-run MUST exit non-zero on synthetic_voice_v1
            mut = copy.deepcopy(base_cast)
            mut["characters"]["lin_chen"]["source_voice_name"] = "synthetic_voice_v1"
            vc_file.write_text(json.dumps(mut, ensure_ascii=False, indent=2), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(COLAB_DIR / "run_global_edge_96gb_studio.py"),
                    "--studio-dir",
                    str(studio),
                    "--output-dir",
                    str(tmp / "out"),
                    "--cache-dir",
                    str(tmp / "cache"),
                    "--episodes",
                    "E001_VA",
                    "--offline-dry-run",
                ],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(
                proc.returncode,
                0,
                f"Studio CLI should reject synthetic_voice_v1 even under --offline-dry-run:\n{proc.stdout}\n{proc.stderr}",
            )

    # ------------------------------------------------------------------
    # G2 — Pre-unpacked self-contained --bundle-dir outside repo
    # ------------------------------------------------------------------
    def test_g2_launcher_offline_dry_run_preunpacked_bundle_outside_repo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t5_g2_") as td:
            tmp = Path(td)
            mini_cues = tmp / "mini_cues"
            mini_cues.mkdir(parents=True, exist_ok=True)
            _write_minimal_e001_va_sheet(mini_cues / "E001_VA_mini.json")

            unpacked = tmp / "unpacked_bundle"
            exp_proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "export_drama3_bundle.py"),
                    "--project-dir",
                    str(GLOBAL_EDGE_DIR),
                    "--cue-sheets-dir",
                    str(mini_cues),
                    "--output-dir",
                    str(unpacked),
                    "--offline-stub",
                ],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(exp_proc.returncode, 0, f"Export failed:\n{exp_proc.stderr}")

            vc_path = unpacked / "voice_cast_drama3.json"
            vc_before = vc_path.read_text(encoding="utf-8")

            # (a) Run BUNDLED launcher from cwd=tmp (outside repo!) with --bundle-dir unpacked
            out1 = tmp / "out_bundled"
            clean_env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            clean_env["PYTHONDONTWRITEBYTECODE"] = "1"
            p1 = subprocess.run(
                [
                    sys.executable,
                    str(unpacked / "launch_g4_global_edge_drama3.py"),
                    "--bundle-dir",
                    str(unpacked),
                    "--output-dir",
                    str(out1),
                    "--episodes",
                    "E001_VA",
                    "--offline-dry-run",
                ],
                cwd=str(tmp),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(p1.returncode, 0, f"Bundled launcher failed:\n{p1.stdout}\n{p1.stderr}")
            for ext in ("wav", "mp3", "srt", "json", "done"):
                matches = list((out1 / "masters").glob(f"E001_VA*_v001.{ext}"))
                self.assertEqual(len(matches), 1, f"Missing E001_VA*_v001.{ext} in {out1 / 'masters'}")
            self.assertEqual(vc_path.read_text(encoding="utf-8"), vc_before, "Pre-unpacked bundle was clobbered!")

            # (b) Run REPO launcher with --bundle-dir unpacked + nonexistent --project-dir + --cue-sheets-dir override
            override_cues = tmp / "override_cues"
            override_cues.mkdir(parents=True, exist_ok=True)
            _write_minimal_e001_va_sheet(
                override_cues / "E001_VA_override.json",
                title="E001_VA_OVERRIDE_MARKER",
            )
            out2 = tmp / "out_repo_launcher"
            p2 = subprocess.run(
                [
                    sys.executable,
                    str(COLAB_DIR / "launch_g4_global_edge_drama3.py"),
                    "--bundle-dir",
                    str(unpacked),
                    "--project-dir",
                    str(tmp / "nonexistent_project_dir"),
                    "--cue-sheets-dir",
                    str(override_cues),
                    "--output-dir",
                    str(out2),
                    "--episodes",
                    "E001_VA",
                    "--offline-dry-run",
                ],
                cwd=str(tmp),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(p2.returncode, 0, f"Repo launcher w/ pre-unpacked bundle failed:\n{p2.stdout}\n{p2.stderr}")
            man_files = list((out2 / "masters").glob("E001_VA*_v001.json"))
            self.assertEqual(len(man_files), 1, f"Missing E001_VA*_v001.json in {out2 / 'masters'}")
            man_payload = json.loads(man_files[0].read_text(encoding="utf-8"))
            self.assertEqual(
                man_payload.get("title"),
                "E001_VA_OVERRIDE_MARKER",
                "--cue-sheets-dir override was not forwarded to studio runner!",
            )

            # (c) Tampered pre-unpacked bundle MUST be rejected (zero gate bypass)
            tampered = json.loads(vc_before)
            tampered["characters"]["lin_chen"]["source_voice_name"] = "synthetic_voice_v1"
            vc_path.write_text(json.dumps(tampered, ensure_ascii=False, indent=2), encoding="utf-8")
            p3 = subprocess.run(
                [
                    sys.executable,
                    str(unpacked / "launch_g4_global_edge_drama3.py"),
                    "--bundle-dir",
                    str(unpacked),
                    "--output-dir",
                    str(tmp / "out_tampered"),
                    "--episodes",
                    "E001_VA",
                    "--offline-dry-run",
                ],
                cwd=str(tmp),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(p3.returncode, 0, "Tampered pre-unpacked bundle should have failed validation!")

    # ------------------------------------------------------------------
    # G3 — Bundle exporter anti-laundering, missing anchors, in-place & stereo LUFS
    # ------------------------------------------------------------------
    def test_g3_bundle_exporter_rejects_tainted_or_missing_anchors_and_handles_inplace_stereo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t5_g3_") as td:
            tmp = Path(td)
            mini_cues = tmp / "cues"
            mini_cues.mkdir(parents=True, exist_ok=True)
            _write_minimal_e001_va_sheet(mini_cues / "E001_VA_g3.json")

            valid_anchors = tmp / "valid_anchors"
            prep_mod.prepare_all_global_edge_anchors(
                registry_path=META_DIR / "voice_casting_registry.json",
                anchor_sources_path=META_DIR / "anchor_sources.json",
                output_dir=valid_anchors,
                offline_stub=True,
            )

            # (a) Tainted v1_edge_tts / Neural / missing-role --anchors-dir MUST fail
            tainted_dir = tmp / "tainted_anchors"
            shutil.copytree(valid_anchors, tainted_dir)
            t_vc_path = tainted_dir / "voice_cast_drama3.json"
            t_vc = json.loads(t_vc_path.read_text(encoding="utf-8"))
            t_vc["anchor_schema_version"] = "v1_edge_tts"
            t_vc["characters"]["lin_chen"]["source_voice_name"] = "zh-CN-YunxiNeural"
            del t_vc["characters"]["henrik_lindqvist"]
            t_vc_path.write_text(json.dumps(t_vc, ensure_ascii=False, indent=2), encoding="utf-8")

            p_tainted = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "export_drama3_bundle.py"),
                    "--cue-sheets-dir",
                    str(mini_cues),
                    "--anchors-dir",
                    str(tainted_dir),
                    "--output-dir",
                    str(tmp / "out_tainted"),
                    "--offline-stub",
                ],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(p_tainted.returncode, 0, "Exporter laundered tainted v1_edge_tts/Neural anchors!")

            # (b) --real-anchors MUST reject offline_synthetic_stub --anchors-dir
            p_real_stub = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "export_drama3_bundle.py"),
                    "--cue-sheets-dir",
                    str(mini_cues),
                    "--anchors-dir",
                    str(valid_anchors),
                    "--output-dir",
                    str(tmp / "out_real_stub"),
                    "--real-anchors",
                ],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(p_real_stub.returncode, 0, "--real-anchors accepted offline_synthetic_stub anchors!")

            # (c) Nonexistent --anchors-dir MUST fail (never silently synthesize stubs)
            p_missing = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "export_drama3_bundle.py"),
                    "--cue-sheets-dir",
                    str(mini_cues),
                    "--anchors-dir",
                    str(tmp / "does_not_exist_anchors"),
                    "--output-dir",
                    str(tmp / "out_missing"),
                    "--offline-stub",
                ],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertNotEqual(p_missing.returncode, 0, "Nonexistent --anchors-dir silently fell back to stubs!")

            # (d) In-place export (--anchors-dir X --output-dir X) MUST succeed cleanly
            p_inplace = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "export_drama3_bundle.py"),
                    "--cue-sheets-dir",
                    str(mini_cues),
                    "--anchors-dir",
                    str(valid_anchors),
                    "--output-dir",
                    str(valid_anchors),
                    "--offline-stub",
                ],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(p_inplace.returncode, 0, f"In-place export failed:\n{p_inplace.stderr}")
            with wave.open(str(valid_anchors / "voice_anchors" / "lin_chen.wav"), "rb") as wf:
                self.assertEqual((wf.getnchannels(), wf.getsampwidth(), wf.getframerate()), (1, 2, 44100))
                self.assertGreater(wf.getnframes(), 44100)

            # (e) convert_to_drama3_anchor_wav on uncorrelated 48kHz stereo WAV hits -16.0 +/- 1.5 LUFS & supports src == dst
            stereo_wav = _write_uncorrelated_stereo_48k_wav(tmp / "stereo_in.wav", duration_s=2.5)
            mono_out = tmp / "mono_out.wav"
            dur = convert_to_drama3_anchor_wav(stereo_wav, mono_out)
            self.assertGreater(dur, 2.0)
            lufs = _measure_lufs(mono_out)
            self.assertAlmostEqual(lufs, -16.0, delta=1.5, msg=f"Stereo->mono anchor LUFS drifted: {lufs:.2f}")

            # In-place convert_to_drama3_anchor_wav(p, p)
            dur_inplace = convert_to_drama3_anchor_wav(mono_out, mono_out)
            self.assertGreater(dur_inplace, 2.0)
            self.assertFalse(mono_out.with_suffix(".cond_tmp.wav").exists())

    # ------------------------------------------------------------------
    # G4 — ETL cleanly rejects overflow, extreme floats, deep JSON & leaves zero dirty out_dir
    # ------------------------------------------------------------------
    def test_g4_etl_cleanly_rejects_overflow_extreme_floats_and_deep_json(self) -> None:
        self.assertTrue(RAW_ARSENAL_PATH.is_file(), f"Missing raw corpus source: {RAW_ARSENAL_PATH}")
        base_raw = json.loads(RAW_ARSENAL_PATH.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory(prefix="t5_g4_") as td:
            tmp = Path(td)

            # Case 1–3: 10**400 in duration_sec, virality_score, subtitles[0].start_sec
            # Case 4: 2x 1e308 in duration_sec (float64 sum overflow)
            def _write_mut_json(name: str, mutator) -> Path:
                d = copy.deepcopy(base_raw)
                mutator(d)
                p = tmp / f"{name}.json"
                p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
                return p

            big_int = 10**400
            mut_paths = [
                ("dur_10pow400", _write_mut_json("dur_10pow400", lambda d: d[0].__setitem__("duration_sec", big_int))),
                (
                    "vir_10pow400",
                    _write_mut_json("vir_10pow400", lambda d: d[0]["plan"].__setitem__("virality_score", big_int)),
                ),
                (
                    "sub_10pow400",
                    _write_mut_json(
                        "sub_10pow400", lambda d: d[0]["plan"]["subtitles"][0].__setitem__("start_sec", big_int)
                    ),
                ),
                (
                    "dur_2x_1e308",
                    _write_mut_json(
                        "dur_2x_1e308",
                        lambda d: (d[0].__setitem__("duration_sec", 1e308), d[1].__setitem__("duration_sec", 1e308)),
                    ),
                ),
            ]
            # Case 5: 5001-digit integer (int_max_str_digits ValueError)
            p_5001 = tmp / "int_5001.json"
            p_5001.write_text('[{"duration_sec": ' + ("9" * 5001) + "}]", encoding="utf-8")
            mut_paths.append(("int_5001_digits", p_5001))

            # Case 6: 50,000-deep nested JSON (RecursionError)
            p_deep = tmp / "deep_rec.json"
            p_deep.write_text("[" * 50000 + "]" * 50000, encoding="utf-8")
            mut_paths.append(("deep_recursion", p_deep))

            for label, src_path in mut_paths:
                out_dir = tmp / f"out_{label}"
                proc = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS_DIR / "extract_100_clips_corpus.py"),
                        "--source",
                        str(src_path),
                        "--out-dir",
                        str(out_dir),
                    ],
                    env=self._base_env(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(proc.returncode, 1, f"{label}: expected rc=1, got {proc.returncode}")
                self.assertIn("ERROR:", proc.stderr, f"{label}: missing clean ERROR: prefix:\n{proc.stderr}")
                self.assertNotIn("Traceback", proc.stderr, f"{label}: unhandled Traceback leaked:\n{proc.stderr}")
                self.assertFalse(out_dir.exists(), f"{label}: dirty --out-dir was created on error!")

            # Direct write_outputs serialization guard: inf/nan raises CorpusValidationError BEFORE mkdir
            dirty_out = tmp / "never_created_dir"
            with self.assertRaises(etl_mod.CorpusValidationError):
                etl_mod.write_outputs(dirty_out, {"bad": float("inf")}, [], "# report")
            self.assertFalse(dirty_out.exists(), "write_outputs created out_dir despite serialization failure!")

    # ------------------------------------------------------------------
    # G5 (part 1) — models.py bool/type/NaN & chained duck_under_next guards
    # ------------------------------------------------------------------
    def test_g5_models_validation_bool_type_and_chained_duck_guards(self) -> None:
        # validate_v3_dialogue_text stability guards
        for bad_stab in (True, False, "0.5", None, float("nan"), float("inf")):
            errs = validate_v3_dialogue_text("[measured] Clean text.", bad_stab, language_code="en")  # type: ignore[arg-type]
            self.assertTrue(
                any("stability" in e for e in errs),
                f"Expected stability validation error for {bad_stab!r}, got {errs}",
            )

        def _sheet(cues: list[TimelineCue]) -> EpisodeCueSheet:
            return EpisodeCueSheet(
                episode_id="E001_G5",
                chapter_number=1,
                title="G5 Validation Test",
                mode="bilingual_business_drama",
                acts=[ActMusicSpec(act_id="a1", title="Act 1", bgm_prompt="Minimalist cello, no vocals")],
                cues=cues,
            )

        # duck_lead_in_s, duck_gain, duration_seconds type/bool/NaN checks MUST return errors (never TypeError!)
        bad_numeric_values = (True, False, "2.0", None, float("nan"), float("inf"))
        for bad_val in bad_numeric_values:
            s_lead = _sheet(
                [
                    TimelineCue(
                        cue_id="L1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en",
                        text="Hello.", duck_under_next=True, duck_lead_in_s=bad_val,  # type: ignore[arg-type]
                    ),
                    TimelineCue(cue_id="L2", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="你好。"),
                ]
            )
            errs_lead = s_lead.validate(self.registry)
            self.assertTrue(any("duck_lead_in_s" in e for e in errs_lead), f"lead_in={bad_val!r}: {errs_lead}")

            s_gain = _sheet(
                [
                    TimelineCue(
                        cue_id="G1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en",
                        text="Hello.", duck_under_next=True, duck_gain=bad_val,  # type: ignore[arg-type]
                    ),
                    TimelineCue(cue_id="G2", act_id="a1", kind="dialogue", role_id="zhou_mo", language_code="zh", text="你好。"),
                ]
            )
            errs_gain = s_gain.validate(self.registry)
            self.assertTrue(any("duck_gain" in e for e in errs_gain), f"duck_gain={bad_val!r}: {errs_gain}")

            s_dur = _sheet(
                [
                    TimelineCue(
                        cue_id="S1", act_id="a1", kind="sfx", sfx_prompt="Click, no voice",
                        duration_seconds=bad_val,  # type: ignore[arg-type]
                    )
                ]
            )
            errs_dur = s_dur.validate(self.registry)
            self.assertTrue(any("duration_seconds" in e for e in errs_dur), f"duration_seconds={bad_val!r}: {errs_dur}")

        # Chained duck_under_next MUST be rejected cleanly
        s_chained = _sheet(
            [
                TimelineCue(cue_id="K1", act_id="a1", kind="dialogue", role_id="alistair_finch", language_code="en", text="First.", duck_under_next=True),
                TimelineCue(cue_id="K2", act_id="a1", kind="dialogue", role_id="victoria_vance", language_code="en", text="Second.", duck_under_next=True),
                TimelineCue(cue_id="K3", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="zh", text="同传翻译。"),
            ]
        )
        errs_chain = s_chained.validate(self.registry)
        self.assertTrue(any("Chained duck_under_next" in e for e in errs_chain), f"Expected chained duck rejection: {errs_chain}")

    # ------------------------------------------------------------------
    # G5 (part 2) — Short duck overlap, SRT/MD control-char sanitization, QA NaN
    # ------------------------------------------------------------------
    def test_g5_mixer_short_duck_overlap_srt_control_char_sanitization_and_qa_nan(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t5_g5_mix_") as td:
            tmp = Path(td)
            # 1. Short 0.50s duck_under_next cue MUST overlap interpreter before d1.end_s
            sheet = EpisodeCueSheet(
                episode_id="E001_G5_MIX",
                chapter_number=1,
                title="Short Duck & Control Char Test",
                mode="bilingual_business_drama",
                head_pad_s=0.30,
                tail_pad_s=0.30,
                acts=[ActMusicSpec(act_id="a1", title="Act 1", bgm_prompt="Minimalist cello, no vocals")],
                cues=[
                    TimelineCue(
                        cue_id="D1",
                        act_id="a1",
                        kind="dialogue",
                        role_id="alistair_finch",
                        speaker_name="Alistair Finch",
                        language_code="en",
                        text="[deadpan] Short line.",
                        duck_under_next=True,
                        duck_lead_in_s=2.0,
                        duck_gain=0.15,
                        gap_after_s=0.0,
                    ),
                    TimelineCue(
                        cue_id="D2",
                        act_id="a1",
                        kind="dialogue",
                        role_id="lin_chen",
                        speaker_name="Lin Chen",
                        language_code="zh",
                        text="[aside] 同步口译叠音测试。",
                        gap_after_s=0.30,
                    ),
                    TimelineCue(
                        cue_id="D3",
                        act_id="a1",
                        kind="dialogue",
                        role_id="victoria_vance",
                        speaker_name="Victoria Vance",
                        language_code="en",
                        text="[measured] Control character test.",
                        gap_after_s=0.30,
                        subtitle_translation="第一行\r\n\r\n第二行\x00\x07\x1b[31m红字\x7f",
                    ),
                ],
            )
            self.assertEqual(sheet.validate(self.registry), [])

            w1 = self.e2e.write_sine_wav(tmp / "d1.wav", 0.50, freq_hz=330.0, sample_rate=48000, channels=2, amplitude=0.4)
            w2 = self.e2e.write_sine_wav(tmp / "d2.wav", 1.50, freq_hz=440.0, sample_rate=48000, channels=2, amplitude=0.4)
            w3 = self.e2e.write_sine_wav(tmp / "d3.wav", 1.20, freq_hz=520.0, sample_rate=48000, channels=2, amplitude=0.4)

            res = master_episode_three_bus(
                cue_sheet=sheet,
                cue_audio_map={"D1": w1, "D2": w2, "D3": w3},
                act_bgm_map={},
                output_dir=tmp / "masters",
                registry=self.registry,
            )
            tl = {it["cue_id"]: it for it in json.loads(Path(res["manifest_json"]).read_text(encoding="utf-8"))["timeline"]}
            self.assertLess(
                tl["D2"]["start_s"],
                tl["D1"]["end_s"],
                f"Short-clip duck_under_next placed D2 after D1 ended! D1={tl['D1']} D2={tl['D2']}",
            )

            # 2. C0/DEL control chars stripped from BOTH .srt and exported .md
            srt_text = Path(res["subtitles_srt"]).read_text(encoding="utf-8")
            md_text = export_cue_sheet_markdown(sheet, registry=self.registry)
            for label, rendered in (("SRT", srt_text), ("Markdown", md_text)):
                for ctrl in ("\x00", "\x07", "\x1b", "\x7f"):
                    self.assertNotIn(ctrl, rendered, f"Control byte {ctrl!r} leaked into {label}!")
                self.assertIn("第一行 第二行", rendered, f"Expected normalized Chinese gloss in {label}")
                self.assertIn("红字", rendered, f"Expected preserved CJK text in {label}")

        # 3. qa.py accepts finite signal and rejects NaN / +/-inf duration_s and peak_dbfs
        ok_qa = evaluate_dialogue_qa(
            tagged_prompt="[measured] That is a phantom number.",
            asr_text="That is a phantom number.",
            duration_s=1.5,
            peak_dbfs=-12.0,
            language_code="en",
        )
        self.assertTrue(ok_qa.passed, f"Expected finite QA to pass, got {ok_qa.reasons}")
        for bad_dur, bad_peak in (
            (float("nan"), -12.0),
            (float("inf"), -12.0),
            (1.5, float("nan")),
            (1.5, float("-inf")),
        ):
            qa_res = evaluate_dialogue_qa(
                tagged_prompt="[measured] That is a phantom number.",
                asr_text="That is a phantom number.",
                duration_s=bad_dur,
                peak_dbfs=bad_peak,
                language_code="en",
            )
            self.assertFalse(
                qa_res.passed,
                f"evaluate_dialogue_qa passed non-finite duration={bad_dur!r}, peak={bad_peak!r}!",
            )

    # ------------------------------------------------------------------
    # G6a + D4 — Real FFmpeg boardroom vs vast_hall / mental_realm / memory_echo DSP discrimination
    # ------------------------------------------------------------------
    def test_g6_and_d4_boardroom_vs_vast_hall_reverb_discrimination(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t5_g6_dsp_") as td:
            tmp = Path(td)
            mt_src = self.e2e.write_multitone_wav(
                tmp / "mt_src.wav",
                1.6,
                [(100.0, 0.16), (150.0, 0.16), (1000.0, 0.16), (3200.0, 0.16), (6000.0, 0.16)],
                sample_rate=48000,
                channels=2,
            )
            burst_src = self.e2e.write_tone_burst_wav(tmp / "burst_src.wav", burst_s=0.80, silence_s=0.80, channels=2)

            mt_out: dict[str, Path] = {}
            for sp in ("dry", "phone_call", "inner_monologue", "boardroom"):
                dst = tmp / f"mt_{sp}.wav"
                condition_dialogue_clip(mt_src, dst, acoustic_space=sp)
                mt_out[sp] = dst

            burst_out: dict[str, Path] = {}
            for sp in ("dry", "inner_monologue", "boardroom", "vast_hall", "mental_realm", "memory_echo"):
                dst = tmp / f"burst_{sp}.wav"
                condition_dialogue_clip(burst_src, dst, acoustic_space=sp)
                burst_out[sp] = dst

            # Positive: genuine boardroom passes with near-zero 45-160ms late tail
            report = self.e2e.oracle_corporate_acoustic_spaces_dsp(
                dry_mt_wav=mt_out["dry"],
                phone_mt_wav=mt_out["phone_call"],
                inner_mt_wav=mt_out["inner_monologue"],
                boardroom_mt_wav=mt_out["boardroom"],
                dry_burst_wav=burst_out["dry"],
                inner_burst_wav=burst_out["inner_monologue"],
                boardroom_burst_wav=burst_out["boardroom"],
            )
            self.assertLess(report["boardroom_burst"]["late"], 0.005)

            # Negative: vast_hall, mental_realm, memory_echo MUST all fail when substituted as boardroom
            for bad_space in ("vast_hall", "mental_realm", "memory_echo"):
                with self.assertRaises(AssertionError, msg=f"{bad_space} falsely passed as boardroom!"):
                    self.e2e.oracle_corporate_acoustic_spaces_dsp(
                        dry_mt_wav=mt_out["dry"],
                        phone_mt_wav=mt_out["phone_call"],
                        inner_mt_wav=mt_out["inner_monologue"],
                        boardroom_mt_wav=mt_out["boardroom"],
                        dry_burst_wav=burst_out["dry"],
                        inner_burst_wav=burst_out["inner_monologue"],
                        boardroom_burst_wav=burst_out[bad_space],
                    )

    # ------------------------------------------------------------------
    # D1 + G6b — Notebook AST dynamic flags & multiline !magic continuations
    # ------------------------------------------------------------------
    def test_d1_and_g6_notebook_ast_dynamic_flags_and_multiline_magic(self) -> None:
        nb_path = COLAB_DIR / "Global_Edge_96GB_Drama3_Studio.ipynb"
        real_nb = json.loads(nb_path.read_text(encoding="utf-8"))
        extracted = self.e2e.extract_notebook_launcher_flags(real_nb)
        expected_flags = {
            "--episodes",
            "--profile",
            "--skip-existing",
            "--mirror-to-main-masters",
            "--auto-unassign",
        }
        self.assertEqual(extracted, expected_flags)

        help_proc = subprocess.run(
            [sys.executable, str(COLAB_DIR / "launch_g4_global_edge_drama3.py"), "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        help_flags = set(re.findall(r"--[a-zA-Z0-9][a-zA-Z0-9_-]*", help_proc.stdout))
        self.assertTrue(expected_flags.issubset(help_flags))

        # Positive: multiline trailing-backslash magic cell passes cleanly
        mm_nb = copy.deepcopy(real_nb)
        for cell in mm_nb["cells"]:
            if cell.get("id") == "ge05_mode_b_run":
                cell["source"] = [
                    "!python3 colab_96gb/launch_g4_global_edge_drama3.py \\\n",
                    "  --episodes E001_VARIANTS \\\n",
                    "  --skip-existing\n",
                ]
        res = self.e2e.oracle_notebook_and_bundle_integrity(notebook_data=mm_nb, launcher_help_flags=help_flags)
        self.assertEqual(res["notebook"]["launcher_flags"], ["--episodes", "--skip-existing"])

        # Negative: ALL 6 dynamic bogus-flag mutations on the real Mode B cell MUST fail
        dyn_cases = [
            ("append", ["cmd.append('--bogus-append')\n"]),
            ("extend", ["cmd.extend(['--bogus-extend', '1'])\n"]),
            ("augassign", ["cmd += ['--bogus-aug']\n"]),
            ("binop_add", ["cmd = cmd + ['--bogus-add']\n"]),
            ("fstring", ["x = '1'\n", "cmd.append(f'--bogus-fstr={x}')\n"]),
            ("indirect_helper", ["extra = ['--bogus-ind']\n", "cmd.extend(extra)\n"]),
        ]
        for lbl, snippet in dyn_cases:
            mut_nb = copy.deepcopy(real_nb)
            for cell in mut_nb["cells"]:
                if cell.get("id") == "ge05_mode_b_run":
                    src = list(cell["source"])
                    insert_at = next(i for i, ln in enumerate(src) if "subprocess.check_call(cmd" in ln)
                    src[insert_at:insert_at] = snippet
                    cell["source"] = src
            with self.assertRaises(AssertionError, msg=f"Dynamic notebook bogus flag ({lbl}) escaped oracle!"):
                self.e2e.oracle_notebook_and_bundle_integrity(notebook_data=mut_nb, launcher_help_flags=help_flags)

    # ------------------------------------------------------------------
    # D2 — Season 1 24-ep bijection strict type checks (no None / {} / int bypass)
    # ------------------------------------------------------------------
    def test_d2_season1_bijection_rejects_none_empty_dict_and_non_string_fields(self) -> None:
        live_map = json.loads((META_DIR / "season1_24ep_map.json").read_text(encoding="utf-8"))
        self.e2e.oracle_season1_24ep_bijection(live_map)

        mutators = [
            ("target_phrases_empty_dict", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, {})),
            ("target_phrases_blank_phrase_en", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, {"phrase_en": "   "})),
            ("target_phrases_none_elem", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, None)),
            ("target_phrases_int_elem", lambda d: d["episodes"][0]["target_phrases"].__setitem__(0, 123)),
            ("viral_45s_hook_empty_dict", lambda d: d["episodes"][0].__setitem__("viral_45s_hook", {})),
            ("viral_45s_hook_blank_fields", lambda d: d["episodes"][0].__setitem__("viral_45s_hook", {"conflict_angle": "", "hook_line_en": ""})),
            ("viral_45s_hook_none", lambda d: d["episodes"][0].__setitem__("viral_45s_hook", None)),
            ("title_zh_none", lambda d: d["episodes"][0].__setitem__("title_zh", None)),
            ("cliffhanger_zh_none", lambda d: d["episodes"][0].__setitem__("cliffhanger_zh", None)),
        ]
        for lbl, mut in mutators:
            bad_map = copy.deepcopy(live_map)
            mut(bad_map)
            with self.assertRaises(AssertionError, msg=f"D2 mutant {lbl} bypassed oracle_season1_24ep_bijection!"):
                self.e2e.oracle_season1_24ep_bijection(bad_map)

    # ------------------------------------------------------------------
    # D3 — Expanded Xianxia tropes, narrow ML-jargon allowlist, ASCII 0 guardrail
    # ------------------------------------------------------------------
    def test_d3_xianxia_tropes_ml_jargon_and_zero_guardrail_across_all_docs(self) -> None:
        # Positive: ALL live Global Edge Markdown files pass with 0 false positives
        md_files = sorted(GLOBAL_EDGE_DIR.rglob("*.md"))
        self.assertGreaterEqual(len(md_files), 10)
        for md_p in md_files:
            self.e2e.assert_no_xianxia_plot_drift(md_p.read_text(encoding="utf-8"), str(md_p.name))

        # Positive specificity controls
        self.e2e.assert_no_xianxia_plot_drift("对比推理轻量化与预训练炼丹天价成本。", "ml_ok")
        self.e2e.assert_no_xianxia_plot_drift("上线门禁确保 0 仙侠词泄露。", "zero_ok")

        # Negative: expanded tropes banned in BOTH Markdown ban tables AND prose
        for trope in ("炼气", "渡劫", "筑基", "元婴", "化神", "飞升", "辟谷", "灵根", "道侣", "丹田", "道行", "炼丹"):
            ban_tbl = f"| 违禁词 | 严禁出现 |\n|---|---|\n| 剧情 | {trope} |\n"
            with self.assertRaises(AssertionError, msg=f"Trope {trope!r} slipped past inside ban table!"):
                self.e2e.assert_no_xianxia_plot_drift(ban_tbl, f"ban_{trope}")
            with self.assertRaises(AssertionError, msg=f"Trope {trope!r} slipped past in prose!"):
                self.e2e.assert_no_xianxia_plot_drift(f"商战剧情中出现{trope}元素。", f"prose_{trope}")

        # Negative: '10 集仙侠' MUST NOT match '0' negation regex
        with self.assertRaises(AssertionError):
            self.e2e.assert_no_xianxia_plot_drift("第 10 集仙侠商战终极对决。", "ep10_xianxia")

    # ------------------------------------------------------------------
    # D5 — Lexicon provenance: 4-char stopword slash, per-cid check, world_bridge empty clip_ids
    # ------------------------------------------------------------------
    def test_d5_lexicon_provenance_blocks_stopword_slash_extra_cids_and_world_bridge_cids(self) -> None:
        corp = json.loads((CORPUS_DIR / "corpus_100_structured.json").read_text(encoding="utf-8"))
        lex = json.loads((CORPUS_DIR / "executive_lexicon.json").read_text(encoding="utf-8"))
        self.e2e.oracle_lexicon_provenance_70_30(lex, corp)

        # (1) 4-char stopword slash spoof
        m1 = copy.deepcopy(lex)
        first_corpus = next(e for e in m1 if e["source_type"] == "corpus")
        first_cid = first_corpus["clip_ids"][0]
        m_corp = copy.deepcopy(corp)
        for c in m_corp["clips"]:
            if c["clip_id"] == first_cid:
                c["en_clean"] = "We proved that this deal structure holds."
        first_corpus["phrase_en"] = "that / totally fabricated bogus jargon"
        first_corpus["verbatim_context_en"] = "We proved that this deal structure holds."
        with self.assertRaises(AssertionError, msg="4-char stopword slash spoof bypassed oracle!"):
            self.e2e.oracle_lexicon_provenance_70_30(m1, m_corp)

        # (2) Unrelated valid clip_id appended to corpus entry
        m2 = copy.deepcopy(lex)
        target_e = next(e for e in m2 if e["source_type"] == "corpus" and "015_AI" not in e["clip_ids"])
        target_e["clip_ids"].append("015_AI")
        with self.assertRaises(AssertionError, msg="Extra unrelated clip_id bypassed oracle!"):
            self.e2e.oracle_lexicon_provenance_70_30(m2, corp)

        # (3) world_bridge entry with non-empty clip_ids
        m3 = copy.deepcopy(lex)
        wb_e = next(e for e in m3 if e["source_type"] == "world_bridge")
        wb_e["clip_ids"] = ["02_BIZ_Anthropic"]
        with self.assertRaises(AssertionError, msg="world_bridge non-empty clip_ids bypassed oracle!"):
            self.e2e.oracle_lexicon_provenance_70_30(m3, corp)

    # ------------------------------------------------------------------
    # D6 — AST zero-API / zero-edge-tts list-mutator taint propagation
    # ------------------------------------------------------------------
    def test_d6_ast_zero_api_propagates_list_mutator_taint(self) -> None:
        # Positive: benign list mutations + all real Global Edge / Colab scripts pass
        self.e2e.oracle_ast_zero_api_and_zero_edge_tts(
            'import subprocess\ncmd = ["python3"]\ncmd.append("--episodes")\nsubprocess.run(cmd)\n',
            "benign.py",
        )
        for py_path in (
            COLAB_DIR / "prepare_global_edge_voice_anchors.py",
            COLAB_DIR / "run_global_edge_96gb_studio.py",
            COLAB_DIR / "launch_g4_global_edge_drama3.py",
            SCRIPTS_DIR / "export_drama3_bundle.py",
            SCRIPTS_DIR / "build_e001_variants.py",
        ):
            self.e2e.oracle_ast_zero_api_and_zero_edge_tts(py_path.read_text(encoding="utf-8"), py_path.name)

        # Negative: append / extend / insert tainting MUST all be caught
        for lbl, code in (
            ("append", 'import subprocess\ncmd = ["python3"]\ncmd.append("edge-tts")\nsubprocess.run(cmd)\n'),
            ("extend", 'import subprocess\ncmd = ["python3"]\ncmd.extend(["edge-tts", "-t", "x"])\nsubprocess.run(cmd)\n'),
            ("insert", 'import subprocess\ncmd = ["-t", "x"]\ncmd.insert(0, "edge-tts")\nsubprocess.run(cmd)\n'),
        ):
            with self.assertRaises(AssertionError, msg=f"AST zero-API missed cmd.{lbl} edge-tts taint!"):
                self.e2e.oracle_ast_zero_api_and_zero_edge_tts(code, f"bad_{lbl}.py")

    # ------------------------------------------------------------------
    # D7 — Crosstalk self-overlap, Act 5 1.0x gap, duck duration, unregistered/inherited accent
    # ------------------------------------------------------------------
    def test_d7_drama_contract_oracles_crosstalk_act5_duck_duration_and_accent(self) -> None:
        live_variants = self.e2e.load_all_e001_variants()
        live_smap = json.loads((META_DIR / "season1_24ep_map.json").read_text(encoding="utf-8"))

        # Positive: all 4 live variants pass all hardened D7 oracles
        self.e2e.oracle_variant_differentiation_and_crosstalk(live_variants)
        self.e2e.oracle_accent_matrix_budget(self.registry, live_smap, live_variants)
        for cs in live_variants.values():
            self.e2e.oracle_runtime_and_debrief_windows(cs)

        # D7.1: Same-speaker negative-gap crosstalk spoof fails
        mut_vars = {k: copy.deepcopy(v) for k, v in live_variants.items()}
        va = mut_vars["E001_VA"]
        for c in va.cues:
            if c.kind == "dialogue" and float(c.gap_after_s) < 0.0:
                c.gap_after_s = 0.25
        for k in range(10):
            va.cues.insert(
                5 + k,
                TimelineCue(
                    cue_id=f"SELF_SPK_{k}",
                    act_id="act_1",
                    kind="dialogue",
                    role_id="lin_chen",
                    language_code="en",
                    text=f"[measured] Same speaker line {k}.",
                    gap_after_s=-0.15 if k < 9 else 0.3,
                ),
            )
        with self.assertRaises(AssertionError, msg="Same-speaker negative gaps bypassed crosstalk oracle!"):
            self.e2e.oracle_variant_differentiation_and_crosstalk(mut_vars)

        # D7.2: Act 5 shadowing gap decoupled onto 0.8x cues only fails
        va_deb = copy.deepcopy(live_variants["E001_VA"])
        deb_id = self.e2e.get_debrief_act_id(va_deb)
        for c in va_deb.cues:
            if c.act_id == deb_id and c.kind == "dialogue":
                if abs(float(c.playback_rate) - 1.0) < 1e-3:
                    c.gap_after_s = 0.25
                elif abs(float(c.playback_rate) - 0.8) < 1e-3:
                    c.gap_after_s = 2.2
        with self.assertRaises(AssertionError, msg="Act 5 0.8x-only shadow gaps bypassed runtime oracle!"):
            self.e2e.oracle_runtime_and_debrief_windows(va_deb)

        # D7.3: duck_under_next paired duration >55s (~57.7s) caught by estimate_cue_slice_duration_s & viral oracle
        duck_cues: list[TimelineCue] = []
        for k in range(3):
            duck_cues.append(
                TimelineCue(
                    cue_id=f"DK_EN_{k}",
                    act_id="act_2",
                    kind="dialogue",
                    role_id="alistair_finch",
                    language_code="en",
                    text="[measured] " + " ".join(["margin"] * 50),
                    duck_under_next=True,
                    duck_lead_in_s=3.5,
                    duck_gain=0.15,
                    gap_after_s=0.0,
                )
            )
            duck_cues.append(
                TimelineCue(
                    cue_id=f"DK_ZH_{k}",
                    act_id="act_2",
                    kind="dialogue",
                    role_id="lin_chen",
                    language_code="zh",
                    text="[aside] " + "同传拆解渠道压价底线防守" * 3,
                    gap_after_s=0.35,
                )
            )
        est_s = self.e2e.estimate_cue_slice_duration_s(duck_cues)
        self.assertGreater(est_s, 55.0, f"Expected ducked slice > 55s, got {est_s:.2f}s")
        long_vd = EpisodeCueSheet(
            episode_id="E001_VD",
            chapter_number=1,
            title="Long Duck Slice",
            mode="bilingual_business_drama",
            acts=live_variants["E001_VD"].acts,
            cues=duck_cues,
        )
        with self.assertRaises(AssertionError, msg=">55s ducked viral slice bypassed cutlist oracle!"):
            self.e2e.oracle_viral_45s_cutlist_and_rubric(
                [{"variant_id": "E001_VD", "start_cue_id": "DK_EN_0", "end_cue_id": "DK_ZH_2", "has_hook": True, "has_cta": True}],
                {"E001_VD": long_vd},
            )

        # D7.4: Unregistered role & inherited language_code bypasses caught by oracle_accent_matrix_budget
        for bad_lang in ("", "zh-en"):
            va_unreg = copy.deepcopy(live_variants["E001_VA"])
            first_dlg = next(c for c in va_unreg.cues if c.kind == "dialogue")
            first_dlg.role_id = "unregistered_accent_guest"
            first_dlg.language_code = bad_lang
            with self.assertRaises(AssertionError, msg=f"Unregistered role (lang={bad_lang!r}) bypassed accent oracle!"):
                self.e2e.oracle_accent_matrix_budget(self.registry, live_smap, {"E001_VA": va_unreg})

        reg_ext = copy.deepcopy(self.registry)
        reg_ext.roles["custom_sz_en"] = VoiceProfile(
            role_id="custom_sz_en",
            display_name="Custom SZ EN",
            tier="recurring",
            gender="male",
            language_code="en",
            accent_code="zh_mainland_sz",
            voice_id="v_sz_en",
        )
        va_inh = copy.deepcopy(live_variants["E001_VA"])
        first_dlg_inh = next(c for c in va_inh.cues if c.kind == "dialogue")
        first_dlg_inh.role_id = "custom_sz_en"
        first_dlg_inh.language_code = ""
        with self.assertRaises(AssertionError, msg="Inherited EN language on non-US/UK role bypassed accent oracle!"):
            self.e2e.oracle_accent_matrix_budget(reg_ext, live_smap, {"E001_VA": va_inh})

    # ------------------------------------------------------------------
    # D8 — drama_helpers.py linter catches all 5 bypass families
    # ------------------------------------------------------------------
    def test_d8_drama_helpers_linter_catches_all_bypass_mutations(self) -> None:
        # Positive: live --check-only passes with 0 errors
        chk = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "build_e001_variants.py"), "--check-only"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(chk.returncode, 0, f"--check-only failed:\n{chk.stdout}\n{chk.stderr}")
        chk_data = json.loads(chk.stdout)
        self.assertTrue(chk_data.get("ok"))
        self.assertEqual(chk_data.get("error_count"), 0)

        va_path = next(CUE_SHEETS_DIR.glob("E001_VA_*.json"))
        vd_path = next(CUE_SHEETS_DIR.glob("E001_VD_*.json"))
        base_va = EpisodeCueSheet.load(va_path)
        base_vd = EpisodeCueSheet.load(vd_path)
        self.assertEqual(drama_helpers.lint_e001_variant(base_va, self.registry, "E001_VA"), [])
        self.assertEqual(drama_helpers.lint_e001_variant(base_vd, self.registry, "E001_VD"), [])

        # A1a: cross-cue stitch ("phantom" + "number") across two consecutive cues
        m_stitch = copy.deepcopy(base_va)
        for c in m_stitch.cues:
            if c.kind == "dialogue" and "phantom number" in c.text.lower():
                c.text = re.sub(r"phantom\s+number", "phantom", c.text, flags=re.IGNORECASE)
                idx = m_stitch.cues.index(c)
                m_stitch.cues.insert(
                    idx + 1,
                    TimelineCue(
                        cue_id="STITCH_NEXT",
                        act_id=c.act_id,
                        kind="dialogue",
                        role_id="lin_chen",
                        language_code="en",
                        text="[measured] number one priority is cash flow.",
                        gap_after_s=0.3,
                        subtitle_translation="第一优先级是现金流。",
                    ),
                )
                break
        m_st_metrics = drama_helpers.compute_variant_metrics(m_stitch, self.registry)
        self.assertIn("phantom number", m_st_metrics["missing_subphrases"])
        self.assertTrue(drama_helpers.lint_e001_variant(m_stitch, self.registry, "E001_VA"))

        # A1b: substring spoof ("upsidedown" replacing "upside")
        m_sub = copy.deepcopy(base_va)
        for c in m_sub.cues:
            if c.kind == "dialogue" and re.search(r"\bupside\b", c.text, re.IGNORECASE):
                c.text = re.sub(r"\bupside\b", "upsidedown", c.text, flags=re.IGNORECASE)
        m_sub_metrics = drama_helpers.compute_variant_metrics(m_sub, self.registry)
        self.assertIn("upside", m_sub_metrics["missing_subphrases"])

        # A2: banned YouTube / cliché in sheet.title, act.title, inline [tag] (while director_note stays allowed!)
        m_title = copy.deepcopy(base_va)
        m_title.title = "Global Edge YouTube 特别版"
        self.assertTrue(
            any("sheet.title" in e for e in drama_helpers.lint_e001_variant(m_title, self.registry, "E001_VA"))
        )

        m_act = copy.deepcopy(base_va)
        m_act.acts[0].title = "第一幕：视频号开场"
        self.assertTrue(
            any("act.title" in e for e in drama_helpers.lint_e001_variant(m_act, self.registry, "E001_VA"))
        )

        m_tag = copy.deepcopy(base_va)
        dlg0 = next(c for c in m_tag.cues if c.kind == "dialogue")
        dlg0.text = "[youtube] " + dlg0.text
        self.assertTrue(
            any("inline tags" in e for e in drama_helpers.lint_e001_variant(m_tag, self.registry, "E001_VA"))
        )

        # Positive control: director_note guardrail referencing YouTube remains allowed
        m_note = copy.deepcopy(base_va)
        next(c for c in m_note.cues if c.kind == "dialogue").director_note = "严禁出现 YouTube 主播腔"
        self.assertEqual(drama_helpers.lint_e001_variant(m_note, self.registry, "E001_VA"), [])

        # A3: strip ALL Act 5 Chinglish contrast markers
        m_a3 = copy.deepcopy(base_va)
        for c in m_a3.cues:
            if c.act_id == drama_helpers.DEBRIEF_ACT_ID and c.kind == "dialogue":
                for tok in ("直译", "中式", "Chinglish", "chinglish", "别说", "不要说", "菜鸟", "对比"):
                    c.text = c.text.replace(tok, "普通表达")
        errs_a3 = drama_helpers.lint_e001_variant(m_a3, self.registry, "E001_VA")
        self.assertTrue(any("Chinglish" in e for e in errs_a3), f"Expected Chinglish contrast lint error: {errs_a3}")

        # A4: strip ALL NovaEdge / 灵犀 brand mentions
        m_a4 = copy.deepcopy(base_va)
        for c in m_a4.cues:
            if c.kind == "dialogue":
                c.text = re.sub(r"novaedge", "AcmeCorp", c.text, flags=re.IGNORECASE).replace("灵犀", "某公司")
        errs_a4 = drama_helpers.lint_e001_variant(m_a4, self.registry, "E001_VA")
        self.assertTrue(any("NovaEdge" in e for e in errs_a4), f"Expected NovaEdge brand lint error: {errs_a4}")

        # A7: Xianxia tropes (渡劫/飞升/金丹/元婴/炼气/灵根) in ZH dialogue
        for trope in ("渡劫", "飞升", "金丹", "元婴", "炼气", "灵根"):
            m_a7 = copy.deepcopy(base_va)
            zh_cue = next(c for c in m_a7.cues if c.kind == "dialogue" and c.language_code == "zh")
            zh_cue.text = f"[aside] 今晚这场融资宛如{trope}。{zh_cue.text}"
            errs_a7 = drama_helpers.lint_e001_variant(m_a7, self.registry, "E001_VA")
            self.assertTrue(
                any(trope in e for e in errs_a7),
                f"Xianxia trope {trope!r} bypassed drama_helpers linter: {errs_a7}",
            )

        # Malformed duck_under_next checks on E001_VD
        duck_idx = next(i for i, c in enumerate(base_vd.cues) if c.kind == "dialogue" and c.duck_under_next)

        m_drate = copy.deepcopy(base_vd)
        m_drate.cues[duck_idx].playback_rate = 0.8
        self.assertTrue(any("playback_rate=1.0" in e for e in drama_helpers.lint_e001_variant(m_drate, self.registry, "E001_VD")))

        m_dgap = copy.deepcopy(base_vd)
        m_dgap.cues[duck_idx].gap_after_s = 0.5
        self.assertTrue(any("gap_after_s=0.0" in e for e in drama_helpers.lint_e001_variant(m_dgap, self.registry, "E001_VD")))

        m_dact = copy.deepcopy(base_vd)
        m_dact.cues[duck_idx + 1].act_id = "act_4" if m_dact.cues[duck_idx].act_id != "act_4" else "act_3"
        self.assertTrue(any("crosses act boundary" in e for e in drama_helpers.lint_e001_variant(m_dact, self.registry, "E001_VD")))

        m_dzh = copy.deepcopy(base_vd)
        m_dzh.cues[duck_idx].language_code = "zh"
        self.assertTrue(any("must be pure English" in e for e in drama_helpers.lint_e001_variant(m_dzh, self.registry, "E001_VD")))


if __name__ == "__main__":
    unittest.main()
