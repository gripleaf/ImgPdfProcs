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

        # task beginning
        print "\n>>>>>>>>>>>>>>>>>"
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

        # task ended
        print "<<<<<<<<<<<<<<<<<"


def daemonize():
    cwd = os.getcwd()

    try:
        pid = os.fork()
        if pid > 0:
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
        if pid > 0:
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
    os.dup2(si.fileno(),sys.stdin.fileno())
    os.dup2(so.fileno(),sys.stdout.fileno())
    os.dup2(se.fileno(),sys.stderr.fileno())

    #write pid file
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
    # daemonize()
    main()

