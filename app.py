from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/database_name'
db = SQLAlchemy(app)
Bootstrap(app)

from models import Task

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        if request.form['password'] == '1234':
            # Обработка добавления задачи
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

# Аналогично реализуем edit и delete с проверкой пароля

if __name__ == '__main__':
    app.run(debug=True)