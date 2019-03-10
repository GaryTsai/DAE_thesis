import pymysql
from .resident.method.config.database_setting import mysql_config
# from ..models import *


class Database():
    def __init__(self, host='127.0.0.1', user='root', passwd='', db='', charset='utf8'):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.conn = pymysql.connect(self.host, self.user, self.passwd, self.db)

    def getConnection(self):
        if not self.conn.open:
            self.conn = pymysql.connect(
                self.host, self.user, self.passwd, self.db)
        return self.conn


db = Database(host=mysql_config['host'], user=mysql_config['user'],
              passwd=mysql_config['password'], db=mysql_config['db'], charset = "utf8")
conn = db.getConnection()
conn.ping(reconnect=True)
db_query = conn.cursor(pymysql.cursors.DictCursor)
