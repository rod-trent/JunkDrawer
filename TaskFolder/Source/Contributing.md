# Contributing to TaskFolder

First off, thank you for considering contributing to TaskFolder! 🎉

This is a straightforward project with a simple goal: make a reliable, lightweight application launcher for Windows. We welcome all contributions that align with this vision.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Pull Request Process](#pull-request-process)
- [Good First Issues](#good-first-issues)

## Code of Conduct

Be nice. That's it. We're all here to build something useful.

Specifically:
- Be respectful and constructive
- Welcome newcomers
- Focus on the code, not the person
- Assume good intentions

## How Can I Contribute?

### Reporting Bugs

Found a bug? Here's how to report it:

1. **Check existing issues** - Someone may have already reported it
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs. actual behavior
   - Your environment (Windows version, .NET version)
   - Screenshots if helpful

### Suggesting Features

Have an idea? Great! Before opening an issue:

1. **Check the roadmap** in README.md
2. **Search existing feature requests**
3. **Consider if it fits the project goals**:
   - ✅ Makes launching apps easier
   - ✅ Stays lightweight and fast
   - ✅ Works on Windows 10/11
   - ❌ Adds bloat or complexity
   - ❌ Requires external services

### Writing Code

Want to contribute code? Awesome! Here's the process:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
6. **Push to your fork**
7. **Open a Pull Request**

## Development Setup

### Prerequisites
- Windows 10 or 11
- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- Visual Studio 2022 OR VS Code with C# extension

### Getting Started

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/JunkDrawer.git
cd JunkDrawer/TaskFolder

# Open in your editor
code .  # VS Code
# OR
start TaskFolder.sln  # Visual Studio

# Build
dotnet build

# Run
dotnet run
```

### Project Structure

```
TaskFolder/
├── Program.cs              # Entry point, system tray logic
├── Models/                 # Data models
├── Services/               # Business logic
├── Views/                  # UI components
├── Utilities/              # Helper classes
└── .vscode/               # VS Code configuration
```

### Key Files to Know

- **Program.cs**: System tray icon, menu creation, application lifecycle
- **ShortcutManager.cs**: Loading, adding, removing shortcuts
- **IconExtractor.cs**: Icon extraction from various sources
- **SettingsForm.cs**: Settings dialog UI

## Coding Guidelines

### Style

Follow standard C# conventions:
- PascalCase for classes, methods, properties
- camelCase for local variables, parameters
- Meaningful names (no `x`, `temp`, `data`)
- XML documentation for public APIs

Example:
```csharp
/// <summary>
/// Launches a shortcut by executing its .lnk file
/// </summary>
/// <param name="shortcut">The shortcut to launch</param>
private void LaunchShortcut(ShortcutItem shortcut)
{
    try
    {
        // Implementation
    }
    catch (Exception ex)
    {
        // User-friendly error message
        MessageBox.Show($"Failed to launch: {ex.Message}");
    }
}
```

### Best Practices

**DO:**
- ✅ Add error handling with user-friendly messages
- ✅ Use `using` statements for IDisposable
- ✅ Write self-documenting code
- ✅ Keep methods focused and small
- ✅ Test on Windows 10 AND 11
- ✅ Update documentation

**DON'T:**
- ❌ Add external NuGet dependencies (without discussion)
- ❌ Break existing functionality
- ❌ Remove error handling
- ❌ Add complex dependencies
- ❌ Ignore compiler warnings

### Error Handling

Always handle errors gracefully:

```csharp
try
{
    // Your code
}
catch (Exception ex)
{
    System.Diagnostics.Debug.WriteLine($"Error: {ex.Message}");
    MessageBox.Show("Something went wrong. Please try again.");
}
```

Users should NEVER see a crash dialog if avoidable.

### Testing

Before submitting:

1. **Build succeeds** (no errors or warnings)
2. **App starts** without errors
3. **Core features work**:
   - Add shortcut
   - Launch shortcut
   - Remove shortcut
   - Settings dialog
4. **No crashes** during normal use
5. **Test on clean Windows install** (if possible)

## Pull Request Process

### Before Submitting

- [ ] Code builds without errors
- [ ] All existing functionality still works
- [ ] New code follows style guidelines
- [ ] Added XML documentation for public APIs
- [ ] Tested manually on Windows 11
- [ ] Updated README.md if needed
- [ ] Updated CHANGELOG.md

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How did you test this?

## Screenshots (if applicable)
Add screenshots showing the change

## Checklist
- [ ] Code builds without errors
- [ ] Tested on Windows 11
- [ ] Updated documentation
- [ ] No new warnings
```

### Review Process

1. Maintainer reviews your PR
2. Feedback is provided (if needed)
3. You make requested changes
4. PR is approved and merged

**Note**: I'm a single maintainer, so reviews might take a few days. Be patient!

## Good First Issues

New to the project? Start here:

### Easy
- [ ] Add search box to tray menu (filter shortcuts by name)
- [ ] Add "About" dialog with version info
- [ ] Improve error messages
- [ ] Add tooltips to settings
- [ ] Create application icon

### Medium
- [ ] Implement usage statistics (launch counts, last used)
- [ ] Add keyboard shortcut support (global hotkeys)
- [ ] Create categories/folders for shortcuts
- [ ] Add import from Start Menu
- [ ] Implement backup/restore

### Advanced
- [ ] Create installer (Inno Setup or WiX)
- [ ] Add unit tests
- [ ] Implement cloud sync
- [ ] Add plugin system
- [ ] Create portable mode

## Development Tips

### Debugging

**System Tray Issues:**
- TaskFolder icon not showing? Check Task Manager → TaskFolder.exe is running
- Click the `^` arrow in system tray to see hidden icons

**Icon Extraction:**
- Use Debug.WriteLine to log icon paths
- Check `%APPDATA%\TaskFolder\Shortcuts\` for actual .lnk files

**Build Errors:**
- Clean: `dotnet clean`
- Rebuild: `dotnet build`
- Check .NET SDK version: `dotnet --version`

### Performance

Keep TaskFolder fast:
- Avoid blocking UI thread
- Use async/await for I/O
- Cache icons in memory
- Minimize startup time

### Common Pitfalls

1. **Don't launch executables directly** - Launch the .lnk file instead
2. **Check for null** - Shortcuts might not load properly
3. **Handle icon extraction failures** - Always have a fallback icon
4. **Test with PWAs** - They have special requirements

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open a GitHub Issue
- **Feature ideas**: Open a GitHub Issue with [Feature Request] tag
- **Direct contact**: @rod-trent on GitHub

## Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Mentioned in release notes
- Appreciated forever! 🎉

---

**Thank you for contributing to TaskFolder!** 🚀

Every contribution, no matter how small, makes this project better for everyone.
