import os
import shutil
import re
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog
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
        'log_level': os.getenv('LOG_LEVEL', 'INFO')
    }

def select_folder():
    """Ask the user to select a folder using a GUI dialog."""
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select folder to clean PDF revisions")
    return folder_selected

def parse_filename(filename):
    """
    Extract base name and revision letter from filename.
    Example: 'W-A5-2_E.pdf' -> ('W-A5-2', 'E')
    Returns None if pattern doesn't match.
    """
    match = re.match(r'^(.+)_([A-Z])\.pdf$', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

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
    
    folder = select_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return

    superceded_dir = find_or_create_superceded_folder(folder, config['superceded_folder_name'])

    # Group files by base name
    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    grouped_files = defaultdict(list)

    for filename in pdf_files:
        base, rev = parse_filename(filename)
        if base and rev:
            grouped_files[base].append((rev, filename))
        else:
            print("Skipping unrecognized file:", filename)

    moved_files = []

    for base, rev_files in grouped_files.items():
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
    
    print("\nCleanup complete.")
    print("Moved files:", moved_files if moved_files else "None")

if __name__ == "__main__":
    main()