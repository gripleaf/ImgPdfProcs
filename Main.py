#! /usr/bin/env python
# -*- coding: utf-8 -*-
import thread
import threading
from FenyinGlobals import Settings, MyDeamon, RandomHelper
from FenyinClients import DBClient, MQSClient, OSSClient, LocalPdfClient
import time
import os
import json
import logging
import sys


def upload_to_oss(obj_key, filelist):
    '''
        :param obj_key: file key
        :param filelist: files to upload
        :return: None
    '''
    for file_item in filelist:
        img_key = obj_key + os.path.basename(file_item).replace(".", "-")
        _ossClient.upload_file_to_oss(img_key, file_item)


def upload_img_to_oss(obj_key, img_file):
    '''
    :param obj_key: file key before upload
    :param img_file: image file path
    :return: True -> success | False -> fail
    '''
    try:
        img_key = obj_key + "-img0"
        return _ossClient.upload_file_to_oss(img_key, img_file)
    except Exception, e:
        print "[upload img file to oss]", e.message
        return False


def upload_pdf_to_oss(obj_key, pdf_file):
    '''
        :param obj_key: file key before upload
        :param pdf_file: pdf file path
        :return: True -> success | False -> fail
    '''
    try:
        pdf_key = obj_key + "-tbl"
        return _ossClient.upload_file_to_oss(pdf_key, pdf_file)
    except Exception, e:
        print "[upload pdf to oss]", e.message
        return False


def download_from_oss(obj_key, obj_id):
    '''
        @:param obj_key: file key
        @:param obj_id: file id
        @:return:s True -> success | False -> fail
    '''

    try:
        return _ossClient.download_file_from_oss(
            obj_key, os.path.join(Settings.Pdf_Path["source"], obj_id + ".pdf"))
    except Exception, ex:
        print "[download from oss]", ex.message
        return False


def check_file_on_oss(obj_key):
    '''
        @:param obj_key: file key
        @:return: True -> success | False -> fail
    '''

    try:
        return _ossClient.check_file_on_oss(obj_key)
    except Exception, ex:
        print "[check file on oss]", ex.message
        return False


def create_pdf_task(obj_id):
    '''
        :param obj_id: file id
        :return: instance -> success | None -> fail
    '''
    try:
        proc = LocalPdfClient.FenyinPdfProcess(
            os.path.join(Settings.Pdf_Path["source"], obj_id + ".pdf"),
            os.path.join(Settings.Pdf_Path["transformed"], obj_id + ".pdf"),
            os.path.join(Settings.Pdf_Path["toimg"], obj_id + ".png"),
            Settings.Pdf_Path["wtmkfile"])
        return proc
    except Exception, e:
        return None


def handle_pdf_process(proc_pdf):
    '''
        :param proc_pdf: instance of LocalPdfClient.FenyinPdfProcess
        :return: string(file path) -> success | None -> fail
    '''
    try:
        # process file
        return proc_pdf.process_pdf()
        # return proc_pdf.convert_to_image(Settings.Pdf_Path["toimg"])
    except Exception, e:
        print "[handle pdf process]", e.message
        return None


def WorkerThread():
    while True:

        # task beginning
        print "\n>>>>>>>>>>>>>>>>>"
        # get task
        msg_recv = _mqsClient.MQS_ReceiveMsg()
        if not hasattr(msg_recv, "message_body"):
            time.sleep(1.5)
            continue

        try:
            jobj = json.loads(msg_recv.message_body)

            for ite in Settings.Msg_Format:
                if not jobj.has_key(ite):
                    raise ValueError("necessary key lack like " + ite)

        except Exception, e:
            print "load json failed", e.message

        # check file on oss
        res = check_file_on_oss(jobj['key'])

        # if file on oss, then delete msg
        if res == True:
            # delete mqs msg
            _mqsClient.MQS_DeleteMsg()
            continue

        # download file from oss
        res = download_from_oss(jobj["key"], jobj["id"])

        # if file download failed, then delete msg
        if res == False:
            # delete mqs msg
            _mqsClient.MQS_DeleteMsg()
            continue

        # create the pdf process task
        proc_pdf = create_pdf_task(jobj["id"])

        # if proc_pdf is None, then delete msg
        if proc_pdf is None:
            # delete mqs msg
            _mqsClient.MQS_DeleteMsg()
            continue

        # handle engine
        res_pdf, res_img = handle_pdf_process(proc_pdf)

        # upload file to oss
        # upload_to_oss(jobj["key"], res)
        if res_pdf is not None:
            upload_pdf_to_oss(jobj["key"], res_pdf)

        if res_img is not None:
            upload_img_to_oss(jobj["key"], res_img)

        # delete mqs msg
        _mqsClient.MQS_DeleteMsg()

        # task ended
        print "<<<<<<<<<<<<<<<<<"


def main():
    global _ossClient, _mqsClient
    _ossClient = OSSClient.FenyinOSSClient(Settings)
    _mqsClient = MQSClient.FenyinMQSClient(Settings)

    # start the worker thread

    wh = threading.Thread(target=WorkerThread, args=(),
                          name="WorkerThread " + time.strftime("%m%d%H-%M-%S"))
    wh.setDaemon(True)
    wh.start()

    while True:
        time.sleep(10)
        if not wh.is_alive():
            wh = threading.Thread(
                target=WorkerThread, args=(), name="WorkerThread " + time.strftime("%m%d%H-%M-%S"))
            wh.setDaemon(True)
            wh.start()
            print "Thread ", wh.name, "start!"
            continue
        _mqsClient.MQS_RenewMsg()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "****FRONT****"
        main()
    else:
        print "***BACK****"
        if sys.argv[1].upper() == "START":
            MyDeamon.daemonize(Settings.PidPath + RandomHelper.gen_num_key(5) + ".pid", main)
        elif sys.argv[1].upper() == "STOP":
            MyDeamon.del_all_pids(Settings.PidPath)
        else:
            print "You have only [start|stop] to run."


