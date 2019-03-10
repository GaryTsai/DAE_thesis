import datetime
import json
import time
from datetime import timedelta
import os
from flask import json, jsonify, request
from sqlalchemy import and_, between, exists, func, or_
from config import role
from . import api, mqtttalker
from . import mqtttalker_client
from .resident.method import cflag as cflag
from .. import db
from ..models import *
from .log import log_info
from .resident.method.config.cloud_setting import *
from .resident.method.config.gateway_setting import *

#日出日落
time_region = ['sunset', 'sunrise']

@api.route('/schedule_setting/initset', methods=['POST', 'GET'])
def schedule_setting_initset():
    gateway_uid = ""
    control_time = ""
    state = {}
    if role == "Gateway":
        if request.method == "GET":
            gateway_uid = request.args.get('gateway_uid', default="", type=str)
            schedule_data = Schedule.query.join(Group, Schedule.group_id == Group.id).add_columns(
                Schedule.schedule_table, Schedule.id, Group.group_name, Group.group_num, Schedule.group_id, Schedule.schedule_group_state, Schedule.control_time, Schedule.control_time_of_sun).filter(Schedule.group_id == Group.id).order_by(Schedule.control_time, Schedule.group_id)
            schedule_time = {}
            schedule_time[str('weekday')] = []
            schedule_time[str('holiday')] = []
            # 初始化時間點
            for data in schedule_data:
                if data.control_time is None:
                    if str(data.control_time_of_sun) not in schedule_time[str(data.schedule_table)]:
                        schedule_time[str(data.schedule_table)].append(
                            data.control_time_of_sun)
                else:
                    control_time = datetime.datetime.strptime(
                        str(data.control_time), '%H:%M:%S').strftime('%H:%M')
                    if control_time not in schedule_time[str(data.schedule_table)]:
                        schedule_time[str(data.schedule_table)].append(
                            control_time)
            state['state'] = "ok"
            return jsonify(schedule_time), 201
        if request.method == "POST":
            gateway_uid = request.form.get('gateway_uid', default="", type=str)
            control_time = request.form.get(
                'control_time', default="", type=str)
            schedule_festival = request.form.get(
                'festival', default="", type=str)
            schedule_data = Schedule.query.join(Group, Schedule.group_id == Group.id).add_columns(
                Schedule.schedule_table,
                Schedule.id,
                Schedule.group_id,
                Schedule.schedule_group_state,
                Schedule.control_time, Schedule.control_time_of_sun, Group.group_name, Group.group_num, Schedule.setting).filter(or_(and_(Schedule.schedule_table == schedule_festival, Schedule.control_time == control_time), and_(Schedule.schedule_table == schedule_festival, Schedule.control_time_of_sun == control_time))).order_by(Group.group_num)

            schedule_time = {}
            schedule_time[str(schedule_festival)] = {}
            # 初始化時間點
            for data in schedule_data:
                if data.control_time is None:
                    if data.control_time_of_sun not in schedule_time[str(data.schedule_table)]:
                        schedule_time[str(data.schedule_table)
                                      ][data.control_time_of_sun] = []
                else:
                    control_time = datetime.datetime.strptime(
                        str(data.control_time), '%H:%M:%S').strftime('%H:%M')
                    if control_time not in schedule_time[str(data.schedule_table)]:
                        schedule_time[str(data.schedule_table)
                                      ][control_time] = []
            # 包裝每一個時間點的資料
            for data in schedule_data:
                if data.control_time != None and data.control_time_of_sun == None:
                    control_time = datetime.datetime.strptime(
                        str(data.control_time), '%H:%M:%S').strftime('%H:%M')
                    schedule_time[str(data.schedule_table)][control_time].append({
                        "schedule_table": data.schedule_table,
                        "group_id": data.group_id,
                        "schedule_group_state": data.schedule_group_state,
                        "control_time": datetime.datetime.strptime(str(data.control_time), '%H:%M:%S').strftime('%H:%M'),
                        "group_number": data.group_num,
                        "group_name": data.group_name,
                        "setting": data.setting
                    })
                elif data.control_time == None and data.control_time_of_sun != None:
                    schedule_time[str(data.schedule_table)][str(data.control_time_of_sun)].append({
                        "schedule_table": data.schedule_table,
                        "group_id": data.group_id,
                        "schedule_group_state": data.schedule_group_state,
                        "control_time": data.control_time_of_sun,
                        "group_number": data.group_num,
                        "group_name": data.group_name,
                        "setting": data.setting
                    })
            return jsonify(schedule_time), 201
    elif role == "Cloud":
        if request.method == "GET":
            gateway_uid = request.args.get('gateway_uid', default="", type=str)
            control_time = request.args.get(
                'control_time', default="", type=str)
            festival = request.args.get('festival', default="", type=str)
        elif request.method == "POST":
            gateway_uid = request.form.get('gateway_uid', default="", type=str)
            control_time = request.form.get(
                'control_time', default="", type=str)
            festival = request.form.get('festival', default="", type=str)
        message = json.dumps({
            'method': request.method,
            'control_time': control_time,
            'schedule_table': festival,
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "schedule_setting/initset", message)
        response = mqtt_talker.start()
        if response:
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/schedule_setting/insert', methods=['POST', 'GET'])
def schedule_setting_insert():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    state = {}
    Schedule_time_group = request.get_json()
    if role == "Gateway":
        # 判斷是否超過24個時間點
        time_count = db.session.query(Schedule.control_time).filter(
            Schedule.schedule_table == Schedule_time_group['festival']).distinct(Schedule.control_time).count()
        if time_count >= 24:
            state['state'] = 'overcount'
            log_info(Schedule_time_group['gateway_uid'],
                     "insert", "schedule", None, "overcount", "Gateway")
            return jsonify(state), 201
        elif db.session.query(Schedule.control_time).filter(or_(and_(Schedule.schedule_table == Schedule_time_group['festival'], Schedule.control_time == str(Schedule_time_group['control_time'])), and_(Schedule.schedule_table == Schedule_time_group['festival'], Schedule.control_time_of_sun == str(Schedule_time_group['control_time'])))).count() > 0:
            state['state'] = "repeat"
            log_info(Schedule_time_group['gateway_uid'],
                     "insert", "schedule", None, "repeat", "Gateway")
            return jsonify(state), 201
        else:
            for_log = ""
            sun = db.session.query(Gateway).all()
            for data in sun:
                sunrise = datetime.datetime.strptime(
                    str(data.sunrise), "%H:%M:%S").strftime("%H:%M:%S")
                sunset = datetime.datetime.strptime(
                    str(data.sunset), "%H:%M:%S").strftime("%H:%M:%S")
            # 判斷是否有設定日出日落
            for data in Schedule_time_group['Schedule_group_list']:
                if(Schedule_time_group['control_time'] in time_region):
                    insert_data = Schedule(None, Schedule_time_group['festival'], str(
                        data['group_id']), data['group_state'], None, Schedule_time_group['control_time'], data['group_setting'])
                    sql = "INSERT INTO schedule(schedule_table, group_id, schedule_group_state, control_time, control_time_of_sun, setting)VALUES('%s','%s','%s','false','%s','%s')" % (
                        Schedule_time_group['festival'], data['group_id'], data['group_state'],  Schedule_time_group['control_time'], data['group_setting'])
                else:
                    insert_data = Schedule(None, Schedule_time_group['festival'], str(data['group_id']),
                                           data['group_state'], Schedule_time_group['control_time'], None, data['group_setting'])
                    sql = "INSERT INTO schedule(chedule_table,group_id,schedule_group_state,control_time,control_time_of_sun,setting)VALUES('%s','%s','%s','%s','false','%s')" % (
                        Schedule_time_group['festival'], str(data['group_id']), data['group_state'], Schedule_time_group['control_time'], data['group_setting'])
                db.session.add(insert_data)
                for_log = for_log + "\n" + sql
            cflag.cflag()
            message_for_client = json.dumps({
                'festival' : Schedule_time_group['festival'],
                'control_time' : Schedule_time_group['control_time']
            })
            mqtt_talker = mqtttalker_client.MqttTalker(mqtt_host, Schedule_time_group['gateway_uid'], "schedule/insert", message_for_client)
            response = mqtt_talker.start()
            state['state'] = "ok"
            log_info(Schedule_time_group['gateway_uid'],
                     "insert", "schedule", for_log, "ok", "Gateway")
            db.session.commit()
            db.session.close()
            return jsonify(state), 201
    # 使用MQTT傳送起始期間與結束時間要加入判斷日落、日落Gateway時間功能
    elif role == "Cloud":
        message = json.dumps({
            'Schedule_time_group': Schedule_time_group
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, Schedule_time_group['gateway_uid'], "schedule_setting/insert", message)
        response = mqtt_talker.start()
        if response:
            log_info(Schedule_time_group['gateway_uid'], "insert", "schedule time", str(
                message), json.loads(response)['state'], "Cloud")
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/schedule_setting/delete', methods=['POST', 'GET'])
def schedule_setting_delete():
    festival = request.args.get('festival', default="", type=str)
    control_time = request.args.get('control_time', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    state = {}
    if role == "Gateway":
        if control_time in time_region:
            db.session.query(Schedule).filter(Schedule.control_time_of_sun ==
                                              control_time, Schedule.schedule_table == festival).delete()
            sql = "\nDELETE FROM schedule WHERE control_time ='%s' AND schedule_table ='%s'" % (
                time, festival)
            state['state'] = "ok"
            cflag.cflag()
            message_for_client = json.dumps({
                'festival' : festival,
                'control_time' : control_time
            })
            mqtt_talker = mqtttalker_client.MqttTalker(mqtt_host, gateway_uid, "schedule/delete", message_for_client)
            response = mqtt_talker.start()
            log_info(gateway_uid, "delete", "schedule", sql, "ok", "Gateway")
            db.session.commit()
            db.session.close()
            return jsonify(state), 201
        else:
            db.session.query(Schedule).filter(
                Schedule.control_time == control_time, Schedule.schedule_table == festival).delete()
            sql = "\nDELETE FROM schedule WHERE control_time ='%s' AND schedule_table ='%s'" % (
                time, festival)
            state['state'] = "ok"
            cflag.cflag()
            message_for_client = json.dumps({
                'festival' : festival,
                'control_time' : control_time
            })
            mqtt_talker = mqtttalker_client.MqttTalker(mqtt_host, gateway_uid, "schedule/delete", message_for_client)
            response = mqtt_talker.start()
            log_info(gateway_uid, "delete", "schedule", sql, "ok", "Gateway")
            db.session.commit()
            db.session.close()
            return jsonify(state), 201
    elif role == "Cloud":
        message = json.dumps({
            'festival': festival,
            'control_time': control_time
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "schedule_setting/delete", message)
        response = mqtt_talker.start()
        if response:
            log_info(gateway_uid, "delete", "schedule time", str(
                message), json.loads(response)['state'], "Cloud")
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/schedule_setting/update', methods=['POST', 'GET'])
def schedule_setting_update():
    schedule_data = request.get_json()
    state = {}
    if role == "Gateway":
        # 判斷是否遠本時間有無更新沒有則去更新群組，有則透過原本時間去更新
        control_time_count = db.session.query(Schedule.control_time).filter(and_(
            Schedule.control_time == schedule_data['update_control_time'], Schedule.schedule_table == schedule_data['festival'])).count()
        control_time_of_time_count = db.session.query(Schedule.control_time).filter(and_(
            Schedule.control_time_of_sun == schedule_data['update_control_time'], Schedule.schedule_table == schedule_data['festival'])).count()
        if(schedule_data['origin_control_time'] != schedule_data['update_control_time']and(control_time_count > 0 or control_time_of_time_count > 0)):
            state['state'] = "repeat"
            return jsonify(state), 201
        else:
            # 為加入控制時間判斷
            for_log = ""
            sql = ""
            for i in range(0, int(schedule_data['length']), 1):
                # 如果原本控制時間是sunrise、sunset
                if schedule_data['update_control_time'] in time_region:
                    if schedule_data['origin_control_time'] in time_region:
                        sql = "UPDATE schedule SET setting='%s', schedule_group_state='%s',control_time=null,control_time_of_sun = '%s' WHERE schedule_table ='%s' AND control_time_of_sun='%s' AND group_id='%s'" % (
                            schedule_data['Schedule_group_list'][i]['group_setting'], schedule_data['Schedule_group_list'][i]['group_state'], schedule_data['update_control_time'], schedule_data['festival'], schedule_data['origin_control_time'], schedule_data['Schedule_group_list'][i]['group_id'])
                        db.session.query(Schedule).filter(and_(Schedule.schedule_table == schedule_data['festival'], Schedule.control_time_of_sun == schedule_data['origin_control_time'], Schedule.group_id == schedule_data['Schedule_group_list'][i]['group_id'])).update({
                            Schedule.schedule_group_state: schedule_data['Schedule_group_list'][i]['group_state'],
                            Schedule.control_time: None,
                            Schedule.control_time_of_sun: schedule_data['update_control_time'],
                            Schedule.setting: str(schedule_data['Schedule_group_list'][i]['group_setting'])
                        })
                    else:
                        sql = "UPDATE schedule SET setting='%s', schedule_group_state='%s',control_time=null,control_time_of_sun = '%s' WHERE schedule_table ='%s' AND control_time='%s' AND group_id='%s'" % (
                            schedule_data['Schedule_group_list'][i]['group_setting'], schedule_data['Schedule_group_list'][i]['group_state'], schedule_data['update_control_time'], schedule_data['festival'], schedule_data['origin_control_time'], schedule_data['Schedule_group_list'][i]['group_id'])
                        db.session.query(Schedule).filter(and_(Schedule.schedule_table == schedule_data['festival'], Schedule.control_time == schedule_data['origin_control_time'], Schedule.group_id == schedule_data['Schedule_group_list'][i]['group_id'])).update({
                            Schedule.schedule_group_state: schedule_data['Schedule_group_list'][i]['group_state'],
                            Schedule.control_time: None,
                            Schedule.control_time_of_sun: schedule_data['update_control_time'],
                            Schedule.setting: str(schedule_data['Schedule_group_list'][i]['group_setting'])
                        })
                else:
                    if schedule_data['origin_control_time'] in time_region:
                        sql = "UPDATE schedule SET setting='%s', schedule_group_state='%s',control_time='%s',control_time_of_sun=null WHERE schedule_table ='%s' AND control_time_of_sun='%s' AND group_id='%s'" % (
                            schedule_data['Schedule_group_list'][i]['group_setting'], schedule_data['Schedule_group_list'][i]['group_state'], schedule_data['update_control_time'], schedule_data['festival'], schedule_data['origin_control_time'], schedule_data['Schedule_group_list'][i]['group_id'])
                        db.session.query(Schedule).filter(and_(Schedule.schedule_table == schedule_data['festival'], Schedule.control_time_of_sun == schedule_data['origin_control_time'], Schedule.group_id == schedule_data['Schedule_group_list'][i]['group_id'])).update({
                            Schedule.schedule_group_state: schedule_data['Schedule_group_list'][i]['group_state'],
                            Schedule.control_time: schedule_data['update_control_time'],
                            Schedule.control_time_of_sun: None,
                            Schedule.setting: str(schedule_data['Schedule_group_list'][i]['group_setting'])
                        })
                    else:
                        sql = "UPDATE schedule SET setting='%s', schedule_group_state='%s',control_time='%s',control_time_of_sun=null WHERE schedule_table ='%s' AND control_time='%s' AND group_id='%s'" % (
                            schedule_data['Schedule_group_list'][i]['group_setting'], schedule_data['Schedule_group_list'][i]['group_state'], schedule_data['update_control_time'], schedule_data['festival'], schedule_data['origin_control_time'], schedule_data['Schedule_group_list'][i]['group_id'])
                        db.session.query(Schedule).filter(and_(Schedule.schedule_table == schedule_data['festival'], Schedule.control_time == schedule_data['origin_control_time'], Schedule.group_id == schedule_data['Schedule_group_list'][i]['group_id'])).update({
                            Schedule.schedule_group_state: schedule_data['Schedule_group_list'][i]['group_state'],
                            Schedule.control_time: schedule_data['update_control_time'],
                            Schedule.control_time_of_sun: None,
                            Schedule.setting: str(schedule_data['Schedule_group_list'][i]['group_setting'])
                        })
                for_log = for_log + "\n" + sql
            state['state'] = "ok"
            cflag.cflag()
            message_for_client = json.dumps({
                'festival' : schedule_data['festival'],
                'control_time' : schedule_data['update_control_time'],
                'origin_control_time' : schedule_data["origin_control_time"]
            })
            mqtt_talker = mqtttalker_client.MqttTalker(mqtt_host, schedule_data['gateway_uid'], "schedule/update", message_for_client)
            response = mqtt_talker.start()
            log_info(schedule_data['gateway_uid'], "update",
                     "schedule", for_log, "ok", "Gateway")
            db.session.commit()
            db.session.close()
            return jsonify(state), 201
    elif role == "Cloud":
        message = json.dumps({
            'schedule_data': schedule_data
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, schedule_data['gateway_uid'], "schedule_setting/update", message)
        response = mqtt_talker.start()
        if response:
            log_info(schedule_data['gateway_uid'], "update", "schedule time", str(
                message), json.loads(response)['state'], "Cloud")
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/schedule_setting/information', methods=['POST', 'GET'])
def schedule_setting_information():
    Group_name = db.session.query(Group).all()
    group = []
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    if role == "Gateway":
        for data in Group_name:
            group.append({'group_name': data.group_name,
                          'group_id': data.id})
        return jsonify(group), 201
    elif role == "Cloud":
        message = json.dumps({})
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "schedule_setting/information", message)
        response = mqtt_talker.start()
        if response:
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/schedule_setting/today_state', methods=['POST', 'GET'])
def today_state():
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    today = datetime.datetime.now()
    today = today.strftime("%Y-%m-%d")
    today_info = today_check(today, gateway_uid)
    return jsonify(today_info), 201


def today_check(today, gateway_uid):
    if role == "Gateway":
        festival_info = db.session.query(festival).all()
        today_state = {}
        today = datetime.datetime.strptime(
            str(today), "%Y-%m-%d").strftime("%Y-%m-%d")
        if festival_info == []:
            today_state['today_state'] = '無'
            today_state['bind_table'] = '工作日'
        else:
            for data in festival_info:
                if str(data.date) == today:
                    today_state['today_state'] = data.statement
                    today_state['bind_table'] = '例假日'
                    return today_state
                else:
                    today_state['today_state'] = '無'
                    today_state['bind_table'] = '工作日'
        # 如無符合假日情形
        db.session.commit()
        db.session.close()
        return today_state
    elif role == "Cloud":
        message = json.dumps({})
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "schedule_setting/today_state", message)
        response = mqtt_talker.start()
        if response:
            return response


@api.route('/schedule_setting/prev_next_control_time', methods=['POST', 'GET'])
def control_time_initset_setting():
    current_time = datetime.datetime.now()
    current_date = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S").split()[0]
    compare_time = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S").split()[1]
    controltime = ""
    next_controltime = ""
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    if role == "Gateway":
         # 判斷是工作日還是例假日，取得今日狀態
        sun = db.session.query(Gateway).all()
        for data in sun:
            sunrise = datetime.datetime.strptime(
                str(data.sunrise), "%H:%M:%S").strftime("%H:%M:%S")
            sunset = datetime.datetime.strptime(
                str(data.sunset), "%H:%M:%S").strftime("%H:%M:%S")
        today_state = {}
        today_state = today_check(current_date, gateway_uid)
        bind_table = transformdate(today_state)
        state = {}
        # 存取該天的控制時間
        current_timeInfo = db.session.query(Schedule.control_time, Schedule.control_time_of_sun).filter(Schedule.schedule_table == bind_table).distinct(
            Schedule.control_time, Schedule.control_time_of_sun).group_by(Schedule.control_time, Schedule.control_time_of_sun)
        # 如果無控制時間設定
        current_info = []
        date_info = []
        for_sort = []
        # 如果今天沒有控制時間*****************************
        if current_timeInfo.count() == 0:
            temp_time = datetime.datetime.now()
            # 檢查其他日子時間
            next_controltime = check_other_controltime(
                temp_time, '+', gateway_uid)
            controltime = check_other_controltime(temp_time, '-', gateway_uid)
            state['state'] = "ok"
            db.session.close()
            return jsonify(state, controltime, next_controltime), 201
        else:
            for data in current_timeInfo:
                if data.control_time is None:
                    if data.control_time_of_sun == 'sunrise':
                        input_start_time = sunrise
                    else:
                        input_start_time = sunset
                else:
                    input_start_time = datetime.datetime.strptime(
                        str(data.control_time), "%H:%M:%S").strftime("%H:%M:%S")

                date_info.append({
                    'control_time': input_start_time,
                })
            while len(current_info) < len(date_info):
                for_index = 0
                for_check = 100
                to_compare = datetime.datetime.strptime(
                    "23:59:59", "%H:%M:%S").strftime("%H:%M:%S")
                while for_index < len(date_info):
                    if for_index not in for_sort:
                        if date_info[for_index]['control_time'] <= to_compare:
                            to_compare = date_info[for_index]['control_time']
                            for_check = for_index
                    for_index = for_index + 1
                for_sort.append(for_check)
                current_info.append(date_info[for_check])
            temp_time = datetime.datetime.now()
            if compare_time < current_info[0]['control_time']:
                controltime = check_other_controltime(
                    temp_time, '-', gateway_uid)
                next_controltime = {
                    'control_time': current_info[0]['control_time'],
                    'weekday': current_time.weekday(),
                    'date': current_date
                }
                state['state'] = "ok"
                db.session.commit()
                db.session.close()
                return jsonify(state, controltime, next_controltime), 201
            elif compare_time >= current_info[len(current_info) - 1]['control_time']:
                controltime = {
                    'control_time': current_info[len(current_info) - 1]['control_time'],
                    'weekday': current_time.weekday(),
                    'date': current_date
                }
                next_controltime = check_other_controltime(
                    temp_time, '+', gateway_uid)
                state['state'] = "ok"
                db.session.commit()
                db.session.close()
                return jsonify(state, controltime, next_controltime), 201
            else:
                for_index = 0
                while(for_index < len(current_info)):
                    if current_info[for_index]['control_time'] <= compare_time and compare_time < current_info[for_index + 1]['control_time']:
                        break
                    for_index = for_index + 1
                controltime = {
                    'control_time': current_info[for_index]['control_time'],
                    'weekday': current_time.weekday(),
                    'date': current_date
                }
                next_controltime = {
                    'control_time': current_info[for_index + 1]['control_time'],
                    'weekday': current_time.weekday(),
                    'date': current_date
                }
                state['state'] = "ok"
                db.session.commit()
                db.session.close()
                return jsonify(state, controltime, next_controltime), 201
    elif role == "Cloud":
        message = json.dumps({})
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "schedule_setting/prev_next_control_time", message)
        response = mqtt_talker.start()
        if response:
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


def check_other_controltime(temp_time, search, gateway_uid):
    controltime = ""
    count = 0
    date_state = {}
    sun = db.session.query(Gateway).all()
    for data in sun:
        sunrise = datetime.datetime.strptime(
            str(data.sunrise), "%H:%M:%S").strftime("%H:%M:%S")
        sunset = datetime.datetime.strptime(
            str(data.sunset), "%H:%M:%S").strftime("%H:%M:%S")
    while(count != 7):
        if(search == "+"):
            temp_time = (temp_time + timedelta(days=1))
        else:
            temp_time = (temp_time - timedelta(days=1))

        date_state = today_check(temp_time.strftime("%Y-%m-%d"), gateway_uid)
        table = transformdate(date_state)
        date_data = db.session.query(Schedule.control_time, Schedule.control_time_of_sun).filter(Schedule.schedule_table == table).distinct(
            Schedule.control_time, Schedule.control_time_of_sun).group_by(Schedule.control_time, Schedule.control_time_of_sun).all()
        if len(date_data) != 0:
            date_info = []
            date_current_info = []
            for_sort = []
            for data in date_data:
                if data.control_time is None:
                    if data.control_time_of_sun == 'sunrise':
                        input_control_time = sunrise
                    else:
                        input_control_time = sunset
                else:
                    input_control_time = datetime.datetime.strptime(
                        str(data.control_time), "%H:%M:%S").strftime("%H:%M:%S")

                date_info.append({
                    'control_time': input_control_time,
                })
            while len(date_current_info) < len(date_info):
                for_index = 0
                for_check = 100
                to_compare = datetime.datetime.strptime(
                    "23:59:59", "%H:%M:%S").strftime("%H:%M:%S")
                while for_index < len(date_info):
                    if for_index not in for_sort:
                        if date_info[for_index]['control_time'] <= to_compare:
                            to_compare = date_info[for_index]['control_time']
                            for_check = for_index
                    for_index = for_index + 1
                for_sort.append(for_check)
                date_current_info.append(date_info[for_check])
            temp_date = datetime.datetime.strftime(
                temp_time, "%Y-%m-%d %H:%M:%S").split()[0]
            if(search == "+"):
                controltime = {
                    'control_time': date_current_info[0]['control_time'],
                    'weekday': temp_time.weekday(),
                    'date': temp_date
                }
                return (controltime)
            else:
                controltime = {
                    'control_time': date_current_info[len(date_current_info) - 1]['control_time'],
                    'weekday': temp_time.weekday(),
                    'date': temp_date
                }
                return (controltime)
        else:
            if(search == "+"):
                controltime = {
                    'control_time': "後七天無設定",
                    'weekday': "",
                    'date': ""
                }
            if(search == "-"):
                controltime = {
                    'control_time': "前七天無設定",
                    'weekday': "",
                    'date': ""
                }
        count += 1
    return (controltime)


def transformdate(today_state):
    bind_table = ""
    if(today_state['bind_table'] == "工作日"):
        bind_table = "weekday"
    else:
        bind_table = "holiday"
    return bind_table
