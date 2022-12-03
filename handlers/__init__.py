from telegram import CallbackQuery
from telegram import InlineKeyboardButton as btn
from telegram import InlineKeyboardMarkup as kbd
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler as CBQ
from telegram.ext import CommandHandler, Dispatcher

from data.model_user import User


def register_handlers(dispatcher: Dispatcher) -> None:
    # Начало общения с пользователем
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CBQ(main_menu, pattern="^main_menu$"))

    # Объявления
    # notices.register(dispatcher)

    # Обработка ошибки
    dispatcher.add_error_handler(error)


def show_main_menu(prev: Update | CallbackQuery) -> None:
    msg = "Главное меню:"
    main_menu = kbd([[
        btn("Поиск объявления", callback_data="notice/search"),
    ], [
        btn("Категории объявлений", callback_data="category/list"),
    ]])
    if isinstance(prev, Update):
        prev.message.reply_text(msg, reply_markup=main_menu)
    elif isinstance(prev, CallbackQuery):
        prev.edit_message_text(msg, reply_markup=main_menu)


def start(update: Update, _context: CallbackContext) -> None:
    """Команда start"""
    user = User.get(update.effective_user.id)
    if user:
        update.message.reply_text(f"Здравствуйте, {user.name}!")
        show_main_menu(update)
    else:
        update.message.reply_text("Извините, но мы не знакомы.")


def main_menu(update: Update, _context: CallbackContext):
    query = update.callback_query
    query.answer()
    show_main_menu(query)


def error(update: Update, context: CallbackContext) -> None:
    """ Обработчик ошибки """
    print("Update:", update)
    print("Error:", context.error)
    update.message.reply_text("Ой, произошла ошибка..")
