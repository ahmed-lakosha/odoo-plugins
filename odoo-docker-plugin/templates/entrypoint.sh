#!/bin/bash
set -e

# =============================================================
# Universal Odoo Entrypoint Script
# Supports Odoo 14-19, dev mode, and remote debugging
# =============================================================

# Validate Odoo source is mounted
if [ ! -f "/opt/odoo/source/setup/odoo" ] && [ ! -f "/opt/odoo/source/odoo-bin" ]; then
    echo "ERROR: Odoo source not found at /opt/odoo/source"
    echo "  Mount your Odoo source code to /opt/odoo/source"
    echo "  Example: -v /path/to/odoo:/opt/odoo/source:ro"
    exit 1
fi

# PYTHONPATH — avoids slow editable install
export PYTHONPATH=/opt/odoo/source:${PYTHONPATH:-}

# Auto-detect entry point
# v19 uses setup/odoo (no odoo-bin at root)
# v14-18 use odoo-bin
if [ -f "/opt/odoo/source/setup/odoo" ]; then
    ODOO_BIN="python /opt/odoo/source/setup/odoo"
    echo "[entrypoint] Detected Odoo 19+ (setup/odoo)"
else
    ODOO_BIN="python /opt/odoo/source/odoo-bin"
    echo "[entrypoint] Detected Odoo 14-18 (odoo-bin)"
fi

# Wait for database (optional)
if [ "${WAIT_FOR_DB:-0}" = "1" ]; then
    echo "[entrypoint] Waiting for database..."
    for i in $(seq 1 30); do
        if pg_isready -h db -p 5432 -U ${POSTGRES_USER:-odoo} > /dev/null 2>&1; then
            echo "[entrypoint] Database ready."
            break
        fi
        echo "[entrypoint] Waiting for database... ($i/30)"
        sleep 1
    done
fi

# Override log level (optional)
if [ -n "${LOG_LEVEL:-}" ]; then
    set -- "$@" --log-level="${LOG_LEVEL}"
    echo "[entrypoint] Log level: ${LOG_LEVEL}"
fi

# Extra arguments (optional)
if [ -n "${ODOO_EXTRA_ARGS:-}" ]; then
    set -- "$@" ${ODOO_EXTRA_ARGS}
    echo "[entrypoint] Extra args: ${ODOO_EXTRA_ARGS}"
fi

# Dev mode (auto-reload on file changes)
if [ "${DEV_MODE:-0}" = "1" ]; then
    set -- "$@" --dev=all
    echo "[entrypoint] DEV_MODE enabled: --dev=all"
fi

# Remote debugger (debugpy on port 5678)
if [ "${ENABLE_DEBUGGER:-0}" = "1" ]; then
    pip install --user --quiet debugpy 2>/dev/null || true
    echo "[entrypoint] Debugger enabled: waiting for IDE on port 5678..."
    exec python -m debugpy --listen 0.0.0.0:5678 --wait-for-client \
        /opt/odoo/source/setup/odoo "$@"
fi

echo "[entrypoint] Starting Odoo..."
exec $ODOO_BIN "$@"
