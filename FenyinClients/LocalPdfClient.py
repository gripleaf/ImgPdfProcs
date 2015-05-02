#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import logging
# sys.path.append("..")
from FenyinGlobals import Settings
# sys.path.remove("..")


class FenyinPdfProcess:
    def __init__(self, pdffile, outfile, outimg, wtmkfile, pdf2img):
        if not pdffile.endswith(".pdf"):
            raise Exception(
                "create task error! pdf file name is not correct format(*.pdf)")
        self.pdffile = pdffile
        self.outfile = outfile
        self.imgpath = outimg
        self.wtmkfile = wtmkfile
        self.pdf2img = pdf2img
        self.script_path = os.path.join(os.path.dirname(os.path.abspath("__file__")), "FenyinClients", "watermark.jar")


    def process_pdf(self):
        '''
            :return: file of path -> success | None -> fail
        '''
        logging.info("process %s..." % self.pdffile)
        # add watermark to pdf
        res = self.__add_water_mark()

        if res == None:
            return None, None

        # convert pdf -> images
        res = self.__convert_pdf_image(res)

        if res == None:
            return None, None

        # convert images -> pdf
        res = self.__convert_btw_pdfimg(res)

        if res == None:
            logging.info("\t1)add watermark [failed]!")
            return res, None
        logging.warning("\t1)add watermark [success]!")
        return res, self.__gen_homepage_img()

    def convert_to_image(self, img_path):
        if img_path is None:
            img_path = "/tmp"
        img_path = os.path.join(
            img_path, os.path.basename(self.pdffile).replace(".pdf", ""))
        self.__create_path_re(img_path)

        # _cmd = "convert -density 200 -colorspace Gray " + self.outfile + " -transparent \"#ffffff\" " + \
        #       os.path.join(img_path, os.path.basename(self.pdffile).replace(".pdf", ".png"))

        _cmd = "sh resources/conImg.sh %s %s" % (
        self.outfile, os.path.join(img_path, os.path.basename(self.pdffile).replace(".pdf", "")))

        logging.info("running$ %s" % _cmd)
        subprocess.call(_cmd, shell=True)
        # calc img list
        img_list = os.listdir(img_path)
        return [os.path.join(img_path, file_name) for file_name in img_list]

    def __gen_homepage_img(self):
        '''generate a image(png) of the first page of pdf
        :return:image path
        '''
        _cmd = "convert -density 50 " + self.pdffile + "\\[0\\] " + self.imgpath

        res = subprocess.call(_cmd, shell=True)
        if res == 0:
            logging.info("\t2)gen home image [success]!")
            return self.imgpath
        logging.warning('\t2)gen home image [fail]!')
        return None

    def __add_water_mark(self):
        '''add watermark on pdf file
            :return: file of path -> success | None -> fail
        '''
        # java -jar XX.jar in_pdf_file watermark_image out_pdf_file
        res = subprocess.call(
            "java -jar %s Add %s %s %s > /dev/null" % (self.script_path, self.pdffile, self.wtmkfile, self.outfile),
            shell=True)

        if res == 0:
            logging.info("\t\tadd pdf image [success]!")
            return self.outfile
        logging.warning("\t\tadd pdf image [fail]!")
        return None

    def __convert_btw_pdfimg(self, imgs_path):
        ''' convert images to pdf
        :param imgs_path:
        :return: pdf file
        '''
        _cmd = "java -jar %s Convert %s %s _ > /dev/null" % (self.script_path, imgs_path, self.outfile)

        res = subprocess.call(_cmd, shell=True)
        if res == 0:
            logging.info("\t\tconvert images -> pdf [success]!")
            return self.outfile
        logging.warning("\t\tconvert images -> pdf [failed]!")
        return None


    def __convert_pdf_image(self, pdf_file):
        '''generate a image(png) of all the pdf
        :return:images path
        '''
        _path = os.path.dirname(self.pdf2img)
        if not os.path.exists(_path):
            os.mkdir(_path)
        _cmd = "convert -density 180 " + pdf_file + " " + self.pdf2img

        res = subprocess.call(_cmd, shell=True)
        if res == 0:
            logging.info("\t\t convert pdf -> images [success]!")
            return _path
        logging.warning("\t\t convert pdf -> images [failed]!")
        return None


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
        logging.info("add word: %s" % _cmd)
        subprocess.call(_cmd, shell=True)


    # add logo to image
    def __add_logo_to_image(self, img_path, logo, position=(0, 0)):
        '''TODO: you may need to judge if the paras is correct!'''
        if not os.path.exists(img_path) or not os.path.exists(logo):
            raise IOError("uncorrect image/logo path")

        _cmd = ' '.join(["convert", img_path, logo, "-gravity southeast -geometry",
                         ''.join(['+', position[0], '+', position[1]]), "-composite", img_path])
        logging.info("add logo: %s" % _cmd)
        subprocess.call(_cmd, shell=True)


if __name__ == '__main__':
    pass
    # ouput = ProcessPdf("test.pdf", "document-output.pdf", 3)
    # ConvertToImage("document-output.pdf", "tmp/test.jpg")
    # UploadToOSS("tmp/test.jpg", 3)
