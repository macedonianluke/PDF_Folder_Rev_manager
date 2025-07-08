import os
import re
import datetime
from tkinter import Tk, filedialog
from odf.opendocument import OpenDocumentSpreadsheet, load
from odf.table import Table, TableRow, TableCell
from odf.text import P

ODS_FILENAME = "Drawing_Transmittal.ods"
TABLE_NAME = "Transmittal"

def select_folder():
    root = Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select folder with PDF drawings")

def parse_drawing_info(filename):
    # First try to match pattern with underscore and revision (e.g., W-A5-2_E.pdf)
    match = re.match(r'^(.+)_([A-Z])\.pdf$', filename)
    if match:
        return match.group(1), match.group(2)
    
    # If no underscore, treat as first issue (revision A) - remove .pdf extension
    if filename.lower().endswith('.pdf'):
        base_name = filename[:-4]  # Remove .pdf extension
        return base_name, 'A'
    
    return None, None

def get_existing_entries(doc):
    entries = set()
    for table in doc.spreadsheet.getElementsByType(Table):
        if table.getAttribute("name") == TABLE_NAME:
            for row in table.getElementsByType(TableRow)[1:]:  # skip header
                cells = row.getElementsByType(TableCell)
                if len(cells) >= 2:
                    # Extract text content safely
                    drawing_number = ""
                    revision = ""
                    
                    # Try to get drawing number
                    if cells[0].firstChild:
                        if hasattr(cells[0].firstChild, 'firstChild') and cells[0].firstChild.firstChild:
                            drawing_number = str(cells[0].firstChild.firstChild)
                        else:
                            drawing_number = str(cells[0].firstChild)
                    
                    # Try to get revision
                    if cells[1].firstChild:
                        if hasattr(cells[1].firstChild, 'firstChild') and cells[1].firstChild.firstChild:
                            revision = str(cells[1].firstChild.firstChild)
                        else:
                            revision = str(cells[1].firstChild)
                    
                    # Clean up the strings (remove XML tags if present)
                    drawing_number = re.sub(r'<[^>]+>', '', drawing_number).strip()
                    revision = re.sub(r'<[^>]+>', '', revision).strip()
                    
                    if drawing_number and revision:
                        entries.add((drawing_number, revision))
    return entries

def create_text_cell(value):
    cell = TableCell()
    cell.addElement(P(text=value))
    return cell

def create_new_sheet():
    doc = OpenDocumentSpreadsheet()
    table = Table(name=TABLE_NAME)
    header = TableRow()
    for heading in ["Drawing Number", "Revision", "File Name", "Issue Date", "Description"]:
        header.addElement(create_text_cell(heading))
    table.addElement(header)
    doc.spreadsheet.addElement(table)
    return doc, table

def get_or_create_doc(path):
    if os.path.exists(path):
        doc = load(path)
        for table in doc.spreadsheet.getElementsByType(Table):
            if table.getAttribute("name") == TABLE_NAME:
                return doc, table
        # Table not found, create it
        table = Table(name=TABLE_NAME)
        doc.spreadsheet.addElement(table)
        return doc, table
    else:
        return create_new_sheet()

def append_entries(doc, table, folder, existing_entries):
    added = 0
    today = datetime.date.today().isoformat()
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.pdf')])

    for f in files:
        base, rev = parse_drawing_info(f)
        if not base or not rev:
            print("Skipping invalid file:", f)
            continue

        if (base, rev) in existing_entries:
            continue

        row = TableRow()
        row.addElement(create_text_cell(base))
        row.addElement(create_text_cell(rev))
        row.addElement(create_text_cell(f))
        row.addElement(create_text_cell(today))
        row.addElement(create_text_cell("Auto-generated"))
        table.addElement(row)
        added += 1

    return added

def main():
    folder = select_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return

    ods_path = os.path.join(folder, ODS_FILENAME)
    doc, table = get_or_create_doc(ods_path)
    existing = get_existing_entries(doc)
    added_count = append_entries(doc, table, folder, existing)

    doc.save(ods_path)
    print("\n✅ Transmittal updated.")
    print("Added rows:", added_count)
    print("Saved to:", ods_path)

if __name__ == "__main__":
    main()
