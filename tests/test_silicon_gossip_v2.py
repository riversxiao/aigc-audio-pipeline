"""Regression & contract tests for《商战大瓜英语局》Silicon Gossip V2.1 pilot and 96GB G4 studio runner."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "colab_96gb"))

from aigc_audio_pipeline.drama3_adapter import translate_cue_to_drama3_input
from aigc_audio_pipeline.mixer import _compute_chatroom_pan_map
from aigc_audio_pipeline.models import (
    EpisodeCueSheet,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
)
from run_silicon_gossip_96gb import (
    _sanitize_modern_bgm_prompt,
    canonical_v2_stem,
    resolve_v2_targets,
)

PROJECT_DIR = REPO_ROOT / "projects" / "silicon_gossip"
REG_PATH = PROJECT_DIR / "00_节目圣经与选角档案" / "voice_casting_registry.json"
CUE_DIR = PROJECT_DIR / "02_分集广播剧台本"
E001_PATH = CUE_DIR / "V2_E001_OpenAI政变72小时_商战大瓜英语剧场.json"
NOTEBOOK_PATH = REPO_ROOT / "colab_96gb" / "Silicon_Gossip_96GB_Drama3_Studio.ipynb"


class SiliconGossipV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = VoiceCastingRegistry.load(REG_PATH)
        self.cue_sheet = EpisodeCueSheet.load(E001_PATH)

    def test_v2_pilot_validates_with_zero_errors(self) -> None:
        errors = self.cue_sheet.validate(self.registry, require_locked_voices=True)
        self.assertEqual(errors, [])
        self.assertEqual(self.registry.domain, "hotline_roundtable")
        self.assertEqual(self.cue_sheet.episode_id, "V2_E001")

    def test_v2_english_ceiling_and_light_english_ratio(self) -> None:
        en_cues = [c for c in self.cue_sheet.cues if c.kind == "dialogue" and c.language_code == "en"]
        self.assertGreaterEqual(len(en_cues), 16)
        for cue in en_cues:
            _, spoken = extract_tags_and_spoken_text(cue.text)
            words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", spoken)
            self.assertLessEqual(
                len(words),
                10,
                f"V2 hard rule violated on {cue.cue_id}: {len(words)} words > 10 ({spoken!r})",
            )

    def test_v2_1_dry_same_booth_hosts_relaxed_tone_and_brisk_pace(self) -> None:
        pan_map = _compute_chatroom_pan_map(self.cue_sheet)
        self.assertIn("host_xiaowei", pan_map)
        self.assertIn("guest_huaiyuan", pan_map)
        self.assertNotIn("guest_laozhou", pan_map)
        # Opposing table seating (left vs right)
        self.assertLess(pan_map["host_xiaowei"] * pan_map["guest_huaiyuan"], 0.0)

        host_cues = [
            c for c in self.cue_sheet.cues
            if c.kind == "dialogue" and c.role_id in ("host_xiaowei", "guest_huaiyuan")
        ]
        self.assertGreaterEqual(len(host_cues), 30)
        chuckle_count = 0
        for cue in host_cues:
            self.assertAlmostEqual(cue.playback_rate, 1.16, places=2)
            self.assertEqual(cue.stability, 0.5)
            if "[chuckles]" in cue.text:
                chuckle_count += 1
        # Keep chuckles subtle & organic (never stage-acting over-laughing)
        self.assertLessEqual(chuckle_count, 4)

    def test_v2_1_act5_exact_character_voice_matching(self) -> None:
        by_id = {c.cue_id: c for c in self.cue_sheet.cues}
        # Phrase 1 (candid) -> Ilya (`board_ilya`)
        self.assertEqual(by_id["v2_055"].role_id, "board_ilya")
        self.assertEqual(by_id["v2_056"].role_id, "board_ilya")
        # Phrases 2 & 3 (blindsided / Not on my watch) -> Satya Nadella (`satya_nadella`)
        self.assertEqual(by_id["v2_058"].role_id, "satya_nadella")
        self.assertEqual(by_id["v2_061"].role_id, "satya_nadella")
        # Phrase 4 (leverage) -> Sam Altman (`sam_altman`)
        self.assertEqual(by_id["v2_064"].role_id, "sam_altman")
        self.assertEqual(by_id["v2_065"].role_id, "sam_altman")

    def test_v2_drama3_prompt_hybrid_natural_zh_and_dramatic_en(self) -> None:
        by_id = {c.cue_id: c for c in self.cue_sheet.cues}
        zh_prompt = translate_cue_to_drama3_input(
            by_id["v2_007"],
            self.registry.resolve_role("host_xiaowei"),
            domain=self.registry.domain,
        )
        self.assertIn("[light chuckle]", zh_prompt)
        self.assertNotIn("conversational", zh_prompt.lower())

        en_prompt = translate_cue_to_drama3_input(
            by_id["v2_029"],
            self.registry.resolve_role("satya_nadella"),
            domain=self.registry.domain,
        )
        self.assertIn("<forceful>", en_prompt)
        self.assertIn("We were completely blindsided.", en_prompt)

    def test_v2_dry_chatroom_acts_have_zero_bgm_and_shadowing_has_085x(self) -> None:
        dry_acts = [a for a in self.cue_sheet.acts if not a.bgm_prompt.strip()]
        music_acts = [a for a in self.cue_sheet.acts if a.bgm_prompt.strip()]
        self.assertGreaterEqual(len(dry_acts), 4)
        self.assertGreaterEqual(len(music_acts), 4)
        for act in dry_acts:
            self.assertEqual(act.bgm_gain_speech, 0.0)
            self.assertEqual(act.bgm_gain_gap, 0.0)

        slow_cues = [c for c in self.cue_sheet.cues if c.kind == "dialogue" and abs(c.playback_rate - 0.85) < 1e-3]
        self.assertEqual(len(slow_cues), 4)

    def test_v2_runner_helpers_and_colab_notebook_valid(self) -> None:
        targets = resolve_v2_targets(CUE_DIR, "V2_E001")
        self.assertEqual([t[0] for t in targets], ["V2_E001"])
        self.assertEqual(resolve_v2_targets(CUE_DIR, "ALL")[0][0], "V2_E001")
        self.assertTrue(canonical_v2_stem(self.cue_sheet).startswith("V2_E001_"))
        san = _sanitize_modern_bgm_prompt("Upbeat pizzicato bass groove")
        self.assertIn("strictly instrumental", san)
        self.assertIn("no vocals", san)
        self.assertNotIn("cello", san.lower())

        nb = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(nb["metadata"]["colab"]["gpuType"], "G4")
        self.assertGreaterEqual(len(nb["cells"]), 6)


if __name__ == "__main__":
    unittest.main()
