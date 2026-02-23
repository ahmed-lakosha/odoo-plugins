#!/usr/bin/env python3
"""
docker_manager.py — Odoo Docker Manager

Generate Dockerfiles and docker-compose.yml files, and manage Docker containers
for Odoo deployments. Supports Odoo 14-19.

Usage:
    python docker_manager.py init --version 17 --project myproject [--port 8069]
    python docker_manager.py build
    python docker_manager.py up [--detach]
    python docker_manager.py down [--volumes]
    python docker_manager.py start
    python docker_manager.py stop
    python docker_manager.py restart [--service odoo]
    python docker_manager.py logs [--follow] [--tail 100]
    python docker_manager.py shell [--service odoo]
    python docker_manager.py odoo-shell --db mydb
    python docker_manager.py update --db mydb --module my_module
    python docker_manager.py status
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

IS_WINDOWS = platform.system() == "Windows"


# ---------------------------------------------------------------------------
# Dockerfile Templates
# ---------------------------------------------------------------------------

DOCKERFILES: dict = {
    14: """\
FROM python:3.8-slim-buster

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libjpeg62-turbo-dev \\
    libfreetype6-dev \\
    libsasl2-dev \\
    libldap2-dev \\
    libssl-dev \\
    node-less \\
    npm \\
    git \\
    postgresql-client \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.buster_amd64.deb \\
    && dpkg -i wkhtmltox_0.12.6.1-3.buster_amd64.deb \\
    && rm wkhtmltox_0.12.6.1-3.buster_amd64.deb

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
""",

    15: """\
FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libjpeg-dev \\
    libfreetype6-dev \\
    libsasl2-dev \\
    libldap2-dev \\
    libssl-dev \\
    npm \\
    git \\
    postgresql-client \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb \\
    && dpkg -i wkhtmltox_0.12.6.1-3.bullseye_amd64.deb \\
    && rm wkhtmltox_0.12.6.1-3.bullseye_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
""",

    16: """\
FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libjpeg-dev \\
    libfreetype6-dev \\
    libsasl2-dev \\
    libldap2-dev \\
    libssl-dev \\
    libffi-dev \\
    npm \\
    git \\
    postgresql-client \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb \\
    && dpkg -i wkhtmltox_0.12.6.1-3.bullseye_amd64.deb \\
    && rm wkhtmltox_0.12.6.1-3.bullseye_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
""",

    17: """\
FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libjpeg-dev \\
    libfreetype6-dev \\
    libsasl2-dev \\
    libldap2-dev \\
    libssl-dev \\
    libffi-dev \\
    liblzma-dev \\
    npm \\
    git \\
    postgresql-client \\
    wget \\
    curl \\
    gettext-base \\
    fonts-noto-cjk \\
    fonts-noto-core \\
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \\
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \\
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip \\
    && pip install -r requirements.txt \\
    && pip install geoip2

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
""",

    18: """\
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libjpeg-dev \\
    libfreetype6-dev \\
    libsasl2-dev \\
    libldap2-dev \\
    libssl-dev \\
    libffi-dev \\
    npm \\
    git \\
    postgresql-client \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \\
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \\
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip \\
    && pip install -r requirements.txt \\
    && pip install cbor2

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
""",

    19: """\
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \\
    build-essential \\
    libpq-dev \\
    libxml2-dev \\
    libxslt1-dev \\
    libjpeg-dev \\
    libfreetype6-dev \\
    libsasl2-dev \\
    libldap2-dev \\
    libssl-dev \\
    libffi-dev \\
    libmagic1 \\
    npm \\
    git \\
    postgresql-client \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \\
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \\
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip \\
    && pip install -r requirements.txt \\
    && pip install cbor2 python-magic

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
""",
}


# ---------------------------------------------------------------------------
# docker-compose Template
# ---------------------------------------------------------------------------

def _compose_template(project_name: str, odoo_version: int, http_port: int = 8069) -> str:
    lp_port = http_port + 3
    pg_version = "15" if odoo_version >= 18 else "12"

    return f"""\
version: '3.8'

services:
  db:
    image: postgres:{pg_version}
    container_name: {project_name}_db
    environment:
      POSTGRES_USER: ${{POSTGRES_USER:-odoo}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD:-odoo}}
      POSTGRES_DB: postgres
    volumes:
      - {project_name}_db_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${{POSTGRES_USER:-odoo}}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    restart: unless-stopped

  odoo:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {project_name}_web
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/opt/odoo/source:ro
      - ./projects:/opt/odoo/custom-addons
      - ./conf:/etc/odoo:ro
      - {project_name}_filestore:/var/lib/odoo
      - ./logs:/var/log/odoo
    ports:
      - "${{ODOO_HTTP_PORT:-{http_port}}}:{http_port}"
      - "${{ODOO_LONGPOLLING_PORT:-{lp_port}}}:{lp_port}"
    environment:
      POSTGRES_HOST: db
      POSTGRES_PORT: 5432
      POSTGRES_USER: ${{POSTGRES_USER:-odoo}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD:-odoo}}
    restart: unless-stopped

volumes:
  {project_name}_db_data:
  {project_name}_filestore:
"""


def _env_template(project_name: str, http_port: int = 8069) -> str:
    lp_port = http_port + 3
    return f"""\
# .env — Docker environment variables
# Copy this file to .env and customize

# PostgreSQL
POSTGRES_USER=odoo
POSTGRES_PASSWORD=change_me_in_production
POSTGRES_DB=postgres

# Odoo ports
ODOO_HTTP_PORT={http_port}
ODOO_LONGPOLLING_PORT={lp_port}

# Development mode (set to 'all' for dev, empty for prod)
DEV_MODE=all

# Project info
PROJECT_NAME={project_name}
"""


# ---------------------------------------------------------------------------
# File Generators
# ---------------------------------------------------------------------------

def generate_dockerfile(odoo_version: int, output_path: str = ".") -> Path:
    """Write a version-appropriate Dockerfile to the given directory."""
    if odoo_version not in DOCKERFILES:
        raise ValueError(f"Unsupported Odoo version: {odoo_version}. Supported: {list(DOCKERFILES.keys())}")

    out = Path(output_path) / "Dockerfile"
    out.write_text(DOCKERFILES[odoo_version], encoding="utf-8")
    print(f"[OK] Dockerfile created for Odoo {odoo_version}: {out}")
    return out


def generate_compose(
    project_name: str,
    odoo_version: int,
    http_port: int = 8069,
    output_path: str = ".",
) -> Path:
    """Write docker-compose.yml to the given directory."""
    content = _compose_template(project_name, odoo_version, http_port)
    out = Path(output_path) / "docker-compose.yml"
    out.write_text(content, encoding="utf-8")
    print(f"[OK] docker-compose.yml created: {out}")
    return out


def generate_env_file(project_name: str, http_port: int = 8069, output_path: str = ".") -> Path:
    """Write .env.example to the given directory."""
    content = _env_template(project_name, http_port)
    out = Path(output_path) / ".env.example"
    out.write_text(content, encoding="utf-8")

    # Also create .env if it doesn't exist
    env_out = Path(output_path) / ".env"
    if not env_out.exists():
        env_out.write_text(content, encoding="utf-8")
        print(f"[OK] .env created: {env_out}")
    else:
        print(f"[INFO] .env already exists, not overwriting.")

    print(f"[OK] .env.example created: {out}")
    return out


# ---------------------------------------------------------------------------
# Docker-Compose Commands
# ---------------------------------------------------------------------------

def _compose_cmd(compose_file: Optional[str] = None) -> List[str]:
    """Base docker-compose command."""
    cmd = ["docker-compose"]
    if compose_file:
        cmd += ["-f", compose_file]
    return cmd


def _run(cmd: List[str]) -> int:
    """Run a command and return exit code."""
    print(f"[CMD] {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def build(compose_file: Optional[str] = None, no_cache: bool = False) -> int:
    """Build Docker images."""
    cmd = _compose_cmd(compose_file) + ["build"]
    if no_cache:
        cmd.append("--no-cache")
    return _run(cmd)


def up(
    compose_file: Optional[str] = None,
    detach: bool = True,
    build_first: bool = False,
) -> int:
    """Start Docker containers."""
    cmd = _compose_cmd(compose_file) + ["up"]
    if detach:
        cmd.append("-d")
    if build_first:
        cmd.append("--build")
    return _run(cmd)


def down(compose_file: Optional[str] = None, volumes: bool = False) -> int:
    """Stop and remove Docker containers."""
    cmd = _compose_cmd(compose_file) + ["down"]
    if volumes:
        cmd.append("-v")
        print("[WARNING] -v flag will also DELETE volumes (database data). This is irreversible!")
    return _run(cmd)


def start(compose_file: Optional[str] = None) -> int:
    """Start existing Docker containers."""
    return _run(_compose_cmd(compose_file) + ["start"])


def stop(compose_file: Optional[str] = None) -> int:
    """Stop running Docker containers without removing them."""
    return _run(_compose_cmd(compose_file) + ["stop"])


def restart(compose_file: Optional[str] = None, service: str = "odoo") -> int:
    """Restart a Docker service."""
    cmd = _compose_cmd(compose_file) + ["restart"]
    if service:
        cmd.append(service)
    return _run(cmd)


def logs(
    compose_file: Optional[str] = None,
    follow: bool = True,
    tail: int = 100,
    service: str = "odoo",
) -> int:
    """View Docker container logs."""
    cmd = _compose_cmd(compose_file) + ["logs"]
    if follow:
        cmd.append("-f")
    cmd += ["--tail", str(tail)]
    if service:
        cmd.append(service)
    return _run(cmd)


def shell(compose_file: Optional[str] = None, service: str = "odoo") -> int:
    """Open a bash shell in a Docker container."""
    cmd = _compose_cmd(compose_file) + ["exec", service, "bash"]
    return _run(cmd)


def odoo_shell(
    compose_file: Optional[str] = None,
    database: str = "",
    odoo_conf: str = "/etc/odoo/odoo.conf",
) -> int:
    """Open an Odoo Python shell in the Docker container."""
    inner_cmd = f"python -m odoo shell -d {database} -c {odoo_conf}"
    cmd = _compose_cmd(compose_file) + ["exec", "odoo", "bash", "-c", inner_cmd]
    return _run(cmd)


def update_module_docker(
    compose_file: Optional[str],
    database: str,
    module: str,
    odoo_conf: str = "/etc/odoo/odoo.conf",
) -> int:
    """Update an Odoo module inside a Docker container."""
    inner_cmd = (
        f"python -m odoo -c {odoo_conf} "
        f"-d {database} -u {module} --stop-after-init"
    )
    cmd = _compose_cmd(compose_file) + ["exec", "odoo", "bash", "-c", inner_cmd]
    return _run(cmd)


def install_module_docker(
    compose_file: Optional[str],
    database: str,
    module: str,
    odoo_conf: str = "/etc/odoo/odoo.conf",
) -> int:
    """Install an Odoo module inside a Docker container."""
    inner_cmd = (
        f"python -m odoo -c {odoo_conf} "
        f"-d {database} -i {module} --stop-after-init"
    )
    cmd = _compose_cmd(compose_file) + ["exec", "odoo", "bash", "-c", inner_cmd]
    return _run(cmd)


def status(compose_file: Optional[str] = None) -> int:
    """Show Docker container status."""
    return _run(_compose_cmd(compose_file) + ["ps"])


def db_backup_docker(
    container_name: str,
    database: str,
    output_path: str,
    user: str = "odoo",
) -> bool:
    """Backup PostgreSQL database from Docker container."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Backing up '{database}' from container '{container_name}'...")
    with open(out, "wb") as f:
        result = subprocess.run(
            ["docker", "exec", container_name, "pg_dump", "-U", user, "-Fc", database],
            stdout=f,
            stderr=subprocess.PIPE,
        )

    if result.returncode == 0:
        size = out.stat().st_size / (1024 * 1024)
        print(f"[OK] Backup: {out} ({size:.1f} MB)")
        return True
    else:
        print(f"[ERROR] Backup failed")
        return False


def db_restore_docker(
    container_name: str,
    database: str,
    backup_file: str,
    user: str = "odoo",
) -> bool:
    """Restore database into Docker PostgreSQL container."""
    bp = Path(backup_file)
    if not bp.exists():
        print(f"[ERROR] Backup file not found: {backup_file}")
        return False

    with open(bp, "rb") as f:
        result = subprocess.run(
            ["docker", "exec", "-i", container_name,
             "pg_restore", "-U", user, "-d", database],
            stdin=f,
            capture_output=True,
        )

    if result.returncode in (0, 1):
        print(f"[OK] Restore complete: {database}")
        return True
    else:
        print(f"[ERROR] Restore failed")
        return False


# ---------------------------------------------------------------------------
# Full Init
# ---------------------------------------------------------------------------

def init_docker_project(
    project_name: str,
    odoo_version: int,
    http_port: int = 8069,
    output_path: str = ".",
) -> None:
    """Generate all Docker files for a new Odoo project."""
    out = Path(output_path)
    out.mkdir(parents=True, exist_ok=True)

    print(f"\n[INFO] Initializing Docker project: {project_name} (Odoo {odoo_version})")

    generate_dockerfile(odoo_version, str(out))
    generate_compose(project_name, odoo_version, http_port, str(out))
    generate_env_file(project_name, http_port, str(out))

    # Create required directories
    for d in ["conf", "logs", "backups", f"projects/{project_name}"]:
        (out / d).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {out / d}")

    print(f"\n[OK] Docker project initialized in: {out}")
    print("\nNext steps:")
    print(f"  1. Edit .env to set passwords")
    print(f"  2. Add your .conf file to conf/")
    print(f"  3. Run: docker-compose build")
    print(f"  4. Run: docker-compose up -d")
    print(f"  5. Open: http://localhost:{http_port}")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Odoo Docker Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    def add_compose_arg(p):
        p.add_argument("--compose-file", "-f", help="docker-compose file path")

    # init
    init_p = subparsers.add_parser("init", help="Generate Docker files for new project")
    init_p.add_argument("--version", "-v", type=int, required=True, choices=[14,15,16,17,18,19])
    init_p.add_argument("--project", "-p", required=True)
    init_p.add_argument("--port", type=int, default=8069)
    init_p.add_argument("--output", "-o", default=".")

    # build
    build_p = subparsers.add_parser("build", help="Build Docker images")
    build_p.add_argument("--no-cache", action="store_true")
    add_compose_arg(build_p)

    # up
    up_p = subparsers.add_parser("up", help="Start containers")
    up_p.add_argument("--no-detach", action="store_true")
    up_p.add_argument("--build", action="store_true", dest="build_first")
    add_compose_arg(up_p)

    # down
    down_p = subparsers.add_parser("down", help="Stop and remove containers")
    down_p.add_argument("--volumes", "-v", action="store_true")
    add_compose_arg(down_p)

    # start
    start_p = subparsers.add_parser("start", help="Start existing containers")
    add_compose_arg(start_p)

    # stop
    stop_p = subparsers.add_parser("stop", help="Stop containers")
    add_compose_arg(stop_p)

    # restart
    restart_p = subparsers.add_parser("restart", help="Restart service")
    restart_p.add_argument("--service", default="odoo")
    add_compose_arg(restart_p)

    # logs
    logs_p = subparsers.add_parser("logs", help="View container logs")
    logs_p.add_argument("--no-follow", action="store_true")
    logs_p.add_argument("--tail", type=int, default=100)
    logs_p.add_argument("--service", default="odoo")
    add_compose_arg(logs_p)

    # shell
    shell_p = subparsers.add_parser("shell", help="Open bash shell in container")
    shell_p.add_argument("--service", default="odoo")
    add_compose_arg(shell_p)

    # odoo-shell
    oshell_p = subparsers.add_parser("odoo-shell", help="Open Odoo Python shell in container")
    oshell_p.add_argument("--db", required=True)
    oshell_p.add_argument("--conf", default="/etc/odoo/odoo.conf")
    add_compose_arg(oshell_p)

    # update
    update_p = subparsers.add_parser("update", help="Update Odoo module in container")
    update_p.add_argument("--db", required=True)
    update_p.add_argument("--module", "-m", required=True)
    update_p.add_argument("--conf", default="/etc/odoo/odoo.conf")
    add_compose_arg(update_p)

    # install
    install_p = subparsers.add_parser("install", help="Install Odoo module in container")
    install_p.add_argument("--db", required=True)
    install_p.add_argument("--module", "-m", required=True)
    install_p.add_argument("--conf", default="/etc/odoo/odoo.conf")
    add_compose_arg(install_p)

    # status
    status_p = subparsers.add_parser("status", help="Show container status")
    add_compose_arg(status_p)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    cf = getattr(args, "compose_file", None)

    if args.command == "init":
        init_docker_project(args.project, args.version, args.port, args.output)

    elif args.command == "build":
        sys.exit(build(cf, args.no_cache))

    elif args.command == "up":
        sys.exit(up(cf, detach=not args.no_detach, build_first=args.build_first))

    elif args.command == "down":
        sys.exit(down(cf, volumes=args.volumes))

    elif args.command == "start":
        sys.exit(start(cf))

    elif args.command == "stop":
        sys.exit(stop(cf))

    elif args.command == "restart":
        sys.exit(restart(cf, service=args.service))

    elif args.command == "logs":
        sys.exit(logs(cf, follow=not args.no_follow, tail=args.tail, service=args.service))

    elif args.command == "shell":
        sys.exit(shell(cf, service=args.service))

    elif args.command == "odoo-shell":
        sys.exit(odoo_shell(cf, database=args.db, odoo_conf=args.conf))

    elif args.command == "update":
        sys.exit(update_module_docker(cf, args.db, args.module, args.conf))

    elif args.command == "install":
        sys.exit(install_module_docker(cf, args.db, args.module, args.conf))

    elif args.command == "status":
        sys.exit(status(cf))


if __name__ == "__main__":
    main()
