#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'gripleaf'

from FenyinGlobals import Settings
from FenyinClients import MQSClient


def old_test():
    _mqsClient = MQSClient.FenyinMQSClient(Settings)
    _mqsClient.MQS_SendMsg("""
    {"handouts": "V11", "callback": "http://api.fenyin.me/v2/manage/file/previewPrepared?key=b3782cacecfe9f72997074003803d6ff-60a207c51ebe1f1b0c196918b2a81effb8a1e046-pdf-941539-1-tbl", "type": "convert_to_img", "id": "-287719", "key": "b3782cacecfe9f72997074003803d6ff-60a207c51ebe1f1b0c196918b2a81effb8a1e046-pdf-941539-1"}
    """)


def sendMsg2ppt(msg):
    _mqsPptClient.MQS_SendMsg(msg)


def sendMsg2def(msg):
    _mqsDefClient.MQS_SendMsg(msg)


def createMsg(file_id, file_key, handouts):
    return """
    {"handouts": "%s", "callback": "", "type": "convert_to_pdf", "id": "%s", "key": "%s"}
    """ % (handouts, file_id, file_key)


def readErrorList(file_path):
    lines = open(file_path).readlines()
    res = []
    for line in lines:
        line = line[0:-2]
        res.append(line.split('\t'))
    return res


if __name__ == "__main__":
    global _mqsPptClient, _mqsDefClient
    _mqsPptClient = MQSClient.FenyinMQSClient(Settings.AccessId, Settings.AccessKey, "fpt-ppt",
                                              Settings.MQS["ServerName"])
    _mqsDefClient = MQSClient.FenyinMQSClient(Settings.AccessId, Settings.AccessKey, "fpt",
                                              Settings.MQS["ServerName"])

    cfgs = readErrorList("error.list")
    for cfg in cfgs:
        msg = createMsg(cfg[1],cfg[0],cfg[2])
        print msg
        print "sending...."
        if cfg[0].find('-ppt') >= 0:
            sendMsg2ppt(msg)
        else:
            sendMsg2def(msg)

        print ''
        #raw_input("press to continue.")




