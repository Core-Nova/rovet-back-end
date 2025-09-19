#!/bin/bash
set -e

echo "Running database migrations..."
poetry run alembic upgrade head || echo "Migration failed but continuing..."

echo "Starting the service..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 3001