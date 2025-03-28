import psycopg2
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

from config import Articles, db, User2, Role2, Dealers, Restaurants, Orders, OrderGoods
from forms import RegistrationForm, RoleForm, AssignRoleForm, AddGoodForm, AddDealerForm, RestaurantsNew

app = Flask(__name__)
app.secret_key = '1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)
# Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Устанавливаем русскую локаль для отображения месяцев
# Словарь с русскими названиями месяцев
MONTHS_RU = {
    "January": "Январь", "February": "Февраль", "March": "Март",
    "April": "Апрель", "May": "Май", "June": "Июнь",
    "July": "Июль", "August": "Август", "September": "Сентябрь",
    "October": "Октябрь", "November": "Ноябрь", "December": "Декабрь"
}
def format_date(date):
    english_month = date.strftime("%B")  # Получаем месяц на английском
    russian_month = MONTHS_RU.get(english_month, english_month)  # Переводим в русский
    return f"{date.strftime('%d')} {russian_month} {date.strftime('%H:%M')}"  # Формат: 25 Январь 14:30

app.jinja_env.filters['format_date'] = format_date

@login_manager.user_loader
def load_user(user_id):
    return User2.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()
    # Проверка, существует ли роль "user"
    if not Role2.query.filter_by(name='user').first():
        user_role = Role2(name='user', description='Обычный пользователь')
        db.session.add(user_role)
        db.session.commit()
    # Проверка, существует ли роль "admin"
    if not Role2.query.filter_by(name='admin').first():
        admin_role = Role2(name='admin', description='Администратор')
        db.session.add(admin_role)
        db.session.commit()

# Декоратор для проверки ролей
def role_required(role_name):
    def decorator(f):
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.has_role(role_name):
                flash('Доступ запрещён.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper

    return decorator

# Регистрация пользователя с ролью "user" по умолчанию
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if User2.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует.', 'error')
            return redirect(url_for('register'))
        if User2.query.filter_by(email=email).first():
            flash('Этот адрес электронной почты уже зарегистрирован.', 'error')
            return redirect(url_for('register'))
        new_user = User2(username=username, email=email)
        new_user.set_password(password)
        # Назначение роли "user" по умолчанию
        user_role = Role2.query.filter_by(name='admin').first()
        if user_role:
            new_user.set_role(user_role)  # Ограничение на одну роль и обновление primary_role_name
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User2.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Вы вошли в систему!', 'success')
            return redirect(url_for('dashboard'))
        flash('Неверные данные.', 'error')
    return render_template('login.html')

# Панель управления
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Управление ролями (только для админов)
@app.route('/roles', methods=['GET', 'POST'])
@role_required('admin')
def manage_roles():
    form = RoleForm()
    roles = Role2.query.all()
    if form.validate_on_submit():
        new_role = Role2(name=form.name.data, description=form.description.data)
        db.session.add(new_role)
        db.session.commit()
        flash('Роль добавлена!', 'success')
        return redirect(url_for('manage_roles'))
    return render_template('manage_roles.html', form=form, roles=roles)

@app.route('/show_users')  # Список пользователей
@role_required('admin')
def show_users():
    user2 = User2.query.order_by(User2.id).all()
    role2 = Role2.query.order_by(Role2.id).all()
    return render_template('all_users.html', user2=user2, role2=role2)

# Назначение ролей пользователям (только для админов)
@app.route('/assign_role/<int:user_id>', methods=['GET', 'POST'])
@role_required('admin')
def assign_role(user_id):
    user = User2.query.get_or_404(user_id)
    form = AssignRoleForm()
    # Подгружаем список ролей для выбора
    form.roles.choices = [(role.id, role.name) for role in Role2.query.all()]
    if form.validate_on_submit():
        selected_role = Role2.query.get(form.roles.data)  # Выбираем одну роль
        if selected_role:
            user.role_id = selected_role.id  # Обновляем role_id
            user.role_name = selected_role.name  # Обновляем имя роли
            db.session.commit()  # Сохраняем изменения в БД
            flash("Роль пользователя успешно обновлена!", "success")
        else:
            flash("Ошибка: выбранная роль не найдена!", "error")
        return redirect(url_for('show_users'))
    # Устанавливаем текущее значение роли в форме
    form.roles.data = user.role_id
    return render_template('assign_role.html', form=form, user=user)

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('login'))

@app.route("/add_dealer", methods=["GET", "POST"])
def add_dealer():
    form = AddDealerForm()
    if form.validate_on_submit():
        new_dealer = Dealers(
            name=form.name.data,
            adres=form.adres.data,
            e_mail=form.e_mail.data,
            phone=form.phone.data,
        )
        db.session.add(new_dealer)
        db.session.commit()
        flash("Dealer успешно добавлен!", "success")
        return redirect(url_for("add_dealer"))
    return render_template("adddealer.html", form=form)

@app.route("/add_restaurant", methods=["GET", "POST"])
def add_restaurant():
    form = RestaurantsNew()
    if form.validate_on_submit():
        new_restaurant = Restaurants(
            name=form.name.data,
            ur_name=form.ur_name.data,
            address=form.address.data,
        )
        db.session.add(new_restaurant)
        db.session.commit()
        flash("restaurant успешно добавлен!", "success")
        return redirect(url_for("add_restaurant"))
    return render_template("addrestaurant.html", form=form)


@app.route("/add_good", methods=["GET", "POST"])
def add_good():
    form = AddGoodForm()
    form.dealer.choices = [(dealer.id, dealer.name) for dealer in Dealers.query.all()]
    form.second_dealer.choices = [(dealer.id, dealer.name) for dealer in Dealers.query.all()]

    if form.validate_on_submit():
        selected_restaurant_ids = request.form.getlist('restaurants', type=int)
        selected_restaurants = Restaurants.query.filter(Restaurants.id.in_(selected_restaurant_ids)).all()

        # Получаем объекты дилеров
        dealer_obj = Dealers.query.get(form.dealer.data)
        second_dealer_obj = Dealers.query.get(form.second_dealer.data) if form.second_dealer.data else None

        new_good = Articles(
            article=form.article.data,
            name=form.name.data,
            dealer=dealer_obj,  # Передаем объект дилера
            price=form.price.data,
            type=form.type.data,
            multiplicity=form.multiplicity.data,
            unit=form.unit.data,
            restaurants=selected_restaurants,
            second_dealer=second_dealer_obj,  # Передаем объект второго дилера
            second_price=form.second_price.data,
        )
        db.session.add(new_good)
        db.session.commit()
        flash("Товар успешно добавлен!", "success")
        return redirect(url_for("add_good"))

    return render_template("addgoods.html", form=form, Restaurants=Restaurants)

@app.route('/show_goods')  # Список товаров
def show_goods():
    articles = Articles.query.order_by(Articles.id).all()
    return render_template('allgoods.html', articles=articles)

@app.route('/show_goods', methods=["POST"])  # Удаление товаров из списка
def delete_good():
    articles = Articles.query.order_by(Articles.id).all()
    conn = psycopg2.connect(
        host="localhost",
        database="flask",
        user="postgres",
        password="postgres"
    )
    ids = request.form.getlist('ids')  # Получаем список ID
    if ids:
        ids_tuple = tuple(map(int, ids))  # Преобразуем в tuple
        if len(ids_tuple) == 1:  # Если только 1 элемент, добавляем запятую
            ids_tuple = (ids_tuple[0],)
        with conn:
            with conn.cursor() as curs:
                # Удаляем сначала зависимости, потом сам товар
                curs.execute("DELETE FROM article_restaurants WHERE article_id IN %s", (ids_tuple,))
                curs.execute("DELETE FROM dealer_articles WHERE article_id IN %s", (ids_tuple,))
                curs.execute("DELETE FROM order_goods WHERE article_id IN %s", (ids_tuple,))
                curs.execute("DELETE FROM articles WHERE id IN %s", (ids_tuple,))
        flash(f"Удалено {len(ids)} записей!", "success")
    conn.close()
    return render_template('allgoods.html', articles=articles)

@app.route('/show_dealers')  # Список товаров
def show_dealers():
    dealers = Dealers.query.order_by(Dealers.id).all()
    return render_template('all_dealers.html', dealers=dealers)

@app.route('/show_dealers', methods=["POST"])  # Удаление dealer из списка
def delete_dealer():
    conn = psycopg2.connect(
        host="localhost",
        database="flask",
        user="postgres",
        password="postgres"
    )
    ids = request.form.getlist('ids')
    if ids:
        ids_tuple = tuple(map(int, ids))
        query = "DELETE FROM dealers WHERE id IN %s"
        with conn:
            with conn.cursor() as curs:
                curs.execute(query, (ids_tuple,))
        flash(f"Удалено {len(ids)} записей!", "success")
    conn.close()
    dealers = Dealers.query.order_by(Dealers.id).all()
    return render_template('all_dealers.html', dealers=dealers)

@app.route('/restaurants')
def restaurants():
    restaurants = Restaurants.query.order_by(Restaurants.id).all()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/update_good/<int:id>')  # Переход к конкретному товару
def update_good(id):
    article = Articles.query.get_or_404(id)
    # Получаем список всех ресторанов для отображения (включая связанных)
    all_restaurants = Restaurants.query.all()
    # Получаем список ID ресторанов, связанных с этим товаром
    associated_restaurant_ids = [r.id for r in article.restaurants]
    return render_template('article.html', article=article, all_restaurants=all_restaurants,
                           associated_restaurant_ids=associated_restaurant_ids)

@app.route('/update_good/<int:id>', methods=["POST"])  # Изменение в товаре
def update_goods(id):
    article = Articles.query.get_or_404(id)
    conn = psycopg2.connect(
        host="localhost",
        database="flask",
        user="postgres",
        password="postgres"
    )
    with conn:
        with conn.cursor():
            article_data = request.form
            article.article = article_data.get('article', article.article)
            article.name = article_data.get('name', article.name)
            article.dealer_name = article_data.get('dealer_name', article.dealer_name)
            article.type = article_data.get('type', article.type)
            article.price = float(article_data.get('price', article.price)) if article_data.get(
                'price') else article.price
            article.multiplicity = article_data.get('multiplicity', article.multiplicity)
            article.unit = article_data.get('unit', article.unit)
            article.second_dealer = article_data.get('second_dealer', article.second_dealer)
            article.second_price = article_data.get('second_price', article.second_price)
            # Обработка ресторанов
            selected_restaurant_ids = request.form.getlist('restaurants', type=int)
            selected_restaurants = Restaurants.query.filter(Restaurants.id.in_(selected_restaurant_ids)).all()
            article.restaurants = selected_restaurants  # Обновляем список ресторанов
            db.session.commit()  # Сохраняем изменения в БД
            flash("Товар успешно обновлён!", "success")
            return redirect(url_for("show_goods"))
    conn.close()
    return render_template('article.html', article=article)

@app.route('/edit_dealer/<int:dealer_id>', methods=["GET", "POST"])  # Изменение в dealer
def edit_dealer(dealer_id):
    dealer = Dealers.query.get_or_404(dealer_id)
    form = AddDealerForm(obj=dealer)
    if form.validate_on_submit():
        old_name = dealer.name  # Старое имя дилера
        new_name = form.name.data  # Новое имя
        try:
            with db.session.begin_nested():  # Используем вложенную транзакцию
                # 1️⃣ Сначала обновляем dealerName в articles
                db.session.execute("UPDATE articles SET dealer = :new_name WHERE dealer = :old_name",
                                   {"new_name": new_name, "old_name": old_name})
                # 2️⃣ Теперь обновляем имя в таблице dealers
                dealer.name = new_name
                dealer.adres = form.adres.data
                dealer.e_mail = form.e_mail.data
                dealer.phone = form.phone.data
            db.session.commit()  # Фиксируем транзакцию
            flash("Dealer edited successfully", "success")
            return redirect(url_for("show_dealers"))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка: {e}", "error")
    return render_template("edit_dealer.html", form=form, dealer=dealer)

@app.route('/create_order', methods=['GET', 'POST'])
@login_required
def create_order():
    articles = Articles.query.all()
    if request.method == 'POST':
        selected_article_ids = request.form.getlist('selected_articles')
        if not selected_article_ids:
            flash("Вы не выбрали ни одного товара!", "warning")
            return redirect(url_for('create_order'))
        new_order = Orders(user_id=current_user.id)
        db.session.add(new_order)
        db.session.commit()
        for article_id in selected_article_ids:
            article = Articles.query.get(article_id)
            quantity = request.form.get(f'quantity_{article_id}', type=int)
            # Проверяем, что количество не меньше кратности
            if quantity is None or quantity < article.multiplicity or quantity % article.multiplicity != 0:
                flash(f"Ошибка: количество товара {article.name} должно быть кратно {article.multiplicity}!", "danger")
                db.session.rollback()
                return redirect(url_for('create_order'))
            order_good = OrderGoods(order_id=new_order.id, article_id=article.id, quantity=quantity)
            db.session.add(order_good)
        db.session.commit()
        flash("Заказ успешно создан!", "success")
        return redirect(url_for('orders'))
    return render_template("create_order.html", articles=articles)

@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def view_order(order_id):
    order = Orders.query.get_or_404(order_id)

    # Назначаем dealer объектам, если не назначен
    for item in order.items:
        if not item.dealer:
            if item.dealer_id:
                item.dealer = Dealers.query.get(item.dealer_id)
            elif item.article.dealer_id:
                item.dealer_id = item.article.dealer_id
                item.dealer = item.article.dealer

    if request.method == 'POST':
        for item in order.items:
            item_id = item.id
            qty_key = f'quantity_{item_id}'
            dealer_key = f'dealer_{item_id}'
            delete_key = f'delete_{item_id}'

            article = item.article
            multiplicity = article.multiplicity or 1

            # Проверка на удаление
            if delete_key in request.form:
                db.session.delete(item)
                continue

            # Проверка кратности
            try:
                new_qty = int(request.form.get(qty_key, item.quantity))
                if new_qty % multiplicity != 0:
                    flash(f"Количество товара '{article.name}' должно быть кратным {multiplicity}.", "error")
                    return redirect(url_for('view_order', order_id=order_id))
            except ValueError:
                flash(f"Некорректное значение количества товара '{article.name}'.", "danger")
                return redirect(url_for('view_order', order_id=order_id))

            item.quantity = new_qty

            # Получаем нового поставщика по ID
            new_dealer_id = int(request.form.get(dealer_key, item.dealer_id))
            allowed_dealers = [article.dealer_id, article.second_dealer_id]

            if new_dealer_id in allowed_dealers:
                item.dealer_id = new_dealer_id  # Меняем поставщика в позиции заказа
            else:
                flash(f"Поставщик недоступен для товара '{article.name}'.", "danger")
                return redirect(url_for('view_order', order_id=order_id))

        db.session.commit()
        flash("Изменения в заказе сохранены!", "success")
        return redirect(url_for('orders'))

    return render_template('view_order.html', order=order)

@app.route('/orders')
@login_required
def orders():
    all_orders = Orders.query.order_by(Orders.created_at.desc()).all()
    print(f"DEBUG: Найдено заказов: {len(all_orders)}")  # Проверяем в консоли
    return render_template('orders.html', orders=all_orders)

@app.route('/home')
@login_required
def home():
    recent_orders = Orders.query.order_by(Orders.created_at.desc()).limit(5).all()
    # Добавляем сумму заказа и форматируем дату вручную
    for order in recent_orders:
        order.total_price = sum(item.quantity * item.article.price for item in order.items)
        order.formatted_date = format_date(order.created_at)
    return render_template("index.html", orders=recent_orders)

if __name__ == "__main__":
    app.run(debug=True)
