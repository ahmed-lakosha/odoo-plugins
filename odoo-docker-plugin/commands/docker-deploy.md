---
title: 'Docker Production Deploy'
read_only: false
type: 'command'
description: 'Generate production-grade Docker deployment with nginx reverse proxy, SSL, PostgreSQL tuning, resource limits, and warm-up services'
---

# /docker-deploy — Production Deployment

Generate a complete production Docker deployment for an Odoo project. Includes nginx reverse proxy with gzip compression, PostgreSQL tuning, resource limits, health checks, and asset warm-up.

## Usage

```
/docker-deploy [options]
```

## Arguments (if provided): $ARGUMENTS

## Interactive Flow

When invoked, follow these steps:

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

Create the following files:

#### 3a. `docker-compose.{project}.prod.yml`

Use the **Production Compose** pattern from SKILL.md §6.3:
- PostgreSQL with tuned settings (shared_buffers, work_mem, effective_cache_size)
- Odoo with resource limits (memory: 2G, cpus: 2)
- Nginx reverse proxy (public-facing on port 80/443)
- Warm-up service for asset pre-compilation
- Health checks on all services
- Named volumes for data persistence
- Isolated Docker network

#### 3b. `conf/nginx.conf`

Use the complete nginx config from SKILL.md §8:
- Rate limiting (10 req/s per IP, burst 20)
- Gzip compression level 6 (90% CSS reduction)
- WebSocket routing (`/websocket` → port 8072)
- Static asset caching (365d for `/web/assets/`, 7d for `/web/static/`)
- Proxy headers (X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
- Upload limit: 200MB
- If SSL: add HTTPS redirect + SSL certificate paths

#### 3c. `conf/{project}.conf`

Use the Odoo config template from SKILL.md §7:
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
- Production checklist (from SKILL.md §21 / reference/production-checklist.md)

## Key Reference

- SKILL.md §6.3: Production Compose pattern
- SKILL.md §8: Nginx configuration
- SKILL.md §10: Production deployment
- SKILL.md §11: Performance tuning
- SKILL.md §12: Security hardening
- reference/production-checklist.md: Pre-deployment checklist

## Natural Language Triggers

- "deploy to production", "production docker setup"
- "deploy odoo with nginx", "production compose"
- "add ssl to odoo docker", "enable https"
- "generate production config", "production-ready deployment"
