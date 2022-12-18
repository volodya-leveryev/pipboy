# from telegram import InlineKeyboardButton as btn
from telegram import Update
from telegram.ext import CallbackContext

# from telegram.ext import CallbackQueryHandler as CBQ
from telegram.ext import (
    #     CommandHandler,
    ConversationHandler,
    Dispatcher,
    #     Filters,
    #     MessageHandler,
)
from enum import Enum

# from models.category import Category
# from models.notice import Notice
# from models.user import Role, User


class NoticeState(Enum):
    pass


def register_handlers(disp: Dispatcher) -> None:
    """Регистрация обработчиков"""
    # disp.add_handler(CBQ(category_list, pattern="^category/list$"))
    # disp.add_handler(CBQ(category_show, pattern="^category/[0-9]+$"))
    # disp.add_handler(create_category())
    # disp.add_handler(create_notice())


# def category_list(update: Update, context: CallbackContext):
#     """Список категорий"""
#     query = update.callback_query

#     buttons = [[btn("Возврат в главное меню", callback_data="main_menu")]]
#     for cat in Category.get_list():
#         cat_btn = btn(cat.name, callback_data=f"category/{cat.id}")
#         buttons.append([cat_btn])
#     keyboard = InlineKeyboardMarkup(buttons)

#     user = User.get(update.effective_user.id)
#     if user.role() == Role.ADMIN:
#         cat_btn = btn("Создать категорию", callback_data="category/create")
#         buttons.append([cat_btn])

#     query.answer()
#     query.edit_message_text("Выберите категорию:", reply_markup=keyboard)


# def category_show(update: Update, context: CallbackContext):
#     """Показать категорию"""
#     query = update.callback_query
#     _, cat_id = query.data.split("/")
#     cat_id = int(cat_id)
#     if not context.user_data or not isinstance(context.user_data, dict):
#         context.user_data = {}
#     context.user_data["category"] = cat_id

#     buttons = [[btn("Возврат в главное меню", callback_data="main_menu")]]
#     for note in Notice.get_list(cat_id):
#         button = btn(note.title, callback_data=f"notice/{note.id}")
#         buttons.append([button])

#     user = User.get(update.effective_user.id)
#     if user.role() == "admin":
#         button = btn("Создать объявление", callback_data="notice/create")
#         buttons.append([button])

#     query.answer()
#     query.edit_message_text("Выберите объявление:", reply_markup=kbd(buttons))


# def create_category() -> ConversationHandler:
#     states = {
#         TYPE_CATEGORY: [MessageHandler(~Filters.command, type_category)],
#     }
#     return ConversationHandler(
#         entry_points=[CBQ(start_category_create, pattern="category/create")],
#         states=states,
#         fallbacks=[CommandHandler("cancel", cancel)],
#         name="Create category",
#         persistent=True,
#     )


# def start_category_create(update: Update, _context: CallbackContext) -> int:
#     query = update.callback_query
#     query.edit_message_text("Введите название категории:")
#     return TYPE_CATEGORY


# def type_category(update: Update, context: CallbackContext) -> int:
#     Category.create(update.message.text)
#     show_main_menu(update)
#     context.user_data.clear()
#     return ConversationHandler.END


# def create_notice() -> ConversationHandler:
#     states = {
#         TYPE_NOTICE_TITLE: [
#             MessageHandler(~Filters.command, type_notice_title),
#         ],
#         TYPE_NOTICE_TEXT: [
#             MessageHandler(~Filters.command, type_notice_text),
#         ],
#     }
#     return ConversationHandler(
#         entry_points=[CBQ(start_notice_create, pattern="notice/create")],
#         states=states,
#         fallbacks=[CommandHandler("cancel", cancel)],
#         name="Create notice",
#         persistent=True,
#     )


# def start_notice_create(update: Update, _context: CallbackContext) -> int:
#     query = update.callback_query
#     query.edit_message_text("Введите заголовок объявления:")
#     return TYPE_NOTICE_TITLE


# def type_notice_title(update: Update, context: CallbackContext) -> int:
#     context.user_data["title"] = update.message.text
#     update.message.reply_text("Введите текст объявления:")
#     return TYPE_NOTICE_TEXT


# def type_notice_text(update: Update, context: CallbackContext) -> int:
#     context.user_data["text"] = update.message.text
#     Notice.create(context.user_data)
#     show_main_menu(update)
#     context.user_data.clear()
#     return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Прервать диалог"""
    if isinstance(context.user_data, dict):
        context.user_data.clear()
    else:
        context.user_data = {}
    return ConversationHandler.END
