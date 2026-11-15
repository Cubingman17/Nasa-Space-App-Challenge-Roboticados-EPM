@echo off
rem AstroHealth AI - start the app (run setup.bat first)
rem
rem   start.bat
rem
rem Launches the backend and opens the web console at http://localhost:5000
cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo === AstroHealth AI - starting ===
echo ^>^> Backend + web console: http://localhost:5000
echo ^>^> Press Ctrl+C to stop

start "" http://localhost:5000
pushd backend
python -m uvicorn main:app --host 127.0.0.1 --port 5000
popd
