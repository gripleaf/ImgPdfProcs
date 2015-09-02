__author__ = 'gripleaf'
from FenyinClients import MQSClient
from FenyinGlobals import Settings
from FenyinClients import FenyinDBClient
import json


if __name__ == "__main__":
    _mqsClient = MQSClient.FenyinMQSClient(Settings)
    _sqlClient = FenyinDBClient.FenyinDBClient(Settings)
    while True:
        msg_recv = _mqsClient.MQS_ReceiveMsg()
        jobj = json.loads(msg_recv.message_body)
        _sqlClient.set_mqs_message(jobj)
        _mqsClient.MQS_DeleteMsg()
