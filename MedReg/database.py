import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from config import DB_PATH


class DatabaseManager:
    """Класс для работы с SQLite-базой данных."""

    def __init__(self, db_path: Union[str, Path] = DB_PATH) -> None:
        self.db_path = str(db_path)
        self.schema_path = Path(__file__).with_name("schema.sql")

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    def initialize(self) -> None:
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Не найден файл схемы БД: {self.schema_path}")

        sql = self.schema_path.read_text(encoding="utf-8")
        connection = self.connect()

        try:
            connection.executescript(sql)
            connection.commit()
        finally:
            connection.close()

    def execute(self, query: str, params: Iterable[Any] = ()) -> int:
        connection = self.connect()

        try:
            cursor = connection.execute(query, tuple(params))
            connection.commit()
            return int(cursor.lastrowid or 0)
        finally:
            connection.close()

    def fetch_one(
        self,
        query: str,
        params: Iterable[Any] = (),
    ) -> Optional[Dict[str, Any]]:
        connection = self.connect()

        try:
            row = connection.execute(query, tuple(params)).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def fetch_all(
        self,
        query: str,
        params: Iterable[Any] = (),
    ) -> List[Dict[str, Any]]:
        connection = self.connect()

        try:
            rows = connection.execute(query, tuple(params)).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()