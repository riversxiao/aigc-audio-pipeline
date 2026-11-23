"""Comprehensive unit tests for Global Edge Milestone M2 (100-clip corpus ETL,
executive lexicon, programmatic intelligence report, and 5-pillar research report).

Pure Python stdlib `unittest` using `tempfile.TemporaryDirectory()` exclusively.
"""

from __future__ import annotations

import copy
import json
import os
import random
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "projects" / "global_edge" / "scripts" / "extract_100_clips_corpus.py"
CORPUS_DIR = REPO_ROOT / "projects" / "global_edge" / "01_视频号语料与商业词库"
CORPUS_JSON_PATH = CORPUS_DIR / "corpus_100_structured.json"
LEXICON_JSON_PATH = CORPUS_DIR / "executive_lexicon.json"
CORPUS_REPORT_PATH = CORPUS_DIR / "CORPUS_INTELLIGENCE_REPORT.md"
RESEARCH_REPORT_PATH = (
    REPO_ROOT
    / "projects"
    / "global_edge"
    / "00_节目圣经与第一季24集总纲"
    / "RESEARCH_REPORT.md"
)
RAW_SOURCE_PATH = Path("/tmp/arsenal_100_queue.json")


class TestGlobalEdgeCorpusM2(unittest.TestCase):
    """End-to-end verification of M2 corpus ETL, lexicon provenance, and reports."""

    @classmethod
    def setUpClass(cls) -> None:
        if not RAW_SOURCE_PATH.exists():
            raise AssertionError(f"Canonical source file missing at {RAW_SOURCE_PATH}")
        cls.raw_records = json.loads(RAW_SOURCE_PATH.read_text(encoding="utf-8"))
        cls.corpus = json.loads(CORPUS_JSON_PATH.read_text(encoding="utf-8"))
        cls.lexicon = json.loads(LEXICON_JSON_PATH.read_text(encoding="utf-8"))
        cls.clips_by_id = {c["clip_id"]: c for c in cls.corpus["clips"]}

    def _run_etl(
        self,
        *extra_args: str,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *extra_args],
            cwd=str(cwd if cwd is not None else REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    # ------------------------------------------------------------------
    # Test 1: Byte-exact determinism (--out-dir & --output-dir & --check-only)
    # ------------------------------------------------------------------
    def test_etl_cli_determinism_and_committed_parity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out1 = Path(td) / "run1"
            out2 = Path(td) / "run2"
            out_check = Path(td) / "check_only_dir"

            proc1 = self._run_etl(
                "--source",
                str(RAW_SOURCE_PATH),
                "--out-dir",
                str(out1),
            )
            self.assertEqual(proc1.returncode, 0, msg=proc1.stderr)

            proc2 = self._run_etl(
                "--source",
                str(RAW_SOURCE_PATH),
                "--output-dir",
                str(out2),
            )
            self.assertEqual(proc2.returncode, 0, msg=proc2.stderr)

            proc_check = self._run_etl(
                "--source",
                str(RAW_SOURCE_PATH),
                "--out-dir",
                str(out_check),
                "--check-only",
            )
            self.assertEqual(proc_check.returncode, 0, msg=proc_check.stderr)
            self.assertFalse(
                out_check.exists(),
                "--check-only must not create output directory or files",
            )

            for fname in (
                "corpus_100_structured.json",
                "executive_lexicon.json",
                "CORPUS_INTELLIGENCE_REPORT.md",
            ):
                b1 = (out1 / fname).read_bytes()
                b2 = (out2 / fname).read_bytes()
                b_committed = (CORPUS_DIR / fname).read_bytes()
                self.assertEqual(b1, b2, f"Non-deterministic output across runs for {fname}")
                self.assertEqual(
                    b1,
                    b_committed,
                    f"Committed artifact {fname} drifted from fresh ETL run",
                )

    # ------------------------------------------------------------------
    # Test 2: Schema, exact metrics, strict monotonicity, prefix collisions
    # ------------------------------------------------------------------
    def test_corpus_schema_metrics_and_prefix_collision_survival(self) -> None:
        required_top = {
            "schema_version",
            "source_file",
            "source_sha256",
            "source_gdrive_file_id",
            "total_clips",
            "topic_counts",
            "summary_metrics",
            "asr_corrections_applied",
            "data_quality_audit",
            "clips",
        }
        self.assertTrue(required_top.issubset(self.corpus.keys()))

        self.assertEqual(self.corpus["total_clips"], 100)
        self.assertEqual(len(self.corpus["clips"]), 100)
        self.assertEqual(len(self.clips_by_id), 100)
        self.assertEqual(
            self.corpus["topic_counts"],
            {"AI": 25, "BUSINESS": 25, "FINANCE": 25, "US_CHINA": 25},
        )

        sm = self.corpus["summary_metrics"]
        self.assertEqual(sm["total_segments"], 1408)
        self.assertEqual(
            sum(len(c["subtitles_clean"]) for c in self.corpus["clips"]),
            1408,
        )
        self.assertEqual(sm["total_zh_chars"], 27095)
        self.assertEqual(sm["total_en_words"], 14409)
        self.assertEqual(sm["total_en_words_ws"], 14379)
        self.assertEqual(sm["raw_total_en_words"], 14420)
        self.assertEqual(sm["raw_total_en_words_ws"], 14392)
        self.assertEqual(sm["unique_channels"], 64)
        self.assertEqual(sm["published_count"], 9)
        self.assertEqual(sm["queued_count"], 91)
        self.assertAlmostEqual(sm["total_duration_sec"], 4976.89, places=2)
        self.assertAlmostEqual(sm["median_wpm"], 170.34, places=2)
        self.assertAlmostEqual(sm["raw_median_wpm"], 170.20, places=2)
        self.assertAlmostEqual(sm["mean_wpm"], 173.72, places=2)
        self.assertAlmostEqual(sm["raw_mean_wpm"], 173.86, places=2)
        self.assertAlmostEqual(sm["raw_p25_wpm"], 154.24, places=2)
        self.assertAlmostEqual(sm["raw_p75_wpm"], 194.86, places=2)
        self.assertAlmostEqual(sm["raw_min_wpm"], 125.31, places=2)
        self.assertAlmostEqual(sm["raw_max_wpm"], 227.45, places=2)
        self.assertAlmostEqual(sm["p25_wpm"], 154.24, places=2)
        self.assertAlmostEqual(sm["p75_wpm"], 194.46, places=2)

        required_clip_keys = {
            "clip_id",
            "topic_key",
            "topic_label",
            "video_id",
            "video_title",
            "channel",
            "inferred_speakers",
            "duration_sec",
            "wpm",
            "virality_score",
            "hook_line_1",
            "hook_line_2",
            "en_title_hook",
            "summary_zh",
            "en_raw",
            "en_clean",
            "zh_full",
            "subtitles_clean",
        }
        for c in self.corpus["clips"]:
            self.assertEqual(set(c.keys()), required_clip_keys)
            subs = c["subtitles_clean"]
            self.assertGreater(len(subs), 0)
            for idx, seg in enumerate(subs):
                self.assertGreater(
                    seg["end_sec"],
                    seg["start_sec"],
                    f"Non-positive duration in {c['clip_id']}[{idx}]",
                )
                if idx > 0:
                    self.assertGreaterEqual(
                        seg["start_sec"],
                        subs[idx - 1]["end_sec"],
                        f"Overlap remains in {c['clip_id']}[{idx - 1}->{idx}]",
                    )

        dqa = self.corpus["data_quality_audit"]
        self.assertEqual(dqa["subtitle_overlaps_repaired_count"], 36)
        self.assertEqual(dqa["subtitle_overlaps_repaired_clips_count"], 24)
        self.assertEqual(dqa["missing_numeric_prefixes"], ["028", "046"])

        # Prefix collision survival (030_AI / 030_BIZ and 054_BIZ / 054_FIN)
        for cid in ("030_AI", "030_BIZ", "054_BIZ", "054_FIN"):
            self.assertIn(cid, self.clips_by_id)
        self.assertEqual(self.clips_by_id["030_AI"]["topic_key"], "AI")
        self.assertEqual(self.clips_by_id["030_BIZ"]["topic_key"], "BUSINESS")
        self.assertNotEqual(
            self.clips_by_id["030_AI"]["video_id"],
            self.clips_by_id["030_BIZ"]["video_id"],
        )
        self.assertEqual(self.clips_by_id["054_BIZ"]["topic_key"], "BUSINESS")
        self.assertEqual(self.clips_by_id["054_FIN"]["topic_key"], "FINANCE")
        self.assertNotEqual(
            self.clips_by_id["054_BIZ"]["video_id"],
            self.clips_by_id["054_FIN"]["video_id"],
        )

    # ------------------------------------------------------------------
    # Test 3: All 85 ASR rules applied cleanly while en_raw stays untouched
    # ------------------------------------------------------------------
    def test_all_asr_corrections_applied_while_en_raw_untouched(self) -> None:
        fixes = self.corpus["asr_corrections_applied"]
        dqa = self.corpus["data_quality_audit"]
        self.assertEqual(dqa["asr_rules_defined"], 85)
        self.assertEqual(dqa["asr_rules_fired"], 85)
        self.assertEqual(len(fixes), 98)
        self.assertEqual(dqa["asr_clips_modified_count"], 47)

        for fix in fixes:
            self.assertTrue({"clip_id", "seg_idx", "raw", "clean", "reason"}.issubset(fix.keys()))
            self.assertIn(fix["clip_id"], self.clips_by_id)

        # Verify all core + key extended fixes in en_clean and absence of raw typos
        expected_present_absent: list[tuple[str, list[str], list[str]]] = [
            ("010_AI", ["like $5 trillion"], ["like5 trillion"]),
            ("014_AI", ["Hammurabi"], ["Hammarabi"]),
            ("015_AI", ["Grok 3", "Claude", "programming language"], ["grock 3", "Claudee", "programming l language"]),
            ("018_AI", ["1,024 tokens", "project called llm.c."], ["1,24 tokens", "project called lm."]),
            ("021_AI", ["Abilene"], ["Abene"]),
            ("031_BIZ", ["these mats", "Dilbert cartoon", "fiberglass mats"], ["these Ms", "dber cartoon", "five glass mats"]),
            ("037_BIZ", ["Meta AI be", "405 billion parameters"], ["met AI be", "45 billion parameters"]),
            ("038_BIZ", ["Thiel"], ["Teal"]),
            ("039_BIZ", ["SaaS software"], ["SAS software"]),
            ("045_BIZ", ["Palantir", "Palantir's", "Shyam Sankar"], ["Palanteer", "Palunteers", "Sham Sankar"]),
            ("050_BIZ", ["R&D spend"], ["r d v span"]),
            ("051_BIZ", ["GPT-4"], ["gp4"]),
            ("054_BIZ", ["totally shelved", "crewed mission"], ["totally shelf", "crude mission"]),
            ("055_FIN", ["for Druckenmiller he got out", "Druckenmiller", "Soros", "to cut losses"], ["truckee", "drucker miller", "sorrows", "to colossus"]),
            ("063_FIN", ["(or DCF)", "we've"], ["we\u2019ve"]),
            ("064_FIN", ["tight money soon", "easy money soon"], ["tight money suit", "easy money suit"]),
            ("069_FIN", ["law of holes", "cut in half"], ["law of holds", "caught in half"]),
            ("070_FIN", ["torrid rate", "a trillion and change"], ["tor rate", "a trillion change"]),
            ("073_FIN", ["is a catastrophe"], ["cast robbery"]),
            ("079_USC", ["former Google CEO Eric Schmidt", "OpenAI's moat really is", "ChatGPT", "Anthropic's Claude"], ["chat gbt", "anthropics"]),
            ("082_USC", ["one tiny flaw", "Tainan Science Park", "cutting-edge"], ["one tiny floor", "Tynan Science Park", "cuttingedge"]),
            ("085_USC", ["Zhejiang"], ["chakyang"]),
            ("086_USC", ["kinds of supply chain"], ["Kaiser Supply Chain"]),
            ("090_USC", ["Zhipu"], ["Jipu"]),
            ("093_USC", ["BYD's", "$12,000", "$15,000"], ["BD's", "$122,000", "$115,000"]),
            ("099_USC", ["dollar announcement", "Masayoshi Son", "Larry Ellison", "Sam Altman"], ["do announcement", "Mas son", "Arison", "Sam Alman", "Larry Ellison and Larry Ellison"]),
            ("100_USC", ["UBTECH", "BrainNet 2.0", "19 degrees of freedom"], ["UBEC", "Brainet 2.0", "19\u00b0"]),
            ("009_AI", ["on-prem"], ["on prem"]),
        ]
        for cid, must_have, must_not_have in expected_present_absent:
            en_clean = self.clips_by_id[cid]["en_clean"]
            for s in must_have:
                self.assertIn(s, en_clean, f"Expected {s!r} in {cid} en_clean")
            for s in must_not_have:
                self.assertNotIn(s, en_clean, f"Unexpected raw typo {s!r} left in {cid} en_clean")

        # Verify en_raw matches raw /tmp/arsenal_100_queue.json 100% verbatim across all 100 clips
        for rec in self.raw_records:
            plan = rec["plan"]
            cid = plan["clip_id"]
            expected_raw = " ".join(s["en"].strip() for s in plan["subtitles"])
            self.assertEqual(
                self.clips_by_id[cid]["en_raw"],
                expected_raw,
                f"en_raw was mutated for {cid}",
            )

    # ------------------------------------------------------------------
    # Test 4: [snorts] preserved in en_raw, absent in en_clean & subtitles_clean; pure ASCII
    # ------------------------------------------------------------------
    def test_snorts_sanitized_from_en_clean_and_subtitles_clean(self) -> None:
        self.assertIn("[snorts]", self.clips_by_id["087_USC"]["en_raw"])
        for c in self.corpus["clips"]:
            cid = c["clip_id"]
            self.assertNotIn("[snorts]", c["en_clean"].lower(), f"[snorts] leaked in {cid} en_clean")
            self.assertTrue(
                all(ord(ch) < 128 for ch in c["en_clean"]),
                f"Non-ASCII char remains in {cid} en_clean",
            )
            for idx, seg in enumerate(c["subtitles_clean"]):
                self.assertNotIn(
                    "[snorts]",
                    seg["en"].lower(),
                    f"[snorts] leaked in {cid} subtitles_clean[{idx}]",
                )
                self.assertTrue(
                    all(ord(ch) < 128 for ch in seg["en"]),
                    f"Non-ASCII char remains in {cid} subtitles_clean[{idx}]",
                )

    # ------------------------------------------------------------------
    # Test 5: 100/100 inferred speakers complete and accurate
    # ------------------------------------------------------------------
    def test_inferred_speakers_complete_and_accurate(self) -> None:
        for c in self.corpus["clips"]:
            speakers = c["inferred_speakers"]
            self.assertIsInstance(speakers, list)
            self.assertGreater(len(speakers), 0, f"Empty speakers on {c['clip_id']}")
            for sp in speakers:
                self.assertIsInstance(sp, str)
                self.assertTrue(sp.strip(), f"Blank speaker string on {c['clip_id']}")

        anchor_checks: dict[str, str] = {
            "01_AI_DHH": "David Heinemeier Hansson (DHH)",
            "006_AI": "Andrej Karpathy",
            "012_AI": "Jensen Huang",
            "031_BIZ": "Elon Musk",
            "032_BIZ": "Business Motiversity (Storyteller on Jeff Bezos)",
            "033_BIZ": "Jeff Bezos",
            "03_FIN_Dalio": "Ray Dalio",
            "054_FIN": "Warren Buffett (Boardroom Billions Commentary)",
            "058_FIN": "FINAiUS (Narrator)",
            "059_FIN": "The Swedish Investor (Narrator)",
            "087_USC": "Kishore Mahbubani",
            "094_USC": "Kevin Rudd",
        }
        for cid, expected_speaker in anchor_checks.items():
            self.assertIn(
                expected_speaker,
                self.clips_by_id[cid]["inferred_speakers"],
                f"Expected speaker {expected_speaker!r} in {cid}",
            )

    # ------------------------------------------------------------------
    # Test 6: Executive lexicon schema, volume, 80/20 ratio, 0 bridge collisions
    # ------------------------------------------------------------------
    def test_executive_lexicon_schema_volume_and_corpus_ratio(self) -> None:
        self.assertIsInstance(self.lexicon, list)
        self.assertGreaterEqual(len(self.lexicon), 110)
        self.assertEqual(len(self.lexicon), 120)

        req_keys = {
            "phrase_id",
            "phrase_en",
            "category",
            "cefr_level",
            "chinglish_trap",
            "executive_subtext_zh",
            "verbatim_context_en",
            "source_type",
            "clip_ids",
        }
        valid_categories = {
            "executive_hedging_framing",
            "vc_valuation_finance",
            "ai_compute_product",
            "tariffs_supply_chain_geopolitics",
            "retail_channel_bridge",
            "compliance_hardware_bridge",
        }

        ids: set[str] = set()
        phrases_lower: set[str] = set()
        corpus_entries = []
        bridge_entries = []

        for e in self.lexicon:
            self.assertEqual(set(e.keys()), req_keys)
            ids.add(e["phrase_id"])
            phrases_lower.add(e["phrase_en"].lower())
            self.assertIn(e["category"], valid_categories)
            self.assertIn(e["cefr_level"], {"B1", "B2", "C1", "C2"})
            self.assertIn(e["source_type"], {"corpus", "world_bridge"})
            for k in (
                "phrase_id",
                "phrase_en",
                "chinglish_trap",
                "executive_subtext_zh",
                "verbatim_context_en",
            ):
                self.assertTrue(isinstance(e[k], str) and e[k].strip(), f"Empty {k} on {e['phrase_id']}")
            self.assertIn(
                e["phrase_en"].lower(),
                e["verbatim_context_en"].lower(),
                f"phrase_en missing from verbatim_context_en on {e['phrase_id']}",
            )
            self.assertIsInstance(e["clip_ids"], list)
            if e["source_type"] == "corpus":
                corpus_entries.append(e)
            else:
                bridge_entries.append(e)
                self.assertEqual(e["clip_ids"], [], f"world_bridge {e['phrase_id']} must have empty clip_ids")
                for cid, c in self.clips_by_id.items():
                    self.assertNotIn(
                        e["phrase_en"].lower(),
                        c["en_clean"].lower(),
                        f"world_bridge {e['phrase_en']!r} collided with corpus clip {cid}",
                    )

        self.assertEqual(len(ids), 120)
        self.assertEqual(len(phrases_lower), 120)
        self.assertEqual(len(corpus_entries), 96)
        self.assertEqual(len(bridge_entries), 24)
        self.assertGreaterEqual(len(corpus_entries) / len(self.lexicon), 0.75)

    # ------------------------------------------------------------------
    # Test 7: Every corpus lexicon phrase & verbatim_context verified in en_clean
    # ------------------------------------------------------------------
    def test_every_corpus_lexicon_phrase_verbatim_in_every_cited_clip(self) -> None:
        by_id = {e["phrase_id"]: e for e in self.lexicon}
        self.assertEqual(by_id["LEX_065"]["phrase_en"], "on-prem")
        self.assertEqual(by_id["LEX_065"]["clip_ids"], ["009_AI"])

        for e in self.lexicon:
            if e["source_type"] != "corpus":
                continue
            self.assertGreaterEqual(len(e["clip_ids"]), 1, f"Missing clip_ids on {e['phrase_id']}")
            for cid in e["clip_ids"]:
                self.assertIn(cid, self.clips_by_id, f"Unknown clip_id {cid} on {e['phrase_id']}")
                self.assertIn(
                    e["phrase_en"].lower(),
                    self.clips_by_id[cid]["en_clean"].lower(),
                    f"Corpus phrase {e['phrase_en']!r} ({e['phrase_id']}) missing in {cid}",
                )
            primary_cid = e["clip_ids"][0]
            self.assertIn(
                e["verbatim_context_en"],
                self.clips_by_id[primary_cid]["en_clean"],
                f"verbatim_context_en mismatch for {e['phrase_id']} in {primary_cid}",
            )

    # ------------------------------------------------------------------
    # Test 8: E001 5 seed clips & all 8 mandatory phrase groups (13 phrases)
    # ------------------------------------------------------------------
    def test_e001_seed_clips_and_all_eight_mandatory_phrase_groups(self) -> None:
        for seed_cid in ("02_BIZ_Anthropic", "012_AI", "039_BIZ", "090_USC", "059_FIN"):
            self.assertIn(seed_cid, self.clips_by_id)

        by_phrase_lower = {e["phrase_en"].lower(): e for e in self.lexicon}
        mandatory_pairs = [
            ("phantom number", "02_BIZ_Anthropic"),
            ("not a cash loss", "02_BIZ_Anthropic"),
            ("flowed through into the income statement", "02_BIZ_Anthropic"),
            ("capital-efficient", "02_BIZ_Anthropic"),
            ("10 times the throughput", "012_AI"),
            ("Pick your favorite number", "012_AI"),
            ("In other words", "039_BIZ"),
            ("eating into budgets", "090_USC"),
            ("a really hard trade-off", "090_USC"),
            ("What is good enough", "090_USC"),
            ("run this thing a million times", "090_USC"),
            ("upside", "059_FIN"),
            ("When are you going to get it", "059_FIN"),
        ]
        for phrase, seed_cid in mandatory_pairs:
            entry = by_phrase_lower.get(phrase.lower())
            self.assertIsNotNone(entry, f"Missing E001 mandatory phrase {phrase!r}")
            assert entry is not None
            self.assertEqual(entry["source_type"], "corpus")
            self.assertIn(seed_cid, entry["clip_ids"])
            self.assertIn(phrase.lower(), self.clips_by_id[seed_cid]["en_clean"].lower())

    # ------------------------------------------------------------------
    # Test 9: Fail-fast CLI error handling (nonexistent/corrupt/truncated/dup/missing)
    # ------------------------------------------------------------------
    def test_cli_error_handling_invalid_missing_truncated_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            # (a) Nonexistent source path
            out_a = base / "out_missing"
            res_a = self._run_etl("--source", str(base / "does_not_exist.json"), "--out-dir", str(out_a))
            self.assertNotEqual(res_a.returncode, 0)
            self.assertIn("--fetch-gdrive", res_a.stderr)
            self.assertFalse(out_a.exists())

            # (b) Corrupt JSON syntax
            bad_json = base / "bad.json"
            bad_json.write_text("{not valid json", encoding="utf-8")
            out_b = base / "out_bad_json"
            res_b = self._run_etl("--source", str(bad_json), "--out-dir", str(out_b))
            self.assertNotEqual(res_b.returncode, 0)
            self.assertIn("Invalid JSON", res_b.stderr)
            self.assertFalse(out_b.exists())

            # (c) Non-list JSON root
            obj_json = base / "obj.json"
            obj_json.write_text('{"clips": []}', encoding="utf-8")
            out_c = base / "out_obj"
            res_c = self._run_etl("--source", str(obj_json), "--out-dir", str(out_c))
            self.assertNotEqual(res_c.returncode, 0)
            self.assertIn("list", res_c.stderr.lower())
            self.assertFalse(out_c.exists())

            # (d) Truncated list (5 clips instead of 100)
            trunc_json = base / "trunc.json"
            trunc_json.write_text(json.dumps(self.raw_records[:5]), encoding="utf-8")
            out_d = base / "out_trunc"
            res_d = self._run_etl("--source", str(trunc_json), "--out-dir", str(out_d))
            self.assertNotEqual(res_d.returncode, 0)
            self.assertIn("100", res_d.stderr)
            self.assertFalse(out_d.exists())

            # (e) Duplicate clip_id
            dup_records = copy.deepcopy(self.raw_records)
            dup_records[1]["plan"]["clip_id"] = dup_records[0]["plan"]["clip_id"]
            dup_json = base / "dup.json"
            dup_json.write_text(json.dumps(dup_records), encoding="utf-8")
            out_e = base / "out_dup"
            res_e = self._run_etl("--source", str(dup_json), "--out-dir", str(out_e))
            self.assertNotEqual(res_e.returncode, 0)
            self.assertIn("Duplicate clip_id", res_e.stderr)
            self.assertFalse(out_e.exists())

            # (f) Missing subtitles key
            nosub_records = copy.deepcopy(self.raw_records)
            del nosub_records[0]["plan"]["subtitles"]
            nosub_json = base / "nosub.json"
            nosub_json.write_text(json.dumps(nosub_records), encoding="utf-8")
            out_f = base / "out_nosub"
            res_f = self._run_etl("--source", str(nosub_json), "--out-dir", str(out_f))
            self.assertNotEqual(res_f.returncode, 0)
            self.assertIn("subtitles", res_f.stderr)
            self.assertFalse(out_f.exists())

    # ------------------------------------------------------------------
    # Test 10: CORPUS_INTELLIGENCE_REPORT.md exact numeric parity with JSONs
    # ------------------------------------------------------------------
    def test_corpus_intelligence_report_matches_json_metrics(self) -> None:
        self.assertTrue(CORPUS_REPORT_PATH.exists())
        text = CORPUS_REPORT_PATH.read_text(encoding="utf-8")
        self.assertGreater(len(text), 20000)

        required_tokens = [
            "100",
            "1,408",
            "4,976.89s",
            "82.95 min",
            "170.34",
            "170.20",
            "173.72",
            "173.86",
            "14,409",
            "14,420",
            "27,095",
            "64",
            "030_AI",
            "030_BIZ",
            "054_BIZ",
            "054_FIN",
            "087_USC",
            "[snorts]",
            "Best Buy",
            "Selfridges",
            "GDPR",
            "120",
            "96/120",
            "80.0%",
            "24/120",
            "20.0%",
            "`36`",
            "`85`",
            "`98`",
            self.corpus["source_sha256"],
        ]
        for token in required_tokens:
            self.assertIn(token, text, f"Missing synced token {token!r} in CORPUS_INTELLIGENCE_REPORT.md")

    # ------------------------------------------------------------------
    # Test 11: RESEARCH_REPORT.md 5-pillar completeness, metric parity, zero placeholders
    # ------------------------------------------------------------------
    def test_research_report_five_pillars_and_integrity(self) -> None:
        self.assertTrue(RESEARCH_REPORT_PATH.exists())
        text = RESEARCH_REPORT_PATH.read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertGreaterEqual(len(lines), 200, "RESEARCH_REPORT.md must meet publication depth >= 200 lines")
        self.assertGreaterEqual(len(text), 10000, "RESEARCH_REPORT.md must exceed 10,000 chars")

        required_tokens = [
            # Evidence governance & Pillar 1
            "[语料实证]",
            "[仓库实测]",
            "[行业基准与测算模型]",
            "小宇宙",
            "喜马拉雅",
            "微信听书",
            "微信视频号",
            "45 秒",
            "单位经济",
            "hayek_1944",
            # Pillar 2
            "B1–C1",
            "通勤",
            "10–14",
            # Pillar 3
            "Business English Pod",
            "All-In",
            "Succession",
            "buffett_letters",
            # Pillar 4 (exact synced metrics + gap audit + 70/30 rule)
            "100",
            "1,408",
            "4,976.89s",
            "82.95 min",
            "170.34",
            "170.20",
            "173.72",
            "173.86",
            "27,095",
            "64",
            "030_AI",
            "054_FIN",
            "70%",
            "30%",
            "80.0%",
            "Best Buy",
            "Selfridges",
            "GDPR",
            # Pillar 5 (accent, prosody, SLA, E001 4 variants, 100-pt rubric)
            "85%",
            "15%",
            "0.80x",
            "atempo",
            "1.8s",
            "E001_VA",
            "E001_VB",
            "E001_VC",
            "E001_VD",
            "100 分盲测",
            "Hybrid-Winner",
        ]
        for token in required_tokens:
            self.assertIn(token, text, f"Missing required pillar/metric token {token!r} in RESEARCH_REPORT.md")

        for banned in ("TODO", "TBD", "FIXME", "Lorem ipsum"):
            self.assertNotIn(banned, text, f"Forbidden placeholder {banned!r} found in RESEARCH_REPORT.md")

    # ------------------------------------------------------------------
    # Test 12: Adversarial numeric, boolean, non-finite JSON & malformed plan fields
    # ------------------------------------------------------------------
    def test_rejects_bool_non_finite_and_malformed_plan_fields(self) -> None:
        raw_text = RAW_SOURCE_PATH.read_text(encoding="utf-8")
        dur0 = self.raw_records[0]["duration_sec"]
        vir0 = self.raw_records[0]["plan"]["virality_score"]

        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            def _assert_clean_rejection(name: str, payload_text: str) -> None:
                src = base / f"{name}.json"
                out = base / f"out_{name}"
                src.write_text(payload_text, encoding="utf-8")
                res = self._run_etl("--source", str(src), "--out-dir", str(out))
                self.assertNotEqual(res.returncode, 0, f"{name} unexpectedly succeeded")
                self.assertIn("ERROR:", res.stderr, f"{name} missing ERROR: prefix: {res.stderr!r}")
                self.assertNotIn("Traceback", res.stderr, f"{name} leaked Python traceback: {res.stderr!r}")
                self.assertFalse(out.exists(), f"{name} created output directory despite failing")

            # (a) Raw JSON non-finite constants (NaN / Infinity / -Infinity)
            _assert_clean_rejection(
                "duration_nan",
                raw_text.replace(f'"duration_sec": {dur0}', '"duration_sec": NaN', 1),
            )
            _assert_clean_rejection(
                "duration_inf",
                raw_text.replace(f'"duration_sec": {dur0}', '"duration_sec": Infinity', 1),
            )
            _assert_clean_rejection(
                "virality_neginf",
                raw_text.replace(f'"virality_score": {vir0}', '"virality_score": -Infinity', 1),
            )

            # (b) Python bool bypass on duration_sec and subtitle timestamps
            cases: list[tuple[str, object]] = []

            d_bool_dur = copy.deepcopy(self.raw_records)
            d_bool_dur[0]["duration_sec"] = True
            cases.append(("duration_bool_true", d_bool_dur))

            d_bool_sub = copy.deepcopy(self.raw_records)
            d_bool_sub[0]["plan"]["subtitles"][0]["start_sec"] = False
            d_bool_sub[0]["plan"]["subtitles"][0]["end_sec"] = True
            cases.append(("subtitle_bool_timestamps", d_bool_sub))

            # (c) Sub-cent duration rounding to 0.00
            d_tiny_dur = copy.deepcopy(self.raw_records)
            d_tiny_dur[0]["duration_sec"] = 0.001
            cases.append(("duration_rounds_to_zero", d_tiny_dur))

            # (d) Invalid virality_score & string plan fields (no unhandled tracebacks)
            for tag, bad_vir in (("vir_str", "high"), ("vir_none", None), ("vir_bool", True)):
                d_vir = copy.deepcopy(self.raw_records)
                d_vir[0]["plan"]["virality_score"] = bad_vir
                cases.append((tag, d_vir))

            for tag, bad_ch in (("channel_none", None), ("channel_blank", "   "), ("channel_int", 42)):
                d_ch = copy.deepcopy(self.raw_records)
                d_ch[0]["plan"]["channel"] = bad_ch
                cases.append((tag, d_ch))

            d_topic_list = copy.deepcopy(self.raw_records)
            d_topic_list[0]["plan"]["topic_key"] = ["AI"]
            cases.append(("topic_key_unhashable", d_topic_list))

            d_mp4_int = copy.deepcopy(self.raw_records)
            d_mp4_int[0]["local_mp4_path"] = 123
            cases.append(("local_mp4_path_int", d_mp4_int))

            d_ytid_int = copy.deepcopy(self.raw_records)
            d_ytid_int[0]["youtube_video_id"] = 999
            cases.append(("youtube_video_id_int", d_ytid_int))

            for name, obj in cases:
                _assert_clean_rejection(name, json.dumps(obj))

    # ------------------------------------------------------------------
    # Test 13: Fail-fast timestamp, severe/nested overlap & cardinality guards
    # ------------------------------------------------------------------
    def test_rejects_invalid_timestamps_severe_overlaps_and_bad_cardinality(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            def _assert_rejected(name: str, obj: object) -> None:
                src = base / f"{name}.json"
                out = base / f"out_{name}"
                src.write_text(json.dumps(obj), encoding="utf-8")
                res = self._run_etl("--source", str(src), "--out-dir", str(out))
                self.assertNotEqual(res.returncode, 0, f"{name} unexpectedly succeeded")
                self.assertIn("ERROR:", res.stderr)
                self.assertNotIn("Traceback", res.stderr)
                self.assertFalse(out.exists(), f"{name} wrote outputs despite validation error")

            # (a) Negative start_sec
            d_neg = copy.deepcopy(self.raw_records)
            d_neg[0]["plan"]["subtitles"][0]["start_sec"] = -2.0
            _assert_rejected("negative_start_sec", d_neg)

            # (b) Raw non-positive segment duration (end_sec <= start_sec)
            d_zero = copy.deepcopy(self.raw_records)
            d_zero[0]["plan"]["subtitles"][0]["end_sec"] = d_zero[0]["plan"]["subtitles"][0]["start_sec"]
            _assert_rejected("raw_zero_duration_segment", d_zero)

            # (c) Nested overlap where prev_end > curr_end ([10, 20] swallows [12, 15])
            d_nested = copy.deepcopy(self.raw_records)
            d_nested[0]["plan"]["subtitles"][0]["start_sec"] = 10.0
            d_nested[0]["plan"]["subtitles"][0]["end_sec"] = 20.0
            d_nested[0]["plan"]["subtitles"][1]["start_sec"] = 12.0
            d_nested[0]["plan"]["subtitles"][1]["end_sec"] = 15.0
            _assert_rejected("nested_overlap_swallows_next", d_nested)

            # (d) Severe overlap (2.5s > 0.25s) and tight boundary overlap (0.26s > 0.25s)
            d_severe = copy.deepcopy(self.raw_records)
            d_severe[0]["plan"]["subtitles"][0]["start_sec"] = 10.0
            d_severe[0]["plan"]["subtitles"][0]["end_sec"] = 15.0
            d_severe[0]["plan"]["subtitles"][1]["start_sec"] = 12.5
            d_severe[0]["plan"]["subtitles"][1]["end_sec"] = 17.0
            _assert_rejected("severe_overlap_2_5s", d_severe)

            d_over_max = copy.deepcopy(self.raw_records)
            d_over_max[0]["plan"]["subtitles"][0]["start_sec"] = 10.0
            d_over_max[0]["plan"]["subtitles"][0]["end_sec"] = 12.26
            d_over_max[0]["plan"]["subtitles"][1]["start_sec"] = 12.0
            d_over_max[0]["plan"]["subtitles"][1]["end_sec"] = 15.0
            _assert_rejected("overlap_exceeds_0_25s", d_over_max)

            # (e) Non-monotonic segment starts (curr_start < prev_start)
            d_nonmono = copy.deepcopy(self.raw_records)
            d_nonmono[0]["plan"]["subtitles"][0]["start_sec"] = 10.0
            d_nonmono[0]["plan"]["subtitles"][0]["end_sec"] = 12.0
            d_nonmono[0]["plan"]["subtitles"][1]["start_sec"] = 9.0
            d_nonmono[0]["plan"]["subtitles"][1]["end_sec"] = 14.0
            _assert_rejected("non_monotonic_start", d_nonmono)

            # (f) Wrong topic balance (26 AI + 24 BUSINESS)
            d_imbal = copy.deepcopy(self.raw_records)
            for rec in d_imbal:
                if rec["plan"]["topic_key"] == "BUSINESS":
                    rec["plan"]["topic_key"] = "AI"
                    break
            _assert_rejected("topic_imbalance_26_24", d_imbal)

            # (g) 99 and 101 clip cardinality
            _assert_rejected("clips_99", self.raw_records[:99])
            d_101 = copy.deepcopy(self.raw_records)
            extra = copy.deepcopy(self.raw_records[0])
            extra["plan"]["clip_id"] = "101_AI_EXTRA"
            d_101.append(extra)
            _assert_rejected("clips_101", d_101)

    # ------------------------------------------------------------------
    # Test 14: Shuffled-order invariance & CWD independence
    # ------------------------------------------------------------------
    def test_shuffled_order_invariance_and_cwd_independence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            # Shuffled raw corpus preserves summary_metrics, lexicon, and 030/054 collisions
            shuffled = copy.deepcopy(self.raw_records)
            random.Random(42).shuffle(shuffled)
            shuf_src = base / "shuffled_100.json"
            shuf_src.write_text(json.dumps(shuffled), encoding="utf-8")
            shuf_out = base / "out_shuffled"

            res_shuf = self._run_etl(
                "--source",
                str(shuf_src),
                "--out-dir",
                str(shuf_out),
                cwd=base,
            )
            self.assertEqual(res_shuf.returncode, 0, msg=res_shuf.stderr)

            shuf_corpus = json.loads((shuf_out / "corpus_100_structured.json").read_text(encoding="utf-8"))
            shuf_lex = json.loads((shuf_out / "executive_lexicon.json").read_text(encoding="utf-8"))
            self.assertEqual(shuf_corpus["summary_metrics"], self.corpus["summary_metrics"])
            self.assertEqual(shuf_lex, self.lexicon)
            shuf_cids = {c["clip_id"] for c in shuf_corpus["clips"]}
            for cid in ("030_AI", "030_BIZ", "054_BIZ", "054_FIN"):
                self.assertIn(cid, shuf_cids)

            # CWD independence on canonical source produces byte-exact committed parity
            cwd_out = base / "out_cwd"
            res_cwd = self._run_etl(
                "--source",
                str(RAW_SOURCE_PATH),
                "--out-dir",
                str(cwd_out),
                cwd=base,
            )
            self.assertEqual(res_cwd.returncode, 0, msg=res_cwd.stderr)
            for fname in (
                "corpus_100_structured.json",
                "executive_lexicon.json",
                "CORPUS_INTELLIGENCE_REPORT.md",
            ):
                self.assertEqual(
                    (cwd_out / fname).read_bytes(),
                    (CORPUS_DIR / fname).read_bytes(),
                    f"CWD-independent run drifted on {fname}",
                )

    # ------------------------------------------------------------------
    # Test 15: --fetch-gdrive PATH-shim verification (zero live Drive calls)
    # ------------------------------------------------------------------
    def test_fetch_gdrive_cli_invocation_with_safe_path_shim(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            bin_dir = base / "bin"
            bin_dir.mkdir()
            argv_log = base / "gdrive_argv.json"
            dest_json = base / "downloaded_arsenal.json"
            out_ok = base / "out_gdrive_ok"

            shim = bin_dir / "gdrive"
            shim.write_text(
                f"#!{sys.executable}\n"
                "import json, shutil, sys\n"
                "from pathlib import Path\n"
                f"Path({str(argv_log)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n"
                "if '--out' in sys.argv:\n"
                "    out_idx = sys.argv.index('--out') + 1\n"
                f"    shutil.copyfile({str(RAW_SOURCE_PATH)!r}, sys.argv[out_idx])\n"
                "sys.exit(0)\n",
                encoding="utf-8",
            )
            shim.chmod(shim.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"

            res_ok = self._run_etl(
                "--fetch-gdrive",
                "--source",
                str(dest_json),
                "--out-dir",
                str(out_ok),
                cwd=base,
                env=env,
            )
            self.assertEqual(res_ok.returncode, 0, msg=res_ok.stderr)
            recorded_argv = json.loads(argv_log.read_text(encoding="utf-8"))
            self.assertEqual(
                recorded_argv,
                [
                    "readonly",
                    "download",
                    "1K61WnLZKDEwW5QIwkc1BJ9SzOxRD-Gzj",
                    "--out",
                    str(dest_json),
                ],
            )
            self.assertTrue((out_ok / "corpus_100_structured.json").exists())

            # Failing gdrive binary exits cleanly with zero traceback and zero output files
            fail_shim = bin_dir / "gdrive"
            fail_shim.write_text(
                f"#!{sys.executable}\nimport sys\nsys.exit(42)\n",
                encoding="utf-8",
            )
            fail_shim.chmod(fail_shim.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            out_fail = base / "out_gdrive_fail"
            res_fail = self._run_etl(
                "--fetch-gdrive",
                "--source",
                str(base / "never_written.json"),
                "--out-dir",
                str(out_fail),
                cwd=base,
                env=env,
            )
            self.assertNotEqual(res_fail.returncode, 0)
            self.assertIn("ERROR:", res_fail.stderr)
            self.assertNotIn("Traceback", res_fail.stderr)
            self.assertFalse(out_fail.exists())

    # ------------------------------------------------------------------
    # Test 16: Dynamic report renders zero hardcoded stats on modified corpus
    # ------------------------------------------------------------------
    def test_dynamic_report_zero_hardcoded_stats_on_modified_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            # (a) Mutate 007_AI published status, duration_sec, virality_score
            mod_records = copy.deepcopy(self.raw_records)
            found = False
            for rec in mod_records:
                if rec["plan"]["clip_id"] == "007_AI":
                    rec["youtube_video_id"] = "TEST_PUBLISHED_10"
                    rec["duration_sec"] = 99.99
                    rec["plan"]["virality_score"] = 10.0
                    found = True
                    break
            self.assertTrue(found)

            mod_src = base / "mod_100.json"
            mod_src.write_text(json.dumps(mod_records), encoding="utf-8")
            mod_out = base / "out_mod"

            res = self._run_etl("--source", str(mod_src), "--out-dir", str(mod_out))
            self.assertEqual(res.returncode, 0, msg=res.stderr)

            mod_corpus = json.loads((mod_out / "corpus_100_structured.json").read_text(encoding="utf-8"))
            mod_md = (mod_out / "CORPUS_INTELLIGENCE_REPORT.md").read_text(encoding="utf-8")
            mod_sm = mod_corpus["summary_metrics"]

            self.assertEqual(mod_sm["published_count"], 10)
            self.assertEqual(mod_sm["queued_count"], 90)
            self.assertIn("已发布 **`10`** / 待发 **`90`**", mod_md)
            self.assertIn("90 条未发弹药", mod_md)
            self.assertIn("`43.33–99.99s`", mod_md)
            self.assertIn("`9.2–10.0`", mod_md)
            self.assertIn(f"`{mod_sm['min_wpm']:.2f}–{mod_sm['max_wpm']:.2f}`", mod_md)
            self.assertIn(f"`{mod_sm['raw_min_wpm']:.2f}–{mod_sm['raw_max_wpm']:.2f}`", mod_md)
            self.assertIn(f"`{mod_sm['raw_mean_wpm']:.1f}` 基线", mod_md)

            for stale in (
                "91 条未发弹药",
                "43.33–57.76s",
                "`9.2–9.9`",
                "125.31–227.45",
            ):
                self.assertNotIn(stale, mod_md, f"Stale canonical stat {stale!r} leaked into dynamic report")

            # (b) Pre-repaired zero-overlap corpus renders 0.00s cleanly (never hardcoded 0.04-0.09s)
            no_ovl_records = copy.deepcopy(self.raw_records)
            for rec in no_ovl_records:
                subs = rec["plan"]["subtitles"]
                for idx in range(1, len(subs)):
                    if subs[idx]["start_sec"] < subs[idx - 1]["end_sec"]:
                        subs[idx - 1]["end_sec"] = subs[idx]["start_sec"]
            no_ovl_src = base / "no_ovl_100.json"
            no_ovl_src.write_text(json.dumps(no_ovl_records), encoding="utf-8")
            no_ovl_out = base / "out_no_ovl"
            res_no_ovl = self._run_etl("--source", str(no_ovl_src), "--out-dir", str(no_ovl_out))
            self.assertEqual(res_no_ovl.returncode, 0, msg=res_no_ovl.stderr)
            no_ovl_md = (no_ovl_out / "CORPUS_INTELLIGENCE_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("**`0` 对重叠**（跨 **`0` 条切片**，`0.00s`）", no_ovl_md)
            self.assertNotIn("0.04–0.09s", no_ovl_md)


if __name__ == "__main__":
    unittest.main()
