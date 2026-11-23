"""Comprehensive unit & real-FFmpeg verification suite for Global Edge M5 (E001 Multi-Variant Suite).

Pure stdlib `unittest` + first-party `aigc_audio_pipeline` (zero third-party dependencies,
zero mocks, zero skips, all temporary outputs isolated in `tempfile.TemporaryDirectory()`).
"""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
SCRIPTS_DIR = REPO_ROOT / "projects" / "global_edge" / "scripts"
for _p in (str(SRC_DIR), str(SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from aigc_audio_pipeline.drama3_adapter import (  # noqa: E402
    split_cue_into_subcues_for_drama3,
    translate_cue_to_drama3_input,
)
from aigc_audio_pipeline.models import (  # noqa: E402
    EpisodeCueSheet,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
)
from build_e001_variants import (  # noqa: E402
    OUTPUT_FILENAMES,
    VIRAL_CLIP_RANGES,
    compute_pairwise_distinctiveness,
)
from drama_helpers import (  # noqa: E402
    DEFAULT_LAUNCH_DIR,
    DEFAULT_OUT_DIR,
    DOMAIN,
    GLOBAL_EDGE_ROOT,
    REGISTRY_PATH,
    SHOW_BIBLE_PATH,
    XIANXIA_LEAK_TOKENS,
    compute_variant_metrics,
    estimate_cue_range_duration_s,
    lint_audition_pack,
    lint_e001_variant,
    motif_cue,
)
from ost_and_motifs import (  # noqa: E402
    GLOBAL_EDGE_OST_PROMPTS,
    GLOBAL_EDGE_OST_SPECS,
    GLOBAL_EDGE_SONIC_MOTIFS,
    verify_sync_with_bible_and_registry,
)

BUILD_SCRIPT = SCRIPTS_DIR / "build_e001_variants.py"
RUBRIC_PATH = DEFAULT_OUT_DIR / "E001_COMPARATIVE_EVAL_RUBRIC.md"
LAUNCH_KIT_PATH = DEFAULT_LAUNCH_DIR / "LAUNCH_KIT_AND_E001_45S_CLIPS.md"
MANUAL_PATH = DEFAULT_LAUNCH_DIR / "E001_BILINGUAL_COMPANION_MANUAL.md"
README_PATH = GLOBAL_EDGE_ROOT / "README.md"


def _sub_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{SRC_DIR}:{existing}" if existing else str(SRC_DIR)
    return env


def _parse_srt_timestamp_s(ts: str) -> float:
    hh, mm, rest = ts.strip().split(":")
    ss, ms = rest.split(",")
    return int(hh) * 3600.0 + int(mm) * 60.0 + int(ss) + int(ms) / 1000.0


class TestGlobalEdgeE001Variants(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = VoiceCastingRegistry.load(REGISTRY_PATH)
        cls.committed_sheets: dict[str, EpisodeCueSheet] = {}
        for ep_id, stem in OUTPUT_FILENAMES.items():
            json_path = DEFAULT_OUT_DIR / f"{stem}.json"
            cls.committed_sheets[ep_id] = EpisodeCueSheet.load(json_path)

    def test_01_isolated_rebuild_byte_parity_and_check_only(self) -> None:
        """Rebuilding into a clean TemporaryDirectory must match committed files byte-for-byte."""
        with tempfile.TemporaryDirectory() as td:
            tmp_out = Path(td) / "out"
            proc = subprocess.run(
                [sys.executable, str(BUILD_SCRIPT), "--out-dir", str(tmp_out)],
                cwd=str(REPO_ROOT),
                env=_sub_env(),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=f"build failed:\n{proc.stderr}\n{proc.stdout}")
            report = json.loads(proc.stdout)
            self.assertTrue(report["ok"])
            self.assertEqual(report["error_count"], 0)

            for stem in OUTPUT_FILENAMES.values():
                for ext in (".json", ".md"):
                    rebuilt = (tmp_out / f"{stem}{ext}").read_bytes()
                    committed = (DEFAULT_OUT_DIR / f"{stem}{ext}").read_bytes()
                    self.assertEqual(
                        rebuilt,
                        committed,
                        msg=f"Byte drift detected on {stem}{ext} — re-run build_e001_variants.py",
                    )

            self.assertEqual(
                (tmp_out / "E001_COMPARATIVE_EVAL_RUBRIC.md").read_bytes(),
                RUBRIC_PATH.read_bytes(),
                msg="Byte drift detected on E001_COMPARATIVE_EVAL_RUBRIC.md",
            )

        # --check-only must pass cleanly without writing files
        with tempfile.TemporaryDirectory() as td:
            empty_dir = Path(td) / "should_not_exist"
            chk = subprocess.run(
                [
                    sys.executable,
                    str(BUILD_SCRIPT),
                    "--out-dir",
                    str(empty_dir),
                    "--check-only",
                ],
                cwd=str(REPO_ROOT),
                env=_sub_env(),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(chk.returncode, 0, msg=chk.stderr)
            chk_report = json.loads(chk.stdout)
            self.assertTrue(chk_report["ok"])
            self.assertTrue(chk_report["check_only"])
            self.assertEqual(chk_report["written_files"], [])
            self.assertFalse(empty_dir.exists())

    def test_02_ost_and_sonic_motifs_exact_sync(self) -> None:
        """All 5 OST prompts & 7 sonic_motifs must match SHOW_BIBLE.md and registry verbatim."""
        errs = verify_sync_with_bible_and_registry(self.registry, SHOW_BIBLE_PATH)
        self.assertEqual(errs, [], msg=f"Sync drift: {errs}")
        self.assertEqual(len(GLOBAL_EDGE_OST_PROMPTS), 5)
        self.assertEqual(len(GLOBAL_EDGE_OST_SPECS), 5)
        self.assertEqual(len(GLOBAL_EDGE_SONIC_MOTIFS), 7)
        for key, prompt in GLOBAL_EDGE_OST_PROMPTS.items():
            self.assertTrue(prompt.endswith("purely instrumental"), msg=f"{key} ending drifted")
            self.assertIn("no vocals", prompt)
            self.assertIn("no singing", prompt)
        for mid, m in GLOBAL_EDGE_SONIC_MOTIFS.items():
            self.assertTrue(
                str(m["sfx_prompt"]).endswith(", pure foley, no human voice"),
                msg=f"{mid} foley ending drifted",
            )
            self.assertFalse(m["loop"])

    def test_03_schema_validation_and_zero_xianxia_drama3_preview(self) -> None:
        """All 5 cue sheets must pass strict validation and emit 0 Xianxia leaks in Drama 3 preview."""
        for ep_id, sheet in self.committed_sheets.items():
            schema_errs = sheet.validate(registry=self.registry, require_locked_voices=True)
            self.assertEqual(schema_errs, [], msg=f"{ep_id} schema errors: {schema_errs}")

            for cue in sheet.cues:
                if cue.kind != "dialogue":
                    continue
                prof = self.registry.resolve_role(cue.role_id)
                for attempt in (1, 2):
                    rendered = translate_cue_to_drama3_input(
                        cue, prof, attempt=attempt, domain=DOMAIN
                    )
                    for bad_tok in XIANXIA_LEAK_TOKENS:
                        self.assertNotIn(
                            bad_tok,
                            rendered,
                            msg=f"{ep_id}:{cue.cue_id} attempt={attempt} leaked {bad_tok!r}",
                        )
                if cue.duck_under_next:
                    subcues = split_cue_into_subcues_for_drama3(cue, domain=DOMAIN)
                    self.assertEqual(
                        len(subcues),
                        1,
                        msg=f"{ep_id}:{cue.cue_id} duck_under_next cue must not auto-split",
                    )

            # Subprocess CLI preview-drama3 with --registry
            json_path = DEFAULT_OUT_DIR / f"{OUTPUT_FILENAMES[ep_id]}.json"
            prev = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "aigc_audio_pipeline.cli",
                    "preview-drama3",
                    "--registry",
                    str(REGISTRY_PATH),
                    "--cue-sheet",
                    str(json_path),
                    "--limit",
                    "15",
                ],
                cwd=str(REPO_ROOT),
                env=_sub_env(),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(prev.returncode, 0, msg=f"preview-drama3 failed for {ep_id}: {prev.stderr}")
            for bad_tok in XIANXIA_LEAK_TOKENS:
                self.assertNotIn(bad_tok, prev.stdout, msg=f"CLI preview leaked {bad_tok!r} in {ep_id}")

    def test_04_audition_pack_and_e001_shared_invariants(self) -> None:
        """AUDITION_GLOBAL_EDGE and all 4 E001 variants must pass 100% of automated lint gates."""
        aud_errs = lint_audition_pack(self.committed_sheets["AUDITION_GLOBAL_EDGE"], self.registry)
        self.assertEqual(aud_errs, [], msg=f"Audition lint errors: {aud_errs}")

        for vid in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
            sheet = self.committed_sheets[vid]
            errs = lint_e001_variant(sheet, self.registry, vid)
            self.assertEqual(errs, [], msg=f"{vid} lint errors: {errs}")
            m = compute_variant_metrics(sheet, self.registry)
            self.assertEqual(m["mandatory_phrase_groups_hit"], 8)
            self.assertEqual(m["missing_subphrases"], [])
            self.assertEqual(m["core_us_uk_en_pct"], 100.0)
            self.assertEqual(m["banned_cliche_count"], 0)
            self.assertEqual(m["xianxia_drama3_leak_count"], 0)

    def test_05_runtime_budgets_and_act5_shadowing(self) -> None:
        """All 4 variants must sit strictly inside empirical & synth runtime windows + Act 5 shadowing."""
        for vid in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
            m = compute_variant_metrics(self.committed_sheets[vid], self.registry)
            self.assertGreaterEqual(m["total_duration_est_s"], 600.0, vid)
            self.assertLessEqual(m["total_duration_est_s"], 840.0, vid)
            self.assertGreaterEqual(m["drama_duration_est_s"], 480.0, vid)
            self.assertLessEqual(m["drama_duration_est_s"], 600.0, vid)
            self.assertGreaterEqual(m["debrief_duration_est_s"], 165.0, vid)
            self.assertLessEqual(m["debrief_duration_est_s"], 210.0, vid)
            self.assertGreaterEqual(m["synth_drama_duration_est_s"], 480.0, vid)
            self.assertGreaterEqual(m["synth_debrief_duration_est_s"], 165.0, vid)
            self.assertGreaterEqual(m["act5_slow_count"], 3, vid)
            self.assertGreaterEqual(m["act5_shadow_gap_2s_count"], 3, vid)

    def test_06_variant_structural_differentiation_and_anti_cloning(self) -> None:
        """All 4 variants must differ genuinely in structure, bilingual ratio, and written dialogue."""
        variants = {k: self.committed_sheets[k] for k in ("E001_VA", "E001_VB", "E001_VC", "E001_VD")}
        m_va = compute_variant_metrics(variants["E001_VA"], self.registry)
        m_vb = compute_variant_metrics(variants["E001_VB"], self.registry)
        m_vc = compute_variant_metrics(variants["E001_VC"], self.registry)
        m_vd = compute_variant_metrics(variants["E001_VD"], self.registry)

        # VA: pure HBO duel
        self.assertEqual(m_va["inner_monologue_count"], 0)
        self.assertGreaterEqual(m_va["crosstalk_count"], 6)
        self.assertTrue(0.65 <= m_va["drama_en_ratio"] <= 0.75)
        self.assertEqual(m_va["act5_roles"], ["lin_chen"])

        # VB: House-of-Cards freeze-frame sniper
        self.assertGreaterEqual(m_vb["inner_monologue_count"], 6)
        self.assertGreaterEqual(m_vb["crosstalk_count"], 4)
        self.assertTrue(0.50 <= m_vb["drama_en_ratio"] <= 0.60)
        self.assertTrue({"lin_chen", "zhou_mo"}.issubset(set(m_vb["act5_roles"])))

        # VC: 3-timezone thriller + antagonist roleplay
        self.assertEqual(m_vc["inner_monologue_count"], 0)
        self.assertGreaterEqual(m_vc["phone_call_count"], 4)
        self.assertGreaterEqual(m_vc["sfx_cues"], 13)
        self.assertGreaterEqual(m_vc["crosstalk_count"], 6)
        self.assertTrue(0.55 <= m_vc["drama_en_ratio"] <= 0.65)
        self.assertTrue(
            bool({"victoria_vance", "alistair_finch"} & set(m_vc["act5_roles"])),
            msg="VC Act 5 must include antagonist cold-call roleplay",
        )

        # VD: documentary simultaneous translation ducking + E002 teaser
        self.assertGreaterEqual(m_vd["duck_under_next_count"], 2)
        self.assertGreaterEqual(m_vd["crosstalk_count"], 3)
        self.assertTrue(0.50 <= m_vd["drama_en_ratio"] <= 0.60)
        self.assertGreaterEqual(m_vd["studio_warm_drama_count"], 3)

        # Anti-cloning pairwise distinctiveness across all 6 variant pairs
        sim = compute_pairwise_distinctiveness(variants)
        self.assertEqual(len(sim), 6)
        for pair_key, jaccard in sim.items():
            self.assertLess(
                jaccard,
                0.15,
                msg=f"Variants too similar ({pair_key}: Jaccard={jaccard})",
            )

    def test_07_live_ffmpeg_three_bus_mastering_atempo_and_bilingual_srt(self) -> None:
        """Real FFmpeg synth-dry-test on AUDITION_GLOBAL_EDGE must verify 48kHz stereo, 0.80x stretch & SRT."""
        aud_json = DEFAULT_OUT_DIR / f"{OUTPUT_FILENAMES['AUDITION_GLOBAL_EDGE']}.json"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "audition_master"
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "aigc_audio_pipeline.cli",
                    "synth-dry-test",
                    "--registry",
                    str(REGISTRY_PATH),
                    "--cue-sheet",
                    str(aud_json),
                    "--output-dir",
                    str(out_dir),
                ],
                cwd=str(REPO_ROOT),
                env=_sub_env(),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=f"synth-dry-test failed:\n{proc.stderr}\n{proc.stdout}")
            res = json.loads(proc.stdout)
            self.assertTrue(res["dry_test_passed"])

            master_wav = Path(res["master_wav"])
            master_mp3 = Path(res["master_mp3"])
            srt_path = Path(res["subtitles_srt"])
            manifest_path = Path(res["manifest_json"])
            for p in (master_wav, master_mp3, srt_path, manifest_path):
                self.assertTrue(p.exists() and p.stat().st_size > 0, msg=f"Missing/empty output {p}")

            # Verify real 48kHz stereo via ffprobe on both WAV and MP3
            for audio_file in (master_wav, master_mp3):
                probe = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "error",
                        "-select_streams",
                        "a:0",
                        "-show_entries",
                        "stream=sample_rate,channels",
                        "-of",
                        "json",
                        str(audio_file),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                stream = json.loads(probe.stdout)["streams"][0]
                self.assertEqual(int(stream["sample_rate"]), 48000, msg=str(audio_file))
                self.assertEqual(int(stream["channels"]), 2, msg=str(audio_file))

            # Verify 0.80x tempo stretch ratio (~1.25x) between aud_014 (0.8x) and aud_015 (1.0x)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            by_id = {item["cue_id"]: item for item in manifest["timeline"]}
            dur_slow = float(by_id["aud_014"]["duration_s"])
            dur_native = float(by_id["aud_015"]["duration_s"])
            ratio = dur_slow / dur_native
            self.assertGreater(ratio, 1.18, msg=f"0.80x stretch too small: {dur_slow}/{dur_native}={ratio:.3f}")
            self.assertLess(ratio, 1.32, msg=f"0.80x stretch too large: {dur_slow}/{dur_native}={ratio:.3f}")

            # Verify zero overlapping .srt timestamps + bilingual EN/ZH lines + ducked EN: block
            srt_text = srt_path.read_text(encoding="utf-8")
            blocks = [b.strip() for b in re.split(r"\n\s*\n", srt_text) if b.strip()]
            self.assertGreaterEqual(len(blocks), 10)
            prev_end = -1.0
            has_dual_line_gloss = False
            has_ducked_en_line = False
            for block in blocks:
                blines = block.splitlines()
                self.assertGreaterEqual(len(blines), 3, msg=f"Malformed SRT block: {block!r}")
                t_start_str, t_end_str = blines[1].split("-->")
                t_start = _parse_srt_timestamp_s(t_start_str)
                t_end = _parse_srt_timestamp_s(t_end_str)
                self.assertGreater(t_end, t_start, msg=f"Non-positive SRT block: {block!r}")
                self.assertGreaterEqual(
                    t_start,
                    prev_end,
                    msg=f"Overlapping SRT timestamps: prev_end={prev_end} > start={t_start}",
                )
                prev_end = t_end
                text_lines = blines[2:]
                if len(text_lines) >= 2:
                    has_dual_line_gloss = True
                    if any(ln.startswith("EN:") for ln in text_lines):
                        has_ducked_en_line = True

            self.assertTrue(has_dual_line_gloss, msg="SRT missing dual-line EN/ZH subtitle_translation")
            self.assertTrue(has_ducked_en_line, msg="SRT missing duck_under_next bilingual EN: line")

    def test_08_docs_clip_cutlists_rubric_manual_and_readme_integrity(self) -> None:
        """Verify Launch Kit 45s clips, Rubric 100-pt sum + live parity, Companion Manual, and README."""
        # 1. Launch Kit 45s clips
        launch_text = LAUNCH_KIT_PATH.read_text(encoding="utf-8")
        self.assertIn("[语料实证]", launch_text)
        self.assertIn("[行业基准与测算模型]", launch_text)

        clip_matches = re.findall(
            r"- \*\*Variant\*\*: `(E001_V[A-D])`\s*\n"
            r"- \*\*Cue Range\*\*: `([a-z0-9_]+)` \.\. `([a-z0-9_]+)`\s*\n"
            r"- \*\*Estimated Duration\*\*: `([0-9.]+)s`",
            launch_text,
        )
        self.assertEqual(len(clip_matches), 4, msg=f"Expected 4 clip cutlists, found {clip_matches}")
        seen_variants = set()
        for vid, start_id, end_id, doc_dur_str in clip_matches:
            seen_variants.add(vid)
            self.assertEqual((start_id, end_id), VIRAL_CLIP_RANGES[vid])
            live_dur = estimate_cue_range_duration_s(self.committed_sheets[vid], start_id, end_id)
            self.assertAlmostEqual(live_dur, float(doc_dur_str), delta=0.05)
            self.assertGreaterEqual(live_dur, 38.0)
            self.assertLessEqual(live_dur, 55.0)
        self.assertEqual(seen_variants, {"E001_VA", "E001_VB", "E001_VC", "E001_VD"})

        # 2. Comparative Evaluation Rubric: live metric parity + 100-point sum + Track 1-4
        rubric_text = RUBRIC_PATH.read_text(encoding="utf-8")
        dim_weights = [
            int(w)
            for w in re.findall(r"\| \*\*D[1-7]\*\* \| [^|]+ \| \*\*(\d+)\*\* \|", rubric_text)
        ]
        self.assertEqual(len(dim_weights), 7, msg=f"Expected 7 rubric dimensions, got {dim_weights}")
        self.assertEqual(sum(dim_weights), 100, msg=f"Rubric weights sum={sum(dim_weights)} != 100")
        for tok in ("Track 1", "Track 2", "Track 3", "Track 4", "Hybrid-Winner"):
            self.assertIn(tok, rubric_text)
        for vid in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
            m = compute_variant_metrics(self.committed_sheets[vid], self.registry)
            self.assertIn(f"`{m['total_duration_est_s']}s`", rubric_text)
            self.assertIn(f"`{m['drama_duration_est_s']}s`", rubric_text)
            self.assertIn(f"`{m['debrief_duration_est_s']}s`", rubric_text)

        # 3. Bilingual Companion Manual: all 8 groups, 13 mandatory + 5 bonus LEX IDs, 5 seed clips, accurate speakers
        manual_text = MANUAL_PATH.read_text(encoding="utf-8")
        for lex_id in (
            "LEX_025", "LEX_026", "LEX_027", "LEX_028",
            "LEX_049", "LEX_001", "LEX_002",
            "LEX_050", "LEX_003", "LEX_004", "LEX_051",
            "LEX_029", "LEX_030",
            "LEX_008", "LEX_031", "LEX_032", "LEX_052", "LEX_053",
        ):
            self.assertIn(lex_id, manual_text, msg=f"Companion manual missing {lex_id}")
        for clip_id in ("02_BIZ_Anthropic", "012_AI", "039_BIZ", "090_USC", "059_FIN"):
            self.assertIn(clip_id, manual_text, msg=f"Companion manual missing seed {clip_id}")
        self.assertIn("All-In Podcast (Hosts)", manual_text)
        self.assertIn("The Swedish Investor (Narrator)", manual_text)
        self.assertNotIn("Dario Amodei", manual_text)
        self.assertIn("不属于 `059_FIN`", manual_text)

        # Build lookup across all 4 committed E001 variant JSONs
        cue_by_id = {}
        variant_by_cue_id = {}
        for vid in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
            for c in self.committed_sheets[vid].cues:
                cue_by_id[c.cue_id] = c
                variant_by_cue_id[c.cue_id] = vid

        # Verify ALL 8 cited drama excerpts match their JSON cue verbatim
        excerpt_matches = re.findall(
            r"- \*\*E001 剧本原声摘录（`(E001_V[A-D])` · `([a-z0-9_]+)` · `([a-z0-9_]+)`）\*\*：\s*\n"
            r'  > "([^"]+)"',
            manual_text,
        )
        self.assertEqual(len(excerpt_matches), 8, msg=f"Expected 8 drama excerpts, got {len(excerpt_matches)}")
        for vid, cid, role_id, quoted_md in excerpt_matches:
            self.assertIn(cid, cue_by_id, msg=f"Drama excerpt cue {cid} missing from JSONs")
            self.assertEqual(variant_by_cue_id[cid], vid)
            cue = cue_by_id[cid]
            self.assertEqual(cue.role_id, role_id)
            _, spoken = extract_tags_and_spoken_text(cue.text)
            plain_quote = quoted_md.replace("**", "")
            self.assertEqual(
                plain_quote,
                spoken,
                msg=f"Drama excerpt mismatch for {vid}:{cid}",
            )

        # Verify ALL 7 cited Act 5 0.80x -> 1.0x shadowing cue pairs match JSON verbatim + rate/gap invariants
        shadow_pair_matches = re.findall(
            r"- \*\*`0\.80x -> 1\.0x` 跟读训练（对应 `([a-z0-9_]+)`/`([a-z0-9_]+)`[^）]*）\*\*：\s*\n"
            r"  - `0\.80x` [^：]+：`([^`]+)`",
            manual_text,
        )
        self.assertEqual(
            len(shadow_pair_matches),
            7,
            msg=f"Expected 7 Act 5 shadowing cue pairs, got {len(shadow_pair_matches)}",
        )
        for slow_id, native_id, quoted_text in shadow_pair_matches:
            self.assertIn(slow_id, cue_by_id, msg=f"Shadow slow cue {slow_id} missing")
            self.assertIn(native_id, cue_by_id, msg=f"Shadow native cue {native_id} missing")
            self.assertEqual(variant_by_cue_id[slow_id], variant_by_cue_id[native_id])
            slow_cue = cue_by_id[slow_id]
            native_cue = cue_by_id[native_id]
            self.assertEqual(slow_cue.act_id, "act5", msg=f"{slow_id} not in act5")
            self.assertEqual(native_cue.act_id, "act5", msg=f"{native_id} not in act5")
            self.assertAlmostEqual(float(slow_cue.playback_rate), 0.8, places=6, msg=slow_id)
            self.assertAlmostEqual(float(native_cue.playback_rate), 1.0, places=6, msg=native_id)
            self.assertGreaterEqual(float(native_cue.gap_after_s), 2.0, msg=native_id)
            self.assertEqual(
                quoted_text,
                extract_tags_and_spoken_text(slow_cue.text)[1],
                msg=f"Shadow slow quote mismatch for {slow_id}",
            )
            self.assertEqual(
                quoted_text,
                extract_tags_and_spoken_text(native_cue.text)[1],
                msg=f"Shadow native quote mismatch for {native_id}",
            )

        # Verify Group 3 extension shadowing quote traces verbatim to vd_010
        ext_shadow_matches = re.findall(
            r"- \*\*`0\.80x -> 1\.0x` 跟读训练（延伸跟读，原句见 `([a-z0-9_]+)`）\*\*：\s*\n"
            r"  - `0\.80x` [^：]+：`([^`]+)`",
            manual_text,
        )
        self.assertEqual(len(ext_shadow_matches), 1, msg=f"Expected 1 extension drill, got {ext_shadow_matches}")
        ext_cid, ext_quote = ext_shadow_matches[0]
        self.assertIn(ext_cid, cue_by_id)
        self.assertIn(ext_quote, extract_tags_and_spoken_text(cue_by_id[ext_cid].text)[1])

        # Verify ALL 5 bonus table cue references exist and contain the cited phrase
        bonus_rows = re.findall(
            r"\| \*\*`(LEX_\d+)`\*\* \| \*\*`([^`]+)`\*\*[^|]*\|[^|]*\|[^|]*（见 `([a-z0-9_]+)` / `([a-z0-9_]+)`） \|",
            manual_text,
        )
        self.assertEqual(len(bonus_rows), 5, msg=f"Expected 5 bonus cue rows, got {bonus_rows}")
        for lex_id, phrase, cid_a, cid_b in bonus_rows:
            for cid in (cid_a, cid_b):
                self.assertIn(cid, cue_by_id, msg=f"Bonus {lex_id} cue {cid} missing")
                spoken_low = extract_tags_and_spoken_text(cue_by_id[cid].text)[1].lower()
                self.assertIn(
                    phrase.lower(),
                    spoken_low,
                    msg=f"Bonus {lex_id} phrase {phrase!r} not found in {cid}",
                )

        # 4. README canonical commands & runnable Colab 96GB anchor chaining flags
        readme_text = README_PATH.read_text(encoding="utf-8")
        for expected_cmd in (
            "build_e001_variants.py",
            "cli validate",
            "cli preview-drama3",
            "cli synth-dry-test",
            "prepare_global_edge_voice_anchors.py",
            "export_drama3_bundle.py",
            "launch_g4_global_edge_drama3.py",
            "AUDITION,E001_VARIANTS",
            "test_global_edge_e001_variants.py",
        ):
            self.assertIn(expected_cmd, readme_text, msg=f"README missing {expected_cmd!r}")
        self.assertRegex(
            readme_text,
            r"prepare_global_edge_voice_anchors\.py[^\n]*(?:\\\n[^\n]*)*--output-dir\s+\S+",
            msg="README §5 must pass --output-dir to prepare_global_edge_voice_anchors.py",
        )
        self.assertRegex(
            readme_text,
            r"export_drama3_bundle\.py[^\n]*(?:\\\n[^\n]*)*--anchors-dir\s+\S+",
            msg="README §5 must pass --anchors-dir to export_drama3_bundle.py",
        )

    def test_09_same_speaker_overlap_and_subtitle_leak_linter_guards(self) -> None:
        """Linter must reject same-speaker negative-gap overlap, same-speaker [interrupting], and subtitle leaks."""
        base_vd = self.committed_sheets["E001_VD"]
        base_metrics = compute_variant_metrics(base_vd, self.registry)
        self.assertEqual(lint_e001_variant(base_vd, self.registry, "E001_VD"), [])

        # 1. Adjacent same-speaker negative-gap self-overlap (vd_022 -> vd_023, both victoria_vance)
        mut_overlap = copy.deepcopy(base_vd)
        by_id = {c.cue_id: c for c in mut_overlap.cues}
        by_id["vd_022"].gap_after_s = -0.15
        errs_overlap = lint_e001_variant(mut_overlap, self.registry, "E001_VD")
        self.assertTrue(
            any("same-speaker negative-gap self-overlap" in e and "vd_022" in e for e in errs_overlap),
            msg=f"Expected same-speaker negative-gap error, got: {errs_overlap}",
        )
        # Same-speaker negative gap must NOT inflate crosstalk_count
        mut_metrics = compute_variant_metrics(mut_overlap, self.registry)
        self.assertEqual(mut_metrics["crosstalk_count"], base_metrics["crosstalk_count"])

        # 2. Same-speaker negative-gap bridged by an overlay_next SFX must also be rejected
        mut_bridged = copy.deepcopy(base_vd)
        idx_22 = next(i for i, c in enumerate(mut_bridged.cues) if c.cue_id == "vd_022")
        mut_bridged.cues[idx_22].gap_after_s = -0.15
        mut_bridged.cues.insert(
            idx_22 + 1,
            motif_cue(
                "vd_022_bridge_sfx",
                "act2",
                "smart_glasses_haptic_ping",
                placement="overlay_next",
                gap_after_s=0.0,
            ),
        )
        errs_bridged = lint_e001_variant(mut_bridged, self.registry, "E001_VD")
        self.assertTrue(
            any("same-speaker negative-gap self-overlap" in e and "vd_022" in e for e in errs_bridged),
            msg=f"Expected bridged same-speaker negative-gap error, got: {errs_bridged}",
        )

        # 3. Same-speaker [interrupting] self-interruption (vd_023 following vd_022)
        mut_int = copy.deepcopy(base_vd)
        by_id_int = {c.cue_id: c for c in mut_int.cues}
        by_id_int["vd_023"].text = "[interrupting] " + by_id_int["vd_023"].text
        errs_int = lint_e001_variant(mut_int, self.registry, "E001_VD")
        self.assertTrue(
            any("same-speaker [interrupting]" in e and "vd_023" in e for e in errs_int),
            msg=f"Expected same-speaker [interrupting] error, got: {errs_int}",
        )

        # 4. Banned external-source leak inside subtitle_translation must be caught
        mut_sub = copy.deepcopy(base_vd)
        by_id_sub = {c.cue_id: c for c in mut_sub.cues}
        by_id_sub["vd_007"].subtitle_translation += "（详见 YouTube 切片）"
        errs_sub = lint_e001_variant(mut_sub, self.registry, "E001_VD")
        self.assertTrue(
            any("subtitle_translation" in e and "youtube" in e for e in errs_sub),
            msg=f"Expected subtitle_translation leak error, got: {errs_sub}",
        )
        self.assertGreater(
            compute_variant_metrics(mut_sub, self.registry)["banned_cliche_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
