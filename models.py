""" Модели данных """
import json
import os
from typing import Any, Dict

import ydb
from ydb.iam import ServiceAccountCredentials
from pydantic import BaseModel


def query_db(query: str) -> (Any | None):

    def exec_query(session: ydb.Session) -> Any:
        return session.transaction().execute(
            query, commit_tx=True,
            settings=ydb.BaseRequestSettings()
                        .with_timeout(3)
                        .with_operation_timeout(2)
        )

    credentials = ServiceAccountCredentials.from_file(
        os.getenv("SA_KEY_FILE")
    )
    driver = ydb.Driver(
        endpoint=os.getenv('YDB_ENDPOINT'),
        database=os.getenv('YDB_DATABASE'),
        credentials=credentials,
    )

    with driver:
        driver.wait(fail_fast=True, timeout=5)
        with ydb.SessionPool(driver) as pool:
            result = pool.retry_operation_sync(exec_query)

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
