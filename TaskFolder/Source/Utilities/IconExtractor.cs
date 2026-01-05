using System;
using System.Drawing;
using System.Runtime.InteropServices;

namespace TaskFolder.Utilities
{
    /// <summary>
    /// Utility class for extracting icons from executable files
    /// </summary>
    public static class IconExtractor
    {
        [DllImport("shell32.dll", CharSet = CharSet.Auto)]
        private static extern IntPtr ExtractIcon(IntPtr hInst, string lpszExeFileName, int nIconIndex);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool DestroyIcon(IntPtr hIcon);

        /// <summary>
        /// Extracts an icon from an executable file
        /// </summary>
        /// <param name="filePath">Path to the executable file</param>
        /// <param name="iconIndex">Index of the icon to extract (default: 0)</param>
        /// <returns>The extracted icon, or a default icon if extraction fails</returns>
        public static Icon ExtractIcon(string filePath, int iconIndex = 0)
        {
            if (string.IsNullOrEmpty(filePath) || !System.IO.File.Exists(filePath))
            {
                return SystemIcons.Application;
            }

            IntPtr hIcon = IntPtr.Zero;
            Icon icon = null;

            try
            {
                // Extract the icon
                hIcon = ExtractIcon(IntPtr.Zero, filePath, iconIndex);

                if (hIcon != IntPtr.Zero && hIcon != new IntPtr(-1))
                {
                    // Create a copy of the icon
                    icon = (Icon)Icon.FromHandle(hIcon).Clone();
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to extract icon from {filePath}: {ex.Message}");
            }
            finally
            {
                // Clean up the extracted icon handle
                if (hIcon != IntPtr.Zero && hIcon != new IntPtr(-1))
                {
                    DestroyIcon(hIcon);
                }
            }

            // Return the extracted icon or a default icon
            return icon ?? SystemIcons.Application;
        }

        /// <summary>
        /// Extracts the large icon from a file
        /// </summary>
        public static Icon ExtractLargeIcon(string filePath)
        {
            if (string.IsNullOrEmpty(filePath) || !System.IO.File.Exists(filePath))
            {
                return SystemIcons.Application;
            }

            try
            {
                Icon icon = Icon.ExtractAssociatedIcon(filePath);
                return icon ?? SystemIcons.Application;
            }
            catch
            {
                return SystemIcons.Application;
            }
        }

        /// <summary>
        /// Gets the icon for a shortcut (.lnk) file
        /// </summary>
        public static Icon GetShortcutIcon(string shortcutPath)
        {
            if (string.IsNullOrEmpty(shortcutPath) || !System.IO.File.Exists(shortcutPath))
            {
                return SystemIcons.Application;
            }

            try
            {
                // If it's a .lnk file, check for custom icon first
                if (shortcutPath.EndsWith(".lnk", StringComparison.OrdinalIgnoreCase))
                {
                    Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                    dynamic shell = Activator.CreateInstance(shellType);
                    dynamic link = shell.CreateShortcut(shortcutPath);
                    
                    // First, try to get custom icon from IconLocation
                    try
                    {
                        string iconLocation = link.IconLocation;
                        if (!string.IsNullOrEmpty(iconLocation))
                        {
                            // IconLocation format: "path,index" like "C:\path\icon.ico,0"
                            var parts = iconLocation.Split(',');
                            string iconPath = parts[0].Trim().Trim('"');
                            int iconIndex = 0;
                            
                            if (parts.Length > 1)
                            {
                                int.TryParse(parts[1].Trim(), out iconIndex);
                            }
                            
                            if (System.IO.File.Exists(iconPath))
                            {
                                Icon customIcon = ExtractIcon(iconPath, iconIndex);
                                if (customIcon != null)
                                {
                                    return customIcon;
                                }
                            }
                        }
                    }
                    catch
                    {
                        // IconLocation not available or failed
                    }
                    
                    // If no custom icon, try target path
                    string targetPath = link.TargetPath;
                    if (!string.IsNullOrEmpty(targetPath) && System.IO.File.Exists(targetPath))
                    {
                        Icon targetIcon = ExtractIcon(targetPath);
                        if (targetIcon != null)
                        {
                            return targetIcon;
                        }
                    }
                }

                // Fallback: Extract associated icon from the .lnk file itself
                Icon associatedIcon = Icon.ExtractAssociatedIcon(shortcutPath);
                if (associatedIcon != null)
                {
                    return associatedIcon;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to extract icon from {shortcutPath}: {ex.Message}");
            }
            
            return SystemIcons.Application;
        }

        /// <summary>
        /// Converts an icon to a bitmap for use in menus
        /// </summary>
        public static Bitmap IconToBitmap(Icon icon, int size = 16)
        {
            if (icon == null)
                return null;

            try
            {
                Bitmap bitmap = new Bitmap(size, size);
                using (Graphics g = Graphics.FromImage(bitmap))
                {
                    g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                    g.DrawIcon(icon, new Rectangle(0, 0, size, size));
                }
                return bitmap;
            }
            catch
            {
                return null;
            }
        }
    }
}
