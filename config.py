from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/flask'
db = SQLAlchemy(app)

# Вспомогательная таблица для связи User2 и Role2
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer, db.ForeignKey('user2.id'), primary_key=True),
                      db.Column('role_id', db.Integer, db.ForeignKey('role2.id'), primary_key=True)
                      )


class Role2(db.Model):
    __tablename__ = 'role2'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    description = db.Column(db.String(256))
    users = db.relationship('User2', secondary=user_roles, back_populates='roles')


class User2(UserMixin, db.Model):
    __tablename__ = 'user2'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role2.id'), nullable=True)
    role_name = db.Column(db.String(256), nullable=True)
    roles = db.relationship('Role2', secondary=user_roles, back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def set_role(self, role):
        """
        Устанавливает только одну роль для пользователя и обновляет primary_role_name.
        """
        self.roles = [role]  # Ограничение на одну роль
        self.role_name = role.name


dealer_articles = db.Table('dealer_articles',
                           db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
                           db.Column('dealer_id', db.Integer, db.ForeignKey('dealers.id'), primary_key=True)
                           )
article_restaurants = db.Table('article_restaurants',
                               db.Column('article_id', db.Integer, db.ForeignKey('articles.id'), primary_key=True),
                               db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
                               )

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    article = db.Column(db.String, nullable=True)
    dealer = db.Column(db.String, db.ForeignKey('dealers.name'), nullable=True)
    price = db.Column(db.Float, nullable=True)
    type = db.Column(db.String, nullable=True)
    restaurant = db.Column(db.String, nullable=True)
    multiplicity = db.Column(db.Integer, nullable=True)
    unit = db.Column(db.String, nullable=True)
    second_dealer = db.Column(db.String)
    second_price = db.Column(db.String)
    dealers = db.relationship('Dealers', secondary=dealer_articles, back_populates='articles')
    restaurants = db.relationship('Restaurants', secondary=article_restaurants, back_populates='articles')

    def set_role(self, dealer):
        self.dealers = [dealer]  # Ограничение на одну роль
        self.dealer = dealer.name


class Restaurants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True, nullable=False)
    ur_name = db.Column(db.String(256), unique=True, nullable=False)
    address = db.Column(db.String(256), unique=True, nullable=False)
    articles = db.relationship('Articles', secondary=article_restaurants, back_populates='restaurants')

class Dealers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=True)
    adres = db.Column(db.String, unique=True, nullable=True)
    e_mail = db.Column(db.String, unique=True, nullable=True)
    phone = db.Column(db.String, unique=True, nullable=True)
    articles = db.relationship('Articles', secondary=dealer_articles, back_populates='dealers')


with app.app_context():
    db.create_all()
