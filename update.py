import os
import time
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def update():
    #  Здесь будет ваш код обновления 
    #  Например, обновление базы данных или загрузка файлов

    return render_template('update.html')


@app.route('/<path:path>')  #  Перехват всех остальных маршрутов
def catch_all(path):
    return redirect(url_for('update'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 