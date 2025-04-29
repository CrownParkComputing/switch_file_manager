import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
print("DEBUG: sys.path set")
try:
    pass # No longer importing nsz_main directly here
except Exception as e:
    print(f"IMPORT ERROR: {e}")

import threading
import re
from pathlib import Path # Import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLabel, QMenu, QPushButton, QSplitter, QAbstractItemView, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QTextEdit,
    QCheckBox, QSpinBox, QComboBox # Import QCheckBox, QSpinBox, QComboBox
)
from PySide6.QtGui import QFont, QCursor, QAction
from PySide6.QtCore import Qt, Signal, QSettings, Slot, QThread, QObject # Import QThread, QObject

# --- Constants --- #
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NSZ_DIR = os.path.dirname(SCRIPT_DIR)
# nsz.py is in the root directory, not in the nsz directory
NSZ_SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(NSZ_DIR), 'nsz.py'))
TITLE_ID_REGEX = re.compile(r"\[(01[0-9A-Fa-f]{14})\]") # Regex to find TitleID like [01...]

# Add NSZ directory to sys.path to allow importing nsz_main
if NSZ_DIR not in sys.path:
    sys.path.insert(0, NSZ_DIR)

# --- Action logic with console output hooks ---
def format_size(size):
    # Human-readable size
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

# Ensure this function definition is at the top-level (module scope)
def list_files_with_info(folder):
    if not folder or not os.path.isdir(folder):
        return []
    files = []
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path):
            try:
                 size = os.path.getsize(path)
                 ext = os.path.splitext(f)[1][1:].upper() or 'File'
                 title_id = None
                 base_id = None
                 match = TITLE_ID_REGEX.search(f)
                 if match:
                     title_id = match.group(1)
                     # Extract the base ID (first 13 characters) for grouping
                     base_id = title_id[:13]

                 files.append({
                     'name': f,
                     'type': ext,
                     'size': size,
                     'path': path,
                     'title_id': title_id,
                     'base_id': base_id
                 })
            except OSError:
                 # Ignore files we can't access (e.g., permission errors)
                 pass
        # elif os.path.isdir(path):
             # Optionally include directories if needed in the future
             # files.append({'name': f, 'type': 'Folder', 'size': 0, 'path': path})
             # pass
    return files

class FileTreeConsoleWidget(QWidget):
    def __init__(self, folder_type='Input', main_window=None):
        super().__init__()
        self.folder_type = folder_type
        self.main_window = main_window

        layout = QVBoxLayout()

        # --- Add Expand/Collapse Buttons --- 
        button_layout = QHBoxLayout()
        expand_button = QPushButton("Expand All")
        collapse_button = QPushButton("Collapse All")
        expand_button.clicked.connect(self.expand_all_items)
        collapse_button.clicked.connect(self.collapse_all_items)
        button_layout.addWidget(expand_button)
        button_layout.addWidget(collapse_button)
        button_layout.addStretch() # Push buttons to the left
        layout.addLayout(button_layout) 
        # --- End Buttons --- 

        self.tree = FileTreeWidget(folder_type=folder_type, parent=self, main_window=self.main_window)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #181c1f; color: #00ff00; font-family: Consolas, monospace;")
        self.console.setMaximumHeight(120)
        layout.addWidget(self.tree)
        layout.addWidget(QLabel("Console Output:"))
        layout.addWidget(self.console)
        self.setLayout(layout)

        # Connect tree's log signal to console's append method
        self.tree.log_signal.connect(self.append_log)

    def expand_all_items(self):
        self.tree.expandAll()
        self.tree.resize_columns() # Resize after expanding

    def collapse_all_items(self):
        self.tree.collapseAll()
        self.tree.resize_columns() # Resize after collapsing

    @Slot(str)
    def append_log(self, text):
        self.console.append(text)

    def set_folder(self, folder_path):
        self.tree.set_folder(folder_path)

class FileTreeWidget(QTreeWidget):
    log_signal = Signal(str) # Define the signal for logging
    info_result_signal = Signal(str, str, str) # file_path, stdout, stderr for info parsing

    def __init__(self, parent=None, folder_type='Input', main_window=None): # Add main_window arg
        super().__init__(parent)
        self.folder_path = ''
        self.folder_type = folder_type
        self.main_window = main_window
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.setColumnCount(3)
        self.setHeaderLabels(['Name', 'Type', 'Size'])
        self.setRootIsDecorated(True) # Show expand indicators for groups
        self.setAlternatingRowColors(True)
        self.info_result_signal.connect(self.handle_info_result) # Connect info result signal
        self.itemChanged.connect(self.handle_item_changed) # Connect item changed signal for checkboxes
        self.itemExpanded.connect(self.resize_columns) # Resize columns when item is expanded
        self.setStyleSheet("background-color: #263238; color: #fff;")

    def set_folder(self, folder_path):
        self.folder_path = folder_path
        self.refresh()

    def refresh(self):
        self.clear()
        files = list_files_with_info(self.folder_path)
        groups = {} # Key: base_id, Value: QTreeWidgetItem (group parent)

        for f in files:
            base_id = f.get('base_id')
            if base_id:
                group_item = groups.get(base_id)
                if not group_item:
                    # Create new group item
                    # Display the base ID with the correct format
                    group_item = QTreeWidgetItem([f"[{base_id}]"])
                    # Store group info: type, the FOLDER path it belongs to, and the base ID
                    group_item.setData(0, Qt.UserRole, {'type': 'group', 'path': self.folder_path, 'base_id': base_id})
                    group_item.setFlags(group_item.flags() | Qt.ItemIsUserCheckable) # Enable checkbox
                    group_item.setCheckState(0, Qt.Unchecked) # Default to unchecked
                    # Optionally set an icon for groups
                    # group_item.setIcon(0, QIcon(...))
                    self.addTopLevelItem(group_item)
                    groups[base_id] = group_item

                # Create file item as child
                file_item = QTreeWidgetItem([
                    f['name'],
                    f['type'],
                    format_size(f['size'])
                ])
                # Store file info: type, the FILE path, and full title ID
                file_item.setData(0, Qt.UserRole, {'type': 'file', 'path': f['path'], 'title_id': f['title_id']})
                file_item.setFlags(file_item.flags() | Qt.ItemIsUserCheckable) # Enable checkbox
                file_item.setCheckState(0, Qt.Unchecked) # Default to unchecked
                group_item.addChild(file_item)
            else:
                # File without a parsable TitleID - add as top-level
                item = QTreeWidgetItem([
                    f['name'],
                    f['type'],
                    format_size(f['size'])
                ])
                # Store file info: type and FILE path
                item.setData(0, Qt.UserRole, {'type': 'file', 'path': f['path']})
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable) # Enable checkbox
                item.setCheckState(0, Qt.Unchecked) # Default to unchecked
                self.addTopLevelItem(item)

        # Optionally sort top-level items (groups and non-grouped files)
        self.sortItems(0, Qt.AscendingOrder)
        # Autofit columns after populating
        self.resize_columns()

    def resize_columns(self):
        """Resize all columns to fit their content."""
        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)

    def open_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return

        menu = QMenu()
        item_data = item.data(0, Qt.UserRole)
        item_type = item_data.get('type') if isinstance(item_data, dict) else None
        path = item_data.get('path') if isinstance(item_data, dict) else None # Path for file or folder

        if item_type == 'file' and path and os.path.isfile(path):
            # --- Actions for Files (Children or non-grouped top-level) ---
            menu.addAction('Compress...', lambda: self.show_compress_options(path))
            menu.addAction('Decompress...', lambda: self.show_decompress_options(path))
            menu.addAction('Verify', lambda: self.run_nsz_action('verify', path))
            menu.addAction('Info', lambda: self.run_nsz_action('info', path))
            menu.addAction('Titlekeys', lambda: self.run_nsz_action('titlekeys', path))
            menu.addAction('Extract...', lambda: self.show_extract_options(path))
            menu.addAction('Parse Info & Rename', lambda: self.run_nsz_action('info_for_rename', path))
        elif item_type == 'group' and path and os.path.isdir(path):
            # --- Actions for Folders (Parents/Groups) ---
            # Path here is the FOLDER path stored in the group item's data
            menu.addAction('Undupe Folder...', lambda: self.show_undupe_options(path))
        else:
            # Fallback or placeholder for unexpected items
            pass

        menu.exec(QCursor.pos())

    @Slot(QTreeWidgetItem, int)
    def handle_item_changed(self, item, column):
        """Handle changes to item check state for hierarchical selection."""
        if column != 0: # Only handle changes in the first column (checkbox column)
            return

        # --- Temporarily block signals to prevent recursion --- #
        self.blockSignals(True)

        try:
            item_data = item.data(0, Qt.UserRole)
            item_type = item_data.get('type') if isinstance(item_data, dict) else None
            current_state = item.checkState(0)

            if item_type == 'group':
                # Parent item changed: Update all children
                child_count = item.childCount()
                for i in range(child_count):
                    child = item.child(i)
                    child.setCheckState(0, current_state)
            elif item_type == 'file':
                # Child item changed: Update parent
                parent = item.parent()
                if parent:
                    if current_state == Qt.Unchecked:
                        # If one child is unchecked, parent becomes partially or fully unchecked
                        all_unchecked = True
                        for i in range(parent.childCount()):
                            if parent.child(i).checkState(0) != Qt.Unchecked:
                                all_unchecked = False
                                break
                        if all_unchecked:
                            parent.setCheckState(0, Qt.Unchecked)
                        else:
                            parent.setCheckState(0, Qt.PartiallyChecked)
                    elif current_state == Qt.Checked:
                        # If one child is checked, check if all siblings are now checked
                        all_checked = True
                        for i in range(parent.childCount()):
                            if parent.child(i).checkState(0) == Qt.Unchecked:
                                all_checked = False
                                parent.setCheckState(0, Qt.PartiallyChecked)
                                break
                        if all_checked:
                            parent.setCheckState(0, Qt.Checked)
        finally:
            # --- Always unblock signals --- #
            self.blockSignals(False)

    # --- Intermediate methods to show dialogs --- #
    def show_compress_options(self, file_path):
        if not self.main_window or not getattr(self.main_window, 'output_folder_path', None):
             self.log_signal.emit("[ERROR] Output folder not selected.")
             return
        dialog = CompressOptionsDialog(file_path, self)
        if dialog.exec():
             extra_options = dialog.get_selected_options()
             self.run_nsz_action('compress', file_path, extra_args=extra_options)
        else:
             self.log_signal.emit("[INFO] Compress action cancelled by user.")

    def show_undupe_options(self, folder_path):
        dialog = UndupeOptionsDialog(folder_path, self)
        if dialog.exec():
             selected_options = dialog.get_selected_options()
             self.log_signal.emit(f"[INFO] Starting unduplication for folder: {folder_path} with options: {' '.join(selected_options) if selected_options else 'None'}")
             # Pass selected options as extra_args
             self.run_nsz_action('undupe', folder_path, extra_args=selected_options)
        else:
             self.log_signal.emit("[INFO] Unduplication cancelled by user.")

    def show_decompress_options(self, file_path):
        if not self.main_window or not getattr(self.main_window, 'output_folder_path', None):
             self.log_signal.emit("[ERROR] Output folder not selected.")
             return
        dialog = DecompressOptionsDialog(file_path, self)
        if dialog.exec():
             extra_options = dialog.get_selected_options()
             self.run_nsz_action('decompress', file_path, extra_args=extra_options)
        else:
             self.log_signal.emit("[INFO] Decompress action cancelled by user.")

    def show_extract_options(self, file_path):
        if not self.main_window or not getattr(self.main_window, 'output_folder_path', None):
             self.log_signal.emit("[ERROR] Output folder not selected.")
             return
        dialog = ExtractOptionsDialog(file_path, self)
        if dialog.exec():
             extra_options = dialog.get_selected_options()
             self.run_nsz_action('extract', file_path, extra_args=extra_options)
        else:
             self.log_signal.emit("[INFO] Extract action cancelled by user.")

    def run_nsz_action(self, action, file_path, extra_args=None):
        # Access the main window instance directly via the stored reference
        if not self.main_window:
            self.log_signal.emit("[ERROR] Internal error: MainWindow reference not found.")
            return
        output_folder = getattr(self.main_window, 'output_folder_path', None)

        args = ['nsz.py'] # Keep script name as first arg for sys.argv manipulation
        callback_signal = None # Default: no specific callback needed

        if action == 'compress':
            if not output_folder:
                self.log_signal.emit("[ERROR] Output folder not selected.")
                return
            args += ['-C', '-i', file_path, '-o', output_folder]
            if extra_args:
                 args.extend(extra_args)
        elif action == 'decompress':
            if not output_folder:
                self.log_signal.emit("[ERROR] Output folder not selected.")
                return
            args += ['-D', '-i', file_path, '-o', output_folder]
            if extra_args:
                 args.extend(extra_args)
        elif action == 'verify':
            args += ['--verify', file_path]
        elif action == 'info': # Regular info action (just log output)
            args += ['--info', file_path]
        elif action == 'titlekeys':
             # Assuming titlekeys takes the file path directly
             args += ['--titlekeys', file_path]
        elif action == 'extract':
            if not output_folder:
                self.log_signal.emit("[ERROR] Output folder not selected for extraction.")
                return
            args += ['--extract', '-i', file_path, '-o', output_folder]
            if extra_args:
                 args.extend(extra_args)
        elif action == 'info_for_rename': # Action to trigger info gathering for rename
            args += ['--info', file_path]
            callback_signal = self.info_result_signal # Use the specific signal for info results
        elif action == 'undupe': # Dedupe action (path is the folder)
             args += ['--undupe', file_path] # Changed from '--dedupe' to '--undupe'
             if extra_args:
                  args.extend(extra_args)
        else:
            self.log_signal.emit(f"Unknown action: {action}")
            return

        self.log_signal.emit(f"[NSZ] Running: {' '.join(args)} (subprocess)")
        thread_args = (args, file_path, callback_signal) # Pass file_path for context in callback
        threading.Thread(target=self.run_nsz_subprocess, args=thread_args).start()

    def run_nsz_subprocess(self, args, context_file_path=None, callback_signal=None):
        import subprocess
        import sys
        import os

        self.log_signal.emit(f"[DEBUG] run_nsz_subprocess started in thread: {threading.current_thread().name}")

        script_dir = os.path.dirname(__file__)
        # Correctly use the constant defined at the top
        nsz_script_path = str(NSZ_SCRIPT_PATH)

        command = [sys.executable, nsz_script_path] + args[1:]

        self.log_signal.emit(f"[DEBUG] Executing subprocess: {' '.join(command)}")

        result = None # Initialize result
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8')

            if result.stdout:
                self.log_signal.emit("--- NSZ Output ---")
                for line in result.stdout.splitlines():
                    self.log_signal.emit(line)
                self.log_signal.emit("------------------")

            if result.stderr:
                self.log_signal.emit("--- NSZ Error Output ---")
                for line in result.stderr.splitlines():
                    self.log_signal.emit(f"[ERROR] {line}")
                self.log_signal.emit("------------------------")

            if result.returncode != 0:
                self.log_signal.emit(f"[ERROR] nsz.py exited with code: {result.returncode}")
            else:
                self.log_signal.emit(f"[INFO] nsz.py completed successfully.")

            if callback_signal and result:
                 callback_signal.emit(context_file_path, result.stdout or "", result.stderr or "")

        except FileNotFoundError:
            self.log_signal.emit(f"[ERROR] Could not find nsz.py at: {nsz_script_path}")
        except Exception as e:
            self.log_signal.emit(f"[ERROR] Subprocess execution failed: {e}")

    @Slot(str, str, str)
    def handle_info_result(self, file_path, stdout, stderr):
        if not stdout or stderr:
            self.log_signal.emit(f"[ERROR] Failed to get info for {os.path.basename(file_path)} for renaming. Error: {stderr}")
            return

        self.log_signal.emit(f"[INFO] Parsing info for {os.path.basename(file_path)}...")
        title_id = None
        version = None
        current_section = None
        current_file = None
        is_cnmt = False
        is_cnmt_xml = False

        try:
            # Parse the output to find the CNMT Title ID and version
            for line in stdout.splitlines():
                line = line.strip()
                
                # Track which section we're in
                if line.startswith("NCA Archive"):
                    current_section = "nca"
                    is_cnmt = False
                elif line.startswith("File Path:"):
                    current_section = "file"
                    current_file = line.split("File Path:")[1].strip()
                    if current_file.endswith(".cnmt.nca"):
                        is_cnmt = True
                    elif current_file.endswith(".cnmt.xml"):
                        is_cnmt_xml = True
                elif line.startswith("Ticket"):
                    current_section = "ticket"
                
                # Get Title ID from CNMT NCA
                if current_section == "nca" and is_cnmt and "titleId = " in line:
                    title_id = line.split("titleId = ")[1].strip()
                    # Remove any whitespace or extra characters
                    title_id = title_id.strip()
                # Get version from CNMT XML
                elif current_section == "file" and is_cnmt_xml and "version=" in line:
                    version_str = line.split("version=")[1].strip()
                    if version_str.startswith('"'):
                        version_str = version_str.strip('"')
                    try:
                        version = str(int(version_str, 16))
                    except ValueError:
                        self.log_signal.emit(f"[WARNING] Could not parse version: {version_str}")
                        version = None

            if not title_id:
                # Try to get Title ID from ticket section as fallback
                for line in stdout.splitlines():
                    line = line.strip()
                    if line.startswith("titleId = "):
                        title_id = line.split("titleId = ")[1].strip()
                        break

            if not title_id:
                raise ValueError("TitleID not found in CNMT NCA or ticket output")

            # Format the version if we have one
            if version:
                version = version.lstrip('v').replace(' ', '_')
            
            # Extract the base name without any existing Title ID and version
            base_name = os.path.basename(file_path)
            # Remove any existing Title ID and version patterns
            base_name = re.sub(r'__[0-9A-Fa-f]{16}__v\d+.*$', '', base_name)
            base_name = re.sub(r'\[[0-9A-Fa-f]{16}\]\[v\d+\].*$', '', base_name)
            base_name = re.sub(r'\[[0-9A-Fa-f]{16}\].*$', '', base_name)
            base_name = base_name.rstrip('_')  # Remove trailing underscore if present
            base_name = base_name.strip()  # Remove any extra whitespace
            
            # Create new filename with proper format
            if version:
                new_name = f"{base_name} [{title_id}][v{version}]{os.path.splitext(file_path)[1]}"
            else:
                new_name = f"{base_name} [{title_id}]{os.path.splitext(file_path)[1]}"
                
            dir_name = os.path.dirname(file_path)
            new_path = os.path.join(dir_name, new_name)

            if file_path == new_path:
                self.log_signal.emit(f"[INFO] File '{os.path.basename(file_path)}' already has the correct name format.")
                return

            if os.path.exists(new_path):
                self.log_signal.emit(f"[ERROR] Target file '{new_name}' already exists. Skipping rename.")
                return

            self.log_signal.emit(f"[INFO] Renaming '{os.path.basename(file_path)}' to '{new_name}'")
            os.rename(file_path, new_path)
            self.log_signal.emit(f"[SUCCESS] Renamed to '{new_name}'")
            self.refresh() # Refresh list to show new name

        except Exception as e:
            self.log_signal.emit(f"[ERROR] Failed to parse info or rename '{os.path.basename(file_path)}': {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.keys_found_status = False # Track status
        self.settings = QSettings("YourOrgName", "SwitchFileManager") # Use appropriate names
        self.setWindowTitle("Switch File Manager NSZ GUI")
        self.setGeometry(100, 100, 1200, 800)
        # Check for key files
        self.check_key_files()

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Folder selection buttons
        folder_button_layout = QHBoxLayout()
        self.input_folder_button = QPushButton("Select Input Folder")
        self.output_folder_button = QPushButton("Select Output Folder")
        self.input_folder_button.clicked.connect(self.select_input_folder)
        self.output_folder_button.clicked.connect(self.select_output_folder)
        folder_button_layout.addWidget(self.input_folder_button)
        folder_button_layout.addWidget(self.output_folder_button)
        main_layout.addLayout(folder_button_layout)

        # Splitter for input/output areas
        splitter = QSplitter(Qt.Horizontal)
        
        # Input Area
        self.input_widget = FileTreeConsoleWidget(folder_type='Input', main_window=self)
        splitter.addWidget(self.input_widget)

        # Output Area
        self.output_widget = FileTreeConsoleWidget(folder_type='Output', main_window=self)
        splitter.addWidget(self.output_widget)
        
        splitter.setSizes([600, 600]) # Initial size distribution
        main_layout.addWidget(splitter)

        self.input_folder_path = ""
        self.output_folder_path = ""

        # Setup Status Bar
        self.key_status_label = QLabel("Key Status: Unknown")
        self.statusBar().addPermanentWidget(self.key_status_label) # Add to status bar (usually right side)
        self.update_key_status_label() # Set initial text/color
        # End Status Bar Setup

        # Load last used folders
        self.load_settings()

    def check_key_files(self):
        """Check for the existence of standard key files."""
        home_dir = Path.home()
        switch_dir = home_dir / '.switch'
        prod_keys_path = switch_dir / 'prod.keys'
        titlekeys_path = switch_dir / 'titlekeys.txt'
        self.keys_found_status = prod_keys_path.exists() or titlekeys_path.exists()

    def update_key_status_label(self):
        """Update the text and color of the key status label."""
        if self.keys_found_status:
            self.key_status_label.setText("Key Status: prod.keys or titlekeys.txt FOUND in ~/.switch/")
            self.key_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;") # Green
        else:
            self.key_status_label.setText("Key Status: prod.keys or titlekeys.txt NOT FOUND in ~/.switch/")
            self.key_status_label.setStyleSheet("color: #F44336; font-weight: bold;") # Red

    def load_settings(self):
        """Load last used folder paths from QSettings."""
        input_path = self.settings.value("lastInputFolder", "")
        if input_path and os.path.isdir(input_path):
            self.input_folder_path = input_path
            self.input_widget.set_folder(input_path)
            self.input_folder_button.setText(f"Input: ...{os.path.basename(input_path)}")

        output_path = self.settings.value("lastOutputFolder", "")
        if output_path and os.path.isdir(output_path):
            self.output_folder_path = output_path
            self.output_widget.set_folder(output_path)
            self.output_folder_button.setText(f"Output: ...{os.path.basename(output_path)}")

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_folder_path = folder
            self.input_widget.set_folder(folder)
            self.input_folder_button.setText(f"Input: ...{os.path.basename(folder)}")
            self.settings.setValue("lastInputFolder", folder) # Save setting
            # Optionally set output folder automatically if empty
            # if not self.output_folder_path:
            #     self.output_folder_path = os.path.join(folder, "output") # Example output subfolder
            #     if not os.path.exists(self.output_folder_path):
            #         os.makedirs(self.output_folder_path)
            #     self.output_widget.set_folder(self.output_folder_path)
            #     self.output_folder_button.setText(f"Output: ...{os.path.basename(self.output_folder_path)}")


    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_path = folder # Ensure path is updated first
            self.output_widget.set_folder(folder)
            self.output_folder_button.setText(f"Output: ...{os.path.basename(folder)}")
            self.settings.setValue("lastOutputFolder", folder) # Save setting

class UndupeOptionsDialog(QDialog):
    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        # Add undupe options UI elements here later
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Undupe functionality options placeholder."))
        # Example button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

class CompressOptionsDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compress Options")
        self.file_path = file_path
        
        layout = QFormLayout()
        
        # Compression level
        self.compression_level = QSpinBox()
        self.compression_level.setRange(1, 22)
        self.compression_level.setValue(12)
        layout.addRow("Compression Level:", self.compression_level)
        
        # Block size
        self.block_size = QComboBox()
        self.block_size.addItems(["128KB", "256KB", "512KB", "1MB", "2MB", "4MB"])
        self.block_size.setCurrentText("1MB")
        layout.addRow("Block Size:", self.block_size)
        
        # Verify after compression
        self.verify = QCheckBox("Verify after compression")
        self.verify.setChecked(True)
        layout.addRow(self.verify)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
    
    def get_selected_options(self):
        options = []
        # Add compression level
        options.extend(["-l", str(self.compression_level.value())])
        # Add block size
        block_size = self.block_size.currentText()
        block_size_kb = int(block_size.replace("KB", "").replace("MB", "000"))
        options.extend(["-s", str(block_size_kb)])
        # Add verify if checked
        if self.verify.isChecked():
            options.append("-V")
        return options

class ExtractOptionsDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extract Options")
        self.file_path = file_path
        
        layout = QFormLayout()
        
        # Extract all files
        self.extract_all = QCheckBox("Extract all files")
        self.extract_all.setChecked(True)
        layout.addRow(self.extract_all)
        
        # Verify after extraction
        self.verify = QCheckBox("Verify after extraction")
        self.verify.setChecked(True)
        layout.addRow(self.verify)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
    
    def get_selected_options(self):
        options = []
        # Add extract all if checked
        if self.extract_all.isChecked():
            options.append("--all")
        # Add verify if checked
        if self.verify.isChecked():
            options.append("--verify")
        return options

def main():
    app = QApplication(sys.argv)
    
    # Apply a dark theme (requires qt-material)
    try:
        import qt_material
        qt_material.apply_stylesheet(app, theme='dark_teal.xml')
    except ImportError:
        print("WARNING: qt-material not found, run 'pip install qt-material' for theming. Using default style.")
        
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
