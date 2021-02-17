import telegram.config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from web.app.models import TelegramState
from logger import logger

engine = create_engine(telegram.config.ConfigTelegram.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    logger.debug("Создается новая сессия бд")
    session = Session()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_telegram_session_or_create_new(telegram_id):
    with session_scope() as session:
        logger.debug(f"Пытаемся получить существующую или создать новую сессию тг для юзера {telegram_id}")
        return get_telegram_session_or_create_new_with_existing_db_session(telegram_id, session)


def get_telegram_session_or_create_new_with_existing_db_session(telegram_id, session):
    element = session.query(TelegramState).filter_by(telegram_id=telegram_id).first()

    if element is not None:
        return element

    new_element = TelegramState(telegram_id=telegram_id)
    session.add(new_element)
    session.commit()

    return session.query(TelegramState).filter_by(telegram_id=telegram_id).first()
