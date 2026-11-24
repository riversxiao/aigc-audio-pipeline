#!/usr/bin/env python3
"""《商战大瓜英语局》Silicon Gossip V2 · Colab 96GB G4 零成本一键渲染与云盘归档引擎 (v2.0.0).

V2 架构核心升级（100% 零商业语音 API 费用 · 0% 合成 TTS 锚点）：
1. 【6 位 `v2_real_human_studio` 真人棚录干声锚点自动装配】：
   - `host_xiaowei` (小微) <- 仓库内置 `host_zhiwei.{wav,txt}`（小宇宙自然中英混说女主播）
   - `guest_laozhou` (大周) <- 仓库内置 `guest_laozhou.{wav,txt}`（接地气男捧哏，自动触发去闷 EQ 与右桌位声像）
   - `board_ilya` (董事会代表 Ilya) <- 复用 Drive 已精选 `alistair_finch.{wav,txt}`（冷峻英伦/欧陆学者）
   - `satya_nadella` (微软 CEO 纳德拉) <- 复用 Drive 已精选 `rajiv_menon.{wav,txt}`（47.8dB 印度商界播客真声）
   - `exec_female` (OpenAI 女高管) <- 复用 Drive 已精选 `victoria_vance.{wav,txt}`（Meta Expresso ex02 48kHz 美音女声）
   - `sam_altman` (Sam Altman) <- Meta Expresso `ex01`（48kHz 硅谷年轻美式创始人男声，HuggingFace CDN Parquet 秒级拉取并永久缓存云盘）
2. 【`hotline_roundtable` 双语混血表演引擎】：
   - 中文/中英混说双主播对谈自动剥离僵硬朗诵词，保留自然笑声 `[light chuckle]` 与呼吸气口，零播音腔；
   - 纯英文 20 秒名场面闪回保留完整戏剧爆发标签（`[angry]`, `[coldly]`, `[shocked]`, `[firmly]`）；
   - 片尾 90 秒 4 句职场狠话带走卡自动复用 `1.0x` Drama 3 干声缓存，经 FFmpeg 不降调 `atempo=0.850` 确定性输出慢速 + 原速跟读。
3. 【纯干声吐槽幕零配乐直出 + 明快现代商战 OST】：
   - 双主播日常吐槽幕（`bgm_prompt == ""`）严格跳过 ACE-Step 零配乐直出，彻底告别沉闷大提琴；
   - 仅在冷开场、3 段 20 秒名场面闪回与片尾跟读卡渲染《大空头》/《社交网络》轻快纯器乐律动。
4. 【96GB G4 极速冷启动 + 云盘双通道原子归档 + 完工立停计费】：
   - 复用 `MyDrive/AI_Workstation/AudioStudio_G4_Cache/` 缓存的 `sglang-omni` 与 `MOSS-TTS` 源码包；
   - 渲染完成后原子同步 WAV / MP3 / 双语 `.srt` / `.json` / `.done` 至 Google Drive，并支持 `--auto-unassign` 自动释放 G4 实例。
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any
import wave

if os.path.isdir("/content/drive/My Drive") and not os.path.exists("/content/drive/MyDrive"):
    os.symlink("/content/drive/My Drive", "/content/drive/MyDrive")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
for _p in (REPO_ROOT / "src", SCRIPT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from aigc_audio_pipeline.batch_queue import measure_ebur128  # noqa: E402
from aigc_audio_pipeline.drama3_adapter import DRAMA3_ANCHOR_SAMPLE_RATE  # noqa: E402
from aigc_audio_pipeline.mixer import master_episode_three_bus  # noqa: E402
from aigc_audio_pipeline.models import (  # noqa: E402
    EpisodeCueSheet,
    VoiceCastingRegistry,
    extract_tags_and_spoken_text,
    utc_now_iso,
)
from launch_g4_global_edge_drama3 import (  # noqa: E402
    ANCHOR_SCHEMA_VERSION,
    DRIVE_ROOT,
    NVME_ROOT,
    OFFLINE_STUB_SOURCE_NAME,
    build_isolated_venvs,
    drive_api_ensure_folder,
    drive_api_upsert_file,
    ensure_uv_and_hf_tools,
    get_drive_token,
    stage_hf_models_nvme,
    validate_production_voice_cast,
)
from prepare_global_edge_voice_anchors import (  # noqa: E402
    _write_stub_speech_like_raw_wav,
    condition_studio_anchor_wav as condition_anchor_wav,
    probe_duration_seconds,
)
from run_global_edge_96gb_studio import (  # noqa: E402
    _ACESTEP_WORKER_CODE,
    _CJK_RE,
    _MOSS_WORKER_CODE,
    BilingualWhisperQA,
    Drama3ServerClient,
    SubprocessJsonWorker,
    _sha24,
    _write_offline_voiced_wav,
    detect_gpu_profile,
    sanitize_moss_foley_prompt,
    synthesize_cue_chunked,
)

PROJECT_DIR = REPO_ROOT / "projects" / "silicon_gossip"
META_DIR = PROJECT_DIR / "00_节目圣经与选角档案"
CUE_SHEETS_DIR = PROJECT_DIR / "02_分集广播剧台本"
BUFFETT_ANCHORS_DIR = REPO_ROOT / "projects" / "buffett_letters" / "00_节目圣经与第一季12期总纲" / "voice_anchors"

DRIVE_GLOBAL_EDGE_STUDIO_DIR = (
    DRIVE_ROOT
    / "《跨境底牌：硅深暗战》Global_Edge_双语商战广播剧"
    / "01_Colab_96GB_FishDrama3_工作台"
)
DRIVE_SHOW_FOLDER_NAME = "《商战大瓜英语局》Silicon_Gossip_V2_轻英语广播剧"
DRIVE_WORKBENCH_FOLDER_NAME = "01_Colab_96GB_FishDrama3_工作台"
DRIVE_MASTERS_FOLDER_NAME = "02_分集双语成片母带_WAV_MP3_SRT"

DRIVE_PROJECT_ROOT = DRIVE_ROOT / DRIVE_SHOW_FOLDER_NAME
DRIVE_STUDIO_DIR = DRIVE_PROJECT_ROOT / DRIVE_WORKBENCH_FOLDER_NAME
DRIVE_ANCHORS_DIR = DRIVE_STUDIO_DIR / "voice_anchors"
DRIVE_OUTPUTS_DIR = DRIVE_STUDIO_DIR / "outputs"
DRIVE_MAIN_MASTERS_DIR = DRIVE_PROJECT_ROOT / DRIVE_MASTERS_FOLDER_NAME

WORK_ROOT = NVME_ROOT / "silicon_gossip_work"


class SiliconGossipBilingualWhisperQA(BilingualWhisperQA):
    """Zero-VRAM CPU int8 `faster-whisper` QA tuned for Silicon Gossip bilingual real-world business episodes."""

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
                    f"🔍 [V2 双语 ASR 质检门] 加载 CPU int8 faster-whisper ({self.model_size}, 0 MB 显存占用)...",
                    flush=True,
                )
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                self._available = True
            except Exception as exc:
                print(f"ℹ️ [V2 双语 ASR 质检门] faster-whisper 未安装 ({exc})，启用纯语速边界质检。", flush=True)
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
                        "OpenAI, ChatGPT, Sam Altman, Satya Nadella, Ilya, Google Meet, Microsoft, "
                        "consistently candid, Let's be candid, completely blindsided, I'm a bit blindsided here, "
                        "Not on my watch, Seven hundred people signed, We have the leverage, Step down, walk away, "
                        "Let's talk terms, We're back in business, effective immediately."
                    ),
                )
                return " ".join(seg.text.strip() for seg in segments if seg.text.strip()).strip()

            zh_prompt = (
                "以下是现代商业英语播客《商战大瓜英语局》小微和大周的中英双语对谈："
                "OpenAI、ChatGPT、奥特曼、伊利亚、微软、纳德拉、榜一大哥、居委会大爷、"
                "consistently candid、Let's be candid、blindsided、I'm a bit blindsided here、"
                "Not on my watch、We have the leverage、walk away、offer。"
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
            print(f"⚠️ [V2 双语 ASR 质检门] 单句转写回退纯语速质检 ({exc})", flush=True)
            return None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sanitize_modern_bgm_prompt(raw_prompt: str) -> str:
    """Keep upbeat modern Big Short / Social Network BGM prompts crisp and strictly instrumental."""
    prompt = " ".join((raw_prompt or "").split()).strip(" ,.")
    if not prompt:
        return ""
    lower = prompt.lower()
    suffixes: list[str] = []
    if "instrumental" not in lower:
        suffixes.append("strictly instrumental")
    if "no vocals" not in lower:
        suffixes.append("no vocals")
    if "no singing" not in lower:
        suffixes.append("no singing")
    if suffixes:
        prompt = f"{prompt}, {', '.join(suffixes)}"
    return prompt


def _fetch_expresso_us_male_anchor(
    dst_wav: Path,
    dst_txt: Path,
    *,
    preferred_speakers: tuple[str, ...] = ("ex01", "ex03"),
) -> str:
    """Fetch a clean 48kHz studio US young male reference anchor from `ylacombe/expresso` via HF Parquet CDN."""
    try:
        import pyarrow.parquet as pq  # type: ignore[import-not-found]
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyarrow"], check=True)
        import pyarrow.parquet as pq  # type: ignore[import-not-found]

    from huggingface_hub import HfApi, hf_hub_download  # type: ignore[import-not-found]

    api = HfApi()
    repo_files = api.list_repo_files("ylacombe/expresso", repo_type="dataset")
    pq_files = sorted(f for f in repo_files if f.endswith(".parquet") and "train" in f)
    if not pq_files:
        pq_files = sorted(f for f in repo_files if f.endswith(".parquet"))
    if not pq_files:
        raise RuntimeError("No parquet shards found in dataset ylacombe/expresso")

    selected_clips: list[tuple[Path, str, float]] = []
    chosen_speaker = ""
    total_dur = 0.0

    with tempfile.TemporaryDirectory(prefix="expresso_ex01_") as tmpdir:
        tmp_path = Path(tmpdir)
        for spk in preferred_speakers:
            selected_clips.clear()
            total_dur = 0.0
            for pq_rel in pq_files:
                local_pq = Path(
                    hf_hub_download(
                        repo_id="ylacombe/expresso",
                        repo_type="dataset",
                        filename=pq_rel,
                    )
                )
                table = pq.read_table(local_pq)
                cols = set(table.column_names)
                spk_col = "speaker_id" if "speaker_id" in cols else ("speaker" if "speaker" in cols else "")
                style_col = "style" if "style" in cols else ""
                text_col = "text" if "text" in cols else ("transcript" if "transcript" in cols else "")
                audio_col = "audio" if "audio" in cols else ""
                if not (spk_col and text_col and audio_col):
                    continue

                rows = table.to_pylist()
                for idx, row in enumerate(rows):
                    if str(row.get(spk_col, "")).strip().lower() != spk:
                        continue
                    style_val = str(row.get(style_col, "default")).strip().lower() if style_col else "default"
                    if style_val not in ("default", "read", "enunciated", "narration", ""):
                        continue
                    txt = " ".join(str(row.get(text_col, "")).split()).strip()
                    if len(txt) < 28 or len(txt) > 180 or any(ch in txt for ch in ("<", ">", "[", "]")):
                        continue
                    audio_obj = row.get(audio_col)
                    if not isinstance(audio_obj, dict) or not audio_obj.get("bytes"):
                        continue
                    raw_clip = tmp_path / f"{spk}_{len(selected_clips):02d}_{idx}.bin"
                    raw_clip.write_bytes(audio_obj["bytes"])
                    norm_clip = tmp_path / f"{spk}_{len(selected_clips):02d}_{idx}.wav"
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-hide_banner",
                            "-loglevel",
                            "error",
                            "-i",
                            str(raw_clip),
                            "-ar",
                            str(DRAMA3_ANCHOR_SAMPLE_RATE),
                            "-ac",
                            "1",
                            "-c:a",
                            "pcm_s16le",
                            str(norm_clip),
                        ],
                        check=True,
                    )
                    dur = probe_duration_seconds(norm_clip)
                    if 2.6 <= dur <= 8.5:
                        selected_clips.append((norm_clip, txt, dur))
                        total_dur += dur
                        if total_dur >= 10.5 and len(selected_clips) >= 2:
                            chosen_speaker = spk
                            break
                if chosen_speaker:
                    break
            if chosen_speaker:
                break

        if not selected_clips:
            raise RuntimeError(f"Could not extract clean US male anchor from ylacombe/expresso ({preferred_speakers})")

        # Concatenate clips with 0.22s natural breath silence, then apply broadcast studio conditioning (zero afftdn!)
        gap_wav = tmp_path / "gap.wav"
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
                f"anullsrc=r={DRAMA3_ANCHOR_SAMPLE_RATE}:cl=mono",
                "-t",
                "0.22",
                "-c:a",
                "pcm_s16le",
                str(gap_wav),
            ],
            check=True,
        )
        concat_list = tmp_path / "concat.txt"
        lines: list[str] = []
        for i, (clip_p, _, _) in enumerate(selected_clips):
            lines.append(f"file '{clip_p.resolve()}'")
            if i + 1 < len(selected_clips):
                lines.append(f"file '{gap_wav.resolve()}'")
        concat_list.write_text("\n".join(lines) + "\n", encoding="utf-8")

        raw_joined = tmp_path / "joined_raw.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-ar",
                str(DRAMA3_ANCHOR_SAMPLE_RATE),
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(raw_joined),
            ],
            check=True,
        )
        condition_anchor_wav(raw_joined, dst_wav)
        verbatim = " ".join(txt for _, txt, _ in selected_clips).strip()
        dst_txt.write_text(verbatim + "\n", encoding="utf-8")
        print(
            f"🎙️ [Meta Expresso {chosen_speaker}] 成功提取 48kHz 硅谷美音男主干声锚点 "
            f"({probe_duration_seconds(dst_wav):.2f}s, {len(selected_clips)} 句拼接)",
            flush=True,
        )
        return f"hf_dataset:ylacombe/expresso:{chosen_speaker}_default_studio"


def assemble_silicon_gossip_studio(
    local_studio: Path,
    *,
    offline_dry_run: bool = False,
    refresh_anchors: bool = False,
) -> Path:
    """Assemble `voice_casting_registry.json`, `cue_sheets/`, 6 real-human studio anchors, and `voice_cast_drama3.json`."""
    local_studio.mkdir(parents=True, exist_ok=True)
    anchors_dir = local_studio / "voice_anchors"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    cues_dst = local_studio / "cue_sheets"
    cues_dst.mkdir(parents=True, exist_ok=True)

    reg_src = META_DIR / "voice_casting_registry.json"
    if not reg_src.is_file():
        raise FileNotFoundError(f"Missing Silicon Gossip registry: {reg_src}")
    shutil.copy2(reg_src, local_studio / "voice_casting_registry.json")
    registry = VoiceCastingRegistry.load(local_studio / "voice_casting_registry.json")

    for jp in sorted(CUE_SHEETS_DIR.glob("*.json")):
        shutil.copy2(jp, cues_dst / jp.name)

    # Role -> candidate (source_wav, source_txt, provenance_label) search paths
    role_sources: dict[str, list[tuple[Path, Path, str]]] = {
        "host_xiaowei": [
            (
                DRIVE_ANCHORS_DIR / "host_xiaowei.wav",
                DRIVE_ANCHORS_DIR / "host_xiaowei.txt",
                "drive_cached:host_xiaowei_studio",
            ),
            (
                BUFFETT_ANCHORS_DIR / "host_zhiwei.wav",
                BUFFETT_ANCHORS_DIR / "host_zhiwei.txt",
                "repo_real_human:openmoss_host_zhiwei_studio",
            ),
        ],
        "guest_huaiyuan": [
            (
                DRIVE_ANCHORS_DIR / "guest_huaiyuan.wav",
                DRIVE_ANCHORS_DIR / "guest_huaiyuan.txt",
                "drive_cached:openmoss_dry_guest_huaiyuan_studio",
            ),
            (
                BUFFETT_ANCHORS_DIR / "guest_huaiyuan.wav",
                BUFFETT_ANCHORS_DIR / "guest_huaiyuan.txt",
                "repo_real_human:openmoss_dry_guest_huaiyuan_studio",
            ),
        ],
        "guest_laozhou": [
            (
                DRIVE_ANCHORS_DIR / "guest_laozhou.wav",
                DRIVE_ANCHORS_DIR / "guest_laozhou.txt",
                "drive_cached:guest_laozhou_studio",
            ),
            (
                BUFFETT_ANCHORS_DIR / "guest_laozhou.wav",
                BUFFETT_ANCHORS_DIR / "guest_laozhou.txt",
                "repo_real_human:mainland_guest_laozhou_studio",
            ),
        ],
        "board_ilya": [
            (
                DRIVE_ANCHORS_DIR / "board_ilya.wav",
                DRIVE_ANCHORS_DIR / "board_ilya.txt",
                "drive_real_person:ilya_sutskever_022_ai_studio",
            ),
            (
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "custom_anchors" / "alistair_finch.wav",
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "custom_anchors" / "alistair_finch.txt",
                "drive_real_human:openslr83_southern_male_alistair_finch",
            ),
            (
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "voice_anchors" / "alistair_finch.wav",
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "voice_anchors" / "alistair_finch.txt",
                "drive_real_human:openslr83_southern_male_alistair_finch",
            ),
        ],
        "satya_nadella": [
            (
                DRIVE_ANCHORS_DIR / "satya_nadella.wav",
                DRIVE_ANCHORS_DIR / "satya_nadella.txt",
                "drive_cached:satya_nadella_indian_exec_studio",
            ),
            (
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "custom_anchors" / "rajiv_menon.wav",
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "custom_anchors" / "rajiv_menon.txt",
                "drive_real_human:sarvam_indian_business_podcaster_rajiv_menon",
            ),
            (
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "voice_anchors" / "rajiv_menon.wav",
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "voice_anchors" / "rajiv_menon.txt",
                "drive_real_human:sarvam_indian_business_podcaster_rajiv_menon",
            ),
        ],
        "exec_female": [
            (
                DRIVE_ANCHORS_DIR / "exec_female.wav",
                DRIVE_ANCHORS_DIR / "exec_female.txt",
                "drive_cached:exec_female_studio",
            ),
            (
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "custom_anchors" / "victoria_vance.wav",
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "custom_anchors" / "victoria_vance.txt",
                "drive_real_human:meta_expresso_ex02_victoria_vance",
            ),
            (
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "voice_anchors" / "victoria_vance.wav",
                DRIVE_GLOBAL_EDGE_STUDIO_DIR / "voice_anchors" / "victoria_vance.txt",
                "drive_real_human:meta_expresso_ex02_victoria_vance",
            ),
        ],
        "sam_altman": [
            (
                DRIVE_ANCHORS_DIR / "sam_altman.wav",
                DRIVE_ANCHORS_DIR / "sam_altman.txt",
                "drive_real_person:sam_altman_014_ai_studio",
            ),
        ],
    }

    stub_freqs = {
        "host_xiaowei": 215.0,
        "guest_huaiyuan": 126.0,
        "guest_laozhou": 128.0,
        "sam_altman": 135.0,
        "board_ilya": 116.0,
        "satya_nadella": 124.0,
        "exec_female": 208.0,
    }

    characters: dict[str, dict[str, Any]] = {}
    for role_id, prof in registry.roles.items():
        dst_wav = anchors_dir / f"{role_id}.wav"
        dst_txt = anchors_dir / f"{role_id}.txt"
        source_voice_name = ""

        # Reuse local NVMe anchor if valid & not refreshing
        if not refresh_anchors and dst_wav.is_file() and dst_txt.is_file() and dst_wav.stat().st_size >= 4096:
            try:
                with wave.open(str(dst_wav), "rb") as wf:
                    if wf.getnchannels() == 1 and wf.getsampwidth() == 2 and wf.getframerate() == DRAMA3_ANCHOR_SAMPLE_RATE:
                        source_voice_name = f"nvme_cached:{role_id}_studio"
            except Exception:
                pass

        if not source_voice_name:
            for cand_wav, cand_txt, prov in role_sources.get(role_id, []):
                if cand_wav.is_file() and cand_txt.is_file() and cand_wav.stat().st_size >= 4096:
                    condition_anchor_wav(cand_wav, dst_wav)
                    shutil.copy2(cand_txt, dst_txt)
                    source_voice_name = prov
                    print(f"✅ [真人棚录锚点复用] {role_id} ({prof.display_name}) <- {cand_wav.name}", flush=True)
                    break

        if not source_voice_name and role_id == "sam_altman" and not offline_dry_run:
            source_voice_name = _fetch_expresso_us_male_anchor(dst_wav, dst_txt)

        if not source_voice_name:
            if offline_dry_run:
                raw_stub = anchors_dir / f".{role_id}_stub_raw.wav"
                _write_stub_speech_like_raw_wav(raw_stub, base_freq_hz=stub_freqs.get(role_id, 140.0), duration_s=10.0)
                condition_anchor_wav(raw_stub, dst_wav)
                raw_stub.unlink(missing_ok=True)
                _, clean_aud = extract_tags_and_spoken_text(prof.audition_line)
                dst_txt.write_text((clean_aud or f"Offline stub anchor for {role_id}.") + "\n", encoding="utf-8")
                source_voice_name = OFFLINE_STUB_SOURCE_NAME
            else:
                raise FileNotFoundError(
                    f"Missing genuine real-human studio anchor for role {role_id!r}! "
                    f"Ensure Google Drive is mounted at {DRIVE_ROOT} so curated anchors can be reused."
                )

        anchor_text = dst_txt.read_text(encoding="utf-8").strip()
        characters[role_id] = {
            "role_id": role_id,
            "display_name": prof.display_name,
            "gender": prof.gender,
            "language_code": prof.language_code,
            "accent_code": prof.accent_code,
            "source_voice_name": source_voice_name,
            "anchor_wav": f"voice_anchors/{role_id}.wav",
            "anchor_text": anchor_text,
            "duration_s": round(probe_duration_seconds(dst_wav), 3),
            "sha256": _sha256_file(dst_wav),
        }

    cast_manifest = {
        "anchor_schema_version": ANCHOR_SCHEMA_VERSION,
        "project_id": registry.project_id,
        "project_title": registry.project_title,
        "domain": registry.domain,
        "updated_at": utc_now_iso(),
        "characters": characters,
    }
    vc_path = local_studio / "voice_cast_drama3.json"
    vc_path.write_text(json.dumps(cast_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ok, errs = validate_production_voice_cast(
        local_studio,
        required_roles=list(registry.roles.keys()),
        allow_offline_stub=offline_dry_run,
    )
    if not ok:
        raise RuntimeError(
            "声纹门禁 validate_production_voice_cast() 未通过：\n  - " + "\n  - ".join(errs)
        )

    # Persist all 6 anchors into Silicon Gossip's Drive studio folder for instant future reuse
    if not offline_dry_run and DRIVE_ROOT.exists():
        try:
            DRIVE_ANCHORS_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vc_path, DRIVE_STUDIO_DIR / "voice_cast_drama3.json")
            for f in sorted(anchors_dir.glob("*")):
                if f.is_file() and f.suffix.lower() in (".wav", ".txt"):
                    shutil.copy2(f, DRIVE_ANCHORS_DIR / f.name)
        except Exception as exc:
            print(f"⚠️ 云盘缓存锚点跳过 ({exc})", flush=True)

    return local_studio


def resolve_v2_targets(cue_dir: Path, spec: str) -> list[tuple[str, Path]]:
    """Resolve `--episodes` (`V2_E001`, `V2_E001,V2_E002`, `ALL`) against Silicon Gossip cue sheets."""
    all_sheets: dict[str, Path] = {}
    for jp in sorted(cue_dir.glob("*.json")):
        try:
            raw = json.loads(jp.read_text(encoding="utf-8"))
            eid = str(raw.get("episode_id", "")).strip().upper()
            if eid:
                all_sheets[eid] = jp
        except Exception:
            continue

    tokens = [t.strip().upper() for t in (spec or "V2_E001").split(",") if t.strip()]
    if not tokens:
        raise ValueError("Empty --episodes specification")

    targets: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for tok in tokens:
        if tok == "ALL":
            for eid in sorted(all_sheets):
                if eid not in seen:
                    seen.add(eid)
                    targets.append((eid, all_sheets[eid]))
            continue
        if tok in all_sheets:
            if tok not in seen:
                seen.add(tok)
                targets.append((tok, all_sheets[tok]))
            continue
        alt = f"V2_{tok}" if not tok.startswith("V2_") else tok
        if alt in all_sheets:
            if alt not in seen:
                seen.add(alt)
                targets.append((alt, all_sheets[alt]))
            continue
        raise FileNotFoundError(f"未在 {cue_dir} 找到剧集台本 {tok!r}（可用: {sorted(all_sheets)}）")
    return targets


def canonical_v2_stem(cue_sheet: EpisodeCueSheet) -> str:
    safe_title = re.sub(r"[^\w\u4e00-\u9fff]+", "_", cue_sheet.title).strip("_")[:28]
    return f"{cue_sheet.episode_id}_{safe_title}" if safe_title else cue_sheet.episode_id


def sync_v2_outputs_to_drive(local_outputs: Path) -> None:
    """Atomically sync rendered V2 masters (WAV, MP3, SRT, JSON, .done) to Google Drive (single-copy, no duplicates)."""
    if not local_outputs.is_dir():
        return
    done_files = sorted(local_outputs.glob("*.done"))
    if not done_files:
        return

    tok = get_drive_token()
    drive_out_id = ""
    drive_main_id = ""
    if tok:
        try:
            show_id = drive_api_ensure_folder(DRIVE_SHOW_FOLDER_NAME, "root", tok)
            wb_id = drive_api_ensure_folder(DRIVE_WORKBENCH_FOLDER_NAME, show_id, tok)
            drive_out_id = drive_api_ensure_folder("outputs", wb_id, tok)
            drive_main_id = drive_api_ensure_folder(DRIVE_MASTERS_FOLDER_NAME, show_id, tok)
        except Exception as exc:
            print(f"⚠️ Drive API 目录初始化回退 FUSE ({exc})", flush=True)

    use_api = bool(tok and drive_out_id and drive_main_id)
    if not use_api and DRIVE_ROOT.exists():
        DRIVE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        DRIVE_MAIN_MASTERS_DIR.mkdir(parents=True, exist_ok=True)

    for done_p in done_files:
        stem = done_p.stem
        siblings = [
            done_p.with_suffix(ext)
            for ext in (".mp3", ".srt", ".json", ".wav", ".done")
            if done_p.with_suffix(ext).is_file()
        ]
        for fpath in siblings:
            api_ok = False
            if use_api:
                try:
                    drive_api_upsert_file(fpath, drive_out_id, tok)
                    drive_api_upsert_file(fpath, drive_main_id, tok)
                    api_ok = True
                except Exception as exc:
                    print(f"⚠️ Drive API 上传 {fpath.name} 失败，回退 FUSE ({exc})", flush=True)
            if not api_ok and DRIVE_ROOT.exists():
                for tdir in (DRIVE_OUTPUTS_DIR, DRIVE_MAIN_MASTERS_DIR):
                    tdir.mkdir(parents=True, exist_ok=True)
                    dst = tdir / fpath.name
                    if not dst.is_file() or dst.stat().st_size != fpath.stat().st_size:
                        shutil.copy2(fpath, dst)
        print(f"☁️  [{stem}] 已原子同步至 Google Drive: {DRIVE_MAIN_MASTERS_DIR}", flush=True)


def run_studio(args: argparse.Namespace) -> int:
    work_dir = Path(args.work_dir).resolve()
    local_studio = work_dir / "studio"
    out_dir = Path(args.output_dir).resolve() if args.output_dir else (work_dir / "outputs")
    cache_dir = Path(args.cache_dir).resolve() if args.cache_dir else (work_dir / "cache")
    for sub in ("drama3_tts", "moss_sfx", "acestep_bgm", "logs"):
        (cache_dir / sub).mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Bootstrap isolated venvs + HF weights + anchors, then delegate render stage to `moss_venv` Python
    # so CPU int8 `faster-whisper` bilingual QA runs natively inside `moss-venv`!
    sgl_bin = args.sgl_bin or "sgl-omni"
    moss_py = args.moss_python or sys.executable
    acestep_py = args.acestep_python or sys.executable
    gpu_name, vram_gb, cc = detect_gpu_profile()
    co_resident_96g = (not args.offline_dry_run) and (vram_gb >= 85.0) and (not args.force_int4)
    drama_repo = "fishaudio/drama-3" if (co_resident_96g and not args.force_int4) else "fishaudio/drama-3-int4"

    if not args.offline_dry_run and not args.render_only:
        uv_bin = ensure_uv_and_hf_tools()
        drama_venv, moss_venv, acestep_venv = build_isolated_venvs(uv_bin, refresh_envs=args.refresh_envs)
        sgl_bin = str(drama_venv / "bin/sgl-omni")
        moss_py = str(moss_venv / "bin/python")
        acestep_py = str(acestep_venv / "bin/python")
        stage_hf_models_nvme(drama_repo)
        assemble_silicon_gossip_studio(
            local_studio,
            offline_dry_run=False,
            refresh_anchors=args.refresh_anchors,
        )
        # Re-exec render phase inside `moss_venv` so `faster-whisper` & `numpy` are guaranteed available
        if Path(sys.executable).resolve() != Path(moss_py).resolve():
            sub_cmd = [
                moss_py,
                "-u",
                str(Path(__file__).resolve()),
                "--render-only",
                "--episodes",
                args.episodes,
                "--work-dir",
                str(work_dir),
                "--output-dir",
                str(out_dir),
                "--cache-dir",
                str(cache_dir),
                "--sgl-bin",
                sgl_bin,
                "--moss-python",
                moss_py,
                "--acestep-python",
                acestep_py,
                "--sgl-port",
                str(args.sgl_port),
                "--mp3-bitrate",
                args.mp3_bitrate,
            ]
            for flag_name, flag_cli in (
                ("force_int4", "--force-int4"),
                ("disable_ras", "--disable-ras"),
                ("skip_asr_qa", "--skip-asr-qa"),
                ("skip_existing", "--skip-existing"),
                ("auto_unassign", "--auto-unassign"),
            ):
                if getattr(args, flag_name, False):
                    sub_cmd.append(flag_cli)
            return subprocess.run(sub_cmd, check=False).returncode

    if args.offline_dry_run or not (local_studio / "voice_cast_drama3.json").is_file():
        assemble_silicon_gossip_studio(
            local_studio,
            offline_dry_run=args.offline_dry_run,
            refresh_anchors=args.refresh_anchors,
        )

    registry = VoiceCastingRegistry.load(local_studio / "voice_casting_registry.json")
    voice_cast = json.loads((local_studio / "voice_cast_drama3.json").read_text(encoding="utf-8"))
    characters: dict[str, dict[str, Any]] = voice_cast["characters"]
    domain = registry.domain or "hotline_roundtable"

    targets = resolve_v2_targets(local_studio / "cue_sheets", args.episodes)

    print("=" * 80, flush=True)
    print(
        f"🎙️ 《商战大瓜英语局》Silicon Gossip V2 合成台 | 任务: {[t[0] for t in targets]} | domain={domain}",
        flush=True,
    )
    print(
        f"🖥️  设备: {gpu_name} ({vram_gb:.1f} GB, sm_{cc[0]}{cc[1]}) | "
        f"模式: {'CPU 离线全链路干跑' if args.offline_dry_run else ('96GB 三模型同卡常驻' if co_resident_96g else '显存分阶段接力')}",
        flush=True,
    )
    print(f"🎭 已锁定 {len(characters)} 位真人棚录声纹锚点 | 拟音母题: {len(registry.sonic_motifs)} 枚", flush=True)
    print("=" * 80, flush=True)

    drama_client: Drama3ServerClient | None = None
    moss_worker: SubprocessJsonWorker | None = None
    acestep_worker: SubprocessJsonWorker | None = None
    whisper_qa = SiliconGossipBilingualWhisperQA(enabled=(not args.skip_asr_qa and not args.offline_dry_run))

    if not args.offline_dry_run:
        drama_client = Drama3ServerClient(
            sgl_bin=sgl_bin,
            model_repo=drama_repo,
            port=args.sgl_port,
            co_resident_96g=co_resident_96g,
            enable_ras=not args.disable_ras,
            log_path=cache_dir / "logs" / "sglang_omni_silicon_gossip.log",
        )
        moss_worker = SubprocessJsonWorker("MOSS-SFX v2.0", moss_py, _MOSS_WORKER_CODE, "OpenMOSS-Team/MOSS-SoundEffect-v2.0")
        acestep_worker = SubprocessJsonWorker(
            "ACE-Step 1.5 XL", acestep_py, _ACESTEP_WORKER_CODE, "ACE-Step/acestep-v15-xl-turbo-diffusers"
        )
        if co_resident_96g:
            drama_client.start()

    rendered_summaries: list[dict[str, Any]] = []
    try:
        for label, cs_path in targets:
            cue_sheet = EpisodeCueSheet.load(cs_path)
            if args.skip_existing:
                existing = [
                    p
                    for d in (out_dir, DRIVE_MAIN_MASTERS_DIR)
                    if d.is_dir()
                    for p in sorted(d.glob(f"{cue_sheet.episode_id}_*.mp3"))
                ]
                if existing:
                    print(f"⏭️  [{cue_sheet.episode_id}] 已存在成片 {existing[-1].name}，跳过。", flush=True)
                    continue

            t_ep = time.time()
            dialogue_cues = [c for c in cue_sheet.cues if c.kind == "dialogue"]
            sfx_cues = [c for c in cue_sheet.cues if c.kind == "sfx"]
            print(
                f"\n▶️  开始合成 [{label}] 《{cue_sheet.title}》 "
                f"(对白 {len(dialogue_cues)} 轨 | 拟音 {len(sfx_cues)} 轨 | 配乐 {len(cue_sheet.acts)} 幕)",
                flush=True,
            )

            cue_audio_map: dict[str, Path] = {}
            cue_meta_map: dict[str, dict[str, Any]] = {}
            act_bgm_map: dict[str, Path] = {}

            # 1. Bilingual Dialogue Synthesis (1.0x Drama 3 cached; mixer applies pitch-preserving 0.85x atempo)
            if dialogue_cues and not args.offline_dry_run and not co_resident_96g:
                assert drama_client is not None
                drama_client.start()

            for idx, cue in enumerate(dialogue_cues, 1):
                cinfo = characters[cue.role_id]
                prof = registry.resolve_role(cue.role_id)
                wav_p, meta_d = synthesize_cue_chunked(
                    cue,
                    drama_repo=drama_repo,
                    prof=prof,
                    anchor_wav=local_studio / cinfo["anchor_wav"],
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

            # 2. Foreground Modern Foley SFX (MOSS-SoundEffect-v2.0 + SHA-256 cache)
            for idx, cue in enumerate(sfx_cues, 1):
                raw_prompt = cue.sfx_prompt or (
                    registry.sonic_motifs[cue.motif_id].sfx_prompt if cue.motif_id in registry.sonic_motifs else ""
                )
                prompt = sanitize_moss_foley_prompt(raw_prompt)
                sfx_key = _sha24({"prompt": prompt, "dur": round(cue.duration_seconds, 2)})
                sfx_wav = cache_dir / "moss_sfx" / f"{sfx_key}.wav"
                if args.offline_dry_run:
                    if not sfx_wav.is_file():
                        _write_offline_voiced_wav(sfx_wav, duration_s=cue.duration_seconds, base_freq_hz=120.0, amp=0.14, is_bgm=True)
                elif not sfx_wav.is_file():
                    assert moss_worker is not None
                    raw_moss = cache_dir / "moss_sfx" / f"{sfx_key}_raw.wav"
                    sfx_req = {"prompt": prompt, "seconds": cue.duration_seconds, "out_path": str(raw_moss), "seed": 208 + idx}
                    try:
                        moss_worker.request(sfx_req)
                    except RuntimeError:
                        if acestep_worker is not None:
                            acestep_worker.close()
                        moss_worker.close()
                        moss_worker.request(sfx_req)
                    subprocess.run(
                        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw_moss), "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(sfx_wav)],
                        check=True,
                    )
                    raw_moss.unlink(missing_ok=True)
                cue_audio_map[cue.cue_id] = sfx_wav

            if not args.offline_dry_run and not co_resident_96g and moss_worker is not None:
                moss_worker.close()

            # 3. Per-Act Modern Upbeat BGM (strictly SKIP dry zero-BGM banter acts!)
            for a_idx, act in enumerate(cue_sheet.acts, 1):
                if (
                    not (act.bgm_prompt or "").strip()
                    or (float(act.bgm_gain_speech) <= 1e-4 and float(act.bgm_gain_gap) <= 1e-4)
                ):
                    print(f"   🎙️ [纯干声聊天室] {act.act_id} ({act.title}) 零配乐直出，突出双人吐槽互动感", flush=True)
                    continue
                target_dur = float(max(30.0, min(90.0, float(act.bgm_duration_s or 45.0))))
                bgm_prompt = _sanitize_modern_bgm_prompt(act.bgm_prompt)
                bgm_key = _sha24({"prompt": bgm_prompt, "vocal_language": "unknown", "dur": round(target_dur, 1)})
                bgm_wav = cache_dir / "acestep_bgm" / f"{bgm_key}.wav"
                if args.offline_dry_run:
                    if not bgm_wav.is_file():
                        _write_offline_voiced_wav(bgm_wav, duration_s=12.0, base_freq_hz=150.0, amp=0.09, is_bgm=True)
                elif not bgm_wav.is_file():
                    assert acestep_worker is not None
                    raw_bgm = cache_dir / "acestep_bgm" / f"{bgm_key}_raw.wav"
                    print(f"   🎵 [ACE-Step 1.5 XL] 生成轻快现代商战配乐 {act.act_id} ({target_dur:.0f}s): {act.title}", flush=True)
                    bgm_req = {
                        "prompt": bgm_prompt,
                        "lyrics": "[Instrumental]",
                        "vocal_language": "unknown",
                        "duration_s": target_dur,
                        "out_path": str(raw_bgm),
                        "seed": 5000 + cue_sheet.chapter_number * 10 + a_idx,
                    }
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
                act_bgm_map[act.act_id] = bgm_wav

            if not args.offline_dry_run and not co_resident_96g and acestep_worker is not None:
                acestep_worker.close()

            # 4. 3-Bus -16 LUFS Mastering (stereo chatroom seating pan, guest_laozhou EQ, 0.85x atempo, bilingual SRT)
            stem_prefix = canonical_v2_stem(cue_sheet)
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
            if not args.offline_dry_run:
                sync_v2_outputs_to_drive(out_dir)
    finally:
        if drama_client is not None:
            drama_client.close()
        if moss_worker is not None:
            moss_worker.close()
        if acestep_worker is not None:
            acestep_worker.close()

    if not args.offline_dry_run:
        sync_v2_outputs_to_drive(out_dir)
        os.sync()
        if args.auto_unassign:
            Path("/content/.colab_auto_unassign").write_text("done\n", encoding="utf-8")
            print("🛑 已写入 /content/.colab_auto_unassign 标记，Notebook 将自动销毁 G4 实例立停计费！", flush=True)

    print("=" * 80, flush=True)
    print(f"🎉 《商战大瓜英语局》V2 渲染全部完成！共输出 {len(rendered_summaries)} 期 -> {out_dir}", flush=True)
    print("=" * 80, flush=True)
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="《商战大瓜英语局》Silicon Gossip V2 · Colab 96GB G4 一键渲染引擎")
    parser.add_argument("--episodes", default="V2_E001", help="渲染目标：V2_E001, ALL 等")
    parser.add_argument("--work-dir", default=str(WORK_ROOT), help="本地 NVMe 工作目录")
    parser.add_argument("--output-dir", default="", help="成片输出目录覆盖（默认 <work-dir>/outputs）")
    parser.add_argument("--cache-dir", default="", help="分轨缓存目录覆盖（默认 <work-dir>/cache）")
    parser.add_argument("--sgl-port", type=int, default=8000)
    parser.add_argument("--sgl-bin", default="")
    parser.add_argument("--moss-python", default="")
    parser.add_argument("--acestep-python", default="")
    parser.add_argument("--mp3-bitrate", default="192k")
    parser.add_argument("--force-int4", action="store_true")
    parser.add_argument("--disable-ras", action="store_true")
    parser.add_argument("--skip-asr-qa", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--refresh-envs", action="store_true")
    parser.add_argument("--refresh-anchors", action="store_true")
    parser.add_argument("--auto-unassign", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--offline-dry-run", action="store_true")
    return parser


if __name__ == "__main__":
    raise SystemExit(run_studio(build_arg_parser().parse_args()))
