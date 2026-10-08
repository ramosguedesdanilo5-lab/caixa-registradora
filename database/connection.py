import sqlite3
from pathlib import Path

from config.settings import DATABASE_PATH

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_connection(database_path: str | Path = DATABASE_PATH) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def initialize_database(database_path: str | Path = DATABASE_PATH) -> None:
    connection = get_connection(database_path)
    try:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    finally:
        connection.close()
