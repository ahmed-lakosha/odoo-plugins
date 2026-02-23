# Odoo Deployment Patterns

> **Purpose**: CI/CD deployment patterns for Odoo — SSH-based self-hosted servers and Odoo.sh.
> Covers production, staging, rollback, and health checks.

---

## Deployment Approaches

| Approach | Best For | Tool |
|----------|----------|------|
| SSH + git pull | Self-hosted servers, VPS | `appleboy/ssh-action` |
| Docker Compose | Containerized setup | SSH + `docker compose pull && up` |
| Odoo.sh | Managed hosting, custom addons only | Push to repo = deploy |
| systemd unit | Linux servers with direct install | `systemctl restart odoo` |

---

## SSH Deployment Script (GitHub Actions)

```yaml
# In .github/workflows/4-deploy-staging.yml
- name: Deploy via SSH
  uses: appleboy/ssh-action@v1.2.0
  with:
    host: ${{ secrets.STAGING_HOST }}
    username: ${{ secrets.STAGING_USER }}
    key: ${{ secrets.STAGING_SSH_KEY }}
    script: |
      set -e

      # 1. Backup database before any changes
      BACKUP=/tmp/backup_$(date +%Y%m%d_%H%M%S).sql.gz
      pg_dump -U odoo mydb | gzip > $BACKUP
      echo "✓ Backup: $BACKUP"

      # 2. Pull latest code and detect changed modules
      cd /opt/odoo/projects
      OLD_SHA=$(git rev-parse HEAD)
      git pull origin main
      CHANGED=$(git diff --name-only $OLD_SHA HEAD \
        | grep "^my_project/" \
        | awk -F/ '{print $2}' \
        | sort -u | tr '\n' ',' | sed 's/,$//')

      if [ -z "$CHANGED" ]; then
        echo "No module changes detected — restarting only"
      else
        echo "Updating modules: $CHANGED"
        # 3. Update only changed modules (10x faster than -u all)
        cd /opt/odoo
        python -m odoo \
          -c conf/myproject.conf \
          -d mydb \
          -u "$CHANGED" \
          --stop-after-init \
          --log-level=warn
      fi

      # 4. Restart Odoo service
      sudo systemctl restart odoo
      sleep 5

      # 5. Health check (Odoo 16+)
      curl -sf http://localhost:8069/web/health || {
        echo "HEALTH CHECK FAILED — rolling back"
        sudo systemctl stop odoo
        gunzip -c $BACKUP | psql -U odoo mydb
        sudo systemctl start odoo
        exit 1
      }

      echo "✓ Deployment complete"
```

---

## Production Deployment Script (Full with Rollback)

```bash
#!/bin/bash
# deploy_production.sh - Full production deployment with rollback

set -e

ODOO_DIR="/opt/odoo"
PROJECTS_DIR="$ODOO_DIR/projects"
CONF_FILE="$ODOO_DIR/conf/production.conf"
DB_NAME="mydb"
DB_USER="odoo"
BACKUP_DIR="/backups"

echo "=== Odoo Production Deployment ==="
echo "Time: $(date)"

# 1. Pre-deploy backup
BACKUP_FILE="$BACKUP_DIR/pre_deploy_$(date +%Y%m%d_%H%M%S).sql.gz"
echo "Creating backup: $BACKUP_FILE"
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE
echo "✓ Backup complete ($(du -sh $BACKUP_FILE | cut -f1))"

# 2. Pull code
echo "Pulling latest code..."
cd $PROJECTS_DIR
OLD_SHA=$(git rev-parse HEAD)
git fetch origin main
git checkout main
git pull origin main
NEW_SHA=$(git rev-parse HEAD)

if [ "$OLD_SHA" = "$NEW_SHA" ]; then
    echo "No code changes. Restarting only."
    sudo systemctl restart odoo
    exit 0
fi

# 3. Detect changed modules
CHANGED=$(git diff --name-only $OLD_SHA $NEW_SHA \
    | awk -F/ '{print $2}' \
    | sort -u \
    | tr '\n' ',' \
    | sed 's/,$//')

echo "Changed modules: $CHANGED"

# 4. Update modules
echo "Running module update..."
cd $ODOO_DIR
python -m odoo \
    -c $CONF_FILE \
    -d $DB_NAME \
    -u "$CHANGED" \
    --stop-after-init \
    --log-level=warn

# 5. Restart
echo "Restarting Odoo..."
sudo systemctl restart odoo
sleep 10

# 6. Health check with retry
MAX_TRIES=3
for i in $(seq 1 $MAX_TRIES); do
    if curl -sf http://localhost:8069/web/health > /dev/null; then
        echo "✓ Health check passed (attempt $i)"
        break
    fi
    echo "Health check attempt $i failed, retrying..."
    sleep 10
    if [ $i -eq $MAX_TRIES ]; then
        echo "CRITICAL: Health check FAILED after $MAX_TRIES attempts"
        echo "Starting rollback..."
        sudo systemctl stop odoo
        echo "Restoring database from backup: $BACKUP_FILE"
        gunzip -c $BACKUP_FILE | psql -U $DB_USER $DB_NAME
        cd $PROJECTS_DIR && git checkout $OLD_SHA
        sudo systemctl start odoo
        echo "✗ Rollback complete — previous version restored"
        exit 1
    fi
done

echo ""
echo "=== Deployment SUCCESS ==="
echo "  SHA: $OLD_SHA → $NEW_SHA"
echo "  Modules updated: $CHANGED"
echo "  Backup: $BACKUP_FILE"
echo "  Time: $(date)"
```

---

## Odoo.sh Deployment Model

When the GitHub repo holds **only custom addons** (Odoo.sh injects Odoo core):

```
Push to main branch
       │
       ▼ Odoo.sh receives webhook
       │
       ▼ Installs requirements.txt
       │
       ▼ Runs module tests (odoo_tests.cfg)
       │
       ▼ Deploys to production environment
       │
       ▼ Available at your-project.odoo.com
```

**Required repo files for Odoo.sh:**
```
your-repo/
├── requirements.txt        ← pip packages auto-installed
├── odoo_tests.cfg          ← test configuration
└── my_module/              ← your Odoo addons
    └── __manifest__.py
```

**`requirements.txt`** (place at repo root, not inside module):
```
# Extra Python packages your modules need
requests>=2.28.0
pycryptodome>=3.15.0
```

**Odoo.sh branch strategy:**
- `main` / `master` → production environment
- Any other branch → staging / development build (auto-created)
- PRs → development build for testing

---

## Health Check Endpoint

```bash
# Odoo 16+ built-in health check
curl -sf http://localhost:8069/web/health
# Returns: {"status": "pass"}

# Odoo 14/15 (no /web/health) — check login page instead
curl -sf http://localhost:8069/web/login | grep -q "Odoo" || exit 1

# Full health check script
check_odoo_health() {
    local HOST="${1:-localhost}"
    local PORT="${2:-8069}"
    local URL="http://$HOST:$PORT/web/health"

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL" --max-time 10)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✓ Odoo is healthy (HTTP $HTTP_CODE)"
        return 0
    else
        echo "✗ Odoo health check failed (HTTP $HTTP_CODE)"
        return 1
    fi
}
```

---

## Process Management

### systemd (Linux — recommended for production)

```bash
# /etc/systemd/system/odoo.service
[Unit]
Description=Odoo
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
ExecStart=/usr/bin/python3 -m odoo -c /opt/odoo/conf/production.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Commands
sudo systemctl start odoo
sudo systemctl stop odoo
sudo systemctl restart odoo
sudo systemctl status odoo
journalctl -u odoo -f  # tail logs
```

### supervisor (alternative)

```ini
# /etc/supervisor/conf.d/odoo.conf
[program:odoo]
command=python3 -m odoo -c /opt/odoo/conf/production.conf
user=odoo
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/odoo/odoo.log

# Commands
supervisorctl start odoo
supervisorctl stop odoo
supervisorctl restart odoo
supervisorctl tail -f odoo  # tail logs
```

---

## Pre-Deploy Checklist

```bash
# 1. Backup database
pg_dump -U odoo mydb | gzip > backup_$(date +%Y%m%d).sql.gz

# 2. Check disk space (Odoo log files grow fast)
df -h /opt/odoo /var/log

# 3. Test module update on staging first
python -m odoo -c conf/staging.conf -d staging_mydb -u my_module --stop-after-init

# 4. Verify all module tests pass
python -m odoo -c conf/staging.conf -d staging_mydb \
  --test-enable -u my_module --stop-after-init \
  --test-tags=post_install,standard

# 5. Production deploy
sudo systemctl stop odoo
git pull origin main
python -m odoo -c conf/production.conf -d mydb -u my_module --stop-after-init
sudo systemctl start odoo
curl -sf http://localhost:8069/web/health
```

---

---

## Starting Odoo for Playwright E2E Testing (CI)

When running Playwright against a locally started Odoo instance in GitHub Actions:

### Start Odoo in Background + Wait

```bash
#!/bin/bash
# start_odoo_for_e2e.sh

DB_NAME="${1:-e2e_test}"

# Create test database
PGPASSWORD=odoo psql -h localhost -U odoo -c "CREATE DATABASE $DB_NAME" postgres 2>/dev/null || true

# Start Odoo with demo data (required for E2E tests that need existing records)
python -m odoo \
    --db_host=localhost \
    --db_user=odoo \
    --db_password=odoo \
    -d $DB_NAME \
    --addons-path=odoo/addons,projects \
    --without-demo=False \
    --http-port=8069 \
    --log-level=warn &

ODOO_PID=$!
echo "Odoo PID: $ODOO_PID"

# Wait for Odoo to be ready (up to 150 seconds)
echo "Waiting for Odoo to start..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8069/web/health > /dev/null 2>&1; then
        echo "✓ Odoo is ready (${i}x5s = $((i*5))s)"
        exit 0
    fi
    echo "  Attempt $i/30..."
    sleep 5
done

echo "ERROR: Odoo failed to start after 150 seconds"
kill $ODOO_PID 2>/dev/null
exit 1
```

### GitHub Actions Step

```yaml
- name: Start Odoo for E2E tests
  run: |
    # Create database
    PGPASSWORD=odoo psql -h localhost -U odoo -c "CREATE DATABASE e2e_test" postgres

    # Start Odoo in background
    python -m odoo \
      --db_host=localhost --db_user=odoo --db_password=odoo \
      -d e2e_test --addons-path=odoo/addons,projects \
      --without-demo=False --http-port=8069 --log-level=warn &

    # Wait for health
    for i in $(seq 1 30); do
      curl -sf http://localhost:8069/web/health && break || true
      sleep 5
    done

- name: Run Playwright E2E
  run: npx playwright test
  env:
    PLAYWRIGHT_BASE_URL: http://localhost:8069
    ODOO_USER: admin
    ODOO_PASSWORD: admin
```

### Demo Data vs Test Data

```bash
# With Odoo demo data (recommended for E2E — pre-populated records)
--without-demo=False

# Fresh database (E2E tests must create all test data themselves)
--without-demo=all

# Install specific module with demo
python -m odoo ... -i my_module --without-demo=False --stop-after-init
# Then restart without --stop-after-init for Playwright to connect
```

### Odoo.sh: No Server to Start

When using Odoo.sh, Playwright tests target the public staging URL directly:

```bash
# Odoo.sh staging URL is auto-created per branch
# Just point Playwright at it — no server management needed
PLAYWRIGHT_BASE_URL=https://your-project-staging.odoo.com npx playwright test
```

Odoo.sh creates a staging environment per git branch automatically.
No SSH access or server management required.

---

## Related

- `server_commands.md` — Startup flags and configuration reference
- `devops-plugin/memories/cicd_patterns.md` — Full GitHub Actions YAML for all stages
- `devops-plugin/commands/ci-setup.md` — Generate CI/CD workflow files
- `odoo-test-plugin/memories/playwright_e2e_patterns.md` — Playwright patterns and page objects
