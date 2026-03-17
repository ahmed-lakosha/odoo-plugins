---
name: odoo-docker
description: |
  Docker infrastructure manager for Odoo — production deployment, nginx proxy, CI/CD pipelines, performance tuning, multi-version image management, container debugging, and centralized workspace orchestration for Odoo 14-19 Enterprise. v2.0 consolidates nginx, debug, and perf into natural language triggers alongside the /odoo-docker sub-command interface.


  <example>
  Context: User wants to deploy Odoo to production with Docker
  user: "Deploy my Odoo 17 project to production using Docker"
  assistant: "I will use the odoo-docker skill to generate a production docker-compose.yml with Odoo, PostgreSQL, and nginx containers, with proper volume mounts and restart policies."
  <commentary>Core trigger - production Docker deployment.</commentary>
  </example>

  <example>
  Context: User wants nginx reverse proxy configuration
  user: "Set up nginx as a reverse proxy in front of my Odoo Docker container"
  assistant: "I will use the odoo-docker skill to generate an nginx.conf with SSL termination, WebSocket longpolling proxy, and proper cache headers for Odoo static assets."
  <commentary>Infrastructure trigger - nginx configuration for Odoo.</commentary>
  </example>

  <example>
  Context: User has a crashing Docker container
  user: "My Odoo Docker container keeps restarting - how do I debug it?"
  assistant: "I will use the odoo-docker skill to check container logs, verify environment variables, inspect the Odoo config, and identify the startup failure cause."
  <commentary>Debugging trigger - container crash diagnosis.</commentary>
  </example>

  <example>
  Context: User needs nginx reverse proxy for Odoo
  user: "Generate nginx config for my Odoo Docker setup"
  assistant: "I will use the odoo-docker skill to generate an optimized nginx.conf with gzip, WebSocket proxy, caching, and rate limiting."
  <commentary>Nginx trigger - reverse proxy configuration.</commentary>
  </example>

  <example>
  Context: User's container keeps crashing
  user: "My Odoo container keeps restarting, help me debug it"
  assistant: "I will use the odoo-docker skill to check container status, logs, health, network, and volumes systematically."
  <commentary>Debug trigger - container troubleshooting.</commentary>
  </example>

  <example>
  Context: User wants performance optimization
  user: "Analyze and tune my Odoo Docker performance"
  assistant: "I will use the odoo-docker skill to analyze Docker config, PostgreSQL tuning, resource limits, and generate recommendations."
  <commentary>Performance trigger - Docker tuning analysis.</commentary>
  </example>

  <example>
  Context: User wants to build Docker images
  user: "Build Docker image for Odoo 17 with my custom modules"
  assistant: "I will use the odoo-docker skill to create a Dockerfile and build the image with proper layer caching."
  <commentary>Build trigger - Docker image creation.</commentary>
  </example>
version: "2.0.0"
author: "TaqaTechno"
license: "MIT"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - AskUserQuestion
metadata:
  mode: codebase
  odoo-versions: ["14", "15", "16", "17", "18", "19"]
  categories: [docker, infrastructure, deployment, nginx, ci-cd, performance-tuning, troubleshooting]
---

# Odoo Docker Infrastructure Skill

## 1. Overview / Role

The `odoo-docker` skill is the Docker **infrastructure and deployment** expert for TaqaTechno's multi-version Odoo Enterprise environment. It handles everything beyond basic container lifecycle — production deployment, nginx configuration, CI/CD pipelines, performance tuning, security hardening, and container troubleshooting.

> **v2.0 Architecture**: Nginx config, debugging, and performance tuning are handled via natural language.
> For project init, compose generation, deployment, and builds, use `/odoo-docker` sub-commands.

### What This Skill Does

- **Production Deployment**: Generate production-grade docker-compose with nginx reverse proxy, SSL, PostgreSQL tuning, resource limits, and warm-up services
- **CI/CD Pipelines**: Build and push multi-version Docker images to Docker Hub via GitHub Actions
- **Performance Tuning**: Analyze and optimize workers, PostgreSQL settings, gzip compression, and asset compilation — backed by real stress test data
- **Nginx Configuration**: Generate optimized nginx configs with gzip (90% CSS reduction), WebSocket routing, asset caching, and rate limiting
- **Container Debugging**: Systematic troubleshooting using a comprehensive knowledge base of known issues and fixes
- **Interactive Project Setup**: Auto-detect Odoo version, scan modules, and generate all Docker configs with IDE integration
- **Docker Compose Generation**: Smart compose generation for dev/staging/production scenarios
- **Multi-Version Image Management**: Build, tag, and push images for Odoo 14-19 across amd64 and arm64 platforms

### When to Use This Skill vs `odoo-service`

| Use `odoo-service` for... | Use `odoo-docker` for... |
|---|---|
| Starting/stopping servers | Deploying to production |
| Basic `docker up/down/logs` | Configuring nginx reverse proxy |
| Database backup/restore | CI/CD pipeline setup |
| IDE configuration | Performance analysis & tuning |
| Environment initialization | Container debugging & troubleshooting |
| Module install/update | Building & pushing Docker images |
| | Multi-project workspace orchestration |
| | Security hardening |

### Natural Language Triggers

- "deploy to production", "production docker setup", "deploy odoo with nginx"
- "configure nginx for odoo", "add reverse proxy", "enable gzip"
- "optimize docker performance", "slow containers", "tune workers"
- "build docker image", "push to docker hub", "ci/cd pipeline"
- "container won't start", "500 errors in docker", "debug container"
- "set up docker for this project", "initialize docker environment"
- "generate docker-compose", "create compose file"

---

## 2. Architecture

TaqaTechno uses a **shared base image model** for all Odoo Docker deployments.

### Core Principle: Source Mounted, Not Baked

```
Docker Hub:  taqatechno/odoo:19.0-enterprise   (pre-built base image)
             taqatechno/odoo:18.0-enterprise
             taqatechno/odoo:17.0-enterprise
             ...

Workspace:
  sources/odoo-19/          <-- Odoo Enterprise source (git clone, mounted read-only)
  projects/relief_center/   <-- Custom modules (git clone, mounted read-only)
  compose/relief_center.yml <-- Per-project Docker Compose
  conf/relief_center.conf   <-- Per-project Odoo config

One image --> Many containers. No rebuilding per project.
```

### Key Design Decisions

1. **Source code is NOT baked into the image** — mounted at runtime via Docker volumes:
   - No image rebuild when source changes
   - Same image serves all projects on the same Odoo version
   - Source mounted read-only (`:ro`) to prevent accidental modification

2. **Two deployment models** coexist:
   - **Standalone workspaces** (`docker/odoo-14/` through `docker/odoo-19/`) — each version has its own Dockerfile, docker-compose, and entrypoint. Build locally.
   - **Centralized workspace** (`docker/architecture/odoo-workspace/`) — all projects share pre-built images from Docker Hub. No local building needed.

3. **Container isolation** — each project gets:
   - Its own Docker network (`{project}_{version}_net`)
   - Its own named volumes for database and filestore
   - Its own port mappings (configurable via `.env`)

### Container Directory Structure

```
/opt/odoo/source/           <-- Odoo source (mounted, read-only)
/opt/odoo/custom-addons/    <-- Custom modules (mounted)
/etc/odoo/odoo.conf         <-- Configuration (mounted, read-only)
/var/log/odoo/              <-- Log files (mounted)
/var/lib/odoo/              <-- Filestore + compiled assets (named volume)
/home/odoo/                 <-- Home directory for odoo user
```

### Exposed Ports

| Port | Purpose |
|------|---------|
| **8069** | HTTP — Odoo web interface |
| **8072** | Gevent/Longpolling — WebSocket, live chat, bus |
| **5678** | Remote debugger (debugpy, optional) |

---

## 3. Version Matrix

| Version | Python Base Image | Debian | PostgreSQL | Node.js/rtlcss | wkhtmltopdf | Gevent Key | Entry Point |
|---------|-------------------|--------|------------|----------------|-------------|------------|-------------|
| **14** | python:3.8-slim-buster | Buster (10) | 12 | No | 0.12.6-1 buster | `longpolling_port` | `odoo-bin` |
| **15** | python:3.9-slim-bullseye | Bullseye (11) | 12 | No | 0.12.6.1-3 bullseye | `longpolling_port` | `odoo-bin` |
| **16** | python:3.10-slim-bullseye | Bullseye (11) | 12 | No | 0.12.6.1-3 bullseye | `longpolling_port` | `odoo-bin` |
| **17** | python:3.10-slim-bookworm | Bookworm (12) | 12 | Yes (v20 LTS) | 0.12.6.1-3 bookworm | `gevent_port` | `odoo-bin` |
| **18** | python:3.11-slim-bookworm | Bookworm (12) | 15 | Yes (v20 LTS) | 0.12.6.1-3 bookworm | `gevent_port` | `odoo-bin` |
| **19** | python:3.12-slim-bookworm | Bookworm (12) | 15 | Yes (v20 LTS) | 0.12.6.1-3 bookworm | `gevent_port` | `setup/odoo` |

### CI/CD Build Matrix

| Version | Python | Platforms |
|---------|--------|-----------|
| 14 | 3.10 | linux/amd64, linux/arm64 |
| 15 | 3.10 | linux/amd64, linux/arm64 |
| 16 | 3.10 | linux/amd64, linux/arm64 |
| 17 | 3.12 | linux/amd64, linux/arm64 |
| 18 | 3.12 | linux/amd64, linux/arm64 |
| 19 | 3.12 | linux/amd64, linux/arm64 |

### Version-Specific Dependencies

| Version | Extra Packages |
|---------|---------------|
| 14 | Mako, libev-dev, `fonts-noto` (not `fonts-noto-core`) |
| 15 | cryptography, pyopenssl |
| 17 | geoip2, rjsmin, libev-dev |
| 18 | cbor2 (may need Rust), asn1crypto, openpyxl |
| 19 | python-magic (`libmagic1`), lxml-html-clean |

### PostgreSQL Version Mapping (for docker-compose generation)

| Odoo Version | PostgreSQL Image | Gevent Config Key |
|-------------|-----------------|-------------------|
| 14 | postgres:12 | longpolling_port |
| 15 | postgres:12 | longpolling_port |
| 16 | postgres:12 | longpolling_port |
| 17 | postgres:15 | gevent_port |
| 18 | postgres:15 | gevent_port |
| 19 | postgres:15 | gevent_port |

---

## 4. Base Docker Image

**Published to:** `taqatechno/odoo:{VERSION}.0-enterprise`

### What the Image Provides

- System dependencies (postgres libs, XML, image processing, fonts)
- Python runtime with all Odoo packages pre-installed
- wkhtmltopdf 0.12.6 for PDF generation
- Node.js 20 LTS + rtlcss for RTL/Arabic text support
- Non-root `odoo` user (uid 1000, gid 1000)
- Entrypoint supporting both `odoo-bin` (v14-18) and `setup/odoo` (v19)

### What the Image Does NOT Contain

- Odoo source code — mount at `/opt/odoo/source`
- Custom project modules — mount at `/opt/odoo/custom-addons`
- Configuration files — mount at `/etc/odoo/odoo.conf`

### System Dependencies

```
# Database
libpq-dev, postgresql-client

# Image Processing (Pillow)
libpng-dev, libjpeg-dev, libwebp-dev, libtiff-dev, libopenjp2-7-dev

# XML / XSLT
libxml2-dev, libxslt1-dev

# LDAP / SASL
libldap2-dev, libsasl2-dev

# Build Tools
build-essential, gcc

# Fonts (PDF + multilingual)
fonts-noto-core, fonts-noto-cjk, fontconfig

# wkhtmltopdf native deps
libjpeg62-turbo, libxrender1, libfontconfig1, libxext6, xfonts-75dpi, xfonts-base

# Misc
libssl-dev, tzdata, curl, wget
```

### Dockerfile Template (Base Image)

```dockerfile
ARG PYTHON_VERSION=3.12
ARG ODOO_VERSION=19

FROM python:${PYTHON_VERSION}-slim-bookworm

# System deps, wkhtmltopdf, Node.js, rtlcss...
RUN groupadd -g 1000 odoo \
    && useradd -u 1000 -g odoo -m -d /home/odoo -s /bin/bash odoo

RUN mkdir -p /opt/odoo/source /opt/odoo/custom-addons \
    /var/log/odoo /var/lib/odoo /etc/odoo \
    && chown -R odoo:odoo /opt/odoo /var/log/odoo /var/lib/odoo /etc/odoo

COPY requirements-${ODOO_VERSION}.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY entrypoint.sh /opt/odoo/entrypoint.sh
RUN chmod +x /opt/odoo/entrypoint.sh

USER odoo
WORKDIR /opt/odoo/source
EXPOSE 8069 8072
ENTRYPOINT ["/opt/odoo/entrypoint.sh"]
CMD ["-c", "/etc/odoo/odoo.conf"]
```

---

## 5. Entrypoint Script

The universal entrypoint handles startup logic for all Odoo versions.

### Features

| Feature | Environment Variable | Default | Behavior |
|---------|---------------------|---------|----------|
| Source validation | — | — | Checks `/opt/odoo/source` for `odoo-bin` or `setup/odoo`; exits with error if missing |
| PYTHONPATH setup | — | — | `export PYTHONPATH=/opt/odoo/source` (avoids slow editable install) |
| Entry point auto-detect | — | — | Uses `setup/odoo` if exists (v19), else `odoo-bin` (v14-18) |
| Development mode | `DEV_MODE` | `0` | When `1`, appends `--dev=all` for auto-reload |
| Remote debugger | `ENABLE_DEBUGGER` | `0` | When `1`, starts debugpy on port 5678, waits for IDE |

### Universal Entrypoint Script

```bash
#!/bin/bash
set -e

# Validate Odoo source is mounted
if [ ! -f "/opt/odoo/source/setup/odoo" ] && [ ! -f "/opt/odoo/source/odoo-bin" ]; then
    echo "ERROR: Odoo source not found at /opt/odoo/source"
    exit 1
fi

# PYTHONPATH — avoids slow editable install
export PYTHONPATH=/opt/odoo/source:${PYTHONPATH:-}

# Auto-detect entry point
if [ -f "/opt/odoo/source/setup/odoo" ]; then
    ODOO_BIN="python /opt/odoo/source/setup/odoo"
else
    ODOO_BIN="python /opt/odoo/source/odoo-bin"
fi

# Dev mode
if [ "${DEV_MODE:-0}" = "1" ]; then
    set -- "$@" --dev=all
    echo "[entrypoint] DEV_MODE enabled: --dev=all"
fi

# Remote debugger
if [ "${ENABLE_DEBUGGER:-0}" = "1" ]; then
    pip install --user --quiet debugpy 2>/dev/null || true
    echo "[entrypoint] Debugger enabled: waiting for IDE on port 5678..."
    exec python -m debugpy --listen 0.0.0.0:5678 --wait-for-client \
        /opt/odoo/source/setup/odoo "$@"
fi

echo "[entrypoint] Starting Odoo..."
exec $ODOO_BIN "$@"
```

### Odoo 19 Standalone Variant

```bash
#!/bin/bash
set -e
# v19 needs editable install (no __init__.py at root)
pip install --user --no-deps -e /opt/odoo/source 2>/dev/null
exec python /opt/odoo/source/setup/odoo "$@"
```

---

## 6. Docker Compose Patterns

### 6.1 Development Compose (Standalone)

```yaml
services:
  db:
    image: postgres:15
    container_name: odoo19_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-odoo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-odoo}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}
    volumes:
      - odoo19_db_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-odoo}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  odoo:
    build: .
    container_name: odoo19_web
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/opt/odoo/source:ro
      - ./projects:/opt/odoo/custom-addons
      - ./conf/odoo.conf:/etc/odoo/odoo.conf:ro
      - ./logs:/var/log/odoo
      - odoo19_filestore:/var/lib/odoo/filestore
    ports:
      - "8069:8069"
      - "8072:8072"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-odoo}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-odoo}
    restart: unless-stopped

volumes:
  odoo19_db_data:
  odoo19_filestore:
```

### 6.2 Centralized Workspace Compose

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: relief_center_19_db
    volumes:
      - relief_center_19_db:/var/lib/postgresql/data
    networks:
      - relief_center_19_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-odoo}"]

  odoo:
    image: taqatechno/odoo:19.0-enterprise
    container_name: relief_center_19_web
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ${WORKSPACE_ROOT}/sources/odoo-19:/opt/odoo/source:ro
      - ${WORKSPACE_ROOT}/projects/relief_center:/opt/odoo/custom-addons/relief_center:ro
      - ${WORKSPACE_ROOT}/conf/relief_center.conf:/etc/odoo/odoo.conf:ro
      - relief_center_19_filestore:/var/lib/odoo
      - ${WORKSPACE_ROOT}/logs/relief_center:/var/log/odoo
    ports:
      - "${RELIEF_CENTER_HTTP_PORT:-8069}:8069"
      - "${RELIEF_CENTER_GEVENT_PORT:-8072}:8072"
    environment:
      DEV_MODE: ${DEV_MODE:-0}
      ENABLE_DEBUGGER: ${ENABLE_DEBUGGER:-0}
    networks:
      - relief_center_19_net
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:8069/web/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  relief_center_19_db:
  relief_center_19_filestore:

networks:
  relief_center_19_net:
    driver: bridge
```

### 6.3 Production Compose (With Nginx)

```yaml
services:
  db:
    image: postgres:16
    command:
      - "postgres"
      - "-c" "shared_buffers=256MB"
      - "-c" "work_mem=16MB"
      - "-c" "maintenance_work_mem=128MB"
      - "-c" "effective_cache_size=512MB"
      - "-c" "max_connections=100"
      - "-c" "checkpoint_completion_target=0.9"
      - "-c" "wal_buffers=16MB"
      - "-c" "random_page_cost=1.1"
    shm_size: '256m'
    deploy:
      resources:
        limits: { memory: 1G, cpus: '1.0' }
        reservations: { memory: 256M }

  odoo:
    image: taqatechno/odoo:{VERSION}.0-enterprise
    expose:
      - "8069"
      - "8072"
    # NOT exposed to host — nginx is the public-facing endpoint
    deploy:
      resources:
        limits: { memory: 2G, cpus: '2.0' }
        reservations: { memory: 512M }

  nginx:
    image: nginx:alpine
    volumes:
      - ./conf/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "8069:80"
    depends_on:
      odoo:
        condition: service_healthy

  warmup:
    image: curlimages/curl:latest
    depends_on:
      odoo: { condition: service_healthy }
    command: |
      curl -sf http://odoo:8069/web/login > /dev/null 2>&1 || true
      curl -sf http://odoo:8069/shop > /dev/null 2>&1 || true
    restart: "no"
```

---

## 7. Odoo Configuration for Docker

### Full Configuration Template

```ini
[options]
; --- Database ---
db_host = db                                ; Docker service name (DNS resolution)
db_port = 5432                              ; Standard PostgreSQL port
db_user = odoo
db_password = odoo
db_name = {project_name}                    ; Default database
admin_passwd = changeme_in_production       ; Master password

; --- Addons ---
addons_path = /opt/odoo/source/odoo/addons,/opt/odoo/custom-addons/{project_name}

; --- Network ---
http_port = 8069
http_interface = 0.0.0.0                    ; Listen on all interfaces
gevent_port = 8072                          ; v17+ (use longpolling_port for v14-16)

; --- Database Filtering ---
dbfilter = {project_name}.*                 ; Prevents cross-project DB access
list_db = True                              ; Set False for production

; --- Data & Logging ---
data_dir = /var/lib/odoo                    ; CRITICAL: filestore + compiled assets
logfile = /var/log/odoo/odoo.log
log_level = info

; --- Performance ---
workers = 0                                 ; Dev: single-threaded. Prod: 2-4
max_cron_threads = 1
db_maxconn = 16                             ; Connection pool per worker
limit_time_cpu = 600
limit_time_real = 1200
limit_memory_soft = 2147483648              ; 2 GB
limit_memory_hard = 2684354560              ; 2.5 GB

; --- Security ---
proxy_mode = False                          ; Set True when behind nginx
```

### Critical Configuration Notes

| Setting | Why It Matters |
|---------|---------------|
| `data_dir = /var/lib/odoo` | **CRITICAL.** Without this, filestore defaults to `~/.local/share/Odoo/` (ephemeral). JS assets return HTTP 500. Pages load without JavaScript. |
| `workers = 0` | Single-threaded mode. OK for dev, UNUSABLE for production. At 50 users, response time is 10+ seconds. |
| `proxy_mode = True` | Required when behind nginx. Without it, IP logging and URL generation are incorrect. |
| `list_db = False` | Production security. Prevents database name enumeration via `/web/database/selector`. |
| `gevent_port` vs `longpolling_port` | v14-16 use `longpolling_port`. v17+ use `gevent_port`. Wrong key = WebSocket broken. |

---

## 8. Nginx Reverse Proxy

### Complete Nginx Configuration

```nginx
# Rate limiting: 10 requests/second per IP, burst 20
limit_req_zone $binary_remote_addr zone=odoo_limit:10m rate=10r/s;

upstream odoo {
    server odoo:8069;
}

upstream odoo-websocket {
    server odoo:8072;
}

server {
    listen 80;
    server_name _;

    # --- Proxy Buffering ---
    proxy_buffers 16 64k;
    proxy_buffer_size 128k;
    proxy_busy_buffers_size 128k;

    # --- Gzip Compression (90% CSS reduction) ---
    gzip on;
    gzip_types text/plain text/css text/javascript text/xml
               application/javascript application/json application/xml
               application/xml+rss image/svg+xml font/woff2;
    gzip_min_length 256;
    gzip_comp_level 6;
    gzip_vary on;
    gzip_proxied any;
    gzip_static on;

    # --- Upload Limit ---
    client_max_body_size 200m;

    # --- Timeouts ---
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    proxy_read_timeout 600;
    send_timeout 600;

    # --- Proxy Headers ---
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # --- WebSocket (live chat, bus) ---
    location /websocket {
        proxy_pass http://odoo-websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # --- Static Asset Caching ---
    location ~* /web/assets/ {
        proxy_pass http://odoo;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    location ~* /web/static/ {
        proxy_pass http://odoo;
        expires 7d;
        add_header Cache-Control "public";
    }

    # --- Health Check (no rate limiting) ---
    location = /web/health {
        proxy_pass http://odoo;
    }

    # --- All Other Requests (rate limited) ---
    location / {
        limit_req zone=odoo_limit burst=20 nodelay;
        proxy_pass http://odoo;
        proxy_redirect off;
    }
}
```

### Performance Impact (Verified via Stress Tests)

| Metric | Without Nginx | With Nginx (gzip level 6) | Improvement |
|--------|---------------|---------------------------|-------------|
| CSS bundle size | 894 KB | 89 KB | **90% reduction** |
| `/web/login` transfer | 65,790 bytes | 4,376 bytes | **93% reduction** |
| Homepage TTFB | 176 ms | 53 ms | **70% faster** |

### SSL/TLS Configuration (Production)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... (same location blocks as above)
}
```

---

## 9. Environment Variables

### Standard `.env` Template

```env
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo
POSTGRES_DB=postgres
DEV_MODE=0
ENABLE_DEBUGGER=0
WAIT_FOR_DB=0
LOG_LEVEL=info
ODOO_EXTRA_ARGS=
```

### Entrypoint Variables

| Variable | Default | Values | Purpose |
|----------|---------|--------|---------|
| `DEV_MODE` | `0` | `0`, `1` | Enables `--dev=all` for auto-reload on file changes |
| `ENABLE_DEBUGGER` | `0` | `0`, `1` | Starts debugpy on port 5678, waits for IDE attach |
| `WAIT_FOR_DB` | `0` | `0`, `1` | Waits up to 30s for PostgreSQL before starting |
| `LOG_LEVEL` | (none) | `debug`, `info`, `warn`, `error`, `critical` | Overrides odoo.conf log level |
| `ODOO_EXTRA_ARGS` | (none) | Any CLI args | Passed directly to Odoo (e.g., `--test-enable`) |

### Multi-Project Port Variables

```env
RELIEF_CENTER_HTTP_PORT=8069
RELIEF_CENTER_GEVENT_PORT=8072
RELIEF_CENTER_DEBUG_PORT=5678

SOQYA_HTTP_PORT=8169
SOQYA_GEVENT_PORT=8172
SOQYA_DEBUG_PORT=5679
```

### Port Allocation Convention

| Port | Calculation | Example (8069) | Example (8169) |
|------|-------------|----------------|----------------|
| HTTP | `HTTP_PORT` | 8069 | 8169 |
| Gevent | `HTTP_PORT + 3` | 8072 | 8172 |
| Debug | `HTTP_PORT + 609` | 8678 | 8778 |

---

## 10. Production Deployment

### Minimum Production Configuration

```ini
[options]
workers = 2                    ; Minimum for production (4 for heavy load)
max_cron_threads = 1
db_maxconn = 16
data_dir = /var/lib/odoo       ; CRITICAL
proxy_mode = True              ; Required behind nginx
list_db = False                ; Security
admin_passwd = <strong-32-char-password>
```

### Production Docker Compose Additions

```yaml
services:
  db:
    command:
      - "postgres"
      - "-c" "shared_buffers=256MB"
      - "-c" "work_mem=16MB"
      - "-c" "maintenance_work_mem=128MB"
      - "-c" "effective_cache_size=512MB"
      - "-c" "checkpoint_completion_target=0.9"
    shm_size: '256m'
    deploy:
      resources:
        limits: { memory: 1G, cpus: '1.0' }
        reservations: { memory: 256M }

  odoo:
    deploy:
      resources:
        limits: { memory: 2G, cpus: '2.0' }
        reservations: { memory: 512M }
```

### Updating Source (Zero Downtime)

```bash
# Pull latest Odoo source (no rebuild needed)
git -C sources/odoo-19 pull

# Restart containers
./scripts/stop.sh relief_center
./scripts/start.sh relief_center
```

### Upgrading Base Image

```bash
docker pull taqatechno/odoo:19.0-enterprise
./scripts/stop.sh relief_center
./scripts/start.sh relief_center
# Containers use new image on next up
```

---

## 11. Performance Tuning

### Workers Configuration

| Setting | Response at 50 Users | Use Case |
|---------|---------------------|----------|
| `workers=0` | P50 = 9,068ms, 10% errors | **Dev only** — single-threaded |
| `workers=2` | P50 ~ 800ms | Minimum production |
| `workers=4` | P50 ~ 400ms | Heavy load (8+ concurrent users) |

**Formula:** `workers = (CPU cores * 2) + 1` (capped at available RAM / 512MB per worker)

### data_dir Impact

| Configuration | Asset Load Time | JavaScript |
|---------------|----------------|------------|
| **Without** `data_dir` | 19-49 seconds (cold) | HTTP 500 errors |
| **With** `data_dir = /var/lib/odoo` | 2-3 seconds | Works correctly |

### PostgreSQL Tuning

| Setting | Default | Recommended (4 GB RAM) | Recommended (16 GB RAM) |
|---------|---------|------------------------|-------------------------|
| `shared_buffers` | 128 MB | 1 GB | 4 GB |
| `work_mem` | 4 MB | 16 MB | 32 MB |
| `effective_cache_size` | 4 GB | 3 GB | 12 GB |
| `maintenance_work_mem` | 64 MB | 128 MB | 512 MB |
| `random_page_cost` | 4.0 | 1.1 | 1.1 |
| `checkpoint_completion_target` | 0.5 | 0.9 | 0.9 |

### Connection Pool Management

- Set `db_maxconn = 16` per worker to prevent pool exhaustion
- Monitor: `SELECT state, count(*) FROM pg_stat_activity GROUP BY state;`
- Risk: Without limits, 50+ idle connections accumulate under stress

### Asset Warm-Up

After container restart, first request compiles all assets (25-120 seconds). Use a warm-up service:

```yaml
warmup:
  image: curlimages/curl:latest
  depends_on:
    odoo: { condition: service_healthy }
  command: |
    curl -sf http://odoo:8069/web/login > /dev/null 2>&1 || true
    curl -sf http://odoo:8069/shop > /dev/null 2>&1 || true
  restart: "no"
```

### Gzip Compression

| Configuration | CSS Size | Reduction |
|---------------|----------|-----------|
| Dev (Werkzeug, no gzip) | 894 KB | — |
| Prod (nginx, gzip level 6) | 89 KB | **90%** |

---

## 12. Security Hardening

### High-Risk Issues (Fix Before Production)

| Issue | Default | Fix |
|-------|---------|-----|
| Database enumeration | `list_db = True` | `list_db = False` |
| Weak master password | `admin_passwd = 123` | Strong 32+ character password |
| No SSL/TLS | Plaintext HTTP | Nginx + Let's Encrypt (Certbot) |
| Default DB credentials | `odoo` / `odoo` | Custom credentials per environment |
| Proxy mode disabled | `proxy_mode = False` | `proxy_mode = True` behind nginx |

### Volume Security

- Odoo source: Always mount `:ro` (read-only)
- Config files: Always mount `:ro`
- Filestore and logs: Read-write (necessary for operation)

### Network Isolation

- Each project gets its own Docker network
- Database containers are NOT exposed to host in production
- Only nginx exposes ports to the outside

---

## 13. Database Management in Docker

### Create Database via API

```bash
curl -s -X POST http://localhost:8069/web/database/create \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "master_pwd": "123",
      "name": "my_database",
      "lang": "en_US",
      "password": "admin",
      "login": "admin",
      "country_code": "US"
    }
  }'
```

### Database Access from Host

PostgreSQL exposed on port 5433 (host) → 5432 (container):

```bash
psql -h localhost -p 5433 -U odoo -d my_database
```

### Interactive Odoo Shell

```bash
docker exec -it relief_center_19_web bash
python /opt/odoo/source/setup/odoo shell -d my_database -c /etc/odoo/odoo.conf
```

```python
>>> self.env['res.partner'].search([])
>>> self.env.user
>>> self.env.cr.execute("SELECT count(*) FROM res_partner")
```

### Backup and Restore

```bash
# Backup
docker exec relief_center_19_db pg_dump -U odoo my_database > backup.sql

# Restore
docker exec -i relief_center_19_db psql -U odoo -d my_database < backup.sql
```

---

## 14. Debugging & Development

### Dev Mode (Auto-Reload)

```bash
# Via environment variable
DEV_MODE=1 docker compose -f compose/relief_center.yml up -d

# Via script
./scripts/start.sh relief_center --dev
```

### Remote Debugger (debugpy)

1. Enable in `.env`: `ENABLE_DEBUGGER=1`
2. Expose port in docker-compose: `- "5678:5678"`
3. Start container — waits for IDE attach
4. VS Code launch configuration:
```json
{
  "name": "Attach to Odoo Docker",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "localhost", "port": 5678 },
  "pathMappings": [
    { "localRoot": "${workspaceFolder}", "remoteRoot": "/opt/odoo/source" }
  ]
}
```

### Module Management Inside Container

```bash
# Update module after code changes
python -m odoo -c /etc/odoo/odoo.conf -d my_db -u my_module --stop-after-init

# Install new module
python -m odoo -c /etc/odoo/odoo.conf -d my_db -i my_module --stop-after-init

# Run tests
python odoo-bin -c /etc/odoo/odoo.conf -d my_db --test-enable -i my_module --stop-after-init
```

---

## 15. CI/CD Pipeline

### GitHub Actions Workflow

- **Triggers:** Push to `main` (Dockerfile/entrypoint/requirements changes) or manual dispatch
- **Matrix:** Builds all 6 versions in parallel
- **Multi-platform:** `linux/amd64` + `linux/arm64`
- **Cache:** GitHub Actions layer cache per version
- **Tags:** `taqatechno/odoo:{version}.0-enterprise` + `taqatechno/odoo:{version}.0-enterprise-{sha}`

### Required Secrets

| Secret | Purpose |
|--------|---------|
| `DOCKERHUB_USERNAME` | Docker Hub login (taqatechno) |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

### Manual Version Build

GitHub Actions > "Build & Push Odoo Base Images" > Run workflow > Select version (14-19 or "all").

### GitHub Actions Workflow Template

```yaml
name: Build & Push Odoo Base Images
on:
  push:
    branches: [main]
    paths:
      - 'Dockerfile'
      - 'entrypoint.sh'
      - 'requirements-*.txt'
  workflow_dispatch:
    inputs:
      version:
        description: 'Odoo version to build (14-19 or all)'
        required: true
        default: 'all'

jobs:
  build:
    strategy:
      matrix:
        include:
          - version: "14"
            python: "3.10"
          - version: "15"
            python: "3.10"
          - version: "16"
            python: "3.10"
          - version: "17"
            python: "3.12"
          - version: "18"
            python: "3.12"
          - version: "19"
            python: "3.12"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          platforms: linux/amd64,linux/arm64
          build-args: |
            PYTHON_VERSION=${{ matrix.python }}
            ODOO_VERSION=${{ matrix.version }}
          tags: |
            taqatechno/odoo:${{ matrix.version }}.0-enterprise
            taqatechno/odoo:${{ matrix.version }}.0-enterprise-${{ github.sha }}
          cache-from: type=gha,scope=odoo-${{ matrix.version }}
          cache-to: type=gha,mode=max,scope=odoo-${{ matrix.version }}
```

---

## 16. Centralized Multi-Project Workspace

### Workspace Layout

```
~/odoo-docker/
├── sources/                     <-- Git clones of Odoo Enterprise
│   ├── odoo-17/
│   ├── odoo-18/
│   └── odoo-19/
├── projects/                    <-- Git clones of custom modules
│   ├── relief_center/
│   └── soqya/
├── conf/                        <-- Generated Odoo configs
├── compose/                     <-- Generated Docker Compose files
├── logs/                        <-- Runtime logs
├── scripts/
│   ├── init-project.sh          # Initialize new project
│   ├── start.sh                 # Start containers
│   ├── stop.sh                  # Stop containers
│   ├── logs.sh                  # Tail logs
│   ├── shell.sh                 # Bash into container
│   └── pull-sources.sh          # Update all git repos
├── .env                         # Global config
└── .env.local                   # Machine-specific overrides
```

### Adding a New Project

```bash
# 1. Clone project modules
git clone git@github.com:taqat-techno/relief_center.git projects/relief_center

# 2. Initialize (generates conf + docker-compose)
./scripts/init-project.sh relief_center 19 8069

# 3. Start
./scripts/start.sh relief_center
```

### Daily Developer Commands

```bash
./scripts/start.sh <project>            # Start containers
./scripts/start.sh <project> --dev      # Start with auto-reload
./scripts/stop.sh <project>             # Stop containers
./scripts/logs.sh <project>             # Odoo logs (default)
./scripts/logs.sh <project> db          # Database logs
./scripts/shell.sh <project> 19         # Bash into container
./scripts/pull-sources.sh               # Update all git repos
```

### Running Multiple Projects Simultaneously

Assign unique ports per project in `.env`:

```env
RELIEF_CENTER_HTTP_PORT=8069
SOQYA_HTTP_PORT=8169
TAQAT_HTTP_PORT=8269
```

---

## 17. Build Workarounds & Known Issues

### Odoo 14 — Buster EOL

Debian Buster is end-of-life. Dockerfile must use archive mirrors:

```dockerfile
RUN sed -i 's/deb.debian.org/archive.debian.org/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/archive.debian.org/g' /etc/apt/sources.list \
    && sed -i '/buster-updates/d' /etc/apt/sources.list \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until
```

### Odoo 14-15 — gevent + greenlet Compilation

```dockerfile
RUN pip install --no-cache-dir "setuptools<81" "Cython<3" wheel \
    && pip install --no-cache-dir --no-build-isolation greenlet==0.4.17 gevent==20.9.0
```

### Odoo 16-17 — gevent Compilation

```dockerfile
RUN pip install --no-cache-dir "Cython<3" wheel \
    && pip install --no-cache-dir --no-build-isolation gevent==21.8.0
```

### Odoo 18 — cbor2 Build

cbor2 may need Rust compiler. Try pip first, add Rust only if needed:

```dockerfile
ENV PIP_CONSTRAINT="setuptools<81"
RUN pip install --no-cache-dir -r requirements.txt
```

### Odoo 19 — No `__init__.py` at Root

`import odoo` fails without either:
- `pip install --user --no-deps -e /opt/odoo/source` (editable install)
- `export PYTHONPATH=/opt/odoo/source` (base image approach)

### Odoo 19 — New Entry Point

v19 uses `setup/odoo` instead of `odoo-bin`:

```bash
# v14-18
python /opt/odoo/source/odoo-bin -c /etc/odoo/odoo.conf

# v19
python /opt/odoo/source/setup/odoo -c /etc/odoo/odoo.conf
```

### setuptools 80+ Breaking Change

setuptools 80+ removed `pkg_resources` used by older packages:

```dockerfile
ENV PIP_CONSTRAINT="setuptools<81"
```

### wkhtmltopdf Version Differences

| Debian | wkhtmltopdf URL |
|--------|----------------|
| Buster | `wkhtmltox_0.12.6-1.buster_amd64.deb` (0.12.6.1-3 was removed) |
| Bullseye | `wkhtmltox_0.12.6.1-3.bullseye_amd64.deb` |
| Bookworm | `wkhtmltox_0.12.6.1-3.bookworm_amd64.deb` |

---

## 18. Stress Test Findings

**Source:** Al Majal Al Maktabi (Odoo 17 Enterprise), 59 MB database, 3 custom modules.

### Critical Issues Found

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | `workers=0` serializes ALL requests | 10s P50 at 50 users; 10% HTTP 500 | `workers=2` minimum |
| 2 | Missing `data_dir` | JS assets return 500; forms non-functional | `data_dir = /var/lib/odoo` |
| 3 | No gzip in dev mode | 894 KB raw CSS per page load | Use nginx (90% reduction) |
| 4 | 51 idle DB connections after stress | Pool exhaustion risk | `db_maxconn=16` |

### Response Time Scaling (workers=0)

```
/shop P50:  127ms (1 user) → 751ms (5) → 1,604ms (10) → 3,668ms (25) → 9,068ms (50)
                                                                                ~71x slower
```

### Memory Behavior

| Metric | Value |
|--------|-------|
| At rest | 227.6 MB |
| Peak (50 users) | 234.8 MB |
| After cool-down | 231.7 MB |
| Growth | +4.1 MB (+1.8%) |
| Memory leak? | **No** |

### Database Sequential Scan Issues

7 core tables had **zero index scans** — all access via sequential scan. Acceptable for small datasets, will degrade as data grows.

---

## 19. Troubleshooting Reference

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8069
taskkill /PID {PID} /F

# Linux/Mac
lsof -ti:8069 | xargs kill -9

# Or change port in .env and restart
```

### Container Won't Start — Source Not Mounted

```bash
./scripts/logs.sh relief_center
# Look for: "ERROR: Odoo source not found at /opt/odoo/source"
ls sources/odoo-19/setup/odoo  # Verify source exists
```

### Database Connection Error

```bash
docker ps | grep relief_center_19_db    # Is DB container running?
./scripts/logs.sh relief_center db       # Check DB logs
```

### Module Not Found

```bash
docker exec relief_center_19_web ls /opt/odoo/custom-addons/
cat conf/relief_center.conf | grep addons_path
```

### JavaScript Assets Return HTTP 500

**Cause:** Missing `data_dir` in `odoo.conf`.
**Fix:** Add `data_dir = /var/lib/odoo` and restart.

### Changes Not Reflecting

1. Update module: `python -m odoo -c /etc/odoo/odoo.conf -d {db} -u {module} --stop-after-init`
2. Clear browser cache: Ctrl+Shift+R
3. Use `--dev=all` for auto-reload
4. For JS/CSS: may need full restart

### Container Out of Memory

```yaml
deploy:
  resources:
    limits: { memory: 2G, cpus: '2' }
```

### 502 Bad Gateway (Nginx)

1. Check Odoo container is running: `docker ps`
2. Check Odoo health: `docker exec {container} curl -sf http://localhost:8069/web/health`
3. Check nginx upstream: `docker logs {nginx_container}`
4. Verify `proxy_mode = True` in odoo.conf

### No Space Left on Device

```bash
docker system prune -af --volumes  # WARNING: removes all unused data
docker system df                    # Check what's using space
```

---

## 20. Quick Command Reference

### Container Lifecycle

```bash
# Build local image (standalone)
docker-compose build

# Pull pre-built image (centralized)
docker pull taqatechno/odoo:19.0-enterprise

# Start / Stop
docker-compose -f docker-compose.{project}.yml up -d
docker-compose -f docker-compose.{project}.yml down

# Stop + remove volumes (DESTROYS DATA)
docker-compose -f docker-compose.{project}.yml down -v

# Logs / Shell
docker-compose -f docker-compose.{project}.yml logs -f odoo
docker-compose -f docker-compose.{project}.yml exec odoo bash
```

### Module Management (Inside Container)

```bash
python -m odoo -c /etc/odoo/odoo.conf -d {db} -u {module} --stop-after-init
python -m odoo -c /etc/odoo/odoo.conf -d {db} -i {module} --stop-after-init
python odoo-bin -c /etc/odoo/odoo.conf -d {db} --test-enable -i {module} --stop-after-init
```

---

## 21. Commands Reference

This skill provides the following slash commands:

| Command | Description |
|---------|-------------|
| `/docker-deploy` | Generate production deployment (nginx, SSL, workers, resource limits) |
| `/docker-build` | Build and push Docker images (single version or all) |
| `/docker-init-project` | Interactive project setup with auto-detection |
| `/docker-perf` | Performance analysis and tuning recommendations |
| `/docker-compose-gen` | Generate docker-compose for any scenario |
| `/docker-debug` | Systematic container troubleshooting |
| `/docker-nginx` | Generate optimized nginx configuration |
