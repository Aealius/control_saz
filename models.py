from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Инициализация db вне функции

class Executor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return self.name


def create_task_model(db):
    class Task(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        executor_id = db.Column(db.Integer, db.ForeignKey('executor.id'), nullable=False)
        executor = db.relationship('Executor', backref=db.backref('tasks', lazy=True)) 
        date_created = db.Column(db.Date, nullable=False)
        deadline = db.Column(db.Date, nullable=False)
        description = db.Column(db.Text, nullable=False)
        is_valid = db.Column(db.Boolean, default=True)

        def is_overdue(self):
            return self.deadline < datetime.today().date()

    return Task