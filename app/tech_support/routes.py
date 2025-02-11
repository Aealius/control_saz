from datetime import datetime
from flask import flash, render_template, request
from flask_login import current_user, login_required
from app.models import TechMessage
from app.tech_support import bp
from app import db

@bp.route('/tech_support', methods=['GET', 'POST'])
@login_required
def tech_support():
    if request.method == 'POST':
        tech_message_id = str(len(db.session.query(TechMessage).all()) + 1)
        date_created = datetime.now()
        description = request.form['description']
        comp_number = request.form['compNumber']
                
        new_tech_message = TechMessage(
                id = tech_message_id,
                date_created=date_created,
                description=description,
                user_id=current_user.id,
                comp_number=comp_number  
            )
        db.session.add(new_tech_message)
        db.session.commit()
        flash('Сообщение успешно отправлено!', 'success')
        return '', 200
    return render_template('tech_support/tech_support.html')