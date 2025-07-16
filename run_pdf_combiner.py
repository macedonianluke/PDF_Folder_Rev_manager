#!/usr/bin/env python3
"""
Simple launcher for PDF Combiner Tool
This script launches the PDF combiner with options to open the generated PDF
"""

import os
import sys
import subprocess
from pathlib import Path
from tkinter import Tk, filedialog

def select_folder():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select folder containing PDFs to combine")
    root.destroy()
    return folder_selected

def main():
    """Launch the PDF combiner"""
    print("🔗 PDF Combiner Tool Launcher")
    print("=" * 40)
    
    # Check if PDF combiner exists
    pdf_combiner_path = Path("pdf_combiner/combine_pdf.py")
    if not pdf_combiner_path.exists():
        print("❌ PDF combiner not found!")
        print(f"   Expected location: {pdf_combiner_path}")
        return
    
    # Check if configuration exists
    config_path = Path("pdf_combiner/config.json")
    if not config_path.exists():
        print("⚠️  PDF combiner configuration not found!")
        print(f"   Expected location: {config_path}")
        print("\n💡 A default configuration will be used.")
    
    # Show auto-naming info
    print("\n📝 Auto-Naming Feature:")
    print("   • Automatically names PDFs based on folder structure")
    print("   • Format: Ample_ProjectName_IssueType_Date.pdf")
    print("   • Example: Ample_ProjectA_Design_20241201.pdf")
    print("   • Configure in pdf_combiner/config.json")
    
    # Show options
    print("\n📋 Available options:")
    print("   1. Combine PDFs (normal)")
    print("   2. Combine PDFs and open result")
    print("   3. Combine PDFs and ask before opening")
    print("   4. Combine PDFs with custom filename")
    print("   5. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                folder = select_folder()
                if not folder:
                    print("No folder selected. Exiting.")
                    return
                args = [sys.executable, str(pdf_combiner_path), folder]
                break
            elif choice == '2':
                folder = select_folder()
                if not folder:
                    print("No folder selected. Exiting.")
                    return
                args = [sys.executable, str(pdf_combiner_path), folder, '--open']
                break
            elif choice == '3':
                folder = select_folder()
                if not folder:
                    print("No folder selected. Exiting.")
                    return
                args = [sys.executable, str(pdf_combiner_path), folder, '--ask-open']
                break
            elif choice == '4':
                folder = select_folder()
                if not folder:
                    print("No folder selected. Exiting.")
                    return
                custom_name = input("Enter custom filename (without .pdf): ").strip()
                if custom_name:
                    if not custom_name.lower().endswith('.pdf'):
                        custom_name += '.pdf'
                    args = [sys.executable, str(pdf_combiner_path), folder, '--custom-name', custom_name]
                else:
                    print("❌ No filename provided. Using auto-naming.")
                    args = [sys.executable, str(pdf_combiner_path), folder]
                break
            elif choice == '5':
                print("👋 Goodbye!")
                return
            else:
                print("❌ Invalid choice. Please select 1-5.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return
    
    # Launch the PDF combiner
    print("\n🎯 Launching PDF Combiner...")
    print("=" * 40)
    
    try:
        # Run the PDF combiner
        result = subprocess.run(args, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("\n✅ PDF combiner completed successfully")
        else:
            print(f"\n⚠️  PDF combiner exited with code {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️  PDF combiner interrupted by user")
    except Exception as e:
        print(f"\n❌ Error launching PDF combiner: {e}")

if __name__ == "__main__":
    main() 