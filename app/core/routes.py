import os
from flask import (render_template, request, redirect, url_for, flash, send_from_directory, current_app)
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from werkzeug.utils import safe_join
from urllib.parse import unquote
from app.core.utils import calculate_penalty, filter_data, hide_buh
from app.enums.status_enum import Status
from app import db, login_manager
from app.core import bp
from app.models import (
    User,
    Task,
    DocTypeSubType,
    Executive,
    TechMessage)
import shutil

FILTER_PARAM_KEYS = ['executor',
                    'creator',
                    'month',
                    'date',
                    'status',
                    'nm-select',
                    'sn']

STATUS_DICT =  {'in_work' : 'В работе',
                'at_check' : 'На проверке',
                'reviewed' : 'Ознакомлен',
                'completed' : 'Выполнено',
                'complete_delayed' :'Выполнено, просрочено',
                'delayed' :'Просрочено',
                'invalid' :'Недействительно',
                'pending' :'Ожидается выполнение'} 

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@bp.route('/', methods = ['GET'])
@login_required
def index():
    
    filter_params_dict = {f : request.args.get(f) for f in FILTER_PARAM_KEYS if request.args.get(f)}
    page = request.args.get('p', 1, type=int) #параметр для страницы 
    
    # Начальный фильтр, если user - admin
    if current_user.is_admin:
        tasks = db.session.query(Task).filter(Task.is_archived == False, Task.is_deleted == False)
    else:
        # Если user - обычный пользователь, то видим только задачи где он - executor, а также те, которые он отправил
        
        tasks = db.session.query(Task).filter(
            db.or_(Task.executor_id == current_user.id, Task.creator_id == current_user.id), Task.is_archived == False, Task.is_deleted == False)
       
    tasks, task_count = filter_data(tasks, page, **filter_params_dict)

    for task in tasks:
        if task.extended_deadline:
            task.deadline_for_check = task.extended_deadline
        elif task.deadline:  # Добавляем проверку на deadline
            task.deadline_for_check = task.deadline
        else:
            task.deadline_for_check = date(9999,12,31)
            
        task.creator_files = task.creator_file.rstrip(';').split(';')
        if (task.attached_file):
            task.attached_files = task.attached_file.rstrip(';').split(';')
    

    executors =  db.session.query(User).filter(User.is_deleted == False).all()
        
    executors_for_resend = hide_buh(current_user.login)
        
    employees = db.session.query(Executive).all()
    nomenclature = db.session.query(DocTypeSubType).all()
    
    buh = db.session.query(User).filter(User.login == current_app.config.get('BUH_LOGIN')).first()
    return render_template('core/index.html',tasks=tasks,
                                        task_count = task_count,
                                        executors=executors,
                                        executors_for_resend = executors_for_resend,
                                        page = page,
                                        employees = employees,
                                        filter_params_dict = filter_params_dict,
                                        buh = buh,
                                        calculate_penalty=calculate_penalty,
                                        unquote=unquote,
                                        date=date,
                                        datetime = datetime,
                                        time = time,
                                        executive = Executive,
                                        status = Status,
                                        status_dict = STATUS_DICT,
                                        per_page = current_app.config['PER_PAGE'],
                                        nomenclature = nomenclature,
                                        BUH_LOGIN = current_app.config.get('BUH_LOGIN')) 


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_admin and not current_user.is_deputy:  # Проверка прав
        flash('У вас нет прав для создания задач.', 'danger')
        return redirect(url_for('index'))

    executors = hide_buh(current_user.login)
    nomenclature = db.session.query(DocTypeSubType).all()
    
    if request.method == 'POST':

        selected_executors = request.form.get('executor[]')
        #получаем тип документа по номенлатуре (номер)
        nm_doc = request.form.get('nm-select')
        #получаем порядковый номер типа документа
        nm_number = request.form.get('nm-number')
        
        dtst = db.session.get(DocTypeSubType, nm_doc)
        if (dtst):
            dtst.counter = nm_number
        else:
            nm_doc = None

        # Генерируем task_id для новой задачи
        task_id = str(len(db.session.query(Task).all()) + 1)

        # Обработка 'all'
        if 'all' in selected_executors:
            # Добавляем всех пользователей как исполнителей
            executors_for_task = executors
            task_uploads_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER'), task_id, 'creator')
            os.makedirs(task_uploads_folder, exist_ok=True)
        else:
            # Добавляем выбранных пользователей как исполнителей
            executors_for_task = db.session.query(User).filter(
                User.id.in_([int(executor) for executor in selected_executors.split(',')])
            ).all()
            task_uploads_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER'), task_id, 'creator')
            os.makedirs(task_uploads_folder, exist_ok=True)

        date_created = datetime.combine(datetime.strptime(request.form['date_created'], '%Y-%m-%d'), datetime.now().time())
        
        deadline = None
        if 'deadline' in request.form.keys() :
            deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d').date()
            
        description = request.form['description']
        
        if(request.form.get('is_valid') == 'on'):
            status_id = Status.in_work.value
        else:
            status_id = Status.invalid.value
        
        
        for_review = request.form.get('for_review') == 'on'
        files = request.files.getlist('files') #массив файлов

        creator_file_path = ''
        # Сохраняем файл только один раз
        for file in files:
            if file and file.filename != '':
                tmp_file_path = ''
                filename = file.filename
                file.save(os.path.join(task_uploads_folder, filename))
                tmp_file_path = os.path.join(task_id, 'creator', filename)
                tmp_file_path = tmp_file_path.replace('\\', '/')
                creator_file_path += tmp_file_path + ';'

        for executor in executors_for_task:
            if str(executor.id) in current_app.config.get('CAN_GET_RESENDED_TASKS_ARR'):
                employeeId = request.form.get('employee') or None
            else:
                employeeId = None

            new_task = Task(
                executor_id=executor.id,
                date_created=date_created,
                deadline=deadline,
                description=description,
                creator_id=current_user.id,
                employeeId = employeeId,
                for_review=for_review,
                creator_file=creator_file_path,
                status_id = status_id,
                doctype_id = nm_doc,
                docnum = nm_number
            )
            db.session.add(new_task)
            db.session.commit()    
        
        #TODO: notifications
        flash('Задача успешно добавлена!', 'success')
        return '', 200

    return render_template('core/add.html',  executors=executors,
                                        nomenclature = nomenclature,
                                        current_user=current_user,
                                        datetime=datetime)

import shutil



@bp.route('/add_memo', methods=['GET', 'POST']) #  Маршрут для создания служебных записок
@login_required
def add_memo():
    
    executors = hide_buh(current_user.login)

    if request.method == 'POST':
        selected_executor_id = request.form.get('executor[]')  #  Получаем ID выбранного исполнителя
        if 'all' in selected_executor_id:
            selected_executor_id = [executor.id for executor in executors if executor.id != current_user.id]
        else:
            selected_executor_id = [int(executor) for executor in selected_executor_id.split(',')]
        description = request.form['description']
        files = request.files.getlist('files') #  Получаем файл вне цикла

        if 'all' in selected_executor_id:
            all_count = 1
            # Проверка, есть ли уже папка 'all1', 'all2' и т.д.
            while os.path.exists(os.path.join(current_app.config.get('UPLOAD_FOLDER'), f'all{all_count}', 'creator')):
                all_count += 1
            task_id = f'all{all_count}' # Использовать "all" + счетчик
        else:
            # Генерируем task_id для "не all"
            task_id = str(len(db.session.query(Task).all()) + 1)

            memo_uploads_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER'), task_id, 'creator') # Папка для всех записок
            os.makedirs(memo_uploads_folder, exist_ok=True)
        
        creator_file_path = ''
        # Сохраняем файл только один раз
        if files and len(files) > 0:
            for file in files:
                tmp_file_path = ''
                filename = file.filename  
                file.save(os.path.join(memo_uploads_folder, filename))
                tmp_file_path = os.path.join(task_id, 'creator', filename)
                tmp_file_path = tmp_file_path.replace('\\', '/') # Запись пути к файлу в базу
                creator_file_path += tmp_file_path + ';'
                
        for executor_id in selected_executor_id:
            if str(executor_id) in current_app.config.get('CAN_GET_RESENDED_TASKS_ARR'):
                employeeId = request.form.get('employee') or None
            else:
                employeeId = None
            
            new_memo = Task(
                executor_id=int(executor_id),
                creator_id=current_user.id,
                date_created=datetime.now(),
                for_review=True,
                description=description,
                creator_file=creator_file_path, # Запись пути к файлу в базу
                status_id = Status.in_work.value,
                employeeId = employeeId                
            )
            db.session.add(new_memo)
            db.session.commit()
            
        #TODO: notifications    
        flash('Служебная записка успешно отправлена!', 'success')
        return '', 200

    return render_template('core/add_memo.html', executors=executors, current_user = current_user)  #  Передаем executors в шаблон

@bp.route('/resend/<int:task_id>', methods=['POST'])
@login_required
def resend(task_id):
    if not current_user.is_admin and not current_user.is_deputy:  # Проверка прав
        flash('У вас нет прав для создания задач.', 'danger')
        return redirect(url_for('index'))

    # Генерируем new_task_id для новой задачи
    new_task_id = str(len(db.session.query(Task).all()) + 1)
    task = db.session.query(Task).get_or_404(task_id)
    
    # Пока что меняем статус только для задач. Для служебных записок не меняем.
    if not task.for_review:
        task.status_id = Status.pending.value

    executor_for_task_id = request.json.get('executors').split(',')
    if 'all' in executor_for_task_id:
        executor_for_task_id = [executor.id for executor in db.session.query(User).filter(User.is_deleted == False).all() if executor.id != current_user.id]
    task_uploads_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER'), new_task_id, 'creator')
    os.makedirs(task_uploads_folder, exist_ok=True)

    date_created = datetime.now()
    deadline = task.deadline
    description = task.description
    for_review = task.for_review
    doctype_id = task.doctype_id
    docnum = task.docnum

    try:        
        creator_file_path = ''
        uploadFolder = current_app.config.get('UPLOAD_FOLDER') + '/'

        file_path_arr = task.creator_file.rstrip(';').split(';')
        # Сохраняем файл только один раз
        for filePath in file_path_arr:
            if filePath != '':
                shutil.copy2(uploadFolder + filePath, task_uploads_folder)
                tmp_file_path = ''
                filename = os.path.basename(filePath)
                tmp_file_path = os.path.join(new_task_id, 'creator', filename)
                tmp_file_path = tmp_file_path.replace('\\', '/')
                creator_file_path += tmp_file_path + ';'
    except Exception as e:
        s = str(e)
        flash("Произошла ошибка: " + s, 'danger')
        return '', 500
    
    for executor_id in executor_for_task_id:
        if str(executor_id) in current_app.config.get('CAN_GET_RESENDED_TASKS_ARR'):
            employeeId = request.json.get('employee') or None
        else:
            employeeId = None

        new_task = Task(
            executor_id=executor_id,
            date_created=date_created,
            deadline=deadline,
            description=description,
            creator_id=current_user.id,
            employeeId = employeeId,
            for_review=for_review,
            creator_file=creator_file_path,
            parent_task_id = task_id,
            docnum = docnum,
            doctype_id = doctype_id
        )
        db.session.add(new_task)
        db.session.commit()
        
    #TODO: notifications
    flash('Задача успешно добавлена!', 'success')
    return '', 200



@bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    task = db.session.query(Task).get(task_id)
    if task.creator_id != current_user.id and not current_user.is_admin:  # Проверка прав
        flash('У вас нет прав для редактирования этой задачи.', 'danger')
        return redirect(url_for('core.index'))

    executors = hide_buh(current_user.login)
        
    if request.method == 'POST':
        task.executor_id = request.form['executor']
        task.description = request.form['description']
        
        if (request.form.get('is_valid') != 'on'):
            task.status_id = Status.invalid.value
            
        task.edit_datetime = datetime.now()
        
        files = request.files.getlist('files') #массив файлов
        
        if str(task.executor_id) in current_app.config.get('CAN_GET_RESENDED_TASKS_ARR'):
            task.employeeId = request.form.get('employee') or None
        else:
            task.employeeId = None

        
        if (current_user.is_admin or current_user.is_deputy):
            
            if 'deadline' in request.form.keys() :
                task.deadline = datetime.strptime(request.form.get('deadline'), '%Y-%m-%d').date()
            
            extend_deadline = request.form.get('extend_deadline')
            if extend_deadline:
                try:
                    extended_deadline_date = datetime.strptime(request.form['extended_deadline'], '%Y-%m-%d').date()
                    task.extended_deadline = extended_deadline_date
                except ValueError:
                    flash("Некорректный формат даты продления", "danger")
                    return render_template('core/edit.html', task=task,
                                                        executors=executors,
                                                        current_user = current_user,
                                                        status = Status,
                                                        datetime=datetime)
      
        if task.deadline:            
            if (task.status_id != Status.invalid):
                if (task.deadline < datetime.now().date()):
                    task.status_id = Status.delayed.value
                elif (task.deadline >= datetime.now().date()):
                    task.status_id = Status.in_work.value
        
        creator_file_path = ''

        if(len(files) > 0):
            for file in files:
                if file and file.filename != '':
                    filename = file.filename  # Оригинальное имя
                    task_id = str(task_id)
                    tmp_file_path = ''

                    memo_uploads_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER'), task_id, 'creator') # Папка для всех записок
                    os.makedirs(memo_uploads_folder, exist_ok=True)

                    # Сохранение файла
                    file.save(os.path.join(memo_uploads_folder, filename)) 
                    tmp_file_path = os.path.join(task_id, 'creator', filename)
                    tmp_file_path = tmp_file_path.replace('\\', '/') # Запись пути к файлу в базу
                    creator_file_path += tmp_file_path + ';'
            task.creator_file = creator_file_path
        
        #получаем тип документа по номенлатуре (номер)
        nm_doc = request.form.get('nm-select')

        dtst = db.session.get(DocTypeSubType, nm_doc)
        if (dtst):
            #получаем порядковый номер типа документа
            nm_number = request.form.get('nm-number')
            task.doctype_id = nm_doc
            task.docnum = nm_number
        else:
            task.doctype_id = None
            task.docnum = None
        
        db.session.commit()
        flash('Задача успешно отредактирована!', 'success')
        return '', 200

    nomenclature = db.session.query(DocTypeSubType).all()
    
    return render_template('core/edit.html', task=task,
                                        executors=executors,
                                        status = Status,
                                        current_user = current_user,
                                        nomenclature = nomenclature,
                                        datetime=datetime)



@bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    task = db.session.get(Task, task_id)
    if task.creator_id != current_user.id and not current_user.is_admin:  # Проверка прав
        flash('У вас нет прав для удаления этой задачи.', 'danger')
        return redirect(url_for('index'))

    task.is_deleted = True
    task.when_deleted = datetime.now()
    
    db.session.commit()
    flash('Задача успешно удалена!', 'success')
    return redirect(request.referrer or url_for('core.index'))


@bp.route('/complete/<int:task_id>', methods=['GET', 'POST'])
@login_required
def complete(task_id):
    task = db.session.query(Task).get_or_404(task_id)

    if current_user.id != task.executor_id:
        flash('Вы можете изменять только свои задачи.', 'danger')
        return redirect(url_for('core.index'))

    if request.method == 'POST':

        files = request.files.getlist('files')  # Получаем файл, если он есть
        executor_file_path = ''
        if files and len(files) > 0:
            for file in files:
                tmp_file_path = ''
                filename = file.filename  # Оригинальное имя
            
                task_uploads_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER'), str(task_id), 'executor')
                os.makedirs(task_uploads_folder, exist_ok=True)

                file.save(os.path.join(task_uploads_folder, filename)) # Сохраняем с оригинальным именем!

                tmp_file_path = os.path.join(str(task_id), 'executor', filename) #  Оригинальное имя в базе
                tmp_file_path = tmp_file_path.replace('\\', '/') 
                executor_file_path += tmp_file_path + ';'
                
        task.attached_file = executor_file_path
        task.completion_note = request.form.get('completion_note')
        task.status_id = Status.at_check.value
        db.session.commit()
        
        #TODO: notifications
        flash('Отметка о выполнении отправлена администратору.', 'success')
        return '', 200

    return render_template('core/complete.html', task=task)


@bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    uploads_folder = current_app.config.get('UPLOAD_FOLDER')
    safe_path = safe_join(uploads_folder, filename) # Используем safe_join
    if safe_path and os.path.exists(safe_path):
       return send_from_directory(uploads_folder, filename, as_attachment=False)
    else:
        flash(f"Файл не найден: {filename}")
        return redirect(url_for('core.index'))

@bp.route('/tasks/<int:task_id>/confirm', methods=['POST'])
@login_required
def confirm_task_deputy(task_id):
    if not current_user.is_deputy and not current_user.is_admin:
        flash('У вас нет прав для подтверждения выполнения задач.', 'danger')
        return redirect(url_for('core.index'))
    
    task = db.session.query(Task).get_or_404(task_id)
    if current_user.is_deputy and task.creator_id != current_user.id:
        flash('Вы можете подтверждать только задачи, которые вы выдали.', 'danger')
        return redirect(url_for('core.index'))

    task.completion_confirmed_at = datetime.now()
    task.admin_note = request.json.get('note')
        
    if task.deadline:
        if(task.get_deadline_for_check() < task.completion_confirmed_at.date()):
            task.status_id = Status.complete_delayed.value
        else:
            task.status_id = Status.completed.value
    else:
        task.status_id = Status.completed.value
        
    # Если задача была дочерней и пользователь зам, то работаем с родителем
    if current_user.is_deputy and task.parent_task_id != None:
        parentTask = Task.query.filter_by(id = task.parent_task_id).first()
        
        # Пока что для служебных записок с родителем ничего не делаем
        # Также проверяем, что родительская таска сама в работе
        if parentTask != None and (not parentTask.for_review) and (parentTask.status_id == Status.in_work.value or parentTask.status_id == Status.delayed.value or parentTask.status_id == Status.pending.value): 
            parentTask.status_id = Status.at_check.value
            parentTask.completion_note = task.completion_note
                
            # Работа с файлами
            try:        
                exev_file_path = ''
                task_uploads_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER'), str(task.parent_task_id), 'executor')
                uploadFolder = current_app.config.get('UPLOAD_FOLDER') + '/'
                if not os.path.exists(uploadFolder):
                    os.makedirs(uploadFolder)
                os.makedirs(task_uploads_folder, exist_ok=True)

                if task.attached_file:
                    file_path_arr = task.attached_file.rstrip(';').split(';')
                else:
                    file_path_arr = ''
                    
                # Сохраняем файл только один раз
                for filePath in file_path_arr:
                    if filePath != '':
                        shutil.copy2(uploadFolder + filePath, task_uploads_folder)
                        tmp_file_path = ''
                        filename = os.path.basename(filePath)
                        tmp_file_path = os.path.join(str(task.parent_task_id), 'executor', filename)
                        tmp_file_path = tmp_file_path.replace('\\', '/')
                        exev_file_path += tmp_file_path + ';'
            except Exception as e:
                s = str(e)
                flash("Произошла ошибка: " + s, 'danger')
                return '', 500   
                
            parentTask.attached_file = exev_file_path
                
    db.session.commit()
    flash('Выполнение задачи подтверждено.', 'success')
    return '', 200

@bp.route('/tasks/<int:task_id>/reject', methods=['POST'])
@login_required
def reject_task_deputy(task_id):
    if not current_user.is_deputy and not current_user.is_admin:
        flash('У вас нет прав для отклонения задач.', 'danger')
        return redirect(url_for('core.index'))
    
    task = Task.query.get_or_404(task_id)
    
    if current_user.is_deputy and task.creator_id != current_user.id:
        flash('Вы можете отклоненять только задачи, которые вы выдали.', 'danger')
        return redirect(url_for('core.index'))

    if task.attached_file != None and task.attached_file != "":
        for file in task.attached_file.rstrip(';').split(';'):
            test = current_app.config.get('UPLOAD_FOLDER') + '/' + file
            os.remove(current_app.config.get('UPLOAD_FOLDER') + '/' + file)
 
    task.attached_file = None
    task.completion_note = None
    task.admin_note = request.json.get('note')
    task.status_id = Status.in_work.value
    db.session.commit()
    flash('Выполнение задачи отклонено.', 'warning')
    return '', 200

@bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(url_for('core.index'))
    users = db.session.query(User).filter(User.is_deleted == False).all()
    return render_template('core/users.html', users=users)


@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('У вас нет прав для создания пользователей.', 'danger')
        return redirect(url_for('core.index'))

    if request.method == 'POST':
        department = request.form['department']
        login = request.form['login']
        password = request.form['password']
        is_admin = request.form.get('is_admin') == 'on'
        is_deputy = request.form.get('is_deputy') == 'on' # Добавляем проверку на is_deputy

        existing_user = db.session.query(User).filter(User.login == login).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует.', 'danger')
            return redirect(url_for('core.add_user'))

        hashed_password = generate_password_hash(password)
        new_user = User(department=department, login=login, password_hash=hashed_password, is_admin=is_admin, is_deputy=is_deputy)
        db.session.add(new_user)
        db.session.commit()
        flash('Пользователь успешно добавлен!', 'success')
        return redirect(url_for('core.users'))
    return render_template('core/add_user.html')


@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('У вас нет прав для удаления пользователей.', 'danger')
        return redirect(url_for('core.index'))

    user = db.session.get(User, user_id)
    
    user.is_deleted = True
    user.when_deleted = datetime.now()
    
    db.session.commit()
    flash('Пользователь успешно удален!', 'success')
    return redirect(url_for('core.users'))


@bp.route('/review/<int:task_id>', methods=['GET', 'POST'])
@login_required
def review(task_id):
    task = db.session.query(Task).get(task_id)
    if request.method == 'POST':  #  Обработка POST-запроса от кнопки "Ознакомлен"
        task.completion_confirmed_at = datetime.now()
        task.status_id = Status.reviewed.value
        
        db.session.commit()
        flash('Вы ознакомились с задачей.', 'success')
        return '', 200  #  Перенаправление на главную страницу
    return render_template('core/review.html', task=task)


@bp.route('/reports')
@login_required
def reports():
    if not current_user.is_admin:
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(url_for('core.index'))

    all_users = db.session.query(User).filter(User.is_deleted == False).all()
    report_data = {}

    for user in all_users:
        report_data[user] = {}
        for month in range(1, 13): #  Перебираем все месяцы
            tasks_in_month = db.session.query(Task).filter(
                Task.executor_id == user.id,
                Task.is_deleted == False,
                db.extract('month', Task.date_created) == month,
                Task.date_created >= date(2024,12,1) # Попросили начать отсчет с 1 декабря 2024, поэтому старые пока не учитываем
            ).all()

            total_penalty = 0
            for task in tasks_in_month:
                task.deadline_for_check = task.get_deadline_for_check() # используем метод модели
                penalty = calculate_penalty(task) # calculate_penalty(task)
                total_penalty += penalty
            report_data[user][month] = total_penalty

    return render_template('core/reports.html', report_data=report_data, all_users=all_users, date=date, any=any)

@bp.route('/archived')
@login_required
def archived():

    filter_params_dict = {f : request.args.get(f) for f in FILTER_PARAM_KEYS if request.args.get(f)}
    page = request.args.get('p', 1, type=int)
    if current_user.is_admin:
        archived_data = db.session.query(Task).filter(Task.is_archived ==True, Task.is_deleted == False)
    else:
        archived_data = db.session.query(Task).filter(db.or_(Task.executor_id == current_user.id, Task.creator_id == current_user.id),
                                          Task.is_archived == True, Task.is_deleted == False)

    archived_data, task_count = filter_data(archived_data, page, **filter_params_dict)
    executors = db.session.query(User).filter(User.is_deleted == False).all()

    for task in archived_data:
        if task.extended_deadline:
            task.deadline_for_check = task.extended_deadline
        elif task.deadline:  # Добавляем проверку на deadline
            task.deadline_for_check = task.deadline
        else:
            task.deadline_for_check = date(9999,12,31)

        task.creator_files = task.creator_file.rstrip(';').split(';')


    nomenclature = db.session.query(DocTypeSubType).all()
    return render_template('core/archived.html', data = archived_data,
                                            task_count = task_count,
                                            executors = executors,
                                            per_page = current_app.config['PER_PAGE'],
                                            page=page,
                                            filter_params_dict = filter_params_dict,
                                            time=time,
                                            date=date,
                                            datetime=datetime,
                                            executive = Executive,
                                            nomenclature = nomenclature,
                                            unquote = unquote,
                                            status = Status,
                                            status_dict = STATUS_DICT)
    

@bp.route('/create_memo', methods=['GET'])
@login_required
def create_memo():
    executors = [executor for executor in db.session.query(User).all() if executor.id != current_user.id]
    
    current_user_department = ''
    
    if not current_user.department.split(' ', maxsplit=1)[0].isdigit():
        current_user_department = current_user.department
    else:
        current_user_department = current_user.department.split(' ', maxsplit=1)[1]
    
    return render_template('core/create_memo.html', executors = executors,
                                               current_user_department = current_user_department)



@bp.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

