# Odoo Database Patterns

Complete reference for PostgreSQL setup, backup/restore strategies, multi-tenant configuration, admin operations, and Docker database patterns for Odoo.

---

## 1. PostgreSQL Installation and User Setup

### Windows

```powershell
# Install via Chocolatey
choco install postgresql15

# Install via installer from https://www.postgresql.org/download/windows/
# Remember the password you set for 'postgres' superuser

# Start service
net start postgresql-x64-15

# Connect as postgres superuser
psql -U postgres

# Create odoo user
CREATE USER odoo WITH PASSWORD 'odoo' CREATEDB;
# For development (easier):
CREATE USER odoo WITH PASSWORD 'odoo' SUPERUSER;

# Verify
\du              # List users
\l               # List databases
\q               # Quit
```

### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL 15
sudo apt update
sudo apt install postgresql-15 postgresql-client-15

# Start and enable
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create Odoo user
sudo -u postgres createuser --createdb --no-superuser --no-createrole -P odoo
# Enter password when prompted: odoo

# For development (simpler, superuser):
sudo -u postgres createuser --superuser odoo
sudo -u postgres psql -c "ALTER USER odoo PASSWORD 'odoo';"

# Verify connection
psql -U odoo -h localhost -c "SELECT version();"
```

### macOS

```bash
# Install via Homebrew
brew install postgresql@15
brew services start postgresql@15

# Add to PATH
echo 'export PATH="/usr/local/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Create Odoo user
createuser --superuser odoo
psql postgres -c "ALTER USER odoo PASSWORD 'odoo';"
```

---

## 2. pg_dump / pg_restore Options and Formats

### Backup Formats Comparison

| Format | Flag | Extension | Size | Speed | Use Case |
|--------|------|-----------|------|-------|----------|
| Plain SQL | (default) | `.sql` | Largest | Slow restore | Human-readable, cross-version |
| Custom | `-Fc` | `.dump` | Compressed | Fast restore | Recommended for Odoo |
| Directory | `-Fd` | dir/ | Compressed | Parallel | Very large databases |
| Tar | `-Ft` | `.tar` | Compressed | Moderate | Simple archives |

### pg_dump Options

```bash
# Basic SQL backup
pg_dump -U odoo -h localhost mydb > mydb.sql

# Custom format (compressed, recommended)
pg_dump -U odoo -h localhost -Fc mydb > mydb.dump

# Directory format with parallel jobs (large DBs)
pg_dump -U odoo -h localhost -Fd -j 4 mydb -f mydb_dir/

# With timestamp in filename
pg_dump -U odoo -h localhost -Fc mydb > mydb_$(date +%Y%m%d_%H%M%S).dump

# Specific tables only
pg_dump -U odoo -h localhost -t res_partner -t res_users mydb > users.sql

# Schema only (no data)
pg_dump -U odoo -h localhost --schema-only mydb > schema.sql

# Data only (no schema)
pg_dump -U odoo -h localhost --data-only mydb > data.sql

# Exclude table data (but keep structure)
pg_dump -U odoo -h localhost --exclude-table-data=ir_attachment mydb > mydb_no_attach.dump
```

### pg_restore Options

```bash
# Restore custom dump to existing database
pg_restore -U odoo -h localhost -d mydb backup.dump

# Create database and restore
createdb -U odoo mydb && pg_restore -U odoo -h localhost -d mydb backup.dump

# Parallel restore (faster)
pg_restore -U odoo -h localhost -d mydb -j 4 backup.dump

# Restore with verbose output
pg_restore -U odoo -h localhost -d mydb -v backup.dump

# List contents of dump without restoring
pg_restore --list backup.dump

# Restore specific tables
pg_restore -U odoo -d mydb -t res_partner backup.dump
```

### psql Restore (SQL format)

```bash
# Restore plain SQL file
psql -U odoo -h localhost -d mydb < backup.sql

# Create database first
createdb -U odoo mydb
psql -U odoo -h localhost -d mydb < backup.sql

# With progress output
pv backup.sql | psql -U odoo -h localhost -d mydb
# (pv = pipe viewer, shows progress)
```

---

## 3. Odoo Database Manager (Web UI)

Access at: `http://localhost:8069/web/database/manager`

Requires `admin_passwd` from .conf file.

### Web UI Operations

```
Create:  Create new empty database
Backup:  Download .zip backup (includes filestore)
Restore: Upload .zip backup
Duplicate: Clone existing database
Drop:    Delete database
```

### ZIP Backup Format

Odoo web manager creates `.zip` files containing:
- `dump.sql` — PostgreSQL dump
- `filestore/` — Binary attachments (PDF, images, etc.)

```bash
# Extract and restore from Odoo ZIP backup
unzip mydb_backup.zip -d /tmp/odoo_restore/

# Restore database
createdb -U odoo mydb_restored
psql -U odoo -d mydb_restored < /tmp/odoo_restore/dump.sql

# Restore filestore
cp -r /tmp/odoo_restore/filestore/* /path/to/odoo/data/filestore/mydb_restored/
```

---

## 4. Multi-Tenant Database Patterns

### dbfilter Configuration

```ini
# Only show databases matching this regex
dbfilter = myproject17.*
# Matches: myproject17, myproject17_dev, myproject17_staging

# Single database (exact match)
dbfilter = myproject17$

# Multiple projects on same port (avoid — use separate ports instead)
dbfilter = (projecta|projectb)17.*

# No filter (show all — development only)
dbfilter =
```

### Database Naming Conventions

```
Recommended naming: {project}{version}[_{env}]
Examples:
  myproject17           # Project Alpha, Odoo 17, production
  myproject17_dev       # Project Alpha, Odoo 17, development
  myproject17_staging   # Project Alpha, Odoo 17, staging
  myproject2_17         # Project Beta, Odoo 17
  myproject19           # Project Gamma, Odoo 19
```

### Separate Instance Per Project

```bash
# Run multiple Odoo instances, each with own port and dbfilter
# Instance A — port 8069
python -m odoo -c conf/projectA17.conf  # dbfilter=projectA17.*

# Instance B — port 8070
python -m odoo -c conf/projectB17.conf  # dbfilter=projectB17.*
```

---

## 5. Backup Automation

### Windows Task Scheduler

```powershell
# Create backup script: C:\odoo\backup_all.ps1
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\odoo\backups"

# Create backup directory
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Backup Odoo 17 projects
$env:PGPASSWORD = "odoo"
pg_dump -U odoo -h localhost -Fc mydb -f "$backupDir\mydb_$timestamp.dump"
pg_dump -U odoo -h localhost -Fc mydb -f "$backupDir\mydb_$timestamp.dump"

# Remove backups older than 30 days
Get-ChildItem $backupDir -Filter "*.dump" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item

Write-Host "Backup complete: $timestamp"
```

```powershell
# Schedule via Task Scheduler
schtasks /create /tn "OdooBackup" /tr "powershell -File C:\odoo\backup_all.ps1" /sc daily /st 02:00
```

### Linux Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/odoo/backup_all.sh >> /var/log/odoo_backup.log 2>&1
```

```bash
#!/bin/bash
# /opt/odoo/backup_all.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/odoo/backups"
PGPASSWORD="odoo"
export PGPASSWORD

mkdir -p "$BACKUP_DIR"

# Backup databases
pg_dump -U odoo -h localhost -Fc mydb -f "$BACKUP_DIR/mydb_$TIMESTAMP.dump"
pg_dump -U odoo -h localhost -Fc mydb -f "$BACKUP_DIR/mydb_$TIMESTAMP.dump"

# Remove old backups (older than 30 days)
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete

echo "Backup complete: $TIMESTAMP"
```

---

## 6. Admin Password Reset

### Method 1: psql SQL UPDATE (Fastest)

```bash
# Set plaintext password (Odoo hashes it on next login)
psql -U odoo -h localhost -d mydb -c \
    "UPDATE res_users SET password='newpassword' WHERE login='admin';"

# Verify
psql -U odoo -h localhost -d mydb -c \
    "SELECT id, login, active FROM res_users WHERE login='admin';"
```

### Method 2: Odoo Shell (Recommended — Proper Hashing)

```python
python odoo-bin shell -d mydb

# In shell:
user = env['res.users'].search([('login', '=', 'admin')], limit=1)
user.write({'password': 'newpassword'})
env.cr.commit()
print("Password reset complete")
```

### Method 3: Odoo Web Manager Reset

Navigate to: `http://localhost:8069/web/database/manager`
Use "Set Master Password" to reset admin_passwd (different from user password).

---

## 7. Useful Database Queries

### Check Installed Modules

```sql
-- All installed modules
SELECT name, state, author FROM ir_module_module WHERE state = 'installed' ORDER BY name;

-- Modules to update (upgrade needed)
SELECT name, state FROM ir_module_module WHERE state = 'to upgrade';

-- Modules installed by category
SELECT c.name as category, m.name FROM ir_module_module m
JOIN ir_module_category c ON c.id = m.category_id
WHERE m.state = 'installed'
ORDER BY c.name, m.name;
```

### Check Users

```sql
-- Active users
SELECT u.id, u.login, p.name, u.active
FROM res_users u
JOIN res_partner p ON p.id = u.partner_id
WHERE u.active = true
ORDER BY u.id;

-- Users by group
SELECT rg.name as group_name, p.name as user_name, u.login
FROM res_groups_users_rel r
JOIN res_groups rg ON rg.id = r.gid
JOIN res_users u ON u.id = r.uid
JOIN res_partner p ON p.id = u.partner_id
WHERE u.active = true
ORDER BY rg.name;
```

### Database Size Monitoring

```sql
-- Database size
SELECT pg_database.datname,
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;

-- Table sizes in current database
SELECT relname AS table_name,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
       pg_size_pretty(pg_relation_size(relid)) AS data_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;

-- Largest ir_attachment records
SELECT res_model, count(*) as count,
       pg_size_pretty(sum(file_size)) as total_size
FROM ir_attachment
WHERE store_fname IS NOT NULL
GROUP BY res_model
ORDER BY sum(file_size) DESC
LIMIT 10;
```

### System Configuration

```sql
-- System parameters
SELECT key, value FROM ir_config_parameter ORDER BY key;

-- Web base URL
SELECT value FROM ir_config_parameter WHERE key = 'web.base.url';
```

---

## 8. Restore Procedures (Step-by-Step)

### Full Restore from Custom Dump

```bash
# Step 1: Verify backup integrity
pg_restore --list mydb_backup.dump | head -20  # Should list contents

# Step 2: Create target database
createdb -U odoo -h localhost new_mydb

# Step 3: Restore
pg_restore -U odoo -h localhost -d new_mydb mydb_backup.dump

# Step 4: Verify restoration
psql -U odoo -h localhost -d new_mydb -c "SELECT count(*) FROM res_partner;"

# Step 5: Update web.base.url if needed
psql -U odoo -h localhost -d new_mydb -c \
    "UPDATE ir_config_parameter SET value='http://localhost:8069' WHERE key='web.base.url';"

# Step 6: Reset admin password if needed
psql -U odoo -h localhost -d new_mydb -c \
    "UPDATE res_users SET password='admin' WHERE login='admin';"

# Step 7: Start Odoo with new database
python -m odoo -c conf/project.conf -d new_mydb --dev=all
```

---

## 9. PostgreSQL Performance Tuning for Odoo

### postgresql.conf Recommendations

```ini
# Memory settings (adjust based on available RAM)
shared_buffers = 256MB          # 25% of RAM
effective_cache_size = 1GB      # 75% of RAM
work_mem = 64MB                  # Per sort/join operation
maintenance_work_mem = 256MB    # Vacuum, index creation

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 64MB

# Query planner
random_page_cost = 1.1          # For SSDs (vs 4.0 for HDDs)
effective_io_concurrency = 200   # For SSDs

# Connection settings
max_connections = 100           # Adjust based on workers*max_db_conn
```

### Create Index for Common Queries

```sql
-- Common indexes that improve Odoo performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_res_partner_company_id
    ON res_partner(company_id) WHERE company_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ir_attachment_res_model_id
    ON ir_attachment(res_model, res_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mail_message_model_id
    ON mail_message(model, res_id);
```

---

## 10. Docker Database Patterns

### Database Inside Docker Volume

```yaml
# Persistent volume (survives container restart)
volumes:
  db_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/odoo/db_data  # Host path

services:
  db:
    volumes:
      - db_data:/var/lib/postgresql/data
```

### Database Backup from Docker

```bash
# Method 1: docker exec + redirect
docker exec odoo_db pg_dump -U odoo mydb > backup.sql
docker exec odoo_db pg_dump -U odoo -Fc mydb > backup.dump

# Method 2: docker cp (copy file out of container)
docker exec odoo_db pg_dump -U odoo -Fc mydb -f /tmp/backup.dump
docker cp odoo_db:/tmp/backup.dump ./backup.dump

# Scheduled backup via Docker
docker exec odoo_db pg_dump -U odoo -Fc mydb > /host/backups/mydb_$(date +%Y%m%d).dump
```

### Database Restore into Docker

```bash
# Method 1: stdin pipe
cat backup.sql | docker exec -i odoo_db psql -U odoo mydb
docker exec -i odoo_db pg_restore -U odoo -d mydb < backup.dump

# Method 2: Copy file in then restore
docker cp backup.dump odoo_db:/tmp/backup.dump
docker exec odoo_db pg_restore -U odoo -d mydb /tmp/backup.dump
docker exec odoo_db rm /tmp/backup.dump

# Create database in Docker first
docker exec odoo_db createdb -U odoo mydb_new
docker exec -i odoo_db pg_restore -U odoo -d mydb_new < backup.dump
```

### Connecting to Docker PostgreSQL from Host

```bash
# If port 5432 is mapped in docker-compose.yml
psql -U odoo -h localhost -p 5432 mydb

# Via docker exec
docker exec -it odoo_db psql -U odoo mydb

# Run SQL via docker exec
docker exec odoo_db psql -U odoo mydb -c "SELECT count(*) FROM res_partner;"
```
