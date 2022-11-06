""" Telegram-бот "Помощник куратора" """

import json
import os
from queue import Queue

from telegram import Bot, Update
from telegram.ext import Dispatcher, Updater

from handlers import register_handlers
from models import obj_type


def get_token() -> str:
    """ Получаем токен """
    return os.getenv('BOT_TOKEN')


def lambda_handler(event: obj_type, _context: obj_type) -> obj_type:
    """ Точка входа в Yandex Cloud Functions (AWS Lambda) """
    bot = Bot(token=get_token())
    dispatcher = Dispatcher(bot, Queue())
    register_handlers(dispatcher)
    message = json.loads(event['body'])
    update = Update.de_json(message, bot)
    dispatcher.process_update(update)
    return {'statusCode': 200}


def main() -> None:
    """ Точка входа для разработки"""
    updater = Updater(token=get_token())
    register_handlers(updater.dispatcher)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
