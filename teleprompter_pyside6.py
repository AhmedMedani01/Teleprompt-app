"""
Desktop Teleprompter Application (PySide6 Version)
A frameless, transparent teleprompter with pin and hide functionality
Features a text editor page with formatting controls and a teleprompter display page.
"""

import sys
import os
import io
import ctypes
import ctypes.wintypes
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QVBoxLayout,
    QHBoxLayout, QTextEdit, QPushButton, QMenu, QLabel,
    QStackedWidget, QWidget, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, QPoint, QTimer, QElapsedTimer, QThread, Signal, QBuffer
from PySide6.QtGui import (
    QAction, QFont, QTextCharFormat, QTextCursor, QTextDocument, QColor,
    QGuiApplication, QPixmap
)


class EditorPage(QWidget):
    """Page 1: Text editor with formatting controls and a Start button."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        # Start with empty editor, no pre-loading

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

        # --- Separator ---
        sep1 = QFrame()
        sep1.setFixedWidth(1)
        sep1.setFixedHeight(20)
        sep1.setStyleSheet("background-color: rgba(150, 150, 160, 0.5);")
        tb_layout.addWidget(sep1)

        # Undo button
        self.undo_btn = QPushButton("↩")
        self.undo_btn.setFont(QFont("Arial", 14))
        self.undo_btn.setStyleSheet(btn_style)
        self.undo_btn.setToolTip("Undo (Ctrl+Z)")
        self.undo_btn.clicked.connect(lambda: self.editor.undo())
        tb_layout.addWidget(self.undo_btn)

        # Redo button
        self.redo_btn = QPushButton("↪")
        self.redo_btn.setFont(QFont("Arial", 14))
        self.redo_btn.setStyleSheet(btn_style)
        self.redo_btn.setToolTip("Redo (Ctrl+Y)")
        self.redo_btn.clicked.connect(lambda: self.editor.redo())
        tb_layout.addWidget(self.redo_btn)

        # --- Separator ---
        sep2 = QFrame()
        sep2.setFixedWidth(1)
        sep2.setFixedHeight(20)
        sep2.setStyleSheet("background-color: rgba(150, 150, 160, 0.5);")
        tb_layout.addWidget(sep2)

        # Find & Replace toggle
        self.find_btn = QPushButton("🔍")
        self.find_btn.setFont(QFont("Arial", 13))
        self.find_btn.setCheckable(True)
        self.find_btn.setStyleSheet(btn_style)
        self.find_btn.setToolTip("Find & Replace")
        self.find_btn.clicked.connect(self.toggle_find_panel)
        tb_layout.addWidget(self.find_btn)

        tb_layout.addStretch()
        outer_layout.addWidget(toolbar)

        # --- Find & Replace Panel ---
        self.find_panel = QFrame()
        self.find_panel.setObjectName("findPanel")
        self.find_panel.setStyleSheet("""
            QFrame#findPanel {
                background-color: rgba(60, 60, 68, 0.9);
                border-radius: 6px;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #222;
                border: 1px solid rgba(180, 180, 190, 0.6);
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #6aa5e8;
            }
            QLabel {
                color: rgba(200, 200, 210, 0.9);
                font-size: 12px;
            }
        """)
        self.find_panel.hide()

        fp_layout = QVBoxLayout(self.find_panel)
        fp_layout.setContentsMargins(12, 10, 12, 10)
        fp_layout.setSpacing(8)

        # Find row
        find_row = QHBoxLayout()
        find_row.setSpacing(6)
        find_label = QLabel("Find")
        find_label.setFixedWidth(52)
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find in text…")
        self.find_input.returnPressed.connect(self.find_next)

        fr_btn_style = """
            QPushButton {
                background-color: rgba(90, 90, 100, 0.7);
                color: white; border: none; border-radius: 4px;
                font-size: 13px; padding: 4px 10px; min-width: 28px;
            }
            QPushButton:hover { background-color: rgba(120, 120, 135, 0.85); }
            QPushButton:pressed { background-color: rgba(60, 60, 70, 0.95); }
        """

        self.find_prev_btn = QPushButton("↑")
        self.find_prev_btn.setStyleSheet(fr_btn_style)
        self.find_prev_btn.setToolTip("Previous match")
        self.find_prev_btn.clicked.connect(self.find_prev)

        self.find_next_btn = QPushButton("↓")
        self.find_next_btn.setStyleSheet(fr_btn_style)
        self.find_next_btn.setToolTip("Next match")
        self.find_next_btn.clicked.connect(self.find_next)

        self.match_label = QLabel("")
        self.match_label.setFixedWidth(60)

        find_row.addWidget(find_label)
        find_row.addWidget(self.find_input, 1)
        find_row.addWidget(self.find_prev_btn)
        find_row.addWidget(self.find_next_btn)
        find_row.addWidget(self.match_label)
        fp_layout.addLayout(find_row)

        # Replace row
        replace_row = QHBoxLayout()
        replace_row.setSpacing(6)
        replace_label = QLabel("Replace")
        replace_label.setFixedWidth(52)
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with…")

        self.replace_btn = QPushButton("Replace")
        self.replace_btn.setStyleSheet(fr_btn_style)
        self.replace_btn.clicked.connect(self.replace_current)

        self.replace_all_btn = QPushButton("Replace All")
        self.replace_all_btn.setStyleSheet(fr_btn_style)
        self.replace_all_btn.clicked.connect(self.replace_all)

        replace_row.addWidget(replace_label)
        replace_row.addWidget(self.replace_input, 1)
        replace_row.addWidget(self.replace_btn)
        replace_row.addWidget(self.replace_all_btn)
        fp_layout.addLayout(replace_row)

        outer_layout.addWidget(self.find_panel)

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
        self.editor.textChanged.connect(self.on_text_changed)
        outer_layout.addWidget(self.editor, 1)

        # --- Start button ---
        self.start_btn = QPushButton("Start")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setFixedHeight(44)
        self.start_btn.setEnabled(False)  # Initially disabled
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
            QPushButton:disabled {
                background-color: rgba(100, 100, 110, 0.5);
                color: rgba(255, 255, 255, 0.4);
            }
        """)
        outer_layout.addWidget(self.start_btn)

        # --- AI Mode button ---
        self.ai_mode_btn = QPushButton("✨ AI Mode")
        self.ai_mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_mode_btn.setFixedHeight(44)
        self.ai_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #a855f7
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
                    stop:0 #6d28d9, stop:1 #9333ea
                );
            }
            QPushButton:pressed {
                background-color: #5b21b6;
            }
        """)
        outer_layout.addWidget(self.ai_mode_btn)

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

    # ----- Find & Replace -----

    def toggle_find_panel(self):
        visible = self.find_btn.isChecked()
        self.find_panel.setVisible(visible)
        if visible:
            self.find_input.setFocus()
            self.find_input.selectAll()

    def find_next(self):
        self._do_find(backward=False)

    def find_prev(self):
        self._do_find(backward=True)

    def _do_find(self, backward=False):
        text = self.find_input.text()
        if not text:
            self.match_label.setText("")
            return
        flags = QTextDocument.FindFlag(0)
        if backward:
            flags |= QTextDocument.FindFlag.FindBackward
        found = self.editor.find(text, flags)
        if not found:
            # Wrap around: move cursor to start/end and try again
            cursor = self.editor.textCursor()
            if backward:
                cursor.movePosition(QTextCursor.MoveOperation.End)
            else:
                cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            found = self.editor.find(text, flags)
        self.match_label.setText("Found" if found else "No match")

    def replace_current(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.find_input.text():
            cursor.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        text = self.find_input.text()
        replacement = self.replace_input.text()
        if not text:
            return
        # Move to start
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        count = 0
        while self.editor.find(text):
            tc = self.editor.textCursor()
            tc.insertText(replacement)
            count += 1
        self.match_label.setText(f"{count} replaced")

    def on_text_changed(self):
        """Enable/disable Start button based on text content."""
        has_text = bool(self.editor.toPlainText().strip())
        self.start_btn.setEnabled(has_text)

    def get_html(self):
        """Return the editor content as HTML (preserves formatting)."""
        return self.editor.toHtml()


class TeleprompterPage(QWidget):
    """Page 2: The actual teleprompter display with auto-scroll."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_scrolling = False
        self.scroll_speed = 1        # pixels per tick
        self.scroll_interval = 50    # ms between ticks
        self.init_ui()

        # Scroll timer
        self.scroll_timer = QTimer(self)
        self.scroll_timer.setInterval(self.scroll_interval)
        self.scroll_timer.timeout.connect(self._scroll_tick)

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
        # Click on text area toggles scrolling
        self.text_display.installEventFilter(self)
        layout.addWidget(self.text_display, 1)

        # Hint label (shown when scrolling is paused)
        self.hint_label = QLabel("Press Enter or click to start scrolling")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 12px;
            padding: 4px;
        """)
        layout.addWidget(self.hint_label)

    def set_content_html(self, html):
        self.text_display.setHtml(html)
        # Reset scroll to top
        self.text_display.verticalScrollBar().setValue(0)

    def set_content_plain(self, text):
        self.text_display.setPlainText(text)
        self.text_display.verticalScrollBar().setValue(0)

    def toggle_scroll(self):
        """Start or pause auto-scrolling."""
        if self.is_scrolling:
            self.pause_scroll()
        else:
            self.start_scroll()

    def start_scroll(self):
        self.is_scrolling = True
        self.scroll_timer.start()
        self.hint_label.setText("Scrolling… (press Enter or click to pause)")

    def pause_scroll(self):
        self.is_scrolling = False
        self.scroll_timer.stop()
        self.hint_label.setText("Paused — press Enter or click to resume")

    def stop_scroll(self):
        """Fully stop and reset scroll state."""
        self.is_scrolling = False
        self.scroll_timer.stop()
        self.hint_label.setText("Press Enter or click to start scrolling")

    def _scroll_tick(self):
        sb = self.text_display.verticalScrollBar()
        if sb.value() >= sb.maximum():
            self.pause_scroll()
            self.hint_label.setText("End of script")
            return
        sb.setValue(sb.value() + self.scroll_speed)

    # --- Event filter: capture Enter key and mouse clicks ---

    def eventFilter(self, obj, event):
        if obj is self.text_display:
            from PySide6.QtCore import QEvent
            if event.type() == QEvent.Type.KeyPress:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.toggle_scroll()
                    return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.toggle_scroll()
                    return True
        return super().eventFilter(obj, event)


# -------------------------------------------------------------------- #
#  AI Worker Thread (runs API call off the UI thread)
# -------------------------------------------------------------------- #

class AIWorkerThread(QThread):
    """Background thread for AI vision model calls."""
    finished = Signal(str)   # emits the response text
    error = Signal(str)      # emits error message

    def __init__(self, image_bytes: bytes, prompt: str, parent=None):
        super().__init__(parent)
        self.image_bytes = image_bytes
        self.prompt = prompt

    def run(self):
        try:
            from ai_model_factory import get_vision_model
            model = get_vision_model()
            response = model(self.image_bytes, self.prompt)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


# -------------------------------------------------------------------- #
#  AI Mode Page
# -------------------------------------------------------------------- #

class AIModePage(QWidget):
    """Page 3: AI assistant mode — capture screen and get AI analysis."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Outer frame ---
        outer_frame = QFrame()
        outer_frame.setObjectName("aiOuter")
        outer_frame.setStyleSheet("""
            QFrame#aiOuter {
                background-color: transparent;
                border-radius: 10px;
            }
        """)
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(16, 12, 16, 16)
        outer_layout.setSpacing(10)

        # --- Capture toolbar ---
        capture_bar = QFrame()
        capture_bar.setObjectName("captureBar")
        capture_bar.setFixedHeight(44)
        capture_bar.setStyleSheet("""
            QFrame#captureBar {
                background-color: rgba(55, 45, 80, 0.5);
                border-radius: 8px;
            }
        """)
        cb_layout = QHBoxLayout(capture_bar)
        cb_layout.setContentsMargins(12, 6, 12, 6)
        cb_layout.setSpacing(10)

        # Capture button
        self.capture_btn = QPushButton("📸  Capture & Analyze")
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.setFixedHeight(32)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #a855f7
                );
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                padding: 4px 18px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6d28d9, stop:1 #9333ea
                );
            }
            QPushButton:pressed {
                background-color: #5b21b6;
            }
            QPushButton:disabled {
                background-color: rgba(100, 80, 140, 0.4);
                color: rgba(255, 255, 255, 0.4);
            }
        """)
        cb_layout.addWidget(self.capture_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: rgba(200, 180, 255, 0.8);
            font-size: 12px;
            padding: 0 8px;
        """)
        cb_layout.addWidget(self.status_label)
        cb_layout.addStretch()

        outer_layout.addWidget(capture_bar)

        # --- AI response canvas ---
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setFont(QFont("Consolas", 13))
        self.response_display.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 16px;
                selection-background-color: rgba(120, 80, 220, 0.4);
            }
        """)
        self.response_display.setPlaceholderText(
            "Click \"📸 Capture & Analyze\" to capture your screen and get AI analysis…"
        )
        outer_layout.addWidget(self.response_display, 1)

        layout.addWidget(outer_frame)

    def set_loading(self, loading: bool):
        """Toggle loading state."""
        self.capture_btn.setEnabled(not loading)
        if loading:
            self.status_label.setText("⏳ Analyzing screenshot…")
        else:
            self.status_label.setText("")

    def set_response(self, text: str):
        """Display the AI response."""
        self.response_display.setPlainText(text)

    def set_error(self, msg: str):
        """Display an error."""
        self.response_display.setPlainText(f"❌ Error: {msg}")

    def clear(self):
        """Reset the canvas."""
        self.response_display.clear()
        self.status_label.setText("")


class TeleprompterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_pinned = False
        self.is_hidden = False
        self._always_on_top = True   # starts on top
        self._click_through = False  # click-through disabled by default
        self.normal_opacity = 0.5
        self.hidden_opacity = 0.05

        # For dragging
        self.drag_position = QPoint()

        # AI worker thread reference
        self._ai_worker = None

        # Session elapsed timer
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_display_timer = QTimer(self)
        self.elapsed_display_timer.setInterval(1000)
        self.elapsed_display_timer.timeout.connect(self._update_elapsed)

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
        
        # Enable screen capture protection after window is shown
        # Using QTimer to ensure window is fully initialized first
        QTimer.singleShot(100, lambda: self.set_screen_capture_protection(True))

        # --- Central container ---
        self.main_frame = QFrame()
        self.main_frame.setStyleSheet("""
            QFrame#mainFrame {
                background-color: rgba(0, 0, 0, 0.5);
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
        self.editor_page.ai_mode_btn.clicked.connect(self.go_to_ai_mode)
        self.stack.addWidget(self.editor_page)

        # Page 1 – Teleprompter
        self.teleprompter_page = TeleprompterPage()
        self.teleprompter_page.text_display.customContextMenuRequested.connect(
            self.show_context_menu
        )
        self.stack.addWidget(self.teleprompter_page)

        # Page 2 – AI Mode
        self.ai_page = AIModePage()
        self.ai_page.capture_btn.clicked.connect(self.capture_and_analyze)
        self.stack.addWidget(self.ai_page)

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

        # AI / Prompter switch button in header
        self.mode_switch_btn = QPushButton("✨ AI")
        self.mode_switch_btn.setFixedHeight(20)
        self.mode_switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_switch_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 60, 200, 0.7), stop:1 rgba(160, 80, 240, 0.7)
                );
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 600;
                padding: 2px 10px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(120, 70, 220, 0.85), stop:1 rgba(180, 100, 255, 0.85)
                );
            }
        """)
        self.mode_switch_btn.setToolTip("Switch between AI and Prompter mode")
        self.mode_switch_btn.clicked.connect(self._toggle_mode)
        header_layout.addWidget(self.mode_switch_btn)

        # Title
        self.title_label = QLabel("Teleprompter")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Elapsed timer label
        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.85);
            font-size: 12px;
            font-family: 'Consolas', 'Courier New', monospace;
            padding: 0 6px;
        """)
        self.timer_label.setToolTip("Session elapsed time")
        header_layout.addWidget(self.timer_label)

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

        # Always-on-top button
        self.ontop_button = QPushButton("📏")
        self.ontop_button.setFixedSize(25, 20)
        self.ontop_button.setStyleSheet(self._btn_style() + """
            QPushButton { background-color: rgba(100, 150, 100, 0.8); }
        """)
        self.ontop_button.setToolTip("Toggle always on top")
        self.ontop_button.clicked.connect(self.toggle_always_on_top)
        header_layout.addWidget(self.ontop_button)

        # Click-through button
        self.clickthrough_button = QPushButton("👆")
        self.clickthrough_button.setFixedSize(25, 20)
        self.clickthrough_button.setStyleSheet(self._btn_style())
        self.clickthrough_button.setToolTip("Click-through mode (clicks pass to apps behind)")
        self.clickthrough_button.clicked.connect(self.toggle_click_through)
        header_layout.addWidget(self.clickthrough_button)

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
        self.timer_label.hide()
        self.ontop_button.hide()
        self.clickthrough_button.hide()
        self.mode_switch_btn.setText("✨ AI")
        self.mode_switch_btn.show()
        self.title_label.setText("Teleprompter")
        # Disable click-through when returning to editor
        if self._click_through:
            self._click_through = False
            self.clickthrough_button.setStyleSheet(self._btn_style())
        # Full opacity for editor page
        self.setWindowOpacity(0.95)

    def _show_teleprompter_page(self):
        self.stack.setCurrentIndex(1)
        self.back_button.show()
        self.pin_button.show()
        self.eye_button.show()
        self.timer_label.show()
        self.ontop_button.show()
        self.clickthrough_button.show()
        self.mode_switch_btn.setText("✨ AI")
        self.mode_switch_btn.show()
        self.title_label.setText("Teleprompter")
        # Restore configured opacity
        self.is_hidden = False
        self.eye_button.setText("👁")
        self.setWindowOpacity(self.normal_opacity)

    def _show_ai_page(self):
        self.stack.setCurrentIndex(2)
        self.back_button.hide()
        self.pin_button.show()
        self.eye_button.show()
        self.timer_label.hide()
        self.ontop_button.show()
        self.clickthrough_button.show()
        self.mode_switch_btn.setText("📝 Prompter")
        self.mode_switch_btn.show()
        self.title_label.setText("✨ AI Assistant")
        # Same transparency as teleprompter
        self.is_hidden = False
        self.eye_button.setText("👁")
        self.setWindowOpacity(self.normal_opacity)

    def _toggle_mode(self):
        """Switch between AI mode and Prompter (editor) mode."""
        current = self.stack.currentIndex()
        if current == 2:  # AI page → Editor
            self.go_to_editor_from_ai()
        else:  # Editor or Teleprompter → AI
            self.go_to_ai_mode()

    def go_to_teleprompter(self):
        """Transfer editor content → teleprompter display and switch page."""
        html = self.editor_page.get_html()
        self.teleprompter_page.set_content_html(html)
        self._show_teleprompter_page()
        # Start session timer
        self.elapsed_timer.start()
        self.elapsed_display_timer.start()
        self.timer_label.setText("00:00")

    def go_to_editor(self):
        """Switch back to editor page."""
        # Stop scrolling and session timer
        self.teleprompter_page.stop_scroll()
        self.elapsed_display_timer.stop()
        self._show_editor_page()

    def go_to_ai_mode(self):
        """Switch to AI mode with an empty canvas."""
        self.ai_page.clear()
        self._show_ai_page()

    def go_to_editor_from_ai(self):
        """Switch from AI mode back to editor."""
        self._show_editor_page()

    def _update_elapsed(self):
        """Update the elapsed timer label every second."""
        elapsed_ms = self.elapsed_timer.elapsed()
        total_secs = elapsed_ms // 1000
        mins = total_secs // 60
        secs = total_secs % 60
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")

    # ------------------------------------------------------------------ #
    #  AI Mode – Screen Capture & Analysis
    # ------------------------------------------------------------------ #

    def capture_and_analyze(self):
        """Capture the screen (quietly) and send to AI for analysis."""
        self.ai_page.set_loading(True)

        # 1. Temporarily hide the window so it doesn't appear in the screenshot
        self.hide()
        QApplication.processEvents()  # ensure repaint
        QTimer.singleShot(200, self._do_capture)

    def _do_capture(self):
        """Take the screenshot and restore the window."""
        try:
            screen = QGuiApplication.primaryScreen()
            if screen is None:
                self.show()
                self.ai_page.set_error("Could not access primary screen.")
                self.ai_page.set_loading(False)
                return

            pixmap = screen.grabWindow(0)  # 0 = entire screen

            # Convert QPixmap → PNG bytes
            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.ReadWrite)
            pixmap.save(buffer, "PNG")
            image_bytes = bytes(buffer.data())
            buffer.close()

        except Exception as e:
            self.show()
            self.ai_page.set_error(f"Screenshot failed: {e}")
            self.ai_page.set_loading(False)
            return

        # 2. Restore the window
        self.show()
        self.raise_()
        self.activateWindow()

        # 3. Send to AI in background thread
        prompt = (
            "Analyze the screenshot carefully. "
            "If there is a question visible, answer it clearly. "
            "If there is code, explain it and fix any issues. "
            "If there is a problem or error, provide a solution. "
            "Give a clear, well-structured response."
        )

        self._ai_worker = AIWorkerThread(image_bytes, prompt, parent=self)
        self._ai_worker.finished.connect(self._on_ai_response)
        self._ai_worker.error.connect(self._on_ai_error)
        self._ai_worker.start()

    def _on_ai_response(self, text: str):
        """Handle successful AI response."""
        self.ai_page.set_loading(False)
        self.ai_page.set_response(text)

    def _on_ai_error(self, msg: str):
        """Handle AI error."""
        self.ai_page.set_loading(False)
        self.ai_page.set_error(msg)

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

    # ------------------------------------------------------------------ #
    #  Screen Capture Protection
    # ------------------------------------------------------------------ #

    def set_screen_capture_protection(self, enabled=True):
        """Enable or disable screen capture protection (Windows only).
        
        This prevents the window from being captured in screenshots,
        screen recordings, and screen sharing sessions.
        
        Args:
            enabled (bool): True to enable protection, False to disable
            
        Returns:
            bool: True if successful, False otherwise
        """
        if sys.platform != 'win32':
            return False
        
        try:
            # Get window handle
            hwnd = int(self.winId())
            
            # Define Windows API constants
            WDA_NONE = 0x00000000
            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            
            # Set display affinity
            user32 = ctypes.windll.user32
            affinity = WDA_EXCLUDEFROMCAPTURE if enabled else WDA_NONE
            result = user32.SetWindowDisplayAffinity(hwnd, affinity)
            
            if result:
                status = "enabled" if enabled else "disabled"
                print(f"Screen capture protection {status}")
            else:
                print("Failed to set screen capture protection")
            
            return result != 0
        except Exception as e:
            print(f"Error setting screen capture protection: {e}")
            return False


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = TeleprompterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
