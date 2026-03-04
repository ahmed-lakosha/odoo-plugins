# Odoo Docker Version Matrix — Quick Reference

## Core Version Table

| Version | Python | Debian | PostgreSQL | Node.js | wkhtmltopdf | Gevent Key | Entry Point |
|---------|--------|--------|------------|---------|-------------|------------|-------------|
| **14** | 3.8 | Buster (10) | 12 | No | 0.12.6-1 | `longpolling_port` | `odoo-bin` |
| **15** | 3.9 | Bullseye (11) | 12 | No | 0.12.6.1-3 | `longpolling_port` | `odoo-bin` |
| **16** | 3.10 | Bullseye (11) | 12 | No | 0.12.6.1-3 | `longpolling_port` | `odoo-bin` |
| **17** | 3.10 | Bookworm (12) | 15 | 20 LTS | 0.12.6.1-3 | `gevent_port` | `odoo-bin` |
| **18** | 3.11 | Bookworm (12) | 15 | 20 LTS | 0.12.6.1-3 | `gevent_port` | `odoo-bin` |
| **19** | 3.12 | Bookworm (12) | 15 | 20 LTS | 0.12.6.1-3 | `gevent_port` | `setup/odoo` |

## Docker Hub Image Tags

```
taqatechno/odoo:14.0-enterprise
taqatechno/odoo:15.0-enterprise
taqatechno/odoo:16.0-enterprise
taqatechno/odoo:17.0-enterprise
taqatechno/odoo:18.0-enterprise
taqatechno/odoo:19.0-enterprise
```

## Extra Dependencies by Version

| Version | Extra Packages |
|---------|---------------|
| 14 | Mako, libev-dev, fonts-noto |
| 15 | cryptography, pyopenssl |
| 17 | geoip2, rjsmin, libev-dev |
| 18 | cbor2, asn1crypto, openpyxl |
| 19 | python-magic (libmagic1), lxml-html-clean |

## Build Workarounds

| Version | Issue | Fix |
|---------|-------|-----|
| 14 | Buster EOL | Use archive.debian.org mirrors |
| 14-15 | gevent compilation | Cython<3, no-build-isolation |
| 16-17 | gevent compilation | Cython<3, no-build-isolation |
| 18 | cbor2 needs Rust | PIP_CONSTRAINT="setuptools<81" |
| 19 | No __init__.py | PYTHONPATH or editable install |
| All | setuptools 80+ | PIP_CONSTRAINT="setuptools<81" |

## wkhtmltopdf URLs

| Debian | URL |
|--------|-----|
| Buster | `wkhtmltox_0.12.6-1.buster_amd64.deb` |
| Bullseye | `wkhtmltox_0.12.6.1-3.bullseye_amd64.deb` |
| Bookworm | `wkhtmltox_0.12.6.1-3.bookworm_amd64.deb` |
