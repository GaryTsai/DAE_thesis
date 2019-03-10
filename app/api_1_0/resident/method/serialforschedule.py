# encoding=utf-8
#! /usr/bin/python
import serial as pyserial
import sys
import gpio as GPIO
import logging
import time
import array
import threading
from .crc import get_crc16
from . import condition as condition


class TestModbusSerial:

    def __init__(self, port='/dev/ttyS2', tr_pin=6, baudrate=38400, timeout=0.5):
        super(TestModbusSerial, self).__init__()
        self._serial = pyserial.Serial(
            port=port, baudrate=baudrate, timeout=timeout)
        self._tr = tr_pin
        # self._cond=cond

        if not self._serial.isOpen():
            self._serial.open()
        GPIO.log.setLevel(logging.WARNING)
        GPIO.setwarnings(False)
#        GPIO.setmode(GPIO.BCM)
        GPIO.setup(tr_pin, GPIO.OUT)
        # self._serial.flushOutput()

    # 寫指令進入電表,並取得回應
    def write_command_to_modbus(self, data):
        """
        print("into modbus,flag=",flag.flag)
        while(flag.flag!=0):
            print("waiting...")
            time.sleep(0.01)
        flag.flag=1
      #  time.sleep(100)
        print("after modbus,flag=",flag.flag)
        time.sleep(100)
        """
        print("1")
        filex = open(
            "/home/var/www/dae-web/app/api_1_0/resident/method/config/device_flag.txt", 'r', encoding='utf-8')
        a = filex.read()
        while(a == ''):
            a = filex.read()
        a = int(a)
        filex.close()
        while(a != 0):
            filex = open(
                "/home/var/www/dae-web/app/api_1_0/resident/method/config/device_flag.txt", 'r', encoding='utf-8')
            a = filex.read()
            while(a == ''):
                a = filex.read()
            a = int(a)
            filex.close()
        filex = open(
            "/home/var/www/dae-web/app/api_1_0/resident/method/config/device_flag.txt", 'w', encoding='utf-8')
        filex.write('1')
        filex.close()
        print("jk2")
        # short delay
#        self._cond.acquire()
#        print("acquire")
        # time.sleep(0.02)
        ser = self._serial
        print("a")
        data_list = get_crc16(data)
        print("b")
        data_list = array.array('B', data_list)
        print("c")
        print(data_list)
        # write data to rs485
        GPIO.set(self._tr, 1)
        # time.sleep(.03)
        ser.write(data_list)
        ser.flush()
        # ser.flushInput()
        # get resposne
        GPIO.set(self._tr, 0)
        # time.sleep(.03)
        # 前三碼固定 後兩碼CRC
        words = data_list[5]  # words length
        length = 3 + words * 2 + 2
        print("get response")
        response = ser.read(length)  # send command to meter and get response
        # ser.flush()
        # Convert hex string to array
        print("testresponse=", response)
        response = array.array('B', response)

        time.sleep(0.01)

        filex = open(
            "/home/var/www/dae-web/app/api_1_0/resident/method/config/device_flag.txt", 'w', encoding='utf-8')
        filex.write('0')
        filex.close()

        # if length is not match then reload it
        if len(response) != length or data_list[0] != response[0] or data_list[1] != response[1]:
            # 資料錯誤就重新讀ii
            print("ERROR", response)
            ex = ser.read(1)
            time.sleep(0.03)
            """
            if(data_list[0] == response[1]):
                response.append(1)
                print("new rep=",response[1:])
                time.sleep(1)
                return response[1:]
            #return -1
            if(data_list[0] == response[2]):
                response.append(1)
                response.append(1)
                print("new rep2=",response[2:])
                time.sleep(1)
                return response[2:]
            """
            response = self.write_command_to_modbus(data[:-2])
      #  f=open('time.txt','w',encoding='UTF-8')
       # f.write(str(count)+'\n')
      #  f.close()
#        self._cond.release()
        return response

    def close(self):
        self._serial.close()
