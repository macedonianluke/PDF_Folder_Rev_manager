# PDF Folder Revision Manager

A Python tool for managing PDF file revisions by keeping only the latest version and organizing older revisions into a "Superceded" folder.

## Features

- 📁 **Revision Management**: Automatically identifies and organizes PDF file revisions
- 🔍 **Smart Filtering**: Filter files by prefix or use interactive selection
- 🖱️ **GUI Interface**: User-friendly folder selection and file filtering dialogs
- 📊 **Visual Selection**: Interactive treeview to select which file groups to process
- ⚙️ **Flexible Configuration**: Environment variables for customization
- 🔄 **Automatic Organization**: Keeps latest revisions, moves older ones to "Superceded" folder
- ✅ **Error Handling**: Comprehensive error handling and progress feedback
- 📋 **File Pattern Recognition**: Recognizes revision patterns like `W-A5-2_A.pdf`, `W-A5-2_B.pdf`

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Create a `.env` file for configuration:
```bash
# Copy the content from env_example.txt to .env
COMBINED_PDF_OUTPUT_NAME=My_Combined_PDF.pdf
```

## Usage

### PDF Revision Manager

#### Basic Usage
```bash
python scripts/pdf_manage_1.py
```
This will open a folder selection dialog where you can choose the folder containing your PDF files.

#### File Filtering Options

**1. Prefix-based Filtering**
Set the `FILE_PREFIX_FILTER` environment variable to only process files starting with specific prefixes:

```bash
# Only process files starting with "W-"
FILE_PREFIX_FILTER=W-

# Only process files starting with "DOC-"
FILE_PREFIX_FILTER=DOC-
```

**2. Custom Pattern Recognition**
Use the `FILE_PATTERNS` environment variable to define custom regex patterns for different file naming conventions:

```bash
# Handle LF_ format files (e.g., LF_001_A.pdf)
FILE_PATTERNS=^LF_(\d+)_([A-Z])\.pdf$

# Handle multiple formats
FILE_PATTERNS=^LF_(\d+)_([A-Z])\.pdf$,^DOC-(\d+)_([A-Z])\.pdf$

# Handle files without underscores (e.g., fileA.pdf)
FILE_PATTERNS=^(.+)([A-Z])\.pdf$
```

**3. Interactive Selection**
Enable interactive mode to manually select which file groups to process:

```bash
# Always show file selection dialog
INTERACTIVE_MODE=True
```

#### Example Workflow

1. **Select Folder**: Choose the folder containing your PDF files
2. **Review Files**: The script identifies files with revision patterns
3. **Filter/Select**: Use prefix filtering, custom patterns, or interactive selection
4. **Process**: Automatically keeps latest revisions, moves older ones

#### Pattern Examples

| File Format | Example | Pattern |
|-------------|---------|---------|
| Standard | `W-A5-2_A.pdf` | `^(.+)_([A-Z])\.pdf$` |
| LF Format | `LF_001_A.pdf` | `^LF_(\d+)_([A-Z])\.pdf$` |
| DOC Format | `DOC-001_A.pdf` | `^DOC-(\d+)_([A-Z])\.pdf$` |
| No Underscore | `fileA.pdf` | `^(.+)([A-Z])\.pdf$` |
| Space Separated | `file A.pdf` | `^(.+)\s+([A-Z])\.pdf$` |

### Other Tools

#### PDF Combination Tool
```bash
python scripts/combine_pdf.py
```

#### ODS Transmittal Generator
```bash
python scripts/generate_transmittal_ods.py
```

## Configuration

You can configure the script using environment variables in a `.env` file:

### PDF Revision Manager
- `DEFAULT_PDF_FOLDER`: Default folder path (optional)
- `SUPERCEDED_FOLDER_NAME`: Name for the folder containing old revisions (default: "Superceded")
- `DEBUG`: Enable debug output (True/False)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)
- `FILE_PREFIX_FILTER`: Only process files starting with this prefix (e.g., "W-")
- `FILE_PATTERNS`: Custom regex patterns for file recognition (comma-separated)
- `INTERACTIVE_MODE`: Force interactive file selection (True/False)

### PDF Combination Tool
- `COMBINED_PDF_OUTPUT_NAME`: Default output filename (defaults to "Combined_Output.pdf")

## Example Output

### PDF Revision Manager
```
=== Filtering Configuration ===
Prefix Filter: 'W-' (only files starting with this prefix)
Custom Patterns: 1 pattern(s) defined
  Pattern 1: ^LF_(\d+)_([A-Z])\.pdf$
Interactive Mode: Disabled (automatic processing)
===================================

Prefix filter 'W-' applied: 3/5 files match
Using custom patterns: ['^LF_(\\d+)_([A-Z])\\.pdf$']
Skipping unrecognized files: ['other_file.pdf']
Processing all 3 file groups automatically

Moving old revision to Superceded: W-A5-2_A.pdf
Moving old revision to Superceded: W-A5-2_B.pdf
Keeping latest revision: W-A5-2_C.pdf
Moving old revision to Superceded: W-B1-1_A.pdf
Keeping latest revision: W-B1-1_B.pdf
Moving old revision to Superceded: LF_001_A.pdf
Keeping latest revision: LF_001_B.pdf

Cleanup complete.
Kept files: ['W-A5-2_C.pdf', 'W-B1-1_B.pdf', 'LF_001_B.pdf']
Moved files: ['W-A5-2_A.pdf', 'W-A5-2_B.pdf', 'W-B1-1_A.pdf', 'LF_001_A.pdf']
Total files processed: 7
```

### PDF Combination Tool
```
🔗 PDF Combiner Tool
==============================
Found 3 PDF files to combine:
  - document1.pdf
  - document2.pdf
  - document3.pdf
Adding: document1.pdf
Adding: document2.pdf
Adding: document3.pdf

✅ Successfully combined 3 PDF files!
📄 Combined PDF saved as: C:/path/to/folder/Combined_Output.pdf
```

## Requirements

- Python 3.6+
- PyPDF2
- odfpy (for ODS file handling)
- python-dotenv
- tkinter (included with Python)

## Notes

- The script combines PDFs in alphabetical order by filename
- The combined PDF is saved in the same folder as the source PDFs
- If a file with the same name already exists, it will be overwritten 