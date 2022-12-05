from telegram import InlineKeyboardButton as btn
from telegram import InlineKeyboardMarkup as kbd
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler as CBQHandler
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Dispatcher,
    Filters,
    MessageHandler,
)

from models.group import Group

# from models.user import User

(ENTER_NAME,) = range(1)


def register_handlers(disp: Dispatcher) -> None:
    disp.add_handler(CBQHandler(groups_menu, pattern="^groups_list$"))
    disp.add_handler(CBQHandler(group_create, pattern="^group_create$"))

    group_create_states = {
        ENTER_NAME: [MessageHandler(~Filters.command, group_create_0)],
    }
    disp.add_handler(
        ConversationHandler(
            entry_points=[],
            states=group_create_states,  # type: ignore
            name="create_group",
            persistent=True,
            fallbacks=[CommandHandler("cancel", cancel)],  # type: ignore
        )
    )


def groups_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    buttons = [
        [btn("Главное меню", callback_data="main_menu")],
        [btn("Создать группу", callback_data="groups_create")],
    ]
    for g in Group.get_list():
        buttons.append([btn(g.name, callback_data=f"{g.id}")])

    query.edit_message_text("", reply_markup=kbd(buttons))


def group_create(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text("Введите название группы")
    return ENTER_NAME


def group_create_0(update: Update, context: CallbackContext) -> int:

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> object:
    """Прервать диалог"""
    if isinstance(context.user_data, dict):
        context.user_data.clear()
    else:
        context.user_data = {}
    return ConversationHandler.END


SELECT_GROUP, ENTER_MESSAGE, CONFIRM = range(3)


# def start_dispatch_group_msg(update: Update, _context: CallbackContext) -> int:
#     """Начало разговора"""
#     tg_user = update.effective_user
#     if not tg_user:
#         retval = ConversationHandler.END
#     else:
#         db_user = User.get(tg_user.id)
#         if db_user:
#             groups = db_user.manage_on
#             if groups:
#                 buttons = [
#                     [
#                         InlineKeyboardButton(g.name, callback_data=f"{g.id} {g.name}")
#                         for g in groups
#                     ]
#                 ]
#                 update.message.reply_text(
#                     "Начинаем рассылку сообщения. Выберите группу …",
#                     reply_markup=InlineKeyboardMarkup(buttons),
#                 )
#                 retval = SELECT_GROUP
#             else:
#                 update.message.reply_text(
#                     "Извините, но вы не можете рассылать сообщения."
#                 )
#                 retval = ConversationHandler.END
#         else:
#             update.message.reply_text("Извините, но мы не знакомы.")
#             retval = ConversationHandler.END
#     return retval


# def choose_group(update: Update, context: CallbackContext) -> int:
#     """Пользователь выбрал группу для рассылки"""
#     query = update.callback_query
#     group_id, group_name = query.data.split(maxsplit=1)
#     context.user_data["group_id"] = int(group_id)
#     query.edit_message_text(
#         f"Выбрана группа {group_name}.\n" "Введите сообщение для рассылки …"
#     )
#     query.answer()
#     return ENTER_MESSAGE


# def typing_message(update: Update, context: CallbackContext) -> int:
#     """Пользователь ввел сообщение для рассылки"""
#     context.user_data["message"] = update.message.text
#     buttons = [
#         [
#             InlineKeyboardButton("Да", callback_data="YES"),
#             InlineKeyboardButton("Нет", callback_data="NO"),
#         ]
#     ]
#     update.message.reply_text(
#         "Вы уверены что нужно начать рассылку?",
#         reply_markup=InlineKeyboardMarkup(buttons),
#     )
#     return CONFIRM


# def confirm(update: Update, context: CallbackContext) -> int:
#     """Подтверждение рассылки"""
#     query = update.callback_query
#     if query.data == "YES":
#         query.message.edit_text("Начинаем рассылку сообщения …")
#         for user in Group.members(context.user_data["group_id"]):
#             print(user)
#         print(context.user_data)
#         retval = ConversationHandler.END
#     else:
#         query.message.edit_text("Отменяю рассылку")
#         for key in ("user_id", "message"):
#             if key in context.user_data:
#                 del context.user_data[key]
#         retval = ConversationHandler.END
#     query.answer()
#     return retval


# def cancel(update: Update, context: CallbackContext) -> int:
#     """Прерывание разговора"""
#     for key in ("user_id", "message"):
#         if key in context.user_data:
#             del context.user_data[key]
#     update.message.reply_text("Извините если не смог помочь.")
#     return ConversationHandler.END


# def handler():
#     """Обработчик разговора"""
#     return ConversationHandler(
#         entry_points=[CommandHandler("dispatch", start_dispatch_group_msg)],
#         states={
#             SELECT_GROUP: [CallbackQueryHandler(choose_group)],
#             ENTER_MESSAGE: [MessageHandler(~Filters.command, typing_message)],
#             CONFIRM: [CallbackQueryHandler(confirm)],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#         # per_message=True,
#         name="Dispatch message to group",
#         persistent=True,
#     )
