@echo off
REM Teleprompter Application Launcher
REM Uses uv to run in the project virtual environment

echo Starting Teleprompter Application...
echo.
echo Syncing dependencies...
uv sync --quiet

if errorlevel 1 (
    echo.
    echo ======================================================
    echo ERROR: Failed to sync dependencies
    echo.
    echo Please check your pyproject.toml and uv.lock files
    echo ======================================================
    pause
    exit /b 1
)

echo Running teleprompter...
uv run teleprompter_pyside6.py

if errorlevel 1 (
    echo.
    echo ======================================================
    echo ERROR: Failed to start the teleprompter application
    echo.
    echo Please ensure all dependencies are correctly installed
    echo You can try: uv sync --reinstall
    echo ======================================================
    pause
    exit /b 1
)
