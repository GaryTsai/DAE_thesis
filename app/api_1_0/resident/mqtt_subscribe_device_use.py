import sys
import os
import time
import signal
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
from datetime import datetime, timedelta
import json
import pymysql
import datetime
import method.mysql as daesql
import method.config.database_setting as dbconfig
import method.config.gateway_setting as gateway_setting
import method.group as switch

#import pymysql
#使用pymysql前將資料庫名稱帳戶密碼資訊寫成global變數呼叫

this_gateway_uid = gateway_setting.uid
model_percent = ['LT4500']
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def update_node(update_id):
    try:
        dbh = daesql.MySQL(dbconfig.mysql_config)
        node_data = []
        for data in update_id:
            sql = "SELECT * FROM node WHERE id='%s'"%(data)
            results = dbh.query(sql)
            for data in results:
                node_data.append({
                    'id': data["id"],
                    'gateway_address': data["gateway_address"],
                    'model': data["model"],
                    'node_name': data["node_name"],
                    'node': data["node"],
                    'group_id': data["group_id"],
                    'model_type': data["model_type"],
                    'node_state': data["node_state"]
                })
        message = json.dumps(node_data)
        dbh.close
    except BaseException as n:
        print (n)
    time.sleep(0.5)
    publish.single("{}/client_response/{}".format(this_gateway_uid, "node/update"), message, qos=2, hostname=mqtt_host)
    print("update_node_ok")

class MqttSubscribe:

    def __init__(self, host, uuid, topic):
        self._host = host
        self._uuid = uuid
        self._topic = topic
        self._response = ""
        self.mqtt_client = mqtt.Client()
        self.__init_mqtt()

    def __init_mqtt(self):
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        try:
            self.mqtt_client.connect_async(self._host, 1883, 30)
            self.mqtt_client.loop_start()
        except:
            print('MQTT Broker is not online. Connect later.')

    def on_mqtt_connect(self, mq, userdata, flags, rc):
        self.mqtt_client.subscribe("{}/{}".format(self._uuid, self._topic), qos=2)

    def run(self):
        while True:
            pass

    def on_mqtt_message(self, mq, userdata, msg):
        try:
            uuid, action, table = msg.topic.split("/")

        except:
            return

        #對gateway裝置做的action寫之後，用publish.single去發佈response topic和內容，之後才update資料庫狀態
        #json.loads(msg.payload)['value'] 解開payload message
        #json.dumps({"status":msg.payload["reload_gap"], "id":"2"}) 打包傳送message格式
        dbh = daesql.MySQL(dbconfig.mysql_config)
        msgFromServer=json.loads(msg.payload.decode('utf-8'))
        if action == 'node':
            if table == 'setting':
                print("######################node/setting##########################")
                try:
                    if msgFromServer["methods"]=="POST":
                        sql="SELECT * FROM node WHERE id='%s' ORDER BY node"%(msgFromServer["node_id"])
                    else:
                        sql="SELECT * FROM node ORDER BY node"
                    node_data = []
                    results = dbh.query(sql)
                    for data in results:
                        node_data.append({
                            'id': data["id"],
                            'gateway': data["gateway"],
                            'gateway_address': data["gateway_address"],
                            'model': data["model"],
                            'node_name': data["node_name"],
                            'node': data["node"],
                            'group_id': data["group_id"],
                            'model_type': data["model_type"],
                            'node_state': data["node_state"]
                        })
                    message = json.dumps(node_data)
                except BaseException as n:
                    print("fail:",n)
                    message =json.dumps({"state" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "node/setting"), message, qos=2, hostname=mqtt_host)

        elif action == 'group':
            if table == 'setting':
                print("######################group/setting##########################")
                try:
                    group_data = []
                    sql = "SELECT * FROM `group`"
                    results = dbh.query(sql)
                    for data in results:
                        group_data.append({
                            'id': data["id"],
                            'group_num': data["group_num"],
                            'group_name': data["group_name"],
                            'group_state': data["group_state"]
                        })
                    message = json.dumps(group_data)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state":"failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "group/setting"), message, qos=2, hostname=mqtt_host)

        elif action == 'scene':
            if table == 'setting':
                print("###################/scene/setting######################")
                try:
                    scenes_data = []
                    sql = "SELECT scene_number,scene_name FROM scenes GROUP BY scene_number,scene_name ORDER BY scene_number"
                    results = dbh.query(sql)
                    for data in results:
                        scenes_data.append({
                            'scene_name': data["scene_name"],
                            'scene_number': data["scene_number"]
                        })
                    message = json.dumps(scenes_data)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state":"failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "scene/setting"), message, qos=2, hostname=mqtt_host)

        elif action == 'device':
            if table == 'realtime_group_state':
                print("###################device/realtime_group_state######################")
                try:
                    for_log = ""
                    if(msgFromServer["group_state"] == "ON"):
                        state_change = "OFF"
                        node_state_number = "0"
                    else:
                        state_change = "ON"
                        node_state_number = "100"
                    sql = "SELECT * from `group` WHERE id='%s'"%(msgFromServer["group_id"])
                    results = dbh.query(sql)
                    for data in results:
                        switch.switch_group(int(data["group_num"]),state_change)
                        message_for_client = json.dumps([{
                            'id' : data["id"],
                            'group_num' : data["group_num"],
                            'group_name' : data["group_name"],
                            'group_state' : state_change
                        }])
                    sql = "UPDATE `group` SET group_state='%s',updated_at='%s' WHERE id='%s'"%(state_change,current_time,msgFromServer["group_id"])
                    result = dbh.execute(sql)
                    for_log = for_log + '\n' + sql
                    sql = "SELECT id , model_type FROM node WHERE group_id='%s'"%(msgFromServer["group_id"])
                    results = dbh.query(sql)
                    update_node_id = []
                    for data in results:
                        node_num = data["id"]
                        sql = "UPDATE node SET node_state='%s' WHERE id='%s'"%(state_change if data["model_type"] == 1 else node_state_number,node_num)
                        result = dbh.execute(sql)
                        for_log = for_log + '\n' + sql
                        update_node_id.append(data["id"])
                    update_node(update_node_id)
                    message = json.dumps({
                        "state" : "ok",
                        "state_change" : state_change
                    })
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "group/update"), message_for_client, qos=2, hostname=mqtt_host)
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','realtime change group state',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content,  execute_state, `datetime`)VALUES('Server','%s','update','realtime change group state','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "device/realtime_group_state"), message, qos=2, hostname=mqtt_host)
            elif table == 'realtime_node_state':
                print("###################device/realtime_node_state######################")
                try:
                    sql = "SELECT * FROM node WHERE id='%s'"%(msgFromServer["node_id"])
                    results = dbh.query(sql)
                    update_node_id = []
                    update_node_id.append(results[0]["id"])
                    if(msgFromServer["node_state"] == "ON"):
                        state_change = "OFF"
                    elif(msgFromServer["node_state"] == "OFF"):
                        state_change = "ON"
                    elif(msgFromServer["node_state"] >= str(0)):
                        state_change = msgFromServer["node_state_value"]
                    switch.switch_power(int(results[0]["gateway_address"]),int(results[0]["node"]),state_change)
                    message = json.dumps({
                        "state" : "ok",
                        "state_change" : state_change
                    })
                    sql = "UPDATE node SET node_state='%s' WHERE id='%s'"%(state_change,msgFromServer["node_id"])
                    result = dbh.execute(sql)
                    update_node(update_node_id)
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','realtime change node state',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+sql,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state":"failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','realtime change node state','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "device/realtime_node_state"), message, qos=2, hostname=mqtt_host)

            elif table == 'realtime_scene_state':
                print("###################device/realtime_scene_state######################")
                try:
                    node_change = []
                    update_node_id = []
                    for_log = ""
                    switch.switch_scene(int(msgFromServer["scene_number"]), "ON")
                    sql = "SELECT * FROM scenes WHERE scene_number='%s'"%(msgFromServer["scene_number"])
                    results = dbh.query(sql)
                    for data in results:
                        node_change.append({
                            'node_id': data["node"],
                            'node_state': data["node_state"]
                        })
                        update_node_id.append(data["node"])
                    for data in node_change:
                        sql = "UPDATE node SET node_state='%s' WHERE id='%s'"%(data['node_state'],data['node_id'])
                        result = dbh.execute(sql)
                        for_log = for_log + '\n' + sql
                    update_node(update_node_id)
                    message = json.dumps({"state":"ok"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','realtime change scene state',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state":"failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content,  execute_state, `datetime`)VALUES('Server','%s','update','realtime change scene state','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except :
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "device/realtime_scene_state"), message, qos=2, hostname=mqtt_host)
        dbh.close()

topic_list = ["node/setting", "group/setting", "scene/setting", "device/realtime_group_state", "device/realtime_node_state", "device/realtime_scene_state"]#訂閱主題清單

#uuid之後改為用query gatwayid的欄位或global變數

if __name__ == "__main__":
    mqtt_host = gateway_setting.mqtt_host#global變數
    for topic in topic_list:
        mqtt_subscribe = MqttSubscribe(mqtt_host, this_gateway_uid, topic)
    mqtt_service = threading.Thread(target=mqtt_subscribe.run)
    mqtt_service.start()