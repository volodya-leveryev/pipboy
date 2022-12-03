import json
from typing import List

from pydantic import BaseModel
from pymystem3 import Mystem

from data.base import DictObject, exec_query


def get_keywords(text: str) -> List[str]:
    stemmer = Mystem()
    result = []
    for word in stemmer.analyze(text):
        analysis = word.get("analysis")
        if analysis:
            gr = analysis[0]["gr"]
            gr = gr.translate(str.maketrans(",=(|)", "     "))
            part, _ = gr.split(maxsplit=1)
            if part in ("A", "ADV", "NUM", "S", "V"):
                result.append(analysis["lex"])
    return sorted(result)


class Notice(BaseModel):
    """ Информационное сообщение """
    id: int = 0
    title: str = ""
    message: str = ""

    @classmethod
    def create(cls, user_data: DictObject):
        if isinstance(user_data['category'], int):
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
                "$category": user_data['category'],
                "$keywords": json.dumps(get_keywords(user_data['text'])),
                "$text": user_data['text'],
                "$title": user_data['title'],
            }
            exec_query(query, params)

    @classmethod
    def get_list(cls, category: int) -> List['Notice']:
        query = """
            DECLARE $category AS Uint64;
            SELECT id, title, text
            FROM notices
            WHERE category == $category;
        """
        params = {'$category': category}
        rows = exec_query(query, params)
        return [cls(**row) for row in rows]

    @classmethod
    def find_by_keywords(cls, keywords: str) -> List['Notice']:
        """ Список сообщений по запросу """
        # keyword_list = sorted(set(keywords.lower().split()))
        query = """
            SELECT id, title, message
            FROM notice
            ORDER BY distance;
        """
        rows = exec_query(query)
        return [cls(**row) for row in rows]
