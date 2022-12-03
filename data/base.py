import os
from contextlib import contextmanager

from ydb import Driver, SessionPool
from ydb.iam import ServiceAccountCredentials


@contextmanager
def connection_to_database() -> None:
    """Подключение к базе данных"""
    global _session_pool

    filename = os.getenv("SA_KEY_FILE")
    credentials = None
    if filename:
        credentials = ServiceAccountCredentials.from_file(filename)

    with Driver(endpoint=os.getenv("YDB_ENDPOINT"),
                database=os.getenv("YDB_DATABASE"),
                credentials=credentials) as driver:
        driver.wait(timeout=5, fail_fast=True)

        with SessionPool(driver) as session_pool:
            _session_pool = session_pool
            yield
