# Garmin Chat - Desktop Application

A standalone desktop application for querying your Garmin Connect data using natural language and AI.

## What's Different from the Web Version?

- **Native desktop app** - Runs as a local application, no web browser needed
- **Tkinter-based** - Uses Python's built-in GUI framework (no Gradio dependency)
- **Lighter weight** - Fewer dependencies, faster startup
- **Same functionality** - All features from the web version work identically

## Requirements

- **Python 3.12 or 3.13**
- **Tkinter** (usually included with Python)
- An **xAI API key** from [console.x.ai](https://console.x.ai/)
- A **Garmin Connect account**

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements-desktop.txt
```

Note: Tkinter is usually included with Python. If you get an error about Tkinter, install it:
- **Windows/Mac**: Tkinter comes pre-installed
- **Linux (Ubuntu/Debian)**: `sudo apt-get install python3-tk`
- **Linux (Fedora)**: `sudo dnf install python3-tkinter`

2. **Configure credentials:**

Copy `.env.example` to `.env` and add your credentials:
```
XAI_API_KEY=your_xai_api_key_here
GARMIN_EMAIL=your_garmin_email@example.com
GARMIN_PASSWORD=your_garmin_password_here
```

## Usage

Run the desktop application:

```bash
python GarminChatDesktop.py
```

**Windows users:**
```bash
py GarminChatDesktop.py
```

The application window will open with:
- Connect button to authenticate with Garmin
- Chat interface for asking questions
- Example questions to get started
- Buttons to refresh data and reset conversations

## Features

### Authentication
- Click "🔐 Connect to Garmin" to authenticate
- If MFA is enabled, enter your 6-digit code
- Session persists while app is running

### Chat Interface
- Type questions in the input box and press Enter or click Send
- View conversation history with timestamps
- Color-coded messages (You, Garmin Chat, System)

### Controls
- **🔄 Refresh Data** - Update with latest Garmin sync
- **🗑️ Reset Chat** - Clear conversation and start fresh
- **Example Questions** - Quick-click common queries

### Example Questions
- "How many steps did I take today?"
- "What was my last workout?"
- "How did I sleep last night?"
- "Show me my recent activities"

## Keyboard Shortcuts

- **Enter** in message box - Send message
- **Enter** in MFA field - Submit MFA code

## Advantages of Desktop Version

✅ **No browser overhead** - Lighter on system resources  
✅ **Faster startup** - No web server to initialize  
✅ **Native feel** - Proper desktop application  
✅ **Fewer dependencies** - No Gradio requirement  
✅ **Portable** - Can be packaged as standalone executable  

## Troubleshooting

### "No module named 'tkinter'"
Tkinter needs to be installed:
- Windows/Mac: Reinstall Python with Tkinter option checked
- Linux: `sudo apt-get install python3-tk`

### Window doesn't appear
Check console for errors. Ensure all dependencies are installed.

### Authentication fails
- Verify credentials in `.env` file
- Check Garmin Connect login works in browser
- Ensure MFA code is entered correctly (6 digits)

### App freezes
Authentication and API calls run in background threads. Brief pauses during data fetching are normal.

## Creating a Standalone Executable

Want to distribute the app without requiring Python installation? Use **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "GarminChat" GarminChatDesktop.py
```

This creates a single executable in the `dist/` folder that can run on any machine without Python installed.

**Note:** You'll still need to provide the `.env` file with credentials alongside the executable.

## Customization

### Change Window Size
Edit `GarminChatDesktop.py`:
```python
self.root.geometry("900x700")  # width x height
```

### Change Theme Colors
Modify the `setup_styles()` method to customize colors, fonts, and styling.

### Add More Example Questions
Edit the `examples` list in `create_widgets()` method.

## Comparison: Web vs Desktop

| Feature | Web (Gradio) | Desktop (Tkinter) |
|---------|--------------|-------------------|
| Browser needed | Yes | No |
| Dependencies | More (Gradio) | Fewer (built-in) |
| Startup time | ~5 seconds | ~1 second |
| Memory usage | ~200MB | ~50MB |
| Look & feel | Modern web UI | Native desktop |
| Port conflicts | Possible | No |
| Distribution | Share code | Can package as .exe |

## Files

- `GarminChatDesktop.py` - Main desktop application
- `garmin_handler.py` - Garmin Connect integration (shared with web version)
- `xai_client.py` - xAI API client (shared with web version)
- `requirements-desktop.txt` - Python dependencies (no Gradio)
- `.env` - Your credentials (create from `.env.example`)

## Support

Issues? Check:
1. Python version (3.12 or 3.13 recommended)
2. All dependencies installed
3. `.env` file configured correctly
4. Tkinter installed (usually automatic)

## License

Personal use project. Use at your own discretion.

---

**Enjoy chatting with your fitness data!** 🏃‍♂️💪
