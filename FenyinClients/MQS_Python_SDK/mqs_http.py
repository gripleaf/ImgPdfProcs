# -*- coding: utf-8 -*-

from httplib import HTTPConnection, BadStatusLine
from mqs_exception import *

class MyHTTPConnection(HTTPConnection):
    def __init__(self, host, port=None, strict=None):
        HTTPConnection.__init__(self, host, port, strict)
        self.request_length = 0

    def send(self, str):
        HTTPConnection.send(self, str)
        self.request_length += len(str)

    def request(self, method, url, body=None, headers={}):
        self.request_length = 0
        HTTPConnection.request(self, method, url, body, headers)

class MQSHttp:
    def __init__(self, host, connection_timeout = 60, keep_alive = True):
        self.conn = MyHTTPConnection(host)
        self.connection_timeout = connection_timeout
        self.keep_alive = keep_alive
        self.request_size = 0
        self.response_size = 0

    def set_connection_timeout(self, connection_timeout):
        self.connection_timeout = connection_timeout

    def set_keep_alive(self, keep_alive):
        self.keep_alive = keep_alive

    def is_keep_alive(self):
        return self.keep_alive
 
    def send_request(self, req_inter):
        try:
            self.conn.request(req_inter.method, req_inter.uri, req_inter.data, req_inter.header)
            self.conn.sock.settimeout(self.connection_timeout)
            try:
                http_resp = self.conn.getresponse()
            except BadStatusLine:
                #open another connection when keep-alive timeout
                #httplib will not handle keep-alive timeout, so we must handle it ourself
                self.conn.close()
                self.conn.request(req_inter.method, req_inter.uri, req_inter.data, req_inter.header)
                self.conn.sock.settimeout(self.connection_timeout)
                http_resp = self.conn.getresponse()
            headers = dict(http_resp.getheaders())
            resp_inter = ResponseInternal(status = http_resp.status, header = headers, data = http_resp.read())
            self.request_size = self.conn.request_length
            self.response_size = len(resp_inter.data)
            if not self.is_keep_alive():
                self.conn.close()
            return resp_inter
        except Exception,e:
            self.conn.close()
            raise MQSClientNetworkException("NetWorkException", str(e)) #raise netException

class RequestInternal:
    def __init__(self, method = "", uri = "", header = None, data = ""):
        if header == None:
            header = {}
        self.method = method
        self.uri = uri
        self.header = header
        self.data = data 

    def __str__(self):
        return "method: %s\nuri: %s\nheader: %s\ndata: %s\n" % (self.method, self.uri, self.header, self.data)

class ResponseInternal:
    def __init__(self, status = 0, header = None, data = ""):
        if header == None:
            header = {}
        self.status = status
        self.header = header
        self.data = data

    def __str__(self):
        return "status: %s\nheader: %s\ndata: %s" % (self.status, self.header, self.data)
