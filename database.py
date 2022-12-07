import os
from contextlib import contextmanager
from typing import Any, Dict, List

from ydb import Driver, SerializableReadWrite, Session, SessionPool, convert
from ydb.iam import ServiceAccountCredentials

_session_pool: SessionPool

DictObject = Dict[str, Any]


@contextmanager
def database_connection():
    """Подключение к базе данных"""
    global _session_pool

    filename = os.getenv("SA_KEY_FILE")
    credentials = None
    if filename:
        credentials = ServiceAccountCredentials.from_file(filename)

    params = {
        "endpoint": os.getenv("YDB_ENDPOINT"),
        "database": os.getenv("YDB_DATABASE"),
        "credentials": credentials,
    }
    with Driver(**params) as driver:

        driver.wait(timeout=5, fail_fast=True)

        with SessionPool(driver) as session_pool:
            _session_pool = session_pool
            yield


def exec_query(query: str, params: DictObject = {}) -> List[convert.ResultSet]:
    """Выполнить запрос к базе данных"""
    global _session_pool

    def callee(session: Session) -> List[convert.ResultSet]:
        nonlocal query, params

        if params:
            query = session.prepare(query)

        tx_mode = SerializableReadWrite()
        transaction = session.transaction(tx_mode)
        return transaction.execute(query, params, commit_tx=True)

    result = _session_pool.retry_operation_sync(callee)
    if result is None:
        raise Exception("Cannot execute query to database")

    return result
