from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash
from app import db
from app.auth import bp
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        
        user = db.session.query(User).filter(User.login == login, User.is_deleted == False).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Вы успешно авторизовались!', 'success')
            return redirect(url_for('core.index', sn = 'in', p=1))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('auth/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    if request.method == 'POST':
        department = request.form['department']
        login = request.form['login']
        password = request.form['password']

        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(department=department, login=login, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not current_user.check_password(old_password):
            flash('Неверный текущий пароль', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('Новый пароль и подтверждение не совпадают', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(new_password)
        db.session.commit()
        flash('Пароль успешно изменен!', 'success')
        return redirect(url_for('core.index'))  # Перенаправляем на главную после смены пароля
    return render_template('auth/change_password.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))