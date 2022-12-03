""" Telegram-бот "Помощник куратора" """

import json
import os
from queue import Queue

from telegram import Bot, Update
from telegram.ext import Dispatcher, Updater

from data.base import DictObject, connection
from data.persistance import YdbPersistence
from handlers import register_handlers


def get_token() -> str:
    """ Читаем токен из переменных окружения """
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise Exception("Token not found")
    return token


def lambda_handler(event: DictObject, _context: DictObject) -> DictObject:
    """ Точка входа в Yandex Cloud Functions (AWS Lambda) """
    bot = Bot(token=get_token())
    message = json.loads(event['body'])
    with connection():
        dispatcher = Dispatcher(bot, Queue(), persistence=YdbPersistence())
        update = Update.de_json(message, bot)
        register_handlers(dispatcher)
        dispatcher.process_update(update)
    return {'statusCode': 200}


def main() -> None:
    """ Точка входа для разработки"""
    with connection():
        updater = Updater(token=get_token(), persistence=YdbPersistence())
        register_handlers(updater.dispatcher)
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    main()
