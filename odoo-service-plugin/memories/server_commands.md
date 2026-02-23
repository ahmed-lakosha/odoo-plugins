# Odoo Server Commands Reference

Complete reference for all Odoo server startup flags, configuration options, module management commands, and version-specific differences.

---

## 1. Startup Command Reference

### Base Command Forms

```bash
# Form 1: Python module (recommended for venv, Windows-friendly)
python -m odoo [flags]

# Form 2: odoo-bin script (Linux/Mac direct execution)
python odoo-bin [flags]
./odoo-bin [flags]  # If executable bit set

# Form 3: Full path (bare Python, no venv)
/path/to/python -m odoo [flags]
C:\Python311\python.exe -m odoo [flags]
```

---

## 2. Core Startup Flags

### Configuration File

```bash
-c, --config FILE     # Path to .conf file
                      # REQUIRED for anything beyond simple testing
python -m odoo -c conf/TAQAT17.conf
```

### Database Selection

```bash
-d, --database DB     # Connect to specific database
                      # Overrides db_name in config

python -m odoo -c conf/project.conf -d mydb
```

### Port Override

```bash
--http-port PORT      # HTTP server port (overrides config)
--gevent-port PORT    # Longpolling port (v17+, overrides config)

python -m odoo -c conf/project.conf --http-port=8070
```

---

## 3. Development Mode Flags

### --dev Options (Can Combine)

```bash
# Full development mode (recommended — enables all below)
--dev=all

# Individual options:
--dev=reload    # Auto-reload Python files on change
--dev=qweb      # Detailed QWeb template error reporting
--dev=werkzeug  # Enable Werkzeug interactive debugger
--dev=xml       # Show XML validation errors in browser
--dev=tests     # Load test tags at startup
```

```bash
# Development startup (most common for developers)
python -m odoo -c conf/TAQAT17.conf --dev=all

# Auto-reload only (lighter than all)
python -m odoo -c conf/TAQAT17.conf --dev=reload
```

### Development Mode Behavior

When `--dev=all` is active:
- Python files: auto-reloaded on change (SIGINT + restart)
- JS/CSS assets: recompiled on next page load (no manual update)
- XML templates: re-read on each request (slower but no restart)
- Error tracebacks: shown in browser, not just logs
- Session: persists across reloads

---

## 4. Module Management Flags

### Install Module(s)

```bash
-i, --init MODULE     # Install module(s) on startup
                      # Comma-separated for multiple

python -m odoo -c conf/proj.conf -d mydb -i my_module --stop-after-init
python -m odoo -c conf/proj.conf -d mydb -i module1,module2,module3 --stop-after-init
```

### Update Module(s)

```bash
-u, --update MODULE   # Update existing module(s)
                      # Comma-separated for multiple
                      # Use 'all' to update everything (slow)

python -m odoo -c conf/proj.conf -d mydb -u my_module --stop-after-init
python -m odoo -c conf/proj.conf -d mydb -u all --stop-after-init
```

### --stop-after-init

```bash
--stop-after-init     # Stop server after initialization
                      # ALWAYS use with -i and -u
                      # Without this flag, server keeps running
```

### Update Module List

```bash
--update-list         # Refresh the list of available modules
                      # Required before installing NEW modules

python -m odoo -c conf/proj.conf -d mydb --update-list
```

---

## 5. Worker Process Flags

```bash
--workers N           # Number of worker processes
                      # 0 = single-threaded (development)
                      # > 0 = multi-worker (production)
                      # Recommended: 2 * CPU_cores + 1

--max-cron-threads N  # Background job worker count
                      # Default: 2

# Production startup
python -m odoo -c conf/proj.conf --workers=4 --max-cron-threads=2
```

### Worker Type Notes

- **Workers = 0**: Single-threaded, blocking, good for development
- **Workers = 1-N**: Prefork architecture, each worker is independent
- **Cron workers**: Handle scheduled actions, email sending, etc.
- **Gevent worker**: Handles longpolling/live chat (always 1)

---

## 6. Database Initialization Flags

```bash
# Create new database and initialize
python odoo-bin -d newdb -i base --stop-after-init

# With specific demo data
python odoo-bin -d demo_db --without-demo=all -i base --stop-after-init

# Exclude demo data (production-like)
python odoo-bin -d prod_db --without-demo=all -i base,sale,crm --stop-after-init
```

---

## 7. Interactive Shell

```bash
# Open interactive Python shell with Odoo environment
python odoo-bin shell -d DATABASE
python odoo-bin shell -d DATABASE -c conf/project.conf

# Shell with specific module path
python odoo-bin shell -d DATABASE --addons-path=odoo/addons,projects/myproject
```

### Shell Usage Patterns

```python
# Access models
env['res.partner'].search([], limit=5)

# Current user
env.user.name
env.user.id
env.user.company_id.name

# CRUD operations
record = env['res.partner'].create({'name': 'Test', 'is_company': True})
record.write({'email': 'test@example.com'})
record.unlink()

# Commit changes (REQUIRED after writes)
env.cr.commit()

# Rollback
env.cr.rollback()

# System parameters
env['ir.config_parameter'].sudo().get_param('web.base.url')
env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://mysite.com')
env.cr.commit()

# Raw SQL
env.cr.execute("SELECT id, name FROM res_partner WHERE is_company = true LIMIT 5")
rows = env.cr.fetchall()
for row in rows:
    print(row)

# List installed modules
modules = env['ir.module.module'].search([('state', '=', 'installed')])
print([m.name for m in modules])

# Check module state
env['ir.module.module'].search([('name', '=', 'sale')])[0].state

# Upgrade module in shell (not recommended, use CLI instead)
env['ir.module.module'].search([('name', '=', 'my_module')]).button_immediate_upgrade()
env.cr.commit()
```

---

## 8. Logging and Debug Flags

```bash
# Log level
--log-level LEVEL     # debug, info, warning, error, critical

# Log to file
--logfile PATH        # Path to log file (default: stderr/stdout)

# Log specific handlers
--log-handler :DEBUG  # Enable debug for all
--log-handler odoo.models:DEBUG   # Debug for models only
--log-handler werkzeug:WARNING    # Suppress werkzeug noise

# Log to syslog
--syslog              # Use system syslog

# Examples
python -m odoo -c conf/proj.conf --log-level=debug
python -m odoo -c conf/proj.conf --logfile=logs/odoo.log
python -m odoo -c conf/proj.conf --log-handler=odoo.addons.my_module:DEBUG
```

---

## 9. Test Commands

```bash
# Run tests for specific module
python odoo-bin -c conf/proj.conf -d testdb --test-enable -i my_module --stop-after-init

# Run with specific test tags
python odoo-bin -c conf/proj.conf -d testdb --test-enable --test-tags=my_module --stop-after-init

# Run post-install tests
python odoo-bin -c conf/proj.conf -d testdb --test-enable --test-tags=post_install --stop-after-init

# Standard test tags:
# @tagged('post_install', '-at_install')  — Run after install
# @tagged('at_install')                   — Run during install
# @tagged('standard')                     — Standard tests
# @tagged('-standard')                    — Exclude standard tests
```

---

## 10. Version-Specific Differences

### Odoo 14 vs 17+ Port Flag

```bash
# Odoo 14-16 (longpolling_port)
[options]
longpolling_port = 8072

# Odoo 17+ (gevent_port)
[options]
gevent_port = 8072

# Command line override
# v14-16:
python -m odoo --longpolling-port=8072

# v17+:
python -m odoo --gevent-port=8072
```

### Odoo 17+ Asset Pipeline

```bash
# Force asset recompilation (v17+)
python -m odoo -c conf/proj.conf -d db -u web --stop-after-init

# Clear assets cache (v17+)
python odoo-bin -c conf/proj.conf -d db --test-enable --test-tags=clear_caches --stop-after-init
```

### Odoo 16+ Workers

```bash
# Odoo 16+ uses gevent for longpolling differently
# Workers > 0 required for longpolling in 16+
python -m odoo -c conf/proj.conf --workers=2
```

---

## 11. Quick Reference Table

| Task | Command |
|------|---------|
| Start (dev) | `python -m odoo -c conf/X.conf --dev=all` |
| Start (prod) | `python -m odoo -c conf/X.conf --workers=4` |
| Install module | `python -m odoo -c conf/X.conf -d DB -i MODULE --stop-after-init` |
| Update module | `python -m odoo -c conf/X.conf -d DB -u MODULE --stop-after-init` |
| Update all | `python -m odoo -c conf/X.conf -d DB -u all --stop-after-init` |
| Refresh module list | `python -m odoo -c conf/X.conf -d DB --update-list` |
| Interactive shell | `python odoo-bin shell -d DB` |
| Run tests | `python odoo-bin -c conf/X.conf -d testdb --test-enable -i MODULE --stop-after-init` |
| Create new DB | `python odoo-bin -d NEWDB -i base --stop-after-init` |
| Scaffold module | `python odoo-bin scaffold MODULE_NAME projects/myproject/` |
| Debug mode | `python -m odoo -c conf/X.conf --dev=all` |

---

## 12. Config File Options Reference

Complete list of `[options]` keys in .conf file:

```ini
[options]
# --- Addon Paths ---
addons_path = odoo\addons,projects\myproject

# --- Admin ---
admin_passwd = secretpassword

# --- Database ---
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
db_name = False             # False = no default db
db_filter = myproject.*     # Regex filter
db_maxconn = 64             # Max connections per worker
db_template = template1     # Template for new databases

# --- Network ---
http_interface = 0.0.0.0   # Bind address
http_port = 8069            # HTTP port
gevent_port = 8072          # Longpolling port (v17+)
longpolling_port = 8072     # Longpolling port (v14-16)

# --- Workers ---
workers = 0                 # 0=single-threaded
max_cron_threads = 2        # Background job workers

# --- Memory ---
limit_memory_soft = 2147483648    # 2GB soft limit
limit_memory_hard = 2684354560    # 2.5GB hard limit

# --- Time ---
limit_time_cpu = 600        # CPU time per request
limit_time_real = 1200      # Wall clock per request
limit_time_real_cron = 1800 # Cron task time limit

# --- Proxy ---
proxy_mode = False          # True if behind nginx

# --- Logging ---
logfile = logs/odoo.log     # Log file (False=console)
log_level = info            # debug|info|warning|error|critical
syslog = False              # Use syslog

# --- Data ---
data_dir = data             # Filestore and session path

# --- Email ---
smtp_server = localhost
smtp_port = 25
smtp_ssl = False
smtp_user = False
smtp_password = False

# --- Reporting ---
# wkhtmltopdf_command = wkhtmltopdf

# --- Testing ---
test_enable = False
test_file = False
test_tags = False
```

---

## 13. Scaffold Module Structure

```bash
python odoo-bin scaffold my_module projects/myproject/
```

Creates:
```
my_module/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── controllers.py
├── demo/
│   └── demo.xml
├── models/
│   ├── __init__.py
│   └── models.py
├── security/
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       ├── scss/
│       └── xml/
└── views/
    └── views.xml
```

---

## 14. Common Command Patterns

### Development Workflow

```bash
# 1. Activate venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux

# 2. Start in dev mode
python -m odoo -c conf/TAQAT17.conf --dev=all

# 3. After code changes (Python/XML) — in another terminal
python -m odoo -c conf/TAQAT17.conf -d taqat17 -u my_module --stop-after-init

# 4. Restart server (dev mode picks up automatically, but restart ensures clean state)
# Ctrl+C to stop, then:
python -m odoo -c conf/TAQAT17.conf --dev=all
```

### Module Installation Flow

```bash
# New module — must run refresh first
python -m odoo -c conf/proj.conf -d mydb --update-list
# Then install
python -m odoo -c conf/proj.conf -d mydb -i my_new_module --stop-after-init
```

### Production Deployment Flow

```bash
# 1. Stop current server
sudo systemctl stop odoo17

# 2. Pull latest code
git pull origin main

# 3. Install new dependencies
.venv/bin/pip install -r requirements.txt

# 4. Update modules
python -m odoo -c conf/TAQAT17.conf -d mydb -u my_module --stop-after-init

# 5. Restart server
sudo systemctl start odoo17
```
