# Switch File Manager NSZ GUI

A graphical user interface (GUI) built with Python and PySide6 to manage Nintendo Switch game files (NSP, NSZ, XCI) using the underlying `nsz` command-line tool.

## Acknowledgments

This project is a Qt-based file manager built on top of the NSZ compression tool originally created by [Nico Bosshard (nicoboss)](https://github.com/nicoboss/nsz). The core compression/decompression functionality is preserved from the original project, while the GUI has been completely reimplemented using PySide6 (Qt) instead of Kivy.

## Features

*   Browse input and output folders with a modern split-pane interface
*   View files grouped by TitleID with expandable/collapsible groups
*   Select files individually or by group using checkboxes
*   Context menu actions (requires `nsz.py`):
    *   Compress (to NSZ) with options for:
        *   Compression level (1-22)
        *   Block size (128KB to 4MB)
        *   Verification after compression
    *   Decompress (from NSZ)
    *   Unduplicate
    *   Get Info / Rename with automatic Title ID and version detection
    *   Extract with options for:
        *   Extract all files
        *   Verification after extraction
*   Folder selection persistence between sessions
*   Expand/Collapse all groups
*   Auto-resizing columns
*   Key file detection status indicator
*   Modern dark theme using qt-material
*   Console output display for operation feedback
*   Automatic file renaming with Title ID and version detection

## Requirements

*   Python 3.6+
*   PySide6 (`pip install PySide6`)
*   qt-material (`pip install qt-material`) for theming
*   Other dependencies as specified in `requirements.txt`

## Installation

```bash
# Clone the repository
git clone https://github.com/jonwhittingham/switch-file-manager.git
cd switch-file-manager

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .
```

## Running the Application

You can run the application in one of these ways:

1. Using the dedicated launcher:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python nsz-qt.py
   ```

2. Running the GUI module directly:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python nsz/gui_qt/main_qt.py
   ```

## File Naming Convention

The application automatically renames files using the following format:
- Base game: `Game Name [TitleID].nsp`
- Updates/DLC: `Game Name [TitleID][vVersion].nsp`

The Title ID and version are automatically detected from the file's metadata. If a version is not found and the Title ID ends in '000', it is treated as version 0.

## Title Keys

For operations that require decryption (like getting info from encrypted files), you need to have the appropriate key files in your `~/.switch/` directory:
- `prod.keys` - Contains the keys needed for decryption
- `titlekeys.txt` - Contains title-specific keys

The application will show a status indicator at the bottom of the window to let you know if these files are detected.

## Author

- Jon Whittingham (jon@crownparkcomputing.com)

Based on NSZ by Nico Bosshard (nico@bosshome.ch)
