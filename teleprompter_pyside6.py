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
    QStackedWidget, QWidget, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, QPoint, QTimer, QElapsedTimer
from PySide6.QtGui import (
    QAction, QFont, QTextCharFormat, QTextCursor, QTextDocument, QColor
)


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
            elif event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.toggle_scroll()
                    return True
        return super().eventFilter(obj, event)


class TeleprompterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_pinned = False
        self.is_hidden = False
        self.normal_opacity = 0.5
        self.hidden_opacity = 0.05

        # For dragging
        self.drag_position = QPoint()

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
        self.title_label.setText("Teleprompter")
        # Full opacity for editor page
        self.setWindowOpacity(0.95)

    def _show_teleprompter_page(self):
        self.stack.setCurrentIndex(1)
        self.back_button.show()
        self.pin_button.show()
        self.eye_button.show()
        self.timer_label.show()
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

    def _update_elapsed(self):
        """Update the elapsed timer label every second."""
        elapsed_ms = self.elapsed_timer.elapsed()
        total_secs = elapsed_ms // 1000
        mins = total_secs // 60
        secs = total_secs % 60
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")

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
