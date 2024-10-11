# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin@localhost/control_saz'
db = SQLAlchemy(app)
Bootstrap(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False) 
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
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
    executor = db.relationship('User', backref=db.backref('tasks', lazy=True))
    date_created = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    deadline = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
    completion_note = db.Column(db.Text)  
    completion_confirmed = db.Column(db.Boolean, default=False)
    completion_confirmed_at = db.Column(db.DateTime)
    admin_note = db.Column(db.Text)

    def is_overdue(self):
        return self.deadline < datetime.today().date()


@app.route('/')
@login_required
def index():
    executor_filter = request.args.get('executor')
    date_filter = request.args.get('date')

    tasks = Task.query.filter_by(executor_id=current_user.id) # Фильтрация по текущему пользователю
    
    if current_user.is_admin:
        tasks = Task.query  # Если админ, то показываем все задачи

    if executor_filter:
        tasks = tasks.filter_by(executor_id=User.query.filter_by(name=executor_filter).first().id)
    if date_filter:
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
        tasks = tasks.filter(db.cast(Task.date_created, db.Date) == date_filter)

    tasks = tasks.order_by(Task.is_valid.desc(), Task.deadline, Task.date_created.desc()).all()
    executors = User.query.all()
    return render_template('index.html', tasks=tasks, executors=executors)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_admin:
        flash('У вас нет прав для создания задач.', 'danger')
        return redirect(url_for('index'))

    executors = User.query.all()
    if request.method == 'POST':
        executor_id = request.form['executor']
        date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
        description = request.form['description']
        is_valid = request.form.get('is_valid') == 'on' 

        new_task = Task(executor_id=executor_id, date_created=date_created, deadline=deadline,
                        description=description, is_valid=is_valid)
        db.session.add(new_task)
        db.session.commit()
        flash('Задача успешно добавлена!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html', executors=executors, datetime=datetime)


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
        task.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
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
        task.completion_note = request.form.get('completion_note')
        task.completion_confirmed = False
        db.session.commit()
        flash('Отметка о выполнении отправлена администратору.', 'success')
        return redirect(url_for('index'))

    return render_template('complete.html', task=task)


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
        name = request.form['name']
        surname = request.form['surname']
        login = request.form['login']
        password = request.form['password']
        is_admin = request.form.get('is_admin') == 'on'

        new_user = User(name=name, surname=surname, login=login, is_admin=is_admin)
        new_user.set_password(password)
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
        name = request.form['name']
        surname = request.form['surname']
        login = request.form['login']
        password = request.form['password']
        
        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, surname=surname, login=login, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)