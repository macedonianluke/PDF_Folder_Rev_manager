
# Configuration for update_transmittal_matrix_refactored.py

# Regex patterns for extracting drawing information from filenames
# Each pattern should capture: (drawing_number, revision, format)
FILENAME_PATTERNS = [
    r"^(.+)[_.-]([A-Z])\.(pdf|dwg|dxf)$",  # e.g., A101_B.pdf, A101-B.pdf, A101.B.pdf
]

# Keywords to identify header rows in the ODS file
HEADER_KEYWORDS = {
    "date_row": "Date",
    "issue_row": "Issue",
    "drawing_no_header": "Drawing No.",
}

# Default name for the transmittal template file
DEFAULT_TEMPLATE_NAME = "Transmittal_Template.ods"

# File extensions to scan for
DRAWING_FILE_EXTENSIONS = ('.pdf', '.dwg', '.dxf')
