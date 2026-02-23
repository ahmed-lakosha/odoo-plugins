# Odoo Environment Patterns

Complete reference for setting up and managing Odoo environments across Windows, Linux, and macOS. Covers virtual environments, Docker, bare Python, nginx, and all supporting infrastructure.

---

## 1. Virtual Environment Setup

### Windows (PowerShell / CMD)

```powershell
# Navigate to Odoo version directory
cd C:\odoo\odoo17

# Create venv using system Python
python -m venv .venv

# Activate
.\.venv\Scripts\activate

# Verify activation (should show .venv path)
where python

# Upgrade pip
python -m pip install --upgrade pip

# Install Odoo requirements
pip install -r requirements.txt

# Install project requirements
pip install -r projects\myproject\requirements.txt

# Deactivate when done
deactivate
```

### Linux / macOS

```bash
# Navigate to Odoo directory
cd /opt/odoo17

# Create venv with specific Python version
python3.10 -m venv .venv
# or
python3.11 -m venv .venv

# Activate
source .venv/bin/activate

# Verify
which python  # Should show .venv/bin/python

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
pip install -r projects/myproject/requirements.txt

# Deactivate
deactivate
```

### Verify Venv is Active

```python
import sys
print(sys.prefix)  # Should show path to .venv
print(sys.executable)  # Should show .venv/Scripts/python or .venv/bin/python
```

---

## 2. Python Version Compatibility Matrix

| Odoo Version | Min Python | Max Python | Recommended | EOL Notes |
|---|---|---|---|---|
| 14.0 | 3.7 | 3.10 | 3.8 | Python 3.7 EOL June 2023 |
| 15.0 | 3.8 | 3.11 | 3.9 | Python 3.8 EOL Oct 2024 |
| 16.0 | 3.9 | 3.12 | 3.10 | Stable range |
| 17.0 | 3.10 | 3.13 | 3.11 | PRIMARY version |
| 18.0 | 3.10 | 3.13 | 3.11 | Active development |
| 19.0 | 3.10 | 3.13 | 3.12 | Latest |

### Installing Specific Python Versions

**Windows (pyenv-win):**
```powershell
# Install pyenv-win
choco install pyenv-win  # or
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

# Install Python 3.11
pyenv install 3.11.9
pyenv local 3.11.9

# Create venv with specific version
pyenv exec python -m venv .venv
```

**Linux (pyenv):**
```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to .bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python
pyenv install 3.11.9
pyenv local 3.11.9

# Create venv
python -m venv .venv
```

**Ubuntu/Debian (apt):**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev
python3.11 -m venv .venv
```

---

## 3. Docker vs Local Decision Guide

### Use Docker When:
- Deploying to production server
- Team members have different OS setups
- Need exact environment reproducibility
- Testing Odoo against specific PostgreSQL version
- CI/CD pipeline (GitHub Actions, Jenkins)
- Onboarding new developers quickly

### Use Local Venv When:
- Active development with frequent file changes
- Need fast reload (no Docker layer overhead)
- Debugging with IDE (PyCharm/VSCode)
- Single developer working solo
- Limited system resources (Docker overhead)

### Use Bare Python When:
- Quickest possible setup
- One-off scripts or shell exploration
- System-level Odoo installation
- Production servers managed by system package manager

---

## 4. .env File Patterns for Docker

### Standard Docker .env

```bash
# .env
# PostgreSQL
POSTGRES_USER=odoo
POSTGRES_PASSWORD=securepwd_change_me
POSTGRES_DB=postgres

# Odoo
ODOO_HTTP_PORT=8069
ODOO_LONGPOLLING_PORT=8072
DEV_MODE=all

# Optional
PROJECT_NAME=myproject
ODOO_VERSION=17
```

### Loading .env in Different Contexts

**Docker Compose (automatic):**
```yaml
# docker-compose automatically reads .env in same directory
# Reference variables with ${VAR_NAME}
```

**PowerShell (manual):**
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#=\s]+)\s*=\s*(.*)$') {
        $env:($matches[1]) = $matches[2]
    }
}
```

**Bash (manual):**
```bash
export $(grep -v '^#' .env | xargs)
# or
set -a && source .env && set +a
```

**Python:**
```python
from dotenv import load_dotenv
load_dotenv()
import os
postgres_pass = os.getenv('POSTGRES_PASSWORD')
```

---

## 5. Multi-Project Local Setup

### Port Allocation Strategy

```
Standard port allocation for multiple projects:
  Project A: HTTP=8069, Longpolling=8072
  Project B: HTTP=8070, Longpolling=8073
  Project C: HTTP=8071, Longpolling=8074
  Project D: HTTP=8079, Longpolling=8082
```

### Running Multiple Projects Simultaneously

```powershell
# Windows PowerShell — start each in background
Start-Process python -ArgumentList "-m odoo -c conf\projectA17.conf" -WindowStyle Hidden
Start-Process python -ArgumentList "-m odoo -c conf\projectB17.conf" -WindowStyle Hidden
Start-Process python -ArgumentList "-m odoo -c conf\projectC17.conf" -WindowStyle Hidden

# Check which ports are in use
netstat -ano | findstr "8069\|8070\|8071"
```

```bash
# Linux — background with nohup
nohup python -m odoo -c conf/projectA17.conf > logs/projectA.log 2>&1 &
nohup python -m odoo -c conf/projectB17.conf > logs/projectB.log 2>&1 &
```

### Config File Naming Convention

```
conf/
├── TAQAT17.conf         # Project: TAQAT, Version: 17, Port: 8069
├── arcelia17.conf       # Project: arcelia, Version: 17, Port: 8070
├── oksouq1717.conf      # Project: oksouq, Version: 17, Port: 8071
├── ittihadclub17.conf   # Project: ittihadclub, Version: 17, Port: 8072
└── relief_center17.conf # Project: relief_center, Version: 17, Port: 8073
```

---

## 6. Windows-Specific Patterns

### Kill Odoo by Port

```powershell
# Method 1: CMD
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F

# Method 2: PowerShell
$port = 8069
$conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($conn) { Stop-Process -Id $conn.OwningProcess -Force }

# Method 3: Kill all Python (nuclear)
taskkill /IM python.exe /F

# Kill multiple ports
8069,8070,8071,8072,8073 | ForEach-Object {
    $conn = Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue
    if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
}
```

### Windows Service (NSSM)

```powershell
# Download NSSM from https://nssm.cc/download
# or: choco install nssm

# Install Odoo as Windows service
nssm install OdooTAQAT "C:\odoo\odoo17\.venv\Scripts\python.exe" "-m odoo -c C:\odoo\odoo17\conf\TAQAT17.conf"
nssm set OdooTAQAT AppDirectory "C:\odoo\odoo17"
nssm set OdooTAQAT AppEnvironmentExtra PYTHONPATH=C:\odoo\odoo17
nssm start OdooTAQAT

# Service management
nssm status OdooTAQAT
nssm restart OdooTAQAT
nssm stop OdooTAQAT
nssm remove OdooTAQAT confirm
```

### Windows Firewall for Odoo

```powershell
# Allow port 8069 through firewall
netsh advfirewall firewall add rule name="Odoo HTTP" dir=in action=allow protocol=TCP localport=8069
netsh advfirewall firewall add rule name="Odoo Longpolling" dir=in action=allow protocol=TCP localport=8072
```

---

## 7. Linux / macOS Patterns

### Systemd Service (Production)

```ini
# /etc/systemd/system/odoo17.service
[Unit]
Description=Odoo 17 Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo17
PermissionsStartOnly=true
User=odoo
Group=odoo
WorkingDirectory=/opt/odoo17
ExecStart=/opt/odoo17/.venv/bin/python -m odoo -c /opt/odoo17/conf/TAQAT17.conf
StandardOutput=journal+console
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable odoo17
sudo systemctl start odoo17
sudo systemctl status odoo17

# View logs
sudo journalctl -u odoo17 -f

# Restart after code changes
sudo systemctl restart odoo17
```

### macOS LaunchAgent

```xml
<!-- ~/Library/LaunchAgents/com.odoo.server.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.odoo.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/odoo17/.venv/bin/python</string>
        <string>-m</string>
        <string>odoo</string>
        <string>-c</string>
        <string>/opt/odoo17/conf/TAQAT17.conf</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/opt/odoo17</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

---

## 8. Conda Environment Setup (Alternative)

```bash
# Create Conda environment for Odoo 17
conda create -n odoo17 python=3.11
conda activate odoo17

# Install requirements
pip install -r requirements.txt

# Deactivate
conda deactivate

# List environments
conda env list

# Remove environment
conda env remove -n odoo17
```

---

## 9. Nginx Reverse Proxy for Production

### Basic Config (HTTP only)

```nginx
# /etc/nginx/sites-available/odoo.conf
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoo_longpolling {
    server 127.0.0.1:8072;
}

server {
    listen 80;
    server_name odoo.example.com;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /longpolling {
        proxy_pass http://odoo_longpolling;
        proxy_set_header Host $host;
    }

    # Static files cache
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    # Max upload size (for attachments)
    client_max_body_size 200m;
}
```

### With SSL (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d odoo.example.com

# Auto-renewal (added by certbot)
# Verify: sudo certbot renew --dry-run
```

---

## 10. wkhtmltopdf Installation

### Windows

```powershell
# Option 1: Chocolatey
choco install wkhtmltopdf

# Option 2: Manual download
# Download from https://github.com/wkhtmltopdf/packaging/releases
# Install .exe and add to PATH

# Verify
wkhtmltopdf --version
```

### Linux (Debian/Ubuntu)

```bash
# Download version matching your OS
# Bookworm (Debian 12):
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed

# Bullseye (Debian 11):
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-3.bullseye_amd64.deb

# Verify
wkhtmltopdf --version
```

### macOS

```bash
brew install --cask wkhtmltopdf
# or
brew install wkhtmltopdf
```

---

## 11. rtlcss Installation (Arabic/RTL Support)

### Requirements
- Node.js 14+
- npm

```bash
# Install Node.js first
# Windows: choco install nodejs
# Linux: sudo apt install nodejs npm
# macOS: brew install node

# Install rtlcss globally
npm install -g rtlcss

# Verify
rtlcss --version

# If not in PATH (Windows):
# Add C:\Users\[username]\AppData\Roaming\npm to PATH
```

---

## 12. PostgreSQL Setup

### Windows

```powershell
# Install via chocolatey
choco install postgresql

# Or download installer from https://www.postgresql.org/download/windows/

# Start service
net start postgresql-x64-15

# Create Odoo user
psql -U postgres -c "CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB;"

# Verify
psql -U odoo -c "SELECT 1;"
```

### Linux

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create Odoo user
sudo -u postgres psql -c "CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB SUPERUSER;"

# Verify
psql -U odoo -h localhost -c "SELECT 1;"

# pg_hba.conf (allow password auth)
# /etc/postgresql/15/main/pg_hba.conf
# Change peer to md5 for local connections
```

---

## 13. Environment-Specific Requirements

### Odoo 17 Extra Dependencies

```bash
pip install geoip2            # GeoIP database support
pip install phonenumbers      # Phone number validation
pip install vobject           # vCard/iCal support
pip install python-ldap       # LDAP authentication
pip install pyotp             # 2FA support
```

### Odoo 18 Extra Dependencies

```bash
pip install cbor2             # CBOR serialization (required)
```

### Odoo 19 Extra Dependencies

```bash
pip install cbor2             # CBOR serialization
pip install python-magic      # File type detection
# System: apt-get install libmagic1
```

---

## 14. Environment Validation Checklist

Run before starting development:

```bash
# 1. Python version
python --version               # Must match Odoo version requirements

# 2. pip version
pip --version                  # Should be 23.x+

# 3. PostgreSQL connection
pg_isready -h localhost -p 5432

# 4. wkhtmltopdf
wkhtmltopdf --version          # 0.12.6.x

# 5. rtlcss (for Arabic support)
rtlcss --version               # 4.x

# 6. Odoo importable
python -c "import odoo; print(odoo.__version__)"

# 7. Port availability
python -c "import socket; s=socket.socket(); s.connect(('localhost',8069))" 2>&1 | grep refused
# Should say "Connection refused" (port is free)
```
