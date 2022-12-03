import json
from typing import List

from pydantic import BaseModel

from data.base import exec_query


class User(BaseModel):
    """ Пользователь """
    tg_id: int
    tg_username: str
    full_name: str
    name: str
    is_admin: bool
    manage_on: List[int]

    @classmethod
    def get(cls, tg: int | str) -> 'User':
        if isinstance(tg, int):
            query = """
                DECLARE $tg_id AS Uint64;
                SELECT tg_id, tg_username, full_name, name, is_admin
                FROM users
                WHERE tg_id == $tg_id;
            """
            params = {"$tg_id": tg}
            rows = exec_query(query, params)

        elif isinstance(tg, str):
            query = """
                DECLARE $tg_username AS String;
                SELECT tg_id, tg_username, full_name, name, is_admin
                FROM users
                WHERE tg_username == $tg_username;
            """
            params = {"$tg_username": tg.encode()}
            rows = exec_query(query, params)

        if rows:
            return cls(**rows[0])

    def add_group(self, group_id: int):
        if not isinstance(self.manage_on, set):
            self.manage_on = set()
        self.manage_on.add(group_id)

        query = """
            DECLARE $tg_id AS Uint64;
            DECLARE $manage_on AS Set<Uint64>;
            UPDATE users
            SET manage_on = $manage_on
            WHERE tg_id == $tg_id;
        """
        params = {"$tg_id": self.id, "$manage_on": json.dumps(self.manage_on)}

        exec_query(query, params)

    def role(self) -> str:
        if self.is_admin:
            return 'admin'
        elif self.is_admin:  # TODO: куратор
            return 'tutor'
        else:
            return 'student'
