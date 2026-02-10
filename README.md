# Desktop Teleprompter Application

A professional desktop teleprompter built with PyQt6, featuring a frameless, transparent window with customizable controls.

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

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python teleprompter.py
```

2. **Loading Your Script**:
   - Option 1: Edit the `script.txt` file with your teleprompter text
   - Option 2: Right-click in the text area and select "Paste Text" to paste from clipboard

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

You can modify the following in the `teleprompter.py` file:

- **Font Size**: Change `QFont("Arial", 24)` on line 144
- **Opacity Levels**: Modify `self.normal_opacity` and `self.hidden_opacity` in `__init__`
- **Window Size**: Adjust `self.setGeometry(100, 100, 800, 600)` values
- **Background Color**: Edit the RGBA values in the QFrame stylesheet
- **Text Color**: Change `color: white;` in the text display stylesheet

## Tips

- Use the **Pin** feature when you want to ensure the window stays in place during recording
- Use the **Eye** toggle to temporarily hide the teleprompter while keeping it active
- The window has no visible scrollbars - use your mouse wheel to scroll through long scripts
- Right-click for quick access to paste and reload functions

## Requirements

- Python 3.8+
- PyQt6 6.6.1+

## License

Free to use and modify as needed.
