from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import LoginManager, UserMixin
from app import login_manager


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

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    blocks = db.relationship('CourseBlock', backref='course', lazy='dynamic')
    tasks = db.relationship('LmsTask', backref='course', lazy='dynamic')

    def __repr__(self):
        return '<Course {}>'.format(self.body)

    @staticmethod
    def delete_course_by_id(course_id):
        Course.query.filter_by(id=course_id).first().deleted = True


class CourseBlock(db.Model):
    __tablename__ = 'courseBlocks'
    id = db.Column(db.Integer(), primary_key=True)
    number = db.Column(db.Integer(), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    # id таски, которую нужно выполнить чтобы открылся блок. Если null, то блок открыт и так
    required_task_id = db.Column(db.Integer, db.ForeignKey('lmsTasks.id'))


class LmsTask(db.Model):
    __tablename__ = 'lmsTasks'
    id = db.Column(db.Integer(), primary_key=True)

    lms_id = db.Column(db.Integer(), nullable=False)
    name = db.Column(db.Integer(), nullable=False)
    # Короткое имя по которому будет идти запрос в телегу
    short_name = db.Column(db.Integer(), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    related_blocks = db.relationship('CourseBlock', backref='task', lazy='dynamic')





