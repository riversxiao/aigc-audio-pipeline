#!/usr/bin/env python3
"""
《诸界锁仙》 Colab G4 <-> 云端 Antigravity Agent 纯 HTTPS 远程接管桥接服务 (`colab_agent_bridge.py`)

解决问题：
  云端远程沙箱 VM（`jetski_remote_agents_3p`）的安全出口代理允许纯 HTTPS (`GET`/`POST`)，
  但禁止 WebSocket 升级（`HTTP 403: WebSocket upgrades are not allowed`），导致无法通过 `colab exec` 发送首条指令。

工作机制：
  1. 用户在 Colab Notebook 点一次 Cell 1，本脚本启动本地 `ThreadingHTTPServer` (127.0.0.1:8765) + `cloudflared` HTTPS 隧道。
  2. 自动生成 256-bit 随机 `Bearer` 密钥，将 `{url, token, gpu, created_at}` 写入 Google Drive
     `05_Colab_96GB_FishDrama3_满血本地推理管线/colab_agent_bridge.json`。
  3. 云端 Antigravity Agent 通过 `gdrive` 读取该 JSON 后，即可走 100% 纯 HTTPS 异步操控 G4：
     - `GET  /health`           : 查看 GPU 显存、磁盘与任务队列状态
     - `POST /exec_sync`        : 执行短命令 (<30s)
     - `POST /jobs/start`       : 异步启动长耗时渲染任务（彻底规避 Cloudflare 100s 超时限制）
     - `GET  /jobs/status`      : 增量拉取实时日志与 `.done` 成品列表
     - `POST /jobs/kill`        : 终止指定后台任务
     - `POST /upload_file`      : 热更新脚本或配置至 Colab NVMe
     - `GET  /download_file`    : 直接通过 HTTPS 高速拉取成品音频回云端 VM 质检与归档
     - `POST /shutdown`         : 任务完成后主动调用 `runtime.unassign()` 销毁 G4 实例立停 CCU 计费
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import threading
import time
from typing import Any, Optional
import urllib.parse


NVME_ROOT = Path("/content") if Path("/content").exists() else Path("/tmp")
JOBS_DIR = NVME_ROOT / "agent_bridge_jobs"
DEFAULT_DRIVE_BRIDGE_REL = (
    "《诸界锁仙》长篇修仙小说工程/04_有声剧与广播剧音频/"
    "05_Colab_96GB_FishDrama3_满血本地推理管线/colab_agent_bridge.json"
)


class JobRegistry:
    def __init__(self, jobs_dir: Path) -> None:
        self.jobs_dir = jobs_dir
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._procs: dict[str, subprocess.Popen] = {}
        self._meta: dict[str, dict[str, Any]] = {}

    def start_job(
        self,
        job_id: str,
        cmd: list[str] | str,
        cwd: str = "/content",
        env_overrides: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", job_id) or f"job_{int(time.time())}"
        with self._lock:
            existing = self._procs.get(safe_id)
            if existing is not None and existing.poll() is None:
                return {
                    "ok": True,
                    "already_running": True,
                    "job_id": safe_id,
                    "pid": existing.pid,
                    "log_path": str(self._meta[safe_id]["log_path"]),
                }

            log_path = self.jobs_dir / f"{safe_id}.log"
            log_fh = open(log_path, "w", encoding="utf-8", buffering=1)
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            if env_overrides:
                for k, v in env_overrides.items():
                    env[str(k)] = str(v)

            use_shell = isinstance(cmd, str)
            proc = subprocess.Popen(
                cmd,
                shell=use_shell,
                cwd=cwd if os.path.isdir(cwd) else str(NVME_ROOT),
                env=env,
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            self._procs[safe_id] = proc
            self._meta[safe_id] = {
                "job_id": safe_id,
                "cmd": cmd,
                "cwd": cwd,
                "pid": proc.pid,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "log_path": str(log_path),
                "log_fh": log_fh,
            }
            return {
                "ok": True,
                "already_running": False,
                "job_id": safe_id,
                "pid": proc.pid,
                "log_path": str(log_path),
            }

    def status(self, job_id: str, offset: int = 0, limit: int = 32768) -> dict[str, Any]:
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", job_id)
        with self._lock:
            proc = self._procs.get(safe_id)
            meta = self._meta.get(safe_id)
        if proc is None or meta is None:
            return {"ok": False, "error": f"Unknown job_id: {safe_id}"}

        rc = proc.poll()
        running = rc is None
        log_path = Path(meta["log_path"])
        chunk = ""
        next_offset = offset
        total_bytes = 0
        if log_path.exists():
            total_bytes = log_path.stat().st_size
            with open(log_path, "rb") as f:
                if offset > 0:
                    f.seek(min(offset, total_bytes))
                raw = f.read(max(1024, min(limit, 512 * 1024)))
                next_offset = f.tell()
            chunk = raw.decode("utf-8", errors="replace")

        out_dir = NVME_ROOT / "zhujie_suoxian_work" / "zhujie_studio" / "outputs"
        done_files = sorted(p.name for p in out_dir.glob("*")) if out_dir.exists() else []
        return {
            "ok": True,
            "job_id": safe_id,
            "pid": meta["pid"],
            "running": running,
            "returncode": rc,
            "started_at": meta["started_at"],
            "offset": offset,
            "next_offset": next_offset,
            "total_log_bytes": total_bytes,
            "log_chunk": chunk,
            "output_files": done_files,
        }

    def kill_job(self, job_id: str) -> dict[str, Any]:
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", job_id)
        with self._lock:
            proc = self._procs.get(safe_id)
        if proc is None:
            return {"ok": False, "error": f"Unknown job_id: {safe_id}"}
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                proc.terminate()
        return {"ok": True, "job_id": safe_id, "returncode": proc.poll()}

    def summary(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        with self._lock:
            keys = sorted(self._procs.keys())
        for k in keys:
            proc = self._procs[k]
            meta = self._meta[k]
            rc = proc.poll()
            items.append(
                {
                    "job_id": k,
                    "pid": meta["pid"],
                    "running": rc is None,
                    "returncode": rc,
                    "started_at": meta["started_at"],
                }
            )
        return items


def query_gpu_summary() -> str:
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    except Exception:
        pass
    return "CPU / No NVIDIA GPU detected"


def build_handler_class(secret_token: str, registry: JobRegistry) -> type[BaseHTTPRequestHandler]:
    class AgentBridgeHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt: str, *args: Any) -> None:
            # Suppress noisy query strings or auth headers
            print(f"[AgentBridge] {self.command} {self.path.split('?')[0]} -> {fmt % args}", flush=True)

        def _check_auth(self) -> bool:
            auth = self.headers.get("Authorization", "")
            expected = f"Bearer {secret_token}"
            if not hmac.compare_digest(auth.encode("utf-8"), expected.encode("utf-8")):
                self._send_json(401, {"ok": False, "error": "Unauthorized"})
                return False
            return True

        def _send_json(self, code: int, payload: dict[str, Any]) -> None:
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))

        def do_GET(self) -> None:
            if not self._check_auth():
                return
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)

            if parsed.path == "/health":
                total, used, free = shutil.disk_usage(str(NVME_ROOT))
                self._send_json(
                    200,
                    {
                        "ok": True,
                        "gpu": query_gpu_summary(),
                        "disk_free_gb": round(free / (1024**3), 2),
                        "drive_mounted": Path("/content/drive/MyDrive").exists(),
                        "jobs": registry.summary(),
                    },
                )
                return

            if parsed.path == "/jobs/status":
                job_id = (qs.get("job_id") or [""])[0]
                offset = int((qs.get("offset") or ["0"])[0])
                limit = int((qs.get("limit") or ["32768"])[0])
                res = registry.status(job_id, offset=offset, limit=limit)
                self._send_json(200 if res.get("ok") else 404, res)
                return

            if parsed.path == "/download_file":
                target = Path((qs.get("path") or [""])[0])
                if not target.is_file():
                    self._send_json(404, {"ok": False, "error": f"File not found: {target}"})
                    return
                size = target.stat().st_size
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(size))
                self.send_header("X-File-Name", target.name)
                self.end_headers()
                with open(target, "rb") as fin:
                    shutil.copyfileobj(fin, self.wfile, length=1024 * 1024)
                return

            self._send_json(404, {"ok": False, "error": f"Unknown GET path: {parsed.path}"})

        def do_POST(self) -> None:
            if not self._check_auth():
                return
            parsed = urllib.parse.urlparse(self.path)
            body = self._read_json()

            if parsed.path == "/exec_sync":
                cmd = body.get("cmd", "")
                timeout = min(float(body.get("timeout", 30.0)), 60.0)
                cwd = str(body.get("cwd") or NVME_ROOT)
                try:
                    p = subprocess.run(
                        cmd,
                        shell=isinstance(cmd, str),
                        cwd=cwd if os.path.isdir(cwd) else str(NVME_ROOT),
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                    )
                    self._send_json(
                        200,
                        {
                            "ok": True,
                            "returncode": p.returncode,
                            "stdout": p.stdout[-32000:],
                            "stderr": p.stderr[-32000:],
                        },
                    )
                except Exception as exc:
                    self._send_json(500, {"ok": False, "error": str(exc)})
                return

            if parsed.path == "/jobs/start":
                job_id = str(body.get("job_id") or "zhujie_drama3")
                cmd = body.get("cmd")
                if not cmd:
                    self._send_json(400, {"ok": False, "error": "Missing 'cmd'"})
                    return
                cwd = str(body.get("cwd") or NVME_ROOT)
                env_overrides = body.get("env") if isinstance(body.get("env"), dict) else None
                res = registry.start_job(job_id=job_id, cmd=cmd, cwd=cwd, env_overrides=env_overrides)
                self._send_json(200, res)
                return

            if parsed.path == "/jobs/kill":
                job_id = str(body.get("job_id") or "")
                res = registry.kill_job(job_id)
                self._send_json(200 if res.get("ok") else 404, res)
                return

            if parsed.path == "/upload_file":
                dest = Path(str(body.get("path") or ""))
                b64 = str(body.get("content_b64") or "")
                if not dest or not b64:
                    self._send_json(400, {"ok": False, "error": "Missing 'path' or 'content_b64'"})
                    return
                dest.parent.mkdir(parents=True, exist_ok=True)
                raw = base64.b64decode(b64)
                dest.write_bytes(raw)
                if body.get("executable"):
                    dest.chmod(0o755)
                self._send_json(200, {"ok": True, "path": str(dest), "bytes": len(raw)})
                return

            if parsed.path == "/shutdown":
                self._send_json(200, {"ok": True, "message": "Shutting down Colab runtime in 2s..."})

                def _delayed_unassign() -> None:
                    time.sleep(1.5)
                    (NVME_ROOT / ".colab_auto_unassign").write_text("shutdown_requested\n", encoding="utf-8")
                    for bp in (
                        NVME_ROOT / "colab_agent_bridge.json",
                        Path("/content/drive/MyDrive") / DEFAULT_DRIVE_BRIDGE_REL,
                    ):
                        try:
                            bp.unlink(missing_ok=True)
                        except Exception:
                            pass
                    os.sync()
                    try:
                        from google.colab import runtime  # type: ignore

                        runtime.unassign()
                    except Exception as exc:
                        print(f"[AgentBridge] Delegating runtime.unassign() to parent Notebook cell ({exc})", flush=True)
                    try:
                        self.server.shutdown()
                    except Exception:
                        pass

                threading.Thread(target=_delayed_unassign, daemon=True).start()
                return

            self._send_json(404, {"ok": False, "error": f"Unknown POST path: {parsed.path}"})

    return AgentBridgeHandler


def start_cloudflared(port: int) -> tuple[subprocess.Popen, str]:
    cf_bin = NVME_ROOT / "cloudflared"
    if not cf_bin.exists():
        subprocess.run(
            f"curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 "
            f"-o '{cf_bin}' && chmod +x '{cf_bin}'",
            shell=True,
            check=True,
        )
    log_path = NVME_ROOT / "cloudflared_agent_bridge.log"
    log_fh = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(cf_bin), "tunnel", "--url", f"http://127.0.0.1:{port}", "--no-autoupdate"],
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )
    for _ in range(50):
        if log_path.exists():
            txt = log_path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", txt)
            if m:
                return proc, m.group(0)
        time.sleep(0.5)
    raise RuntimeError("未能获取 trycloudflare.com 隧道地址，请检查网络后重试。")


def write_bridge_handshake(payload: dict[str, Any], bridge_path: Path) -> None:
    bridge_path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with open(bridge_path, "wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.sync()


def serve_colab_bridge(port: int = 8765, bridge_file: Optional[str] = None, no_tunnel: bool = False) -> None:
    if os.path.isdir("/content/drive/My Drive") and not os.path.exists("/content/drive/MyDrive"):
        os.symlink("/content/drive/My Drive", "/content/drive/MyDrive")

    auto_sentinel = NVME_ROOT / ".colab_auto_unassign"
    auto_sentinel.unlink(missing_ok=True)

    secret_token = secrets.token_urlsafe(32)
    registry = JobRegistry(JOBS_DIR)
    handler_cls = build_handler_class(secret_token, registry)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler_cls)

    tunnel_proc: Optional[subprocess.Popen] = None
    public_url = f"http://127.0.0.1:{port}"
    if not no_tunnel:
        tunnel_proc, public_url = start_cloudflared(port=port)

    gpu_info = query_gpu_summary()
    handshake = {
        "url": public_url,
        "token": secret_token,
        "gpu": gpu_info,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    target_paths: list[Path] = [NVME_ROOT / "colab_agent_bridge.json"]
    if bridge_file:
        target_paths.append(Path(bridge_file))
    elif Path("/content/drive/MyDrive").exists():
        target_paths.append(Path("/content/drive/MyDrive") / DEFAULT_DRIVE_BRIDGE_REL)

    for p in target_paths:
        try:
            write_bridge_handshake(handshake, p)
            print(f"✅ 桥接凭证已同步落盘: {p}", flush=True)
        except Exception as exc:
            print(f"⚠️ 写入 {p} 失败: {exc}", flush=True)

    def _watch_auto_unassign() -> None:
        while True:
            if auto_sentinel.exists():
                print("🛑 [AgentBridge] 检测到自动关机哨兵文件，正在退出桥接服务并交由 Notebook 销毁实例...", flush=True)
                for p in target_paths:
                    try:
                        p.unlink(missing_ok=True)
                    except Exception:
                        pass
                os.sync()
                time.sleep(1.5)
                try:
                    server.shutdown()
                except Exception:
                    pass
                return
            time.sleep(2.0)

    threading.Thread(target=_watch_auto_unassign, daemon=True).start()

    print("=" * 76, flush=True)
    print("🚀 《诸界锁仙》 Colab G4 纯 HTTPS 云端接管桥接服务已就绪！", flush=True)
    print(f"🖥️  当前 GPU : {gpu_info}", flush=True)
    print(f"🌐 隧道地址 : {public_url}", flush=True)
    print("👉 现在请保持本单元格运行，直接回到聊天窗口对 Agent 说：「开了」即可！", flush=True)
    print("   （Agent 跑完并把成片归档回 Google Drive 后，即使网页无人值守也会自动关停实例止费）", flush=True)
    print("=" * 76, flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if tunnel_proc and tunnel_proc.poll() is None:
            tunnel_proc.terminate()


def main() -> None:
    parser = argparse.ArgumentParser(description="Colab G4 <-> Cloud Agent Pure-HTTPS Bridge")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bridge-file", default="", help="Optional explicit path for colab_agent_bridge.json")
    parser.add_argument("--no-tunnel", action="store_true", help="Bind local HTTP only (for unit testing)")
    args = parser.parse_args()
    serve_colab_bridge(
        port=args.port,
        bridge_file=args.bridge_file or None,
        no_tunnel=args.no_tunnel,
    )


if __name__ == "__main__":
    main()
