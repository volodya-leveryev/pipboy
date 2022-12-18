from typing import Optional, Union, overload

from telegram import InlineKeyboardButton as btn, User as TgUser

from utils.database import exec_query

_current_user: "User"


class User:
    """Пользователь"""

    def __init__(self, **kwargs) -> None:
        self.id: int = kwargs["id"]
        self.bot_id: int = kwargs["bot_id"]
        self.user_id: int = kwargs["user_id"]
        self.username: str = kwargs["username"]
        self.full_name: str = kwargs["full_name"]
        self.name: str = kwargs["name"]
        self.is_admin: bool = kwargs["is_admin"]
        self.is_tutor: bool = kwargs["is_tutor"]
        self.is_student: bool = kwargs["is_student"]
        self.manage_on: list[int] = kwargs["manage_on"]

    def get_main_menu(self) -> list[list[btn]]:
        # return [
        #     [btn("Поиск объявления", callback_data="post_search")],
        #     [btn("Категории объявлений", callback_data="post_list")],
        # ]
        return []

    # def set_chat_id(self, bot_id: int, chat_id: int) -> None:
    #     query = """
    #         DECLARE $bot_id AS Uint64;
    #         DECLARE $user_id AS Uint64;
    #         DECLARE $chat_id AS Uint64;
    #         UPDATE users SET chat_id = $chat_id
    #         WHERE bot_id == $bot_id AND user_id == $user_id;
    #     """
    #     params = {"$bot_id": bot_id, "$user_id": self.user_id, "chat_id": chat_id}
    #     exec_query(query, params)

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


# class UserTutor(User):
#     def get_main_menu(self) -> list[list[btn]]:
#         buttons = super().get_main_menu()
#         buttons.append([btn("Разослать сообщение", callback_data="disp_msg")])
#         return buttons


# class UserAdmin(UserTutor):
#     def get_main_menu(self) -> list[list[btn]]:
#         buttons = super().get_main_menu()
#         buttons.append([btn("Обновить объявления", callback_data="post_refresh")])
#         return buttons

#     def get_cat_list(self) -> list[list[btn]]:
#         buttons = super().get_cat_list()
#         buttons.append([btn("Создать группу", callback_data="grp_create")])
#         return buttons

#     def get_cat_menu(self, cat_id) -> list[list[btn]]:
#         buttons = super().get_cat_menu(cat_id)
#         post_new = btn("Создать объявление", callback_data=f"post_create {cat_id}")
#         buttons.append([post_new])
#         return buttons


def create_user(obj: dict) -> User:
    """Создает пользователя нужно вида"""

    # if row["is_admin"]:
    #     return UserAdmin(**row)

    # if row["manage_on"]:
    #     return UserTutor(**row)
    return User(**obj)


def create_database_user(bot_id: int, tg_user: TgUser) -> Optional[User]:
    params = {
        "$bot_id": bot_id,
        "$user_id": tg_user.id,
        "$username": (tg_user.username or "").encode(),
    }
    query = """
        DECLARE $bot_id AS Uint64;
        DECLARE $user_id AS Uint64;
        DECLARE $username AS String;
        $id = (SELECT COUNT(*) FROM users);
        INSERT INTO users (id, bot_id, user_id, username)
        VALUES ($id, $bot_id, $user_id, $username);
    """
    exec_query(query, params)
    return find_user(params["user_id"], params["bot_id"])


@overload
def find_user(user: int, bot: int) -> Optional[User]:
    ...


@overload
def find_user(user: bytes, bot: int = 0) -> Optional[User]:
    ...


def find_user(user: Union[int, bytes], bot: int = 0) -> Optional[User]:
    """Поиск пользователя по идентификатору"""

    if bot:
        declaration = "DECLARE $bot_id AS Uint64; DECLARE $user_id AS Uint64;"
        condition = "t1.bot_id == $bot_id AND t1.user_id == $user_id"
        params = {"$bot_id": bot, "$user_id": user}
    else:
        declaration = "DECLARE $username AS String;"
        condition = "t1.username == $username"
        params = {"$username": user}
    query = f"""
        {declaration}
        SELECT
            id, bot_id, user_id, username, full_name, name,
            is_admin, is_tutor, is_student,
            AGG_LIST_DISTINCT(t2.group) AS manage_on
        FROM users AS t1 LEFT JOIN manage_on AS t2 ON t1.user_id == t2.user
        WHERE {condition}
        GROUP BY
            t1.id AS id,
            t1.bot_id AS bot_id,
            t1.user_id AS user_id,
            t1.username AS username,
            t1.full_name AS full_name,
            t1.name AS name,
            t1.is_admin AS is_admin,
            t1.is_tutor AS is_tutor,
            t1.is_student AS is_student;
    """
    rows = exec_query(query, params)
    if rows:
        return create_user(rows[0])


def set_user(user: User) -> None:
    global _current_user
    _current_user = user


def get_user() -> User:
    global _current_user
    return _current_user
