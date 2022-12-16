from copy import deepcopy
from pydantic import BaseModel
from telegram import InlineKeyboardButton as btn

# from models.post import Post
from cache import DictObject, users
from database import exec_query
from models.category import Category

current_user: DictObject


def get_main_menu() -> list[list[btn]]:
    """Создать главное меню"""
    global current_user

    student_menu = [[]]
    tutor_menu = deepcopy(student_menu)
    # tutor_menu.append([btn("Разослать сообщение", callback_data="disp_msg")])
    admin_menu = deepcopy(tutor_menu)
    admin_menu.append([btn("Обновить объявления", callback_data="post_refresh")])

    if current_user["admin"]:
        return admin_menu
    elif current_user["manage_on"]:
        return tutor_menu
    else:
        return student_menu


def user_required(handler):
    """Декоратор для поиска пользователя в базе данных"""

    def wrapper(update, context):
        global current_user
        try:
            # current_user = find_user(update.effective_user.username)
            current_user = users[update.effective_user.username]
            return handler(update, context)
        except (AttributeError, IndexError):
            update.message.reply_text("Извините, но мы не знакомы")

    return wrapper


class User(BaseModel):
    """Пользователь"""

    id: int
    username: str
    full_name: str
    name: str
    is_admin: bool
    manage_on: list[int]

    def get_main_menu(self) -> list[list[btn]]:
        # return [
        #     [btn("Поиск объявления", callback_data="post_search")],
        #     [btn("Категории объявлений", callback_data="post_list")],
        # ]
        return []

    def get_cat_list(self) -> list[list[btn]]:
        buttons = [[btn("Назад", callback_data="main_menu")]]
        for c in Category.get_list():
            buttons.append([btn(c.name, callback_data=f"cat {c.id}")])
        return buttons

    def get_cat_menu(self, cat_id) -> list[list[btn]]:
        buttons = [[btn("Назад", callback_data="cat_list")]]
        # for n in Post.get_list(cat_id):
        #     buttons.append([btn(n.title, callback_data=f"post {n.id}")])
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
        post_new = btn("Создать объявление", callback_data=f"post_create {cat_id}")
        buttons.append([post_new])
        return buttons


def find_user(username: str) -> User:
    """Поиск пользователя в базе данных"""

    query = """
        DECLARE $username AS String;
        SELECT
            t1.id AS id, t1.username AS username, t1.full_name AS full_name,
            t1.name AS name, t1.is_admin AS is_admin,
            AGG_LIST_DISTINCT(t2.group) AS manage_on
        FROM users AS t1 JOIN manage_on AS t2 ON t1.id == t2.user
        WHERE t1.username == $username
        GROUP BY t1.id, t1.username, t1.full_name, t1.name, t1.is_admin;
    """
    params = {"$username": username.encode()}
    row = exec_query(query, params)[0].rows[0]

    if row["is_admin"]:
        return UserAdmin(**row)

    if row["manage_on"]:
        return UserTutor(**row)

    return User(**row)
