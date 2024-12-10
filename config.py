class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345@localhost/control_saz'
    JSON_AS_ASCII = False # Важно!
    CanGetResendedTasksArr = ['27'] # Бухгалтерия
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB