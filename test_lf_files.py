#!/usr/bin/env python3
"""
Test script for LF files without revision letters
Tests the new PDF manager with your actual file naming pattern
"""

import sys
import os
sys.path.append('pdf_manager')

def test_parse_filename():
    """Test the parse_filename function with your actual files"""
    print("🧪 Testing LF file parsing...")
    print("=" * 50)
    
    try:
        from pdf_manager_v2 import parse_filename
        
        # Your actual files
        test_files = [
            "LF_A0-1.pdf",
            "LF_A1-1.pdf", 
            "LF_A1-2.pdf",
            "LF_A1-3.pdf",
            "LF_A3-1.pdf",
            "LF_A3-2.pdf",
            "LF_A4-1.pdf",
            "LF_A4-2.pdf",
            "LF_A2-1.pdf",
            "LF_A7-1.pdf",
            "LF_A9-1.pdf",
            "LF_A0-3.pdf",
            "LF_A5-1.pdf",
            "LF_A5-2.pdf",
            "Ample_LittleFella_Ungaroo_Detailing.pdf",  # Should not match
            "Ample_Ungaroo_Katoomnba__Transmittal_V2.pdf"  # Should not match
        ]
        
        # Test with the new pattern
        pattern = r"^LF_([A-Z0-9\-]+)\.pdf$"
        
        print("Testing pattern:", pattern)
        print("-" * 50)
        
        for filename in test_files:
            base, rev = parse_filename(filename, [pattern])
            if base and rev:
                print(f"✅ {filename} → Base: '{base}', Revision: '{rev}'")
            else:
                print(f"❌ {filename} → No match")
        
        print("-" * 50)
        
        # Test grouping logic
        print("\n📁 Testing file grouping...")
        print("=" * 50)
        
        from collections import defaultdict
        grouped_files = defaultdict(list)
        
        for filename in test_files:
            base, rev = parse_filename(filename, [pattern])
            if base and rev:
                grouped_files[base].append((rev, filename))
        
        print(f"Found {len(grouped_files)} file groups:")
        for base, rev_files in grouped_files.items():
            rev_files.sort(key=lambda x: x[0])
            latest_rev, latest_file = rev_files[-1]
            print(f"• {base}: {len(rev_files)} files, latest: {latest_file}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import pdf_manager_v2: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing: {e}")
        return False

def test_configuration():
    """Test the configuration loading"""
    print("\n⚙️  Testing configuration...")
    print("=" * 50)
    
    try:
        import json
        
        with open("pdf_manager/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        file_processing = config.get('file_processing', {})
        patterns = file_processing.get('file_patterns', [])
        
        print("Current configuration:")
        print(f"• Prefix filter: '{file_processing.get('file_prefix_filter', 'None')}'")
        print(f"• Interactive mode: {file_processing.get('interactive_mode', False)}")
        print(f"• Patterns: {len(patterns)}")
        
        for i, pattern in enumerate(patterns):
            print(f"  Pattern {i+1}: {pattern}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 LF Files Test - PDF Manager V2")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_parse_filename
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new PDF manager should work with your LF files.")
        print("\n🚀 You can now run:")
        print("   python run_pdf_manager.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 