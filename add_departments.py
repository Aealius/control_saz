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
203 БППиТД
204 КО
204/1 КО, ОЭУ
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
238/1 Бюро реал.на внутр.рынке
238/2 реал.на внеш.рынках
238/3 Группа тамож.оф. и ст.отч
238/5 СГП
250/0 Хоз. служба
250/1 РСБ
250/2 Столовая
250/3 Здравпункт
250/5 ПМ
250/6 АБК
251 ЖЭУ
252 здрав.пункт
253 ЮрС
301 ЭнРЦ
302 Уч.теплогазоводоснабжения
302/1 Станция промводоснабжения
302/2 Котельная
303 ЦРТО
304 ИЦ
304/1 ИЦ, ТУ
307 АТУ
401 Цех №1
401/2 Цех №1 участок №2
401/3 Цех №1 участок №3
402 Цех №2
403 Цех №3
403/1 Сборочный участок (сб. минитехники)
403/2 Сборочный участок (сб.садов.тракт.)
404 Цех №4
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