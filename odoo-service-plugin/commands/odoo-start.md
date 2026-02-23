---
title: 'Start Odoo Server'
read_only: false
type: 'command'
description: 'Start Odoo server — auto-detects environment (local venv or Docker), handles config selection, dev mode, workers'
---

# /odoo-start — Start Odoo Server

Starts an Odoo server, auto-detecting whether to use local venv or Docker. Handles config file selection, development mode, worker count, and process management.

## Usage

```
/odoo-start [--config CONFIG] [--dev] [--docker] [--workers N] [--db DATABASE] [--port PORT]
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--config CONFIG` | Path or name of .conf file | Auto-detected |
| `--dev` | Enable `--dev=all` (auto-reload, debug) | False |
| `--docker` | Force Docker mode (docker-compose up) | Auto |
| `--workers N` | Number of worker processes | 0 (dev) |
| `--db DATABASE` | Override database from config | From config |
| `--port PORT` | HTTP port override | From config |
| `--detach` | Run in background (Windows/Linux) | False |

## Examples

### Interactive Config Selection (No flags)
```
/odoo-start
```
Scans `conf/` directory, lists available .conf files, prompts user to select one, then starts in foreground with dev mode.

### Specific Config File
```
/odoo-start --config TAQAT17.conf
```
Runs:
```bash
python -m odoo -c conf/TAQAT17.conf
```

### Development Mode
```
/odoo-start --dev
/odoo-start --config TAQAT17.conf --dev
```
Runs:
```bash
python -m odoo -c conf/TAQAT17.conf --dev=all
```
Enables:
- Auto-reload on file changes
- Detailed QWeb error messages
- Werkzeug interactive debugger
- Full XML error tracebacks

### Production Mode (Workers)
```
/odoo-start --config TAQAT17.conf --workers 4
```
Runs:
```bash
python -m odoo -c conf/TAQAT17.conf --workers=4
```

### Force Docker Mode
```
/odoo-start --docker
```
Runs:
```bash
docker-compose up -d
```

### Background Process
```
/odoo-start --config TAQAT17.conf --detach
```

## Natural Language Triggers

These phrases invoke `/odoo-start`:
- "start odoo"
- "run odoo server"
- "launch odoo"
- "start odoo server"
- "run odoo with [config]"
- "start development server"

## Implementation

Uses `odoo-service/scripts/server_manager.py`:

```python
from odoo-service.scripts.server_manager import start_local

start_local(
    config_path="conf/TAQAT17.conf",
    dev=True,
    workers=0,
    database=None,
    detach=False,
)
```

## Post-Start Verification

After starting, the command verifies:
1. Port 8069 is listening within 10 seconds
2. HTTP GET to `/web/login` returns 200
3. Prints: `Odoo is running at http://localhost:8069`

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Address already in use` | Port 8069 occupied | Run `/odoo-stop` first |
| `Config file not found` | Wrong path | Check conf/ directory |
| `No module named odoo` | venv not activated | Activate venv or use full path |
| PostgreSQL connection failed | DB not running | Start PostgreSQL service |
