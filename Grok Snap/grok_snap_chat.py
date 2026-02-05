import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                              QComboBox, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect
from PyQt6.QtGui import QFont, QTextCursor
import ctypes
from ctypes import wintypes
import requests

# Windows API constants and structures
user32 = ctypes.windll.user32
GWL_STYLE = -16
WS_VISIBLE = 0x10000000
WS_MINIMIZE = 0x20000000

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

def get_open_windows():
    """Get list of all visible windows with titles"""
    windows = []
    
    def enum_windows_callback(hwnd, lParam):
        """Callback for EnumWindows to collect visible windows"""
        if user32.IsWindowVisible(hwnd):
            # Get window style to filter out tool windows and other non-standard windows
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            
            # Skip minimized windows
            if style & WS_MINIMIZE:
                return True
                
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                title = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title, length + 1)
                if title.value:
                    # Get window rect to verify it has reasonable dimensions
                    rect = RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    width = rect.right - rect.left
                    height = rect.bottom - rect.top
                    
                    # Only include windows with reasonable dimensions
                    if width > 100 and height > 100:
                        windows.append((hwnd, title.value))
        return True
    
    # Define callback type and call EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
    return windows

def get_window_rect(hwnd):
    """Get window position and size"""
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect

class GrokAPIThread(QThread):
    """Thread for handling Grok API calls without blocking UI"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key, messages, image_data=None):
        super().__init__()
        self.api_key = api_key
        self.messages = messages
        self.image_data = image_data
        
    def run(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # If image data is provided, format message with image
            if self.image_data:
                # Get the last user message
                last_message = self.messages[-1]
                
                # Format message with image for vision model
                vision_message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{self.image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": last_message["content"]
                        }
                    ]
                }
                
                # Replace last message with vision-formatted message
                messages = self.messages[:-1] + [vision_message]
            else:
                messages = self.messages
            
            data = {
                "model": "grok-2-vision-1212",
                "messages": messages,
                "stream": False,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']['content']
                self.response_received.emit(message)
            else:
                self.error_occurred.emit(f"API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")

class GrokSnapChat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.target_hwnd = None
        self.conversation_history = []
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.snap_position = "right"  # Default snap position
        self.current_opacity = 1.0  # Default full opacity
        
        # Timer for detecting window underneath
        self.detect_timer = QTimer()
        self.detect_timer.timeout.connect(self.detect_window_underneath)
        self.detect_timer.start(500)  # Check every 500ms
        
        # Load settings including API key
        self.load_settings()
        
        self.init_ui()
        self.load_windows()
    
    def load_settings(self):
        """Load settings from config file"""
        import json
        from pathlib import Path
        
        # Settings file location
        settings_dir = Path.home() / ".grok_snap_chat"
        settings_file = settings_dir / "settings.json"
        
        # Default settings
        defaults = {
            "api_key": os.environ.get('XAI_API_KEY', ''),
            "snap_position": "right",
            "opacity": 1.0
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.api_key = settings.get("api_key", defaults["api_key"])
                    self.snap_position = settings.get("snap_position", defaults["snap_position"])
                    self.current_opacity = settings.get("opacity", defaults["opacity"])
            else:
                # Use defaults
                self.api_key = defaults["api_key"]
                self.snap_position = defaults["snap_position"]
                self.current_opacity = defaults["opacity"]
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Use defaults on error
            self.api_key = defaults["api_key"]
            self.snap_position = defaults["snap_position"]
            self.current_opacity = defaults["opacity"]
    
    def save_settings(self):
        """Save settings to config file"""
        import json
        from pathlib import Path
        
        # Settings file location
        settings_dir = Path.home() / ".grok_snap_chat"
        settings_file = settings_dir / "settings.json"
        
        try:
            # Create directory if it doesn't exist
            settings_dir.mkdir(exist_ok=True)
            
            settings = {
                "api_key": self.api_key,
                "snap_position": self.snap_position,
                "opacity": self.current_opacity
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def init_ui(self):
        self.setWindowTitle("Grok Snap Chat")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(400)
        self.setMinimumHeight(600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Custom title bar
        title_bar = QFrame()
        title_bar.setStyleSheet("background-color: #1a1a2e; padding: 10px;")
        title_bar.setFixedHeight(50)
        title_layout = QHBoxLayout(title_bar)
        
        title_label = QLabel("🤖 Grok Snap Chat")
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(30, 30)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0f3460;
                border-radius: 15px;
            }
        """)
        settings_btn.clicked.connect(self.show_settings)
        title_layout.addWidget(settings_btn)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                border-radius: 15px;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        layout.addWidget(title_bar)
        
        # Window selector
        selector_frame = QFrame()
        selector_frame.setStyleSheet("background-color: #16213e; padding: 10px;")
        selector_layout = QVBoxLayout(selector_frame)
        
        selector_label = QLabel("Select Window to Snap To:")
        selector_label.setStyleSheet("color: white; font-size: 11px;")
        selector_layout.addWidget(selector_label)
        
        # Combo box and refresh button container
        combo_container = QHBoxLayout()
        
        self.window_combo = QComboBox()
        self.window_combo.setStyleSheet("""
            QComboBox {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:hover {
                background-color: #1a4d7a;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        combo_container.addWidget(self.window_combo)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1a4d7a;
            }
        """)
        refresh_btn.setToolTip("Refresh window list")
        refresh_btn.clicked.connect(self.load_windows)
        combo_container.addWidget(refresh_btn)
        
        selector_layout.addLayout(combo_container)
        
        # Button container for snap/unsnap
        button_container = QHBoxLayout()
        
        snap_btn = QPushButton("📌 Snap to Window")
        snap_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5577;
            }
        """)
        snap_btn.clicked.connect(self.snap_to_window)
        button_container.addWidget(snap_btn)
        
        unsnap_btn = QPushButton("🔓 Unsnap")
        unsnap_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a4d7a;
            }
        """)
        unsnap_btn.clicked.connect(self.unsnap_from_window)
        button_container.addWidget(unsnap_btn)
        
        selector_layout.addLayout(button_container)
        
        # Analyze window button
        analyze_btn = QPushButton("👁️ Analyze Window Content")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_window)
        selector_layout.addWidget(analyze_btn)
        
        layout.addWidget(selector_frame)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #16213e; padding: 10px;")
        input_layout = QVBoxLayout(input_frame)
        
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type your message... (Ctrl+Enter to send)")
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 3px;
            }
        """)
        self.input_field.setMaximumHeight(100)
        self.input_field.setMinimumHeight(60)
        input_layout.addWidget(self.input_field)
        
        # Button container for send and clear
        button_container = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Clear Chat")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a4d7a;
            }
        """)
        clear_btn.clicked.connect(self.clear_chat)
        button_container.addWidget(clear_btn)
        
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5577;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        button_container.addWidget(send_btn)
        
        input_layout.addLayout(button_container)
        
        layout.addWidget(input_frame)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            background-color: #1a1a2e;
            color: #888;
            padding: 5px 10px;
            font-size: 10px;
        """)
        layout.addWidget(self.status_label)
        
        # Check for API key
        if not self.api_key:
            self.append_message("System", "⚠️ No xAI API key found. Click the ⚙️ Settings button to add your API key.", "#e94560")
        
    def load_windows(self):
        """Load available windows into combo box"""
        windows = get_open_windows()
        self.window_combo.clear()
        
        # Filter out this application's window
        my_title = self.windowTitle()
        for hwnd, title in windows:
            if title != my_title and len(title.strip()) > 0:
                self.window_combo.addItem(title, hwnd)
    
    def detect_window_underneath(self):
        """Detect which window the chat pane is hovering over and update dropdown"""
        # Only detect if not currently snapped
        if self.target_hwnd:
            return
        
        try:
            # Get the position of this window
            my_rect = self.frameGeometry()
            
            # Check a point just to the left/right/top/bottom depending on intended snap position
            # This ensures we're checking the window we'd snap TO, not ourselves
            check_x = my_rect.x() - 10  # Check 10 pixels to the left
            check_y = my_rect.y() + my_rect.height() // 2  # Middle height
            
            # Use ctypes to call WindowFromPoint
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            
            point = POINT(check_x, check_y)
            hwnd = user32.WindowFromPoint(point)
            
            if not hwnd:
                return
            
            # Get the actual window (not a child control)
            hwnd = user32.GetAncestor(hwnd, 2)  # GA_ROOT = 2
            
            if not hwnd:
                return
            
            # Skip if it's this window
            my_hwnd = int(self.winId())
            if hwnd == my_hwnd:
                return
            
            # Get window title
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                title = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title, length + 1)
                
                if title.value and title.value != self.windowTitle():
                    # Find this window in the combo box and select it
                    for i in range(self.window_combo.count()):
                        if self.window_combo.itemData(i) == hwnd:
                            if self.window_combo.currentIndex() != i:
                                self.window_combo.setCurrentIndex(i)
                            return
                    
                    # Window not in list, refresh the list
                    self.load_windows()
                    # Try again to find it
                    for i in range(self.window_combo.count()):
                        if self.window_combo.itemData(i) == hwnd:
                            self.window_combo.setCurrentIndex(i)
                            return
        except Exception as e:
            # For debugging - you can comment this out later
            # print(f"Detection error: {e}")
            pass
                
    def snap_to_window(self):
        """Snap chat pane to selected window"""
        if self.window_combo.currentIndex() < 0:
            return
            
        self.target_hwnd = self.window_combo.currentData()
        
        # Verify we got a valid window handle
        if not self.target_hwnd or not user32.IsWindow(self.target_hwnd):
            self.status_label.setText("⚠️ Invalid window selected")
            return
            
        self.update_position()
        self.position_timer.start(100)  # Update position every 100ms
        self.status_label.setText(f"📌 Snapped to: {self.window_combo.currentText()}")
        
    def unsnap_from_window(self):
        """Unsnap from current window and allow free movement"""
        if self.target_hwnd:
            self.position_timer.stop()
            self.target_hwnd = None
            self.status_label.setText("🔓 Unsnapped - Free floating")
            # Refresh window list when unsnapping
            self.load_windows()
        else:
            self.status_label.setText("⚠️ Not currently snapped to any window")
        
    def update_position(self):
        """Update position to stay snapped to target window"""
        if not self.target_hwnd:
            return
            
        # Check if window still exists
        if not user32.IsWindow(self.target_hwnd):
            self.position_timer.stop()
            self.status_label.setText("⚠️ Target window closed")
            self.target_hwnd = None
            return
            
        try:
            rect = get_window_rect(self.target_hwnd)
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            
            # Calculate position based on snap_position setting
            if self.snap_position == "right":
                x = rect.right
                y = rect.top
                snap_height = height
                snap_width = self.width()
            elif self.snap_position == "left":
                x = rect.left - self.width()
                y = rect.top
                snap_height = height
                snap_width = self.width()
            elif self.snap_position == "top":
                x = rect.left
                y = rect.top - 300  # Fixed height for top/bottom
                snap_height = 300
                snap_width = width
            elif self.snap_position == "bottom":
                x = rect.left
                y = rect.bottom
                snap_height = 300
                snap_width = width
            
            # Ensure minimum height for left/right
            if self.snap_position in ["left", "right"] and snap_height < 200:
                snap_height = 600
            
            self.setGeometry(x, y, snap_width, snap_height)
        except Exception as e:
            self.status_label.setText(f"⚠️ Error: {str(e)}")
            self.position_timer.stop()
            self.target_hwnd = None
        
    def append_message(self, sender, message, color="#00ff88"):
        """Append message to chat display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Add proper spacing and line breaks for readability
        html_message = message.replace('\n', '<br>')
        cursor.insertHtml(f'''
            <div style="margin: 10px 0; padding: 10px; background-color: rgba(255,255,255,0.05); border-radius: 5px; border-left: 3px solid {color};">
                <div style="margin-bottom: 8px;">
                    <span style="color: {color}; font-size: 13px; font-weight: bold;">{sender}</span>
                </div>
                <div style="color: #e0e0e0; font-size: 12px; line-height: 1.6;">
                    {html_message}
                </div>
            </div>
            <br>
        ''')
        
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()
        
    def send_message(self):
        """Send message to Grok API"""
        message = self.input_field.toPlainText().strip()
        if not message:
            return
            
        if not self.api_key:
            self.append_message("System", "Please set your xAI API key in Settings (⚙️ button)", "#e74c3c")
            return
            
        self.input_field.clear()
        self.append_message("You", message, "#00d4ff")
        self.status_label.setText("⏳ Thinking...")
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Start API thread
        self.api_thread = GrokAPIThread(self.api_key, self.conversation_history)
        self.api_thread.response_received.connect(self.handle_response)
        self.api_thread.error_occurred.connect(self.handle_error)
        self.api_thread.start()
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        from PyQt6.QtCore import Qt
        # Ctrl+Enter to send message
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.send_message()
        else:
            super().keyPressEvent(event)
        
    def handle_response(self, response):
        """Handle successful API response"""
        self.conversation_history.append({"role": "assistant", "content": response})
        self.append_message("Grok", response, "#00ff88")
        self.status_label.setText("✓ Ready")
        
    def handle_error(self, error):
        """Handle API error"""
        self.append_message("System", error, "#e74c3c")
        self.status_label.setText("✗ Error")
        
    def clear_chat(self):
        """Clear the chat history and display"""
        self.chat_display.clear()
        self.conversation_history = []
        self.status_label.setText("✓ Chat cleared - Fresh start!")
    
    def show_settings(self):
        """Show settings dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton, QFileDialog, QMessageBox, QLineEdit
        from PyQt6.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setModal(True)
        dialog.setFixedSize(450, 550)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QComboBox, QLineEdit {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit {
                padding: 8px;
            }
            QSlider::groove:horizontal {
                background: #0f3460;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #e94560;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5577;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # API Key Setting
        api_label = QLabel("xAI API Key:")
        api_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        layout.addWidget(api_label)
        
        api_input = QLineEdit()
        api_input.setPlaceholderText("Enter your xAI API key...")
        api_input.setText(self.api_key)
        api_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(api_input)
        
        # Show/Hide API key toggle
        show_api_btn = QPushButton("👁 Show Key")
        show_api_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1a4d7a;
            }
        """)
        
        def toggle_api_visibility():
            if api_input.echoMode() == QLineEdit.EchoMode.Password:
                api_input.setEchoMode(QLineEdit.EchoMode.Normal)
                show_api_btn.setText("🔒 Hide Key")
            else:
                api_input.setEchoMode(QLineEdit.EchoMode.Password)
                show_api_btn.setText("👁 Show Key")
        
        show_api_btn.clicked.connect(toggle_api_visibility)
        layout.addWidget(show_api_btn)
        
        # Snap Position Setting
        snap_label = QLabel("Snap Position:")
        snap_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white; margin-top: 10px;")
        layout.addWidget(snap_label)
        
        snap_combo = QComboBox()
        snap_combo.addItems(["Right Edge", "Left Edge", "Top Edge", "Bottom Edge"])
        snap_combo.setCurrentText({
            "right": "Right Edge",
            "left": "Left Edge", 
            "top": "Top Edge",
            "bottom": "Bottom Edge"
        }[self.snap_position])
        layout.addWidget(snap_combo)
        
        # Opacity Setting
        opacity_label = QLabel(f"Window Opacity: {int(self.current_opacity * 100)}%")
        opacity_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white; margin-top: 10px;")
        layout.addWidget(opacity_label)
        
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setMinimum(30)
        opacity_slider.setMaximum(100)
        opacity_slider.setValue(int(self.current_opacity * 100))
        opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        opacity_slider.setTickInterval(10)
        
        def update_opacity_label(value):
            opacity_label.setText(f"Window Opacity: {value}%")
            self.setWindowOpacity(value / 100)
            self.current_opacity = value / 100
            
        opacity_slider.valueChanged.connect(update_opacity_label)
        layout.addWidget(opacity_slider)
        
        # Save Conversation Setting
        layout.addWidget(QLabel("Conversation History:", styleSheet="font-size: 14px; font-weight: bold; color: white; margin-top: 10px;"))
        
        save_container = QVBoxLayout()
        save_container.setSpacing(10)
        
        # Save conversation button
        save_btn = QPushButton("💾 Save Current Conversation")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5577;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_conversation_history(dialog))
        save_container.addWidget(save_btn)
        
        # Load conversation button
        load_btn = QPushButton("📂 Load Conversation")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
        """)
        load_btn.clicked.connect(lambda: self.load_conversation_history(dialog))
        save_container.addWidget(load_btn)
        
        # Open folder button
        folder_btn = QPushButton("📁 Open Conversations Folder")
        folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a4d7a;
            }
        """)
        folder_btn.clicked.connect(self.open_conversations_folder)
        save_container.addWidget(folder_btn)
        
        layout.addLayout(save_container)
        
        # Save and Close buttons
        layout.addStretch()
        button_layout = QHBoxLayout()
        
        save_settings_btn = QPushButton("💾 Save Settings")
        save_settings_btn.clicked.connect(lambda: self.apply_settings(api_input.text(), snap_combo.currentText(), dialog))
        button_layout.addWidget(save_settings_btn)
        
        close_btn = QPushButton("Cancel")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a4d7a;
            }
        """)
        close_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def apply_settings(self, api_key, snap_position_text, dialog):
        """Apply and save settings from dialog"""
        # Update API key
        if api_key.strip():
            self.api_key = api_key.strip()
        
        # Update snap position
        position_map = {
            "Right Edge": "right",
            "Left Edge": "left",
            "Top Edge": "top",
            "Bottom Edge": "bottom"
        }
        self.snap_position = position_map[snap_position_text]
        
        # Save settings to file
        self.save_settings()
        
        # Update position if currently snapped
        if self.target_hwnd:
            self.update_position()
        
        # Show confirmation
        self.status_label.setText("✓ Settings saved")
        
        dialog.accept()
    
    def save_conversation_history(self, parent_dialog=None):
        """Save conversation history to a JSON file"""
        if not self.conversation_history:
            self.append_message("System", "⚠️ No conversation history to save", "#e74c3c")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        import json
        from datetime import datetime
        from pathlib import Path
        
        # Default conversations folder
        conversations_dir = Path.home() / "Documents" / "Grok Snap Chat Conversations"
        conversations_dir.mkdir(parents=True, exist_ok=True)
        
        default_filename = conversations_dir / f"grok_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filename, _ = QFileDialog.getSaveFileName(
            parent_dialog or self,
            "Save Conversation",
            str(default_filename),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                # Get all chat display text for reference
                chat_text = self.chat_display.toPlainText()
                
                save_data = {
                    "timestamp": datetime.now().isoformat(),
                    "conversation_history": self.conversation_history,
                    "chat_display": chat_text,
                    "message_count": len(self.conversation_history)
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                
                self.append_message("System", f"✓ Conversation saved to {Path(filename).name}", "#00ff88")
                self.status_label.setText("✓ Conversation saved")
            except Exception as e:
                self.append_message("System", f"⚠️ Error saving conversation: {str(e)}", "#e74c3c")
                self.status_label.setText("✗ Save failed")
    
    def load_conversation_history(self, parent_dialog=None):
        """Load conversation history from a JSON file"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json
        from pathlib import Path
        
        # Start in conversations folder
        conversations_dir = Path.home() / "Documents" / "Grok Snap Chat Conversations"
        start_dir = str(conversations_dir) if conversations_dir.exists() else ""
        
        filename, _ = QFileDialog.getOpenFileName(
            parent_dialog or self,
            "Load Conversation",
            start_dir,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                # Confirm overwrite
                if self.conversation_history:
                    reply = QMessageBox.question(
                        parent_dialog or self,
                        "Load Conversation",
                        "This will clear your current conversation. Continue?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                
                # Load the conversation
                self.conversation_history = save_data.get("conversation_history", [])
                
                # Clear and rebuild chat display
                self.chat_display.clear()
                
                # Rebuild display from history
                for msg in self.conversation_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    
                    if role == "user":
                        self.append_message("You", content, "#00d4ff")
                    elif role == "assistant":
                        self.append_message("Grok", content, "#00ff88")
                
                message_count = save_data.get("message_count", len(self.conversation_history))
                timestamp = save_data.get("timestamp", "unknown")
                
                self.append_message("System", f"✓ Loaded conversation from {timestamp} ({message_count} messages)", "#00ff88")
                self.status_label.setText("✓ Conversation loaded")
                
            except Exception as e:
                self.append_message("System", f"⚠️ Error loading conversation: {str(e)}", "#e74c3c")
                self.status_label.setText("✗ Load failed")
    
    def open_conversations_folder(self):
        """Open the conversations folder in Windows Explorer"""
        from pathlib import Path
        import subprocess
        
        conversations_dir = Path.home() / "Documents" / "Grok Snap Chat Conversations"
        
        try:
            # Create folder if it doesn't exist
            conversations_dir.mkdir(parents=True, exist_ok=True)
            
            # Open in Windows Explorer
            subprocess.run(['explorer', str(conversations_dir)])
            
            self.status_label.setText("✓ Opened conversations folder")
        except Exception as e:
            self.append_message("System", f"⚠️ Error opening folder: {str(e)}", "#e74c3c")
            self.status_label.setText("✗ Could not open folder")
        
    def analyze_window(self):
        """Capture and analyze the content of the snapped window"""
        if not self.target_hwnd:
            self.append_message("System", "⚠️ Please snap to a window first before analyzing", "#e74c3c")
            return
            
        if not self.api_key:
            self.append_message("System", "Please set your xAI API key in Settings (⚙️ button)", "#e74c3c")
            return
            
        self.status_label.setText("📸 Capturing window...")
        
        try:
            from PIL import ImageGrab
            import io
            import base64
            
            # Get window dimensions
            rect = get_window_rect(self.target_hwnd)
            
            # Get window title
            length = user32.GetWindowTextLengthW(self.target_hwnd)
            title = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(self.target_hwnd, title, length + 1)
            
            # Bring window to front for better capture
            user32.SetForegroundWindow(self.target_hwnd)
            user32.BringWindowToTop(self.target_hwnd)
            
            # Small delay to let window render
            import time
            time.sleep(0.2)
            
            # Capture the window area using PIL
            bbox = (rect.left, rect.top, rect.right, rect.bottom)
            img = ImageGrab.grab(bbox)
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Create analysis request
            analysis_prompt = f"Please analyze and summarize the content visible in this window ('{title.value}'). What information do you see? Provide a clear, concise summary."
            
            self.append_message("You", f"[Analyzing window: {title.value}]", "#00d4ff")
            self.status_label.setText("⏳ Analyzing with Grok Vision...")
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": analysis_prompt})
            
            # Start API thread with image
            self.api_thread = GrokAPIThread(self.api_key, self.conversation_history, img_str)
            self.api_thread.response_received.connect(self.handle_response)
            self.api_thread.error_occurred.connect(self.handle_error)
            self.api_thread.start()
            
        except ImportError as ie:
            self.append_message("System", f"⚠️ Missing required libraries: {str(ie)}. Install with: pip install Pillow", "#e74c3c")
            self.status_label.setText("✗ Missing dependencies")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.append_message("System", f"⚠️ Error capturing window: {str(e)}", "#e74c3c")
            print(f"Capture error details:\n{error_details}")  # For debugging
            self.status_label.setText("✗ Capture failed")
        
    def mousePressEvent(self, event):
        """Allow dragging from title bar area"""
        if event.position().y() < 50:  # Title bar height
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = GrokSnapChat()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
