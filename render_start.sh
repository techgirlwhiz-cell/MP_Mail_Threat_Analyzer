#!/usr/bin/env bash
# Render start script: ensure we listen on $PORT so the service responds to HTTP.
set -e
cd "$(dirname "$0")"
export PORT="${PORT:-10000}"
echo "Listening on 0.0.0.0:${PORT}"
exec gunicorn --bind "0.0.0.0:${PORT}" --workers 1 --threads 4 --timeout 300 --access-logfile - --log-level info web_backend:app
