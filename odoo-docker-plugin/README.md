# odoo-docker Plugin

Docker infrastructure manager for Odoo — production deployment, nginx proxy, CI/CD pipelines, performance tuning, multi-version image management, and container debugging for Odoo 14-19 Enterprise.

## Installation

Add to your Claude Code settings:
```json
{
  "odoo-docker@plugins": true
}
```

## Commands

| Command | Description |
|---------|-------------|
| `/docker-deploy` | Generate production deployment (nginx, SSL, workers, resource limits) |
| `/docker-build` | Build and push Docker images (single version or all) |
| `/docker-init-project` | Interactive project setup with auto-detection |
| `/docker-perf` | Performance analysis and tuning recommendations |
| `/docker-compose-gen` | Generate docker-compose for dev/staging/production |
| `/docker-debug` | Systematic container troubleshooting |
| `/docker-nginx` | Generate optimized nginx configuration |

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
