using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using TaskFolder.Models;
using TaskFolder.Utilities;

namespace TaskFolder.Services
{
    /// <summary>
    /// Manages shortcuts in the TaskFolder
    /// </summary>
    public class ShortcutManager : IDisposable
    {
        private readonly string shortcutsFolder;
        private readonly List<ShortcutItem> shortcuts;
        private FileSystemWatcher fileWatcher;

        public event EventHandler ShortcutsChanged;

        /// <summary>
        /// Gets the folder where shortcuts are stored
        /// </summary>
        public string ShortcutsFolder => shortcutsFolder;

        public ShortcutManager()
        {
            // Create shortcuts folder in AppData
            string appDataFolder = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            shortcutsFolder = Path.Combine(appDataFolder, "TaskFolder", "Shortcuts");

            if (!Directory.Exists(shortcutsFolder))
            {
                Directory.CreateDirectory(shortcutsFolder);
            }

            shortcuts = new List<ShortcutItem>();
            LoadShortcuts();
            InitializeFileWatcher();
        }

        private void InitializeFileWatcher()
        {
            fileWatcher = new FileSystemWatcher(shortcutsFolder)
            {
                NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite,
                Filter = "*.lnk"
            };

            fileWatcher.Created += OnFileSystemChanged;
            fileWatcher.Deleted += OnFileSystemChanged;
            fileWatcher.Renamed += OnFileSystemChanged;
            fileWatcher.Changed += OnFileSystemChanged;

            fileWatcher.EnableRaisingEvents = true;
        }

        private void OnFileSystemChanged(object sender, FileSystemEventArgs e)
        {
            // Reload shortcuts when the folder changes
            LoadShortcuts();
            ShortcutsChanged?.Invoke(this, EventArgs.Empty);
        }

        /// <summary>
        /// Loads all shortcuts from the shortcuts folder
        /// </summary>
        private void LoadShortcuts()
        {
            shortcuts.Clear();

            try
            {
                var linkFiles = Directory.GetFiles(shortcutsFolder, "*.lnk");

                foreach (var linkFile in linkFiles)
                {
                    try
                    {
                        var shortcut = LoadShortcutFromFile(linkFile);
                        if (shortcut != null && shortcut.IsValid())
                        {
                            shortcuts.Add(shortcut);
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Failed to load shortcut {linkFile}: {ex.Message}");
                    }
                }

                // Sort by custom order, then by name
                shortcuts.Sort((a, b) =>
                {
                    int orderCompare = a.SortOrder.CompareTo(b.SortOrder);
                    return orderCompare != 0 ? orderCompare : 
                        string.Compare(a.GetDisplayName(), b.GetDisplayName(), StringComparison.OrdinalIgnoreCase);
                });
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to load shortcuts: {ex.Message}");
            }
        }

        /// <summary>
        /// Loads a shortcut from a .lnk file using dynamic COM
        /// </summary>
        private ShortcutItem LoadShortcutFromFile(string linkPath)
        {
            try
            {
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                dynamic shell = Activator.CreateInstance(shellType);
                dynamic link = shell.CreateShortcut(linkPath);

                // Try to get the icon from the shortcut's IconLocation property first
                Icon shortcutIcon = null;
                try
                {
                    string iconLocation = link.IconLocation;
                    if (!string.IsNullOrEmpty(iconLocation))
                    {
                        // IconLocation format is typically "path,index" like "C:\path\file.ico,0"
                        var parts = iconLocation.Split(',');
                        string iconPath = parts[0].Trim();
                        int iconIndex = parts.Length > 1 && int.TryParse(parts[1].Trim(), out int idx) ? idx : 0;
                        
                        if (System.IO.File.Exists(iconPath))
                        {
                            shortcutIcon = IconExtractor.ExtractIcon(iconPath, iconIndex);
                        }
                    }
                }
                catch
                {
                    // IconLocation not available or failed, will fall back below
                }
                
                // If no custom icon, try to extract from the shortcut file itself
                if (shortcutIcon == null)
                {
                    shortcutIcon = IconExtractor.GetShortcutIcon(linkPath);
                }
                
                // Last resort: extract from target executable
                if (shortcutIcon == null)
                {
                    shortcutIcon = IconExtractor.ExtractIcon(link.TargetPath);
                }

                var shortcut = new ShortcutItem
                {
                    Name = Path.GetFileNameWithoutExtension(linkPath),
                    TargetPath = link.TargetPath,
                    WorkingDirectory = link.WorkingDirectory,
                    Arguments = link.Arguments,
                    Description = link.Description,
                    ShortcutFilePath = linkPath,
                    DateCreated = System.IO.File.GetCreationTime(linkPath),
                    Icon = shortcutIcon
                };

                return shortcut;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to load shortcut {linkPath}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Gets all shortcuts
        /// </summary>
        public List<ShortcutItem> GetAllShortcuts()
        {
            return new List<ShortcutItem>(shortcuts);
        }

        /// <summary>
        /// Adds a new shortcut for the specified application
        /// </summary>
        public ShortcutItem AddShortcut(string targetPath, string customName = null)
        {
            if (string.IsNullOrEmpty(targetPath) || !System.IO.File.Exists(targetPath))
            {
                throw new ArgumentException("Target path is invalid or file does not exist.");
            }

            // Check if shortcut already exists
            if (shortcuts.Any(s => s.TargetPath.Equals(targetPath, StringComparison.OrdinalIgnoreCase)))
            {
                throw new InvalidOperationException("A shortcut for this application already exists.");
            }

            // Create shortcut name
            string shortcutName = customName ?? Path.GetFileNameWithoutExtension(targetPath);
            string linkPath = Path.Combine(shortcutsFolder, $"{shortcutName}.lnk");

            // Ensure unique filename
            int counter = 1;
            while (System.IO.File.Exists(linkPath))
            {
                linkPath = Path.Combine(shortcutsFolder, $"{shortcutName} ({counter}).lnk");
                counter++;
            }

            // Create the shortcut using dynamic COM
            try
            {
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                dynamic shell = Activator.CreateInstance(shellType);
                dynamic link = shell.CreateShortcut(linkPath);
                
                link.TargetPath = targetPath;
                link.WorkingDirectory = Path.GetDirectoryName(targetPath);
                link.Description = $"Launch {shortcutName}";
                link.Save();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to create shortcut: {ex.Message}");
                throw;
            }

            // Reload shortcuts
            LoadShortcuts();
            ShortcutsChanged?.Invoke(this, EventArgs.Empty);

            return shortcuts.FirstOrDefault(s => s.ShortcutFilePath == linkPath);
        }

        /// <summary>
        /// Removes a shortcut
        /// </summary>
        public bool RemoveShortcut(ShortcutItem shortcut)
        {
            if (shortcut == null || string.IsNullOrEmpty(shortcut.ShortcutFilePath))
                return false;

            try
            {
                if (System.IO.File.Exists(shortcut.ShortcutFilePath))
                {
                    System.IO.File.Delete(shortcut.ShortcutFilePath);
                }

                shortcuts.Remove(shortcut);
                ShortcutsChanged?.Invoke(this, EventArgs.Empty);
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to remove shortcut: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Renames a shortcut
        /// </summary>
        public bool RenameShortcut(ShortcutItem shortcut, string newName)
        {
            if (shortcut == null || string.IsNullOrEmpty(newName))
                return false;

            try
            {
                string newPath = Path.Combine(shortcutsFolder, $"{newName}.lnk");
                
                if (System.IO.File.Exists(newPath))
                {
                    throw new InvalidOperationException("A shortcut with this name already exists.");
                }

                System.IO.File.Move(shortcut.ShortcutFilePath, newPath);
                
                LoadShortcuts();
                ShortcutsChanged?.Invoke(this, EventArgs.Empty);
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to rename shortcut: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Updates the launch statistics for a shortcut
        /// </summary>
        public void RecordLaunch(ShortcutItem shortcut)
        {
            if (shortcut != null)
            {
                shortcut.LaunchCount++;
                shortcut.LastUsed = DateTime.Now;
            }
        }

        public void Dispose()
        {
            fileWatcher?.Dispose();
        }
    }
}
