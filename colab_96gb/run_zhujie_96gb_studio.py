#!/usr/bin/env python3
"""《诸界锁仙》 96GB GPU 旗舰三件套有声剧/广播剧本地推理与三母线母带合成引擎 (v1.1.0).

架构亮点（针对旧版 Drama 3 声音偏平、混音无闪避痛点的 6 大工业级升级）：
1. 【24 角色原生国风干音锚点】：直接复用 ElevenLabs `eleven_ttv_v3` 精调锁定的《诸界锁仙》全剧 24 位角色
   纯净大陆普通话棚录干音 (`44.1kHz` -16 LUFS WAV + 100% 逐字对齐 `anchor_text`) 作为 Drama 3 零样本克隆底座。
2. 【Drama 3 原生导演指令转译】：通过 `aigc_audio_pipeline.drama3_adapter` 将全 40 集未删减台本中的情绪标签、
   气口与空间属性转译为 Fish Audio Drama 3 专属自然语言表演提示 + `<whisper>`/`<forceful>`/`<slow>` 成对韵律标签
   + 70+ 仙侠多音字/古账册大写数字纠偏 (`polyphones.py` / `<|phoneme_start|>` 拼音锚定)。
3. 【Reference Sampling (`ras`) 防复读高表现力采样】：自动检测并开启 SGLang-Omni 官方推荐的
   `reference_sampling=true` + `ras` 回退策略，消除平淡机械腔。
4. 【零显存开销 CPU `faster-whisper` + 时长语速双重质检门】：自动拦截标签漏读、句尾吞字与静音拖尾，
   最多自动降级标签重抽 2 次，并对首尾死寂空白做无损微裁切，确保对白节奏刀锋般紧凑。
5. 【6 大跨集母题零成本直通 + MOSS v2.0 拟音 + ACE-Step 1.5 XL 分幕配乐】：96GB 显存下三模型同卡常驻
   (~75.1 GB / 96 GB)，零重载等待；跨集标志性母题（墟界开石门、玄霜叩棺、基因锁心跳等）直接复用母带级 WAV。
6. 【完整接入 `aigc-audio-pipeline` 三母线 -16 LUFS 母带台】：支持 `overlay_next` 前景音效叠化不闪避、
   `dry`/`mental_realm`/`memory_echo` 识海空间混响、对白侧链平滑压低 BGM (`0.11`/`0.34`)、中文角色名 `.srt` 字幕，
   并采用 `E001_drama3_master_v001` 独立命名，绝不覆盖 ElevenLabs 版成片，支持直接同集 A/B 盲听对比！
"""

from __future__ import annotations

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
# Allow importing bundled `src/aigc_audio_pipeline` (NVMe bundle) or repo `../src/aigc_audio_pipeline`
for candidate_src in (STUDIO_DIR / "src", STUDIO_DIR.parent / "src"):
    if (candidate_src / "aigc_audio_pipeline").is_dir() and str(candidate_src) not in sys.path:
        sys.path.insert(0, str(candidate_src))

from aigc_audio_pipeline.batch_queue import measure_ebur128
from aigc_audio_pipeline.drama3_adapter import (
    translate_cue_to_drama3_input,
    trim_edge_silence_wav,
)
from aigc_audio_pipeline.elevenlabs_client import probe_duration_seconds
from aigc_audio_pipeline.mixer import master_episode_three_bus, render_audition_reel
from aigc_audio_pipeline.models import (
    EpisodeCueSheet,
    TimelineCue,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
    utc_now_iso,
)
from aigc_audio_pipeline.qa import evaluate_dialogue_qa, inspect_audio_peak_dbfs

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")

# Persistent isolated worker scripts (MOSS v2.0 uses transformers 4.57 / diffusers 0.37;
# ACE-Step 1.5 XL uses diffusers >= 0.41 AceStepPipeline)
_MOSS_WORKER_CODE = r"""
import gc, json, os, sys
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import numpy as np
import soundfile as sf
import torch
from moss_soundeffect_v2 import MossSoundEffectPipeline

model_id = sys.argv[1]
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
print(f"[MOSS-SoundEffect v2.0] Loading {model_id} ({dtype}, 48kHz)...", flush=True)
pipe = MossSoundEffectPipeline.from_pretrained(model_id, torch_dtype=dtype, device="cuda")
sr = int(getattr(pipe, "sample_rate", 48000))
torch.cuda.empty_cache()
print("__RPC__:" + json.dumps({"status": "ready", "sample_rate": sr}), flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if req.get("cmd") == "quit":
        break
    try:
        seconds = float(np.clip(float(req["seconds"]), 0.8, 28.0))
        steps = int(req.get("steps", 100))
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
        torch.cuda.empty_cache()
        print("__RPC__:" + json.dumps({"status": "error", "error": str(exc)}), flush=True)
"""

_ACESTEP_WORKER_CODE = r"""
import gc, json, os, sys
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import numpy as np
import soundfile as sf
import torch
from diffusers import AceStepPipeline

model_id = sys.argv[1]
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
print(f"[ACE-Step 1.5 XL] Loading {model_id} ({dtype}, 48kHz Stereo, VAE tiling+slicing)...", flush=True)
pipe = AceStepPipeline.from_pretrained(model_id, torch_dtype=dtype).to("cuda")
if hasattr(pipe, "vae"):
    if hasattr(pipe.vae, "enable_tiling"):
        pipe.vae.enable_tiling()
    if hasattr(pipe.vae, "enable_slicing"):
        pipe.vae.enable_slicing()
sr = int(getattr(pipe, "sample_rate", 48000))
torch.cuda.empty_cache()
print("__RPC__:" + json.dumps({"status": "ready", "sample_rate": sr}), flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if req.get("cmd") == "quit":
        break
    try:
        dur_s = float(max(12.0, min(float(req["duration_s"]), 120.0)))
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
        torch.cuda.empty_cache()
        print("__RPC__:" + json.dumps({"status": "error", "error": str(exc)}), flush=True)
"""


def detect_gpu_profile() -> tuple[str, float, tuple[int, int]]:
    """Return `(gpu_name, total_vram_gb, compute_capability)` or CPU fallback."""
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
    """Offline dry-run tone generator for verifying 100% of pipeline & 3-bus mastering on CPU."""
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
            # ~58GB for 35B MoE FP8 Drama 3 (0.46 tts + 0.08 vocoder + 4GiB prep) -> >31GB free for MOSS v2.0 + ACE-Step 1.5 XL!
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
            print("✨ [Drama 3] 已启用官方 Reference Sampling + RAS 防复读高表现力采样策略", flush=True)

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
                raise RuntimeError(
                    f"[Drama 3] SGLang-Omni 启动异常退出 (rc={self.proc.returncode}):\n{tail}"
                )
            if self.is_healthy():
                print(f"✅ [Drama 3] 服务就绪 ({time.time() - t0:.1f}s) -> {self.base_url}", flush=True)
                return
            if tick > 0 and tick % 10 == 0:
                print(f"   ⏳ [Drama 3] 等待权重加载与 CUDA Graph 编译预热 ({int(time.time() - t0)}s)...", flush=True)
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
                "max_new_tokens": 1536,
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


class LocalWhisperQA:
    """Zero-VRAM CPU int8 `faster-whisper` ASR gate (falls back cleanly if package absent)."""

    def __init__(self, enabled: bool = True, model_size: str = "small") -> None:
        self.enabled = enabled
        self._model: Any = None
        self._available: bool | None = None
        self.model_size = model_size

    def transcribe(self, wav_path: Path) -> str | None:
        if not self.enabled:
            return None
        if self._available is False:
            return None
        if self._model is None:
            try:
                from faster_whisper import WhisperModel  # type: ignore[import-not-found]

                print(
                    f"🔍 [ASR 质检门] 加载 CPU int8 faster-whisper ({self.model_size}, 0 MB 显存占用)...",
                    flush=True,
                )
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                self._available = True
            except Exception as exc:
                print(f"ℹ️ [ASR 质检门] faster-whisper 未安装 ({exc})，启用纯信号与语速边界质检。", flush=True)
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
            segments, _ = self._model.transcribe(
                audio_16k,
                language="zh",
                beam_size=2,
                vad_filter=True,
                initial_prompt="以下是普通话的句子，请使用简体中文输出。",
            )
            return "".join(seg.text for seg in segments).strip()
        except Exception as exc:
            print(f"⚠️ [ASR 质检门] 单句转写回退纯语速质检 ({exc})", flush=True)
            return None


def resolve_episode_targets(
    spec: str,
    cue_sheets_dir: Path,
    auditions_dir: Path,
) -> list[tuple[str, Path]]:
    """Parse `--episodes` (e.g. `AUDITION`, `E001`, `E007-E040`, `E001,E007-E010`) into `(label, path)`."""
    ep_files: dict[str, Path] = {}
    for p in sorted(cue_sheets_dir.glob("E*.json")):
        m = re.match(r"^(E\d{3})(?:_|\.|$)", p.name)
        if m:
            ep_files[m.group(1)] = p

    targets: list[tuple[str, Path]] = []
    for token in [t.strip() for t in spec.split(",") if t.strip()]:
        upper = token.upper()
        if upper in ("AUDITION", "AUDITION_A"):
            aud_candidates = sorted(auditions_dir.glob("E001_AUDITION_A*.json"))
            if not aud_candidates:
                raise FileNotFoundError(f"未在 {auditions_dir} 找到方案A六句试听清单 JSON")
            targets.append(("AUDITION_A", aud_candidates[0]))
            continue

        m_range = re.match(r"^E?(\d{1,3})\s*-\s*E?(\d{1,3})$", upper)
        if m_range:
            start_n, end_n = int(m_range.group(1)), int(m_range.group(2))
            for n in range(start_n, end_n + 1):
                eid = f"E{n:03d}"
                if eid not in ep_files:
                    raise FileNotFoundError(f"未找到第 {eid} 集台本 JSON ({cue_sheets_dir})")
                targets.append((eid, ep_files[eid]))
            continue

        m_single = re.match(r"^E?(\d{1,3})$", upper)
        if m_single:
            eid = f"E{int(m_single.group(1)):03d}"
            if eid not in ep_files:
                raise FileNotFoundError(f"未找到第 {eid} 集台本 JSON ({cue_sheets_dir})")
            targets.append((eid, ep_files[eid]))
            continue

        raise ValueError(f"无法解析 --episodes 参数片段: {token!r}（示例: AUDITION, E001, E007-E040）")
    return targets


def check_speaking_rate_ok(cue: TimelineCue, duration_s: float) -> tuple[bool, str]:
    """Catch runaway autoregressive babbling or clipped syllables via CJK speaking rate."""
    _, spoken = extract_tags_and_spoken_text(cue.text)
    cjk_n = len(_CJK_RE.findall(spoken))
    if cjk_n < 4:
        return (duration_s >= 0.30 and duration_s <= 8.0), f"short_line_dur={duration_s:.2f}s"
    sec_per_char = duration_s / cjk_n
    if sec_per_char < 0.085:
        return False, f"语速异常过快/疑似吞字 ({sec_per_char:.3f}s/字, dur={duration_s:.2f}s, chars={cjk_n})"
    if sec_per_char > 0.72:
        return False, f"语速异常过慢/疑似尾音拖沓 ({sec_per_char:.3f}s/字, dur={duration_s:.2f}s, chars={cjk_n})"
    return True, f"{sec_per_char:.3f}s/字"


_HUMAN_VOCAL_CLAUSE_RE = re.compile(
    r"(?:,?\s*(?:accompanied by|with|and)\s+[^,.]*?\b(?:cough(?:ing|s)?|groan(?:ing|s)?|grunt(?:ing|s)?|sigh(?:ing|s)?|scream(?:ing|s)?|sob(?:bing|s)?|voice|vocal)\b[^,.]*)",
    re.IGNORECASE,
)
_PERCUSSION_ALLOW_RE = re.compile(r"\b(?:war\s+drum|taiko|battle\s+drum|percussion|timpani)\b", re.IGNORECASE)


def sanitize_moss_foley_prompt(prompt: str) -> str:
    """Strip human vocalization clauses so MOSS-SoundEffect v2.0 generates pure clean Foley without synthetic grunts."""
    cleaned = _HUMAN_VOCAL_CLAUSE_RE.sub("", prompt or "").strip(" ,.")
    if not cleaned:
        cleaned = (prompt or "subtle environmental foley movement").strip()
    if "no human voice" not in cleaned.lower():
        cleaned = f"{cleaned}, pure foley sound effect only, no human voice, no speech"
    return cleaned


def enrich_acestep_bgm_prompt(prompt: str) -> str:
    """Enforce pure ancient Chinese instrumental chamber scoring without modern pop/trap beats or vocals."""
    base = (prompt or "").strip().rstrip(".")
    lower = base.lower()
    extras: list[str] = []
    if "traditional chinese" not in lower and "ancient chinese" not in lower:
        extras.append("traditional Chinese xianxia instrumental score")
    if not _PERCUSSION_ALLOW_RE.search(base) and "no drums" not in lower:
        extras.append("no drums, no modern beat, no pop rhythm")
    if "no singing" not in lower:
        extras.append("purely instrumental, no vocals, no singing")
    return ", ".join([base, *extras]) if extras else base


def canonical_drama3_stem(cue_sheet: EpisodeCueSheet) -> str:
    """Build human-readable Chinese master filename stem matching E001-E006 archive convention."""
    clean_title = re.sub(r'[\\/:*?"<>|\s，。！？：；、“”‘’·—]+', "_", cue_sheet.title).strip("_")
    m = re.match(r"^第(\d+)章_(.*)$", clean_title)
    if m:
        clean_title = f"第{int(m.group(1)):02d}章_{m.group(2)}"
    return f"{cue_sheet.episode_id}_{clean_title}_Drama3同源古风母带"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="《诸界锁仙》 96GB GPU (Fish Audio Drama 3 + MOSS v2.0 + ACE-Step 1.5 XL) 全自动合成引擎"
    )
    parser.add_argument(
        "--studio-dir",
        default=str(STUDIO_DIR),
        help="包含 voice_cast_drama3.json、voice_anchors/、motifs/、cue_sheets/ 的工程根目录",
    )
    parser.add_argument(
        "--episodes",
        default="E001",
        help="要渲染的集数：AUDITION（6句极速试听）、E001（首集A/B对比）、或 E007-E120（全本收官续跑）",
    )
    parser.add_argument("--output-dir", default="", help="成品输出目录（默认: <studio-dir>/outputs）")
    parser.add_argument("--existing-dir", default="", help="额外检查已完成成片的目录（如挂载的 Google Drive outputs/）")
    parser.add_argument("--cache-dir", default="", help="分轨干音与配乐断点续传缓存目录（默认: <studio-dir>/cache）")
    parser.add_argument("--sgl-bin", default="sgl-omni", help="drama3-venv 中的 sgl-omni 可执行文件路径")
    parser.add_argument("--sgl-port", type=int, default=8000)
    parser.add_argument("--moss-python", default=sys.executable, help="moss-venv Python 路径")
    parser.add_argument("--acestep-python", default=sys.executable, help="acestep-venv Python 路径")
    parser.add_argument("--force-int4", action="store_true", help="强制使用 fishaudio/drama-3-int4 (20.8GB)")
    parser.add_argument("--disable-ras", action="store_true", help="禁用 SGLang-Omni reference_sampling ras 标志")
    parser.add_argument("--phoneme-pins", action="store_true", help="额外注入 <|phoneme_start|> 拼音锚点")
    parser.add_argument("--skip-asr-qa", action="store_true", help="跳过本地 faster-whisper 语音回听质检")
    parser.add_argument("--skip-existing", action="store_true", help="若目标集数已存在成品 MP3 则自动跳过")
    parser.add_argument("--mp3-bitrate", default="320k", help="成品 MP3 码率（默认 320k）")
    parser.add_argument(
        "--offline-dry-run",
        action="store_true",
        help="CPU 离线全链路干跑自检（无需 GPU，验证全剧角色锚点、台本转译、母题复用与三母线 -16 LUFS 混音）",
    )
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

    # Pre-verify all vocal anchor WAVs exist on disk before touching GPU
    for role_id, cinfo in characters.items():
        ap = root / cinfo["anchor_wav"]
        if not ap.is_file():
            raise FileNotFoundError(f"角色 {role_id} 参考干音锚点缺失: {ap}")

    targets = resolve_episode_targets(args.episodes, root / "cue_sheets", root / "auditions")
    gpu_name, vram_gb, cc = detect_gpu_profile()
    co_resident_96g = (not args.offline_dry_run) and (vram_gb >= 85.0) and (not args.force_int4)
    drama_repo = "fishaudio/drama-3" if (co_resident_96g and not args.force_int4) else "fishaudio/drama-3-int4"
    moss_repo = "OpenMOSS-Team/MOSS-SoundEffect-v2.0"
    acestep_repo = "ACE-Step/acestep-v15-xl-turbo-diffusers"

    print("=" * 78, flush=True)
    print(f"🎬 《诸界锁仙》 Fish Audio Drama 3 影视级有声剧合成台 | 待处理任务数: {len(targets)} ({targets[0][0]}..{targets[-1][0]})", flush=True)
    print(
        f"🖥️  设备: {gpu_name} ({vram_gb:.1f} GB, sm_{cc[0]}{cc[1]}) | "
        f"模式: {'离线干跑自检' if args.offline_dry_run else ('96GB 三模型同卡满血常驻' if co_resident_96g else '显存分阶段接力')}",
        flush=True,
    )
    print(f"🎙️  已加载 {len(characters)} 位国风角色声线锚点 | 跨集母题库: {len(registry.sonic_motifs)} 枚", flush=True)
    print("=" * 78, flush=True)

    drama_client: Drama3ServerClient | None = None
    moss_worker: SubprocessJsonWorker | None = None
    acestep_worker: SubprocessJsonWorker | None = None
    whisper_qa = LocalWhisperQA(enabled=(not args.skip_asr_qa and not args.offline_dry_run))

    if not args.offline_dry_run:
        drama_client = Drama3ServerClient(
            sgl_bin=args.sgl_bin,
            model_repo=drama_repo,
            port=args.sgl_port,
            co_resident_96g=co_resident_96g,
            enable_ras=not args.disable_ras,
            log_path=cache_dir / "logs" / "sglang_omni_drama3.log",
        )
        moss_worker = SubprocessJsonWorker("MOSS-SFX v2.0", args.moss_python, _MOSS_WORKER_CODE, moss_repo)
        acestep_worker = SubprocessJsonWorker("ACE-Step 1.5 XL", args.acestep_python, _ACESTEP_WORKER_CODE, acestep_repo)

        if co_resident_96g:
            drama_client.start()

    rendered_summaries: list[dict[str, Any]] = []

    try:
        for label, cs_path in targets:
            cue_sheet = EpisodeCueSheet.load(cs_path)
            if args.skip_existing and label != "AUDITION_A":
                check_dirs = [out_dir]
                if extra_existing_dir and extra_existing_dir.exists() and extra_existing_dir != out_dir:
                    check_dirs.append(extra_existing_dir)
                existing: list[Path] = []
                for cdir in check_dirs:
                    existing.extend(sorted(cdir.glob(f"{cue_sheet.episode_id}_*Drama3*.mp3")))
                    existing.extend(sorted(cdir.glob(f"{cue_sheet.episode_id}_drama3_master_*.mp3")))
                if existing:
                    print(f"⏭️  [{cue_sheet.episode_id}] 已存在成品 {existing[-1].name}，自动跳过。", flush=True)
                    continue

            t_ep = time.time()
            dialogue_cues = [c for c in cue_sheet.cues if c.kind == "dialogue"]
            sfx_cues = [c for c in cue_sheet.cues if c.kind == "sfx"]
            print(
                f"\n▶️  开始合成 [{label}] 《{cue_sheet.title}》 "
                f"(对白 {len(dialogue_cues)} 轨 | 音效 {len(sfx_cues)} 轨 | 分幕配乐 {len(cue_sheet.acts)} 幕)",
                flush=True,
            )

            cue_audio_map: dict[str, Path] = {}
            cue_meta_map: dict[str, dict[str, Any]] = {}
            act_bgm_map: dict[str, Path] = {}

            # ------------------------------------------------------------------
            # Stage 1: Dialogue Synthesis via Fish Audio Drama 3 (+ QA Retry)
            # ------------------------------------------------------------------
            if not args.offline_dry_run and not co_resident_96g:
                assert drama_client is not None
                drama_client.start()

            for idx, cue in enumerate(dialogue_cues, 1):
                if cue.role_id not in characters:
                    raise KeyError(f"[{cue.cue_id}] 角色 {cue.role_id!r} 未在 voice_cast_drama3.json 中注册！")
                cinfo = characters[cue.role_id]
                prof = registry.resolve_role(cue.role_id)
                anchor_wav = root / cinfo["anchor_wav"]
                anchor_text = cinfo["anchor_text"]

                prompt_a1 = translate_cue_to_drama3_input(
                    cue, prof, attempt=1, use_phoneme_pins=args.phoneme_pins
                )
                cache_key = _sha24(
                    {
                        "engine": drama_repo,
                        "role_id": cue.role_id,
                        "anchor_sha": anchor_wav.stat().st_size,
                        "prompt": prompt_a1,
                    }
                )
                cached_wav = cache_dir / "drama3_tts" / f"{cache_key}.wav"

                if args.offline_dry_run:
                    _, spoken = extract_tags_and_spoken_text(cue.text)
                    est_dur = max(0.8, min(14.0, len(_CJK_RE.findall(spoken)) * 0.21))
                    freq = 185.0 if cue.role_id == "narrator" else (240.0 if cinfo.get("gender") == "male" else 330.0)
                    _write_synthetic_tone_wav(cached_wav, duration_s=est_dur, freq_hz=freq, amp=0.22)
                    cue_audio_map[cue.cue_id] = cached_wav
                    cue_meta_map[cue.cue_id] = {
                        "voice_id": f"drama3:{cue.role_id}",
                        "drama3_prompt": prompt_a1,
                        "qa_passed": True,
                    }
                    continue

                if cached_wav.is_file() and cached_wav.stat().st_size > 1024:
                    cue_audio_map[cue.cue_id] = cached_wav
                    cue_meta_map[cue.cue_id] = {
                        "voice_id": f"drama3:{cue.role_id}",
                        "drama3_prompt": prompt_a1,
                        "qa_passed": True,
                        "cached": True,
                    }
                    continue

                assert drama_client is not None
                best_wav: Path | None = None
                best_score = -1.0
                final_qa_passed = False
                used_prompt = prompt_a1

                for attempt in (1, 2, 3):
                    cur_prompt = translate_cue_to_drama3_input(
                        cue, prof, attempt=attempt, use_phoneme_pins=(args.phoneme_pins and attempt == 1)
                    )
                    try_wav = cache_dir / "drama3_tts" / f"{cache_key}_try{attempt}.wav"
                    drama_client.synthesize(
                        drama3_input=cur_prompt,
                        anchor_wav=anchor_wav,
                        anchor_text=anchor_text,
                        out_wav=try_wav,
                    )
                    dur_s, peak_db = inspect_audio_peak_dbfs(try_wav)
                    rate_ok, rate_msg = check_speaking_rate_ok(cue, dur_s)
                    asr_txt = whisper_qa.transcribe(try_wav)

                    if asr_txt is not None:
                        qa_res = evaluate_dialogue_qa(
                            tagged_prompt=cue.tts_text or cue.text,
                            asr_text=asr_txt,
                            duration_s=dur_s,
                            peak_dbfs=peak_db,
                            attempt=attempt,
                            min_char_recall=0.70,
                            canonical_prompt=cue.text,
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
                        f"   ⚠️ [{cue.cue_id}] 第 {attempt} 次质检未过 ({reason_str})，自动降级提示词重抽...",
                        flush=True,
                    )

                assert best_wav is not None
                shutil.copy2(best_wav, cached_wav)
                for a_idx in (1, 2, 3):
                    (cache_dir / "drama3_tts" / f"{cache_key}_try{a_idx}.wav").unlink(missing_ok=True)

                cue_audio_map[cue.cue_id] = cached_wav
                cue_meta_map[cue.cue_id] = {
                    "voice_id": f"drama3:{cue.role_id}",
                    "drama3_prompt": used_prompt,
                    "qa_passed": final_qa_passed,
                }
                if idx % 10 == 0 or idx == len(dialogue_cues):
                    print(
                        f"   🎙️ 对白进度: {idx}/{len(dialogue_cues)} ({cue.role_id}: {probe_duration_seconds(cached_wav):.1f}s)",
                        flush=True,
                    )

            if not args.offline_dry_run and not co_resident_96g and drama_client is not None:
                drama_client.close()

            # Fast path for dialogue-only Audition Pack (`--episodes AUDITION`)
            if cue_sheet.mode == "audition_pack":
                aud_items = []
                for cue in dialogue_cues:
                    _, spoken = extract_tags_and_spoken_text(cue.text)
                    aud_items.append(
                        {
                            "cue_id": cue.cue_id,
                            "role_id": cue.role_id,
                            "wav_path": cue_audio_map[cue.cue_id],
                            "spoken_text": spoken,
                        }
                    )
                reel = render_audition_reel(aud_items, out_dir, "AUDITION_A_drama3_reel")
                aud_summary = {
                    "episode_id": "AUDITION_A",
                    "master_wav": str(reel["wav"]),
                    "master_mp3": str(reel["mp3"]),
                    "manifest_json": str(reel["manifest"]),
                    "rendered_at": utc_now_iso(),
                }
                Path(str(reel["wav"])).with_suffix(".done").write_text(
                    json.dumps(aud_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                print(f"✅ [六句试听合集渲染完成] -> {reel['mp3']}", flush=True)
                rendered_summaries.append(aud_summary)
                continue

            # ------------------------------------------------------------------
            # Stage 2: Foreground SFX (6 Studio Motifs Direct Reuse + MOSS v2.0)
            # ------------------------------------------------------------------
            novel_sfx_cues: list[TimelineCue] = []
            for cue in sfx_cues:
                if cue.motif_id and cue.motif_id in registry.sonic_motifs:
                    motif = registry.sonic_motifs[cue.motif_id]
                    m_path = Path(motif.cached_file)
                    if not m_path.is_Absolute() if hasattr(m_path, "is_Absolute") else not m_path.is_absolute():
                        m_path = root / m_path
                    if m_path.is_file():
                        cue_audio_map[cue.cue_id] = m_path
                        continue
                novel_sfx_cues.append(cue)

            if novel_sfx_cues:
                if not args.offline_dry_run and not co_resident_96g:
                    assert moss_worker is not None
                    moss_worker.start()

                for idx, cue in enumerate(novel_sfx_cues, 1):
                    raw_prompt = cue.sfx_prompt
                    if not raw_prompt and cue.motif_id in registry.sonic_motifs:
                        raw_prompt = registry.sonic_motifs[cue.motif_id].sfx_prompt
                    prompt = sanitize_moss_foley_prompt(raw_prompt)
                    sfx_key = _sha24({"prompt": prompt, "dur": round(cue.duration_seconds, 2)})
                    sfx_wav = cache_dir / "moss_sfx" / f"{sfx_key}.wav"

                    if args.offline_dry_run:
                        _write_synthetic_tone_wav(sfx_wav, duration_s=cue.duration_seconds, freq_hz=110.0, amp=0.16)
                    elif not sfx_wav.is_file():
                        assert moss_worker is not None
                        raw_moss = cache_dir / "moss_sfx" / f"{sfx_key}_raw.wav"
                        moss_req = {
                            "prompt": prompt,
                            "seconds": cue.duration_seconds,
                            "out_path": str(raw_moss),
                            "seed": 42 + idx,
                        }
                        try:
                            moss_worker.request(moss_req)
                        except RuntimeError as exc:
                            if "out of memory" in str(exc).lower():
                                print("⚠️ [MOSS-SFX] 显存峰值触顶，临时释放 ACE-Step 显存并自动重试...", flush=True)
                                if acestep_worker is not None:
                                    acestep_worker.close()
                                moss_worker.close()
                                moss_worker.request(moss_req)
                            else:
                                raise
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

            # ------------------------------------------------------------------
            # Stage 3: Per-Act BGM Score (Cached Studio BGM or ACE-Step 1.5 XL)
            # ------------------------------------------------------------------
            novel_acts = []
            for act in cue_sheet.acts:
                if act.cached_bgm_file:
                    b_path = Path(act.cached_bgm_file)
                    if not b_path.is_absolute():
                        b_path = root / b_path
                    if b_path.is_file():
                        act_bgm_map[act.act_id] = b_path
                        continue
                novel_acts.append(act)

            if novel_acts:
                if not args.offline_dry_run and not co_resident_96g:
                    assert acestep_worker is not None
                    acestep_worker.start()

                for a_idx, act in enumerate(novel_acts, 1):
                    target_dur = 75.0 if float(act.bgm_duration_s or 75.0) >= 60.0 else 48.0
                    bgm_prompt = enrich_acestep_bgm_prompt(act.bgm_prompt)
                    bgm_key = _sha24(
                        {"prompt": bgm_prompt, "vocal_language": "unknown", "dur": round(target_dur, 1)}
                    )
                    bgm_wav = cache_dir / "acestep_bgm" / f"{bgm_key}.wav"

                    if args.offline_dry_run:
                        _write_synthetic_tone_wav(bgm_wav, duration_s=12.0, freq_hz=146.8, amp=0.14)
                    elif not bgm_wav.is_file():
                        assert acestep_worker is not None
                        raw_bgm = cache_dir / "acestep_bgm" / f"{bgm_key}_raw.wav"
                        print(f"   🎵 [ACE-Step 1.5 XL] 生成分幕配乐 {act.act_id} ({target_dur:.0f}s): {act.title}", flush=True)
                        bgm_req = {
                            "prompt": bgm_prompt,
                            "lyrics": "[Instrumental]",
                            "vocal_language": "unknown",
                            "duration_s": target_dur,
                            "out_path": str(raw_bgm),
                            "seed": 100 + cue_sheet.chapter_number * 10 + a_idx,
                        }
                        try:
                            acestep_worker.request(bgm_req)
                        except RuntimeError as exc:
                            if "out of memory" in str(exc).lower():
                                print("⚠️ [ACE-Step] 显存峰值触顶，临时释放 MOSS-SFX 显存并自动重试...", flush=True)
                                if moss_worker is not None:
                                    moss_worker.close()
                                acestep_worker.close()
                                acestep_worker.request(bgm_req)
                            else:
                                raise
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

            # ------------------------------------------------------------------
            # Stage 4: Cinema-Grade 3-Bus Mastering (-16 LUFS + Ducked BGM + SRT)
            # ------------------------------------------------------------------
            print(f"   🎚️  [{cue_sheet.episode_id}] 正在执行三母线混音母带处理 (-16 LUFS + 侧链闪避 + 识海混响)...", flush=True)
            master_res = master_episode_three_bus(
                cue_sheet=cue_sheet,
                cue_audio_map=cue_audio_map,
                act_bgm_map=act_bgm_map,
                output_dir=out_dir,
                cue_meta_map=cue_meta_map,
                registry=registry,
                workers=4,
                clean_work_dir=True,
                stem_prefix=canonical_drama3_stem(cue_sheet),
                mp3_bitrate=args.mp3_bitrate,
            )
            lufs, tp_db = measure_ebur128(master_res["master_wav"])
            # Write `.done` marker AFTER WAV + MP3 + SRT + JSON are all flushed so background Drive sync is atomic!
            done_marker = Path(str(master_res["master_wav"])).with_suffix(".done")
            summary_item = {
                "episode_id": cue_sheet.episode_id,
                "chapter_number": cue_sheet.chapter_number,
                "title": cue_sheet.title,
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
                f"   🎧 MP3: {master_res['master_mp3']}",
                flush=True,
            )
    finally:
        if drama_client is not None:
            drama_client.close()
        if moss_worker is not None:
            moss_worker.close()
        if acestep_worker is not None:
            acestep_worker.close()

    print("\n" + "=" * 78, flush=True)
    print(f"🎉 全部批次合成完毕！共完成 {len(rendered_summaries)} 项产出，保存目录: {out_dir}", flush=True)
    print("=" * 78, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
