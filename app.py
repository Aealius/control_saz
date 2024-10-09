from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin@localhost/control_saz'
db = SQLAlchemy(app)
Bootstrap(app)
migrate = Migrate(app, db)

from models import create_task_model  # Импортируем функцию
Task = create_task_model(db)  # Импорт Task после инициализации db

@app.route('/')
def index():
    tasks = Task.query.order_by(Task.is_valid.desc(), Task.deadline, Task.date_created.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        if request.form['password'] == '1234':
            executor = request.form['executor']
            date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
            deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
            description = request.form['description']
            is_valid = request.form.get('is_valid') == 'on'

            new_task = Task(executor=executor, date_created=date_created, deadline=deadline, description=description, is_valid=is_valid)
            db.session.add(new_task)
            db.session.commit()
            flash('Задача успешно добавлена!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный пароль!', 'danger')
    return render_template('add.html')


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        if request.form['password'] == '1234':
            # Обработка редактирования задачи
            task.executor = request.form['executor']
            task.date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
            task.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
            task.description = request.form['description']
            task.is_valid = request.form.get('is_valid') == 'on'
            db.session.commit()
            flash('Задача успешно отредактирована!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный пароль!', 'danger')
    return render_template('edit.html', task=task)

@app.route('/delete/<int:task_id>', methods=['POST']) 
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if request.form['password'] == '1234':
        db.session.delete(task)
        db.session.commit()
        flash('Задача успешно удалена!', 'success')
    else:
        flash('Неверный пароль!', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 