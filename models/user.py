from copy import deepcopy
from typing import Optional

from pydantic import BaseModel
from telegram import InlineKeyboardButton as btn

# from models.post import Post
# from cache import DictObject, users
# from models.category import Category
from database import exec_query


class User(BaseModel):
    """Пользователь"""

    user_id: int
    chat_id: int
    username: str
    full_name: str
    admin: bool

    # def get_main_menu(self) -> list[list[btn]]:
    #     # return [
    #     #     [btn("Поиск объявления", callback_data="post_search")],
    #     #     [btn("Категории объявлений", callback_data="post_list")],
    #     # ]
    #     return []

    # def get_cat_list(self) -> list[list[btn]]:
    #     buttons = [[btn("Назад", callback_data="main_menu")]]
    #     for c in Category.get_list():
    #         buttons.append([btn(c.name, callback_data=f"cat {c.id}")])
    #     return buttons

    # def get_cat_menu(self, cat_id) -> list[list[btn]]:
    #     buttons = [[btn("Назад", callback_data="cat_list")]]
    #     # for n in Post.get_list(cat_id):
    #     #     buttons.append([btn(n.title, callback_data=f"post {n.id}")])
    #     return buttons


def create_user(obj: dict) -> User:
    """Создает пользователя нужно вида"""
    # if row["is_admin"]:
    #     return UserAdmin(**row)

    # if row["manage_on"]:
    #     return UserTutor(**row)
    return User(**obj)


def find_user(bot_id: int, user_id: int) -> Optional[User]:
    """Ищет пользователя в базе данных"""

    query = """
        DECLARE $bot_id AS Uint64;
        DECLARE $user_id AS Uint64;
        SELECT
            t1.user_id AS user_id,
            t1.chat_id AS chat_id,
            t1.username AS username,
            t1.full_name AS full_name,
            t1.admin AS admin,
            AGG_LIST_DISTINCT(t2.group) AS manage_on
        FROM users AS t1 LEFT JOIN manage_on AS t2 ON t1.user_id == t2.user
        WHERE t1.bot_id == $bot_id AND t1.user_id == $user_id
        GROUP BY t1.user_id, t1.chat_id, t1.username, t1.full_name, t1.admin;
    """
    params = {"$bot_id": bot_id, "$user_id": user_id}
    rows = exec_query(query, params).rows
    if rows:
        return create_user(rows[0])


current_user: User


def get_main_menu() -> list[list[btn]]:
    """Создать главное меню"""
    global current_user

    student_menu = [[]]
    tutor_menu = deepcopy(student_menu)
    # tutor_menu.append([btn("Разослать сообщение", callback_data="disp_msg")])
    admin_menu = deepcopy(tutor_menu)
    # admin_menu.append([btn("Обновить объявления", callback_data="post_refresh")])

    if current_user.admin:
        return admin_menu
    # elif current_user["manage_on"]:
    #     return tutor_menu
    else:
        return student_menu


# class UserTutor(User):
#     def get_main_menu(self) -> list[list[btn]]:
#         buttons = super().get_main_menu()
#         buttons.append([btn("Разослать сообщение", callback_data="disp_msg")])
#         return buttons


# class UserAdmin(UserTutor):
#     def get_cat_list(self) -> list[list[btn]]:
#         buttons = super().get_cat_list()
#         buttons.append([btn("Создать группу", callback_data="grp_create")])
#         return buttons

#     def get_cat_menu(self, cat_id) -> list[list[btn]]:
#         buttons = super().get_cat_menu(cat_id)
#         post_new = btn("Создать объявление", callback_data=f"post_create {cat_id}")
#         buttons.append([post_new])
#         return buttons
