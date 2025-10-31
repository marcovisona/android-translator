"""
Export HTML translations to Excel format.
"""
import csv
import re

from commands.utils.util import convert_to_excel


def execute(args):
    """Execute the HTML export command."""
    html_path = args.html_path
    output_dir = args.output_dir
    remove_html_tags = args.remove_html_tags
    
    # Validate HTML path
    if not html_path.exists():
        raise FileNotFoundError(f"HTML path does not exist: {html_path}")
    
    if not html_path.is_dir():
        raise NotADirectoryError(f"HTML path is not a directory: {html_path}")
    
    # Determine project name from the html_path
    # Try to get the project name from the directory structure
    # Typical structure: /path/to/project/module/src/main/assets/html
    path_parts = html_path.parts
    
    # Try to find 'assets' in the path and use the project root name
    try:
        # Navigate up from html -> assets -> main -> src -> module -> project
        if 'assets' in path_parts:
            assets_index = path_parts.index('assets')
            if assets_index >= 4:  # Need at least html/assets/main/src/module
                project_name = path_parts[assets_index - 4]
            else:
                project_name = html_path.parent.parent.parent.parent.name
        else:
            # Fallback: use parent directory name
            project_name = html_path.parent.name
    except (ValueError, IndexError):
        # Fallback: use the immediate parent directory name
        project_name = html_path.parent.name
    
    print(f"📁 Scanning HTML directory: {html_path}")
    print(f"Output directory: {output_dir}")
    print(f"🏷️ Remove HTML tags: {remove_html_tags}")
    print()
    
    # Get all language directories
    languages = [item for item in html_path.iterdir() if item.is_dir()]
    
    if not languages:
        raise ValueError(f"No language directories found in {html_path}")
    
    # Create output directory structure: output_dir/project_name/html/
    project_output_dir = output_dir / project_name / "html"
    project_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each language
    for lang in sorted(languages):
        print(f"  🌍 Processing language: {lang.name}")
        
        csv_file = project_output_dir / f"{lang.name}.csv"
                    
        # Get all HTML files in this language directory
        html_files = sorted([x for x in lang.iterdir() if x.suffix == '.html'])
        
        if not html_files:
            print(f"    ⚠️  No HTML files found in {lang.name}")
            continue

        with open(csv_file, mode='w', newline='') as out_lang_file:
            writer = csv.writer(out_lang_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            for html_file in html_files:
                try:
                    with open(html_file, 'r', encoding='utf-8') as file_handler:
                        lines = file_handler.readlines()
                        joined_lines = "".join(lines)
                        
                        # Remove HTML tags (unless --keep-html-tags is specified)
                        if remove_html_tags:
                            joined_lines = re.sub('<[^<]+?>', '', joined_lines)
                        
                        # Trim leading and trailing whitespaces
                        joined_lines = joined_lines.strip()
                        
                        writer.writerow([html_file.name, joined_lines])
                        print(f"    ✓ {html_file.name}")
                        
                except Exception as e:
                    print(f"    ⚠️  Skipped file {html_file.name}: {e}")
        
        # Convert CSV to Excel
        convert_to_excel(csv_file)
        
        # Clean up CSV if Excel was created
        xlsx_file = csv_file.with_suffix('.xlsx')
        if xlsx_file.exists():
            csv_file.unlink()
            print(f"    ✅ {lang.name}.xlsx")
    
    print()
    print(f"✅ Successfully exported HTML translations!")
    print(f"   Languages: {', '.join([lang.name for lang in sorted(languages)])}")
    print(f"   Output location: {project_output_dir}")
