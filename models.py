""" Модели данных """

import json
import os
from functools import cache
from typing import Any, Dict

import ydb
from ydb.iam import ServiceAccountCredentials
from pydantic import BaseModel


@cache
def get_db_driver():
    credentials = None
    if filename := os.getenv('SA_KEY_FILE'):
        credentials = ServiceAccountCredentials.from_file(filename)
    return ydb.Driver(
        endpoint=os.getenv('YDB_ENDPOINT'),
        database=os.getenv('YDB_DATABASE'),
        credentials=credentials,
    )


def query_db(query: str):

    def exec_query(session: ydb.Session) -> Any:
        settings = ydb.BaseRequestSettings()
        settings.timeout = 3
        settings.operation_timeout = 5
        transaction = session.transaction()
        return transaction.execute(query, commit_tx=True, settings=settings)

    driver = get_db_driver()
    driver.wait(timeout=5, fail_fast=True)
    with ydb.SessionPool(driver) as pool:
        result = pool.retry_operation_sync(exec_query)
    driver.stop()

    return result[0].rows


class User(BaseModel):
    """ Пользователь """
    telegram_username: str = ""  # логин в Telegram
    data: Dict[str, Any] = {}  # дополнительные данные
    full_name: str = ""  # полное имя пользователя
    is_admin: bool = False  # признак администратора
    name: str = ""  # обращение
    telegram_number: str = ""  # телефона в Telegram

    @staticmethod
    def get_by_username(telegram_username: str):
        users = query_db(f"""
            SELECT * FROM `users` 
            WHERE `telegram_username` == \"{telegram_username}\";
        """)
        if users:
            user = users[0]
            user['data'] = json.loads(user['data'])
            return User(**user)
