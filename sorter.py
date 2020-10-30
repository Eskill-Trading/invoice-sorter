import json
import os
import re
from datetime import datetime
from time import sleep

import PyPDF2

# Load config file
with open("config.json") as conf:
    config = json.load(conf)
    source = config["reprint"]
    regex = config["regex"]


while not sleep(1):
    # Locate files in Reprint folder
    invoices = []
    for root, dirs, files in os.walk(source):
        for file in files:
            if re.search(regex["pdf"], file):
                invoices.append(file)
        if (root == source):
            break

    if not invoices:
        continue
    print("Pending PDFs:", invoices, end= "\n\n")


    # Get invoice info, rename pdf and move to correct folder
    for file in invoices:
        sourceFile = source + os.sep + file
        destination = ""
        with open(sourceFile, "rb") as invoice:
            try:
                pdf = PyPDF2.PdfFileReader(invoice)
                docInfo = pdf.getDocumentInfo()
                if not (invoiceNum := re.findall(regex["invoice number"], docInfo["/Title"])[0]):
                    raise Exception("No invoice number")
                print("Invoice:", invoiceNum)
                text = pdf.getPage(0).extractText()
                if not (customer := re.findall(regex["customer"], text)[0]):
                    raise Exception("Unable to find customer")
                print("Customer:", customer)
                dateTime = docInfo[r"/ModDate"][2:-7]
                if not dateTime.isnumeric() or len(dateTime) != 14:
                    raise Exception("Bad datetime")
                dateTime = datetime(int(dateTime[0:4]), int(dateTime[4:6]), int(dateTime[6:8]), int(dateTime[8:10]), int(dateTime[10:12]), int(dateTime[12:]))
                print("Fiscalised:", dateTime.strftime(r"%d %B %Y %H:%M:%S"))
                if not os.path.isdir(destination = source + os.sep + str(dateTime.year) + os.sep + dateTime.strftime("%B %Y")):
                    print("Folder(s) not found- generating now.")
                    os.makedirs(destination)
                newName = f"{invoiceNum}_{customer}_{dateTime.strftime('%Y%m%d_%H%M%S')}.pdf"
                destination += os.sep + newName
            except Exception as error:
                print(error)
                invoice.close()
        if destination:
            os.rename(sourceFile, destination)
            print("Destination:", destination, end= "\n\n")