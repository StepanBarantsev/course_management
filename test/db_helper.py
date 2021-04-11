from web.app.models import User, Course, Student
from werkzeug.security import generate_password_hash


def create_minimal_user(session):
    user = User(username='Stepan', email='stepan.barantsev@gmail.com', password_hash=generate_password_hash('1'))
    session.add(user)
    session.commit()
    return user


def create_full_info_user(session):
    user = User(username='Stepan', email='stepan.barantsev@gmail.com', password_hash=generate_password_hash('1'),
                name='testName', telegram_id=1, telegram_nickname='Bars', lms_id=1)
    session.add(user)
    session.commit()
    return user


def create_course(session, user_id, course_name, course_lms_id):
    course = Course(name=course_name, lms_id=course_lms_id, trainer_telegram_id=1, trainer_lms_id=1,
                    number_of_homeworks=2, review_link='link', user_id=user_id)
    session.add(course)
    session.commit()
    return course


def create_student(session, course_id, student_name, student_lms_id):
    student = Student(name=student_name, course_id=course_id, lms_id=student_lms_id, registration_code=1,
                      email='stepan.barantsev@gmail.com', lms_email='stepan.barantsev@gmail.com', number_of_days=0)
    session.add(student)
    session.commit()
    return student

