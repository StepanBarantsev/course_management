from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, FieldList, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Optional, NumberRange
from web.app.models import Course


class CreateOrEditCourseForm(FlaskForm):

    name = StringField('Название курса', validators=[DataRequired('Поле не должно быть пустым')])
    lms_id = IntegerField('LMS ID курса', validators=[DataRequired('Введите число')])
    trainer_lms_id = IntegerField('LMS ID Тренера', validators=[DataRequired('Введите число')])
    trainer_telegram_id = IntegerField('Telegram ID тренера', validators=[DataRequired('Введите число')])
    review_link = StringField('Где оставить отзыв?', validators=[DataRequired('Поле не должно быть пустым')])
    help_field = TextAreaField('Вспомогательная информация о курсе', validators=[DataRequired('Поле не должно быть пустым')])

    default_number_of_days = IntegerField('Количество дней поддержки за блок',
                                          validators=[DataRequired('Поле не должно быть пустым'), Optional('Введите число'),
                                                      NumberRange(1, 1000, "Число должно быть не больше 1000 и не меньше 1")])

    number_homeworks = IntegerField('Количество домашних заданий',
                                    validators=[DataRequired('Поле не должно быть пустым'), Optional('Введите число'),
                                                NumberRange(1, 1000, "Число должно быть не больше 1000 и не меньше 1")])

    is_more_then_one_block = BooleanField('Курс разделяется на блоки?')
    number_of_blocks = IntegerField('Количество блоков', validators=[Optional('Введите число'),
                                                                     NumberRange(2, 20, "Число должно быть не больше 20 и не меньше 2")])

    is_certificate_needed = BooleanField('Отслеживать ли выдачу сертификата?')

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, current_user, old_course_name=None, old_lms_id=None,  *args, **kwargs):
        super(CreateOrEditCourseForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.old_course_name = old_course_name
        self.old_lms_id = old_lms_id

    def validate_name(self, name):
        course = self.current_user.get_course_by_name(name.data)
        if course is not None and (course.name != self.old_course_name or self.old_course_name is None):
            raise ValidationError('Данное имя курса уже занято!')

    def validate_lms_id(self, lms_id):
        # Валидация по всем юзерам, а не по current
        course = Course.get_course_by_lms_id(lms_id.data)
        if course is not None and (course.lms_id != self.old_lms_id or self.old_lms_id is None):
            raise ValidationError('Данное LMS ID уже занято!')


class BlockForm(FlaskForm):
    link = StringField('Ссылка на материал')
    required_task = IntegerField('Lms id задания (для открытия блока)', validators=[Optional('Введите число')])


class HomeworkForm(FlaskForm):
    lms_id = IntegerField('Lms id задания', validators=[Optional('Введите число')])
    shortname = StringField('Краткое название')
    answer_link = StringField('Ссылка на решение')


class CreateOrEditCourseFormAdditional(FlaskForm):

    blocks = FieldList(FormField(BlockForm), min_entries=1)
    homeworks = FieldList(FormField(HomeworkForm), min_entries=1)

    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})



