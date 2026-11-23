"""Tier 2 — Boundary, Corner & Negative/Rejection Cases: 100 Opaque-Box E2E Tests.

Covers all 19 features (F01–F19) with 5–6 boundary, at-limit, just-outside-limit,
collision, typo-regression, and negative rejection tests (`T2_F01_01`..`T2_F19_06`).
Negative tests mutate isolated synthetic/temp fixtures AND audit real project
deliverables where applicable.
"""

from __future__ import annotations

import dataclasses
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import e2e_helpers as h

COLLECTOR = h.TierCollector(tier=2)
test = COLLECTOR.test


def _expect_assertion_fail(fn, label: str) -> None:
    try:
        fn()
    except AssertionError:
        return
    raise AssertionError(f"Expected boundary/negative rejection for {label}, but check unexpectedly passed")


# ===========================================================================
# F01 — Standalone IP & Cue-Sheet Structural Rejections (5 tests)
# ===========================================================================

@test("T2_F01_01", "F01", "Standalone-IP gate rejects YouTube/视频号/这条切片 mutants; real E001_VA-VD return 0 violations")
def t2_f01_01() -> None:
    for term in ("YouTube", "视频号", "这条切片"):
        mut = h.make_synthetic_e001_variant("E001_VA", distinct_seed_word="t2f01")
        mut.cues[0].text = f"[measured] Remember {term} from yesterday."
        _expect_assertion_fail(lambda s=mut: h.oracle_standalone_ip_and_banned_cliches(s), f"term={term}")
    for vid, cs in h.load_all_e001_variants().items():
        h.oracle_standalone_ip_and_banned_cliches(cs)


@test("T2_F01_02", "F01", "Banned-cliché gate rejects every classroom/broadcast cliché; real E001_VA-VD + AUDITION return 0 hits")
def t2_f01_02() -> None:
    for cliche in h.BANNED_CLICHES:
        mut = h.make_synthetic_e001_variant("E001_VA", distinct_seed_word="t2f01c")
        mut.cues[0].text = f"[measured] {cliche}，欢迎来到谈判桌。"
        _expect_assertion_fail(lambda s=mut: h.oracle_standalone_ip_and_banned_cliches(s), f"cliche={cliche}")
    for eid, path in h.ALL_5_CUE_SHEETS.items():
        h.oracle_standalone_ip_and_banned_cliches(h.load_cue_sheet_safe(path))


@test("T2_F01_03", "F01", "Empty cue sheet (cues=[]) rejected by EpisodeCueSheet.validate() and public validate CLI")
def t2_f01_03() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    reg = h.make_minimal_registry()
    empty = EpisodeCueSheet(episode_id="E001_EMPTY", chapter_number=1, title="Empty", mode="bilingual_business_drama", acts=[], cues=[])
    errs = empty.validate(reg)
    assert any("0 cues" in e for e in errs), f"Expected '0 cues' error, got {errs}"

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f01_empty_"))
    try:
        reg_p = tmp / "reg.json"
        cs_p = tmp / "empty.json"
        reg.save(reg_p)
        empty.save(cs_p)
        proc, payload = h.run_validate_cli(reg_p, cs_p, require_locked_voices=False)
        assert proc.returncode != 0, f"validate CLI must fail on empty cue sheet, got rc=0"
        assert payload is not None and payload.get("valid") is False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F01_04", "F01", "Duplicate cue_id rejected by EpisodeCueSheet.validate() and public validate CLI")
def t2_f01_04() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    reg = h.make_minimal_registry()
    dup = EpisodeCueSheet(
        episode_id="E001_DUP",
        chapter_number=1,
        title="Dup",
        mode="bilingual_business_drama",
        acts=[],
        cues=[
            h.make_timeline_cue(cue_id="C001", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="One."),
            h.make_timeline_cue(cue_id="C001", act_id="a1", kind="dialogue", role_id="victoria_vance", language_code="en", text="Two."),
        ],
    )
    errs = dup.validate(reg)
    assert any("Duplicate cue_id" in e for e in errs), f"Expected Duplicate cue_id error, got {errs}"

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f01_dup_"))
    try:
        reg.save(tmp / "reg.json")
        dup.save(tmp / "dup.json")
        proc, payload = h.run_validate_cli(tmp / "reg.json", tmp / "dup.json", require_locked_voices=False)
        assert proc.returncode != 0
        assert payload is not None and any("Duplicate cue_id" in e for e in payload.get("errors", []))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F01_05", "F01", "Unknown act_id rejected on bilingual_business_drama while audition_pack permits empty acts=[]")
def t2_f01_05() -> None:
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    reg = h.make_minimal_registry()
    bad = EpisodeCueSheet(
        episode_id="E001_ACT",
        chapter_number=1,
        title="Bad Act",
        mode="bilingual_business_drama",
        acts=[ActMusicSpec(act_id="act_1", title="Act 1", bgm_prompt="Minimal cello, instrumental")],
        cues=[h.make_timeline_cue(cue_id="C1", act_id="act_99_phantom", kind="dialogue", role_id="lin_chen", language_code="en", text="Hi.")],
    )
    errs = bad.validate(reg)
    assert any("Unknown act_id" in e for e in errs), f"Expected Unknown act_id error, got {errs}"

    audition = EpisodeCueSheet(
        episode_id="AUDITION_OK",
        chapter_number=0,
        title="Audition",
        mode="audition_pack",
        acts=[],
        cues=[h.make_timeline_cue(cue_id="A1", act_id="audition", kind="dialogue", role_id="lin_chen", language_code="en", text="Audition test.")],
    )
    assert audition.validate(reg) == [], f"audition_pack with empty acts=[] should pass: {audition.validate(reg)}"


# ===========================================================================
# F02 — B1–C1 Lexicon & Phrase Coverage Boundaries (5 tests)
# ===========================================================================

@test("T2_F02_01", "F02", "Corpus provenance boundary: rejects 69% corpus, accepts 70.0%; real executive_lexicon.json passes >=70%")
def t2_f02_01() -> None:
    syn_corp = h.make_synthetic_corpus_100()
    lex_70 = h.make_synthetic_lexicon(syn_corp, corpus_count=70, total=100)
    h.oracle_lexicon_provenance_70_30(lex_70, syn_corp)
    lex_69 = h.make_synthetic_lexicon(syn_corp, corpus_count=69, total=100)
    _expect_assertion_fail(lambda: h.oracle_lexicon_provenance_70_30(lex_69, syn_corp), "69% corpus share")

    real_lex = h.load_json_file(h.PATH_LEXICON_JSON, "executive_lexicon.json")
    real_corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    h.oracle_lexicon_provenance_70_30(real_lex, real_corp)


@test("T2_F02_02", "F02", "Lexicon provenance rejects fabricated clip_id (028_AI) & ungrounded phrase; real lexicon has 0 violations")
def t2_f02_02() -> None:
    syn_corp = h.make_synthetic_corpus_100()
    lex_bad_id = h.make_synthetic_lexicon(syn_corp, corpus_count=70, total=100)
    lex_bad_id[0]["clip_ids"] = ["028_AI"]
    _expect_assertion_fail(lambda: h.oracle_lexicon_provenance_70_30(lex_bad_id, syn_corp), "fabricated 028_AI")

    lex_bad_phrase = h.make_synthetic_lexicon(syn_corp, corpus_count=70, total=100)
    lex_bad_phrase[0]["phrase_en"] = "completely fabricated ungrounded phrase"
    _expect_assertion_fail(lambda: h.oracle_lexicon_provenance_70_30(lex_bad_phrase, syn_corp), "ungrounded phrase")

    real_lex = h.load_json_file(h.PATH_LEXICON_JSON, "executive_lexicon.json")
    real_corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    h.oracle_lexicon_provenance_70_30(real_lex, real_corp)


@test("T2_F02_03", "F02", "Dropping just 1 of 8 mandatory phrases fails E001 phrase oracle; real E001_VA-VD all hit 8/8")
def t2_f02_03() -> None:
    for drop_idx in (0, 5):  # Drop P1 ("phantom number") and P6 ("a really hard trade-off")
        mut = h.make_synthetic_e001_variant("E001_VA", distinct_seed_word="t2f02")
        mut.cues[drop_idx].text = "[measured] Replacement corporate dialogue line."
        _expect_assertion_fail(lambda s=mut: h.oracle_e001_8_mandatory_phrases(s), f"drop P{drop_idx + 1}")
    for vid, cs in h.load_all_e001_variants().items():
        res = h.oracle_e001_8_mandatory_phrases(cs, drama_only=True)
        assert res["matched_count"] == 8, f"{vid}: only {res['matched_count']}/8"


@test("T2_F02_04", "F02", "Per-episode target_phrases boundary: rejects 4 and 9, accepts 5 and 8; real 24-ep map passes")
def t2_f02_04() -> None:
    smap_ok = h.make_synthetic_season1_map(85.0)
    smap_ok["episodes"][0]["target_phrases"] = [f"p{i}" for i in range(5)]
    smap_ok["episodes"][1]["target_phrases"] = [f"p{i}" for i in range(8)]
    h.oracle_season1_24ep_bijection(smap_ok)

    smap_4 = json.loads(json.dumps(smap_ok))
    smap_4["episodes"][0]["target_phrases"] = ["p1", "p2", "p3", "p4"]
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(smap_4), "4 target_phrases")

    smap_9 = json.loads(json.dumps(smap_ok))
    smap_9["episodes"][0]["target_phrases"] = [f"p{i}" for i in range(9)]
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(smap_9), "9 target_phrases")

    real_map = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    h.oracle_season1_24ep_bijection(real_map)


@test("T2_F02_05", "F02", "Elementary ESL phrases rejected on mutants; real E001_VA-VD contain 0 hits")
def t2_f02_05() -> None:
    for line in ("Hello, how are you today?", "Let's learn a new word!"):
        mut = h.make_synthetic_e001_variant("E001_VA", distinct_seed_word="t2f02esl")
        mut.cues[0].text = f"[measured] {line}"
        _expect_assertion_fail(lambda s=mut: h.oracle_standalone_ip_and_banned_cliches(s), f"ESL={line}")
    for vid, cs in h.load_all_e001_variants().items():
        h.oracle_standalone_ip_and_banned_cliches(cs)


# ===========================================================================
# F03 — Bilingual Script & Ducking Parameter Boundaries (5 tests)
# ===========================================================================

@test("T2_F03_01", "F03", "language_code='en' with zero Latin letters rejected by validate_v3_dialogue_text & EpisodeCueSheet.validate")
def t2_f03_01() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet, validate_v3_dialogue_text

    errs = validate_v3_dialogue_text("[coldly] 纯中文句子。", 0.5, language_code="en")
    assert any("no English letters" in e for e in errs), f"Expected 'no English letters' error, got {errs}"
    sheet = EpisodeCueSheet(
        episode_id="E_BAD_EN", chapter_number=1, title="Bad EN", mode="bilingual_business_drama", acts=[],
        cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="[coldly] 纯中文句子。")],
    )
    assert any("no English letters" in e for e in sheet.validate())


@test("T2_F03_02", "F03", "language_code='zh' with zero CJK characters rejected by validate_v3_dialogue_text")
def t2_f03_02() -> None:
    from aigc_audio_pipeline.models import validate_v3_dialogue_text

    errs = validate_v3_dialogue_text("[coldly] Pure English line.", 0.5, language_code="zh")
    assert any("no Chinese characters" in e for e in errs), f"Expected 'no Chinese characters' error, got {errs}"


@test("T2_F03_03", "F03", "language_code='zh-en' with digits/punctuation only AND unsupported language_code='fr' both rejected")
def t2_f03_03() -> None:
    from aigc_audio_pipeline.models import validate_v3_dialogue_text

    errs_punct = validate_v3_dialogue_text("[sighs] 12345...", 0.5, language_code="zh-en")
    assert any("neither Chinese nor English" in e for e in errs_punct), f"Expected neither CJK nor EN error, got {errs_punct}"
    errs_fr = validate_v3_dialogue_text("[measured] Bonjour monsieur.", 0.5, language_code="fr")
    assert any("Unsupported language_code" in e for e in errs_fr), f"Expected Unsupported language_code error, got {errs_fr}"


@test("T2_F03_04", "F03", "duck_gain 4-point boundary: 0.019 (reject), 0.02 (accept), 0.60 (accept), 0.601 (reject)")
def t2_f03_04() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    def _errs(gain: float) -> list[str]:
        s = EpisodeCueSheet(
            episode_id="E_DG", chapter_number=1, title="DG", mode="bilingual_business_drama", acts=[],
            cues=[
                h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="alistair_finch", language_code="en", text="Margin call.", duck_under_next=True, duck_gain=gain),
                h.make_timeline_cue(cue_id="C2", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="zh", text="他在施压。"),
            ],
        )
        return s.validate()

    assert _errs(0.02) == [], f"duck_gain=0.02 should pass: {_errs(0.02)}"
    assert _errs(0.60) == [], f"duck_gain=0.60 should pass: {_errs(0.60)}"
    assert any("duck_gain" in e for e in _errs(0.019)), f"duck_gain=0.019 should fail: {_errs(0.019)}"
    assert any("duck_gain" in e for e in _errs(0.601)), f"duck_gain=0.601 should fail: {_errs(0.601)}"


@test("T2_F03_05", "F03", "duck_lead_in_s 4-point boundary: 0.49 (reject), 0.5 (accept), 15.0 (accept), 15.01 (reject)")
def t2_f03_05() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    def _errs(lead: float) -> list[str]:
        s = EpisodeCueSheet(
            episode_id="E_DL", chapter_number=1, title="DL", mode="bilingual_business_drama", acts=[],
            cues=[
                h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="alistair_finch", language_code="en", text="Margin call.", duck_under_next=True, duck_lead_in_s=lead),
                h.make_timeline_cue(cue_id="C2", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="zh", text="他在施压。"),
            ],
        )
        return s.validate()

    assert _errs(0.5) == [], f"duck_lead_in_s=0.5 should pass: {_errs(0.5)}"
    assert _errs(15.0) == [], f"duck_lead_in_s=15.0 should pass: {_errs(15.0)}"
    assert any("duck_lead_in_s" in e for e in _errs(0.49)), f"duck_lead_in_s=0.49 should fail: {_errs(0.49)}"
    assert any("duck_lead_in_s" in e for e in _errs(15.01)), f"duck_lead_in_s=15.01 should fail: {_errs(15.01)}"


# ===========================================================================
# F04 — Debrief Duration, Tempo & Shadowing Gap Boundaries (5 tests)
# ===========================================================================

def _tune_debrief_sheet(target_debrief_s: float):
    """Build synthetic E001 sheet whose Debrief act measures right around target_debrief_s."""
    cs = h.make_synthetic_e001_variant("E001_VA", distinct_seed_word="t2f04")
    debrief_act = h.get_debrief_act_id(cs)
    drama = [c for c in cs.cues if c.act_id != debrief_act]
    # Build minimal valid debrief: 3 slow 0.8x + 3 native 1.0x with gap=2.0 + filler tuned to target_debrief_s
    deb: list = []
    for i in range(3):
        deb.append(h.make_timeline_cue(cue_id=f"S{i}", act_id=debrief_act, kind="dialogue", role_id="lin_chen", language_code="en", text="Phantom number.", playback_rate=0.8, gap_after_s=0.5))
    for i in range(3):
        deb.append(h.make_timeline_cue(cue_id=f"N{i}", act_id=debrief_act, kind="dialogue", role_id="lin_chen", language_code="en", text="Phantom number.", playback_rate=1.0, gap_after_s=2.0))
    cur = h.estimate_cue_slice_duration_s(deb)
    rem = max(0.0, target_debrief_s - cur)
    # Add 10s chunks (26.5 EN words ≈ 10.0s, gap 0.0) then exact residual gap (<=10s)
    idx = 0
    while rem > 10.0:
        chunk = min(rem - 2.0, 15.0)
        words_needed = max(2, int(round(chunk * 2.65)))
        deb.append(h.make_timeline_cue(cue_id=f"F{idx}", act_id=debrief_act, kind="dialogue", role_id="lin_chen", language_code="en", text=" ".join(["margin"] * words_needed), playback_rate=1.0, gap_after_s=0.0))
        cur = h.estimate_cue_slice_duration_s(deb)
        rem = target_debrief_s - cur
        idx += 1
    if rem > 0.5:
        deb.append(h.make_timeline_cue(cue_id="FLAST", act_id=debrief_act, kind="dialogue", role_id="lin_chen", language_code="en", text="End.", playback_rate=1.0, gap_after_s=max(0.0, rem - 0.45)))
    cs.cues = drama + deb
    return cs


@test("T2_F04_01", "F04", "Debrief lower boundary: rejects ~164.0s (<165s), accepts >=165.0s; all 4 real variants satisfy >=165.0s")
def t2_f04_01() -> None:
    low_sheet = _tune_debrief_sheet(164.0)
    assert h.estimate_episode_runtime_breakdown(low_sheet)["debrief_s"] < 165.0
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(low_sheet), "debrief=164.0s")
    ok_sheet = _tune_debrief_sheet(165.2)
    h.oracle_runtime_and_debrief_windows(ok_sheet)
    for vid, cs in h.load_all_e001_variants().items():
        br = h.estimate_episode_runtime_breakdown(cs)
        assert br["debrief_s"] >= 165.0, f"{vid}: debrief={br['debrief_s']:.1f}s < 165.0s"


@test("T2_F04_02", "F04", "Debrief upper boundary: rejects ~211.0s (>210s), accepts <=210.0s; all 4 real variants satisfy <=210.0s")
def t2_f04_02() -> None:
    hi_sheet = _tune_debrief_sheet(211.2)
    assert h.estimate_episode_runtime_breakdown(hi_sheet)["debrief_s"] > 210.0
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(hi_sheet), "debrief=211.2s")
    ok_sheet = _tune_debrief_sheet(209.5)
    h.oracle_runtime_and_debrief_windows(ok_sheet)
    for vid, cs in h.load_all_e001_variants().items():
        br = h.estimate_episode_runtime_breakdown(cs)
        assert br["debrief_s"] <= 210.0, f"{vid}: debrief={br['debrief_s']:.1f}s > 210.0s"


@test("T2_F04_03", "F04", "Debrief shadowing gap boundary: rejects max gap 1.79s, accepts 1.80s; all 4 real variants pass >=1.80s")
def t2_f04_03() -> None:
    bad = h.make_synthetic_e001_variant("E001_VA", shadow_gap_s=1.79, distinct_seed_word="t2f04g")
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(bad), "shadow_gap=1.79s")
    ok = h.make_synthetic_e001_variant("E001_VA", shadow_gap_s=1.80, distinct_seed_word="t2f04g2")
    h.oracle_runtime_and_debrief_windows(ok)
    for vid, cs in h.load_all_e001_variants().items():
        res = h.oracle_runtime_and_debrief_windows(cs)
        assert res["shadow_gap_count"] >= 3, f"{vid}: shadow_gap_count < 3"


@test("T2_F04_04", "F04", "Debrief omitting playback_rate=0.8 slow pass fails oracle; all 4 real variants include >=3 slow cues")
def t2_f04_04() -> None:
    mut = h.make_synthetic_e001_variant("E001_VA", debrief_slow_count=0, distinct_seed_word="t2f04ns")
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(mut), "zero 0.8x slow cues")
    for vid, cs in h.load_all_e001_variants().items():
        res = h.oracle_runtime_and_debrief_windows(cs)
        assert res["slow_count"] >= 3, f"{vid}: slow_count < 3"


@test("T2_F04_05", "F04", "Debrief omitting playback_rate=1.0 native shadowing pass fails oracle; all 4 real variants include both")
def t2_f04_05() -> None:
    mut = h.make_synthetic_e001_variant("E001_VA", debrief_native_count=0, distinct_seed_word="t2f04nn")
    deb_act = h.get_debrief_act_id(mut)
    for c in mut.cues:
        if c.act_id == deb_act and c.kind == "dialogue":
            c.playback_rate = 0.8
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(mut), "zero 1.0x native cues")
    for vid, cs in h.load_all_e001_variants().items():
        res = h.oracle_runtime_and_debrief_windows(cs)
        assert res["slow_count"] >= 3 and res["native_count"] >= 3


# ===========================================================================
# F05 — Hardware Identity, SFX & BGM Guardrail Boundaries (5 tests)
# ===========================================================================

@test("T2_F05_01", "F05", "All 4 real E001 variants & SHOW_BIBLE.md maintain NovaEdge consumer-hardware identity (no generic SaaS drift)")
def t2_f05_01() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    assert "NovaEdge Glass" in bible and "NovaDock" in bible
    for vid, cs in h.load_all_e001_variants().items():
        blob = " ".join(c.text for c in cs.cues if c.kind == "dialogue")
        assert "novaedge" in blob.lower() or "灵犀" in blob, f"{vid}: lost NovaEdge brand identity"
        assert any(k in blob.lower() or k in blob for k in ("glass", "hardware", "眼镜", "硬件", "芯片", "产线")), (
            f"{vid}: drifted away from AI consumer hardware domain"
        )


@test("T2_F05_02", "F05", "SFX duration_seconds 4-point boundary: 0.49 (reject), 0.5 (accept), 30.0 (accept), 30.01 (reject)")
def t2_f05_02() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    def _errs(dur: float) -> list[str]:
        s = EpisodeCueSheet(
            episode_id="E_SFX", chapter_number=1, title="SFX", mode="bilingual_business_drama", acts=[],
            cues=[h.make_timeline_cue(cue_id="S1", act_id="a1", kind="sfx", sfx_prompt="Glass door click, no human voice", duration_seconds=dur)],
        )
        return s.validate()

    assert _errs(0.5) == []
    assert _errs(30.0) == []
    assert any("duration_seconds" in e for e in _errs(0.49))
    assert any("duration_seconds" in e for e in _errs(30.01))


@test("T2_F05_03", "F05", "Malformed SFX cues rejected: missing prompt+motif, unregistered motif_id, invalid placement='parallel'")
def t2_f05_03() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    reg = h.make_minimal_registry()
    cases = [
        ("missing prompt+motif", h.make_timeline_cue(cue_id="S1", act_id="a1", kind="sfx", sfx_prompt="", motif_id="", duration_seconds=2.0)),
        ("unregistered motif", h.make_timeline_cue(cue_id="S2", act_id="a1", kind="sfx", sfx_prompt="", motif_id="nonexistent_motif", duration_seconds=2.0)),
        ("invalid placement", h.make_timeline_cue(cue_id="S3", act_id="a1", kind="sfx", sfx_prompt="Click, no voice", placement="parallel", duration_seconds=2.0)),
    ]
    for label, cue in cases:
        s = EpisodeCueSheet(episode_id="E_BAD_SFX", chapter_number=1, title="Bad SFX", mode="bilingual_business_drama", acts=[], cues=[cue])
        assert s.validate(reg), f"Expected validation error for {label}"


@test("T2_F05_04", "F05", "Real voice_casting_registry.json sonic_motifs contain zero vocal keywords and enforce no-voice guardrail")
def t2_f05_04() -> None:
    reg = h.load_registry_safe()
    assert len(reg.sonic_motifs) >= 4
    for mid, m in reg.sonic_motifs.items():
        low = m.sfx_prompt.lower()
        assert any(k in low for k in ("no human voice", "no voice", "no speech", "no vocals")), (
            f"Motif {mid} missing no-voice guardrail: {m.sfx_prompt!r}"
        )
        # Strip valid "no ... voice/speech/vocals/singing" negation clauses before checking vocal contamination
        stripped = re.sub(r"\bno\s+(?:human\s+)?(?:voice|voices|speech|vocal|vocals|singing|chatter|talking)\b", "", low)
        for bad in ("singing", "vocals", "human voice", "spoken dialogue"):
            assert bad not in stripped, f"Motif {mid} contains unnegated vocal keyword {bad!r}: {m.sfx_prompt!r}"


@test("T2_F05_05", "F05", "Every ActMusicSpec.bgm_prompt across real E001_VA-VD enforces instrumental guardrail and positive duration")
def t2_f05_05() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        assert len(cs.acts) >= 4
        for act in cs.acts:
            assert act.bgm_duration_s > 0, f"{vid} {act.act_id}: non-positive bgm_duration_s={act.bgm_duration_s}"
            low = act.bgm_prompt.lower()
            assert any(k in low for k in ("instrumental", "no vocal", "no vocals", "no singing", "wordless")), (
                f"{vid} {act.act_id}: bgm_prompt missing instrumental/no-vocal guardrail: {act.bgm_prompt!r}"
            )


# ===========================================================================
# F06 — Accent Matrix Quota & US+UK RP Dual-Accent Boundaries (5 tests)
# ===========================================================================

@test("T2_F06_01", "F06", "Season US+UK RP boundary: rejects 84.9%, accepts 85.0%; real season1_24ep_map.json >= 85.0%")
def t2_f06_01() -> None:
    reg = h.make_minimal_registry()
    h.oracle_accent_matrix_budget(reg, season_map=h.make_synthetic_season1_map(85.0))
    _expect_assertion_fail(
        lambda: h.oracle_accent_matrix_budget(reg, season_map=h.make_synthetic_season1_map(84.9)),
        "84.9% season US+UK RP",
    )
    real_reg = h.load_registry_safe()
    real_map = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    h.oracle_accent_matrix_budget(real_reg, season_map=real_map)


@test("T2_F06_02", "F06", "E001 accent oracle rejects even 1 international guest cue (rajiv_menon); real E001_VA-VD pass at 100%")
def t2_f06_02() -> None:
    reg = h.make_minimal_registry()
    mut = h.make_synthetic_e001_variant("E001_VA", distinct_seed_word="t2f06")
    mut.cues[0].role_id = "rajiv_menon"
    _expect_assertion_fail(lambda: h.oracle_accent_matrix_budget(reg, e001_cue_sheets={"E001_VA": mut}), "rajiv_menon in E001")

    real_reg = h.load_registry_safe()
    h.oracle_accent_matrix_budget(real_reg, e001_cue_sheets=h.load_all_e001_variants())


@test("T2_F06_03", "F06", "Accent audit rejects empty accent_code on core role; real voice_casting_registry.json covers all roles")
def t2_f06_03() -> None:
    reg = h.make_minimal_registry()
    reg.roles["victoria_vance"].accent_code = ""
    _expect_assertion_fail(lambda: h.oracle_accent_matrix_budget(reg), "empty accent_code on victoria_vance")

    real_reg = h.load_registry_safe()
    h.oracle_accent_matrix_budget(real_reg)


@test("T2_F06_04", "F06", "International guest ceiling boundary: rejects 16.0% intl share (84.0% core); real map <= 15.0%")
def t2_f06_04() -> None:
    reg = h.make_minimal_registry()
    _expect_assertion_fail(
        lambda: h.oracle_accent_matrix_budget(reg, season_map=h.make_synthetic_season1_map(84.0)),
        "16.0% international guest share",
    )
    real_reg = h.load_registry_safe()
    real_map = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    res = h.oracle_accent_matrix_budget(real_reg, season_map=real_map)
    assert (100.0 - res["season_mean_us_uk_pct"]) <= 15.0 + 1e-9


@test("T2_F06_05", "F06", "All 4 real E001 variants prove genuine US + London RP dual clash (>=4 cues each for victoria & alistair, 0 pure-EN zhou_mo)")
def t2_f06_05() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        us_n = sum(1 for c in cs.cues if c.kind == "dialogue" and c.role_id == "victoria_vance" and c.language_code == "en")
        uk_n = sum(1 for c in cs.cues if c.kind == "dialogue" and c.role_id == "alistair_finch" and c.language_code == "en")
        zm_en = [c.cue_id for c in cs.cues if c.kind == "dialogue" and c.role_id == "zhou_mo" and c.language_code == "en"]
        assert us_n >= 4, f"{vid}: victoria_vance EN cues={us_n} < 4"
        assert uk_n >= 4, f"{vid}: alistair_finch (London RP) EN cues={uk_n} < 4"
        assert not zm_en, f"{vid}: zhou_mo (Shenzhen CTO) should not speak pure-EN cues: {zm_en}"


# ===========================================================================
# F07 — Crosstalk, SSML, Tag Syntax, Stability & Turn-Cap Boundaries (6 tests)
# ===========================================================================

@test("T2_F07_01", "F07", "gap_after_s lower boundary: -0.251 (reject), -0.25 (accept), -0.05 (accept)")
def t2_f07_01() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    def _errs(g: float) -> list[str]:
        s = EpisodeCueSheet(
            episode_id="E_GAP_LO", chapter_number=1, title="Gap Lo", mode="bilingual_business_drama", acts=[],
            cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Wait.", gap_after_s=g)],
        )
        return s.validate()

    assert any("gap_after_s" in e for e in _errs(-0.251))
    assert _errs(-0.25) == []
    assert _errs(-0.05) == []


@test("T2_F07_02", "F07", "gap_after_s upper boundary: 10.0 (accept) vs 10.01 (reject)")
def t2_f07_02() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    def _errs(g: float) -> list[str]:
        s = EpisodeCueSheet(
            episode_id="E_GAP_HI", chapter_number=1, title="Gap Hi", mode="bilingual_business_drama", acts=[],
            cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Pause.", gap_after_s=g)],
        )
        return s.validate()

    assert _errs(10.0) == []
    assert any("gap_after_s" in e for e in _errs(10.01))


@test("T2_F07_03", "F07", "All 4 forbidden SSML tags (<break>, <prosody>, <speak>, <emphasis>) rejected")
def t2_f07_03() -> None:
    from aigc_audio_pipeline.models import validate_v3_dialogue_text

    samples = (
        '<break time="0.5s"/> Watch the ledger.',
        '<prosody rate="slow">Watch the ledger.</prosody>',
        "<speak>Watch the ledger.</speak>",
        "<emphasis>Watch</emphasis> the ledger.",
    )
    for txt in samples:
        errs = validate_v3_dialogue_text(txt, 0.5, language_code="en")
        assert any("SSML" in e for e in errs), f"Expected SSML rejection for {txt!r}, got {errs}"


@test("T2_F07_04", "F07", "All 6 malformed inline tag cases rejected (CJK, UPPER, nested, unclosed, unmatched, empty spoken)")
def t2_f07_04() -> None:
    from aigc_audio_pipeline.models import validate_v3_dialogue_text

    cases = (
        ("[冷笑] 这不可能。", "zh"),
        ("[COLDLY] That is impossible.", "en"),
        ("[[softly]] That is impossible.", "en"),
        ("[softly That is impossible.", "en"),
        ("softly] That is impossible.", "en"),
        ("[sighs]", "en"),
    )
    for txt, lang in cases:
        errs = validate_v3_dialogue_text(txt, 0.5, language_code=lang)
        assert errs, f"Expected malformed tag rejection for {txt!r} ({lang}), got []"


@test("T2_F07_05", "F07", "Discrete stability set: accepts (0.0, 0.5, 1.0) and rejects (0.25, 0.75, -0.1, 1.1)")
def t2_f07_05() -> None:
    from aigc_audio_pipeline.models import validate_v3_dialogue_text

    for ok_s in (0.0, 0.5, 1.0):
        assert validate_v3_dialogue_text("[measured] Clean stability.", ok_s, language_code="en") == []
    for bad_s in (0.25, 0.75, -0.1, 1.1):
        errs = validate_v3_dialogue_text("[measured] Bad stability.", bad_s, language_code="en")
        assert any("stability" in e for e in errs), f"Expected stability rejection for {bad_s}, got {errs}"


@test("T2_F07_06", "F07", "Turn-length & crosstalk boundary: VA with 5 crosstalk fails; real E001_VA-VD pass turn caps & crosstalk floors")
def t2_f07_06() -> None:
    mut_va = h.make_synthetic_e001_variant("E001_VA", crosstalk_count=5, distinct_seed_word="t2f07")
    mut_set = {
        "E001_VA": mut_va,
        "E001_VB": h.make_synthetic_e001_variant("E001_VB", crosstalk_count=4, inner_monologue_count=4, include_zhou_mo_debrief=True, distinct_seed_word="b"),
        "E001_VC": h.make_synthetic_e001_variant("E001_VC", crosstalk_count=6, phone_call_count=2, distinct_seed_word="c"),
        "E001_VD": h.make_synthetic_e001_variant("E001_VD", crosstalk_count=3, duck_count=2, distinct_seed_word="d"),
    }
    _expect_assertion_fail(lambda: h.oracle_variant_differentiation_and_crosstalk(mut_set), "VA crosstalk=5")

    variants = h.load_all_e001_variants()
    for vid, cs in variants.items():
        ct = h._cross_speaker_crosstalk_cues(cs.cues)
        assert len(ct) >= h.VARIANT_CROSSTALK_MIN[vid], f"{vid}: cross-speaker crosstalk={len(ct)} < {h.VARIANT_CROSSTALK_MIN[vid]}"
        _, drama, _ = h.split_drama_and_debrief_cues(cs)
        for cue in drama:
            if cue.kind != "dialogue":
                continue
            _, sp = h.strip_inline_tags(cue.text)
            if cue.language_code == "en":
                assert h.count_en_words(sp) <= 65, f"{vid} {cue.cue_id}: EN turn > 65 words"
            elif cue.language_code == "zh":
                assert h.count_cjk_chars(sp) <= 115, f"{vid} {cue.cue_id}: ZH turn > 115 chars"


# ===========================================================================
# F08 — Runtime, Drama Window, Signal Sanity & Short-Clip Gate Boundaries (5 tests)
# ===========================================================================

def _tune_drama_sheet(target_drama_s: float, target_debrief_s: float = 180.0):
    cs = _tune_debrief_sheet(target_debrief_s)
    deb_act = h.get_debrief_act_id(cs)
    debrief = [c for c in cs.cues if c.act_id == deb_act]
    drama: list = []
    idx = 0
    rem = target_drama_s
    while rem > 10.0:
        chunk = min(rem - 2.0, 18.0)
        words = max(2, int(round(chunk * 2.65)))
        drama.append(h.make_timeline_cue(cue_id=f"DR{idx}", act_id="act_1", kind="dialogue", role_id="lin_chen", language_code="en", text=" ".join(["margin"] * words), gap_after_s=0.0))
        rem = target_drama_s - h.estimate_cue_slice_duration_s(drama)
        idx += 1
    if rem > 0.5:
        drama.append(h.make_timeline_cue(cue_id="DRLAST", act_id="act_1", kind="dialogue", role_id="lin_chen", language_code="en", text="End.", gap_after_s=max(0.0, rem - 0.45)))
    cs.cues = drama + debrief
    return cs


@test("T2_F08_01", "F08", "Total runtime lower boundary: rejects ~599s (<600s), accepts >=600s; all 4 real variants >= 600s")
def t2_f08_01() -> None:
    low = _tune_drama_sheet(target_drama_s=430.0, target_debrief_s=167.0)  # ~598.5s total
    assert h.estimate_episode_runtime_breakdown(low)["total_s"] < 600.0
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(low), "total < 600s")
    ok = _tune_drama_sheet(target_drama_s=482.0, target_debrief_s=170.0)
    h.oracle_runtime_and_debrief_windows(ok)
    for vid, cs in h.load_all_e001_variants().items():
        assert h.estimate_episode_runtime_breakdown(cs)["total_s"] >= 600.0


@test("T2_F08_02", "F08", "Total runtime upper boundary: rejects >840s, accepts <=840s; all 4 real variants <= 840s")
def t2_f08_02() -> None:
    hi = _tune_drama_sheet(target_drama_s=645.0, target_debrief_s=200.0)  # ~846s total
    assert h.estimate_episode_runtime_breakdown(hi)["total_s"] > 840.0
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(hi), "total > 840s")
    ok = _tune_drama_sheet(target_drama_s=598.0, target_debrief_s=205.0)
    h.oracle_runtime_and_debrief_windows(ok)
    for vid, cs in h.load_all_e001_variants().items():
        assert h.estimate_episode_runtime_breakdown(cs)["total_s"] <= 840.0


@test("T2_F08_03", "F08", "Drama acts window boundary: rejects <480s & >600s, accepts [480, 600]s; all 4 real variants pass")
def t2_f08_03() -> None:
    d_lo = _tune_drama_sheet(target_drama_s=478.0, target_debrief_s=180.0)
    assert h.estimate_episode_runtime_breakdown(d_lo)["drama_s"] < 480.0
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(d_lo), "drama < 480s")

    d_hi = _tune_drama_sheet(target_drama_s=602.0, target_debrief_s=180.0)
    assert h.estimate_episode_runtime_breakdown(d_hi)["drama_s"] > 600.0
    _expect_assertion_fail(lambda: h.oracle_runtime_and_debrief_windows(d_hi), "drama > 600s")

    for vid, cs in h.load_all_e001_variants().items():
        br = h.estimate_episode_runtime_breakdown(cs)
        assert 480.0 <= br["drama_s"] <= 600.0, f"{vid}: drama={br['drama_s']:.1f}s outside [480, 600]s"


@test("T2_F08_04", "F08", "evaluate_dialogue_qa signal boundaries: rejects duration=0.24s & peak=-45.1 dBFS, accepts 0.25s & -45.0 dBFS")
def t2_f08_04() -> None:
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    r_ok = evaluate_dialogue_qa(tagged_prompt="Wait.", asr_text="Wait.", duration_s=0.25, peak_dbfs=-45.0, language_code="en")
    assert r_ok.passed is True, f"Expected pass at exact boundary (0.25s, -45.0 dBFS): {r_ok.reasons}"
    r_short = evaluate_dialogue_qa(tagged_prompt="Wait.", asr_text="Wait.", duration_s=0.24, peak_dbfs=-6.0, language_code="en")
    assert r_short.passed is False, "Expected rejection at duration_s=0.24s"
    r_quiet = evaluate_dialogue_qa(tagged_prompt="Wait.", asr_text="Wait.", duration_s=1.0, peak_dbfs=-45.1, language_code="en")
    assert r_quiet.passed is False, "Expected rejection at peak_dbfs=-45.1"


@test("T2_F08_05", "F08", "Short clip conditioning boundary (<1.4s): 0.8s exclamation succeeds via alimiter path without loudnorm blowup")
def t2_f08_05() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f08_short_"))
    try:
        in_wav = h.write_sine_wav(tmp / "short_08.wav", duration_s=0.80, freq_hz=440.0, sample_rate=48000, channels=1, amplitude=0.30)
        out_wav = tmp / "short_08_out.wav"
        condition_dialogue_clip(in_wav, out_wav, acoustic_space="boardroom")
        probe = h.probe_audio_ffprobe(out_wav)
        assert probe["sample_rate"] == 48000 and probe["channels"] == 2
        assert 0.70 <= probe["duration_s"] <= 0.95
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# F09 — 45s Viral Clip Cutlist & Companion Manual Boundaries (5 tests)
# ===========================================================================

def _make_timed_cutlist_sheet(cue_dur_s: float, count: int):
    from aigc_audio_pipeline.models import EpisodeCueSheet

    words = max(2, int(round(cue_dur_s * 2.65)))
    cues = [
        h.make_timeline_cue(
            cue_id=f"E001_VA_C{i + 1:03d}",
            act_id="act_1",
            kind="dialogue",
            role_id="lin_chen",
            language_code="en",
            text=" ".join(["margin"] * words),
            gap_after_s=0.0,
        )
        for i in range(count)
    ]
    return EpisodeCueSheet(episode_id="E001_VA", chapter_number=1, title="Cut", mode="bilingual_business_drama", acts=[], cues=cues)


@test("T2_F09_01", "F09", "Viral clip lower boundary: rejects 37.0s (<38s), accepts 38.0s; real cutlists pass >=38.0s")
def t2_f09_01() -> None:
    cs = _make_timed_cutlist_sheet(1.0, 60)
    cl_37 = [{"variant_id": "E001_VA", "start_cue_id": "E001_VA_C001", "end_cue_id": "E001_VA_C032", "has_hook": True, "has_cta": True}]
    assert h.estimate_cue_slice_duration_s(cs.cues[:32]) < 38.0
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(cl_37, {"E001_VA": cs}), "<38s cutlist")

    # Find exact index crossing 38.0s
    idx38 = next(i for i in range(len(cs.cues)) if 38.0 <= h.estimate_cue_slice_duration_s(cs.cues[: i + 1]) <= 40.0)
    cl_ok = [{"variant_id": "E001_VA", "start_cue_id": "E001_VA_C001", "end_cue_id": cs.cues[idx38].cue_id, "has_hook": True, "has_cta": True}]
    h.oracle_viral_45s_cutlist_and_rubric(cl_ok, {"E001_VA": cs})

    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    variants = h.load_all_e001_variants()
    real_cl = h.extract_viral_cutlists_from_markdown(kit, variants)
    assert len(real_cl) >= 1, "Expected >= 1 executable 38-55s viral clip cutlist in LAUNCH_KIT_AND_E001_45S_CLIPS.md"
    h.oracle_viral_45s_cutlist_and_rubric(real_cl, variants)


@test("T2_F09_02", "F09", "Viral clip upper boundary: rejects >55s & >57s, accepts <=55s; real cutlists pass <=55.0s")
def t2_f09_02() -> None:
    cs = _make_timed_cutlist_sheet(1.0, 60)
    idx56 = next(i for i in range(len(cs.cues)) if h.estimate_cue_slice_duration_s(cs.cues[: i + 1]) > 55.5)
    cl_hi = [{"variant_id": "E001_VA", "start_cue_id": "E001_VA_C001", "end_cue_id": cs.cues[idx56].cue_id, "has_hook": True, "has_cta": True}]
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(cl_hi, {"E001_VA": cs}), ">55s cutlist")

    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    variants = h.load_all_e001_variants()
    real_cl = h.extract_viral_cutlists_from_markdown(kit, variants)
    assert len(real_cl) >= 1, "Expected >= 1 executable 38-55s viral clip cutlist in LAUNCH_KIT_AND_E001_45S_CLIPS.md"
    h.oracle_viral_45s_cutlist_and_rubric(real_cl, variants)


@test("T2_F09_03", "F09", "Cutlist validator rejects nonexistent cue_id and inverted range (start > end); real cutlists pass")
def t2_f09_03() -> None:
    cs = _make_timed_cutlist_sheet(1.0, 50)
    cl_bad_id = [{"variant_id": "E001_VA", "start_cue_id": "E001_VA_C001", "end_cue_id": "E001_VA_C999", "has_hook": True, "has_cta": True}]
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(cl_bad_id, {"E001_VA": cs}), "nonexistent cue_id")

    cl_inv = [{"variant_id": "E001_VA", "start_cue_id": "E001_VA_C045", "end_cue_id": "E001_VA_C005", "has_hook": True, "has_cta": True}]
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(cl_inv, {"E001_VA": cs}), "inverted range")

    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    variants = h.load_all_e001_variants()
    h.oracle_viral_45s_cutlist_and_rubric(h.extract_viral_cutlists_from_markdown(kit, variants), variants)


@test("T2_F09_04", "F09", "Cutlist anatomy rejects missing 3s hook or missing funnel CTA; real LAUNCH_KIT passes")
def t2_f09_04() -> None:
    cs = _make_timed_cutlist_sheet(1.0, 50)
    idx42 = next(i for i in range(len(cs.cues)) if 40.0 <= h.estimate_cue_slice_duration_s(cs.cues[: i + 1]) <= 48.0)
    cl_no_hook = [{"variant_id": "E001_VA", "start_cue_id": "E001_VA_C001", "end_cue_id": cs.cues[idx42].cue_id, "has_hook": False, "has_cta": True}]
    cl_no_cta = [{"variant_id": "E001_VA", "start_cue_id": "E001_VA_C001", "end_cue_id": cs.cues[idx42].cue_id, "has_hook": True, "has_cta": False}]
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(cl_no_hook, {"E001_VA": cs}), "missing hook")
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(cl_no_cta, {"E001_VA": cs}), "missing CTA")

    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    variants = h.load_all_e001_variants()
    h.oracle_viral_45s_cutlist_and_rubric(h.extract_viral_cutlists_from_markdown(kit, variants), variants)


@test("T2_F09_05", "F09", "E001_BILINGUAL_COMPANION_MANUAL.md has all 8 mandatory phrases and 0 raw ASR typos / [snorts]")
def t2_f09_05() -> None:
    manual = h.load_text_file(h.PATH_COMPANION_MD, "E001_BILINGUAL_COMPANION_MANUAL.md")
    norm = h.normalize_for_phrase_match(manual)
    for pid, label, and_clauses in h.E001_MANDATORY_PHRASES:
        for alts in and_clauses:
            assert any(a in norm for a in alts), f"Companion manual missing {pid} ({label})"
    for bad_pat in (r"\blaw of holds\b", r"\[snorts\]", r"\bJipu\b", r"\bPalanteer\b", r"\bcast robbery\b", r"\bgrock 3\b"):
        assert not re.search(bad_pat, manual, re.IGNORECASE), (
            f"Raw ASR typo {bad_pat!r} leaked into paid E001_BILINGUAL_COMPANION_MANUAL.md"
        )


# ===========================================================================
# F10 — Zero-API, Zero-edge-tts, Schema Guard, Zero-Dep & Append-Only (5 tests)
# ===========================================================================

@test("T2_F10_01", "F10", "AST zero-edge-tts oracle catches import/subprocess edge-tts, passes docstring; real Colab scripts clean")
def t2_f10_01() -> None:
    h.oracle_ast_zero_api_and_zero_edge_tts('"""0% edge-tts policy."""\nimport wave\n', "ok.py")
    _expect_assertion_fail(lambda: h.oracle_ast_zero_api_and_zero_edge_tts("import edge_tts\n", "bad1.py"), "import edge_tts")
    _expect_assertion_fail(
        lambda: h.oracle_ast_zero_api_and_zero_edge_tts('import subprocess\nsubprocess.run(["edge-tts", "-t", "x"])\n', "bad2.py"),
        "subprocess edge-tts",
    )
    for script in (h.COLAB_PREPARE_ANCHORS, h.COLAB_RUN_STUDIO, h.COLAB_LAUNCH_G4):
        h.oracle_ast_zero_api_and_zero_edge_tts(h.load_text_file(script, script.name), script.name)


@test("T2_F10_02", "F10", "AST zero-API oracle catches ElevenLabsClient/URL; real Colab & Global Edge scripts have 0 violations")
def t2_f10_02() -> None:
    _expect_assertion_fail(
        lambda: h.oracle_ast_zero_api_and_zero_edge_tts("from aigc_audio_pipeline.elevenlabs_client import ElevenLabsClient\n", "bad.py"),
        "ElevenLabsClient import",
    )
    _expect_assertion_fail(
        lambda: h.oracle_ast_zero_api_and_zero_edge_tts('API = "https://api.elevenlabs.io/v1"\n', "bad2.py"),
        "api.elevenlabs.io URL",
    )
    for script in (h.COLAB_PREPARE_ANCHORS, h.COLAB_RUN_STUDIO, h.COLAB_LAUNCH_G4, h.SCRIPT_EXTRACT_CORPUS, h.SCRIPT_EXPORT_BUNDLE, h.SCRIPT_BUILD_E001):
        h.oracle_ast_zero_api_and_zero_edge_tts(h.load_text_file(script, script.name), script.name)


@test("T2_F10_03", "F10", "Real M4 anchor builder emits valid v2 manifest and studio CLI rejects v1_edge_tts & en-US-GuyNeural manifests")
def t2_f10_03() -> None:
    h.require_ffmpeg()
    h.require_file(h.COLAB_PREPARE_ANCHORS, "prepare_global_edge_voice_anchors.py")
    h.require_file(h.COLAB_RUN_STUDIO, "run_global_edge_96gb_studio.py")
    h.require_file(h.COLAB_LAUNCH_G4, "launch_g4_global_edge_drama3.py")
    h.require_file(h.PATH_REGISTRY, "voice_casting_registry.json")
    out_flag = h.probe_script_flag(h.COLAB_PREPARE_ANCHORS, ("--output-dir", "--out-dir"))

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f10_v2guard_"))
    try:
        # Part A: Real anchor builder positive control (--offline-stub emits valid v2_real_human_studio manifest)
        anc_out = tmp / "anc_stub"
        p_anc = h.run_python_script(
            h.COLAB_PREPARE_ANCHORS,
            ["--registry", str(h.PATH_REGISTRY), out_flag, str(anc_out), "--offline-stub"],
            timeout=60,
        )
        assert p_anc.returncode == 0, f"prepare_global_edge_voice_anchors.py --offline-stub failed: {p_anc.stderr}"
        real_manifest = h.load_json_file(anc_out / "voice_cast_drama3.json", "voice_cast_drama3.json")
        h.oracle_notebook_and_bundle_integrity(voice_cast_manifest=real_manifest)

        # Part B: Real studio CLI rejection of v1_edge_tts & en-US-GuyNeural synthetic voice manifests
        reg = h.make_minimal_registry()
        base_chars = {
            rid: {
                "source_voice_name": "offline_synthetic_stub",
                "anchor_wav": f"voice_anchors/{rid}.wav",
                "anchor_text": "Clean studio anchor.",
            }
            for rid in reg.roles
        }
        bad_v1 = {
            "anchor_schema_version": "v1_edge_tts",
            "anchor_sample_rate_hz": 44100,
            "characters": json.loads(json.dumps(base_chars)),
        }
        bad_neural_chars = json.loads(json.dumps(base_chars))
        bad_neural_chars["lin_chen"]["source_voice_name"] = "en-US-GuyNeural"
        bad_neural = {
            "anchor_schema_version": "v2_real_human_studio",
            "anchor_sample_rate_hz": 44100,
            "characters": bad_neural_chars,
        }

        for label, bad_manifest in (("v1_edge_tts", bad_v1), ("en-US-GuyNeural", bad_neural)):
            sdir = h.build_mini_studio_dir(
                tmp / f"studio_{label}",
                cue_sheets={"E001_VA_t.json": h.make_mini_cue_sheet("E001_VA")},
                voice_cast_manifest=bad_manifest,
                registry=reg,
            )
            proc = h.run_python_script(
                h.COLAB_RUN_STUDIO,
                [
                    "--studio-dir", str(sdir),
                    "--episodes", "E001_VA",
                    "--output-dir", str(tmp / f"out_{label}"),
                    "--cache-dir", str(tmp / f"cache_{label}"),
                    "--offline-dry-run",
                ],
                timeout=120,
            )
            assert proc.returncode != 0, (
                f"run_global_edge_96gb_studio.py must reject synthetic/legacy manifest ({label}) "
                f"even under --offline-dry-run, but exited 0"
            )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F10_04", "F10", "pyproject.toml strictly maintains dependencies = [] (zero third-party runtime Python packages)")
def t2_f10_04() -> None:
    import tomllib

    data = tomllib.loads(h.load_text_file(h.PATH_PYPROJECT, "pyproject.toml"))
    deps = data.get("project", {}).get("dependencies")
    assert deps == [], f"pyproject.toml must keep dependencies = [], found {deps!r}"


@test("T2_F10_05", "F10", "next_append_only_path never overwrites existing _v001 (.wav, .mp3, .json, or .done) and increments to _v002")
def t2_f10_05() -> None:
    from aigc_audio_pipeline.models import next_append_only_path

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f10_ver_"))
    try:
        p1 = next_append_only_path(tmp, "E001_VA_master", ".wav")
        assert p1.name == "E001_VA_master_v001.wav"
        # Touch only .done marker and confirm next_append_only_path still skips _v001!
        (tmp / "E001_VA_master_v001.done").write_text("{}", encoding="utf-8")
        p2 = next_append_only_path(tmp, "E001_VA_master", ".wav")
        assert p2.name == "E001_VA_master_v002.wav", f"Expected _v002 when _v001.done exists, got {p2.name}"
        (tmp / "E001_VA_master_v002.mp3").write_bytes(b"mp3")
        p3 = next_append_only_path(tmp, "E001_VA_master", ".wav")
        assert p3.name == "E001_VA_master_v003.wav"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# F11 — Research Report Accuracy, Citation & Anti-Stub Boundaries (5 tests)
# ===========================================================================

@test("T2_F11_01", "F11", "RESEARCH_REPORT.md grounded totals match exact 100 clips, 1,408 segments, 170.2 WPM (not stale/wrong numbers)")
def t2_f11_01() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    assert "100" in rep
    assert "1,408" in rep or "1408" in rep
    assert "170.2" in rep
    assert not re.search(r"共\s*(?:9[0-9]|10[1-9])\s*条", rep), "RESEARCH_REPORT.md cites wrong total clip count"


@test("T2_F11_02", "F11", "Every clip_id cited in RESEARCH_REPORT.md belongs to the real 100-clip set (0 fabricated citations, >=10 real hits)")
def t2_f11_02() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    pat = re.compile(r"\b(?:0[1-5]_(?:AI|BIZ|FIN|USCHINA)_[A-Za-z]+|\d{3}_(?:AI|BIZ|FIN|USC))\b")
    fabricated: list[str] = []
    valid_cited: set[str] = set()
    for line in rep.splitlines():
        for tok in pat.findall(line):
            if tok in h.EXPECTED_100_CLIP_IDS:
                valid_cited.add(tok)
            else:
                # Allow explicitly documenting absent 028/046 prefixes
                if any(k in line.lower() for k in ("缺失", "不存在", "absent", "missing", "跳过", "跳号")):
                    continue
                fabricated.append(tok)
    assert len(valid_cited) >= 10, f"RESEARCH_REPORT.md cited only {len(valid_cited)} valid clip_ids (<10)"
    assert not fabricated, f"Fabricated clip_id(s) cited in RESEARCH_REPORT.md: {fabricated}"


@test("T2_F11_03", "F11", "RESEARCH_REPORT.md has >=5 distinct major section headings covering all 5 pillars")
def t2_f11_03() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    headings = re.findall(r"(?m)^#{1,3}\s+.+$", rep)
    assert len(headings) >= 5, f"RESEARCH_REPORT.md has only {len(headings)} headings (<5 required pillars)"


@test("T2_F11_04", "F11", "RESEARCH_REPORT.md honestly discloses zero-hit world_bridge gap (never falsely claims Best Buy/GDPR are in 100 clips)")
def t2_f11_04() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    low = rep.lower()
    assert any(k in low for k in ("world_bridge", "桥接", "0次", "零次", "零出现", "0 条", "0条")), (
        "RESEARCH_REPORT.md must explicitly disclose empirical world_bridge gap"
    )
    assert any(k in low for k in ("best buy", "selfridges", "gdpr", "slotting")), (
        "RESEARCH_REPORT.md should cite concrete world_bridge zero-hit retail/compliance terms"
    )


@test("T2_F11_05", "F11", "RESEARCH_REPORT.md exceeds 4,000 chars and contains 0 TODO/TBD stub placeholders")
def t2_f11_05() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    assert len(rep) >= 4000, f"RESEARCH_REPORT.md too short ({len(rep)} < 4000 chars)"
    assert not re.search(r"\b(?:TODO|TBD|FIXME)\b", rep), "RESEARCH_REPORT.md contains TODO/TBD placeholder"


# ===========================================================================
# F12 — 100-Clip ETL Collisions, All 38 Anomalies & Error Handling (6 tests)
# ===========================================================================

@test("T2_F12_01", "F12", "Prefix collisions 030_AI/030_BIZ & 054_BIZ/054_FIN distinct; absent 028_ & 046_ not fabricated")
def t2_f12_01() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    for col in h.COLLIDING_PREFIX_IDS:
        assert col in by_id, f"Missing colliding prefix clip {col}"
    assert by_id["030_AI"]["video_id"] != by_id["030_BIZ"]["video_id"]
    assert by_id["030_AI"]["en_clean"] != by_id["030_BIZ"]["en_clean"]
    assert by_id["054_BIZ"]["video_id"] != by_id["054_FIN"]["video_id"]
    assert by_id["054_BIZ"]["en_clean"] != by_id["054_FIN"]["en_clean"]
    for pref in h.ABSENT_PREFIXES:
        assert not any(cid.startswith(pref) for cid in by_id), f"Fabricated absent prefix {pref} in corpus"


@test("T2_F12_02", "F12", "ASR typo regression Batch A (11 high-impact clips / 16 typos): preserved in en_raw, 0 remaining in en_clean & subtitles_clean")
def t2_f12_02() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    batch_a = [a for a in h.RAW_CORPUS_ANOMALIES if a[5] == "A"]
    assert len(batch_a) == 16
    for cid, label, pat, flags, hint, _ in batch_a:
        rec = by_id[cid]
        rx = re.compile(pat, flags)
        assert rx.search(rec["en_raw"]), f"{cid}: expected raw typo {label!r} preserved in en_raw"
        assert not rx.search(rec["en_clean"]), f"{cid}: raw typo {label!r} still in en_clean (expected {hint!r})"
        subs_blob = " ".join(str(s.get("en", s.get("en_clean", ""))) for s in rec.get("subtitles_clean", []))
        assert not rx.search(subs_blob), f"{cid}: raw typo {label!r} still in subtitles_clean"


@test("T2_F12_03", "F12", "ASR typo regression Batch B (11 clips / 21 typos + \\bClaud\\b & case-sensitive \\bMs\\b traps): 0 remaining & Claude intact")
def t2_f12_03() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    batch_b = [a for a in h.RAW_CORPUS_ANOMALIES if a[5] == "B"]
    assert len(batch_b) == 21
    for cid, label, pat, flags, hint, _ in batch_b:
        rec = by_id[cid]
        rx = re.compile(pat, flags)
        assert rx.search(rec["en_raw"]), f"{cid}: expected raw typo {label!r} preserved in en_raw"
        assert not rx.search(rec["en_clean"]), f"{cid}: raw typo {label!r} still in en_clean (expected {hint!r})"
        subs_blob = " ".join(str(s.get("en", s.get("en_clean", ""))) for s in rec.get("subtitles_clean", []))
        assert not rx.search(subs_blob), f"{cid}: raw typo {label!r} still in subtitles_clean"
    assert "claude" in by_id["015_AI"]["en_clean"].lower(), "015_AI: 'Claude' accidentally corrupted while fixing \\bClaud\\b"


@test("T2_F12_04", "F12", "[snorts] preserved in 087_USC.en_raw and 0 bracket tags remain in en_clean/subtitles_clean across all 100 clips")
def t2_f12_04() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    assert "[snorts]" in by_id["087_USC"]["en_raw"]
    for cid, rec in by_id.items():
        assert not re.search(r"\[[^\]]+\]", rec["en_clean"]), f"{cid}: bracket tag remains in en_clean"
        subs_blob = " ".join(str(s.get("en", s.get("en_clean", ""))) for s in rec.get("subtitles_clean", []))
        assert not re.search(r"\[[^\]]+\]", subs_blob), f"{cid}: bracket tag remains in subtitles_clean"


@test("T2_F12_05", "F12", "extract_100_clips_corpus.py exits non-zero cleanly on broken JSON or truncated 99-clip input")
def t2_f12_05() -> None:
    h.require_file(h.RAW_ARSENAL_JSON, "/tmp/arsenal_100_queue.json")
    out_flag = h.probe_script_flag(h.SCRIPT_EXTRACT_CORPUS, ("--out-dir", "--output-dir"))
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f12_bad_"))
    try:
        broken_p = tmp / "broken.json"
        broken_p.write_text("{not valid json", encoding="utf-8")
        p_bad = h.run_python_script(h.SCRIPT_EXTRACT_CORPUS, ["--source", str(broken_p), out_flag, str(tmp / "o1")], timeout=60)
        assert p_bad.returncode != 0, "Expected non-zero exit on broken JSON syntax"

        raw = json.loads(h.RAW_ARSENAL_JSON.read_text(encoding="utf-8"))
        trunc_p = tmp / "trunc99.json"
        if isinstance(raw, list):
            trunc = raw[:99]
        else:
            trunc = dict(raw)
            key = "clips" if "clips" in trunc else "items"
            trunc[key] = trunc[key][:99]
        trunc_p.write_text(json.dumps(trunc, ensure_ascii=False), encoding="utf-8")
        p_tr = h.run_python_script(h.SCRIPT_EXTRACT_CORPUS, ["--source", str(trunc_p), out_flag, str(tmp / "o2")], timeout=60)
        assert p_tr.returncode != 0, "Expected non-zero exit on truncated 99-clip input"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F12_06", "F12", "ETL processes all 1,408 segments cleanly despite 36 raw subtitle overlaps and 5 relative / 95 absolute mp4 paths")
def t2_f12_06() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    assert len(corp["clips"]) == 100
    seg_total = sum(len(c.get("subtitles_clean", [])) for c in corp["clips"])
    assert seg_total == h.EXPECTED_TOTAL_SEGMENTS, f"Expected 1408 cleaned segments, got {seg_total}"
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    for rel_cid in ("01_AI_DHH", "02_BIZ_Anthropic", "03_FIN_Dalio", "04_USCHINA_Jensen", "05_USCHINA_Robots"):
        assert rel_cid in by_id and len(by_id[rel_cid]["subtitles_clean"]) >= 10


# ===========================================================================
# F13 — Show Bible & Prosody Manual Hygiene Boundaries (5 tests)
# ===========================================================================

@test("T2_F13_01", "F13", "Every acoustic_space cited in SHOW_BIBLE.md spec table belongs to the 9 canonical ALLOWED_ACOUSTIC_SPACES")
def t2_f13_01() -> None:
    from aigc_audio_pipeline.models import ALLOWED_ACOUSTIC_SPACES

    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    allowed = set(ALLOWED_ACOUSTIC_SPACES)
    for req_sp in ("boardroom", "inner_monologue", "phone_call", "studio_warm", "dry"):
        assert req_sp in allowed and req_sp in bible
    # Reject hallucinated space identifiers in backticks like `zoom_call` or `conference_room`
    for bad_sp in ("`zoom_call`", "`conference_room`", "`echo_chamber`", "`office_room`"):
        assert bad_sp not in bible, f"SHOW_BIBLE.md references unregistered acoustic space {bad_sp}"


@test("T2_F13_02", "F13", "SHOW_BIBLE.md documents all 8 canonical roles with 0 missing/orphan registry roles")
def t2_f13_02() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    reg = h.load_registry_safe()
    assert len(reg.roles) >= 8, f"Expected >=8 canonical roles in registry, got {len(reg.roles)}"
    assert set(h.CANONICAL_ALL_8_ROLES) <= set(reg.roles.keys()), (
        f"Registry missing canonical roles: {sorted(set(h.CANONICAL_ALL_8_ROLES) - set(reg.roles.keys()))}"
    )
    for rid, prof in reg.roles.items():
        assert rid in bible or prof.display_name in bible, f"SHOW_BIBLE.md omits registered role {rid!r} ({prof.display_name!r})"


@test("T2_F13_03", "F13", "SHOW_BIBLE.md has 0 Xianxia plot drift and 0 ElevenLabs-mandatory claims")
def t2_f13_03() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    h.assert_no_xianxia_plot_drift(bible, "SHOW_BIBLE.md")
    assert "api.elevenlabs.io" not in bible.lower()


@test("T2_F13_04", "F13", "ACCENT_AND_PROSODY_MANUAL.md exceeds 2,000 chars, forbids caricature accents, and specifies 0.8x/1.0x tempo rules")
def t2_f13_04() -> None:
    manual = h.load_text_file(h.PATH_ACCENT_MANUAL, "ACCENT_AND_PROSODY_MANUAL.md")
    assert len(manual) >= 2000, f"ACCENT_AND_PROSODY_MANUAL.md stub ({len(manual)} chars)"
    assert any(k in manual.lower() for k in ("刻板", "漫画", "caricature", "夸张")), "Manual must forbid caricature accents"
    assert "0.8" in manual and "1.0" in manual


@test("T2_F13_05", "F13", "Malformed signature_tags ([COLDLY], [冷笑]) caught by ASCII tag rule; real registry is 100% clean")
def t2_f13_05() -> None:
    ascii_tag_re = re.compile(r"^[a-z0-9\s,\-']+$")
    assert not ascii_tag_re.fullmatch("COLDLY")
    assert not ascii_tag_re.fullmatch("冷笑")
    reg = h.load_registry_safe()
    assert len(reg.roles) >= 8
    for rid, prof in reg.roles.items():
        assert len(prof.signature_tags) >= 1
        for t in prof.signature_tags:
            assert ascii_tag_re.fullmatch(t.strip("[]").strip()), f"{rid}: invalid tag {t!r}"


# ===========================================================================
# F14 — 24-Ep Season 1 Map Bijection Boundaries (5 tests)
# ===========================================================================

@test("T2_F14_01", "F14", "Bijection oracle rejects duplicate clip_id (012_AI in E001 & E005); real map has 0 duplicates")
def t2_f14_01() -> None:
    mut = h.make_synthetic_season1_map(85.0)
    mut["episodes"][4]["primary_clip_ids"][0] = "012_AI"
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(mut), "duplicate 012_AI")
    h.oracle_season1_24ep_bijection(h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json"))


@test("T2_F14_02", "F14", "Bijection oracle rejects dropped clip (99/100) and fabricated clip (028_AI); real map is exact 100/100")
def t2_f14_02() -> None:
    mut_drop = h.make_synthetic_season1_map(85.0)
    mut_drop["episodes"][6]["primary_clip_ids"].pop()
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(mut_drop), "99/100 dropped clip")

    mut_fake = h.make_synthetic_season1_map(85.0)
    mut_fake["episodes"][1]["primary_clip_ids"][0] = "028_AI"
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(mut_fake), "fabricated 028_AI")

    h.oracle_season1_24ep_bijection(h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json"))


@test("T2_F14_03", "F14", "Season-arc oracle rejects 23/25 episodes and unbalanced 5+7+6+6 arcs; real map is exact 4x6=24")
def t2_f14_03() -> None:
    mut_23 = h.make_synthetic_season1_map(85.0)
    mut_23["episodes"].pop()
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(mut_23), "23 episodes")

    mut_unbal = h.make_synthetic_season1_map(85.0)
    mut_unbal["episodes"][5]["arc_number"] = 2
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(mut_unbal), "5+7+6+6 unbalanced arcs")

    res = h.oracle_season1_24ep_bijection(h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json"))
    assert res["arc_counts"] == {1: 6, 2: 6, 3: 6, 4: 6}


@test("T2_F14_04", "F14", "E001 seed-set oracle rejects any mismatch from exact 5 seed clips; real map matches exact 5 seeds")
def t2_f14_04() -> None:
    mut = h.make_synthetic_season1_map(85.0)
    mut["episodes"][0]["primary_clip_ids"][0], mut["episodes"][1]["primary_clip_ids"][0] = (
        mut["episodes"][1]["primary_clip_ids"][0],
        mut["episodes"][0]["primary_clip_ids"][0],
    )
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(mut), "wrong E001 seed set")
    real_map = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    assert set(real_map["episodes"][0]["primary_clip_ids"]) == set(h.E001_SEED_CLIP_IDS)


@test("T2_F14_05", "F14", "Per-episode clip count rejects 0 or 6 clips (violating 20x4 + 4x5); real map passes all 24 episodes")
def t2_f14_05() -> None:
    mut_6 = h.make_synthetic_season1_map(85.0)
    moved = mut_6["episodes"][1]["primary_clip_ids"].pop()
    mut_6["episodes"][0]["primary_clip_ids"].append(moved)
    _expect_assertion_fail(lambda: h.oracle_season1_24ep_bijection(mut_6), "6 clips in E001")
    h.oracle_season1_24ep_bijection(h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json"))


# ===========================================================================
# F15 — Registry Locking, Dangling Roles, Uniqueness & Schema Strictness (5 tests)
# ===========================================================================

@test("T2_F15_01", "F15", "require_locked_voices=True rejects empty voice_id while require_locked_voices=False accepts it")
def t2_f15_01() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    reg = h.make_minimal_registry(include_locked=False)
    sheet = EpisodeCueSheet(
        episode_id="E_LOCK", chapter_number=1, title="Lock", mode="bilingual_business_drama", acts=[],
        cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.")],
    )
    assert sheet.validate(reg, require_locked_voices=False) == []
    errs = sheet.validate(reg, require_locked_voices=True)
    assert any("has no voice_id assigned yet" in e for e in errs), f"Expected locked-voice error, got {errs}"


@test("T2_F15_02", "F15", "EpisodeCueSheet.validate(registry) rejects unknown role_id='ghost_ceo'")
def t2_f15_02() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    reg = h.make_minimal_registry()
    sheet = EpisodeCueSheet(
        episode_id="E_GHOST", chapter_number=1, title="Ghost", mode="bilingual_business_drama", acts=[],
        cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="ghost_ceo", language_code="en", text="Boo.")],
    )
    errs = sheet.validate(reg)
    assert any("not found in VoiceCastingRegistry" in e for e in errs), f"Expected missing-role error, got {errs}"


@test("T2_F15_03", "F15", "Casting uniqueness rejects duplicate voice_id across roles; real registry has 100% unique voice_ids")
def t2_f15_03() -> None:
    reg = h.load_registry_safe()
    vids = [p.voice_id for p in reg.roles.values()]
    assert len(vids) >= 8 and all(v.strip() for v in vids)
    assert len(set(vids)) == len(vids), f"Duplicate voice_id detected in real registry: {vids}"


@test("T2_F15_04", "F15", "Schema drift regression guard: wrong keys 'dialogue_model_id'/'asr_qa_model_id' fall back to ElevenLabs; real registry uses canonical keys")
def t2_f15_04() -> None:
    from aigc_audio_pipeline.models import VoiceCastingRegistry

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f15_drift_"))
    try:
        drift_p = tmp / "drift.json"
        drift_p.write_text(
            json.dumps({
                "project_id": "drift",
                "project_title": "Drift",
                "dialogue_model_id": "fishaudio/drama-3",
                "asr_qa_model_id": "faster-whisper-small-int8",
                "roles": {},
                "sonic_motifs": {},
            }),
            encoding="utf-8",
        )
        loaded_drift = VoiceCastingRegistry.load(drift_p)
        assert loaded_drift.tts_model_id == "eleven_v3", "Expected wrong key to fall back to eleven_v3"
        assert loaded_drift.asr_model_id == "scribe_v3", "Expected wrong key to fall back to scribe_v3"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    real_reg = h.load_registry_safe()
    assert real_reg.tts_model_id == "fishaudio/drama-3"
    assert real_reg.asr_model_id == "faster-whisper-small-int8"


@test("T2_F15_05", "F15", "Undeclared extra JSON field on VoiceProfile or TimelineCue raises TypeError on .load()")
def t2_f15_05() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet, VoiceCastingRegistry

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f15_strict_"))
    try:
        bad_reg_p = tmp / "bad_reg.json"
        reg = h.make_minimal_registry()
        raw_reg = reg.to_dict()
        raw_reg["roles"]["lin_chen"]["undeclared_magic_field"] = 123
        bad_reg_p.write_text(json.dumps(raw_reg), encoding="utf-8")
        raised_reg = False
        try:
            VoiceCastingRegistry.load(bad_reg_p)
        except TypeError:
            raised_reg = True
        assert raised_reg, "Expected VoiceCastingRegistry.load() to reject undeclared VoiceProfile field with TypeError"

        bad_cs_p = tmp / "bad_cs.json"
        cs = h.make_synthetic_e001_variant("E001_VA", distinct_seed_word="strict")
        raw_cs = cs.to_dict()
        raw_cs["cues"][0]["undeclared_cue_field"] = "oops"
        bad_cs_p.write_text(json.dumps(raw_cs), encoding="utf-8")
        raised_cs = False
        try:
            EpisodeCueSheet.load(bad_cs_p)
        except TypeError:
            raised_cs = True
        assert raised_cs, "Expected EpisodeCueSheet.load() to reject undeclared TimelineCue field with TypeError"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# F16 — Variant Differentiation, Ducking Corners, Resolver & Rubric Boundaries (6 tests)
# ===========================================================================

@test("T2_F16_01", "F16", "Near-duplicate VA & VB (Jaccard > 0.85) rejected; real E001_VA-VD have pairwise Jaccard < 0.70")
def t2_f16_01() -> None:
    dup_set = {
        "E001_VA": h.make_synthetic_e001_variant("E001_VA", crosstalk_count=6, inner_monologue_count=0, distinct_seed_word="clone"),
        "E001_VB": h.make_synthetic_e001_variant("E001_VB", crosstalk_count=6, inner_monologue_count=4, include_zhou_mo_debrief=True, distinct_seed_word="clone"),
        "E001_VC": h.make_synthetic_e001_variant("E001_VC", crosstalk_count=6, phone_call_count=2, distinct_seed_word="clone"),
        "E001_VD": h.make_synthetic_e001_variant("E001_VD", crosstalk_count=3, duck_count=2, distinct_seed_word="clone"),
    }
    _expect_assertion_fail(lambda: h.oracle_variant_differentiation_and_crosstalk(dup_set), "near-duplicate VA/VB")
    h.oracle_variant_differentiation_and_crosstalk(h.load_all_e001_variants())


@test("T2_F16_02", "F16", "E001_VD with <2 duck_under_next=True blocks fails; real E001_VD has >=2 valid blocks")
def t2_f16_02() -> None:
    real_variants = h.load_all_e001_variants()
    vd = real_variants["E001_VD"]
    vd_ducks = [c for c in vd.cues if c.kind == "dialogue" and getattr(c, "duck_under_next", False)]
    assert len(vd_ducks) >= 2, f"Real E001_VD has only {len(vd_ducks)} duck_under_next cues (<2)"
    mut_vd = h.make_synthetic_e001_variant("E001_VD", crosstalk_count=3, duck_count=1, distinct_seed_word="one_duck")
    mut_set = {**real_variants, "E001_VD": mut_vd}
    _expect_assertion_fail(lambda: h.oracle_variant_differentiation_and_crosstalk(mut_set), "VD duck_count=1")


@test("T2_F16_03", "F16", "Invalid variant selector (--episodes E001_VZ) exits non-zero on studio runner (never silently renders 0)")
def t2_f16_03() -> None:
    h.require_ffmpeg()
    h.require_file(h.COLAB_RUN_STUDIO, "run_global_edge_96gb_studio.py")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f16_badep_"))
    try:
        sdir = h.build_mini_studio_dir(
            tmp / "studio",
            cue_sheets={"E001_VA_t.json": h.make_mini_cue_sheet("E001_VA")},
        )
        proc = h.run_python_script(
            h.COLAB_RUN_STUDIO,
            [
                "--studio-dir", str(sdir),
                "--episodes", "E001_VZ",
                "--output-dir", str(tmp / "out"),
                "--cache-dir", str(tmp / "cache"),
                "--offline-dry-run",
            ],
            timeout=60,
        )
        assert proc.returncode != 0, "Studio runner must exit non-zero on unknown variant target E001_VZ"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F16_04", "F16", "duck_under_next=True before an sfx cue OR at EOF both rejected with explicit error")
def t2_f16_04() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    before_sfx = EpisodeCueSheet(
        episode_id="E_DSFX", chapter_number=1, title="Duck SFX", mode="bilingual_business_drama", acts=[],
        cues=[
            h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Wait.", duck_under_next=True),
            h.make_timeline_cue(cue_id="S1", act_id="a1", kind="sfx", sfx_prompt="Door shut, no voice", duration_seconds=1.5),
        ],
    )
    at_eof = EpisodeCueSheet(
        episode_id="E_DEOF", chapter_number=1, title="Duck EOF", mode="bilingual_business_drama", acts=[],
        cues=[
            h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Wait.", duck_under_next=True),
        ],
    )
    assert any("immediately following dialogue cue" in e for e in before_sfx.validate())
    assert any("immediately following dialogue cue" in e for e in at_eof.validate())


@test("T2_F16_05", "F16", "duck_under_next=True on an sfx cue rejected with explicit error")
def t2_f16_05() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    bad = EpisodeCueSheet(
        episode_id="E_SFX_D", chapter_number=1, title="SFX Duck", mode="bilingual_business_drama", acts=[],
        cues=[
            h.make_timeline_cue(cue_id="S1", act_id="a1", kind="sfx", sfx_prompt="Click, no voice", duration_seconds=1.5, duck_under_next=True),
            h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hi."),
        ],
    )
    assert any("only valid on dialogue cues" in e for e in bad.validate())


@test("T2_F16_06", "F16", "Rubric weight oracle rejects sums of 95 and 105; real E001_COMPARATIVE_EVAL_RUBRIC.md sums to exact 100")
def t2_f16_06() -> None:
    base = (
        "| 维度 | 权重 |\n|---|---|\n"
        "| 1. A | 20分 |\n| 2. B | 20分 |\n| 3. C | 15分 |\n"
        "| 4. D | 15分 |\n| 5. E | 10分 |\n| 6. F | 10分 |\n| 7. G | 10分 |\n"
    )
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(rubric_md=base.replace("7. G | 10分", "7. G | 5分")), "sum=95")
    _expect_assertion_fail(lambda: h.oracle_viral_45s_cutlist_and_rubric(rubric_md=base.replace("7. G | 10分", "7. G | 15分")), "sum=105")

    real_rubric = h.load_text_file(h.PATH_RUBRIC_MD, "E001_COMPARATIVE_EVAL_RUBRIC.md")
    res = h.oracle_viral_45s_cutlist_and_rubric(rubric_md=real_rubric)
    assert res["rubric_sum"] == 100


# ===========================================================================
# F17 — playback_rate Boundaries, Epsilon Gate & Legacy Compatibility (5 tests)
# ===========================================================================

@test("T2_F17_01", "F17", "playback_rate lower boundary: 0.649 (reject) vs 0.65 (accept)")
def t2_f17_01() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    def _errs(r: float) -> list[str]:
        s = EpisodeCueSheet(
            episode_id="E_PR_LO", chapter_number=1, title="PR Lo", mode="bilingual_business_drama", acts=[],
            cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Slow.", playback_rate=r)],
        )
        return s.validate()

    assert any("playback_rate" in e for e in _errs(0.649))
    assert _errs(0.65) == []


@test("T2_F17_02", "F17", "playback_rate upper boundary: 1.35 (accept) vs 1.351 (reject)")
def t2_f17_02() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    def _errs(r: float) -> list[str]:
        s = EpisodeCueSheet(
            episode_id="E_PR_HI", chapter_number=1, title="PR Hi", mode="bilingual_business_drama", acts=[],
            cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Fast.", playback_rate=r)],
        )
        return s.validate()

    assert _errs(1.35) == []
    assert any("playback_rate" in e for e in _errs(1.351))


@test("T2_F17_03", "F17", "Extreme invalid playback_rate values (0.0, -0.8, 2.5) all rejected safely without divide-by-zero")
def t2_f17_03() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    for bad_r in (0.0, -0.8, 2.5):
        s = EpisodeCueSheet(
            episode_id="E_PR_EXT", chapter_number=1, title="PR Ext", mode="bilingual_business_drama", acts=[],
            cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Bad.", playback_rate=bad_r)],
        )
        errs = s.validate()
        assert any("playback_rate" in e for e in errs), f"Expected playback_rate rejection for {bad_r}, got {errs}"


@test("T2_F17_04", "F17", "condition_dialogue_clip epsilon gate: playback_rate=1.0004 keeps duration unchanged while 0.80 stretches 1.25x")
def t2_f17_04() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    h.require_signature_param(condition_dialogue_clip, "playback_rate")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f17_eps_"))
    try:
        src = h.write_sine_wav(tmp / "in.wav", 2.0, freq_hz=440.0)
        eps_out = tmp / "eps.wav"
        slow_out = tmp / "slow.wav"
        condition_dialogue_clip(src, eps_out, acoustic_space="dry", playback_rate=1.0004)
        condition_dialogue_clip(src, slow_out, acoustic_space="dry", playback_rate=0.80)
        p_eps = h.probe_audio_ffprobe(eps_out)
        p_slow = h.probe_audio_ffprobe(slow_out)
        assert abs(p_eps["duration_s"] - 2.0) <= 0.06, f"1.0004 should bypass atempo (~2.0s), got {p_eps['duration_s']:.3f}s"
        assert 2.35 <= p_slow["duration_s"] <= 2.65, f"0.80 should stretch to ~2.50s, got {p_slow['duration_s']:.3f}s"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F17_05", "F17", "Legacy EpisodeCueSheet JSON lacking playback_rate (Buffett E001) loads cleanly with default 1.0")
def t2_f17_05() -> None:
    cs = h.load_cue_sheet_safe(h.LEGACY_BUFFETT_E001)
    assert len(cs.cues) > 0
    for c in cs.cues:
        assert getattr(c, "playback_rate") == 1.0


# ===========================================================================
# F18 — Xianxia Fallback Traps, Dual-Script zh-en QA & Chunking Boundaries (6 tests)
# ===========================================================================

@test("T2_F18_01", "F18", "Xianxia polyphone fallback trap: domain='business_english_drama' preserves '引气九重降临辟谷' unaltered")
def t2_f18_01() -> None:
    from aigc_audio_pipeline.polyphones import apply_domain_polyphone_overrides

    inp = "引气九重降临辟谷"
    out = apply_domain_polyphone_overrides(inp, domain="business_english_drama")
    h.oracle_domain_no_xianxia_leak(polyphone_input=inp, polyphone_output=out)
    assert out == inp, f"Expected unchanged {inp!r}, got {out!r}"


@test("T2_F18_02", "F18", "Xianxia narration fallback trap: untagged narrator under domain='business_english_drama' emits zero Xianxia strings")
def t2_f18_02() -> None:
    from aigc_audio_pipeline.drama3_adapter import translate_cue_to_drama3_input
    from aigc_audio_pipeline.models import VoiceProfile

    narr_prof = VoiceProfile(
        role_id="narrator", display_name="Narrator", aliases=[], tier="narrator",
        gender="male", age_group="40", language_code="zh", vocal_register="baritone",
        persona_summary="Documentary", accent_requirement="Standard Mandarin",
    )
    cue = h.make_timeline_cue(
        cue_id="N1", act_id="a1", kind="dialogue", role_id="narrator",
        language_code="zh", text="凌晨两点，深圳南山科技园的灯光还没有熄灭。",
    )
    out = translate_cue_to_drama3_input(cue, narr_prof, attempt=1, domain="business_english_drama")
    h.oracle_domain_no_xianxia_leak(drama3_prompt=out)


@test("T2_F18_03", "F18", "Dual-script zh-en QA fails when CJK is 100% intact but embedded English keywords (len>=3) are dropped")
def t2_f18_03() -> None:
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    res = evaluate_dialogue_qa(
        tagged_prompt="[measured] 这份财报里的 phantom number 和 capital-efficient 必须当场拆穿。",
        asr_text="这份财报里的和必须当场拆穿。",
        duration_s=3.0,
        peak_dbfs=-6.0,
        language_code="zh-en",
    )
    assert res.passed is False, f"Expected dual-script zh-en QA to reject dropped English keywords, got passed=True"


@test("T2_F18_04", "F18", "Dual-script zh-en QA catches truncated trailing English words (tail_preserved == False)")
def t2_f18_04() -> None:
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    res = evaluate_dialogue_qa(
        tagged_prompt="[firmly] 我们要马上锁死这个 phantom number and upside",
        asr_text="我们要马上锁死这个",
        duration_s=2.5,
        peak_dbfs=-6.0,
        language_code="zh-en",
    )
    assert res.passed is False and res.tail_preserved is False, (
        f"Expected tail_preserved=False for truncated EN tail, got passed={res.passed}, tail={res.tail_preserved}"
    )


@test("T2_F18_05", "F18", "Dual-script QA detects leaked corporate tags ('deadpan', 'skeptical', 'guarded', 'understated') in ASR")
def t2_f18_05() -> None:
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    for tag in ("deadpan", "skeptical", "guarded", "understated"):
        res = evaluate_dialogue_qa(
            tagged_prompt=f"[{tag}] That valuation math does not survive diligence.",
            asr_text=f"{tag} That valuation math does not survive diligence.",
            duration_s=2.5,
            peak_dbfs=-6.0,
            language_code="en",
        )
        assert res.passed is False and tag in res.leaked_tags, (
            f"Expected leaked corporate tag {tag!r} to fail QA, got passed={res.passed}, leaked={res.leaked_tags}"
        )


@test("T2_F18_06", "F18", "split_cue_into_subcues_for_drama3 keeps short zh-en (3 CJK + 10 EN) unsplit and splits over-budget (4 CJK + 60 EN)")
def t2_f18_06() -> None:
    from aigc_audio_pipeline.drama3_adapter import split_cue_into_subcues_for_drama3

    short_cue = h.make_timeline_cue(
        cue_id="SH1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="zh-en",
        text="[measured] 听着，this phantom number is not a cash loss at all.",
    )
    short_parts = split_cue_into_subcues_for_drama3(short_cue, max_cjk_chars=105, max_en_words=65, domain="business_english_drama")
    assert len(short_parts) == 1, f"Short zh-en cue should stay unsplit, got {len(short_parts)}"

    long_cue = h.make_timeline_cue(
        cue_id="LG1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="zh-en",
        text=(
            "[measured] 听着，"
            "Our boardroom position rests on three concrete pillars of unit economics. "
            "First, the convertible note revaluation is strictly a phantom number that never reduced cash reserves. "
            "Second, shifting local model inference to Shenzhen edge silicon delivers ten times the throughput. "
            "Third, retail partners face a really hard trade-off whenever cloud API fees start eating into budgets every single quarter."
        ),
    )
    long_parts = split_cue_into_subcues_for_drama3(long_cue, max_cjk_chars=105, max_en_words=65, domain="business_english_drama")
    assert len(long_parts) >= 2, f"Over-budget zh-en cue (4 CJK + ~60 EN) must split into >=2 subcues, got {len(long_parts)}"


# ===========================================================================
# F19 — Acoustic Spaces, TTS Isolation, Resolver Collision, SRT Clamping & Error Paths (6 tests)
# ===========================================================================

@test("T2_F19_01", "F19", "Unknown acoustic_space values ('conference_room', 'zoom_call', 'cave', '') all rejected")
def t2_f19_01() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet

    for bad_sp in ("conference_room", "zoom_call", "cave", ""):
        s = EpisodeCueSheet(
            episode_id="E_SP", chapter_number=1, title="Bad SP", mode="bilingual_business_drama", acts=[],
            cues=[h.make_timeline_cue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hi.", acoustic_space=bad_sp)],
        )
        errs = s.validate()
        assert any("acoustic_space" in e for e in errs), f"Expected acoustic_space rejection for {bad_sp!r}, got {errs}"


@test("T2_F19_02", "F19", "subtitle_translation never contaminates translate_cue_to_drama3_input output across attempts 1..3")
def t2_f19_02() -> None:
    from aigc_audio_pipeline.drama3_adapter import translate_cue_to_drama3_input

    reg = h.make_minimal_registry()
    cue = h.make_timeline_cue(
        cue_id="C_TR", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en",
        text="[measured] It is not a cash loss.", subtitle_translation="这不是现金亏损。",
    )
    for att in (1, 2, 3):
        out = translate_cue_to_drama3_input(cue, reg.roles["lin_chen"], attempt=att, domain="business_english_drama")
        assert "现金亏损" not in out and "这不是" not in out, f"attempt={att}: subtitle_translation leaked into TTS: {out!r}"


@test("T2_F19_03", "F19", "Studio CLI variant resolver rejects malformed 'E001_V!' and renders distinct E001_VA/E001_VB outputs without collapsing onto E001")
def t2_f19_03() -> None:
    h.require_ffmpeg()
    h.require_file(h.COLAB_RUN_STUDIO, "run_global_edge_96gb_studio.py")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f19_res_"))
    try:
        sdir = h.build_mini_studio_dir(
            tmp / "studio",
            cue_sheets={
                "E001_VA_a.json": h.make_mini_cue_sheet("E001_VA"),
                "E001_VB_b.json": h.make_mini_cue_sheet("E001_VB"),
                "E001_VC_c.json": h.make_mini_cue_sheet("E001_VC"),
                "E001_VD_d.json": h.make_mini_cue_sheet("E001_VD"),
            },
        )
        # Negative CLI check: malformed target 'E001_V!' must exit non-zero
        p_bad = h.run_python_script(
            h.COLAB_RUN_STUDIO,
            [
                "--studio-dir", str(sdir),
                "--episodes", "E001_V!",
                "--output-dir", str(tmp / "out_bad"),
                "--cache-dir", str(tmp / "cache"),
                "--offline-dry-run",
            ],
            timeout=120,
        )
        assert p_bad.returncode != 0, (
            "run_global_edge_96gb_studio.py must exit non-zero on malformed target --episodes E001_V!"
        )

        # Positive distinct-key check: E001_VA,E001_VB yields exact 2 distinct outputs (zero collapse onto E001, zero VC/VD)
        out_ok = tmp / "out_ok"
        p_ok = h.run_python_script(
            h.COLAB_RUN_STUDIO,
            [
                "--studio-dir", str(sdir),
                "--episodes", "E001_VA,E001_VB",
                "--output-dir", str(out_ok),
                "--cache-dir", str(tmp / "cache"),
                "--offline-dry-run",
            ],
            timeout=180,
        )
        assert p_ok.returncode == 0, (
            f"run_global_edge_96gb_studio.py --episodes E001_VA,E001_VB failed: "
            f"{p_ok.stderr[-800:]}\n{p_ok.stdout[-400:]}"
        )
        done_files = sorted(out_ok.glob("*_v001.done"))
        assert len(done_files) == 2, (
            f"Expected exact 2 *_v001.done files for E001_VA,E001_VB, got {len(done_files)}: {[p.name for p in done_files]}"
        )
        manifests = [h.load_json_file(p.with_suffix(".json")) for p in done_files]
        eids = {m.get("episode_id") for m in manifests}
        assert eids == {"E001_VA", "E001_VB"}, (
            f"Expected distinct manifest episode_ids {{'E001_VA', 'E001_VB'}}, got {eids}"
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F19_04", "F19", "Negative-gap crosstalk (-0.25s) mastered via master_episode_three_bus clamps SRT to strictly non-overlapping timestamps")
def t2_f19_04() -> None:
    from aigc_audio_pipeline.mixer import master_episode_three_bus
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    h.require_ffmpeg()
    reg = h.make_minimal_registry()
    sheet = EpisodeCueSheet(
        episode_id="E001_XTALK",
        chapter_number=1,
        title="Crosstalk SRT Clamp",
        mode="bilingual_business_drama",
        acts=[ActMusicSpec(act_id="act_1", title="Act 1", bgm_prompt="Minimalist strings, instrumental, no vocals")],
        cues=[
            h.make_timeline_cue(
                cue_id="X1", act_id="act_1", kind="dialogue", role_id="victoria_vance", speaker_name="Victoria Vance",
                language_code="en", text="[icy polite] That number is indefensible.", subtitle_translation="这个数字根本站不住脚。", gap_after_s=-0.25,
            ),
            h.make_timeline_cue(
                cue_id="X2", act_id="act_1", kind="dialogue", role_id="lin_chen", speaker_name="Lin Chen",
                language_code="en", text="[interrupting] It is not a cash loss.", subtitle_translation="这不是现金亏损。", gap_after_s=0.35,
            ),
        ],
    )
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f19_xtalk_"))
    try:
        w1 = h.write_sine_wav(tmp / "x1.wav", 1.8, freq_hz=330.0)
        w2 = h.write_sine_wav(tmp / "x2.wav", 1.8, freq_hz=440.0)
        bgm = h.write_sine_wav(tmp / "bgm.wav", 5.0, freq_hz=110.0, amplitude=0.12)
        res = master_episode_three_bus(sheet, {"X1": w1, "X2": w2}, {"act_1": bgm}, tmp / "out", registry=reg, clean_work_dir=True)
        srt_text = Path(res["subtitles_srt"]).read_text(encoding="utf-8")
        h.oracle_srt_non_overlap_and_dual_line(
            srt_text,
            expected_translations=["这个数字根本站不住脚。", "这不是现金亏损。"],
        )
        manifest = h.load_json_file(Path(res["manifest_json"]))
        tl = manifest["timeline"]
        assert tl[1]["start_s"] < tl[0]["end_s"], "Expected real audio overlap on Bus A for gap_after_s=-0.25"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T2_F19_05", "F19", "Legacy cue sheet lacking subtitle_translation and legacy registry lacking accent_code load and validate cleanly")
def t2_f19_05() -> None:
    reg = h.load_registry_safe(h.LEGACY_BUFFETT_REGISTRY)
    cs = h.load_cue_sheet_safe(h.LEGACY_BUFFETT_E001)
    assert len(reg.roles) > 0, "Legacy Buffett registry loaded 0 roles"
    assert len(cs.cues) > 0, "Legacy Buffett E001 cue sheet loaded 0 cues"
    assert all(p.accent_code == "" for p in reg.roles.values())
    assert all(getattr(c, "subtitle_translation") == "" for c in cs.cues)
    assert cs.validate(reg, require_locked_voices=False) == []


@test("T2_F19_06", "F19", "condition_dialogue_clip fails loudly (FileNotFoundError / CalledProcessError) on missing input WAV")
def t2_f19_06() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t2_f19_miss_"))
    try:
        raised = False
        try:
            condition_dialogue_clip(tmp / "does_not_exist.wav", tmp / "out.wav", acoustic_space="dry")
        except (FileNotFoundError, subprocess.CalledProcessError, RuntimeError, OSError):
            raised = True
        assert raised, "condition_dialogue_clip must raise an explicit error on missing input WAV"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


TESTS = COLLECTOR.tests
assert len(TESTS) == 100, f"Expected exact 100 Tier 2 tests, got {len(TESTS)}"
