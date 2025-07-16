import os
import re
import datetime
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from typing import Optional, List, Tuple, Dict

try:
    from . import config
except ImportError:
    import config

class TransmittalUpdater:
    """A class to manage updating ODS transmittal files."""

    def __init__(self, folder_path: str, ods_path: str):
        """
        Initializes the TransmittalUpdater.

        Args:
            folder_path: The path to the folder containing drawing files.
            ods_path: The path to the ODS transmittal file.
        """
        self.folder_path = folder_path
        self.ods_path = ods_path
        self.doc = load(ods_path)
        self.table = self.doc.spreadsheet.getElementsByType(Table)[0]

    def update_transmittal(self, issue_code: str, formats: str):
        """
        Update the transmittal matrix with new issue information.
        """
        try:
            print(f"Loading transmittal file: {os.path.basename(self.ods_path)}")

            # Debug: Show table structure
            self._debug_table_structure()

            # Create issue information
            today = datetime.date.today().strftime("%Y-%m-%d")
            issue_label = today
            issue_meta = f"{issue_code} ({formats})"

            print(f"Adding issue: {issue_meta} for {today}")

            # Find or create column for this issue
            issue_column_idx = self._find_or_create_issue_column(issue_label, issue_meta)

            # Get existing drawing rows
            drawing_rows = self._get_drawing_rows()

            # Scan folder for drawing files
            print("Scanning for drawing files...")
            issued_drawings = self._scan_for_drawings()

            if not issued_drawings:
                print("Warning: No valid drawing files found!")
                return

            # Update the matrix
            self._update_matrix(issued_drawings, drawing_rows, issue_column_idx)

            # Save the updated file
            self.doc.save(self.ods_path)
            print(f"\nTransmittal updated successfully!")
            print(f"Updated {len(issued_drawings)} drawings")
            print(f"File saved: {os.path.basename(self.ods_path)}")

        except Exception as e:
            print(f"Error updating transmittal: {str(e)}")
            raise

    def _scan_for_drawings(self) -> Dict[str, Tuple[str, str]]:
        """Scans the folder for drawing files and extracts information."""
        files = [f for f in os.listdir(self.folder_path)
                 if f.lower().endswith(config.DRAWING_FILE_EXTENSIONS)]

        issued_drawings = {}
        for f in files:
            drawing_no, rev, ext = self._extract_drawing_info(f)
            if drawing_no and rev:
                if drawing_no not in issued_drawings or rev > issued_drawings[drawing_no][0]:
                    issued_drawings[drawing_no] = (rev, ext)
                    print(f"  Found: {drawing_no} Rev {rev} ({ext})")
        return issued_drawings

    def _extract_drawing_info(self, filename: str) -> Optional[Tuple[str, str, str]]:
        """Extract drawing number, revision, and format from filename."""
        for pattern in config.FILENAME_PATTERNS:
            match = re.match(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1), match.group(2).upper(), match.group(3).upper()
        return None, None, None

    def _get_cell_text(self, cell: TableCell) -> str:
        """Safely extract text content from a cell."""
        if not cell.firstChild:
            return ""
        if hasattr(cell.firstChild, 'data'):
            return cell.firstChild.data.strip()
        elif hasattr(cell.firstChild, 'firstChild') and cell.firstChild.firstChild:
            return str(cell.firstChild.firstChild).strip()
        else:
            return str(cell.firstChild).strip()

    def _debug_table_structure(self):
        """Debug function to show table structure."""
        rows = self.table.getElementsByType(TableRow)
        print(f"Debug: Table structure analysis")
        print(f"   Total rows: {len(rows)}")

        for i, row in enumerate(rows[:5]):
            cells = row.getElementsByType(TableCell)
            cell_texts = [f"Cell{j+1}:'{self._get_cell_text(cell)}'" for j, cell in enumerate(cells[:3])]
            print(f"   Row {i+1}: {len(cells)} cells - {' | '.join(cell_texts)}")

        if len(rows) > 5:
            print(f"   ... and {len(rows) - 5} more rows")

    def _find_header_rows(self) -> Tuple[Optional[int], Optional[int]]:
        """Find the row indices for the date and issue headers."""
        rows = self.table.getElementsByType(TableRow)
        date_row_idx, meta_row_idx = None, None
        for i, row in enumerate(rows):
            cells = row.getElementsByType(TableCell)
            if cells:
                cell_text = self._get_cell_text(cells[0])
                if cell_text == config.HEADER_KEYWORDS["date_row"]:
                    date_row_idx = i
                elif cell_text == config.HEADER_KEYWORDS["issue_row"]:
                    meta_row_idx = i
        return date_row_idx, meta_row_idx

    def _find_or_create_issue_column(self, issue_label: str, issue_meta: str) -> int:
        """Find existing column for this date or create new one."""
        rows = self.table.getElementsByType(TableRow)
        date_row_idx, meta_row_idx = self._find_header_rows()

        if date_row_idx is None or meta_row_idx is None:
            raise ValueError("Could not find header rows in the transmittal file.")

        while len(rows) <= meta_row_idx + 1:
            self.table.addElement(TableRow())
            rows = self.table.getElementsByType(TableRow)

        date_row = rows[date_row_idx]
        meta_row = rows[meta_row_idx]

        date_cells = date_row.getElementsByType(TableCell)
        for col_idx, cell in enumerate(date_cells):
            if self._get_cell_text(cell) == issue_label:
                meta_cells = meta_row.getElementsByType(TableCell)
                if col_idx < len(meta_cells):
                    if meta_cells[col_idx].firstChild:
                        meta_cells[col_idx].removeChild(meta_cells[col_idx].firstChild)
                    meta_cells[col_idx].addElement(P(text=issue_meta))
                print(f"Using existing column for date: {issue_label}")
                return col_idx

        print(f"Creating new column for date: {issue_label}")
        date_cell = TableCell()
        date_cell.addElement(P(text=issue_label))
        date_row.addElement(date_cell)

        meta_cell = TableCell()
        meta_cell.addElement(P(text=issue_meta))
        meta_row.addElement(meta_cell)

        for i in range(meta_row_idx + 1, len(rows)):
            if i < len(rows):
                rows[i].addElement(TableCell())

        return len(date_row.getElementsByType(TableCell)) - 1

    def _get_drawing_rows(self) -> Dict[str, TableRow]:
        """Get all drawing data rows from the table."""
        rows = self.table.getElementsByType(TableRow)
        _, meta_row_idx = self._find_header_rows()
        if meta_row_idx is None:
            return {}
            
        drawing_rows = {}
        for i in range(meta_row_idx + 1, len(rows)):
            row = rows[i]
            cells = row.getElementsByType(TableCell)
            if cells:
                drawing_no = self._get_cell_text(cells[0])
                if drawing_no and drawing_no != config.HEADER_KEYWORDS["drawing_no_header"]:
                    drawing_rows[drawing_no] = row
        return drawing_rows

    def _update_matrix(self, issued_drawings: Dict[str, Tuple[str, str]], drawing_rows: Dict[str, TableRow], issue_column_idx: int):
        """Updates the transmittal matrix with the drawing information."""
        rows = self.table.getElementsByType(TableRow)
        _, meta_row_idx = self._find_header_rows()
        if meta_row_idx is None:
            return

        for drawing_no, (rev, ext) in issued_drawings.items():
            if drawing_no in drawing_rows:
                row = drawing_rows[drawing_no]
                cells = row.getElementsByType(TableCell)
                while len(cells) <= issue_column_idx:
                    row.addElement(TableCell())
                    cells = row.getElementsByType(TableCell)
                if cells[issue_column_idx].firstChild:
                    cells[issue_column_idx].removeChild(cells[issue_column_idx].firstChild)
                cells[issue_column_idx].addElement(P(text=rev))
                print(f"  Updated: {drawing_no} -> Rev {rev} (Column {issue_column_idx + 1})")
            else:
                print(f"  Adding new drawing: {drawing_no}")
                new_row = TableRow()
                drawing_cell = TableCell()
                drawing_cell.addElement(P(text=drawing_no))
                new_row.addElement(drawing_cell)
                # Add empty cells for title and up to the issue column
                for _ in range(issue_column_idx):
                    new_row.addElement(TableCell())
                rev_cell = new_row.getElementsByType(TableCell)[-1]
                rev_cell.addElement(P(text=rev))

                # Ensure row has same number of cells as header
                header_cells = len(rows[meta_row_idx].getElementsByType(TableCell))
                while len(new_row.getElementsByType(TableCell)) < header_cells:
                    new_row.addElement(TableCell())
                self.table.addElement(new_row)


def prompt_issue_details() -> Optional[Tuple[str, str]]:
    """Prompt user for issue details."""
    print("\n=== Drawing Transmittal Update ===")
    issue_code = input("Enter issue code (e.g. TP, REV, FC): ").strip().upper()
    if not issue_code:
        print("Error: Issue code is required!")
        return None
    formats = input("Enter formats issued (comma separated, e.g. PDF, DWG, DXF): ").strip().upper()
    if not formats:
        print("Error: Formats are required!")
        return None
    return issue_code, formats


def find_ods_file(folder_path: str) -> Optional[str]:
    """Find .ods file in the folder, preferring the default template name."""
    ods_files = []
    template_file = None
    for f in os.listdir(folder_path):
        if f.lower().endswith(".ods"):
            ods_files.append(f)
            if f.lower() == config.DEFAULT_TEMPLATE_NAME.lower():
                template_file = os.path.join(folder_path, f)
    if template_file:
        return template_file
    elif ods_files:
        return os.path.join(folder_path, ods_files[0])
    return None


def create_transmittal_template() -> 'OpenDocumentSpreadsheet':
    """Create a clean transmittal template."""
    from odf.opendocument import OpenDocumentSpreadsheet
    doc = OpenDocumentSpreadsheet()
    table = Table(name="Transmittal")
    
    project_row = TableRow()
    project_cell = TableCell()
    project_cell.addElement(P(text="PROJECT: "))
    project_row.addElement(project_cell)
    table.addElement(project_row)
    
    table.addElement(TableRow())
    
    title_row = TableRow()
    title_cell = TableCell()
    title_cell.addElement(P(text="DRAWING TRANSMITTAL"))
    title_row.addElement(title_cell)
    table.addElement(title_row)
    
    for _ in range(7):
        table.addElement(TableRow())
        
    date_row = TableRow()
    date_cell = TableCell()
    date_cell.addElement(P(text=config.HEADER_KEYWORDS["date_row"]))
    date_row.addElement(date_cell)
    table.addElement(date_row)
    
    issue_row = TableRow()
    issue_cell = TableCell()
    issue_cell.addElement(P(text=config.HEADER_KEYWORDS["issue_row"]))
    issue_row.addElement(issue_cell)
    table.addElement(issue_row)
    
    drawing_header_row = TableRow()
    drawing_cell = TableCell()
    drawing_cell.addElement(P(text=config.HEADER_KEYWORDS["drawing_no_header"]))
    drawing_header_row.addElement(drawing_cell)
    
    title_cell = TableCell()
    title_cell.addElement(P(text="Title"))
    drawing_header_row.addElement(title_cell)
    table.addElement(drawing_header_row)
    
    doc.spreadsheet.addElement(table)
    return doc


def create_or_use_template(folder_path: str) -> str:
    """Create a new template or use existing one."""
    template_path = os.path.join(folder_path, config.DEFAULT_TEMPLATE_NAME)
    if os.path.exists(template_path):
        print(f"Using existing template: {config.DEFAULT_TEMPLATE_NAME}")
        return template_path
    else:
        print(f"Creating new template: {config.DEFAULT_TEMPLATE_NAME}")
        doc = create_transmittal_template()
        doc.save(template_path)
        return template_path


def select_folder() -> Optional[str]:
    """Let user select a folder using file dialog."""
    try:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select folder containing drawing files and .ods file")
        root.destroy()
        return folder
    except ImportError:
        print("Please enter the full path to the folder containing your drawing files:")
        folder = input("Folder path: ").strip()
        if folder.startswith('"') and folder.endswith('"'):
            folder = folder[1:-1]
        return folder if os.path.isdir(folder) else None


def main():
    """Main function."""
    print("Drawing Transmittal Matrix Updater")
    print("=" * 40)

    folder_path = select_folder()
    if not folder_path:
        print("Error: No folder selected. Exiting.")
        return

    if not os.path.isdir(folder_path):
        print(f"Error: Invalid folder path: {folder_path}")
        return

    print(f"Selected folder: {folder_path}")

    print("\nTemplate Options:")
    print("1. Use existing .ods file (if found)")
    print(f"2. Create/use {config.DEFAULT_TEMPLATE_NAME}")

    template_choice = input("Choose option (1 or 2): ").strip()

    if template_choice == "2":
        ods_path = create_or_use_template(folder_path)
    else:
        ods_path = find_ods_file(folder_path)
        if not ods_path:
            print("Error: No .ods file found in the selected folder!")
            print("   Please ensure there's a .ods file in the selected directory.")
            return
        print(f"Found transmittal file: {os.path.basename(ods_path)}")

    issue_details = prompt_issue_details()
    if not issue_details:
        return
    issue_code, formats = issue_details

    print(f"\nSummary:")
    print(f"   Issue Code: {issue_code}")
    print(f"   Formats: {formats}")
    print(f"   Folder: {folder_path}")
    print(f"   File: {os.path.basename(ods_path)}")

    confirm = input("\nProceed with update? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Update cancelled.")
        return

    try:
        updater = TransmittalUpdater(folder_path, ods_path)
        updater.update_transmittal(issue_code, formats)
    except Exception as e:
        print(f"Failed to update transmittal: {str(e)}")

if __name__ == "__main__":
    main()


