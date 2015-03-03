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
import sys


def upload_to_oss(obj_key, filelist):
    for file_item in filelist:
        img_key = obj_key + os.path.basename(file_item).replace(".", "-")
        _ossClient.upload_file_to_oss(img_key, file_item)


def upload_pdf_to_oss(obj_key, pdf_file):
    pdf_key = obj_key + "-tbl"
    _ossClient.upload_file_to_oss(pdf_key, pdf_file)


def download_from_oss(obj_key, obj_id):
    _ossClient.download_file_from_oss(
        obj_key, os.path.join(Settings.Pdf_Path["source"], obj_id + ".pdf"))


def create_pdf_task(obj_id):
    proc = LocalPdfClient.FenyinPdfProcess(
        os.path.join(Settings.Pdf_Path["source"], obj_id + ".pdf"),
        os.path.join(Settings.Pdf_Path["transformed"], obj_id + ".pdf"),
        Settings.Pdf_Path["wtmkfile"])
    return proc


def handle_pdf_process(proc_pdf):
    # process file
    return proc_pdf.process_pdf()
    # return proc_pdf.convert_to_image(Settings.Pdf_Path["toimg"])


def WorkerThread():
    while True:

        # task beginning
        print "\n>>>>>>>>>>>>>>>>>"
        # get task
        msg_recv = _mqsClient.MQS_ReceiveMsg()
        if not hasattr(msg_recv, "message_body"):
            time.sleep(1)
            continue

        try:
            jobj = json.loads(msg_recv.message_body)

            for ite in Settings.Msg_Format:
                if not jobj.has_key(ite):
                    raise ValueError("necessary key lack like " + ite)

        except Exception, e:
            print "load json failed", e.message

        # download file from oss
        download_from_oss(jobj["key"], jobj["id"])

        # create the pdf process task
        proc_pdf = create_pdf_task(jobj["id"])

        # handle engine
        res = handle_pdf_process(proc_pdf)

        # upload file to oss
        # upload_to_oss(jobj["key"], res)
        if res != "error":
            upload_pdf_to_oss(jobj["key"], res)

        # delete mqs msg
        _mqsClient.MQS_DeleteMsg()

        # task ended
        print "<<<<<<<<<<<<<<<<<"


def daemonize():
    cwd = os.getcwd()

    try:
        pid = os.fork()
        if pid > 0:  # father thread exit
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)

    # decoup from parent environment
    os.chdir(cwd)
    os.setsid()
    os.umask(0)

    try:
        pid = os.fork()
        if pid > 0:  # father thread exit
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = file("/dev/null", "r")
    so = file("/dev/null", "w")
    se = file("/dev/null", "w")
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # write pid file
    main()


def main():
    global _ossClient, _mqsClient
    _ossClient = OSSClient.FenyinOSSClient()
    _mqsClient = MQSClient.FenyinMQSClient()

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
        daemonize()

