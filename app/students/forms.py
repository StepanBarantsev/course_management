from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class AddOrEditStudentForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired('Поле не должно быть пустым')])
    lms_id = IntegerField('Lms Id', validators=[DataRequired('Поле не должно быть пустым')])
    days = IntegerField('Начальное количество дней', validators=[DataRequired('Поле не должно быть пустым')])

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, current_course, *args, **kwargs):
        super(AddOrEditStudentForm, self).__init__(*args, **kwargs)
        self.current_course = current_course






