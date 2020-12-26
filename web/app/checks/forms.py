from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class AddOrEditCheckForm(FlaskForm):

    block_number = SelectField('Номер блока', validators=[DataRequired('Поле не должно быть пустым')])
    link = StringField('Сслыка на чек', validators=[DataRequired('Поле не должно быть пустым')])

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, block_numbers, *args, **kwargs):
        super(AddOrEditCheckForm, self).__init__(*args, **kwargs)
        self.block_number.choices = [[block_number, block_number] for block_number in block_numbers]
