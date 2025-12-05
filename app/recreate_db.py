from app import app, db
from app.models import User

with app.app_context():
    # Удаляем все таблицы
    db.drop_all()
    print("🗑️ Старые таблицы удалены")

    # Создаем новые
    db.create_all()
    print("✅ Новые таблицы созданы")

    # Проверяем структуру
    columns = [column.name for column in User.__table__.columns]
    print(f"📊 Колонки в таблице User: {columns}")

    # Проверяем, есть ли нужные поля
    required_fields = ['clicks_per_minute', 'click_history']
    for field in required_fields:
        if field in columns:
            print(f"✅ Поле '{field}' присутствует")
        else:
            print(f"❌ Поле '{field}' отсутствует!")