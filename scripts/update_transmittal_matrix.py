import os
import re
import datetime
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P

def prompt_issue_details():
    """Prompt user for issue details"""
    print("\n=== Drawing Transmittal Update ===")
    issue_code = input("Enter issue code (e.g. TP, REV, FC): ").strip().upper()
    if not issue_code:
        print("❌ Issue code is required!")
        return None, None
    
    formats = input("Enter formats issued (comma separated, e.g. PDF, DWG, DXF): ").strip().upper()
    if not formats:
        print("❌ Formats are required!")
        return None, None
    
    return issue_code, formats

def extract_drawing_info(filename):
    """Extract drawing number, revision, and format from filename"""
    # Support multiple filename patterns
    patterns = [
        r"^([A-Za-z0-9\-]+)_([A-Z])\.(pdf|dwg|dxf)$",  # A101_B.pdf
        r"^([A-Za-z0-9\-]+)-([A-Z])\.(pdf|dwg|dxf)$",  # A101-B.pdf
        r"^([A-Za-z0-9\-]+)\.([A-Z])\.(pdf|dwg|dxf)$", # A101.B.pdf
    ]
    
    for pattern in patterns:
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).upper(), match.group(3).upper()
    
    return None, None, None

def find_ods_file(folder_path):
    """Find .ods file in the folder, preferring Transmittal_Template.ods"""
    ods_files = []
    template_file = None
    
    for f in os.listdir(folder_path):
        if f.lower().endswith(".ods"):
            ods_files.append(f)
            if f.lower() == "transmittal_template.ods":
                template_file = os.path.join(folder_path, f)
    
    # Return template file if found, otherwise first .ods file
    if template_file:
        return template_file
    elif ods_files:
        return os.path.join(folder_path, ods_files[0])
    
    return None

def get_cell_text(cell):
    """Safely extract text content from a cell"""
    if not cell.firstChild:
        return ""
    
    # Handle different types of text elements
    if hasattr(cell.firstChild, 'data'):
        return cell.firstChild.data.strip()
    elif hasattr(cell.firstChild, 'firstChild') and cell.firstChild.firstChild:
        return str(cell.firstChild.firstChild).strip()
    else:
        return str(cell.firstChild).strip()

def debug_table_structure(table):
    """Debug function to show table structure"""
    rows = table.getElementsByType(TableRow)
    print(f"🔍 Debug: Table structure analysis")
    print(f"   Total rows: {len(rows)}")
    
    for i, row in enumerate(rows[:5]):  # Show first 5 rows
        cells = row.getElementsByType(TableCell)
        cell_texts = []
        for j, cell in enumerate(cells[:3]):  # Show first 3 cells
            text = get_cell_text(cell)
            cell_texts.append(f"Cell{j+1}:'{text}'")
        print(f"   Row {i+1}: {len(cells)} cells - {' | '.join(cell_texts)}")
    
    if len(rows) > 5:
        print(f"   ... and {len(rows) - 5} more rows")

def find_header_rows(table):
    """Hardcoded: Date row is 12 (index 11), Issue/meta row is 13 (index 12)"""
    rows = table.getElementsByType(TableRow)
    date_row_idx = 11  # Row 12 (0-based)
    meta_row_idx = 12  # Row 13 (0-based)
    return date_row_idx, meta_row_idx

def find_or_create_issue_column(table, issue_label, issue_meta):
    """Find existing column for this date or create new one"""
    rows = table.getElementsByType(TableRow)
    date_row_idx, meta_row_idx = find_header_rows(table)
    
    # Ensure we have enough rows
    while len(rows) <= meta_row_idx + 1:
        table.addElement(TableRow())
        rows = table.getElementsByType(TableRow)
    
    date_row = rows[date_row_idx]
    meta_row = rows[meta_row_idx]
    
    # Check if we already have a column for this date
    date_cells = date_row.getElementsByType(TableCell)
    for col_idx, cell in enumerate(date_cells):
        cell_text = get_cell_text(cell)
        if cell_text == issue_label:
            # Found existing column for this date, update the issue meta
            meta_cells = meta_row.getElementsByType(TableCell)
            if col_idx < len(meta_cells):
                # Clear existing content and update
                if meta_cells[col_idx].firstChild:
                    meta_cells[col_idx].removeChild(meta_cells[col_idx].firstChild)
                meta_cells[col_idx].addElement(P(text=issue_meta))
            print(f"📅 Using existing column for date: {issue_label}")
            return col_idx
    
    # Create new column if date not found
    print(f"📅 Creating new column for date: {issue_label}")
    
    # Add new cells to header rows
    date_cell = TableCell()
    date_cell.addElement(P(text=issue_label))
    date_row.addElement(date_cell)
    
    meta_cell = TableCell()
    meta_cell.addElement(P(text=issue_meta))
    meta_row.addElement(meta_cell)
    
    # Add empty cells to all data rows
    for i in range(meta_row_idx + 1, len(rows)):
        if i < len(rows):
            row = rows[i]
            # Ensure row has enough cells for drawing number and title
            while len(row.getElementsByType(TableCell)) < 2:
                row.addElement(TableCell())
            # Add cell for this issue
            row.addElement(TableCell())
    
    # Return the new column index
    return len(date_row.getElementsByType(TableCell)) - 1

def get_drawing_rows(table):
    """Get all drawing data rows from the table (start at row 14, index 13)"""
    rows = table.getElementsByType(TableRow)
    # Hardcoded: data matrix starts at row 14 (index 13)
    drawing_rows = {}
    for i in range(13, len(rows)):
        row = rows[i]
        cells = row.getElementsByType(TableCell)
        if cells:
            drawing_no = get_cell_text(cells[0])
            if drawing_no:  # Skip empty rows
                drawing_rows[drawing_no] = row
    return drawing_rows

def update_transmittal(ods_path, folder_path, issue_code, formats):
    """Update the transmittal matrix with new issue information"""
    try:
        print(f"📂 Loading transmittal file: {os.path.basename(ods_path)}")
        doc = load(ods_path)
        table = doc.spreadsheet.getElementsByType(Table)[0]
        
        # Debug: Show table structure
        debug_table_structure(table)
        
        # Create issue information
        today = datetime.date.today().strftime("%Y-%m-%d")
        issue_label = today
        issue_meta = f"{issue_code} ({formats})"
        
        print(f"📅 Adding issue: {issue_meta} for {today}")
        
        # Find or create column for this issue
        issue_column_idx = find_or_create_issue_column(table, issue_label, issue_meta)
        
        # Get existing drawing rows
        drawing_rows = get_drawing_rows(table)
        
        # Scan folder for drawing files
        print("🔍 Scanning for drawing files...")
        files = [f for f in os.listdir(folder_path) 
                if f.lower().endswith(('.pdf', '.dwg', '.dxf'))]
        
        issued_drawings = {}
        for f in files:
            drawing_no, rev, ext = extract_drawing_info(f)
            if drawing_no and rev:
                # Keep the highest revision if multiple files exist
                if drawing_no not in issued_drawings or rev > issued_drawings[drawing_no][0]:
                    issued_drawings[drawing_no] = (rev, ext)
                    print(f"  📄 Found: {drawing_no} Rev {rev} ({ext})")
        
        if not issued_drawings:
            print("⚠️  No valid drawing files found!")
            return
        
        # Update the matrix using the correct column index
        rows = table.getElementsByType(TableRow)
        _, meta_row_idx = find_header_rows(table)
        
        for drawing_no, (rev, ext) in issued_drawings.items():
            if drawing_no in drawing_rows:
                # Update existing row
                row = drawing_rows[drawing_no]
                cells = row.getElementsByType(TableCell)
                # Ensure we have enough cells up to the issue column
                while len(cells) <= issue_column_idx:
                    row.addElement(TableCell())
                    cells = row.getElementsByType(TableCell)
                # Update the cell in the correct column
                if cells[issue_column_idx].firstChild:
                    # Clear existing content and add new text
                    cells[issue_column_idx].removeChild(cells[issue_column_idx].firstChild)
                cells[issue_column_idx].addElement(P(text=rev))
                print(f"  ✅ Updated: {drawing_no} → Rev {rev} (Column {issue_column_idx + 1})")
            else:
                # Create new row
                print(f"  ➕ Adding new drawing: {drawing_no}")
                new_row = TableRow()
                # Add drawing number cell
                drawing_cell = TableCell()
                drawing_cell.addElement(P(text=drawing_no))
                new_row.addElement(drawing_cell)
                # Add title cell (empty)
                title_cell = TableCell()
                new_row.addElement(title_cell)
                # Fill empty cells up to the issue column
                for _ in range(issue_column_idx - 1):  # -1 because two cells already added
                    new_row.addElement(TableCell())
                # Add revision to the correct column
                rev_cell = TableCell()
                rev_cell.addElement(P(text=rev))
                new_row.addElement(rev_cell)
                # If there are more columns after, pad with empty cells to match header
                header_cells = len(rows[meta_row_idx].getElementsByType(TableCell))
                while len(new_row.getElementsByType(TableCell)) < header_cells:
                    new_row.addElement(TableCell())
                table.addElement(new_row)
        # Save the updated file
        doc.save(ods_path)
        print(f"\n✅ Transmittal updated successfully!")
        print(f"📊 Updated {len(issued_drawings)} drawings")
        print(f"📁 File saved: {os.path.basename(ods_path)}")
    except Exception as e:
        print(f"❌ Error updating transmittal: {str(e)}")
        raise

def create_transmittal_template():
    """Create a clean transmittal template"""
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
    
    doc = OpenDocumentSpreadsheet()
    table = Table(name="Transmittal")
    
    # Create header rows
    # Row 1: Project info (empty for now)
    project_row = TableRow()
    project_cell = TableCell()
    project_cell.addElement(P(text="PROJECT: "))
    project_row.addElement(project_cell)
    table.addElement(project_row)
    
    # Row 2: Empty
    table.addElement(TableRow())
    
    # Row 3: Title
    title_row = TableRow()
    title_cell = TableCell()
    title_cell.addElement(P(text="DRAWING TRANSMITTAL"))
    title_row.addElement(title_cell)
    table.addElement(title_row)
    
    # Row 4-10: Empty rows for spacing
    for _ in range(7):
        table.addElement(TableRow())
    
    # Row 11: Date row (will be populated with dates)
    date_row = TableRow()
    date_cell = TableCell()
    date_cell.addElement(P(text="Date"))
    date_row.addElement(date_cell)
    table.addElement(date_row)
    
    # Row 12: Issue row (will be populated with issue codes)
    issue_row = TableRow()
    issue_cell = TableCell()
    issue_cell.addElement(P(text="Issue"))
    issue_row.addElement(issue_cell)
    table.addElement(issue_row)
    
    # Row 13: Drawing number header
    drawing_header_row = TableRow()
    drawing_cell = TableCell()
    drawing_cell.addElement(P(text="Drawing No."))
    drawing_header_row.addElement(drawing_cell)
    
    title_cell = TableCell()
    title_cell.addElement(P(text="Title"))
    drawing_header_row.addElement(title_cell)
    table.addElement(drawing_header_row)
    
    doc.spreadsheet.addElement(table)
    return doc

def create_or_use_template(folder_path):
    """Create a new template or use existing one"""
    template_path = os.path.join(folder_path, "Transmittal_Template.ods")
    
    if os.path.exists(template_path):
        print(f"📄 Using existing template: Transmittal_Template.ods")
        return template_path
    else:
        print(f"📄 Creating new template: Transmittal_Template.ods")
        doc = create_transmittal_template()
        doc.save(template_path)
        return template_path

def select_folder():
    """Let user select a folder using file dialog"""
    try:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()  # Hide the main window
        folder = filedialog.askdirectory(title="Select folder containing drawing files and .ods file")
        root.destroy()
        return folder
    except ImportError:
        # Fallback if tkinter is not available
        print("📂 Please enter the full path to the folder containing your drawing files:")
        folder = input("Folder path: ").strip()
        if folder.startswith('"') and folder.endswith('"'):
            folder = folder[1:-1]  # Remove quotes if user added them
        return folder if os.path.isdir(folder) else None

def main():
    """Main function"""
    print("🧠 Drawing Transmittal Matrix Updater")
    print("=" * 40)
    
    # Let user select folder
    folder_path = select_folder()
    if not folder_path:
        print("❌ No folder selected. Exiting.")
        return
    
    if not os.path.isdir(folder_path):
        print(f"❌ Invalid folder path: {folder_path}")
        return
    
    print(f"📂 Selected folder: {folder_path}")
    
    # Check for template option
    print("\n📋 Template Options:")
    print("1. Use existing .ods file (if found)")
    print("2. Create/use Transmittal_Template.ods")
    
    template_choice = input("Choose option (1 or 2): ").strip()
    
    if template_choice == "2":
        # Use template
        ods_path = create_or_use_template(folder_path)
    else:
        # Find existing ODS file
        ods_path = find_ods_file(folder_path)
        if not ods_path:
            print("❌ No .ods file found in the selected folder!")
            print("   Please ensure there's a .ods file in the selected directory.")
            return
        print(f"📄 Found transmittal file: {os.path.basename(ods_path)}")
    
    # Get issue details
    issue_code, formats = prompt_issue_details()
    if not issue_code or not formats:
        return
    
    # Confirm before proceeding
    print(f"\n📋 Summary:")
    print(f"   Issue Code: {issue_code}")
    print(f"   Formats: {formats}")
    print(f"   Folder: {folder_path}")
    print(f"   File: {os.path.basename(ods_path)}")
    
    confirm = input("\nProceed with update? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Update cancelled.")
        return
    
    # Update the transmittal
    try:
        update_transmittal(ods_path, folder_path, issue_code, formats)
    except Exception as e:
        print(f"❌ Failed to update transmittal: {str(e)}")

if __name__ == "__main__":
    main()
