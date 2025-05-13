from telegram.config import ConfigTelegram
from logger import logger
from datetime import datetime, timedelta
import requests


def send_mail(student):
    logger.critical(f'Отправляем письмо студенту {student}')
    date = datetime.today().date() + timedelta(days=31)
    # bcc просто на мою запасную почту
    requests.post(f'{ConfigTelegram.MAIL_ADDRESS}/email',
                  json={"secret": ConfigTelegram.MAIL_KEY,
                        "message": {
                        "to": [student.email],
                        "bcc": ['pythonbeginners.info@gmail.com'],
                        "from": ConfigTelegram.CERT_MAIL_ADDR,
                        "subject": f"Сертификат ({student.course.name})",
                        "body": f'''
<!DOCTYPE html><html><head></head><body>
Добрый день! <br/>
<br/>
Электронный сертификат доступен по ссылке: <a href="{student.cert_link}">{student.cert_link}<a/><br/>
<br/>
Вы можете разместить ссылку на сертификат в своих резюме, публичных профилях и любых других общедоступных местах.\n
<br/>
Если Вы заметили ошибку -- напишите, мы все исправим.<br/>
<br/>
Также Вы получаете 15% скидку на любой курс из нашего расписания, при условии оплаты курса в течение месяца (т.е. до {date}). Вы можете использовать скидку для себя или передать ее другу. При регистрации на курс просто сообщите ваш e-mail и код купона на скидку: “{ConfigTelegram.COUPON_CODE}”.<br/>
<br/>
С уважением, <br/>
команда поддержки <br/>
Software-Testing.RU
</body></html>''',
"html": True}},
)

