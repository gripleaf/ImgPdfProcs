#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys

importTimes = 0


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


def __check_create_path():
    try:
        # tmp file
        __create_path_re(Tmp_Path)
        # pdf file
        __create_path_re(Pdf_Path["source"])
        __create_path_re(Pdf_Path["transformed"])
        __create_path_re(Pdf_Path["toimg"])
        # log path
        __create_path_re(os.path.dirname(LogPath))
    except Exception, ex:
        print "create path failed!\n>>>>"
        print ex, "\n<<<<"


def __readconfigfiles(config_file="config.json"):
    global AccessId, AccessKey, OSSFrom, OSSTo, MQS, LogPath, tbl_length, Pdf_Path, Tmp_Path
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
        LogPath = jsobj["LogPath"]
        tbl_length = int(jsobj["tbl_length"])
        Tmp_Path = jsobj["Tmp_Path"]
        Pdf_Path = jsobj["Pdf_Path"]
    except Exception, ex:
        print "read config file failed! \n>>>>"
        print ex, "\n<<<<"
        sys.exit(-1)

    __check_create_path()
    Pdf_Path.setdefault("")


def __initialize_fenyin_log():
    global LogPath
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename=LogPath,
                        filemode='w')


def InitOnce():
    __readconfigfiles()
    __initialize_fenyin_log()

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
