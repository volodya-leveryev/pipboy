import json
import re
from collections import Counter
from typing import Iterable

from pydantic import BaseModel
from pymorphy2 import MorphAnalyzer

from database import DictObject, exec_query

stopwords: set = set()
posts: dict = {}

with open("posts.json", encoding="utf-8") as f:
    posts = json.load(f)


def get_stopwords():
    """Чтение списка незначимых слов из файла"""
    global stopwords
    if not stopwords:
        with open("stopwords.txt") as f:
            stopwords = set(f.read().split())
    return stopwords


def get_keywords(text: str) -> set[str]:
    """Извлечение ключевых слов из текста"""
    # Разбивка текста на слова
    tokens = text.split()
    # Приведение к нижнему регистру, замена ё на е
    tokens = [token.lower().replace("ё", "e") for token in tokens]
    # Очистка символов пунктуации
    puncts = re.compile("[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~–—«»№0-9]")
    tokens = [puncts.sub("", token) for token in tokens]
    # Приведение слов к основной форме
    morph = MorphAnalyzer(lang="ru")
    tokens = [morph.parse(token)[0].normal_form for token in tokens if token]
    # Очистка незначимых слов
    stopwords = get_stopwords()
    tokens = [token for token in tokens if len(token) > 1 and token not in stopwords]
    # Очистка повторов
    return set(tokens)


def find_posts(query: Iterable[str]) -> list[tuple[str, str]]:
    """Поиск объявлений по ключевым словам"""
    # Индексы объявлений по ключевым словам
    post_indices = [i for token in query for i in posts["index"].get(token, [])]
    # Количество повторов каждого индекса
    post_indices = [item for item in Counter(post_indices).items()]
    # Сортировка, чтобы сначала шли наиболее релевантные объявления
    post_indices.sort(key=lambda i: -i[1])
    # Возвращаем индексы объявлений
    return [i for i, _ in post_indices]


def refresh_posts():
    """Обновление объявлений в базе данных"""
    pass


def create_post(title, text):
    """Создать объявление"""

    def get_value(p):
        nonlocal post_id
        kw_id = hash(p) + post_id + 2**63
        return kw_id % 2**64, post_id, p

    query = """
        DECLARE $id AS Uint64;
        DECLARE $title AS Utf8;
        DECLARE $text AS Utf8;
        UPSERT INTO posts (id, title, text)
        VALUES ($id, $title, $text);
    """
    post_id = hash(title + text) + 2**63
    params = {"$id": post_id, "$title": title, "$text": text}
    exec_query(query, params)

    keywords = get_keywords(text)
    query = """
        DECLARE $values AS List<Tuple<Uint64,Uint64,Utf8>>
        UPSERT INTO keywords (id, post, keyword)
        VALUES $values;
    """
    params = {"$values": [get_value(p) for p in keywords]}
    exec_query(query, params)


class Post(BaseModel):
    """Информационное сообщение"""

    id: int = 0
    title: str = ""
    message: str = ""

    @staticmethod
    def create(user_data: DictObject):
        """Создать категорию"""

        if isinstance(user_data["category"], int):
            query = """
                DECLARE $category AS Uint64;
                DECLARE $keywords AS JsonDocument;
                DECLARE $text AS JsonDocument;
                DECLARE $title AS JsonDocument;
                $id = Digest::MurMurHash($text);
                INSERT INTO notice (id, category, keywords, text, title)
                VALUES ($id, $category, $keywords, $text, $title);
            """
            params = {
                "$category": user_data["category"],
                "$keywords": json.dumps(get_keywords(user_data["text"])),
                "$text": user_data["text"],
                "$title": user_data["title"],
            }
            exec_query(query, params)

    @staticmethod
    def get_list(category: int) -> list["Post"]:
        """Получить список объявлений в категории"""

        query = """
            DECLARE $category AS Uint64;
            SELECT id, title, text
            FROM notices
            WHERE category == $category;
        """
        params = {"$category": category}
        rows = exec_query(query, params)[0].rows

        return [Post(**row) for row in rows]

    @staticmethod
    def find_by_keywords(keywords: str) -> list["Post"]:
        """Список сообщений по запросу"""

        # keyword_list = sorted(set(keywords.lower().split()))
        query = """
            SELECT id, title, message
            FROM notice
            ORDER BY distance;
        """
        rows = exec_query(query)[0].rows
        return [Post(**row) for row in rows]
