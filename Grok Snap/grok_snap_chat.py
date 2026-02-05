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
        self.api_key = os.environ.get('XAI_API_KEY', '')
        self.conversation_history = []
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        
        self.init_ui()
        self.load_windows()
        
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
            self.append_message("System", "⚠️ XAI_API_KEY not found in environment variables. Please set it to use Grok API.", "#e74c3c")
        
    def load_windows(self):
        """Load available windows into combo box"""
        windows = get_open_windows()
        self.window_combo.clear()
        
        # Filter out this application's window
        my_title = self.windowTitle()
        for hwnd, title in windows:
            if title != my_title and len(title.strip()) > 0:
                self.window_combo.addItem(title, hwnd)
                
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
            
            # Position chat pane to the right of target window
            x = rect.right
            y = rect.top
            height = rect.bottom - rect.top
            
            # Ensure minimum height
            if height < 200:
                height = 600
            
            # Debug output (you can remove this later)
            # print(f"Target window rect: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}")
            # print(f"Setting chat pane to: x={x}, y={y}, height={height}")
            
            self.setGeometry(x, y, self.width(), height)
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
            self.append_message("System", "Please set XAI_API_KEY environment variable", "#e74c3c")
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
        
    def analyze_window(self):
        """Capture and analyze the content of the snapped window"""
        if not self.target_hwnd:
            self.append_message("System", "⚠️ Please snap to a window first before analyzing", "#e74c3c")
            return
            
        if not self.api_key:
            self.append_message("System", "Please set XAI_API_KEY environment variable", "#e74c3c")
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
