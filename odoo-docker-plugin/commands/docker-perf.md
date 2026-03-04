---
title: 'Docker Performance Analyzer'
read_only: false
type: 'command'
description: 'Analyze Docker configuration for performance issues and generate tuning recommendations based on real stress test data'
---

# /docker-perf — Performance Analysis & Tuning

Analyze your Docker-based Odoo deployment for performance issues and generate data-driven recommendations. Uses findings from real stress tests (SKILL.md §18).

## Usage

```
/docker-perf
/docker-perf --compose docker-compose.yml --config conf/myproject.conf
```

## Arguments (if provided): $ARGUMENTS

## Analysis Steps

### Step 1: Read Current Configuration

1. Find and read `docker-compose*.yml` files
2. Find and read `conf/*.conf` files
3. Find and read `.env` files
4. Check for nginx configuration

### Step 2: Analyze Odoo Configuration

Check each setting against known performance impacts:

| Setting | Check | Impact |
|---------|-------|--------|
| `workers` | Must be >= 2 for production | workers=0 causes 10s P50 at 50 users |
| `data_dir` | Must be set to `/var/lib/odoo` | Missing = JS 500 errors, 19-49s asset load |
| `db_maxconn` | Should be 16 per worker | Unset = 51+ idle connections under stress |
| `proxy_mode` | True when behind nginx | False = incorrect IP logging |
| `max_cron_threads` | Should be 1 | Multiple = concurrent cron conflicts |
| `limit_memory_soft` | Should be 2GB | Too low = OOM kills |
| `limit_time_real` | Should be >= 600 | Too low = timeout on heavy operations |

### Step 3: Analyze Docker Compose

| Check | Issue | Recommendation |
|-------|-------|----------------|
| Resource limits | No limits = unbounded memory | Add `deploy.resources.limits` |
| Health checks | No health checks = silent failures | Add `healthcheck` to all services |
| PostgreSQL tuning | Default settings = suboptimal | Add `shared_buffers`, `work_mem`, etc. |
| Volume type | bind mount for data = fragile | Use named volumes for DB + filestore |
| Gzip/Nginx | Direct Odoo exposure | Add nginx with gzip (90% CSS reduction) |
| Warm-up service | First load compiles assets (25-120s) | Add warm-up curl service |

### Step 4: Analyze PostgreSQL Configuration

Check docker-compose `command` for PostgreSQL tuning. Recommend based on available RAM:

| Setting | Default | 4 GB RAM | 16 GB RAM |
|---------|---------|----------|-----------|
| shared_buffers | 128 MB | 1 GB | 4 GB |
| work_mem | 4 MB | 16 MB | 32 MB |
| effective_cache_size | 4 GB | 3 GB | 12 GB |
| maintenance_work_mem | 64 MB | 128 MB | 512 MB |
| random_page_cost | 4.0 | 1.1 | 1.1 |

### Step 5: Generate Report

Output a structured report:

```
Performance Analysis Report
═══════════════════════════

Critical Issues:
  ✗ workers=0 — Production unusable (10s P50 at 50 users)
  ✗ data_dir not set — JS assets will fail

Warnings:
  △ No nginx/gzip — 894 KB CSS per page (vs 89 KB with gzip)
  △ No resource limits — containers can consume all host resources
  △ No warm-up service — first load takes 25-120s

Good:
  ✓ Health checks configured
  ✓ Named volumes for persistence

Recommendations:
  1. Set workers=2 (minimum) or workers=4 (heavy load)
  2. Add data_dir = /var/lib/odoo
  3. Add nginx reverse proxy with gzip level 6
  4. Add resource limits (Odoo: 2G RAM, DB: 1G RAM)
  5. Add warm-up service
  6. Set db_maxconn=16
```

### Step 6: Auto-Fix (Optional)

Ask user: "Apply recommended fixes automatically?"

If yes, generate optimized versions of:
- `odoo.conf` with performance settings
- `docker-compose.yml` with resource limits, health checks, nginx
- `nginx.conf` with gzip and caching

## Key Data Points (From Stress Tests)

- `workers=0`: P50 = 9,068ms at 50 users, 10% HTTP 500 errors
- `workers=2`: P50 ~ 800ms (10x improvement)
- Missing `data_dir`: 19-49s asset load, HTTP 500 on JS bundles
- Gzip level 6: 894 KB → 89 KB CSS (90% reduction)
- No `db_maxconn`: 51 idle connections accumulate
- Memory at rest: 227.6 MB, peak: 234.8 MB (no leak)
- Workers formula: `(CPU cores * 2) + 1`

## Natural Language Triggers

- "optimize docker performance", "slow containers"
- "tune workers", "fix slow response time"
- "analyze performance", "performance report"
- "why is odoo slow in docker", "container performance"
