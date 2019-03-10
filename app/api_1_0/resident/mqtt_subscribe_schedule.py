import sys
import os
import time
from time import sleep
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
import method.cflag as cflag

this_gateway_uid = gateway_setting.uid
model_percent = ['LT4500']
time_region=['sunset' , 'sunrise']
def check_other_controltime(temp_time, search):
    controltime = ""
    count = 0
    date_state = {}
    try:
        dbh = daesql.MySQL(dbconfig.mysql_config)
        sql = "SELECT * FROM gateway "
        results = dbh.query(sql)
        sunrise = datetime.datetime.strptime(str(results[0]["sunrise"]), "%H:%M:%S").strftime("%H:%M:%S")
        sunset = datetime.datetime.strptime(str(results[0]["sunset"]), "%H:%M:%S").strftime("%H:%M:%S")
        while(count != 7):
            temp_time = (temp_time + timedelta(days=1)) if (search == "+") else (temp_time - timedelta(days=1))
            date_state = today_check(temp_time.strftime("%Y-%m-%d"), date_state)
            table = transformdate(date_state)
            sql = "SELECT DISTINCT control_time,control_time_of_sun FROM schedule WHERE schedule_table ='%s' GROUP BY control_time,control_time_of_sun"%(table)
            date_data = dbh.query(sql)
            if len(date_data) != 0:
                date_info = []
                for data in date_data:
                    date_info.append({
                        'control_time': (sunrise if (data["control_time_of_sun"] == 'sunrise') else sunset) if (data["control_time"] is None) else datetime.datetime.strptime(str(data["control_time"]), "%H:%M:%S").strftime("%H:%M:%S")
                    })
                date_info = sorted(date_info, key = lambda k: k['control_time']) 
                temp_date = datetime.datetime.strftime(temp_time,"%Y-%m-%d %H:%M:%S").split()[0]
                controltime = {
                    'control_time' : date_info[0]['control_time'] if (search == "+") else date_info[len(date_info) - 1]['control_time'],
                    'weekday' : temp_time.weekday(),
                    'date' : temp_date
                }
                return (controltime)
            elif count == 6:
                controltime = {
                    'control_time' : "後七天無設定" if (search == "+") else "前七天無設定",
                    'weekday' : "",
                    'date' : ""
                }
                return (controltime)
            count+=1
        dbh.close
    except BaseException as n:
        print("fail:",n)
    return (controltime)

def today_check(today, today_state):
    try:
        dbh = daesql.MySQL(dbconfig.mysql_config)
        sql = "SELECT * FROM festival"
        festival_info = dbh.query(sql)
        dbh.close
        today_state = {}
        today_state['today_state'] = '無'
        today_state['bind_table'] = '工作日'
        for data in festival_info:
            if str(data["date"]) == today:
                today_state['today_state'] = data["statement"]
                today_state['bind_table'] = '例假日'
                return today_state
        return today_state
    except  BaseException as n:
        print("fail:",n)
        return {"state":"failed"}

def transformdate(today_state):
    bind_table = ""
    if(today_state['bind_table'] == "工作日"):
        bind_table = "weekday"
    else:
        bind_table = "holiday"
    return bind_table

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
        if action == 'schedule_setting':
            if table == 'initset':
                print("###################schedule_setting/initset######################")
                try:
                    if msgFromServer["method"] == "GET":
                        sql = "SELECT schedule.schedule_table, schedule.id, schedule.group_id,schedule.schedule_group_state, schedule.control_time, schedule.control_time_of_sun, `group`.group_name, `group`.group_num FROM schedule JOIN `group` ON schedule.group_id = `group`.id ORDER BY schedule.control_time , schedule.group_id"
                        schedule_data = dbh.query(sql)
                        schedule_time = {}
                        schedule_time[str('weekday')] = []
                        schedule_time[str('holiday')] = []
                        for data in schedule_data:
                            control_time = data["control_time_of_sun"] if (data["control_time"] is None) else datetime.datetime.strptime(str(data["control_time"]), '%H:%M:%S').strftime('%H:%M')
                            if control_time not in schedule_time[str(data["schedule_table"])]:
                                schedule_time[str(data["schedule_table"])].append(control_time)
                        message =json.dumps(schedule_time)
                    elif msgFromServer["method"] == "POST":
                        sql = "SELECT schedule.schedule_table, schedule.id, schedule.group_id,schedule.schedule_group_state, schedule.control_time, schedule.control_time_of_sun, `group`.group_name, `group`.group_num, schedule.setting FROM schedule JOIN `group` ON schedule.group_id = `group`.id WHERE schedule_table ='%s' AND (control_time ='%s' OR control_time_of_sun ='%s') ORDER BY `group`.group_num"%(msgFromServer["schedule_table"],msgFromServer["control_time"],msgFromServer["control_time"])
                        schedule_data = dbh.query(sql)
                        schedule_time = {}
                        schedule_time[str(msgFromServer["schedule_table"])] = {}
                        for data in schedule_data:
                            control_time = data["control_time_of_sun"] if (data["control_time"] is None) else datetime.datetime.strptime(str(data["control_time"]), '%H:%M:%S').strftime('%H:%M')
                            if control_time not in schedule_time[str(data["schedule_table"])]:
                                schedule_time[str(data["schedule_table"])][control_time] = []
                            schedule_time[str(data["schedule_table"])][control_time].append({
                                "schedule_table" : data["schedule_table"],
                                "group_id" : data["group_id"],
                                "schedule_group_state" : data["schedule_group_state"],
                                "control_time" : control_time,
                                "group_number" : data["group_num"],
                                "group_name" : data["group_name"],
                                "setting" : data["setting"]
                            })
                        message = json.dumps(schedule_time)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state":"failed"})
                print(message)
                sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "schedule_setting/initset"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'insert':
                print("###################schedule_setting/insert######################")
                try:
                    sql = "SELECT DISTINCT control_time FROM schedule where schedule_table='%s'"%(msgFromServer["Schedule_time_group"]['festival'])
                    schedule_overcount_check = dbh.query(sql)
                    sql2 = "SELECT DISTINCT control_time FROM schedule where schedule_table='%s' AND (control_time='%s' OR control_time_of_sun='%s')"%(msgFromServer["Schedule_time_group"]['festival'],msgFromServer["Schedule_time_group"]['control_time'],msgFromServer["Schedule_time_group"]['control_time'])
                    schedule_repeat_check = dbh.query(sql2)
                    if len(schedule_overcount_check) >= 24:
                        message = json.dumps({"state" : "overcount"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','schedule','overcount','%s')"%(this_gateway_uid,current_time)
                    elif len(schedule_repeat_check) > 0:
                        message = json.dumps({"state" : "repeat"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','schedule','repeat','%s')"%(this_gateway_uid,current_time)
                    else:
                        for_log = ""
                        sql = "SELECT * FROM gateway "
                        results = dbh.query(sql)
                        sunrise = datetime.datetime.strptime(str(results[0]["sunrise"]), "%H:%M:%S").strftime("%H:%M:%S")
                        sunset = datetime.datetime.strptime(str(results[0]["sunset"]), "%H:%M:%S").strftime("%H:%M:%S")
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        for data in msgFromServer["Schedule_time_group"]['Schedule_group_list']:
                            sql = "INSERT INTO schedule(schedule_table,group_id,schedule_group_state," + ("control_time_of_sun" if (msgFromServer["Schedule_time_group"]['control_time'] in time_region) else "control_time") + ",setting)VALUES('%s','%s','%s','%s','%s')"%(msgFromServer["Schedule_time_group"]['festival'],str(data["group_id"]),data["group_state"],msgFromServer["Schedule_time_group"]['control_time'],data["group_setting"])
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                            message = json.dumps({"state" : "ok"})
                            log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','insert','schedule',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                        message_for_client = json.dumps({
                            'festival' : msgFromServer["Schedule_time_group"]['festival'],
                            'control_time' : msgFromServer["Schedule_time_group"]['control_time']
                        })
                        time.sleep(0.5)
                        publish.single("{}/client_response/{}".format(this_gateway_uid, "schedule/insert"), message_for_client, qos=2, hostname=mqtt_host)
                        cflag.cflag()
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','insert','schedule','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except BaseException as n:
                    print("log_failed")
                print(message)
                sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "schedule_setting/insert"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'delete':
                print("###################schedule_setting/delete######################")
                try:
                    sql = "DELETE FROM schedule WHERE " + ("control_time_of_sun" if (msgFromServer["control_time"] in time_region) else "control_time") + "='%s' AND schedule_table ='%s'"%(msgFromServer["control_time"],msgFromServer["festival"])
                    result = dbh.execute(sql)
                    message_for_client = json.dumps({
                        'festival' : msgFromServer["festival"],
                        'control_time' : msgFromServer["control_time"]
                    })
                    time.sleep(0.5)
                    publish.single("{}/client_response/{}".format(this_gateway_uid, "schedule/delete"), message_for_client, qos=2, hostname=mqtt_host)
                    message = json.dumps({"state" : "ok"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','delete','schedule',\"%s\",'ok','%s')"%(this_gateway_uid,"\n"+sql,current_time)
                    cflag.cflag()
                except  BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','delete','schedule','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except BaseException as n:
                    print("log_failed")
                print(message)
                sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "schedule_setting/delete"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'information':
                print("###################schedule_setting/information######################")
                try:
                    group = []
                    sql = "SELECT * FROM `group`"
                    Group_name = dbh.query(sql)
                    for data in Group_name:
                        group.append({
                            'group_name' : data["group_name"],
                            'group_id' : data["id"]
                        })
                    message = json.dumps(group)
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                print(message)
                sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "schedule_setting/information"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'update':
                print("###################schedule_setting/update######################")
                try:
                    sql1 = "SELECT * FROM schedule where schedule_table='%s' AND (control_time='%s' OR control_time_of_sun='%s')"%(msgFromServer["schedule_data"]['festival'],msgFromServer["schedule_data"]['update_control_time'],msgFromServer["schedule_data"]['update_control_time'])
                    control_time_repeat_check = dbh.query(sql1)
                    if( msgFromServer["schedule_data"]['origin_control_time'] != msgFromServer["schedule_data"]['update_control_time'] and len(control_time_repeat_check) > 0):
                        message = json.dumps({"state" : "repeat"})
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, execute_state, `datetime`)VALUES('Server','%s','update','schedule','repeat','%s')"%(this_gateway_uid,current_time)
                    else:
                        for_log = ""
                        for i in range(0, int(msgFromServer["schedule_data"]["length"]), 1):
                            if (msgFromServer["schedule_data"]['update_control_time']  in time_region):
                                if (msgFromServer["schedule_data"]['origin_control_time']  in time_region):
                                    sql = "UPDATE schedule SET setting='%s', schedule_group_state='%s',control_time= null,control_time_of_sun= '%s' WHERE schedule_table ='%s' AND control_time_of_sun='%s' AND group_id='%s'"%(str(msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_setting']),msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_state'],msgFromServer["schedule_data"]['update_control_time'],msgFromServer["schedule_data"]['festival'],msgFromServer["schedule_data"]["origin_control_time"],msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_id'])
                                else:
                                    sql = "UPDATE schedule SET setting='%s', schedule_group_state='%s',control_time= null,control_time_of_sun= '%s' WHERE schedule_table ='%s' AND control_time='%s' AND group_id='%s'"%(str(msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_setting']),msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_state'],msgFromServer["schedule_data"]['update_control_time'],msgFromServer["schedule_data"]['festival'],msgFromServer["schedule_data"]["origin_control_time"],msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_id'])
                            else:
                                if (msgFromServer["schedule_data"]['origin_control_time']  in time_region):
                                    sql = "UPDATE schedule SET setting='%s', schedule_group_state= '%s',control_time= '%s',control_time_of_sun= null WHERE schedule_table ='%s' AND control_time_of_sun='%s' AND group_id='%s'"%(str(msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_setting']),msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_state'],msgFromServer["schedule_data"]['update_control_time'],msgFromServer["schedule_data"]['festival'],msgFromServer["schedule_data"]["origin_control_time"],msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_id'])
                                else:
                                    sql = "UPDATE schedule SET setting='%s', schedule_group_state= '%s',control_time= '%s',control_time_of_sun= null WHERE schedule_table ='%s' AND control_time='%s' AND group_id='%s'"%(str(msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_setting']),msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_state'],msgFromServer["schedule_data"]['update_control_time'],msgFromServer["schedule_data"]['festival'],msgFromServer["schedule_data"]["origin_control_time"],msgFromServer["schedule_data"]['Schedule_group_list'][i]['group_id'])
                            result = dbh.execute(sql)
                            for_log = for_log + "\n" + sql
                            message = json.dumps({"state" : "ok"})
                        message_for_client = json.dumps({
                            'festival' : msgFromServer["schedule_data"]['festival'],
                            'control_time' : msgFromServer["schedule_data"]['update_control_time'],
                            'origin_control_time' : msgFromServer["schedule_data"]["origin_control_time"]
                        })
                        time.sleep(0.5)
                        publish.single("{}/client_response/{}".format(this_gateway_uid, "schedule/update"), message_for_client, qos=2, hostname=mqtt_host)
                        log_sql = "INSERT INTO log(role, gateway_uid, action, content, data, execute_state, `datetime`)VALUES('Server','%s','update','schedule',\"%s\",'ok','%s')"%(this_gateway_uid,for_log,current_time)
                        cflag.cflag()
                except BaseException as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                    log_sql = "INSERT INTO log(role, gateway_uid, action, content,  execute_state, `datetime`)VALUES('Server','%s','update','schedule','failed','%s')"%(this_gateway_uid,current_time)
                try:
                    result = dbh.execute(log_sql)
                except BaseException as n:
                    print("log_failed")
                print(message)
                sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "schedule_setting/update"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'today_state':
                print("###################schedule_setting/today_state######################")
                try:
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    today_state = {}
                    today_info = today_check(today, today_state)
                    message = json.dumps(today_info)
                except BaseException as n:
                    print("fail:",n)
                    message =json.dumps({"state" : "failed"})
                print(message)
                sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "schedule_setting/today_state"), message, qos=2, hostname=mqtt_host)
        
            elif table == 'prev_next_control_time':
                print("###################schedule_setting/prev_next_control_time######################")
                current_time = datetime.datetime.now()
                current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[0]
                compare_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").split()[1]
                controltime = ""
                next_controltime = ""
                try:
                    sql = "SELECT * FROM gateway "
                    results = dbh.query(sql)
                    sunrise = datetime.datetime.strptime(str(results[0]["sunrise"]), "%H:%M:%S").strftime("%H:%M:%S")
                    sunset = datetime.datetime.strptime(str(results[0]["sunset"]), "%H:%M:%S").strftime("%H:%M:%S")
                    today_state = {}
                    today_state = today_check(current_date, today_state)
                    bind_table = transformdate(today_state)
                    state = {}
                    sql = "SELECT DISTINCT control_time,control_time_of_sun FROM schedule WHERE schedule_table ='%s' GROUP BY control_time,control_time_of_sun"%(bind_table)
                    current_timeInfo = dbh.query(sql)
                    current_info = []
                    if len(current_timeInfo) == 0:
                        temp_time = datetime.datetime.now()
                        next_controltime = check_other_controltime(temp_time,'+')
                        controltime = check_other_controltime(temp_time,'-')
                        message = json.dumps([{"state" : "ok"}, controltime, next_controltime])
                    else:
                        for data in current_timeInfo:
                            current_info.append({
                                'control_time': (sunrise if (data["control_time_of_sun"] == 'sunrise') else sunset) if (data["control_time"] is None) else datetime.datetime.strptime(str(data["control_time"]), "%H:%M:%S").strftime("%H:%M:%S")
                            })
                        current_info = sorted(current_info, key = lambda k: k['control_time']) 
                        temp_time = datetime.datetime.now()
                        if compare_time < current_info[0]['control_time']:
                            controltime = check_other_controltime(temp_time,'-')
                            next_controltime = {
                                'control_time' : current_info[0]['control_time'],
                                'weekday' : current_time.weekday(),
                                'date' : current_date
                            }
                            message = json.dumps([{"state" : "ok"}, controltime, next_controltime])
                        elif compare_time >= current_info[len(current_info) - 1]['control_time']:
                            controltime = {
                                'control_time' : current_info[len(current_info) - 1]['control_time'],
                                'weekday' : current_time.weekday(),
                                'date' : current_date
                            }
                            next_controltime = check_other_controltime(temp_time,'+')
                            message = json.dumps([{"state" : "ok"}, controltime, next_controltime])
                        else:
                            for_index = 0
                            while(for_index < len(current_info)):
                                if current_info[for_index]['control_time'] <= compare_time and compare_time < current_info[for_index + 1]['control_time']:
                                    break;
                                for_index = for_index + 1
                            controltime = {
                                'control_time' : current_info[for_index]['control_time'],
                                'weekday' : current_time.weekday(),
                                'date' : current_date
                            }
                            next_controltime = {
                                'control_time' : current_info[for_index + 1]['control_time'],
                                'weekday' : current_time.weekday(),
                                'date' : current_date
                            }
                            message = json.dumps([{"state" : "ok"}, controltime, next_controltime])
                except Exception as n:
                    print("fail:",n)
                    message = json.dumps({"state" : "failed"})
                print(message)
                sleep(0.5)
                publish.single("{}/response/{}".format(this_gateway_uid, "schedule_setting/prev_next_control_time"), message, qos=2, hostname=mqtt_host)
        dbh.close()

topic_list = ["schedule_setting/initset", "schedule_setting/insert","schedule_setting/delete", "schedule_setting/information","schedule_setting/update", "schedule_setting/time_check","schedule_setting/today_state","schedule_setting/prev_next_control_time"]#訂閱主題清單

#uuid之後改為用query gatwayid的欄位或global變數

if __name__ == "__main__":
    mqtt_host = gateway_setting.mqtt_host#global變數
    for topic in topic_list:
        mqtt_subscribe = MqttSubscribe(mqtt_host, this_gateway_uid, topic)
    mqtt_service = threading.Thread(target=mqtt_subscribe.run)
    mqtt_service.start()