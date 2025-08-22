#!/bin/sh
redis-server --daemonize yes
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

#set -e
#
#echo "Running Alembic migrations"
#alembic upgrade head
#
#echo "Starting FastAPI server..."
#uvicorn main:app --host 0.0.0.0 --port 8000