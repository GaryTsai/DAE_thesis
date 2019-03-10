# coding: utf-8
import sys, os, time, signal
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from datetime import datetime, timedelta
import json
from base64 import  encodestring

class MqttTalker():
    def __init__(self, host, uuid, topic, payload):
        self._host = host
        self._uuid = uuid
        self._topic = topic
        self._payload = payload


    def start(self):
        publish.single("{}/client_response/{}".format(self._uuid, self._topic),self._payload, qos=2, hostname=self._host)


def test():
    mqtt_host = "140.116.39.212"
    message = json.dumps({"value": "test connection"})
    mqtt_talker = MqttTalker(
    mqtt_host, "UID","test", message)
    mqtt_talker.start()

if __name__ == "__main__":
    test()
