#!/bin/bash

# Run migrations
poetry run alembic upgrade head

# Start the service
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001