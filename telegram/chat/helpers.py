from web.app.models import TelegramState, Course, Student
from telebot import types


def get_buttons_by_telegram_id(telegram_id):
    return ['Заглушка']


def get_telegram_session_or_create_new(telegram_id, session):
    element = session.query(TelegramState).filter_by(telegram_id=telegram_id).first()

    if element is not None:
        return element

    new_element = TelegramState(telegram_id=telegram_id)
    session.add(new_element)
    session.commit()

    return session.query(TelegramState).filter_by(telegram_id=telegram_id).first()


def set_new_state(element, state, session):
    element.state = state
    session.commit()


def print_available_courses_as_buttons(session):
    courses_list = session.query(Course).all()

    markup = types.InlineKeyboardMarkup()

    for i in courses_list:
        markup.add(types.InlineKeyboardButton(text=f'{i.name} [{i.author.name}]', callback_data=f'course_id: {i.id}, course_name_with_author: {i.name} [{i.author.name}]'))

    return markup


def parse_callback_data(string):
    new_strings = string.split(',')

    d = {}

    for s in new_strings:
        d[s.split(':')[0].strip()] = s.split(':')[1].strip()

    return d


def get_student_by_email_and_course_id(course_id, email, session):
    return session.query(Student).filter_by(course_id=int(course_id)).filter_by(email=email).first()


