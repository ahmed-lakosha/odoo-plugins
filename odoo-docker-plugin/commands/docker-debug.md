---
title: 'Docker Container Debugger'
read_only: false
type: 'command'
description: 'Systematic container troubleshooting — check status, logs, health, network, and volumes with auto-suggested fixes'
---

# /docker-debug — Container Troubleshooting

Systematic debugging workflow for Docker-based Odoo deployments. Checks container status, logs, health, network, and volumes, then suggests fixes based on known issue patterns.

## Usage

```
/docker-debug
/docker-debug --compose docker-compose.relief_center.yml
/docker-debug --container relief_center_19_web
```

## Arguments (if provided): $ARGUMENTS

## Debugging Workflow

### Step 1: Identify Target

Find docker-compose files or running containers:
```bash
ls docker-compose*.yml 2>/dev/null
docker ps -a --filter "label=com.docker.compose.project" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Step 2: Check Container Status

```bash
docker-compose -f {compose_file} ps
```

Analyze each container:
- **Running + Healthy**: OK
- **Running + Unhealthy**: Check health command
- **Restarting**: Check logs for crash loop
- **Exited (non-zero)**: Check exit code and logs
- **Not found**: Compose not started

### Step 3: Check Logs

```bash
# Last 100 lines from Odoo
docker-compose -f {compose_file} logs --tail=100 odoo 2>&1

# Last 50 lines from DB
docker-compose -f {compose_file} logs --tail=50 db 2>&1
```

Scan for known error patterns:

| Pattern | Issue | Fix |
|---------|-------|-----|
| `Odoo source not found` | Source not mounted | Check volume paths in compose |
| `could not connect to server` | DB not ready | Check db health, depends_on |
| `Address already in use` | Port conflict | Kill process on port or change port |
| `No module named` | Missing Python package | Rebuild image or pip install |
| `FATAL: role .* does not exist` | Wrong DB credentials | Check POSTGRES_USER in .env |
| `database .* does not exist` | DB not created | Create via API or CLI |
| `HTTP 500.*assets` | Missing data_dir | Add `data_dir = /var/lib/odoo` |
| `OOM` or `Killed` | Out of memory | Add resource limits |
| `Permission denied` | File ownership | Check odoo user (uid 1000) |

### Step 4: Check Health

```bash
# Odoo health
docker exec {container} curl -sf http://localhost:8069/web/health

# DB health
docker exec {db_container} pg_isready -U odoo
```

### Step 5: Check Network

```bash
# Can Odoo reach DB?
docker exec {odoo_container} ping -c 1 db

# Check Docker networks
docker network ls
docker network inspect {network}
```

### Step 6: Check Volumes

```bash
# List volumes
docker volume ls | grep {project}

# Check volume contents
docker exec {container} ls -la /opt/odoo/source/
docker exec {container} ls -la /opt/odoo/custom-addons/
docker exec {container} ls -la /var/lib/odoo/
docker exec {container} cat /etc/odoo/odoo.conf
```

### Step 7: Check Resources

```bash
docker stats --no-stream
docker system df
```

### Step 8: Generate Diagnostic Report

```
Diagnostic Report
═════════════════

Containers:
  ✓ relief_center_19_db: Running (healthy)
  ✗ relief_center_19_web: Restarting (unhealthy)

Issues Found:
  1. [CRITICAL] Odoo container in restart loop
     Log: "ERROR: Odoo source not found at /opt/odoo/source"
     Fix: Verify source volume mount path exists on host

  2. [WARNING] No health check on db service
     Fix: Add healthcheck with pg_isready

Suggested Actions:
  1. Check volume mount: ls -la {source_path}
  2. Fix compose volume path
  3. Restart: docker-compose -f {compose} up -d
```

## Common Issues Quick Reference

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| Container exits immediately | Source not mounted | Fix volume path |
| 502 Bad Gateway | Odoo not ready / nginx misconfigured | Check Odoo health + upstream |
| JS/CSS not loading | Missing `data_dir` | Add `data_dir = /var/lib/odoo` |
| Very slow (10s+) | `workers=0` in production | Set `workers=2` minimum |
| Port already in use | Another container/process | `docker-compose down` or kill PID |
| DB connection refused | DB container not running | Check `docker-compose ps` |
| No space left | Docker disk full | `docker system prune` |
| Permission denied in logs | Wrong file ownership | Files must be owned by uid 1000 |

## Natural Language Triggers

- "container won't start", "debug docker"
- "500 errors in docker", "docker troubleshoot"
- "odoo container crashing", "restart loop"
- "why is my container unhealthy"
- "docker logs show error", "container problems"
