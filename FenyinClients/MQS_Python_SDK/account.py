# -*- coding: utf-8 -*-

from mqs_client import MQSClient
from mqs_request import *
from queue import Queue

class Account:
    def __init__(self, host, access_id, access_key):
        self.access_id = access_id
        self.access_key = access_key
        self.queue_client = MQSClient(host, access_id, access_key)

    def set_queue_client(self, host):
        self.queue_client = MQSClient(host, self.access_id, self.access_key)

    def get_queue_client(self):
        return self.queue_client

    def get_queue(self, queue_name):
        return Queue(queue_name, self.queue_client)

    def list_queue(self, prefix = "", ret_number = -1, marker = ""):
        req = ListQueueRequest(prefix, ret_number, marker)
        resp = ListQueueResponse()
        self.queue_client.list_queue(req, resp)
        return resp.queueurl_list, resp.next_marker

