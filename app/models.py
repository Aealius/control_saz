from typing import List, Optional
from flask_login import UserMixin
from sqlalchemy import Date, DateTime, ForeignKeyConstraint, Index, Integer, SmallInteger, String, Text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import datetime


class DocType(db.Model):
    __tablename__ = 'doc_type'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    doc_type_sub_type: Mapped[List['DocTypeSubType']] = relationship('DocTypeSubType', back_populates='doctype')


class SubType(db.Model):
    __tablename__ = 'sub_type'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    doc_type_sub_type: Mapped[List['DocTypeSubType']] = relationship('DocTypeSubType', back_populates='subtype')


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = (
        Index('login', 'login', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_deleted: Mapped[bool] = mapped_column(TINYINT(1), default=False)
    full_department: Mapped[Optional[str]] = mapped_column(String(1000))
    is_admin: Mapped[Optional[bool]] = mapped_column(TINYINT(1))
    is_deputy: Mapped[Optional[bool]] = mapped_column(TINYINT(1))
    when_deleted: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    executive: Mapped[List['Executive']] = relationship('Executive', back_populates='user')
    head: Mapped[List['Head']] = relationship('Head', back_populates='user')
    tech_message: Mapped[List['TechMessage']] = relationship('TechMessage', back_populates='user')
    task: Mapped[List['Task']] = relationship('Task', foreign_keys='[Task.creator_id]', back_populates='creator')
    task_: Mapped[List['Task']] = relationship('Task', foreign_keys='[Task.executor_id]', back_populates='executor')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, with_head = False):
        data = {
            'id': self.id,
            'department': self.department,
            'full_department': self.full_department,
            'login': self.login,
           #'password_hash': self.,
           #'is_deleted': self.,
           #'when_deleted': self.,
            'is_admin': self.is_admin,
            'is_deputy': self.is_deputy,
        }
        
        if with_head:
            data.update({'head' : []})
            for head in self.head:
                data['head'].append(head.to_dict())
        return data


class DocTypeSubType(db.Model):
    __tablename__ = 'doc_type_sub_type'
    __table_args__ = (
        ForeignKeyConstraint(['doctype_id'], ['doc_type.id'], name='doc_type_sub_type_ibfk_1'),
        ForeignKeyConstraint(['subtype_id'], ['sub_type.id'], name='doc_type_sub_type_ibfk_2'),
        Index('doctype_id', 'doctype_id'),
        Index('subtype_id', 'subtype_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctype_id: Mapped[int] = mapped_column(Integer)
    counter: Mapped[int] = mapped_column(Integer)
    subtype_id: Mapped[Optional[int]] = mapped_column(Integer)

    doctype: Mapped['DocType'] = relationship('DocType', back_populates='doc_type_sub_type')
    subtype: Mapped['SubType'] = relationship('SubType', back_populates='doc_type_sub_type')
    task: Mapped[List['Task']] = relationship('Task', back_populates='doctype')
    
    def to_dict(self):
        data = {
            'id': self.id,
            'doctype_id': self.doctype_id,
            'subtype_id': self.subtype_id,
            'counter': self.counter,
        }
        return data


class Executive(db.Model):
    __tablename__ = 'executive'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], name='executive_ibfk_1'),
        Index('user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    surname: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(Integer)
    patronymic: Mapped[Optional[str]] = mapped_column(String(255))

    user: Mapped['User'] = relationship('User', back_populates='executive')
    task: Mapped[List['Task']] = relationship('Task', back_populates='executive')
    
    def to_dict(self):
        data = {
            'id':self.id,
            'name':self.name,
            'surname':self.surname,
            'user_id':self.user_id,
            'patronymic':self.patronymic,
        }
        return data
    


class Head(db.Model):
    __tablename__ = 'head'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], name='head_ibfk_1'),
        Index('user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    surname: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(1000))
    patronymic: Mapped[Optional[str]] = mapped_column(String(255))
    signature_path: Mapped[Optional[str]] = mapped_column(String(1000))

    user: Mapped['User'] = relationship('User', back_populates='head')
    
    def to_dict(self):
        data = {
            'id': self.id,
            'user_id':self.user_id,
            'name':self.name,
            'surname':self.surname,
            'position':self.position,
            'patronymic':self.patronymic,
            'signature_path':self.signature_path,
        }
        return data


class Task(db.Model):
    __tablename__ = 'task'
    __table_args__ = (
        ForeignKeyConstraint(['creator_id'], ['user.id'], name='task_ibfk_1'),
        ForeignKeyConstraint(['doctype_id'], ['doc_type_sub_type.id'], ondelete='SET NULL', name='task_ibfk_6'),
        ForeignKeyConstraint(['employeeId'], ['executive.id'], name='task_ibfk_3'),
        ForeignKeyConstraint(['executor_id'], ['user.id'], name='task_ibfk_4'),
        ForeignKeyConstraint(['parent_task_id'], ['task.id'], ondelete='SET NULL', name='task_ibfk_5'),
        Index('creator_id', 'creator_id'),
        Index('doctype_id', 'doctype_id'),
        Index('employeeId', 'employeeId'),
        Index('executor_id', 'executor_id'),
        Index('parent_task_id', 'parent_task_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    executor_id: Mapped[int] = mapped_column(Integer)
    creator_id: Mapped[int] = mapped_column(Integer)
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(Text)
    is_archived: Mapped[bool] = mapped_column(TINYINT(1), default=False)
    status_id: Mapped[int] = mapped_column(SmallInteger, default=1)
    is_deleted: Mapped[bool] = mapped_column(TINYINT(1), default=False)
    deadline: Mapped[Optional[datetime.date]] = mapped_column(Date)
    extended_deadline: Mapped[Optional[datetime.date]] = mapped_column(Date)
    edit_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    completion_note: Mapped[Optional[str]] = mapped_column(Text)
    completion_confirmed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    admin_note: Mapped[Optional[str]] = mapped_column(Text)
    attached_file: Mapped[Optional[str]] = mapped_column(String(255))
    creator_file: Mapped[Optional[str]] = mapped_column(String(2048))
    for_review: Mapped[Optional[bool]] = mapped_column(TINYINT(1), default=False)
    employeeId: Mapped[Optional[int]] = mapped_column(Integer)
    parent_task_id: Mapped[Optional[int]] = mapped_column(Integer)
    when_deleted: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    doctype_id: Mapped[Optional[int]] = mapped_column(Integer)
    docnum: Mapped[Optional[int]] = mapped_column(Integer)

    creator: Mapped['User'] = relationship('User', foreign_keys=[creator_id], back_populates='task')
    doctype: Mapped['DocTypeSubType'] = relationship('DocTypeSubType', back_populates='task')
    executive: Mapped['Executive'] = relationship('Executive', back_populates='task')
    executor: Mapped['User'] = relationship('User', foreign_keys=[executor_id], back_populates='task_')
    parent_task: Mapped['Task'] = relationship('Task', remote_side=[id], back_populates='parent_task_reverse')
    parent_task_reverse: Mapped[List['Task']] = relationship('Task', remote_side=[parent_task_id], back_populates='parent_task')
    
    def is_overdue(self):
        return self.deadline < datetime.today().date() if self.deadline is not None else False
    
    def get_deadline_for_check(self):
        return self.extended_deadline or self.deadline or datetime.datetime(9999, 12, 31).date()
    
    
    def to_dict(self):
        data = {
            'id': self.id,
            'executor_id':self.executor_id,
            'creator_id':self.creator_id,
            'date_created':self.date_created,
            'description':self.description,
            'is_archived':self.is_archived,
            'status_id':self.status_id,
            'is_deleted':self.is_deleted,
            'deadline':self.deadline,
            'extended_deadline':self.extended_deadline,
            'edit_datetime':self.edit_datetime,
            'completion_note':self.completion_note,
            'completion_confirmed_at':self.completion_confirmed_at,
            'admin_note':self.admin_note,
            'attached_file':self.attached_file,
            'creator_file':self.creator_file,
            'for_review':self.for_review,
            'employeeId':self.employeeId,
            'parent_task_id':self.parent_task_id,
            'when_deleted':self.when_deleted,
            'doctype_id':self.doctype_id,
            'docnum':self.docnum,
        }
        return data

class TechMessage(db.Model):
    __tablename__ = 'tech_message'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], name='tech_message_ibfk_1'),
        Index('user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(2048))
    comp_number: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime)

    user: Mapped['User'] = relationship('User', back_populates='tech_message')
    
    def to_dict(self):
        data = {
            'id':self.id,
            'description':self.description,
            'comp_number':self.comp_number,
            'date_created':self.date_created,
            'user_id':self.user_id
        }
        return data