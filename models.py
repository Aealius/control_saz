from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    executor = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)

    def is_overdue(self):
        return self.deadline < datetime.date.today()