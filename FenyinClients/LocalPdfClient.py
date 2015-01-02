#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from pyPdf import PdfFileWriter, PdfFileReader
import sys
import os

# sys.path.append("..")
from FenyinGlobals import Settings
# sys.path.remove("..")


class FenyinPdfProcess:

    def __init__(self, pdffile, outfile, wtmkfile):
        if not pdffile.endswith(".pdf"):
            raise Exception(
                "create task error! pdf file name is not correct format(*.pdf)")
        self.pdffile = pdffile
        self.outfile = outfile
        self.wtmkfile = wtmkfile

    def __add_water_mark(self, paget, tb):
        watermark = PdfFileReader(file(self.wtmkfile, "rb"))

        paget.mergePage(watermark.getPage(tb).rotateClockwise(270))

    def process_pdf(self):
        outputs = PdfFileWriter()
        intputs = PdfFileReader(file(self.pdffile, "rb"))
        print "tilte = %s " % (intputs.getDocumentInfo().title)

        length = min(intputs.getNumPages(), Settings.tbl_length)
        for i in range(length):
            paget = intputs.getPage(i)
            # add water mark to page
            self.__add_water_mark(paget, i)

            outputs.addPage(paget)

        outputStream = file(self.outfile, "wb")
        outputs.write(outputStream)
        outputStream.close()

    def __create_path_re(self, path_to_create):
        cur_path = ""
        for pp in path_to_create.split(os.path.sep):
            if pp == "":
                cur_path="/"
                continue
            cur_path = os.path.join(cur_path, pp)
            if os.path.isdir(cur_path):
                continue
            else:
                os.mkdir(cur_path)

    def convert_to_image(self, img_path):
        if img_path == None:
            img_path = "/tmp"
        img_path = os.path.join(
            img_path, os.path.basename(self.pdffile).replace(".pdf", ""))
        self.__create_path_re(img_path)
        subprocess.call("convert " + self.outfile + " " +
                        os.path.join(
                            img_path, os.path.basename(self.pdffile).replace(".pdf", ".jpg")),
                        shell=True)
        # calc img list
        img_list = os.listdir(img_path)
        return [os.path.join(img_path, file_name) for file_name in img_list]


if __name__ == '__main__':
    proc = FenyinPdfProcess(
        "tmp/test.pdf", "tmp/document-output.pdf", "tmp/test.pdf")
    proc.process_pdf(Settings.tbl_length)
    proc.convert_to_image("tmp/test.jpg")

    #ouput = ProcessPdf("test.pdf", "document-output.pdf", 3)
    #ConvertToImage("document-output.pdf", "tmp/test.jpg")
    #UploadToOSS("tmp/test.jpg", 3)
