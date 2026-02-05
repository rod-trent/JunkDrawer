# Grok Snap Chat - Windows Snapping AI Assistant

A PyQt6-based chat interface that snaps to any Windows application window and provides AI assistance via xAI's Grok API.

![Grok Snap Chat](https://img.shields.io/badge/Python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Window Snapping**: Attach the chat pane to the right edge of any Windows application
- **Always On Top**: Stays visible while you work in your target application
- **Real-time Position Tracking**: Automatically follows when target window moves or resizes
- **Window Content Analysis**: Capture and analyze what's visible in the snapped window using Grok Vision
- **Grok AI Integration**: Full conversational AI powered by xAI's Grok-4 and Grok-4-Vision models
- **Conversation History**: Maintains context throughout your chat session
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

3. **Set your xAI API key**:

**Option A - Environment Variable (Recommended)**:
```bash
# PowerShell
$env:XAI_API_KEY="your-api-key-here"

# Command Prompt
set XAI_API_KEY=your-api-key-here
```

**Option B - System Environment Variable**:
- Right-click "This PC" → Properties
- Advanced system settings → Environment Variables
- Add new variable: `XAI_API_KEY` = `your-api-key-here`

## Usage

1. **Launch the application**:
```bash
python grok_snap_chat.py
```

2. **Select a target window**:
   - Use the dropdown to choose which application window to snap to
   - Click "📌 Snap to Window"

3. **Start chatting**:
   - The chat pane will attach to the right edge of your selected window
   - Type your message and press Ctrl+Enter or click Send
   - The pane follows your target window automatically

4. **Analyze window content**:
   - Click "👁️ Analyze Window Content" to capture what's visible in the snapped window
   - Grok Vision will analyze the screenshot and provide a summary
   - Ask follow-up questions about the content

5. **Clear chat**:
   - Click "🗑️ Clear Chat" to start a fresh conversation
   - Clears all history and message display

6. **Unsnap** (optional):
   - Click "🔓 Unsnap" to stop following the window
   - Drag the chat pane anywhere you want
   - Window list automatically refreshes when you unsnap

## How It Works

### Window Snapping Technology
The application uses Windows API (`ctypes` with `user32.dll`) to:
- Enumerate all visible windows with `EnumWindows`
- Get real-time window positions with `GetWindowRect`
- Monitor window movements every 100ms
- Calculate and update chat pane position accordingly

### Position Calculation
```python
# Snaps to right edge of target window
x = target_window.right
y = target_window.top
height = target_window.height
```

### API Integration
- Uses xAI's `/v1/chat/completions` endpoint
- Grok-4 model for text conversations
- Grok-4-Vision model for window content analysis
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

### Change Snap Position
Edit the `update_position` method in `grok_snap_chat.py`:

```python
# Left side
x = rect.left - self.width()

# Bottom
y = rect.bottom
height = 400  # Fixed height

# Top overlay
y = rect.top + 50  # Offset from top
```

### Adjust Width/Height
```python
self.setFixedWidth(400)  # Change width
self.setMinimumHeight(600)  # Change min height
```

### Update Rate
```python
self.position_timer.start(100)  # Change from 100ms
```

### Theme Colors
Modify the StyleSheet strings in `init_ui()`:
```python
"background-color: #1a1a2e"  # Title bar
"background-color: #0f3460"  # Chat area
"background-color: #e94560"  # Accent buttons
```

## Keyboard Shortcuts

- **Ctrl+Enter** - Send message
- **Alt+F4** - Close application

## Troubleshooting

**"XAI_API_KEY not found"**
- Make sure you've set the environment variable
- Restart your terminal/IDE after setting system variables
- Check spelling: `XAI_API_KEY` (case-sensitive)

**Chat pane not following window**
- Window may have closed - check status bar
- Try clicking "📌 Snap to Window" again
- Some special windows (like Task Manager) may have restrictions

**API errors**
- Check your API key is valid
- Verify you have API credits remaining
- Check internet connection

## Performance Notes

- Position checking runs every 100ms (low CPU impact)
- API calls are threaded (non-blocking)
- Window enumeration happens only on dropdown refresh
- Memory footprint: ~50-80MB typical

## Future Enhancements

- [ ] Multi-monitor support detection
- [ ] Snap to left/top/bottom edges
- [ ] Minimize to system tray
- [ ] Save conversation history
- [ ] Custom keyboard shortcuts
- [ ] Transparency/opacity controls
- [ ] Multiple chat sessions
- [ ] Window filters (ignore certain apps)

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
