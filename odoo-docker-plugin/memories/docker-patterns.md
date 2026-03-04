# Docker Patterns & Lessons Learned

## Performance Patterns

### workers=0 is Catastrophic for Production
- At 50 concurrent users: P50 = 9,068ms, 10% HTTP 500 errors
- Single-threaded mode serializes ALL requests
- Minimum production: workers=2
- Formula: (CPU * 2) + 1, capped by RAM / 512MB per worker

### data_dir is Non-Negotiable
- Without it: filestore goes to `~/.local/share/Odoo/` (ephemeral in containers)
- Symptoms: JS assets return HTTP 500, pages load without JavaScript
- Asset load time: 19-49s cold (without) vs 2-3s (with)
- Always set: `data_dir = /var/lib/odoo`

### Gzip Provides 90% Compression
- CSS bundle: 894 KB → 89 KB (gzip level 6)
- /web/login transfer: 65 KB → 4.3 KB
- Homepage TTFB: 176ms → 53ms
- Always use nginx with gzip in production

### Connection Pool Requires db_maxconn
- Without limit: 51+ idle connections accumulate under stress
- Risk: PostgreSQL max_connections exhaustion
- Always set: `db_maxconn = 16` per worker

## Build Patterns

### Buster EOL (Odoo 14)
- Must use archive.debian.org mirrors
- Must disable Check-Valid-Until

### gevent Compilation
- v14-15: greenlet==0.4.17 + gevent==20.9.0 + Cython<3
- v16-17: gevent==21.8.0 + Cython<3
- Always use --no-build-isolation

### setuptools 80+
- Breaks pkg_resources used by older packages
- Fix: PIP_CONSTRAINT="setuptools<81"

### Odoo 19 Entry Point
- No odoo-bin at root; uses setup/odoo
- No __init__.py; needs PYTHONPATH=/opt/odoo/source

## Deployment Patterns

### Source Mounted, Not Baked
- Image = system deps + Python packages
- Source = volume mounted at runtime (read-only)
- Benefit: no rebuild on code changes

### Asset Warm-Up
- First request after restart compiles assets: 25-120s
- Solution: warm-up service with curl to /web/login and /shop

### Multi-Project Port Convention
- HTTP = base port (e.g., 8069)
- Gevent = base + 3 (e.g., 8072)
- Debug = base + 609 (e.g., 5678)
