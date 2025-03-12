from flask import Blueprint

bp = Blueprint('tech_support', __name__)

from app.tech_support import routes