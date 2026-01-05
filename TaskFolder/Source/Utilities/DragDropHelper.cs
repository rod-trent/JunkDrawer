using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace TaskFolder.Utilities
{
    /// <summary>
    /// Provides drag and drop functionality for the TaskFolder application.
    /// Note: Direct taskbar drag-and-drop is limited in Windows 11.
    /// This class provides alternative solutions.
    /// </summary>
    public class DragDropHelper
    {
        [DllImport("ole32.dll")]
        private static extern int RegisterDragDrop(IntPtr hwnd, IDropTarget pDropTarget);

        [DllImport("ole32.dll")]
        private static extern int RevokeDragDrop(IntPtr hwnd);

        /// <summary>
        /// Enables drag-and-drop for a window handle
        /// </summary>
        public static void EnableDragDrop(IntPtr windowHandle, Action<string[]> onFilesDropped)
        {
            if (windowHandle == IntPtr.Zero)
                throw new ArgumentException("Invalid window handle");

            // Create a drop target
            var dropTarget = new FileDropTarget(onFilesDropped);
            
            // Register the drop target with OLE
            int result = RegisterDragDrop(windowHandle, dropTarget);
            
            if (result != 0)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to register drag-drop: HRESULT {result:X8}");
            }
        }

        /// <summary>
        /// Disables drag-and-drop for a window handle
        /// </summary>
        public static void DisableDragDrop(IntPtr windowHandle)
        {
            if (windowHandle != IntPtr.Zero)
            {
                RevokeDragDrop(windowHandle);
            }
        }

        /// <summary>
        /// Creates a Form that accepts file drops and adds them to TaskFolder
        /// This can be used as an alternative to direct taskbar drag-drop
        /// </summary>
        public static Form CreateDropZoneForm(Action<string[]> onFilesDropped)
        {
            var form = new Form
            {
                Text = "TaskFolder Drop Zone",
                Width = 300,
                Height = 200,
                FormBorderStyle = FormBorderStyle.FixedToolWindow,
                StartPosition = FormStartPosition.CenterScreen,
                AllowDrop = true,
                TopMost = true
            };

            var label = new Label
            {
                Text = "Drop application files here\nto add to TaskFolder",
                Dock = DockStyle.Fill,
                TextAlign = System.Drawing.ContentAlignment.MiddleCenter,
                Font = new System.Drawing.Font("Segoe UI", 12, System.Drawing.FontStyle.Regular)
            };

            form.Controls.Add(label);

            form.DragEnter += (s, e) =>
            {
                if (e.Data.GetDataPresent(DataFormats.FileDrop))
                {
                    e.Effect = DragDropEffects.Copy;
                    label.BackColor = System.Drawing.Color.LightGreen;
                }
                else
                {
                    e.Effect = DragDropEffects.None;
                }
            };

            form.DragLeave += (s, e) =>
            {
                label.BackColor = System.Drawing.SystemColors.Control;
            };

            form.DragDrop += (s, e) =>
            {
                label.BackColor = System.Drawing.SystemColors.Control;
                
                if (e.Data.GetDataPresent(DataFormats.FileDrop))
                {
                    string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                    onFilesDropped?.Invoke(files);
                }
            };

            return form;
        }
    }

    /// <summary>
    /// Implementation of IDropTarget for OLE drag-and-drop
    /// </summary>
    [ComVisible(true)]
    internal class FileDropTarget : IDropTarget
    {
        private readonly Action<string[]> onFilesDropped;

        public FileDropTarget(Action<string[]> onFilesDropped)
        {
            this.onFilesDropped = onFilesDropped;
        }

        public int DragEnter(IDataObject pDataObj, uint grfKeyState, POINTL pt, ref uint pdwEffect)
        {
            pdwEffect = (uint)DragDropEffects.Copy;
            return 0; // S_OK
        }

        public int DragOver(uint grfKeyState, POINTL pt, ref uint pdwEffect)
        {
            pdwEffect = (uint)DragDropEffects.Copy;
            return 0; // S_OK
        }

        public int DragLeave()
        {
            return 0; // S_OK
        }

        public int Drop(IDataObject pDataObj, uint grfKeyState, POINTL pt, ref uint pdwEffect)
        {
            try
            {
                // Get the dropped files
                var format = new FORMATETC
                {
                    cfFormat = (short)DataFormats.GetFormat(DataFormats.FileDrop).Id,
                    dwAspect = DVASPECT.DVASPECT_CONTENT,
                    lindex = -1,
                    tymed = TYMED.TYMED_HGLOBAL
                };

                STGMEDIUM medium;
                pDataObj.GetData(ref format, out medium);

                if (medium.unionmember != IntPtr.Zero)
                {
                    string[] files = GetFilesFromHDrop(medium.unionmember);
                    onFilesDropped?.Invoke(files);
                    
                    ReleaseStgMedium(ref medium);
                }

                pdwEffect = (uint)DragDropEffects.Copy;
                return 0; // S_OK
            }
            catch
            {
                pdwEffect = (uint)DragDropEffects.None;
                return unchecked((int)0x80004005); // E_FAIL
            }
        }

        [DllImport("shell32.dll")]
        private static extern uint DragQueryFile(IntPtr hDrop, uint iFile, 
            System.Text.StringBuilder lpszFile, uint cch);

        [DllImport("ole32.dll")]
        private static extern void ReleaseStgMedium(ref STGMEDIUM pmedium);

        private string[] GetFilesFromHDrop(IntPtr hDrop)
        {
            uint fileCount = DragQueryFile(hDrop, 0xFFFFFFFF, null, 0);
            string[] files = new string[fileCount];

            for (uint i = 0; i < fileCount; i++)
            {
                uint length = DragQueryFile(hDrop, i, null, 0);
                var fileName = new System.Text.StringBuilder((int)length + 1);
                DragQueryFile(hDrop, i, fileName, (uint)fileName.Capacity);
                files[i] = fileName.ToString();
            }

            return files;
        }
    }

    #region COM Interop Definitions

    [ComImport]
    [Guid("00000121-0000-0000-C000-000000000046")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IDropTarget
    {
        [PreserveSig]
        int DragEnter([In] IDataObject pDataObj, [In] uint grfKeyState, 
            [In] POINTL pt, [In, Out] ref uint pdwEffect);

        [PreserveSig]
        int DragOver([In] uint grfKeyState, [In] POINTL pt, [In, Out] ref uint pdwEffect);

        [PreserveSig]
        int DragLeave();

        [PreserveSig]
        int Drop([In] IDataObject pDataObj, [In] uint grfKeyState, 
            [In] POINTL pt, [In, Out] ref uint pdwEffect);
    }

    [ComImport]
    [Guid("0000010E-0000-0000-C000-000000000046")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IDataObject
    {
        void GetData(ref FORMATETC format, out STGMEDIUM medium);
        void GetDataHere(ref FORMATETC format, ref STGMEDIUM medium);
        int QueryGetData(ref FORMATETC format);
        int GetCanonicalFormatEtc(ref FORMATETC formatIn, out FORMATETC formatOut);
        void SetData(ref FORMATETC formatIn, ref STGMEDIUM medium, bool release);
        int EnumFormatEtc(uint direction);
        int DAdvise(ref FORMATETC pFormatetc, uint advf, IntPtr adviseSink, out uint connection);
        void DUnadvise(uint connection);
        int EnumDAdvise(out IntPtr enumAdvise);
    }

    [StructLayout(LayoutKind.Sequential)]
    internal struct POINTL
    {
        public int x;
        public int y;
    }

    [StructLayout(LayoutKind.Sequential)]
    internal struct FORMATETC
    {
        public short cfFormat;
        public IntPtr ptd;
        public DVASPECT dwAspect;
        public int lindex;
        public TYMED tymed;
    }

    [StructLayout(LayoutKind.Sequential)]
    internal struct STGMEDIUM
    {
        public TYMED tymed;
        public IntPtr unionmember;
        public IntPtr pUnkForRelease;
    }

    internal enum DVASPECT
    {
        DVASPECT_CONTENT = 1,
        DVASPECT_THUMBNAIL = 2,
        DVASPECT_ICON = 4,
        DVASPECT_DOCPRINT = 8
    }

    [Flags]
    internal enum TYMED
    {
        TYMED_HGLOBAL = 1,
        TYMED_FILE = 2,
        TYMED_ISTREAM = 4,
        TYMED_ISTORAGE = 8,
        TYMED_GDI = 16,
        TYMED_MFPICT = 32,
        TYMED_ENHMF = 64,
        TYMED_NULL = 0
    }

    #endregion
}
