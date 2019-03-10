from flask import jsonify, request
from sqlalchemy import func, and_, or_, between, exists
from . import api
from .. import db
from config import role
from ..models import *
from . import mqtttalker
from . import mqtttalker_client
from .log import log_info
from .resident.method import switch as switch
import datetime, time, calendar, json
from datetime import timedelta
from .resident.method.config.cloud_setting import *
from .resident.method.config.gateway_setting import *



@api.route('/query/records', methods=['POST', 'GET'])
def query_records():
    setting_data = db.session.query(Demand).order_by(Demand.id.desc()).limit(50)
    data_output = []
    for data in setting_data:
        data_output.append({'id': data.id,
                            'demand_value': data.demand_quarter,
                            'circuit': data.circuit,
                            'created_at': data.datetime
        })
    return jsonify(data_output), 201


@api.route('/search/record', methods=['POST', 'GET'])
def search_record():
    req_circuit = request.args.get('circuit', default="20", type=str)
    req_date = request.args.get('date', default=datetime.datetime.now().strftime("%Y-%m-%d"), type=str)
    req_dateend = request.args.get('dateend', default=datetime.datetime.now().strftime("%Y-%m-%d"), type=str)

    setting_data = db.session.query(Demand).filter(Demand.circuit == req_circuit, Demand.datetime >= req_date, Demand.datetime <= req_dateend).limit(50)
    data_output = []
    for data in setting_data:
        data_output.append({'id': data.id,
                            'demand_value': data.demand_quarter,
                            'circuit': data.circuit,
                            'created_at': data.datetime})
    return jsonify(data_output), 201


@api.route('/getnew/record', methods=['POST', 'GET'])
def getnew_record():
    req_circuit = request.args.get('circuit', default="5", type=str)
    req_time = datetime.datetime.now()
    tt = req_time - timedelta(seconds=100)
    setting_data = db.session.query(Demand).filter(Demand.circuit == req_circuit, Demand.datetime >=tt, Demand.datetime <= req_time).order_by(Demand.datetime.desc()).limit(1).all()
    data_output = []
    for data in setting_data:
        data_output.append({'id': data.id,
                            'demand_value': data.demand_min,
                            'circuit': data.circuit,
                            'created_at': data.datetime})

    return jsonify(data_output), 201

# storage data from POST data
@api.route('/demand', methods=['POST', 'GET'])
def demand_post():
    print("\n\n", "[*] Receiving POST data from",request.remote_addr, "\n", request.data, "\n\n")
    if request.method == 'POST':
        req_json = json.loads(request.data.decode("utf-8"))
        if isinstance(req_json, list):
            req_json = req_json[0]

        insert_data = Demand(
            None,
            req_json['address'],
            req_json['channel'],
            None,
            req_json['model'],
            req_json['datetime'],
            req_json['demand_min']['value'],
            req_json['demand_quarter']['value'],
            req_json['instantaneous_power'][0]['value'],
            req_json['instantaneous_power'][1]['value'],
            req_json['instantaneous_power'][2]['value'],
            req_json['instantaneous_power'][3]['value'],
            req_json['gateway_uid'])
        db.session.add(insert_data)
        db.session.commit()

    return jsonify({"message": "feedback success"}), 201


# get gatewayid from gateway and store in datebase
@api.route('/gatewayid', methods=['POST', 'GET'])
def gatewayid():
    if request.method == 'POST':
        if request.is_json:
            req_json = request.get_json()
            insert_data = Gatewayid(
                req_json['gatewayid'],
                req_json['created_at'])
            db.session.add(insert_data)
            db.session.commit()
    return jsonify({"message": "feedback success"}), 201

# post all gatewayid to front end


@api.route('/front_gatewayid', methods=['POST', 'GET'])
def front_end_gatewayid():
    req_address = request.args.get('usertoken', default="", type=str)
    req_gatewayid = db.session.query(Gatewayid.gatewayid)
    req_gatewayid_output['gatewayid'] = [data for data in rep_gatewayid]
    return jsonify(req_gatewayid_output), 201


##### MQTT API for settings ########
@api.route('/query/settings', methods=['POST', 'GET'])
def query_boot_settings():
    authority = request.args.get('authority', default="1", type=str)
    if role == "Gateway":
        gateway_uid = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
        setting_data = db.session.query(Setting).all()
        data_output = []
        for data in setting_data:
            data_output.append({'id': data.id,
                                'model': data.model,
                                'address': data.address,
                                'ch': data.ch,
                                'speed': data.speed,
                                'circuit': data.circuit,
                                'pt': data.pt,
                                'ct': data.ct,
                                'meter_type': data.meter_type})

        return jsonify(data_output), 201

    elif role == "Cloud":
        if authority =='0':
            gateway_uid = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
            setting_data = db.session.query(Setting).filter(Setting.gateway_uid==gateway_uid).all()
            data_output = []
            for data in setting_data:
                data_output.append({'id': data.id,
                                    'model': data.model,
                                    'address': data.address,
                                    'ch': data.ch,
                                    'speed': data.speed,
                                    'circuit': data.circuit,
                                    'pt': data.pt,
                                    'ct': data.ct,
                                    'meter_type': data.meter_type})
            return jsonify(data_output), 201
        else:
            global mqtt_host
            gateway_uid = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
            message = json.dumps({})
            mqtt_talker = mqtttalker.MqttTalker(
                cloud_mqtt_host, gateway_uid, "query/settings", message)
            response = mqtt_talker.start()
            print(jsonify(response))
            if response:
                return jsonify(response), 201
            else:
                return "Request Timeout", 500


@api.route('/update/settings', methods=['POST', 'GET'])
def update_boot_settings():
    if role == "Gateway":
        gateway_uid = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
        query_req_address = request.args.get('query_update_address', default="16", type=str)
        query_req_ch = request.args.get('query_update_ch', default="16", type=str)
        req_model = request.args.get('update_model', default="950", type=str)
        req_address = request.args.get('update_address', default="15", type=str)
        req_channel = request.args.get('update_ch', default="15", type=str)
        req_speed = request.args.get('update_speed', default="9600", type=str)
        req_circuit = request.args.get( 'update_circuit', default="20", type=str)
        req_updated_at = request.args.get('updated_at', default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type=str)
        req_pt = request.args.get('update_pt', default="1", type=int)
        req_ct = request.args.get('update_ct', default="320", type=int)
        req_type = request.args.get('update_type', default="main_meter", type=str)
        data_repeat = db.session.query(Setting.ch, Setting.address).filter(and_(Setting.address == req_address, Setting.ch == req_channel)).first()
        data_repeat_circuit = db.session.query(Setting.ch, Setting.address, Setting.circuit).filter(Setting.circuit == req_circuit).first()
        state = {}
        if data_repeat != None and (data_repeat[0] != query_req_ch or data_repeat[1] != query_req_address):
            success['status'] = "repeat"
            log_info(gateway_uid, "update", "setting", None, "repeat", "Gateway")
            return jsonify(success), 201
        elif data_repeat_circuit != None and (data_repeat_circuit[0] != query_req_ch or data_repeat_circuit[1] != query_req_address):
            success['status'] = "circuit_repeat"
            log_info(gateway_uid, "update", "setting",None, "circuit_repeat", "Gateway")
            return jsonify(success), 201
        else:
            db.session.query(Setting).filter(and_(Setting.address == query_req_address, Setting.ch == query_req_ch)).update({Setting.model: req_model, Setting.address: req_address,Setting.updated_at: req_updated_at, Setting.pt: req_pt, Setting.ct: req_ct, Setting.meter_type: req_type})
            sql = "\nUPDATE setting SET model='%s',address='%s',ch='%s',speed='%s',circuit='%s',pt='%s',ct='%s',meter_type='%s',updated_at='%s' WHERE address='%s' AND ch='%s'"%(req_model,req_address,req_channel,req_speed,req_circuit,req_pt,req_ct,req_type,req_updated_at,query_req_address,query_req_ch)
            log_info(gateway_uid, "update", "setting", sql, "ok", "Gateway")
            db.session.commit()
            state['status'] = "ok"
            return jsonify(state), 201
    elif role == "Cloud":
        global mqtt_host
        gateway_uid = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
        req_id = request.args.get('update_id', default="16", type=str)
        req_model = request.args.get('update_model', default="950", type=str)
        req_address = request.args.get('update_address', default="15", type=str)
        req_channel = request.args.get('update_ch', default="15", type=str)
        req_speed = request.args.get('update_speed', default="9600", type=str)
        req_circuit = request.args.get('update_circuit', default="20", type=str)
        req_updated_at = request.args.get('updated_at', default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type=str)
        req_pt = request.args.get('update_pt', default="1", type=int)
        req_ct = request.args.get('update_ct', default="320", type=int)
        req_type = request.args.get('update_type', default="main_meter", type=str)

        message = json.dumps({
            "id": req_id,
            "model": req_model,
            "address": req_address,
            "ch": req_channel,
            "speed": req_speed,
            "circuit": req_circuit,
            "updated_at": req_updated_at,
            "pt": req_pt,
            "ct": req_ct,
            "type": req_type
        })

        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "update/settings", message)
        response = mqtt_talker.start()
        if response:
            log_info(gateway_uid, "update", 'Setting', "gateway_uid: " + gateway_uid + "\nmodel: " + str(req_model) + "\naddress:" + str(req_address) + "\nspeed: " +
                     str(req_speed) + "\ncircuit: " + str(req_circuit) + "\npt: " + str(req_pt) + "\nct: " + str(req_ct) + "\ntype: " + str(req_type), json.loads(response)['status'], 'Cloud')
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/insert/settings', methods=['POST', 'GET'])
def insert_boot_settings():
    if role == "Gateway":
        gateway_uid = request.args.get(
            'gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
        req_model = request.args.get('model', default="950", type=str)
        req_address = request.args.get('address', default="15", type=str)
        req_channel = request.args.get('ch', default="15", type=str)
        req_speed = request.args.get('speed', default="9600", type=str)
        req_circuit = request.args.get('circuit', default="20", type=str)
        req_pt = request.args.get('pt', default="1", type=str)
        req_ct = request.args.get('ct', default="320", type=str)
        req_type = request.args.get('type', default="main_meter", type=str)
        req_created_at = request.args.get('created_at', default=datetime.datetime.now(
        ).strftime("%Y-%m-%d %H:%M:%S"), type=str)
        req_updated_at = request.args.get('updated_at', default=datetime.datetime.now(
        ).strftime("%Y-%m-%d %H:%M:%S"), type=str)
        data_repeat = db.session.query(Setting).filter(
            and_(Setting.ch == req_channel, Setting.address == req_address)).first()
        data_repeat_circuit = db.session.query(Setting).filter(
            Setting.circuit == req_circuit).first()
        success = {}

        if data_repeat != None:
            success["status"] = "repeat"
            log_info(gateway_uid, "insert", "setting",
                     None, "repeat", "Gateway")
            return jsonify(success), 201
        elif data_repeat_circuit != None:
            success["status"] = "circuit_repeat"
            log_info(gateway_uid, "insert", "setting",
                     None, "circuit_repeat", "Gateway")
            return jsonify(success), 201
        else:
            insert_data = Setting(
                None,
                req_model,
                req_address,
                req_channel,
                req_speed,
                req_circuit,
                req_pt,
                req_ct,
                req_type,
                req_created_at,
                req_updated_at,
                gateway_uid)
            db.session.add(insert_data)
            state = "\nINSERT INTO setting(model,address,ch,speed,circuit,pt,ct,meter_type,created_at,updated_at,gateway_uid)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(req_model,req_address,req_channel,req_speed,req_circuit,req_pt,req_ct,req_type,req_created_at,req_updated_at,gateway_uid)
            log_info(gateway_uid, "insert", "setting", state, "ok", "Gateway")
            db.session.commit()
            new_open_setting= db.session.query(Setting).filter(and_(Setting.address==req_address,Setting.ch==req_channel)).first()
            success = {}
            success["status"] = "ok"
            success["id"] = new_open_setting.id
            return jsonify(success), 201
    elif role == "Cloud":
        global mqtt_host
        gateway_uid = request.args.get(
            'gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
        # req_id = request.args.get('id', default="16", type=str)
        req_model = request.args.get('model', default="950", type=str)
        req_address = request.args.get('address', default="15", type=str)
        req_channel = request.args.get('ch', default="15", type=str)
        req_speed = request.args.get('speed', default="9600", type=str)
        req_circuit = request.args.get('circuit', default="20", type=str)
        req_created_at = request.args.get('created_at', default=datetime.datetime.now(
        ).strftime("%Y-%m-%d %H:%M:%S"), type=str)
        req_updated_at = request.args.get('updated_at', default=datetime.datetime.now(
        ).strftime("%Y-%m-%d %H:%M:%S"), type=str)
        req_pt = request.args.get('pt', default="1", type=str)
        req_ct = request.args.get('ct', default="320", type=str)
        req_type = request.args.get('type', default="main_meter", type=str)

        message = json.dumps({
            "model": req_model,
            "address": req_address,
            "ch": req_channel,
            "speed": req_speed,
            "circuit": req_circuit,
            "created_at": req_created_at,
            "updated_at": req_updated_at,
            "pt": req_pt,
            "ct": req_ct,
            "type": req_type
        })
        mqtt_talker =  mqtttalker.MqttTalker(cloud_mqtt_host, gateway_uid, "insert/settings", message)
        response = mqtt_talker.start()
        if response:
            print('#368', response)
            log_info(gateway_uid, "insert", "Setting", "gateway_uid: " + gateway_uid + "model: " +str(req_model + ' ' + req_channel + "/" + req_address), json.loads(response)['status'],'Cloud')
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/delete/settings', methods=['POST', 'GET'])
def delete_boot_settings():
    gateway_uid = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
    req_id = request.args.get('id', default="2", type=str)
    state = {}
    if role == "Gateway":
        db.session.query(Setting).filter(and_(Setting.gateway_uid == gateway_uid, Setting.id == req_id)).delete()
        state['status'] = "ok"
        sql = "\nDELETE FROM setting WHERE id='%s' AND gateway_uid='%s'" % (req_id, gateway_uid)
        log_info(gateway_uid, "delete", "setting", sql, "ok", "Gateway")
        db.session.commit()
        return jsonify(state), 201
    elif role == "Cloud":
        global mqtt_host
        message = json.dumps({"id": req_id})
        mqtt_talker = mqtttalker.MqttTalker(cloud_mqtt_host, gateway_uid, "delete/settings", message)
        response = mqtt_talker.start()
        if response:
            log_info(gateway_uid, "delete", "Setting", "gateway_uid: " +gateway_uid + "\nmeter id: " + str(req_id), json.loads(response)['status'], 'Cloud')

            return jsonify(response), 201
        else:
            return "Request Timeout", 500

##### MQTT API for demand settings ########
@api.route('/query/demand_settings', methods=['POST', 'GET'])
def query_demand_settings():
    if role == "Gateway":
        setting_data = db.session.query(DemandSettings).all()
        data_output = []
        for data in setting_data:
            data_output.append({'value': data.value,
                                'value_max': data.value_max,
                                'value_min': data.value_min,
                                'load_off_gap': data.load_off_gap,
                                'reload_delay': data.reload_delay,
                                'reload_gap': data.reload_gap,
                                'cycle': data.cycle,
                                'mode': data.mode,
                                'created_at': data.created_at,
                                'updated_at': data.updated_at,
                                'group': data.groups})

        return jsonify(data_output), 201
    if role == "Cloud":
        global mqtt_host
        req_gatewayId = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
        message = ""
        message = json.dumps({})
        mqtt_talker = mqtttalker.MqttTalker(cloud_mqtt_host, req_gatewayId, "query/demand_settings", message)
        response = mqtt_talker.start()
        if response:
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/insert/demand_settings', methods=['POST', 'GET'])
def insert_demand_settings():
    gateway_uid = request.args.get('gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
    req_value = request.args.get('value', default=980, type=int)
    req_value_max = request.args.get('value_max', default=950, type=int)
    req_value_min = request.args.get('value_min', default=700, type=int)
    req_load_off_gap = request.args.get('load_off_gap', default=0, type=int)
    req_reload_delay = request.args.get('reload_delay', default=0, type=int)
    req_reload_gap = request.args.get('reload_gap', default=0, type=int)
    req_cycle = request.args.get('cycle', default=15, type=int)
    req_mode = request.args.get('mode', default="u5148", type=str)
    req_group = request.args.get('group', default="u6a21", type=str)
    req_created_at = request.args.get('created_at', default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type=str)
    req_updated_at = request.args.get('created_at', default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), type=str)
    if role == "Gateway":
        db.session.query(DemandSettings).delete()
        db.session.commit()

        data = DemandSettings(
            req_value,
            req_value_max,
            req_value_min,
            req_load_off_gap,
            req_reload_delay,
            req_reload_gap,
            req_cycle,
            req_mode,
            req_group,
            req_created_at,
            req_updated_at)
        db.session.add(data)
        db.session.commit()
        state = "\nTRUNCATE TABLE demand_settings\nINSERT INTO demand_settings(value,value_max,value_min,load_off_gap,reload_delay,reload_gap,cycle,mode,groups,created_at,updated_at)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(req_value,req_value_max,req_value_min,req_load_off_gap,req_reload_delay,req_reload_gap,req_cycle,req_mode,req_group,req_created_at,req_updated_at)
        log_info(gateway_uid, "insert", "demand_settings", state, "ok", "Gateway")
        success = {"status": "ok"}
        return jsonify(success), 201
    if role == "Cloud":
        global mqtt_host
        message = json.dumps({
            "value": req_value,
            "value_max": req_value_max,
            "value_min": req_value_min,
            "load_off_gap": req_load_off_gap,
            "reload_delay": req_reload_delay,
            "reload_gap": req_reload_gap,
            "cycle": req_cycle,
            "mode": req_mode,
            "group": req_group,
            "created_at": req_created_at
        })
        # MQTT
        mqtt_talker = mqtttalker.MqttTalker(cloud_mqtt_host, gateway_uid, "insert/demand_settings", message)
        response = mqtt_talker.start()
        if response:
            log_info(gateway_uid, "insert" ,"demand_settings", "gateway_uid: " + str(gateway_uid) + "\nvalue: " + str(req_value) + "\nvalue_max: " + str(req_value_max) + "\nvalue_min: " + str(req_value_min) + "\nload_off_gap: " +
                     str(req_load_off_gap) + "\nreload_delay: " + str(req_reload_delay) + "\ncycle: " + str(req_cycle) + "\nmode: " + str(req_mode) + "\ngroup: " + str(req_group) + "\ncreated_at: " + str(req_created_at), json.loads(response)['status'], 'Cloud')
            return jsonify(response), 201
        else:
            return "Request Timeout", 500



@api.route('/query/offloads', methods=['POST', 'GET'])
def query_offloads():
    global mqtt_host
    if role == "Gateway":
        setting_data = db.session.query(Offloads).all()
        data_output = []
        for data in setting_data:
            data_output.append({"group":data.group,"available":data.offload_available,"boolean":data.hand_controls})
        return jsonify(data_output), 201
    if role == "Cloud":
        # Get the identification of the device, and the time to check
        req_gatewayId = request.args.get(
            'gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)

        message = ""
        message = json.dumps({})
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, req_gatewayId, "query/offloads", message)
        response = mqtt_talker.start()

        if response:
            print(response)
            return jsonify(response), 201
        else:
            return "Request Timeout", 500
    elif role == "Gateway":
        print('312', 'Gateway')
        return "Gateway Setting", 500


@api.route('/update/offloads', methods=['POST', 'GET'])
def update_offloads():
    global mqtt_host

    gateway_uid = request.args.get(
        'gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
    req_group = request.args.get('group', default=1, type=int)
    req_available = request.args.get('available', default="true", type=str)
    req_boolean = request.args.get('boolean', default="true", type=str)
    req_updated_at = request.args.get('updated_at', default=datetime.datetime.now(
    ).strftime("%Y-%m-%d %H:%M:%S"), type=str)

    if role == "Gateway":
        numgroup = int(req_group) - 1


        if(req_boolean == "true"):
            switch.switch_power(numgroup, 1)
        elif(req_boolean == "false"):
            switch.switch_power(numgroup, 0)
        data_output = []
        data_output.append(
            {"group": req_group, "available": req_available, "boolean": req_boolean})
        message = json.dumps(data_output)
        db.session.query(Offloads).filter(Offloads.group == req_group).update(
                {Offloads.hand_controls:req_boolean,Offloads.offload_available:req_available,Offloads.updated_at:req_updated_at})


        success = {"status": "ok"}
        # new_mqtt_subscribe.update_offload(data_output)
        #update_offload(data_output)
        mqtt_talker = mqtttalker_client.MqttTalker(
            mqtt_host, gateway_uid, "update/offload", message)
        response = mqtt_talker.start()
        state = "\nUPDATE offloads SET hand_controls='%s',offload_available='%s',updated_at='%s' WHERE `group` = '%s'"%(req_boolean,req_available,req_updated_at,req_group)
        log_info(gateway_uid, "update", "offloads", state, "ok", "Gateway")
        # log_info(gateway_uid, "update offloads", "gateway_uid: " + gateway_uid + "\ngroup: " +
        #          str(req_group) + "\navailable: " + req_available + "\nboolean: " + req_boolean)

        return jsonify(success), 201

    if role == "Cloud":

        message = json.dumps({
            "group": req_group,
            "available": req_available,
            "boolean": req_boolean
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "update/offloads", message)
        response = mqtt_talker.start()
        if response:
            log_info(gateway_uid, "update", "offloads", "gateway_uid: " + gateway_uid + "\ngroup: " +str(req_group) + "\navailable: " + req_available + "\nboolean: " + req_boolean, json.loads(response)['status'], "Cloud")
            return jsonify(response), 201
        else:
            return "Request Timeout", 500


@api.route('/insert/offloads', methods=['POST', 'GET'])
def insert_offloads():
    global mqtt_host
    req_gatewayId = request.args.get(
        'gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
    req_group = request.args.get('group', default=1, type=int)

    message = json.dumps({
        "group": req_group,
    })
    mqtt_talker = mqtttalker.MqttTalker(
        cloud_mqtt_host, req_gatewayId, "insert/offloads", message)
    response = mqtt_talker.start()

    if response:
        return jsonify(response), 201
        # log_info(gateway_uid, "insert offloads", "gateway_uid: "+gateway_uid+"\nreq_group: "+req_group)
    else:
        return "Request Timeout", 500


@api.route('/delete/offloads', methods=['POST', 'GET'])
def delete_offloads():
    global mqtt_host
    gateway_uid = request.args.get(
        'gateway_uid', default="09ea6335-d2bd-4678-9ca9-647b5574a09e", type=str)
    req_group = request.args.get('group', default=1, type=int)

    message = json.dumps({"group": req_group})

    mqtt_talker = mqtttalker.MqttTalker(
        cloud_mqtt_host, gateway_uid, "delete/offloads", message)
    response = mqtt_talker.start()

    if response:
        return jsonify(response), 201
    else:
        return "Request Timeout", 500


@api.route('/demand_min')
def demand_min():
    # Get the identification of the device
    req_address = request.args.get('address', default="15", type=str)
    req_channel = request.args.get('channel', default="15", type=str)

    # Try get data of the latest instantaneous power
    power_data = db.session.query(Demand.datetime, Demand.demand_min).filter(
        Demand.address == req_address,
        Demand.channel == req_channel).order_by(Demand.datetime.desc()).first()

    pt_ct_setting = db.session.query(Setting.pt, Setting.ct).filter(
        Demand.address == req_address,
        Demand.channel == req_channel).first()

    # Pack the result
    data_output = {}
    if power_data:
        print(pt_ct_setting.pt,pt_ct_setting.ct)
        data_output['time'] = power_data.datetime.strftime("%Y-%m-%d %H:%M:%S")
        data_output['demand_min'] = "{:0.3f}".format(
            power_data.demand_min * int(pt_ct_setting.pt) * int(pt_ct_setting.ct) / 1000)

    return jsonify(data_output), 201




##### Query for power information ########
@api.route('/peak_period_in_day')
def get_peak_period_in_day():
    '''
    Get the peak period in one specific day, and return all real-time power
    data captured during a total of three periods, which is the peak period
    and the periods before and after it.
    '''
    # Get the identification of the device, and the time to check
    req_address = request.args.get('address', default="15", type=str)
    req_channel = request.args.get('channel', default="15", type=str)
    req_datetime = request.args.get('datetime', default=datetime.datetime(2017, 6, 8).strftime("%Y-%m-%d"),
                                    type=str)
    req_interval = get_interval_of_day(req_datetime)

    pt_ct_setting = db.session.query(Setting.pt, Setting.ct).filter(
        Demand.address == req_address,
        Demand.channel == req_channel).first()
    # Try get data of the latest instantaneous power
    power_data = db.session.query(Demand.datetime, Demand.demand_quarter).filter(
        Demand.address == req_address,
        Demand.channel == req_channel,
        or_(
            func.MINUTE(Demand.datetime) == 0,
            func.MINUTE(Demand.datetime) == 15,
            func.MINUTE(Demand.datetime) == 30,
            func.MINUTE(Demand.datetime) == 45,
            func.MINUTE(Demand.datetime) == 60),
        func.SECOND(Demand.datetime) == 0,
        Demand.datetime.between(*req_interval)).order_by(Demand.demand_quarter.desc()).first()

    data_output = {}
    final_data_output = {}
    if power_data:
        data_output['time'] = power_data.datetime.strftime("%Y-%m-%d %H:%M:%S")
        data_output['peak_demand'] = power_data.demand_quarter * \
            int(pt_ct_setting.pt) * int(pt_ct_setting.ct) / 1000
    final_data_output['peak'] = data_output
    date = power_data.datetime

    interval_start = date - timedelta(minutes=30)
    interval_end = date + timedelta(minutes=15)

    interval_power_data = db.session.query(Demand.datetime, Demand.Total_value).filter(
        Demand.address == req_address,
        Demand.channel == req_channel,
        Demand.datetime.between(interval_start, interval_end))

    # Pack the result
    linecolor = ["#b7e021", "#e26f6f", "#2498d2"]
    final_data_output['demands'] = []
    for data in interval_power_data:
        index_color = 1
        if data.datetime >= date:
            index_color = 2
        elif (date - data.datetime).seconds > 900:
            index_color = 0
        final_data_output['demands'].append({'time': data.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                             'Value': data.Total_value * int(pt_ct_setting.pt) * int(pt_ct_setting.ct),
                                             'lineColor': linecolor[index_color]})
    return jsonify(final_data_output), 201


@api.route('/peak_period_everyday_in_month')
def get_peak_period_everyday_in_month():
    '''
    Get the daily peak periods in the month which is same as the date
    specified.
    '''
    req_address = request.args.get('address', default="1", type=str)
    req_channel = request.args.get('channel', default="1", type=str)
    req_datetime = request.args.get('datetime',default=datetime.datetime.now().strftime("%Y-%m-%d"),type=str)
    req_interval = get_interval_of_month(req_datetime)
    power_data = []
    data_output = []
    date = req_interval[0]
    data_output_top = []

    pt_ct_setting = db.session.query(Setting.pt, Setting.ct).filter(
        Demand.address == req_address,
        Demand.channel == req_channel).first()

    # Try get data of the latest instantaneous power
    for i in range(req_interval[0].day, req_interval[1].day + 1):
        interval_start = req_interval[0] + timedelta(hours=24 * i - 24)
        interval_end = req_interval[0] + timedelta(hours=24 * i)
        power_data = db.session.query(Demand.datetime, Demand.demand_quarter).filter(
            Demand.address == req_address,
            Demand.channel == req_channel,
            or_(
                func.MINUTE(Demand.datetime) == 0,
                func.MINUTE(Demand.datetime) == 15,
                func.MINUTE(Demand.datetime) == 30,
                func.MINUTE(Demand.datetime) == 45,
                func.MINUTE(Demand.datetime) == 60),
            func.SECOND(Demand.datetime) == 0,
            Demand.datetime.between(interval_start, interval_end)).order_by(Demand.demand_quarter.desc()).first()

    # Pack the result
        if(power_data):
            data_output.append({'time': power_data.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                'peak_demand': power_data.demand_quarter * int(pt_ct_setting.pt) * int(pt_ct_setting.ct) / 1000})
    data_output_top = sorted(
        data_output, key=lambda datum: datum['peak_demand'], reverse=True)
    i = 1
    for data in data_output_top[:3]:
        data['label'] = "第{}高".format(i)
        i += 1
    # Formatting value to first decimal point
    for data in data_output:
        data['peak_demand'] = "{:0.3f}".format(data['peak_demand'])

    return jsonify(data_output), 201


@api.route('/peak_periods_in_month')
def get_peak_periods_in_month():
    '''
    Get the daily peak periods in the month which is the same as the date
    specified, and return the top three daily peak periods.
    '''
    # Get the identification of the device, and the time to check
    req_address = request.args.get('address', default="15", type=str)
    req_channel = request.args.get('channel', default="15", type=str)
    req_datetime = request.args.get('datetime',
                                    default=datetime.datetime.now().strftime("%Y-%m-%d"),
                                    type=str)

    req_interval = get_interval_of_month(req_datetime)
    power_data = []
    data_output = []
    date = req_interval[0]

    # Try get data of the latest instantaneous power
    for i in range(req_interval[0].day, req_interval[1].day + 1):
        interval_start = req_interval[0] + timedelta(hours=24 * i - 24)
        interval_end = req_interval[0] + timedelta(hours=24 * i)

        power_data = db.session.query(Demand.datetime, Demand.demand_quarter).filter(
            Demand.address == req_address,
            Demand.channel == req_channel,
            or_(
                func.MINUTE(Demand.datetime) == 0,
                func.MINUTE(Demand.datetime) == 15,
                func.MINUTE(Demand.datetime) == 30,
                func.MINUTE(Demand.datetime) == 45,
                func.MINUTE(Demand.datetime) == 60),
            func.SECOND(Demand.datetime) == 0,
            Demand.datetime.between(
                interval_start, interval_end)).order_by(Demand.demand_quarter.desc()).first()

        # Pack the result
        if(power_data):
            data_output.append({'time': power_data.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                'peak_demand': power_data.demand_quarter})

    data_output = sorted(
        data_output, key=lambda datum: int(datum['peak_demand']), reverse=True)

    data_output = sorted(
        data_output[:3], key=lambda datum: datum['time'])

    return jsonify(data_output), 201


@api.route('/peak_periods_in_month_interval')
def get_peak_periods_in_month_interval():
    '''
    Get the daily peak periods in the month which isthe same as the date
    specified, and return the top three daily peak periods, and for each one,
    also the real-time power data captured during a total of three periods,
    the peak period and the periods before and after it.
    '''
    # Get the identification of the device, and the time to check
    req_address = request.args.get('address', default="15", type=str)
    req_channel = request.args.get('channel', default="15", type=str)
    req_datetime = request.args.get('datetime',
                                    default="2017-06-01")

    req_interval = get_interval_of_month(req_datetime)
    daily_peaks = []
    date = req_interval[0]
    # Try get data of the latest instantaneous power
    for i in range(req_interval[0].day, req_interval[1].day + 1):
        interval_start = req_interval[0] + timedelta(hours=24 * i - 24)
        interval_end = req_interval[0] + timedelta(hours=24 * i)

        power_data = db.session.query(Demand.datetime, Demand.demand_quarter).filter(
            Demand.address == req_address,
            Demand.channel == req_channel,
            func.DAY(Demand.datetime) == interval_start.day,
            or_(
                func.MINUTE(Demand.datetime) == 0,
                func.MINUTE(Demand.datetime) == 15,
                func.MINUTE(Demand.datetime) == 30,
                func.MINUTE(Demand.datetime) == 45,
                func.MINUTE(Demand.datetime) == 60),
            func.SECOND(Demand.datetime) == 0,
            Demand.datetime.between(
                interval_start, interval_end)).order_by(Demand.demand_quarter.desc()).first()

        # Pack the result
        if power_data:
            daily_peaks.append({'time': power_data.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                                'peak_demand': power_data.demand_quarter})

    daily_peaks = sorted(
        daily_peaks, key=lambda datum: int(datum['peak_demand']), reverse=True)

    daily_peaks = sorted(
        daily_peaks[:3], key=lambda datum: datum['time'])

    data_output = []
    linecolor = ["#b7e021", "#e26f6f", "#2498d2"]

    for peak in daily_peaks:
        date = datetime.datetime.strptime(peak['time'], '%Y-%m-%d %H:%M:%S')

        interval_start = date - timedelta(minutes=30)
        interval_end = date + timedelta(minutes=15)

        interval_power_data = db.session.query(Demand.datetime, Demand.Total_value).filter(
            Demand.address == req_address,
            Demand.channel == req_channel,
            Demand.datetime.between(interval_start, interval_end))

        temp_data = {}
        temp_data['peak'] = peak
        temp_data['demands'] = []
        for data in interval_power_data:
            temp_data['demands'].append(
                {'time': data.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                 'Value': data.Total_value})
        data_output.append(temp_data)
        for data in data_output[:3]:
            i = 0
            for d in data['demands'][:-1:90]:
                d['lineColor'] = linecolor[i]
                i += 1

    data_output = sorted(
        data_output, key=lambda datum: datum['peak']['time'])

    return jsonify(data_output), 201


@api.route('/real_contronl_group/retrieve', methods=['POST', 'GET'])
def real_control_group_retrieve():
    model_data = db.session.query(Setting.model, Setting.ch, Setting.address).all()
    model_data_dict = []
    for idx in model_data:
        model_data_dict.append(
            {'model': idx[0], 'ch': idx[1], 'address': idx[2]})
    return jsonify(model_data_dict), 201


def get_interval_of_day(today):
    today = datetime.datetime.strptime(today, '%Y-%m-%d')

    return (datetime.datetime.combine(today, datetime.time.min),
            datetime.datetime.combine(today, datetime.time.max))


def get_interval_of_month(today):
    today = datetime.datetime.strptime(today, '%Y-%m-%d')
    _, last_day_num = calendar.monthrange(today.year, today.month)
    first_date = datetime.date(today.year, today.month, 1)
    last_date = datetime.date(today.year, today.month, last_day_num)

    return (datetime.datetime.combine(first_date, datetime.time.min),
            datetime.datetime.combine(last_date, datetime.time.max))
