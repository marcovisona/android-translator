"""
The MIT License (MIT)

Copyright (c) 2014 Jean-Philippe Jodoin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import codecs
import collections
import csv
import os
import sys
from xml.dom import minidom


def escapeAndroidChar(text):
    text = text.replace('\'', "\\'")
    return text


# pathToString = raw_input("Path to CSV file:")
# outputFolder = raw_input("Path to Android project (output):")
# defaultLanguage = raw_input("Default langage ISO-639-1 code. (write en if your default langage is english):")

pathToExportString = sys.argv[1]
# pathToString = sys.argv[2]
outputFolder = sys.argv[2]
defaultLanguage = "en"

outputFolder = os.path.join(outputFolder, "res")


def read_csv(filename):
    # Open the CSV file in read mode
    rows = []
    with open(filename, 'r') as csvfile:
        # Create a CSV reader object
        reader = csv.reader(csvfile)

        # Read and process each row
        for row in reader:
            rows.append(row)

    return rows


def read_file(file_name):
    content = dict()
    lines = read_csv(file_name)
    if len(lines) <= 0:
        return content

    header_tmp = lines[0]
    langList = []
    for lang in header_tmp[1:]:
        if lang:
            content[lang] = dict()
            langList.append(lang)
    for l in lines[1:]:
        key = l[0]
        for idx, item in enumerate(l[1:]):
            if item:
                # 3) Escape character
                content[langList[idx]][key] = escapeAndroidChar(item)
            else:
                print("Empty item for " + langList[idx])
    return content


# 1) Read the file and build dictionnary for each langage
langageExportDict = read_file(pathToExportString)
# langageDict = read_file(pathToString)

# 2) Create an XML document from each langage dictionnary
xmldict = dict()


def load_strings_arr(lang):
    with codecs.open(lang, 'r', "utf-8") as f:
        return [x.strip("\n") for x in f.readlines()]


def add(collection):
    for key in collection:
        if ',' in key:
            if ',0' in key:  # first node. Order is guaranteed by the sort
                topNode = doc.createElement("string-array")
                topNode.setAttribute("name", key[0:key.find(',0')])
                rootNode.appendChild(topNode)

            if stringsDict.get(key):
                node = doc.createElement("item")
                node.appendChild(doc.createTextNode(stringsDict[key]))
                topNode.appendChild(node)
        else:
            if stringsDict.get(key):
                node = doc.createElement("string")
                node.setAttribute("name", key)
                node.appendChild(doc.createTextNode(stringsDict[key]))
                rootNode.appendChild(node)


for lang in langageExportDict:
    stringsDict = collections.OrderedDict(langageExportDict[lang])
    stringsExportDict = langageExportDict[lang]
    doc = minidom.Document()
    xmldict[lang] = doc
    rootNode = doc.createElement("resources")
    doc.appendChild(rootNode)

    # stringsExportDict = collections.OrderedDict((stringsExportDict.items()))
    # stringsDict = collections.OrderedDict((stringsDict.items()))
    # stringsExportDict = stringsExportDict.items()
    # stringsDict = stringsDict.items()

    stringsArr = list(stringsDict.values())

    add(stringsArr)

    for key in stringsArr:
        if stringsDict.get(key):
            stringsDict.pop(key)

    add(stringsDict)

# 3) Write XML for each langage in the correct directory structure
for lang in langageExportDict:
    folderName = "values"
    if lang != defaultLanguage:
        folderName = "values-" + lang
    langFolder = os.path.join(outputFolder, folderName)
    if not os.path.exists(langFolder):
        os.makedirs(langFolder)
    stringPath = os.path.join(langFolder, "strings.xml")
    with open(stringPath, 'wb') as f:
        xmlContain = xmldict[lang].toprettyxml(encoding="utf-8", indent='    ')
        # print(xmlContain)
        f.write(xmlContain)
