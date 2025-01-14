from flask import jsonify
from flask_login import current_user, login_required
from app.api import bp
from app.api.dtos import CreateMemoDTO
from app.models import DocTypeSubType,Executive, Task, User
from app import db

@bp.route('/api/nomenclature/counters')
@login_required
def getDocCounterData():
    dtsts = db.session.query(DocTypeSubType).all()
    d_a = []
    for dtst in dtsts:
        d_a.append(dtst.to_dict())
    
    return jsonify(d_a)

#API-метод, возвращающий список сотрудников по id отдела 
@bp.route('/api/users/<int:user_id>/employees', methods=['GET'])
@login_required
def getEmployees(user_id):
    emp = []
    employees = db.session.query(Executive).filter(Executive.user_id == user_id).all()
    for employee in employees:
        emp.append(employee.to_dict())
    return jsonify(emp)

#API-метод, возвращающий задачу по ее id
@bp.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def getTaskById(task_id):
    task = db.session.get(Task, task_id).to_dict()
    if (not task):
        return '', 404
    return jsonify(task)

@bp.route('/api/users/current_user', methods=['GET'])
@login_required
def getCurrentUser():
    user = db.session.get(User, current_user.id).to_dict()
    if (not user):
        return '', 404
    return jsonify(user)

@bp.route('/api/users/current_user_with_head', methods=['GET'])
@login_required
def getCurrentUserWithHead():
    data = db.session.get(User, current_user.id)
    current_user_with_head = CreateMemoDTO(
        department=data.department,
        full_department=data.full_department,
        headName=data.head[0].name,
        headSurname=data.head[0].surname,
        headPatronymic=data.head[0].patronymic,
        headPosition=data.head[0].position,
        headSignaturePath=data.head[0].signature_path,
    )
    if (not data):
        return '', 404
    return jsonify(current_user_with_head)