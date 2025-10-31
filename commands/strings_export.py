"""
Export Android strings.xml files to Excel format.
"""
import csv
import os
from xml.dom import minidom

from commands.utils.OrderedSet import OrderedSet
from commands.utils.util import convert_to_excel, discover_android_modules


def unescape_android_char(text):
    """Unescape Android-specific characters."""
    return text.replace("\\'", "'")


def export_to_csv(data, filename):
    """Export data to CSV file with all fields quoted."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        
        if isinstance(data[0], dict):
            header = data[0].keys()
            writer.writerow(header)
            for row in data:
                writer.writerow(row.values())
        else:
            for row in data:
                writer.writerow(row)


def parse_strings_xml(file_path, strings_dict, strings_arr):
    """
    Parse a strings.xml file and extract translatable strings.
    
    Args:
        file_path: Path to strings.xml file
        strings_dict: Dictionary to populate with key-value pairs
        strings_arr: List to track key order
    """
    if not file_path.exists():
        return
    
    try:
        xmldoc = minidom.parse(str(file_path))
        root_node = xmldoc.getElementsByTagName("resources")
        
        if len(root_node) != 1:
            print(f'⚠️  Invalid resource file: {file_path}. Expected a resources node.')
            return
        
        node_list = root_node[0].childNodes
        
        for n in node_list:
            attr = n.attributes
            if attr is None:
                continue
            
            tag = n.tagName
            
            # Check if translatable
            tr = n.attributes.get('translatable', None)
            translatable = True if not tr else tr.nodeValue != 'false'
            
            if not translatable:
                continue
            
            if tag == 'string':
                key = attr['name'].nodeValue
                value = n.childNodes[0].nodeValue if len(n.childNodes) else ''
                strings_arr.append(key)
                strings_dict[key] = value.strip()
                
            elif tag == 'string-array':
                name = attr['name'].nodeValue
                item_list = n.getElementsByTagName("item")
                
                for idx, item in enumerate(item_list):
                    key = f"{name},{idx}"
                    value = item.childNodes[0].nodeValue if len(item.childNodes) else ''
                    strings_arr.append(key)
                    strings_dict[key] = value.strip()
                    
    except Exception as e:
        print(f'⚠️  Error parsing {file_path}: {e}')


def export_module(module_name, module_path, output_dir, project_name, default_language):
    """
    Export strings from a single module.
    
    Args:
        module_name: Name of the module
        module_path: Path to the module's src/main directory
        output_dir: Base output directory
        project_name: Name of the project (for organizing output)
        default_language: Default language code
        
    Returns:
        True if export was successful, False otherwise
    """
    res_path = module_path / "res"
    if not res_path.exists():
        print(f"  ⚠️  No res directory found for module '{module_name}'")
        return False
    
    print(f"\n Module: {module_name}")
    print(f"   Path: {module_path}")
    
    # Parse all values-* folders
    language_dict = {}
    folder_list = os.listdir(res_path)
    
    for folder in sorted(folder_list):
        if not folder.startswith("values"):
            continue
        
        # Extract language code
        try:
            index = folder.index("-")
            lang = folder[index + 1:]
        except ValueError:
            lang = default_language
        
        print(f"  🌍 Processing language: {lang}")
        
        language_dict[lang] = {}
        strings_dict = language_dict[lang]
        strings_arr = []
        
        values_path = res_path / folder
        if not values_path.is_dir():
            continue
        
        file_path = values_path / "strings.xml"
        parse_strings_xml(file_path, strings_dict, strings_arr)
    
    if not language_dict:
        print(f"  ⚠️  No language folders found in module '{module_name}'")
        return False
    
    # Get all unique keys
    unique_keys = set()
    for lang_dict in language_dict.values():
        unique_keys.update(lang_dict.keys())
    unique_keys = OrderedSet(sorted(unique_keys))
    
    if not unique_keys:
        print(f"  ℹ️  No strings found in module '{module_name}'")
        return False
    
    # Build CSV data
    data = [["key"] + list(language_dict.keys())]
    
    for key in unique_keys:
        elements = [key]
        for lang in language_dict:
            strings_dict = language_dict[lang]
            if key in strings_dict:
                elements.append(unescape_android_char(strings_dict[key]))
            else:
                elements.append("")
        data.append(elements)
    
    # Create output directory structure: output_dir/project_name/module_name/
    module_output_dir = output_dir / project_name / module_name
    module_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Use module name as filename (replace / with _)
    safe_module_name = module_name.replace('/', '_').replace('\\', '_')
    output_file = module_output_dir / f"{safe_module_name}.xlsx"
    
    # Export to CSV
    csv_path = output_file.with_suffix('.csv')
    export_to_csv(data, csv_path)
    
    # Convert to Excel
    convert_to_excel(csv_path)
    
    # Clean up CSV if Excel was created successfully
    xlsx_path = output_file.with_suffix('.xlsx')
    if xlsx_path.exists():
        csv_path.unlink()
        print(f"  ✅ Exported to: {xlsx_path.relative_to(output_dir)}")
        print(f"     Strings: {len(unique_keys)}, Languages: {', '.join(language_dict.keys())}")
    else:
        print(f"  ✅ Exported to: {csv_path.relative_to(output_dir)}")
    
    return True


def execute(args):
    """Execute the strings export command."""
    android_root = args.android_root
    output_dir = args.output_dir
    default_language = args.default_language
    
    # Validate project path
    if not android_root.exists():
        raise FileNotFoundError(f"Android root path does not exist: {android_root}")
    
    # Get project name from the root directory
    project_name = android_root.name
    
    print(f"🔍 Discovering Android modules in: {android_root}")
    print(f"📂 Output directory: {output_dir}")
    print()
    
    # Discover all modules
    modules = discover_android_modules(android_root)
    
    if not modules:
        raise ValueError(f"No Android modules found in {android_root}. "
                        "Expected to find directories with res/values folders.")
    
    print(f"Found {len(modules)} module(s):")
    for module_name, _ in modules:
        print(f"  • {module_name}")
    
    # Export each module
    successful_exports = 0
    for module_name, module_path in modules:
        if export_module(module_name, module_path, output_dir, project_name, default_language):
            successful_exports += 1
    
    print()
    print(f"✅ Export complete!")
    print(f"   Successfully exported {successful_exports}/{len(modules)} module(s)")
    print(f"   Output location: {output_dir / project_name}")
