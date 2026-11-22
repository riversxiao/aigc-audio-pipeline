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

        # Acoustic ASR homophone at sentence end ('异变骤生' -> '一遍咒声') passes when full syllable count matches
        homophone_tail = evaluate_dialogue_qa(
            tagged_prompt="当陆烬右脚踏在第九十九丈的冻土边缘，试探着伸出右手食指触碰面前翻涌的灰雾时，异变骤生。",
            asr_text="当路径右脚踏在第九十九丈的冻土边缘，试探着伸出右手食指触碰面前翻涌的灰雾时，一遍咒声。",
            duration_s=9.2,
            peak_dbfs=-11.0,
        )
        self.assertTrue(homophone_tail.passed)

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

    def test_unabridged_episode_compiler_and_banker_numerals(self) -> None:
        from aigc_audio_pipeline.compiler import compile_episode_cue_sheet, save_episode_scripts

        tmp = Path("/tmp/test_aigc_audio_compiler")
        if tmp.exists():
            subprocess.run(["rm", "-rf", str(tmp)], check=True)
        tmp.mkdir(parents=True)

        md_file = tmp / "第05章_古骸兽皮卷，莫信头顶月.md"
        md_file.write_text(
            "# 第5章 古骸兽皮卷，莫信头顶月\n\n"
            "夜风呼啸的死寂荒原上，陆烬借着残破石碑投下的幽冷微光，缓缓翻开那卷所谓的“牧场血账”，"
            "只见泛黄兽皮第一行赫然用暗红血迹写着第柒拾叁号血引已于北渊城再度降临，字字透着刺骨凉意。\n\n"
            "下一瞬，他丹田废墟深处引气三重的灵力如惊雷般轰然冲破青铜锁扣，掌中玄铁断刀寒意森然，将漫天煞气尽数斩碎。\n\n"
            "陆烬低声道：“九月廿三，原来当年的真相竟藏在这里。”\n",
            encoding="utf-8",
        )
        reg = VoiceCastingRegistry(
            project_id="zhujie",
            project_title="诸界锁仙",
            roles={
                "narrator": VoiceProfile(role_id="narrator", display_name="旁白", voice_id="v_nar", status="locked"),
                "lu_jin": VoiceProfile(role_id="lu_jin", display_name="陆烬", voice_id="v_lu", status="locked"),
            },
        )
        sheet = compile_episode_cue_sheet(
            episode_id="E005",
            chapter_number=5,
            source_md_path=md_file,
            source_rel_path="02_分章精修正文/第05章.md",
            registry=reg,
            acts_blueprint=[
                {"act_id": "act1", "start_p": 1, "title": "第一幕", "bgm_prompt": "dark guqin instrumental", "bgm_duration_s": 60.0}
            ],
            dialogue_specs=[
                {"role_id": "lu_jin", "tags": "[coldly]", "stability": 0.0, "match": "九月廿三"}
            ],
            sfx_blueprint=[
                {"p": 2, "pos": "before", "slug": "blade", "sfx_prompt": "cold iron blade hum", "duration_seconds": 2.0}
            ],
            acoustic_ranges=[(1, 2, "mental_realm")],
        )
        self.assertEqual(len(sheet.cues), 4)  # nar p1 + sfx + nar p2 + dialogue p3
        self.assertIn("第七十三号", sheet.cues[0].tts_text)
        self.assertIn("再度酱临", sheet.cues[0].tts_text)
        self.assertEqual(sheet.cues[0].acoustic_space, "mental_realm")
        self.assertEqual(sheet.cues[2].stability, 0.0)
        self.assertIn("[dramatically]", sheet.cues[2].text)
        self.assertIn("引气三崇", sheet.cues[2].tts_text)
        self.assertIn("九月念三", sheet.cues[3].tts_text)

        jp, mp = save_episode_scripts(sheet, tmp / "scripts", reg)
        self.assertTrue(jp.is_file())
        self.assertTrue(mp.is_file())

    def test_batch_queue_ebur128_and_cli_extract_quotes(self) -> None:
        from aigc_audio_pipeline.batch_queue import canonical_episode_stem, measure_ebur128
        from aigc_audio_pipeline.cli import main as cli_main

        self.assertEqual(
            canonical_episode_stem("E006", "第6章 鬼樊楼试水，瞎眼鉴药人"),
            "E006_第06章_鬼樊楼试水瞎眼鉴药人_电影感多人有声剧",
        )

        tmp = Path("/tmp/test_aigc_audio_ebur128")
        tmp.mkdir(parents=True, exist_ok=True)
        wav = tmp / "tone.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=2.0:sample_rate=48000",
                "-af", "volume=-16dB", "-ac", "2", "-c:a", "pcm_s16le", str(wav),
            ],
            check=True,
        )
        lufs, tp = measure_ebur128(wav)
        self.assertLess(lufs, -10.0)
        self.assertLess(tp, 0.0)

        md = tmp / "ch.md"
        md.write_text("# 第1章 试音\n\n福伯道：“少主小心！”\n", encoding="utf-8")
        self.assertEqual(cli_main(["extract-quotes", "--chapter", str(md)]), 0)

    def test_drama3_adapter_and_bundle_export(self) -> None:
        from array import array
        import wave
        from aigc_audio_pipeline.cli import main as cli_main
        from aigc_audio_pipeline.drama3_adapter import (
            export_colab_96gb_bundle,
            strip_drama3_markup,
            translate_cue_to_drama3_input,
            trim_edge_silence_wav,
        )

        pei_profile = VoiceProfile(
            role_id="pei_xuandu",
            display_name="裴玄度",
            tier="antagonist",
            voice_id="v_pei",
            status="locked",
        )
        cue = TimelineCue(
            cue_id="c_pei",
            act_id="act1",
            kind="dialogue",
            role_id="pei_xuandu",
            text="[dismissive] [laughs] 引气三重也敢妄言？ [whispers] 裴真传替你留条残命。",
            stability=0.0,
        )
        d3_a1 = translate_cue_to_drama3_input(cue, pei_profile, attempt=1, use_phoneme_pins=False)
        self.assertIn("[aloof, aristocratic disdain]", d3_a1)
        self.assertIn("[cold laugh]", d3_a1)
        self.assertIn("引气三崇", d3_a1)
        self.assertIn("<whisper>裴真船替你留条残命。</whisper>", d3_a1)
        self.assertEqual(strip_drama3_markup(d3_a1), "引气三崇也敢妄言？ 裴真船替你留条残命。")

        d3_pins = translate_cue_to_drama3_input(cue, pei_profile, attempt=1, use_phoneme_pins=True)
        self.assertIn("<|phoneme_start|>yin3 qi4 san1 chong2<|phoneme_end|>", d3_pins)
        self.assertIn("<|phoneme_start|>zhen1 chuan2<|phoneme_end|>", d3_pins)

        d3_a2 = translate_cue_to_drama3_input(cue, pei_profile, attempt=2)
        self.assertNotIn("<whisper>", d3_a2)
        self.assertTrue(d3_a2.startswith("[aloof, aristocratic disdain]"))

        d3_a3 = translate_cue_to_drama3_input(cue, pei_profile, attempt=3)
        self.assertNotIn("[", d3_a3)
        self.assertEqual(d3_a3, "引气三崇也敢妄言？ 裴真船替你留条残命。")

        # Verify edge silence trimmer trims outer dead air while keeping active center intact
        tmp = Path("/tmp/test_drama3_bundle")
        if tmp.exists():
            subprocess.run(["rm", "-rf", str(tmp)], check=True)
        tmp.mkdir(parents=True)

        padded_wav = tmp / "padded.wav"
        sr = 48000
        # 0.4s silence + 0.6s 440Hz tone + 0.8s trailing silence = 1.8s total
        samples = array("h", [0] * int(0.4 * sr))
        for i in range(int(0.6 * sr)):
            samples.append(int(12000 * __import__("math").sin(2.0 * 3.14159265 * 440.0 * i / sr)))
        samples.extend([0] * int(0.8 * sr))
        with wave.open(str(padded_wav), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(samples.tobytes())

        trimmed_dur = trim_edge_silence_wav(padded_wav)
        self.assertGreater(trimmed_dur, 0.65)
        self.assertLess(trimmed_dur, 0.85)

        # Verify export_colab_96gb_bundle + preview-drama3 CLI
        reg_path = tmp / "reg.json"
        reg = VoiceCastingRegistry(
            project_id="test_proj",
            project_title="测试工程",
            roles={"pei_xuandu": pei_profile},
        )
        reg.save(reg_path)

        cs_dir = tmp / "cs"
        cs_dir.mkdir()
        sheet = EpisodeCueSheet(
            episode_id="E001",
            chapter_number=1,
            title="第一集",
            acts=[ActMusicSpec(act_id="act1", title="幕一", bgm_prompt="dark ost")],
            cues=[cue],
        )
        cs_file = cs_dir / "E001_第一集.json"
        sheet.save(cs_file)

        self.assertEqual(
            cli_main(["preview-drama3", "--cue-sheet", str(cs_file), "--registry", str(reg_path)]),
            0,
        )
        bundle_info = export_colab_96gb_bundle(
            registry_path=reg_path,
            cue_sheets_dir=cs_dir,
            anchor_specs={"pei_xuandu": {"audio_path": str(padded_wav), "anchor_text": "裴玄度参考干音"}},
            output_bundle_dir=tmp / "bundle_out",
            zip_output_path=tmp / "bundle_out.zip",
        )
        self.assertEqual(bundle_info["role_count"], 1)
        self.assertEqual(bundle_info["episode_count"], 1)
        self.assertTrue((tmp / "bundle_out" / "voice_anchors" / "pei_xuandu.wav").is_file())
        self.assertTrue((tmp / "bundle_out.zip").is_file())

    def test_colab_agent_bridge_endpoints(self) -> None:
        import base64
        from http.server import ThreadingHTTPServer
        import importlib.util
        import json
        import threading
        import time
        import urllib.error
        import urllib.request

        bridge_py = Path(__file__).resolve().parents[1] / "colab_96gb" / "colab_agent_bridge.py"
        spec = importlib.util.spec_from_file_location("colab_agent_bridge", bridge_py)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        tmp = Path("/tmp/test_colab_agent_bridge")
        tmp.mkdir(parents=True, exist_ok=True)
        reg = mod.JobRegistry(tmp / "jobs")
        token = "test_secret_token_12345"
        srv = ThreadingHTTPServer(("127.0.0.1", 0), mod.build_handler_class(token, reg))
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            # 1. Unauthorized check
            req_unauth = urllib.request.Request(f"http://127.0.0.1:{port}/health")
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(req_unauth, timeout=5)
            self.assertEqual(ctx.exception.code, 401)

            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            # 2. Health check
            req_h = urllib.request.Request(f"http://127.0.0.1:{port}/health", headers=headers)
            health = json.loads(urllib.request.urlopen(req_h, timeout=5).read().decode("utf-8"))
            self.assertTrue(health["ok"])

            # 3. Upload & download round-trip
            target_file = tmp / "sample_payload.txt"
            up_body = json.dumps(
                {
                    "path": str(target_file),
                    "content_b64": base64.b64encode("诸界锁仙".encode("utf-8")).decode("ascii"),
                }
            ).encode("utf-8")
            req_up = urllib.request.Request(f"http://127.0.0.1:{port}/upload_file", data=up_body, headers=headers, method="POST")
            up_res = json.loads(urllib.request.urlopen(req_up, timeout=5).read().decode("utf-8"))
            self.assertTrue(up_res["ok"])

            req_dl = urllib.request.Request(f"http://127.0.0.1:{port}/download_file?path={target_file}", headers=headers)
            dl_bytes = urllib.request.urlopen(req_dl, timeout=5).read()
            self.assertEqual(dl_bytes.decode("utf-8"), "诸界锁仙")

            # 4. Async background job start & incremental log poll
            job_body = json.dumps(
                {
                    "job_id": "unit_job",
                    "cmd": ["python3", "-c", "print('hello_drama3', flush=True)"],
                    "cwd": str(tmp),
                }
            ).encode("utf-8")
            req_js = urllib.request.Request(f"http://127.0.0.1:{port}/jobs/start", data=job_body, headers=headers, method="POST")
            js_res = json.loads(urllib.request.urlopen(req_js, timeout=5).read().decode("utf-8"))
            self.assertTrue(js_res["ok"])

            for _ in range(20):
                req_st = urllib.request.Request(f"http://127.0.0.1:{port}/jobs/status?job_id=unit_job&offset=0", headers=headers)
                st_res = json.loads(urllib.request.urlopen(req_st, timeout=5).read().decode("utf-8"))
                if not st_res["running"]:
                    break
                time.sleep(0.1)
            self.assertEqual(st_res["returncode"], 0)
            self.assertIn("hello_drama3", st_res["log_chunk"])
        finally:
            srv.shutdown()
            srv.server_close()

    def test_moss_foley_and_acestep_bgm_guardrails(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "run_zhujie_96gb_studio",
            Path(__file__).resolve().parents[1] / "colab_96gb" / "run_zhujie_96gb_studio.py",
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        foley = mod.sanitize_moss_foley_prompt(
            "Wooden clogs stepping carefully through shallow courtyard puddles accompanied by an old man's muffled suppressed cough under a rainy corridor"
        )
        self.assertNotIn("cough", foley.lower())
        self.assertIn("no human voice", foley.lower())

        bgm_chamber = mod.enrich_acestep_bgm_prompt(
            "Melancholic ancient Chinese xianxia soundtrack, sparse guqin plucks and lone xiao flute"
        )
        self.assertIn("no drums", bgm_chamber.lower())
        self.assertIn("no singing", bgm_chamber.lower())

        bgm_war = mod.enrich_acestep_bgm_prompt(
            "Epic ancient Chinese xianxia battle score with heavy taiko war drums and fast pipa"
        )
        self.assertNotIn("no drums", bgm_war.lower())
        self.assertIn("no singing", bgm_war.lower())

    def test_drama3_sentence_chunking_and_surgical_v002_recovery(self) -> None:
        from aigc_audio_pipeline.drama3_adapter import concat_pcm_wavs, split_cue_into_subcues_for_drama3
        from aigc_audio_pipeline.mixer import (
            _read_stereo_s16,
            condition_dialogue_clip,
            master_episode_three_bus,
            recover_intact_dialogue_from_master,
        )
        from aigc_audio_pipeline.models import extract_tags_and_spoken_text

        # 1. Verify natural sentence chunking on a 220+ CJK-char narrator cue (like E009 c006_nar_p006)
        long_text = (
            "[tense] 血月悬于北渊城残破的飞檐之上，暗红色的月华犹如粘稠血浆般浸透青石院落。"
            "陆烬反手握紧掌中那柄豁口斑驳的玄铁断刀，丹田废墟深处第一阶基因锁轰然震鸣，周身气血瞬间暴涨三倍不止！"
            "祠堂阴影里，厉苍枯瘦的五指如铁钩般撕裂寒雾，九月廿三遗留的杀机彻底爆发，爪尖距离陆烬咽喉已不足三寸！"
            "千钧一发之际，识海古棺轻轻一震，将那股侵蚀神魂的威压硬生生迟滞了三成！"
        )
        long_cue = TimelineCue(
            cue_id="c006_nar_p006",
            act_id="act1",
            kind="dialogue",
            role_id="narrator",
            text=long_text,
            stability=0.5,
            gap_after_s=0.45,
        )
        subcues = split_cue_into_subcues_for_drama3(long_cue, max_cjk_chars=105)
        self.assertGreaterEqual(len(subcues), 2)
        for idx, sc in enumerate(subcues):
            _, sc_spoken = extract_tags_and_spoken_text(sc.text)
            self.assertLessEqual(len([ch for ch in sc_spoken if "\u4e00" <= ch <= "\u9fff"]), 115)
            self.assertTrue(sc.text.startswith("[tense]"))
            if idx < len(subcues) - 1:
                self.assertAlmostEqual(sc.gap_after_s, 0.16, places=2)
            else:
                self.assertAlmostEqual(sc.gap_after_s, 0.45, places=2)
        # Polyphone overrides ('祠堂' -> '磁堂', '廿三' -> '念三') preserved on subcues
        joined_tts = "".join(sc.tts_text or sc.text for sc in subcues)
        self.assertIn("磁堂", joined_tts)
        self.assertIn("念三", joined_tts)

        # 2. Verify bit-exact recovery of intact dialogue from v001 master + surgical v002 remaster
        tmp = Path("/tmp/test_aigc_surgical_recovery")
        if tmp.exists():
            subprocess.run(["rm", "-rf", str(tmp)], check=True)
        tmp.mkdir(parents=True)

        def _make_wav(path: Path, freq: float, dur: float, vol_db: float = -12.0) -> Path:
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
                    f"pan=stereo|c0=c0|c1=c0,volume={vol_db}dB",
                    "-c:a",
                    "pcm_s16le",
                    str(path),
                ],
                check=True,
            )
            return path

        d1_wav = _make_wav(tmp / "d1.wav", 220.0, 1.8)
        d2_trunc_wav = _make_wav(tmp / "d2_trunc.wav", 185.0, 2.0)
        d2_part1 = _make_wav(tmp / "d2_p1.wav", 185.0, 1.7)
        d2_part2 = _make_wav(tmp / "d2_p2.wav", 195.0, 1.9)
        d2_repaired_wav = concat_pcm_wavs([d2_part1, d2_part2], tmp / "d2_repaired.wav", pause_ms=160.0)
        d3_wav = _make_wav(tmp / "d3.wav", 310.0, 1.6)
        sfx_wav = _make_wav(tmp / "sfx1.wav", 130.0, 1.2, vol_db=-16.0)
        bgm1_wav = _make_wav(tmp / "bgm1.wav", 98.0, 8.0, vol_db=-14.0)
        bgm2_wav = _make_wav(tmp / "bgm2.wav", 110.0, 8.0, vol_db=-14.0)

        reg = VoiceCastingRegistry(
            project_id="zhujie",
            project_title="诸界锁仙",
            roles={
                "narrator": VoiceProfile(role_id="narrator", display_name="旁白", voice_id="v_nar", status="locked"),
                "lu_jin": VoiceProfile(role_id="lu_jin", display_name="陆烬", voice_id="v_lu", status="locked"),
            },
        )
        sheet = EpisodeCueSheet(
            episode_id="E009",
            chapter_number=9,
            title="第9章 血月之下",
            acts=[
                ActMusicSpec(act_id="act1", title="第一幕", bgm_prompt="dark guqin", bgm_duration_s=8.0),
                ActMusicSpec(act_id="act2", title="第二幕", bgm_prompt="tense pipa", bgm_duration_s=8.0),
            ],
            cues=[
                TimelineCue(cue_id="c1_keep", act_id="act1", kind="dialogue", role_id="lu_jin", text="先看清他的破绽！", gap_after_s=0.35),
                TimelineCue(cue_id="s1_fx", act_id="act1", kind="sfx", sfx_prompt="blade clash", duration_seconds=1.2, placement="overlay_next", gap_after_s=0.25),
                TimelineCue(cue_id="c2_trunc", act_id="act1", kind="dialogue", role_id="narrator", text=long_text, gap_after_s=0.40),
                TimelineCue(cue_id="c3_keep", act_id="act2", kind="dialogue", role_id="lu_jin", text="就是现在，断刀斩！", gap_after_s=0.35),
            ],
        )

        out_dir = tmp / "masters"
        v1 = master_episode_three_bus(
            cue_sheet=sheet,
            cue_audio_map={"c1_keep": d1_wav, "s1_fx": sfx_wav, "c2_trunc": d2_trunc_wav, "c3_keep": d3_wav},
            act_bgm_map={"act1": bgm1_wav, "act2": bgm2_wav},
            output_dir=out_dir,
            registry=reg,
            stem_prefix="E009_Drama3",
        )
        self.assertTrue(str(v1["master_wav"]).endswith("_v001.wav"))

        # Ground-truth conditioned samples for c1_keep & c3_keep
        gt_c1 = _read_stereo_s16(condition_dialogue_clip(d1_wav, tmp / "gt_c1.wav"))
        gt_c3 = _read_stereo_s16(condition_dialogue_clip(d3_wav, tmp / "gt_c3.wav"))

        rec_samples, rec_meta = recover_intact_dialogue_from_master(
            cue_sheet=sheet,
            v001_wav_path=v1["master_wav"],
            v001_manifest_path=v1["manifest_json"],
            sfx_audio_map={"s1_fx": sfx_wav},
            act_bgm_map={"act1": bgm1_wav, "act2": bgm2_wav},
            keep_cue_ids={"c1_keep", "c3_keep"},
        )
        self.assertEqual(set(rec_samples.keys()), {"c1_keep", "c3_keep"})
        self.assertTrue(rec_meta["c1_keep"]["recovered_from_v001"])

        # Verify near-zero (< 2 LSB out of 32767) sample reconstruction across BOTH acts!
        for gt, rec in ((gt_c1, rec_samples["c1_keep"]), (gt_c3, rec_samples["c3_keep"])):
            n = min(len(gt), len(rec))
            self.assertGreater(n, 48000)
            max_err = max(abs(gt[i] - rec[i]) for i in range(n))
            self.assertLessEqual(max_err, 2)

        # Remaster v002 substituting ONLY c2_trunc -> d2_repaired_wav
        v2 = master_episode_three_bus(
            cue_sheet=sheet,
            cue_audio_map={"s1_fx": sfx_wav, "c2_trunc": d2_repaired_wav},
            act_bgm_map={"act1": bgm1_wav, "act2": bgm2_wav},
            output_dir=out_dir,
            preconditioned_samples=rec_samples,
            cue_meta_map=rec_meta,
            registry=reg,
            stem_prefix="E009_Drama3",
        )
        self.assertTrue(str(v2["master_wav"]).endswith("_v002.wav"))
        self.assertGreater(v2["total_duration_s"], v1["total_duration_s"] + 1.4)

    def test_bilingual_validation_finance_polyphones_and_english_qa(self) -> None:
        from aigc_audio_pipeline.polyphones import (
            apply_domain_polyphone_overrides,
            apply_finance_polyphone_overrides,
        )

        # Pure English valid under language_code='en', rejected under strict 'zh'
        en_line = "[wryly] In God we trust; all others pay cash."
        self.assertEqual(validate_v3_dialogue_text(en_line, stability=0.5, language_code="en"), [])
        self.assertTrue(len(validate_v3_dialogue_text(en_line, stability=0.5, language_code="zh")) > 0)

        # Bilingual code-switched Chinese line valid under 'zh-en'
        zhen_line = "[warmly] 巴菲特把这种退潮叫 swimming naked，也就是裸泳。"
        self.assertEqual(validate_v3_dialogue_text(zhen_line, stability=0.5, language_code="zh-en"), [])

        # Finance polyphones disambiguate without breaking '重仓'
        fin_raw = "在伯克希尔·哈撒韦的老行当里，重仓优质股比频繁调仓或盲目资产重组更重要。"
        fin_out = apply_finance_polyphone_overrides(fin_raw)
        self.assertIn("伯克希尔哈撒韦", fin_out)
        self.assertIn("老航当", fin_out)
        self.assertIn("条仓", fin_out)
        self.assertIn("资产崇组", fin_out)
        self.assertIn("重仓", fin_out)
        self.assertEqual(apply_domain_polyphone_overrides(fin_raw, domain="finance_podcast"), fin_out)

        # English ASR QA: intact passes, tail truncation fails, tag leak fails
        en_ok = evaluate_dialogue_qa(
            tagged_prompt="[wryly] Beware the investment activity that produces applause; the great moves are usually greeted by yawns.",
            asr_text="Beware the investment activity that produces applause, the great moves are usually greeted by yawns.",
            duration_s=6.2,
            peak_dbfs=-10.0,
        )
        self.assertTrue(en_ok.passed)
        self.assertGreaterEqual(en_ok.char_recall, 0.95)

        en_trunc = evaluate_dialogue_qa(
            tagged_prompt="[wryly] Beware the investment activity that produces applause; the great moves are usually greeted by yawns.",
            asr_text="Beware the investment activity that produces applause",
            duration_s=3.1,
            peak_dbfs=-10.0,
        )
        self.assertFalse(en_trunc.passed)

        en_leak = evaluate_dialogue_qa(
            tagged_prompt="[wryly] In God we trust; all others pay cash.",
            asr_text="wryly In God we trust, all others pay cash.",
            duration_s=3.4,
            peak_dbfs=-10.0,
        )
        self.assertFalse(en_leak.passed)
        self.assertIn("wryly", en_leak.leaked_tags)

        # Bilingual guest code-switching ('swimming naked', 'float') must NOT trigger false tag-leak failure
        bilingual_ok = evaluate_dialogue_qa(
            tagged_prompt="[warmly] 这就是他说的 swimming naked，靠保险 float 才能在危机里接金子。",
            asr_text="这就是他说的 swimming naked，靠保险 float 才能在危机里接金子。",
            duration_s=5.1,
            peak_dbfs=-10.5,
        )
        self.assertTrue(bilingual_ok.passed)
        self.assertEqual(bilingual_ok.leaked_tags, [])

    def test_drama3_podcast_buffett_translation_and_english_chunking(self) -> None:
        from aigc_audio_pipeline.drama3_adapter import (
            split_cue_into_subcues_for_drama3,
            translate_cue_to_drama3_input,
        )

        buffett_prof = VoiceProfile(
            role_id="buffett_prime_en",
            display_name="沃伦·巴菲特",
            language_code="en",
            voice_id="anchor_buffett",
            status="locked",
        )
        en_cue = TimelineCue(
            cue_id="c_buf",
            act_id="act1",
            kind="dialogue",
            role_id="buffett_prime_en",
            language_code="en",
            text=(
                "[folksy] By the fourth quarter, the credit crisis, coupled with tumbling home and stock prices, "
                "had produced a paralyzing fear that engulfed the country. "
                "A freefall in business activity ensued, accelerating at a pace that I have never before witnessed. "
                "The watchword throughout the country became the creed I saw on restaurant walls when I was young: "
                "In God we trust; all others pay cash."
            ),
            stability=0.5,
            gap_after_s=0.35,
        )
        d3_en = translate_cue_to_drama3_input(en_cue, buffett_prof, attempt=1, domain="finance_podcast")
        self.assertIn("Midwestern storyteller cadence", d3_en)
        self.assertIn("In God we trust; all others pay cash.", d3_en)

        subcues_en = split_cue_into_subcues_for_drama3(en_cue, max_en_words=35, domain="finance_podcast")
        self.assertGreaterEqual(len(subcues_en), 2)
        self.assertTrue(all(sc.language_code == "en" for sc in subcues_en))
        self.assertAlmostEqual(subcues_en[-1].gap_after_s, 0.35, places=2)

    def test_documentary_simultaneous_translation_ducking_and_bilingual_srt(self) -> None:
        from aigc_audio_pipeline.mixer import apply_voiceover_duck_envelope

        # 1. Verify envelope gain shape directly on constant 10,000 amplitude stereo signal (10.0s)
        en_raw = array("h", [10000]) * (10 * 48000 * 2)
        env_out = apply_voiceover_duck_envelope(
            en_raw,
            rel_duck_start_s=3.5,
            rel_duck_end_s=8.5,
            duck_gain=0.15,
        )
        # Solo lead-in at t=1.5s -> ~10000; ducked bed at t=5.5s -> ~1500; tail lift at t=9.4s -> ~7800
        self.assertAlmostEqual(env_out[int(1.5 * 48000) * 2], 10000, delta=60)
        self.assertAlmostEqual(env_out[int(5.5 * 48000) * 2], 1500, delta=80)
        self.assertAlmostEqual(env_out[int(9.4 * 48000) * 2], 7800, delta=120)

        # 2. Verify full 3-bus timeline overlap, non-collision with c3, and non-overlapping bilingual SRT
        tmp = Path("/tmp/test_aigc_simul_duck")
        if tmp.exists():
            subprocess.run(["rm", "-rf", str(tmp)], check=True)
        tmp.mkdir(parents=True)

        def _tone(p: Path, freq: float, dur: float) -> Path:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={dur}:sample_rate=48000",
                    "-af", "pan=stereo|c0=c0|c1=c0,volume=-12dB", "-c:a", "pcm_s16le", str(p),
                ],
                check=True,
            )
            return p

        en_wav = _tone(tmp / "en.wav", 190.0, 9.0)   # 9.0s English quote
        zh_wav = _tone(tmp / "zh.wav", 260.0, 5.5)   # 5.5s Chinese translation (starts +2.5s -> ends +8.0s < 9.0s!)
        c3_wav = _tone(tmp / "c3.wav", 310.0, 2.0)   # Next speaker must wait until max(9.0, 8.0) + gap!
        bgm_wav = _tone(tmp / "bgm.wav", 110.0, 14.0)

        reg = VoiceCastingRegistry(
            project_id="buffett_letters",
            project_title="穿越周期的信",
            domain="finance_podcast",
            roles={
                "buffett_prime_en": VoiceProfile(
                    role_id="buffett_prime_en", display_name="沃伦·巴菲特", language_code="en", voice_id="v_b", status="locked"
                ),
                "guest_huaiyuan": VoiceProfile(
                    role_id="guest_huaiyuan", display_name="陈怀远", language_code="zh-en", voice_id="v_h", status="locked"
                ),
                "guest_laozhou": VoiceProfile(
                    role_id="guest_laozhou", display_name="老周", language_code="zh", voice_id="v_z", status="locked"
                ),
            },
        )
        sheet = EpisodeCueSheet(
            episode_id="E001_SIMUL",
            chapter_number=1,
            title="2008年致股东信",
            mode="podcast_roundtable",
            head_pad_s=0.5,
            tail_pad_s=1.0,
            acts=[ActMusicSpec(act_id="act1", title="第一幕", bgm_prompt="acoustic guitar study", bgm_duration_s=14.0)],
            cues=[
                TimelineCue(
                    cue_id="c1_en",
                    act_id="act1",
                    kind="dialogue",
                    role_id="buffett_prime_en",
                    language_code="en",
                    text="[wryly] In God we trust; all others pay cash.",
                    stability=0.5,
                    acoustic_space="vintage_study",
                    duck_under_next=True,
                    duck_lead_in_s=2.5,
                    duck_gain=0.15,
                    gap_after_s=0.0,
                ),
                TimelineCue(
                    cue_id="c2_zh",
                    act_id="act1",
                    kind="dialogue",
                    role_id="guest_huaiyuan",
                    language_code="zh-en",
                    text="[warmly] 我们相信上帝，但其他人请一律付现。",
                    stability=0.5,
                    acoustic_space="studio_warm",
                    gap_after_s=0.4,
                ),
                TimelineCue(
                    cue_id="c3_zhou",
                    act_id="act1",
                    kind="dialogue",
                    role_id="guest_laozhou",
                    language_code="zh",
                    text="[earthy] 这话太狠了，跟我们餐馆欠账免谈一模一样！",
                    stability=0.0,
                    acoustic_space="studio_warm",
                    gap_after_s=0.3,
                ),
            ],
        )
        self.assertEqual(sheet.validate(registry=reg, require_locked_voices=True), [])

        res = master_episode_three_bus(
            cue_sheet=sheet,
            cue_audio_map={"c1_en": en_wav, "c2_zh": zh_wav, "c3_zhou": c3_wav},
            act_bgm_map={"act1": bgm_wav},
            output_dir=tmp / "out",
            registry=reg,
        )
        manifest = json.loads(res["manifest_json"].read_text(encoding="utf-8"))
        tl = {it["cue_id"]: it for it in manifest["timeline"]}
        # c1_en starts at 0.5s, ends ~9.5s; c2_zh starts at 0.5 + 2.5 = 3.0s, ends ~8.5s; c3_zhou starts at ~9.5 + 0.4 = ~9.9s!
        self.assertAlmostEqual(tl["c1_en"]["start_s"], 0.5, delta=0.05)
        self.assertAlmostEqual(tl["c2_zh"]["start_s"], 3.0, delta=0.05)
        self.assertGreaterEqual(tl["c3_zhou"]["start_s"], tl["c1_en"]["end_s"] + 0.35)

        srt_text = res["subtitles_srt"].read_text(encoding="utf-8")
        self.assertIn("【沃伦·巴菲特】In God we trust; all others pay cash.", srt_text)
        self.assertIn("【陈怀远】我们相信上帝，但其他人请一律付现。\nEN: In God we trust; all others pay cash.", srt_text)
        self.assertIn("【老周】这话太狠了", srt_text)

    def test_buffett_96gb_studio_guardrails_and_zero_cost_anchor_builder(self) -> None:
        import importlib.util

        repo_root = Path(__file__).resolve().parents[1]
        studio_py = repo_root / "colab_96gb" / "run_buffett_96gb_studio.py"
        spec_s = importlib.util.spec_from_file_location("run_buffett_96gb_studio", studio_py)
        assert spec_s and spec_s.loader
        studio_mod = importlib.util.module_from_spec(spec_s)
        spec_s.loader.exec_module(studio_mod)

        # 1. American documentary acoustic BGM enrichment must never inject ancient Chinese xianxia instruments
        bgm_p = studio_mod.enrich_buffett_acestep_bgm_prompt("Warm Omaha midnight study reflection")
        self.assertIn("acoustic guitar", bgm_p.lower())
        self.assertIn("no singing", bgm_p.lower())
        self.assertNotIn("xianxia", bgm_p.lower())

        # 2. Bilingual speaking-rate gate handles both pure English Buffett lines and code-switched ZH-EN lines
        en_cue = TimelineCue(
            cue_id="en1",
            act_id="act1",
            kind="dialogue",
            role_id="buffett_prime_en",
            language_code="en",
            text="[wryly] In God we trust; all others pay cash when the tide goes out.",
            stability=0.5,
        )
        ok_en, _ = studio_mod.check_bilingual_speaking_rate_ok(en_cue, 4.8)
        self.assertTrue(ok_en)
        fast_en, _ = studio_mod.check_bilingual_speaking_rate_ok(en_cue, 0.9)
        self.assertFalse(fast_en)

        zhen_cue = TimelineCue(
            cue_id="zh1",
            act_id="act1",
            kind="dialogue",
            role_id="guest_huaiyuan",
            language_code="zh-en",
            text="[warmly] 巴菲特真正的底牌叫 insurance float，靠 house-price appreciation 赌命迟早翻车。",
            stability=0.5,
        )
        ok_zh, _ = studio_mod.check_bilingual_speaking_rate_ok(zhen_cue, 7.2)
        self.assertTrue(ok_zh)

        # 3. Real-human vocal anchor builder (v2_real_human_studio, 0% edge-tts) produces all 4 locked roles
        prep_py = repo_root / "colab_96gb" / "prepare_buffett_voice_anchors.py"
        spec_p = importlib.util.spec_from_file_location("prepare_buffett_voice_anchors", prep_py)
        assert spec_p and spec_p.loader
        prep_mod = importlib.util.module_from_spec(spec_p)
        spec_p.loader.exec_module(prep_mod)
        self.assertEqual(prep_mod.ANCHOR_SCHEMA_VERSION, "v2_real_human_studio")
        self.assertNotIn("edge_tts", prep_py.read_text(encoding="utf-8"))

        tmp_anc = Path("/tmp/test_buffett_anchors_unit")
        if tmp_anc.exists():
            subprocess.run(["rm", "-rf", str(tmp_anc)], check=True)
        reg_path = repo_root / "projects" / "buffett_letters" / "00_节目圣经与第一季12期总纲" / "voice_casting_registry.json"
        vc_res = prep_mod.prepare_all_buffett_anchors(
            registry_path=reg_path,
            output_dir=tmp_anc,
            offline_stub=False,  # Uses bundled real-human voice_anchors/*.wav directly!
        )
        self.assertEqual(vc_res["role_count"], 4)
        self.assertEqual(vc_res["anchor_schema_version"], "v2_real_human_studio")
        for rid in ("host_zhiwei", "guest_huaiyuan", "guest_laozhou", "buffett_prime_en"):
            self.assertTrue((tmp_anc / f"voice_anchors/{rid}.wav").is_file())

    def test_v2_podcast_zero_announcer_and_micro_interruption(self) -> None:
        from aigc_audio_pipeline.drama3_adapter import (
            estimate_drama3_max_new_tokens,
            translate_cue_to_drama3_input,
        )

        repo_root = Path(__file__).resolve().parents[1]
        reg_path = repo_root / "projects" / "buffett_letters" / "00_节目圣经与第一季12期总纲" / "voice_casting_registry.json"
        reg = VoiceCastingRegistry.load(reg_path)

        # 1. Chinese podcast dialogue must NOT inject announcer-inducing '[...podcast host tone]' prefixes
        zhiwei_prof = reg.roles["host_zhiwei"]
        zh_plain = TimelineCue(
            cue_id="c_zw_plain",
            act_id="act1",
            kind="dialogue",
            role_id="host_zhiwei",
            language_code="zh",
            text="你是说充会员卡？",
            stability=0.5,
        )
        d3_plain = translate_cue_to_drama3_input(zh_plain, zhiwei_prof, attempt=1, domain="finance_podcast")
        self.assertEqual(d3_plain, "你是说充会员卡？")
        self.assertNotIn("podcast host", d3_plain)

        zh_laugh = TimelineCue(
            cue_id="c_lz_laugh",
            act_id="act1",
            kind="dialogue",
            role_id="guest_laozhou",
            language_code="zh",
            text="[chuckles] 跌九点六就叫狠啊？",
            stability=0.0,
        )
        d3_laugh = translate_cue_to_drama3_input(zh_laugh, reg.roles["guest_laozhou"], attempt=1, domain="finance_podcast")
        self.assertEqual(d3_laugh, "[light chuckle] 跌九点六就叫狠啊？")

        # 2. Token budget scales safely with utterance length without bloated 2048 runaway window on short turns
        self.assertLessEqual(estimate_drama3_max_new_tokens(zh_plain), 560)
        en_long = TimelineCue(
            cue_id="c_en_long",
            act_id="act1",
            kind="dialogue",
            role_id="buffett_prime_en",
            language_code="en",
            text="[seriously] " + " ".join(["cash"] * 60),
            stability=0.5,
        )
        self.assertGreaterEqual(estimate_drama3_max_new_tokens(en_long), 750)

        # 3. Negative gap_after_s (-0.06s conversational latch) mixes cleanly AND clamps SRT timestamps to prevent overlap
        tmp = Path("/tmp/test_v2_micro_interrupt")
        if tmp.exists():
            subprocess.run(["rm", "-rf", str(tmp)], check=True)
        tmp.mkdir(parents=True)
        for name, freq, dur in [("a.wav", 210.0, 2.0), ("b.wav", 280.0, 1.8), ("bgm.wav", 110.0, 6.0)]:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={dur}:sample_rate=48000",
                    "-af", "pan=stereo|c0=c0|c1=c0,volume=-12dB", "-c:a", "pcm_s16le", str(tmp / name),
                ],
                check=True,
            )
        reg_locked = VoiceCastingRegistry.load(reg_path)
        for r in reg_locked.roles.values():
            r.voice_id = f"v_{r.role_id}"
            r.status = "locked"
        sheet = EpisodeCueSheet(
            episode_id="TEST_LATCH",
            chapter_number=1,
            title="抢话测试",
            mode="podcast_roundtable",
            head_pad_s=0.4,
            tail_pad_s=0.8,
            acts=[ActMusicSpec(act_id="act1", title="第一幕", bgm_prompt="acoustic guitar", bgm_duration_s=6.0)],
            cues=[
                TimelineCue(cue_id="c1", act_id="act1", kind="dialogue", role_id="guest_laozhou", text="巴菲特手里那几百亿叫什么来着——", gap_after_s=-0.06),
                TimelineCue(cue_id="c2", act_id="act1", kind="dialogue", role_id="guest_huaiyuan", language_code="zh-en", text="Insurance float，保险浮存金。", gap_after_s=0.3),
            ],
        )
        self.assertEqual(sheet.validate(registry=reg_locked, require_locked_voices=True), [])
        res = master_episode_three_bus(
            cue_sheet=sheet,
            cue_audio_map={"c1": tmp / "a.wav", "c2": tmp / "b.wav"},
            act_bgm_map={"act1": tmp / "bgm.wav"},
            output_dir=tmp / "out",
            registry=reg_locked,
        )
        manifest = json.loads(res["manifest_json"].read_text(encoding="utf-8"))
        tl = {it["cue_id"]: it for it in manifest["timeline"]}
        self.assertLess(tl["c2"]["start_s"], tl["c1"]["end_s"])
        srt_lines = res["subtitles_srt"].read_text(encoding="utf-8").splitlines()
        ts_lines = [ln for ln in srt_lines if " --> " in ln]
        self.assertEqual(len(ts_lines), 2)
        first_end = ts_lines[0].split(" --> ")[1]
        second_start = ts_lines[1].split(" --> ")[0]
        self.assertLessEqual(first_end, second_start)

        # 4. Compiled V2.1 AUDITION_BUFFETT and E001 cue sheets validate cleanly with zero clichés
        for fn in (
            "AUDITION_BUFFETT_四角色定角试听包.json",
            "E001_2008年致股东信_满地是血的夜晚谁在裸泳_完整圆桌台本.json",
        ):
            cs = EpisodeCueSheet.load(repo_root / "projects" / "buffett_letters" / "02_分期圆桌台本" / fn)
            self.assertEqual(cs.validate(registry=reg_locked, require_locked_voices=True), [])
            joined_zh = "\n".join(c.text for c in cs.cues if c.kind == "dialogue" and c.language_code != "en")
            for banned in ("问到根子上了", "这个比方绝了", "穿越周期·三阶锦囊", "各位听众"):
                self.assertNotIn(banned, joined_zh)

        # 5. Natural sentence-pause ducking snap & percentage ASR QA normalization ("百分之二十？" == "20%?")
        from aigc_audio_pipeline.mixer import find_natural_duck_pause_s

        sr = 48000
        speech_a = array("h", [9000]) * int(6.60 * sr * 2)
        pause_gap = array("h", [80]) * int(0.32 * sr * 2)  # natural sentence break at 6.60s..6.92s
        speech_b = array("h", [9000]) * int(5.00 * sr * 2)
        full_clip = speech_a + pause_gap + speech_b
        snapped_s = find_natural_duck_pause_s(
            full_clip,
            target_s=5.4,
            dur_s=(len(full_clip) // 2) / sr,
            sample_rate=sr,
        )
        self.assertGreaterEqual(snapped_s, 6.60)
        self.assertLessEqual(snapped_s, 6.92)

        pct_qa = evaluate_dialogue_qa(
            tagged_prompt="百分之二十？",
            asr_text="20%?",
            duration_s=1.4,
            peak_dbfs=-11.0,
        )
        self.assertTrue(pct_qa.passed)

    def test_anthology_three_shows_validation_polyphones_and_studio_guardrails(self) -> None:
        """Verify Liaozhai, Cthulhu, and Hayek anthology registries, 21 cue sheets, polyphones, and G4 studio guardrails."""
        import importlib.util
        import json

        from aigc_audio_pipeline.drama3_adapter import translate_cue_to_drama3_input
        from aigc_audio_pipeline.polyphones import compute_tts_text_override

        repo_root = Path(__file__).resolve().parents[1]
        zhujie_cast = json.loads(
            (repo_root / "projects/zhujie_suoxian/00_声音选角档案与进度台账/voice_cast_drama3.json").read_text(encoding="utf-8")
        )["characters"]

        # 1. Domain polyphone disambiguation keeps canonical text clean while fixing error-prone readings
        self.assertEqual(
            compute_tts_text_override("三更夜访兰若寺，屏住呼吸。", domain="liaozhai_horror"),
            "三羹夜访兰惹寺，丙住呼吸。",
        )
        self.assertEqual(
            compute_tts_text_override("弗朗西斯·瑟斯顿屏息望向船舷。", domain="cosmic_horror"),
            "弗朗西斯瑟斯顿丙息望向船咸。",
        )
        self.assertEqual(
            compute_tts_text_override("弗里德里希·哈耶克与约翰·梅纳德·凯恩斯谈各行各业。", domain="hayek_economics"),
            "弗里德里希哈耶克与约翰梅纳德凯恩斯谈各航各业。",
        )
        self.assertEqual(
            compute_tts_text_override("爱德蒙·唐泰斯屏息倚在船舷，押解前往伊夫堡。", domain="monte_cristo_drama"),
            "爱德蒙唐泰斯丙息倚在船咸，押借前往伊夫堡。",
        )

        # 2. Validate every registry, anchor mapping, and all 7 cue sheets across all 4 anthology shows
        shows = [
            ("liaozhai_midnight", "liaozhai_horror", 7),
            ("cthulhu_archives", "cosmic_horror", 7),
            ("hayek_1944", "hayek_economics", 7),
            ("monte_cristo", "monte_cristo_drama", 7),
        ]
        for proj_name, expected_domain, expected_count in shows:
            proj_dir = repo_root / "projects" / proj_name
            reg = VoiceCastingRegistry.load(proj_dir / "00_节目圣经与选角档案/voice_casting_registry.json")
            self.assertEqual(reg.domain, expected_domain)

            anchor_cfg = json.loads((proj_dir / "00_节目圣经与选角档案/anchor_sources.json").read_text(encoding="utf-8"))
            self.assertEqual(set(anchor_cfg["role_mappings"].keys()), set(reg.roles.keys()))
            for r_id, mapping in anchor_cfg["role_mappings"].items():
                if mapping["source_bundle"] == "zhujie_suoxian":
                    self.assertIn(mapping["source_role_id"], zhujie_cast, f"{proj_name}.{r_id} missing in zhujie cast")
                elif mapping["source_bundle"] == "repo_buffett_real_human":
                    wav_p = (
                        repo_root
                        / "projects/buffett_letters/00_节目圣经与第一季12期总纲/voice_anchors"
                        / f"{mapping['source_role_id']}.wav"
                    )
                    self.assertTrue(wav_p.is_file(), f"Missing real-human anchor {wav_p}")

            scripts_dir = proj_dir / "02_分集广播剧台本"
            jsons = sorted([*scripts_dir.glob("AUDITION*.json"), *scripts_dir.glob("E*.json")])
            self.assertEqual(len(jsons), expected_count)
            for jp in jsons:
                cs = EpisodeCueSheet.load(jp)
                self.assertEqual(cs.validate(reg, require_locked_voices=True), [], f"Errors in {jp.name}")

        # 3. Verify horror/intellectual/revenge Drama 3 tag translation & domain-aware narrator styles
        c_liao = TimelineCue(cue_id="t1", act_id="a1", kind="dialogue", role_id="narrator", text="三更雨落兰若寺。", stability=0.5)
        d3_liao = translate_cue_to_drama3_input(c_liao, VoiceProfile(role_id="narrator", display_name="旁白", tier="narrator"), domain="liaozhai_horror")
        self.assertIn("folklore suspense", d3_liao)
        self.assertIn("兰惹寺", d3_liao)

        c_cth = TimelineCue(cue_id="t2", act_id="a1", kind="dialogue", role_id="eldritch_whisper", text="[haunting] [whispers] 拉莱耶在呼唤。", stability=0.0)
        d3_cth = translate_cue_to_drama3_input(c_cth, VoiceProfile(role_id="eldritch_whisper", display_name="低语", tier="antagonist"), domain="cosmic_horror")
        self.assertIn("<whisper>", d3_cth)

        c_mc = TimelineCue(cue_id="t3", act_id="a1", kind="dialogue", role_id="narrator", text="爱德蒙·唐泰斯屏息站在船舷。", stability=0.5)
        d3_mc = translate_cue_to_drama3_input(c_mc, VoiceProfile(role_id="narrator", display_name="史诗旁白", tier="narrator"), domain="monte_cristo_drama")
        self.assertIn("gothic revenge drama", d3_mc)
        self.assertIn("爱德蒙唐泰斯丙息站在船咸", d3_mc)

        # 4. Verify universal anthology studio BGM isolation & QA leak detection on new horror tags
        spec = importlib.util.spec_from_file_location(
            "run_anthology_96gb_studio",
            repo_root / "colab_96gb/run_anthology_96gb_studio.py",
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        cthulhu_bgm = mod.enrich_anthology_bgm_prompt("Sparse cold cello drone", bgm_style="cosmic_horror")
        self.assertIn("no vocals", cthulhu_bgm.lower())
        self.assertNotIn("traditional chinese", cthulhu_bgm.lower())

        mc_bgm = mod.enrich_anthology_bgm_prompt("Mediterranean cliff twilight suspense", bgm_style="monte_cristo_drama")
        self.assertIn("no vocals", mc_bgm.lower())
        self.assertIn("orchestral", mc_bgm.lower())
        self.assertNotIn("traditional chinese", mc_bgm.lower())

        leak_qa = evaluate_dialogue_qa(
            tagged_prompt="[haunting] 拉莱耶在呼唤。",
            asr_text="haunting 拉莱耶在呼唤",
            duration_s=2.0,
            peak_dbfs=-10.0,
        )
        self.assertFalse(leak_qa.passed)
        self.assertIn("haunting", leak_qa.leaked_tags)


if __name__ == "__main__":
    unittest.main()



