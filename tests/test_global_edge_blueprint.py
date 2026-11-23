"""Unit tests for Milestone M3 of global_edge (《跨境底牌：硅深暗战》).

Pure Python stdlib unittest suite (zero third-party dependencies, zero working-tree mutations)
verifying:
- Canonical VoiceCastingRegistry load, lossless round-trip, strict M1 schema, 8 locked roles,
  live EpisodeCueSheet.validate() integration, Drama 3 zero-Xianxia translation across attempts
  1/2/3 & stabilities 0.0/0.5/1.0, EN [wryly] isolation, and 7 pure-physical English sonic motifs.
- Season 1 24-episode map (season1_24ep_map.json) lossless 100/100 bijective partition against
  corpus_100_structured.json, prefix-collision separation, exact 96.0%/4.0% accent quota math,
  full 8-role appearance_chapters sync, E001 control constants & 8 mandatory verbatim phrase groups
  (13 sub-phrases), strict atomic foreign-key validation on ALL corpus & companion lexicon IDs,
  >=70% corpus provenance per episode, and 24/24 false-hit-free world_bridge closure.
- Cross-document & code-to-doc parity across SHOW_BIBLE.md (including §3.2 unit economics & §6.1
  FFmpeg DSP chains vs mixer.py), ACCENT_AND_PROSODY_MANUAL.md (§3.2 tag table vs drama3_adapter.py),
  and SEASON1_24EP_BLUEPRINT.md (all 24 episode dossiers + Appendix III), plus full banned-cliché,
  24/24 uniqueness, and Chinese doubled-word typo hygiene.
"""

from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path

from aigc_audio_pipeline.drama3_adapter import (
    BUSINESS_DRAMA_ZH_MICRO_MAP,
    DRAMA3_POINT_EVENTS,
    DRAMA3_TAG_MAP,
    translate_cue_to_drama3_input,
)
from aigc_audio_pipeline.models import (
    ALLOWED_LANGUAGE_CODES,
    ALLOWED_V3_STABILITIES,
    ActMusicSpec,
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    validate_v3_dialogue_text,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
BIBLE_DIR = REPO_ROOT / "projects/global_edge/00_节目圣经与第一季24集总纲"
CORPUS_DIR = REPO_ROOT / "projects/global_edge/01_视频号语料与商业词库"

REGISTRY_PATH = BIBLE_DIR / "voice_casting_registry.json"
SEASON_MAP_PATH = BIBLE_DIR / "season1_24ep_map.json"
SHOW_BIBLE_PATH = BIBLE_DIR / "SHOW_BIBLE.md"
ACCENT_MANUAL_PATH = BIBLE_DIR / "ACCENT_AND_PROSODY_MANUAL.md"
BLUEPRINT_MD_PATH = BIBLE_DIR / "SEASON1_24EP_BLUEPRINT.md"
MIXER_PY_PATH = REPO_ROOT / "src/aigc_audio_pipeline/mixer.py"

CORPUS_JSON_PATH = CORPUS_DIR / "corpus_100_structured.json"
LEXICON_JSON_PATH = CORPUS_DIR / "executive_lexicon.json"
BUFFETT_BIBLE_PATH = (
    REPO_ROOT / "projects/buffett_letters/00_节目圣经与第一季12期总纲/SEASON1_SHOW_BIBLE.md"
)

CANONICAL_ROLE_ACCENTS = {
    "lin_chen": ("zh-en", "zh_en_bilingual_us", "protagonist"),
    "zhou_mo": ("zh-en", "zh_mainland_sz", "core_supporting"),
    "victoria_vance": ("en", "us_silicon_valley", "antagonist"),
    "alistair_finch": ("en", "uk_london_rp", "antagonist"),
    "claire_chen_gc": ("en", "us_nyc", "core_supporting"),
    "rajiv_menon": ("en", "intl_indian_exec", "recurring"),
    "wei_ling_tan": ("en", "intl_singapore_vc", "recurring"),
    "henrik_lindqvist": ("en", "intl_eu_legal", "recurring"),
}

GUEST_ROLE_CHAPTERS = {
    "henrik_lindqvist": [11],
    "rajiv_menon": [13],
    "wei_ling_tan": [13, 16],
}

EN_ROLE_MENTION_TOKENS = {
    "victoria_vance": ("Victoria", "维多利亚"),
    "alistair_finch": ("Alistair", "阿利斯泰尔"),
    "claire_chen_gc": ("Claire", "克莱尔"),
    "henrik_lindqvist": ("Henrik",),
    "rajiv_menon": ("Rajiv",),
    "wei_ling_tan": ("Wei-Ling",),
}

HUMAN_VOCAL_CLAUSE_RE = re.compile(
    r"(?:,?\s*(?:accompanied by|with|and)\s+[^,.]*?\b"
    r"(?:cough(?:ing|s)?|groan(?:ing|s)?|grunt(?:ing|s)?|sigh(?:ing|s)?|"
    r"scream(?:ing|s)?|sob(?:bing|s)?|voice|vocal)\b[^,.]*)",
    re.IGNORECASE,
)

FORBIDDEN_FOLEY_WORDS = (
    "cough",
    "groan",
    "grunt",
    "sigh",
    "scream",
    "sob",
    "vocal",
    "speech",
    "whisper",
    "laugh",
    "chatter",
    "murmur",
    "voice",
)

# Synchronized 1:1 with SHOW_BIBLE.md §7.3 ban-list
BANNED_CLICHES_AND_LEAKS = (
    "各位听众",
    "欢迎收听今天的英语课",
    "欢迎收听",
    "大家好，我是",
    "问到根子上了",
    "这个比方绝了",
    "说得太好了",
    "一针见血",
    "youtube",
    "视频号",
    "上期切片",
    "本期视频",
    "今天这条短视频",
)

CHINESE_DOUBLED_WORD_RE = re.compile(r"([\u4e00-\u9fff]{2,4})\1")

XIANXIA_DEFAULT_ACCENT_REQ = "大陆普通话戏剧配音（严禁港台/美式/澳洲/新加坡飘口音）"

E001_SEED_CLIPS = ["02_BIZ_Anthropic", "012_AI", "039_BIZ", "090_USC", "059_FIN"]
E001_MANDATORY_13_PHRASES = [
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

REQUIRED_MIXER_DSP_FILTERS = (
    "aformat=sample_rates=48000:channel_layouts=stereo",
    "highpass=f=75",
    "aecho=0.88:0.86:18|36:0.12|0.06",
    "equalizer=f=150:t=q:w=1.2:g=1.8,equalizer=f=3200:t=q:w=1.4:g=0.9",
    "highpass=f=300,lowpass=f=3400,acompressor=threshold=-18dB:ratio=3:attack=5:release=60",
    "equalizer=f=175:t=q:w=1.2:g=1.2,equalizer=f=3600:t=q:w=1.4:g=0.8",
    "aecho=0.88:0.85:35|75:0.16|0.08",
    "apad=pad_dur=0.12",
    "highpass=f=180,lowpass=f=5500",
    "aecho=0.85:0.80:65|130:0.24|0.12",
    "apad=pad_dur=0.20",
    "loudnorm=I=-16:TP=-1.5:LRA=11",
    "alimiter=limit=0.84:level=disabled",
)


class TestGlobalEdgeBlueprintM3(unittest.TestCase):
    """Comprehensive verification of M3 Show Bible, Accent Manual, 24-Ep Map & Casting Registry."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw_registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.registry = VoiceCastingRegistry.load(REGISTRY_PATH)
        cls.season_map = json.loads(SEASON_MAP_PATH.read_text(encoding="utf-8"))
        cls.corpus = json.loads(CORPUS_JSON_PATH.read_text(encoding="utf-8"))
        cls.clips_by_id = {c["clip_id"]: c for c in cls.corpus["clips"]}
        cls.lexicon = json.loads(LEXICON_JSON_PATH.read_text(encoding="utf-8"))
        cls.lex_by_id = {e["phrase_id"]: e for e in cls.lexicon}
        cls.show_bible_md = SHOW_BIBLE_PATH.read_text(encoding="utf-8")
        cls.accent_manual_md = ACCENT_MANUAL_PATH.read_text(encoding="utf-8")
        cls.blueprint_md = BLUEPRINT_MD_PATH.read_text(encoding="utf-8")
        cls.mixer_py_src = MIXER_PY_PATH.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # 1. Registry Load, Canonical Schema, Lossless Round-Trip & Aliases
    # ------------------------------------------------------------------
    def test_registry_canonical_top_level_schema_and_round_trip(self) -> None:
        self.assertNotIn("dialogue_model_id", self.raw_registry)
        self.assertNotIn("asr_qa_model_id", self.raw_registry)
        for key in (
            "project_id",
            "project_title",
            "language_code",
            "domain",
            "tts_model_id",
            "sfx_model_id",
            "music_model_id",
            "asr_model_id",
            "updated_at",
            "drive_audio_root_id",
            "roles",
            "sonic_motifs",
        ):
            self.assertIn(key, self.raw_registry, f"Missing canonical key: {key}")

        self.assertEqual(self.registry.project_id, "global_edge")
        self.assertEqual(self.registry.language_code, "zh-en")
        self.assertEqual(self.registry.domain, "business_english_drama")
        self.assertEqual(self.registry.tts_model_id, "fishaudio/drama-3")
        self.assertEqual(self.registry.sfx_model_id, "OpenMOSS-Team/MOSS-SoundEffect-v2.0")
        self.assertEqual(self.registry.music_model_id, "ACE-Step/acestep-v15-xl-turbo-diffusers")
        self.assertEqual(self.registry.asr_model_id, "faster-whisper-small-int8")

        # Lossless round-trip check
        serialized = self.registry.to_dict()
        self.assertEqual(self.raw_registry, serialized)
        reloaded = VoiceCastingRegistry.from_dict(serialized)
        self.assertEqual(serialized, reloaded.to_dict())

        # Alias resolution uniqueness across all 8 roles
        seen_aliases: dict[str, str] = {}
        for role_id, prof in self.registry.roles.items():
            self.assertIs(self.registry.resolve_role(role_id), prof)
            self.assertIs(self.registry.resolve_role(prof.display_name), prof)
            for alias in prof.aliases:
                self.assertNotIn(
                    alias,
                    seen_aliases,
                    f"Alias collision '{alias}' between {seen_aliases.get(alias)} and {role_id}",
                )
                seen_aliases[alias] = role_id
                self.assertIs(self.registry.resolve_role(alias), prof)

    # ------------------------------------------------------------------
    # 2. All 8 Roles Locked, Valid Tags & Zero EN [wryly] Leakage
    # ------------------------------------------------------------------
    def test_eight_canonical_locked_roles_and_tags(self) -> None:
        self.assertEqual(set(self.registry.roles.keys()), set(CANONICAL_ROLE_ACCENTS.keys()))
        self.assertEqual(len(self.registry.roles), 8)

        allowed_tags = set(DRAMA3_TAG_MAP) | set(DRAMA3_POINT_EVENTS)
        seen_voice_ids: set[str] = set()

        for role_id, (exp_lang, exp_accent, exp_tier) in CANONICAL_ROLE_ACCENTS.items():
            prof = self.registry.roles[role_id]
            self.assertEqual(prof.role_id, role_id)
            self.assertEqual(prof.language_code, exp_lang)
            self.assertIn(prof.language_code, ALLOWED_LANGUAGE_CODES)
            self.assertEqual(prof.accent_code, exp_accent)
            self.assertEqual(prof.tier, exp_tier)
            self.assertEqual(prof.status, "locked")
            self.assertEqual(prof.voice_id, f"drama3_anchor_{role_id}")
            self.assertNotIn(prof.voice_id, seen_voice_ids)
            seen_voice_ids.add(prof.voice_id)

            self.assertIn(prof.default_stability, ALLOWED_V3_STABILITIES)
            self.assertGreater(prof.similarity_boost, 0.0)
            self.assertLessEqual(prof.similarity_boost, 1.0)

            self.assertTrue(prof.accent_requirement.strip())
            self.assertNotEqual(prof.accent_requirement.strip(), XIANXIA_DEFAULT_ACCENT_REQ)
            self.assertNotIn("严禁港台/美式/澳洲/新加坡飘口音", prof.accent_requirement)

            self.assertTrue(prof.signature_tags, f"{role_id} must define signature_tags")
            for tag_token in prof.signature_tags:
                match = re.fullmatch(r"\[([a-z0-9\s,\-']+)\]", tag_token)
                self.assertIsNotNone(match, f"Malformed signature tag {tag_token} on {role_id}")
                tag_name = match.group(1)
                self.assertIn(tag_name, allowed_tags, f"Unknown Drama 3 tag {tag_token} on {role_id}")
                if prof.language_code == "en":
                    self.assertNotEqual(
                        tag_name,
                        "wryly",
                        f"Pure-EN role {role_id} must not use [wryly] (maps to Midwestern wit)",
                    )

            self.assertTrue(prof.appearance_chapters)
            self.assertEqual(prof.first_appearance_chapter, min(prof.appearance_chapters))
            for ch in prof.appearance_chapters:
                self.assertTrue(1 <= ch <= 24)
            if role_id in GUEST_ROLE_CHAPTERS:
                self.assertEqual(prof.appearance_chapters, GUEST_ROLE_CHAPTERS[role_id])
                self.assertNotIn(1, prof.appearance_chapters)

    # ------------------------------------------------------------------
    # 3. Audition Lines & Live Drama 3 Zero-Xianxia Translation
    # ------------------------------------------------------------------
    def test_audition_lines_validate_and_translate_cleanly(self) -> None:
        allowed_tags = set(DRAMA3_TAG_MAP) | set(DRAMA3_POINT_EVENTS)
        style_tags = set(DRAMA3_TAG_MAP)

        for role_id, prof in self.registry.roles.items():
            errs = validate_v3_dialogue_text(
                prof.audition_line,
                prof.default_stability,
                language_code=prof.language_code,
                item_label=f"audition_line:{role_id}",
            )
            self.assertEqual(errs, [], f"Validation errors for {role_id}: {errs}")

            inline_tags = re.findall(r"\[([^\]]+)\]", prof.audition_line)
            self.assertTrue(inline_tags, f"{role_id} audition_line should include HBO acting tags")
            for tag_name in inline_tags:
                self.assertIn(tag_name, allowed_tags, f"Unknown inline tag [{tag_name}] on {role_id}")
                if prof.language_code == "en":
                    self.assertNotEqual(tag_name, "wryly")

            # Enforce max 2 style tags per sentence/clause
            clauses = re.split(r"[。！？.!?]+", prof.audition_line)
            for clause in clauses:
                clause_style_tags = [
                    t for t in re.findall(r"\[([^\]]+)\]", clause) if t in style_tags
                ]
                self.assertLessEqual(
                    len(clause_style_tags),
                    2,
                    f"Clause has >2 style tags on {role_id}: {clause}",
                )

            # Anti-cliché / anti-Shorts leakage check
            low_line = prof.audition_line.lower()
            for banned in BANNED_CLICHES_AND_LEAKS:
                self.assertNotIn(banned, low_line, f"Banned phrase '{banned}' in {role_id} audition_line")

            for stability in ALLOWED_V3_STABILITIES:
                cue = TimelineCue(
                    cue_id=f"AUD_{role_id}_{str(stability).replace('.', '_')}",
                    act_id="ACT1",
                    kind="dialogue",
                    role_id=role_id,
                    speaker_name=prof.display_name,
                    language_code=prof.language_code,
                    text=prof.audition_line,
                    stability=stability,
                )
                for attempt in (1, 2, 3):
                    translated = translate_cue_to_drama3_input(
                        cue,
                        prof,
                        attempt=attempt,
                        domain="business_english_drama",
                    )
                    self.assertTrue(translated.strip())
                    low_out = translated.lower()
                    for forbidden in ("xianxia", "ancient monotone", "cultivation", "midwestern", "<slow>"):
                        self.assertNotIn(
                            forbidden,
                            low_out,
                            f"Forbidden leak '{forbidden}' for {role_id} stab={stability} attempt={attempt}: {translated}",
                        )

    # ------------------------------------------------------------------
    # 4. Synthetic EpisodeCueSheet.validate() Integration Against Locked Registry
    # ------------------------------------------------------------------
    def test_synthetic_episode_cue_sheet_validates_with_locked_registry(self) -> None:
        corporate_spaces = (
            "boardroom",
            "inner_monologue",
            "phone_call",
            "studio_warm",
            "dry",
            "vast_hall",
            "memory_echo",
        )
        cues: list[TimelineCue] = []

        # Include all 7 sonic motifs via motif_id reference
        for idx, motif_id in enumerate(self.registry.sonic_motifs, 1):
            cues.append(
                TimelineCue(
                    cue_id=f"SFX_{idx:03d}",
                    act_id="ACT1",
                    kind="sfx",
                    motif_id=motif_id,
                    gap_after_s=0.25,
                )
            )

        # Include all 8 roles' audition_lines, negative-gap crosstalk (-0.15s), and duck_under_next
        role_items = list(self.registry.roles.items())
        for idx, (role_id, prof) in enumerate(role_items, 1):
            space = corporate_spaces[(idx - 1) % len(corporate_spaces)]
            cues.append(
                TimelineCue(
                    cue_id=f"DLG_{idx:03d}",
                    act_id="ACT1",
                    kind="dialogue",
                    role_id=role_id,
                    speaker_name=prof.display_name,
                    language_code=prof.language_code,
                    text=prof.audition_line,
                    stability=prof.default_stability,
                    acoustic_space=space,
                    playback_rate=1.0,
                    subtitle_translation="高管实战双语字幕验证。" if prof.language_code == "en" else "",
                    duck_under_next=(idx == 3),
                    gap_after_s=-0.15 if idx == 1 else 0.35,
                )
            )

        # Include Act 5 slow breakdown (playback_rate=0.8) and native shadowing (1.0x + 2.2s gap)
        lin = self.registry.roles["lin_chen"]
        cues.append(
            TimelineCue(
                cue_id="ACT5_SLOW_001",
                act_id="ACT5",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name=lin.display_name,
                language_code="en",
                text="[coach] That eighty-million-dollar loss is a phantom number.",
                stability=0.5,
                acoustic_space="studio_warm",
                playback_rate=0.8,
                subtitle_translation="那八千万美元的亏损只是一个账面幽灵数字。",
                gap_after_s=0.5,
            )
        )
        cues.append(
            TimelineCue(
                cue_id="ACT5_SHADOW_002",
                act_id="ACT5",
                kind="dialogue",
                role_id="lin_chen",
                speaker_name=lin.display_name,
                language_code="en",
                text="[coach] That eighty-million-dollar loss is a phantom number.",
                stability=0.5,
                acoustic_space="dry",
                playback_rate=1.0,
                subtitle_translation="原速跟读示范。",
                gap_after_s=2.2,
            )
        )

        sheet = EpisodeCueSheet(
            episode_id="E001_SYNTH",
            chapter_number=1,
            title="Synthetic M3 Registry Validation Cue Sheet",
            mode="bilingual_business_drama",
            acts=[
                ActMusicSpec(
                    act_id="ACT1",
                    title="Boardroom Cold Open",
                    bgm_prompt="Minimalist HBO chamber strings underscore, purely instrumental, no vocals",
                    bgm_gain_speech=0.07,
                    bgm_gain_gap=0.26,
                ),
                ActMusicSpec(
                    act_id="ACT5",
                    title="Executive Black-Book Debrief",
                    bgm_prompt="Ultra-clean minimalist modern executive podcast bed, purely instrumental, no vocals",
                    bgm_gain_speech=0.06,
                    bgm_gain_gap=0.24,
                ),
            ],
            cues=cues,
        )
        errors = sheet.validate(self.registry, require_locked_voices=True)
        self.assertEqual(errors, [], f"Synthetic EpisodeCueSheet validation failed: {errors}")

    # ------------------------------------------------------------------
    # 5. Sonic Motifs Pure Physical English Foley
    # ------------------------------------------------------------------
    def test_sonic_motifs_pure_physical_english_foley(self) -> None:
        motifs = self.registry.sonic_motifs
        self.assertGreaterEqual(len(motifs), 6)
        self.assertLessEqual(len(motifs), 8)
        self.assertEqual(len(motifs), 7)

        for motif_id, motif in motifs.items():
            self.assertEqual(motif.motif_id, motif_id)
            self.assertTrue(motif.name.strip())
            self.assertTrue(motif.description.strip())
            self.assertTrue(motif.sfx_prompt.isascii(), f"{motif_id} sfx_prompt must be pure ASCII")
            self.assertGreaterEqual(motif.duration_seconds, 0.5)
            self.assertLessEqual(motif.duration_seconds, 30.0)
            self.assertGreaterEqual(motif.prompt_influence, 0.55)
            self.assertLessEqual(motif.prompt_influence, 0.65)
            self.assertFalse(motif.loop)

            suffix = ", pure foley, no human voice"
            self.assertTrue(
                motif.sfx_prompt.endswith(suffix),
                f"{motif_id} sfx_prompt must end with exact '{suffix}': {motif.sfx_prompt}",
            )
            self.assertNotIn("with no human voice", motif.sfx_prompt.lower())
            self.assertNotIn("and no human voice", motif.sfx_prompt.lower())
            self.assertIsNone(
                HUMAN_VOCAL_CLAUSE_RE.search(motif.sfx_prompt),
                f"{motif_id} triggered HUMAN_VOCAL_CLAUSE_RE: {motif.sfx_prompt}",
            )

            body = motif.sfx_prompt[: -len(suffix)].lower()
            for word in FORBIDDEN_FOLEY_WORDS:
                self.assertNotRegex(
                    body,
                    rf"\b{re.escape(word)}\w*\b",
                    f"Forbidden vocalization word '{word}' in {motif_id} body: {body}",
                )

    # ------------------------------------------------------------------
    # 6. Season 1 24-Episode Map & Lossless 100/100 Corpus Bijection
    # ------------------------------------------------------------------
    def test_season1_map_bijective_100_clip_partition(self) -> None:
        self.assertEqual(self.season_map["project_id"], "global_edge")
        self.assertEqual(self.season_map["season"], 1)
        self.assertEqual(self.season_map["total_episodes"], 24)
        self.assertEqual(self.season_map["total_mapped_clips"], 100)

        episodes = self.season_map["episodes"]
        arcs = self.season_map["arcs"]
        self.assertEqual(len(episodes), 24)
        self.assertEqual(len(arcs), 4)
        self.assertEqual([e["episode_id"] for e in episodes], [f"E{i:03d}" for i in range(1, 25)])

        required_ep_keys = {
            "episode_id",
            "arc_number",
            "arc_title",
            "title_zh",
            "title_en",
            "logline_zh",
            "primary_clip_ids",
            "accent_profile",
            "core_us_uk_en_pct",
            "target_phrases",
            "viral_45s_hook",
            "cliffhanger_zh",
        }
        all_assigned: list[str] = []
        ep_by_id = {}
        for ep in episodes:
            self.assertTrue(required_ep_keys.issubset(ep.keys()), f"Missing keys in {ep['episode_id']}")
            all_assigned.extend(ep["primary_clip_ids"])
            ep_by_id[ep["episode_id"]] = ep

        # Exact 100/100 bijection
        self.assertEqual(len(all_assigned), 100)
        self.assertEqual(len(set(all_assigned)), 100)
        self.assertEqual(set(all_assigned), set(self.clips_by_id.keys()))

        # Exact 20x4 + 4x5 tentpole structure
        tentpoles = [e["episode_id"] for e in episodes if len(e["primary_clip_ids"]) == 5]
        standards = [e["episode_id"] for e in episodes if len(e["primary_clip_ids"]) == 4]
        self.assertEqual(tentpoles, ["E001", "E006", "E012", "E024"])
        self.assertEqual(len(standards), 20)

        # Prefix collision separation
        self.assertIn("030_BIZ", ep_by_id["E003"]["primary_clip_ids"])
        self.assertIn("030_AI", ep_by_id["E011"]["primary_clip_ids"])
        self.assertIn("054_FIN", ep_by_id["E021"]["primary_clip_ids"])
        self.assertIn("054_BIZ", ep_by_id["E024"]["primary_clip_ids"])

        # Balanced 4-pillar coverage (25 x 4)
        pillar_counts = Counter(self.clips_by_id[cid]["topic_key"] for cid in all_assigned)
        self.assertEqual(pillar_counts, {"AI": 25, "BUSINESS": 25, "FINANCE": 25, "US_CHINA": 25})

        # 4 six-episode arcs integrity
        for idx, arc in enumerate(arcs, 1):
            self.assertEqual(arc["arc_number"], idx)
            arc_eps = [e for e in episodes if e["arc_number"] == idx]
            self.assertEqual(len(arc_eps), 6)
            self.assertEqual(arc["episode_ids"], [e["episode_id"] for e in arc_eps])
            self.assertEqual(arc["clip_count"], sum(len(e["primary_clip_ids"]) for e in arc_eps))

    # ------------------------------------------------------------------
    # 7. Accent Quota Math & Full 8-Role Appearance Chapter Sync
    # ------------------------------------------------------------------
    def test_accent_quota_math_and_full_eight_role_appearance_sync(self) -> None:
        episodes = self.season_map["episodes"]
        ep_by_id = {e["episode_id"]: e for e in episodes}

        self.assertEqual(ep_by_id["E001"]["core_us_uk_en_pct"], 100)
        guest_eps = {e["episode_id"] for e in episodes if e["core_us_uk_en_pct"] < 100}
        self.assertEqual(guest_eps, {"E011", "E013", "E016"})

        # Verify guest episodes in map match guest appearance_chapters in voice_casting_registry.json
        reg_guest_eps = {
            f"E{ch:03d}"
            for rid in GUEST_ROLE_CHAPTERS
            for ch in self.registry.roles[rid].appearance_chapters
        }
        self.assertEqual(guest_eps, reg_guest_eps)

        self.assertEqual(ep_by_id["E011"]["core_us_uk_en_pct"], 70)
        self.assertEqual(ep_by_id["E013"]["core_us_uk_en_pct"], 64)
        self.assertEqual(ep_by_id["E016"]["core_us_uk_en_pct"], 70)

        computed_mean = sum(e["core_us_uk_en_pct"] for e in episodes) / len(episodes)
        self.assertAlmostEqual(computed_mean, self.season_map["season_core_us_uk_en_pct"], places=6)
        self.assertGreaterEqual(self.season_map["season_core_us_uk_en_pct"], 85.0)
        self.assertAlmostEqual(
            self.season_map["international_guest_en_pct"],
            100.0 - self.season_map["season_core_us_uk_en_pct"],
            places=6,
        )
        self.assertLessEqual(self.season_map["international_guest_en_pct"], 15.0)

        for arc in self.season_map["arcs"]:
            arc_eps = [ep_by_id[eid] for eid in arc["episode_ids"]]
            arc_mean = sum(e["core_us_uk_en_pct"] for e in arc_eps) / 6
            self.assertAlmostEqual(arc_mean, arc["core_us_uk_en_pct"], places=6)

        # Full 8-role appearance_chapters sync against season1_24ep_map.json
        self.assertEqual(self.registry.roles["lin_chen"].appearance_chapters, list(range(1, 25)))
        self.assertEqual(self.registry.roles["zhou_mo"].appearance_chapters, list(range(1, 25)))
        for ep in episodes:
            self.assertIn(
                "林沉",
                ep["accent_profile"],
                f"Protagonist lin_chen missing from {ep['episode_id']}.accent_profile",
            )

        for role_id, tokens in EN_ROLE_MENTION_TOKENS.items():
            mentioned_chapters = [
                int(ep["episode_id"][1:])
                for ep in episodes
                if any(tok in ep["accent_profile"] for tok in tokens)
            ]
            self.assertEqual(
                mentioned_chapters,
                self.registry.roles[role_id].appearance_chapters,
                f"Role '{role_id}' appearance_chapters out of sync with season1_24ep_map.json accent_profile",
            )

        # Verify London RP banner appears in accent_profile iff alistair_finch appears in that chapter
        alistair_chapters = set(self.registry.roles["alistair_finch"].appearance_chapters)
        for ep in episodes:
            ch = int(ep["episode_id"][1:])
            has_rp_banner = ("伦敦 RP" in ep["accent_profile"]) or ("伦敦" in ep["accent_profile"])
            self.assertEqual(
                has_rp_banner,
                ch in alistair_chapters,
                f"{ep['episode_id']}: London RP mention in accent_profile contradicts alistair_finch.appearance_chapters",
            )

    # ------------------------------------------------------------------
    # 8. E001 Controls, Strict Atomic Foreign-Key Provenance & Viral Hooks
    # ------------------------------------------------------------------
    def test_e001_controls_and_verbatim_phrase_provenance(self) -> None:
        episodes = self.season_map["episodes"]
        e001 = episodes[0]

        self.assertEqual(e001["title_zh"], "八千万幽灵账单")
        self.assertEqual(e001["title_en"], "The $80M Phantom")
        self.assertEqual(e001["primary_clip_ids"], E001_SEED_CLIPS)
        self.assertEqual(len(e001["target_phrases"]), 8)

        # Verify all 13 mandatory E001 verbatim phrases present and NO "10x the throughput"
        e001_pairs: list[tuple[str, str]] = []
        for item in e001["target_phrases"]:
            self.assertEqual(item["source_type"], "corpus")
            e001_pairs.append((item["phrase_en"], item["clip_id"]))
            if item.get("companion_phrase_en"):
                e001_pairs.append((item["companion_phrase_en"], item["clip_id"]))
        self.assertEqual(e001_pairs, E001_MANDATORY_13_PHRASES)
        self.assertNotIn("10x the throughput", json.dumps(e001, ensure_ascii=False).lower())

        all_clean_texts = [c["en_clean"] for c in self.corpus["clips"]]
        world_bridge_ids: list[str] = []

        for ep in episodes:
            eid = ep["episode_id"]
            phrases = ep["target_phrases"]
            self.assertGreaterEqual(len(phrases), 5, f"{eid} has <5 target_phrases")
            self.assertLessEqual(len(phrases), 8, f"{eid} has >8 target_phrases")

            corpus_count = sum(1 for p in phrases if p["source_type"] == "corpus")
            self.assertGreaterEqual(
                corpus_count / len(phrases),
                0.70,
                f"{eid} corpus share below 70%: {corpus_count}/{len(phrases)}",
            )

            for item in phrases:
                self.assertTrue(item["phrase_en"].strip())
                self.assertTrue(item["chinglish_trap"].strip())
                self.assertTrue(item["executive_subtext_zh"].strip())

                if item["source_type"] == "corpus":
                    cid = item["clip_id"]
                    self.assertIn(
                        cid,
                        ep["primary_clip_ids"],
                        f"{eid}: phrase '{item['phrase_en']}' cites {cid} outside primary_clip_ids",
                    )
                    en_clean = self.clips_by_id[cid]["en_clean"].lower()
                    self.assertIn(
                        item["phrase_en"].lower(),
                        en_clean,
                        f"{eid}: '{item['phrase_en']}' not verbatim in {cid} en_clean",
                    )

                    # Strict atomic foreign-key validation for corpus lexicon_id
                    lex_id = item.get("lexicon_id")
                    if lex_id is not None:
                        self.assertIsInstance(lex_id, str)
                        self.assertNotIn(
                            "/",
                            lex_id,
                            f"{eid}: lexicon_id must be atomic (no '/'), got {lex_id!r}",
                        )
                        self.assertIn(
                            lex_id,
                            self.lex_by_id,
                            f"{eid}: unknown corpus lexicon_id {lex_id!r}",
                        )
                        lex = self.lex_by_id[lex_id]
                        self.assertEqual(lex["source_type"], "corpus")
                        self.assertEqual(lex["phrase_en"].lower(), item["phrase_en"].lower())
                        self.assertIn(
                            cid,
                            lex["clip_ids"],
                            f"{eid}: {lex_id} clip_ids {lex['clip_ids']} missing {cid}",
                        )

                    # Strict atomic foreign-key validation for companion_phrase_en + companion_lexicon_id
                    if item.get("companion_phrase_en"):
                        comp_phrase = item["companion_phrase_en"]
                        self.assertIn(
                            comp_phrase.lower(),
                            en_clean,
                            f"{eid}: companion '{comp_phrase}' not verbatim in {cid}",
                        )
                        comp_lex_id = item.get("companion_lexicon_id")
                        self.assertIsInstance(
                            comp_lex_id,
                            str,
                            f"{eid}: companion_phrase_en '{comp_phrase}' requires atomic companion_lexicon_id",
                        )
                        self.assertNotIn("/", comp_lex_id)
                        self.assertIn(comp_lex_id, self.lex_by_id)
                        comp_lex = self.lex_by_id[comp_lex_id]
                        self.assertEqual(comp_lex["source_type"], "corpus")
                        self.assertEqual(comp_lex["phrase_en"].lower(), comp_phrase.lower())
                        self.assertIn(cid, comp_lex["clip_ids"])
                elif item["source_type"] == "world_bridge":
                    self.assertIsNone(
                        item["clip_id"],
                        f"{eid}: world_bridge phrase '{item['phrase_en']}' must have clip_id=None",
                    )
                    lex_id = item["lexicon_id"]
                    self.assertIsInstance(lex_id, str)
                    self.assertNotIn("/", lex_id)
                    self.assertIn(lex_id, self.lex_by_id)
                    self.assertEqual(self.lex_by_id[lex_id]["source_type"], "world_bridge")
                    self.assertEqual(self.lex_by_id[lex_id]["phrase_en"], item["phrase_en"])
                    world_bridge_ids.append(lex_id)

                    # Zero false world_bridge misclassifications against all 100 clips' en_clean
                    wb_pat = re.compile(rf"\b{re.escape(item['phrase_en'])}\b", re.IGNORECASE)
                    for clean_text in all_clean_texts:
                        self.assertIsNone(
                            wb_pat.search(clean_text),
                            f"{eid}: world_bridge '{item['phrase_en']}' unexpectedly appears in corpus en_clean",
                        )
                else:
                    self.fail(f"Unknown source_type in {eid}: {item['source_type']}")

            # Viral 45s hook validation
            hook = ep["viral_45s_hook"]
            self.assertIsInstance(hook["duration_target_s"], int)
            self.assertGreaterEqual(hook["duration_target_s"], 38)
            self.assertLessEqual(hook["duration_target_s"], 55)
            for key in ("conflict_angle", "hook_line_en", "hook_line_zh", "cta_zh"):
                self.assertTrue(hook[key].strip(), f"{eid} viral_45s_hook.{key} is empty")

        # Complete 24/24 world_bridge deployment without duplication
        self.assertEqual(len(world_bridge_ids), 24)
        self.assertEqual(set(world_bridge_ids), {f"LEX_{i:03d}" for i in range(97, 121)})

    # ------------------------------------------------------------------
    # 9. Cross-File Markdown, Engine DSP/Tag & Unit-Economics Parity
    # ------------------------------------------------------------------
    def test_markdown_parity_and_depth_exceeds_buffett_reference(self) -> None:
        buffett_text = BUFFETT_BIBLE_PATH.read_text(encoding="utf-8")
        self.assertGreater(len(self.show_bible_md.encode("utf-8")), len(buffett_text.encode("utf-8")))
        self.assertGreater(len(self.show_bible_md.splitlines()), len(buffett_text.splitlines()))

        # SHOW_BIBLE.md cast & motif parity
        for role_id, prof in self.registry.roles.items():
            self.assertIn(role_id, self.show_bible_md, f"SHOW_BIBLE missing role {role_id}")
            self.assertIn(prof.voice_id, self.show_bible_md, f"SHOW_BIBLE missing voice_id {prof.voice_id}")
            self.assertIn(prof.accent_code, self.show_bible_md, f"SHOW_BIBLE missing accent_code {prof.accent_code}")
            self.assertIn(
                prof.audition_line,
                self.show_bible_md,
                f"SHOW_BIBLE audition_line out of sync for {role_id}",
            )
            self.assertIn(prof.accent_code, self.accent_manual_md, f"ACCENT_MANUAL missing {prof.accent_code}")
        for motif_id, motif in self.registry.sonic_motifs.items():
            self.assertIn(motif_id, self.show_bible_md, f"SHOW_BIBLE missing motif {motif_id}")
            self.assertIn(
                motif.sfx_prompt,
                self.show_bible_md,
                f"SHOW_BIBLE sfx_prompt out of sync for {motif_id}",
            )

        # SHOW_BIBLE.md §3.2 unit-economics arithmetic parity
        self.assertAlmostEqual(124 * 0.25, 31.0, places=4)
        self.assertAlmostEqual(218 * 0.25, 54.5, places=4)
        self.assertAlmostEqual(3 * 365 * 0.18, 197.1, places=4)
        self.assertAlmostEqual((0.18 - 0.04) / 0.18 * 100.0, 77.7778, places=3)
        for token in (
            "NovaEdge Glass",
            "NovaDock",
            "+\\$31",
            "+\\$54.5",
            "\\$197/台",
            "78%",
            "77.8%",
            "\\$0.04/天",
            "boardroom",
            "inner_monologue",
            "phone_call",
            "studio_warm",
            "dry",
            "vast_hall",
            "memory_echo",
            "170.34",
            "170.20",
            "0.80",
            "atempo",
        ):
            self.assertIn(token, self.show_bible_md, f"SHOW_BIBLE missing anchor '{token}'")
        self.assertNotIn("+\\$52", self.show_bible_md)
        self.assertNotIn("+$52", self.show_bible_md)
        self.assertNotIn("68%", self.show_bible_md)
        self.assertNotIn("68%", json.dumps(self.season_map, ensure_ascii=False))

        # SHOW_BIBLE.md §6.1 FFmpeg DSP filter parity against src/aigc_audio_pipeline/mixer.py
        normalized_bible = self.show_bible_md.replace("\\|", "|")
        for flt in REQUIRED_MIXER_DSP_FILTERS:
            self.assertIn(flt, self.mixer_py_src, f"Expected filter missing from mixer.py: {flt}")
            self.assertIn(flt, normalized_bible, f"SHOW_BIBLE.md §6.1 missing mixer.py filter: {flt}")

        # ACCENT_AND_PROSODY_MANUAL.md §3.2 live tag & prompt parity against drama3_adapter.py
        allowed_tags = set(DRAMA3_TAG_MAP) | set(DRAMA3_POINT_EVENTS)
        table_row_re = re.compile(
            r"^\|\s*`\[([^\]]+)\]`[^|]*\|\s*`(TAG_MAP|POINT)`\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|",
            re.MULTILINE,
        )
        parsed_rows = table_row_re.findall(self.accent_manual_md)
        self.assertEqual(len(parsed_rows), 21, f"Expected 21 core tag rows in §3.2, found {len(parsed_rows)}")
        for tag_name, dict_kind, en_cell, _xml_cell, zh_cell in parsed_rows:
            self.assertIn(tag_name, allowed_tags, f"ACCENT_MANUAL §3.2 unknown tag [{tag_name}]")
            if dict_kind == "TAG_MAP":
                self.assertIn(tag_name, DRAMA3_TAG_MAP)
                self.assertIn(tag_name, BUSINESS_DRAMA_ZH_MICRO_MAP)
                if tag_name != "wryly":
                    self.assertIn(
                        DRAMA3_TAG_MAP[tag_name][0],
                        en_cell,
                        f"ACCENT_MANUAL §3.2 EN prompt mismatch for [{tag_name}]",
                    )
                self.assertIn(
                    BUSINESS_DRAMA_ZH_MICRO_MAP[tag_name][0],
                    zh_cell,
                    f"ACCENT_MANUAL §3.2 ZH micro-prompt mismatch for [{tag_name}]",
                )
            else:
                self.assertIn(tag_name, DRAMA3_POINT_EVENTS)
                self.assertIn(DRAMA3_POINT_EVENTS[tag_name], en_cell)

        # Verify extra documented M1 tags in §3.2 footnote also exist in drama3_adapter.py
        for extra_zh in ("calmly", "rushed", "seriously", "softly", "whispers", "whispering"):
            self.assertIn(extra_zh, BUSINESS_DRAMA_ZH_MICRO_MAP)
            self.assertIn(f"`[{extra_zh}]`", self.accent_manual_md)
        for extra_pt in ("pause", "long pause", "exhales", "gasps", "chuckles"):
            self.assertIn(extra_pt, DRAMA3_POINT_EVENTS)
            self.assertIn(f"`[{extra_pt}]`", self.accent_manual_md)

        for token in (
            "85%",
            "15%",
            "96.0%",
            "4.0%",
            "170.34",
            "170.20",
            "150–185",
            "atempo=0.80",
            "1.8s",
            "[-0.25, -0.05]",
            "lin_chen",
            "核心 21 个",
        ):
            self.assertIn(token, self.accent_manual_md, f"ACCENT_MANUAL missing '{token}'")

        # Full SEASON1_24EP_BLUEPRINT.md parity with season1_24ep_map.json (dossier + Appendix III)
        for ep in self.season_map["episodes"]:
            eid = ep["episode_id"]
            self.assertIn(eid, self.blueprint_md)
            self.assertGreaterEqual(
                self.blueprint_md.count(ep["title_zh"]),
                2,
                f"BLUEPRINT missing dossier or Appendix III title_zh for {eid}: {ep['title_zh']}",
            )
            self.assertGreaterEqual(
                self.blueprint_md.count(ep["title_en"]),
                2,
                f"BLUEPRINT missing dossier or Appendix III title_en for {eid}: {ep['title_en']}",
            )
            self.assertIn(ep["logline_zh"], self.blueprint_md, f"BLUEPRINT logline_zh drift on {eid}")
            self.assertIn(ep["accent_profile"], self.blueprint_md, f"BLUEPRINT accent_profile drift on {eid}")
            self.assertIn(ep["cliffhanger_zh"], self.blueprint_md, f"BLUEPRINT cliffhanger_zh drift on {eid}")

            vh = ep["viral_45s_hook"]
            for key in ("conflict_angle", "hook_line_en", "hook_line_zh", "cta_zh"):
                self.assertIn(
                    vh[key],
                    self.blueprint_md,
                    f"BLUEPRINT viral_45s_hook.{key} drift on {eid}",
                )
            for cid in ep["primary_clip_ids"]:
                self.assertIn(cid, self.blueprint_md, f"BLUEPRINT missing clip_id {cid}")
            for tp in ep["target_phrases"]:
                self.assertIn(tp["phrase_en"], self.blueprint_md, f"BLUEPRINT missing phrase on {eid}")
                if tp.get("lexicon_id"):
                    self.assertIn(tp["lexicon_id"], self.blueprint_md)
                if tp.get("companion_phrase_en"):
                    self.assertIn(tp["companion_phrase_en"], self.blueprint_md)
                if tp.get("companion_lexicon_id"):
                    self.assertIn(tp["companion_lexicon_id"], self.blueprint_md)

    # ------------------------------------------------------------------
    # 10. Full Banned-Cliché Hygiene, 24/24 Uniqueness & Doubled-Word Typo Guard
    # ------------------------------------------------------------------
    def test_zero_banned_cliches_uniqueness_and_typo_hygiene(self) -> None:
        episodes = self.season_map["episodes"]

        # 24/24 uniqueness across all headline, logline, cliffhanger & hook fields
        for label, values in (
            ("title_zh", [e["title_zh"] for e in episodes]),
            ("title_en", [e["title_en"] for e in episodes]),
            ("logline_zh", [e["logline_zh"] for e in episodes]),
            ("cliffhanger_zh", [e["cliffhanger_zh"] for e in episodes]),
            ("hook_line_en", [e["viral_45s_hook"]["hook_line_en"] for e in episodes]),
            ("hook_line_zh", [e["viral_45s_hook"]["hook_line_zh"] for e in episodes]),
        ):
            self.assertEqual(len(set(values)), 24, f"Duplicate values detected in {label}")

        # Full banned-cliché + Shorts-leak + Chinese doubled-word typo scan across structured JSON story fields
        for ep in episodes:
            eid = ep["episode_id"]
            vh = ep["viral_45s_hook"]
            fields_to_check = [
                ("title_zh", ep["title_zh"]),
                ("title_en", ep["title_en"]),
                ("logline_zh", ep["logline_zh"]),
                ("accent_profile", ep["accent_profile"]),
                ("cliffhanger_zh", ep["cliffhanger_zh"]),
                ("viral_45s_hook.conflict_angle", vh["conflict_angle"]),
                ("viral_45s_hook.hook_line_en", vh["hook_line_en"]),
                ("viral_45s_hook.hook_line_zh", vh["hook_line_zh"]),
                ("viral_45s_hook.cta_zh", vh["cta_zh"]),
            ]
            for tp in ep["target_phrases"]:
                fields_to_check.append(("executive_subtext_zh", tp["executive_subtext_zh"]))
                fields_to_check.append(("chinglish_trap", tp["chinglish_trap"]))

            for field_name, value in fields_to_check:
                low = value.lower()
                for banned in BANNED_CLICHES_AND_LEAKS:
                    self.assertNotIn(
                        banned,
                        low,
                        f"Banned phrase '{banned}' leaked into {eid}.{field_name}: {value}",
                    )
                typo_match = CHINESE_DOUBLED_WORD_RE.search(value)
                self.assertIsNone(
                    typo_match,
                    f"Unintended doubled Chinese word '{typo_match.group(0) if typo_match else ''}' "
                    f"in {eid}.{field_name}: {value}",
                )

        # Verify ACCENT_AND_PROSODY_MANUAL.md prose contains zero banned clichés or Shorts leaks
        low_manual = self.accent_manual_md.lower()
        for banned in BANNED_CLICHES_AND_LEAKS:
            self.assertNotIn(
                banned,
                low_manual,
                f"Banned cliché/leak '{banned}' found in ACCENT_AND_PROSODY_MANUAL.md",
            )

        # Verify zero Chinese doubled-word typos across all 3 Markdown docs
        for doc_name, doc_text in (
            ("SHOW_BIBLE.md", self.show_bible_md),
            ("ACCENT_AND_PROSODY_MANUAL.md", self.accent_manual_md),
            ("SEASON1_24EP_BLUEPRINT.md", self.blueprint_md),
        ):
            typo_match = CHINESE_DOUBLED_WORD_RE.search(doc_text)
            self.assertIsNone(
                typo_match,
                f"Unintended doubled Chinese word '{typo_match.group(0) if typo_match else ''}' in {doc_name}",
            )


if __name__ == "__main__":
    unittest.main()
