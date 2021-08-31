from pathlib import Path
import logging
import requests
import time

import telegram
from telegram import (
    ReplyKeyboardRemove,
    Update,
    ParseMode,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.ext.callbackqueryhandler import CallbackQueryHandler

from utils import TgLogger
from utils.inline_keyboard import *
from messages import Messages

TOKEN = Path(".secrets/bot_token.txt").read_text()
MESSAGES = Messages()
HOST = "http://carolyn-spreadsheets:5000"
BROADCAST_MESSAGE, BROADCAST_PUBLISH_DONE = range(2)
GRADES_CALLBACK = 1

logging.setLoggerClass(TgLogger)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
LOG = logging.getLogger(__name__)

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
    look_msg = update.message.reply_html(MESSAGES.Assignments.START)
    try:
        data = requests.get(f"{HOST}/grades", params={"tg_id": user_id}).json()

        subjects = data["subjects"]
        assignments = data["assignments"]

        if len(subjects) > 1:
            context.user_data["subjects"] = subjects
            context.user_data["all_assignments"] = assignments
            reply_markup = build_menu_of_subjects(subjects)
            update.message.reply_text(
                text=MESSAGES.Assignments.SELECT_COURSE, reply_markup=reply_markup
            )
        else:
            context.user_data["assignments"] = assignments
            reply_markup = build_menu_of_assignments(assignments)
            update.message.reply_text(
                text=MESSAGES.Assignments.SELECT_ASSNT, reply_markup=reply_markup
            )
        return_value = GRADES_CALLBACK

    except:
        LOG.exception("Failed to get grades.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return_value = ConversationHandler.END
    diff = time.monotonic() - start
    look_msg.edit_text(MESSAGES.Assignments.timeit(diff))
    return return_value


def callback(update: Update, context: CallbackContext):

    call = update.callback_query.data

    # Нажатие кнопок при выборе задания
    if call.startswith("assignment#"):

        if "$back$" in call:
            subjects = context.user_data["subjects"]
            reply_markup = build_menu_of_subjects(subjects)
            update.callback_query.message.edit_text(
                text=MESSAGES.Assignments.SELECT_COURSE, reply_markup=reply_markup
            )
            return GRADES_CALLBACK

        assignments = context.user_data["assignments"]
        name, subject = call.split("#")[1:3]

        reply_markup = build_menu_of_assignments(
            assignments, name, has_back_button=context.user_data["has_back_button"]
        )

        f = lambda ass: ass["name"] == name and ass["subject"] == subject
        assignment = next(filter(f, assignments))
        update.callback_query.message.edit_text(
            text=MESSAGES.Assignments.get(assignment['name'], 
                                        assignment['points'],
                                        assignment['how_to_display']), 
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

    # Нажатие кнопок при выборе дисциплины
    if call.startswith("subject#"):
        all_assignments = context.user_data["all_assignments"]
        subject = call.split("#")[1]

        f = lambda ass: ass["subject"] == subject
        assignments = list(filter(f, all_assignments))
        context.user_data["assignments"] = assignments
        context.user_data["has_back_button"] = True

        reply_markup = build_menu_of_assignments(assignments, has_back_button=True)
        update.callback_query.message.edit_text(
            MESSAGES.Assignments.SELECT_ASSNT, reply_markup=reply_markup
        )

    if call.startswith("cancel#"):
        update.callback_query.message.edit_text(
            MESSAGES.Assignments.END,
        )
        return ConversationHandler.END

    return GRADES_CALLBACK

def timeout(update: Update, context: CallbackContext):
    update.callback_query.message.edit_text(
        MESSAGES.Assignments.TIMEOUT, 
        )
    return ConversationHandler.END

def grades_end(update: Update, context: CallbackContext):
    update.message.edit_text(
        MESSAGES.Assignments.TIMEOUT, 
        )
    update.message.reply_text(
        MESSAGES.Assignments.END
    )
    return ConversationHandler.END


def broadcast(update: Update, context: CallbackContext):
    """Команда: разослать студентам."""
    access_message = update.message.reply_text("🔐 Проверка доступа...")
    user_id = update.message.from_user.id
    try:
        r = requests.get(f"{HOST}/broadcast", params={"tg_id": user_id})
        assert r.status_code == 200, "Доступ запрещен к /broadcast"
        data = r.json()
        context.bot_data["groups"] = data
        access_message.edit_text(f"✅ Доступ получен")

        groups_list = [k for k in data.keys()]
        n = 5  # кол-во кнопок в строке
        summary_keyboard = []
        LOG.info(groups_list)
        for i in range((len(groups_list) // n) + 1):
            LOG.debug(groups_list[i * n : i * n + n])
            keyboard_row = groups_list[i * n : i * n + n]
            summary_keyboard.append(keyboard_row)

        LOG.info(f"{summary_keyboard}")
        reply_keyboard = telegram.ReplyKeyboardMarkup(
            summary_keyboard,
            one_time_keyboard=True,
        )
        update.message.reply_text("Выбери группу", reply_markup=reply_keyboard)
        return BROADCAST_MESSAGE
    except:
        access_message.edit_text("🤚 Команда не может быть выполнена")
        LOG.exception("Не удалось отправить сообщение в бродкаст.")
        return ConversationHandler.END


def publish_message(update: Update, context: CallbackContext):
    """Чел выбирает группу и для нее готовится сообщение."""
    message = update.message.text
    context.user_data["broadcast_to"] = message
    update.message.reply_html(
        f"🖋 Сообщение для группы {message}:",
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
    return BROADCAST_PUBLISH_DONE


def publish_done(update: Update, context: CallbackContext):
    """Рассылка выполняется здесь."""
    message = f"📣 {update.message.text}\n<i>— {update.message.from_user.name}</i>"
    group = context.user_data["broadcast_to"]
    send_status = update.message.reply_text("0%")
    students = context.bot_data["groups"][group]["students"]
    for i, student in enumerate(students):
        progress = i / len(students) * 100
        if student["tg_id"]:
            context.bot.send_message(
                chat_id=student["tg_id"], text=message, parse_mode="HTML"
            )
        send_status.edit_text(f"{progress:.1f}% 🏃‍♂️ Рассылка")
    send_status.edit_text("100% 👍 Все сообщения разосланы")
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    update.message.reply_text("Отмена операции", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ==================================================================== HANDLERS


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    LOG.bot = updater.bot

    start_handler = CommandHandler("start", start)

    grades_handler = ConversationHandler(
        entry_points=[CommandHandler("grades", grades)],
        states={
            GRADES_CALLBACK: [CallbackQueryHandler(callback)],
            ConversationHandler.TIMEOUT: [
                MessageHandler(Filters.text | Filters.command, timeout)
                ],
            # ConversationHandler.END: [
            #     MessageHandler(Filters.text | Filters.command, grades_end)
            # ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=10,
    )

    broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast)],
        states={
            BROADCAST_MESSAGE: [MessageHandler(Filters.text, publish_message)],
            BROADCAST_PUBLISH_DONE: [MessageHandler(Filters.text, publish_done)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(grades_handler)
    dispatcher.add_handler(broadcast_handler)
    #dispatcher.add_handler(callback_handler)

    # Начало работы бота
    updater.start_polling()


if __name__ == "__main__":
    main()
