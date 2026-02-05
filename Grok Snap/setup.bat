@echo off
echo ========================================
echo Grok Snap Chat Setup
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.9 or higher.
    pause
    exit /b 1
)
echo.

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup complete!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Run the application:
echo    python grok_snap_chat.py
echo.
echo 2. Click the Settings button (gear icon) in the app
echo.
echo 3. Enter your xAI API key
echo    Get your key at: https://x.ai
echo.
echo 4. Click Save Settings
echo.
echo Your API key will be saved and loaded automatically!
echo.
pause