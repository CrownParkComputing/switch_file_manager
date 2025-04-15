# Switch File Manager NSZ GUI

A graphical user interface (GUI) built with Python and PySide6 to manage Nintendo Switch game files (NSP, NSZ, XCI) using the underlying `nsz` command-line tool.

## Acknowledgments

This project is a Qt-based file manager built on top of the NSZ compression tool originally created by [Nico Bosshard (nicoboss)](https://github.com/nicoboss/nsz). The core compression/decompression functionality is preserved from the original project, while the GUI has been completely reimplemented using PySide6 (Qt) instead of Kivy.

## Features

*   Browse input and output folders.
*   View files grouped by TitleID.
*   Select files individually or by group using checkboxes.
*   Context menu actions (requires `nsz.py`):
    *   Compress (to NSZ)
    *   Decompress (from NSZ)
    *   Unduplicate
    *   Get Info / Rename
    *   Extract
*   Folder selection persistence between sessions.
*   Expand/Collapse all groups.
*   Auto-resizing columns.
*   Key file detection status indicator.
*   Modern dark theme using qt-material.

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

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

You can run the application in one of these ways:

1. Using the dedicated launcher:
   ```bash
   python nsz-qt.py
   ```

2. Running the GUI module directly:
   ```bash
   python nsz/gui_qt/main_qt.py
   ```

## Title Keys

For operations that require decryption (like getting info from encrypted files), you need to have the appropriate key files in your `~/.switch/` directory:
- `prod.keys` - Contains the keys needed for decryption
- `titlekeys.txt` - Contains title-specific keys

The application will show a status indicator at the bottom of the window to let you know if these files are detected.

## Author

- Jon Whittingham (jon@crownparkcomputing.com)

Based on NSZ by Nico Bosshard (nico@bosshome.ch)
