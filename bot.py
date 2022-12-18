"""Telegram-бот «Помощник куратора»"""

import json
from queue import Queue

from telegram import Bot, Update
from telegram.ext import Dispatcher, Updater

from utils.config import config
from database import database_connection
from handlers import register_handlers
from persistance import YdbPersistence


def lambda_handler(event: dict, _context: dict) -> dict:
    """Точка входа в Yandex Cloud Functions (AWS Lambda)"""
    message = json.loads(event["body"])
    bot = Bot(config["TOKEN"])
    update = Update.de_json(message, bot)
    with database_connection():
        dispatcher = Dispatcher(bot, Queue(), persistence=YdbPersistence())
        register_handlers(dispatcher)
        dispatcher.process_update(update)
    return {"statusCode": 200}


def main() -> None:
    """Точка входа для разработки"""
    with database_connection():
        updater = Updater(config["TOKEN"], persistence=YdbPersistence())
        register_handlers(updater.dispatcher)
        updater.start_polling()
        updater.idle()


if __name__ == "__main__":
    main()
