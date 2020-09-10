from web.app.models import TelegramState, Course
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
        markup.add(types.InlineKeyboardButton(text=i.name, callback_data=i.id))

    return markup


