import pymysql

# Замените placeholders на свои данные
config = {
  'user': 'root',
  'password': '',
  'host': 'localhost',
  'database': 'control_saz',
  'cursorclass': pymysql.cursors.DictCursor
}

# Создание подключения к базе данных
conn = pymysql.connect(**config)
cursor = conn.cursor()

# Выполнение запроса
cursor.execute("""
    UPDATE Task
    SET creator_file = REPLACE(creator_file, 'uploads/', ''),
        attached_file = REPLACE(attached_file, 'uploads/', '')
    WHERE creator_file LIKE 'uploads/%' OR attached_file LIKE 'uploads/%';
""")

# Сохранение изменений
conn.commit()

# Закрытие соединения
cursor.close()
conn.close()

print("Пути к файлам в базе данных обновлены!")