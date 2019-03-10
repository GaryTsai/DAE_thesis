import json
from . import mysql as daesql
from .config import database_setting as dbconfig
from .config import gateway_setting as gateway_setting
import sys, os, time, signal
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from datetime import datetime, timedelta
import json
from base64 import  encodestring

this_gateway_uid = gateway_setting.uid
mqtt_host = gateway_setting.mqtt_host

def update_node(update_id):
    try:
        dbh = daesql.MySQL(dbconfig.mysql_config)
        node_data=[]
        for data in update_id:
            sql="SELECT * FROM node WHERE id='%s'"%(data)
            results =dbh.query(sql)
            for data in results:
                node_data.append({
                    'id': data["id"],
                    'gateway': data["gateway"],
                    'gateway_address': data["gateway_address"],
                    'model': data["model"],
                    'node_name': data["node_name"],
                    'node': data["node"],
                    # 'group_num': data.group_num,
                    'group_id': data["group_id"],
                    'created_at': data["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    'updated_at': data["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    'model_type': data["model_type"],
                    'node_state': data["node_state"]
                })
        dbh.close
        message =json.dumps(node_data)
        publish.single("{}/client_response/{}".format(this_gateway_uid, "node/update"), message, qos=2, hostname=mqtt_host)
    except BaseException as n:
        print (n)


def update_group(update_id):
    try:
        dbh = daesql.MySQL(dbconfig.mysql_config)
        sql="SELECT * FROM `group` WHERE id='%s'"%(update_id)
        results=dbh.query(sql)
        group_data = []
        for data in results:
            group_data.append({
                'id':update_id,
                'group_num':data["group_num"],
                'group_name':data["group_name"],
                'group_state':data["group_state"]
            })
        dbh.close
        message =json.dumps(group_data)
        publish.single("{}/client_response/{}".format(this_gateway_uid, "group/update"), message, qos=2, hostname=mqtt_host)
    except BaseException as n:
        print (n)
