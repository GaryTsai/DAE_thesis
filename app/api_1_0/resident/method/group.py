import json
import time
from . import serialforschedule as serial2
from . import serialforset as serialset
from . import mysql as daesql
from . import condition as conditioni
from .config import database_setting as dbconfig
from . import mcu 

def set_group(ID):
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('MBUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])

    ser = serialset.TestModbusSerial()

    """
    read data from mysql
    """
    dbh=daesql.MySQL(dbconfig.mysql_config)
    state = "SELECT group_num FROM `group` WHERE id={0}".format(ID)
    result = dbh.query(state)
    group_num=result[0]['group_num'] 
    state = "SELECT * FROM {0} WHERE group_id= {1} ".format("node",ID)
    result = dbh.query(state)
    print("result=",result)    
    rule={}
    state={}
    for row in result:
        add=row['gateway_address']
        node=row['node']
        node=1<<(node-1)
        if(rule.__contains__(add)):
            a=rule[add]
            a=a+node
            rule[add]=a
        else:
            rule[add]=node
    key=rule.keys()
    
    for a in key:
        b=rule.get(a)
        if (int(a)!=3):

            cmd=[int(a),16,40,group_num*2,0,2,4,group_num,b,1,0]
        elif(int(a)==3):
            cmd=[3,16,80,group_num*4,0,4,8,group_num,b,1,0,80,80,80,80]
        print("set cmd=",cmd) 
        ser.write_command_to_modbus(cmd)
        time.sleep(0.1)
        
    
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('BUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
    time.sleep(0.03)

def set_scene(scene_number):
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('MBUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])

#    time.sleep(10)
    ser = serialset.TestModbusSerial()

    """
    read data from mysql
    """
    dbh=daesql.MySQL(dbconfig.mysql_config)
    state = "SELECT * FROM scenes WHERE scene_number={0}".format(scene_number)
    result = dbh.query(state)
    rule={}
    state={}
    nstate=[0,0,0,0]
    for row in result:

        node=row['node']
        node_state=row['node_state'] 
        state2 = "SELECT * FROM {0} WHERE id= {1} ".format("node",node)
        result2 = dbh.query(state2)
    
        for row2 in result2:
            add=row2['gateway_address']
            node=row2['node']
            mtype=row2['model_type']
            nnode=1<<(node-1)
            if(rule.__contains__(add)):
                a=rule[add]
                a=a+nnode
                rule[add]=a
                if(mtype==0):
                    nstate[(node-1)]=int(node_state)
                    a=state[add]
                    a=a+nnode
                    state[add]=a
                elif(node_state=='ON'):
                    a=state[add]
                    a=a+nnode
                    state[add]=a
            else:
                rule[add]=nnode
                state[add]=0
                if(mtype==0):
                    nstate[(node-1)]=int(node_state)
                    state[add]=nnode
                elif(node_state=='ON'):
                    state[add]=nnode
                
                
        
    print("final=",rule)
    print("state for 4x=",nstate)
    print("state for 3x=",state)
    key=rule.keys()
    local=(scene_number+16)*2
    scene_number=scene_number+63
    for a in key:
        b=rule.get(a)
        
        c=state.get(a)
        if (int(a)!=3):
            cmd=[int(a),16,40,local,0,2,4,scene_number,b,c,0]
        elif(int(a)==3):
            cmd=[3,16,80,local*2,0,4,8,scene_number,b,c,0,nstate[0],nstate[1],nstate[2],nstate[3]]
        
        ser.write_command_to_modbus(cmd)
        time.sleep(0.1)
        
    
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('BUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
    time.sleep(0.03)

def delete_group(ID):
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('MBUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])

    ser = serialset.TestModbusSerial()

    """
    read data from mysql
    """
    dbh=daesql.MySQL(dbconfig.mysql_config)
    state = "SELECT group_num FROM `group` WHERE id={0}".format(ID)
    result = dbh.query(state)
    group_num=result[0]['group_num']
    state = "SELECT * FROM {0} WHERE group_id= {1} ".format("node",ID)
    result = dbh.query(state)
    rule={}
    state={}
    for row in result:
        add=row['gateway_address']
        node=row['node']
        node=1<<(node-1)
        if(rule.__contains__(add)):
            a=rule[add]
            a=a+node
            rule[add]=a
        else:
            rule[add]=node
    key=rule.keys()
    for a in key:
        b=rule.get(a)
        if (int(a)!=3):

            cmd=[int(a),16,40,group_num*2,0,2,4,0,0,0,0]
        elif(int(a)==3):
            cmd=[3,16,80,group_num*4,0,4,8,0,0,0,0,0,0,0,0]
        print("delete cmd=",cmd)
        ser.write_command_to_modbus(cmd)
        time.sleep(0.1)


    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('BUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
    time.sleep(0.03)
    

def delete_scene(scene_number):
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('MBUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])

    ser = serialset.TestModbusSerial()

    """
    read data from mysql
    """
    dbh=daesql.MySQL(dbconfig.mysql_config)
    state = "SELECT * FROM scenes WHERE scene_number={0}".format(scene_number)
    result = dbh.query(state)
    rule={}
    state={}
    nstate=[0,0,0,0]
    for row in result:

        node=row['node']
        node_state=row['node_state'] 
        state2 = "SELECT * FROM {0} WHERE id= {1} ".format("node",node)
        result2 = dbh.query(state2)
    
        for row2 in result2:
            add=row2['gateway_address']
            node=row2['node']
            mtype=row2['model_type']
            nnode=1<<(node-1)
            if(rule.__contains__(add)):
                pass
            else:
                rule[add]=0
                state[add]=0
        
    key=rule.keys()
    local=(scene_number+16)*2
    scene_number=scene_number+63
    for a in key:
        b=rule.get(a)
        
        c=state.get(a)
        if (int(a)!=3):
            cmd=[int(a),16,40,local,0,2,4,scene_number,b,c,0]
        elif(int(a)==3):
            cmd=[3,16,80,local*2,0,4,8,scene_number,b,c,0,nstate[0],nstate[1],nstate[2],nstate[3]]
        
        ser.write_command_to_modbus(cmd)
        time.sleep(0.1)
        
    
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('BUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
    time.sleep(0.03)

def switch_power(num,group,status):
    if group < 1 or group > 4:
        raise Exception('group error')
    ser = serial2.TestModbusSerial()
    if status == 'ON':
        group=group-1+(num-1)*8
        cmd = [1, 5, 1, group, 255, 0]
        ser.write_command_to_modbus(cmd)
    elif status == 'OFF':
        group=group-1+(num-1)*8
        cmd = [1, 5, 1, group, 0, 0]
        ser.write_command_to_modbus(cmd)
    else:
        mcuser=mcu.MCUinitialize()
        mcuser.mcu_process('MBUS')
        mcuser.open_serial()
        mcuser.send_data(mcuser.data_MCU_read_mode)
        a = mcuser.read_data().hex()
        print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
        
        status=int(status)
        cmd = [num, 16, 240, 2, 0, 1,2,group,status]
        ser.write_command_to_modbus(cmd)
        time.sleep(0.1)
        
        mcuser=mcu.MCUinitialize()
        mcuser.mcu_process('BUS')
        mcuser.open_serial()
        mcuser.send_data(mcuser.data_MCU_read_mode)
        a = mcuser.read_data().hex()
        print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
        time.sleep(0.03)
        

"""

def switch_percent(num,group,status):
    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('MBUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
    
    ser = serial2.TestModbusSerial()
    if status >=-1 and status <=100:
        cmd = [num, 16, 240, 2, 0, 1,2,group,status]
    else:
        raise Exception('status error')
    if group < 1 or group > 4:
        raise Exception('group error')


    ser.write_command_to_modbus(cmd)


    mcuser=mcu.MCUinitialize()
    mcuser.mcu_process('BUS')
    mcuser.open_serial()
    mcuser.send_data(mcuser.data_MCU_read_mode)
    a = mcuser.read_data().hex()
    print([str(int(a[i:i + 2], 16)) for i in range(0, len(a), 2)])
"""
def switch_group(group,status):
    ser = serial2.TestModbusSerial()
    if status == 'ON':
        cmd = [1, 5, 0, group, 255, 0]
    elif status == 'OFF':
        cmd = [1, 5, 0, group, 0, 0]
    else:
        raise Exception('status error')
    if group < 1 and group > 63:
        raise Exception('group error')
    ser.write_command_to_modbus(cmd)
def switch_scene(scene,status):
    scene=scene+63
    ser = serial2.TestModbusSerial()
    if status == 'ON':
        cmd = [1, 5, 0, scene, 255, 0]
    elif status == 'OFF':
        cmd = [1, 5, 0, scene, 0, 0]
    else:
        raise Exception('status error')
    if scene < 64 and scene > 127:
        raise Exception('scene error')
        #filex = json.load(file)
    ser.write_command_to_modbus(cmd)

