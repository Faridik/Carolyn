import logging
import requests
from pathlib import Path


from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from messages import Messages

TOKEN = Path(".secrets/bot_token.txt").read_text()
MESSAGES = Messages()
HOST = "http://carolyn-spreadsheets:5000"
CHAT_LOG_ID = -507530583

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
LOG = logging.getLogger(__name__)

LOG.debug("Token is %s", TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def log_to_group_chat(update: Update, text: str):
    update.message.bot.send_message(chat_id=CHAT_LOG_ID, text=text)


# ================================================================ BOT COMMANDS


def start(update: Update, context: CallbackContext):
    """Стартовое сообщение (к команде /start)"""

    user_id = update.message.from_user.id

    p = context.args[0] if len(context.args) > 0 else None

    if p is None:
        update.message.reply_markdown_v2(text=MESSAGES.auth.NO_AUTH)
        return

    update.message.reply_text(text=MESSAGES.auth.START)

    LOG.info(f"Authenticanting {user_id}")

    try:
        data = requests.get(
            f"{HOST}/auth",
            params={"token": p, "tg_id": user_id},
        ).json()
    except requests.exceptions.ConnectionError:
        log_to_group_chat(update, 
            text=MESSAGES.auth.failure_log(
                {'desc':'ConnectionError'})
        )
        update.message.reply_sticker(MESSAGES.stickers.DEAD)
        return

    if data['error']:
        log_to_group_chat(update, 
            text=MESSAGES.auth.failure_log(data)
        )
        update.message.reply_text(
            text=MESSAGES.auth.failure(data)
        )
        update.message.reply_sticker(MESSAGES.stickers.DEAD)
        return

    log_to_group_chat(update, 
        text=MESSAGES.auth.success_log(data['student'])
    )
    update.message.reply_text(
        text=MESSAGES.auth.hello(data['student']),
    )


def grades(update: Update, context: CallbackContext):
    """Команда: Получить оценки студента."""

    user_id = update.message.from_user.id
    try:
        data = requests.get(f"{HOST}/grades", params={"tg_id": user_id}).json()
        score = data["score"]
        grade = data["grade"]
        n_of_assignments = len(data["assignments"])

        score_message = MESSAGES.score.get(grade, score, n_of_assignments)
        update.message.reply_html(score_message)
        update.message.reply_sticker(MESSAGES.stickers.bad())
    except:
        LOG.exception("Failed to get grades.")
        update.message.reply_sticker(MESSAGES.stickers.DEAD)


def echo(update: Update, context: CallbackContext):
    """Ответ на не командное сообщение (отвечает тем же сообщением)"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


# ==================================================================== HANDLERS

start_handler = CommandHandler("start", start)
grades_handler = CommandHandler("grades", grades)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(grades_handler)
dispatcher.add_handler(echo_handler)

# Начало работы бота
updater.start_polling()
