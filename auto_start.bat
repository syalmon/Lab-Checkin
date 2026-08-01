@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo uv was not found. Install uv first, then run setup.bat.
    pause
    exit /b 1
)

uv run --locked --no-sync report_entry.py
set "exit_code=%errorlevel%"

if not "%exit_code%"=="0" (
    echo.
    echo Attendance registration failed. If this is the first run, execute setup.bat once.
)

pause
exit /b %exit_code%
