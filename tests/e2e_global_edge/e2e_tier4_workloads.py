"""Tier 4 — Real-World End-to-End Application Workflows: 10 Isolated Scenarios.

Every scenario (`T4_S01`..`T4_S10`) executes strictly inside isolated `mktemp -d`
workspaces (cleaned up via `try/finally`) through public CLIs and public Python
APIs with zero side effects on tracked repository files.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import e2e_helpers as h

COLLECTOR = h.TierCollector(tier=4)
test = COLLECTOR.test


def _strip_timestamps(obj):
    if isinstance(obj, dict):
        return {
            k: _strip_timestamps(v)
            for k, v in obj.items()
            if k not in ("generated_at", "exported_at", "updated_at", "timestamp")
        }
    if isinstance(obj, list):
        return [_strip_timestamps(x) for x in obj]
    return obj


@test("T4_S01", "F12+F02", "Cold-Start 100-Clip Corpus ETL, Determinism, 38-Anomaly Cleaning & 70/30 Lexicon Provenance")
def t4_s01() -> None:
    h.require_file(h.RAW_ARSENAL_JSON, "/tmp/arsenal_100_queue.json")
    out_flag = h.probe_script_flag(h.SCRIPT_EXTRACT_CORPUS, ("--out-dir", "--output-dir"))
    tmp1 = Path(tempfile.mkdtemp(prefix="ge_e2e_t4_s01_a_"))
    tmp2 = Path(tempfile.mkdtemp(prefix="ge_e2e_t4_s01_b_"))
    try:
        for d in (tmp1, tmp2):
            proc = h.run_python_script(
                h.SCRIPT_EXTRACT_CORPUS,
                ["--source", str(h.RAW_ARSENAL_JSON), out_flag, str(d)],
                timeout=120,
            )
            assert proc.returncode == 0, f"extract_100_clips_corpus.py failed (rc={proc.returncode}): {proc.stderr}"

        corp1 = h.load_json_file(tmp1 / "corpus_100_structured.json")
        corp2 = h.load_json_file(tmp2 / "corpus_100_structured.json")
        lex1 = h.load_json_file(tmp1 / "executive_lexicon.json")
        lex2 = h.load_json_file(tmp2 / "executive_lexicon.json")
        rep1 = h.load_text_file(tmp1 / "CORPUS_INTELLIGENCE_REPORT.md")

        assert _strip_timestamps(corp1) == _strip_timestamps(corp2), "Non-deterministic corpus_100_structured.json"
        assert _strip_timestamps(lex1) == _strip_timestamps(lex2), "Non-deterministic executive_lexicon.json"
        assert len(rep1) >= 1000

        raw_data = h.load_json_file(h.RAW_ARSENAL_JSON)
        h.oracle_corpus_100_etl_integrity(corp1, raw_data=raw_data)
        h.oracle_lexicon_provenance_70_30(lex1, corp1)

        # Verify raw typos preserved verbatim in en_raw while cleaned in en_clean
        by_id = {c["clip_id"]: c for c in corp1["clips"]}
        for cid, label, pat, flags, _hint, _batch in h.RAW_CORPUS_ANOMALIES:
            rx = re.compile(pat, flags)
            assert rx.search(by_id[cid]["en_raw"]), f"{cid}: {label!r} not preserved in en_raw"
            assert not rx.search(by_id[cid]["en_clean"]), f"{cid}: {label!r} leaked into en_clean"
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)
        shutil.rmtree(tmp2, ignore_errors=True)


@test("T4_S02", "F01+F05+F06+F11+F13+F14+F15", "Season 1 Worldbuilding & Cross-Document Lineage Audit across all 8 00_* Artifacts")
def t4_s02() -> None:
    rep = h.load_text_file(h.PATH_RESEARCH_REPORT, "RESEARCH_REPORT.md")
    bible = h.load_text_file(h.PATH_SHOW_BIBLE, "SHOW_BIBLE.md")
    manual = h.load_text_file(h.PATH_ACCENT_MANUAL, "ACCENT_AND_PROSODY_MANUAL.md")
    bp = h.load_text_file(h.PATH_SEASON1_BLUEPRINT, "SEASON1_24EP_BLUEPRINT.md")
    smap = h.load_json_file(h.PATH_SEASON1_MAP, "season1_24ep_map.json")
    reg = h.load_registry_safe()
    anc_src = h.load_json_file(h.PATH_ANCHOR_SOURCES, "anchor_sources.json")
    anc_spec = h.load_text_file(h.PATH_ANCHOR_SPEC, "VOICE_ANCHOR_ACQUISITION_SPEC.md")

    # 100/100 bijective clip mapping across 4x6 = 24 episodes
    raw_ids = frozenset(h.load_raw_arsenal_by_id().keys())
    h.oracle_season1_24ep_bijection(smap, expected_ids=raw_ids)

    # Season US+UK RP >= 85% + all 8 canonical roles locked with canonical accents & models
    h.oracle_accent_matrix_budget(reg, season_map=smap)
    for key, expected in h.CANONICAL_MODEL_IDS.items():
        assert getattr(reg, key) == expected, f"Registry.{key}={getattr(reg, key)!r}, expected {expected!r}"
    for rid, prof in reg.roles.items():
        assert prof.status == "locked" and prof.voice_id.strip()
        assert rid in bible or prof.display_name in bible, f"Role {rid!r} absent from SHOW_BIBLE.md"

    h.assert_anchor_sources_clean(anc_src, list(reg.roles.keys()), label="anchor_sources.json")

    # Cross-doc sanity: NovaEdge hardware + v2_real_human_studio + zero Xianxia/ElevenLabs/edge-tts drift
    assert "NovaEdge" in bible and "NovaEdge Glass" in bible and "NovaDock" in bible
    assert "170.2" in (rep + manual)
    assert "v2_real_human_studio" in anc_spec
    for cid in sorted(h.EXPECTED_100_CLIP_IDS):
        assert cid in bp, f"SEASON1_24EP_BLUEPRINT.md missing clip {cid}"
    h.assert_no_xianxia_plot_drift(bible, "SHOW_BIBLE.md")


@test("T4_S03", "F16+F04+F08+F19", "Multi-Variant E001 Isolated Build, validate --require-locked-voices CLI & export-markdown Parity")
def t4_s03() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t4_s03_"))
    try:
        # 1. Execute build_e001_variants.py safely in isolation (pre-existing copies unlinked; zero git dirtying)
        b_proc, built_dir = h.run_build_e001_isolated(tmp)
        assert b_proc.returncode == 0, f"build_e001_variants.py failed: {b_proc.stderr}\n{b_proc.stdout}"

        # 2. Verify all 5 freshly generated .json + .md files, validate via CLI, and confirm parity vs tracked files
        for eid, tracked_path in h.ALL_5_CUE_SHEETS.items():
            built_json = built_dir / tracked_path.name
            built_md = built_dir / tracked_path.with_suffix(".md").name
            assert built_json.is_file() and built_json.stat().st_size > 200, (
                f"build_e001_variants.py did not freshly write {built_json.name} in {built_dir}"
            )
            assert built_md.is_file() and built_md.stat().st_size > 200, (
                f"build_e001_variants.py did not freshly write {built_md.name} in {built_dir}"
            )
            proc, payload = h.run_validate_cli(h.PATH_REGISTRY, built_json, require_locked_voices=True)
            assert proc.returncode == 0, f"validate CLI failed on freshly built {eid}: {proc.stdout}\n{proc.stderr}"
            assert payload is not None and payload.get("valid") is True and payload.get("errors") == []
            assert _strip_timestamps(h.load_json_file(built_json)) == _strip_timestamps(h.load_json_file(tracked_path)), (
                f"Freshly built {eid} JSON diverged from tracked {tracked_path.name}"
            )

        # 3. Verify 8/8 phrases, runtime/debrief windows, crosstalk floors & structural differentiation
        variants = h.load_all_e001_variants()
        for vid, cs in variants.items():
            h.oracle_standalone_ip_and_banned_cliches(cs)
            h.oracle_e001_8_mandatory_phrases(cs, drama_only=True)
            h.oracle_runtime_and_debrief_windows(cs)
        h.oracle_variant_differentiation_and_crosstalk(variants)

        # 4. Run public export-markdown CLI on E001_VA and E001_VD into tmp
        for vid in ("E001_VA", "E001_VD"):
            out_md = tmp / f"{vid}_exported.md"
            p_md = h.run_pipeline_cli(
                [
                    "export-markdown",
                    "--cue-sheet", str(h.VARIANT_JSON_PATHS[vid]),
                    "--registry", str(h.PATH_REGISTRY),
                    "--output", str(out_md),
                ],
                timeout=60,
            )
            assert p_md.returncode == 0, f"export-markdown CLI failed on {vid}: {p_md.stderr}"
            md_txt = h.load_text_file(out_md)
            assert "0.80x" in md_txt, f"Exported MD for {vid} missing [0.80x] badge"
            assert "ACE-Step" in md_txt and "music_v2_5" not in md_txt, f"Exported MD for {vid} wrong BGM header"
            assert h.count_cjk_chars(md_txt) >= 100
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T4_S04", "F18+F16", "Public preview-drama3 CLI & Bilingual Sub-Cue Chunking across AUDITION + E001_VA/VB/VC/VD")
def t4_s04() -> None:
    from aigc_audio_pipeline.drama3_adapter import (
        estimate_drama3_max_new_tokens,
        split_cue_into_subcues_for_drama3,
        translate_cue_to_drama3_input,
    )

    reg = h.load_registry_safe()
    for eid, path in h.ALL_5_CUE_SHEETS.items():
        proc = h.run_pipeline_cli(
            [
                "preview-drama3",
                "--registry", str(h.PATH_REGISTRY),
                "--cue-sheet", str(path),
                "--limit", "200",
            ],
            timeout=90,
        )
        assert proc.returncode == 0, f"preview-drama3 CLI failed on {eid}: {proc.stderr}"
        payload = h.parse_last_json_object(proc.stdout)
        assert payload.get("domain") == "business_english_drama", (
            f"{eid}: preview-drama3 domain={payload.get('domain')!r}, expected 'business_english_drama'"
        )
        cues_out = payload.get("cues", [])
        min_cues = 6 if eid == "AUDITION_GLOBAL_EDGE" else 10
        assert len(cues_out) >= min_cues, f"{eid}: preview-drama3 returned too few cues ({len(cues_out)} < {min_cues})"
        for item in cues_out:
            h.oracle_domain_no_xianxia_leak(drama3_prompt=item.get("drama3_attempt1", ""))
            h.oracle_domain_no_xianxia_leak(drama3_prompt=item.get("drama3_retry2", ""))

        # Verify split_cue_into_subcues_for_drama3 & subtitle_translation non-leakage on all cues
        cs = h.load_cue_sheet_safe(path)
        for cue in cs.cues:
            if cue.kind != "dialogue":
                continue
            prof = reg.resolve_role(cue.role_id)
            subcues = split_cue_into_subcues_for_drama3(cue, domain="business_english_drama")
            assert len(subcues) >= 1
            for sc in subcues:
                d3 = translate_cue_to_drama3_input(sc, prof, attempt=1, domain="business_english_drama")
                h.oracle_domain_no_xianxia_leak(drama3_prompt=d3)
                toks = estimate_drama3_max_new_tokens(d3, language_code=sc.language_code or prof.language_code)
                assert toks <= 2048, f"{eid} {sc.cue_id}: max_new_tokens={toks} > 2048"
                gloss = str(getattr(cue, "subtitle_translation", "") or "").strip()
                if gloss and cue.language_code == "en" and h.count_cjk_chars(gloss) >= 3:
                    assert gloss not in d3, f"{eid} {cue.cue_id}: subtitle_translation leaked into TTS"


@test("T4_S05", "F17+F19+F10", "Offline 3-Bus FFmpeg Mastering (synth-dry-test), Direct Loudness Probe, Dual-Line SRT & 0.80x Pitch Preservation")
def t4_s05() -> None:
    from aigc_audio_pipeline.mixer import condition_dialogue_clip

    h.require_ffmpeg()
    h.require_file(h.PATH_REGISTRY, "voice_casting_registry.json")
    target_path = h.VARIANT_JSON_PATHS["E001_VD"]
    h.require_file(target_path, "E001_VD JSON")
    cs = h.load_cue_sheet_safe(target_path)

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t4_s05_"))
    try:
        out_dir = tmp / "dry_out"
        proc = h.run_pipeline_cli(
            [
                "synth-dry-test",
                "--registry", str(h.PATH_REGISTRY),
                "--cue-sheet", str(target_path),
                "--output-dir", str(out_dir),
            ],
            timeout=300,
        )
        assert proc.returncode == 0, f"synth-dry-test failed (rc={proc.returncode}): {proc.stderr}\n{proc.stdout}"
        payload = h.parse_last_json_object(proc.stdout)
        assert payload.get("dry_test_passed") is True

        wav_p = Path(payload["master_wav"])
        mp3_p = Path(payload["master_mp3"])
        srt_p = Path(payload["subtitles_srt"])
        man_p = Path(payload["manifest_json"])
        for p in (wav_p, mp3_p, srt_p, man_p):
            assert p.is_file() and p.stat().st_size > 100, f"Missing/empty output artifact {p}"

        probe = h.probe_audio_ffprobe(wav_p)
        assert probe["sample_rate"] == 48000 and probe["channels"] == 2 and probe["codec_name"] == "pcm_s16le"
        lufs, tp = h.measure_loudness_ffmpeg(wav_p)
        assert -24.0 <= lufs <= -12.0, f"Master integrated LUFS out of bounds: {lufs:.2f}"
        assert tp <= -0.5, f"Master true peak exceeded ceiling: {tp:.2f} dBTP"

        # Verify dual-line bilingual SRT with zero overlap
        srt_txt = srt_p.read_text(encoding="utf-8")
        sample_glosses = [
            c.subtitle_translation.strip()
            for c in cs.cues
            if c.kind == "dialogue" and c.language_code == "en" and str(getattr(c, "subtitle_translation", "")).strip() and not getattr(c, "duck_under_next", False)
        ][:3]
        h.oracle_srt_non_overlap_and_dual_line(srt_txt, expected_translations=sample_glosses)

        # Verify real 0.80x atempo duration stretch + 440Hz Goertzel pitch preservation
        raw_tone = h.write_sine_wav(tmp / "tone_440.wav", 2.0, freq_hz=440.0, sample_rate=48000, channels=1)
        norm_tone = tmp / "tone_100.wav"
        slow_tone = tmp / "tone_080.wav"
        condition_dialogue_clip(raw_tone, norm_tone, acoustic_space="studio_warm", playback_rate=1.0)
        condition_dialogue_clip(raw_tone, slow_tone, acoustic_space="studio_warm", playback_rate=0.8)
        h.oracle_audio_signal_and_atempo_ratio(
            wav_48k_path=slow_tone,
            slow_wav_path=slow_tone,
            base_wav_path=norm_tone,
            expected_pitch_hz=440.0,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T4_S06", "F15+F10+F16", "Real-Human Voice Anchor Builder (--offline-stub) & Self-Contained Colab 96GB Bundle ZIP")
def t4_s06() -> None:
    h.require_ffmpeg()
    reg = h.load_registry_safe()
    anc_out_flag = h.probe_script_flag(h.COLAB_PREPARE_ANCHORS, ("--output-dir", "--out-dir"))
    bnd_dir_flag = h.probe_script_flag(h.SCRIPT_EXPORT_BUNDLE, ("--bundle-dir", "--output-dir", "--out-dir"))
    bnd_zip_flag = h.probe_script_flag(h.SCRIPT_EXPORT_BUNDLE, ("--zip-out", "--zip-path", "--zip-output"))
    bnd_help_flags = h.get_script_help_flags(h.SCRIPT_EXPORT_BUNDLE)

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t4_s06_"))
    try:
        anc_dir = tmp / "anchors_out"
        p_anc = h.run_python_script(
            h.COLAB_PREPARE_ANCHORS,
            ["--registry", str(h.PATH_REGISTRY), anc_out_flag, str(anc_dir), "--offline-stub"],
            timeout=60,
        )
        assert p_anc.returncode == 0, f"prepare_global_edge_voice_anchors.py failed: {p_anc.stderr}"
        manifest = h.load_json_file(anc_dir / "voice_cast_drama3.json")
        h.oracle_notebook_and_bundle_integrity(voice_cast_manifest=manifest)
        assert set(manifest["characters"].keys()) == set(reg.roles.keys())
        for rid in reg.roles:
            wav_p = anc_dir / "voice_anchors" / f"{rid}.wav"
            txt_p = anc_dir / "voice_anchors" / f"{rid}.txt"
            h.oracle_audio_signal_and_atempo_ratio(wav_anchor_path=wav_p)
            assert txt_p.is_file() and txt_p.read_text(encoding="utf-8").strip()

        bnd_dir = tmp / "bundle_out"
        zip_p = tmp / "global_edge_96gb_bundle.zip"
        exp_args = [bnd_dir_flag, str(bnd_dir), bnd_zip_flag, str(zip_p)]
        if "--anchors-dir" in bnd_help_flags:
            exp_args.extend(["--anchors-dir", str(anc_dir)])
        elif "--offline-stub" in bnd_help_flags:
            exp_args.append("--offline-stub")
        p_exp = h.run_python_script(h.SCRIPT_EXPORT_BUNDLE, exp_args, timeout=180)
        assert p_exp.returncode == 0, f"export_drama3_bundle.py failed: {p_exp.stderr}\n{p_exp.stdout}"
        h.oracle_notebook_and_bundle_integrity(zip_path=zip_p)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T4_S07", "F10+F16+F19", "Unpacked Self-Contained Bundle Studio Dry-Run, Append-Only Artifacts, 0.8x Cache & E001_VARIANTS --skip-existing Idempotency")
def t4_s07() -> None:
    h.require_ffmpeg()
    bnd_dir_flag = h.probe_script_flag(h.SCRIPT_EXPORT_BUNDLE, ("--bundle-dir", "--output-dir", "--out-dir"))
    bnd_zip_flag = h.probe_script_flag(h.SCRIPT_EXPORT_BUNDLE, ("--zip-out", "--zip-path", "--zip-output"))
    bnd_help_flags = h.get_script_help_flags(h.SCRIPT_EXPORT_BUNDLE)

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t4_s07_"))
    try:
        zip_p = tmp / "bundle.zip"
        exp_args = [bnd_dir_flag, str(tmp / "raw_bnd"), bnd_zip_flag, str(zip_p)]
        if "--offline-stub" in bnd_help_flags:
            exp_args.append("--offline-stub")
        elif "--anchors-dir" in bnd_help_flags:
            anc_dir = tmp / "anchors_stub"
            anc_out_flag = h.probe_script_flag(h.COLAB_PREPARE_ANCHORS, ("--output-dir", "--out-dir"))
            p_anc = h.run_python_script(
                h.COLAB_PREPARE_ANCHORS,
                ["--registry", str(h.PATH_REGISTRY), anc_out_flag, str(anc_dir), "--offline-stub"],
                timeout=60,
            )
            assert p_anc.returncode == 0, f"Stub anchor build failed: {p_anc.stderr}"
            exp_args.extend(["--anchors-dir", str(anc_dir)])
        p_exp = h.run_python_script(h.SCRIPT_EXPORT_BUNDLE, exp_args, timeout=180)
        assert p_exp.returncode == 0, f"Bundle export failed: {p_exp.stderr}\n{p_exp.stdout}"

        # Unpack ZIP into a clean directory to prove 100% self-containment
        unpacked = tmp / "unpacked_studio"
        with zipfile.ZipFile(zip_p, "r") as zf:
            zf.extractall(unpacked)

        studio_script = unpacked / "run_global_edge_96gb_studio.py"
        h.require_file(studio_script, "unpacked run_global_edge_96gb_studio.py")
        out_dir = tmp / "outputs"
        cache_dir = tmp / "cache"

        # Run 1: AUDITION,E001_VA
        p1 = subprocess.run(
            [
                sys.executable,
                str(studio_script),
                "--studio-dir", str(unpacked),
                "--episodes", "AUDITION,E001_VA",
                "--output-dir", str(out_dir),
                "--cache-dir", str(cache_dir),
                "--offline-dry-run",
            ],
            cwd=str(unpacked),
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert p1.returncode == 0, f"Unpacked studio dry-run 1 failed: {p1.stderr}\n{p1.stdout}"

        for prefix in ("AUDITION_GLOBAL_EDGE", "E001_VA"):
            for ext in (".wav", ".mp3", ".srt", ".json", ".done"):
                matches = list(out_dir.glob(f"{prefix}*_v001{ext}"))
                assert matches, f"Missing {prefix}*_v001{ext} after studio dry-run"

        va_mp3 = sorted(out_dir.glob("E001_VA*_v001.mp3"))[0]
        va_hash_before = hashlib.sha256(va_mp3.read_bytes()).hexdigest()

        # Verify real 0.8x atempo stretch over raw 1.0x cached stems in E001_VA manifest
        va_man = h.load_json_file(sorted(out_dir.glob("E001_VA*_v001.json"))[0])
        assert va_man.get("episode_id") == "E001_VA"
        assert va_man.get("sample_rate_hz") == 48000
        dlg_tl = [it for it in va_man.get("timeline", []) if it.get("kind") == "dialogue"]
        slow_items = [it for it in dlg_tl if abs(float(it.get("playback_rate", 1.0)) - 0.8) < 1e-3]
        assert len(slow_items) >= 2, f"Expected >=2 slow 0.8x items in E001_VA manifest, got {len(slow_items)}"
        for it in slow_items:
            stem_p = Path(str(it.get("stem_file", "")))
            assert stem_p.is_file(), f"E001_VA slow item missing raw cached stem_file: {stem_p}"
            raw_dur = h.probe_audio_ffprobe(stem_p)["duration_s"]
            ratio = float(it["duration_s"]) / max(raw_dur, 1e-6)
            assert 1.15 <= ratio <= 1.35, (
                f"E001_VA slow cue {it.get('cue_id')} manifest stretch ratio={ratio:.3f} "
                f"(dur={it['duration_s']}s / raw={raw_dur:.3f}s) outside [1.15, 1.35]"
            )
        # Check stem_file equality on any identical (role_id, language_code, tagged_text) pair with 0.8x & 1.0x
        by_key: dict[tuple[str, str, str], list[dict]] = {}
        for it in dlg_tl:
            k = (str(it.get("role_id", "")), str(it.get("language_code", "")), str(it.get("tagged_text", it.get("text", ""))))
            by_key.setdefault(k, []).append(it)
        for k, group in by_key.items():
            slow_g = [x for x in group if abs(float(x.get("playback_rate", 1.0)) - 0.8) < 1e-3]
            norm_g = [x for x in group if abs(float(x.get("playback_rate", 1.0)) - 1.0) < 1e-3]
            if slow_g and norm_g:
                assert Path(slow_g[0]["stem_file"]).resolve() == Path(norm_g[0]["stem_file"]).resolve(), (
                    f"Identical text tuple {k} did not share cached 1.0x stem between 0.8x and 1.0x"
                )
        # Deterministic 2-cue identical-text 1.0x/0.8x cache probe using unpacked self-contained studio script
        h.verify_studio_08x_cache_reuse(studio_script, tmp, self_contained=True)

        # Run 2: REAL --episodes E001_VARIANTS --skip-existing --offline-dry-run
        # Proves E001_VA stays untouched (0 _v002, identical MP3 SHA-256) while VB/VC/VD all render _v001.*
        p2 = subprocess.run(
            [
                sys.executable,
                str(studio_script),
                "--studio-dir", str(unpacked),
                "--episodes", "E001_VARIANTS",
                "--output-dir", str(out_dir),
                "--cache-dir", str(cache_dir),
                "--skip-existing",
                "--offline-dry-run",
            ],
            cwd=str(unpacked),
            capture_output=True,
            text=True,
            timeout=360,
        )
        assert p2.returncode == 0, f"Studio E001_VARIANTS --skip-existing failed: {p2.stderr[-800:]}\n{p2.stdout[-400:]}"
        assert not list(out_dir.glob("E001_VA*_v002.*")), "--skip-existing unexpectedly created E001_VA _v002!"
        assert hashlib.sha256(va_mp3.read_bytes()).hexdigest() == va_hash_before
        for vid in ("E001_VB", "E001_VC", "E001_VD"):
            for ext in (".wav", ".mp3", ".srt", ".json", ".done"):
                assert list(out_dir.glob(f"{vid}*_v001{ext}")), (
                    f"E001_VARIANTS expansion failed to render {vid}*_v001{ext}"
                )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@test("T4_S08", "F10+F16", "Colab G4 Launcher Offline Dry-Run (Isolated TMPDIR/work-dir) & Jupyter Notebook Schema + Flag Parity")
def t4_s08() -> None:
    h.require_ffmpeg()
    launcher_flags = h.get_script_help_flags(h.COLAB_LAUNCH_G4)
    nb = h.load_json_file(h.COLAB_NOTEBOOK, h.COLAB_NOTEBOOK.name)
    h.oracle_notebook_and_bundle_integrity(notebook_data=nb, launcher_help_flags=launcher_flags)

    tmp = Path(tempfile.mkdtemp(prefix="ge_e2e_t4_s08_"))
    preexisting_default_work = Path("/tmp/global_edge_work").exists()
    try:
        args = ["--episodes", "E001_VA", "--offline-dry-run"]
        if "--work-dir" in launcher_flags:
            args.extend(["--work-dir", str(tmp / "work")])
        if "--output-dir" in launcher_flags:
            args.extend(["--output-dir", str(tmp / "out")])
        proc = h.run_python_script(
            h.COLAB_LAUNCH_G4,
            args,
            timeout=300,
            extra_env={"TMPDIR": str(tmp)},
        )
        assert proc.returncode == 0, (
            f"launch_g4_global_edge_drama3.py --offline-dry-run failed (rc={proc.returncode}):\n"
            f"{proc.stderr[-1200:]}\n{proc.stdout[-800:]}"
        )

        # Verify generated E001_VA _v001.{wav,mp3,srt,json,done} and v2 voice_cast_drama3.json
        search_roots = [tmp]
        if "--work-dir" not in launcher_flags and "--output-dir" not in launcher_flags:
            default_work = Path("/tmp/global_edge_work")
            if default_work.is_dir():
                search_roots.append(default_work)

        done_hits = [p for root in search_roots for p in root.rglob("E001_VA*_v001.done")]
        assert done_hits, (
            f"Launcher dry-run exited 0 but produced no E001_VA*_v001.done under {[str(r) for r in search_roots]}"
        )
        done_p = sorted(done_hits)[0]
        for ext in (".wav", ".mp3", ".srt", ".json", ".done"):
            art_p = done_p.with_suffix(ext)
            assert art_p.is_file() and art_p.stat().st_size > 0, f"Launcher missing/empty artifact {art_p}"
        man = h.load_json_file(done_p.with_suffix(".json"))
        assert man.get("episode_id") == "E001_VA", f"Launcher manifest episode_id={man.get('episode_id')!r}"
        assert man.get("sample_rate_hz") == 48000, f"Launcher manifest sample_rate_hz={man.get('sample_rate_hz')!r}"

        anc_manifests = [p for root in search_roots for p in root.rglob("voice_cast_drama3.json")]
        assert anc_manifests, (
            f"Launcher dry-run produced no voice_cast_drama3.json under {[str(r) for r in search_roots]}"
        )
        h.oracle_notebook_and_bundle_integrity(voice_cast_manifest=h.load_json_file(sorted(anc_manifests)[0]))

        # AST audit confirms zero ElevenLabs/edge-tts in launcher
        h.oracle_ast_zero_api_and_zero_edge_tts(h.load_text_file(h.COLAB_LAUNCH_G4), h.COLAB_LAUNCH_G4.name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if not preexisting_default_work and Path("/tmp/global_edge_work").exists():
            shutil.rmtree("/tmp/global_edge_work", ignore_errors=True)


@test("T4_S09", "F09+F16+F02", "Comparative Rubric, 45s Viral Clip Funnel, Paid Companion Manual & README Cross-Audit")
def t4_s09() -> None:
    variants = h.load_all_e001_variants()
    rubric = h.load_text_file(h.PATH_RUBRIC_MD, "E001_COMPARATIVE_EVAL_RUBRIC.md")
    kit = h.load_text_file(h.PATH_LAUNCH_KIT_MD, "LAUNCH_KIT_AND_E001_45S_CLIPS.md")
    manual = h.load_text_file(h.PATH_COMPANION_MD, "E001_BILINGUAL_COMPANION_MANUAL.md")
    readme = h.load_text_file(h.PATH_README, "projects/global_edge/README.md")

    # 1. 5-10 dimension blind-listening rubric sums to exact 100 + Hybrid-Winner Rule + all 4 variants
    h.oracle_viral_45s_cutlist_and_rubric(rubric_md=rubric)
    for vid in ("E001_VA", "E001_VB", "E001_VC", "E001_VD"):
        assert vid in rubric and vid in readme
    assert any(k in rubric.lower() for k in ("hybrid", "融合", "混合胜出"))

    # 2. All viral clip cutlists map to valid cue_id ranges summing to [38, 55]s with hook + CTA
    cutlists = h.extract_viral_cutlists_from_markdown(kit, variants)
    assert len(cutlists) >= 1, "Expected >= 1 executable 38-55s viral clip cutlist in LAUNCH_KIT_AND_E001_45S_CLIPS.md"
    h.oracle_viral_45s_cutlist_and_rubric(cutlists=cutlists, cue_sheets_by_variant=variants)

    # 3. Paid Companion Manual covers 8/8 mandatory phrases with 0 raw ASR typos
    norm_manual = h.normalize_for_phrase_match(manual)
    for pid, label, and_clauses in h.E001_MANDATORY_PHRASES:
        for alts in and_clauses:
            assert any(a in norm_manual for a in alts), f"Companion manual missing {pid} ({label})"
    for bad_pat in (r"\blaw of holds\b", r"\[snorts\]", r"\bJipu\b", r"\bPalanteer\b"):
        assert not re.search(bad_pat, manual, re.IGNORECASE), f"ASR typo {bad_pat!r} leaked into Companion Manual"

    # 4. README launcher flags match launch_g4_global_edge_drama3.py --help (zero Buffett-style flag drift!)
    launcher_flags = h.get_script_help_flags(h.COLAB_LAUNCH_G4)
    readme_flags = h.extract_launcher_cli_flags_from_text(readme, "launch_g4_global_edge_drama3.py")
    unknown_in_readme = sorted(readme_flags - launcher_flags)
    assert not unknown_in_readme, (
        f"README.md passes unsupported CLI flag(s) to launch_g4_global_edge_drama3.py: {unknown_in_readme}"
    )


@test("T4_S10", "F18+F19", "Zero-Regression Baseline (21/21), Unit-Test Isolation & Live Dual-Script zh-en QA on Real E001 Cues")
def t4_s10() -> None:
    from aigc_audio_pipeline.qa import evaluate_dialogue_qa

    # 1. check-env --offline exits 0
    env_proc = h.run_pipeline_cli(["check-env", "--offline"], timeout=30)
    assert env_proc.returncode == 0, f"check-env --offline failed: {env_proc.stdout}\n{env_proc.stderr}"

    # 2. Legacy baseline tests/test_pipeline.py passes 21/21
    base_proc = subprocess.run(
        [sys.executable, "-m", "unittest", "tests/test_pipeline.py"],
        cwd=str(h.REPO_ROOT),
        env=h.pipeline_env(),
        capture_output=True,
        text=True,
        timeout=180,
    )
    combined = (base_proc.stdout or "") + "\n" + (base_proc.stderr or "")
    assert base_proc.returncode == 0, f"Baseline tests/test_pipeline.py failed:\n{combined[-1000:]}"
    m = re.search(r"Ran\s+(\d+)\s+tests?", combined)
    assert m and int(m.group(1)) >= 21

    # 3. Verify tests/e2e_global_edge/__init__.py does NOT exist & unittest discover excludes E2E modules
    assert not (h.THIS_DIR / "__init__.py").exists(), "ZERO-POLLUTION VIOLATION: tests/e2e_global_edge/__init__.py exists!"
    suite = unittest.TestLoader().discover(str(h.REPO_ROOT / "tests"))

    def _iter_ids(s):
        for item in s:
            if isinstance(item, unittest.TestSuite):
                yield from _iter_ids(item)
            else:
                yield item.id()

    discovered_ids = list(_iter_ids(suite))
    assert len(discovered_ids) >= 21
    assert not any("e2e_global_edge" in tid for tid in discovered_ids), (
        f"E2E modules polluted unittest discover: {[t for t in discovered_ids if 'e2e_global_edge' in t]}"
    )

    # 4. Live dual-script zh-en QA on real bilingual cues from E001_VB / E001_VD
    vb = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VB"])
    vd = h.load_cue_sheet_safe(h.VARIANT_JSON_PATHS["E001_VD"])
    bilingual = [
        c for c in (vb.cues + vd.cues)
        if c.kind == "dialogue"
        and c.language_code == "zh-en"
        and h.count_cjk_chars(h.strip_inline_tags(c.text)[1]) >= 4
        and h.count_en_words(h.strip_inline_tags(c.text)[1]) >= 3
    ]
    assert len(bilingual) >= 1, "No mixed zh-en cues found in E001_VB/E001_VD"
    cue = bilingual[0]
    _, spoken = h.strip_inline_tags(cue.text)
    assert evaluate_dialogue_qa(tagged_prompt=cue.text, asr_text=spoken, duration_s=3.5, peak_dbfs=-6.0, language_code="zh-en").passed is True

    # Mutated dropped-EN must FAIL
    no_en = re.sub(r"[A-Za-z][A-Za-z0-9'\-]*", "", spoken).strip()
    assert evaluate_dialogue_qa(tagged_prompt=cue.text, asr_text=no_en, duration_s=3.5, peak_dbfs=-6.0, language_code="zh-en").passed is False

    # Mutated truncated tail must FAIL
    trunc = spoken[: max(4, len(spoken) // 3)]
    assert evaluate_dialogue_qa(tagged_prompt=cue.text, asr_text=trunc, duration_s=3.5, peak_dbfs=-6.0, language_code="zh-en").passed is False

    # Mutated leaked corporate tag must FAIL
    leaked = evaluate_dialogue_qa(
        tagged_prompt="[deadpan] " + spoken,
        asr_text="deadpan " + spoken,
        duration_s=3.5,
        peak_dbfs=-6.0,
        language_code="zh-en",
    )
    assert leaked.passed is False and "deadpan" in leaked.leaked_tags


TESTS = COLLECTOR.tests
assert len(TESTS) == 10, f"Expected exact 10 Tier 4 workload scenarios, got {len(TESTS)}"
