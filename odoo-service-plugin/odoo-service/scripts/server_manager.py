#!/usr/bin/env python3
"""
server_manager.py — Odoo Server Lifecycle Manager

Start, stop, restart Odoo processes. Works on Windows, Linux, and macOS.
Supports local venv, bare Python, and Docker environments.

Usage:
    python server_manager.py start --config conf/TAQAT17.conf [--dev] [--workers 4]
    python server_manager.py stop [--port 8069]
    python server_manager.py status [--port 8069]
    python server_manager.py restart --config conf/TAQAT17.conf
    python server_manager.py install --config conf/TAQAT17.conf --db mydb --module my_module
    python server_manager.py update --config conf/TAQAT17.conf --db mydb --module my_module
    python server_manager.py refresh --config conf/TAQAT17.conf --db mydb
    python server_manager.py logs [--file logs/odoo.log] [--lines 50]
    python server_manager.py processes
"""

import argparse
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Optional psutil import (graceful degradation)
# ---------------------------------------------------------------------------
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARNING] psutil not installed. Some features limited. Install: pip install psutil")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_HTTP_PORT = 8069
DEFAULT_LONGPOLLING_PORT = 8072
ODOO_PROCESS_NAME = "python"
ODOO_MODULE_MARKER = "odoo"

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"


# ---------------------------------------------------------------------------
# Port Utilities
# ---------------------------------------------------------------------------

def is_port_in_use(port: int, host: str = "localhost") -> bool:
    """Check if a TCP port is currently in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        return result == 0


def get_pid_on_port(port: int) -> Optional[int]:
    """Return PID of the process listening on the given port, or None."""
    if PSUTIL_AVAILABLE:
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == port and conn.status == "LISTEN":
                return conn.pid
        return None

    # Fallback: use platform-specific commands
    if IS_WINDOWS:
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    return int(parts[-1])
        except Exception:
            pass
    else:
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True, text=True
            )
            pids = result.stdout.strip().split()
            if pids:
                return int(pids[0])
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# Process Management
# ---------------------------------------------------------------------------

def kill_process(pid: int, force: bool = True) -> bool:
    """Kill a process by PID. Returns True on success."""
    try:
        if IS_WINDOWS:
            flags = "/F" if force else ""
            cmd = ["taskkill", "/PID", str(pid)]
            if force:
                cmd.append("/F")
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        else:
            import signal
            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(pid, sig)
            return True
    except Exception as e:
        print(f"[ERROR] Failed to kill PID {pid}: {e}")
        return False


def kill_port(port: int) -> bool:
    """Kill whatever process is listening on the given port."""
    pid = get_pid_on_port(port)
    if pid is None:
        print(f"[INFO] No process found on port {port}")
        return True

    print(f"[INFO] Killing PID {pid} on port {port}...")
    success = kill_process(pid)
    if success:
        print(f"[OK] Killed PID {pid} (port {port})")
    return success


def get_running_odoo_processes() -> List[dict]:
    """Return list of running Odoo-related Python processes."""
    processes = []

    if PSUTIL_AVAILABLE:
        for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
            try:
                if proc.info["name"] and "python" in proc.info["name"].lower():
                    cmdline = proc.info.get("cmdline") or []
                    cmdline_str = " ".join(cmdline)
                    if "odoo" in cmdline_str.lower():
                        processes.append({
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "cmdline": cmdline_str[:120],
                            "create_time": proc.info.get("create_time"),
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    else:
        # Fallback
        if IS_WINDOWS:
            try:
                result = subprocess.run(
                    ["wmic", "process", "where", "name='python.exe'",
                     "get", "ProcessId,CommandLine", "/format:csv"],
                    capture_output=True, text=True
                )
                for line in result.stdout.splitlines():
                    if "odoo" in line.lower():
                        parts = line.split(",")
                        if len(parts) >= 2:
                            processes.append({
                                "pid": parts[-1].strip(),
                                "cmdline": line[:120]
                            })
            except Exception:
                pass
        else:
            try:
                result = subprocess.run(
                    ["pgrep", "-a", "-f", "odoo"],
                    capture_output=True, text=True
                )
                for line in result.stdout.splitlines():
                    parts = line.split(None, 1)
                    if len(parts) >= 2:
                        processes.append({
                            "pid": int(parts[0]),
                            "cmdline": parts[1][:120]
                        })
            except Exception:
                pass

    return processes


# ---------------------------------------------------------------------------
# Build Odoo Command
# ---------------------------------------------------------------------------

def build_odoo_command(
    config_path: str,
    dev: bool = False,
    workers: int = 0,
    database: Optional[str] = None,
    install_modules: Optional[str] = None,
    update_modules: Optional[str] = None,
    stop_after_init: bool = False,
    update_list: bool = False,
    python_executable: Optional[str] = None,
) -> List[str]:
    """Build the Odoo startup command list."""
    python = python_executable or sys.executable

    cmd = [python, "-m", "odoo", "-c", str(config_path)]

    if database:
        cmd += ["-d", database]
    if install_modules:
        cmd += ["-i", install_modules]
    if update_modules:
        cmd += ["-u", update_modules]
    if stop_after_init or install_modules or update_modules or update_list:
        cmd.append("--stop-after-init")
    if update_list:
        cmd.append("--update-list")
    if dev:
        cmd.append("--dev=all")
    if workers > 0:
        cmd += [f"--workers={workers}"]

    return cmd


# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------

def start_local(
    config_path: str,
    dev: bool = False,
    workers: int = 0,
    database: Optional[str] = None,
    detach: bool = False,
    python_executable: Optional[str] = None,
) -> Optional[subprocess.Popen]:
    """Start Odoo server locally. Returns Popen object or None if detached."""
    config = Path(config_path)
    if not config.exists():
        print(f"[ERROR] Config file not found: {config}")
        return None

    cmd = build_odoo_command(
        config_path=config_path,
        dev=dev,
        workers=workers,
        database=database,
        python_executable=python_executable,
    )

    print(f"[INFO] Starting Odoo with command: {' '.join(cmd)}")

    if detach:
        if IS_WINDOWS:
            proc = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                close_fds=True,
            )
        else:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        print(f"[OK] Odoo started in background with PID {proc.pid}")
        return proc
    else:
        # Foreground (blocking)
        try:
            proc = subprocess.Popen(cmd)
            print(f"[OK] Odoo started (PID {proc.pid}). Press Ctrl+C to stop.")
            proc.wait()
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted. Stopping Odoo...")
            proc.terminate()
        return None


# ---------------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------------

def stop_local(port: int = DEFAULT_HTTP_PORT, also_longpolling: bool = True) -> bool:
    """Stop Odoo by killing processes on the HTTP (and optionally longpolling) port."""
    stopped_any = False

    http_stopped = kill_port(port)
    if http_stopped:
        stopped_any = True

    if also_longpolling:
        lp_port = port + 3  # Typically 8069 -> 8072
        lp_stopped = kill_port(lp_port)
        if lp_stopped:
            stopped_any = True

    if stopped_any:
        # Wait a moment and verify
        time.sleep(1)
        if not is_port_in_use(port):
            print(f"[OK] Odoo stopped successfully.")
        else:
            print(f"[WARNING] Port {port} still in use after kill attempt.")

    return stopped_any


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def status(port: int = DEFAULT_HTTP_PORT) -> bool:
    """Check if Odoo is running on the given port."""
    running = is_port_in_use(port)
    pid = get_pid_on_port(port)

    if running:
        print(f"[OK] Odoo is RUNNING on port {port} (PID: {pid or 'unknown'})")
        processes = get_running_odoo_processes()
        if processes:
            print(f"[INFO] Found {len(processes)} Odoo-related Python process(es):")
            for p in processes:
                print(f"       PID {p['pid']}: {p.get('cmdline', 'unknown')[:80]}")
    else:
        print(f"[INFO] Odoo is NOT running on port {port}")

    return running


# ---------------------------------------------------------------------------
# Restart
# ---------------------------------------------------------------------------

def restart_local(
    config_path: str,
    dev: bool = False,
    workers: int = 0,
    port: int = DEFAULT_HTTP_PORT,
    python_executable: Optional[str] = None,
) -> None:
    """Stop Odoo then start it again."""
    print("[INFO] Restarting Odoo...")
    stop_local(port=port)
    time.sleep(2)
    start_local(
        config_path=config_path,
        dev=dev,
        workers=workers,
        python_executable=python_executable,
    )


# ---------------------------------------------------------------------------
# Module Operations
# ---------------------------------------------------------------------------

def install_module(
    config: str,
    database: str,
    module: str,
    stop: bool = True,
    python_executable: Optional[str] = None,
) -> int:
    """Install one or more modules. Returns subprocess return code."""
    cmd = build_odoo_command(
        config_path=config,
        database=database,
        install_modules=module,
        stop_after_init=stop,
        python_executable=python_executable,
    )
    print(f"[INFO] Installing module(s): {module}")
    print(f"[CMD] {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"[OK] Module(s) installed successfully: {module}")
    else:
        print(f"[ERROR] Module installation failed (exit code {result.returncode})")
    return result.returncode


def update_module(
    config: str,
    database: str,
    module: str,
    stop: bool = True,
    python_executable: Optional[str] = None,
) -> int:
    """Update one or more modules. Returns subprocess return code."""
    cmd = build_odoo_command(
        config_path=config,
        database=database,
        update_modules=module,
        stop_after_init=stop,
        python_executable=python_executable,
    )
    print(f"[INFO] Updating module(s): {module}")
    print(f"[CMD] {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"[OK] Module(s) updated successfully: {module}")
    else:
        print(f"[ERROR] Module update failed (exit code {result.returncode})")
    return result.returncode


def refresh_modules(
    config: str,
    database: str,
    python_executable: Optional[str] = None,
) -> int:
    """Refresh the module list in the database."""
    cmd = build_odoo_command(
        config_path=config,
        database=database,
        update_list=True,
        python_executable=python_executable,
    )
    print(f"[INFO] Refreshing module list for database: {database}")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print(f"[OK] Module list refreshed.")
    else:
        print(f"[ERROR] Module list refresh failed.")
    return result.returncode


# ---------------------------------------------------------------------------
# Log Tailing
# ---------------------------------------------------------------------------

def tail_log(log_file: str, lines: int = 50) -> None:
    """Print the last N lines of a log file."""
    log_path = Path(log_file)
    if not log_path.exists():
        print(f"[ERROR] Log file not found: {log_file}")
        return

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            for line in last_lines:
                print(line, end="")
    except Exception as e:
        print(f"[ERROR] Could not read log file: {e}")


def follow_log(log_file: str) -> None:
    """Follow a log file (like tail -f). Press Ctrl+C to stop."""
    log_path = Path(log_file)
    if not log_path.exists():
        print(f"[ERROR] Log file not found: {log_file}")
        return

    print(f"[INFO] Following log file: {log_file} (Ctrl+C to stop)")
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)  # Seek to end
            while True:
                line = f.readline()
                if line:
                    print(line, end="", flush=True)
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped following log.")


# ---------------------------------------------------------------------------
# Environment Detection
# ---------------------------------------------------------------------------

def detect_environment(project_root: str = ".") -> str:
    """Detect the current Odoo environment type."""
    root = Path(project_root).resolve()

    if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
        return "docker"
    if (root / "Dockerfile").exists():
        return "docker"

    for venv_dir in [".venv", "venv", "env"]:
        venv_path = root / venv_dir
        if venv_path.is_dir():
            if (venv_path / "Scripts" / "python.exe").exists():
                return "venv"
            if (venv_path / "bin" / "python").exists():
                return "venv"

    return "bare"


def find_python_in_venv(project_root: str = ".") -> Optional[str]:
    """Find the Python executable inside the virtual environment."""
    root = Path(project_root).resolve()

    for venv_dir in [".venv", "venv", "env"]:
        venv_path = root / venv_dir
        win_python = venv_path / "Scripts" / "python.exe"
        linux_python = venv_path / "bin" / "python"

        if win_python.exists():
            return str(win_python)
        if linux_python.exists():
            return str(linux_python)

    return None


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Odoo Server Manager — start, stop, status, and manage Odoo servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server_manager.py start --config conf/TAQAT17.conf --dev
  python server_manager.py stop --port 8069
  python server_manager.py status
  python server_manager.py restart --config conf/TAQAT17.conf
  python server_manager.py install --config conf/TAQAT17.conf --db mydb --module my_module
  python server_manager.py update --config conf/TAQAT17.conf --db mydb --module my_module
  python server_manager.py logs --file logs/odoo.log --lines 50
  python server_manager.py processes
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # start
    start_p = subparsers.add_parser("start", help="Start Odoo server")
    start_p.add_argument("--config", "-c", required=True, help="Path to .conf file")
    start_p.add_argument("--dev", action="store_true", help="Enable development mode (--dev=all)")
    start_p.add_argument("--workers", "-w", type=int, default=0, help="Number of workers (0=dev)")
    start_p.add_argument("--db", "-d", help="Database name override")
    start_p.add_argument("--detach", action="store_true", help="Start in background")
    start_p.add_argument("--python", help="Python executable path")

    # stop
    stop_p = subparsers.add_parser("stop", help="Stop Odoo server")
    stop_p.add_argument("--port", "-p", type=int, default=DEFAULT_HTTP_PORT)
    stop_p.add_argument("--all", dest="kill_all", action="store_true",
                         help="Kill all Odoo Python processes")

    # status
    status_p = subparsers.add_parser("status", help="Check if Odoo is running")
    status_p.add_argument("--port", "-p", type=int, default=DEFAULT_HTTP_PORT)

    # restart
    restart_p = subparsers.add_parser("restart", help="Restart Odoo server")
    restart_p.add_argument("--config", "-c", required=True)
    restart_p.add_argument("--dev", action="store_true")
    restart_p.add_argument("--workers", "-w", type=int, default=0)
    restart_p.add_argument("--port", "-p", type=int, default=DEFAULT_HTTP_PORT)
    restart_p.add_argument("--python", help="Python executable path")

    # install
    install_p = subparsers.add_parser("install", help="Install Odoo module(s)")
    install_p.add_argument("--config", "-c", required=True)
    install_p.add_argument("--db", "-d", required=True)
    install_p.add_argument("--module", "-m", required=True, help="Module name(s), comma-separated")
    install_p.add_argument("--python", help="Python executable path")

    # update
    update_p = subparsers.add_parser("update", help="Update Odoo module(s)")
    update_p.add_argument("--config", "-c", required=True)
    update_p.add_argument("--db", "-d", required=True)
    update_p.add_argument("--module", "-m", required=True, help="Module name(s), comma-separated")
    update_p.add_argument("--python", help="Python executable path")

    # refresh
    refresh_p = subparsers.add_parser("refresh", help="Refresh module list in database")
    refresh_p.add_argument("--config", "-c", required=True)
    refresh_p.add_argument("--db", "-d", required=True)
    refresh_p.add_argument("--python", help="Python executable path")

    # logs
    logs_p = subparsers.add_parser("logs", help="Show/follow Odoo log file")
    logs_p.add_argument("--file", "-f", default="logs/odoo.log")
    logs_p.add_argument("--lines", "-n", type=int, default=50)
    logs_p.add_argument("--follow", action="store_true", help="Follow log (like tail -f)")

    # processes
    subparsers.add_parser("processes", help="List running Odoo processes")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "start":
        start_local(
            config_path=args.config,
            dev=args.dev,
            workers=args.workers,
            database=getattr(args, "db", None),
            detach=args.detach,
            python_executable=getattr(args, "python", None),
        )

    elif args.command == "stop":
        if getattr(args, "kill_all", False):
            print("[INFO] Killing all Odoo Python processes...")
            procs = get_running_odoo_processes()
            for p in procs:
                kill_process(p["pid"])
                print(f"[OK] Killed PID {p['pid']}")
        else:
            stop_local(port=args.port)

    elif args.command == "status":
        running = status(port=args.port)
        sys.exit(0 if running else 1)

    elif args.command == "restart":
        restart_local(
            config_path=args.config,
            dev=args.dev,
            workers=args.workers,
            port=args.port,
            python_executable=getattr(args, "python", None),
        )

    elif args.command == "install":
        rc = install_module(
            config=args.config,
            database=args.db,
            module=args.module,
            python_executable=getattr(args, "python", None),
        )
        sys.exit(rc)

    elif args.command == "update":
        rc = update_module(
            config=args.config,
            database=args.db,
            module=args.module,
            python_executable=getattr(args, "python", None),
        )
        sys.exit(rc)

    elif args.command == "refresh":
        rc = refresh_modules(
            config=args.config,
            database=args.db,
            python_executable=getattr(args, "python", None),
        )
        sys.exit(rc)

    elif args.command == "logs":
        if args.follow:
            follow_log(args.file)
        else:
            tail_log(args.file, lines=args.lines)

    elif args.command == "processes":
        procs = get_running_odoo_processes()
        if procs:
            print(f"Found {len(procs)} Odoo-related process(es):")
            for p in procs:
                print(f"  PID {p['pid']}: {p.get('cmdline', 'unknown')[:100]}")
        else:
            print("No Odoo processes found.")


if __name__ == "__main__":
    main()
