#!/usr/bin/env python3
"""Export and serve the local read-only Agent Hub viewer."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def skill_paths() -> tuple[Path, Path, Path]:
    skill_dir = Path(__file__).resolve().parents[1]
    skills_dir = skill_dir.parent
    viewer_dir = skills_dir / "list-agent-hub-issues" / "viewer"
    agent_hub_script = skills_dir / "manage-agent-hub-issues" / "scripts" / "agent_hub.py"
    return skill_dir, viewer_dir, agent_hub_script


def port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


def serves_hub_snapshot(host: str, port: int) -> bool:
    url = f"http://{host}:{port}/api/state"
    try:
        with urllib.request.urlopen(url, timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return False
    return (
        payload.get("version") == "3"
        and isinstance(payload.get("columns"), list)
        and isinstance(payload.get("summary"), dict)
        and isinstance(payload.get("revision"), dict)
    )


def choose_port(host: str, requested_port: int) -> tuple[int, bool]:
    if not port_is_open(host, requested_port):
        return requested_port, False
    if serves_hub_snapshot(host, requested_port):
        return requested_port, True
    for port in range(requested_port + 1, requested_port + 51):
        if not port_is_open(host, port):
            return port, False
    raise RuntimeError(f"No free local port found near {requested_port}.")


def runtime_dir(repo: Path) -> Path:
    hub_runtime = repo / ".hub" / "runtime" / "agent-hub-app"
    hub_runtime.mkdir(parents=True, exist_ok=True)
    return hub_runtime


def export_snapshot(
    repo: Path,
    change: str,
    output: Path,
    agent_hub_script: Path,
) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    if agent_hub_script.exists():
        command = [
            sys.executable,
            str(agent_hub_script),
            "--repo",
            str(repo),
            "dashboard",
            "export",
            "--output",
            str(output),
        ]
    else:
        command = [
            "agent-hub",
            "--repo",
            str(repo),
            "dashboard",
            "export",
            "--output",
            str(output),
        ]
    if change:
        command.extend(["--change", change])

    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "dashboard export failed").strip())
    return json.loads(result.stdout or "{}")


def build_serve_command(
    host: str,
    port: int,
    repo: Path,
    change: str,
    agent_hub_script: Path,
) -> list[str]:
    if agent_hub_script.exists():
        command = [
            sys.executable,
            str(agent_hub_script),
            "--repo",
            str(repo),
            "dashboard",
            "serve",
        ]
    else:
        command = [
            "agent-hub",
            "--repo",
            str(repo),
            "dashboard",
            "serve",
        ]
    if change:
        command.extend(["--change", change])
    command.extend(["--host", host, "--port", str(port)])
    return command


def start_background_server(
    host: str,
    port: int,
    viewer_dir: Path,
    run_dir: Path,
    repo: Path,
    change: str,
    agent_hub_script: Path,
) -> subprocess.Popen[str]:
    del viewer_dir
    log_path = run_dir / "server.log"
    log_file = log_path.open("ab")
    command = build_serve_command(host, port, repo, change, agent_hub_script)
    process = subprocess.Popen(
        command,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    (run_dir / "server.pid").write_text(f"{process.pid}\n", encoding="utf-8")
    return process


def wait_for_server(host: str, port: int, process: subprocess.Popen[str] | None) -> None:
    for _ in range(30):
        if port_is_open(host, port):
            return
        if process is not None and process.poll() is not None:
            raise RuntimeError(f"server exited early with status {process.returncode}")
        time.sleep(0.1)
    raise RuntimeError(f"server did not start on {host}:{port}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Target repo containing .hub/.")
    parser.add_argument("--change", default="", help="Optional change slug to filter the dashboard.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for the local viewer.")
    parser.add_argument("--port", type=int, default=8765, help="Port for the local viewer.")
    parser.add_argument("--foreground", action="store_true", help="Run the HTTP server in the foreground.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo = args.repo.expanduser().resolve()
    _, viewer_dir, agent_hub_script = skill_paths()
    if not viewer_dir.exists():
        print(f"Viewer directory not found: {viewer_dir}", file=sys.stderr)
        return 1
    if not (repo / ".hub").exists():
        print(f"Repo does not contain .hub/: {repo}", file=sys.stderr)
        return 1

    run_dir = runtime_dir(repo)
    snapshot_path = viewer_dir / "hub-state.json"
    try:
        export_payload = export_snapshot(repo, args.change, snapshot_path, agent_hub_script)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        port, reused = choose_port(args.host, args.port)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    url = f"http://{args.host}:{port}"
    if args.foreground:
        if reused:
            print(json.dumps({"ok": True, "url": url, "snapshot": str(snapshot_path), "server": "reused"}))
            return 0
        print(json.dumps({"ok": True, "url": url, "snapshot": str(snapshot_path), "foreground": True}))
        command = build_serve_command(args.host, port, repo, args.change, agent_hub_script)
        os.execvp(command[0], command)

    process = None
    if not reused:
        process = start_background_server(args.host, port, viewer_dir, run_dir, repo, args.change, agent_hub_script)
        wait_for_server(args.host, port, process)

    response = {
        "ok": True,
        "url": url,
        "repo": str(repo),
        "change": args.change,
        "snapshot": str(snapshot_path),
        "server": "reused" if reused else "started",
        "pid": None if reused else process.pid if process else None,
        "port": port,
        "requested_port": args.port,
        "export": export_payload,
    }
    print(json.dumps(response, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
