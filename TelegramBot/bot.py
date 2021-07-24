import logging
import os
import platform
import time
import requests

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

TOKEN = "1903048555:AAFK-d7prKvOvwwXo0IPzeRwJ1ZcuOT5ty8"  # os.environ["TOKEN"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# ================================================================ BOT COMMANDS

# Стартовое сообщение (к команде /start)
def start(update, context):

    p = context.args[0] if len(context.args) > 0 else None

    data = requests.get("http://127.0.0.1:5000/auth").text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello World! {context.args} Authorized? {data}",
    )


# Ответ на не командное сообщение (отвечает тем же сообщением)
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


# ==================================================================== HANDLERS

start_handler = CommandHandler("start", start)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)

# Начало работы бота
updater.start_polling()
