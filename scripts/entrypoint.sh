#!/bin/sh
set -e

# ==============================================================================
# MwohaOS Container Entrypoint Script
# Waits for PostgreSQL and Redis to be ready before starting services.
# ==============================================================================

python /app/scripts/wait_for_services.py

exec "$@"
