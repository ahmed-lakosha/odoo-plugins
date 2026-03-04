---
title: 'Nginx Configuration Generator'
read_only: false
type: 'command'
description: 'Generate optimized nginx reverse proxy configuration for Odoo with gzip, WebSocket, caching, rate limiting, and optional SSL'
---

# /docker-nginx — Nginx Configuration Generator

Generate an optimized nginx reverse proxy configuration for Odoo Docker deployments. Includes gzip compression (90% CSS reduction), WebSocket routing, static asset caching, rate limiting, and optional SSL/TLS.

## Usage

```
/docker-nginx
/docker-nginx --ssl --domain example.com
/docker-nginx --gzip-level 6 --rate-limit 10
```

## Arguments (if provided): $ARGUMENTS

## Interactive Flow

### Step 1: Gather Requirements

Use `AskUserQuestion` for:
1. **Domain name** (or `_` for any): server_name
2. **SSL/HTTPS**: Enable with Let's Encrypt?
3. **Gzip level**: 1-9 (default: 6, optimal balance)
4. **Rate limiting**: requests/second per IP (default: 10)
5. **Upload limit**: max body size (default: 200m)
6. **Asset cache duration**: (default: 365d for /web/assets/, 7d for /web/static/)

### Step 2: Generate nginx.conf

Use the complete, stress-test-proven configuration from SKILL.md §8:

**Core features always included:**
- Rate limiting zone
- Upstream definitions (odoo:8069, odoo-websocket:8072)
- Proxy buffering (16 × 64k)
- Gzip compression with optimized MIME types
- WebSocket routing for `/websocket`
- Static asset caching with immutable headers
- Health check passthrough (no rate limiting)
- Proxy headers (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
- Timeouts (600s for all proxy operations)

**Optional SSL block (when --ssl):**
- HTTP → HTTPS redirect
- TLS 1.2 + 1.3
- Let's Encrypt certificate paths
- HSTS header

### Step 3: Generate Docker Compose nginx Service

```yaml
nginx:
  image: nginx:alpine
  container_name: {project}_nginx
  volumes:
    - ./conf/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    # If SSL:
    # - /etc/letsencrypt:/etc/letsencrypt:ro
  ports:
    - "80:80"
    # If SSL:
    # - "443:443"
  depends_on:
    odoo:
      condition: service_healthy
  restart: unless-stopped
```

### Step 4: Update Odoo Config

Remind user to set in `odoo.conf`:
```ini
proxy_mode = True    ; REQUIRED behind nginx
```

### Step 5: Display Performance Impact

```
Expected Performance Impact (verified via stress tests):
  CSS bundle: 894 KB → 89 KB (90% reduction)
  /web/login: 65 KB → 4.3 KB (93% reduction)
  Homepage TTFB: 176 ms → 53 ms (70% faster)
```

## Configuration Reference

### Gzip MIME Types

```
text/plain text/css text/javascript text/xml
application/javascript application/json application/xml
application/xml+rss image/svg+xml font/woff2
```

### Cache Headers

| Path | Duration | Cache-Control |
|------|----------|---------------|
| `/web/assets/` | 365 days | `public, immutable` |
| `/web/static/` | 7 days | `public` |
| All other | No caching | — |

### Rate Limiting

Default: 10 requests/second per IP, burst 20, nodelay
- Health check (`/web/health`) bypasses rate limiting
- WebSocket (`/websocket`) bypasses rate limiting

## Natural Language Triggers

- "configure nginx for odoo", "add reverse proxy"
- "enable gzip", "optimize nginx"
- "ssl setup for odoo", "add https"
- "nginx configuration", "reverse proxy"
- "enable asset caching", "nginx rate limiting"
