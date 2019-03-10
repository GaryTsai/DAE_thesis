import logging
from logging.handlers import RotatingFileHandler

global role
role = "Cloud"


class BasicConfig(object):
    # Flask（以及相關的擴展extension）需要進行加密
    SECRET_KEY = '421d7fa062a76ca25669e91923a3c79f'
    # 設置是否在每次連接結束後自動提交數據庫中的變動。
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 如果設置成 True (默認情況)，Flask-SQLAlchemy 將會追蹤對象的修改並且發送信號。這需要額外的內存，如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 可以用於顯式地禁用或者啟用查詢記錄。查詢記錄 在調試或者測試模式下自動啟用。一般我們不設置。
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        # 這程式主要的功能是希望每次運行程式後能將log續寫至指定的檔案
        # 並在檔案達到maxBytes指定的大小後便新增新的log檔
        # 新增到backupCount指定的數量後刪除最舊的檔案
        _handler = RotatingFileHandler('app.log',
                                       maxBytes=10000,
                                       backupCount=1)
        # 指定被處理的訊息級別，低於lel級別的訊息將被忽略 logging.WARNING為日誌級別
        _handler.setLevel(logging.WARNING)
        logging_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
        _handler.setFormatter(logging_format)
        # 增加或刪除指定的handler
        app.logger.addHandler(_handler)


class DevelopmentConfig(BasicConfig):
    DEBUG = True
    # 用於連接數據的數據庫
    SQLALCHEMY_DATABASE_URI = 'mysql://root:kDd414o6@localhost/lvami'  # here needs change
    SQLALCHEMY_ECHO = True

   # SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
   #     'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(BasicConfig):
    pass


class ProductionConfig(BasicConfig):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
