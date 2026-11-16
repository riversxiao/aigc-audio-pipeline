#!/usr/bin/env python3
"""《穿越周期的信》——巴菲特致股东信双语圆桌 · 96GB GPU 三件套本地推理与同传母带合成引擎 (v1.0.0).

核心工业级特性（100% 零 API 费用）：
1. 【`3+1` 跨阶层声线锚点】：许知微（现代播客女主持）+ 陈怀远（中英混说双语投资人）+ 老周（接地气实业老板）
   + 沃伦·巴菲特（1980s–90s 50岁壮年奥马哈原声态），统一 `44.1kHz -16 LUFS` 零样本锚定。
2. 【中英双语 Drama 3 表演指令转译与智能切句】：通过 `domain="finance_podcast"` 自动完成财经多音字纠偏
   （`老行当`、`资产重组`、`调仓` 等），中文按 `<=115` 字切句、英文按 `<=65` 词完整句号切句，搭配 `ras` 高表现力采样。
3. 【双语感知 CPU `faster-whisper` 零显存回听质检】：巴菲特原声轨自动走 `language="en"` 英文词级召回与句尾防吞词检测；
   中文与中英混说轨走 `language="zh"` + 财经播客词汇提示，保留 `float`/`swimming naked` 等原词零误判。
4. 【商业纪录片声效母题 + 美式原声书房配乐】：`MOSS-SoundEffect v2.0` 生成年报翻页、1980s 机械打字机回车铃声；
   `ACE-Step 1.5 XL` 生成指弹木吉他、室内乐大提琴与深夜毛毡钢琴纯器乐床（严禁古风民乐串台与人声吟唱）。
5. 【采样级“纪录片同声传译叠音”三母线混音】：巴菲特英文原声前 `3.5s` 满音量独奏抓耳 → 半余弦平滑压低至 `0.15` 垫底
   → 陈怀远中文同传清晰切入 → 英文尾韵自然收束，同步导出零重叠中英双行 `.srt` 字幕与 `-16 LUFS` 320k MP3 母带！
"""

from __future__ import annotations

from array import array
import argparse
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
for candidate_src in (STUDIO_DIR / "src", STUDIO_DIR.parent / "src"):
    if (candidate_src / "aigc_audio_pipeline").is_dir() and str(candidate_src) not in sys.path:
        sys.path.insert(0, str(candidate_src))

from aigc_audio_pipeline.batch_queue import measure_ebur128  # noqa: E402
from aigc_audio_pipeline.drama3_adapter import (  # noqa: E402
    concat_pcm_wavs,
    estimate_drama3_max_new_tokens,
    split_cue_into_subcues_for_drama3,
    translate_cue_to_drama3_input,
    trim_edge_silence_wav,
)
from aigc_audio_pipeline.elevenlabs_client import probe_duration_seconds  # noqa: E402
from aigc_audio_pipeline.mixer import master_episode_three_bus  # noqa: E402
from aigc_audio_pipeline.models import (  # noqa: E402
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
    utc_now_iso,
)
from aigc_audio_pipeline.qa import evaluate_dialogue_qa, inspect_audio_peak_dbfs  # noqa: E402

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
    # Hide GPU BEFORE importing torch so 0 bytes of CUDA context are allocated on a busy shared GPU!
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
    print(f"[MOSS-SoundEffect v2.0] Loading {model_id} on multi-core CPU (0 MB VRAM, shared-GPU free={free_gb:.2f}GB)...", flush=True)
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
    # Hide GPU BEFORE importing torch so 0 bytes of CUDA context are allocated on a busy shared GPU!
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import soundfile as sf
import torch
from diffusers import AceStepPipeline

if not can_touch_cuda:
    torch.set_num_threads(min(32, max(4, (os.cpu_count() or 16) - 4)))

model_id = sys.argv[1]
dtype = (torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16) if (can_touch_cuda and torch.cuda.is_available()) else torch.float32
print(f"[ACE-Step 1.5 XL] Loading {model_id} ({dtype}, shared-GPU free={free_gb:.2f}GB)...", flush=True)
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
            print(f"[ACE-Step 1.5 XL] Offload hook fallback to CPU ({exc})", flush=True)

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


def _write_synthetic_tone_wav(
    out_wav: Path,
    *,
    duration_s: float,
    freq_hz: float = 220.0,
    amp: float = 0.22,
    sample_rate: int = 48000,
) -> Path:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    nframes = max(int(0.4 * sample_rate), int(round(duration_s * sample_rate)))
    fade = min(int(0.03 * sample_rate), nframes // 4)
    buf = bytearray(nframes * 4)
    two_pi_f = 2.0 * math.pi * freq_hz / sample_rate
    for i in range(nframes):
        env = 1.0
        if i < fade:
            env = i / max(1, fade)
        elif i > nframes - fade:
            env = (nframes - i) / max(1, fade)
        val = int(max(-32767, min(32767, 32767.0 * amp * env * math.sin(two_pi_f * i))))
        lo = val & 0xFF
        hi = (val >> 8) & 0xFF
        base = i * 4
        buf[base] = lo
        buf[base + 1] = hi
        buf[base + 2] = lo
        buf[base + 3] = hi
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(buf))
    return out_wav


class SubprocessJsonWorker:
    """Persistent GPU model worker running inside its own isolated Python virtualenv."""

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
        print(f"🚀 [{self.label}] 正在加载模型权重至显存: {self.model_id} ...", flush=True)
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
            print(f"✅ [Drama 3] 检测到 {self.base_url} 已在线，直接复用！", flush=True)
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
            print("✨ [Drama 3] 已启用官方 Reference Sampling + RAS 高表现力圆桌采样策略", flush=True)

        print(f"🚀 [Drama 3] 启动 SGLang-Omni 服务: {' '.join(cmd)}", flush=True)
        env = os.environ.copy()
        env["TORCHDYNAMO_DISABLE"] = "1"
        sgl_bin_dir = str(Path(self.sgl_bin).resolve().parent)
        env["PATH"] = f"{sgl_bin_dir}:/usr/local/cuda/bin:{env.get('PATH', '')}"
        self._log_fh = self.log_path.open("a", encoding="utf-8")
        self.proc = subprocess.Popen(cmd, stdout=self._log_fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env)

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
    """Language-aware Zero-VRAM CPU int8 `faster-whisper` ASR gate (`en` for Buffett, `zh` for podcast hosts)."""

    def __init__(self, enabled: bool = True, model_size: str = "small") -> None:
        self.enabled = enabled
        self._model: Any = None
        self._available: bool | None = None
        self.model_size = model_size

    def transcribe(self, wav_path: Path, *, language_code: str = "zh") -> str | None:
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
            if language_code == "en":
                segments, _ = self._model.transcribe(
                    audio_16k,
                    language="en",
                    beam_size=2,
                    vad_filter=True,
                    initial_prompt=(
                        "Warren Buffett Berkshire Hathaway shareholder letter: "
                        "In God we trust, all others pay cash, Clayton Homes, ConocoPhillips, applause, yawns."
                    ),
                )
                return " ".join(seg.text.strip() for seg in segments if seg.text.strip()).strip()

            zh_prompt = (
                "以下是现代中文商业播客日常对谈：许知微、陈怀远、老周、沃伦巴菲特、伯克希尔哈撒韦、百分之二十。"
                if language_code == "zh"
                else (
                    "以下是现代中英双语商业圆桌播客对谈：许知微、陈怀远、老周、沃伦巴菲特、伯克希尔哈撒韦、"
                    "insurance float、swimming naked、pay cash、house-price appreciation、skin in the game。"
                )
            )
            segments, _ = self._model.transcribe(
                audio_16k,
                language="zh",
                beam_size=2,
                vad_filter=(len(audio_16k) > 36000),
                initial_prompt=zh_prompt,
            )
            return "".join(seg.text for seg in segments).strip()
        except Exception as exc:
            print(f"⚠️ [双语 ASR 质检门] 单句转写回退纯语速质检 ({exc})", flush=True)
            return None


def resolve_buffett_targets(
    spec: str,
    cue_sheets_dir: Path,
    auditions_dir: Path,
) -> list[tuple[str, Path]]:
    """Parse `--episodes` (e.g. `AUDITION`, `E001`, `E001-E012`) into `(label, path)`."""
    ep_files: dict[str, Path] = {}
    for p in sorted(cue_sheets_dir.glob("E*.json")):
        m = re.match(r"^(E\d{3})(?:_|\.|$)", p.name)
        if m:
            ep_files[m.group(1)] = p

    targets: list[tuple[str, Path]] = []
    for token in [t.strip() for t in spec.split(",") if t.strip()]:
        upper = token.upper()
        if upper in ("AUDITION", "AUDITION_BUFFETT"):
            aud_candidates = sorted(
                [*auditions_dir.glob("AUDITION*.json"), *cue_sheets_dir.glob("AUDITION*.json")]
            )
            if not aud_candidates:
                raise FileNotFoundError(f"未在 {auditions_dir} 找到四角色试听台本 JSON")
            targets.append(("AUDITION_BUFFETT", aud_candidates[0]))
            continue

        m_range = re.match(r"^E?(\d{1,3})\s*-\s*E?(\d{1,3})$", upper)
        if m_range:
            start_n, end_n = int(m_range.group(1)), int(m_range.group(2))
            for n in range(start_n, end_n + 1):
                eid = f"E{n:03d}"
                if eid not in ep_files:
                    raise FileNotFoundError(f"未找到第 {eid} 期台本 JSON ({cue_sheets_dir})")
                targets.append((eid, ep_files[eid]))
            continue

        m_single = re.match(r"^E?(\d{1,3})$", upper)
        if m_single:
            eid = f"E{int(m_single.group(1)):03d}"
            if eid not in ep_files:
                raise FileNotFoundError(f"未找到第 {eid} 期台本 JSON ({cue_sheets_dir})")
            targets.append((eid, ep_files[eid]))
            continue

        raise ValueError(f"无法解析 --episodes 参数片段: {token!r}（示例: AUDITION, E001, E001-E012）")
    return targets


def check_bilingual_speaking_rate_ok(cue: TimelineCue, duration_s: float) -> tuple[bool, str]:
    """Language-aware speaking-rate gate supporting both pure English Buffett quotes and bilingual Chinese lines."""
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

    # Chinese or code-switched ZH-EN: count each embedded English word as ~2.2 CJK syllable equivalents
    effective_units = cjk_n + 2.2 * len(en_words)
    if effective_units < 4.0:
        return (0.30 <= duration_s <= 8.0), f"short_zh_dur={duration_s:.2f}s"
    sec_per_unit = duration_s / effective_units
    if sec_per_unit < 0.085:
        return False, f"语速过快/疑似吞字 ({sec_per_unit:.3f}s/字, dur={duration_s:.2f}s)"
    if sec_per_unit > 0.72:
        return False, f"语速过慢/疑似尾音拖沓 ({sec_per_unit:.3f}s/字, dur={duration_s:.2f}s)"
    return True, f"{sec_per_unit:.3f}s/字"


_HUMAN_VOCAL_CLAUSE_RE = re.compile(
    r"(?:,?\s*(?:accompanied by|with|and)\s+[^,.]*?\b(?:cough(?:ing|s)?|groan(?:ing|s)?|grunt(?:ing|s)?|sigh(?:ing|s)?|scream(?:ing|s)?|sob(?:bing|s)?|voice|vocal)\b[^,.]*)",
    re.IGNORECASE,
)


def sanitize_moss_foley_prompt(prompt: str) -> str:
    cleaned = _HUMAN_VOCAL_CLAUSE_RE.sub("", prompt or "").strip(" ,.")
    if not cleaned:
        cleaned = "Crisp vintage annual report paper page turn in a quiet study"
    if "no human voice" not in cleaned.lower():
        cleaned = f"{cleaned}, pure foley sound effect only, no human voice, no speech"
    return cleaned


def enrich_buffett_acestep_bgm_prompt(prompt: str) -> str:
    """Enforce warm American documentary / late-night study acoustic instrumental BGM without vocals or EDM beats."""
    base = (prompt or "").strip().rstrip(".")
    lower = base.lower()
    extras: list[str] = []
    if "acoustic" not in lower and "piano" not in lower and "cello" not in lower:
        extras.append("warm American documentary acoustic guitar and chamber cello underscore")
    if "no drums" not in lower:
        extras.append("no heavy drums, no trap beat, no pop vocals")
    if "no singing" not in lower:
        extras.append("purely instrumental, no vocals, no singing")
    return ", ".join([base, *extras]) if extras else base


def canonical_buffett_stem(cue_sheet: EpisodeCueSheet) -> str:
    clean_title = re.sub(r'[\\/:*?"<>|\s，。！？：；、“”‘’·—]+', "_", cue_sheet.title).strip("_")
    if cue_sheet.mode == "audition_pack":
        return f"{cue_sheet.episode_id}_四角色声线与同传叠音试听母带"
    return f"{cue_sheet.episode_id}_{clean_title}_双语圆桌母带"


def _synthesize_subcue_with_qa(
    subcue: TimelineCue,
    *,
    drama_repo: str,
    cinfo: dict[str, Any],
    prof: Any,
    anchor_wav: Path,
    anchor_text: str,
    cache_dir: Path,
    offline_dry_run: bool,
    drama_client: Drama3ServerClient | None,
    whisper_qa: BilingualWhisperQA,
    domain: str = "finance_podcast",
) -> tuple[Path, str, bool]:
    eff_lang = subcue.language_code or (prof.language_code if prof is not None else "zh") or "zh"
    prompt_a1 = translate_cue_to_drama3_input(subcue, prof, attempt=1, use_phoneme_pins=False, domain=domain)
    anchor_digest = hashlib.sha256(anchor_wav.read_bytes()).hexdigest()[:16] if anchor_wav.is_file() else "missing"
    dyn_max_tokens = estimate_drama3_max_new_tokens(prompt_a1, language_code=eff_lang)
    cache_key = _sha24(
        {
            "engine": drama_repo,
            "domain": domain,
            "role_id": subcue.role_id,
            "anchor_sha256": anchor_digest,
            "prompt_v2": prompt_a1,
            "max_tok": dyn_max_tokens,
        }
    )
    cached_wav = cache_dir / "drama3_tts" / f"{cache_key}.wav"

    if offline_dry_run:
        _, spoken = extract_tags_and_spoken_text(subcue.text)
        if eff_lang == "en":
            est_dur = max(1.2, min(26.0, len(spoken.split()) / 2.65))
        else:
            est_dur = max(0.9, min(26.0, len(spoken) / 4.15))
        freq_map = {
            "host_zhiwei": 295.0,
            "guest_huaiyuan": 215.0,
            "guest_laozhou": 175.0,
            "buffett_prime_en": 195.0,
        }
        _write_synthetic_tone_wav(cached_wav, duration_s=est_dur, freq_hz=freq_map.get(subcue.role_id, 220.0), amp=0.22)
        return cached_wav, prompt_a1, True

    if cached_wav.is_file() and cached_wav.stat().st_size > 1024:
        if probe_duration_seconds(cached_wav) < 68.0:
            return cached_wav, prompt_a1, True

    assert drama_client is not None
    best_wav: Path | None = None
    best_score = -1.0
    final_qa_passed = False
    used_prompt = prompt_a1

    for attempt in (1, 2, 3):
        cur_prompt = translate_cue_to_drama3_input(subcue, prof, attempt=attempt, use_phoneme_pins=False, domain=domain)
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
        asr_txt = whisper_qa.transcribe(try_wav, language_code=eff_lang)

        if asr_txt is not None:
            qa_res = evaluate_dialogue_qa(
                tagged_prompt=subcue.tts_text or subcue.text,
                asr_text=asr_txt,
                duration_s=dur_s,
                peak_dbfs=peak_db,
                attempt=attempt,
                min_char_recall=0.70,
                canonical_prompt=subcue.text,
            )
            passed = qa_res.passed and rate_ok
            score = qa_res.char_recall - (0.25 if not rate_ok else 0.0) - (0.4 * len(qa_res.leaked_tags))
            reason_str = "; ".join(qa_res.reasons + ([] if rate_ok else [rate_msg]))
        else:
            passed = (dur_s >= 0.30) and (peak_db >= -44.0) and rate_ok
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
            f"   ⚠️ [{subcue.cue_id}] 第 {attempt} 次双语质检未过 ({reason_str})，自动降级提示词重抽...",
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
    cinfo: dict[str, Any],
    prof: Any,
    anchor_wav: Path,
    anchor_text: str,
    cache_dir: Path,
    offline_dry_run: bool,
    drama_client: Drama3ServerClient | None,
    whisper_qa: BilingualWhisperQA,
    domain: str = "finance_podcast",
) -> tuple[Path, dict[str, Any]]:
    subcues = split_cue_into_subcues_for_drama3(cue, max_cjk_chars=165, max_en_words=65, domain=domain)
    if len(subcues) == 1:
        wav_p, used_prompt, qa_ok = _synthesize_subcue_with_qa(
            subcues[0],
            drama_repo=drama_repo,
            cinfo=cinfo,
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

    combo_key = _sha24(
        {
            "engine": drama_repo,
            "domain": domain,
            "role_id": cue.role_id,
            "anchor_sha": anchor_wav.stat().st_size,
            "subcues_v2": [sc.text for sc in subcues],
        }
    )
    combo_wav = cache_dir / "drama3_tts" / f"{combo_key}_joined.wav"
    if not offline_dry_run and combo_wav.is_file() and combo_wav.stat().st_size > 1024:
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
            cinfo=cinfo,
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

    concat_pcm_wavs(part_wavs, combo_wav, pause_ms=150.0)
    return combo_wav, {
        "voice_id": f"drama3:{cue.role_id}",
        "drama3_prompt": " || ".join(used_prompts),
        "qa_passed": all_qa_ok,
        "subcue_count": len(subcues),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="《穿越周期的信》 96GB GPU (Fish Audio Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL) 双语同传圆桌合成引擎"
    )
    parser.add_argument("--studio-dir", default=str(STUDIO_DIR))
    parser.add_argument("--episodes", default="AUDITION,E001", help="如 AUDITION,E001 或 E001-E012")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--existing-dir", default="")
    parser.add_argument("--cache-dir", default="")
    parser.add_argument("--sgl-bin", default="sgl-omni")
    parser.add_argument("--sgl-port", type=int, default=8000)
    parser.add_argument("--moss-python", default=sys.executable)
    parser.add_argument("--acestep-python", default=sys.executable)
    parser.add_argument("--force-int4", action="store_true")
    parser.add_argument("--disable-ras", action="store_true")
    parser.add_argument("--skip-asr-qa", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--mp3-bitrate", default="320k")
    parser.add_argument("--offline-dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.studio_dir).resolve()
    out_dir = Path(args.output_dir).resolve() if args.output_dir else (root / "outputs")
    extra_existing_dir = Path(args.existing_dir).resolve() if args.existing_dir else None
    cache_dir = Path(args.cache_dir).resolve() if args.cache_dir else (root / "cache")
    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("drama3_tts", "moss_sfx", "acestep_bgm", "logs"):
        (cache_dir / sub).mkdir(parents=True, exist_ok=True)

    registry = VoiceCastingRegistry.load(root / "voice_casting_registry.json")
    voice_cast = json.loads((root / "voice_cast_drama3.json").read_text(encoding="utf-8"))
    characters: dict[str, dict[str, Any]] = voice_cast["characters"]
    domain = registry.domain or "finance_podcast"

    for role_id, cinfo in characters.items():
        ap = root / cinfo["anchor_wav"]
        if not ap.is_file():
            raise FileNotFoundError(f"角色 {role_id} 参考干音锚点缺失: {ap}")

    targets = resolve_buffett_targets(args.episodes, root / "cue_sheets", root / "auditions")
    gpu_name, vram_gb, cc = detect_gpu_profile()
    co_resident_96g = (not args.offline_dry_run) and (vram_gb >= 85.0) and (not args.force_int4)
    drama_repo = "fishaudio/drama-3" if (co_resident_96g and not args.force_int4) else "fishaudio/drama-3-int4"
    moss_repo = "OpenMOSS-Team/MOSS-SoundEffect-v2.0"
    acestep_repo = "ACE-Step/acestep-v15-xl-turbo-diffusers"

    print("=" * 80, flush=True)
    print(f"🎙️ 《穿越周期的信》双语同传圆桌合成台 | 任务数: {len(targets)} ({targets[0][0]}..{targets[-1][0]})", flush=True)
    print(
        f"🖥️  设备: {gpu_name} ({vram_gb:.1f} GB, sm_{cc[0]}{cc[1]}) | "
        f"模式: {'CPU 离线干跑自检' if args.offline_dry_run else ('96GB 三模型同卡满血常驻' if co_resident_96g else '显存分阶段接力')}",
        flush=True,
    )
    print(f"🧑‍🤝‍🧑 已加载 {len(characters)} 位跨阶层角色声线锚点 | 商业纪实声效母题: {len(registry.sonic_motifs)} 枚", flush=True)
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
            log_path=cache_dir / "logs" / "sglang_omni_buffett.log",
        )
        moss_worker = SubprocessJsonWorker("MOSS-SFX v2.0", args.moss_python, _MOSS_WORKER_CODE, moss_repo)
        acestep_worker = SubprocessJsonWorker("ACE-Step 1.5 XL", args.acestep_python, _ACESTEP_WORKER_CODE, acestep_repo)
        if co_resident_96g:
            drama_client.start()

    rendered_summaries: list[dict[str, Any]] = []

    try:
        for label, cs_path in targets:
            cue_sheet = EpisodeCueSheet.load(cs_path)
            if args.skip_existing and cue_sheet.mode != "audition_pack":
                check_dirs = [out_dir]
                if extra_existing_dir and extra_existing_dir.exists() and extra_existing_dir != out_dir:
                    check_dirs.append(extra_existing_dir)
                existing = [p for cdir in check_dirs for p in sorted(cdir.glob(f"{cue_sheet.episode_id}_*.mp3"))]
                if existing:
                    print(f"⏭️  [{cue_sheet.episode_id}] 已存在成品 {existing[-1].name}，自动跳过。", flush=True)
                    continue

            t_ep = time.time()
            dialogue_cues = [c for c in cue_sheet.cues if c.kind == "dialogue"]
            sfx_cues = [c for c in cue_sheet.cues if c.kind == "sfx"]
            print(
                f"\n▶️  开始合成 [{label}] 《{cue_sheet.title}》 "
                f"(对白 {len(dialogue_cues)} 轨 | 声效 {len(sfx_cues)} 轨 | 分幕配乐 {len(cue_sheet.acts)} 幕)",
                flush=True,
            )

            cue_audio_map: dict[str, Path] = {}
            cue_meta_map: dict[str, dict[str, Any]] = {}
            act_bgm_map: dict[str, Path] = {}

            # 1. Bilingual Roundtable + Prime-Age Buffett Dialogue Synthesis (Fish Drama 3 — 0 MB extra VRAM when server is online)
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
                    cinfo=cinfo,
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
                if idx % 5 == 0 or idx == len(dialogue_cues):
                    print(
                        f"   🎙️ 圆桌对白进度: {idx}/{len(dialogue_cues)} ({cue.cue_id} [{cue.role_id}] -> {probe_duration_seconds(wav_p):.1f}s)",
                        flush=True,
                    )

            if dialogue_cues and not args.offline_dry_run and not co_resident_96g and drama_client is not None:
                drama_client.close()

            # 2. Foreground Documentary Foley SFX (Motifs + MOSS v2.0, VRAM-elastic / CPU-safe)
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
                need_moss_gpu = (not args.offline_dry_run) and any(
                    not (
                        cache_dir
                        / "moss_sfx"
                        / f"{_sha24({'prompt': sanitize_moss_foley_prompt(c.sfx_prompt or (registry.sonic_motifs[c.motif_id].sfx_prompt if c.motif_id in registry.sonic_motifs else '')), 'dur': round(c.duration_seconds, 2)})}.wav"
                    ).is_file()
                    for c in novel_sfx_cues
                )
                if need_moss_gpu and not co_resident_96g:
                    assert moss_worker is not None
                    moss_worker.start()

                for idx, cue in enumerate(novel_sfx_cues, 1):
                    raw_prompt = cue.sfx_prompt or (
                        registry.sonic_motifs[cue.motif_id].sfx_prompt if cue.motif_id in registry.sonic_motifs else ""
                    )
                    prompt = sanitize_moss_foley_prompt(raw_prompt)
                    sfx_key = _sha24({"prompt": prompt, "dur": round(cue.duration_seconds, 2)})
                    sfx_wav = cache_dir / "moss_sfx" / f"{sfx_key}.wav"

                    if args.offline_dry_run:
                        _write_synthetic_tone_wav(sfx_wav, duration_s=cue.duration_seconds, freq_hz=125.0, amp=0.14)
                    elif not sfx_wav.is_file():
                        assert moss_worker is not None
                        raw_moss = cache_dir / "moss_sfx" / f"{sfx_key}_raw.wav"
                        moss_worker.request(
                            {"prompt": prompt, "seconds": cue.duration_seconds, "out_path": str(raw_moss), "seed": 88 + idx}
                        )
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

                if need_moss_gpu and (not co_resident_96g or len(targets) <= 2) and moss_worker is not None:
                    moss_worker.close()

            # 3. Per-Act American Study / Documentary Instrumental BGM (ACE-Step 1.5 XL, VRAM-elastic / offload-safe)
            novel_acts = []
            for act in cue_sheet.acts:
                if act.cached_bgm_file:
                    b_path = Path(act.cached_bgm_file) if Path(act.cached_bgm_file).is_absolute() else (root / act.cached_bgm_file)
                    if b_path.is_file():
                        act_bgm_map[act.act_id] = b_path
                        continue
                novel_acts.append(act)

            if novel_acts:
                need_acestep_gpu = (not args.offline_dry_run) and any(
                    not (
                        cache_dir
                        / "acestep_bgm"
                        / f"{_sha24({'prompt': enrich_buffett_acestep_bgm_prompt(a.bgm_prompt), 'vocal_language': 'unknown', 'dur': round(float(a.bgm_duration_s or 85.0), 1)})}.wav"
                    ).is_file()
                    for a in novel_acts
                )
                if need_acestep_gpu and not co_resident_96g:
                    assert acestep_worker is not None
                    acestep_worker.start()

                for a_idx, act in enumerate(novel_acts, 1):
                    target_dur = float(max(30.0, min(110.0, float(act.bgm_duration_s or 85.0))))
                    bgm_prompt = enrich_buffett_acestep_bgm_prompt(act.bgm_prompt)
                    bgm_key = _sha24({"prompt": bgm_prompt, "vocal_language": "unknown", "dur": round(target_dur, 1)})
                    bgm_wav = cache_dir / "acestep_bgm" / f"{bgm_key}.wav"

                    if args.offline_dry_run:
                        _write_synthetic_tone_wav(bgm_wav, duration_s=14.0, freq_hz=130.8, amp=0.12)
                    elif not bgm_wav.is_file():
                        assert acestep_worker is not None
                        raw_bgm = cache_dir / "acestep_bgm" / f"{bgm_key}_raw.wav"
                        print(f"   🎸 [ACE-Step 1.5 XL] 生成商业纪实配乐 {act.act_id} ({target_dur:.0f}s): {act.title}", flush=True)
                        acestep_worker.request(
                            {
                                "prompt": bgm_prompt,
                                "lyrics": "[Instrumental]",
                                "vocal_language": "unknown",
                                "duration_s": target_dur,
                                "out_path": str(raw_bgm),
                                "seed": 2008 + cue_sheet.chapter_number * 10 + a_idx,
                            }
                        )
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

                if need_acestep_gpu and (not co_resident_96g or len(targets) <= 2) and acestep_worker is not None:
                    acestep_worker.close()

            # 4. 3-Bus Mastering with Documentary Simultaneous-Translation Ducking + Bilingual SRT
            stem_prefix = canonical_buffett_stem(cue_sheet)
            print(f"   🎚️  [{cue_sheet.episode_id}] 执行纪录片同传压混与三母线母带处理 (-16 LUFS + 双语 SRT)...", flush=True)
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
                f"✅ [{cue_sheet.episode_id}] 成片出炉！时长 {master_res['total_duration_s']/60.0:.2f} 分钟 | "
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
    print(f"🎉 《穿越周期的信》本批次渲染全部完成！共完成 {len(rendered_summaries)} 项，目录: {out_dir}", flush=True)
    print("=" * 80, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
