from web.app.models import TelegramState, Course, Student
from telebot import types


def set_new_state(element, state, session):
    element.state = state
    session.commit()


def print_available_courses_as_buttons(session):
    courses_list = session.query(Course).filter_by(deleted=0).all()

    markup = types.InlineKeyboardMarkup()

    for i in courses_list:
        markup.add(types.InlineKeyboardButton(text=f'{i.name} [{i.author.name}]', callback_data=f'course_id: {i.id}'))

    return markup


def parse_callback_data(string):
    new_strings = string.split(',')

    d = {}

    for s in new_strings:
        d[s.split(':')[0].strip()] = s.split(':')[1].strip()

    return d


def get_student_by_email_and_course_id(course_id, email, session):
    return session.query(Student).filter_by(course_id=int(course_id)).filter_by(lms_email=email).filter_by(deleted=0).first()


def get_student_by_telegram_id_and_course_id(course_id, telegram_id, session):

    if course_id is None or telegram_id is None:
        return None

    return session.query(Student).filter_by(course_id=int(course_id)).filter_by(telegram_id=telegram_id).filter_by(deleted=0).first()


def get_student_by_id(student_id, session):
    return session.query(Student).filter_by(id=int(student_id)).filter_by(deleted=0).first()


def create_string_with_course_and_author_by_course_id(course_id, session):

    if course_id is None:
        return None

    course = session.query(Course).filter_by(deleted=0).filter_by(id=int(course_id)).first()
    if course is None:
        return None
    else:
        return f'{course.name} [{course.author.name}]'


def get_all_active_students_by_telegram_id(telegram_id, session):
    return session.query(Student).filter_by(deleted=0).filter_by(telegram_id=telegram_id).all()


def get_all_active_courses_by_telegram_id(telegram_id, session):
    return [i.course for i in get_all_active_students_by_telegram_id(telegram_id, session)]


def print_available_courses_as_buttons_by_telegram_id(telegram_id, session):
    courses_list = get_all_active_courses_by_telegram_id(telegram_id, session)

    markup = types.InlineKeyboardMarkup()

    for i in courses_list:
        markup.add(types.InlineKeyboardButton(text=f'{i.name} [{i.author.name}]', callback_data=f'course_id: {i.id}'))

    return markup


def get_current_course_by_id(course_id, session):
    return session.query(Course).filter_by(id=course_id).first()


# Отправляет сообщение студенту, если тот зарегистрирован у телеграм бота
def try_to_send_message_to_student(student, message, bot):
    if student.telegram_id is not None:
        bot.send_message(student.telegram_id, message)

