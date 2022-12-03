import json
from collections import defaultdict
from typing import DefaultDict, Optional, Tuple

from telegram.ext import BasePersistence
from telegram.ext.utils.types import UD, ConversationDict

from data.base import exec_query


class YdbPersistence(BasePersistence):
    """Хранение состояния в базе данных"""

    def __init__(self) -> None:
        super().__init__(
            store_user_data=True,
            store_chat_data=False,
            store_bot_data=False,
            store_callback_data=False,
        )

    def get_user_data(self) -> DefaultDict[int, UD]:
        """Прочитать данные диалогов с пользователями"""
        query = """
            SELECT user_id, data FROM user_data;
        """
        result = defaultdict(dict)
        for row in exec_query(query):
            result[row["user_id"]] = json.loads(row["data"])
        return result

    def update_user_data(self, user_id: int, data: UD) -> None:
        """Обновить данные диалога с пользователем"""
        if data:
            # Обновить разговор
            query = """
                DECLARE $user_id AS Uint64;
                DECLARE $data AS Json;
                UPSERT INTO user_data (user_id, data, updated)
                VALUES ($user_id, $data, CurrentUtcDatetime());
            """
            params = {
                "$user_id": user_id,
                "$data": json.dumps(data),
            }
            exec_query(query, params)
        else:
            # Удалить разговор
            query = """
                DECLARE $user_id AS Uint64;
                DELETE FROM user_data WHERE user_id == $user_id
            """
            params = {
                "$user_id": user_id,
            }
            exec_query(query, params)

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