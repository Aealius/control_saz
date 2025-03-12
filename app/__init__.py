import os
from time import strftime
from flask import Flask, current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager
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
    
    from app.tech_support import bp as support_bp
    app.register_blueprint(support_bp, url_prefix = '/tech')
    
    if not app.debug:
        
        if not os.path.exists(app.config.get('UPLOAD_FOLDER')):
            os.makedirs(app.config.get('UPLOAD_FOLDER'))
        
        if not os.path.exists(app.config.get('LOGS_FOLDER')):
            os.mkdir(app.config.get('LOGS_FOLDER'))
            
        logger = logging.getLogger('waitress')
        file_handler = RotatingFileHandler(app.config.get('LOGS_FOLDER') + '/app.log', maxBytes=1024 * 1024 * 10 ,backupCount=10, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        
        @app.after_request
        def after_request(response):
            
            timestamp = strftime('[%d.%m.%Y %H:%M]')
            app.logger.error('%s %s - %s %s %s - %s', timestamp, request.remote_addr, request.scheme, request.method, request.full_path, response.status)
            
            if 'Cache-Control' not in response.headers:
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
                
            return response
        
    return app
