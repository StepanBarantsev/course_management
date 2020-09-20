from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, InputRequired


class AddOrEditStudentForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired('Поле не должно быть пустым'),
                                             Email('Формат Email некорректный')])
    lms_id = IntegerField('Lms Id', validators=[DataRequired('Поле не должно быть пустым')])
    days = IntegerField('Количество дней', validators=[InputRequired('Поле не должно быть пустым')])

    # Тут заблокированные формы
    lms_email_locked = StringField('Lms Email')
    telegram_id_locked = StringField('Telegram Id')
    name_locked = StringField('Имя')
    registration_code_locked = StringField('Код регистрации')

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, current_course, old_email=None, old_lms_id=None, *args, **kwargs):
        super(AddOrEditStudentForm, self).__init__(*args, **kwargs)
        self.current_course = current_course
        self.old_email = old_email
        self.old_lms_id = old_lms_id

    # Поля уникальны только в рамках курса

    def validate_email(self, email):
        student = self.current_course.get_not_deleted_student_by_email(email.data)
        if student is not None and student.email != self.old_email:
            raise ValidationError('Данный email уже занят!')

    def validate_lms_id(self, lms_id):
        # Валидация по всем юзерам, а не по current
        student = self.current_course.get_not_deleted_student_by_lms_id(lms_id.data)
        if student is not None and student.lms_id != self.old_lms_id:
            raise ValidationError('Данное LMS ID уже занято!')






