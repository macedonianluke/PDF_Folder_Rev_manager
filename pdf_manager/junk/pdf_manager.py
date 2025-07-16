"""
PDF Revision Manager

This script helps organize PDF files by managing different revisions of the same document.
It identifies PDF files with revision letters (e.g., W-A5-2_A.pdf, W-A5-2_B.pdf, W-A5-2_C.pdf)
and keeps only the latest revision while moving older revisions to a 'Superceded' folder.

Key Features:
- Uses a GUI dialog to select the folder containing PDF files
- Parses filenames to extract base names and revision letters
- Groups files by their base name (e.g., 'W-A5-2')
- Sorts revisions alphabetically (A < B < C < ...)
- Keeps the highest revision letter in the original folder
- Moves all older revisions to a 'Superceded' subfolder
- Handles case-insensitive folder naming and creates folders as needed
- File filtering options: prefix-based or interactive selection
- Interactive GUI to select which files to process

Usage:
- Run the script and select a folder when prompted
- Choose filtering method: prefix-based or interactive selection
- The script will automatically organize PDF revisions
- Files not matching the expected pattern (base_revision.pdf) are skipped

Environment Variables (optional):
- DEFAULT_PDF_FOLDER: Default folder path
- SUPERCEDED_FOLDER_NAME: Name for the folder containing old revisions
- DEBUG: Enable debug output (True/False)
- LOG_LEVEL: Logging level (INFO, DEBUG, etc.)
- FILE_PREFIX_FILTER: Only process files starting with this prefix (e.g., "W-")
- INTERACTIVE_MODE: Force interactive file selection (True/False)

Example:
Input folder: /documents/
  - W-A5-2_A.pdf
  - W-A5-2_B.pdf  
  - W-A5-2_C.pdf
  - DOC-001_A.pdf
  - DOC-001_B.pdf

Output:
  /documents/
    - W-A5-2_C.pdf (latest kept)
    - DOC-001_B.pdf (latest kept)
    /Superceded/
      - W-A5-2_A.pdf (moved)
      - W-A5-2_B.pdf (moved)
      - DOC-001_A.pdf (moved)
"""

import os
import shutil
import re
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path

# Load environment variables if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_env_config():
    """Get configuration from environment variables"""
    return {
        'default_pdf_folder': os.getenv('DEFAULT_PDF_FOLDER', './pdfs'),
        'superceded_folder_name': os.getenv('SUPERCEDED_FOLDER_NAME', 'Superceded'),
        'debug': os.getenv('DEBUG', 'True').lower() == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'file_prefix_filter': os.getenv('FILE_PREFIX_FILTER', '').lower(),
        'interactive_mode': os.getenv('INTERACTIVE_MODE', 'False').lower() == 'true',
        'file_patterns': os.getenv('FILE_PATTERNS', '').split(',') if os.getenv('FILE_PATTERNS') else []
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
    if config['file_prefix_filter']:
        print(f"Prefix Filter: '{config['file_prefix_filter']}' (only files starting with this prefix)")
    else:
        print("Prefix Filter: None (all PDF files will be considered)")
    
    if config['file_patterns']:
        print(f"Custom Patterns: {len(config['file_patterns'])} pattern(s) defined")
        for i, pattern in enumerate(config['file_patterns']):
            print(f"  Pattern {i+1}: {pattern}")
    else:
        print("Custom Patterns: None (using default pattern)")
    
    if config['interactive_mode']:
        print("Interactive Mode: Enabled (you will select which files to process)")
    else:
        print("Interactive Mode: Disabled (automatic processing)")
    
    print("=" * 35)

def parse_filename(filename, patterns=None):
    """
    Extract base name and revision letter from filename using configurable patterns.
    
    Supported patterns:
    - Default: 'W-A5-2_E.pdf' -> ('W-A5-2', 'E')
    - LF pattern: 'LF_001_A.pdf' -> ('LF_001', 'A')
    - Custom patterns can be defined in FILE_PATTERNS environment variable
    
    Returns (base_name, revision) or (None, None) if no pattern matches.
    """
    if patterns is None:
        patterns = []
    
    # Default pattern (original behavior)
    default_patterns = [
        r'^(.+)_([A-Z])\.pdf$',  # Standard: base_revision.pdf
    ]
    
    # Add custom patterns from environment
    all_patterns = default_patterns + patterns
    
    for pattern in all_patterns:
        try:
            match = re.match(pattern, filename, re.IGNORECASE)
            if match:
                # Extract base name and revision
                if len(match.groups()) >= 2:
                    base_name = match.group(1)
                    revision = match.group(2)
                    return base_name, revision
                else:
                    # Handle patterns with different group structures
                    continue
        except re.error as e:
            print(f"Warning: Invalid regex pattern '{pattern}': {e}")
            continue
    
    return None, None

def get_predefined_patterns():
    """Get a dictionary of predefined patterns for common file naming conventions."""
    return {
        'standard': r'^(.+)_([A-Z])\.pdf$',
        'lf_format': r'^LF_(\d+)_([A-Z])\.pdf$',
        'doc_format': r'^DOC-(\d+)_([A-Z])\.pdf$',
        'drawing_format': r'^DWG-(\d+)_([A-Z])\.pdf$',
        'letter_number': r'^([A-Z]+)-(\d+)_([A-Z])\.pdf$',
        'simple_underscore': r'^(.+)_([A-Z])\.pdf$',
        'no_underscore': r'^(.+)([A-Z])\.pdf$',
        'space_separated': r'^(.+)\s+([A-Z])\.pdf$',
    }

def test_pattern(pattern, test_files):
    """Test a pattern against sample filenames and show results."""
    print(f"\nTesting pattern: {pattern}")
    print("-" * 50)
    
    for filename in test_files:
        base, rev = parse_filename(filename, [pattern])
        if base and rev:
            print(f"✓ {filename} -> Base: '{base}', Revision: '{rev}'")
        else:
            print(f"✗ {filename} -> No match")
    
    print("-" * 50)

def show_pattern_examples():
    """Show examples of common file patterns and how to configure them."""
    print("\n=== Pattern Examples ===")
    
    examples = [
        ("Standard format", "W-A5-2_A.pdf", r"^(.+)_([A-Z])\.pdf$"),
        ("LF format", "LF_001_A.pdf", r"^LF_(\d+)_([A-Z])\.pdf$"),
        ("DOC format", "DOC-001_A.pdf", r"^DOC-(\d+)_([A-Z])\.pdf$"),
        ("No underscore", "fileA.pdf", r"^(.+)([A-Z])\.pdf$"),
        ("Space separated", "file A.pdf", r"^(.+)\s+([A-Z])\.pdf$"),
    ]
    
    for desc, example, pattern in examples:
        print(f"\n{desc}:")
        print(f"  Example: {example}")
        print(f"  Pattern: {pattern}")
        base, rev = parse_filename(example, [pattern])
        if base and rev:
            print(f"  Result: Base='{base}', Revision='{rev}'")
        else:
            print(f"  Result: No match")
    
    print("\nTo use custom patterns, set FILE_PATTERNS environment variable:")
    print("FILE_PATTERNS=^LF_(\\d+)_([A-Z])\\.pdf$")
    print("=" * 35)

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
            
            # Add child items for individual files
            for rev, filename in rev_files:
                status = "Keep" if filename == latest_file else "Move"
                self.tree.insert(item, "end", text=f"  {filename}", values=("", status))
            
            # Check by default
            self.tree.item(item, tags=("checked",))
            self.selected_files.add(base_name)
        
        # Bind click events for selection
        self.tree.bind("<Button-1>", self.on_tree_click)
    
    def on_tree_click(self, event):
        """Handle treeview click events for selection."""
        region = self.tree.identify_region(event.x, event.y)
        if region == "tree":  # Only handle clicks on the tree column
            item = self.tree.identify_row(event.y)
            if item:
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
    config = get_env_config()
    
    if config['debug']:
        print(f"Debug mode: {config['debug']}")
        print(f"Log level: {config['log_level']}")
    
    # Show filtering configuration
    show_filtering_info(config)
    
    folder = select_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return

    superceded_dir = find_or_create_superceded_folder(folder, config['superceded_folder_name'])

    # Get all PDF files
    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in the selected folder.")
        return
    
    # Apply prefix filtering if specified
    if config['file_prefix_filter']:
        original_count = len(pdf_files)
        pdf_files = filter_files_by_prefix(pdf_files, config['file_prefix_filter'])
        filtered_count = len(pdf_files)
        print(f"Prefix filter '{config['file_prefix_filter']}' applied: {filtered_count}/{original_count} files match")
        
        if filtered_count == 0:
            print("No files match the specified prefix filter. Exiting.")
            return

    # Group files by base name
    grouped_files = defaultdict(list)
    skipped_files = []
    
    # Get custom patterns from config
    custom_patterns = config['file_patterns']
    if config['debug'] and custom_patterns:
        print(f"Using custom patterns: {custom_patterns}")

    for filename in pdf_files:
        base, rev = parse_filename(filename, custom_patterns)
        if base and rev:
            grouped_files[base].append((rev, filename))
        else:
            skipped_files.append(filename)

    if skipped_files:
        print("Skipping unrecognized files:", skipped_files)
        if config['debug']:
            print("Available patterns:")
            predefined = get_predefined_patterns()
            for name, pattern in predefined.items():
                print(f"  {name}: {pattern}")
            if custom_patterns:
                print("Custom patterns:")
                for i, pattern in enumerate(custom_patterns):
                    print(f"  custom_{i}: {pattern}")

    if not grouped_files:
        print("No files with valid revision patterns found. Exiting.")
        print("Tip: Use FILE_PATTERNS environment variable to define custom patterns.")
        
        # Show pattern examples to help user
        if config['debug']:
            show_pattern_examples()
        return

    # Determine which file groups to process
    selected_groups = None
    
    if config['interactive_mode'] or (not config['file_prefix_filter'] and len(grouped_files) > 1):
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
            
        # Sort by revision letter (A < B < C ...)
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