from typing import List

from pydantic import BaseModel

from data.base import exec_query


class Category(BaseModel):
    """ Категория объявлений """
    id: int
    name: str

    @classmethod
    def get_list(cls) -> List['Category']:
        query = """
            SELECT id, name FROM categories;
        """
        rows = exec_query(query)
        return [cls(**cat) for cat in rows]

    @classmethod
    def create(cls, name: str) -> None:
        query = """
            DECLARE $name AS Utf8;
            $id = Digest::MurMurHash($name);
            INSERT INTO categories (id, name)
            VALUES ($id, $name);
        """
        params = {'$name': name}
        exec_query(query, params)
