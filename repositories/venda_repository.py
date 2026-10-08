import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import DATABASE_PATH
from database.connection import get_connection


class VendaRepository:
    def __init__(self, database_path: str | Path = DATABASE_PATH):
        self.database_path = database_path

    def criar(self, connection: sqlite3.Connection, venda: dict[str, Any], itens: list[dict[str, Any]]) -> int:
        cursor = connection.execute(
            """INSERT INTO vendas
               (data_hora, usuario_id, cliente_id, subtotal, desconto, total, forma_pagamento)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().astimezone().isoformat(timespec="seconds"),
                venda.get("usuario_id"), venda.get("cliente_id"), venda["subtotal"],
                venda["desconto"], venda["total"], venda["forma_pagamento"],
            ),
        )
        venda_id = int(cursor.lastrowid)
        connection.executemany(
            """INSERT INTO itens_venda
               (venda_id, produto_id, quantidade, preco_unitario, subtotal)
               VALUES (?, ?, ?, ?, ?)""",
            [
                (venda_id, item["produto_id"], item["quantidade"], item["preco_unitario"], item["subtotal"])
                for item in itens
            ],
        )
        return venda_id

    def listar(self, limite: int = 100) -> list[dict[str, Any]]:
        connection = get_connection(self.database_path)
        try:
            rows = connection.execute(
                """SELECT v.*, COUNT(i.id) AS quantidade_itens
                   FROM vendas v LEFT JOIN itens_venda i ON i.venda_id = v.id
                   GROUP BY v.id ORDER BY v.data_hora DESC LIMIT ?""",
                (limite,),
            )
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def resumo_hoje(self) -> dict[str, Any]:
        connection = get_connection(self.database_path)
        try:
            row = connection.execute(
                """SELECT COUNT(*) AS quantidade_vendas, COALESCE(SUM(total), 0) AS faturamento
                   FROM vendas WHERE date(data_hora, 'localtime') = date('now', 'localtime')"""
            ).fetchone()
            return dict(row)
        finally:
            connection.close()

    def itens_da_venda(self, venda_id: int) -> list[dict[str, Any]]:
        connection = get_connection(self.database_path)
        try:
            rows = connection.execute(
                """SELECT i.*, p.nome AS produto_nome FROM itens_venda i
                   JOIN produtos p ON p.id = i.produto_id WHERE i.venda_id = ? ORDER BY i.id""",
                (venda_id,),
            )
            return [dict(row) for row in rows]
        finally:
            connection.close()
