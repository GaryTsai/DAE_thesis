# encoding=utf-8
#! /usr/bin/python

import threading
import time
import requests
import json
import sys

from . import common as common
from . import serialformeter as serial
from . import mysql as daesql
from . import condition as condition
from .config import database_setting as dbconfig
#from apscheduler.schedulers.background import BackgroundScheduler

class Meter(threading.Thread):
    # /dev/ttyS1 for Nanopi RS485, tr pin is 6
    def __init__(self, cond, port="/dev/ttyS1", tr_pin=6, baudrate=9600):
        super(Meter, self).__init__()
        global status, unloading_list, last_number
        unloading_list = []
        status = 0
        last_number = 0
        self._serial = serial.TestModbusSerial(port=port, tr_pin=tr_pin, baudrate=baudrate)
        self._cond = cond
        self._dbh = daesql.MySQL(dbconfig.mysql_config)


    # Read data from meter
    def run(self):
        #self._cond.acquire()
        print("today test")

        while True:
            #try:
            print("today test")
            config = common.get_server_settings()
            """
            filex=open("../../flag.txt",'r',encoding='utf-8')
            print("testflag")
            a=filex.read()
            
            while(a==''):
                a=filex.read()
            
            print("flag=",a)
            a=int(a)
            filex.close()
            while(a!=0):
                time.sleep(0.5)
                filex=open("../../flag.txt",'r',encoding='utf-8')
                print("testflag2")
                a=filex.read()
                filex.close()
                a=int(a)
                if(a==0):
                    break;
                if(a==1):
                    filex=open("../../flag.txt",'w',encoding='utf-8')

                    filex.write('2')
                    filex.close()

                if(a==3):
                    filex=open("../../flag.txt",'w',encoding='utf-8')

                    filex.write('4')
                    filex.close()
            """
#            self._cond.acquire()
            print("config=",config)
            #record_gap = int(config['record_gap'])
            self.read_data_from_meter()
#            self._cond.release()
            #time.sleep(record_gap)

            #except KeyboardInterrupt:
            #    print("Keyboard Interrupt.")

            #except:
            #    print("Unexcepted error: {0}".format(sys.exc_info()[0]))

        self._dbh.close()
        print("close*100")
        self._serial.close()


    # 讀取資料並作處理
    def read_data_from_meter(self):
        global status, unloading_list
        # 取得現在的電表開機設定
        dbh = self._dbh
        state = "SELECT * FROM {0} ORDER BY {1} DESC LIMIT 1".format("demand_settings", "id")
        print("state=",state)
        demand_settings = dbh.query(state)
        print("demand=",demand_settings)
        
        # if not foudn
        if len(demand_settings) != 1:
            common.log("demand settings not found.")
            sys.exit()

        settings = demand_settings[0]
        max_demand = settings['value'] # 最大需量
        upper_limit_demand = settings['value_max'] # 高限
        lower_limit_demand = settings['value_min'] # 低限
        load_off_gap = settings['load_off_gap'] # 卸載延遲時間
        reload_delay = settings['reload_delay'] # 復歸延遲時間
        cycle = settings['cycle'] # 計算週期 default 15min
        mode = settings['mode'] # 卸載模式
        group = settings['groups'] # 群組

        # demand value
        values = 0
        print("test")
        values = self.read_demand()
        print("values=",values)

        # 如果需量超過高限，則啟動卸載機制，保證需量不會超過
        if status == 0 or status == 2:
            if float(values) >= float(upper_limit_demand):
                status = 1
                self.unload_devices(mode, upper_limit_demand, load_off_gap)

        # 如果需量已經低於低限，則復歸裝置
        if status == 1:
            if float(values) < float(lower_limit_demand):
                status = 2
                self.revert_devices(mode, reload_delay)

   
    def check_to_revert(self, value, demand):
        global status

        if float(value) < float(demand):
            status = 1

            return True


    def unload_devices(self, mode, upper_limit_demand, delay):
        global unloading_list, last_number
        offload_list=[]
        dbh = self._dbh
        state = "SELECT * FROM {0} ORDER BY {1}".format("offloads","id")
        print("state=",state)
        result = dbh.query(state)
        for row in result:
            offload_list.append(row['offload_available'])
        print("offlist",offload_list) 
        #time.sleep(5)   
            
        if mode == '先卸先復歸' or mode == '先卸一起復歸' or mode == '先卸後復歸':
            time.sleep(0.1)
            for i in range(0, 4):
                time.sleep(0.1)
                if offload_list[i]=="true":
                    time.sleep(0.1)
                    value = self.switch_power(i, 0)
                    unloading_list.append(i)
                    isOK = self.check_to_revert(value, upper_limit_demand)

                    if isOK:
                        break

                    time.sleep(delay)


        elif mode == '循環先卸一起復歸' or mode == '循環先卸先復歸' or mode == '循環先卸後復歸':
            time.sleep(0.1)
            for i in range(0, 4):
                time.sleep(0.1)
                index = 4 - last_number if (last_number + i + 1) >= 5 else last_number + i
                if offload_list[index]=="true":
                    time.sleep(0.1)
                    value = self.switch_power(index, 0)
                    unloading_list.append(index)
                    isOK = self.check_to_revert(value, upper_limit_demand)

                    if isOK:
                        break

                    time.sleep(delay)


    def revert_devices(self, mode, delay):
        global unloading_list, last_number

        last_number = 0
        length = len(unloading_list)
        index = 0

        if length == 0:
            print("nothing")
            """
            offload_list=[]
            dbh = self._dbh
            state = "SELECT * FROM {0} ORDER BY {1}".format("offloads","id")
            print("state=",state)
            result = dbh.query(state)
            for row in result:
                offload_list.append(row['offload_available'])    
            for i in range(0, 4):
                if offload_list[index]=="true":
                    self.switch_power(i, 1)
                    time.sleep(delay)
            """

        elif mode == '先卸先復歸' or mode == '循環先卸先復歸':
            for i in range(0, length):
                index = unloading_list[0]
                value = self.switch_power(index, 1)
                unloading_list.remove(index)
                time.sleep(delay)

        elif mode == '先卸一起復歸' or mode == '循環先卸一起復歸':
            for i in range(0, length):
                index = unloading_list[0]
                value = self.switch_power(index, 1)
                unloading_list.remove(index)

        elif mode == '先卸後復歸' or mode == '循環先卸後復歸':
            for i in range(0, length):
                index = unloading_list[-1]
                value = self.switch_power(index, 1)
                unloading_list.remove(index)
                time.sleep(delay)

        last_number = index
        status = 0


    def switch_power(self, group=1, status=0, check=True):
        ser = self._serial

        if status == 1:
            cmd = [1, 5, 1, group, 255, 0]
        elif status == 0:
            cmd = [1, 5, 1, group, 0, 0]
        else:
            raise Exception('status error')

        if group < 1 and group > 5:
            raise Exception('group error')
        
        # close switch power
        ser.write_command_to_modbus(cmd)

        if check:
            value = self.read_demand()

            return value

        return False


    # 讀取 PM 210 的資料
    def read_demand(self):
        dbh = self._dbh
        serial = self._serial
        meter_settings = dbh.query_machine_settings()
        demand = 0
        print("test3")
        # meter settings loop
        for config in meter_settings:
            print("test4")
            model = config['model']
            address = config['address']
            ch = config['ch']
            circuit=config['circuit']
            uid=config['uid']
            print("uid=",uid)
            # 從電表規格書中取得位址
            cursor = dbh.get_meter_table(model)
            databuff = []
            output = []

            # 根據位址依序讀取資料
            for row in cursor:
                print("11")
                meter_type = row['type']
                start_address = row['start_address']
                table_length = row['table_length']
                channel_numbers = row['channel_numbers']
                channel_length = row['channel_length']
                phase_numbers = row['phase_numbers']
                phase_length = row['phase_length']
                point_array = [row['point_1'], row['point_2'], row['point_3'], row['point_4'], row['point_5'], row['point_6'], row['point_7']]
                point_number = 0
                for p in point_array:
                    print("test15")   
                    if p is None:
                        break

                    point_number = point_number + 1

                unit_array = [row['unit_1'], row['unit_2'], row['unit_3'], row['unit_4'], row['unit_5'], row['unit_6'], row['unit_7']]
                unit_number = 0
                for u in unit_array:
                    print("test16") 
                    if u is None:
                        break

                    unit_number = unit_number + 1

                description_array = row['description_array'].split(',')
                chinint=int(ch)
                position = int(start_address) + ((chinint - 1) * channel_length)
                length = phase_numbers * phase_length
                code_h = int(position / 256)
                code_l = int(position % 256)

                if type(self) is Meter and self._cond.is_wait:
                    self._cond.wait()
                
                #length=int(length/2)
                addressinint=int(address)
                command = [addressinint, 3, code_h, code_l, 0, length]
                #command = [1, 3, 0, 52, 0, 2]
                print("command",command) 
                #print("command",command) 
               
                response = self._serial.write_command_to_modbus(command)
                
                if len(response) > 0 and response[0] != 1:
                    common.log("{0}ERROR{0}".format("*ABC*" * 100), response)
                    common.log("AAA", ("B" * 600))
                    #for error
                    #demand=0
                    #return demand

                common.log("modbus response", response)
                print("test13")
                # parse data loop
                for i in range(3, len(response) - 2, phase_length * 2):
                    print("test12")
                    LH = response[i]
                    LL = response[i + 1]
                    HH = response[i + 2]
                    HL = response[i + 3]
                    index = int((i - 3) / (phase_length * 2)) # description array index
                    unit_index = index if unit_number > 1 else 0
                    point_index = index if point_number > 1 else 0
                    #¥¿½T»ݶqŪ¨úOB
                    total = round(int(LH * 256 + LL + HH * 256 * 256 * 256 + HL * 256 * 256) * point_array[point_index], 2)
                    #total = round(int(LH * 256 + LL) * point_array[point_index], 2)
                    total = total * 0.001
                    # json format
                    temp = {
                        'datetime': common.get_now(),
                        'address': address,
                        'channel': ch,
                        'register': [code_h, code_l + i - 3],
                        'unit': unit_array[unit_index],
                        'value': total,
                        'description': description_array[index]
                    }
                    output.append(temp)
                # end for parse data loop
            # end for cursor loop
            print("test2")
            datas =  []
            for row in output:
                des = row['description'].strip()
                if des == 'Pd1' or des == 'Pd15' or des == 'R Phase P (RP)' or des == 'S Phase P (SP)' or des == 'T Phase P (TP)' or des == 'Combined Phase P (ALL P)':
                    print("*"*20)
                    print(des);
                    print("*"*20)
                    datas.append(row)


            # save to local database
            print("value:",datas[0]['value'])
            print('uid=',uid)
            print('model=',model)
            print('model type=',type(model))
            state = "INSERT INTO {0} (demand_quarter, circuit, datetime,demand_min,channel,address,model,gateway_uid) VALUES ({1}, {2}, {3},{4},{5},{6},'{7}','{8}')".format('demand', datas[0]['value'], circuit, 'now()',datas[1]['value'],chinint,address,model,uid)

            print('state=',state)
            result = dbh.execute(state)

            print("***Q*WE*QW*EQ*WE*QW*E*"*300)

        demand = datas[0]['value']
        common.log("aaa", demand)
        print("test6")
        # demand
        api_json =  []
        CTRT = 0.001
        api_data = {
            'gateway_uid': uid,
            'address': address,
            'channel': ch,
            'model': model,
            'datetime': common.get_now(),
            'demand_min': {
                'value': datas[1]['value'],
                'unit': datas[1]['unit']
            },
            'demand_quarter': {
                'value': datas[0]['value'],
                'unit': datas[0]['unit']
            },
            
            'instantaneous_power': [{
                'tag': 'R',
                'value': datas[2]['value'] * CTRT,
                'unit': datas[2]['unit']
            }, {
                'tag': 'S',
                'value': datas[3]['value'] * CTRT,
                'unit': datas[3]['unit']
            }, {
                'tag': 'T',
                'value': datas[4]['value'] * CTRT,
                'unit': datas[4]['unit']
            }, {
                'tag': 'Total',
                'value': datas[5]['value'] * CTRT,
                'unit': datas[5]['unit']
            }]
            
            
        }
        api_json.append(api_data)
        # write to last data note
        try:
            file = open("last_data.json", 'w', encoding='utf-8')
            file.write(json.dumps(api_json))
            file.close()

        except:
            print("Unexcepted error: {0}".format(sys.exc_info()[0]))
            raise
        #response = common.post_data_to_server(api_json)

        # end for meter settings
        print("demand=",demand)
        time.sleep(1)
        return demand
