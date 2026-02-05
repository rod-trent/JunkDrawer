# Quick Start Guide (Windows)

The easiest way to get Garmin Chat Desktop running on Windows.

## First Time Setup

1. **Run Setup.bat**
   - Double-click `Setup.bat`
   - It will install all dependencies
   - That's it for setup!

2. **Run Startup.bat**
   - Double-click `Startup.bat`
   - The Garmin Chat Desktop app will open
   - A welcome dialog will appear

3. **Configure your credentials**
   - Click OK on the welcome dialog
   - The Settings dialog will open automatically
   - Enter your credentials:
     - **xAI API Key** (get from https://console.x.ai/)
     - **Garmin Connect Email**
     - **Garmin Connect Password**
   - Click "Save"
   - Your credentials are stored securely in `~/.garmin_chat/config.json`

4. **Start chatting!**
   - Click "Connect to Garmin" to authenticate
   - If you have MFA, enter your 6-digit code
   - Start asking questions about your fitness data!

## Every Time After Setup

Just double-click **Startup.bat** to launch the app.

Your credentials are remembered - no need to enter them again!

## Troubleshooting

### "Python is not installed or not in PATH"
- You need Python 3.12 or 3.13 installed
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### "Failed to install dependencies"
- Make sure you have an internet connection
- Try running Setup.bat again
- If it still fails, open Command Prompt and run:
  ```
  py -m pip install -r requirements-desktop.txt
  ```

### App closes immediately with error
- Make sure you configured your credentials in Settings (⚙️ button)
- Verify your Garmin Connect login works in a web browser
- Check that your xAI API key is valid
- Check the console output for specific error messages

### "Configuration Required" error
- Click the ⚙️ Settings button in the app
- Enter all three credentials:
  - xAI API key
  - Garmin email  
  - Garmin password
- Click "Save"

### "No module named 'tkinter'"
- Tkinter should come with Python
- If missing, reinstall Python and ensure Tkinter is selected during installation

## What Do The Batch Files Do?

**Setup.bat:**
- Checks if Python is installed
- Upgrades pip to latest version
- Installs all required Python packages
- That's it! No .env file needed

**Startup.bat:**
- Checks if Python is installed
- Runs GarminChatDesktop.py
- Shows helpful error messages if something goes wrong
- Pauses on error so you can read the message

## Creating a Desktop Shortcut

Want to launch directly from your desktop?

1. Right-click `Startup.bat`
2. Click "Create shortcut"
3. Drag the shortcut to your Desktop
4. (Optional) Right-click the shortcut → Properties → Change Icon

Now you can launch Garmin Chat Desktop right from your desktop!

## Files You Need

Make sure these files are in the same folder:
- ✅ `Setup.bat` - Run once for setup
- ✅ `Startup.bat` - Run every time to launch app
- ✅ `GarminChatDesktop.py` - Main application
- ✅ `garmin_handler.py` - Garmin integration
- ✅ `xai_client.py` - AI integration
- ✅ `requirements-desktop.txt` - Dependencies list

Note: Your credentials are stored securely in `~/.garmin_chat/config.json` (created automatically)

---

**That's it! You're ready to chat with your fitness data.** 🏃‍♂️
