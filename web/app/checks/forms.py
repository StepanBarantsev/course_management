from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError


class AddOrEditCheckForm(FlaskForm):

    block_number = SelectField('Номер блока', validators=[DataRequired('Поле не должно быть пустым')])
    link = StringField('Ссылка на чек', validators=[DataRequired('Поле не должно быть пустым')])
    amount = IntegerField('Сумма чека', validators=[DataRequired('Поле не должно быть пустым')])

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, block_numbers, *args, **kwargs):
        super(AddOrEditCheckForm, self).__init__(*args, **kwargs)
        self.block_numbers = block_numbers
        self.block_number.choices = [[block_number, block_number] for block_number in block_numbers]

    def validate_block_number(self, block_number):
        if block_number.data not in self.block_numbers:
            raise ValidationError('Чек для данного блока уже выбит!')
