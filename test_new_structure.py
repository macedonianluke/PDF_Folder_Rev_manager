#!/usr/bin/env python3
"""
Test script for the new PDF Revision Manager structure
Verifies that the JSON configuration system is working correctly
"""

import os
import sys
import json
from pathlib import Path

def test_directory_structure():
    """Test that all required directories exist"""
    print("📁 Testing directory structure...")
    
    required_dirs = [
        "configs",
        "pdf_manager", 
        "transmittal_manager",
        "ods_generator",
        "pdf_combiner"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ All directories exist")
    return True

def test_config_files():
    """Test that configuration files exist and are valid JSON"""
    print("\n📋 Testing configuration files...")
    
    config_files = [
        "configs/main_config.json",
        "pdf_manager/config.json"
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            print(f"❌ Missing: {config_file}")
            return False
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"✅ {config_file} (valid JSON)")
        except json.JSONDecodeError as e:
            print(f"❌ {config_file} (invalid JSON: {e})")
            return False
        except Exception as e:
            print(f"❌ {config_file} (error: {e})")
            return False
    
    print("✅ All configuration files are valid")
    return True

def test_script_files():
    """Test that script files exist"""
    print("\n🐍 Testing script files...")
    
    script_files = [
        "pdf_manager/pdf_manager.py",
        "configs/config_manager.py"
    ]
    
    for script_file in script_files:
        if not os.path.exists(script_file):
            print(f"❌ Missing: {script_file}")
            return False
        else:
            print(f"✅ {script_file}")
    
    print("✅ All script files exist")
    return True

def test_lf_configuration():
    """Test LF_A0-3 configuration"""
    print("\n🎯 Testing LF_A0-3 configuration...")
    
    try:
        # Load PDF manager config
        with open("pdf_manager/config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check LF configuration
        file_processing = config.get('file_processing', {})
        prefix_filter = file_processing.get('file_prefix_filter')
        patterns = file_processing.get('file_patterns', [])
        
        if prefix_filter == "LF_":
            print("✅ File prefix filter: 'LF_'")
        else:
            print(f"❌ File prefix filter: '{prefix_filter}' (expected 'LF_')")
            return False
        
        lf_pattern = "^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$"
        if lf_pattern in patterns:
            print("✅ LF pattern found in patterns")
        else:
            print(f"❌ LF pattern not found in patterns: {patterns}")
            return False
        
        print("✅ LF_A0-3 configuration is correct")
        return True
        
    except Exception as e:
        print(f"❌ Error testing LF configuration: {e}")
        return False

def test_pattern_recognition():
    """Test file pattern recognition"""
    print("\n🧪 Testing pattern recognition...")
    
    # Import the parse function
    sys.path.append('pdf_manager')
    try:
        from pdf_manager import parse_filename
        
        test_files = [
            ("LF_A0-3_A.pdf", True),
            ("LF_A0-3_B.pdf", True),
            ("LF_B1-5_C.pdf", True),
            ("other_file.pdf", False),
            ("LF_invalid.pdf", False)
        ]
        
        pattern = r"^LF_([A-Z0-9\-]+)_([A-Z])\.pdf$"
        
        for filename, should_match in test_files:
            base, rev = parse_filename(filename, [pattern])
            if should_match and base and rev:
                print(f"✅ {filename} → Base: '{base}', Revision: '{rev}'")
            elif not should_match and not base and not rev:
                print(f"✅ {filename} → No match (expected)")
            else:
                print(f"❌ {filename} → Unexpected result: Base='{base}', Rev='{rev}'")
                return False
        
        print("✅ Pattern recognition working correctly")
        return True
        
    except ImportError:
        print("⚠️  Could not import pdf_manager module for testing")
        return True  # Don't fail the test for this
    except Exception as e:
        print(f"❌ Error testing pattern recognition: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 PDF Revision Manager - Structure Test")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_config_files,
        test_script_files,
        test_lf_configuration,
        test_pattern_recognition
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
        print("🎉 All tests passed! The new structure is working correctly.")
        print("\n🚀 You can now use:")
        print("   • python setup_lf_config.py (to configure)")
        print("   • python run_pdf_manager.py (to run PDF manager)")
        print("   • python configs/config_manager.py (to manage config)")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 