# @ John Bills
# @ johnbills64@gmail.com

import datetime
import io
import os
import re
import shutil
import subprocess
import time
import barcode
import chardet
import openpyxl
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from PyPDF2 import PdfReader, PdfWriter

# get date
date = str(datetime.datetime.now())
date = date.replace(' ','__')
date = date.replace(':','-')
date = date[:-7]
labelDate = str(datetime.datetime.now())
labelDate = labelDate.replace('-','/')
labelDate = labelDate[:-16]

# excel file preparation
masterXL = openpyxl.load_workbook("Templates/Master Template.xlsx")
masterXLsh = masterXL['Master Inventory']
exportedXL = "Imaging Report_" + date + ".xlsx"

# set misc directories
barcodeDir = "Barcode PDFs/" + date[:-10] + "/"
imageDir = "HW_Inventory/"
tempDir = "Templates/temp/"
templateDir = "Templates/"
reportsDir = "Inventory Reports/"
print("Report Directory: " + imageDir)
try:
    os.mkdir(barcodeDir)
    print("Barcode PDFs will be sent to: " + barcodeDir)
except FileExistsError:
    print("Barcode PDFs will be sent to: " + barcodeDir)

# misc variables
currentRow = 0

print("Program Started...")

while True:
    try:
        for txtFile in os.listdir(imageDir):

            # assign path to txt file
            file = os.path.join(imageDir, txtFile)

            # get file encoding type
            if ".txt" in file:
                with open(file, 'rb') as f:
                    result = chardet.detect(f.read())

                # get rid of garbage within inbound report
                with open(file, 'r', encoding=result['encoding']) as f:
                    lines = f.readlines()
                    lines = lines[2:]
                    if len(lines) == 24:
                        del lines[8]
                    if len(lines) > 17:
                        del lines[10]
                        del lines[10]
                        del lines[10]
                        del lines[10]
                        del lines[10]

                        # put data in to dictionary for processing, also remove remaining garbage
                        k = []
                        for i in lines:
                            j = i.replace('  ', '')
                            k.append(j)
                        k = k[:-3]
                        k= [x[:-1] for x in k]
                        data = dict(line.strip().split(':', 1) for line in k)

                        # print data to spreadsheet
                        if type(data['CsManufacturer']) is type('string'):
                            data['CsProcessors'] = data['CsProcessors'].replace('{', '')
                            data['CsProcessors'] = data['CsProcessors'].replace('}', '')
                            biosSeralNumber = data['BiosSeralNumber '][1:]
                            masterXLsh['A' + str(currentRow + 2)] = data['CsManufacturer']
                            masterXLsh['B' + str(currentRow + 2)] = data['CsModel ']
                            masterXLsh['C' + str(currentRow + 2)] = biosSeralNumber
                            masterXLsh['D' + str(currentRow + 2)] = data['CsSystemSKUNumber ']
                            masterXLsh['E' + str(currentRow + 2)] = data['OsName']
                            masterXLsh['F' + str(currentRow + 2)] = data['OsVersion ']
                            masterXLsh['G' + str(currentRow + 2)] = data['OsArchitecture']
                            masterXLsh['H' + str(currentRow + 2)] = data['CsProcessors']
                            masterXLsh['L' + str(currentRow + 2)] = data['FriendlyName ']
                            masterXLsh['M' + str(currentRow + 2)] = data['SerialNumber ']
                            masterXLsh['N' + str(currentRow + 2)] = data['MediaType']
                            masterXLsh['O' + str(currentRow + 2)] = data['HealthStatus ']

                            # derive intel core generation based on CsProcessors value
                            proGen = data['CsProcessors']
                            proGen5 = re.findall("[0-9][0-9][0-9][0-9][0-9]", proGen)
                            proGen4 = re.findall("[0-9][0-9][0-9][0-9]", proGen)
                            proGen5 = ''.join(proGen5)
                            proGen4 = ''.join(proGen4)
                            if len(str(proGen5)) != 0:
                                proGen = (proGen5[:2] + "th Gen")
                            else:
                                proGen = (proGen4[:1] + "th Gen")

                            # handling for AMD, Pentium and Xeon processors
                            if "AMD" in data['CsProcessors']:
                                proGen = ''
                            if "Xeon" in data['CsProcessors']:
                                proGen = ''
                            if "Pentium" in data['CsProcessors']:
                                proGen = ''
                            else:
                                masterXLsh['I' + str(currentRow + 2)] = proGen
                            cores = int(data['CsNumberOfLogicalProcessors '])/2
                            masterXLsh['J' + str(currentRow + 2)] = cores

                            # translate memory amount into GB and print to spreadsheet
                            mem = (int(data['CsPhyicallyInstalledMemory']) / 1000000)
                            mem = int(mem)
                            mem = str(mem) + "GB"
                            masterXLsh['K' + str(currentRow + 2)] = mem

                            # translate storage into GB and print to spreadsheet
                            size = (int(data['Size ']) / 1000000000)
                            size = int(size)
                            masterXLsh['P' + str(currentRow + 2)] = str(size) + "GB"

                            # label generation
                            barcode.PROVIDED_BARCODES
                            code128 = barcode.get_barcode_class('code128')
                            seralBarcode = code128(biosSeralNumber)
                            seralBarcodeOut = seralBarcode.save(tempDir + 'SeralBarcodeOut',
                                                    {"module_width": .35, "module_height": 8, "font_size": 0, "text_distance": 0,
                                                     "quiet_zone": 0})
                            skuBarcode = code128(data['CsSystemSKUNumber '])
                            skuBarcodeOut = skuBarcode.save(tempDir + 'skuBarcodeOut',
                                                    {"module_width": .38, "module_height": 8, "font_size": 0, "text_distance": 0,
                                                     "quiet_zone": 0})
                            # asset tag creation
                            packet = io.BytesIO()
                            c = canvas.Canvas(packet)

                            # merge SVG files to PDF
                            drawing = svg2rlg(tempDir + "skuBarcodeOut.svg")
                            renderPDF.draw(drawing, c, 105, 0)
                            drawing = svg2rlg(tempDir + "SeralBarcodeOut.svg")
                            renderPDF.draw(drawing, c, 105, 43)

                            # write text, Vera font used for availability. Include reportlab library in distro!
                            pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
                            pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
                            pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
                            pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
                            c.setFont("Vera", 10)
                            c.drawString(2, 75, "SN:" + biosSeralNumber)
                            c.drawString(227, 75, labelDate)
                            c.drawString(2, 2, "SKU:" + data['CsSystemSKUNumber '][1:])
                            c.setFont("Vera", 8)

                            # format text output
                            manufacturer = data['CsManufacturer']
                            if len(data['CsManufacturer']) > 6:
                                manufacturer = ''
                            if "Intel(R) Core(TM)" in data['CsProcessors']:
                                processorTrim = data['CsProcessors'][:-10]
                                processorTrim = processorTrim[-12:]
                                c.drawCentredString(143, 30,
                                                      manufacturer + data['CsModel '] + " " + processorTrim + " " + str(
                                                          mem) + " RAM" + " " + str(size) + "GB" + " " + data[
                                                          'MediaType'])

                            # save canvas
                            c.save()

                            # print canvas to PDF
                            packet.seek(0)
                            barcodePDF = PdfReader(packet)
                            with open(templateDir + "Master_Blank.pdf", "rb") as f:
                                templatePdf = PdfReader(f)
                                writer = PdfWriter()
                                page = templatePdf.pages[0]
                                page.merge_page(barcodePDF.pages[0])
                                writer.add_page(page)
                                output_stream = open(biosSeralNumber + ".pdf", "wb")
                                writer.write(output_stream)
                                output_stream.close()

                            # remove potential duplicate files to prevent errors
                            if os.path.exists(barcodeDir + biosSeralNumber + ".pdf"):
                                os.remove(barcodeDir + biosSeralNumber + ".pdf")

                            # move PDF to barcode dir
                            shutil.move(biosSeralNumber + ".pdf", barcodeDir)
                            time.sleep(10)

                            # print out barcode
                            subprocess.Popen(["start", "Acrobat.exe", "/t", barcodeDir + biosSeralNumber + ".pdf"], shell=True)

                            # remove temp barcode files
                            os.remove(tempDir + 'skuBarcodeOut.svg')
                            os.remove(tempDir + 'SeralBarcodeOut.svg')
                            for artefact in os.listdir(tempDir):
                                if ".pdf" in artefact:
                                    os.remove(artefact)

                        currentRow = currentRow + 1
                        masterXL.save(reportsDir + "Imaging_Report_" + date + ".xlsx")
                        print("Information exported to: " + exportedXL)
                        waiting = False
                    else:
                        time.sleep(5)
                        waiting = True

                # remove temp file if not waiting on partial report
                if not waiting:
                    os.remove(file)

    # error handling
    except IndexError:
        print("Incomplete file detected(Index Error): " + file)
    except PermissionError:
        time.sleep(5)
    except shutil.Error:
        print("shutil.Error, removing duplicate file...")
        os.remove(file)
        print("Duplicate file removed.")

wait = input()
