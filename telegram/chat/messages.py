def get_message(name, *args):

    if name == 'HELP_TEXT':
        return '''Чтобы зарегистрироваться на новый курс, введите команду /register'''
    if name == 'ENTER_EMAIL':
        return f'''Вы выбрали курс {args[0]}

Введите Ваш e-mail, с которым Вы записаны на курс (то есть e-mail в системе электронного обучения LMS)

Если Вы хотите выбрать другой курс, то снова введите команду /register'''
