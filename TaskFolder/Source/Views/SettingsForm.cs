using System;
using System.Windows.Forms;
using Microsoft.Win32;
using TaskFolder.Services;

namespace TaskFolder.Views
{
    /// <summary>
    /// Settings form for TaskFolder configuration
    /// </summary>
    public partial class SettingsForm : Form
    {
        private ShortcutManager shortcutManager;
        private CheckBox chkAutoStart;
        private CheckBox chkShowNotifications;
        private Button btnOpenFolder;
        private Button btnClearShortcuts;
        private Button btnOK;
        private Button btnCancel;
        private Label lblVersion;
        private GroupBox grpStartup;
        private GroupBox grpShortcuts;
        private GroupBox grpAbout;

        public SettingsForm(ShortcutManager manager)
        {
            shortcutManager = manager;
            InitializeComponent();
            LoadSettings();
        }

        private void InitializeComponent()
        {
            this.Text = "TaskFolder Settings";
            this.Size = new System.Drawing.Size(450, 400);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;

            // Startup group
            grpStartup = new GroupBox
            {
                Text = "Startup",
                Location = new System.Drawing.Point(15, 15),
                Size = new System.Drawing.Size(405, 80)
            };

            chkAutoStart = new CheckBox
            {
                Text = "Start TaskFolder when Windows starts",
                Location = new System.Drawing.Point(15, 25),
                Size = new System.Drawing.Size(370, 20),
                Checked = IsAutoStartEnabled()
            };
            chkAutoStart.CheckedChanged += ChkAutoStart_CheckedChanged;

            chkShowNotifications = new CheckBox
            {
                Text = "Show notifications when applications are launched",
                Location = new System.Drawing.Point(15, 50),
                Size = new System.Drawing.Size(370, 20),
                Checked = true
            };

            grpStartup.Controls.Add(chkAutoStart);
            grpStartup.Controls.Add(chkShowNotifications);

            // Shortcuts group
            grpShortcuts = new GroupBox
            {
                Text = "Shortcuts Management",
                Location = new System.Drawing.Point(15, 105),
                Size = new System.Drawing.Size(405, 100)
            };

            btnOpenFolder = new Button
            {
                Text = "Open Shortcuts Folder",
                Location = new System.Drawing.Point(15, 25),
                Size = new System.Drawing.Size(180, 30)
            };
            btnOpenFolder.Click += BtnOpenFolder_Click;

            btnClearShortcuts = new Button
            {
                Text = "Remove All Shortcuts",
                Location = new System.Drawing.Point(210, 25),
                Size = new System.Drawing.Size(180, 30)
            };
            btnClearShortcuts.Click += BtnClearShortcuts_Click;

            Label lblFolderPath = new Label
            {
                Text = $"Folder: {shortcutManager.ShortcutsFolder}",
                Location = new System.Drawing.Point(15, 65),
                Size = new System.Drawing.Size(375, 25),
                AutoEllipsis = true
            };

            grpShortcuts.Controls.Add(btnOpenFolder);
            grpShortcuts.Controls.Add(btnClearShortcuts);
            grpShortcuts.Controls.Add(lblFolderPath);

            // About group
            grpAbout = new GroupBox
            {
                Text = "About",
                Location = new System.Drawing.Point(15, 215),
                Size = new System.Drawing.Size(405, 80)
            };

            lblVersion = new Label
            {
                Text = "TaskFolder v1.0\nWindows 11 Application Launcher\n© 2025",
                Location = new System.Drawing.Point(15, 25),
                Size = new System.Drawing.Size(375, 45),
                TextAlign = System.Drawing.ContentAlignment.MiddleCenter
            };

            grpAbout.Controls.Add(lblVersion);

            // Buttons
            btnOK = new Button
            {
                Text = "OK",
                DialogResult = DialogResult.OK,
                Location = new System.Drawing.Point(250, 315),
                Size = new System.Drawing.Size(80, 30)
            };
            btnOK.Click += BtnOK_Click;

            btnCancel = new Button
            {
                Text = "Cancel",
                DialogResult = DialogResult.Cancel,
                Location = new System.Drawing.Point(340, 315),
                Size = new System.Drawing.Size(80, 30)
            };

            // Add controls to form
            this.Controls.Add(grpStartup);
            this.Controls.Add(grpShortcuts);
            this.Controls.Add(grpAbout);
            this.Controls.Add(btnOK);
            this.Controls.Add(btnCancel);

            this.AcceptButton = btnOK;
            this.CancelButton = btnCancel;
        }

        private void LoadSettings()
        {
            // Load settings from registry or config file
            chkAutoStart.Checked = IsAutoStartEnabled();
        }

        private bool IsAutoStartEnabled()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(
                    @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", false))
                {
                    return key?.GetValue("TaskFolder") != null;
                }
            }
            catch
            {
                return false;
            }
        }

        private void SetAutoStart(bool enable)
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(
                    @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", true))
                {
                    if (enable)
                    {
                        string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location;
                        key?.SetValue("TaskFolder", $"\"{exePath}\"");
                    }
                    else
                    {
                        key?.DeleteValue("TaskFolder", false);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to update startup settings:\n{ex.Message}",
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ChkAutoStart_CheckedChanged(object sender, EventArgs e)
        {
            // Auto-start setting will be saved when OK is clicked
        }

        private void BtnOpenFolder_Click(object sender, EventArgs e)
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
                MessageBox.Show($"Failed to open folder:\n{ex.Message}",
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void BtnClearShortcuts_Click(object sender, EventArgs e)
        {
            var result = MessageBox.Show(
                "Are you sure you want to remove all shortcuts?\nThis action cannot be undone.",
                "Confirm Clear Shortcuts",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Warning);

            if (result == DialogResult.Yes)
            {
                try
                {
                    var shortcuts = shortcutManager.GetAllShortcuts();
                    foreach (var shortcut in shortcuts)
                    {
                        shortcutManager.RemoveShortcut(shortcut);
                    }

                    MessageBox.Show("All shortcuts have been removed.",
                        "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Failed to clear shortcuts:\n{ex.Message}",
                        "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        private void BtnOK_Click(object sender, EventArgs e)
        {
            // Save settings
            SetAutoStart(chkAutoStart.Checked);
            this.Close();
        }
    }
}
