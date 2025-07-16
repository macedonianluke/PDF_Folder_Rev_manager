# PDF Revision Manager - New Structure

This document describes the new organized structure of the PDF Revision Manager project, which now uses JSON configuration files instead of environment variables.

## 📁 Project Structure

```
PDF_Folder_Rev_manager/
├── configs/                          # Configuration management
│   ├── main_config.json             # Main project configuration
│   └── config_manager.py            # Configuration management utility
├── pdf_manager/                      # PDF revision management
│   ├── pdf_manager.py               # Main PDF manager script
│   └── config.json                  # PDF manager specific config
├── transmittal_manager/              # Transmittal management
│   ├── transmittal_manager.py       # Transmittal script
│   └── config.json                  # Transmittal specific config
├── ods_generator/                    # ODS file generation
│   ├── ods_generator.py             # ODS generator script
│   └── config.json                  # ODS generator config
├── pdf_combiner/                     # PDF combination
│   ├── pdf_combiner.py              # PDF combiner script
│   └── config.json                  # PDF combiner config
├── setup_lf_config.py               # Setup script for LF_A0-3 files
├── run_pdf_manager.py               # Simple launcher for PDF manager
└── README_NEW_STRUCTURE.md          # This file
```

## 🚀 Quick Start

### 1. Setup for LF_A0-3 Files

Run the setup script to configure the system for your LF_A0-3 files:

```bash
python setup_lf_config.py
```

This will:
- Create the main configuration file (`configs/main_config.json`)
- Configure the PDF manager for LF_A0-3 format files
- Set up the file pattern recognition
- Test the configuration

### 2. Run the PDF Manager

Use the simple launcher:

```bash
python run_pdf_manager.py
```

Or run directly:

```bash
python pdf_manager/pdf_manager.py
```

## ⚙️ Configuration System

### Main Configuration (`configs/main_config.json`)

The main configuration file contains:
- Project metadata (name, version, description)
- Script registry with paths and descriptions
- File pattern definitions
- Default settings
- Logging configuration

### Script-Specific Configuration

Each script has its own configuration file:
- `pdf_manager/config.json` - PDF manager settings
- `transmittal_manager/config.json` - Transmittal manager settings
- `ods_generator/config.json` - ODS generator settings
- `pdf_combiner/config.json` - PDF combiner settings

### Configuration Management

Use the configuration manager to update settings:

```bash
python configs/config_manager.py
```

Options:
1. Setup LF_A0-3 configuration
2. Show configuration info
3. Validate configuration
4. List available scripts
5. Exit

## 📋 Configuration Examples

### PDF Manager Configuration

```json
{
  "file_processing": {
    "file_prefix_filter": "LF_",
    "interactive_mode": false,
    "file_patterns": [
      "^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$"
    ]
  },
  "folder_settings": {
    "default_pdf_folder": "./pdfs",
    "superceded_folder_name": "Superceded"
  },
  "logging": {
    "debug_mode": true,
    "log_level": "INFO"
  }
}
```

### File Pattern Examples

The system supports multiple file patterns:

1. **LF Format**: `LF_A0-3_A.pdf` → Base: 'A0-3', Revision: 'A'
2. **Standard Format**: `DOC-001_A.pdf` → Base: 'DOC-001', Revision: 'A'
3. **Custom Patterns**: Can be defined in configuration

## 🔧 Customization

### Adding New File Patterns

1. Edit the main configuration file (`configs/main_config.json`)
2. Add your pattern to the `file_patterns` section
3. Update the script-specific configuration

### Modifying Script Settings

1. Edit the script's configuration file (e.g., `pdf_manager/config.json`)
2. Or use the configuration manager: `python configs/config_manager.py`

### Adding New Scripts

1. Create a new folder for your script
2. Add script info to `configs/main_config.json`
3. Create a `config.json` file in the script folder
4. Use the configuration manager to register the script

## 📝 Usage Examples

### LF_A0-3 Files

The system is configured to handle files like:
- `LF_A0-3_A.pdf`
- `LF_A0-3_B.pdf`
- `LF_B1-5_C.pdf`
- `LF_C2-8_A.pdf`

### Standard Files

Also supports standard formats:
- `DOC-001_A.pdf`
- `W-A5-2_B.pdf`
- `Drawing_001_C.pdf`

## 🛠️ Development

### Adding New Features

1. Create a new script folder
2. Add configuration to main config
3. Create script-specific config
4. Update documentation

### Testing Configuration

Use the configuration manager to validate settings:

```bash
python configs/config_manager.py
# Choose option 3: Validate configuration
```

## 📞 Support

If you encounter issues:

1. Check the configuration files are valid JSON
2. Run the configuration manager to validate settings
3. Check the script-specific logs
4. Ensure file patterns match your file naming convention

## 🔄 Migration from Old Structure

If you're migrating from the old structure:

1. Run `python setup_lf_config.py` to create new configuration
2. The old `.env` files are no longer needed
3. Scripts are now organized in separate folders
4. Configuration is now in JSON format for better structure

## 📄 File Pattern Reference

### Supported Patterns

| Pattern | Description | Example | Result |
|---------|-------------|---------|--------|
| `^LF_([A-Z0-9\\-]+)_([A-Z])\\.pdf$` | LF format | `LF_A0-3_A.pdf` | Base: 'A0-3', Rev: 'A' |
| `^(.+)_([A-Z])\\.pdf$` | Standard format | `DOC-001_A.pdf` | Base: 'DOC-001', Rev: 'A' |
| `^DOC-(\\d+)_([A-Z])\\.pdf$` | DOC format | `DOC-001_A.pdf` | Base: '001', Rev: 'A' |

### Pattern Components

- `^` - Start of string
- `([A-Z0-9\\-]+)` - Base name (letters, numbers, hyphens)
- `_` - Underscore separator
- `([A-Z])` - Revision letter
- `\\.pdf$` - PDF extension and end of string 