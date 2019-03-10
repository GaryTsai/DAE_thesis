# encoding=utf-8
#! /usr/bin/python

import method.condition as condition
import sys
import threading
import json

from method.meter import Meter
import method.common as common

class PostAPI(threading.Thread):
    def run(self):

        while True:
            thetime = common.get_now_sec()

            while int(thetime) % 10 != 0:
                thetime = common.get_now_sec()

            thetime = common.get_now()
            print("post")
            file = open('/home/var/www/dae-web/app/api_1_0/resident/method/config/last_data.json', 'r', encoding='utf-8')
            last_data = file.read()
            while(last_data==''):
                last_data=file.read()
            data = json.loads(last_data)
            file.close()

            data[0]['datetime'] = thetime
            print("post*100")
            response = common.post_data_to_server(data)


def main():
    try:
        #flag.flag=1

        cond = condition.Condition()
        meter_thread = Meter(cond)
        meter_thread.start() # start thread
        PostAPI().start()

    except:
        print("read error")
        pass



if __name__ == '__main__':
    main()
