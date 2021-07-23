def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello World! Это не просто копипаста, я вот что-то подправил даже")

from telegram.ext import Updater
updater = Updater(token='1903048555:AAFK-d7prKvOvwwXo0IPzeRwJ1ZcuOT5ty8', use_context=True)

dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()