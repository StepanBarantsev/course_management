import telebot
import telegram.config
import telegram.chat.messages as messages
import telegram.chat.states as states
from web.app.models import TelegramState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.chat.helpers import get_telegram_session_or_create_new, print_available_courses_as_buttons
from telebot import types

engine = create_engine(telegram.config.ConfigTelegram.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

bot = telebot.TeleBot(telegram.config.ConfigTelegram.TOKEN)


@bot.message_handler(commands=['start'], func=lambda message: get_telegram_session_or_create_new(message.chat.id, session).state == states.START)
def hello(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, messages.HELP_TEXT)


@bot.message_handler(commands=['help'])
def hello(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, messages.HELP_TEXT)


@bot.message_handler(commands=['register'])
def register(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    bot.send_message(chat_id=message.chat.id,
                     text="Список доступных курсов для регистрации:",
                     reply_markup=print_available_courses_as_buttons(session),
                     parse_mode='HTML')

    telegram_session.state = states.WAITING_FOR_COURSE_NAME_REGISTER
    session.commit()


if __name__ == '__main__':
    bot.polling(none_stop=True)
