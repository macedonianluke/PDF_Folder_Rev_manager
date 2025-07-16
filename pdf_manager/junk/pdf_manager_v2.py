"""
PDF Revision Manager V2

This script helps organize PDF files by managing different revisions of the same document.
Updated to handle LF files without revision letters (e.g., LF_A0-1.pdf, LF_A1-1.pdf)

Key Features:
- Uses a GUI dialog to select the folder containing PDF files
- Parses filenames to extract base names and revision information
- Groups files by their base name (e.g., 'LF_A0-1')
- Sorts revisions by filename (alphabetical)
- Keeps the latest revision in the original folder
- Moves all older revisions to a 'Superceded' subfolder
- Handles case-insensitive folder naming and creates folders as needed
- File filtering options: prefix-based or interactive selection
- Interactive GUI to select which files to process
- JSON configuration support

Usage:
- Run the script and select a folder when prompted
- Choose filtering method: prefix-based or interactive selection
- The script will automatically organize PDF revisions
- Files not matching the expected pattern are skipped

Configuration:
- Uses JSON configuration files instead of environment variables
- Supports multiple file patterns
- Configurable prefix filters and interactive modes
"""

import os
import shutil
import re
import json
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path

def load_config():
    """Load configuration from JSON file"""
    config_path = "pdf_manager/config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return default config
        return {
            "file_processing": {
                "file_prefix_filter": "LF_",
                "interactive_mode": False,
                "file_patterns": ["^LF_([A-Z0-9\\-]+)\\.pdf$"]
            },
            "folder_settings": {
                "superceded_folder_name": "Superceded"
            },
            "logging": {
                "debug_mode": True,
                "log_level": "INFO"
            }
        }

def select_folder():
    """Ask the user to select a folder using a GUI dialog."""
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select folder to clean PDF revisions")
    return folder_selected

def show_filtering_info(config):
    """Show information about current filtering settings."""
    print("\n=== Filtering Configuration ===")
    file_processing = config.get('file_processing', {})
    
    if file_processing.get('file_prefix_filter'):
        print(f"Prefix Filter: '{file_processing['file_prefix_filter']}' (only files starting with this prefix)")
    else:
        print("Prefix Filter: None (all PDF files will be considered)")
    
    patterns = file_processing.get('file_patterns', [])
    if patterns:
        print(f"Custom Patterns: {len(patterns)} pattern(s) defined")
        for i, pattern in enumerate(patterns):
            print(f"  Pattern {i+1}: {pattern}")
    else:
        print("Custom Patterns: None (using default pattern)")
    
    if file_processing.get('interactive_mode'):
        print("Interactive Mode: Enabled (you will select which files to process)")
    else:
        print("Interactive Mode: Disabled (automatic processing)")
    
    print("=" * 35)

def parse_filename(filename, patterns=None):
    """
    Extract base name and revision information from filename using configurable patterns.
    
    Updated to handle files without revision letters:
    - LF_A0-1.pdf -> ('LF_A0-1', '1') (uses filename as base, '1' as revision)
    - LF_A1-2.pdf -> ('LF_A1-2', '2') (uses filename as base, '2' as revision)
    - LF_A0-3_A.pdf -> ('LF_A0-3', 'A') (standard format with revision letter)
    
    Returns (base_name, revision) or (None, None) if no pattern matches.
    """
    if patterns is None:
        patterns = []
    
    # Default patterns
    default_patterns = [
        r'^(.+)_([A-Z])\.pdf$',  # Standard: base_revision.pdf
        r'^(.+)\.pdf$',          # Simple: base.pdf (no revision letter)
    ]
    
    # Add custom patterns
    all_patterns = default_patterns + patterns
    
    for pattern in all_patterns:
        try:
            match = re.match(pattern, filename, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 2:
                    # Standard format: base_revision.pdf
                    base_name = groups[0]
                    revision = groups[1]
                    return base_name, revision
                elif len(groups) == 1:
                    # Simple format: base.pdf (no revision letter)
                    base_name = groups[0]
                    # Extract revision from the base name if possible
                    # For LF_A0-1.pdf, use '1' as revision
                    if '_' in base_name:
                        parts = base_name.split('_')
                        if len(parts) >= 2:
                            # Try to extract revision from last part
                            last_part = parts[-1]
                            if '-' in last_part:
                                revision_part = last_part.split('-')[-1]
                                if revision_part.isdigit():
                                    revision = revision_part
                                else:
                                    revision = last_part
                            else:
                                revision = last_part
                        else:
                            revision = base_name
                    else:
                        revision = base_name
                    
                    return base_name, revision
                    
        except re.error as e:
            print(f"Warning: Invalid regex pattern '{pattern}': {e}")
            continue
    
    return None, None

def filter_files_by_prefix(files, prefix):
    """Filter files to only include those starting with the specified prefix."""
    if not prefix:
        return files
    return [f for f in files if f.lower().startswith(prefix.lower())]

class FileSelectionDialog:
    """GUI dialog for selecting which files to process."""
    
    def __init__(self, parent, grouped_files):
        self.parent = parent
        self.grouped_files = grouped_files
        self.selected_files = set()
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Files to Process")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title label
        title_label = ttk.Label(main_frame, text="Select which file groups to process:", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Select None", command=self.select_none).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Invert Selection", command=self.invert_selection).pack(side=tk.LEFT)
        
        # Create treeview for file groups
        self.tree = ttk.Treeview(main_frame, columns=("files", "action"), show="tree headings", height=15)
        self.tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configure columns
        self.tree.heading("#0", text="Base Name")
        self.tree.heading("files", text="Files")
        self.tree.heading("action", text="Action")
        
        self.tree.column("#0", width=200)
        self.tree.column("files", width=250)
        self.tree.column("action", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure treeview styling
        style = ttk.Style()
        style.configure("Checked.Treeview", background="lightgreen")
        style.configure("Unchecked.Treeview", background="white")
        
        # Populate treeview
        self.populate_tree()
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Process Selected", command=self.process_selected).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
        # Summary label
        self.summary_label = ttk.Label(main_frame, text="")
        self.summary_label.grid(row=4, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)
        
        self.update_summary()
        
    def populate_tree(self):
        """Populate the treeview with file groups."""
        for base_name, rev_files in self.grouped_files.items():
            # Sort revisions
            rev_files.sort(key=lambda x: x[0])
            latest_rev, latest_file = rev_files[-1]
            
            # Create file list string
            file_list = ", ".join([f"{rev}_{rev_file.split('_')[-1]}" for rev, rev_file in rev_files])
            
            # Determine action
            if len(rev_files) > 1:
                action = f"Keep {latest_file}, move {len(rev_files)-1} others"
            else:
                action = "Keep (no older revisions)"
            
            # Insert into tree
            item = self.tree.insert("", "end", text=base_name, values=(file_list, action))
            
            # Select by default
            self.tree.item(item, tags=("checked",))
            self.selected_files.add(base_name)
        
        # Bind click event
        self.tree.bind("<Button-1>", self.on_tree_click)
        
    def on_tree_click(self, event):
        """Handle tree item clicks."""
        item = self.tree.selection()[0]
        base_name = self.tree.item(item, "text")
        
        current_tags = self.tree.item(item, "tags")
        if "checked" in current_tags:
            self.tree.item(item, tags=())
            self.selected_files.discard(base_name)
        else:
            self.tree.item(item, tags=("checked",))
            self.selected_files.add(base_name)
        
        self.update_summary()
    
    def select_all(self):
        """Select all file groups."""
        for item in self.tree.get_children():
            self.tree.item(item, tags=("checked",))
            self.selected_files.add(self.tree.item(item, "text"))
        self.update_summary()
    
    def select_none(self):
        """Deselect all file groups."""
        for item in self.tree.get_children():
            self.tree.item(item, tags=())
            self.selected_files.discard(self.tree.item(item, "text"))
        self.update_summary()
    
    def invert_selection(self):
        """Invert the current selection."""
        for item in self.tree.get_children():
            base_name = self.tree.item(item, "text")
            if base_name in self.selected_files:
                self.tree.item(item, tags=())
                self.selected_files.discard(base_name)
            else:
                self.tree.item(item, tags=("checked",))
                self.selected_files.add(base_name)
        self.update_summary()
    
    def update_summary(self):
        """Update the summary label."""
        total_groups = len(self.grouped_files)
        selected_groups = len(self.selected_files)
        total_files = sum(len(files) for files in self.grouped_files.values())
        
        summary = f"Selected {selected_groups} of {total_groups} file groups ({total_files} total files)"
        self.summary_label.config(text=summary)
    
    def process_selected(self):
        """Process the selected files."""
        self.result = list(self.selected_files)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the operation."""
        self.result = None
        self.dialog.destroy()

def find_or_create_superceded_folder(parent_folder, folder_name="Superceded"):
    """
    Find an existing 'Superceded' folder (any case), rename if necessary,
    or create a new one spelled exactly 'Superceded'.
    """
    for item in os.listdir(parent_folder):
        item_path = os.path.join(parent_folder, item)
        if os.path.isdir(item_path) and item.lower() == folder_name.lower():
            # Rename to ensure consistent casing
            corrected_path = os.path.join(parent_folder, folder_name)
            if item != folder_name:
                os.rename(item_path, corrected_path)
                print("Renamed existing folder to:", corrected_path)
            return corrected_path

    # Not found — create it
    new_path = os.path.join(parent_folder, folder_name)
    os.makedirs(new_path)
    print("Created new folder:", new_path)
    return new_path

def main():
    # Load configuration
    config = load_config()
    
    debug_mode = config.get('logging', {}).get('debug_mode', True)
    if debug_mode:
        print(f"Debug mode: {debug_mode}")
        print(f"Log level: {config.get('logging', {}).get('log_level', 'INFO')}")
    
    # Show filtering configuration
    show_filtering_info(config)
    
    folder = select_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return

    folder_settings = config.get('folder_settings', {})
    superceded_dir = find_or_create_superceded_folder(folder, folder_settings.get('superceded_folder_name', 'Superceded'))

    # Get all PDF files
    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in the selected folder.")
        return
    
    # Apply prefix filtering if specified
    file_processing = config.get('file_processing', {})
    prefix_filter = file_processing.get('file_prefix_filter', '')
    
    if prefix_filter:
        original_count = len(pdf_files)
        pdf_files = filter_files_by_prefix(pdf_files, prefix_filter)
        filtered_count = len(pdf_files)
        print(f"Prefix filter '{prefix_filter}' applied: {filtered_count}/{original_count} files match")
        
        if filtered_count == 0:
            print("No files match the specified prefix filter. Exiting.")
            return

    # Group files by base name
    grouped_files = defaultdict(list)
    skipped_files = []
    
    # Get custom patterns from config
    custom_patterns = file_processing.get('file_patterns', [])
    if debug_mode and custom_patterns:
        print(f"Using custom patterns: {custom_patterns}")

    for filename in pdf_files:
        base, rev = parse_filename(filename, custom_patterns)
        if base and rev:
            grouped_files[base].append((rev, filename))
        else:
            skipped_files.append(filename)

    if skipped_files:
        print("Skipping unrecognized files:", skipped_files)
        if debug_mode:
            print("Available patterns:")
            print("  simple: ^(.+)\.pdf$ (base.pdf)")
            print("  standard: ^(.+)_([A-Z])\.pdf$ (base_revision.pdf)")
            if custom_patterns:
                print("Custom patterns:")
                for i, pattern in enumerate(custom_patterns):
                    print(f"  custom_{i}: {pattern}")

    if not grouped_files:
        print("No files with valid revision patterns found. Exiting.")
        print("Tip: Check your file naming convention and update the configuration.")
        return

    # Determine which file groups to process
    selected_groups = None
    
    interactive_mode = file_processing.get('interactive_mode', False)
    if interactive_mode or (not prefix_filter and len(grouped_files) > 1):
        # Show interactive selection dialog
        root = tk.Tk()
        root.withdraw()
        
        dialog = FileSelectionDialog(root, grouped_files)
        root.wait_window(dialog.dialog)
        
        if dialog.result is None:
            print("Operation cancelled by user.")
            return
        
        selected_groups = set(dialog.result)
        print(f"User selected {len(selected_groups)} file groups to process")
    else:
        # Process all groups automatically
        selected_groups = set(grouped_files.keys())
        print(f"Processing all {len(selected_groups)} file groups automatically")

    # Process selected file groups
    moved_files = []
    kept_files = []

    for base, rev_files in grouped_files.items():
        if base not in selected_groups:
            print(f"Skipping unselected group: {base}")
            continue
            
        # Sort by revision (alphabetical)
        rev_files.sort(key=lambda x: x[0])
        latest_rev, latest_file = rev_files[-1]

        for rev, file in rev_files[:-1]:
            source = os.path.join(folder, file)
            destination = os.path.join(superceded_dir, file)
            print("Moving old revision to Superceded:", file)
            shutil.move(source, destination)
            moved_files.append(file)

        print("Keeping latest revision:", latest_file)
        kept_files.append(latest_file)
    
    print("\nCleanup complete.")
    print(f"Kept files: {kept_files}")
    print(f"Moved files: {moved_files if moved_files else 'None'}")
    print(f"Total files processed: {len(kept_files) + len(moved_files)}")

if __name__ == "__main__":
    main() 