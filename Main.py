#! /usr/bin/env python
# -*- coding: utf-8 -*-
import thread
import threading
from FenyinGlobals import Settings, MyDeamon, RandomHelper
from FenyinClients import MQSClient, OSSClient, LocalPdfClient
from FenyinClients.FenyinDBClient import FenyinDBClient
import time
import os
import json
import logging
import urllib
import sys


def upload_to_oss(obj_key, filelist):
    '''
        @:param obj_key: file key
        @:param filelist: files to upload
        @:return: None
    '''
    for file_item in filelist:
        img_key = obj_key + os.path.basename(file_item).replace(".", "-")
        _ossClient.upload_file_to_oss(img_key, file_item)


def upload_img_to_oss(obj_key, img_file):
    '''
        @:param obj_key: file key before upload
        @:param img_file: image file path
        @:return: True -> success | False -> fail
    '''
    try:
        img_key = obj_key + "-img0"
        return _ossClient.upload_file_to_oss(img_key, img_file)
    except Exception, e:
        logging.warning("[upload img file to oss] %s" % e.message)
        return False


def upload_pdf_to_oss(obj_key, pdf_file):
    '''
        @:param obj_key: file key before upload
        @:param pdf_file: pdf file path
        @:return: True -> success | False -> fail
    '''
    try:
        pdf_key = obj_key + "-tbl"
        return _ossClient.upload_file_to_oss(pdf_key, pdf_file)
    except Exception, e:
        logging.warning("[upload pdf to oss] %s" % e.message)
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
        logging.warning("[download from oss] %s" % ex.message)
        return False


def check_file_on_oss(obj_key):
    '''
        @:param obj_key: file key
        @:return: True -> success | False -> fail
    '''

    try:
        return _ossClient.check_file_on_oss(obj_key)
    except Exception, ex:
        logging.warning("[check file on oss] %s" % ex.message)
        return False


def create_pdf_task(obj_id):
    '''
        @:param obj_id: file id
        @:return: instance -> success | None -> fail
    '''
    try:
        proc = LocalPdfClient.FenyinPdfProcess(
            os.path.join(Settings.Pdf_Path["source"], obj_id + ".pdf"),
            os.path.join(Settings.Pdf_Path["transformed"], obj_id + ".pdf"),
            os.path.join(Settings.Pdf_Path["toimg"], obj_id + ".png"),
            Settings.Pdf_Path["wtmkfile"],
            os.path.join(Settings.Pdf2Img, obj_id, obj_id))
        return proc
    except Exception, e:
        logging.warning("[create pdf task] %s" % e.message)
        return None


def handle_pdf_process(proc_pdf):
    '''
        @:param proc_pdf: instance of LocalPdfClient.FenyinPdfProcess
        @:return: string(file path) -> success | None -> fail
    '''
    try:
        # process file
        return proc_pdf.process_pdf()
        # return proc_pdf.convert_to_image(Settings.Pdf_Path["toimg"])
    except Exception, e:
        logging.warning("[handle pdf process] %s" % e.message)
        return None


def handle_callback(url_cb):
    '''callback to finish the task
        @:param url_cb: the url of callback
        @:return: True -> success | False -> fail
    '''
    if url_cb is None or url_cb == "":
        return True
    try:
        logging.info(urllib.urlopen(url_cb).read())
        return True
    except Exception, ex:
        logging.warning("[handle callback] %s" % ex.message)
        return False


def record_mqs_message(jobj):
    ''' record mqs message into sqlite db
    :param jobj: message dict
    :return:
    '''
    try:
        _sqlClient.set_mqs_message(jobj)
    except Exception, ex:
        logging.warning("[record mqs message] %s" % ex.message)


def check_task_security(jobj):
    ''' check current task is security to do
    :param jobj: message dict
    :return: True -> security, False -> dangerous
    '''
    if os.path.isfile(os.path.join(Settings.Pdf_Path["source"], jobj["id"] + ".pdf")):
        return False
    return True


def remove_all_useless_files(jobj):
    '''remove all the useless files we don't need
    :param jobj: message dict
    :return: True -> yes, False -> no
    '''
    try:
        # source file
        source_file = os.path.join(Settings.Pdf_Path["source"], jobj["id"] + ".pdf")
        # pdf2image path
        p2i_path = os.path.join(Settings.Pdf2Img, jobj["id"])
        # to image file
        img_file = os.path.join(Settings.Pdf_Path["toimg"], jobj["id"] + ".png")
        # transformed file
        trans_file = os.path.join(Settings.Pdf_Path["transformed"], jobj["id"] + ".pdf")

        _filelist = [source_file, img_file, trans_file]
        if os.path.isdir(p2i_path):
            _filelist.extend([os.path.join(p2i_path, _filename) for _filename in os.listdir(p2i_path)])

        for _file in _filelist:
            if os.path.isfile(_file):
                os.remove(_file)

        if os.path.isdir(p2i_path) and len(os.listdir(p2i_path)) == 0:
            os.rmdir(p2i_path)
    except Exception, e:
        logging.warning("[remove file failed] %s" % e.message)


def WorkerThread():
    try:
        while True:

            # task beginning
            logging.info(">>>>>>>>>>>>>>>>>")
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
                logging.error("load json failed %s" % e.message)

            # check file on oss
            res = check_file_on_oss(jobj['key'] + "-tbl") and check_file_on_oss(jobj['key'] + "-img0")

            # if file on oss, then delete msg
            if res == True:
                logging.info("&&files has already on oss&&")
                # if jobj has key callback, then call it.
                if jobj.has_key("callback"):
                    handle_callback(jobj["callback"])
                # delete mqs msg
                _mqsClient.MQS_DeleteMsg()
                continue

            # record all the message
            # record_mqs_message(jobj)

            # task process begin
            # change the - to normal char
            jobj["id"].replace("-", "x")

            # security check
            res = check_task_security(jobj)

            # if not safe enough to handle the task
            if not res:
                logging.info("!!!Not Safe Enough to process!!!")
                return

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

            if jobj.has_key("callback"):
                handle_callback(jobj["callback"])

            # delete mqs msg
            _mqsClient.MQS_DeleteMsg()

            # remove file
            remove_all_useless_files(jobj)

            # task ended
            logging.info("<<<<<<<<<<<<<<<<<")

    except Exception, e:
        # throw a dead error that will kill the thread, it's a very sad thing.
        logging.error("Evil Error: %s" % e.message)


def main():
    global _ossClient, _mqsClient, _sqlClient
    _ossClient = OSSClient.FenyinOSSClient(Settings)
    _mqsClient = MQSClient.FenyinMQSClient(Settings)
    _sqlClient = FenyinDBClient(Settings)

    # start the worker thread

    wh = threading.Thread(target=WorkerThread, args=(),
                          name="WorkerThread " + time.strftime("%m%d%H-%M-%S"))
    wh.setDaemon(True)
    wh.start()

    while True:
        time.sleep(10)
        # os.system('sh resources/monitor.sh')
        if not wh.is_alive():
            wh = threading.Thread(
                target=WorkerThread, args=(), name="WorkerThread " + time.strftime("%m%d%H-%M-%S"))
            wh.setDaemon(True)
            wh.start()
            logging.warning("Thread %s start!" % wh.name)
            continue

        _mqsClient.MQS_RenewMsg()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.info("****FRONT****")
        main()
    else:
        logging.info("***BACK****")
        if sys.argv[1].upper() == "START":
            MyDeamon.daemonize(Settings.PidPath + RandomHelper.gen_num_key(5) + ".pid", main)
        elif sys.argv[1].upper() == "STOP":
            MyDeamon.del_all_pids(Settings.PidPath)
        else:
            logging.warning("You have only [start|stop] to run.")


