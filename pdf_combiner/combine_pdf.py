import os
import sys
import json
import subprocess
import re
from datetime import datetime
from tkinter import filedialog, Tk, messagebox
from PyPDF2 import PdfMerger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Configuration file not found: {config_path}")
        print("   Using default settings...")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Error reading configuration: {e}")
        print("   Using default settings...")
        return {}

def generate_auto_filename(folder_path, config):
    """
    Generate automatic filename based on folder structure and configuration.
    
    Args:
        folder_path (str): Path to the folder containing PDFs
        config (dict): Configuration dictionary
    
    Returns:
        str: Generated filename with .pdf extension
    """
    auto_naming = config.get('output_settings', {}).get('auto_naming', {})
    
    if not auto_naming.get('enabled', False):
        return None
    
    # Try to extract project name from full path first
    project_name = extract_project_from_path(folder_path, auto_naming)
    
    if not project_name:
        # Fallback to folder name parsing
        folder_name = os.path.basename(folder_path)
        
        # Parse folder name using regex pattern
        folder_pattern = auto_naming.get('folder_pattern', '^(Ample_)?([^_]+)_([^_]+)$')
        match = re.match(folder_pattern, folder_name)
        
        if match:
            # Extract project name and issue type from folder name
            groups = match.groups()
            if len(groups) >= 2:
                # If pattern starts with Ample_, groups[0] will be "Ample_" or None
                if groups[0]:  # Ample_ prefix found
                    project_name = groups[1] if len(groups) > 1 else auto_naming.get('default_project_name', 'Project')
                else:  # No Ample_ prefix
                    project_name = groups[0] if groups[0] else auto_naming.get('default_project_name', 'Project')
            else:
                project_name = auto_naming.get('default_project_name', 'Project')
        else:
            # Fallback to defaults if pattern doesn't match
            project_name = auto_naming.get('default_project_name', 'Project')
    
    # Generate current date
    date_format = auto_naming.get('date_format', '%Y%m%d')
    current_date = datetime.now().strftime(date_format)
    
    # Build filename using structure
    structure = auto_naming.get('structure', 'Ample_{project_name}_{date}')
    
    filename = structure.format(
        project_name=project_name,
        date=current_date
    )
    
    # Clean filename (remove invalid characters)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'_+', '_', filename)  # Replace multiple underscores with single
    filename = filename.strip('_')  # Remove leading/trailing underscores
    
    # Add .pdf extension if not present
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    return filename

def extract_project_from_path(folder_path, auto_naming):
    """
    Extract project name from the full folder path using configured patterns.
    
    Args:
        folder_path (str): Full path to the folder
        auto_naming (dict): Auto-naming configuration
    
    Returns:
        str: Extracted project name or None
    """
    if not auto_naming.get('extract_from_path', False):
        return None
    
    path_patterns = auto_naming.get('path_patterns', [])
    
    for pattern_config in path_patterns:
        pattern = pattern_config.get('pattern', '')
        extract_type = pattern_config.get('extract', 'project_name')
        
        # Use the pattern directly since it's already configured for both separators
        pattern_regex = pattern
        print(f"[DEBUG] Trying pattern: {pattern_regex}")
        print(f"[DEBUG] Against path: {folder_path}")
        
        match = re.search(pattern_regex, folder_path, re.IGNORECASE)
        print(f"[DEBUG] Match found: {match is not None}")
        if match:
            groups = match.groups()
            print(f"[DEBUG] Groups: {groups}")
            
            if extract_type == 'project_name':
                # Extract the project name from the path
                if len(groups) >= 1:
                    project_name = groups[0]
                    # Clean up the project name - remove spaces, commas, and other special characters
                    project_name = re.sub(r'[<>:"/\\|?*,]', '_', project_name)  # Remove commas and other invalid chars
                    project_name = re.sub(r'\s+', '_', project_name)  # Replace spaces with underscores
                    project_name = re.sub(r'_+', '_', project_name)  # Replace multiple underscores with single
                    project_name = project_name.strip('_')  # Remove leading/trailing underscores
                    print(f"[DEBUG] Extracted project name: {project_name}")
                    return project_name
            
            elif extract_type == 'address':
                # Extract address components and format them
                if len(groups) >= 3:
                    street_number = groups[0]
                    street_name = groups[1]
                    suburb = groups[2]
                    postcode = groups[3] if len(groups) > 3 else ''
                    
                    # Format address as project name
                    address_format = auto_naming.get('address_format', '{street_number} {street_name}, {suburb}')
                    project_name = address_format.format(
                        street_number=street_number,
                        street_name=street_name,
                        suburb=suburb,
                        postcode=postcode
                    )
                    # Clean up the project name - remove spaces, commas, and other special characters
                    project_name = re.sub(r'[<>:"/\\|?*,]', '_', project_name)  # Remove commas and other invalid chars
                    project_name = re.sub(r'\s+', '_', project_name)  # Replace spaces with underscores
                    project_name = re.sub(r'_+', '_', project_name)  # Replace multiple underscores with single
                    project_name = project_name.strip('_')  # Remove leading/trailing underscores
                    print(f"[DEBUG] Extracted address as project name: {project_name}")
                    return project_name
    print("[DEBUG] No project name extracted from path.")
    return None

def select_folder():
    """Open a folder selection dialog and return the selected folder path."""
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select folder containing PDFs to combine")
    return folder_selected

def ask_open_pdf():
    """Ask user if they want to open the PDF after creation."""
    root = Tk()
    root.withdraw()
    result = messagebox.askyesno(
        "Open PDF", 
        "PDF file created successfully!\n\nWould you like to open it now?"
    )
    root.destroy()
    return result

def open_pdf_file(file_path):
    """Open a PDF file with the default system PDF viewer."""
    try:
        if sys.platform.startswith('win'):
            # Windows
            os.startfile(file_path)
        elif sys.platform.startswith('darwin'):
            # macOS
            subprocess.run(['open', file_path], check=True)
        else:
            # Linux
            subprocess.run(['xdg-open', file_path], check=True)
        print(f"📖 Opening PDF: {os.path.basename(file_path)}")
        return True
    except Exception as e:
        print(f"⚠️  Could not open PDF automatically: {e}")
        print(f"   You can manually open: {file_path}")
        return False

def combine_pdfs_in_folder(folder_path, output_filename=None, open_on_completion=None, ask_before_opening=True):
    """
    Combine all PDF files in the specified folder into a single PDF.
    
    Args:
        folder_path (str): Path to the folder containing PDF files
        output_filename (str): Name of the output file (optional, defaults to config or env var)
        open_on_completion (bool): Whether to open the PDF file after creation (None = use config)
        ask_before_opening (bool): Whether to ask user before opening
    """
    # Load configuration
    config = load_config()
    output_settings = config.get('output_settings', {})
    
    # Generate automatic filename if enabled and no output_filename provided
    if output_filename is None:
        auto_filename = generate_auto_filename(folder_path, config)
        if auto_filename:
            output_filename = auto_filename
            print(f"📝 Auto-generated filename: {output_filename}")
        else:
            # Fallback to config, environment variable, or use default
            output_filename = (output_settings.get('default_output_name') or 
                              os.getenv('COMBINED_PDF_OUTPUT_NAME', 'Combined_Output.pdf'))
    
    # Determine if we should open the PDF
    if open_on_completion is None:
        open_on_completion = output_settings.get('open_on_completion', False)
    
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
    if config.get('file_processing', {}).get('sort_by_name', True):
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
        
        # Handle opening the PDF
        should_open = open_on_completion
        if ask_before_opening and output_settings.get('ask_before_opening', True):
            should_open = ask_open_pdf()
        
        if should_open:
            open_pdf_file(output_path)
        
    except Exception as e:
        print(f"❌ Error combining PDFs: {str(e)}")
        merger.close()
        return

def main():
    """Main function to run the PDF combiner."""
    print("🔗 PDF Combiner Tool")
    print("=" * 30)
    
    # Check if folder path is provided as command line argument
    folder_path = None
    output_filename = None
    
    # Parse arguments
    args = sys.argv[1:]
    if args:
        folder_path = args[0]
        if not os.path.isdir(folder_path):
            print(f"❌ Error: '{folder_path}' is not a valid directory.")
            return
        # Check for custom filename flag
        if '--custom-name' in args:
            custom_index = args.index('--custom-name')
            if custom_index + 1 < len(args):
                output_filename = args[custom_index + 1]
    else:
        # Use GUI folder selector
        folder_path = select_folder()
        if not folder_path:
            print("No folder selected. Exiting.")
            return
    
    # Check for open flags
    open_on_completion = None
    ask_before_opening = True
    if '--open' in args or '-o' in args:
        open_on_completion = True
        ask_before_opening = False  # Force open without asking
    elif '--ask-open' in args or '-a' in args:
        open_on_completion = True
        ask_before_opening = True   # Ask before opening
    
    combine_pdfs_in_folder(folder_path, output_filename, open_on_completion, ask_before_opening)

if __name__ == "__main__":
    main()
