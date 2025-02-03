import sys
from pathlib import Path

import pandas as pd
import os
import re


def convert_excel_to_html(excel_file, output_dir):
    # Read the Excel file
    df = pd.read_excel(excel_file, sheet_name=None)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for sheet_name, data in df.items():
        for index, row in data.iterrows():
            file_name = row.iloc[0]
            content = row.iloc[1]

            # Reconstruct the HTML content
            content = re.sub(r'\\n', '\n', content)
            content = re.sub(r'\\t', '\t', content)
            content = re.sub(r'\\r', '\r', content)

            html_content = content

            # Write the HTML content to a file
            with open(os.path.join(output_dir, file_name), 'w') as html_file:
                html_file.write(html_content)


# Example usage
excel_files = sys.argv[1]
output_dir = sys.argv[2]

languages = [item.stem for item in Path(excel_files).iterdir() if item.name.endswith('.xlsx')]

for lang in languages:
    excel_file = '{}/{}.xlsx'.format(excel_files, lang)
    output_directory = '{}/{}'.format(output_dir, lang)
    print('excel_file ' + excel_file)
    print('output_directory ' + output_directory)
    convert_excel_to_html(excel_file, output_directory)
