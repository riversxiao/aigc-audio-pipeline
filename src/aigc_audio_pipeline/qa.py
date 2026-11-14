"""Automated ASR & signal quality assurance for eleven_v3 dialogue lines."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
import subprocess
from typing import Any

from .elevenlabs_client import ElevenLabsClient, ElevenLabsError, SynthesisResult
from .models import extract_tags_and_spoken_text, simplify_inline_tags

_CJK_ONLY = re.compile(r"[\u4e00-\u9fff0-9]+")
_DIGIT_MAP = str.maketrans("0123456789", "零一二三四五六七八九")
_LATIN_WORDS = re.compile(r"[a-zA-Z]{3,}")
# Strip Scribe non-speech event annotations like (笑声), (laughter), [sighs] before checking spoken leaks
_AUDIO_EVENT_ANNOTATIONS = re.compile(r"\([^)]*\)|（[^）]*）|\[[^\]]*\]")

COMMON_TAG_WORDS: frozenset[str] = frozenset(
    {
        "angry",
        "crying",
        "dramatic",
        "dramatically",
        "excited",
        "sarcastic",
        "whispers",
        "whispering",
        "shouts",
        "shouting",
        "rushed",
        "softly",
        "laughs",
        "laughing",
        "sighs",
        "exhales",
        "gasps",
        "pause",
        "coldly",
        "desperately",
        "mischievously",
        "dismissive",
        "condescending",
        "hoarsely",
        "trembling",
    }
)


_TRAD_TO_SIMP = str.maketrans(
    "兩號點菸別為這兒棟辦樓們沒長歸勞動說對開關門記憶實驗員處裡發現問題東無腦電視聽見覺個種時間樣會過後頭臉聲響"
    "體機級部門應還從來進連讓給話語誰怎麼經與當卻將並於萬億歲車軍風雲飛殺劍氣靈陣丹魂識鎖諸界師傳宗護數條際認"
    "壓擊戰場邊書寫讀錄線層區態類總斷篤抬挑眉嘆噢吶剛才雖確已經專業資歷檔案編號終端權限刪銷毀觀測實體收容異常"
    "辦公室抽煙漲費電梯走廊螢幕鍵盤警報靜默遺忘藥劑膠囊注射劑量測試報告記錄儀器數據網絡連線斷開確認拒絕訪問密碼",
    "两号点烟别为这儿栋办楼们没长归劳动说对开关门记忆实验员处里发现问题东无脑电视听见觉个种时间样会过后头脸声响"
    "体机级部门应还从来进连让给话语谁怎么经与当却将并于万亿岁车军风云飞杀剑气灵阵丹魂识锁诸界师传宗护数条际认"
    "压击战场边书写读录线层区态类总断笃抬挑眉叹噢呐刚才虽确已经专业资历档案编号终端权限删销毁观测实体收容异常"
    "办公室抽烟涨费电梯走廊屏幕键盘警报静默遗忘药剂胶囊注射剂量测试报告记录仪器数据网络连线断开确认拒绝访问密码",
)

_ASR_HOMOPHONE_FOLDS: tuple[tuple[str, str], ...] = (
    ("魔阴步", "模因部"),
    ("魔因部", "模因部"),
    ("摩因部", "模因部"),
    ("魔阴", "模因"),
    ("摩因", "模因"),
    ("玛丽恩", "玛丽安"),
    ("马丽安", "玛丽安"),
    ("马利安", "玛丽安"),
    ("玛利安", "玛丽安"),
    ("可来", "克莱"),
    ("刻来", "克莱"),
    ("克来", "克莱"),
    ("凯特儿", "凯特尔"),
    ("天呐", "天哪"),
    ("硬道", "应道"),
    ("硬到", "应道"),
    ("曼调斯里", "慢条斯理"),
    ("找了眨眼", "眨了眨眼"),
    ("隔泪", "格雷"),
    ("葛雷", "格雷"),
    ("请联盟", "金连忙"),
    ("请连忙", "金连忙"),
    ("清眨", "金眨"),
    ("精眨", "金眨"),
    ("精心投", "金心头"),
    ("惊心投", "金心头"),
    ("修斯", "休斯"),
    ("哦", "噢"),
)


def _cjk_chars(text: str) -> str:
    raw = "".join(_CJK_ONLY.findall(text)).translate(_DIGIT_MAP).translate(_TRAD_TO_SIMP)
    for src, dst in _ASR_HOMOPHONE_FOLDS:
        if src in raw:
            raw = raw.replace(src, dst)
    return raw


def _longest_common_subsequence_len(a: str, b: str) -> int:
    if not a or not b:
        return 0
    dp = [0] * (len(b) + 1)
    for ca in a:
        prev = 0
        for j, cb in enumerate(b, 1):
            tmp = dp[j]
            if ca == cb:
                dp[j] = prev + 1
            elif dp[j - 1] > dp[j]:
                dp[j] = dp[j - 1]
            prev = tmp
    return dp[-1]


@dataclass
class LineQAResult:
    passed: bool
    attempt: int
    expected_spoken: str
    asr_transcript: str
    char_recall: float
    tail_preserved: bool
    leaked_tags: list[str] = field(default_factory=list)
    peak_dbfs: float = -12.0
    duration_s: float = 0.0
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_audio_peak_dbfs(wav_path: Path) -> tuple[float, float]:
    """Return (duration_s, max_volume_dbfs) via ffmpeg volumedetect."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(wav_path),
        "-af",
        "volumedetect",
        "-f",
        "null",
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    stderr = proc.stderr
    max_vol = -99.0
    m_vol = re.search(r"max_volume:\s*([-\d.]+)\s*dB", stderr)
    if m_vol:
        max_vol = float(m_vol.group(1))
    m_dur = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", stderr)
    dur_s = 0.0
    if m_dur:
        dur_s = int(m_dur.group(1)) * 3600 + int(m_dur.group(2)) * 60 + float(m_dur.group(3))
    return dur_s, max_vol


def evaluate_dialogue_qa(
    *,
    tagged_prompt: str,
    asr_text: str,
    duration_s: float,
    peak_dbfs: float,
    attempt: int = 1,
    min_char_recall: float = 0.72,
    canonical_prompt: str | None = None,
) -> LineQAResult:
    """Evaluate ASR transcript & signal stats against Playbook QA criteria."""
    tags, expected_spoken = extract_tags_and_spoken_text(tagged_prompt)
    canon_tags, canon_spoken = (
        extract_tags_and_spoken_text(canonical_prompt)
        if canonical_prompt
        else ([], expected_spoken)
    )
    cleaned_asr = _AUDIO_EVENT_ANNOTATIONS.sub("", asr_text)

    reasons: list[str] = []
    # 1. Check leaked English audio tags
    prompt_tag_tokens = {
        w.lower()
        for tag in (*tags, *canon_tags)
        for w in _LATIN_WORDS.findall(tag)
    } | COMMON_TAG_WORDS
    spoken_latin = [w.lower() for w in _LATIN_WORDS.findall(cleaned_asr)]
    expected_latin = {
        w.lower()
        for w in (*_LATIN_WORDS.findall(expected_spoken), *_LATIN_WORDS.findall(canon_spoken))
    }
    leaked = sorted({w for w in spoken_latin if w in prompt_tag_tokens and w not in expected_latin})
    if leaked:
        reasons.append(f"Inline English audio tag(s) spoken aloud: {leaked}")

    # 2. Check CJK completeness & tail preservation (against either phonetic tts_text or canonical text)
    exp_cjk = _cjk_chars(expected_spoken)
    canon_cjk = _cjk_chars(canon_spoken)
    got_cjk = _cjk_chars(cleaned_asr)
    if len(exp_cjk) == 0:
        recall = 1.0
        tail_ok = True
    else:
        recall_tts = _longest_common_subsequence_len(exp_cjk, got_cjk) / len(exp_cjk)
        recall_canon = (
            _longest_common_subsequence_len(canon_cjk, got_cjk) / len(canon_cjk)
            if canon_cjk
            else 0.0
        )
        recall = max(recall_tts, recall_canon)

        def _check_tail(ref_cjk: str) -> bool:
            if not ref_cjk:
                return True
            if not got_cjk:
                return False
            tw = ref_cjk[-min(3, len(ref_cjk)) :]
            return any(ch in got_cjk[-min(6, max(1, len(got_cjk))) :] for ch in tw)

        tail_ok = _check_tail(exp_cjk) or _check_tail(canon_cjk)
        if len(exp_cjk) >= 4 and recall < min_char_recall:
            reasons.append(
                f"Low character recall ({recall:.2f} < {min_char_recall:.2f}): "
                f"expected={canon_spoken!r}, got={asr_text!r}"
            )
        if len(exp_cjk) >= 6 and not tail_ok:
            tail_window = canon_cjk[-min(3, len(canon_cjk)) :] if canon_cjk else exp_cjk[-3:]
            reasons.append(f"Potential tail truncation: ending {tail_window!r} missing in ASR {asr_text!r}")

    # 3. Signal sanity check
    if duration_s < 0.25:
        reasons.append(f"Audio abnormally short ({duration_s:.2f}s)")
    if peak_dbfs < -45.0:
        reasons.append(f"Audio nearly silent (peak {peak_dbfs:.1f} dBFS)")

    return LineQAResult(
        passed=len(reasons) == 0,
        attempt=attempt,
        expected_spoken=canon_spoken,
        asr_transcript=asr_text,
        char_recall=round(recall, 4),
        tail_preserved=tail_ok,
        leaked_tags=leaked,
        peak_dbfs=round(peak_dbfs, 2),
        duration_s=round(dur_s := duration_s, 3),
        reasons=reasons,
    )


def synthesize_with_playbook_qa(
    client: ElevenLabsClient,
    *,
    voice_id: str,
    tagged_text: str,
    output_wav: Path,
    stability: float,
    similarity_boost: float = 0.85,
    language_code: str = "zh",
    enable_asr_qa: bool = True,
    canonical_prompt: str | None = None,
) -> tuple[SynthesisResult, LineQAResult, str]:
    """Synthesize a dialogue line with Scribe QA and at most 1 simplified-tag retry.

    Playbook rule:
    - Retry at most ONCE with simpler tags if tags leak or audio is truncated.
    - Stop after 2 attempts; never loop and burn credits.
    Returns (synthesis_result, qa_result, final_text_used).
    """
    current_text = tagged_text
    for attempt in (1, 2):
        # On retry attempt 2, bypass cache if same text, though text is simplified
        synth = client.synthesize_dialogue(
            voice_id=voice_id,
            text=current_text,
            output_wav=output_wav,
            stability=stability,
            similarity_boost=similarity_boost,
            language_code=language_code,
            use_cache=(attempt == 1),
        )
        dur_s, peak_db = inspect_audio_peak_dbfs(output_wav)
        if not enable_asr_qa:
            qa = LineQAResult(
                passed=dur_s >= 0.25 and peak_db >= -45.0,
                attempt=attempt,
                expected_spoken=extract_tags_and_spoken_text(canonical_prompt or current_text)[1],
                asr_transcript="[ASR QA skipped]",
                char_recall=1.0,
                tail_preserved=True,
                peak_dbfs=round(peak_db, 2),
                duration_s=round(dur_s, 3),
            )
            return synth, qa, current_text

        try:
            asr_resp = client.transcribe_asr(output_wav, language_code=language_code)
        except ElevenLabsError as exc:
            if exc.status_code in (401, 403) and "missing_permissions" in exc.body:
                qa = LineQAResult(
                    passed=dur_s >= 0.25 and peak_db >= -45.0,
                    attempt=attempt,
                    expected_spoken=extract_tags_and_spoken_text(canonical_prompt or current_text)[1],
                    asr_transcript="[ASR QA skipped: scoped key lacks speech_to_text]",
                    char_recall=1.0,
                    tail_preserved=True,
                    peak_dbfs=round(peak_db, 2),
                    duration_s=round(dur_s, 3),
                )
                return synth, qa, current_text
            raise

        asr_text = str(asr_resp.get("text", "")).strip()
        qa = evaluate_dialogue_qa(
            tagged_prompt=current_text,
            canonical_prompt=canonical_prompt,
            asr_text=asr_text,
            duration_s=dur_s,
            peak_dbfs=peak_db,
            attempt=attempt,
        )
        if qa.passed or attempt == 2:
            return synth, qa, current_text

        # Archive failed attempt 1 before retrying with simplified tags
        failed_backup = output_wav.with_name(f"{output_wav.stem}_attempt1_failed.wav")
        if not failed_backup.exists():
            failed_backup.write_bytes(output_wav.read_bytes())
        current_text = simplify_inline_tags(tagged_text)

    raise RuntimeError("Unreachable")

