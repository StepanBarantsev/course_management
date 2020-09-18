import telebot
import telegram.config
from telegram.chat.messages import get_message
import telegram.chat.states as states
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.chat.helpers import get_telegram_session_or_create_new, print_available_courses_as_buttons, \
    parse_callback_data, get_student_by_email_and_course_id, get_student_by_id, \
    create_string_with_course_and_author_by_course_id, get_all_active_courses_by_telegram_id,\
    print_available_courses_as_buttons_by_telegram_id, get_current_course_by_id, get_student_by_telegram_id_and_course_id

engine = create_engine(telegram.config.ConfigTelegram.SQLALCHEMY_DATABASE_URI, convert_unicode=True, connect_args=dict(use_unicode=True))
Session = sessionmaker(bind=engine)
session = Session()

bot = telebot.TeleBot(telegram.config.ConfigTelegram.TOKEN)


################
#  DECORATORS  #
################

def no_current_course_decorator(f):
    def func(message):
        telegram_session = get_telegram_session_or_create_new(message.chat.id, session)
        chat_id = message.chat.id
        if telegram_session.current_course_id is not None:
            f(message)
        else:
            bot.send_message(chat_id, get_message('NO_CURRENT_COURSE'))

    return func


##############
#  HANDLERS  #
##############

@bot.message_handler(commands=['start'], func=lambda message: get_telegram_session_or_create_new(message.chat.id, session).state == states.START)
def hello(message):
    get_telegram_session_or_create_new(message.chat.id, session)

    chat_id = message.chat.id
    bot.send_message(chat_id, get_message('HELP_TEXT'))


@bot.message_handler(commands=['help'])
def help(message):
    get_telegram_session_or_create_new(message.chat.id, session)

    chat_id = message.chat.id
    bot.send_message(chat_id, get_message('HELP_TEXT'))


@bot.message_handler(commands=['current'])
def current(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)
    chat_id = message.chat.id
    bot.send_message(chat_id, get_message('CURRENT_COURSE', create_string_with_course_and_author_by_course_id(telegram_session.current_course_id, session)))


@bot.message_handler(commands=['checkout'])
def checkout(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    bot.send_message(chat_id=message.chat.id,
                     text="Выберите курс, на который хотите переключиться:",
                     reply_markup=print_available_courses_as_buttons_by_telegram_id(message.chat.id, session),
                     parse_mode='HTML')

    telegram_session.state = states.WAITING_FOR_COURSE_NAME
    session.commit()


@bot.message_handler(commands=['getdays'])
@no_current_course_decorator
def getdays(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)
    chat_id = message.chat.id

    bot.send_message(chat_id, get_message('NUM_OF_DAYS', create_string_with_course_and_author_by_course_id(telegram_session.current_course_id, session),
                                          get_student_by_telegram_id_and_course_id(telegram_session.current_course_id, message.chat.id, session).number_of_days))


@bot.message_handler(commands=['register'])
def register(message):
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    bot.send_message(chat_id=message.chat.id,
                     text="Список доступных курсов для регистрации:",
                     reply_markup=print_available_courses_as_buttons(session),
                     parse_mode='HTML')

    telegram_session.state = states.WAITING_FOR_COURSE_NAME_REGISTER
    session.commit()


@bot.message_handler(func=lambda message: get_telegram_session_or_create_new(message.chat.id, session).state == states.WAITING_FOR_EMAIL_REGISTER)
def waiting_for_email(message):

    email = message.text
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    student = get_student_by_email_and_course_id(telegram_session.temp_course_register_id, email, session)

    if student is None:
        bot.send_message(message.chat.id, get_message('EMAIL_ERROR'))
        return
    else:
        if student.telegram_id is None:
            bot.send_message(message.chat.id, get_message('EMAIL_SUCCESS'))
            telegram_session.temp_lms_email = email
            telegram_session.temp_course_student_id = student.id
            telegram_session.state = states.WAITING_FOR_AUTHCODE_REGISTER
            session.commit()
        else:
            bot.send_message(message.chat.id, get_message('ANOTHER_USER_ALREADY_REGISTERED'))


@bot.message_handler(func=lambda message: get_telegram_session_or_create_new(message.chat.id, session).state == states.WAITING_FOR_AUTHCODE_REGISTER)
def waiting_for_authcode(message):

    authcode = message.text
    telegram_session = get_telegram_session_or_create_new(message.chat.id, session)

    student = get_student_by_id(telegram_session.temp_course_student_id, session)

    if student is None:
        bot.send_message(message.chat.id, get_message('UNKNOWN_ERROR'))
        return
    else:
        if student.registration_code == authcode:
            bot.send_message(message.chat.id, get_message('AUTHCODE_SUCCESS'))
            telegram_session.current_course_id = telegram_session.temp_course_register_id
            student.telegram_id = telegram_session.telegram_id
            telegram_session.state = states.REGISTERED
            session.commit()
        else:
            bot.send_message(message.chat.id, get_message('AUTHCODE_ERROR'))
            return


#################
# QUERY HANDLER #
#################


@bot.callback_query_handler(func=lambda call: get_telegram_session_or_create_new(call.message.chat.id, session).state == states.WAITING_FOR_COURSE_NAME_REGISTER)
def handle_query(call):

    if call.data.startswith("course_id"):
        callback_data = parse_callback_data(call.data)
        telegram_session = get_telegram_session_or_create_new(call.message.chat.id, session)

        courses = get_all_active_courses_by_telegram_id(call.message.chat.id, session)
        ids_courses = [course.id for course in courses]

        if int(callback_data['course_id']) not in ids_courses:
            telegram_session.temp_course_register_id = int(callback_data['course_id'])
            telegram_session.state = states.WAITING_FOR_EMAIL_REGISTER
            session.commit()

            bot.send_message(call.message.chat.id, get_message('ENTER_EMAIL', callback_data['course_name_with_author']))
        else:
            bot.send_message(call.message.chat.id, get_message('YOU_ARE_ALREADY_REGISTERED'))


@bot.callback_query_handler(func=lambda call: get_telegram_session_or_create_new(call.message.chat.id, session).state == states.WAITING_FOR_COURSE_NAME)
def handle_query(call):

    if call.data.startswith("course_id"):
        callback_data = parse_callback_data(call.data)
        telegram_session = get_telegram_session_or_create_new(call.message.chat.id, session)
        telegram_session.current_course_id = int(callback_data['course_id'])
        telegram_session.state = states.REGISTERED
        session.commit()
        bot.send_message(call.message.chat.id, get_message('CHECKOUT_SUCCESS',
                                                           create_string_with_course_and_author_by_course_id(callback_data['course_id'], session)))


##################
#  LONG POLLING  #
##################

if __name__ == '__main__':
    bot.polling(none_stop=True)
