@echo off
echo ============================================================
echo Garmin Chat Desktop - Starting...
echo ============================================================
echo.

REM Check if Python is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run Setup.bat first
    echo.
    pause
    exit /b 1
)

REM Check if the main script exists
if not exist GarminChatDesktop.py (
    echo ERROR: GarminChatDesktop.py not found!
    echo Please make sure you're running this from the correct directory.
    echo.
    pause
    exit /b 1
)

echo Starting Garmin Chat Desktop...
echo.
echo ============================================================
echo.

REM Run the desktop application
py GarminChatDesktop.py

REM If the app exits with an error, pause so user can see the error
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo Application closed with an error
    echo ============================================================
    echo.
    echo Common issues:
    echo   1. Missing dependencies - Run Setup.bat
    echo   2. Invalid credentials in app settings
    echo   3. Garmin Connect connection issues
    echo   4. Configure credentials via Settings (gear icon) in the app
    echo.
    pause
)