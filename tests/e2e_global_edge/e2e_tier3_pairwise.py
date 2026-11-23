"""Tier 3 — Cross-Feature Pairwise Combinations: 26 Opaque-Box Integration Tests.

Tests shared dataflows and cross-artifact / cross-CLI invariants across all 19
features (`T3_P01`..`T3_P26`).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import e2e_helpers as h

COLLECTOR = h.TierCollector(tier=3)
test = COLLECTOR.test


@test("T3_P01", "F01xF12", "Corpus seed transcripts -> E001 standalone scripts: 8/8 phrases grounded in seeds & 0 YouTube/视频号 meta-talk")
def t3_p01() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    seed_blob = h.normalize_for_phrase_match(
        " ".join(by_id[cid]["en_clean"] for cid in sorted(h.E001_SEED_CLIP_IDS))
    )
    # On cleaned corpus 012_AI, literal '10 times the throughput' must appear
    assert "10 times the throughput" in h.normalize_for_phrase_match(by_id["012_AI"]["en_clean"])
    for pid, label, and_clauses in h.E001_MANDATORY_PHRASES:
        for alts in and_clauses:
            assert any(a in seed_blob for a in alts), (
                f"Seed corpus clips missing {pid} ({label}): none of {list(alts)}"
            )
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    for vid, cs in variants.items():
        h.oracle_e001_8_mandatory_phrases(cs, drama_only=True)
        h.oracle_standalone_ip_and_banned_cliches(cs)


@test("T3_P02", "F02xF12", "executive_lexicon.json <-> corpus_100_structured.json: provenance honesty, zero-hit world_bridge separation, clean verbatim parity & 4-pillar coverage")
def t3_p02() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    lex = h.load_json_file(h.PATH_LEXICON_JSON, "executive_lexicon.json")
    res = h.oracle_lexicon_provenance_70_30(lex, corp)
    assert res["total"] >= 100 and res["corpus_ratio"] >= 0.70 and res["world_bridge_count"] >= 1

    entries = (
        lex
        if isinstance(lex, list)
        else lex.get("phrases", lex.get("entries", lex.get("lexicon", [])))
    )
    by_id = {c["clip_id"]: c for c in corp["clips"]}
    anomalies_by_cid: dict[str, list[tuple[str, re.Pattern[str]]]] = {}
    for cid, label, pat, flags, _hint, _batch in h.RAW_CORPUS_ANOMALIES:
        anomalies_by_cid.setdefault(cid, []).append((label, re.compile(pat, flags)))

    wb_zero_hit_covered: set[str] = set()
    cited_clips_by_topic: dict[str, set[str]] = {"AI": set(), "BUSINESS": set(), "FINANCE": set(), "US_CHINA": set()}

    for entry in entries:
        pid = entry.get("phrase_id", "?")
        phrase_norm = h.normalize_for_phrase_match(str(entry.get("phrase_en", "")))
        verb_raw = str(entry.get("verbatim_context_en", ""))
        verb_norm = h.normalize_for_phrase_match(verb_raw)
        # Zero bracket tags (e.g. [snorts]) in any lexicon verbatim context
        assert not re.search(r"\[[^\]]+\]", verb_raw), f"{pid}: bracket tag leaked into verbatim_context_en: {verb_raw!r}"

        stype = entry.get("source_type")
        cids = entry.get("clip_ids", [])
        if stype == "corpus":
            # Provenance honesty: zero-hit world_bridge terms must never be mislabeled source_type='corpus'
            for zt in h.ZERO_HIT_WORLD_BRIDGE_TERMS:
                assert not h._word_bounded_in(zt, phrase_norm), (
                    f"{pid}: zero-hit world_bridge term {zt!r} mislabeled source_type='corpus' ({entry.get('phrase_en')!r})"
                )
            # Zero raw ASR anomalies in verbatim_context_en + exact verbatim_context_en <-> en_clean parity
            verb_core = re.sub(r"^['\"“”‘’….\s]+|['\"“”‘’….\s]+$", "", verb_norm)
            matched_clean = False
            for cid in cids:
                for albl, rx in anomalies_by_cid.get(cid, ()):
                    assert not rx.search(verb_raw), (
                        f"{pid} ({cid}): raw ASR anomaly {albl!r} leaked into verbatim_context_en"
                    )
                en_clean_norm = h.normalize_for_phrase_match(str(by_id[cid].get("en_clean", "")))
                if verb_core and verb_core in en_clean_norm:
                    matched_clean = True
                cited_clips_by_topic[h.CLIP_TOPIC_LOOKUP[cid]].add(cid)
            assert matched_clean, (
                f"{pid}: verbatim_context_en does not match en_clean of cited clip_ids={cids}: {verb_raw[:120]!r}"
            )
        elif stype == "world_bridge":
            assert cids == [], f"{pid}: world_bridge entry must have empty clip_ids=[], got {cids!r}"
            for zt in h.ZERO_HIT_WORLD_BRIDGE_TERMS:
                if h._word_bounded_in(zt, phrase_norm) or h._word_bounded_in(zt, verb_norm):
                    wb_zero_hit_covered.add(zt)

    assert len(wb_zero_hit_covered) >= 3, (
        f"Expected >=3 zero-hit world_bridge retail/compliance terms in world_bridge entries, found {sorted(wb_zero_hit_covered)}"
    )
    for topic, cited_set in cited_clips_by_topic.items():
        assert len(cited_set) >= 5, (
            f"Corpus lexicon draws from only {len(cited_set)} unique {topic} clips (<5 required)"
        )


@test("T3_P03", "F03xF19", "Bilingual cue sheets -> Corporate spaces + Dual-line SRT (zero TTS leak) + VB inner_monologue")
def t3_p03() -> None:
    from aigc_audio_pipeline.drama3_adapter import translate_cue_to_drama3_input
    from aigc_audio_pipeline.mixer import master_episode_three_bus
    from aigc_audio_pipeline.models import EpisodeCueSheet

    h.require_ffmpeg()
    reg = h.load_registry_safe()
    vb = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VB"])

    inner_cues = [c for c in vb.cues if c.kind == "dialogue" and c.acoustic_space == "inner_monologue"]
    assert len(inner_cues) >= 4, f"E001_VB needs >=4 inner_monologue cues, got {len(inner_cues)}"
    en_trans_cues = [
        c for c in vb.cues
        if c.kind == "dialogue"
        and c.language_code == "en"
        and str(getattr(c, "subtitle_translation", "")).strip()
        and c.acoustic_space in ("boardroom", "dry", "phone_call")
    ]
    assert len(en_trans_cues) >= 2, "E001_VB missing pure-EN corporate cues with subtitle_translation"

    sample_cues = [en_trans_cues[0], inner_cues[0], en_trans_cues[1]]
    used_act_ids = {c.act_id for c in sample_cues}
    sample_acts = [a for a in vb.acts if a.act_id in used_act_ids]
    mini = EpisodeCueSheet(
        episode_id="E001_VB_P03",
        chapter_number=1,
        title="P03 Mini Master",
        mode="bilingual_business_drama",
        acts=sample_acts,
        cues=sample_cues,
    )
    tts_prompts = [
        translate_cue_to_drama3_input(c, reg.resolve_role(c.role_id), domain="business_english_drama")
        for c in sample_cues
    ]
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p03_"))
    try:
        audio_map = {
            c.cue_id: h.write_sine_wav(tmp / f"{c.cue_id}.wav", 1.8, freq_hz=300.0 + i * 60.0)
            for i, c in enumerate(sample_cues)
        }
        bgm_map = {a.act_id: h.write_sine_wav(tmp / f"{a.act_id}.wav", 6.0, freq_hz=110.0, amplitude=0.12) for a in sample_acts}
        res = master_episode_three_bus(mini, audio_map, bgm_map, tmp / "out", registry=reg, clean_work_dir=True)
        srt_text = Path(res["subtitles_srt"]).read_text(encoding="utf-8")
        expected_glosses = [
            en_trans_cues[0].subtitle_translation.strip(),
            en_trans_cues[1].subtitle_translation.strip(),
        ]
        h.oracle_srt_non_overlap_and_dual_line(
            srt_text,
            expected_translations=expected_glosses,
            tts_prompts=tts_prompts,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P04", "F04xF17", "Act 5 Debrief -> playback_rate=0.8 atempo 1.25x pitch-preserved stretch & >=1.8s shadowing gaps")
def t3_p04() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    h.require_signature_param(condition_dialogue_clip, "playback_rate")
    va = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VA"])
    _, _, debrief = h.split_drama_and_debrief_cues(va)
    slow_cues = [c for c in debrief if c.kind == "dialogue" and abs(float(getattr(c, "playback_rate", 1.0)) - 0.8) < 1e-3]
    shadow_cues = [c for c in debrief if c.kind == "dialogue" and float(c.gap_after_s) >= 1.8]
    assert len(slow_cues) >= 3 and len(shadow_cues) >= 3

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p04_"))
    try:
        base_wav = h.write_sine_wav(tmp / "base.wav", 2.0, freq_hz=440.0)
        norm_out = tmp / "norm.wav"
        slow_out = tmp / "slow.wav"
        condition_dialogue_clip(base_wav, norm_out, acoustic_space=slow_cues[0].acoustic_space, playback_rate=1.0)
        condition_dialogue_clip(base_wav, slow_out, acoustic_space=slow_cues[0].acoustic_space, playback_rate=slow_cues[0].playback_rate)
        h.oracle_audio_signal_and_atempo_ratio(
            wav_48k_path=slow_out,
            slow_wav_path=slow_out,
            base_wav_path=norm_out,
            expected_pitch_hz=440.0,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P05", "F05xF14", "NovaEdge hardware world <-> 24-ep bijective map: 100/100 unique clips & all 5 hardware verticals")
def t3_p05() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    bp = h.load_text_file(h.PATH_SEASON1_BLUEPRINT, "SEASON1_24EP_BLUEPRINT.md")
    h.oracle_season1_24ep_bijection(smap)
    blob = (bp + "\n" + json.dumps(smap, ensure_ascii=False)).lower()
    assert "novaedge" in blob or "灵犀" in blob
    for vertical_kws in (
        ("渠道", "零售", "margin", "selfridges", "best buy"),
        ("估值", "series c", "融资", "vc"),
        ("算力", "token", "推理", "compute"),
        ("隐私", "合规", "gdpr", "ai act", "诉讼"),
        ("关税", "供应链", "tariff", "东南亚"),
    ):
        assert any(k in blob for k in vertical_kws), f"Missing vertical {vertical_kws} across Season 1 blueprint/map"


@test("T3_P06", "F06xF15", "Accent matrix (85%/15%) <-> Registry, Anchor Sources & Season 1 Map 1:1 alignment")
def t3_p06() -> None:
    reg = h.load_registry_safe()
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    variants = h.load_all_e001_variants()
    anc_cfg = h.load_json_file(h.PATH_ANCHOR_SOURCES, "anchor_sources.json")
    h.assert_anchor_sources_clean(anc_cfg, list(reg.roles.keys()), label="anchor_sources.json")
    h.oracle_accent_matrix_budget(reg, season_map=smap, e001_cue_sheets=variants)


@test("T3_P07", "F07xF18", "All 13 HBO corporate tags -> drama3_adapter translation (0 Xianxia) + qa.py leak & spoken-word rules")
def t3_p07() -> None:
    from aigc_audio_pipeline.drama3_adapter import DRAMA3_TAG_MAP, translate_cue_to_drama3_input
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    reg = h.make_minimal_registry()
    for tag in h.REQUIRED_13_HBO_TAGS:
        assert tag in DRAMA3_TAG_MAP, f"Missing corporate tag {tag!r} in DRAMA3_TAG_MAP"
        cue = h.make_timeline_cue(
            cue_id=f"TAG_{tag.replace(' ', '_')}",
            act_id="act_1",
            kind="dialogue",
            role_id="victoria_vance",
            language_code="en",
            text=f"[{tag}] That valuation multiple requires proof.",
        )
        d3 = translate_cue_to_drama3_input(cue, reg.roles["victoria_vance"], attempt=1, domain="business_english_drama")
        h.oracle_domain_no_xianxia_leak(drama3_prompt=d3)
        assert "valuation multiple" in d3.lower()

    # Leak caught when not spoken
    leaked = evaluate_dialogue_qa(
        tagged_prompt="[skeptical] Your cash flow forecast is optimistic.",
        asr_text="skeptical Your cash flow forecast is optimistic.",
        duration_s=2.0,
        peak_dbfs=-6.0,
        language_code="en",
    )
    assert leaked.passed is False and "skeptical" in leaked.leaked_tags

    # Exempt when legitimately spoken
    spoken_ok = evaluate_dialogue_qa(
        tagged_prompt="[skeptical] Our syndicate remains skeptical about your margin forecast.",
        asr_text="Our syndicate remains skeptical about your margin forecast.",
        duration_s=2.5,
        peak_dbfs=-6.0,
        language_code="en",
    )
    assert spoken_ok.passed is True and spoken_ok.leaked_tags == []


@test("T3_P08", "F07xF19", "Negative-gap crosstalk (-0.18s) -> 3-Bus Mixer overlaps Bus A while clamping dual-line SRT cleanly")
def t3_p08() -> None:
    from aigc_audio_pipeline.mixer import master_episode_three_bus
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    h.require_ffmpeg()
    reg = h.make_minimal_registry()
    sheet = EpisodeCueSheet(
        episode_id="E001_P08",
        chapter_number=1,
        title="P08 Crosstalk",
        mode="bilingual_business_drama",
        acts=[ActMusicSpec(act_id="act_1", title="Act 1", bgm_prompt="Minimal strings, instrumental, no vocals")],
        cues=[
            h.make_timeline_cue(cue_id="C1", act_id="act_1", kind="dialogue", role_id="victoria_vance", speaker_name="Victoria", language_code="en", text="[icy polite] Pick your favorite number.", subtitle_translation="随便挑你最喜欢的数字。", gap_after_s=-0.18),
            h.make_timeline_cue(cue_id="C2", act_id="act_1", kind="dialogue", role_id="lin_chen", speaker_name="Lin Chen", language_code="en", text="[interrupting] Ten times the throughput.", subtitle_translation="十倍吞吐量。", gap_after_s=0.30),
        ],
    )
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p08_"))
    try:
        w1 = h.write_sine_wav(tmp / "c1.wav", 1.8, freq_hz=330.0)
        w2 = h.write_sine_wav(tmp / "c2.wav", 1.8, freq_hz=440.0)
        bgm = h.write_sine_wav(tmp / "bgm.wav", 5.0, freq_hz=110.0, amplitude=0.10)
        res = master_episode_three_bus(sheet, {"C1": w1, "C2": w2}, {"act_1": bgm}, tmp / "out", registry=reg, clean_work_dir=True)
        manifest = h.load_json_file(Path(res["manifest_json"]))
        tl = manifest["timeline"]
        assert tl[1]["start_s"] < tl[0]["end_s"], "Bus A did not overlap negative-gap crosstalk"
        srt_text = Path(res["subtitles_srt"]).read_text(encoding="utf-8")
        h.oracle_srt_non_overlap_and_dual_line(srt_text, expected_translations=["随便挑你最喜欢的数字。", "十倍吞吐量。"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P09", "F08xF16", "All 4 E001 variants couple structural divergence (crosstalk/inner_monologue/duck overlap) with commuter runtime windows")
def t3_p09() -> None:
    variants = h.load_all_e001_variants()
    assert len(variants) == 4
    h.oracle_variant_differentiation_and_crosstalk(variants)
    rt_map = {vid: h.oracle_runtime_and_debrief_windows(cs) for vid, cs in variants.items()}

    # 1. E001_VD simultaneous duck_under_next overlap must genuinely compress drama pacing (>0.5s saved)
    _, vd_drama, _ = h.split_drama_and_debrief_cues(variants["E001_VD"])
    vd_unducked_s = 0.0
    for c in vd_drama:
        if c.kind == "sfx":
            if getattr(c, "placement", "sequential") != "overlay_next":
                vd_unducked_s += max(0.0, float(c.duration_seconds) + float(c.gap_after_s))
        else:
            vd_unducked_s += max(0.0, h.estimate_cue_spoken_duration_s(c) + float(c.gap_after_s))
    assert vd_unducked_s > rt_map["E001_VD"]["drama_s"] + 0.5, (
        f"E001_VD duck_under_next overlap failed to compress drama runtime "
        f"(unducked={vd_unducked_s:.2f}s vs actual={rt_map['E001_VD']['drama_s']:.2f}s)"
    )

    # 2. E001_VA & E001_VC negative-gap crosstalk tightening (>0.25s tighter than non-overlapping playback)
    for vid in ("E001_VA", "E001_VC"):
        _, d_cues, _ = h.split_drama_and_debrief_cues(variants[vid])
        non_overlap_s = 0.0
        for idx, c in enumerate(d_cues):
            if c.kind == "sfx":
                if getattr(c, "placement", "sequential") != "overlay_next":
                    non_overlap_s += max(0.0, float(c.duration_seconds) + max(0.0, float(c.gap_after_s)))
            else:
                dur = h.estimate_cue_spoken_duration_s(c)
                has_next_dlg = idx + 1 < len(d_cues) and d_cues[idx + 1].kind == "dialogue"
                if getattr(c, "duck_under_next", False) and has_next_dlg:
                    non_overlap_s += min(dur, float(getattr(c, "duck_lead_in_s", 3.5)))
                else:
                    non_overlap_s += dur + max(0.0, float(c.gap_after_s))
        assert non_overlap_s > rt_map[vid]["drama_s"] + 0.25, (
            f"{vid}: negative-gap crosstalk did not tighten drama pacing by >0.25s "
            f"(non_overlap={non_overlap_s:.2f}s vs actual={rt_map[vid]['drama_s']:.2f}s)"
        )

    # 3. E001_VB inner_monologue time budget >= 10.0s & zhou_mo present in Act 5 debrief
    _, vb_drama, vb_debrief = h.split_drama_and_debrief_cues(variants["E001_VB"])
    vb_inner_s = sum(
        h.estimate_cue_spoken_duration_s(c)
        for c in vb_drama
        if c.kind == "dialogue" and c.acoustic_space == "inner_monologue"
    )
    assert vb_inner_s >= 10.0, f"E001_VB inner_monologue drama duration={vb_inner_s:.1f}s < 10.0s"
    vb_debrief_roles = {c.role_id for c in vb_debrief if c.kind == "dialogue"}
    assert {"lin_chen", "zhou_mo"} <= vb_debrief_roles, (
        f"E001_VB Act 5 debrief must include lin_chen & zhou_mo, got {sorted(vb_debrief_roles)}"
    )

    # 4. Cross-variant comparability envelope (spread <= 240s)
    totals = [r["total_s"] for r in rt_map.values()]
    assert (max(totals) - min(totals)) <= 240.0, f"Cross-variant total runtime spread > 240s: {rt_map}"


@test("T3_P10", "F09xF16", "Viral clip cutlists & Companion Manual <-> All 4 E001 JSON cue sheets cross-verified")
def t3_p10() -> None:
    variants = h.load_all_e001_variants()
    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    manual = h.load_text_file(h.PATH_COMPANION_MD, "E001_BILINGUAL_COMPANION_MANUAL.md")
    cutlists = h.extract_viral_cutlists_from_markdown(kit, variants)
    assert len(cutlists) >= 1, "Expected >= 1 executable 38-55s viral clip cutlist in LAUNCH_KIT_AND_E001_45S_CLIPS.md"
    h.oracle_viral_45s_cutlist_and_rubric(cutlists=cutlists, cue_sheets_by_variant=variants)
    norm_manual = h.normalize_for_phrase_match(manual)
    for pid, label, and_clauses in h.E001_MANDATORY_PHRASES:
        for alts in and_clauses:
            assert any(a in norm_manual for a in alts), f"Companion manual missing {pid} ({label})"


@test("T3_P11", "F10xF15", "prepare_global_edge_voice_anchors.py --offline-stub -> run_global_edge_96gb_studio.py --offline-dry-run")
def t3_p11() -> None:
    h.require_ffmpeg()
    h.require_file(h.PATH_REGISTRY, "voice_casting_registry.json")
    h.require_file(h.PATH_AUDITION_JSON, "AUDITION_GLOBAL_EDGE JSON")
    out_flag = h.probe_script_flag(h.COLAB_PREPARE_ANCHORS, ("--output-dir", "--out-dir"))
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p11_"))
    try:
        studio = tmp / "studio"
        (studio / "auditions").mkdir(parents=True)
        (studio / "cue_sheets").mkdir(parents=True)
        shutil.copy2(h.PATH_REGISTRY, studio / "voice_casting_registry.json")
        shutil.copy2(h.PATH_AUDITION_JSON, studio / "auditions" / h.PATH_AUDITION_JSON.name)

        p_anc = h.run_python_script(
            h.COLAB_PREPARE_ANCHORS,
            ["--registry", str(studio / "voice_casting_registry.json"), out_flag, str(studio), "--offline-stub"],
            timeout=60,
        )
        assert p_anc.returncode == 0, f"Anchor stub build failed: {p_anc.stderr}"
        manifest = h.load_json_file(studio / "voice_cast_drama3.json")
        h.oracle_notebook_and_bundle_integrity(voice_cast_manifest=manifest)

        p_run = h.run_python_script(
            h.COLAB_RUN_STUDIO,
            [
                "--studio-dir", str(studio),
                "--episodes", "AUDITION",
                "--output-dir", str(tmp / "out"),
                "--cache-dir", str(tmp / "cache"),
                "--offline-dry-run",
            ],
            timeout=180,
        )
        assert p_run.returncode == 0, f"Studio dry-run on AUDITION failed: {p_run.stderr}\n{p_run.stdout}"
        out_dir = tmp / "out"
        assert list(out_dir.glob("*_v001.wav")), "Studio dry-run produced no _v001.wav"
        assert list(out_dir.glob("*_v001.done")), "Studio dry-run produced no _v001.done"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P12", "F10xF19", "Colab Studio CLI <-> Widened variant resolver resolves E001_VARIANTS (exact 4) and ALL (exact 5 incl. AUDITION)")
def t3_p12() -> None:
    h.require_ffmpeg()
    h.require_file(h.COLAB_RUN_STUDIO, "run_global_edge_96gb_studio.py")
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p12_"))
    try:
        sdir = h.build_mini_studio_dir(
            tmp / "studio",
            audition_sheets={
                "AUDITION_GLOBAL_EDGE_t.json": h.make_mini_cue_sheet(
                    "AUDITION_GLOBAL_EDGE", mode="audition_pack", chapter_number=0
                ),
            },
            cue_sheets={
                "E001_VA_t.json": h.make_mini_cue_sheet("E001_VA"),
                "E001_VB_t.json": h.make_mini_cue_sheet("E001_VB"),
                "E001_VC_t.json": h.make_mini_cue_sheet("E001_VC"),
                "E001_VD_t.json": h.make_mini_cue_sheet("E001_VD"),
            },
        )
        cache_dir = tmp / "cache"

        # Execution 1: --episodes E001_VARIANTS -> exact 4 (E001_VA..VD, no audition)
        out_var = tmp / "out_var"
        p_var = h.run_python_script(
            h.COLAB_RUN_STUDIO,
            [
                "--studio-dir", str(sdir),
                "--episodes", "E001_VARIANTS",
                "--output-dir", str(out_var),
                "--cache-dir", str(cache_dir),
                "--offline-dry-run",
            ],
            timeout=240,
        )
        assert p_var.returncode == 0, (
            f"Studio --episodes E001_VARIANTS failed (rc={p_var.returncode}): {p_var.stderr[-800:]}\n{p_var.stdout[-400:]}"
        )
        var_dones = sorted(out_var.glob("*_v001.done"))
        assert len(var_dones) == 4, f"Expected exact 4 outputs for E001_VARIANTS, got {[p.name for p in var_dones]}"
        var_eids = {h.load_json_file(p.with_suffix(".json")).get("episode_id") for p in var_dones}
        assert var_eids == {"E001_VA", "E001_VB", "E001_VC", "E001_VD"}, f"Unexpected E001_VARIANTS eids: {var_eids}"

        # Execution 2: --episodes ALL -> exact 5 (AUDITION_GLOBAL_EDGE + E001_VA..VD, all 5 extensions each)
        out_all = tmp / "out_all"
        p_all = h.run_python_script(
            h.COLAB_RUN_STUDIO,
            [
                "--studio-dir", str(sdir),
                "--episodes", "ALL",
                "--output-dir", str(out_all),
                "--cache-dir", str(cache_dir),
                "--offline-dry-run",
            ],
            timeout=240,
        )
        assert p_all.returncode == 0, (
            f"Studio --episodes ALL failed (rc={p_all.returncode}): {p_all.stderr[-800:]}\n{p_all.stdout[-400:]}"
        )
        all_dones = sorted(out_all.glob("*_v001.done"))
        assert len(all_dones) == 5, f"Expected exact 5 outputs for ALL, got {[p.name for p in all_dones]}"
        expected_all = {"AUDITION_GLOBAL_EDGE", "E001_VA", "E001_VB", "E001_VC", "E001_VD"}
        all_eids = {h.load_json_file(p.with_suffix(".json")).get("episode_id") for p in all_dones}
        assert all_eids == expected_all, f"Unexpected ALL eids: {all_eids}"
        for eid in expected_all:
            for ext in (".wav", ".mp3", ".srt", ".json", ".done"):
                assert list(out_all.glob(f"{eid}*_v001{ext}")), f"ALL missing {eid}*_v001{ext}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P13", "F11xF12", "RESEARCH_REPORT.md <-> corpus_100_structured.json & CORPUS_INTELLIGENCE_REPORT.md metric parity")
def t3_p13() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    corp_rep = h.load_text_file(h.PATH_CORPUS_REPORT, "CORPUS_INTELLIGENCE_REPORT.md")
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    assert corp["total_clips"] == 100
    assert int(corp["summary_metrics"]["total_segments"]) == 1408
    med_str = f"{float(corp['summary_metrics']['median_wpm']):.1f}"
    for label, txt in (("RESEARCH_REPORT.md", rep), ("CORPUS_INTELLIGENCE_REPORT.md", corp_rep)):
        assert "100" in txt, f"{label} missing 100 clips"
        assert "1,408" in txt or "1408" in txt, f"{label} missing 1,408 segments"
        assert med_str in txt or "170.2" in txt, f"{label} missing median WPM {med_str}"


@test("T3_P14", "F13xF15", "SHOW_BIBLE.md / ACCENT_AND_PROSODY_MANUAL.md <-> voice_casting_registry.json 1:1 role & motif parity")
def t3_p14() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    manual = h.load_text_file(h.PATH_ACCENT_MANUAL, "ACCENT_AND_PROSODY_MANUAL.md")
    reg = h.load_registry_safe()
    assert len(reg.roles) >= 8, f"Expected >=8 canonical roles in registry, got {len(reg.roles)}"
    assert set(h.CANONICAL_ALL_8_ROLES) <= set(reg.roles.keys()), (
        f"Registry missing canonical roles: {sorted(set(h.CANONICAL_ALL_8_ROLES) - set(reg.roles.keys()))}"
    )
    combined = bible + "\n" + manual
    for rid, prof in reg.roles.items():
        assert rid in combined or prof.display_name in combined, f"Role {rid!r} missing from Bible/Manual"
    assert len(reg.sonic_motifs) >= 4
    motif_hits = sum(1 for mid, m in reg.sonic_motifs.items() if mid in combined or m.name in combined)
    assert motif_hits >= 2, f"Expected registered sonic_motifs documented in Show Bible, found only {motif_hits}"


@test("T3_P15", "F13xF16", "Show Bible archetype rules <-> E001_VA/VB/VC/VD structural signatures")
def t3_p15() -> None:
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    assert "inner_monologue" in bible and "boardroom" in bible and "phone_call" in bible
    variants = h.load_all_e001_variants()
    res = h.oracle_variant_differentiation_and_crosstalk(variants)
    assert res["metrics"]["E001_VB"]["inner_monologue"] >= 4
    assert res["metrics"]["E001_VB"]["inner_monologue"] > res["metrics"]["E001_VA"]["inner_monologue"]
    assert res["metrics"]["E001_VC"]["phone_call"] >= 1
    assert res["metrics"]["E001_VD"]["duck_under_next"] >= 2


@test("T3_P16", "F14xF09", "season1_24ep_map.json <-> SEASON1_24EP_BLUEPRINT.md: all 24 episodes carry viral_45s_hook, cliffhanger & 5..8 phrases")
def t3_p16() -> None:
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    bp = h.load_text_file(h.PATH_SEASON1_BLUEPRINT, "SEASON1_24EP_BLUEPRINT.md")
    h.oracle_season1_24ep_bijection(smap)
    for ep in smap["episodes"]:
        assert ep["episode_id"] in bp, f"Blueprint missing {ep['episode_id']}"
        vh = ep.get("viral_45s_hook")
        vh_ok = (isinstance(vh, str) and len(vh.strip()) >= 10) or (
            isinstance(vh, dict)
            and isinstance(vh.get("conflict_angle"), str)
            and bool(vh["conflict_angle"].strip())
            and isinstance(vh.get("hook_line_en"), str)
            and bool(vh["hook_line_en"].strip())
        )
        assert vh_ok, f"{ep['episode_id']}: invalid or blank viral_45s_hook: {vh!r}"
        assert isinstance(ep.get("cliffhanger_zh"), str) and bool(ep["cliffhanger_zh"].strip()), (
            f"{ep['episode_id']}: blank cliffhanger_zh"
        )
        assert 5 <= len(ep["target_phrases"]) <= 8


@test("T3_P17", "F16xF04", "E001_COMPARATIVE_EVAL_RUBRIC.md <-> Automated Debrief & Variant Scorecard consistency")
def t3_p17() -> None:
    rubric = h.load_text_file(h.PATH_RUBRIC_MD, "E001_COMPARATIVE_EVAL_RUBRIC.md")
    res = h.oracle_viral_45s_cutlist_and_rubric(rubric_md=rubric)
    assert res["rubric_sum"] == 100
    variants = h.load_all_e001_variants()
    for vid, cs in variants.items():
        assert vid in rubric, f"Rubric missing {vid}"
        h.oracle_runtime_and_debrief_windows(cs)
    assert any(k in rubric.lower() for k in ("0.8", "debrief", "拆局"))
    assert any(k in rubric.lower() for k in ("hybrid", "融合", "混合胜出"))


@test("T3_P18", "F16xF18", "All 5 real cue sheets -> drama3_adapter translate & chunk with domain='business_english_drama' (0 Xianxia, <=2048 tok)")
def t3_p18() -> None:
    from aigc_audio_pipeline.drama3_adapter import (
        estimate_drama3_max_new_tokens,
        split_cue_into_subcues_for_drama3,
        translate_cue_to_drama3_input,
    )

    reg = h.load_registry_safe()
    for eid, path in h.ALL_5_CUE_SHEETS.items():
        cs = h.load_cue_sheet_safe(path)
        dlg = [c for c in cs.cues if c.kind == "dialogue"]
        assert len(dlg) > 0, f"{eid}: 0 dialogue cues"
        for cue in dlg:
            prof = reg.resolve_role(cue.role_id)
            assert prof is not None, f"{eid} {cue.cue_id}: unresolved role {cue.role_id!r}"
            subcues = split_cue_into_subcues_for_drama3(cue, domain="business_english_drama")
            assert len(subcues) >= 1
            for sc in subcues:
                d3 = translate_cue_to_drama3_input(sc, prof, attempt=1, domain="business_english_drama")
                h.oracle_domain_no_xianxia_leak(drama3_prompt=d3)
                toks = estimate_drama3_max_new_tokens(d3, language_code=sc.language_code or prof.language_code)
                assert toks <= 2048, f"{eid} {sc.cue_id}: max_new_tokens={toks} > 2048"
                gloss = str(getattr(cue, "subtitle_translation", "") or "").strip()
                if gloss and h.count_cjk_chars(gloss) >= 3 and cue.language_code == "en":
                    assert gloss not in d3, f"{eid} {cue.cue_id}: subtitle_translation leaked into Drama 3 TTS"


@test("T3_P19", "F17xF19", "playback_rate + subtitle_translation + mode='bilingual_business_drama' round-trip through JSON & export_cue_sheet_markdown")
def t3_p19() -> None:
    from aigc_audio_pipeline.adapter import export_cue_sheet_markdown
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    reg = h.make_minimal_registry()
    sheet = EpisodeCueSheet(
        episode_id="E001_P19",
        chapter_number=1,
        title="P19 Roundtrip",
        mode="bilingual_business_drama",
        acts=[ActMusicSpec(act_id="act_5", title="Act 5 Debrief", bgm_prompt="Minimal jazz noir, instrumental, no vocals")],
        cues=[
            h.make_timeline_cue(
                cue_id="C1", act_id="act_5", kind="dialogue", role_id="lin_chen",
                language_code="en", text="[coach] Not a cash loss.", playback_rate=0.8,
                subtitle_translation="这不是现金亏损。", acoustic_space="studio_warm", gap_after_s=2.0,
            ),
        ],
    )
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p19_"))
    try:
        p = tmp / "p19.json"
        sheet.save(p)
        reloaded = EpisodeCueSheet.load(p)
        assert reloaded.mode == "bilingual_business_drama"
        assert abs(reloaded.cues[0].playback_rate - 0.8) < 1e-9
        assert reloaded.cues[0].subtitle_translation == "这不是现金亏损。"
        md = export_cue_sheet_markdown(reloaded, reg)
        assert "0.80x" in md and "这不是现金亏损。" in md and "ACE-Step" in md and "music_v2_5" not in md
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P20", "F18xF03", "Dual-script zh-en QA <-> Real bilingual cues extracted from E001_VB / E001_VD")
def t3_p20() -> None:
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    vb = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VB"])
    vd = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VD"])
    bilingual_cues = [
        c for c in (vb.cues + vd.cues)
        if c.kind == "dialogue"
        and c.language_code == "zh-en"
        and h.count_cjk_chars(h.strip_inline_tags(c.text)[1]) >= 4
        and h.count_en_words(h.strip_inline_tags(c.text)[1]) >= 3
    ]
    assert len(bilingual_cues) >= 1, "No mixed zh-en cues with >=4 CJK and >=3 EN words found in E001_VB/E001_VD"
    target = bilingual_cues[0]
    _, spoken = h.strip_inline_tags(target.text)
    ok = evaluate_dialogue_qa(tagged_prompt=target.text, asr_text=spoken, duration_s=3.5, peak_dbfs=-6.0, language_code="zh-en")
    assert ok.passed is True, f"Exact transcript failed QA on real cue {target.cue_id}: {ok.reasons}"

    # Drop all English words from ASR -> must FAIL!
    en_dropped = re.sub(r"[A-Za-z][A-Za-z0-9'\-]*", "", spoken).strip()
    bad = evaluate_dialogue_qa(tagged_prompt=target.text, asr_text=en_dropped, duration_s=3.5, peak_dbfs=-6.0, language_code="zh-en")
    assert bad.passed is False, f"Expected QA failure when dropping English words from {target.cue_id}"


@test("T3_P21", "F17xF10", "playback_rate=0.8 -> 3-Bus -16 LUFS mastering produces 48kHz stereo WAV/MP3 with ~1.25x manifest duration")
def t3_p21() -> None:
    from aigc_audio_pipeline.mixer import master_episode_three_bus
    from aigc_audio_pipeline.models import ActMusicSpec, EpisodeCueSheet

    h.require_ffmpeg()
    reg = h.make_minimal_registry()
    sheet = EpisodeCueSheet(
        episode_id="E001_P21",
        chapter_number=1,
        title="P21 3-Bus Slow Master",
        mode="bilingual_business_drama",
        acts=[
            ActMusicSpec(act_id="act_1", title="Act 1", bgm_prompt="Minimalist cello, instrumental, no vocals"),
            ActMusicSpec(act_id="act_5", title="Act 5 Debrief", bgm_prompt="Warm jazz pulse, instrumental, no vocals"),
        ],
        cues=[
            h.make_timeline_cue(cue_id="N1", act_id="act_1", kind="dialogue", role_id="lin_chen", language_code="en", text="[measured] Phantom number.", playback_rate=1.0, gap_after_s=0.35),
            h.make_timeline_cue(cue_id="S1", act_id="act_5", kind="dialogue", role_id="lin_chen", language_code="en", text="[coach] Phantom number.", playback_rate=0.8, gap_after_s=0.35),
        ],
    )
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p21_"))
    try:
        raw_stem = h.write_sine_wav(tmp / "stem.wav", 2.0, freq_hz=440.0, amplitude=0.40)
        bgm1 = h.write_sine_wav(tmp / "b1.wav", 5.0, freq_hz=110.0, amplitude=0.10)
        bgm5 = h.write_sine_wav(tmp / "b5.wav", 5.0, freq_hz=130.0, amplitude=0.10)
        res = master_episode_three_bus(
            sheet,
            {"N1": raw_stem, "S1": raw_stem},
            {"act_1": bgm1, "act_5": bgm5},
            tmp / "out",
            registry=reg,
            clean_work_dir=True,
        )
        wav_p = Path(res["master_wav"])
        mp3_p = Path(res["master_mp3"])
        probe = h.probe_audio_ffprobe(wav_p)
        assert probe["sample_rate"] == 48000 and probe["channels"] == 2
        assert mp3_p.is_file() and mp3_p.stat().st_size > 2000
        lufs, tp = h.measure_loudness_ffmpeg(wav_p)
        assert -20.5 <= lufs <= -13.0, f"Master LUFS out of expected range: {lufs:.2f}"
        assert tp <= -0.5, f"Master true peak exceeded ceiling: {tp:.2f} dBTP"
        tl = h.load_json_file(Path(res["manifest_json"]))["timeline"]
        ratio = tl[1]["duration_s"] / tl[0]["duration_s"]
        assert 1.18 <= ratio <= 1.32, f"Expected ~1.25x manifest duration ratio for 0.8x vs 1.0x, got {ratio:.3f}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P22", "F03xF16", "E001_VD duck_under_next pairs -> 3-Bus Mixer produces Bus A overlap & non-overlapping bilingual EN: SRT blocks")
def t3_p22() -> None:
    from aigc_audio_pipeline.mixer import master_episode_three_bus
    from aigc_audio_pipeline.models import EpisodeCueSheet

    h.require_ffmpeg()
    reg = h.load_registry_safe()
    vd = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VD"])
    duck_idx = next((i for i, c in enumerate(vd.cues) if c.kind == "dialogue" and getattr(c, "duck_under_next", False)), None)
    assert duck_idx is not None and duck_idx + 1 < len(vd.cues), "E001_VD missing valid duck_under_next pair"
    pair = [vd.cues[duck_idx], vd.cues[duck_idx + 1]]
    acts = [a for a in vd.acts if a.act_id in {pair[0].act_id, pair[1].act_id}]
    mini = EpisodeCueSheet(
        episode_id="E001_VD_P22",
        chapter_number=1,
        title="P22 Duck Master",
        mode="bilingual_business_drama",
        acts=acts,
        cues=pair,
    )
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p22_"))
    try:
        w0 = h.write_sine_wav(tmp / "p0.wav", 6.0, freq_hz=330.0)
        w1 = h.write_sine_wav(tmp / "p1.wav", 3.5, freq_hz=440.0)
        bgm_map = {a.act_id: h.write_sine_wav(tmp / f"{a.act_id}.wav", 10.0, freq_hz=110.0, amplitude=0.10) for a in acts}
        res = master_episode_three_bus(mini, {pair[0].cue_id: w0, pair[1].cue_id: w1}, bgm_map, tmp / "out", registry=reg, clean_work_dir=True)
        tl = h.load_json_file(Path(res["manifest_json"]))["timeline"]
        assert tl[1]["start_s"] < tl[0]["end_s"], "Expected duck_under_next simultaneous overlap on Bus A"
        srt_text = Path(res["subtitles_srt"]).read_text(encoding="utf-8")
        h.oracle_srt_non_overlap_and_dual_line(srt_text)
        assert "EN:" in srt_text, "Expected bilingual 'EN:' simultaneous-translation block in SRT"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P23", "F15xF16", "AUDITION_GLOBAL_EDGE validates locked, tests all 4 core voices, US+UK accents & EN+ZH switching on lin_chen")
def t3_p23() -> None:
    reg = h.load_registry_safe()
    aud = h.load_cue_sheet_safe(h.PATH_AUDITION_JSON)
    assert aud.episode_id == "AUDITION_GLOBAL_EDGE"
    assert aud.mode == "audition_pack"
    assert aud.validate(reg, require_locked_voices=True) == []
    dlg = [c for c in aud.cues if c.kind == "dialogue"]
    assert len(dlg) >= 6, f"AUDITION_GLOBAL_EDGE expected >=6 dialogue cues, got {len(dlg)}"
    roles = {c.role_id for c in dlg}
    for r in h.CORE_E001_ROLES:
        assert r in roles, f"AUDITION_GLOBAL_EDGE missing core E001 role {r!r}"
    lin_langs = {c.language_code for c in dlg if c.role_id == "lin_chen"}
    assert "en" in lin_langs and (lin_langs & {"zh", "zh-en"}), (
        f"AUDITION_GLOBAL_EDGE must audition both EN and ZH/ZH-EN on lin_chen, found {lin_langs}"
    )
    us_en = sum(1 for c in dlg if c.role_id == "victoria_vance" and c.language_code == "en")
    uk_en = sum(1 for c in dlg if c.role_id == "alistair_finch" and c.language_code == "en")
    assert us_en >= 1 and uk_en >= 1, (
        f"AUDITION_GLOBAL_EDGE must audition both US (victoria_vance={us_en}) and London RP (alistair_finch={uk_en}) EN lines"
    )


@test("T3_P24", "F10xF16", "export_drama3_bundle.py packages complete self-contained Colab 96GB ZIP with 0 __pycache__/.pyc")
def t3_p24() -> None:
    h.require_ffmpeg()
    dir_flag = h.probe_script_flag(h.SCRIPT_EXPORT_BUNDLE, ("--bundle-dir", "--output-dir", "--out-dir"))
    zip_flag = h.probe_script_flag(h.SCRIPT_EXPORT_BUNDLE, ("--zip-out", "--zip-path", "--zip-output"))
    bnd_help_flags = h.get_script_help_flags(h.SCRIPT_EXPORT_BUNDLE)
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t3_p24_"))
    try:
        bnd_dir = tmp / "bundle"
        zip_p = tmp / "global_edge_bundle.zip"
        exp_args = [dir_flag, str(bnd_dir), zip_flag, str(zip_p)]
        if "--offline-stub" in bnd_help_flags:
            exp_args.append("--offline-stub")
        elif "--anchors-dir" in bnd_help_flags:
            anc_dir = tmp / "anchors"
            anc_out_flag = h.probe_script_flag(h.COLAB_PREPARE_ANCHORS, ("--output-dir", "--out-dir"))
            p_anc = h.run_python_script(
                h.COLAB_PREPARE_ANCHORS,
                ["--registry", str(h.PATH_REGISTRY), anc_out_flag, str(anc_dir), "--offline-stub"],
                timeout=60,
            )
            assert p_anc.returncode == 0, f"Stub anchor build for bundle export failed: {p_anc.stderr}"
            exp_args.extend(["--anchors-dir", str(anc_dir)])
        proc = h.run_python_script(h.SCRIPT_EXPORT_BUNDLE, exp_args, timeout=180)
        assert proc.returncode == 0, f"export_drama3_bundle.py failed (rc={proc.returncode}): {proc.stderr}\n{proc.stdout}"
        h.oracle_notebook_and_bundle_integrity(zip_path=zip_p)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T3_P25", "F19xF01", "Legacy 21-test baseline suite tests/test_pipeline.py passes 21/21 with 0 failures and 0 errors")
def t3_p25() -> None:
    h.require_ffmpeg()
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "tests/test_pipeline.py"],
        cwd=str(h.REPO_ROOT),
        env=h.pipeline_env(),
        capture_output=True,
        text=True,
        timeout=180,
    )
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    assert proc.returncode == 0, f"Baseline tests/test_pipeline.py failed (rc={proc.returncode}):\n{combined[-1200:]}"
    m = re.search(r"Ran\s+(\d+)\s+tests?", combined)
    assert m and int(m.group(1)) >= 21, f"Expected >=21 baseline tests executed, got output:\n{combined[-400:]}"


@test("T3_P26", "F12xF14", "Every clip_id in season1_24ep_map.json resolves in corpus_100_structured.json with 0 ASR typos & exact 5 E001 seeds")
def t3_p26() -> None:
    corp = h.load_json_file(h.PATH_CORPUS_JSON, "corpus_100_structured.json")
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    h.oracle_corpus_100_etl_integrity(corp)
    h.oracle_season1_24ep_bijection(smap, expected_ids=frozenset(c["clip_id"] for c in corp["clips"]))
    assert set(smap["episodes"][0]["primary_clip_ids"]) == set(h.E001_SEED_CLIP_IDS)


TESTS = COLLECTOR.tests
assert len(TESTS) == 26, f"Expected exact 26 Tier 3 pairwise tests, got {len(TESTS)}"
