import telebot
import telegram.config

bot = telebot.TeleBot(telegram.config.ConfigTelegram.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def hello(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Помощь по боту (ЗАГЛУШКА)')


@bot.message_handler(commands=['register'])
def hello(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Регистрация у бота')


if __name__ == '__main__':
    bot.polling(none_stop=True)
