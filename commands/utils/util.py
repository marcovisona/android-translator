import pandas as pd
from pathlib import Path


def convert_to_excel(csv_file):
    excel_file = csv_file.with_suffix('.xlsx')
    try:
        print(f"Converting {csv_file} to {excel_file}")
        df = pd.read_csv(csv_file)

        df.to_excel(excel_file, index=False)
    except Exception as e:
        print(f"Ignored file")


def discover_android_modules(android_root):
    """
    Discover all Android modules in a project by finding directories that contain
    src/main/res/values or res/values folders.
    
    Args:
        android_root: Path to the Android project root directory
        
    Returns:
        List of tuples (module_name, module_path) where module_path is the path to src/main
        or the parent of res/ directory
    """
    android_root = Path(android_root)
    modules = []
    
    # Walk through the directory tree
    for path in android_root.rglob('res'):
        if not path.is_dir():
            continue
            
        # Check if this res directory contains values folders
        has_values = any(
            item.is_dir() and item.name.startswith('values')
            for item in path.iterdir()
        )
        
        if not has_values:
            continue
        
        # Determine the module path (parent of res)
        # Typically: module/src/main/res -> we want module/src/main
        module_main_path = path.parent
        
        # Calculate module name relative to project root
        try:
            relative_path = module_main_path.relative_to(android_root)
            # Remove 'src/main' from the end to get the module name
            parts = list(relative_path.parts)
            
            # If path ends with src/main, use everything before that as module name
            if len(parts) >= 2 and parts[-2] == 'src' and parts[-1] == 'main':
                module_name = '/'.join(parts[:-2]) if len(parts) > 2 else 'app'
            else:
                # Fallback: use the whole relative path
                module_name = '/'.join(parts)
            
            # If module_name is empty, use the directory name
            if not module_name:
                module_name = module_main_path.parent.name
                
        except ValueError:
            # Path is not relative to android_root
            module_name = module_main_path.name
        
        modules.append((module_name, module_main_path))
    
    # Remove duplicates and sort
    modules = sorted(set(modules), key=lambda x: x[0])
    
    return modules
