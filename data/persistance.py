import json
from typing import Optional, Tuple

from telegram.ext import BasePersistence
from telegram.ext.utils.types import ConversationDict

from data.base import exec_query


class YdbPersistence(BasePersistence):
    """Хранение состояния в базе данных"""

    def __init__(self) -> None:
        super().__init__(
            store_user_data=False,
            store_chat_data=False,
            store_bot_data=False,
            store_callback_data=False,
        )

    def get_conversations(self, name: str) -> ConversationDict:
        """Прочитать состояние разговора из базы данных"""
        query = """
            DECLARE $name AS String;
            SELECT key, state FROM conversations WHERE name == $name;
        """
        params = {"$name": name.encode()}
        result = {}
        for row in exec_query(query, params):
            result[tuple(json.loads(row["key"]))] = row["state"]
        return result

    def update_conversation(self, name: str, key: Tuple[int, ...],
                            new_state: Optional[object]) -> None:
        """Обновить или удалить разговор в базе данных"""
        if new_state:
            # Обновить разговор
            query = """
                DECLARE $name AS String;
                DECLARE $key AS String;
                DECLARE $state AS Uint32;
                UPSERT INTO conversations (name, key, state, updated)
                VALUES ($name, $key, $state, CurrentUtcDatetime());
            """
            params = {
                "$name": name.encode(),
                "$key": json.dumps(key).encode(),
                "$state": new_state,
            }
            exec_query(query, params)
        else:
            # Удалить разговор
            query = """
                DECLARE $name AS String;
                DECLARE $key AS String;
                DELETE FROM conversations WHERE name == $name AND key == $key
            """
            params = {
                "$name": name.encode(),
                "$key": json.dumps(key).encode(),
            }
            exec_query(query, params)
