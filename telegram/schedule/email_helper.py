import smtplib, ssl
from telegram.config import ConfigTelegram
from logger import logger


def send_email(receiver_email, message, subject, bcc,
               port=ConfigTelegram.CERT_MAIL_PORT,
               server=ConfigTelegram.CERT_MAIL_SERVER,
               email=ConfigTelegram.CERT_MAIL_USERNAME,
               password=ConfigTelegram.CERT_MAIL_PASSWORD):
    logger.critical(f"Отправляется письмо на адрес {receiver_email}")
    message = "From: %s\r\n" % email + "To: %s\r\n" % receiver_email + "BCC: %s\r\n" % bcc + "Subject: %s\r\n" % subject + "\r\n" + message
    with smtplib.SMTP_SSL(server, port) as server:
        server.login(email, password)
        server.sendmail(email, receiver_email, message.encode('utf-8'))


