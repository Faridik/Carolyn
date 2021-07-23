#Подключение к боту
from telegram.ext import Updater
updater = Updater(token='1903048555:AAFK-d7prKvOvwwXo0IPzeRwJ1ZcuOT5ty8', use_context=True)

dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

#Стартовое сообщение (к команде /start)
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello World! Это не просто копипаста, я вот что-то подправил даже")

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)   

#Ответ на не командное сообщение (отвечает тем же сообщением)
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

from telegram.ext import MessageHandler, Filters
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

#Начало работы бота
updater.start_polling()