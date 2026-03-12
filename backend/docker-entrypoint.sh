#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "import os; import asyncio; import asyncpg; asyncio.run(asyncpg.connect(os.environ['DATABASE_URL'].replace('postgresql+asyncpg://','postgresql://')).close())" 2>/dev/null; do
  sleep 1
done

echo "Running migrations..."
alembic upgrade head

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

