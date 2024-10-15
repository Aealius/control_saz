from werkzeug.security import generate_password_hash
from app import db, User, app

departments = """
100 Дирекция
101 Служба по ЧС и ГО
120 ОК
121 отдел по молодежи
130 СБиР
201 ОКС
202 ОГТ
204 КО
205 ОАСУП
206 СГМ
207 СГЭ
208 ОТКиУК
209 СГР
210 ИНО
213 ООТ
230 ООТиЗ
231 ПЭО
233 ОМТС
234 Бухгалтерия
236 ФС
237 ПДО
238 УМиС
250 Хоз. служба
253 ЮрС
301 ЭнРЦ
303 ЦРТО
304 ИЦ
307 АТУ
401 Цех №1
402 Цех №2
403 Цех №3
404 Цех №4
1 Главный инжинер
2 Зам. дир. по производству
3 Зам. дир. по экономике
4 Зам. дир. по идеологии
5 Зам. дир. по безопасности
6 Зам. глав. инжинера
"""

with app.app_context():
    for line in departments.strip().split('\n'):
        department = line.strip()
        login = department.split(' ')[0] 
        password = login
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter_by(login=login).first()
        if not existing_user: 
            new_user = User(department=department, login=login, password_hash=hashed_password)
            db.session.add(new_user)

    db.session.commit()
    print("Все отделы успешно добавлены!")