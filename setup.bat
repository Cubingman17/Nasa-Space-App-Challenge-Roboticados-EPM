@echo off
rem AstroHealth AI - one-command setup (Windows CMD / PowerShell)
rem
rem   setup.bat
rem
rem Installs the Python dependencies, sets up the local AI model (optional),
rem imports the metric datasets and tells you how to start the app.
cd /d "%~dp0"

echo === AstroHealth AI - setup ===

if not exist .venv (
    echo ^>^> Creating virtual environment (.venv)
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo ^>^> Installing Python dependencies
python -m pip install -q -r requirements.txt

where ollama >nul 2>&1
if %errorlevel%==0 (
    echo ^>^> Setting up the local AI model (AstroAI, ~2 GB download on first run)
    pushd backend\ai
    python setup_ollama.py
    popd
    if errorlevel 1 echo !! Ollama setup skipped - the app will use the rule-based fallback
) else (
    echo !! Ollama is not installed - get it from https://ollama.com/download
    echo    The app works without it (rule-based fallback + metric summary).
)

echo ^>^> Importing metric datasets
pushd backend
python -m services.import_datasets
popd

echo.
echo === Setup complete ===
echo ^>^> Start the app any time with:  start.bat
