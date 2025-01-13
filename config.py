import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345@localhost/control_saz'
    JSON_AS_ASCII = False
    CanGetResendedTasksArr = ['27']
    BUH_LOGIN = '234'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    PER_PAGE = 20