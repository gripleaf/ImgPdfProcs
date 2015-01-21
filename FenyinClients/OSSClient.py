#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

try:
    from OSS_Python_API.oss.oss_api import *
except:
    from OSS_Python_API.oss_api import *
try:
    from OSS_Python_API.oss.oss_xml_handler import *
except:
    from OSS_Python_API.oss_xml_handler import *
import sys
# sys.path.append("..")
from FenyinGlobals import Settings
# sys.path.remove("..")


class FenyinOSSClient:
    def __init__(self):
        ACCESS_ID = Settings.AccessId
        SECRET_ACCESS_KEY = Settings.AccessKey

        self.BUCKET_FROM = Settings.OSSFrom["QueueName"]
        self.HOST_FROM = Settings.OSSFrom["ServerName"]
        self.__oss_from = OssAPI(self.HOST_FROM, ACCESS_ID, SECRET_ACCESS_KEY)

        self.BUCKET_TO = Settings.OSSTo["QueueName"]
        self.HOST_TO = Settings.OSSTo["ServerName"]
        self.__oss_to = OssAPI(self.HOST_TO,
                               ACCESS_ID, SECRET_ACCESS_KEY)

        print self.HOST_TO, self.BUCKET_TO

    def download_file_from_oss(self, object="object_test", filename="object"):
        if os.path.exists(filename):
            return

        # todo pdf file is not have -pdf suffix
        if object.count("-pdf-") > 0 and object.endswith("-pdf"):
            object = object[0:-4]

        # 下载bucket中的object，把内容写入到本地文件中
        headers = {}

        res = self.__oss_from.get_object_to_file(
            self.BUCKET_FROM, object, filename, headers)
        if (res.status / 100) == 2:
            print "get_object_to_file OK"
        else:
            print "get_object_to_file ERROR"

    def upload_file_to_oss(self, object="object_test", filename="123"):
        # upload the file to a buketƒ√

        content_type = "text/HTML"
        headers = {}
        print "uploading", filename, "to", object
        res = self.__oss_to.put_object_from_file(
            self.BUCKET_TO, object, filename)

        if (res.status / 100) == 2:
            print "put_object_from_file OK"
        else:
            print "put_object_from_file ERROR"


if __name__ == '__main__':
    fy_oss = FenyinOSSClient()
    # res = fy_oss.download_file_from_oss("00131e5fd97a56d5db52670087699598-f2f3154bfdcbaf50870a8569154d00d04956670c-doc-76288", "test2.pdf")
    # fy_oss.upload_file_to_oss("test.pdf","test.pdf")
