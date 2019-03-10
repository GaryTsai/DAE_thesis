from flask import jsonify, request
from sqlalchemy import func, and_, or_, between, exists
from . import api
from .. import db
from config import role
from ..models import *
from . import mqtttalker
from config import role
from .log import log_info
import datetime
import json
from .resident.method.config.cloud_setting import *


@api.route('/project/query', methods=['POST', 'GET'])
def project_initset():
    req_account = request.args.get('account', default="dae", type=str)
    project_data = db.session.query(Project.project_name, Project.id).filter(
        Project.account == req_account).all()
    db.session.close()
    project_info = []
    for data in project_data:
        project_info.append(
            {'project_name': data.project_name, 'project_id': data.id})

    return jsonify(project_info), 201


@api.route('/project/delete', methods=['POST', 'GET'])
def project_delete():
    req_p_id = request.args.get('p_id', default="dae", type=str)
    state = {}
    db.session.query(Project).filter(Project.id == req_p_id).delete()
    db.session.query(Project).filter(Project.id == req_p_id).delete()
    db.session.commit()
    db.session.close()
    state['status'] = "ok"
    log_info(None, "delete",  "project", "project_id: " +
             str(req_p_id), "ok", "Cloud")
    return jsonify(state), 201


@api.route('/project/insert', methods=['POST', 'GET'])
def project_insert():
    project_name = request.args.get('project_name', default="dae", type=str)
    account = request.args.get('account', default="dae", type=str)
    state = {}

    if db.session.query(Project).filter(and_(Project.project_name == project_name,  Project.account == account)).first():
        state['status'] = "repeat"
        db.session.close()
        return jsonify(state), 201
    else:
        insert_data = Project(None, project_name, account)
        db.session.add(insert_data)
        db.session.commit()
        project_data = db.session.query(Project).filter(
            and_(Project.project_name == project_name,  Project.account == account)).first()
        db.session.close()

    state['status'] = "ok"
    state['project_id'] = project_data.id
    state['project_name'] = project_data.project_name

    log_info(None, "insert", "project", "account: " + account +
             "\nproject_name: " + str(project_data), "ok", "Cloud")
    return jsonify(state), 201


@api.route('/project/update', methods=['POST', 'GET'])
def project_update():
    update_project_name = request.args.get(
        'update_project_name', default="dae", type=str)
    p_id = request.args.get('p_id', default="dae", type=str)
    account = request.args.get('account', default="dae", type=str)
    state = {}
    if db.session.query(Project).filter(and_(Project.account == account, Project.project_name == update_project_name)).first():
        state['status'] = "repeat"
        db.session.close()
        return jsonify(state), 201
    else:
        db.session.query(Project).filter(and_(Project.account == account, Project.id == p_id)).update(
            {Project.project_name: update_project_name})
        db.session.commit()
        db.session.close()

    state['status'] = "ok"
    log_info(None, "update", "project", "account: " + account + "p_id" + str(p_id) +
             "\nupdate_project_name: " + str(update_project_name), "ok", "Cloud")
    return jsonify(state), 201


@api.route('/gateway_setting/query', methods=['POST', 'GET'])
def gateway_setting():
    req_p_id = request.args.get('p_id', default="dae", type=str)
    gateway_info = []
    Gateway_data = db.session.query(Gateway).filter(
        Gateway.project_id == req_p_id).all()
    db.session.close()
    for data in Gateway_data:
        gateway_info.append({'gateway_id': data.id, 'uid': data.uid, 'country': data.country,
                             'city': data.city, 'physical_address': data.physical_address, 'gateway_name': data.gateway_name})
    return jsonify(gateway_info), 201


@api.route('/gateway_setting/insert', methods=['POST', 'GET'])
def gateway_insert():
    p_id = request.args.get('p_id', default="dae", type=str)
    gateway_uid = request.args.get('uid', default="dae", type=str)
    name = request.args.get('name', default="dae", type=str)
    country = request.args.get('country', default="dae", type=str)
    city = request.args.get('city', default="dae", type=str)
    physical_address = request.args.get(
        'physical_address', default="dae", type=str)
    # lvami
    lvami_account = request.args.get('lvami_account', default="", type=str)
    authority = request.args.get('authority', default="", type=str)

    state = {}
    Gateway_data = db.session.query(Gateway).filter(or_(
        Gateway.gateway_name == name, Gateway.uid == gateway_uid), Gateway.project_id == p_id).first()
    # lvami data
    print('#121# authority', authority)
    if authority == '0':
        insert_data = Gateway(None, gateway_uid, country,
                              city, physical_address, name, p_id)
        db.session.add(insert_data)
        db.session.commit()
        Gateway_data = db.session.query(Gateway).filter(or_(
            Gateway.gateway_name == name, Gateway.uid == gateway_uid), Gateway.project_id == p_id).first()
        state['gateway_id'] = Gateway_data.id
        state['country'] = Gateway_data.country
        state['city'] = Gateway_data.city
        state['physical_address'] = Gateway_data.physical_address
        state['gateway_name'] = Gateway_data.gateway_name
        state['uid'] = Gateway_data.uid
        sql = "\nINSERT INTO gateway(uid,country,city,physical_address, gateway_name,project_id)VALUES('%s','%s','%s','%s','%s','%s') " % (
            gateway_uid, country, city, physical_address, name, p_id)
        log_info(gateway_uid, "insert",
                 "gateway_setting", sql, "ok", "Cloud")
        state['status'] = "ok"
        db.session.close()
        return jsonify(state), 201
    elif Gateway_data is None:
        message = json.dumps({
            'project_id': p_id,
            'gateway_uid': gateway_uid,
            'name': name,
            'country': country,
            'city': city,
            'physical_address': physical_address,
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "gateway_setting/insert", message)
        response = mqtt_talker.start()
        if json.loads(response['status']) == "ok":
            insert_data = Gateway(None, gateway_uid, country,
                                  city, physical_address, name, p_id)
            db.session.add(insert_data)
            db.session.commit()
            Gateway_data = db.session.query(Gateway).filter(or_(
                Gateway.gateway_name == name, Gateway.uid == gateway_uid), Gateway.project_id == p_id).first()
            state['gateway_id'] = Gateway_data.id
            state['country'] = Gateway_data.country
            state['city'] = Gateway_data.city
            state['physical_address'] = Gateway_data.physical_address
            state['gateway_name'] = Gateway_data.gateway_name
            state['uid'] = Gateway_data.uid
            sql = "\nINSERT INTO gateway(uid,country,city,physical_address, gateway_name,project_id)VALUES('%s','%s','%s','%s','%s','%s') " % (
                gateway_uid, country, city, physical_address, name, p_id)
            log_info(gateway_uid, "insert",
                     "gateway_setting", sql, "ok", "Cloud")
            state['status'] = "ok"
            db.session.close()
            return jsonify(state), 201
        else:
            return "Request Timeout", 500
    else:
        state['status'] = "repeat"
        return jsonify(state), 201


@api.route('/gateway_setting/update', methods=['POST', 'GET'])
def gateway_update():
    gateway_id = request.args.get('id', default="dae", type=str)
    gateway_uid = request.args.get('uid', default="dae", type=str)
    name = request.args.get('name', default="dae", type=str)
    country = request.args.get('country', default="dae", type=str)
    city = request.args.get('city', default="dae", type=str)
    physical_address = request.args.get(
        'physical_address', default="dae", type=str)
    # lvami
    lvami_account = request.args.get('lvami_account', default="", type=str)
    authority = request.args.get('authority', default="", type=str)
    state = {}
    db.session.query(Gateway).filter(Gateway.id == gateway_id).update(
        {Gateway.uid: "", Gateway.country: "", Gateway.city: "", Gateway.physical_address: "", Gateway.gateway_name: ""})
    print('194', lvami_account, authority)
    if authority == "0":
        db.session.query(Gateway).filter(Gateway.id == gateway_id).update(
            {Gateway.uid: gateway_uid, Gateway.country: country, Gateway.city: city, Gateway.physical_address: physical_address, Gateway.gateway_name: name})
        sql = "\nUPDATE gateway SET uid='%s', country='%s', city='%s',physical_address='%s', gateway_name='%s' WHERE id ='%s'" % (
            gateway_uid, country, city, physical_address, name, gateway_id)
        log_info(gateway_uid, "update",
                 "gateway_setting", sql, "ok", "Cloud")
        db.session.commit()
        db.session.close()
        state['status'] = "ok"
        return jsonify(state), 201
    elif db.session.query(Gateway).filter(Gateway.id == gateway_id, or_(Gateway.uid == gateway_uid, Gateway.gateway_name == name)).first():
        state['status'] = "repeat"
        db.session.close()
        return jsonify(state), 201
    else:
        message = json.dumps({
            'gateway_id': gateway_id,
            'gateway_uid': gateway_uid,
            'name': name,
            'country': country,
            'city': city,
            'physical_address': physical_address,
        })
        mqtt_talker = mqtttalker.MqttTalker(
            cloud_mqtt_host, gateway_uid, "gateway_setting/update", message)
        response = mqtt_talker.start()
        print('#232', json.loads(response)[0]['status'])
        if json.loads(response)[0]['status'] == "ok":
            db.session.query(Gateway).filter(Gateway.id == gateway_id).update(
                {Gateway.uid: gateway_uid, Gateway.country: country, Gateway.city: city, Gateway.physical_address: physical_address, Gateway.gateway_name: name})
            sql = "\nUPDATE gateway SET uid='%s', country='%s', city='%s',physical_address='%s', gateway_name='%s' WHERE id ='%s'" % (
                gateway_uid, country, city, physical_address, name, gateway_id)
            log_info(gateway_uid, "update",
                     "gateway_setting", sql, "ok", "Cloud")
            db.session.commit()
            db.session.close()
            state['status'] = "ok"
            print('#232')
            return jsonify(state), 201
        else:
            return "Request Timeout", 500


@api.route('/gateway_setting/delete', methods=['POST', 'GET'])
def gateway_delete():
    gateway_id = request.args.get('gateway_id', default="dae", type=str)
    gateway_uid = request.args.get('gateway_uid', default="dae", type=str)
    state = {}
    db.session.query(Gateway).filter(Gateway.id == gateway_id).delete()
    db.session.commit()
    db.session.close()
    state['status'] = "ok"
    sql = "\nDELETE FROM gateway WHERE id='%s'" % (gateway_id)
    log_info(gateway_uid, "delete", "gateway_setting", sql, "ok", "Cloud")
    return jsonify(state), 201
