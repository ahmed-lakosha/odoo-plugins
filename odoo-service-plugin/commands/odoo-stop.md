---
title: 'Stop Odoo Server'
read_only: false
type: 'command'
description: 'Stop running Odoo server — kills processes on port 8069/8072 or stops Docker containers'
---

# /odoo-stop — Stop Odoo Server

Stops a running Odoo server by killing processes using port 8069 (and optionally 8072), or stops Docker containers with `docker-compose stop`.

## Usage

```
/odoo-stop [--port PORT] [--docker] [--all] [--force]
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--port PORT` | HTTP port to kill | 8069 |
| `--docker` | Stop Docker containers | Auto-detect |
| `--all` | Kill ALL Odoo Python processes | False |
| `--force` | Skip confirmation | False |

## Examples

### Auto-Detect and Stop
```
/odoo-stop
```
Auto-detects environment (docker-compose.yml → Docker; else local), then stops appropriately.

### Kill by Port (Local)
```
/odoo-stop --port 8069
```

Windows implementation:
```powershell
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8072') DO taskkill /PID %P /F
```

Linux/Mac implementation:
```bash
lsof -ti:8069 | xargs kill -9
lsof -ti:8072 | xargs kill -9
```

### Stop Docker Containers
```
/odoo-stop --docker
```
Runs:
```bash
docker-compose stop
```
(Preserves container state and volumes)

### Kill All Odoo Processes (Nuclear Option)
```
/odoo-stop --all
```

Windows:
```powershell
taskkill /IM python.exe /F
```

Linux/Mac:
```bash
pkill -f "odoo"
```

### Stop Multiple Ports (Multi-Project)
```
/odoo-stop --port 8069
/odoo-stop --port 8070
/odoo-stop --port 8071
```

## Natural Language Triggers

- "stop odoo"
- "kill odoo"
- "shut down server"
- "stop the server"
- "kill port 8069"
- "stop docker"
- "stop odoo containers"

## Implementation

Uses `odoo-service/scripts/server_manager.py`:

```python
from server_manager import stop_local
stop_local(port=8069, also_longpolling=True)
```

## Verification

After stopping, verifies:
- Port 8069 no longer listening
- Prints confirmation message
- If port still in use after 3 seconds, suggests force kill
