from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from models import db, create_task_model, Executor 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin@localhost/control_saz' 
db.init_app(app)
Bootstrap(app)
migrate = Migrate(app, db)

Task = create_task_model(db)

@app.route('/')
def index():
    executor_filter = request.args.get('executor')
    date_filter = request.args.get('date')

    tasks = Task.query
    if executor_filter:
        tasks = tasks.filter_by(executor_id=Executor.query.filter_by(name=executor_filter).first().id) 
    if date_filter:
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
        tasks = tasks.filter(db.cast(Task.date_created, db.Date) == date_filter) 

    tasks = tasks.order_by(Task.is_valid.desc(), Task.deadline, Task.date_created.desc()).all()
    executors = Executor.query.all()
    return render_template('index.html', tasks=tasks, executors=executors)


@app.route('/add', methods=['GET', 'POST'])
def add():
    executors = Executor.query.all()
    if request.method == 'POST':
        if request.form['password'] == '1234':
            executor_name = request.form['executor']
            executor = Executor.query.filter_by(name=executor_name).first()
            if not executor:
                new_executor = Executor(name=executor_name)
                db.session.add(new_executor)
                db.session.commit()
                executor = new_executor 

            date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
            deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
            description = request.form['description']
            is_valid = request.form.get('is_valid') == 'on'

            new_task = Task(executor_id=executor.id, date_created=date_created, deadline=deadline, description=description, is_valid=is_valid)
            db.session.add(new_task)
            db.session.commit()
            flash('Задача успешно добавлена!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный пароль!', 'danger')
    return render_template('add.html', executors=executors, datetime=datetime)


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    executors = Executor.query.all()
    if request.method == 'POST':
        if request.form['password'] == '1234':
            executor_name = request.form['executor']
            executor = Executor.query.filter_by(name=executor_name).first()
            if not executor:
                new_executor = Executor(name=executor_name)
                db.session.add(new_executor)
                db.session.commit()
                executor = new_executor

            task.executor_id = executor.id
            task.date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d').date()
            task.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
            task.description = request.form['description']
            task.is_valid = request.form.get('is_valid') == 'on'
            db.session.commit()
            flash('Задача успешно отредактирована!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный пароль!', 'danger')
    return render_template('edit.html', task=task, executors=executors, datetime=datetime)


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

@app.route('/executors')
def executors():
    executors = Executor.query.all()
    return render_template('executors.html', executors=executors)

@app.route('/add_executor', methods=['GET', 'POST'])
def add_executor():
    if request.method == 'POST':
        if request.form['password'] == '1234':
            name = request.form['name']
            new_executor = Executor(name=name)
            db.session.add(new_executor)
            db.session.commit()
            flash('Исполнитель успешно добавлен!', 'success')
            return redirect(url_for('executors'))
        else:
            flash('Неверный пароль!', 'danger')
    return render_template('add_executor.html')


@app.route('/delete_executor/<int:executor_id>', methods=['POST'])
def delete_executor(executor_id):
    executor = Executor.query.get_or_404(executor_id)
    if request.form['password'] == '1234':
        db.session.delete(executor)
        db.session.commit()
        flash('Исполнитель успешно удален!', 'success')
    else:
        flash('Неверный пароль!', 'danger')
    return redirect(url_for('executors'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(host='0.0.0.0', debug=True) 