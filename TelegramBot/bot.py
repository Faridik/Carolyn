import logging
from typing import Any, Optional
import requests
import time
from pathlib import Path


from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import telegram
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
"""ID канала где собираются логи"""
CHAT_LOG_ID = -507530583


class TgLogger(logging.Logger):
    """Обертка на логгер, чтобы можно было использовать обычные лог-функции,
    но при этом получать логи в телеграм чат.

    Есть баг, который не позволяет вызывать лог с ленивыми аргументами. Если
    вызывать
    ```python
    LOG.warning("%s", var)
    ```
    , то можно получить такую ошибку:
    ```python
    TypeError: _log_to_telegram() got multiple values for argument 'msg'
    ```
    Поэтому используйте,
    ```
    LOG.warning(f"{var}")
    ```
    """

    def __init__(self, name, level=logging.NOTSET):
        self._bot = None
        self._chat_log_id = CHAT_LOG_ID
        return super(TgLogger, self).__init__(name, level)

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

    def _log_to_telegram(
        self,
        msg: str,
        *args,
        emoji: str,
    ):
        if self._bot is not None:
            txt = f"{emoji} {msg};"
            self._bot.send_message(chat_id=CHAT_LOG_ID, text=txt)

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log_to_telegram(msg=msg, emoji="⚠", *args)
        return super().warning(
            msg,
            *args,
            **kwargs,
        )

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log_to_telegram(msg=msg, emoji="💢", *args)
        return super().error(
            msg,
            *args,
            **kwargs,
        )

    def exception(self, msg, *args: Any, **kwargs: Any) -> None:
        self._log_to_telegram(msg=msg, emoji="💥", *args)
        return super().exception(msg, *args, **kwargs)


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.setLoggerClass(TgLogger)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
LOG = logging.getLogger(__name__)
LOG.bot = updater.bot

# ================================================================ BOT COMMANDS


def start(update: Update, context: CallbackContext):
    """Стартовое сообщение (к команде /start)"""

    user_id = update.message.from_user.id
    username = update.message.from_user.username
    student_token = context.args[0] if len(context.args) > 0 else None

    if student_token is None:
        update.message.reply_markdown_v2(text=MESSAGES.Auth.NO_AUTH)
        return

    # Длинная операция, сообщим о запущенном процессе.
    update.message.reply_text(text=MESSAGES.Auth.START)

    LOG.info(f"Authenticanting {user_id}")

    try:
        req = requests.get(
            f"{HOST}/auth",
            params={"token": student_token, "tg_id": user_id},
        )
        data = req.json()
    except requests.exceptions.RequestException:
        LOG.exception("@{username} вызвал: Ошибка подключения к сервису Spreadsheets.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return

    if req.status_code != 200:
        LOG.error(f"Ошибка авторизации, у пользователя @{username} {data}")
        err = data.get("error", "")
        update.message.reply_text(text=MESSAGES.Auth.failure(err))
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return

    update.message.reply_text(
        text=MESSAGES.Auth.hello(data["student"]),
    )


def grades(update: Update, context: CallbackContext):
    """Команда: Получить оценки студента."""

    user_id = update.message.from_user.id

    start = time.monotonic()
    # Длинная операция, сообщим о запущенном процессе.
    look_msg = update.message.reply_html(MESSAGES.Score.START)
    try:
        data = requests.get(f"{HOST}/grades", params={"tg_id": user_id}).json()
        score = data["score"]
        grade = data["grade"]
        n_of_assignments = len(data["assignments"])

        score_message = MESSAGES.Score.get(grade, score, n_of_assignments)
        update.message.reply_html(score_message)
        update.message.reply_sticker(MESSAGES.Stickers.bad())
    except:
        LOG.exception("Failed to get grades.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
    diff = time.monotonic() - start
    look_msg.edit_text(MESSAGES.Score.timeit(diff))


def broadcast(update: Update, context: CallbackContext):
    """Команда: разослать студентам."""
    access_message = update.message.reply_text("🔐 Проверка доступа...")
    user_id = update.message.from_user.id
    try:
        r = requests.get(f"{HOST}/broadcast", params={"tg_id": user_id})
        assert r.status_code == 200, "Доступ запрещен к /broadcast"
        data = r.json()
        access_message.edit_text(f"👨‍💻 {data['name']}")

        kb = telegram.ReplyKeyboardMarkup(
            [
                [telegram.KeyboardButton("5374"), telegram.KeyboardButton("5371")],
                [telegram.KeyboardButton("1337")],
            ],
            one_time_keyboard=True,
        )
        update.message.reply_text("Выбери группу", reply_markup=kb)
    except:
        access_message.edit_text("🤚 Команда не может быть выполнена")
        LOG.exception("Не удалось отправить сообщение в бродкаст.")


def echo(update: Update, context: CallbackContext):
    """Ответ на не командное сообщение (отвечает тем же сообщением)"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


# ==================================================================== HANDLERS

start_handler = CommandHandler("start", start)
grades_handler = CommandHandler("grades", grades)
broadcast_handler = CommandHandler("broadcast", broadcast)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(grades_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(broadcast_handler)

# Начало работы бота
updater.start_polling()
