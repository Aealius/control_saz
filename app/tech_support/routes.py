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
                    'status',
                    'search']



@bp.route('/add_issue', methods=['GET', 'POST'])
@login_required
def tech_support():
    if request.method == 'POST':
        description = request.form.get('description')
        comp_number = request.form.get('compNumber')
        theme = request.form.get('common-issues')
                
        new_tech_message = TechMessage(
                date_created=datetime.now(),
                theme = theme,
                description=description,
                user_id=current_user.id,
                comp_number=comp_number  
            )
        db.session.add(new_tech_message)
        db.session.commit()
        flash('Сообщение успешно отправлено!', 'success')
        return '', 200
    return render_template('tech_support/add_issue.html')


@bp.route('/issue_table', methods=['GET'])
@login_required
def tech_requests():
    return send_filtered_data(is_archived=False)

@bp.route('/archived', methods=['GET'])
@login_required
def archived_issues():
    return send_filtered_data(is_archived=True)


#далее предполагается, что пользователю придет датасет уже с только НЕ удаленными и НЕ архивированными

@bp.route('/issue_completed/<int:issue_id>', methods = ['POST'])
@login_required
def issue_completed(issue_id):
    if current_user.department == '205 ОАСУП':

        issue = db.session.query(TechMessage).get(issue_id)
        issue.status_id = Status.completed.value
        issue.completion_confirmed_at = datetime.now()
        db.session.commit()
    return '', 200

@bp.route('/issue_in_work/<int:issue_id>', methods = ['POST'])
@login_required
def issue_in_work(issue_id):
    if current_user.department == '205 ОАСУП':
        issue = db.session.query(TechMessage).get(issue_id)
        issue.status_id = Status.in_work.value
        db.session.commit()
    return '', 200

@bp.route("/delete/<int:issue_id>", methods = ['DELETE'])
@login_required
def delete_issue(issue_id):
    issue_to_delete = db.session.get(TechMessage, issue_id)
    issue_to_delete.is_deleted = True
    db.session.commit()
    flash('Заявка удалена!', 'success')
    return '', 200


#мейби поменять потом темплейт
def send_filtered_data(is_archived):
    filter_params_dict = {f : request.args.get(f) for f in FILTER_PARAM_KEYS if request.args.get(f)}
    page = request.args.get('p', 1, int)
    
    tech_messages_query = db.session.query(TechMessage)
    if not is_archived:
        if current_user.department == '205 ОАСУП':
            tech_messages = tech_messages_query.filter(TechMessage.is_deleted == False, TechMessage.is_archived ==False)
        else:
            tech_messages = tech_messages_query.filter(TechMessage.user_id == current_user.id, TechMessage.is_deleted == False, TechMessage.is_archived ==False)
    else:
        if current_user.department == '205 ОАСУП':
            tech_messages = tech_messages_query.filter(TechMessage.is_deleted == False, TechMessage.is_archived == True)
        else:
            tech_messages = tech_messages_query.filter(TechMessage.user_id == current_user.id, TechMessage.is_deleted == False, TechMessage.is_archived == True)
    
    tech_messages, messages_count = filter_TechMessage_data(tech_messages, page, **filter_params_dict)
    
    return render_template('tech_support/issue_table.html', tech_messages = tech_messages,
                                                              per_page = current_app.config['PER_PAGE'],
                                                              filter_params_dict = filter_params_dict,
                                                              status = Status,
                                                              page = page,
                                                              messages_count = messages_count,
                                                              archive = is_archived)
