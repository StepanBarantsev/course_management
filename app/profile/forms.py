from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email
from app.models import User


class EditProfileForm(FlaskForm):

    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Имя')
    submit = SubmitField('Сохранить')

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

