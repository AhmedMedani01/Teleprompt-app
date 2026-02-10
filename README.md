# Desktop Teleprompter Application

A professional desktop teleprompter built with PyQt6/PySide6, featuring a frameless, transparent window with customizable controls.

## Features

- **Frameless Window**: Clean, distraction-free interface
- **Always on Top**: Stays visible over other applications
- **Transparent Background**: Adjustable opacity (0.5 default, 0.05 when hidden)
- **Draggable Header**: Move the window anywhere on your screen
- **Pin/Freeze**: Lock the window in place to prevent accidental dragging
- **Hide/Show Toggle**: Quickly minimize opacity for screen recording or presentations
- **Large, Readable Text**: White text on semi-transparent background
- **Script Loading**: Automatically loads from `script.txt`
- **Right-Click Menu**: Paste text directly from clipboard or reload script

## Installation

### Option 1: Using PySide6 (Recommended - Better Compatibility)

```bash
pip install PySide6
```

Then run:
```bash
python teleprompter_pyside6.py
```

### Option 2: Using PyQt6

```bash
pip install PyQt6
```

Then run:
```bash
python teleprompter.py
```

**Note**: If you encounter build errors with PyQt6 (especially on older Python 3.7), use PySide6 instead. Both applications are functionally identical.

## Usage

1. **Run the application**:
   ```bash
   # PySide6 version (recommended)
   python teleprompter_pyside6.py
   
   # OR PyQt6 version
   python teleprompter.py
   ```

2. **Loading Your Script**:
   - **Option 1**: Edit the `script.txt` file with your teleprompter text
   - **Option 2**: Right-click in the text area and select "Paste Text" to paste from clipboard

3. **Controls**:
   - **📌 Pin Button**: Click to freeze/unfreeze window dragging (changes to 🔒 when pinned)
   - **👁 Eye Button**: Click to toggle opacity between normal (0.5) and hidden (0.05)
   - **✕ Close Button**: Close the application
   - **Header Area**: Click and drag to move the window (when not pinned)

4. **Right-Click Menu**:
   - **Paste Text**: Insert text from clipboard
   - **Reload Script from File**: Reload content from `script.txt`
   - **Clear Text**: Clear all text

## Customization

You can modify the following in either `teleprompter.py` or `teleprompter_pyside6.py`:

- **Font Size**: Change `QFont("Arial", 24)` to your preferred size
- **Opacity Levels**: Modify `self.normal_opacity` and `self.hidden_opacity` in `__init__`
  ```python
  self.normal_opacity = 0.5  # Change this (0.0 to 1.0)
  self.hidden_opacity = 0.05 # Change this (0.0 to 1.0)
  ```
- **Window Size**: Adjust `self.setGeometry(100, 100, 800, 600)` values
  ```python
  self.setGeometry(x_pos, y_pos, width, height)
  ```
- **Background Color**: Edit the RGBA values in the QFrame stylesheet
  ```python
  background-color: rgba(128, 128, 128, 0.5);  # R, G, B, Alpha
  ```
- **Text Color**: Change `color: white;` in the text display stylesheet

## Tips

- Use the **Pin** feature when you want to ensure the window stays in place during recording
- Use the **Eye** toggle to temporarily hide the teleprompter while keeping it active
- The window has no visible scrollbars - use your mouse wheel to scroll through long scripts
- Right-click for quick access to paste and reload functions
- Place the teleprompter near your camera for natural eye contact during recordings

## Requirements

- **Python**: 3.8+ (recommended), 3.7+ (PySide6 only)
- **PyQt6**: 6.4.0+ OR **PySide6**: 6.4.0+

## Troubleshooting

**Problem**: PyQt6 installation fails with "qmake not found" error

**Solution**: Use PySide6 instead:
```bash
pip install PySide6
python teleprompter_pyside6.py
```

**Problem**: Window doesn't appear or crashes immediately

**Solution**: Ensure you have a compatible graphics driver. Try updating your display drivers.

**Problem**: Text is too small/large

**Solution**: Edit the font size in the script (line with `QFont("Arial", 24)`)

## License

Free to use and modify as needed.
