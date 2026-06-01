@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
    pause
    goto end
)

echo [ERROR] Environment not found. Please run setup.bat first.
pause

:end
