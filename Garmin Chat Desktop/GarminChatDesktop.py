"""
Garmin Chat - Standalone Desktop Application
A local desktop chatbot for querying Garmin Connect data.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
from pathlib import Path
from garmin_handler import GarminDataHandler
from xai_client import XAIClient
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SettingsDialog(tk.Toplevel):
    """Dialog for managing application settings"""
    
    def __init__(self, parent, current_config=None):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x520")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.result = None
        self.current_config = current_config or {}
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create settings dialog widgets"""
        main_frame = ttk.Frame(self, padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame,
                               text="Application Settings",
                               font=('Segoe UI', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        
        # xAI API Key section
        xai_header = ttk.Label(main_frame,
                              text="xAI Configuration",
                              font=('Segoe UI', 11, 'bold'))
        xai_header.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(main_frame, text="API Key:", font=('Segoe UI', 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        
        self.api_key_var = tk.StringVar(value=self.current_config.get('xai_api_key', ''))
        self.api_key_entry = ttk.Entry(main_frame, 
                                       textvariable=self.api_key_var,
                                       width=50,
                                       show="*",
                                       font=('Segoe UI', 10))
        self.api_key_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        # Show/Hide API key
        self.show_api_key_var = tk.BooleanVar(value=False)
        show_api_check = ttk.Checkbutton(main_frame,
                                         text="Show API key",
                                         variable=self.show_api_key_var,
                                         command=self.toggle_api_key_visibility)
        show_api_check.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # xAI help text
        xai_help = ttk.Label(main_frame,
                            text="Get your API key from: https://console.x.ai/",
                            foreground='#7f8c8d',
                            font=('Segoe UI', 9))
        xai_help.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        # Garmin section
        garmin_header = ttk.Label(main_frame,
                                 text="Garmin Connect Credentials",
                                 font=('Segoe UI', 11, 'bold'))
        garmin_header.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 10))
        
        ttk.Label(main_frame, text="Email:", font=('Segoe UI', 10)).grid(row=6, column=0, sticky=tk.W, pady=8)
        
        self.garmin_email_var = tk.StringVar(value=self.current_config.get('garmin_email', ''))
        self.garmin_email_entry = ttk.Entry(main_frame,
                                           textvariable=self.garmin_email_var,
                                           width=50,
                                           font=('Segoe UI', 10))
        self.garmin_email_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        ttk.Label(main_frame, text="Password:", font=('Segoe UI', 10)).grid(row=7, column=0, sticky=tk.W, pady=8)
        
        self.garmin_password_var = tk.StringVar(value=self.current_config.get('garmin_password', ''))
        self.garmin_password_entry = ttk.Entry(main_frame,
                                              textvariable=self.garmin_password_var,
                                              width=50,
                                              show="*",
                                              font=('Segoe UI', 10))
        self.garmin_password_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))
        
        # Show/Hide Garmin password
        self.show_garmin_password_var = tk.BooleanVar(value=False)
        show_garmin_check = ttk.Checkbutton(main_frame,
                                           text="Show password",
                                           variable=self.show_garmin_password_var,
                                           command=self.toggle_garmin_password_visibility)
        show_garmin_check.grid(row=8, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Garmin help text
        garmin_help = ttk.Label(main_frame,
                               text="Your Garmin Connect login credentials",
                               foreground='#7f8c8d',
                               font=('Segoe UI', 9))
        garmin_help.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 25))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=(20, 10))
        
        save_btn = ttk.Button(button_frame,
                             text="Save",
                             command=self.save_settings,
                             width=15)
        save_btn.grid(row=0, column=0, padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame,
                               text="Cancel",
                               command=self.cancel,
                               width=15)
        cancel_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Add some bottom padding to ensure buttons are visible
        ttk.Label(main_frame, text="").grid(row=11, column=0, pady=(0, 5))
        
        # Focus on first empty field
        if not self.api_key_var.get():
            self.api_key_entry.focus()
        elif not self.garmin_email_var.get():
            self.garmin_email_entry.focus()
        elif not self.garmin_password_var.get():
            self.garmin_password_entry.focus()
        else:
            self.api_key_entry.focus()
        
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.show_api_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
            
    def toggle_garmin_password_visibility(self):
        """Toggle Garmin password visibility"""
        if self.show_garmin_password_var.get():
            self.garmin_password_entry.config(show="")
        else:
            self.garmin_password_entry.config(show="*")
            
    def save_settings(self):
        """Save settings and close"""
        api_key = self.api_key_var.get().strip()
        garmin_email = self.garmin_email_var.get().strip()
        garmin_password = self.garmin_password_var.get().strip()
        
        # Validation
        errors = []
        if not api_key:
            errors.append("xAI API key is required")
        if not garmin_email:
            errors.append("Garmin email is required")
        if not garmin_password:
            errors.append("Garmin password is required")
            
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors), parent=self)
            return
            
        self.result = {
            'xai_api_key': api_key,
            'garmin_email': garmin_email,
            'garmin_password': garmin_password
        }
        self.destroy()
        
    def cancel(self):
        """Cancel and close"""
        self.result = None
        self.destroy()


class GarminChatApp:
    """Main application class for Garmin Chat desktop app"""
    
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.root.title("Garmin Chat")
        self.root.geometry("900x800")
        
        # Set minimum window size
        self.root.minsize(700, 650)
        
        # Configuration file path
        self.config_dir = Path.home() / ".garmin_chat"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        # Application state
        self.garmin_handler = None
        self.xai_client = None
        self.authenticated = False
        self.mfa_required = False
        self.xai_api_key = None
        self.garmin_email = None
        self.garmin_password = None
        
        # Load configuration
        self.load_config()
        
        # Configure style
        self.setup_styles()
        
        # Create UI
        self.create_widgets()
        
        # Center window on screen
        self.center_window()
        
        # Check if credentials are configured
        if not self.xai_api_key or not self.garmin_email or not self.garmin_password:
            self.root.after(100, self.prompt_for_credentials)
        else:
            # Auto-connect if credentials are configured
            self.root.after(500, self.auto_connect)
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.xai_api_key = config.get('xai_api_key', '')
                    self.garmin_email = config.get('garmin_email', '')
                    self.garmin_password = config.get('garmin_password', '')
                    logger.info("Configuration loaded")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.xai_api_key = None
            self.garmin_email = None
            self.garmin_password = None
            
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'xai_api_key': self.xai_api_key,
                'garmin_email': self.garmin_email,
                'garmin_password': self.garmin_password
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            
    def prompt_for_credentials(self):
        """Prompt user to enter credentials on first run"""
        messagebox.showinfo(
            "Welcome to Garmin Chat",
            "Welcome! Before you can start chatting, you need to configure your credentials.\n\n"
            "You'll need:\n"
            "1. An xAI API key (get from https://console.x.ai/)\n"
            "2. Your Garmin Connect email and password\n\n"
            "Click OK to open the settings dialog.",
            parent=self.root
        )
        self.open_settings()
        
    def auto_connect(self):
        """Automatically connect to Garmin on startup if credentials are configured"""
        self.add_message("System", "Auto-connecting to Garmin Connect...", 'system')
        self.update_status("Connecting to Garmin...", False)
        self.connect_to_garmin()
        
    def setup_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 16, 'bold'),
                       background='#f0f0f0',
                       foreground='#2c3e50')
        style.configure('Status.TLabel',
                       font=('Segoe UI', 9),
                       background='#f0f0f0',
                       foreground='#7f8c8d')
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10),
                       padding=8)
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Create all UI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Chat display gets the extra space
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, 
                               text="🏃‍♂️ Garmin Chat",
                               style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame,
                                  text="Ask questions about your Garmin fitness data",
                                  style='Status.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W)
        
        # Settings button (top right)
        settings_btn = ttk.Button(header_frame,
                                 text="⚙️ Settings",
                                 command=self.open_settings,
                                 width=12)
        settings_btn.grid(row=0, column=1, rowspan=2, padx=(10, 0))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.connect_btn = ttk.Button(control_frame,
                                     text="🔐 Connect to Garmin",
                                     command=self.connect_to_garmin,
                                     style='Primary.TButton')
        self.connect_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(control_frame,
                                     text="🔄 Refresh Data",
                                     command=self.refresh_data,
                                     state=tk.DISABLED)
        self.refresh_btn.grid(row=0, column=1, padx=5)
        
        self.reset_btn = ttk.Button(control_frame,
                                   text="🗑️ Reset Chat",
                                   command=self.reset_chat,
                                   state=tk.DISABLED)
        self.reset_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(control_frame,
                                     text="Not connected",
                                     style='Status.TLabel')
        self.status_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # MFA frame (initially hidden)
        self.mfa_frame = ttk.LabelFrame(main_frame, text="Multi-Factor Authentication", padding="10")
        self.mfa_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.mfa_frame.grid_remove()  # Hide initially
        self.mfa_frame.columnconfigure(2, weight=1)
        
        ttk.Label(self.mfa_frame, text="Enter 6-digit code:", font=('Segoe UI', 10)).grid(row=0, column=0, padx=(5, 10), pady=5)
        
        self.mfa_entry = ttk.Entry(self.mfa_frame, width=20, font=('Segoe UI', 11))
        self.mfa_entry.grid(row=0, column=1, padx=(0, 10), pady=5)
        self.mfa_entry.bind('<Return>', lambda e: self.submit_mfa())
        
        self.mfa_btn = ttk.Button(self.mfa_frame,
                                 text="🔑 Submit MFA Code",
                                 command=self.submit_mfa,
                                 style='Primary.TButton')
        self.mfa_btn.grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # Chat display frame
        chat_frame = ttk.Frame(main_frame)
        chat_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat history (scrolled text)
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                      wrap=tk.WORD,
                                                      font=('Segoe UI', 10),
                                                      bg='#ffffff',
                                                      relief=tk.FLAT,
                                                      borderwidth=1,
                                                      padx=10,
                                                      pady=10)
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure text tags for styling
        self.chat_display.tag_configure('user', foreground='#2980b9', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_configure('assistant', foreground='#27ae60', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_configure('system', foreground='#e74c3c', font=('Segoe UI', 9, 'italic'))
        self.chat_display.tag_configure('timestamp', foreground='#95a5a6', font=('Segoe UI', 8))
        self.chat_display.tag_configure('bold', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_configure('header', font=('Segoe UI', 11, 'bold'), foreground='#34495e')
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        input_frame.columnconfigure(0, weight=1)
        
        # Message input (multi-line Text widget)
        input_container = ttk.Frame(input_frame)
        input_container.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        input_container.columnconfigure(0, weight=1)
        
        self.message_entry = tk.Text(input_container, 
                                     height=3,
                                     width=1,
                                     font=('Segoe UI', 10),
                                     wrap=tk.WORD,
                                     relief=tk.FLAT,
                                     borderwidth=1,
                                     bg='white')
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=1, pady=1)
        
        # Scrollbar for input
        input_scrollbar = ttk.Scrollbar(input_container, orient=tk.VERTICAL, command=self.message_entry.yview)
        input_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.message_entry.config(yscrollcommand=input_scrollbar.set)
        
        # Bind Ctrl+Enter to send (Enter alone creates new line)
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
        self.message_entry.bind('<Control-Key-Return>', lambda e: self.send_message())
        self.message_entry.config(state=tk.DISABLED)
        
        self.send_btn = ttk.Button(input_frame,
                                   text="Send\n(Ctrl+Enter)",
                                   command=self.send_message,
                                   state=tk.DISABLED,
                                   style='Primary.TButton',
                                   width=12)
        self.send_btn.grid(row=0, column=1)
        
        # Example questions frame
        examples_frame = ttk.LabelFrame(main_frame, text="Example Questions", padding="15")
        examples_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        examples_frame.columnconfigure(0, weight=1)
        examples_frame.columnconfigure(1, weight=1)
        
        examples = [
            "How many steps did I take today?",
            "What was my last workout?",
            "How did I sleep last night?",
            "Show me my recent activities",
        ]
        
        for i, example in enumerate(examples):
            btn = ttk.Button(examples_frame,
                           text=example,
                           command=lambda q=example: self.use_example(q))
            btn.grid(row=i//2, column=i%2, padx=8, pady=6, sticky=(tk.W, tk.E))
        
    def add_message(self, sender, message, tag='user'):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Add sender
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        
        # Parse and add message with markdown formatting
        if tag == 'assistant':
            self._insert_markdown(message)
        else:
            self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def _insert_markdown(self, text):
        """Insert text with basic markdown formatting (headers, bold, bullets)"""
        import re
        
        lines = text.split('\n')
        
        for line in lines:
            # Handle headers (#### or ### or ## or #)
            if line.startswith('#### '):
                header_text = line[5:]
                self._insert_inline_formatting(header_text)
                self.chat_display.insert(tk.END, '\n', 'header')
            elif line.startswith('### '):
                header_text = line[4:]
                self._insert_inline_formatting(header_text)
                self.chat_display.insert(tk.END, '\n', 'header')
            elif line.startswith('## '):
                header_text = line[3:]
                self._insert_inline_formatting(header_text)
                self.chat_display.insert(tk.END, '\n', 'header')
            elif line.startswith('# '):
                header_text = line[2:]
                self._insert_inline_formatting(header_text)
                self.chat_display.insert(tk.END, '\n', 'header')
            # Handle bullets (- item or * item)
            elif line.strip().startswith(('- ', '* ')):
                bullet_text = '  • ' + line.strip()[2:]
                self._insert_inline_formatting(bullet_text)
                self.chat_display.insert(tk.END, '\n')
            # Handle numbered lists (1. item)
            elif re.match(r'^\d+\.\s', line.strip()):
                self._insert_inline_formatting(line)
                self.chat_display.insert(tk.END, '\n')
            # Regular line with possible inline formatting
            else:
                self._insert_inline_formatting(line)
                self.chat_display.insert(tk.END, '\n')
        
        self.chat_display.insert(tk.END, "\n")
    
    def _insert_inline_formatting(self, text):
        """Insert text with inline bold formatting (**text**)"""
        import re
        
        # Split by bold markers **text**
        parts = re.split(r'(\*\*.*?\*\*)', text)
        
        for part in parts:
            if part.startswith('**') and part.endswith('**') and len(part) > 4:
                # Bold text
                bold_text = part[2:-2]
                self.chat_display.insert(tk.END, bold_text, 'bold')
            else:
                # Regular text
                self.chat_display.insert(tk.END, part)
        
    def update_status(self, message, is_error=False):
        """Update the status label"""
        self.status_label.config(text=message)
        if is_error:
            self.status_label.config(foreground='#e74c3c')
        else:
            self.status_label.config(foreground='#27ae60')
            
    def open_settings(self):
        """Open settings dialog"""
        current_config = {
            'xai_api_key': self.xai_api_key or '',
            'garmin_email': self.garmin_email or '',
            'garmin_password': self.garmin_password or ''
        }
        
        dialog = SettingsDialog(self.root, current_config)
        self.root.wait_window(dialog)
        
        if dialog.result:
            self.xai_api_key = dialog.result['xai_api_key']
            self.garmin_email = dialog.result['garmin_email']
            self.garmin_password = dialog.result['garmin_password']
            self.save_config()
            
            # If already authenticated, reinitialize clients
            if self.xai_client:
                try:
                    self.xai_client = XAIClient(self.xai_api_key)
                    self.add_message("System", "Settings updated successfully!", 'system')
                except Exception as e:
                    self.add_message("System", f"Error updating settings: {e}", 'system')
                    
    def connect_to_garmin(self):
        """Initialize and authenticate with Garmin Connect"""
        # Check if all credentials are configured
        if not self.xai_api_key or not self.garmin_email or not self.garmin_password:
            messagebox.showerror(
                "Configuration Required",
                "Please configure all your credentials in Settings before connecting to Garmin.\n\n"
                "You need:\n"
                "- xAI API key\n"
                "- Garmin Connect email\n"
                "- Garmin Connect password",
                parent=self.root
            )
            self.open_settings()
            return
            
        self.connect_btn.config(state=tk.DISABLED)
        self.update_status("Connecting to Garmin...", False)
        
        # Run in thread to prevent UI freezing
        thread = threading.Thread(target=self._authenticate_garmin)
        thread.daemon = True
        thread.start()
        
    def _authenticate_garmin(self):
        """Authenticate with Garmin (runs in thread)"""
        try:
            # Initialize xAI client with stored API key
            self.xai_client = XAIClient(self.xai_api_key)
            
            # Initialize Garmin handler with stored credentials
            self.garmin_handler = GarminDataHandler(self.garmin_email, self.garmin_password)
            result = self.garmin_handler.authenticate()
            
            if result.get('success'):
                self.authenticated = True
                self.mfa_required = False
                self.root.after(0, lambda: self._on_auth_success())
            elif result.get('mfa_required'):
                self.mfa_required = True
                self.authenticated = False
                self.root.after(0, lambda: self._show_mfa_input())
            else:
                error_msg = result.get('error', 'Unknown error')
                self.root.after(0, lambda: self.update_status(f"❌ {error_msg}", True))
                self.root.after(0, lambda: self.connect_btn.config(state=tk.NORMAL))
                
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"❌ Error: {str(e)}", True))
            self.root.after(0, lambda: self.connect_btn.config(state=tk.NORMAL))
            
    def _show_mfa_input(self):
        """Show MFA input frame"""
        self.mfa_frame.grid()
        self.update_status("🔐 MFA Required: Enter your 6-digit code", False)
        self.mfa_entry.focus()
        
    def submit_mfa(self):
        """Submit MFA code"""
        mfa_code = self.mfa_entry.get().strip()
        
        if not mfa_code or len(mfa_code) != 6:
            self.update_status("❌ Please enter a valid 6-digit MFA code", True)
            return
            
        self.mfa_btn.config(state=tk.DISABLED)
        self.update_status("Submitting MFA code...", False)
        
        # Run in thread
        thread = threading.Thread(target=self._submit_mfa_code, args=(mfa_code,))
        thread.daemon = True
        thread.start()
        
    def _submit_mfa_code(self, mfa_code):
        """Submit MFA code (runs in thread)"""
        try:
            result = self.garmin_handler.submit_mfa(mfa_code)
            
            if result.get('success'):
                self.authenticated = True
                self.mfa_required = False
                self.root.after(0, lambda: self._on_auth_success())
                self.root.after(0, lambda: self.mfa_frame.grid_remove())
            else:
                error_msg = result.get('error', 'Unknown error')
                self.root.after(0, lambda: self.update_status(f"❌ {error_msg}", True))
                self.root.after(0, lambda: self.mfa_btn.config(state=tk.NORMAL))
                
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"❌ Error: {str(e)}", True))
            self.root.after(0, lambda: self.mfa_btn.config(state=tk.NORMAL))
            
    def _on_auth_success(self):
        """Handle successful authentication"""
        self.update_status("✅ Connected to Garmin Connect!", False)
        self.message_entry.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.refresh_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)
        self.connect_btn.config(state=tk.DISABLED)
        self.message_entry.focus()
        
        self.add_message("System",
                        "Connected! You can now ask questions about your Garmin data.",
                        'system')
        
    def send_message(self):
        """Send a message to the chatbot"""
        if not self.authenticated:
            self.update_status("❌ Please connect to Garmin first", True)
            return
            
        # Get message from Text widget
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
            
        # Add user message to display
        self.add_message("You", message, 'user')
        
        # Clear input
        self.message_entry.delete("1.0", tk.END)
        
        # Disable input while processing
        self.message_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        
        # Process in thread
        thread = threading.Thread(target=self._process_message, args=(message,))
        thread.daemon = True
        thread.start()
        
        # Return 'break' to prevent default behavior when called from key binding
        return 'break'
        
    def _process_message(self, message):
        """Process the message and get AI response (runs in thread)"""
        try:
            # Determine what data to fetch
            query_lower = message.lower()
            
            if any(word in query_lower for word in ["activity", "activities", "workout", "run", "walk", "bike", "exercise"]):
                garmin_context = self.garmin_handler.format_data_for_context("activities")
            elif any(word in query_lower for word in ["sleep", "rest", "bed"]):
                garmin_context = self.garmin_handler.format_data_for_context("sleep")
            elif any(word in query_lower for word in ["step", "walk", "distance", "calorie"]):
                garmin_context = self.garmin_handler.format_data_for_context("summary")
            else:
                garmin_context = self.garmin_handler.format_data_for_context("all")
            
            # Get AI response
            response = self.xai_client.chat(message, garmin_context)
            
            # Add response to display
            self.root.after(0, lambda: self.add_message("Garmin Chat", response, 'assistant'))
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.root.after(0, lambda: self.add_message("System", error_msg, 'system'))
            
        finally:
            # Re-enable input
            self.root.after(0, lambda: self.message_entry.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.message_entry.focus())
            
    def use_example(self, question):
        """Use an example question"""
        if not self.authenticated:
            self.update_status("❌ Please connect to Garmin first", True)
            return
            
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", question)
        self.send_message()
        
    def refresh_data(self):
        """Refresh Garmin data"""
        self.refresh_btn.config(state=tk.DISABLED)
        self.update_status("Refreshing data...", False)
        
        thread = threading.Thread(target=self._refresh_data)
        thread.daemon = True
        thread.start()
        
    def _refresh_data(self):
        """Refresh data (runs in thread)"""
        try:
            result = self.garmin_handler.authenticate()
            if result.get('success'):
                self.root.after(0, lambda: self.update_status("✅ Data refreshed!", False))
                self.root.after(0, lambda: self.add_message("System", "Data refreshed successfully!", 'system'))
            elif result.get('mfa_required'):
                # MFA is required for refresh
                self.mfa_required = True
                self.authenticated = False
                self.root.after(0, lambda: self._show_mfa_input())
                self.root.after(0, lambda: self.update_status("🔐 MFA Required: Enter your 6-digit code", False))
            else:
                error_msg = result.get('error', 'Unknown error')
                self.root.after(0, lambda: self.update_status(f"❌ {error_msg}", True))
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"❌ Error: {str(e)}", True))
        finally:
            self.root.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
            
    def reset_chat(self):
        """Reset the conversation"""
        if self.xai_client:
            self.xai_client.reset_conversation()
            
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        self.add_message("System", "Conversation reset!", 'system')
        self.update_status("✅ Chat reset", False)


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🏃‍♂️ Garmin Chat - Desktop Application")
    print("="*60)
    print("\nStarting application...")
    print("\nAll credentials are configured in the app settings.")
    print("No .env file needed!")
    print("="*60 + "\n")
    
    root = tk.Tk()
    app = GarminChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()