import schedule
import time
from telegram.chat.singleton_bot import bot
from telegram.chat.db_session import session_scope
from web.app.models import Course
from telegram.chat.messages import get_message_with_course_prefix
from telebot.apihelper import ApiTelegramException


def job():
    with session_scope() as session:
        courses = session.query(Course).filter_by(deleted=0).all()

        for course in courses:
            students = course.get_all_not_deleted_students()
            message_about_days = f'Курс {course.name}\n\n'

            for student in students:
                student.number_of_days -= 1
                message_about_days += f'У студента {student.name} осталось {student.number_of_days} дней.\n'
                send_message_about_days_to_student(student)
                if course.is_certificate_needed:
                    if student.cert_link is None:
                        cert_link = try_to_generate_cert_to_student(student)
                        send_message_about_certificate(student.telegram_id, cert_link)
                        send_message_about_certificate(course.author.telegram_id, cert_link)

            bot.send_message(course.author.telegram_id, message_about_days)
            session.commit()


def send_message_about_days_to_student(student):
    try:
        if student.number_of_days % 10 == 0:
            bot.send_message(student.telegram_id, get_message_with_course_prefix('NUM_OF_DAYS_SCHEDULED', student.telegram_id, student.number_of_days))
    except ApiTelegramException:
        pass


def send_message_about_certificate(telegram_id, cert_link):
    try:
        if cert_link is not None:
            pass
            # bot.send_message(telegram_id, get_message_with_course_prefix('CERTIFICATE', telegram_id, cert_link))
    except ApiTelegramException:
        pass


def try_to_generate_cert_to_student(student):
    return 'Заглушечная ссылка на сертификат'


schedule.every(10).seconds.do(job)
# schedule.every().day.at("10:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
