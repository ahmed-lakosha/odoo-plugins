---
title: 'Odoo Database Manager'
read_only: false
type: 'command'
description: 'Database operations — backup, restore, create, drop, list, reset admin password. Works with local PostgreSQL and Docker containers'
---

# /odoo-db — Odoo Database Manager

Complete database lifecycle management for Odoo PostgreSQL databases. Supports local PostgreSQL and Docker containers.

## Usage

```
/odoo-db <operation> [options]
```

## Operations

### Backup

```
/odoo-db backup --db myproject17
/odoo-db backup --db myproject17 --format sql
/odoo-db backup --db myproject17 --output /path/to/backups/
/odoo-db backup --docker odoo_db --db myproject17
```

Creates timestamped backup file:
- Default format: `.dump` (pg_dump -Fc, compressed, faster restore)
- SQL format: `.sql` (plain text, human-readable, larger)

Output: `backups/myproject17_20240101_143000.dump`

### Restore

```
/odoo-db restore --file backups/backup.dump --db restored_db
/odoo-db restore --file backups/backup.sql --db restored_db --no-create
/odoo-db restore --docker odoo_db --file backup.dump --db mydb
```

Auto-detects format from file extension (`.sql` vs `.dump`).

### Create Database

```
/odoo-db create --db newproject17
/odoo-db create --db newproject17 --host localhost --port 5432
```

Equivalent to:
```bash
createdb -U odoo newproject17
```

### Drop Database

```
/odoo-db drop --db oldproject
/odoo-db drop --db oldproject --yes  # Skip confirmation
```

Prompts for confirmation: `Are you sure? [yes/N]`

### List Databases

```
/odoo-db list
/odoo-db list --host localhost --user odoo
```

Output:
```
Found 5 database(s):
  - myproject17
  - myproject17_dev
  - mydb
  - mydb
  - postgres
```

### Reset Admin Password

```
/odoo-db reset-admin --db myproject17 --password newpassword
```

Executes:
```sql
UPDATE res_users SET password='newpassword' WHERE login='admin';
```

Odoo re-hashes the password on next login.

### List Installed Modules

```
/odoo-db modules --db myproject17
```

Queries `ir_module_module` table for all installed modules.

### Auto-Backup (from Config)

```
/odoo-db auto-backup --config conf/myproject.conf --output backups/
```

Reads `dbfilter` from config, backs up all matching databases.

## Connection Options

All operations support:
```
--host localhost    (default: localhost)
--port 5432        (default: 5432)
--user odoo        (default: odoo)
--password odoo    (default: odoo)
```

## Docker Operations

```
/odoo-db backup --docker odoo_db --db myproject17
```

Executes:
```bash
docker exec odoo_db pg_dump -U odoo -Fc myproject17 > backups/myproject17_20240101.dump
```

```
/odoo-db restore --docker odoo_db --file backup.dump --db mydb
```

Executes:
```bash
docker exec -i odoo_db pg_restore -U odoo -d mydb < backup.dump
```

## Natural Language Triggers

- "backup database", "backup odoo db", "backup myproject17"
- "restore database", "restore from backup"
- "create new database", "create db newproject"
- "drop database", "delete database"
- "list databases", "show databases"
- "reset admin password", "change admin password"

## Implementation

Uses `odoo-service/scripts/db_manager.py`:

```python
from db_manager import backup_dump, restore_auto, create_database

# Backup
backup_dump("myproject17", output_dir="backups/")

# Restore
restore_auto("backups/backup.dump", "restored_db")

# Create
create_database("newproject17")
```

## Backup Schedule (Recommended)

```bash
# Windows Task Scheduler or cron (Linux)
# Daily backup at 2 AM
python db_manager.py auto-backup --config conf/myproject.conf --output backups/
```

Implement log rotation — keep last 30 days of backups:
```bash
# Linux: Remove backups older than 30 days
find backups/ -name "*.dump" -mtime +30 -delete
```
