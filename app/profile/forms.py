from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from werkzeug.security import check_password_hash


class EditProfileForm(FlaskForm):

    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Имя')
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

    old_password = PasswordField('Введите старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Введите новый пароль', validators=[DataRequired()])
    repeated_password = PasswordField('Введите новый пароль еще раз', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Изменить')

    def __init__(self, current_user, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_old_password(self, old_password):
        if not self.current_user.check_password(old_password.data):
            raise ValidationError('Неверно введен старый пароль!')
