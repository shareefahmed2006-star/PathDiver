@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File"
if exist "dist\PathDiver.exe" (
    start "" "dist\PathDiver.exe"
) else if exist "PathDiver.exe" (
    start "" "PathDiver.exe"
) else (
    start "" Run_PathDiver.bat
)
exit
