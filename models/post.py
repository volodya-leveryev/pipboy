import json
from typing import List

from pydantic import BaseModel
from pymystem3 import Mystem

from database import DictObject, exec_query


def get_keywords(text: str) -> List[str]:
    """Список ключевых слов в тексте"""

    important = (
        "A"  # Adjective, имя прилагательное
        "ADV"  # Adverb, наречие
        "NUM"  # Numeral, числительное
        "S"  # Noun, имя существительное
        "V"  # Verb, глагол
    )

    punctuation = ",=()|"
    puncts_to_space = str.maketrans(punctuation, " " * len(punctuation))

    result = set()
    for word in Mystem().analyze(text):
        analysis = word.get("analysis")
        if analysis:
            parts = [variant["gr"] for variant in analysis]
            parts = " ".join(parts)
            parts = parts.translate(puncts_to_space)
            parts = parts.split()
            signs_importance = (p in important for p in parts)
            if any(signs_importance):
                result.add(analysis["lex"])

    return sorted(result)


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
    def get_list(category: int) -> List["Post"]:
        """Получить список объявлений в категории"""

        query = """
            DECLARE $category AS Uint64;
            SELECT id, title, text
            FROM notices
            WHERE category == $category;
        """
        params = {"$category": category}
        rows = exec_query(query, params)

        return [Post(**row) for row in rows]

    @staticmethod
    def find_by_keywords(keywords: str) -> List["Post"]:
        """Список сообщений по запросу"""

        # keyword_list = sorted(set(keywords.lower().split()))
        query = """
            SELECT id, title, message
            FROM notice
            ORDER BY distance;
        """
        rows = exec_query(query)
        return [Post(**row) for row in rows]
