# Invoice Sorter
Program to sort fiscalised invoices.

The program was designed for a scenario in which Signus fiscal software is in use,
in which PDFs are generated by PDF Creator and passed on to Signus. The invoices are picked up
in the reprint folder (designated in config.json) after being fiscalised by Signus. They are then
sorted into folders by year, then by month in said reprint folder.

**Note: the program expects to be run from the same directory as the config.json**
