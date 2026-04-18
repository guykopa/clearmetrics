#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL environment variable is required}"

echo "[init_db] Waiting for PostgreSQL to be ready..."
until python3 -c "
import sqlalchemy
engine = sqlalchemy.create_engine('${DATABASE_URL}')
engine.connect()
" 2>/dev/null; do
  echo "[init_db] PostgreSQL not ready yet — retrying in 2s..."
  sleep 2
done

echo "[init_db] PostgreSQL is ready. Creating tables..."
python3 -c "
from sqlalchemy import create_engine
import os
from clearmetrics.adapters.outbound.postgresql_models import Base

engine = create_engine(os.environ['DATABASE_URL'])
Base.metadata.create_all(engine)
print('[init_db] Tables created successfully.')
"

echo "[init_db] Done."
