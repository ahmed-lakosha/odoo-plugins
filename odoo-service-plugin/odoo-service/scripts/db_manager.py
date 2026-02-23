#!/usr/bin/env python3
"""
db_manager.py — Odoo Database Manager

Backup, restore, create, drop, and manage PostgreSQL databases for Odoo.
Supports local PostgreSQL and Docker containers.

Usage:
    python db_manager.py backup --db mydb [--format sql|dump] --output backups/
    python db_manager.py restore --file backups/backup.dump --db newdb
    python db_manager.py create --db newproject17
    python db_manager.py drop --db oldproject
    python db_manager.py list
    python db_manager.py reset-admin --db mydb --password newpass
    python db_manager.py modules --db mydb
    python db_manager.py auto-backup --config conf/myproject.conf --output backups/
"""

import argparse
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

IS_WINDOWS = platform.system() == "Windows"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pg_env(user: str, password: str) -> dict:
    """Build environment dict with PostgreSQL credentials."""
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    env["PGUSER"] = user
    return env


def _pg_args(host: str, port: int, user: str) -> List[str]:
    """Common PostgreSQL connection arguments."""
    return ["-h", host, "-p", str(port), "-U", user]


def _timestamp() -> str:
    """Return current timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _run(cmd: List[str], env: Optional[dict] = None, input_data: Optional[str] = None) -> int:
    """Run a subprocess command and return exit code."""
    print(f"[CMD] {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        env=env or os.environ.copy(),
        input=input_data,
        text=bool(input_data),
    )
    return result.returncode


def _run_capture(
    cmd: List[str],
    env: Optional[dict] = None
) -> tuple:
    """Run command and capture output. Returns (stdout, stderr, returncode)."""
    result = subprocess.run(
        cmd,
        env=env or os.environ.copy(),
        capture_output=True,
        text=True,
    )
    return result.stdout, result.stderr, result.returncode


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

def backup_sql(
    database: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
    output_dir: str = "backups",
) -> Optional[Path]:
    """
    Backup database to plain SQL format using pg_dump.
    Returns path to backup file or None on failure.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = out_dir / f"{database}_{_timestamp()}.sql"
    env = _pg_env(user, password)

    cmd = ["pg_dump"] + _pg_args(host, port, user) + [database]
    print(f"[INFO] Backing up '{database}' to SQL: {filename}")

    with open(filename, "w", encoding="utf-8") as f:
        result = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        size = filename.stat().st_size / (1024 * 1024)
        print(f"[OK] Backup complete: {filename} ({size:.1f} MB)")
        return filename
    else:
        print(f"[ERROR] Backup failed: {result.stderr.strip()}")
        if filename.exists():
            filename.unlink()
        return None


def backup_dump(
    database: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
    output_dir: str = "backups",
) -> Optional[Path]:
    """
    Backup database to custom (compressed) format using pg_dump -Fc.
    Returns path to backup file or None on failure.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = out_dir / f"{database}_{_timestamp()}.dump"
    env = _pg_env(user, password)

    cmd = ["pg_dump"] + _pg_args(host, port, user) + ["-Fc", database, "-f", str(filename)]
    print(f"[INFO] Backing up '{database}' to dump: {filename}")

    rc = _run(cmd, env=env)

    if rc == 0:
        size = filename.stat().st_size / (1024 * 1024)
        print(f"[OK] Backup complete: {filename} ({size:.1f} MB)")
        return filename
    else:
        print(f"[ERROR] Backup failed with exit code {rc}")
        return None


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

def restore_sql(
    backup_file: str,
    database: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
    create_db: bool = True,
) -> bool:
    """Restore database from a SQL file."""
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"[ERROR] Backup file not found: {backup_file}")
        return False

    env = _pg_env(user, password)

    # Create database if requested
    if create_db:
        print(f"[INFO] Creating database: {database}")
        rc = _run(["createdb"] + _pg_args(host, port, user) + [database], env=env)
        if rc != 0:
            print(f"[ERROR] Could not create database '{database}'")
            return False

    print(f"[INFO] Restoring '{database}' from: {backup_file}")

    cmd = ["psql"] + _pg_args(host, port, user) + ["-d", database, "-f", str(backup_path)]
    rc = _run(cmd, env=env)

    if rc == 0:
        print(f"[OK] Restore complete: {database}")
        return True
    else:
        print(f"[ERROR] Restore failed (exit code {rc})")
        return False


def restore_dump(
    backup_file: str,
    database: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
    create_db: bool = True,
    jobs: int = 1,
) -> bool:
    """Restore database from a custom dump file (pg_restore)."""
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"[ERROR] Backup file not found: {backup_file}")
        return False

    env = _pg_env(user, password)

    # Create database if requested
    if create_db:
        print(f"[INFO] Creating database: {database}")
        rc = _run(["createdb"] + _pg_args(host, port, user) + [database], env=env)
        if rc != 0:
            print(f"[ERROR] Could not create database '{database}'")
            return False

    print(f"[INFO] Restoring '{database}' from dump: {backup_file}")

    cmd = (
        ["pg_restore"] +
        _pg_args(host, port, user) +
        ["-d", database, "-j", str(jobs), str(backup_path)]
    )
    rc = _run(cmd, env=env)

    if rc == 0:
        print(f"[OK] Restore complete: {database}")
        return True
    else:
        print(f"[WARNING] Restore completed with warnings (exit code {rc}). This is often normal.")
        return True  # pg_restore often returns 1 for non-fatal errors


def restore_auto(
    backup_file: str,
    database: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
    create_db: bool = True,
) -> bool:
    """Auto-detect backup format and restore."""
    path = Path(backup_file)

    if path.suffix == ".sql":
        return restore_sql(backup_file, database, host, port, user, password, create_db)
    elif path.suffix == ".dump":
        return restore_dump(backup_file, database, host, port, user, password, create_db)
    else:
        # Try dump format first
        print(f"[INFO] Unknown extension '{path.suffix}'. Trying dump format...")
        return restore_dump(backup_file, database, host, port, user, password, create_db)


# ---------------------------------------------------------------------------
# Create / Drop
# ---------------------------------------------------------------------------

def create_database(
    name: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
) -> bool:
    """Create a new PostgreSQL database."""
    env = _pg_env(user, password)
    cmd = ["createdb"] + _pg_args(host, port, user) + [name]
    print(f"[INFO] Creating database: {name}")
    rc = _run(cmd, env=env)

    if rc == 0:
        print(f"[OK] Database created: {name}")
        return True
    else:
        print(f"[ERROR] Failed to create database '{name}' (exit code {rc})")
        return False


def drop_database(
    name: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
    confirm: bool = True,
) -> bool:
    """Drop a PostgreSQL database with optional confirmation prompt."""
    if confirm:
        response = input(f"Are you sure you want to DROP database '{name}'? [yes/N]: ").strip().lower()
        if response != "yes":
            print("[INFO] Drop cancelled.")
            return False

    env = _pg_env(user, password)
    cmd = ["dropdb"] + _pg_args(host, port, user) + [name]
    print(f"[INFO] Dropping database: {name}")
    rc = _run(cmd, env=env)

    if rc == 0:
        print(f"[OK] Database dropped: {name}")
        return True
    else:
        print(f"[ERROR] Failed to drop database '{name}' (exit code {rc})")
        return False


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

def list_databases(
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
) -> List[str]:
    """List all PostgreSQL databases."""
    env = _pg_env(user, password)
    cmd = ["psql"] + _pg_args(host, port, user) + [
        "-c",
        "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;",
        "-t", "-A"
    ]
    stdout, stderr, rc = _run_capture(cmd, env=env)

    if rc == 0:
        databases = [line.strip() for line in stdout.splitlines() if line.strip()]
        print(f"[OK] Found {len(databases)} database(s):")
        for db in databases:
            print(f"  - {db}")
        return databases
    else:
        print(f"[ERROR] Could not list databases: {stderr.strip()}")
        return []


# ---------------------------------------------------------------------------
# Admin Password
# ---------------------------------------------------------------------------

def reset_admin_password(
    database: str,
    new_password: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
) -> bool:
    """Reset the Odoo admin user password directly in PostgreSQL."""
    env = _pg_env(user, password)

    # Use bcrypt hash or plaintext (Odoo will re-hash on next login)
    sql = f"UPDATE res_users SET password='{new_password}' WHERE login='admin';"
    cmd = (
        ["psql"] +
        _pg_args(host, port, user) +
        ["-d", database, "-c", sql]
    )
    print(f"[INFO] Resetting admin password for database: {database}")
    rc = _run(cmd, env=env)

    if rc == 0:
        print(f"[OK] Admin password reset. Log in with 'admin' / '{new_password}'")
        print("[INFO] Odoo will re-hash the password on first login.")
        return True
    else:
        print(f"[ERROR] Failed to reset admin password (exit code {rc})")
        return False


# ---------------------------------------------------------------------------
# Module Query
# ---------------------------------------------------------------------------

def check_odoo_installed_modules(
    database: str,
    host: str = "localhost",
    port: int = 5432,
    user: str = "odoo",
    password: str = "odoo",
) -> List[str]:
    """Query and return list of installed Odoo modules."""
    env = _pg_env(user, password)
    sql = "SELECT name FROM ir_module_module WHERE state='installed' ORDER BY name;"
    cmd = (
        ["psql"] +
        _pg_args(host, port, user) +
        ["-d", database, "-c", sql, "-t", "-A"]
    )

    stdout, stderr, rc = _run_capture(cmd, env=env)

    if rc == 0:
        modules = [line.strip() for line in stdout.splitlines() if line.strip()]
        print(f"[OK] Found {len(modules)} installed module(s) in '{database}':")
        for m in modules:
            print(f"  - {m}")
        return modules
    else:
        print(f"[ERROR] Could not query modules: {stderr.strip()}")
        return []


# ---------------------------------------------------------------------------
# Auto Backup (from .conf file)
# ---------------------------------------------------------------------------

def auto_backup(
    config_file: str,
    output_dir: str = "backups",
    backup_format: str = "dump",
) -> List[Path]:
    """
    Read Odoo .conf file and backup all databases matching the dbfilter.
    Returns list of created backup files.
    """
    import configparser

    conf = configparser.ConfigParser()
    conf.read(config_file)

    options = conf.get("options", fallback=None)
    if not conf.has_section("options"):
        print(f"[ERROR] No [options] section in config file: {config_file}")
        return []

    host = conf.get("options", "db_host", fallback="localhost")
    port = int(conf.get("options", "db_port", fallback="5432"))
    user = conf.get("options", "db_user", fallback="odoo")
    password_val = conf.get("options", "db_password", fallback="odoo")
    dbfilter = conf.get("options", "dbfilter", fallback="")

    print(f"[INFO] Auto-backup from config: {config_file}")
    print(f"[INFO] DB filter pattern: {dbfilter}")

    # List all databases
    databases = list_databases(host, port, user, password_val)

    # Filter by dbfilter pattern (simplified regex match)
    import re
    pattern = dbfilter.replace(".*", ".*").replace("*", ".*")

    matching = []
    for db in databases:
        if not dbfilter or re.match(pattern, db):
            matching.append(db)

    print(f"[INFO] Backing up {len(matching)} database(s) matching filter...")

    backups = []
    for db in matching:
        if backup_format == "sql":
            path = backup_sql(db, host, port, user, password_val, output_dir)
        else:
            path = backup_dump(db, host, port, user, password_val, output_dir)
        if path:
            backups.append(path)

    print(f"\n[OK] Auto-backup complete. {len(backups)}/{len(matching)} succeeded.")
    return backups


# ---------------------------------------------------------------------------
# Docker Database Operations
# ---------------------------------------------------------------------------

def backup_docker(
    container_name: str,
    database: str,
    output_path: str,
    user: str = "odoo",
    backup_format: str = "dump",
) -> bool:
    """Backup a PostgreSQL database from a Docker container."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Backing up '{database}' from Docker container '{container_name}'...")

    if backup_format == "sql":
        cmd = ["docker", "exec", container_name, "pg_dump", "-U", user, database]
        with open(out, "w", encoding="utf-8") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
    else:
        cmd = ["docker", "exec", container_name, "pg_dump", "-U", user, "-Fc", database]
        with open(out, "wb") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)

    if result.returncode == 0:
        size = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"[OK] Docker backup complete: {output_path} ({size:.1f} MB)")
        return True
    else:
        print(f"[ERROR] Docker backup failed")
        return False


def restore_docker(
    container_name: str,
    database: str,
    backup_file: str,
    user: str = "odoo",
) -> bool:
    """Restore a database into a Docker PostgreSQL container."""
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"[ERROR] Backup file not found: {backup_file}")
        return False

    print(f"[INFO] Restoring '{database}' in Docker container '{container_name}'...")

    if backup_file.endswith(".sql"):
        # cat file | docker exec -i container psql
        with open(backup_path, "r", encoding="utf-8") as f:
            result = subprocess.run(
                ["docker", "exec", "-i", container_name, "psql", "-U", user, database],
                stdin=f,
                capture_output=True,
                text=True,
            )
    else:
        # pg_restore via docker exec -i
        with open(backup_path, "rb") as f:
            result = subprocess.run(
                ["docker", "exec", "-i", container_name, "pg_restore", "-U", user, "-d", database],
                stdin=f,
                capture_output=True,
            )

    if result.returncode in (0, 1):  # pg_restore returns 1 for warnings
        print(f"[OK] Docker restore complete: {database}")
        return True
    else:
        print(f"[ERROR] Docker restore failed")
        return False


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Odoo Database Manager — backup, restore, create, drop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Common database connection arguments
    def add_db_args(p):
        p.add_argument("--host", default="localhost")
        p.add_argument("--port", type=int, default=5432)
        p.add_argument("--user", "-U", default="odoo")
        p.add_argument("--password", "-W", default="odoo")

    subparsers = parser.add_subparsers(dest="command")

    # backup
    backup_p = subparsers.add_parser("backup", help="Backup database")
    backup_p.add_argument("--db", "-d", required=True)
    backup_p.add_argument("--format", choices=["sql", "dump"], default="dump")
    backup_p.add_argument("--output", "-o", default="backups")
    backup_p.add_argument("--docker", help="Docker container name (optional)")
    add_db_args(backup_p)

    # restore
    restore_p = subparsers.add_parser("restore", help="Restore database from backup")
    restore_p.add_argument("--file", "-f", required=True)
    restore_p.add_argument("--db", "-d", required=True)
    restore_p.add_argument("--no-create", action="store_true", help="Skip database creation")
    restore_p.add_argument("--docker", help="Docker container name (optional)")
    add_db_args(restore_p)

    # create
    create_p = subparsers.add_parser("create", help="Create new database")
    create_p.add_argument("--db", "-d", required=True)
    add_db_args(create_p)

    # drop
    drop_p = subparsers.add_parser("drop", help="Drop database")
    drop_p.add_argument("--db", "-d", required=True)
    drop_p.add_argument("--yes", action="store_true", help="Skip confirmation")
    add_db_args(drop_p)

    # list
    list_p = subparsers.add_parser("list", help="List databases")
    add_db_args(list_p)

    # reset-admin
    reset_p = subparsers.add_parser("reset-admin", help="Reset admin password")
    reset_p.add_argument("--db", "-d", required=True)
    reset_p.add_argument("--password", "-p", required=True)
    reset_p.add_argument("--host", default="localhost")
    reset_p.add_argument("--port", type=int, default=5432)
    reset_p.add_argument("--user", "-U", default="odoo")
    reset_p.add_argument("--pg-password", default="odoo")

    # modules
    modules_p = subparsers.add_parser("modules", help="List installed Odoo modules")
    modules_p.add_argument("--db", "-d", required=True)
    add_db_args(modules_p)

    # auto-backup
    auto_p = subparsers.add_parser("auto-backup", help="Backup all DBs matching config filter")
    auto_p.add_argument("--config", "-c", required=True)
    auto_p.add_argument("--output", "-o", default="backups")
    auto_p.add_argument("--format", choices=["sql", "dump"], default="dump")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    host = getattr(args, "host", "localhost")
    port = getattr(args, "port", 5432)
    user = getattr(args, "user", "odoo")
    password = getattr(args, "password", "odoo")

    if args.command == "backup":
        docker = getattr(args, "docker", None)
        if docker:
            ts = _timestamp()
            out = Path(args.output) / f"{args.db}_{ts}.{args.format}"
            success = backup_docker(docker, args.db, str(out), user, args.format)
        elif args.format == "sql":
            path = backup_sql(args.db, host, port, user, password, args.output)
            success = path is not None
        else:
            path = backup_dump(args.db, host, port, user, password, args.output)
            success = path is not None
        sys.exit(0 if success else 1)

    elif args.command == "restore":
        docker = getattr(args, "docker", None)
        if docker:
            success = restore_docker(docker, args.db, args.file, user)
        else:
            success = restore_auto(
                args.file, args.db, host, port, user, password,
                create_db=not args.no_create
            )
        sys.exit(0 if success else 1)

    elif args.command == "create":
        success = create_database(args.db, host, port, user, password)
        sys.exit(0 if success else 1)

    elif args.command == "drop":
        success = drop_database(args.db, host, port, user, password, confirm=not args.yes)
        sys.exit(0 if success else 1)

    elif args.command == "list":
        dbs = list_databases(host, port, user, password)
        sys.exit(0 if dbs is not None else 1)

    elif args.command == "reset-admin":
        success = reset_admin_password(
            args.db, args.password, args.host,
            args.port, args.user, args.pg_password
        )
        sys.exit(0 if success else 1)

    elif args.command == "modules":
        modules = check_odoo_installed_modules(args.db, host, port, user, password)
        sys.exit(0 if modules is not None else 1)

    elif args.command == "auto-backup":
        backups = auto_backup(args.config, args.output, args.format)
        sys.exit(0 if backups else 1)


if __name__ == "__main__":
    main()
