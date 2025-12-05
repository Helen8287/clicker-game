from flask import render_template, request, redirect, url_for, flash
from app import app, db, bcrypt
from app.models import User
from app.forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta
import json

@app.route('/')
@login_required
def index():
    return render_template('index.html') #гл стр б открываться только
                                         # при условии, что мы зарегсттрированы
                                         # и находимся в аккаунте

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: #эта ф-ция проверяет, точно ли чел зашел в аккаунт,
                                      # тогда его перенавравляет на ф-цию index, где его ждет игра
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit(): #проверка условия, точно ли мы нажали кнопку отправки формы,тогда
                                  # зашифровываем пароль
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #из формы
                                  # мы берем пароль и зашифровываем его

        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверно введены данные аккаунта', 'danger')
    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/click', methods=['POST'])
@login_required
def click():
    print(f"DEBUG: Кнопка нажата! Текущие клики: {current_user.clicks}")

    # 1. Увеличиваем счетчик кликов
    current_user.clicks += 1

    # 2. Получаем или создаем историю кликов
    if current_user.click_history:
        try:
            history = json.loads(current_user.click_history)
        except:
            history = []
    else:
        history = []

    # 3. Добавляем текущее время в историю
    now = datetime.utcnow()
    history.append(now.isoformat())  # Сохраняем как строку

    # 4. Оставляем только клики за последние 60 секунд
    sixty_seconds_ago = now - timedelta(seconds=60)
    recent_clicks = [
        click_time for click_time in history
        if datetime.fromisoformat(click_time) > sixty_seconds_ago
    ]

    # 5. Рассчитываем скорость (кликов в минуту)
    # Если есть клики за последнюю минуту, считаем скорость
    if len(recent_clicks) > 0:
        if len(recent_clicks) == 1:
            # Если только один клик за минуту - скорость 1
            current_user.clicks_per_minute = 1
        else:
            # Берем первый и последний клик за минуту
            first_click = datetime.fromisoformat(recent_clicks[0])
            last_click = datetime.fromisoformat(recent_clicks[-1])

            # Время в минутах между первым и последним кликом
            time_diff_minutes = (last_click - first_click).total_seconds() / 60

            if time_diff_minutes > 0:
                # Кликов в минуту = количество кликов / время в минутах
                current_user.clicks_per_minute = round(len(recent_clicks) / time_diff_minutes, 1)
            else:
                # Если все клики в одну секунду
                current_user.clicks_per_minute = len(recent_clicks) * 60
    else:
        current_user.clicks_per_minute = 0

    # 6. Сохраняем историю (ограничиваем размер)
    current_user.click_history = json.dumps(recent_clicks[-300:])  # Храним последние 300 кликов

    # 7. Обновляем время
    current_user.updated_at = now

    # 8. Сохраняем в БД
    try:
        db.session.commit()
        print(f"DEBUG: Клики обновлены! Новое значение: {current_user.clicks}")
        print(f"DEBUG: Скорость кликов: {current_user.clicks_per_minute}")
        flash(f'+1 клик! Всего: {current_user.clicks}', 'success')
    except Exception as e:
        print(f"DEBUG: Ошибка при сохранении: {e}")
        db.session.rollback()
        flash('Ошибка при сохранении клика', 'danger')

    return redirect(url_for('index'))