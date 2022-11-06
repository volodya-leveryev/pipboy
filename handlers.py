""" Обработчики команд """

from telegram import Update
from telegram.ext import CallbackContext, Dispatcher
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.filters import Filters

from models import User, InfoMessage


def register_handlers(dispatcher: Dispatcher) -> None:
    """ Регистрация """
    dispatcher.add_handler(CommandHandler('start', start_cmd))

    messages = Filters.text & ~Filters.command
    dispatcher.add_handler(MessageHandler(messages, find_note_by_msg))

    dispatcher.add_error_handler(error)


def start_cmd(update: Update, _context: CallbackContext) -> None:
    """ Команда start """
    tg_user = update.effective_user
    db_user = User.get_by_username(tg_user.username)
    if db_user:
        update.message.reply_text(f"Здравствуйте, {db_user.name}!")
    else:
        update.message.reply_text("Извините, но мы не знакомы.")


def find_note_by_msg(update: Update, _context: CallbackContext) -> None:
    """ Поиск заметки по тексту """
    messages = InfoMessage.get_by_keywords(update.message.text)
    for m in messages:
        update.message.reply_text(m.message)


def error(update: Update, context: CallbackContext) -> None:
    """ Обработчик ошибки """
    print("Update:", update)
    print("Error:", context.error)
    update.message.reply_text("Ой, произошла ошибка..")
