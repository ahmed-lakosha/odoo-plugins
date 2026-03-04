# Docker Troubleshooting Quick Reference

## Issue → Solution Map

### Container Startup Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Container exits immediately | Source not mounted | Fix volume path in docker-compose |
| "Odoo source not found" | Missing volume mount | `ls sources/odoo-{v}/` and fix path |
| "No module named 'odoo'" | v19 PYTHONPATH issue | Add `PYTHONPATH=/opt/odoo/source` in entrypoint |
| Container in restart loop | Python crash on start | `docker logs {container} --tail 100` |
| "Permission denied" | Wrong file ownership | Files must be owned by uid 1000 (odoo) |

### Network Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Port already in use | Another process on 8069 | Kill: `netstat -ano \| findstr :8069` + `taskkill /PID {PID} /F` |
| Can't connect to DB | DB container not ready | Add `depends_on: db: condition: service_healthy` |
| "Connection refused" on port | Container not running | `docker ps` to check, `docker-compose up -d` |
| 502 Bad Gateway | Nginx can't reach Odoo | Check Odoo health, same network, upstream config |

### Application Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| JS/CSS returns HTTP 500 | Missing `data_dir` | Add `data_dir = /var/lib/odoo` in odoo.conf |
| Very slow (10s+ response) | `workers=0` | Set `workers=2` minimum for production |
| WebSocket not working | Wrong gevent key | v14-16: `longpolling_port`, v17+: `gevent_port` |
| Module not found | Wrong addons_path | Check `addons_path` in odoo.conf vs volume mounts |
| Changes not reflecting | Module not updated | `-u {module} --stop-after-init` inside container |
| Slow first load (25-120s) | Asset compilation | Add warm-up service or accept first-load delay |

### Resource Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Container OOM killed | Insufficient memory limit | Increase `deploy.resources.limits.memory` |
| "No space left on device" | Docker disk full | `docker system prune -af` |
| High CPU usage | Too many workers | Reduce workers, check cron threads |
| 51+ idle DB connections | No `db_maxconn` limit | Set `db_maxconn = 16` per worker |

### Database Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Role does not exist" | Missing PostgreSQL user | `CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB;` |
| "Database does not exist" | DB not created | Create via API or `createdb -U odoo {name}` |
| Can't connect from host | Port not exposed | Add `ports: - "5433:5432"` to db service |

## Diagnostic Commands

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs --tail=100 odoo
docker-compose logs --tail=50 db

# Check health
docker exec {container} curl -sf http://localhost:8069/web/health
docker exec {db_container} pg_isready -U odoo

# Check volumes
docker exec {container} ls -la /opt/odoo/source/
docker exec {container} ls -la /opt/odoo/custom-addons/
docker exec {container} cat /etc/odoo/odoo.conf

# Check resources
docker stats --no-stream
docker system df

# Check network
docker network ls
docker exec {container} ping -c 1 db
```
