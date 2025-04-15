# Switch File Manager NSZ GUI

A graphical user interface (GUI) built with Python and PySide6 to manage Nintendo Switch game files (NSP, NSZ, XCI) using the underlying `nsz` command-line tool.

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

## Requirements

*   Python 3.x
*   PySide6 (`pip install PySide6`)
*   The `nsz` Python script ([https://github.com/nicoboss/nsz](https://github.com/nicoboss/nsz)) placed correctly relative to this GUI script (or ensure `nsz.py` is in your system's PATH).

## Running the Application

1.  Ensure Python and PySide6 are installed.
2.  Make sure the `nsz` script is accessible (e.g., in the parent directory).
3.  Navigate to the project directory in your terminal.
4.  Run the main GUI script:
    ```bash
    python nsz/gui_qt/main_qt.py
    ```
