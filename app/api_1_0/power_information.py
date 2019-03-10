from flask import jsonify, request
from . import api
import datetime
import json
import requests
from sqlalchemy import func, and_, or_, between, exists
# from ..models import *
import pymysql
import ctypes
import sys
import math
from time import gmtime, strftime
import time
import numpy
from datetime import timedelta
from .database import db_query
# from .method import mysql as daesql
import calendar
@api.route('/power_check', methods=['GET'])
def power_check():
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    address = request.args.get('address', default="", type=str)
    channel = request.args.get('channel', default="", type=str)
    model = request.args.get('model', default="", type=str)
    authority = request.args.get('authority', default="", type=str)
    month = request.args.get('month', default="", type=str)
    year = request.args.get('year', default="", type=str)

    start_time =  datetime.datetime.now().replace(year=int(year), month=int(month), day=1, hour=0, minute=0, second=0, microsecond=0)
    if(month =="12"):
        end_time = datetime.datetime.now().replace(year=int(year)+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        end_time = datetime.datetime.now().replace(year=int(year), month=int(month)+1, day=1, hour=0, minute=0, second=0, microsecond=0)

    sql = "select COUNT(Total_value) from {} as d where d.address = '{}' and d.channel = '{}' and d.gateway_uid='{}' and d.datetime > '{}' and d.datetime <'{}' ".format("demand",  address, channel, gateway_uid, start_time, end_time)
    print('sql:'+sql)
    db_query.execute(sql)
    data = db_query.fetchall()
    power_count = int(data[0]['COUNT(Total_value)'])

    return jsonify(power_count), 201

@api.route('/realtime_power', methods=['GET'])
def post_request_n():
    authority = request.args.get('authority', default="", type=str)
    req_customerID = request.args.get('CustomerID', default="", type=str)
    year = request.args.get('year', default="", type=str)
    month = request.args.get('month', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    address = request.args.get('address', default="", type=str)
    channel = request.args.get('channel', default="", type=str)
    days = calendar.monthrange(int(year), int(month))[1]

    if(month == '1'):
        req_dateFrom = datetime.datetime.now().replace(year=int(year)-1, month=12, day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo = datetime.datetime.now().replace(year=int(year), month=1, day=1,hour=0, minute=15, second=0, microsecond=0)
        req_dateTo_count = datetime.datetime.now().replace(year=int(year), month=int(month), day=days, hour=0, minute=0, second=0, microsecond=0)
    elif(month == '12'):
        req_dateFrom = datetime.datetime.now().replace(year=int(year), month=int(month),day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo = datetime.datetime.now().replace(year=int(year)+1, month=1, day=1,hour=0, minute=15, second=0, microsecond=0)
        req_dateTo_count = datetime.datetime.now().replace(year=int(year), month=int(month), day=days, hour=0, minute=0, second=0, microsecond=0)
    else :
        req_dateFrom = datetime.datetime.now().replace(year=int(year), month=int(month), day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo = datetime.datetime.now().replace(year=int(year), month=(int(month) + 1), day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo_count = datetime.datetime.now().replace(year=int(year), month=(int(month)), day=calendar.monthrange(int(year), (int(month)))[1], hour=0, minute=0, second=0, microsecond=0)
    result= sum_electricity_data(db_query,authority, req_customerID.lower(), req_dateFrom, req_dateTo,gateway_uid,address,channel)
    time_count = sum_electricity_data(db_query,authority, req_customerID.lower(), req_dateFrom, req_dateTo_count,gateway_uid,address,channel)
    temp_timecount = len(time_count['demands'] )
    print('69', req_dateFrom, req_dateTo)
    if temp_timecount == 0:
        return jsonify(temp_timecount), 201
    power_data = {}
    sum_electricity_power=0#累加總電量
    power_data['demands'] = []
    TimeList=[]#紀錄時間
    for r in result['demands'] :
        sum_electricity_power += r["value"]
        power_data['demands'].append({'time': datetime.datetime.strftime(r["datetime"], '%Y-%m-%d  %H:%M:%S'),'value': r["value"]})
        TimeList.append(datetime.datetime.strftime(r["datetime"], '%Y-%m-%d  %H:%M:%S'))
    # 補足該月沒有電力的時間點
    time_end = power_data['demands'][len(power_data['demands']) - 1]['time']
    time_start = power_data['demands'][0]['time']
    if(type(time_end) != type(req_dateTo)):
        time_end = datetime.datetime.strptime(time_end, '%Y-%m-%d  %H:%M:%S')
        time_start = datetime.datetime.strptime(time_start, '%Y-%m-%d  %H:%M:%S')
    for item in power_data['demands']:
        TimeList.append(item['time'])
    # 補足該月沒有電力的時間點
    while(time_start < req_dateTo):
        time_start = time_start + timedelta(minutes=15)
        if (datetime.datetime.strftime(time_start, '%Y-%m-%d  %H:%M:%S') not in TimeList) and (time_start < time_end):#沒有此電力的時間點
            power_data['demands'].append({'time': datetime.datetime.strftime(time_start, '%Y-%m-%d  %H:%M:%S'), 'value': 0, 'time_count': temp_timecount})
        elif(time_start == time_end):
                temp_timecount = len(power_data['demands'])
        else:
            power_data['demands'].append({'time': datetime.datetime.strftime(time_start, '%Y-%m-%d  %H:%M:%S'), 'time_count': temp_timecount})
    power_data['demands'] =sorted(power_data['demands'], key=foo2)
    power_data['demands'].append({'sum_power': sum_electricity_power})


    return jsonify(power_data), 201

@api.route('/data_accumulation_kWh', methods=['GET'])
def post_request_test():
    authority = request.args.get('authority', default="", type=str)
    req_customerID = request.args.get('CustomerID', default="", type=str)
    year = request.args.get('year', default="", type=str)
    month = request.args.get('month', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    address = request.args.get('address', default="", type=str)
    channel = request.args.get('channel', default="", type=str)
    req_dateFrom = datetime.datetime.now().replace(year=int(year), month=int(month), day=1, hour=0, minute=0, second=0, microsecond=0)
    # 當一個月時間設定
    today_month = 12
    if(month == '12'):
        req_dateTo = datetime.datetime.now().replace(year=int(year)+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        req_dateTo = datetime.datetime.now().replace(year=int(year), month=int(month)+1,
                                                     day=1, hour=0, minute=0, second=0, microsecond=0)
    if (month == '1'):
        ex_req_dateTo = datetime.datetime.now().replace(year=int(year)-1, month=int(month), day=1, hour=0, minute=0, second=0, microsecond=0)
        ex_req_dateFrom = datetime.datetime.now().replace(year=int(year)-1, month=int(month), day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        ex_req_dateTo = datetime.datetime.now().replace(year=int(year), month=int(month), day=1, hour=0, minute=0, second=0, microsecond=0)
        ex_req_dateFrom = datetime.datetime.now().replace(year=int(year), month=int(month)-1, day=1, hour=0, minute=0, second=0, microsecond=0)

    start= time.time()#計算執行時間1
    result = sum_electricity_data(db_query, authority ,req_customerID, req_dateFrom, req_dateTo,gateway_uid,address,channel)
    ex_result = sum_electricity_data(db_query, authority,req_customerID, ex_req_dateFrom, ex_req_dateTo,gateway_uid,address,channel)
    ex_month_power = 0
    count=0
    for data in ex_result['demands']:
        ex_month_power += data['value']

    def monthBill5(add):
        bill = 0
        if (add['timestamp5'].month == 6) or (add['timestamp5'].month == 7) or (add['timestamp5'].month == 8) or (add['timestamp5'].month == 9):
            if add['value'] <= 120:
                bill = add['value'] * 1.63
            elif add['value'] <= 330:
                bill = (add['value'] - 120) * 2.38 + 120 * 1.63
            elif add['value'] <= 500:
                bill = (add['value'] - 330) * 3.52 + 120 * 1.63 + 210 * 2.38
            elif add['value'] <= 700:
                bill = (add['value'] - 500) * 4.61 + 120 * \
                    1.63 + 210 * 2.38 + 170 * 3.52
            elif add['value'] <= 1000:
                bill = (add['value'] - 700) * 5.42 + 120 * 1.63 + \
                    210 * 2.38 + 170 * 3.52 + 200 * 4.61
            else:
                bill = (add['value'] - 1000) * 6.13 + 120 * 1.63 + \
                    210 * 2.38 + 170 * 3.52 + 200 * 4.61 + 300 * 5.42
        else:
            if add['value'] <= 120:
                bill = add['value'] * 1.63
            elif add['value'] <= 330:
                bill = (add['value'] - 120) * 2.10 + 120 * 1.63
            elif add['value'] <= 500:
                bill = (add['value'] - 330) * 2.89 + 120 * 1.63 + 210 * 2.10
            elif add['value'] <= 700:
                bill = (add['value'] - 500) * 3.79 + 120 * \
                    1.63 + 210 * 2.10 + 170 * 2.89
            elif add['value'] <= 1000:
                bill = (add['value'] - 700) * 4.42 + 120 * 1.63 + \
                    210 * 2.10 + 170 * 2.89 + 200 * 3.79
            else:
                bill = (add['value'] - 1000) * 4.83 + 120 * 1.63 + \
                    210 * 2.10 + 170 * 2.89 + 200 * 3.79 + 300 * 4.42
        return bill

    def month2Bill5(add):
        bill = 0
        if (add['timestamp5'].month == 6) or (add['timestamp5'].month == 7) or (add['timestamp5'].month == 8) or (add['timestamp5'].month == 9):
            if add['value'] <= 240:
                bill = add['value'] * 1.63
            elif add['value'] <= 660:
                bill = (add['value'] - 240) * 2.38 + 240 * 1.63
            elif add['value'] <= 1000:
                bill = (add['value'] - 660) * 3.52 + 240 * 1.63 + 420 * 2.38
            elif add['value'] <= 1400:
                bill = (add['value'] - 1000) * 4.61 + \
                    240 * 1.63 + 420 * 2.38 + 340 * 3.52
            elif add['value'] <= 1000:
                bill = (add['value'] - 1400) * 5.42 + 240 * \
                    1.63 + 420 * 2.38 + 340 * 3.52 + 400 * 4.61
            else:
                bill = (add['value'] - 2000) * 6.13 + 240 * 1.63 + \
                    420 * 2.38 + 340 * 3.52 + 400 * 4.61 + 600 * 5.42
        else:
            if add['value'] <= 240:
                bill = add['value'] * 1.63
            elif add['value'] <= 660:
                bill = (add['value'] - 240) * 2.10 + 240 * 1.63
            elif add['value'] <= 1000:
                bill = (add['value'] - 660) * 2.89 + 240 * 1.63 + 420 * 2.10
            elif add['value'] <= 1400:
                bill = (add['value'] - 1000) * 3.79 + \
                    240 * 1.63 + 420 * 2.10 + 340 * 2.89
            elif add['value'] <= 2000:
                bill = (add['value'] - 1400) * 4.42 + 240 * \
                    1.63 + 420 * 2.10 + 340 * 2.89 + 400 * 3.79
            else:
                bill = (add['value'] - 2000) * 4.83 + 240 * 1.63 + \
                    420 * 2.10 + 340 * 2.89 + 400 * 3.79 + 600 * 4.42
        return bill
    time0730 = datetime.time(7, 30, 0)
    time2230 = datetime.time(22, 30, 0)

    def monthBill6(res):
        bill = 0

        if (((res['datetime'].month == 1) and (res['datetime'].day == 1)) or
                ((res['datetime'].month == 1) and (res['datetime'].day == 27)) or
                ((res['datetime'].month == 1) and (res['datetime'].day == 28)) or
                ((res['datetime'].month == 1) and (res['datetime'].day == 29)) or
                ((res['datetime'].month == 1) and (res['datetime'].day == 30)) or
                ((res['datetime'].month == 1) and (res['datetime'].day == 31)) or
                ((res['datetime'].month == 2) and (res['datetime'].day == 1)) or
                ((res['datetime'].month == 2) and (res['datetime'].day == 28)) or
                ((res['datetime'].month == 4) and (res['datetime'].day == 4)) or
                ((res['datetime'].month == 5) and (res['datetime'].day == 1)) or
                ((res['datetime'].month == 5) and (res['datetime'].day == 30)) or
                ((res['datetime'].month == 10) and (res['datetime'].day == 4)) or
                ((res['datetime'].month == 10) and (res['datetime'].day == 10))):
            bill = res['value'] * 1.65
        elif ((res['datetime'].month == 6) or (res['datetime'].month == 7)
              or (res['datetime'].month == 8) or (res['datetime'].month == 9)):

            if ((res['datetime'].weekday() == 0) or (res['datetime'].weekday() == 1) or
                    (res['datetime'].weekday() == 2) or (res['datetime'].weekday() == 3) or
                    (res['datetime'].weekday() == 4)):

                if (((res['datetime'].hour > 7) and (res['datetime'].hour < 22))
                    or ((res['datetime'].hour == 7) and (res['datetime'].minute > 30))
                        or ((res['datetime'].hour == 22) and (res['datetime'].minute <= 30))):
                    bill = res['value'] * 4.19
                else:
                    bill = res['value'] * 1.71
            else:
                bill = res['value'] * 1.71
        else:

            if ((res['datetime'].weekday() == 0) or (res['datetime'].weekday() == 1) or
                    (res['datetime'].weekday() == 2) or (res['datetime'].weekday() == 3) or
                    (res['datetime'].weekday() == 4)):

                if (((res['datetime'].hour > time0730.hour) and (res['datetime'].hour < time2230.hour))
                    or ((res['datetime'].hour == 7) and (res['datetime'].minute >= 30))
                        or ((res['datetime'].hour == 22) and (res['datetime'].minute <= 30))):
                    bill = res['value'] * 4.01
                else:
                    bill = res['value'] * 1.65
            else:
                bill = res['value'] * 1.65
        return bill

    addresult = []
    if(authority == "1"):

        for i in result['demands']:
            addresult.append({'datetime': i["datetime"], 'timestamp5': result['demands'][0]
                            ['datetime'], 'value': i["value"], 'lineColor': '1', 'bill5': 0, 'bill6': 0})
            addresult[0]['bill6'] = monthBill6(result['demands'][0])
    else:
         for i in result['demands']:
            addresult.append({'datetime': i["datetime"], 'timestamp5': result['demands'][0]
                            ['datetime'], 'value': i["value"], 'lineColor': '1', 'bill5': 0, 'bill6': 0})
            addresult[0]['bill6'] = monthBill6(result['demands'][0])
    # addresult[0]['bill6'] = monthBill6(result[0])
    d = 1
    while d < len(result['demands']):
        addresult[d]['value'] += addresult[d - 1]['value']
        if addresult[d]['value'] <= 2000:
            addresult[d]['bill6'] = monthBill6(result['demands'][d])
        else:
            break
        d += 1
    if d < len(addresult) and addresult[d]['value'] > 2000:
        tem = []
        tem.append(
            {'datetime': addresult[d]['datetime'], 'value': addresult[d]['value'] - 2000})
        addresult[d]['bill6'] = monthBill6(tem[0]) + (tem[0]['value']) * 0.91
        d += 1
        while d < len(addresult):
            addresult[d]['value'] += addresult[d - 1]['value']
            addresult[d]['bill6'] = monthBill6(
                result['demands'][d]) + result['demands'][d]['value'] * 0.91
            d += 1
    d = d - 1
    data_count = 0
    colorlist = ['#9cfc85', '#ccfc85', '#fcec85','#fccc85', '#fcb885', '#fc9c85']

    while (data_count < len(result['demands'])):
        if addresult[data_count]['value'] <= 120:
            addresult[data_count]['lineColor'] = colorlist[0]
        elif (addresult[data_count]['value'] <= 330) and (addresult[d]['value'] > 120):
            addresult[data_count]['lineColor'] = colorlist[1]
        elif (addresult[data_count]['value'] <= 500) and (addresult[d]['value'] > 330):
            addresult[data_count]['lineColor'] = colorlist[2]
        elif (addresult[data_count]['value'] <= 700) and (addresult[d]['value'] > 500):
            addresult[data_count]['lineColor'] = colorlist[3]
        elif (addresult[data_count]['value'] <= 1000) and (addresult[d]['value'] > 700):
            addresult[data_count]['lineColor'] = colorlist[4]
        else:
            addresult[data_count]['lineColor'] = colorlist[5]
        data_count += 1

    j = 0
    while j < len(addresult):
        if len(addresult) <= 32 * 24 * 4:
            addresult[j]['bill5'] = monthBill5(addresult[j])
        else:
            addresult[j]['bill5'] = month2Bill5(addresult[j])
        j += 1
    a = 1

    while a < len(addresult):
        addresult[a]['bill6'] += addresult[a - 1]['bill6']
        a += 1
    a = 0

    final_data_output = {}
    final_data_output['demands'] = []
    final_data_output['power_of_expense'] = []
    for data in addresult:
        final_data_output['demands'].append({'time': data["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                                             'value': round(data["value"], 2), 'lineColor': data["lineColor"],
                                             'bill5': round(data["bill5"], 2), 'bill6': round(data["bill6"], 2)})
    if(len(final_data_output['demands']))==0:
        return jsonify(len(final_data_output['demands'])), 201
    max_power = final_data_output['demands'][len(final_data_output['demands']) - 1]['value']
    time_end = final_data_output['demands'][len(final_data_output['demands']) - 1]['time']
    house_bill = final_data_output['demands'][len(final_data_output['demands']) - 1]['bill5']
    store_bill = final_data_output['demands'][len(final_data_output['demands']) - 1]['bill6']
    time_end = datetime.datetime.strptime(time_end, '%Y-%m-%d  %H:%M:%S')

    while (time_end < req_dateTo):
        time_end = time_end + timedelta(minutes=15)
        final_data_output['demands'].append({'time': datetime.datetime.strftime(time_end, '%Y-%m-%d  %H:%M:%S')})
    final_data_output['power_of_expense'].append({'max_powernumber': max_power, 'house_bill': house_bill, 'store_bill': store_bill, 'ex_month_power': round(ex_month_power, 2)})

    return jsonify(final_data_output), 201


@api.route('/avg_day_power', methods=['GET'])
def avg_request_n():
    authority = request.args.get('authority', default="", type=str)
    req_customerID = request.args.get('CustomerID', default="", type=str)
    year = request.args.get('year', default="", type=str)
    month = request.args.get('month', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    address = request.args.get('address', default="", type=str)
    channel = request.args.get('channel', default="", type=str)
    days = calendar.monthrange(int(year), int(month))[1]
    today = datetime.date.today().day


    if(month == '1'):
        req_dateFrom = datetime.datetime.now().replace(year=int(year)-1, month=12, day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo = datetime.datetime.now().replace(year=int(year), month=1, day=1,hour=0, minute=15, second=0, microsecond=0)
        req_dateTo_count = datetime.datetime.now().replace(year=int(year), month=int(month), day=days, hour=0, minute=0, second=0, microsecond=0)
    elif(month == '12'):
        req_dateFrom = datetime.datetime.now().replace(year=int(year), month=int(month),day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo = datetime.datetime.now().replace(year=int(year)+1, month=1, day=1,hour=0, minute=15, second=0, microsecond=0)
        req_dateTo_count = datetime.datetime.now().replace(year=int(year), month=int(month), day=days, hour=0, minute=0, second=0, microsecond=0)
    else :
        req_dateFrom = datetime.datetime.now().replace(year=int(year), month=int(month), day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo = datetime.datetime.now().replace(year=int(year), month=(int(month) + 1), day=1, hour=0, minute=15, second=0, microsecond=0)
        req_dateTo_count = datetime.datetime.now().replace(year=int(year), month=(int(month)), day=calendar.monthrange(int(year), (int(month)))[1], hour=0, minute=0, second=0, microsecond=0)

    # req_dateFrom = datetime.datetime.now().replace(year=int(year), month=int(month), day=1, hour=0, minute=0, second=0, microsecond=0)
    # req_dateTo = datetime.datetime.now().replace(year=int(year), month=int(month)+1, day=1, hour=0, minute=0, second=0, microsecond=0)

    realtime_req_dateFrom = datetime.datetime.now().replace(year=int(year), month=7, day=15, hour=0, minute=0, second=0, microsecond=0)
    realtime_req_dateTo = realtime_req_dateFrom + datetime.timedelta(hours=23, minutes=59)
    start = time.time()#計算執行時間1
    realtime_result = sum_electricity_data(db_query,authority, req_customerID.lower(), realtime_req_dateFrom, realtime_req_dateTo,gateway_uid,address,channel)
    result = sum_electricity_data(db_query, authority, req_customerID.lower(), req_dateFrom, req_dateTo,gateway_uid,address,channel)

    time_storage = []#儲存時間
    realtime_storage = []  # 儲存時間
    same_time_times = []#時間次數
    avg_power_value = []#電力平均值
    realtime_value = {}
    # 當月時間並累加用電值
    for item in result['demands']:
        hr_min = datetime.datetime.strftime(item['datetime'], "%Y-%m-%d %H:%M:%S").split(" ")[1]
        if hr_min not in time_storage:
            time_storage.append(hr_min)
            same_time_times.append(1)
            avg_power_value.append(item['value'])
        else:
            # same time in hr and minutes
            index = time_storage.index(hr_min)
            same_time_times[index] += 1
            avg_power_value[index] = avg_power_value[index] + item['value']  # 用電值累加計算
    time_storage.sort()#排序時間
    # 當天時間並累加用電值
    for real_item in realtime_result['demands']:
        hr_min = datetime.datetime.strftime(real_item['datetime'], "%Y-%m-%d %H:%M:%S").split(" ")[1]
        if hr_min not in realtime_storage:
            realtime_storage.append(hr_min)
            realtime_value[str(hr_min)]=real_item['value']
        else:
            realtime_value[str(hr_min)] =real_item['value'] # 用電值累加計算
    realtime_storage.sort()#排序時間

    for i in range(len(avg_power_value)):
        avg_power_value[i] = avg_power_value[i] / same_time_times[i]

    final_data_output = []
    # 電力資料
    for i in range(len(time_storage)):
        if(time_storage[i] in realtime_value):
            final_data_output.append({'time': time_storage[i], 'value': round(avg_power_value[i], 5), 'real_time': realtime_value[str(time_storage[i])] })
        else:
            final_data_output.append( {'time': time_storage[i], 'value': round(avg_power_value[i], 5)})

    return jsonify(final_data_output), 201


@api.route('/avg_week_power', methods=['GET'])
def avg_request_week():
    # Data Request
    authority = request.args.get('authority', default="", type=str)
    req_customerID = request.args.get('CustomerID', default="", type=str)
    year = request.args.get('year', default="", type=str)
    month = request.args.get('month', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    address = request.args.get('address', default="", type=str)
    channel = request.args.get('channel', default="", type=str)
    '''
    req_dateFrom = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    req_dateTo = datetime.datetime.now()
    '''
    days = calendar.monthrange(int(year), int(month))[1]
    req_dateFrom = datetime.datetime.now().replace(year=int(year), month=7, day=1, hour=0, minute=0, second=0, microsecond=0)
    req_dateTo = datetime.datetime.now().replace(year=int(year), month=7, day=days, hour=0, minute=0, second=0, microsecond=0)
    current_time = datetime.datetime.now().replace(year=int(year), month=7, day=15, hour=0, minute=0, second=0, microsecond=0)
    start = time.time()  # 計算執行時間1
    result = sum_electricity_data(db_query,authority, req_customerID.lower(), req_dateFrom, req_dateTo,gateway_uid,address,channel)
    final_data_output = {}
    final_data_output['demands'] = []
    for data in result['demands']:
        final_data_output['demands'].append({'time': datetime.datetime.strftime(data["datetime"], '%Y-%m-%d %H:%M'), 'value': data["value"]})
    week_now_value={}#即時用電值[0,0,0,0,0,0,0]
    week = [ '星期一', '星期二', '星期三', '星期四', '星期五', '星期六','星期日']
    weekdate = {}#用電累加[0,0,0,0,0,0,0]
    weekcount = {}# 次數 [0,,0,0,0,0,0,0]
    weekdays= {}#每周次數
    week_avg = []#每天平均用電值
    # initail week data
    for i in range(0,7):
        weekdate[str(i)] = 0
        weekcount[str(i)] = 0
        weekdays[str(i)] = []
        week_now_value[str(i)] = 0

    for it in final_data_output['demands']:
        weekday = datetime.datetime.strptime(it['time'], "%Y-%m-%d %H:%M").weekday()#取出當天的為星期幾
        d = datetime.datetime.strptime(it['time'], "%Y-%m-%d %H:%M")
        if not d.strftime("%Y-%m-%d") in weekdays[str(weekday)]:  # 初始化
            weekdays[str(weekday)].append(d.strftime("%Y-%m-%d"))
        if not str(weekday) in weekdate:#初始化
            weekdate[str(weekday)] = it['value']
            weekcount[str(weekday)] = 1
            week_now_value[str(weekday)] = 0
        # 判斷是否為當週
        elif datetime.datetime.strptime(it['time'], "%Y-%m-%d %H:%M").isocalendar()[1] == current_time.isocalendar()[1]:
            week_now_value[str(weekday)] += it['value']
        weekdate[str(weekday)] += it['value']
        weekcount[str(weekday)] += 1

    # 計算平均用電
    if authority == "1":
        for i in range(len(weekdate)):
                if(int(i) != current_time.weekday() and int(i) != (current_time.weekday() - 1) and int(i) <= current_time.weekday()):
                    week_avg.append({'time': week[i], 'value': round((weekdate[str(i)] / (len(weekdays[str(i)]))if len(weekdays[str(i)]) else 0), 2),  'week_now_value': round(week_now_value[str(i)], 2)})
                # 當週還未到的設定值
                elif(int(i) > current_time.weekday()):
                    week_avg.append({'time': week[i], 'value': round(
                        (weekdate[str(i)] / (len(weekdays[str(i)]))if len(weekdays[str(i)]) else 0), 2)})
                # 設定即時用電值
                elif(int(i) == (current_time.weekday() - 1)):
                    week_avg.append({'time': week[i], 'value': round((weekdate[str(i)] / (len(weekdays[str(i)]))if len(weekdays[str(i)])
                    else 0), 2), "dashLengthLine": 5, 'week_now_value': round(week_now_value[str(i)], 2)})
                # 設定當天長條圖設定
                else:
                    week_avg.append({'time': week[i], 'value': round(
                        (weekdate[str(i)] / (len(weekdays[str(i)]))if len(weekdays[str(i)]) else 0), 2), 'week_now_value': round(week_now_value[str(i)], 2), 'lineColor': '#f17a7a', "dashLengthColumn": 5,
                    "alpha": 0.2,"additional": "(projection)"})
    else:
        for i in range(len(weekdate)):
                if(int(i) != current_time.weekday() and int(i) != (current_time.weekday() - 1) and int(i) <= current_time.weekday()):
                    week_avg.append({'time': week[i], 'value': round(
                        (weekdate[str(i)] / (weekcount[str(i)] / 96)if weekcount[str(i)] else 0), 2),  'week_now_value': round(week_now_value[str(i)], 2)})
                # 當週還未到的設定值
                elif(int(i) > current_time.weekday()):
                    week_avg.append({'time': week[i], 'value': round(
                        (weekdate[str(i)] / (weekcount[str(i)] / 96)if weekcount[str(i)] else 0), 2)})
                # 設定即時用電值
                elif(int(i) == (current_time.weekday() - 1)):
                    week_avg.append({'time': week[i], 'value': round((weekdate[str(i)] / (weekcount[str(i)] / 96)if weekcount[str(i)]
                                                                      else 0), 2), "dashLengthLine": 5, 'week_now_value': round(week_now_value[str(i)], 2)})
                # 設定當天長條圖設定
                else:
                    week_avg.append({'time': week[i], 'value': round(
                        (weekdate[str(i)] / (weekcount[str(i)] / 96)if weekcount[str(i)] else 0), 2), 'week_now_value': round(week_now_value[str(i)], 2), 'lineColor': '#f17a7a', "dashLengthColumn": 5,
                        "alpha": 0.2, "additional": "(projection)"})

    return jsonify(week_avg), 201
#
@api.route('/realtime_change', methods=['GET'])
def realtime_change():
    authority = request.args.get('authority', default="", type=str)
    req_customerID = request.args.get('CustomerID', default="D00001", type=str)
    year = request.args.get('year', default="", type=str)
    month = request.args.get('month', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    address = request.args.get('address', default="", type=str)
    channel = request.args.get('channel', default="", type=str)
    # 今天前一小時間
    current_time_from = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    current_time_to = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # 昨天同時段前一小時間
    yesterday_time_from = (datetime.datetime.now() - datetime.timedelta(days=1,hours=1)).strftime("%Y-%m-%d %H:%M")
    yesterday_time_to =((datetime.datetime.now() - datetime.timedelta(days=1))).strftime("%Y-%m-%d %H:%M")
    # 計算一小時內的值
    current_value = sum_value(db_query, authority, req_customerID, current_time_from, current_time_to, gateway_uid,address ,channel)
    yesterday_value = sum_value(db_query, authority, req_customerID, yesterday_time_from, yesterday_time_to, gateway_uid,address ,channel)
    # 計算差值
    diff_percent = ""
    diff_percent = diff_value(current_value, yesterday_value)#-(1.25-1.10/1.25)% string
    data_output = []
    data_output.append({'current_value': round(current_value, 2), 'yesterday_value': round(yesterday_value, 2), 'diff_percent': diff_percent})
    return jsonify(data_output), 201

@api.route('/base_demand_detection', methods=['GET'])
def base_demand_detection():
    authority = request.args.get('authority', default="", type=str)
    req_customerID = request.args.get('CustomerID', default="D00001", type=str)
    year = request.args.get('year', default="", type=str)
    month = request.args.get('month', default="", type=str)
    gateway_uid = request.args.get('gateway_uid', default="", type=str)
    address = request.args.get('address', default="", type=str)
    channel = request.args.get('channel', default="", type=str)

    if month == '12':
        req_dateTo = datetime.datetime(int(year)+1, 1, 1, 0, 0, 0)
    else:
        req_dateTo = datetime.datetime(int(year), int(month)+1, 1, 0, 0, 0)
    # time_range = datetime.timedelta(days = 60)#可調整計算基準值的時間
    # req_dateFrom =  (req_dateTo-time_range )
    # today_month = datetime.datetime.now().month
    req_dateFrom = datetime.datetime(int(year), int(month), 1, 0, 0, 0)
    req_dateFrom = datetime.datetime.strftime(datetime.datetime(int(year), int(month), 1, 0, 0, 0), "%Y-%m-%d %H:%M:%S")
    req_dateTo = datetime.datetime.strftime(req_dateTo, "%Y-%m-%d %H:%M:%S")
    this_month = datetime.datetime(int(year), int(month), 1, 0, 0, 0)


    start= time.time()#計算執行時間1
    # 計算筆數
    this_month_count = sum_electricity_data(db_query, authority, req_customerID, datetime.datetime.strftime(
        this_month, "%Y-%m-%d %H:%M:%S"), req_dateTo, gateway_uid, address, channel)
    # 電力資料存取
    result = sum_electricity_data(db_query, authority, req_customerID, req_dateFrom, req_dateTo, gateway_uid, address, channel)

    data_value = []
    count = len(result)
    for i in range(0, len(result['demands'])):
        data_value.append(result['demands'][i]['value'])
    if(len(data_value))==0:
        return jsonify(len(data_value)), 201
    step = 0.01  # 可調整
    target_percentage = 0.5  # 可調整
    base_demand = 0.0
    i = 0.0
    while(i < max(data_value)):
        i += step
        count = 0
        for j in range(0, len(data_value)):
            if(data_value[j] >= i):
                count += 1
        if(count / len(data_value) <= target_percentage):
            base_demand = i - step
            break
    data_output = {"base_demand": round(base_demand, 10), "count": len(this_month_count)}

    return jsonify(data_output), 201

# Sub function call
# return query data
def sum_electricity_data(db_query,authority, CustomerID, time_from, time_to,uid,address,channel):
    electricity_table = 'electricity_information'
    dataformat={}
    dataformat['demands'] =[]
    if(authority == "1" or authority == "0"):
        sql = "select datetime,demand_quarter from {} as d  where d.address ='{}' and d.channel = '{}'and  d.gateway_uid ='{}' and  datetime >='{}' and datetime <='{}' and  SECOND(datetime)=0 and MOD(MINUTE(datetime),15)=0  ORDER BY datetime ASC".format(
            "demand", address, channel,  uid,  time_from, time_to)
        db_query.execute(sql)
        electricity_data = db_query.fetchall()
        for data in electricity_data:
            dataformat['demands'].append({'datetime':data['datetime'],'value': data['demand_quarter']/1000,})
        return dataformat


def sum_value(db_query, authority, req_customerID, from_time, to_time, gateway_uid, address, channel):
    sumvalue = 0
    if(authority == "1" or authority == "0"):
        sql = "select datetime,demand_quarter from {} where gateway_uid='{}' and address='{}'and channel='{}' and datetime >='{}' and datetime <='{}'and  SECOND(datetime)=0 and  MOD(MINUTE(datetime),15)=0 ORDER BY datetime ASC".format(
            "demand",  gateway_uid, address, channel, from_time, to_time)
        db_query.execute(sql)
        realtime_data = db_query.fetchall()
        for idx in realtime_data:
            sumvalue += idx['demand_quarter']/1000


    return sumvalue

# return result(string) of diff(%) between today and yesterday
def diff_value(today, ex_time):

    diff_value = today - ex_time
    if(diff_value >= 0):
        diff_percent = "+" + \
            str(round(((today - ex_time) / ex_time)if ex_time else 0, 2))
    else:
        diff_percent = "-" + \
            str(round(((ex_time - today) / ex_time)if ex_time else 0, 2))
    return diff_percent


def foo2(x):
    return x['time']


