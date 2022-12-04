from enum import Enum, auto

from pydantic import BaseModel

from database import exec_query


class Role(Enum):
    ADMIN = auto()
    TUTOR = auto()
    STUDENT = auto()


class User(BaseModel):
    """Пользователь"""

    tg_id: int
    tg_username: str
    full_name: str
    name: str
    is_admin: bool
    manage_on: set[int]

    @staticmethod
    def get(tg: int) -> "User":
        """Поиск пользователя в базе данных"""

        query = """
            DECLARE $tg_id AS Uint64;
            SELECT tg_id, tg_username, full_name, name, is_admin
            FROM users
            WHERE tg_id == $tg_id;
        """
        params = {"$tg_id": tg}
        rows = exec_query(query, params)

        if not rows:
            raise Exception("User not found")

        return User(**rows[0])

    def role(self) -> Role:
        """Роль которую исполняет пользователь"""

        if self.is_admin:
            return Role.ADMIN
        elif self.manage_on:
            return Role.TUTOR
        else:
            return Role.STUDENT
