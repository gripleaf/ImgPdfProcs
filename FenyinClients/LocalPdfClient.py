#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
import os
from StringIO import StringIO
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

    def __add_water_mark(self, paget):
        imgTemp = StringIO()
        imgDoc = canvas.Canvas(imgTemp)

        imgDoc.drawImage(self.wtmkfile, 0, 0, 400, 200)
        imgDoc.save()

        print paget.mediaBox.getWidth(), paget.mediaBox.getHeight()
        self.watermark = PdfFileReader(StringIO(imgTemp.getvalue()), strict=False).getPage(0)

        self.watermark.mergePage(paget)
        return self.watermark

    def process_pdf(self):
        print "process", self.pdffile, "..."
        outputs = PdfFileWriter()
        try:
            intputs = PdfFileReader(file(self.pdffile, "rb"), strict=False)
        except Exception, ex:
            print "fix pdf ", self.pdffile, "..."
            return "error"
        # print "tilte = %s " % (intputs.getDocumentInfo().title)

        length = min(intputs.getNumPages(), Settings.tbl_length)
        for i in range(length):
            paget = intputs.getPage(i)
            # add water mark to page
            paget = self.__add_water_mark(paget)

            outputs.addPage(paget)

        outputStream = file(self.outfile, "wb")
        outputs.write(outputStream)
        outputStream.close()
        return self.outfile

    def __create_path_re(self, path_to_create):
        cur_path = ""
        for pp in path_to_create.split(os.path.sep):
            if pp == "":
                cur_path = "/"
                continue
            cur_path = os.path.join(cur_path, pp)
            if os.path.isdir(cur_path):
                continue
            else:
                os.mkdir(cur_path)

    def convert_to_image(self, img_path):
        if img_path is None:
            img_path = "/tmp"
        img_path = os.path.join(
            img_path, os.path.basename(self.pdffile).replace(".pdf", ""))
        self.__create_path_re(img_path)

        _cmd = "convert -density 200 -colorspace Gray " + self.outfile + " -transparent \"#ffffff\" " + \
               os.path.join(img_path, os.path.basename(self.pdffile).replace(".pdf", ".png"))

        print _cmd
        subprocess.call(_cmd, shell=True)
        # calc img list
        img_list = os.listdir(img_path)
        return [os.path.join(img_path, file_name) for file_name in img_list]

    def mogrify_image(self, img_path):
        pass


    def __translate_words_for_add(self, words):
        if os.path.exists(words):
            return words
        open("/tmp/" + str(words.__hash__()), 'a').write(words)
        return "/tmp/" + str(words.__hash__())

    # add word to image
    def __add_word_to_image(self, img_path, words, size, position=(0, 0), font=None):
        '''TODO: you may need to judge if the paras is correct!'''
        if not type(size) == int:
            raise TypeError("uncorrect size type")

        if not os.path.exists(img_path):
            raise IOError("uncorrect image path")

        if words is None:
            raise ValueError("uncorrect value of words")

        if font is not None and os.path.exists(font):
            _cmd = ' '.join(['mogrify -font', font, ' -pointsize ', size,
                             ' -fill black -weight bolder -gravity southeast -annotate',
                             ''.join(['+', position[0], '+', position[1]]),
                             ''.join(['@"', self.__translate_words_for_add(words), '"']),
                             img_path])

        else:
            _cmd = ' '.join(
                ['mogrify -pointsize ', size, ' -fill black -weight bolder -gravity southeast -annotate',
                 ''.join(['+', position[0], '+', position[1]]), words, img_path])
        print "add word:", _cmd
        subprocess.call(_cmd, shell=True)


    # add logo to image
    def __add_logo_to_image(self, img_path, logo, position=(0, 0)):
        '''TODO: you may need to judge if the paras is correct!'''
        if not os.path.exists(img_path) or not os.path.exists(logo):
            raise IOError("uncorrect image/logo path")

        _cmd = ' '.join(["convert", img_path, logo, "-gravity southeast -geometry",
                         ''.join(['+', position[0], '+', position[1]]), "-composite", img_path])
        print "add logo:", _cmd
        subprocess.call(_cmd, shell=True)


if __name__ == '__main__':
    proc = FenyinPdfProcess(
        "tmp/test.pdf", "tmp/document-output.pdf", "tmp/test.pdf")
    proc.process_pdf(Settings.tbl_length)
    proc.convert_to_image("tmp/test.png")

    # ouput = ProcessPdf("test.pdf", "document-output.pdf", 3)
    # ConvertToImage("document-output.pdf", "tmp/test.jpg")
    # UploadToOSS("tmp/test.jpg", 3)
