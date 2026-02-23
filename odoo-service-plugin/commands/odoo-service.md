---
title: 'Odoo Service Manager'
read_only: true
type: 'command'
description: 'Main entry point for Odoo server lifecycle management — start, stop, deploy, initialize, database ops, Docker, and IDE configuration'
---

# Odoo Service Manager

Complete Odoo server lifecycle management across local venv, Docker, and bare Python environments. Supports Odoo 14-19 and IDE integration for PyCharm and VSCode.

## Command Overview

| Command | Description | Triggers |
|---------|-------------|---------|
| `/odoo-start` | Start Odoo server (auto-detects env) | "start odoo", "run odoo", "launch server" |
| `/odoo-stop` | Stop Odoo server or containers | "stop odoo", "kill odoo", "shut down" |
| `/odoo-init` | Initialize new Odoo environment | "set up odoo", "new project", "init environment" |
| `/odoo-db` | Database operations | "backup database", "restore db", "create db" |
| `/odoo-docker` | Docker management | "docker build", "docker logs", "container shell" |
| `/odoo-ide` | IDE config generator | "pycharm config", "vscode settings", "setup ide" |

## Environment Detection

The plugin automatically detects your environment before any operation:

```
Project directory scan:
  1. docker-compose.yml found? → Docker mode
  2. Dockerfile found?         → Docker build mode
  3. .venv/ or venv/ found?   → Local venv mode
  4. None of above?            → Bare Python mode
```

Override with flags: `--docker`, `--venv`, `--env local`

## Quick Start Examples

### Scenario 1: Existing Local Project (Most Common)

```bash
# Start in dev mode
/odoo-start --config myproject.conf --dev

# Or type naturally:
"start odoo with myproject.conf in dev mode"

# Stop server
/odoo-stop

# Backup database
/odoo-db backup --db mydb
```

### Scenario 2: New Project from Scratch

```bash
# Initialize environment
/odoo-init --version 17 --project myproject --port 8069

# Generate IDE configs
/odoo-ide --ide both --env local --config myproject17.conf

# Start server
/odoo-start --config myproject17.conf --dev
```

### Scenario 3: Docker Deployment

```bash
# Initialize Docker project
/odoo-init --docker --version 17 --project myproject

# Build and start
/odoo-docker up

# View logs
/odoo-docker logs

# Update module
/odoo-docker update --db mydb --module my_module

# Stop
/odoo-docker down
```

## Supported Odoo Versions

| Version | Python Range | Environment | Notes |
|---------|-------------|-------------|-------|
| 14 | 3.7 - 3.10 | venv/docker | Legacy, longpolling_port |
| 15 | 3.8 - 3.11 | venv/docker | |
| 16 | 3.9 - 3.12 | venv/docker | |
| 17 | 3.10 - 3.13 | venv/docker | PRIMARY — gevent_port |
| 18 | 3.10 - 3.13 | venv/docker | cbor2 required |
| 19 | 3.10 - 3.13 | venv/docker | libmagic1 required |

## Available Scripts

Located in `odoo-service/scripts/`:

- `server_manager.py` — Start/stop/status/restart Odoo processes
- `env_initializer.py` — Create venv, install deps, generate conf
- `db_manager.py` — Backup/restore/create/drop databases
- `docker_manager.py` — Docker lifecycle + Dockerfile/compose generation
- `ide_configurator.py` — PyCharm/VSCode config generation

## Natural Language Triggers

The plugin responds to these natural language patterns:

- "start odoo", "run odoo server", "launch odoo" → `/odoo-start`
- "stop odoo", "kill odoo", "shut down server" → `/odoo-stop`
- "set up odoo", "initialize project", "new odoo env" → `/odoo-init`
- "backup database", "restore db", "create database" → `/odoo-db`
- "docker build", "start container", "view logs" → `/odoo-docker`
- "pycharm config", "vscode setup", "ide configuration" → `/odoo-ide`
