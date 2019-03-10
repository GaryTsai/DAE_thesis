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
import numpy
from datetime import timedelta
from time import gmtime, strftime
from .database import db

# API


@api.route('/temperature_alarm', methods=['GET'])
def temperature_alarm():
    conn = db.getConnection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    req_customerID = request.args.get(
        'CustomerID', default="", type=str).lower()
    req_dateFrom = datetime.datetime.now().replace(
        day=1, hour=0, minute=15, second=0, microsecond=0)
    req_dateTo = datetime.datetime.now()
    # 體感與電力資料整合
    data = apparent_temp_electricity_integrate(
        cur, req_dateFrom, req_dateTo, req_customerID)

    # 取出最新溫度與體感
    cur.execute(
        "SELECT DateTime,Temperature,apparent_temperature FROM weather ORDER BY Datetime DESC LIMIT 1")
    now_data = cur.fetchall()
    now_temp = now_data[0]['Temperature']
    print('00000', now_temp)

    # 最大值、最小值向上取整
    max_min_region = max_min_apparent_temperature(
        cur, req_dateFrom, req_dateTo)
    if max_min_region[0]['MIN(apparent_temperature)'] is None and max_min_region[0]['MAX(apparent_temperature)'] is None:
        inital_apparent_temperature = 0
        max_apparent_temperature = 0
    else:
        inital_apparent_temperature = math.ceil(
            max_min_region[0]['MIN(apparent_temperature)'])
        max_apparent_temperature = math.ceil(
            max_min_region[0]['MAX(apparent_temperature)'])

    # set ini key and value
    pre_temp_str = 'temp'
    interval_apparent_temperature = 2
    max_offset = 2
    apparentemp_dict = {}
    count_dict = {}
    region_temp_avg_dict = {}
    apparentemp_dict, count_dict, region_temp_avg_dict = set_temperature_region(
        inital_apparent_temperature, max_apparent_temperature, max_offset, interval_apparent_temperature, pre_temp_str)

    # cal key val
    for temp in data:
        for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
            if apparent_temp >= max_apparent_temperature:
                if(temp["apparenttemperature"] > apparent_temp - interval_apparent_temperature):
                    temp_key_str = pre_temp_str + \
                        str(apparent_temp - interval_apparent_temperature) + '_up'
                    apparentemp_dict[temp_key_str] += temp['value']
                    count_dict[temp_key_str] += 1
                    break
            elif apparent_temp == inital_apparent_temperature:
                if(temp["apparenttemperature"] <= apparent_temp):
                    temp_key_str = pre_temp_str + str(apparent_temp) + '_down'
                    apparentemp_dict[temp_key_str] += temp['value']
                    count_dict[temp_key_str] += 1
                    break
            else:
                if(temp["apparenttemperature"] > apparent_temp - interval_apparent_temperature and temp["apparenttemperature"] <= apparent_temp):
                    temp_key_str = pre_temp_str +\
                        str(apparent_temp - interval_apparent_temperature) +\
                        '_' + str(apparent_temp)
                    apparentemp_dict[temp_key_str] += temp['value']
                    count_dict[temp_key_str] += 1
                    break

    max_value = 0
    max_value_region = 0
    for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
        if apparent_temp >= max_apparent_temperature:
            temp_key_str = pre_temp_str +\
                str(apparent_temp - interval_apparent_temperature) + '_up'
        elif apparent_temp == inital_apparent_temperature:
            temp_key_str = pre_temp_str + str(apparent_temp) + '_down'
        else:
            temp_key_str = pre_temp_str +\
                str(apparent_temp - interval_apparent_temperature) +\
                '_' + str(apparent_temp)

        if count_dict[temp_key_str] == 0:
            pass
        else:
            region_temp_avg_dict[temp_key_str] = apparentemp_dict[temp_key_str] / \
                count_dict[temp_key_str]
        if region_temp_avg_dict[temp_key_str] >= max_value:
            max_value = region_temp_avg_dict[temp_key_str]
            max_value_region = apparent_temp

    temperature_present = []
    temperature_present.append({'alarm': 0})
    if max_value_region == max_apparent_temperature:
        if(now_temp >= max_value_region):
            temperature_present[0]['alarm'] = 1
    elif max_value_region == inital_apparent_temperature:
        if(now_temp <= max_value_region):
            temperature_present[0]['alarm'] = 1
    else:
        if(now_temp <= max_value_region and now_temp > max_value_region - interval_apparent_temperature):
            temperature_present[0]['alarm'] = 1
    temperature_present.append(
        {'alarm_apptemp': max_value_region - interval_apparent_temperature})

    now_apptemp = now_data[0]['apparent_temperature']

    for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
        if apparent_temp >= max_apparent_temperature:
            if(now_apptemp > apparent_temp - interval_apparent_temperature):
                temp_key_str = pre_temp_str +\
                    str(apparent_temp - interval_apparent_temperature) + '_up'
                now_avg_value = region_temp_avg_dict[temp_key_str]
                break
        elif apparent_temp == inital_apparent_temperature:
            if(now_apptemp <= apparent_temp):
                temp_key_str = pre_temp_str + str(apparent_temp) + '_down'
                now_avg_value = region_temp_avg_dict[temp_key_str]
                break
        else:
            if(now_apptemp > apparent_temp - interval_apparent_temperature and now_apptemp <= apparent_temp):
                temp_key_str = pre_temp_str +\
                    str(apparent_temp - interval_apparent_temperature) +\
                    '_' + str(apparent_temp)
                now_avg_value = region_temp_avg_dict[temp_key_str]
                break

# now_data[0]['Temperature']
    if max_min_region[0]['MIN(apparent_temperature)'] is None and max_min_region[0]['MAX(apparent_temperature)'] is None:
        temperature_present.append({'now_apptemp': "無即時體感溫度", 'now_temp': "無即時溫度",
                                    'now_avg_value': "無", 'last_update_time': now_data[0]['DateTime']})
    else:
        temperature_present.append({'now_apptemp': now_data[0]['apparent_temperature'], 'now_temp': now_data[0]['Temperature'],
                                    'now_avg_value': round(now_avg_value * 4, 2), 'last_update_time': now_data[0]['DateTime']})
    print(temperature_present)
    return jsonify(temperature_present), 201


@api.route('/temperature_correlation', methods=['GET'])
def temperature_correlation():
    conn = db.getConnection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    req_customerID = request.args.get(
        'CustomerID', default="", type=str).lower()
    '''
    req_dateFrom = datetime.datetime.now().replace(
        day=1, hour=0, minute=15, second=0, microsecond=0)
    req_dateTo = datetime.datetime.now()
    '''
    req_dateFrom = datetime.datetime.now().replace(
        year=2017, month=12, day=1, hour=0, minute=15, second=0, microsecond=0)
    req_dateTo = datetime.datetime.now().replace(
        year=2017, month=12, day=31, hour=23, minute=45, second=0, microsecond=0)
    data = {}
    data = apparent_temp_electricity_integrate(
        cur, req_dateFrom, req_dateTo, req_customerID)
    print('體感與電力資料整合')
    print(data)
    # print('當月每筆用電度數與體感溫度')
    # print(data)
    # 取最大、最小值向上取整
    max_min_region = max_min_apparent_temperature(
        cur, req_dateFrom, req_dateTo)
    inital_apparent_temperature = math.ceil(
        max_min_region[0]['MIN(apparent_temperature)'])
    max_apparent_temperature = math.ceil(
        max_min_region[0]['MAX(apparent_temperature)'])

    # set ini key and value
    interval_apparent_temperature = 2
    max_offset = 2
    pre_temp_str = 'temp'
    apparentemp_dict = {}
    count_dict = {}
    region_temp_avg_dict = {}

    apparentemp_dict, count_dict, region_temp_avg_dict = set_temperature_region(
        inital_apparent_temperature, max_apparent_temperature, max_offset, interval_apparent_temperature, pre_temp_str)
    print('設定溫度區間')
    print(apparentemp_dict)

    sum_of_tempcount = 0
    # sum_of_electricity = 0
    # 計算每個溫度區間的溫度個數與用電累積
    for temp in data:
        for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
            if apparent_temp >= max_apparent_temperature:
                if(temp["apparenttemperature"] >= apparent_temp - interval_apparent_temperature):
                    temp_key_str = pre_temp_str + \
                        str(apparent_temp - interval_apparent_temperature) + '_up'
                    apparentemp_dict[temp_key_str] += temp['value']
                    # sum_of_electricity += temp['value']
                    count_dict[temp_key_str] += 1
                    sum_of_tempcount += 1
                    break
            elif apparent_temp == inital_apparent_temperature:
                if(temp["apparenttemperature"] <= apparent_temp):
                    temp_key_str = pre_temp_str + str(apparent_temp) + '_down'
                    apparentemp_dict[temp_key_str] += temp['value']
                    # sum_of_electricity += temp['value']
                    count_dict[temp_key_str] += 1
                    sum_of_tempcount += 1
                    break
            else:
                if(temp["apparenttemperature"] > apparent_temp - interval_apparent_temperature and temp["apparenttemperature"] <= apparent_temp):
                    temp_key_str = pre_temp_str + \
                        str(apparent_temp - interval_apparent_temperature) + \
                        '_' + str(apparent_temp)
                    apparentemp_dict[temp_key_str] += temp['value']
                    # sum_of_electricity += temp['value']
                    count_dict[temp_key_str] += 1
                    sum_of_tempcount += 1
                    break
    # print('sum_of_tempcount')
    # print(sum_of_tempcount)
    print('溫度區間用電累積')
    print(apparentemp_dict)
    print('該溫度區間次數')
    print(count_dict)

    electricity_persent = []
    region_str = 0
    # 該溫度區間計算每小時用電度度數與每天溫度平均時數(一天在此溫度有幾小時)
    for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
        if apparent_temp >= max_apparent_temperature:
            temp_key_str = pre_temp_str + \
                str(apparent_temp - interval_apparent_temperature) + '_up'
            # print(temp_key_str)
            region_str = str(
                apparent_temp - interval_apparent_temperature) + '°C以上'
            electricity_persent.append({'region': region_str, 'value': round(
                (apparentemp_dict[temp_key_str] / count_dict[temp_key_str]) * 4, 2)if count_dict[temp_key_str]else 0,
                'count': round(count_dict[temp_key_str] * 24 / sum_of_tempcount, 2)if sum_of_tempcount else 0})

        elif apparent_temp == inital_apparent_temperature:
            temp_key_str = pre_temp_str + str(apparent_temp) + '_down'
            region_str = str(apparent_temp) + '°C以下'
            # print(temp_key_str)
            electricity_persent.append({'region': region_str, 'value': round(
                (apparentemp_dict[temp_key_str] / count_dict[temp_key_str]) * 4, 2)if count_dict[temp_key_str] else 0,
                'count': round(count_dict[temp_key_str] * 24 / sum_of_tempcount, 2)if sum_of_tempcount else 0})

        else:
            temp_key_str = pre_temp_str + \
                str(apparent_temp - interval_apparent_temperature) + \
                '_' + str(apparent_temp)
            # print(temp_key_str)
            region_str = str(
                apparent_temp - interval_apparent_temperature) + '°C~' + str(apparent_temp) + '°C'
            electricity_persent.append({'region': region_str, 'value': round(
                (apparentemp_dict[temp_key_str] / count_dict[temp_key_str]) * 4, 2)if count_dict[temp_key_str] else 0,
                'count': round(count_dict[temp_key_str] * 24 / sum_of_tempcount, 2)if sum_of_tempcount else 0})

    print('溫度區間溫度與用電平均值')
    print(electricity_persent)
    # 相關係數計算
    temp_powervalue = []
    # 取出每小時用電度數
    for temperature_region in electricity_persent:
        temp_powervalue.append(temperature_region['value'])

    print('該溫度區間每小時用電度數')
    print(temp_powervalue)
    temp_range = []
    # 取出溫度
    for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
        temp_range.append(apparent_temp)

    print('該溫度區間每小時用電度數')
    print(temp_range)
    temp_corrcoef = numpy.corrcoef(temp_powervalue, temp_range)
    print('相關係數')
    print(temp_corrcoef)
    temp_corrcoef_value = 0
    temp_corrcoef_value = round(-30 * temp_corrcoef[0][1] + 70, 2)
    # 1 到 -1之間，溫度越高用電量越高
    print('相關係數換算結果')
    print(temp_corrcoef_value)

    return jsonify(temp_corrcoef_value), 201


@api.route('/data_persent', methods=['GET'])
def post_request_persent():
    conn = db.getConnection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    req_customerID = request.args.get('CustomerID', default="", type=str)
    req_customerID = req_customerID.lower()
    table = 'electricity_information'
    '''
    req_dateFrom = datetime.datetime.now().replace(
        day=1, hour=0, minute=15, second=0, microsecond=0)
    req_dateTo = datetime.datetime.now()
    '''
    req_dateFrom = datetime.datetime.now().replace(
        year=2017, month=12, day=1, hour=0, minute=15, second=0, microsecond=0)
    req_dateTo = datetime.datetime.now().replace(
        year=2017, month=12, day=31, hour=23, minute=45, second=0, microsecond=0)

    data = {}
    data = apparent_temp_electricity_integrate(
        cur, req_dateFrom, req_dateTo, req_customerID)

    max_min_region = max_min_apparent_temperature(
        cur, req_dateFrom, req_dateTo)
    inital_apparent_temperature = math.ceil(
        max_min_region[0]['MIN(apparent_temperature)'])
    max_apparent_temperature = math.ceil(
        max_min_region[0]['MAX(apparent_temperature)'])

    interval_apparent_temperature = 2
    max_offset = 2
    pre_temp_str = 'temp'
    apparentemp_dict = {}
    count_dict = {}
    region_temp_avg_dict = {}

    # set ini key and value
    for i in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):

        if i >= max_apparent_temperature:
            key_str = pre_temp_str + str(i - max_offset) + '_up'  # max的前一區間之上
        elif i == inital_apparent_temperature:
            key_str = pre_temp_str + str(i) + '_down'
        else:
            key_str = pre_temp_str + \
                str(i - interval_apparent_temperature) + '_' + str(i)
        if key_str not in apparentemp_dict:
            apparentemp_dict[key_str] = 0
            count_dict[key_str] = 0
            region_temp_avg_dict[key_str] = 0

    sum_of_tempcount = 0
    sum_of_electricity = 0
    for temp in data:
        for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
            if apparent_temp >= max_apparent_temperature:
                if(temp["apparenttemperature"] > apparent_temp - interval_apparent_temperature):
                    temp_key_str = pre_temp_str + \
                        str(apparent_temp - interval_apparent_temperature) + '_up'
                    apparentemp_dict[temp_key_str] += temp['value']
                    sum_of_electricity += temp['value']
                    count_dict[temp_key_str] += 1
                    sum_of_tempcount += 1
                    break
            elif apparent_temp == inital_apparent_temperature:
                if(temp["apparenttemperature"] <= apparent_temp):
                    temp_key_str = pre_temp_str + str(apparent_temp) + '_down'
                    apparentemp_dict[temp_key_str] += temp['value']
                    sum_of_electricity += temp['value']
                    count_dict[temp_key_str] += 1
                    sum_of_tempcount += 1
                    break
            else:
                if(temp["apparenttemperature"] > apparent_temp - interval_apparent_temperature and temp["apparenttemperature"] <= apparent_temp):
                    temp_key_str = pre_temp_str + \
                        str(apparent_temp - interval_apparent_temperature) + \
                        '_' + str(apparent_temp)
                    apparentemp_dict[temp_key_str] += temp['value']
                    sum_of_electricity += temp['value']
                    count_dict[temp_key_str] += 1
                    sum_of_tempcount += 1
                    break

    electricity_persent = []
    region_str = 0

    for apparent_temp in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
        if apparent_temp >= max_apparent_temperature:
            temp_key_str = pre_temp_str + \
                str(apparent_temp - interval_apparent_temperature) + '_up'
            region_str = str(
                apparent_temp - interval_apparent_temperature) + '~' + str(
                apparent_temp)
            electricity_persent.append({'region': region_str, 'value': round(
                (apparentemp_dict[temp_key_str] / count_dict[temp_key_str]) * 4, 2)if count_dict[temp_key_str]else 0,
                'count': round(count_dict[temp_key_str] * 24 / sum_of_tempcount, 2)if sum_of_tempcount else 0})

        elif apparent_temp == inital_apparent_temperature:
            temp_key_str = pre_temp_str + str(apparent_temp) + '_down'
            region_str = str(
                apparent_temp - interval_apparent_temperature) + '~' + str(apparent_temp)
            electricity_persent.append({'region': region_str, 'value': round(
                (apparentemp_dict[temp_key_str] / count_dict[temp_key_str]) * 4, 2)if count_dict[temp_key_str] else 0,
                'count': round(count_dict[temp_key_str] * 24 / sum_of_tempcount, 2)if sum_of_tempcount else 0})

        else:
            temp_key_str = pre_temp_str +\
                str(apparent_temp - interval_apparent_temperature) +\
                '_' + str(apparent_temp)
            region_str = str(
                apparent_temp - interval_apparent_temperature) + '~' + str(apparent_temp)
            electricity_persent.append({'region': region_str, 'value': round(
                (apparentemp_dict[temp_key_str] / count_dict[temp_key_str]) * 4, 2)if count_dict[temp_key_str] else 0,
                'count': round(count_dict[temp_key_str] * 24 / sum_of_tempcount, 2)if sum_of_tempcount else 0})

    return jsonify(electricity_persent), 201

# Sub function


def set_temperature_region(inital_apparent_temperature, max_apparent_temperature, max_offset, interval_apparent_temperature, pre_temp_str):

    apparentemp_dict = {}
    count_dict = {}
    region_temp_avg_dict = {}
    for i in range(inital_apparent_temperature, max_apparent_temperature + max_offset, interval_apparent_temperature):
        if i >= max_apparent_temperature:
            key_str = pre_temp_str + str(i - max_offset) + '_up'  # max的前一區間之上
        elif i == inital_apparent_temperature:
            key_str = pre_temp_str + str(i) + '_down'
        else:
            key_str = pre_temp_str + \
                str(i - interval_apparent_temperature) + '_' + str(i)
        if key_str not in apparentemp_dict:
            apparentemp_dict[key_str] = 0
            count_dict[key_str] = 0
            region_temp_avg_dict[key_str] = 0

    return apparentemp_dict, count_dict, region_temp_avg_dict


def apparent_temp_electricity_integrate(cur, req_dateFrom, req_dateTo, req_customerID):
    table = 'electricity_information'
    # 用戶電力資訊
    cur.execute("select datetime,value from {} where datetime >='{}' and datetime <='{}' and user_id = '{}' ORDER BY datetime ASC".format(
        table, req_dateFrom, req_dateTo, req_customerID))
    electricity_data = cur.fetchall()
    # 體感資訊
    cur.execute("select DateTime,apparent_temperature from weather where DateTime >='{}' and DateTime <='{}'".format(
        req_dateFrom, req_dateTo))
    apparent_temperature_data = cur.fetchall()
    apparent_temperature = {}
    for j in apparent_temperature_data:
        apparent_temperature[datetime.datetime.strftime(
            j['DateTime'], '%Y-%m-%d  %H:%M')] = j['apparent_temperature']
    # 體感溫度與電力資訊整合
    combine_data = []
    for r in electricity_data:
        res_time = r["datetime"]
        if not res_time.minute == 0:
            res_time = res_time.replace(minute=0) + datetime.timedelta(hours=1)
            if res_time > datetime.datetime.now():
                res_time = res_time - datetime.timedelta(hours=1)
        if not datetime.datetime.strftime(res_time, '%Y-%m-%d  %H:%M') in apparent_temperature:
            res_time = res_time - datetime.timedelta(hours=1)
        combine_data.append({'timestamp': r["datetime"], 'value': r["value"],
                             'apparenttemperature': apparent_temperature[datetime.datetime.strftime(res_time, '%Y-%m-%d  %H:%M')]})
    return combine_data


def max_min_apparent_temperature(cur, req_dateFrom, req_dateTo):
    max_min_apparent_temperature = []
    cur.execute("SELECT MAX(apparent_temperature) , MIN(apparent_temperature) from weather where DateTime >='{}' and DateTime <='{}'".format(
        req_dateFrom, req_dateTo))
    max_min_apparent_temperature = cur.fetchall()
    return max_min_apparent_temperature
