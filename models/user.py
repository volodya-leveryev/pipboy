from enum import Enum, auto

from pydantic import BaseModel
from telegram import InlineKeyboardButton as btn

from database import exec_query
from models.category import Category
from models.group import Group
from models.notice import Notice


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
    manage_on: set[Group]

    def role(self) -> Role:
        """Роль которую исполняет пользователь"""

        if self.is_admin:
            return Role.ADMIN
        elif self.manage_on:
            return Role.TUTOR
        else:
            return Role.STUDENT


class UserStudent(User):
    def get_main_menu(self) -> list[list[btn]]:
        return [[btn("Объявления", callback_data="notices_menu")]]

    def get_notices_menu(self) -> list[list[btn]]:
        buttons = [[btn("Главное меню", callback_data="main_menu")]]
        buttons.append([btn("Поиск", callback_data="notice_search")])
        for c in Category.get_list():
            buttons.append([btn(c.name, callback_data=f"category_{c.id}")])
        return buttons

    def get_category_menu(self, cat_id) -> list[list[btn]]:
        buttons = [[btn("Главное меню", callback_data="main_menu")]]
        for n in Notice.get_list(cat_id):
            buttons.append([btn(n.title, callback_data=f"notice_{n.id}")])
        return buttons

    def get_notice_menu(self, notice_id) -> list[list[btn]]:
        return [[btn("Главное меню", callback_data="main_menu")]]


class UserTutor(UserStudent):
    def get_main_menu(self) -> list[list[btn]]:
        buttons = super().get_main_menu()
        buttons.append([btn("Группы", callback_data="groups_menu")])
        return buttons

    def get_groups_menu(self) -> list[list[btn]]:
        buttons = [[btn("Главное меню", callback_data="main_menu")]]
        for g in self.manage_on:
            buttons.append([btn(g.name, callback_data=f"group_{g.id}")])
        return buttons

    def get_group_menu(self, group_id: int) -> list[list[btn]]:
        return [[btn("Разослать сообщение", callback_data=f"dispatch_msg_{group_id}")]]


class UserAdmin(UserTutor):
    def get_notices_menu(self) -> list[list[btn]]:
        buttons = super().get_notices_menu()
        buttons.append([btn("Создать категорию", callback_data="category_create")])
        return buttons

    def get_category_menu(self, cat_id) -> list[list[btn]]:
        buttons = super().get_category_menu(cat_id)
        if len(buttons) == 1:
            buttons.append(
                [btn("Удалить категорию", callback_data=f"category_delete_{cat_id}")]
            )
        buttons.append(
            [btn("Создать объявление", callback_data=f"notice_create_{cat_id}")]
        )
        return buttons

    def get_notice_menu(self, notice_id) -> list[list[btn]]:
        buttons = super().get_notice_menu(notice_id)
        buttons.append(
            [btn("Удалить объявление", callback_data=f"notice_delete_{notice_id}")]
        )
        return buttons

    def get_groups_menu(self) -> list[list[btn]]:
        buttons = super().get_groups_menu()
        buttons.append([btn("Создать группу", callback_data="group_create")])
        return buttons

    def get_group_menu(self, group_id: int) -> list[list[btn]]:
        buttons = super().get_group_menu(group_id)
        buttons.append(
            [btn("Удалить группу", callback_data=f"group_delete_{group_id}")]
        )
        return buttons


def get_user(tg_id: int) -> User:
    """Поиск пользователя в базе данных"""

    query = """
        DECLARE $tg_id AS Uint64;
        SELECT tg_id, tg_username, full_name, name, is_admin
        FROM users
        WHERE tg_id == $tg_id;
    """
    params = {"$tg_id": tg_id}
    rows = exec_query(query, params)
    if not rows:
        raise RuntimeError("User not found")

    row = rows[0]

    if row["is_admin"]:
        return UserAdmin(**row)

    if row["manage_on"]:
        return UserTutor(**row)

    return UserStudent(**row)
