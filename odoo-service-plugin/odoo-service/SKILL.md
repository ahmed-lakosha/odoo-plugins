---
name: odoo-service
description: "Complete Odoo server lifecycle manager — run, deploy, initialize, and manage Odoo across local venv, Docker, and any IDE. Handles server startup/shutdown, environment initialization, database management, Docker orchestration, and IDE configuration for Odoo 14-19."
version: "1.0.0"
author: "TaqaTechno"
license: "MIT"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  mode: codebase
  odoo-versions: ["14", "15", "16", "17", "18", "19"]
  environments: ["local-venv", "docker", "bare-python"]
  ide-support: ["pycharm", "vscode", "any"]
  categories: [server-management, deployment, database, docker, ide-integration]
---

# Odoo Service Skill

## 1. Overview / Role

The `odoo-service` skill is the complete Odoo server lifecycle manager. It handles every aspect of running, deploying, initializing, and managing Odoo servers across ANY environment and ANY IDE.

### What This Skill Does

- **Server Management**: Start, stop, restart Odoo processes across Windows, Linux, and macOS
- **Environment Detection**: Automatically detects whether you are in a local venv, Docker, or bare Python environment
- **Environment Initialization**: Creates virtual environments, installs dependencies, sets up PostgreSQL, generates config files
- **Database Management**: Backup, restore, create, drop, list databases; reset admin passwords
- **Docker Orchestration**: Generate Dockerfiles, docker-compose files, manage containers, exec into shells
- **IDE Configuration**: Generate PyCharm run configurations and VSCode tasks/launch/settings files
- **Module Management**: Install, update, scaffold Odoo modules from CLI or plugin commands
- **Multi-Project Support**: Manage multiple Odoo projects with different configs, ports, and databases simultaneously

### Supported Odoo Versions

| Version | Status | Python Range | Notes |
|---------|--------|--------------|-------|
| 14 | Supported | 3.7 - 3.10 | LTS, legacy projects |
| 15 | Supported | 3.8 - 3.11 | Community projects |
| 16 | Supported | 3.9 - 3.12 | Active enterprise |
| 17 | Supported | 3.10 - 3.13 | Primary development version |
| 18 | Supported | 3.10 - 3.13 | Active new projects |
| 19 | Supported | 3.10 - 3.13 | Latest features |

### Quick Decision Matrix: Which Environment?

```
Are you deploying to production?
  YES → Docker (isolation, reproducibility, easy scaling)
  NO  →
    Do you have an existing venv/ or .venv/ directory?
      YES → Local venv (keep using it)
      NO  →
        Do you want isolation from system Python?
          YES → Local venv (recommended for dev)
          NO  → Bare Python (simplest, least isolation)
```

---

## 2. Environment Detection Logic

The skill auto-detects the running environment using the following priority order:

### Detection Algorithm

```python
import os
from pathlib import Path

def detect_environment(project_root: str) -> str:
    """
    Detect which Odoo environment is active.
    Returns: 'venv', 'docker', or 'bare'
    Priority: docker > venv > bare
    """
    root = Path(project_root)

    # 1. Check for Docker environment (highest priority)
    if (root / 'docker-compose.yml').exists():
        return 'docker'
    if (root / 'docker-compose.yaml').exists():
        return 'docker'
    if (root / 'Dockerfile').exists():
        return 'docker'

    # 2. Check for virtual environment
    venv_dirs = ['.venv', 'venv', 'env', '.env']
    for venv_dir in venv_dirs:
        venv_path = root / venv_dir
        if venv_path.is_dir():
            # Verify it's actually a venv (has python executable)
            if (venv_path / 'Scripts' / 'python.exe').exists():  # Windows
                return 'venv'
            if (venv_path / 'bin' / 'python').exists():  # Linux/Mac
                return 'venv'

    # 3. Fall back to bare Python
    return 'bare'
```

### Detection Signals

- `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/Mac) → **local-venv**
- `docker-compose.yml` or `docker-compose.yaml` in project root → **docker**
- `Dockerfile` only (no compose) → **docker-build mode**
- None of the above → **bare-python**

### Override Detection

You can force an environment by passing flags:
- `--env venv` — force local venv
- `--env docker` — force Docker
- `--env bare` — force bare Python
- `--docker` — shorthand for `--env docker`

---

## 3. Local Virtual Environment Setup

### Windows Setup (Step-by-Step)

```powershell
# Step 1: Navigate to your Odoo version directory
cd C:\odoo\odoo17

# Step 2: Create virtual environment
python -m venv .venv

# Step 3: Activate
.\.venv\Scripts\activate

# Step 4: Upgrade pip
python -m pip install --upgrade pip

# Step 5: Install core Odoo requirements
pip install -r requirements.txt

# Step 6: Install project-specific requirements (if exists)
pip install -r projects\myproject\requirements.txt

# Step 7: Verify installation
python -c "import odoo; print('Odoo importable')"
```

### Linux / macOS Setup

```bash
# Step 1: Navigate to Odoo directory
cd /opt/odoo17

# Step 2: Create virtual environment with specific Python version
python3.10 -m venv .venv

# Step 3: Activate
source .venv/bin/activate

# Step 4: Upgrade pip
pip install --upgrade pip

# Step 5: Install requirements
pip install -r requirements.txt

# Step 6: Project-specific requirements
pip install -r projects/myproject/requirements.txt

# Step 7: Verify
python -c "import odoo; print('Odoo importable')"
```

### Python Version Requirements Table

| Odoo Version | Min Python | Max Python | Recommended | Notes |
|---|---|---|---|---|
| 14 | 3.7 | 3.10 | 3.8 | EOL versions, be careful with libraries |
| 15 | 3.8 | 3.11 | 3.9 | Stable range |
| 16 | 3.9 | 3.12 | 3.10 | Wider support |
| 17 | 3.10 | 3.13 | 3.11 | Primary dev version |
| 18 | 3.10 | 3.13 | 3.11 | New projects |
| 19 | 3.10 | 3.13 | 3.12 | Latest features |

### Verifying Python Version Compatibility

```python
import sys

def check_python_compatibility(odoo_version: int) -> bool:
    """Check if current Python is compatible with given Odoo version."""
    version_ranges = {
        14: ((3, 7), (3, 10)),
        15: ((3, 8), (3, 11)),
        16: ((3, 9), (3, 12)),
        17: ((3, 10), (3, 13)),
        18: ((3, 10), (3, 13)),
        19: ((3, 10), (3, 13)),
    }

    current = sys.version_info[:2]
    min_ver, max_ver = version_ranges.get(odoo_version, ((3, 10), (3, 13)))

    return min_ver <= current <= max_ver

# Usage
if not check_python_compatibility(17):
    print(f"WARNING: Python {sys.version} may not be compatible with Odoo 17")
```

### Managing Multiple Venvs (Multi-Version Setup)

```bash
# Separate venv per Odoo version
C:\odoo\odoo14\.venv\   # Python 3.8
C:\odoo\odoo15\.venv\   # Python 3.9
C:\odoo\odoo17\.venv\   # Python 3.11
C:\odoo\odoo18\.venv\   # Python 3.11

# Each has its own requirements installed independently
# Never share venvs across Odoo versions
```

---

## 4. Server Startup (Local)

### Basic Startup Commands

```bash
# Basic startup — reads all config from .conf file
python -m odoo -c conf\TAQAT17.conf

# Explicit database override
python -m odoo -c conf\TAQAT17.conf -d taqat17

# Development mode — enables auto-reload, full tracebacks, asset recompilation
python -m odoo -c conf\TAQAT17.conf --dev=all

# Development mode options (can combine):
# --dev=reload    — auto-reload Python on file change
# --dev=qweb      — detailed QWeb error reporting
# --dev=werkzeug  — Werkzeug debugger
# --dev=xml       — show XML errors in browser
# --dev=all       — enable all dev options (recommended)

# With workers (production mode)
python -m odoo -c conf\TAQAT17.conf --workers=4

# Custom port
python -m odoo -c conf\TAQAT17.conf --http-port=8070

# Install module and stop
python -m odoo -c conf\TAQAT17.conf -d taqat17 -i my_module --stop-after-init

# Update module and stop
python -m odoo -c conf\TAQAT17.conf -d taqat17 -u my_module --stop-after-init

# Update ALL modules (slow — use only when necessary)
python -m odoo -c conf\TAQAT17.conf -d taqat17 -u all --stop-after-init
```

### Background Process (Windows)

```powershell
# Method 1: Start-Process (PowerShell)
Start-Process python -ArgumentList "-m odoo -c conf\TAQAT17.conf" -WindowStyle Hidden

# Method 2: Background job
$job = Start-Job -ScriptBlock { python -m odoo -c conf\TAQAT17.conf }
$job.Id  # Save this to stop later

# Method 3: With log file
Start-Process python -ArgumentList "-m odoo -c conf\TAQAT17.conf" -WindowStyle Hidden -RedirectStandardOutput "logs\odoo.log" -RedirectStandardError "logs\odoo_err.log"

# Method 4: Windows service (nssm recommended for production)
nssm install OdooService "python" "-m odoo -c C:\odoo\odoo17\conf\TAQAT17.conf"
nssm start OdooService
```

### Background Process (Linux/Mac)

```bash
# Method 1: nohup (survives terminal close)
nohup python -m odoo -c conf/TAQAT17.conf > logs/odoo.log 2>&1 &
echo $! > logs/odoo.pid   # Save PID for later

# Method 2: screen session
screen -dmS odoo python -m odoo -c conf/TAQAT17.conf

# Method 3: tmux session
tmux new-session -d -s odoo "python -m odoo -c conf/TAQAT17.conf"

# Method 4: systemd service (production)
# Create /etc/systemd/system/odoo17.service:
[Unit]
Description=Odoo 17 Server
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
WorkingDirectory=/opt/odoo17
ExecStart=/opt/odoo17/.venv/bin/python -m odoo -c conf/TAQAT17.conf
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
systemctl enable odoo17
systemctl start odoo17
systemctl status odoo17
```

### Startup Sequence Verification

```bash
# After starting, verify Odoo is running:
# 1. Check port is listening
netstat -ano | findstr :8069          # Windows
lsof -i :8069                         # Linux/Mac

# 2. Check HTTP response
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login
# Expected: 200

# 3. Check process
tasklist | findstr python              # Windows
ps aux | grep odoo                     # Linux/Mac
```

---

## 5. Server Shutdown / Port Management

### Windows: Kill by Port

```powershell
# Method 1: netstat + taskkill (CMD)
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F

# Method 2: PowerShell (more reliable)
$port = 8069
$process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $process.OwningProcess -Force
    Write-Host "Killed process on port $port"
} else {
    Write-Host "No process found on port $port"
}

# Method 3: Kill all Python processes (nuclear option)
taskkill /IM python.exe /F

# Kill both Odoo ports (web + longpolling)
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8072') DO taskkill /PID %P /F
```

### Linux / macOS: Kill by Port

```bash
# Method 1: lsof + kill
lsof -ti:8069 | xargs kill -9

# Method 2: fuser
fuser -k 8069/tcp

# Method 3: pkill for Odoo specifically
pkill -f "odoo.*8069"

# Kill both ports
lsof -ti:8069 | xargs kill -9
lsof -ti:8072 | xargs kill -9

# Verify port is free
lsof -i :8069   # Should return nothing
```

### Find and Inspect Running Processes

```powershell
# Windows: Find Odoo-related Python processes
Get-Process python | Where-Object {$_.CommandLine -like "*odoo*"}

# Windows: Detailed process with ports
netstat -ano | findstr :8069

# Linux/Mac: Inspect what's on port 8069
lsof -i :8069
ss -tlnp | grep 8069
```

### Graceful vs Force Stop

```python
import subprocess
import signal
import os

def stop_graceful(pid: int, timeout: int = 10):
    """Try SIGTERM first, then SIGKILL after timeout."""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/PID', str(pid), '/F'])
        else:  # Linux/Mac
            os.kill(pid, signal.SIGTERM)
            import time
            time.sleep(timeout)
            try:
                os.kill(pid, 0)  # Check if still alive
                os.kill(pid, signal.SIGKILL)  # Force kill
            except ProcessLookupError:
                pass  # Already dead, good
    except Exception as e:
        print(f"Error stopping process {pid}: {e}")
```

---

## 6. Configuration File Reference (.conf)

### Complete Annotated Configuration

```ini
[options]
# ==========================================================
# ADDON PATHS
# ==========================================================
# Comma-separated list of directories containing Odoo modules
# Order matters: modules found first take precedence
addons_path = odoo\addons,projects\myproject

# ==========================================================
# SECURITY
# ==========================================================
# Master password for the database manager UI
# Set to a strong password in production
admin_passwd = CHANGE_ME_IN_PRODUCTION

# ==========================================================
# DATABASE CONNECTION
# ==========================================================
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo

# Database name (optional — can be specified at startup with -d)
# db_name = myproject17

# Database filter (regex pattern — only show matching databases)
# Multi-tenant: each project has its own prefix
dbfilter = myproject17.*

# Max database connections per worker
db_maxconn = 64

# ==========================================================
# NETWORK PORTS
# ==========================================================
# Main web interface port
http_port = 8069

# Longpolling port (chat, notifications, buses)
# Called gevent_port in v17+, longpolling_port in v14-16
gevent_port = 8072
# longpolling_port = 8072   # Use this for Odoo 14-16

# Interface to bind (0.0.0.0 = all, 127.0.0.1 = localhost only)
# http_interface = 0.0.0.0

# ==========================================================
# WORKER PROCESSES
# ==========================================================
# Number of worker processes
# 0 = single-threaded (development)
# >0 = multi-worker (production, requires --workers flag)
# Rule of thumb: 2 * CPU_CORES + 1
workers = 0

# Cron workers (background tasks)
max_cron_threads = 2

# ==========================================================
# MEMORY LIMITS (bytes)
# ==========================================================
# Soft limit: worker restarts after processing current request
limit_memory_soft = 2147483648   # 2 GB

# Hard limit: worker killed immediately
limit_memory_hard = 2684354560   # 2.5 GB

# ==========================================================
# TIME LIMITS (seconds)
# ==========================================================
# CPU time per request
limit_time_cpu = 600

# Real (wall clock) time per request
limit_time_real = 1200

# Time per cron task
limit_time_real_cron = 1800

# ==========================================================
# PROXY / PRODUCTION
# ==========================================================
# Set True when behind nginx/Apache reverse proxy
# Required for correct IP forwarding and SSL headers
proxy_mode = False

# ==========================================================
# LOGGING
# ==========================================================
# Log output file (omit or leave empty for console output)
logfile = logs\odoo.log

# Log level: debug, info, warning, error, critical
log_level = info

# Log handler format
# log_handler = :INFO

# ==========================================================
# DATA DIRECTORY
# ==========================================================
# Where Odoo stores file attachments, sessions, etc.
data_dir = data

# ==========================================================
# EMAIL (optional)
# ==========================================================
# smtp_server = localhost
# smtp_port = 25
# smtp_ssl = False
# smtp_user = False
# smtp_password = False

# ==========================================================
# REPORT RENDERING
# ==========================================================
# Path to wkhtmltopdf for PDF reports
# wkhtmltopdf_command = wkhtmltopdf   # Auto-detected if in PATH
```

### Config Templates by Environment

```ini
# --- DEVELOPMENT CONFIG ---
[options]
addons_path = odoo\addons,projects\myproject
admin_passwd = 123
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = myproject17_dev
http_port = 8069
gevent_port = 8072
workers = 0
log_level = debug

# --- PRODUCTION CONFIG ---
[options]
addons_path = odoo\addons,projects\myproject
admin_passwd = STRONG_RANDOM_PASSWORD_HERE
db_host = localhost
db_port = 5432
db_user = odoo
db_password = STRONG_DB_PASSWORD
dbfilter = myproject17_prod
http_port = 8069
gevent_port = 8072
workers = 4
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_time_cpu = 600
limit_time_real = 1200
proxy_mode = True
logfile = logs\odoo_prod.log
log_level = warning
data_dir = data_prod
```

---

## 7. Module Operations

### Install, Update, Scaffold

```bash
# ----------------------------------------
# INSTALL (new module, first time)
# ----------------------------------------
python -m odoo -c conf\TAQAT17.conf -d taqat17 -i my_module --stop-after-init

# Install multiple modules
python -m odoo -c conf\TAQAT17.conf -d taqat17 -i module1,module2,module3 --stop-after-init

# ----------------------------------------
# UPDATE (after code changes — most common)
# ----------------------------------------
python -m odoo -c conf\TAQAT17.conf -d taqat17 -u my_module --stop-after-init

# Update multiple modules
python -m odoo -c conf\TAQAT17.conf -d taqat17 -u module1,module2 --stop-after-init

# Update ALL modules (slow, use sparingly)
python -m odoo -c conf\TAQAT17.conf -d taqat17 -u all --stop-after-init

# ----------------------------------------
# REFRESH MODULE LIST
# ----------------------------------------
# Run before installing a NEW module that wasn't there before
python -m odoo -c conf\TAQAT17.conf -d taqat17 --update-list

# ----------------------------------------
# SCAFFOLD NEW MODULE
# ----------------------------------------
python odoo-bin scaffold my_new_module projects\myproject\
# Creates: projects/myproject/my_new_module/ with standard structure
```

### Module Management in Docker

```bash
# Update module inside Docker container
docker-compose exec odoo python -m odoo \
    -c /etc/odoo/odoo.conf \
    -d mydb \
    -u my_module \
    --stop-after-init

# Install module inside Docker container
docker-compose exec odoo python -m odoo \
    -c /etc/odoo/odoo.conf \
    -d mydb \
    -i my_module \
    --stop-after-init

# Scaffold inside Docker
docker-compose exec odoo python /opt/odoo/source/odoo-bin scaffold my_module /opt/odoo/custom-addons/
```

### Check Installed Modules

```bash
# Via Odoo shell
python odoo-bin shell -d mydb
>>> installed = self.env['ir.module.module'].search([('state', '=', 'installed')])
>>> print(installed.mapped('name'))

# Via psql directly
psql -U odoo -d mydb -c "SELECT name, state FROM ir_module_module WHERE state='installed' ORDER BY name;"
```

---

## 8. Database Operations

### Backup and Restore

```bash
# ----------------------------------------
# BACKUP
# ----------------------------------------
# SQL format (human-readable, larger file)
pg_dump -U odoo -h localhost mydb > backups/mydb_$(date +%Y%m%d_%H%M%S).sql

# Custom format (compressed, faster restore)
pg_dump -U odoo -h localhost -Fc mydb > backups/mydb_$(date +%Y%m%d_%H%M%S).dump

# Directory format (parallel dump — fastest for large DBs)
pg_dump -U odoo -h localhost -Fd mydb -j 4 -f backups/mydb_dir/

# ----------------------------------------
# RESTORE
# ----------------------------------------
# From SQL file
createdb -U odoo new_mydb
psql -U odoo -d new_mydb < backups/mydb_20240101.sql

# From custom dump
createdb -U odoo new_mydb
pg_restore -U odoo -d new_mydb backups/mydb_20240101.dump

# From directory format
createdb -U odoo new_mydb
pg_restore -U odoo -d new_mydb -j 4 backups/mydb_dir/

# ----------------------------------------
# MANAGE
# ----------------------------------------
# Create database
createdb -U odoo newproject17

# Drop database (DANGER: irreversible)
dropdb -U odoo oldproject

# List all databases
psql -U odoo -l

# Connect interactively
psql -U odoo -h localhost -d mydb
```

### Reset Admin Password

```bash
# Method 1: SQL UPDATE (fastest)
psql -U odoo -h localhost -d mydb -c \
    "UPDATE res_users SET password='\$pbkdf2-sha512\$...' WHERE login='admin';"

# Better: Use Odoo's password hashing
psql -U odoo -h localhost -d mydb -c \
    "UPDATE res_users SET password='newpassword' WHERE login='admin';"
# Note: Odoo hashes on next login attempt; for immediate hash use shell method

# Method 2: Odoo shell (recommended)
python odoo-bin shell -d mydb
>>> user = self.env['res.users'].search([('login', '=', 'admin')])
>>> user.write({'password': 'newpassword'})
>>> self.env.cr.commit()
```

### Interactive Shell Usage

```python
# Start shell
python odoo-bin shell -d mydb

# ---- COMMON SHELL OPERATIONS ----

# List all partners
env['res.partner'].search([], limit=10)

# Find specific record
env['res.partner'].search([('name', 'like', 'TAQAT')])

# Current user
env.user.name
env.user.id

# Raw SQL
env.cr.execute("SELECT id, name FROM res_partner LIMIT 5")
env.cr.fetchall()

# System parameters
env['ir.config_parameter'].sudo().get_param('web.base.url')
env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://mysite.com')

# List installed modules
env['ir.module.module'].search([('state', '=', 'installed')]).mapped('name')

# Commit changes (required for writes)
env.cr.commit()
```

---

## 9. Docker Environment

### Complete docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: odoo_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-odoo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-odoo}
      POSTGRES_DB: postgres
    volumes:
      - odoo_db_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-odoo}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s
    restart: unless-stopped

  odoo:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: odoo_web
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/opt/odoo/source:ro
      - ./projects:/opt/odoo/custom-addons
      - ./conf:/etc/odoo:ro
      - odoo_filestore:/var/lib/odoo
      - ./logs:/var/log/odoo
    ports:
      - "${ODOO_HTTP_PORT:-8069}:8069"
      - "${ODOO_LONGPOLLING_PORT:-8072}:8072"
    environment:
      POSTGRES_HOST: db
      POSTGRES_PORT: 5432
      POSTGRES_USER: ${POSTGRES_USER:-odoo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-odoo}
    restart: unless-stopped
    command: odoo -c /etc/odoo/odoo.conf

volumes:
  odoo_db_data:
  odoo_filestore:
```

### Docker Management Commands

```bash
# ---- BUILD ----
docker-compose build
docker-compose build --no-cache   # Force full rebuild

# ---- START / STOP ----
docker-compose up -d              # Start in background
docker-compose up                  # Start in foreground (see logs)
docker-compose start               # Start existing containers
docker-compose stop                # Stop containers (preserves state)
docker-compose down                # Stop and remove containers
docker-compose down -v             # Also remove volumes (DANGER: deletes data)
docker-compose restart             # Restart all
docker-compose restart odoo        # Restart only Odoo service

# ---- REBUILD AFTER CHANGES ----
docker-compose up -d --build       # Rebuild and restart

# ---- LOGS ----
docker-compose logs -f             # Follow all logs
docker-compose logs -f odoo        # Follow only Odoo logs
docker-compose logs --tail=100 odoo

# ---- SHELL ACCESS ----
docker-compose exec odoo bash      # Bash shell in Odoo container
docker-compose exec db psql -U odoo  # PostgreSQL in DB container

# ---- ODOO COMMANDS IN CONTAINER ----
docker-compose exec odoo python -m odoo -c /etc/odoo/odoo.conf -d mydb -u my_module --stop-after-init
docker-compose exec odoo python -m odoo shell -d mydb -c /etc/odoo/odoo.conf

# ---- STATUS ----
docker-compose ps
docker-compose top

# ---- DATABASE IN DOCKER ----
# Backup
docker exec odoo_db pg_dump -U odoo mydb > backup.sql
docker exec odoo_db pg_dump -U odoo -Fc mydb > backup.dump

# Restore
cat backup.sql | docker exec -i odoo_db psql -U odoo mydb
docker exec -i odoo_db pg_restore -U odoo -d mydb < backup.dump
```

---

## 10. Dockerfile Reference (Per Odoo Version)

### Odoo 14 Dockerfile

```dockerfile
FROM python:3.8-slim-buster

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    node-less \
    npm \
    git \
    postgresql-client \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf for PDF reports
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.buster_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-3.buster_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.buster_amd64.deb

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
```

### Odoo 17 Dockerfile (Primary)

```dockerfile
FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libffi-dev \
    liblzma-dev \
    npm \
    git \
    postgresql-client \
    wget \
    curl \
    gettext-base \
    fonts-noto-cjk \
    fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf for PDF reports (Odoo 17 uses bookworm)
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

# Install rtlcss for RTL/Arabic support
RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install GeoIP2 for geolocation features
RUN pip install geoip2

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
```

### Odoo 18 Dockerfile

```dockerfile
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libffi-dev \
    npm \
    git \
    postgresql-client \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install cbor2

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
```

### Odoo 19 Dockerfile

```dockerfile
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libffi-dev \
    libmagic1 \
    npm \
    git \
    postgresql-client \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install cbor2 python-magic

RUN mkdir -p /var/lib/odoo /var/log/odoo /etc/odoo
EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
```

---

## 11. PyCharm Configuration

### Local Python Run Configuration (XML)

Save to `.idea/runConfigurations/Odoo_[PROJECT].xml`:

```xml
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Odoo 17 [PROJECT]" type="PythonConfigurationType"
                 factoryName="Python">
    <module name="[PROJECT_NAME]" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <option name="SDK_HOME" value="$PROJECT_DIR$/.venv/Scripts/python.exe" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="IS_MODULE_SDK" value="false" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <EXTENSION ID="PythonCoverageRunConfigurationExtension" runner="coverage.py" />
    <option name="SCRIPT_NAME" value="$PROJECT_DIR$/odoo-bin" />
    <option name="PARAMETERS" value="-c conf/[CONFIG].conf" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="true" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>
```

### Docker Compose Run Configuration (XML)

Save to `.idea/runConfigurations/Odoo_Docker.xml`:

```xml
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Odoo [VERSION] Docker" type="docker-deploy"
                 factoryName="docker-compose.yml" server-name="Docker">
    <deployment type="docker-compose.yml">
      <settings>
        <option name="envFilePath" value="$PROJECT_DIR$/.env" />
        <option name="composeFilePaths">
          <list>
            <option value="$PROJECT_DIR$/docker-compose.yml" />
          </list>
        </option>
        <option name="sourceFilePath" value="docker-compose.yml" />
      </settings>
    </deployment>
    <method v="2" />
  </configuration>
</component>
```

### PyCharm Settings (idea.properties / .idea/misc.xml)

```xml
<!-- .idea/misc.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="Black">
    <option name="sdkName" value="Python 3.11 (.venv)" />
  </component>
  <component name="JavaScriptSettings">
    <option name="languageLevel" value="ES6" />
  </component>
  <component name="PythonProjectView">
    <option name="showLibraryContents" value="false" />
  </component>
</project>
```

---

## 12. VSCode Configuration

### tasks.json (Local + Docker)

Save to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Odoo: Start (dev mode)",
      "type": "shell",
      "command": "python -m odoo -c conf/${input:configFile} --dev=all",
      "group": {"kind": "build", "isDefault": true},
      "presentation": {
        "reveal": "always",
        "panel": "new",
        "showReuseMessage": false
      },
      "problemMatcher": []
    },
    {
      "label": "Odoo: Start (production mode)",
      "type": "shell",
      "command": "python -m odoo -c conf/${input:configFile} --workers=4",
      "group": "build",
      "presentation": {"reveal": "always", "panel": "new"}
    },
    {
      "label": "Odoo: Stop (kill port 8069)",
      "type": "shell",
      "command": "FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F",
      "windows": {
        "command": "FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F"
      },
      "linux": {"command": "lsof -ti:8069 | xargs kill -9"},
      "osx": {"command": "lsof -ti:8069 | xargs kill -9"},
      "presentation": {"reveal": "always"}
    },
    {
      "label": "Odoo: Update Module",
      "type": "shell",
      "command": "python -m odoo -c conf/${input:configFile} -d ${input:database} -u ${input:moduleName} --stop-after-init",
      "presentation": {"reveal": "always", "panel": "shared"}
    },
    {
      "label": "Odoo: Install Module",
      "type": "shell",
      "command": "python -m odoo -c conf/${input:configFile} -d ${input:database} -i ${input:moduleName} --stop-after-init",
      "presentation": {"reveal": "always"}
    },
    {
      "label": "Docker: Start",
      "type": "shell",
      "command": "docker-compose up -d",
      "group": "build",
      "presentation": {"reveal": "always"}
    },
    {
      "label": "Docker: Stop",
      "type": "shell",
      "command": "docker-compose down",
      "presentation": {"reveal": "always"}
    },
    {
      "label": "Docker: Rebuild",
      "type": "shell",
      "command": "docker-compose up -d --build",
      "presentation": {"reveal": "always", "panel": "new"}
    },
    {
      "label": "Docker: Logs",
      "type": "shell",
      "command": "docker-compose logs -f odoo",
      "presentation": {"reveal": "always", "panel": "shared"}
    },
    {
      "label": "Docker: Shell",
      "type": "shell",
      "command": "docker-compose exec odoo bash",
      "presentation": {"reveal": "always", "panel": "new"}
    },
    {
      "label": "Docker: Update Module",
      "type": "shell",
      "command": "docker-compose exec odoo python -m odoo -c /etc/odoo/odoo.conf -d ${input:database} -u ${input:moduleName} --stop-after-init",
      "presentation": {"reveal": "always"}
    }
  ],
  "inputs": [
    {
      "id": "configFile",
      "type": "promptString",
      "description": "Config file name (e.g. TAQAT17.conf)",
      "default": "odoo.conf"
    },
    {
      "id": "database",
      "type": "promptString",
      "description": "Database name",
      "default": "myproject17"
    },
    {
      "id": "moduleName",
      "type": "promptString",
      "description": "Module name(s) to install/update",
      "default": "my_module"
    }
  ]
}
```

### launch.json (Debugging)

Save to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Odoo: Debug (Local)",
      "type": "debugpy",
      "request": "launch",
      "module": "odoo",
      "args": ["-c", "conf/${input:configFile}", "--dev=all"],
      "cwd": "${workspaceFolder}",
      "python": "${workspaceFolder}/.venv/Scripts/python.exe",
      "justMyCode": false,
      "console": "integratedTerminal",
      "env": {
        "PYTHONDONTWRITEBYTECODE": "1"
      }
    },
    {
      "name": "Odoo: Debug (Docker attach)",
      "type": "debugpy",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}",
          "remoteRoot": "/opt/odoo/source"
        }
      ]
    },
    {
      "name": "Odoo: Debug with DB override",
      "type": "debugpy",
      "request": "launch",
      "module": "odoo",
      "args": [
        "-c", "conf/${input:configFile}",
        "-d", "${input:database}",
        "--dev=all"
      ],
      "cwd": "${workspaceFolder}",
      "python": "${workspaceFolder}/.venv/Scripts/python.exe",
      "justMyCode": false,
      "console": "integratedTerminal"
    }
  ],
  "inputs": [
    {
      "id": "configFile",
      "type": "promptString",
      "description": "Config file name",
      "default": "odoo.conf"
    },
    {
      "id": "database",
      "type": "promptString",
      "description": "Database name",
      "default": "myproject17"
    }
  ]
}
```

### settings.json (Workspace)

Save to `.vscode/settings.json`:

```json
{
  "python.analysis.extraPaths": [
    "./odoo",
    "./odoo/addons",
    "./projects"
  ],
  "python.languageServer": "Pylance",
  "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,

  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/*.pyo": true,
    "odoo.egg-info": true
  },
  "search.exclude": {
    "odoo.egg-info": true,
    "**/__pycache__": true,
    ".venv": true,
    "**/*.pyc": true
  },
  "editor.rulers": [79, 120],
  "editor.formatOnSave": false,
  "files.associations": {
    "*.xml": "xml",
    "*.conf": "ini",
    "*.po": "po"
  },
  "xml.validation.enabled": false,
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "[python]": {
    "editor.tabSize": 4
  },
  "[xml]": {
    "editor.tabSize": 4
  }
}
```

---

## 13. Multi-Project / Multi-Tenant Setup

### Port Allocation Strategy

```ini
# Project A — Port 8069 (default)
http_port = 8069
gevent_port = 8072
dbfilter = projecta17.*

# Project B — Port 8070
http_port = 8070
gevent_port = 8073
dbfilter = projectb17.*

# Project C — Port 8071
http_port = 8071
gevent_port = 8074
dbfilter = projectc17.*
```

### Nginx Reverse Proxy (Domain Routing)

```nginx
# /etc/nginx/sites-available/projecta.conf
server {
    listen 80;
    server_name projecta.example.com;

    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /longpolling {
        proxy_pass http://127.0.0.1:8072;
        proxy_set_header Host $host;
    }
}

# /etc/nginx/sites-available/projectb.conf
server {
    listen 80;
    server_name projectb.example.com;

    location / {
        proxy_pass http://127.0.0.1:8070;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /longpolling {
        proxy_pass http://127.0.0.1:8073;
        proxy_set_header Host $host;
    }
}
```

### Running Multiple Instances Simultaneously

```bash
# Terminal 1 — Project A
.\.venv\Scripts\activate
python -m odoo -c conf\projecta17.conf

# Terminal 2 — Project B
.\.venv\Scripts\activate
python -m odoo -c conf\projectb17.conf

# Background both (Windows PowerShell)
Start-Process python -ArgumentList "-m odoo -c conf\projecta17.conf" -WindowStyle Hidden
Start-Process python -ArgumentList "-m odoo -c conf\projectb17.conf" -WindowStyle Hidden
```

---

## 14. Production Checklist

Before going live, verify each item:

```
SECURITY
[ ] admin_passwd set to strong, unique password (not '123' or 'admin')
[ ] db_password set to strong password
[ ] PostgreSQL user has limited privileges (not superuser)
[ ] Firewall: only ports 80/443 exposed to internet
[ ] SSH key-based authentication (no password login)
[ ] SSL/TLS certificate installed (Let's Encrypt via certbot)

SERVER CONFIGURATION
[ ] proxy_mode = True (if behind nginx/Apache)
[ ] workers = 4 (or more based on CPU: 2*CPU+1)
[ ] max_cron_threads = 2 (or 1 for smaller servers)
[ ] limit_memory_soft / limit_memory_hard configured
[ ] limit_time_cpu / limit_time_real configured
[ ] logfile set and log rotation configured
[ ] data_dir set and backed up

DATABASE
[ ] dbfilter set to restrict accessible databases
[ ] Automated backup schedule configured
[ ] Backup tested (actually restore to verify)
[ ] PostgreSQL pg_hba.conf restricts remote access

INFRASTRUCTURE
[ ] Regular server snapshots configured
[ ] Monitoring configured (uptime, CPU, memory)
[ ] Alert on server down / high memory
[ ] wkhtmltopdf installed for PDF reports
[ ] rtlcss installed if using Arabic/RTL

ODOO SPECIFIC
[ ] website.base.url system parameter set correctly
[ ] Email (SMTP) configured and tested
[ ] CDN configured if using attachments
[ ] Session timeout configured appropriately
```

---

## 15. Troubleshooting Guide

### Common Error Reference

| Problem | Likely Cause | Solution |
|---------|-------------|---------|
| `Address already in use: 8069` | Previous Odoo still running | `lsof -ti:8069 \| xargs kill -9` or Windows: find/kill PID |
| `could not connect to server: Connection refused` | PostgreSQL not running | Start PostgreSQL: `net start postgresql` (Win) or `systemctl start postgresql` |
| `ImportError: No module named X` | Missing Python package | `pip install X` or `pip install -r requirements.txt` |
| Module not appearing in apps list | Module path not in addons_path | Add path to .conf, run `--update-list` |
| `Access Denied` on module install | Wrong admin_passwd | Check `admin_passwd` in .conf matches what you typed |
| Docker health check failing | PostgreSQL container not ready | Increase `start_period` in healthcheck config |
| `wkhtmltopdf` not found (PDF fails) | wkhtmltopdf not installed/PATH | Install via apt/choco, add to PATH |
| Longpolling not working | Port 8072 blocked or `workers=0` | Set `workers > 0` for longpolling |
| Dev mode not auto-reloading | Only using `--dev=reload` | Use `--dev=all` for full dev mode |
| `database "X" does not exist` | Database not created yet | `createdb -U odoo X` |
| `FATAL: role "odoo" does not exist` | PostgreSQL user not created | `createuser -s odoo` |
| Changes not reflecting after update | Browser cache | Hard refresh: Ctrl+Shift+R |
| XML view error (blank page) | Malformed XML | Check XML syntax, look at server logs |
| `KeyError: 'field_name'` in view | Field not in model | Check field exists in Python model |
| Slow startup | Too many modules | Check `-i` / `-u` flags, use `--stop-after-init` |

### Diagnostic Commands

```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432

# Check Odoo port
netstat -ano | findstr :8069        # Windows
lsof -i :8069                        # Linux/Mac

# Check Odoo logs (last 50 lines)
Get-Content logs\odoo.log -Tail 50  # PowerShell
tail -50 logs/odoo.log               # Linux/Mac

# Check Python version
python --version

# Check installed packages
pip list | findstr odoo              # Windows
pip list | grep odoo                 # Linux/Mac

# Test PostgreSQL connection
psql -U odoo -h localhost -c "SELECT 1"

# Docker diagnostics
docker-compose ps
docker-compose logs --tail=50 odoo
docker inspect odoo_web | grep -A 5 "Health"
```

---

## 16. Interactive Shell Usage

### Starting the Shell

```bash
# Local
python odoo-bin shell -d mydatabase

# Docker
docker-compose exec odoo python -m odoo shell -d mydatabase -c /etc/odoo/odoo.conf

# With specific config
python odoo-bin shell -d mydatabase -c conf/TAQAT17.conf
```

### Common Shell Operations

```python
# ---- PARTNERS ----
# List all partners
env['res.partner'].search([], limit=10)

# Search by name
env['res.partner'].search([('name', 'ilike', 'company')])

# Create partner
p = env['res.partner'].create({'name': 'Test Company', 'is_company': True})
env.cr.commit()

# ---- USERS ----
env.user.name        # Current user name
env.user.id          # Current user ID
env.user.groups_id   # User's groups

# Find admin user
admin = env['res.users'].browse(2)
admin.login

# ---- MODULES ----
# List installed modules
env['ir.module.module'].search([('state', '=', 'installed')]).mapped('name')

# Find specific module
env['ir.module.module'].search([('name', '=', 'sale')])[0].state

# ---- SYSTEM PARAMS ----
env['ir.config_parameter'].sudo().get_param('web.base.url')
env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://mysite.com')
env.cr.commit()

# ---- RAW SQL ----
env.cr.execute("SELECT id, name, state FROM ir_module_module WHERE state='installed' LIMIT 10")
rows = env.cr.fetchall()
for row in rows:
    print(row)

# ---- COMMIT CHANGES ----
env.cr.commit()   # Always commit after writes!

# ---- ROLLBACK ----
env.cr.rollback()  # Undo uncommitted changes
```

---

## 17. Environment Variables (.env)

### Docker .env File

```bash
# .env (for docker-compose)
# Copy from .env.example and customize

# PostgreSQL settings
POSTGRES_USER=odoo
POSTGRES_PASSWORD=change_me_in_production
POSTGRES_DB=postgres

# Odoo ports
ODOO_HTTP_PORT=8069
ODOO_LONGPOLLING_PORT=8072

# Development mode (set to 'all' for dev, empty for prod)
DEV_MODE=all

# Build settings
ODOO_VERSION=17

# Optional: custom config file
ODOO_CONFIG=/etc/odoo/odoo.conf
```

### Local Development .env File

```bash
# .env.local (for local dev, load with dotenv or manually)
ODOO_CONFIG=conf/myproject17.conf
ODOO_DATABASE=myproject17
ODOO_PORT=8069
ODOO_LONGPOLLING_PORT=8072
PGUSER=odoo
PGPASSWORD=odoo
PGHOST=localhost
PGPORT=5432
```

### Using .env in PowerShell

```powershell
# Load .env file in PowerShell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}

# Or use dotenv package
pip install python-dotenv
```

---

## 18. Available Commands Reference

### Command Overview Table

| Command | Description | Environment |
|---------|-------------|-------------|
| `/odoo-service` | Main help and status | Any |
| `/odoo-start` | Start Odoo server (auto-detects env) | Local / Docker |
| `/odoo-stop` | Stop Odoo server / containers | Local / Docker |
| `/odoo-init` | Initialize new Odoo environment | Local / Docker |
| `/odoo-db` | Database operations (backup, restore, create, drop) | Local / Docker |
| `/odoo-docker` | Docker management (build, up, down, logs, shell) | Docker |
| `/odoo-ide` | Generate PyCharm/VSCode configurations | Any |

### Quick Start Examples

```bash
# --- LOCAL VENV WORKFLOW ---

# 1. Initialize new project
/odoo-init --version 17 --project myproject --port 8069

# 2. Start in dev mode
/odoo-start --config myproject17.conf --dev

# 3. Update a module
python -m odoo -c conf/myproject17.conf -d myproject17 -u my_module --stop-after-init

# 4. Stop server
/odoo-stop

# 5. Backup database
/odoo-db backup --db myproject17

# --- DOCKER WORKFLOW ---

# 1. Initialize Docker project
/odoo-init --docker --version 17 --project myproject

# 2. Build and start
/odoo-docker up

# 3. View logs
/odoo-docker logs

# 4. Open shell
/odoo-docker shell

# 5. Update module
/odoo-docker update --db mydb --module my_module

# 6. Backup database
/odoo-db backup --docker odoo_db --db mydb

# 7. Stop
/odoo-docker down
```

---

## 19. Odoo Version-Specific Notes

### Odoo 14 Specifics

```bash
# Use longpolling_port (not gevent_port)
longpolling_port = 8072

# Python must be 3.7-3.10 (3.8 recommended)
# node.js + npm required for JS assets
npm install -g less less-plugin-clean-css

# Worker restart is via SIGHUP on Linux
kill -HUP $(cat logs/odoo.pid)
```

### Odoo 17 Specifics

```bash
# gevent_port is the correct name (not longpolling_port)
gevent_port = 8072

# rtlcss required for Arabic/RTL language support
npm install -g rtlcss

# Assets are compiled differently (OWL 2.x)
# Use --dev=all for asset recompilation

# New: ORM caching improvements
# New: WhatsApp integration support
```

### Odoo 18-19 Specifics

```bash
# cbor2 package required
pip install cbor2

# Odoo 19: libmagic1 required
apt-get install libmagic1
pip install python-magic

# New REST API framework in v17+
# New: spreadsheet integration
# PostgreSQL 15+ recommended for v18/19
```

---

## 20. Script Usage Reference

### server_manager.py

```bash
# Start Odoo
python odoo-service/scripts/server_manager.py start --config conf/TAQAT17.conf --dev

# Stop Odoo
python odoo-service/scripts/server_manager.py stop --port 8069

# Check status
python odoo-service/scripts/server_manager.py status

# Restart
python odoo-service/scripts/server_manager.py restart --config conf/TAQAT17.conf

# Install module
python odoo-service/scripts/server_manager.py install --config conf/TAQAT17.conf --db taqat17 --module my_module

# Update module
python odoo-service/scripts/server_manager.py update --config conf/TAQAT17.conf --db taqat17 --module my_module
```

### env_initializer.py

```bash
# Initialize complete environment
python odoo-service/scripts/env_initializer.py init --version 17 --project myproject --port 8069

# Just create venv
python odoo-service/scripts/env_initializer.py venv --python python3.11

# Check environment
python odoo-service/scripts/env_initializer.py check

# Generate config file only
python odoo-service/scripts/env_initializer.py conf --project myproject --version 17 --db mydb
```

### db_manager.py

```bash
# Backup database
python odoo-service/scripts/db_manager.py backup --db myproject17 --output backups/

# Restore from dump
python odoo-service/scripts/db_manager.py restore --file backups/backup.dump --db restored_db

# Create database
python odoo-service/scripts/db_manager.py create --db newproject17

# Drop database
python odoo-service/scripts/db_manager.py drop --db oldproject

# List databases
python odoo-service/scripts/db_manager.py list

# Reset admin password
python odoo-service/scripts/db_manager.py reset-admin --db myproject17 --password newpass
```

### docker_manager.py

```bash
# Generate Docker files
python odoo-service/scripts/docker_manager.py init --version 17 --project myproject

# Build image
python odoo-service/scripts/docker_manager.py build

# Start containers
python odoo-service/scripts/docker_manager.py up

# Stop containers
python odoo-service/scripts/docker_manager.py down

# Follow logs
python odoo-service/scripts/docker_manager.py logs

# Open shell
python odoo-service/scripts/docker_manager.py shell

# Check status
python odoo-service/scripts/docker_manager.py status
```

### ide_configurator.py

```bash
# Generate VSCode config (local env)
python odoo-service/scripts/ide_configurator.py --ide vscode --env local --config TAQAT17.conf

# Generate PyCharm config (Docker)
python odoo-service/scripts/ide_configurator.py --ide pycharm --env docker --project myproject

# Generate both IDE configs
python odoo-service/scripts/ide_configurator.py --ide both --env docker --project myproject

# Generate .gitignore
python odoo-service/scripts/ide_configurator.py --gitignore-only
```

---

*This skill covers Odoo 14-19 server lifecycle management across all environments. For project-specific patterns, refer to version-specific CLAUDE.md files.*
