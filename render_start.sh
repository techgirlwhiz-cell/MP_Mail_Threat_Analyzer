#!/usr/bin/env bash
# Render start script: ensure we listen on $PORT so the service responds to HTTP.
set -e
PORT="${PORT:-10000}"
echo "Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn --bind "0.0.0.0:${PORT}" --workers 1 --threads 2 --timeout 120 web_backend:app
