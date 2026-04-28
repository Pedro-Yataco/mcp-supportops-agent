from contextlib import contextmanager
from typing import Generator

import mysql.connector
from mysql.connector import MySQLConnection

from app.config import get_settings


@contextmanager
def get_db_connection() -> Generator[MySQLConnection, None, None]:
    settings = get_settings()

    connection = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.mysql_database,
        user=settings.mysql_user,
        password=settings.mysql_password,
    )

    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_db_cursor(dictionary: bool = True):
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=dictionary)
        try:
            yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()