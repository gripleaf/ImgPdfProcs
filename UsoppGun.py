#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'gripleaf'

from FenyinGlobals import Settings
from FenyinClients import MQSClient


if __name__ == "__main__":
    _mqsClient = MQSClient.FenyinMQSClient(Settings)
    _mqsClient.MQS_SendMsg("""
    {"handouts": "V11", "callback": "http://api.fenyin.me/v2/manage/file/previewPrepared?key=b3782cacecfe9f72997074003803d6ff-60a207c51ebe1f1b0c196918b2a81effb8a1e046-pdf-941539-1-tbl", "type": "convert_to_img", "id": "-287719", "key": "b3782cacecfe9f72997074003803d6ff-60a207c51ebe1f1b0c196918b2a81effb8a1e046-pdf-941539-1"}
    """)



