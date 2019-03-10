# coding: utf-8
from flask import jsonify
import sys
import os
import time
import signal
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from datetime import datetime, timedelta
import json
from base64 import encodestring


class MqttTalker():
    def __init__(self, host, uuid, topic, payload):
        self._host = host
        self._uuid = uuid
        self._topic = topic
        self._payload = payload
        self._response = ""
        self.mqtt_looping = True

    def on_connect(self, mq, userdata, rc, _):
        mq.subscribe("{}/response/{}".format(self._uuid, self._topic))
        publish.single(
            "{}/{}".format(self._uuid, self._topic),
            self._payload, qos=1, hostname=self._host)

    def on_message(self, mq, userdata, msg):
        print("Receiving messages from {} (qos={})...".format(
            msg.topic, msg.qos))
        print("Content:\n{}".format(msg.payload))
        self.mqtt_looping = False
        self._response = msg.payload

    def start(self):
        mqtt_looping = True
        client = mqtt.Client()

        client.on_connect = self.on_connect
        client.on_message = self.on_message

        try:
            client.connect(self._host)
        except:
            print("MQTT Broker is not online. Connect later.")
            return ""

        print("Sending message:\n{}".format(self._payload))
        wait_until = datetime.now() + timedelta(seconds=30)
        while self.mqtt_looping:
            client.loop()
            if wait_until < datetime.now():
                break

        if not self._response:
            print("timeout")
            return None
        client.disconnect()

        return self._response.decode("utf-8")


def test():
    mqtt_host = "140.116.39.212"
    message = json.dumps({})
    mqtt_talker = MqttTalker(mqtt_host, "09ea6335-d2bd-4678-9ca9-647b5574a09e","query/demand_settings", message)
    response = mqtt_talker.start()
    if response:
        return response, 201
    else:
        return "Failure", 201


if __name__ == "__main__":
    print("Result:\n", test())
