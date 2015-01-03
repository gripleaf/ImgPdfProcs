#! /usr/bin/env python
# -*- coding: utf-8 -*-
import thread
import threading
from FenyinGlobals import Settings
from FenyinClients import DBClient, MQSClient, OSSClient, LocalPdfClient
import time
import os
import json
import logging


def upload_to_oss(msg_body, filelist):
    jobj = json.loads(msg_body)
    for file_item in filelist:
        img_key = jobj["key"] + os.path.basename(file_item).replace(".", "-")
        _ossClient.upload_file_to_oss(img_key, file_item)


def download_from_oss(msg_body):
    jobj = json.loads(msg_body)
    _ossClient.download_file_from_oss(
        jobj["key"], os.path.join(Settings.Pdf_Path["source"], jobj["id"] + ".pdf"))


def __create_pdf_task(msg_body):
    jobj = json.loads(msg_body)
    proc = LocalPdfClient.FenyinPdfProcess(
        os.path.join(Settings.Pdf_Path["source"], jobj["id"] + ".pdf"),
        os.path.join(Settings.Pdf_Path["transformed"], jobj["id"] + ".pdf"),
        Settings.Pdf_Path["wtmkfile"])
    return proc


def handle_pdf_process(msg_body):
    # process file
    proc_pdf = __create_pdf_task(msg_body)
    proc_pdf.process_pdf()
    return proc_pdf.convert_to_image(Settings.Pdf_Path["toimg"])


def WorkerThread():
    while True:

        # get task
        msg_recv = _mqsClient.MQS_ReceiveMsg()
        if not hasattr(msg_recv, "message_body"):
            time.sleep(1)
            continue

        # download file from oss
        download_from_oss(msg_recv.message_body)

        # handle engine
        img_list = handle_pdf_process(msg_recv.message_body)

        # upload file to oss
        upload_to_oss(msg_recv.message_body, img_list)

        # delete mqs msg
        _mqsClient.MQS_DeleteMsg()


if __name__ == "__main__":
    global _ossClient, _mqsClient
    _ossClient = OSSClient.FenyinOSSClient()
    _mqsClient = MQSClient.FenyinMQSClient()

    # start the worker thread

    wh = threading.Thread(target=WorkerThread, args=(),
                          name="WorkerThread " + time.strftime("%m%d%H-%M-%S"))
    wh.start()
    while True:
        time.sleep(10)
        if not wh.is_alive():
            wh = threading.Thread(
                target=WorkerThread, args=(), name="WorkerThread " + time.strftime("%m%d%H-%M-%S"))
            print "Thread ", wh.name, "start!"
            continue
        _mqsClient.MQS_RenewMsg()


'''
    output = PdfFileWriter()
    input1 = PdfFileReader(file("test.pdf", "rb"))
    # print the title of document1.pdf
    print "title = %s" % (input1.getDocumentInfo().title)

    # add page 1 from input1 to output document, unchanged
    output.addPage(input1.getPage(0))

    # add page 2 from input1, but rotated clockwise 90 degrees
    output.addPage(input1.getPage(1))

    # add page 3 from input1, rotated the other way:
    output.addPage(input1.getPage(2))
    # alt: output.addPage(input1.getPage(2).rotateClockwise(270))

    # add page 4 from input1, but first add a watermark from another pdf:
    # page4 = input1.getPage(3)
    #watermark = PdfFileReader(file("watermark.pdf", "rb"))
    #page4.mergePage(watermark.getPage(0))

    # add page 5 from input1, but crop it to half size:
    #page5 = input1.getPage(4)
    #page5.mediaBox.upperRight = (
    #    page5.mediaBox.getUpperRight_x() / 2,
    #    page5.mediaBox.getUpperRight_y() / 2
    #)
    #output.addPage(page5)

    # print how many pages input1 has:
    #print "document1.pdf has %s pages." % input1.getNumPages()

    # finally, write "output" to document-output.pdf
    outputStream = file("document-output.pdf", "wb")
    output.write(outputStream)
    outputStream.close()

'''
