import json
import time
from . import serialformeter as serial
from . import mysql as daesql
from . import condition as condition
from .config import database_setting as dbconfig

def switch_power(group,status):
    print("intoSWITCH")
    """
    filex=open("flag.txt",'r',encoding='utf-8')
    a=filex.read()
    while(a==''):
        a=filex.read()

    a=int(a)
    filex.close()
    while(a!=0):

        filex=open("flag.txt",'r',encoding='utf-8')
        a=filex.read()
        while(a==''):
            a=filex.read()

        a=int(a)
        filex.close()

    filex=open("flag.txt",'w',encoding='utf-8')
    filex.write('1')
    filex.close()
    """
    ser = serial.TestModbusSerial()
    if status == 1:
        cmd = [1, 5, 1, group, 255, 0]
    elif status == 0:
        cmd = [1, 5, 1, group, 0, 0]
    else:
        raise Exception('status error')
    if group < 1 and group > 5:
        raise Exception('group error')
        #filex = json.load(file)
    """
    filex=open("flag.txt",'r',encoding='utf-8')
    a=filex.read()
    a=int(a)
    filex.close()
    print("before while")
    while(a!=2):
        #time.sleep(0.01)
        filex=open("flag.txt",'r',encoding='utf-8')
        a=filex.read()
        while(a==''):
            a=filex.read()
        a=int(a)
        filex.close()
        print("inWhile")
    print("beforeSer")
    """
    ser.write_command_to_modbus(cmd)
    """
    print("afterSer")
    filex=open("flag.txt",'w',encoding='utf-8')
    filex.write('0')
    filex.close()
    """
