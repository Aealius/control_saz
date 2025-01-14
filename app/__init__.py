import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager
from waitress import serve
from config import Config
import logging
from logging.handlers import RotatingFileHandler


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для того, чтобы просматривать эту страницу необходим вход'


def create_app(config_class=Config) -> Flask:
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.core import bp as core_bp
    app.register_blueprint(core_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
    
    if not app.debug:
        
        if not os.path.exists(app.config.get('UPLOAD_FOLDER')):
            os.makedirs(app.config.get('UPLOAD_FOLDER'))
        
        if not os.path.exists(app.config.get('LOGS_FOLDER')):
            os.mkdir(app.config.get('LOGS_FOLDER'))
            
        file_handler = RotatingFileHandler(app.config.get('LOGS_FOLDER') + '/app.log', maxBytes=1024 * 1024 * 10 ,backupCount=10, encoding='utf-8')
        app.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        app.logger.addHandler(console_handler)
        
    return app


from app import models
