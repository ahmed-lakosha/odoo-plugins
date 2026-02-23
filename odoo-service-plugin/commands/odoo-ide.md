---
title: 'IDE Configuration Generator'
read_only: false
type: 'command'
description: 'Generate IDE run configurations for PyCharm and VSCode — creates run configs, tasks.json, launch.json, settings.json for Odoo development'
---

# /odoo-ide — IDE Configuration Generator

Generates complete IDE configurations for PyCharm and VSCode to develop Odoo projects without manual setup. Supports both local venv and Docker environments.

## Usage

```
/odoo-ide [--ide IDE] [--env ENV] [--project NAME] [--config CONFIG] [--venv PATH]
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--ide` | IDE target: `pycharm`, `vscode`, `both` | `both` |
| `--env` | Environment: `local`, `docker` | `local` |
| `--project NAME` | Project name | `myproject` |
| `--config CONFIG` | Odoo config filename | `odoo.conf` |
| `--venv PATH` | Venv directory path | `.venv` |
| `--output DIR` | Output directory | `.` (current dir) |

## Examples

### VSCode (Local Venv)

```
/odoo-ide --ide vscode --env local --config TAQAT17.conf --project TAQAT
```

Creates:
```
.vscode/
├── tasks.json    ← Start, stop, update, install tasks
├── launch.json   ← Debug configurations
├── settings.json ← Python paths, file exclusions
└── extensions.json ← Recommended extensions
```

### PyCharm (Docker)

```
/odoo-ide --ide pycharm --env docker --project myproject
```

Creates:
```
.idea/
└── runConfigurations/
    └── Odoo_myproject_Docker.xml
```

### Both IDEs (Local)

```
/odoo-ide --ide both --env local --config TAQAT17.conf --project TAQAT
```

### Generate Only .gitignore

```
/odoo-ide --gitignore-only
```

## Generated Files Detail

### .vscode/tasks.json — Available Tasks

| Task Label | Action |
|-----------|--------|
| `Odoo: Start (dev mode)` | `python -m odoo -c conf/X --dev=all` |
| `Odoo: Start (production)` | `python -m odoo -c conf/X --workers=4` |
| `Odoo: Stop` | Kill process on port 8069 |
| `Odoo: Update Module` | `-u module --stop-after-init` |
| `Odoo: Install Module` | `-i module --stop-after-init` |
| `Odoo: Refresh Module List` | `--update-list` |
| `Docker: Start` | `docker-compose up -d` |
| `Docker: Stop` | `docker-compose down` |
| `Docker: Rebuild` | `docker-compose up -d --build` |
| `Docker: Logs` | `docker-compose logs -f odoo` |
| `Docker: Shell` | `docker-compose exec odoo bash` |
| `Docker: Update Module` | `exec odoo ... -u module` |
| `DB: Backup` | `db_manager.py backup` |

### .vscode/launch.json — Debug Configurations

| Configuration | Description |
|--------------|-------------|
| `Odoo: Debug (Local)` | Debug local Odoo with `--dev=all` |
| `Odoo: Debug (Local, specific DB)` | Debug with explicit DB |
| `Odoo: Debug (Docker attach)` | Attach to debugpy in Docker container |
| `Odoo: Update Module` | Run module update with debugger |

### .idea/runConfigurations/ — PyCharm

| File | Description |
|------|-------------|
| `Odoo_[PROJECT].xml` | Local Python run config |
| `Odoo_[PROJECT]_dev.xml` | Local Python + `--dev=all` |
| `Odoo_[PROJECT]_Docker.xml` | Docker Compose run config |

### .vscode/settings.json — Key Settings

```json
{
  "python.analysis.extraPaths": ["./odoo", "./odoo/addons", "./projects"],
  "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
  "files.exclude": {"**/__pycache__": true, "**/*.pyc": true},
  "editor.rulers": [79, 120],
  "files.associations": {"*.conf": "ini", "*.po": "po"}
}
```

## Natural Language Triggers

- "create pycharm config"
- "generate vscode settings"
- "set up ide for odoo"
- "generate run configuration"
- "create debug configuration"
- "setup vscode for odoo development"

## Implementation

Uses `odoo-service/scripts/ide_configurator.py`:

```python
from ide_configurator import generate_all_vscode, generate_all_pycharm

generate_all_vscode("myproject", config_file="TAQAT17.conf")
generate_all_pycharm("myproject", env_type="docker")
```
