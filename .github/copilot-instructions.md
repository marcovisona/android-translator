# Copilot Instructions for android-translator

## Project Overview
- **Purpose:** Unified CLI for exporting/importing Android `strings.xml` and HTML translations to/from Excel (CSV/XLSX), streamlining workflows with translators.
- **Main Entrypoint:** `android_translator.py` (CLI), with subcommands for `strings` and `html` export/import.
- **Command Modules:** Located in `commands/` (e.g., `strings_export.py`, `html_import.py`). Utilities in `commands/utils/`.

## Architecture & Data Flow
- **CLI Structure:** All commands are routed through `android_translator.py`, which dispatches to modules in `commands/`.
- **Subcommands:** Each subcommand (e.g., `strings export`, `html import`) is a separate module, responsible for argument parsing, file I/O, and calling shared utilities.
- **Order Preservation:** String order is maintained using a custom `OrderedSet` (`commands/utils/OrderedSet.py`).
- **Data Flow:**
  - Reads Android `strings.xml` and HTML files
  - Exports to Excel/CSV (`out/<project>/<module>/<module>.xlsx`)
  - Imports update original files from translated Excel/CSV
  - Non-translatable strings are preserved; missing translations are reported

## Developer Workflows
- **Install:** Use Poetry (`poetry install`).
- **Run CLI:** `poetry run android-translator <command> <subcommand> [options]`
- **Test:** `poetry run python test_android_translator.py`
- **Debug:** Add print/log statements; CLI errors are surfaced in terminal output.

## Conventions & Patterns
- **CSV Separator:** Tab (`\t`) is used for CSV files. Avoid tabs in string values.
- **Excel Format:** Output files are `.xlsx` (via pandas/openpyxl). Columns: key, language codes.
- **Module Discovery:** Project modules are auto-discovered by searching for `res/values/` directories.
- **Utilities:** Shared logic in `commands/utils/` (XML parsing, file I/O, order preservation).
- **Safe Import:** Always preserve string order and non-translatable entries.

## Integration Points
- **External Dependencies:**
  - `pandas`, `openpyxl` for Excel/CSV handling
  - Poetry for dependency management
- **No network calls or external APIs**; all processing is local file I/O.

## Key Files & Directories
- `android_translator.py`: Main CLI
- `commands/`: Subcommand implementations
- `commands/utils/`: Shared utilities (e.g., `OrderedSet.py`, `util.py`)
- `test_android_translator.py`: Test suite
- `README.md`: Usage, workflow, and troubleshooting

## Example Workflow
```bash
poetry run android-translator strings export /path/to/project
# Edit Excel files
poetry run android-translator strings import /path/to/project
```

## Tips for AI Agents
- Use Poetry for builds/tests unless user requests otherwise.
- Reference `README.md` for command details and troubleshooting.
- When adding new commands, follow the pattern in `commands/` and update CLI help.
- Always preserve string order and non-translatable entries.

---

_Review these instructions for accuracy. If any section is unclear or missing, please provide feedback to improve._
