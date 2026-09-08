@echo off
title RazorRevive B2B Conversational Autonomous Agent
cd /d "%~dp0"
if exist "%USERPROFILE%\.local\bin\uv.exe" (
    "%USERPROFILE%\.local\bin\uv.exe" run python run_agent_chat.py
) else (
    python run_agent_chat.py
)
pause
