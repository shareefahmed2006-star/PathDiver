@echo off
title PathDiver
cd /d "%~dp0"
echo ========================================================
echo   Starting PathDiver Application...
echo   Intelligent File Traversal & Storage Manager
echo ========================================================

if exist "PathDiver.exe" (
    start "" "PathDiver.exe"
    exit /b 0
)

python desktop_main.py
if errorlevel 1 (
    echo.
    echo [Info] Launching browser web server mode...
    start http://127.0.0.1:8000
    python server.py 8000
)
