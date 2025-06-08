from api_helper.certificate_helper import CertDBHelper
from api_helper.date_helper import DateHelper
from telegram.chat.singleton_bot import bot
from telegram.chat.db_session import session_scope
from web.app.models import Course
from telegram.chat.messages import get_message_with_course_prefix
from telebot.apihelper import ApiTelegramException
from api_helper.lms_api_helper import LmsApiHelper
from datetime import datetime
from dateutil.relativedelta import relativedelta
from telegram.chat.helpers import get_trainer_by_telegram_id
from web.app.models import Student
from logger import logger
from telegram.schedule.email_helper import send_mail
from telegram.config import ConfigTelegram

cert_db_helper = CertDBHelper()

def job():
    with session_scope() as session:
        courses = session.query(Course).filter_by(deleted=False).all()
        discount_coupon = ConfigTelegram.COUPON_CODE

        for course in courses:
            students = course.get_all_not_deleted_students()
            message_about_days = f'Курс: {course.name}\n\nДата: {datetime.today().strftime("%d.%m.%Y")}\n\n'

            for student in students:
                if student.status == Student.student_statuses['active']:
                    student.number_of_days -= 1
                    logger.info(f"Уменьшаем на 1 количество дней у студента {student}")
                    is_delivered = send_message_about_days_to_student(student, session)

                    if is_delivered:
                        message_about_days += f'У студента {student.name} осталось {student.number_of_days} дней. (Доставлено)\n'
                    else:
                        message_about_days += f'У студента {student.name} осталось {student.number_of_days} дней. (Не доставлено)\n'
                    if course.is_certificate_needed:
                        if student.cert_link is None:
                            cert_link = try_to_generate_cert_to_student(student)
                            if cert_link is not None:
                                send_message_about_certificate(student.telegram_id, student.course.author.name, cert_link, discount_coupon, student)
            try:
                bot.send_message(course.author.telegram_id, message_about_days)
                trainer = get_trainer_by_telegram_id(course.author.telegram_id, session)
                trainer.flag_is_messages_from_bot_is_delivered = True
                session.commit()
                logger.info(f"Сообщение о курсе {course} успешно доставлено тренеру {trainer}")
            except:
                trainer = get_trainer_by_telegram_id(course.author.telegram_id, session)
                trainer.flag_is_messages_from_bot_is_delivered = False
                session.commit()
                logger.warning(f"Сообщение о курсе {course} НЕ доставлено тренеру {trainer}")

            session.commit()


def send_message_about_days_to_student(student, session):
    try:
        if student.number_of_days % 10 == 0 and student.number_of_days >= 0:
            course_name_and_author = f'{student.course.name} [{student.course.author.name}]'
            if student.number_of_days == 0:
                bot.send_message(student.telegram_id, get_message_with_course_prefix('ZERO_DAYS_SCHEDULED', None, course_name=course_name_and_author))
                logger.info(f"Студенту {student} доставлено сообщение о том что у него осталось 0 дней")
            else:
                bot.send_message(student.telegram_id, get_message_with_course_prefix('NUM_OF_DAYS_SCHEDULED', None, student.number_of_days, course_name=course_name_and_author))
                logger.info(f"Студенту {student} доставлено сообщение о том что у него остался {student.number_of_days} деней")
            return True
        if student.number_of_days == -10:
            student.status = Student.student_statuses['dropped']
            session.commit()
            logger.info(f"У студента {student} просрочилось время на 10 дней и его записывают в бросившие курс")
        return False
    except ApiTelegramException:
        logger.info(f"Студенту {student} не было доставлено сообщение о количестве дней")
        return False


def send_message_about_certificate(student_telegram_id, trainer_telegram_id, cert_link, discount_coupon, student):
    date_after_month = (datetime.today() + relativedelta(months=1)).strftime("%d.%m.%Y")
    course_name_and_author = f'{student.course.name} [{student.course.author.name}]'
    send_mail(student)
    try:
        bot.send_message(student_telegram_id, get_message_with_course_prefix('CERTIFICATE', None, cert_link, discount_coupon, student.course.review_link, date_after_month, student.course.author.name, course_name=course_name_and_author))
        logger.info(f"Студенту с telegram_id {student_telegram_id} доставлено сообщение о сертификате: {cert_link}")
    except ApiTelegramException:
        logger.critical(f"Студенту с telegram_id {student_telegram_id} НЕ доставлено сообщение о сертификате: {cert_link}")

    bot.send_message(trainer_telegram_id, get_message_with_course_prefix('CERTIFICATE', None, cert_link, discount_coupon, student.course.review_link, date_after_month, student.course.author.name, course_name=course_name_and_author))


def try_to_generate_cert_to_student(student):
    if LmsApiHelper.can_we_give_certificate_to_student(student.lms_id, student.course.lms_id):
        cert_link = 'http://cert.software-testing.ru/' + cert_db_helper.insert_certificate(student.email, student.name, student.course.name.split(',')[0], DateHelper.create_current_date_in_specific_format(), False)
        print(cert_link)
        student.cert_link = cert_link
        student.status = 'finished'
        logger.critical(f"Сертификат с ссылкой {cert_link} был сгенерирован")
        return cert_link
    return None


job()
