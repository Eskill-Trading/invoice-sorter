import json
import os
import re
from datetime import date
from time import sleep

import PyPDF2


def invoiceDuplicate(dest: str, version: int) :
    "Append copy number to invoice if multiples found."
    if os.path.isfile((dest[:-len(".pdf")] if not re.search(r"_\d$", dest[:-len(".pdf")]) else dest[:-len("_1.pdf")]) + f"_{str(version)}.pdf"):
        version += 1
        newDestination = invoiceDuplicate(dest, version)
    else:
        newDestination = (dest[:-len(".pdf")] if not re.search(r"_\d$", dest[:-len(".pdf")]) else dest[:-len("_1.pdf")]) + f"_{str(version)}.pdf"
    return newDestination


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
                fiscalDate = docInfo[r"/ModDate"][2:10]
                if not fiscalDate.isnumeric() or len(fiscalDate) != 8:
                    raise Exception("Bad date")
                fiscalDate = date(int(fiscalDate[0:4]), int(fiscalDate[4:6]), int(fiscalDate[6:8]))
                print("Fiscalised:", fiscalDate.strftime(r"%d %B %Y"))
                if not os.path.isdir(destination := source + os.sep + str(fiscalDate.year) + os.sep + fiscalDate.strftime("%B %Y")):
                    print("Folder(s) not found- generating now.")
                    os.makedirs(destination)
                newName = f"{invoiceNum}_{customer}_{fiscalDate.strftime(r'%Y%m%d')}.pdf"
                destination += os.sep + newName
            except Exception as error:
                print(error)
                invoice.close()

        if destination:
            if os.path.isfile(destination):
                print("Duplicate found.")
                destination = invoiceDuplicate(destination, 1)
            os.rename(sourceFile, destination)
            print("Destination:", destination, end= "\n\n")