from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, BooleanField, FieldList, FormField, IntegerField
from wtforms.fields.choices import SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from config import Restaurants, Articles
from flask import current_app

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])  # Добавлено поле email
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class RoleForm(FlaskForm):
    name = StringField('Название роли', validators=[DataRequired(), Length(min=2, max=50)])
    description = StringField('Описание', validators=[Length(max=255)])
    submit = SubmitField('Сохранить')

class AssignRoleForm(FlaskForm):
    roles = SelectField('Выберите роль', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class RestaurantSelectionForm(FlaskForm):
    restaurant_id = StringField()  # Храним ID ресторана
    selected = BooleanField()  # Флажок для выбора

class AddGoodForm(FlaskForm):
    article = StringField("Артикул", validators=[DataRequired(), Length(max=256)])
    name = StringField("Название", validators=[DataRequired(), Length(max=256)])
    dealer = SelectField("Поставщик", coerce=int, validators=[DataRequired()])
    type = StringField("Тип", validators=[Length(max=256)])
    price = FloatField("Цена", validators=[DataRequired()])
    multiplicity = IntegerField("Кратность", validators=[DataRequired()])
    unit = StringField("Единица измерения", validators=[DataRequired()])
    second_dealer = StringField("Доп. поставщик", validators=[Optional()])
    second_price = FloatField("Доп. цена", validators=[Optional()])
    submit = SubmitField("Добавить товар")


class AddDealerForm(FlaskForm):
    name = StringField("Наименование поставщика", validators=[DataRequired(), Length(max=256)])
    adres = StringField("Адрес поставщика", validators=[DataRequired(), Length(max=256)])
    e_mail = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional(),
                                             Regexp(r"^\+7\s?\(\d{3}\)\s?\d{3}-\d{2}-\d{2}$")])
    submit = SubmitField("Add Dealer")

class RestaurantsNew(FlaskForm):
    name = StringField("Ресторан", validators=[DataRequired(), Length(max=256)])
    ur_name = StringField("Юр. лицо", validators=[DataRequired(), Length(max=256)])
    address = StringField("Адрес", validators=[DataRequired(), Length(max=256)])

class OrderGoodsForm(FlaskForm):
    article_id = IntegerField("ID товара", validators=[DataRequired()])
    quantity = IntegerField("Количество", validators=[DataRequired(), NumberRange(min=1)])

class OrderForm(FlaskForm):
    goods = FieldList(FormField(OrderGoodsForm), min_entries=1)  # Позволяет выбрать несколько товаров
    submit = SubmitField("Сформировать заказ")
