from web.app.models import Course, Student, User
from telebot import types
from logger import logger


def set_new_state(element, state, session):
    element.state = state
    session.commit()
    logger.info(f'Элемент {element} меняет состояние с {element.state} на {state}')


def print_available_courses_as_buttons(session):
    courses_list = session.query(Course).filter_by(deleted=0).all()

    markup = types.InlineKeyboardMarkup()

    for i in courses_list:
        markup.add(types.InlineKeyboardButton(text=f'{i.name} [{i.author.name}]', callback_data=f'course_id: {i.id}'))

    logger.debug(f'Печатаем существующие курсы: {courses_list} в виде кнопок')
    return markup


def parse_callback_data(string):
    new_strings = string.split(',')

    d = {}

    for s in new_strings:
        d[s.split(':')[0].strip()] = s.split(':')[1].strip()

    logger.debug(f'Парсим данные из колбека')

    return d


def get_student_by_email_and_course_id(course_id, email, session):
    student = session.query(Student).filter_by(course_id=int(course_id)).filter_by(lms_email=email).filter_by(deleted=0).first()
    logger.debug(f'Получаем студента {student} по course_id: {course_id} и email: {email}')
    return student


def get_student_by_telegram_id_and_course_id(course_id, telegram_id, session):

    if course_id is None or telegram_id is None:
        return None

    student = session.query(Student).filter_by(course_id=int(course_id)).filter_by(telegram_id=telegram_id).filter_by(deleted=0).first()
    logger.debug(f'Получаем студента {student} по course_id: {course_id} и telegram_id: {telegram_id}')
    return student


def get_student_by_id(student_id, session):
    student = session.query(Student).filter_by(id=int(student_id)).filter_by(deleted=0).first()
    logger.debug(f'Получаем студента {student} по student_id: {student_id}')
    return student


def create_string_with_course_and_author_by_course_id(course_id, session):
    logger.debug(f'Пробуем создать строку с автором и названием курса для курса с id: {course_id}')
    if course_id is None:
        return None

    course = get_course_by_id(course_id, session)
    if course is None:
        return None
    else:
        logger.debug(f'Создаем строку {course.name} [{course.author.name}] для курса с id: {course_id}')
        return f'{course.name} [{course.author.name}]'


def get_course_by_id(course_id, session):
    course = session.query(Course).filter_by(deleted=0).filter_by(id=int(course_id)).first()
    logger.debug(f'Получаем курс {course} по id: {course_id}')
    return course


def get_all_active_students_by_telegram_id(telegram_id, session):
    students = session.query(Student).filter_by(deleted=0).filter_by(telegram_id=telegram_id).all()
    logger.debug(f'Получаем студентов {students} по telegram_id: {telegram_id}')
    return students


def get_all_active_courses_by_telegram_id(telegram_id, session):
    courses = [i.course for i in get_all_active_students_by_telegram_id(telegram_id, session)]
    logger.debug(f'Получаем курсы {courses} по telegram_id: {telegram_id}')
    return courses


def print_available_courses_as_buttons_by_telegram_id(telegram_id, session):
    courses_list = get_all_active_courses_by_telegram_id(telegram_id, session)

    markup = types.InlineKeyboardMarkup()

    for i in courses_list:
        markup.add(types.InlineKeyboardButton(text=f'{i.name} [{i.author.name}]', callback_data=f'course_id: {i.id}'))

    logger.debug(f'Печатаем существующие курсы: {courses_list} в виде кнопок')

    return markup


def get_current_course_by_id(course_id, session):
    course = session.query(Course).filter_by(id=course_id).first()
    logger.debug(f'Получаем курс {course} по id: {course_id}')
    return course


# Отправляет сообщение студенту, если тот зарегистрирован у телеграм бота
def try_to_send_message_to_student(student, message, bot):
    if student.telegram_id is not None:
        logger.info(f'Пытаемся отправить сообщение {message} студенту: {student.telegram_id}')
        try:
            bot.send_message(student.telegram_id, message)
            logger.info(f'Сообщение {message} успешно доставлено студенту: {student.telegram_id}')
        except:
            logger.warning(f'Сообщение {message} не было доставлено студенту: {student.telegram_id}')


def get_trainer_by_telegram_id(telegram_id, session):
    trainer = session.query(User).filter_by(telegram_id=telegram_id).first()
    logger.debug(f'Получаем тренера {trainer} по telegram_id: {telegram_id}')
    return trainer
