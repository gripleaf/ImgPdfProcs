#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from MQS_Python_SDK.account import Account
from MQS_Python_SDK.queue import *
import logging
import threading
import time
#sys.path.append("..")
from FenyinGlobals import Settings
#sys.path.remove("..")

class FenyinMQSClient:

    def MQS_ReceiveMsg(self):

        # get the mqs message
        try:
            # we need to lock the process
            self.__lock.acquire()

            self.recv_msg = self.my_queue.receive_message()

            self.__lock.release()

            print "Receive Message Succeed!"
            #print "message_id is %s" % self.recv_msg.message_id
            #print "message_body_md5 is %s" % self.recv_msg.message_body_md5
            print "message_body is %s" % self.recv_msg.message_body
            #print "dequeue_count is %s" % self.recv_msg.dequeue_count
            #print "enqueue_time is %s" % self.recv_msg.enqueue_time
            #print "first_dequeue_time is %s" % self.recv_msg.first_dequeue_time
            #print "priority %s" % self.recv_msg.priority
            #print "next_visible_time %s" % self.recv_msg.next_visible_time
            #print "receipt_handle is %s" % self.recv_msg.receipt_handle
            return self.recv_msg
        except MQSExceptionBase, e:
            print "Receive Message Fail:", e
            self.__lock.release()
            return None
        finally:
            pass

    def MQS_RenewMsg(self):

        # change message visibility
        try:
            # we need to lock the process
            self.__lock.acquire()

            change_msg_vis = self.my_queue.change_message_visibility(
                self.recv_msg.receipt_handle, 35)
            self.recv_msg.receipt_handle = change_msg_vis.receipt_handle

            self.__lock.release()
            print "Change Message Visibility Succeed!"
            print "receipt_handle is %s" % change_msg_vis.receipt_handle
            print "next_visible_time is %s" % change_msg_vis.next_visible_time
        except MQSExceptionBase, e:
            print "Change Message Visibility Fail:", e
            # sys.exit(1)

    def MQS_DeleteMsg(self):
            # delete message
        try:
            # we need to lock the process
            self.__lock.acquire()

            self.my_queue.delete_message(self.recv_msg.receipt_handle)

            self.__lock.release()
            print "Delete Message Succeed."
        except MQSExceptionBase, e:
            print "Delete Message Fail:", e
            # sys.exit(1)

    def __init__(self):
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
    #_mqs.MQS_ReceiveMsg()
    #_mqs.MQS_RenewMsg()
    #_mqs.MQS_DeleteMsg()
