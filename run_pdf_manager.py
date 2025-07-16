#!/usr/bin/env python3
"""
Simple launcher for PDF Revision Manager
This script launches the PDF manager with the current configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the PDF manager"""
    print("🚀 PDF Revision Manager Launcher")
    print("=" * 40)
    
    # Check if PDF manager exists
    pdf_manager_path = Path("pdf_manager/pdf_manager_v2.py")
    if not pdf_manager_path.exists():
        print("❌ PDF manager not found!")
        print(f"   Expected location: {pdf_manager_path}")
        print("\n💡 Make sure you have run the setup script first:")
        print("   python setup_lf_config.py")
        return
    
    # Check if configuration exists
    config_path = Path("pdf_manager/config.json")
    if not config_path.exists():
        print("⚠️  PDF manager configuration not found!")
        print(f"   Expected location: {config_path}")
        print("\n💡 Run the setup script to create configuration:")
        print("   python setup_lf_config.py")
        
        response = input("\nContinue anyway? (y/N): ").lower().strip()
        if response != 'y':
            return
    
    # Launch the PDF manager
    print("🎯 Launching PDF Revision Manager...")
    print("=" * 40)
    
    try:
        # Run the PDF manager
        result = subprocess.run([sys.executable, str(pdf_manager_path)], 
                              cwd=os.getcwd())
        
        if result.returncode == 0:
            print("\n✅ PDF manager completed successfully")
        else:
            print(f"\n⚠️  PDF manager exited with code {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️  PDF manager interrupted by user")
    except Exception as e:
        print(f"\n❌ Error launching PDF manager: {e}")

if __name__ == "__main__":
    main() 