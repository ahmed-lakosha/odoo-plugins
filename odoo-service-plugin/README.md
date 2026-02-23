# Odoo Service Manager Plugin

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/taqat-techno/plugins)
[![Odoo](https://img.shields.io/badge/odoo-14--19-green)](https://www.odoo.com)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![Author](https://img.shields.io/badge/author-TaqaTechno-purple)](https://taqat-techno.com)

Complete Odoo server lifecycle manager for Claude Code. Run, deploy, initialize, and manage Odoo servers across any environment and any IDE — without manual setup.

---

## Overview

The `odoo-service` plugin gives Claude Code deep knowledge of Odoo server operations, enabling it to:

- **Start and stop** Odoo servers across Windows, Linux, and macOS
- **Initialize** complete Odoo environments (venv, Docker, or bare Python)
- **Manage databases** — backup, restore, create, drop, list, reset passwords
- **Orchestrate Docker** — generate Dockerfiles, docker-compose files, manage containers
- **Configure IDEs** — generate PyCharm run configs and VSCode tasks/launch/settings
- **Detect environments** — auto-detect whether you're using venv, Docker, or bare Python
- **Handle all Odoo versions** — 14, 15, 16, 17, 18, 19

---

## Supported Environments

| Environment | Description | Best For |
|-------------|-------------|---------|
| Local venv | Virtual environment in project root | Active development |
| Docker | docker-compose with PostgreSQL service | Deployment, team onboarding |
| Bare Python | System Python without venv | Quick testing |

## Supported IDEs

| IDE | Config Generated |
|-----|-----------------|
| PyCharm | `.idea/runConfigurations/*.xml` |
| VSCode | `.vscode/tasks.json`, `launch.json`, `settings.json` |

## Supported Odoo Versions

| Version | Python Range | Notes |
|---------|-------------|-------|
| 14 | 3.7 - 3.10 | Legacy support |
| 15 | 3.8 - 3.11 | |
| 16 | 3.9 - 3.12 | |
| 17 | 3.10 - 3.13 | Primary development version |
| 18 | 3.10 - 3.13 | cbor2 required |
| 19 | 3.10 - 3.13 | libmagic1 required |

---

## Quick Start

### Scenario 1: Start Existing Local Project

```bash
# Tell Claude: "start odoo with myproject.conf in dev mode"
# Claude runs:
python -m odoo -c conf/myproject.conf --dev=all
```

### Scenario 2: New Project from Scratch

```bash
# 1. Initialize environment
/odoo-init --version 17 --project myproject --port 8069

# 2. Generate IDE configs
/odoo-ide --ide both --env local --config myproject17.conf

# 3. Start server
/odoo-start --config myproject17.conf --dev
```

### Scenario 3: Docker Deployment

```bash
# 1. Generate Docker files
/odoo-docker init --version 17 --project myproject

# 2. Build and start
/odoo-docker up

# 3. View logs
/odoo-docker logs

# 4. Update module
/odoo-docker update --db mydb --module my_module
```

### Scenario 4: Database Management

```bash
# Backup
/odoo-db backup --db mydb

# Restore to new database
/odoo-db restore --file backups/mydb_20240101.dump --db mydb_restored

# Reset admin password
/odoo-db reset-admin --db mydb --password newpassword

# Backup from Docker container
/odoo-db backup --docker odoo_db --db mydb
```

---

## Commands Reference

### /odoo-service — Main Help

```
/odoo-service
```

Displays overview of all commands, environment detection status, and quick-start examples.

### /odoo-start — Start Server

```
/odoo-start [--config CONFIG] [--dev] [--docker] [--workers N]
```

| Example | Action |
|---------|--------|
| `/odoo-start` | Interactive config selection |
| `/odoo-start --config myproject.conf` | Start with specific config |
| `/odoo-start --dev` | Start with `--dev=all` |
| `/odoo-start --docker` | `docker-compose up -d` |
| `/odoo-start --workers 4` | Production mode (4 workers) |

### /odoo-stop — Stop Server

```
/odoo-stop [--port PORT] [--docker] [--all]
```

| Example | Action |
|---------|--------|
| `/odoo-stop` | Auto-detect and stop |
| `/odoo-stop --port 8069` | Kill by port |
| `/odoo-stop --docker` | `docker-compose stop` |
| `/odoo-stop --all` | Kill all Odoo processes |

### /odoo-init — Initialize Environment

```
/odoo-init --version N --project NAME [--port PORT] [--docker]
```

| Example | Action |
|---------|--------|
| `/odoo-init --version 17 --project myproject` | Local venv setup |
| `/odoo-init --docker --version 17 --project myproject` | Docker setup |
| `/odoo-init --version 17 --project proj --port 8070` | Custom port |

Creates: venv, conf file, log/data/backup dirs, .gitignore.

### /odoo-db — Database Operations

```
/odoo-db <backup|restore|create|drop|list|reset-admin|modules|auto-backup> [options]
```

| Example | Action |
|---------|--------|
| `/odoo-db backup --db mydb` | Backup to backups/ (dump format) |
| `/odoo-db backup --db mydb --format sql` | Backup as SQL |
| `/odoo-db restore --file backup.dump --db newdb` | Restore |
| `/odoo-db create --db newproject17` | Create database |
| `/odoo-db drop --db oldproject` | Drop (with confirmation) |
| `/odoo-db list` | List all databases |
| `/odoo-db reset-admin --db mydb --password newpass` | Reset admin |
| `/odoo-db backup --docker odoo_db --db mydb` | Docker backup |
| `/odoo-db auto-backup --config conf/proj.conf` | Backup all matching DBs |

### /odoo-docker — Docker Management

```
/odoo-docker <init|build|up|down|start|stop|restart|logs|shell|odoo-shell|update|install|status>
```

| Example | Action |
|---------|--------|
| `/odoo-docker init --version 17 --project myproject` | Generate Docker files |
| `/odoo-docker build` | `docker-compose build` |
| `/odoo-docker up` | `docker-compose up -d` |
| `/odoo-docker down` | `docker-compose down` |
| `/odoo-docker logs` | Follow container logs |
| `/odoo-docker shell` | Bash in Odoo container |
| `/odoo-docker odoo-shell --db mydb` | Odoo Python shell |
| `/odoo-docker update --db mydb --module my_module` | Update module |
| `/odoo-docker status` | `docker-compose ps` |

### /odoo-ide — IDE Configuration

```
/odoo-ide [--ide pycharm|vscode|both] [--env local|docker] [--project NAME] [--config CONFIG]
```

| Example | Action |
|---------|--------|
| `/odoo-ide --ide vscode --env local --config myproject.conf` | VSCode local config |
| `/odoo-ide --ide pycharm --env docker --project myproject` | PyCharm Docker config |
| `/odoo-ide --ide both --env local` | Both IDEs |
| `/odoo-ide --gitignore-only` | Generate .gitignore only |

---

## Architecture

```
odoo-service-plugin/
│
├── .claude-plugin/
│   └── plugin.json              ← Plugin metadata and registration
│
├── odoo-service/
│   ├── SKILL.md                 ← 900+ line skill definition
│   └── scripts/
│       ├── server_manager.py    ← Start/stop/status/restart Odoo
│       ├── env_initializer.py   ← Venv, PostgreSQL, conf setup
│       ├── db_manager.py        ← Backup/restore/create/drop
│       ├── docker_manager.py    ← Docker lifecycle + file generation
│       └── ide_configurator.py  ← PyCharm/VSCode config generation
│
├── commands/
│   ├── odoo-service.md          ← /odoo-service (main help)
│   ├── odoo-start.md            ← /odoo-start
│   ├── odoo-stop.md             ← /odoo-stop
│   ├── odoo-init.md             ← /odoo-init
│   ├── odoo-db.md               ← /odoo-db
│   ├── odoo-docker.md           ← /odoo-docker
│   └── odoo-ide.md              ← /odoo-ide
│
├── memories/
│   ├── environment_patterns.md  ← venv, Docker, OS-specific patterns
│   ├── server_commands.md       ← All startup flags, config reference
│   └── database_patterns.md    ← PostgreSQL operations, backup strategy
│
├── hooks/
│   └── hooks.json               ← 12 smart trigger hooks
│
└── README.md                    ← This file
```

---

## Python Scripts

All scripts in `odoo-service/scripts/` are standalone and work without Odoo installed. They use only Python standard library plus optional `psutil`.

### server_manager.py

```bash
python server_manager.py start --config conf/myproject.conf --dev
python server_manager.py stop --port 8069
python server_manager.py status
python server_manager.py restart --config conf/myproject.conf
python server_manager.py install --config conf/myproject.conf --db mydb --module my_module
python server_manager.py update --config conf/myproject.conf --db mydb --module my_module
python server_manager.py logs --file logs/odoo.log --lines 50
python server_manager.py processes
```

### env_initializer.py

```bash
python env_initializer.py init --version 17 --project myproject --port 8069
python env_initializer.py venv --python python3.11
python env_initializer.py check
python env_initializer.py conf --project myproject --version 17 --port 8069
python env_initializer.py scaffold --name my_module --path projects/myproject/
```

### db_manager.py

```bash
python db_manager.py backup --db mydb --output backups/
python db_manager.py restore --file backups/backup.dump --db newdb
python db_manager.py create --db newproject17
python db_manager.py drop --db oldproject
python db_manager.py list
python db_manager.py reset-admin --db mydb --password newpass
python db_manager.py modules --db mydb
python db_manager.py auto-backup --config conf/proj.conf --output backups/
```

### docker_manager.py

```bash
python docker_manager.py init --version 17 --project myproject
python docker_manager.py build
python docker_manager.py up
python docker_manager.py down
python docker_manager.py logs
python docker_manager.py shell
python docker_manager.py status
python docker_manager.py update --db mydb --module my_module
```

### ide_configurator.py

```bash
python ide_configurator.py --ide vscode --env local --config myproject.conf
python ide_configurator.py --ide pycharm --env docker --project myproject
python ide_configurator.py --ide both --env local --project myproject
python ide_configurator.py --gitignore-only
```

---

## Smart Hooks

The plugin includes 12 automatic triggers that fire based on context:

| Hook | Triggers When | Suggests |
|------|--------------|---------|
| requirements-changed | `requirements.txt` modified | Run `pip install -r requirements.txt` |
| conf-file-changed | `*.conf` file modified | Restart Odoo server |
| docker-compose-changed | `docker-compose.yml` modified | `docker-compose up -d` |
| dockerfile-changed | `Dockerfile` modified | Rebuild image |
| model-file-created | New `models/*.py` created | `python -m odoo ... -u MODULE` |
| manifest-changed | `__manifest__.py` modified | Update module, bump version |
| pre-commit-reminder | Before git commit | Restart server after commit |
| error-address-in-use | Port already in use error | `/odoo-stop` command |
| error-postgresql-connection | Cannot connect to PostgreSQL | Start PostgreSQL service |
| error-no-module-named | Python ImportError | `pip install` or requirements |
| error-access-denied | Odoo AccessDenied error | Check admin_passwd in conf |
| error-database-not-exist | DB not found error | `/odoo-db create` command |

---

## Natural Language Support

Claude responds to natural language requests using this plugin:

| You say... | Plugin action |
|------------|--------------|
| "start odoo" | `/odoo-start` (interactive) |
| "run odoo with myproject.conf" | `/odoo-start --config myproject.conf` |
| "stop odoo" | `/odoo-stop` |
| "kill the server" | `/odoo-stop` |
| "set up a new odoo 17 project" | `/odoo-init --version 17` |
| "backup the database" | `/odoo-db backup` |
| "restore from backup" | `/odoo-db restore` |
| "start docker" | `/odoo-docker up` |
| "view container logs" | `/odoo-docker logs` |
| "generate vscode settings" | `/odoo-ide --ide vscode` |
| "create pycharm config" | `/odoo-ide --ide pycharm` |

---

## Troubleshooting

### Port 8069 Already In Use

```bash
# Windows
FOR /F "tokens=5" %P IN ('netstat -ano ^| findstr :8069') DO taskkill /PID %P /F

# Linux/Mac
lsof -ti:8069 | xargs kill -9

# Or use plugin
/odoo-stop
```

### PostgreSQL Not Running

```bash
# Windows
net start postgresql-x64-15

# Linux
sudo systemctl start postgresql

# Verify
pg_isready -h localhost -p 5432
```

### Module Not Appearing

```bash
# Refresh module list
python -m odoo -c conf/proj.conf -d mydb --update-list

# Then check addons_path in .conf includes your module directory
```

### Changes Not Reflecting

```bash
# Python/XML changes: update module
python -m odoo -c conf/proj.conf -d mydb -u my_module --stop-after-init

# JS/CSS changes: hard refresh in browser
# Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

### Docker Health Check Failing

```yaml
# Increase start_period in docker-compose.yml
healthcheck:
  start_period: 30s  # Give PostgreSQL more time to start
  retries: 10
```

---

## Contributing

This plugin is maintained by TaqaTechno. To report issues or suggest improvements:

1. Submit issues via GitHub: https://github.com/taqat-techno/plugins/issues
2. Contact: support@example.com

---

## License

MIT License — See LICENSE file for details.

---

## Related Plugins

- `odoo-module-scaffold` — Advanced Odoo module scaffolding with templates
- `odoo-theme-builder` — Website theme development tools
- `odoo-deploy` — Production deployment with nginx, SSL, and monitoring

---

*Built by TaqaTechno — Odoo development specialists since 2019*
*Website: https://taqat-techno.com | Email: support@example.com*
