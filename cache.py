import json
import os
from typing import Any

# from models.post import get_keywords

DictObject = dict[str, Any]

_config_file = "config_dev.json"
if os.getenv("BOT_ENV") == "PRODUCTION":
    _config_file = "config.json"
with open(_config_file, encoding="utf-8") as f:
    config = json.load(f)


def get_google_spreadsheet_values(spreadsheet_id):
    """Получить значения из ячеек Google-таблицы"""
    from pathlib import Path

    import gspread

    gc = gspread.service_account(Path("google_service_account.json"))
    wks = gc.open_by_key(spreadsheet_id)
    values = wks.sheet1.get_all_values()
    return values


# def refresh_posts():
#     """Обновить кэш объявлений"""
#     rows = get_values(config["POSTS"])
#     posts = {"titles": [], "posts": [], "index": {}}
#     for i, row in enumerate(rows[1:]):
#         posts["titles"].append(row[0])
#         posts["posts"].append(row[1])
#         keywords = get_keywords(row[1])
#         for keyword in keywords:
#             posts["index"].setdefault(keyword, [])
#             posts["index"][keyword].append(i)
#     with open("posts.json", "w", encoding="utf-8") as f:
#         json.dump(posts, f, ensure_ascii=False)
#     return posts


def refresh_users():
    """Обновить кэш пользователей"""
    rows = get_google_spreadsheet_values(config["USERS"])
    users = {
        row[0]: {
            "full_name": row[1],
            "name": row[2],
            "admin": row[3] == "TRUE",
            "member_of": row[4].split(),
            "manage_on": row[5].split(),
        }
        for row in rows[1:]
    }
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)
    return users


if __name__ == "__main__":
    # posts = refresh_posts()
    users = refresh_users()

else:
    # with open("posts.json", encoding="utf-8") as f:
    #     posts = json.load(f)

    with open("users.json", encoding="utf-8") as f:
        users = json.load(f)
