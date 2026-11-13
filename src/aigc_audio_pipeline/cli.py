"""CLI entrypoints for validating scripts, searching voices, running auditions, and mastering episodes."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from .adapter import analyze_markdown_chapter, write_cue_sheet_markdown
from .elevenlabs_client import (
    PERSISTENT_KEY_PATHS,
    ElevenLabsClient,
    resolve_elevenlabs_api_key,
)
from .mixer import master_episode_three_bus, render_audition_reel
from .models import (
    AuditionRecord,
    EpisodeCueSheet,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
    next_append_only_path,
    utc_now_iso,
)
from .polyphones import apply_xianxia_polyphone_overrides
from .qa import synthesize_with_playbook_qa


def append_ledger_entry(ledger_path: Path, entry: dict[str, Any]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def cmd_check_env(args: argparse.Namespace) -> int:
    ffmpeg_ok = subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode == 0
    key = resolve_elevenlabs_api_key()
    info: dict[str, Any] = {
        "ffmpeg_available": ffmpeg_ok,
        "api_key_configured": bool(key),
        "persistent_key_search_paths": [str(p) for p in PERSISTENT_KEY_PATHS],
    }
    if key and not args.offline:
        client = ElevenLabsClient(api_key=key)
        sub = client.get_subscription_safe()
        if sub.get("_permission_skipped"):
            info["subscription"] = sub
        else:
            used = sub.get("character_count", 0)
            limit = sub.get("character_limit", 0)
            info["subscription"] = {
                "tier": sub.get("tier"),
                "status": sub.get("status"),
                "character_count": used,
                "character_limit": limit,
                "character_remaining": max(0, int(limit) - int(used)) if limit else None,
            }
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0 if ffmpeg_ok else 1


def cmd_validate(args: argparse.Namespace) -> int:
    registry = VoiceCastingRegistry.load(Path(args.registry))
    cue_sheet = EpisodeCueSheet.load(Path(args.cue_sheet))
    errors = cue_sheet.validate(registry=registry, require_locked_voices=args.require_locked_voices)
    dialogue_cues = [c for c in cue_sheet.cues if c.kind == "dialogue"]
    sfx_cues = [c for c in cue_sheet.cues if c.kind == "sfx"]
    summary = {
        "valid": len(errors) == 0,
        "episode_id": cue_sheet.episode_id,
        "mode": cue_sheet.mode,
        "act_count": len(cue_sheet.acts),
        "dialogue_cue_count": len(dialogue_cues),
        "sfx_cue_count": len(sfx_cues),
        "estimated_tts_characters_with_tags": sum(len(c.text) for c in dialogue_cues),
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


def cmd_voices_search(args: argparse.Namespace) -> int:
    client = ElevenLabsClient()
    voices = client.search_shared_voices(
        language="zh",
        locale=args.locale,
        gender=args.gender,
        age=args.age,
        search=args.search,
        page_size=args.limit,
        strict_mainland=not args.allow_all_accents,
    )
    compact = [
        {
            "name": v.get("name"),
            "voice_id": v.get("voice_id"),
            "public_owner_id": v.get("public_owner_id"),
            "gender": v.get("gender"),
            "age": v.get("age"),
            "accent": v.get("accent"),
            "locale": v.get("locale"),
            "category": v.get("category"),
            "descriptive": v.get("descriptive"),
            "use_case": v.get("use_case"),
            "preview_url": v.get("preview_url"),
            "description": (v.get("description") or "")[:140],
        }
        for v in voices
    ]
    print(json.dumps({"count": len(compact), "voices": compact}, ensure_ascii=False, indent=2))
    return 0


def cmd_voices_list_mine(_args: argparse.Namespace) -> int:
    client = ElevenLabsClient()
    voices = client.list_my_voices()
    compact = [
        {
            "name": v.get("name"),
            "voice_id": v.get("voice_id"),
            "category": v.get("category"),
            "labels": v.get("labels"),
            "preview_url": v.get("preview_url"),
        }
        for v in voices
    ]
    print(json.dumps({"count": len(compact), "voices": compact}, ensure_ascii=False, indent=2))
    return 0


def cmd_voices_bind(args: argparse.Namespace) -> int:
    reg_path = Path(args.registry)
    registry = VoiceCastingRegistry.load(reg_path)
    prof = registry.resolve_role(args.role)
    if prof is None:
        print(f"Error: role {args.role!r} not found in {reg_path}", file=sys.stderr)
        return 1

    if args.public_owner_id and args.add_to_library:
        client = ElevenLabsClient()
        new_name = args.new_name or f"{registry.project_id}_{prof.display_name}_{args.library_name or args.voice_id[:6]}"
        client.add_shared_voice(args.public_owner_id, args.voice_id, new_name=new_name)
        prof.library_voice_name = new_name
    elif args.library_name:
        prof.library_voice_name = args.library_name

    prof.voice_id = args.voice_id
    if args.public_owner_id:
        prof.public_owner_id = args.public_owner_id
    prof.status = "locked" if args.lock else "auditioning"
    registry.save(reg_path)
    print(
        json.dumps(
            {
                "updated_role": prof.role_id,
                "display_name": prof.display_name,
                "voice_id": prof.voice_id,
                "library_voice_name": prof.library_voice_name,
                "status": prof.status,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_voices_design(args: argparse.Namespace) -> int:
    """Design 3 custom native Chinese voice previews via ElevenLabs `eleven_ttv_v3`."""
    client = ElevenLabsClient()
    out_dir = Path(args.output_dir)
    previews, text_used = client.design_voice_previews(
        voice_description=args.description,
        sample_text=args.sample_text or None,
        output_dir=out_dir,
        filename_prefix=args.prefix,
        loudness=args.loudness,
        guidance_scale=args.guidance_scale,
        auto_generate_text=args.auto_generate_text,
    )
    manifest = {
        "created_at": utc_now_iso(),
        "model_id": "eleven_ttv_v3",
        "voice_description": args.description,
        "sample_text_used": text_used,
        "previews": [
            {
                "generated_voice_id": p.generated_voice_id,
                "wav_path": str(p.wav_path),
                "mp3_path": str(p.mp3_path),
                "duration_s": p.duration_s,
                "language": p.language,
            }
            for p in previews
        ],
    }
    manifest_path = out_dir / f"{args.prefix}_design_manifest.json"
    idx = 2
    while manifest_path.exists():
        manifest_path = out_dir / f"{args.prefix}_design_manifest_v{idx:02d}.json"
        idx += 1
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), **manifest}, ensure_ascii=False, indent=2))
    return 0


def cmd_voices_create_designed(args: argparse.Namespace) -> int:
    """Save a chosen `generated_voice_id` into workspace My Voices and optionally bind to registry."""
    client = ElevenLabsClient()
    created = client.create_designed_voice(
        generated_voice_id=args.generated_voice_id,
        voice_name=args.name,
        voice_description=args.description,
    )
    voice_id = str(created.get("voice_id") or "")
    out: dict[str, Any] = {
        "created_voice_id": voice_id,
        "voice_name": args.name,
        "generated_voice_id": args.generated_voice_id,
    }
    if args.registry and args.role and voice_id:
        reg_path = Path(args.registry)
        registry = VoiceCastingRegistry.load(reg_path)
        prof = registry.resolve_role(args.role)
        if prof is None:
            print(f"Error: role {args.role!r} not found in {reg_path}", file=sys.stderr)
            return 1
        prof.voice_id = voice_id
        prof.library_voice_name = f"{args.name} (VoiceDesign eleven_ttv_v3)"
        prof.status = "locked" if args.lock else "auditioning"
        registry.save(reg_path)
        out["bound_role"] = prof.role_id
        out["status"] = prof.status
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_audition(args: argparse.Namespace) -> int:
    """Run Playbook Step 1 / Step 3 short dialogue-only audition with Scribe QA."""
    reg_path = Path(args.registry)
    registry = VoiceCastingRegistry.load(reg_path)
    cue_sheet = EpisodeCueSheet.load(Path(args.cue_sheet))
    errors = cue_sheet.validate(registry=registry, require_locked_voices=True)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    cache_dir = Path(args.cache_dir) if args.cache_dir else out_dir / ".cache"
    client = ElevenLabsClient(cache_dir=cache_dir)
    sub_before = client.get_subscription_safe()

    audition_items: list[dict[str, Any]] = []
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    for cue in cue_sheet.cues:
        if cue.kind != "dialogue":
            continue
        prof = registry.resolve_role(cue.role_id)
        assert prof is not None
        clip_wav = clips_dir / f"{cue_sheet.episode_id}_{cue.cue_id}_{prof.role_id}_{prof.voice_id[:8]}.wav"
        # Append-only if already exists
        if clip_wav.exists():
            idx = 2
            while clip_wav.exists():
                clip_wav = clips_dir / f"{cue_sheet.episode_id}_{cue.cue_id}_{prof.role_id}_{prof.voice_id[:8]}_v{idx:02d}.wav"
                idx += 1

        synth, qa, final_text = synthesize_with_playbook_qa(
            client,
            voice_id=prof.voice_id,
            tagged_text=cue.tts_text or apply_xianxia_polyphone_overrides(cue.text),
            canonical_prompt=cue.text,
            output_wav=clip_wav,
            stability=cue.stability,
            similarity_boost=cue.similarity_boost,
            language_code=registry.language_code,
            enable_asr_qa=not args.skip_asr_qa,
        )
        prof.audition_history.append(
            AuditionRecord(
                recorded_at=utc_now_iso(),
                voice_id=prof.voice_id,
                library_voice_name=prof.library_voice_name,
                sample_text=final_text,
                stability=cue.stability,
                similarity_boost=cue.similarity_boost,
                local_file=str(clip_wav),
                qa_passed=qa.passed,
                decision="candidate",
                notes="; ".join(qa.reasons) if qa.reasons else "ASR QA passed",
            )
        )
        audition_items.append(
            {
                "cue_id": cue.cue_id,
                "role_id": prof.role_id,
                "display_name": prof.display_name,
                "voice_id": prof.voice_id,
                "library_voice_name": prof.library_voice_name,
                "stability": cue.stability,
                "similarity_boost": cue.similarity_boost,
                "requested_text": cue.text,
                "final_text_used": final_text,
                "wav_path": clip_wav,
                "duration_s": synth.duration_s,
                "qa": qa.to_dict(),
            }
        )

    registry.save(reg_path)
    reel = render_audition_reel(audition_items, out_dir, f"{cue_sheet.episode_id}_audition_reel")
    sub_after = client.get_subscription_safe()

    if args.ledger:
        append_ledger_entry(
            Path(args.ledger),
            {
                "timestamp": utc_now_iso(),
                "action": "audition",
                "episode_id": cue_sheet.episode_id,
                "line_count": len(audition_items),
                "qa_all_passed": all(it["qa"]["passed"] for it in audition_items),
                "subscription_used_before": sub_before.get("character_count"),
                "subscription_used_after": sub_after.get("character_count"),
                "reel_mp3": str(reel["mp3"]),
                "manifest": str(reel["manifest"]),
            },
        )

    print(
        json.dumps(
            {
                "audition_reel_wav": str(reel["wav"]),
                "audition_reel_mp3": str(reel["mp3"]),
                "manifest": str(reel["manifest"]),
                "qa_all_passed": all(it["qa"]["passed"] for it in audition_items),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_render_episode(args: argparse.Namespace) -> int:
    """Render full multi-cast episode: ElevenLabs v3 dialogue + SFX v3 + Music v2.5 + 3-bus master."""
    reg_path = Path(args.registry)
    registry = VoiceCastingRegistry.load(reg_path)
    cue_sheet = EpisodeCueSheet.load(Path(args.cue_sheet))
    errors = cue_sheet.validate(registry=registry, require_locked_voices=True)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    stems_dir = out_dir / f"{cue_sheet.episode_id}_stems"
    stems_dir.mkdir(parents=True, exist_ok=True)
    motifs_dir = Path(args.motifs_dir) if getattr(args, "motifs_dir", "") else None
    if motifs_dir is not None:
        motifs_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = Path(args.cache_dir) if args.cache_dir else out_dir / ".cache"
    workers = max(1, int(getattr(args, "workers", 4)))

    client = ElevenLabsClient(cache_dir=cache_dir)
    sub_before = client.get_subscription_safe()

    cue_audio_map: dict[str, Path] = {}
    cue_meta_map: dict[str, dict[str, Any]] = {}
    qa_failures: list[dict[str, Any]] = []

    # 1a. Pre-resolve/generate reusable sonic motifs sequentially (prevents duplicate motif races)
    pending_cues: list[Any] = []
    for cue in cue_sheet.cues:
        if cue.kind == "sfx" and cue.motif_id and cue.motif_id in registry.sonic_motifs:
            motif = registry.sonic_motifs[cue.motif_id]
            if motif.cached_file and Path(motif.cached_file).is_file():
                cue_audio_map[cue.cue_id] = Path(motif.cached_file)
                continue
            stem_wav = (
                next_append_only_path(motifs_dir, cue.motif_id, ".wav")
                if motifs_dir is not None
                else stems_dir / f"{cue.cue_id}_sfx.wav"
            )
            sfx_res = client.generate_sfx(
                prompt=cue.sfx_prompt or motif.sfx_prompt,
                output_wav=stem_wav,
                duration_seconds=cue.duration_seconds or motif.duration_seconds,
                prompt_influence=motif.prompt_influence,
                loop=motif.loop,
                model_id=registry.sfx_model_id,
            )
            motif.cached_file = str(sfx_res.wav_path)
            cue_audio_map[cue.cue_id] = sfx_res.wav_path
        else:
            pending_cues.append(cue)

    # 1b. Synthesize all dialogue & custom SFX cues concurrently
    def _synth_cue(cue: Any) -> tuple[str, Path, dict[str, Any] | None, dict[str, Any] | None]:
        if cue.kind == "dialogue":
            prof = registry.resolve_role(cue.role_id)
            assert prof is not None
            stem_wav = stems_dir / f"{cue.cue_id}_{prof.role_id}.wav"
            effective_tts = cue.tts_text or apply_xianxia_polyphone_overrides(cue.text)
            synth, qa, final_text = synthesize_with_playbook_qa(
                client,
                voice_id=prof.voice_id,
                tagged_text=effective_tts,
                canonical_prompt=cue.text,
                output_wav=stem_wav,
                stability=cue.stability,
                similarity_boost=cue.similarity_boost,
                language_code=registry.language_code,
                enable_asr_qa=not args.skip_asr_qa,
            )
            meta = {
                "voice_id": prof.voice_id,
                "final_text": final_text,
                "qa_passed": qa.passed,
                "qa": qa.to_dict(),
            }
            fail = {"cue_id": cue.cue_id, "role_id": prof.role_id, "qa": qa.to_dict()} if not qa.passed else None
            return cue.cue_id, synth.wav_path, meta, fail

        stem_wav = stems_dir / f"{cue.cue_id}_sfx.wav"
        sfx_res = client.generate_sfx(
            prompt=cue.sfx_prompt,
            output_wav=stem_wav,
            duration_seconds=cue.duration_seconds,
            prompt_influence=cue.prompt_influence,
            loop=cue.loop,
            model_id=registry.sfx_model_id,
        )
        return cue.cue_id, sfx_res.wav_path, None, None

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_synth_cue, c) for c in pending_cues]
        for fut in as_completed(futs):
            cid, wav_path, meta, fail = fut.result()
            cue_audio_map[cid] = wav_path
            if meta is not None:
                cue_meta_map[cid] = meta
            if fail is not None:
                qa_failures.append(fail)

    qa_failures.sort(key=lambda x: x["cue_id"])
    if qa_failures and args.strict_qa:
        print(
            json.dumps(
                {"aborted_on_qa_failure": qa_failures[0]["cue_id"], "qa_failures": qa_failures},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 3

    # 2. Compose or reuse per-act instrumental BGM beds concurrently
    act_bgm_map: dict[str, Path] = {}
    pending_acts: list[Any] = []
    for act in cue_sheet.acts:
        if act.cached_bgm_file and Path(act.cached_bgm_file).is_file():
            act_bgm_map[act.act_id] = Path(act.cached_bgm_file)
        else:
            pending_acts.append(act)

    if pending_acts:
        def _compose_act(act: Any) -> tuple[str, Path]:
            bgm_wav = stems_dir / f"bgm_{act.act_id}.wav"
            bgm_res = client.compose_music(
                prompt=act.bgm_prompt,
                output_wav=bgm_wav,
                duration_seconds=act.bgm_duration_s,
                force_instrumental=True,
                model_id=registry.music_model_id,
            )
            return act.act_id, bgm_res.wav_path

        with ThreadPoolExecutor(max_workers=min(workers, len(pending_acts))) as pool:
            for aid, bpath in pool.map(_compose_act, pending_acts):
                act_bgm_map[aid] = bpath

    registry.save(reg_path)

    # 3. Master 3-bus natural timeline
    master_info = master_episode_three_bus(
        cue_sheet=cue_sheet,
        cue_audio_map=cue_audio_map,
        act_bgm_map=act_bgm_map,
        output_dir=out_dir,
        cue_meta_map=cue_meta_map,
        registry=registry,
        workers=workers,
        clean_work_dir=bool(getattr(args, "clean_work_dir", False)),
    )
    sub_after = client.get_subscription_safe()

    result_payload = {
        "episode_id": cue_sheet.episode_id,
        "total_duration_s": master_info["total_duration_s"],
        "master_wav": str(master_info["master_wav"]),
        "master_mp3": str(master_info["master_mp3"]),
        "subtitles_srt": str(master_info["subtitles_srt"]),
        "manifest_json": str(master_info["manifest_json"]),
        "qa_failures": qa_failures,
        "subscription_used_before": sub_before.get("character_count"),
        "subscription_used_after": sub_after.get("character_count"),
    }
    if args.ledger:
        append_ledger_entry(
            Path(args.ledger),
            {"timestamp": utc_now_iso(), "action": "render_episode", **result_payload},
        )

    print(json.dumps(result_payload, ensure_ascii=False, indent=2))
    return 0


def cmd_export_markdown(args: argparse.Namespace) -> int:
    registry = VoiceCastingRegistry.load(Path(args.registry)) if args.registry else None
    cue_sheet = EpisodeCueSheet.load(Path(args.cue_sheet))
    out_md = write_cue_sheet_markdown(cue_sheet, Path(args.output), registry=registry)
    print(json.dumps({"markdown_script": str(out_md)}, ensure_ascii=False, indent=2))
    return 0


def cmd_analyze_chapter(args: argparse.Namespace) -> int:
    registry = VoiceCastingRegistry.load(Path(args.registry)) if args.registry else None
    text = Path(args.chapter).read_text(encoding="utf-8")
    report = analyze_markdown_chapter(text, registry=registry)
    segments = report.pop("segments")
    if args.include_segments:
        report["segments"] = [asdict(s) for s in segments]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_synth_dry_test(args: argparse.Namespace) -> int:
    """Offline end-to-end verification of cue sheet + 3-bus mixer using FFmpeg lavfi synthetic waveforms."""
    registry = VoiceCastingRegistry.load(Path(args.registry)) if args.registry else None
    cue_sheet = EpisodeCueSheet.load(Path(args.cue_sheet))
    errors = cue_sheet.validate(registry=registry, require_locked_voices=False)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    synth_dir = out_dir / "_synthetic_stems"
    synth_dir.mkdir(parents=True, exist_ok=True)

    cue_audio_map: dict[str, Path] = {}
    for idx, cue in enumerate(cue_sheet.cues):
        wav = synth_dir / f"{cue.cue_id}.wav"
        if cue.kind == "dialogue":
            _, spoken = extract_tags_and_spoken_text(cue.text)
            # Natural Mandarin dramatic cadence ~ 4.2 chars/sec
            dur_s = max(0.8, min(18.0, len(spoken) / 4.2))
            freq = 185 + (idx % 5) * 35
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    f"sine=frequency={freq}:duration={dur_s:.2f}:sample_rate=48000",
                    "-af",
                    "volume=-14dB,afade=t=in:st=0:d=0.04,afade=t=out:st=" + f"{max(0.0, dur_s - 0.08):.2f}:d=0.08",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    str(wav),
                ],
                check=True,
            )
        else:
            dur_s = min(cue.duration_seconds, 6.0)
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    f"anoisesrc=color=pink:duration={dur_s:.2f}:sample_rate=48000:amplitude=0.25",
                    "-af",
                    f"afade=t=in:st=0:d=0.05,afade=t=out:st={max(0.0, dur_s - 0.2):.2f}:d=0.2",
                    "-ac",
                    "2",
                    "-c:a",
                    "pcm_s16le",
                    str(wav),
                ],
                check=True,
            )
        cue_audio_map[cue.cue_id] = wav

    act_bgm_map: dict[str, Path] = {}
    for a_idx, act in enumerate(cue_sheet.acts):
        bgm_wav = synth_dir / f"bgm_{act.act_id}.wav"
        base_f = 110 + a_idx * 22
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency={base_f}:duration=12.0:sample_rate=48000",
                "-af",
                "volume=-12dB",
                "-ac",
                "2",
                "-c:a",
                "pcm_s16le",
                str(bgm_wav),
            ],
            check=True,
        )
        act_bgm_map[act.act_id] = bgm_wav

    master_info = master_episode_three_bus(
        cue_sheet=cue_sheet,
        cue_audio_map=cue_audio_map,
        act_bgm_map=act_bgm_map,
        output_dir=out_dir,
        registry=registry,
    )
    print(
        json.dumps(
            {
                "dry_test_passed": True,
                "total_duration_s": master_info["total_duration_s"],
                "master_wav": str(master_info["master_wav"]),
                "master_mp3": str(master_info["master_mp3"]),
                "subtitles_srt": str(master_info["subtitles_srt"]),
                "manifest_json": str(master_info["manifest_json"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aigc-audio",
        description="Chinese radio-drama & multi-cast audio drama pipeline (ElevenLabs v3 + FFmpeg 3-bus master).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_env = sub.add_parser("check-env", help="Verify FFmpeg, API key, and ElevenLabs quota.")
    p_env.add_argument("--offline", action="store_true", help="Do not query remote subscription endpoint.")
    p_env.set_defaults(func=cmd_check_env)

    p_val = sub.add_parser("validate", help="Validate registry and episode cue sheet against Playbook hard rules.")
    p_val.add_argument("--registry", required=True, help="Path to voice_casting_registry.json")
    p_val.add_argument("--cue-sheet", required=True, help="Path to episode_cue_sheet.json")
    p_val.add_argument("--require-locked-voices", action="store_true", help="Fail if any role lacks voice_id.")
    p_val.set_defaults(func=cmd_validate)

    p_voices = sub.add_parser("voices", help="Search, design, list, or bind Mainland Mandarin dramatic voices.")
    v_sub = p_voices.add_subparsers(dest="voices_cmd", required=True)

    p_vs = v_sub.add_parser("search", help="Search ElevenLabs Shared Voice Library (Mainland Mandarin filtered).")
    p_vs.add_argument("--locale", default="cmn-CN", help="ElevenLabs locale (default: cmn-CN).")
    p_vs.add_argument("--gender", default=None, choices=["male", "female", "neutral"])
    p_vs.add_argument("--age", default=None, choices=["young", "middle_aged", "old"])
    p_vs.add_argument("--search", default=None, help="Keyword (e.g. drama, audiobook, cold, narrator, old).")
    p_vs.add_argument("--limit", type=int, default=25)
    p_vs.add_argument("--allow-all-accents", action="store_true")
    p_vs.set_defaults(func=cmd_voices_search)

    p_vl = v_sub.add_parser("list-mine", help="List voices already in your ElevenLabs workspace.")
    p_vl.set_defaults(func=cmd_voices_list_mine)

    p_vd = v_sub.add_parser(
        "design",
        help="Create 3 brand-new native Chinese voice candidates from text prompt via eleven_ttv_v3.",
    )
    p_vd.add_argument("--description", required=True, help="20..1000 char Chinese/English timbre & persona prompt.")
    p_vd.add_argument("--sample-text", default="", help="100..1000 char Chinese audition text.")
    p_vd.add_argument("--auto-generate-text", action="store_true")
    p_vd.add_argument("--output-dir", required=True)
    p_vd.add_argument("--prefix", default="designed_voice")
    p_vd.add_argument("--loudness", type=float, default=0.5)
    p_vd.add_argument("--guidance-scale", type=float, default=6.0)
    p_vd.set_defaults(func=cmd_voices_design)

    p_vc = v_sub.add_parser(
        "create-designed",
        help="Save a chosen generated_voice_id permanently into My Voices and optionally bind to registry.",
    )
    p_vc.add_argument("--generated-voice-id", required=True)
    p_vc.add_argument("--name", required=True, help="Permanent voice name in My Voices.")
    p_vc.add_argument("--description", required=True, help="20..1000 char description.")
    p_vc.add_argument("--registry", default="")
    p_vc.add_argument("--role", default="")
    p_vc.add_argument("--lock", action="store_true")
    p_vc.set_defaults(func=cmd_voices_create_designed)

    p_vb = v_sub.add_parser("bind", help="Bind (and optionally add from shared library) a voice_id to a role.")
    p_vb.add_argument("--registry", required=True)
    p_vb.add_argument("--role", required=True)
    p_vb.add_argument("--voice-id", required=True)
    p_vb.add_argument("--public-owner-id", default="")
    p_vb.add_argument("--library-name", default="")
    p_vb.add_argument("--new-name", default="", help="Mandatory name when adding from Shared Voice Library.")
    p_vb.add_argument("--add-to-library", action="store_true")
    p_vb.add_argument("--lock", action="store_true", help="Mark role status as locked.")
    p_vb.set_defaults(func=cmd_voices_bind)

    p_aud = sub.add_parser("audition", help="Render dialogue-only key audition clips + reel with Scribe QA.")
    p_aud.add_argument("--registry", required=True)
    p_aud.add_argument("--cue-sheet", required=True)
    p_aud.add_argument("--output-dir", required=True)
    p_aud.add_argument("--cache-dir", default="")
    p_aud.add_argument("--ledger", default="")
    p_aud.add_argument("--skip-asr-qa", action="store_true")
    p_aud.set_defaults(func=cmd_audition)

    p_ren = sub.add_parser("render-episode", help="Synthesize stems, run QA, and master 3-bus episode.")
    p_ren.add_argument("--registry", required=True)
    p_ren.add_argument("--cue-sheet", required=True)
    p_ren.add_argument("--output-dir", required=True)
    p_ren.add_argument("--motifs-dir", default="", help="Dedicated folder to persist reusable sonic_motifs WAVs.")
    p_ren.add_argument("--cache-dir", default="")
    p_ren.add_argument("--ledger", default="")
    p_ren.add_argument("--workers", type=int, default=4, help="Concurrent synthesis/conditioning worker threads.")
    p_ren.add_argument("--clean-work-dir", action="store_true", help="Remove temporary _stems_work folder after mastering.")
    p_ren.add_argument("--skip-asr-qa", action="store_true")
    p_ren.add_argument("--strict-qa", action="store_true", help="Abort immediately if a line fails QA twice.")
    p_ren.set_defaults(func=cmd_render_episode)

    p_md = sub.add_parser("export-markdown", help="Export EpisodeCueSheet JSON into a readable Markdown script.")
    p_md.add_argument("--cue-sheet", required=True)
    p_md.add_argument("--output", required=True)
    p_md.add_argument("--registry", default="")
    p_md.set_defaults(func=cmd_export_markdown)

    p_ana = sub.add_parser("analyze-chapter", help="Analyze novel chapter dialogue & speaker distribution.")
    p_ana.add_argument("--chapter", required=True)
    p_ana.add_argument("--registry", default="")
    p_ana.set_defaults(func=cmd_analyze_chapter)
    p_ana.add_argument("--include-segments", action="store_true")

    p_dry = sub.add_parser("synth-dry-test", help="Verify timeline & 3-bus ducking mixer offline with synthetic audio.")
    p_dry.add_argument("--cue-sheet", required=True)
    p_dry.add_argument("--output-dir", required=True)
    p_dry.add_argument("--registry", default="")
    p_dry.set_defaults(func=cmd_synth_dry_test)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

