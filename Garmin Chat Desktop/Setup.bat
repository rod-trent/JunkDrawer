@echo off
echo ============================================================
echo Garmin Chat Desktop - Setup
echo ============================================================
echo.
echo This will install all required dependencies...
echo.

REM Check if Python is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12 or 3.13 from python.org
    echo.
    pause
    exit /b 1
)

echo Python found:
py --version
echo.

echo Installing dependencies...
echo.
py -m pip install --upgrade pip
py -m pip install -r requirements-desktop.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Run Startup.bat to launch Garmin Chat Desktop
echo 2. Configure your credentials in the Settings dialog
echo.
echo You'll need:
echo   - xAI API key (from https://console.x.ai/)
echo   - Garmin Connect email
echo   - Garmin Connect password
echo.
echo All credentials are stored securely in the app.
echo No .env file needed!
echo.
pause
