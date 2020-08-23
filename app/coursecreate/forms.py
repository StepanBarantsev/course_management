from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, Optional
from app.models import Course, User
from app import db


class BlockForm(FlaskForm):
    blocks_number = FieldList(IntegerField('Номер блока', validators=[DataRequired('Введите число')]), min_entries=0)
    blocks_required_task_lms_id = FieldList(
        IntegerField('Lms Id, необходимое чтобы блок был открыт (можно оставить пустым)',
                     validators=[Optional('Введите число')]), min_entries=0)


class CreateOrEditCourseForm(FlaskForm):

    name = StringField('Название курса', validators=[DataRequired('Поле не должно быть пустым')])
    lms_id = IntegerField('LMS ID курса', validators=[DataRequired('Введите число')])
    trainer_lms_id = IntegerField('LMS ID Тренера', validators=[DataRequired('Введите число')])
    trainer_telegram_id = IntegerField('Telegram ID тренера', validators=[DataRequired('Введите число')])

    blocks = FieldList(FormField(BlockForm), min_entries=0)

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, current_user, old_course_name=None, old_lms_id=None,  *args, **kwargs):
        super(CreateOrEditCourseForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.old_course_name = old_course_name
        self.old_lms_id = old_lms_id

    def validate_name(self, name):
        coursename = self.current_user.get_course_by_name(name.data)
        if coursename is not None and (coursename.name != self.old_course_name or self.old_course_name is None):
            raise ValidationError('Данное имя курса уже занято!')

    def validate_lms_id(self, lms_id):
        lmsid = self.current_user.get_course_by_lms_id(lms_id.data)
        if lmsid is not None and lmsid.lms_id != (self.old_lms_id or self.old_lms_id is None):
            raise ValidationError('Данное LMS ID уже занято!')



