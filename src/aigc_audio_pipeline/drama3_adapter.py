"""Fish Audio Drama 3 (SGLang-Omni) acting-prompt translator, vocal anchor exporter, and 96GB Colab bundle builder.

Bridges `aigc-audio-pipeline`'s canonical `EpisodeCueSheet` + `VoiceCastingRegistry` directly to the
open-weight 96GB Co-Resident Golden Stack:
  1. `fishaudio/drama-3` (35B MoE, 3B active, FP8/BF16 via `sglang-omni` `/v1/audio/speech`)
  2. `OpenMOSS-Team/MOSS-SoundEffect-v2.0` (48kHz Foley SFX)
  3. `ACE-Step/acestep-v15-xl-turbo-diffusers` (48kHz Stereo Per-Act BGM)
"""

from __future__ import annotations

from array import array
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import wave
import zipfile
from typing import Any

from .elevenlabs_client import probe_duration_seconds
from .models import (
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    VoiceProfile,
    extract_tags_and_spoken_text,
    utc_now_iso,
)
from .polyphones import apply_domain_polyphone_overrides, apply_xianxia_polyphone_overrides

DRAMA3_ANCHOR_SAMPLE_RATE = 44100
_TAG_TOKEN_RE = re.compile(r"\[([^\[\]]+)\]")
_XML_SPAN_RE = re.compile(r"</?(?:whisper|soft|forceful|slow|fast|emphasis)>")
_PHONEME_SPAN_RE = re.compile(r"<\|phoneme_start\|>.*?<\|phoneme_end\|>")

# Maps eleven_v3 lowercase tags -> (Drama 3 natural-language acting brief, optional paired XML span tag)
DRAMA3_TAG_MAP: dict[str, tuple[str, str]] = {
    "coldly": ("cold, restrained and icy tone", ""),
    "calmly": ("calm, steady and composed", ""),
    "softly": ("soft, gentle and hushed", "soft"),
    "whispers": ("low tense whisper, close to mic", "whisper"),
    "whispering": ("low tense whisper, close to mic", "whisper"),
    "dramatically": ("epic, solemn and cinematic gravity", ""),
    "dramatic tone": ("epic, solemn and cinematic gravity", ""),
    "dramatic": ("epic, solemn and cinematic gravity", ""),
    "shouting": ("forceful, commanding roar", "forceful"),
    "shouts": ("forceful, commanding roar", "forceful"),
    "angry": ("seething suppressed fury, sharp bite", "forceful"),
    "fiercely": ("fierce, razor-sharp intensity", "forceful"),
    "crying": ("choked with tears, trembling grief", ""),
    "desperately": ("urgent, breathless desperation", ""),
    "hoarsely": ("raspy, strained and breathless", ""),
    "dismissive": ("aloof, aristocratic disdain", ""),
    "condescending": ("warm yet condescending sneer", ""),
    "sarcastic": ("cold, mocking sneer", ""),
    "trembling": ("shaky breath, trembling voice", ""),
    "rushed": ("urgent, rapid breathless pace", ""),
    "excited": ("intense, surging excitement", ""),
    "mischievously": ("sly, knowing smirk", ""),
    # Modern conversational podcast & prime-age Omaha Buffett delivery tags
    "conversational": ("warm, relaxed modern podcast conversation", ""),
    "curious": ("bright, curious and engaging podcast host tone", ""),
    "pushback": ("sharp, lively conversational pushback", ""),
    "warmly": ("warm, measured and thoughtful tone", ""),
    "wryly": ("wry, folksy Midwestern wit with a knowing smile", ""),
    "folksy": ("energetic, clear prime-age Midwestern storyteller cadence", ""),
    "earthy": ("hearty, down-to-earth street-smart entrepreneur tone", ""),
    "seriously": ("grounded, sober and earnest gravity", ""),
    # Supernatural folklore & cosmic horror radio-drama delivery tags
    "eerie": ("eerie, ghostly, bone-chilling undertone", ""),
    "terrified": ("panting in sheer terror, voice cracking with dread", ""),
    "seductive": ("silky, bewitching, velvet-soft allure with hidden menace", "soft"),
    "maniacal": ("unhinged, manic trembling intensity on the brink of madness", ""),
    "solemn": ("grave, solemn, heavy cinematic stillness", "slow"),
    "haunting": ("hollow, haunting unearthly whisper", "whisper"),
    # Modern news hotline roundtable, commentary & urban social drama tags
    "ironic": ("dry, pointed ironic undertone", ""),
    "skeptical": ("sharp, skeptical questioning tone", ""),
    "urgent": ("urgent, tight breaking-news energy", ""),
    "emphatic": ("firm, emphatic clarity on key point", ""),
    "amused": ("light, amused wry delivery", ""),
    "somber": ("quiet, somber, heavy emotional weight", "slow"),
    "indignant": ("heated, righteous indignation", "forceful"),
    "weary": ("exhausted, hollow, worn-down quiet resignation", "soft"),
    "tender": ("gentle, compassionate, intimate warmth", "soft"),
    "nervous": ("hesitant, tight nervous breath", ""),
    "smug": ("brazen, self-satisfied smug arrogance", ""),
    "shocked": ("stunned, caught-off-guard disbelief", ""),
    "composed": ("steady, dignified, restrained composure", ""),
    "sardonic": ("biting, cynical sardonic edge", ""),
}

# Paralinguistic point events kept inline in Drama 3 square brackets
DRAMA3_POINT_EVENTS: dict[str, str] = {
    "sighs": "[sighs]",
    "exhales": "[slow exhale]",
    "gasps": "[sharp inhale]",
    "pause": "[short pause]",
    "short pause": "[short pause]",
    "long pause": "[short pause]",
    "chuckles": "[light chuckle]",
    "clears throat": "[clears throat]",
}

# Optional Fish Audio Drama 3 native Chinese Pinyin phoneme overrides (<|phoneme_start|>...<|phoneme_end|>)
XIANXIA_DRAMA3_PHONEME_PINS: tuple[tuple[str, str], ...] = (
    ("引气一重", "<|phoneme_start|>yin3 qi4 yi1 chong2<|phoneme_end|>"),
    ("引气二重", "<|phoneme_start|>yin3 qi4 er4 chong2<|phoneme_end|>"),
    ("引气三重", "<|phoneme_start|>yin3 qi4 san1 chong2<|phoneme_end|>"),
    ("引气四重", "<|phoneme_start|>yin3 qi4 si4 chong2<|phoneme_end|>"),
    ("引气五重", "<|phoneme_start|>yin3 qi4 wu3 chong2<|phoneme_end|>"),
    ("引气六重", "<|phoneme_start|>yin3 qi4 liu4 chong2<|phoneme_end|>"),
    ("引气七重", "<|phoneme_start|>yin3 qi4 qi1 chong2<|phoneme_end|>"),
    ("引气八重", "<|phoneme_start|>yin3 qi4 ba1 chong2<|phoneme_end|>"),
    ("引气九重", "<|phoneme_start|>yin3 qi4 jiu3 chong2<|phoneme_end|>"),
    ("真传", "<|phoneme_start|>zhen1 chuan2<|phoneme_end|>"),
    ("亲传", "<|phoneme_start|>qin1 chuan2<|phoneme_end|>"),
    ("拾级而上", "<|phoneme_start|>she4 ji2 er2 shang4<|phoneme_end|>"),
    ("龟裂", "<|phoneme_start|>jun1 lie4<|phoneme_end|>"),
    ("龟息", "<|phoneme_start|>gui1 xi1<|phoneme_end|>"),
    ("辟谷", "<|phoneme_start|>bi4 gu3<|phoneme_end|>"),
    ("道行", "<|phoneme_start|>dao4 heng2<|phoneme_end|>"),
    ("九月廿三", "<|phoneme_start|>jiu3 yue4 nian4 san1<|phoneme_end|>"),
    ("廿三", "<|phoneme_start|>nian4 san1<|phoneme_end|>"),
)


def split_tagged_clauses(tagged_text: str) -> list[tuple[list[str], str]]:
    """Split `[tag1] [tag2] clause A [tag3] clause B` into `[(tags, clause_text), ...]`."""
    segments: list[tuple[list[str], str]] = []
    pending_tags: list[str] = []
    cursor = 0
    for match in _TAG_TOKEN_RE.finditer(tagged_text):
        before = tagged_text[cursor : match.start()].strip()
        if before:
            segments.append((pending_tags, before))
            pending_tags = []
        pending_tags.append(match.group(1).strip().lower())
        cursor = match.end()

    tail = tagged_text[cursor:].strip()
    if tail:
        segments.append((pending_tags, tail))
    elif pending_tags and segments:
        prev_tags, prev_text = segments[-1]
        segments[-1] = (prev_tags + pending_tags, prev_text)
    return segments


def _apply_drama3_phonetics(
    raw_tagged: str,
    *,
    use_phoneme_pins: bool = False,
    domain: str = "xianxia",
    language_code: str = "zh",
) -> str:
    if language_code == "en":
        return raw_tagged
    if domain != "xianxia":
        return apply_domain_polyphone_overrides(raw_tagged, domain=domain)
    if use_phoneme_pins:
        out = raw_tagged
        for canonical, pin in XIANXIA_DRAMA3_PHONEME_PINS:
            if canonical in out:
                out = out.replace(canonical, pin)
        return apply_xianxia_polyphone_overrides(out)
    return apply_xianxia_polyphone_overrides(raw_tagged)


def strip_drama3_markup(drama3_text: str) -> str:
    """Strip Drama 3 `[directions]` and `<whisper>` XML tags, leaving spoken text."""
    no_xml = _XML_SPAN_RE.sub("", drama3_text)
    no_brackets = _TAG_TOKEN_RE.sub("", no_xml)
    return re.sub(r"\s+", " ", no_brackets).strip()


# Subtle non-announcer micro-cues for Chinese finance_podcast & hotline talk/roundtable
# (conversational/curious/warmly/earthy/seriously intentionally map to "" so the real-human studio
# reference WAV drives 100% natural, unforced conversational prosody!)
FINANCE_PODCAST_ZH_MICRO_MAP: dict[str, tuple[str, str]] = {
    "softly": ("", "soft"),
    "whispers": ("压低声音", "whisper"),
    "whispering": ("压低声音", "whisper"),
    "pushback": ("语气微顿、敏锐追问", ""),
    "wryly": ("带着一丝冷幽默", ""),
    "sarcastic": ("略带反讽", ""),
    "ironic": ("略带反讽", ""),
    "skeptical": ("带着几分质疑追问", ""),
    "urgent": ("语速紧凑、切入重点", ""),
    "emphatic": ("吐字加重、点出关键", ""),
    "amused": ("带着笑意调侃", ""),
    "somber": ("语气放缓、沉静克制", "slow"),
    "indignant": ("语气发沉、带着不平", ""),
}


def estimate_drama3_max_new_tokens(drama3_input: str | TimelineCue, *, language_code: str = "zh") -> int:
    """Estimate safe upper-bound `max_new_tokens` (~3.2x expected 21.53Hz frames, clamped to [384, 2048])."""
    if isinstance(drama3_input, TimelineCue):
        language_code = drama3_input.language_code or language_code
        raw_text = drama3_input.tts_text or drama3_input.text
    else:
        raw_text = drama3_input
    plain = strip_drama3_markup(_PHONEME_SPAN_RE.sub("字", raw_text))
    cjk_n = len(_CJK_COUNT_RE.findall(plain))
    en_words = len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", plain))
    if language_code == "en" or (cjk_n == 0 and en_words > 0):
        est_sec = max(1.5, en_words / 2.35)
    else:
        est_sec = max(1.2, (cjk_n + 2.2 * en_words) / 3.6)
    est_tokens = int(math.ceil(est_sec * 21.53 * 3.2)) + 96
    return max(384, min(2048, est_tokens))


_ECON_FINANCE_NARRATOR_BRIEFS: dict[str, str] = {
    "extraordinary_delusions": "vivid, wry 1841 Victorian London historical chronicle narration",
    "bastiat_unseen": "witty, sparkling 1850 Parisian satirical intellectual drama narration",
    "one_lesson_econ": "clear, sharp, everyday-life practical economics storytelling narration",
    "basic_economics": "grounded, lucid, down-to-earth investigative economics drama narration",
    "freakonomics_theater": "curious, snappy modern investigative mystery storytelling narration",
    "leisure_class_1899": "dry, observant 1899 Gilded Age social satire narration",
    "schumpeter_1911": "energetic, sweeping 1911 Vienna industrial innovation drama narration",
    "moral_sentiments_1759": "warm, empathetic, poetic 18th-century Scottish philosophical drama narration",
    "why_nations_fail": "grand, vivid global economic history documentary narration",
    "stock_operator_1923": "taut, gripping 1920s Wall Street trading-floor memoir narration",
    "intelligent_investor": "calm, measured, reassuring Columbia value-investing classroom narration",
    "random_walk_wallstreet": "breezy, witty, irreverent modern Wall Street commentary narration",
    "behavioral_econ_traps": "engaging, insightful cognitive psychology documentary drama narration",
    "psychology_of_money": "warm, intimate, reflective fireside personal-wealth storytelling narration",
    "black_swan_antifragile": "incisive, suspenseful risk-philosophy documentary narration",
    "big_short_2008": "tense, taut 2008 financial crisis investigative thriller narration",
    "lords_of_finance_1929": "solemn, cinematic 1929 interwar central-bank historical epic narration",
    "ascent_of_money": "sweeping, vibrant centuries-spanning financial history documentary narration",
    "capitalism_and_freedom": "crisp, articulate 1962 Chicago public-policy debate narration",
    "game_theory_strategy": "clever, brisk strategic game-theory thriller narration",
    "debt_cycle_machine": "clear, steady macro-cycle analytical documentary drama narration",
    "hotline_drama": "cinematic, grounded modern urban investigative radio drama narration, restrained and vivid",
}

_NATURAL_ZH_PODCAST_DOMAINS: frozenset[str] = frozenset({
    "finance_podcast",
    "hotline_roundtable",
    "hotline_express",
})

# Real-human multi-guest chatroom podcasts: NEVER inject Chinese stage-direction acting prefixes
# (which override real-human anchor cadence into theatrical AI-announcer prosody!). Keep ONLY
# genuine paralinguistic point events ([light chuckle], [sighs], [short pause]) and [whispers].
_CHATROOM_PODCAST_DOMAINS: frozenset[str] = frozenset({
    "hotline_roundtable",
    "hotline_express",
})


def translate_cue_to_drama3_input(
    cue: TimelineCue,
    profile: VoiceProfile | None = None,
    *,
    attempt: int = 1,
    use_phoneme_pins: bool = False,
    domain: str = "xianxia",
) -> str:
    """Translate an `EpisodeCueSheet` dialogue `TimelineCue` into Fish Audio Drama 3 acting syntax.

    - `attempt == 1`: Full multi-segment natural-language acting directions (`[...]`), paralinguistic
      point events (`[sighs]`, `[sharp inhale]`), and paired prosody spans (`<whisper>…</whisper>`,
      `<forceful>…</forceful>`, `<slow>…</slow>`), plus domain-aware polyphone disambiguation.
      In `hotline_roundtable` / `hotline_express` chatroom mode, strips ALL stage-direction adjective
      tags and preserves ONLY organic paralinguistic events (`[light chuckle]`, `[sighs]`, `[short pause]`)
      so real-human studio reference anchors carry 100% authentic conversational rhythm.
    - `attempt == 2`: Simplified single leading emotion bracket (or clean text for natural zh podcasts) for retry.
    - `attempt >= 3`: Zero-tag plain phonetic text (guaranteed 0% tag-reading fallback).
    """
    lang = cue.language_code or (profile.language_code if profile is not None else "") or "zh"
    is_zh_podcast = (domain in _NATURAL_ZH_PODCAST_DOMAINS) and (lang != "en")
    is_chatroom_podcast = (domain in _CHATROOM_PODCAST_DOMAINS) and (lang != "en")
    source_tagged = cue.tts_text if (cue.tts_text and not use_phoneme_pins) else cue.text
    phonetic_tagged = _apply_drama3_phonetics(
        source_tagged,
        use_phoneme_pins=use_phoneme_pins,
        domain=domain,
        language_code=lang,
    )
    all_tags, plain_spoken = extract_tags_and_spoken_text(phonetic_tagged)

    if attempt >= 3 or not plain_spoken:
        return plain_spoken

    role_tier = profile.tier if profile is not None else "recurring"
    is_villain = role_tier == "antagonist"

    if attempt == 2:
        if not all_tags:
            return plain_spoken
        first_tag = all_tags[0].lower().strip()
        if first_tag in DRAMA3_POINT_EVENTS:
            return f"{DRAMA3_POINT_EVENTS[first_tag]} {plain_spoken}"
        if is_zh_podcast:
            return plain_spoken
        brief, _ = DRAMA3_TAG_MAP.get(first_tag, ("calm, natural dramatic delivery", ""))
        return f"[{brief}] {plain_spoken}"

    # Attempt 1: Full segment-aware Drama 3 acting prompt
    clauses = split_tagged_clauses(phonetic_tagged)
    if not clauses:
        return plain_spoken

    rendered_parts: list[str] = []
    for seg_idx, (tags, clause_text) in enumerate(clauses):
        point_tokens: list[str] = []
        style_briefs: list[str] = []
        xml_span = ""

        for raw_t in tags:
            t = raw_t.lower().strip()
            if t in ("laughs", "laughing"):
                point_tokens.append("[cold laugh]" if is_villain else "[light chuckle]")
                continue
            if t in DRAMA3_POINT_EVENTS:
                point_tokens.append(DRAMA3_POINT_EVENTS[t])
                continue
            if is_chatroom_podcast:
                # Preserve only whisper/soft intimacy; drop all theatrical acting adjectives
                if t in ("whispers", "whispering"):
                    xml_span = xml_span or "whisper"
                continue
            if is_zh_podcast:
                if t in FINANCE_PODCAST_ZH_MICRO_MAP:
                    zh_brief, span_candidate = FINANCE_PODCAST_ZH_MICRO_MAP[t]
                    if zh_brief and zh_brief not in style_briefs:
                        style_briefs.append(zh_brief)
                    if span_candidate and not xml_span:
                        xml_span = span_candidate
                continue
            if t in DRAMA3_TAG_MAP:
                brief, span_candidate = DRAMA3_TAG_MAP[t]
                if brief not in style_briefs:
                    style_briefs.append(brief)
                if span_candidate and not xml_span:
                    xml_span = span_candidate

        # Inject subtle stability/space acting cues on the opening clause when appropriate (never force announcer tone on zh_podcast)
        if seg_idx == 0:
            if lang == "en" and not style_briefs and cue.role_id.startswith("buffett"):
                style_briefs.append("clear, brisk prime-age Midwestern investor voice, warm and folksy")
            elif domain not in _NATURAL_ZH_PODCAST_DOMAINS:
                if cue.stability == 1.0 and not style_briefs:
                    style_briefs.append("solemn, measured broadcast gravity" if domain == "hotline_drama" else "solemn, ancient monotone resonance")
                    xml_span = xml_span or "slow"
                elif cue.acoustic_space == "memory_echo" and not style_briefs:
                    style_briefs.append("distant, solemn memory voice")
                elif domain == "hotline_drama" and cue.role_id == "female_elder" and not style_briefs:
                    style_briefs.append("dignified, weathered elderly Chinese woman, warm measured cadence")
                    xml_span = xml_span or "slow"
                elif not style_briefs and role_tier == "narrator":
                    if domain == "liaozhai_horror":
                        style_briefs.append("eerie, midnight classical Chinese folklore suspense narration")
                    elif domain == "cosmic_horror":
                        style_briefs.append("chilling, restrained 1920s investigative cosmic horror narration")
                    elif domain == "hayek_economics":
                        style_briefs.append("warm, lucid 1944 historical intellectual drama narration")
                    elif domain == "monte_cristo_drama":
                        style_briefs.append("sweeping, cinematic 19th-century European gothic revenge drama narration")
                    elif domain == "wealth_of_nations":
                        style_briefs.append("warm, witty, lucid 18th-century Scottish Enlightenment historical drama narration")
                    elif domain == "free_to_choose":
                        style_briefs.append("crisp, warm, incisive 1980 Chicago documentary intellectual drama narration")
                    elif domain == "keynes_1936":
                        style_briefs.append("reflective, lucid 1936 Cambridge interwar historical drama narration")
                    elif domain in _ECON_FINANCE_NARRATOR_BRIEFS:
                        style_briefs.append(_ECON_FINANCE_NARRATOR_BRIEFS[domain])
                    else:
                        style_briefs.append("steady, cinematic Xianxia narration")

        prefix_items: list[str] = []
        if style_briefs:
            combined_brief = "; ".join(style_briefs[:2])
            prefix_items.append(f"[{combined_brief}]")
        prefix_items.extend(point_tokens)

        wrapped_clause = f"<{xml_span}>{clause_text}</{xml_span}>" if xml_span else clause_text
        if prefix_items:
            rendered_parts.append(f"{' '.join(prefix_items)} {wrapped_clause}")
        else:
            rendered_parts.append(wrapped_clause)

    return " ".join(rendered_parts)


def trim_edge_silence_wav(
    wav_path: Path,
    *,
    threshold_dbfs: float = -48.0,
    keep_head_ms: float = 65.0,
    keep_tail_ms: float = 115.0,
    min_duration_s: float = 0.35,
) -> float:
    """Trim excess leading/trailing dead air on a 16-bit PCM WAV without touching interior pauses.

    Autoregressive audio LLMs (`fishaudio/drama-3`) occasionally emit 0.5s-1.5s of trailing silence
    before EOS; trimming only the outer edges preserves exact `gap_after_s` pacing in the 3-bus mixer.
    Returns final duration in seconds.
    """
    with wave.open(str(wav_path), "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    if sampwidth != 2 or nframes == 0:
        return nframes / max(sr, 1)

    samples = array("h")
    samples.frombytes(raw)
    thresh_amp = max(16, int(32767.0 * (10.0 ** (threshold_dbfs / 20.0))))

    # Scan in 10ms windows from left and right edges
    win_frames = max(1, sr // 100)
    total_frames = len(samples) // channels
    min_frames = int(min_duration_s * sr)
    if total_frames <= min_frames:
        return total_frames / sr

    first_active = 0
    for f in range(0, total_frames, win_frames):
        end_f = min(total_frames, f + win_frames)
        chunk = samples[f * channels : end_f * channels]
        if chunk and max(abs(x) for x in chunk) >= thresh_amp:
            first_active = f
            break

    last_active = total_frames
    for f in range(total_frames, 0, -win_frames):
        start_f = max(0, f - win_frames)
        chunk = samples[start_f * channels : f * channels]
        if chunk and max(abs(x) for x in chunk) >= thresh_amp:
            last_active = f
            break

    if last_active <= first_active:
        return total_frames / sr

    head_pad = int((keep_head_ms / 1000.0) * sr)
    tail_pad = int((keep_tail_ms / 1000.0) * sr)
    trim_start = max(0, first_active - head_pad)
    trim_end = min(total_frames, last_active + tail_pad)
    if trim_end - trim_start < min_frames:
        trim_end = min(total_frames, trim_start + min_frames)

    if trim_start == 0 and trim_end == total_frames:
        return total_frames / sr

    trimmed = samples[trim_start * channels : trim_end * channels]
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(trimmed.tobytes())
    return (trim_end - trim_start) / sr


_CJK_COUNT_RE = re.compile(r"[\u4e00-\u9fff]")
_MAJOR_SENT_SPLIT_RE = re.compile(r"(?<=[。！？；…])\s*")
_MINOR_CLAUSE_SPLIT_RE = re.compile(r"(?<=[，、：])\s*")
_EN_MAJOR_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_EN_MINOR_CLAUSE_SPLIT_RE = re.compile(r"(?<=[,;:])\s+")


def split_cue_into_subcues_for_drama3(
    cue: TimelineCue,
    max_cjk_chars: int = 105,
    *,
    max_en_words: int = 65,
    domain: str = "xianxia",
) -> list[TimelineCue]:
    """Split long dialogue/narrator cues at natural sentence boundaries so Drama 3 never hits its token cap.

    Fish Audio Drama 3 operates at ~21.53 codec frames/s (`1536` tokens = `71.33s`, vocoder max ~`139s`).
    Splitting cues > `max_cjk_chars` (~35-38s at 2.8 chars/s) or > `max_en_words` (~25-28s at 2.5 words/s)
    into sentence-aligned sub-cues guarantees >2.5x token headroom, crisper prosody, and 100% tail-completeness.
    """
    tags, spoken = extract_tags_and_spoken_text(cue.text)
    cjk_count = len(_CJK_COUNT_RE.findall(spoken))
    is_english = cue.language_code == "en" or (cjk_count == 0 and bool(spoken.strip()))

    # Inherit leading style tag(s) (excluding one-shot point laughs/sighs) across sub-cues for consistent tone
    inherited_tags = [
        f"[{t}]"
        for t in tags[:2]
        if t.lower().strip() not in DRAMA3_POINT_EVENTS and t.lower().strip() not in ("laughs", "laughing")
    ]
    prefix = " ".join(inherited_tags)
    clean_body = _TAG_TOKEN_RE.sub("", cue.text).strip()

    if is_english:
        en_words = spoken.split()
        if len(en_words) <= max_en_words:
            return [cue]
        raw_sents = [s.strip() for s in _EN_MAJOR_SENT_SPLIT_RE.split(clean_body) if s.strip()]
        atomic_units_en: list[str] = []
        for sent in raw_sents:
            if len(sent.split()) <= max_en_words:
                atomic_units_en.append(sent)
            else:
                clauses = [c.strip() for c in _EN_MINOR_CLAUSE_SPLIT_RE.split(sent) if c.strip()]
                atomic_units_en.extend(clauses if len(clauses) > 1 else [sent])

        chunks_en: list[str] = []
        cur_en = ""
        for unit in atomic_units_en:
            candidate = f"{cur_en} {unit}".strip() if cur_en else unit
            if cur_en and len(candidate.split()) > max_en_words:
                chunks_en.append(cur_en)
                cur_en = unit
            else:
                cur_en = candidate
        if cur_en:
            if (
                chunks_en
                and len(cur_en.split()) < 8
                and len(f"{chunks_en[-1]} {cur_en}".split()) <= max_en_words + 12
            ):
                chunks_en[-1] = f"{chunks_en[-1]} {cur_en}"
            else:
                chunks_en.append(cur_en)

        if len(chunks_en) <= 1:
            return [cue]

        subcues_en: list[TimelineCue] = []
        for idx, chunk_txt in enumerate(chunks_en, 1):
            tagged_txt = f"{prefix} {chunk_txt}".strip() if prefix else chunk_txt
            subcues_en.append(
                TimelineCue(
                    cue_id=f"{cue.cue_id}_pt{idx}",
                    act_id=cue.act_id,
                    kind="dialogue",
                    role_id=cue.role_id,
                    speaker_name=cue.speaker_name,
                    language_code=cue.language_code or "en",
                    text=tagged_txt,
                    tts_text=None,
                    stability=cue.stability,
                    acoustic_space=cue.acoustic_space,
                    gap_after_s=cue.gap_after_s if idx == len(chunks_en) else 0.16,
                )
            )
        return subcues_en

    if cjk_count <= max_cjk_chars:
        return [cue]

    raw_sents = [s.strip() for s in _MAJOR_SENT_SPLIT_RE.split(clean_body) if s.strip()]

    # Sub-split any single ultra-long sentence on commas/colons
    atomic_units: list[str] = []
    for sent in raw_sents:
        if len(_CJK_COUNT_RE.findall(sent)) <= max_cjk_chars:
            atomic_units.append(sent)
        else:
            clauses = [c.strip() for c in _MINOR_CLAUSE_SPLIT_RE.split(sent) if c.strip()]
            atomic_units.extend(clauses if len(clauses) > 1 else [sent])

    chunks: list[str] = []
    cur = ""
    for unit in atomic_units:
        candidate = (cur + unit) if cur else unit
        if cur and len(_CJK_COUNT_RE.findall(candidate)) > max_cjk_chars:
            chunks.append(cur)
            cur = unit
        else:
            cur = candidate
    if cur:
        if chunks and len(_CJK_COUNT_RE.findall(cur)) < 14 and len(_CJK_COUNT_RE.findall(chunks[-1] + cur)) <= max_cjk_chars + 20:
            chunks[-1] = chunks[-1] + cur
        else:
            chunks.append(cur)

    if len(chunks) <= 1:
        return [cue]

    subcues: list[TimelineCue] = []
    for idx, chunk_txt in enumerate(chunks, 1):
        tagged_txt = f"{prefix} {chunk_txt}".strip() if prefix else chunk_txt
        phonetic_txt = apply_domain_polyphone_overrides(tagged_txt, domain=domain)
        subcues.append(
            TimelineCue(
                cue_id=f"{cue.cue_id}_pt{idx}",
                act_id=cue.act_id,
                kind="dialogue",
                role_id=cue.role_id,
                speaker_name=cue.speaker_name,
                language_code=cue.language_code,
                text=tagged_txt,
                tts_text=phonetic_txt if phonetic_txt != tagged_txt else None,
                stability=cue.stability,
                acoustic_space=cue.acoustic_space,
                gap_after_s=cue.gap_after_s if idx == len(chunks) else 0.16,
            )
        )
    return subcues


def concat_pcm_wavs(wav_paths: list[Path], out_wav: Path, *, pause_ms: float = 160.0) -> Path:
    """Concatenate multiple PCM16 WAV segments (same format, e.g. 48kHz stereo) with natural breath pauses."""
    if not wav_paths:
        raise ValueError("concat_pcm_wavs requires at least 1 wav_path")
    if len(wav_paths) == 1:
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wav_paths[0], out_wav)
        return out_wav

    combined = array("h")
    channels = 2
    sr = 48000
    for idx, wp in enumerate(wav_paths):
        with wave.open(str(wp), "rb") as wf:
            if idx == 0:
                channels = wf.getnchannels()
                sr = wf.getframerate()
            raw = wf.readframes(wf.getnframes())
        seg = array("h")
        seg.frombytes(raw)
        if idx > 0 and pause_ms > 0:
            pad_frames = int(round((pause_ms / 1000.0) * sr))
            combined.extend([0] * (pad_frames * channels))
        combined.extend(seg)

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(combined.tobytes())
    return out_wav


def convert_to_drama3_anchor_wav(src_audio: Path, dst_wav: Path) -> float:
    """Convert a character reference take into clean 44.1kHz mono PCM16 WAV leveled to -16 LUFS."""
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    dur = probe_duration_seconds(src_audio)
    af = "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11" if dur >= 1.5 else "highpass=f=70,alimiter=limit=0.89:level=disabled"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(src_audio),
            "-af",
            af,
            "-ar",
            str(DRAMA3_ANCHOR_SAMPLE_RATE),
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(dst_wav),
        ],
        check=True,
    )
    return round(probe_duration_seconds(dst_wav), 3)


def export_colab_96gb_bundle(
    *,
    registry_path: Path,
    cue_sheets_dir: Path,
    anchor_specs: dict[str, dict[str, str]],
    output_bundle_dir: Path,
    motifs_source_dir: Path | None = None,
    bgm_source_dir: Path | None = None,
    pipeline_repo_root: Path | None = None,
    studio_scripts: list[Path] | None = None,
    zip_output_path: Path | None = None,
) -> dict[str, Any]:
    """Assemble a self-contained 96GB Colab Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL Studio bundle.

    `anchor_specs` maps `role_id -> {"audio_path": "/path/to/clean.wav", "anchor_text": "exact verbatim text"}`.
    """
    registry = VoiceCastingRegistry.load(registry_path)
    output_bundle_dir.mkdir(parents=True, exist_ok=True)

    anchors_dir = output_bundle_dir / "voice_anchors"
    motifs_dir = output_bundle_dir / "motifs"
    bgm_dir = output_bundle_dir / "bgm_cache"
    scripts_out_dir = output_bundle_dir / "cue_sheets"
    auditions_out_dir = output_bundle_dir / "auditions"
    for d in (anchors_dir, motifs_dir, bgm_dir, scripts_out_dir, auditions_out_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Export clean 44.1kHz mono PCM16 voice anchors + voice_cast_drama3.json
    cast_entries: dict[str, dict[str, Any]] = {}
    for role_id, spec in sorted(anchor_specs.items()):
        prof = registry.resolve_role(role_id)
        src_audio = Path(spec["audio_path"])
        if not src_audio.is_file():
            raise FileNotFoundError(f"Missing voice anchor audio for {role_id}: {src_audio}")
        anchor_text = spec["anchor_text"].strip()
        if not anchor_text:
            raise ValueError(f"Empty anchor_text for {role_id}")

        rel_wav = f"voice_anchors/{role_id}.wav"
        dst_wav = output_bundle_dir / rel_wav
        dur_s = convert_to_drama3_anchor_wav(src_audio, dst_wav)
        cast_entries[role_id] = {
            "role_id": role_id,
            "display_name": prof.display_name if prof else role_id,
            "tier": prof.tier if prof else "recurring",
            "gender": prof.gender if prof else "male",
            "age_group": prof.age_group if prof else "adult",
            "language_code": prof.language_code if prof else "zh",
            "vocal_register": prof.vocal_register if prof else "",
            "source_voice_name": spec.get("source_voice_name") or (prof.library_voice_name if prof else ""),
            "anchor_wav": rel_wav,
            "anchor_duration_s": dur_s,
            "anchor_text": anchor_text,
            "default_stability": prof.default_stability if prof else 0.5,
        }

    voice_cast_json = output_bundle_dir / "voice_cast_drama3.json"
    voice_cast_payload = {
        "project_id": registry.project_id,
        "project_title": registry.project_title,
        "domain": registry.domain,
        "engine": "fishaudio/drama-3 + OpenMOSS-Team/MOSS-SoundEffect-v2.0 + ACE-Step/acestep-v15-xl-turbo-diffusers",
        "exported_at": utc_now_iso(),
        "anchor_sample_rate_hz": DRAMA3_ANCHOR_SAMPLE_RATE,
        "role_count": len(cast_entries),
        "characters": cast_entries,
    }
    voice_cast_json.write_text(json.dumps(voice_cast_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 2. Copy registry (with relative motif paths normalized) & all EpisodeCueSheet JSONs
    exported_motifs: dict[str, str] = {}
    for motif_id, motif in registry.sonic_motifs.items():
        candidates: list[Path] = []
        if motif.cached_file:
            candidates.append(Path(motif.cached_file))
        if motifs_source_dir:
            candidates.extend(sorted(motifs_source_dir.glob(f"{motif_id}*.wav")))
        src_m = next((p for p in candidates if p.is_file()), None)
        if src_m is not None:
            dst_m = motifs_dir / f"{motif_id}.wav"
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(src_m),
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    "-c:a",
                    "pcm_s16le",
                    str(dst_m),
                ],
                check=True,
            )
            motif.cached_file = f"motifs/{motif_id}.wav"
            exported_motifs[motif_id] = motif.cached_file

    registry.save(output_bundle_dir / "voice_casting_registry.json")

    copied_episodes: list[str] = []
    candidate_jsons = sorted(
        set(cue_sheets_dir.glob("E*.json")) | set(cue_sheets_dir.glob("AUDITION*.json")),
        key=lambda p: p.name,
    )
    for cs_path in candidate_jsons:
        cs = EpisodeCueSheet.load(cs_path)
        if cs.mode == "audition_pack":
            cs.save(auditions_out_dir / cs_path.name)
            continue
        for act in cs.acts:
            if bgm_source_dir and act.cached_bgm_file:
                bgm_src = Path(act.cached_bgm_file)
                if not bgm_src.is_file():
                    bgm_src = bgm_source_dir / bgm_src.name
                if bgm_src.is_file():
                    dst_b = bgm_dir / bgm_src.name
                    if not dst_b.exists():
                        shutil.copy2(bgm_src, dst_b)
                    act.cached_bgm_file = f"bgm_cache/{bgm_src.name}"
        # Also auto-bind E001/E002 pre-existing studio BGM stems if present in bgm_source_dir
        if bgm_source_dir:
            ep_lower = cs.episode_id.lower()
            for act in cs.acts:
                if not act.cached_bgm_file:
                    matches = sorted(bgm_source_dir.glob(f"{ep_lower}_bgm_{act.act_id}*.wav"))
                    if matches:
                        dst_b = bgm_dir / matches[0].name
                        if not dst_b.exists():
                            shutil.copy2(matches[0], dst_b)
                        act.cached_bgm_file = f"bgm_cache/{matches[0].name}"
        cs.save(scripts_out_dir / cs_path.name)
        copied_episodes.append(cs.episode_id)

    # 3. Embed `src/aigc_audio_pipeline` package + studio runner scripts for zero-git offline NVMe execution
    if pipeline_repo_root is not None:
        pkg_src = pipeline_repo_root / "src" / "aigc_audio_pipeline"
        pkg_dst = output_bundle_dir / "src" / "aigc_audio_pipeline"
        if pkg_dst.exists():
            shutil.rmtree(pkg_dst)
        shutil.copytree(pkg_src, pkg_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    for script_path in studio_scripts or []:
        if script_path.is_file():
            shutil.copy2(script_path, output_bundle_dir / script_path.name)

    zip_size_mb = 0.0
    if zip_output_path is not None:
        zip_output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for fpath in sorted(output_bundle_dir.rglob("*")):
                if fpath.is_file():
                    zf.write(fpath, fpath.relative_to(output_bundle_dir).as_posix())
        zip_size_mb = round(zip_output_path.stat().st_size / (1024 * 1024), 2)

    return {
        "bundle_dir": str(output_bundle_dir),
        "zip_path": str(zip_output_path) if zip_output_path else "",
        "zip_size_mb": zip_size_mb,
        "role_count": len(cast_entries),
        "motif_count": len(exported_motifs),
        "episode_count": len(copied_episodes),
    }
