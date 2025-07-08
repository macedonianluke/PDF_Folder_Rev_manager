# PDF Folder Revision Manager

A Python tool for combining multiple PDF files in a folder into a single PDF, sorted alphabetically by filename.

## Features

- 🔗 Combines all PDF files in a selected folder
- 📝 Sorts files alphabetically by filename
- 📊 Generates ODS transmittal spreadsheets for LibreOffice
- 🖱️ GUI folder selection dialog
- ⚙️ Environment variable configuration
- 💻 Command-line interface support
- ✅ Error handling and progress feedback

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

### PDF Combination Tool

#### Method 1: GUI Interface (Recommended)
```bash
python scripts/combine_pdf.py
```
This will open a folder selection dialog where you can choose the folder containing your PDF files.

#### Method 2: Command Line
```bash
# Specify folder path directly
python scripts/combine_pdf.py "C:/path/to/your/pdf/folder"

# Specify folder path and output filename
python scripts/combine_pdf.py "C:/path/to/your/pdf/folder" "My_Output.pdf"
```

### ODS Transmittal Generator

Generate LibreOffice spreadsheets from PDF drawing files:

```bash
python scripts/generate_transmittal_ods.py
```

This tool:
- Extracts drawing numbers and revisions from PDF filenames (e.g., `W-A5-2_E.pdf` → Drawing: `W-A5-2`, Revision: `E`)
- Creates or updates `Drawing_Transmittal.ods` in the selected folder
- Prevents duplicate entries based on Drawing Number + Revision
- Includes columns for: Drawing Number, Revision, File Name, Issue Date, Description

## Configuration

You can configure the script using environment variables in a `.env` file:

- `COMBINED_PDF_OUTPUT_NAME`: Default output filename (defaults to "Combined_Output.pdf")

## Example Output

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