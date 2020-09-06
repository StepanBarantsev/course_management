import telebot
import telegram.config
import telegram.chat.messages as messages
import telegram.chat.states as states
from web.app.models import TelegramState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.chat.helpers import get_telegram_session_or_create_new

engine = create_engine(telegram.config.ConfigTelegram.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

bot = telebot.TeleBot(telegram.config.ConfigTelegram.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def hello(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    chat_id = message.chat.id
    bot.send_message(chat_id, messages.HELP_TEXT)


@bot.message_handler(commands=['register'])
def register(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    chat_id = message.chat.id
    bot.send_message(chat_id, 'Выберите курс на который хотите зарегистрироваться')

    session.query(TelegramState).filter_by(telegram_id=message.chat.id).first().state = states.WAITING_FOR_COURSE_NAME_REGISTER
    session.commit()


@bot.message_handler(func=lambda message: TelegramState.get_state_by_telegram_id(message.chat.id) == states.WAITING_FOR_COURSE_NAME_REGISTER)
def user_entering_course_name(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    bot.send_message(message.chat.id, "Курс был успешно введен")


if __name__ == '__main__':
    bot.polling(none_stop=True)
