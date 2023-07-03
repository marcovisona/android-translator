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
import os
import sys
from xml.dom import minidom
from OrderedSet import OrderedSet
import csv


def export_to_csv(data, filename):
    # Open the CSV file in write mode
    with open(filename, 'w', newline='') as csvfile:
        # Create a CSV writer object with QUOTE_ALL option
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

        # Write the header row (if necessary)
        if (isinstance(data[0], dict)):
            header = data[0].keys()  # Assuming data is a list of dictionaries
            writer.writerow(header)

            # Write the data rows
            for row in data:
                writer.writerow(row.values())  # Assuming data is a list of dictionaries
        else:
            for row in data:
                writer.writerow(row)


def unescapeAndroidChar(text):
    text = text.replace("\\'", '\'')
    return text


defaultLangage = 'en'  # raw_input("Default langage ISO-639-1 code. (write en if your default langage is english):")
pathToProject = sys.argv[1]  # raw_input("Path to Android project file:")
outputFilepath = sys.argv[2]  # raw_input("Path to CSV file (output):")

ressourcePath = os.path.join(pathToProject, "res")
folderList = os.listdir(ressourcePath)
langageDict = dict()
for f in folderList:
    if f.startswith("values"):

        try:
            index = f.index("-")
            lang = f[index + 1:]
        except:
            lang = defaultLangage
        print(lang)

        langageDict[lang] = dict()
        stringsDict = langageDict[lang]
        stringsArr = []
        valuesPath = os.path.join(ressourcePath, f)
        if os.path.isdir(valuesPath):
            filePath = os.path.join(valuesPath, "strings.xml")
            if os.path.exists(filePath):
                # Open String XML
                # print(filePath)
                xmldoc = minidom.parse(filePath)
                rootNode = xmldoc.getElementsByTagName("resources")
                if len(rootNode) == 1:
                    nodeList = rootNode[0].childNodes
                    for n in nodeList:
                        attr = n.attributes
                        if attr != None:
                            tag = n.tagName

                            tr = n.attributes.get('translatable', None)
                            translatable = True if not tr else tr.nodeValue != 'false'

                            if translatable and tag == 'string':
                                key = attr['name'].nodeValue
                                value = n.childNodes[0].nodeValue if len(n.childNodes) else ''
                                stringsArr.append(key)
                                stringsDict[key] = value.strip()
                                # print(key + " = " + value)
                            elif translatable and tag == 'string-array':
                                name = attr['name'].nodeValue
                                itemList = n.getElementsByTagName("item")
                                for idx, item in enumerate(itemList):
                                    key = str(name) + "," + str(idx)
                                    value = item.childNodes[0].nodeValue
                                    # print(key + " = " + value)
                                    stringsArr.append(key)
                                    stringsDict[key] = value.strip()
                            else:
                                print("Unknown node")
                else:
                    print('Invalid ressource file. We expect a ressources node')
                # for s in itemlist :
                # print(s)

        # with codecs.open(lang, 'w', "utf-8") as ff:
        #     ff.write("\n".join(stringsArr)  + "\n")

# Get all key list
uniqueKeys = set()
for k in langageDict:
    stringsDict = langageDict[k]
    for keys in stringsDict:
        uniqueKeys.add(keys)
uniqueKeys = OrderedSet(sorted(uniqueKeys))
# Write CSV
data = [["key"] + [k for k in langageDict]]

for key in uniqueKeys:
    elements = [key]
    for k in langageDict:
        stringsDict = langageDict[k]
        if key in stringsDict:
            elements.append(unescapeAndroidChar(stringsDict[key]))
        else:
            elements.append("")
            print("Undefined string for key " + str(key) + " in " + str(k))

    data.append(elements)

export_to_csv(data, outputFilepath)
