__author__ = 'gripleaf'
from FenyinClients import MQSClient
from FenyinGlobals import Settings


if __name__ == "__main__":
    _mqsClient = MQSClient.FenyinMQSClient(Settings)
    while True:
        msg_recv = _mqsClient.MQS_ReceiveMsg()
        _mqsClient.MQS_DeleteMsg()