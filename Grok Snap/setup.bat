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
echo 1. Set your XAI_API_KEY environment variable
echo    PowerShell: $env:XAI_API_KEY="your-key"
echo    CMD: set XAI_API_KEY=your-key
echo.
echo 2. Run the application:
echo    python grok_snap_chat.py
echo.
pause
