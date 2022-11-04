""" Модели данных """
import os
# from csv import reader
from typing import Any, List

import ydb
from pydantic import BaseModel


def query_db(query: str) -> (Any | None):

    def exec_query(session: ydb.Session) -> Any:
        return session.transaction().execute(
            query, commit_tx=True,
            settings=ydb.BaseRequestSettings()
                        .with_timeout(3)
                        .with_operation_timeout(2)
        )

    driver = ydb.Driver(
        endpoint=os.getenv('YDB_ENDPOINT'),
        database=os.getenv('YDB_DATABASE'),
        credentials=ydb.AcccessTokenCredentials(
            os.getenv('YDB_CREDENTIALS')
        )
    )

    with driver:
        driver.wait(fail_fast=True, timeout=5)
        with ydb.SessionPool(driver) as pool:
            result = pool.retry_operation_sync(exec_query)

    return result


class User(BaseModel):
    """ Пользователь """
    telegram_id: str = ""  # логин в Telegram
    telegram_num: str = ""  # телефона в Telegram
    name: str = ""  # обращение
    full_name: str = ""  # полное имя пользователя
    is_admin: bool = False  # признак администратора
    member_of: List[str] = []  # входит в группы
    manage_on: List[str] = []  # управляет группами
    comment: str = ""  # комментарий

    @staticmethod
    def get_user(telegram_id) -> ('User' | None):
        condition = f"WHERE telegram_id=`{telegram_id}`"
        users = query_db(f"SELECT * FROM users {condition}")
        print('DEBUG:', users)
        if users:
            return User(**users[0])
        return None

    # @staticmethod
    # def get_users() -> List['User']:
    #     """ Получить список пользователей """
    #     users = []
    #     with open('users.csv', encoding='utf-8') as csvfile:
    #         csv_reader = reader(csvfile, dialect='excel')
    #         next(csv_reader)
    #         for row in csv_reader:
    #             user = User(
    #                 telegram_id=row[0],
    #                 telegram_num=row[1],
    #                 full_name=row[2],
    #                 name=row[3],
    #                 is_admin=row[4] == 'TRUE',
    #                 member_of=row[5].split(),
    #                 manage_on=row[6].split(),
    #                 comment=row[7],
    #             )
    #             users.append(user)
    #     return users
