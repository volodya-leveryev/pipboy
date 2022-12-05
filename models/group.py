from typing import Set

from pydantic import BaseModel

from database import exec_query


class Group(BaseModel):
    """Группа пользователей"""

    id: int
    name: str
    members: Set[int]
    secret_word: str

    def add_member(self, user_id: int) -> None:
        """Добавить пользователя в группу"""

        if not isinstance(self.members, set):
            self.members = set()
        self.members.add(user_id)

    @staticmethod
    def get_list() -> list["Group"]:
        """Список групп"""

        query = """
            SELECT id, name FROM groups;
        """
        rows = exec_query(query)
        return [Group(**row) for row in rows]
