# TaskFolder v1.0.0

**A lightweight Windows 11 application launcher for your system tray**

Quick access to your favorite apps, PWAs, and shortcuts - no taskbar clutter required.

---

## 🚀 Installation

1. **Extract** this ZIP file to any location
2. **Run** `TaskFolder.exe`
3. Look for the icon in your **system tray** (bottom-right corner, near the clock)
4. **Right-click** the icon → "Add Application..." to get started!

That's it! No installation wizard, no admin rights required.

---

## ⚙️ Requirements

### Framework-Dependent Version (This Version)
- **Windows 10 or Windows 11**
- **.NET 8.0 Runtime** (download below if needed)

**Don't have .NET 8.0?**
Download it here: https://dotnet.microsoft.com/download/dotnet/8.0
(Choose "Download .NET Runtime" - it's quick and free)

### Alternative: Standalone Version
If you don't want to install .NET, download the **Standalone version** instead:
- No prerequisites required
- Larger download (~60 MB vs 200 KB)
- Available on the GitHub releases page

---

## 📖 Quick Start

### Adding Applications

**Method 1: Use the GUI**
1. Right-click the TaskFolder tray icon
2. Click "Add Application..."
3. Browse to any `.exe` or `.lnk` (shortcut) file
4. Click Open

**Method 2: Drag & Drop**
1. Right-click tray icon → "Open Shortcuts Folder"
2. Drag shortcut files into that folder
3. TaskFolder automatically detects them!

### Launching Applications

1. **Left-click** the TaskFolder tray icon
2. Your menu appears with all your apps
3. **Click** any app to launch it

### Settings

Right-click tray icon → "Settings" to:
- Enable "Start with Windows" (auto-start)
- Open the shortcuts folder
- Clear all shortcuts

---

## 💡 Perfect For

- **Edge & Chrome PWAs** (Progressive Web Apps like Gmail, Twitter, YouTube)
- **Frequently-used applications** (VS Code, Notepad++, Office apps)
- **Development tools** (Database clients, terminals, IDEs)
- **Remote desktop shortcuts**
- **PowerShell scripts** (anything with a shortcut!)

---

## 🎨 Special Features

### Progressive Web Apps (PWAs)
TaskFolder handles PWAs perfectly:
- Shows the **correct app icon** (not generic Edge icon)
- Launches as a **dedicated app window** (not browser tab)
- Preserves all launch parameters

Add your Gmail PWA, and it shows up with Gmail's icon and opens as a proper app!

### Smart Icon Detection
Automatically extracts icons from:
- Executables (.exe files)
- Shortcuts (.lnk files)
- Custom icon locations (PWAs)
- Network paths

### Auto-Refresh
The shortcuts folder is monitored in real-time. Add or remove shortcuts, and TaskFolder updates instantly.

---

## 📁 File Locations

**Shortcuts Folder:**
```
%APPDATA%\TaskFolder\Shortcuts\
```

To access quickly:
- Press `Win+R`
- Type: `%APPDATA%\TaskFolder\Shortcuts`
- Press Enter

All your shortcuts are stored here as standard Windows `.lnk` files.

---

## 🔧 Troubleshooting

### "Application won't start"
- **Check**: Do you have .NET 8.0 Runtime installed?
- **Fix**: Download from https://dotnet.microsoft.com/download/dotnet/8.0

### "Can't find the system tray icon"
- Click the **^** (up arrow) in your system tray
- TaskFolder icon might be in the hidden icons area
- Right-click taskbar → "Taskbar settings" → "Select which icons appear on the taskbar"

### "Application opens but shows no icon"
- This is normal - Windows may hide new tray icons
- Click the ^ arrow to see all icons
- TaskFolder is running and working!

### "Error adding an application"
- Make sure the file exists and is accessible
- Check you have permission to read the file
- Try copying the shortcut to the shortcuts folder instead

### "PWA shows wrong icon"
- Remove the shortcut (right-click → Remove)
- Add it again
- TaskFolder will reload with the correct icon

---

## 🗑️ Uninstallation

TaskFolder doesn't install anything system-wide. To remove:

1. **Exit TaskFolder** (right-click icon → "Exit")
2. **Delete** the executable
3. **Optional**: Delete the shortcuts folder at `%APPDATA%\TaskFolder\`
4. **Optional**: Remove auto-start (if enabled):
   - Press `Win+R`
   - Type: `shell:startup`
   - Delete TaskFolder shortcut if present

That's it! No registry cleaning, no leftover files.

---

## 🆓 License

TaskFolder is **completely free** and open source (MIT License).

- Use it however you want
- Modify it if you like
- Share it with friends
- No ads, no tracking, no subscriptions

---

## 📞 Support

- **Bug reports**: https://github.com/rod-trent/JunkDrawer/issues
- **Feature requests**: https://github.com/rod-trent/JunkDrawer/issues
- **Source code**: https://github.com/rod-trent/JunkDrawer/tree/main/TaskFolder
- **Documentation**: Full guides available on GitHub

---

## ✨ What's Next?

After you've added a few applications:

1. **Try auto-start**: Settings → "Start TaskFolder when Windows starts"
2. **Organize**: Rename shortcuts to change their display names
3. **Share**: Tell friends who are frustrated with Windows 11's limitations!

---

## 🎯 Why TaskFolder?

Windows 11 removed the quick-access toolbar features from Windows 7. Commercial alternatives are bloated or expensive. TaskFolder brings it back:

- ✅ Under 200 KB
- ✅ Uses <5 MB RAM
- ✅ Zero CPU when idle
- ✅ No ads, no telemetry
- ✅ Completely free

---

**Made with ❤️ for Windows users who miss the old taskbar**

**Version:** 1.0.0  
**Released:** January 2025  
**Author:** Rod Trent ([@rod-trent](https://github.com/rod-trent))

---

*Enjoy TaskFolder? Star it on GitHub and share with others!* ⭐
