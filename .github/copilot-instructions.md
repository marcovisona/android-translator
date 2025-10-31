# Android Strings Translation Tool - AI Instructions

## Project Overview
This is a Python-based tool for converting Android string resources between XML and CSV/Excel formats to facilitate translation workflows. The codebase handles two distinct workflows: XML string translations and HTML content translations.

## Architecture & Data Flow

### Core Components
- **androidproject2csv.py**: Extracts strings from multiple `values-{lang}/strings.xml` files → single CSV/Excel
- **csv2androidproject.py**: Converts CSV/Excel back → multiple `values-{lang}/strings.xml` files  
- **export_translations.py + export_html.sh**: Extracts HTML content → CSV per language
- **import_translations.py + import_html.sh**: Converts CSV back → HTML files

### Key Data Structures
- `langageDict[lang][key] = value` - Main translation storage (note: "langage" spelling is intentional)
- `OrderedSet` - Custom implementation preserving string key order for consistent CSV output
- XML parsing uses `minidom` with specific handling for `<string>` and `<string-array>` elements

## Critical Patterns

### String Handling
- **Escape/Unescape**: `escapeAndroidChar()` converts `'` ↔ `\'` for Android XML compatibility
- **Translatable filtering**: Respects `translatable="false"` attribute in XML
- **Array handling**: String arrays become `"array_name,index"` keys in CSV

### File Structure Expectations
```
Android Project/
├── res/
│   ├── values/strings.xml          # Default language (en)
│   ├── values-fr/strings.xml       # French
│   └── values-es/strings.xml       # Spanish
HTML Project/
├── module/src/main/assets/html/
│   ├── en/file1.html, file2.html
│   └── fr/file1.html, file2.html
```

### Command Line Usage
```bash
# XML workflow
python3 androidproject2csv.py /path/to/android/project output.csv
python3 csv2androidproject.py input.xlsx /path/to/android/project

# HTML workflow  
./export_html.sh -m module_name /path/to/project
./import_html.sh -m module_name /path/to/project
```

## Development Conventions

### CSV Format
- Tab-separated by default (configurable in scripts)
- First column: string keys (including `array_name,index` for arrays)
- Subsequent columns: language codes (en, fr, es, etc.)
- Auto-converts to Excel (.xlsx) via `util.py`

### Error Handling
- Prints warnings for missing translations: `"Undefined string for key {key} in {lang}"`
- Gracefully skips non-translatable strings and malformed XML
- Uses try/except for file operations without stopping execution

### Dependencies
- `xml.dom.minidom` for XML parsing (built-in)
- `pandas` + `openpyxl` for Excel conversion
- `OrderedSet.py` - custom ordered set implementation
- Shell scripts expect `python3` in PATH

## Module-Specific Notes
- HTML extraction removes all tags via regex: `re.sub('<[^<]+?>', '', content)`
- Default language assumption: `en` (hardcoded in multiple places)
- Module structure supports different Android project layouts via `-m module_name` parameter