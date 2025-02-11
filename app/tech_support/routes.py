from datetime import datetime
from flask import current_app, flash, render_template, request
from flask_login import current_user, login_required
from app.models import TechMessage
from app.tech_support import bp
from app import db

@bp.route('/tech_support', methods=['GET', 'POST'])
@login_required
def tech_support():
    if request.method == 'POST':
        date_created = datetime.now()
        description = request.form['description']
        comp_number = request.form['compNumber']
                
        new_tech_message = TechMessage(
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

@bp.route('/support_table', methods=['GET'])
@login_required
def tech_requests():
    
    tech_messages = db.session.query(TechMessage).all()
    
    return render_template('tech_support/support_table.html', tech_messages = tech_messages,
                                                              per_page = current_app.config['PER_PAGE'])