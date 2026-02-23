---
title: 'Odoo Docker Manager'
read_only: false
type: 'command'
description: 'Docker management for Odoo — build images, start/stop containers, view logs, open shell, generate docker-compose and Dockerfile'
---

# /odoo-docker — Odoo Docker Manager

Complete Docker lifecycle management for Odoo. Generates Dockerfiles and docker-compose files, manages containers, and provides exec shortcuts.

## Usage

```
/odoo-docker <operation> [options]
```

## Operations

### Initialize Docker Project

```
/odoo-docker init --version 17 --project myproject
/odoo-docker init --version 17 --project myproject --port 8069 --output .
```

Generates:
- `Dockerfile` — version-appropriate Python base, wkhtmltopdf, rtlcss
- `docker-compose.yml` — PostgreSQL + Odoo services with healthchecks
- `.env` + `.env.example` — environment variables template
- `conf/`, `logs/`, `backups/`, `projects/myproject/` directories

### Build Image

```
/odoo-docker build
/odoo-docker build --no-cache
```

Runs:
```bash
docker-compose build
docker-compose build --no-cache  # Full rebuild
```

### Start Containers

```
/odoo-docker up
/odoo-docker up --build    # Rebuild first
```

Runs:
```bash
docker-compose up -d
docker-compose up -d --build
```

### Stop and Remove Containers

```
/odoo-docker down
/odoo-docker down --volumes   # WARNING: Deletes volumes/data
```

### Start/Stop (Without Remove)

```
/odoo-docker start    # Start stopped containers
/odoo-docker stop     # Stop without removing
/odoo-docker restart  # Restart all
/odoo-docker restart --service odoo   # Restart only Odoo
```

### View Logs

```
/odoo-docker logs
/odoo-docker logs --tail 100
/odoo-docker logs --no-follow    # Don't follow, just print
/odoo-docker logs --service db   # PostgreSQL logs
```

Runs:
```bash
docker-compose logs -f --tail=100 odoo
```

### Open Shell

```
/odoo-docker shell              # Bash in Odoo container
/odoo-docker shell --service db # Bash in DB container
```

Runs:
```bash
docker-compose exec odoo bash
```

### Open Odoo Python Shell

```
/odoo-docker odoo-shell --db myproject17
```

Runs:
```bash
docker-compose exec odoo python -m odoo shell -d myproject17 -c /etc/odoo/odoo.conf
```

### Update Module

```
/odoo-docker update --db myproject17 --module my_module
/odoo-docker update --db myproject17 --module module1,module2
```

Runs:
```bash
docker-compose exec odoo python -m odoo -c /etc/odoo/odoo.conf -d myproject17 -u my_module --stop-after-init
```

### Install Module

```
/odoo-docker install --db myproject17 --module my_module
```

### Check Status

```
/odoo-docker status
```

Runs:
```bash
docker-compose ps
```

## Generated Dockerfile (Odoo 17 Example)

```dockerfile
FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libxml2-dev libxslt1-dev \
    libjpeg-dev libfreetype6-dev libssl-dev npm git \
    postgresql-client wget curl \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

RUN npm install -g rtlcss

WORKDIR /opt/odoo/source
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install geoip2

EXPOSE 8069 8072
CMD ["python", "-m", "odoo", "-c", "/etc/odoo/odoo.conf"]
```

## Natural Language Triggers

- "build docker image", "docker build", "build container"
- "start docker", "docker up", "start containers"
- "stop docker", "docker down", "stop containers"
- "view odoo logs", "docker logs", "show container logs"
- "open container shell", "docker shell", "exec into container"
- "update module in docker", "odoo-docker update"
- "initialize docker project", "setup docker for odoo"

## Implementation

Uses `odoo-service/scripts/docker_manager.py`:

```python
from docker_manager import init_docker_project, up, logs, shell

# Initialize
init_docker_project("myproject", 17, 8069)

# Start
up(detach=True)

# Logs
logs(follow=True, tail=100)

# Shell
shell(service="odoo")
```
