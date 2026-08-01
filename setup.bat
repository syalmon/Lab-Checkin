@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo uv was not found. Install uv first.
    pause
    exit /b 1
)

echo Setting up the lab-checkin environment with uv...
uv sync --locked
set "exit_code=%errorlevel%"

if "%exit_code%"=="0" (
    echo Setup complete. You can now run auto_start.bat.
) else (
    echo Setup failed.
)

pause
exit /b %exit_code%
