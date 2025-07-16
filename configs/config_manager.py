#!/usr/bin/env python3
"""
Configuration Manager for PDF Revision Manager
Handles loading, saving, and updating JSON configuration files
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages JSON configuration files for the PDF Revision Manager project"""
    
    def __init__(self, config_path: str = None):
        """Initialize the configuration manager"""
        self.config_path = config_path or "configs/main_config.json"
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Loaded configuration from {self.config_path}")
            else:
                print(f"⚠️  Configuration file {self.config_path} not found")
                self.config = {}
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            self.config = {}
        
        return self.config
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to JSON file"""
        if config:
            self.config = config
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    
    def get_script_config(self, script_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific script"""
        if 'scripts' in self.config and script_name in self.config['scripts']:
            script_info = self.config['scripts'][script_name]
            config_path = script_info.get('config_path')
            
            if config_path and os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"❌ Error loading script config {config_path}: {e}")
        
        return None
    
    def update_script_config(self, script_name: str, updates: Dict[str, Any]) -> bool:
        """Update configuration for a specific script"""
        script_config = self.get_script_config(script_name)
        if not script_config:
            print(f"❌ Script configuration not found for {script_name}")
            return False
        
        # Update the configuration
        script_config.update(updates)
        
        # Save back to file
        script_info = self.config['scripts'][script_name]
        config_path = script_info.get('config_path')
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(script_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Updated configuration for {script_name}")
            return True
        except Exception as e:
            print(f"❌ Error updating script config: {e}")
            return False
    
    def create_script_config(self, script_name: str, config_data: Dict[str, Any]) -> bool:
        """Create a new script configuration"""
        if 'scripts' not in self.config:
            self.config['scripts'] = {}
        
        # Add script info to main config
        script_path = f"{script_name}/{script_name}.py"
        config_path = f"{script_name}/config.json"
        
        self.config['scripts'][script_name] = {
            "script_path": script_path,
            "config_path": config_path,
            "description": config_data.get('description', f'{script_name} script')
        }
        
        # Save main config
        if not self.save_config():
            return False
        
        # Save script config
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Created configuration for {script_name}")
            return True
        except Exception as e:
            print(f"❌ Error creating script config: {e}")
            return False
    
    def list_scripts(self) -> list:
        """List all available scripts"""
        if 'scripts' in self.config:
            return list(self.config['scripts'].keys())
        return []
    
    def get_file_patterns(self) -> Dict[str, Any]:
        """Get available file patterns"""
        return self.config.get('file_patterns', {})
    
    def validate_config(self) -> bool:
        """Validate the current configuration"""
        required_keys = ['project_name', 'version', 'scripts']
        
        for key in required_keys:
            if key not in self.config:
                print(f"❌ Missing required configuration key: {key}")
                return False
        
        print("✅ Configuration validation passed")
        return True

def setup_lf_config():
    """Setup configuration for LF_A0-3 files"""
    config_manager = ConfigManager()
    
    # Update PDF manager config for LF format
    lf_updates = {
        "file_processing": {
            "file_prefix_filter": "LF_",
            "interactive_mode": False,
            "file_patterns": ["^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$"]
        }
    }
    
    success = config_manager.update_script_config("pdf_manager", lf_updates)
    
    if success:
        print("\n🎯 LF_A0-3 configuration applied!")
        print("• File prefix filter: 'LF_'")
        print("• Pattern: ^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$")
        print("• Interactive mode: Disabled")
    else:
        print("❌ Failed to apply LF configuration")
    
    return success

def show_config_info():
    """Show current configuration information"""
    config_manager = ConfigManager()
    
    print("\n📋 Configuration Information:")
    print("=" * 40)
    
    if config_manager.config:
        print(f"Project: {config_manager.config.get('project_name', 'Unknown')}")
        print(f"Version: {config_manager.config.get('version', 'Unknown')}")
        print(f"Description: {config_manager.config.get('description', 'No description')}")
        
        scripts = config_manager.list_scripts()
        if scripts:
            print(f"\nAvailable Scripts ({len(scripts)}):")
            for script in scripts:
                script_info = config_manager.config['scripts'][script]
                print(f"• {script}: {script_info.get('description', 'No description')}")
        
        patterns = config_manager.get_file_patterns()
        if patterns:
            print(f"\nFile Patterns ({len(patterns)}):")
            for name, pattern_info in patterns.items():
                print(f"• {name}: {pattern_info.get('description', 'No description')}")
    else:
        print("No configuration loaded")

def main():
    """Main function for configuration management"""
    print("⚙️  PDF Revision Manager - Configuration Manager")
    print("=" * 50)
    
    config_manager = ConfigManager()
    
    while True:
        print("\nOptions:")
        print("1. Setup LF_A0-3 configuration")
        print("2. Show configuration info")
        print("3. Validate configuration")
        print("4. List available scripts")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            setup_lf_config()
        elif choice == '2':
            show_config_info()
        elif choice == '3':
            config_manager.validate_config()
        elif choice == '4':
            scripts = config_manager.list_scripts()
            if scripts:
                print(f"\nAvailable scripts ({len(scripts)}):")
                for script in scripts:
                    print(f"• {script}")
            else:
                print("No scripts configured")
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 