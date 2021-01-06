from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Optional
from web.app.models import User


class EditProfileForm(FlaskForm):

    username = StringField('Логин', validators=[DataRequired('Поле не должно быть пустым')])
    email = StringField('Email', validators=[DataRequired('Поле не должно быть пустым'), Email('Некорректный для e-mail формат')])
    name = StringField('Имя (показывается в письме в качестве отправителя)')
    lms_id = IntegerField('LMS Id', validators=[Optional('Введите число')])
    telegram_id = IntegerField('Telegram Id', validators=[Optional('Введите число')])
    telegram_nickname = StringField('Ник в Telegram', validators=[DataRequired('Поле не должно быть пустым')])
    flag_emails_from_default_mail = BooleanField('Включить отпраку писем с почты?')
    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, current_user, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_username(self, username):
        if username.data != self.current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Данный логин уже занят')

    def validate_email(self, email):
        if email.data != self.current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Данный email уже занят')


class ResetPasswordForm(FlaskForm):

    old_password = PasswordField('Введите старый пароль', validators=[DataRequired('Поле не должно быть пустым')])
    new_password = PasswordField('Введите новый пароль', validators=[DataRequired('Поле не должно быть пустым')])
    repeated_password = PasswordField('Введите новый пароль еще раз', validators=[DataRequired('Поле не должно быть пустым'), EqualTo('new_password', message='Пароли не совпадают!')])
    submit = SubmitField('Изменить')

    def __init__(self, current_user, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_old_password(self, old_password):
        if not self.current_user.check_password(old_password.data):
            raise ValidationError('Неверно введен старый пароль!')
