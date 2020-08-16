from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from app.models import Course, User
from app import db


class CreateCourseProfileForm(FlaskForm):

    name = StringField('Название курса', validators=[DataRequired()])
    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, current_user, *args, **kwargs):
        super(CreateCourseProfileForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_name(self, name):
        coursename = db.session.query(Course).filter(Course.name == name.data).filter(Course.user_id == self.current_user.id).first()
        if coursename is not None:
            raise ValidationError('Данное имя курса уже занято!')


class EditCourseProfileForm(FlaskForm):

    name = StringField('Название курса', validators=[DataRequired()])
    submit = SubmitField('Сохранить', render_kw={'class': "btn btn-success"})

    def __init__(self, current_user, old_course_name, *args, **kwargs):
        super(EditCourseProfileForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.old_course_name = old_course_name

    def validate_name(self, name):
        coursename = db.session.query(Course.name).filter(Course.name == name.data).filter(Course.user_id == self.current_user.id).first()
        if coursename is not None and coursename.name != self.old_course_name:
            raise ValidationError('Данное имя курса уже занято!')


