import datetime
from flask import current_app, flash
from app import db
from app.models import TechMessage, User

def filter_TechMessage_data(dataset, page : int, **params):
                
    match params.get('status'):
        case 'in_work':
            dataset = dataset.filter(TechMessage.status_id == 1)
        case 'completed':
            dataset = dataset.filter(TechMessage.status_id == 4)
        case 'pending':
            dataset = dataset.filter(TechMessage.status_id == 8)
        case _:
            pass

    if params.get('creator'):
        creator = db.session.query(User).filter(User.department == params['creator']).first()
        if creator:
            dataset = dataset.filter(TechMessage.user_id == creator.id)
    
    if params.get('month'):
        try:
            year, month = map(int, params['month'].split('-'))
            dataset = dataset.filter(db.extract('year', TechMessage.date_created) == year,
                                 db.extract('month', TechMessage.date_created) == month)
        except ValueError:
            # Обработка некорректного формата месяца
            flash("Некорректный формат месяца", "danger")

    if params.get('date'):
        date_filter = datetime.strptime(params['date'], '%Y-%m-%d').date()
        dataset = dataset.filter(db.cast(TechMessage.date_created, db.Date) == date_filter)

    dataset_count = dataset.count()
    

    dataset = dataset.order_by(TechMessage.date_created.desc())\
                                                           .paginate(page=page, per_page=current_app.config['PER_PAGE'])
    
    return (dataset, dataset_count,)