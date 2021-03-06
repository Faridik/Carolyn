from collections import defaultdict
from pathlib import Path
import logging
import requests
import time
import datetime
import os

import telegram
from telegram import (
    ReplyKeyboardRemove,
    Update,
    ParseMode,
)
from telegram import message
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.ext.callbackqueryhandler import CallbackQueryHandler

# from utils import TgLogger
from utils.inline_keyboard import *
from messages import Messages

ADMIN = "admin"
HOST = "http://carolyn-google:5000"
MESSAGES = Messages()
SUB_TIME_DELTA = datetime.timedelta(minutes=30)
TOKEN = Path(".secrets/bot_token.txt").read_text()
DEV_CHAT = -507530583  # ID канала где собираются логи

BROADCAST_MESSAGE, BROADCAST_PUBLISH_DONE = range(2)
GRADES_ASSNT, GRADES_VIEW = range(2)

# logging.setLoggerClass(TgLogger)
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
        LOG.exception("@{username} вызвал: Ошибка подключения к сервису Google.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return

    if req.status_code != 200:
        LOG.error(f"Ошибка авторизации у пользователя @{username} {data}")
        err = data.get("error", "")
        update.message.reply_text(text=MESSAGES.Auth.failure(err))
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return

    update.message.reply_text(
        text=MESSAGES.Auth.hello(data["student"]),
    )


def grades_start(update: Update, context: CallbackContext):
    """Сообщение 'Выбери дисциплину'.

    Обновляет текст сообщения и дает клавиатуру с выбором дисциплины.
    """
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    start = time.monotonic()

    # Длинная операция, сообщим о запущенном процессе.
    look_msg = update.message.reply_html(MESSAGES.Assignments.START)

    try:
        req = requests.get(f"{HOST}/grades", params={"tg_id": user_id})
        data = req.json()
    except:
        LOG.exception("Failed to get grades.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return ConversationHandler.END

    if req.status_code != 200:
        LOG.error(f"Ошибка получения оценок у пользователя @{username} {data}")
        err = data.get("error", "")
        update.message.reply_text(text=MESSAGES.Assignments.failure(err))
        diff = time.monotonic() - start
        look_msg.edit_text(MESSAGES.Assignments.timeit(diff))
        update.message.reply_sticker(MESSAGES.Stickers.bad())
        return

    # При инициализации бота словарь отсутствует
    if "fingerprints" not in context.bot_data:
        context.bot_data["fingerprints"] = defaultdict(str)

    context.bot_data["fingerprints"][user_id] = data["fingerprint"]

    context.user_data["subjects"] = data["subjects"]
    context.user_data["assignments"] = data["assignments"]
    diff = time.monotonic() - start
    look_msg.edit_text(MESSAGES.Assignments.timeit(diff))
    update.message.reply_text(
        MESSAGES.Assignments.SELECT_COURSE,
        reply_markup=build_menu_of_subjects(data["subjects"]),
    )
    return GRADES_ASSNT


def grades_pick_assignment(update: Update, context: CallbackContext):
    """Сообщение 'Выбери задание'.

    Обновляет текст сообщения и дает клавиатуру с выбором дисциплины.
    В `callback_query` содержится имя предмета, либо ключевое слово.
    Может завершить диалог.
    """
    query = update.callback_query
    query.answer()
    if query.data == "cancel":
        query.edit_message_text(MESSAGES.Assignments.END, reply_markup=None)
        return ConversationHandler.END
    context.user_data["selected_subject"] = query.data
    assignments = [
        a for a in context.user_data["assignments"] if a["subject"] == query.data
    ]
    query.edit_message_text(
        MESSAGES.Assignments.SELECT_ASSNT,
        reply_markup=build_menu_of_assignments(assignments, has_back_button=True),
    )
    return GRADES_VIEW


def grades_view(update: Update, context: CallbackContext):
    """Отображение домашки.

    В `callback_query` содержится UUID, идентификатор задания. Либо команда:
    cancel или back. Может завершить диалог.
    """
    query = update.callback_query
    query.answer()

    if query.data == "cancel":
        query.edit_message_text(MESSAGES.Assignments.END, reply_markup=None)
        return ConversationHandler.END

    if query.data == "back":
        subjects = context.user_data["subjects"]
        query.edit_message_text(
            MESSAGES.Assignments.SELECT_COURSE,
            reply_markup=build_menu_of_subjects(subjects),
        )
        return GRADES_ASSNT

    assignments_map = {a["uuid"]: a for a in context.user_data["assignments"]}
    assignment = assignments_map[query.data]
    subject = context.user_data["selected_subject"]

    raw_menu = build_menu(
        [
            InlineKeyboardButton("Отмена", callback_data="cancel"),
            InlineKeyboardButton("⏮ Назад", callback_data=subject),
        ],
        2,
    )

    reply_markup = InlineKeyboardMarkup(raw_menu)

    query.edit_message_text(
        text=MESSAGES.Assignments.get(
            assignment["name"],
            assignment["points"],
            assignment["how_to_display"],
            assignment["notes"],
            assignment["deadline"],
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )

    return GRADES_ASSNT


def broadcast(update: Update, context: CallbackContext):
    """Команда: разослать студентам."""
    access_message = update.message.reply_text("🔐 Проверка доступа...")
    user_id = update.message.from_user.id
    try:
        r = requests.get(f"{HOST}/students", params={"tg_id": user_id})
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

    def send_message(chat_id: int, message: telegram.Message):
        txt = message.text if message.text else message.caption
        txt = "" if not txt else txt
        txt = f"📣 {txt}\n<i>— {message.from_user.name}</i>"

        if message.document:
            context.bot.send_document(
                chat_id=chat_id,
                caption=txt,
                parse_mode="HTML",
                document=message.document,
            )
        elif message.photo:
            file = message.photo[-1]
            context.bot.send_photo(
                chat_id=chat_id, caption=txt, parse_mode="HTML", photo=file
            )
        elif message.animation:
            context.bot.send_animation(
                chat_id=chat_id,
                caption=txt,
                parse_mode="HTML",
                animation=message.animation,
            )
        else:
            context.bot.send_message(chat_id=chat_id, text=txt, parse_mode="HTML")

    group = context.user_data["broadcast_to"]
    send_status = update.message.reply_text("0%")
    try:
        students = context.bot_data["groups"][group]["students"]
    except:
        LOG.exception(
            "Не получилось взять студента с группой, %s, группы %s",
            group,
            context.bot_data["groups"],
        )
    for i, student in enumerate(students):
        progress = i / len(students) * 100
        if student["tg_id"]:
            send_message(student["tg_id"], update.message)
        send_status.edit_text(f"{progress:.1f}% 🏃‍♂️ Рассылка")

    send_message(DEV_CHAT, update.message)
    send_status.edit_text("100% 👍 Все сообщения разосланы")
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    update.message.reply_text("Отмена операции", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def sub(update: Update, context: CallbackContext):
    """Подписка на обновление оценок"""

    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Длинная операция, сообщим о запущенном процессе.
    msg = update.message.reply_text(text=MESSAGES.Sub.START)

    try:
        req = requests.get(
            f"{HOST}/sub",
            params={"tg_id": user_id},
        )
        data = req.json()
    except requests.exceptions.RequestException:
        LOG.exception("@{user_id} вызвал: Ошибка подключения к сервису Google.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return

    if req.status_code != 200:
        LOG.error(f"Ошибка подписки, у пользователя @{username} {data}")
        err = data.get("error", "")
        update.message.reply_text(text=MESSAGES.Sub.failure(err))
        update.message.reply_sticker(MESSAGES.Stickers.bad())
        return

    msg.edit_text(text=MESSAGES.Sub.SUBBED)


def unsub(update: Update, context: CallbackContext):
    """Отписка от обновления оценок"""

    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Длинная операция, сообщим о запущенном процессе.
    msg = update.message.reply_text(text=MESSAGES.Unsub.START)

    try:
        req = requests.get(
            f"{HOST}/unsub",
            params={"tg_id": user_id},
        )
        data = req.json()
    except requests.exceptions.RequestException:
        LOG.exception("@{user_id} вызвал: Ошибка подключения к сервису Google.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return

    if req.status_code != 200:
        LOG.error(f"Ошибка отписки, у пользователя @{username} {data}")
        err = data.get("error", "")
        update.message.reply_text(text=MESSAGES.Unsub.failure(err))
        update.message.reply_sticker(MESSAGES.Stickers.bad())
        return

    msg.edit_text(text=MESSAGES.Unsub.UNSUBBED)


def variant(update: Update, context: CallbackContext):
    """Проверка своего варианта внутри группы"""

    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Длинная операция, сообщим о запущенном процессе.
    msg = update.message.reply_text(text=MESSAGES.Variant.START)

    try:
        req = requests.get(
            f"{HOST}/student",
            params={"tg_id": user_id},
        )
        data = req.json()
    except requests.exceptions.RequestException:
        LOG.exception("@{user_id} вызвал: Ошибка подключения к сервису Google.")
        update.message.reply_sticker(MESSAGES.Stickers.DEAD)
        return

    if req.status_code != 200:
        LOG.error(f"Ошибка выяснения варианта, у пользователя @{username} {data}")
        err = data.get("error", "")
        update.message.reply_text(text=MESSAGES.Variant.failure(err))
        update.message.reply_sticker(MESSAGES.Stickers.bad())
        return

    msg.edit_text(text=MESSAGES.Variant.get(data["student"]["number"]))


def about(update: Update, context: CallbackContext):
    """Получить инфу о развертывании бота."""
    commit_id = os.environ.get("CAROLYN_DEPLOY_ID", "")
    verison = os.environ.get("CAROLYN_DEPLOY_VERSION", "")
    update.message.reply_html(MESSAGES.Deploy.about(commit_id, verison))


def error(update: Update, context: CallbackContext):
    LOG.error(msg="Exception while handling an update:", exc_info=context.error)
    if context.error is not None and update is not None:
        update.message.reply_text("Ой, кажется у меня %s" % repr(context.error))
    update.message.reply_sticker(MESSAGES.Stickers.DEAD)
    return ConversationHandler.END


# ======================================================================= SCHED


def grades_checker(context: CallbackContext):
    """Задача по проверке оценок.

    Запрашивает список подписавшихся вместе с подключенными домашками. У
    каждого студента проверяет отпечаток. Отпечаток (fingerprint) - текстовая
    строка захешированных оценок. При изменении оценок, меняется и их хеш. Бот с
    каждым вызовом задачи запоминает эти хеши всех студентов и сверяет их. Если
    вдруг несовпадение, то значит, что данные об оценках были изменены.

    Это простой и универсальный способ смотреть изменения, но он не дает инфы о
    том, в каком задании появилась новая оценка.

    """

    r = requests.get(
        f"{HOST}/students",
        params={"god_mode": True, "sub_only": True, "include_assignments": True},
    )
    data = r.json()
    context.bot_data["groups"] = data

    # При инициализации бота словарь отсутствует
    if "fingerprints" not in context.bot_data:
        context.bot_data["fingerprints"] = defaultdict(str)

    for group in data.values():
        for student in group["students"]:
            tg_id = student["tg_id"]
            fingerprint = student.get("fingerprint", "")
            old_fingerprint = context.bot_data["fingerprints"][tg_id]
            # При инициализации у старого отпечатка ещё не установлено значение.
            # Там находится пустая строка, поэтому нужна дополн. проверка.
            if old_fingerprint != fingerprint and old_fingerprint != "":
                context.bot.send_message(
                    chat_id=tg_id,
                    text=MESSAGES.Sub.GRADES_CHANGED,
                )
                LOG.info(
                    "Fingerprint = %s, old = %s",
                    fingerprint,
                    context.bot_data["fingerprints"][tg_id],
                )
            context.bot_data["fingerprints"][tg_id] = fingerprint


# ==================================================================== HANDLERS


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    jobber = updater.job_queue
    jobber.run_repeating(grades_checker, SUB_TIME_DELTA)
    LOG.bot = updater.bot

    start_handler = CommandHandler("start", start)

    grades_handler = ConversationHandler(
        entry_points=[CommandHandler("grades", grades_start)],
        states={
            GRADES_ASSNT: [CallbackQueryHandler(grades_pick_assignment)],
            GRADES_VIEW: [CallbackQueryHandler(grades_view)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast)],
        states={
            BROADCAST_MESSAGE: [MessageHandler(Filters.text, publish_message)],
            BROADCAST_PUBLISH_DONE: [
                MessageHandler(Filters.all & ~Filters.command, publish_done)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    sub_handler = CommandHandler("sub", sub)
    unsub_handler = CommandHandler("unsub", unsub)
    variant_handler = CommandHandler("variant", variant)
    about_handler = CommandHandler("about", about)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(grades_handler)
    dispatcher.add_handler(broadcast_handler)
    dispatcher.add_handler(sub_handler)
    dispatcher.add_handler(unsub_handler)
    dispatcher.add_handler(variant_handler)
    dispatcher.add_handler(about_handler)
    dispatcher.add_error_handler(error)

    # Начало работы бота
    updater.start_polling()


if __name__ == "__main__":
    main()
