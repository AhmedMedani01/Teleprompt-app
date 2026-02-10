"""
Desktop Teleprompter Application
A frameless, transparent teleprompter with pin and hide functionality
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QPushButton, QMenu
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QFont, QColor, QPalette


class TeleprompterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_file = "script.txt"
        self.is_pinned = False
        self.is_hidden = False
        self.normal_opacity = 0.5
        self.hidden_opacity = 0.05
        
        # For dragging functionality
        self.drag_position = QPoint()
        
        self.init_ui()
        self.load_script()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Window properties
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(self.normal_opacity)
        
        # Set initial size and position
        self.setGeometry(100, 100, 800, 600)
        
        # Main container frame with semi-transparent background
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 128, 128, 0.5);
                border-radius: 10px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self.main_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header (draggable area)
        self.header = self.create_header()
        main_layout.addWidget(self.header)
        
        # Text display area
        self.text_display = self.create_text_display()
        main_layout.addWidget(self.text_display, 1)  # Stretch factor 1
        
        # Set the main frame as central widget
        self.setCentralWidget(self.main_frame)
    
    def create_header(self):
        """Create the draggable header with control buttons"""
        header = QFrame()
        header.setFixedHeight(30)
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(80, 80, 80, 0.7);
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title label
        from PyQt6.QtWidgets import QLabel
        title = QLabel("Teleprompter")
        title.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Pin button
        self.pin_button = QPushButton("📌")
        self.pin_button.setFixedSize(25, 20)
        self.pin_button.setStyleSheet(self.get_button_style())
        self.pin_button.setToolTip("Pin/Unpin window (disable dragging)")
        self.pin_button.clicked.connect(self.toggle_pin)
        header_layout.addWidget(self.pin_button)
        
        # Eye button (hide/show)
        self.eye_button = QPushButton("👁")
        self.eye_button.setFixedSize(25, 20)
        self.eye_button.setStyleSheet(self.get_button_style())
        self.eye_button.setToolTip("Hide/Show content")
        self.eye_button.clicked.connect(self.toggle_visibility)
        header_layout.addWidget(self.eye_button)
        
        # Close button
        close_button = QPushButton("✕")
        close_button.setFixedSize(25, 20)
        close_button.setStyleSheet(self.get_button_style(is_close=True))
        close_button.clicked.connect(self.close)
        header_layout.addWidget(close_button)
        
        return header
    
    def get_button_style(self, is_close=False):
        """Get stylesheet for buttons"""
        hover_color = "rgba(200, 50, 50, 0.8)" if is_close else "rgba(100, 100, 100, 0.8)"
        return f"""
            QPushButton {{
                background-color: rgba(60, 60, 60, 0.6);
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: rgba(40, 40, 40, 0.9);
            }}
        """
    
    def create_text_display(self):
        """Create the text display area"""
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Set large white text
        font = QFont("Arial", 24)
        text_edit.setFont(font)
        
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: white;
                border: none;
                padding: 20px;
            }
        """)
        
        # Enable right-click context menu
        text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        text_edit.customContextMenuRequested.connect(self.show_context_menu)
        
        return text_edit
    
    def load_script(self):
        """Load script from script.txt file"""
        if os.path.exists(self.script_file):
            try:
                with open(self.script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_display.setPlainText(content)
            except Exception as e:
                self.text_display.setPlainText(f"Error loading script: {str(e)}")
        else:
            self.text_display.setPlainText(
                "Welcome to Teleprompter!\n\n"
                "Right-click to paste your script or create a 'script.txt' file in the same directory."
            )
    
    def show_context_menu(self, position):
        """Show custom context menu for right-click"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(60, 60, 60, 0.95);
                color: white;
                border: 1px solid rgba(100, 100, 100, 0.8);
            }
            QMenu::item:selected {
                background-color: rgba(100, 100, 100, 0.8);
            }
        """)
        
        # Paste action
        paste_action = QAction("Paste Text", self)
        paste_action.triggered.connect(self.paste_text)
        menu.addAction(paste_action)
        
        # Reload script action
        reload_action = QAction("Reload Script from File", self)
        reload_action.triggered.connect(self.load_script)
        menu.addAction(reload_action)
        
        # Clear action
        clear_action = QAction("Clear Text", self)
        clear_action.triggered.connect(self.text_display.clear)
        menu.addAction(clear_action)
        
        menu.exec(self.text_display.mapToGlobal(position))
    
    def paste_text(self):
        """Paste text from clipboard"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.text_display.setPlainText(text)
    
    def toggle_pin(self):
        """Toggle pin state to freeze/unfreeze window dragging"""
        self.is_pinned = not self.is_pinned
        
        if self.is_pinned:
            self.pin_button.setText("🔒")
            self.pin_button.setStyleSheet(self.get_button_style() + """
                QPushButton {
                    background-color: rgba(100, 150, 100, 0.8);
                }
            """)
        else:
            self.pin_button.setText("📌")
            self.pin_button.setStyleSheet(self.get_button_style())
    
    def toggle_visibility(self):
        """Toggle visibility (opacity) of the window"""
        self.is_hidden = not self.is_hidden
        
        if self.is_hidden:
            self.setWindowOpacity(self.hidden_opacity)
            self.eye_button.setText("👁‍🗨")
        else:
            self.setWindowOpacity(self.normal_opacity)
            self.eye_button.setText("👁")
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton and not self.is_pinned:
            # Check if click is in header area
            if self.header.geometry().contains(event.pos()):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and not self.is_pinned:
            if not self.drag_position.isNull():
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = QPoint()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = TeleprompterWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
