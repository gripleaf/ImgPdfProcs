#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import subprocess

importTimes = 0

# a method to create path
def __create_path_re(path_to_create):
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


# create the path we needed
def __check_create_path():
    try:
        # tmp file
        __create_path_re(Tmp_Path)
        # pdf file
        __create_path_re(Pdf_Path["source"])
        __create_path_re(Pdf_Path["transformed"])
        __create_path_re(Pdf_Path["toimg"])
        # log path
        __create_path_re(os.path.dirname(LogFile))
        # pid path
        __create_path_re(PidPath)
    except Exception, ex:
        print "create path failed!\n>>>>"
        print ex, "\n<<<<"


# check the network is connected?
def __check_network_connect():
    global OSSFrom, OSSTo, MQS
    if True or OSSFrom["ServerName"].count("-internal."):
        print "network check is cancel."
        return
    res = subprocess.call("ping -c 1 -t 1 " + OSSFrom["ServerName"] + " > /dev/null", shell=True)
    res += subprocess.call("ping -c 1 -t 2 " + OSSTo["ServerName"] + " > /dev/null", shell=True)
    res += subprocess.call("ping -c 1 -t 3 " + MQS["ServerName"] + " > /dev/null", shell=True)
    if not res == 0:
        print "network is not connected!"
        sys.exit(-1)
    print "network is ok!"


# read the config file and check if system is ready to run
def _readconfigfiles(config_file="config.json"):
    global AccessId, AccessKey, OSSFrom, OSSTo, MQS, LogFile, tbl_length, Pdf_Path, Tmp_Path, Msg_Format, PidPath, Sqlite
    if not os.path.isfile(config_file):
        raise Exception(
            "File not found!(" + os.path.abspath(os.path.curdir) + " , " + config_file + " }")

    try:
        json_txt = open(config_file, "r+").readlines()
        jsobj = json.loads("".join(json_txt))
        AccessId = jsobj["AccessId"]
        AccessKey = jsobj["AccessKey"]
        OSSTo = jsobj["OSSTo"]
        OSSFrom = jsobj["OSSFrom"]
        MQS = jsobj["MQS"]
        LogFile = jsobj["LogFile"]
        LogFile = LogFile + str(os.getpid()) + ".log"
        PidPath = jsobj["PidPath"]
        tbl_length = int(jsobj["tbl_length"])
        Tmp_Path = jsobj["Tmp_Path"]
        Pdf_Path = jsobj["Pdf_Path"]
        Sqlite = jsobj["Sqlite"]  # not necessary for program
        if jsobj.has_key("Msg_Format"):
            Msg_Format = jsobj["Msg_Format"]
        else:
            Msg_Format = []
    except Exception, ex:
        print "read config file failed! \n>>>>"
        print ex, "\n<<<<"
        sys.exit(-1)

    __check_create_path()
    __check_network_connect()
    Pdf_Path.setdefault("")


def _initialize_fenyin_log():
    global LogFile
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename=LogFile,
                        filemode='w')

    # add a handle for writing message on console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logging.getLogger('').addHandler(ch)


def InitOnce():
    _readconfigfiles()
    _initialize_fenyin_log()


if __name__ == "__main__":
    print "this py script is used to read the json config file"

# init
else:
    global importTimes
    importTimes += 1
    # run the once function
    if importTimes < 2:
        InitOnce()
        importTimes += 1
