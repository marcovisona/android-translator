#!/usr/bin/env poetry run python
"""
Android Translator CLI
A unified tool for managing translations in Android projects.

The MIT License (MIT)
Copyright (c) 2014 Jean-Philippe Jodoin
Modified and refactored 2025
"""

import argparse
import sys
from pathlib import Path

# Import subcommand modules
from commands import strings_export, strings_import, html_export, html_import


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='android-translator',
        description='Manage translations for Android projects (strings.xml and HTML files)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export strings from Android project to Excel (auto-discovers all modules)
  %(prog)s strings export /path/to/android/project
  
  # Export with custom output directory
  %(prog)s strings export /path/to/android/project --output-dir translations
  
  # Import strings from Excel back to Android project
  %(prog)s strings import /path/to/android/project
  
  # Export HTML translations
  %(prog)s html export /path/to/project/module/src/main/assets/html
  
  # Import HTML translations
  %(prog)s html import /path/to/project/module/src/main/assets/html
  
For more information, see README.md
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    subparsers = parser.add_subparsers(
        title='commands',
        description='Available commands',
        dest='command',
        required=True
    )
    
    # Strings subcommand group
    strings_parser = subparsers.add_parser(
        'strings',
        help='Manage Android strings.xml translations',
        description='Export and import Android strings.xml files to/from Excel format'
    )
    strings_subparsers = strings_parser.add_subparsers(
        title='strings commands',
        dest='strings_command',
        required=True
    )
    
    # Strings export
    strings_export_parser = strings_subparsers.add_parser(
        'export',
        help='Export strings.xml files to Excel',
        description='Export all strings.xml files from Android modules to Excel files (one per module)'
    )
    strings_export_parser.add_argument(
        'android_root',
        type=Path,
        help='Path to Android project root (will auto-discover all modules)'
    )
    strings_export_parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('out'),
        help='Output directory for Excel files (default: out). Files organized as output-dir/project/module/'
    )
    strings_export_parser.add_argument(
        '--default-language',
        default='en',
        help='Default language code (default: en)'
    )
    strings_export_parser.set_defaults(func=strings_export.execute)
    
    # Strings import
    strings_import_parser = strings_subparsers.add_parser(
        'import',
        help='Import Excel files to strings.xml files',
        description='Import translations from Excel files back to Android strings.xml files (one per module)'
    )
    strings_import_parser.add_argument(
        'android_root',
        type=Path,
        help='Path to Android project root (will auto-discover all modules)'
    )
    strings_import_parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('out'),
        help='Directory containing exported Excel files (default: out). Expected structure: output-dir/project/module/'
    )
    strings_import_parser.add_argument(
        '--default-language',
        default='en',
        help='Default language code (default: en)'
    )
    strings_import_parser.set_defaults(func=strings_import.execute)
    
    # HTML subcommand group
    html_parser = subparsers.add_parser(
        'html',
        help='Manage HTML translations',
        description='Export and import HTML translations to/from Excel format'
    )
    html_subparsers = html_parser.add_subparsers(
        title='html commands',
        dest='html_command',
        required=True
    )
    
    # HTML export
    html_export_parser = html_subparsers.add_parser(
        'export',
        help='Export HTML files to Excel',
        description='Export HTML files from language directories to Excel files (one per language)'
    )
    html_export_parser.add_argument(
        'html_path',
        type=Path,
        help='Path to HTML directory containing language folders (e.g., /path/to/project/module/src/main/assets/html)'
    )
    html_export_parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('out'),
        help='Output directory for Excel files (default: out). Files organized as output-dir/project/html/'
    )
    html_export_parser.add_argument(
        '--remove-html-tags',
        action='store_true',
        help='Remove HTML tags in exported content (default: keep tags)'
    )
    html_export_parser.set_defaults(func=html_export.execute)
    
    # HTML import
    html_import_parser = html_subparsers.add_parser(
        'import',
        help='Import Excel files to HTML',
        description='Import translations from Excel files back to HTML files'
    )
    html_import_parser.add_argument(
        'html_path',
        type=Path,
        help='Path to HTML directory containing language folders (e.g., /path/to/project/module/src/main/assets/html)'
    )
    html_import_parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('out'),
        help='Directory containing exported Excel files (default: out). Expected structure: output-dir/project/html/'
    )
    html_import_parser.set_defaults(func=html_import.execute)
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Execute the appropriate subcommand
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
