---
title: 'Initialize Odoo Environment'
read_only: false
type: 'command'
description: 'Initialize a new Odoo environment — creates venv, installs requirements, configures PostgreSQL, generates .conf file, optionally creates database'
---

# /odoo-init — Initialize Odoo Environment

Full environment initialization for a new Odoo project. Creates virtual environment, installs dependencies, generates configuration files, and optionally scaffolds a new module.

## Usage

```
/odoo-init --version VERSION --project NAME [--port PORT] [--docker] [--db DATABASE]
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--version N` | Odoo version (14-19) | Required |
| `--project NAME` | Project/client name | Required |
| `--port PORT` | HTTP port | 8069 |
| `--docker` | Generate Docker files instead of venv | False |
| `--db DATABASE` | Database name | project+version |
| `--workers N` | Worker count in conf | 0 |
| `--no-venv` | Skip venv creation | False |

## Examples

### Local Venv Initialization
```
/odoo-init --version 17 --project myproject --port 8069
```

Creates:
```
myproject/
├── .venv/                    ← Virtual environment (Python 3.11)
├── conf/
│   └── myproject17.conf      ← Generated config file
├── logs/                     ← Log directory
├── data/                     ← Data directory
├── backups/                  ← Backup directory
├── projects/
│   └── myproject/            ← Project addon directory
└── .gitignore                ← Odoo-specific gitignore
```

Generated `conf/myproject17.conf`:
```ini
[options]
addons_path = odoo\addons,projects\myproject
admin_passwd = 123
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = myproject17.*
http_port = 8069
gevent_port = 8072
workers = 0
```

### Docker Initialization
```
/odoo-init --docker --version 17 --project myproject
```

Creates:
```
myproject/
├── Dockerfile                ← Odoo 17 Dockerfile
├── docker-compose.yml        ← PostgreSQL + Odoo services
├── .env                      ← Environment variables
├── .env.example              ← Template
├── conf/
├── logs/
├── backups/
└── projects/myproject/
```

### Custom Port (Multi-Project)
```
/odoo-init --version 17 --project projectb --port 8070
```

Creates conf with `http_port=8070`, `gevent_port=8073`.

## Step-by-Step Wizard Output

```
==================================================
ODOO 17 ENVIRONMENT INITIALIZATION
==================================================
Project: myproject
Version: 17
Port: 8069
Database: myproject17
Mode: Local venv
==================================================

[STEP 1] Creating directory structure...
  [OK] conf/
  [OK] logs/
  [OK] data/
  [OK] backups/
  [OK] projects/myproject/

[STEP 2] Creating virtual environment...
  [OK] .venv/ created (Python 3.11.x)

[STEP 3] Installing requirements...
  [OK] requirements.txt installed (142 packages)

[STEP 4] Checking PostgreSQL...
  [OK] PostgreSQL connection successful (localhost:5432)

[STEP 5] Generating configuration file...
  [OK] conf/myproject17.conf created

[STEP 6] Creating .gitignore...
  [OK] .gitignore created

[STEP 7] Checking wkhtmltopdf...
  [OK] wkhtmltopdf found: 0.12.6.1 (with patched qt)

==================================================
INITIALIZATION COMPLETE
==================================================
Config file: conf/myproject17.conf

Next steps:
  1. Activate venv:  .venv\Scripts\activate
  2. Start Odoo:     python -m odoo -c conf/myproject17.conf --dev=all
  3. Open browser:   http://localhost:8069
==================================================
```

## Natural Language Triggers

- "set up odoo"
- "initialize odoo project"
- "create new odoo environment"
- "setup new project"
- "initialize environment for odoo 17"
- "create odoo 17 project"

## Implementation

Uses `odoo-service/scripts/env_initializer.py`:

```python
from env_initializer import full_init
full_init(
    version=17,
    project="myproject",
    port=8069,
    docker=False,
)
```
