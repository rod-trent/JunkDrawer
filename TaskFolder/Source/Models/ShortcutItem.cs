using System;
using System.Drawing;
using System.IO;

namespace TaskFolder.Models
{
    /// <summary>
    /// Represents a shortcut item in the TaskFolder
    /// </summary>
    public class ShortcutItem
    {
        /// <summary>
        /// Display name of the shortcut
        /// </summary>
        public string Name { get; set; }

        /// <summary>
        /// Full path to the target executable or link file
        /// </summary>
        public string TargetPath { get; set; }

        /// <summary>
        /// Working directory for the application
        /// </summary>
        public string WorkingDirectory { get; set; }

        /// <summary>
        /// Arguments to pass to the application
        /// </summary>
        public string Arguments { get; set; }

        /// <summary>
        /// Icon associated with the shortcut
        /// </summary>
        public Icon Icon { get; set; }

        /// <summary>
        /// Path to the shortcut file (.lnk) in the TaskFolder directory
        /// </summary>
        public string ShortcutFilePath { get; set; }

        /// <summary>
        /// Date the shortcut was created
        /// </summary>
        public DateTime DateCreated { get; set; }

        /// <summary>
        /// Date the shortcut was last used
        /// </summary>
        public DateTime? LastUsed { get; set; }

        /// <summary>
        /// Number of times the shortcut has been launched
        /// </summary>
        public int LaunchCount { get; set; }

        /// <summary>
        /// Custom sort order (lower numbers appear first)
        /// </summary>
        public int SortOrder { get; set; }

        /// <summary>
        /// Description or tooltip for the shortcut
        /// </summary>
        public string Description { get; set; }

        public ShortcutItem()
        {
            DateCreated = DateTime.Now;
            LaunchCount = 0;
            SortOrder = int.MaxValue;
        }

        /// <summary>
        /// Returns true if the target file exists
        /// </summary>
        public bool IsValid()
        {
            if (string.IsNullOrEmpty(TargetPath))
                return false;

            try
            {
                return File.Exists(TargetPath) || Directory.Exists(TargetPath);
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Gets the file name without extension for display
        /// </summary>
        public string GetDisplayName()
        {
            if (!string.IsNullOrEmpty(Name))
                return Name;

            if (string.IsNullOrEmpty(TargetPath))
                return "Unknown";

            return Path.GetFileNameWithoutExtension(TargetPath);
        }

        public override string ToString()
        {
            return $"{Name ?? GetDisplayName()} -> {TargetPath}";
        }

        public override bool Equals(object obj)
        {
            if (obj is ShortcutItem other)
            {
                return string.Equals(TargetPath, other.TargetPath, StringComparison.OrdinalIgnoreCase);
            }
            return false;
        }

        public override int GetHashCode()
        {
            return TargetPath?.ToLowerInvariant().GetHashCode() ?? 0;
        }
    }
}
