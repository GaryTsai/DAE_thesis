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
import method.cflag as cflag

#import pymysql
#使用pymysql前將資料庫名稱帳戶密碼資訊寫成global變數呼叫

this_gateway_uid = gateway_setting.uid
model_percent = ['LT4500']

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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if action == 'node_setting':
            if table == 'insert':
                print("###################node_setting/insert######################")
                try:
                    sql1 = "SELECT * FROM node "
                    overcount_check = dbh.query(sql1)
                    sql2 = "SELECT * FROM node WHERE (gateway_address = '%s' AND node = '%s') OR node_name='%s'"%(msgFromServer["gateway_address"],msgFromServer["node"],msgFromServer["node_name"]) 
                    repeat_address_node_check = dbh.query(sql2)
                    if len(overcount_check) >= 256:
                        message = json.dumps([{"status":"overcount"}, {"state":"failed"}])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','node','overcount','%s')"%(this_gateway_uid,current_time)
                    elif len(repeat_address_node_check) != 0:
                        message = json.dumps([{"status":"repeat error"}, {"state":"failed"}])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','node','repeat error','%s')"%(this_gateway_uid,current_time)
                    else:
                        insert_sql = "INSERT INTO node(gateway,gateway_address,model,node_name,node,created_at,updated_at,model_type,node_state)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(msgFromServer["node_gateway"],msgFromServer["gateway_address"],msgFromServer["node_model"],msgFromServer["node_name"],msgFromServer["node"],msgFromServer["created_at"],msgFromServer["updated_at"] ,'0' if msgFromServer["node_model"] in model_percent else '1' ,'0' if msgFromServer["node_model"] in model_percent else 'OFF')
                        result = dbh.execute(insert_sql)
                        node_data = []
                        sql = "SELECT * FROM node WHERE gateway_address = '%s' AND node= '%s'"%(msgFromServer["gateway_address"],msgFromServer["node"])
                        results = dbh.query(sql)
                        for data in results:
                            node_data.append({
                                'id' : data["id"],
                                'gateway' : data["gateway"],
                                'gateway_address' : data["gateway_address"],
                                'model' : data["model"],
                                'node_name' : data["node_name"],
                                'node' : data["node"],
                                'model_type' : data["model_type"],
                                'node_state' : data["node_state"]
                            })
                        message_for_client = json.dumps(node_data)
                        time.sleep(0.5)
                        publish.single("{}/client_response/{}".format(this_gateway_uid, "node/insert"), message_for_client, qos=2, hostname=mqtt_host)
                        message = json.dumps([{"status":"ok"}, node_data])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','node',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+insert_sql,current_time)   
                except  BaseException as n:
                    print("fail:",n)
                    message = json.dumps([{"status" : "failed"}, {"state" : "failed"}])
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','node','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "node_setting/insert"), message, qos=2, hostname=mqtt_host)

            elif table == 'update':
                print("###################node_setting/update######################")
                try:
                    sql = "SELECT * FROM node WHERE ((gateway_address = '%s' AND node = '%s') OR node_name='%s') AND id !='%s'"%(msgFromServer["node_update_gateway_address"],msgFromServer["node_update_node"],msgFromServer["node_update_node_name"],msgFromServer["node_id"]) 
                    repeat_check = dbh.query(sql)
                    if len(repeat_check) != 0:
                        message = json.dumps({"state" : "repeat error"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','node','repeat error','%s')"%(this_gateway_uid,current_time)
                    else:
                        sql = "UPDATE node SET gateway= '%s',gateway_address= '%s',model= '%s',node_name= '%s',node= '%s',updated_at= '%s',model_type = '%s',node_state= '%s' WHERE id='%s'"%(msgFromServer["node_update_gateway"],msgFromServer["node_update_gateway_address"],msgFromServer["node_update_model"],msgFromServer["node_update_node_name"],msgFromServer["node_update_node"],current_time,'0' if msgFromServer["node_update_model"] in model_percent else '1','0' if msgFromServer["node_update_model"] in model_percent else 'OFF',msgFromServer["node_id"]) #以目前前端而言 model_type = '%s',node_state= '%s' 可以不用寫
                        result = dbh.execute(sql)
                        message = json.dumps({"state" : "ok"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','node',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+sql,current_time)
                        update_node([msgFromServer["node_id"]])
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','node','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "node_setting/update"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'delete':
                print("###################node_setting/delete######################")
                try:
                    delete_scene_sql = "DELETE FROM scenes WHERE node='%s'"%(msgFromServer["node"])
                    result = dbh.execute(delete_scene_sql)
                    delete_node_sql = "DELETE FROM node WHERE id='%s'"%(msgFromServer["node_id"])
                    result = dbh.execute(delete_node_sql)
                    message = json.dumps({"state":"ok"})
                    message_for_client = json.dumps([{'id':msgFromServer["node_id"]}])
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "node/delete"), message_for_client, qos=2, hostname=mqtt_host)
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','delete','node',\"%s\",'ok','%s')"%(this_gateway_uid,'\n'+delete_scene_sql+'\n'+delete_node_sql,current_time)
                except  BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state":"failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','delete','node','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "node_setting/delete"), message, qos=2, hostname=mqtt_host)
        
        elif action == 'group_setting':
            if table == 'insert':
                print("###################group_setting/insert######################")
                try:
                    sql1 = "SELECT * FROM `group`"
                    overcount_check = dbh.query(sql1)
                    sql2 = "SELECT * FROM `group` WHERE group_num = '%s' OR group_name = '%s' "%(msgFromServer["group_num"],msgFromServer["group_name"]) 
                    data_repeat_check = dbh.query(sql2)
                    if len(overcount_check) >= 32:
                        message = json.dumps([{"state" : "failed"}, {"status" : "overcount"}])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','group','repeat error','%s')"%(this_gateway_uid,current_time)
                    elif len(data_repeat_check) != 0:
                        message = json.dumps([{"state":"failed"},{"status":"repeat error"}])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','group','repeat error','%s')"%(this_gateway_uid,current_time)
                    else:
                        for_log = ""
                        sql = "INSERT INTO `group`(group_num,group_name,group_state,created_at,updated_at)VALUES('%s','%s','OFF','%s','%s')"%(msgFromServer["group_num"],msgFromServer["group_name"],current_time,current_time)
                        result = dbh.execute(sql)
                        for_log = for_log + "\n" + sql
                        sql = "SELECT * FROM `group` WHERE group_num = '%s' AND group_name = '%s'"%(msgFromServer["group_num"],msgFromServer["group_name"])
                        results = dbh.query(sql)
                        group_data = []
                        for data in results:
                            group_data.append({
                                'id' : data["id"],
                                'group_num' : data["group_num"],
                                'group_name' : data["group_name"],
                                'group_state' : data["group_state"]
                            })
                        sql = "SELECT control_time,control_time_of_sun,schedule_table FROM schedule GROUP BY control_time,schedule_table,control_time_of_sun "
                        Schedule_data = dbh.query(sql)
                        for d in Schedule_data:
                            sql = "INSERT INTO schedule(schedule_table,group_id,schedule_group_state," + ("control_time_of_sun" if d["control_time"] is None else "control_time") + ",setting)VALUES('%s','%s','OFF','%s','false')"%(d["schedule_table"], group_data[0]["id"], d["control_time_of_sun"] if d["control_time"] is None else d["control_time"])
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                        for i in range(0, msgFromServer["length"], 1):
                            sql="UPDATE node SET group_id= '%s' WHERE id='%s'"%(group_data[0]["id"],msgFromServer["node"][i])
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                        message = json.dumps([group_data, {"state" : "ok"}])
                        switch.set_group(group_data[0]["id"])
                        cflag.cflag()
                        message_for_client = json.dumps(group_data)
                        time.sleep(0.5)
                        publish.single("{}/client_response/{}".format(this_gateway_uid, "group/insert"), message_for_client, qos=2, hostname=mqtt_host)
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','group',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','group','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "group_setting/insert"), message, qos=2, hostname=mqtt_host)

            elif table == 'delete':
                print("###################group_setting/delete######################")
                try:
                    switch.delete_group(msgFromServer["group_id"])
                    sql1 = "UPDATE node SET group_id=NULL WHERE group_id='%s'"%(msgFromServer["group_id"])
                    result = dbh.execute(sql1)
                    sql2 = "DELETE FROM `group` WHERE id='%s'"%(msgFromServer["group_id"])
                    result = dbh.execute(sql2)
                    sql3 = "DELETE FROM schedule WHERE group_id='%s'"%(msgFromServer["group_id"])
                    result = dbh.execute(sql3)
                    message = json.dumps({"state" : "ok"})
                    message_for_client = json.dumps([{'id' : msgFromServer["group_id"]}])
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "group/delete"), message_for_client, qos=2, hostname=mqtt_host)
                    cflag.cflag()
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','delete','group',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+sql1+"\n"+sql2+"\n"+sql3,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','delete','group','failed','%s')"%(this_gateway_uid,current_time) 
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "group_setting/delete"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'update':
                print("###################group_setting/update######################")
                try:
                    sql = "SELECT * FROM `group` WHERE (group_num='%s' OR group_name='%s') AND id != '%s'"%(msgFromServer["group_num"],msgFromServer["group_name"],msgFromServer["group_id"])
                    name_number_repeat_check = dbh.query(sql)
                    if len(name_number_repeat_check) != 0:
                        message = json.dumps([{"status":"repeat error"},{"state":"name_number_repeat"}])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','group','repeat error','%s')"%(this_gateway_uid,current_time)
                    else:
                        for_log = ""
                        switch.delete_group(msgFromServer["group_id"])
                        sql = "UPDATE `group` SET group_num='%s',group_name='%s' WHERE id='%s'"%(msgFromServer["group_num"],msgFromServer["group_name"],msgFromServer["group_id"])
                        result = dbh.execute(sql)
                        for_log = for_log + "\n" + sql
                        sql = "UPDATE node SET group_id=NULL,updated_at='%s' WHERE group_id='%s'"%(current_time,msgFromServer["group_id"])
                        result = dbh.execute(sql)
                        for_log = for_log + "\n" + sql
                        for i in range(0, msgFromServer["length"], 1):
                            sql = "UPDATE node SET group_id='%s',updated_at='%s' WHERE id='%s'"%(msgFromServer["group_id"],current_time,msgFromServer["node"][i])
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                        group_data = []
                        sql = "SELECT * FROM `group` WHERE id='%s' AND group_name='%s'"%(msgFromServer["group_id"],msgFromServer["group_name"])
                        Group_data = dbh.query(sql)
                        for data in Group_data:
                            group_data.append({
                                'id' : data["id"],
                                'group_num' : data["group_num"],
                                'group_name' : data["group_name"],
                                'group_state' : data["group_state"]
                            })
                        message = json.dumps([group_data, {"state" : "ok"}])
                        switch.set_group(msgFromServer["group_id"])
                        message_for_client = json.dumps(group_data)
                        time.sleep(0.5)
                        publish.single("{}/client_response/{}".format(this_gateway_uid, "group/update"), message_for_client, qos=2, hostname=mqtt_host)
                        cflag.cflag()
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','group',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state":"failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','group',,'failed','%s')"%(this_gateway_uid,current_time) 
                print(message)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "group_setting/update"), message, qos=2, hostname=mqtt_host)


        elif action == 'scene_setting':
            if table == 'delete':
                print("###################scene_setting/delete######################")
                try:
                    switch.delete_scene(int(msgFromServer["scene_number"]))
                    sql = "DELETE FROM scenes WHERE scene_number='%s'"%(msgFromServer["scene_number"])
                    results = dbh.execute(sql)
                    message = json.dumps({"state":"ok"})
                    message_for_client = json.dumps([{'scene_number' : msgFromServer["scene_number"]}])
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "scene/delete"), message_for_client, qos=2, hostname=mqtt_host)
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','delete','scene',\"%s\",'ok','%s')"%(this_gateway_uid,sql,current_time)
                except  BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','delete','scene','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "scene_setting/delete"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'update_information':
                print("###################scene_setting/update_information######################")
                try:
                    sql = "SELECT scene_number,scene_name,scenes.node,scenes.node_state,node.id ,node.node_name, node.model, node.model_type FROM scenes JOIN node ON scenes.node = node.id AND node.id= scenes.node  "
                    Scenes_data = dbh.query(sql)
                    sql = "SELECT * FROM node"
                    Node_node = dbh.query(sql)
                    sql = "SELECT DISTINCT model FROM node"
                    Node_model = dbh.query(sql)
                    sql = "SELECT DISTINCT scene_number FROM scenes"
                    scene_record = dbh.query(sql)
                    scene_record_number = []
                    for data in scene_record:
                        scene_record_number.append(data["scene_number"])
                    node_data = []
                    scenes_data = []
                    model_type = []
                    for model_data in Node_model:
                        model_type.append(model_data["model"])
                    for data in Scenes_data:
                        scenes_data.append({
                            'scene_number': data["scene_number"],
                            'scene_name': data["scene_name"],
                            'node': data["node"],
                            'node_state': data["node_state"],
                            'node_name': data["node_name"],
                            'node_model': data["model"],
                            'model_type': data["model_type"]
                        })
                    for data in Node_node:
                        node_data.append({
                            'id': data["id"],
                            'node_name': data["node_name"],
                            'node_model': data["model"],
                            'model_type': data["model_type"]
                        })
                    scene_information = {}
                    node_record = {}
                    node_not_record = {}
                    for scene_number in scene_record_number:
                        scene_information[str(scene_number)] = []
                    for scene_number in scene_record_number:
                        node_record[str(scene_number)] = []
                        node_not_record[str(scene_number)] = []
                    for scene_number in scene_record_number:
                        for data in scenes_data:
                            if(data['scene_number'] == scene_number):
                                node_record[str(scene_number)].append(data['node'])
                        for data in node_data:
                            if(data['id'] not in node_record[str(scene_number)]):
                                node_not_record[str(scene_number)].append(data['id'])
                    for scene_number in scene_record_number:
                        for data in scenes_data:
                            if(data['scene_number'] == scene_number):
                                scene_information[str(scene_number)].append({
                                    'scene_number': data['scene_number'],
                                    'scene_name': data['scene_name'],
                                    'node': data['node'],
                                    'node_state': data['node_state'],
                                    'node_name': data['node_name'],
                                    'node_model': data['node_model'],
                                    'model_type': data['model_type']
                                })
                        for data in node_not_record[str(scene_number)]:
                            for node_datas in node_data:
                                if data == node_datas['id']:
                                    scene_information[str(scene_number)].append({
                                        'scene_number' : scene_number,
                                        'scene_name' : "",
                                        'node' : node_datas['id'],
                                        'node_name' : node_datas['node_name'],
                                        'node_model' : node_datas['node_model'],
                                        'model_type' : node_datas['model_type']
                                    })
                    message = json.dumps([scenes_data, node_data, scene_information, model_type])
                except  BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "scene_setting/update_information"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'update':
                print("###################scene_setting/update######################")
                try:
                    sql1 = "SELECT * FROM scenes WHERE scene_name='%s'"%(msgFromServer["scene_name"])
                    data_repaet1 = dbh.query(sql1)
                    sql2 = "SELECT * FROM scenes WHERE  scene_number = '%s'"%(msgFromServer["scene_number"])
                    data_repaet2 = dbh.query(sql2)
                    sql3 = "SELECT * FROM scenes WHERE scene_name='%s' OR scene_number = '%s'"%(msgFromServer["scene_name"],msgFromServer["scene_number"])
                    data_repaet3 = dbh.query(sql3)
                    if((msgFromServer["origin_scene_number"] == msgFromServer["scene_number"]) and (msgFromServer["origin_scene_name"] != msgFromServer["scene_name"]) and (len(data_repaet1) != 0)) or ((msgFromServer["origin_scene_number"] != msgFromServer["scene_number"]) and (msgFromServer["origin_scene_name"] == msgFromServer["scene_name"]) and (len(data_repaet2) != 0)) or ((msgFromServer["origin_scene_number"] != msgFromServer["scene_number"]) and (msgFromServer["origin_scene_name"] != msgFromServer["scene_name"] and len(data_repaet3) != 0)):
                        message = json.dumps({"state":"repeat error"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','scene','repeat error','%s')"%(this_gateway_uid,current_time)
                    else:
                        for_log = ""
                        exists_scene_number = []
                        switch.delete_scene(int(msgFromServer["origin_scene_number"]))
                        sql = "DELETE FROM scenes WHERE scene_number = '%s'"%(msgFromServer["origin_scene_number"])
                        result = dbh.execute(sql)
                        for_log = for_log + "\n" + sql
                        for i in range(0, msgFromServer["length"], 1):
                            sql = "INSERT INTO scenes(node,node_state,scene_name,scene_number,created_at,updated_at)VALUES('%s','%s','%s','%s','%s','%s')"%(msgFromServer["node_id"][i],msgFromServer["node_value"][i],msgFromServer["scene_name"],msgFromServer["scene_number"],current_time,current_time)
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                        switch.set_scene(int(msgFromServer["scene_number"]))
                        message = json.dumps({"state":"ok"})
                        message_for_client = json.dumps([{
                            'origin_scene_number' : msgFromServer["origin_scene_number"],
                            'scene_number' : msgFromServer["scene_number"],
                            'scene_name' : msgFromServer["scene_name"]
                        }])
                        time.sleep(0.5)
                        publish.single("{}/client_response/{}".format(this_gateway_uid, "scene/update"), message_for_client, qos=2, hostname=mqtt_host)
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','scene',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','scene','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except :
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "scene_setting/update"), message, qos=2, hostname=mqtt_host)

            elif table == 'setting':
                print("###################scene_setting/setting######################")
                try:
                    sql = "SELECT * FROM node"
                    Node_data = dbh.query(sql)
                    scenes_node_data = []
                    for data in Node_data:
                        scenes_node_data.append({
                            'id' : data["id"],
                            'model' : data["model"],
                            'node_name' : data["node_name"],
                            'scene_node_state' : "0" if data["model"] in model_percent else "1"
                        })
                    message = json.dumps([{"state" : "ok"},scenes_node_data])
                except BaseException as n:
                    print("fail:",n)
                    message =json.dumps({"state" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "scene_setting/setting"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'insert':
                print("###################scene_setting/insert######################")
                try:
                    sql = "SELECT  DISTINCT scene_number FROM scenes "
                    overcount_check = dbh.query(sql)
                    sql2 = "SELECT * FROM scenes WHERE scene_number='%s' OR scene_name='%s'"%(msgFromServer["scene_number"],msgFromServer["scene_name"])
                    repeat_check = dbh.query(sql2)
                    if len(overcount_check) >= 32:
                        message = json.dumps([{"state" : "overcount"}])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','scene','overcount','%s')"%(this_gateway_uid,current_time)
                    elif len(repeat_check) != 0:
                        message = json.dumps([{"state" : "repeat error"}])
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','scene','repeat error','%s')"%(this_gateway_uid,current_time)
                    else:
                        for_log = ""
                        for i in range(0, msgFromServer["length"], 1):
                            sql = "INSERT INTO scenes(node,node_state,scene_name,scene_number,created_at)VALUES('%s','%s','%s','%s','%s')"%(msgFromServer["node_id"][i],msgFromServer["node_value"][i],msgFromServer["scene_name"],msgFromServer["scene_number"],current_time)
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                        sql = "SELECT * FROM scenes WHERE scene_number='%s'"%(msgFromServer["scene_number"])
                        scene_data = dbh.query(sql)
                        scene_node_data_output = []
                        for data in scene_data:
                            scene_node_data_output.append({
                                'id' : data["id"],
                                'node' : data["node"],
                                'node_state' : data["node_state"],
                                'scene_name' : data["scene_name"],
                                'scene_number' : data["scene_number"]
                            })
                        message = json.dumps([{"state":"ok"},scene_node_data_output])
                        switch.set_scene(int(msgFromServer["scene_number"]))
                        message_for_client = json.dumps([{
                            'scene_name' : scene_node_data_output[0]["scene_name"],
                            'scene_number' : scene_node_data_output[0]["scene_number"]
                        }])
                        time.sleep(0.5)
                        publish.single("{}/client_response/{}".format(this_gateway_uid, "scene/insert"), message_for_client, qos=2, hostname=mqtt_host)
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','scene',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                except  BaseException as n:
                    print("fail:",n)
                    message =json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','scene','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "scene_setting/insert"), message, qos=2, hostname=mqtt_host)
        dbh.close()
    
topic_list = ["node_setting/insert","node_setting/update","node_setting/delete","group_setting/insert","group_node_setting/setting","group_setting/delete","group_setting/update","scene_setting/delete","scene_setting/update_information","scene_setting/update","scene_setting/setting","scene_setting/insert"]#訂閱主題清單

#uuid之後改為用query gatwayid的欄位或global變數

if __name__ == "__main__":
    mqtt_host = gateway_setting.mqtt_host#global變數
    for topic in topic_list:
        mqtt_subscribe = MqttSubscribe(mqtt_host, this_gateway_uid, topic)
    mqtt_service = threading.Thread(target=mqtt_subscribe.run)
    mqtt_service.start()
