"""
Import Excel translations back to Android strings.xml files.
"""
import collections
from xml.dom import minidom

import openpyxl

from commands.utils.util import discover_android_modules


def escape_android_char(text):
    """Escape Android-specific characters."""
    return text.replace("'", "\\'")


def get_original_key_order(xml_file_path):
    """
    Read the existing XML file and extract the order of keys.
    Returns an ordered list of keys as they appear in the original XML.
    """
    if not xml_file_path.exists():
        return []
    
    key_order = []
    try:
        xmldoc = minidom.parse(str(xml_file_path))
        root_node = xmldoc.getElementsByTagName("resources")
        
        if len(root_node) == 1:
            node_list = root_node[0].childNodes
            for n in node_list:
                if hasattr(n, 'attributes') and n.attributes is not None:
                    tag = n.tagName
                    if tag == 'string':
                        key = n.attributes['name'].nodeValue
                        key_order.append(key)
                    elif tag == 'string-array':
                        name = n.attributes['name'].nodeValue
                        item_list = n.getElementsByTagName("item")
                        for idx in range(len(item_list)):
                            key = f"{name},{idx}"
                            key_order.append(key)
    except Exception as e:
        print(f"  ⚠️  Could not read original XML file {xml_file_path}: {e}")
    
    return key_order


def get_non_translatable_elements(xml_file_path):
    """
    Read the existing XML file and extract all non-translatable elements.
    Returns a list of tuples (position, element_node) where position is the index
    in the original XML and element_node is a clone of the original node.
    """
    if not xml_file_path.exists():
        return []
    
    non_translatable_elements = []
    try:
        xmldoc = minidom.parse(str(xml_file_path))
        root_node = xmldoc.getElementsByTagName("resources")
        
        if len(root_node) == 1:
            node_list = root_node[0].childNodes
            position = 0
            
            for n in node_list:
                if hasattr(n, 'attributes') and n.attributes is not None:
                    tag = n.tagName
                    
                    # Check if translatable
                    tr = n.attributes.get('translatable', None)
                    translatable = True if not tr else tr.nodeValue != 'false'
                    
                    if not translatable:
                        # Store position and a tuple of (key, node_clone)
                        if tag == 'string':
                            key = n.attributes['name'].nodeValue
                        elif tag == 'string-array':
                            key = n.attributes['name'].nodeValue
                        else:
                            key = None
                        
                        non_translatable_elements.append((position, key, n.cloneNode(deep=True)))
                    
                    position += 1
                    
    except Exception as e:
        print(f"  ⚠️  Could not read non-translatable elements from {xml_file_path}: {e}")
    
    return non_translatable_elements


def read_xlsx(filename):
    """Read translations from Excel file."""
    content = {}
    wb = openpyxl.load_workbook(filename)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))
    
    if len(rows) <= 0:
        return content
    
    header_tmp = rows[0]
    lang_list = []
    
    for lang in header_tmp[1:]:
        if lang:
            content[lang] = {}
            lang_list.append(lang)
    
    for row in rows[1:]:
        key = row[0]
        for idx, item in enumerate(row[1:]):
            if item:
                content[lang_list[idx]][key] = escape_android_char(item)
    
    return content


def add_elements_to_xml(doc, root_node, keys_to_process, strings_dict, non_translatable_elements=None):
    """
    Add string elements to the XML document.
    
    Args:
        doc: XML document
        root_node: Root resources node
        keys_to_process: List of keys in the desired order
        strings_dict: Dictionary of key-value pairs
        non_translatable_elements: List of tuples (position, key, node) for non-translatable elements
    """
    if non_translatable_elements is None:
        non_translatable_elements = []
    
    # Build a map of keys to their positions for non-translatable elements
    non_translatable_map = {}
    for pos, key, node in non_translatable_elements:
        if key:
            non_translatable_map[key] = (pos, node)
    
    current_array_node = None
    current_array_name = None
    element_position = 0
    non_translatable_index = 0
    
    # Insert non-translatable elements at the beginning if they come before any translatable content
    while non_translatable_index < len(non_translatable_elements):
        pos, key, node = non_translatable_elements[non_translatable_index]
        if pos <= element_position:
            imported_node = doc.importNode(node, deep=True)
            root_node.appendChild(imported_node)
            non_translatable_index += 1
            element_position += 1
        else:
            break
    
    for key in keys_to_process:
        if key is None:
            continue
        
        # Check if this key exists in strings_dict
        if key not in strings_dict:
            continue
        
        # Check if there are non-translatable elements to insert before this key
        while non_translatable_index < len(non_translatable_elements):
            pos, nt_key, node = non_translatable_elements[non_translatable_index]
            if pos <= element_position:
                imported_node = doc.importNode(node, deep=True)
                root_node.appendChild(imported_node)
                non_translatable_index += 1
                element_position += 1
            else:
                break
        
        if ',' in key:
            # This is a string-array item
            array_name = key[:key.rfind(',')]
            
            # If this is a new array, create the array node
            if current_array_name != array_name:
                current_array_node = doc.createElement("string-array")
                current_array_node.setAttribute("name", array_name)
                root_node.appendChild(current_array_node)
                current_array_name = array_name
                element_position += 1
            
            # Add item to the current array
            node = doc.createElement("item")
            node.appendChild(doc.createTextNode(strings_dict[key]))
            current_array_node.appendChild(node)
        else:
            # Regular string element
            current_array_name = None  # Reset array tracking
            node = doc.createElement("string")
            node.setAttribute("name", key)
            node.appendChild(doc.createTextNode(strings_dict[key]))
            root_node.appendChild(node)
            element_position += 1
    
    # Append any remaining non-translatable elements at the end
    while non_translatable_index < len(non_translatable_elements):
        pos, key, node = non_translatable_elements[non_translatable_index]
        imported_node = doc.importNode(node, deep=True)
        root_node.appendChild(imported_node)
        non_translatable_index += 1


def import_module(module_name, module_path, excel_file, default_language):
    """
    Import strings to a single module.
    
    Args:
        module_name: Name of the module
        module_path: Path to the module's src/main directory
        excel_file: Path to the Excel file with translations
        default_language: Default language code
        
    Returns:
        True if import was successful, False otherwise
    """
    if not excel_file.exists():
        print(f"  ⚠️  Excel file not found: {excel_file}")
        return False
    
    res_path = module_path / "res"
    
    print(f"\n Module: {module_name}")
    print(f"   Source: {excel_file.name}")
    
    # Read Excel file
    language_export_dict = read_xlsx(excel_file)
    
    if not language_export_dict:
        print(f"  ⚠️  No data found in Excel file")
        return False
    
    xml_dict = {}
    
    # Create XML documents for each language
    for lang in language_export_dict:
        print(f"  🌍 Processing language: {lang}")
        
        strings_dict = collections.OrderedDict(language_export_dict[lang])
        doc = minidom.Document()
        xml_dict[lang] = doc
        root_node = doc.createElement("resources")
        doc.appendChild(root_node)
        
        # Determine the output path for this language
        folder_name = "values" if lang == default_language else f"values-{lang}"
        lang_folder = res_path / folder_name
        string_path = lang_folder / "strings.xml"
        
        # Get the original key order from the existing XML file
        original_key_order = get_original_key_order(string_path)
        
        # Get non-translatable elements from the original XML
        non_translatable_elements = get_non_translatable_elements(string_path)
        
        # Separate keys into: existing (in original order) and new (not in original XML)
        existing_keys = []
        new_keys = []
        
        for key in strings_dict.keys():
            if key in original_key_order:
                existing_keys.append(key)
            else:
                new_keys.append(key)
        
        # Sort existing keys by their original position
        existing_keys.sort(key=lambda k: original_key_order.index(k))
        
        # Add existing keys first (preserving original order) along with non-translatable elements
        add_elements_to_xml(doc, root_node, existing_keys, strings_dict, non_translatable_elements)
        
        # Add new keys at the end
        add_elements_to_xml(doc, root_node, new_keys, strings_dict)
    
    # Write XML files
    for lang in language_export_dict:
        folder_name = "values" if lang == default_language else f"values-{lang}"
        lang_folder = res_path / folder_name
        lang_folder.mkdir(parents=True, exist_ok=True)
        
        string_path = lang_folder / "strings.xml"

        # If the xml content is empty, skip writing
        if not xml_dict[lang].getElementsByTagName("string") and not xml_dict[lang].getElementsByTagName("string-array"):
            print(f"     ⚠️  No strings to write for {folder_name}, skipping.")
            continue
        
        with open(string_path, 'wb') as f:
            xml_contain = xml_dict[lang].toprettyxml(encoding="utf-8", indent='    ')
            f.write(xml_contain)
        
        print(f"     ✅ {folder_name}/strings.xml")
    
    return True


def execute(args):
    """Execute the strings import command."""
    android_root = args.android_root
    output_dir = args.output_dir
    default_language = args.default_language
    
    # Validate Android root
    if not android_root.exists():
        raise FileNotFoundError(f"Android root path does not exist: {android_root}")
    
    # Validate output directory
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    
    # Get project name from the root directory
    project_name = android_root.name
    
    print(f"🔍 Discovering Android modules in: {android_root}")
    print(f"📂 Import directory: {output_dir}")
    print()
    
    # Discover all modules in the Android project
    modules = discover_android_modules(android_root)
    
    if not modules:
        raise ValueError(f"No Android modules found in {android_root}. "
                        "Expected to find directories with res/values folders.")
    
    print(f"Found {len(modules)} module(s) in project")
    
    # Import each module
    successful_imports = 0
    project_output_dir = output_dir / project_name
    
    if not project_output_dir.exists():
        raise FileNotFoundError(f"Project output directory not found: {project_output_dir}")
    
    for module_name, module_path in modules:
        # Construct path to the Excel file for this module
        safe_module_name = module_name.replace('/', '_').replace('\\', '_')
        module_output_dir = project_output_dir / module_name
        excel_file = module_output_dir / f"{safe_module_name}.xlsx"
        
        if import_module(module_name, module_path, excel_file, default_language):
            successful_imports += 1
    
    print()
    print(f"✅ Import complete!")
    print(f"   Successfully imported {successful_imports}/{len(modules)} module(s)")
