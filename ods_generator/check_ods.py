import sys
import os
from odf.opendocument import load

ods_path = r'C:\Users\User\Documents\GitHub\PDF_Folder_Rev_manager\sample_drawings\Transmittal_Template.ods'

try:
    doc = load(ods_path)
    print(f"Successfully loaded ODS file: {ods_path}")
    # You can add more checks here, e.g., print table names or cell content
except Exception as e:
    print(f"Error loading ODS file: {ods_path}")
    print(f"Error details: {e}")
    sys.exit(1)
