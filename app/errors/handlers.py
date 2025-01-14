from flask import render_template
from app import db
from app.errors import bp
import werkzeug


@bp.errorhandler(werkzeug.exceptions.NotFound)
def page_not_found(error):
    return render_template('404.html'), 404

@bp.errorhandler(werkzeug.exceptions.InternalServerError)
def internal_server_error(error):
    db.session.rollback()
    return render_template('500.html', error = error), 500
