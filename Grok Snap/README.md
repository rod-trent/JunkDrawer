# Grok Snap Chat - Windows Snapping AI Assistant

A PyQt6-based chat interface that snaps to any Windows application window and provides AI assistance via xAI's Grok API.

![Grok Snap Chat](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Window Snapping**: Attach the chat pane to any edge (left, right, top, or bottom) of any Windows application
- **Auto-Window Detection**: Dropdown automatically updates to show which window you're hovering over
- **Always On Top**: Stays visible while you work in your target application
- **Real-time Position Tracking**: Automatically follows when target window moves or resizes
- **Window Content Analysis**: Capture and analyze what's visible in the snapped window using Grok Vision
- **Grok AI Integration**: Full conversational AI powered by xAI's Grok-2-Vision-1212 model
- **Conversation History**: Save and load conversations to continue them later
- **In-App Settings**: Store API key and preferences directly in the app
- **Adjustable Opacity**: Control window transparency from 30% to 100%
- **Clear Chat**: Start fresh conversations with a single click
- **Multi-line Input**: Type longer messages with line breaks (Ctrl+Enter to send)
- **Modern Dark UI**: Sleek, professional interface that won't distract
- **Frameless Design**: Clean look without standard window decorations

## Requirements

- Windows 10/11
- Python 3.9 or higher
- xAI API Key (get one at https://x.ai)
- Dependencies: PyQt6, requests, Pillow

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Or use the provided setup script:
```bash
setup.bat
```

3. **Get your xAI API key** from [https://x.ai](https://x.ai)

4. **Run the application**:
```bash
python grok_snap_chat.py
```

5. **Configure your API key**:
   - Click the **⚙️ Settings** button in the app
   - Enter your xAI API key
   - Click **Save Settings**
   - Your key is saved and will load automatically on future launches

**Note**: You can also set the `XAI_API_KEY` environment variable if you prefer, but it's easier to use the in-app settings.

## Usage

1. **Launch the application**:
```bash
python grok_snap_chat.py
```

2. **Configure settings** (first time):
   - Click the **⚙️ Settings** button
   - Enter your xAI API key
   - Choose your preferred snap position (Right, Left, Top, or Bottom)
   - Adjust window opacity if desired
   - Click **Save Settings**

3. **Select and snap to a window**:
   - Drag the chat pane near any application window
   - The dropdown automatically detects and selects the window underneath
   - Click **📌 Snap to Window** to attach

4. **Start chatting**:
   - The chat pane attaches to your selected edge
   - Type your message (Ctrl+Enter to send)
   - The pane follows your target window automatically

5. **Analyze window content**:
   - Click **👁️ Analyze Window Content** to capture what's visible
   - Grok Vision analyzes the screenshot and provides insights
   - Ask follow-up questions about the content

6. **Manage conversations**:
   - Click **🗑️ Clear Chat** to start a fresh conversation
   - Use **⚙️ Settings** to save/load conversations
   - Click **📁 Open Conversations Folder** to access saved chats

7. **Unsnap** (optional):
   - Click **🔓 Unsnap** to stop following the window
   - Drag the chat pane anywhere you want
   - Window list automatically refreshes when you unsnap

## How It Works

### Window Snapping Technology
The application uses Windows API (`ctypes` with `user32.dll`) to:
- Enumerate all visible windows with `EnumWindows`
- Get real-time window positions with `GetWindowRect`
- Monitor window movements every 100ms
- Calculate and update chat pane position accordingly
- Detect windows underneath using `WindowFromPoint`

### Position Calculation
Snap positions are calculated based on your preference:
```python
# Right edge (default)
x = target_window.right
y = target_window.top
height = target_window.height

# Left edge
x = target_window.left - chat_width
y = target_window.top
height = target_window.height

# Top edge
x = target_window.left
y = target_window.top - 300
width = target_window.width

# Bottom edge
x = target_window.left
y = target_window.bottom
width = target_window.width
```

### Settings Storage
All settings are stored locally in your user directory:
- **Location**: `C:\Users\[YourUsername]\.grok_snap_chat\settings.json`
- **Stored settings**: API key, snap position, opacity
- **Conversation history**: `C:\Users\[YourUsername]\Documents\Grok Snap Chat Conversations\`

### Auto-Window Detection
A timer checks twice per second (500ms) to detect which window the chat pane is hovering over:
- Uses the chat window's position to check what's underneath
- Automatically updates the dropdown selection
- Only active when not snapped (to avoid interference)
- Refreshes window list if new windows are detected

### API Integration
- Uses xAI's `/v1/chat/completions` endpoint
- Grok-2-Vision-1212 model for both text conversations and vision analysis
- Maintains full conversation history for context
- Threaded API calls to keep UI responsive
- Error handling with user-friendly messages

### Window Content Analysis
When you click "Analyze Window Content":
1. Captures a screenshot of the snapped window using PIL's ImageGrab
2. Converts the image to base64 PNG format
3. Sends to Grok-4-Vision with the window title as context
4. Receives detailed analysis of visible content
5. You can ask follow-up questions about what Grok saw

## Customization

### Through Settings Dialog (⚙️ Button)
- **API Key**: Store your xAI API key securely
- **Snap Position**: Choose Right, Left, Top, or Bottom edge
- **Opacity**: Adjust from 30% to 100% transparency
- **Save/Load Conversations**: Manage chat history

### Code Modifications
If you want to modify the code directly:

**Change Default Snap Position** (edit `__init__` method):
```python
self.snap_position = "left"  # or "top", "bottom", "right"
```

**Adjust Width/Height**:
```python
self.setFixedWidth(400)  # Change width
self.setMinimumHeight(600)  # Change min height
```

**Update Detection Rate**:
```python
self.detect_timer.start(1000)  # Check every 1 second instead of 500ms
```

**Change Position Update Rate**:
```python
self.position_timer.start(100)  # Change from 100ms
```

**Theme Colors** (modify StyleSheet strings in `init_ui()`):
```python
"background-color: #1a1a2e"  # Title bar
"background-color: #0f3460"  # Chat area
"background-color: #e94560"  # Accent buttons
```

## Keyboard Shortcuts

- **Ctrl+Enter** - Send message
- **Alt+F4** - Close application

## Troubleshooting

**"No xAI API key found"**
- Click the ⚙️ Settings button in the app
- Enter your API key in the text field
- Click "Save Settings"
- Key is stored in: `C:\Users\[YourUsername]\.grok_snap_chat\settings.json`

**Auto-detection not working**
- Feature only works when NOT snapped to a window
- Make sure you're dragging the window over other applications
- Try clicking the 🔄 refresh button to update the window list

**Chat pane not following window**
- Window may have closed - check status bar
- Try clicking "📌 Snap to Window" again
- Some special windows (like Task Manager) may have restrictions

**API errors**
- Verify your API key is correct in Settings
- Check you have API credits remaining at x.ai
- Verify internet connection

**Window capture not working**
- Make sure the target window is visible and not minimized
- Try bringing the window to the foreground
- Some protected windows (UAC prompts) cannot be captured

**Settings not saving**
- Check that `C:\Users\[YourUsername]\.grok_snap_chat\` is writable
- Run the app as regular user (not administrator)

## Performance Notes

- Position checking runs every 100ms (low CPU impact)
- API calls are threaded (non-blocking)
- Window enumeration happens only on dropdown refresh
- Memory footprint: ~50-80MB typical

## Future Enhancements

- [x] Multi-position snapping (left/top/bottom) - **COMPLETED**
- [x] Opacity/transparency controls - **COMPLETED**
- [x] Saved conversations with export - **COMPLETED**
- [x] In-app API key management - **COMPLETED**
- [x] Auto-window detection - **COMPLETED**
- [ ] Multi-monitor support detection
- [ ] Custom keyboard shortcuts for common actions
- [ ] Window filters to exclude certain application types
- [ ] Multiple simultaneous chats for different windows
- [ ] Minimize to system tray for quick access
- [ ] Auto-snap based on active window focus
- [ ] Theme customization options

## Known Limitations

- Windows only (uses Windows API)
- Cannot snap to UAC prompts or elevated windows
- Some fullscreen applications may cover the chat pane
- Requires manual window selection (no auto-detection yet)

## License

MIT License - feel free to modify and distribute

## Credits

Created by Rod Trent
- GitHub: https://github.com/rod-trent/JunkDrawer
- Blog: https://rodtrent.substack.com

Powered by xAI's Grok API

## Contributing

Issues and pull requests welcome! This is part of my JunkDrawer repository of practical AI tools.

---

**Note**: This tool is designed for productivity and convenience. Always follow xAI's API usage terms and be mindful of API costs during extended chat sessions.