import argparse
import csv
import os
import re
from pathlib import Path

from util import convert_to_excel

parser = argparse.ArgumentParser(description='Export HTML translations to CSV')
parser.add_argument('base_path', help='Base path containing language directories')
parser.add_argument('output_filepath', help='Output directory for CSV files')
parser.add_argument('--keep-html-tags', action='store_true', 
                    help='Keep HTML tags in the exported content (default: remove tags)')

args = parser.parse_args()

base_path = args.base_path
outputFilepath = args.output_filepath
keep_html_tags = args.keep_html_tags

print(base_path)
print(outputFilepath)
languages = [item for item in Path(base_path).iterdir() if item.is_dir()]

for lang in languages:

    os.makedirs(outputFilepath, exist_ok=True)

    csv_file = '{}/{}.csv'.format(outputFilepath, lang.name)
    with open(csv_file, mode='w') as out_lang_file:
        writer = csv.writer(out_lang_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print(out_lang_file.name)

        filePath = "{}/{}".format(base_path, lang.name)
        listdir = sorted([x for x in os.listdir(filePath) if re.match(r'.*\.html', x)])

        for path in listdir:
            with open("{}/{}".format(filePath, path)) as file_handler:
                print(file_handler.name)

                try:
                    lines = file_handler.readlines()
                    joined_lines = str("".join(lines))

                    # Remove html tags (unless --keep-html-tags is specified)
                    if not keep_html_tags:
                        joined_lines = re.sub('<[^<]+?>', '', joined_lines)

                    # trim leading and trailing whitespaces and other invisible characters
                    joined_lines = joined_lines.strip()

                    # joined_lines = joined_lines.split("<body>")[1]
                    # joined_lines = joined_lines.split("</body>")[0]
                    # joined_lines = joined_lines.strip("\n ")
                    # joined_lines = joined_lines.replace("\n", "")
                    # joined_lines = joined_lines.replace("<br>", "")

                    writer.writerow([path, joined_lines])
                except:
                    print("Skipped file " + file_handler.name)

# Loop through all CSV files in the directory
for csv_file in Path(outputFilepath).glob('*.csv'):
    convert_to_excel(csv_file)


