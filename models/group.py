from typing import Set

from pydantic import BaseModel


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
