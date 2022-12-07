import json

from pydantic import BaseModel
from telegram import InlineKeyboardButton as btn

from database import exec_query
from models.category import Category
from models.group import Group
from models.post import Post


class User(BaseModel):
    """Пользователь"""

    tg_id: int
    tg_username: str
    full_name: str
    name: str
    is_admin: bool
    manage_on: set[Group]

    def get_main_menu(self) -> list[list[btn]]:
        return [
            [btn("Поиск объявления", callback_data="post_search")],
            [btn("Категории объявлений", callback_data="post_list")],
        ]

    def get_cat_list(self) -> list[list[btn]]:
        buttons = [[btn("Назад", callback_data="main_menu")]]
        for c in Category.get_list():
            buttons.append([btn(c.name, callback_data=f"cat_{c.id}")])
        return buttons

    def get_cat_menu(self, cat_id) -> list[list[btn]]:
        buttons = [[btn("Назад", callback_data="cat_list")]]
        for n in Post.get_list(cat_id):
            buttons.append([btn(n.title, callback_data=f"post_{n.id}")])
        return buttons


class UserTutor(User):
    def get_main_menu(self) -> list[list[btn]]:
        buttons = super().get_main_menu()
        buttons.append([btn("Разослать сообщение", callback_data="disp_msg")])
        return buttons


class UserAdmin(UserTutor):
    def get_cat_list(self) -> list[list[btn]]:
        buttons = super().get_cat_list()
        buttons.append([btn("Создать группу", callback_data="grp_create")])
        return buttons

    def get_cat_menu(self, cat_id) -> list[list[btn]]:
        buttons = super().get_cat_menu(cat_id)
        post_new = btn("Создать объявление", callback_data=f"post_create_{cat_id}")
        buttons.append([post_new])
        return buttons


def find_user(tg_id: int) -> User:
    """Поиск пользователя в базе данных"""

    query = """
        DECLARE $tg_id AS Uint64;
        SELECT tg_id, tg_username, full_name, name, is_admin, manage_on
        FROM users
        WHERE tg_id == $tg_id;
    """
    params = {"$tg_id": tg_id}
    row = exec_query(query, params)[0].rows[0]
    row["manage_on"] = set(json.loads(row["manage_on"]))

    if row["is_admin"]:
        return UserAdmin(**row)

    if row["manage_on"]:
        return UserTutor(**row)

    return User(**row)
