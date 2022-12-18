from typing import List

from pydantic import BaseModel

from utils.database import exec_query


class Category(BaseModel):
    """Категория объявлений"""

    id: int
    name: str

    @staticmethod
    def get_list() -> List["Category"]:
        """Список категорий"""

        query = """
            SELECT id, name FROM categories;
        """
        rows = exec_query(query)
        return [Category(**cat) for cat in rows]

    @staticmethod
    def create(name: str) -> None:
        """Создать категорию"""

        query = """
            DECLARE $name AS Utf8;
            $id = Digest::MurMurHash($name);
            INSERT INTO categories (id, name)
            VALUES ($id, $name);
        """
        params = {"$name": name}
        exec_query(query, params)
