from app import app, db, login_manager
from flask import (Flask, render_template, request, redirect, url_for, flash, send_from_directory, Blueprint, jsonify)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename, safe_join
from urllib.parse import quote, unquote
from enums.status_enum import Status
from app.models import User, Task, Executive
import shutil
import os


UPLOAD_FOLDER = 'uploads'
PER_PAGE = 20
FILTER_PARAM_KEYS = ['executor',
                    'creator',
                    'month',
                    'date',
                    'status',
                    'sn']

STATUS_DICT =  {'in_work' : 'В работе',
                'at_check' : 'На проверке',
                'reviewed' : 'Ознакомлен',
                'completed' : 'Выполнено',
                'complete_delayed' :'Выполнено, просрочено',
                'delayed' :'Просрочено',
                'invalid' :'Недействительно',
                'pending' :'Ожидается выполнение'} 


# Id отделов, у которых можно выбрать конкретного исполнителя


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/', methods = ['GET'])
@login_required
def index():
    
    filter_params_dict = {f : request.args.get(f) for f in FILTER_PARAM_KEYS if request.args.get(f)}

    page = request.args.get('p', 1, type=int)
    
    # Начальный фильтр, если user - admin
    if current_user.is_admin:
        tasks = Task.query.filter(Task.is_archived == False, Task.is_deleted == False)
    else:
        # Если user - обычный пользователь, то видим только задачи где он - executor, а также те, которые он отправил
       tasks = Task.query.filter(
            db.or_(Task.executor_id == current_user.id, Task.creator_id == current_user.id), Task.is_archived == False, Task.is_deleted == False)
       
    tasks, task_count = filter_data(tasks, page, **filter_params_dict)

    add_fields(tasks)

    executors = User.query.filter(User.is_deleted == False).all()
    employees = Executive.query.all()
    return render_template('index.html',tasks=tasks,
                                        task_count = task_count,
                                        executors=executors,
                                        date=date,
                                        datetime = datetime,
                                        time = time,
                                        calculate_penalty=calculate_penalty,
                                        unquote=unquote,
                                        page = page,
                                        employees = employees,
                                        executive = Executive,
                                        filter_params_dict = filter_params_dict,
                                        per_page = PER_PAGE,
                                        status = Status, 
                                        status_dict = STATUS_DICT) 


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_admin and not current_user.is_deputy:  # Проверка прав
        flash('У вас нет прав для создания задач.', 'danger')
        return redirect(url_for('index'))

    executors = [executor for executor in User.query.all() if (executor.id != current_user.id and executor.is_deleted == False)]
    
    if request.method == 'POST':

        selected_executors = request.form.get('executor[]')

        # Генерируем task_id для новой задачи
        task_id = str(len(Task.query.all()) + 1)

        # Обработка 'all'
        if 'all' in selected_executors:
            # Добавляем всех пользователей как исполнителей
            executors_for_task = executors
            task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id, 'creator')
            os.makedirs(task_uploads_folder, exist_ok=True)
        else:
            # Добавляем выбранных пользователей как исполнителей
            executors_for_task = User.query.filter(
                User.id.in_([int(executor) for executor in selected_executors.split(',')])
            ).all()
            task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id, 'creator')
            os.makedirs(task_uploads_folder, exist_ok=True)

        date_created = datetime.combine(datetime.strptime(request.form['date_created'], '%Y-%m-%d'), datetime.now().time())
        is_бессрочно = request.form.get('is_бессрочно') == 'on'
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() if not is_бессрочно else None
        description = request.form['description']
        
        if(request.form.get('is_valid') == 'on'):
            is_valid = True
            status_id = Status.in_work.value
        else:
            is_valid =False
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
            if str(executor.id) in app.config['CanGetResendedTasksArr']:
                employeeId = request.form.get('employee') or None
            else:
                employeeId = None

            new_task = Task(
                executor_id=executor.id,
                date_created=date_created,
                deadline=deadline,
                description=description,
                is_valid=is_valid,
                is_бессрочно=is_бессрочно,
                creator_id=current_user.id,
                employeeId = employeeId,
                for_review=for_review,
                creator_file=creator_file_path,
                status_id = status_id
            )
            db.session.add(new_task)
            db.session.commit()

        flash('Задача успешно добавлена!', 'success')
        return '', 200

    return render_template('add.html', executors=executors, datetime=datetime, current_user=current_user)

import shutil



@app.route('/add_memo', methods=['GET', 'POST']) #  Маршрут для создания служебных записок
@login_required
def add_memo():
    executors = User.query.filter(User.is_deleted == False).all()

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
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f'all{all_count}', 'creator')):
                all_count += 1
            task_id = f'all{all_count}' # Использовать "all" + счетчик
        else:
            # Генерируем task_id для "не all"
            task_id = str(len(Task.query.all()) + 1)

            memo_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id, 'creator') # Папка для всех записок
            os.makedirs(memo_uploads_folder, exist_ok=True)
        
        creator_file_path = ''
        # Сохраняем файл только один раз
        for file in files:
            if file and file.filename != '':
                tmp_file_path = ''
                filename = file.filename  
                filename = file.filename
                file.save(os.path.join(memo_uploads_folder, filename))
                tmp_file_path = os.path.join(task_id, 'creator', filename)
                tmp_file_path = tmp_file_path.replace('\\', '/') # Запись пути к файлу в базу
                creator_file_path += tmp_file_path + ';'
                
        for executor_id in selected_executor_id:
            if str(executor_id) in app.config['CanGetResendedTasksArr']:
                employeeId = request.form.get('employee') or None
            else:
                employeeId = None
            
            new_memo = Task(
                executor_id=int(executor_id),
                creator_id=current_user.id,
                date_created=datetime.now(),
                is_бессрочно=True,
                for_review=True,
                description=description,
                creator_file=creator_file_path, # Запись пути к файлу в базу
                status_id = Status.in_work.value,
                employeeId = employeeId                
            )
            db.session.add(new_memo)
            db.session.commit()
            
        flash('Служебная записка успешно отправлена!', 'success')
        return '', 200

    return render_template('add_memo.html', executors=executors)  #  Передаем executors в шаблон

@app.route('/resend/<int:task_id>', methods=['POST'])
@login_required
def resend(task_id):
    if not current_user.is_admin and not current_user.is_deputy:  # Проверка прав
        flash('У вас нет прав для создания задач.', 'danger')
        return redirect(url_for('index'))

    # Генерируем new_task_id для новой задачи
    new_task_id = str(len(Task.query.all()) + 1)
    task = Task.query.get_or_404(task_id)
    
    # Пока что меняем статус только для задач. Для служебных записок не меняем.
    if not task.for_review:
        task.status_id = Status.pending.value

    executor_for_task_id = request.json.get('executors').split(',')
    if 'all' in executor_for_task_id:
        executor_for_task_id = [executor.id for executor in User.query.filter(User.is_deleted == False).all() if executor.id != current_user.id]
    task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], new_task_id, 'creator')
    os.makedirs(task_uploads_folder, exist_ok=True)

    date_created = datetime.now()
    is_бессрочно = task.is_бессрочно
    deadline = task.deadline
    description = task.description
    is_valid = task.is_valid
    for_review = task.for_review

    try:        
        creator_file_path = ''
        uploadFolder = os.getcwd() + '/' + app.config['UPLOAD_FOLDER'] + '/'

        file_path_arr = task.creator_file.split(';')
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
        if str(executor_id) in app.config['CanGetResendedTasksArr']:
            employeeId = request.json.get('employee') or None
        else:
            employeeId = None

        new_task = Task(
            executor_id=executor_id,
            date_created=date_created,
            deadline=deadline,
            description=description,
            is_valid=is_valid,
            is_бессрочно=is_бессрочно,
            creator_id=current_user.id,
            employeeId = employeeId,
            for_review=for_review,
            creator_file=creator_file_path,
            parent_task_id = task_id
        )
        db.session.add(new_task)
        db.session.commit()

    flash('Задача успешно добавлена!', 'success')
    return '', 200



@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    if task.creator_id != current_user.id and not current_user.is_admin:  # Проверка прав
        flash('У вас нет прав для редактирования этой задачи.', 'danger')
        return redirect(url_for('index'))

    executors = User.query.all()
    if request.method == 'POST':
        task.executor_id = request.form['executor']
        task.description = request.form['description']
        
        if (request.form.get('is_valid') == 'on'):
            task.is_valid = True
        else:
            task.is_valid = False
            task.status_id = Status.invalid.value
            
        task.edit_datetime = datetime.now()
        task.is_бессрочно = request.form.get('is_бессрочно') == 'on'
        files = request.files.getlist('files') #массив файлов
        
        if str(task.executor_id) in app.config['CanGetResendedTasksArr']:
            task.employeeId = request.form.get('employee') or None
        else:
            task.employeeId = None

        
        if (current_user.is_admin or current_user.is_deputy):
            task.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() if not task.is_бессрочно else None
            extend_deadline = request.form.get('extend_deadline')
            if extend_deadline:
                try:
                    extended_deadline_date = datetime.strptime(request.form['extended_deadline'], '%Y-%m-%d').date()
                    task.extended_deadline = extended_deadline_date
                except ValueError:
                    flash("Некорректный формат даты продления", "danger")
                    return render_template('edit.html', task=task,
                                                        executors=executors,
                                                        current_user = current_user,
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

                    memo_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id, 'creator') # Папка для всех записок
                    os.makedirs(memo_uploads_folder, exist_ok=True)

                    # Сохранение файла
                    file.save(os.path.join(memo_uploads_folder, filename)) 
                    tmp_file_path = os.path.join(task_id, 'creator', filename)
                    tmp_file_path = tmp_file_path.replace('\\', '/') # Запись пути к файлу в базу
                    creator_file_path += tmp_file_path + ';'
            task.creator_file = creator_file_path
        
        db.session.commit()
        flash('Задача успешно отредактирована!', 'success')
        return '', 200

    return render_template('edit.html', task=task,
                                        executors=executors,
                                        current_user = current_user,
                                        datetime=datetime)



@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.creator_id != current_user.id and not current_user.is_admin:  # Проверка прав
        flash('У вас нет прав для удаления этой задачи.', 'danger')
        return redirect(url_for('index'))

    task.is_deleted = True
    task.when_deleted = datetime.now()
    
    db.session.commit()
    flash('Задача успешно удалена!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/complete/<int:task_id>', methods=['GET', 'POST'])
@login_required
def complete(task_id):
    task = Task.query.get_or_404(task_id)

    if current_user.id != task.executor_id:
        flash('Вы можете изменять только свои задачи.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':

        file = request.files.get('file')  # Получаем файл, если он есть

        if file and file.filename != '':
            filename = file.filename  # Оригинальное имя
            
            task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(task_id), 'executor')
            os.makedirs(task_uploads_folder, exist_ok=True)

            file.save(os.path.join(task_uploads_folder, filename)) # Сохраняем с оригинальным именем!

            task.attached_file = os.path.join(str(task_id), 'executor', filename) #  Оригинальное имя в базе
            task.attached_file = task.attached_file.replace('\\', '/')



        task.completion_note = request.form.get('completion_note')
        task.completion_confirmed = False
        task.status_id = Status.at_check.value
        db.session.commit()
        flash('Отметка о выполнении отправлена администратору.', 'success')
        return '', 200

    return render_template('complete.html', task=task)


@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    uploads_folder = app.config['UPLOAD_FOLDER']
    safe_path = safe_join(uploads_folder, filename) # Используем safe_join
    if safe_path and os.path.exists(safe_path):
       return send_from_directory(uploads_folder, filename, as_attachment=True)
    else:
        flash(f"File not found: {filename}")
        return redirect(url_for('index'))

@app.route('/admin/tasks/<int:task_id>/confirm', methods=['POST'])
@login_required
def confirm_task(task_id):
    if not current_user.is_admin:
        flash('У вас нет прав для подтверждения выполнения задач.', 'danger')
        return redirect(url_for('index'))
    
    task = Task.query.get_or_404(task_id)
    task.completion_confirmed = True
    task.completion_confirmed_at = datetime.now()
    task.admin_note = request.json.get('note')
    
    if task.deadline:
        if(task.get_deadline_for_check() < datetime.now().date()):
            task.status_id = Status.complete_delayed.value
        else:
            task.status_id = Status.completed.value
    else:
        task.status_id = Status.completed.value
        
    db.session.commit()
    flash('Выполнение задачи подтверждено.', 'success')
    return '', 200


@app.route('/admin/tasks/<int:task_id>/reject', methods=['POST'])
@login_required
def reject_task(task_id):
    if not current_user.is_admin:
        flash('У вас нет прав для отклонения выполнения задач.', 'danger')
        return redirect(url_for('index'))
    
    task = Task.query.get_or_404(task_id)

    if task.attached_file != None and task.attached_file != "":
        os.remove(task.attached_file)
    task.attached_file = None
    task.completion_note = None
    task.completion_confirmed = False
    task.admin_note = request.json.get('note')
    task.status_id = Status.in_work.value
    db.session.commit()
    flash('Выполнение задачи отклонено.', 'warning')
    return '', 200

@app.route('/deputy/tasks/<int:task_id>/confirm', methods=['POST'])
@login_required
def confirm_task_deputy(task_id):
    if not current_user.is_deputy:
        flash('У вас нет прав для подтверждения выполнения задач.', 'danger')
        return redirect(url_for('index'))
    
    task = Task.query.get_or_404(task_id)
    if task.creator_id != current_user.id:
        flash('Вы можете подтверждать только задачи, которые вы выдали.', 'danger')
        return redirect(url_for('index'))

    task.completion_confirmed = True
    task.completion_confirmed_at = datetime.now()
    task.admin_note = request.json.get('note')
    
    if task.deadline:
        if(task.get_deadline_for_check() < task.completion_confirmed_at.date()):
            task.status_id = Status.complete_delayed.value
        else:
            task.status_id = Status.completed.value
    else:
        task.status_id = Status.completed.value
        
    # Если задача была дочерней, то работаем с родителем
    if task.parent_task_id != None:
        parentTask = Task.query.filter_by(id = task.parent_task_id).first()
        
        # Пока что для служебных записок с родителем ничего не делаем
        # Также проверяем, что родительская таска сама в работе
        if parentTask != None and (not parentTask.for_review) and (parentTask.status_id == Status.in_work.value or parentTask.status_id == Status.delayed.value or parentTask.status_id == Status.pending.value): 
            parentTask.status_id = Status.at_check.value
            parentTask.completion_note = task.completion_note
            parentTask.completion_confirmed = False
                
            # Работа с файлами
            try:        
                exev_file_path = ''
                task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(task.parent_task_id), 'executor')
                uploadFolder = os.getcwd() + '/' + app.config['UPLOAD_FOLDER'] + '/'
                if not os.path.exists(uploadFolder):
                    os.makedirs(uploadFolder)
                os.makedirs(task_uploads_folder, exist_ok=True)

                if task.attached_file:
                    file_path_arr = task.attached_file.split(';')
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
                        exev_file_path += tmp_file_path # когда сделаем многофайловую загрузку - дописать + ';'
            except Exception as e:
                s = str(e)
                flash("Произошла ошибка: " + s, 'danger')
                return '', 500   
                
            parentTask.attached_file = exev_file_path
                
    db.session.commit()
    flash('Выполнение задачи подтверждено.', 'success')
    return '', 200

@app.route('/deputy/tasks/<int:task_id>/reject', methods=['POST'])
@login_required
def reject_task_deputy(task_id):
    if not current_user.is_deputy:
        flash('У вас нет прав для отклонения задач.', 'danger')
        return redirect(url_for('index'))
    
    task = Task.query.get_or_404(task_id)
    if task.creator_id != current_user.id:
        flash('Вы можете отклоненять только задачи, которые вы выдали.', 'danger')
        return redirect(url_for('index'))

    if task.attached_file != None and task.attached_file != "":
        os.remove(task.attached_file)
    task.attached_file = None
    task.completion_note = None
    task.completion_confirmed = False
    task.admin_note = request.json.get('note')
    task.status_id = Status.in_work.value
    
    db.session.commit()
    flash('Выполнение задачи отклонено.', 'warning')
    return '', 200

@app.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(url_for('index'))
    users = User.query.filter(User.is_deleted == False).all()
    return render_template('users.html', users=users)


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('У вас нет прав для создания пользователей.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        department = request.form['department']
        login = request.form['login']
        password = request.form['password']
        is_admin = request.form.get('is_admin') == 'on'
        is_deputy = request.form.get('is_deputy') == 'on' # Добавляем проверку на is_deputy

        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует.', 'danger')
            return redirect(url_for('add_user'))

        hashed_password = generate_password_hash(password)
        new_user = User(department=department, login=login, password_hash=hashed_password, is_admin=is_admin, is_deputy=is_deputy)
        db.session.add(new_user)
        db.session.commit()
        flash('Пользователь успешно добавлен!', 'success')
        return redirect(url_for('users'))
    return render_template('add_user.html')


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('У вас нет прав для удаления пользователей.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    
    user.is_deleted = True
    user.when_deleted = datetime.now()
    
    db.session.commit()
    flash('Пользователь успешно удален!', 'success')
    return redirect(url_for('users'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Вы успешно авторизовались!', 'success')
            return redirect(url_for('index', sn = 'in', p=1))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        department = request.form['department']
        login = request.form['login']
        password = request.form['password']

        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(department=department, login=login, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not current_user.check_password(old_password):
            flash('Неверный текущий пароль', 'danger')
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash('Новый пароль и подтверждение не совпадают', 'danger')
            return redirect(url_for('change_password'))

        current_user.set_password(new_password)
        db.session.commit()
        flash('Пароль успешно изменен!', 'success')
        return redirect(url_for('index'))  # Перенаправляем на главную после смены пароля
    return render_template('change_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/review/<int:task_id>', methods=['GET', 'POST'])
@login_required
def review(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':  #  Обработка POST-запроса от кнопки "Ознакомлен"
        
        task.completion_confirmed = True
        task.completion_confirmed_at = datetime.now()
        task.status_id = Status.reviewed.value
        
        db.session.commit()
        flash('Вы ознакомились с задачей.', 'success')
        return '', 200  #  Перенаправление на главную страницу
    return render_template('review.html', task=task)

#API-метод, возвращающий список сотрудников по id отдела 
@app.route('/api/users/<int:user_id>/employees', methods=['GET'])
@login_required
def getEmployees(user_id):
    employees = Executive.query.filter(Executive.user_id == user_id).all()
    return jsonify(employees)

#API-метод, возвращающий задачу по ее id
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def getTaskById(task_id):
    task = Task.query.filter_by(id = task_id).first()
    if (not task):
        return '', 404
    return jsonify(task)

@app.route('/api/users/current_user', methods=['GET'])
@login_required
def getCurrentUser():
    user = User.query.filter_by(id = current_user.id).first()
    if (not user):
        return '', 404
    return jsonify(user)


reports_bp = Blueprint('reports', __name__) # Создаем Blueprint


@reports_bp.route('/reports')
@login_required
def reports():
    if not current_user.is_admin:
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(url_for('index'))

    all_users = User.query.filter(User.is_deleted == False).all()
    report_data = {}

    for user in all_users:
        report_data[user] = {}
        for month in range(1, 13): #  Перебираем все месяцы
            tasks_in_month = Task.query.filter(
                Task.executor_id == user.id,
                db.extract('month', Task.date_created) == month,
                Task.date_created >= date(2024,12,1) # Попросили начать отсчет с 1 декабря 2024, поэтому старые пока не учитываем
            ).all()

            total_penalty = 0
            for task in tasks_in_month:
                task.deadline_for_check = task.get_deadline_for_check() # используем метод модели
                penalty = calculate_penalty(task) # calculate_penalty(task)
                total_penalty += penalty
            report_data[user][month] = total_penalty

    return render_template('reports.html', report_data=report_data, all_users=all_users, date=date, any=any)

@app.route('/archived')
@login_required
def archived():

    filter_params_dict = {f : request.args.get(f) for f in FILTER_PARAM_KEYS if request.args.get(f)}
    page = request.args.get('p', 1, type=int)
    if current_user.is_admin:
        archived_data = Task.query.filter(Task.is_archived ==True, Task.is_deleted == False)
    else:
        archived_data = Task.query.filter(db.or_(Task.executor_id == current_user.id, Task.creator_id == current_user.id),
                                          Task.is_archived == True, Task.is_deleted == False)

    archived_data, task_count = filter_data(archived_data, page, **filter_params_dict)
    executors = User.query.filter(User.is_deleted == False).all()

    add_fields(archived_data)

    return render_template('archived.html', data = archived_data,
                                            task_count = task_count,
                                            executors = executors,
                                            per_page = PER_PAGE,
                                            page=page,
                                            filter_params_dict = filter_params_dict,
                                            time=time,
                                            date=date,
                                            datetime=datetime, 
                                            unquote = unquote,
                                            status = Status,
                                            status_dict = STATUS_DICT)


@app.route('/create_memo', methods=['GET'])
@login_required
def create_memo():
    if not current_user.is_deputy:
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(request.referrer)
    
    executors = [executor for executor in User.query.all() if executor.id != current_user.id]
    
    current_user_department = current_user.department.split(' ', maxsplit=1)
    
    if not current_user_department[0].isdigit():
        current_user_department = current_user.department
    else:
        current_user_department = current_user_department[1]
    
    return render_template('create_memo.html', executors = executors,
                                               current_user_department = current_user_department)


def filter_data(dataset, page, **params):

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
                
    if params.get('executor'):
        dataset = dataset.filter(Task.executor_id == User.query
                                                            .filter(User.department == params['executor'])
                                                            .first().id)

    if params.get('creator'):
        creator = User.query.filter(User.department == params['creator']).first()
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
    

    dataset = dataset.options(db.joinedload(Task.executor)).order_by(
        Task.is_valid.desc(),
        Task.date_created.desc(),
        Task.deadline.desc() if not Task.is_бессрочно else Task.id).paginate(page=page, per_page=PER_PAGE)
    
    return (dataset, dataset_count,)


'''
Метод, добавляющий следующие поля:
deadline_for_check - срок, который нужно проверять
creator_files - массив из расспличенной строки с путями к файлам
Необходим для главной страницы и архива
'''
def add_fields(tasks):
    for task in tasks:
        task.deadline_for_check = task.get_deadline_for_check()
        task.creator_files = task.creator_file.split(';')


def calculate_penalty(task):  
    if (task.status_id == Status.completed.value or task.status_id == Status.complete_delayed.value) and task.deadline_for_check and task.completion_confirmed_at: # task.completion_confirmed_at
        overdue_days = (task.completion_confirmed_at.date() - task.deadline_for_check).days
        if overdue_days > 0:
            max_penalty = 20
            penalty = min(overdue_days, max_penalty)
            return penalty
    return 0

app.register_blueprint(reports_bp, url_prefix='/') # Регистрируем Blueprint



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug = True)