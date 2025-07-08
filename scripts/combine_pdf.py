import os
import sys
from tkinter import filedialog, Tk
from PyPDF2 import PdfMerger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def select_folder():
    """Open a folder selection dialog and return the selected folder path."""
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select folder containing PDFs to combine")
    return folder_selected

def combine_pdfs_in_folder(folder_path, output_filename=None):
    """
    Combine all PDF files in the specified folder into a single PDF.
    
    Args:
        folder_path (str): Path to the folder containing PDF files
        output_filename (str): Name of the output file (optional, defaults to env var or "Combined_Output.pdf")
    """
    # Get output filename from environment variable or use default
    if output_filename is None:
        output_filename = os.getenv('COMBINED_PDF_OUTPUT_NAME', 'Combined_Output.pdf')
    
    # Get PDF files from the folder
    try:
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    except FileNotFoundError:
        print(f"❌ Error: Folder '{folder_path}' not found.")
        return
    except PermissionError:
        print(f"❌ Error: Permission denied accessing folder '{folder_path}'.")
        return
    
    if not pdf_files:
        print("No PDF files found in the selected folder.")
        return

    # Sort files alphabetically (by filename)
    pdf_files.sort()
    print(f"Found {len(pdf_files)} PDF files to combine:")
    for pdf in pdf_files:
        print(f"  - {pdf}")

    # Combine PDFs
    merger = PdfMerger()
    try:
        for pdf in pdf_files:
            full_path = os.path.join(folder_path, pdf)
            print(f"Adding: {pdf}")
            merger.append(full_path)

        output_path = os.path.join(folder_path, output_filename)
        merger.write(output_path)
        merger.close()

        print(f"\n✅ Successfully combined {len(pdf_files)} PDF files!")
        print(f"📄 Combined PDF saved as: {output_path}")
        
    except Exception as e:
        print(f"❌ Error combining PDFs: {str(e)}")
        merger.close()
        return

def main():
    """Main function to run the PDF combiner."""
    print("🔗 PDF Combiner Tool")
    print("=" * 30)
    
    # Check if folder path is provided as command line argument
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if not os.path.isdir(folder_path):
            print(f"❌ Error: '{folder_path}' is not a valid directory.")
            return
    else:
        # Use GUI folder selector
        folder_path = select_folder()
        if not folder_path:
            print("No folder selected. Exiting.")
            return
    
    # Get output filename from command line or environment
    output_filename = None
    if len(sys.argv) > 2:
        output_filename = sys.argv[2]
    
    combine_pdfs_in_folder(folder_path, output_filename)

if __name__ == "__main__":
    main()
