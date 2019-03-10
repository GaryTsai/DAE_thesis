#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import csv
import MySQLdb
CHANNEL = 24
ADDRESS = 24
COUNT = 1
CIRCUIT = 24



db = MySQLdb.connect(host='127.0.0.1', db='lvami',
                     user='root', passwd='kDd414o6')
cur = db.cursor()
# datas = csv.reader('/electricity_information.csv')
with open(str('electricity_information.csv'), newline='',  encoding="utf8") as csvfile:
    datas = csv.reader(csvfile)
    for number in range(10, 11, 1):
        CHANNEL += 1
        ADDRESS += 1
        CIRCUIT += 1
        for data in datas:
            if data[0] == ("d000"+str(number)):
                sql = "INSERT INTO demand(`id`, `address`, `channel`, `model`, `datetime`, `demand_min`, `demand_quarter`, `R_value`, `S_value`, `T_value`, `Total_value`, `circuit`, `gateway_uid`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' );" % (
                    None, str(CHANNEL),  str(ADDRESS), data[0], data[1], None, data[2] * 1000,
                    None, None, None, None,  str(
                        CIRCUIT), 'lvami' + str(number) + '_data')
                print(data)
                try:
                    # Execute the SQL command
                    cur.execute(sql)
                    # Commit your changes in the database
                    db.commit()
                except BaseException as e:
                    print(e)

    # Rollback in case there is any error
