from web.app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from web.app import login_manager
import telegram.chat.states as states
from sqlalchemy import or_
from time import time
import jwt
from flask import current_app


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
    telegram_nickname = db.Column(db.String(100))
    lms_id = db.Column(db.Integer())
    flag_emails_from_default_mail = db.Column(db.Boolean(), nullable=False, default=False)
    flag_is_messages_from_bot_is_delivered = db.Column(db.Boolean(), nullable=False, default=True)

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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(140), nullable=False)
    deleted = db.Column(db.Boolean(), nullable=False, default=False)
    lms_id = db.Column(db.Integer(), nullable=False)
    trainer_telegram_id = db.Column(db.Integer(), nullable=False)
    trainer_lms_id = db.Column(db.Integer(), nullable=False)
    num_of_blocks = db.Column(db.Integer(), nullable=False, default=1)
    number_of_homeworks = db.Column(db.Integer(), nullable=False)
    is_certificate_needed = db.Column(db.Boolean(), nullable=False, default=False)
    default_num_days = db.Column(db.Integer(), nullable=False, default=30)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    review_link = db.Column(db.String(300), nullable=False)
    help = db.Column(db.Text(), nullable=False, default="К сожалению, к данному курсу отсутствуют какие-либо вспомогательные материалы.")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    blocks = db.relationship('CourseBlock', backref='course', lazy='dynamic')
    homeworks = db.relationship('Homework', backref='course', lazy='dynamic')
    students = db.relationship('Student', backref='course', lazy='dynamic')

    def __repr__(self):
        return '<Course {}>'.format(self.body)

    @staticmethod
    def delete_course_by_id(course_id):
        Course.query.filter_by(id=course_id).first().deleted = True

    @staticmethod
    def get_course_by_id(course_id):
        return Course.query.filter_by(id=course_id).first()

    def get_all_not_deleted_students(self):
        return self.students.filter_by(deleted=False)

    def get_all_not_deleted_blocks(self):
        return self.blocks.filter_by(deleted=False)

    def get_all_not_deleted_active_students(self):
        print(Student.student_statuses["active"])
        return self.get_all_not_deleted_students().filter_by(status=Student.student_statuses["active"])

    def get_all_not_deleted_freezed_students(self):
        return self.get_all_not_deleted_students().filter_by(status=Student.student_statuses["freezed"])

    def get_all_not_deleted_finished_students(self):
        return self.get_all_not_deleted_students().filter_by(status=Student.student_statuses["finished"])

    def get_all_not_deleted_dropped_students(self):
        return self.get_all_not_deleted_students().filter_by(status=Student.student_statuses["dropped"])

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
        return self.get_all_not_deleted_students().filter_by(email=email).first()

    def get_not_deleted_student_by_lms_id(self, lms_id):
        return self.get_all_not_deleted_students().filter_by(lms_id=lms_id).first()

    @staticmethod
    def find_students_by_search_param(students, search_param):
        return students.filter(or_(Student.name == search_param, Student.email == search_param, Student.lms_email == search_param, Student.telegram_id == search_param))

    def delete_block_by_num(self, num):
        self.get_all_not_deleted_blocks().filter_by(number=num).first().deleted = True

    def get_block_by_num(self, num):
        return self.get_all_not_deleted_blocks().filter_by(number=num).first()

    def get_all_not_deleted_homeworks(self):
        return self.homeworks.filter_by(deleted=False)

    def delete_homework_by_num(self, num):
        self.get_all_not_deleted_homeworks().filter_by(number=num).first().deleted = True

    def get_homework_by_num(self, num):
        return self.get_all_not_deleted_homeworks().filter_by(number=num).first()

    def get_homework_by_short_name(self, short_name):
        return self.get_all_not_deleted_homeworks().filter_by(short_name=short_name).first()


class CourseBlock(db.Model):
    __tablename__ = 'course_blocks'
    id = db.Column(db.Integer(), primary_key=True)

    number = db.Column(db.Integer(), nullable=False)
    # lms_id таски, которую нужно выполнить чтобы открылся блок. Если null, то блок открыт и так
    required_task_lms_id = db.Column(db.Integer())
    # Материалы по блоку. Могут отсутствовать если их не настроить
    link = db.Column(db.String(100))
    deleted = db.Column(db.Boolean(), nullable=False, default=False)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    check = db.relationship('Check', backref='block', uselist=False)


class Homework(db.Model):
    __tablename__ = 'homeworks'
    id = db.Column(db.Integer(), primary_key=True)

    lms_id = db.Column(db.Integer())
    short_name = db.Column(db.String(100))
    answer_link = db.Column(db.String(100))
    deleted = db.Column(db.Boolean(), nullable=False, default=False)

    # Невидимое поле нужное для корректного удаления и добавления из при изменении их количества
    number = db.Column(db.Integer(), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)


class Student(db.Model):

    student_statuses = {"active": "active", "finished": "finished", "dropped": "dropped", "freezed": "freezed"}

    __tablename__ = 'students'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    lms_email = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False, default=student_statuses["active"])
    number_of_days = db.Column(db.Integer(), nullable=False)
    lms_id = db.Column(db.Integer(), nullable=False)
    registration_code = db.Column(db.String(100), nullable=False)
    telegram_id = db.Column(db.Integer())
    deleted = db.Column(db.Boolean(), nullable=False, default=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    cert_link = db.Column(db.String(100))

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    checks = db.relationship('Check', backref='student', lazy='dynamic')

    @staticmethod
    def delete_student_by_id(student_id):
        Student.get_student_by_id(student_id).deleted = True

    @staticmethod
    def get_student_by_id(student_id):
        return Student.query.filter_by(id=student_id).first()

    @staticmethod
    def freeze_or_unfreeze_student_by_id(student_id):
        student = Student.get_student_by_id(student_id)
        if student.status == Student.student_statuses["freezed"]:
            student.status = Student.student_statuses["active"]
        else:
            student.status = Student.student_statuses["freezed"]

    @staticmethod
    def finish_or_unfinish_student_by_id(student_id):
        student = Student.get_student_by_id(student_id)
        if student.status == Student.student_statuses["finished"]:
            student.status = Student.student_statuses["active"]
        else:
            student.status = Student.student_statuses["finished"]

    @staticmethod
    def drop_or_undrop_student_by_id(student_id):
        student = Student.get_student_by_id(student_id)
        if student.status == Student.student_statuses["dropped"]:
            student.status = Student.student_statuses["active"]
        else:
            student.status = Student.student_statuses["dropped"]

    @staticmethod
    def add_days_to_student(student_id):
        student = Student.get_student_by_id(student_id)
        course = Course.get_course_by_id(student.course_id)
        student.number_of_days += course.default_num_days
        return student.number_of_days

    def get_all_not_deleted_checks(self):
        return self.checks.filter_by(deleted=False)

    def return_color_of_td(self):
        if self.status == Student.student_statuses["dropped"]:
            return "gray"
        elif self.status == Student.student_statuses["finished"]:
            return "9966cc"
        elif self.status == Student.student_statuses["freezed"]:
            return "aqua"
        else:
            if self.number_of_days < 0:
                return "ffc0cb"
            else:
                return "98ff98"


class TelegramState(db.Model):
    __tablename__ = 'telegram_states'
    id = db.Column(db.Integer(), primary_key=True)
    telegram_id = db.Column(db.Integer(), nullable=False, unique=True)
    state = db.Column(db.String(100), nullable=False, default=states.START)
    temp_lms_email = db.Column(db.String(100))

    temp_course_register_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    current_course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    # id студентов которые соотносятся с конкретным телеграм id
    # Для каждого курса студент создается заново, хотя это может быть один и тот же человек
    # Создание отдельных студентов для кжадого курса очень сильно упрощает систему, но вот в данном месте это немного костыль
    # После верификации, экземпляр студента получает в свое поле телеграм id
    temp_course_student_id = db.Column(db.Integer, db.ForeignKey('students.id'))


class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.Integer(), primary_key=True)
    link = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Оплата может быть за блок или другую услугу
    another = db.Column(db.String(50), nullable=True)
    block_id = db.Column(db.Integer, db.ForeignKey('course_blocks.id'), nullable=True)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    deleted = db.Column(db.Boolean(), nullable=False, default=False)
    
    @staticmethod
    def delete_check_by_id(check_id):
        Check.query.filter_by(id=check_id).first().deleted = True




