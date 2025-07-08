import os
import shutil
import re
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog

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

def main():
    folder = select_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return

    superseded_dir = os.path.join(folder, "superseded")
    if not os.path.exists(superseded_dir):
        os.makedirs(superseded_dir)

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
        # Keep the last one (highest rev)
        latest_rev, latest_file = rev_files[-1]

        for rev, file in rev_files[:-1]:
            source = os.path.join(folder, file)
            destination = os.path.join(superseded_dir, file)
            print("Moving old revision to superseded:", file)
            shutil.move(source, destination)
            moved_files.append(file)

        print("Keeping latest revision:", latest_file)
    
    print("\nCleanup complete.")
    print("Moved files:", moved_files if moved_files else "None")

if __name__ == "__main__":
    main()
