import argparse
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


# Parse command line arguments
parser = argparse.ArgumentParser(description='Import translations from Excel files to HTML')
parser.add_argument('excel_files', help='Directory containing Excel files with translations')
parser.add_argument('output_dir', help='Output directory for HTML files')

args = parser.parse_args()

excel_files = args.excel_files
output_dir = args.output_dir

languages = [item.stem for item in Path(excel_files).iterdir() if item.name.endswith('.xlsx')]

for lang in languages:
    excel_file = '{}/{}.xlsx'.format(excel_files, lang)
    output_directory = '{}/{}'.format(output_dir, lang)
    print('excel_file ' + excel_file)
    print('output_directory ' + output_directory)
    convert_excel_to_html(excel_file, output_directory)
