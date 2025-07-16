#!/usr/bin/env python3
"""
Test script for PDF Revision Manager pattern recognition.
This script demonstrates how to use custom patterns to recognize different file formats.
"""

import os
import sys

# Add the scripts directory to the path so we can import the functions
sys.path.append('scripts')

from pdf_manage_1 import parse_filename, get_predefined_patterns, test_pattern, show_pattern_examples

def main():
    print("PDF Revision Manager - Pattern Recognition Test")
    print("=" * 50)
    
    # Test files with different naming conventions
    test_files = [
        "W-A5-2_A.pdf",      # Standard format
        "W-A5-2_B.pdf",      # Standard format
        "LF_001_A.pdf",      # LF format
        "LF_002_B.pdf",      # LF format
        "DOC-001_A.pdf",     # DOC format
        "DOC-002_B.pdf",     # DOC format
        "fileA.pdf",         # No underscore
        "fileB.pdf",         # No underscore
        "drawing A.pdf",     # Space separated
        "drawing B.pdf",     # Space separated
        "other_file.pdf",    # Should not match any pattern
    ]
    
    print(f"Testing {len(test_files)} sample files:")
    for file in test_files:
        print(f"  - {file}")
    
    # Test default pattern
    print("\n" + "="*50)
    print("TESTING DEFAULT PATTERN")
    print("="*50)
    default_pattern = r"^(.+)_([A-Z])\.pdf$"
    test_pattern(default_pattern, test_files)
    
    # Test LF pattern
    print("\n" + "="*50)
    print("TESTING LF PATTERN")
    print("="*50)
    lf_pattern = r"^LF_(\d+)_([A-Z])\.pdf$"
    test_pattern(lf_pattern, test_files)
    
    # Test multiple patterns
    print("\n" + "="*50)
    print("TESTING MULTIPLE PATTERNS")
    print("="*50)
    multiple_patterns = [
        r"^(.+)_([A-Z])\.pdf$",      # Standard
        r"^LF_(\d+)_([A-Z])\.pdf$",  # LF format
        r"^DOC-(\d+)_([A-Z])\.pdf$", # DOC format
        r"^(.+)([A-Z])\.pdf$",       # No underscore
        r"^(.+)\s+([A-Z])\.pdf$",    # Space separated
    ]
    
    print(f"Testing {len(multiple_patterns)} patterns combined:")
    for pattern in multiple_patterns:
        print(f"  - {pattern}")
    
    print("\nResults:")
    for filename in test_files:
        base, rev = parse_filename(filename, multiple_patterns)
        if base and rev:
            print(f"✓ {filename} -> Base: '{base}', Revision: '{rev}'")
        else:
            print(f"✗ {filename} -> No match")
    
    # Show all available patterns
    print("\n" + "="*50)
    print("AVAILABLE PREDEFINED PATTERNS")
    print("="*50)
    predefined = get_predefined_patterns()
    for name, pattern in predefined.items():
        print(f"{name}: {pattern}")
    
    # Show pattern examples
    show_pattern_examples()
    
    print("\n" + "="*50)
    print("USAGE INSTRUCTIONS")
    print("="*50)
    print("To use custom patterns in the PDF Revision Manager:")
    print("1. Set the FILE_PATTERNS environment variable:")
    print("   export FILE_PATTERNS='^LF_(\\d+)_([A-Z])\\.pdf$'")
    print("2. Or add to your .env file:")
    print("   FILE_PATTERNS=^LF_(\\d+)_([A-Z])\\.pdf$")
    print("3. Run the script:")
    print("   python scripts/pdf_manage_1.py")

if __name__ == "__main__":
    main() 