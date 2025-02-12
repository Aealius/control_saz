from datetime import datetime
from flask import current_app, flash, render_template, request
from flask_login import current_user, login_required
from app.enums.status_enum import Status
from app.models import TechMessage
from app.tech_support import bp
from app import db
from app.tech_support.utils import filter_TechMessage_data

FILTER_PARAM_KEYS = ['creator',
                    'month',
                    'date',
                    'status']


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
    filter_params_dict = {f : request.args.get(f) for f in FILTER_PARAM_KEYS if request.args.get(f)}
    page = request.args.get('p', 1, int)
    
    if current_user.department == '205 ОАСУП':
        tech_messages = db.session.query(TechMessage)
    else:
        tech_messages = db.session.query(TechMessage).filter(TechMessage.user_id == current_user.id)
    
    tech_messages, messages_count = filter_TechMessage_data(tech_messages, page, **filter_params_dict)
    
    return render_template('tech_support/support_table.html', tech_messages = tech_messages,
                                                              per_page = current_app.config['PER_PAGE'],
                                                              filter_params_dict = filter_params_dict,
                                                              status = Status,
                                                              page = page,
                                                              messages_count = messages_count)