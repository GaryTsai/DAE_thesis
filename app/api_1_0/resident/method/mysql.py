# encoding=utf-8
#! /usr/bin/python

import time
import sqlite3
import sys
import pymysql.cursors
import json
from .config.path import *


class MySQL:
    def __init__(self, dbconfig):
        super(MySQL, self).__init__()
        self.connection = pymysql.connect(host=dbconfig['host'],
                                          user=dbconfig['user'],
                                          password=dbconfig['password'],
                                          db=dbconfig['db'],
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

    def execute(self, sql):
        connection = self.connection
        cursor = connection.cursor()
        result = cursor.execute(sql)
        connection.commit()
        response = {
            'result': result,
            'last_id': cursor.lastrowid
        }

        return response

    def query(self, state):
        connection = self.connection
        with connection.cursor() as cursor:
            cursor.execute(state)
            result = cursor.fetchall()

        return result

    def query_machine_settings(self):
        time.sleep(.05)
        conn = self.connection
        cursor = conn.cursor()
        table_name = "setting"
        state = "SELECT * FROM {0}".format(table_name)
        cursor.execute(state)
        result = cursor.fetchall()
        output = []

        for row in result:
            model = row['model']
            # 查詢機器代碼
            code = self.query_codes(model)
            # 機器代碼舉例為4,60，拆開各自存放
            code_split = code.split(',')
            code_h = int(code_split[0])
            code_l = int(code_split[1])
            address = row['address']
            ch = row['ch']
            speed = row['speed']  # baudrate
            uid = row['gateway_uid']
            baudrate = self.convert_speed_to_number(speed)
            circuit = row['circuit']
            setting = {
                'model': model,
                'speed': speed,
                'code_h': code_h,
                'code_l': code_l,
                'address': address,
                'ch': ch,
                'baudrate': baudrate,
                'circuit': circuit,
                'uid': uid

            }
            output.append(setting)

        return output

    # 將baudrate轉換成台科電的規定格式 1-1200,2-2400,3-4800,4-9600
    def convert_speed_to_number(self, spped):
        if spped == 1200:
            return 1

        if spped == 2400:
            return 2

        if spped == 4800:
            return 3

        if spped == 9600:
            return 4

    # 查詢電表型號的代碼
    def query_codes(self, model):
        """
        conn = self.connection
        cursor = conn.cursor()
        table_name = 'codes'
        state = "SELECT * FROM {0} WHERE {1}='{2}'".format(table_name, 'model', model)
        cursor.execute(state)
        result = cursor.fetchone()
        """
        codes = open(
            "/home/var/www/dae-web/app/api_1_0/resident/method/config/input_code_data.json", 'r', encoding='utf-8')
        codes = codes.read()
        codes = json.loads(codes)
        for temp in codes:
            if(temp['model'] == model):
                return temp['code']

    # 取得電表的位址表
    def get_meter_table(self, model):
        # sqlite
        conn = sqlite3.connect(METER_DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        machine_split = model.split('-')
        table_name = machine_split[0]
        state = "SELECT * FROM {0}".format(table_name)
        cursor = conn.execute(state)

        return cursor

    def close(self):
        self.connection.close()
