import schedule
import time
from telegram.chat.singleton_bot import bot
from telegram.chat.db_session import session_scope
from web.app.models import Course
from telegram.chat.messages import get_message_with_course_prefix
from telebot.apihelper import ApiTelegramException
from api_helper.lms_api_helper import LmsApiHelper
from api_helper.fauna_helper import FaunaHelper
from web.app.email import send_email
from telegram.config import ConfigTelegram
from flask import render_template
from datetime import datetime


def job():
    with session_scope() as session:
        courses = session.query(Course).filter_by(deleted=0).all()
        discount_coupon = FaunaHelper.get_discount_coupon()

        for course in courses:
            students = course.get_all_not_deleted_students()
            message_about_days = f'Курс {course.name}\n\nДата: {datetime.today().strftime("%d.%m.%Y")}\n\n'

            for student in students:
                student.number_of_days -= 1
                message_about_days += f'У студента {student.name} осталось {student.number_of_days} дней.\n'
                send_message_about_days_to_student(student)
                if course.is_certificate_needed:
                    if student.cert_link is None:
                        cert_link = try_to_generate_cert_to_student(student)
                        send_message_about_certificate(student.telegram_id, cert_link, discount_coupon)
                        send_message_about_certificate(course.author.telegram_id, cert_link, discount_coupon)
                        if course.author.flag_emails_from_default_mail:
                            send_message_about_certificate_to_mail(student, cert_link, discount_coupon)

            bot.send_message(course.author.telegram_id, message_about_days)
            session.commit()


def send_message_about_certificate_to_mail(student, cert_link, discount_coupon):
    send_email(f'Сертификат по курсу {student.course.name}',
               sender=ConfigTelegram.DEFAULT_MAIL,
               recipients=[student.email],
               text_body=render_template('email/certificate.txt', cert_link=cert_link, trainer_name=student.course.author.name, discount_coupon=discount_coupon),
               html_body=render_template('email/certificate.html', cert_link=cert_link, trainer_name=student.course.author.name, discount_coupon=discount_coupon))


def send_message_about_days_to_student(student):
    try:
        if student.number_of_days % 10 == 0:
            bot.send_message(student.telegram_id, get_message_with_course_prefix('NUM_OF_DAYS_SCHEDULED', student.telegram_id, student.number_of_days))
    except ApiTelegramException:
        pass


def send_message_about_certificate(telegram_id, cert_link, discount_coupon):
    try:
        if cert_link is not None:
            bot.send_message(telegram_id, get_message_with_course_prefix('CERTIFICATE', telegram_id, cert_link, discount_coupon))
    except ApiTelegramException:
        pass


def try_to_generate_cert_to_student(student):
    if LmsApiHelper.can_we_give_certificate_to_student(student.lms_id, student.course.lms_id):
        cert_link = 'http://cert.software-testing.ru/' + FaunaHelper.create_certify(student)
        student.cert_link = cert_link
        return cert_link
    return None


schedule.every(10).seconds.do(job)
# schedule.every().day.at("10:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
