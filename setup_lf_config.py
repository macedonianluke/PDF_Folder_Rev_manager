#!/usr/bin/env python3
"""
Setup script to configure PDF Revision Manager for LF_A0-3 format files
This script uses JSON configuration files instead of .env files.
"""

import os
import sys
from pathlib import Path

# Add configs directory to path
sys.path.append('configs')
from config_manager import ConfigManager

def setup_lf_configuration():
    """Setup configuration for LF_A0-3 files using JSON config"""
    
    print("🔧 PDF Revision Manager - LF_A0-3 Configuration Setup")
    print("=" * 60)
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Check if main config exists
    if not config_manager.config:
        print("❌ Main configuration not found. Please ensure configs/main_config.json exists.")
        return False
    
    # Update PDF manager config for LF format
    lf_updates = {
        "file_processing": {
            "file_prefix_filter": "LF_",
            "interactive_mode": False,
            "file_patterns": ["^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$"]
        },
        "logging": {
            "debug_mode": True,
            "log_level": "INFO"
        }
    }
    
    success = config_manager.update_script_config("pdf_manager", lf_updates)
    
    if success:
        print("\n✅ LF_A0-3 configuration applied successfully!")
        show_configuration_info()
        test_lf_pattern()
        show_usage_instructions()
    else:
        print("❌ Failed to apply LF configuration")
    
    return success

def show_configuration_info():
    """Show what configuration was created"""
    print("\n📋 Configuration created:")
    print("=" * 40)
    print("• File prefix filter: 'LF_'")
    print("• File pattern: ^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$")
    print("• Interactive mode: Disabled")
    print("• Debug mode: Enabled")
    
    print("\n🎯 This configuration will recognize:")
    print("• LF_A0-3_A.pdf → Base: 'A0-3', Revision: 'A'")
    print("• LF_A0-3_B.pdf → Base: 'A0-3', Revision: 'B'")
    print("• LF_B1-5_C.pdf → Base: 'B1-5', Revision: 'C'")
    print("• LF_C2-8_A.pdf → Base: 'C2-8', Revision: 'A'")

def test_lf_pattern():
    """Test the LF pattern with sample files"""
    print("\n🧪 Testing LF pattern recognition...")
    print("-" * 50)
    
    # Import the parse function from the main script
    sys.path.append('pdf_manager')
    try:
        from pdf_manager import parse_filename
        
        test_files = [
            "LF_A0-3_A.pdf",
            "LF_A0-3_B.pdf", 
            "LF_B1-5_C.pdf",
            "LF_C2-8_A.pdf",
            "other_file.pdf",  # Should not match
            "LF_invalid.pdf"   # Should not match
        ]
        
        pattern = r"^LF_([A-Z0-9\-]+)_([A-Z])\.pdf$"
        
        for filename in test_files:
            base, rev = parse_filename(filename, [pattern])
            if base and rev:
                print(f"✅ {filename} → Base: '{base}', Revision: '{rev}'")
            else:
                print(f"❌ {filename} → No match")
        
        print("-" * 50)
    except ImportError:
        print("⚠️  Could not import pdf_manager module for testing")
        print("   Make sure pdf_manager/pdf_manager.py exists")

def show_usage_instructions():
    """Show how to use the configured system"""
    print("\n📖 Usage Instructions:")
    print("=" * 40)
    print("1. Run the PDF Revision Manager:")
    print("   python pdf_manager/pdf_manager.py")
    print()
    print("2. Select a folder containing your LF_ files")
    print()
    print("3. The script will automatically:")
    print("   • Filter for files starting with 'LF_'")
    print("   • Recognize the pattern LF_A0-3_A.pdf")
    print("   • Group files by base name (e.g., 'A0-3')")
    print("   • Keep the latest revision")
    print("   • Move older revisions to 'Superceded' folder")
    
    print("\n💡 Tips:")
    print("• The script will only process files starting with 'LF_'")
    print("• Files must follow the pattern: LF_[base]_[revision].pdf")
    print("• Revisions are sorted alphabetically (A < B < C < ...)")
    print("• You can modify the JSON config files anytime to change settings")
    
    print("\n⚙️  Configuration Management:")
    print("• Main config: configs/main_config.json")
    print("• PDF Manager config: pdf_manager/config.json")
    print("• Use: python configs/config_manager.py to manage settings")

def main():
    """Main setup function"""
    success = setup_lf_configuration()
    
    if success:
        print("\n🎉 Setup complete! Your PDF Revision Manager is now configured for LF_A0-3 files.")
        print("\n📁 Configuration files:")
        print("   • configs/main_config.json (main project config)")
        print("   • pdf_manager/config.json (PDF manager specific config)")
        print("\n   You can edit these JSON files anytime to modify the configuration.")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 