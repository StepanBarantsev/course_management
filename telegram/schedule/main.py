from telegram.chat.singleton_bot import bot
from telegram.chat.db_session import session_scope
from web.app.models import Course
from telegram.chat.messages import get_message_with_course_prefix
from telebot.apihelper import ApiTelegramException
from api_helper.lms_api_helper import LmsApiHelper
from api_helper.fauna_helper import FaunaHelper
from datetime import datetime
from dateutil.relativedelta import relativedelta
from telegram.chat.helpers import get_trainer_by_telegram_id
from web.app.models import Student
from logger import logger


def job():
    with session_scope() as session:
        courses = session.query(Course).filter_by(deleted=False).all()
        discount_coupon = FaunaHelper.get_discount_coupon()

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
                                is_delivered = send_message_about_certificate(student.telegram_id, cert_link, discount_coupon, student)
                                send_message_about_certificate(course.author.telegram_id, cert_link, discount_coupon, student, is_delivered)

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


def send_message_about_certificate(telegram_id, cert_link, discount_coupon, student, is_delivered=None):
    with session_scope() as session:
        date_after_month = (datetime.today() + relativedelta(months=1)).strftime("%d.%m.%Y")
        course_name_and_author = f'{student.course.name} [{student.course.author.name}]'
        if is_delivered is None:
            try:
                bot.send_message(telegram_id, get_message_with_course_prefix('CERTIFICATE', None, cert_link, discount_coupon, student.course.review_link, date_after_month, course_name=course_name_and_author))
                logger.info(f"Студенту с telegram_id {telegram_id} доставлено сообщение о сертификате: {cert_link}")
                return True
            except ApiTelegramException:
                logger.critical(f"Студенту с telegram_id {telegram_id} НЕ доставлено сообщение о сертификате: {cert_link}")
                return False
        # Сообщение для теренера о том, доставлено ли студенту сообщение
        else:
            try:
                if is_delivered:
                    bot.send_message(telegram_id,
                                     get_message_with_course_prefix('CERTIFICATE', None, cert_link, discount_coupon,
                                                                    student.course.review_link,
                                                                    date_after_month,
                                                                    course_name=course_name_and_author) + '\n\n(Доставлено)')
                else:
                    bot.send_message(telegram_id,
                                     get_message_with_course_prefix('CERTIFICATE', None, cert_link, discount_coupon,
                                                                    student.course.review_link,
                                                                    date_after_month,
                                                                    course_name=course_name_and_author) + '\n\n(Не доставлено)')
                logger.info(f"Тренеру с telegram_id {telegram_id} доставлено сообщение о сертификате: {cert_link}")
                trainer = get_trainer_by_telegram_id(telegram_id, session)
                trainer.flag_is_messages_from_bot_is_delivered = True
                session.commit()
            except ApiTelegramException:
                trainer = get_trainer_by_telegram_id(telegram_id, session)
                trainer.flag_is_messages_from_bot_is_delivered = False
                session.commit()
                logger.critical(f"Тренеру НЕ telegram_id {telegram_id} доставлено сообщение о сертификате: {cert_link}")


def try_to_generate_cert_to_student(student):
    if LmsApiHelper.can_we_give_certificate_to_student(student.lms_id, student.course.lms_id):
        cert_link = 'http://cert.software-testing.ru/' + FaunaHelper.create_certify(student)
        print(cert_link)
        student.cert_link = cert_link
        student.status = 'finished'
        logger.critical(f"Сертификат с ссылкой {cert_link} был сгенерирован")
        return cert_link
    return None


job()
