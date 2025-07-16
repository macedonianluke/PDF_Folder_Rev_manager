"""
PDF Revision Manager V3

This script helps organize PDF files by managing different revisions of the same document.
Updated to handle LF files with comparison logic:
- If file exists without revision letter AND with revision letter, keep the one WITH revision letter
- Move the older one (without revision letter) to Superceded

Key Features:
- Uses a GUI dialog to select the folder containing PDF files
- Parses filenames to extract base names and revision information
- Groups files by their base name (e.g., 'LF_A0-1')
- Compares files with and without revision letters
- Keeps files WITH revision letters over those without
- Moves older revisions to a 'Superceded' subfolder
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
                "file_patterns": ["^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$"]
            },
            "folder_settings": {
                "superceded_folder_name": "Superceded"
            },
            "logging": {
                "debug_mode": True,
                "log_level": "INFO"
            },
            "output_settings": {
                "open_on_completion": False,
                "ask_before_opening": True
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
    
    Handles two formats:
    - LF_A0-1_A.pdf -> ('LF_A0-1', 'A') (with revision letter)
    - LF_A0-1.pdf -> ('LF_A0-1', '') (without revision letter)
    
    Returns (base_name, revision) or (None, None) if no pattern matches.
    """
    if patterns is None:
        patterns = []
    
    # Pattern for files WITH revision letters
    revision_pattern = r'^(.+)_([A-Z])\.pdf$'
    
    # Try revision pattern first
    match = re.match(revision_pattern, filename, re.IGNORECASE)
    if match:
        base_name = match.group(1)
        revision = match.group(2)
        return base_name, revision
    
    # Pattern for files WITHOUT revision letters (LF files only)
    no_revision_pattern = r'^LF_([A-Z0-9\-]+)\.pdf$'
    match = re.match(no_revision_pattern, filename, re.IGNORECASE)
    if match:
        base_name = match.group(0).replace('.pdf', '')  # Full filename without extension
        revision = ''  # Empty revision indicates no revision letter
        return base_name, revision
    
    return None, None

def filter_files_by_prefix(files, prefix):
    """Filter files to only include those starting with the specified prefix."""
    if not prefix:
        return files
    return [f for f in files if f.lower().startswith(prefix.lower())]

def compare_and_group_files(files):
    """
    Compare files and group them by base name.
    If a file exists without revision letter AND with revision letter,
    prioritize the one WITH revision letter.
    """
    grouped_files = defaultdict(list)
    skipped_files = []
    
    for filename in files:
        base, rev = parse_filename(filename)
        if base and rev is not None:  # rev can be empty string for no revision
            grouped_files[base].append((rev, filename))
        else:
            skipped_files.append(filename)
    
    # Process each group to handle revision comparison
    final_groups = {}
    
    for base_name, rev_files in grouped_files.items():
        # Check if we have both types of files (with and without revision letters)
        files_with_revision = [(rev, filename) for rev, filename in rev_files if rev]
        files_without_revision = [(rev, filename) for rev, filename in rev_files if not rev]
        
        if files_with_revision and files_without_revision:
            # We have both types - keep the ones WITH revision letters
            print(f"📁 {base_name}: Found both types - keeping files WITH revision letters")
            print(f"   Files with revision: {[f[1] for f in files_with_revision]}")
            print(f"   Files without revision: {[f[1] for f in files_without_revision]} (will be moved)")
            
            # Sort revision files alphabetically and keep the latest
            files_with_revision.sort(key=lambda x: x[0])
            final_groups[base_name] = {
                'keep': files_with_revision[-1],  # Latest revision
                'move': files_without_revision + files_with_revision[:-1]  # All others
            }
        elif files_with_revision:
            # Only files with revision letters
            files_with_revision.sort(key=lambda x: x[0])
            final_groups[base_name] = {
                'keep': files_with_revision[-1],  # Latest revision
                'move': files_with_revision[:-1]  # Older revisions
            }
        elif files_without_revision:
            # Only files without revision letters
            files_without_revision.sort(key=lambda x: x[0])
            final_groups[base_name] = {
                'keep': files_without_revision[-1],  # Latest (alphabetical)
                'move': files_without_revision[:-1]  # Older
            }
    
    return final_groups, skipped_files

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
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"700x500+{x}+{y}")
        
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
        self.tree = ttk.Treeview(main_frame, columns=("keep", "move", "action"), show="tree headings", height=15)
        self.tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configure columns
        self.tree.heading("#0", text="Base Name")
        self.tree.heading("keep", text="Keep")
        self.tree.heading("move", text="Move")
        self.tree.heading("action", text="Action")
        
        self.tree.column("#0", width=150)
        self.tree.column("keep", width=200)
        self.tree.column("move", width=200)
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
        for base_name, group_info in self.grouped_files.items():
            keep_rev, keep_file = group_info['keep']
            move_files = [f[1] for f in group_info['move']]
            
            # Create file lists
            keep_text = keep_file
            move_text = ", ".join(move_files) if move_files else "None"
            
            # Determine action
            if move_files:
                action = f"Move {len(move_files)} files"
            else:
                action = "No action needed"
            
            # Insert into tree
            item = self.tree.insert("", "end", text=base_name, values=(keep_text, move_text, action))
            
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
        total_files_to_move = sum(len(group_info['move']) for base, group_info in self.grouped_files.items() if base in self.selected_files)
        
        summary = f"Selected {selected_groups} of {total_groups} file groups ({total_files_to_move} files to move)"
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

    # Group and compare files
    grouped_files, skipped_files = compare_and_group_files(pdf_files)

    if skipped_files:
        print("Skipping unrecognized files:", skipped_files)

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

    for base, group_info in grouped_files.items():
        if base not in selected_groups:
            print(f"Skipping unselected group: {base}")
            continue
            
        keep_rev, keep_file = group_info['keep']
        move_files = group_info['move']

        # Move files to superceded
        for rev, file in move_files:
            source = os.path.join(folder, file)
            destination = os.path.join(superceded_dir, file)
            print("Moving to Superceded:", file)
            shutil.move(source, destination)
            moved_files.append(file)

        print("Keeping:", keep_file)
        kept_files.append(keep_file)
    
    print("\nCleanup complete.")
    print(f"Kept files: {kept_files}")
    print(f"Moved files: {moved_files if moved_files else 'None'}")
    print(f"Total files processed: {len(kept_files) + len(moved_files)}")

if __name__ == "__main__":
    main() 