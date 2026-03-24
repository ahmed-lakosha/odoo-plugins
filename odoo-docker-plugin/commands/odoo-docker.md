---
title: 'Odoo Docker Infrastructure'
read_only: false
type: 'command'
description: 'Docker infrastructure for Odoo - init, compose, deploy, build, and status'
argument-hint: '[init|compose|deploy|build] [args...]'
---

# /odoo-docker - Unified Docker Infrastructure

Parse `$ARGUMENTS` and route to the appropriate operation:

| Sub-command | Description | Example |
|-------------|-------------|---------|
| `init` | Initialize Docker project structure | `/odoo-docker init --project relief_center` |
| `compose` | Generate docker-compose for dev/staging/prod | `/odoo-docker compose dev --version 19` |
| `deploy` | Full production deployment with nginx + SSL | `/odoo-docker deploy --domain example.com` |
| `build` | Build, tag, and push Docker images | `/odoo-docker build 19` or `build --all` |
| *(none)* | Show Docker status + help | `/odoo-docker` |

## Status (no args)

Run `docker info` and `docker --version` to check Docker. Scan for `docker-compose*.yml`, `conf/*.conf`, and `odoo/release.py` to detect existing projects. Display the help table above.

## Execution

Use the odoo-docker skill for:
- Architecture decisions (source-mounted vs baked-in)
- Version matrix (PostgreSQL versions, Python versions per Odoo 14-19)
- Template placeholders and configuration notes
- Performance tuning (workers, PostgreSQL, gzip)
- Security hardening and SSL/TLS
- CI/CD pipeline patterns
- Troubleshooting and debugging

Check `~/.claude/odoo-docker.local.md` for user-specific `image_prefix`, `default_version`, and other settings. Replace `{image_prefix}` in generated configs with the user's value (or ask on first use).

Templates are in `${CLAUDE_PLUGIN_ROOT}/templates/`.
