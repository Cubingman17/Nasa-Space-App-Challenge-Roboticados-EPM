#!/usr/bin/env bash
# AstroHealth AI - one-command setup (Linux / macOS / Git Bash on Windows)
#
#   ./setup.sh
#
# Installs the Python dependencies, sets up the local AI model (optional),
# imports the metric datasets and launches the app at http://localhost:5000
set -e
cd "$(dirname "$0")"

echo "=== AstroHealth AI - setup ==="

# 1. Python virtual environment + dependencies
if [ ! -d .venv ]; then
    echo ">> Creating virtual environment (.venv)"
    python -m venv .venv
fi
if [ -f .venv/Scripts/activate ]; then
    # Windows (Git Bash)
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

echo ">> Installing Python dependencies"
python -m pip install -q -r requirements.txt

# 2. Local AI model (optional: the app falls back to rule-based advice)
if command -v ollama >/dev/null 2>&1; then
    echo ">> Setting up the local AI model (AstroAI, ~2 GB download on first run)"
    (cd backend/ai && python setup_ollama.py) \
        || echo "!! Ollama setup skipped - the app will use the rule-based fallback"
else
    echo "!! Ollama is not installed - get it from https://ollama.com/download"
    echo "   The app works without it (rule-based fallback + metric summary)."
fi

# 3. Import the metric datasets into the local database
echo ">> Importing metric datasets"
(cd backend && python -m services.import_datasets)

echo ""
echo "=== Setup complete ==="
echo ">> Start the app any time with:  ./start.sh"
