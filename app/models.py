from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    clicks = db.Column(db.Integer, default=0)

    # Для расчета скорости кликов
    clicks_per_minute = db.Column(db.Float, default=0.0)
    click_history = db.Column(db.Text, default='[]')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'User {self.username} - clicks: {self.clicks} - cpm: {self.clicks_per_minute}'

@login_manager.user_loader # Этот декоратор связывает функцию
                           # с flask_login, чтобы загружать
                           # пользователя по id
def load_user(user_id):
    return User.query.get(int(user_id))
