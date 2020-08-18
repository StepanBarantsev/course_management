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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Course {}>'.format(self.body)

    @staticmethod
    def delete_course_by_id(course_id):
        Course.query.filter_by(id=course_id).first().deleted = True

