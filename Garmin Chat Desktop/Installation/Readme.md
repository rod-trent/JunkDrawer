# Garmin Chat Desktop

> AI-powered fitness assistant for your Garmin Connect data

Chat with your Garmin data using natural language. Ask questions about your workouts, sleep, activities, and trends - all powered by AI.

---

## 🎯 What Is This?

**Garmin Chat Desktop** is a standalone Windows application that lets you have natural conversations with your Garmin fitness data. Instead of navigating through charts and menus, just ask questions like:

- *"How did I sleep last night?"*
- *"What were my activities this week?"*
- *"Show me my heart rate trends"*
- *"How many steps do I average per day?"*

The app uses AI (powered by xAI's Grok) to understand your questions and provide insights from your Garmin Connect data.

---

## ✨ Key Features

- 💬 **Natural Language Chat** - Ask questions in plain English
- 🏃 **Real-time Garmin Data** - Access your latest workouts, sleep, and activities
- 💾 **Save Conversations** - Keep chat history for future reference
- 📄 **Export Reports** - Generate PDF, Word, or text reports
- 🔍 **Search History** - Find past conversations instantly
- 🌙 **Dark Mode** - Easy on the eyes during evening workouts
- 🎨 **Modern UI** - Windows 11 Fluent Design interface
- 🔐 **Secure** - Your credentials stored locally, never in the cloud

---

## 📋 Requirements

### **To Run the Application:**

- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 150 MB for installation
- **Internet Connection**: Required for AI queries and Garmin data sync

### **To Use the Application:**

1. **xAI API Key** (Required)
   - Sign up at: https://console.x.ai/
   - Free tier available
   - Used for AI-powered responses

2. **Garmin Connect Account** (Required)
   - Free account at: https://connect.garmin.com/
   - Requires a Garmin device (watch, tracker, etc.)
   - Account must have some activity data

3. **Multi-Factor Authentication** (If Enabled)
   - If you have MFA enabled on your Garmin account
   - You'll need your authenticator app ready during first login

---

## 🚀 Quick Start

### **Option 1: Install Pre-Built Application (Easiest)**

1. **Download** the installer:
   - Go to [Releases](https://github.com/rod-trent/JunkDrawer/Installation)
   - Download `GarminChatDesktop_Setup_v3.0.exe`

2. **Run the installer**:
   - Double-click the downloaded file
   - Follow the installation wizard
   - Choose installation location (default: `C:\Program Files\GarminChat`)
   - Create desktop shortcut (optional)

3. **Launch the app**:
   - Find it in Start Menu → "Garmin Chat Desktop"
   - Or use the desktop shortcut

4. **First-time setup**:
   - Enter your xAI API key
   - Enter your Garmin Connect credentials
   - Click "Connect"
   - Start chatting!

### **Option 2: Run from Source (For Developers)**

```bash
# Clone the repository
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/garmin chat desktop

# Install dependencies
pip install -r requirements.txt

# Run the application
python GarminChatDesktop.py
```

---

## 🔑 Getting Your xAI API Key

1. Visit https://console.x.ai/
2. Sign up or log in
3. Click "Create API Key"
4. Copy the key (starts with `xai-...`)
5. Paste it into Garmin Chat settings

**Cost**: Free tier includes 25,000 tokens/month (roughly 500-1000 chat messages)

---

## 🎮 How to Use

### **Basic Queries:**
```
You: "What was my sleep last night?"
AI: You slept 7 hours and 32 minutes with 1h 45m deep sleep...

You: "Show me this week's activities"
AI: This week you completed 3 runs, 2 bike rides...

You: "How's my resting heart rate trend?"
AI: Your resting heart rate has been averaging 58 bpm...
```

### **Control Panel Buttons:**
- **🔗 Connect** - Connect to Garmin (one-time setup)
- **Refresh** - Fetch latest data from Garmin
- **🗑️ Reset** - Clear current conversation
- **💾 Prompts** - Save/load frequently used questions
- **📝 Save** - Save current conversation
- **📂 History** - View past conversations
- **📄 Export** - Create PDF/Word/Text reports
- **🌙 Dark Mode** - Toggle theme
- **Settings** - Manage API keys and credentials

### **Tips:**
- Ask follow-up questions naturally
- Reference time periods: "last week", "this month", "yesterday"
- Ask for comparisons: "How does this week compare to last week?"
- Request specific metrics: "Show me my VO2 max trend"

---

## 📦 What's Included

```
GarminChat/
├── GarminChat.exe          # Main application
├── LICENSE.txt             # MIT License
├── README-Desktop.md       # User documentation
└── Uninstall.exe          # Clean uninstaller
```

**Installation creates:**
- Start Menu shortcuts
- Desktop icon (optional)
- User data folder: `C:\Users\YourName\.garmin_chat\`

**User data includes:**
- `config.json` - Your credentials (encrypted)
- `chat_history/` - Saved conversations
- `saved_prompts.json` - Your favorite questions
- `oauth_tokens.json` - Garmin authentication

---

## 🔒 Privacy & Security

- ✅ **Credentials stored locally** - Never sent to cloud
- ✅ **Garmin OAuth** - Secure authentication
- ✅ **No telemetry** - We don't track your usage
- ✅ **Open source** - Audit the code yourself

**What data leaves your computer:**
- Queries sent to xAI API for responses
- Garmin data fetched from Garmin Connect
- That's it!

**What stays local:**
- Your API keys
- Garmin credentials
- Chat history
- All settings

---

## 🐛 Troubleshooting

### **"Cannot connect to Garmin"**
- Check your credentials
- Verify internet connection
- If MFA enabled, enter the code when prompted
- Try "Refresh" button

### **"xAI API Error"**
- Verify your API key in Settings
- Check you have API credits remaining
- Ensure internet connection is active

### **"Window icon showing incorrectly"**
- Rebuild the exe with updated spec file
- Make sure `logo.ico` is in project folder

### **App won't start**
- Run as Administrator
- Check antivirus isn't blocking it
- Reinstall the application

### **Slow responses**
- Normal - AI takes 2-5 seconds to respond
- Check internet connection speed
- Try shorter queries

---

## 📚 Documentation

- **[API Limits Guide](https://github.com/rod-trent/JunkDrawer/blob/main/Garmin%20Chat%20Desktop/GarminAPILimits.md)** - Understanding Garmin API
- **[Blog Post](https://rodtrent.substack.com/p/transform-your-fitness-data-into)** - Deep dive into features

---

## 🚧 Roadmap

### **v3.1 (Coming Soon)**
- [ ] Voice input support
- [ ] More chart visualizations
- [ ] Goal tracking and reminders
- [ ] Training plan suggestions

### **v4.0 (Future)**
- [ ] Mobile companion app
- [ ] Apple Watch integration
- [ ] Social sharing
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions welcome! This is an open source project.

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Areas where help is needed:**
- UI/UX improvements
- Additional data visualizations
- Bug fixes
- Documentation
- Testing on different systems

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

**TL;DR:** You can use, modify, and distribute this freely. No warranty provided.

---

## 🙏 Acknowledgments

- **xAI** - For the Grok API powering the AI responses
- **Garmin** - For the Connect API and fitness data
- **Python Community** - For amazing libraries (tkinter, requests, etc.)
- **You** - For using this app!

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/rod-trent/JunkDrawer/issues)
- **Blog**: [Rod's Blog](https://rodtrent.substack.com/)
- **Twitter**: [@rodtrent](https://x.com/rodtrent)

---

## ⭐ Star This Repo!

If you find this useful, please star the repository! It helps others discover the project.

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/rod-trent/JunkDrawer?style=social)
![GitHub forks](https://img.shields.io/github/forks/rod-trent/JunkDrawer?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/rod-trent/JunkDrawer?style=social)

---

**Made with ❤️ by Rod Trent**

*Helping you understand your fitness data, one chat at a time.*
