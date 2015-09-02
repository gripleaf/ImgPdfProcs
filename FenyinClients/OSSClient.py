#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging

try:
    from OSS_Python_API.oss.oss_api import *
except:
    from OSS_Python_API.oss_api import *
try:
    from OSS_Python_API.oss.oss_xml_handler import *
except:
    from OSS_Python_API.oss_xml_handler import *
import sys
import datetime


class FenyinOSSClient:
    def __init__(self, Settings):
        ACCESS_ID = Settings.AccessId
        SECRET_ACCESS_KEY = Settings.AccessKey

        self.BUCKET_FROM = Settings.OSSFrom["QueueName"]
        self.HOST_FROM = Settings.OSSFrom["ServerName"]
        self.__oss_from = OssAPI(self.HOST_FROM, ACCESS_ID, SECRET_ACCESS_KEY)

        self.BUCKET_TO = Settings.OSSTo["QueueName"]
        self.HOST_TO = Settings.OSSTo["ServerName"]
        self.__oss_to = OssAPI(self.HOST_TO,
                               ACCESS_ID, SECRET_ACCESS_KEY)

        if Settings.OSSTo["ExpireTime"] is None or Settings.OSSTo["ExpireTime"] == "":
            self.Expire_Time = None
        else:
            # 2015 10 1 14 23 12
            try:
                self.Expire_Time = datetime.datetime(map(int, Settings.OSSTo["ExpireTime"].split(" ")))
            except Exception, e:
                self.Expire_Time = None

        logging.info("%s %s" % (self.HOST_TO, self.BUCKET_TO))


    def download_file_from_oss(self, object="object_test", filename="object"):
        '''
            @:param object key
            @:param filename download_file_path
            @:return None
        '''

        if os.path.exists(filename):
            return

        # todo pdf file is not have -pdf suffix
        if object.count("-pdf-") > 0 and object.endswith("-pdf"):
            object = object[0:-4]

        # 下载bucket中的object，把内容写入到本地文件中
        headers = {}

        for i in range(3):
            try:
                res = self.__oss_from.get_object_to_file(
                    self.BUCKET_FROM, object, filename, headers)
                if (res.status / 100) == 2:
                    logging.info("vvv get %s OK vvv" % filename)
                    return True
                else:
                    logging.warning("get %s ERROR" % filename)
                    continue
            except Exception, e:
                logging.error("download failed... retry %s ... error vvv %s vvv" % (i, e.message))
        return False


    def upload_file_to_oss(self, object="object_test", filename="123"):
        '''
            @:param object: object File Object
            @:param filename: filename key
            @:return: None
        '''
        # upload the file to a buketƒ√

        logging.info("uploading %s to %s" % (filename, object))
        for i in range(3):
            try:
                res = self.__oss_to.put_object_from_file(
                    self.BUCKET_TO, object, filename)

                if (res.status / 100) == 2:
                    logging.info("^^^ put %s OK ^^^" % filename)
                    return True
                else:
                    logging.warning("^^^ put %s ERROR ^^^" % filename)
                    continue
            except Exception, e:
                logging.error("upload failed... retry %s ... error^^^ %s ^^^" % (i, e.message))
        return False


    def __date_format(self, date="Tue, 03 Mar 2015 05:18:03 GMT"):
        '''convert a
            @:param date: Tue, 03 Mar 2015 05:18:03 GMT
            @:return: datetime
        '''
        _months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        if date is None:
            return None
        gpart = date.split(' ')
        if len(gpart) != 6:
            return None
        mon = 0
        for it in range(len(_months)):
            if _months[it] == gpart[2]:
                mon = it + 1
                break
        hour, mins, sec = map(int, gpart[-2].split(":"))
        try:
            return datetime.datetime(int(gpart[3]), mon, int(gpart[1]), hour, mins, sec)
        except Exception, ex:
            logging.error(ex.message)
            return None

    def check_file_on_oss(self, file_key):
        ''' check the file if on oss and not expire
            :param file_key: key of file in oss
            :return: True -> exist | False -> not exist or expire
        '''
        # check the file if in oss
        try:
            res = self.__oss_to.get_object_info(self.BUCKET_TO, file_key)
            last_modify = self.__date_format(res.getheader("Last-Modified"))
            if last_modify is not None and (self.Expire_Time is None or last_modify < self.Expire_Time):
                return True
            else:
                return False
        except Exception, e:
            logging.warning("checking error: %s" % e.message)
            return e.message


if __name__ == '__main__':
    # fy_oss = FenyinOSSClient()
    # res = fy_oss.download_file_from_oss("00131e5fd97a56d5db52670087699598-f2f3154bfdcbaf50870a8569154d00d04956670c-doc-76288", "test2.pdf")
    # fy_oss.upload_file_to_oss("test.pdf","test.pdf")
    # fy_oss.check_file_on_oss("")
    pass
