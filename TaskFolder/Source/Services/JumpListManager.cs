using System;
using System.Collections.Generic;
using System.Windows.Shell;
using System.Linq;
using TaskFolder.Models;

namespace TaskFolder.Services
{
    /// <summary>
    /// Manages Windows Jump List integration for TaskFolder
    /// </summary>
    public class JumpListManager
    {
        private JumpList jumpList;

        public JumpListManager()
        {
            InitializeJumpList();
        }

        private void InitializeJumpList()
        {
            try
            {
                // JumpList requires WPF Application which doesn't exist in Windows Forms
                // We'll skip Jump List functionality for now
                System.Diagnostics.Debug.WriteLine("Jump List disabled - WPF Application required");
                jumpList = null;
                return;
                
                /* Disabled until WPF Application is properly initialized
                // Check if WPF Application exists, if not create one
                if (System.Windows.Application.Current == null)
                {
                    // JumpList requires WPF Application, skip initialization
                    System.Diagnostics.Debug.WriteLine("WPF Application not available, Jump List disabled");
                    return;
                }
                
                jumpList = JumpList.GetJumpList(System.Windows.Application.Current);
                
                if (jumpList == null)
                {
                    jumpList = new JumpList();
                    JumpList.SetJumpList(System.Windows.Application.Current, jumpList);
                }

                // Configure jump list settings
                jumpList.ShowFrequentCategory = false;
                jumpList.ShowRecentCategory = false;
                */
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to initialize Jump List: {ex.Message}");
                jumpList = null;
            }
        }

        /// <summary>
        /// Updates the jump list with the current shortcuts
        /// </summary>
        public void UpdateJumpList(List<ShortcutItem> shortcuts)
        {
            if (jumpList == null)
                return;

            try
            {
                // Clear existing custom categories
                jumpList.JumpItems.Clear();

                // Add shortcuts as jump tasks
                foreach (var shortcut in shortcuts.Take(10)) // Limit to 10 items
                {
                    if (!shortcut.IsValid())
                        continue;

                    var jumpTask = new JumpTask
                    {
                        Title = shortcut.GetDisplayName(),
                        Description = shortcut.Description ?? $"Launch {shortcut.GetDisplayName()}",
                        ApplicationPath = shortcut.TargetPath,
                        Arguments = shortcut.Arguments ?? string.Empty,
                        WorkingDirectory = shortcut.WorkingDirectory ?? 
                            System.IO.Path.GetDirectoryName(shortcut.TargetPath),
                        IconResourcePath = shortcut.TargetPath,
                        IconResourceIndex = 0,
                        CustomCategory = "Applications"
                    };

                    jumpList.JumpItems.Add(jumpTask);
                }

                // Add TaskFolder management tasks
                AddManagementTasks();

                // Apply changes
                jumpList.Apply();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to update jump list: {ex.Message}");
            }
        }

        private void AddManagementTasks()
        {
            // Add separator
            jumpList.JumpItems.Add(new JumpTask
            {
                CustomCategory = "TaskFolder",
                Title = "-"
            });

            // Add "Open Shortcuts Folder" task
            var openFolderTask = new JumpTask
            {
                Title = "Open Shortcuts Folder",
                Description = "Open the folder containing your shortcuts",
                ApplicationPath = "explorer.exe",
                Arguments = GetShortcutsFolder(),
                IconResourcePath = "explorer.exe",
                CustomCategory = "TaskFolder"
            };
            jumpList.JumpItems.Add(openFolderTask);

            // Add "Settings" task
            var settingsTask = new JumpTask
            {
                Title = "Settings",
                Description = "Configure TaskFolder settings",
                ApplicationPath = System.Reflection.Assembly.GetExecutingAssembly().Location,
                Arguments = "/settings",
                CustomCategory = "TaskFolder"
            };
            jumpList.JumpItems.Add(settingsTask);
        }

        private string GetShortcutsFolder()
        {
            string appDataFolder = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            return System.IO.Path.Combine(appDataFolder, "TaskFolder", "Shortcuts");
        }

        /// <summary>
        /// Adds a single shortcut to the recent items
        /// </summary>
        public void AddRecentItem(ShortcutItem shortcut)
        {
            if (shortcut == null || !shortcut.IsValid())
                return;

            try
            {
                // Note: This requires the application to be registered for the file type
                // For now, we'll skip this as it's complex for a general-purpose launcher
                System.Diagnostics.Debug.WriteLine($"Added recent item: {shortcut.GetDisplayName()}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to add recent item: {ex.Message}");
            }
        }
    }
}
