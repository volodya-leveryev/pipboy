from telegram import CallbackQuery
from telegram import InlineKeyboardButton as btn
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler as CBQHandler
from telegram.ext import CommandHandler, Dispatcher

from models.user import get_user


def register_handlers(disp: Dispatcher) -> None:
    """Регистрируем обработчики"""

    # Начало общения с пользователем
    disp.add_handler(CommandHandler("start", start_cmd))
    disp.add_handler(CBQHandler(main_menu_cbq, pattern="^main_menu$"))

    # Объявления
    # notices.register(dispatcher)

    # Обработка ошибки
    disp.add_error_handler(error)


def show_main_menu(prev: Update | CallbackQuery) -> None:
    """Показать главное меню"""

    msg = "Главное меню:"
    row1 = [btn("Поиск объявления", callback_data="notice/search")]
    row2 = [btn("Категории объявлений", callback_data="category/list")]
    menu = InlineKeyboardMarkup([row1, row2])

    if isinstance(prev, Update):
        prev.message.reply_text(msg, reply_markup=menu)
    elif isinstance(prev, CallbackQuery):
        prev.edit_message_text(msg, reply_markup=menu)


def start_cmd(update: Update, context: CallbackContext) -> None:
    """Команда start"""
    try:
        user = get_user(update.effective_user.id)
        update.message.reply_text(f"Здравствуйте, {user.name}!")
        show_main_menu(update)
    except (AttributeError, RuntimeError):
        update.message.reply_text("Извините, но мы не знакомы.")


def main_menu_cbq(update: Update, context: CallbackContext):
    """Показать главное меню"""
    query = update.callback_query
    query.answer()
    show_main_menu(query)


def error(update, context: CallbackContext) -> None:
    """Обработчик ошибки"""
    print("Update:", update)
    print("Error:", context.error)
    update.message.reply_text("Ой, произошла ошибка..")
