from array import array
import json
from pathlib import Path
import subprocess
import unittest
import wave

from aigc_audio_pipeline.adapter import analyze_markdown_chapter, export_cue_sheet_markdown
from aigc_audio_pipeline.mixer import apply_bgm_ducking_envelope, master_episode_three_bus
from aigc_audio_pipeline.models import (
    ActMusicSpec,
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    VoiceProfile,
    next_append_only_path,
    simplify_inline_tags,
    validate_v3_dialogue_text,
)
from aigc_audio_pipeline.qa import evaluate_dialogue_qa


class AudioPipelineTests(unittest.TestCase):
    def test_v3_hard_rules_validation(self) -> None:
        # Valid creative line with inline English tags
        errs = validate_v3_dialogue_text(
            "[dramatically] 陆烬骤然睁开双眼—— [shouting] 给我破！",
            stability=0.0,
        )
        self.assertEqual(errs, [])

        # Non-discrete stability (0.35) must be rejected per Playbook
        errs_stab = validate_v3_dialogue_text("今日两清。", stability=0.35)
        self.assertTrue(any("discrete values" in e for e in errs_stab))

        # SSML must be rejected on eleven_v3
        errs_ssml = validate_v3_dialogue_text('今日<break time="0.5s"/>两清。', stability=0.5)
        self.assertTrue(any("SSML" in e for e in errs_ssml))

        # Chinese inside square brackets should be rejected (would be read or confuse tagger)
        errs_zh_tag = validate_v3_dialogue_text("[愤怒大喊] 今日两清！", stability=0.0)
        self.assertTrue(any("lowercase English" in e for e in errs_zh_tag))

    def test_simplify_inline_tags_for_single_retry(self) -> None:
        simplified = simplify_inline_tags("[dramatically] 沈渊一口心头血—— [shouting] 轰然开启！")
        self.assertEqual(simplified, "[dramatic tone] 沈渊一口心头血—— 轰然开启！")

    def test_asr_qa_detects_tag_leak_and_tail_truncation(self) -> None:
        # Clean transcript passes
        ok = evaluate_dialogue_qa(
            tagged_prompt="[coldly] 拿去便是，自此两不相干。",
            asr_text="拿去便是，自此两不相干。",
            duration_s=2.8,
            peak_dbfs=-9.5,
        )
        self.assertTrue(ok.passed)

        # Leaked tag word 'coldly' fails
        leaked = evaluate_dialogue_qa(
            tagged_prompt="[coldly] 拿去便是，自此两不相干。",
            asr_text="coldly 拿去便是，自此两不相干。",
            duration_s=3.1,
            peak_dbfs=-9.5,
        )
        self.assertFalse(leaked.passed)
        self.assertIn("coldly", leaked.leaked_tags)

        # Truncated ending fails
        truncated = evaluate_dialogue_qa(
            tagged_prompt="[shouting] 用我十年阳寿，换你一缕斩铁剑意！",
            asr_text="用我十年阳寿",
            duration_s=1.2,
            peak_dbfs=-10.0,
        )
        self.assertFalse(truncated.passed)

    def test_bgm_ducking_curve_preserves_speech_ratio(self) -> None:
        # 4 seconds of constant amplitude 10000 stereo 48kHz samples
        bgm = array("h", [10000]) * (4 * 48000 * 2)
        ducked = apply_bgm_ducking_envelope(
            bgm,
            speech_intervals=[(1.0, 2.0)],
            gain_speech=0.11,
            gain_gap=0.34,
        )
        # At t=0.2s (pure gap): ~3400; at t=1.5s (mid-speech): ~1100; at t=3.5s (gap): ~3400
        self.assertAlmostEqual(ducked[int(0.2 * 48000) * 2], 3400, delta=60)
        self.assertAlmostEqual(ducked[int(1.5 * 48000) * 2], 1100, delta=60)
        self.assertAlmostEqual(ducked[int(3.5 * 48000) * 2], 3400, delta=60)

    def test_three_bus_master_and_append_only_versioning(self) -> None:
        tmp = Path("/tmp/test_aigc_audio_pipeline_unit")
        if tmp.exists():
            subprocess.run(["rm", "-rf", str(tmp)], check=True)
        tmp.mkdir(parents=True)

        p1 = next_append_only_path(tmp, "ep01_master", ".wav")
        p1.write_bytes(b"stub")
        p2 = next_append_only_path(tmp, "ep01_master", ".wav")
        self.assertEqual(p1.name, "ep01_master_v001.wav")
        self.assertEqual(p2.name, "ep01_master_v002.wav")

        # Synthesize 1 dialogue clip, 1 foreground SFX clip, and 1 BGM clip
        d_wav = tmp / "d1.wav"
        s_wav = tmp / "s1.wav"
        b_wav = tmp / "bgm1.wav"
        for out, freq, dur in [(d_wav, 220, 1.6), (s_wav, 660, 1.0), (b_wav, 110, 6.0)]:
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
                    f"sine=frequency={freq}:duration={dur}:sample_rate=48000",
                    "-af",
                    "pan=stereo|c0=c0|c1=c0,volume=6dB",
                    "-c:a",
                    "pcm_s16le",
                    str(out),
                ],
                check=True,
            )

        sheet = EpisodeCueSheet(
            episode_id="TEST_E01",
            chapter_number=1,
            title="单元测试集",
            head_pad_s=0.3,
            tail_pad_s=1.2,
            acts=[ActMusicSpec(act_id="act1", title="第一幕", bgm_prompt="test instrumental", bgm_duration_s=6.0)],
            cues=[
                TimelineCue(cue_id="c1", act_id="act1", kind="sfx", sfx_prompt="door knock", duration_seconds=1.0, gap_after_s=0.2),
                TimelineCue(cue_id="c2", act_id="act1", kind="dialogue", role_id="lu_jin", text="[coldly] 去开门罢。", stability=0.0, gap_after_s=0.4),
            ],
        )
        res = master_episode_three_bus(
            cue_sheet=sheet,
            cue_audio_map={"c1": s_wav, "c2": d_wav},
            act_bgm_map={"act1": b_wav},
            output_dir=tmp / "renders",
        )
        self.assertTrue(res["master_wav"].is_file())
        self.assertTrue(res["master_mp3"].is_file())
        self.assertTrue(res["subtitles_srt"].is_file())
        # Expected natural duration: 0.3 + 1.0 + 0.2 + 1.6 + 0.4 + 1.2 = 4.7s
        self.assertAlmostEqual(res["total_duration_s"], 4.7, delta=0.08)

        # Verify SFX bus was NOT ducked (peak amplitude intact)
        manifest = json.loads(res["manifest_json"].read_text(encoding="utf-8"))
        sfx_bus_path = Path(manifest["buses"]["sfx_foreground_bus"])
        with wave.open(str(sfx_bus_path), "rb") as wf:
            sfx_samples = array("h")
            sfx_samples.frombytes(wf.readframes(wf.getnframes()))
        self.assertGreater(max(sfx_samples), 6000)

    def test_chapter_analyzer_and_markdown_export(self) -> None:
        reg = VoiceCastingRegistry(
            project_id="zhujie",
            project_title="诸界锁仙",
            roles={
                "narrator": VoiceProfile(role_id="narrator", display_name="旁白"),
                "fu_bo": VoiceProfile(role_id="fu_bo", display_name="福伯", aliases=["陆忠"]),
            },
        )
        sample_md = "# 第1章 测试\n\n福伯端着陶碗走进堂内，低声道：“少主，趁热喝口灵米粥罢。”\n"
        report = analyze_markdown_chapter(sample_md, registry=reg)
        segs = report["segments"]
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0].text, "福伯端着陶碗走进堂内")  # stripped redundant '低声道：'
        self.assertEqual(segs[1].speaker_hint, "fu_bo")

        sheet = EpisodeCueSheet(
            episode_id="E001",
            chapter_number=1,
            title="测试",
            cues=[TimelineCue(cue_id="c1", act_id="", kind="dialogue", role_id="fu_bo", text="[softly] 少主，趁热喝口灵米粥罢。", stability=0.5)],
        )
        md_out = export_cue_sheet_markdown(sheet, registry=reg)
        self.assertIn("福伯 (`fu_bo`)", md_out)

    def test_voice_design_and_shared_voice_mainland_filter(self) -> None:
        from aigc_audio_pipeline.elevenlabs_client import (
            filter_mainland_mandarin_voices,
            normalize_shared_voice_locale,
            validate_voice_design_inputs,
        )

        self.assertEqual(normalize_shared_voice_locale("zh-CN"), "cmn-CN")
        self.assertEqual(normalize_shared_voice_locale("cmn-CN"), "cmn-CN")

        raw_shared = [
            {
                "voice_id": "v_british_leak",
                "name": "Older Joe",
                "accent": "british",
                "locale": "cmn-CN",
                "description": "A friendly, polished older British narrator",
            },
            {
                "voice_id": "v_tw",
                "name": "Taipei Girl",
                "accent": "taiwan mandarin",
                "locale": "cmn-TW",
                "description": "Sweet voice",
            },
            {
                "voice_id": "v_cn_good",
                "name": "Alvinluo",
                "accent": "beijing mandarin",
                "locale": "cmn-CN",
                "description": "Warm standard Mainland Chinese dramatic actor",
            },
        ]
        filtered = filter_mainland_mandarin_voices(raw_shared)
        self.assertEqual([v["voice_id"] for v in filtered], ["v_cn_good"])

        # Voice design sample text < 100 chars must fail validation
        errs_short = validate_voice_design_inputs(
            "一位六十五岁的中国北方老管家，纯正标准中国大陆普通话，嗓音苍老沙哑。",
            "太短的试听文本。",
        )
        self.assertTrue(any("100..1000" in e for e in errs_short))
        errs_ok = validate_voice_design_inputs(
            "一位六十五岁的中国北方老管家，纯正标准中国大陆普通话，嗓音苍老沙哑。",
            "少主撑住！外头秋雨寒重，您丹田刚受了反噬，老奴这就去西街敲李郎中的门，绝不叫少主死在这儿！" * 3,
        )
        self.assertEqual(errs_ok, [])

        # Arabic numeral in ASR ('50') should match Chinese numeral ('五十') cleanly
        num_qa = evaluate_dialogue_qa(
            tagged_prompt="[coldly] 这五十枚灵石拿去便是。",
            asr_text="这50枚灵石拿去便是。",
            duration_s=2.4,
            peak_dbfs=-10.0,
        )
        self.assertTrue(num_qa.passed)

    def test_tts_text_polyphone_and_srt_chinese_speaker_label(self) -> None:
        # Polyphone override: tts_text uses homophone '真船' (chuán), canonical text keeps '真传'
        poly_qa = evaluate_dialogue_qa(
            tagged_prompt="[gasps] [hoarsely] 裴真船……好威风。",
            canonical_prompt="[gasps] [hoarsely] 裴真传……好威风。",
            asr_text="裴真传，好威风。",
            duration_s=2.1,
            peak_dbfs=-9.8,
        )
        self.assertTrue(poly_qa.passed)
        self.assertEqual(poly_qa.expected_spoken, "裴真传……好威风。")
        self.assertEqual(poly_qa.char_recall, 1.0)

        # SRT subtitle should display 【陆烬】 instead of 【lu_jin】 and preserve canonical '真传'
        tmp = Path("/tmp/test_aigc_audio_srt_label")
        if tmp.exists():
            subprocess.run(["rm", "-rf", str(tmp)], check=True)
        tmp.mkdir(parents=True)

        d_wav = tmp / "d1.wav"
        b_wav = tmp / "bgm1.wav"
        for out, freq, dur in [(d_wav, 220, 1.5), (b_wav, 110, 5.0)]:
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
                    f"sine=frequency={freq}:duration={dur}:sample_rate=48000",
                    "-af",
                    "pan=stereo|c0=c0|c1=c0,volume=6dB",
                    "-c:a",
                    "pcm_s16le",
                    str(out),
                ],
                check=True,
            )

        reg = VoiceCastingRegistry(
            project_id="zhujie",
            project_title="诸界锁仙",
            roles={"lu_jin": VoiceProfile(role_id="lu_jin", display_name="陆烬", voice_id="v_lujin", status="locked")},
        )
        sheet = EpisodeCueSheet(
            episode_id="TEST_SRT",
            chapter_number=1,
            title="多音字字幕测试",
            acts=[ActMusicSpec(act_id="act1", title="第一幕", bgm_prompt="test", bgm_duration_s=5.0)],
            cues=[
                TimelineCue(
                    cue_id="c1",
                    act_id="act1",
                    kind="dialogue",
                    role_id="lu_jin",
                    text="[gasps] [hoarsely] 裴真传……好威风。",
                    tts_text="[gasps] [hoarsely] 裴真船……好威风。",
                    stability=0.0,
                )
            ],
        )
        self.assertEqual(sheet.validate(registry=reg, require_locked_voices=True), [])
        res = master_episode_three_bus(
            cue_sheet=sheet,
            cue_audio_map={"c1": d_wav},
            act_bgm_map={"act1": b_wav},
            output_dir=tmp / "renders",
            registry=reg,
        )
        srt_text = res["subtitles_srt"].read_text(encoding="utf-8")
        self.assertIn("【陆烬】裴真传……好威风。", srt_text)
        self.assertNotIn("真船", srt_text)
        self.assertNotIn("lu_jin", srt_text)

    def test_polyphones_and_inline_scare_quotes(self) -> None:
        from aigc_audio_pipeline.polyphones import apply_xianxia_polyphone_overrides, compute_tts_text_override

        raw = "[dramatically] 祠堂内，裴真传翻阅九月廿三与九月卅日的参汤卷宗。"
        over = apply_xianxia_polyphone_overrides(raw)
        self.assertEqual(over, "[dramatically] 磁堂内，裴真船翻阅九月念三与九月萨日的深汤卷宗。")
        self.assertEqual(compute_tts_text_override("风雪漫过北渊城。"), "")

        md = (
            "# 第3章 测试\n\n"
            "那凶兽体内的精血，岂不正是冲开体内“血锁”最好的大药！\n\n"
            "纸鹤并未设下“人死即燃”的魂血禁制。\n\n"
            "陆烬低声道：“先试试边界在哪。”\n"
        )
        reg = VoiceCastingRegistry(
            project_id="zhujie",
            project_title="诸界锁仙",
            roles={"lu_jin": VoiceProfile(role_id="lu_jin", display_name="陆烬")},
        )
        rep = analyze_markdown_chapter(md, registry=reg)
        segs = rep["segments"]
        self.assertEqual(len(segs), 3)
        self.assertEqual(segs[0].kind, "narration")
        self.assertIn("“血锁”", segs[0].text)
        self.assertEqual(segs[1].kind, "narration")
        self.assertIn("“人死即燃”", segs[1].text)
        self.assertEqual(segs[2].kind, "dialogue")
        self.assertEqual(segs[2].speaker_hint, "lu_jin")


if __name__ == "__main__":
    unittest.main()


