#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import sys
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
        self.script_path = os.path.join(os.path.dirname(os.path.abspath("__file__")), "FenyinClients", "watermark.jar")

    def __add_water_mark(self):
        '''add watermark on pdf file
            :return: file of path -> success | None -> fail
        '''
        # java -jar XX.jar in_pdf_file watermark_image out_pdf_file
        res = subprocess.call(
            "java -jar %s %s %s %s > /dev/null" % (self.script_path, self.pdffile, self.wtmkfile, self.outfile),
            shell=True)
        if res == 0:
            return self.outfile
        return None

    def process_pdf(self):
        '''
            :return: file of path -> success | None -> fail
        '''
        print "process", self.pdffile, "..."
        return self.__add_water_mark()

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
    pass
    # ouput = ProcessPdf("test.pdf", "document-output.pdf", 3)
    # ConvertToImage("document-output.pdf", "tmp/test.jpg")
    # UploadToOSS("tmp/test.jpg", 3)
