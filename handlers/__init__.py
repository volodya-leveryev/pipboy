from telegram import CallbackQuery, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler as CBQHandler
from telegram.ext import CommandHandler, Dispatcher, MessageHandler, Filters

from models.user import User, find_user

current_user: User


def register_handlers(disp: Dispatcher):
    """Регистрируем обработчики"""

    # Начало общения с пользователем
    disp.add_handler(CommandHandler("start", start_cmd))

    # Главное меню
    disp.add_handler(CBQHandler(main_menu_cbq, pattern="^main_menu$"))

    # Объявления
    # notices.register(dispatcher)

    # Необработанные сообщения / команды / нажатия
    disp.add_handler(MessageHandler(Filters.all, not_implemented))
    disp.add_handler(CBQHandler(not_implemented))

    # Обработка ошибки
    disp.add_error_handler(error)


def user_required(handler):
    def wrapper(update, context):
        global current_user
        try:
            current_user = find_user(update.effective_user.id)
        except (AttributeError, IndexError):
            update.message.reply_text("Извините, но мы не знакомы")
        return handler(update, context)

    return wrapper


def show_main_menu(prev: Update | CallbackQuery):
    """Показать главное меню"""

    msg = "Главное меню:"
    menu = InlineKeyboardMarkup(current_user.get_main_menu())

    if isinstance(prev, Update):
        prev.message.reply_text(msg, reply_markup=menu)
    elif isinstance(prev, CallbackQuery):
        prev.edit_message_text(msg, reply_markup=menu)


@user_required
def start_cmd(update: Update, _context: CallbackContext):
    """Команда start"""
    if current_user:
        update.message.reply_text(f"Здравствуйте, {current_user.name}!")
    show_main_menu(update)


@user_required
def main_menu_cbq(update: Update, _context: CallbackContext):
    """Показать главное меню"""
    query = update.callback_query
    query.answer()
    show_main_menu(query)


def not_implemented(update: Update, _context: CallbackContext):
    msg = "Извините, я вас не понимаю"
    if query := update.callback_query:
        query.answer
        query.edit_message_text(msg)
    else:
        update.message.reply_text(msg)


def error(update, context: CallbackContext):
    """Обработчик ошибки"""
    print("Update:", update)
    print("Error:", context.error)
    update.message.reply_text("Ой, произошла ошибка..")
