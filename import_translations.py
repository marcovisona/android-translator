import csv
import os
import re
from typing import Dict

header = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" type="text/css" href="../style.css">
</head>

<body>
"""
footer = """
</body>
</html>
"""

base_path = 'html_doctorvet2'
languages = ['en', 'es', 'fr', 'it']

assoc = {}
with open('files/assoc.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        assoc[row[0]] = {
            'to': row[1],
            'additional': row[3]
        }

errors = []
for lang in languages:

    translations = {}
    with open('files/{}.csv'.format(lang)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            translations[row[0]] = row[1]

    filePath = "{}/{}".format(base_path, lang)
    # listdir = sorted([x for x in os.listdir(filePath) if re.match(r'.*\.html', x)])

    for (file, val) in assoc.items():
        try:
            transl = translations[assoc[file]['to']]
            with open("{}/{}".format(filePath, file), 'w') as f:
                f.write(header)
                f.write(transl.replace(" ", "<br>\n"))
                f.write('<br>\n')
                additional = assoc[file]['additional']
                if additional:
                    f.write(translations[additional].replace(" ", "<br>\n"))
                    f.write('<br>\n')
                f.write(footer)
        except Exception as e:
            errors.append(assoc[file]['to'])

if errors:
    print("Error importing:\n{}".format("\n".join(set(errors))))
