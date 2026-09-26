#!/usr/bin/env python3
"""
MwohaOS Service Readiness Check
Verifies PostgreSQL and Redis availability before starting services.
"""
import os
import sys
import time
from urllib.parse import urlparse

def wait_for_postgres(database_url: str, timeout: int = 60) -> bool:
    if not database_url or not database_url.startswith(("postgres://", "postgresql://")):
        return True

    parsed = urlparse(database_url)
    host = parsed.hostname or "postgres"
    port = parsed.port or 5432
    user = parsed.username or "mwohaos"
    password = parsed.password or "mwohaos"
    dbname = parsed.path.lstrip("/") or "mwohaos"

    print(f"[MwohaOS] Waiting for PostgreSQL at {host}:{port} (db: {dbname})...")
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname,
                connect_timeout=3,
            )
            conn.close()
            print("[MwohaOS] ✓ PostgreSQL is ready.")
            return True
        except Exception as exc:
            time.sleep(1)
            
    print(f"[MwohaOS] ✗ Timed out waiting for PostgreSQL ({exc})", file=sys.stderr)
    return False

def wait_for_redis(redis_url: str, timeout: int = 30) -> bool:
    if not redis_url:
        return True

    print(f"[MwohaOS] Waiting for Redis at {redis_url}...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            import redis
            client = redis.from_url(redis_url, socket_connect_timeout=3)
            if client.ping():
                print("[MwohaOS] ✓ Redis is ready.")
                return True
        except Exception as exc:
            time.sleep(1)

    print(f"[MwohaOS] ✗ Timed out waiting for Redis ({exc})", file=sys.stderr)
    return False

if __name__ == "__main__":
    db_url = os.environ.get("DATABASE_URL", "postgresql://mwohaos:mwohaos@postgres:5432/mwohaos")
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    # In local/docker environments wait for dependencies
    if os.environ.get("SKIP_WAIT_FOR_SERVICES") != "true":
        pg_ok = wait_for_postgres(db_url)
        redis_ok = wait_for_redis(redis_url)
        if not (pg_ok and redis_ok):
            print("[MwohaOS] Service readiness check failed.", file=sys.stderr)
            sys.exit(1)
    sys.exit(0)
