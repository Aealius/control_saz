from enum import Enum

#перечисление для статусов
class Status(Enum):
    in_work = 1 #в работе
    at_check = 2 #на проверке
    reviewed = 3 #ознакомлен
    completed = 4 #выполнено
    complete_delayed = 5 #выполнено, просрочено
    delayed = 6 #просрочено
    invalid = 7 #недействительно
    pending = 8 #ожидается выполнение
    
    
    