# PDF Combiner - Auto-Naming Feature

The PDF Combiner now includes an intelligent auto-naming feature that automatically generates filenames based on your folder structure and current date.

## 🎯 Overview

The auto-naming feature reads your folder structure and creates a structured filename following the pattern:
```
Ample_ProjectName_Date.pdf
```

The tool can extract project information from:
- Simple folder names (e.g., `ProjectName_Type`)
- Complex folder paths (e.g., `Z:\AOA\Ample\02_Specific_Projects\30 Oatley Avenue, Katoomba NSW, 2780\Drawings\PDF`)

## 📁 Folder Structure Examples

### Example 1: Standard Format
```
Folder: Ample_ProjectA_Design
Output: Ample_ProjectA_20241201.pdf
```

### Example 2: Without Ample Prefix
```
Folder: ProjectB_Review
Output: Ample_ProjectB_20241201.pdf
```

### Example 3: Complex Project Names
```
Folder: Ample_MyProject_TechnicalSpecs
Output: Ample_MyProject_20241201.pdf
```

### Example 4: Complex Path Structure
```
Path: Z:\AOA\Ample\02_Specific_Projects\30 Oatley Avenue, Katoomba NSW, 2780\Drawings\PDF
Output: Ample_30 Oatley Avenue, Katoomba NSW, 2780_20241201.pdf
```

## ⚙️ Configuration

Edit `pdf_combiner/config.json` to customize the auto-naming behavior:

```json
{
  "output_settings": {
    "auto_naming": {
      "enabled": true,
      "structure": "Ample_{project_name}_{issue_type}_{date}",
      "date_format": "%Y%m%d",
      "folder_pattern": "^(Ample_)?([^_]+)_([^_]+)$",
      "default_project_name": "Project",
      "default_issue_type": "Issue"
    }
  }
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `enabled` | Enable/disable auto-naming | `true` |
| `structure` | Filename template with placeholders | `"Ample_{project_name}_{date}"` |
| `date_format` | Date format (Python strftime) | `"%Y%m%d"` |
| `folder_pattern` | Regex to parse folder names | `"^(Ample_)?([^_]+)_([^_]+)$"` |
| `default_project_name` | Fallback project name | `"Project"` |
| `extract_from_path` | Enable path-based extraction | `true` |
| `path_patterns` | Array of path extraction patterns | See configuration |

## 🔧 Customization

### 1. Change Date Format

```json
{
  "auto_naming": {
    "date_format": "%Y-%m-%d"  // Results in: Ample_Project_Design_2024-12-01.pdf
  }
}
```

Common date formats:
- `%Y%m%d` → `20241201`
- `%Y-%m-%d` → `2024-12-01`
- `%d%m%Y` → `01122024`
- `%Y%m%d_%H%M` → `20241201_1430`

### 2. Custom Filename Structure

```json
{
  "auto_naming": {
    "structure": "Combined_{project_name}_{date}_{issue_type}"
  }
}
```

Available placeholders:
- `{project_name}` - Extracted from folder name or path
- `{date}` - Current date in specified format

### 3. Custom Folder Pattern

```json
{
  "auto_naming": {
    "folder_pattern": "^(Client_)?([A-Za-z0-9]+)-([A-Za-z]+)$"
  }
}
```

This would match folders like:
- `Client_ABC-Design` → `Ample_ABC_20241201.pdf`
- `XYZ-Review` → `Ample_XYZ_20241201.pdf`

### 4. Path-Based Extraction

For complex folder structures like `Z:\AOA\Ample\02_Specific_Projects\30 Oatley Avenue, Katoomba NSW, 2780\Drawings\PDF`:

```json
{
  "auto_naming": {
    "extract_from_path": true,
    "path_patterns": [
      {
        "pattern": ".*\\\\([^\\\\]+)\\\\Drawings\\\\PDF$",
        "extract": "project_name",
        "description": "Extract project name from path ending with Drawings\\PDF"
      }
    ]
  }
}
```

## 🚀 Usage

### Option 1: Interactive Launcher
```bash
python run_pdf_combiner.py
```
Choose option 1-3 for auto-naming, or option 4 for custom filename.

### Option 2: Command Line
```bash
# Auto-naming (default)
python pdf_combiner/combine_pdf.py

# Custom filename
python pdf_combiner/combine_pdf.py --custom-name "MyCustomName.pdf"

# Auto-naming with open
python pdf_combiner/combine_pdf.py --open
```

### Option 3: Disable Auto-Naming
```json
{
  "output_settings": {
    "auto_naming": {
      "enabled": false
    }
  }
}
```

## 📋 Examples

### Example 1: Design Project
```
Input folder: Ample_Website_Design
Output file: Ample_Website_20241201.pdf
```

### Example 2: Technical Review
```
Input folder: Ample_App_TechnicalReview
Output file: Ample_App_20241201.pdf
```

### Example 3: Client Project
```
Input folder: Client_ProjectA_FinalReview
Output file: Ample_ProjectA_20241201.pdf
```

### Example 4: Simple Project
```
Input folder: MyProject_Docs
Output file: Ample_MyProject_20241201.pdf
```

### Example 5: Complex Path Structure
```
Input path: Z:\AOA\Ample\02_Specific_Projects\30 Oatley Avenue, Katoomba NSW, 2780\Drawings\PDF
Output file: Ample_30 Oatley Avenue, Katoomba NSW, 2780_20241201.pdf
```

## 🛠️ Troubleshooting

### Auto-naming not working?
1. Check if `enabled: true` in config
2. Verify folder name matches the pattern
3. Check console output for auto-generated filename message

### Wrong project/issue names extracted?
1. Review the `folder_pattern` regex
2. Test your folder name against the pattern
3. Adjust the pattern to match your naming convention

### Date format issues?
1. Check the `date_format` setting
2. Use valid Python strftime format codes
3. Test with a simple format like `%Y%m%d`

### Filename contains invalid characters?
- The tool automatically cleans filenames
- Invalid characters are replaced with underscores
- Multiple underscores are collapsed to single

## 💡 Tips

1. **Consistent Folder Naming**: Use consistent naming for best results
2. **Test Patterns**: Test your folder pattern with regex tools
3. **Backup Config**: Keep a backup of your working configuration
4. **Date Formats**: Choose date formats that work well with your workflow
5. **Fallbacks**: Set meaningful default project and issue names

## 🔄 Migration

To migrate from manual naming to auto-naming:

1. **Enable the feature** in config
2. **Test with a sample folder** to verify naming
3. **Adjust patterns** if needed
4. **Update folder names** to match your desired pattern
5. **Use the tool** with confidence!

## 📝 Notes

- Auto-naming only works when no custom filename is provided
- Command line custom names override auto-naming
- The tool shows the auto-generated filename in console output
- Invalid characters in folder names are handled gracefully
- Date is always current date when the tool runs 