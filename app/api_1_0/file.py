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
from .resident.method import group as switch
from .resident.method.config.cloud_setting import *
from .resident.method.config.gateway_setting import *


# 進階設定，檔案匯出


@api.route('/file/export', methods=['POST', 'GET'])
def file_export():
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    length = request.args.get('file_length', default="", type=str)
    file_list = []
    state = {}
    # 取得要匯出的TABLE名稱
    for i in range(0, int(length)):
        file_list.append(request.args.get(
            'file_export_list[' + str(i) + ']', default="", type=str))
    if role == "Gateway":
        final_output = {}
        for table in file_list:
            final_output = transfer_json(table, final_output)
        state['state'] = 'ok'
        db.session.commit()
        db.session.close()
        return jsonify(final_output, state), 201
    elif role == "Cloud":
        message = json.dumps({
            'file_list': file_list
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "file/export", message)
        response = mqtt_talker.start()
        if response:
            log_info(gateway_uid, "export", "file_export", str(
                message), json.loads(response)[1]['state'], "Cloud")
            return jsonify(response), 201
        else:
            return "Request Timeout", 500

# 內容轉換成json檔並儲存


def transfer_json(table, final_output):
    # 初始化檔案格式
    final_output[table] = []
    if table == "Schedule":
        for data in db.session.query(Schedule).all():
            final_output[table].append(data.Schedule_to_json())
    if table == "festival":
        for data in db.session.query(festival).all():
            final_output[table].append(data.festival_to_json())
    if table == "Node":
        for data in db.session.query(Node).all():
            final_output[table].append(data.Node_to_json())
    if table == "Group":
        for data in db.session.query(Group).all():
            final_output[table].append(data.Group_to_json())
    if table == "Scenes":
        for data in db.session.query(Scenes).all():
            final_output[table].append(data.Scenes_to_json())
    if table == "Setting":
        for data in db.session.query(Setting).all():
            final_output[table].append(data.Setting_to_json())
    return final_output
# 進階設定，檔案匯入


@api.route('/file/upload', methods=['POST', 'GET'])
def file_upload():
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    file_data = request.args.get('file_data', default="", type=str)
    file_table_group = ['Group', 'Scenes']
    file_table = ['Schedule', 'festival', 'Node', 'Scenes', 'Setting', 'Group']
    state = {}
    # 讀檔
    if role == "Gateway":
        content = json.loads(file_data)
        if 'Group' in content.keys():
            insert_file(gateway_uid, 'Group', content)
        for data_table in content:
            if data_table not in file_table:
                state['state'] = 'file_error'
                log_info(gateway_uid, "import", "file import ", str(
                    content).replace('\\n', ''), "file_error", "Cloud")
                db.session.commit()
                db.session.close()
                return jsonify(state), 201
            elif data_table not in file_table_group:
                insert_file(gateway_uid, data_table, content)
                state['state'] = 'ok'
        if 'Group' in content.keys():
            db.session.commit()
            for data in content['Group']:
                switch.set_group(data['id'])
                group_data = []
                group_data.append({
                    'id': data["id"],
                    'group_num': data["group_num"],
                    'group_name': data["group_name"],
                    'group_state': data["group_state"]
                })
                message = json.dumps(group_data)
                mqtt_talker = mqtttalker_client.MqttTalker(
                    mqtt_host, gateway_uid, "group/insert", message)
                response = mqtt_talker.start()
        if 'Scenes' in content.keys():
            insert_file(gateway_uid, 'Scenes', content)
        log_info(gateway_uid, "import", "file import ", str(
            content).replace('\\n', ''), "ok", "Cloud")
        state['state'] = "ok"
        db.session.commit()
        db.session.close()
        return jsonify(state), 201
    elif role == "Cloud":
        message = json.dumps({
            'file_data': file_data
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "file/upload", message)
        response = mqtt_talker.start()
        if response:
            log_info(gateway_uid, "import", "file", str(message).replace(
                '\\n', ''), json.loads(response)['state'], "Cloud")
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


def insert_file(gateway_uid, table, content):
    for_log = ""
    if table == "Schedule":
        for data in content[table]:
            insert_data = Schedule(data['id'], data['schedule_table'], data['group_id'],
                                   data['schedule_group_state'], data['control_time'], data['control_time_of_sun'], data['setting'])
            db.session.add(insert_data)
            sql = "INSERT INTO schedule(id,schedule_table,group_id, schedule_group_state, control_time,control_time_of_sun,setting)VALUES('%s','%s','%s','%s','%s','%s','%s')" % (
                data['id'], data['schedule_table'], data['group_id'], data['schedule_group_state'], data['control_time'], data['control_time_of_sun'], data['setting'])
            for_log = for_log + "\n" + sql
    if table == "festival":
        for data in content[table]:
            insert_data = festival(
                data['id'], data['date'], data['statement'], data['bind_table'])
            db.session.add(insert_data)
            sql = "INSERT INTO festival(id,`date`,statement,bind_table)VALUES('%s','%s','%s','%s')" % (
                data['id'], data['date'], data['statement'], data['bind_table'])
            for_log = for_log + "\n" + sql
    if table == "Node":
        for data in content[table]:
            insert_data = Node(data['id'], data['gateway'], data['model'], data['node_name'], data['node'], data['gateway_address'],
                               data['created_at'], data['updated_at'], data['model_type'], data['node_state'], data['group_id'])
            db.session.add(insert_data)
            sql = "INSERT INTO node(id,gateway,model,node_name,node,gateway_address,created_at,updated_at,model_type,node_state,group_id)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                data['id'], data['gateway'], data['model'], data['node_name'], data['node'], data['gateway_address'], data['created_at'], data['updated_at'], data['model_type'], data['node_state'], data['group_id'])
            for_log = for_log + "\n" + sql
            node_data = []
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
            mqtt_talker = mqtttalker_client.MqttTalker(
                mqtt_host, gateway_uid, "node/insert", message)
            response = mqtt_talker.start()
    if table == "Group":
        for data in content[table]:
            insert_data = Group(data['id'], data['group_num'], data['group_name'],
                                data['group_state'], data['created_at'], data['updated_at'])
            db.session.add(insert_data)
            sql = "INSERT INTO `group`(id,group_num,group_name,group_state,created_at,updated_at)VALUES('%s','%s','%s','%s','%s','%s')" % (
                data['id'], data['group_num'], data['group_name'], data['group_state'], data['created_at'], data['updated_at'])
            for_log = for_log + "\n" + sql

    if table == "Scenes":
        for data in content[table]:
            insert_data = Scenes(data['id'], data['node'], data['node_state'], data['scene_name'], data['scene_number'], data['created_at'],
                                 data['updated_at'])
            db.session.add(insert_data)
            sql = "INSERT INTO scenes(id,node,node_state,scene_name,scene_number,created_at,updated_at)VALUES('%s','%s','%s','%s','%s','%s','%s')" % (
                data['id'], data['node'], data['node_state'], data['scene_name'], data['scene_number'], data['created_at'], data['updated_at'])
            for_log = for_log + "\n" + sql
    if table == "Setting":
        for data in content[table]:
            insert_data = Setting(data['id'], data['model'], data['address'], data['ch'], data['speed'], data['circuit'],
                                  data['pt'], data['ct'], data['meter_type'], data['created_at'], data['updated_at'], data['gateway_uid'])
            db.session.add(insert_data)
            sql = "INSERT INTO setting(id,model,address,ch,speed,circuit,pt,ct,meter_type,created_at,updated_at,gateway_uid)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                data['id'], data['model'], data['address'], data['ch'], data['speed'], data['circuit'], data['pt'], data['ct'], data['meter_type'], data['created_at'], data['updated_at'], data['gateway_uid'])
            for_log = for_log + "\n" + sql
    log_info(gateway_uid, "insert", "file", for_log, "ok", "Gateway")
    if table == "Scenes":
        db.session.commit()
        for_get_distinct_scene = []
        for data in content[table]:
            if data['scene_number'] not in for_get_distinct_scene:
                for_get_distinct_scene.append(data['scene_number'])
                switch.set_scene(int(data['scene_number']))
                node_data = []
                node_data.append({
                    'scene_name': data["scene_name"],
                    'scene_number': data["scene_number"]
                })
                message = json.dumps(node_data)
                mqtt_talker = mqtttalker_client.MqttTalker(mqtt_host, gateway_uid, "scene/insert", message)
                response = mqtt_talker.start()
    if table == "festival" or table == "Schedule":
        db.session.commit()
        cflag.cflag()
