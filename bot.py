""" Telegram-бот "Помощник куратора" """
import json
import os
from queue import Queue
from typing import Any, Dict

from telegram import Bot, Update
from telegram.ext import CommandHandler
from telegram.ext import Updater, Dispatcher, CallbackContext


def start_cmd(update: Update, _context: CallbackContext) -> None:
    """ Команда start """
    user = update.effective_user
    update.message.reply_text(f"Hello {user.name}")


def register_handlers(dispatcher: Dispatcher) -> None:
    """ Регистрация """
    dispatcher.add_handler(CommandHandler('start', start_cmd))


def main(event: Dict[str, Any] = None, context: dict = None) -> Dict[str, Any]:
    """ Точка входа """
    token = os.environ.get('BOT_TOKEN')

    if event and context:
        # Production mode
        bot = Bot(token=token)
        dispatcher = Dispatcher(bot, Queue())
        register_handlers(dispatcher)
        body = json.loads(event['body'])
        update = Update.de_json(body, bot)
        dispatcher.process_update(update)
        return {'statusCode': 200}
    else:
        # Development mode
        updater = Updater(token=token)
        register_handlers(updater.dispatcher)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
