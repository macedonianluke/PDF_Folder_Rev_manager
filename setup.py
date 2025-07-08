#!/usr/bin/env python3
"""
Setup script for PDF Folder Revision Manager
"""
import os
import subprocess
import sys
from pathlib import Path

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    if not env_file.exists():
        env_content = """# Python Environment Configuration
PYTHON_VERSION=3.9
VIRTUAL_ENV_NAME=pdf_manager_env

# Project Configuration
PROJECT_NAME=PDF_Folder_Rev_manager
PROJECT_VERSION=1.0.0

# Development Settings
DEBUG=True
LOG_LEVEL=INFO

# File Paths
DEFAULT_PDF_FOLDER=./pdfs
SUPERCEDED_FOLDER_NAME=Superceded
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("Created .env file")

def install_dependencies():
    """Install dependencies from requirements.txt"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error installing dependencies")

def main():
    print("Setting up PDF Folder Revision Manager...")
    create_env_file()
    install_dependencies()
    print("Setup complete!")

if __name__ == "__main__":
    main()