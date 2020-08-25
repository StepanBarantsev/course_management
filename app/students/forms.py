from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList, FormField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Optional, NumberRange
from app.models import Course, User
from app import db


class AddOrEditStudentForm(FlaskForm):

    name = StringField('ФИО', validators=[DataRequired('Поле не должно быть пустым')])
    email = StringField('Email', validators=[DataRequired('Поле не должно быть пустым')])
    lms_id = IntegerField('Lms Id', validators=[DataRequired('Поле не должно быть пустым')])
    days = IntegerField('Начальное количество дней', validators=[DataRequired('Поле не должно быть пустым')])

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, *args, **kwargs):
        super(AddOrEditStudentForm, self).__init__(*args, **kwargs)




