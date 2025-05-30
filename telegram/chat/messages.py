from telegram.chat.db_session import session_scope
from telegram.chat.db_session import get_telegram_session_or_create_new_with_existing_db_session
from web.app.models import Course
from telegram.chat.helpers import create_string_with_course_and_author_by_course_id
from logger import logger


def get_message_with_course_prefix(name, telegram_id, *args, course_name=None):
    with session_scope() as session:
        message = get_message(name, *args)

        names_required_course_prefix = ['NUM_OF_DAYS', 'FIRST_PAYMENT', 'NO_FIRST_PAYMENT', 'NUM_OF_DAYS_SCHEDULED', 'CERTIFICATE',
                                        'HOMEWORK_SOLUTION', 'MESSAGE_ABOUT_HOMEWORK_SOLUTION', 'HOMEWORK_IS_NOT_COMPLETED', 'HOMEWORK_NOT_EXIST',
                                        'HELP_COURSE', 'BLOCKS_MESSAGE', 'ZERO_DAYS_SCHEDULED']

        if name in names_required_course_prefix:
            if telegram_id is not None:
                current_telegram_session = get_telegram_session_or_create_new_with_existing_db_session(telegram_id, session)

                if current_telegram_session.current_course_id is not None:
                    course = session.query(Course).filter_by(id=int(current_telegram_session.current_course_id)).first()
                    course_name_and_author = create_string_with_course_and_author_by_course_id(course.id, session)
                    message = f'Курс: {course_name_and_author}\n\n{message}'

            elif course_name is not None:
                message = f'Курс: {course_name}\n\n{message}'

        return message


def get_message(name, *args):
    logger.debug(f"Получаем сообщение для отправки по ключевому слову: {name}")

    if name == 'ENTER_EMAIL':
        return f'''Вы выбрали курс {args[0]}

Введите Ваш e-mail, с которым Вы записаны на курс (то есть e-mail в системе электронного обучения LMS)

Если Вы хотите выбрать другой курс, то снова введите команду /register'''

    if name == 'EMAIL_ERROR':
        return '''На данном курсе не числится студент с таким e-mail. Возможно Вы неправильно выбрали курс или ввели некорректный email.
         
Попробуйте ввести email повторно, либо же пройдите регистрацию заново (с помощью команды /register)'''

    if name == 'EMAIL_SUCCESS':
        return 'Ваш email успешно принят. Введите регистрационный код, который был получен Вами в письме об успешном зачислении на курс.'

    if name == 'UNKNOWN_ERROR':
        return '''Произошла неизвестная ошибка. Сообщите об этом тренеру'''

    if name == 'AUTHCODE_SUCCESS':
        return '''Код успешно принят. Вы зачислены на курс!'''

    if name == 'AUTHCODE_ERROR':
        return '''Вы ввели неправильный код регистрации. Попробуйте ввести его еще раз.
        
Также Вы можете пройти регистрацию заново. Для этого введите /register'''

    if name == 'CURRENT_COURSE':
        if args[0] is None:
            return '''На данный момент никакой из курсов не является активным. 
            
Если Вы уже зарегистрированы на какой то из курсов, Вы можете сделать его активным при помощи /checkout'''
        else:
            return f'''На данный момент активен курс {args[0]}

Чтобы активировать другой курс, выполните команду /checkout'''

    if name == 'YOU_ARE_ALREADY_REGISTERED':
        return '''Вы уже зарегистрированы на данный курс!'''

    if name == 'ANOTHER_USER_ALREADY_REGISTERED':
        return '''На курс уже зачислен другой пользователь с таким email. Если Вы считаете что произошла какая то ошибка, сообщите об этом тренеру.'''

    if name == 'CHECKOUT_SUCCESS':
        return f'''Вы успешно переключились на курс {args[0]}'''

    if name == 'NUM_OF_DAYS':
        return f'''Оставшееся количество дней: {args[0]}'''

    if name == 'ZERO_DAYS_SCHEDULED':
        return f'''Добрый день.

У Вас закончилось время поддержки. Для продолжения прохождения курса следует продлить время или приобрести новый блок (см. правила).'''

    if name == 'NUM_OF_DAYS_SCHEDULED':
        return f'''Добрый день.
        
Напоминаю, что до конца курса у Вас осталось {args[0]} дней.'''

    if name == 'CERTIFICATE':
        return f'''Добрый день.

Поздравляю с успешным окончанием курса!

Ссылка на сертификат: {args[0]}

Вы можете разместить ссылку на сертификат в своих резюме, публичных профилях и любых других общедоступных местах.

Также Вы получаете 15% скидку на любой курс из нашего расписания, при условии оплаты курса в течение месяца (то есть до {args[3]}). Вы можете использовать скидку для себя или передать ее другу. При регистрации на курс просто сообщите ваш e-mail и код купона на скидку: “{args[1]}”.

Кроме того, я буду весьма признателен, если Вы напишете отзыв по результатам прохождения курса: {args[2]}

С уважением,
{args[4]}'''

    if name == 'NO_CURRENT_COURSE':
        return '''У Вас на данный момент нет активного курса.

Выберите курс при помощи команды /checkout либо зарегистрируйтесь с помощью /register

Для более подробной информации выполните команду /help'''

    if name == 'FIRST_PAYMENT':
        return f'''Добрый день!

Оплата была успешно получена. Вы успешно были подключены к курсу.

Ссылка на электронный чек: {args[0]} 

Все материалы (в том числе записи занятий и домашние задания) будут публиковаться в системе дистанционного обучения (для краткости - СДО).

Ссылка на курс: http://software-testing.ru/lms/course/view.php?id={args[1]} 

Не забудьте связаться со мной в мессенджере telegram. Там Вы сможете задать любые вопросы касательно содержимого курса.

Telegram: https://t.me/{args[2]} 

Также Вы можете зарегистрироваться у telegram-бота, у которого можно будет получить дополнительную информацию о курсе. Ссылка на бота: https://t.me/PythonForBeginnersBot

Чтобы зарегистрироваться, используйте следующий код: {args[3]} (введите его боту, когда он попросит).

Если Вы не имеете возможности использовать Telegram, то связь может осуществляться в другом мессенджере (по договоренности), например в скайпе. Однако желательно все же осуществлять связь именно в Telegram.

Дальнейшие инструкции находятся в СДО (Правила участия)

С уважением, {args[4]}'''

    if name == 'NO_FIRST_PAYMENT':
        return f'''Добрый день.

Оплата за {args[0]} была успешно получена.

Ссылка на электронный чек: {args[1]}

С уважением,
{args[2]}'''

    if name == 'HOMEWORK_SOLUTION':
        return f'''Ссылка на решение домашнего задания: 
{args[0]}'''

    if name == "MESSAGE_ABOUT_HOMEWORK_SOLUTION":
        return "Введите номер задания, решение которого Вы хотите получить. Например '3.3' если Вы хотите получить решение задания 3.3"

    if name == "HOMEWORK_IS_NOT_COMPLETED":
        return "Данное задание не выполнено на максимальный балл. Вы не можете посмотреть его решение."

    if name == "HOMEWORK_NOT_EXIST":
        return "Вы ввели название несуществующей домашней работы. Попробуйте ввести другое название или напишите тренеру."

    if name == 'HELP':
        return '''Здравствуйте. Данный бот предназначен для предоставления студентам различного рода информации о курсе.
        
Бот поддерживает следующие команды:

/register -- позволяет зарегистрироваться на курс. Для успешной регистрации нужно будет по запросу бота ввести e-mail с которым Вы зарегистрированы в LMS, а также код регистрации, пришедший Вам на почту. 
Регистрироваться можно на несколько курсов. При взаимодействии с ботом активным считается один курс.

/current -- позволяет узнать, какой курс сейчас считается активным.

/checkout -- позволяет сделать активным любой из курсов на которых Вы зарегистрированы.

/help -- получить справку по командам бота и по текущему курсу.

/getdays -- бот отдаст количество дней до окончания срока поддержки активного курса.

/getavailableblocks -- бот отдаст все блоки со всеми видеозаписями и дз, которые у Вас приобретены для активного курса.

/getsolution -- позволяет получить решение по домашнему заданию активного курса. Решение можно получить только если задание выполнено на максимальный балл.

Если с ботом какие-то проблемы или есть какие-то пожелания к нему, то пишите мне в личные сообщения в telegram

При нахождении ошибки в решении задач, сообщите об этом в личные сообщения тренеру.'''

    if name == 'HELP_COURSE':
        return f'''Вспомогательные инструкции, касающиеся активного в данный момент курса:

{args[0]}'''

    if name == "BLOCKS_MESSAGE":
        return f'''Скачать доступные блоки можно по ссылке:
        
{args[0]}'''
