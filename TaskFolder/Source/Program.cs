using System;
using System.Drawing;
using System.Windows.Forms;
using System.IO;
using TaskFolder.Models;
using TaskFolder.Services;
using TaskFolder.Views;

namespace TaskFolder
{
    /// <summary>
    /// Main application entry point for TaskFolder
    /// </summary>
    static class Program
    {
        [STAThread]
        static void Main()
        {
            try
            {
                Application.EnableVisualStyles();
                Application.SetCompatibleTextRenderingDefault(false);
                
                // Check if already running
                bool createdNew;
                using (var mutex = new System.Threading.Mutex(true, "TaskFolder_SingleInstance", out createdNew))
                {
                    if (!createdNew)
                    {
                        MessageBox.Show("TaskFolder is already running. Check your system tray.", 
                            "TaskFolder", MessageBoxButtons.OK, MessageBoxIcon.Information);
                        return;
                    }
                    
                    // Run the main application context
                    Application.Run(new TaskFolderApplicationContext());
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Fatal error starting TaskFolder:\n\n{ex.Message}\n\n{ex.StackTrace}", 
                    "TaskFolder Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    /// <summary>
    /// Application context that manages the system tray icon and core services
    /// </summary>
    public class TaskFolderApplicationContext : ApplicationContext
    {
        private NotifyIcon trayIcon;
        private ShortcutManager shortcutManager;
        private JumpListManager jumpListManager;
        private ContextMenuStrip trayMenu;

        public TaskFolderApplicationContext()
        {
            InitializeServices();
            InitializeTrayIcon();
            InitializeJumpList();
        }

        private void InitializeServices()
        {
            // Initialize the shortcut manager
            shortcutManager = new ShortcutManager();
            shortcutManager.ShortcutsChanged += OnShortcutsChanged;

            // Initialize jump list manager
            jumpListManager = new JumpListManager();
        }

        private void InitializeTrayIcon()
        {
            // Create the tray icon
            trayIcon = new NotifyIcon()
            {
                Icon = GetApplicationIcon(),
                ContextMenuStrip = CreateTrayMenu(),
                Visible = true,
                Text = "TaskFolder - Quick Application Launcher"
            };

            // Handle tray icon clicks
            trayIcon.Click += OnTrayIconClick;
            trayIcon.DoubleClick += OnTrayIconDoubleClick;
        }

        private Icon GetApplicationIcon()
        {
            try
            {
                // Try to load custom icon from Resources folder
                string iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Resources", "TaskFolder.ico");
                
                if (File.Exists(iconPath))
                {
                    return new Icon(iconPath);
                }
                
                // Try to load from the executable itself
                var assembly = System.Reflection.Assembly.GetExecutingAssembly();
                var icon = Icon.ExtractAssociatedIcon(assembly.Location);
                if (icon != null)
                {
                    return icon;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to load custom icon: {ex.Message}");
            }
            
            // Fallback to default folder icon
            return SystemIcons.Application;
        }

        private ContextMenuStrip CreateTrayMenu()
        {
            trayMenu = new ContextMenuStrip();

            // Shortcuts header
            var shortcutsHeader = new ToolStripLabel("Applications")
            {
                Font = new Font(trayMenu.Font, FontStyle.Bold),
                ForeColor = Color.DarkBlue
            };
            trayMenu.Items.Add(shortcutsHeader);
            trayMenu.Items.Add(new ToolStripSeparator());

            // Load shortcuts
            RefreshShortcutsList();

            // Separator
            trayMenu.Items.Add(new ToolStripSeparator());

            // Add application option
            var addItem = new ToolStripMenuItem("Add Application...", null, OnAddApplication);
            addItem.Font = new Font(trayMenu.Font, FontStyle.Regular);
            trayMenu.Items.Add(addItem);

            // Open folder option
            var openFolderItem = new ToolStripMenuItem("Open Shortcuts Folder", null, OnOpenFolder);
            trayMenu.Items.Add(openFolderItem);

            // Settings
            var settingsItem = new ToolStripMenuItem("Settings...", null, OnSettings);
            trayMenu.Items.Add(settingsItem);

            // Separator
            trayMenu.Items.Add(new ToolStripSeparator());

            // Exit
            var exitItem = new ToolStripMenuItem("Exit TaskFolder", null, OnExit);
            trayMenu.Items.Add(exitItem);

            return trayMenu;
        }

        private void RefreshShortcutsList()
        {
            // Remove existing shortcut items (items tagged with ShortcutItem)
            // Work backwards to avoid index issues
            for (int i = trayMenu.Items.Count - 1; i >= 0; i--)
            {
                if (trayMenu.Items[i] is ToolStripMenuItem item && item.Tag is ShortcutItem)
                {
                    trayMenu.Items.RemoveAt(i);
                }
                // Also remove the "(No applications added)" item
                else if (trayMenu.Items[i] is ToolStripMenuItem emptyItem && 
                         emptyItem.Text == "(No applications added)")
                {
                    trayMenu.Items.RemoveAt(i);
                }
            }

            // Find the position to insert shortcuts (after header and first separator)
            int insertIndex = 2; // After "Applications" header and separator
            
            // Make sure the index is valid
            if (insertIndex > trayMenu.Items.Count)
            {
                insertIndex = trayMenu.Items.Count;
            }

            // Add current shortcuts
            var shortcuts = shortcutManager.GetAllShortcuts();

            foreach (var shortcut in shortcuts)
            {
                var menuItem = new ToolStripMenuItem(shortcut.GetDisplayName(), shortcut.Icon?.ToBitmap(), 
                    (s, e) => LaunchShortcut(shortcut))
                {
                    Tag = shortcut,
                    ToolTipText = shortcut.TargetPath
                };
                
                // Safety check before inserting
                if (insertIndex <= trayMenu.Items.Count)
                {
                    trayMenu.Items.Insert(insertIndex++, menuItem);
                }
                else
                {
                    trayMenu.Items.Add(menuItem);
                    insertIndex++;
                }
            }

            if (shortcuts.Count == 0)
            {
                var emptyItem = new ToolStripMenuItem("(No applications added)")
                {
                    Enabled = false,
                    Font = new Font(trayMenu.Font, FontStyle.Italic),
                    ForeColor = Color.Gray
                };
                
                // Safety check before inserting
                if (insertIndex <= trayMenu.Items.Count)
                {
                    trayMenu.Items.Insert(insertIndex, emptyItem);
                }
                else
                {
                    trayMenu.Items.Add(emptyItem);
                }
            }
        }

        private void InitializeJumpList()
        {
            // Populate jump list with shortcuts
            var shortcuts = shortcutManager.GetAllShortcuts();
            jumpListManager.UpdateJumpList(shortcuts);
        }

        private void OnShortcutsChanged(object sender, EventArgs e)
        {
            // Refresh both the tray menu and jump list
            RefreshShortcutsList();
            
            var shortcuts = shortcutManager.GetAllShortcuts();
            jumpListManager.UpdateJumpList(shortcuts);
        }

        private void OnTrayIconClick(object sender, EventArgs e)
        {
            // Show context menu on left-click
            if (e is MouseEventArgs me && me.Button == MouseButtons.Left)
            {
                // Use reflection to show the context menu
                var method = typeof(NotifyIcon).GetMethod("ShowContextMenu", 
                    System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                method?.Invoke(trayIcon, null);
            }
        }

        private void OnTrayIconDoubleClick(object sender, EventArgs e)
        {
            // Open the shortcuts folder on double-click
            OnOpenFolder(sender, e);
        }

        private void LaunchShortcut(ShortcutItem shortcut)
        {
            try
            {
                // Launch the .lnk file itself - Windows will handle all the parameters correctly
                if (!string.IsNullOrEmpty(shortcut.ShortcutFilePath) && 
                    File.Exists(shortcut.ShortcutFilePath))
                {
                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = shortcut.ShortcutFilePath,
                        UseShellExecute = true
                    });
                }
                else
                {
                    // Fallback: try launching target directly with arguments
                    var startInfo = new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = shortcut.TargetPath,
                        UseShellExecute = true
                    };
                    
                    if (!string.IsNullOrEmpty(shortcut.Arguments))
                    {
                        startInfo.Arguments = shortcut.Arguments;
                    }
                    
                    if (!string.IsNullOrEmpty(shortcut.WorkingDirectory))
                    {
                        startInfo.WorkingDirectory = shortcut.WorkingDirectory;
                    }
                    
                    System.Diagnostics.Process.Start(startInfo);
                }
                
                // Update statistics
                shortcutManager.RecordLaunch(shortcut);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to launch application:\n{ex.Message}", 
                    "TaskFolder Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void OnAddApplication(object sender, EventArgs e)
        {
            using (var openFileDialog = new OpenFileDialog())
            {
                openFileDialog.Filter = "Applications (*.exe;*.lnk)|*.exe;*.lnk|All Files (*.*)|*.*";
                openFileDialog.Title = "Select Application to Add";

                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    shortcutManager.AddShortcut(openFileDialog.FileName);
                }
            }
        }

        private void OnOpenFolder(object sender, EventArgs e)
        {
            try
            {
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                {
                    FileName = shortcutManager.ShortcutsFolder,
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to open shortcuts folder:\n{ex.Message}", 
                    "TaskFolder Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void OnSettings(object sender, EventArgs e)
        {
            var settingsForm = new SettingsForm(shortcutManager);
            settingsForm.ShowDialog();
        }

        private void OnExit(object sender, EventArgs e)
        {
            // Cleanup
            trayIcon.Visible = false;
            shortcutManager?.Dispose();
            Application.Exit();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                trayIcon?.Dispose();
                trayMenu?.Dispose();
                shortcutManager?.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}
