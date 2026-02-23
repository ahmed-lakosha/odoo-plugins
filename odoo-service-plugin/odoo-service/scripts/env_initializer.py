#!/usr/bin/env python3
"""
env_initializer.py — Odoo Environment Initializer

Set up virtual environments, install dependencies, configure PostgreSQL,
generate config files, and scaffold new Odoo projects.

Usage:
    python env_initializer.py init --version 17 --project myproject --port 8069
    python env_initializer.py venv --python python3.11
    python env_initializer.py check
    python env_initializer.py conf --project myproject --version 17 --db mydb --port 8069
    python env_initializer.py scaffold --name my_module --path projects/myproject/
"""

import argparse
import configparser
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

PYTHON_VERSION_REQUIREMENTS: Dict[int, Tuple[Tuple[int, int], Tuple[int, int]]] = {
    14: ((3, 7), (3, 10)),
    15: ((3, 8), (3, 11)),
    16: ((3, 9), (3, 12)),
    17: ((3, 10), (3, 13)),
    18: ((3, 10), (3, 13)),
    19: ((3, 10), (3, 13)),
}

DEFAULT_CONF_TEMPLATE = """\
[options]
addons_path = odoo\\addons,projects\\{project}
admin_passwd = 123
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = {project}{version}.*
http_port = {http_port}
gevent_port = {gevent_port}
workers = 0
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_time_cpu = 600
limit_time_real = 1200
proxy_mode = False
log_level = info
data_dir = data
"""

GITIGNORE_TEMPLATE = """\
# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/
*.egg

# Virtual environments
.venv/
venv/
env/
.env/

# Odoo
*.pyc
data/
logs/
backups/
*.log

# IDE
.idea/
.vscode/
*.iml

# OS
.DS_Store
Thumbs.db
desktop.ini

# Database
*.dump
*.sql

# Environment
.env
.env.local
.env.production
"""


# ---------------------------------------------------------------------------
# Environment Detection
# ---------------------------------------------------------------------------

def detect_environment(path: str = ".") -> str:
    """
    Detect the current Odoo environment type.
    Returns: 'venv', 'docker', or 'bare'
    """
    root = Path(path).resolve()

    # Docker detection (highest priority)
    if (root / "docker-compose.yml").exists():
        return "docker"
    if (root / "docker-compose.yaml").exists():
        return "docker"
    if (root / "Dockerfile").exists():
        return "docker"

    # Venv detection
    for venv_dir in [".venv", "venv", "env"]:
        venv_path = root / venv_dir
        if venv_path.is_dir():
            if (venv_path / "Scripts" / "python.exe").exists():
                return "venv"
            if (venv_path / "bin" / "python").exists():
                return "venv"

    return "bare"


def detect_python_version(odoo_version: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Return (min_version, max_version) tuple for the given Odoo version."""
    return PYTHON_VERSION_REQUIREMENTS.get(odoo_version, ((3, 10), (3, 13)))


def check_python_compatibility(odoo_version: int) -> bool:
    """Check if current Python is compatible with the given Odoo version."""
    current = sys.version_info[:2]
    min_ver, max_ver = detect_python_version(odoo_version)
    return min_ver <= current <= max_ver


# ---------------------------------------------------------------------------
# Virtual Environment
# ---------------------------------------------------------------------------

def find_python_executable(preferred: Optional[str] = None) -> str:
    """Find the best Python executable to use."""
    if preferred:
        if shutil.which(preferred):
            return preferred
        raise RuntimeError(f"Python executable not found: {preferred}")

    # Try common Python executables
    candidates = ["python3.11", "python3.10", "python3.12", "python3", "python"]
    for candidate in candidates:
        if shutil.which(candidate):
            return candidate

    raise RuntimeError("No Python executable found. Install Python 3.10+")


def create_venv(
    path: str,
    python_executable: Optional[str] = None,
    upgrade: bool = True
) -> Path:
    """
    Create a virtual environment at the given path.
    Returns Path to the venv directory.
    """
    venv_path = Path(path)
    python = find_python_executable(python_executable)

    print(f"[INFO] Creating virtual environment at: {venv_path}")
    print(f"[INFO] Using Python: {python}")

    # Create venv
    result = subprocess.run(
        [python, "-m", "venv", str(venv_path)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to create venv: {result.stderr}")

    print(f"[OK] Virtual environment created at: {venv_path}")

    # Upgrade pip
    if upgrade:
        pip = get_venv_pip(str(venv_path))
        print("[INFO] Upgrading pip...")
        subprocess.run([pip, "install", "--upgrade", "pip"], check=True,
                       capture_output=True)
        print("[OK] pip upgraded.")

    return venv_path


def get_venv_python(venv_path: str) -> str:
    """Get the Python executable path inside a venv."""
    venv = Path(venv_path)
    win_py = venv / "Scripts" / "python.exe"
    linux_py = venv / "bin" / "python"

    if win_py.exists():
        return str(win_py)
    if linux_py.exists():
        return str(linux_py)

    raise RuntimeError(f"Python not found in venv: {venv_path}")


def get_venv_pip(venv_path: str) -> str:
    """Get the pip executable path inside a venv."""
    venv = Path(venv_path)
    win_pip = venv / "Scripts" / "pip.exe"
    linux_pip = venv / "bin" / "pip"

    if win_pip.exists():
        return str(win_pip)
    if linux_pip.exists():
        return str(linux_pip)

    # Fallback: use python -m pip
    return get_venv_python(venv_path)


def install_requirements(
    venv_path: str,
    requirements_file: str,
    use_python_m_pip: bool = False
) -> int:
    """Install requirements from a file into a venv."""
    req_path = Path(requirements_file)
    if not req_path.exists():
        print(f"[WARNING] Requirements file not found: {requirements_file}")
        return 0

    pip = get_venv_pip(venv_path)
    python = get_venv_python(venv_path)

    print(f"[INFO] Installing requirements from: {requirements_file}")

    if use_python_m_pip:
        cmd = [python, "-m", "pip", "install", "-r", str(req_path)]
    else:
        if pip == python:
            cmd = [python, "-m", "pip", "install", "-r", str(req_path)]
        else:
            cmd = [pip, "install", "-r", str(req_path)]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"[OK] Requirements installed from: {requirements_file}")
    else:
        print(f"[ERROR] Failed to install requirements (exit code {result.returncode})")

    return result.returncode


# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

def check_postgresql(
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo"
) -> bool:
    """Test PostgreSQL connection. Returns True if successful."""
    # First check port is open
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        result = s.connect_ex((host, port))
        if result != 0:
            print(f"[ERROR] Cannot connect to PostgreSQL at {host}:{port}")
            return False

    # Try psql command
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    try:
        result = subprocess.run(
            ["psql", "-U", user, "-h", host, "-p", str(port), "-c", "SELECT 1;"],
            env=env, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"[OK] PostgreSQL connection successful ({host}:{port})")
            return True
        else:
            print(f"[WARNING] psql returned error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("[WARNING] psql not found in PATH. Cannot verify PostgreSQL.")
        return False
    except subprocess.TimeoutExpired:
        print(f"[ERROR] PostgreSQL connection timed out.")
        return False


def create_postgresql_user(
    username: str = "odoo",
    password: str = "odoo",
    superuser: bool = True
) -> bool:
    """Create a PostgreSQL user for Odoo."""
    try:
        flags = ["-s"] if superuser else []
        result = subprocess.run(
            ["createuser", "-P"] + flags + [username],
            input=f"{password}\n{password}\n",
            text=True, capture_output=True
        )
        if result.returncode == 0:
            print(f"[OK] PostgreSQL user '{username}' created.")
            return True
        else:
            if "already exists" in result.stderr:
                print(f"[INFO] PostgreSQL user '{username}' already exists.")
                return True
            print(f"[ERROR] Failed to create user: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("[ERROR] createuser not found. Is PostgreSQL installed?")
        return False


# ---------------------------------------------------------------------------
# Config File Generation
# ---------------------------------------------------------------------------

def create_conf_file(
    project: str,
    version: int,
    database: Optional[str] = None,
    port: int = 8069,
    workers: int = 0,
    output_dir: str = "conf",
    addons_path: Optional[str] = None,
) -> Path:
    """Generate an Odoo .conf file."""
    conf_dir = Path(output_dir)
    conf_dir.mkdir(parents=True, exist_ok=True)

    conf_file = conf_dir / f"{project}{version}.conf"

    # Build addons path
    if not addons_path:
        addons_path = f"odoo\\addons,projects\\{project}"

    # Determine the gevent/longpolling port name by version
    longpolling_key = "gevent_port" if version >= 17 else "longpolling_port"

    conf_content = f"""[options]
addons_path = {addons_path}
admin_passwd = 123
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = {database or f"{project}{version}"}.*
http_port = {port}
{longpolling_key} = {port + 3}
workers = {workers}
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_time_cpu = 600
limit_time_real = 1200
proxy_mode = False
log_level = info
data_dir = data
"""

    conf_file.write_text(conf_content, encoding="utf-8")
    print(f"[OK] Config file created: {conf_file}")
    return conf_file


# ---------------------------------------------------------------------------
# Scaffold
# ---------------------------------------------------------------------------

def scaffold_project(
    name: str,
    path: str,
    odoo_bin: str = "odoo-bin",
    python_executable: Optional[str] = None,
) -> bool:
    """Run odoo-bin scaffold to create a new module skeleton."""
    python = python_executable or sys.executable
    output_path = Path(path)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find odoo-bin
    odoo_bin_path = Path(odoo_bin)
    if not odoo_bin_path.exists():
        # Try to find odoo-bin relative to current dir
        for candidate in ["odoo-bin", "../odoo-bin", "../../odoo-bin"]:
            if Path(candidate).exists():
                odoo_bin_path = Path(candidate)
                break

    cmd = [python, str(odoo_bin_path), "scaffold", name, str(output_path)]
    print(f"[INFO] Scaffolding module: {name} -> {output_path}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"[OK] Module scaffold created: {output_path / name}")
        return True
    else:
        print(f"[ERROR] Scaffold failed (exit code {result.returncode})")
        return False


# ---------------------------------------------------------------------------
# wkhtmltopdf Check
# ---------------------------------------------------------------------------

def check_wkhtmltopdf() -> bool:
    """Verify wkhtmltopdf is installed and accessible."""
    wk_path = shutil.which("wkhtmltopdf")
    if wk_path:
        try:
            result = subprocess.run(
                ["wkhtmltopdf", "--version"],
                capture_output=True, text=True
            )
            version = result.stdout.strip()
            print(f"[OK] wkhtmltopdf found: {version} (at {wk_path})")
            return True
        except Exception:
            pass

    print("[WARNING] wkhtmltopdf not found in PATH. PDF reports may not work.")
    print("[INFO] Install wkhtmltopdf:")
    if IS_WINDOWS:
        print("       choco install wkhtmltopdf")
        print("       or download from https://wkhtmltopdf.org/downloads.html")
    elif IS_LINUX:
        print("       sudo apt-get install wkhtmltopdf")
        print("       or use the .deb from https://github.com/wkhtmltopdf/packaging/releases")
    elif IS_MAC:
        print("       brew install --cask wkhtmltopdf")
    return False


# ---------------------------------------------------------------------------
# Environment Check
# ---------------------------------------------------------------------------

def check_environment(project_root: str = ".") -> Dict[str, bool]:
    """
    Run a comprehensive environment check.
    Returns dict of check_name -> passed.
    """
    root = Path(project_root).resolve()
    results = {}

    print(f"\n{'='*50}")
    print("ENVIRONMENT CHECK")
    print(f"{'='*50}")
    print(f"Project root: {root}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()

    # Check Python version
    results["python_version"] = sys.version_info >= (3, 10)
    icon = "[OK]" if results["python_version"] else "[WARN]"
    print(f"{icon} Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check virtual environment
    env_type = detect_environment(str(root))
    results["environment"] = True
    print(f"[OK] Environment type: {env_type}")

    # Check PostgreSQL
    results["postgresql"] = check_postgresql()

    # Check wkhtmltopdf
    results["wkhtmltopdf"] = check_wkhtmltopdf()

    # Check Odoo requirements
    requirements_file = root / "requirements.txt"
    results["requirements_file"] = requirements_file.exists()
    icon = "[OK]" if results["requirements_file"] else "[WARN]"
    print(f"{icon} requirements.txt: {'found' if results['requirements_file'] else 'NOT FOUND'}")

    # Check conf directory
    conf_dir = root / "conf"
    results["conf_dir"] = conf_dir.is_dir()
    icon = "[OK]" if results["conf_dir"] else "[WARN]"
    print(f"{icon} conf/ directory: {'found' if results['conf_dir'] else 'NOT FOUND'}")

    # Check projects directory
    projects_dir = root / "projects"
    results["projects_dir"] = projects_dir.is_dir()
    icon = "[OK]" if results["projects_dir"] else "[WARN]"
    print(f"{icon} projects/ directory: {'found' if results['projects_dir'] else 'NOT FOUND'}")

    print(f"\n{'='*50}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    print(f"{'='*50}\n")

    return results


# ---------------------------------------------------------------------------
# Full Init Wizard
# ---------------------------------------------------------------------------

def full_init(
    version: int,
    project: str,
    port: int = 8069,
    workers: int = 0,
    docker: bool = False,
    create_db: bool = False,
    database: Optional[str] = None,
    project_root: str = ".",
) -> None:
    """
    Full initialization wizard for a new Odoo environment.
    Creates venv, installs requirements, generates conf file.
    """
    root = Path(project_root).resolve()
    db_name = database or f"{project}{version}"

    print(f"\n{'='*60}")
    print(f"ODOO {version} ENVIRONMENT INITIALIZATION")
    print(f"{'='*60}")
    print(f"Project: {project}")
    print(f"Version: {version}")
    print(f"Port: {port}")
    print(f"Database: {db_name}")
    print(f"Mode: {'Docker' if docker else 'Local venv'}")
    print(f"{'='*60}\n")

    if not check_python_compatibility(version):
        min_v, max_v = detect_python_version(version)
        print(f"[WARNING] Current Python {sys.version_info.major}.{sys.version_info.minor} "
              f"may not be compatible with Odoo {version}.")
        print(f"[INFO] Odoo {version} requires Python {min_v[0]}.{min_v[1]} - {max_v[0]}.{max_v[1]}")

    # Step 1: Create directories
    print("[STEP 1] Creating directory structure...")
    for d in ["conf", "logs", "data", "backups", f"projects/{project}"]:
        dir_path = root / d
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] {dir_path}")

    # Step 2: Create venv (if not Docker)
    if not docker:
        print("\n[STEP 2] Creating virtual environment...")
        venv_path = root / ".venv"
        if not venv_path.exists():
            create_venv(str(venv_path))
        else:
            print(f"  [INFO] Virtual environment already exists at {venv_path}")

        # Step 3: Install requirements
        print("\n[STEP 3] Installing requirements...")
        req_file = root / "requirements.txt"
        if req_file.exists():
            install_requirements(str(venv_path), str(req_file))
        else:
            print("  [WARNING] requirements.txt not found. Skipping.")

        # Project-specific requirements
        proj_req = root / "projects" / project / "requirements.txt"
        if proj_req.exists():
            print(f"\n  Installing project-specific requirements...")
            install_requirements(str(venv_path), str(proj_req))

    # Step 4: Check PostgreSQL
    print("\n[STEP 4] Checking PostgreSQL...")
    pg_ok = check_postgresql()
    if not pg_ok:
        print("  [WARNING] PostgreSQL not accessible. Configure it before running Odoo.")

    # Step 5: Generate config file
    print("\n[STEP 5] Generating configuration file...")
    conf_file = create_conf_file(
        project=project,
        version=version,
        database=db_name,
        port=port,
        workers=workers,
        output_dir=str(root / "conf"),
    )

    # Step 6: Generate .gitignore
    print("\n[STEP 6] Creating .gitignore...")
    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
        print(f"  [OK] .gitignore created.")
    else:
        print(f"  [INFO] .gitignore already exists.")

    # Step 7: Check wkhtmltopdf
    print("\n[STEP 7] Checking wkhtmltopdf...")
    check_wkhtmltopdf()

    # Summary
    print(f"\n{'='*60}")
    print("INITIALIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"Config file: {conf_file}")
    print(f"\nNext steps:")
    if not docker:
        if IS_WINDOWS:
            print(f"  1. Activate venv:  .venv\\Scripts\\activate")
        else:
            print(f"  1. Activate venv:  source .venv/bin/activate")
    print(f"  2. Start Odoo:     python -m odoo -c {conf_file} --dev=all")
    print(f"  3. Open browser:   http://localhost:{port}")
    print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Odoo Environment Initializer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command")

    # init
    init_p = subparsers.add_parser("init", help="Full environment initialization")
    init_p.add_argument("--version", "-v", type=int, required=True, choices=[14,15,16,17,18,19])
    init_p.add_argument("--project", "-p", required=True)
    init_p.add_argument("--port", type=int, default=8069)
    init_p.add_argument("--workers", type=int, default=0)
    init_p.add_argument("--docker", action="store_true")
    init_p.add_argument("--db", help="Database name (default: project+version)")
    init_p.add_argument("--root", default=".", help="Project root directory")

    # venv
    venv_p = subparsers.add_parser("venv", help="Create virtual environment")
    venv_p.add_argument("--path", default=".venv")
    venv_p.add_argument("--python", help="Python executable to use")

    # check
    check_p = subparsers.add_parser("check", help="Check environment health")
    check_p.add_argument("--root", default=".")

    # conf
    conf_p = subparsers.add_parser("conf", help="Generate config file only")
    conf_p.add_argument("--project", "-p", required=True)
    conf_p.add_argument("--version", "-v", type=int, required=True)
    conf_p.add_argument("--db", help="Database name")
    conf_p.add_argument("--port", type=int, default=8069)
    conf_p.add_argument("--output-dir", default="conf")

    # scaffold
    scaffold_p = subparsers.add_parser("scaffold", help="Scaffold new Odoo module")
    scaffold_p.add_argument("--name", "-n", required=True)
    scaffold_p.add_argument("--path", required=True)
    scaffold_p.add_argument("--odoo-bin", default="odoo-bin")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        full_init(
            version=args.version,
            project=args.project,
            port=args.port,
            workers=args.workers,
            docker=args.docker,
            database=args.db,
            project_root=args.root,
        )

    elif args.command == "venv":
        create_venv(path=args.path, python_executable=getattr(args, "python", None))

    elif args.command == "check":
        results = check_environment(project_root=args.root)
        passed = all(results.values())
        sys.exit(0 if passed else 1)

    elif args.command == "conf":
        create_conf_file(
            project=args.project,
            version=args.version,
            database=args.db,
            port=args.port,
            output_dir=args.output_dir,
        )

    elif args.command == "scaffold":
        success = scaffold_project(
            name=args.name,
            path=args.path,
            odoo_bin=args.odoo_bin,
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
