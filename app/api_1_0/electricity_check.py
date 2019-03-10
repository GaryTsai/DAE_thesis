from flask import jsonify, request
from . import api
import datetime
import json
import requests
from sqlalchemy import func, and_, or_, between, exists
# from .. import db
# from ..models import *
import pymysql
import ctypes
import sys
import math
import time
import numpy
# import scipy.stats as stats
from datetime import timedelta
from .database import db

totalkwh = 0


@api.route('/data_co2', methods=['GET'])
def post_request_co2():
    conn = db.getConnection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # 用戶帳號與讀取資料區段
    req_customerID = request.args.get('CustomerID', default="D00001", type=str)
    authority = request.args.get('authority', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)

    '''
    req_dateTo = datetime.datetime.now()
    # time_range = datetime.timedelta(days = 60)#可調整時間長度
    # req_dateFrom = datetime.datetime.now()-time_range
    req_dateFrom = datetime.datetime.now().replace(
        day=1, hour=0, minute=15, second=0, microsecond=0)
    '''
    if authority == '0':
        req_dateTo = datetime.datetime.now().replace(year=2017, month=12, day=31,
                                                     hour=23, minute=45, second=0, microsecond=0)
        # time_range = datetime.timedelta(days = 60)#可調整時間長度
        # req_dateFrom = datetime.datetime.now()-time_range
        req_dateFrom = datetime.datetime.now().replace(year=2017, month=12, day=1,
                                                       hour=0, minute=15, second=0, microsecond=0)
        electricity_table = 'electricity_information'
        cur.execute("select datetime,value from {} where user_id = '{}'  and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
            electricity_table, req_customerID.lower(), req_dateFrom, req_dateTo))
        result = cur.fetchall()
        totalkwh = 0
        i = 0
        while i < len(result):
            totalkwh += result[i]['value']
            i += 1
        # co2 = 0.529*totalkwh
        power_co2 = []
        power_co2.append(
            {'sum_power': totalkwh, 'day_percent': (96 / 2880)if result != 0 else 0})

        return jsonify(power_co2), 201
    else:
        current_time = datetime.datetime.now()
        year, month = current_time.year, current_time.month
        req_dateFrom = datetime.datetime.now().replace(year=year, month=6, day=1,
                                                       hour=0, minute=15, second=0, microsecond=0)
        if month == 12:
            month = 1
        else:
            month += 1
        req_dateTo = datetime.datetime.now().replace(year=year, month=7, day=1,
                                                     hour=0, minute=15, second=0, microsecond=0)
        electricity_table = 'demand'
        # 先找出gateway的
        sql = "select datetime,demand_quarter from {} where gateway_uid='{}' and address='{}'and channel='{}' and datetime >='{}' and datetime <='{}'and  SECOND(datetime)=0 and  MOD(MINUTE(datetime),15)=0 ORDER BY datetime ASC".format(
            "demand",  gateway_uid, '1', '1', req_dateFrom, req_dateTo)
        cur.execute(sql)
        result = cur.fetchall()

        i = 0
        totalkwh = 0
        while i < len(result):
            totalkwh += result[i]['demand_quarter'] / 1000
            i += 1
        # co2 = 0.529*totalkwh
        power_co2 = []
        power_co2.append(
            {'sum_power': totalkwh, 'day_percent': (96 / 2880)if result != 0 else 0})

        return jsonify(power_co2), 201


@api.route('/rank_user', methods=['GET'])
def rank_user():
    conn = db.getConnection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # req_dateFrom = request.args.get('DateFrom', default="", type=str)
    # req_d
    # ateTo = request.args.get('DateTo', default="", type=str)
    req_customerID = request.args.get('CustomerID', default="D00001", type=str).encode("utf-8").decode("latin1")
    authority = request.args.get('authority', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)


    '''
    req_dateTo = datetime.datetime.now()
    # time_range = datetime.timedelta(days = 60)#可調整時間長度
    # req_dateFrom = datetime.datetime.now()-time_range
    req_dateFrom = datetime.datetime.now().replace(
        day=1, hour=0, minute=15, second=0, microsecond=0)
    '''
    if authority == "1":
        sum_power = 0
        power = 0
        current_time = datetime.datetime.now()
        year, month = current_time.year, current_time.month
        req_dateFrom = datetime.datetime.now().replace(year=year, month=6, day=1,
                                                       hour=0, minute=15, second=0, microsecond=0)
        if month == 12:
            month = 1
        else:
            month += 1
        req_dateTo = datetime.datetime.now().replace(year=year, month=7, day=1,
                                                     hour=0, minute=15, second=0, microsecond=0)
        electricity_table = 'demand'
        sql_uid = "select uid from gateway where project_id in (select project_id from gateway where gateway_name=N'{}')".format(
            req_customerID)
        cur.execute(sql_uid)
        uid_list = cur.fetchall()
        for uid in uid_list:

            sql = "select datetime,demand_quarter from {} where gateway_uid='{}' and address='{}'and channel='{}' and datetime >='{}' and datetime <='{}'and  SECOND(datetime)=0 and  MOD(MINUTE(datetime),15)=0 ORDER BY datetime ASC".format(
                "demand",  uid['uid'], '1', '1', req_dateFrom, req_dateTo, req_customerID)
            cur.execute(sql)
            result = cur.fetchall()
            i = 0
            totalkwh = 0
            while i < len(result):
                totalkwh += result[i]['demand_quarter'] / 1000
                i += 1
            # co2 = 0.529*totalkwh
            if gateway_uid == uid['uid']:
                power = totalkwh
            sum_power += totalkwh
        output = []
        output.append({'user': req_customerID, 'power': power, 'local_averagepower': sum_power / len(uid_list), 'percent': round(
            (power / (sum_power / len(uid_list))) * 100, 0)if (sum_power / len(uid_list)) != 0 else 0})
        return jsonify(output), 201
    else:
        req_dateTo = datetime.datetime.now().replace(
            year=2017, month=12, day=31, hour=23, minute=45, second=0, microsecond=0)
        # time_range = datetime.timedelta(days = 60)#可調整時間長度
        # req_dateFrom = datetime.datetime.now()-time_range
        req_dateFrom = datetime.datetime.now().replace(
            year=2017, month=12, day=1, hour=0, minute=15, second=0, microsecond=0)

        data_output = {}
        data_output['total'] = []
        for acc in range(1, 11):  # here needs change, note that 1,11 means 1-10
            account = "d{num:05d}".format(num=acc)

            electricity_table = 'electricity_information'
            cur.execute("select datetime,value from {} where user_id = '{}'  and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
                electricity_table, account.lower(), req_dateFrom, req_dateTo))
            result = cur.fetchall()

            addresult = []
            for i in result:
                addresult.append(
                    {'timestamp': i["datetime"], 'value': i["value"]})

            for d in range(len(result)):
                addresult[d]['value'] += addresult[d - 1]['value']

            data_output['total'].append({'account': account, 'max_powernumber': round(
                addresult[-1]['value'], 0)})
            averagepower = 0
        for value in data_output['total']:
            averagepower += value['max_powernumber']
        averagepower = averagepower / 10

        output = []
        for d in data_output['total']:
            if(req_customerID.lower() == d['account']):
                output.append({'user': req_customerID, 'power': d['max_powernumber'], 'local_averagepower': averagepower, 'percent': round(
                    (d['max_powernumber'] / averagepower) * 100, 0)})

        return jsonify(output), 201
