from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from web.app.models import User


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired('Поле не должно быть пустым')])
    password = PasswordField('Пароль', validators=[DataRequired('Поле не должно быть пустым')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти', render_kw={'class': "btn btn-success"})


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired('Поле не должно быть пустым')])
    email = StringField('Email', validators=[DataRequired('Поле не должно быть пустым'), Email('Некорректный для e-mail формат')])
    password = PasswordField('Пароль', validators=[DataRequired('Поле не должно быть пустым')])
    password2 = PasswordField('Введите пароль еще раз', validators=[DataRequired('Поле не должно быть пустым'), EqualTo('password', message='Пароли не совпадают!')])
    registration_code = PasswordField('Код для регистрации', validators=[DataRequired('Поле не должно быть пустым')])
    submit = SubmitField('Зарегистрироваться', render_kw={'class': "btn btn-success"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Данный логин уже занят')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Данный email уже занят')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Выслать запрос на смену пароля')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Введите пароль еще раз', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')
