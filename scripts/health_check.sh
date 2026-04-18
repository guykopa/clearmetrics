#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-http://localhost:8000}"
DB_URL="${DATABASE_URL:-}"
EXIT_CODE=0

echo "=== clearmetrics health check ==="

# API health
echo -n "[API] ${APP_URL}/health ... "
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${APP_URL}/health")
if [ "${HTTP_STATUS}" = "200" ]; then
  echo "OK"
else
  echo "FAIL (HTTP ${HTTP_STATUS})"
  EXIT_CODE=1
fi

# Prometheus metrics endpoint
echo -n "[API] ${APP_URL}/metrics ... "
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${APP_URL}/metrics")
if [ "${HTTP_STATUS}" = "200" ]; then
  echo "OK"
else
  echo "FAIL (HTTP ${HTTP_STATUS})"
  EXIT_CODE=1
fi

# PostgreSQL
if [ -n "${DB_URL}" ]; then
  echo -n "[DB]  PostgreSQL ... "
  if python3 -c "
import sqlalchemy, os
engine = sqlalchemy.create_engine(os.environ['DATABASE_URL'])
engine.connect()
" 2>/dev/null; then
    echo "OK"
  else
    echo "FAIL"
    EXIT_CODE=1
  fi
else
  echo "[DB]  Skipped (DATABASE_URL not set)"
fi

# Prometheus
echo -n "[MON] Prometheus (port 9090) ... "
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:9090/-/healthy" | grep -q "200"; then
  echo "OK"
else
  echo "FAIL"
  EXIT_CODE=1
fi

# Grafana
echo -n "[MON] Grafana (port 3000) ... "
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/api/health" | grep -q "200"; then
  echo "OK"
else
  echo "FAIL"
  EXIT_CODE=1
fi

echo "================================="
if [ "${EXIT_CODE}" -eq 0 ]; then
  echo "All checks passed."
else
  echo "Some checks failed."
fi

exit "${EXIT_CODE}"
