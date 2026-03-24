---
title: 'Odoo Service Manager'
read_only: false
type: 'command'
description: 'Odoo server lifecycle - start, stop, init, database, Docker, and IDE configuration'
argument-hint: '[start|stop|init|db|docker|ide|scaffold|ready] [args...]'
---

# /odoo-service - Unified Odoo Service Manager

Parse the first argument of `$ARGUMENTS` and dispatch:

| Sub-command | Description |
|-------------|-------------|
| *(none)* | Show environment status + help |
| `start` | Start Odoo server (auto-detect venv/Docker/bare) |
| `stop` | Stop Odoo server (kill process on port 8069/8072) |
| `init` | Initialize environment (venv + PostgreSQL + conf) |
| `db` | Database operations (backup, restore, create, drop, reset-admin) |
| `docker` | Docker management (init, build, up, down, logs, shell) |
| `ide` | Generate IDE config (VSCode launch/tasks, PyCharm run configs) |
| `scaffold` | Scaffold new TaqaTechno module |
| `ready` | Production readiness check (tests, security, translations) |

Natural language also routes: "start odoo" -> `start`, "backup database" -> `db backup`, "generate vscode config" -> `ide vscode`.

## Environment Detection

```
1. docker-compose.yml found? --> Docker mode
2. .venv/ or venv/ found?   --> Local venv mode
3. None of above?            --> Bare Python mode
```

Override with flags: `--docker`, `--venv`, `--env local`.

## Execution

Use the odoo-service skill for:
- Complete workflow steps for each sub-command
- Environment detection rules and version matrix
- Config file format and database connection patterns
- IDE configuration templates (VSCode, PyCharm)
- Module scaffolding with TaqaTechno manifest standards
- Production readiness validation criteria

Scripts are at `${CLAUDE_PLUGIN_ROOT}/odoo-service/scripts/`:
- `server_manager.py` - Start/stop/status
- `db_manager.py` - Database operations
- `env_initializer.py` - Virtual environment setup
- `docker_manager.py` - Docker orchestration
- `ide_configurator.py` - IDE config generation
