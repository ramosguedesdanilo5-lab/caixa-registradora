import sqlite3
from pathlib import Path
from typing import Any

from config.settings import DATABASE_PATH
from database.connection import get_connection
from utils.validators import validate_cpf


class ClienteRepository:
    def __init__(self, database_path: str | Path = DATABASE_PATH):
        self.database_path = database_path

    def listar(self) -> list[dict[str, Any]]:
        connection = get_connection(self.database_path)
        try:
            rows = connection.execute("SELECT * FROM clientes WHERE ativo = 1 ORDER BY nome COLLATE NOCASE")
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def criar(self, nome: str, cpf: str | None = None, telefone: str | None = None) -> int:
        if not nome.strip():
            raise ValueError("Informe o nome do cliente.")
        cpf = validate_cpf(cpf)
        connection = get_connection(self.database_path)
        try:
            cursor = connection.execute(
                "INSERT INTO clientes (nome, cpf, telefone) VALUES (?, ?, ?)",
                (nome.strip(), cpf, telefone or None),
            )
            connection.commit()
            return int(cursor.lastrowid)
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ValueError("Ja existe um cliente com esse CPF.") from error
        finally:
            connection.close()
