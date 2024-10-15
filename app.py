import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin@localhost/control_saz'
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
    description = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
    completion_note = db.Column(db.Text)
    completion_confirmed = db.Column(db.Boolean, default=False)
    completion_confirmed_at = db.Column(db.DateTime)
    admin_note = db.Column(db.Text)
    attached_file = db.Column(db.String(255))  #  Файл исполнителя
    creator_file = db.Column(db.String(255))
    is_бессрочно = db.Column(db.Boolean, default=False)
    for_review = db.Column(db.Boolean, default=False)  # Поле для галочки "Для ознакомления"

    def is_overdue(self):
        return self.deadline < datetime.today().date() if self.deadline is not None else False


@app.route('/')
@login_required
def index():
    executor_filter = request.args.get('executor')
    date_filter = request.args.get('date')

    tasks = Task.query.filter_by(executor_id=current_user.id)

    if current_user.is_admin:
        tasks = Task.query  # Если админ, то показываем все задачи

    if executor_filter:
        tasks = tasks.filter_by(executor_id=User.query.filter_by(department=executor_filter).first().id)
    if date_filter:
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
        tasks = tasks.filter(db.cast(Task.date_created, db.Date) == date_filter)

    tasks = tasks.options(db.joinedload(Task.executor)).order_by(
        Task.is_valid.asc(),
        Task.completion_confirmed.asc(),
        Task.deadline.asc() if not Task.is_бессрочно else Task.id # Сортировка, если is_бессрочно is not None

    ).all()


    creator_department = {}
    for task in tasks:
        if task.creator_id not in creator_department:  # Проверяем creator_id, а не executor_id
            creator_department[task.creator_id] = task.creator.department
        if current_user.is_admin and task.executor and task.executor_id not in creator_department:
            creator_department[task.executor_id] = task.executor.department
        elif not current_user.is_admin and task.executor and task.executor_id not in creator_department:
            creator_department[task.executor.id] = task.executor.department

    executors = User.query.all()
    return render_template('index.html', tasks=tasks, executors=executors, creator_department=creator_department)



@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_admin:
        flash('У вас нет прав для создания задач.', 'danger')
        return redirect(url_for('index'))

    executors = User.query.all()
    if request.method == 'POST':
        selected_executors = request.form.getlist('executor[]')
        date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
        is_бессрочно = request.form.get('is_бессрочно') == 'on'
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() if not is_бессрочно else None
        description = request.form['description']
        is_valid = request.form.get('is_valid') == 'on'
        for_review = request.form.get('for_review') == 'on'
        file = request.files.get('file')

        #  Логика для создания задачи для всех или выбранных пользователей
        if 'all' in selected_executors:
            executors_for_task = User.query.all()
        else:
            #  Преобразуем строковые ID в целые числа
            executors_for_task = User.query.filter(User.id.in_([int(id) for id in selected_executors])).all()

        for executor in executors_for_task:
            new_task = Task(
                executor_id=executor.id,
                date_created=date_created,
                deadline=deadline,
                description=description,
                is_valid=is_valid,
                creator_id=current_user.id,
                for_review=for_review
            )
            db.session.add(new_task)
            db.session.commit()  # Сохраняем задачу, чтобы получить ее ID

            if file and file.filename != '':
                filename = secure_filename(file.filename)
                task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(new_task.id), 'creator')
                os.makedirs(task_uploads_folder, exist_ok=True)
                file.save(os.path.join(task_uploads_folder, filename))
                creator_file = os.path.join(str(new_task.id), 'creator', filename)
                new_task.creator_file = creator_file
                db.session.commit()  # Сохраняем изменения в файле задачи

        flash('Задача успешно добавлена!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html', executors=executors, datetime=datetime, current_user=current_user)

@app.route('/add_memo', methods=['GET', 'POST']) #  Маршрут для создания служебных записок
@login_required
def add_memo():
    executors = User.query.all()
    if request.method == 'POST':
        selected_executor_id = int(request.form['executor'])  #  Получаем ID выбранного исполнителя
        description = request.form['description']
        file = request.files.get('file')

        new_memo = Task(
            executor_id=selected_executor_id,
            creator_id=current_user.id,
            date_created=datetime.now(),
            is_бессрочно=True,
            for_review=True,
            description=description
        )
        db.session.add(new_memo)
        db.session.commit()

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            memo_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(new_memo.id), 'creator')
            os.makedirs(memo_uploads_folder, exist_ok=True)
            file.save(os.path.join(memo_uploads_folder, filename))
            creator_file = os.path.join(str(new_memo.id), 'creator', filename)
            new_memo.creator_file = creator_file
            db.session.commit()  

        flash('Служебная записка успешно отправлена!', 'success')
        return redirect(url_for('index'))

    return render_template('add_memo.html', executors=executors)  #  Передаем executors в шаблон

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    if not current_user.is_admin:
        flash('У вас нет прав для редактирования задач.', 'danger')
        return redirect(url_for('index'))

    task = Task.query.get_or_404(task_id)
    executors = User.query.all()
    if request.method == 'POST':
        task.executor_id = request.form['executor']
        task.date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
        task.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date() if request.form['deadline'] else None
        task.description = request.form['description']
        task.is_valid = request.form.get('is_valid') == 'on'
        db.session.commit()
        flash('Задача успешно отредактирована!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', task=task, executors=executors, datetime=datetime)


@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    if not current_user.is_admin:
        flash('У вас нет прав для удаления задач.', 'danger')
        return redirect(url_for('index'))

    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Задача успешно удалена!', 'success')
    return redirect(url_for('index'))


@app.route('/complete/<int:task_id>', methods=['GET', 'POST'])
@login_required
def complete(task_id):
    task = Task.query.get_or_404(task_id)

    if current_user.id != task.executor_id:
        flash('Вы можете изменять только свои задачи.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        file = request.files.get('file')  # Получаем файл, если он есть

        if file and file.filename != '':  # Проверяем, выбран ли файл
            filename = secure_filename(file.filename)
            task_uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(task_id), 'executor')
            os.makedirs(task_uploads_folder, exist_ok=True)
            file.save(os.path.join(task_uploads_folder, filename))
            task.attached_file = os.path.join(str(task_id), 'executor', filename)

        task.completion_note = request.form.get('completion_note')
        task.completion_confirmed = False
        db.session.commit()
        flash('Отметка о выполнении отправлена администратору.', 'success')
        return redirect(url_for('index'))

    return render_template('complete.html', task=task)


@app.route('/uploads/<path:filename>')  # <path:filename> для подпапок
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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

        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует.', 'danger')
            return redirect(url_for('add_user'))

        hashed_password = generate_password_hash(password)
        new_user = User(department=department, login=login, password_hash=hashed_password, is_admin=is_admin)
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)