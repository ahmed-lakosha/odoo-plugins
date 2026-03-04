---
title: 'Odoo Docker Infrastructure'
read_only: true
type: 'command'
description: 'Main entry point for Docker infrastructure management — routes to production deployment, CI/CD, performance tuning, nginx, debugging, and compose generation'
---

# Odoo Docker Infrastructure Manager

Complete Docker infrastructure management for Odoo. Goes beyond basic container lifecycle to handle production deployments, nginx proxy, CI/CD pipelines, performance tuning, and systematic debugging.

## Command Overview

| Command | Description | Triggers |
|---------|-------------|---------|
| `/docker-deploy` | Production deployment with nginx | "deploy to production", "production setup" |
| `/docker-build` | Build & push Docker images | "build docker image", "push to docker hub" |
| `/docker-init-project` | Interactive project setup | "set up docker for this project", "initialize docker" |
| `/docker-perf` | Performance analysis & tuning | "optimize performance", "slow containers" |
| `/docker-compose-gen` | Generate docker-compose files | "generate docker-compose", "create compose" |
| `/docker-debug` | Container troubleshooting | "container won't start", "debug docker" |
| `/docker-nginx` | Nginx config generation | "configure nginx", "add reverse proxy" |

## Relationship with `odoo-service`

This plugin complements the `odoo-service` plugin's `/odoo-docker` command:

- **`odoo-service /odoo-docker`**: Daily lifecycle — `up`, `down`, `logs`, `shell`, `update`, `install`, `status`
- **`odoo-docker` (this plugin)**: Infrastructure — production deployment, nginx, CI/CD, performance, debugging

## Quick Start Examples

### Deploy to Production
```
/docker-deploy --version 19 --project relief_center --domain relief.taqatechno.com
```

### Analyze Performance
```
/docker-perf
# Reads your docker-compose and odoo.conf, provides recommendations
```

### Debug Container Issues
```
/docker-debug
# Systematic check: status → logs → health → network → volumes
```

### Build All Docker Images
```
/docker-build --all
# Builds and pushes taqatechno/odoo:{14-19}.0-enterprise
```

## Natural Language Triggers

- "deploy to production", "production docker setup", "deploy odoo"
- "configure nginx for odoo", "add reverse proxy", "enable gzip", "ssl setup"
- "optimize docker performance", "slow containers", "tune workers", "fix slow response"
- "build docker image", "push to docker hub", "ci/cd pipeline", "github actions"
- "container won't start", "500 errors in docker", "debug container", "troubleshoot"
- "set up docker for this project", "initialize docker environment"
- "generate docker-compose", "create compose file", "docker compose for production"
- "what version should I use for postgres", "version matrix"
