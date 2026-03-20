"""
Import Excel translations back to HTML files.
"""
from html import escape
import os
import re

import pandas as pd


def normalize_excel_content(content):
    """Normalize Excel cell content and unescape supported control characters."""
    if pd.isna(content):
        return ""

    normalized_content = str(content)
    normalized_content = re.sub(r'\\n', '\n', normalized_content)
    normalized_content = re.sub(r'\\t', '\t', normalized_content)
    normalized_content = re.sub(r'\\r', '\r', normalized_content)

    return normalized_content


def wrap_plain_text_lines_in_paragraphs(content):
    """Convert plain text lines to HTML paragraphs."""
    lines = content.splitlines()

    if not lines:
        return ""

    return "\n".join(f"<p>{escape(line)}</p>" for line in lines)


def convert_excel_to_html(excel_file, output_dir, plain_text_to_html=False):
    """
    Convert Excel file to HTML files.
    
    Args:
        excel_file: Path to Excel file
        output_dir: Output directory for HTML files
    """
    # Read the Excel file
    df = pd.read_excel(excel_file, sheet_name=None)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for sheet_name, data in df.items():
        for _, row in data.iterrows():
            file_name = row.iloc[0]
            content = normalize_excel_content(row.iloc[1])

            html_content = content

            if plain_text_to_html:
                html_content = wrap_plain_text_lines_in_paragraphs(content)
            
            # Write the HTML content to a file
            output_file = os.path.join(output_dir, file_name)
            with open(output_file, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)


def execute(args):
    """Execute the HTML import command."""
    html_path = args.html_path
    output_dir = args.output_dir
    plain_text_to_html = args.plain_text_to_html
    
    # Validate HTML path
    if not html_path.exists():
        raise FileNotFoundError(f"HTML path does not exist: {html_path}")
    
    # Validate output directory
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    
    # Determine project name from the html_path (same logic as export)
    path_parts = html_path.parts
    
    try:
        if 'assets' in path_parts:
            assets_index = path_parts.index('assets')
            if assets_index >= 4:
                project_name = path_parts[assets_index - 4]
            else:
                project_name = html_path.parent.parent.parent.parent.name
        else:
            project_name = html_path.parent.name
    except (ValueError, IndexError):
        project_name = html_path.parent.name
    
    # Construct the expected input directory: output_dir/project_name/html/
    input_dir = output_dir / project_name / "html"
    
    if not input_dir.exists():
        raise FileNotFoundError(f"HTML export directory not found: {input_dir}")
    
    print(f"📥 Importing from: {input_dir}")
    print(f"📁 Target HTML directory: {html_path}")
    print(f"📝 Plain text to HTML: {plain_text_to_html}")
    print()
    
    # Get all Excel files (language files)
    excel_files = list(input_dir.glob('*.xlsx'))
    
    if not excel_files:
        raise ValueError(f"No Excel files found in {input_dir}")
    
    # Process each language file
    for excel_file in sorted(excel_files):
        lang = excel_file.stem
        print(f"  🌍 Processing language: {lang}")
        
        output_directory = html_path / lang
        
        try:
            convert_excel_to_html(
                excel_file,
                output_directory,
                plain_text_to_html=plain_text_to_html,
            )
            
            # Count HTML files created
            html_files = list(output_directory.glob('*.html'))
            print(f"    ✅ Created {len(html_files)} HTML files")
            
        except Exception as e:
            print(f"    ❌ Error processing {excel_file.name}: {e}")
    
    print()
    print(f"✅ Successfully imported HTML translations!")
    print(f"   Languages: {', '.join([f.stem for f in sorted(excel_files)])}")
