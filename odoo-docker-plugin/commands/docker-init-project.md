---
title: 'Docker Project Initializer'
read_only: false
type: 'command'
description: 'Interactive project setup — auto-detect version, scan modules, generate Docker configs, and create IDE integration'
---

# /docker-init-project — Interactive Project Setup

Set up a complete Docker environment for an Odoo project. Auto-detects the Odoo version, scans for custom modules, generates configuration files, and creates IDE integration.

## Usage

```
/docker-init-project
/docker-init-project --project relief_center --version 19
```

## Arguments (if provided): $ARGUMENTS

## Interactive 10-Step Flow

### Step 1: Check Docker

Run `docker info` to verify Docker Desktop is running. If it fails:
> "Docker Desktop is not running. Please start it first."

### Step 2: Detect Odoo Version

Auto-detect from `odoo/release.py`:
- Look for `version_info = (` → extract first integer
- Fallback: look for `version = '` → extract major version

If `odoo/release.py` not found, ask user with `AskUserQuestion`:
> "Which Odoo version is this?"
> Options: Odoo 14, 15, 16, 17, 18, 19

Display: `Detected Odoo {version} from odoo/release.py`

### Step 3: Select Project

List subdirectories in `project-addons/` or `projects/` (whichever exists).

If no projects found:
```
No projects found.
Clone your project first:
  gh repo clone taqat-techno/my-project projects/my-project
```

Use `AskUserQuestion` to let user pick a project.

### Step 4: Scan for Custom Modules

Search project directory for `__manifest__.py` or `__openerp__.py` (max depth 3).

For each manifest:
- Module directory = parent of manifest
- Addons path = parent of module directory
- Container path: `/opt/odoo/custom-addons/{project}/{subdir}`

Display:
```
Found {count} Odoo modules in {project_name}:
  - module_a
  - module_b
Addons paths:
  - /opt/odoo/custom-addons/{project_name}
```

### Step 5: Check Existing Config

Check if `conf/{project_name}.conf` or `docker-compose.{project_name}.yml` exist.
If yes, ask user before overwriting.

### Step 6: Generate Odoo Config

Create `conf/{project_name}.conf` using SKILL.md §7 template:
- `db_host = db`
- `addons_path` with discovered paths
- Correct `gevent_port` or `longpolling_port` (from version matrix §3)
- `data_dir = /var/lib/odoo`

### Step 7: Generate Docker Compose

Create `docker-compose.{project_name}.yml` using SKILL.md §6.1 or §6.2 pattern:
- PostgreSQL image from version matrix
- Pre-built image from Docker Hub or local build
- Health checks, volumes, port mappings

### Step 8: Generate IDE Configs

**PyCharm**: Create `.idea/runConfigurations/{project}_docker.xml`

**VSCode**: Create or merge into `.vscode/tasks.json` with 5 tasks:
- `{project}: Start`
- `{project}: Stop`
- `{project}: Logs`
- `{project}: Shell`
- `{project}: Update Image`

### Step 9: Pull Image and Start (Optional)

Ask user: "Pull the Docker image and start containers now?"

If yes:
1. `docker-compose -f docker-compose.{project}.yml down 2>/dev/null`
2. `docker pull taqatechno/odoo:{version}.0-enterprise` (or `alakosha/odoo-image:{version}.0`)
3. `docker-compose -f docker-compose.{project}.yml up -d`

### Step 10: Display Summary

```
Docker environment ready!

Odoo Version: {version}
Odoo Web:     http://localhost:8069
Master Pwd:   123
Database:     {project_name}

Files created:
  - conf/{project_name}.conf
  - docker-compose.{project_name}.yml
  - .idea/runConfigurations/{project}_docker.xml  (PyCharm)
  - .vscode/tasks.json                            (VSCode)

Terminal commands:
  Start:  docker-compose -f docker-compose.{project}.yml up -d
  Stop:   docker-compose -f docker-compose.{project}.yml down
  Logs:   docker-compose -f docker-compose.{project}.yml logs -f odoo
  Shell:  docker-compose -f docker-compose.{project}.yml exec odoo bash
```

## Natural Language Triggers

- "set up docker for this project", "initialize docker"
- "create docker environment", "docker setup"
- "configure docker for odoo", "new docker project"
