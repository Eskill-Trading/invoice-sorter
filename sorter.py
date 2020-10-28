import json
import os
import re


# Load config file
with open("config.json") as conf:
    config = json.load(conf)

source = config["reprint"]


# Locate files in Reprint folder
invoices = []
for root, dirs, files in os.walk(source):
    print("Root: ", root)
    print("Folders: ", dirs)
    print("Files: ", files)
    print()
    for file in files:
        if re.search(r".\.pdf$", file):
            invoices.append(file)
    if (root == source):
        break

print(invoices)
