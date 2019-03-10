# coding: utf-8
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
import method.switch
import datetime
import method.mysql as daesql
import method.config.database_setting as dbconfig
import method.config.gateway_setting as gateway_setting
#使用pymysql前將資料庫名稱帳戶密碼資訊寫成global變數呼叫

this_gateway_uid = gateway_setting.uid
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
        if action == 'insert':
            if table == 'settings':
                print("######################insert/settings##########################")
                try:
                    sql1 = "SELECT * FROM setting WHERE address='%s' AND ch='%s'"%(msgFromServer["address"],msgFromServer["ch"])
                    repeat_address_ch_check = dbh.query(sql1)
                    sql2 = "SELECT * FROM setting WHERE circuit='%s'"%(msgFromServer["circuit"])
                    repeat_circuit_check = dbh.query(sql2)
                    if len(repeat_address_ch_check) != 0:
                        message = json.dumps({"status" : "repeat"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','setting','repeat','%s')"%(this_gateway_uid,current_time)
                    elif len(repeat_circuit_check) != 0:
                        message = json.dumps({"status" : "circuit_repeat"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','setting','circuit_repeat','%s')"%(this_gateway_uid,current_time)
                    else:
                        state = "INSERT INTO setting(model,address,ch,speed,circuit,pt,ct,meter_type,created_at,updated_at,gateway_uid)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(msgFromServer["model"],msgFromServer["address"],msgFromServer["ch"],msgFromServer["speed"],msgFromServer["circuit"],msgFromServer["pt"],msgFromServer["ct"],msgFromServer["type"],msgFromServer["created_at"],msgFromServer["updated_at"],this_gateway_uid) 
                        results = dbh.execute(state)
                        sql = "SELECT * from setting WHERE circuit = '%s'"%(msgFromServer["circuit"])
                        results = dbh.query(sql)
                        message = json.dumps({"status" : "ok", "id" : results[0]["id"]})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','setting',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+state,current_time)
                except Exception as n:
                    print("fail: ",n)
                    message = json.dumps({"status" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','setting','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "insert/settings"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'demand_settings':
                print("###################insert/demand_settings######################")
                try:
                    sql = "UPDATE demand_settings SET value='%s',value_max='%s',value_min='%s',load_off_gap='%s',reload_delay='%s',reload_gap='%s',cycle='%s',mode='%s',groups='%s',created_at='%s',updated_at='%s'"%(msgFromServer["value"],msgFromServer["value_max"],msgFromServer["value_min"],msgFromServer["load_off_gap"],msgFromServer["reload_delay"],msgFromServer["reload_gap"],msgFromServer["cycle"],msgFromServer["mode"],msgFromServer["group"],msgFromServer["created_at"],msgFromServer["created_at"])
                    result = dbh.execute(sql)
                    message = json.dumps({"status" : "ok"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','demand_settings',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+sql,current_time)
                except Exception as n:
                    print("fail:",n)
                    message = json.dumps({"status" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','demand_settings','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "insert/demand_settings"), message, qos=2, hostname=mqtt_host)

        elif action == 'update':
            if table == 'settings':
                print("###################update/settings######################")
                try:
                    sql1 = "SELECT * FROM setting WHERE address='%s' AND ch='%s' AND id!='%s'"%(msgFromServer["address"],msgFromServer["ch"],msgFromServer["id"])
                    repeat_address_ch_check = dbh.query(sql1)
                    sql2 = "SELECT * FROM setting WHERE circuit='%s' AND id!='%s'"%(msgFromServer["circuit"],msgFromServer["id"])
                    repeat_circuit_check = dbh.query(sql2)
                    if len(repeat_address_ch_check) != 0:
                        message = json.dumps({"status" : "repeat"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','setting','repeat','%s')"%(this_gateway_uid,current_time)
                    elif len(repeat_circuit_check) != 0:
                        message = json.dumps({"status" : "circuit_repeat"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','setting','circuit_repeat','%s')"%(this_gateway_uid,current_time)
                    else:
                        state = "UPDATE setting SET model='%s',address='%s',ch='%s',speed='%s',circuit='%s',pt='%s',ct='%s',meter_type='%s',updated_at='%s' WHERE id='%s'"%(msgFromServer["model"],msgFromServer["address"],msgFromServer["ch"],msgFromServer["speed"],msgFromServer["circuit"],msgFromServer["pt"],msgFromServer["ct"],msgFromServer["type"],msgFromServer["updated_at"],msgFromServer["id"]) 
                        result = dbh.execute(state)
                        message = json.dumps({"status" : "ok"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','setting',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+state,current_time)
                except Exception as n:
                    print("fail:",n)
                    message = json.dumps({"status" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','setting','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "update/settings"), message, qos=2, hostname=mqtt_host)

            elif table == 'offloads':
                print("###################update/offloads######################")
                try:
                    numgroup = int(msgFromServer["group"]) - 1
                    if msgFromServer["boolean"] == "true":
                        method.switch.switch_power(numgroup,1)
                    elif msgFromServer["boolean"] == "false":
                        method.switch.switch_power(numgroup,0)
                    sql = "UPDATE offloads SET hand_controls='%s',offload_available='%s',updated_at='%s' WHERE `group` = '%s'"%(msgFromServer["boolean"],msgFromServer["available"],current_time,msgFromServer["group"])
                    result = dbh.execute(sql)
                    message_for_client = json.dumps([{
                        "group" : msgFromServer["group"],
                        "available" : msgFromServer["available"],
                        "boolean" : msgFromServer["boolean"]
                    }])
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "offload/update"), message_for_client, qos=2, hostname=mqtt_host)
                    message = json.dumps({"status" : "ok"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','offloads',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+sql,current_time)
                except Exception as n:
                    print("fail:",n)
                    message =json.dumps({"status" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','offloads','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "update/offloads"), message, qos=2, hostname=mqtt_host)
            
        elif action == 'delete':
            if table == 'settings':
                print("###################delete/settings######################")
                try:
                    sql = "DELETE FROM setting WHERE id='%s'"%(msgFromServer["id"])
                    result = dbh.execute(sql)
                    message = json.dumps({"status" : "ok"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','delete','setting',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+sql,current_time)
                except Exception as n:
                    print("fail:",n)
                    message = json.dumps({"status" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','delete','setting','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "delete/settings"), message, qos=2, hostname=mqtt_host)
            
        elif action == 'query':
            if table == 'settings':
                print("###################query/settings######################")
                try:
                    sql = "SELECT * FROM setting"
                    results = dbh.query(sql)
                    data_output = []
                    for data in results:
                        data_output.append({
                            'id' : data["id"],
                            'model' : data["model"],
                            'address' : data["address"],
                            'ch' : data["ch"],
                            'speed' : data["speed"],
                            'circuit' : data["circuit"],
                            'pt' : data["pt"],
                            'ct' : data["ct"],
                            'meter_type' : data["meter_type"]
                        })
                    message = json.dumps(data_output)
                except Exception as n:
                    print("fail:",n)
                    message =json.dumps({"status" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "query/settings"), message, qos=2, hostname=mqtt_host)
            
            elif table == 'demand_settings':
                print("###################query/demand_settings######################")
                try:
                    sql = "SELECT * FROM demand_settings"
                    results = dbh.query(sql)
                    data_output = []
                    for data in results:
                        data_output.append({
                            "id" : data["id"],
                            'value' : data["value"],
                            'value_max' : data["value_max"],
                            'value_min' : data["value_min"],
                            'load_off_gap' : data["load_off_gap"],
                            'reload_delay' : data["reload_delay"],
                            'reload_gap' : data["reload_gap"],
                            'cycle' : data["cycle"],
                            'mode' : data["mode"],
                            'group' : data["groups"]
                        })
                    message = json.dumps(data_output)
                except BaseException as n:
                    print("fail:",n)
                    message =json.dumps({"status" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "query/demand_settings"), message, qos=2, hostname=mqtt_host)
            
            elif table == 'offloads':
                print("###################query/offloads######################")
                try:
                    data_output = []
                    sql = "SELECT * FROM offloads ORDER BY 'group' ASC"
                    results = dbh.query(sql)
                    for data in results:
                        data_output.append({
                            "group" : data["group"],
                            "available" : data["offload_available"],
                            "boolean" : data["hand_controls"]
                        })
                    message = json.dumps(data_output)
                except BaseException as n:
                    print("fail:",n)
                    message =json.dumps({"status" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "query/offloads"), message, qos=2, hostname=mqtt_host)
        dbh.close()
    
topic_list = ["insert/settings", "insert/demand_settings","update/settings","update/offloads","delete/settings","query/settings","query/demand_settings","query/offloads"]#訂閱主題清單

#uuid之後改為用query gatwayid的欄位或global變數

if __name__ == "__main__":
    mqtt_host = gateway_setting.mqtt_host#global變數
    for topic in topic_list:
        mqtt_subscribe = MqttSubscribe(mqtt_host, this_gateway_uid, topic)
    mqtt_service = threading.Thread(target=mqtt_subscribe.run)
    mqtt_service.start()
