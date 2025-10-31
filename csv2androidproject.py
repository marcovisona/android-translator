import codecs
import collections
import csv
import os
import sys
from xml.dom import minidom
import openpyxl

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


def read_xlsx(filename):
    content = dict()
    wb = openpyxl.load_workbook(filename)
    sheet = wb.active
    rows = list(sheet.iter_rows(values_only=True))

    if len(rows) <= 0:
        return content

    header_tmp = rows[0]
    langList = []
    for lang in header_tmp[1:]:
        if lang:
            content[lang] = dict()
            langList.append(lang)
    for l in rows[1:]:
        key = l[0]
        for idx, item in enumerate(l[1:]):
            if item:
                content[langList[idx]][key] = escapeAndroidChar(item)
            else:
                print("Empty item for " + langList[idx])
    return content

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

languageExportDict = read_xlsx(pathToExportString)
# languageExportDict = read_file(pathToExportString)
xmldict = dict()


def load_strings_arr(lang):
    with codecs.open(lang, 'r', "utf-8") as f:
        return [x.strip("\n") for x in f.readlines()]


def add(collection):
    for key in collection:
        if key is None:
            continue

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


for lang in languageExportDict:
    stringsDict = collections.OrderedDict(languageExportDict[lang])
    stringsExportDict = languageExportDict[lang]
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
for lang in languageExportDict:
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
