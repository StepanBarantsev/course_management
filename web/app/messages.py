from telegram.chat.helpers import try_to_send_message_to_student
from telegram.chat.singleton_bot import bot
from web.app.email import send_email
from flask import current_app, flash


# Это стандартный метод для посылки сообщения студенту
# Он включает в себя три разных возможности для посылки
# 1) Можно послать сообщение в телеграме. Оно будет выслано, если студент зарегистирован у бота.
# 2) Можно послать сообщение по почте. Оно посылается только если включен флаг в настройках юзера
# 3) Можно сгенерировать письмо для аутлука, тогда его нужно будет отправить самостоятельно
def send_message_to_telegram_and_mail_or_outlook(user, student, message, subject, text_body, html_body):
    try_to_send_message_to_student(student, message, bot)

    if user.flag_emails_from_default_mail:
        send_email(subject, sender=current_app.config['ADMINS'][0], recipients=[student.email],
                   text_body=text_body, html_body=html_body)
        flash('Было отправлено письмо студенту с адреса %s!' % current_app.config['ADMINS'][0])
    else:
        generate_and_save_outlook(user, student, message, subject)


def generate_and_save_outlook(user, student, message, subject):
    pass
