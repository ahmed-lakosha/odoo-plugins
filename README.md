# ☁️ Odoo Marketplace — Odoo Plugins for Claude Code

> **7 professional Odoo development plugins** for [Claude Code](https://claude.ai/code) — covering the full Odoo development lifecycle from upgrade migrations to testing, security, internationalization, and server lifecycle management.

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin%20Marketplace-blue)](https://claude.ai/code)
[![Odoo Versions](https://img.shields.io/badge/Odoo-14%20→%2019-purple)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-green)](./LICENSE)

---

## Quick Install

```bash
# Install all 7 Odoo plugins at once
claude mcp add cloud-market [https://github.com/ahmed-lakosha/odoo-plugins.git]
```

Or install individual plugins from the marketplace by referencing this repo.

---

## Plugins

### 🔄 odoo-upgrade
**Comprehensive Odoo module upgrade assistant for migrating between versions (14-19)**

Handles XML view transformations (`<tree>`→`<list>`, `attrs`→inline), Python API changes,
OWL 1.x→2.0 lifecycle hooks, controller type migrations, SCSS variable restructuring,
and RPC service replacements. Includes 150+ patterns and 75+ auto-fixes.

Commands: `/odoo-upgrade`

---

### 🎨 odoo-frontend
**Odoo website theme development with MCP integration and Bootstrap version management**

Full publicWidget framework, dark mode toggle patterns, RTL/LTR switcher, Figma→Odoo
conversion, `$o-website-values-palettes` reference, theme mirror model architecture,
and OWL 2.0 component patterns for Odoo 18+.

Commands: `/odoo-frontend`, `/create-theme`, `/theme_web_rec`

---

### 📄 odoo-report
**Professional Odoo QWeb reports & email templates toolkit across Odoo 14-19**

Create, debug, migrate, and validate QWeb PDF reports and email templates. Includes
QR code/barcode patterns (ZATCA/Saudi), Report Wizard templates, bilingual Arabic/English
layouts, and Odoo 19 company branding migration guide.

Commands: `/odoo-report`, `/create-qweb-report`, `/create-email-template`, `/debug-template`,
`/migrate-template`, `/validate-template`, `/fix-template`, `/preview-template`

---

### 🧪 odoo-test
**Odoo testing toolkit — test generation, mock data, coverage analysis (v14-19)**

Generate `TransactionCase` test skeletons from model definitions using AST parsing,
run tests with colored output and JUnit XML reports, create realistic mock data by
field type, and analyze test coverage gaps with HTML/JSON reports.

Commands: `/odoo-test`, `/test-generate`, `/test-run`, `/test-coverage`, `/test-data`

---

### 🔒 odoo-security
**Odoo security audit — access rules, route auth, sudo() analysis with risk scoring**

Audit `ir.model.access.csv` completeness, verify `@http.route auth=` parameters,
analyze every `sudo()` call with context classification (CRITICAL/HIGH/MEDIUM/LOW),
and generate a unified risk score (0-100) with remediation guidance. CI-ready with
exit codes.

Commands: `/odoo-security`, `/security-audit`, `/check-access`, `/find-sudo`, `/check-routes`

---

### 🌐 odoo-i18n
**Odoo i18n toolkit — extract, validate, report missing translations, Arabic/RTL (v14-19)**

Extract translatable strings from Python/XML/JS/QWeb to `.pot`/`.po` files using AST
parsing, validate translation completeness with Arabic plural form support (nplurals=6),
find missing translations by language, and merge/clean/convert `.po` files. Full
Arabic/RTL layout patterns included.

Commands: `/odoo-i18n`, `/i18n-extract`, `/i18n-missing`, `/i18n-validate`, `/i18n-export`

---

### ⚙️ odoo-service
**Complete Odoo server lifecycle manager — run, deploy, initialize across any environment and IDE**

Start/stop Odoo with auto-detection of local venv or Docker, initialize new environments
(venv + PostgreSQL + .conf generation), manage databases (pg_dump backup/restore, create/drop,
admin reset), orchestrate Docker (build, up, down, logs, shell, Dockerfile generation for
all versions 14-19), and generate IDE configurations for PyCharm and VSCode automatically.

Commands: `/odoo-service`, `/odoo-start`, `/odoo-stop`, `/odoo-init`, `/odoo-db`, `/odoo-docker`, `/odoo-ide`

---

## Odoo Version Support

| Plugin | 14 | 15 | 16 | 17 | 18 | 19 |
|--------|----|----|----|----|----|----|
| odoo-upgrade | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| odoo-frontend | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| odoo-report | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| odoo-test | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| odoo-security | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| odoo-i18n | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| odoo-service | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Repository Structure

```
cloud-market/
├── .claude-plugin/
│   └── marketplace.json          ← Plugin registry (v1.1.0, 7 plugins)
├── odoo-upgrade-plugin/          ← Upgrade migration toolkit
├── odoo-frontend-plugin/         ← Theme & frontend development
├── odoo-report-plugin/           ← QWeb reports & email templates
├── odoo-test-plugin/             ← Testing & coverage
├── odoo-security-plugin/         ← Security audit
├── odoo-i18n-plugin/             ← Internationalization
├── odoo-service-plugin/          ← Server lifecycle & deployment
├── validate_plugin.py            ← Plugin validation utility
├── CLAUDE_CODE_PLUGIN_DEVELOPMENT_GUIDE.md
└── LICENSE
```

---

## Author

**ahmed-lakosha** — [ahmed.lakosha94@gmail.com](mailto:ahmed.lakosha94@gmail.com)

---

## License

[LGPL-3](./LICENSE)
