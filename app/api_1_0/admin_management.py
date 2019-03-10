from flask import jsonify, request
from . import api
import datetime
import json
import requests
from sqlalchemy import func, and_, or_, between, exists
from .. import db
from ..models import *
import pymysql
import ctypes,sys
import math
from .database import db
from datetime import timedelta
### 用電累積折線圖(含電費)
# @api.route('/data_accumulation_kWh', methods=['GET'])
@api.route('/data_total', methods=['GET'])
def add_for_total():
    conn = db.getConnection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    req_customerID = request.args.get('CustomerID', default="D00001", type=str)
    req_dateTo = datetime.datetime.now()
    # time_range = datetime.timedelta(days = 60)#可調整時間長度
    # req_dateFrom = datetime.datetime.now()-time_range
    req_dateFrom = datetime.datetime.now().replace(year=2017, month=11,day=1, hour=0, minute=15, second=0, microsecond=0)

    data_output = {}
    data_output['total'] = []
    user_count=1
    if datetime.date.today().month == 12:
        next_month = 1
        year = datetime.date.today().year + 1
        req_dateTo = datetime.datetime.now().replace(year=2017, month=next_month, day=1,
                                                     hour=0, minute=0, second=0)
    else:
        req_dateTo = datetime.datetime.now().replace(year=2017, month=12, day=1,
                                                     hour=0, minute=0, second=0)
    print('req_dateTo')
    print(req_dateTo)
    print('req_dateFrom')
    print(req_dateFrom)
    for acc in range(1,11):                   #here needs change, note that 1,11 means 1-10
        account = "d{num:05d}".format(num=acc)
        electricity_table = 'electricity_information'
        cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
            electricity_table, account, req_dateFrom, req_dateTo))
        result = cur.fetchall()
        # print(result)
        def monthBill5(add):
            bill = 0
            if (add['datetime'].month == 6) or (add['datetime'].month == 7) or (add['datetime'].month == 8) or (add['datetime'].month == 9):
                if add['value'] <= 120:
                    bill = add['value']*1.63
                elif add['value'] <= 330:
                    bill = (add['value']-120)*2.38+120*1.63
                elif add['value'] <= 500:
                    bill = (add['value']-330)*3.52+120*1.63+210*2.38
                elif add['value'] <= 700:
                    bill = (add['value']-500)*4.61+120*1.63+210*2.38+170*3.52
                elif add['value'] <= 1000:
                    bill = (add['value']-700)*5.42+120*1.63+210*2.38+170*3.52+200*4.61
                else:
                    bill = (add['value']-1000)*6.13+120*1.63+210*2.38+170*3.52+200*4.61+300*5.42
            else:
                if add['value'] <= 120:
                    bill = add['value']*1.63
                elif add['value'] <= 330:
                    bill = (add['value']-120)*2.10+120*1.63
                elif add['value'] <= 500:
                    bill = (add['value']-330)*2.89+120*1.63+210*2.10
                elif add['value'] <= 700:
                    bill = (add['value']-500)*3.79+120*1.63+210*2.10+170*2.89
                elif add['value'] <= 1000:
                    bill = (add['value']-700)*4.42+120*1.63+210*2.10+170*2.89+200*3.79
                else:
                    bill = (add['value']-1000)*4.83+120*1.63+210*2.10+170*2.89+200*3.79+300*4.42
            return bill

        def month2Bill5(add):
            bill = 0
            if (add['datetime'].month == 6) or (add['datetime'].month == 7) or (add['datetime'].month == 8) or (add['datetime'].month == 9):
                if add['value'] <= 240:
                    bill = add['value']*1.63
                elif add['value'] <= 660:
                    bill = (add['value']-240)*2.38+240*1.63
                elif add['value'] <= 1000:
                    bill = (add['value']-660)*3.52+240*1.63+420*2.38
                elif add['value'] <= 1400:
                    bill = (add['value']-1000)*4.61+240*1.63+420*2.38+340*3.52
                elif add['value'] <= 1000:
                    bill = (add['value']-1400)*5.42+240*1.63+420*2.38+340*3.52+400*4.61
                else:
                    bill = (add['value']-2000)*6.13+240*1.63+420*2.38+340*3.52+400*4.61+600*5.42
            else:
                if add['value'] <= 240:
                    bill = add['value']*1.63
                elif add['value'] <= 660:
                    bill = (add['value']-240)*2.10+240*1.63
                elif add['value'] <= 1000:
                    bill = (add['value']-660)*2.89+240*1.63+420*2.10
                elif add['value'] <= 1400:
                    bill = (add['value']-1000)*3.79+240*1.63+420*2.10+340*2.89
                elif add['value'] <= 2000:
                    bill = (add['value']-1400)*4.42+240*1.63+420*2.10+340*2.89+400*3.79
                else:
                    bill = (add['value']-2000)*4.83+240*1.63+420*2.10+340*2.89+400*3.79+600*4.42
            return bill


        time0730 = datetime.time(7,30,0)
        time2230 = datetime.time(22,30,0)
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
                bill = res['value']*1.65
            elif ((res['datetime'].month == 6) or (res['datetime'].month == 7)
                or (res['datetime'].month == 8) or (res['datetime'].month == 9)):

                if ((res['datetime'].weekday() == 0) or (res['datetime'].weekday() == 1) or
                        (res['datetime'].weekday() == 2) or (res['datetime'].weekday() == 3) or
                        (res['datetime'].weekday() == 4)):

                    if (((res['datetime'].hour > 7) and (res['datetime'].hour < 22))
                        or ((res['datetime'].hour == 7) and (res['datetime'].minute > 30))
                        or ((res['datetime'].hour == 22) and (res['datetime'].minute <= 30))):
                        bill = res['value']*4.19
                    else:
                        bill = res['value']*1.71
                else:
                    bill = res['value']*1.71
            else:

                if ((res['datetime'].weekday() == 0) or (res['datetime'].weekday() == 1) or
                        (res['datetime'].weekday() == 2) or (res['datetime'].weekday() == 3) or
                        (res['datetime'].weekday() == 4)):

                    if (((res['datetime'].hour > time0730.hour) and (res['datetime'].hour < time2230.hour))
                        or ((res['datetime'].hour == 7) and (res['datetime'].minute >= 30))
                        or ((res['datetime'].hour == 22) and (res['datetime'].minute <= 30))):
                        bill = res['value']*4.01
                    else:
                        bill = res['value']*1.65
                else:
                    bill = res['value']*1.65
            return bill

        addresult = []
        for i in result:
            addresult.append({'datetime':i["datetime"],'value': i["value"], 'mor' : 0,'night' : 0,
                              'bill5':0,'bill6':0})
        ###早晚總用電度數
        print('早晚總用電度數', addresult)
        def count_second(cs):
            t = ((cs['datetime'].hour*60) + cs['datetime'].minute)*60
            return t
        t = 0
        mor = 0
        night = 0
        k = 0
        #morning0600 = 6*60*60 = 21600
        #night1800 = 18*60*60 =64800
        while k < len(result):
            cs = count_second(result[k])
            if (cs >= 21600 and cs< 64800) :
                mor += result[k]['value']
                k += 1
            elif ( cs >= 64800 or cs < 21600) :
                night += result[k]['value']
                k += 1
            else :
                print('itswrong')
                break
        # addresult[0]['bill6'] = monthBill6(result[0])
        d = 1
        while d < len(result):
            addresult[d]['value'] += addresult[d-1]['value']
            # if addresult[d]['value'] <= 2000:
            #     addresult[d]['bill6'] = monthBill6(result[d])
            # else:
            #     break
            d += 1
        if d < len(addresult) and addresult[d]['value'] > 2000:
            tem = []
            tem.append({'datetime':addresult[d]['datetime'],'value':addresult[d]['value']-2000})
            # addresult[d]['bill6'] = monthBill6(tem[0]) + (tem[0]['value'])*0.91
            d += 1
            while d < len(addresult):
                addresult[d]['value'] += addresult[d-1]['value']
                # addresult[d]['bill6'] = monthBill6(result[d]) + result[d]['value']*0.91
                d += 1
        d = d-1

        # j = 0
        # while j < len(addresult):
        #     if len(addresult) <= 32*24*4:
        #         addresult[j]['bill5'] = monthBill5(addresult[j])
        #     else:
        #         addresult[j]['bill5'] = month2Bill5(addresult[j])
        #     j += 1


        # a = 1
        # while a < len(addresult):
        #     addresult[a]['bill6'] += addresult[a-1]['bill6']
        #     a += 1

        # a = 0
        # while a < len(addresult):
        #     addresult[a]['bill6'] = addresult[a]['bill6'] + (int(len(addresult)/(31*24*4+1))+1)*75
        #     a += 1


        final_data_output = {}
        final_data_output['demands'] = []

        for data in addresult:
            final_data_output['demands'].append({'time': data["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                                                'value': round(data["value"],0)})
        print('ADMIN', final_data_output['demands'])
        # max_power = final_data_output['demands'][len(final_data_output['demands'])-1]['value']
        # max_bill5 = final_data_output['demands'][len(final_data_output['demands'])-1]['bill5']
        # max_bill6 = final_data_output['demands'][len(final_data_output['demands'])-1]['bill6']

        # if(type(req_dateTo) != type(final_data_output['demands'][len(final_data_output['demands'])-1]['time']) ):
        #     req_dateTo=req_dateTo.strftime("%Y-%m-%d %H:%M")

        # if (final_data_output['demands'][len(final_data_output['demands'])-1]['time']<req_dateTo):
        #     time_end = final_data_output['demands'][len(final_data_output['demands'])-1]['time']
        #     time_end= datetime.datetime.strptime(time_end, '%Y-%m-%d  %H:%M:%S')
        #     req_dateTo= datetime.datetime.strptime(req_dateTo, '%Y-%m-%d  %H:%M')
        #     while (time_end<req_dateTo):
        #             time_end = time_end + timedelta(minutes=15)
        #             final_data_output['demands'].append({'time':datetime.datetime.strftime(time_end , '%Y-%m-%d  %H:%M:%S')})

        if(user_count==10):
            data_output['total'].append({'account' : account,'max_powernumber':500,
                                     'max_power_morning':round(mor,0),'max_power_night':round(night,0),
                                     "bullet":"/static/img/D000"+str(10)+".png"})
        else:
            data_output['total'].append({'account' : account,'max_powernumber':0,
                                     'max_power_morning':round(night,0),'max_power_night':round(mor,0),
                                 "bullet":"/static/img/D0000"+str(user_count)+".png"})
        user_count+=1


    return jsonify(data_output['total']), 201


@api.route('/data_ten_users', methods=['GET'])
def post_request_ten_users():
    conn = db.getConnection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    req_customerID = "d00001"
    # Use = request.args.get('CustomerID', default="D00001", type=str)
    # req_dateTo = datetime.datetime.now()
    # # time_range = datetime.timedelta(days = 1)#可調整時間長度
    # # req_dateFrom = datetime.datetime.now()-time_range
    req_dateFrom = datetime.datetime.now().replace(
        year=2017, day=1, hour=0, minute=15, second=0, microsecond=0)

    if datetime.date.today().month == 12:
        next_month = 1
        year = datetime.date.today().year + 1
        req_dateTo = datetime.datetime.now().replace(year=2017, month=next_month, day=1,
                                                     hour=0, minute=0, second=0)
    else:
        req_dateTo = datetime.datetime.now().replace(year=2017, month=12, day=1,
                                                     hour=0, minute=0, second=0)

    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_1 = cur.fetchall()

    req_customerID = "d00002"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_2 = cur.fetchall()

    req_customerID = "d00003"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_3 = cur.fetchall()

    req_customerID = "d00004"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_4 = cur.fetchall()

    req_customerID = "d00005"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_5 = cur.fetchall()

    req_customerID = "d00006"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_6 = cur.fetchall()

    req_customerID = "d00007"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_7 = cur.fetchall()

    req_customerID = "d00008"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
         'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_8 = cur.fetchall()

    req_customerID = "d00009"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_9 = cur.fetchall()

    req_customerID = "d00010"
    cur.execute("select datetime,value from {} where user_id ='{}' and datetime >='{}' and datetime <='{}' ORDER BY datetime ASC".format(
        'electricity_information', req_customerID, req_dateFrom, req_dateTo))
    result_10 = cur.fetchall()

    result = []
    for i in result_1:
        result.append({'datetime': i["datetime"],
                       'd00001': i["value"], 'd00002': 0, 'd00003': 0, 'd00004': 0, 'd00005': 0,
                       'd00006': 0, 'd00007': 0, 'd00008': 0, 'd00009': 0, 'd00010': 0})
    j = 0
    while j < len(result):
        result[j]['d00002'] = result_2[j]['value']
        result[j]['d00003'] = result_3[j]['value']
        result[j]['d00005'] = result_5[j]['value']
        result[j]['d00006'] = result_6[j]['value']
        result[j]['d00007'] = result_7[j]['value']
        result[j]['d00008'] = result_8[j]['value']
        result[j]['d00009'] = result_9[j]['value']
        result[j]['d00010'] = result_10[j]['value']
        j += 1
    j = 0
    # while j < len(result_4):
    #   result[j]['d00004'] = result_4[j]['value']
    # j += 1
    final_data_output = {}
    final_data_output['demands'] = []
    for data in result:
        final_data_output['demands'].append({"time": data["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                                             "d00001": data["d00001"], "d00002": data["d00002"],
                                             "d00003": data["d00003"], "d00004": data["d00004"],
                                             "d00005": data["d00005"], "d00006": data["d00006"],
                                             "d00007": data["d00007"], "d00008": data["d00008"],
                                             "d00009": data["d00009"], "d00010": data["d00010"]})

    return jsonify(final_data_output['demands']), 201
