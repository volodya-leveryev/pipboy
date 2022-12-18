from typing import Any, Callable

from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from models.user import create_database_user, find_user, set_user


def user_required(callback: Callable[[Update, CallbackContext], Any]):
    """Декоратор для поиска пользователя в базе данных"""

    def wrapper(update: Update, context: CallbackContext):
        if not update.effective_user:
            return

        # Поиск пользователя по идентификатору
        if user := find_user(update.effective_user.id, context.bot.id):
            set_user(user)
            return callback(update, context)

        # Поиск пользователя по нику
        if username := update.effective_user.username:
            user = find_user(username.encode())
            if user:
                set_user(user)
                return callback(update, context)

        # Создаем пользователя
        if user := create_database_user(context.bot.id, update.effective_user):
            return callback(update, context)

    return wrapper
