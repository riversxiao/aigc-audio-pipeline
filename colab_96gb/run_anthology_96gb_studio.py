#!/usr/bin/env python3
"""通用精品广播剧矩阵 · 96GB Colab G4 黄金三件套本地推理与三母线母带合成引擎 (v1.0.0).

支持多部不同题材广播剧统一零 API 成本量产：
  - `liaozhai_horror`  : 《聊斋志异·午夜悬疑广播剧场》（纯中国古典幽玄器乐 + 古风多音字纠偏）
  - `cosmic_horror`    : 《克苏鲁神话·不可名状声音档案》（1920s 暗黑室内乐/悬疑配乐 + 译名顺读）
  - `hayek_economics`  : 《1944剑桥夜话：〈通往奴役之路〉思想剧场》（1944 剑桥历史人文室内乐）

内置全部 16 项工业级优化：
  1. 96GB G4 三模同卡常驻 (`fishaudio/drama-3` 0.46/0.08/4GiB + `MOSS v2.0` + `ACE-Step 1.5 XL` VAE tiling/slicing)
  2. `expandable_segments:True` + 逐条清显存 + OOM 对偶让位自愈
  3. Drama 3 原生导演指令 + `<whisper>`/`<forceful>`/`<slow>` + `<=105` 字句界切分 + `max_new_tokens <= 2048` 根治截断
  4. 零显存 CPU int8 `faster-whisper` 简体中文分域词表回听防吞字/防标签外泄质检
  5. `aigc_audio_pipeline.mixer` 48kHz 三母线 `-16 LUFS` 闪避母带 + 角色真名 `.srt` + `.done` 原子落盘标记
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

_MOSS_WORKER_CODE = r"""
import gc, json, os, subprocess, sys
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

def _probe_free_vram_gb() -> float:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            text=True, stderr=subprocess.DEVNULL,
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
        print(f"[MOSS-SoundEffect v2.0] CUDA fallback to CPU ({exc})", flush=True)
        gc.collect()
        torch.cuda.empty_cache()
        pipe = None
        use_cuda = False

if pipe is None:
    print(f"[MOSS-SoundEffect v2.0] Loading {model_id} on CPU (0 MB VRAM)...", flush=True)
    pipe = MossSoundEffectPipeline.from_pretrained(model_id, torch_dtype=torch.float32, device="cpu")

sr = int(getattr(pipe, "sample_rate", 48000))
if use_cuda and torch.cuda.is_available():
    torch.cuda.empty_cache()
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
            audio = pipe(prompt=req["prompt"], seconds=seconds, num_inference_steps=steps, cfg_scale=cfg)
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
        if use_cuda and torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("__RPC__:" + json.dumps({"status": "error", "error": str(exc)}), flush=True)
"""

_ACESTEP_WORKER_CODE = r"""
import gc, json, os, subprocess, sys
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

def _probe_free_vram_gb() -> float:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        return float(out.splitlines()[0].strip()) / 1024.0
    except Exception:
        return 0.0

free_gb = _probe_free_vram_gb()
use_cuda = free_gb >= 11.0
if not use_cuda:
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import soundfile as sf
import torch
from diffusers import AceStepPipeline

model_id = sys.argv[1]
if use_cuda and torch.cuda.is_available():
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    print(f"[ACE-Step 1.5 XL] Loading {model_id} on CUDA ({dtype}, VAE tiling+slicing, free={free_gb:.1f}GB)...", flush=True)
    pipe = AceStepPipeline.from_pretrained(model_id, torch_dtype=dtype).to("cuda")
else:
    print(f"[ACE-Step 1.5 XL] Loading {model_id} on CPU (free={free_gb:.1f}GB)...", flush=True)
    pipe = AceStepPipeline.from_pretrained(model_id, torch_dtype=torch.float32).to("cpu")

if hasattr(pipe, "vae"):
    if hasattr(pipe.vae, "enable_tiling"):
        pipe.vae.enable_tiling()
    if hasattr(pipe.vae, "enable_slicing"):
        pipe.vae.enable_slicing()
sr = int(getattr(pipe, "sample_rate", 48000))
if use_cuda and torch.cuda.is_available():
    torch.cuda.empty_cache()
print("__RPC__:" + json.dumps({"status": "ready", "sample_rate": sr, "device": "cuda" if use_cuda else "cpu"}), flush=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    if req.get("cmd") == "quit":
        break
    try:
        dur_s = float(max(12.0, min(float(req["duration_s"]), 115.0)))
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
        if use_cuda and torch.cuda.is_available():
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
        if use_cuda and torch.cuda.is_available():
            torch.cuda.empty_cache()
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
        return name_s, float(mem_mib_s) / 1024.0, (int(cc_parts[0]), int(cc_parts[1]) if len(cc_parts) > 1 else 0)
    except Exception:
        return "CPU / Offline Mode", 0.0, (0, 0)


def _sha24(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:24]


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
                raise RuntimeError(f"[{self.label}] 进程意外退出 (rc={self.proc.poll()})")
            if line.startswith("__RPC__:"):
                return json.loads(line[len("__RPC__:") :].strip())
            print(f"  {line}", end="", flush=True)

    def start(self) -> None:
        if self.proc is not None and self.proc.poll() is None:
            return
        print(f"🚀 [{self.label}] 加载模型: {self.model_id} ...", flush=True)
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
        print(f"✅ [{self.label}] 就绪 ({info.get('device')}, {info.get('sample_rate')}Hz)", flush=True)

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
                "8GiB",
            ]
        if self.co_resident_96g:
            return [
                "--tts_engine.gpu_memory_fraction",
                "0.34",
                "--vocoder.gpu_memory_fraction",
                "0.08",
                "--preprocessing.total_reserve_bytes",
                "8GiB",
            ]
        return [
            "--tts_engine.gpu_memory_fraction",
            "0.62",
            "--vocoder.gpu_memory_fraction",
            "0.12",
            "--preprocessing.total_reserve_bytes",
            "5GiB",
        ]

    def _supports_reference_sampling_flag(self) -> bool:
        try:
            p = subprocess.run([self.sgl_bin, "serve", "--help"], capture_output=True, text=True, timeout=20, check=False)
            return "reference_sampling" in ((p.stdout or "") + "\n" + (p.stderr or ""))
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
            print(f"✅ [Drama 3] 复用已在线服务 {self.base_url}", flush=True)
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [self.sgl_bin, "serve", "--model-path", self.model_repo, "--port", str(self.port), *self._budget_flags()]
        if self.enable_ras and self._supports_reference_sampling_flag():
            cmd.extend(["--tts_engine.factory.reference_sampling", "true", "--tts_engine.factory.reference_sampling_fallback", "ras"])
            print("✨ [Drama 3] 已开启 Reference Sampling + RAS 高表现力广播剧采样", flush=True)
        env = os.environ.copy()
        env["TORCHDYNAMO_DISABLE"] = "1"
        env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        env["PATH"] = f"{Path(self.sgl_bin).resolve().parent}:/usr/local/cuda/bin:{env.get('PATH', '')}"
        self._log_fh = self.log_path.open("a", encoding="utf-8")
        self.proc = subprocess.Popen(
            cmd,
            stdout=self._log_fh,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
        )
        t0 = time.time()
        tick = 0
        while time.time() - t0 < timeout_s:
            if self.proc.poll() is not None:
                tail = "\n".join(self.log_path.read_text(errors="replace").splitlines()[-45:]) if self.log_path.is_file() else ""
                raise RuntimeError(f"[Drama 3] 启动异常 (rc={self.proc.returncode}):\n{tail}")
            if self.is_healthy():
                print(f"✅ [Drama 3] 服务就绪 ({time.time() - t0:.1f}s) -> {self.base_url}", flush=True)
                return
            if tick > 0 and tick % 10 == 0:
                print(f"   ⏳ [Drama 3] 权重与 CUDA Graph 预热中 ({int(time.time() - t0)}s)...", flush=True)
            tick += 1
            time.sleep(3.0)
        raise TimeoutError(f"[Drama 3] 启动超时 ({timeout_s}s)")

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
            self.start()
        payload = json.dumps(
            {
                "model": self.model_repo,
                "input": drama3_input,
                "response_format": "wav",
                "references": [{"audio_path": str(anchor_wav.resolve()), "text": anchor_text}],
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
            raise RuntimeError(f"[Drama 3] HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:600]}") from exc
        if len(audio_bytes) < 512:
            raise RuntimeError(f"[Drama 3] 返回音频过短 ({len(audio_bytes)} bytes)")
        tmp_raw = out_wav.with_suffix(".raw_d3.wav")
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        tmp_raw.write_bytes(audio_bytes)
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(tmp_raw), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(out_wav)],
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


_WHISPER_PROMPTS: dict[str, str] = {
    "liaozhai_horror": "以下是简体中文聊斋志异广播剧台词：画皮、聂小倩、兰若寺、燕赤霞、宁采臣、陆判官、尸变、崂山道士、考城隍、三更梆子。",
    "cosmic_horror": "以下是简体中文克苏鲁神话广播剧台词：克苏鲁、拉莱耶、密斯卡托尼克大学、印斯茅斯、深潜者、阿卡姆、星之彩、暗夜呢喃、敦威治、修格斯、疯狂山脉。",
    "hayek_economics": "以下是简体中文经济学历史广播剧台词：哈耶克、凯恩斯、通往奴役之路、剑桥大学、红绿灯、法治、价格信号、安全网、布雷顿森林。",
    "monte_cristo_drama": "以下是简体中文基督山伯爵广播剧台词：爱德蒙唐泰斯、基督山伯爵、伊夫堡、马赛港、法老号、梅尔塞苔丝、法利亚神父、维尔福、费尔南、莫尔塞夫、唐格拉尔、卡德鲁斯、摩莱尔、海黛、瓦朗蒂娜、等待和希望。",
    "wealth_of_nations": "以下是简体中文国富论商业思想广播剧台词：亚当斯密、大卫休谟、詹姆斯瓦特、爱丁堡、格拉斯哥、扣针厂、分工、看不见的手、重商主义、东印度公司、自然价格、市场价格、守夜人、道德情操论。",
    "free_to_choose": "以下是简体中文自由选择商业思想广播剧台词：米尔顿弗里德曼、罗丝弗里德曼、芝加哥、铅笔的故事、价格信号、四种花钱的人、大萧条、美联储、职业牌照、教育券、负所得税、通货膨胀、货币现象。",
    "keynes_1936": "以下是简体中文凯恩斯通论宏观思想广播剧台词：约翰梅纳德凯恩斯、庇古教授、剑桥大学、大萧条、有效需求、非自愿失业、节俭悖论、乘数效应、选美比赛、动物精神、流动性偏好、流动性陷阱、财政刺激、布雷顿森林。",
    "extraordinary_delusions": "以下是简体中文大癫狂金融泡沫广播剧台词：郁金香狂热、阿姆斯特丹、球茎、约翰劳、密西西比泡沫、巴黎、南海泡沫、伦敦、艾萨克牛顿、群体癫狂、投机崩盘。",
    "bastiat_unseen": "以下是简体中文巴斯夏讽刺经济学广播剧台词：弗雷德里克巴斯夏、巴黎议会、破窗谬误、看得见的与看不见的、蜡烛请愿书、太阳竞争、断轨铁路、关税保护、机会成本。",
    "one_lesson_econ": "以下是简体中文一课经济学广播剧台词：亨利黑兹利特、二阶后果、破窗、机器取代人工、公共工程、租金管制、最低工资、价格上限、通货膨胀、储蓄投资。",
    "basic_economics": "以下是简体中文常识经济学广播剧台词：价格信号、稀缺资源、房租管制、短缺与过剩、利润与亏损、比较优势、国际贸易、医疗教育、人力资本、常识。",
    "freakonomics_theater": "以下是简体中文魔鬼经济学广播剧台词：激励机制、相扑作弊、房产中介、信息不对称、幼儿园迟到罚款、隐秘动机、因果与相关、数据侦探、反直觉真相。",
    "leisure_class_1899": "以下是简体中文有闲阶级论广播剧台词：索尔斯坦凡勃伦、镀金时代、炫耀性消费、炫耀性闲暇、凡勃伦效应、奢侈品、银勺子、品味符号、社会阶层。",
    "schumpeter_1911": "以下是简体中文熊彼特经济发展理论广播剧台词：约瑟夫熊彼特、维也纳、创造性破坏、企业家精神、银行信用、创新组合、马车与汽车、经济周期、静态均衡。",
    "moral_sentiments_1759": "以下是简体中文道德情操论广播剧台词：亚当斯密、格拉斯哥、同情心、共情、内心公正旁观者、自爱与利他、荣誉与虚荣、崇富轻贫、商业信任、美德。",
    "why_nations_fail": "以下是简体中文为什么国家会失败广播剧台词：诺加莱斯、包容性制度、汲取性制度、光荣革命、产权保护、工业革命、威尼斯、制度惯性、国运。",
    "stock_operator_1923": "以下是简体中文股票大作手回忆录广播剧台词：杰西利弗莫尔、对赌行、华尔街、纸带报价、1907年恐慌、棉花大王、趋势交易、仓位控制、人性弱点、止损。",
    "intelligent_investor": "以下是简体中文聪明的投资者广播剧台词：本杰明格雷厄姆、哥伦比亚大学、市场先生、安全边际、防御型投资者、进取型投资者、烟蒂股、内在价值、巴菲特、复利。",
    "random_walk_wallstreet": "以下是简体中文漫步华尔街广播剧台词：伯顿马尔基尔、随机漫步、飞镖猩猩、空中楼阁、坚实基础、漂亮50、科网泡沫、指数基金、约翰博格、低费率。",
    "behavioral_econ_traps": "以下是简体中文行为经济学剧场台词：系统一、系统二、损失厌恶、心理账户、锚定效应、沉没成本、前景理论、过度自信、助推、认知偏差。",
    "psychology_of_money": "以下是简体中文金钱心理学广播剧台词：复利时间、运气与风险、知足、尾部事件、财务自由、掌控时间、容错空间、低调致富、长期主义、心态。",
    "black_swan_antifragile": "以下是简体中文黑天鹅与反脆弱广播剧台词：黑天鹅、感恩节火鸡、平均斯坦、极端斯坦、肥尾分布、反脆弱、杠铃策略、切身利益在局中、非线性风险。",
    "big_short_2008": "以下是简体中文大空头次贷危机广播剧台词：2008年金融危机、次级房贷、CDO、信用违约互换、CDS、评级机构、三A评级、做空华尔街、雷曼兄弟、泡沫崩盘。",
    "lords_of_finance_1929": "以下是简体中文金融之王1929广播剧台词：金本位、黄金镣铐、英格兰银行、美联储、法兰西银行、德国帝国银行、魏玛通胀、战争赔款、大萧条、货币政策。",
    "ascent_of_money": "以下是简体中文金钱的崛起广播剧台词：美第奇银行、复式记账、荷兰东印度公司、阿姆斯特丹交易所、债券市场、罗斯柴尔德、保险精算、房贷证券化、金融演进。",
    "capitalism_and_freedom": "以下是简体中文资本主义与自由广播剧台词：芝加哥学派、经济自由、货币增长规则、浮动汇率、职业许可垄断、负所得税、教育券、反垄断、财政约束。",
    "game_theory_strategy": "以下是简体中文策略思维与博弈论广播剧台词：囚徒困境、纳什均衡、破釜沉舟、可信威胁、先发优势、价格战、赢家诅咒、倒推法、信号传递、合作博弈。",
    "debt_cycle_machine": "以下是简体中文大债务危机周期剧场台词：信贷扩张、短期债务周期、长期债务周期、去杠杆、和谐去杠杆、央行降息、印钞货币化、通缩萧条、通胀泡沫、经济机器。",
    "xianxia": "以下是普通话简体中文仙侠有声剧对白，请使用简体中文输出。",
}


class LocalChineseWhisperQA:
    def __init__(self, *, domain: str, enabled: bool = True, model_size: str = "small") -> None:
        self.domain = domain
        self.enabled = enabled
        self.model_size = model_size
        self._model: Any = None
        self._available: bool | None = None

    def transcribe(self, wav_path: Path) -> str | None:
        if not self.enabled or self._available is False:
            return None
        if self._model is None:
            try:
                from faster_whisper import WhisperModel  # type: ignore[import-not-found]

                print(f"🔍 [简中 ASR 质检门] 加载 CPU int8 faster-whisper ({self.model_size}, 0 MB 显存)...", flush=True)
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                self._available = True
            except Exception as exc:
                print(f"ℹ️ [简中 ASR 质检门] faster-whisper 不可用 ({exc})，回退纯语速信号质检。", flush=True)
                self._available = False
                return None
        try:
            import numpy as np  # type: ignore[import-not-found]

            raw_pcm = subprocess.check_output(
                ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(wav_path), "-ar", "16000", "-ac", "1", "-f", "f32le", "pipe:1"]
            )
            audio_16k = np.frombuffer(raw_pcm, dtype=np.float32).copy()
            segments, _ = self._model.transcribe(
                audio_16k,
                language="zh",
                beam_size=2,
                vad_filter=(len(audio_16k) > 36000),
                initial_prompt=_WHISPER_PROMPTS.get(self.domain, _WHISPER_PROMPTS["xianxia"]),
            )
            return "".join(seg.text for seg in segments).strip()
        except Exception:
            return None


_HUMAN_VOCAL_CLAUSE_RE = re.compile(
    r"(?:,?\s*(?:accompanied by|with|and)\s+[^,.]*?\b(?:cough(?:ing|s)?|groan(?:ing|s)?|grunt(?:ing|s)?|sigh(?:ing|s)?|scream(?:ing|s)?|sob(?:bing|s)?|voice|vocal)\b[^,.]*)",
    re.IGNORECASE,
)


def sanitize_moss_foley_prompt(prompt: str) -> str:
    cleaned = _HUMAN_VOCAL_CLAUSE_RE.sub("", prompt or "").strip(" ,.")
    if not cleaned:
        cleaned = "Subtle atmospheric environmental foley"
    if "no human voice" not in cleaned.lower():
        cleaned = f"{cleaned}, pure foley sound effect only, no human voice, no speech"
    return cleaned


_ECON_FINANCE_BGM_PRESETS: dict[str, str] = {
    "extraordinary_delusions": "1841 Victorian London baroque-romantic chamber strings, harpsichord and dramatic cello, no modern drums",
    "bastiat_unseen": "1850 Parisian salon witty chamber string quartet, crisp pizzicato cello and light fortepiano, no modern drums",
    "one_lesson_econ": "warm modern documentary acoustic felt piano, upright bass and gentle guitar chamber score, no loud drums",
    "basic_economics": "grounded warm documentary acoustic piano, mellow cello and plucked acoustic bass, no loud drums",
    "freakonomics_theater": "curious playful pizzicato chamber strings, marimba pulse, upright bass and crisp felt piano, no loud rock drums",
    "leisure_class_1899": "1899 Gilded Age ironic waltz chamber strings, solo violin and parlor grand piano, no modern drums",
    "schumpeter_1911": "1911 Vienna expressive romantic string quartet, driving cello ostinato and grand piano, no modern pop drums",
    "moral_sentiments_1759": "1759 Scottish Enlightenment warm intimate baroque chamber strings, solo cello and wooden flute, no modern drums",
    "why_nations_fail": "grand historical documentary cinematic chamber strings, warm horn swell and deep cello, no pop drums",
    "stock_operator_1923": "1920s Wall Street noir late-night upright bass, muted brass chamber accents and moody felt piano, no loud rock drums",
    "intelligent_investor": "calm warm 1950s New York academic study acoustic piano, soft cello and gentle jazz upright bass, no loud drums",
    "random_walk_wallstreet": "breezy witty Manhattan acoustic jazz piano trio with warm upright bass and light acoustic guitar, no loud drums",
    "behavioral_econ_traps": "curious modern documentary felt piano, pulsing pizzicato strings and warm subtle marimba, no heavy drums",
    "psychology_of_money": "warm fireside intimate acoustic guitar, soft felt piano and tender solo cello, no modern drums",
    "black_swan_antifragile": "tense intellectual Mediterranean-meets-chamber cello drone, stark solo piano and suspenseful strings, no pop drums",
    "big_short_2008": "taut 2008 financial thriller low pulsing cello ostinato, moody upright bass and dark minimalist piano, no EDM beat",
    "lords_of_finance_1929": "1929 interwar European tragic chamber orchestra, somber solo cello and dark stately piano, no modern drums",
    "ascent_of_money": "sweeping European historical documentary chamber strings, renaissance lute accents and warm cello, no pop drums",
    "capitalism_and_freedom": "1962 Chicago late-night intellectual acoustic jazz piano, warm upright bass and mellow strings, no loud drums",
    "game_theory_strategy": "clever crisp minimalist chamber strings, rhythmic pizzicato cello and sharp felt piano, no heavy pop drums",
    "debt_cycle_machine": "steady cyclical macro documentary minimalist piano arpeggio, warm cello and subtle string swell, no pop drums",
}


def enrich_anthology_bgm_prompt(prompt: str, *, bgm_style: str) -> str:
    base = (prompt or "").strip().rstrip(".")
    lower = base.lower()
    extras: list[str] = []
    if bgm_style == "liaozhai_horror":
        if "chinese" not in lower:
            extras.append("traditional Chinese midnight folklore instrumental chamber score")
        if "no drums" not in lower and "frame drum" not in lower:
            extras.append("no modern beat, no pop drums")
    elif bgm_style == "cosmic_horror":
        if "dark" not in lower and "ambient" not in lower and "chamber" not in lower:
            extras.append("1920s dark investigative cosmic horror chamber score")
        if "no drums" not in lower and "timpani" not in lower:
            extras.append("no modern beat, no synth trap")
    elif bgm_style == "hayek_economics":
        if "chamber" not in lower and "piano" not in lower and "cello" not in lower:
            extras.append("1944 British historical intellectual drama chamber strings and felt piano")
        if "no drums" not in lower:
            extras.append("no heavy drums, no modern beat")
    elif bgm_style == "monte_cristo_drama":
        if "orchestral" not in lower and "strings" not in lower and "cello" not in lower and "harpsichord" not in lower:
            extras.append("19th-century European romantic orchestral gothic chamber strings and solo cello")
        if "no modern beat" not in lower and "no drums" not in lower:
            extras.append("no modern pop beat, no synth trap")
    elif bgm_style == "wealth_of_nations":
        if "chamber" not in lower and "harpsichord" not in lower and "cello" not in lower and "guitar" not in lower:
            extras.append("18th-century Scottish Enlightenment warm baroque chamber strings, gentle harpsichord and acoustic cello")
        if "no drums" not in lower and "no modern beat" not in lower:
            extras.append("no modern drums, no pop beat")
    elif bgm_style == "free_to_choose":
        if "jazz" not in lower and "piano" not in lower and "bass" not in lower and "acoustic" not in lower:
            extras.append("1980 Chicago warm late-night documentary acoustic felt piano, upright double bass and mellow strings")
        if "no loud drums" not in lower and "no modern beat" not in lower:
            extras.append("no loud drums, no modern synth trap")
    elif bgm_style == "keynes_1936":
        if "cello" not in lower and "piano" not in lower and "strings" not in lower and "chamber" not in lower:
            extras.append("1936 interwar Cambridge reflective chamber strings, deep solo cello and muted upright piano")
        if "no drums" not in lower and "no modern beat" not in lower:
            extras.append("no modern drums, no pop beat")
    elif bgm_style in _ECON_FINANCE_BGM_PRESETS:
        if "chamber" not in lower and "piano" not in lower and "cello" not in lower and "strings" not in lower and "guitar" not in lower:
            extras.append(_ECON_FINANCE_BGM_PRESETS[bgm_style])
        elif "no drums" not in lower and "no loud drums" not in lower and "no modern beat" not in lower:
            extras.append("no pop beat, no synth trap")
    if "no singing" not in lower:
        extras.append("purely instrumental, no vocals, no singing")
    return ", ".join([base, *extras]) if extras else base


def canonical_anthology_stem(cue_sheet: EpisodeCueSheet, *, domain: str) -> str:
    clean_title = re.sub(r'[\\/:*?"<>|\s，。！？：；、“”‘’·—]+', "_", cue_sheet.title).strip("_")
    suffix_map = {
        "liaozhai_horror": "午夜聊斋广播剧母带",
        "cosmic_horror": "克苏鲁声音档案母带",
        "hayek_economics": "1944剑桥夜话思想剧母带",
        "monte_cristo_drama": "基督山伯爵广播剧母带",
        "wealth_of_nations": "国富论思想剧母带",
        "free_to_choose": "自由选择思想剧母带",
        "keynes_1936": "凯恩斯通论思想剧母带",
        "extraordinary_delusions": "大癫狂泡沫剧母带",
        "bastiat_unseen": "巴斯夏讽刺剧母带",
        "one_lesson_econ": "一课经济学剧母带",
        "basic_economics": "常识经济学剧母带",
        "freakonomics_theater": "魔鬼经济学剧母带",
        "leisure_class_1899": "有闲阶级论剧母带",
        "schumpeter_1911": "熊彼特创新剧母带",
        "moral_sentiments_1759": "道德情操论剧母带",
        "why_nations_fail": "国家成败制度剧母带",
        "stock_operator_1923": "股票大作手剧母带",
        "intelligent_investor": "聪明的投资者母带",
        "random_walk_wallstreet": "漫步华尔街剧母带",
        "behavioral_econ_traps": "行为经济学剧母带",
        "psychology_of_money": "金钱心理学剧母带",
        "black_swan_antifragile": "黑天鹅反脆弱母带",
        "big_short_2008": "大空头危机剧母带",
        "lords_of_finance_1929": "金融之王央行剧母带",
        "ascent_of_money": "金钱的崛起剧母带",
        "capitalism_and_freedom": "资本主义自由母带",
        "game_theory_strategy": "博弈论策略剧母带",
        "debt_cycle_machine": "债务大周期剧母带",
    }
    label = suffix_map.get(domain, "Drama3广播剧母带")
    if cue_sheet.mode == "audition_pack":
        return f"{cue_sheet.episode_id}_{label}_试听"
    return f"{cue_sheet.episode_id}_{clean_title}_{label}"


def resolve_targets(spec: str, cue_sheets_dir: Path, auditions_dir: Path) -> list[tuple[str, Path]]:
    ep_files: dict[str, Path] = {}
    for p in sorted(cue_sheets_dir.glob("E*.json")):
        m = re.match(r"^(E\d{3})(?:_|\.|$)", p.name)
        if m:
            ep_files[m.group(1)] = p

    targets: list[tuple[str, Path]] = []
    for token in [t.strip() for t in spec.split(",") if t.strip()]:
        upper = token.upper()
        if upper.startswith("AUDITION"):
            cands = sorted([*auditions_dir.glob("AUDITION*.json"), *cue_sheets_dir.glob("AUDITION*.json")])
            if not cands:
                raise FileNotFoundError(f"未在 {auditions_dir} 找到试听台本 JSON")
            targets.append((cands[0].stem.split("_")[0] + "_AUDITION", cands[0]))
            continue
        m_range = re.match(r"^E?(\d{1,3})\s*-\s*E?(\d{1,3})$", upper)
        if m_range:
            for n in range(int(m_range.group(1)), int(m_range.group(2)) + 1):
                eid = f"E{n:03d}"
                if eid not in ep_files:
                    raise FileNotFoundError(f"未找到 {eid} 台本 ({cue_sheets_dir})")
                targets.append((eid, ep_files[eid]))
            continue
        m_single = re.match(r"^E?(\d{1,3})$", upper)
        if m_single:
            eid = f"E{int(m_single.group(1)):03d}"
            if eid not in ep_files:
                raise FileNotFoundError(f"未找到 {eid} 台本 ({cue_sheets_dir})")
            targets.append((eid, ep_files[eid]))
            continue
        raise ValueError(f"无法解析 --episodes 参数: {token!r}")
    return targets


def check_speaking_rate_ok(cue: TimelineCue, duration_s: float) -> tuple[bool, str]:
    _, spoken = extract_tags_and_spoken_text(cue.text)
    cjk_n = len(_CJK_RE.findall(spoken))
    if cjk_n < 4:
        return (0.30 <= duration_s <= 8.5), f"short_dur={duration_s:.2f}s"
    sec_per_char = duration_s / cjk_n
    if sec_per_char < 0.085:
        return False, f"语速过快/疑似吞字 ({sec_per_char:.3f}s/字)"
    if sec_per_char > 0.78:
        return False, f"语速过慢/疑似尾音拖沓 ({sec_per_char:.3f}s/字)"
    return True, f"{sec_per_char:.3f}s/字"


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
    whisper_qa: LocalChineseWhisperQA,
    domain: str,
) -> tuple[Path, str, bool]:
    prompt_a1 = translate_cue_to_drama3_input(subcue, prof, attempt=1, use_phoneme_pins=False, domain=domain)
    anchor_digest = hashlib.sha256(anchor_wav.read_bytes()).hexdigest()[:16] if anchor_wav.is_file() else "missing"
    dyn_max_tokens = estimate_drama3_max_new_tokens(prompt_a1, language_code="zh")
    cache_key = _sha24(
        {
            "engine": drama_repo,
            "domain": domain,
            "role_id": subcue.role_id,
            "anchor_sha256": anchor_digest,
            "prompt": prompt_a1,
            "max_tok": dyn_max_tokens,
        }
    )
    cached_wav = cache_dir / "drama3_tts" / f"{cache_key}.wav"

    if offline_dry_run:
        _, spoken = extract_tags_and_spoken_text(subcue.text)
        est_dur = max(0.8, min(22.0, len(_CJK_RE.findall(spoken)) / 4.2))
        freq = 165.0 + (hash(subcue.role_id) % 140)
        _write_synthetic_tone_wav(cached_wav, duration_s=est_dur, freq_hz=freq, amp=0.22)
        return cached_wav, prompt_a1, True

    if cached_wav.is_file() and cached_wav.stat().st_size > 1024 and probe_duration_seconds(cached_wav) < 68.0:
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
        dur_s, peak_dbfs = inspect_audio_peak_dbfs(try_wav)
        if dur_s <= 0.0:
            dur_s = probe_duration_seconds(try_wav)
        rate_ok, _ = check_speaking_rate_ok(subcue, dur_s)
        transcript = whisper_qa.transcribe(try_wav)
        qa_res = evaluate_dialogue_qa(
            tagged_prompt=subcue.tts_text or subcue.text,
            canonical_prompt=subcue.text,
            asr_text=transcript or "",
            peak_dbfs=peak_dbfs,
            duration_s=dur_s,
            attempt=attempt,
            language_code="zh",
        )
        passed = rate_ok and (qa_res.passed if transcript is not None else (peak_dbfs > -32.0))
        score = (10.0 if passed else 0.0) + (qa_res.char_recall if transcript is not None else 0.5)
        if score > best_score:
            best_score = score
            best_wav = try_wav
            used_prompt = cur_prompt
            final_qa_passed = passed
        if passed:
            break

    assert best_wav is not None
    shutil.copy2(best_wav, cached_wav)
    for attempt in (1, 2, 3):
        (cache_dir / "drama3_tts" / f"{cache_key}_try{attempt}.wav").unlink(missing_ok=True)
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
    whisper_qa: LocalChineseWhisperQA,
    domain: str,
) -> tuple[Path, dict[str, Any]]:
    subcues = split_cue_into_subcues_for_drama3(cue, max_cjk_chars=105, domain=domain)
    if len(subcues) == 1:
        wav_p, prompt_used, qa_ok = _synthesize_subcue_with_qa(
            cue,
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
        return wav_p, {"drama3_prompt": prompt_used, "qa_passed": qa_ok}

    seg_wavs: list[Path] = []
    prompts: list[str] = []
    all_ok = True
    for sc in subcues:
        wp, pr, ok = _synthesize_subcue_with_qa(
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
        seg_wavs.append(wp)
        prompts.append(pr)
        all_ok = all_ok and ok

    joined = cache_dir / "drama3_tts" / f"{_sha24({'joined': [p.name for p in seg_wavs]})}_joined.wav"
    concat_pcm_wavs(seg_wavs, joined, pause_ms=160.0)
    return joined, {"drama3_prompt": " || ".join(prompts), "qa_passed": all_ok}


def main() -> int:
    parser = argparse.ArgumentParser(description="通用精品广播剧矩阵 · 96GB G4 本地推理与三总线母带引擎")
    parser.add_argument("--studio-dir", required=True)
    parser.add_argument("--episodes", default="AUDITION,E001")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--bgm-style", default="", help="liaozhai_horror / cosmic_horror / hayek_economics / xianxia")
    parser.add_argument("--sgl-bin", default="sgl-omni")
    parser.add_argument("--moss-python", default=sys.executable)
    parser.add_argument("--acestep-python", default=sys.executable)
    parser.add_argument("--sgl-port", type=int, default=8000)
    parser.add_argument("--existing-dir", default="")
    parser.add_argument("--mp3-bitrate", default="320k")
    parser.add_argument("--force-int4", action="store_true")
    parser.add_argument("--disable-ras", action="store_true")
    parser.add_argument("--skip-asr-qa", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--keep-drama-alive", action="store_true")
    parser.add_argument("--offline-dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.studio_dir).resolve()
    out_dir = Path(args.output_dir).resolve()
    cache_dir = Path(args.cache_dir).resolve()
    extra_existing_dir = Path(args.existing_dir).resolve() if args.existing_dir else None
    for sub in ("drama3_tts", "moss_sfx", "acestep_bgm", "logs"):
        (cache_dir / sub).mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    registry = VoiceCastingRegistry.load(root / "voice_casting_registry.json")
    cast_data = json.loads((root / "voice_cast_drama3.json").read_text(encoding="utf-8"))
    characters: dict[str, dict[str, Any]] = cast_data["characters"]
    domain = registry.domain or "liaozhai_horror"
    bgm_style = args.bgm_style or domain

    targets = resolve_targets(args.episodes, root / "cue_sheets", root / "auditions")
    gpu_name, vram_gb, _ = detect_gpu_profile()
    co_resident_96g = (not args.offline_dry_run) and (vram_gb >= 80.0)
    drama_repo = "fishaudio/drama-3-int4" if (args.force_int4 or (not args.offline_dry_run and vram_gb < 80.0)) else "fishaudio/drama-3"

    print(f"🎭 项目: {registry.project_title} | domain={domain} | bgm_style={bgm_style} | GPU={gpu_name} ({vram_gb:.1f}GB)", flush=True)

    drama_client: Drama3ServerClient | None = None
    moss_worker: SubprocessJsonWorker | None = None
    acestep_worker: SubprocessJsonWorker | None = None
    whisper_qa = LocalChineseWhisperQA(domain=domain, enabled=(not args.skip_asr_qa and not args.offline_dry_run))

    if not args.offline_dry_run:
        drama_client = Drama3ServerClient(
            sgl_bin=args.sgl_bin,
            model_repo=drama_repo,
            port=args.sgl_port,
            co_resident_96g=co_resident_96g,
            enable_ras=not args.disable_ras,
            log_path=cache_dir / "logs" / f"sglang_omni_{registry.project_id}.log",
        )
        moss_worker = SubprocessJsonWorker("MOSS-SFX v2.0", args.moss_python, _MOSS_WORKER_CODE, "OpenMOSS-Team/MOSS-SoundEffect-v2.0")
        acestep_worker = SubprocessJsonWorker("ACE-Step 1.5 XL", args.acestep_python, _ACESTEP_WORKER_CODE, "ACE-Step/acestep-v15-xl-turbo-diffusers")
        if co_resident_96g:
            drama_client.start()

    rendered: list[dict[str, Any]] = []
    try:
        for label, cs_path in targets:
            cue_sheet = EpisodeCueSheet.load(cs_path)
            if args.skip_existing and cue_sheet.mode != "audition_pack":
                check_dirs = [out_dir] + ([extra_existing_dir] if extra_existing_dir and extra_existing_dir.exists() else [])
                existing = [p for d in check_dirs for p in sorted(d.glob(f"{cue_sheet.episode_id}_*.mp3"))]
                if existing:
                    print(f"⏭️  [{cue_sheet.episode_id}] 已存在成片 {existing[-1].name}，跳过。", flush=True)
                    continue

            t_ep = time.time()
            dialogue_cues = [c for c in cue_sheet.cues if c.kind == "dialogue"]
            sfx_cues = [c for c in cue_sheet.cues if c.kind == "sfx"]
            print(f"\n▶️  开始合成 [{label}] 《{cue_sheet.title}》 (对白 {len(dialogue_cues)} | 拟音 {len(sfx_cues)} | 配乐 {len(cue_sheet.acts)} 幕)", flush=True)

            cue_audio_map: dict[str, Path] = {}
            cue_meta_map: dict[str, dict[str, Any]] = {}
            act_bgm_map: dict[str, Path] = {}

            # 1. Dialogue Synthesis
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
                    print(f"   🎙️ 对白进度: {idx}/{len(dialogue_cues)} ({cue.cue_id} [{cue.speaker_name or cue.role_id}] -> {probe_duration_seconds(wav_p):.1f}s)", flush=True)

            if dialogue_cues and not args.offline_dry_run and not co_resident_96g and drama_client is not None:
                drama_client.close()

            # 2. Foreground Foley SFX (MOSS v2.0 + SHA-256 Cache)
            for idx, cue in enumerate(sfx_cues, 1):
                raw_prompt = cue.sfx_prompt or (registry.sonic_motifs[cue.motif_id].sfx_prompt if cue.motif_id in registry.sonic_motifs else "")
                prompt = sanitize_moss_foley_prompt(raw_prompt)
                sfx_key = _sha24({"prompt": prompt, "dur": round(cue.duration_seconds, 2)})
                sfx_wav = cache_dir / "moss_sfx" / f"{sfx_key}.wav"
                if args.offline_dry_run:
                    _write_synthetic_tone_wav(sfx_wav, duration_s=cue.duration_seconds, freq_hz=125.0, amp=0.14)
                elif not sfx_wav.is_file():
                    assert moss_worker is not None
                    raw_moss = cache_dir / "moss_sfx" / f"{sfx_key}_raw.wav"
                    try:
                        moss_worker.request({"prompt": prompt, "seconds": cue.duration_seconds, "out_path": str(raw_moss)})
                    except RuntimeError:
                        if acestep_worker is not None:
                            acestep_worker.close()
                        moss_worker.close()
                        moss_worker.request({"prompt": prompt, "seconds": cue.duration_seconds, "out_path": str(raw_moss)})
                    subprocess.run(
                        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw_moss), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(sfx_wav)],
                        check=True,
                    )
                    raw_moss.unlink(missing_ok=True)
                cue_audio_map[cue.cue_id] = sfx_wav

            if not co_resident_96g and moss_worker is not None:
                moss_worker.close()

            # 3. Per-Act Instrumental BGM (ACE-Step 1.5 XL + SHA-256 Cache)
            for act_spec in cue_sheet.acts:
                target_dur = 75.0 if float(act_spec.bgm_duration_s or 75.0) >= 60.0 else 48.0
                bgm_prompt = enrich_anthology_bgm_prompt(act_spec.bgm_prompt, bgm_style=bgm_style)
                bgm_key = _sha24({"prompt": bgm_prompt, "vocal_language": "unknown", "dur": round(target_dur, 1)})
                bgm_wav = cache_dir / "acestep_bgm" / f"{bgm_key}.wav"
                if args.offline_dry_run:
                    _write_synthetic_tone_wav(bgm_wav, duration_s=12.0, freq_hz=140.0, amp=0.11)
                elif not bgm_wav.is_file():
                    assert acestep_worker is not None
                    raw_bgm = cache_dir / "acestep_bgm" / f"{bgm_key}_raw.wav"
                    print(f"   🎻 [ACE-Step 1.5 XL] 生成配乐 {act_spec.act_id} ({target_dur:.0f}s): {act_spec.title}", flush=True)
                    bgm_req = {"prompt": bgm_prompt, "lyrics": "[Instrumental]", "vocal_language": "unknown", "duration_s": target_dur, "out_path": str(raw_bgm)}
                    try:
                        acestep_worker.request(bgm_req)
                    except RuntimeError:
                        if moss_worker is not None:
                            moss_worker.close()
                        acestep_worker.close()
                        acestep_worker.request(bgm_req)
                    subprocess.run(
                        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw_bgm), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(bgm_wav)],
                        check=True,
                    )
                    raw_bgm.unlink(missing_ok=True)
                act_bgm_map[act_spec.act_id] = bgm_wav

            if not co_resident_96g and acestep_worker is not None:
                acestep_worker.close()

            # 4. 3-Bus -16 LUFS Mastering + SRT + Atomic .done
            stem_prefix = canonical_anthology_stem(cue_sheet, domain=domain)
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
            rendered.append(summary_item)
            print(
                f"✅ [{cue_sheet.episode_id}] 成片出炉！时长 {master_res['total_duration_s']/60.0:.2f} 分钟 | "
                f"响度 {lufs:.1f} LUFS (TP {tp_db:.1f} dBTP) | 耗时 {time.time() - t_ep:.1f}s\n"
                f"   🎧 MP3: {master_res['master_mp3']}",
                flush=True,
            )
    finally:
        if drama_client is not None and not args.keep_drama_alive:
            drama_client.close()
        elif drama_client is not None and args.keep_drama_alive:
            print(f"♻️ [Drama 3] --keep-drama-alive 已开启，保持服务常驻 {drama_client.base_url} 供下一批秒级复用", flush=True)
        if moss_worker is not None:
            moss_worker.close()
        if acestep_worker is not None:
            acestep_worker.close()

    print(f"\n🎉 {registry.project_title} 本批次完成 {len(rendered)} 项 -> {out_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
