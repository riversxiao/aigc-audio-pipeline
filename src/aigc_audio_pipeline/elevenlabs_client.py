"""Unified ElevenLabs API client (eleven_v3 TTS, SFX v3, Music v2.5, Scribe v3 STT, Shared Voices)."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any

from .models import ALLOWED_V3_STABILITIES

DEFAULT_BASE_URL = "https://api.elevenlabs.io"
PERSISTENT_KEY_PATHS: tuple[Path, ...] = (
    Path.home() / ".gemini" / "config" / "aigc_audio.env",
    Path.home() / ".config" / "aigc-audio-pipeline" / "credentials.env",
)


class ElevenLabsError(RuntimeError):
    def __init__(self, status_code: int, message: str, body: str = "") -> None:
        super().__init__(f"ElevenLabs HTTP {status_code}: {message}")
        self.status_code = status_code
        self.body = body


def resolve_elevenlabs_api_key(explicit_key: str | None = None) -> str | None:
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()
    for env_name in ("ELEVENLABS_API_KEY", "XI_API_KEY"):
        val = os.environ.get(env_name, "").strip()
        if val:
            return val
    for path in PERSISTENT_KEY_PATHS:
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                if k in ("ELEVENLABS_API_KEY", "XI_API_KEY") and v:
                    return v
    return None


def normalize_to_wav_48k(src_audio: Path, dst_wav: Path, channels: int = 1) -> Path:
    """Convert raw API audio response to 48kHz 16-bit PCM WAV without trimming a single sample."""
    dst_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(src_audio),
        "-vn",
        "-ar",
        "48000",
        "-ac",
        str(channels),
        "-c:a",
        "pcm_s16le",
        str(dst_wav),
    ]
    subprocess.run(cmd, check=True)
    return dst_wav


def probe_duration_seconds(audio_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out)


@dataclass
class SynthesisResult:
    wav_path: Path
    duration_s: float
    output_format_used: str
    character_cost: int | None
    request_id: str
    from_cache: bool = False


class ElevenLabsClient:
    """Zero-dependency HTTP client implementing Playbook rules & tier-safe fallbacks."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        cache_dir: Path | None = None,
        timeout_s: float = 180.0,
    ) -> None:
        resolved = resolve_elevenlabs_api_key(api_key)
        if not resolved:
            raise ValueError(
                "Missing ELEVENLABS_API_KEY. Set ELEVENLABS_API_KEY in environment or "
                f"save ELEVENLABS_API_KEY=... in {PERSISTENT_KEY_PATHS[0]}."
            )
        self._api_key = resolved
        self.base_url = base_url.rstrip("/")
        self.cache_dir = cache_dir
        self.timeout_s = timeout_s

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        raw_body: bytes | None = None,
        content_type: str | None = None,
        retries: int = 2,
    ) -> tuple[bytes, dict[str, str]]:
        url = f"{self.base_url}{path}"
        if query:
            clean_q: list[tuple[str, str]] = []
            for k, v in query.items():
                if v is None:
                    continue
                if isinstance(v, (list, tuple)):
                    for item in v:
                        clean_q.append((k, str(item)))
                elif isinstance(v, bool):
                    clean_q.append((k, "true" if v else "false"))
                else:
                    clean_q.append((k, str(v)))
            if clean_q:
                url = f"{url}?{urllib.parse.urlencode(clean_q)}"

        headers: dict[str, str] = {
            "xi-api-key": self._api_key,
            "Accept": "*/*",
            "User-Agent": "aigc-audio-pipeline/0.2.0",
        }
        payload: bytes | None = raw_body
        if json_body is not None:
            payload = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif content_type:
            headers["Content-Type"] = content_type

        attempt = 0
        while True:
            req = urllib.request.Request(url, data=payload, headers=headers, method=method.upper())
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    body = resp.read()
                    resp_headers = {k.lower(): v for k, v in resp.headers.items()}
                    return body, resp_headers
            except urllib.error.HTTPError as exc:
                err_bytes = exc.read()
                err_text = err_bytes.decode("utf-8", errors="replace")
                if exc.code in (429, 500, 502, 503, 504) and attempt < retries:
                    attempt += 1
                    time.sleep(1.5 * (2**attempt))
                    continue
                raise ElevenLabsError(exc.code, err_text[:400], body=err_text) from exc

    # ------------------------------------------------------------------
    # Subscription & Voices
    # ------------------------------------------------------------------
    def get_subscription(self) -> dict[str, Any]:
        body, _ = self._request("GET", "/v1/user/subscription")
        return json.loads(body.decode("utf-8"))

    def list_my_voices(self) -> list[dict[str, Any]]:
        body, _ = self._request("GET", "/v1/voices")
        data = json.loads(body.decode("utf-8"))
        return list(data.get("voices", []))

    def search_shared_voices(
        self,
        *,
        language: str = "zh",
        locale: str | None = "zh-CN",
        gender: str | None = None,
        age: str | None = None,
        search: str | None = None,
        use_cases: list[str] | None = None,
        page_size: int = 30,
        strict_mainland: bool = True,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {
            "language": language,
            "locale": locale,
            "gender": gender,
            "age": age,
            "search": search,
            "use_cases": use_cases,
            "page_size": min(max(page_size, 1), 100),
        }
        body, _ = self._request("GET", "/v1/shared-voices", query=query)
        voices = list(json.loads(body.decode("utf-8")).get("voices", []))
        if not strict_mainland:
            return voices

        # Filter out known drifting accents per Playbook hard rule
        blocked_tokens = ("american", "australian", "british", "singapore", "taiwan", "cantonese", "hong kong", "indian")
        filtered: list[dict[str, Any]] = []
        for v in voices:
            accent = str(v.get("accent") or "").lower()
            loc = str(v.get("locale") or "").lower()
            desc = str(v.get("description") or "").lower()
            if any(tok in accent for tok in blocked_tokens):
                continue
            if loc and loc not in ("zh-cn", "zh", "cmn-hans-cn", "zh_cn"):
                continue
            if any(tok in desc for tok in ("taiwanese", "singaporean", "hong kong accent")):
                continue
            filtered.append(v)
        return filtered

    def add_shared_voice(self, public_owner_id: str, voice_id: str, new_name: str) -> dict[str, Any]:
        """Add a voice from ElevenLabs Shared Voice Library.

        Playbook hard rule: `new_name` is strictly mandatory (otherwise HTTP 422).
        """
        if not new_name or not new_name.strip():
            raise ValueError("new_name is strictly required when adding a shared voice (Playbook rule: prevents 422).")
        body, _ = self._request(
            "POST",
            f"/v1/voices/add/{public_owner_id}/{voice_id}",
            json_body={"new_name": new_name.strip()},
        )
        return json.loads(body.decode("utf-8"))

    # ------------------------------------------------------------------
    # Dialogue Synthesis (eleven_v3)
    # ------------------------------------------------------------------
    def synthesize_dialogue(
        self,
        *,
        voice_id: str,
        text: str,
        output_wav: Path,
        stability: float = 0.5,
        similarity_boost: float = 0.85,
        language_code: str = "zh",
        model_id: str = "eleven_v3",
        preferred_formats: tuple[str, ...] = ("wav_48000", "mp3_44100_192", "mp3_44100_128"),
        use_cache: bool = True,
    ) -> SynthesisResult:
        if stability not in ALLOWED_V3_STABILITIES:
            raise ValueError(
                f"eleven_v3 requires discrete stability in {ALLOWED_V3_STABILITIES}, got {stability!r}."
            )

        cache_path: Path | None = None
        if use_cache and self.cache_dir is not None:
            digest = hashlib.sha256(
                json.dumps(
                    {
                        "kind": "tts",
                        "voice_id": voice_id,
                        "model_id": model_id,
                        "language_code": language_code,
                        "text": text,
                        "stability": stability,
                        "similarity_boost": similarity_boost,
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                ).encode("utf-8")
            ).hexdigest()[:24]
            cache_path = self.cache_dir / "tts" / f"{digest}.wav"
            if cache_path.is_file():
                output_wav.parent.mkdir(parents=True, exist_ok=True)
                output_wav.write_bytes(cache_path.read_bytes())
                return SynthesisResult(
                    wav_path=output_wav,
                    duration_s=probe_duration_seconds(output_wav),
                    output_format_used="cache_wav_48000",
                    character_cost=0,
                    request_id="cached",
                    from_cache=True,
                )

        # Playbook hard rule: never send previous_text or next_text to eleven_v3
        payload: dict[str, Any] = {
            "text": text,
            "model_id": model_id,
            "language_code": language_code,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
            },
        }

        last_err: Exception | None = None
        for fmt in preferred_formats:
            try:
                audio_bytes, headers = self._request(
                    "POST",
                    f"/v1/text-to-speech/{voice_id}",
                    query={"output_format": fmt},
                    json_body=payload,
                )
                ext = ".wav" if fmt.startswith("wav") else ".mp3"
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = Path(tmp.name)
                try:
                    normalize_to_wav_48k(tmp_path, output_wav, channels=1)
                finally:
                    tmp_path.unlink(missing_ok=True)

                if cache_path is not None:
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_bytes(output_wav.read_bytes())

                char_cost_raw = headers.get("character-cost") or headers.get("x-character-count")
                char_cost = int(char_cost_raw) if char_cost_raw and char_cost_raw.isdigit() else None
                return SynthesisResult(
                    wav_path=output_wav,
                    duration_s=probe_duration_seconds(output_wav),
                    output_format_used=fmt,
                    character_cost=char_cost,
                    request_id=headers.get("request-id", ""),
                    from_cache=False,
                )
            except ElevenLabsError as exc:
                last_err = exc
                # Tier restriction on output_format returns 400 or 403 -> fall back to next format
                if exc.status_code in (400, 403) and ("output_format" in exc.body or "tier" in exc.body.lower()):
                    continue
                raise
        assert last_err is not None
        raise last_err

    # ------------------------------------------------------------------
    # Sound Effects (eleven_text_to_sound_v3)
    # ------------------------------------------------------------------
    def generate_sfx(
        self,
        *,
        prompt: str,
        output_wav: Path,
        duration_seconds: float | None = 3.0,
        prompt_influence: float = 0.55,
        loop: bool = False,
        model_id: str = "eleven_text_to_sound_v3",
        preferred_formats: tuple[str, ...] = ("wav_48000", "mp3_44100_192", "mp3_44100_128"),
        use_cache: bool = True,
    ) -> SynthesisResult:
        cache_path: Path | None = None
        if use_cache and self.cache_dir is not None:
            digest = hashlib.sha256(
                json.dumps(
                    {
                        "kind": "sfx",
                        "model_id": model_id,
                        "prompt": prompt,
                        "duration_seconds": duration_seconds,
                        "prompt_influence": prompt_influence,
                        "loop": loop,
                    },
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()[:24]
            cache_path = self.cache_dir / "sfx" / f"{digest}.wav"
            if cache_path.is_file():
                output_wav.parent.mkdir(parents=True, exist_ok=True)
                output_wav.write_bytes(cache_path.read_bytes())
                return SynthesisResult(
                    wav_path=output_wav,
                    duration_s=probe_duration_seconds(output_wav),
                    output_format_used="cache_wav_48000",
                    character_cost=0,
                    request_id="cached",
                    from_cache=True,
                )

        payload: dict[str, Any] = {
            "text": prompt,
            "model_id": model_id,
            "prompt_influence": prompt_influence,
            "loop": loop,
        }
        if duration_seconds is not None:
            payload["duration_seconds"] = round(min(max(duration_seconds, 0.5), 30.0), 2)

        last_err: Exception | None = None
        for fmt in preferred_formats:
            # ElevenLabs docs note: wav_48000 is for non-looping effects
            if loop and fmt.startswith("wav"):
                continue
            try:
                audio_bytes, headers = self._request(
                    "POST",
                    "/v1/sound-generation",
                    query={"output_format": fmt},
                    json_body=payload,
                )
                ext = ".wav" if fmt.startswith("wav") else ".mp3"
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = Path(tmp.name)
                try:
                    normalize_to_wav_48k(tmp_path, output_wav, channels=2)
                finally:
                    tmp_path.unlink(missing_ok=True)

                if cache_path is not None:
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_bytes(output_wav.read_bytes())

                char_cost_raw = headers.get("character-cost")
                char_cost = int(char_cost_raw) if char_cost_raw and char_cost_raw.isdigit() else None
                return SynthesisResult(
                    wav_path=output_wav,
                    duration_s=probe_duration_seconds(output_wav),
                    output_format_used=fmt,
                    character_cost=char_cost,
                    request_id=headers.get("request-id", ""),
                    from_cache=False,
                )
            except ElevenLabsError as exc:
                last_err = exc
                if exc.status_code in (400, 403) and ("output_format" in exc.body or "tier" in exc.body.lower()):
                    continue
                raise
        assert last_err is not None
        raise last_err

    # ------------------------------------------------------------------
    # Music Composition (music_v2_5)
    # ------------------------------------------------------------------
    def compose_music(
        self,
        *,
        prompt: str,
        output_wav: Path,
        duration_seconds: float = 60.0,
        force_instrumental: bool = True,
        model_id: str = "music_v2_5",
        preferred_formats: tuple[str, ...] = ("mp3_48000_192", "auto"),
        use_cache: bool = True,
    ) -> SynthesisResult:
        music_length_ms = int(round(min(max(duration_seconds * 1000.0, 3000.0), 600000.0)))
        cache_path: Path | None = None
        if use_cache and self.cache_dir is not None:
            digest = hashlib.sha256(
                json.dumps(
                    {
                        "kind": "music",
                        "model_id": model_id,
                        "prompt": prompt,
                        "music_length_ms": music_length_ms,
                        "force_instrumental": force_instrumental,
                    },
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()[:24]
            cache_path = self.cache_dir / "music" / f"{digest}.wav"
            if cache_path.is_file():
                output_wav.parent.mkdir(parents=True, exist_ok=True)
                output_wav.write_bytes(cache_path.read_bytes())
                return SynthesisResult(
                    wav_path=output_wav,
                    duration_s=probe_duration_seconds(output_wav),
                    output_format_used="cache_wav_48000",
                    character_cost=0,
                    request_id="cached",
                    from_cache=True,
                )

        # API rule: never send `seed` alongside `prompt` (causes HTTP 422)
        payload: dict[str, Any] = {
            "prompt": prompt,
            "music_length_ms": music_length_ms,
            "model_id": model_id,
            "force_instrumental": force_instrumental,
        }

        last_err: Exception | None = None
        for fmt in preferred_formats:
            try:
                audio_bytes, headers = self._request(
                    "POST",
                    "/v1/music",
                    query={"output_format": fmt},
                    json_body=payload,
                )
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = Path(tmp.name)
                try:
                    normalize_to_wav_48k(tmp_path, output_wav, channels=2)
                finally:
                    tmp_path.unlink(missing_ok=True)

                if cache_path is not None:
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_bytes(output_wav.read_bytes())

                return SynthesisResult(
                    wav_path=output_wav,
                    duration_s=probe_duration_seconds(output_wav),
                    output_format_used=fmt,
                    character_cost=None,
                    request_id=headers.get("song-id") or headers.get("request-id", ""),
                    from_cache=False,
                )
            except ElevenLabsError as exc:
                last_err = exc
                if exc.status_code in (400, 403, 422) and fmt != "auto":
                    continue
                raise
        assert last_err is not None
        raise last_err

    # ------------------------------------------------------------------
    # Speech-to-Text QA (scribe_v3 / scribe_v2)
    # ------------------------------------------------------------------
    def transcribe_asr(
        self,
        audio_path: Path,
        *,
        language_code: str = "zh",
        secondary_language_codes: tuple[str, ...] = ("en",),
        model_candidates: tuple[str, ...] = ("scribe_v3", "scribe_v2"),
    ) -> dict[str, Any]:
        file_bytes = audio_path.read_bytes()
        last_err: Exception | None = None
        for model_id in model_candidates:
            boundary = f"----AigcAudioBoundary{uuid.uuid4().hex}"
            fields: list[tuple[str, str]] = [
                ("model_id", model_id),
                ("language_code", language_code),
                ("tag_audio_events", "true"),
            ]
            if model_id == "scribe_v3":
                for sec in secondary_language_codes:
                    fields.append(("secondary_language_codes", sec))

            parts: list[bytes] = []
            for name, val in fields:
                parts.append(
                    f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode("utf-8")
                )
            parts.append(
                (
                    f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
                    f'filename="{audio_path.name}"\r\nContent-Type: audio/wav\r\n\r\n'
                ).encode("utf-8")
                + file_bytes
                + b"\r\n"
            )
            parts.append(f"--{boundary}--\r\n".encode("utf-8"))
            raw_body = b"".join(parts)

            try:
                body, _ = self._request(
                    "POST",
                    "/v1/speech-to-text",
                    raw_body=raw_body,
                    content_type=f"multipart/form-data; boundary={boundary}",
                )
                result = json.loads(body.decode("utf-8"))
                result["_asr_model_used"] = model_id
                return result
            except ElevenLabsError as exc:
                last_err = exc
                if exc.status_code in (400, 404, 422) and model_id != model_candidates[-1]:
                    continue
                raise
        assert last_err is not None
        raise last_err
