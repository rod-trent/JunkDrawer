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
        self.geometry("600x550")
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
        
        # App Preferences section
        prefs_header = ttk.Label(main_frame,
                                text="Application Preferences",
                                font=('Segoe UI', 11, 'bold'))
        prefs_header.grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=(10, 10))
        
        # Auto-login checkbox
        self.auto_login_var = tk.BooleanVar(value=self.current_config.get('auto_login', True))
        auto_login_check = ttk.Checkbutton(main_frame,
                                          text="Automatically connect to Garmin on startup",
                                          variable=self.auto_login_var)
        auto_login_check.grid(row=11, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=2, pady=(20, 10))
        
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
        ttk.Label(main_frame, text="").grid(row=13, column=0, pady=(0, 5))
        
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
        auto_login = self.auto_login_var.get()
        
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
            'garmin_password': garmin_password,
            'auto_login': auto_login
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
        self.saved_prompts_file = self.config_dir / "saved_prompts.json"
        self.chat_history_dir = self.config_dir / "chat_history"
        self.chat_history_dir.mkdir(exist_ok=True)
        
        # Chat history for current session
        self.current_chat_history = []
        
        # Application state
        self.garmin_handler = None
        self.xai_client = None
        self.authenticated = False
        self.mfa_required = False
        self.xai_api_key = None
        self.garmin_email = None
        self.garmin_password = None
        self.auto_login = True  # Default to auto-login enabled
        
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
        elif self.auto_login:
            # Auto-connect if credentials are configured and auto-login is enabled
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
                    self.auto_login = config.get('auto_login', True)  # Default to enabled
                    logger.info("Configuration loaded")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.xai_api_key = None
            self.garmin_email = None
            self.garmin_password = None
            self.auto_login = True
            
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'xai_api_key': self.xai_api_key,
                'garmin_email': self.garmin_email,
                'garmin_password': self.garmin_password,
                'auto_login': self.auto_login
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
        self.reset_btn.grid(row=0, column=2, padx=5)
        
        self.save_prompts_btn = ttk.Button(control_frame,
                                          text="💾 Prompts",
                                          command=self.open_saved_prompts)
        self.save_prompts_btn.grid(row=0, column=3, padx=5)
        
        self.save_chat_btn = ttk.Button(control_frame,
                                       text="📝 Save Chat",
                                       command=self.save_chat_history,
                                       state=tk.DISABLED)
        self.save_chat_btn.grid(row=0, column=4, padx=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(control_frame,
                                     text="Not connected",
                                     style='Status.TLabel')
        self.status_label.grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=(5, 0))
        
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
        self.chat_display.tag_configure('table', font=('Courier New', 9), foreground='#2c3e50', spacing1=2, spacing3=2)
        
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
        
        # Date range button
        date_range_btn = ttk.Button(examples_frame,
                                   text="📅 Set Date Range (7/14/30 days)",
                                   command=self.show_date_range_dialog,
                                   style='Accent.TButton')
        date_range_btn.grid(row=2, column=0, columnspan=2, padx=8, pady=(10, 6), sticky=(tk.W, tk.E))
        
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
        
        # Save to chat history (but not system messages)
        if tag != 'system':
            self.current_chat_history.append({
                'timestamp': datetime.now().isoformat(),
                'sender': sender,
                'message': message,
                'type': tag
            })
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def _insert_markdown(self, text):
        """Insert text with basic markdown formatting (headers, bold, bullets, tables)"""
        import re
        
        lines = text.split('\n')
        in_table = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect table (lines with | characters)
            if '|' in line and line.strip().startswith('|'):
                # Skip separator lines (lines with only |, -, and +)
                if re.match(r'^[\|\-\+\s]+$', line):
                    i += 1
                    continue
                
                # This is a table line
                if not in_table:
                    in_table = True
                
                # Render table row with monospace font
                self.chat_display.insert(tk.END, line + '\n', 'table')
                i += 1
                continue
            else:
                # Not a table line
                if in_table:
                    in_table = False
                    self.chat_display.insert(tk.END, '\n')  # Extra space after table
            
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
            
            i += 1
        
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
            'garmin_password': self.garmin_password or '',
            'auto_login': self.auto_login
        }
        
        dialog = SettingsDialog(self.root, current_config)
        self.root.wait_window(dialog)
        
        if dialog.result:
            self.xai_api_key = dialog.result['xai_api_key']
            self.garmin_email = dialog.result['garmin_email']
            self.garmin_password = dialog.result['garmin_password']
            self.auto_login = dialog.result['auto_login']
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
        self.save_chat_btn.config(state=tk.NORMAL)
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
        self.current_chat_history = []
        
        self.add_message("System", "Conversation reset!", 'system')
        self.update_status("✅ Chat reset", False)
    
    def open_saved_prompts(self):
        """Open dialog to manage saved prompts"""
        SavedPromptsDialog(self.root, self)
    
    def load_saved_prompts(self):
        """Load saved prompts from file"""
        try:
            if self.saved_prompts_file.exists():
                with open(self.saved_prompts_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading saved prompts: {e}")
            return []
    
    def save_prompt(self, name, prompt):
        """Save a prompt for reuse"""
        try:
            prompts = self.load_saved_prompts()
            prompts.append({'name': name, 'prompt': prompt, 'created': datetime.now().isoformat()})
            with open(self.saved_prompts_file, 'w') as f:
                json.dump(prompts, f, indent=2)
            logger.info(f"Saved prompt: {name}")
        except Exception as e:
            logger.error(f"Error saving prompt: {e}")
    
    def delete_saved_prompt(self, index):
        """Delete a saved prompt"""
        try:
            prompts = self.load_saved_prompts()
            if 0 <= index < len(prompts):
                deleted = prompts.pop(index)
                with open(self.saved_prompts_file, 'w') as f:
                    json.dump(prompts, f, indent=2)
                logger.info(f"Deleted prompt: {deleted['name']}")
        except Exception as e:
            logger.error(f"Error deleting prompt: {e}")
    
    def save_chat_history(self):
        """Save current chat session to file"""
        if not self.current_chat_history:
            messagebox.showinfo("No Chat History", "There's no chat history to save yet!", parent=self.root)
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.chat_history_dir / f"chat_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump({
                    'saved_at': datetime.now().isoformat(),
                    'messages': self.current_chat_history
                }, f, indent=2)
            
            messagebox.showinfo("Chat Saved", f"Chat history saved successfully!\n\nLocation: {filename}", parent=self.root)
            logger.info(f"Saved chat history to: {filename}")
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            messagebox.showerror("Save Error", f"Failed to save chat history: {e}", parent=self.root)
    
    def show_date_range_dialog(self):
        """Show dialog to select date range for data queries"""
        DateRangeDialog(self.root, self)


class SavedPromptsDialog(tk.Toplevel):
    """Dialog for managing saved prompts"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.title("Saved Prompts")
        self.geometry("700x500")
        self.app = app
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="Saved Prompts", font=('Segoe UI', 14, 'bold'))
        title.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Prompts list
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Scrolled listbox
        self.prompts_listbox = tk.Listbox(list_frame, font=('Segoe UI', 10), height=15)
        self.prompts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.prompts_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.prompts_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 10))
        
        ttk.Button(button_frame, text="➕ New Prompt", command=self.new_prompt).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="✏️ Use Selected", command=self.use_prompt).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_prompt).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).grid(row=0, column=3, padx=5)
        
        self.load_prompts()
    
    def load_prompts(self):
        """Load and display saved prompts"""
        self.prompts_listbox.delete(0, tk.END)
        self.prompts = self.app.load_saved_prompts()
        
        for prompt in self.prompts:
            display = f"{prompt['name']} - {prompt['prompt'][:50]}..."
            self.prompts_listbox.insert(tk.END, display)
    
    def new_prompt(self):
        """Create new saved prompt"""
        dialog = tk.Toplevel(self)
        dialog.title("New Prompt")
        dialog.geometry("500x300")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        
        ttk.Label(frame, text="Prompt Name:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame, font=('Segoe UI', 10))
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Prompt Text:", font=('Segoe UI', 10)).grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        prompt_text = tk.Text(frame, font=('Segoe UI', 10), wrap=tk.WORD, height=8)
        prompt_text.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        
        def save():
            name = name_entry.get().strip()
            prompt = prompt_text.get("1.0", tk.END).strip()
            
            if not name or not prompt:
                messagebox.showerror("Validation Error", "Please enter both name and prompt text", parent=dialog)
                return
            
            self.app.save_prompt(name, prompt)
            self.load_prompts()
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame, text="Save", command=save).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).grid(row=0, column=1, padx=5)
    
    def use_prompt(self):
        """Use selected prompt"""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a prompt to use", parent=self)
            return
        
        index = selection[0]
        prompt = self.prompts[index]
        
        # Insert into message entry and close dialog
        self.app.message_entry.delete("1.0", tk.END)
        self.app.message_entry.insert("1.0", prompt['prompt'])
        self.destroy()
    
    def delete_prompt(self):
        """Delete selected prompt"""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a prompt to delete", parent=self)
            return
        
        index = selection[0]
        prompt = self.prompts[index]
        
        if messagebox.askyesno("Confirm Delete", f"Delete prompt '{prompt['name']}'?", parent=self):
            self.app.delete_saved_prompt(index)
            self.load_prompts()


class DateRangeDialog(tk.Toplevel):
    """Dialog for selecting date range for queries"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.title("Query Date Range")
        self.geometry("400x250")
        self.app = app
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="Select Date Range", font=('Segoe UI', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        # Days selection
        ttk.Label(main_frame, text="Query data for the last:", font=('Segoe UI', 10)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.days_var = tk.IntVar(value=7)
        
        ttk.Radiobutton(main_frame, text="7 days", variable=self.days_var, value=7).grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Radiobutton(main_frame, text="14 days", variable=self.days_var, value=14).grid(row=3, column=0, sticky=tk.W, pady=3)
        ttk.Radiobutton(main_frame, text="30 days", variable=self.days_var, value=30).grid(row=4, column=0, sticky=tk.W, pady=3)
        
        # Info label
        info = ttk.Label(main_frame, text="Your next question will query data\nfrom the selected time period.", 
                        font=('Segoe UI', 9), foreground='#7f8c8d')
        info.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(15, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Apply", command=self.apply_range).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).grid(row=0, column=1, padx=5)
    
    def apply_range(self):
        """Apply selected date range"""
        from datetime import timedelta
        days = self.days_var.get()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Add a system message to guide the user
        self.app.add_message("System", 
                           f"Date range set to last {days} days ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}). "
                           f"Your next question will query data from this period.", 
                           'system')
        
        # Store the date range for use in queries
        self.app.date_range_days = days
        
        self.destroy()


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🏃‍♂️ Garmin Chat - Desktop Application")
    print("="*60)
    print("\nStarting application...")
    print("="*60 + "\n")
    
    root = tk.Tk()
    app = GarminChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()