from typing import Any, Callable

from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from models.user import find_user


def user_required(callback: Callable[[Update, CallbackContext], Any]):
    """Декоратор для поиска пользователя в базе данных"""

    def wrapper(update: Update, context: CallbackContext):
        global current_user

        if not update.effective_user:
            return

        current_user = find_user(context.bot.id, update.effective_user.id)
        if not current_user:
            update.message.reply_text("Извините, но мы не знакомы")
            return

        return callback(update, context)

    return wrapper

    # if row.get("chat_id") != chat_id:
    #     query = """
    #         DECLARE $bot_id AS Uint64;
    #         DECLARE $user_id AS Uint64;
    #         DECLARE $chat_id AS Uint64;
    #         UPDATE users SET chat_id = $chat_id
    #         WHERE bot_id == $bot_id AND user_id == $user_id;
    #     """
    #     params["chat_id"] = chat_id
    #     exec_query(query, params)
