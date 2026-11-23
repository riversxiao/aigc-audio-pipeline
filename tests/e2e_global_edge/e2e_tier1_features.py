"""Tier 1 — Feature Coverage (Happy-Path Equivalence Classes): 100 Opaque-Box E2E Tests.

Covers all 19 features (F01–F19) with 5–6 genuine, non-trivial tests per feature
(`T1_F01_01`..`T1_F19_06`). Every test asserts concrete public contracts and fails
crisply when target artifacts or extensions are missing or non-compliant.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import re
import shutil
import statistics
import tempfile
from pathlib import Path

import e2e_helpers as h

COLLECTOR = h.TierCollector(tier=1)
test = COLLECTOR.test


# ===========================================================================
# F01 — Standalone Serial Business Drama IP (5 tests)
# ===========================================================================

@test("T1_F01_01", "F01", "All 4 E001 variants have 0 YouTube/Shorts commentary references in drama dialogue")
def t1_f01_01() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        h.oracle_standalone_ip_and_banned_cliches(cs)


@test("T1_F01_02", "F01", "All 4 E001 variants use bilingual_business_drama mode, >=4 acts, >=35 dialogue cues, >=4 named characters")
def t1_f01_02() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        assert cs.mode == "bilingual_business_drama", f"{vid}: mode={cs.mode!r}, expected 'bilingual_business_drama'"
        assert len(cs.acts) >= 4, f"{vid}: act count={len(cs.acts)} < 4"
        dlg = [c for c in cs.cues if c.kind == "dialogue"]
        assert len(dlg) >= 35, f"{vid}: dialogue cue count={len(dlg)} < 35"
        roles = {c.role_id for c in dlg if c.role_id}
        assert len(roles) >= 4, f"{vid}: distinct speakers={sorted(roles)} (< 4)"


@test("T1_F01_03", "F01", "SHOW_BIBLE.md and SEASON1_24EP_BLUEPRINT.md establish standalone 4-arc serial IP")
def t1_f01_03() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    blueprint = h.load_text_file(h.PATH_SEASON1_BLUEPRINT, "SEASON1_24EP_BLUEPRINT.md")
    for label, txt in (("SHOW_BIBLE.md", bible), ("SEASON1_24EP_BLUEPRINT.md", blueprint)):
        low = txt.lower()
        assert "global edge" in low or "跨境底牌" in txt, f"{label}: missing IP title Global Edge / 跨境底牌"
        assert any(k in txt for k in ("独立", "standalone", "连续", "商战")), f"{label}: missing standalone serial IP framing"
    assert any(k in blueprint for k in ("第一幕", "第一单元", "Arc 1", "弧光", "篇章")), (
        "SEASON1_24EP_BLUEPRINT.md missing serialized 4-arc structure"
    )


@test("T1_F01_04", "F01", "All 4 E001 variants dramatize Series C convertible-note GAAP loss + AI token retail margin squeeze")
def t1_f01_04() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, drama_cues, _ = h.split_drama_and_debrief_cues(cs)
        assert len(drama_cues) > 0, f"{vid}: empty drama cues"
        blob = h.normalize_for_phrase_match(
            " ".join(h.strip_inline_tags(c.text)[1] for c in drama_cues if c.kind == "dialogue")
        )
        has_fin_crisis = any(
            k in blob for k in ("convertible", "phantom number", "not a cash loss", "income statement", "可转债", "账面")
        )
        has_margin_ai = any(
            k in blob for k in ("margin", "budget", "throughput", "token", "毛利", "算力", "推理")
        )
        assert has_fin_crisis, f"{vid}: missing Series C convertible-note/GAAP loss crisis in drama"
        assert has_margin_ai, f"{vid}: missing retail margin / AI compute bill squeeze in drama"


@test("T1_F01_05", "F01", "season1_24ep_map.json defines 24 unique episodes with non-empty loglines, titles, and cliffhangers")
def t1_f01_05() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    eps = smap.get("episodes", [])
    assert len(eps) == 24, f"Expected 24 episodes, got {len(eps)}"
    zh_titles: set[str] = set()
    en_titles: set[str] = set()
    for ep in eps:
        for k in ("episode_id", "title_zh", "title_en", "logline_zh", "cliffhanger_zh"):
            assert isinstance(ep.get(k), str) and bool(ep[k].strip()), (
                f"{ep.get('episode_id')}: invalid/empty {k}={ep.get(k)!r}"
            )
        zh_titles.add(ep["title_zh"].strip())
        en_titles.add(ep["title_en"].strip())
    assert len(zh_titles) == 24, f"Duplicate Chinese titles: only {len(zh_titles)}/24 unique"
    assert len(en_titles) == 24, f"Duplicate English titles: only {len(en_titles)}/24 unique"


# ===========================================================================
# F02 — B1–C1 Executive English Threshold (5 tests)
# ===========================================================================

@test("T1_F02_01", "F02", "executive_lexicon.json has >=100 entries with complete B1-C1 schema")
def t1_f02_01() -> None:
    lex = h.load_json_file(h.PATH_LEXICON_JSON, "executive_lexicon.json")
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    summary = h.oracle_lexicon_provenance_70_30(lex, corp)
    assert summary["total"] >= 100


@test("T1_F02_02", "F02", "executive_lexicon.json enforces >=70% corpus / <=30% world_bridge split and C1 executive depth")
def t1_f02_02() -> None:
    lex = h.load_json_file(h.PATH_LEXICON_JSON, "executive_lexicon.json")
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    summary = h.oracle_lexicon_provenance_70_30(lex, corp)
    assert summary["corpus_ratio"] >= 0.70
    entries = lex if isinstance(lex, list) else lex.get("phrases", lex.get("entries", lex.get("lexicon", [])))
    c1_entries = [e for e in entries if "C1" in str(e.get("cefr_level", "")).upper()]
    assert len(c1_entries) >= 25, f"Expected >=25 C1 executive entries, got {len(c1_entries)}"


@test("T1_F02_03", "F02", "All 4 E001 variants hit 8/8 mandatory executive target phrases in drama cues")
def t1_f02_03() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        res = h.oracle_e001_8_mandatory_phrases(cs, drama_only=True)
        assert res["matched_count"] == 8, f"{vid}: only {res['matched_count']}/8 phrases matched"


@test("T1_F02_04", "F02", "E001_BILINGUAL_COMPANION_MANUAL.md covers all 8 mandatory phrases with Chinglish contrasts and subtext")
def t1_f02_04() -> None:
    manual = h.load_text_file(h.PATH_COMPANION_MD, "E001_BILINGUAL_COMPANION_MANUAL.md")
    norm = h.normalize_for_phrase_match(manual)
    for pid, label, and_clauses in h.E001_MANDATORY_PHRASES:
        for alts in and_clauses:
            assert any(a in norm for a in alts), (
                f"Companion manual missing mandatory phrase {pid} ({label}): none of {list(alts)}"
            )
    assert any(k in manual for k in ("中式", "Chinglish", "直译")), "Companion manual missing Chinglish vs C-suite contrast"
    assert any(k in manual for k in ("潜台词", "重音", "连读", "发音", "用法")), "Companion manual missing subtext/usage notes"


@test("T1_F02_05", "F02", "Every episode E001-E024 in season1_24ep_map.json defines 5..8 non-empty target phrases")
def t1_f02_05() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    eps = smap.get("episodes", [])
    assert len(eps) == 24
    for ep in eps:
        tp = ep.get("target_phrases")
        assert isinstance(tp, list) and 5 <= len(tp) <= 8, (
            f"{ep.get('episode_id')}: expected 5..8 target_phrases, got {tp!r}"
        )
        assert all(
            (isinstance(x, str) and bool(x.strip()))
            or (isinstance(x, dict) and isinstance(x.get("phrase_en"), str) and bool(x["phrase_en"].strip()))
            for x in tp
        ), f"{ep.get('episode_id')}: blank or invalid phrase in target_phrases"


# ===========================================================================
# F03 — Diegetic Cross-Border Bilingual Acting (5 tests)
# ===========================================================================

@test("T1_F03_01", "F03", "Foreign executives victoria_vance and alistair_finch speak 100% pure English (0 CJK) across all 4 variants")
def t1_f03_01() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        foreign_cues = [
            c for c in cs.cues if c.kind == "dialogue" and c.role_id in ("victoria_vance", "alistair_finch")
        ]
        assert len(foreign_cues) >= 8, f"{vid}: too few foreign executive cues ({len(foreign_cues)})"
        for cue in foreign_cues:
            assert cue.language_code == "en", f"{vid} {cue.cue_id}: {cue.role_id} language_code={cue.language_code!r} != 'en'"
            _, spoken = h.strip_inline_tags(cue.text)
            assert h.count_cjk_chars(spoken) == 0, f"{vid} {cue.cue_id}: CJK found in foreign exec line {spoken!r}"


@test("T1_F03_02", "F03", "Protagonist lin_chen switches authentically between >=6 pure EN cues and >=4 Mandarin/bilingual cues per variant")
def t1_f03_02() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        lin_en = [c for c in cs.cues if c.kind == "dialogue" and c.role_id == "lin_chen" and c.language_code == "en"]
        lin_zh = [c for c in cs.cues if c.kind == "dialogue" and c.role_id == "lin_chen" and c.language_code in ("zh", "zh-en")]
        assert len(lin_en) >= 6, f"{vid}: lin_chen has only {len(lin_en)} pure EN cues (<6)"
        assert len(lin_zh) >= 4, f"{vid}: lin_chen has only {len(lin_zh)} ZH/ZH-EN cues (<4)"


@test("T1_F03_03", "F03", "Drama acts English duration ratio sits in 30%-88% bilingual bounds with E001_VA >= 50% exceeding E001_VB")
def t1_f03_03() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    en_shares: dict[str, float] = {}
    for vid, cs in variants.items():
        _, drama_cues, _ = h.split_drama_and_debrief_cues(cs)
        dlg = [c for c in drama_cues if c.kind == "dialogue"]
        assert len(dlg) > 0
        total_dur = sum(h.estimate_cue_spoken_duration_s(c) for c in dlg)
        en_dur = 0.0
        for c in dlg:
            d = h.estimate_cue_spoken_duration_s(c)
            if c.language_code == "en":
                en_dur += d
            elif c.language_code == "zh-en":
                _, sp = h.strip_inline_tags(c.text)
                cjk_t = h.count_cjk_chars(sp) / 3.60
                en_t = h.count_en_words(sp) / 2.65
                en_dur += d * (en_t / max(cjk_t + en_t, 1e-6))
        share = en_dur / total_dur
        en_shares[vid] = share
        assert 0.30 <= share <= 0.88, f"{vid}: drama EN share={share:.1%} outside [30%, 88%]"
    assert en_shares["E001_VA"] >= 0.50, f"E001_VA drama EN share={en_shares['E001_VA']:.1%} < 50%"
    assert en_shares["E001_VA"] > en_shares["E001_VB"], (
        f"Expected VA EN share ({en_shares['E001_VA']:.1%}) > VB ({en_shares['E001_VB']:.1%})"
    )


@test("T1_F03_04", "F03", "Non-ducked pure-EN drama cues carry >=80% Chinese subtitle_translation coverage without polluting English text")
def t1_f03_04() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, drama_cues, _ = h.split_drama_and_debrief_cues(cs)
        en_cues = [c for c in drama_cues if c.kind == "dialogue" and c.language_code == "en"]
        assert len(en_cues) >= 10, f"{vid}: too few pure EN drama cues ({len(en_cues)})"
        for cue in en_cues:
            _, spoken = h.strip_inline_tags(cue.text)
            assert h.count_cjk_chars(spoken) == 0, f"{vid} {cue.cue_id}: CJK leaked into pure-EN cue text"
        # Exclude simultaneous-translation duck_under_next cues (which pair with the next ZH cue in SRT)
        non_ducked = [c for c in en_cues if not getattr(c, "duck_under_next", False)]
        assert len(non_ducked) >= 6, f"{vid}: too few non-ducked pure-EN drama cues ({len(non_ducked)})"
        translated = sum(
            1
            for cue in non_ducked
            if str(getattr(cue, "subtitle_translation", "") or "").strip()
            and h.count_cjk_chars(str(getattr(cue, "subtitle_translation", "") or "")) >= 2
        )
        cov = translated / len(non_ducked)
        assert cov >= 0.80, (
            f"{vid}: non-ducked pure-EN subtitle_translation coverage={cov:.1%} "
            f"({translated}/{len(non_ducked)}) < 80%"
        )


@test("T1_F03_05", "F03", "E001_VB uses >=4 inner_monologue Mandarin decoders; E001_VD uses >=2 duck_under_next EN->ZH pairs")
def t1_f03_05() -> None:
    vb = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VB"])
    vd = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VD"])
    vb_inner = [
        c for c in vb.cues
        if c.kind == "dialogue" and c.acoustic_space == "inner_monologue" and c.language_code in ("zh", "zh-en")
    ]
    assert len(vb_inner) >= 4, f"E001_VB has only {len(vb_inner)} Mandarin/bilingual inner_monologue cues (<4)"

    vd_ducks = 0
    for idx, c in enumerate(vd.cues):
        if c.kind == "dialogue" and getattr(c, "duck_under_next", False):
            assert idx + 1 < len(vd.cues) and vd.cues[idx + 1].kind == "dialogue", (
                f"E001_VD {c.cue_id}: duck_under_next not followed by dialogue"
            )
            vd_ducks += 1
    assert vd_ducks >= 2, f"E001_VD has only {vd_ducks} valid duck_under_next pairs (<2)"


# ===========================================================================
# F04 — 3-Min Post-Drama Black-Book Debrief (5 tests)
# ===========================================================================

@test("T1_F04_01", "F04", "Standalone Act 5 Debrief runtime lies in [165, 210]s across all 4 E001 variants")
def t1_f04_01() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        br = h.estimate_episode_runtime_breakdown(cs)
        assert 165.0 <= br["debrief_s"] <= 210.0, (
            f"{vid}: Debrief runtime={br['debrief_s']:.1f}s outside [165.0, 210.0]s"
        )


@test("T1_F04_02", "F04", "Every variant's Debrief includes >=3 playback_rate=0.8 slow cues and >=3 playback_rate=1.0 native cues")
def t1_f04_02() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, _, debrief = h.split_drama_and_debrief_cues(cs)
        dlg = [c for c in debrief if c.kind == "dialogue"]
        assert len(dlg) > 0
        slow = [c for c in dlg if abs(float(getattr(c, "playback_rate", 1.0)) - 0.8) < 1e-3]
        native = [
            c for c in dlg
            if abs(float(getattr(c, "playback_rate", 1.0)) - 1.0) < 1e-3
            and c.language_code in ("en", "zh-en")
        ]
        assert len(slow) >= 3, f"{vid}: Debrief slow 0.8x count={len(slow)} < 3"
        assert len(native) >= 3, f"{vid}: Debrief native 1.0x EN/ZH-EN count={len(native)} < 3"


@test("T1_F04_03", "F04", "Every variant's Debrief has >=3 shadowing cues with explicit repeat gap_after_s >= 1.8s")
def t1_f04_03() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, _, debrief = h.split_drama_and_debrief_cues(cs)
        gaps = [
            c
            for c in debrief
            if c.kind == "dialogue"
            and abs(float(getattr(c, "playback_rate", 1.0)) - 1.0) < 1e-3
            and c.language_code in ("en", "zh-en")
            and 1.8 <= float(c.gap_after_s) <= 10.0
        ]
        assert len(gaps) >= 3, f"{vid}: Debrief 1.0x shadowing cues with gap>=1.8s = {len(gaps)} < 3"


@test("T1_F04_04", "F04", "Debrief contrasts Chinglish literal vs C-suite native and drills >=3 shared E001 target phrases")
def t1_f04_04() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, _, debrief = h.split_drama_and_debrief_cues(cs)
        assert len(debrief) > 0
        raw_blob = " ".join(h.strip_inline_tags(c.text)[1] for c in debrief if c.kind == "dialogue")
        norm = h.normalize_for_phrase_match(raw_blob)
        has_contrast = any(
            k in raw_blob or k in norm
            for k in ("直译", "中式", "chinglish", "别说", "不要说", "菜鸟", "对比")
        )
        assert has_contrast, f"{vid}: Debrief missing Chinglish vs C-suite contrast cues"
        hits = 0
        for _pid, _lbl, and_clauses in h.E001_MANDATORY_PHRASES:
            if any(any(a in norm for a in alts) for alts in and_clauses):
                hits += 1
        assert hits >= 3, f"{vid}: Debrief drills only {hits} E001 target phrases (<3)"


@test("T1_F04_05", "F04", "Debrief is hosted in-world by lin_chen (plus zhou_mo in VB) in studio_warm/dry space without teacher clichés")
def t1_f04_05() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, _, debrief = h.split_drama_and_debrief_cues(cs)
        dlg = [c for c in debrief if c.kind == "dialogue"]
        assert len(dlg) > 0
        roles = {c.role_id for c in dlg}
        assert "lin_chen" in roles, f"{vid}: lin_chen missing from Debrief roles={sorted(roles)}"
        if vid == "E001_VB":
            assert "zhou_mo" in roles, f"E001_VB: zhou_mo missing from taxi post-mortem Debrief"
        spaces = {c.acoustic_space for c in dlg}
        assert spaces & {"studio_warm", "dry", "boardroom"}, f"{vid}: unexpected Debrief acoustic spaces {spaces}"
        h.oracle_standalone_ip_and_banned_cliches(cs)


# ===========================================================================
# F05 — AI Consumer Hardware Global Expansion Unicorn (5 tests)
# ===========================================================================

@test("T1_F05_01", "F05", "SHOW_BIBLE.md defines NovaEdge Technologies (灵犀智造), NovaEdge Glass, NovaDock, and SZ/SV/London/SE Asia")
def t1_f05_01() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    assert "NovaEdge" in bible and "灵犀智造" in bible, "SHOW_BIBLE.md missing NovaEdge / 灵犀智造"
    assert "NovaEdge Glass" in bible, "SHOW_BIBLE.md missing flagship SKU NovaEdge Glass"
    assert "NovaDock" in bible, "SHOW_BIBLE.md missing SKU NovaDock"
    for geo in ("深圳", "硅谷", "伦敦", "东南亚"):
        assert geo in bible, f"SHOW_BIBLE.md missing geography {geo!r}"


@test("T1_F05_02", "F05", "All 4 E001 variants ground drama in NovaEdge hardware unicorn stakes")
def t1_f05_02() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        blob = " ".join(c.text for c in cs.cues if c.kind == "dialogue")
        low = blob.lower()
        assert "novaedge" in low or "灵犀" in blob, f"{vid}: missing NovaEdge/灵犀 brand identity"
        assert any(k in low or k in blob for k in ("glass", "hardware", "眼镜", "硬件", "设备", "供应链", "深圳")), (
            f"{vid}: missing consumer hardware context"
        )


@test("T1_F05_03", "F05", "Season 1 blueprint covers all 5 core vertical battlegrounds across 24 episodes")
def t1_f05_03() -> None:
    bp = h.load_text_file(h.PATH_SEASON1_BLUEPRINT, "SEASON1_24EP_BLUEPRINT.md")
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    combined = (bp + "\n" + json.dumps(smap, ensure_ascii=False)).lower()
    pillars = {
        "retail_margin": ("selfridges", "best buy", "渠道", "毛利", "零售", "margin"),
        "vc_valuation": ("series c", "估值", "融资", "cap table", "可转债", "vc"),
        "compute_bills": ("token", "算力", "推理", "compute", "gpu", "inference"),
        "privacy_compliance": ("gdpr", "ai act", "隐私", "合规", "欧盟", "诉讼"),
        "tariffs_supply_chain": ("关税", "tariff", "供应链", "东南亚", "越南", "产线"),
    }
    for pname, kws in pillars.items():
        assert any(k in combined for k in kws), f"Season 1 blueprint missing vertical battleground {pname!r}"


@test("T1_F05_04", "F05", "voice_casting_registry.json defines >=4 corporate/hardware sonic_motifs with no-voice English prompts")
def t1_f05_04() -> None:
    reg = h.load_registry_safe()
    assert len(reg.sonic_motifs) >= 4, f"Expected >=4 sonic_motifs, got {len(reg.sonic_motifs)}"
    for mid, motif in reg.sonic_motifs.items():
        prompt = motif.sfx_prompt.strip()
        assert prompt and h.count_en_words(prompt) >= 4, f"Motif {mid}: sfx_prompt too short/non-English: {prompt!r}"
        low = prompt.lower()
        assert any(k in low for k in ("no human voice", "no voice", "no speech", "no vocals")), (
            f"Motif {mid}: missing no-voice guardrail in sfx_prompt: {prompt!r}"
        )


@test("T1_F05_05", "F05", "season1_24ep_map.json structures exactly 4 sequential arcs of 6 episodes each (24 total)")
def t1_f05_05() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    res = h.oracle_season1_24ep_bijection(smap)
    assert res["arc_counts"] == {1: 6, 2: 6, 3: 6, 4: 6}


# ===========================================================================
# F06 — 85% US + London RP / 15% Intl Accent Matrix (5 tests)
# ===========================================================================

@test("T1_F06_01", "F06", "Core cast roles carry exact canonical accent_codes in voice_casting_registry.json")
def t1_f06_01() -> None:
    from aigc_audio_pipeline.models import VoiceProfile

    h.require_dataclass_fields(VoiceProfile, ("accent_code",))
    reg = h.load_registry_safe()
    for rid in h.CANONICAL_CORE_ROLES:
        assert rid in reg.roles, f"Missing core role {rid!r}"
        actual = reg.roles[rid].accent_code
        expected = h.EXPECTED_ROLE_ACCENTS[rid]
        assert actual == expected, f"Core role {rid}: accent_code={actual!r}, expected {expected!r}"


@test("T1_F06_02", "F06", "International guest pool roles declared with exact accent_codes and non-caricature requirements")
def t1_f06_02() -> None:
    reg = h.load_registry_safe()
    for rid in h.CANONICAL_GUEST_ROLES:
        assert rid in reg.roles, f"Missing international guest role {rid!r}"
        prof = reg.roles[rid]
        assert prof.accent_code == h.EXPECTED_ROLE_ACCENTS[rid], (
            f"Guest role {rid}: accent_code={prof.accent_code!r}, expected {h.EXPECTED_ROLE_ACCENTS[rid]!r}"
        )
        assert prof.accent_requirement.strip(), f"Guest role {rid}: empty accent_requirement"


@test("T1_F06_03", "F06", "100% of pure EN duration in all 4 E001 variants comes from core US + London RP cast (0 guest accents)")
def t1_f06_03() -> None:
    reg = h.load_registry_safe()
    variants = h.load_all_e001_variants()
    res = h.oracle_accent_matrix_budget(reg, e001_cue_sheets=variants)
    assert len(res["e001"]) == 4


@test("T1_F06_04", "F06", "Season-wide mean core_us_uk_en_pct >= 85.0% with international guests concentrated in E011/E013/E016")
def t1_f06_04() -> None:
    reg = h.load_registry_safe()
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    res = h.oracle_accent_matrix_budget(reg, season_map=smap)
    assert res["season_mean_us_uk_pct"] is not None and res["season_mean_us_uk_pct"] >= 85.0
    eps_by_id = {ep["episode_id"]: ep for ep in smap["episodes"]}
    guest_eps = [eid for eid in ("E011", "E013", "E016") if float(eps_by_id[eid]["core_us_uk_en_pct"]) < 100.0]
    assert len(guest_eps) >= 2, (
        f"Expected international guest accents concentrated in E011/E013/E016, found <100% only on {guest_eps}"
    )


@test("T1_F06_05", "F06", "ACCENT_AND_PROSODY_MANUAL.md specifies US/UK RP phonology, bilingual isolation, and non-caricature guest clarity")
def t1_f06_05() -> None:
    manual = h.load_text_file(h.PATH_ACCENT_MANUAL, "ACCENT_AND_PROSODY_MANUAL.md")
    low = manual.lower()
    assert len(manual) >= 2500, f"ACCENT_AND_PROSODY_MANUAL.md too short ({len(manual)} chars)"
    assert "rp" in low and ("美音" in manual or "general american" in low), "Missing US + London RP phonological spec"
    assert any(k in manual for k in ("同一母语", "双语", "口音串味", "bilingual", "lin_chen")), "Missing bilingual protagonist strategy"
    assert any(k in manual for k in ("刻板", "漫画化", "caricature", "清晰", "可控")), "Missing non-caricature guest guideline"


# ===========================================================================
# F07 — HBO Restrained Realism & Dynamic Executive Rate (5 tests)
# ===========================================================================

@test("T1_F07_01", "F07", "Crosstalk interruption counts meet variant floors (VA>=6, VB>=4, VC>=6, VD>=3)")
def t1_f07_01() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        ct = [c for c in cs.cues if c.kind == "dialogue" and -0.25 <= float(c.gap_after_s) <= -0.05]
        need = h.VARIANT_CROSSTALK_MIN[vid]
        assert len(ct) >= need, f"{vid}: crosstalk count={len(ct)} < {need}"


@test("T1_F07_02", "F07", "Each E001 variant uses >=5 distinct HBO corporate/restrained inline delivery tags")
def t1_f07_02() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        tags_used: set[str] = set()
        for cue in cs.cues:
            if cue.kind != "dialogue":
                continue
            tags, _ = h.strip_inline_tags(cue.text)
            for t in tags:
                tags_used.add(t.strip().lower())
        assert len(tags_used) >= 5, f"{vid}: only {len(tags_used)} distinct delivery tags used: {sorted(tags_used)}"


@test("T1_F07_03", "F07", "Zero melodrama yelling tags ([shouting]/[screaming]/[hysterical]/[roaring]) in E001 drama cues")
def t1_f07_03() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, drama_cues, _ = h.split_drama_and_debrief_cues(cs)
        assert len(drama_cues) > 0
        for cue in drama_cues:
            if cue.kind != "dialogue":
                continue
            tags, _ = h.strip_inline_tags(cue.text)
            bad = [t for t in tags if t.strip().lower() in h.BANNED_MELODRAMA_YELLING_TAGS]
            assert not bad, f"{vid} {cue.cue_id}: forbidden melodrama yelling tag(s) {bad}"


@test("T1_F07_04", "F07", "Single-turn HBO punchiness: median EN <=45w, max EN <=65w, max ZH <=115 chars across all 4 variants")
def t1_f07_04() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        _, drama_cues, _ = h.split_drama_and_debrief_cues(cs)
        en_lens: list[int] = []
        zh_lens: list[int] = []
        for cue in drama_cues:
            if cue.kind != "dialogue":
                continue
            _, sp = h.strip_inline_tags(cue.text)
            if cue.language_code == "en":
                w = h.count_en_words(sp)
                en_lens.append(w)
                assert w <= 65, f"{vid} {cue.cue_id}: EN turn too long ({w} > 65 words)"
            elif cue.language_code == "zh":
                ch = h.count_cjk_chars(sp)
                zh_lens.append(ch)
                assert ch <= 115, f"{vid} {cue.cue_id}: ZH turn too long ({ch} > 115 chars)"
        assert len(en_lens) >= 10, f"{vid}: too few EN drama turns ({len(en_lens)})"
        med = statistics.median(en_lens)
        assert med <= 45.0, f"{vid}: median EN drama turn={med:.1f} words > 45"


@test("T1_F07_05", "F07", "ACCENT_AND_PROSODY_MANUAL.md and RESEARCH_REPORT.md ground rate targets in empirical 170.2 WPM")
def t1_f07_05() -> None:
    manual = h.load_text_file(h.PATH_ACCENT_MANUAL, "ACCENT_AND_PROSODY_MANUAL.md")
    report = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    combined = manual + "\n" + report
    assert "170.2" in combined, "Missing empirical corpus median 170.2 WPM citation"
    assert any(k in manual.lower() for k in ("wpm", "词/分", "词每分", "words per minute")), (
        "ACCENT_AND_PROSODY_MANUAL.md missing speech-rate unit (WPM / 词/分)"
    )
    assert re.search(r"1[45]\d\s*[-–—~～至]\s*1[789]\d", manual), (
        "ACCENT_AND_PROSODY_MANUAL.md missing 150-185 (or 145-185) WPM drama rate target"
    )
    assert re.search(r"0\.8[0x]?", manual), "ACCENT_AND_PROSODY_MANUAL.md missing 0.80x slow breakdown spec"


# ===========================================================================
# F08 — 10–14 Min Commuter Runtime × 24-Ep Season 1 (5 tests)
# ===========================================================================

@test("T1_F08_01", "F08", "E001_VA hits total [600, 840]s, drama [480, 600]s, debrief [165, 210]s")
def t1_f08_01() -> None:
    h.oracle_runtime_and_debrief_windows(h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VA"]))


@test("T1_F08_02", "F08", "E001_VB hits total [600, 840]s, drama [480, 600]s, debrief [165, 210]s")
def t1_f08_02() -> None:
    h.oracle_runtime_and_debrief_windows(h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VB"]))


@test("T1_F08_03", "F08", "E001_VC hits total [600, 840]s, drama [480, 600]s, debrief [165, 210]s")
def t1_f08_03() -> None:
    h.oracle_runtime_and_debrief_windows(h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VC"]))


@test("T1_F08_04", "F08", "E001_VD hits total [600, 840]s, drama [480, 600]s, debrief [165, 210]s")
def t1_f08_04() -> None:
    h.oracle_runtime_and_debrief_windows(h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VD"]))


@test("T1_F08_05", "F08", "Season 1 map & blueprint define exact monotonic E001..E024 and 10-14 min commuter format")
def t1_f08_05() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    bp = h.load_text_file(h.PATH_SEASON1_BLUEPRINT, "SEASON1_24EP_BLUEPRINT.md")
    eps = smap.get("episodes", [])
    assert [e["episode_id"] for e in eps] == [f"E{i:03d}" for i in range(1, 25)]
    assert any(k in bp for k in ("10–14", "10-14", "10~14", "通勤")), "SEASON1_24EP_BLUEPRINT.md missing 10-14 min commuter spec"


# ===========================================================================
# F09 — Podcast Main Disk + 45s Viral Clip + Paid Companion Loop (5 tests)
# ===========================================================================

@test("T1_F09_01", "F09", "LAUNCH_KIT_AND_E001_45S_CLIPS.md covers Xiaoyuzhou, Ximalaya, and WeChat Listen packaging")
def t1_f09_01() -> None:
    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    for platform in ("小宇宙", "喜马拉雅", "微信听书"):
        assert platform in kit, f"Launch kit missing podcast platform {platform!r}"
    assert any(k in kit for k in ("Show Notes", "shownotes", "单集简介", "标题")), "Launch kit missing titles/show notes"


@test("T1_F09_02", "F09", "LAUNCH_KIT_AND_E001_45S_CLIPS.md defines executable 38-55s viral cutlists mapped to real E001 cue_ids")
def t1_f09_02() -> None:
    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    variants = h.load_all_e001_variants()
    cutlists = h.extract_viral_cutlists_from_markdown(kit, variants)
    assert len(cutlists) >= 1, "Expected >= 1 executable 38-55s viral clip cutlist in LAUNCH_KIT_AND_E001_45S_CLIPS.md"
    h.oracle_viral_45s_cutlist_and_rubric(cutlists=cutlists, cue_sheets_by_variant=variants)


@test("T1_F09_03", "F09", "Each 45s viral clip spec defines 3s conflict hook, A vs B headline, golden English keyword, and funnel CTA")
def t1_f09_03() -> None:
    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    variants = h.load_all_e001_variants()
    cutlists = h.extract_viral_cutlists_from_markdown(kit, variants)
    assert len(cutlists) >= 1, "Expected >= 1 executable 38-55s viral clip cutlist in LAUNCH_KIT_AND_E001_45S_CLIPS.md"
    for cl in cutlists:
        assert cl["has_hook"], f"Cutlist {cl['variant_id']} missing 3s conflict hook"
        assert cl["has_cta"], f"Cutlist {cl['variant_id']} missing funnel CTA"
        assert cl["has_title"], f"Cutlist {cl['variant_id']} missing A vs B / conflict title"


@test("T1_F09_04", "F09", "E001_BILINGUAL_COMPANION_MANUAL.md delivers full study companion with shadowing checklist and paid CTA")
def t1_f09_04() -> None:
    manual = h.load_text_file(h.PATH_COMPANION_MD, "E001_BILINGUAL_COMPANION_MANUAL.md")
    assert len(manual) >= 3000, f"Companion manual too short ({len(manual)} chars)"
    assert any(k in manual for k in ("跟读", "打卡", "Shadowing", "0.8")), "Companion manual missing shadowing checklist"
    assert any(k in manual for k in ("专栏", "社群", "付费", "精读", "会员")), "Companion manual missing backend monetization CTA"


@test("T1_F09_05", "F09", "All 24 episodes in season1_24ep_map.json define a non-empty viral_45s_hook")
def t1_f09_05() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    eps = smap.get("episodes", [])
    assert len(eps) == 24
    for ep in eps:
        hook = str(ep.get("viral_45s_hook", "")).strip()
        assert len(hook) >= 10, f"{ep.get('episode_id')}: viral_45s_hook too short/empty: {hook!r}"


# ===========================================================================
# F10 — Zero-API Colab 96GB Open-Weight Golden Stack (5 tests)
# ===========================================================================

@test("T1_F10_01", "F10", "voice_casting_registry.json uses canonical 96GB open-weight model IDs (zero ElevenLabs defaults)")
def t1_f10_01() -> None:
    raw = h.load_json_file(h.PATH_REGISTRY, "voice_casting_registry.json")
    reg = h.load_registry_safe()
    for key, expected in h.CANONICAL_MODEL_IDS.items():
        assert raw.get(key) == expected, f"Raw registry JSON {key}={raw.get(key)!r}, expected {expected!r}"
        assert getattr(reg, key) == expected, f"Loaded VoiceCastingRegistry.{key}={getattr(reg, key)!r}, expected {expected!r}"


@test("T1_F10_02", "F10", "AST audit proves 0 ElevenLabs API imports/calls and 0 edge-tts production usage in all 3 Colab scripts")
def t1_f10_02() -> None:
    for script in (h.COLAB_PREPARE_ANCHORS, h.COLAB_RUN_STUDIO, h.COLAB_LAUNCH_G4):
        src = h.load_text_file(script, script.name)
        h.oracle_ast_zero_api_and_zero_edge_tts(src, script.name)


@test("T1_F10_03", "F10", "run_global_edge_96gb_studio.py exposes required CLI flags and HBO instrumental BGM guardrail")
def t1_f10_03() -> None:
    flags = h.get_script_help_flags(h.COLAB_RUN_STUDIO)
    for req in ("--offline-dry-run", "--skip-existing", "--episodes", "--studio-dir", "--output-dir", "--cache-dir"):
        assert req in flags, f"run_global_edge_96gb_studio.py --help missing {req}"
    src = h.load_text_file(h.COLAB_RUN_STUDIO, h.COLAB_RUN_STUDIO.name)
    assert "no vocal" in src.lower() or "instrumental" in src.lower(), "Studio script missing instrumental BGM guardrail"
    assert "no human voice" in src.lower() or "no speech" in src.lower(), "Studio script missing no-voice foley guardrail"


@test("T1_F10_04", "F10", "launch_g4_global_edge_drama3.py exposes --offline-dry-run, --episodes, --skip-existing, and v2 anchor guard")
def t1_f10_04() -> None:
    flags = h.get_script_help_flags(h.COLAB_LAUNCH_G4)
    for req in ("--offline-dry-run", "--episodes", "--skip-existing"):
        assert req in flags, f"launch_g4_global_edge_drama3.py --help missing {req}"
    src = h.load_text_file(h.COLAB_LAUNCH_G4, h.COLAB_LAUNCH_G4.name)
    assert "v2_real_human_studio" in src, "Launcher missing v2_real_human_studio anchor schema guard"
    assert ".done" in src, "Launcher missing atomic .done Drive sync marker logic"


@test("T1_F10_05", "F10", "Global_Edge_96GB_Drama3_Studio.ipynb is valid nbformat 4 G4 notebook with Mode A/B and launcher flag parity")
def t1_f10_05() -> None:
    nb = h.load_json_file(h.COLAB_NOTEBOOK, h.COLAB_NOTEBOOK.name)
    launcher_flags = h.get_script_help_flags(h.COLAB_LAUNCH_G4)
    h.oracle_notebook_and_bundle_integrity(notebook_data=nb, launcher_help_flags=launcher_flags)


# ===========================================================================
# F11 — 5-Pillar Pre-Production Research Report (5 tests)
# ===========================================================================

@test("T1_F11_01", "F11", "RESEARCH_REPORT.md contains all 5 mandatory pre-production research pillars")
def t1_f11_01() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    low = rep.lower()
    pillars = {
        "market_podcast": ("小宇宙", "喜马拉雅", "播客", "通勤"),
        "audience_b1_c1": ("b1", "c1", "受众", "痛点", "付费"),
        "competitor_teardown": ("竞品", "对标", "差异化", "esl"),
        "corpus_100_analysis": ("100", "170.2", "语料", "1,408", "1408"),
        "accent_prosody_science": ("85%", "rp", "0.8", "心理语言", "语速", "口音"),
    }
    for pname, kws in pillars.items():
        assert sum(1 for k in kws if k in low or k in rep) >= 2, (
            f"RESEARCH_REPORT.md missing or thin on pillar {pname!r}"
        )


@test("T1_F11_02", "F11", "RESEARCH_REPORT.md cites verified corpus totals (100 clips, 25x4, 1408 segments, 170.2 WPM)")
def t1_f11_02() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    assert "100" in rep
    assert "25" in rep
    assert "1,408" in rep or "1408" in rep, "RESEARCH_REPORT.md missing 1,408 total segments"
    assert "170.2" in rep, "RESEARCH_REPORT.md missing 170.2 median WPM"
    assert any(x in rep for x in ("14,420", "14420", "14,392", "14392")), (
        "RESEARCH_REPORT.md missing empirical EN word count (~14,420 / 14,392)"
    )


@test("T1_F11_03", "F11", "RESEARCH_REPORT.md cites >=10 real corpus clip_ids and documents honest world_bridge gap audit")
def t1_f11_03() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    cited = set(re.findall(r"\b(?:0[1-5]_(?:AI|BIZ|FIN|USCHINA)_[A-Za-z]+|\d{3}_(?:AI|BIZ|FIN|USC))\b", rep))
    valid_cited = cited & h.EXPECTED_100_CLIP_IDS
    assert len(valid_cited) >= 10, f"RESEARCH_REPORT.md cites only {len(valid_cited)} valid clip_ids (<10)"
    assert "world_bridge" in rep.lower() or "0次" in rep or "零出现" in rep or "未出现" in rep, (
        "RESEARCH_REPORT.md missing honest world_bridge zero-hit gap disclosure"
    )


@test("T1_F11_04", "F11", "RESEARCH_REPORT.md analyzes podcast distribution funnel and competitor differentiation")
def t1_f11_04() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    for term in ("小宇宙", "微信视频号"):
        assert term in rep, f"RESEARCH_REPORT.md missing distribution channel {term!r}"
    assert any(k in rep for k in ("45秒", "45s", "38", "切片引流")), "RESEARCH_REPORT.md missing 45s viral funnel analysis"
    assert any(k in rep.lower() for k in ("succession", "继承之战", "hbo", "硅谷")), "RESEARCH_REPORT.md missing HBO drama positioning"


@test("T1_F11_05", "F11", "RESEARCH_REPORT.md documents psycholinguistic rationale for 85%/15% accents and 0.80x + 1.0x shadowing")
def t1_f11_05() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    assert "85%" in rep and "15%" in rep, "RESEARCH_REPORT.md missing 85%/15% accent quota rationale"
    assert "0.8" in rep and any(k in rep for k in ("跟读", "shadowing", "慢速")), (
        "RESEARCH_REPORT.md missing 0.80x slow + shadowing psycholinguistic rationale"
    )


# ===========================================================================
# F12 — Reproducible 100-Clip Corpus Extraction ETL (6 tests)
# ===========================================================================

@test("T1_F12_01", "F12", "extract_100_clips_corpus.py CLI executes cleanly into mktemp -d and writes all 3 deliverables")
def t1_f12_01() -> None:
    h.require_file(h.RAW_ARSENAL_JSON, "/tmp/arsenal_100_queue.json")
    out_flag = h.probe_script_flag(h.SCRIPT_EXTRACT_CORPUS, ("--out-dir", "--output-dir"))
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f12_"))
    try:
        proc = h.run_python_script(
            h.SCRIPT_EXTRACT_CORPUS,
            ["--source", str(h.RAW_ARSENAL_JSON), out_flag, str(tmp)],
            timeout=120,
        )
        assert proc.returncode == 0, f"extract_100_clips_corpus.py failed (rc={proc.returncode}): {proc.stderr}"
        for fname in ("corpus_100_structured.json", "executive_lexicon.json", "CORPUS_INTELLIGENCE_REPORT.md"):
            p = tmp / fname
            assert p.is_file() and p.stat().st_size > 200, f"Expected non-empty {fname} in {tmp}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F12_02", "F12", "corpus_100_structured.json matches PROJECT.md §3 schema, 25x4 topics, 1408 segs, median WPM ~170.2")
def t1_f12_02() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    res = h.oracle_corpus_100_etl_integrity(corp)
    assert res["total_clips"] == 100
    assert res["total_segments"] == 1408


@test("T1_F12_03", "F12", "corpus_100_structured.json preserves exact 100/100 clip_ids including 030_AI/030_BIZ & 054_BIZ/054_FIN")
def t1_f12_03() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    raw_by_id = h.load_raw_arsenal_by_id()
    clips_by_id = {c["clip_id"]: c for c in corp["clips"]}
    assert set(clips_by_id.keys()) == set(raw_by_id.keys()) == set(h.EXPECTED_100_CLIP_IDS)
    for col_id in h.COLLIDING_PREFIX_IDS:
        assert col_id in clips_by_id
    assert clips_by_id["030_AI"]["topic_key"] == "AI"
    assert clips_by_id["030_BIZ"]["topic_key"] == "BUSINESS"
    assert clips_by_id["054_BIZ"]["topic_key"] == "BUSINESS"
    assert clips_by_id["054_FIN"]["topic_key"] == "FINANCE"


@test("T1_F12_04", "F12", "corpus_100_structured.json logs >=20 auditable ASR corrections while preserving en_raw verbatim")
def t1_f12_04() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    corr = corp.get("asr_corrections_applied", [])
    assert len(corr) >= 20, f"Expected >=20 ASR corrections, got {len(corr)}"
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    assert "[snorts]" in by_id["087_USC"]["en_raw"], "en_raw must preserve original [snorts]"
    assert "[snorts]" not in by_id["087_USC"]["en_clean"], "en_clean must strip [snorts]"
    assert "law of holds" in by_id["069_FIN"]["en_raw"].lower(), "en_raw must preserve original 'law of holds'"
    assert "law of holds" not in by_id["069_FIN"]["en_clean"].lower(), "en_clean must normalize 'law of holds'"


@test("T1_F12_05", "F12", "All 100 clips derive non-empty inferred_speakers and empirical WPM in [110, 245]")
def t1_f12_05() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    clips = corp.get("clips", [])
    assert len(clips) == 100
    for c in clips:
        sp = c.get("inferred_speakers")
        assert isinstance(sp, list) and len(sp) >= 1 and all(str(x).strip() for x in sp), (
            f"{c['clip_id']}: empty inferred_speakers={sp!r}"
        )
        wpm = float(c.get("wpm", 0.0))
        assert 110.0 <= wpm <= 245.0, f"{c['clip_id']}: out-of-range wpm={wpm}"


@test("T1_F12_06", "F12", "extract_100_clips_corpus.py produces deterministic output across two clean runs")
def t1_f12_06() -> None:
    h.require_file(h.RAW_ARSENAL_JSON, "/tmp/arsenal_100_queue.json")
    out_flag = h.probe_script_flag(h.SCRIPT_EXTRACT_CORPUS, ("--out-dir", "--output-dir"))
    tmp1 = Path(tempfile.mkdtemp(prefix="ge_e2e_det1_"))
    tmp2 = Path(tempfile.mkdtemp(prefix="ge_e2e_det2_"))
    try:
        for d in (tmp1, tmp2):
            p = h.run_python_script(
                h.SCRIPT_EXTRACT_CORPUS,
                ["--source", str(h.RAW_ARSENAL_JSON), out_flag, str(d)],
                timeout=120,
            )
            assert p.returncode == 0, f"Determinism run failed: {p.stderr}"

        def _strip_ts(obj):
            if isinstance(obj, dict):
                return {
                    k: _strip_ts(v)
                    for k, v in obj.items()
                    if k not in ("generated_at", "exported_at", "updated_at", "timestamp")
                }
            if isinstance(obj, list):
                return [_strip_ts(x) for x in obj]
            return obj

        for fname in ("corpus_100_structured.json", "executive_lexicon.json"):
            a = _strip_ts(h.load_json_file(tmp1 / fname))
            b = _strip_ts(h.load_json_file(tmp2 / fname))
            assert a == b, f"{fname} differed between two consecutive deterministic ETL runs"
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)
        shutil.rmtree(tmp2, ignore_errors=True)


# ===========================================================================
# F13 — Top-Level Show Bible + Accent & Prosody Manual (5 tests)
# ===========================================================================

@test("T1_F13_01", "F13", "SHOW_BIBLE.md documents all 8 canonical roles with 4-layer character profiles")
def t1_f13_01() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    reg = h.load_registry_safe()
    for rid in h.CANONICAL_ALL_8_ROLES:
        dname = reg.roles[rid].display_name if rid in reg.roles else rid
        assert rid in bible or dname in bible, f"SHOW_BIBLE.md missing canonical role {rid!r} ({dname!r})"
    assert len(bible) >= 4000, f"SHOW_BIBLE.md too thin ({len(bible)} chars)"
    for kw_group in (("声线", "音色", "vocal"), ("语言", "口音", "accent"), ("禁忌", "禁止", "forbidden")):
        assert any(k in bible.lower() or k in bible for k in kw_group), f"SHOW_BIBLE.md missing profile layer {kw_group}"


@test("T1_F13_02", "F13", "SHOW_BIBLE.md documents bilingual code-switching, corporate acoustic spaces, OST palette, and mode")
def t1_f13_02() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    for space in ("boardroom", "inner_monologue", "phone_call", "studio_warm"):
        assert space in bible, f"SHOW_BIBLE.md missing corporate acoustic_space {space!r}"
    assert "bilingual_business_drama" in bible or "business_english_drama" in bible, (
        "SHOW_BIBLE.md missing engine mode/domain contract reference"
    )
    assert any(k in bible.lower() for k in ("ace-step", "ost", "motif", "音景", "配乐")), (
        "SHOW_BIBLE.md missing OST / sonic motif palette"
    )


@test("T1_F13_03", "F13", "ACCENT_AND_PROSODY_MANUAL.md defines HBO acting direction, crosstalk [-0.25, -0.05]s, and 0.80x prosody")
def t1_f13_03() -> None:
    manual = h.load_text_file(h.PATH_ACCENT_MANUAL, "ACCENT_AND_PROSODY_MANUAL.md")
    assert any(k in manual for k in ("-0.25", "-0.05", "打断", "抢话", "crosstalk")), "Manual missing crosstalk timing spec"
    assert any(k in manual for k in ("降调", "克制", "礼貌带刀", "HBO", "呼吸")), "Manual missing HBO restrained acting rules"
    assert "0.8" in manual and "1.0" in manual, "Manual missing 0.80x / 1.0x prosody contrast"


@test("T1_F13_04", "F13", "Every role in voice_casting_registry.json has valid lowercase ASCII signature_tags and non-empty forbidden_habits")
def t1_f13_04() -> None:
    reg = h.load_registry_safe()
    assert len(reg.roles) >= 8
    ascii_tag_re = re.compile(r"^[a-z0-9\s,\-']+$")
    for rid, prof in reg.roles.items():
        assert len(prof.signature_tags) >= 1, f"{rid}: empty signature_tags"
        for tag in prof.signature_tags:
            clean = tag.strip("[]").strip()
            assert ascii_tag_re.fullmatch(clean), f"{rid}: invalid signature_tag {tag!r} (must be lowercase ASCII)"
        assert len(prof.forbidden_habits) >= 1 and all(x.strip() for x in prof.forbidden_habits), (
            f"{rid}: empty forbidden_habits"
        )


@test("T1_F13_05", "F13", "SHOW_BIBLE.md & ACCENT_AND_PROSODY_MANUAL.md specify Colab 96GB real-human studio stack and 0 Xianxia plot drift")
def t1_f13_05() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    manual = h.load_text_file(h.PATH_ACCENT_MANUAL, "ACCENT_AND_PROSODY_MANUAL.md")
    h.assert_no_xianxia_plot_drift(bible, "SHOW_BIBLE.md")
    combined_raw = bible + "\n" + manual
    combined_low = combined_raw.lower()
    has_engine = any(k in combined_low for k in ("drama-3", "drama 3", "96gb"))
    has_real_human = (
        "v2_real_human_studio" in combined_low
        or "real-human" in combined_low
        or "real human" in combined_low
        or ("真人" in combined_raw and any(k in combined_raw for k in ("干声", "锚点", "声纹", "录音棚")))
    )
    assert has_engine and has_real_human, (
        "Creative docs must specify Colab 96GB Drama 3 + real-human studio voice anchor stack"
    )


# ===========================================================================
# F14 — 24-Episode Season 1 Blueprint (100/100 Bijective Map) (5 tests)
# ===========================================================================

@test("T1_F14_01", "F14", "season1_24ep_map.json defines 24 episodes with all 12 required PROJECT.md §3 schema keys")
def t1_f14_01() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    h.oracle_season1_24ep_bijection(smap)


@test("T1_F14_02", "F14", "season1_24ep_map.json achieves mathematical 100/100 bijection against /tmp/arsenal_100_queue.json")
def t1_f14_02() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    raw_ids = frozenset(h.load_raw_arsenal_by_id().keys())
    res = h.oracle_season1_24ep_bijection(smap, expected_ids=raw_ids)
    assert res["unique_clips"] == 100


@test("T1_F14_03", "F14", "season1_24ep_map.json follows exact 20x4 + 4x5 clip distribution and exact 5 E001 seed clips")
def t1_f14_03() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    counts = [len(ep["primary_clip_ids"]) for ep in smap["episodes"]]
    assert counts.count(4) == 20 and counts.count(5) == 4, f"Expected 20x4 + 4x5, got 4s={counts.count(4)}, 5s={counts.count(5)}"
    assert set(smap["episodes"][0]["primary_clip_ids"]) == set(h.E001_SEED_CLIP_IDS)


@test("T1_F14_04", "F14", "SEASON1_24EP_BLUEPRINT.md documents all 24 episodes and cites all 100 clip_ids from season1_24ep_map.json")
def t1_f14_04() -> None:
    bp = h.load_text_file(h.PATH_SEASON1_BLUEPRINT, "SEASON1_24EP_BLUEPRINT.md")
    for i in range(1, 25):
        eid = f"E{i:03d}"
        assert eid in bp, f"SEASON1_24EP_BLUEPRINT.md missing episode {eid}"
    missing_cids = [cid for cid in sorted(h.EXPECTED_100_CLIP_IDS) if cid not in bp]
    assert not missing_cids, f"SEASON1_24EP_BLUEPRINT.md missing {len(missing_cids)} clip_ids: {missing_cids[:10]}"


@test("T1_F14_05", "F14", "Each of the 4 arcs spans >=2 corpus pillars while the full 24-ep season balances all 4 pillars (25x4)")
def t1_f14_05() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    by_arc: dict[int, set[str]] = {1: set(), 2: set(), 3: set(), 4: set()}
    season_counts: dict[str, int] = {"AI": 0, "BUSINESS": 0, "FINANCE": 0, "US_CHINA": 0}
    for ep in smap["episodes"]:
        arc = int(ep["arc_number"])
        for cid in ep["primary_clip_ids"]:
            topic = h.CLIP_TOPIC_LOOKUP[cid]
            by_arc[arc].add(topic)
            season_counts[topic] += 1
    for arc, topics in by_arc.items():
        assert len(topics) >= 2, f"Arc {arc} covers only {sorted(topics)}, expected >=2 corpus pillars"
    assert season_counts == {"AI": 25, "BUSINESS": 25, "FINANCE": 25, "US_CHINA": 25}, (
        f"Full-season corpus pillar counts={season_counts}, expected exact 25x4 balance"
    )


# ===========================================================================
# F15 — 96GB Real-Human Voice Casting Registry & Anchor Acquisition (6 tests)
# ===========================================================================

@test("T1_F15_01", "F15", "voice_casting_registry.json loads cleanly with domain=business_english_drama and >=8 unique locked roles")
def t1_f15_01() -> None:
    reg = h.load_registry_safe()
    assert reg.domain == "business_english_drama"
    assert len(reg.roles) >= 8
    for rid in h.CANONICAL_ALL_8_ROLES:
        assert rid in reg.roles, f"Missing canonical role {rid!r}"
    vids: list[str] = []
    for rid, prof in reg.roles.items():
        assert prof.status == "locked", f"{rid}: status={prof.status!r}, expected 'locked'"
        assert prof.voice_id.strip(), f"{rid}: empty voice_id"
        vids.append(prof.voice_id.strip())
    assert len(set(vids)) == len(vids), f"Duplicate voice_id values in registry: {vids}"


@test("T1_F15_02", "F15", "Every registered role's audition_line passes validate_v3_dialogue_text with 0 errors")
def t1_f15_02() -> None:
    reg = h.load_registry_safe()
    assert len(reg.roles) >= 8
    for rid, prof in reg.roles.items():
        h.oracle_dialogue_text_and_bilingual_rules(
            prof.audition_line, prof.default_stability, prof.language_code
        )


@test("T1_F15_03", "F15", "anchor_sources.json maps 100% of registered roles to clean real-human sources (0 edge-tts)")
def t1_f15_03() -> None:
    reg = h.load_registry_safe()
    src_cfg = h.load_json_file(h.PATH_ANCHOR_SOURCES, "anchor_sources.json")
    h.assert_anchor_sources_clean(src_cfg, list(reg.roles.keys()), label="anchor_sources.json")


@test("T1_F15_04", "F15", "VOICE_ANCHOR_ACQUISITION_SPEC.md specifies v2_real_human_studio, 44.1kHz mono -16 LUFS, clean studio dry-stem rules & bilingual lin_chen")
def t1_f15_04() -> None:
    spec = h.load_text_file(h.PATH_ANCHOR_SPEC, "VOICE_ANCHOR_ACQUISITION_SPEC.md")
    low = spec.lower()
    assert "v2_real_human_studio" in spec
    assert "44.1" in spec or "44100" in spec
    assert "-16" in spec and "lufs" in low
    assert any(k in low for k in ("afftdn", "降噪", "denoise", "发闷", "muffl", "近讲", "干声", "滤波")), (
        "Anchor spec must document clean studio dry-stem / anti-muffling audio acquisition hygiene"
    )
    assert "lin_chen" in spec or "林沉" in spec, "Anchor spec missing bilingual protagonist strategy"


@test("T1_F15_05", "F15", "prepare_global_edge_voice_anchors.py --offline-stub generates v2 manifest + WAV + .txt for every role")
def t1_f15_05() -> None:
    reg = h.load_registry_safe()
    out_flag = h.probe_script_flag(h.COLAB_PREPARE_ANCHORS, ("--output-dir", "--out-dir"))
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f15_"))
    try:
        proc = h.run_python_script(
            h.COLAB_PREPARE_ANCHORS,
            ["--registry", str(h.PATH_REGISTRY), out_flag, str(tmp), "--offline-stub"],
            timeout=60,
        )
        assert proc.returncode == 0, f"prepare_global_edge_voice_anchors.py failed: {proc.stderr}"
        manifest = h.load_json_file(tmp / "voice_cast_drama3.json", "voice_cast_drama3.json")
        h.oracle_notebook_and_bundle_integrity(voice_cast_manifest=manifest)
        assert set(manifest["characters"].keys()) == set(reg.roles.keys())
        for rid in reg.roles:
            assert (tmp / "voice_anchors" / f"{rid}.wav").is_file(), f"Missing stub WAV for {rid}"
            assert (tmp / "voice_anchors" / f"{rid}.txt").is_file(), f"Missing stub .txt sidecar for {rid}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F15_06", "F15", "Every generated stub anchor WAV is 44100 Hz mono PCM16 >= 3.0s matching its UTF-8 .txt sidecar")
def t1_f15_06() -> None:
    reg = h.load_registry_safe()
    out_flag = h.probe_script_flag(h.COLAB_PREPARE_ANCHORS, ("--output-dir", "--out-dir"))
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f15_wav_"))
    try:
        proc = h.run_python_script(
            h.COLAB_PREPARE_ANCHORS,
            ["--registry", str(h.PATH_REGISTRY), out_flag, str(tmp), "--offline-stub"],
            timeout=60,
        )
        assert proc.returncode == 0, f"Anchor stub build failed: {proc.stderr}"
        manifest = h.load_json_file(tmp / "voice_cast_drama3.json")
        for rid in reg.roles:
            wav_p = tmp / "voice_anchors" / f"{rid}.wav"
            txt_p = tmp / "voice_anchors" / f"{rid}.txt"
            res = h.oracle_audio_signal_and_atempo_ratio(wav_anchor_path=wav_p)
            assert res["wav_anchor"]["dur_s"] >= 3.0, f"{rid}.wav too short ({res['wav_anchor']['dur_s']:.2f}s < 3.0s)"
            sidecar_text = txt_p.read_text(encoding="utf-8").strip()
            assert sidecar_text, f"{rid}.txt sidecar is empty"
            assert manifest["characters"][rid]["anchor_text"].strip() == sidecar_text, (
                f"{rid}: manifest anchor_text does not match .txt sidecar verbatim"
            )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# F16 — Multi-Variant E001 Production & Comparative Evaluation Suite (6 tests)
# ===========================================================================

@test("T1_F16_01", "F16", "Public validate --require-locked-voices CLI exits 0 with 0 errors on all 5 cue sheets")
def t1_f16_01() -> None:
    h.require_file(h.PATH_REGISTRY, "voice_casting_registry.json")
    for eid, path in h.ALL_5_CUE_SHEETS.items():
        h.require_file(path, f"{eid} JSON")
        proc, payload = h.run_validate_cli(h.PATH_REGISTRY, path, require_locked_voices=True)
        assert proc.returncode == 0, f"validate CLI failed on {eid} (rc={proc.returncode}): {proc.stdout}\n{proc.stderr}"
        assert payload is not None and payload.get("valid") is True and payload.get("errors") == [], (
            f"validate CLI JSON invalid on {eid}: {payload}"
        )


@test("T1_F16_02", "F16", "All 5 exact PROJECT.md §5 cue sheets exist as paired .json + non-empty .md with matching episode_id")
def t1_f16_02() -> None:
    for expected_eid, json_p in h.ALL_5_CUE_SHEETS.items():
        cs = h.load_cue_sheet_safe(json_p)
        assert cs.episode_id == expected_eid, f"{json_p.name}: episode_id={cs.episode_id!r}, expected {expected_eid!r}"
        md_p = h.ALL_5_MD_PATHS[expected_eid]
        md_txt = h.load_text_file(md_p, md_p.name)
        assert len(md_txt) >= 500, f"{md_p.name} too short ({len(md_txt)} chars)"


@test("T1_F16_03", "F16", "All 4 E001 variants are genuinely differentiated (Jaccard < 0.70 + unique structural signatures)")
def t1_f16_03() -> None:
    variants = h.load_all_e001_variants()
    h.oracle_variant_differentiation_and_crosstalk(variants)


@test("T1_F16_04", "F16", "E001_COMPARATIVE_EVAL_RUBRIC.md defines 4-variant scorecard, 100-pt blind listening rubric, retention protocol & Hybrid-Winner Rule")
def t1_f16_04() -> None:
    rubric = h.load_text_file(h.PATH_RUBRIC_MD, "E001_COMPARATIVE_EVAL_RUBRIC.md")
    for vid in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
        assert vid in rubric, f"Rubric missing variant {vid}"
    h.oracle_viral_45s_cutlist_and_rubric(rubric_md=rubric)
    assert any(k in rubric.lower() for k in ("盲听", "blind", "recall", "回忆", "回译", "留存", "复述", "测试")), (
        "Rubric missing blind-listening / retention / comprehension evaluation protocol"
    )
    assert any(k in rubric.lower() for k in ("hybrid", "融合", "混合胜出")), (
        "Rubric missing Hybrid-Winner Decision Rule"
    )


@test("T1_F16_05", "F16", "build_e001_variants.py compiles all 5 cue sheets cleanly in isolated execution (exit 0)")
def t1_f16_05() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f16_build_"))
    try:
        proc, out_dir = h.run_build_e001_isolated(tmp)
        assert proc.returncode == 0, f"build_e001_variants.py failed (rc={proc.returncode}): {proc.stderr}\n{proc.stdout}"
        for eid, canon_json_path in h.ALL_5_CUE_SHEETS.items():
            built_json = out_dir / canon_json_path.name
            built_md = out_dir / canon_json_path.with_suffix(".md").name
            assert built_json.is_file() and built_json.stat().st_size > 200, (
                f"build_e001_variants.py did not freshly generate {built_json.name} in {out_dir}"
            )
            assert built_md.is_file() and built_md.stat().st_size > 200, (
                f"build_e001_variants.py did not freshly generate {built_md.name} in {out_dir}"
            )
            cs = h.load_cue_sheet_safe(built_json)
            assert cs.episode_id == eid and len(cs.cues) > 0, (
                f"Freshly built {built_json.name} invalid: episode_id={cs.episode_id!r}, cues={len(cs.cues)}"
            )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F16_06", "F16", "projects/global_edge/README.md documents quickstart, folder map, variant matrix, and Colab G4 launch commands")
def t1_f16_06() -> None:
    readme = h.load_text_file(h.PATH_README, "projects/global_edge/README.md")
    assert len(readme) >= 1500, f"README.md too short ({len(readme)} chars)"
    for token in ("E001_VA", "E001_VB", "E001_VC", "E001_VD", "launch_g4_global_edge_drama3.py", "validate"):
        assert token in readme, f"README.md missing key documentation token {token!r}"


# ===========================================================================
# F17 — Deterministic Pitch-Preserving 0.80x Slow Breakdown (atempo) (5 tests)
# ===========================================================================

@test("T1_F17_01", "F17", "TimelineCue.playback_rate defaults to 1.0, validates 0.8, and round-trips through EpisodeCueSheet save/load")
def t1_f17_01() -> None:
    from aigc_audio_pipeline.models import EpisodeCueSheet, TimelineCue

    h.require_dataclass_fields(TimelineCue, ("playback_rate",))
    default_cue = TimelineCue(cue_id="C1", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Hello.")
    assert default_cue.playback_rate == 1.0
    slow_cue = h.make_timeline_cue(
        cue_id="C2", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="[coach] Phantom number.", playback_rate=0.8
    )
    sheet = EpisodeCueSheet(
        episode_id="E001_RATE", chapter_number=1, title="Rate Test", mode="bilingual_business_drama", acts=[], cues=[default_cue, slow_cue]
    )
    assert sheet.validate() == []
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f17_rt_"))
    try:
        p = tmp / "rate.json"
        sheet.save(p)
        reloaded = EpisodeCueSheet.load(p)
        assert reloaded.cues[0].playback_rate == 1.0
        assert abs(reloaded.cues[1].playback_rate - 0.8) < 1e-9
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F17_02", "F17", "condition_dialogue_clip(playback_rate=0.8) stretches 2.0s 440Hz WAV to ~2.50s while preserving 440Hz pitch")
def t1_f17_02() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    h.require_signature_param(condition_dialogue_clip, "playback_rate")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f17_slow_"))
    try:
        raw_wav = h.write_sine_wav(tmp / "in_440.wav", duration_s=2.0, freq_hz=440.0, sample_rate=48000, channels=1, amplitude=0.45)
        out_wav = tmp / "out_080.wav"
        condition_dialogue_clip(raw_wav, out_wav, acoustic_space="dry", playback_rate=0.8)
        probe = h.probe_audio_ffprobe(out_wav)
        assert probe["sample_rate"] == 48000 and probe["channels"] == 2
        assert 2.35 <= probe["duration_s"] <= 2.65, f"Expected 2.50±0.15s, got {probe['duration_s']:.3f}s"
        h.oracle_audio_signal_and_atempo_ratio(
            wav_48k_path=out_wav,
            slow_wav_path=out_wav,
            base_wav_path=raw_wav,
            expected_pitch_hz=440.0,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F17_03", "F17", "condition_dialogue_clip(playback_rate=1.25) speeds up 2.0s WAV to ~1.60s")
def t1_f17_03() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    h.require_signature_param(condition_dialogue_clip, "playback_rate")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f17_fast_"))
    try:
        raw_wav = h.write_sine_wav(tmp / "in_fast.wav", duration_s=2.0, freq_hz=440.0, sample_rate=48000, channels=1)
        out_wav = tmp / "out_125.wav"
        condition_dialogue_clip(raw_wav, out_wav, acoustic_space="dry", playback_rate=1.25)
        probe = h.probe_audio_ffprobe(out_wav)
        assert probe["sample_rate"] == 48000 and probe["channels"] == 2
        assert 1.48 <= probe["duration_s"] <= 1.72, f"Expected 1.60±0.12s, got {probe['duration_s']:.3f}s"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F17_04", "F17", "1.20s raw clip stretched at playback_rate=0.8 crosses >=1.4s loudnorm gate and levels to -16 ± 2.5 LUFS")
def t1_f17_04() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    h.require_signature_param(condition_dialogue_clip, "playback_rate")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f17_gate_"))
    try:
        raw_wav = h.write_sine_wav(tmp / "in_120.wav", duration_s=1.20, freq_hz=330.0, sample_rate=48000, channels=1, amplitude=0.15)
        out_wav = tmp / "out_150.wav"
        condition_dialogue_clip(raw_wav, out_wav, acoustic_space="studio_warm", playback_rate=0.8)
        probe = h.probe_audio_ffprobe(out_wav)
        assert probe["duration_s"] >= 1.40, f"Expected stretched duration >= 1.40s, got {probe['duration_s']:.3f}s"
        lufs, tp = h.measure_loudness_ffmpeg(out_wav)
        assert -18.5 <= lufs <= -13.5, f"Expected loudnorm leveling to -16 ± 2.5 LUFS, got {lufs:.2f} LUFS"
        assert tp <= -0.5, f"Expected true peak <= -0.5 dBTP, got {tp:.2f} dBTP"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F17_05", "F17", "Markdown export renders [0.80x] badge on slow cues (omitted on 1.0x) and studio runner reuses 1.0x Drama 3 cache")
def t1_f17_05() -> None:
    from aigc_audio_pipeline.adapter import export_cue_sheet_markdown
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    reg = h.make_minimal_registry()
    sheet = EpisodeCueSheet(
        episode_id="E001_MD_RATE",
        chapter_number=1,
        title="Badge Test",
        mode="bilingual_business_drama",
        acts=[ActMusicSpec(act_id="act_5", title="Act 5 Debrief", bgm_prompt="Minimalist piano, instrumental, no vocals")],
        cues=[
            h.make_timeline_cue(cue_id="D1", act_id="act_5", kind="dialogue", role_id="lin_chen", language_code="en", text="[coach] Phantom number.", playback_rate=0.8, subtitle_translation="虚构数字。"),
            h.make_timeline_cue(cue_id="D2", act_id="act_5", kind="dialogue", role_id="lin_chen", language_code="en", text="[measured] Phantom number.", playback_rate=1.0, subtitle_translation="虚构数字。"),
        ],
    )
    md = export_cue_sheet_markdown(sheet, reg)
    d1_lines = [ln for ln in md.splitlines() if "[D1]" in ln]
    d2_lines = [ln for ln in md.splitlines() if "[D2]" in ln]
    assert len(d1_lines) == 1 and "0.80x" in d1_lines[0], f"D1 slow cue missing [0.80x] badge: {d1_lines}"
    assert len(d2_lines) == 1 and "1.00x" not in d2_lines[0] and "0.80x" not in d2_lines[0], (
        f"D2 normal 1.0x cue must omit rate badge: {d2_lines}"
    )
    assert "虚构数字。" in md, "Markdown export missing subtitle_translation"
    assert "ACE-Step" in md and "music_v2_5" not in md, "Markdown export must emit ACE-Step BGM header, not music_v2_5"

    # Real opaque-box CLI proof: identical (role_id, language_code, text) at 1.0x & 0.8x reuses 1 cached TTS stem
    h.require_ffmpeg()
    h.require_file(h.COLAB_RUN_STUDIO, "run_global_edge_96gb_studio.py")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f17_cache_"))
    try:
        h.verify_studio_08x_cache_reuse(h.COLAB_RUN_STUDIO, tmp, self_contained=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ===========================================================================
# F18 — business_english_drama Domain + Dual-Script zh-en QA & Chunking (6 tests)
# ===========================================================================

@test("T1_F18_01", "F18", "polyphones.py registers BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP and applies domain='business_english_drama'")
def t1_f18_01() -> None:
    from aigc_audio_pipeline import polyphones

    pmap = getattr(polyphones, "BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP", None)
    assert isinstance(pmap, (dict, list, tuple)) and len(pmap) > 0, (
        "M1 contract gap: polyphones.BUSINESS_ENGLISH_DRAMA_POLYPHONE_MAP missing or empty"
    )
    sample_key = next(iter(pmap.keys())) if isinstance(pmap, dict) else pmap[0][0]
    expected_val = pmap[sample_key] if isinstance(pmap, dict) else pmap[0][1]
    out = polyphones.apply_domain_polyphone_overrides(f"董事会上提到{sample_key}条款。", domain="business_english_drama")
    assert expected_val in out, f"Expected polyphone override {sample_key!r}->{expected_val!r} in {out!r}"


@test("T1_F18_02", "F18", "DRAMA3_TAG_MAP registers all 13 required HBO corporate acting tags")
def t1_f18_02() -> None:
    from aigc_audio_pipeline.drama3_adapter import DRAMA3_TAG_MAP

    missing = [t for t in h.REQUIRED_13_HBO_TAGS if t not in DRAMA3_TAG_MAP]
    assert not missing, f"M1 contract gap: DRAMA3_TAG_MAP missing HBO corporate tag(s): {missing}"


@test("T1_F18_03", "F18", "translate_cue_to_drama3_input(domain='business_english_drama') translates corporate tags cleanly across attempts 1..3")
def t1_f18_03() -> None:
    from aigc_audio_pipeline.drama3_adapter import translate_cue_to_drama3_input

    reg = h.make_minimal_registry()
    en_cue = h.make_timeline_cue(
        cue_id="T1", act_id="a1", kind="dialogue", role_id="victoria_vance",
        language_code="en", text="[icy polite] That is a phantom number, Lin.",
    )
    p1 = translate_cue_to_drama3_input(en_cue, reg.roles["victoria_vance"], attempt=1, domain="business_english_drama")
    p3 = translate_cue_to_drama3_input(en_cue, reg.roles["victoria_vance"], attempt=3, domain="business_english_drama")
    h.oracle_domain_no_xianxia_leak(drama3_prompt=p1)
    assert "phantom number" in p1.lower()
    assert "[" not in p3 and "]" not in p3 and "phantom number" in p3.lower(), f"attempt=3 must strip tags: {p3!r}"


@test("T1_F18_04", "F18", "split_cue_into_subcues_for_drama3 splits English-heavy mixed zh-en cue via combined units (cjk + 2.2*en_words)")
def t1_f18_04() -> None:
    from aigc_audio_pipeline.drama3_adapter import split_cue_into_subcues_for_drama3

    long_mixed = h.make_timeline_cue(
        cue_id="MIX1",
        act_id="a1",
        kind="dialogue",
        role_id="lin_chen",
        language_code="zh-en",
        text=(
            "[measured] 听好了。"
            "First, that convertible note charge is strictly a phantom number that never touched our operating cash account this quarter. "
            "Second, our Shenzhen hardware engineering team delivered ten times the throughput on edge silicon while keeping gross margin intact across Europe. "
            "Third, when buyers complain that cloud inference bills are eating into budgets, we show them a capital-efficient local architecture that survives a million runs."
        ),
        gap_after_s=0.45,
    )
    parts = split_cue_into_subcues_for_drama3(long_mixed, max_cjk_chars=105, max_en_words=65, domain="business_english_drama")
    assert len(parts) >= 2, f"Expected English-heavy zh-en cue to split into >=2 subcues, got {len(parts)}"
    assert parts[0].gap_after_s <= 0.25, f"Expected tight internal sub-cue gap_after_s, got {parts[0].gap_after_s}"


@test("T1_F18_05", "F18", "evaluate_dialogue_qa passes matching dual-script zh-en cue transcript")
def t1_f18_05() -> None:
    res = h.oracle_dual_script_zh_en_qa(
        "[measured] 这份财报里的 phantom number 根本不是 not a cash loss。",
        "这份财报里的 phantom number 根本不是 not a cash loss。",
        language_code="zh-en",
    )
    assert res["passed"] is True
    assert res["tail_preserved"] is True
    assert res["leaked_tags"] == []


@test("T1_F18_06", "F18", "evaluate_dialogue_qa exempts legitimate spoken business words ('confident', 'measured') from leaked-tag false positives")
def t1_f18_06() -> None:
    from aigc_audio_pipeline.qa import COMMON_TAG_WORDS

    for tag in ("deadpan", "skeptical", "guarded", "understated"):
        assert tag in COMMON_TAG_WORDS, f"M1 contract gap: corporate tag {tag!r} missing from qa.COMMON_TAG_WORDS"
    res = h.oracle_dual_script_zh_en_qa(
        "[confident] We remain confident and measured in our capital allocation.",
        "We remain confident and measured in our capital allocation.",
        language_code="en",
    )
    assert res["passed"] is True and res["leaked_tags"] == []


# ===========================================================================
# F19 — Corporate Acoustic Spaces, Dual-Line SRT, Variant Resolver & Devbox FFmpeg (6 tests)
# ===========================================================================

@test("T1_F19_01", "F19", "ALLOWED_ACOUSTIC_SPACES contains all 9 canonical spaces and mode='bilingual_business_drama' validates")
def t1_f19_01() -> None:
    from aigc_audio_pipeline.models import ALLOWED_ACOUSTIC_SPACES, EpisodeCueSheet

    for space in h.EXPECTED_9_ACOUSTIC_SPACES:
        assert space in ALLOWED_ACOUSTIC_SPACES, f"Missing acoustic space {space!r} in ALLOWED_ACOUSTIC_SPACES"
    cues = [
        h.make_timeline_cue(cue_id=f"SP_{i}", act_id="a1", kind="dialogue", role_id="lin_chen", language_code="en", text="Check space.", acoustic_space=sp)
        for i, sp in enumerate(("inner_monologue", "boardroom", "phone_call"))
    ]
    sheet = EpisodeCueSheet(episode_id="E001_SP", chapter_number=1, title="Spaces", mode="bilingual_business_drama", acts=[], cues=cues)
    assert sheet.validate() == []


@test("T1_F19_02", "F19", "condition_dialogue_clip produces valid 48kHz stereo WAVs with real DSP on phone_call, inner_monologue & boardroom vs dry")
def t1_f19_02() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f19_dsp_"))
    try:
        # 5-tone multi-tone: 100Hz (<300Hz HPF), 150Hz (proximity EQ), 1000Hz (ref), 3200Hz (presence EQ), 6000Hz (>3400Hz LPF)
        mt_in = h.write_multitone_wav(
            tmp / "multitone.wav",
            duration_s=2.0,
            freqs_amps=[(100.0, 0.18), (150.0, 0.18), (1000.0, 0.18), (3200.0, 0.18), (6000.0, 0.18)],
            sample_rate=48000,
            channels=1,
        )
        burst_in = h.write_tone_burst_wav(
            tmp / "burst.wav",
            burst_s=0.80,
            silence_s=0.80,
            freq_hz=1000.0,
            sample_rate=48000,
            channels=1,
        )
        mt_outs: dict[str, Path] = {}
        burst_outs: dict[str, Path] = {}
        for sp in ("dry", "inner_monologue", "boardroom", "phone_call"):
            mt_p = tmp / f"mt_{sp}.wav"
            condition_dialogue_clip(mt_in, mt_p, acoustic_space=sp)
            mt_outs[sp] = mt_p
            if sp in ("dry", "inner_monologue", "boardroom"):
                b_p = tmp / f"burst_{sp}.wav"
                condition_dialogue_clip(burst_in, b_p, acoustic_space=sp)
                burst_outs[sp] = b_p

        h.oracle_corporate_acoustic_spaces_dsp(
            dry_mt_wav=mt_outs["dry"],
            phone_mt_wav=mt_outs["phone_call"],
            inner_mt_wav=mt_outs["inner_monologue"],
            boardroom_mt_wav=mt_outs["boardroom"],
            dry_burst_wav=burst_outs["dry"],
            inner_burst_wav=burst_outs["inner_monologue"],
            boardroom_burst_wav=burst_outs["boardroom"],
            burst_end_s=0.80,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F19_03", "F19", "master_episode_three_bus emits dual-line SRT from subtitle_translation while TTS prompt stays pure English")
def t1_f19_03() -> None:
    from aigc_audio_pipeline.drama3_adapter import translate_cue_to_drama3_input
    from aigc_audio_pipeline.mixer import master_episode_three_bus
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    h.require_ffmpeg()
    reg = h.make_minimal_registry()
    gloss = "这是虚构数字。"
    cue = h.make_timeline_cue(
        cue_id="SRT_01",
        act_id="act_1",
        kind="dialogue",
        role_id="lin_chen",
        speaker_name="Lin Chen",
        language_code="en",
        text="[measured] That is a phantom number.",
        subtitle_translation=gloss,
        acoustic_space="boardroom",
    )
    sheet = EpisodeCueSheet(
        episode_id="E001_SRT",
        chapter_number=1,
        title="SRT Dual Line",
        mode="bilingual_business_drama",
        acts=[ActMusicSpec(act_id="act_1", title="Act 1", bgm_prompt="Minimal cello, instrumental, no vocals")],
        cues=[cue],
    )
    tts_prompt = translate_cue_to_drama3_input(cue, reg.roles["lin_chen"], domain="business_english_drama")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f19_srt_"))
    try:
        dlg_wav = h.write_sine_wav(tmp / "dlg.wav", 2.0, freq_hz=330.0)
        bgm_wav = h.write_sine_wav(tmp / "bgm.wav", 5.0, freq_hz=110.0, amplitude=0.15)
        res = master_episode_three_bus(
            sheet,
            {"SRT_01": dlg_wav},
            {"act_1": bgm_wav},
            tmp / "out",
            registry=reg,
            clean_work_dir=True,
        )
        srt_text = Path(res["subtitles_srt"]).read_text(encoding="utf-8")
        h.oracle_srt_non_overlap_and_dual_line(
            srt_text,
            expected_translations=[gloss],
            tts_prompts=[tts_prompt],
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F19_04", "F19", "VoiceProfile.accent_code round-trips cleanly and defaults to '' on legacy Buffett registry")
def t1_f19_04() -> None:
    from aigc_audio_pipeline.models import VoiceCastingRegistry, VoiceProfile

    h.require_dataclass_fields(VoiceProfile, ("accent_code",))
    reg = h.make_minimal_registry()
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f19_acc_"))
    try:
        p = tmp / "reg.json"
        reg.save(p)
        reloaded = VoiceCastingRegistry.load(p)
        assert reloaded.roles["alistair_finch"].accent_code == "uk_london_rp"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    legacy = h.load_registry_safe(h.LEGACY_BUFFETT_REGISTRY)
    assert len(legacy.roles) >= 4
    for prof in legacy.roles.values():
        assert prof.accent_code == "", f"Legacy role {prof.role_id} expected default accent_code=''"


@test("T1_F19_05", "F19", "Studio CLI variant resolver distinguishes E001_VA..E001_VD, E002, and E003A with zero collisions")
def t1_f19_05() -> None:
    h.require_ffmpeg()
    h.require_file(h.COLAB_RUN_STUDIO, "run_global_edge_96gb_studio.py")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t1_f19_res_"))
    try:
        sdir = h.build_mini_studio_dir(
            tmp / "studio",
            cue_sheets={
                "E001_VA_t.json": h.make_mini_cue_sheet("E001_VA"),
                "E001_VB_t.json": h.make_mini_cue_sheet("E001_VB"),
                "E001_VC_t.json": h.make_mini_cue_sheet("E001_VC"),
                "E001_VD_t.json": h.make_mini_cue_sheet("E001_VD"),
                "E002_t.json": h.make_mini_cue_sheet("E002", chapter_number=2),
                "E003A_t.json": h.make_mini_cue_sheet("E003A", chapter_number=3),
            },
        )
        out_dir = tmp / "out"
        cache_dir = tmp / "cache"
        proc = h.run_python_script(
            h.COLAB_RUN_STUDIO,
            [
                "--studio-dir", str(sdir),
                "--episodes", "E001_VARIANTS,E002,E003A",
                "--output-dir", str(out_dir),
                "--cache-dir", str(cache_dir),
                "--offline-dry-run",
            ],
            timeout=240,
        )
        assert proc.returncode == 0, (
            f"run_global_edge_96gb_studio.py --episodes E001_VARIANTS,E002,E003A failed "
            f"(rc={proc.returncode}): {proc.stderr[-800:]}\n{proc.stdout[-400:]}"
        )
        done_files = sorted(out_dir.glob("*_v001.done"))
        assert len(done_files) == 6, (
            f"Expected exact 6 *_v001.done artifacts for E001_VARIANTS,E002,E003A, "
            f"got {len(done_files)}: {[p.name for p in done_files]}"
        )
        expected_ids = ("E001_VA", "E001_VB", "E001_VC", "E001_VD", "E002", "E003A")
        manifest_eids: set[str] = set()
        for eid in expected_ids:
            for ext in (".wav", ".mp3", ".srt", ".json", ".done"):
                hits = list(out_dir.glob(f"{eid}*_v001{ext}"))
                assert len(hits) == 1, f"Expected 1 {eid}*_v001{ext} artifact, found {[p.name for p in hits]}"
            man = h.load_json_file(sorted(out_dir.glob(f"{eid}*_v001.json"))[0])
            assert man.get("episode_id") == eid, f"Manifest episode_id={man.get('episode_id')!r}, expected {eid!r}"
            manifest_eids.add(man["episode_id"])
        assert manifest_eids == set(expected_ids)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T1_F19_06", "F19", "Devbox ffmpeg/ffprobe present, check-env --offline exits 0, and export_cue_sheet_markdown renders ACE-Step header")
def t1_f19_06() -> None:
    from aigc_audio_pipeline.adapter import export_cue_sheet_markdown
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    h.require_ffmpeg()
    proc = h.run_pipeline_cli(["check-env", "--offline"], timeout=30)
    assert proc.returncode == 0, f"check-env --offline failed (rc={proc.returncode}): {proc.stdout}\n{proc.stderr}"
    payload = h.parse_last_json_object(proc.stdout)
    assert payload.get("ffmpeg_available") is True

    sheet = EpisodeCueSheet(
        episode_id="E001_HDR",
        chapter_number=1,
        title="Header Check",
        mode="bilingual_business_drama",
        acts=[ActMusicSpec(act_id="act_1", title="Act 1", bgm_prompt="Minimalist strings, no vocals")],
        cues=[h.make_timeline_cue(cue_id="C1", act_id="act_1", kind="dialogue", role_id="lin_chen", language_code="en", text="Check.")],
    )
    md = export_cue_sheet_markdown(sheet)
    assert "ACE-Step" in md and "music_v2_5" not in md, "bilingual_business_drama MD export must show ACE-Step header"


TESTS = COLLECTOR.tests
assert len(TESTS) == 100, f"Expected exact 100 Tier 1 tests, got {len(TESTS)}"
