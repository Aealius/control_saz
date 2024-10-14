from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(255), nullable=False, default='Общая служба')
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.login}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executor = db.relationship('User', backref=db.backref('tasks', lazy=True))
    date_created = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    deadline = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
    completion_note = db.Column(db.Text)
    attached_file = db.Column(db.String(255))
    completion_confirmed = db.Column(db.Boolean, default=False)
    completion_confirmed_at = db.Column(db.DateTime)
    admin_note = db.Column(db.Text)


    def is_overdue(self):
        return self.deadline < datetime.today().date()