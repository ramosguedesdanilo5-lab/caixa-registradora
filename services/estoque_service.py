import sqlite3
from pathlib import Path

from config.settings import DATABASE_PATH
from database.connection import get_connection
from repositories.produto_repository import ProdutoRepository


class EstoqueService:
    def __init__(self, database_path: str | Path = DATABASE_PATH, produto_repository: ProdutoRepository | None = None):
        self.database_path = database_path
        self.produtos = produto_repository or ProdutoRepository(database_path)

    def produtos_com_estoque_baixo(self) -> list[dict]:
        return [
            produto for produto in self.produtos.listar()
            if produto["estoque"] <= produto["estoque_minimo"]
        ]

    def ajustar(self, produto_id: int, quantidade: int) -> None:
        if quantidade == 0:
            raise ValueError("O ajuste precisa alterar o estoque.")
        connection = get_connection(self.database_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = self.produtos.buscar_por_id(produto_id, connection)
            if row is None or not row["ativo"]:
                raise ValueError("Produto nao encontrado ou inativo.")
            novo_estoque = row["estoque"] + quantidade
            if novo_estoque < 0:
                raise ValueError("O ajuste deixaria o estoque negativo.")
            connection.execute("UPDATE produtos SET estoque = ? WHERE id = ?", (novo_estoque, produto_id))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def baixar(connection: sqlite3.Connection, produto_id: int, quantidade: int) -> None:
        cursor = connection.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND ativo = 1 AND estoque >= ?",
            (quantidade, produto_id, quantidade),
        )
        if cursor.rowcount != 1:
            raise ValueError("Estoque insuficiente ou produto indisponivel.")
