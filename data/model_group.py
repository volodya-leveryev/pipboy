from typing import Set

from pydantic import BaseModel


class Group(BaseModel):
    """ Группа пользователей """
    id: int = 0
    name: str = ""
    members: Set[int] = 0
    secret_word: str = ""

    def add_member(self, user_id: int) -> None:
        if not isinstance(self.members, set):
            self.members = set()
        self.members.add(user_id)
