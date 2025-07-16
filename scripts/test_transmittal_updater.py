import unittest
import os
import shutil
from odf.opendocument import OpenDocumentSpreadsheet, load
from odf.table import Table, TableRow, TableCell
from odf.text import P

# Set the correct path to import from the parent directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.update_transmittal_matrix_refactored import TransmittalUpdater, create_transmittal_template
from scripts import config

class TestTransmittalUpdater(unittest.TestCase):
    """Test suite for the TransmittalUpdater class."""

    def setUp(self):
        """Set up a temporary environment for testing."""
        self.test_dir = "temp_test_folder"
        os.makedirs(self.test_dir, exist_ok=True)

        # Create a dummy ODS file for testing
        self.ods_path = os.path.join(self.test_dir, "test_transmittal.ods")
        doc = create_transmittal_template()
        doc.save(self.ods_path)

        # Create some dummy drawing files
        self.drawing_files = [
            "TEST-001_A.pdf",
            "TEST-002-B.dwg",
            "TEST-003.C.dxf",
            "TEST-001_B.pdf",  # Newer revision of TEST-001
            "invalid_file.txt",
        ]
        for filename in self.drawing_files:
            with open(os.path.join(self.test_dir, filename), "w") as f:
                f.write("dummy content")

    def tearDown(self):
        """Clean up the temporary environment after tests."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_scan_for_drawings(self):
        """Test the scanning of drawing files."""
        updater = TransmittalUpdater(self.test_dir, self.ods_path)
        issued_drawings = updater._scan_for_drawings()

        # Expecting 3 unique drawings, with TEST-001 at revision B
        self.assertEqual(len(issued_drawings), 3)
        self.assertIn("TEST-001", issued_drawings)
        self.assertEqual(issued_drawings["TEST-001"], ("B", "PDF"))
        self.assertIn("TEST-002", issued_drawings)
        self.assertEqual(issued_drawings["TEST-002"], ("B", "DWG"))
        self.assertIn("TEST-003", issued_drawings)
        self.assertEqual(issued_drawings["TEST-003"], ("C", "DXF"))

    def test_update_transmittal_new_column(self):
        """Test updating the transmittal with a new issue column."""
        updater = TransmittalUpdater(self.test_dir, self.ods_path)
        updater.update_transmittal("TP", "PDF, DWG")

        # Verify the ODS file was updated
        doc = load(self.ods_path)
        table = doc.spreadsheet.getElementsByType(Table)[0]
        rows = table.getElementsByType(TableRow)

        # Check header update
        date_row_idx, meta_row_idx = updater._find_header_rows()
        self.assertIsNotNone(date_row_idx)
        self.assertIsNotNone(meta_row_idx)

        date_row = rows[date_row_idx]
        meta_row = rows[meta_row_idx]
        self.assertIn("TP (PDF, DWG)", updater._get_cell_text(meta_row.getElementsByType(TableCell)[-1]))

        # Check drawing row update
        drawing_rows = {updater._get_cell_text(row.getElementsByType(TableCell)[0]): row for row in rows[meta_row_idx + 2:]}
        self.assertIn("TEST-001", drawing_rows)
        self.assertEqual(updater._get_cell_text(drawing_rows["TEST-001"].getElementsByType(TableCell)[-1]), "B")

    def test_full_run(self):
        """A full run test to simulate user actions."""
        # Simulate a full run: create updater, update transmittal
        updater = TransmittalUpdater(self.test_dir, self.ods_path)
        updater.update_transmittal("FC", "PDF")

        # First update done, now let's do a second one
        # Create a new drawing file
        with open(os.path.join(self.test_dir, "NEW-001_A.pdf"), "w") as f:
            f.write("new dummy content")
        
        # Update an existing one
        with open(os.path.join(self.test_dir, "TEST-001_C.pdf"), "w") as f:
            f.write("updated dummy content")

        updater2 = TransmittalUpdater(self.test_dir, self.ods_path)
        updater2.update_transmittal("REV", "PDF")

        # Verify the ODS file
        doc = load(self.ods_path)
        table = doc.spreadsheet.getElementsByType(Table)[0]
        rows = table.getElementsByType(TableRow)
        
        # Check headers for the updated column
        date_row_idx, meta_row_idx = updater2._find_header_rows()
        self.assertIsNotNone(date_row_idx)
        self.assertIsNotNone(meta_row_idx)

        meta_row = rows[meta_row_idx]
        meta_cells = meta_row.getElementsByType(TableCell)
        self.assertIn("REV (PDF)", updater2._get_cell_text(meta_cells[-1]))

        # Check drawing rows
        drawing_rows = {updater2._get_cell_text(row.getElementsByType(TableCell)[0]): row for row in rows[meta_row_idx + 2:]}
        self.assertIn("NEW-001", drawing_rows)
        self.assertEqual(updater2._get_cell_text(drawing_rows["NEW-001"].getElementsByType(TableCell)[-1]), "A")
        self.assertEqual(updater2._get_cell_text(drawing_rows["TEST-001"].getElementsByType(TableCell)[-1]), "C")

    def get_cell_text_from_cells(self, cells, index):
        """Helper to safely get text from a list of cells."""
        if index < len(cells):
            cell = cells[index]
            if not cell.firstChild:
                return ""
            if hasattr(cell.firstChild, 'data'):
                return cell.firstChild.data.strip()
            elif hasattr(cell.firstChild, 'firstChild') and cell.firstChild.firstChild:
                return str(cell.firstChild.firstChild).strip()
            else:
                return str(cell.firstChild).strip()
        return ""

if __name__ == '__main__':
    unittest.main()
