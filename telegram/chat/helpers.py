from web.app.models import TelegramState


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

