---
title: 'Docker Compose Generator'
read_only: false
type: 'command'
description: 'Generate docker-compose files for dev, staging, or production scenarios with smart defaults'
---

# /docker-compose-gen — Smart Compose Generator

Generate docker-compose files tailored to your scenario. Uses version-specific settings and proven patterns from production deployments.

## Usage

```
/docker-compose-gen
/docker-compose-gen --scenario dev --version 19 --project relief_center
/docker-compose-gen --scenario prod --version 17 --project almajal
```

## Arguments (if provided): $ARGUMENTS

## Scenarios

### Development (`--scenario dev`)

Generates a lightweight compose for local development:
- Build from local Dockerfile
- PostgreSQL with exposed port (5433)
- Source mounted read-only
- No nginx, no resource limits
- `DEV_MODE` and `ENABLE_DEBUGGER` env vars
- Template: SKILL.md §6.1

### Staging (`--scenario staging`)

Generates a staging compose with production-like settings:
- Pre-built image from Docker Hub
- PostgreSQL with basic tuning
- Nginx reverse proxy (no SSL)
- Health checks on all services
- Moderate resource limits
- Template: blend of §6.2 and §6.3

### Production (`--scenario prod`)

Generates a full production compose:
- Pre-built image from Docker Hub
- PostgreSQL with full tuning (shared_buffers, work_mem, etc.)
- Nginx with gzip, rate limiting, asset caching
- SSL/TLS configuration
- Resource limits (memory + CPU)
- Warm-up service
- Isolated Docker network
- Template: SKILL.md §6.3

## Interactive Flow

### Step 1: Gather Information

Use `AskUserQuestion` for:
1. **Scenario**: dev / staging / production
2. **Odoo Version**: 14-19 (auto-detect if possible)
3. **Project Name**: for container/volume naming
4. **HTTP Port**: default 8069
5. **Additional Services** (for staging/prod):
   - Nginx reverse proxy?
   - pgAdmin for database management?
   - Monitoring (optional)?

### Step 2: Apply Version Matrix

Look up SKILL.md §3 for the selected version:
- PostgreSQL image version
- Gevent config key
- Entry point (`odoo-bin` vs `setup/odoo`)
- Python version for build args

### Step 3: Generate Files

Create:
- `docker-compose.{project}.yml` (or `docker-compose.{project}.{scenario}.yml`)
- `conf/{project}.conf` (Odoo config)
- `.env` (environment variables)

### Step 4: Display Summary

Show file paths, port mappings, and startup commands.

## Version-Specific Compose Settings

| Version | PostgreSQL | Image Tag | Gevent |
|---------|-----------|-----------|--------|
| 14 | postgres:12 | 14.0-enterprise | longpolling_port |
| 15 | postgres:12 | 15.0-enterprise | longpolling_port |
| 16 | postgres:12 | 16.0-enterprise | longpolling_port |
| 17 | postgres:15 | 17.0-enterprise | gevent_port |
| 18 | postgres:15 | 18.0-enterprise | gevent_port |
| 19 | postgres:15 | 19.0-enterprise | gevent_port |

## Natural Language Triggers

- "generate docker-compose", "create compose file"
- "docker compose for dev", "development compose"
- "production compose", "staging docker setup"
- "create docker config for project"
