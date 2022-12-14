from contextlib import contextmanager
from typing import Any, Optional, TypeVar

from ydb import Driver, SerializableReadWrite, Session, SessionPool
from ydb.convert import ResultSet
from ydb.iam import ServiceAccountCredentials

from utils.config import config

DictObject = TypeVar("DictObject", bound=dict[str, Any])

_session_pool: SessionPool


@contextmanager
def database_connection():
    """Подключение к базе данных"""
    global _session_pool

    filename = config["SA_KEY_FILE"]
    credentials = ServiceAccountCredentials.from_file(filename)
    connection_params = {
        "endpoint": config["YDB_ENDPOINT"],
        "database": config["YDB_DATABASE"],
        "credentials": credentials,
    }
    with Driver(**connection_params) as driver:
        driver.wait(timeout=5, fail_fast=True)

        with SessionPool(driver) as session_pool:
            _session_pool = session_pool
            yield


def exec_query(query: str, params: Optional[DictObject] = None) -> list[DictObject]:
    """Выполнить запрос к базе данных"""
    global _session_pool

    def callee(session: Session) -> list[ResultSet]:
        nonlocal query, params

        if params:
            query = session.prepare(query)

        tx_mode = SerializableReadWrite()
        transaction = session.transaction(tx_mode)
        return transaction.execute(query, params, commit_tx=True)

    results: Optional[list[ResultSet]] = _session_pool.retry_operation_sync(callee)
    return results[0].rows if results else []
