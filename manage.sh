#!/bin/bash

# Configuration
SERVICE_API_DIR="./services/api"
SERVICE_FRONTEND_DIR="./services/frontend"
DB_NAME="propai"
DB_USER="postgres"

case "$1" in
  # --- Service Control ---
  start)
    echo "Starting all services..."
    docker-compose up -d redis postgres
    cd $SERVICE_API_DIR && DATABASE_URL="postgresql+psycopg2://$DB_USER:bismillah123@localhost:5432/$DB_NAME" uvicorn propai_api.main:app --host 0.0.0.0 --port 8000 &
    cd ../frontend && npm run dev &
    ;;
  stop)
    echo "Stopping services..."
    pkill -f uvicorn
    pkill -f node
    docker-compose stop
    ;;

  # --- Database & Alembic ---
  db-generate)
    echo "Generating database models/schema..."
    # (Optional: Logic to sync ORM models if needed)
    ;;
  db-migrate)
    echo "Running Alembic migrations..."
    alembic -c alembic.ini upgrade head
    ;;
  db-rollback)
    echo "Rolling back one step..."
    alembic -c alembic.ini downgrade -1
    ;;
  db-reset)
    echo "WARNING: Resetting database..."
    psql -U $DB_USER -d postgres -c "DROP DATABASE $DB_NAME;"
    psql -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"
    alembic -c alembic.ini upgrade head
    ;;

  *)
    echo "Usage: $0 {start|stop|db-generate|db-migrate|db-rollback|db-reset}"
    exit 1
esac