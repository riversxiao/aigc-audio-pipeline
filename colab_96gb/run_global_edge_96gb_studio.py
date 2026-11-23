#!/usr/bin/env python3
"""《跨境底牌：硅深暗战》/ Global Edge · Colab 96GB 双语多变体商战广播剧本地推理与母带引擎 (v1.0.0).

核心工业级特性（100% 零商业语音 API 费用、0% 合成 TTS 锚点）：
1. 【8 角色 `v2_real_human_studio` 真人棚录干声锚点】：5 位核心常驻（林沉同声源英中双语、周默深圳科技高管、
   Victoria Vance 硅谷美音、Alistair Finch 伦敦 RP 英音、Claire Sterling 纽约法务）+ 3 位受控国际客串，
   生产模式强制执行 `validate_production_voice_cast()` 门禁。
2. 【`business_english_drama` 商战双语转译与 `0.80x` 确定性缓存复用】：显式传入 `domain="business_english_drama"`
   彻底隔离仙侠多音字与古风旁白回退；Drama 3 始终以 `1.0x` 自然语速合成并缓存（缓存键使用锚点 WAV 真实 SHA-256
   且严禁包含 `playback_rate` 与 `acoustic_space`），Act 5 慢速拆解由 `mixer.py` 经 pitch-preserving FFmpeg `atempo=0.800`
   确定性拉伸，实现跨变体/跨速高缓存命中。
3. 【变体感知剧集解析器】：支持 `AUDITION` / `AUDITION_GLOBAL_EDGE`、`E001_VA`..`E001_VD`、`E001A`..`E001D`、
   `E001_VARIANTS`、`E001-E024`、`ALL`，杜绝 `E001` 与 `E001_VA` 前缀冲突。
4. 【HBO 商战纯器乐 OST 护栏 + MOSS 纯拟音护栏 + 互让防 OOM】：`enrich_business_drama_bgm_prompt()` 彻底清洗
   古风/民乐/人声词并保持幂等；`MOSS-SoundEffect-v2.0` 与 `ACE-Step 1.5 XL` 均采用 `CUDA_VISIBLE_DEVICES=""`
   前置显存探测保护与互让重试机制。
5. 【CPU `faster-whisper-small-int8` 双脚本零显存质检 + 48kHz `-16 LUFS` 三母线母带】：直接对接 M1
   `evaluate_dialogue_qa(..., canonical_prompt=..., language_code=...)` 与 `master_episode_three_bus()`，
   输出 48kHz 立体声 WAV + MP3 + 零重叠中英双行 `.srt` + `.json` 清单 + 原子 `.done` 标记。
"""

from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any
import wave

os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

STUDIO_DIR = Path(__file__).resolve().parent
for _candidate_src in (STUDIO_DIR / "src", STUDIO_DIR.parent / "src"):
    if (_candidate_src / "aigc_audio_pipeline").is_dir() and str(_candidate_src) not in sys.path:
        sys.path.insert(0, str(_candidate_src))
if str(STUDIO_DIR) not in sys.path:
    sys.path.insert(0, str(STUDIO_DIR))

from aigc_audio_pipeline.batch_queue import measure_ebur128  # noqa: E402
from aigc_audio_pipeline.drama3_adapter import (  # noqa: E402
    concat_pcm_wavs,
    estimate_drama3_max_new_tokens,
    split_cue_into_subcues_for_drama3,
    translate_cue_to_drama3_input,
    trim_edge_silence_wav,
)
from aigc_audio_pipeline.mixer import master_episode_three_bus  # noqa: E402
from aigc_audio_pipeline.models import (  # noqa: E402
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
    utc_now_iso,
)
from aigc_audio_pipeline.qa import evaluate_dialogue_qa, inspect_audio_peak_dbfs  # noqa: E402

DEFAULT_DOMAIN = "business_english_drama"
EPISODE_ID_RE = re.compile(r"^(E\d{3}(?:_V[A-Z0-9]+|[A-Z])?)(?:_|\.|$)")

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_LATIN_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

_MOSS_WORKER_CODE = r"""
import gc, json, os, subprocess, sys
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

def _probe_free_vram_gb() -> float:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return float(out.splitlines()[0].strip()) / 1024.0
    except Exception:
        return 0.0

free_gb = _probe_free_vram_gb()
use_cuda = free_gb >= 9.5
if not use_cuda:
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import soundfile as sf
import torch
from moss_soundeffect_v2 import MossSoundEffectPipeline

if not use_cuda:
    torch.set_num_threads(min(32, max(4, (os.cpu_count() or 16) - 4)))

model_id = sys.argv[1]
pipe = None
if use_cuda and torch.cuda.is_available():
    try:
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        print(f"[MOSS-SoundEffect v2.0] Loading {model_id} on CUDA ({dtype}, free={free_gb:.1f}GB)...", flush=True)
        pipe = MossSoundEffectPipeline.from_pretrained(model_id, torch_dtype=dtype, device="cuda")
    except Exception as exc:
        print(f"[MOSS-SoundEffect v2.0] CUDA load fallback to CPU ({exc})", flush=True)
        gc.collect()
        torch.cuda.empty_cache()
        pipe = None
        use_cuda = False

if pipe is None:
    print(f"[MOSS-SoundEffect v2.0] Loading {model_id} on multi-core CPU (0 MB VRAM, free={free_gb:.2f}GB)...", flush=True)
    pipe = MossSoundEffectPipeline.from_pretrained(model_id, torch_dtype=torch.float32, device="cpu")

sr = int(getattr(pipe, "sample_rate", 48000))
print("__RPC__:" + json.dumps({"status": "ready", "sample_rate": sr, "device": "cuda" if use_cuda else "cpu"}), flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if req.get("cmd") == "quit":
        break
    try:
        seconds = float(np.clip(float(req["seconds"]), 0.8, 28.0))
        steps = int(req.get("steps", 100 if use_cuda else 28))
        cfg = float(req.get("cfg", 4.0))
        with torch.inference_mode():
            audio = pipe(
                prompt=req["prompt"],
                seconds=seconds,
                num_inference_steps=steps,
                cfg_scale=cfg,
            )
        wav = audio.detach().cpu()
        del audio
        gc.collect()
        if use_cuda and torch.cuda.is_available():
            torch.cuda.empty_cache()
        if wav.ndim == 3:
            wav = wav[0]
        elif wav.ndim == 1:
            wav = wav.unsqueeze(0)
        wav_np = wav.T.float().numpy()
        peak = float(np.max(np.abs(wav_np))) if wav_np.size else 0.0
        if peak > 1e-4:
            wav_np = wav_np / peak * 0.86
        out_p = req["out_path"]
        os.makedirs(os.path.dirname(out_p) or ".", exist_ok=True)
        sf.write(out_p, wav_np, sr, subtype="PCM_16")
        print("__RPC__:" + json.dumps({"status": "ok", "out_path": out_p}), flush=True)
    except Exception as exc:
        gc.collect()
        print("__RPC__:" + json.dumps({"status": "error", "error": str(exc)}), flush=True)
"""

_ACESTEP_WORKER_CODE = r"""
import gc, json, os, subprocess, sys
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

def _probe_free_vram_gb() -> float:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return float(out.splitlines()[0].strip()) / 1024.0
    except Exception:
        return 0.0

free_gb = _probe_free_vram_gb()
can_touch_cuda = free_gb >= 5.0
if not can_touch_cuda:
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import soundfile as sf
import torch
from diffusers import AceStepPipeline

if not can_touch_cuda:
    torch.set_num_threads(min(32, max(4, (os.cpu_count() or 16) - 4)))

model_id = sys.argv[1]
dtype = (
    (torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16)
    if (can_touch_cuda and torch.cuda.is_available())
    else torch.float32
)
print(f"[ACE-Step 1.5 XL] Loading {model_id} ({dtype}, free={free_gb:.2f}GB)...", flush=True)
pipe = AceStepPipeline.from_pretrained(model_id, torch_dtype=dtype)
if hasattr(pipe, "vae"):
    if hasattr(pipe.vae, "enable_tiling"):
        pipe.vae.enable_tiling()
    if hasattr(pipe.vae, "enable_slicing"):
        pipe.vae.enable_slicing()

mode = "cpu"
if can_touch_cuda and torch.cuda.is_available():
    if free_gb >= 14.0:
        try:
            pipe = pipe.to("cuda")
            mode = "cuda"
        except Exception:
            gc.collect()
            torch.cuda.empty_cache()
    if mode == "cpu":
        try:
            if free_gb >= 8.0 and hasattr(pipe, "enable_model_cpu_offload"):
                pipe.enable_model_cpu_offload()
                mode = "model_cpu_offload"
            elif hasattr(pipe, "enable_sequential_cpu_offload"):
                pipe.enable_sequential_cpu_offload()
                mode = "sequential_cpu_offload"
        except Exception as exc:
            print(f"[ACE-Step 1.5 XL] Offload fallback to CPU ({exc})", flush=True)

if mode == "cpu":
    pipe = pipe.to("cpu", dtype=torch.float32)

sr = int(getattr(pipe, "sample_rate", 48000))
print("__RPC__:" + json.dumps({"status": "ready", "sample_rate": sr, "mode": mode}), flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if req.get("cmd") == "quit":
        break
    try:
        dur_s = float(max(12.0, min(float(req["duration_s"]), 120.0 if mode != "cpu" else 42.0)))
        with torch.inference_mode():
            out = pipe(
                prompt=req["prompt"],
                lyrics=req.get("lyrics") or "[Instrumental]",
                audio_duration=dur_s,
                vocal_language=req.get("vocal_language", "unknown"),
                guidance_scale=float(req.get("guidance_scale", 1.0)),
            )
        audio = out.audios[0].T.detach().cpu().float().numpy()
        del out
        gc.collect()
        if can_touch_cuda and torch.cuda.is_available():
            torch.cuda.empty_cache()
        peak = float(np.max(np.abs(audio))) if audio.size else 0.0
        if peak > 1e-4:
            audio = audio / peak * 0.88
        out_p = req["out_path"]
        os.makedirs(os.path.dirname(out_p) or ".", exist_ok=True)
        sf.write(out_p, audio, sr, subtype="PCM_16")
        print("__RPC__:" + json.dumps({"status": "ok", "out_path": out_p}), flush=True)
    except Exception as exc:
        gc.collect()
        print("__RPC__:" + json.dumps({"status": "error", "error": str(exc)}), flush=True)
"""


def probe_duration_seconds(audio_path: Path) -> float:
    """Pure-stdlib `ffprobe` + `wave` duration helper (zero commercial API client imports)."""
    if not audio_path.is_file():
        return 0.0
    try:
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=15,
        ).strip()
        if out and out != "N/A":
            dur = float(out.splitlines()[0].strip())
            if math.isfinite(dur) and dur > 0.0:
                return dur
    except Exception:
        pass
    try:
        with wave.open(str(audio_path), "rb") as wf:
            rate = wf.getframerate()
            if rate > 0:
                return wf.getnframes() / float(rate)
    except Exception:
        pass
    return 0.0


def detect_gpu_profile() -> tuple[str, float, tuple[int, int]]:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,compute_cap", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        first = out.splitlines()[0]
        name_s, mem_mib_s, cc_s = [p.strip() for p in first.split(",")[:3]]
        cc_parts = cc_s.split(".")
        cc = (int(cc_parts[0]), int(cc_parts[1]) if len(cc_parts) > 1 else 0)
        return name_s, float(mem_mib_s) / 1024.0, cc
    except Exception:
        return "CPU / Offline Mode", 0.0, (0, 0)


def _sha24(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:24]


def _file_sha256_prefix(path: Path, length: int = 16) -> str:
    if not path.is_file():
        return "missing"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:length]


def build_dialogue_tts_cache_key(
    engine: str,
    domain: str,
    role_id: str,
    anchor_sha256: str,
    prompt_a1: str,
    max_tokens: int,
) -> str:
    """Compute deterministic Drama 3 1.0x TTS cache key (strictly excludes playback_rate & acoustic_space)."""
    return _sha24(
        {
            "engine": engine,
            "domain": domain,
            "role_id": role_id,
            "anchor_sha256": anchor_sha256,
            "prompt_v2": prompt_a1,
            "max_tok": int(max_tokens),
        }
    )


def _write_offline_voiced_wav(
    out_wav: Path,
    *,
    duration_s: float,
    base_freq_hz: float = 165.0,
    amp: float = 0.30,
    sample_rate: int = 48000,
    is_bgm: bool = False,
) -> Path:
    """Generate clean 48kHz stereo multi-harmonic audio for offline dry-run 3-bus FFmpeg mastering."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    nframes = max(int(0.5 * sample_rate), int(round(duration_s * sample_rate)))
    tile_frames = sample_rate  # 1.0s periodic tile keeps pure-stdlib synthesis ultra-fast
    if is_bgm:
        harmonics = ((base_freq_hz, 0.55), (base_freq_hz * 1.5, 0.25), (base_freq_hz * 2.0, 0.20))
    else:
        harmonics = (
            (base_freq_hz, 0.26),
            (base_freq_hz * 2.0, 0.30),
            (base_freq_hz * 3.0, 0.22),
            (base_freq_hz * 5.0, 0.13),
            (base_freq_hz * 7.0, 0.06),
            (base_freq_hz * 10.0, 0.03),
        )
    norm_scale = sum(w for _, w in harmonics)
    tile = array("h", [0]) * (tile_frames * 2)
    two_pi = 2.0 * math.pi
    for i in range(tile_frames):
        t = i / sample_rate
        env = 0.85 + 0.15 * math.sin(two_pi * 1.0 * t) if is_bgm else (0.55 + 0.35 * math.sin(two_pi * 3.0 * t) + 0.10 * math.cos(two_pi * 7.0 * t))
        sig = sum(w * math.sin(two_pi * f * t) for f, w in harmonics) / norm_scale
        val = int(max(-32767, min(32767, round(32767.0 * amp * env * sig))))
        tile[2 * i] = val
        tile[2 * i + 1] = val

    full_repeats, remainder = divmod(nframes, tile_frames)
    buf = array("h")
    for _ in range(full_repeats):
        buf.extend(tile)
    if remainder > 0:
        buf.extend(tile[: remainder * 2])

    fade_frames = min(int(0.025 * sample_rate), nframes // 4)
    for i in range(fade_frames):
        gain = 0.5 * (1.0 - math.cos(math.pi * i / max(1, fade_frames)))
        buf[2 * i] = int(round(buf[2 * i] * gain))
        buf[2 * i + 1] = int(round(buf[2 * i + 1] * gain))
        tail_idx = nframes - 1 - i
        buf[2 * tail_idx] = int(round(buf[2 * tail_idx] * gain))
        buf[2 * tail_idx + 1] = int(round(buf[2 * tail_idx + 1] * gain))

    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(buf.tobytes())
    return out_wav


class SubprocessJsonWorker:
    """Persistent GPU/CPU model worker running inside its own isolated Python virtualenv."""

    def __init__(self, label: str, python_bin: str, inline_code: str, model_id: str) -> None:
        self.label = label
        self.python_bin = python_bin
        self.inline_code = inline_code
        self.model_id = model_id
        self.proc: subprocess.Popen[str] | None = None

    def _wait_rpc(self) -> dict[str, Any]:
        assert self.proc is not None and self.proc.stdout is not None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                rc = self.proc.poll()
                raise RuntimeError(f"[{self.label}] 进程意外退出 (rc={rc})")
            if line.startswith("__RPC__:"):
                return json.loads(line[len("__RPC__:") :].strip())
            print(f"  {line}", end="", flush=True)

    def start(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            return
        print(f"🚀 [{self.label}] 加载模型权重: {self.model_id} ...", flush=True)
        env = os.environ.copy()
        env["TORCHDYNAMO_DISABLE"] = "1"
        env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        env["PYTHONUNBUFFERED"] = "1"
        self.proc = subprocess.Popen(
            [self.python_bin, "-u", "-c", self.inline_code, self.model_id],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
        info = self._wait_rpc()
        if info.get("status") != "ready":
            raise RuntimeError(f"[{self.label}] 初始化失败: {info}")
        print(f"✅ [{self.label}] 常驻就绪 (sample_rate={info.get('sample_rate')}Hz)", flush=True)

    def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.proc is None or self.proc.poll() is not None:
            self.start()
        assert self.proc is not None and self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        resp = self._wait_rpc()
        if resp.get("status") != "ok":
            raise RuntimeError(f"[{self.label}] 推理异常: {resp.get('error')}")
        return resp

    def close(self) -> None:
        if self.proc is None:
            return
        try:
            if self.proc.poll() is None and self.proc.stdin is not None:
                self.proc.stdin.write(json.dumps({"cmd": "quit"}) + "\n")
                self.proc.stdin.flush()
                self.proc.wait(timeout=10)
        except Exception:
            try:
                self.proc.kill()
                self.proc.wait(timeout=5)
            except Exception:
                pass
        finally:
            self.proc = None


class Drama3ServerClient:
    """Manages `sgl-omni serve` (`fishaudio/drama-3` or `fishaudio/drama-3-int4`) on localhost."""

    def __init__(
        self,
        *,
        sgl_bin: str,
        model_repo: str,
        port: int = 8000,
        co_resident_96g: bool = True,
        enable_ras: bool = True,
        log_path: Path,
    ) -> None:
        self.sgl_bin = sgl_bin
        self.model_repo = model_repo
        self.port = port
        self.co_resident_96g = co_resident_96g
        self.enable_ras = enable_ras
        self.log_path = log_path
        self.base_url = f"http://127.0.0.1:{port}"
        self.proc: subprocess.Popen[Any] | None = None
        self._log_fh: Any = None

    def _budget_flags(self) -> list[str]:
        if self.co_resident_96g and not self.model_repo.endswith("-int4"):
            return [
                "--tts_engine.gpu_memory_fraction",
                "0.46",
                "--vocoder.gpu_memory_fraction",
                "0.08",
                "--preprocessing.total_reserve_bytes",
                "4GiB",
            ]
        if self.co_resident_96g:
            return [
                "--tts_engine.gpu_memory_fraction",
                "0.34",
                "--vocoder.gpu_memory_fraction",
                "0.08",
                "--preprocessing.total_reserve_bytes",
                "4GiB",
            ]
        return [
            "--tts_engine.gpu_memory_fraction",
            "0.62",
            "--vocoder.gpu_memory_fraction",
            "0.12",
            "--preprocessing.total_reserve_bytes",
            "3GiB",
        ]

    def _supports_reference_sampling_flag(self) -> bool:
        try:
            help_proc = subprocess.run(
                [self.sgl_bin, "serve", "--help"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            combined = (help_proc.stdout or "") + "\n" + (help_proc.stderr or "")
            return "reference_sampling" in combined
        except Exception:
            return False

    def is_healthy(self) -> bool:
        import urllib.request

        for ep in ("/health", "/v1/models"):
            try:
                with urllib.request.urlopen(f"{self.base_url}{ep}", timeout=3.0) as resp:
                    if 200 <= resp.status < 300:
                        return True
            except Exception:
                continue
        return False

    def start(self, timeout_s: int = 1500) -> None:
        if self.is_healthy():
            print(f"✅ [Drama 3] 检测到 {self.base_url} 已在线，直接复用。", flush=True)
            return

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.sgl_bin,
            "serve",
            "--model-path",
            self.model_repo,
            "--port",
            str(self.port),
            *self._budget_flags(),
        ]
        if self.enable_ras and self._supports_reference_sampling_flag():
            cmd.extend(
                [
                    "--tts_engine.factory.reference_sampling",
                    "true",
                    "--tts_engine.factory.reference_sampling_fallback",
                    "ras",
                ]
            )
            print("✨ [Drama 3] 已启用 Reference Sampling + RAS 高表现力采样", flush=True)

        print(f"🚀 [Drama 3] 启动 SGLang-Omni 服务: {' '.join(cmd)}", flush=True)
        env = os.environ.copy()
        env["TORCHDYNAMO_DISABLE"] = "1"
        sgl_bin_dir = str(Path(self.sgl_bin).resolve().parent)
        env["PATH"] = f"{sgl_bin_dir}:/usr/local/cuda/bin:{env.get('PATH', '')}"
        self._log_fh = self.log_path.open("a", encoding="utf-8")
        self.proc = subprocess.Popen(
            cmd,
            stdout=self._log_fh,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            env=env,
        )

        t0 = time.time()
        tick = 0
        while time.time() - t0 < timeout_s:
            if self.proc.poll() is not None:
                tail = ""
                if self.log_path.is_file():
                    tail = "\n".join(self.log_path.read_text(errors="replace").splitlines()[-45:])
                raise RuntimeError(f"[Drama 3] SGLang-Omni 启动异常退出 (rc={self.proc.returncode}):\n{tail}")
            if self.is_healthy():
                print(f"✅ [Drama 3] 服务就绪 ({time.time() - t0:.1f}s) -> {self.base_url}", flush=True)
                return
            if tick > 0 and tick % 10 == 0:
                print(f"   ⏳ [Drama 3] 等待权重加载与 CUDA Graph 预热 ({int(time.time() - t0)}s)...", flush=True)
            tick += 1
            time.sleep(3.0)
        raise TimeoutError(f"[Drama 3] 等待 SGLang-Omni 就绪超时 ({timeout_s}s)")

    def synthesize(
        self,
        *,
        drama3_input: str,
        anchor_wav: Path,
        anchor_text: str,
        out_wav: Path,
        max_new_tokens: int = 2048,
        timeout_s: int = 300,
    ) -> Path:
        import urllib.error
        import urllib.request

        if not self.is_healthy():
            print("⚠️ [Drama 3] 服务连接中断，正在自动拉起恢复...", flush=True)
            self.start()

        payload = json.dumps(
            {
                "model": self.model_repo,
                "input": drama3_input,
                "response_format": "wav",
                "references": [
                    {
                        "audio_path": str(anchor_wav.resolve()),
                        "text": anchor_text,
                    }
                ],
                "temperature": 1.0,
                "top_p": 0.9,
                "max_new_tokens": max_new_tokens,
            },
            ensure_ascii=False,
        ).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/audio/speech",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                audio_bytes = resp.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:600]
            raise RuntimeError(f"[Drama 3] HTTP {exc.code}: {detail}") from exc

        if len(audio_bytes) < 512:
            raise RuntimeError(f"[Drama 3] 返回音频过短 ({len(audio_bytes)} bytes)")

        tmp_raw = out_wav.with_suffix(".raw_d3.wav")
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        tmp_raw.write_bytes(audio_bytes)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(tmp_raw),
                "-ar",
                "48000",
                "-ac",
                "2",
                "-c:a",
                "pcm_s16le",
                str(out_wav),
            ],
            check=True,
        )
        tmp_raw.unlink(missing_ok=True)
        trim_edge_silence_wav(out_wav)
        return out_wav

    def close(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=12)
            except Exception:
                self.proc.kill()
        self.proc = None
        if self._log_fh is not None:
            try:
                self._log_fh.close()
            except Exception:
                pass
            self._log_fh = None


class BilingualWhisperQA:
    """Zero-VRAM CPU int8 `faster-whisper` ASR gate calibrated for Global Edge bilingual corporate drama."""

    def __init__(self, enabled: bool = True, model_size: str = "small") -> None:
        self.enabled = enabled
        self._model: Any = None
        self._available: bool | None = None
        self.model_size = model_size

    def transcribe(
        self,
        wav_path: Path,
        *,
        language_code: str = "zh",
        spoken_text: str = "",
    ) -> str | None:
        if not self.enabled or self._available is False:
            return None
        if self._model is None:
            try:
                from faster_whisper import WhisperModel  # type: ignore[import-not-found]

                print(
                    f"🔍 [双语 ASR 质检门] 加载 CPU int8 faster-whisper ({self.model_size}, 0 MB 显存占用)...",
                    flush=True,
                )
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                self._available = True
            except Exception as exc:
                print(f"ℹ️ [双语 ASR 质检门] faster-whisper 未安装 ({exc})，启用纯信号与语速边界质检。", flush=True)
                self._available = False
                return None

        try:
            import numpy as np  # type: ignore[import-not-found]

            raw_pcm = subprocess.check_output(
                [
                    "ffmpeg",
                    "-nostdin",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(wav_path),
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    "-f",
                    "f32le",
                    "pipe:1",
                ]
            )
            audio_16k = np.frombuffer(raw_pcm, dtype=np.float32).copy()
            _, clean_spoken = extract_tags_and_spoken_text(spoken_text) if spoken_text else ([], "")
            cjk_n = len(_CJK_RE.findall(clean_spoken))
            use_en = (language_code == "en") or (
                language_code == "zh-en" and bool(clean_spoken.strip()) and cjk_n == 0
            )
            if use_en:
                segments, _ = self._model.transcribe(
                    audio_16k,
                    language="en",
                    beam_size=2,
                    vad_filter=True,
                    initial_prompt=(
                        "NovaEdge Technologies, NovaEdge Glass, NovaDock, Lin Chen, Zhou Mo, "
                        "Victoria Vance, Alistair Finch, Claire Sterling, Rajiv Menon, Wei-Ling Tan, "
                        "Henrik Lindqvist, Sand Hill Road, Selfridges, phantom number, not a cash loss, "
                        "income statement, capital-efficient, throughput, eating into budgets, upside, GDPR, BOM cost."
                    ),
                )
                return " ".join(seg.text.strip() for seg in segments if seg.text.strip()).strip()

            zh_prompt = (
                "以下是现代跨国商战广播剧《跨境底牌：硅深暗战》中英双语对白与内心独白："
                "林沉、周默、NovaEdge、NovaEdge Glass、NovaDock、沙丘路、可转债重估、端侧推理、"
                "phantom number、income statement、capital-efficient、BOM cost、term sheet、upside。"
            )
            segments, _ = self._model.transcribe(
                audio_16k,
                language="zh",
                beam_size=2,
                vad_filter=(len(audio_16k) > 36000),
                initial_prompt=zh_prompt,
            )
            parts = [seg.text.strip() for seg in segments if seg.text.strip()]
            if not parts:
                return ""
            joined = parts[0]
            for seg in parts[1:]:
                if joined[-1].isascii() and joined[-1].isalnum() and seg[0].isascii() and seg[0].isalnum():
                    joined = f"{joined} {seg}"
                else:
                    joined = f"{joined}{seg}"
            return joined.strip()
        except Exception as exc:
            print(f"⚠️ [双语 ASR 质检门] 单句转写回退纯语速质检 ({exc})", flush=True)
            return None


def _episode_sort_key(ep_id: str) -> tuple[int, int, str]:
    num = int(ep_id[1:4])
    suffix = ep_id[4:]
    # Base E001 before letter variants (E001A) and _V variants (E001_VA)
    tier = 0 if not suffix else (1 if not suffix.startswith("_") else 2)
    return (num, tier, suffix)


def resolve_global_edge_targets(
    cue_dir: Path,
    auditions_dir: Path,
    spec: str,
) -> list[tuple[str, Path]]:
    """Resolve `--episodes` specs (`AUDITION`, `E001_VA..VD`, `E001_VARIANTS`, `E001-E024`, `ALL`)."""
    ep_files: dict[str, Path] = {}
    if cue_dir.is_dir():
        for p in sorted(cue_dir.glob("E*.json")):
            m = EPISODE_ID_RE.match(p.name)
            if m:
                ep_files[m.group(1)] = p

    aud_candidates: list[Path] = []
    if auditions_dir.is_dir():
        aud_candidates.extend(sorted(auditions_dir.glob("AUDITION*.json")))
    if cue_dir.is_dir() and cue_dir.resolve() != auditions_dir.resolve():
        aud_candidates.extend(sorted(cue_dir.glob("AUDITION*.json")))

    targets: list[tuple[str, Path]] = []
    seen: set[str] = set()

    def _add(label: str, path: Path) -> None:
        if label not in seen:
            seen.add(label)
            targets.append((label, path))

    tokens = [t.strip() for t in (spec or "").split(",") if t.strip()]
    if not tokens:
        raise ValueError("Empty --episodes specification.")

    for token in tokens:
        upper = token.upper()

        if upper in ("AUDITION", "AUDITION_GLOBAL_EDGE"):
            if not aud_candidates:
                raise FileNotFoundError(
                    f"未在 {auditions_dir} 或 {cue_dir} 找到 AUDITION*.json 试听台本"
                )
            _add("AUDITION_GLOBAL_EDGE", aud_candidates[0])
            continue

        if upper == "ALL":
            if not aud_candidates and not ep_files:
                raise FileNotFoundError(
                    f"未在 {auditions_dir} 或 {cue_dir} 找到任何 AUDITION*.json 或 E*.json 剧集台本"
                )
            if aud_candidates:
                _add("AUDITION_GLOBAL_EDGE", aud_candidates[0])
            for eid in sorted(ep_files, key=_episode_sort_key):
                _add(eid, ep_files[eid])
            continue

        m_variants = re.match(r"^E?(\d{1,3})_VARIANTS$", upper)
        if m_variants:
            prefix = f"E{int(m_variants.group(1)):03d}"
            var_re = re.compile(rf"^{re.escape(prefix)}(?:_V[A-Z0-9]+|[A-Z])$")
            matched = [eid for eid in sorted(ep_files, key=_episode_sort_key) if var_re.match(eid)]
            if not matched:
                raise FileNotFoundError(
                    f"未在 {cue_dir} 找到 {prefix} 变体台本（如 {prefix}_VA..{prefix}_VD）"
                )
            for eid in matched:
                _add(eid, ep_files[eid])
            continue

        m_range = re.match(r"^E?(\d{1,3})\s*-\s*E?(\d{1,3})$", upper)
        if m_range:
            start_n, end_n = int(m_range.group(1)), int(m_range.group(2))
            if start_n > end_n:
                raise ValueError(f"无效剧集区间: {token!r}")
            matched = [
                eid
                for eid in sorted(ep_files, key=_episode_sort_key)
                if start_n <= int(eid[1:4]) <= end_n
            ]
            if not matched:
                raise FileNotFoundError(
                    f"未在 {cue_dir} 找到区间 E{start_n:03d}-E{end_n:03d} 内的任何台本 JSON"
                )
            for eid in matched:
                _add(eid, ep_files[eid])
            continue

        m_single = re.match(r"^E?(\d{1,3})(?:(_V[A-Z0-9]+)|([A-Z]))?$", upper)
        if m_single:
            num = int(m_single.group(1))
            suffix = m_single.group(2) or m_single.group(3) or ""
            eid = f"E{num:03d}{suffix}"
            if eid not in ep_files:
                raise FileNotFoundError(f"未在 {cue_dir} 找到台本 {eid} JSON")
            _add(eid, ep_files[eid])
            continue

        raise ValueError(
            f"无法解析 --episodes 参数片段: {token!r}（支持: AUDITION, E001_VA..VD, E001_VARIANTS, E001-E024, ALL）"
        )

    return targets


def find_existing_episode_mp3s(episode_id: str, search_dirs: list[Path]) -> list[Path]:
    """Collision-safe MP3 existence lookup distinguishing `E001` vs `E001_VA..VD` vs `E001A..D`."""
    found: list[Path] = []
    for cdir in search_dirs:
        if not cdir.is_dir():
            continue
        for p in sorted(cdir.glob("*.mp3")):
            if episode_id.startswith("AUDITION"):
                if p.name.startswith(f"{episode_id}_") or p.name.startswith(f"{episode_id}."):
                    found.append(p)
            else:
                m = EPISODE_ID_RE.match(p.name)
                if m and m.group(1) == episode_id:
                    found.append(p)
    return found


def check_bilingual_speaking_rate_ok(cue: TimelineCue, duration_s: float) -> tuple[bool, str]:
    """Language-aware speaking-rate gate evaluated on raw 1.0x Drama 3 stems."""
    _, spoken = extract_tags_and_spoken_text(cue.text)
    cjk_n = len(_CJK_RE.findall(spoken))
    en_words = _LATIN_WORD_RE.findall(spoken)

    if cue.language_code == "en" or cjk_n == 0:
        w_n = len(en_words)
        if w_n < 4:
            return (0.35 <= duration_s <= 6.5), f"short_en_dur={duration_s:.2f}s"
        sec_per_word = duration_s / w_n
        if sec_per_word < 0.14:
            return False, f"英文语速过快/疑似吞词 ({sec_per_word:.3f}s/word, dur={duration_s:.2f}s, words={w_n})"
        if sec_per_word > 0.92:
            return False, f"英文语速过慢/疑似拖尾 ({sec_per_word:.3f}s/word, dur={duration_s:.2f}s, words={w_n})"
        return True, f"{sec_per_word:.3f}s/word"

    effective_units = cjk_n + 2.2 * len(en_words)
    if effective_units < 4.0:
        return (0.30 <= duration_s <= 8.0), f"short_zh_dur={duration_s:.2f}s"
    sec_per_unit = duration_s / effective_units
    if sec_per_unit < 0.085:
        return False, f"语速过快/疑似吞字 ({sec_per_unit:.3f}s/unit, dur={duration_s:.2f}s)"
    if sec_per_unit > 0.72:
        return False, f"语速过慢/疑似拖尾 ({sec_per_unit:.3f}s/unit, dur={duration_s:.2f}s)"
    return True, f"{sec_per_unit:.3f}s/unit"


_NEGATIVE_PREFIX_RE = re.compile(r"^\s*(?:strictly\s+)?(?:no|without|zero|non-)\b", re.IGNORECASE)

_HUMAN_VOCAL_WORD_RE = re.compile(
    r"\b(?:cough(?:ing|s)?|groan(?:ing|s)?|grunt(?:ing|s)?|sigh(?:ing|s)?|"
    r"scream(?:ing|s)?|sob(?:bing|s)?|whisper(?:ing|s)?|laugh(?:ter|ing|s)?|"
    r"voices?|vocals?|speech|talking|chatter)\b",
    re.IGNORECASE,
)

_HUMAN_VOCAL_CLAUSE_RE = re.compile(
    r"(?:,?\s*(?:accompanied by|with|and)\s+(?:(?!\b(?:accompanied by|with|and)\b)[^,.])*?"
    r"\b(?:cough(?:ing|s)?|groan(?:ing|s)?|grunt(?:ing|s)?|sigh(?:ing|s)?|"
    r"scream(?:ing|s)?|sob(?:bing|s)?|whisper(?:ing|s)?|laugh(?:ter|ing|s)?|"
    r"voices?|vocals?|speech|talking|chatter)\b[^,.]*)",
    re.IGNORECASE,
)


def sanitize_moss_foley_prompt(prompt: str) -> str:
    """Sanitize MOSS-SoundEffect-v2.0 prompt to pure corporate foley with zero human vocal leakage."""
    raw_clauses = [c.strip(" .") for c in re.split(r"[,;]+", prompt or "") if c.strip(" .")]
    kept: list[str] = []
    for clause in raw_clauses:
        if _NEGATIVE_PREFIX_RE.match(clause):
            kept.append(clause)
            continue
        sub_cleaned = _HUMAN_VOCAL_CLAUSE_RE.sub("", clause).strip(" ,.")
        if not sub_cleaned or _HUMAN_VOCAL_WORD_RE.search(sub_cleaned):
            continue
        kept.append(sub_cleaned)

    cleaned = ", ".join(kept).strip(" ,.")
    if not cleaned:
        cleaned = "Subtle frameless glass boardroom latch click and quiet executive desk ambient foley"
    lower = cleaned.lower()
    if "pure foley" not in lower and "no human voice" not in lower:
        cleaned = f"{cleaned}, pure foley, no human voice"
    elif "no human voice" not in lower:
        cleaned = f"{cleaned}, no human voice"
    elif "pure foley" not in lower:
        cleaned = f"{cleaned}, pure foley"
    return cleaned


_FORBIDDEN_BGM_TRADITIONAL_RE = re.compile(
    r"\b(?:xianxia|wuxia|cultivation|guqin|guzheng|erhu|dizi|pipa|flutes?|suona|shakuhachi|xiao|"
    r"traditional\s+(?:chinese|asian|eastern)(?:\s+(?:folk\s+)?(?:instruments?|music|melody|melodies|style|sound))?|"
    r"(?:chinese|asian|oriental)\s+folk(?:\s+(?:instruments?|music|melody|melodies))?|"
    r"ancient\s+chinese)\b",
    re.IGNORECASE,
)

_POSITIVE_VOCAL_OR_POP_SUBCLAUSE_RE = re.compile(
    r"\b(?:with|and|featuring|plus)\s+[^,;.]*?\b(?:vocals?|singing|singer|sung|choir|choral|lyrics?|rap|chant(?:ing)?|pop\s+drums?|trap\s+beats?|edm(?:\s+drops?)?)\b[^,;.]*",
    re.IGNORECASE,
)

_POSITIVE_VOCAL_OR_POP_TOKEN_RE = re.compile(
    r"\b(?:vocals?|singing|singer|sung|choir|choral|lyrics?|rap|chant(?:ing)?|pop\s+drums?|trap\s+beats?|edm(?:\s+drops?)?)\b",
    re.IGNORECASE,
)

_HBO_CHAMBER_MARKER_RE = re.compile(
    r"\b(?:cello|viola|chamber\s+strings|dark\s+chamber|felt\s+piano|grand\s+piano|rhodes|upright\s+bass|"
    r"acoustic\s+bass|analog\s+(?:pulse|ticking)|underscore|low\s+strings)\b",
    re.IGNORECASE,
)


def enrich_business_drama_bgm_prompt(raw_prompt: str) -> str:
    """Enforce HBO corporate-thriller purely-instrumental OST guardrails cleanly and idempotently.

    - Strips ANY Xianxia / traditional Chinese / Asian folk instrument mentions (both positive & negative)
      so the returned prompt NEVER contains `xianxia`, `guqin`, `guzheng`, `erhu`, `flute`, `dizi`, or `pipa`.
    - Strips positive vocal/singing/choir/pop-drum/trap/EDM requests.
    - Ensures minimalist dark chamber strings, felt piano, and tense subtle analog pulse when missing.
    - Appends concise purely-instrumental negative guardrails idempotently (`enrich(enrich(p)) == enrich(p)`).
    """
    raw_clauses = [c.strip(" .") for c in re.split(r"[,;]+", raw_prompt or "") if c.strip(" .")]
    kept: list[str] = []
    seen_lower: set[str] = set()

    for clause in raw_clauses:
        if _FORBIDDEN_BGM_TRADITIONAL_RE.search(clause):
            continue
        is_neg = bool(_NEGATIVE_PREFIX_RE.match(clause))
        if not is_neg:
            clause = _POSITIVE_VOCAL_OR_POP_SUBCLAUSE_RE.sub("", clause).strip(" ,.")
            if not clause or _POSITIVE_VOCAL_OR_POP_TOKEN_RE.search(clause):
                continue
        norm_key = " ".join(clause.lower().split())
        if norm_key and norm_key not in seen_lower:
            seen_lower.add(norm_key)
            kept.append(clause)

    joined = ", ".join(kept)
    if not joined:
        kept = [
            "Minimalist HBO corporate thriller underscore",
            "muted dark chamber strings",
            "sparse felt piano chords",
            "tense subtle analog pulse",
        ]
    elif not _HBO_CHAMBER_MARKER_RE.search(joined):
        kept.extend(["minimalist dark chamber strings", "felt piano", "tense subtle analog pulse"])

    lower_all = ", ".join(kept).lower()
    guardrails: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("strictly instrumental", ("strictly instrumental", "purely instrumental")),
        ("no vocals", ("no vocals",)),
        ("no singing", ("no singing",)),
        ("no choir", ("no choir",)),
        ("no pop drums", ("no pop drums", "no drums", "no heavy drums", "no percussion")),
        ("no trap beats", ("no trap beats", "no trap beat")),
        ("no EDM drops", ("no edm drops", "no edm drop")),
    )
    for phrase, satisfied_by in guardrails:
        if not any(tok in lower_all for tok in satisfied_by):
            kept.append(phrase)
            lower_all = f"{lower_all}, {phrase.lower()}"

    return ", ".join(kept)


def canonical_global_edge_stem(cue_sheet: EpisodeCueSheet) -> str:
    clean_title = re.sub(r'[\\/:*?"<>|\s，。！？：；、“”‘’·—]+', "_", cue_sheet.title).strip("_")
    if cue_sheet.mode == "audition_pack":
        return f"{cue_sheet.episode_id}_全口音与双语飙戏试听母带"
    return f"{cue_sheet.episode_id}_{clean_title}_双语商战母带"


_OFFLINE_ROLE_FREQS: dict[str, float] = {
    "lin_chen": 124.0,
    "zhou_mo": 138.0,
    "victoria_vance": 210.0,
    "alistair_finch": 116.0,
    "claire_chen_gc": 226.0,
    "rajiv_menon": 130.0,
    "wei_ling_tan": 218.0,
    "henrik_lindqvist": 112.0,
}


def _synthesize_subcue_with_qa(
    subcue: TimelineCue,
    *,
    drama_repo: str,
    prof: Any,
    anchor_wav: Path,
    anchor_text: str,
    cache_dir: Path,
    offline_dry_run: bool,
    drama_client: Drama3ServerClient | None,
    whisper_qa: BilingualWhisperQA,
    domain: str = DEFAULT_DOMAIN,
) -> tuple[Path, str, bool]:
    eff_lang = subcue.language_code or (prof.language_code if prof is not None else "zh-en") or "zh-en"
    prompt_a1 = translate_cue_to_drama3_input(
        subcue,
        prof,
        attempt=1,
        use_phoneme_pins=False,
        domain=domain,
    )
    anchor_digest = _file_sha256_prefix(anchor_wav, length=16)
    dyn_max_tokens = estimate_drama3_max_new_tokens(prompt_a1, language_code=eff_lang)
    # Deterministically EXCLUDES `playback_rate` and `acoustic_space` so 0.80x reuses 1.0x Drama 3 stems!
    cache_key = build_dialogue_tts_cache_key(
        engine=drama_repo,
        domain=domain,
        role_id=subcue.role_id,
        anchor_sha256=anchor_digest,
        prompt_a1=prompt_a1,
        max_tokens=dyn_max_tokens,
    )
    cached_wav = cache_dir / "drama3_tts" / f"{cache_key}.wav"

    if offline_dry_run:
        if not (cached_wav.is_file() and cached_wav.stat().st_size > 1024):
            _, spoken = extract_tags_and_spoken_text(subcue.text)
            cjk_n = len(_CJK_RE.findall(spoken))
            en_w = len(_LATIN_WORD_RE.findall(spoken))
            if eff_lang == "en" or cjk_n == 0:
                est_dur = max(1.6, min(14.0, max(4, en_w) / 2.85))
            else:
                eff_units = cjk_n + 2.2 * en_w
                est_dur = max(1.6, min(14.0, max(5.0, eff_units) / 3.8))
            _write_offline_voiced_wav(
                cached_wav,
                duration_s=est_dur,
                base_freq_hz=_OFFLINE_ROLE_FREQS.get(subcue.role_id, 165.0),
                amp=0.30,
            )
        return cached_wav, prompt_a1, True

    if cached_wav.is_file() and cached_wav.stat().st_size > 1024:
        if probe_duration_seconds(cached_wav) < 68.0:
            return cached_wav, prompt_a1, True

    assert drama_client is not None
    best_wav: Path | None = None
    best_score = float("-inf")
    final_qa_passed = False
    used_prompt = prompt_a1

    for attempt in (1, 2, 3):
        cur_prompt = translate_cue_to_drama3_input(
            subcue,
            prof,
            attempt=attempt,
            use_phoneme_pins=False,
            domain=domain,
        )
        try_wav = cache_dir / "drama3_tts" / f"{cache_key}_try{attempt}.wav"
        drama_client.synthesize(
            drama3_input=cur_prompt,
            anchor_wav=anchor_wav,
            anchor_text=anchor_text,
            out_wav=try_wav,
            max_new_tokens=dyn_max_tokens,
        )
        dur_s, peak_db = inspect_audio_peak_dbfs(try_wav)
        rate_ok, rate_msg = check_bilingual_speaking_rate_ok(subcue, dur_s)
        if dur_s >= 90.0:
            rate_ok = False
            rate_msg = f"接近 token 上限 ({dur_s:.2f}s)"
        asr_txt = whisper_qa.transcribe(
            try_wav,
            language_code=eff_lang,
            spoken_text=subcue.tts_text or subcue.text,
        )

        if asr_txt is not None:
            qa_res = evaluate_dialogue_qa(
                tagged_prompt=subcue.tts_text or subcue.text,
                asr_text=asr_txt,
                duration_s=dur_s,
                peak_dbfs=peak_db,
                attempt=attempt,
                min_char_recall=0.72,
                canonical_prompt=subcue.text,
                language_code=eff_lang,
            )
            passed = qa_res.passed and rate_ok
            score = qa_res.char_recall - (0.25 if not rate_ok else 0.0) - (0.4 * len(qa_res.leaked_tags))
            reason_str = "; ".join(qa_res.reasons + ([] if rate_ok else [rate_msg]))
        else:
            passed = (dur_s >= 0.25) and (peak_db >= -45.0) and rate_ok
            score = 1.0 if passed else 0.2
            reason_str = "" if passed else f"dur={dur_s:.2f}s, peak={peak_db:.1f}dB, {rate_msg}"

        if score > best_score:
            best_score = score
            best_wav = try_wav
            used_prompt = cur_prompt
            final_qa_passed = passed

        if passed:
            break
        print(
            f"   ⚠️ [{subcue.cue_id}] 第 {attempt} 次双语质检未过 ({reason_str})，降级重抽...",
            flush=True,
        )

    assert best_wav is not None
    shutil.copy2(best_wav, cached_wav)
    for a_idx in (1, 2, 3):
        (cache_dir / "drama3_tts" / f"{cache_key}_try{a_idx}.wav").unlink(missing_ok=True)
    return cached_wav, used_prompt, final_qa_passed


def synthesize_cue_chunked(
    cue: TimelineCue,
    *,
    drama_repo: str,
    prof: Any,
    anchor_wav: Path,
    anchor_text: str,
    cache_dir: Path,
    offline_dry_run: bool,
    drama_client: Drama3ServerClient | None,
    whisper_qa: BilingualWhisperQA,
    domain: str = DEFAULT_DOMAIN,
) -> tuple[Path, dict[str, Any]]:
    subcues = split_cue_into_subcues_for_drama3(
        cue,
        max_cjk_chars=105,
        max_en_words=65,
        domain=domain,
    )
    if len(subcues) == 1:
        wav_p, used_prompt, qa_ok = _synthesize_subcue_with_qa(
            subcues[0],
            drama_repo=drama_repo,
            prof=prof,
            anchor_wav=anchor_wav,
            anchor_text=anchor_text,
            cache_dir=cache_dir,
            offline_dry_run=offline_dry_run,
            drama_client=drama_client,
            whisper_qa=whisper_qa,
            domain=domain,
        )
        return wav_p, {
            "voice_id": f"drama3:{cue.role_id}",
            "drama3_prompt": used_prompt,
            "qa_passed": qa_ok,
            "subcue_count": 1,
        }

    # Uses real SHA-256 of anchor_wav bytes (never st_size shortcut) and excludes playback_rate
    anchor_digest = _file_sha256_prefix(anchor_wav, length=16)
    combo_key = _sha24(
        {
            "engine": drama_repo,
            "domain": domain,
            "role_id": cue.role_id,
            "anchor_sha256": anchor_digest,
            "subcues_v2": [sc.tts_text or sc.text for sc in subcues],
        }
    )
    combo_wav = cache_dir / "drama3_tts" / f"{combo_key}_joined.wav"
    if combo_wav.is_file() and combo_wav.stat().st_size > 1024:
        return combo_wav, {
            "voice_id": f"drama3:{cue.role_id}",
            "drama3_prompt": " || ".join(sc.text for sc in subcues),
            "qa_passed": True,
            "subcue_count": len(subcues),
            "cached": True,
        }

    part_wavs: list[Path] = []
    used_prompts: list[str] = []
    all_qa_ok = True
    for sc in subcues:
        pw, up, qok = _synthesize_subcue_with_qa(
            sc,
            drama_repo=drama_repo,
            prof=prof,
            anchor_wav=anchor_wav,
            anchor_text=anchor_text,
            cache_dir=cache_dir,
            offline_dry_run=offline_dry_run,
            drama_client=drama_client,
            whisper_qa=whisper_qa,
            domain=domain,
        )
        part_wavs.append(pw)
        used_prompts.append(up)
        all_qa_ok = all_qa_ok and qok

    concat_pcm_wavs(part_wavs, combo_wav, pause_ms=160.0)
    return combo_wav, {
        "voice_id": f"drama3:{cue.role_id}",
        "drama3_prompt": " || ".join(used_prompts),
        "qa_passed": all_qa_ok,
        "subcue_count": len(subcues),
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "《跨境底牌：硅深暗战》/ Global Edge 96GB GPU "
            "(Fish Audio Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL) 双语多变体商战广播剧合成引擎"
        )
    )
    parser.add_argument(
        "--studio-dir",
        "--bundle-dir",
        dest="studio_dir",
        default=str(STUDIO_DIR),
        help="包含 voice_casting_registry.json、voice_cast_drama3.json、voice_anchors/ 的工作台目录",
    )
    parser.add_argument(
        "--cue-sheets-dir",
        default="",
        help="可选：分集台本目录覆盖路径（默认 <studio-dir>/cue_sheets）",
    )
    parser.add_argument(
        "--auditions-dir",
        default="",
        help="可选：试音台本目录覆盖路径（默认 <studio-dir>/auditions）",
    )
    parser.add_argument(
        "--episodes",
        default="AUDITION,E001_VARIANTS",
        help="渲染目标：AUDITION, E001_VARIANTS, E001_VA..VD, E001-E024, ALL",
    )
    parser.add_argument("--output-dir", default="", help="母带输出目录（默认 <studio-dir>/outputs）")
    parser.add_argument("--existing-dir", default="", help="可选：云盘已归档 MP3 标记目录（用于 --skip-existing）")
    parser.add_argument("--cache-dir", default="", help="可选：分轨缓存目录（默认 <studio-dir>/cache）")
    parser.add_argument("--sgl-bin", default="sgl-omni")
    parser.add_argument("--sgl-port", type=int, default=8000)
    parser.add_argument("--moss-python", default=sys.executable)
    parser.add_argument("--acestep-python", default=sys.executable)
    parser.add_argument("--force-int4", action="store_true")
    parser.add_argument("--disable-ras", action="store_true")
    parser.add_argument("--skip-asr-qa", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--mp3-bitrate", default="192k")
    parser.add_argument("--offline-dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    root = Path(args.studio_dir).resolve()
    cue_dir = Path(args.cue_sheets_dir).resolve() if args.cue_sheets_dir else (root / "cue_sheets")
    auditions_dir = Path(args.auditions_dir).resolve() if args.auditions_dir else (root / "auditions")
    out_dir = Path(args.output_dir).resolve() if args.output_dir else (root / "outputs")
    extra_existing_dir = Path(args.existing_dir).resolve() if args.existing_dir else None
    cache_dir = Path(args.cache_dir).resolve() if args.cache_dir else (root / "cache")

    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("drama3_tts", "moss_sfx", "acestep_bgm", "logs"):
        (cache_dir / sub).mkdir(parents=True, exist_ok=True)

    registry = VoiceCastingRegistry.load(root / "voice_casting_registry.json")
    domain = registry.domain or DEFAULT_DOMAIN

    from launch_g4_global_edge_drama3 import validate_production_voice_cast  # noqa: E402

    cast_ok, cast_errors = validate_production_voice_cast(
        root,
        required_roles=list(registry.roles.keys()),
        allow_offline_stub=args.offline_dry_run,
    )
    if not cast_ok:
        raise RuntimeError(
            "声纹门禁 validate_production_voice_cast() 未通过，严禁启动 Drama 3：\n  - "
            + "\n  - ".join(cast_errors)
        )

    voice_cast = json.loads((root / "voice_cast_drama3.json").read_text(encoding="utf-8"))
    characters: dict[str, dict[str, Any]] = voice_cast["characters"]

    for role_id, cinfo in characters.items():
        ap = root / cinfo["anchor_wav"]
        if not ap.is_file():
            raise FileNotFoundError(f"角色 {role_id} 参考干音锚点缺失: {ap}")

    targets = resolve_global_edge_targets(cue_dir, auditions_dir, args.episodes)
    gpu_name, vram_gb, cc = detect_gpu_profile()
    co_resident_96g = (not args.offline_dry_run) and (vram_gb >= 85.0) and (not args.force_int4)
    drama_repo = "fishaudio/drama-3" if (co_resident_96g and not args.force_int4) else "fishaudio/drama-3-int4"
    moss_repo = "OpenMOSS-Team/MOSS-SoundEffect-v2.0"
    acestep_repo = "ACE-Step/acestep-v15-xl-turbo-diffusers"

    print("=" * 80, flush=True)
    print(
        f"🎙️ 《跨境底牌：硅深暗战》Global Edge 双语多变体合成台 | "
        f"任务数: {len(targets)} ({targets[0][0]}..{targets[-1][0]}) | domain={domain}",
        flush=True,
    )
    print(
        f"🖥️  设备: {gpu_name} ({vram_gb:.1f} GB, sm_{cc[0]}{cc[1]}) | "
        f"模式: {'CPU 离线全链路干跑' if args.offline_dry_run else ('96GB 三模型同卡常驻' if co_resident_96g else '显存分阶段接力')}",
        flush=True,
    )
    print(f"🎭 已加载 {len(characters)} 位角色声纹锚点 | 商战拟音母题: {len(registry.sonic_motifs)} 枚", flush=True)
    print("=" * 80, flush=True)

    drama_client: Drama3ServerClient | None = None
    moss_worker: SubprocessJsonWorker | None = None
    acestep_worker: SubprocessJsonWorker | None = None
    whisper_qa = BilingualWhisperQA(enabled=(not args.skip_asr_qa and not args.offline_dry_run))

    if not args.offline_dry_run:
        drama_client = Drama3ServerClient(
            sgl_bin=args.sgl_bin,
            model_repo=drama_repo,
            port=args.sgl_port,
            co_resident_96g=co_resident_96g,
            enable_ras=not args.disable_ras,
            log_path=cache_dir / "logs" / "sglang_omni_global_edge.log",
        )
        moss_worker = SubprocessJsonWorker("MOSS-SFX v2.0", args.moss_python, _MOSS_WORKER_CODE, moss_repo)
        acestep_worker = SubprocessJsonWorker("ACE-Step 1.5 XL", args.acestep_python, _ACESTEP_WORKER_CODE, acestep_repo)
        if co_resident_96g:
            drama_client.start()

    rendered_summaries: list[dict[str, Any]] = []

    try:
        for label, cs_path in targets:
            cue_sheet = EpisodeCueSheet.load(cs_path)
            if args.skip_existing:
                check_dirs = [out_dir]
                if extra_existing_dir and extra_existing_dir.exists() and extra_existing_dir != out_dir:
                    check_dirs.append(extra_existing_dir)
                existing = find_existing_episode_mp3s(cue_sheet.episode_id, check_dirs)
                if existing:
                    print(f"⏭️  [{cue_sheet.episode_id}] 已存在成片 {existing[-1].name}，自动跳过。", flush=True)
                    continue

            t_ep = time.time()
            dialogue_cues = [c for c in cue_sheet.cues if c.kind == "dialogue"]
            sfx_cues = [c for c in cue_sheet.cues if c.kind == "sfx"]
            print(
                f"\n▶️  开始合成 [{label}] 《{cue_sheet.title}》 "
                f"(对白 {len(dialogue_cues)} 轨 | 拟音 {len(sfx_cues)} 轨 | 分幕配乐 {len(cue_sheet.acts)} 幕)",
                flush=True,
            )

            cue_audio_map: dict[str, Path] = {}
            cue_meta_map: dict[str, dict[str, Any]] = {}
            act_bgm_map: dict[str, Path] = {}

            # 1. Bilingual Dialogue Synthesis (Drama 3 at 1.0x; mixer applies atempo for playback_rate != 1.0)
            if dialogue_cues and not args.offline_dry_run and not co_resident_96g:
                assert drama_client is not None
                drama_client.start()

            for idx, cue in enumerate(dialogue_cues, 1):
                if cue.role_id not in characters:
                    raise KeyError(f"[{cue.cue_id}] 角色 {cue.role_id!r} 未在 voice_cast_drama3.json 中注册！")
                cinfo = characters[cue.role_id]
                prof = registry.resolve_role(cue.role_id)
                wav_p, meta_d = synthesize_cue_chunked(
                    cue,
                    drama_repo=drama_repo,
                    prof=prof,
                    anchor_wav=root / cinfo["anchor_wav"],
                    anchor_text=cinfo["anchor_text"],
                    cache_dir=cache_dir,
                    offline_dry_run=args.offline_dry_run,
                    drama_client=drama_client,
                    whisper_qa=whisper_qa,
                    domain=domain,
                )
                cue_audio_map[cue.cue_id] = wav_p
                cue_meta_map[cue.cue_id] = meta_d
                if idx % 8 == 0 or idx == len(dialogue_cues):
                    print(
                        f"   🎙️ 对白进度: {idx}/{len(dialogue_cues)} "
                        f"({cue.cue_id} [{cue.role_id}, rate={cue.playback_rate:.2f}x] -> {probe_duration_seconds(wav_p):.1f}s)",
                        flush=True,
                    )

            if dialogue_cues and not args.offline_dry_run and not co_resident_96g and drama_client is not None:
                drama_client.close()

            # 2. Foreground Corporate Foley SFX (MOSS-SoundEffect-v2.0 + SHA-256 Cache + Mutual OOM Yield)
            novel_sfx_cues: list[TimelineCue] = []
            for cue in sfx_cues:
                if cue.motif_id and cue.motif_id in registry.sonic_motifs:
                    motif = registry.sonic_motifs[cue.motif_id]
                    if motif.cached_file:
                        m_path = Path(motif.cached_file) if Path(motif.cached_file).is_absolute() else (root / motif.cached_file)
                        if m_path.is_file():
                            cue_audio_map[cue.cue_id] = m_path
                            continue
                novel_sfx_cues.append(cue)

            if novel_sfx_cues:
                for idx, cue in enumerate(novel_sfx_cues, 1):
                    raw_prompt = cue.sfx_prompt or (
                        registry.sonic_motifs[cue.motif_id].sfx_prompt if cue.motif_id in registry.sonic_motifs else ""
                    )
                    prompt = sanitize_moss_foley_prompt(raw_prompt)
                    sfx_key = _sha24({"prompt": prompt, "dur": round(cue.duration_seconds, 2)})
                    sfx_wav = cache_dir / "moss_sfx" / f"{sfx_key}.wav"

                    if args.offline_dry_run:
                        if not sfx_wav.is_file():
                            _write_offline_voiced_wav(
                                sfx_wav,
                                duration_s=cue.duration_seconds,
                                base_freq_hz=92.0,
                                amp=0.14,
                                is_bgm=True,
                            )
                    elif not sfx_wav.is_file():
                        assert moss_worker is not None
                        raw_moss = cache_dir / "moss_sfx" / f"{sfx_key}_raw.wav"
                        sfx_req = {
                            "prompt": prompt,
                            "seconds": cue.duration_seconds,
                            "out_path": str(raw_moss),
                            "seed": 108 + idx,
                        }
                        try:
                            moss_worker.request(sfx_req)
                        except RuntimeError:
                            if acestep_worker is not None:
                                acestep_worker.close()
                            moss_worker.close()
                            moss_worker.request(sfx_req)
                        subprocess.run(
                            [
                                "ffmpeg",
                                "-y",
                                "-hide_banner",
                                "-loglevel",
                                "error",
                                "-i",
                                str(raw_moss),
                                "-ar",
                                "48000",
                                "-ac",
                                "2",
                                "-c:a",
                                "pcm_s16le",
                                str(sfx_wav),
                            ],
                            check=True,
                        )
                        raw_moss.unlink(missing_ok=True)
                    cue_audio_map[cue.cue_id] = sfx_wav

                if not args.offline_dry_run and not co_resident_96g and moss_worker is not None:
                    moss_worker.close()

            # 3. Per-Act HBO Corporate Thriller Instrumental BGM (ACE-Step 1.5 XL + SHA-256 Cache + Mutual OOM Yield)
            novel_acts = []
            for act in cue_sheet.acts:
                if act.cached_bgm_file:
                    b_path = Path(act.cached_bgm_file) if Path(act.cached_bgm_file).is_absolute() else (root / act.cached_bgm_file)
                    if b_path.is_file():
                        act_bgm_map[act.act_id] = b_path
                        continue
                novel_acts.append(act)

            if novel_acts:
                for a_idx, act in enumerate(novel_acts, 1):
                    target_dur = float(max(30.0, min(110.0, float(act.bgm_duration_s or 75.0))))
                    bgm_prompt = enrich_business_drama_bgm_prompt(act.bgm_prompt)
                    bgm_key = _sha24({"prompt": bgm_prompt, "vocal_language": "unknown", "dur": round(target_dur, 1)})
                    bgm_wav = cache_dir / "acestep_bgm" / f"{bgm_key}.wav"

                    if args.offline_dry_run:
                        if not bgm_wav.is_file():
                            _write_offline_voiced_wav(
                                bgm_wav,
                                duration_s=12.0,
                                base_freq_hz=110.0,
                                amp=0.09,
                                is_bgm=True,
                            )
                    elif not bgm_wav.is_file():
                        assert acestep_worker is not None
                        raw_bgm = cache_dir / "acestep_bgm" / f"{bgm_key}_raw.wav"
                        print(f"   🎻 [ACE-Step 1.5 XL] 生成商战纯器乐配乐 {act.act_id} ({target_dur:.0f}s): {act.title}", flush=True)
                        bgm_req = {
                            "prompt": bgm_prompt,
                            "lyrics": "[Instrumental]",
                            "vocal_language": "unknown",
                            "duration_s": target_dur,
                            "out_path": str(raw_bgm),
                            "seed": 3000 + cue_sheet.chapter_number * 10 + a_idx,
                        }
                        try:
                            acestep_worker.request(bgm_req)
                        except RuntimeError:
                            if moss_worker is not None:
                                moss_worker.close()
                            acestep_worker.close()
                            acestep_worker.request(bgm_req)
                        subprocess.run(
                            [
                                "ffmpeg",
                                "-y",
                                "-hide_banner",
                                "-loglevel",
                                "error",
                                "-i",
                                str(raw_bgm),
                                "-ar",
                                "48000",
                                "-ac",
                                "2",
                                "-c:a",
                                "pcm_s16le",
                                str(bgm_wav),
                            ],
                            check=True,
                        )
                        raw_bgm.unlink(missing_ok=True)
                    act_bgm_map[act.act_id] = bgm_wav

                if not args.offline_dry_run and not co_resident_96g and acestep_worker is not None:
                    acestep_worker.close()

            # 4. 3-Bus -16 LUFS Mastering (atempo 0.80x, corporate acoustic spaces, crosstalk, ducking, dual-line SRT)
            stem_prefix = canonical_global_edge_stem(cue_sheet)
            print(f"   🎚️  [{cue_sheet.episode_id}] 执行三母线混音与双行双语字幕导出 (-16 LUFS)...", flush=True)
            master_res = master_episode_three_bus(
                cue_sheet=cue_sheet,
                cue_audio_map=cue_audio_map,
                act_bgm_map=act_bgm_map,
                output_dir=out_dir,
                cue_meta_map=cue_meta_map,
                registry=registry,
                workers=4,
                clean_work_dir=True,
                stem_prefix=stem_prefix,
                mp3_bitrate=args.mp3_bitrate,
            )

            lufs, tp_db = measure_ebur128(master_res["master_wav"])
            done_marker = Path(str(master_res["master_wav"])).with_suffix(".done")
            summary_item = {
                "project_id": registry.project_id,
                "domain": domain,
                "episode_id": cue_sheet.episode_id,
                "chapter_number": cue_sheet.chapter_number,
                "title": cue_sheet.title,
                "mode": cue_sheet.mode,
                "engine": "offline_dry_run" if args.offline_dry_run else drama_repo,
                "rendered_at": utc_now_iso(),
                "elapsed_s": round(time.time() - t_ep, 2),
                "total_duration_s": master_res["total_duration_s"],
                "integrated_lufs": round(lufs, 2),
                "true_peak_dbfs": round(tp_db, 2),
                "master_wav": str(master_res["master_wav"]),
                "master_mp3": str(master_res["master_mp3"]),
                "subtitles_srt": str(master_res["subtitles_srt"]),
                "manifest_json": str(master_res["manifest_json"]),
            }
            done_marker.write_text(json.dumps(summary_item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            rendered_summaries.append(summary_item)
            print(
                f"✅ [{cue_sheet.episode_id}] 成片出炉！时长 {master_res['total_duration_s'] / 60.0:.2f} 分钟 | "
                f"响度 {lufs:.1f} LUFS (TP {tp_db:.1f} dBTP) | 耗时 {time.time() - t_ep:.1f}s\n"
                f"   🎧 MP3: {master_res['master_mp3']}\n"
                f"   📝 双语字幕: {master_res['subtitles_srt']}",
                flush=True,
            )
    finally:
        if drama_client is not None:
            drama_client.close()
        if moss_worker is not None:
            moss_worker.close()
        if acestep_worker is not None:
            acestep_worker.close()

    print("\n" + "=" * 80, flush=True)
    print(f"🎉 《跨境底牌：硅深暗战》本批次渲染全部完成！共完成 {len(rendered_summaries)} 项，目录: {out_dir}", flush=True)
    print("=" * 80, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
