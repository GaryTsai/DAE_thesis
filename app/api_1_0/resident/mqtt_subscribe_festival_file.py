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
import googlemaps
import method.forSunSetRise as sunsetrise
import method.cflag as cflag

#import pymysql
#使用pymysql前將資料庫名稱帳戶密碼資訊寫成global變數呼叫

this_gateway_uid = gateway_setting.uid
model_percent = ['LT4500']
time_region=['sunset' , 'sunrise']
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def transfer_time(value):
    if (value is None):
        return None
    else:
        hours, remainder = divmod(value.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if(hours == 0):
            hours = str(hours)+'0'
        if(minutes == 0):
            minutes = str(minutes)+'0'
        if(seconds == 0):
            seconds = str(seconds)+'0'
        return  '{}:{}:{}'.format(hours, minutes, seconds)


def transfer_json(table, final_output):
    final_output[table] = []
    try:
        dbh = daesql.MySQL(dbconfig.mysql_config)
        if table == "Schedule":
            sql = "SELECT * FROM schedule"
            result = dbh.query(sql)
            for data in result:
                final_output[table].append({
                    'id' : data["id"],
                    'schedule_table': data["schedule_table"],
                    'group_id': data["group_id"],
                    'schedule_group_state': data["schedule_group_state"],
                    'control_time': transfer_time(data["control_time"]),
                    'control_time_of_sun': data["control_time_of_sun"],
                    'setting': data["setting"]
                })
        if table == "festival":
            sql = "SELECT * FROM festival"
            result = dbh.query(sql)
            for data in result:
                final_output[table].append({
                    'id': data["id"],
                    'date': data["date"].strftime("%Y-%m-%d"),
                    'statement': data["statement"],
                    'bind_table': data["bind_table"]
                })
        if table == "Node":
            sql = "SELECT * FROM node"
            result = dbh.query(sql)
            for data in result:
                final_output[table].append({
                    'id': data["id"],
                    'gateway': data["gateway"],
                    'gateway_address': data["gateway_address"],
                    'model': data["model"],
                    'node_name': data["node_name"],
                    'node': data["node"],
                    'created_at': data["created_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["created_at"] is not None) else None,
                    'updated_at': data["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["updated_at"] is not None) else None,
                    'model_type': data["model_type"],
                    'group_id': data["group_id"],
                    'node_state': data["node_state"]
                })
        if table == "Group":
            sql = "SELECT * FROM `group`"
            result = dbh.query(sql)
            for data in result:
                final_output[table].append({
                    'id': data["id"],
                    'group_num': data["group_num"],
                    'group_name': data["group_name"],
                    'group_state': data["group_state"],
                    'created_at': data["created_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["created_at"] is not None) else None,
                    'updated_at': data["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["updated_at"] is not None) else None,

                })
        if table == "Scenes":
            sql = "SELECT * FROM scenes"
            result = dbh.query(sql)
            for data in result:
                final_output[table].append({
                    'id': data["id"],
                    'node': data["node"],
                    'node_state': data["node_state"],
                    'scene_name': data["scene_name"],
                    'scene_number': data["scene_number"],
                    'created_at': data["created_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["created_at"] is not None) else None,
                    'updated_at': data["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["updated_at"] is not None) else None,
                })
        if table == "Setting":
            sql = "SELECT * FROM setting"
            result = dbh.query(sql)
            for data in result:
                final_output[table].append({
                    'id': data["id"],
                    'model': data["model"],
                    'address': data["address"],
                    'ch': data["ch"],
                    'speed': data["speed"],
                    'circuit': data["circuit"],
                    'pt': data["pt"],
                    'ct': data["ct"],
                    'meter_type': data["meter_type"],
                    'created_at': data["created_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["created_at"] is not None) else None,
                    'updated_at': data["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if (data["updated_at"] is not None) else None,
                    'gateway_uid': data["gateway_uid"]
                })
        dbh.close
        return final_output
    except BaseException as n:
        print("fail:",n)
        return {"state":"failed"}

def insert_into_string(state_one, state_two, column_data, column_name):
    if column_data != None:
        state_one = state_one + column_name
        state_two = state_two + ",'%s'"%(column_data)
    return state_one, state_two


def insert_file(table, content):
    try:
        dbh = daesql.MySQL(dbconfig.mysql_config)
        for_log = ""
        if table == "Schedule":
            for data in content[table]:
                state_one = "INSERT INTO schedule(id"
                state_two = ")VALUES('%s'"%(data['id'])
                for key in data.keys():
                    if key != "id":
                        state_one, state_two = insert_into_string(state_one, state_two, data[key], ", "+str(key))
                sql = state_one + state_two + ")"
                dbh.execute(sql)
                for_log = for_log + "\n" + sql
            cflag.cflag()
            for_get_distinct_schedule = []
            for data in content[table]:
                control_time = data['control_time'] if (data['control_time'] != None) else data['control_time_of_sun']
                if control_time not in for_get_distinct_schedule:
                    for_get_distinct_schedule.append(control_time)
                    message_for_client = json.dumps({
                        'festival' : data['schedule_table'],
                        'control_time' : control_time
                    })
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "schedule/insert"), message_for_client, qos=2, hostname=mqtt_host)
            log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','file',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
        if table == "festival":
            for data in content[table]:
                state_one = "INSERT INTO festival(id"
                state_two = ")VALUES('%s'"%(data['id'])
                for key in data.keys():
                    if key != "id":
                        state_one, state_two = insert_into_string(state_one, state_two, data[key], ", "+str(key))
                sql = state_one + state_two + ")"
                dbh.execute(sql)
                for_log = for_log + "\n" + sql
            cflag.cflag()
            log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','file',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
        if table == "Node":
            for data in content[table]:
                state_one = "INSERT INTO node(id"
                state_two = ")VALUES('%s'"%(data['id'])
                for key in data.keys():
                    if key != "id":
                        state_one, state_two = insert_into_string(state_one, state_two, data[key], ", "+str(key))
                sql = state_one + state_two + ")"
                dbh.execute(sql)
                for_log = for_log + "\n" + sql
                node_data=[]
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
                message_for_client =json.dumps(node_data)
                time.sleep(0.5)
                publish.single("{}/client_response/{}".format(this_gateway_uid, "node/insert"), message_for_client, qos=2, hostname=mqtt_host)
            log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','file',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
        if table == "Group":
            for data in content[table]:
                state_one = "INSERT INTO `group`(id"
                state_two = ")VALUES('%s'"%(data['id'])
                for key in data.keys():
                    if key != "id":
                        state_one, state_two = insert_into_string(state_one, state_two, data[key], ", "+str(key))
                sql = state_one + state_two + ")"
                dbh.execute(sql)
                for_log = for_log + "\n" + sql
            log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','file',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
        if table == "Scenes":
            for data in content[table]:
                state_one = "INSERT INTO scenes(id"
                state_two = ")VALUES('%s'"%(data['id'])
                for key in data.keys():
                    if key != "id":
                        state_one, state_two = insert_into_string(state_one, state_two, data[key], ", "+str(key))
                sql = state_one + state_two + ")"
                dbh.execute(sql)
                for_log = for_log + "\n" + sql
            for_get_distinct_scene = []
            for data in content[table]:
                if data['scene_number'] not in for_get_distinct_scene:
                    for_get_distinct_scene.append(data['scene_number'])
                    switch.set_scene(int(data["scene_number"]))
                    node_data = []
                    node_data.append({
                        'scene_name': data["scene_name"],
                        'scene_number': data["scene_number"]
                    })
                    message_for_client =json.dumps(node_data)
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "scene/insert"), message_for_client, qos=2, hostname=mqtt_host)
            log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','file',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
        if table == "Setting":
            for data in content[table]:
                state_one = "INSERT INTO setting(id"
                state_two = ")VALUES('%s'"%(data['id'])
                for key in data.keys():
                    if key != "id":
                        state_one, state_two = insert_into_string(state_one, state_two, data[key], ", "+str(key))
                sql = state_one + state_two + ")"
                dbh.execute(sql)
                for_log = for_log + "\n" + sql
            log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','file',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
        dbh.close
    except BaseException as n:
        print("fail:",n)
        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','scene','failed','%s')"%(this_gateway_uid,current_time)
    try:
        result = dbh.execute(log_sql)
    except BaseException as n:
        print("log_failed")

def week_transform(weekday):
    if(weekday) == 6:
        weekday == 0
    else:
        weekday += 1
    return weekday

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
        if action == 'festival_setting':
            if table == 'information':
                print("###################festival_setting/information######################")
                try:
                    sql = "SELECT * FROM festival ORDER BY `date`"
                    festival_information = dbh.query(sql)
                    festival_list = []
                    for data in festival_information:
                        festival_list.append({
                            'id': data["id"],
                            'date': data["date"].strftime("%Y-%m-%d %H:%M:%S"),
                            'statement': data["statement"],
                            'bind_table': data["bind_table"]
                        })
                    message = json.dumps(festival_list)
                except BaseException as n:
                    print("fail:",n)
                    message =json.dumps({"state" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "festival_setting/information"), message, qos=2, hostname=mqtt_host)
            elif table == 'rest_days_get':
                print("###################festival_setting/rest_days_get######################")
                try:
                    sql = "SELECT `date` FROM festival"
                    result = dbh.query(sql)
                    rest_days = [row["date"].strftime("%Y-%m-%d %H:%M:%S") for row in result]
                    message = json.dumps(rest_days)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "festival_setting/rest_days_get"), message, qos=2, hostname=mqtt_host)
            
            elif table == 'rest_days_post':
                print("###################festival_setting/rest_days_post######################")
                try:
                    for_log = ""
                    sql = "SELECT `date` FROM festival"
                    origin = dbh.query(sql)
                    origin_date = []
                    for data in origin:
                        origin_date.append(data["date"])
                    for date in msgFromServer["rest_days"]:
                        sql = "SELECT * FROM festival WHERE `date`='%s'"%(date)
                        result = dbh.query(sql)
                        ret = False if (len(result) == 0) else True
                        if ret is False:
                            weekday = datetime.datetime.strptime(str(date), "%Y-%m-%d").weekday()
                            weekday = week_transform(weekday)
                            sql = ""
                            if(str(date) in msgFromServer["week_statement"]):
                                sql = "INSERT INTO festival(`date`,statement,bind_table)VALUES('%s','%s','%s')"%(date,msgFromServer["week_statement"][str(date)],'holiday')
                                result = dbh.execute(sql)
                            elif str(date) in msgFromServer["month_statement"]:
                                sql = "INSERT INTO festival(`date`,statement,bind_table)VALUES('%s','%s','%s')"%(date,msgFromServer["month_statement"][str(date)],'holiday')
                                result = dbh.execute(sql)
                            elif msgFromServer["everyMonthWeek_thisday"]!={}:
                                for data in msgFromServer["everyMonthWeek_number"]:
                                    for key in data:
                                        if str(date) in msgFromServer["everyMonthWeek_thisday"][str(key)][str(data[key])]:
                                            state = "INSERT INTO festival(`date`,statement,bind_table)VALUES('%s','%s','%s')"%(date,msgFromServer["everyMonthWeek_statement"][str(key)][str(data[key])],'holiday')
                                            result = dbh.execute(state)
                                            sql = sql + "\n" + state
                                        else:
                                            state = "INSERT INTO festival(`date`,statement,bind_table)VALUES('%s','%s','%s')"%(date,msgFromServer["date_statement"][str(date)],'holiday')
                                            result = dbh.execute(state)
                                            sql = sql + "\n" + state
                            else:
                                sql = "INSERT INTO festival(`date`,statement,bind_table)VALUES('%s','%s','%s')" % (date, msgFromServer["date_statement"][str(date)], 'holiday')
                                result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                    for date in origin_date:
                        if(str(date) not in msgFromServer["rest_days"]):
                            sql = "DELETE FROM festival WHERE `date`='%s'"%(str(date))
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                    message = json.dumps({'status' : 200})
                    cflag.cflag()
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','festival',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"status" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','festival','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except BaseException as n:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "festival_setting/rest_days_post"), message, qos=2, hostname=mqtt_host)
        
        elif action == 'file':
            if table == 'export':
                print("###################file/export######################")
                try:
                    final_output = {}
                    for table in msgFromServer["file_list"]:
                        final_output = transfer_json(table, final_output)
                    message = json.dumps([final_output, {"state" : "ok"}])
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "file/export"), message, qos=2, hostname=mqtt_host)

            elif table == 'upload':
                print("###################file/upload######################")
                try:
                    file_table = ['Schedule','festival','Node','Scenes','Setting','Group']
                    group_scene_list = ['Group','Scenes']
                    content = json.loads(msgFromServer["file_data"])
                    message = json.dumps({"state" : "ok"})
                    if 'Group' in content.keys():
                        insert_file('Group', content)
                    for data_table in content:
                        if data_table not in file_table:
                            message = json.dumps({"state" : "file_error"})
                            break
                        elif data_table not in group_scene_list:
                            insert_file(data_table, content)
                    if 'Group' in content.keys():
                        for data in content['Group']:
                            switch.set_group(data['id'])
                            group_data = []
                            group_data.append({
                                'id': data["id"],
                                'group_num': data["group_num"],
                                'group_name': data["group_name"],
                                'group_state': data["group_state"]
                            })
                            message_for_client = json.dumps(group_data)
                            time.sleep(0.5)
                            publish.single("{}/client_response/{}".format(this_gateway_uid, "group/insert"), message_for_client, qos=2, hostname=mqtt_host)
                    if 'Scenes' in content.keys():
                        insert_file('Scenes', content)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "file/upload"), message, qos=2, hostname=mqtt_host)
        
        elif action == 'gateway_setting':
            if table == 'insert':
                print("###################gateway_setting/insert######################")
                try:
                    city = msgFromServer["country"]+msgFromServer["city"]+msgFromServer["physical_address"]
                    gmaps = googlemaps.Client(key='AIzaSyB-HvngwR_Y-Dhd-uohRRyTLyV8hTZvygU')
                    googlemapresult = gmaps.geocode(city)
                    lat = googlemapresult[0]['geometry']['location']['lat']
                    lng = googlemapresult[0]['geometry']['location']['lng']
                    sunrise, sunset = sunsetrise.sun_time(lng,lat)
                    sql = "UPDATE gateway SET country='%s', city='%s',physical_address='%s', gateway_name='%s', lat='%s', lng='%s',sunrise='%s',sunset='%s'"%(msgFromServer["country"],msgFromServer["city"],msgFromServer["physical_address"],msgFromServer["name"],lat,lng,sunrise,sunset)
                    result = dbh.execute(sql)
                    message = json.dumps([{"status" : "ok"}])
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','gateway_setting',\"%s\",'ok','%s')"%(this_gateway_uid,sql,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','gateway_setting','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except BaseException as n:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "gateway_setting/insert"), message, qos=2, hostname=mqtt_host)
            
            elif table == 'update':
                print("###################gateway_setting/update######################")
                try:
                    city = msgFromServer["country"]+msgFromServer["city"]+msgFromServer["physical_address"]
                    gmaps = googlemaps.Client(key='AIzaSyB-HvngwR_Y-Dhd-uohRRyTLyV8hTZvygU')
                    googlemapresult = gmaps.geocode(city)
                    lat = googlemapresult[0]['geometry']['location']['lat']
                    lng = googlemapresult[0]['geometry']['location']['lng']
                    sunrise, sunset = sunsetrise.sun_time(lng,lat)
                    sql = "UPDATE gateway SET country='%s', city='%s',physical_address='%s', gateway_name='%s', lat='%s', lng='%s',sunrise='%s',sunset='%s'"%(msgFromServer["country"],msgFromServer["city"],msgFromServer["physical_address"],msgFromServer["name"],lat,lng,sunrise,sunset)
                    result = dbh.execute(sql)
                    message = json.dumps([{"status" : "ok"}])
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','gateway_setting',\"%s\",'ok','%s')"%(this_gateway_uid,sql,current_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','gateway_setting','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except BaseException as n:
                    print("log_failed")
                print(message)
                time.sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "gateway_setting/update"), message, qos=2, hostname=mqtt_host)
        dbh.close()
    
topic_list = [ "festival_setting/information", "file/export", "file/upload", "festival_setting/rest_days_get", "festival_setting/rest_days_post", "gateway_setting/insert", "gateway_setting/update"]#訂閱主題清單

#uuid之後改為用query gatwayid的欄位或global變數

if __name__ == "__main__":
    mqtt_host = gateway_setting.mqtt_host#global變數
    for topic in topic_list:
        mqtt_subscribe = MqttSubscribe(mqtt_host, this_gateway_uid, topic)
    mqtt_service = threading.Thread(target=mqtt_subscribe.run)
    mqtt_service.start()