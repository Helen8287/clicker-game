from app import app, db
from app.models import User

with app.app_context():
    columns = [column.name for column in User.__table__.columns]
    print(f"Колонки в таблице User: {columns}")

    # Проверьте конкретного пользователя
    user = User.query.first()
    if user:
        print(f"Пользователь: {user.username}")
        print(f"Клики: {user.clicks}")
        print(f"CPM: {user.clicks_per_minute}")
        print(f"История: {user.click_history[:50]}...")