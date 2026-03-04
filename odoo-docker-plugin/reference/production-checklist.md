# Production Deployment Checklist

## Pre-Deployment

### Odoo Configuration (odoo.conf)
- [ ] `workers >= 2` (minimum); `workers = 4` for heavy load
- [ ] `data_dir = /var/lib/odoo` (filestore persistence)
- [ ] `proxy_mode = True` (required behind nginx)
- [ ] `list_db = False` (prevent database enumeration)
- [ ] `admin_passwd` = strong 32+ character password
- [ ] `db_maxconn = 16` per worker (connection pool safety)
- [ ] `max_cron_threads = 1` (prevent concurrent cron conflicts)
- [ ] `limit_time_cpu = 600` (prevent runaway processes)
- [ ] `limit_time_real = 1200` (prevent hung requests)
- [ ] `limit_memory_soft = 2147483648` (2 GB)
- [ ] `limit_memory_hard = 2684354560` (2.5 GB)
- [ ] Correct gevent key: `gevent_port` (v17+) or `longpolling_port` (v14-16)

### Docker Compose
- [ ] Health checks on ALL services (db, odoo, nginx)
- [ ] Resource limits: Odoo (memory: 2G, cpus: 2)
- [ ] Resource limits: PostgreSQL (memory: 1G, cpus: 1)
- [ ] Named volumes for DB data and filestore (NOT bind mounts)
- [ ] Source code mounted read-only (`:ro`)
- [ ] Config file mounted read-only (`:ro`)
- [ ] Isolated Docker network per project
- [ ] Warm-up service for asset pre-compilation
- [ ] `restart: unless-stopped` on all services

### Nginx
- [ ] Gzip compression enabled (level 6)
- [ ] WebSocket routing (`/websocket` → port 8072)
- [ ] Static asset caching (365d for `/web/assets/`)
- [ ] Rate limiting (10 req/s per IP, burst 20)
- [ ] Client max body size: 200m
- [ ] Proxy headers set (X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
- [ ] Proxy timeouts: 600s

### Security
- [ ] SSL/TLS with Let's Encrypt or other CA
- [ ] HTTP → HTTPS redirect
- [ ] TLS 1.2+ only
- [ ] Custom database credentials (not default odoo/odoo)
- [ ] Database container NOT exposed to host
- [ ] Firewall rules configured

### PostgreSQL
- [ ] `shared_buffers` tuned (25% of RAM)
- [ ] `work_mem` tuned (16-32 MB)
- [ ] `effective_cache_size` tuned (75% of RAM)
- [ ] `maintenance_work_mem` tuned (128-512 MB)
- [ ] `random_page_cost = 1.1` (SSD)
- [ ] `checkpoint_completion_target = 0.9`
- [ ] `shm_size: '256m'` in docker-compose

### Operations
- [ ] Backup strategy in place (pg_dump scheduled)
- [ ] Tested database restore procedure
- [ ] Log aggregation configured
- [ ] Monitoring/alerting in place
- [ ] Update/upgrade procedure documented

## Post-Deployment Verification

```bash
# 1. All containers healthy
docker-compose ps

# 2. Odoo web UI accessible
curl -sf -o /dev/null -w "%{http_code}" http://localhost:8069/web/login
# Expect: 200

# 3. Health check passes
curl -sf http://localhost:8069/web/health

# 4. No errors in logs
docker-compose logs odoo 2>&1 | grep -i "ERROR\|CRITICAL"
# Expect: empty

# 5. SSL working (if configured)
curl -sf -o /dev/null -w "%{http_code}" https://yourdomain.com/web/login

# 6. WebSocket working
# Check browser console for WebSocket connection

# 7. Assets loading (no 500 errors)
# Open browser DevTools → Network → check JS/CSS responses
```
