#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NSZ-Qt Launcher
---------------
Dedicated launcher for the Qt-based GUI for NSZ
"""

import sys
import os
import pathlib

# Ensure Python version is compatible
if sys.hexversion < 0x03060000:
    print("NSZ-Qt requires at least Python 3.6!")
    print(f"Current python version is {sys.version}")
    sys.exit(1)

# Add the parent directory to the path if needed
if __name__ == '__main__':
    # Setup multiprocessing support
    import multiprocessing
    multiprocessing.freeze_support()
    
    # Try to import the nsz package
    try:
        import nsz.gui_qt.main_qt as main_qt
    except ImportError:
        # If import fails, add the parent directory to the path
        path = pathlib.Path(__file__).resolve().parent.absolute()
        sys.path.append(str(path))
        try:
            import nsz.gui_qt.main_qt as main_qt
        except ImportError:
            print("Error: Could not import the nsz.gui_qt.main_qt module.")
            print("Make sure the nsz package is properly installed.")
            sys.exit(1)
    
    # Launch the Qt GUI
    main_qt.main()
