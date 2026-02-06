# Garmin Chat - Desktop Application

A standalone desktop application for querying your Garmin Connect data using natural language and AI.

## 🎯 What is Garmin Chat?

Garmin Chat transforms your fitness data from passive numbers into actionable insights through natural conversation. Instead of navigating through multiple screens in Garmin Connect, simply ask questions like "How did I sleep last night?" or "What was my last workout?" and get instant, AI-powered responses.

![Garmin Chat Desktop](https://github.com/rod-trent/JunkDrawer/blob/main/Garmin%20Chat%20Desktop/GarminChatDesktop.jpg)

## ✨ Key Features

### **💬 Natural Language Interface**
- Ask questions in plain English about your fitness data
- Multi-line input field for complex queries
- Rich markdown formatting in responses (bold text, headers, bullet points, tables)
- Conversation history with timestamps
- Context-aware AI remembers previous conversations

### **🔐 Secure Credential Management**
- All credentials stored securely in the app (no .env files needed)
- xAI API key stored in `~/.garmin_chat/config.json`
- Garmin credentials encrypted and stored locally
- Easy-to-use Settings dialog for managing credentials
- Show/hide toggles for sensitive information

### **🚀 Smart Auto-Connect**
- Optional auto-login on startup (configurable in Settings)
- Persistent MFA token storage (authenticate once, works for ~30 days)
- Automatic token refresh when expired
- Graceful fallback to MFA when needed

### **🎨 Modern Fluent Design Interface**
- Windows 11-inspired Fluent Design aesthetic
- **🌙 Dark Mode** - Toggle between light and dark themes instantly
- Card-based layout with elevated components
- Color-coded messages (You, Garmin Chat, System)
- Larger, clearer icon buttons with tooltips
- Real-time status indicators
- Responsive layout with proper spacing

### **🧠 AI Intelligence & Context**
- **Chat Context Memory** - AI remembers conversations across sessions
- **💡 Smart Suggestions** - Proactive insights based on your activity patterns
- **🔄 Follow-up Questions** - Context-aware quick action buttons after responses
- "What did we discuss yesterday?" type questions supported
- Learns your preferences and interests over time

### **📊 Comprehensive Garmin Data Access**
- Recent activities (runs, cycling, strength training, etc.)
- Sleep data (duration, quality, REM/deep sleep)
- Daily summaries (steps, calories, heart rate)
- Heart rate statistics
- All data types supported by Garmin Connect

### **💾 Advanced Chat Management**
- **📝 Save Chat** - Save conversations for later review
- **📂 Chat History Viewer** - Browse, load, and delete past chats
- **🔍 Search** - Full-text search across all saved chats
- **💾 Saved Prompts** - Reuse your favorite questions

### **📄 Export & Reporting**
- Export conversations to **PDF**, **Word (.docx)**, or **Text (.txt)**
- Professional formatting with customizable options
- Include/exclude timestamps and system messages
- Perfect for sharing with coaches or doctors
- Export workout recommendations and plans

### **🔄 Session Management**
- MFA support with auto-detection
- Session resume with saved tokens
- Refresh data button to sync latest from Garmin
- Reset chat to start fresh conversations
- Automatic reconnection on token expiration

## 🆚 Advantages Over Web Version

| Feature | Web (Gradio) | Desktop (Tkinter) |
|---------|--------------|-------------------|
| Browser needed | ✅ Yes | ❌ No |
| Dependencies | More (Gradio) | Fewer (built-in) |
| Startup time | ~5 seconds | ~1 second |
| Memory usage | ~200MB | ~50MB |
| Credential storage | .env file | Secure in-app |
| Auto-login | ❌ No | ✅ Yes |
| Token persistence | ❌ No | ✅ Yes (30 days) |
| Dark mode | ❌ No | ✅ Yes |
| Chat history | ❌ No | ✅ Yes |
| Saved prompts | ❌ No | ✅ Yes |
| Export reports | ❌ No | ✅ Yes (PDF/Word/Text) |
| Search chats | ❌ No | ✅ Yes |
| Context memory | ❌ No | ✅ Yes |
| Smart suggestions | ❌ No | ✅ Yes |
| Follow-up questions | ❌ No | ✅ Yes |
| Port conflicts | Possible | Never |
| Distribution | Share code | Package as .exe |

## 📋 Requirements

- **Python 3.11, 3.12, or 3.13** (recommended: 3.12 or 3.13)
- **Tkinter** (usually included with Python)
- An **xAI API key** from [console.x.ai](https://console.x.ai/) (free tier available)
- A **Garmin Connect account** with MFA enabled (recommended for security)

**Optional (for full export features):**
- **reportlab** - PDF export support (auto-installed, fallback to text if missing)
- **python-docx** - Word document export (auto-installed, fallback to text if missing)

## 🚀 Quick Start (Windows)

### **First Time Setup:**

1. **Run Setup.bat**
   - Double-click `Setup.bat`
   - Installs all Python dependencies
   - Takes ~30 seconds

2. **Run Startup.bat**
   - Double-click `Startup.bat`
   - App opens and shows welcome dialog

3. **Configure Settings**
   - Settings dialog opens automatically
   - Enter your **xAI API key**
   - Enter your **Garmin email**
   - Enter your **Garmin password**
   - Choose if you want **auto-login** (recommended: enabled)
   - Click **Save**

4. **Connect & Authenticate**
   - Click "🔐 Connect to Garmin"
   - If MFA is enabled, enter your 6-digit code
   - Tokens are saved for future sessions

5. **Start Chatting!**
   - Type questions about your fitness data
   - Press **Ctrl+Enter** to send
   - Get instant AI-powered insights

### **Every Time After:**
Just double-click **Startup.bat** - that's it!

- If auto-login enabled: Connects automatically
- If tokens are valid: No MFA needed
- Ready to chat in seconds!

## 💻 Manual Installation

### **1. Install Dependencies**

```bash
pip install -r requirements-desktop.txt
```

**Included packages:**
- `garminconnect` - Garmin Connect API
- `garth` - Garmin authentication
- `openai` - xAI API client
- `requests` - HTTP library

**Note:** Tkinter is built into Python. If missing:
- **Windows/Mac**: Tkinter pre-installed
- **Linux (Ubuntu)**: `sudo apt-get install python3-tk`
- **Linux (Fedora)**: `sudo dnf install python3-tkinter`

### **2. Run the Application**

```bash
python GarminChatDesktop.py
```

**Windows users:**
```bash
py GarminChatDesktop.py
```

## ⚙️ Settings & Configuration

### **Access Settings:**
Click the **⚙️ Settings** button in the top-right corner

### **xAI Configuration:**
- **API Key**: Get from [console.x.ai](https://console.x.ai/)
- Masked by default with show/hide toggle
- Required for AI responses

### **Garmin Connect Credentials:**
- **Email**: Your Garmin Connect email
- **Password**: Your Garmin Connect password
- Password masked with show/hide toggle
- Required for authentication

### **Application Preferences:**
- **☑ Automatically connect to Garmin on startup**
  - Enabled: App auto-connects on launch
  - Disabled: Manual connect required
  - Default: Enabled

### **Storage Locations:**
- **App settings**: `~/.garmin_chat/config.json` (Windows: `C:\Users\YourName\.garmin_chat\`)
- **Chat history**: `~/.garmin_chat/chat_history/` (saved conversations)
- **Saved prompts**: `~/.garmin_chat/saved_prompts.json` (reusable questions)
- **Garmin tokens**: `~/.garmin_tokens/` (OAuth1 and OAuth2 tokens)

## 🎮 Using the App

### **Main Interface:**

**Header Buttons:**
- **🔍 Search** - Full-text search across all saved chats
- **🌙 Dark Mode** - Toggle between light and dark themes
- **⚙️ Settings** - Configure credentials and preferences

**Control Panel:**
- **🔐 Connect to Garmin** - Authenticate with Garmin Connect
- **🔄 Refresh** - Sync latest data from Garmin
- **🗑️ Reset** - Clear conversation history
- **💾 Prompts** - Manage saved prompts for quick reuse
- **📝 Save** - Save current conversation
- **📂 History** - View and load previous chats
- **📄 Export** - Export conversation as PDF/Word/Text

**Smart Features:**
- **💡 Smart Suggestions** - AI-generated suggestions based on your data patterns
- **🔄 Follow-up Questions** - Quick action buttons after responses (context-aware)

**Message Input:**
- Multi-line text field (3 rows)
- Press **Enter** for new line
- Press **Ctrl+Enter** to send message
- Word wrap enabled
- Auto-focus after connecting

**Example Questions:**
- "How many steps did I take today?"
- "What was my last workout?"
- "How did I sleep last night?"
- "Show me my recent activities"

### **Keyboard Shortcuts:**
- **Ctrl+Enter** - Send message
- **Enter** - New line in input field

### **Response Features:**
- **Bold text** - Important information highlighted
- **Headers** - Organized sections
- **Bullet points** - Easy-to-read lists
- **Tables** - Clean data presentation
- **Timestamps** - All messages time-stamped
- **Color coding** - User (blue), Assistant (green), System (gray)

### **Chat Management:**
- **Save conversations** for later review
- **Search across all chats** to find past discussions
- **Load previous chats** to continue conversations
- **Export to documents** for sharing or archiving

### **Dark Mode:**
- Click 🌙 in header to toggle
- Applies instantly to entire interface
- Optimized contrast for readability
- Button hover states adjusted for visibility

## 🔐 Authentication Flow

### **First Connection:**
1. Click "Connect to Garmin" (or auto-connects if enabled)
2. App attempts to use saved tokens
3. If no tokens or expired:
   - Prompts for MFA code (if MFA enabled)
   - Enter 6-digit code from authenticator app
   - Tokens saved for 30 days

### **Subsequent Connections:**
1. App loads saved tokens
2. Verifies tokens are valid
3. If expired: Automatically refreshes
4. If refresh fails: Prompts for MFA
5. **Usually no MFA needed!**

### **Session Management:**
- **Access tokens**: Valid for 1 hour, auto-refreshed
- **Refresh tokens**: Valid for ~30 days
- **MFA required**: Only when refresh token expires
- **Token storage**: Secure local JSON files

## 🎯 Example Use Cases

### **1. Morning Routine**
```
You: How did I sleep last night?
```
Get instant feedback on sleep quality, REM, deep sleep.

### **2. Workout Review**
```
You: Show me my activities from this week
```
See all workouts with duration, distance, calories.

### **3. Progress Tracking**
```
You: Compare my running pace this month vs last month
```
AI analyzes trends and provides insights.

### **4. Goal Monitoring**
```
You: Am I on track to hit my step goal today?
```
Quick check without opening Garmin Connect app.

### **5. Recovery Assessment**
```
You: What's my resting heart rate trend this week?
```
Monitor recovery and training load.

## 🔧 Troubleshooting

### **"Python is not installed"**
- Install Python 3.11+ from [python.org](https://www.python.org/)
- Check "Add Python to PATH" during installation

### **"No module named 'tkinter'"**
- **Windows/Mac**: Reinstall Python with Tkinter option
- **Linux**: `sudo apt-get install python3-tk`

### **"Configuration Required" on startup**
- Click ⚙️ Settings
- Enter all three credentials
- Click Save

### **MFA code errors**
- Ensure code is 6 digits
- Enter within 30 seconds of generation
- If "CSRF token" error: Wait a moment and try again

### **Rate limit errors (429)**
- Garmin has blocked your IP temporarily
- Wait 15-30 minutes before trying again
- Usually caused by repeated failed auth attempts

### **Tokens not persisting**
- Check `~/.garmin_tokens/` folder exists
- Ensure `oauth1_token` and `oauth2_token` files present
- Delete token files and re-authenticate if corrupted

### **Display name errors (403 with /None/)**
- App will retry loading display name
- Usually resolves after 2-3 retries
- If persists: Reset chat and reconnect

## 📦 Creating a Standalone Executable

Want to distribute without requiring Python installation?

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "GarminChat" GarminChatDesktop.py
```

**Result:**
- Single `.exe` file in `dist/` folder
- No Python installation needed
- Still requires credentials configuration

**Note:** Config files (`~/.garmin_chat/config.json`) created on first run.

## 🎨 Customization

### **Change Window Size:**
Edit `GarminChatDesktop.py` line ~223:
```python
self.root.geometry("1200x950")  # width x height (larger for better chat viewing)
```

### **Theme Preferences:**
- Click 🌙 button to toggle dark mode
- Changes apply instantly
- Preference saved for next session (coming soon)

### **Change Colors:**
Edit `setup_styles()` method in `colors` dictionary:
```python
self.colors = {
    'bg': '#F3F3F3',        # Background
    'card_bg': '#FFFFFF',   # Card background
    'accent': '#0078D4',    # Accent color
    'text': '#1F1F1F',      # Text color
    # ... more colors
}
```

### **Button Styles:**
Modify button padding, fonts, and sizes in `setup_styles()`:
```python
style.configure('Modern.TButton',
               padding=(12, 6),  # horizontal, vertical
               font=('Segoe UI', 11))
```

### **Add More Examples:**
Edit `create_widgets()` method, `examples` list:
```python
examples = [
    "Your custom question here",
    "Another example question",
]
```

## 📁 Project Structure

```
garmin-chat-bot/
├── GarminChatDesktop.py      # Main application
├── garmin_handler.py          # Garmin Connect integration
├── xai_client.py              # xAI API wrapper
├── requirements-desktop.txt   # Python dependencies
├── Setup.bat                  # Windows setup script
├── Startup.bat                # Windows launch script
├── README-Desktop.md          # This file
└── QUICKSTART-Windows.md      # Quick start guide
```

## 🔒 Security & Privacy

### **Data Storage:**
- **Credentials**: Stored locally in `~/.garmin_chat/config.json`
- **Tokens**: Stored locally in `~/.garmin_tokens/`
- **No cloud storage**: Everything stays on your machine
- **No telemetry**: App doesn't send usage data

### **API Usage:**
- **xAI API**: Only receives queries and Garmin data you explicitly send
- **Garmin Connect**: Standard OAuth authentication
- **No data sharing**: Your data isn't shared with third parties

### **Best Practices:**
- ✅ Enable MFA on your Garmin account
- ✅ Keep your xAI API key secure
- ✅ Don't share your config files
- ✅ Use a strong Garmin password
- ✅ Regularly update the app

## 🚀 Performance Tips

### **Faster Startup:**
- Enable auto-login in Settings
- Keep token files intact
- Use Python 3.12 or 3.13

### **Better Responses:**
- Be specific in your questions
- Ask one question at a time
- Use the example questions as templates

### **Troubleshooting Authentication:**
- Delete token files to force fresh auth
- Check Garmin Connect web login works
- Verify MFA code is current

## 📝 Known Limitations & Notes

- **No offline mode**: Requires internet for Garmin and xAI
- **Token expiration**: Need MFA every ~30 days
- **Rate limits**: Garmin may throttle frequent requests
- **Data latency**: Garmin data updates every 15-30 minutes
- **MFA required**: Cannot disable MFA requirement from Garmin
- **Export libraries**: PDF/Word export requires additional packages (auto-fallback to text)
- **Context memory**: Limited to last 10 messages across sessions
- **Search scope**: Searches saved chats only (not current session until saved)

## 🆕 Version History

### **v3.0 - Major AI & UX Update (Current)**
- 🎨 **Fluent Design UI** - Windows 11-inspired modern interface
- 🌙 **Dark Mode** - Full dark theme with instant toggle
- 🧠 **Chat Context Memory** - AI remembers across sessions
- 💡 **Smart Suggestions** - Proactive AI insights
- 🔄 **Follow-up Questions** - Context-aware quick actions
- 📂 **Chat History Viewer** - Browse and load past conversations
- 🔍 **Full-Text Search** - Search across all saved chats
- 💾 **Saved Prompts** - Reuse favorite questions
- 📄 **Export Reports** - PDF, Word, and Text format exports
- 🎯 **Larger Icons** - Better visibility with tooltips
- 🖱️ **Improved Hover States** - Better contrast in dark mode
- 📊 **Table Rendering** - Clean markdown table display
- 🗂️ **Better Layout** - Fixed grid system, no overlaps

### **v2.0 - Desktop Enhancement**
- ✨ In-app credential management (no .env files)
- 🔐 Persistent MFA token storage
- 🚀 Auto-login on startup (configurable)
- 🎨 Enhanced markdown rendering
- 💬 Multi-line input field
- 🔄 Automatic token refresh
- 🪟 Improved UI spacing and layout
- 📊 Better error handling and logging
- ⚙️ Application preferences in Settings

### **v1.0 - Initial Release**
- Basic desktop application
- Single-line input
- Manual authentication each session
- .env file for credentials

## 🤝 Support

### **Getting Help:**
1. Check this README thoroughly
2. Review QUICKSTART-Windows.md
3. Check console logs for errors
4. Verify all requirements are met

### **Common Issues:**
- Most issues are authentication-related
- Check Settings are configured correctly
- Verify Garmin Connect login works in browser
- Wait if you hit rate limits

## 📜 License

Personal use project. Use at your own discretion.

## 🙏 Acknowledgments

- **Garmin Connect** - Fitness data platform
- **xAI (Grok)** - AI API provider
- **garminconnect/garth** - Python libraries for Garmin integration
- **Tkinter** - Python GUI framework

---

**Ready to transform your fitness data into insights?** 

Download all files, run `Setup.bat`, then `Startup.bat`, and start chatting! 🏃‍♂️💪
