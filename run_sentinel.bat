@echo off
title RazorRevive Autonomous Sentinel Daemon
cd /d "%~dp0"
if exist "%USERPROFILE%\.local\bin\uv.exe" (
    "%USERPROFILE%\.local\bin\uv.exe" run python run_sentinel.py
) else (
    python run_sentinel.py
)
pause
