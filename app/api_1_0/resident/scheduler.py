from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from datetime import timedelta
import json
import time
import method.group as switch
import method.forSunSetRise as sun
import method.mysql as daesql
import method.config.database_setting as dbconfig
import method.Mqttforschedule as mqtt


def day():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    today = time.strftime("%Y-%m-%d")
    dbh = daesql.MySQL(dbconfig.mysql_config)
    state = "SELECT * FROM gateway "
    result = dbh.query(state)
    lng = result[0]['lng']
    lat = result[0]['lat']
    ID = result[0]['id']
    sunrise, sunset = sun.sun_time(float(lng), float(lat))
    state = "UPDATE gateway SET sunrise='%s',sunset='%s' WHERE id='%d'" % (
        str(sunrise), str(sunset), ID)
    result = dbh.execute(state)
    time.sleep(1)


def job():
    today = time.strftime("%Y-%m-%d")
    dbh = daesql.MySQL(dbconfig.mysql_config)
    state = "SELECT * FROM gateway "
    result = dbh.query(state)
    a = result[0]['sunrise']
    b = result[0]['sunset']
    state = "SELECT * FROM festival WHERE date='%s'" % (today)
    result = dbh.query(state)
    if len(result) == 0:
        Type = 'weekday'
    else:
        Type = 'holiday'

    state = "SELECT * FROM schedule WHERE schedule_table='%s'" % (Type)
    result = dbh.query(state)
    i = 0
    for row in result:
        setting = row['setting']
        if setting == 'false':
            continue
        x = timedelta(seconds=i)
        ID = row['group_id']
        stime = row['control_time']
        onoff = row['schedule_group_state']
        state = "SELECT * FROM node WHERE group_id='%d'" % (ID)
        result2 = dbh.query(state)
        nodelist = []
        modeltype = result2[0]['model_type']
        for temp in result2:
            node = temp['id']
            nodelist.append(node)
        if (stime is None):
            stime = row['control_time_of_sun']
            if(stime == 'sunrise'):
                stime = a
            else:
                stime = b
        stime = stime + x
        state = "SELECT * FROM `group` WHERE id='%d'" % (ID)
        result2 = dbh.query(state)
        stime = str(stime)
        stime = today + ' ' + stime
        group_num = int(result2[0]['group_num'])
        scheduler.add_job(switch.switch_group, 'date',
                          run_date=stime, args=[group_num, onoff])
        scheduler.add_job(update, 'date', run_date=stime, args=[
                          ID, group_num, onoff, nodelist, modeltype])
        i = i + 1


def update(ID, num, upstate, ndlist, mdtype):
    if upstate == 'ON':
        numberstate = 100

    else:
        numberstate = 0
    dbh = daesql.MySQL(dbconfig.mysql_config)
    if mdtype == 1:
        state = "UPDATE node SET node_state='%s' WHERE group_id='%d'" % (
            upstate, ID)
        print("node update state=", state)
        result = dbh.execute(state)
    else:
        state = "UPDATE node SET node_state='%s' WHERE group_id='%d'" % (
            numberstate, ID)
        print("node update state=", state)
        result = dbh.execute(state)

    state = "UPDATE `group` SET group_state='%s' WHERE group_num='%d'" % (
        upstate, num)
    print("group update state=", state)
    result = dbh.execute(state)
    mqtt.update_group(ID)
    mqtt.update_node(ndlist)


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(day, 'cron', day_of_week='0-6', hour=0, minute=0)
    scheduler.start()
    while True:
        print("waiting...")
        filex = open(
            "/home/var/www/dae-web/app/api_1_0/resident/method/config/schedule_flag.txt", 'r', encoding='utf-8')
        flag = filex.read()
        while(flag == ''):
            flag = filex.read()
        flag = int(flag)
        filex.close()

        if flag == 1:
            print("change scheduler")
            scheduler.shutdown(wait=False)
            scheduler = BackgroundScheduler()
            scheduler.add_job(day, 'cron', day_of_week='0-6', hour=0, minute=0)
            scheduler.start()
            stime = datetime.now()
            print("time=", stime)
            x = timedelta(seconds=10)
            stime = stime + x
            scheduler.add_job(job, 'date', run_date=stime)
            filex = open(
                "/home/var/www/dae-web/app/api_1_0/resident/method/config/schedule_flag.txt", 'w', encoding='utf-8')
            filex.write('0')
            filex.close()

        time.sleep(1)
