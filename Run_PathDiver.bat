@echo off
title PathDiver
cd /d "%~dp0"
echo ========================================================
echo   Starting PathDiver Desktop Application...
echo   Intelligent File Traversal & Storage Manager
echo ========================================================
python desktop_main.py
if errorlevel 1 (
    echo.
    echo [Info] Python desktop_main.py exited. Falling back to web server mode...
    start http://127.0.0.1:8000
    python server.py 8000
)
pause
