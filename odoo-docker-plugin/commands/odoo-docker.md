---
title: 'Odoo Docker Infrastructure'
read_only: false
type: 'command'
description: 'Docker infrastructure for Odoo — init, compose, deploy, build, and status'
argument-hint: '[init|compose|deploy|build] [args...]'
---

# /odoo-docker — Unified Docker Infrastructure

Complete Docker infrastructure management for Odoo projects. Handles project initialization, compose generation, production deployment, and image building.

## Argument Routing

Parse `$ARGUMENTS` and route to the appropriate section:

| First Argument | Route To | Example |
|----------------|----------|---------|
| `init` | [Project Init](#section-init) | `/odoo-docker init --project relief_center` |
| `compose` | [Compose Generator](#section-compose) | `/odoo-docker compose dev --version 19` |
| `deploy` | [Production Deploy](#section-deploy) | `/odoo-docker deploy --domain relief.taqatechno.com` |
| `build` | [Image Builder](#section-build) | `/odoo-docker build 19` or `/odoo-docker build --all` |
| *(none)* | [Status + Help](#section-status) | `/odoo-docker` |

Strip the first argument before passing the rest to the section logic.

---

## Section: Status + Help {#section-status}

When no arguments are provided, show environment status and available sub-commands.

### Step 1: Docker Detection

Run `docker info` silently. Report:
- Docker Desktop: Running / Not running
- Docker version: `docker --version`

### Step 2: Project Detection

Scan current directory for:
- `docker-compose*.yml` files — list project names
- `conf/*.conf` files — list Odoo configs
- `odoo/release.py` — detect Odoo version

### Step 3: Display Help

```
Odoo Docker Infrastructure

Sub-commands:
  /odoo-docker init                    Set up Docker for a project (interactive)
  /odoo-docker compose [dev|staging|prod]  Generate docker-compose files
  /odoo-docker deploy                  Production deployment with nginx + SSL
  /odoo-docker build [version|--all]   Build & push Docker images

Examples:
  /odoo-docker init --project relief_center --version 19
  /odoo-docker compose dev
  /odoo-docker compose prod --version 17 --project almajal
  /odoo-docker deploy --domain relief.taqatechno.com
  /odoo-docker build 19
  /odoo-docker build --all --push

Related skills (separate commands):
  /docker-perf     Performance analysis & tuning
  /docker-debug    Container troubleshooting
  /docker-nginx    Nginx config generation
```

---

## Section: Project Init {#section-init}

**Absorbed from**: `docker-init-project.md`

Set up a complete Docker environment for an Odoo project. Auto-detects version, scans modules, generates configs, and creates IDE integration.

### Step 1: Check Docker

Run `docker info` to verify Docker Desktop is running. If it fails:
> "Docker Desktop is not running. Please start it first."

### Step 2: Detect Odoo Version

Auto-detect from `odoo/release.py`:
- Look for `version_info = (` — extract first integer
- Fallback: look for `version = '` — extract major version

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

Create `conf/{project_name}.conf` using SKILL.md section 7 template:
- `db_host = db`
- `addons_path` with discovered paths
- Correct `gevent_port` or `longpolling_port` (from version matrix section 3)
- `data_dir = /var/lib/odoo`

### Step 7: Generate Docker Compose

Create `docker-compose.{project_name}.yml` using SKILL.md section 6.1 or 6.2 pattern:
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

---

## Section: Compose Generator {#section-compose}

**Absorbed from**: `docker-compose-gen.md`

Generate docker-compose files tailored to dev, staging, or production scenarios. Uses version-specific settings and proven patterns.

Parse remaining arguments for scenario: `dev`, `staging`, or `prod`. If not provided, ask with `AskUserQuestion`.

### Scenarios

#### Development (`dev`)

Lightweight compose for local development:
- Build from local Dockerfile
- PostgreSQL with exposed port (5433)
- Source mounted read-only
- No nginx, no resource limits
- `DEV_MODE` and `ENABLE_DEBUGGER` env vars
- Template: SKILL.md section 6.1

#### Staging (`staging`)

Production-like settings for testing:
- Pre-built image from Docker Hub
- PostgreSQL with basic tuning
- Nginx reverse proxy (no SSL)
- Health checks on all services
- Moderate resource limits
- Template: blend of SKILL.md sections 6.2 and 6.3

#### Production (`prod`)

Full production compose:
- Pre-built image from Docker Hub
- PostgreSQL with full tuning (shared_buffers, work_mem, etc.)
- Nginx with gzip, rate limiting, asset caching
- SSL/TLS configuration
- Resource limits (memory + CPU)
- Warm-up service
- Isolated Docker network
- Template: SKILL.md section 6.3

### Interactive Flow

#### Step 1: Gather Information

Use `AskUserQuestion` for any missing values:
1. **Scenario**: dev / staging / production
2. **Odoo Version**: 14-19 (auto-detect if possible)
3. **Project Name**: for container/volume naming
4. **HTTP Port**: default 8069
5. **Additional Services** (staging/prod only):
   - Nginx reverse proxy?
   - pgAdmin for database management?

#### Step 2: Apply Version Matrix

Look up SKILL.md section 3 for the selected version:
- PostgreSQL image version
- Gevent config key
- Entry point (`odoo-bin` vs `setup/odoo`)
- Python version for build args

#### Version-Specific Settings

| Version | PostgreSQL | Image Tag | Gevent |
|---------|-----------|-----------|--------|
| 14 | postgres:12 | 14.0-enterprise | longpolling_port |
| 15 | postgres:12 | 15.0-enterprise | longpolling_port |
| 16 | postgres:12 | 16.0-enterprise | longpolling_port |
| 17 | postgres:15 | 17.0-enterprise | gevent_port |
| 18 | postgres:15 | 18.0-enterprise | gevent_port |
| 19 | postgres:15 | 19.0-enterprise | gevent_port |

#### Step 3: Generate Files

Create:
- `docker-compose.{project}.yml` (or `docker-compose.{project}.{scenario}.yml`)
- `conf/{project}.conf` (Odoo config)
- `.env` (environment variables)

#### Step 4: Display Summary

Show file paths, port mappings, and startup commands.

---

## Section: Production Deploy {#section-deploy}

**Absorbed from**: `docker-deploy.md`

Generate a complete production Docker deployment with nginx reverse proxy, SSL, PostgreSQL tuning, resource limits, health checks, and asset warm-up.

### Step 1: Detect Environment

1. Check if Docker is running: `docker info`
2. Auto-detect Odoo version from `odoo/release.py` or `setup.py`
3. If not found, ask user with `AskUserQuestion`

### Step 2: Gather Project Info

Use `AskUserQuestion` for:
- **Project name**: Name for containers, configs, volumes
- **Domain** (optional): For nginx server_name and SSL
- **SSL**: Enable HTTPS with Let's Encrypt?
- **Workers**: Number of Odoo workers (recommend: `(CPU * 2) + 1`)

### Step 3: Generate Production Files

#### 3a. `docker-compose.{project}.prod.yml`

Use the Production Compose pattern from SKILL.md section 6.3:
- PostgreSQL with tuned settings (shared_buffers, work_mem, effective_cache_size)
- Odoo with resource limits (memory: 2G, cpus: 2)
- Nginx reverse proxy (public-facing on port 80/443)
- Warm-up service for asset pre-compilation
- Health checks on all services
- Named volumes for data persistence
- Isolated Docker network

#### 3b. `conf/nginx.conf`

Use the complete nginx config from SKILL.md section 8:
- Rate limiting (10 req/s per IP, burst 20)
- Gzip compression level 6 (90% CSS reduction)
- WebSocket routing (`/websocket` to port 8072)
- Static asset caching (365d for `/web/assets/`, 7d for `/web/static/`)
- Proxy headers (X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
- Upload limit: 200MB
- If SSL: add HTTPS redirect + SSL certificate paths

#### 3c. `conf/{project}.conf`

Use the Odoo config template from SKILL.md section 7:
- `workers = {user_choice}` (minimum 2)
- `proxy_mode = True`
- `list_db = False`
- `data_dir = /var/lib/odoo`
- `db_maxconn = 16`
- `admin_passwd = <generated-32-char-password>`
- Correct `gevent_port` or `longpolling_port` based on version

#### 3d. `.env.production`

```env
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<generated-secure-password>
POSTGRES_DB=postgres
DEV_MODE=0
ENABLE_DEBUGGER=0
```

### Step 4: Security Review

Display security checklist:
- [ ] Strong admin_passwd set
- [ ] Custom database credentials
- [ ] SSL/TLS configured
- [ ] list_db = False
- [ ] proxy_mode = True
- [ ] Firewall rules in place
- [ ] Backup strategy defined

### Step 5: Deploy (Optional)

Ask user if they want to deploy now:
1. Pull image: `docker pull taqatechno/odoo:{version}.0-enterprise`
2. Start: `docker-compose -f docker-compose.{project}.prod.yml up -d`
3. Verify health: check all containers are healthy
4. Run warm-up: wait for asset compilation

### Step 6: Display Summary

Show:
- Files created (with paths)
- URLs (HTTP and HTTPS if SSL)
- Container names
- Port mappings
- Management commands (start, stop, logs, backup)
- Production checklist (from SKILL.md section 21 / reference/production-checklist.md)

### Key Reference

- SKILL.md section 6.3: Production Compose pattern
- SKILL.md section 8: Nginx configuration
- SKILL.md section 10: Production deployment
- SKILL.md section 11: Performance tuning
- SKILL.md section 12: Security hardening

---

## Section: Image Builder {#section-build}

**Absorbed from**: `docker-build.md`

Build, tag, and push Odoo Docker images to Docker Hub. Supports single version or full matrix builds across Odoo 14-19.

Parse remaining arguments:
- A number (e.g. `19`) — build that version
- `--all` — build all versions
- `--push` — push after building
- `--no-cache` — full rebuild without Docker layer cache
- `--generate-ci` — generate GitHub Actions workflow

### Build Single Version

```
/odoo-docker build 19
```

1. Locate or generate Dockerfile using version matrix (SKILL.md section 3)
2. Build image: `docker build --build-arg PYTHON_VERSION=3.12 --build-arg ODOO_VERSION=19 -t taqatechno/odoo:19.0-enterprise .`
3. Tag with SHA: `docker tag taqatechno/odoo:19.0-enterprise taqatechno/odoo:19.0-enterprise-$(git rev-parse --short HEAD)`

### Build All Versions

```
/odoo-docker build --all
```

Builds all 6 versions sequentially using the version matrix:

| Version | Python | Tag |
|---------|--------|-----|
| 14 | 3.10 | `taqatechno/odoo:14.0-enterprise` |
| 15 | 3.10 | `taqatechno/odoo:15.0-enterprise` |
| 16 | 3.10 | `taqatechno/odoo:16.0-enterprise` |
| 17 | 3.12 | `taqatechno/odoo:17.0-enterprise` |
| 18 | 3.12 | `taqatechno/odoo:18.0-enterprise` |
| 19 | 3.12 | `taqatechno/odoo:19.0-enterprise` |

### Push to Docker Hub

```
/odoo-docker build 19 --push
/odoo-docker build --all --push
```

Requires Docker Hub login:
```bash
docker login -u taqatechno
```

### Generate GitHub Actions CI/CD

```
/odoo-docker build --generate-ci
```

Creates `.github/workflows/build-push.yml` using SKILL.md section 15 template:
- Matrix strategy for all 6 versions
- Multi-platform: linux/amd64 + linux/arm64
- GitHub Actions layer cache per version
- Automatic push on main branch changes
- Manual dispatch with version selection
- Required secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`

### Build with No Cache

```
/odoo-docker build 19 --no-cache
```

Full rebuild without Docker layer cache. Use when:
- Requirements changed
- System package updates needed
- Base image updated

### Build Workarounds (Applied Automatically)

Version-specific issues handled per SKILL.md section 17:

| Version | Workaround |
|---------|-----------|
| 14 | Buster EOL — archive.debian.org mirrors |
| 14-15 | gevent 20.9.0 — Cython<3, no-build-isolation |
| 16-17 | gevent 21.8.0 — Cython<3, no-build-isolation |
| 18 | cbor2 — PIP_CONSTRAINT="setuptools<81" |
| 19 | No __init__.py — PYTHONPATH or editable install |
| All | setuptools 80+ — PIP_CONSTRAINT="setuptools<81" |

---

## Previously Available Commands

This unified command replaces the following individual commands. They continue to work but route through `/odoo-docker`:

| Old Command | New Equivalent |
|-------------|---------------|
| `/docker-init-project` | `/odoo-docker init` |
| `/docker-compose-gen` | `/odoo-docker compose` |
| `/docker-deploy` | `/odoo-docker deploy` |
| `/docker-build` | `/odoo-docker build` |
| `/odoo-docker-infra` | `/odoo-docker` (no args) |

The following remain as separate commands (specialized tools):
- `/docker-perf` — Performance analysis and tuning
- `/docker-debug` — Container troubleshooting
- `/docker-nginx` — Nginx config generation

## Natural Language Triggers

- "set up docker for this project", "initialize docker", "docker setup"
- "generate docker-compose", "create compose file", "compose for dev/staging/prod"
- "deploy to production", "production docker setup", "deploy odoo with nginx"
- "build docker image", "push to docker hub", "ci/cd pipeline", "github actions"
- "docker status", "what docker projects exist"
