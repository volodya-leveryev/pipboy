""" Telegram-бот "Помощник куратора" """

import json
import os
from queue import Queue

from telegram import Bot, Update
from telegram.ext import Dispatcher, Updater

from data.base import connection_to_database
from handlers import register_handlers
from models import obj_type


def get_token() -> str:
    """ Получаем токен """
    return os.getenv('BOT_TOKEN')


def lambda_handler(event: obj_type, _context: obj_type) -> obj_type:
    """ Точка входа в Yandex Cloud Functions (AWS Lambda) """
    bot = Bot(token=get_token())
    message = json.loads(event['body'])
    with connection_to_database():
        dispatcher = Dispatcher(bot, Queue())
        update = Update.de_json(message, bot)
        register_handlers(dispatcher)
        dispatcher.process_update(update)
    return {'statusCode': 200}


def main() -> None:
    """ Точка входа для разработки"""
    with connection_to_database():
        updater = Updater(token=get_token())
        register_handlers(updater.dispatcher)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
