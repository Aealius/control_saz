from datetime import datetime
from flask import current_app, flash
from flask_login import current_user
from app.enums.status_enum import Status
from app.models import Task, User
from app import db


def filter_data(dataset, page : int, **params):

    match params.get('sn'):
        case 'in':
            dataset = dataset.filter(Task.executor_id == current_user.id)
        case 'out':
            dataset = dataset.filter(Task.creator_id == current_user.id)
        case 'all':
            if (not current_user.is_admin):
                dataset = dataset.filter(db.or_(Task.executor_id == current_user.id,
                                                Task.creator_id == current_user.id))
        case _:
            dataset = dataset.filter(Task.executor_id == current_user.id)
                
    match params.get('status'):
        case 'in_work':
            dataset = dataset.filter(Task.status_id == 1)
        case 'at_check':
            dataset = dataset.filter(Task.status_id == 2)
        case 'reviewed':
            dataset = dataset.filter(Task.status_id == 3)
        case 'completed':
            dataset = dataset.filter(Task.status_id == 4)
        case 'complete_delayed':
            dataset = dataset.filter(Task.status_id == 5)
        case 'delayed':
            dataset = dataset.filter(Task.status_id == 6)
        case 'invalid':
            dataset = dataset.filter(Task.status_id == 7)
        case 'pending':
            dataset = dataset.filter(Task.status_id == 8)
        case _:
            pass      
           
    match params.get('nm-select'):
        case '1':
            dataset = dataset.filter(Task.doctype_id == 1)
        case '2':
            dataset = dataset.filter(Task.doctype_id == 2)
        case '3':
            dataset = dataset.filter(Task.doctype_id == 3)
        case '4':
            dataset = dataset.filter(Task.doctype_id == 4)
        case '5':
            dataset = dataset.filter(Task.doctype_id == 5)
        case '6':
            dataset = dataset.filter(Task.doctype_id == 6)
        case '7':
            dataset = dataset.filter(Task.doctype_id == 7)
        case '8':
            dataset = dataset.filter(Task.doctype_id == 8)
        case '9':
            dataset = dataset.filter(Task.doctype_id == 9)
        case '10':
            dataset = dataset.filter(Task.doctype_id == 10)
        case _:
            pass  
             
    if params.get('executor'):
        dataset = dataset.filter(Task.executor_id ==  db.session.query(User)
                                                                .filter(User.department == params['executor'])
                                                                .first().id)

    if params.get('creator'):
        creator = db.session.query(User).filter(User.department == params['creator']).first()
        if creator:
            dataset = dataset.filter(Task.creator_id== creator.id)
    
    if params.get('month'):
        try:
            year, month = map(int, params['month'].split('-'))
            dataset = dataset.filter(db.extract('year', Task.date_created) == year,
                                 db.extract('month', Task.date_created) == month)
        except ValueError:
            # Обработка некорректного формата месяца
            flash("Некорректный формат месяца", "danger")

    if params.get('date'):
        date_filter = datetime.strptime(params['date'], '%Y-%m-%d').date()
        dataset = dataset.filter(db.cast(Task.date_created, db.Date) == date_filter)

    dataset_count = dataset.count()
    

    dataset = dataset.options(db.joinedload(Task.executor)).order_by(Task.date_created.desc())\
                                                           .paginate(page=page, per_page=current_app.config['PER_PAGE'])
    
    return (dataset, dataset_count,)

def hide_buh(current_user_login : str):
    if current_user_login == '8':
        return db.session.query(User).filter(User.id != current_user.id, User.is_deleted == False).all()
    else:
        #бухгалтерия скрыта по запросу главбуха
        return db.session.query(User).filter(User.id != current_user.id, User.login != current_app.config.get('BUH_LOGIN'), User.is_deleted == False).all()
         

def calculate_penalty(task : Task):  
    if (task.status_id == Status.completed.value or task.status_id == Status.complete_delayed.value) and task.deadline_for_check and task.completion_confirmed_at: # task.completion_confirmed_at
        overdue_days = (task.completion_confirmed_at.date() - task.deadline_for_check).days
        if overdue_days > 0:
            max_penalty = 20
            penalty = min(overdue_days, max_penalty)
            return penalty
    return 0