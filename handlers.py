""" Обработчики команд """

from telegram import Update
from telegram.ext import Dispatcher
from telegram.ext import CallbackContext, CommandHandler, MessageHandler
from telegram.ext.filters import Filters

from models import User


def register_handlers(dispatcher: Dispatcher) -> None:
    """ Регистрация """
    messages = Filters.text & ~Filters.command
    dispatcher.add_handler(MessageHandler(messages, start_cmd))
    dispatcher.add_handler(CommandHandler('start', find_note_by_msg))


def start_cmd(update: Update, _context: CallbackContext) -> None:
    """ Команда start """
    user = update.effective_user
    db_user = User.get_user(user.id)
    if db_user:
        update.message.reply_text(f"Hello {user.name}")
    else:
        update.message.reply_text("Who are you?")


def find_note_by_msg(update: Update, _context: CallbackContext) -> None:
    """ Поиск заметки по тексту """
    update.message.reply_text(update.message.text)
