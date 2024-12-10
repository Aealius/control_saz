from app import db
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from dataclasses import dataclass
from datetime import datetime, date


@dataclass(unsafe_hash=True)
class User(UserMixin, db.Model):
    id:int
    department:str
    login:str
    is_admin:bool
    is_deputy:bool
    
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(255), nullable=False, default='Общая служба')
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_deputy = db.Column(db.Boolean, default=False)  # Новый атрибут для заместителя
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    when_deleted = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@dataclass
class Task(db.Model):
    id: int
    executor_id: int
    creator_id: int
    date_created: datetime
    deadline: datetime
    extended_deadline: datetime
    edit_datetime: datetime
    description: str
    is_valid: bool
    completion_note: str
    completion_confirmed: bool
    completion_confirmed_at: datetime
    admin_note: str
    attached_file: str
    creator_file: str
    is_бессрочно: bool
    for_review: bool
    employeeId: int
    is_archived: bool
    status_id: int
    parent_task_id: int
    
    id = db.Column(db.Integer, primary_key=True)
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    executor = db.relationship('User', backref=db.backref('tasks', lazy=True), foreign_keys=[executor_id])
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('created_tasks', lazy=True), foreign_keys=[creator_id])
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #теперь datetime
    deadline = db.Column(db.Date, nullable=True)
    extended_deadline = db.Column(db.Date, nullable=True)
    edit_datetime = db.Column(db.DateTime, nullable=True) #поле, запоминающее дату последнего редактирования
    description = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
    completion_note = db.Column(db.Text)
    completion_confirmed = db.Column(db.Boolean, default=False)
    completion_confirmed_at = db.Column(db.DateTime)
    admin_note = db.Column(db.Text)
    attached_file = db.Column(db.String(255))  
    creator_file = db.Column(db.String(2048))  
    is_бессрочно = db.Column(db.Boolean, default=False)
    for_review = db.Column(db.Boolean, default=False)
    employeeId = db.Column(db.Integer, db.ForeignKey('executive.id'), nullable=True)
    employee = db.relationship('Executive', backref=db.backref('executed_tasks', lazy=True), foreign_keys=[employeeId])
    is_archived = db.Column(db.Boolean, default = False, nullable = False)
    status_id = db.Column(db.SmallInteger, default=1, nullable=False)
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id', ondelete = 'SET NULL'), nullable=True)
    parent_task =db.relationship('Task', remote_side = id, foreign_keys=parent_task_id)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    when_deleted = db.Column(db.DateTime, nullable=True)

    def is_overdue(self):
        return self.deadline < datetime.today().date() if self.deadline is not None else False
    
    def get_deadline_for_check(self):
        return self.extended_deadline or self.deadline or date(9999, 12, 31)
    
@dataclass
class Executive(db.Model):
    id: int
    name: str
    surname: str
    patronymic: str
    user_id: int

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    patronymic = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref=db.backref("executive", lazy=True), foreign_keys=[user_id])