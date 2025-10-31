# Android Translator CLI

A unified command-line tool for managing translations in Android projects. Export and import Android `strings.xml` files and HTML translations to/from Excel format, making it easy to work with professional translators.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Poetry](https://img.shields.io/badge/dependency-Poetry-blue.svg)](https://python-poetry.org/)

---

## 📚 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Using Poetry (Recommended)](#using-poetry-recommended)
  - [Using pip](#alternative-using-pip)
- [Usage](#-usage)
  - [Export Android Strings](#1-export-android-strings-to-excel)
  - [Import Android Strings](#2-import-excel-to-android-strings)
  - [Export HTML Translations](#3-export-html-translations)
  - [Import HTML Translations](#4-import-html-translations)
- [Command Reference](#-command-reference)
- [Workflow Examples](#-workflow-examples)
- [Technical Details](#-technical-details)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Changelog](#-changelog)

---

## ✨ Features

- ✅ **Unified CLI**: Single tool with intuitive subcommands
- 📊 **Excel Format**: Automatic CSV to Excel (.xlsx) conversion
- 🌍 **Multi-language Support**: Handle multiple languages simultaneously
- 🔄 **Bidirectional**: Export for translation, import back seamlessly
- 📝 **HTML Support**: Export and import HTML content translations
- 🎯 **Order Preservation**: Maintains original string order in XML files
- 🛡️ **Safe**: Preserves non-translatable strings and handles edge cases
- 🎨 **Beautiful Output**: Colored terminal output with progress indicators
- 🧪 **Well-tested**: Comprehensive test suite included
- 🐍 **Poetry Ready**: Modern dependency management with Poetry

---

## 🚀 Quick Start

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | poetry run python -

# Clone/download this repository
git clone git@github.com:marcovisona/android-translator.git
cd android-translator

# Install dependencies with Poetry
poetry install

# Run the tool
poetry run android-translator --help

# Export strings from Android project (auto-discovers all modules)
poetry run android-translator strings export /path/to/android/project

# This creates: out/projectname/module1/module1.xlsx, out/projectname/module2/module2.xlsx, etc.

# Edit the Excel files for translation

# Import translations back to Android project
poetry run android-translator strings import /path/to/android/project
```

---

## 📦 Installation

### Using Poetry (Recommended)

[Poetry](https://python-poetry.org/) provides the best development experience with automatic dependency management and virtual environments.

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | poetry run python -

# Clone/download this repository
git clone git@github.com:marcovisona/android-translator.git
cd android-translator

# Install all dependencies in a virtual environment
poetry install

# Run the tool (Poetry automatically uses the virtual environment)
poetry run android-translator --help
```

### Alternative: Using pip

If you prefer pip or can't use Poetry:

```bash
# Install required dependencies
pip install --user pandas openpyxl

# Or using requirements.txt
pip install --user -r requirements.txt

# Run the tool directly
poetry run android-translator --help
```

### Verify Installation

```bash
# Check Poetry installation
poetry --version

# Check Python version (3.12+ required)
poetry run python --version

# Test the tool
poetry run android-translator --help

# Or activate the virtual environment
poetry shell
android-translator --help
```

---

## 💻 Usage

### General Command Structure

```bash
# With Poetry (recommended)
poetry run android-translator <command> <subcommand> [options]

# Or with direct Python (if not using Poetry)
poetry run android-translator <command> <subcommand> [options]
```

### 1. Export Android Strings to Excel

Extract all `strings.xml` files from all Android modules in your project to separate Excel files:

```bash
poetry run android-translator strings export <android_root> [--output-dir OUTPUT_DIR]
```

**Arguments:**
- `android_root`: Path to Android project root (will auto-discover all modules)
- `--output-dir`: (Optional) Output directory for Excel files (default: `out`)

**Output Structure:**
Files are organized as: `output-dir/project-name/module-name/module-name.xlsx`

**Options:**
- `--default-language LANG`: Default language code (default: `en`)

**Example:**
```bash
# Export strings from all modules in Android project
poetry run android-translator strings export ~/projects/MyApp

# With custom output directory
poetry run android-translator strings export ~/projects/MyApp --output-dir translations

# With custom default language
poetry run android-translator strings export ~/projects/MyApp --default-language fr
```

**What it does:**
- Automatically discovers all Android modules (directories containing `res/values/`)
- For each module, scans `res/values/`, `res/values-fr/`, `res/values-es/`, etc.
- Extracts all translatable strings and string arrays
- Creates separate Excel files for each module
- Reports missing translations

**Example output for a multi-module project:**
```
out/
└── MyApp/
    ├── app/
    │   └── app.xlsx
    ├── feature-login/
    │   └── feature-login.xlsx
    └── core-ui/
        └── core-ui.xlsx
```

**Output format:**

| key             | en       | fr         | es           |
|-----------------|----------|------------|--------------|
| app_name        | My App   | Mon App    | Mi App       |
| welcome_message | Welcome! | Bienvenue! | ¡Bienvenido! |
| colors,0        | Red      | Rouge      | Rojo         |
| colors,1        | Green    | Vert       | Verde        |

### 2. Import Excel to Android Strings

Import translations from Excel files back to `strings.xml` files for all modules:

```bash
poetry run android-translator strings import <android_root> [--output-dir OUTPUT_DIR]
```

**Arguments:**
- `android_root`: Path to Android project root (must match the path used for export)
- `--output-dir`: (Optional) Directory containing exported Excel files (default: `out`)

**Options:**
- `--default-language LANG`: Default language code (default: `en`)

**Example:**
```bash
# Import translations back to all modules in Android project
poetry run android-translator strings import ~/projects/MyApp

# With custom input directory
poetry run android-translator strings import ~/projects/MyApp --output-dir translations
```

**What it does:**
- Automatically discovers all Android modules (matching the export structure)
- For each module, reads translations from the corresponding Excel file
- Creates/updates `values-<lang>/strings.xml` for each language in each module
- Preserves original key order in existing files
- Properly escapes special characters (e.g., `'` → `\'`)
- Handles both regular strings and string arrays

### 3. Export HTML Translations

Extract HTML files from language directories to Excel files (one per language):

```bash
poetry run android-translator html export <html_path> [--output-dir OUTPUT_DIR]
```

**Arguments:**
- `html_path`: Path to HTML directory containing language folders
- `--output-dir`: (Optional) Output directory for Excel files (default: `out`)

**Options:**
- `--remove-html-tags`: Remove HTML tags in exported content (default: keep tags)

**Expected directory structure:**
```
project/module/src/main/assets/html/
├── en/
│   ├── page1.html
│   ├── page2.html
├── fr/
│   ├── page1.html
│   ├── page2.html
└── es/
    ├── page1.html
    ├── page2.html
```

**Example:**
```bash
# Export HTML translations (keeps HTML tags by default)
poetry run android-translator html export \
    ~/projects/MyApp/app/src/main/assets/html

# With custom output directory
poetry run android-translator html export \
    ~/projects/MyApp/app/src/main/assets/html \
    --output-dir translations

# Remove HTML tags
poetry run android-translator html export \
    ~/projects/MyApp/app/src/main/assets/html \
    --remove-html-tags
```

**Output Structure:**
Files organized as: `output-dir/project-name/html/language.xlsx`

**Example output:**
```
out/
└── MyApp/
    └── html/
        ├── en.xlsx
        ├── fr.xlsx
        └── es.xlsx
```

### 4. Import HTML Translations

Import translations from Excel files back to HTML files:

```bash
poetry run android-translator html import <html_path> [--output-dir OUTPUT_DIR]
```

**Arguments:**
- `html_path`: Path to HTML directory containing language folders (must match the path used for export)
- `--output-dir`: (Optional) Directory containing exported Excel files (default: `out`)

**Example:**
```bash
# Import HTML translations from Excel (using default 'out' directory)
poetry run android-translator html import \
    ~/projects/MyApp/app/src/main/assets/html

# With custom input directory
poetry run android-translator html import \
    ~/projects/MyApp/app/src/main/assets/html \
    --output-dir translations
```

**What it does:**
- Reads Excel files (one per language) from `output-dir/project-name/html/`
- Recreates HTML files in language subdirectories
- Handles escaped characters (newlines, tabs, etc.)

---

## 📖 Command Reference

### Global Options

```bash
--version          Show program version
--help, -h         Show help message
```

### Strings Commands

| Command          | Description                                    |
|------------------|------------------------------------------------|
| `strings export` | Export Android strings.xml files to Excel      |
| `strings import` | Import Excel file to Android strings.xml files |

### HTML Commands

| Command       | Description                                        |
|---------------|----------------------------------------------------|
| `html export` | Export HTML files to Excel (one file per language) |
| `html import` | Import Excel files to HTML files                   |

### Get Help

```bash
# General help
poetry run android-translator --help

# Strings help
poetry run android-translator strings --help
poetry run android-translator strings export --help
poetry run android-translator strings import --help

# HTML help
poetry run android-translator html --help
poetry run android-translator html export --help
poetry run android-translator html import --help
```

---

## 🔄 Workflow Examples

### Typical Translation Workflow

1. **Export translations from your Android project:**

```bash
poetry run android-translator strings export ~/projects/MyApp
```

2. **Send Excel files to translators** (via email, Dropbox, etc.)
   - All Excel files are in `out/MyApp/` directory
   - Each module has its own Excel file

3. **Translators edit the Excel files** (add/update translations in their columns)

4. **Import the updated translations back:**

```bash
poetry run android-translator strings import ~/projects/MyApp
```

5. **Verify in your Android project** - all `strings.xml` files across all modules are updated!

### Multi-Module Project Example

The tool automatically handles multi-module projects:

```bash
# Single command exports all modules
poetry run android-translator strings export ~/projects/MyApp

# Output structure:
# out/
# └── MyApp/
#     ├── app/
#     │   └── app.xlsx
#     ├── libutilities/
#     │   └── libutilities.xlsx
#     └── libdata/
#         └── libdata.xlsx

# After translation, single command imports all modules
poetry run android-translator strings import ~/projects/MyApp
```

### Creating Convenience Scripts

Create a wrapper script for common workflows:

**translate.sh:**
```bash
#!/bin/bash
# Convenience script for exporting, translating, and importing

PROJECT_PATH="$1"
COMMAND="${2:-export}"

if [ -z "$PROJECT_PATH" ]; then
    echo "Usage: $0 <project_path> [export|import]"
    exit 1
fi

case "$COMMAND" in
    export)
        echo "🔍 Exporting translations from all modules..."
        poetry run android-translator strings export "$PROJECT_PATH"
        echo "📧 Send the files in out/$(basename $PROJECT_PATH)/ to translators"
        ;;
    import)
        echo "📥 Importing translations to all modules..."
        poetry run android-translator strings import "$PROJECT_PATH"
        echo "✅ All translations imported!"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Usage: $0 <project_path> [export|import]"
        exit 1
        ;;
esac
```

Usage: 
- Export: `./translate.sh ~/projects/MyApp export`
- Import: `./translate.sh ~/projects/MyApp import`

---

## 🔧 Technical Details

### String Handling

- **Escaping**: Single quotes (`'`) are automatically escaped to `\'` for Android XML compatibility
- **Arrays**: String arrays become `"array_name,index"` keys in Excel (e.g., `"colors,0"`, `"colors,1"`)
- **Translatable attribute**: Respects `translatable="false"` in XML (these strings are not exported)
- **Order preservation**: When importing, existing strings maintain their original order in XML

### File Structure

The tool expects standard Android project structure:

```
src/main/
└── res/
    ├── values/
    │   └── strings.xml          # Default language (en)
    ├── values-fr/
    │   └── strings.xml          # French
    ├── values-es/
    │   └── strings.xml          # Spanish
    └── ...
```

### Excel Format

- First column: String keys
- Subsequent columns: Language codes (en, fr, es, etc.)
- All fields are quoted for safety
- Automatic conversion from CSV to Excel format

### Architecture

```
android_translator.py (CLI interface)
      ↓
commands/ (command implementations)
   ├── strings_export.py
   ├── strings_import.py
   ├── html_export.py
   └── html_import.py
      ↓
util.py, OrderedSet.py (shared utilities)
```

---

## 🔍 Troubleshooting

### Common Issues

**Problem**: `ModuleNotFoundError: No module named 'pandas'`  
**Solution**: Install dependencies:
```bash
# With Poetry
poetry install

# With pip
pip install --user pandas openpyxl
```

**Problem**: `No Android modules found`  
**Solution**: Ensure you're pointing to the Android project root directory (the one containing module directories with `src/main/res/values` folders)

**Problem**: Strings are not in the expected order after import  
**Solution**: This is expected for new strings. The tool preserves the order of existing strings but adds new ones at the end.

**Problem**: Special characters appear incorrectly  
**Solution**: Ensure your Excel editor saves the file with UTF-8 encoding

**Problem**: Python version mismatch  
**Solution**: Ensure you're using Python 3.12 or higher:
```bash
poetry run python --version
```

### Getting Help

If you encounter issues:

1. **Check the help**: `poetry run android-translator --help`
2. **Check Python version**: `poetry run python --version` (need 3.12+)
3. **Verify Poetry**: `poetry --version`
4. **Check dependencies**: `poetry show` or `poetry run pip list | grep -E 'pandas|openpyxl'`

---

## 📄 License

The MIT License (MIT)

Copyright (c) 2014 Jean-Philippe Jodoin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

---

## 📝 Changelog

### Version 2.0.0 (2025-10-31)

- 🎉 Complete refactor into unified CLI tool
- ✨ Added Poetry support for dependency management
- 📚 Consolidated documentation into single README
- 🧪 Added comprehensive test suite
- 🎨 Added colored output and progress indicators
- 🔧 Improved error handling and validation
- 📖 Added intuitive help system
- 🚀 Better user experience throughout

### Version 1.0.0 (2014)

- Initial release with separate Python and shell scripts

---

## 🙏 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Made with ❤️ for Android developers who work with translations**

For quick reference, run: `poetry run android-translator --help`
