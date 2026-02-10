"""
Desktop Teleprompter Application (PySide6 Version)
A frameless, transparent teleprompter with pin and hide functionality
Features a text editor page with formatting controls and a teleprompter display page.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QVBoxLayout,
    QHBoxLayout, QTextEdit, QPushButton, QMenu, QLabel,
    QStackedWidget, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction, QFont, QTextCharFormat, QTextCursor


class EditorPage(QWidget):
    """Page 1: Text editor with formatting controls and a Start button."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_script()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Outer frame ---
        outer_frame = QFrame()
        outer_frame.setStyleSheet("""
            QFrame#editorOuter {
                background-color: rgba(50, 50, 55, 0.92);
                border-radius: 10px;
            }
        """)
        outer_frame.setObjectName("editorOuter")
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(24, 18, 24, 24)
        outer_layout.setSpacing(14)

        # --- Title ---
        title = QLabel("Prepare Your Script")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #ffffff;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 1px;
            padding: 4px 0 2px 0;
        """)
        outer_layout.addWidget(title)

        # --- Formatting toolbar ---
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame#toolbar {
                background-color: rgba(70, 70, 78, 0.85);
                border-radius: 6px;
            }
        """)
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(38)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 4, 8, 4)
        tb_layout.setSpacing(6)

        btn_style = """
            QPushButton {
                background-color: rgba(90, 90, 100, 0.7);
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                padding: 2px 12px;
                min-width: 32px;
            }
            QPushButton:hover {
                background-color: rgba(120, 120, 135, 0.85);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 70, 0.95);
            }
            QPushButton:checked {
                background-color: rgba(100, 160, 255, 0.75);
            }
        """

        self.bold_btn = QPushButton("B")
        self.bold_btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.bold_btn.setCheckable(True)
        self.bold_btn.setStyleSheet(btn_style)
        self.bold_btn.setToolTip("Bold")
        self.bold_btn.clicked.connect(self.toggle_bold)
        tb_layout.addWidget(self.bold_btn)

        self.italic_btn = QPushButton("I")
        _italic_font = QFont("Arial", 13)
        _italic_font.setItalic(True)
        self.italic_btn.setFont(_italic_font)
        self.italic_btn.setCheckable(True)
        self.italic_btn.setStyleSheet(btn_style)
        self.italic_btn.setToolTip("Italic")
        self.italic_btn.clicked.connect(self.toggle_italic)
        tb_layout.addWidget(self.italic_btn)

        self.underline_btn = QPushButton("U")
        _underline_font = QFont("Arial", 13)
        _underline_font.setUnderline(True)
        self.underline_btn.setFont(_underline_font)
        self.underline_btn.setCheckable(True)
        self.underline_btn.setStyleSheet(btn_style)
        self.underline_btn.setToolTip("Underline")
        self.underline_btn.clicked.connect(self.toggle_underline)
        tb_layout.addWidget(self.underline_btn)

        tb_layout.addStretch()
        outer_layout.addWidget(toolbar)

        # --- White text editor ---
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Arial", 14))
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #222222;
                border: none;
                border-radius: 8px;
                padding: 16px;
                selection-background-color: #b3d4fc;
            }
        """)
        self.editor.setPlaceholderText("Type or paste your teleprompter script here…")
        self.editor.cursorPositionChanged.connect(self.update_format_buttons)
        outer_layout.addWidget(self.editor, 1)

        # --- Start button ---
        self.start_btn = QPushButton("Start")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setFixedHeight(44)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c4c, stop:1 #ff6b6b
                );
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d43f3f, stop:1 #e85d5d
                );
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        outer_layout.addWidget(self.start_btn)

        layout.addWidget(outer_frame)

    # ----- Formatting helpers -----

    def toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(
            QFont.Weight.Bold if self.bold_btn.isChecked() else QFont.Weight.Normal
        )
        self._merge_format(fmt)

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self._merge_format(fmt)

    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.underline_btn.isChecked())
        self._merge_format(fmt)

    def _merge_format(self, fmt):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)

    def update_format_buttons(self):
        """Sync toolbar button states with the current cursor format."""
        fmt = self.editor.currentCharFormat()
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())
        self.underline_btn.setChecked(fmt.fontUnderline())

    def load_script(self):
        """Pre-load script.txt into the editor if it exists."""
        script_file = "script.txt"
        if os.path.exists(script_file):
            try:
                with open(script_file, "r", encoding="utf-8") as f:
                    self.editor.setPlainText(f.read())
            except Exception:
                pass

    def get_html(self):
        """Return the editor content as HTML (preserves formatting)."""
        return self.editor.toHtml()


class TeleprompterPage(QWidget):
    """Page 2: The actual teleprompter display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Text display ---
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_display.setFont(QFont("Arial", 24))
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: white;
                border: none;
                padding: 20px;
            }
        """)
        self.text_display.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.text_display, 1)

    def set_content_html(self, html):
        self.text_display.setHtml(html)

    def set_content_plain(self, text):
        self.text_display.setPlainText(text)


class TeleprompterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_pinned = False
        self.is_hidden = False
        self.normal_opacity = 0.5
        self.hidden_opacity = 0.05

        # For dragging
        self.drag_position = QPoint()

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(self.normal_opacity)
        self.setGeometry(100, 100, 800, 600)

        # --- Central container ---
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("""
            QFrame#mainFrame {
                background-color: rgba(128, 128, 128, 0.5);
                border-radius: 10px;
            }
        """)
        self.main_frame.setObjectName("mainFrame")

        main_layout = QVBoxLayout(self.main_frame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header ---
        self.header = self._create_header()
        main_layout.addWidget(self.header)

        # --- Stacked pages ---
        self.stack = QStackedWidget()

        # Page 0 – Editor
        self.editor_page = EditorPage()
        self.editor_page.start_btn.clicked.connect(self.go_to_teleprompter)
        self.stack.addWidget(self.editor_page)

        # Page 1 – Teleprompter
        self.teleprompter_page = TeleprompterPage()
        self.teleprompter_page.text_display.customContextMenuRequested.connect(
            self.show_context_menu
        )
        self.stack.addWidget(self.teleprompter_page)

        main_layout.addWidget(self.stack, 1)
        self.setCentralWidget(self.main_frame)

        # Start on the editor page
        self._show_editor_page()

    # ------------------------------------------------------------------ #
    #  Header
    # ------------------------------------------------------------------ #

    def _create_header(self):
        header = QFrame()
        header.setFixedHeight(30)
        header.setStyleSheet("""
            QFrame#header {
                background-color: rgba(80, 80, 80, 0.7);
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        header.setObjectName("header")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Back button (hidden on editor page)
        self.back_button = QPushButton("← Back")
        self.back_button.setFixedHeight(20)
        self.back_button.setStyleSheet(self._btn_style())
        self.back_button.setToolTip("Back to editor")
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.clicked.connect(self.go_to_editor)
        header_layout.addWidget(self.back_button)

        # Title
        self.title_label = QLabel("Teleprompter")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Pin button
        self.pin_button = QPushButton("📌")
        self.pin_button.setFixedSize(25, 20)
        self.pin_button.setStyleSheet(self._btn_style())
        self.pin_button.setToolTip("Pin/Unpin window (disable dragging)")
        self.pin_button.clicked.connect(self.toggle_pin)
        header_layout.addWidget(self.pin_button)

        # Eye button
        self.eye_button = QPushButton("👁")
        self.eye_button.setFixedSize(25, 20)
        self.eye_button.setStyleSheet(self._btn_style())
        self.eye_button.setToolTip("Hide/Show content")
        self.eye_button.clicked.connect(self.toggle_visibility)
        header_layout.addWidget(self.eye_button)

        # Close button
        close_button = QPushButton("✕")
        close_button.setFixedSize(25, 20)
        close_button.setStyleSheet(self._btn_style(is_close=True))
        close_button.clicked.connect(self.close)
        header_layout.addWidget(close_button)

        return header

    def _btn_style(self, is_close=False):
        hover = "rgba(200, 50, 50, 0.8)" if is_close else "rgba(100, 100, 100, 0.8)"
        return f"""
            QPushButton {{
                background-color: rgba(60, 60, 60, 0.6);
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: rgba(40, 40, 40, 0.9);
            }}
        """

    # ------------------------------------------------------------------ #
    #  Page Navigation
    # ------------------------------------------------------------------ #

    def _show_editor_page(self):
        self.stack.setCurrentIndex(0)
        self.back_button.hide()
        self.pin_button.hide()
        self.eye_button.hide()
        self.title_label.setText("Teleprompter")
        # Full opacity for editor page
        self.setWindowOpacity(0.95)

    def _show_teleprompter_page(self):
        self.stack.setCurrentIndex(1)
        self.back_button.show()
        self.pin_button.show()
        self.eye_button.show()
        self.title_label.setText("Teleprompter")
        # Restore configured opacity
        self.is_hidden = False
        self.eye_button.setText("👁")
        self.setWindowOpacity(self.normal_opacity)

    def go_to_teleprompter(self):
        """Transfer editor content → teleprompter display and switch page."""
        html = self.editor_page.get_html()
        self.teleprompter_page.set_content_html(html)
        self._show_teleprompter_page()

    def go_to_editor(self):
        """Switch back to editor page."""
        self._show_editor_page()

    # ------------------------------------------------------------------ #
    #  Context menu (teleprompter page)
    # ------------------------------------------------------------------ #

    def show_context_menu(self, position):
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

        paste_action = QAction("Paste Text", self)
        paste_action.triggered.connect(self.paste_text)
        menu.addAction(paste_action)

        reload_action = QAction("Reload Script from File", self)
        reload_action.triggered.connect(self.reload_script)
        menu.addAction(reload_action)

        clear_action = QAction("Clear Text", self)
        clear_action.triggered.connect(self.teleprompter_page.text_display.clear)
        menu.addAction(clear_action)

        menu.exec(self.teleprompter_page.text_display.mapToGlobal(position))

    def paste_text(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.teleprompter_page.set_content_plain(text)

    def reload_script(self):
        script_file = "script.txt"
        if os.path.exists(script_file):
            try:
                with open(script_file, "r", encoding="utf-8") as f:
                    self.teleprompter_page.set_content_plain(f.read())
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    #  Pin / Eye toggles
    # ------------------------------------------------------------------ #

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.pin_button.setText("🔒")
            self.pin_button.setStyleSheet(self._btn_style() + """
                QPushButton { background-color: rgba(100, 150, 100, 0.8); }
            """)
        else:
            self.pin_button.setText("📌")
            self.pin_button.setStyleSheet(self._btn_style())

    def toggle_visibility(self):
        self.is_hidden = not self.is_hidden
        if self.is_hidden:
            self.setWindowOpacity(self.hidden_opacity)
            self.eye_button.setText("👁‍🗨")
        else:
            self.setWindowOpacity(self.normal_opacity)
            self.eye_button.setText("👁")

    # ------------------------------------------------------------------ #
    #  Window dragging
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.is_pinned:
            if self.header.geometry().contains(event.position().toPoint()):
                self.drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.is_pinned:
            if not self.drag_position.isNull():
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = QPoint()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TeleprompterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
