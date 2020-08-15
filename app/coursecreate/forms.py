from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from app.models import Course, User
from app import db


class CreateCourseProfileForm(FlaskForm):

    name = StringField('Название курса', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, current_user, *args, **kwargs):
        super(CreateCourseProfileForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_name(self, name):
        coursename = db.session.query(Course).filter(Course.name == name.data).filter(Course.user_id == self.current_user.id).first()
        print(db.session.query(Course).filter(Course.name == name.data).filter(Course.user_id == self.current_user.id))
        if coursename is not None:
            raise ValidationError('Данное имя курса уже занято!')

