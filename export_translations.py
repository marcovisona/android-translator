import csv
import os
import re
import sys
from pathlib import Path

base_path = sys.argv[1]
outputFilepath = sys.argv[2]
print(base_path)
print(outputFilepath)
languages = [item for item in Path(base_path).iterdir() if item.is_dir()]

for lang in languages:

    os.makedirs(outputFilepath, exist_ok=True)

    with open('{}/{}.csv'.format(outputFilepath, lang.name), mode='w') as out_lang_file:
        writer = csv.writer(out_lang_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print(out_lang_file.name)

        filePath = "{}/{}".format(base_path, lang.name)
        listdir = sorted([x for x in os.listdir(filePath) if re.match(r'.*\.html', x)])

        for path in listdir:
            with open("{}/{}".format(filePath, path)) as file_handler:
                print(file_handler.name)
                lines = file_handler.readlines()
                joined_lines = str("\n".join(lines))

                # joined_lines = joined_lines.split("<body>")[1]
                # joined_lines = joined_lines.split("</body>")[0]
                # joined_lines = joined_lines.strip("\n ")
                # joined_lines = joined_lines.replace("\n", "")
                # joined_lines = joined_lines.replace("<br>", "")

                writer.writerow([path, joined_lines])
