from telegram import InlineKeyboardMarkup, Update
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton as btn
from telegram.ext import CallbackContext, Dispatcher, Filters
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler

from utils.config import config
from utils.decorators import user_required
from models.post import find_posts, get_keywords, posts
from models.user import get_user


def register_handlers(disp: Dispatcher):
    """Регистрируем обработчики"""

    # Начало общения с пользователем
    disp.add_handler(CommandHandler("start", main_menu))

    # Главное меню
    disp.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))

    # Рассылка сообщений
    # disp.add_handler(disp_msg.handler)

    # Поиск объявлений
    disp.add_handler(MessageHandler(~Filters.command, post_search))
    disp.add_handler(CallbackQueryHandler(post_show, pattern=r"^post_show\ "))

    # Необработанные сообщения / команды / нажатия
    disp.add_handler(MessageHandler(Filters.all, not_implemented))
    disp.add_handler(CallbackQueryHandler(not_implemented))

    # Обработка ошибки
    if config.get("BOT_ENV") != "development":
        disp.add_error_handler(error)

    # Меню команд в кнопке
    disp.bot.set_my_commands([])


@user_required
def main_menu(update: Update, _context: CallbackContext):
    """Показать главное меню"""
    msg = "Главное меню:"
    kbd = InlineKeyboardMarkup(get_user().get_main_menu())
    if query := update.callback_query:
        query.answer()
        query.edit_message_text(msg, reply_markup=kbd)
    else:
        update.message.reply_text(msg, reply_markup=kbd)


def post_search(update: Update, _context: CallbackContext):
    """Найти объявление по ключевым словам"""
    keywords = get_keywords(update.message.text)
    results = find_posts(keywords)
    if results:
        if len(results) == 1:
            i = results[0]
            title = posts["titles"][i]
            text = posts["posts"][i]
            update.message.reply_text(f"{title}\n{text}")
        else:
            buttons = [
                [btn(posts["titles"][i], callback_data=f"post_show {i}")]
                for i in results
            ]
            kbd = InlineKeyboardMarkup(buttons)
            update.message.reply_text("Выберите сообщение:", reply_markup=kbd)
    else:
        update.message.reply_text(
            "Извините, но ничего не найдено. Попробуйте изменить запрос."
        )


def post_show(update: Update, _context: CallbackContext):
    """Показ выбранного объявления"""
    query = update.callback_query
    query.answer()
    _, i = query.data.split(maxsplit=1)
    i = int(i)
    title, text = posts["titles"][i], posts["posts"][i]
    query.edit_message_text(f"{title}\n{text}")


def not_implemented(update: Update, _context: CallbackContext):
    """Обработчик команд и сообщений не обработанных штатным образом"""
    msg = "Извините, я вас не понимаю"
    if query := update.callback_query:
        query.answer()
        query.edit_message_text(msg)
    else:
        update.message.reply_text(msg)


def error(update, context: CallbackContext):
    """Обработчик ошибки"""
    print("Update:", update)
    print("Error:", context.error)
    msg = "Ой, произошла ошибка.."
    if query := update.callback_query:
        query.answer()
        query.edit_message_text(msg)
    else:
        update.message.reply_text(msg)
