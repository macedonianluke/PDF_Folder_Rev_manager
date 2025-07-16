# PDF Combiner - Open on Completion Feature

The PDF Combiner tool now includes an option to automatically open the generated PDF file upon completion. This feature is available in multiple ways:

## 🚀 Quick Start

### Option 1: Use the Launcher Script
Run the interactive launcher:
```bash
python run_pdf_combiner.py
```

This will show you options to:
- Combine PDFs normally
- Combine PDFs and automatically open the result
- Combine PDFs and ask before opening

### Option 2: Command Line Options
Use command line flags directly:

```bash
# Normal mode (no auto-open)
python pdf_combiner/combine_pdf.py

# Force open the PDF after creation
python pdf_combiner/combine_pdf.py --open

# Ask user if they want to open the PDF
python pdf_combiner/combine_pdf.py --ask-open
```

### Option 3: Configuration File
Edit `pdf_combiner/config.json` to set default behavior:

```json
{
  "output_settings": {
    "default_output_name": "Combined_Output.pdf",
    "open_on_completion": true,    // Set to true for auto-open
    "ask_before_opening": false    // Set to false to skip asking
  }
}
```

## 📋 Command Line Options

| Option | Description |
|--------|-------------|
| `--open` or `-o` | Automatically open the PDF after creation |
| `--ask-open` or `-a` | Ask user if they want to open the PDF |
| (no flag) | Use configuration file settings |

## ⚙️ Configuration Options

In `pdf_combiner/config.json`:

- `open_on_completion`: Set to `true` to automatically open PDFs
- `ask_before_opening`: Set to `true` to show a dialog asking user preference
- `default_output_name`: Name of the output PDF file

## 🔧 How It Works

1. **PDF Creation**: The tool combines your PDF files as usual
2. **Completion Check**: After successful creation, it checks if opening is requested
3. **User Prompt**: If configured to ask, shows a dialog: "Would you like to open it now?"
4. **Auto-Open**: Opens the PDF with your system's default PDF viewer
5. **Cross-Platform**: Works on Windows, macOS, and Linux

## 💡 Examples

### Example 1: Always Open After Creation
```bash
python pdf_combiner/combine_pdf.py --open
```

### Example 2: Ask User Each Time
```bash
python pdf_combiner/combine_pdf.py --ask-open
```

### Example 3: Configure Default Behavior
Edit `pdf_combiner/config.json`:
```json
{
  "output_settings": {
    "open_on_completion": true,
    "ask_before_opening": false
  }
}
```

Then run normally:
```bash
python pdf_combiner/combine_pdf.py
```

## 🛠️ Troubleshooting

**PDF doesn't open automatically?**
- Check if you have a default PDF viewer installed
- Try the `--ask-open` option to see if the dialog appears
- Check the console output for error messages

**Configuration not working?**
- Ensure `pdf_combiner/config.json` exists and is valid JSON
- Check that the file paths are correct
- Try using command line flags instead

## 📝 Notes

- The feature uses your system's default PDF viewer
- Works with any PDF viewer (Adobe Reader, Chrome, Firefox, etc.)
- Command line flags override configuration file settings
- The tool will show helpful messages if opening fails 