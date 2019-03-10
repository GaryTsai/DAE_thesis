def cflag():
    filex=open("/home/var/www/dae-web/app/api_1_0/resident/method/config/schedule_flag.txt",'w',encoding='utf-8')
    filex.write('1')
    filex.close()

    print("cflag working")

