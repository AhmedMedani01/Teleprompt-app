@echo off
REM Teleprompter Application Launcher
REM Uses uv to run in the project virtual environment

echo Starting Teleprompter Application...
uv run python teleprompter_pyside6.py

if errorlevel 1 (
    echo.
    echo ======================================================
    echo ERROR: Failed to start the teleprompter application
    echo.
    echo Please ensure PySide6 is installed:
    echo    uv add PySide6
    echo ======================================================
    pause
)
