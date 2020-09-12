from web.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from web.app import login_manager
import telegram.chat.states as states


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    telegram_id = db.Column(db.Integer())
    lms_id = db.Column(db.Integer())

    courses = db.relationship('Course', backref='author', lazy='dynamic')

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_all_not_deleted_courses(self):
        return self.courses.filter_by(deleted=False)

    def get_course_by_name(self, name):
        return self.get_all_not_deleted_courses().filter_by(name=name).first()

    def get_course_by_lms_id(self, lms_id):
        return self.get_all_not_deleted_courses().filter_by(lms_id=lms_id).first()


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(140), nullable=False)
    deleted = db.Column(db.Boolean(), nullable=False, default=False)
    lms_id = db.Column(db.Integer(), nullable=False)
    trainer_telegram_id = db.Column(db.Integer(), nullable=False)
    trainer_lms_id = db.Column(db.Integer(), nullable=False)
    num_of_blocks = db.Column(db.Integer(), nullable=False, default=1)
    is_certificate_needed = db.Column(db.Boolean(), nullable=False, default=False)
    default_num_days = db.Column(db.Integer(), nullable=False, default=30)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    blocks = db.relationship('CourseBlock', backref='course', lazy='dynamic')
    students = db.relationship('Student', backref='course', lazy='dynamic')

    def __repr__(self):
        return '<Course {}>'.format(self.body)

    @staticmethod
    def delete_course_by_id(course_id):
        Course.query.filter_by(id=course_id).first().deleted = True

    def get_all_not_delete_students(self):
        return self.students.filter_by(deleted=False)

    @staticmethod
    def get_all_not_deleted_courses():
        return Course.query.filter_by(deleted=False)

    @staticmethod
    def get_course_by_lms_id(lms_id):
        return Course.get_all_not_deleted_courses().filter_by(lms_id=lms_id).first()

    @staticmethod
    def get_course_by_name(name):
        return Course.get_all_not_deleted_courses().filter_by(name=name).first()

    def get_not_deleted_student_by_email(self, email):
        return self.get_all_not_delete_students().filter_by(email=email).first()

    def get_not_deleted_student_by_lms_id(self, lms_id):
        return self.get_all_not_delete_students().filter_by(lms_id=lms_id).first()


class CourseBlock(db.Model):
    __tablename__ = 'course_blocks'
    id = db.Column(db.Integer(), primary_key=True)

    number = db.Column(db.Integer(), nullable=False)
    # lms_id таски, которую нужно выполнить чтобы открылся блок. Если null, то блок открыт и так
    required_task_lms_id = db.Column(db.Integer())

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    lms_email = db.Column(db.String(100), nullable=False)
    freezed = db.Column(db.Boolean(), nullable=False, default=False)
    number_of_days = db.Column(db.Integer(), nullable=False)
    lms_id = db.Column(db.Integer(), nullable=False)
    registration_code = db.Column(db.String(100), nullable=False)
    telegram_id = db.Column(db.Integer())
    deleted = db.Column(db.Boolean(), nullable=False, default=False)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    @staticmethod
    def delete_student_by_id(student_id):
        Student.query.filter_by(id=student_id).first().deleted = True

    @staticmethod
    def freeze_or_unfreeze_student_by_id(student_id):
        Student.query.filter_by(id=student_id).first().freezed = not Student.query.filter_by(id=student_id).first().freezed

    def return_color_of_td(self):
        if self.freezed:
            return "aqua"
        elif self.number_of_days < 0:
            return "ffc0cb"
        else:
            return "98ff98"


class TelegramState(db.Model):
    __tablename__ = 'telegram_states'
    id = db.Column(db.Integer(), primary_key=True)
    telegram_id = db.Column(db.Integer(), nullable=False, unique=True)
    state = db.Column(db.String(100), nullable=False, default=states.START)
    temp_lms_email = db.Column(db.String(100))
    temp_authcode = db.Column(db.String(100))
    temp_course_register_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    current_course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

