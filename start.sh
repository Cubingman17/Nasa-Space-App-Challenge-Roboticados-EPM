#!/usr/bin/env bash
# AstroHealth AI - start the app (run ./setup.sh first)
#
#   ./start.sh
#
# Launches the backend and opens the web console at http://localhost:5000
set -e
cd "$(dirname "$0")"

if [ -f .venv/Scripts/activate ]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

echo "=== AstroHealth AI - starting ==="
echo ">> Backend + web console: http://localhost:5000"
echo ">> Press Ctrl+C to stop"

(cd backend && exec python -m uvicorn main:app --host 127.0.0.1 --port 5000)
