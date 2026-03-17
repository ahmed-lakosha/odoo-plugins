# odoo-docker Plugin

> **v2.0.0** — Consolidated architecture with unified command + natural language triggers

Docker infrastructure manager for Odoo — production deployment, nginx proxy, CI/CD pipelines, performance tuning, multi-version image management, and container debugging for Odoo 14-19 Enterprise.

## Installation

Add to your Claude Code settings:
```json
{
  "odoo-docker@plugins": true
}
```

## Command

v2.0 consolidates all functionality into a single command with sub-commands:

| Command | Description |
|---------|-------------|
| `/odoo-docker` | Unified Docker infrastructure command |

### Sub-Commands

| Sub-Command | Description |
|-------------|-------------|
| `/odoo-docker deploy` | Generate production deployment (nginx, SSL, workers, resource limits) |
| `/odoo-docker build` | Build and push Docker images (single version or all) |
| `/odoo-docker init` | Interactive project setup with auto-detection |
| `/odoo-docker compose` | Generate docker-compose for dev/staging/production |

## Natural Language Triggers

In addition to the `/odoo-docker` command, the skill responds to natural language requests for nginx, debugging, and performance tuning. No slash command needed — just describe what you need:

| Category | Example Prompts |
|----------|----------------|
| **Nginx** | "Generate nginx config for my Odoo Docker setup", "Add reverse proxy with SSL" |
| **Debugging** | "My Odoo container keeps restarting", "Help me debug Docker 500 errors" |
| **Performance** | "Analyze and tune my Odoo Docker performance", "Optimize workers and PostgreSQL" |
| **Build** | "Build Docker image for Odoo 17 with my custom modules" |
| **Deploy** | "Deploy my Odoo 17 project to production using Docker" |

## Migration from v1.x

v1.x had 7 separate slash commands (`/docker-deploy`, `/docker-build`, `/docker-init-project`, `/docker-perf`, `/docker-compose-gen`, `/docker-debug`, `/docker-nginx`). In v2.0:

- **`/docker-deploy`** → `/odoo-docker deploy`
- **`/docker-build`** → `/odoo-docker build`
- **`/docker-init-project`** → `/odoo-docker init`
- **`/docker-compose-gen`** → `/odoo-docker compose`
- **`/docker-perf`** → Natural language: "Analyze my Docker performance"
- **`/docker-debug`** → Natural language: "Debug my Odoo container"
- **`/docker-nginx`** → Natural language: "Generate nginx config for Odoo"

## Relationship with odoo-service

This plugin complements `odoo-service`:

| Use `odoo-service` for... | Use `odoo-docker` for... |
|---|---|
| Start/stop server | Production deployment |
| Basic docker up/down/logs | Nginx reverse proxy |
| Database backup/restore | CI/CD pipelines |
| IDE configuration | Performance tuning |
| Environment init | Container debugging |

## Key Features

- **Production Deployment**: nginx with gzip (90% CSS reduction), PostgreSQL tuning, resource limits, warm-up services
- **Performance Analysis**: Data-driven recommendations from real stress tests (workers=0 → 10s P50 at 50 users)
- **Multi-Version Support**: Odoo 14-19 with version-specific build workarounds (Buster EOL, gevent compilation, cbor2)
- **CI/CD**: GitHub Actions multi-platform builds (amd64 + arm64)
- **Templates**: Proven docker-compose, nginx, Dockerfile, and config templates
- **Troubleshooting**: Systematic debugging with known issue patterns and auto-suggested fixes

## Architecture

```
One base image → Many containers → No rebuilding per project

taqatechno/odoo:19.0-enterprise  (pre-built, published to Docker Hub)
  + source code (mounted read-only)
  + custom modules (mounted)
  + config file (mounted read-only)
  = Running Odoo container
```

## Templates Included

- `docker-compose.dev.yml` — Development
- `docker-compose.prod.yml` — Production with nginx
- `nginx.conf` — Optimized reverse proxy
- `Dockerfile.template` — Multi-version base image
- `entrypoint.sh` — Universal startup script
- `odoo.conf.template` — Docker-specific config
- `.env.template` — Environment variables

## Author

**TaqaTechno** — info@taqatechno.com
