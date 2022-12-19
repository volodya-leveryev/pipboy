# import json

# from models.post import get_keywords
# from utils.config import config


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


# if __name__ == "__main__":
#     posts = refresh_posts()
# else:
#     with open("posts.json", encoding="utf-8") as f:
#         posts = json.load(f)
