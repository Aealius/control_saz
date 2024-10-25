import os
from flask import (Flask, render_template, request, redirect, url_for, flash, send_from_directory, Blueprint)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename, safe_join
from urllib.parse import quote, unquote
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/control_saz'
app.config['JSON_AS_ASCII'] = False # Важно!
db = SQLAlchemy(app)
Bootstrap(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(255), nullable=False, default='Общая служба')
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_deputy = db.Column(db.Boolean, default=False)  # Новый атрибут для заместителя

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.login}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executor = db.relationship('User', backref=db.backref('tasks', lazy=True), foreign_keys=[executor_id])
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('created_tasks', lazy=True), foreign_keys=[creator_id])
    date_created = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    deadline = db.Column(db.Date, nullable=True)
    extended_deadline = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
    completion_note = db.Column(db.Text)
    completion_confirmed = db.Column(db.Boolean, default=False)
    completion_confirmed_at = db.Column(db.DateTime)
    admin_note = db.Column(db.Text)
    attached_file = db.Column(db.String(255))  
    creator_file = db.Column(db.String(255))  
    is_бессрочно = db.Column(db.Boolean, default=False)
    for_review = db.Column(db.Boolean, default=False)  

    def is_overdue(self):
        return self.deadline < datetime.today().date() if self.deadline is not None else False
    
    def get_deadline_for_check(self):
        return self.extended_deadline or self.deadline or date(9999, 12, 31)



@app.route('/')
@login_required
def index():
    executor_filter = request.args.get('executor')
    creator_filter = request.args.get('creator') # новый фильтр
    month_filter = request.args.get('month') # новый фильтр
    date_filter = request.args.get('date')
    overdue_filter = request.args.get('overdue') # новый фильтр
    completed_filter = request.args.get('completed') # новый фильтр

    # Начальный фильтр, если user - admin
    if current_user.is_admin:
        tasks = Task.query 
    # Начальный фильтр, если user - deputy
    elif current_user.is_deputy:
        tasks = Task.query.filter(
            db.or_(Task.executor_id == current_user.id, Task.creator_id == current_user.id)
        )
    else:
        # Если user - обычный пользователь, то видим только задачи где он - executor
        tasks = Task.query.filter_by(executor_id=current_user.id)

    if executor_filter:
        tasks = tasks.filter_by(executor_id=User.query.filter_by(department=executor_filter).first().id)
    
    if creator_filter:
        creator = User.query.filter_by(department=creator_filter).first()
        if creator:
            tasks = tasks.filter_by(creator_id=creator.id)

    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            tasks = tasks.filter(db.extract('year', Task.date_created) == year,
                                 db.extract('month', Task.date_created) == month)
        except ValueError:
            # Обработка некорректного формата месяца
            flash("Некорректный формат месяца", "danger")
    
    if date_filter:
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
        tasks = tasks.filter(db.cast(Task.date_created, db.Date) == date_filter)

    if overdue_filter:
        tasks = tasks.filter(Task.deadline < date.today())

    if completed_filter:
        tasks = tasks.filter_by(completion_confirmed = True)

    tasks = tasks.options(db.joinedload(Task.executor)).order_by(
        Task.is_valid.asc(),
        Task.completion_confirmed.asc(),
        Task.deadline.asc() if not Task.is_бессрочно else Task.id 

    ).all()


    for task in tasks:
        if task.extended_deadline:
            task.deadline_for_check = task.extended_deadline
        elif task.deadline:  # Добавляем проверку на deadline
            task.deadline_for_check = task.deadline
        else:
            task.deadline_for_check = date(9999,12,31)


    creator_department = {}
    for task in tasks:
        if task.creator_id not in creator_department:  # Проверяем creator_id, а не executor_id
            creator_department[task.creator_id] = task.creator.department
        if current_user.is_admin and task.executor and task.executor_id not in creator_department:
            creator_department[task.executor_id] = task.executor.department
        elif not current_user.is_admin and task.executor and task.executor_id not in creator_department:
            creator_department[task.executor.id] = task.executor.department

    executors = User.query.all()
    return render_template('index.html', tasks=tasks, executors=executors, 
                           creator_department=creator_department, date=date, 
                           calculate_penalty=calculate_penalty, unquote=unquote) 




@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_admin and not current_user.is_deputy:  # Проверка прав
        flash('У вас нет прав для создания задач.', 'danger')
        return redirect(url_for('index'))

    executors = User.query.all()
    if request.method == 'POST':
        selected_executors = request.form.getlist('executor[]')

        # Генерируем task_id для новой задачи
        task_id = str(len(Task.query.all()) + 1)

        # Обработка 'all'
        if 'all' in selected_executors:
            # Добавляем всех пользователей как исполнителей
            executors_for_task = User.query.all()
            task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id, 'creator')
            os.makedirs(task_uploads_folder, exist_ok=True)
        else:
            # Добавляем выбранных пользователей как исполнителей
            executors_for_task = User.query.filter(
                User.id.in_([int(executor) for executor in selected_executors])
            ).all()
            task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id, 'creator')
            os.makedirs(task_uploads_folder, exist_ok=True)

        date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
        is_бессрочно = request.form.get('is_бессрочно') == 'on'
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() if not is_бессрочно else None
        description = request.form['description']
        is_valid = request.form.get('is_valid') == 'on'
        for_review = request.form.get('for_review') == 'on'
        file = request.files.get('file')

        creator_file_path = ''
        # Сохраняем файл только один раз
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(task_uploads_folder, filename))
            creator_file_path = os.path.join('uploads', task_id, 'creator', filename)
            creator_file_path = creator_file_path.replace('\\', '/')

        for executor in executors_for_task:
            new_task = Task(
                executor_id=executor.id,
                date_created=date_created,
                deadline=deadline,
                description=description,
                is_valid=is_valid,
                creator_id=current_user.id,
                for_review=for_review,
                creator_file=creator_file_path  
            )
            db.session.add(new_task)
            db.session.commit()

        flash('Задача успешно добавлена!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html', executors=executors, datetime=datetime, current_user=current_user)

import shutil 



@app.route('/add_memo', methods=['GET', 'POST']) #  Маршрут для создания служебных записок
@login_required
def add_memo():
    executors = User.query.all()
    if request.method == 'POST':
        selected_executor_id = request.form.getlist('executor[]')  #  Получаем ID выбранного исполнителя 
        if 'all' in selected_executor_id:
            selected_executor_id = [executor.id for executor in User.query.all() if executor.id != current_user.id]
        description = request.form['description']
        file = request.files.get('file') #  Получаем файл вне цикла

        # Сохраняем файл только один раз
        if file and file.filename != '':
            filename = file.filename  # Оригинальное имя

            # Счетчик для task_id при "all"
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

            # Сохранение файла
            file.save(os.path.join(memo_uploads_folder, filename)) 
            creator_file_path = os.path.join('uploads', task_id, 'creator', filename)
            creator_file_path = creator_file_path.replace('\\', '/') # Запись пути к файлу в базу

        for executor_id in selected_executor_id:
            new_memo = Task(
                executor_id=int(executor_id), 
                creator_id=current_user.id,
                date_created=datetime.now(),
                is_бессрочно=True,
                for_review=True,
                description=description,
                creator_file=creator_file_path # Запись пути к файлу в базу
            )
            db.session.add(new_memo)
            db.session.commit()

        flash('Служебная записка успешно отправлена!', 'success')
        return redirect(url_for('index'))

    return render_template('add_memo.html', executors=executors)  #  Передаем executors в шаблон
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
        task.date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
        task.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() if request.form['deadline'] else None
        task.description = request.form['description']
        task.is_valid = request.form.get('is_valid') == 'on'
        extend_deadline = request.form.get('extend_deadline')
        if extend_deadline:
            try:
                extended_deadline_date = datetime.strptime(request.form['extended_deadline'], '%Y-%m-%d').date()
                task.extended_deadline = extended_deadline_date
            except ValueError:
                flash("Некорректный формат даты продления", "danger")
                return render_template('edit.html', task=task, executors=executors, datetime=datetime)


        db.session.commit()
        flash('Задача успешно отредактирована!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', task=task, executors=executors, datetime=datetime)



@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.creator_id != current_user.id and not current_user.is_admin:  # Проверка прав
        flash('У вас нет прав для удаления этой задачи.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(task)
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

            task.attached_file = os.path.join('uploads', str(task_id), 'executor', filename) #  Оригинальное имя в базе
            task.attached_file = task.attached_file.replace('\\', '/')
            


        task.completion_note = request.form.get('completion_note')
        task.completion_confirmed = False
        db.session.commit()
        flash('Отметка о выполнении отправлена администратору.', 'success')
        return redirect(url_for('index'))

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
    task.admin_note = request.form.get('admin_note')
    db.session.commit()
    flash('Выполнение задачи подтверждено.', 'success')
    return redirect(url_for('index'))


@app.route('/admin/tasks/<int:task_id>/reject', methods=['POST'])
@login_required
def reject_task(task_id):
    if not current_user.is_admin:
        flash('У вас нет прав для отклонения выполнения задач.', 'danger')
        return redirect(url_for('index'))

    task = Task.query.get_or_404(task_id)
    task.completion_confirmed = False
    task.admin_note = request.form.get('admin_note')
    db.session.commit()
    flash('Выполнение задачи отклонено.', 'warning')
    return redirect(url_for('index'))


@app.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
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
    db.session.delete(user)
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
            return redirect(url_for('index'))
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
        db.session.commit()
        flash('Вы ознакомились с задачей.', 'success')
        return redirect(url_for('index'))  #  Перенаправление на главную страницу
    return render_template('review.html', task=task)


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
    task.admin_note = request.form.get('admin_note')
    db.session.commit()
    flash('Выполнение задачи подтверждено.', 'success')
    return redirect(url_for('index'))


reports_bp = Blueprint('reports', __name__) # Создаем Blueprint


@reports_bp.route('/reports')
@login_required
def reports():
    if not current_user.is_admin:
        flash('У вас нет прав для просмотра этой страницы.', 'danger')
        return redirect(url_for('index'))

    all_users = User.query.all()
    report_data = {}

    for user in all_users:
        report_data[user] = {}
        for month in range(1, 13): #  Перебираем все месяцы
            tasks_in_month = Task.query.filter(
                Task.executor_id == user.id,
                db.extract('month', Task.date_created) == month
            ).all()
            
            total_penalty = 0
            for task in tasks_in_month:
                task.deadline_for_check = task.get_deadline_for_check() # используем метод модели
                penalty = calculate_penalty(task) # calculate_penalty(task)
                total_penalty += penalty
            report_data[user][month] = total_penalty

    return render_template('reports.html', report_data=report_data, all_users=all_users, date=date, any=any)


def calculate_penalty(task):  
    if task.completion_confirmed and task.deadline_for_check and task.completion_confirmed_at: # task.completion_confirmed_at
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
    app.run(host='0.0.0.0', debug=True)