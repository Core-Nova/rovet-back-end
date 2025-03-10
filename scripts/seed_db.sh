#!/bin/bash
set -e

# Function to test if postgres is ready and create database if needed
postgres_ready() {
    python << END
import sys
import psycopg2
try:
    # First try to connect to postgres database to check if server is up
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="db",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Check if our target database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname='app_db'")
    if cur.fetchone() is None:
        # Create database if it doesn't exist
        cur.execute("CREATE DATABASE app_db")
    
    cur.close()
    conn.close()
    
    # Now try to connect to the target database
    psycopg2.connect(
        dbname="app_db",
        user="postgres",
        password="postgres",
        host="db",
        port="5432"
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
count=0
until postgres_ready; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  count=$((count+1))
  if [ $count -gt 30 ]; then
    >&2 echo "PostgreSQL is unavailable - giving up"
    exit 1
  fi
  sleep 1
done
>&2 echo "PostgreSQL is up - executing migrations"

# Run migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Run the seeding script
echo "Seeding the database..."
poetry run python -m app.scripts.seed_db

echo "Database setup completed!" 