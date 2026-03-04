---
title: 'Docker Image Builder'
read_only: false
type: 'command'
description: 'Build and push Docker images for Odoo — single version or all versions, multi-platform, Docker Hub integration, and GitHub Actions CI/CD generation'
---

# /docker-build — Build & Push Docker Images

Build, tag, and push Odoo Docker images to Docker Hub. Supports single version or full matrix builds across Odoo 14-19.

## Usage

```
/docker-build [options]
/docker-build --version 19
/docker-build --all
/docker-build --generate-ci
```

## Arguments (if provided): $ARGUMENTS

## Operations

### Build Single Version

```
/docker-build --version 19
```

1. Locate or generate Dockerfile using version matrix (SKILL.md §3)
2. Build image: `docker build --build-arg PYTHON_VERSION=3.12 --build-arg ODOO_VERSION=19 -t taqatechno/odoo:19.0-enterprise .`
3. Tag with SHA: `docker tag taqatechno/odoo:19.0-enterprise taqatechno/odoo:19.0-enterprise-$(git rev-parse --short HEAD)`

### Build All Versions

```
/docker-build --all
```

Builds all 6 versions sequentially using the version matrix:

| Version | Python | Tag |
|---------|--------|-----|
| 14 | 3.10 | `taqatechno/odoo:14.0-enterprise` |
| 15 | 3.10 | `taqatechno/odoo:15.0-enterprise` |
| 16 | 3.10 | `taqatechno/odoo:16.0-enterprise` |
| 17 | 3.12 | `taqatechno/odoo:17.0-enterprise` |
| 18 | 3.12 | `taqatechno/odoo:18.0-enterprise` |
| 19 | 3.12 | `taqatechno/odoo:19.0-enterprise` |

### Push to Docker Hub

```
/docker-build --version 19 --push
/docker-build --all --push
```

Requires Docker Hub login:
```bash
docker login -u taqatechno
```

### Generate GitHub Actions CI/CD

```
/docker-build --generate-ci
```

Creates `.github/workflows/build-push.yml` using the template from SKILL.md §15:
- Matrix strategy for all 6 versions
- Multi-platform: linux/amd64 + linux/arm64
- GitHub Actions layer cache per version
- Automatic push on main branch changes
- Manual dispatch with version selection
- Required secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`

### Build with No Cache

```
/docker-build --version 19 --no-cache
```

Full rebuild without Docker layer cache. Use when:
- Requirements changed
- System package updates needed
- Base image updated

## Build Workarounds Applied Automatically

The build command automatically handles version-specific issues (SKILL.md §17):

| Version | Workaround |
|---------|-----------|
| 14 | Buster EOL → archive.debian.org mirrors |
| 14-15 | gevent 20.9.0 → Cython<3, no-build-isolation |
| 16-17 | gevent 21.8.0 → Cython<3, no-build-isolation |
| 18 | cbor2 → PIP_CONSTRAINT="setuptools<81" |
| 19 | No __init__.py → PYTHONPATH or editable install |
| All | setuptools 80+ → PIP_CONSTRAINT="setuptools<81" |

## Natural Language Triggers

- "build docker image", "build odoo image"
- "push to docker hub", "publish image"
- "ci/cd pipeline", "github actions for docker"
- "rebuild image", "update docker image"
- "build all versions", "multi-version build"
