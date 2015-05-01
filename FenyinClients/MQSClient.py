#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from MQS_Python_SDK.account import Account
from MQS_Python_SDK.queue import *
import logging
import threading
import time
import base64

class FenyinMQSClient:
    def MQS_ReceiveMsg(self):

        # get the mqs message
        for i in range(10):
            try:
                # we need to lock the process
                self.__lock.acquire()

                self.__receive_mqs_message()

                self.__lock.release()

                #self.recv_msg.message_body = base64.b64encode(self.recv_msg.message_body)
                logging.info("Receive Message Succeed! message_body is %s" % self.recv_msg.message_body)
                # print "message_id is %s" % self.recv_msg.message_id
                # print "message_body_md5 is %s" %
                # self.recv_msg.message_body_md5
                # print "dequeue_count is %s" % self.recv_msg.dequeue_count
                # print "enqueue_time is %s" % self.recv_msg.enqueue_time
                # print "first_dequeue_time is %s" % self.recv_msg.first_dequeue_time
                # print "priority %s" % self.recv_msg.priority
                # print "next_visible_time %s" % self.recv_msg.next_visible_time
                # print "receipt_handle is %s" % self.recv_msg.receipt_handle
                return self.recv_msg
            except MQSExceptionBase, e:
                time.sleep(1)
            except Exception:
                pass
            finally:
                if self.__lock.locked():
                    self.__lock.release()

        self.recv_msg = None
        logging.warning("Receive Message Fail: %s" % e.message)
        return None

    def __receive_mqs_message(self):
        self.recv_msg = self.my_queue.receive_message()

    def MQS_RenewMsg(self):

        # change message visibility
        for i in range(3):
            try:
                if not hasattr(self, "recv_msg") or self.recv_msg is None:
                    # raise Exception(" recv_msg is None.")
                    return
                # we need to lock the process
                self.__lock.acquire()

                change_msg_vis = self.my_queue.change_message_visibility(
                    self.recv_msg.receipt_handle, 35)
                self.recv_msg.receipt_handle = change_msg_vis.receipt_handle

                self.__lock.release()
                logging.info(
                    "Change Message Visibility Succeed! receipt_handle is %s next_visible_time is %s" % (
                        change_msg_vis.receipt_handle,
                        change_msg_vis.next_visible_time))
                break
            except MQSExceptionBase, e:
                logging.warning("Change Message Visibility Fail: %s" % e.message)
            except AttributeError, ae:
                break
                # sys.exit(1)
            finally:
                if self.__lock.locked():
                    self.__lock.release()

    def MQS_DeleteMsg(self):
        # delete message
        for i in range(3):
            try:
                # we need to lock the process
                self.__lock.acquire()

                self.my_queue.delete_message(self.recv_msg.receipt_handle)
                self.recv_msg = None

                self.__lock.release()

                logging.info("Delete Message Succeed.")
                break
            except MQSExceptionBase, e:
                self.__lock.release()
                logging.warning("Delete Message Fail: %s" % e.message)
            finally:
                if self.__lock.locked():
                    self.__lock.release()

                # sys.exit(1)

    def __init__(self, Settings):
        logging.debug("initialize fenyin mqs client")
        accessId = Settings.AccessId
        accessKey = Settings.AccessKey
        queue_name = Settings.MQS["QueueName"]
        server_name = Settings.MQS["ServerName"]
        # print Settings.MQS["ServerName"]
        self.mqs_client = MQSClient(
            str(server_name), str(accessId), str(accessKey))

        self.my_queue = Queue(str(queue_name), self.mqs_client)
        # get lock  which is use to every operation about mqs
        self.__lock = threading.Lock()

        # reveive message
        # MQS_ReceiveMsg(my_queue)


if __name__ == "__main__":
    # print "unable to solve this problem"
    _mqs = FenyinMQSClient()
    # _mqs.MQS_ReceiveMsg()
    # _mqs.MQS_RenewMsg()
    # _mqs.MQS_DeleteMsg()
