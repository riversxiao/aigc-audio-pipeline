"""Automated ASR & signal quality assurance for eleven_v3 dialogue lines."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
import subprocess
from typing import Any

from .elevenlabs_client import ElevenLabsClient, SynthesisResult
from .models import extract_tags_and_spoken_text, simplify_inline_tags

_CJK_ONLY = re.compile(r"[\u4e00-\u9fff0-9]+")
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


def _cjk_chars(text: str) -> str:
    return "".join(_CJK_ONLY.findall(text))


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
) -> LineQAResult:
    """Evaluate ASR transcript & signal stats against Playbook QA criteria."""
    tags, expected_spoken = extract_tags_and_spoken_text(tagged_prompt)
    cleaned_asr = _AUDIO_EVENT_ANNOTATIONS.sub("", asr_text)

    reasons: list[str] = []
    # 1. Check leaked English audio tags
    prompt_tag_tokens = {
        w.lower()
        for tag in tags
        for w in _LATIN_WORDS.findall(tag)
    } | COMMON_TAG_WORDS
    spoken_latin = [w.lower() for w in _LATIN_WORDS.findall(cleaned_asr)]
    expected_latin = {w.lower() for w in _LATIN_WORDS.findall(expected_spoken)}
    leaked = sorted({w for w in spoken_latin if w in prompt_tag_tokens and w not in expected_latin})
    if leaked:
        reasons.append(f"Inline English audio tag(s) spoken aloud: {leaked}")

    # 2. Check CJK completeness & tail preservation
    exp_cjk = _cjk_chars(expected_spoken)
    got_cjk = _cjk_chars(cleaned_asr)
    if len(exp_cjk) == 0:
        recall = 1.0
        tail_ok = True
    else:
        lcs = _longest_common_subsequence_len(exp_cjk, got_cjk)
        recall = lcs / len(exp_cjk)
        tail_window = exp_cjk[-min(3, len(exp_cjk)) :]
        tail_ok = any(ch in got_cjk[-min(6, max(1, len(got_cjk))) :] for ch in tail_window) if got_cjk else False
        if len(exp_cjk) >= 4 and recall < min_char_recall:
            reasons.append(f"Low character recall ({recall:.2f} < {min_char_recall:.2f}): expected={expected_spoken!r}, got={asr_text!r}")
        if len(exp_cjk) >= 6 and not tail_ok:
            reasons.append(f"Potential tail truncation: ending {tail_window!r} missing in ASR {asr_text!r}")

    # 3. Signal sanity check
    if duration_s < 0.25:
        reasons.append(f"Audio abnormally short ({duration_s:.2f}s)")
    if peak_dbfs < -45.0:
        reasons.append(f"Audio nearly silent (peak {peak_dbfs:.1f} dBFS)")

    return LineQAResult(
        passed=len(reasons) == 0,
        attempt=attempt,
        expected_spoken=expected_spoken,
        asr_transcript=asr_text,
        char_recall=round(recall, 4),
        tail_preserved=tail_ok,
        leaked_tags=leaked,
        peak_dbfs=round(peak_dbfs, 2),
        duration_s=round(duration_s, 3),
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
                expected_spoken=extract_tags_and_spoken_text(current_text)[1],
                asr_transcript="[ASR QA skipped]",
                char_recall=1.0,
                tail_preserved=True,
                peak_dbfs=round(peak_db, 2),
                duration_s=round(dur_s, 3),
            )
            return synth, qa, current_text

        asr_resp = client.transcribe_asr(output_wav, language_code=language_code)
        asr_text = str(asr_resp.get("text", "")).strip()
        qa = evaluate_dialogue_qa(
            tagged_prompt=current_text,
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
