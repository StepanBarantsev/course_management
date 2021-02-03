from telegram.chat.messages import get_message_with_course_prefix
import telegram.chat.states as states
from telegram.chat.helpers import print_available_courses_as_buttons, \
    parse_callback_data, get_student_by_email_and_course_id, get_student_by_id, \
    create_string_with_course_and_author_by_course_id, get_all_active_courses_by_telegram_id,\
    print_available_courses_as_buttons_by_telegram_id, get_student_by_telegram_id_and_course_id
from telegram.chat.singleton_bot import bot
from telegram.chat.db_session import session_scope, get_telegram_session_or_create_new, get_telegram_session_or_create_new_with_existing_db_session


################
#  DECORATORS  #
################

def no_current_course_decorator(f):
    def func(message):
        with session_scope() as session:
            telegram_session = get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)
            chat_id = message.chat.id
            if telegram_session.current_course_id is not None:
                f(message)
            else:
                bot.send_message(chat_id, get_message_with_course_prefix('NO_CURRENT_COURSE', chat_id))

    return func


##############
#  HANDLERS  #
##############


@bot.message_handler(commands=['start'], func=lambda message: get_telegram_session_or_create_new(message.chat.id).state == states.START)
def hello(message):
    with session_scope() as session:
        get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)

        chat_id = message.chat.id
        bot.send_message(chat_id, get_message_with_course_prefix('HELP_TEXT', chat_id))


@bot.message_handler(commands=['help'])
def help(message):
    with session_scope() as session:
        get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)

        chat_id = message.chat.id
        bot.send_message(chat_id, get_message_with_course_prefix('HELP_TEXT', chat_id))


@bot.message_handler(commands=['current'])
def current(message):
    with session_scope() as session:
        telegram_session = get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)
        chat_id = message.chat.id
        bot.send_message(chat_id, get_message_with_course_prefix('CURRENT_COURSE', chat_id, create_string_with_course_and_author_by_course_id(telegram_session.current_course_id, session)))


@bot.message_handler(commands=['checkout'])
def checkout(message):
    with session_scope() as session:
        telegram_session = get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)

        bot.send_message(chat_id=message.chat.id,
                         text="Выберите курс, на который хотите переключиться:",
                         reply_markup=print_available_courses_as_buttons_by_telegram_id(message.chat.id, session),
                         parse_mode='HTML')

        telegram_session.state = states.WAITING_FOR_COURSE_NAME
        session.commit()


@bot.message_handler(commands=['getdays'])
@no_current_course_decorator
def getdays(message):
    with session_scope() as session:
        telegram_session = get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)
        chat_id = message.chat.id

        bot.send_message(chat_id, get_message_with_course_prefix('NUM_OF_DAYS', chat_id,
                                                                 get_student_by_telegram_id_and_course_id(telegram_session.current_course_id, message.chat.id, session).number_of_days))


@bot.message_handler(commands=['register'])
def register(message):
    with session_scope() as session:
        telegram_session = get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)

        bot.send_message(chat_id=message.chat.id,
                         text="Список доступных курсов для регистрации:",
                         reply_markup=print_available_courses_as_buttons(session),
                         parse_mode='HTML')

        telegram_session.state = states.WAITING_FOR_COURSE_NAME_REGISTER
        session.commit()


@bot.message_handler(func=lambda message: get_telegram_session_or_create_new(message.chat.id).state == states.WAITING_FOR_EMAIL_REGISTER)
def waiting_for_email(message):
    with session_scope() as session:

        email = message.text
        telegram_session = get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)

        student = get_student_by_email_and_course_id(telegram_session.temp_course_register_id, email, session)

        if student is None:
            bot.send_message(message.chat.id, get_message_with_course_prefix('EMAIL_ERROR', message.chat.id))
            return
        else:
            if student.telegram_id is None:
                bot.send_message(message.chat.id, get_message_with_course_prefix('EMAIL_SUCCESS', message.chat.id))
                telegram_session.temp_lms_email = email
                telegram_session.temp_course_student_id = student.id
                telegram_session.state = states.WAITING_FOR_AUTHCODE_REGISTER
                session.commit()
            else:
                bot.send_message(message.chat.id, get_message_with_course_prefix('ANOTHER_USER_ALREADY_REGISTERED', message.chat.id))


@bot.message_handler(func=lambda message: get_telegram_session_or_create_new(message.chat.id).state == states.WAITING_FOR_AUTHCODE_REGISTER)
def waiting_for_authcode(message):
    with session_scope() as session:

        authcode = message.text
        telegram_session = get_telegram_session_or_create_new_with_existing_db_session(message.chat.id, session)

        student = get_student_by_id(telegram_session.temp_course_student_id, session)

        if student is None:
            bot.send_message(message.chat.id, get_message_with_course_prefix('UNKNOWN_ERROR', message.chat.id))
            return
        else:
            if student.registration_code == authcode:
                bot.send_message(message.chat.id, get_message_with_course_prefix('AUTHCODE_SUCCESS', message.chat.id))
                telegram_session.current_course_id = telegram_session.temp_course_register_id
                student.telegram_id = telegram_session.telegram_id
                telegram_session.state = states.REGISTERED
                session.commit()
            else:
                bot.send_message(message.chat.id, get_message_with_course_prefix('AUTHCODE_ERROR', message.chat.id))
                return


#################
# QUERY HANDLER #
#################


@bot.callback_query_handler(func=lambda call: get_telegram_session_or_create_new(call.message.chat.id).state == states.WAITING_FOR_COURSE_NAME_REGISTER)
def handle_query(call):
    with session_scope() as session:

        if call.data.startswith("course_id"):
            callback_data = parse_callback_data(call.data)
            telegram_session = get_telegram_session_or_create_new_with_existing_db_session(call.message.chat.id, session)

            courses = get_all_active_courses_by_telegram_id(call.message.chat.id, session)
            ids_courses = [course.id for course in courses]

            if int(callback_data['course_id']) not in ids_courses:
                course_id = int(callback_data['course_id'])
                telegram_session.temp_course_register_id = course_id
                telegram_session.state = states.WAITING_FOR_EMAIL_REGISTER
                session.commit()

                course_name_with_author = create_string_with_course_and_author_by_course_id(course_id, session)
                bot.send_message(call.message.chat.id, get_message_with_course_prefix('ENTER_EMAIL', call.message.chat.id, course_name_with_author))
            else:
                bot.send_message(call.message.chat.id, get_message_with_course_prefix('YOU_ARE_ALREADY_REGISTERED', call.message.chat.id))


@bot.callback_query_handler(func=lambda call: get_telegram_session_or_create_new(call.message.chat.id).state == states.WAITING_FOR_COURSE_NAME)
def handle_query(call):
    with session_scope() as session:
        if call.data.startswith("course_id"):
            callback_data = parse_callback_data(call.data)
            telegram_session = get_telegram_session_or_create_new_with_existing_db_session(call.message.chat.id, session)
            telegram_session.current_course_id = int(callback_data['course_id'])
            telegram_session.state = states.REGISTERED
            session.commit()
            bot.send_message(call.message.chat.id, get_message_with_course_prefix('CHECKOUT_SUCCESS', call.message.chat.id,
                                                                                  create_string_with_course_and_author_by_course_id(callback_data['course_id'], session)))


##################
#  LONG POLLING  #
##################

if __name__ == '__main__':
    bot.polling(none_stop=True)
