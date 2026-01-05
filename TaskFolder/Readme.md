# TaskFolder

**A lightweight, modern application launcher for Windows 11**

TaskFolder brings back quick-access application launching to Windows 11's taskbar area through a clean system tray menu. Launch your favorite apps, PWAs, and scripts with a single click—no taskbar clutter required.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![.NET 8.0](https://img.shields.io/badge/.NET-8.0-purple.svg)
![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2011%2F10-blue.svg)

## ✨ Features

- **🎯 System Tray Integration** - Quick access without cluttering your taskbar
- **🌐 Perfect PWA Support** - Edge/Chrome Progressive Web Apps work flawlessly with correct icons
- **⚡ Lightning Fast** - Under 200 KB, <5 MB RAM, zero CPU when idle
- **🔄 Auto-Refresh** - Monitors shortcuts folder for automatic updates
- **🎨 Smart Icons** - Extracts proper icons from PWAs, executables, and custom locations
- **🚀 Auto-Start** - Optional startup with Windows
- **📁 Simple Management** - Drag-and-drop shortcuts or use the built-in browser
- **🆓 Completely Free** - Open source under MIT License

## 🚀 Quick Start

### Prerequisites

- Windows 11 or Windows 10
- .NET 8.0 Runtime ([Download](https://dotnet.microsoft.com/download/dotnet/8.0))

### Installation

1. Download the latest release from [Releases](../../releases) *(or build from source)*
2. Extract and run `TaskFolder.exe`
3. Look for the icon in your system tray
4. Right-click → "Add Application..." to get started!

### Building from Source

```bash
git clone https://github.com/rod-trent/JunkDrawer.git
cd JunkDrawer/TaskFolder
dotnet build -c Release
```

Output: `bin/Release/net8.0-windows/TaskFolder.exe`

## 📖 Usage

### Adding Applications

**Method 1: GUI**
1. Right-click TaskFolder system tray icon
2. Click "Add Application..."
3. Browse to any `.exe` or `.lnk` file
4. Done!

**Method 2: Direct**
- Drop shortcut files into: `%APPDATA%\TaskFolder\Shortcuts\`
- TaskFolder automatically detects and adds them

### Launching Applications

- **Left-click** the tray icon to see your menu
- **Click** any application to launch it
- **Right-click** for settings and management

### Managing Shortcuts

- **Remove**: Right-click shortcut in menu → Remove
- **Rename**: Open shortcuts folder → Rename the .lnk file
- **Reorder**: Rename files (sorted alphabetically)
- **Organize**: Use the shortcuts folder like any Windows folder

## 💡 Use Cases

### For Power Users
- Quick access to development tools
- Launch different IDE profiles
- Access PowerShell scripts instantly
- Open VMs and databases

### For Productivity
- Email and calendar (as PWAs)
- Slack, Teams, Discord
- Notion, Todoist, Trello
- Reference documents

### For Everyone
- Favorite websites as apps
- Frequently-used Office apps
- Remote desktop connections
- Anything with a shortcut!

## 🎨 PWA Support

TaskFolder has excellent support for Progressive Web Apps:

**Correct Icon Extraction**
- Gmail shows ✉️ Gmail icon (not Edge icon)
- YouTube shows ▶️ YouTube icon
- Twitter shows 🐦 Twitter icon

**Proper Launch Behavior**
- PWAs open as dedicated app windows
- All command-line arguments preserved
- Works identically to taskbar-pinned PWAs

**How?** TaskFolder launches the `.lnk` file itself (not the executable), letting Windows handle all the parameters correctly.

## ⚙️ Settings

Access via: Right-click tray icon → "Settings"

- ☑️ **Start with Windows** - Auto-start on boot
- 📁 **Shortcuts Folder** - Open the shortcuts directory
- 🗑️ **Clear All** - Remove all shortcuts at once

## 📂 File Locations

**Shortcuts Folder:**
```
%APPDATA%\TaskFolder\Shortcuts\
```
Typical: `C:\Users\YourName\AppData\Roaming\TaskFolder\Shortcuts\`

**Auto-Start Registry:**
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run\TaskFolder
```

## 🏗️ Architecture

### Tech Stack
- **.NET 8.0** - Modern, cross-platform framework
- **Windows Forms** - System tray and UI
- **WPF Components** - Advanced Windows features
- **Dynamic COM** - Shortcut manipulation
- **Win32 APIs** - Icon extraction

### Project Structure
```
TaskFolder/
├── Program.cs              # Entry point & tray logic
├── Models/
│   └── ShortcutItem.cs    # Shortcut data model
├── Services/
│   ├── ShortcutManager.cs # Core management
│   └── JumpListManager.cs # Jump List (disabled)
├── Views/
│   └── SettingsForm.cs    # Settings dialog
└── Utilities/
    ├── IconExtractor.cs   # Icon handling
    └── DragDropHelper.cs  # Drag-drop support
```

### Design Principles

**Why launch `.lnk` files instead of executables?**

Most launcher apps make the mistake of launching the target executable directly, which breaks:
- PWAs with `--app` flags
- Applications with specific parameters
- Shortcuts with custom working directories

TaskFolder launches the shortcut file itself, letting Windows handle everything correctly.

**Why system tray instead of taskbar toolbar?**

Windows 11 deprecated the toolbar APIs that Windows 7 used. The system tray approach is actually better:
- Always accessible (no need to pin)
- Takes zero taskbar space
- Faster to access (single click)
- More reliable across Windows updates

## 🔧 Development

### Requirements
- Visual Studio 2022 or VS Code
- .NET 8.0 SDK

### Build Commands
```bash
# Debug build
dotnet build

# Release build
dotnet build -c Release

# Run
dotnet run

# Create self-contained executable
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

### Code Style
- Standard C# conventions
- XML documentation comments
- Async/await where appropriate
- Exception handling with user-friendly messages

## 🐛 Known Issues

None currently reported! 🎉

If you find a bug, please [open an issue](../../issues).

## 🚧 Roadmap

Potential future features (contributions welcome!):

- [ ] **Search functionality** - Filter shortcuts by name
- [ ] **Categories/folders** - Organize shortcuts in groups
- [ ] **Keyboard shortcuts** - Launch with hotkeys
- [ ] **Statistics** - Track most-used applications
- [ ] **Themes** - Light/dark mode
- [ ] **Cloud sync** - Sync shortcuts across machines
- [ ] **Portable mode** - Run from USB drive
- [ ] **Custom icon picker** - Override detected icons

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Good First Issues
- Add search box to tray menu
- Implement custom icon selection
- Add usage statistics
- Create installer (Inno Setup or WiX)
- Add unit tests

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

**TL;DR:** Do whatever you want with this code. Use it, modify it, distribute it, sell it—I don't care. Just don't blame me if something breaks. 😊

## 🙏 Acknowledgments

- Inspired by Windows 7's taskbar toolbars (RIP)
- Built out of frustration with Windows 11's limitations
- Powered by coffee and stubbornness

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Blog Post**: [Read the full story](#) *(link to your blog post)*

## ⭐ Star History

If you find TaskFolder useful, consider giving it a star! ⭐

It helps others discover the project and motivates continued development.

---

**Made with ❤️ by [@rod-trent](https://github.com/rod-trent)**

*A human-written tool for humans who are tired of Windows 11's taskbar limitations.*
